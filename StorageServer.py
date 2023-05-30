import logging
import socket
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Header import Header
from p2pstorage_core.server.Package import AbstractPackage, PackageType


class StorageServer:
    def __init__(self, server_address: SocketAddress):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__server_address = server_address

        self.__server_socket.bind(server_address)

        self.__connected_hosts = set()

    def run(self):
        self.__server_socket.listen()

        running = True

        while running:
            client_socket, addr = self.__server_socket.accept()

            client_address: SocketAddress = addr

            logging.info(f'Host {addr} try to connect...')

            client_thread = threading.Thread(target=self.handle_connection, args=(client_socket,
                                                                                  client_address))

            client_thread.start()

    def handle_connection(self, client_socket: socket.socket, client_address: SocketAddress) -> None:
        connection_active = True

        while connection_active:
            header_data = client_socket.recv(Header.MAX_SIZE)

            header = Header.decode(header_data)

            if header.get_type() == PackageType.HOST_CONNECTED:
                header = Header(0, PackageType.HOST_CONNECTED, client_address)

                self.__server_socket.send()

                self.__connected_hosts.add(self.__server_socket)

                logging.info(f'Host {client_address} connected!')
