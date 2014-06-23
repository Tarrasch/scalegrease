import argparse
import json
import logging
import os
import subprocess


class CalledProcessError(subprocess.CalledProcessError):
    """
    Python 2.6 subprocess.CalledProcessError has no "output" property.
    """
    def __init__(self, returncode, cmd, output=None):
        super(CalledProcessError, self).__init__(returncode, cmd)
        self.output = output

    def __str__(self):
        return super(CalledProcessError, self).__str__() + ('\nOutput:\n"""\n%s"""' % self.output)


def check_output(cmd, env=None):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    output, _ = process.communicate()
    exit_code = process.poll()
    if exit_code:
        raise CalledProcessError(exit_code, cmd, output=output)
    return output


def run_with_logging(cmd, env=None):
    """
    Run cmd and wait for it to finish. While cmd is running, we read it's
    output and print it to a logger.
    """
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=env)
    logger = logging.getLogger('subprocess.{0}'.format(cmd[0]))
    output_lines = []
    while True:
        line = process.stdout.readline().rstrip('\n')
        if not line:
            break
        output_lines += [line]
        logger.info(line)

    exit_code = process.poll()
    if exit_code:
        output = '\n'.join(output_lines)
        raise CalledProcessError(exit_code, cmd, output=output)
    return None


def write_file(path, content):
    f = open(path, "w")
    with f:
        f.write(content)


def read_file(path):
    f = open(path)
    with f:
        return f.read()


def load_class(rn):
    module_name, class_name = rn.rsplit('.', 1)
    mod = __import__(module_name, globals(), locals(), [class_name])
    clazz = getattr(mod, class_name)
    return clazz


def initialise(argv, extra_arguments_adder):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", "-c", default="/etc/scalegrease.json",
                        help="Read configuration from CONFIG_FILE. "
                             "Environment variables in the content will be expanded.")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Increase debug verbosity")
    extra_arguments_adder(parser)
    args, rest_argv = parser.parse_known_args(argv[1:])
    if rest_argv[:1] == ['--']:
        # Argparse really should have removed it for us.
        rest_argv = rest_argv[1:]
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.info("Reading configuration from %s", args.config_file)
    config_file_contents = read_file(args.config_file)
    config_expanded = os.path.expandvars(config_file_contents)
    config = json.loads(config_expanded)
    logging.debug("Configuration read:\n%s", config)
    return args, config, rest_argv
