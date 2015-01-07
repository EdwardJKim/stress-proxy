import sys
import time
from itertools import count
from subprocess import Popen

from tornado.options import define, options, parse_command_line


if __name__ == '__main__':
    define("host", default='proxy:8000', type=str)
    define("nservers", default=1, type=int, help="number of servers")
    define("b", default=0, type=int, help="size of message in bytes")
    define("n", default=1, type=int, help="total number of messages")
    define("nc", default=1, type=int, help="number of concurrent messages")
    
    parse_command_line()
    
    clients = []
    
    for i in count():
        url = "ws://%s/%i/ws" % (options.host, i % options.nservers)
        print(i)
        p = Popen([sys.executable, 'client.py',
            '--url=%s' % url,
            '-n=%i' % options.n,
            '-b=%i' % options.b,
            '-nc=%i' % options.nc,
        ])
        clients.append(p)
        time.sleep(0.25)
        if any([c.poll() is not None for c in clients]):
            break
    for c in clients:
        c.wait()
