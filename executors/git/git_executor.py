import re
import subprocess

from task_executer.lib.config_helper import ConfigHelper
from task_executer.lib.executor import Executor
from task_executer.lib.task import Task


class GitExecutor(Executor):
    def __init__(self):
        super().__init__("git", required_config={"path": str})

    async def execute(self, task: Task, optional_parameters: dict):
        task_config = ConfigHelper(task.name, task.parameters)

        branch_override = "master"
        use_branch_from_parameters = "branch_override" in task.parameters

        if use_branch_from_parameters:
            if "branch" not in optional_parameters:
                self.logger.warning(
                    f"Git option 'branch_override' was set but no 'branch' was given from optional parameters, {optional_parameters}")
                use_branch_from_parameters = False
            else:
                branch_override = optional_parameters["branch"]

                pattern = re.compile("^([a-zA-Z0-9\\-._+])+$")
                use_branch_from_parameters = pattern.match(branch_override)

                if not use_branch_from_parameters:
                    self.logger.warning(f"The provided optional branch override is not allowed, only 'a-zA-Z0-9-._+', please remove invalid characters")

        cwd = task_config.get_string("path", "")

        if use_branch_from_parameters:
            command = f"git switch {branch_override}"
            output = subprocess.check_output(command, shell=True, cwd=cwd)
            self.logger.debug(f"Command output: {output}")

        command = f"git pull"
        output = subprocess.check_output(command, shell=True, cwd=cwd)
        self.logger.debug(f"Command output: {output}")
