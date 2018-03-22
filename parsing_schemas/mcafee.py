import datetime
import dateutil.parser
import pytz

def getSchema(software, device):
	return {
		# Need this hack for the macfee data
		"pre": lambda l: r"%s" % l,

		"ignore_fields": ["src_ip", "dest_ip", "datetime"],
		"parse_fields": {
			"fields": {
				"src_ip": "src_ip",
				"src_port": False,
				"dst_ip": "dest_ip",
				"dst_port": False,
				"timestamp": "datetime",
				"protocol": False,
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
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