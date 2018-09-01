import http.server
from .cache import Cache
from .endpoints import handle_get_lines


class Server(http.server.ThreadingHTTPServer):
    def __init__(self, port: int, file_name: str):
        super().__init__(('127.0.0.1', port), _Handler)
        self.cache = Cache(file_name, 2 ** 20)


class _Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'LineServer/1.0'
    responses = {413: ("Request out of range", "Requested line past the end of the file")}

    endpoint_get_handlers = {
        "lines": handle_get_lines
    }

    def do_GET(self):
        endpoint = self.path.split('/')[1]
        try:
            self.endpoint_get_handlers[endpoint](self)
        except KeyError as ex:
            self.send_error(404, "No handler for endpoint", str(ex))
