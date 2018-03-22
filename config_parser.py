import os

OPTIONS = {
	"raw_data_location": {
		"description": "Raw data location description",
		"default": "..%sdata" % os.sep,
		"read": (lambda x: x)
	},

	"parsed_data_location": {
		"description": "Parsed data location description",
		"default": "..%sdata_parsed" % os.sep,
		"read": (lambda x: x)
	},

	"collected_data_location": {
		"description": "Collected data location description",
		"default": "..%sdata_collected" % os.sep,
		"read": (lambda x: x)
	},

	"es_index": {
		"description": "Elasticsearch index description",
		"default": "es-index",
		"read": (lambda x: x)
	},

	"ignore_software": {
		"description": "Ignore software description",
		"default": "",
		"read": (lambda x: x.split(","))
	},

	"ignore_device": {
		"description": "Ignore device description",
		"default": "",
		"read": (lambda x: x.split(","))
	},

	"ignore_file_name": {
		"description": "Ignore file name description",
		"default": "_SUCCESS",
		"read": (lambda x: x.split(","))
	},

	"ignore_file_ext": {
		"description": "Ignore file ext description",
		"default": "zip,gz",
		"read": (lambda x: x.split(","))
	}
}

OPTIONS_ORDER = [
	"raw_data_location", "parsed_data_location", "collected_data_location",
	"es_index",
	"ignore_software", "ignore_device", "ignore_file_name", "ignore_file_ext"
]

def read(config_path):
	"""
	Read the configuration for the specified location
	Parameters:
		{str} config_path The path to the config file to read
	Returns:
		{dict} Dictionary containing the options read from the config file in key => value format
	"""
	config = dict()
	try:
		with open(config_path, "r") as fh:
			for line in fh:
				line = line.split("\n")[0]
				ls = line.split("=")
				key = ls[0]
				value = ls[1] if len(ls) > 1 else ""
				if key in OPTIONS:
					config[key] = OPTIONS[key]["read"](value)

	except IOError:
		print "Could not find config file. Run main.py install to create a config file"
		exit(-1)

	return config

def write(config_path):
	"""
	Prompt use to write configuration
	"""
	print "\n"

	with open(config_path, "w") as fh:
		print "Writing config file. Press <enter> for default values or type '.' for writing blank values instead"
		for opt in OPTIONS_ORDER:
			value = raw_input("\n%s\n%s\n[%s] " % (opt, OPTIONS[opt]["description"], OPTIONS[opt]["default"]))

			if value == ".": value = ""
			elif not value: value = OPTIONS[opt]["default"]

			fh.write("%s=%s\n" % (opt, value))