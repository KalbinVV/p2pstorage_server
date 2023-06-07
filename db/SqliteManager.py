import os
import sqlite3
from sqlite3 import Cursor


class SqliteManager:
    STORAGE_PATH = 'db/storage.db'

    def __init__(self):
        self.__connection = sqlite3.connect(self.STORAGE_PATH, check_same_thread=False)
        self.__cursor = self.__connection.cursor()

        # Add support for foreign keys
        self.__cursor.execute('PRAGMA foreign_keys = ON;')

    def execute(self, sql_query: str, parameters: tuple = tuple()) -> Cursor:
        self.__cursor.execute(sql_query, parameters)
        self.__connection.commit()

        return self.__cursor

    def execute_file(self, file_path: str, parameters: tuple = tuple()) -> Cursor:
        with open(file_path, 'r') as f:
            sql_query = f.read()

        return self.execute(sql_query, parameters)

    def close(self):
        self.__cursor.close()
        self.__connection.close()

        os.remove(self.STORAGE_PATH)
