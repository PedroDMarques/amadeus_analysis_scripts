def getSchema(software, device):
	return {
		"diversity_key": "ip_port_pair",
		"fields": ["timestamp", "protocol"],
	}