import json

def json_load_byteified(file_handle):
	"""
	Same as json_loads_byteified but loads json from a file_handle
	Parameters:
		{fh} file_handle An handle to the file to read json from
	Returns:
		{dict} The json object correctly parsed with byte keys and values
	"""
	return _byteify(
		json.load(file_handle, object_hook=_byteify),
		ignore_dicts=True
	)

def json_loads_byteified(json_text):
	"""
	Parse a json object into a dict with byte keys and values, instead of unicode strings.
	This is from (https://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-from-json),
	python 3 shouldn't have this problem probably
	Parameters:
		{str} json_text The json string object to parse
	Returns:
		{dict} The json object correctly parsed with byte keys and values
	"""
	return _byteify(json.loads(json_text, object_hook=_byteify), ignore_dicts=True)

def _byteify(data, ignore_dicts = False):
	# if this is a unicode string, return its string representation
	if isinstance(data, unicode):
		return data.encode('utf-8')
	# if this is a list of values, return list of byteified values
	if isinstance(data, list):
		return [ _byteify(item, ignore_dicts=True) for item in data ]
	# if this is a dictionary, return dictionary of byteified keys and values
	# but only if we haven't already byteified it
	if isinstance(data, dict) and not ignore_dicts:
		return {
			_byteify(key, ignore_dicts=True): _byteify(value, ignore_dicts=True)
			for key, value in data.iteritems()
		}
	# if it's anything else, return it in its original form
	return data