import json
import collections
import types
from jsonutil import json_loads_byteified as json_loads

def collect_file(fpath, savepath, schema):
	data = {
		"total_alerts": 0,
		"aggs": dict()
	}

	with open(fpath, "r") as infile:
		for line in infile:
			props = json_loads(line)
			data["total_alerts"] = data.get("total_alerts", 0) + 1

			for agg in schema["aggs"]:
				if agg not in data["aggs"]: data["aggs"][agg] = dict()

				if agg in props:
					value = props[agg]
					if not isinstance(value, collections.Hashable):
						value = tuple(value)

					if isinstance(value, collections.Iterable) and not isinstance(value, types.StringTypes):
						for k in value:
							k = str(k)
							data["aggs"][agg][k] = data["aggs"][agg].get(k, 0) + 1

					value = str(value)
					data["aggs"][agg][value] = data["aggs"][agg].get(value, 0) + 1

	with open(savepath, "w") as outfile:
		outfile.write(json.dumps(data))