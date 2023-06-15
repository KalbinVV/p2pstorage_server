import logging

from p2pstorage_core.helper_classes.SocketAddress import SocketAddress
from p2pstorage_core.server.FileInfo import FileInfo, FileDataBaseInfo
from p2pstorage_core.server.Host import HostInfo

from db.SqliteSingletonManager import SqliteSingletonManager


class FilesManager:
    def __init__(self):
        self.__sqlite_manager = SqliteSingletonManager.instance()

    def init_tables(self) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/create_files_table.sql')
        self.__sqlite_manager.execute_file('./db/sqls/create_owners_table.sql')

    def is_contains_file_by_id(self, file_id: int) -> bool:
        return (self.__sqlite_manager.execute_file('./db/sqls/contains_file_by_id.sql',
                                                   (file_id,)).fetchone() == (1,))

    def is_contains_file_by_name(self, name: str) -> bool:
        return (self.__sqlite_manager.execute_file('./db/sqls/contains_file_by_name.sql',
                                                   (name,)).fetchone() == (1,))

    def add_file(self, file_info: FileInfo):
        self.__sqlite_manager.execute_file('./db/sqls/add_file.sql',
                                           (file_info.name, file_info.size, file_info.hash))

        logging.debug(f'File added: file_info = {file_info}')

    def get_file_by_id(self, file_id: int) -> FileDataBaseInfo:
        return FileDataBaseInfo(self.__sqlite_manager.execute_file('./db/sqls/get_file_by_id.sql',
                                                                   (file_id,)).fetchone())

    def get_file_id_by_name(self, name: str) -> int:
        return self.__sqlite_manager.execute_file('./db/sqls/get_file_id_by_name.sql',
                                                  (name,)).fetchone()[0]

    def get_files(self) -> list[FileDataBaseInfo]:
        files: list[FileDataBaseInfo] = list()

        for row in self.__sqlite_manager.execute_file('./db/sqls/get_files.sql'):
            files.append(FileDataBaseInfo(row))

        return files

    def add_file_owner(self, file_id: int, host_id: int) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/add_file_owner.sql',
                                           (file_id, host_id))

        logging.debug(f'Owner {host_id} for {file_id} file added!')

    def get_file_owners(self, file_id: int) -> list[HostInfo]:
        files_owners: list[HostInfo] = []

        for row in self.__sqlite_manager.execute_file('./db/sqls/get_file_owners.sql',
                                                      (file_id,)):

            name, addr, port = row

            files_owners.append(HostInfo(name, SocketAddress(addr, port)))

        return files_owners

    def remove_file_by_id(self, file_id: int) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/remove_file_by_id.sql',
                                           (file_id,))

        logging.info(f'File id:{file_id} removed!')

    def remove_file_owner(self, file_id: int, host_id: int) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/remove_file_owner.sql',
                                           (file_id, host_id))

        logging.info(f'File owner host_id:{host_id} for file file_id:{file_id} removed!')
