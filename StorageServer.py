import logging
import socket
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Exceptions import EmptyHeaderException, InvalidHeaderException
from p2pstorage_core.server.Host import Host
from p2pstorage_core.server.Package import PackageType, Package, ConnectionLostPackage

from db.HostsManager import HostsManager
from db.SqliteSingletonManager import SqliteSingletonManager


class StorageServer:
    def __init__(self, server_address: SocketAddress):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind(server_address)

        self.__running = False
        self.__server_address = server_address
        self.__hosts_manager: HostsManager | None = None

        self.init_hosts_manager()

    def init_hosts_manager(self) -> None:
        self.__hosts_manager = HostsManager()

        self.__hosts_manager.init_table()

    def add_connected_host(self, addr: SocketAddress, host: Host) -> None:
        self.__hosts_manager.add_host(addr, host)

    def is_host_connected(self, addr: SocketAddress) -> bool:
        return self.__hosts_manager.contains_host(addr)

    def remove_connected_host(self, addr: SocketAddress) -> None:
        return self.__hosts_manager.remove_host(addr)

    def get_connected_hosts(self) -> list[Host]:
        return self.__hosts_manager.get_hosts()

    def get_connected_host_by_addr(self, addr: SocketAddress) -> Host:
        host_id, host_name, host_socket = self.__hosts_manager.get_host_by_addr(addr)

        return Host(host_name, host_socket)

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

        for host in self.__hosts_manager.get_hosts():
            server_stop_package = ConnectionLostPackage('Server stopped')

            server_stop_package.send(host.host_socket)

        self.__server_socket.close()

    def handle_connection(self, host_socket: socket.socket) -> None:
        connection_active = True
        host_addr = host_socket.getpeername()

        def disconnect_host():
            host = self.get_connected_host_by_addr(host_addr)

            logging.info(f'Host {host_addr}:{host.host_name} disconnected!')

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

    def __del__(self):
        logging.debug('Closing db...')

        SqliteSingletonManager.instance().close()