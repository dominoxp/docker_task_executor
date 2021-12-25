FROM python:3.9

ENV TASK_HANDLER_EXECUTORS_CONFIG="/config/executors" \
    TASK_HANDLER_DETECTORS_CONFIG="/config/detectors" \
    TASK_HANDLER_TASKS_CONFIG="/config/tasks" \
    DETECTOR_HTTP_REST=true \
    DETECTOR_FILE_SOCKET=false \
    OBSERVE_TASK_CHANGE=true \
    LOGGING=INFO

COPY requirements.txt /app/requirements.txt
RUN apt-get update && apt-get install ca-certificates curl gnupg lsb-release -y && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null && \
    apt-get update && apt-get install docker-ce-cli -y
RUN useradd -ms /bin/bash docker
USER docker

COPY . /app
RUN pip install -r /app/requirements.txt --no-warn-script-location

EXPOSE 8080
VOLUME /config
WORKDIR /app

ENTRYPOINT python3 /app/start.py