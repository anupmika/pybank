import sqlite3

from src.common.helpers.design import SingletonMeta
from src.const import DB_PATH


class SqliteDB(metaclass=SingletonMeta):
    """
    Provides a Singleton interface for SQLite database connections.
    """

    def db_connect(self, *args, **kwargs):
        """
        Create and return a SQLite database connection.

        If no database path is provided, the default path from DB_PATH
        is used. Additional positional and keyword arguments are passed
        directly to sqlite3.connect().
        """
        if not args:
            args = (DB_PATH,)

        return sqlite3.connect(*args, **kwargs)
