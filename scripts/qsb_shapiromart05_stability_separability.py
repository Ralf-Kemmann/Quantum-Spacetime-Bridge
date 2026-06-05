#!/usr/bin/env python3
"""QSB-SHAPIROMART05: descriptive stability and separability.

This script reads complete SHAPIROMART04 fingerprints from the workcopy DB and
builds descriptive within-context stability and between-context separability
tables. It does not read raw TIM/PAR files, alter the live DB, weight rows,
impute values, cluster records, or compute inferential quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sqlite3
import statistics
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart05_stability_separability.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART05_STABILITY_SEPARABILITY"
)

READOUT_MD = "shapiromart05_readout.md"
SUMMARY_JSON = "shapiromart05_summary.json"
WITHIN_CONTEXT_CSV = "shapiromart05_within_context_stability.csv"
CENTROIDS_CSV = "shapiromart05_context_centroids.csv"
DIMENSION_SEPARABILITY_CSV = "shapiromart05_dimension_separability.csv"
BETWEEN_CONTEXT_CSV = "shapiromart05_between_context_separability.csv"
NEXT_STEP_CSV = "shapiromart05_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    WITHIN_CONTEXT_CSV,
    CENTROIDS_CSV,
    DIMENSION_SEPARABILITY_CSV,
    BETWEEN_CONTEXT_CSV,
    NEXT_STEP_CSV,
]

TARGET_TABLES = [
    "mart_shapiro_within_context_stability",
    "mart_shapiro_context_centroid",
    "mart_shapiro_dimension_separability",
    "mart_shapiro_between_context_separability",
    "shapiromart05_run_log",
]

TARGET_VIEWS = [
    "qsb_v_shapiromart05_dashboard",
    "qsb_v_shapiromart05_within_context_stability",
    "qsb_v_shapiromart05_context_centroids",
    "qsb_v_shapiromart05_dimension_separability",
    "qsb_v_shapiromart05_between_context_separability",
]

REQUIRED_OBJECTS = [
    ("mart_shapiro_structural_fingerprint", "table"),
    ("mart_shapiro_fingerprint_context_summary", "table"),
    ("mart_shapiro_fingerprint_context_difference", "table"),
    ("mart_shapiro_fingerprint_build_gap", "table"),
    ("shapiromart04_run_log", "table"),
    ("qsb_v_shapiromart04_complete_fingerprints", "view"),
    ("qsb_v_shapiromart04_context_summary", "view"),
    ("qsb_v_shapiromart04_context_difference", "view"),
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

SHAPIROMART04_TABLES = [
    "mart_shapiro_structural_fingerprint",
    "mart_shapiro_fingerprint_context_summary",
    "mart_shapiro_fingerprint_context_difference",
    "mart_shapiro_fingerprint_build_gap",
    "shapiromart04_run_log",
]

PRIOR_TABLE_SETS = {
    "SHAPIROMART01": SHAPIROMART01_TABLES,
    "SHAPIROMART02": SHAPIROMART02_TABLES,
    "SHAPIROMART03": SHAPIROMART03_TABLES,
    "SHAPIROMART04": SHAPIROMART04_TABLES,
}

CONTEXT_A_RECEIVER = "Rcvr_800"
CONTEXT_B_RECEIVER = "Rcvr1_2"
SUPPORTED_BACKEND = "GUPPI"
EXPECTED_SCIENCE_OBJECT = "J0740+6620"
EXPECTED_COMPLETE_TOTAL = 7419
EXPECTED_CONTEXT_COUNTS = {
    CONTEXT_A_RECEIVER: 2916,
    CONTEXT_B_RECEIVER: 4503,
}
CONTEXT_ORDER = {
    CONTEXT_A_RECEIVER: 1,
    CONTEXT_B_RECEIVER: 2,
}

DIMENSIONS = [
    ("coordinate_primary", "coordinate_primary"),
    ("coordinate_secondary", "coordinate_secondary"),
    ("signal_value_primary", "signal_value_primary"),
    ("signal_value_secondary", "signal_value_secondary"),
]

CENTROID_FIELDS = {
    "coordinate_primary": "coordinate_primary_centroid",
    "coordinate_secondary": "coordinate_secondary_centroid",
    "signal_value_primary": "signal_primary_centroid",
    "signal_value_secondary": "signal_secondary_centroid",
}

STABILITY_STATUSES = {
    "compact_relative_to_scale",
    "moderate_internal_spread",
    "broad_internal_spread",
    "not_assessable",
}

DIMENSION_STATUSES = {
    "clear_descriptive_shift",
    "moderate_descriptive_shift",
    "small_descriptive_shift",
    "broad_overlap",
    "not_assessable",
}

INTERPRETATION_STATUS = "descriptive_only_no_physical_interpretation"
NEXT_STEP = (
    "Identify and attach a geometry/Shapiro-exposure axis while holding "
    "receiver/backend context fixed."
)

CLAIM_BOUNDARY = (
    "SHAPIROMART05 is a descriptive stability and separability readout only. "
    "It does not compute TOAs, delays, residuals, model quantities, p-values, "
    "confidence intervals, or assign physical interpretation."
)

HEURISTIC_NOTES = (
    "Stability status uses IQR divided by the larger absolute mean/median scale: "
    "<=0.10 compact, <=0.75 moderate, otherwise broad. Dimension shift status "
    "uses absolute standardized mean difference: >=2 clear, >=1 moderate, "
    ">=0.2 small, otherwise broad overlap. Between-context status compares raw "
    "centroid distance to the arithmetic mean of within-context centroid "
    "distances and records p05-p95 overlap by dimension."
)

EPSILON = 1.0e-12


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


def percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    if p < 0.0 or p > 1.0:
        fail(f"Invalid percentile fraction: {p}")
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    position = (len(ordered) - 1) * p
    lower = int(math.floor(position))
    upper = int(math.ceil(position))
    if lower == upper:
        return float(ordered[lower])
    fraction = position - lower
    return float(ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction)


def mad(values: list[float], median_value: float | None) -> float | None:
    if not values or median_value is None:
        return None
    return safe_median([abs(value - median_value) for value in values])


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
            "SHAPIROMART05 output files already exist. Use --overwrite to replace: "
            + "; ".join(existing_outputs)
        )


def validate_required_objects(con: sqlite3.Connection) -> None:
    missing: list[str] = []
    for name, object_type in REQUIRED_OBJECTS:
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
            "SHAPIROMART05 target objects already exist. Use --allow-existing "
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


def load_complete_fingerprints(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT
            structural_fingerprint_id,
            raw_record_id,
            science_object_id,
            receiver_context,
            backend_context,
            coordinate_primary,
            coordinate_secondary,
            signal_value_primary,
            signal_value_secondary
        FROM qsb_v_shapiromart04_complete_fingerprints
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            structural_fingerprint_id
        """,
    )
    if len(rows) != EXPECTED_COMPLETE_TOTAL:
        fail(f"Expected {EXPECTED_COMPLETE_TOTAL} complete fingerprints, found {len(rows)}.")
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        receiver = str(row["receiver_context"])
        counts[receiver] += 1
        if str(row["science_object_id"]) != EXPECTED_SCIENCE_OBJECT:
            fail(f"Unexpected science_object_id: {row['science_object_id']}")
        if str(row["backend_context"]) != SUPPORTED_BACKEND:
            fail(f"Unexpected backend_context: {row['backend_context']}")
        for dimension, column in DIMENSIONS:
            value = row[column]
            if value is None:
                fail(f"Complete fingerprint has null {dimension}: {row['raw_record_id']}")
            parsed = float(value)
            if not math.isfinite(parsed):
                fail(f"Complete fingerprint has non-finite {dimension}: {row['raw_record_id']}")
            row[column] = parsed
    if dict(counts) != EXPECTED_CONTEXT_COUNTS:
        fail(
            "Context complete counts mismatch. expected="
            + json.dumps(EXPECTED_CONTEXT_COUNTS, sort_keys=True)
            + " actual="
            + json.dumps(dict(counts), sort_keys=True)
        )
    return rows


def group_by_context(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row["receiver_context"])].append(row)
    return dict(sorted(grouped.items(), key=lambda item: CONTEXT_ORDER.get(item[0], 99)))


def dimension_values(rows: list[dict[str, Any]], column: str) -> list[float]:
    return [float(row[column]) for row in rows]


def classify_stability(
    count: int,
    mean_value: float | None,
    median_value: float | None,
    iqr_value: float | None,
) -> tuple[str, float | None]:
    if count < 2 or mean_value is None or median_value is None or iqr_value is None:
        return "not_assessable", None
    scale = max(abs(mean_value), abs(median_value), EPSILON)
    spread_ratio = iqr_value / scale
    if spread_ratio <= 0.10:
        return "compact_relative_to_scale", spread_ratio
    if spread_ratio <= 0.75:
        return "moderate_internal_spread", spread_ratio
    return "broad_internal_spread", spread_ratio


def build_stability_rows(
    grouped: dict[str, list[dict[str, Any]]],
    created_at: str,
) -> tuple[list[dict[str, Any]], dict[str, dict[str, dict[str, float | None]]]]:
    rows: list[dict[str, Any]] = []
    stats_by_context: dict[str, dict[str, dict[str, float | None]]] = {}
    row_index = 1
    for receiver in [CONTEXT_A_RECEIVER, CONTEXT_B_RECEIVER]:
        context_rows = grouped.get(receiver, [])
        if not context_rows:
            continue
        stats_by_context[receiver] = {}
        for dimension, column in DIMENSIONS:
            values = dimension_values(context_rows, column)
            mean_value = safe_mean(values)
            median_value = safe_median(values)
            stddev_value = safe_stddev(values)
            p25 = percentile(values, 0.25)
            p75 = percentile(values, 0.75)
            iqr_value = None if p25 is None or p75 is None else p75 - p25
            p05_value = percentile(values, 0.05)
            p95_value = percentile(values, 0.95)
            coefficient_of_variation = (
                None
                if mean_value is None or abs(mean_value) <= EPSILON or stddev_value is None
                else stddev_value / abs(mean_value)
            )
            stability_status, spread_ratio = classify_stability(
                len(values),
                mean_value,
                median_value,
                iqr_value,
            )
            if stability_status not in STABILITY_STATUSES:
                fail(f"Unexpected stability status: {stability_status}")
            stats = {
                "count": float(len(values)),
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "mean": mean_value,
                "median": median_value,
                "stddev": stddev_value,
                "mad": mad(values, median_value),
                "iqr": iqr_value,
                "p05": p05_value,
                "p95": p95_value,
                "coefficient_of_variation": coefficient_of_variation,
                "spread_ratio": spread_ratio,
            }
            stats_by_context[receiver][dimension] = stats
            rows.append(
                {
                    "stability_id": f"SHAPIROMART05_STAB_{row_index:03d}",
                    "science_object_id": context_rows[0]["science_object_id"],
                    "receiver_context": receiver,
                    "backend_context": context_rows[0]["backend_context"],
                    "fingerprint_dimension": dimension,
                    "complete_record_count": len(values),
                    "numeric_min": stats["min"],
                    "numeric_max": stats["max"],
                    "mean_value": mean_value,
                    "median_value": median_value,
                    "stddev_value": stddev_value,
                    "mad_value": stats["mad"],
                    "iqr_value": iqr_value,
                    "p05_value": p05_value,
                    "p95_value": p95_value,
                    "coefficient_of_variation": coefficient_of_variation,
                    "stability_status": stability_status,
                    "created_at_utc": created_at,
                    "notes": (
                        f"{HEURISTIC_NOTES} spread_ratio={fmt(spread_ratio)}; "
                        "status is descriptive only."
                    ),
                }
            )
            row_index += 1
    return rows, stats_by_context


def build_centroid_rows(
    grouped: dict[str, list[dict[str, Any]]],
    created_at: str,
) -> tuple[list[dict[str, Any]], dict[str, list[float]], dict[str, list[float]]]:
    rows: list[dict[str, Any]] = []
    centroids: dict[str, list[float]] = {}
    distance_by_context: dict[str, list[float]] = {}
    for index, receiver in enumerate([CONTEXT_A_RECEIVER, CONTEXT_B_RECEIVER], start=1):
        context_rows = grouped.get(receiver, [])
        if not context_rows:
            continue
        centroid = [
            safe_mean(dimension_values(context_rows, column)) or 0.0
            for _, column in DIMENSIONS
        ]
        centroids[receiver] = centroid
        distances: list[float] = []
        for row in context_rows:
            distances.append(
                math.sqrt(
                    sum(
                        (float(row[column]) - centroid[position]) ** 2
                        for position, (_, column) in enumerate(DIMENSIONS)
                    )
                )
            )
        distance_by_context[receiver] = distances
        row_payload = {
            "context_centroid_id": f"SHAPIROMART05_CENTROID_{index:03d}",
            "science_object_id": context_rows[0]["science_object_id"],
            "receiver_context": receiver,
            "backend_context": context_rows[0]["backend_context"],
            "complete_record_count": len(context_rows),
            "mean_raw_euclidean_distance_to_centroid": safe_mean(distances),
            "median_raw_euclidean_distance_to_centroid": safe_median(distances),
            "p95_raw_euclidean_distance_to_centroid": percentile(distances, 0.95),
            "created_at_utc": created_at,
            "notes": (
                "Centroid and distances are in raw four-dimensional fingerprint "
                "units; no stored rows were normalized or weighted."
            ),
        }
        for position, (dimension, _) in enumerate(DIMENSIONS):
            row_payload[CENTROID_FIELDS[dimension]] = centroid[position]
        rows.append(row_payload)
    return rows, centroids, distance_by_context


def pooled_stddev(left: float | None, right: float | None) -> float | None:
    if left is None or right is None:
        return None
    value = math.sqrt((left * left + right * right) / 2.0)
    return value if value > EPSILON else None


def interval_overlap(
    left_low: float | None,
    left_high: float | None,
    right_low: float | None,
    right_high: float | None,
) -> int:
    if None in (left_low, left_high, right_low, right_high):
        return 0
    return 1 if max(float(left_low), float(right_low)) <= min(float(left_high), float(right_high)) else 0


def classify_dimension_shift(
    standardized_mean_difference: float | None,
    overlap: int,
) -> str:
    if standardized_mean_difference is None:
        return "not_assessable"
    absolute = abs(standardized_mean_difference)
    if absolute >= 2.0 and overlap == 0:
        return "clear_descriptive_shift"
    if absolute >= 1.0:
        return "moderate_descriptive_shift"
    if absolute >= 0.2:
        return "small_descriptive_shift"
    return "broad_overlap"


def build_dimension_separability_rows(
    stats_by_context: dict[str, dict[str, dict[str, float | None]]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, (dimension, _) in enumerate(DIMENSIONS, start=1):
        stats_a = stats_by_context[CONTEXT_A_RECEIVER][dimension]
        stats_b = stats_by_context[CONTEXT_B_RECEIVER][dimension]
        mean_a = stats_a["mean"]
        mean_b = stats_b["mean"]
        median_a = stats_a["median"]
        median_b = stats_b["median"]
        mean_difference = (
            None if mean_a is None or mean_b is None else float(mean_a) - float(mean_b)
        )
        median_difference = (
            None
            if median_a is None or median_b is None
            else float(median_a) - float(median_b)
        )
        pooled = pooled_stddev(stats_a["stddev"], stats_b["stddev"])
        standardized = (
            None if mean_difference is None or pooled is None else mean_difference / pooled
        )
        overlap = interval_overlap(
            stats_a["p05"],
            stats_a["p95"],
            stats_b["p05"],
            stats_b["p95"],
        )
        status = classify_dimension_shift(standardized, overlap)
        if status not in DIMENSION_STATUSES:
            fail(f"Unexpected dimension status: {status}")
        rows.append(
            {
                "dimension_separability_id": f"SHAPIROMART05_DIMSEP_{index:03d}",
                "science_object_id": EXPECTED_SCIENCE_OBJECT,
                "fingerprint_dimension": dimension,
                "context_a_mean": mean_a,
                "context_b_mean": mean_b,
                "mean_difference_a_minus_b": mean_difference,
                "context_a_median": median_a,
                "context_b_median": median_b,
                "median_difference_a_minus_b": median_difference,
                "context_a_stddev": stats_a["stddev"],
                "context_b_stddev": stats_b["stddev"],
                "pooled_descriptive_stddev": pooled,
                "standardized_mean_difference": standardized,
                "context_a_p05": stats_a["p05"],
                "context_a_p95": stats_a["p95"],
                "context_b_p05": stats_b["p05"],
                "context_b_p95": stats_b["p95"],
                "p05_p95_overlap": overlap,
                "dimension_status": status,
                "created_at_utc": created_at,
                "notes": (
                    "Standardized mean difference is descriptive only and uses "
                    "population stddev pooled by dimension; no inference or "
                    "physical interpretation is attached."
                ),
            }
        )
    return rows


def classify_between_context(
    raw_separation_ratio: float | None,
    standardized_centroid_distance: float | None,
    overlap_count: int,
    nonoverlap_count: int,
) -> str:
    if raw_separation_ratio is None or standardized_centroid_distance is None:
        return "not_assessable"
    if nonoverlap_count == 4 and standardized_centroid_distance >= 2.0:
        return "descriptive_separation_without_p05_p95_overlap"
    if nonoverlap_count > 0 and overlap_count > 0:
        return "descriptive_separation_with_overlap"
    if raw_separation_ratio >= 1.0 or standardized_centroid_distance >= 1.0:
        return "descriptive_centroid_shift_with_interval_overlap"
    return "broad_overlap_descriptive"


def build_between_context_rows(
    centroid_rows: list[dict[str, Any]],
    centroids: dict[str, list[float]],
    distance_by_context: dict[str, list[float]],
    dimension_rows: list[dict[str, Any]],
    stats_by_context: dict[str, dict[str, dict[str, float | None]]],
    created_at: str,
) -> list[dict[str, Any]]:
    by_receiver = {str(row["receiver_context"]): row for row in centroid_rows}
    row_a = by_receiver[CONTEXT_A_RECEIVER]
    row_b = by_receiver[CONTEXT_B_RECEIVER]
    centroid_a = centroids[CONTEXT_A_RECEIVER]
    centroid_b = centroids[CONTEXT_B_RECEIVER]
    raw_centroid_distance = math.sqrt(
        sum((left - right) ** 2 for left, right in zip(centroid_a, centroid_b))
    )
    mean_within_a = safe_mean(distance_by_context[CONTEXT_A_RECEIVER])
    mean_within_b = safe_mean(distance_by_context[CONTEXT_B_RECEIVER])
    pooled_within = (
        None
        if mean_within_a is None or mean_within_b is None
        else (mean_within_a + mean_within_b) / 2.0
    )
    raw_ratio = (
        None
        if pooled_within is None or pooled_within <= EPSILON
        else raw_centroid_distance / pooled_within
    )
    standardized_terms: list[float] = []
    for dimension, _ in DIMENSIONS:
        stats_a = stats_by_context[CONTEXT_A_RECEIVER][dimension]
        stats_b = stats_by_context[CONTEXT_B_RECEIVER][dimension]
        pooled = pooled_stddev(stats_a["stddev"], stats_b["stddev"])
        if pooled is None:
            continue
        difference = float(stats_a["mean"]) - float(stats_b["mean"])
        standardized_terms.append((difference / pooled) ** 2)
    standardized_distance = (
        math.sqrt(sum(standardized_terms)) if standardized_terms else None
    )
    overlap_count = sum(int(row["p05_p95_overlap"]) for row in dimension_rows)
    nonoverlap_count = len(dimension_rows) - overlap_count
    status = classify_between_context(
        raw_ratio,
        standardized_distance,
        overlap_count,
        nonoverlap_count,
    )
    return [
        {
            "separability_id": "SHAPIROMART05_BETWEEN_001",
            "science_object_id": EXPECTED_SCIENCE_OBJECT,
            "context_a_receiver": CONTEXT_A_RECEIVER,
            "context_b_receiver": CONTEXT_B_RECEIVER,
            "shared_backend_context": SUPPORTED_BACKEND
            if row_a["backend_context"] == row_b["backend_context"]
            else None,
            "complete_count_a": int(row_a["complete_record_count"]),
            "complete_count_b": int(row_b["complete_record_count"]),
            "raw_centroid_distance": raw_centroid_distance,
            "mean_within_centroid_distance_a": mean_within_a,
            "mean_within_centroid_distance_b": mean_within_b,
            "pooled_within_distance": pooled_within,
            "raw_separation_ratio": raw_ratio,
            "standardized_centroid_distance": standardized_distance,
            "dimension_overlap_count": overlap_count,
            "dimension_nonoverlap_count": nonoverlap_count,
            "separability_status": status,
            "interpretation_status": INTERPRETATION_STATUS,
            "created_at_utc": created_at,
            "notes": (
                "Different receiver/frequency contexts are expected to differ; "
                "this row records descriptive separation and overlap only."
            ),
        }
    ]


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS mart_shapiro_within_context_stability (
            stability_id TEXT PRIMARY KEY,
            science_object_id TEXT,
            receiver_context TEXT NOT NULL,
            backend_context TEXT NOT NULL,
            fingerprint_dimension TEXT NOT NULL,
            complete_record_count INTEGER NOT NULL,
            numeric_min REAL,
            numeric_max REAL,
            mean_value REAL,
            median_value REAL,
            stddev_value REAL,
            mad_value REAL,
            iqr_value REAL,
            p05_value REAL,
            p95_value REAL,
            coefficient_of_variation REAL,
            stability_status TEXT NOT NULL CHECK (
                stability_status IN (
                    'compact_relative_to_scale',
                    'moderate_internal_spread',
                    'broad_internal_spread',
                    'not_assessable'
                )
            ),
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_context_centroid (
            context_centroid_id TEXT PRIMARY KEY,
            science_object_id TEXT,
            receiver_context TEXT NOT NULL,
            backend_context TEXT NOT NULL,
            complete_record_count INTEGER NOT NULL,
            coordinate_primary_centroid REAL,
            coordinate_secondary_centroid REAL,
            signal_primary_centroid REAL,
            signal_secondary_centroid REAL,
            mean_raw_euclidean_distance_to_centroid REAL,
            median_raw_euclidean_distance_to_centroid REAL,
            p95_raw_euclidean_distance_to_centroid REAL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_dimension_separability (
            dimension_separability_id TEXT PRIMARY KEY,
            science_object_id TEXT,
            fingerprint_dimension TEXT NOT NULL,
            context_a_mean REAL,
            context_b_mean REAL,
            mean_difference_a_minus_b REAL,
            context_a_median REAL,
            context_b_median REAL,
            median_difference_a_minus_b REAL,
            context_a_stddev REAL,
            context_b_stddev REAL,
            pooled_descriptive_stddev REAL,
            standardized_mean_difference REAL,
            context_a_p05 REAL,
            context_a_p95 REAL,
            context_b_p05 REAL,
            context_b_p95 REAL,
            p05_p95_overlap INTEGER NOT NULL CHECK (p05_p95_overlap IN (0, 1)),
            dimension_status TEXT NOT NULL CHECK (
                dimension_status IN (
                    'clear_descriptive_shift',
                    'moderate_descriptive_shift',
                    'small_descriptive_shift',
                    'broad_overlap',
                    'not_assessable'
                )
            ),
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_between_context_separability (
            separability_id TEXT PRIMARY KEY,
            science_object_id TEXT,
            context_a_receiver TEXT NOT NULL,
            context_b_receiver TEXT NOT NULL,
            shared_backend_context TEXT,
            complete_count_a INTEGER NOT NULL,
            complete_count_b INTEGER NOT NULL,
            raw_centroid_distance REAL,
            mean_within_centroid_distance_a REAL,
            mean_within_centroid_distance_b REAL,
            pooled_within_distance REAL,
            raw_separation_ratio REAL,
            standardized_centroid_distance REAL,
            dimension_overlap_count INTEGER,
            dimension_nonoverlap_count INTEGER,
            separability_status TEXT NOT NULL,
            interpretation_status TEXT NOT NULL CHECK (
                interpretation_status = 'descriptive_only_no_physical_interpretation'
            ),
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS shapiromart05_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            complete_fingerprint_count_used INTEGER,
            context_a_complete_count INTEGER,
            context_b_complete_count INTEGER,
            context_count INTEGER,
            dimension_count INTEGER,
            stability_row_count INTEGER,
            dimension_separability_row_count INTEGER,
            between_context_row_count INTEGER,
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
        CREATE VIEW qsb_v_shapiromart05_dashboard AS
        SELECT
            b.science_object_id,
            b.context_a_receiver,
            b.context_b_receiver,
            b.shared_backend_context,
            b.complete_count_a,
            b.complete_count_b,
            b.raw_centroid_distance,
            b.pooled_within_distance,
            b.raw_separation_ratio,
            b.standardized_centroid_distance,
            b.dimension_overlap_count,
            b.dimension_nonoverlap_count,
            b.separability_status,
            b.interpretation_status,
            (SELECT COUNT(*)
             FROM mart_shapiro_within_context_stability) AS stability_row_count,
            (SELECT COUNT(*)
             FROM mart_shapiro_dimension_separability) AS dimension_separability_row_count
        FROM mart_shapiro_between_context_separability AS b
        ORDER BY b.separability_id;

        CREATE VIEW qsb_v_shapiromart05_within_context_stability AS
        SELECT *
        FROM mart_shapiro_within_context_stability
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            CASE fingerprint_dimension
              WHEN 'coordinate_primary' THEN 1
              WHEN 'coordinate_secondary' THEN 2
              WHEN 'signal_value_primary' THEN 3
              WHEN 'signal_value_secondary' THEN 4
              ELSE 99
            END;

        CREATE VIEW qsb_v_shapiromart05_context_centroids AS
        SELECT *
        FROM mart_shapiro_context_centroid
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            receiver_context;

        CREATE VIEW qsb_v_shapiromart05_dimension_separability AS
        SELECT *
        FROM mart_shapiro_dimension_separability
        ORDER BY
            CASE fingerprint_dimension
              WHEN 'coordinate_primary' THEN 1
              WHEN 'coordinate_secondary' THEN 2
              WHEN 'signal_value_primary' THEN 3
              WHEN 'signal_value_secondary' THEN 4
              ELSE 99
            END;

        CREATE VIEW qsb_v_shapiromart05_between_context_separability AS
        SELECT *
        FROM mart_shapiro_between_context_separability
        ORDER BY separability_id;
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


def write_readout(
    path: Path,
    run_id: str,
    created_at: str,
    stability_rows: list[dict[str, Any]],
    centroid_rows: list[dict[str, Any]],
    dimension_rows: list[dict[str, Any]],
    between_rows: list[dict[str, Any]],
    validation: dict[str, Any],
) -> None:
    between = between_rows[0]
    most_stable = sorted(
        stability_rows,
        key=lambda row: (
            float("inf") if row["iqr_value"] is None else abs(float(row["iqr_value"])),
            str(row["receiver_context"]),
            str(row["fingerprint_dimension"]),
        ),
    )[:4]
    largest_shifts = sorted(
        dimension_rows,
        key=lambda row: (
            -abs(float(row["standardized_mean_difference"]))
            if row["standardized_mean_difference"] is not None
            else 0.0,
            str(row["fingerprint_dimension"]),
        ),
    )
    overlap_rows = [
        {
            "fingerprint_dimension": row["fingerprint_dimension"],
            "p05_p95_overlap": row["p05_p95_overlap"],
            "dimension_status": row["dimension_status"],
        }
        for row in dimension_rows
    ]
    lines: list[str] = [
        "# QSB-SHAPIROMART05 - Stability and Separability",
        "",
        f"Run ID: {run_id}",
        f"Run timestamp UTC: {created_at}",
        "",
        "## Scope",
        "",
        CLAIM_BOUNDARY,
        "",
        HEURISTIC_NOTES,
        "",
        "Different receiver/frequency contexts are expected to differ. "
        "Descriptive separation is not an anomaly by itself and is not a "
        "Beam/geometry influence test.",
        "",
        "## 1. Internal compactness or dispersion",
        "",
    ]
    lines.extend(
        markdown_table(
            stability_rows,
            [
                "receiver_context",
                "fingerprint_dimension",
                "complete_record_count",
                "mad_value",
                "iqr_value",
                "coefficient_of_variation",
                "stability_status",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 2. Most stable dimensions",
            "",
            "Smallest raw IQR rows are listed here. This is a descriptive ranking "
            "inside raw units, not a cross-dimension normalized claim.",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            most_stable,
            ["receiver_context", "fingerprint_dimension", "iqr_value", "mad_value"],
        )
    )
    lines.extend(
        [
            "",
            "## 3. Largest between-context shifts",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            largest_shifts,
            [
                "fingerprint_dimension",
                "mean_difference_a_minus_b",
                "standardized_mean_difference",
                "dimension_status",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 4. Centroid separation relative to internal spread",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            between_rows,
            [
                "raw_centroid_distance",
                "mean_within_centroid_distance_a",
                "mean_within_centroid_distance_b",
                "pooled_within_distance",
                "raw_separation_ratio",
                "standardized_centroid_distance",
                "separability_status",
            ],
        )
    )
    lines.extend(
        [
            "",
            "Context centroids and raw centroid-distance summaries:",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            centroid_rows,
            [
                "receiver_context",
                "complete_record_count",
                "coordinate_primary_centroid",
                "coordinate_secondary_centroid",
                "signal_primary_centroid",
                "signal_secondary_centroid",
                "mean_raw_euclidean_distance_to_centroid",
                "p95_raw_euclidean_distance_to_centroid",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 5. p05-p95 interval overlap",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            overlap_rows,
            ["fingerprint_dimension", "p05_p95_overlap", "dimension_status"],
        )
    )
    lines.extend(
        [
            "",
            "## 6. Separation, overlap, or both",
            "",
            f"Dimension overlap count: {between['dimension_overlap_count']}.",
            f"Dimension non-overlap count: {between['dimension_nonoverlap_count']}.",
            f"Overall descriptive status: {between['separability_status']}.",
            "",
            "## 7. Why this still does not test Beam/geometry influence",
            "",
            "The comparison is between two receiver/backend contexts and does not "
            "attach an exposure axis while holding receiver/backend fixed. Because "
            "receiver/frequency contexts can differ for ordinary instrumental and "
            "selection reasons, this output remains a structural descriptive "
            "readout only.",
            "",
            "## 8. Single next concrete step",
            "",
            NEXT_STEP,
            "",
            "## Validation",
            "",
            "```json",
            json.dumps(validation, indent=2, sort_keys=True),
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(
    output_root: Path,
    run_id: str,
    created_at: str,
    stability_rows: list[dict[str, Any]],
    centroid_rows: list[dict[str, Any]],
    dimension_rows: list[dict[str, Any]],
    between_rows: list[dict[str, Any]],
    validation: dict[str, Any],
) -> dict[str, str]:
    paths = output_paths(output_root)
    write_csv(
        paths[WITHIN_CONTEXT_CSV],
        stability_rows,
        [
            "stability_id",
            "science_object_id",
            "receiver_context",
            "backend_context",
            "fingerprint_dimension",
            "complete_record_count",
            "numeric_min",
            "numeric_max",
            "mean_value",
            "median_value",
            "stddev_value",
            "mad_value",
            "iqr_value",
            "p05_value",
            "p95_value",
            "coefficient_of_variation",
            "stability_status",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[CENTROIDS_CSV],
        centroid_rows,
        [
            "context_centroid_id",
            "science_object_id",
            "receiver_context",
            "backend_context",
            "complete_record_count",
            "coordinate_primary_centroid",
            "coordinate_secondary_centroid",
            "signal_primary_centroid",
            "signal_secondary_centroid",
            "mean_raw_euclidean_distance_to_centroid",
            "median_raw_euclidean_distance_to_centroid",
            "p95_raw_euclidean_distance_to_centroid",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[DIMENSION_SEPARABILITY_CSV],
        dimension_rows,
        [
            "dimension_separability_id",
            "science_object_id",
            "fingerprint_dimension",
            "context_a_mean",
            "context_b_mean",
            "mean_difference_a_minus_b",
            "context_a_median",
            "context_b_median",
            "median_difference_a_minus_b",
            "context_a_stddev",
            "context_b_stddev",
            "pooled_descriptive_stddev",
            "standardized_mean_difference",
            "context_a_p05",
            "context_a_p95",
            "context_b_p05",
            "context_b_p95",
            "p05_p95_overlap",
            "dimension_status",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[BETWEEN_CONTEXT_CSV],
        between_rows,
        [
            "separability_id",
            "science_object_id",
            "context_a_receiver",
            "context_b_receiver",
            "shared_backend_context",
            "complete_count_a",
            "complete_count_b",
            "raw_centroid_distance",
            "mean_within_centroid_distance_a",
            "mean_within_centroid_distance_b",
            "pooled_within_distance",
            "raw_separation_ratio",
            "standardized_centroid_distance",
            "dimension_overlap_count",
            "dimension_nonoverlap_count",
            "separability_status",
            "interpretation_status",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[NEXT_STEP_CSV],
        [
            {
                "next_step_id": "SHAPIROMART05_NEXT_001",
                "recommended_next_step": NEXT_STEP,
                "scope_limit": "not_implemented_in_shapiromart05",
                "db_write_expected": "yes_in_separate_explicit_task",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        ],
        [
            "next_step_id",
            "recommended_next_step",
            "scope_limit",
            "db_write_expected",
            "claim_boundary",
        ],
    )
    summary_payload = {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script": SCRIPT_NAME,
        "complete_fingerprint_count_used": EXPECTED_COMPLETE_TOTAL,
        "context_counts": EXPECTED_CONTEXT_COUNTS,
        "within_context_stability": stability_rows,
        "context_centroids": centroid_rows,
        "dimension_separability": dimension_rows,
        "between_context_separability": between_rows,
        "validation": validation,
        "heuristic_notes": HEURISTIC_NOTES,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_step": NEXT_STEP,
        "warnings": [
            "No weighting, imputation, clustering, or stored-row normalization was applied.",
            "No inferential statistics or physical interpretation were computed.",
            "Different receiver/frequency contexts are expected to differ.",
        ],
        "output_files": {name: str(path) for name, path in paths.items()},
        "stop_reason": "completed_descriptive_stability_separability_build",
    }
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary_payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_readout(
        paths[READOUT_MD],
        run_id,
        created_at,
        stability_rows,
        centroid_rows,
        dimension_rows,
        between_rows,
        validation,
    )
    return {name: str(path) for name, path in paths.items()}


def build_run_log_row(
    run_id: str,
    created_at: str,
    live_db_modified: bool,
    workcopy_db_modified: bool,
    integrity_result: str,
    fk_violation_count: int,
) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "complete_fingerprint_count_used": EXPECTED_COMPLETE_TOTAL,
        "context_a_complete_count": EXPECTED_CONTEXT_COUNTS[CONTEXT_A_RECEIVER],
        "context_b_complete_count": EXPECTED_CONTEXT_COUNTS[CONTEXT_B_RECEIVER],
        "context_count": 2,
        "dimension_count": 4,
        "stability_row_count": 8,
        "dimension_separability_row_count": 4,
        "between_context_row_count": 1,
        "live_db_modified": 1 if live_db_modified else 0,
        "workcopy_db_modified": 1 if workcopy_db_modified else 0,
        "integrity_check_result": integrity_result,
        "foreign_key_violation_count": fk_violation_count,
        "notes": (
            "Descriptive within-context stability and between-context "
            "separability only; no receiver/backend-fixed exposure axis attached."
        ),
    }


def validate_results(
    complete_rows: list[dict[str, Any]],
    stability_rows: list[dict[str, Any]],
    centroid_rows: list[dict[str, Any]],
    dimension_rows: list[dict[str, Any]],
    between_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    context_counts: dict[str, int] = defaultdict(int)
    for row in complete_rows:
        context_counts[str(row["receiver_context"])] += 1
    return {
        "complete_fingerprints_used": len(complete_rows),
        "context_counts": dict(context_counts),
        "context_count": len(context_counts),
        "dimension_count": len(DIMENSIONS),
        "stability_row_count": len(stability_rows),
        "context_centroid_row_count": len(centroid_rows),
        "dimension_separability_row_count": len(dimension_rows),
        "between_context_row_count": len(between_rows),
        "expected_complete_count_pass": len(complete_rows) == EXPECTED_COMPLETE_TOTAL,
        "expected_context_counts_pass": dict(context_counts) == EXPECTED_CONTEXT_COUNTS,
        "expected_context_count_pass": len(context_counts) == 2,
        "expected_dimension_count_pass": len(DIMENSIONS) == 4,
        "expected_stability_rows_pass": len(stability_rows) == 8,
        "expected_dimension_rows_pass": len(dimension_rows) == 4,
        "expected_between_rows_pass": len(between_rows) == 1,
        "compound_labels_promoted": False,
        "weighting_applied": False,
        "imputation_applied": False,
        "inferential_statistics_applied": False,
        "physical_interpretation_applied": False,
        "stored_rows_normalized": False,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)
    created_at = utc_now()
    run_id = "SHAPIROMART05_RUN_" + created_at.replace("-", "").replace(":", "")

    with connect_readonly(args.live_db) as live_con:
        live_con.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()

    con = connect_writable(args.workcopy_db)
    try:
        validate_required_objects(con)
        target_state = validate_existing_target_state(con, args.allow_existing)
        prior_before = prior_counts(con)
        complete_rows = load_complete_fingerprints(con)
        grouped = group_by_context(complete_rows)
        stability_rows, stats_by_context = build_stability_rows(grouped, created_at)
        centroid_rows, centroids, distance_by_context = build_centroid_rows(
            grouped,
            created_at,
        )
        dimension_rows = build_dimension_separability_rows(
            stats_by_context,
            created_at,
        )
        between_rows = build_between_context_rows(
            centroid_rows,
            centroids,
            distance_by_context,
            dimension_rows,
            stats_by_context,
            created_at,
        )
        result_validation = validate_results(
            complete_rows,
            stability_rows,
            centroid_rows,
            dimension_rows,
            between_rows,
        )

        create_tables(con)
        if args.allow_existing:
            clear_target_tables(con)
        insert_rows(con, "mart_shapiro_within_context_stability", stability_rows)
        insert_rows(con, "mart_shapiro_context_centroid", centroid_rows)
        insert_rows(con, "mart_shapiro_dimension_separability", dimension_rows)
        insert_rows(con, "mart_shapiro_between_context_separability", between_rows)
        create_views(con)
        con.commit()

        integrity_result = integrity_check(con)
        fk_violations = foreign_key_violations(con)
        prior_after_data = prior_counts(con)
        queryable_after_data = queryable_counts(con)
        live_after_data = db_state(args.live_db)
        workcopy_after_data = db_state(args.workcopy_db)
        run_log_row = build_run_log_row(
            run_id,
            created_at,
            live_before != live_after_data,
            workcopy_before != workcopy_after_data,
            integrity_result,
            len(fk_violations),
        )
        insert_rows(con, "shapiromart05_run_log", [run_log_row])
        con.commit()

        final_integrity = integrity_check(con)
        final_fk_violations = foreign_key_violations(con)
        prior_after = prior_counts(con)
        final_live_state = db_state(args.live_db)
        final_workcopy_state = db_state(args.workcopy_db)
        final_live_modified = live_before != final_live_state
        final_workcopy_modified = workcopy_before != final_workcopy_state
        con.execute(
            """
            UPDATE shapiromart05_run_log
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
            **result_validation,
            "live_db_checksum_stat_unchanged": not final_live_modified,
            "workcopy_db_modified": final_workcopy_modified,
            "workcopy_integrity_check": final_integrity,
            "workcopy_foreign_key_violation_count": len(final_fk_violations),
            "prior_shapiromart01_04_counts_preserved": prior_before == prior_after,
            "all_new_tables_views_queryable": all(
                isinstance(value, int) for value in queryable_final.values()
            ),
            "queryable_counts": queryable_final,
            "queryable_counts_after_data_before_run_log": queryable_after_data,
            "pre_run_target_state": target_state,
            "prior_counts_before": prior_before,
            "prior_counts_after_data": prior_after_data,
            "prior_counts_after": prior_after,
            "live_db_before": live_before,
            "live_db_after": final_live_state,
            "workcopy_db_before": workcopy_before,
            "workcopy_db_after": final_workcopy_state,
            "interpretation_status": INTERPRETATION_STATUS,
        }

        required_passes = [
            validation["expected_complete_count_pass"],
            validation["expected_context_counts_pass"],
            validation["expected_context_count_pass"],
            validation["expected_dimension_count_pass"],
            validation["expected_stability_rows_pass"],
            validation["expected_dimension_rows_pass"],
            validation["expected_between_rows_pass"],
            validation["live_db_checksum_stat_unchanged"],
            validation["workcopy_integrity_check"] == "ok",
            validation["workcopy_foreign_key_violation_count"] == 0,
            validation["prior_shapiromart01_04_counts_preserved"],
            validation["all_new_tables_views_queryable"],
        ]
        if not all(required_passes):
            fail("SHAPIROMART05 validation failed; see validation payload.")

        output_files = write_outputs(
            args.output_root,
            run_id,
            created_at,
            stability_rows,
            centroid_rows,
            dimension_rows,
            between_rows,
            validation,
        )
        return {
            "run_id": run_id,
            "run_timestamp_utc": created_at,
            "complete_fingerprint_count_used": len(complete_rows),
            "context_counts": EXPECTED_CONTEXT_COUNTS,
            "stability_rows": stability_rows,
            "centroid_rows": centroid_rows,
            "dimension_separability_rows": dimension_rows,
            "between_context_rows": between_rows,
            "output_files": output_files,
            "validation": validation,
        }
    finally:
        con.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build SHAPIROMART05 descriptive within-context stability and "
            "between-context separability tables in the existing workcopy DB."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing SHAPIROMART05 output files.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow replacing existing SHAPIROMART05 DB target rows/views.",
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
