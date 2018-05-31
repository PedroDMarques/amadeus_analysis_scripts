import importlib
import time
import os
import os.path
import collections
import types
import json
from os.path import getsize
from random import randint

from print_util import colorLog
from utils import toFilename, fromFilename

import arg_parser
import config_parser
import file_agg
import file_commit
import data_parser
import data_collector
import data_compiler
import es_handler
from timetracker import Timetracker

REQUIRED_SCHEMA_PROPERTIES = {
	"parsing": ["timestamp_field"],
	"collection": ["aggs"],
	"diversity": ["diversity_key"],
}

COMMITNAME_PARSE = "meta-commit-parsed"
LOCATION_PARSE = "parsed"

COMMITNAME_PARSE_DIVERSITY = "meta-commit-parsed-diversity"
LOCATION_PARSE_DIVERSITY = "parsed-diversity"

COMMITNAME_COLLECT_STATS = "meta-commit-collected-stats"
LOCATION_COLLECT_STATS = "stats"

COMMITNAME_COLLECT_DIVERSITY = "meta-commit-collected-diversity"
LOCATION_COLLECT_DIVERSITY = "diversity"

COMMITNAME_ES_SEND = "meta-commit-es-send"

def esCreateIndex(args, config):
	"""
	Create elasticsearch index
	"""
	global es

	index = config["es_index"]
	schema = getIndexSchema(index)
	es_handler.createIndex(index, schema)

def esDeleteIndex(args, config):
	"""
	Delete elasticsearch index
	"""
	global es

	index = config["es_index"]
	es_handler.deleteIndex(index)
	

def esSend(args, config):
	"""
	Send parsed data to elasticsearch
	"""
	global es

	index = config["es_index"]
	timetracker = Timetracker()
	parsedlocation = os.path.join(config["parsed_data_location"], LOCATION_PARSE)
	commit_filepath = os.path.join(config["parsed_data_location"], COMMITNAME_ES_SEND)

	data, filtered = file_agg.get_parsed_data_files(parsedlocation,
		ignore_software=config["ignore_software"],
		ignore_device=config["ignore_device"],
		minsize=args.minsize,
		maxsize=args.maxsize
	)

	if args.verbose > 0:
		for fpath, reason in filtered:
			print colorLog("danger", "%s | Filtered based on %s" % (fpath, reason))

		for _, _, _, fpath in data:
			print colorLog("info", "%s | Ready for sending" % fpath)

	print colorLog("info-2", "%d data files filtered" % len(filtered))
	print colorLog("info-2", "%d data files ready for sending" % len(data))
	print colorLog("info-2", "Starting elasticsearch sending process")

	for hour, software, device, fpath in data:
		# Fail if the file was already parsed and the user is not forcing it
		if file_commit.isCommitted(commit_filepath, fpath) and not args.force:
			print colorLog("danger", "Did not send %s because it has already been sent before" % fpath)
			continue

		size = getsize(fpath)
		print colorLog("info", "Sending %s %s" % (fpath, "[%d bytes]" % size if args.verbose > 0 else ""))
		print colorLog("info", "Estimated to take %d seconds to complete" % timetracker.estimate(size))
		startTime = time.time()

		with open(fpath, "r") as fh:
			try:
				es_handler.sendFile(index, fh, config["es-pipeline"])
			except es_handler.TimeoutError:
				print colorLog("danger", "Timeout error occurred. Continuing...")

		elapsed_seconds = time.time() - startTime
		print colorLog("info", "Finished sending. Took %s" % round(elapsed_seconds, 3))
		timetracker.update(elapsed_seconds, size)

		# Commit if we haven't commited it before (might have committed it before with -f)
		if not file_commit.isCommitted(commit_filepath, fpath):
			file_commit.commit(commit_filepath, fpath)

def createlocation(location):
	"""
	Creates a location if it does not already exist
	Parameters:
		{str|str[]} location The location to create
	"""
	if isinstance(location, collections.Iterable) and not isinstance(location, types.StringTypes):
		map(createlocation, location)

	elif not os.path.exists(location):
		os.makedirs(location)

def getIndexSchema(name):
	"""
	Get the dictionary used to create an elasticsearch index
	Parameters:
		{str} name The name of the index to get
	Returns:
		{dict} The index options
	"""
	try:
		schema = importlib.import_module("index_schemas.%s" % name).getSchema()
		return json.dumps(schema)

	except ImportError:
		print "Could not find schema for index '%s'. Read readme for more information" % name
		exit(-1)
	
	except AttributeError:
		print "Schema module for index '%s' does not expose a 'getSchema' function. Read readme for more information" % name
		exit(-1)


def getschema(schema_type, software, device):
	"""
	Get the parsing schema for a specified software
	Parameters:
		{str} schema_type The type of the schema to get. Acceptable values are "parsing", "collection", "diversity"
		{str} software The name of the software to get the parsing schema for
		{str} device The name of the device to get the parsing schema for
	Returns:
		{dict} The parsing schema for the software specified

	Todo: Should probably launch an error if the schema_type provided does not conform to the acceptable values, instead of just returning None like currently
	"""
	if schema_type == "parsing": foldername = "parsing_schemas"
	elif schema_type == "collection": foldername = "collection_schemas"
	elif schema_type == "diversity": foldername = "diversity_schemas"
	else:
		return None

	try:
		schema = importlib.import_module("%s.%s" % (foldername, software)).getSchema(software, device)
		missing_keys = [x for x in REQUIRED_SCHEMA_PROPERTIES[schema_type] if x not in schema]
		if len(missing_keys) > 0:
			print "Schema for software '%s' is missing the following required properties. Read readme for more information\n" % software, missing_keys
			exit(-1)
		
		return schema
	
	except ImportError:
		print "Could not find schema for software '%s'. Read readme for more information" % software
		exit(-1)
	
	except AttributeError:
		print "Schema module for software '%s' does not expose a 'getSchema' function. Read readme for more information" % software
		exit(-1)

def install(args):
	"""
	Create config file for later use of the scripts
	"""
	config_parser.write(args.config_path)
	exit(0)

def parse(args, config):
	"""
	Script parse action
	Parameters:
		{namespace} args The arguments supplied for the script
		{dict} config The configuration supplied for the script
	"""
	timetracker = Timetracker()
	rawlocation = config["raw_data_location"]
	savelocation = os.path.join(config["parsed_data_location"], LOCATION_PARSE)
	commit_filepath = os.path.join(config["parsed_data_location"], COMMITNAME_PARSE)

	data, filtered = file_agg.get_raw_data_files(rawlocation,
		ignore_software=config["ignore_software"],
		ignore_device=config["ignore_device"],
		ignore_file_name=config["ignore_file_name"],
		ignore_file_ext=config["ignore_file_ext"],
		minsize=args.minsize,
		maxsize=args.maxsize,
	)

	if args.verbose > 0:
		for fpath, reason in filtered:
			print colorLog("danger", "%s | Filtered based on %s" % (fpath, reason))

		for _, _, _, _, fpath in data:
			print colorLog("info", "%s | Ready for parsing" % fpath)

	print colorLog("info-2", "%d data files filtered" % len(filtered))
	print colorLog("info-2", "%d data files ready for parsing" % len(data))
	print colorLog("info-2", "Starting parsing process")

	for software, device, _, _, fpath in data:
		# Fail if the file was already parsed and the user is not forcing it
		if file_commit.isCommitted(commit_filepath, fpath) and not args.force:
			print colorLog("danger", "Did not parse %s because it has already been parsed before" % fpath)
			continue

		size = getsize(fpath)
		print colorLog("info", "Parsing %s %s" % (fpath, "[%d bytes]" % size if args.verbose > 0 else ""))
		print colorLog("info", "Estimated to take %d seconds to complete" % timetracker.estimate(size))
		startTime = time.time()

		schema = getschema("parsing", software, device)
		data_parser.parse_file(fpath, savelocation, schema,
			originalSoftware=software,
			originalDevice=device,
			getOutFileName=(lambda s,d: "%s-%s" % (s, d))
		)

		elapsed_seconds = time.time() - startTime
		print colorLog("info", "Finished parsing. Took %s" % round(elapsed_seconds, 3))
		timetracker.update(elapsed_seconds, size)

		# Commit if we haven't commited it before (might have committed it before with -f)
		if not file_commit.isCommitted(commit_filepath, fpath):
			file_commit.commit(commit_filepath, fpath)

def parse_diversity(args, config):
	"""
	Script parse-diversity action
	Parameters:
		{namespace} args The arguments supplied to the script
		{dict} config The configuration supplied to the script
	"""
	timetracker = Timetracker()
	parsedlocation = os.path.join(config["parsed_data_location"], LOCATION_PARSE)
	savelocation = os.path.join(config["parsed_data_location"], LOCATION_PARSE_DIVERSITY)
	commit_filepath = os.path.join(config["parsed_data_location"], COMMITNAME_PARSE_DIVERSITY)

	data, filtered = file_agg.get_parsed_data_files(parsedlocation,
		ignore_software=config["ignore_software"],
		ignore_device=config["ignore_device"],
		minsize=args.minsize,
		maxsize=args.maxsize
	)

	if args.verbose > 0:
		for fpath, reason in filtered:
			print colorLog("danger", "%s | Filtered based on %s" % (fpath, reason))

		for _, _, _, fpath in data:
			print colorLog("info", "%s | Ready for parsing" % fpath)

	for hour, software, device, fpath in data:
		# Fail if the file was already parsed and the user is not forcing it
		if file_commit.isCommitted(commit_filepath, fpath) and not args.force:
			print colorLog("danger", "Did not parse %s because it has already been parsed before" % fpath)
			continue

		size = getsize(fpath)
		print colorLog("info", "Parsing %s %s" % (fpath, "[%d bytes]" % size if args.verbose > 0 else ""))
		print colorLog("info", "Estimated to take %d seconds to complete" % timetracker.estimate(size))
		startTime = time.time()

		schema = getschema("diversity", software, device)
		hourlocation = os.path.join(savelocation, hour)
		createlocation(hourlocation)
		
		savepath = os.path.join(hourlocation, toFilename(software, device))
		data_parser.parse_diversity(fpath, savepath, schema)

		elapsed_seconds = time.time() - startTime
		print colorLog("info", "Finished parsing. Took %s" % round(elapsed_seconds, 3))
		timetracker.update(elapsed_seconds, size)

		# Commit if we haven't commited it before (might have committed it before with -f)
		if not file_commit.isCommitted(commit_filepath, fpath):
			file_commit.commit(commit_filepath, fpath)

def listFiles(args, config):
	"""
	Script list action
	Parameters:
		{namespace} args The arguments supplied to the script
		{dict} config The configuration supplied to the script
	"""
	rawlocation = config["raw_data_location"]

	data, filtered = file_agg.get_raw_data_files(rawlocation,
		ignore_software=config["ignore_software"],
		ignore_device=config["ignore_device"],
		ignore_file_name=config["ignore_file_name"],
		ignore_file_ext=config["ignore_file_ext"],
		minsize=args.minsize,
		maxsize=args.maxsize,
	)

	for fpath, reason in filtered:
		size = getsize(fpath)
		print colorLog("danger", "%s [%d bytes] | Filtered based on %s" % (fpath, size, reason))

	for _, _, _, _, fpath in data:
		size = getsize(fpath)
		print colorLog("info", "%s [%d bytes]" % (fpath, size))

	print colorLog("info-2", "%d data files filtered" % len(filtered))
	print colorLog("info-2", "%d data files accepted" % len(data))

def collect_stats(args, config):
	"""
	Script collect-stats action
	Parameters:
		{namespace} args The arguments supplied to the script
		{dict} config The configuration supplied to the script
	"""
	timetracker = Timetracker()
	parsedlocation = os.path.join(config["parsed_data_location"], LOCATION_PARSE)
	savelocation = os.path.join(config["collected_data_location"], LOCATION_COLLECT_STATS)
	commit_filepath = os.path.join(config["collected_data_location"], COMMITNAME_COLLECT_STATS)

	data, filtered = file_agg.get_parsed_data_files(parsedlocation,
		ignore_software=config["ignore_software"],
		ignore_device=config["ignore_device"],
		minsize=args.minsize,
		maxsize=args.maxsize
	)

	if args.verbose > 0:
		for fpath, reason in filtered:
			print colorLog("danger", "%s | Filtered based on %s" % (fpath, reason))

		for _, _, _, fpath in data:
			print colorLog("info", "%s | Ready for collection" % fpath)

	print colorLog("info-2", "%d data files filtered" % len(filtered))
	print colorLog("info-2", "%d data files ready for collection" % len(data))
	print colorLog("info-2", "Starting collection process")

	for hour, software, device, fpath in data:
		# Fail if the file was already parsed and the user is not forcing it
		if file_commit.isCommitted(commit_filepath, fpath) and not args.force:
			print colorLog("danger", "Did not collect %s because it has already been collected before" % fpath)
			continue

		size = getsize(fpath)
		print colorLog("info", "Collecting %s %s" % (fpath, "[%d bytes]" % size if args.verbose > 0 else ""))
		print colorLog("info", "Estimated to take %d seconds to complete" % timetracker.estimate(size))
		startTime = time.time()

		schema = getschema("collection", software, device)
		savehourlocation = os.path.join(savelocation, hour)
		if not os.path.exists(savehourlocation):
			os.makedirs(savehourlocation)

		savepath = os.path.join(savehourlocation, "%s-%s" % (software, device))
		data_collector.collect_file(fpath, savepath, schema)

		elapsed_seconds = time.time() - startTime
		print colorLog("info", "Finished collecting. Took %s" % round(elapsed_seconds, 3))
		timetracker.update(elapsed_seconds, size)

		# Commit if we haven't commited it before (might have committed it before with -f)
		if not file_commit.isCommitted(commit_filepath, fpath):
			file_commit.commit(commit_filepath, fpath)

def collect_diversity(args, config):
	"""
	Script collect-diversity action
	Parameters:
		{namespace} args The arguments supplied to the script
		{dict} config The configuration supplied to the script
	"""
	pass

def compile_stats(args, config):
	"""
	Script compile-stats action
	Parameters:
		{namespace} args The arguments supplied to the script
		{dict} config The configuration supplied to the script
	"""
	collectedlocation = os.path.join(config["collected_data_location"], LOCATION_COLLECT_STATS)

	data, filtered = file_agg.get_collected_stats_data_files(collectedlocation,
		ignore_software=config["ignore_software"],
		ignore_device=config["ignore_device"]
	)

	if args.verbose > 0:
		for fpath, reason in filtered:
			print colorLog("danger", "%s | Filtered based on %s" % (fpath, reason))

		for _, _, _, fpath in data:
			print colorLog("info", "%s | Will be used for compilation" % fpath)

	if args.compile_software:
		print ""
		compiledata = data_compiler.compile_software(data)
		for software in compiledata:
			print "%s - [%s, %s]" % (software, compiledata[software]["mintime"], compiledata[software]["maxtime"])
			print "Devices = %s" % compiledata[software]["unique_devices"]
			printDataDeep(compiledata[software]["data"])
			print ""

	if args.compile_device:
		print ""
		compiledata = data_compiler.compile_device(data)
		for device in compiledata:
			print "%s - [%s, %s]" % (device, compiledata[device]["mintime"], compiledata[device]["maxtime"])
			print "Softwares = %s" % compiledata[device]["unique_softwares"]
			printDataDeep(compiledata[device]["data"])
			print ""

def printDataDeep(d, indent=0):
	for k in d:
		if isinstance(d[k], dict):
			print (" " * indent) + k
			printDataDeep(d[k], indent+4)
		else:
			print (" " * indent) + ("%s = %d" % (k, d[k]))

if __name__ == "__main__":
	
	args = arg_parser.parse()

	if args.action == "install": install(args)
	else:
		config = config_parser.read(args.config_path)

		createlocation([
			config["raw_data_location"],
			os.path.join(config["parsed_data_location"], LOCATION_PARSE),
			os.path.join(config["parsed_data_location"], LOCATION_PARSE_DIVERSITY),
			os.path.join(config["collected_data_location"], LOCATION_COLLECT_STATS),
			os.path.join(config["collected_data_location"], LOCATION_COLLECT_DIVERSITY),
		])

		if args.action == "parse": parse(args, config)
		elif args.action == "parse-diversity": parse_diversity(args, config)
		elif args.action == "list": listFiles(args, config)
		elif args.action == "collect-stats": collect_stats(args, config)
		elif args.action == "collect-diversity": collect_diversity(args, config)
		elif args.action == "compile-stats": compile_stats(args, config)
		elif args.action == "es-create": esCreateIndex(args, config)
		elif args.action == "es-delete": esDeleteIndex(args, config)
		elif args.action == "es-send": esSend(args, config)