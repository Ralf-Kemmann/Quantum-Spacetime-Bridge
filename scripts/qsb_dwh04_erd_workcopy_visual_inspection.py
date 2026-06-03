#!/usr/bin/env python3
"""QSB-DWH04: ERD prep and visual inspection package for the DWH03 workcopy.

This is a read-only documentation and ERD inspection step. It opens the live
Research DWH and the DWH03 workcopy in sqlite3 read-only mode, inspects only
schema metadata and row counts for the DWH03 skeleton tables, and writes a
human-readable ERD inspection package.

It does not modify either DB, does not read raw TIM/PAR files, does not ingest
or migrate data, does not create/alter/drop DB objects, and does not compute
physical, timing, residual, delay, model, or statistical quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh04_erd_workcopy_visual_inspection.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh04_erd_workcopy_visual_inspection_readout.md"
SUMMARY_JSON = "dwh04_erd_workcopy_visual_inspection_summary.json"
NODES_CSV = "dwh04_workcopy_erd_nodes.csv"
EDGES_CSV = "dwh04_workcopy_erd_edges.csv"
FK_MATRIX_CSV = "dwh04_workcopy_fk_matrix.csv"
MERMAID_MD = "dwh04_workcopy_erd_mermaid.md"
CHECKLIST_CSV = "dwh04_visual_inspection_checklist.csv"
NEXT_STEPS_CSV = "dwh04_next_dwh_steps.csv"

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

DWH03_TABLES = [
    "dwh03_workcopy_run_log",
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
]

SKELETON_TABLES = [
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
]

EXPECTED_INDEXES = {
    "core_dataset": {"source_registry_id"},
    "core_observation": {"dataset_id"},
    "raw_source_file": {"source_registry_id", "dataset_id"},
    "raw_ingest_run": {"raw_source_file_id"},
    "raw_record": {"ingest_run_id", "raw_source_file_id"},
    "raw_field_value": {"raw_record_id", "token_position"},
    "core_observation_record_link": {"observation_id", "raw_record_id"},
}

DIMENSION_PLACEHOLDERS = {
    "object_id",
    "telescope_id",
    "receiver_id",
    "backend_id",
    "time_context_id",
    "processing_context_id",
    "quality_status_id",
}

CLAIM_BOUNDARY = (
    "DWH04 is a read-only ERD/visual inspection preparation step over the live "
    "DB and DWH03 workcopy DB. It inspects schema metadata, FK/index structure, "
    "and empty-skeleton row counts only. It does not modify either DB, does not "
    "migrate data, does not test a Bridge relation, and does not make physical "
    "interpretation claims."
)


@dataclass(frozen=True)
class NodeMeta:
    layer: str
    table_role: str
    erd_group: str
    visual_priority: str
    notes: str


NODE_META = {
    "dwh03_workcopy_run_log": NodeMeta(
        "Governance Workcopy Log",
        "DWH03 workcopy run metadata",
        "Governance Workcopy Log",
        "P3",
        "Isolated by design; documents the workcopy skeleton run.",
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
        "Observation-centered chassis node; dimension columns remain placeholders.",
    ),
    "core_observation_record_link": NodeMeta(
        "Observation-to-Raw Link",
        "Observation/raw many-to-many link",
        "Observation-to-Raw Link",
        "P1",
        "Connects the core observation branch to raw records.",
    ),
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
}

EDGE_LABELS = {
    ("core_dataset", "source_registry_id", "core_source_registry", "source_registry_id"): "source registry owns dataset",
    ("core_observation", "dataset_id", "core_dataset", "dataset_id"): "dataset contains observation",
    ("core_observation_record_link", "observation_id", "core_observation", "observation_id"): "link references observation",
    ("core_observation_record_link", "raw_record_id", "raw_record", "raw_record_id"): "link references raw record",
    ("raw_source_file", "source_registry_id", "core_source_registry", "source_registry_id"): "source registry catalogs raw file",
    ("raw_source_file", "dataset_id", "core_dataset", "dataset_id"): "dataset includes raw file",
    ("raw_ingest_run", "raw_source_file_id", "raw_source_file", "raw_source_file_id"): "raw file has ingest run",
    ("raw_record", "ingest_run_id", "raw_ingest_run", "ingest_run_id"): "ingest run emits raw record",
    ("raw_record", "raw_source_file_id", "raw_source_file", "raw_source_file_id"): "raw file contains raw record",
    ("raw_field_value", "raw_record_id", "raw_record", "raw_record_id"): "raw record contains field value",
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
    return con


def fetch_dicts(
    con: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql, params).fetchall()]


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


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


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
        raise FileNotFoundError(f"DWH03 workcopy DB does not exist: {workcopy_db}")
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
            "Refusing to overwrite existing DWH04 output file(s): "
            + "; ".join(existing_outputs)
        )


def inspect_db(path: Path, dwh03_tables: bool = False) -> dict[str, Any]:
    sha_before = file_sha256(path)
    stat_before = file_stat(path)
    with connect_readonly(path) as con:
        result: dict[str, Any] = {
            "integrity": integrity_check(con),
            "foreign_key_violations": foreign_key_violations(con),
            "sha256_before": sha_before,
            "stat_before": stat_before,
        }
        if dwh03_tables:
            table_exists = {table: object_exists(con, table, "table") for table in DWH03_TABLES}
            infos = {table: table_info(con, table) if table_exists[table] else [] for table in DWH03_TABLES}
            fks = {table: fk_list(con, table) if table_exists[table] else [] for table in DWH03_TABLES}
            indexes = {table: index_list(con, table) if table_exists[table] else [] for table in DWH03_TABLES}
            index_columns: dict[str, dict[str, list[str]]] = {}
            for table in DWH03_TABLES:
                index_columns[table] = {}
                for index in indexes[table]:
                    name = str(index["name"])
                    index_columns[table][name] = [
                        str(row["name"]) for row in index_info(con, name)
                    ]
            counts = {
                table: row_count(con, table) if table_exists[table] else None
                for table in DWH03_TABLES
            }
            result.update(
                {
                    "table_exists": table_exists,
                    "table_info": infos,
                    "fks": fks,
                    "indexes": indexes,
                    "index_columns": index_columns,
                    "row_counts": counts,
                }
            )
    result["sha256_after"] = file_sha256(path)
    result["stat_after"] = file_stat(path)
    result["modified"] = (
        result["sha256_before"] != result["sha256_after"]
        or result["stat_before"]["size_bytes"] != result["stat_after"]["size_bytes"]
    )
    return result


def primary_key(table_fields: list[dict[str, Any]]) -> str:
    pk_fields = [
        str(field["name"])
        for field in sorted(table_fields, key=lambda item: int(item["pk"]))
        if int(field["pk"]) > 0
    ]
    return ", ".join(pk_fields)


def build_nodes(work: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for table in DWH03_TABLES:
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


def notnull_fields(work: dict[str, Any], table: str) -> set[str]:
    return {
        str(field["name"])
        for field in work["table_info"].get(table, [])
        if int(field["notnull"]) == 1
    }


def build_edges(work: dict[str, Any]) -> list[dict[str, Any]]:
    edges = []
    for table in DWH03_TABLES:
        mandatory_fields = notnull_fields(work, table)
        for fk in work["fks"].get(table, []):
            source_field = str(fk["from"])
            target_table = str(fk["table"])
            target_field = str(fk["to"])
            key = (table, source_field, target_table, target_field)
            edges.append(
                {
                    "source_table": table,
                    "source_field": source_field,
                    "target_table": target_table,
                    "target_field": target_field,
                    "relationship_label": EDGE_LABELS.get(key, "declared FK relationship"),
                    "relationship_type": "many_to_one",
                    "mandatory": "yes" if source_field in mandatory_fields else "no",
                    "erd_group": NODE_META.get(table, NODE_META[target_table]).erd_group,
                    "notes": "Declared SQLite FK inspected from PRAGMA foreign_key_list.",
                }
            )
    return sorted(
        edges,
        key=lambda row: (row["source_table"], row["source_field"], row["target_table"]),
    )


def build_fk_matrix(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    outgoing = Counter(edge["source_table"] for edge in edges)
    incoming = Counter(edge["target_table"] for edge in edges)
    rows = []
    for node in nodes:
        table = node["table_name"]
        out_count = outgoing[table]
        in_count = incoming[table]
        is_connected = out_count + in_count > 0
        if table == "dwh03_workcopy_run_log":
            expected_status = "isolated_by_design"
            actual_status = "isolated_by_design" if not is_connected else "unexpectedly_connected"
            inspection_status = "passed" if actual_status == expected_status else "failed"
            comment = "Governance run log is expected to stand outside the raw/core ERD slice."
        else:
            expected_status = "connected"
            actual_status = "connected" if is_connected else "not_connected"
            inspection_status = "passed" if actual_status == expected_status else "failed"
            comment = "Connected through declared FK graph." if is_connected else "No declared FK edge found."
        rows.append(
            {
                "table_name": table,
                "fk_count": out_count,
                "incoming_edge_count": in_count,
                "outgoing_edge_count": out_count,
                "is_connected": "yes" if is_connected else "no",
                "connection_comment": comment,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "inspection_status": inspection_status,
            }
        )
    return rows


def edge_exists(edges: list[dict[str, Any]], source: str, target: str) -> bool:
    return any(edge["source_table"] == source and edge["target_table"] == target for edge in edges)


def indexed_columns(work: dict[str, Any], table: str) -> set[str]:
    columns: set[str] = set()
    for name, index_cols in work["index_columns"].get(table, {}).items():
        if name.startswith("idx_dwh03_"):
            columns.update(index_cols)
    return columns


def index_check(work: dict[str, Any]) -> tuple[bool, str]:
    missing = []
    for table, expected_columns in EXPECTED_INDEXES.items():
        present = indexed_columns(work, table)
        for column in expected_columns:
            if column not in present:
                missing.append(f"{table}.{column}")
    if missing:
        return False, "Missing DWH03 indexes for: " + ", ".join(missing)
    return True, "All expected DWH03 FK/lookup indexes are present."


def dimension_placeholder_check(work: dict[str, Any]) -> tuple[bool, str]:
    observation_fields = {
        str(field["name"])
        for field in work["table_info"].get("core_observation", [])
    }
    present_placeholders = sorted(DIMENSION_PLACEHOLDERS.intersection(observation_fields))
    fk_sources = {
        str(fk["from"])
        for fk in work["fks"].get("core_observation", [])
    }
    enforced_placeholders = sorted(DIMENSION_PLACEHOLDERS.intersection(fk_sources))
    ok = bool(present_placeholders) and not enforced_placeholders
    if ok:
        return True, "Dimension placeholders are present as TEXT columns and not enforced as FKs."
    return False, f"Unexpected placeholder FK state: {enforced_placeholders}"


def skeleton_empty_check(work: dict[str, Any]) -> tuple[bool, str]:
    expected = {"dwh03_workcopy_run_log": 1}
    expected.update({table: 0 for table in SKELETON_TABLES})
    mismatches = [
        f"{table}={work['row_counts'].get(table)} expected {count}"
        for table, count in expected.items()
        if work["row_counts"].get(table) != count
    ]
    if mismatches:
        return False, "; ".join(mismatches)
    return True, "Skeleton tables are empty except dwh03_workcopy_run_log = 1."


def build_checklist(
    live: dict[str, Any],
    work: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    fk_matrix: list[dict[str, Any]],
) -> list[dict[str, str]]:
    index_ok, index_answer = index_check(work)
    placeholders_ok, placeholders_answer = dimension_placeholder_check(work)
    empty_ok, empty_answer = skeleton_empty_check(work)
    all_tables_present = all(work["table_exists"].get(table) for table in DWH03_TABLES)
    fk_clean = not live["foreign_key_violations"] and not work["foreign_key_violations"]
    connected_failures = [
        row["table_name"]
        for row in fk_matrix
        if row["inspection_status"] != "passed"
    ]
    visually_understandable = (
        not connected_failures
        and edge_exists(edges, "core_dataset", "core_source_registry")
        and edge_exists(edges, "core_observation", "core_dataset")
        and edge_exists(edges, "core_observation_record_link", "core_observation")
        and edge_exists(edges, "core_observation_record_link", "raw_record")
    )

    items = [
        ("DWH04_C01", "Does core_source_registry connect to core_dataset?", "yes", "yes" if edge_exists(edges, "core_dataset", "core_source_registry") else "no", edge_exists(edges, "core_dataset", "core_source_registry"), "Declared FK core_dataset.source_registry_id -> core_source_registry.source_registry_id."),
        ("DWH04_C02", "Does core_dataset connect to core_observation?", "yes", "yes" if edge_exists(edges, "core_observation", "core_dataset") else "no", edge_exists(edges, "core_observation", "core_dataset"), "Declared FK core_observation.dataset_id -> core_dataset.dataset_id."),
        ("DWH04_C03", "Does core_observation connect to core_observation_record_link?", "yes", "yes" if edge_exists(edges, "core_observation_record_link", "core_observation") else "no", edge_exists(edges, "core_observation_record_link", "core_observation"), "Declared FK core_observation_record_link.observation_id -> core_observation.observation_id."),
        ("DWH04_C04", "Does raw_source_file connect to raw_ingest_run?", "yes", "yes" if edge_exists(edges, "raw_ingest_run", "raw_source_file") else "no", edge_exists(edges, "raw_ingest_run", "raw_source_file"), "Declared FK raw_ingest_run.raw_source_file_id -> raw_source_file.raw_source_file_id."),
        ("DWH04_C05", "Does raw_ingest_run connect to raw_record?", "yes", "yes" if edge_exists(edges, "raw_record", "raw_ingest_run") else "no", edge_exists(edges, "raw_record", "raw_ingest_run"), "Declared FK raw_record.ingest_run_id -> raw_ingest_run.ingest_run_id."),
        ("DWH04_C06", "Does raw_record connect to raw_field_value?", "yes", "yes" if edge_exists(edges, "raw_field_value", "raw_record") else "no", edge_exists(edges, "raw_field_value", "raw_record"), "Declared FK raw_field_value.raw_record_id -> raw_record.raw_record_id."),
        ("DWH04_C07", "Does core_observation_record_link connect observations to raw_record?", "yes", "yes" if edge_exists(edges, "core_observation_record_link", "core_observation") and edge_exists(edges, "core_observation_record_link", "raw_record") else "no", edge_exists(edges, "core_observation_record_link", "core_observation") and edge_exists(edges, "core_observation_record_link", "raw_record"), "Bridge/link table has declared FKs to both sides."),
        ("DWH04_C08", "Are all DWH03 raw/core skeleton tables present?", "yes", "yes" if all_tables_present else "no", all_tables_present, "Nine DWH03 tables checked."),
        ("DWH04_C09", "Are skeleton tables empty except dwh03_workcopy_run_log?", "yes", empty_answer, empty_ok, "No legacy data should be migrated in DWH04."),
        ("DWH04_C10", "Are FK checks clean?", "yes", f"live={len(live['foreign_key_violations'])}; workcopy={len(work['foreign_key_violations'])}", fk_clean, "Both DBs inspected read-only."),
        ("DWH04_C11", "Are indexes present for FK columns?", "yes", index_answer, index_ok, "Expected DWH03 FK/lookup indexes checked by PRAGMA index_list/index_info."),
        ("DWH04_C12", "Is the Raw/Core skeleton visually understandable as a first DWH chassis?", "yes", "yes" if visually_understandable else "no", visually_understandable, "Core and raw branches are connected through core_observation_record_link."),
        ("DWH04_C13", "Are dimension placeholders clearly not yet enforced as FKs?", "yes", placeholders_answer, placeholders_ok, "core_observation placeholder columns are future FKs only."),
        ("DWH04_C14", "Is the workcopy suitable for visual inspection in DbSchema?", "yes", "yes" if visually_understandable and fk_clean else "no", visually_understandable and fk_clean, "Use the DWH03 workcopy and hide legacy table forest."),
        ("DWH04_C15", "Is the workcopy suitable for DWH05 dry-run migration planning?", "yes", "yes" if visually_understandable and fk_clean and index_ok else "no", visually_understandable and fk_clean and index_ok, "Proceed to planning only; no live DB migration implied."),
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
    if failed:
        recommendation = "DWH05A: adjust raw/core skeleton DDL in a new workcopy, not the live DB."
        status = "use_if_visual_inspection_fails"
    else:
        recommendation = "DWH05 Option B: raw/core migration dry-run into workcopy with row-count parity."
        status = "recommended_if_human_visual_inspection_passes"
    return [
        {
            "step_id": "DWH04_NEXT_01",
            "condition": "If visual inspection passes",
            "recommended_step": "DWH05 Option B: raw/core migration dry-run into workcopy with row-count parity.",
            "target_db": str(DEFAULT_WORKCOPY_DB),
            "blocking_status": "ready_for_planning" if not failed else "wait_for_failed_check_resolution",
            "notes": "Dry-run should remain workcopy-only and include row-count parity checks.",
        },
        {
            "step_id": "DWH04_NEXT_02",
            "condition": "If visual inspection fails",
            "recommended_step": "DWH05A: adjust raw/core skeleton DDL in a new workcopy, not the live DB.",
            "target_db": "new controlled workcopy",
            "blocking_status": "fallback_path",
            "notes": "Do not alter the live DB or mutate this inspection package.",
        },
        {
            "step_id": "DWH04_NEXT_03",
            "condition": "Current automated checklist result",
            "recommended_step": recommendation,
            "target_db": str(DEFAULT_WORKCOPY_DB),
            "blocking_status": status,
            "notes": "Human DbSchema inspection remains the visual confirmation step.",
        },
    ]


def render_mermaid() -> str:
    return """# DWH04 Workcopy Raw/Core Mermaid ERD

This Mermaid diagram includes only the DWH03 skeleton tables. It intentionally excludes the legacy DBXX table forest.

## Raw / Entrance Layer

```mermaid
erDiagram
    core_source_registry ||--o{ core_dataset : owns
    core_dataset ||--o{ core_observation : contains
    core_observation ||--o{ core_observation_record_link : links
    raw_record ||--o{ core_observation_record_link : linked_by
    core_source_registry ||--o{ raw_source_file : catalogs
    core_dataset ||--o{ raw_source_file : includes
    raw_source_file ||--o{ raw_ingest_run : ingested_by
    raw_ingest_run ||--o{ raw_record : emits
    raw_source_file ||--o{ raw_record : contains
    raw_record ||--o{ raw_field_value : contains

    core_source_registry {
        TEXT source_registry_id PK
        TEXT source_name
        TEXT source_type
        TEXT retrieval_status
        TEXT source_status
    }
    core_dataset {
        TEXT dataset_id PK
        TEXT source_registry_id FK
        TEXT dataset_name
        TEXT dataset_status
    }
    core_observation {
        TEXT observation_id PK
        TEXT dataset_id FK
        TEXT object_id
        TEXT telescope_id
        TEXT receiver_id
        TEXT backend_id
        TEXT time_context_id
        TEXT processing_context_id
        TEXT quality_status_id
        TEXT observation_status
    }
    core_observation_record_link {
        TEXT observation_record_link_id PK
        TEXT observation_id FK
        TEXT raw_record_id FK
        TEXT link_status
    }
    raw_source_file {
        TEXT raw_source_file_id PK
        TEXT source_registry_id FK
        TEXT dataset_id FK
        TEXT source_filename
        TEXT ingest_status
    }
    raw_ingest_run {
        TEXT ingest_run_id PK
        TEXT raw_source_file_id FK
        TEXT run_timestamp_utc
        TEXT ingest_mode
        TEXT status
    }
    raw_record {
        TEXT raw_record_id PK
        TEXT ingest_run_id FK
        TEXT raw_source_file_id FK
        INTEGER record_index
        TEXT record_status
    }
    raw_field_value {
        TEXT raw_field_value_id PK
        TEXT raw_record_id FK
        TEXT token_position
        TEXT field_name
        TEXT field_status
    }
    dwh03_workcopy_run_log {
        TEXT run_id PK
        TEXT run_timestamp_utc
        TEXT operation_mode
    }
```

## Core Observation Layer

Expected visual chain:
`core_source_registry -> core_dataset -> core_observation -> core_observation_record_link`

## Observation-to-Raw Link

Expected link:
`core_observation_record_link -> raw_record`

## Governance Workcopy Log

`dwh03_workcopy_run_log` is intentionally isolated from the raw/core ERD graph.
"""


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "/") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def render_readout(
    live_db: Path,
    workcopy_db: Path,
    live: dict[str, Any],
    work: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    fk_matrix: list[dict[str, Any]],
    checklist: list[dict[str, str]],
) -> str:
    passed = sum(1 for row in checklist if row["status"] == "passed")
    failed = sum(1 for row in checklist if row["status"] != "passed")
    index_rows = []
    for table in DWH03_TABLES:
        for index in work["indexes"].get(table, []):
            name = str(index["name"])
            if name.startswith("idx_dwh03_"):
                index_rows.append(
                    {
                        "table": table,
                        "index": name,
                        "columns": ", ".join(work["index_columns"][table].get(name, [])),
                    }
                )
    lines = [
        "# QSB-DWH04 ERD Workcopy Visual Inspection Readout",
        "",
        f"Generated at UTC: {utc_now()}",
        f"Script: `{SCRIPT_NAME}`",
        f"Live DB: `{live_db}`",
        f"Workcopy DB: `{workcopy_db}`",
        "",
        "## 1. Executive summary",
        "",
        (
            "DWH04 inspected the DWH03 workcopy raw/core skeleton in read-only "
            "mode and produced an ERD package for human visual inspection. The "
            "raw/core skeleton is connected through declared SQLite FKs, with "
            "the DWH03 run log intentionally isolated."
        ),
        "",
        f"Automated checklist: {passed} passed, {failed} failed.",
        "",
        "## 2. Workcopy inspected",
        "",
        f"Workcopy integrity_check: `{work['integrity']}`",
        f"Workcopy foreign_key_check count: `{len(work['foreign_key_violations'])}`",
        f"Workcopy modified by DWH04: `{str(work['modified']).lower()}`",
        "",
        "## 3. Live DB protection result",
        "",
        f"Live integrity_check: `{live['integrity']}`",
        f"Live foreign_key_check count: `{len(live['foreign_key_violations'])}`",
        f"Live DB modified by DWH04: `{str(live['modified']).lower()}`",
        f"Live checksum before: `{live['sha256_before']}`",
        f"Live checksum after: `{live['sha256_after']}`",
        "",
        "## 4. DWH03 skeleton table inventory",
        "",
        markdown_table(nodes, ["table_name", "layer", "primary_key", "row_count", "visual_priority"]),
        "",
        "## 5. FK / edge inventory",
        "",
        markdown_table(edges, ["source_table", "source_field", "target_table", "target_field", "mandatory", "relationship_label"]),
        "",
        "## 6. Index inventory",
        "",
        markdown_table(index_rows, ["table", "index", "columns"]),
        "",
        "## 7. Visual ERD interpretation",
        "",
        (
            "The first-viewport ERD slice should show two readable branches: "
            "`core_source_registry -> core_dataset -> core_observation` and "
            "`raw_source_file -> raw_ingest_run -> raw_record -> raw_field_value`. "
            "`core_observation_record_link` joins the observation branch to "
            "`raw_record`, making the raw/core chassis visually coherent for "
            "the next workcopy-only planning step."
        ),
        "",
        "## 8. DbSchema inspection instructions",
        "",
        "1. Open DbSchema.",
        f"2. Create/reverse-engineer a project from `{workcopy_db}`.",
        "3. Focus on these tables only: `core_source_registry`, `core_dataset`, `core_observation`, `core_observation_record_link`, `raw_source_file`, `raw_ingest_run`, `raw_record`, `raw_field_value`, `dwh03_workcopy_run_log`.",
        "4. Hide legacy DBXX tables for the first ERD slice if possible.",
        "5. Expected visual pattern: `core_source_registry -> core_dataset -> core_observation -> core_observation_record_link -> raw_record -> raw_field_value` and `raw_source_file -> raw_ingest_run -> raw_record -> raw_field_value`.",
        "6. Export PNG/SVG/PDF if available.",
        "7. Do not synchronize/write schema changes from DbSchema back to the DB.",
        "",
        "## 9. Pass/fail checklist",
        "",
        markdown_table(checklist, ["checklist_id", "inspection_question", "actual_answer", "status"]),
        "",
        "## 10. Recommended next DWH step",
        "",
        (
            "If human visual inspection passes: DWH05 Option B, raw/core "
            "migration dry-run into workcopy with row-count parity. If visual "
            "inspection fails: DWH05A, adjust raw/core skeleton DDL in a new "
            "workcopy, not the live DB."
        ),
        "",
        "## 11. What DWH04 does not do",
        "",
        "- It does not modify the live DB.",
        "- It does not modify the DWH03 workcopy DB.",
        "- It does not ingest or migrate data.",
        "- It does not create, alter, or drop DB tables/views.",
        "- It does not inspect the full legacy DBXX table forest for this ERD slice.",
        "",
        "## 12. Claim boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ]
    return "\n".join(lines)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_outputs(
    output_root: Path,
    live_db: Path,
    workcopy_db: Path,
    live: dict[str, Any],
    work: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    fk_matrix: list[dict[str, Any]],
    checklist: list[dict[str, str]],
    next_steps: list[dict[str, str]],
) -> None:
    paths = output_paths(output_root)
    summary = {
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "live_db_modified": live["modified"],
        "workcopy_db_modified": work["modified"],
        "live_integrity_check": live["integrity"],
        "live_foreign_key_violation_count": len(live["foreign_key_violations"]),
        "workcopy_integrity_check": work["integrity"],
        "workcopy_foreign_key_violation_count": len(work["foreign_key_violations"]),
        "dwh03_tables_inspected": DWH03_TABLES,
        "erd_node_count": len(nodes),
        "erd_edge_count": len(edges),
        "checklist_passed_count": sum(1 for row in checklist if row["status"] == "passed"),
        "checklist_failed_count": sum(1 for row in checklist if row["status"] != "passed"),
        "mermaid_output_path": str(paths[MERMAID_MD]),
        "recommended_next_dwh_step": next_steps[2]["recommended_step"],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    paths[READOUT_MD].write_text(
        render_readout(live_db, workcopy_db, live, work, nodes, edges, fk_matrix, checklist),
        encoding="utf-8",
    )
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    write_csv(
        paths[NODES_CSV],
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
        nodes,
    )
    write_csv(
        paths[EDGES_CSV],
        [
            "source_table",
            "source_field",
            "target_table",
            "target_field",
            "relationship_label",
            "relationship_type",
            "mandatory",
            "erd_group",
            "notes",
        ],
        edges,
    )
    write_csv(
        paths[FK_MATRIX_CSV],
        [
            "table_name",
            "fk_count",
            "incoming_edge_count",
            "outgoing_edge_count",
            "is_connected",
            "connection_comment",
            "expected_status",
            "actual_status",
            "inspection_status",
        ],
        fk_matrix,
    )
    paths[MERMAID_MD].write_text(render_mermaid(), encoding="utf-8")
    write_csv(
        paths[CHECKLIST_CSV],
        [
            "checklist_id",
            "inspection_question",
            "expected_answer",
            "actual_answer",
            "status",
            "notes",
        ],
        checklist,
    )
    write_csv(
        paths[NEXT_STEPS_CSV],
        [
            "step_id",
            "condition",
            "recommended_step",
            "target_db",
            "blocking_status",
            "notes",
        ],
        next_steps,
    )


def run(args: argparse.Namespace) -> int:
    live_db = Path(args.live_db)
    workcopy_db = Path(args.workcopy_db)
    output_root = Path(args.output_root)
    ensure_preconditions(live_db, workcopy_db, output_root, args.overwrite)

    live = inspect_db(live_db, dwh03_tables=False)
    work = inspect_db(workcopy_db, dwh03_tables=True)

    if live["integrity"] != "ok":
        raise RuntimeError(f"Live DB integrity_check failed: {live['integrity']}")
    if live["foreign_key_violations"]:
        raise RuntimeError(f"Live DB FK check has {len(live['foreign_key_violations'])} violation(s).")
    if work["integrity"] != "ok":
        raise RuntimeError(f"Workcopy DB integrity_check failed: {work['integrity']}")
    if work["foreign_key_violations"]:
        raise RuntimeError(f"Workcopy DB FK check has {len(work['foreign_key_violations'])} violation(s).")

    missing_tables = [table for table, exists in work["table_exists"].items() if not exists]
    if missing_tables:
        raise RuntimeError("Missing DWH03 skeleton table(s): " + ", ".join(missing_tables))

    nodes = build_nodes(work)
    edges = build_edges(work)
    fk_matrix = build_fk_matrix(nodes, edges)
    checklist = build_checklist(live, work, nodes, edges, fk_matrix)
    next_steps = build_next_steps(checklist)

    write_outputs(output_root, live_db, workcopy_db, live, work, nodes, edges, fk_matrix, checklist, next_steps)

    print(f"Live DB modified: {live['modified']}")
    print(f"Workcopy DB modified: {work['modified']}")
    print(f"Workcopy DB: {workcopy_db}")
    print(f"ERD nodes: {len(nodes)}")
    print(f"ERD edges: {len(edges)}")
    print(f"Live FK violations: {len(live['foreign_key_violations'])}")
    print(f"Workcopy FK violations: {len(work['foreign_key_violations'])}")
    print(f"Checklist passed: {sum(1 for row in checklist if row['status'] == 'passed')}")
    print(f"Checklist failed: {sum(1 for row in checklist if row['status'] != 'passed')}")
    print(f"Wrote {len(OUTPUT_FILENAMES)} DWH04 output files to {output_root}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a read-only ERD/visual inspection package for the DWH03 "
            "raw/core workcopy skeleton."
        )
    )
    parser.add_argument("--live-db", default=str(DEFAULT_LIVE_DB), help="Path to live consolidated Research DB.")
    parser.add_argument("--workcopy-db", default=str(DEFAULT_WORKCOPY_DB), help="Path to DWH03 workcopy DB.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Directory for DWH04 output reports.")
    parser.add_argument("--overwrite", action="store_true", help="Allow controlled regeneration of DWH04 report outputs only.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parse_args(sys.argv[1:] if argv is None else argv))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
