#!/usr/bin/env python

import requests

from tornado.ioloop import IOLoop
from tornado.log import gen_log
from tornado.options import define, options, parse_command_line
from tornado.gen import coroutine

from nbbot import NBAPI, open_run_save

def login(hub_url, username, password):
    """Authenticate to jupyterhub and get the login cookie"""
    url = hub_url + '/login?next='
    response = requests.post(url, params=dict(
        username=username,
        password=password))
    response.raise_for_status()
    return response.history[0].cookies

@coroutine
def start_notebook(url, port, user):
    hub_url = 'http://%s:%s/hub' % (url, port)
    user_url = 'http://%s:%s/user/%s' % (url, port, user)

    cookies = login(hub_url, user, user)
    api = NBAPI(url=user_url, cookies=cookies)

    path = 'Hello.ipynb'
    gen_log.info("Running %s/notebooks/%s", api.url, path)
    open_run_save(api, path)


if __name__ == "__main__":
    define('url', default='localhost')
    define('port', default='8000')
    define('N', type=int, default=1, help="number of users")
    parse_command_line()

    loop = IOLoop.current()
    for i in range(options.N):
        loop.run_sync(lambda: start_notebook(options.url, options.port, "user{}".format(i)))
    IOLoop.current().start()
