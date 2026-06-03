#!/usr/bin/env python3
"""QSB-DWH07: ERD inspection package for raw/core plus dimensions.

This is a read-only documentation step over the live Research DWH and the
DWH03/DWH05/DWH06 workcopy DB. It inspects SQLite schema metadata, row counts,
declared FK structure, validation-view-governed dimension links, and report
readiness for a human DBeaver visual inspection.

It does not modify either DB, does not read raw TIM/PAR files, does not ingest
or migrate data, does not create/alter/drop DB objects, and does not compute
physical, timing, delay, model, or statistical quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh07_erd_core_dimension_visual_inspection.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh07_erd_core_dimension_visual_inspection_readout.md"
SUMMARY_JSON = "dwh07_erd_core_dimension_visual_inspection_summary.json"
NODES_CSV = "dwh07_core_dimension_erd_nodes.csv"
EDGES_CSV = "dwh07_core_dimension_erd_edges.csv"
FK_MATRIX_CSV = "dwh07_core_dimension_fk_matrix.csv"
MERMAID_MD = "dwh07_core_dimension_erd_mermaid.md"
CHECKLIST_CSV = "dwh07_visual_inspection_checklist.csv"
NEXT_STEPS_CSV = "dwh07_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    NODES_CSV,
    EDGES_CSV,
    FK_MATRIX_CSV,
    MERMAID_MD,
    CHECKLIST_CSV,
    NEXT_STEPS_CSV,
]

RAW_CORE_TABLES = [
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
]

DIMENSION_TABLES = [
    "dim_science_object",
    "dim_telescope",
    "dim_receiver",
    "dim_backend",
    "dim_time_context",
    "dim_processing_context",
    "dim_quality_status",
]

LOG_TABLES = [
    "dwh03_workcopy_run_log",
    "dwh05_migration_dry_run_log",
    "dwh06_dimension_run_log",
]

INSPECTED_TABLES = [
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    *DIMENSION_TABLES,
    *LOG_TABLES,
]

REQUIRED_VIEWS = [
    "qsb_v_dwh06_dimension_dashboard",
    "qsb_v_dwh06_observation_dimension_link_status",
    "qsb_v_dwh06_dimension_seed_rows",
    "qsb_v_dwh06_next_dimension_actions",
]

DWH05_EXPECTED_COUNTS = {
    "core_source_registry": 1,
    "core_dataset": 1,
    "core_observation": 1,
    "raw_source_file": 2,
    "raw_ingest_run": 2,
    "raw_record": 11395,
    "raw_field_value": 471874,
    "core_observation_record_link": 11395,
}

CLAIM_BOUNDARY = (
    "DWH07 is a read-only ERD and visual-inspection preparation step for the "
    "DWH06 workcopy state. It documents schema connectivity, row-count "
    "preservation, declared SQLite FKs, and validation-view-governed dimension "
    "links. It does not modify either DB, does not read raw files, does not "
    "perform model/statistical work, and does not make physical interpretation "
    "or Bridge claim statements."
)


@dataclass(frozen=True)
class NodeMeta:
    layer: str
    table_role: str
    erd_group: str
    visual_priority: str
    notes: str


NODE_META = {
    "raw_source_file": NodeMeta(
        "Raw / Entrance Layer",
        "Raw file entrance node",
        "Raw / Entrance Layer",
        "P1",
        "Raw entrance branch root with nullable core source/dataset references.",
    ),
    "raw_ingest_run": NodeMeta(
        "Raw / Entrance Layer",
        "Raw ingest run",
        "Raw / Entrance Layer",
        "P1",
        "Ingest-run node under raw_source_file.",
    ),
    "raw_record": NodeMeta(
        "Raw / Entrance Layer",
        "Raw record/line node",
        "Raw / Entrance Layer",
        "P1",
        "Raw record node shared by raw lineage and observation-record link.",
    ),
    "raw_field_value": NodeMeta(
        "Raw / Entrance Layer",
        "Raw field/token value node",
        "Raw / Entrance Layer",
        "P1",
        "Raw token/field values before semantic commitment.",
    ),
    "core_source_registry": NodeMeta(
        "Core Observation Layer",
        "Source authority/root registry",
        "Core Observation Layer",
        "P1",
        "Root source registry node for core dataset and raw source-file branches.",
    ),
    "core_dataset": NodeMeta(
        "Core Observation Layer",
        "Dataset/snapshot anchor",
        "Core Observation Layer",
        "P1",
        "Connects source registry to observation anchors.",
    ),
    "core_observation": NodeMeta(
        "Core Observation Layer",
        "Central observation anchor",
        "Core Observation Layer",
        "P1",
        "Observation-centered hub with DWH06 dimension context columns.",
    ),
    "core_observation_record_link": NodeMeta(
        "Observation-to-Raw Link",
        "Observation/raw many-to-many link",
        "Observation-to-Raw Link",
        "P1",
        "Connects the core observation branch to raw records.",
    ),
    "dim_science_object": NodeMeta(
        "Dimension Context Spokes",
        "Science-object context dimension",
        "Dimension Context Spokes",
        "P1",
        "Placeholder-governed context row linked by validation view.",
    ),
    "dim_telescope": NodeMeta(
        "Dimension Context Spokes",
        "Telescope context dimension",
        "Dimension Context Spokes",
        "P1",
        "Placeholder-governed telescope row and parent of receiver/backend rows.",
    ),
    "dim_receiver": NodeMeta(
        "Dimension Context Spokes",
        "Receiver context dimension",
        "Dimension Context Spokes",
        "P1",
        "Placeholder-governed receiver row with declared FK to dim_telescope.",
    ),
    "dim_backend": NodeMeta(
        "Dimension Context Spokes",
        "Backend context dimension",
        "Dimension Context Spokes",
        "P1",
        "Placeholder-governed backend row with declared FK to dim_telescope.",
    ),
    "dim_time_context": NodeMeta(
        "Dimension Context Spokes",
        "Time-context dimension",
        "Dimension Context Spokes",
        "P1",
        "Placeholder-governed context row; no time conversion is performed here.",
    ),
    "dim_processing_context": NodeMeta(
        "Dimension Context Spokes",
        "Processing-context dimension",
        "Dimension Context Spokes",
        "P1",
        "Placeholder-governed processing row for mapping-planning only.",
    ),
    "dim_quality_status": NodeMeta(
        "Dimension Context Spokes",
        "Quality-status dimension",
        "Dimension Context Spokes",
        "P1",
        "Placeholder-governed quality row for dry-run review state.",
    ),
    "dwh03_workcopy_run_log": NodeMeta(
        "Workcopy Logs",
        "DWH03 workcopy run metadata",
        "Workcopy Logs",
        "P3",
        "Isolated by design; documents the raw/core skeleton run.",
    ),
    "dwh05_migration_dry_run_log": NodeMeta(
        "Workcopy Logs",
        "DWH05 migration dry-run metadata",
        "Workcopy Logs",
        "P3",
        "Isolated by design; documents workcopy-only raw/core migration.",
    ),
    "dwh06_dimension_run_log": NodeMeta(
        "Workcopy Logs",
        "DWH06 dimension skeleton metadata",
        "Workcopy Logs",
        "P3",
        "Isolated by design; documents workcopy-only dimension skeleton creation.",
    ),
}

EDGE_LABELS = {
    ("core_source_registry", "source_registry_id", "core_dataset", "source_registry_id"):
        "source registry owns dataset",
    ("core_source_registry", "source_registry_id", "raw_source_file", "source_registry_id"):
        "source registry catalogs raw file",
    ("core_dataset", "dataset_id", "core_observation", "dataset_id"):
        "dataset contains observation",
    ("core_dataset", "dataset_id", "raw_source_file", "dataset_id"):
        "dataset includes raw file",
    ("raw_source_file", "raw_source_file_id", "raw_ingest_run", "raw_source_file_id"):
        "raw file has ingest run",
    ("raw_source_file", "raw_source_file_id", "raw_record", "raw_source_file_id"):
        "raw file contains raw record",
    ("raw_ingest_run", "ingest_run_id", "raw_record", "ingest_run_id"):
        "ingest run emits raw record",
    ("raw_record", "raw_record_id", "raw_field_value", "raw_record_id"):
        "raw record contains field value",
    ("core_observation", "observation_id", "core_observation_record_link", "observation_id"):
        "observation connects to raw-record link",
    ("raw_record", "raw_record_id", "core_observation_record_link", "raw_record_id"):
        "raw record connects to observation link",
    ("dim_telescope", "telescope_id", "dim_receiver", "telescope_id"):
        "telescope context owns receiver context",
    ("dim_telescope", "telescope_id", "dim_backend", "telescope_id"):
        "telescope context owns backend context",
}

RAW_CORE_EXPECTED_PARENT_CHILD = [
    ("core_source_registry", "core_dataset"),
    ("core_source_registry", "raw_source_file"),
    ("core_dataset", "core_observation"),
    ("core_dataset", "raw_source_file"),
    ("raw_source_file", "raw_ingest_run"),
    ("raw_source_file", "raw_record"),
    ("raw_ingest_run", "raw_record"),
    ("raw_record", "raw_field_value"),
    ("core_observation", "core_observation_record_link"),
    ("raw_record", "core_observation_record_link"),
]

DIMENSION_LINKS = [
    ("dim_science_object", "object_id", "core_observation", "object_id"),
    ("dim_telescope", "telescope_id", "core_observation", "telescope_id"),
    ("dim_receiver", "receiver_id", "core_observation", "receiver_id"),
    ("dim_backend", "backend_id", "core_observation", "backend_id"),
    ("dim_time_context", "time_context_id", "core_observation", "time_context_id"),
    (
        "dim_processing_context",
        "processing_context_id",
        "core_observation",
        "processing_context_id",
    ),
    ("dim_quality_status", "quality_status_id", "core_observation", "quality_status_id"),
]

DIMENSION_LINK_LABELS = {
    "object_id": "science object context",
    "telescope_id": "telescope context",
    "receiver_id": "receiver context",
    "backend_id": "backend context",
    "time_context_id": "time context",
    "processing_context_id": "processing context",
    "quality_status_id": "quality status context",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA query_only = ON")
    return con


def fetch_dicts(
    con: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql, params).fetchall()]


def object_exists(con: sqlite3.Connection, name: str, object_type: str | None = None) -> bool:
    if object_type is None:
        row = con.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE name = ?
              AND type IN ('table', 'view')
            """,
            (name,),
        ).fetchone()
    else:
        row = con.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE name = ?
              AND type = ?
            """,
            (name, object_type),
        ).fetchone()
    return row is not None


def table_info(con: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"PRAGMA table_info({quote_identifier(table)})")


def fk_list(con: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"PRAGMA foreign_key_list({quote_identifier(table)})")


def index_list(con: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"PRAGMA index_list({quote_identifier(table)})")


def index_info(con: sqlite3.Connection, index_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"PRAGMA index_info({quote_identifier(index_name)})")


def row_count(con: sqlite3.Connection, table: str) -> int:
    return int(
        con.execute(
            f"SELECT COUNT(*) AS n FROM {quote_identifier(table)}"
        ).fetchone()["n"]
    )


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_stat(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def db_state(path: Path) -> dict[str, Any]:
    return {
        "sha256": file_sha256(path),
        "stat": file_stat(path),
    }


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


def ensure_preconditions(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
) -> None:
    if not live_db.exists():
        raise FileNotFoundError(f"Live DB does not exist: {live_db}")
    if not live_db.is_file():
        raise ValueError(f"Live DB path is not a file: {live_db}")
    if not workcopy_db.exists():
        raise FileNotFoundError(f"Workcopy DB does not exist: {workcopy_db}")
    if not workcopy_db.is_file():
        raise ValueError(f"Workcopy DB path is not a file: {workcopy_db}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    existing_outputs = [
        str(path) for path in output_paths(output_root).values() if path.exists()
    ]
    if existing_outputs and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH07 output file(s): "
            + "; ".join(existing_outputs)
        )


def inspect_live_db(path: Path) -> dict[str, Any]:
    state_before = db_state(path)
    with connect_readonly(path) as con:
        result: dict[str, Any] = {
            "path": str(path),
            "integrity_check": integrity_check(con),
            "foreign_key_violations": foreign_key_violations(con),
            "state_before": state_before,
        }
    state_after = db_state(path)
    result["state_after"] = state_after
    result["modified"] = state_before != state_after
    return result


def inspect_workcopy_db(path: Path) -> dict[str, Any]:
    state_before = db_state(path)
    with connect_readonly(path) as con:
        table_exists = {
            table: object_exists(con, table, "table") for table in INSPECTED_TABLES
        }
        view_exists = {
            view: object_exists(con, view, "view") for view in REQUIRED_VIEWS
        }
        table_infos = {
            table: table_info(con, table) if table_exists[table] else []
            for table in INSPECTED_TABLES
        }
        fks = {
            table: fk_list(con, table) if table_exists[table] else []
            for table in INSPECTED_TABLES
        }
        indexes = {
            table: index_list(con, table) if table_exists[table] else []
            for table in INSPECTED_TABLES
        }
        index_columns: dict[str, dict[str, list[str]]] = {}
        for table in INSPECTED_TABLES:
            index_columns[table] = {}
            for index in indexes[table]:
                index_name = str(index["name"])
                index_columns[table][index_name] = [
                    str(row["name"]) for row in index_info(con, index_name)
                ]
        counts = {
            table: row_count(con, table) if table_exists[table] else None
            for table in INSPECTED_TABLES
        }
        view_counts: dict[str, int | None] = {}
        view_query_status: dict[str, str] = {}
        for view in REQUIRED_VIEWS:
            if not view_exists[view]:
                view_counts[view] = None
                view_query_status[view] = "missing"
                continue
            try:
                view_counts[view] = row_count(con, view)
                view_query_status[view] = "queryable"
            except sqlite3.Error as exc:
                view_counts[view] = None
                view_query_status[view] = f"query_error: {exc}"
        dashboard = (
            fetch_dicts(con, "SELECT * FROM qsb_v_dwh06_dimension_dashboard")
            if view_exists["qsb_v_dwh06_dimension_dashboard"]
            else []
        )
        link_status = (
            fetch_dicts(
                con,
                """
                SELECT *
                FROM qsb_v_dwh06_observation_dimension_link_status
                ORDER BY observation_id
                """,
            )
            if view_exists["qsb_v_dwh06_observation_dimension_link_status"]
            else []
        )
        seed_rows = (
            fetch_dicts(
                con,
                """
                SELECT *
                FROM qsb_v_dwh06_dimension_seed_rows
                ORDER BY dimension_name, dimension_id
                """,
            )
            if view_exists["qsb_v_dwh06_dimension_seed_rows"]
            else []
        )
        next_actions = (
            fetch_dicts(
                con,
                """
                SELECT *
                FROM qsb_v_dwh06_next_dimension_actions
                ORDER BY action_id
                """,
            )
            if view_exists["qsb_v_dwh06_next_dimension_actions"]
            else []
        )
        result: dict[str, Any] = {
            "path": str(path),
            "integrity_check": integrity_check(con),
            "foreign_key_violations": foreign_key_violations(con),
            "state_before": state_before,
            "table_exists": table_exists,
            "view_exists": view_exists,
            "view_counts": view_counts,
            "view_query_status": view_query_status,
            "table_info": table_infos,
            "foreign_key_list": fks,
            "index_list": indexes,
            "index_columns": index_columns,
            "row_counts": counts,
            "dwh06_dashboard": dashboard,
            "dwh06_link_status": link_status,
            "dwh06_seed_rows": seed_rows,
            "dwh06_next_actions": next_actions,
        }
    state_after = db_state(path)
    result["state_after"] = state_after
    result["modified"] = state_before != state_after
    return result


def primary_key(table_fields: list[dict[str, Any]]) -> str:
    pk_fields = [
        str(field["name"])
        for field in sorted(table_fields, key=lambda item: int(item["pk"]))
        if int(field["pk"]) > 0
    ]
    return ", ".join(pk_fields)


def notnull_fields(work: dict[str, Any], table: str) -> set[str]:
    return {
        str(field["name"])
        for field in work["table_info"].get(table, [])
        if int(field["notnull"]) == 1
    }


def build_nodes(work: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for table in INSPECTED_TABLES:
        meta = NODE_META[table]
        rows.append(
            {
                "table_name": table,
                "layer": meta.layer,
                "table_role": meta.table_role,
                "primary_key": primary_key(work["table_info"].get(table, [])),
                "row_count": work["row_counts"].get(table),
                "erd_group": meta.erd_group,
                "visual_priority": meta.visual_priority,
                "notes": meta.notes,
            }
        )
    return rows


def edge_group(source_table: str, target_table: str) -> str:
    tables = {source_table, target_table}
    if tables.issubset(set(RAW_CORE_TABLES)):
        return "Raw/Core Declared FK"
    if tables.issubset(set(DIMENSION_TABLES)):
        return "Dimension Internal Declared FK"
    if source_table in DIMENSION_TABLES and target_table == "core_observation":
        return "Dimension Context Spokes"
    return "Cross-Layer Declared FK"


def build_declared_edges(work: dict[str, Any]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for child_table in INSPECTED_TABLES:
        mandatory_fields = notnull_fields(work, child_table)
        for fk in work["foreign_key_list"].get(child_table, []):
            parent_table = str(fk["table"])
            child_field = str(fk["from"])
            parent_field = str(fk["to"])
            key = (parent_table, parent_field, child_table, child_field)
            edges.append(
                {
                    "source_table": parent_table,
                    "source_field": parent_field,
                    "target_table": child_table,
                    "target_field": child_field,
                    "relationship_label": EDGE_LABELS.get(key, "declared SQLite FK"),
                    "relationship_type": "declared_fk",
                    "mandatory": "yes" if child_field in mandatory_fields else "no",
                    "erd_group": edge_group(parent_table, child_table),
                    "enforcement_status": "enforced_sqlite_fk",
                    "notes": "Declared SQLite FK inspected from PRAGMA foreign_key_list.",
                }
            )
    return sorted(
        edges,
        key=lambda row: (
            row["erd_group"],
            row["source_table"],
            row["target_table"],
            row["source_field"],
            row["target_field"],
        ),
    )


def build_dimension_edges(work: dict[str, Any]) -> list[dict[str, str]]:
    core_notnull = notnull_fields(work, "core_observation")
    rows = []
    for source_table, source_field, target_table, target_field in DIMENSION_LINKS:
        rows.append(
            {
                "source_table": source_table,
                "source_field": source_field,
                "target_table": target_table,
                "target_field": target_field,
                "relationship_label": DIMENSION_LINK_LABELS[target_field],
                "relationship_type": "validation_view_governed_future_fk",
                "mandatory": "yes" if target_field in core_notnull else "no",
                "erd_group": "Dimension Context Spokes",
                "enforcement_status": "not_enforced_in_sqlite_yet",
                "notes": (
                    "core_observation was not rebuilt with enforced SQLite FKs in "
                    "DWH06; qsb_v_dwh06_observation_dimension_link_status governs "
                    "current link inspection."
                ),
            }
        )
    return rows


def build_edges(work: dict[str, Any]) -> list[dict[str, str]]:
    return build_declared_edges(work) + build_dimension_edges(work)


def edge_exists(
    edges: list[dict[str, str]],
    source_table: str,
    target_table: str,
    relationship_type: str | None = None,
) -> bool:
    return any(
        edge["source_table"] == source_table
        and edge["target_table"] == target_table
        and (relationship_type is None or edge["relationship_type"] == relationship_type)
        for edge in edges
    )


def dwh05_count_status(work: dict[str, Any]) -> dict[str, Any]:
    actual = {
        table: work["row_counts"].get(table) for table in DWH05_EXPECTED_COUNTS
    }
    mismatches = [
        {
            "table_name": table,
            "expected_count": expected,
            "actual_count": actual.get(table),
        }
        for table, expected in DWH05_EXPECTED_COUNTS.items()
        if actual.get(table) != expected
    ]
    return {
        "expected_counts": DWH05_EXPECTED_COUNTS,
        "actual_counts": actual,
        "mismatches": mismatches,
        "status": "passed" if not mismatches else "failed",
    }


def dwh06_dimension_status(work: dict[str, Any]) -> dict[str, Any]:
    table_counts = {
        table: work["row_counts"].get(table) for table in DIMENSION_TABLES
    }
    seed_row_count = len(work["dwh06_seed_rows"])
    dashboard = work["dwh06_dashboard"][0] if work["dwh06_dashboard"] else {}
    link_rows = work["dwh06_link_status"]
    missing_rows = [
        row for row in link_rows
        if row.get("overall_dimension_link_status") != "fully_linked"
    ]
    missing_dashboard = int(dashboard.get("missing_dimension_link_count", -1))
    fully_linked_dashboard = int(dashboard.get("fully_linked_observation_count", -1))
    status = (
        all(count == 1 for count in table_counts.values())
        and seed_row_count == 7
        and missing_dashboard == 0
        and fully_linked_dashboard == 1
        and not missing_rows
    )
    return {
        "dimension_table_counts": table_counts,
        "dimension_seed_row_count": seed_row_count,
        "dashboard": dashboard,
        "non_fully_linked_rows": missing_rows,
        "status": "passed" if status else "failed",
    }


def build_fk_matrix(
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
    work: dict[str, Any],
) -> list[dict[str, Any]]:
    declared_edges = [edge for edge in edges if edge["relationship_type"] == "declared_fk"]
    validation_edges = [
        edge for edge in edges
        if edge["relationship_type"] == "validation_view_governed_future_fk"
    ]
    declared_outgoing = Counter(edge["source_table"] for edge in declared_edges)
    declared_incoming = Counter(edge["target_table"] for edge in declared_edges)
    validation_outgoing = Counter(edge["source_table"] for edge in validation_edges)
    validation_incoming = Counter(edge["target_table"] for edge in validation_edges)
    rows = []
    for node in nodes:
        table = str(node["table_name"])
        declared_fk_count = len(work["foreign_key_list"].get(table, []))
        total_edges = (
            declared_outgoing[table]
            + declared_incoming[table]
            + validation_outgoing[table]
            + validation_incoming[table]
        )
        is_connected = total_edges > 0
        if table in LOG_TABLES:
            expected_status = "isolated_by_design"
            actual_status = "isolated_by_design" if not is_connected else "unexpectedly_connected"
            comment = "Workcopy log table is expected to stand outside the ERD edge graph."
        elif is_connected:
            expected_status = "connected"
            actual_status = "connected"
            if table in DIMENSION_TABLES:
                comment = (
                    "Connected through DWH06 dimension context spokes; declared "
                    "dimension snowflake FKs are counted where present."
                )
            elif table == "core_observation":
                comment = (
                    "Central observation hub connected by declared raw/core FKs "
                    "and validation-governed dimension spokes."
                )
            else:
                comment = "Connected through declared raw/core SQLite FK graph."
        else:
            expected_status = "connected"
            actual_status = "not_connected"
            comment = "No declared or validation-governed ERD edge found."
        inspection_status = "passed" if expected_status == actual_status else "failed"
        rows.append(
            {
                "table_name": table,
                "declared_fk_count": declared_fk_count,
                "incoming_declared_edge_count": declared_incoming[table],
                "outgoing_declared_edge_count": declared_outgoing[table],
                "validation_governed_incoming_edge_count": validation_incoming[table],
                "validation_governed_outgoing_edge_count": validation_outgoing[table],
                "is_connected": "yes" if is_connected else "no",
                "connection_comment": comment,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "inspection_status": inspection_status,
            }
        )
    return rows


def raw_core_edges_present(edges: list[dict[str, str]]) -> bool:
    return all(
        edge_exists(edges, parent, child, "declared_fk")
        for parent, child in RAW_CORE_EXPECTED_PARENT_CHILD
    )


def dimension_edges_labeled(edges: list[dict[str, str]]) -> bool:
    for source_table, _source_field, target_table, target_field in DIMENSION_LINKS:
        matches = [
            edge for edge in edges
            if edge["source_table"] == source_table
            and edge["target_table"] == target_table
            and edge["target_field"] == target_field
        ]
        if not matches:
            return False
        edge = matches[0]
        if edge["relationship_type"] != "validation_view_governed_future_fk":
            return False
        if edge["enforcement_status"] != "not_enforced_in_sqlite_yet":
            return False
    return True


def core_observation_has_dimension_declared_fks(work: dict[str, Any]) -> bool:
    dim_fields = {target_field for _s, _sf, _t, target_field in DIMENSION_LINKS}
    return any(
        str(fk["from"]) in dim_fields
        for fk in work["foreign_key_list"].get("core_observation", [])
    )


def build_checklist(
    live: dict[str, Any],
    work: dict[str, Any],
    edges: list[dict[str, str]],
    fk_matrix: list[dict[str, Any]],
    dwh05_status: dict[str, Any],
    dwh06_status: dict[str, Any],
) -> list[dict[str, str]]:
    raw_core_present = all(work["table_exists"].get(table) for table in RAW_CORE_TABLES)
    dim_present = all(work["table_exists"].get(table) for table in DIMENSION_TABLES)
    fk_clean = (
        live["integrity_check"] == "ok"
        and work["integrity_check"] == "ok"
        and not live["foreign_key_violations"]
        and not work["foreign_key_violations"]
    )
    connected_failures = [
        row["table_name"]
        for row in fk_matrix
        if row["inspection_status"] != "passed"
    ]
    visual_structure_ok = (
        raw_core_edges_present(edges)
        and dimension_edges_labeled(edges)
        and dwh06_status["status"] == "passed"
        and not connected_failures
    )
    no_dimension_sqlite_fks = not core_observation_has_dimension_declared_fks(work)

    items: list[tuple[str, str, str, str, bool, str]] = [
        (
            "DWH07_C01",
            "Are all DWH03 raw/core skeleton tables present?",
            "yes",
            f"{sum(1 for table in RAW_CORE_TABLES if work['table_exists'].get(table))}/8 present",
            raw_core_present,
            "Checked raw/core target tables only; workcopy log table is listed separately.",
        ),
        (
            "DWH07_C02",
            "Are all DWH06 dimension skeleton tables present?",
            "yes",
            f"{sum(1 for table in DIMENSION_TABLES if work['table_exists'].get(table))}/7 present",
            dim_present,
            "Checked all seven DWH06 dimension tables.",
        ),
        (
            "DWH07_C03",
            "Does core_source_registry connect to core_dataset?",
            "yes",
            "yes" if edge_exists(edges, "core_source_registry", "core_dataset", "declared_fk") else "no",
            edge_exists(edges, "core_source_registry", "core_dataset", "declared_fk"),
            "Declared FK core_dataset.source_registry_id -> core_source_registry.source_registry_id.",
        ),
        (
            "DWH07_C04",
            "Does core_dataset connect to core_observation?",
            "yes",
            "yes" if edge_exists(edges, "core_dataset", "core_observation", "declared_fk") else "no",
            edge_exists(edges, "core_dataset", "core_observation", "declared_fk"),
            "Declared FK core_observation.dataset_id -> core_dataset.dataset_id.",
        ),
        (
            "DWH07_C05",
            "Does raw_source_file connect to raw_ingest_run?",
            "yes",
            "yes" if edge_exists(edges, "raw_source_file", "raw_ingest_run", "declared_fk") else "no",
            edge_exists(edges, "raw_source_file", "raw_ingest_run", "declared_fk"),
            "Declared FK raw_ingest_run.raw_source_file_id -> raw_source_file.raw_source_file_id.",
        ),
        (
            "DWH07_C06",
            "Does raw_ingest_run connect to raw_record?",
            "yes",
            "yes" if edge_exists(edges, "raw_ingest_run", "raw_record", "declared_fk") else "no",
            edge_exists(edges, "raw_ingest_run", "raw_record", "declared_fk"),
            "Declared FK raw_record.ingest_run_id -> raw_ingest_run.ingest_run_id.",
        ),
        (
            "DWH07_C07",
            "Does raw_record connect to raw_field_value?",
            "yes",
            "yes" if edge_exists(edges, "raw_record", "raw_field_value", "declared_fk") else "no",
            edge_exists(edges, "raw_record", "raw_field_value", "declared_fk"),
            "Declared FK raw_field_value.raw_record_id -> raw_record.raw_record_id.",
        ),
        (
            "DWH07_C08",
            "Does core_observation connect to core_observation_record_link?",
            "yes",
            (
                "yes"
                if edge_exists(
                    edges,
                    "core_observation",
                    "core_observation_record_link",
                    "declared_fk",
                )
                else "no"
            ),
            edge_exists(edges, "core_observation", "core_observation_record_link", "declared_fk"),
            "Declared FK core_observation_record_link.observation_id -> core_observation.observation_id.",
        ),
        (
            "DWH07_C09",
            "Does core_observation_record_link connect to raw_record?",
            "yes",
            (
                "yes"
                if edge_exists(edges, "raw_record", "core_observation_record_link", "declared_fk")
                else "no"
            ),
            edge_exists(edges, "raw_record", "core_observation_record_link", "declared_fk"),
            "Declared FK core_observation_record_link.raw_record_id -> raw_record.raw_record_id.",
        ),
        (
            "DWH07_C10",
            "Are all seven dimension placeholder rows present?",
            "yes",
            f"seed_rows={dwh06_status['dimension_seed_row_count']}; table_counts={dwh06_status['dimension_table_counts']}",
            dwh06_status["dimension_seed_row_count"] == 7
            and all(count == 1 for count in dwh06_status["dimension_table_counts"].values()),
            "Checked DWH06 seed-row view and dimension table row counts.",
        ),
        (
            "DWH07_C11",
            "Does the DWH06 link view report no missing links?",
            "yes",
            (
                "fully_linked="
                + str(dwh06_status["dashboard"].get("fully_linked_observation_count", "missing"))
                + "; missing="
                + str(dwh06_status["dashboard"].get("missing_dimension_link_count", "missing"))
            ),
            dwh06_status["status"] == "passed",
            "qsb_v_dwh06_observation_dimension_link_status inspected read-only.",
        ),
        (
            "DWH07_C12",
            "Are DWH05 migrated raw/core row counts still present?",
            "yes",
            dwh05_status["status"],
            dwh05_status["status"] == "passed",
            "Compared current workcopy counts to DWH05 expected raw/core counts.",
        ),
        (
            "DWH07_C13",
            "Are FK checks clean?",
            "yes",
            (
                f"live_integrity={live['integrity_check']}; "
                f"live_fk={len(live['foreign_key_violations'])}; "
                f"workcopy_integrity={work['integrity_check']}; "
                f"workcopy_fk={len(work['foreign_key_violations'])}"
            ),
            fk_clean,
            "Both DBs opened read-only; PRAGMA integrity_check and foreign_key_check executed.",
        ),
        (
            "DWH07_C14",
            "Is Raw/Core + Dimension skeleton visually understandable as observation-centered star/snowflake core?",
            "yes",
            "yes" if visual_structure_ok else "no",
            visual_structure_ok,
            "Automated structure check only; DBeaver remains the requested human visual inspection surface.",
        ),
        (
            "DWH07_C15",
            "Are dimension links clearly labeled validation-view governed and not enforced SQLite FKs yet?",
            "yes",
            (
                "yes; core_observation_dimension_fk_count=0"
                if dimension_edges_labeled(edges) and no_dimension_sqlite_fks
                else "no"
            ),
            dimension_edges_labeled(edges) and no_dimension_sqlite_fks,
            "DWH06 did not rebuild core_observation with enforced SQLite FKs.",
        ),
        (
            "DWH07_C16",
            "Is workcopy suitable for DWH08 mapping/evidence skeleton planning?",
            "yes",
            "yes" if visual_structure_ok and fk_clean and dwh05_status["status"] == "passed" else "no",
            visual_structure_ok and fk_clean and dwh05_status["status"] == "passed",
            "Proceed only after human visual inspection agrees with this read-only package.",
        ),
        (
            "DWH07_C17",
            "Is workcopy suitable for future controlled core_observation FK rebuild planning?",
            "yes",
            "yes" if visual_structure_ok and no_dimension_sqlite_fks else "no",
            visual_structure_ok and no_dimension_sqlite_fks,
            "Future hard FK enforcement would require a controlled rebuild plan, not a DWH07 edit.",
        ),
    ]
    return [
        {
            "checklist_id": item[0],
            "inspection_question": item[1],
            "expected_answer": item[2],
            "actual_answer": item[3],
            "status": "passed" if item[4] else "failed",
            "notes": item[5],
        }
        for item in items
    ]


def build_next_steps(checklist: list[dict[str, str]]) -> list[dict[str, str]]:
    failed = [row for row in checklist if row["status"] != "passed"]
    current_recommendation = (
        "DWH08 Option B: Mapping/Evidence target skeleton in workcopy"
        if not failed
        else "DWH08A: adjust dimension skeleton / edge model in a new workcopy"
    )
    return [
        {
            "next_step_id": "DWH07_NEXT_01",
            "next_step_name": "DWH08 Option B",
            "prerequisite": "Human DBeaver visual inspection passes.",
            "recommended_action": (
                "Create a mapping/evidence target skeleton in the workcopy; keep "
                "raw/core and dimension claim boundaries explicit."
            ),
            "risk_level": "moderate",
            "notes": "Preferred path when the observation-centered ERD is visually acceptable.",
        },
        {
            "next_step_id": "DWH07_NEXT_02",
            "next_step_name": "DWH08 Option A",
            "prerequisite": "Visual model demands hard SQLite FK enforcement before mapping work.",
            "recommended_action": (
                "Create a fresh controlled workcopy rebuild plan with enforced "
                "dimension FKs on core_observation."
            ),
            "risk_level": "higher",
            "notes": "Do not mutate the live DB; plan table rebuild details before execution.",
        },
        {
            "next_step_id": "DWH07_NEXT_03",
            "next_step_name": "DWH08A adjustment path",
            "prerequisite": "Human visual inspection fails or automated checklist has failures.",
            "recommended_action": (
                "Adjust the dimension skeleton or edge model in a new workcopy, "
                "not the live DB."
            ),
            "risk_level": "moderate",
            "notes": "Current automated recommendation: " + current_recommendation,
        },
    ]


def build_mermaid() -> str:
    return """```mermaid
erDiagram
    %% QSB-DWH07: compact ERD for DWH03-DWH06 target tables only.
    %% Dimension spokes to core_observation are validation-view-governed future FK links.
    %% DWH06 did not rebuild core_observation with enforced SQLite FKs.

    %% Raw / Entrance Layer
    raw_source_file {
        TEXT raw_source_file_id PK
        TEXT source_registry_id FK
        TEXT dataset_id FK
    }
    raw_ingest_run {
        TEXT ingest_run_id PK
        TEXT raw_source_file_id FK
    }
    raw_record {
        TEXT raw_record_id PK
        TEXT ingest_run_id FK
        TEXT raw_source_file_id FK
    }
    raw_field_value {
        TEXT raw_field_value_id PK
        TEXT raw_record_id FK
    }

    %% Core Observation Layer
    core_source_registry {
        TEXT source_registry_id PK
    }
    core_dataset {
        TEXT dataset_id PK
        TEXT source_registry_id FK
    }
    core_observation {
        TEXT observation_id PK
        TEXT dataset_id FK
        TEXT object_id future_fk
        TEXT telescope_id future_fk
        TEXT receiver_id future_fk
        TEXT backend_id future_fk
        TEXT time_context_id future_fk
        TEXT processing_context_id future_fk
        TEXT quality_status_id future_fk
    }

    %% Observation-to-Raw Link
    core_observation_record_link {
        TEXT observation_record_link_id PK
        TEXT observation_id FK
        TEXT raw_record_id FK
    }

    %% Dimension Context Spokes
    dim_science_object {
        TEXT object_id PK
    }
    dim_telescope {
        TEXT telescope_id PK
    }
    dim_receiver {
        TEXT receiver_id PK
        TEXT telescope_id FK
    }
    dim_backend {
        TEXT backend_id PK
        TEXT telescope_id FK
    }
    dim_time_context {
        TEXT time_context_id PK
    }
    dim_processing_context {
        TEXT processing_context_id PK
    }
    dim_quality_status {
        TEXT quality_status_id PK
    }

    %% Workcopy Logs
    dwh03_workcopy_run_log {
        TEXT run_id PK
    }
    dwh05_migration_dry_run_log {
        TEXT run_id PK
    }
    dwh06_dimension_run_log {
        TEXT run_id PK
    }

    core_source_registry ||--o{ core_dataset : "source registry owns dataset"
    core_source_registry ||--o{ raw_source_file : "catalogs raw file"
    core_dataset ||--o{ core_observation : "contains observation"
    core_dataset ||--o{ raw_source_file : "includes raw file"
    raw_source_file ||--o{ raw_ingest_run : "has ingest run"
    raw_source_file ||--o{ raw_record : "contains raw record"
    raw_ingest_run ||--o{ raw_record : "emits raw record"
    raw_record ||--o{ raw_field_value : "contains field value"
    core_observation ||--o{ core_observation_record_link : "observation link"
    raw_record ||--o{ core_observation_record_link : "raw-record link"

    dim_telescope ||--o{ dim_receiver : "declared dimension FK"
    dim_telescope ||--o{ dim_backend : "declared dimension FK"

    dim_science_object ||..o{ core_observation : "object_id validation-view future FK"
    dim_telescope ||..o{ core_observation : "telescope_id validation-view future FK"
    dim_receiver ||..o{ core_observation : "receiver_id validation-view future FK"
    dim_backend ||..o{ core_observation : "backend_id validation-view future FK"
    dim_time_context ||..o{ core_observation : "time_context_id validation-view future FK"
    dim_processing_context ||..o{ core_observation : "processing_context_id validation-view future FK"
    dim_quality_status ||..o{ core_observation : "quality_status_id validation-view future FK"
```"""


def status_counts(rows: list[dict[str, str]]) -> dict[str, int]:
    counts = Counter(row["status"] for row in rows)
    return dict(sorted(counts.items()))


def build_readout(
    timestamp: str,
    live_db: Path,
    workcopy_db: Path,
    live: dict[str, Any],
    work: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
    fk_matrix: list[dict[str, Any]],
    dwh05_status: dict[str, Any],
    dwh06_status: dict[str, Any],
    checklist: list[dict[str, str]],
    next_steps: list[dict[str, str]],
) -> str:
    declared_edges = [edge for edge in edges if edge["relationship_type"] == "declared_fk"]
    raw_core_declared_edges = [
        edge for edge in declared_edges
        if {edge["source_table"], edge["target_table"]}.issubset(set(RAW_CORE_TABLES))
    ]
    validation_edges = [
        edge for edge in edges
        if edge["relationship_type"] == "validation_view_governed_future_fk"
    ]
    failed_checks = [row for row in checklist if row["status"] != "passed"]
    next_recommendation = (
        "DWH08 Option B: Mapping/Evidence target skeleton in workcopy, after human DBeaver visual inspection passes."
        if not failed_checks
        else "DWH08A: adjust dimension skeleton / edge model in a new workcopy before DWH08 planning."
    )
    dim_counts = dwh06_status["dimension_table_counts"]
    dashboard = dwh06_status["dashboard"]

    lines = [
        "# QSB-DWH07 ERD Core + Dimension Visual Inspection Readout",
        "",
        f"- Run timestamp UTC: {timestamp}",
        f"- Script: {SCRIPT_NAME}",
        f"- Operation mode: read-only documentation",
        "",
        "## 1. Executive summary",
        "",
        (
            "DWH07 inspected the DWH06 workcopy state for the raw/core DWH03 "
            "schema, DWH05 migrated raw/core counts, and DWH06 dimension skeleton. "
            "The generated package is for ERD review and DBeaver visual inspection."
        ),
        "",
        f"- ERD nodes: {len(nodes)}",
        f"- ERD edges: {len(edges)}",
        f"- Declared SQLite FK edges: {len(declared_edges)}",
        f"- Raw/core declared SQLite FK edges: {len(raw_core_declared_edges)}",
        f"- Validation-view-governed dimension future-FK edges: {len(validation_edges)}",
        f"- Checklist status counts: {status_counts(checklist)}",
        "",
        "## 2. Workcopy inspected",
        "",
        f"- Workcopy DB: `{workcopy_db}`",
        f"- Workcopy integrity_check: `{work['integrity_check']}`",
        f"- Workcopy foreign_key_check row count: {len(work['foreign_key_violations'])}",
        f"- Workcopy modified by DWH07: {work['modified']}",
        f"- Workcopy SHA before: `{work['state_before']['sha256']}`",
        f"- Workcopy SHA after: `{work['state_after']['sha256']}`",
        f"- Workcopy stat before: `{work['state_before']['stat']}`",
        f"- Workcopy stat after: `{work['state_after']['stat']}`",
        "",
        "## 3. Live DB protection result",
        "",
        f"- Live DB: `{live_db}`",
        f"- Live integrity_check: `{live['integrity_check']}`",
        f"- Live foreign_key_check row count: {len(live['foreign_key_violations'])}",
        f"- Live DB modified by DWH07: {live['modified']}",
        f"- Live SHA before: `{live['state_before']['sha256']}`",
        f"- Live SHA after: `{live['state_after']['sha256']}`",
        f"- Live stat before: `{live['state_before']['stat']}`",
        f"- Live stat after: `{live['state_after']['stat']}`",
        "",
        "## 4. DWH05 raw/core row-count preservation",
        "",
        f"- Preservation status: {dwh05_status['status']}",
        "",
        "| Table | Expected | Actual |",
        "|---|---:|---:|",
    ]
    for table, expected in DWH05_EXPECTED_COUNTS.items():
        lines.append(f"| {table} | {expected} | {dwh05_status['actual_counts'][table]} |")
    lines.extend(
        [
            "",
            "## 5. DWH06 dimension skeleton inventory",
            "",
            f"- Dimension status: {dwh06_status['status']}",
            f"- Dimension seed rows from view: {dwh06_status['dimension_seed_row_count']}",
            f"- Dashboard fully_linked_observation_count: {dashboard.get('fully_linked_observation_count')}",
            f"- Dashboard missing_dimension_link_count: {dashboard.get('missing_dimension_link_count')}",
            "",
            "| Dimension table | Row count |",
            "|---|---:|",
        ]
    )
    for table, count in dim_counts.items():
        lines.append(f"| {table} | {count} |")
    lines.extend(
        [
            "",
            "## 6. Declared FK / edge inventory",
            "",
            (
                "Declared FK edges are read from PRAGMA foreign_key_list and "
                "reported parent-to-child for visual inspection."
            ),
            "",
            "| Parent table | Parent field | Child table | Child field | Enforcement |",
            "|---|---|---|---|---|",
        ]
    )
    for edge in declared_edges:
        lines.append(
            "| {source_table} | {source_field} | {target_table} | {target_field} | "
            "{enforcement_status} |".format(**edge)
        )
    lines.extend(
        [
            "",
            "## 7. Validation-view governed dimension links",
            "",
            (
                "The dimension spokes below are intentionally not enforced as "
                "SQLite FKs on core_observation in DWH06. The DWH06 link-status "
                "view governs current inspection."
            ),
            "",
            "| Dimension table | Dimension key | Core table | Core field | Enforcement |",
            "|---|---|---|---|---|",
        ]
    )
    for edge in validation_edges:
        lines.append(
            "| {source_table} | {source_field} | {target_table} | {target_field} | "
            "{enforcement_status} |".format(**edge)
        )
    lines.extend(
        [
            "",
            "## 8. Visual ERD interpretation",
            "",
            (
                "The workcopy is readable as an observation-centered raw/core "
                "schema with raw lineage on one side, an observation-to-raw link "
                "table, and seven dimension context spokes around core_observation. "
                "Receiver and backend also retain declared dimension-snowflake "
                "links to dim_telescope."
            ),
            "",
            "## 9. DBeaver inspection instructions",
            "",
            "1. Open DBeaver.",
            "2. Create, reverse-engineer, or open a SQLite connection to the workcopy DB.",
            f"3. Workcopy DB path: `{workcopy_db}`.",
            (
                "4. Focus only these target tables: raw/core tables "
                "`core_source_registry`, `core_dataset`, `core_observation`, "
                "`core_observation_record_link`, `raw_source_file`, "
                "`raw_ingest_run`, `raw_record`, `raw_field_value`; dimension "
                "tables `dim_science_object`, `dim_telescope`, `dim_receiver`, "
                "`dim_backend`, `dim_time_context`, `dim_processing_context`, "
                "`dim_quality_status`; and logs `dwh03_workcopy_run_log`, "
                "`dwh05_migration_dry_run_log`, `dwh06_dimension_run_log`."
            ),
            "5. Hide legacy DBXX tables.",
            (
                "6. Expected patterns: raw chain, observation chain, dimension "
                "context spokes, and observation-to-raw link table."
            ),
            (
                "7. Important: DBeaver may not draw dim_* to core_observation "
                "lines as actual FK lines because DWH06 intentionally did not "
                "rebuild core_observation with enforced SQLite FKs. The validation "
                "view governs these links for now."
            ),
            "8. Do not synchronize or write schema changes from DBeaver back to the DB.",
            "",
            "## 10. Pass/fail checklist",
            "",
            "| ID | Status | Question | Actual answer |",
            "|---|---|---|---|",
        ]
    )
    for row in checklist:
        lines.append(
            f"| {row['checklist_id']} | {row['status']} | "
            f"{row['inspection_question']} | {row['actual_answer']} |"
        )
    lines.extend(
        [
            "",
            "## 11. Recommended next DWH step",
            "",
            f"- Recommended next step: {next_recommendation}",
            "",
            "| Step ID | Step name | Risk | Notes |",
            "|---|---|---|---|",
        ]
    )
    for row in next_steps:
        lines.append(
            f"| {row['next_step_id']} | {row['next_step_name']} | "
            f"{row['risk_level']} | {row['notes']} |"
        )
    lines.extend(
        [
            "",
            "## 12. What DWH07 does not do",
            "",
            "- It does not modify the live DB.",
            "- It does not modify the workcopy DB.",
            "- It does not read raw TIM/PAR files.",
            "- It does not migrate or ingest data.",
            "- It does not create, alter, or drop DB objects.",
            "- It does not compute physical, timing, delay, model, or statistical quantities.",
            "- It does not evaluate Bridge claims or physical interpretation.",
            "",
            "## 13. Claim boundary",
            "",
            CLAIM_BOUNDARY,
            "",
        ]
    )
    return "\n".join(lines)


def build_summary(
    timestamp: str,
    live_db: Path,
    workcopy_db: Path,
    live: dict[str, Any],
    work: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
    fk_matrix: list[dict[str, Any]],
    dwh05_status: dict[str, Any],
    dwh06_status: dict[str, Any],
    checklist: list[dict[str, str]],
    next_steps: list[dict[str, str]],
    output_root: Path,
) -> dict[str, Any]:
    declared_edges = [edge for edge in edges if edge["relationship_type"] == "declared_fk"]
    validation_edges = [
        edge for edge in edges
        if edge["relationship_type"] == "validation_view_governed_future_fk"
    ]
    raw_core_declared_edges = [
        edge for edge in declared_edges
        if {edge["source_table"], edge["target_table"]}.issubset(set(RAW_CORE_TABLES))
    ]
    dimension_internal_declared_edges = [
        edge for edge in declared_edges
        if {edge["source_table"], edge["target_table"]}.issubset(set(DIMENSION_TABLES))
    ]
    return {
        "script_name": SCRIPT_NAME,
        "run_timestamp_utc": timestamp,
        "operation_mode": "read_only_documentation",
        "data_substrate": {
            "live_db": str(live_db),
            "workcopy_db": str(workcopy_db),
            "output_root": str(output_root),
        },
        "live_db_protection": {
            "integrity_check": live["integrity_check"],
            "foreign_key_violation_count": len(live["foreign_key_violations"]),
            "foreign_key_violations": live["foreign_key_violations"],
            "state_before": live["state_before"],
            "state_after": live["state_after"],
            "modified_by_dwh07": live["modified"],
        },
        "workcopy_protection": {
            "integrity_check": work["integrity_check"],
            "foreign_key_violation_count": len(work["foreign_key_violations"]),
            "foreign_key_violations": work["foreign_key_violations"],
            "state_before": work["state_before"],
            "state_after": work["state_after"],
            "modified_by_dwh07": work["modified"],
        },
        "required_tables": work["table_exists"],
        "required_views": {
            view: {
                "exists": work["view_exists"][view],
                "row_count": work["view_counts"][view],
                "query_status": work["view_query_status"][view],
            }
            for view in REQUIRED_VIEWS
        },
        "dwh05_raw_core_counts": dwh05_status,
        "dwh06_dimension_status": dwh06_status,
        "erd_counts": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "declared_sqlite_fk_edge_count": len(declared_edges),
            "raw_core_declared_sqlite_fk_edge_count": len(raw_core_declared_edges),
            "dimension_internal_declared_sqlite_fk_edge_count": len(dimension_internal_declared_edges),
            "validation_view_governed_future_fk_edge_count": len(validation_edges),
        },
        "checklist_status_counts": status_counts(checklist),
        "checklist_failed_ids": [
            row["checklist_id"] for row in checklist if row["status"] != "passed"
        ],
        "next_steps": next_steps,
        "output_files": {name: str(path) for name, path in output_paths(output_root).items()},
        "inspected_schema_metadata": {
            "table_info": work["table_info"],
            "foreign_key_list": work["foreign_key_list"],
            "index_list": work["index_list"],
            "index_columns": work["index_columns"],
            "fk_matrix": fk_matrix,
        },
        "claim_boundary": CLAIM_BOUNDARY,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_outputs(
    output_root: Path,
    readout: str,
    summary: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]],
    fk_matrix: list[dict[str, Any]],
    mermaid: str,
    checklist: list[dict[str, str]],
    next_steps: list[dict[str, str]],
) -> None:
    paths = output_paths(output_root)
    paths[READOUT_MD].write_text(readout, encoding="utf-8")
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    write_csv(
        paths[NODES_CSV],
        nodes,
        [
            "table_name",
            "layer",
            "table_role",
            "primary_key",
            "row_count",
            "erd_group",
            "visual_priority",
            "notes",
        ],
    )
    write_csv(
        paths[EDGES_CSV],
        edges,
        [
            "source_table",
            "source_field",
            "target_table",
            "target_field",
            "relationship_label",
            "relationship_type",
            "mandatory",
            "erd_group",
            "enforcement_status",
            "notes",
        ],
    )
    write_csv(
        paths[FK_MATRIX_CSV],
        fk_matrix,
        [
            "table_name",
            "declared_fk_count",
            "incoming_declared_edge_count",
            "outgoing_declared_edge_count",
            "validation_governed_incoming_edge_count",
            "validation_governed_outgoing_edge_count",
            "is_connected",
            "connection_comment",
            "expected_status",
            "actual_status",
            "inspection_status",
        ],
    )
    paths[MERMAID_MD].write_text(mermaid + "\n", encoding="utf-8")
    write_csv(
        paths[CHECKLIST_CSV],
        checklist,
        [
            "checklist_id",
            "inspection_question",
            "expected_answer",
            "actual_answer",
            "status",
            "notes",
        ],
    )
    write_csv(
        paths[NEXT_STEPS_CSV],
        next_steps,
        [
            "next_step_id",
            "next_step_name",
            "prerequisite",
            "recommended_action",
            "risk_level",
            "notes",
        ],
    )


def run(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    ensure_preconditions(live_db, workcopy_db, output_root, overwrite)
    timestamp = utc_now()
    live = inspect_live_db(live_db)
    work = inspect_workcopy_db(workcopy_db)

    missing_tables = [
        table for table in [*RAW_CORE_TABLES, *DIMENSION_TABLES, "dwh05_migration_dry_run_log", "dwh06_dimension_run_log"]
        if not work["table_exists"].get(table)
    ]
    if missing_tables:
        raise RuntimeError("Missing required workcopy table(s): " + ", ".join(missing_tables))
    missing_views = [
        view for view in REQUIRED_VIEWS
        if not work["view_exists"].get(view)
        or work["view_query_status"].get(view) != "queryable"
    ]
    if missing_views:
        raise RuntimeError("Missing or non-queryable DWH06 view(s): " + ", ".join(missing_views))

    nodes = build_nodes(work)
    edges = build_edges(work)
    fk_matrix = build_fk_matrix(nodes, edges, work)
    dwh05_status = dwh05_count_status(work)
    dwh06_status = dwh06_dimension_status(work)
    checklist = build_checklist(live, work, edges, fk_matrix, dwh05_status, dwh06_status)
    next_steps = build_next_steps(checklist)
    mermaid = build_mermaid()
    readout = build_readout(
        timestamp,
        live_db,
        workcopy_db,
        live,
        work,
        nodes,
        edges,
        fk_matrix,
        dwh05_status,
        dwh06_status,
        checklist,
        next_steps,
    )
    summary = build_summary(
        timestamp,
        live_db,
        workcopy_db,
        live,
        work,
        nodes,
        edges,
        fk_matrix,
        dwh05_status,
        dwh06_status,
        checklist,
        next_steps,
        output_root,
    )
    write_outputs(
        output_root,
        readout,
        summary,
        nodes,
        edges,
        fk_matrix,
        mermaid,
        checklist,
        next_steps,
    )
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create the QSB-DWH07 read-only ERD/visual-inspection package for "
            "the DWH06 workcopy state."
        )
    )
    parser.add_argument(
        "--live-db",
        type=Path,
        default=DEFAULT_LIVE_DB,
        help="Path to the live consolidated SQLite DB; opened read-only.",
    )
    parser.add_argument(
        "--workcopy-db",
        type=Path,
        default=DEFAULT_WORKCOPY_DB,
        help="Path to the DWH03/DWH05/DWH06 workcopy SQLite DB; opened read-only.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory where DWH07 report files are written.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow controlled regeneration of DWH07 report files only.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        summary = run(
            live_db=args.live_db,
            workcopy_db=args.workcopy_db,
            output_root=args.output_root,
            overwrite=args.overwrite,
        )
    except Exception as exc:
        print(f"DWH07 failed: {exc}", file=sys.stderr)
        return 1
    erd_counts = summary["erd_counts"]
    checklist_counts = summary["checklist_status_counts"]
    print(
        "DWH07 completed: "
        f"nodes={erd_counts['node_count']}; "
        f"edges={erd_counts['edge_count']}; "
        f"checklist={checklist_counts}; "
        f"live_modified={summary['live_db_protection']['modified_by_dwh07']}; "
        f"workcopy_modified={summary['workcopy_protection']['modified_by_dwh07']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
