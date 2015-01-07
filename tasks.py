from invoke import task, run

@task
def server(n=1):
    print("starting proxy container")
    run('docker run --name proxy -p 8000:8000 -dt jupyter/configurable-http-proxy --api-ip=0.0.0.0')

    for i in range(n):
        print("starting worker container %i" % i)
        run('docker run --link proxy:proxy --name worker%i -dt stress-worker --id=%i' % (i, i))

@task
def client(n=1, proxy='localhost'):
    try:
        print('starting client')
        run('docker run --name fds -it stress-fds --proxy=%s --n=%i' % (proxy, n))
    finally:
        cleanup_client()

@task
def cleanup_server(n=1):
    workers = ['worker%s' % i for i in range(n)]
    run('docker rm -f proxy %s' % " ".join(workers))

@task
def cleanup_client():
    run('docker rm -f fds')

@task
def build_server():
    run('docker build -t stress-worker worker')

@task
def build_client():
    run('docker build -t stress-fds fds')
