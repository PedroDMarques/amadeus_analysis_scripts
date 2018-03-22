def toFilename(software, device):
	"""
	Get file name based on software and device information supplied
	Use 'fromFilename' to retrieve back software and device information from the resulting filename
	Paramaters:
		{str} software The software name
		{str} device The device name
	Returns:
		{str} A file name based on the software and device
	"""
	return "%s-%s" % (software, device)

def fromFilename(fname):
	"""
	Get software and device information based on the supplied file name
	Use 'toFilename' to retrieve back file name from the resulting software and device name
	Parameters:
		{str} fname The file name to extract software and device information from
	Returns:
		(str, str) Software and device tuple (in order software, device)
	"""
	return fname.split("-")