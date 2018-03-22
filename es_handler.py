from jsonutil import json_loads_byteified

global es
try:
	import elasticsearch
	import elasticsearch.helpers
	from elasticsearch import Elasticsearch
	global es
	es = Elasticsearch(timeout=300)
except:
	pass

class TimeoutError(ValueError):
	pass

class BulkIterator:
	def __init__(self, fh, index):
		self.fh = fh
		self.index = index

	def __iter__(self):
		return self

	def next(self):
		line = self.fh.readline()

		if not line:
			raise StopIteration()

		else:
			return {
				"_op_type": "index",
				"_index": self.index,
				"_type": self.index,
				"_source": json_loads_byteified(line)
			}

def createIndex(index, schema):
	es.indices.create(index=index, body=schema)

def deleteIndex(index):
	es.indices.delete(index=index, ignore=[400, 404])

def sendFile(index, fh)
	try:
		for ok, item in elasticsearch.helpers.streaming_bulk(es, BulkIterator(fh, index)):
			pass
	except elasticsearch.exceptions.ConnectionTimeout:
		raise TimeoutError