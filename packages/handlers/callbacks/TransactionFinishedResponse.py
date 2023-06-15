import logging
import socket

from p2pstorage_core.server.Package import Package, PackageType, FileTransactionFinishedPackage

from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class TransactionFinishedResponse(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.TRANSACTION_FINISHED

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        receiver_addr = host.getpeername()

        server.get_transactions_manager().set_transaction_to_started(receiver_addr, False)

        logging.info(f'[Transaction] {receiver_addr} finished transaction!')

        files_manager = server.get_files_manager()
        hosts_manager = server.get_hosts_manager()

        file_name = FileTransactionFinishedPackage.from_abstract(package).get_filename()

        host_id = hosts_manager.get_host_id_by_addr(receiver_addr)
        file_id = files_manager.get_file_id_by_name(file_name)

        files_manager.add_file_owner(file_id, host_id)
