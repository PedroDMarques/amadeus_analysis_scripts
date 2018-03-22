import datetime
import dateutil.parser
import pytz

def getSchema(software, device):
	return {
		"pre": lambda l: r"%s" % l,
		"ignore_fields": ["proto", "origin_ip", "source_port", "dest_ip", "dest_port", "timestamp", "ts", "sourceType", "sourcetype"],
		"parse_fields": {
			"fields": {
				"src_ip": "origin_ip",
				"src_port": "source_port",
				"dst_ip": "dest_ip",
				"dst_port": "dest_port",
				"timestamp": ["timestamp", "ts"],
				"protocol": "proto",
			},
			"parse": {
				"timestamp": (lambda x: datetime.datetime.utcfromtimestamp(float(x)).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: x.lower()),
			},
		},
		"scripted_fields": {
			"ip_pair": (lambda x, y: "%s -> %s" % (y.get("src_ip"), y.get("dst_ip"))),
			"port_pair": (lambda x, y: "%s -> %s" % (y.get("src_port"), y.get("dst_port"))),
			"ip_port_pair": (lambda x, y: "%s:%s -> %s:%s" % (y.get("src_ip"), y.get("src_port"), y.get("dst_ip"), y.get("dst_port"))),
			
			"des_software_type": (lambda x, y: software),
			"des_device_name": (lambda x, y: device),
		},

		"timestamp_field": "timestamp",
	}