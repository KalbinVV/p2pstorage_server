import socket

from p2pstorage_core.server.Package import Package, PackageType, FilesListResponsePackage

from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class FilesListRequest(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.FILES_LIST_REQUEST

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        files_list = server.get_files_manager().get_files()

        files_list_response = FilesListResponsePackage(files_list=files_list)

        files_list_response.send(host)
