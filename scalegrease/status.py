"""
A simple module that just prints the cron files installed on the machine in a
pretty way.

greasestatus is currently an unfinished dirty hack! Don't rely on its existence.
"""
import sys
import os
import re

from scalegrease import system

CRON_DIR = "/etc/cron.d/"  # TODO(Tarrasch): Make it read the config


def get_cron_files():
    """
    ls /etc/cron.d && filter
    """
    basenames = map(os.path.basename, os.listdir(CRON_DIR))
    return filter(lambda x: x.startswith("scalegrease"), basenames)


def parse_cron_file(basename):
    """
    'just_basename.cron' ==> { artifact_id: "blah", etc. }
    """
    pattern = "scalegrease__(?P<group>.*)__(?P<artifact>.*)__(?P<origpath>.*)_cron"
    match = re.match(pattern, basename)
    raw_content = system.read_file(CRON_DIR + basename)
    okf = lambda x: not x.startswith("#")
    uncommented_content = '\n'.join(filter(okf, raw_content.split('\n')))
    return {
        "group": match.group("group"),
        "artifact": match.group("artifact"),
        "origpath": match.group("origpath"),
        "raw_content": raw_content,
        "uncommented_content": uncommented_content.strip(),
    }


def is_not_empty(parsed_file):
    return parsed_file['uncommented_content'] != ''


def pretty_print(parsed_file):
    """
    We just print so it looks decent in a terminal
    """
    indented_uc = '    ' + parsed_file['uncommented_content'].replace('\n', '\n    ')
    return '{origpath} ({artifact}):\n{indented_uc}'.format(
        origpath=parsed_file['origpath'],
        artifact=parsed_file['artifact'],
        indented_uc=indented_uc,
    ).strip()


def main(argv):
    parsed_files = map(parse_cron_file, get_cron_files())
    parsed_files = filter(is_not_empty, parsed_files)
    print('\n\n'.join(map(pretty_print, parsed_files)))

if __name__ == '__main__':
    sys.exit(main(sys.argv))
