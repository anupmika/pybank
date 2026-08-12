import os
import sqlite3

from src.helpers.design import SingletonMeta
from src.const import DB_PATH


class SqliteDB(metaclass=SingletonMeta):
    """
    Provides a Singleton interface for SQLite database connections.
    """

    def db_connect(self):
        """
        Create and return a SQLite database connection.
        """
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aadhar_num TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT NOT NULL,
                age INTEGER NOT NULL,
                father_name TEXT NOT NULL,
                address TEXT,
                city TEXT NOT NULL,
                initial_balance REAL NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS accounts (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_num INTEGER UNIQUE NOT NULL,
                user_id INTEGER NOT NULL,
                account_type TEXT NOT NULL DEFAULT 'savings',
                balance REAL NOT NULL DEFAULT 0,
                currency TEXT NOT NULL DEFAULT 'INR',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            CREATE TABLE IF NOT EXISTS transactions (

                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_num INTEGER NOT NULL,
                transaction_type TEXT NOT NULL,
                amount REAL NOT NULL,
                balance_after REAL NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY(account_num) REFERENCES accounts(account_num)
            );

            """)
        conn.commit()
        return conn
