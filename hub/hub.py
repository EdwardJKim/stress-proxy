#!/usr/bin/env python

import requests
import itertools

from tornado.ioloop import IOLoop
from tornado.log import gen_log
from tornado.options import define, options, parse_command_line
from tornado.gen import coroutine, Task

from IPython.kernel.zmq.session import Session
from nbbot import NBAPI, run_notebook

def login(hub_url, username, password):
    """Authenticate to jupyterhub and get the login cookie"""
    url = hub_url + '/login?next='
    response = requests.post(url, params=dict(
        username=username,
        password=password), verify=False)
    response.raise_for_status()
    return response.history[0].cookies

def sleep(t):
    loop = IOLoop.current()
    return Task(loop.add_timeout, loop.time() + t)

@coroutine
def start_notebook(url, port, user):
    hub_url = 'https://%s:%s/hub' % (url, port)
    user_url = 'https://%s:%s/user/%s' % (url, port, user)

    cookies = login(hub_url, user, user)
    api = NBAPI(url=user_url, cookies=cookies)

    path = 'Hello.ipynb'
    for i in itertools.count():
        gen_log.info("loading %s (%s)", user, i)
        nb = api.get_notebook(path)

        gen_log.info("starting %s (%s)", user, i)
        session = Session()
        kernel = yield api.new_kernel(session.session)

        try:
            for j in range(20):
                gen_log.info("running %s (%s:%s)", user, j, i)
                yield run_notebook(nb, kernel, session)
                yield sleep(0.05)

            gen_log.info("saving %s (%s)", user, i)
            api.save_notebook(nb, path)

        finally:
            api.kill_kernel(kernel['id'])


    gen_log.info("history: %s", response.history)
if __name__ == "__main__":
    define('url', default='localhost')
    define('port', default='443')
    define('user', default='user')
    parse_command_line()

    loop = IOLoop.current()
    start_notebook(options.url, options.port, options.user)
    IOLoop.current().start()
