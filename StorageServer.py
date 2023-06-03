import logging
import socket
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Package import PackageType, Package, ConnectionResponsePackage


class StorageServer:
    def __init__(self, server_address: SocketAddress):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__server_address = server_address

        self.__server_socket.bind(server_address)

        self.__connected_hosts = set()

        self.__running = False

    def run(self):
        self.__server_socket.listen()

        self.__running = True

        while self.__running:
            try:
                client_socket, addr = self.__server_socket.accept()

                client_address: SocketAddress = addr

                logging.info(f'Host {addr} try to connect...')

                client_thread = threading.Thread(target=self.handle_connection,
                                                 args=(client_socket,))

                client_thread.start()
            except KeyboardInterrupt:
                self.__running = False

        self.__server_socket.close()

    def handle_connection(self, client_socket: socket.socket) -> None:
        connection_active = True

        while connection_active and self.__running:
            package = Package.recv(client_socket)

            if package.get_type() == PackageType.HOST_CONNECT_REQUEST:
                logging.info(f'Host {client_socket.getpeername()} connected!')

                successful_connect_response = ConnectionResponsePackage()

                successful_connect_response.send(client_socket)

        client_socket.close()
