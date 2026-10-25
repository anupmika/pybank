"""
Database management module for PyBank.
Handles SQLite database connections, schema creation, and migrations.
"""

import os
import shutil
import sqlite3
import tempfile
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

    def _get_temp_dir(self) -> Path:
        """Get a writable temp directory."""
        tmp_dir = Path(tempfile.gettempdir())
        tmp_dir.mkdir(parents=True, exist_ok=True)
        return tmp_dir

    def _get_temp_db_path(self) -> str:
        """Get path to DB in temp directory."""
        return str(self._get_temp_dir() / 'pybank.db')

    def _copy_db_if_missing(self, src: Path, dst: Path) -> None:
        """Copy database file if source exists and destination does not."""
        try:
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)
        except Exception:
            pass

    def _is_cloud_environment(self) -> bool:
        """Check if running in a cloud environment."""
        return os.path.exists('/mount/src') or bool(
            os.environ.get('STREAMLIT_SERVER_PORT')
            or os.environ.get('STREAMLIT_RUNTIME_ENV')
        )

    def _should_use_temp_in_cloud(self, default_repo_path: Path, cand_path: Path) -> bool:
        """Determine if we should use temp directory in cloud environment."""
        if str(cand_path) == str(default_repo_path):
            return True
        if str(cand_path).startswith('/mount/src'):
            return True
        db_dir = os.path.dirname(os.path.abspath(cand_path)) or '.'
        return not os.access(db_dir, os.W_OK)

    def _get_cloud_db_path(self, default_repo_path: Path, cand_path: Path) -> str:
        """Get database path for cloud environment."""
        tmp_dir = self._get_temp_dir()
        target = tmp_dir / 'pybank.db'
        self._copy_db_if_missing(default_repo_path, target)
        if cand_path != default_repo_path:
            self._copy_db_if_missing(cand_path, target)
        return str(target)

    def _get_writable_db_path(self):
        """Determine a writable database path (fallback to temp dir on cloud)."""
        candidate = DB_PATH
        default_repo_path = Path(_DEFAULT_DB_PATH)
        cand_path = Path(candidate)

        if self._is_cloud_environment() and self._should_use_temp_in_cloud(
            default_repo_path, cand_path
        ):
            return self._get_cloud_db_path(default_repo_path, cand_path)

        try:
            db_dir = os.path.dirname(os.path.abspath(candidate))
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            return candidate
        except Exception:
            return self._get_temp_db_path()

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
