import os
import platform
import subprocess

from task_executer.lib.config_helper import ConfigHelper
from task_executer.lib.executor import Executor
from task_executer.lib.task import Task


class DockerExecutor(Executor):
    def __init__(self):
        super().__init__("docker", required_config={"action": str})

    async def execute(self, task: Task, optional_parameters: dict):
        task_config = ConfigHelper(task.name, task.parameters)

        command = "docker"

        action = task_config.get_string("action", "custom")
        socket = task_config.get_string("socket", "")
        cwd = task_config.get_string("cwd", ".")

        if socket != "":
            command += f"-H {socket}"

        if action == "login":
            command += f" login -u \"{task_config.get_string('username')}\" -p \"{task_config.get_string('password')}\" \"{task_config.get_string('socket')}\""

        elif action == "custom":
            command += f" {task_config.get_string('cmd', '-v')}"

        else:
            self.logger.warn(f"Cannot recognise Action '{action}'")
            return

        self.logger.debug(f"Executing docker command '{command}'")

        if platform.system() == "Windows":
            output = subprocess.check_output(command, shell=True, cwd=cwd)
        else:
            uid = task_config.get_int("uid", os.getuid())
            gid = task_config.get_int("gid", os.getgid())

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
