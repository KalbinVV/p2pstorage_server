import logging
import socket

from p2pstorage_core.server.Package import Package, PackageType

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
