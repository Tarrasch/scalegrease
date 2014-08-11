import logging
import sys
from scalegrease import error
from scalegrease import system
from scalegrease import common


def extra_arguments_adder(_):
    pass


def log_path_infix(args):
    return "snatcher/"


def cron_install(conf):
    launcher_class = system.load_class(conf["launcher_class"])
    launcher = launcher_class(conf)
    launcher.snatch()


def main(argv):
    _args, conf = common.initialise(argv, extra_arguments_adder,
                                    log_path_infix)

    try:
        cron_install(conf['launch'])
    except error.Error as e:
        logging.error("Job failed: %s", e)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
