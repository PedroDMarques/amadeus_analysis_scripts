import datetime
import dateutil.parser
import pytz

def getSchema(software, device):
	return {
		"pre": lambda l: r"%s" % l,
		"ignore_fields": ["proto", "src", "srcPort", "dst", "dstPort", "datetime", "totalBytes", "DeviceName", "sourceType", "ElapsedTime"],
		"parse_fields": {
			"fields": {
				"src_ip": "src",
				"src_port": "srcPort",
				"dst_ip": "dst",
				"dst_port": "dstPort",
				"timestamp": "datetime",
				"protocol": "proto",
				"des_total_bytes": "totalBytes",
				"des_src_bytes": "srcBytes",
				"des_dst_bytes": "dstBytes",
				"des_session_duration": "ElapsedTime",
			},
			"parse": {
				"timestamp": (lambda x: dateutil.parser.parse(x).replace(tzinfo=pytz.utc).isoformat()),
				"protocol": (lambda x: x.lower()),
			},
		},

		"scripted_fields": {
			"ip_pair": (lambda x, y: "%s -> %s" % (y.get("src_ip"), y.get("dst_ip"))),
			"port_pair": (lambda x, y: "%s -> %s" % (y.get("src_port"), y.get("dst_port"))),
			"ip_port_pair": (lambda x, y: "%s:%s -> %s:%s" % (y.get("src_ip"), y.get("src_port"), y.get("dst_ip"), y.get("dst_port"))),
			
			"des_software_type": (lambda x, y: software),
			"des_device_name": (lambda x, y: x["DeviceName"] if "DeviceName" in x else device),
		},

		"timestamp_field": "timestamp",
	}