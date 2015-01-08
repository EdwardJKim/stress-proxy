Stress testing of the configurable-http-proxy and of JupyterHub.

# Proxy

## Host

Build the container:

```
invoke build_worker
```

You'll also need to have the `jupyter/configurable-http-proxy` image
downloaded.

Start proxy listening:

```
invoke proxy
```

To stop the server and clean up, run:

```
invoke cleanup_proxy
```

## Client

Build containers:

```
invoke build_fds
```

Run fd exhaustion test:

```
invoke stress_fds <hostname> <n> --proxy=<ip>
```

where `<hostname>` is an SSH-friendly hostname (i.e., it can be an
alias), `<n>` is the number of workers to start, and `<ip>` is the IP
address of the proxy (probably the IP address of `<hostname>`).

# JupyterHub

## Host

You'll need to install whatever version of JupyterHub you want. Then:

```
invoke jupyterhub <image>
```

where `<image>` is the name of the JupyterHub image you want to run
(for example, `jupyter/jupyterhub`).

To clean up the JupyterHub docker images, run:

```
invoke cleanup_jupyterhub
```

## Client

Build containers:

```
invoke build_hub
```

Run stress test:

```
invoke stress_hub <url> <port> <user>
```

where `<url>` is the url of the host where JupyterHub is running and
`<port>` is the port number that JupyterHub is running on.
