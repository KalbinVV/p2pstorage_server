import json
import logging
import socket
import threading

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server import StreamConfiguration
from p2pstorage_core.server.Header import Header
from p2pstorage_core.server.Package import PackageType, Package


class StorageServer:
    def __init__(self, server_address: SocketAddress):
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.__server_address = server_address

        self.__server_socket.bind(server_address)

        self.__connected_hosts = set()

        self.__running = False

    def run(self):
        self.__server_socket.listen()

        self.__running = True

        while self.__running:
            try:
                client_socket, addr = self.__server_socket.accept()

                client_address: SocketAddress = addr

                logging.info(f'Host {addr} try to connect...')

                client_thread = threading.Thread(target=self.handle_connection,
                                                 args=(client_socket, SocketAddress(client_address[0],
                                                                                    client_address[1])))

                client_thread.start()
            except KeyboardInterrupt:
                self.__running = False

        self.__server_socket.close()

    def handle_connection(self, client_socket: socket.socket, client_address: SocketAddress) -> None:
        connection_active = True

        while connection_active and self.__running:
            header_data = client_socket.recv(StreamConfiguration.HEADER_SIZE)

            logging.debug(f'Header data from {client_address}: {header_data}')

            if not header_data:
                logging.info(f'Host {client_address} disconnected!')

                if client_address in self.__connected_hosts:
                    self.__connected_hosts.remove(client_address)

                connection_active = False
            else:
                header = Header.decode(header_data)

                logging.debug(f'Header from {client_address}: {header}')

                if header.get_type() == PackageType.HOST_CONNECT_REQUEST:
                    logging.debug(f'Connecting new host {client_address}...')

                    json_response = json.dumps({'host': client_address.host, 'port': client_address.port})

                    package = Package.from_json(json_response)

                    header = Header.generate_from_bytes(package.get_data(),
                                                        PackageType.HOST_SUCCESSFUL_CONNECT_RESPONSE,
                                                        client_address,
                                                        self.__server_address)

                    client_socket.send(header.encode())

                    client_socket.send(package.get_data())

                    self.__connected_hosts.add(self.__server_socket)

                    logging.info(f'Host {client_address} connected!')

        client_socket.close()
