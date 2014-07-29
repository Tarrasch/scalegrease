from scalegrease import runner
from scalegrease import system


class ShellRunner(runner.RunnerBase):
    def run_job(self, artifact_storage, argv):
        cmd_line = argv + [artifact_storage.jar_path(), artifact_storage.spec()]
        system.run_with_logging(cmd_line)
