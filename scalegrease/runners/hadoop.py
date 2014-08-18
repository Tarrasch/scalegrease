import os
from scalegrease import runner
from scalegrease import system

class HadoopRunner(runner.RunnerBase):
    def run_job(self, artifact_storage, argv):
        hadoop_cmd = (self._config["command"] + [artifact_storage.jar_path()] + argv)
        env = dict(os.environ.items() + {"HADOOP_CLASSPATH": artifact_storage.jar_path()}.items())
        system.run_with_logging(hadoop_cmd, env=env)
