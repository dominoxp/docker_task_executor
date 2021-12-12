# Default Task Executor

### Table of Content

- [docker-compose](#docker-compose)
- [docker](#docker)
- [command](#command)
- [git](#git)

#### Global Parameters

- follow_task: str = None
  - The following task to execute after this task

### docker-compose

Executes docker-compose commands.

**Parameters:**

- **file: str**
  - the location of the docker-compose.yml file
- **action: str = [update]**
  - [update] Update existing Docker Project
    - pull: bool = true
      - Should the newest container be pulled from upstream
    - force_recreate: bool = false
      - Should the container be recreated even when dependencies are not met?
    - build: bool = true
      - Should local container be build with local Dockerfiles?

### docker

Executes docker commands.

- socket: str = "/var/run/docker.sock"
  - which docker socket should be used
- cwd: str = "."
  - current working directory
- uid: int = Current UID
  - set the user id to execute command as
- gid: int = Current GID
  - set the group id to execute command as
- **action: str [login, custom]**
  - [login] Login to docker registry
    - username: str
      - Docker Registry Username
    - password: str
      - Docker Registry Password
    - server: str
      - The Address of the docker Registry

### command

Executes shell command.

- **cmd: str**
  - The command to be executed, placeholder can be defined with %< name >% and define by provided arguments
- cwd: str = "."
  - current working directory
- uid: int = Current UID
  - set the user id to execute command as
- gid: int = Current GID
  - set the group id to execute command as
