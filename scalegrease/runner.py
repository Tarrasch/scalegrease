import abc
import argparse
import logging
import random
import sys
import subprocess
import time

from scalegrease import deploy
from scalegrease import error
from scalegrease import system
from scalegrease import common


class RunnerBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def run_job(self, artifact_storage, argv):
        raise NotImplementedError()


# The defaul-runners are hardcoded to simplify deploying of scalegrease. If we
# would put these in the config files, the config file would need to change
# every time we move the Runners.
SCALEGREASE_RUNNERS = [
    "scalegrease.runners.luigi.LuigiRunner",
    "scalegrease.runners.hadoop.HadoopRunner",
    "scalegrease.runners.shell.ShellRunner"
]

def find_runner(runner_name, config):
    for rn in SCALEGREASE_RUNNERS + config.get('extra_runners', []):
        class_name = rn.split('.')[-1]
        if class_name.lower() == (runner_name.lower() + "runner"):
            clazz = system.load_class(rn)
            class_config = config.get(clazz.__name__)
            return clazz(class_config)


def run(runner_name, artifact_spec, runner_argv, config):
    runner = find_runner(runner_name, config)
    if runner is None:
        raise error.Error("Failed to find runner '%s'" % runner_name)
    artifact_storage = deploy.ArtifactStorage.resolve(artifact_spec)
    job_argv = artifact_storage.fetch(runner_argv)
    try:
        runner.run_job(artifact_storage, job_argv)
    except subprocess.CalledProcessError:
        logging.error("Runner %s failed" % runner_name)
        raise


def extra_arguments_adder(parser):
    parser.add_argument("--runner", "-r", required=True,
                        help="Specify runner to use, e.g. hadoop, luigi.  "
                             "It should match one of the runner names in the config, "
                             "with 'runner' removed.")
    parser.add_argument(
        "artifact",
        help="Specify Maven artifact to download and run, either on format "
             "group_id:artifact_id:version or group_id:artifact_id for latest version.")
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        )


def log_path_infix(args):
    artifact_spec = args.artifact
    # It is not a file path, just keep it as it is, otherwise, just keep the
    # basename of the jar
    cleaned_artifact_spec = artifact_spec.split("/")[-1]
    result = "runner/{runner_name}/{cleaned_artifact_spec}/".format(
        runner_name=args.runner,
        cleaned_artifact_spec=cleaned_artifact_spec,
    )
    if args.runner.lower() == 'luigi':
        task_ix = args.command.index('--task')
        result += args.command[task_ix + 1] + "/"
    return result


def main(argv):
    args, conf = common.initialise(argv, extra_arguments_adder, log_path_infix)

    if not args.no_random_delay and system.possible_cron():
        sleep_time = random.randint(0, 59)
        logging.info("Will sleep for %s secs for load balancing", sleep_time)
        time.sleep(sleep_time)
    else:
        logging.debug("Not doing the load balancing random sleep")

    try:
        run(args.runner, args.artifact, args.command, conf)
    except error.Error:
        logging.exception("Job failed")
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
