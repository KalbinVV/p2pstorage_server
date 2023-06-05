import logging
import socket

from p2pstorage_core.server.Host import Host
from p2pstorage_core.server.Package import Package, ConnectionResponsePackage, PackageType, ConnectionRequestPackage, \
    HostsListResponsePackage

from StorageServer import StorageServer


def handle_package(package: Package, host_socket: socket.socket, server: StorageServer) -> None:
    match package.get_type():
        case PackageType.HOST_CONNECT_REQUEST:
            handle_host_connect_request(package, host_socket, server)
        case PackageType.HOSTS_LIST_REQUEST:
            handle_host_list_request(host_socket, server)


def handle_host_connect_request(package, host_socket: socket.socket, server: StorageServer) -> None:
    connect_request_package = ConnectionRequestPackage.from_abstract(package)

    host_addr = host_socket.getpeername()
    host_name = connect_request_package.get_host_name()

    logging.info(f'Host {host_addr}:{host_name} connected!')

    server.add_connected_host(host_addr, Host(host_name, host_socket))

    successful_connect_response = ConnectionResponsePackage()

    successful_connect_response.send(host_socket)


def handle_host_list_request(host_socket: socket.socket, server: StorageServer) -> None:
    hosts = server.get_connected_hosts()

    hosts_list_response = HostsListResponsePackage(response_approved=True, hosts_list=hosts)

    hosts_list_response.send(host_socket)
