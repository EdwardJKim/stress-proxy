import sys
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
        print("couldn't connect to websocket (%s %s)" % (url, n))
        sys.exit(1)

    print("connected to %s %s" % (url, n))
    for i in count():
        ws.write_message('%i:%i' % (n, i))
        yield ws.read_message()
        yield sleep(5)
    ws.close()

def start_echo(host, name, n):
    loop = IOLoop.current()
    url = 'ws://%s:8000/%s/ws' % (host, name)
    echo(url, n)
    loop.add_timeout(loop.time() + 0.25, start_echo, host, name, n+1)

define("proxy", default='proxy')
define("n", default=1, type=int, help="number of workers")
parse_command_line()

print(options.proxy)
for i in range(options.n):
    start_echo(options.proxy, i, 0)
IOLoop.current().start()
