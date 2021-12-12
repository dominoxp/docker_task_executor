#!/usr/bin/python3
# -*- encoding: utf-8 -*-
import asyncio
import logging
import logging.handlers
import os
import sys
from asyncio import AbstractEventLoop

from task_executer.lib.task_handler import TaskHandler


def main():
    logger = logging.getLogger()
    logger.setLevel(os.getenv("LOGGING", "DEBUG").upper())

    console = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]: %(message)s', datefmt='%d.%m %I:%M:%S')
    console.setFormatter(formatter)

    logger.addHandler(console)

    loop = asyncio.get_event_loop()  # type: AbstractEventLoop

    task_handler = TaskHandler(loop)
    try:
        logger.info("Starting TaskExecutor v0.2 by dominoxp")
        loop.create_task(task_handler.main())
        loop.run_forever()

    except KeyboardInterrupt:
        logger.info(f"Shutting down TaskExecutor...")
    except Exception:
        logger.error(f"Shutting down TaskExecutor...", exc_info=True)
    finally:
        task_handler.stop()
        loop.close()
        logger.info("Shutdown completed, good by!")
