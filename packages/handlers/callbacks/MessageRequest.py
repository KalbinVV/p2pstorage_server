import socket

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Package import Package, PackageType, MessagePackage

from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class MessageRequest(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.MESSAGE

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        message_package = MessagePackage.from_abstract(package)

        hosts_manager = server.get_hosts_manager()

        message = message_package.get_message()

        # TODO: Refactor this
        host_addr = hosts_manager.get_host_by_addr(host.getpeername()).host_socket.getpeername()

        message_broadcast_package = MessagePackage(message, SocketAddress(*host_addr))

        server.broadcast_package(message_broadcast_package)
