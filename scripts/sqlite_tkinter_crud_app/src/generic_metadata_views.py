"""Generic read-only metadata browser queries.

These query helpers are intentionally SELECT-only. They expose catalog content
through browser-local abstractions without creating persistent SQLite views.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GenericMetadataPage:
    name: str
    columns: list[str]
    rows: list[dict[str, Any]]
    total_count: int


MART_WORK_PACKAGE_COLUMNS = [
    "mart_code",
    "mart_name",
    "canonical_namespace",
    "scope_status",
    "work_package_code",
    "work_package_name",
    "work_package_status",
]

RESULT_TABLE_COLUMNS = [
    "mart_code",
    "mart_name",
    "result_table_id",
    "table_role",
    "object_title",
    "repository_path",
    "record_lineage_mode",
    "status",
]

RESULT_RECORD_COLUMNS = [
    "mart_code",
    "table_role",
    "source_result_key",
    "result_class",
    "comparability_status",
    "formal_validation_status",
    "physical_validation_status",
    "evidence_class",
]


def empty_page(name: str, columns: list[str]) -> GenericMetadataPage:
    return GenericMetadataPage(name=name, columns=columns, rows=[], total_count=0)
