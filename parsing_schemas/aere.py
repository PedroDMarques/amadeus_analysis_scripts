import datetime
import dateutil.parser
import pytz

def arcane_reported(raw, parsed):
	score = raw.get("sessionScores", dict()).get("score", 0)
	knownViolator = raw.get("knownViolator")
	exceededThresholdsCount = raw.get("exceededThresholdsCount", 0)
	
	return (score >= 7.5 and score <=10) or \
		knownViolator == True or \
		knownViolator == "true" or \
		exceededThresholdsCount > 0

def distil_reported(raw, parsed):
	distilId = raw.get("distilFields", dict()).get("distilId", "0")
	distilWhitelist = raw.get("distilFields", dict()).get("xDistilWhitelist", None)

	return distilId.isdigit() and \
		int(distilId) > 0 and \
		distilWhitelist.isdigit() and \
		int(distilWhitelist) == 0

def getLocation(raw, parsed):
	location = ""

	if "ipMap" in raw:
		ipMap = raw.get("ipMap")
		if "latitude" in ipMap and "longitude" in ipMap:
			location = "%s,%s" % (ipMap.get("latitude"), ipMap.get("longitude"))

	return location

def skip(raw_props):
	p = raw_props.get("httpRequest", dict()).get("path", "")
	
	return p.endswith("css") or \
		p.endswith("js") or \
		p.endswith("woff") or \
		p.endswith("jpg") or \
		p.endswith("gif") or \
		p.endswith("ico") or \
		p.endswith("png") or \
		p.endswith("ttf") or \
		p.endswith("eot") or \
		p.endswith("js_validate.html") or \
		p.endswith("captcha.html") or \
		p.endswith("drop.html") or \
			(
				"/plxnext/" in p and \
				"/default/" in p and \
				"/merci/" in p and \
				"/static/" in p
			)

def getSchema(software, device):
	return {
		"skip": skip,
		
		"ignore_fields": ["orga", "phase", "userID", "regexFailure", "record"],
		"parse_fields": {
			"fields": {
				"timestamp": "epoch",
			},
			"parse": {
				## / 1e3 because it's coming from javascript so it includes milliseconds
				"timestamp": (lambda x: datetime.datetime.utcfromtimestamp(float(x) / 1e3).replace(tzinfo=pytz.utc).isoformat())
			}
		},

		"scripted_fields": {
			#"arcane_reported": arcane_reported,
			#"distil_reported": distil_reported,
			"ipMapLocation": getLocation,
		},

		"timestamp_field": "timestamp",
	}