import argparse
import json
import logging
import os
from scalegrease import system

# This module is for code common to scalegrease that is not system-level enough
# to be put in the system module


def initialise(argv, extra_arguments_adder):
    """ Code common to all scalegrease executables """
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", "-c", default="/etc/scalegrease.json",
                        help="Read configuration from CONFIG_FILE. "
                             "Environment variables in the content will be "
                             "expanded.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Increase debug verbosity")
    extra_arguments_adder(parser)
    args, rest_argv = parser.parse_known_args(argv[1:])
    if rest_argv[:1] == ['--']:
        # Argparse really should have removed it for us.
        rest_argv = rest_argv[1:]
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.info("Reading configuration from %s", args.config_file)
    config_file_contents = system.read_file(args.config_file)
    config_expanded = os.path.expandvars(config_file_contents)
    config = json.loads(config_expanded)
    logging.debug("Configuration read:\n%s", config)
    parse_config_common(config.get("common"))
    return args, config, rest_argv


def parse_config_common(config):
    if config is None:
        logging.info('No "common" value is configured, skipping ...')
    else:
        pass
