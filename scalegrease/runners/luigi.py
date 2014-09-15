from scalegrease.runners.python import PythonRunner


class LuigiRunner(PythonRunner):
    def run_job(self, artifact_storage, argv):
        runner_cmd = self._config["command"]
        super(LuigiRunner, self).run_job(artifact_storage, [runner_cmd] + argv)
