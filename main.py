import logging
import socket

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress

import Configuration
from StorageServer import StorageServer


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] [%(levelname)s] > %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                        )

    server_host = socket.gethostbyname(socket.gethostname())

    server_address = SocketAddress(server_host, Configuration.PORT)

    storage_server = StorageServer(server_address)

    logging.info(f'Server started on {server_address}!')

    storage_server.run()


if __name__ == '__main__':
    main()
