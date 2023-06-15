import logging
import socket

from p2pstorage_core.server.Package import Package, PackageType, NewFileRequestPackage, NewFileResponsePackage

from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class NewFileRequest(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.NEW_FILE_REQUEST

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        new_file_request_package = NewFileRequestPackage.from_abstract(package)

        files_info = new_file_request_package.get_files_info()

        host_addr = host.getpeername()
        host_id = server.get_hosts_manager().get_host_id_by_addr(host_addr)

        files_manager = server.get_files_manager()

        for file_info in files_info:
            if not files_manager.is_contains_file_by_name(file_info.name):
                files_manager.add_file(file_info)

                response_msg = f'[File not exists before]: {file_info.name}'
            else:
                response_msg = f'[File already exists]: {file_info.name}'

            logging.debug(file_info)
            logging.debug(files_manager.is_contains_file_by_name(file_info.name))

            file_id = files_manager.get_file_id_by_name(file_info.name)

            logging.debug(file_id)

            files_manager.add_file_owner(file_id=file_id, host_id=host_id)

            new_file_response_package = NewFileResponsePackage(response_msg)

            new_file_response_package.send(host)
