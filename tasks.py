import time
import socket
from subprocess import Popen, check_output, check_call

from invoke import task, run

def start_proxy():
    return check_output([
        'docker', 'run', '--name=proxy', '-dt', 'jupyter/configurable-http-proxy', '--api-ip=0.0.0.0',
    ]).decode('ascii').strip()

def start_workers(n):
    return check_output([
        'docker', 'run', '--name=worker', '--link', 'proxy:proxy', '-dt', 'stress-worker', '-n=%i' % n,
    ])

def run_client(n, p):
    return check_call([
        'docker', 'run', '--name=client', '--link', 'proxy:proxy', '-it', 'stress-client',
        '--nservers=%i' % p,
        '--n=%i' % n,
        '--b=1024',
    ])

@task
def fds(local_echo=False, local_proxy=False):
    args = ''
    if not local_echo:
        print("starting echo container")
        run('docker run --name echo --net=host -dt stress-echo')
    if not local_proxy:
        assert not local_echo
        print("starting proxy container")
        cmd = 'docker run --name proxy -dt --net=host jupyter/configurable-http-proxy --api-ip=0.0.0.0 --default-target=http://127.0.0.1:9000'
        run(cmd)
    
    try:
        time.sleep(1)
        cmd = 'docker run --net=host'
        args = '' 
        if not local_echo and local_proxy:
            # cmd += ' --link echo:echo '
            args += ' --echo=echo '
        if not local_proxy:
            # cmd += ' --link proxy:proxy '
            args += ' --proxy=proxy '
        print('starting client')
        run(cmd + ' --name fds -it stress-fds ' + args)
    finally:
        cleanup()

@task
def test(n=1, p=1):
    try:
        proxy_id = start_proxy()
        worker_id = start_workers(n)
        time.sleep(0.1 * n)
        run_client(n, p)
    finally:
        cleanup()

@task
def cleanup():
    run('docker rm -f proxy worker client echo fds')

@task
def build():
    run('docker build -t stress-worker worker')
    run('docker build -t stress-client client')
    run('docker build -t stress-echo echo')
    run('docker build -t stress-fds fds')
