from binascii import hexlify
import os
import sys
import time
from subprocess import Popen
from itertools import count

from tornado.gen import coroutine, Task
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.websocket import websocket_connect


def sleep(t):
    loop = IOLoop.current()
    return Task(loop.add_timeout, loop.time() + t)

@coroutine
def echo(url, n):
    try:
        ws = yield websocket_connect(url)
    except:
        sys.exit(1)

    for i in count():
        ws.write_message('%i:%i' % (n, i))
        yield ws.read_message()
        print(n, i)
        yield sleep(5)
    ws.close()

def start_echo(host, n):
    print("starting", n)
    loop = IOLoop.current()
    echo('ws://%s:8000/test/ws' % host, n)
    loop.add_timeout(loop.time() + 0.25, start_echo, host, n+1)

define("echo", default='echo')
define("proxy", default='proxy')
parse_command_line()
if options.proxy == 'localhost':
    proxy = Popen(['configurable-http-proxy', '--default-target=http://%s:9000' % options.echo])
    time.sleep(1)
    assert proxy.poll() is None

if options.echo == 'localhost':
    worker = Popen([sys.executable, 'echo.py', '--port=9000'])
    time.sleep(1)
    assert worker.poll() is None

start_echo(options.proxy, 0)
IOLoop.current().start()
