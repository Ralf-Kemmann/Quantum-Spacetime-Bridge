"""Data access for items."""

from __future__ import annotations

import logging
import sqlite3
from datetime import UTC, datetime

from .database import Database, DatabaseError
from .models import Item


LOGGER = logging.getLogger(__name__)


class DuplicateNameError(Exception):
    """Raised when an item name already exists."""


class ItemNotFoundError(Exception):
    """Raised when an item id does not exist."""


def utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def row_to_item(row: sqlite3.Row) -> Item:
    return Item(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        status=row["status"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


class ItemRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(self, item: Item) -> Item:
        timestamp = utc_now()
        try:
            with self.database.connect() as conn:
                cur = conn.execute(
                    """
                    INSERT INTO items(name, description, status, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (item.name, item.description, item.status, timestamp, timestamp),
                )
                item_id = int(cur.lastrowid)
            return self.get(item_id)
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise DuplicateNameError("Ein Datensatz mit diesem Namen existiert bereits.") from exc
            LOGGER.exception("Integrity error while creating item")
            raise DatabaseError("Datensatz konnte nicht angelegt werden.") from exc

    def get(self, item_id: int) -> Item:
        try:
            with self.database.connect() as conn:
                row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
            if row is None:
                raise ItemNotFoundError("Datensatz wurde nicht gefunden.")
            return row_to_item(row)
        except sqlite3.Error as exc:
            LOGGER.exception("Database error while reading item")
            raise DatabaseError("Datensatz konnte nicht gelesen werden.") from exc

    def update(self, item: Item) -> Item:
        if item.id is None:
            raise ItemNotFoundError("Datensatz wurde nicht gefunden.")
        timestamp = utc_now()
        try:
            with self.database.connect() as conn:
                cur = conn.execute(
                    """
                    UPDATE items
                    SET name = ?, description = ?, status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (item.name, item.description, item.status, timestamp, item.id),
                )
                if cur.rowcount == 0:
                    raise ItemNotFoundError("Datensatz wurde zwischenzeitlich gelöscht.")
            return self.get(item.id)
        except sqlite3.IntegrityError as exc:
            if "UNIQUE" in str(exc).upper():
                raise DuplicateNameError("Ein Datensatz mit diesem Namen existiert bereits.") from exc
            LOGGER.exception("Integrity error while updating item")
            raise DatabaseError("Datensatz konnte nicht aktualisiert werden.") from exc

    def delete(self, item_id: int) -> None:
        try:
            with self.database.connect() as conn:
                cur = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
                if cur.rowcount == 0:
                    raise ItemNotFoundError("Datensatz wurde zwischenzeitlich gelöscht.")
        except sqlite3.Error as exc:
            LOGGER.exception("Database error while deleting item")
            raise DatabaseError("Datensatz konnte nicht gelöscht werden.") from exc

    def search(self, query: str = "", status: str = "", sort_by: str = "name", descending: bool = False) -> list[Item]:
        allowed_sort = {"id", "name", "description", "status", "created_at", "updated_at"}
        if sort_by not in allowed_sort:
            sort_by = "name"
        direction = "DESC" if descending else "ASC"
        params: list[str] = []
        where: list[str] = []
        if query.strip():
            params.extend([f"%{query.strip()}%", f"%{query.strip()}%"])
            where.append("(name LIKE ? OR description LIKE ?)")
        if status.strip():
            params.append(status.strip())
            where.append("status = ?")
        where_sql = " WHERE " + " AND ".join(where) if where else ""
        sql = f"SELECT * FROM items{where_sql} ORDER BY {sort_by} {direction}"
        try:
            with self.database.connect() as conn:
                return [row_to_item(row) for row in conn.execute(sql, params).fetchall()]
        except sqlite3.Error as exc:
            LOGGER.exception("Database error while searching items")
            raise DatabaseError("Datensätze konnten nicht gelesen werden.") from exc
