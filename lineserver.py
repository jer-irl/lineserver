import sys
from lineserver.server import Server


def main():
    if len(sys.argv) != 2:
        raise Exception("Argument should be filename")

    server = Server(8000, sys.argv[1])
    server.serve_forever()


if __name__ == '__main__':
    main()
