import socket

from p2pstorage_core.server.Host import HostInfo
from p2pstorage_core.server.Package import Package, PackageType, HostsListResponsePackage

from StorageServer import StorageServer
from packages.handlers.PackageCallback import AbstractPackageCallback


class HostListRequest(AbstractPackageCallback):
    @classmethod
    def get_package_type(cls) -> PackageType:
        return PackageType.HOSTS_LIST_REQUEST

    @classmethod
    def before_handle(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def after_handler(cls, package: Package, host: socket.socket, server: StorageServer) -> None:
        pass

    @classmethod
    def handle(cls, package: Package, host: socket.socket, server: StorageServer):
        hosts = server.get_hosts_manager().get_hosts()

        hosts_info = [HostInfo(h.host_name, h.host_socket.getpeername()) for h in hosts]

        hosts_list_response = HostsListResponsePackage(response_approved=True, hosts_list=hosts_info)

        hosts_list_response.send(host)

