import logging
import subprocess
import os
import errno


class CalledProcessError(subprocess.CalledProcessError):
    """
    Python 2.6 subprocess.CalledProcessError has no "output" property.
    """
    def __init__(self, returncode, cmd, output=None):
        super(CalledProcessError, self).__init__(returncode, cmd)
        self.output = output

    def __str__(self):
        return (super(CalledProcessError, self).__str__() +
                ('\nOutput:\n"""\n%s"""' % self.output))


def check_output(cmd, env=None):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=env)
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
        line = process.stdout.readline()
        if not line:
            break
        output_lines += [line]
        logger.info(line.rstrip('\n'))

    exit_code = process.poll()
    if exit_code:
        output = ''.join(output_lines)
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


def mkdir_p(path):
    # Copy pasted from http://stackoverflow.com/a/600612/621449
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
