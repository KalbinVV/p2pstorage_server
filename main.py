import logging
import socket

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress

import Configuration
from StorageServer import StorageServer
from db.SqliteSingletonManager import SqliteSingletonManager
from packages.handlers.PackagesHandler import PackagesHandler


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] [%(levelname)s] > %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                        )

    if Configuration.HOST is None:
        server_host = socket.gethostbyname(socket.gethostname())
    else:
        server_host = Configuration.HOST

    server_address = SocketAddress(server_host, Configuration.PORT)

    storage_server = StorageServer(server_address)

    logging.info(f'Registering handlers...')

    PackagesHandler.init_callbacks()

    logging.info(f'Server started on {server_address}!')

    storage_server.run()


if __name__ == '__main__':
    main()
