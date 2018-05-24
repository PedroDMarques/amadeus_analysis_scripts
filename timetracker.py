class Timetracker():
	def __init__(self):
		self.trackings = 0
		self.sum_times = 0
		self.sum_sizes = 0

	def update(self, time, size):
		self.sum_times += time
		self.sum_sizes += size
		self.trackings += 1

	def estimate(self, size):
		try:
			if size == 0:
				return -1

			if self.trackings == 0:
				return -1

			avgTime = self.sum_times / self.trackings
			avgSize = self.sum_sizes / self.trackings

			return (avgTime/avgSize) * size
		except ZeroDivisionError:
			return -1