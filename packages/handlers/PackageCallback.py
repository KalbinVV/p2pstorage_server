import socket
from abc import ABC, abstractmethod

from p2pstorage_core.server.Package import PackageType, Package

from StorageServer import StorageServer
from packages.handlers.PackagesHandlerSingleton import PackagesHandlerSingleton


class AbstractPackageCallback(ABC):

    @classmethod
    @abstractmethod
    def get_package_type(cls) -> PackageType:
        ...

    @classmethod
    @abstractmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        ...

    @classmethod
    @abstractmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        ...

    @classmethod
    @abstractmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        ...

    @classmethod
    def register(cls) -> None:
        packages_handler = PackagesHandlerSingleton.instance()

        packages_handler.register(cls.get_package_type(), cls.handle)
