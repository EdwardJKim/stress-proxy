from invoke import task, run
import time
import subprocess

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
def build_jupyterhub():
    run('docker build -t jupyterhub jupyterhub')
    run('docker pull jhamrick/systemuser')

@task
def restuser():
    run('curl -s https://raw.githubusercontent.com/minrk/restuser/master/restuser.py > restuser.py')
    subprocess.call(['python', 'restuser.py', '--socket=/var/run/restuser.sock', '--skeldir=skeldir'])

@task
def jupyterhub():
    run('docker run --name jupyterhub -p 8000:8000 -d --net=host -v /var/run/docker.sock:/docker.sock -v /var/run/restuser.sock:/restuser.sock jupyterhub')

@task
def cleanup_jupyterhub():
    run('docker rm -f jupyterhub || true')
    with open('jupyterhub/userlist', 'r') as fh:
        users = fh.read().strip().split("\n")
    for user in users:
        run('docker rm -f jupyter-{} || true'.format(user))
        run('deluser --remove-home {} || true'.format(user))

# Client

@task
def build_hub():
    run('docker build -t stress-hub hub')

@task
def stress_hub(url, port=8000, N=1):
    try:
        print('starting stress client')
        run('docker run --name hub --net=host -it stress-hub --url=%s --port=%s --N=%s' % (url, port, N))
    finally:
        cleanup_hub()

@task
def cleanup_hub():
    run('docker rm -f hub')
