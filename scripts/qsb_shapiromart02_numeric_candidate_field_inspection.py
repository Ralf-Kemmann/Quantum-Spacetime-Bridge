#!/usr/bin/env python3
"""QSB-SHAPIROMART02: inspect numeric candidate fields structurally.

The script profiles the nine SHAPIROMART01 numeric candidates from the
workcopy DB. It records descriptive structure only and does not assign final
scientific semantics or compute model/result quantities.
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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart02_numeric_candidate_field_inspection.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART02_NUMERIC_FIELD_INSPECTION"
)

READOUT_MD = "shapiromart02_readout.md"
SUMMARY_JSON = "shapiromart02_summary.json"
PROFILE_CSV = "shapiromart02_numeric_field_profiles.csv"
PAIR_CSV = "shapiromart02_numeric_field_pair_relations.csv"
ROLE_REVIEW_CSV = "shapiromart02_candidate_role_review.csv"
READINESS_CSV = "shapiromart02_first_fingerprint_readiness.csv"
NEXT_STEP_CSV = "shapiromart02_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    PROFILE_CSV,
    PAIR_CSV,
    ROLE_REVIEW_CSV,
    READINESS_CSV,
    NEXT_STEP_CSV,
]

TARGET_TABLES = [
    "mart_shapiro_numeric_field_profile",
    "mart_shapiro_numeric_field_pair_relation",
    "mart_shapiro_numeric_field_review",
    "shapiromart02_run_log",
]

TARGET_VIEWS = [
    "qsb_v_shapiromart02_numeric_field_profiles",
    "qsb_v_shapiromart02_candidate_roles",
    "qsb_v_shapiromart02_pair_relations",
    "qsb_v_shapiromart02_first_fingerprint_readiness",
]

REQUIRED_TABLES = [
    "mart_shapiro_feature_availability",
    "raw_field_value",
    "raw_record",
    "core_observation_record_link",
    "mart_shapiro_observation_context",
    "mart_shapiro_comparison_cohort",
]

SHAPIROMART01_TABLES = [
    "mart_shapiro_observation_context",
    "mart_shapiro_feature_availability",
    "mart_shapiro_comparison_cohort",
    "mart_shapiro_control_gap",
    "shapiromart01_run_log",
]

OPEN_COMPOUND_LABELS = ["Rcvr_800_GUPPI", "Rcvr1_2_GUPPI"]
CONTEXT_A_LABEL = "Rcvr_800_GUPPI"
CONTEXT_B_LABEL = "Rcvr1_2_GUPPI"

NUMERIC_RE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
FIELD_RE = re.compile(r"field_name=([A-Za-z0-9_]+)")
LINE_TYPE_RE = re.compile(r"line_type=([A-Za-z0-9_]+)")

CLAIM_BOUNDARY = (
    "SHAPIROMART02 is a descriptive numeric-field inspection only. It does not "
    "promote compound labels, update mapping decisions, compute model/result "
    "quantities, or make Bridge, Shapiro, or interpretive claims."
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


def stable_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def parse_numeric(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or not NUMERIC_RE.match(text):
        return None
    try:
        return float(text)
    except ValueError:
        return None


def safe_mean(values: list[float]) -> float | None:
    return statistics.fmean(values) if values else None


def safe_median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def safe_stddev(values: list[float]) -> float | None:
    return statistics.pstdev(values) if len(values) > 1 else 0.0 if values else None


def pearson(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) < 2 or len(xs) != len(ys):
        return None
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    dx = [x - mean_x for x in xs]
    dy = [y - mean_y for y in ys]
    denom_x = math.sqrt(sum(value * value for value in dx))
    denom_y = math.sqrt(sum(value * value for value in dy))
    if denom_x == 0 or denom_y == 0:
        return None
    return sum(a * b for a, b in zip(dx, dy)) / (denom_x * denom_y)


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    existing = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing and not args.overwrite:
        fail(
            "SHAPIROMART02 output files already exist. Use --overwrite to replace: "
            + "; ".join(existing)
        )


def validate_required_tables(con: sqlite3.Connection) -> None:
    missing = [name for name in REQUIRED_TABLES if not object_exists(con, name, "table")]
    if missing:
        fail("Missing required workcopy tables: " + "; ".join(missing))


def validate_existing_target_state(con: sqlite3.Connection, allow_existing: bool) -> dict[str, Any]:
    state: list[dict[str, Any]] = []
    populated: list[str] = []
    for table in TARGET_TABLES:
        if object_exists(con, table, "table"):
            count = table_count(con, table)
            state.append({"table": table, "exists": True, "row_count": count})
            if count > 0:
                populated.append(f"{table}:{count}")
        else:
            state.append({"table": table, "exists": False, "row_count": 0})
    if populated and not allow_existing:
        fail(
            "SHAPIROMART02 tables already contain rows. Use --allow-existing "
            "for an explicit rerun: " + "; ".join(populated)
        )
    return {"target_tables": state}


def shapiromart01_counts(con: sqlite3.Connection) -> dict[str, int]:
    return {table: table_count(con, table) for table in SHAPIROMART01_TABLES}


def mapping_separation_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(
        fetch_dicts(
            con,
            """
            SELECT 'supported' AS separation_class, term, token_position,
                   dwh14a_decision_status, new_mapping_status, new_review_status
            FROM qsb_v_dwh15a_supported_review_ready_candidates
            WHERE term IN ('GUPPI', 'Rcvr_800', 'Rcvr1_2',
                           'Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
            ORDER BY separation_class, term, token_position
            """,
        )
    )
    rows.extend(
        fetch_dicts(
            con,
            """
            SELECT 'open_or_deferred' AS separation_class, term, token_position,
                   dwh14a_decision_status, skip_reason AS new_mapping_status,
                   notes AS new_review_status
            FROM qsb_v_dwh15a_skipped_deferred_candidates
            WHERE term IN ('GUPPI', 'Rcvr_800', 'Rcvr1_2',
                           'Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
            ORDER BY separation_class, term, token_position
            """,
        )
    )
    return sorted(rows, key=lambda row: (row["separation_class"], row["term"], row["token_position"]))


def load_candidate_fields(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT
            feature_availability_id,
            source_table,
            source_field,
            populated_row_count,
            distinct_value_count,
            datatype_or_storage_class,
            candidate_use,
            semantic_status,
            notes
        FROM mart_shapiro_feature_availability
        WHERE candidate_use = 'future_fingerprint_candidate_after_semantic_review'
        ORDER BY feature_availability_id
        """,
    )
    if len(rows) != 9:
        fail(f"Expected exactly nine candidate fields, found {len(rows)}.")
    parsed: list[dict[str, Any]] = []
    for row in rows:
        field_match = FIELD_RE.search(str(row["source_field"]))
        line_match = LINE_TYPE_RE.search(str(row["source_field"]))
        if not field_match:
            fail(f"Cannot parse field_name from source_field: {row['source_field']}")
        item = dict(row)
        item["token_position"] = field_match.group(1)
        item["line_type"] = line_match.group(1) if line_match else "data_line"
        parsed.append(item)
    return parsed


def load_field_values(
    con: sqlite3.Connection,
    token_position: str,
    line_type: str,
) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            r.raw_record_id,
            r.record_index,
            typeof(fv.raw_value) AS sqlite_type,
            fv.raw_value,
            CASE
              WHEN EXISTS (
                SELECT 1
                FROM raw_field_value AS cx
                WHERE cx.raw_record_id = fv.raw_record_id
                  AND CAST(cx.raw_value AS TEXT) LIKE ?
              ) THEN 1 ELSE 0
            END AS in_context_a,
            CASE
              WHEN EXISTS (
                SELECT 1
                FROM raw_field_value AS cx
                WHERE cx.raw_record_id = fv.raw_record_id
                  AND CAST(cx.raw_value AS TEXT) LIKE ?
              ) THEN 1 ELSE 0
            END AS in_context_b
        FROM raw_field_value AS fv
        JOIN raw_record AS r
          ON r.raw_record_id = fv.raw_record_id
        WHERE fv.field_name = ?
          AND r.line_type = ?
        ORDER BY r.record_index, r.raw_record_id
        """,
        (f"%{CONTEXT_A_LABEL}%", f"%{CONTEXT_B_LABEL}%", token_position, line_type),
    )


def monotonicity_status(ordered_values: list[tuple[int, float]]) -> tuple[str, dict[str, int]]:
    if len(ordered_values) < 2:
        return "insufficient_rows", {"increase_count": 0, "decrease_count": 0, "equal_count": 0}
    increases = 0
    decreases = 0
    equals = 0
    for (_, left), (_, right) in zip(ordered_values, ordered_values[1:]):
        if right > left:
            increases += 1
        elif right < left:
            decreases += 1
        else:
            equals += 1
    transitions = len(ordered_values) - 1
    if decreases == 0 and equals == 0:
        status = "strictly_increasing"
    elif decreases == 0:
        status = "non_decreasing"
    elif decreases / transitions <= 0.01 and increases > decreases:
        status = "mostly_non_decreasing_sequence_like"
    elif increases == 0 and equals == 0:
        status = "strictly_decreasing"
    elif increases == 0:
        status = "non_increasing"
    else:
        status = "not_monotonic"
    return status, {
        "increase_count": increases,
        "decrease_count": decreases,
        "equal_count": equals,
    }


def classify_profile(
    numeric_count: int,
    distinct_count: int,
    numeric_min: float | None,
    numeric_max: float | None,
    numeric_mean: float | None,
    numeric_median: float | None,
    numeric_stddev: float | None,
    integer_like_fraction: float,
    repeated_value_fraction: float,
    monotonicity: str,
    context_a_mean: float | None,
    context_b_mean: float | None,
) -> tuple[str, str, int, str, str]:
    if numeric_count == 0 or distinct_count == 0:
        return (
            "unresolved_numeric_candidate",
            "low",
            0,
            "No numeric values were parsed.",
            "No provisional role approved.",
        )
    if distinct_count <= 1 or (numeric_stddev is not None and numeric_stddev == 0):
        return (
            "constant_or_near_constant",
            "high",
            0,
            "Constant or near-constant field is not useful for a first fingerprint.",
            "No provisional role approved.",
        )

    distinct_ratio = distinct_count / numeric_count
    value_range = (numeric_max - numeric_min) if numeric_min is not None and numeric_max is not None else 0.0
    median_abs = abs(numeric_median) if numeric_median is not None else 0.0
    context_gap = (
        abs(context_a_mean - context_b_mean)
        if context_a_mean is not None and context_b_mean is not None
        else 0.0
    )
    spread = numeric_stddev or 0.0

    if monotonicity in {"strictly_increasing", "non_decreasing", "mostly_non_decreasing_sequence_like"} and distinct_ratio > 0.5:
        return (
            "coordinate_or_index_candidate",
            "high",
            1,
            "Sequence-like numeric structure; role remains provisional.",
            "sequence_or_coordinate_candidate",
        )
    if value_range > 100 and distinct_ratio > 0.5 and spread > 0 and context_gap > spread:
        return (
            "coordinate_or_index_candidate",
            "medium",
            1,
            "Broad context-separated numeric coordinate-like structure.",
            "sequence_or_coordinate_candidate",
        )
    if repeated_value_fraction > 0.95 and distinct_count <= 200:
        if numeric_median is not None and 0 < numeric_median < 0.2 and (numeric_max or 0) > 1:
            return (
                "uncertainty_or_weight_candidate",
                "medium",
                1,
                "Positive repeated-scale field with small median and large tail; role remains provisional.",
                "uncertainty_or_weight_candidate",
            )
        if numeric_mean is not None and 0.7 <= numeric_mean <= 1.5 and spread < 0.2:
            return (
                "processing_or_control_candidate",
                "medium",
                0,
                "Narrow repeated numeric states look control-like, not a primary fingerprint field.",
                "context_control_candidate",
            )
        return (
            "configuration_parameter_candidate",
            "medium",
            0,
            "Highly repeated field looks configuration-like.",
            "context_control_candidate",
        )
    if numeric_min is not None and numeric_min > 0 and numeric_median is not None:
        if median_abs < 10 and (numeric_max or 0) / max(median_abs, 1.0e-12) < 30:
            return (
                "uncertainty_or_weight_candidate",
                "medium",
                1,
                "Positive continuous field has a plausible structural uncertainty/weight role.",
                "uncertainty_or_weight_candidate",
            )
    if numeric_min is not None and numeric_min > 0 and distinct_ratio > 0.5:
        return (
            "signal_value_candidate",
            "medium",
            1,
            "Broad positive continuous variation may support a structural fingerprint.",
            "primary_numeric_signal_candidate",
        )
    if integer_like_fraction > 0.98 and distinct_count < 100:
        return (
            "categorical_numeric_candidate",
            "medium",
            0,
            "Integer-like repeated states look categorical.",
            "context_control_candidate",
        )
    return (
        "unresolved_numeric_candidate",
        "low",
        0,
        "Observed structure is numeric but not enough for provisional role approval.",
        "No provisional role approved.",
    )


def profile_candidate(
    con: sqlite3.Connection,
    candidate: dict[str, Any],
    index: int,
    created_at: str,
) -> tuple[dict[str, Any], dict[str, float]]:
    token_position = str(candidate["token_position"])
    line_type = str(candidate["line_type"])
    values = load_field_values(con, token_position, line_type)
    expected_rows = table_count_for_line_type(con, line_type)
    populated_values = [
        row for row in values if row["raw_value"] is not None and str(row["raw_value"]).strip() != ""
    ]
    numeric_rows: list[tuple[dict[str, Any], float]] = []
    for row in values:
        parsed = parse_numeric(row["raw_value"])
        if parsed is not None:
            numeric_rows.append((row, parsed))

    numeric_values = [value for _, value in numeric_rows]
    distinct_values = len(set(numeric_values))
    sqlite_counts: dict[str, int] = {}
    for row in values:
        key = str(row["sqlite_type"])
        sqlite_counts[key] = sqlite_counts.get(key, 0) + 1
    ordered_values = [(int(row["record_index"]), value) for row, value in numeric_rows]
    mono_status, mono_counts = monotonicity_status(ordered_values)
    context_a_values = [value for row, value in numeric_rows if int(row["in_context_a"]) == 1]
    context_b_values = [value for row, value in numeric_rows if int(row["in_context_b"]) == 1]
    integer_like_fraction = (
        sum(1 for value in numeric_values if abs(value - round(value)) <= 1.0e-9) / len(numeric_values)
        if numeric_values
        else 0.0
    )
    zero_fraction = (
        sum(1 for value in numeric_values if abs(value) <= 1.0e-12) / len(numeric_values)
        if numeric_values
        else 0.0
    )
    repeated_value_fraction = (
        (len(numeric_values) - distinct_values) / len(numeric_values)
        if numeric_values
        else 0.0
    )
    numeric_min = min(numeric_values) if numeric_values else None
    numeric_max = max(numeric_values) if numeric_values else None
    numeric_mean = safe_mean(numeric_values)
    numeric_median = safe_median(numeric_values)
    numeric_stddev = safe_stddev(numeric_values)
    context_a_mean = safe_mean(context_a_values)
    context_b_mean = safe_mean(context_b_values)
    proposed_class, confidence, usable_now, limitation, approved_role = classify_profile(
        len(numeric_values),
        distinct_values,
        numeric_min,
        numeric_max,
        numeric_mean,
        numeric_median,
        numeric_stddev,
        integer_like_fraction,
        repeated_value_fraction,
        mono_status,
        context_a_mean,
        context_b_mean,
    )
    notes = (
        f"line_type={line_type}; source_feature_id={candidate['feature_availability_id']}; "
        f"sequence_counts={mono_counts}; context_a_label={CONTEXT_A_LABEL}; "
        f"context_b_label={CONTEXT_B_LABEL}; approved_role={approved_role}."
    )
    profile = {
        "numeric_field_profile_id": f"SHAPIROMART02_PROFILE_{index:03d}",
        "source_table": candidate["source_table"],
        "source_field": candidate["source_field"],
        "token_position": token_position,
        "populated_row_count": len(populated_values),
        "numeric_row_count": len(numeric_values),
        "null_or_blank_count": max(expected_rows - len(populated_values), 0),
        "distinct_value_count": distinct_values,
        "sqlite_type_summary": "; ".join(f"{key}:{sqlite_counts[key]}" for key in sorted(sqlite_counts)),
        "numeric_min": numeric_min,
        "numeric_max": numeric_max,
        "numeric_mean": numeric_mean,
        "numeric_median": numeric_median,
        "numeric_stddev": numeric_stddev,
        "integer_like_fraction": integer_like_fraction,
        "zero_fraction": zero_fraction,
        "repeated_value_fraction": repeated_value_fraction,
        "monotonicity_status": mono_status,
        "context_a_count": len(context_a_values),
        "context_b_count": len(context_b_values),
        "context_a_mean": context_a_mean,
        "context_b_mean": context_b_mean,
        "proposed_structural_class": proposed_class,
        "classification_confidence": confidence,
        "usable_for_first_fingerprint": usable_now,
        "limitation": limitation,
        "created_at_utc": created_at,
        "notes": notes,
    }
    aligned = {str(row["raw_record_id"]): value for row, value in numeric_rows}
    return profile, aligned


def table_count_for_line_type(con: sqlite3.Connection, line_type: str) -> int:
    row = con.execute(
        "SELECT COUNT(*) AS n FROM raw_record WHERE line_type = ?",
        (line_type,),
    ).fetchone()
    return int(row["n"])


def pair_relation_status(correlation: float | None, aligned_count: int) -> tuple[str, str]:
    if aligned_count < 3 or correlation is None:
        return "insufficient_aligned_rows", "No structural relation assessed."
    abs_corr = abs(correlation)
    direction = "positive" if correlation >= 0 else "negative"
    if abs_corr >= 0.95:
        strength = "very_strong"
    elif abs_corr >= 0.70:
        strength = "strong"
    elif abs_corr >= 0.30:
        strength = "moderate"
    else:
        strength = "weak"
    return (
        f"{strength}_{direction}_descriptive_relation",
        "Record-aligned descriptive correlation only; no interpretation assigned.",
    )


def build_pair_rows(
    profiles: list[dict[str, Any]],
    aligned_values: dict[str, dict[str, float]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for i, profile_a in enumerate(profiles):
        for profile_b in profiles[i + 1 :]:
            field_a = str(profile_a["source_field"])
            field_b = str(profile_b["source_field"])
            values_a = aligned_values[field_a]
            values_b = aligned_values[field_b]
            common_ids = sorted(set(values_a).intersection(values_b))
            xs = [values_a[record_id] for record_id in common_ids]
            ys = [values_b[record_id] for record_id in common_ids]
            corr = pearson(xs, ys)
            relation_status, relation_note = pair_relation_status(corr, len(common_ids))
            rows.append(
                {
                    "numeric_field_pair_relation_id": f"SHAPIROMART02_PAIR_{len(rows) + 1:03d}",
                    "source_field_a": field_a,
                    "source_field_b": field_b,
                    "aligned_row_count": len(common_ids),
                    "pearson_correlation": corr,
                    "relation_status": relation_status,
                    "possible_structural_relation": relation_note,
                    "created_at_utc": created_at,
                    "notes": "Rows aligned by raw_record_id within workcopy raw_field_value/raw_record.",
                }
            )
    return rows


def build_review_rows(profiles: list[dict[str, Any]], created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, profile in enumerate(profiles, start=1):
        approved = int(profile["usable_for_first_fingerprint"])
        if approved:
            if profile["proposed_structural_class"] == "signal_value_candidate":
                approved_role = "primary_numeric_signal_candidate"
            elif profile["proposed_structural_class"] == "coordinate_or_index_candidate":
                approved_role = "sequence_or_coordinate_candidate"
            elif profile["proposed_structural_class"] == "uncertainty_or_weight_candidate":
                approved_role = "uncertainty_or_weight_candidate"
            else:
                approved_role = "context_control_candidate"
            review_status = "provisionally_approved_structural_role"
            followup = "Carry role into a reviewed feature dictionary before fingerprint build."
        else:
            approved_role = None
            review_status = "not_approved_for_first_fingerprint"
            followup = "Keep field visible but do not use until role review is resolved."
        rows.append(
            {
                "numeric_field_review_id": f"SHAPIROMART02_REVIEW_{index:03d}",
                "source_field": profile["source_field"],
                "proposed_structural_class": profile["proposed_structural_class"],
                "approved_for_first_fingerprint": approved,
                "approved_role": approved_role,
                "review_status": review_status,
                "required_followup": followup,
                "created_at_utc": created_at,
                "notes": profile["limitation"],
            }
        )
    return rows


def build_readiness_rows(profiles: list[dict[str, Any]], review_rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    approved = [row for row in review_rows if int(row["approved_for_first_fingerprint"]) == 1]
    signal_count = sum(1 for row in approved if row["approved_role"] == "primary_numeric_signal_candidate")
    coordinate_count = sum(1 for row in approved if row["approved_role"] == "sequence_or_coordinate_candidate")
    uncertainty_count = sum(1 for row in approved if row["approved_role"] == "uncertainty_or_weight_candidate")
    blocked = []
    if signal_count == 0:
        blocked.append("no_primary_numeric_signal_candidate")
    if coordinate_count == 0:
        blocked.append("no_sequence_or_coordinate_candidate")
    if uncertainty_count == 0:
        blocked.append("no_uncertainty_or_weight_candidate")
    unresolved = sum(1 for row in profiles if row["proposed_structural_class"] == "unresolved_numeric_candidate")
    if unresolved:
        blocked.append("some_numeric_fields_unresolved")
    readiness_status = "structural_minimum_available_pending_review" if not blocked else "blocked_or_partial"
    if approved and not blocked:
        blocking_note = "Structural minimum is present, but roles remain provisional."
    else:
        blocking_note = "; ".join(blocked)
    return [
        {
            "readiness_metric": "candidate_field_count",
            "metric_value": str(len(profiles)),
            "readiness_status": readiness_status,
            "notes": "Exactly nine SHAPIROMART01 candidate fields were inspected.",
        },
        {
            "readiness_metric": "approved_field_count",
            "metric_value": str(len(approved)),
            "readiness_status": readiness_status,
            "notes": blocking_note,
        },
        {
            "readiness_metric": "approved_primary_signal_candidates",
            "metric_value": str(signal_count),
            "readiness_status": readiness_status,
            "notes": "Structural role only; no final meaning assigned.",
        },
        {
            "readiness_metric": "approved_coordinate_candidates",
            "metric_value": str(coordinate_count),
            "readiness_status": readiness_status,
            "notes": "Sequence/index or coordinate-like role only.",
        },
        {
            "readiness_metric": "approved_uncertainty_weight_candidates",
            "metric_value": str(uncertainty_count),
            "readiness_status": readiness_status,
            "notes": "Uncertainty/weight role remains provisional.",
        },
    ]


def build_next_step_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "SHAPIROMART03_RECOMMENDED_001",
            "recommended_next_step": (
                "Create a reviewed minimal feature dictionary that names the "
                "approved structural roles and records why configuration/control "
                "fields are excluded from the first fingerprint."
            ),
            "why_this_step": (
                "SHAPIROMART02 found provisional structural candidates, but the "
                "roles must be reviewed before building a fingerprint table."
            ),
            "db_write_expected": "yes_in_separate_explicit_task",
            "claim_boundary": "Feature dictionary review is still not result analysis.",
        }
    ]


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS mart_shapiro_numeric_field_profile (
            numeric_field_profile_id TEXT PRIMARY KEY,
            source_table TEXT NOT NULL,
            source_field TEXT NOT NULL,
            token_position TEXT,
            populated_row_count INTEGER,
            numeric_row_count INTEGER,
            null_or_blank_count INTEGER,
            distinct_value_count INTEGER,
            sqlite_type_summary TEXT,
            numeric_min REAL,
            numeric_max REAL,
            numeric_mean REAL,
            numeric_median REAL,
            numeric_stddev REAL,
            integer_like_fraction REAL,
            zero_fraction REAL,
            repeated_value_fraction REAL,
            monotonicity_status TEXT,
            context_a_count INTEGER,
            context_b_count INTEGER,
            context_a_mean REAL,
            context_b_mean REAL,
            proposed_structural_class TEXT NOT NULL,
            classification_confidence TEXT NOT NULL,
            usable_for_first_fingerprint INTEGER NOT NULL,
            limitation TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_numeric_field_pair_relation (
            numeric_field_pair_relation_id TEXT PRIMARY KEY,
            source_field_a TEXT NOT NULL,
            source_field_b TEXT NOT NULL,
            aligned_row_count INTEGER NOT NULL,
            pearson_correlation REAL,
            relation_status TEXT NOT NULL,
            possible_structural_relation TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_numeric_field_review (
            numeric_field_review_id TEXT PRIMARY KEY,
            source_field TEXT NOT NULL,
            proposed_structural_class TEXT NOT NULL,
            approved_for_first_fingerprint INTEGER NOT NULL,
            approved_role TEXT,
            review_status TEXT NOT NULL,
            required_followup TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS shapiromart02_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            candidate_field_count INTEGER,
            profiled_field_count INTEGER,
            pair_relation_count INTEGER,
            approved_field_count INTEGER,
            unresolved_field_count INTEGER,
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
        CREATE VIEW qsb_v_shapiromart02_numeric_field_profiles AS
        SELECT *
        FROM mart_shapiro_numeric_field_profile
        ORDER BY numeric_field_profile_id;

        CREATE VIEW qsb_v_shapiromart02_candidate_roles AS
        SELECT
            r.numeric_field_review_id,
            p.token_position,
            r.source_field,
            r.proposed_structural_class,
            r.approved_for_first_fingerprint,
            r.approved_role,
            r.review_status,
            r.required_followup,
            p.context_a_count,
            p.context_b_count
        FROM mart_shapiro_numeric_field_review AS r
        JOIN mart_shapiro_numeric_field_profile AS p
          ON p.source_field = r.source_field
        ORDER BY r.numeric_field_review_id;

        CREATE VIEW qsb_v_shapiromart02_pair_relations AS
        SELECT *
        FROM mart_shapiro_numeric_field_pair_relation
        ORDER BY numeric_field_pair_relation_id;

        CREATE VIEW qsb_v_shapiromart02_first_fingerprint_readiness AS
        SELECT
            'candidate_field_count' AS readiness_metric,
            CAST(COUNT(*) AS TEXT) AS metric_value,
            CASE WHEN COUNT(*) = 9 THEN 'candidate_count_ok' ELSE 'candidate_count_mismatch' END AS readiness_status,
            'Exactly nine fields are required by SHAPIROMART02.' AS notes
        FROM mart_shapiro_numeric_field_profile
        UNION ALL
        SELECT
            'approved_field_count',
            CAST(SUM(approved_for_first_fingerprint) AS TEXT),
            CASE WHEN SUM(approved_for_first_fingerprint) > 0
                 THEN 'provisional_structural_fields_available'
                 ELSE 'blocked_no_approved_structural_fields'
            END,
            'Approval is structural and provisional only.'
        FROM mart_shapiro_numeric_field_review
        UNION ALL
        SELECT
            'approved_primary_signal_candidates',
            CAST(SUM(CASE WHEN approved_role = 'primary_numeric_signal_candidate' THEN 1 ELSE 0 END) AS TEXT),
            'role_count',
            'Structural role only.'
        FROM mart_shapiro_numeric_field_review
        UNION ALL
        SELECT
            'approved_coordinate_candidates',
            CAST(SUM(CASE WHEN approved_role = 'sequence_or_coordinate_candidate' THEN 1 ELSE 0 END) AS TEXT),
            'role_count',
            'Structural role only.'
        FROM mart_shapiro_numeric_field_review
        UNION ALL
        SELECT
            'approved_uncertainty_weight_candidates',
            CAST(SUM(CASE WHEN approved_role = 'uncertainty_or_weight_candidate' THEN 1 ELSE 0 END) AS TEXT),
            'role_count',
            'Structural role only.'
        FROM mart_shapiro_numeric_field_review;
        """
    )


def validate_new_objects(con: sqlite3.Connection) -> dict[str, Any]:
    missing: list[str] = []
    table_counts: dict[str, int] = {}
    view_counts: dict[str, int] = {}
    for table in TARGET_TABLES:
        if not object_exists(con, table, "table"):
            missing.append(f"table:{table}")
        else:
            table_counts[table] = table_count(con, table)
    for view in TARGET_VIEWS:
        if not object_exists(con, view, "view"):
            missing.append(f"view:{view}")
        else:
            view_counts[view] = table_count(con, view)
    if missing:
        fail("Missing SHAPIROMART02 objects: " + "; ".join(missing))
    return {"table_counts": table_counts, "view_counts": view_counts}


def query_rows(con: sqlite3.Connection, table_or_view: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(table_or_view)} ORDER BY 1")


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
    profiles: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    next_step_rows: list[dict[str, str]],
) -> None:
    def tokens_for(class_name: str) -> str:
        values = [
            str(row["token_position"])
            for row in profiles
            if row["proposed_structural_class"] == class_name
        ]
        return ", ".join(values) if values else "none"

    approved = [
        row for row in review_rows if int(row["approved_for_first_fingerprint"]) == 1
    ]
    rejected = [
        row for row in review_rows if int(row["approved_for_first_fingerprint"]) == 0
    ]
    both_contexts = [
        row
        for row in profiles
        if int(row["context_a_count"]) > 0 and int(row["context_b_count"]) > 0
    ]
    readiness_note = "; ".join(
        f"{row['readiness_metric']}={row['metric_value']}" for row in readiness_rows
    )
    next_step = next_step_rows[0]["recommended_next_step"]

    lines = [
        "# QSB-SHAPIROMART02 Numeric Candidate Field Inspection",
        "",
        "## 1. Executive summary",
        "",
        (
            "Befund: SHAPIROMART02 inspected the nine SHAPIROMART01 numeric "
            "candidate fields and classified them by observed structure only."
        ),
        "",
        f"- Candidate fields inspected: {len(profiles)}",
        f"- Fields available in both receiver contexts: {len(both_contexts)}",
        f"- Provisionally approved fields: {len(approved)}",
        f"- Not approved fields: {len(rejected)}",
        f"- Pair relations computed: {summary['counts']['pair_relation_count']}",
        "",
        "## 2. The nine candidate fields",
        "",
    ]
    for row in profiles:
        lines.append(
            "- {token_position}: {source_field}; class={proposed_structural_class}; "
            "A_count={context_a_count}; B_count={context_b_count}; usable={usable_for_first_fingerprint}".format(**row)
        )

    lines.extend(
        [
            "",
            "## 3. Sequence/index-like fields",
            "",
            tokens_for("coordinate_or_index_candidate"),
            "",
            "## 4. Possible signal-value fields",
            "",
            tokens_for("signal_value_candidate"),
            "",
            "## 5. Possible uncertainty/weight fields",
            "",
            tokens_for("uncertainty_or_weight_candidate"),
            "",
            "## 6. Configuration-like or categorical fields",
            "",
            ", ".join(
                token
                for token in [
                    tokens_for("configuration_parameter_candidate"),
                    tokens_for("categorical_numeric_candidate"),
                    tokens_for("processing_or_control_candidate"),
                ]
                if token != "none"
            )
            or "none",
            "",
            "## 7. Constant or unusable fields",
            "",
            ", ".join(
                token
                for token in [
                    tokens_for("constant_or_near_constant"),
                    tokens_for("unresolved_numeric_candidate"),
                ]
                if token != "none"
            )
            or "none",
            "",
            "## 8. Context A/B availability",
            "",
        ]
    )
    for row in profiles:
        lines.append(
            "- {token_position}: context_a_count={context_a_count}; context_b_count={context_b_count}; "
            "context_a_mean={context_a_mean}; context_b_mean={context_b_mean}".format(**row)
        )

    lines.extend(
        [
            "",
            "## 9. Minimal first structural fingerprint set",
            "",
        ]
    )
    if approved:
        for row in approved:
            lines.append(
                "- {source_field}: role={approved_role}; review_status={review_status}".format(**row)
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## 10. Blocking gap and next step",
            "",
            "Main blocking gap: provisional roles still require reviewed feature-dictionary approval before a fingerprint table is built.",
            "",
            f"Readiness summary: {readiness_note}",
            "",
            f"Single next concrete step: {next_step}",
            "",
            "## 11. Validation and claim boundary",
            "",
            f"- Live DB unchanged: {summary['validation']['live_db_unchanged']}",
            f"- Workcopy DB modified: {summary['validation']['workcopy_db_modified']}",
            f"- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}",
            f"- Workcopy foreign-key violations: {summary['validation']['workcopy_foreign_key_violation_count']}",
            f"- SHAPIROMART01 counts preserved: {summary['validation']['shapiromart01_counts_preserved']}",
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
    profiles: list[dict[str, Any]],
    pair_rows: list[dict[str, Any]],
    review_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    next_step_rows: list[dict[str, str]],
) -> None:
    paths = output_paths(output_root)
    write_csv(
        paths[PROFILE_CSV],
        profiles,
        [
            "numeric_field_profile_id",
            "source_table",
            "source_field",
            "token_position",
            "populated_row_count",
            "numeric_row_count",
            "null_or_blank_count",
            "distinct_value_count",
            "sqlite_type_summary",
            "numeric_min",
            "numeric_max",
            "numeric_mean",
            "numeric_median",
            "numeric_stddev",
            "integer_like_fraction",
            "zero_fraction",
            "repeated_value_fraction",
            "monotonicity_status",
            "context_a_count",
            "context_b_count",
            "context_a_mean",
            "context_b_mean",
            "proposed_structural_class",
            "classification_confidence",
            "usable_for_first_fingerprint",
            "limitation",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[PAIR_CSV],
        pair_rows,
        [
            "numeric_field_pair_relation_id",
            "source_field_a",
            "source_field_b",
            "aligned_row_count",
            "pearson_correlation",
            "relation_status",
            "possible_structural_relation",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[ROLE_REVIEW_CSV],
        review_rows,
        [
            "numeric_field_review_id",
            "source_field",
            "proposed_structural_class",
            "approved_for_first_fingerprint",
            "approved_role",
            "review_status",
            "required_followup",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[READINESS_CSV],
        readiness_rows,
        ["readiness_metric", "metric_value", "readiness_status", "notes"],
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
    write_readout(paths[READOUT_MD], summary, profiles, review_rows, readiness_rows, next_step_rows)


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
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
    run_id = "SHAPIROMART02_RUN_001"

    with connect_writable(args.workcopy_db) as con:
        validate_required_tables(con)
        existing_target_state = validate_existing_target_state(con, args.allow_existing)
        pre_integrity = integrity_check(con)
        pre_fk = foreign_key_violations(con)
        if pre_integrity != "ok":
            fail(f"Workcopy DB integrity_check failed before run: {pre_integrity}")
        if pre_fk:
            fail(f"Workcopy DB foreign-key violations before run: {len(pre_fk)}")
        before_sm01_counts = shapiromart01_counts(con)
        before_mapping_digest = stable_digest(mapping_separation_rows(con))

        candidates = load_candidate_fields(con)
        profiles: list[dict[str, Any]] = []
        aligned_by_source_field: dict[str, dict[str, float]] = {}
        for index, candidate in enumerate(candidates, start=1):
            profile, aligned = profile_candidate(con, candidate, index, created_at)
            profiles.append(profile)
            aligned_by_source_field[str(profile["source_field"])] = aligned
        if len(profiles) != 9:
            fail(f"Expected nine profiled fields, built {len(profiles)}.")
        pair_rows = build_pair_rows(profiles, aligned_by_source_field, created_at)
        review_rows = build_review_rows(profiles, created_at)
        readiness_rows = build_readiness_rows(profiles, review_rows)
        next_step_rows = build_next_step_rows()
        approved_count = sum(1 for row in review_rows if int(row["approved_for_first_fingerprint"]) == 1)
        unresolved_count = sum(
            1 for row in profiles if row["proposed_structural_class"] == "unresolved_numeric_candidate"
        )

        try:
            con.execute("BEGIN")
            create_tables(con)
            if args.allow_existing:
                clear_target_tables(con)
            insert_rows(con, "mart_shapiro_numeric_field_profile", profiles)
            insert_rows(con, "mart_shapiro_numeric_field_pair_relation", pair_rows)
            insert_rows(con, "mart_shapiro_numeric_field_review", review_rows)
            insert_rows(
                con,
                "shapiromart02_run_log",
                [
                    {
                        "run_id": run_id,
                        "run_timestamp_utc": created_at,
                        "candidate_field_count": len(candidates),
                        "profiled_field_count": len(profiles),
                        "pair_relation_count": len(pair_rows),
                        "approved_field_count": approved_count,
                        "unresolved_field_count": unresolved_count,
                        "live_db_modified": 0,
                        "workcopy_db_modified": 1,
                        "integrity_check_result": "pending_post_commit_validation",
                        "foreign_key_violation_count": -1,
                        "notes": CLAIM_BOUNDARY,
                    }
                ],
            )
            create_views(con)
            con.commit()
        except Exception:
            con.rollback()
            raise

        post_integrity = integrity_check(con)
        post_fk = foreign_key_violations(con)
        if post_integrity != "ok":
            fail(f"Workcopy DB integrity_check failed after run: {post_integrity}")
        if post_fk:
            fail(f"Workcopy DB foreign-key violations after run: {len(post_fk)}")
        con.execute(
            """
            UPDATE shapiromart02_run_log
            SET integrity_check_result = ?,
                foreign_key_violation_count = ?
            WHERE run_id = ?
            """,
            (post_integrity, len(post_fk), run_id),
        )
        con.commit()

        new_object_validation = validate_new_objects(con)
        db_profiles = query_rows(con, "mart_shapiro_numeric_field_profile")
        db_pair_rows = query_rows(con, "mart_shapiro_numeric_field_pair_relation")
        db_review_rows = query_rows(con, "mart_shapiro_numeric_field_review")
        db_readiness_rows = query_rows(con, "qsb_v_shapiromart02_first_fingerprint_readiness")
        db_next_step_rows = next_step_rows
        after_sm01_counts = shapiromart01_counts(con)
        after_mapping_rows = mapping_separation_rows(con)
        after_mapping_digest = stable_digest(after_mapping_rows)
        supported_terms_after = {
            str(row["term"])
            for row in after_mapping_rows
            if row["separation_class"] == "supported"
        }

    live_after = db_state(args.live_db)
    workcopy_after = db_state(args.workcopy_db)
    live_unchanged = live_before == live_after
    workcopy_modified = workcopy_before != workcopy_after
    if not live_unchanged:
        fail("Live DB checksum/stat changed during SHAPIROMART02.")
    if not workcopy_modified:
        fail("Workcopy DB was not modified; expected SHAPIROMART02 rows/objects.")

    sm01_counts_preserved = before_sm01_counts == after_sm01_counts
    mapping_preserved = before_mapping_digest == after_mapping_digest
    compound_not_promoted = not any(label in supported_terms_after for label in OPEN_COMPOUND_LABELS)
    if not sm01_counts_preserved:
        fail("Existing SHAPIROMART01 table counts changed.")
    if not mapping_preserved:
        fail("Supported/open mapping separation changed.")
    if not compound_not_promoted:
        fail("Compound label appeared in supported mapping terms.")

    summary: dict[str, Any] = {
        "script_name": SCRIPT_NAME,
        "task": "QSB-SHAPIROMART02",
        "paths": {
            "live_db": str(args.live_db),
            "workcopy_db": str(args.workcopy_db),
            "output_root": str(args.output_root),
        },
        "counts": {
            "candidate_field_count": len(candidates),
            "profiled_field_count": len(db_profiles),
            "pair_relation_count": len(db_pair_rows),
            "approved_field_count": sum(
                1 for row in db_review_rows if int(row["approved_for_first_fingerprint"]) == 1
            ),
            "unresolved_field_count": sum(
                1 for row in db_profiles if row["proposed_structural_class"] == "unresolved_numeric_candidate"
            ),
        },
        "validation": {
            "live_integrity_check": live_integrity,
            "live_foreign_key_violation_count": len(live_fk),
            "live_db_unchanged": live_unchanged,
            "workcopy_db_modified": workcopy_modified,
            "workcopy_integrity_check": post_integrity,
            "workcopy_foreign_key_violation_count": len(post_fk),
            "existing_target_state": existing_target_state,
            "new_objects": new_object_validation,
            "shapiromart01_counts_before": before_sm01_counts,
            "shapiromart01_counts_after": after_sm01_counts,
            "shapiromart01_counts_preserved": sm01_counts_preserved,
            "mapping_separation_preserved": mapping_preserved,
            "compound_labels_not_promoted": compound_not_promoted,
            "live_db_state_before": live_before,
            "live_db_state_after": live_after,
            "workcopy_db_state_before": workcopy_before,
            "workcopy_db_state_after": workcopy_after,
        },
        "numeric_field_profiles": db_profiles,
        "numeric_field_pair_relations": db_pair_rows,
        "candidate_role_review": db_review_rows,
        "first_fingerprint_readiness": db_readiness_rows,
        "next_step_rows": db_next_step_rows,
        "workcopy_modified_objects": TARGET_TABLES + TARGET_VIEWS,
        "claim_boundary": CLAIM_BOUNDARY,
    }

    write_outputs(
        args.output_root,
        summary,
        db_profiles,
        db_pair_rows,
        db_review_rows,
        db_readiness_rows,
        db_next_step_rows,
    )
    return {"summary": summary, "output_files": output_paths(args.output_root)}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect the nine SHAPIROMART01 numeric candidate fields and record "
            "small SHAPIROMART02 structural profiles."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing SHAPIROMART02 output files.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow an explicit rerun over existing SHAPIROMART02 target tables.",
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
    print("QSB-SHAPIROMART02 numeric candidate field inspection complete.")
    print(f"Candidate fields: {counts['candidate_field_count']}")
    print(f"Profiled fields: {counts['profiled_field_count']}")
    print(f"Pair relations: {counts['pair_relation_count']}")
    print(f"Approved fields: {counts['approved_field_count']}")
    print(f"Unresolved fields: {counts['unresolved_field_count']}")
    print(f"Live DB unchanged: {summary['validation']['live_db_unchanged']}")
    print(f"Workcopy DB modified: {summary['validation']['workcopy_db_modified']}")
    print(f"Output root: {summary['paths']['output_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
