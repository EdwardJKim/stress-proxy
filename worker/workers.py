#!/usr/bin/env python

import argparse
import json
import socket
import sys
from subprocess import Popen

import requests
from tornado.options import define, options, parse_command_line

myip = socket.gethostbyname(socket.gethostname())

def spawn_worker(i, host):
    port = 8000 + i
    r = requests.post('http://%s:8001/api/routes/%i' % (host, i), data=json.dumps({
        'target': 'http://%s:%i' % (myip, port),
    }))
    r.raise_for_status()
    worker = Popen([sys.executable, 'echo.py', '--port=%i' % port])
    return worker


if __name__ == '__main__':
    
    define("n", default=1, type=int, help="number of workers to start")
    define("proxy_host", default='proxy', help="proxy hostname")

    parse_command_line()
    
    workers = []
    for i in range(options.n):
        workers.append(spawn_worker(i, options.proxy_host))
    print("%i workers ready to go" % options.n)
    for w in workers:
        w.wait()

