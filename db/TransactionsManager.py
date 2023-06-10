from dataclasses import dataclass

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress


@dataclass
class Transaction:
    file_name: str
    receiver_addr: SocketAddress
    sender_addr: SocketAddress


class TransactionsManager:
    def __init__(self):
        self.__active_transactions: list[Transaction] = []
        self.__transaction_was_started: dict[SocketAddress, bool] = dict()

    def is_transaction_was_started(self, addr: SocketAddress):
        return self.__transaction_was_started.get(addr, False)

    def set_transaction_to_started(self, addr: SocketAddress, started: bool):
        self.__transaction_was_started[addr] = started
