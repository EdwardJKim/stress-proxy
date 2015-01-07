#!/usr/bin/env python

import json
import socket
import sys
from subprocess import Popen

import requests
from tornado.options import define, options, parse_command_line

myip = socket.gethostbyname(socket.gethostname())

def spawn_worker(i, host):
    port = 9000 + i
    url = 'http://%s:8001/api/routes/%i' % (host, i)
    print("posting to %s" % url)
    r = requests.post(url, data=json.dumps({
        'target': 'http://%s:%i' % (myip, port),
    }))
    r.raise_for_status()
    worker = Popen([sys.executable, 'echo.py', '--port=%i' % port])
    return worker


if __name__ == '__main__':

    define("id", default=1, type=int, help="integer id of worker to start")
    define("proxy", default='proxy', help="proxy hostname")

    parse_command_line()

    worker = spawn_worker(options.id, options.proxy)
    print("worker %i ready to go" % options.id)
    worker.wait()
