import datetime
import dateutil.parser
import pytz

def parseSessionDuraction(val):
	total = 0

	valSplit = val.split(" ")
	timeSplit = None
	if len(valSplit) > 1:
		timeSplit = valSplit[1]
		dayCount = valSplit[0].split("d")[0]
		if dayCount.isdigit():
			total += int(dayCount) * 24 * 60 * 60
	
	else:
		timeSplit = valSplit[0]

	ts = timeSplit.split(":")
	hourCount = ts[0].split("h")[0]
	if hourCount.isdigit():
		total += int(hourCount) * 60 * 60

	minuteCount = ts[1].split("m")[0]
	if minuteCount.isdigit():
		total += int(minuteCount) * 60

	secondCount = ts[2].split("s")[0]
	if secondCount.isdigit():
		total += int(secondCount)

	return total

def getSchema(software, device):
	return {
		"pre": lambda l: r"%s" % l,
		"ignore_fields": ["ip", "@timestamp", "type"],
		"parse_fields": {
			"fields": {
				"src_ip": "ip",
				"src_port": False,
				"dst_ip": False,
				"dst_port": False,
				"timestamp": "@timestamp",
				"protocol": False,
				"des_src_bytes": "bytes_received",
				"des_dst_bytes": "bytes_transmitted",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
			},
		},

		"scripted_fields": {
			"ip_pair": (lambda x, y: "%s -> %s" % (y.get("src_ip"), y.get("dst_ip"))),
			"port_pair": (lambda x, y: "%s -> %s" % (y.get("src_port"), y.get("dst_port"))),
			"ip_port_pair": (lambda x, y: "%s:%s -> %s:%s" % (y.get("src_ip"), y.get("src_port"), y.get("dst_ip"), y.get("dst_port"))),

			"des_total_bytes": (lambda x, y: (int(x["bytes_received"]) + int(x["bytes_transmitted"])) if "bytes_received" in x and x["bytes_received"].isdigit() and "bytes_transmitted" in x and x["bytes_transmitted"].isdigit() else None),
			"des_session_duration": (lambda x, y: parseSessionDuraction(x["session_duration"]) if "session_duration" in x else None),
			"des_software_type": (lambda x, y: software),
			"des_device_name": (lambda x, y: device),
		},

		"timestamp_field": "timestamp",
	}	