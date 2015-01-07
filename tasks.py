from invoke import task, run

@task
def server():
    print("starting echo container")
    run('docker run --name echo --net=host -dt stress-echo')

    print("starting proxy container")
    run('docker run --name proxy -dt --net=host jupyter/configurable-http-proxy --api-ip=0.0.0.0 --default-target=http://127.0.0.1:9000')

@task
def client(proxy='localhost'):
    try:
        print('starting client')
        run('docker run --name fds -it stress-fds --proxy=%s' % proxy)
    finally:
        cleanup_client()

@task
def cleanup():
    run('docker rm -f proxy echo')

@task
def cleanup_client():
    run('docker rm -f fds')

@task
def build_server():
    run('docker build -t stress-echo echo')

@task
def build_client():
    run('docker build -t stress-fds fds')
