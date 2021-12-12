import json
import logging
import os
from typing import Optional


class ConfigHelper:
    def __init__(self, name: str, data: Optional[dict] = None):
        if data is None:
            data = {}
        self.data = data
        self.name = name
        self.logger = logging.getLogger("ConfigHelper")

    def load(self, file_name: str) -> bool:
        if not (os.path.exists(file_name)) or not (os.path.isfile(file_name)):
            self.logger.warning(f"Could not load json file '{file_name}', because it did not exists or is not a file")
            return False

        try:
            with open(file_name, "r") as File:
                self.data = json.load(fp=File)
            return True

        except Exception as e:
            self.logger.warning(f"Could not load json file '{file_name}', because there was an error: {e}",
                                exc_info=True)
            return False

    def populate_minimum(self, file_name: str):
        data = {}
        with open(file_name, "w") as File:
            json.dump(data, File, indent=4, sort_keys=True)
        self.data = data

    def get_string(self, key: str, default: str = "") -> str:
        env_key = self.name + "_" + key
        return os.getenv(env_key.upper()) or self.data.get(key) or default

    def get_int(self, key: str, default: int = 0) -> int:
        return int(self.get_string(key, str(default)))

    def get_bool(self, key: str, default: bool = False) -> bool:
        return bool(self.get_string(key, str(default)))

    def key_exists(self, key: str) -> bool:
        return key in self.data

    def value_type(self, key: str) -> type:
        return type(self.data[key])

    def get_dict(self, key: str, default: Optional[dict] = None) -> Optional[dict]:
        if key in self.data:
            return self.data[key]
        else:
            return default
