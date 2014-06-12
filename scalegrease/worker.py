import logging
import shutil
import sys
import os
from scalegrease import error
from scalegrease import system


def extra_arguments(_):
    pass


def cron_install(conf):
    cron_src_dir = conf["crontab_repository_dir"]
    cron_dst_dir = conf["crontab_etc_crond"]
    prefix = conf["crontab_unique_prefix"]
    new_crontabs = os.listdir(cron_src_dir)
    existing_crontabs = filter(lambda ct: ct.startswith(prefix), os.listdir(cron_dst_dir))
    for existing in existing_crontabs:
        if existing[len(prefix):] not in new_crontabs:
            stale_path = "{0}/{1}".format(cron_dst_dir, existing)
            logging.info("rm %s", stale_path)
            try:
                os.remove(stale_path)
            except IOError as e:
                logging.error("Failed to remove %s", stale_path, e)
    for new_tab in new_crontabs:
        src_path = "{0}/{1}".format(cron_src_dir, new_tab)
        dst_path = "{0}/{1}{2}".format(cron_dst_dir, prefix, new_tab)
        if not os.path.isfile(dst_path) or system.read_file(src_path) != system.read_file(dst_path):
            logging.info("cp %s %s", src_path, dst_path)
            try:
                shutil.copy2(src_path, dst_path)
            except IOError as e:
                logging.error("Failed to install %s as %s", src_path, dst_path, e)


def main(argv):
    args, conf, rest_argv = system.initialise(argv, extra_arguments)

    try:
        cron_install(conf['launch'])
    except error.Error as e:
        logging.error("Job failed: %s", e)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
