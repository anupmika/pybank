"""
Shared pytest fixtures for the PyBank test suite.

This module provides reusable fixtures for setting up test databases,
isolating singletons, and creating test data. All tests use temporary
databases to avoid affecting the actual application database.
"""

from __future__ import annotations

import os
import sqlite3
import tempfile
from collections.abc import Iterator

import pytest

from src.helpers.design import SingletonMeta


@pytest.fixture
def tmp_db_path() -> Iterator[str]:
    """
    Create and yield a temporary SQLite database file path.

    Automatically cleans up the database file and any WAL/SHM sidecar
    files after the test completes.

    Yields:
        str: Path to a temporary database file.
    """
    fd, path = tempfile.mkstemp(suffix='.db', prefix='pybank_test_')
    os.close(fd)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    yield path
    # Clean up database and sidecar files
    if os.path.exists(path):
        os.remove(path)
    # Also remove WAL / SHM sidecar files if any were created.
    for suffix in ('-wal', '-shm'):
        sidecar = path + suffix
        if os.path.exists(sidecar):
            os.remove(sidecar)


@pytest.fixture
def reset_singletons() -> Iterator[None]:
    """
    Clear all SingletonMeta registries before and after each test.

    Ensures each test starts from a clean slate with no cached singleton
    instances from previous tests.

    Yields:
        None: Control returns to the test after clearing registries.
    """
    # Clear before test
    for cls in list(SingletonMeta._instances.keys()):
        del SingletonMeta._instances[cls]
    yield
    # Clear after test
    for cls in list(SingletonMeta._instances.keys()):
        del SingletonMeta._instances[cls]


@pytest.fixture
def db_path(tmp_db_path: str, monkeypatch, reset_singletons) -> str:
    """
    Point the application to use the temporary test database.

    Args:
        tmp_db_path: Path to temporary database from fixture.
        monkeypatch: Pytest monkeypatch fixture.
        reset_singletons: Fixture to reset singleton instances.

    Returns:
        str: Path to the test database.
    """
    # Override database path in both sqlite_db and const modules
    monkeypatch.setattr('src.sqlite_db.DB_PATH', tmp_db_path)
    monkeypatch.setattr('src.const.DB_PATH', tmp_db_path)
    return tmp_db_path


@pytest.fixture
def db_conn(db_path: str) -> Iterator[sqlite3.Connection]:
    """
    Provide a raw SQLite connection to the test database.

    Args:
        db_path: Path to the test database.

    Yields:
        sqlite3.Connection: Active database connection.
    """
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


@pytest.fixture
def bank(db_path: str, reset_singletons):
    """
    Create a PyBank handler instance backed by the test database.

    Args:
        db_path: Path to the test database.
        reset_singletons: Fixture to reset singleton instances.

    Yields:
        PyBank: Configured PyBank handler for testing.
    """
    from src.handlers.pybank import PyBank

    bank = PyBank()
    yield bank
    bank.connect.close()


def insert_user(
    conn: sqlite3.Connection,
    *,
    aadhar_num: str = '123456789012',
    name: str = 'Alice Example',
    email: str | None = 'alice@example.com',
    phone: str = '9876543210',
    age: int = 30,
    father_name: str = 'Bob Example',
    address: str | None = '123 Main St',
    city: str = 'Metropolis',
    initial_balance: float = 1000.0,
) -> int:
    """
    Insert a user record into the database for testing.

    Args:
        conn: Active database connection.
        aadhar_num: 12-digit Aadhar number.
        name: User's full name.
        email: User's email address (optional).
        phone: User's phone number.
        age: User's age.
        father_name: Father's name.
        address: User's address (optional).
        city: User's city.
        initial_balance: Initial balance.

    Returns:
        int: ID of the inserted user.
    """
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO users
            (aadhar_num, name, email, phone, age, father_name, address, city,
             initial_balance, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """,
        (aadhar_num, name, email, phone, age, father_name, address, city,
         initial_balance),
    )
    conn.commit()
    lastrowid = cur.lastrowid
    assert lastrowid is not None
    return lastrowid


def insert_account(
    conn: sqlite3.Connection,
    *,
    user_id: int,
    account_num: int | None = None,
    account_type: str = 'savings',
    balance: float = 0.0,
    currency: str = 'INR',
    is_active: int = 1,
    pin_hash: str | None = None,
) -> int:
    """
    Insert an account record into the database for testing.

    Args:
        conn: Active database connection.
        user_id: ID of the associated user.
        account_num: Account number (auto-generated if None).
        account_type: Type of account.
        balance: Account balance.
        currency: Currency code.
        is_active: Whether account is active (1) or inactive (0).
        pin_hash: Hashed PIN (optional).

    Returns:
        int: ID of the inserted account.
    """
    if account_num is None:
        account_num = 500000 + user_id
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO accounts
            (account_num, user_id, account_type, balance, currency,
             is_active, created_at, pin_hash)
        VALUES (?, ?, ?, ?, ?, ?, datetime('now'), ?)
        """,
        (account_num, user_id, account_type, balance, currency,
         is_active, pin_hash),
    )
    conn.commit()
    lastrowid = cur.lastrowid
    assert lastrowid is not None
    return lastrowid
