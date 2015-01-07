trying to exhaust FDs with websockets + configurable-http-proxy + docker

this currently seems to run just fine with thousands of connections, so I'm not doing something right, yet.

Build containers:

    invoke build

Run fd exhaustion test:

    invoke fds
