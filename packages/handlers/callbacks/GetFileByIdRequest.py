import socket
from time import sleep

from p2pstorage_core.server.Host import HostInfo
from p2pstorage_core.server.Package import Package, PackageType, FileTransactionStartResponsePackage, \
    GetFileByIdRequestPackage, FileTransactionStartRequestPackage

from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class GetFileByIdRequest(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.GET_FILE_BY_ID_REQUEST

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        get_file_by_id_request_package = GetFileByIdRequestPackage.from_abstract(package)

        files_manager = server.get_files_manager()

        file_id = get_file_by_id_request_package.get_file_id()

        if not files_manager.is_contains_file_by_id(file_id):
            get_file_by_id_response = FileTransactionStartResponsePackage(transaction_started=False,
                                                                          file_name='',
                                                                          reject_reason='File not exists!',
                                                                          sender_addr=None,
                                                                          receiver_addr=None)
            get_file_by_id_response.send(host)

            return

        file_name = files_manager.get_file_by_id(file_id).name

        hosts_manager = server.get_hosts_manager()

        transactions_manager = server.get_transactions_manager()

        host_addr = host.getpeername()

        transaction_was_started = False

        for host_info in files_manager.get_file_owners(file_id):
            owner_host = hosts_manager.get_host_by_addr(host_info.host_addr)
            owner_socket = owner_host.host_socket

            peer_name = owner_socket.getpeername()

            transaction_start_request = FileTransactionStartRequestPackage(file_name,
                                                                           establish_addr=peer_name,
                                                                           receiver_addr=host_addr)
            transaction_start_request.send(owner_socket)

            # TODO: Refactor this in future
            # Waiting response from owner host
            sleep(1)

            if transactions_manager.is_transaction_was_started(host_addr):
                transaction_was_started = True
                break
            else:
                owner_id = hosts_manager.get_host_id_by_addr(host_info.host_addr)

                files_manager.remove_file_owner(file_id, owner_id)

        if not transaction_was_started:
            transaction_start_response = FileTransactionStartResponsePackage(None,
                                                                             None,
                                                                             file_name,
                                                                             False,
                                                                             'File not exists!')
            transaction_start_response.send(host)

            files_manager.remove_file_by_id(file_id)
