import logging
import socket
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Exceptions import EmptyHeaderException, InvalidHeaderException
from p2pstorage_core.server.Package import PackageType, Package, ConnectionLostPackage


class StorageServer:
    def __init__(self, server_address: SocketAddress):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__server_address = server_address

        self.__server_socket.bind(server_address)

        self.__connected_hosts: dict[SocketAddress, socket.socket] = dict()

        self.__running = False

    def add_connected_host(self, addr: SocketAddress, host_socket: socket.socket) -> None:
        self.__connected_hosts[addr] = host_socket

    def is_host_connected(self, addr: SocketAddress) -> bool:
        return addr in self.__connected_hosts

    def remove_connected_host(self, addr: SocketAddress) -> None:
        del self.__connected_hosts[addr]

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

    def handle_connection(self, host_socket: socket.socket) -> None:
        connection_active = True
        host_addr = host_socket.getpeername()

        def disconnect_host():
            logging.info(f'Host {host_addr} disconnected!')

            if self.is_host_connected(host_addr):
                self.remove_connected_host(host_addr)

        while connection_active and self.__running:
            try:
                package = Package.recv(host_socket)
            except EmptyHeaderException:
                disconnect_host()
                break
            except InvalidHeaderException:
                logging.error(f'Invalid header from {host_addr}!')
                continue

            logging.debug(f'Package from {host_addr}: {package}')

            if package.get_type() == PackageType.CONNECTION_LOST:
                disconnect_host()
                break

            from PackagesHandlers import handle_package
            handle_package(package, host_socket, self)

        host_socket.close()
