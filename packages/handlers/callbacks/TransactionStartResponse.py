import socket

from p2pstorage_core.server.Package import Package, PackageType, FileTransactionStartResponsePackage

from Configuration import RATING_BONUS_FOR_FILE
from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class TransactionStartResponse(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.FILE_TRANSACTION_START_RESPONSE

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        transaction_start_response = FileTransactionStartResponsePackage.from_abstract(package)

        transactions_manager = server.get_transactions_manager()

        if transaction_start_response.is_transaction_started():
            receiver_addr = transaction_start_response.get_receiver_addr()
            receiver_host = server.get_hosts_manager().get_host_by_addr(receiver_addr)

            transactions_manager.set_transaction_to_started(receiver_addr, True)

            transaction_start_response.send(receiver_host.host_socket)

            hosts_manager = server.get_hosts_manager()

            host_id = hosts_manager.get_host_id_by_addr(host.getpeername())

            hosts_manager.increment_rating(host_id, RATING_BONUS_FOR_FILE)
