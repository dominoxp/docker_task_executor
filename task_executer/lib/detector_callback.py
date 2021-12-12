

class DetectorCallback:

    # Function will be called when a task was detected, giving the unique task_name and token to verify
    # if the task is correct and to trigger the task
    def on_task_detected(self, task_name: str, task_token: str, optional_parameters: dict) -> bool:
        pass
