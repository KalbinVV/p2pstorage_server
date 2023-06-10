import logging
import socket
from time import sleep

from p2pstorage_core.server.Host import Host, HostInfo
import p2pstorage_core.server.Package as Pckg

import Configuration
from StorageServer import StorageServer


# TODO: Refactor this, maybe dict
def handle_package(package: Pckg.Package, host_socket: socket.socket, server: StorageServer) -> None:
    match package.get_type():
        case Pckg.PackageType.HOST_CONNECT_REQUEST:
            handle_host_connect_request(package, host_socket, server)
        case Pckg.PackageType.HOSTS_LIST_REQUEST:
            handle_host_list_request(host_socket, server)
        case Pckg.PackageType.NEW_FILE_REQUEST:
            handle_new_file_request(package, host_socket, server)
        case Pckg.PackageType.FILES_LIST_REQUEST:
            handle_files_list_request(host_socket, server)
        case Pckg.PackageType.GET_FILE_BY_ID_REQUEST:
            handle_get_file_by_id_request(package, host_socket, server)
        case Pckg.PackageType.FILE_TRANSACTION_START_RESPONSE:
            handle_transaction_start_response(package, host_socket, server)
        case Pckg.PackageType.TRANSACTION_FINISHED:
            handle_transaction_finished_response(host_socket, server)


def handle_host_connect_request(package, host_socket: socket.socket, server: StorageServer) -> None:
    connect_request_package = Pckg.ConnectionRequestPackage.from_abstract(package)

    host_addr = host_socket.getpeername()
    host_name = connect_request_package.get_host_name()

    logging.info(f'Host {host_addr}:{host_name} connected!')

    server.get_hosts_manager().add_host(host_addr, Host(host_name, host_socket))

    successful_connect_response = Pckg.ConnectionResponsePackage(True,
                                                                 broadcast_message=Configuration.BROADCAST_MESSAGE)

    successful_connect_response.send(host_socket)

    new_host_connected_package = Pckg.NewHostConnectedPackage(host_addr, host_name)
    server.broadcast_package(new_host_connected_package)


def handle_host_list_request(host_socket: socket.socket, server: StorageServer) -> None:
    hosts = server.get_hosts_manager().get_hosts()

    hosts_info = [HostInfo(h.host_name, h.host_socket.getpeername()) for h in hosts]

    hosts_list_response = Pckg.HostsListResponsePackage(response_approved=True, hosts_list=hosts_info)

    hosts_list_response.send(host_socket)


def handle_new_file_request(package: Pckg.Package, host_socket: socket.socket, server: StorageServer) -> None:
    new_file_request_package = Pckg.NewFileRequestPackage.from_abstract(package)

    files_info = new_file_request_package.get_files_info()

    host_addr = host_socket.getpeername()
    host_id = server.get_hosts_manager().get_host_id_by_addr(host_addr)

    for file_info in files_info:
        server.get_files_manager().add_file(file_info, host_id)

        new_file_response_package = Pckg.NewFileResponsePackage(file_info.name)

        new_file_response_package.send(host_socket)


def handle_files_list_request(host_socket: socket.socket, server: StorageServer) -> None:
    files_list = server.get_files_manager().get_files()

    files_list_response = Pckg.FilesListResponsePackage(files_list=files_list)

    files_list_response.send(host_socket)


def handle_get_file_by_id_request(package: Pckg.Package, host_socket: socket.socket,
                                  server: StorageServer) -> None:
    get_file_by_id_request_package = Pckg.GetFileByIdRequestPackage.from_abstract(package)

    files_manager = server.get_files_manager()

    file_id = get_file_by_id_request_package.get_file_id()

    if not files_manager.contains_file_by_id(file_id):
        get_file_by_id_response = Pckg.FileTransactionStartResponsePackage(transaction_started=False,
                                                                           file_name='',
                                                                           reject_reason='File not exists!',
                                                                           sender_addr=None,
                                                                           receiver_addr=None)
        get_file_by_id_response.send(host_socket)

        return

    file_name = files_manager.get_file_by_id(file_id).name

    hosts_manager = server.get_hosts_manager()

    transactions_manager = server.get_transactions_manager()

    host_addr = host_socket.getpeername()

    transaction_was_started = False

    for another_host in hosts_manager.get_hosts():
        # if another_host.host_socket.getpeername() == host_socket.getpeername():
        # continue

        peer_name = another_host.host_socket.getpeername()

        transaction_start_request = Pckg.FileTransactionStartRequestPackage(file_name,
                                                                            establish_addr=peer_name,
                                                                            receiver_addr=host_addr)
        transaction_start_request.send(another_host.host_socket)

        # Waiting response from another host
        sleep(1)

        if transactions_manager.is_transaction_was_started(host_addr):
            transaction_was_started = True
            break

    if not transaction_was_started:
        transaction_start_response = Pckg.FileTransactionStartResponsePackage(None,
                                                                              None,
                                                                              file_name,
                                                                              False,
                                                                              'File not exists!')
        transaction_start_response.send(host_socket)


def handle_transaction_start_response(package: Pckg.Package, _host_socket: socket.socket,
                                      server: StorageServer) -> None:
    transaction_start_response = Pckg.FileTransactionStartResponsePackage.from_abstract(package)

    transactions_manager = server.get_transactions_manager()

    if transaction_start_response.is_transaction_started():
        receiver_addr = transaction_start_response.get_receiver_addr()
        receiver_host = server.get_hosts_manager().get_host_by_addr(receiver_addr)

        transactions_manager.set_transaction_to_started(receiver_addr, True)

        transaction_start_response.send(receiver_host.host_socket)


def handle_transaction_finished_response(host_socket: socket.socket, server: StorageServer) -> None:
    receiver_addr = host_socket.getpeername()

    server.get_transactions_manager().set_transaction_to_started(receiver_addr, False)

    logging.info(f'[Transaction] {receiver_addr} finished transaction!')
