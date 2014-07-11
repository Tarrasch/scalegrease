import logging
import subprocess
import os
import errno


def run_with_logging(cmd, env=None):
    """
    Run cmd and wait for it to finish. While cmd is running, we read it's
    output and print it to a logger.
    """
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=env)
    logging.info("Executing: %s", " ".join(cmd))
    short_cmd0 = os.path.basename(cmd[0])
    logger = logging.getLogger('subp.{0}'.format(short_cmd0))
    output_lines = []
    while True:
        line = process.stdout.readline()
        if not line:
            break
        output_lines += [line]
        logger.info(line.rstrip('\n'))

    exit_code = process.poll()
    output = ''.join(output_lines)
    if exit_code:
        raise subprocess.CalledProcessError(exit_code, cmd)
    return output


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


def mkdir_p(path):
    # Copy pasted from http://stackoverflow.com/a/600612/621449
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
