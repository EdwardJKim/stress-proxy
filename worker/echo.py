from tornado.ioloop import IOLoop
from tornado.log import app_log
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler
from tornado.websocket import WebSocketHandler

class EchoWS(WebSocketHandler):
    def on_message(self, msg):
        app_log.info("ws received %s", msg)
        self.write_message(msg)

class EchoHTTP(RequestHandler):
    def get(self):
        app_log.info("http received %s", self.request.path)
        self.finish(self.request.path)

if __name__ == '__main__':
    define('port', default=None)
    parse_command_line()
    
    app = Application([
        (r'.*/ws', EchoWS),
        (r'.*', EchoHTTP),
    ])
    print("listening on port %s" % options.port)
    app.listen(options.port)
    IOLoop.current().start()
