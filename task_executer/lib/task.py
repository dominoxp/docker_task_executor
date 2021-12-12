from typing import Optional


class Task:
    def __init__(self, name: str, task_typ: str, token: str, parameters: dict, following_task: Optional[str]):
        self.name = name
        self.task_typ = task_typ
        self.token = token
        self.parameters = parameters
        self.following_task = following_task
