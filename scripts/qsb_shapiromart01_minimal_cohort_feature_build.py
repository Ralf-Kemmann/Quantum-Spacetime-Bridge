#!/usr/bin/env python3
"""QSB-SHAPIROMART01: minimal cohort and feature availability build.

This script builds a small Shapiro-Mart substrate in the existing workcopy DB.
It uses only existing DB tables/views as input, keeps compound labels open, and
does not compute timing, model, result, or statistical quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart01_minimal_cohort_feature_build.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART01_MINIMAL_COHORT_FEATURE_BUILD"
)

READOUT_MD = "shapiromart01_readout.md"
SUMMARY_JSON = "shapiromart01_summary.json"
OBS_CONTEXT_CSV = "shapiromart01_observation_context.csv"
FEATURE_CSV = "shapiromart01_feature_availability.csv"
COMPARISON_CSV = "shapiromart01_comparison_cohort.csv"
CONTROL_GAP_CSV = "shapiromart01_control_gaps.csv"
NEXT_STEP_CSV = "shapiromart01_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    OBS_CONTEXT_CSV,
    FEATURE_CSV,
    COMPARISON_CSV,
    CONTROL_GAP_CSV,
    NEXT_STEP_CSV,
]

TARGET_TABLES = [
    "mart_shapiro_observation_context",
    "mart_shapiro_feature_availability",
    "mart_shapiro_comparison_cohort",
    "mart_shapiro_control_gap",
    "shapiromart01_run_log",
]

TARGET_VIEWS = [
    "qsb_v_shapiromart01_dashboard",
    "qsb_v_shapiromart01_supported_contexts",
    "qsb_v_shapiromart01_feature_availability",
    "qsb_v_shapiromart01_comparison_readiness",
    "qsb_v_shapiromart01_blocking_gaps",
]

REQUIRED_TABLES = [
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
    "core_observation",
    "core_observation_record_link",
    "dim_science_object",
    "dim_telescope",
    "dim_receiver",
    "dim_backend",
    "dim_time_context",
    "dim_processing_context",
    "dim_quality_status",
    "map_token_dictionary",
    "map_token_value_assertion",
    "map_assertion_evidence",
    "map_review_decision",
    "map_evidence_gap",
]

REQUIRED_VIEWS = [
    "qsb_v_dwh15a_supported_review_ready_candidates",
    "qsb_v_dwh15a_skipped_deferred_candidates",
    "qsb_v_dwh14a_supported_candidate_terms",
    "qsb_v_dwh14a_open_or_conflict_terms",
]

SUPPORTED_COMPONENT_TERMS = ["GUPPI", "Rcvr_800", "Rcvr1_2"]
SUPPORTED_RECEIVERS = ["Rcvr_800", "Rcvr1_2"]
SUPPORTED_BACKEND = "GUPPI"

COMPOUND_CONTEXTS = [
    {
        "raw_context_label": "Rcvr_800_GUPPI",
        "receiver_term": "Rcvr_800",
        "backend_term": SUPPORTED_BACKEND,
    },
    {
        "raw_context_label": "Rcvr1_2_GUPPI",
        "receiver_term": "Rcvr1_2",
        "backend_term": SUPPORTED_BACKEND,
    },
]

OPEN_COMPOUND_LABELS = [row["raw_context_label"] for row in COMPOUND_CONTEXTS]

SUPPORT_BOUNDARY = (
    "Use supported components as context candidates. Compound labels remain "
    "visible as unresolved raw/context labels only."
)

CLAIM_BOUNDARY = (
    "SHAPIROMART01 builds a minimal data-availability and cohort substrate only. "
    "It does not update mapping decisions, promote compound labels, compute "
    "timing/model/statistical quantities, or make Bridge, Shapiro, or "
    "interpretive claims."
)

NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def connect_writable(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=rw", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
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


def table_count(con: sqlite3.Connection, table_name: str) -> int:
    row = con.execute(
        f"SELECT COUNT(*) AS n FROM {quote_identifier(table_name)}"
    ).fetchone()
    return int(row["n"])


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_stat(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {"size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def db_state(path: Path) -> dict[str, Any]:
    return {"sha256": file_sha256(path), "stat": file_stat(path)}


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


def fail(message: str) -> None:
    raise RuntimeError(message)


def stable_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def table_names(con: sqlite3.Connection) -> list[str]:
    return [
        str(row["name"])
        for row in con.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        )
    ]


def object_names(con: sqlite3.Connection) -> list[dict[str, str]]:
    return [
        {"name": str(row["name"]), "type": str(row["type"])}
        for row in con.execute(
            """
            SELECT name, type
            FROM sqlite_master
            WHERE type IN ('table', 'view')
            ORDER BY type, name
            """
        )
    ]


def existing_table_counts(con: sqlite3.Connection) -> dict[str, int]:
    return {
        name: table_count(con, name)
        for name in table_names(con)
        if name not in TARGET_TABLES and not name.startswith("sqlite_")
    }


def mapping_separation_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(
        fetch_dicts(
            con,
            """
            SELECT
                'supported' AS separation_class,
                token_position,
                term,
                dwh14a_decision_status,
                dwh14a_evidence_strength,
                new_mapping_status,
                new_review_status,
                safe_to_promote
            FROM qsb_v_dwh15a_supported_review_ready_candidates
            WHERE term IN ('GUPPI', 'Rcvr_800', 'Rcvr1_2',
                           'Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
            ORDER BY separation_class, term, token_position
            """
        )
    )
    rows.extend(
        fetch_dicts(
            con,
            """
            SELECT
                'open_or_deferred' AS separation_class,
                token_position,
                term,
                dwh14a_decision_status,
                dwh14a_evidence_strength,
                skip_reason AS new_mapping_status,
                notes AS new_review_status,
                safe_to_promote
            FROM qsb_v_dwh15a_skipped_deferred_candidates
            WHERE term IN ('GUPPI', 'Rcvr_800', 'Rcvr1_2',
                           'Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
            ORDER BY separation_class, term, token_position
            """
        )
    )
    return sorted(rows, key=lambda row: (row["separation_class"], row["term"], row["token_position"]))


def validate_required_objects(con: sqlite3.Connection) -> dict[str, Any]:
    missing: list[str] = []
    checks: list[dict[str, str]] = []
    for name in REQUIRED_TABLES:
        status = "exists" if object_exists(con, name, "table") else "missing"
        checks.append({"object_name": name, "object_type": "table", "status": status})
        if status == "missing":
            missing.append(f"table:{name}")
    for name in REQUIRED_VIEWS:
        status = "exists" if object_exists(con, name, "view") else "missing"
        checks.append({"object_name": name, "object_type": "view", "status": status})
        if status == "missing":
            missing.append(f"view:{name}")
    if missing:
        fail("Missing required workcopy objects: " + "; ".join(missing))
    return {"checks": checks, "missing_count": 0}


def ensure_paths(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    if not args.output_root.is_dir():
        fail(f"Output root is not a directory: {args.output_root}")

    existing_outputs = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing_outputs and not args.overwrite:
        fail(
            "SHAPIROMART01 output files already exist. Use --overwrite to replace: "
            + "; ".join(existing_outputs)
        )


def validate_existing_target_state(con: sqlite3.Connection, allow_existing: bool) -> dict[str, Any]:
    target_state: list[dict[str, Any]] = []
    populated: list[str] = []
    for table in TARGET_TABLES:
        if object_exists(con, table, "table"):
            count = table_count(con, table)
            target_state.append({"table": table, "exists": True, "row_count": count})
            if count > 0:
                populated.append(f"{table}:{count}")
        else:
            target_state.append({"table": table, "exists": False, "row_count": 0})
    if populated and not allow_existing:
        fail(
            "SHAPIROMART01 target tables already contain rows. "
            "Use --allow-existing only for an explicit rerun: "
            + "; ".join(populated)
        )
    return {"target_tables": target_state}


def component_statuses(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT
            term,
            token_position,
            dwh14a_decision_status,
            dwh14a_evidence_strength,
            new_mapping_status,
            new_review_status
        FROM qsb_v_dwh15a_supported_review_ready_candidates
        WHERE term IN ('GUPPI', 'Rcvr_800', 'Rcvr1_2')
        ORDER BY term
        """,
    )
    by_term = {str(row["term"]): row for row in rows}
    missing = [term for term in SUPPORTED_COMPONENT_TERMS if term not in by_term]
    if missing:
        fail("Missing supported component terms in DWH15_A view: " + "; ".join(missing))
    return by_term


def open_compound_statuses(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT
            term,
            token_position,
            skip_reason,
            dwh14a_decision_status,
            dwh14a_evidence_strength,
            safe_to_promote,
            notes
        FROM qsb_v_dwh15a_skipped_deferred_candidates
        WHERE term IN ('Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
        ORDER BY term
        """,
    )
    by_term = {str(row["term"]): row for row in rows}
    missing = [term for term in OPEN_COMPOUND_LABELS if term not in by_term]
    if missing:
        fail("Missing open compound labels in DWH15_A skipped view: " + "; ".join(missing))
    return by_term


def term_occurrence_summary(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for term in SUPPORTED_COMPONENT_TERMS + OPEN_COMPOUND_LABELS:
        raw_field_hits = con.execute(
            """
            SELECT COUNT(*) AS n
            FROM raw_field_value
            WHERE CAST(raw_value AS TEXT) LIKE ?
            """,
            (f"%{term}%",),
        ).fetchone()["n"]
        raw_record_hits = con.execute(
            """
            SELECT COUNT(DISTINCT raw_record_id) AS n
            FROM raw_field_value
            WHERE CAST(raw_value AS TEXT) LIKE ?
            """,
            (f"%{term}%",),
        ).fetchone()["n"]
        rows.append(
            {
                "term": term,
                "raw_field_value_hits": int(raw_field_hits),
                "raw_record_hits": int(raw_record_hits),
            }
        )
    return rows


def build_observation_context_rows(
    con: sqlite3.Connection,
    component_by_term: dict[str, dict[str, Any]],
    compound_by_term: dict[str, dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    next_index = 1
    for context in COMPOUND_CONTEXTS:
        label = context["raw_context_label"]
        receiver = context["receiver_term"]
        backend = context["backend_term"]
        trace_rows = fetch_dicts(
            con,
            """
            SELECT
                co.observation_id,
                co.object_id AS science_object_id,
                co.processing_context_id,
                co.quality_status_id,
                co.time_context_id,
                COUNT(DISTINCT r.raw_record_id) AS source_record_count
            FROM raw_field_value AS fv
            JOIN raw_record AS r
              ON r.raw_record_id = fv.raw_record_id
            JOIN core_observation_record_link AS link
              ON link.raw_record_id = r.raw_record_id
            JOIN core_observation AS co
              ON co.observation_id = link.observation_id
            WHERE CAST(fv.raw_value AS TEXT) LIKE ?
            GROUP BY
                co.observation_id,
                co.object_id,
                co.processing_context_id,
                co.quality_status_id,
                co.time_context_id
            ORDER BY co.observation_id
            """,
            (f"%{label}%",),
        )
        for trace in trace_rows:
            receiver_status = (
                f"{component_by_term[receiver]['dwh14a_decision_status']}; "
                f"{component_by_term[receiver]['new_review_status']}"
            )
            backend_status = (
                f"{component_by_term[backend]['dwh14a_decision_status']}; "
                f"{component_by_term[backend]['new_review_status']}"
            )
            compound_status = (
                f"{compound_by_term[label]['dwh14a_decision_status']}; "
                f"{compound_by_term[label]['skip_reason']}"
            )
            rows.append(
                {
                    "shapiro_observation_context_id": (
                        f"SHAPIROMART01_OBSCTX_{next_index:03d}"
                    ),
                    "observation_id": trace["observation_id"],
                    "science_object_id": trace["science_object_id"],
                    "receiver_term": receiver,
                    "backend_term": backend,
                    "raw_context_label": label,
                    "receiver_support_status": receiver_status,
                    "backend_support_status": backend_status,
                    "compound_label_status": compound_status,
                    "processing_context_id": trace["processing_context_id"],
                    "quality_status_id": trace["quality_status_id"],
                    "time_context_id": trace["time_context_id"],
                    "source_record_count": int(trace["source_record_count"]),
                    "context_usable_status": "usable_as_supported_component_context_only",
                    "created_at_utc": created_at,
                    "notes": (
                        "Trace path exists through raw_field_value, raw_record, "
                        "core_observation_record_link, and core_observation. "
                        "Compound label remains unresolved and is not used as a "
                        "supported mapping key."
                    ),
                }
            )
            next_index += 1
    return rows


def parse_note_value(notes: str | None, key: str) -> str | None:
    if not notes:
        return None
    marker = key + "="
    if marker not in notes:
        return None
    return notes.split(marker, 1)[1].split(";", 1)[0].strip()


def raw_field_stats(
    con: sqlite3.Connection,
    field_name: str,
    line_type: str | None = None,
) -> dict[str, Any]:
    params: list[Any] = [field_name]
    line_filter = ""
    if line_type is not None:
        line_filter = "AND r.line_type = ?"
        params.append(line_type)
    row = con.execute(
        f"""
        SELECT
            COUNT(*) AS populated_row_count,
            COUNT(DISTINCT fv.raw_value) AS distinct_value_count
        FROM raw_field_value AS fv
        JOIN raw_record AS r
          ON r.raw_record_id = fv.raw_record_id
        WHERE fv.field_name = ?
          AND fv.raw_value IS NOT NULL
          AND TRIM(CAST(fv.raw_value AS TEXT)) <> ''
          {line_filter}
        """,
        tuple(params),
    ).fetchone()
    sample_values = [
        str(sample["raw_value"])
        for sample in con.execute(
            f"""
            SELECT fv.raw_value
            FROM raw_field_value AS fv
            JOIN raw_record AS r
              ON r.raw_record_id = fv.raw_record_id
            WHERE fv.field_name = ?
              AND fv.raw_value IS NOT NULL
              AND TRIM(CAST(fv.raw_value AS TEXT)) <> ''
              {line_filter}
            ORDER BY fv.raw_record_id
            LIMIT 200
            """,
            tuple(params),
        )
    ]
    if sample_values and all(NUMERIC_RE.match(value.strip()) for value in sample_values):
        storage = "numeric_text"
    elif sample_values and any(NUMERIC_RE.match(value.strip()) for value in sample_values):
        storage = "mixed_text"
    else:
        storage = "text"
    return {
        "populated_row_count": int(row["populated_row_count"]),
        "distinct_value_count": int(row["distinct_value_count"]),
        "datatype_or_storage_class": storage,
    }


def table_field_stats(
    con: sqlite3.Connection,
    table_name: str,
    field_name: str,
) -> dict[str, Any]:
    row = con.execute(
        f"""
        SELECT
            COUNT({quote_identifier(field_name)}) AS populated_row_count,
            COUNT(DISTINCT {quote_identifier(field_name)}) AS distinct_value_count
        FROM {quote_identifier(table_name)}
        WHERE {quote_identifier(field_name)} IS NOT NULL
          AND TRIM(CAST({quote_identifier(field_name)} AS TEXT)) <> ''
        """
    ).fetchone()
    sample_values = [
        str(sample[field_name])
        for sample in con.execute(
            f"""
            SELECT {quote_identifier(field_name)}
            FROM {quote_identifier(table_name)}
            WHERE {quote_identifier(field_name)} IS NOT NULL
              AND TRIM(CAST({quote_identifier(field_name)} AS TEXT)) <> ''
            LIMIT 200
            """
        )
    ]
    if sample_values and all(NUMERIC_RE.match(value.strip()) for value in sample_values):
        storage = "numeric_text"
    elif sample_values and any(NUMERIC_RE.match(value.strip()) for value in sample_values):
        storage = "mixed_text"
    else:
        storage = "text"
    return {
        "populated_row_count": int(row["populated_row_count"]),
        "distinct_value_count": int(row["distinct_value_count"]),
        "datatype_or_storage_class": storage,
    }


def add_feature_row(
    rows: list[dict[str, Any]],
    source_table: str,
    source_field: str,
    inferred_feature_family: str,
    stats: dict[str, Any],
    candidate_use: str,
    semantic_status: str,
    usable_now: int,
    limitation: str,
    created_at: str,
    notes: str,
) -> None:
    rows.append(
        {
            "feature_availability_id": f"SHAPIROMART01_FEATURE_{len(rows) + 1:03d}",
            "source_table": source_table,
            "source_field": source_field,
            "inferred_feature_family": inferred_feature_family,
            "populated_row_count": int(stats["populated_row_count"]),
            "distinct_value_count": int(stats["distinct_value_count"]),
            "datatype_or_storage_class": stats["datatype_or_storage_class"],
            "candidate_use": candidate_use,
            "semantic_status": semantic_status,
            "usable_now": int(usable_now),
            "limitation": limitation,
            "created_at_utc": created_at,
            "notes": notes,
        }
    )


def build_feature_rows(con: sqlite3.Connection, created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    add_feature_row(
        rows,
        "core_observation",
        "observation_id",
        "observation_identifier",
        table_field_stats(con, "core_observation", "observation_id"),
        "traceability_anchor",
        "available_identifier",
        1,
        "Identifier only; not a signal feature.",
        created_at,
        "Used to anchor future mart rows back to core_observation.",
    )
    add_feature_row(
        rows,
        "core_observation",
        "object_id",
        "science_object_identifier",
        table_field_stats(con, "core_observation", "object_id"),
        "same_object_grouping_context",
        "available_identifier_pending_catalog_review",
        1,
        "Science object ID is available, but external catalog mapping remains pending.",
        created_at,
        "Current object context is sufficient for cohort grouping only.",
    )
    add_feature_row(
        rows,
        "core_observation",
        "processing_context_id",
        "processing_context",
        table_field_stats(con, "core_observation", "processing_context_id"),
        "control_context",
        "placeholder_context",
        0,
        "Processing context is unresolved_placeholder in the current core row.",
        created_at,
        "Blocks a controlled processing-context comparison until reviewed.",
    )
    add_feature_row(
        rows,
        "core_observation",
        "time_context_id",
        "phase_or_time_coordinate",
        table_field_stats(con, "core_observation", "time_context_id"),
        "control_context",
        "placeholder_context",
        0,
        "Time context is an unresolved identifier, not an approved coordinate.",
        created_at,
        "No time conversion or final time-context mapping is performed here.",
    )
    add_feature_row(
        rows,
        "dim_quality_status",
        "quality_status",
        "quality_flag",
        table_field_stats(con, "dim_quality_status", "quality_status"),
        "control_context",
        "dry_run_review_status",
        0,
        "Quality status exists but is a pending/dry-run review marker.",
        created_at,
        "Blocks a quality-controlled comparison until review status is resolved.",
    )
    add_feature_row(
        rows,
        "raw_record",
        "line_type",
        "quality_flag",
        table_field_stats(con, "raw_record", "line_type"),
        "record_filter_context",
        "available_record_classification",
        1,
        "Line type helps filter records but is not a signal feature.",
        created_at,
        "Available values separate data, comment, PAR-like, blank, and malformed records.",
    )
    add_feature_row(
        rows,
        "raw_field_value",
        "raw_value where field_name=tim_token_001 and line_type=data_line",
        "observation_identifier",
        raw_field_stats(con, "tim_token_001", "data_line"),
        "raw_file_or_record_grouping_context",
        "available_unverified_identifier",
        1,
        "Filename-like values are provenance/context only.",
        created_at,
        "This row is not treated as a signal feature.",
    )
    add_feature_row(
        rows,
        "raw_field_value",
        "raw_value where field_name=tim_token_007 and line_type=data_line",
        "receiver_context",
        raw_field_stats(con, "tim_token_007", "data_line"),
        "supported_receiver_context_candidate",
        "component_supported_context_only",
        1,
        "Receiver component use is context-only and does not promote compound labels.",
        created_at,
        "Expected supported values include Rcvr_800 and Rcvr1_2.",
    )
    add_feature_row(
        rows,
        "raw_field_value",
        "raw_value where field_name=tim_token_009 and line_type=data_line",
        "backend_context",
        raw_field_stats(con, "tim_token_009", "data_line"),
        "supported_backend_context_candidate",
        "component_supported_context_only",
        1,
        "Backend component use is context-only and does not finalize a compound label.",
        created_at,
        "Expected supported value is GUPPI.",
    )
    add_feature_row(
        rows,
        "raw_field_value",
        "raw_value where field_name=tim_token_011 and line_type=data_line",
        "unknown_or_unresolved",
        raw_field_stats(con, "tim_token_011", "data_line"),
        "unresolved_raw_context_label_only",
        "compound_label_open",
        0,
        "Compound labels remain open and must not be used as supported mapping keys.",
        created_at,
        "Allowed only as visible unresolved context.",
    )

    data_dictionary_rows = fetch_dicts(
        con,
        """
        SELECT token_position, structural_role, mapping_status, review_status, notes
        FROM map_token_dictionary
        WHERE line_family = 'data_line'
          AND structural_role = 'variable_token'
        ORDER BY CAST(REPLACE(token_position, 'tim_token_', '') AS INTEGER)
        """,
    )
    for dict_row in data_dictionary_rows:
        token = str(dict_row["token_position"])
        label = parse_note_value(str(dict_row["notes"] or ""), "profile_structural_label") or ""
        if "numeric" not in label:
            continue
        stats = raw_field_stats(con, token, "data_line")
        add_feature_row(
            rows,
            "raw_field_value",
            f"raw_value where field_name={token} and line_type=data_line",
            "unknown_or_unresolved",
            stats,
            "future_fingerprint_candidate_after_semantic_review",
            "unresolved_structural_numeric_token",
            0,
            "Numeric-like token exists, but its semantic role is not approved here.",
            created_at,
            (
                f"Dictionary status={dict_row['mapping_status']}; "
                f"review={dict_row['review_status']}; structural_label={label}."
            ),
        )
    return rows


def processing_match_status(context_a: dict[str, Any], context_b: dict[str, Any]) -> str:
    if context_a["processing_context_id"] == context_b["processing_context_id"]:
        if str(context_a["processing_context_id"]) == "unresolved_placeholder":
            return "matched_placeholder_unresolved"
        return "matched"
    return "different_or_missing"


def quality_match_status(context_a: dict[str, Any], context_b: dict[str, Any]) -> str:
    if context_a["quality_status_id"] == context_b["quality_status_id"]:
        if str(context_a["quality_status_id"]) == "dry_run_unreviewed":
            return "matched_dry_run_unreviewed"
        return "matched"
    return "different_or_missing"


def time_match_status(context_a: dict[str, Any], context_b: dict[str, Any]) -> str:
    if context_a["time_context_id"] == context_b["time_context_id"]:
        if str(context_a["time_context_id"]) == "unresolved_placeholder":
            return "matched_placeholder_unresolved"
        return "matched"
    return "different_or_missing"


def build_comparison_rows(
    observation_rows: list[dict[str, Any]],
    feature_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    future_feature_count = sum(
        1
        for row in feature_rows
        if row["candidate_use"] == "future_fingerprint_candidate_after_semantic_review"
    )
    rows: list[dict[str, Any]] = []
    ordered = sorted(
        observation_rows,
        key=lambda row: (str(row["science_object_id"]), str(row["backend_term"]), str(row["receiver_term"])),
    )
    for i, context_a in enumerate(ordered):
        for context_b in ordered[i + 1 :]:
            if context_a["science_object_id"] != context_b["science_object_id"]:
                continue
            if context_a["backend_term"] != context_b["backend_term"]:
                continue
            if context_a["receiver_term"] == context_b["receiver_term"]:
                continue

            p_status = processing_match_status(context_a, context_b)
            q_status = quality_match_status(context_a, context_b)
            t_status = time_match_status(context_a, context_b)
            blockers: list[str] = []
            if "unresolved" in p_status:
                blockers.append("processing_context_unresolved")
            if "dry_run" in q_status or "unresolved" in q_status:
                blockers.append("quality_context_unreviewed")
            if "unresolved" in t_status:
                blockers.append("time_context_unresolved")
            if future_feature_count <= 0:
                blockers.append("missing_candidate_signal_fields")
            else:
                blockers.append("candidate_feature_semantics_unresolved")

            readiness = "partial_context_only"
            if future_feature_count <= 0:
                readiness = "blocked_missing_signal_features"
            elif p_status == "different_or_missing" or q_status == "different_or_missing" or t_status == "different_or_missing":
                readiness = "blocked_missing_context"

            rows.append(
                {
                    "comparison_cohort_id": f"SHAPIROMART01_COHORT_{len(rows) + 1:03d}",
                    "science_object_id": context_a["science_object_id"],
                    "context_a_observation_id": context_a["observation_id"],
                    "context_b_observation_id": context_b["observation_id"],
                    "context_a_receiver": context_a["receiver_term"],
                    "context_b_receiver": context_b["receiver_term"],
                    "shared_backend_term": context_a["backend_term"],
                    "processing_match_status": p_status,
                    "quality_match_status": q_status,
                    "time_context_match_status": t_status,
                    "available_feature_count": future_feature_count,
                    "comparison_readiness_status": readiness,
                    "blocking_reason": "; ".join(blockers),
                    "created_at_utc": created_at,
                    "notes": (
                        "Cohort is formed from supported receiver components sharing "
                        "the same science object and backend context. It is not an "
                        "analysis-ready cohort."
                    ),
                }
            )
    return rows


def build_control_gap_rows(
    comparison_rows: list[dict[str, Any]],
    observation_rows: list[dict[str, Any]],
    feature_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    related_id = comparison_rows[0]["comparison_cohort_id"] if comparison_rows else None
    future_features = [
        row
        for row in feature_rows
        if row["candidate_use"] == "future_fingerprint_candidate_after_semantic_review"
    ]
    have_contexts = bool(observation_rows)
    gap_specs: list[tuple[str, str, str, str, str, str]] = []
    if not have_contexts:
        gap_specs.append(
            (
                "supported_context_trace",
                "raw/core trace for supported receiver/backend contexts",
                "missing",
                "blocking",
                "Review raw/core linkage and mapping state before cohort construction.",
                "No traceable supported context rows were found.",
            )
        )
    gap_specs.extend(
        [
            (
                "processing_control",
                "reviewed processing_context_id or comparable processing label",
                "unresolved_placeholder",
                "blocking",
                "Resolve or approve the processing context before comparison.",
                "Current core_observation processing context is a placeholder.",
            ),
            (
                "quality_control",
                "reviewed quality status usable for filtering or matching",
                "dry_run_unreviewed",
                "blocking",
                "Review quality status and define usable/excluded record classes.",
                "Current quality status is not a reviewed comparison control.",
            ),
            (
                "time_context_control",
                "reviewed time/epoch context identifier or approved time grouping",
                "unresolved_placeholder",
                "blocking",
                "Resolve the time context before any temporal comparison.",
                "Current time_context_id is a placeholder only.",
            ),
            (
                "feature_semantic_control",
                "approved feature dictionary for candidate data-line numeric tokens",
                (
                    f"{len(future_features)} unresolved structural numeric token "
                    "candidates"
                ),
                "blocking",
                "Create a minimal reviewed feature dictionary for the candidate tokens.",
                "Numeric-like fields exist, but DWH mapping still marks semantics as needing review.",
            ),
            (
                "uncertainty_or_weight_control",
                "reviewed uncertainty/weight feature role",
                "not_approved",
                "blocking",
                "Identify whether any existing token may be used as uncertainty or weight.",
                "No uncertainty/weight role is approved by SHAPIROMART01.",
            ),
            (
                "compound_label_boundary",
                "direct evidence for exact compound labels before use as mapping keys",
                "compound_labels_open",
                "blocking_for_compound_key_use",
                "Keep compound labels visible but unresolved unless reviewed later.",
                "Supported component context does not support compound-label promotion.",
            ),
        ]
    )
    rows: list[dict[str, Any]] = []
    for index, spec in enumerate(gap_specs, start=1):
        gap_type, required, availability, status, action, notes = spec
        rows.append(
            {
                "control_gap_id": f"SHAPIROMART01_GAP_{index:03d}",
                "related_cohort_id": related_id,
                "gap_type": gap_type,
                "required_control_or_field": required,
                "current_availability": availability,
                "blocking_status": status,
                "recommended_next_action": action,
                "created_at_utc": created_at,
                "notes": notes,
            }
        )
    return rows


def build_next_step_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "SHAPIROMART02_RECOMMENDED_001",
            "recommended_next_step": (
                "Create a minimal reviewed feature dictionary for the data-line "
                "numeric token candidates and the processing/time/quality controls "
                "before any fingerprint comparison."
            ),
            "why_this_step": (
                "The first receiver-context cohort can be formed, but feature "
                "semantics and required controls remain unresolved."
            ),
            "db_write_expected": "yes_in_separate_explicit_task",
            "claim_boundary": "Feature-role review is still not a result analysis.",
        }
    ]


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS mart_shapiro_observation_context (
            shapiro_observation_context_id TEXT PRIMARY KEY,
            observation_id TEXT,
            science_object_id TEXT,
            receiver_term TEXT,
            backend_term TEXT,
            raw_context_label TEXT,
            receiver_support_status TEXT,
            backend_support_status TEXT,
            compound_label_status TEXT,
            processing_context_id TEXT,
            quality_status_id TEXT,
            time_context_id TEXT,
            source_record_count INTEGER,
            context_usable_status TEXT,
            created_at_utc TEXT,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_feature_availability (
            feature_availability_id TEXT PRIMARY KEY,
            source_table TEXT NOT NULL,
            source_field TEXT NOT NULL,
            inferred_feature_family TEXT NOT NULL,
            populated_row_count INTEGER NOT NULL,
            distinct_value_count INTEGER,
            datatype_or_storage_class TEXT,
            candidate_use TEXT,
            semantic_status TEXT NOT NULL,
            usable_now INTEGER NOT NULL,
            limitation TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_comparison_cohort (
            comparison_cohort_id TEXT PRIMARY KEY,
            science_object_id TEXT,
            context_a_observation_id TEXT,
            context_b_observation_id TEXT,
            context_a_receiver TEXT,
            context_b_receiver TEXT,
            shared_backend_term TEXT,
            processing_match_status TEXT,
            quality_match_status TEXT,
            time_context_match_status TEXT,
            available_feature_count INTEGER,
            comparison_readiness_status TEXT NOT NULL,
            blocking_reason TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_control_gap (
            control_gap_id TEXT PRIMARY KEY,
            related_cohort_id TEXT,
            gap_type TEXT NOT NULL,
            required_control_or_field TEXT NOT NULL,
            current_availability TEXT NOT NULL,
            blocking_status TEXT NOT NULL,
            recommended_next_action TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS shapiromart01_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            observation_context_count INTEGER,
            feature_availability_count INTEGER,
            comparison_cohort_count INTEGER,
            ready_cohort_count INTEGER,
            control_gap_count INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT
        );
        """
    )


def clear_target_tables(con: sqlite3.Connection) -> None:
    for table in reversed(TARGET_TABLES):
        if object_exists(con, table, "table"):
            con.execute(f"DELETE FROM {quote_identifier(table)}")


def insert_rows(con: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    placeholders = ", ".join(["?"] * len(fieldnames))
    columns = ", ".join(quote_identifier(field) for field in fieldnames)
    sql = f"INSERT INTO {quote_identifier(table)} ({columns}) VALUES ({placeholders})"
    con.executemany(sql, [tuple(row[field] for field in fieldnames) for row in rows])


def create_views(con: sqlite3.Connection) -> None:
    for view in TARGET_VIEWS:
        con.execute(f"DROP VIEW IF EXISTS {quote_identifier(view)}")
    con.executescript(
        """
        CREATE VIEW qsb_v_shapiromart01_dashboard AS
        SELECT 'observation_context_count' AS metric_name,
               CAST(COUNT(*) AS TEXT) AS metric_value,
               'mart_shapiro_observation_context' AS metric_source
        FROM mart_shapiro_observation_context
        UNION ALL
        SELECT 'feature_availability_count',
               CAST(COUNT(*) AS TEXT),
               'mart_shapiro_feature_availability'
        FROM mart_shapiro_feature_availability
        UNION ALL
        SELECT 'comparison_cohort_count',
               CAST(COUNT(*) AS TEXT),
               'mart_shapiro_comparison_cohort'
        FROM mart_shapiro_comparison_cohort
        UNION ALL
        SELECT 'ready_cohort_count',
               CAST(COUNT(*) AS TEXT),
               'mart_shapiro_comparison_cohort'
        FROM mart_shapiro_comparison_cohort
        WHERE comparison_readiness_status = 'ready_for_feature_definition'
        UNION ALL
        SELECT 'control_gap_count',
               CAST(COUNT(*) AS TEXT),
               'mart_shapiro_control_gap'
        FROM mart_shapiro_control_gap
        UNION ALL
        SELECT 'compound_label_boundary',
               'open_not_promoted',
               'qsb_v_dwh15a_skipped_deferred_candidates';

        CREATE VIEW qsb_v_shapiromart01_supported_contexts AS
        SELECT
            shapiro_observation_context_id,
            observation_id,
            science_object_id,
            receiver_term,
            backend_term,
            raw_context_label,
            receiver_support_status,
            backend_support_status,
            compound_label_status,
            source_record_count,
            context_usable_status,
            notes
        FROM mart_shapiro_observation_context
        ORDER BY receiver_term, backend_term, raw_context_label;

        CREATE VIEW qsb_v_shapiromart01_feature_availability AS
        SELECT
            feature_availability_id,
            source_table,
            source_field,
            inferred_feature_family,
            populated_row_count,
            distinct_value_count,
            datatype_or_storage_class,
            candidate_use,
            semantic_status,
            usable_now,
            limitation
        FROM mart_shapiro_feature_availability
        ORDER BY feature_availability_id;

        CREATE VIEW qsb_v_shapiromart01_comparison_readiness AS
        SELECT
            comparison_readiness_status,
            COUNT(*) AS cohort_count,
            SUM(available_feature_count) AS total_available_feature_count,
            GROUP_CONCAT(DISTINCT blocking_reason) AS blocking_reasons
        FROM mart_shapiro_comparison_cohort
        GROUP BY comparison_readiness_status
        ORDER BY comparison_readiness_status;

        CREATE VIEW qsb_v_shapiromart01_blocking_gaps AS
        SELECT
            control_gap_id,
            related_cohort_id,
            gap_type,
            required_control_or_field,
            current_availability,
            blocking_status,
            recommended_next_action,
            notes
        FROM mart_shapiro_control_gap
        WHERE blocking_status LIKE 'blocking%'
        ORDER BY control_gap_id;
        """
    )


def query_table_rows(con: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(table)} ORDER BY 1")


def validate_new_objects(con: sqlite3.Connection) -> dict[str, Any]:
    missing: list[str] = []
    table_counts: dict[str, int] = {}
    for table in TARGET_TABLES:
        if not object_exists(con, table, "table"):
            missing.append(f"table:{table}")
        else:
            table_counts[table] = table_count(con, table)
    view_counts: dict[str, int] = {}
    for view in TARGET_VIEWS:
        if not object_exists(con, view, "view"):
            missing.append(f"view:{view}")
        else:
            row = con.execute(f"SELECT COUNT(*) AS n FROM {quote_identifier(view)}").fetchone()
            view_counts[view] = int(row["n"])
    if missing:
        fail("Missing expected SHAPIROMART01 objects: " + "; ".join(missing))
    return {"table_counts": table_counts, "view_counts": view_counts}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def write_readout(
    path: Path,
    summary: dict[str, Any],
    observation_rows: list[dict[str, Any]],
    feature_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    control_gap_rows: list[dict[str, Any]],
    next_step_rows: list[dict[str, str]],
) -> None:
    supported_terms_in_records = ", ".join(
        row["term"]
        for row in summary["term_occurrence_summary"]
        if row["term"] in SUPPORTED_COMPONENT_TERMS and row["raw_record_hits"] > 0
    )
    science_objects = ", ".join(
        sorted({str(row["science_object_id"]) for row in observation_rows})
    ) or "none"
    candidate_fields = [
        row
        for row in feature_rows
        if row["candidate_use"] == "future_fingerprint_candidate_after_semantic_review"
    ]
    ready_count = sum(
        1
        for row in comparison_rows
        if row["comparison_readiness_status"] == "ready_for_feature_definition"
    )
    blocked_or_partial = len(comparison_rows) - ready_count
    main_gaps = "; ".join(row["gap_type"] for row in control_gap_rows[:6])
    next_step = next_step_rows[0]["recommended_next_step"] if next_step_rows else "none"

    lines = [
        "# QSB-SHAPIROMART01 Minimal Cohort and Feature Availability Build",
        "",
        "## 1. Executive summary",
        "",
        (
            "Befund: SHAPIROMART01 created the smallest current mart substrate for "
            "supported receiver/backend contexts and future feature-definition review."
        ),
        "",
        f"- Supported observation contexts found: {len(observation_rows)}",
        f"- Supported component terms occurring in actual records: {supported_terms_in_records}",
        f"- Traceable science objects: {science_objects}",
        f"- Candidate future fingerprint fields found: {len(candidate_fields)}",
        f"- Comparison cohorts formed: {len(comparison_rows)}",
        f"- Ready cohorts: {ready_count}",
        f"- Partial or blocked cohorts: {blocked_or_partial}",
        "",
        "## 2. Data substrate used",
        "",
        f"- Live DB: `{summary['paths']['live_db']}`",
        f"- Workcopy DB: `{summary['paths']['workcopy_db']}`",
        f"- Output root: `{summary['paths']['output_root']}`",
        (
            "- Input substrate: existing workcopy DB tables/views only; no raw "
            "TIM/PAR file reads and no report-file inputs."
        ),
        "",
        "## 3. Supported observation contexts",
        "",
    ]
    if observation_rows:
        for row in observation_rows:
            lines.append(
                "- {shapiro_observation_context_id}: object={science_object_id}; "
                "receiver={receiver_term}; backend={backend_term}; raw_label={raw_context_label}; "
                "records={source_record_count}; status={context_usable_status}".format(**row)
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## 4. Component occurrence and compound-label boundary",
            "",
            SUPPORT_BOUNDARY,
            "",
        ]
    )
    for row in summary["term_occurrence_summary"]:
        lines.append(
            "- {term}: raw_field_value_hits={raw_field_value_hits}; raw_record_hits={raw_record_hits}".format(**row)
        )

    lines.extend(["", "## 5. Science-object trace", ""])
    lines.append(
        (
            f"Science-object trace currently reaches `{science_objects}` through "
            "raw_field_value -> raw_record -> core_observation_record_link -> core_observation."
        )
        if science_objects != "none"
        else "No supported science-object trace was found."
    )

    lines.extend(["", "## 6. Candidate signal/information fields actually available", ""])
    if candidate_fields:
        for row in candidate_fields:
            lines.append(
                "- {source_field}: rows={populated_row_count}; distinct={distinct_value_count}; "
                "storage={datatype_or_storage_class}; semantic_status={semantic_status}; "
                "usable_now={usable_now}".format(**row)
            )
    else:
        lines.append("- none")

    lines.extend(["", "## 7. Comparison cohorts", ""])
    if comparison_rows:
        for row in comparison_rows:
            lines.append(
                "- {comparison_cohort_id}: object={science_object_id}; "
                "{context_a_receiver} vs {context_b_receiver}; backend={shared_backend_term}; "
                "features={available_feature_count}; readiness={comparison_readiness_status}; "
                "blocking={blocking_reason}".format(**row)
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## 8. What prevents the first fingerprint comparison",
            "",
            f"Main blocking gaps: {main_gaps}",
            "",
        ]
    )
    for row in control_gap_rows:
        lines.append(
            "- {gap_type}: availability={current_availability}; action={recommended_next_action}".format(**row)
        )

    lines.extend(
        [
            "",
            "## 9. Single next concrete research step",
            "",
            next_step,
            "",
            "## 10. Validation and claim boundary",
            "",
            f"- Live DB unchanged: {summary['validation']['live_db_unchanged']}",
            f"- Workcopy DB modified: {summary['validation']['workcopy_db_modified']}",
            f"- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}",
            f"- Workcopy foreign-key violations: {summary['validation']['workcopy_foreign_key_violation_count']}",
            f"- Existing DWH table row counts unchanged: {summary['validation']['existing_table_counts_unchanged']}",
            f"- Supported/open mapping separation preserved: {summary['validation']['mapping_separation_preserved']}",
            f"- Compound labels not promoted: {summary['validation']['compound_labels_not_promoted']}",
            "",
            CLAIM_BOUNDARY,
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(
    output_root: Path,
    summary: dict[str, Any],
    observation_rows: list[dict[str, Any]],
    feature_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    control_gap_rows: list[dict[str, Any]],
    next_step_rows: list[dict[str, str]],
) -> None:
    paths = output_paths(output_root)
    write_csv(
        paths[OBS_CONTEXT_CSV],
        observation_rows,
        [
            "shapiro_observation_context_id",
            "observation_id",
            "science_object_id",
            "receiver_term",
            "backend_term",
            "raw_context_label",
            "receiver_support_status",
            "backend_support_status",
            "compound_label_status",
            "processing_context_id",
            "quality_status_id",
            "time_context_id",
            "source_record_count",
            "context_usable_status",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[FEATURE_CSV],
        feature_rows,
        [
            "feature_availability_id",
            "source_table",
            "source_field",
            "inferred_feature_family",
            "populated_row_count",
            "distinct_value_count",
            "datatype_or_storage_class",
            "candidate_use",
            "semantic_status",
            "usable_now",
            "limitation",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[COMPARISON_CSV],
        comparison_rows,
        [
            "comparison_cohort_id",
            "science_object_id",
            "context_a_observation_id",
            "context_b_observation_id",
            "context_a_receiver",
            "context_b_receiver",
            "shared_backend_term",
            "processing_match_status",
            "quality_match_status",
            "time_context_match_status",
            "available_feature_count",
            "comparison_readiness_status",
            "blocking_reason",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[CONTROL_GAP_CSV],
        control_gap_rows,
        [
            "control_gap_id",
            "related_cohort_id",
            "gap_type",
            "required_control_or_field",
            "current_availability",
            "blocking_status",
            "recommended_next_action",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[NEXT_STEP_CSV],
        next_step_rows,
        [
            "next_step_id",
            "recommended_next_step",
            "why_this_step",
            "db_write_expected",
            "claim_boundary",
        ],
    )
    write_json(paths[SUMMARY_JSON], summary)
    write_readout(
        paths[READOUT_MD],
        summary,
        observation_rows,
        feature_rows,
        comparison_rows,
        control_gap_rows,
        next_step_rows,
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_paths(args)

    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)

    with connect_readonly(args.live_db) as live_con:
        live_integrity = integrity_check(live_con)
        live_fk = foreign_key_violations(live_con)
        if live_integrity != "ok":
            fail(f"Live DB integrity_check failed: {live_integrity}")
        if live_fk:
            fail(f"Live DB foreign-key violations: {len(live_fk)}")

    created_at = utc_now()
    run_id = "SHAPIROMART01_RUN_001"
    new_object_validation: dict[str, Any] = {}

    with connect_writable(args.workcopy_db) as con:
        before_objects = object_names(con)
        before_table_counts = existing_table_counts(con)
        before_mapping_digest = stable_digest(mapping_separation_rows(con))

        required_object_validation = validate_required_objects(con)
        existing_target_state = validate_existing_target_state(con, args.allow_existing)
        pre_integrity = integrity_check(con)
        pre_fk = foreign_key_violations(con)
        if pre_integrity != "ok":
            fail(f"Workcopy DB integrity_check failed before build: {pre_integrity}")
        if pre_fk:
            fail(f"Workcopy DB foreign-key violations before build: {len(pre_fk)}")

        term_summary = term_occurrence_summary(con)
        component_by_term = component_statuses(con)
        compound_by_term = open_compound_statuses(con)

        observation_rows = build_observation_context_rows(
            con, component_by_term, compound_by_term, created_at
        )
        feature_rows = build_feature_rows(con, created_at)
        comparison_rows = build_comparison_rows(observation_rows, feature_rows, created_at)
        control_gap_rows = build_control_gap_rows(
            comparison_rows, observation_rows, feature_rows, created_at
        )
        next_step_rows = build_next_step_rows()
        ready_count = sum(
            1
            for row in comparison_rows
            if row["comparison_readiness_status"] == "ready_for_feature_definition"
        )

        try:
            con.execute("BEGIN")
            create_tables(con)
            if args.allow_existing:
                clear_target_tables(con)
            insert_rows(con, "mart_shapiro_observation_context", observation_rows)
            insert_rows(con, "mart_shapiro_feature_availability", feature_rows)
            insert_rows(con, "mart_shapiro_comparison_cohort", comparison_rows)
            insert_rows(con, "mart_shapiro_control_gap", control_gap_rows)
            run_log_rows = [
                {
                    "run_id": run_id,
                    "run_timestamp_utc": created_at,
                    "live_db_modified": 0,
                    "workcopy_db_modified": 1,
                    "observation_context_count": len(observation_rows),
                    "feature_availability_count": len(feature_rows),
                    "comparison_cohort_count": len(comparison_rows),
                    "ready_cohort_count": ready_count,
                    "control_gap_count": len(control_gap_rows),
                    "integrity_check_result": "pending_post_commit_validation",
                    "foreign_key_violation_count": -1,
                    "notes": CLAIM_BOUNDARY,
                }
            ]
            insert_rows(con, "shapiromart01_run_log", run_log_rows)
            create_views(con)
            con.commit()
        except Exception:
            con.rollback()
            raise

        post_integrity = integrity_check(con)
        post_fk = foreign_key_violations(con)
        if post_integrity != "ok":
            fail(f"Workcopy DB integrity_check failed after build: {post_integrity}")
        if post_fk:
            fail(f"Workcopy DB foreign-key violations after build: {len(post_fk)}")

        con.execute(
            """
            UPDATE shapiromart01_run_log
            SET integrity_check_result = ?,
                foreign_key_violation_count = ?
            WHERE run_id = ?
            """,
            (post_integrity, len(post_fk), run_id),
        )
        con.commit()

        new_object_validation = validate_new_objects(con)
        db_observation_rows = query_table_rows(con, "mart_shapiro_observation_context")
        db_feature_rows = query_table_rows(con, "mart_shapiro_feature_availability")
        db_comparison_rows = query_table_rows(con, "mart_shapiro_comparison_cohort")
        db_control_gap_rows = query_table_rows(con, "mart_shapiro_control_gap")
        db_run_log_rows = query_table_rows(con, "shapiromart01_run_log")

        after_objects = object_names(con)
        after_table_counts = existing_table_counts(con)
        after_mapping_rows = mapping_separation_rows(con)
        after_mapping_digest = stable_digest(after_mapping_rows)

        existing_names_before = {(row["type"], row["name"]) for row in before_objects}
        existing_names_after = {(row["type"], row["name"]) for row in after_objects}
        existing_objects_preserved = existing_names_before.issubset(existing_names_after)
        existing_table_counts_unchanged = before_table_counts == after_table_counts
        mapping_separation_preserved = before_mapping_digest == after_mapping_digest
        supported_terms_after = {
            row["term"]
            for row in after_mapping_rows
            if row["separation_class"] == "supported"
        }
        compound_labels_not_promoted = not any(
            label in supported_terms_after for label in OPEN_COMPOUND_LABELS
        )

    live_after = db_state(args.live_db)
    workcopy_after = db_state(args.workcopy_db)
    live_db_unchanged = live_before == live_after
    workcopy_db_modified = workcopy_before != workcopy_after
    if not live_db_unchanged:
        fail("Live DB checksum/stat changed during SHAPIROMART01.")
    if not workcopy_db_modified:
        fail("Workcopy DB was not modified; expected SHAPIROMART01 target objects to be added.")

    summary: dict[str, Any] = {
        "script_name": SCRIPT_NAME,
        "task": "QSB-SHAPIROMART01",
        "mode": "minimal_cohort_feature_build",
        "paths": {
            "live_db": str(args.live_db),
            "workcopy_db": str(args.workcopy_db),
            "output_root": str(args.output_root),
        },
        "counts": {
            "observation_context_count": len(db_observation_rows),
            "feature_availability_count": len(db_feature_rows),
            "future_fingerprint_candidate_field_count": sum(
                1
                for row in db_feature_rows
                if row["candidate_use"] == "future_fingerprint_candidate_after_semantic_review"
            ),
            "comparison_cohort_count": len(db_comparison_rows),
            "ready_cohort_count": sum(
                1
                for row in db_comparison_rows
                if row["comparison_readiness_status"] == "ready_for_feature_definition"
            ),
            "control_gap_count": len(db_control_gap_rows),
        },
        "term_occurrence_summary": term_summary,
        "validation": {
            "live_integrity_check": live_integrity,
            "live_foreign_key_violation_count": len(live_fk),
            "live_db_unchanged": live_db_unchanged,
            "workcopy_db_modified": workcopy_db_modified,
            "workcopy_integrity_check": post_integrity,
            "workcopy_foreign_key_violation_count": len(post_fk),
            "required_objects": required_object_validation,
            "existing_target_state": existing_target_state,
            "new_objects": new_object_validation,
            "existing_objects_preserved": existing_objects_preserved,
            "existing_table_counts_unchanged": existing_table_counts_unchanged,
            "mapping_separation_preserved": mapping_separation_preserved,
            "compound_labels_not_promoted": compound_labels_not_promoted,
            "live_db_state_before": live_before,
            "live_db_state_after": live_after,
            "workcopy_db_state_before": workcopy_before,
            "workcopy_db_state_after": workcopy_after,
        },
        "workcopy_modified_objects": TARGET_TABLES + TARGET_VIEWS,
        "observation_context_rows": db_observation_rows,
        "feature_availability_rows": db_feature_rows,
        "comparison_cohort_rows": db_comparison_rows,
        "control_gap_rows": db_control_gap_rows,
        "run_log_rows": db_run_log_rows,
        "next_step_rows": next_step_rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "warnings": [
            "Compound labels are visible only as unresolved raw/context labels.",
            "Candidate numeric fields remain unresolved structural tokens until reviewed.",
            "No cohort is marked analysis-ready by SHAPIROMART01.",
        ],
    }

    if not summary["validation"]["existing_objects_preserved"]:
        fail("Existing DB objects were not preserved.")
    if not summary["validation"]["existing_table_counts_unchanged"]:
        fail("Existing DWH table row counts changed.")
    if not summary["validation"]["mapping_separation_preserved"]:
        fail("Supported/open mapping separation changed.")
    if not summary["validation"]["compound_labels_not_promoted"]:
        fail("Compound label appeared in supported mapping terms after build.")

    write_outputs(
        args.output_root,
        summary,
        db_observation_rows,
        db_feature_rows,
        db_comparison_rows,
        db_control_gap_rows,
        next_step_rows,
    )

    return {
        "summary": summary,
        "output_files": {name: str(path) for name, path in output_paths(args.output_root).items()},
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build the QSB-SHAPIROMART01 minimal cohort and feature availability "
            "substrate in the existing workcopy DB."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing SHAPIROMART01 output files.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow an explicit rerun over existing SHAPIROMART01 target tables.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    summary = result["summary"]
    counts = summary["counts"]
    print("QSB-SHAPIROMART01 minimal cohort and feature build complete.")
    print(f"Observation contexts: {counts['observation_context_count']}")
    print(f"Feature availability rows: {counts['feature_availability_count']}")
    print(
        "Future fingerprint candidate fields: "
        f"{counts['future_fingerprint_candidate_field_count']}"
    )
    print(f"Comparison cohorts: {counts['comparison_cohort_count']}")
    print(f"Ready cohorts: {counts['ready_cohort_count']}")
    print(f"Control gaps: {counts['control_gap_count']}")
    print(f"Live DB unchanged: {summary['validation']['live_db_unchanged']}")
    print(f"Workcopy DB modified: {summary['validation']['workcopy_db_modified']}")
    print(f"Output root: {summary['paths']['output_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
