"""SQLite connection and reproducible schema initialization."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path

from .config import SCHEMA_VERSION


LOGGER = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Raised for database setup and access errors safe for service handling."""


class Database:
    def __init__(self, path: Path) -> None:
        self.path = path

    def connect(self) -> sqlite3.Connection:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(self.path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except sqlite3.Error as exc:
            LOGGER.exception("Could not open database")
            raise DatabaseError("Datenbank konnte nicht geöffnet werden.") from exc

    def initialize(self) -> None:
        try:
            with self.connect() as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS schema_version (
                        version INTEGER NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE CHECK(length(name) <= 120),
                        description TEXT NOT NULL DEFAULT '',
                        status TEXT NOT NULL CHECK(status IN ('active', 'inactive', 'archived')),
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    );

                    CREATE INDEX IF NOT EXISTS idx_items_name ON items(name);
                    CREATE INDEX IF NOT EXISTS idx_items_description ON items(description);
                    CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
                    """
                )
                row = conn.execute("SELECT COUNT(*) AS count FROM schema_version").fetchone()
                if row["count"] == 0:
                    conn.execute("INSERT INTO schema_version(version) VALUES (?)", (SCHEMA_VERSION,))
                version = conn.execute("SELECT MAX(version) AS version FROM schema_version").fetchone()["version"]
                if version != SCHEMA_VERSION:
                    raise DatabaseError("Unerwartete Datenbankschema-Version.")
        except sqlite3.Error as exc:
            LOGGER.exception("Could not initialize database")
            raise DatabaseError("Datenbank konnte nicht initialisiert werden.") from exc
