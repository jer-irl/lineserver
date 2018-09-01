"""
Front-end for server application.

The only command-line argument read is the filename to host
"""
import sys
from lineserver.server import Server


def main():
    if len(sys.argv) != 2:
        raise Exception("CLI argument should be filename to host")

    server = Server(8000, sys.argv[1])
    server.serve_forever()


if __name__ == '__main__':
    main()
