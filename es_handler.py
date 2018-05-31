from jsonutil import json_loads_byteified
import json

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
	def __init__(self, fh, index, pipeline):
		self.fh = fh
		self.index = index
		self.pipeline = pipeline

	def __iter__(self):
		return self

	def next(self):
		line = self.fh.readline()

		if not line:
			raise StopIteration()

		else:
			return {
				"_op_type": "index",
				"pipeline": self.pipeline if self.pipeline else None,
				"_index": self.index,
				"_type": self.index,
				"_source": json.loads(line)
			}

def createIndex(index, schema):
	es.indices.create(index=index, body=schema)

def deleteIndex(index):
	es.indices.delete(index=index, ignore=[400, 404])

def sendFile(index, fh, pipeline=None):
	try:
		for ok, item in elasticsearch.helpers.streaming_bulk(es, BulkIterator(fh, index, pipeline)):
			pass
	except elasticsearch.exceptions.ConnectionTimeout:
		raise TimeoutError("timeout")