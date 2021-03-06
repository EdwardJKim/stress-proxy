#!/usr/bin/env python

"""
Simulate open/run/save of an IPython Notebook


Usage:

    python nbbot.py [--url=http://host:port[/base_url]] notebook.ipynb [notebook2.ipynb]
"""

import json
import logging

import requests
# don't need requests logs
logging.getLogger("requests").setLevel(logging.WARNING)

from tornado import gen
from tornado.log import gen_log, enable_pretty_logging
from tornado.options import options
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.websocket import websocket_connect

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

from IPython.html.utils import url_path_join
from IPython.kernel.zmq.session import Session
from IPython import nbformat
from IPython.utils.jsonutil import date_default

class NBAPI(object):
    """API wrapper for the relevant bits of the IPython REST API"""
    
    def __init__(self, url='http://localhost:8888', cookies=None):
        self.url = url
        self.cookies = cookies or {}
    
    def api_request(self, *path, **kwargs):
        """Make an API request"""
        url = url_path_join(self.url, 'api', *path)
        kwargs.setdefault('method', 'GET')
        kwargs.setdefault('cookies', self.cookies)
        kwargs['url'] = url
        gen_log.debug("%s %s", kwargs['method'], url)
        kwargs['verify'] = False
        r = requests.request(**kwargs)
        r.raise_for_status()
        if r.history and '/login' in r.url:
            raise requests.HTTPError("Login failed", response=r)
        if r.text != '':
            return r.json()
    
    def contents(self, path=''):
        return self.api_request('contents', path)
    
    def get_notebook(self, path):
        """Get a notebook"""
        model = self.contents(path)
        return nbformat.from_dict(model['content'])
    
    def _split_path(self, path):
        if '/' in path:
            path, name = path.rsplit('/', 0)
        else:
            path = ''
            name = path
        return path, name
    
    def save_notebook(self, nb, path):
        """Save a notebook"""
        model = {
            'content': nb,
            'type': 'notebook',
            'format': 'json',
        }
        return self.api_request('contents', path, method='PUT',
            data=json.dumps(model),
        )
    
    @gen.coroutine
    def new_kernel(self, session_id):
        """Start a new kernel, and connect a websocket for each channel
        
        Returns Kernel model dict, adding websocket object at each channel name.
        """
        kernel = self.api_request('kernels', method='POST',
            data=json.dumps({
                'name': 'python'
            })
        )
        kernel_id = kernel['id']
        cookie_headers = {
            'Cookie': '; '.join(['%s=%s' % (name, value) for name, value in self.cookies.items()])
        }
        url = url_path_join('ws' + self.url[4:], 'api', 'kernels', kernel_id, 'channels')
        url += '?session_id=%s' % session_id
        req = HTTPRequest(url, headers=cookie_headers, validate_cert=False)
        kernel['channels'] = yield websocket_connect(req)
        raise gen.Return(kernel)

    def kill_kernel(self, kernel_id):
        """kill a kernel by ID"""
        self.api_request('kernels', kernel_id, method='DELETE')


@gen.coroutine
def execute(cell, kernel, session):
    """Run a single cell, waiting for its output"""
    msg = session.msg('execute_request', content={
        'code': cell.source,
        'user_expressions': [],
        'silent': False,
        'allow_stdin': False,
    })
    msg['channel'] = 'shell'
    
    parent_id = msg['header']['msg_id']
    
    ws = kernel['channels']
    gen_log.debug("Executing:\n%s", cell.source)
    ws.write_message(json.dumps(msg, default=date_default))
    
    output_done = False
    shell_done = False
    while not (output_done and shell_done):
        jmsg = yield ws.read_message()
        msg = json.loads(jmsg)
        if msg['channel'] == 'iopub':
            gen_log.debug("output:\n%s", json.dumps(msg['content'], indent=1))
            if msg['msg_type'] == 'status' \
                and msg['content']['execution_state'] == 'idle' \
                and msg['parent_header']['msg_id'] == parent_id:
                output_done = True
        elif msg['channel'] == 'shell':
            gen_log.debug("reply:\n%s", json.dumps(msg['content'], indent=1))
            shell_done = True
        else:
            gen_log.warn("Unrecognized channel: %s\n%s",
                msg['channel'],
                json.dumps(msg['content'], indent=1)
            )


@gen.coroutine
def run_notebook(nb, kernel, session):
    """Run all the cells of a notebook"""
    ncells = sum(cell['cell_type'] == 'code' for cell in nb.cells)
    i = 0
    for cell in nb.cells:
        if cell['cell_type'] == 'code':
            i += 1
            gen_log.info("Executing cell %i/%i", i, ncells)
            yield execute(cell, kernel, session)


@gen.coroutine
def open_run_save(api, path):
    """open a notebook, run it, and save.
    
    Only the original notebook is saved, the output is not recorded.
    """
    nb = api.get_notebook(path)
    session = Session()
    kernel = yield api.new_kernel(session.session)
    try:
        yield run_notebook(nb, kernel, session)
    finally:
        api.kill_kernel(kernel['id'])
    gen_log.info("Saving %s/notebooks/%s", api.url, path)
    api.save_notebook(nb, path)

if __name__ == '__main__':
    enable_pretty_logging()
    options.define("url", default="http://localhost:8888",
        help="The base URL of the notebook server to test"
    )
    args = options.parse_command_line()
    paths = args or ['Untitled0.ipynb']
    
    api = NBAPI(url=options.url.rstrip('/'))
    loop = IOLoop.current()
    
    for path in paths:
        gen_log.info("Running %s/notebooks/%s", api.url, path)
        loop.run_sync(lambda : open_run_save(api, path))
