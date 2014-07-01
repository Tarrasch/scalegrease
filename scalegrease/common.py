import argparse
import json
import logging
import logging.handlers
import os
import socket
import getpass
from scalegrease import system

# This module is for code common to scalegrease that is not system-level enough
# to be put in the system module


# TODO(arash): We've added so many arguments here now, I think it would be
# better to use an abstract class where the passed functions would be
# implemented methods instead.
def initialise(argv, extra_arguments_adder, log_path_infix):
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
    parse_config_common(config.get("common"), log_path_infix(args))
    return args, config, rest_argv


def parse_config_common(config, instantiated_log_path_infix):
    if config is None:
        logging.info('No "common" value is configured, skipping ...')
    else:
        parse_config_common_file_logger(config.get("file_logger"),
                                        instantiated_log_path_infix)


def parse_config_common_file_logger(config, instantiated_log_path_infix):
    if config is None:
        logging.info('No "file_logger" value is configured, skipping ...')
    else:
        # We add username so we're less likely to get permission issues
        path_prefix = "{config_stripped}/{username}/{short_hostname}/".format(
            config_stripped=config.rstrip("/"),
            username=getpass.getuser(),
            short_hostname=get_short_hostname(),
        )
        logging_directory = path_prefix + instantiated_log_path_infix
        try:
            system.mkdir_p(logging_directory)
        except:
            logging.exception("Could not create directory '%s' for log"
                              "files. Skipping", logging_directory)
            return

        # We include the process id since we can imagine multiple instances
        # writing to the same file
        FORMAT = '[%(process)d] %(asctime)-15s %(levelname)-6s %(message)s'
        total_path = logging_directory + "scalegrease.log"
        trfh_handler = (
            logging.handlers.TimedRotatingFileHandler(total_path,
                                                      when="midnight",
                                                      backupCount=100,
                                                      utc=True))
        trfh_handler.setFormatter(logging.Formatter(fmt=FORMAT))
        root_logger = logging.getLogger()
        root_logger.addHandler(trfh_handler)


def get_short_hostname():
    """ If hostname == 'lon4-abc.acme.net', return 'lon4-abc' """
    return socket.gethostname().split(".")[0]
