"""
Database management module for PyBank.
Handles SQLite database connections, schema creation, and migrations.
"""

import os
import shutil
import sqlite3
from pathlib import Path

from src.const import DB_PATH as _DEFAULT_DB_PATH
from src.helpers.design import SingletonMeta

# Allow tests to override this module-level path
DB_PATH = _DEFAULT_DB_PATH


class SqliteDB(metaclass=SingletonMeta):
    """
    Provides a Singleton interface for SQLite database connections.

    Ensures only one database connection instance exists throughout
    the application lifecycle.
    """

    def _get_writable_db_path(self):
        """Determine a writable database path (fallback to /tmp on cloud)."""
        candidate = DB_PATH

        # If tests have overridden to a custom path (e.g., temp file), respect it
        # unless it's in a clearly unwritable cloud repo mount
        is_cloud_mount = os.path.exists('/mount/src') or bool(
            os.environ.get('STREAMLIT_SERVER_PORT')
            or os.environ.get('STREAMLIT_RUNTIME_ENV')
        )

        # If using default repo-relative path on cloud, move to /tmp for writability
        if is_cloud_mount:
            default_repo_path = Path(_DEFAULT_DB_PATH)
            cand_path = Path(candidate)
            # If it's the default location or under /mount/src, prefer /tmp
            if (
                str(cand_path) == str(default_repo_path)
                or str(cand_path).startswith('/mount/src')
                or not os.access(
                    os.path.dirname(os.path.abspath(cand_path)) or '.', os.W_OK
                )
            ):
                tmp_dir = Path('/tmp')
                tmp_dir.mkdir(parents=True, exist_ok=True)
                target = tmp_dir / 'pybank.db'
                # Try to copy existing DB if present
                try:
                    if default_repo_path.exists() and not target.exists():
                        shutil.copy2(default_repo_path, target)
                    elif cand_path.exists() and not target.exists() and cand_path != target:
                        shutil.copy2(cand_path, target)
                except Exception:
                    pass
                return str(target)

        # Ensure directory exists for candidate
        try:
            db_dir = os.path.dirname(os.path.abspath(candidate))
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
        except Exception:
            # Fall back to /tmp
            tmp_dir = Path('/tmp')
            tmp_dir.mkdir(parents=True, exist_ok=True)
            return str(tmp_dir / 'pybank.db')

        return candidate

    def db_connect(self):
        """
        Create and return a SQLite database connection.

        Creates necessary database files and directories, initializes
        the schema with users, accounts, and transactions tables,
        and performs any required migrations.

        Returns:
            sqlite3.Connection: A configured SQLite database connection.
        """
        db_path = self._get_writable_db_path()

        # Create database connection with WAL mode for better concurrency where possible
        conn = sqlite3.connect(db_path, check_same_thread=False, timeout=30)
        conn.execute('PRAGMA busy_timeout=5000;')
        conn.execute('PRAGMA temp_store=MEMORY;')
        try:
            cur = conn.execute('PRAGMA journal_mode=WAL;')
            mode = cur.fetchone()
            if not mode or str(mode[0]).lower() != 'wal':
                raise sqlite3.OperationalError('WAL not enabled')
            conn.execute('PRAGMA synchronous=NORMAL;')
        except sqlite3.OperationalError:
            conn.execute('PRAGMA journal_mode=DELETE;')
            conn.execute('PRAGMA synchronous=FULL;')

        # Create tables if they don't exist
        conn.executescript(
            """
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

            """
        )

        # Migration: Add pin_hash column for older database files
        # Older database files were created before PIN login existed
        columns = [row[1] for row in conn.execute('PRAGMA table_info(accounts)')]
        if 'pin_hash' not in columns:
            conn.execute('ALTER TABLE accounts ADD COLUMN pin_hash TEXT')

        conn.commit()
        return conn
