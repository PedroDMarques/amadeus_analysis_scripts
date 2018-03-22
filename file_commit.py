import os.path

def commit(path, identifier):
	with open(path, "a+") as fh:
		fh.write("%s\n" % identifier)

def isCommitted(path, identifier):
	if os.path.exists(path):
		with open(path, "r") as fh:
			for line in fh:
				if identifier == line.split("\n")[0]:
					return True

	return False