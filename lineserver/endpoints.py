def handle_get_lines(handler):
    """Handles GET requests for /lines/* requests"""
    line_number = int(handler.path.split('/')[-1])
    try:
        line = handler.server.cache.get_bytes_for_line(line_number)
        handler.send_response(200)
        handler.end_headers()
        handler.wfile.write(line)
    except IndexError as ex:
        handler.send_error(413, "{} is past the end of the file".format(line_number), str(ex))
