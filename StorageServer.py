import logging
import socket
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Exceptions import EmptyHeaderException
from p2pstorage_core.server.Package import PackageType, Package, ConnectionResponsePackage, ConnectionLostPackage


class StorageServer:
    def __init__(self, server_address: SocketAddress):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__server_address = server_address

        self.__server_socket.bind(server_address)

        self.__connected_hosts: dict[SocketAddress, socket.socket] = dict()

        self.__running = False

    def run(self):
        self.__server_socket.listen()

        self.__running = True

        while self.__running:
            try:
                client_socket, addr = self.__server_socket.accept()

                logging.info(f'Host {addr} try to connect...')

                client_thread = threading.Thread(target=self.handle_connection,
                                                 args=(client_socket,))

                client_thread.start()

            except KeyboardInterrupt:
                self.__running = False

        logging.info('Closing connections...')

        for host_addr, host_socket in self.__connected_hosts.items():
            server_stop_package = ConnectionLostPackage('Server stopped')

            server_stop_package.send(host_socket)

        self.__server_socket.close()

    def handle_connection(self, client_socket: socket.socket) -> None:
        connection_active = True
        host_addr = client_socket.getpeername()

        while connection_active and self.__running:
            try:
                package = Package.recv(client_socket)
            except EmptyHeaderException:
                logging.info(f'Host {client_socket.getpeername()} disconnected!')

                if host_addr in self.__connected_hosts.keys():
                    del self.__connected_hosts[host_addr]

                break

            if package.get_type() == PackageType.HOST_CONNECT_REQUEST:
                logging.info(f'Host {host_addr} connected!')

                self.__connected_hosts[host_addr] = client_socket

                successful_connect_response = ConnectionResponsePackage()

                successful_connect_response.send(client_socket)

        client_socket.close()
