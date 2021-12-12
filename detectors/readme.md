# Detectors

### File Socket Detector

This detector is a basic File Socket Server listening on a file socket. Task information are retrieved by send json data
through file e.g.: `echo '{"task": "abc", "token": "1234"}' > /file.sock`. This Detector will not work on Windows
systems as file sockets are not present.

No Response will be sent back, because this is a one way file socket.

#### Available Config:

- socket_path [str] = task_executor_socket.sock
    - The Path of the File Socket

### HTTP Rest Detector

This detector is a basic Webserver listening on local http port. Task information are retrieved by the GET query fields
or POST json data. Parameter names are task and token e.g.:
`GET localhost:8080/?task=abc&token=1234` or `POST localhost:8080 {"task": "abc", "token": "1234"}`.

Will return following status codes:

- 200 If task was successfully triggered
- 400 If Post Data is incorrect or json invalid
- 403 If task was not triggered
- 500 If task parameter were incorrect or an error occurred

#### Available Config:

- port [int] = 8080
    - TCP Port of the Webserver to listen on
- host [str] = "0.0.0.0"
    - IP Address to listen on (from all sources)
- path [str] = "/"
    - The Http Path to listen on, if changed tasks can only be triggered on host:port{host_path} e.g.: localhost:
      8080/?task=a&token=1 localhost:8080/test?task=b&token=2
