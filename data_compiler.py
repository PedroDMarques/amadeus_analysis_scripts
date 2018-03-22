from jsonutil import json_load_byteified as json_loads_file

def sumnested(target, source):
	n = dict(target)
	for k in source:
		value = 0
		if isinstance(source[k], dict):
			value = sumnested(n.get(k, dict()), source[k])
		
		else:
			value = source[k] + n.get(k, 0)

		n[k] = value

	return n

def compile_software(data):
	## Sort the data based on software
	data = sorted(data, key=lambda x: x[1])
	compiledata = dict()
	
	for hour, software, device, fpath in data:
		if software not in compiledata:
			compiledata[software] = {
				"mintime": None,
				"maxtime": None,
				"unique_devices": set(),
				"data": dict()
			}


		if hour < compiledata[software]["mintime"] or compiledata[software]["mintime"] == None:
			compiledata[software]["mintime"] = hour

		if hour > compiledata[software]["maxtime"] or compiledata[software]["maxtime"] == None:
			compiledata[software]["maxtime"] = hour

		compiledata[software]["unique_devices"].add(device)

		with open(fpath, "r") as infile:
			props = json_loads_file(infile)
			compiledata[software]["data"] = sumnested(compiledata[software]["data"], props)

	return compiledata

def compile_device(data):
	data = sorted(data, key=lambda x: x[2])
	compiledata = dict()

	for hour, software, device, fpath in data:
		if device not in compiledata:
			compiledata[device] = {
				"mintime": None,
				"maxtime": None,
				"unique_softwares": set(),
				"data": dict()
			}

		if hour < compiledata[device]["mintime"] or compiledata[device]["mintime"] == None:
			compiledata[device]["mintime"] = hour

		if hour > compiledata[device]["maxtime"] or compiledata[device]["maxtime"] == None:
			compiledata[device]["maxtime"] = hour

		compiledata[device]["unique_softwares"].add(software)

		with open(fpath, "r") as infile:
			props = json_loads_file(infile)
			compiledata[device]["data"] = sumnested(compiledata[device]["data"], props)

	return compiledata