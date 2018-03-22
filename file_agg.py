from os import listdir
from os.path import join, isdir, splitext, getsize
from utils import toFilename, fromFilename

def get_raw_data_files(raw_data_location,
	ignore_software=[],
	ignore_device=[],
	ignore_file_name=[],
	ignore_file_ext=[],
	minsize=False,
	maxsize=False,	
):
	"""
	Returns a tuple of list of raw data files and filtered raw data files
	Parameters:
		{str} raw_data_location The location of the raw data files
		{str[]} [ignore_software=list()] A list of software names to filter
		{str[]} [ignore_device=list()] A list of device names to filter
		{str[]} [ignore_file_name=list()] A list of file names to filter (without extention)
		{str[]} [ignore_file_ext=list()] A list of file extentions to filter
		{int} [minsize=False] The minimum size of a file, in bytes
		{int} [maxsize=False] The maximum size of a file, in bytes 
	Returns:
		(tuple[], tuple[]) Returns index 0 an array of data files and index 1 an array of filtered data files
		The format of the tuples are:
			data -> ((software, device, froot, fext, fpath))
			filtered -> ((fpath, reason)) 
	"""
	data = []
	filtered = []

	for software in listdir(raw_data_location):
		softwareLocation = join(raw_data_location, software)
		if not isdir(softwareLocation):
			continue
		
		for device in listdir(softwareLocation):
			deviceLocation = join(softwareLocation, device)
			if not isdir(deviceLocation):
				continue

			for fname in listdir(deviceLocation):
				fpath = join(deviceLocation, fname)
				if isdir(fpath):
					continue

				froot, fext = splitext(fname)
				fext = fext.replace(".", "")

				size = getsize(fpath)

				if software in ignore_software: filtered.append((fpath, "software"))
				elif device in ignore_device: filtered.append((fpath, "device"))
				elif froot in ignore_file_name: filtered.append((fpath, "name"))
				elif fext in ignore_file_ext: filtered.append((fpath, "extension"))
				elif minsize and size < minsize: filtered.append((fpath, "min size"))
				elif maxsize and size > maxsize: filtered.append((fpath, "max size"))
				else: data.append((software, device, froot, fext, fpath))

	return data, filtered

def get_parsed_data_files(parsed_data_location,
	ignore_software=[],
	ignore_device=[],
	minsize=False,
	maxsize=False,	
):
	"""
	Returns a tuple of list of parsed data files and filtered parsed data files
	Parameters:
		{str} parsed_data_location The location of the parsed data files
		{str[]} [ignore_software=list()] A list of software names to filter
		{str[]} [ignore_device=list()] A list of device names to filter
		{int} [minsize=False] The minimum size of a file, in bytes
		{int} [maxsize=False] The maximum size of a file, in bytes 
	Returns:
		(tuple[], tuple[]) Returns index 0 an array of data files and index 1 an array of filtered data files
		The format of the tuples are:
			data -> ((hour, software, device, fpath))
			filtered -> ((fpath, reason)) 
	"""
	data = []
	filtered = []

	for hour in listdir(parsed_data_location):
		hourLocation = join(parsed_data_location, hour)
		if not isdir(hourLocation):
			continue

		for fname in listdir(hourLocation):
			try:
				fpath = join(hourLocation, fname)
				if isdir(fpath):
					continue
				
				software, device = fromFilename(fname)
				size = getsize(fpath)

				if software in ignore_software: filtered.append((fpath, "software"))
				elif device in ignore_device: filtered.append((fpath, "device"))
				elif minsize and size < minsize: filtered.append((fpath, "min size"))
				elif maxsize and size > maxsize: filtered.append((fpath, "max size"))
				else: data.append((hour, software, device, fpath))

			## There was an error, most likely the file was not a software-device one
			except ValueError:
				continue

	return data, filtered

def get_collected_stats_data_files(collected_stats_data_location,
	ignore_software=[],
	ignore_device=[],	
):
	"""
	Returns a tuple of list of collected stats data files and filtered collected stats data files
	Parameters:
		{str} collected_stats_data_files The location of the collected stats data files
		{str[]} [ignore_software=list()] A list of software names to filter
		{str[]} [ignore_device=list()] A list of device names to filter
	Returns:
		(tuple[], tuple[]) Returns index 0 an array of data files and index 1 an array of filtered data files
		The format of the tuples are:
			data -> ((hour, software, device, fpath))
			filtered -> ((fpath, reason)) 
	"""
	data, filtered = [], []

	for hour in listdir(collected_stats_data_location):
		hourLocation = join(collected_stats_data_location, hour)
		if not isdir(hourLocation):
			continue
		
		for fname in listdir(hourLocation):
			try:
				fpath = join(hourLocation, fname)

				software, device = fromFilename(fname)
				if software in ignore_software: filtered.append((fpath, "software"))
				elif device in ignore_device: filtered.append((fpath, "device"))
				else: data.append((hour, software, device, fpath))

			## There was an error, most likely the file was not a software-device one
			except ValueError:
				continue

	return data, filtered