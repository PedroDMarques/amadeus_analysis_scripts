import datetime
import dateutil.parser
import pytz

def getSoftware(raw, parsed):
	if "distilFields" in raw:
		return "distil"
	elif any(x in raw for x in ["sessionScores", "exceededThresholds", "knownViolator", "exceededThresholdsCount"]):
		return "arcane"
	else:
		return "unknown"

def getSchema(software, device):
	return {
		"ignore_fields": ["orga", "phase", "userID", "regexFailure", "record"],
		"parse_fields": {
			"fields": {
				"timestamp": "epoch",
			},
			"parse": {
				## / 1e3 because it's coming from javascript so it includes milliseconds
				"timestamp": (lambda x: datetime.datetime.utcfromtimestamp(float(x) / 1e3))
			}
		},

		"scripted_fields": {
			"software": getSoftware,
		},

		"software_field": "software",
		"device_field": "software",
		"timestamp_field": "timestamp",
	}