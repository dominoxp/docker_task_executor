import logging
from typing import Optional

from task_executer.lib.config_helper import ConfigHelper
from task_executer.lib.task import Task


class Executor:
    def __init__(self, name: str, required_config: Optional[dict] = None):
        if required_config is None:
            required_config = {}

        self.required_config = required_config  # type: dict
        self.name = name
        self.logger = logging.getLogger(f"executor_{name}")
        self.config: Optional[ConfigHelper] = None

    def init_executor(self, config_helper: ConfigHelper):
        self.config = config_helper  # type: ConfigHelper

    def init(self):
        pass

    async def execute_executor(self, task: Task, optional_parameters: dict):
        for key, typ in self.required_config.items():
            if key not in task.parameters:
                self.logger.error(
                    f"Executor {self.name} cannot proceed because required config option {key} is missing")
                raise ValueError(f"Executor {self.name} cannot proceed because required config option {key} is missing")

            if not isinstance(task.parameters[key], typ):
                self.logger.error(
                    f"Executor {self.name} cannot proceed because required config option type mismatches, expected {typ}, got {str(type(task.parameters[key]))} instead")
                raise ValueError(f"Executor {self.name} cannot proceed because config option typ mismatch")

        await self.execute(task, optional_parameters)

    async def execute(self, task: Task, optional_parameters: dict):
        pass
