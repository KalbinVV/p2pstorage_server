import logging

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.FileInfo import FileInfo, FileDataBaseInfo

from db.SqliteSingletonManager import SqliteSingletonManager


class FilesManager:
    def __init__(self):
        self.__sqlite_manager = SqliteSingletonManager.instance()

    def init_table(self) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/create_files_table.sql')

    def contains_file_by_id(self, file_id: int) -> bool:
        return (self.__sqlite_manager.execute_file('./db/sqls/contains_file_by_id.sql',
                                                   (file_id,)).fetchone() == (1,))

    def add_file(self, file_info: FileInfo, host_id: int):
        self.__sqlite_manager.execute_file('./db/sqls/add_file.sql',
                                           (host_id, file_info.name, file_info.size, file_info.hash))

        logging.debug(f'File added: host_id = {host_id}, file_info = {file_info}')

    def get_file_by_id(self, file_id: int) -> FileDataBaseInfo:
        return FileDataBaseInfo(self.__sqlite_manager.execute_file('./db/sqls/get_file_by_id.sql',
                                                                   (file_id,)).fetchone())

    def get_files(self) -> list[FileDataBaseInfo]:
        files: list[FileDataBaseInfo] = list()

        for row in self.__sqlite_manager.execute_file('./db/sqls/get_files.sql'):
            files.append(FileDataBaseInfo(row))

        return files

    def get_file_owners(self, file_id: int) -> list[SocketAddress]:
        files_owners: list[SocketAddress] = list()

        for row in self.__sqlite_manager.execute_file('./db/sqls/get_files_owners.sql',
                                                      (file_id,)):
            addr, port = row

            files_owners.append(SocketAddress(addr, port))

        return files_owners

    def remove_file_owner(self, file_id: int, host_id: int) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/remove_file_owner.sql',
                                           (file_id, host_id))
