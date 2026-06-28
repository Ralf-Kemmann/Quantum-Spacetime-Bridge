"""Read-only connector for the QSB metadata SQLite catalog."""

from __future__ import annotations

import os
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import DEFAULT_QSB_METADATA_DB, PAGE_SIZE_DEFAULT
from .generic_metadata_views import (
    MART_WORK_PACKAGE_COLUMNS,
    RESULT_RECORD_COLUMNS,
    RESULT_TABLE_COLUMNS,
    GenericMetadataPage,
    empty_page,
)
from .read_only_guard import assert_read_only_sql

class QSBDatabaseError(Exception):
    """Raised for safe-to-display QSB connector errors."""


def resolve_database_path(cli_path: str | None, environ: dict[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ
    if cli_path:
        return Path(cli_path).expanduser().resolve()
    if env.get("QSB_METADATA_DB"):
        return Path(env["QSB_METADATA_DB"]).expanduser().resolve()
    return DEFAULT_QSB_METADATA_DB


def quote_identifier(identifier: str) -> str:
    if not identifier:
        raise ValueError("Identifier must not be empty.")
    return '"' + identifier.replace('"', '""') + '"'


@dataclass(frozen=True)
class ViewPage:
    view_name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    offset: int
    limit: int
    total_count: int


class QSBMetadataDatabase:
    """Small read-only access layer around an introspected SQLite database."""

    def __init__(self, database_path: Path, immutable: bool = True, manifest: dict[str, Any] | None = None) -> None:
        self.database_path = database_path.expanduser().resolve()
        self.immutable = immutable
        self.manifest = manifest or {}
        self._views: set[str] | None = None
        self._tables: set[str] | None = None
        self._columns: dict[str, list[str]] = {}

    def connect(self) -> sqlite3.Connection:
        if not self.database_path.exists() or not self.database_path.is_file():
            raise QSBDatabaseError(f"QSB-Datenbank nicht gefunden: {self.database_path}")
        immutable_part = "&immutable=1" if self.immutable else ""
        uri = f"file:{self.database_path.as_posix()}?mode=ro{immutable_part}"
        try:
            conn = sqlite3.connect(uri, uri=True)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA query_only = ON")
            return conn
        except sqlite3.Error as exc:
            raise QSBDatabaseError("QSB-Datenbank konnte nicht im Read-only-Modus geöffnet werden.") from exc

    def list_relations(self) -> list[dict[str, str]]:
        sql = """
            SELECT type, name, tbl_name, sql
            FROM sqlite_master
            WHERE type IN ('table', 'view')
            ORDER BY type, name
        """
        with self.connect() as conn:
            return [dict(row) for row in conn.execute(sql).fetchall()]

    def list_views(self) -> list[str]:
        sql = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'view'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        with self.connect() as conn:
            views = [row["name"] for row in conn.execute(sql).fetchall()]
        self._views = set(views)
        return views

    def list_tables(self) -> list[str]:
        sql = """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """
        with self.connect() as conn:
            tables = [row["name"] for row in conn.execute(sql).fetchall()]
        self._tables = set(tables)
        return tables

    def has_table(self, table_name: str) -> bool:
        if self._tables is None:
            self.list_tables()
        return table_name in (self._tables or set())

    def has_columns(self, table_name: str, required_columns: list[str]) -> bool:
        if not self.has_table(table_name):
            return False
        columns = set(self.columns_for_relation(table_name))
        return set(required_columns).issubset(columns)

    def ensure_allowed_view(self, view_name: str) -> None:
        if self._views is None:
            self.list_views()
        if view_name not in (self._views or set()):
            raise QSBDatabaseError(f"View ist nicht in der introspektierten Allowlist: {view_name}")

    def ensure_allowed_relation(self, relation_name: str, include_tables: bool = True) -> None:
        if self._views is None:
            self.list_views()
        allowed = set(self._views or set())
        if include_tables:
            if self._tables is None:
                self.list_tables()
            allowed.update(self._tables or set())
        if relation_name not in allowed:
            raise QSBDatabaseError(f"Relation ist nicht in der introspektierten Allowlist: {relation_name}")

    def columns_for_relation(self, relation_name: str) -> list[str]:
        if relation_name not in self._columns:
            with self.connect() as conn:
                rows = conn.execute(f"PRAGMA table_info({quote_identifier(relation_name)})").fetchall()
            self._columns[relation_name] = [row["name"] for row in rows]
        return list(self._columns[relation_name])

    def load_view_page(
        self,
        view_name: str,
        offset: int = 0,
        limit: int = PAGE_SIZE_DEFAULT,
        filter_column: str | None = None,
        filter_value: str = "",
        quick_filter: str = "",
        sort_column: str | None = None,
        sort_descending: bool = False,
    ) -> ViewPage:
        return self.load_relation_page(
            view_name,
            offset=offset,
            limit=limit,
            filter_column=filter_column,
            filter_value=filter_value,
            quick_filter=quick_filter,
            sort_column=sort_column,
            sort_descending=sort_descending,
            include_tables=False,
        )

    def load_relation_page(
        self,
        relation_name: str,
        offset: int = 0,
        limit: int = PAGE_SIZE_DEFAULT,
        filter_column: str | None = None,
        filter_value: str = "",
        quick_filter: str = "",
        sort_column: str | None = None,
        sort_descending: bool = False,
        include_tables: bool = True,
    ) -> ViewPage:
        self.ensure_allowed_relation(relation_name, include_tables=include_tables)
        columns = self.columns_for_relation(relation_name)
        where_parts: list[str] = []
        params: list[Any] = []
        if filter_column and filter_value:
            if filter_column not in columns:
                raise QSBDatabaseError(f"Filterspalte ist nicht in der Relation vorhanden: {filter_column}")
            where_parts.append(f"CAST({quote_identifier(filter_column)} AS TEXT) LIKE ?")
            params.append(f"%{filter_value}%")
        if quick_filter:
            where_parts.append(
                "(" + " OR ".join(f"CAST({quote_identifier(column)} AS TEXT) LIKE ?" for column in columns) + ")"
            )
            params.extend([f"%{quick_filter}%"] * len(columns))
        where_sql = " WHERE " + " AND ".join(where_parts) if where_parts else ""
        order_sql = ""
        if sort_column:
            if sort_column not in columns:
                raise QSBDatabaseError(f"Sortierspalte ist nicht in der Relation vorhanden: {sort_column}")
            direction = "DESC" if sort_descending else "ASC"
            order_sql = f" ORDER BY {quote_identifier(sort_column)} {direction}"

        quoted_relation = quote_identifier(relation_name)
        count_sql = f"SELECT COUNT(*) AS count FROM {quoted_relation}{where_sql}"
        page_sql = f"SELECT * FROM {quoted_relation}{where_sql}{order_sql} LIMIT ? OFFSET ?"
        assert_read_only_sql(count_sql)
        assert_read_only_sql(page_sql)
        safe_offset = max(0, offset)
        safe_limit = max(1, min(limit, 500))
        with self.connect() as conn:
            total_count = int(conn.execute(count_sql, params).fetchone()["count"])
            rows = [
                {column: row[column] for column in columns}
                for row in conn.execute(page_sql, [*params, safe_limit, safe_offset]).fetchall()
            ]
        return ViewPage(relation_name, columns, rows, safe_offset, safe_limit, total_count)

    def execute_read_only(self, sql: str, params: list[Any] | tuple[Any, ...] = ()) -> list[sqlite3.Row]:
        assert_read_only_sql(sql)
        with self.connect() as conn:
            return conn.execute(sql, params).fetchall()

    def generic_mart_work_packages(self) -> GenericMetadataPage:
        if not (
            self.has_columns("meta_mart", ["mart_id", "mart_code", "canonical_namespace", "mart_name", "scope_status"])
            and self.has_columns("meta_work_package", ["mart_id", "work_package_code", "work_package_name", "status"])
        ):
            return empty_page("Marts & Work Packages", MART_WORK_PACKAGE_COLUMNS)
        sql = """
            SELECT
                m.mart_code AS mart_code,
                m.mart_name AS mart_name,
                m.canonical_namespace AS canonical_namespace,
                m.scope_status AS scope_status,
                wp.work_package_code AS work_package_code,
                wp.work_package_name AS work_package_name,
                wp.status AS work_package_status
            FROM meta_mart m
            LEFT JOIN meta_work_package wp ON wp.mart_id = m.mart_id
            ORDER BY m.mart_code, wp.work_package_code
        """
        rows = [dict(row) for row in self.execute_read_only(sql)]
        return GenericMetadataPage("Marts & Work Packages", MART_WORK_PACKAGE_COLUMNS, rows, len(rows))

    def generic_result_tables(self) -> GenericMetadataPage:
        if not (
            self.has_columns("meta_result_table", ["mart_id", "object_id", "result_table_id", "table_role", "record_lineage_mode", "status"])
            and self.has_columns("meta_mart", ["mart_id", "mart_code", "mart_name"])
            and self.has_columns("meta_object", ["object_id", "canonical_name", "repository_path"])
        ):
            return empty_page("Result Tables", RESULT_TABLE_COLUMNS)
        sql = """
            SELECT
                m.mart_code AS mart_code,
                m.mart_name AS mart_name,
                rt.result_table_id AS result_table_id,
                rt.table_role AS table_role,
                o.canonical_name AS object_title,
                o.repository_path AS repository_path,
                rt.record_lineage_mode AS record_lineage_mode,
                rt.status AS status
            FROM meta_result_table rt
            JOIN meta_mart m ON m.mart_id = rt.mart_id
            LEFT JOIN meta_object o ON o.object_id = rt.object_id
            ORDER BY m.mart_code, rt.table_role, rt.result_table_id
        """
        rows = [dict(row) for row in self.execute_read_only(sql)]
        return GenericMetadataPage("Result Tables", RESULT_TABLE_COLUMNS, rows, len(rows))

    def generic_result_records(
        self,
        mart_code: str = "",
        table_role: str = "",
        search: str = "",
        limit: int = PAGE_SIZE_DEFAULT,
    ) -> GenericMetadataPage:
        if not (
            self.has_columns("meta_result_record", RESULT_RECORD_COLUMNS[2:])
            and self.has_columns("meta_result_table", ["result_table_id", "table_role"])
            and self.has_columns("meta_mart", ["mart_id", "mart_code"])
        ):
            return empty_page("Result Records", RESULT_RECORD_COLUMNS)
        where_parts: list[str] = []
        params: list[Any] = []
        if mart_code:
            where_parts.append("m.mart_code LIKE ?")
            params.append(f"%{mart_code}%")
        if table_role:
            where_parts.append("rt.table_role LIKE ?")
            params.append(f"%{table_role}%")
        if search:
            searchable = [
                "rr.source_result_key",
                "rr.result_class",
                "rr.comparability_status",
                "rr.formal_validation_status",
                "rr.physical_validation_status",
                "rr.evidence_class",
            ]
            where_parts.append("(" + " OR ".join(f"{column} LIKE ?" for column in searchable) + ")")
            params.extend([f"%{search}%"] * len(searchable))
        where_sql = " WHERE " + " AND ".join(where_parts) if where_parts else ""
        safe_limit = max(1, min(limit, 1000))
        sql = f"""
            SELECT
                m.mart_code AS mart_code,
                rt.table_role AS table_role,
                rr.source_result_key AS source_result_key,
                rr.result_class AS result_class,
                rr.comparability_status AS comparability_status,
                rr.formal_validation_status AS formal_validation_status,
                rr.physical_validation_status AS physical_validation_status,
                rr.evidence_class AS evidence_class
            FROM meta_result_record rr
            JOIN meta_result_table rt ON rt.result_table_id = rr.result_table_id
            JOIN meta_mart m ON m.mart_id = rr.mart_id
            {where_sql}
            ORDER BY m.mart_code, rt.table_role, rr.source_result_key
            LIMIT ?
        """
        assert_read_only_sql(sql)
        with self.connect() as conn:
            rows = [dict(row) for row in conn.execute(sql, [*params, safe_limit]).fetchall()]
        return GenericMetadataPage("Result Records", RESULT_RECORD_COLUMNS, rows, len(rows))

    def quick_filter_terms(self) -> list[str]:
        page = self.generic_mart_work_packages()
        terms: list[str] = []
        for row in page.rows:
            for column in ("mart_code", "mart_name", "work_package_code", "work_package_name"):
                value = row.get(column)
                if value and str(value) not in terms:
                    terms.append(str(value))
        return terms

    def corrcore_visibility_status(self) -> dict[str, bool]:
        mart_page = self.generic_mart_work_packages()
        table_page = self.generic_result_tables()
        records = self.generic_result_records(mart_code="QSB-CORRCORE01", limit=1000)
        mart_codes = {str(row.get("mart_code", "")) for row in mart_page.rows}
        wp_codes = {str(row.get("work_package_code", "")) for row in mart_page.rows}
        roles = {str(row.get("table_role", "")) for row in table_page.rows if row.get("mart_code") == "QSB-CORRCORE01"}
        keys = {str(row.get("source_result_key", "")) for row in records.rows}
        return {
            "corrcore_mart_found": "QSB-CORRCORE01" in mart_codes,
            "corrcore_work_package_found": "QSB-CORRCORE01" in wp_codes,
            "corrcore_result_tables_found": bool({
                "source_documents",
                "central_objects",
                "equations",
                "quantities",
                "claim_boundaries",
                "cross_strand_relationships",
                "validation_results",
            }.issubset(roles)),
            "correlation_matrix_Kij_found": "correlation_matrix_Kij" in keys,
            "effective_distance_dij_found": "effective_distance_dij" in keys,
            "generic_result_record_query_has_rows": bool(records.rows),
        }

    def assert_read_only(self) -> str:
        with self.connect() as conn:
            query_only = conn.execute("PRAGMA query_only").fetchone()[0]
            database_list = [dict(row) for row in conn.execute("PRAGMA database_list").fetchall()]
        immutable_note = "immutable=1" if self.immutable else "immutable=0"
        return f"mode=ro URI, {immutable_note}, PRAGMA query_only={query_only}, databases={database_list}"
