import pickle
import sys
import tempfile

class TempList(object):
	"""
	List saved to temporary file
	Can be read back, but does not support changes to the internal list
	"""
	def __init__(self, l):
		"""
		After construction the list will be immediately saved to a temporary file, and not kept in memory
		Parameters:
			{list} l The list to save to memory
		"""
		self.l = None
		self.len = len(l)
		self.sizeof = sys.getsizeof(l)
		self.fh = tempfile.TemporaryFile()

		pickler = pickle.Pickler(self.fh)
		pickler.dump(l)

		self.fh.seek(0)

	def remember(self):
		"""
		Read the list from the temporary file into memory. If list is already in memory does nothing
		"""
		if self.isRemembered():
			return

		unpickler = pickle.Unpickler(self.fh)
		self.l = unpickler.load()

		self.fh.seek(0)

	def forget(self):
		"""
		Removes the list from memory
		"""
		self.l = None

	def isRemembered(self):
		"""
		Returns:
			{bool} True if the list is in memory, False otherwise
		"""
		return self.l != None

	def __len__(self):
		return self.len

	def __sizeof__(self):
		return self.sizeof

	def __iter__(self):
		self.remember()
		return self.l.__iter__()

	def __getitem__(self, key):
		self.remember()
		return self.l[key]

class VirtualList(object):
	def __init__(self, maxmem=500000000):
		self.l = list()
		self.maxmem = maxmem
		self.templists = list()

	def append(self, item):
		self.l.append(item)
		if self.maxmem and sys.getsizeof(self.l) > self.maxmem:
			self.shrink()

	def shrink(self):
		if len(self.l) > 0:
			self.templists.append(TempList(self.l))
			self.l = list()

	def __sizeof__(self):
		return sys.getsizeof(self.l)

	def __len__(self):
		return len(self.l) + sum([len(x) for x in self.templists])

	def __iter__(self):
		for temp in self.templists:
			for i in temp: yield i
			temp.forget()

		for i in self.l: yield i

class VirtualListDict(object):
	def __init__(self, maxmem=500000000, onShrink=None):
		self.d = dict()
		self.cursize = 0
		self.maxmem = maxmem
		self.onShrink = onShrink
		self.shrinkCount = 0

	def shrink(self):
		for key in self.d:
			self.d[key].shrink()

		self.cursize = 0
		self.shrinkCount += 1
		if callable(self.onShrink):
			self.onShrink(self.shrinkCount)

	def append(self, key, value):
		if key not in self.d:
			self.d[key] = VirtualList(maxmem=None)

		self.d[key].append(value)
	
		self.cursize += sys.getsizeof(value)
		if self.maxmem and self.cursize > self.maxmem:
			self.shrink()

	def __contains__(self, key):
		return key in self.d

	def __iter__(self):
		return self.d.__iter__()

	def __getitem__(self, key):
		return self.d[key]

	def __len__(self):
		return len(self.d)