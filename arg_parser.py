import argparse

def parse():
	parser = argparse.ArgumentParser(
		description="Script description here"
	)

	parser.add_argument(
		"action",
		choices=[
			"install",
			"parse", "list",
			"parse-diversity",
			"collect-stats",
			"compile-stats", "plot",
		]
	)

	parser.add_argument(
		"-v",
		"--verbose",
		action="count",
		help="-v help"
	)

	parser.add_argument(
		"-c",
		"--config",
		default="config.cfg",
		dest="config_path",
		help="-c help"
	)

	parser.add_argument(
		"-f",
		"--force",
		action="store_true"
	)

	parser.add_argument(
		"--min-size",
		default=False,
		dest="minsize",
		type=int,
		help="--min-size help"
	)

	parser.add_argument(
		"--max-size",
		default=False,
		dest="maxsize",
		type=int,
		help="--max-size help"
	)

	## Compile arguments
	parser.add_argument(
		"--compile-software",
		action="store_true"
	)

	parser.add_argument(
		"--compile-device",
		action="store_true"
	)

	d = parser.parse_args()
	return d