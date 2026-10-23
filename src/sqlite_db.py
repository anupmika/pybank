"""
Database management module for PyBank.
Handles SQLite database connections, schema creation, and migrations.
"""

import os
import sqlite3

from src.const import DB_PATH
from src.helpers.design import SingletonMeta


class SqliteDB(metaclass=SingletonMeta):
    """
    Provides a Singleton interface for SQLite database connections.
    
    Ensures only one database connection instance exists throughout
    the application lifecycle.
    """

    def db_connect(self):
        """
        Create and return a SQLite database connection.
        
        Creates necessary database files and directories, initializes
        the schema with users, accounts, and transactions tables,
        and performs any required migrations.
        
        Returns:
            sqlite3.Connection: A configured SQLite database connection.
        """
        # Ensure database directory exists
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        
        # Create database connection with WAL mode for better concurrency
        conn = sqlite3.connect(DB_PATH)
        conn.execute('PRAGMA journal_mode=WAL')
        
        # Create tables if they don't exist
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
                pin_hash TEXT,
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

        # Migration: Add pin_hash column for older database files
        # Older database files were created before PIN login existed
        columns = [row[1] for row in conn.execute('PRAGMA table_info(accounts)')]
        if 'pin_hash' not in columns:
            conn.execute('ALTER TABLE accounts ADD COLUMN pin_hash TEXT')

        conn.commit()
        return conn

