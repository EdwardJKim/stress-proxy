from binascii import hexlify
import os
import time

from tornado.gen import coroutine
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
        ws.write_message('hi %i:%i' % (n, i))
        yield ws.read_message()
        print(n, i)
        yield sleep(5)
    ws.close()

def start_echo(n):
    print("starting", n)
    loop = IOLoop.current()
    echo('ws://127.0.0.1:8000/test/ws', n)
    loop.add_timeout(loop.time() + 0.25, start_echo, n+1)

if __name__ == '__main__':
    define("url", default='', type=str, help='url of server')
    define("b", default=0, type=int, help="size of message in bytes")
    define("n", default=1, type=int, help="total number of messages")
    define("nc", default=1, type=int, help="number of concurrent messages")
    define("t", default=1, type=float, help="interval between sending messages")
    parse_command_line()
    print(options.url, 'start')
    
    msg = hexlify(os.urandom(options.b // 2))
    
    IOLoop.current().run_sync(lambda : echo(options.url, msg,
        n=options.n,
        nc=options.nc,
        t=options.t,
    ))
    print(options.url, 'done')
    
