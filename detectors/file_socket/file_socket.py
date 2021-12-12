import asyncio
import json
import os
from asyncio import StreamWriter, StreamReader
from platform import system

from task_executer.lib.detector import Detector


class FileSocketDetector(Detector):

    def __init__(self):
        super().__init__("file_socket")

        self.disabled = False

        if system() == "Windows":
            self.logger.warning("The File Socket Detector is not working under Windows, disabling FileSocketDetector")
            self.disabled = True

    def init(self):
        self.socket_path = self.config.get_string("socket_path", "task_executor_socket.sock")

        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except OSError:
                self.logger.warning(f"Could not delete old socket file '{self.socket_path}', "
                                    f"FileSocketDetector might not work correctly", exc_info=True)

    async def start(self) -> bool:
        if self.disabled:
            return False

        self.running = True

        await asyncio.start_unix_server(client_connected_cb=self.handler,
                                        path=self.socket_path)  # type: (StreamReader, StreamWriter)

        os.chmod(self.socket_path, 0o622)
        return True

    async def handler(self, reader, _):
        self.logger.debug("Socket connection opened")

        while self.running:
            raw_line = await reader.readline()  # type: bytes

            if not raw_line:
                break

            line = raw_line.decode(encoding="UTF-8")
            self.on_package_received(line)

        self.logger.debug("Socket connection closed")

    def on_package_received(self, raw_data: str):
        try:
            data = json.loads(raw_data)
        except ValueError:
            self.logger.warning(f"Received Data ({len(raw_data)}) from file could not be decoded '{raw_data}'")
            return

        all_parameter_present = True
        for i in ("task", "task_token"):
            if i not in data:
                all_parameter_present = False

        parameters = {}

        if "parameters" in data:
            parameters = data["parameters"]

        if all_parameter_present:
            self.detector_callback.on_task_detected(
                task_name=data["task"],
                task_token=data["task_token"],
                optional_parameters=parameters
            )
        else:
            self.logger.warning(f"Cannot start task from file socket because parameters were missing, provided data: {data}")

    async def stop(self):
        self.running = False
