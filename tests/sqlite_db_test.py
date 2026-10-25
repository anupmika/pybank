"""
Tests for the SqliteDB singleton and schema bootstrap.
"""

from __future__ import annotations

import sqlite3

import pytest

from src.sqlite_db import SqliteDB


@pytest.fixture(autouse=True)
def _reset_singleton(reset_singletons):
    """Ensure each test starts with a fresh singleton instance."""
    reset_singletons


class TestSingletonBehaviour:
    """Test suite for SqliteDB singleton pattern."""

    def test_same_instance_returned(self, db_path):
        """Test that multiple instantiations return the same instance."""
        first = SqliteDB()
        second = SqliteDB()
        assert first is second

    def test_db_connect_creates_directory_and_file(self, db_path):
        """Test that db_connect creates the database file and directory."""
        instance = SqliteDB()
        conn = instance.db_connect()
        assert conn is not None
        conn.close()

    def test_schema_tables_exist(self, db_path):
        """Test that all required tables are created."""
        instance = SqliteDB()
        conn = instance.db_connect()
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        conn.close()
        assert {'users', 'accounts', 'transactions'}.issubset(tables)

    def test_pin_hash_column_added_on_old_schema(self, db_path, monkeypatch):
        """Test migration adds pin_hash column to old database schemas."""
        instance = SqliteDB()
        conn = instance.db_connect()
        conn.execute('ALTER TABLE accounts DROP COLUMN pin_hash')
        conn.commit()
        conn.close()

        conn2 = instance.db_connect()
        columns = [row[1] for row in conn2.execute('PRAGMA table_info(accounts)')]
        conn2.close()
        assert 'pin_hash' in columns

    def test_wal_mode_is_enabled(self, db_path):
        """Test that WAL journal mode is enabled for better concurrency."""
        instance = SqliteDB()
        conn = instance.db_connect()
        mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
        conn.close()
        assert mode.lower() == 'wal'


class TestSqliteDBRobustness:
    """Tests for cloud/writable path and WAL fallback behavior."""

    def test_fallback_to_delete_when_wal_fails(self, db_path, monkeypatch):
        """Test fallback to DELETE journal mode if WAL cannot be enabled."""
        instance = SqliteDB()

        original_connect = sqlite3.connect

        class ConnWrapper:
            def __init__(self, conn):
                self._conn = conn
                self._wal_attempted = False

            def execute(self, sql, *args, **kwargs):
                sql_stripped = sql.strip().upper()
                if sql_stripped.startswith('PRAGMA JOURNAL_MODE'):
                    if not self._wal_attempted:
                        self._wal_attempted = True
                        raise sqlite3.OperationalError('disk I/O error')

                    class Result:
                        def fetchone(self_inner):
                            return ('delete',)

                    return Result()
                return self._conn.execute(sql, *args, **kwargs)

            def executescript(self, sql):
                return self._conn.executescript(sql)

            def commit(self):
                return self._conn.commit()

            def close(self):
                return self._conn.close()

            def cursor(self):
                return self._conn.cursor()

            def __getattr__(self, name):
                return getattr(self._conn, name)

        def fake_connect(*args, **kwargs):
            conn = original_connect(*args, **kwargs)
            return ConnWrapper(conn)

        monkeypatch.setattr(sqlite3, 'connect', fake_connect)
        conn = instance.db_connect()
        mode = conn.execute('PRAGMA journal_mode').fetchone()[0]
        conn.close()
        assert mode.lower() == 'delete'

    def _setup_cloud_test_env(self, tmp_path, monkeypatch, reset_singletons):
        """Helper to set up cloud test environment."""
        from src import const, sqlite_db
        from src.helpers.design import SingletonMeta

        for cls in list(SingletonMeta._instances.keys()):
            del SingletonMeta._instances[cls]

        repo_dir = tmp_path / 'repo'
        repo_dir.mkdir()
        db_dir = repo_dir / 'db'
        db_dir.mkdir()
        repo_db = db_dir / 'pybank.db'
        repo_db.write_text('')
        return repo_db, const, sqlite_db, repo_dir

    def test_cloud_path_uses_tmp_with_copied_db(self, tmp_path, monkeypatch, reset_singletons):
        """Test copying existing DB from repo to /tmp on cloud."""
        repo_db, const, sqlite_db, _ = self._setup_cloud_test_env(tmp_path, monkeypatch, reset_singletons)
        c = sqlite3.connect(str(repo_db))
        c.execute('CREATE TABLE test(x)')
        c.execute("INSERT INTO test VALUES(1)")
        c.commit()
        c.close()

        monkeypatch.setattr(const, 'DB_PATH', str(repo_db))
        monkeypatch.setattr(sqlite_db, 'DB_PATH', str(repo_db))
        monkeypatch.setattr(sqlite_db, '_DEFAULT_DB_PATH', str(repo_db))
        monkeypatch.setenv('STREAMLIT_SERVER_PORT', '8501')

        instance = SqliteDB()
        conn = instance.db_connect()
        cur = conn.execute("PRAGMA database_list")
        db_list = cur.fetchall()
        conn.close()
        assert '/tmp' in db_list[0][2] or 'tmp' in db_list[0][2].lower()

    def test_makedirs_exception_fallback(self, tmp_path, monkeypatch, reset_singletons):
        """Test fallback when makedirs fails."""
        from src import const, sqlite_db
        from src.helpers.design import SingletonMeta

        for cls in list(SingletonMeta._instances.keys()):
            del SingletonMeta._instances[cls]

        bad_path = str(tmp_path / 'bad' / 'pybank.db')
        monkeypatch.setattr(const, 'DB_PATH', bad_path)
        monkeypatch.setattr(sqlite_db, 'DB_PATH', bad_path)
        monkeypatch.setattr(sqlite_db, '_DEFAULT_DB_PATH', bad_path)
        monkeypatch.delenv('STREAMLIT_SERVER_PORT', raising=False)
        monkeypatch.delenv('STREAMLIT_RUNTIME_ENV', raising=False)

        import os as _os

        original_makedirs = _os.makedirs

        def fake_makedirs(path, *args, **kwargs):
            raise OSError('permission denied')

        monkeypatch.setattr(_os, 'makedirs', fake_makedirs)
        instance = SqliteDB()
        conn = instance.db_connect()
        cur = conn.execute('PRAGMA database_list')
        db_list = cur.fetchall()
        conn.close()
        monkeypatch.setattr(_os, 'makedirs', original_makedirs)
        assert '/tmp' in db_list[0][2] or 'tmp' in db_list[0][2]

    def test_get_temp_db_path(self, tmp_path, monkeypatch, reset_singletons):
        """Test _get_temp_db_path returns path in temp dir."""
        from src.helpers.design import SingletonMeta

        for cls in list(SingletonMeta._instances.keys()):
            del SingletonMeta._instances[cls]

        instance = SqliteDB()
        path = instance._get_temp_db_path()
        assert 'pybank.db' in path

    def test_cloud_env_and_should_use_temp(self, tmp_path, monkeypatch, reset_singletons):
        """Test cloud environment detection and temp usage logic."""
        from src import const, sqlite_db
        from src.helpers.design import SingletonMeta

        for cls in list(SingletonMeta._instances.keys()):
            del SingletonMeta._instances[cls]

        repo_dir = tmp_path / 'repo'
        repo_dir.mkdir()
        db_dir = repo_dir / 'db'
        db_dir.mkdir()
        repo_db = db_dir / 'pybank.db'
        repo_db.write_text('')

        monkeypatch.setattr(const, 'DB_PATH', str(repo_db))
        monkeypatch.setattr(sqlite_db, 'DB_PATH', str(repo_db))
        monkeypatch.setattr(sqlite_db, '_DEFAULT_DB_PATH', str(repo_db))
        monkeypatch.setenv('STREAMLIT_RUNTIME_ENV', 'cloud')

        instance = SqliteDB()
        conn = instance.db_connect()
        cur = conn.execute('PRAGMA database_list')
        db_list = cur.fetchall()
        conn.close()
        assert instance._is_cloud_environment() and ('/tmp' in db_list[0][2] or 'tmp' in db_list[0][2].lower())
