from docker_oauth import DockerAuthenticator
from tornado import gen

class TestAuthenticator(DockerAuthenticator):

    @gen.coroutine
    def authenticate(self, handler, data):
        username = data['username']
        if self.whitelist and username not in self.whitelist:
            return
        if username == data['password']:
            return username
