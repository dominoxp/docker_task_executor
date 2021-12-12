FROM python:3.9

ENV TASK_HANDLER_EXECUTORS_CONFIG="/config/executors" \
    TASK_HANDLER_DETECTORS_CONFIG="/config/detectors" \
    TASK_HANDLER_TASKS_CONFIG="/config/tasks" \
    DETECTOR_HTTP_REST=true \
    DETECTOR_FILE_SOCKET=false \
    OBSERVE_TASK_CHANGE=true \
    LOGGING=INFO

COPY requirements.txt /app/requirements.txt
RUN useradd -ms /bin/bash docker
USER docker

COPY . /app
RUN pip install -r /app/requirements.txt --no-warn-script-location

PORT
VOLUME /config
WORKDIR /app

ENTRYPOINT python3 /app/start.py