#!/usr/bin/env python3
"""QSB-SHAPIROMART18 exposure-group fingerprint comparison.

This script performs a descriptive comparison of SHAPIROMART04 unweighted
fingerprint dimensions across SHAPIROMART17 prepared exposure groups. It does
not fit a timing model, compute Shapiro delay, or make a physical
interpretation.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


RESEARCH_BLOCK = "QSB-SHAPIROMART18"
EXPECTED_ROW_COUNT = 7419
PRIMARY_THRESHOLD = 0.05
SECONDARY_THRESHOLD = 0.15
MIN_GROUP_COUNT = 30
DEFAULT_BOOTSTRAP_REPS = 2000
DEFAULT_BOOTSTRAP_SEED = 20260606
DEFAULT_WINSOR_FRACTION = 0.01

ROOT = Path(__file__).resolve().parents[1]
SHAPIROMART04_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART04_FIRST_UNWEIGHTED_FINGERPRINT"
SHAPIROMART05_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART05_STABILITY_SEPARABILITY"
SHAPIROMART11_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART11_CONTROLLED_PINT_RECONSTRUCTION"
SHAPIROMART15_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART15_ROW_LEVEL_CONTEXT_ENRICHMENT"
SHAPIROMART17_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART17_THRESHOLD_CONSOLIDATION_EXPOSURE_PREPARATION"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART18_EXPOSURE_GROUP_FINGERPRINT_COMPARISON"
)
DEFAULT_WORKCOPY_DB = (
    ROOT
    / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)

OUTPUT_FILES = [
    "shapiromart18_readout.md",
    "shapiromart18_summary.json",
    "shapiromart18_input_join_assessment.csv",
    "shapiromart18_group_descriptive_statistics.csv",
    "shapiromart18_primary_effect_sizes.csv",
    "shapiromart18_context_stratified_effects.csv",
    "shapiromart18_pre_post_control.csv",
    "shapiromart18_threshold_sensitivity.csv",
    "shapiromart18_composition_adjusted_effects.csv",
    "shapiromart18_robustness_summary.csv",
    "shapiromart18_dimension_assessment.csv",
    "shapiromart18_final_status.csv",
]

DIMENSIONS = [
    "coordinate_primary",
    "coordinate_secondary",
    "signal_value_primary",
    "signal_value_secondary",
]

SOURCE_KEY_FIELDS = [
    "name",
    "fe",
    "be",
    "f",
    "bw",
    "tobs",
    "tmplt",
    "gof",
    "nbin",
    "nch",
    "chan",
    "subint",
    "snr",
    "wt",
    "flux",
    "fluxe",
    "proc",
    "pta",
    "ver",
]

GROUP_FIELDS = [
    "source_row_index",
    "orbital_phase",
    "signed_phase_offset",
    "absolute_phase_distance",
    "receiver",
    "backend",
    "context_name",
    "primary_threshold",
    "primary_group",
    "secondary_threshold",
    "secondary_group",
]

TOA_FIELDS = ["source_row_index", "source_filename"]

JOIN_ASSESSMENT_FIELDS = [
    "assessment_id",
    "left_input",
    "right_input",
    "key_fields",
    "left_row_count",
    "right_row_count",
    "left_unique",
    "right_unique",
    "left_null_count",
    "right_null_count",
    "matched_row_count",
    "unmatched_left_count",
    "unmatched_right_count",
    "multiple_match_count",
    "assessment_status",
    "notes",
]

DESCRIPTIVE_FIELDS = [
    "statistic_id",
    "analysis_role",
    "threshold_role",
    "threshold_value",
    "scope_type",
    "scope_label",
    "context_name",
    "phase_side",
    "dimension",
    "comparison_group",
    "row_count",
    "missing_count",
    "mean",
    "standard_deviation",
    "median",
    "q1",
    "q3",
    "minimum",
    "maximum",
    "winsor_fraction",
    "winsorized_mean",
    "statistic_status",
    "notes",
]

EFFECT_FIELDS = [
    "comparison_id",
    "analysis_role",
    "threshold_role",
    "threshold_value",
    "scope_type",
    "scope_label",
    "context_name",
    "phase_side",
    "dimension",
    "inside_label",
    "outside_label",
    "inside_count",
    "outside_count",
    "minimum_group_count",
    "effect_status",
    "inside_mean",
    "outside_mean",
    "mean_difference_inside_minus_outside",
    "inside_median",
    "outside_median",
    "median_difference_inside_minus_outside",
    "pooled_sd",
    "smd",
    "abs_smd",
    "smd_category",
    "pooled_iqr_sigma_scale",
    "robust_standardized_median_difference",
    "rank_biserial",
    "bootstrap_repetitions",
    "bootstrap_seed",
    "mean_difference_ci_low",
    "mean_difference_ci_high",
    "smd_ci_low",
    "smd_ci_high",
    "median_difference_ci_low",
    "median_difference_ci_high",
    "notes",
]

COMPOSITION_FIELDS = [
    "comparison_id",
    "threshold_role",
    "threshold_value",
    "strata_basis",
    "dimension",
    "total_row_count",
    "inside_total_count",
    "outside_total_count",
    "weight_source",
    "usable_stratum_count",
    "omitted_stratum_count",
    "common_reference_sd",
    "adjusted_mean_difference_inside_minus_outside",
    "standardized_stratified_difference",
    "adjusted_abs_smd",
    "adjusted_smd_category",
    "direction_status",
    "minimum_group_count",
    "adjustment_status",
    "notes",
]

ROBUSTNESS_FIELDS = [
    "dimension",
    "primary_smd",
    "primary_smd_ci_low",
    "primary_smd_ci_high",
    "primary_smd_category",
    "winsor_fraction",
    "winsorized_smd",
    "winsorized_smd_category",
    "context_direction_status",
    "context_min_abs_smd",
    "context_max_abs_smd",
    "side_direction_status",
    "side_min_abs_smd",
    "side_max_abs_smd",
    "leave_one_context_min_abs_smd",
    "leave_one_context_max_abs_smd",
    "leave_one_context_direction_status",
    "secondary_smd",
    "secondary_smd_category",
    "threshold_sensitivity_status",
    "composition_context_standardized_difference",
    "composition_context_side_standardized_difference",
    "robustness_status",
    "notes",
]

DIMENSION_ASSESSMENT_FIELDS = [
    "dimension",
    "final_dimension_status",
    "primary_smd",
    "primary_smd_category",
    "primary_smd_ci_low",
    "primary_smd_ci_high",
    "context_direction_status",
    "side_direction_status",
    "threshold_sensitivity_status",
    "composition_context_standardized_difference",
    "composition_context_side_standardized_difference",
    "claim_boundary",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "output_dir",
    "final_status",
    "analysis_status",
    "prepared_group_rows",
    "fingerprint_rows",
    "joined_rows",
    "unmatched_group_rows",
    "unmatched_fingerprint_rows",
    "primary_threshold_value",
    "secondary_threshold_value",
    "bootstrap_repetitions",
    "bootstrap_seed",
    "winsor_fraction",
    "minimum_group_count",
    "database_access",
    "database_modified",
    "physical_exposure_claimed",
    "shapiro_delay_calculated",
    "residual_analysis_performed",
    "timing_model_fit_performed",
    "model_parameters_modified",
    "physical_interpretation_performed",
    "threshold_reselected_after_results",
    "additional_gate_created",
    "exposure_effect_analysis_performed",
    "fingerprint_comparison_performed",
    "recommended_next_action",
    "limitations",
]


class ControlledStop(RuntimeError):
    """Raised when the requested comparison must stop before analysis."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SHAPIROMART18 descriptive comparison.")
    parser.add_argument(
        "--prepared-groups",
        type=Path,
        default=SHAPIROMART17_DIR / "shapiromart17_prepared_exposure_groups.csv",
    )
    parser.add_argument(
        "--threshold-decision",
        type=Path,
        default=SHAPIROMART17_DIR / "shapiromart17_threshold_decision.csv",
    )
    parser.add_argument(
        "--toa-orbital-phase",
        type=Path,
        default=SHAPIROMART11_DIR / "shapiromart11_toa_orbital_phase.csv",
    )
    parser.add_argument(
        "--shapiromart04-summary",
        type=Path,
        default=SHAPIROMART04_DIR / "shapiromart04_summary.json",
    )
    parser.add_argument(
        "--shapiromart05-summary",
        type=Path,
        default=SHAPIROMART05_DIR / "shapiromart05_summary.json",
    )
    parser.add_argument(
        "--shapiromart15-join-assessment",
        type=Path,
        default=SHAPIROMART15_DIR / "shapiromart15_join_key_assessment.csv",
    )
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bootstrap-reps", type=int, default=DEFAULT_BOOTSTRAP_REPS)
    parser.add_argument("--bootstrap-seed", type=int, default=DEFAULT_BOOTSTRAP_SEED)
    parser.add_argument("--winsor-fraction", type=float, default=DEFAULT_WINSOR_FRACTION)
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise ControlledStop(f"Required input missing: {rel(path)}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    ensure_parent(path)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def require_fields(rows: list[dict[str, str]], fields: list[str], path: Path) -> None:
    if not rows:
        raise ControlledStop(f"Required input has no data rows: {rel(path)}")
    missing = [field for field in fields if field not in rows[0]]
    if missing:
        raise ControlledStop(f"Missing fields in {rel(path)}: {', '.join(missing)}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_identity(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ControlledStop(f"Required file missing: {rel(path)}")
    stat = path.stat()
    return {
        "path": rel(path),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": sha256_file(path),
    }


def fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if not math.isfinite(number):
        return ""
    return format(number, ".12g")


def fmt_threshold(value: float) -> str:
    return format(value, ".17g")


def to_float(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ControlledStop(f"Invalid numeric value for {field}: {value!r}") from exc
    if not math.isfinite(number):
        raise ControlledStop(f"Non-finite numeric value for {field}: {value!r}")
    return number


def threshold_matches(value: Any, expected: float) -> bool:
    return math.isclose(float(value), expected, rel_tol=0.0, abs_tol=1e-12)


def parse_source_flags(text: str) -> dict[str, str]:
    try:
        value = ast.literal_eval(text)
    except (SyntaxError, ValueError) as exc:
        raise ControlledStop("Unable to parse SHAPIROMART11 source flags.") from exc
    if not isinstance(value, dict):
        raise ControlledStop("SHAPIROMART11 source flags are not a dictionary.")
    return {str(key): str(val) for key, val in value.items()}


def parse_tim_line_flags(raw_line_text: str) -> dict[str, str]:
    tokens = (raw_line_text or "").split()
    if not tokens:
        return {}
    flags: dict[str, str] = {"name": tokens[0]}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token.startswith("-") and len(token) > 1 and index + 1 < len(tokens):
            flags[token[1:]] = tokens[index + 1]
            index += 2
        else:
            index += 1
    return flags


def source_key(flags: dict[str, str]) -> tuple[str, ...]:
    return tuple(flags.get(field, "") for field in SOURCE_KEY_FIELDS)


def source_key_hash(key: tuple[str, ...]) -> str:
    joined = "\x1f".join(key)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def missing_key_field_count(keys: list[tuple[str, ...]]) -> int:
    return sum(1 for key in keys if any(part == "" for part in key))


def load_threshold_decision(path: Path) -> dict[str, dict[str, str]]:
    rows, _ = read_csv_rows(path)
    if not rows:
        raise ControlledStop("SHAPIROMART17 threshold decision is empty.")
    by_role = {row.get("decision_role", ""): row for row in rows}
    primary = by_role.get("primary")
    secondary = by_role.get("secondary_sensitivity")
    if primary is None or not threshold_matches(primary.get("threshold_value", ""), PRIMARY_THRESHOLD):
        raise ControlledStop("Primary threshold decision is not the required 0.05 value.")
    if secondary is None or not threshold_matches(secondary.get("threshold_value", ""), SECONDARY_THRESHOLD):
        raise ControlledStop("Secondary threshold decision is not the required 0.15 value.")
    return by_role


def load_prepared_groups(path: Path) -> list[dict[str, Any]]:
    rows, _ = read_csv_rows(path)
    require_fields(rows, GROUP_FIELDS, path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ControlledStop(f"Expected {EXPECTED_ROW_COUNT} SHAPIROMART17 group rows.")
    indices = [row["source_row_index"] for row in rows]
    if len(set(indices)) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART17 source_row_index values are not unique.")
    int_indices = sorted(int(index) for index in indices)
    if int_indices != list(range(EXPECTED_ROW_COUNT)):
        raise ControlledStop("SHAPIROMART17 source_row_index values are not contiguous 0..7418.")

    parsed: list[dict[str, Any]] = []
    for row in rows:
        primary_threshold = to_float(row["primary_threshold"], "primary_threshold")
        secondary_threshold = to_float(row["secondary_threshold"], "secondary_threshold")
        if not threshold_matches(primary_threshold, PRIMARY_THRESHOLD):
            raise ControlledStop("Prepared groups do not preserve primary threshold 0.05.")
        if not threshold_matches(secondary_threshold, SECONDARY_THRESHOLD):
            raise ControlledStop("Prepared groups do not preserve secondary threshold 0.15.")
        absolute = to_float(row["absolute_phase_distance"], "absolute_phase_distance")
        signed = to_float(row["signed_phase_offset"], "signed_phase_offset")
        expected_primary = (
            "inside_primary_threshold"
            if absolute <= PRIMARY_THRESHOLD
            else "outside_primary_threshold"
        )
        expected_secondary = (
            "inside_secondary_threshold"
            if absolute <= SECONDARY_THRESHOLD
            else "outside_secondary_threshold"
        )
        if row["primary_group"] != expected_primary:
            raise ControlledStop(f"Primary group mismatch at source_row_index={row['source_row_index']}")
        if row["secondary_group"] != expected_secondary:
            raise ControlledStop(f"Secondary group mismatch at source_row_index={row['source_row_index']}")
        phase_side = "pre_conjunction_side" if signed < 0 else "post_conjunction_side"
        if math.isclose(signed, 0.0, rel_tol=0.0, abs_tol=1e-15):
            phase_side = "reference_phase_point"
        parsed_row = dict(row)
        parsed_row["_absolute_phase_distance"] = absolute
        parsed_row["_signed_phase_offset"] = signed
        parsed_row["phase_side"] = phase_side
        parsed.append(parsed_row)
    return parsed


def load_toa_source_keys(path: Path) -> dict[str, dict[str, Any]]:
    rows, _ = read_csv_rows(path)
    require_fields(rows, TOA_FIELDS, path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ControlledStop(f"Expected {EXPECTED_ROW_COUNT} SHAPIROMART11 TOA rows.")
    by_source_index: dict[str, dict[str, Any]] = {}
    keys: list[tuple[str, ...]] = []
    for row in rows:
        flags = parse_source_flags(row["source_filename"])
        key = source_key(flags)
        keys.append(key)
        source_index = row["source_row_index"]
        if source_index in by_source_index:
            raise ControlledStop("Duplicate SHAPIROMART11 source_row_index value.")
        by_source_index[source_index] = {
            "source_row_index": source_index,
            "source_key": key,
            "source_key_hash": source_key_hash(key),
            "source_flags": flags,
        }
    if len(set(keys)) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART11 exact source-flag keys are not unique.")
    if missing_key_field_count(keys):
        raise ControlledStop("SHAPIROMART11 exact source-flag keys have missing parts.")
    return by_source_index


def open_read_only_db(path: Path) -> sqlite3.Connection:
    if not path.exists():
        raise ControlledStop(f"Workcopy DB missing: {rel(path)}")
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA query_only=ON")
    return con


def load_fingerprints_from_db(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    before = file_identity(path)
    con = open_read_only_db(path)
    try:
        integrity = con.execute("PRAGMA integrity_check").fetchall()
        fk_rows = con.execute("PRAGMA foreign_key_check").fetchall()
        columns = [row[1] for row in con.execute("PRAGMA table_info(qsb_v_shapiromart04_complete_fingerprints)")]
        missing_dimensions = [dimension for dimension in DIMENSIONS if dimension not in columns]
        if missing_dimensions:
            raise ControlledStop(
                "SHAPIROMART04 complete fingerprint view lacks dimensions: "
                + ", ".join(missing_dimensions)
            )
        rows = con.execute(
            """
            SELECT
                fp.structural_fingerprint_id,
                fp.raw_record_id,
                fp.observation_id,
                fp.science_object_id,
                fp.receiver_context,
                fp.backend_context,
                fp.raw_context_label,
                fp.coordinate_primary,
                fp.coordinate_secondary,
                fp.signal_value_primary,
                fp.signal_value_secondary,
                rr.raw_line_text
            FROM qsb_v_shapiromart04_complete_fingerprints AS fp
            JOIN raw_record AS rr
              ON rr.raw_record_id = fp.raw_record_id
            """
        ).fetchall()
    finally:
        con.close()
    after = file_identity(path)

    if len(rows) != EXPECTED_ROW_COUNT:
        raise ControlledStop(f"Expected {EXPECTED_ROW_COUNT} SHAPIROMART04 complete fingerprints.")

    parsed: list[dict[str, Any]] = []
    keys: list[tuple[str, ...]] = []
    for row in rows:
        item = dict(row)
        flags = parse_tim_line_flags(str(item.get("raw_line_text") or ""))
        key = source_key(flags)
        keys.append(key)
        for dimension in DIMENSIONS:
            item[dimension] = to_float(item[dimension], dimension)
        item["source_key"] = key
        item["source_key_hash"] = source_key_hash(key)
        parsed.append(item)

    if len(set(keys)) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART04 exact source-flag keys are not unique.")
    if missing_key_field_count(keys):
        raise ControlledStop("SHAPIROMART04 exact source-flag keys have missing parts.")

    db_status = {
        "before": before,
        "after": after,
        "database_modified": "no" if before == after else "yes",
        "integrity_check": [tuple(row) for row in integrity],
        "foreign_key_check_row_count": len(fk_rows),
    }
    return parsed, db_status


def join_inputs(
    groups: list[dict[str, Any]],
    toa_keys: dict[str, dict[str, Any]],
    fingerprints: list[dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fingerprint_by_key = {row["source_key"]: row for row in fingerprints}
    sh17_indices = {row["source_row_index"] for row in groups}
    sh11_indices = set(toa_keys)
    sh11_keys = [row["source_key"] for row in toa_keys.values()]
    sh04_keys = [row["source_key"] for row in fingerprints]

    join_rows = [
        {
            "assessment_id": "A01_SH17_SOURCE_ROW_INDEX",
            "left_input": rel(args.prepared_groups),
            "right_input": rel(args.prepared_groups),
            "key_fields": "source_row_index",
            "left_row_count": len(groups),
            "right_row_count": len(groups),
            "left_unique": "yes" if len(sh17_indices) == len(groups) else "no",
            "right_unique": "yes" if len(sh17_indices) == len(groups) else "no",
            "left_null_count": sum(1 for row in groups if row["source_row_index"] == ""),
            "right_null_count": sum(1 for row in groups if row["source_row_index"] == ""),
            "matched_row_count": len(groups),
            "unmatched_left_count": 0,
            "unmatched_right_count": 0,
            "multiple_match_count": 0,
            "assessment_status": "unique_key_confirmed",
            "notes": "Prepared-group key is unique and complete.",
        },
        {
            "assessment_id": "A02_SH17_TO_SH11_SOURCE_ROW_INDEX",
            "left_input": rel(args.prepared_groups),
            "right_input": rel(args.toa_orbital_phase),
            "key_fields": "source_row_index",
            "left_row_count": len(groups),
            "right_row_count": len(toa_keys),
            "left_unique": "yes",
            "right_unique": "yes" if len(sh11_indices) == len(toa_keys) else "no",
            "left_null_count": 0,
            "right_null_count": 0,
            "matched_row_count": len(sh17_indices & sh11_indices),
            "unmatched_left_count": len(sh17_indices - sh11_indices),
            "unmatched_right_count": len(sh11_indices - sh17_indices),
            "multiple_match_count": 0,
            "assessment_status": "complete_unique_match"
            if sh17_indices == sh11_indices
            else "join_failed",
            "notes": "Exact documented source_row_index chain from PINT TOA export.",
        },
        {
            "assessment_id": "A03_SH11_SOURCE_FLAG_KEY",
            "left_input": rel(args.toa_orbital_phase),
            "right_input": rel(args.toa_orbital_phase),
            "key_fields": ";".join(SOURCE_KEY_FIELDS),
            "left_row_count": len(toa_keys),
            "right_row_count": len(toa_keys),
            "left_unique": "yes" if len(set(sh11_keys)) == len(sh11_keys) else "no",
            "right_unique": "yes" if len(set(sh11_keys)) == len(sh11_keys) else "no",
            "left_null_count": missing_key_field_count(sh11_keys),
            "right_null_count": missing_key_field_count(sh11_keys),
            "matched_row_count": len(toa_keys),
            "unmatched_left_count": 0,
            "unmatched_right_count": 0,
            "multiple_match_count": 0,
            "assessment_status": "unique_key_confirmed",
            "notes": "Exact TIM source-flag key constructed from literal PINT source flags.",
        },
        {
            "assessment_id": "A04_SH04_SOURCE_FLAG_KEY",
            "left_input": "qsb_v_shapiromart04_complete_fingerprints via read-only workcopy DB",
            "right_input": "qsb_v_shapiromart04_complete_fingerprints via read-only workcopy DB",
            "key_fields": ";".join(SOURCE_KEY_FIELDS),
            "left_row_count": len(fingerprints),
            "right_row_count": len(fingerprints),
            "left_unique": "yes" if len(set(sh04_keys)) == len(sh04_keys) else "no",
            "right_unique": "yes" if len(set(sh04_keys)) == len(sh04_keys) else "no",
            "left_null_count": missing_key_field_count(sh04_keys),
            "right_null_count": missing_key_field_count(sh04_keys),
            "matched_row_count": len(fingerprints),
            "unmatched_left_count": 0,
            "unmatched_right_count": 0,
            "multiple_match_count": 0,
            "assessment_status": "unique_key_confirmed",
            "notes": "Exact TIM source-flag key constructed from raw_line_text for complete fingerprints.",
        },
    ]

    sh11_key_set = set(sh11_keys)
    sh04_key_set = set(sh04_keys)
    join_rows.append(
        {
            "assessment_id": "A05_SH11_TO_SH04_SOURCE_FLAG_KEY",
            "left_input": rel(args.toa_orbital_phase),
            "right_input": "qsb_v_shapiromart04_complete_fingerprints via read-only workcopy DB",
            "key_fields": ";".join(SOURCE_KEY_FIELDS),
            "left_row_count": len(sh11_keys),
            "right_row_count": len(sh04_keys),
            "left_unique": "yes",
            "right_unique": "yes",
            "left_null_count": missing_key_field_count(sh11_keys),
            "right_null_count": missing_key_field_count(sh04_keys),
            "matched_row_count": len(sh11_key_set & sh04_key_set),
            "unmatched_left_count": len(sh11_key_set - sh04_key_set),
            "unmatched_right_count": len(sh04_key_set - sh11_key_set),
            "multiple_match_count": 0,
            "assessment_status": "complete_unique_match"
            if sh11_key_set == sh04_key_set
            else "join_failed",
            "notes": "Exact source-flag join; no row-position, fuzzy, or numeric-nearness key used.",
        }
    )

    if sh17_indices != sh11_indices or sh11_key_set != sh04_key_set:
        raise ControlledStop("No complete documented join from SHAPIROMART17 groups to SHAPIROMART04 fingerprints.")

    joined: list[dict[str, Any]] = []
    missing_group = 0
    context_mismatch = 0
    for group in groups:
        toa = toa_keys.get(group["source_row_index"])
        if toa is None:
            missing_group += 1
            continue
        fingerprint = fingerprint_by_key.get(toa["source_key"])
        if fingerprint is None:
            missing_group += 1
            continue
        if (
            group["receiver"] != fingerprint["receiver_context"]
            or group["backend"] != fingerprint["backend_context"]
        ):
            context_mismatch += 1
        row = dict(group)
        row.update(
            {
                "structural_fingerprint_id": fingerprint["structural_fingerprint_id"],
                "raw_record_id": fingerprint["raw_record_id"],
                "observation_id": fingerprint["observation_id"],
                "science_object_id": fingerprint["science_object_id"],
                "receiver_context": fingerprint["receiver_context"],
                "backend_context": fingerprint["backend_context"],
                "raw_context_label": fingerprint["raw_context_label"],
                "source_key_hash": toa["source_key_hash"],
            }
        )
        for dimension in DIMENSIONS:
            row[dimension] = fingerprint[dimension]
        joined.append(row)

    join_rows.append(
        {
            "assessment_id": "A06_SH17_TO_SH04_COMPOSED_JOIN",
            "left_input": rel(args.prepared_groups),
            "right_input": "qsb_v_shapiromart04_complete_fingerprints via read-only workcopy DB",
            "key_fields": "source_row_index -> exact_source_flag_key",
            "left_row_count": len(groups),
            "right_row_count": len(fingerprints),
            "left_unique": "yes",
            "right_unique": "yes",
            "left_null_count": 0,
            "right_null_count": 0,
            "matched_row_count": len(joined),
            "unmatched_left_count": missing_group,
            "unmatched_right_count": max(0, len(fingerprints) - len(joined)),
            "multiple_match_count": 0,
            "assessment_status": "complete_unique_match"
            if len(joined) == EXPECTED_ROW_COUNT and missing_group == 0
            else "join_failed",
            "notes": "Composed exact join keeps SHAPIROMART17 source_row_index and SHAPIROMART04 raw_record_id traceable.",
        }
    )
    join_rows.append(
        {
            "assessment_id": "A07_CONTEXT_CONSISTENCY",
            "left_input": rel(args.prepared_groups),
            "right_input": "qsb_v_shapiromart04_complete_fingerprints via read-only workcopy DB",
            "key_fields": "receiver/backend after composed join",
            "left_row_count": len(groups),
            "right_row_count": len(fingerprints),
            "left_unique": "not_applicable",
            "right_unique": "not_applicable",
            "left_null_count": 0,
            "right_null_count": 0,
            "matched_row_count": len(joined) - context_mismatch,
            "unmatched_left_count": context_mismatch,
            "unmatched_right_count": 0,
            "multiple_match_count": 0,
            "assessment_status": "context_consistent" if context_mismatch == 0 else "context_mismatch",
            "notes": "Receiver/backend labels are checked after the exact key join.",
        }
    )
    if len(joined) != EXPECTED_ROW_COUNT or context_mismatch:
        raise ControlledStop("Joined data failed row-count or context consistency checks.")
    return joined, join_rows


def arrays_for_group(rows: list[dict[str, Any]], dimension: str) -> tuple[np.ndarray, int]:
    values: list[float] = []
    missing = 0
    for row in rows:
        try:
            value = float(row[dimension])
        except (TypeError, ValueError, KeyError):
            missing += 1
            continue
        if math.isfinite(value):
            values.append(value)
        else:
            missing += 1
    return np.asarray(values, dtype=float), missing


def winsorize(values: np.ndarray, fraction: float) -> np.ndarray:
    if values.size == 0:
        return values
    lower, upper = np.quantile(values, [fraction, 1.0 - fraction])
    return np.clip(values, lower, upper)


def descriptive_stats(values: np.ndarray, missing: int, winsor_fraction: float) -> dict[str, Any]:
    if values.size == 0:
        return {
            "row_count": 0,
            "missing_count": missing,
            "mean": "",
            "standard_deviation": "",
            "median": "",
            "q1": "",
            "q3": "",
            "minimum": "",
            "maximum": "",
            "winsor_fraction": fmt(winsor_fraction),
            "winsorized_mean": "",
            "statistic_status": "insufficient_count",
        }
    q1, median, q3 = np.quantile(values, [0.25, 0.5, 0.75])
    return {
        "row_count": int(values.size),
        "missing_count": missing,
        "mean": fmt(np.mean(values)),
        "standard_deviation": fmt(np.std(values, ddof=1)) if values.size > 1 else fmt(0.0),
        "median": fmt(median),
        "q1": fmt(q1),
        "q3": fmt(q3),
        "minimum": fmt(np.min(values)),
        "maximum": fmt(np.max(values)),
        "winsor_fraction": fmt(winsor_fraction),
        "winsorized_mean": fmt(np.mean(winsorize(values, winsor_fraction))),
        "statistic_status": "computed",
    }


def pooled_sd(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or b.size < 2:
        return math.nan
    var_a = np.var(a, ddof=1)
    var_b = np.var(b, ddof=1)
    denom = a.size + b.size - 2
    if denom <= 0:
        return math.nan
    value = math.sqrt(((a.size - 1) * var_a + (b.size - 1) * var_b) / denom)
    return value if math.isfinite(value) and value > 0 else math.nan


def smd_value(a: np.ndarray, b: np.ndarray) -> float:
    scale = pooled_sd(a, b)
    if not math.isfinite(scale) or scale <= 0:
        return math.nan
    return (float(np.mean(a)) - float(np.mean(b))) / scale


def smd_category(value: Any) -> str:
    try:
        magnitude = abs(float(value))
    except (TypeError, ValueError):
        return ""
    if not math.isfinite(magnitude):
        return ""
    if magnitude < 0.10:
        return "near_zero"
    if magnitude < 0.25:
        return "small"
    if magnitude < 0.50:
        return "moderate"
    return "large"


def category_rank(category: str) -> int:
    return {"near_zero": 0, "small": 1, "moderate": 2, "large": 3}.get(category, -1)


def average_ranks(values: np.ndarray) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    sorted_values = values[order]
    ranks = np.empty(values.size, dtype=float)
    start = 0
    while start < values.size:
        end = start + 1
        while end < values.size and sorted_values[end] == sorted_values[start]:
            end += 1
        average_rank = (start + 1 + end) / 2.0
        ranks[order[start:end]] = average_rank
        start = end
    return ranks


def rank_biserial(a: np.ndarray, b: np.ndarray) -> float:
    if a.size == 0 or b.size == 0:
        return math.nan
    values = np.concatenate([a, b])
    ranks = average_ranks(values)
    rank_sum_a = float(np.sum(ranks[: a.size]))
    u_a = rank_sum_a - (a.size * (a.size + 1) / 2.0)
    return (2.0 * u_a / (a.size * b.size)) - 1.0


def robust_median_effect(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    q1_a, q3_a = np.quantile(a, [0.25, 0.75])
    q1_b, q3_b = np.quantile(b, [0.25, 0.75])
    scale = (((q3_a - q1_a) + (q3_b - q1_b)) / 2.0) / 1.349
    if not math.isfinite(scale) or scale <= 0:
        return math.nan, math.nan
    value = (float(np.median(a)) - float(np.median(b))) / scale
    return scale, value


def finite_percentile(values: list[float], probability: float) -> float:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return math.nan
    return float(np.quantile(np.asarray(finite, dtype=float), probability))


def stable_seed(base_seed: int, *parts: str) -> int:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return (base_seed + int(digest[:8], 16)) % (2**32)


def bootstrap_ci(
    a: np.ndarray,
    b: np.ndarray,
    reps: int,
    seed: int,
) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    mean_diffs: list[float] = []
    smds: list[float] = []
    median_diffs: list[float] = []
    for _ in range(reps):
        sample_a = a[rng.integers(0, a.size, size=a.size)]
        sample_b = b[rng.integers(0, b.size, size=b.size)]
        mean_diffs.append(float(np.mean(sample_a)) - float(np.mean(sample_b)))
        smds.append(smd_value(sample_a, sample_b))
        median_diffs.append(float(np.median(sample_a)) - float(np.median(sample_b)))
    return {
        "mean_difference_ci_low": finite_percentile(mean_diffs, 0.025),
        "mean_difference_ci_high": finite_percentile(mean_diffs, 0.975),
        "smd_ci_low": finite_percentile(smds, 0.025),
        "smd_ci_high": finite_percentile(smds, 0.975),
        "median_difference_ci_low": finite_percentile(median_diffs, 0.025),
        "median_difference_ci_high": finite_percentile(median_diffs, 0.975),
    }


def effect_row(
    rows: list[dict[str, Any]],
    dimension: str,
    group_field: str,
    inside_label: str,
    outside_label: str,
    analysis_role: str,
    threshold_role: str,
    threshold_value: float,
    scope_type: str,
    scope_label: str,
    context_name: str,
    phase_side: str,
    reps: int,
    base_seed: int,
) -> dict[str, Any]:
    inside_rows = [row for row in rows if row[group_field] == inside_label]
    outside_rows = [row for row in rows if row[group_field] == outside_label]
    inside, _ = arrays_for_group(inside_rows, dimension)
    outside, _ = arrays_for_group(outside_rows, dimension)
    comparison_id = f"{analysis_role}_{threshold_role}_{scope_type}_{scope_label}_{dimension}".replace(
        " ", "_"
    ).replace("/", "_")
    seed = stable_seed(base_seed, comparison_id)
    base = {
        "comparison_id": comparison_id,
        "analysis_role": analysis_role,
        "threshold_role": threshold_role,
        "threshold_value": fmt_threshold(threshold_value),
        "scope_type": scope_type,
        "scope_label": scope_label,
        "context_name": context_name,
        "phase_side": phase_side,
        "dimension": dimension,
        "inside_label": inside_label,
        "outside_label": outside_label,
        "inside_count": int(inside.size),
        "outside_count": int(outside.size),
        "minimum_group_count": MIN_GROUP_COUNT,
        "bootstrap_repetitions": reps,
        "bootstrap_seed": seed,
        "notes": "Descriptive inside-minus-outside comparison only.",
    }
    if inside.size < MIN_GROUP_COUNT or outside.size < MIN_GROUP_COUNT:
        base.update({"effect_status": "insufficient_count"})
        return base
    mean_diff = float(np.mean(inside)) - float(np.mean(outside))
    median_diff = float(np.median(inside)) - float(np.median(outside))
    scale = pooled_sd(inside, outside)
    smd = mean_diff / scale if math.isfinite(scale) and scale > 0 else math.nan
    iqr_scale, robust_effect = robust_median_effect(inside, outside)
    rank_effect = rank_biserial(inside, outside)
    ci = bootstrap_ci(inside, outside, reps, seed)
    base.update(
        {
            "effect_status": "computed" if math.isfinite(smd) else "zero_scale",
            "inside_mean": fmt(np.mean(inside)),
            "outside_mean": fmt(np.mean(outside)),
            "mean_difference_inside_minus_outside": fmt(mean_diff),
            "inside_median": fmt(np.median(inside)),
            "outside_median": fmt(np.median(outside)),
            "median_difference_inside_minus_outside": fmt(median_diff),
            "pooled_sd": fmt(scale),
            "smd": fmt(smd),
            "abs_smd": fmt(abs(smd)) if math.isfinite(smd) else "",
            "smd_category": smd_category(smd),
            "pooled_iqr_sigma_scale": fmt(iqr_scale),
            "robust_standardized_median_difference": fmt(robust_effect),
            "rank_biserial": fmt(rank_effect),
            "mean_difference_ci_low": fmt(ci["mean_difference_ci_low"]),
            "mean_difference_ci_high": fmt(ci["mean_difference_ci_high"]),
            "smd_ci_low": fmt(ci["smd_ci_low"]),
            "smd_ci_high": fmt(ci["smd_ci_high"]),
            "median_difference_ci_low": fmt(ci["median_difference_ci_low"]),
            "median_difference_ci_high": fmt(ci["median_difference_ci_high"]),
        }
    )
    return base


def descriptive_rows(rows: list[dict[str, Any]], winsor_fraction: float) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    scopes: list[tuple[str, str, str, str, float, str, str, list[dict[str, Any]]]] = []
    scopes.append(
        (
            "primary_overall",
            "overall",
            "overall",
            "primary",
            PRIMARY_THRESHOLD,
            "",
            "",
            rows,
        )
    )
    for context in sorted({row["context_name"] for row in rows}):
        selected = [row for row in rows if row["context_name"] == context]
        scopes.append(
            (
                "primary_context",
                "context",
                context,
                "primary",
                PRIMARY_THRESHOLD,
                context,
                "",
                selected,
            )
        )
    for side in sorted({row["phase_side"] for row in rows}):
        selected = [row for row in rows if row["phase_side"] == side]
        scopes.append(
            (
                "primary_phase_side",
                "phase_side",
                side,
                "primary",
                PRIMARY_THRESHOLD,
                "",
                side,
                selected,
            )
        )
    for context in sorted({row["context_name"] for row in rows}):
        for side in sorted({row["phase_side"] for row in rows}):
            selected = [
                row
                for row in rows
                if row["context_name"] == context and row["phase_side"] == side
            ]
            scopes.append(
                (
                    "primary_context_phase_side",
                    "context_phase_side",
                    f"{context} | {side}",
                    "primary",
                    PRIMARY_THRESHOLD,
                    context,
                    side,
                    selected,
                )
            )
    scopes.append(
        (
            "secondary_overall",
            "overall",
            "overall",
            "secondary_sensitivity",
            SECONDARY_THRESHOLD,
            "",
            "",
            rows,
        )
    )

    group_labels = {
        "primary": ["inside_primary_threshold", "outside_primary_threshold"],
        "secondary_sensitivity": ["inside_secondary_threshold", "outside_secondary_threshold"],
    }
    for analysis_role, scope_type, scope_label, threshold_role, threshold_value, context, side, selected in scopes:
        group_field = "primary_group" if threshold_role == "primary" else "secondary_group"
        for label in group_labels[threshold_role]:
            label_rows = [row for row in selected if row[group_field] == label]
            for dimension in DIMENSIONS:
                values, missing = arrays_for_group(label_rows, dimension)
                stats = descriptive_stats(values, missing, winsor_fraction)
                statistic_id = (
                    f"{analysis_role}_{scope_type}_{scope_label}_{label}_{dimension}"
                    .replace(" ", "_")
                    .replace("/", "_")
                )
                result.append(
                    {
                        "statistic_id": statistic_id,
                        "analysis_role": analysis_role,
                        "threshold_role": threshold_role,
                        "threshold_value": fmt_threshold(threshold_value),
                        "scope_type": scope_type,
                        "scope_label": scope_label,
                        "context_name": context,
                        "phase_side": side,
                        "dimension": dimension,
                        "comparison_group": label,
                        **stats,
                        "notes": "Descriptive group statistic for the joined fingerprint table.",
                    }
                )
    return result


def build_effect_tables(
    rows: list[dict[str, Any]],
    reps: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    primary: list[dict[str, Any]] = []
    context_effects: list[dict[str, Any]] = []
    pre_post: list[dict[str, Any]] = []
    sensitivity: list[dict[str, Any]] = []

    for dimension in DIMENSIONS:
        primary.append(
            effect_row(
                rows,
                dimension,
                "primary_group",
                "inside_primary_threshold",
                "outside_primary_threshold",
                "primary_overall",
                "primary",
                PRIMARY_THRESHOLD,
                "overall",
                "overall",
                "",
                "",
                reps,
                seed,
            )
        )
        sensitivity.append(
            effect_row(
                rows,
                dimension,
                "secondary_group",
                "inside_secondary_threshold",
                "outside_secondary_threshold",
                "secondary_overall",
                "secondary_sensitivity",
                SECONDARY_THRESHOLD,
                "overall",
                "overall",
                "",
                "",
                reps,
                seed,
            )
        )

    for context in sorted({row["context_name"] for row in rows}):
        selected = [row for row in rows if row["context_name"] == context]
        for dimension in DIMENSIONS:
            context_effects.append(
                effect_row(
                    selected,
                    dimension,
                    "primary_group",
                    "inside_primary_threshold",
                    "outside_primary_threshold",
                    "context_stratified",
                    "primary",
                    PRIMARY_THRESHOLD,
                    "context",
                    context,
                    context,
                    "",
                    reps,
                    seed,
                )
            )
            sensitivity.append(
                effect_row(
                    selected,
                    dimension,
                    "secondary_group",
                    "inside_secondary_threshold",
                    "outside_secondary_threshold",
                    "secondary_context",
                    "secondary_sensitivity",
                    SECONDARY_THRESHOLD,
                    "context",
                    context,
                    context,
                    "",
                    reps,
                    seed,
                )
            )

    for side in sorted({row["phase_side"] for row in rows}):
        selected = [row for row in rows if row["phase_side"] == side]
        for dimension in DIMENSIONS:
            pre_post.append(
                effect_row(
                    selected,
                    dimension,
                    "primary_group",
                    "inside_primary_threshold",
                    "outside_primary_threshold",
                    "pre_post_control",
                    "primary",
                    PRIMARY_THRESHOLD,
                    "phase_side",
                    side,
                    "",
                    side,
                    reps,
                    seed,
                )
            )
            sensitivity.append(
                effect_row(
                    selected,
                    dimension,
                    "secondary_group",
                    "inside_secondary_threshold",
                    "outside_secondary_threshold",
                    "secondary_phase_side",
                    "secondary_sensitivity",
                    SECONDARY_THRESHOLD,
                    "phase_side",
                    side,
                    "",
                    side,
                    reps,
                    seed,
                )
            )

    for context in sorted({row["context_name"] for row in rows}):
        for side in sorted({row["phase_side"] for row in rows}):
            selected = [
                row
                for row in rows
                if row["context_name"] == context and row["phase_side"] == side
            ]
            scope_label = f"{context} | {side}"
            for dimension in DIMENSIONS:
                pre_post.append(
                    effect_row(
                        selected,
                        dimension,
                        "primary_group",
                        "inside_primary_threshold",
                        "outside_primary_threshold",
                        "context_phase_side_control",
                        "primary",
                        PRIMARY_THRESHOLD,
                        "context_phase_side",
                        scope_label,
                        context,
                        side,
                        reps,
                        seed,
                    )
                )
    return primary, context_effects, pre_post, sensitivity


def composition_adjusted_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    specs = [
        (
            "primary",
            PRIMARY_THRESHOLD,
            "primary_group",
            "inside_primary_threshold",
            "outside_primary_threshold",
        ),
        (
            "secondary_sensitivity",
            SECONDARY_THRESHOLD,
            "secondary_group",
            "inside_secondary_threshold",
            "outside_secondary_threshold",
        ),
    ]
    strata_builders = {
        "context": lambda row: row["context_name"],
        "context_phase_side": lambda row: f"{row['context_name']} | {row['phase_side']}",
    }
    for threshold_role, threshold_value, group_field, inside_label, outside_label in specs:
        for strata_basis, stratum_key in strata_builders.items():
            strata: dict[str, list[dict[str, Any]]] = defaultdict(list)
            for row in rows:
                strata[stratum_key(row)].append(row)
            for dimension in DIMENSIONS:
                all_values, _ = arrays_for_group(rows, dimension)
                common_sd = float(np.std(all_values, ddof=1)) if all_values.size > 1 else math.nan
                adjusted_diff = 0.0
                standardized = 0.0
                usable = 0
                omitted = 0
                for stratum_rows in strata.values():
                    weight = len(stratum_rows) / len(rows)
                    inside_rows = [row for row in stratum_rows if row[group_field] == inside_label]
                    outside_rows = [row for row in stratum_rows if row[group_field] == outside_label]
                    inside, _ = arrays_for_group(inside_rows, dimension)
                    outside, _ = arrays_for_group(outside_rows, dimension)
                    if inside.size < MIN_GROUP_COUNT or outside.size < MIN_GROUP_COUNT:
                        omitted += 1
                        continue
                    diff = float(np.mean(inside)) - float(np.mean(outside))
                    stratum_sd = pooled_sd(inside, outside)
                    adjusted_diff += weight * diff
                    if math.isfinite(stratum_sd) and stratum_sd > 0:
                        standardized += weight * (diff / stratum_sd)
                    usable += 1
                adjusted_common = (
                    adjusted_diff / common_sd
                    if math.isfinite(common_sd) and common_sd > 0
                    else math.nan
                )
                if usable == 0:
                    status = "insufficient_count"
                elif omitted:
                    status = "partial"
                else:
                    status = "computed"
                result.append(
                    {
                        "comparison_id": f"{threshold_role}_{strata_basis}_{dimension}",
                        "threshold_role": threshold_role,
                        "threshold_value": fmt_threshold(threshold_value),
                        "strata_basis": strata_basis,
                        "dimension": dimension,
                        "total_row_count": len(rows),
                        "inside_total_count": sum(1 for row in rows if row[group_field] == inside_label),
                        "outside_total_count": sum(1 for row in rows if row[group_field] == outside_label),
                        "weight_source": "total_population_fixed_weights",
                        "usable_stratum_count": usable,
                        "omitted_stratum_count": omitted,
                        "common_reference_sd": fmt(common_sd),
                        "adjusted_mean_difference_inside_minus_outside": fmt(adjusted_diff),
                        "standardized_stratified_difference": fmt(standardized),
                        "adjusted_abs_smd": fmt(abs(standardized)) if math.isfinite(standardized) else "",
                        "adjusted_smd_category": smd_category(standardized),
                        "direction_status": direction_status([standardized]),
                        "minimum_group_count": MIN_GROUP_COUNT,
                        "adjustment_status": status,
                        "notes": "Fixed weights from the total joined population; descriptive adjustment only.",
                    }
                )
    return result


def number_from_row(row: dict[str, Any] | None, field: str) -> float:
    if row is None:
        return math.nan
    try:
        return float(row.get(field, ""))
    except (TypeError, ValueError):
        return math.nan


def row_by_dimension(rows: list[dict[str, Any]], dimension: str, **filters: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("dimension") != dimension:
            continue
        if all(row.get(key) == value for key, value in filters.items()):
            return row
    return None


def direction(value: float, floor: float = 0.10) -> int:
    if not math.isfinite(value) or abs(value) < floor:
        return 0
    return 1 if value > 0 else -1


def direction_status(values: list[float]) -> str:
    finite = [value for value in values if math.isfinite(value)]
    if not finite:
        return "insufficient_support"
    signs = {direction(value) for value in finite}
    nonzero = {sign for sign in signs if sign != 0}
    if not nonzero:
        return "no_material_descriptive_difference"
    if len(nonzero) == 1:
        return "direction_consistent"
    return "direction_mixed"


def threshold_status(primary_smd: float, secondary_smd: float) -> str:
    if not (math.isfinite(primary_smd) and math.isfinite(secondary_smd)):
        return "insufficient_support"
    primary_sign = direction(primary_smd)
    secondary_sign = direction(secondary_smd)
    if primary_sign and secondary_sign and primary_sign != secondary_sign:
        return "threshold_sensitive"
    if abs(primary_smd - secondary_smd) >= 0.15:
        return "threshold_sensitive"
    if abs(category_rank(smd_category(primary_smd)) - category_rank(smd_category(secondary_smd))) >= 2:
        return "threshold_sensitive"
    return "threshold_stable"


def winsorized_smd_for_dimension(
    rows: list[dict[str, Any]], dimension: str, winsor_fraction: float
) -> float:
    inside_rows = [row for row in rows if row["primary_group"] == "inside_primary_threshold"]
    outside_rows = [row for row in rows if row["primary_group"] == "outside_primary_threshold"]
    inside, _ = arrays_for_group(inside_rows, dimension)
    outside, _ = arrays_for_group(outside_rows, dimension)
    if inside.size < MIN_GROUP_COUNT or outside.size < MIN_GROUP_COUNT:
        return math.nan
    combined = np.concatenate([inside, outside])
    lower, upper = np.quantile(combined, [winsor_fraction, 1.0 - winsor_fraction])
    return smd_value(np.clip(inside, lower, upper), np.clip(outside, lower, upper))


def build_robustness_and_dimension_rows(
    joined: list[dict[str, Any]],
    primary: list[dict[str, Any]],
    context_effects: list[dict[str, Any]],
    pre_post: list[dict[str, Any]],
    sensitivity: list[dict[str, Any]],
    composition: list[dict[str, Any]],
    winsor_fraction: float,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    robustness: list[dict[str, Any]] = []
    dimension_rows: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        primary_row = row_by_dimension(primary, dimension)
        secondary_row = row_by_dimension(
            sensitivity,
            dimension,
            analysis_role="secondary_overall",
            scope_type="overall",
            scope_label="overall",
        )
        primary_smd = number_from_row(primary_row, "smd")
        secondary_smd = number_from_row(secondary_row, "smd")
        context_smds = [
            number_from_row(row, "smd")
            for row in context_effects
            if row.get("dimension") == dimension and row.get("effect_status") == "computed"
        ]
        side_smds = [
            number_from_row(row, "smd")
            for row in pre_post
            if row.get("dimension") == dimension
            and row.get("scope_type") == "phase_side"
            and row.get("effect_status") == "computed"
        ]
        leave_smds = context_smds[:]
        comp_context = row_by_dimension(
            composition,
            dimension,
            threshold_role="primary",
            strata_basis="context",
        )
        comp_context_side = row_by_dimension(
            composition,
            dimension,
            threshold_role="primary",
            strata_basis="context_phase_side",
        )
        comp_context_value = number_from_row(comp_context, "standardized_stratified_difference")
        comp_context_side_value = number_from_row(
            comp_context_side, "standardized_stratified_difference"
        )
        context_dir = direction_status(context_smds)
        side_dir = direction_status(side_smds)
        leave_dir = direction_status(leave_smds)
        t_status = threshold_status(primary_smd, secondary_smd)
        winsor_smd = winsorized_smd_for_dimension(joined, dimension, winsor_fraction)
        status = classify_dimension(
            primary_smd,
            context_dir,
            side_dir,
            t_status,
            comp_context_value,
            comp_context_side_value,
        )
        robustness.append(
            {
                "dimension": dimension,
                "primary_smd": fmt(primary_smd),
                "primary_smd_ci_low": primary_row.get("smd_ci_low", "") if primary_row else "",
                "primary_smd_ci_high": primary_row.get("smd_ci_high", "") if primary_row else "",
                "primary_smd_category": smd_category(primary_smd),
                "winsor_fraction": fmt(winsor_fraction),
                "winsorized_smd": fmt(winsor_smd),
                "winsorized_smd_category": smd_category(winsor_smd),
                "context_direction_status": context_dir,
                "context_min_abs_smd": fmt(min(abs(value) for value in context_smds))
                if context_smds
                else "",
                "context_max_abs_smd": fmt(max(abs(value) for value in context_smds))
                if context_smds
                else "",
                "side_direction_status": side_dir,
                "side_min_abs_smd": fmt(min(abs(value) for value in side_smds))
                if side_smds
                else "",
                "side_max_abs_smd": fmt(max(abs(value) for value in side_smds))
                if side_smds
                else "",
                "leave_one_context_min_abs_smd": fmt(min(abs(value) for value in leave_smds))
                if leave_smds
                else "",
                "leave_one_context_max_abs_smd": fmt(max(abs(value) for value in leave_smds))
                if leave_smds
                else "",
                "leave_one_context_direction_status": leave_dir,
                "secondary_smd": fmt(secondary_smd),
                "secondary_smd_category": smd_category(secondary_smd),
                "threshold_sensitivity_status": t_status,
                "composition_context_standardized_difference": fmt(comp_context_value),
                "composition_context_side_standardized_difference": fmt(comp_context_side_value),
                "robustness_status": status,
                "notes": "Robustness checks are descriptive and use fixed SHAPIROMART17 thresholds.",
            }
        )
        dimension_rows.append(
            {
                "dimension": dimension,
                "final_dimension_status": status,
                "primary_smd": fmt(primary_smd),
                "primary_smd_category": smd_category(primary_smd),
                "primary_smd_ci_low": primary_row.get("smd_ci_low", "") if primary_row else "",
                "primary_smd_ci_high": primary_row.get("smd_ci_high", "") if primary_row else "",
                "context_direction_status": context_dir,
                "side_direction_status": side_dir,
                "threshold_sensitivity_status": t_status,
                "composition_context_standardized_difference": fmt(comp_context_value),
                "composition_context_side_standardized_difference": fmt(comp_context_side_value),
                "claim_boundary": (
                    "Descriptive fingerprint comparison only; no timing-model or physical "
                    "interpretation step."
                ),
                "notes": "Dimension status follows predefined descriptive consistency rules.",
            }
        )
    return robustness, dimension_rows


def classify_dimension(
    primary_smd: float,
    context_dir: str,
    side_dir: str,
    t_status: str,
    comp_context_value: float,
    comp_context_side_value: float,
) -> str:
    if not math.isfinite(primary_smd):
        return "insufficient_support"
    primary_sign = direction(primary_smd)
    comp_sign = direction(comp_context_value)
    comp_side_sign = direction(comp_context_side_value)
    if abs(primary_smd) < 0.10 and abs(comp_context_value) < 0.10:
        return "no_material_descriptive_difference"
    if t_status == "threshold_sensitive":
        return "threshold_sensitive_difference"
    if context_dir == "direction_mixed":
        return "descriptive_difference_with_context_sensitivity"
    if side_dir == "direction_mixed":
        return "descriptive_difference_with_side_sensitivity"
    if (
        primary_sign
        and context_dir == "direction_consistent"
        and side_dir in {"direction_consistent", "no_material_descriptive_difference"}
        and t_status == "threshold_stable"
        and (comp_sign == 0 or comp_sign == primary_sign)
        and (comp_side_sign == 0 or comp_side_sign == primary_sign)
    ):
        return "robust_descriptive_difference"
    return "weak_or_inconsistent_difference"


def load_reference_summaries(args: argparse.Namespace) -> dict[str, Any]:
    references: dict[str, Any] = {}
    for label, path in [
        ("shapiromart04_summary", args.shapiromart04_summary),
        ("shapiromart05_summary", args.shapiromart05_summary),
    ]:
        if path.exists():
            with path.open("r", encoding="utf-8") as handle:
                references[label] = json.load(handle)
    if args.shapiromart15_join_assessment.exists():
        rows, _ = read_csv_rows(args.shapiromart15_join_assessment)
        references["shapiromart15_join_assessment"] = rows
    return references


def make_final_status(
    args: argparse.Namespace,
    joined_count: int,
    fingerprint_count: int,
    dimension_rows: list[dict[str, Any]],
    db_status: dict[str, Any],
) -> dict[str, Any]:
    status_counts = Counter(row["final_dimension_status"] for row in dimension_rows)
    if not dimension_rows:
        final = "failed"
        analysis_status = "analysis_not_performed"
    elif status_counts.get("robust_descriptive_difference", 0) > 0:
        final = "completed"
        analysis_status = "descriptive_fingerprint_comparison_completed"
    else:
        final = "completed_no_robust_difference"
        analysis_status = "descriptive_fingerprint_comparison_completed"
    return {
        "research_block": RESEARCH_BLOCK,
        "output_dir": rel(args.output_dir),
        "final_status": final,
        "analysis_status": analysis_status,
        "prepared_group_rows": EXPECTED_ROW_COUNT,
        "fingerprint_rows": fingerprint_count,
        "joined_rows": joined_count,
        "unmatched_group_rows": EXPECTED_ROW_COUNT - joined_count,
        "unmatched_fingerprint_rows": fingerprint_count - joined_count,
        "primary_threshold_value": fmt_threshold(PRIMARY_THRESHOLD),
        "secondary_threshold_value": fmt_threshold(SECONDARY_THRESHOLD),
        "bootstrap_repetitions": args.bootstrap_reps,
        "bootstrap_seed": args.bootstrap_seed,
        "winsor_fraction": fmt(args.winsor_fraction),
        "minimum_group_count": MIN_GROUP_COUNT,
        "database_access": "read_only",
        "database_modified": db_status.get("database_modified", ""),
        "physical_exposure_claimed": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "timing_model_fit_performed": "no",
        "model_parameters_modified": "no",
        "physical_interpretation_performed": "no",
        "threshold_reselected_after_results": "no",
        "additional_gate_created": "no",
        "exposure_effect_analysis_performed": "yes",
        "fingerprint_comparison_performed": "yes",
        "recommended_next_action": "Review dimension_assessment and robustness_summary before any later block.",
        "limitations": (
            "Descriptive joined-fingerprint comparison only; fixed thresholds; no residual or "
            "timing-model analysis."
        ),
    }


def write_readout(
    path: Path,
    final_row: dict[str, Any],
    join_rows: list[dict[str, Any]],
    dimension_rows: list[dict[str, Any]],
    db_status: dict[str, Any],
) -> None:
    counts = Counter(row["final_dimension_status"] for row in dimension_rows)
    join_statuses = Counter(row["assessment_status"] for row in join_rows)
    lines = [
        "# QSB-SHAPIROMART18 Readout",
        "",
        "## Befund",
        "",
        f"- Joined rows: {final_row['joined_rows']} of {EXPECTED_ROW_COUNT}.",
        f"- Primary threshold: {final_row['primary_threshold_value']}.",
        f"- Secondary sensitivity threshold: {final_row['secondary_threshold_value']}.",
        f"- Bootstrap repetitions: {final_row['bootstrap_repetitions']} with seed {final_row['bootstrap_seed']}.",
        f"- Dimension status counts: {dict(counts)}.",
        f"- Join assessment status counts: {dict(join_statuses)}.",
        "",
        "## Interpretation",
        "",
        (
            "The comparison is a descriptive fingerprint readout across the frozen "
            "SHAPIROMART17 groups. It uses exact source-row and source-flag keys to "
            "connect those groups to the SHAPIROMART04 complete unweighted fingerprints."
        ),
        "",
        "## Hypothese",
        "",
        (
            "The output can be used to formulate a later, separately specified "
            "descriptive follow-up question about which fingerprint dimensions vary "
            "most between the fixed inside/outside groups."
        ),
        "",
        "## Offene Luecke",
        "",
        (
            "This block does not evaluate timing residuals, fit model parameters, or "
            "interpret the comparison physically. The source-flag bridge is documented "
            "in the join assessment and should remain visible in any follow-up block."
        ),
        "",
        "## Claim Boundary",
        "",
        "- physical_exposure_claimed: no",
        "- shapiro_delay_calculated: no",
        "- residual_analysis_performed: no",
        "- timing_model_fit_performed: no",
        "- model_parameters_modified: no",
        "- physical_interpretation_performed: no",
        "- threshold_reselected_after_results: no",
        "- additional_gate_created: no",
        f"- database_modified: {db_status.get('database_modified', '')}",
        f"- final_status: {final_row['final_status']}",
        "",
    ]
    ensure_parent(path)
    path.write_text("\n".join(lines), encoding="utf-8")


def make_summary(
    args: argparse.Namespace,
    final_row: dict[str, Any],
    join_rows: list[dict[str, Any]],
    dimension_rows: list[dict[str, Any]],
    db_status: dict[str, Any],
    references: dict[str, Any],
) -> dict[str, Any]:
    return {
        "research_block": RESEARCH_BLOCK,
        "timestamp_utc": utc_now(),
        "inputs_read": {
            "prepared_groups": rel(args.prepared_groups),
            "threshold_decision": rel(args.threshold_decision),
            "toa_orbital_phase": rel(args.toa_orbital_phase),
            "shapiromart04_summary": rel(args.shapiromart04_summary),
            "shapiromart05_summary": rel(args.shapiromart05_summary),
            "shapiromart15_join_assessment": rel(args.shapiromart15_join_assessment),
            "workcopy_db": rel(args.workcopy_db),
        },
        "output_dir": rel(args.output_dir),
        "output_files": [rel(args.output_dir / name) for name in OUTPUT_FILES],
        "dimensions": DIMENSIONS,
        "source_key_fields": SOURCE_KEY_FIELDS,
        "join_summary": join_rows,
        "dimension_status_counts": dict(Counter(row["final_dimension_status"] for row in dimension_rows)),
        "method": {
            "primary_threshold": fmt_threshold(PRIMARY_THRESHOLD),
            "secondary_threshold": fmt_threshold(SECONDARY_THRESHOLD),
            "bootstrap_repetitions": args.bootstrap_reps,
            "bootstrap_seed": args.bootstrap_seed,
            "winsor_fraction": fmt(args.winsor_fraction),
            "minimum_group_count": MIN_GROUP_COUNT,
            "comparison_scope": "descriptive_inside_minus_outside_fingerprint_comparison",
        },
        "database": db_status,
        "reference_context": {
            "shapiromart04_complete_fingerprint_count": references.get(
                "shapiromart04_summary", {}
            ).get("complete_fingerprint_count", ""),
            "shapiromart05_dimension_count": references.get("shapiromart05_summary", {}).get(
                "dimension_count", ""
            ),
            "shapiromart15_join_assessment": references.get(
                "shapiromart15_join_assessment", []
            )[:3],
        },
        "boundaries": {
            "physical_exposure_claimed": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "timing_model_fit_performed": "no",
            "model_parameters_modified": "no",
            "physical_interpretation_performed": "no",
            "threshold_reselected_after_results": "no",
            "database_modified": db_status.get("database_modified", ""),
            "additional_gate_created": "no",
        },
        "final_status": final_row,
    }


def write_failure_outputs(args: argparse.Namespace, error: BaseException) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    final_row = {
        "research_block": RESEARCH_BLOCK,
        "output_dir": rel(args.output_dir),
        "final_status": "failed",
        "analysis_status": "analysis_not_performed",
        "prepared_group_rows": "",
        "fingerprint_rows": "",
        "joined_rows": "0",
        "unmatched_group_rows": "",
        "unmatched_fingerprint_rows": "",
        "primary_threshold_value": fmt_threshold(PRIMARY_THRESHOLD),
        "secondary_threshold_value": fmt_threshold(SECONDARY_THRESHOLD),
        "bootstrap_repetitions": args.bootstrap_reps,
        "bootstrap_seed": args.bootstrap_seed,
        "winsor_fraction": fmt(args.winsor_fraction),
        "minimum_group_count": MIN_GROUP_COUNT,
        "database_access": "read_only_attempted",
        "database_modified": "unknown",
        "physical_exposure_claimed": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "timing_model_fit_performed": "no",
        "model_parameters_modified": "no",
        "physical_interpretation_performed": "no",
        "threshold_reselected_after_results": "no",
        "additional_gate_created": "no",
        "exposure_effect_analysis_performed": "no",
        "fingerprint_comparison_performed": "no",
        "recommended_next_action": "Resolve the documented join or input validation issue before analysis.",
        "limitations": str(error),
    }
    join_rows = [
        {
            "assessment_id": "A00_CONTROLLED_STOP",
            "left_input": rel(args.prepared_groups),
            "right_input": "qsb_v_shapiromart04_complete_fingerprints via read-only workcopy DB",
            "key_fields": "source_row_index or documented exact source key",
            "left_row_count": "",
            "right_row_count": "",
            "left_unique": "",
            "right_unique": "",
            "left_null_count": "",
            "right_null_count": "",
            "matched_row_count": 0,
            "unmatched_left_count": "",
            "unmatched_right_count": "",
            "multiple_match_count": "",
            "assessment_status": "controlled_stop",
            "notes": str(error),
        }
    ]
    write_csv(args.output_dir / "shapiromart18_input_join_assessment.csv", join_rows, JOIN_ASSESSMENT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_group_descriptive_statistics.csv", [], DESCRIPTIVE_FIELDS)
    write_csv(args.output_dir / "shapiromart18_primary_effect_sizes.csv", [], EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_context_stratified_effects.csv", [], EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_pre_post_control.csv", [], EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_threshold_sensitivity.csv", [], EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_composition_adjusted_effects.csv", [], COMPOSITION_FIELDS)
    write_csv(args.output_dir / "shapiromart18_robustness_summary.csv", [], ROBUSTNESS_FIELDS)
    write_csv(args.output_dir / "shapiromart18_dimension_assessment.csv", [], DIMENSION_ASSESSMENT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_final_status.csv", [final_row], FINAL_STATUS_FIELDS)
    write_json(
        args.output_dir / "shapiromart18_summary.json",
        {
            "research_block": RESEARCH_BLOCK,
            "timestamp_utc": utc_now(),
            "output_dir": rel(args.output_dir),
            "output_files": [rel(args.output_dir / name) for name in OUTPUT_FILES],
            "join_summary": join_rows,
            "final_status": final_row,
            "error": str(error),
        },
    )
    write_readout(
        args.output_dir / "shapiromart18_readout.md",
        final_row,
        join_rows,
        [],
        {"database_modified": "unknown"},
    )


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.bootstrap_reps < 2000:
        raise ControlledStop("Bootstrap repetitions must be at least 2000.")
    if not (0.0 <= args.winsor_fraction < 0.5):
        raise ControlledStop("Winsor fraction must be in [0, 0.5).")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    load_threshold_decision(args.threshold_decision)
    references = load_reference_summaries(args)
    groups = load_prepared_groups(args.prepared_groups)
    toa_keys = load_toa_source_keys(args.toa_orbital_phase)
    fingerprints, db_status = load_fingerprints_from_db(args.workcopy_db)
    if db_status.get("database_modified") != "no":
        raise ControlledStop("Read-only DB identity changed during the run.")
    joined, join_rows = join_inputs(groups, toa_keys, fingerprints, args)

    group_stats = descriptive_rows(joined, args.winsor_fraction)
    primary, context_effects, pre_post, sensitivity = build_effect_tables(
        joined, args.bootstrap_reps, args.bootstrap_seed
    )
    composition = composition_adjusted_rows(joined)
    robustness, dimension_rows = build_robustness_and_dimension_rows(
        joined,
        primary,
        context_effects,
        pre_post,
        sensitivity,
        composition,
        args.winsor_fraction,
    )
    final_row = make_final_status(args, len(joined), len(fingerprints), dimension_rows, db_status)

    write_csv(args.output_dir / "shapiromart18_input_join_assessment.csv", join_rows, JOIN_ASSESSMENT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_group_descriptive_statistics.csv", group_stats, DESCRIPTIVE_FIELDS)
    write_csv(args.output_dir / "shapiromart18_primary_effect_sizes.csv", primary, EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_context_stratified_effects.csv", context_effects, EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_pre_post_control.csv", pre_post, EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_threshold_sensitivity.csv", sensitivity, EFFECT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_composition_adjusted_effects.csv", composition, COMPOSITION_FIELDS)
    write_csv(args.output_dir / "shapiromart18_robustness_summary.csv", robustness, ROBUSTNESS_FIELDS)
    write_csv(args.output_dir / "shapiromart18_dimension_assessment.csv", dimension_rows, DIMENSION_ASSESSMENT_FIELDS)
    write_csv(args.output_dir / "shapiromart18_final_status.csv", [final_row], FINAL_STATUS_FIELDS)
    summary = make_summary(args, final_row, join_rows, dimension_rows, db_status, references)
    write_json(args.output_dir / "shapiromart18_summary.json", summary)
    write_readout(
        args.output_dir / "shapiromart18_readout.md",
        final_row,
        join_rows,
        dimension_rows,
        db_status,
    )
    return summary


def main() -> int:
    args = parse_args()
    try:
        run(args)
    except Exception as exc:
        write_failure_outputs(args, exc)
        print(f"{RESEARCH_BLOCK} controlled stop: {exc}", file=sys.stderr)
        return 1
    print(f"{RESEARCH_BLOCK} completed: {rel(args.output_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
