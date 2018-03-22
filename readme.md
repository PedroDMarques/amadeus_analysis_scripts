## Parsing schemas
When parsing raw data, dynamic modules are loaded from "\parsing_schemas".

These modules consist of a python file, with the same name as the software they should be used to parse, and should expose a function 'getSchema' that returns a python dictionary, used to parse the raw data.

The schema object should be structured as follows:
	{
		# A function called when first reading a line of raw data
		# Takes the line of raw data as an argument and returns a new line to use for the rest of the parsing
		# Look at mcafee for an example
		pre: function,

		# An array containing the names of fields to ignore when copying values from the raw data to the parsed data
		# Example: ["source_ip", "destionation_ip"]
		# When parsing raw data, copying data values is the first thing that the scripts do, so the values not ignored at this stage might still be overwritten later on
		ignore_fields: str[],
		
		# A dictionary used to specify fields that need extra parsing besides just copying them
		parse_fields: {
			
			# A list of fields to create in the parsed data
			# Each key is the new key in the parsed data
			# Each value is the name of the field in the raw data to copy
			# The value can also be a list of strings of possible names. Value will be copied from the first field found in the list
			fields: dict(),

			# If a key from "fields" is present in parse the value copied from the raw data will be put through the function given in this object before being saved in the parsed data
			# Each key is a key found in "fields"
			# Each value is a function that takes a value as a parameter and returns the parsed value
			parse: dict()
		},

		# A dictionary containing additional fields to create in the parsed data
		# Each key is the name of the field to create in the parsed data
		# Each value is a function that takes the raw data as a parameter and returns the value of the scripted field
		scripted_fields: dict(),

		# The name of the field that holds the actual software of the data
		# This is useful if data from multiple softwares is present in the same file
		software_field: str,
		# Same as 'software_field' but for device
		device_field: str,

		# The name of the field that holds timestamp data
		# This is used (and must exist) to direct data into the correct date and hour folder
		# This is used after parsing all of the data so the field containing the timestamp should already be part of the parsed values
		timestamp_field: str,
	}