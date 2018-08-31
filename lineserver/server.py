import http.server
from .cache import Cache


class _Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'LineServer/1.0'
    responses = {413: ("Request out of range", "Requested line past the end of the file")}

    def do_GET(self):
        print("Received GET request")
        line_number = self.get_line_number()
        line = self.server.cache.get_bytes_for_line(line_number)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(line)

    def get_line_number(self):
        return int(self.path.split('/')[-1])


class Server(http.server.ThreadingHTTPServer):
    def __init__(self, port: int, file_name: str):
        super().__init__(('127.0.0.1', port), _Handler)
        self.cache = Cache(file_name, 2 ** 20)
