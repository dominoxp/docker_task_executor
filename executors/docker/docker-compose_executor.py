import os
import subprocess

from task_executer.lib.config_helper import ConfigHelper
from task_executer.lib.executor import Executor
from task_executer.lib.task import Task


class DockerComposeExecutor(Executor):
    def __init__(self):
        super().__init__("docker-compose", required_config={"action": str, "file": str})

    async def execute(self, task: Task, optional_parameters: dict):
        task_config = ConfigHelper(task.name, task.parameters)

        action = task_config.get_string("action", "update")
        docker_compose_file = task.parameters["file"]

        if not os.path.exists(docker_compose_file):
            self.logger.error(f"Could not execute docker-compose task, because docker-compose file or folder '{docker_compose_file}' could not be found")
            return

        if os.path.isfile(docker_compose_file):
            docker_compose_folder = os.path.dirname(docker_compose_file)
        else:
            docker_compose_folder = docker_compose_file

        if action == "update":
            pull = task_config.get_bool("pull", True)
            force_recreate = task_config.get_bool("force_recreate", True)
            build = task_config.get_bool("build", True)

            if pull:
                cmd = "docker compose pull"
                output = subprocess.check_output(cmd, shell=True, cwd=docker_compose_folder)
                self.logger.debug(f"Command output: {output}")

            cmd = "docker compose up --quiet-pull --no-color -d"

            if force_recreate:
                cmd += " --force-recreate"

            if build:
                cmd += " --build"

            self.logger.debug(f"Running docker-compose command {cmd}")
            output = subprocess.check_output(cmd, shell=True, cwd=docker_compose_folder)
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
