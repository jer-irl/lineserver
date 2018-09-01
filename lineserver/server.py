import http.server
from .cache import Cache
from . import endpoints


class Server(http.server.ThreadingHTTPServer):
    """
    Simple subclass of ThreadingHTTPServer that changes the constructor arguments
    """
    def __init__(self, port: int, file_name: str):
        super().__init__(('127.0.0.1', port), _Handler)
        self.cache = Cache(file_name, 2 ** 20)
        print("Server initialized on port {}".format(port))


class _Handler(http.server.BaseHTTPRequestHandler):
    """
    Request handler that dispatches to endpoint handlers

    self.server is a reference to the owning Server object
    """

    # For automatic HTTP functionality
    server_version = 'LineServer/1.0'
    responses = {413: ("Request out of range", "Requested line past the end of the file")}

    # Endpoint handler dispatch tables
    endpoint_get_handlers = {
        "lines": endpoints.handle_get_lines
    }

    def do_GET(self):
        """Handles all GET requests, using the `endpoint_get_handlers` dispatch table"""
        endpoint = self.path.split('/')[1]
        try:
            self.endpoint_get_handlers[endpoint](self)
        except KeyError as ex:
            self.send_error(404, "No handler for endpoint", str(ex))
