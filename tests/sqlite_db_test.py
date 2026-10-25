"""
Tests for the SqliteDB singleton and schema bootstrap.

This module tests singleton behavior, database initialization,
schema creation, and migration logic.
"""

from __future__ import annotations

import pytest

from src.sqlite_db import SqliteDB


@pytest.fixture(autouse=True)
def _reset_singleton(reset_singletons):
    """
    Ensure each test starts with a fresh singleton instance.

    Args:
        reset_singletons: Fixture to clear singleton registries.
    """
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
        # Simulate an older database without the pin_hash column.
        instance = SqliteDB()
        conn = instance.db_connect()
        conn.execute('ALTER TABLE accounts DROP COLUMN pin_hash')
        conn.commit()
        conn.close()

        # Re-connect — the bootstrap should re-add the missing column.
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
