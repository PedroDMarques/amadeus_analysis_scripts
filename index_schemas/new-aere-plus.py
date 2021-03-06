def getSchema():
	return {
		"settings": {
			"number_of_shards": 10,
			"number_of_replicas": 1,

			"index.mapping.ignore_malformed": True,
			"index.mapping.total_fields.limit": 10000,
		},

		"mappings": {
			"new-aere-plus": {
				"properties": {
					"timestamp": { "type": "date" },
					"ipMapLocation": { "type": "geo_point" },

					"distil_label": { "type": "boolean" },
					"arcane_label": { "type": "boolean" },
					"manual_label": { "type": "boolean" },

					#"arcane_reported": { "type": "boolean" },
					#"distil_reported": { "type": "boolean" },

					"epoch": { "type": "long" },
					"dcxID": { "type": "keyword" },
					"ipAddress": { "type": "ip" },

					"ipMap.clientIp": { "type": "ip" },
					"ipMap.areaCode": { "type": "keyword" },
					"ipMap.isp_asn": { "type": "keyword" },
					"ipMap.ipB": { "type": "ip" },
					"ipMap.ipC": { "type": "ip" },
					"ipMap.edgeProxyClip": { "type": "ip" },
					"ipMap.remoteClient": { "type": "ip" },
					"ipMap.xForwardedFor": { "type": "ip" },
					"ipMap.isp_org": { "type": "keyword" },
					"ipMap.countryCode": { "type": "keyword" },
					"ipMap.city": { "type": "keyword" },
					"ipMap.regionName": { "type": "keyword" },

					"httpHeaders.bytes_sent": { "type": "long" },
					"httpHeaders.httpMethod": { "type": "keyword" },
					"httpHeaders.contentLength": { "type": "long" },
					"httpHeaders.userAgent": { "type": "keyword" },
					"httpHeaders.httpStatus": { "type": "keyword" },
					"httpHeaders.http_accept": { "type": "keyword" },
					"httpHeaders.http_accept_encoding": { "type": "keyword" },
					"httpHeaders.http_accept_language": { "type": "keyword" },
					"httpHeaders.http_connection": { "type": "keyword" },
					"httpHeaders.http_request_length": { "type": "long" },
					"httpHeaders.status": { "type": "keyword" },
					
					"httpRequest.protocol": { "type": "keyword" },
					"httpRequest.hostname": { "type": "keyword" },
					"httpRequest.port": { "type": "keyword" },
					"httpRequest.path": { "type": "text" },
					"httpRequest.uri": { "type": "keyword" },
					"httpRequest.parseFailure": { "type": "boolean" },
					
					"httpReferer.protocol": { "type": "keyword" },
					"httpReferer.hostname": { "type": "keyword" },
					"httpReferer.port": { "type": "keyword" },
					"httpReferer.path": { "type": "text" },
					"httpReferer.uri": { "type": "keyword" },
					"httpReferer.parseFailure": { "type": "boolean" },

					"userAgent.ua": { "type": "keyword" },

					"processingDuration": { "type": "integer" },

					"distilFields.distilId": { "type": "keyword" },
					"distilFields.dZuid": { "type": "keyword" },
					"distilFields.dZid": { "type": "keyword" },
					"distilFields.xDistil": { "type": "keyword" },
					"distilFields.dHid": { "type": "keyword" },
					"distilFields.distilIsp": { "type": "keyword" },
					"distilFields.xInf": { "type": "keyword" },
					"distilFields.xDistilWhitelist": { "type": "keyword" },
					"distilFields.xDistilRequestId": { "type": "keyword" },
					"distilFields.dSid": { "type": "keyword" },

					"sessionScores.score": { "type": "double" },
					"knownViolator": { "type": "boolean" },
					"exceededThresholdsCount": { "type": "integer" }
				}
			}
		}
	}