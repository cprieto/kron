from .base_server import BaseServer


class RunsServer:
    def __init__(self, server: BaseServer):
        self.server = server

    def list(self):
        return self.server.list('api/runs')
