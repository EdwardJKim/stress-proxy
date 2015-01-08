from invoke import task, run
import time

## Proxy stress testing

# Host

@task
def build_worker():
    run('docker build -t stress-worker worker')

@task
def proxy():
    print("starting proxy container")
    run('docker run --name proxy -p 8000:8000 -dt jupyter/configurable-http-proxy --api-ip=0.0.0.0')

@task
def cleanup_proxy(n=1):
    run('docker rm -f proxy')
    workers = ['worker%s' % i for i in range(n)]
    run('docker rm -f %s' % " ".join(workers))


# Client

@task
def build_fds():
    run('docker build -t stress-fds fds')

@task
def stress_fds(host, n, proxy='localhost'):
    n = int(n)

    print('starting worker containers')
    for i in range(n):
        print("starting worker container %i" % i)
        run('ssh %s docker run --link proxy:proxy --name worker%i -dt stress-worker --id=%i' % (host, i, i))

    time.sleep(1)
    try:
        print('starting stress client')
        run('docker run --name fds -it stress-fds --proxy=%s --n=%i' % (proxy, n))
    finally:
        cleanup_fds(host, n)

@task
def cleanup_fds(host, n):
    run('docker rm -f fds')
    workers = ['worker%s' % i for i in range(n)]
    run('ssh %s docker rm -f %s' % (host, " ".join(workers)))


## JupyterHub stress testing

# Server

@task
def jupyterhub(image):
    run('docker run --name jupyterhub -p 8000:8000 -d --net=host -v /var/run/docker.sock:/docker.sock %s' % image)

@task
def cleanup_jupyterhub():
    run('docker rm -f jupyterhub')

# Client

@task
def build_hub():
    run('docker build -t stress-hub hub')

@task
def stress_hub(url, port=8000, user='user1'):
    try:
        print('starting stress client')
        run('docker run --name hub --net=host -it stress-hub --url=%s --port=%s --user=%s' % (url, port, user))
    finally:
        cleanup_hub()

@task
def cleanup_hub():
    run('docker rm -f hub')
