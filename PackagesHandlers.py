import logging
import socket
import threading

from p2pstorage_core.server.Host import Host, HostInfo
import p2pstorage_core.server.Package as Pckg

import Configuration
from StorageServer import StorageServer


def handle_package(package: Pckg.Package, host_socket: socket.socket, server: StorageServer,
                   thread_lock: threading.Lock) -> None:
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
            handle_get_file_by_id_request(package, host_socket, server, thread_lock)


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

    files_info = new_file_request_package.get_files_info()

    host_addr = host_socket.getpeername()
    host_id = server.get_hosts_manager().get_host_id_by_addr(host_addr)

    for file_info in files_info:
        server.get_files_manager().add_file(file_info, host_id)

        new_file_response_package = Pckg.NewFileResponsePackage()

        new_file_response_package.send(host_socket)


def handle_files_list_request(host_socket: socket.socket, server: StorageServer) -> None:
    files_list = server.get_files_manager().get_files()

    files_list_response = Pckg.FilesListResponsePackage(files_list=files_list)

    files_list_response.send(host_socket)


def handle_get_file_by_id_request(package: Pckg.Package, host_socket: socket.socket,
                                  server: StorageServer, thread_lock) -> None:

    thread_lock.acquire()

    get_file_by_id_request_package = Pckg.GetFileByIdRequestPackage.from_abstract(package)

    files_manager = server.get_files_manager()

    file_id = get_file_by_id_request_package.get_file_id()

    if not files_manager.contains_file_by_id(file_id):
        get_file_by_id_response = Pckg.FileTransactionStartResponsePackage(transaction_started=False,
                                                                           file_name='',
                                                                           reject_reason='File not exists!',
                                                                           sender_addr=None)
        get_file_by_id_response.send(host_socket)
        return
    else:
        hosts_manager = server.get_hosts_manager()

        files_owners = files_manager.get_file_owners(file_id)

        file_info = files_manager.get_file_by_id(file_id)

        sender_host: socket.socket | None = None

        for addr in files_owners:
            host = hosts_manager.get_host_by_addr(addr)

            #if host.host_socket.getpeername() == host_socket.getpeername():
               # continue

            contains_file_request = Pckg.FileContainsRequestPackage(file_info.name)
            contains_file_request.send(host.host_socket)

            contains_file_response: Pckg.FileContainsResponsePackage = Pckg.Package.recv(host.host_socket)

            if contains_file_response.is_file_contains():
                sender_host = host.host_socket
                break

        if not sender_host:
            transaction_start_response = Pckg.FileTransactionStartResponsePackage(transaction_started=False,
                                                                                  file_name='',
                                                                                  reject_reason='File not exists!',
                                                                                  sender_addr=None)
            transaction_start_response.send(host_socket)
        else:
            transaction_start_request = Pckg.FileTransactionStartRequestPackage(file_info.name)
            transaction_start_request.send(sender_host)

            transaction_start_response: Pckg.FileTransactionStartResponsePackage = Pckg.Package.recv(host_socket)
            transaction_start_response.send(host_socket)

    thread_lock.release()
