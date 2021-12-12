import logging
from typing import Optional

from .config_helper import ConfigHelper
from .detector_callback import DetectorCallback


class Detector:
    def __init__(self, name: str):
        self.name: str = name
        self.logger: logging = logging.getLogger(f"detector_{self.name}")
        self.detector_callback: Optional[DetectorCallback] = None
        self.config: Optional[ConfigHelper] = None

    # Function will be called once to initialise all Detectors (eg. read config values)
    def init_detector(self, detector_callback: DetectorCallback, config_helper: ConfigHelper):
        self.detector_callback = detector_callback
        self.config = config_helper
        self.init()

    # Function will be called once to initialise all Detectors (eg. read config values)
    def init(self):
        pass

    # Function will be called once to start the detector (eg. start webserver)
    async def start(self) -> bool:
        self.logger.warning(
            f"The detector {self.name} did not override the Detector.start() callback, the detector might not work correctly")
        return False

    async def stop(self):
        """Function will be called once to stop the detector (on script shutdown)"""
