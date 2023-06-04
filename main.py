import logging

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress

from StorageServer import StorageServer


def main():
    logging.basicConfig(level=logging.DEBUG)

    server_address = SocketAddress('localhost', 5000)

    storage_server = StorageServer(server_address)

    logging.info('Server started!')

    storage_server.run()


if __name__ == '__main__':
    main()
