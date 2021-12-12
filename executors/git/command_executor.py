import os
import platform
import re
import subprocess

from task_executer.lib.executor import Executor
from task_executer.lib.task import Task


class CommandExecutor(Executor):
    def __init__(self):
        super().__init__("command", required_config={"cmd": str})

    async def execute(self, task: Task, optional_parameters: dict):

        cwd = task.parameters.get("cwd", os.getcwd())

        command = task.parameters["cmd"]
        replacement_vars = re.findall("%.*?%", command)
        for replacement_var in replacement_vars:
            key = replacement_var[1:-1]

            if key == "":
                continue

            if key in optional_parameters:
                command = command.replace(replacement_var, str(optional_parameters[key]))
            else:
                self.logger.warning(
                    f"Command Executor detected replacement variable {replacement_var} but no key {key} was found in optional parameters: {optional_parameters}")

        self.logger.debug(f"Executing command '{command}'")

        if platform.system() == "Windows":
            output = subprocess.check_output(command, shell=True, cwd=cwd)
        else:
            uid = task.parameters.get("uid", os.getuid())
            gid = task.parameters.get("gid", os.getgid())

            output = subprocess.check_output(command, shell=True, preexec_fn=self.demote(uid=uid, gid=gid), cwd=cwd)
        self.logger.debug(f"Command output: {output}")

    @staticmethod
    def demote(uid: int, gid: int):
        # Source: https://gist.github.com/sweenzor/1685717
        """Pass the function 'set_ids' to preexec_fn, rather than just calling
        	setuid and setgid. This will change the ids for that subprocess only"""

        def set_ids():
            os.setgid(uid)
            os.setuid(gid)

        return set_ids
