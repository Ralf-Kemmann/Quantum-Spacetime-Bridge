"""Metadata-source detection and safe search over the QSB metadata catalog."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from typing import Any

from .qsb_database import QSBMetadataDatabase, quote_identifier


METADATA_KEYWORDS = {
    "metadata",
    "catalog",
    "lineage",
    "provenance",
    "source",
    "table",
    "view",
    "relation",
    "object",
    "field",
    "column",
    "alias",
    "description",
    "label",
    "quantity",
    "unit",
    "dimension",
    "conversion",
    "validation",
    "evidence",
    "status",
    "target",
    "claim",
    "rule",
    "quelle",
    "einheit",
    "dimension",
    "validierung",
    "ergebnis",
}

CONTEXT_COLUMNS = [
    "object_code",
    "canonical_name",
    "repository_path",
    "canonical_field_name",
    "field_id",
    "object_id",
    "alias_text",
    "german_alias",
    "unit_symbol",
    "unit_name",
    "quantity_kind",
    "dimension_vector",
    "validation_layer",
    "rule_name",
    "claim_text",
    "evidence_class",
    "status",
    "table_role",
    "lineage_status",
    "aussage",
    "quellobjekt",
    "zielobjekt",
    "quellfeld",
    "zielfeld",
    "groessenart",
    "pruefregel",
    "pruefebene",
]

VIEW_HINT_COLUMNS = {
    "view_name",
    "table_name",
    "relation_name",
    "object_name",
    "source_view",
    "target_view",
    "canonical_name",
}


@dataclass(frozen=True)
class MetadataSource:
    name: str
    relation_type: str
    columns: list[str]
    searchable_columns: list[str]
    reason: str


@dataclass(frozen=True)
class SearchResult:
    source: str
    matched_field: str
    matched_value: str
    relation_name: str
    table_or_view_name: str
    field_name: str
    label_or_alias: str
    unit: str
    dimension: str
    validation_status: str
    evidence_status: str
    mart_code: str
    work_package_code: str
    object_type: str
    related_view: str
    row_preview: str


def split_terms(query: str) -> list[str]:
    return [term.casefold() for term in query.split() if term.strip()]


def is_text_column(column_type: str, column_name: str) -> bool:
    ctype = column_type.upper()
    lower = column_name.casefold()
    if any(token in ctype for token in ("TEXT", "CHAR", "CLOB", "VARCHAR")):
        return True
    return any(keyword in lower for keyword in METADATA_KEYWORDS)


def detect_metadata_sources(database: QSBMetadataDatabase) -> list[MetadataSource]:
    """Detect metadata relations from object names and PRAGMA table_info columns."""
    sources: list[MetadataSource] = []
    with database.connect() as conn:
        relations = conn.execute(
            """
            SELECT type, name
            FROM sqlite_master
            WHERE type IN ('table', 'view')
              AND name NOT LIKE 'sqlite_%'
            ORDER BY type, name
            """
        ).fetchall()
        for relation in relations:
            name = relation["name"]
            info = conn.execute(f"PRAGMA table_info({quote_identifier(name)})").fetchall()
            columns = [row["name"] for row in info]
            searchable = [row["name"] for row in info if is_text_column(row["type"] or "", row["name"])]
            name_hits = sorted(keyword for keyword in METADATA_KEYWORDS if keyword in name.casefold())
            column_hits = sorted(
                {keyword for column in columns for keyword in METADATA_KEYWORDS if keyword in column.casefold()}
            )
            if name.startswith("meta_") or name.startswith("v_de_") or len(name_hits) + len(column_hits) >= 2:
                reason_bits = []
                if name.startswith("meta_"):
                    reason_bits.append("name_prefix=meta_")
                if name.startswith("v_de_"):
                    reason_bits.append("name_prefix=v_de_")
                if name_hits:
                    reason_bits.append("name_keywords=" + ",".join(name_hits))
                if column_hits:
                    reason_bits.append("column_keywords=" + ",".join(column_hits[:8]))
                sources.append(
                    MetadataSource(
                        name=name,
                        relation_type=relation["type"],
                        columns=columns,
                        searchable_columns=searchable,
                        reason="; ".join(reason_bits) or "metadata-like columns",
                    )
                )
    return sources


class MetadataSearchAdapter:
    def __init__(self, database: QSBMetadataDatabase, max_results: int = 250) -> None:
        self.database = database
        self.max_results = max_results

    def search(
        self,
        query: str,
        mart: str = "",
        work_package: str = "",
        object_type: str = "",
        evidence_class: str = "",
    ) -> list[SearchResult]:
        terms = split_terms(query)
        if not terms:
            return []
        views = set(self.database.list_views())
        results: list[SearchResult] = []
        with self.database.connect() as conn:
            for source in detect_metadata_sources(self.database):
                if not source.searchable_columns:
                    continue
                for row in self._matching_rows(conn, source, terms):
                    result = self._row_to_result(source, row, terms, views)
                    if result and self._passes_filters(result, mart, work_package, object_type, evidence_class):
                        results.append(result)
                    if len(results) >= self.max_results:
                        return results
        return results

    def _matching_rows(
        self, conn: sqlite3.Connection, source: MetadataSource, terms: list[str]
    ) -> list[sqlite3.Row]:
        quoted_columns = [quote_identifier(column) for column in source.searchable_columns]
        per_term = "(" + " OR ".join(f"LOWER(CAST({column} AS TEXT)) LIKE ?" for column in quoted_columns) + ")"
        where_sql = " AND ".join(per_term for _term in terms)
        params = [f"%{term}%" for term in terms for _column in source.searchable_columns]
        sql = f"SELECT * FROM {quote_identifier(source.name)} WHERE {where_sql} LIMIT ?"
        return conn.execute(sql, [*params, self.max_results]).fetchall()

    def _row_to_result(
        self, source: MetadataSource, row: sqlite3.Row, terms: list[str], views: set[str]
    ) -> SearchResult | None:
        row_dict = {key: row[key] for key in row.keys()}
        matched_field = ""
        matched_value = ""
        for column in source.searchable_columns:
            value = "" if row_dict.get(column) is None else str(row_dict.get(column))
            if all(term in value.casefold() or self._term_elsewhere(row_dict, source.searchable_columns, term) for term in terms):
                if any(term in value.casefold() for term in terms):
                    matched_field = column
                    matched_value = value
                    break
        if not matched_field:
            return None
        related_view = resolve_related_view(source.name, row_dict, views)
        return SearchResult(
            source=source.name,
            matched_field=matched_field,
            matched_value=matched_value,
            relation_name=first_value(row_dict, ["object_code", "canonical_name", "repository_path", "source_reference"]),
            table_or_view_name=related_view or first_value(row_dict, ["table_name", "view_name", "relation_name", "canonical_name"]),
            field_name=first_value(row_dict, ["canonical_field_name", "field_name", "column_name", "quellfeld", "zielfeld"]),
            label_or_alias=first_value(row_dict, ["alias_text", "german_alias", "english_label", "groessenart"]),
            unit=first_value(row_dict, ["unit_symbol", "unit_name", "originaleinheit", "berechnungseinheit", "anzeigeeinheit"]),
            dimension=first_value(row_dict, ["dimension_vector", "dimensionsvektor", "dimension_status", "dimensionsstatus"]),
            validation_status=first_value(row_dict, ["validation_status", "status", "link_status", "lineage_status"]),
            evidence_status=first_value(row_dict, ["evidence_class", "result_class", "comparability_status"]),
            mart_code=first_value(row_dict, ["mart_code", "mart_id"]),
            work_package_code=first_value(row_dict, ["work_package_code", "work_package_id"]),
            object_type=first_value(row_dict, ["object_type"]),
            related_view=related_view,
            row_preview=preview_row(row_dict),
        )

    @staticmethod
    def _term_elsewhere(row: dict[str, Any], columns: list[str], term: str) -> bool:
        return any(term in ("" if row.get(column) is None else str(row.get(column))).casefold() for column in columns)

    @staticmethod
    def _passes_filters(
        result: SearchResult, mart: str = "", work_package: str = "", object_type: str = "", evidence_class: str = ""
    ) -> bool:
        checks = [
            (mart, result.mart_code),
            (work_package, result.work_package_code),
            (object_type, result.object_type),
            (evidence_class, result.evidence_status),
        ]
        for expected, actual in checks:
            if expected and expected.casefold() not in actual.casefold():
                return False
        return True


def group_results_by_source(results: list[SearchResult]) -> dict[str, list[SearchResult]]:
    grouped: dict[str, list[SearchResult]] = {}
    for result in results:
        grouped.setdefault(result.source, []).append(result)
    return grouped


def first_value(row: dict[str, Any], columns: list[str]) -> str:
    for column in columns:
        value = row.get(column)
        if value is not None and str(value) != "":
            return str(value)
    return ""


def preview_row(row: dict[str, Any], limit: int = 700) -> str:
    parts = []
    for column in CONTEXT_COLUMNS:
        if column in row and row[column] is not None:
            parts.append(f"{column}={row[column]}")
    if not parts:
        parts = [f"{key}={value}" for key, value in row.items() if value is not None]
    text = "; ".join(parts)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def resolve_related_view(source_name: str, row: dict[str, Any], views: set[str]) -> str:
    if source_name in views:
        return source_name
    for column, value in row.items():
        if column.casefold() in VIEW_HINT_COLUMNS and value is not None and str(value) in views:
            return str(value)
    for value in row.values():
        if value is not None and str(value) in views:
            return str(value)
    return ""
