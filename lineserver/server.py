import http.server
from .cache import Cache


class _Handler(http.server.BaseHTTPRequestHandler):
    server_version = 'LineServer/1.0'
    responses = {413: ("Request out of range", "Requested line past the end of the file")}

    def do_GET(self):
        line_number = self.get_line_number()
        line = self.server.cache.get_bytes_for_line(line_number)
        message = self.MessageClass()
        message.set_payload(line)
        self.send_response(200, message)

    def get_line_number(self):
        return int(self.requestline.split('/')[-1])


class Server(object):
    def __init__(self, port: int, file_name: str):
        self.cache = Cache(file_name, 2 ** 20)
        self.server = http.server.ThreadingHTTPServer('127.0.0.1:{}'.format(port), _Handler)

    def serve_forever(self):
        self.server.serve_forever()
