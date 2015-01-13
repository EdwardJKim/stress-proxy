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

The first time you run the server processes, you'll need to run:

```
invoke setup_server
```

After that, you shouldn't need to run that again. Next, build the
necessary JupyterHub image:

```
invoke build_jupyterhub
```

Now, run the restuser service:

```
invoke restuser
```

Finally, run JupyterHub:

```
invoke jupyterhub
```

To clean up the JupyterHub docker images and any users that were
created, run:

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
invoke stress_hub <url> --port=<port> -N=<num_users>
```

where `<url>` is the url of the host where JupyterHub is running and
`<port>` is the port number that JupyterHub is running on. The
`<num_users>` argument is for the number of users to test
simultaneously (maximum 100). You can also pass a `--hubid` argument
if you want to run multiple stress processes at once.

