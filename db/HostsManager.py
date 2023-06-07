import logging
import socket

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.Host import Host

from db.SqliteSingletonManager import SqliteSingletonManager


class HostsManager:
    def __init__(self):
        self.__sqlite_manager = SqliteSingletonManager.instance()
        self.__sockets_dict: dict[int, socket.socket] = dict()

    def init_table(self):
        self.__sqlite_manager.execute_file('./db/sqls/create_hosts_table.sql')

    def get_host_id_by_addr(self, host_addr: SocketAddress) -> int:
        addr, port = host_addr

        host_id, _ = self.__sqlite_manager.execute_file('./db/sqls/get_host_by_addr.sql',
                                                        (addr, port)).fetchone()

        return host_id

    def get_host_by_addr(self, host_addr: SocketAddress) -> Host:
        addr, port = host_addr

        host_id, host_name = self.__sqlite_manager.execute_file('./db/sqls/get_host_by_addr.sql',
                                                                (addr, port)).fetchone()

        return Host(host_name, self.__sockets_dict[host_id])

    def add_host(self, host_addr: SocketAddress, host: Host) -> None:
        addr, port = host_addr

        # Add host to table
        self.__sqlite_manager.execute_file('./db/sqls/add_host.sql',
                                           (host.host_name, addr, port))

        # Get created host id from table
        host_id = self.get_host_id_by_addr(host_addr)

        logging.debug(f'Host added: id = {host_id}, addr = {host_addr}')

        self.__sockets_dict[host_id] = host.host_socket

    def remove_host(self, host_addr: SocketAddress):
        host_id = self.get_host_id_by_addr(host_addr)

        self.__sqlite_manager.execute_file('./db/sqls/remove_host.sql',
                                           (host_id,))

        logging.debug(f'Host removed: id = {host_id}, addr = {host_addr}')

        del self.__sockets_dict[host_id]

    def contains_host(self, host_addr: SocketAddress):
        host_id = self.get_host_id_by_addr(host_addr)

        return (self.__sqlite_manager.execute_file('./db/sqls/contains_host.sql',
                                                   (host_id,)).fetchone() == (1,))

    def get_hosts(self) -> list[Host]:
        hosts_query = self.__sqlite_manager.execute_file('./db/sqls/get_hosts.sql')

        hosts: list[Host] = list()

        for host_query_result in hosts_query:
            host_id, host_name, _, _ = host_query_result

            hosts.append(Host(host_name, self.__sockets_dict[host_id]))

        return hosts
