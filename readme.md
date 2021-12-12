# Docker Task Executor

by dominoxp

## Intro

This Project contains a python script which is intended to run inside a docker container and execute tasks based on
events. The events are registered by detectors, at this point, there are HTTP and a File Socket detectors. Whenever an
authorized request was recognized, the internal task will be executed. In order to execute the task, different task
executors are available. The tasks will be executed and can trigger following tasks.

### Detector

The detector receives an authorized request (needs `task_name` and `token` of the given task). All default available
detectors are listed [here](detectors/readme.md).

### Task Executors and Tasks

The task executors contains the logic to execute the individual task. All default available executors are
listed [here](executors/readme.md).

## Getting Started

