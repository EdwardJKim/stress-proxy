#!/usr/bin/env python

import requests

from tornado.ioloop import IOLoop
from tornado.log import gen_log, enable_pretty_logging
from tornado.options import define, options, parse_command_line

from nbbot import NBAPI, open_run_save

def login(hub_url, username, password):
    """Authenticate to jupyterhub and get the login cookie"""
    url = hub_url + '/login?next='
    response = requests.post(url, params=dict(
        username=username,
        password=password))
    response.raise_for_status()
    return response.history[0].cookies


if __name__ == "__main__":
    define('url', default='localhost')
    define('port', default='8000')
    define('user', default='user')
    parse_command_line()

    enable_pretty_logging()

    hub_url = 'http://%s:%s/hub' % (options.url, options.port)
    user_url = 'http://%s:%s/user/%s' % (options.url, options.port, options.user)

    cookies = login(hub_url, options.user, options.user)
    api = NBAPI(url=user_url, cookies=cookies)
    loop = IOLoop.current()

    paths = ['Untitled.ipynb']
    for path in paths:
        gen_log.info("Running %s/notebooks/%s", api.url, path)
        loop.run_sync(lambda: open_run_save(api, path))
