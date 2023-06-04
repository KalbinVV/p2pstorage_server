import logging
import socket

from p2pstorage_core.server.Package import Package, ConnectionResponsePackage, PackageType

from StorageServer import StorageServer


def handle_package(package: Package, host_socket: socket.socket, server: StorageServer) -> None:
    match package.get_type():
        case PackageType.HOST_CONNECT_REQUEST:
            handle_host_connect_request(host_socket, server)


def handle_host_connect_request(host_socket: socket.socket, server: StorageServer) -> None:
    host_addr = host_socket.getpeername()

    logging.info(f'Host {host_addr} connected!')

    server.add_connected_host(host_addr, host_socket)

    successful_connect_response = ConnectionResponsePackage()

    successful_connect_response.send(host_socket)
