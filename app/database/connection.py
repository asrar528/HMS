"""
Database Connection Manager for HMS Application.

Manages the SQLite connection lifecycle using the context-manager
protocol and exposes a thread-safe connection pool pattern.
"""

from __future__ import annotations

import sqlite3
import threading
from pathlib import Path
from typing import Optional


class DatabaseConnection:
    """
    Manages a single SQLite database connection for the application.

    Uses a threading lock to make connection access safe in a
    multi-threaded desktop application.
    """

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._connection: Optional[sqlite3.Connection] = None
        self._lock = threading.Lock()
        self._db_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------

    def get_connection(self) -> sqlite3.Connection:
        """Return the active connection, creating it if necessary."""
        with self._lock:
            if self._connection is None:
                self._connection = sqlite3.connect(
                    str(self._db_path),
                    check_same_thread=False,
                    detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                )
                # Enable foreign key support
                self._connection.execute("PRAGMA foreign_keys = ON")
                # Return rows as dict-like objects
                self._connection.row_factory = sqlite3.Row
        return self._connection

    def close(self) -> None:
        """Commit any pending transaction and close the connection."""
        with self._lock:
            if self._connection:
                self._connection.commit()
                self._connection.close()
                self._connection = None

    # ------------------------------------------------------------------
    # Context Manager Protocol
    # ------------------------------------------------------------------

    def __enter__(self) -> sqlite3.Connection:
        return self.get_connection()

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[override]
        if exc_type:
            self._connection and self._connection.rollback()
        else:
            self._connection and self._connection.commit()

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        conn = self.get_connection()
        return conn.execute(sql, params)

    def executemany(self, sql: str, params_seq) -> sqlite3.Cursor:
        conn = self.get_connection()
        return conn.executemany(sql, params_seq)

    def commit(self) -> None:
        if self._connection:
            self._connection.commit()

    def rollback(self) -> None:
        if self._connection:
            self._connection.rollback()
