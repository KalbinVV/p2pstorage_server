from typing import Optional

from db.SqliteManager import SqliteManager


class SqliteSingletonManager:
    __sqlite_manager: Optional[SqliteManager] = None

    @classmethod
    def instance(cls) -> SqliteManager:
        if not cls.__sqlite_manager:
            cls.__sqlite_manager = SqliteManager()

        return cls.__sqlite_manager
