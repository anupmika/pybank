"""Shared pytest fixtures for the PyBank test suite."""
from __future__ import annotations

import os
import sqlite3
import tempfile
from collections.abc import Iterator

import pytest

from src.helpers.design import SingletonMeta
from src.sqlite_db import SqliteDB


@pytest.fixture
def tmp_db_path() -> Iterator[str]:
    """Return a path to a temporary SQLite database file."""
    fd, path = tempfile.mkstemp(suffix='.db', prefix='pybank_test_')
    os.close(fd)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    yield path
    if os.path.exists(path):
        os.remove(path)
    # Also remove WAL / SHM sidecar files if any were created.
    for suffix in ('-wal', '-shm'):
        sidecar = path + suffix
        if os.path.exists(sidecar):
            os.remove(sidecar)


@pytest.fixture
def reset_singletons() -> Iterator[None]:
    """Clear every SingletonMeta registry so tests start from a clean slate."""
    for cls in list(SingletonMeta._instances.keys()):
        del SingletonMeta._instances[cls]
    yield
    for cls in list(SingletonMeta._instances.keys()):
        del SingletonMeta._instances[cls]


@pytest.fixture
def db_path(tmp_db_path: str, monkeypatch, reset_singletons) -> str:
    """Point the app at a temporary database and return that path."""
    monkeypatch.setattr('src.sqlite_db.DB_PATH', tmp_db_path)
    monkeypatch.setattr('src.const.DB_PATH', tmp_db_path)
    return tmp_db_path


@pytest.fixture
def db_conn(db_path: str) -> Iterator[sqlite3.Connection]:
    """Return a raw SQLite connection to the test database."""
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()


@pytest.fixture
def bank(db_path: str, reset_singletons):
    """A PyBank handler backed by the temporary database."""
    from src.handlers.pybank import PyBank

    return PyBank()


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
    """Insert a user row and return its id."""
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
    """Insert an account row and return its id."""
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
