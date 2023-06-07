import logging
import socket
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Exceptions import EmptyHeaderException, InvalidHeaderException
from p2pstorage_core.server.Package import PackageType, Package, ConnectionLostPackage

from db.FilesManager import FilesManager
from db.HostsManager import HostsManager
from db.SqliteSingletonManager import SqliteSingletonManager


class StorageServer:
    def __init__(self, server_address: SocketAddress):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.bind(server_address)

        self.__running = False
        self.__server_address = server_address

        self.__hosts_manager: HostsManager | None = None
        self.__files_manager: FilesManager | None = None

        self.init_hosts_manager()
        self.init_files_manager()

        self.__handle_connections_locks: dict[SocketAddress, threading.Lock] = dict()

    def get_socket_handler_thread_lock(self, host_socket: socket.socket) -> threading.Lock:
        return self.__handle_connections_locks[host_socket.getpeername()]

    def init_hosts_manager(self) -> None:
        self.__hosts_manager = HostsManager()

        self.__hosts_manager.init_table()

    def init_files_manager(self) -> None:
        self.__files_manager = FilesManager()

        self.__files_manager.init_table()

    def get_hosts_manager(self) -> HostsManager:
        return self.__hosts_manager

    def get_files_manager(self) -> FilesManager:
        return self.__files_manager

    def run(self):
        self.__server_socket.listen()

        self.__running = True

        while self.__running:
            try:
                client_socket, addr = self.__server_socket.accept()

                logging.info(f'Host {addr} try to connect...')

                handling_thread = threading.Thread(target=self.handle_connection,
                                                   args=(client_socket,))

                handling_thread.start()

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

        thread_lock = threading.Lock()

        self.__handle_connections_locks[host_addr] = thread_lock

        def disconnect_host():
            hosts_manager = self.get_hosts_manager()

            host = hosts_manager.get_host_by_addr(host_addr)

            logging.info(f'Host {host_addr}:{host.host_name} disconnected!')

            if hosts_manager.contains_host(host_addr):
                hosts_manager.remove_host(host_addr)

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
            handle_package(package, host_socket, self, thread_lock)

        del self.__handle_connections_locks[host_addr]

        host_socket.close()

    def __del__(self):
        logging.debug('Closing db...')

        SqliteSingletonManager.instance().close()
