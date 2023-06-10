import socket
from typing import Callable

from p2pstorage_core.server.Package import Package

from StorageServer import StorageServer

# Alias for packages handlers functions
HandlerFunction = Callable[[Package, socket.socket, StorageServer], None]
