import glob
import inspect
import json
import logging
import os
import time
import uuid
from asyncio import AbstractEventLoop

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from task_executer.lib.config_helper import ConfigHelper
from task_executer.lib.detector import Detector
from task_executer.lib.detector_callback import DetectorCallback
from task_executer.lib.executor import Executor
from task_executer.lib.task import Task


class TaskHandler(DetectorCallback, FileSystemEventHandler):
    EXECUTORS_CONFIG_PATH = os.getenv("TASK_HANDLER_EXECUTORS_CONFIG", "config/executors")
    DETECTORS_CONFIG_PATH = os.getenv("TASK_HANDLER_DETECTORS_CONFIG", "config/detectors")
    TASKS_CONFIG_PATH = os.getenv("TASK_HANDLER_TASKS_CONFIG", "config/tasks")

    def __init__(self, loop: AbstractEventLoop):
        self.logger = logging.getLogger("TaskHandler")
        self.executors = {}
        self.detectors = {}
        self.tasks = {}
        self.running = True
        self.loop = loop

        for path in (
                TaskHandler.EXECUTORS_CONFIG_PATH, TaskHandler.DETECTORS_CONFIG_PATH, TaskHandler.TASKS_CONFIG_PATH):
            if not os.path.exists(path):
                os.mkdir(path)

    def __load_module(self, path: str, module_class) -> list:
        self.logger.debug("=" * 10 + f" Scanning for {module_class.__name__}... " + "=" * 10)
        modules = []

        if not os.path.exists(path):
            os.mkdir(path)

        # Import Bot Extensions
        for module_path in glob.glob(f"{path}/**/*.py"):
            full_module_name = module_path.replace("/", ".").replace("\\", ".").rsplit(".py")[0]
            module_name = full_module_name.split(".")[-1]

            if module_name in ("__init__", "__pycache__") or module_name.startswith("_") or module_path.endswith(
                    "__pycache__"):
                continue

            try:
                module = __import__(full_module_name)
            except Exception as ee:
                self.logger.warning(
                    f"Could not import Module {full_module_name} ({module_name}) from {module_path}, because of {ee}, continue without module",
                    exc_info=True)
                continue

            modules += self._search_module(full_module_name, module_class, module.__dict__)

        return modules

    def _search_module(self, full_module_name, module_class, module_dict: dict) -> list:
        modules = []

        for key, value in module_dict.items():
            if key == "__name__" and not full_module_name.startswith(value):
                break

            if inspect.ismodule(value):
                modules += self._search_module(full_module_name, module_class, value.__dict__)

            if inspect.isclass(value) and issubclass(value,
                                                     module_class) and value.__name__ != module_class.__name__:
                modules.append(value)
                self.logger.debug(f"Found {module_class.__name__} {value.__name__}")

        return modules

    def _load_executors(self):
        executors = self.__load_module("executors", Executor)

        for item in executors:  # type: Executor.__class__
            executor = item()  # type: Executor

            config_helper = ConfigHelper(executor.name)

            # Check if a config file exists for detector
            config_file: str = os.path.join(TaskHandler.EXECUTORS_CONFIG_PATH, executor.name + ".json")

            if os.path.exists(config_file):
                config_helper.load(config_file)

            try:
                executor.init_executor(config_helper=config_helper)
            except Exception:
                self.logger.error("Executor has thrown error on initialisation", exc_info=True)
            self.executors[executor.name] = executor

    def _load_detectors(self):
        detectors = self.__load_module("detectors", Detector)
        for item in detectors:  # type: Detector.__class__
            detector = item()  # type: Detector

            if (os.getenv("DETECTOR_" + detector.name.upper(), "true")).lower() != "true":
                self.logger.debug(
                    f"Detector {detector.name} was disabled (Set Env DETECTOR_{detector.name.upper()} to 'true' to enable)")
                continue

            config_helper = ConfigHelper(detector.name)

            # Check if a config file exists for detector
            config_file: str = os.path.join(TaskHandler.DETECTORS_CONFIG_PATH, detector.name + ".json")

            if os.path.exists(config_file):
                config_helper.load(config_file)

            detector.init_detector(detector_callback=self, config_helper=config_helper)
            self.detectors[detector.name] = detector

    def _load_tasks(self):
        self.tasks = {}
        self.logger.debug("=" * 10 + f" Scanning for Tasks... " + "=" * 10)
        if not os.path.exists(TaskHandler.TASKS_CONFIG_PATH):
            os.mkdir(TaskHandler.TASKS_CONFIG_PATH)

        for file in os.listdir(TaskHandler.TASKS_CONFIG_PATH):
            path = os.path.join(TaskHandler.TASKS_CONFIG_PATH, file)

            if file.startswith("."):
                continue

            try:
                self._load_task_content(path)
            except Exception as e:
                self.logger.warning(f"Could not load Task @ '{path}' because of {e}", exc_info=True)

    def _load_task_content(self, path):
        if os.path.isfile(path):
            with open(path, "r") as File:
                data = json.load(File)

                if "name" not in data or "typ" not in data:
                    self.logger.warning(f"Could not import task @ '{path} because parameter name or type was missing")
                    return

                if "token" not in data or data["token"] == "":
                    # Generate a new token and save to file
                    with open(path, "w") as File:
                        data["token"] = uuid.uuid4().hex
                        json.dump(data, File, indent=4, sort_keys=True)

                if not data["typ"] in self.executors:
                    self.logger.warning(
                        f"Could not import task @ '{path}' because the executor '{data['typ']}' is unknown, currently registered: [{','.join(self.executors.keys())}]")
                    return

                parameters = {}
                if "parameter" in data:
                    parameters = data["parameter"]
                elif "parameters" in data:
                    parameters = data["parameters"]

                # Check for necessary information
                task = Task(name=data["name"], task_typ=data["typ"], token=data["token"], parameters=parameters,
                            following_task=data.get("following_task", data.get("following")))
                self.tasks[data["name"]] = task
                self.logger.info(f"Task {data['name']} ({data['typ']}) was loaded")

    def on_task_detected(self, task_name: str, task_token: str, optional_parameters: dict):
        if task_name not in self.tasks:
            self.logger.warning(f"The Task {task_name} does not exist or was not loaded, ignoring")
            return False

        task = self.tasks[task_name]

        if task.token != task_token:
            self.logger.warning(f"The Task Token for Task {task_name} does not match '{task_token}', ignoring")
            return False

        executor = self.executors[task.task_typ]  # type: Executor

        self.logger.info(f"The Task {task_name} was triggered")
        self.loop.create_task(self._execute_task(executor, task, optional_parameters))
        return True

    async def _execute_task(self, executor, task, optional_parameters):
        # Execute Task
        await executor.execute_executor(task, optional_parameters=optional_parameters)

        # Check if following task exist and execute if so
        if task.following_task is not None and task.following_task in self.tasks:
            following_task = self.tasks[task.following_task]
            following_executor = self.executors[following_task.task_typ]  # type: Executor

            self.logger.info(f"The Task {task.following_task} was triggered by task {task.name}")
            await self._execute_task(following_executor, following_task, optional_parameters)

    def on_any_event(self, event):
        self.logger.debug(f"File System Change in Task Executor Detected, reloading Tasks... {event}")
        self._load_tasks()

    async def main(self):
        start = time.time()
        self._load_executors()
        self._load_tasks()
        self._load_detectors()

        for detector_name, detector in self.detectors.items():
            try:
                self.logger.debug(f"Event Detector {detector_name} is starting")
                await detector.start()
                self.logger.info(f"Event Detector {detector_name} was enabled")
            except Exception:
                self.logger.error(f"An error occurred while starting Detector {detector_name}!", exc_info=True)

        if os.getenv("OBSERVE_TASK_CHANGE", "true").lower() == "true":
            self.logger.info("Starting Task change observer")
            observer = Observer()
            observer.schedule(event_handler=self, path=TaskHandler.TASKS_CONFIG_PATH, recursive=True)
            observer.start()
        self.logger.info(f"Main started after {time.time() - start} sek")

    def stop(self):
        self.running = False
