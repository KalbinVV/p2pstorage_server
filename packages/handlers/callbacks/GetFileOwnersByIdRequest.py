import socket

from p2pstorage_core.server.Package import Package, PackageType, GetFileOwnersByIdRequestPackage, \
    FileOwnersResponsePackage

from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class GetFileOwnersByIdRequest(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.GET_FILE_OWNERS_BY_ID_REQUEST

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        get_file_owners_by_id_package = GetFileOwnersByIdRequestPackage.from_abstract(package)

        files_manager = server.get_files_manager()
        file_id = get_file_owners_by_id_package.get_file_id()

        if not files_manager.is_contains_file_by_id(file_id):
            unsuccessful_response = FileOwnersResponsePackage(response_approved=False,
                                                              owners=None,
                                                              reject_reason='File not exists!')
            unsuccessful_response.send(host)
            return

        file_owners = files_manager.get_file_owners(file_id)
        successful_response = FileOwnersResponsePackage(response_approved=True,
                                                        owners=file_owners)
        successful_response.send(host)
