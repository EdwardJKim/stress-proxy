trying to exhaust FDs with websockets + configurable-http-proxy + docker

this currently seems to run just fine with thousands of connections, so I'm not doing something right, yet.

## Host

Build containers:

    invoke build_server

Start proxy listening:

    invoke server

To stop the server and clean up, run:

    invoke cleanup_server

## Client

Build containers:

    invoke build_client

Run fd exhaustion test:

    invoke client <hostname> <n> --proxy=<ip>

where `<hostname>` is an SSH-friendly hostname (i.e., it can be an
alias), `<n>` is the number of workers to start, and `<ip>` is the IP
address of the proxy (probably the IP address of `<hostname>`).
