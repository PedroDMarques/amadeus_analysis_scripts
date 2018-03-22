import os
import os.path
import dateutil.parser
import collections
import json

from virtual_list import VirtualListDict
from jsonutil import json_loads_byteified as json_loads

MAXMEM = 500000000

class ParsingError(ValueError):
	pass

def parse_diversity(fpath, savepath, schema):
	data = VirtualListDict(maxmem=MAXMEM)
	
	with open(fpath, "r") as infile:
		for line in infile:
			origprops = json_loads(line)
			divprops = dict()

			divkey = origprops[schema["diversity_key"]]
			## If the diversity key does not exist we don't count it
			if divkey == None:
				continue

			for key in schema["fields"]:
				if key in origprops:
					divprops[key] = origprops[key]

			data.append(divkey, divprops)

	if len(data) > 0:
		with open(savepath, "w") as outfile:
			outfile.write("{")
			i = 0
			for key in data:
				if i > 0:
					outfile.write(",")
				i += 1

				outfile.write('"%s":[' % key)
				j = 0
				for entry in data[key]:
					if j > 0:
						outfile.write(",")
					j += 1

					outfile.write("%s" % json.dumps(entry))
				outfile.write("]")

			outfile.write("}")

def parse_file(fpath, save_location, schema, originalSoftware, originalDevice, getOutFileName):
	outfiles = VirtualListDict(maxmem=MAXMEM)

	with open(fpath, "r") as inFile:
		for line in inFile:
			# Do initial function in schema
			if "pre" in schema: line = schema["pre"](line)

			raw_props = json_loads(line)
			parsed_props = dict()

			# Copy fields from raw data except the ones to ignore
			for field in raw_props:
				if field not in schema.get("ignore_fields", []):
					parsed_props[field] = raw_props[field]

			# Parse fields specified
			for field in schema.get("parse_fields", dict()).get("fields", dict()):
				raw_data_field = schema["parse_fields"]["fields"][field]
				raw_value = None
				
				if type(raw_data_field) is list:
					for fname in raw_data_field:
						if fname in raw_props:
							raw_value = raw_props[fname]
				else:
					raw_value = raw_props.get(raw_data_field, None)

				value = None
				if raw_value and field in schema["parse_fields"].get("parse", dict()):
					value = schema["parse_fields"]["parse"][field](raw_value)
				else:
					value = raw_value

				parsed_props[field] = value

			# Add scripted fields
			for field in schema.get("scripted_fields", dict()):
				parsed_props[field] = schema["scripted_fields"][field](raw_props, parsed_props)

			# Getting the save location
			timestamp = dateutil.parser.parse(parsed_props.get(schema["timestamp_field"]))
			hourFolder = timestamp.strftime("%Y-%m-%dT%H")

			savingDir = os.path.join(save_location, hourFolder)
			if not os.path.exists(savingDir):
				os.makedirs(savingDir)

			software = parsed_props.get(schema["software_field"]) if "software_field" in schema else originalSoftware
			device = parsed_props.get(schema["device_field"]) if "device_field" in schema else originalDevice

			out_file_name = getOutFileName(software, device)
			out_filepath = os.path.join(savingDir, out_file_name)

			for prop in parsed_props:
				if not isinstance(parsed_props[prop], collections.Hashable):
					try:
						parsed_props[prop] = tuple(parsed_props[prop])
					except:
						raise ParsingError("Could not correctly parse %d in line %s" % (prop, line))

			saveline = "%s\n" % json.dumps(parsed_props)
			outfiles.append(out_filepath, saveline)

	for fpath in outfiles:
		with open(fpath, "a+") as fh:
			fh.writelines(outfiles[fpath])