from scalegrease import runner
from scalegrease import system


class ShellRunner(runner.RunnerBase):
    """
    A runner for running custom commands. Use this when you want to run a
    custom command, but still want greaserun's fat-jar downloading and logging
    mechanism.

    Examples:

        $ greaserun < .. args .. > [--] echo a {jar_path} b {artifact_spec} c
        $ greaserun < .. args .. > [--] java -jar {jar_path} --my custom --args

    Where {jar_path} and {artifact_spec} will be substituted by this runner.
    """

    def run_job(self, artifact_storage, argv):
        substitute = lambda arg: arg.format(
            jar_path=artifact_storage.jar_path(),
            artifact_spec=artifact_storage.spec(),
        )
        cmd_line = map(substitute, argv)
        system.run_with_logging(cmd_line)
