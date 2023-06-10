import logging
import socket

from p2pstorage_core.server.Host import Host
from p2pstorage_core.server.Package import Package, PackageType, ConnectionRequestPackage, ConnectionResponsePackage, \
    NewHostConnectedPackage

import Configuration
from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class HostConnectRequest(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.HOST_CONNECT_REQUEST

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        connect_request_package = ConnectionRequestPackage.from_abstract(package)

        host_addr = host.getpeername()
        host_name = connect_request_package.get_host_name()

        logging.info(f'Host {host_addr}:{host_name} connected!')

        server.get_hosts_manager().add_host(host_addr, Host(host_name, host))

        broadcast_message = Configuration.BROADCAST_MESSAGE
        successful_connect_response = ConnectionResponsePackage(True, broadcast_message)

        successful_connect_response.send(host)

        new_host_connected_package = NewHostConnectedPackage(host_addr, host_name)
        server.broadcast_package(new_host_connected_package)
