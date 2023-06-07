import logging
import socket

from p2pstorage_core.server.Host import Host, HostInfo
import p2pstorage_core.server.Package as Pckg

import Configuration
from StorageServer import StorageServer


def handle_package(package: Pckg.Package, host_socket: socket.socket, server: StorageServer) -> None:
    match package.get_type():
        case Pckg.PackageType.HOST_CONNECT_REQUEST:
            handle_host_connect_request(package, host_socket, server)
        case Pckg.PackageType.HOSTS_LIST_REQUEST:
            handle_host_list_request(host_socket, server)
        case Pckg.PackageType.NEW_FILE_REQUEST:
            handle_new_file_request(package, host_socket, server)


def handle_host_connect_request(package, host_socket: socket.socket, server: StorageServer) -> None:
    connect_request_package = Pckg.ConnectionRequestPackage.from_abstract(package)

    host_addr = host_socket.getpeername()
    host_name = connect_request_package.get_host_name()

    logging.info(f'Host {host_addr}:{host_name} connected!')

    server.get_hosts_manager().add_host(host_addr, Host(host_name, host_socket))

    successful_connect_response = Pckg.ConnectionResponsePackage(True,
                                                                 broadcast_message=Configuration.BROADCAST_MESSAGE)

    successful_connect_response.send(host_socket)


def handle_host_list_request(host_socket: socket.socket, server: StorageServer) -> None:
    hosts = server.get_hosts_manager().get_hosts()

    hosts_info = [HostInfo(h.host_name, h.host_socket.getpeername()) for h in hosts]

    hosts_list_response = Pckg.HostsListResponsePackage(response_approved=True, hosts_list=hosts_info)

    hosts_list_response.send(host_socket)


def handle_new_file_request(package: Pckg.Package, host_socket: socket.socket, server: StorageServer) -> None:
    new_file_request_package = Pckg.NewFileRequestPackage.from_abstract(package)

    file_info = new_file_request_package.get_file_info()

    host_addr = host_socket.getpeername()
    host_id = server.get_hosts_manager().get_host_id_by_addr(host_addr)


