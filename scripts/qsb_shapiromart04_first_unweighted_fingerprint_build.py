#!/usr/bin/env python3
"""QSB-SHAPIROMART04: first unweighted structural fingerprint build.

This script builds the first four-field unweighted structural fingerprint table
inside the existing workcopy DB. It uses only existing DB tables/views as input,
keeps the unresolved compound labels as labels only, and writes descriptive
summaries without timing, model, inference, or interpretive quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart04_first_unweighted_fingerprint_build.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART04_FIRST_UNWEIGHTED_FINGERPRINT"
)

READOUT_MD = "shapiromart04_readout.md"
SUMMARY_JSON = "shapiromart04_summary.json"
CONTEXT_SUMMARY_CSV = "shapiromart04_fingerprint_context_summary.csv"
CONTEXT_DIFFERENCE_CSV = "shapiromart04_fingerprint_context_difference.csv"
BUILD_GAPS_CSV = "shapiromart04_fingerprint_build_gaps.csv"
SAMPLE_FINGERPRINTS_CSV = "shapiromart04_sample_fingerprints.csv"
NEXT_STEP_CSV = "shapiromart04_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    CONTEXT_SUMMARY_CSV,
    CONTEXT_DIFFERENCE_CSV,
    BUILD_GAPS_CSV,
    SAMPLE_FINGERPRINTS_CSV,
    NEXT_STEP_CSV,
]

TARGET_TABLES = [
    "mart_shapiro_structural_fingerprint",
    "mart_shapiro_fingerprint_context_summary",
    "mart_shapiro_fingerprint_context_difference",
    "mart_shapiro_fingerprint_build_gap",
    "shapiromart04_run_log",
]

TARGET_VIEWS = [
    "qsb_v_shapiromart04_fingerprint_dashboard",
    "qsb_v_shapiromart04_complete_fingerprints",
    "qsb_v_shapiromart04_context_summary",
    "qsb_v_shapiromart04_context_difference",
    "qsb_v_shapiromart04_build_gaps",
]

PRIMARY_REQUIRED_OBJECTS = [
    ("raw_record", "table"),
    ("raw_field_value", "table"),
    ("core_observation_record_link", "table"),
    ("mart_shapiro_observation_context", "table"),
    ("mart_shapiro_feature_dictionary", "table"),
    ("qsb_v_shapiromart03_first_fingerprint_features", "view"),
    ("qsb_v_shapiromart01_supported_contexts", "view"),
]

SHAPIROMART01_TABLES = [
    "mart_shapiro_observation_context",
    "mart_shapiro_feature_availability",
    "mart_shapiro_comparison_cohort",
    "mart_shapiro_control_gap",
    "shapiromart01_run_log",
]

SHAPIROMART02_TABLES = [
    "mart_shapiro_numeric_field_profile",
    "mart_shapiro_numeric_field_pair_relation",
    "mart_shapiro_numeric_field_review",
    "shapiromart02_run_log",
]

SHAPIROMART03_TABLES = [
    "mart_shapiro_feature_dictionary",
    "mart_shapiro_feature_exclusion",
    "shapiromart03_run_log",
]

PRIOR_TABLE_SETS = {
    "SHAPIROMART01": SHAPIROMART01_TABLES,
    "SHAPIROMART02": SHAPIROMART02_TABLES,
    "SHAPIROMART03": SHAPIROMART03_TABLES,
}

CONTEXT_A_RECEIVER = "Rcvr_800"
CONTEXT_B_RECEIVER = "Rcvr1_2"
SUPPORTED_BACKEND = "GUPPI"
EXPECTED_CONTEXTS = {
    CONTEXT_A_RECEIVER: {
        "backend_term": SUPPORTED_BACKEND,
        "raw_context_label": "Rcvr_800_GUPPI",
        "source_record_count": 5143,
    },
    CONTEXT_B_RECEIVER: {
        "backend_term": SUPPORTED_BACKEND,
        "raw_context_label": "Rcvr1_2_GUPPI",
        "source_record_count": 5799,
    },
}
CONTEXT_ORDER = {
    CONTEXT_A_RECEIVER: 1,
    CONTEXT_B_RECEIVER: 2,
}

FINGERPRINT_TOKENS = [
    "tim_token_002",
    "tim_token_003",
    "tim_token_029",
    "tim_token_033",
]
AUXILIARY_TOKENS = [
    "tim_token_004",
    "tim_token_031",
    "tim_token_035",
]
ALL_TOKENS = [
    "tim_token_002",
    "tim_token_003",
    "tim_token_004",
    "tim_token_029",
    "tim_token_031",
    "tim_token_033",
    "tim_token_035",
]

TOKEN_TO_COLUMN = {
    "tim_token_002": "coordinate_primary",
    "tim_token_003": "coordinate_secondary",
    "tim_token_029": "signal_value_primary",
    "tim_token_033": "signal_value_secondary",
    "tim_token_004": "auxiliary_uncertainty_primary",
    "tim_token_031": "auxiliary_uncertainty_secondary",
    "tim_token_035": "auxiliary_uncertainty_tertiary",
}

FINGERPRINT_STATUSES = {
    "complete_unweighted_fingerprint",
    "partial_missing_fingerprint_field",
    "blocked_duplicate_token_value",
    "blocked_non_numeric_value",
    "unsupported_context",
}

DIFFERENCE_STATUSES = {
    "descriptive_difference_available",
    "insufficient_complete_records",
    "context_alignment_blocked",
}

INTERPRETATION_STATUS = "descriptive_only_no_physical_interpretation"
NEXT_STEP = (
    "Assess within-context stability and between-context separability of the "
    "unweighted four-dimensional fingerprints using descriptive, "
    "non-inferential measures only."
)

NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")

CLAIM_BOUNDARY = (
    "SHAPIROMART04 builds descriptive unweighted structural fingerprints only. "
    "It does not compute TOAs, delays, timing residuals, model quantities, "
    "statistical significance, or assign physical interpretation."
)


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


def parse_numeric(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or not NUMERIC_RE.match(text):
        return None
    try:
        parsed = float(text)
    except ValueError:
        return None
    if not math.isfinite(parsed):
        return None
    return parsed


def safe_mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def safe_median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def safe_stddev(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    return statistics.pstdev(values)


def safe_min(values: list[float]) -> float | None:
    return min(values) if values else None


def safe_max(values: list[float]) -> float | None:
    return max(values) if values else None


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value)


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    existing_outputs = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing_outputs and not args.overwrite:
        fail(
            "SHAPIROMART04 output files already exist. Use --overwrite to replace: "
            + "; ".join(existing_outputs)
        )


def validate_required_objects(con: sqlite3.Connection) -> None:
    missing: list[str] = []
    for name, object_type in PRIMARY_REQUIRED_OBJECTS:
        if not object_exists(con, name, object_type):
            missing.append(f"{object_type}:{name}")
    for table_set, tables in PRIOR_TABLE_SETS.items():
        for table in tables:
            if not object_exists(con, table, "table"):
                missing.append(f"table:{table_set}:{table}")
    if missing:
        fail("Missing required workcopy objects: " + "; ".join(missing))


def validate_existing_target_state(
    con: sqlite3.Connection,
    allow_existing: bool,
) -> dict[str, Any]:
    target_state: list[dict[str, Any]] = []
    existing_objects: list[str] = []
    populated_tables: list[str] = []
    for table in TARGET_TABLES:
        if object_exists(con, table, "table"):
            count = table_count(con, table)
            target_state.append({"name": table, "type": "table", "row_count": count})
            existing_objects.append(f"table:{table}")
            if count > 0:
                populated_tables.append(f"{table}:{count}")
        else:
            target_state.append({"name": table, "type": "table", "row_count": None})
    for view in TARGET_VIEWS:
        if object_exists(con, view, "view"):
            target_state.append({"name": view, "type": "view", "row_count": None})
            existing_objects.append(f"view:{view}")
        else:
            target_state.append({"name": view, "type": "view", "row_count": None})
    if existing_objects and not allow_existing:
        fail(
            "SHAPIROMART04 target objects already exist. Use --allow-existing "
            "for an explicit rerun: " + "; ".join(existing_objects)
        )
    return {
        "target_state": target_state,
        "existing_objects": existing_objects,
        "populated_tables": populated_tables,
    }


def table_counts(con: sqlite3.Connection, tables: list[str]) -> dict[str, int]:
    return {table: table_count(con, table) for table in tables}


def prior_counts(con: sqlite3.Connection) -> dict[str, dict[str, int]]:
    return {
        name: table_counts(con, tables)
        for name, tables in PRIOR_TABLE_SETS.items()
    }


def validate_prior_counts_preserved(
    before: dict[str, dict[str, int]],
    after: dict[str, dict[str, int]],
) -> bool:
    return before == after


def load_feature_scope(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT
            feature_dictionary_id,
            token_position,
            source_field,
            reviewed_feature_name,
            provisional_role,
            fingerprint_role_order,
            first_fingerprint_use,
            weighting_allowed,
            direct_interpretation_allowed,
            limitation
        FROM qsb_v_shapiromart03_first_fingerprint_features
        ORDER BY fingerprint_role_order, token_position
        """,
    )
    if len(rows) != 7:
        fail(f"Expected exactly seven SHAPIROMART03 feature rows, found {len(rows)}.")
    first_tokens = [
        str(row["token_position"])
        for row in rows
        if row["first_fingerprint_use"] == "first_unweighted_feature"
    ]
    aux_tokens = [
        str(row["token_position"])
        for row in rows
        if row["first_fingerprint_use"] == "auxiliary_only_not_weighted"
    ]
    if first_tokens != FINGERPRINT_TOKENS:
        fail(
            "First fingerprint token order mismatch. expected="
            + ",".join(FINGERPRINT_TOKENS)
            + " actual="
            + ",".join(first_tokens)
        )
    if aux_tokens != AUXILIARY_TOKENS:
        fail(
            "Auxiliary token order mismatch. expected="
            + ",".join(AUXILIARY_TOKENS)
            + " actual="
            + ",".join(aux_tokens)
        )
    weighted = [row for row in rows if int(row["weighting_allowed"]) != 0]
    interpreted = [row for row in rows if int(row["direct_interpretation_allowed"]) != 0]
    if weighted:
        fail("Feature dictionary allows weighting for at least one SHAPIROMART04 token.")
    if interpreted:
        fail("Feature dictionary allows direct interpretation for at least one token.")
    return rows


def load_supported_contexts(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
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
        FROM qsb_v_shapiromart01_supported_contexts
        ORDER BY receiver_term, backend_term, raw_context_label
        """,
    )
    by_receiver = {str(row["receiver_term"]): row for row in rows}
    expected_receivers = {CONTEXT_A_RECEIVER, CONTEXT_B_RECEIVER}
    if set(by_receiver) != expected_receivers or len(rows) != 2:
        fail(
            "Supported context receiver mismatch. expected="
            + ",".join(sorted(expected_receivers))
            + " actual="
            + ",".join(sorted(by_receiver))
        )
    ordered = [by_receiver[CONTEXT_A_RECEIVER], by_receiver[CONTEXT_B_RECEIVER]]
    for row in ordered:
        receiver = str(row["receiver_term"])
        expected = EXPECTED_CONTEXTS[receiver]
        if str(row["backend_term"]) != expected["backend_term"]:
            fail(f"Backend mismatch for {receiver}.")
        if str(row["raw_context_label"]) != expected["raw_context_label"]:
            fail(f"Raw context label mismatch for {receiver}.")
        if int(row["source_record_count"]) != int(expected["source_record_count"]):
            fail(f"Source record count mismatch for {receiver}.")
        if "manual_review_deferred" not in str(row["compound_label_status"]):
            fail(f"Compound label status is not deferred for {receiver}.")
    return ordered


def load_candidate_records(
    con: sqlite3.Connection,
    contexts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidate_rows: list[dict[str, Any]] = []
    for context in contexts:
        rows = fetch_dicts(
            con,
            """
            SELECT DISTINCT
                r.raw_record_id,
                r.record_index,
                r.line_type,
                link.observation_id,
                ? AS science_object_id,
                ? AS receiver_context,
                ? AS backend_context,
                ? AS raw_context_label
            FROM raw_field_value AS context_value
            JOIN raw_record AS r
              ON r.raw_record_id = context_value.raw_record_id
            JOIN core_observation_record_link AS link
              ON link.raw_record_id = r.raw_record_id
            WHERE link.observation_id = ?
              AND instr(CAST(context_value.raw_value AS TEXT), ?) > 0
            ORDER BY r.record_index, r.raw_record_id
            """,
            (
                context["science_object_id"],
                context["receiver_term"],
                context["backend_term"],
                context["raw_context_label"],
                context["observation_id"],
                context["raw_context_label"],
            ),
        )
        expected_count = int(context["source_record_count"])
        if len(rows) != expected_count:
            fail(
                f"Candidate record count mismatch for {context['receiver_term']}. "
                f"expected={expected_count} actual={len(rows)}"
            )
        candidate_rows.extend(rows)
    return sorted(
        candidate_rows,
        key=lambda row: (
            CONTEXT_ORDER.get(str(row["receiver_context"]), 99),
            int(row["record_index"]),
            str(row["raw_record_id"]),
        ),
    )


def load_target_values(
    con: sqlite3.Connection,
    candidate_records: list[dict[str, Any]],
) -> dict[str, dict[str, list[Any]]]:
    candidate_ids = {str(row["raw_record_id"]) for row in candidate_records}
    observation_ids = sorted({str(row["observation_id"]) for row in candidate_records})
    observation_placeholders = ", ".join("?" for _ in observation_ids)
    token_placeholders = ", ".join("?" for _ in ALL_TOKENS)
    rows = fetch_dicts(
        con,
        f"""
        SELECT
            fv.raw_record_id,
            fv.field_name,
            fv.raw_value
        FROM raw_field_value AS fv
        JOIN core_observation_record_link AS link
          ON link.raw_record_id = fv.raw_record_id
        WHERE link.observation_id IN ({observation_placeholders})
          AND fv.field_name IN ({token_placeholders})
        ORDER BY fv.raw_record_id, fv.field_name, fv.raw_field_value_id
        """,
        tuple(observation_ids + ALL_TOKENS),
    )
    values: dict[str, dict[str, list[Any]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        raw_record_id = str(row["raw_record_id"])
        if raw_record_id in candidate_ids:
            values[raw_record_id][str(row["field_name"])].append(row["raw_value"])
    return values


def build_fingerprint_rows(
    candidate_records: list[dict[str, Any]],
    values_by_record: dict[str, dict[str, list[Any]]],
    created_at: str,
) -> tuple[list[dict[str, Any]], dict[tuple[str, str, str], int], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    gap_counts: dict[tuple[str, str, str], int] = defaultdict(int)
    line_type_counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    raw_record_context_counts: dict[str, int] = defaultdict(int)
    for record in candidate_records:
        raw_record_context_counts[str(record["raw_record_id"])] += 1

    for index, record in enumerate(candidate_records, start=1):
        raw_record_id = str(record["raw_record_id"])
        receiver = str(record["receiver_context"])
        field_values = values_by_record.get(raw_record_id, {})
        parsed: dict[str, float | None] = {}
        duplicate_tokens: list[str] = []
        missing_required: list[str] = []
        non_numeric_required: list[str] = []
        missing_auxiliary: list[str] = []
        non_numeric_auxiliary: list[str] = []
        source_value_count = 0

        for token in ALL_TOKENS:
            token_values = field_values.get(token, [])
            source_value_count += len(token_values)
            is_required = token in FINGERPRINT_TOKENS
            if len(token_values) == 0:
                gap_counts[(receiver, token, "missing_value")] += 1
                if is_required:
                    missing_required.append(token)
                else:
                    missing_auxiliary.append(token)
                parsed[token] = None
                continue
            if len(token_values) > 1:
                gap_counts[(receiver, token, "duplicate_token_value")] += 1
                duplicate_tokens.append(token)
                parsed[token] = None
                continue
            numeric_value = parse_numeric(token_values[0])
            parsed[token] = numeric_value
            if numeric_value is None:
                gap_counts[(receiver, token, "non_numeric_value")] += 1
                if is_required:
                    non_numeric_required.append(token)
                else:
                    non_numeric_auxiliary.append(token)

        line_type_counts[receiver][str(record["line_type"])] += 1
        if receiver not in EXPECTED_CONTEXTS:
            status = "unsupported_context"
        elif duplicate_tokens:
            status = "blocked_duplicate_token_value"
        elif non_numeric_required:
            status = "blocked_non_numeric_value"
        elif missing_required:
            status = "partial_missing_fingerprint_field"
        else:
            status = "complete_unweighted_fingerprint"
        if status not in FINGERPRINT_STATUSES:
            fail(f"Unexpected fingerprint status: {status}")

        auxiliary_complete = all(
            len(field_values.get(token, [])) == 1 and parsed[token] is not None
            for token in AUXILIARY_TOKENS
        )
        notes_parts = [
            f"line_type={record['line_type']}",
            "vector_order=" + ",".join(FINGERPRINT_TOKENS),
            "unweighted_no_scaling_no_normalization",
        ]
        if missing_required:
            notes_parts.append("missing_required=" + ",".join(missing_required))
        if non_numeric_required:
            notes_parts.append("non_numeric_required=" + ",".join(non_numeric_required))
        if duplicate_tokens:
            notes_parts.append("duplicate_tokens=" + ",".join(duplicate_tokens))
        if missing_auxiliary:
            notes_parts.append("missing_auxiliary=" + ",".join(missing_auxiliary))
        if non_numeric_auxiliary:
            notes_parts.append("non_numeric_auxiliary=" + ",".join(non_numeric_auxiliary))
        if raw_record_context_counts[raw_record_id] > 1:
            notes_parts.append("record_appears_in_multiple_contexts")

        rows.append(
            {
                "structural_fingerprint_id": f"SHAPIROMART04_FP_{index:06d}",
                "raw_record_id": raw_record_id,
                "observation_id": record["observation_id"],
                "science_object_id": record["science_object_id"],
                "receiver_context": receiver,
                "backend_context": record["backend_context"],
                "raw_context_label": record["raw_context_label"],
                "coordinate_primary": parsed["tim_token_002"],
                "coordinate_secondary": parsed["tim_token_003"],
                "signal_value_primary": parsed["tim_token_029"],
                "signal_value_secondary": parsed["tim_token_033"],
                "auxiliary_uncertainty_primary": parsed["tim_token_004"],
                "auxiliary_uncertainty_secondary": parsed["tim_token_031"],
                "auxiliary_uncertainty_tertiary": parsed["tim_token_035"],
                "complete_fingerprint": 1
                if status == "complete_unweighted_fingerprint"
                else 0,
                "auxiliary_complete": 1 if auxiliary_complete else 0,
                "duplicate_or_ambiguity_flag": 1
                if duplicate_tokens or raw_record_context_counts[raw_record_id] > 1
                else 0,
                "source_value_count": source_value_count,
                "fingerprint_status": status,
                "created_at_utc": created_at,
                "notes": "; ".join(notes_parts),
            }
        )

    diagnostics = {
        "line_type_counts_by_context": {
            receiver: dict(counts)
            for receiver, counts in sorted(
                line_type_counts.items(),
                key=lambda item: CONTEXT_ORDER.get(item[0], 99),
            )
        },
        "raw_records_in_multiple_contexts": sum(
            1 for count in raw_record_context_counts.values() if count > 1
        ),
    }
    return rows, gap_counts, diagnostics


def build_gap_rows(
    gap_counts: dict[tuple[str, str, str], int],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    sorted_items = sorted(
        gap_counts.items(),
        key=lambda item: (
            CONTEXT_ORDER.get(item[0][0], 99),
            ALL_TOKENS.index(item[0][1]) if item[0][1] in ALL_TOKENS else 99,
            item[0][2],
        ),
    )
    for index, ((receiver, token, gap_type), count) in enumerate(sorted_items, start=1):
        if count <= 0:
            continue
        is_required = token in FINGERPRINT_TOKENS
        if gap_type == "duplicate_token_value":
            blocking_status = "blocking_deterministic_construction"
            recommended_action = (
                "Inspect duplicate DB token rows before deterministic construction."
            )
        elif is_required:
            blocking_status = "blocking_complete_fingerprint"
            if gap_type == "missing_value":
                recommended_action = (
                    "Review workcopy token availability before treating records as complete."
                )
            else:
                recommended_action = (
                    "Keep records quarantined unless a later DB-only step separates "
                    "non-data rows from structural data rows."
                )
        else:
            blocking_status = "nonblocking_auxiliary_gap"
            recommended_action = (
                "Carry as an auxiliary gap only; do not use the field as a weight."
            )
        rows.append(
            {
                "fingerprint_build_gap_id": f"SHAPIROMART04_GAP_{index:03d}",
                "raw_record_id": None,
                "receiver_context": receiver,
                "gap_type": gap_type,
                "affected_field": token,
                "gap_count": int(count),
                "blocking_status": blocking_status,
                "recommended_action": recommended_action,
                "created_at_utc": created_at,
                "notes": (
                    "Aggregated per supported receiver context from workcopy DB token "
                    "rows; raw_record_id is null for this field-level summary."
                ),
            }
        )
    return rows


def values_for(rows: list[dict[str, Any]], field: str) -> list[float]:
    return [float(row[field]) for row in rows if row[field] is not None]


def build_context_summary_rows(
    fingerprint_rows: list[dict[str, Any]],
    created_at: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, dict[str, float | None]]]]:
    rows: list[dict[str, Any]] = []
    field_profiles: dict[str, dict[str, dict[str, float | None]]] = {}
    for index, receiver in enumerate([CONTEXT_A_RECEIVER, CONTEXT_B_RECEIVER], start=1):
        context_rows = [
            row for row in fingerprint_rows if row["receiver_context"] == receiver
        ]
        if not context_rows:
            continue
        complete_rows = [
            row
            for row in context_rows
            if row["fingerprint_status"] == "complete_unweighted_fingerprint"
        ]
        profiles: dict[str, dict[str, float | None]] = {}
        for field in [
            "coordinate_primary",
            "coordinate_secondary",
            "signal_value_primary",
            "signal_value_secondary",
        ]:
            vals = values_for(complete_rows, field)
            profiles[field] = {
                "min": safe_min(vals),
                "max": safe_max(vals),
                "mean": safe_mean(vals),
                "median": safe_median(vals),
                "stddev": safe_stddev(vals),
            }
        field_profiles[receiver] = profiles
        first_row = context_rows[0]
        partial_count = sum(
            1
            for row in context_rows
            if row["fingerprint_status"] == "partial_missing_fingerprint_field"
        )
        blocked_count = sum(
            1
            for row in context_rows
            if str(row["fingerprint_status"]).startswith("blocked_")
            or row["fingerprint_status"] == "unsupported_context"
        )
        rows.append(
            {
                "context_summary_id": f"SHAPIROMART04_CTXSUM_{index:03d}",
                "receiver_context": receiver,
                "backend_context": first_row["backend_context"],
                "science_object_id": first_row["science_object_id"],
                "total_record_count": len(context_rows),
                "complete_fingerprint_count": len(complete_rows),
                "partial_fingerprint_count": partial_count,
                "blocked_record_count": blocked_count,
                "coordinate_primary_mean": profiles["coordinate_primary"]["mean"],
                "coordinate_primary_median": profiles["coordinate_primary"]["median"],
                "coordinate_secondary_mean": profiles["coordinate_secondary"]["mean"],
                "coordinate_secondary_median": profiles["coordinate_secondary"]["median"],
                "signal_primary_mean": profiles["signal_value_primary"]["mean"],
                "signal_primary_median": profiles["signal_value_primary"]["median"],
                "signal_primary_stddev": profiles["signal_value_primary"]["stddev"],
                "signal_secondary_mean": profiles["signal_value_secondary"]["mean"],
                "signal_secondary_median": profiles["signal_value_secondary"]["median"],
                "signal_secondary_stddev": profiles["signal_value_secondary"]["stddev"],
                "created_at_utc": created_at,
                "notes": (
                    "Statistics use complete_unweighted_fingerprint rows only; "
                    "standard deviation is population stddev; auxiliary fields are "
                    "not used as weights."
                ),
            }
        )
    return rows, field_profiles


def build_context_difference_rows(
    summary_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    by_receiver = {str(row["receiver_context"]): row for row in summary_rows}
    row_a = by_receiver.get(CONTEXT_A_RECEIVER)
    row_b = by_receiver.get(CONTEXT_B_RECEIVER)
    if row_a is None or row_b is None:
        return [
            {
                "context_difference_id": "SHAPIROMART04_CTXDIFF_001",
                "science_object_id": None,
                "context_a_receiver": CONTEXT_A_RECEIVER,
                "context_b_receiver": CONTEXT_B_RECEIVER,
                "shared_backend_context": None,
                "complete_count_a": int(row_a["complete_fingerprint_count"]) if row_a else 0,
                "complete_count_b": int(row_b["complete_fingerprint_count"]) if row_b else 0,
                "coordinate_primary_mean_difference": None,
                "coordinate_secondary_mean_difference": None,
                "signal_primary_mean_difference": None,
                "signal_secondary_mean_difference": None,
                "signal_primary_median_difference": None,
                "signal_secondary_median_difference": None,
                "difference_status": "context_alignment_blocked",
                "interpretation_status": INTERPRETATION_STATUS,
                "created_at_utc": created_at,
                "notes": "One or both supported context summaries are missing.",
            }
        ]
    shared_backend = (
        row_a["backend_context"]
        if row_a["backend_context"] == row_b["backend_context"]
        else None
    )
    same_object = row_a["science_object_id"] == row_b["science_object_id"]
    complete_a = int(row_a["complete_fingerprint_count"])
    complete_b = int(row_b["complete_fingerprint_count"])
    aligned = shared_backend is not None and same_object
    if not aligned:
        status = "context_alignment_blocked"
    elif complete_a <= 0 or complete_b <= 0:
        status = "insufficient_complete_records"
    else:
        status = "descriptive_difference_available"
    if status not in DIFFERENCE_STATUSES:
        fail(f"Unexpected difference status: {status}")

    def diff(field: str) -> float | None:
        if status != "descriptive_difference_available":
            return None
        left = row_a[field]
        right = row_b[field]
        if left is None or right is None:
            return None
        return float(left) - float(right)

    return [
        {
            "context_difference_id": "SHAPIROMART04_CTXDIFF_001",
            "science_object_id": row_a["science_object_id"] if same_object else None,
            "context_a_receiver": CONTEXT_A_RECEIVER,
            "context_b_receiver": CONTEXT_B_RECEIVER,
            "shared_backend_context": shared_backend,
            "complete_count_a": complete_a,
            "complete_count_b": complete_b,
            "coordinate_primary_mean_difference": diff("coordinate_primary_mean"),
            "coordinate_secondary_mean_difference": diff("coordinate_secondary_mean"),
            "signal_primary_mean_difference": diff("signal_primary_mean"),
            "signal_secondary_mean_difference": diff("signal_secondary_mean"),
            "signal_primary_median_difference": diff("signal_primary_median"),
            "signal_secondary_median_difference": diff("signal_secondary_median"),
            "difference_status": status,
            "interpretation_status": INTERPRETATION_STATUS,
            "created_at_utc": created_at,
            "notes": (
                "Differences are context A minus context B, using complete "
                "unweighted fingerprints only; descriptive status only."
            ),
        }
    ]


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS mart_shapiro_structural_fingerprint (
            structural_fingerprint_id TEXT PRIMARY KEY,
            raw_record_id TEXT NOT NULL,
            observation_id TEXT,
            science_object_id TEXT,
            receiver_context TEXT NOT NULL,
            backend_context TEXT NOT NULL,
            raw_context_label TEXT,
            coordinate_primary REAL,
            coordinate_secondary REAL,
            signal_value_primary REAL,
            signal_value_secondary REAL,
            auxiliary_uncertainty_primary REAL,
            auxiliary_uncertainty_secondary REAL,
            auxiliary_uncertainty_tertiary REAL,
            complete_fingerprint INTEGER NOT NULL CHECK (complete_fingerprint IN (0, 1)),
            auxiliary_complete INTEGER NOT NULL CHECK (auxiliary_complete IN (0, 1)),
            duplicate_or_ambiguity_flag INTEGER NOT NULL CHECK (duplicate_or_ambiguity_flag IN (0, 1)),
            source_value_count INTEGER NOT NULL,
            fingerprint_status TEXT NOT NULL CHECK (
                fingerprint_status IN (
                    'complete_unweighted_fingerprint',
                    'partial_missing_fingerprint_field',
                    'blocked_duplicate_token_value',
                    'blocked_non_numeric_value',
                    'unsupported_context'
                )
            ),
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_fingerprint_context_summary (
            context_summary_id TEXT PRIMARY KEY,
            receiver_context TEXT NOT NULL,
            backend_context TEXT NOT NULL,
            science_object_id TEXT,
            total_record_count INTEGER NOT NULL,
            complete_fingerprint_count INTEGER NOT NULL,
            partial_fingerprint_count INTEGER NOT NULL,
            blocked_record_count INTEGER NOT NULL,
            coordinate_primary_mean REAL,
            coordinate_primary_median REAL,
            coordinate_secondary_mean REAL,
            coordinate_secondary_median REAL,
            signal_primary_mean REAL,
            signal_primary_median REAL,
            signal_primary_stddev REAL,
            signal_secondary_mean REAL,
            signal_secondary_median REAL,
            signal_secondary_stddev REAL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_fingerprint_context_difference (
            context_difference_id TEXT PRIMARY KEY,
            science_object_id TEXT,
            context_a_receiver TEXT NOT NULL,
            context_b_receiver TEXT NOT NULL,
            shared_backend_context TEXT,
            complete_count_a INTEGER NOT NULL,
            complete_count_b INTEGER NOT NULL,
            coordinate_primary_mean_difference REAL,
            coordinate_secondary_mean_difference REAL,
            signal_primary_mean_difference REAL,
            signal_secondary_mean_difference REAL,
            signal_primary_median_difference REAL,
            signal_secondary_median_difference REAL,
            difference_status TEXT NOT NULL CHECK (
                difference_status IN (
                    'descriptive_difference_available',
                    'insufficient_complete_records',
                    'context_alignment_blocked'
                )
            ),
            interpretation_status TEXT NOT NULL CHECK (
                interpretation_status = 'descriptive_only_no_physical_interpretation'
            ),
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_fingerprint_build_gap (
            fingerprint_build_gap_id TEXT PRIMARY KEY,
            raw_record_id TEXT,
            receiver_context TEXT,
            gap_type TEXT NOT NULL,
            affected_field TEXT,
            gap_count INTEGER NOT NULL,
            blocking_status TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS shapiromart04_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            total_candidate_record_count INTEGER,
            complete_fingerprint_count INTEGER,
            partial_fingerprint_count INTEGER,
            blocked_fingerprint_count INTEGER,
            context_a_complete_count INTEGER,
            context_b_complete_count INTEGER,
            context_difference_created INTEGER,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
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
    columns = ", ".join(quote_identifier(field) for field in fieldnames)
    placeholders = ", ".join("?" for _ in fieldnames)
    con.executemany(
        f"INSERT INTO {quote_identifier(table)} ({columns}) VALUES ({placeholders})",
        [tuple(row[field] for field in fieldnames) for row in rows],
    )


def create_views(con: sqlite3.Connection) -> None:
    for view in TARGET_VIEWS:
        con.execute(f"DROP VIEW IF EXISTS {quote_identifier(view)}")
    con.executescript(
        """
        CREATE VIEW qsb_v_shapiromart04_fingerprint_dashboard AS
        SELECT
            receiver_context,
            backend_context,
            science_object_id,
            COUNT(*) AS total_record_count,
            SUM(complete_fingerprint) AS complete_fingerprint_count,
            SUM(CASE WHEN fingerprint_status = 'partial_missing_fingerprint_field'
                     THEN 1 ELSE 0 END) AS partial_fingerprint_count,
            SUM(CASE WHEN fingerprint_status LIKE 'blocked_%'
                       OR fingerprint_status = 'unsupported_context'
                     THEN 1 ELSE 0 END) AS blocked_fingerprint_count,
            ROUND(
                CAST(SUM(complete_fingerprint) AS REAL) / CAST(COUNT(*) AS REAL),
                6
            ) AS complete_fingerprint_rate,
            SUM(auxiliary_complete) AS auxiliary_complete_count,
            SUM(duplicate_or_ambiguity_flag) AS duplicate_or_ambiguity_count,
            SUM(source_value_count) AS source_value_count
        FROM mart_shapiro_structural_fingerprint
        GROUP BY receiver_context, backend_context, science_object_id
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            receiver_context;

        CREATE VIEW qsb_v_shapiromart04_complete_fingerprints AS
        SELECT
            structural_fingerprint_id,
            raw_record_id,
            observation_id,
            science_object_id,
            receiver_context,
            backend_context,
            raw_context_label,
            coordinate_primary,
            coordinate_secondary,
            signal_value_primary,
            signal_value_secondary,
            auxiliary_uncertainty_primary,
            auxiliary_uncertainty_secondary,
            auxiliary_uncertainty_tertiary,
            created_at_utc,
            notes
        FROM mart_shapiro_structural_fingerprint
        WHERE complete_fingerprint = 1
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            structural_fingerprint_id;

        CREATE VIEW qsb_v_shapiromart04_context_summary AS
        SELECT *
        FROM mart_shapiro_fingerprint_context_summary
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            receiver_context;

        CREATE VIEW qsb_v_shapiromart04_context_difference AS
        SELECT *
        FROM mart_shapiro_fingerprint_context_difference
        ORDER BY context_difference_id;

        CREATE VIEW qsb_v_shapiromart04_build_gaps AS
        SELECT *
        FROM mart_shapiro_fingerprint_build_gap
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            affected_field,
            gap_type;
        """
    )


def queryable_counts(con: sqlite3.Connection) -> dict[str, int | str]:
    counts: dict[str, int | str] = {}
    for name in TARGET_TABLES + TARGET_VIEWS:
        try:
            counts[name] = table_count(con, name)
        except sqlite3.Error as exc:
            counts[name] = f"ERROR: {exc}"
    return counts


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def markdown_table(rows: list[dict[str, Any]], fieldnames: list[str]) -> list[str]:
    if not rows:
        return ["No rows."]
    lines = [
        "| " + " | ".join(fieldnames) + " |",
        "| " + " | ".join("---" for _ in fieldnames) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row.get(field)) for field in fieldnames) + " |")
    return lines


def status_counts(fingerprint_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {status: 0 for status in sorted(FINGERPRINT_STATUSES)}
    for row in fingerprint_rows:
        status = str(row["fingerprint_status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def summarize_gaps(gap_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        gap_rows,
        key=lambda row: (
            0 if str(row["blocking_status"]).startswith("blocking") else 1,
            -int(row["gap_count"]),
            CONTEXT_ORDER.get(str(row["receiver_context"]), 99),
            str(row["affected_field"]),
        ),
    )


def write_readout(
    path: Path,
    run_id: str,
    created_at: str,
    fingerprint_rows: list[dict[str, Any]],
    context_summary_rows: list[dict[str, Any]],
    difference_rows: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    diagnostics: dict[str, Any],
    validation: dict[str, Any],
) -> None:
    total = len(fingerprint_rows)
    complete_count = sum(int(row["complete_fingerprint"]) for row in fingerprint_rows)
    partial_count = sum(
        1
        for row in fingerprint_rows
        if row["fingerprint_status"] == "partial_missing_fingerprint_field"
    )
    blocked_count = sum(
        1
        for row in fingerprint_rows
        if str(row["fingerprint_status"]).startswith("blocked_")
        or row["fingerprint_status"] == "unsupported_context"
    )
    duplicate_gap_count = sum(
        int(row["gap_count"])
        for row in gap_rows
        if row["gap_type"] == "duplicate_token_value"
    )
    top_gaps = summarize_gaps(gap_rows)[:12]
    difference = difference_rows[0] if difference_rows else {}

    lines: list[str] = [
        "# QSB-SHAPIROMART04 - First Unweighted Structural Fingerprint Build",
        "",
        f"Run ID: {run_id}",
        f"Run timestamp UTC: {created_at}",
        "",
        "## Scope",
        "",
        CLAIM_BOUNDARY,
        "",
        "Fingerprint vector order: "
        + ", ".join(FINGERPRINT_TOKENS)
        + ". No scaling, normalization, weighting, imputation, clustering, "
        + "or significance testing was applied.",
        "",
        "## 1. Candidate records inspected",
        "",
        f"Total candidate records inspected: {total}.",
        "",
    ]
    lines.extend(
        markdown_table(
            context_summary_rows,
            [
                "receiver_context",
                "backend_context",
                "science_object_id",
                "total_record_count",
                "complete_fingerprint_count",
                "partial_fingerprint_count",
                "blocked_record_count",
            ],
        )
    )
    lines.extend(
        [
            "",
            "Line-type inventory by context:",
            "",
            "```json",
            json.dumps(
                diagnostics["line_type_counts_by_context"],
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## 2. Complete four-field fingerprints",
            "",
            f"Complete four-field fingerprints built: {complete_count}.",
            f"Partial records: {partial_count}.",
            f"Blocked records: {blocked_count}.",
            "",
            "Fingerprint status counts:",
            "",
            "```json",
            json.dumps(status_counts(fingerprint_rows), indent=2, sort_keys=True),
            "```",
            "",
            "## 3. Complete fingerprints by receiver context",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            context_summary_rows,
            ["receiver_context", "complete_fingerprint_count"],
        )
    )
    lines.extend(
        [
            "",
            "## 4. Missingness and ambiguity fields",
            "",
            f"Duplicate token-value gaps observed: {duplicate_gap_count}.",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            top_gaps,
            [
                "receiver_context",
                "affected_field",
                "gap_type",
                "gap_count",
                "blocking_status",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 5. Descriptive context differences",
            "",
            "Differences are context A minus context B, where context A is "
            f"{CONTEXT_A_RECEIVER} and context B is {CONTEXT_B_RECEIVER}.",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            difference_rows,
            [
                "context_a_receiver",
                "context_b_receiver",
                "shared_backend_context",
                "complete_count_a",
                "complete_count_b",
                "coordinate_primary_mean_difference",
                "coordinate_secondary_mean_difference",
                "signal_primary_mean_difference",
                "signal_secondary_mean_difference",
                "signal_primary_median_difference",
                "signal_secondary_median_difference",
                "difference_status",
                "interpretation_status",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 6. Readiness for deeper analysis",
            "",
            "The differences are descriptive only. This build supports only a "
            "next descriptive stability/separability check; it does not support "
            "model, timing, or interpretive analysis.",
            "",
            "## 7. What prevents the next comparison step",
            "",
            "The immediate blockers are non-numeric token values in comment-line "
            "records and missing target tokens in par-key-value-like records. "
            "A next comparison step also needs a DB-backed descriptive stability "
            "and separability profile for the complete four-dimensional vectors.",
            "",
            "## 8. Single next concrete research step",
            "",
            NEXT_STEP,
            "",
            "## Validation",
            "",
            "```json",
            json.dumps(validation, indent=2, sort_keys=True),
            "```",
            "",
            "## Notes",
            "",
            "Raw context labels were carried as unresolved labels only. Auxiliary "
            "uncertainty candidates were stored but were not applied as weights.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sample_fingerprints(
    fingerprint_rows: list[dict[str, Any]],
    per_context: int = 10,
) -> list[dict[str, Any]]:
    samples: list[dict[str, Any]] = []
    for receiver in [CONTEXT_A_RECEIVER, CONTEXT_B_RECEIVER]:
        receiver_rows = [
            row
            for row in fingerprint_rows
            if row["receiver_context"] == receiver
            and row["fingerprint_status"] == "complete_unweighted_fingerprint"
        ]
        samples.extend(receiver_rows[:per_context])
    return samples


def write_outputs(
    output_root: Path,
    run_id: str,
    created_at: str,
    fingerprint_rows: list[dict[str, Any]],
    context_summary_rows: list[dict[str, Any]],
    difference_rows: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    diagnostics: dict[str, Any],
    validation: dict[str, Any],
    field_profiles: dict[str, dict[str, dict[str, float | None]]],
) -> dict[str, str]:
    paths = output_paths(output_root)
    write_csv(
        paths[CONTEXT_SUMMARY_CSV],
        context_summary_rows,
        [
            "context_summary_id",
            "receiver_context",
            "backend_context",
            "science_object_id",
            "total_record_count",
            "complete_fingerprint_count",
            "partial_fingerprint_count",
            "blocked_record_count",
            "coordinate_primary_mean",
            "coordinate_primary_median",
            "coordinate_secondary_mean",
            "coordinate_secondary_median",
            "signal_primary_mean",
            "signal_primary_median",
            "signal_primary_stddev",
            "signal_secondary_mean",
            "signal_secondary_median",
            "signal_secondary_stddev",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[CONTEXT_DIFFERENCE_CSV],
        difference_rows,
        [
            "context_difference_id",
            "science_object_id",
            "context_a_receiver",
            "context_b_receiver",
            "shared_backend_context",
            "complete_count_a",
            "complete_count_b",
            "coordinate_primary_mean_difference",
            "coordinate_secondary_mean_difference",
            "signal_primary_mean_difference",
            "signal_secondary_mean_difference",
            "signal_primary_median_difference",
            "signal_secondary_median_difference",
            "difference_status",
            "interpretation_status",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[BUILD_GAPS_CSV],
        gap_rows,
        [
            "fingerprint_build_gap_id",
            "raw_record_id",
            "receiver_context",
            "gap_type",
            "affected_field",
            "gap_count",
            "blocking_status",
            "recommended_action",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[SAMPLE_FINGERPRINTS_CSV],
        sample_fingerprints(fingerprint_rows),
        [
            "structural_fingerprint_id",
            "raw_record_id",
            "observation_id",
            "science_object_id",
            "receiver_context",
            "backend_context",
            "raw_context_label",
            "coordinate_primary",
            "coordinate_secondary",
            "signal_value_primary",
            "signal_value_secondary",
            "auxiliary_uncertainty_primary",
            "auxiliary_uncertainty_secondary",
            "auxiliary_uncertainty_tertiary",
            "complete_fingerprint",
            "auxiliary_complete",
            "duplicate_or_ambiguity_flag",
            "source_value_count",
            "fingerprint_status",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[NEXT_STEP_CSV],
        [
            {
                "next_step_id": "SHAPIROMART04_NEXT_001",
                "recommended_next_step": NEXT_STEP,
                "scope_limit": "descriptive_non_inferential_only",
                "db_write_expected": "yes_in_separate_explicit_task",
                "claim_boundary": CLAIM_BOUNDARY,
                "warnings": (
                    "Do not use auxiliary uncertainty candidates as weights; "
                    "do not assign physical interpretation."
                ),
            }
        ],
        [
            "next_step_id",
            "recommended_next_step",
            "scope_limit",
            "db_write_expected",
            "claim_boundary",
            "warnings",
        ],
    )
    total = len(fingerprint_rows)
    complete = sum(int(row["complete_fingerprint"]) for row in fingerprint_rows)
    partial = sum(
        1
        for row in fingerprint_rows
        if row["fingerprint_status"] == "partial_missing_fingerprint_field"
    )
    blocked = sum(
        1
        for row in fingerprint_rows
        if str(row["fingerprint_status"]).startswith("blocked_")
        or row["fingerprint_status"] == "unsupported_context"
    )
    summary_payload = {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script": SCRIPT_NAME,
        "total_candidate_record_count": total,
        "complete_fingerprint_count": complete,
        "partial_fingerprint_count": partial,
        "blocked_fingerprint_count": blocked,
        "status_counts": status_counts(fingerprint_rows),
        "context_summary": context_summary_rows,
        "context_difference": difference_rows,
        "field_profiles_complete_records": field_profiles,
        "gap_summary": gap_rows,
        "diagnostics": diagnostics,
        "validation": validation,
        "next_step": NEXT_STEP,
        "claim_boundary": CLAIM_BOUNDARY,
        "warnings": [
            "Auxiliary uncertainty candidates were not applied as weights.",
            "No scaling or normalization was applied.",
            "No timing/model/inference quantities were computed.",
        ],
        "output_files": {name: str(path) for name, path in paths.items()},
        "stop_reason": "completed_full_supported_context_build",
    }
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_readout(
        paths[READOUT_MD],
        run_id,
        created_at,
        fingerprint_rows,
        context_summary_rows,
        difference_rows,
        gap_rows,
        diagnostics,
        validation,
    )
    return {name: str(path) for name, path in paths.items()}


def build_run_log_row(
    run_id: str,
    created_at: str,
    fingerprint_rows: list[dict[str, Any]],
    difference_rows: list[dict[str, Any]],
    live_db_modified: bool,
    workcopy_db_modified: bool,
    integrity_result: str,
    fk_violation_count: int,
) -> dict[str, Any]:
    total = len(fingerprint_rows)
    complete = sum(int(row["complete_fingerprint"]) for row in fingerprint_rows)
    partial = sum(
        1
        for row in fingerprint_rows
        if row["fingerprint_status"] == "partial_missing_fingerprint_field"
    )
    blocked = sum(
        1
        for row in fingerprint_rows
        if str(row["fingerprint_status"]).startswith("blocked_")
        or row["fingerprint_status"] == "unsupported_context"
    )
    context_a_complete = sum(
        int(row["complete_fingerprint"])
        for row in fingerprint_rows
        if row["receiver_context"] == CONTEXT_A_RECEIVER
    )
    context_b_complete = sum(
        int(row["complete_fingerprint"])
        for row in fingerprint_rows
        if row["receiver_context"] == CONTEXT_B_RECEIVER
    )
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "total_candidate_record_count": total,
        "complete_fingerprint_count": complete,
        "partial_fingerprint_count": partial,
        "blocked_fingerprint_count": blocked,
        "context_a_complete_count": context_a_complete,
        "context_b_complete_count": context_b_complete,
        "context_difference_created": 1 if difference_rows else 0,
        "live_db_modified": 1 if live_db_modified else 0,
        "workcopy_db_modified": 1 if workcopy_db_modified else 0,
        "integrity_check_result": integrity_result,
        "foreign_key_violation_count": fk_violation_count,
        "notes": (
            "First unweighted structural fingerprint build; context difference "
            "is descriptive only; raw compound labels not promoted."
        ),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)
    created_at = utc_now()
    run_id = "SHAPIROMART04_RUN_" + created_at.replace("-", "").replace(":", "")

    with connect_readonly(args.live_db) as live_con:
        live_con.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()

    con = connect_writable(args.workcopy_db)
    try:
        validate_required_objects(con)
        target_state = validate_existing_target_state(con, args.allow_existing)
        prior_before = prior_counts(con)
        feature_scope = load_feature_scope(con)
        contexts = load_supported_contexts(con)
        candidate_records = load_candidate_records(con, contexts)
        values_by_record = load_target_values(con, candidate_records)
        fingerprint_rows, gap_counts, diagnostics = build_fingerprint_rows(
            candidate_records,
            values_by_record,
            created_at,
        )
        gap_rows = build_gap_rows(gap_counts, created_at)
        context_summary_rows, field_profiles = build_context_summary_rows(
            fingerprint_rows,
            created_at,
        )
        difference_rows = build_context_difference_rows(context_summary_rows, created_at)

        create_tables(con)
        if args.allow_existing:
            clear_target_tables(con)
        insert_rows(con, "mart_shapiro_structural_fingerprint", fingerprint_rows)
        insert_rows(con, "mart_shapiro_fingerprint_context_summary", context_summary_rows)
        insert_rows(con, "mart_shapiro_fingerprint_context_difference", difference_rows)
        insert_rows(con, "mart_shapiro_fingerprint_build_gap", gap_rows)
        create_views(con)
        con.commit()

        integrity_result = integrity_check(con)
        fk_violations = foreign_key_violations(con)
        prior_after = prior_counts(con)
        prior_preserved = validate_prior_counts_preserved(prior_before, prior_after)
        queryable_after_data = queryable_counts(con)
        live_after_data = db_state(args.live_db)
        workcopy_after_data = db_state(args.workcopy_db)
        live_modified = live_before != live_after_data
        workcopy_modified = workcopy_before != workcopy_after_data

        run_log_row = build_run_log_row(
            run_id,
            created_at,
            fingerprint_rows,
            difference_rows,
            live_modified,
            workcopy_modified,
            integrity_result,
            len(fk_violations),
        )
        insert_rows(con, "shapiromart04_run_log", [run_log_row])
        con.commit()

        final_integrity = integrity_check(con)
        final_fk_violations = foreign_key_violations(con)
        final_live_state = db_state(args.live_db)
        final_workcopy_state = db_state(args.workcopy_db)
        final_live_modified = live_before != final_live_state
        final_workcopy_modified = workcopy_before != final_workcopy_state
        con.execute(
            """
            UPDATE shapiromart04_run_log
            SET live_db_modified = ?,
                workcopy_db_modified = ?,
                integrity_check_result = ?,
                foreign_key_violation_count = ?
            WHERE run_id = ?
            """,
            (
                1 if final_live_modified else 0,
                1 if final_workcopy_modified else 0,
                final_integrity,
                len(final_fk_violations),
                run_id,
            ),
        )
        con.commit()

        queryable_final = queryable_counts(con)
        validation = {
            "live_db_checksum_stat_unchanged": not final_live_modified,
            "workcopy_db_modified": final_workcopy_modified,
            "workcopy_integrity_check": final_integrity,
            "workcopy_foreign_key_violation_count": len(final_fk_violations),
            "prior_shapiromart_counts_preserved": prior_preserved,
            "compound_labels_promoted": False,
            "weighting_applied": False,
            "normalization_applied": False,
            "interpretation_status": INTERPRETATION_STATUS,
            "all_new_tables_views_queryable": all(
                isinstance(value, int) for value in queryable_final.values()
            ),
            "queryable_counts": queryable_final,
            "pre_run_target_state": target_state,
            "feature_scope": feature_scope,
            "live_db_before": live_before,
            "live_db_after": final_live_state,
            "workcopy_db_before": workcopy_before,
            "workcopy_db_after": final_workcopy_state,
            "prior_counts_before": prior_before,
            "prior_counts_after": prior_after,
            "queryable_counts_after_data_before_run_log": queryable_after_data,
        }
        if final_integrity != "ok":
            fail(f"Workcopy integrity_check failed: {final_integrity}")
        if final_fk_violations:
            fail(f"Workcopy foreign_key_check returned {len(final_fk_violations)} rows.")
        if final_live_modified:
            fail("Live DB checksum/stat changed.")
        if not prior_preserved:
            fail("SHAPIROMART01/02/03 table counts changed.")
        if not validation["all_new_tables_views_queryable"]:
            fail("At least one SHAPIROMART04 table/view is not queryable.")

        output_files = write_outputs(
            args.output_root,
            run_id,
            created_at,
            fingerprint_rows,
            context_summary_rows,
            difference_rows,
            gap_rows,
            diagnostics,
            validation,
            field_profiles,
        )
        return {
            "run_id": run_id,
            "run_timestamp_utc": created_at,
            "total_candidate_record_count": len(fingerprint_rows),
            "complete_fingerprint_count": sum(
                int(row["complete_fingerprint"]) for row in fingerprint_rows
            ),
            "partial_fingerprint_count": sum(
                1
                for row in fingerprint_rows
                if row["fingerprint_status"] == "partial_missing_fingerprint_field"
            ),
            "blocked_fingerprint_count": sum(
                1
                for row in fingerprint_rows
                if str(row["fingerprint_status"]).startswith("blocked_")
                or row["fingerprint_status"] == "unsupported_context"
            ),
            "context_summary": context_summary_rows,
            "context_difference": difference_rows,
            "output_files": output_files,
            "validation": validation,
        }
    finally:
        con.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build SHAPIROMART04 first unweighted structural fingerprints in "
            "the existing workcopy DB."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing SHAPIROMART04 output files.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow replacing existing SHAPIROMART04 DB target rows/views.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
