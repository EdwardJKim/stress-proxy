from invoke import task, run
import time

@task
def server():
    print("starting proxy container")
    run('docker run --name proxy -p 8000:8000 -dt jupyter/configurable-http-proxy --api-ip=0.0.0.0')

@task
def client(host, n, proxy='localhost'):
    n = int(n)

    print('starting worker containers')
    for i in range(n):
        print("starting worker container %i" % i)
        run('ssh %s docker run --link proxy:proxy --name worker%i -dt stress-worker --id=%i' % (host, i, i))

    time.sleep(1)
    try:
        print('starting client')
        run('docker run --name fds -it stress-fds --proxy=%s --n=%i' % (proxy, n))
    finally:
        cleanup_client(host, n)

@task
def cleanup_server(n=1):
    run('docker rm -f proxy')
    workers = ['worker%s' % i for i in range(n)]
    run('docker rm -f %s' % " ".join(workers))

@task
def cleanup_client(host, n):
    run('docker rm -f fds')
    workers = ['worker%s' % i for i in range(n)]
    run('ssh %s docker rm -f %s' % (host, " ".join(workers)))

@task
def build_server():
    run('docker build -t stress-worker worker')

@task
def build_client():
    run('docker build -t stress-fds fds')
