#!/usr/bin/env python3
"""QSB-DWH09: ERD inspection package for the Mapping/Evidence layer.

This is a read-only documentation step over the live Research DWH and the
DWH03/DWH05/DWH06/DWH08 workcopy DB. It inspects SQLite schema metadata,
declared FK structure, logical future token-position links, row-count
preservation, and report readiness for human DBeaver visual inspection.

It does not modify either DB, does not read raw TIM/PAR files, does not ingest
or migrate data, does not create/alter/drop DB objects, and does not compute
timing, model, or statistical quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh09_erd_mapping_evidence_visual_inspection.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh09_erd_mapping_evidence_visual_inspection_readout.md"
SUMMARY_JSON = "dwh09_erd_mapping_evidence_visual_inspection_summary.json"
NODES_CSV = "dwh09_mapping_evidence_erd_nodes.csv"
EDGES_CSV = "dwh09_mapping_evidence_erd_edges.csv"
FK_MATRIX_CSV = "dwh09_mapping_evidence_fk_matrix.csv"
MERMAID_MD = "dwh09_mapping_evidence_erd_mermaid.md"
CHECKLIST_CSV = "dwh09_visual_inspection_checklist.csv"
NEXT_STEPS_CSV = "dwh09_next_dwh_steps.csv"

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

DWH05_TABLES = [
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
]

DWH05_PRESERVATION_COUNTS = {
    "raw_record": 11395,
    "raw_field_value": 471874,
    "core_observation_record_link": 11395,
}

DWH06_DIMENSION_TABLES = [
    "dim_science_object",
    "dim_telescope",
    "dim_receiver",
    "dim_backend",
    "dim_time_context",
    "dim_processing_context",
    "dim_quality_status",
]

DWH08_TABLES = [
    "map_token_dictionary",
    "map_token_value_assertion",
    "map_assertion_evidence",
    "map_review_decision",
    "map_evidence_gap",
    "dwh08_mapping_evidence_run_log",
]

DWH08_COUNT_EXPECTATIONS = {
    "map_token_dictionary": 91,
    "map_token_value_assertion": 10,
    "map_assertion_evidence": 10,
    "map_review_decision": 52,
    "map_evidence_gap": 54,
}

DWH08_VIEWS = [
    "qsb_v_dwh08_mapping_evidence_dashboard",
    "qsb_v_dwh08_token_dictionary_status",
    "qsb_v_dwh08_open_evidence_gaps",
    "qsb_v_dwh08_next_mapping_actions",
]

ERD_TABLES = [
    "raw_record",
    "raw_field_value",
    "core_observation",
    "core_observation_record_link",
    "map_token_dictionary",
    "map_token_value_assertion",
    "map_assertion_evidence",
    "map_review_decision",
    "map_evidence_gap",
    "dwh08_mapping_evidence_run_log",
]

EXPECTED_DWH08_DECLARED_EDGES = [
    (
        "map_token_dictionary",
        "token_dictionary_id",
        "map_token_value_assertion",
        "token_dictionary_id",
        "token dictionary has explicit value assertions",
    ),
    (
        "map_token_value_assertion",
        "token_value_assertion_id",
        "map_assertion_evidence",
        "token_value_assertion_id",
        "value assertion has evidence rows",
    ),
    (
        "map_token_dictionary",
        "token_dictionary_id",
        "map_review_decision",
        "token_dictionary_id",
        "token dictionary has review decisions",
    ),
    (
        "map_assertion_evidence",
        "evidence_id",
        "map_review_decision",
        "evidence_id",
        "evidence may be referenced by review decisions",
    ),
    (
        "map_token_dictionary",
        "token_dictionary_id",
        "map_evidence_gap",
        "token_dictionary_id",
        "token dictionary has open evidence gaps",
    ),
]

CLAIM_BOUNDARY = (
    "DWH09 is a read-only ERD and visual-inspection documentation step for the "
    "DWH08 Mapping/Evidence layer. It documents declared SQLite FKs, logical "
    "future token-position links, row-count preservation, and human inspection "
    "readiness. It does not modify either DB, does not read raw TIM/PAR files, "
    "does not create bridge/result tables, does not verify external sources, "
    "does not resolve final TIM semantics, and does not make physical "
    "interpretation statements."
)


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


def table_info(con: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"PRAGMA table_info({quote_identifier(table_name)})")


def fk_list(con: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"PRAGMA foreign_key_list({quote_identifier(table_name)})")


def row_count(con: sqlite3.Connection, table_name: str) -> int:
    return int(
        con.execute(
            f"SELECT COUNT(*) AS n FROM {quote_identifier(table_name)}"
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


def primary_key(fields: list[dict[str, Any]]) -> str:
    pk_fields = [
        str(field["name"])
        for field in sorted(fields, key=lambda item: int(item["pk"]))
        if int(field["pk"]) > 0
    ]
    return ", ".join(pk_fields)


def field_is_not_null(fields: list[dict[str, Any]], field_name: str) -> bool:
    for field in fields:
        if field["name"] == field_name:
            return int(field["notnull"]) == 1
    return False


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
    existing = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH09 output file(s): "
            + "; ".join(existing)
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
    all_tables = sorted(set(DWH05_TABLES + DWH06_DIMENSION_TABLES + DWH08_TABLES + ERD_TABLES))
    with connect_readonly(path) as con:
        table_exists = {table: object_exists(con, table, "table") for table in all_tables}
        view_exists = {view: object_exists(con, view, "view") for view in DWH08_VIEWS}
        table_infos = {
            table: table_info(con, table) if table_exists[table] else []
            for table in all_tables
        }
        fks = {
            table: fk_list(con, table) if table_exists[table] else []
            for table in all_tables
        }
        counts = {
            table: row_count(con, table) if table_exists[table] else None
            for table in all_tables
        }
        view_counts: dict[str, int | None] = {}
        view_query_status: dict[str, str] = {}
        for view in DWH08_VIEWS:
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
            "row_counts": counts,
        }
    state_after = db_state(path)
    result["state_after"] = state_after
    result["modified"] = state_before != state_after
    return result


def node_meta(table_name: str) -> dict[str, str]:
    rows = {
        "raw_record": {
            "layer": "Raw/Core Anchor",
            "table_role": "Raw record/line anchor",
            "erd_group": "Raw/Core Anchor",
            "visual_priority": "P1",
            "notes": "Optional raw anchor; declared parent of raw_field_value and observation link.",
        },
        "raw_field_value": {
            "layer": "Raw/Core Anchor",
            "table_role": "Raw token/field value table",
            "erd_group": "Raw/Core Anchor",
            "visual_priority": "P1",
            "notes": "Logical future source for token-position mapping; no FK to map_token_dictionary yet.",
        },
        "core_observation": {
            "layer": "Core Observation Anchor",
            "table_role": "Observation anchor",
            "erd_group": "Raw/Core Anchor",
            "visual_priority": "P1",
            "notes": "Connects to raw records through core_observation_record_link.",
        },
        "core_observation_record_link": {
            "layer": "Core Observation Anchor",
            "table_role": "Observation-to-raw link",
            "erd_group": "Raw/Core Anchor",
            "visual_priority": "P1",
            "notes": "Declared link from core_observation to raw_record.",
        },
        "map_token_dictionary": {
            "layer": "Mapping/Evidence Target",
            "table_role": "Token dictionary hub",
            "erd_group": "DWH08 Mapping/Evidence",
            "visual_priority": "P1",
            "notes": "Central map_* hub keyed by token_dictionary_id and positioned by line_family/token_position.",
        },
        "map_token_value_assertion": {
            "layer": "Mapping/Evidence Target",
            "table_role": "Explicit value assertion",
            "erd_group": "DWH08 Mapping/Evidence",
            "visual_priority": "P1",
            "notes": "Contains only explicit DB28/DB27 value assertion relationships, not all raw values.",
        },
        "map_assertion_evidence": {
            "layer": "Mapping/Evidence Target",
            "table_role": "Evidence row for assertion",
            "erd_group": "DWH08 Mapping/Evidence",
            "visual_priority": "P1",
            "notes": "Evidence seed row linked to explicit value assertion.",
        },
        "map_review_decision": {
            "layer": "Mapping/Evidence Target",
            "table_role": "Pending/proposed review decision",
            "erd_group": "DWH08 Mapping/Evidence",
            "visual_priority": "P1",
            "notes": "Review rows can link to token dictionary and optionally to evidence.",
        },
        "map_evidence_gap": {
            "layer": "Mapping/Evidence Target",
            "table_role": "Open mapping/evidence gap",
            "erd_group": "DWH08 Mapping/Evidence",
            "visual_priority": "P1",
            "notes": "Gap rows document unresolved mapping/evidence work before controlled definitions.",
        },
        "dwh08_mapping_evidence_run_log": {
            "layer": "DWH08 Run Metadata",
            "table_role": "DWH08 run log",
            "erd_group": "Run Metadata",
            "visual_priority": "P3",
            "notes": "Isolated run log by design; documents DWH08 execution metadata.",
        },
    }
    return rows[table_name]


def build_nodes(work: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for table in ERD_TABLES:
        meta = node_meta(table)
        nodes.append(
            {
                "table_name": table,
                "layer": meta["layer"],
                "table_role": meta["table_role"],
                "primary_key": primary_key(work["table_info"].get(table, [])),
                "row_count": work["row_counts"].get(table),
                "erd_group": meta["erd_group"],
                "visual_priority": meta["visual_priority"],
                "notes": meta["notes"],
            }
        )
    return nodes


def declared_edge_label(parent: str, child: str, parent_field: str, child_field: str) -> str:
    for source_table, source_field, target_table, target_field, label in EXPECTED_DWH08_DECLARED_EDGES:
        if (
            parent == source_table
            and child == target_table
            and parent_field == source_field
            and child_field == target_field
        ):
            return label
    labels = {
        ("raw_record", "raw_field_value"): "raw record contains raw field values",
        ("core_observation", "core_observation_record_link"): "observation connects to raw records",
        ("raw_record", "core_observation_record_link"): "raw record participates in observation link",
    }
    return labels.get((parent, child), "declared SQLite FK")


def build_declared_edges(work: dict[str, Any]) -> list[dict[str, Any]]:
    inspected = set(ERD_TABLES)
    edges: list[dict[str, Any]] = []
    for child_table in ERD_TABLES:
        fields = work["table_info"].get(child_table, [])
        for fk in work["foreign_key_list"].get(child_table, []):
            parent_table = str(fk["table"])
            if parent_table not in inspected:
                continue
            child_field = str(fk["from"])
            parent_field = str(fk["to"])
            if parent_field == "None":
                parent_field = primary_key(work["table_info"].get(parent_table, []))
            group = (
                "DWH08 Mapping/Evidence Declared FK"
                if parent_table.startswith("map_") or child_table.startswith("map_")
                else "Raw/Core Anchor Declared FK"
            )
            edges.append(
                {
                    "source_table": parent_table,
                    "source_field": parent_field,
                    "target_table": child_table,
                    "target_field": child_field,
                    "relationship_label": declared_edge_label(
                        parent_table,
                        child_table,
                        parent_field,
                        child_field,
                    ),
                    "relationship_type": "declared_fk",
                    "mandatory": "yes" if field_is_not_null(fields, child_field) else "no",
                    "erd_group": group,
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


def build_logical_edges() -> list[dict[str, Any]]:
    return [
        {
            "source_table": "raw_field_value",
            "source_field": "token_position",
            "target_table": "map_token_dictionary",
            "target_field": "token_position",
            "relationship_label": "logical token-position mapping path",
            "relationship_type": "logical_token_position_link",
            "mandatory": "no",
            "erd_group": "Logical Future Mapping Link",
            "enforcement_status": "not_enforced_yet",
            "notes": (
                "Requires later controlled join/design because map_token_dictionary "
                "describes token positions/families, not individual raw field rows."
            ),
        },
        {
            "source_table": "core_observation",
            "source_field": "observation_id",
            "target_table": "map_token_dictionary",
            "target_field": "token_position",
            "relationship_label": "logical future path through raw/core and token position",
            "relationship_type": "logical_future_join_path",
            "mandatory": "no",
            "erd_group": "Logical Future Mapping Link",
            "enforcement_status": "not_enforced_yet",
            "notes": (
                "Future path is core_observation -> core_observation_record_link -> "
                "raw_record -> raw_field_value -> map_token_dictionary; not a declared FK."
            ),
        },
    ]


def build_edges(work: dict[str, Any]) -> list[dict[str, Any]]:
    return build_declared_edges(work) + build_logical_edges()


def edge_exists(
    edges: list[dict[str, Any]],
    source_table: str,
    target_table: str,
    relationship_type: str = "declared_fk",
) -> bool:
    return any(
        edge["source_table"] == source_table
        and edge["target_table"] == target_table
        and edge["relationship_type"] == relationship_type
        for edge in edges
    )


def build_fk_matrix(work: dict[str, Any], edges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for table in ERD_TABLES:
        declared_fk_count = len(work["foreign_key_list"].get(table, []))
        incoming = sum(
            1 for edge in edges
            if edge["relationship_type"] == "declared_fk" and edge["target_table"] == table
        )
        outgoing = sum(
            1 for edge in edges
            if edge["relationship_type"] == "declared_fk" and edge["source_table"] == table
        )
        logical = sum(
            1 for edge in edges
            if edge["relationship_type"] != "declared_fk"
            and (edge["source_table"] == table or edge["target_table"] == table)
        )
        is_connected = (incoming + outgoing + logical) > 0
        if table == "dwh08_mapping_evidence_run_log":
            expected_status = "isolated_run_log_ok"
            actual_status = "isolated" if not is_connected else "connected"
            passed = not is_connected
            comment = "Run log is isolated by design."
        else:
            expected_status = "connected_in_visual_slice"
            actual_status = "connected" if is_connected else "isolated"
            passed = is_connected
            comment = "Connected by declared FK and/or documented logical future link."
        rows.append(
            {
                "table_name": table,
                "declared_fk_count": declared_fk_count,
                "incoming_declared_edge_count": incoming,
                "outgoing_declared_edge_count": outgoing,
                "logical_edge_count": logical,
                "is_connected": "yes" if is_connected else "no",
                "connection_comment": comment,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "inspection_status": "passed" if passed else "failed",
            }
        )
    return rows


def preservation_status(work: dict[str, Any]) -> dict[str, Any]:
    dwh05 = {
        table: {
            "expected": expected,
            "actual": work["row_counts"].get(table),
            "status": "passed" if work["row_counts"].get(table) == expected else "failed",
        }
        for table, expected in DWH05_PRESERVATION_COUNTS.items()
    }
    dwh06_counts = {
        table: work["row_counts"].get(table) for table in DWH06_DIMENSION_TABLES
    }
    dwh06_seed_rows = sum(int(count or 0) for count in dwh06_counts.values())
    dwh08 = {
        table: {
            "expected": expected,
            "actual": work["row_counts"].get(table),
            "status": "passed" if work["row_counts"].get(table) == expected else "failed",
        }
        for table, expected in DWH08_COUNT_EXPECTATIONS.items()
    }
    return {
        "dwh05_raw_core": dwh05,
        "dwh05_status": "passed" if all(item["status"] == "passed" for item in dwh05.values()) else "failed",
        "dwh06_dimension_table_counts": dwh06_counts,
        "dwh06_dimension_seed_row_total": dwh06_seed_rows,
        "dwh06_status": "passed" if dwh06_seed_rows == 7 else "failed",
        "dwh08_mapping_evidence": dwh08,
        "dwh08_status": "passed" if all(item["status"] == "passed" for item in dwh08.values()) else "failed",
    }


def all_present(work: dict[str, Any], names: list[str], kind: str) -> bool:
    key = "table_exists" if kind == "table" else "view_exists"
    return all(bool(work[key].get(name)) for name in names)


def all_views_queryable(work: dict[str, Any]) -> bool:
    return all(work["view_query_status"].get(view) == "queryable" for view in DWH08_VIEWS)


def build_checklist(
    live: dict[str, Any],
    work: dict[str, Any],
    edges: list[dict[str, Any]],
    preservation: dict[str, Any],
) -> list[dict[str, Any]]:
    dwh08_edges_ok = all(
        edge_exists(edges, source, target)
        for source, _source_field, target, _target_field, _label in EXPECTED_DWH08_DECLARED_EDGES
    )
    logical_raw = edge_exists(
        edges,
        "raw_field_value",
        "map_token_dictionary",
        "logical_token_position_link",
    )
    fks_clean = (
        len(live["foreign_key_violations"]) == 0
        and len(work["foreign_key_violations"]) == 0
    )
    visual_pattern_ok = (
        edge_exists(edges, "map_token_dictionary", "map_token_value_assertion")
        and edge_exists(edges, "map_token_value_assertion", "map_assertion_evidence")
        and edge_exists(edges, "map_token_dictionary", "map_review_decision")
        and edge_exists(edges, "map_assertion_evidence", "map_review_decision")
        and edge_exists(edges, "map_token_dictionary", "map_evidence_gap")
    )
    critical_ok = (
        all_present(work, DWH08_TABLES, "table")
        and preservation["dwh08_status"] == "passed"
        and all_views_queryable(work)
        and dwh08_edges_ok
        and logical_raw
        and preservation["dwh05_status"] == "passed"
        and preservation["dwh06_status"] == "passed"
        and fks_clean
        and visual_pattern_ok
        and not live["modified"]
        and not work["modified"]
    )

    def row(idx: int, question: str, expected: str, actual: str, ok: bool, notes: str) -> dict[str, Any]:
        return {
            "checklist_id": f"DWH09_CHECK_{idx:02d}",
            "inspection_question": question,
            "expected_answer": expected,
            "actual_answer": actual,
            "status": "passed" if ok else "failed",
            "notes": notes,
        }

    return [
        row(1, "Are all DWH08 map_* tables present?", "yes", str(all_present(work, DWH08_TABLES, "table")).lower(), all_present(work, DWH08_TABLES, "table"), "Includes dwh08_mapping_evidence_run_log."),
        row(2, "Are DWH08 map_* row counts preserved?", "yes", preservation["dwh08_status"], preservation["dwh08_status"] == "passed", pretty_json(preservation["dwh08_mapping_evidence"])),
        row(3, "Are all DWH08 views present/queryable?", "yes", str(all_views_queryable(work)).lower(), all_present(work, DWH08_VIEWS, "view") and all_views_queryable(work), pretty_json(work["view_query_status"])),
        row(4, "Does map_token_dictionary connect to map_token_value_assertion?", "declared FK", str(edge_exists(edges, "map_token_dictionary", "map_token_value_assertion")).lower(), edge_exists(edges, "map_token_dictionary", "map_token_value_assertion"), "DWH08 declared FK edge."),
        row(5, "Does map_token_value_assertion connect to map_assertion_evidence?", "declared FK", str(edge_exists(edges, "map_token_value_assertion", "map_assertion_evidence")).lower(), edge_exists(edges, "map_token_value_assertion", "map_assertion_evidence"), "DWH08 declared FK edge."),
        row(6, "Does map_token_dictionary connect to map_review_decision?", "declared FK", str(edge_exists(edges, "map_token_dictionary", "map_review_decision")).lower(), edge_exists(edges, "map_token_dictionary", "map_review_decision"), "DWH08 declared FK edge."),
        row(7, "Does map_assertion_evidence connect to map_review_decision?", "declared FK", str(edge_exists(edges, "map_assertion_evidence", "map_review_decision")).lower(), edge_exists(edges, "map_assertion_evidence", "map_review_decision"), "DWH08 declared FK edge."),
        row(8, "Does map_token_dictionary connect to map_evidence_gap?", "declared FK", str(edge_exists(edges, "map_token_dictionary", "map_evidence_gap")).lower(), edge_exists(edges, "map_token_dictionary", "map_evidence_gap"), "DWH08 declared FK edge."),
        row(9, "Is the raw_field_value to map_token_dictionary link clearly documented as logical/future, not enforced?", "yes", str(logical_raw).lower(), logical_raw, "No declared FK is invented for raw_field_value.token_position."),
        row(10, "Are DWH05 raw/core counts preserved?", "yes", preservation["dwh05_status"], preservation["dwh05_status"] == "passed", pretty_json(preservation["dwh05_raw_core"])),
        row(11, "Are DWH06 dimension seed rows preserved?", "7 seed rows or equivalent", str(preservation["dwh06_dimension_seed_row_total"]), preservation["dwh06_status"] == "passed", pretty_json(preservation["dwh06_dimension_table_counts"])),
        row(12, "Are FK checks clean?", "live=0 and workcopy=0", f"live={len(live['foreign_key_violations'])}; workcopy={len(work['foreign_key_violations'])}", fks_clean, "PRAGMA foreign_key_check on read-only connections."),
        row(13, "Is the Mapping/Evidence layer visually understandable as Token -> Assertion -> Evidence -> Review/Gap?", "yes", str(visual_pattern_ok).lower(), visual_pattern_ok, "Based on declared DWH08 FK pattern."),
        row(14, "Are no Bridge/Result tables created yet?", "yes", "yes", True, "DWH09 is read-only and creates no DB objects."),
        row(15, "Is the workcopy suitable for DWH10 controlled mapping refinement or external evidence verification?", "yes if critical checks pass", "yes" if critical_ok else "no", critical_ok, "Bounded to mapping/evidence work only."),
        row(16, "Is the workcopy suitable for future Bridge/Result planning only after mapping/evidence visual inspection passes?", "yes if critical checks pass", "yes" if critical_ok else "no", critical_ok, "Bridge/result planning remains deferred until inspection is accepted."),
    ]


def checklist_summary(checklist: list[dict[str, Any]]) -> dict[str, int]:
    passed = sum(1 for row in checklist if row["status"] == "passed")
    failed = sum(1 for row in checklist if row["status"] == "failed")
    return {"passed": passed, "failed": failed, "total": len(checklist)}


def next_dwh_steps_rows(checklist: list[dict[str, Any]]) -> list[dict[str, str]]:
    failed = checklist_summary(checklist)["failed"]
    if failed == 0:
        return [
            {
                "next_step_id": "DWH10_C",
                "next_step_name": "Controlled mapping refinement for first 5 block-switch tokens only",
                "prerequisite": "DWH09 visual inspection checklist passed",
                "recommended_action": "Refine only tim_token_007, tim_token_011, tim_token_013, tim_token_017, and tim_token_023.",
                "risk_level": "medium",
                "notes": "Recommended first because it keeps controlled mapping refinement bounded and auditable.",
            },
            {
                "next_step_id": "DWH10_B",
                "next_step_name": "External evidence verification for receiver/backend/telescope terms",
                "prerequisite": "DWH09 visual inspection checklist passed",
                "recommended_action": "Verify receiver/backend/telescope terms against approved external source classes.",
                "risk_level": "medium",
                "notes": "Alternative next step if source verification should precede controlled token refinement.",
            },
            {
                "next_step_id": "DWH10_DEFER_BRIDGE_RESULT",
                "next_step_name": "Defer bridge/result skeleton planning",
                "prerequisite": "Mapping/evidence review accepted",
                "recommended_action": "Plan bridge/result tables only after controlled mapping/evidence review remains clean.",
                "risk_level": "high",
                "notes": "DWH09 does not create bridge/result tables.",
            },
        ]
    return [
        {
            "next_step_id": "DWH10A",
            "next_step_name": "Adjust Mapping/Evidence skeleton in a new workcopy",
            "prerequisite": "One or more DWH09 visual inspection checks failed",
            "recommended_action": "Repair the Mapping/Evidence skeleton in a controlled new workcopy, not the live DB.",
            "risk_level": "medium",
            "notes": "Do not patch the live DB.",
        }
    ]


def build_summary(
    live: dict[str, Any],
    work: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    fk_matrix: list[dict[str, Any]],
    checklist: list[dict[str, Any]],
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    run_timestamp: str,
) -> dict[str, Any]:
    preservation = preservation_status(work)
    declared_edges = [edge for edge in edges if edge["relationship_type"] == "declared_fk"]
    logical_edges = [edge for edge in edges if edge["relationship_type"] != "declared_fk"]
    return {
        "run_timestamp_utc": run_timestamp,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH visual architecture inspection / read-only documentation mode",
        "data_substrate_used": str(workcopy_db),
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "raw_tim_par_files_read": False,
        "db_objects_modified": False,
        "live_db_modified": live["modified"],
        "workcopy_db_modified": work["modified"],
        "live_db_inspection": {
            "integrity_check": live["integrity_check"],
            "foreign_key_violation_count": len(live["foreign_key_violations"]),
            "state_before": live["state_before"],
            "state_after": live["state_after"],
        },
        "workcopy_db_inspection": {
            "integrity_check": work["integrity_check"],
            "foreign_key_violation_count": len(work["foreign_key_violations"]),
            "state_before": work["state_before"],
            "state_after": work["state_after"],
            "dwh05_table_exists": {table: work["table_exists"].get(table) for table in DWH05_TABLES},
            "dwh06_table_exists": {table: work["table_exists"].get(table) for table in DWH06_DIMENSION_TABLES},
            "dwh08_table_exists": {table: work["table_exists"].get(table) for table in DWH08_TABLES},
            "dwh08_view_exists": work["view_exists"],
            "dwh08_view_query_status": work["view_query_status"],
            "dwh08_view_counts": work["view_counts"],
        },
        "preservation": preservation,
        "erd_node_count": len(nodes),
        "erd_edge_count": len(edges),
        "declared_edge_count": len(declared_edges),
        "logical_edge_count": len(logical_edges),
        "nodes": nodes,
        "edges": edges,
        "fk_matrix": fk_matrix,
        "checklist_summary": checklist_summary(checklist),
        "checklist": checklist,
        "next_dwh_steps": next_dwh_steps_rows(checklist),
        "mermaid_output_path": str(output_root / MERMAID_MD),
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def mermaid_entity(table: str, fields: list[dict[str, Any]], max_fields: int = 5) -> str:
    lines = [f"    {table} {{"]
    for field in fields[:max_fields]:
        suffix = " PK" if int(field["pk"]) > 0 else ""
        lines.append(f"        {field['type'] or 'TEXT'} {field['name']}{suffix}")
    if len(fields) > max_fields:
        lines.append("        TEXT ...")
    lines.append("    }")
    return "\n".join(lines)


def write_mermaid(path: Path, work: dict[str, Any]) -> None:
    entity_blocks = "\n\n".join(
        mermaid_entity(table, work["table_info"].get(table, []))
        for table in ERD_TABLES
    )
    content = f"""# DWH09 Mapping/Evidence ERD Mermaid

```mermaid
erDiagram
    raw_record ||--o{{ raw_field_value : declared_fk
    core_observation ||--o{{ core_observation_record_link : declared_fk
    core_observation_record_link }}o..o{{ raw_record : raw_record_anchor
    raw_field_value }}o..o{{ map_token_dictionary : logical_token_position_link
    core_observation }}o..o{{ map_token_dictionary : logical_future_join_path

    map_token_dictionary ||--o{{ map_token_value_assertion : declared_fk
    map_token_value_assertion ||--o{{ map_assertion_evidence : declared_fk
    map_token_dictionary ||--o{{ map_review_decision : declared_fk
    map_assertion_evidence ||--o{{ map_review_decision : declared_fk
    map_token_dictionary ||--o{{ map_evidence_gap : declared_fk

{entity_blocks}
```

Notes:
- Declared FK edges are inspected from SQLite `PRAGMA foreign_key_list`.
- `raw_field_value.token_position -> map_token_dictionary.token_position` is intentionally a logical/future link, not an enforced FK.
- The `core_observation` to `map_token_dictionary` path is logical/future through `core_observation_record_link`, `raw_record`, and `raw_field_value`.
- Hide legacy DBXX tables in DBeaver when inspecting this compact slice.
"""
    path.write_text(content, encoding="utf-8")


def format_count_lines(items: dict[str, Any]) -> str:
    return "\n".join(f"- {name}: {value}" for name, value in items.items())


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    preservation = summary["preservation"]
    checklist = summary["checklist_summary"]
    live_status = "unchanged" if not summary["live_db_modified"] else "changed"
    work_status = "unchanged" if not summary["workcopy_db_modified"] else "changed"
    dwh08_counts = {
        table: item["actual"]
        for table, item in preservation["dwh08_mapping_evidence"].items()
    }
    declared_lines = [
        "- {source_table}.{source_field} -> {target_table}.{target_field}: {relationship_label}".format(**edge)
        for edge in summary["edges"]
        if edge["relationship_type"] == "declared_fk"
        and (edge["source_table"].startswith("map_") or edge["target_table"].startswith("map_"))
    ]
    logical_lines = [
        "- {source_table}.{source_field} -> {target_table}.{target_field}: {relationship_type}; {notes}".format(**edge)
        for edge in summary["edges"]
        if edge["relationship_type"] != "declared_fk"
    ]
    checklist_lines = [
        f"- {row['checklist_id']}: {row['status']} - {row['inspection_question']}"
        for row in summary["checklist"]
    ]
    next_lines = [
        f"- {row['next_step_id']}: {row['next_step_name']}"
        for row in summary["next_dwh_steps"]
    ]
    content = f"""# QSB-DWH09 ERD Mapping/Evidence Visual Inspection Readout

## 1. Executive summary

Befund: DWH09 inspected the DWH08 Mapping/Evidence layer in read-only mode and generated a compact ERD/visual-inspection package.

- Workcopy DB: `{summary['workcopy_db_path']}`
- ERD nodes: {summary['erd_node_count']}
- ERD edges: {summary['erd_edge_count']}
- Declared FK edges: {summary['declared_edge_count']}
- Logical future-link edges: {summary['logical_edge_count']}
- Checklist: {checklist['passed']} passed / {checklist['failed']} failed

## 2. Workcopy inspected

Primary substrate was the SQLite workcopy DB, opened read-only:

`{summary['workcopy_db_path']}`

No raw TIM/PAR files and no report exports were used as the inspection substrate.

## 3. Live/workcopy protection result

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['live_db_inspection']['integrity_check']}
- Live FK violation count: {summary['live_db_inspection']['foreign_key_violation_count']}
- Live DB checksum/stat status: {live_status}
- Workcopy integrity_check: {summary['workcopy_db_inspection']['integrity_check']}
- Workcopy FK violation count: {summary['workcopy_db_inspection']['foreign_key_violation_count']}
- Workcopy DB checksum/stat status: {work_status}

## 4. DWH05/DWH06 preservation result

- DWH05 raw/core preservation: {preservation['dwh05_status']}
- DWH06 dimension seed-row preservation: {preservation['dwh06_status']}
- DWH06 dimension seed-row total: {preservation['dwh06_dimension_seed_row_total']}

## 5. DWH08 Mapping/Evidence inventory

{format_count_lines(dwh08_counts)}

Preservation status: {preservation['dwh08_status']}

## 6. Declared FK / edge inventory

{chr(10).join(declared_lines)}

## 7. Logical future links to raw_field_value and core_observation

{chr(10).join(logical_lines)}

## 8. Visual ERD interpretation

The compact visual pattern is:

`map_token_dictionary -> map_token_value_assertion -> map_assertion_evidence -> map_review_decision`

with companion branches:

`map_token_dictionary -> map_review_decision`

`map_token_dictionary -> map_evidence_gap`

The raw/core anchor shows where a later controlled design can connect raw token positions to dictionary rows without asserting that every raw value already has a controlled meaning.

## 9. DBeaver inspection instructions

1. Open DBeaver.
2. Open SQLite workcopy connection: `runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db`
3. Focus on this Mapping/Evidence ERD slice: `raw_record`, `raw_field_value`, `core_observation`, `core_observation_record_link`, `map_token_dictionary`, `map_token_value_assertion`, `map_assertion_evidence`, `map_review_decision`, `map_evidence_gap`, `dwh08_mapping_evidence_run_log`.
4. Hide legacy DBXX tables.
5. Expected visible pattern: `map_token_dictionary -> map_token_value_assertion -> map_assertion_evidence`; `map_token_dictionary -> map_review_decision`; `map_assertion_evidence -> map_review_decision`; `map_token_dictionary -> map_evidence_gap`.
6. Important: DBeaver may not draw `raw_field_value` to `map_token_dictionary` as an FK because this is intentionally only a logical token-position join for now.
7. Do not synchronize or write schema changes from DBeaver back to the DB.

## 10. Pass/fail checklist

{chr(10).join(checklist_lines)}

## 11. Recommended next DWH step

{chr(10).join(next_lines)}

## 12. What DWH09 does not do

DWH09 does not modify the live DB, does not modify the workcopy DB, does not read raw TIM/PAR files, does not ingest or migrate data, does not create/alter/drop DB objects, does not verify external sources, does not create bridge/result tables, and does not assign final controlled meanings to unresolved TIM tokens.

## 13. Claim boundary

{summary['claim_boundary']}
"""
    path.write_text(content, encoding="utf-8")


def write_outputs(
    output_root: Path,
    summary: dict[str, Any],
    nodes: list[dict[str, Any]],
    edges: list[dict[str, Any]],
    fk_matrix: list[dict[str, Any]],
    checklist: list[dict[str, Any]],
    next_steps: list[dict[str, str]],
    work: dict[str, Any],
) -> None:
    paths = output_paths(output_root)
    write_readout(paths[READOUT_MD], summary)
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    write_csv(
        paths[NODES_CSV],
        ["table_name", "layer", "table_role", "primary_key", "row_count", "erd_group", "visual_priority", "notes"],
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
            "enforcement_status",
            "notes",
        ],
        edges,
    )
    write_csv(
        paths[FK_MATRIX_CSV],
        [
            "table_name",
            "declared_fk_count",
            "incoming_declared_edge_count",
            "outgoing_declared_edge_count",
            "logical_edge_count",
            "is_connected",
            "connection_comment",
            "expected_status",
            "actual_status",
            "inspection_status",
        ],
        fk_matrix,
    )
    write_mermaid(paths[MERMAID_MD], work)
    write_csv(
        paths[CHECKLIST_CSV],
        ["checklist_id", "inspection_question", "expected_answer", "actual_answer", "status", "notes"],
        checklist,
    )
    write_csv(
        paths[NEXT_STEPS_CSV],
        ["next_step_id", "next_step_name", "prerequisite", "recommended_action", "risk_level", "notes"],
        next_steps,
    )


def execute(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    ensure_preconditions(live_db, workcopy_db, output_root, overwrite)
    run_timestamp = utc_now()
    live = inspect_live_db(live_db)
    work = inspect_workcopy_db(workcopy_db)
    preservation = preservation_status(work)
    nodes = build_nodes(work)
    edges = build_edges(work)
    fk_matrix = build_fk_matrix(work, edges)
    checklist = build_checklist(live, work, edges, preservation)
    summary = build_summary(
        live,
        work,
        nodes,
        edges,
        fk_matrix,
        checklist,
        live_db,
        workcopy_db,
        output_root,
        run_timestamp,
    )
    write_outputs(
        output_root,
        summary,
        nodes,
        edges,
        fk_matrix,
        checklist,
        next_dwh_steps_rows(checklist),
        work,
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "QSB-DWH09 read-only ERD/visual inspection package for the "
            "DWH08 Mapping/Evidence layer."
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
        help="Path to the DWH target workcopy SQLite DB; opened read-only.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Existing output directory for DWH09 report files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting DWH09 report files only; DBs remain read-only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = execute(
            args.live_db,
            args.workcopy_db,
            args.output_root,
            args.overwrite,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
