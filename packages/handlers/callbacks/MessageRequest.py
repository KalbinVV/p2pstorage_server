import socket

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
        server.broadcast_package(package)
