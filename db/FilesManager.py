import logging

from p2pstorage_core.server.FileInfo import FileInfo, FileDataBaseInfo

from db.SqliteSingletonManager import SqliteSingletonManager


class FilesManager:
    def __init__(self):
        self.__sqlite_manager = SqliteSingletonManager.instance()

    def init_table(self) -> None:
        self.__sqlite_manager.execute_file('./db/sqls/create_files_table.sql')

    def add_file(self, file_info: FileInfo, host_id: int):
        self.__sqlite_manager.execute_file('./db/sqls/add_file.sql',
                                           (host_id, file_info.name, file_info.size, file_info.hash))

        logging.debug(f'File added: host_id = {host_id}, file_info = {file_info}')

    def get_files(self) -> list[FileDataBaseInfo]:
        files: list[FileDataBaseInfo] = list()

        for row in self.__sqlite_manager.execute_file('./db/sqls/get_files.sql'):
            files.append(FileDataBaseInfo(row))

        return files
