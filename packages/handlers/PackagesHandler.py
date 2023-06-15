import logging
import socket
from p2pstorage_core.server.Package import Package, PackageType

from StorageServer import StorageServer
from packages.Utils import HandlerFunction


class PackagesHandler:
    def __init__(self):
        self.__packages_callbacks: dict[PackageType, HandlerFunction] = dict()

    def register(self, package_type: PackageType, handler: HandlerFunction):
        if package_type in self.__packages_callbacks:
            raise Exception(f'{package_type} already registered!')

        logging.info(f'Registering callback for {package_type.name}...')

        self.__packages_callbacks[package_type] = handler

    def handle(self, package: Package, host: socket.socket, server: StorageServer):
        package_type = package.get_type()

        try:
            self.__packages_callbacks[package_type](package, host, server)
        except KeyError:
            raise Exception(f'{package_type} callback not exists!')

    @staticmethod
    def init_callbacks() -> None:
        # TODO: Refactor this
        from packages.handlers.callbacks.FilesListRequest import FilesListRequest
        from packages.handlers.callbacks.GetFileByIdRequest import GetFileByIdRequest
        from packages.handlers.callbacks.HostConnectRequest import HostConnectRequest
        from packages.handlers.callbacks.HostListRequest import HostListRequest
        from packages.handlers.callbacks.NewFileRequest import NewFileRequest
        from packages.handlers.callbacks.TransactionFinishedResponse import TransactionFinishedResponse
        from packages.handlers.callbacks.TransactionStartResponse import TransactionStartResponse
        from packages.handlers.callbacks.GetFileOwnersByIdRequest import GetFileOwnersByIdRequest
        from packages.handlers.callbacks.MessageRequest import MessageRequest

        HostConnectRequest.register()
        HostListRequest.register()
        NewFileRequest.register()
        FilesListRequest.register()
        GetFileByIdRequest.register()
        TransactionStartResponse.register()
        TransactionFinishedResponse.register()
        GetFileOwnersByIdRequest.register()
        MessageRequest.register()
