import logging
import re
import os
import glob
import abc

from scalegrease import error
from scalegrease import system


def maven_output(mvn_cmd):
    lines = system.check_output(mvn_cmd).splitlines()
    # Filter out log output and dowload output.
    return '\n'.join(
        filter(lambda li: not re.match(r"^(\[(INFO|DEBUG)\]|Downloading: |[0-9]+ )", li), lines))


def launch(crontab_glob, pom_file, offline, conf):
    offline_flag = ["--offline"] if offline else []
    all_crontabs = glob.glob(crontab_glob)
    if not all_crontabs:
        logging.warn("No crontab files found matching '%s', pwd=%s.  Existing production crontabs "
                     "will be deleted", crontab_glob, os.getcwd())
    # Now, it would be great if maven could spit out structured output.  This is fragile.
    group_output = maven_output(["mvn"] + offline_flag + ["--file", pom_file, "help:evaluate",
                                                          "-Dexpression=project.groupId"])
    group_match = re.search(r"^[^\.]+(\.[^\.]+)*$", group_output, re.MULTILINE)
    group_id = group_match.group()
    logging.info("Determined groupId: %s", group_id)
    artifact_output = maven_output(
        ["mvn"] + offline_flag + ["--file", pom_file, "help:evaluate",
                                  "-Dexpression=project.artifactId"])
    artifact_match = re.search(r"^[^\.]+(\.[^\.]+)*$", artifact_output, re.MULTILINE)
    artifact_id = artifact_match.group()
    logging.info("Determined artifactId: %s", artifact_id)

    launch_conf = conf['launch']
    launcher_class = system.load_class(launch_conf["launcher_class"])
    launcher = launcher_class(launch_conf)
    launcher.launch(group_id, artifact_id, all_crontabs)


class Launcher(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def launch(self, group_id, artifact_id, crontabs):
        raise NotImplementedError()


class SshNfsLauncher(Launcher):
    def launch(self, group_id, artifact_id, crontabs):
        repo_host = self._config['crontab_repository_host']
        repo_dir = self._config['crontab_repository_dir']

        clean_cmd = ["ssh", repo_host, "rm", "-f",
                     "%s/%s__%s__*" % (repo_dir, group_id, artifact_id)]
        logging.info("Removing old crontabs: %s", ' '.join(clean_cmd))
        clean_output = system.check_output(clean_cmd)
        logging.info("Ssh output: %s", clean_output)

        for crontab in crontabs:
            dst_name = "__".join([group_id, artifact_id, os.path.basename(crontab)])
            scp_cmd = ["scp", crontab, "%s:%s/%s" % (repo_host, repo_dir, dst_name)]
            logging.info(' '.join(scp_cmd))
            scp_output = system.check_output(scp_cmd)
            logging.info("Scp output: %s" % scp_output)


def add_arguments(parser):
    parser.add_argument("--cron-glob", "-g", default="src/main/cron/*.cron",
                        help="Glob pattern for enumerating cron files")
    parser.add_argument("--mvn-offline", "-o", action="store_true",
                        help="Use Maven in offline mode")
    parser.add_argument("--pom-file", "-p", default="pom.xml",
                        help="Path to project pom file")


def main(argv):
    args, conf, _ = system.initialise(argv, add_arguments)

    try:
        launch(args.cron_glob, args.pom_file, args.mvn_offline, conf)
    except error.Error:
        logging.exception("Job failed")
        return 1
