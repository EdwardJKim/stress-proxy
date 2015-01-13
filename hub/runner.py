import time
import sys

from subprocess import Popen
from tornado.options import define, options, parse_command_line

if __name__ == "__main__":
    define('url', default='localhost')
    define('port', default='8000')
    define('N', type=int, default=1, help="number of users")
    parse_command_line()

    clients = []
    for i in range(options.N):
        p = Popen([
            sys.executable, 'hub.py',
            '--url=%s' % options.url,
            '--port=%s' % options.port,
            '--user=user%s' % i
        ])
        clients.append(p)
        time.sleep(0.25)
        if any([c.poll() is not None for c in clients]):
            break
    for c in clients:
        c.wait()
