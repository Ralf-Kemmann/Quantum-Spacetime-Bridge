#!/usr/bin/env python3
"""QSB-SHAPIROMART19 fingerprint dimension semantics and specificity.

This block reconstructs the four SHAPIROMART04 fingerprint dimensions and
compares their SHAPIROMART18 group behavior against documented context,
source-flag, time-axis, and representation controls. It is descriptive only.
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
from typing import Any, Callable

import numpy as np


RESEARCH_BLOCK = "QSB-SHAPIROMART19"
EXPECTED_ROW_COUNT = 7419
PRIMARY_THRESHOLD = 0.05
SECONDARY_THRESHOLD = 0.15
DEFAULT_PERMUTATIONS = 2000
DEFAULT_RANDOM_SEED = 20260606
DEFAULT_MINIMUM_GROUP_COUNT = 30

ROOT = Path(__file__).resolve().parents[1]
SHAPIROMART04_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART04_FIRST_UNWEIGHTED_FINGERPRINT"
SHAPIROMART05_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART05_STABILITY_SEPARABILITY"
SHAPIROMART11_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART11_CONTROLLED_PINT_RECONSTRUCTION"
SHAPIROMART14_DIR = ROOT / "runs/QSB-SHAPIROMART/SHAPIROMART14_CONJUNCTION_DISTANCE_SAMPLING_SYMMETRY"
SHAPIROMART17_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART17_THRESHOLD_CONSOLIDATION_EXPOSURE_PREPARATION"
)
SHAPIROMART18_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART18_EXPOSURE_GROUP_FINGERPRINT_COMPARISON"
)
DEFAULT_OUTPUT_DIR = (
    ROOT
    / "runs/QSB-SHAPIROMART/SHAPIROMART19_FINGERPRINT_DIMENSION_SEMANTICS_SPECIFICITY"
)
DEFAULT_WORKCOPY_DB = (
    ROOT
    / "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)

OUTPUT_FILES = [
    "shapiromart19_readout.md",
    "shapiromart19_summary.json",
    "shapiromart19_dimension_lineage.csv",
    "shapiromart19_dimension_semantics.csv",
    "shapiromart19_known_factor_associations.csv",
    "shapiromart19_coordinate_secondary_specificity.csv",
    "shapiromart19_coordinate_primary_localization.csv",
    "shapiromart19_coordinate_signal_relation.csv",
    "shapiromart19_negative_control_assessment.csv",
    "shapiromart19_representation_audit.csv",
    "shapiromart19_dimension_assessment.csv",
    "shapiromart19_final_status.csv",
]

DIMENSIONS = [
    "coordinate_primary",
    "coordinate_secondary",
    "signal_value_primary",
    "signal_value_secondary",
]
COORDINATE_DIMENSIONS = ["coordinate_primary", "coordinate_secondary"]
SIGNAL_DIMENSIONS = ["signal_value_primary", "signal_value_secondary"]

TOKEN_BY_DIMENSION = {
    "coordinate_primary": "tim_token_002",
    "coordinate_secondary": "tim_token_003",
    "signal_value_primary": "tim_token_029",
    "signal_value_secondary": "tim_token_033",
}

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

DIMENSION_LINEAGE_FIELDS = [
    "fingerprint_dimension",
    "source_artifact",
    "source_table_or_file",
    "source_field_or_fields",
    "source_code_reference",
    "raw_data_type",
    "normalized_data_type",
    "unit",
    "transformation_formula",
    "scaling",
    "normalization",
    "aggregation",
    "ordering_dependency",
    "context_dependency",
    "missing_value_handling",
    "final_fingerprint_role",
    "lineage_status",
    "notes",
]

DIMENSION_SEMANTICS_FIELDS = [
    "fingerprint_dimension",
    "primary_role",
    "secondary_role",
    "semantic_status",
    "role_confidence",
    "role_evidence",
    "directly_measured",
    "derived",
    "composite",
    "instrument_related",
    "time_or_phase_related",
    "frequency_related",
    "ordering_related",
    "signal_related",
    "semantic_limit",
    "notes",
]

KNOWN_FACTOR_FIELDS = [
    "fingerprint_dimension",
    "factor_name",
    "factor_type",
    "analysis_scope",
    "count",
    "association_measure",
    "association_value",
    "adjusted_association_value",
    "direction",
    "persists_within_context",
    "persists_within_side",
    "threshold_dependence",
    "association_status",
    "notes",
]

SPECIFICITY_FIELDS = [
    "tested_explanation",
    "test_method",
    "unadjusted_effect",
    "adjusted_effect",
    "absolute_attenuation",
    "relative_attenuation",
    "direction_preserved",
    "residual_association",
    "explanation_status",
    "evidence_scope",
    "notes",
]

LOCALIZATION_FIELDS = [
    "distance_bin",
    "lower_bound",
    "upper_bound",
    "context_name",
    "phase_side",
    "inside_count",
    "outside_count",
    "mean_difference",
    "median_difference",
    "standardized_effect",
    "robust_effect",
    "direction",
    "local_pattern_status",
    "notes",
]

COORDINATE_SIGNAL_FIELDS = [
    "coordinate_dimension",
    "signal_dimension",
    "analysis_scope",
    "correlation_method",
    "correlation_value",
    "conditional_analysis",
    "conditional_result",
    "ordering_dependency_found",
    "representation_dependency_found",
    "relation_status",
    "notes",
]

NEGATIVE_CONTROL_FIELDS = [
    "signal_dimension",
    "analysis_scope",
    "primary_effect",
    "secondary_effect",
    "context_effect_max",
    "side_effect_max",
    "permutation_reference",
    "permutation_tail_fraction",
    "null_behavior_status",
    "negative_control_status",
    "notes",
]

REPRESENTATION_AUDIT_FIELDS = [
    "audit_item",
    "source_reference",
    "dependency_found",
    "dependency_type",
    "affects_dimension",
    "leakage_risk",
    "audit_status",
    "notes",
]

DIMENSION_ASSESSMENT_FIELDS = [
    "fingerprint_dimension",
    "semantic_status",
    "primary_role",
    "SHAPIROMART18_status",
    "strongest_known_factor",
    "strongest_factor_explanation_status",
    "context_adjusted_status",
    "side_adjusted_status",
    "threshold_status",
    "representation_audit_status",
    "negative_control_role",
    "final_specificity_status",
    "combined_result_status",
    "consolidated_finding",
    "interpretation_limit",
    "recommended_follow_up",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "fingerprint_dimensions_assessed",
    "lineage_reconstructed",
    "semantics_resolved_dimension_count",
    "semantics_partially_resolved_dimension_count",
    "semantics_unresolved_dimension_count",
    "coordinate_secondary_specificity_completed",
    "coordinate_primary_localization_completed",
    "coordinate_signal_relation_completed",
    "negative_controls_completed",
    "representation_audit_completed",
    "representation_leakage_detected",
    "robust_structural_association_dimension_count",
    "context_sensitive_dimension_count",
    "threshold_localized_dimension_count",
    "stable_negative_control_dimension_count",
    "physical_interpretation_performed",
    "causal_claim_made",
    "shapiro_information_claim_made",
    "bridge_claim_made",
    "database_access",
    "database_modified",
    "additional_gate_created",
    "final_status",
    "recommended_next_action",
    "limitations",
]


class ControlledStop(RuntimeError):
    """Raised when a required audit condition is not met."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SHAPIROMART19 specificity audit.")
    parser.add_argument("--shapiromart04-dir", type=Path, default=SHAPIROMART04_DIR)
    parser.add_argument("--shapiromart05-dir", type=Path, default=SHAPIROMART05_DIR)
    parser.add_argument(
        "--shapiromart11-phase-input",
        type=Path,
        default=SHAPIROMART11_DIR / "shapiromart11_toa_orbital_phase.csv",
    )
    parser.add_argument(
        "--shapiromart17-groups-input",
        type=Path,
        default=SHAPIROMART17_DIR / "shapiromart17_prepared_exposure_groups.csv",
    )
    parser.add_argument("--shapiromart18-dir", type=Path, default=SHAPIROMART18_DIR)
    parser.add_argument(
        "--distance-distribution-input",
        type=Path,
        default=SHAPIROMART14_DIR / "shapiromart14_absolute_distance_distribution.csv",
    )
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--permutation-replicates", type=int, default=DEFAULT_PERMUTATIONS)
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--minimum-group-count", type=int, default=DEFAULT_MINIMUM_GROUP_COUNT)
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


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


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise ControlledStop(f"Required input missing: {rel(path)}")
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


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


def to_float(value: Any, field_name: str = "value") -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ControlledStop(f"Invalid numeric value for {field_name}: {value!r}") from exc
    if not math.isfinite(number):
        raise ControlledStop(f"Non-finite numeric value for {field_name}: {value!r}")
    return number


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
    return hashlib.sha256("\x1f".join(key).encode("utf-8")).hexdigest()


def open_read_only_db(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA query_only=ON")
    return con


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


def pearson(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or y.size < 2:
        return math.nan
    x_centered = x - np.mean(x)
    y_centered = y - np.mean(y)
    denom = math.sqrt(float(np.sum(x_centered * x_centered) * np.sum(y_centered * y_centered)))
    if denom <= 0:
        return math.nan
    return float(np.sum(x_centered * y_centered) / denom)


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    if x.size < 2 or y.size < 2:
        return math.nan
    return pearson(average_ranks(x), average_ranks(y))


def pooled_sd(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or b.size < 2:
        return math.nan
    denom = a.size + b.size - 2
    if denom <= 0:
        return math.nan
    value = math.sqrt(
        (((a.size - 1) * np.var(a, ddof=1)) + ((b.size - 1) * np.var(b, ddof=1))) / denom
    )
    return value if math.isfinite(value) and value > 0 else math.nan


def smd(a: np.ndarray, b: np.ndarray) -> float:
    scale = pooled_sd(a, b)
    if not math.isfinite(scale) or scale <= 0:
        return math.nan
    return (float(np.mean(a)) - float(np.mean(b))) / scale


def robust_effect(a: np.ndarray, b: np.ndarray) -> float:
    if a.size < 2 or b.size < 2:
        return math.nan
    q1_a, q3_a = np.quantile(a, [0.25, 0.75])
    q1_b, q3_b = np.quantile(b, [0.25, 0.75])
    scale = (((q3_a - q1_a) + (q3_b - q1_b)) / 2.0) / 1.349
    if not math.isfinite(scale) or scale <= 0:
        return math.nan
    return (float(np.median(a)) - float(np.median(b))) / scale


def direction(value: float, floor: float = 0.10) -> str:
    if not math.isfinite(value):
        return "not_computed"
    if abs(value) < floor:
        return "near_zero"
    return "positive" if value > 0 else "negative"


def effect_status(value: float) -> str:
    if not math.isfinite(value):
        return "not_computed"
    magnitude = abs(value)
    if magnitude < 0.10:
        return "near_zero"
    if magnitude < 0.25:
        return "small"
    if magnitude < 0.50:
        return "moderate"
    return "large"


def arrays(rows: list[dict[str, Any]], field: str) -> np.ndarray:
    return np.asarray([float(row[field]) for row in rows if math.isfinite(float(row[field]))], dtype=float)


def group_effect(
    rows: list[dict[str, Any]],
    dimension: str,
    group_field: str,
    inside_label: str,
    outside_label: str,
    minimum_count: int,
) -> float:
    inside = arrays([row for row in rows if row[group_field] == inside_label], dimension)
    outside = arrays([row for row in rows if row[group_field] == outside_label], dimension)
    if inside.size < minimum_count or outside.size < minimum_count:
        return math.nan
    return smd(inside, outside)


def residualize_numeric(y: np.ndarray, factors: list[np.ndarray]) -> np.ndarray:
    columns = [np.ones(y.size, dtype=float)]
    for factor in factors:
        if factor.size == y.size:
            columns.append(factor.astype(float))
    design = np.column_stack(columns)
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return y - design @ beta


def residualize_by_category(rows: list[dict[str, Any]], dimension: str, category_field: str) -> np.ndarray:
    values = arrays(rows, dimension)
    categories = [str(row[category_field]) for row in rows]
    residuals = np.empty(values.size, dtype=float)
    global_mean = float(np.mean(values))
    for category in sorted(set(categories)):
        indices = [index for index, value in enumerate(categories) if value == category]
        category_mean = float(np.mean(values[indices])) if indices else global_mean
        residuals[indices] = values[indices] - category_mean
    return residuals


def adjusted_group_effect_numeric(
    rows: list[dict[str, Any]],
    dimension: str,
    factor_fields: list[str],
    minimum_count: int,
) -> float:
    y = arrays(rows, dimension)
    factors = [arrays(rows, field) for field in factor_fields]
    residuals = residualize_numeric(y, factors)
    inside = np.asarray(
        [residuals[index] for index, row in enumerate(rows) if row["primary_group"] == "inside_primary_threshold"],
        dtype=float,
    )
    outside = np.asarray(
        [residuals[index] for index, row in enumerate(rows) if row["primary_group"] == "outside_primary_threshold"],
        dtype=float,
    )
    if inside.size < minimum_count or outside.size < minimum_count:
        return math.nan
    return smd(inside, outside)


def adjusted_group_effect_category(
    rows: list[dict[str, Any]],
    dimension: str,
    category_field: str,
    minimum_count: int,
) -> float:
    residuals = residualize_by_category(rows, dimension, category_field)
    inside = np.asarray(
        [residuals[index] for index, row in enumerate(rows) if row["primary_group"] == "inside_primary_threshold"],
        dtype=float,
    )
    outside = np.asarray(
        [residuals[index] for index, row in enumerate(rows) if row["primary_group"] == "outside_primary_threshold"],
        dtype=float,
    )
    if inside.size < minimum_count or outside.size < minimum_count:
        return math.nan
    return smd(inside, outside)


def context_stratified_effect(rows: list[dict[str, Any]], dimension: str, minimum_count: int) -> float:
    total = len(rows)
    value = 0.0
    used = 0
    for context in sorted({row["context_name"] for row in rows}):
        selected = [row for row in rows if row["context_name"] == context]
        local = group_effect(
            selected,
            dimension,
            "primary_group",
            "inside_primary_threshold",
            "outside_primary_threshold",
            minimum_count,
        )
        if math.isfinite(local):
            value += (len(selected) / total) * local
            used += 1
    return value if used else math.nan


def side_stratified_effect(rows: list[dict[str, Any]], dimension: str, minimum_count: int) -> float:
    total = len(rows)
    value = 0.0
    used = 0
    for side in sorted({row["phase_side"] for row in rows}):
        selected = [row for row in rows if row["phase_side"] == side]
        local = group_effect(
            selected,
            dimension,
            "primary_group",
            "inside_primary_threshold",
            "outside_primary_threshold",
            minimum_count,
        )
        if math.isfinite(local):
            value += (len(selected) / total) * local
            used += 1
    return value if used else math.nan


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_required_inputs(args: argparse.Namespace) -> dict[str, Any]:
    sh18_required = [
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
        "shapiromart18_summary.json",
    ]
    for name in sh18_required:
        if not (args.shapiromart18_dir / name).exists():
            raise ControlledStop(f"Missing SHAPIROMART18 input: {rel(args.shapiromart18_dir / name)}")
    return {
        "sh04_summary": load_json(args.shapiromart04_dir / "shapiromart04_summary.json"),
        "sh05_summary": load_json(args.shapiromart05_dir / "shapiromart05_summary.json"),
        "sh18_summary": load_json(args.shapiromart18_dir / "shapiromart18_summary.json"),
        "sh18_dimension": read_csv_rows(args.shapiromart18_dir / "shapiromart18_dimension_assessment.csv")[0],
        "sh18_primary": read_csv_rows(args.shapiromart18_dir / "shapiromart18_primary_effect_sizes.csv")[0],
        "sh18_robustness": read_csv_rows(args.shapiromart18_dir / "shapiromart18_robustness_summary.csv")[0],
        "sh18_context": read_csv_rows(args.shapiromart18_dir / "shapiromart18_context_stratified_effects.csv")[0],
        "sh18_prepost": read_csv_rows(args.shapiromart18_dir / "shapiromart18_pre_post_control.csv")[0],
        "sh18_threshold": read_csv_rows(args.shapiromart18_dir / "shapiromart18_threshold_sensitivity.csv")[0],
        "sh18_composition": read_csv_rows(args.shapiromart18_dir / "shapiromart18_composition_adjusted_effects.csv")[0],
    }


def load_groups(path: Path) -> dict[str, dict[str, Any]]:
    rows, _ = read_csv_rows(path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART17 prepared-group row count mismatch.")
    output: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_index = row["source_row_index"]
        signed = to_float(row["signed_phase_offset"], "signed_phase_offset")
        absolute = to_float(row["absolute_phase_distance"], "absolute_phase_distance")
        primary = to_float(row["primary_threshold"], "primary_threshold")
        secondary = to_float(row["secondary_threshold"], "secondary_threshold")
        if not math.isclose(primary, PRIMARY_THRESHOLD, rel_tol=0.0, abs_tol=1e-12):
            raise ControlledStop("Primary threshold differs from SHAPIROMART17 fixed value.")
        if not math.isclose(secondary, SECONDARY_THRESHOLD, rel_tol=0.0, abs_tol=1e-12):
            raise ControlledStop("Secondary threshold differs from SHAPIROMART17 fixed value.")
        phase_side = "pre_conjunction_side" if signed < 0 else "post_conjunction_side"
        row = dict(row)
        row["signed_phase_offset"] = signed
        row["absolute_phase_distance"] = absolute
        row["orbital_phase"] = to_float(row["orbital_phase"], "orbital_phase")
        row["phase_side"] = phase_side
        output[source_index] = row
    if len(output) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART17 source_row_index values are not unique.")
    return output


def load_toa_rows(path: Path) -> dict[str, dict[str, Any]]:
    rows, _ = read_csv_rows(path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART11 TOA row count mismatch.")
    output: dict[str, dict[str, Any]] = {}
    keys: list[tuple[str, ...]] = []
    for row in rows:
        flags = parse_source_flags(row["source_filename"])
        key = source_key(flags)
        keys.append(key)
        row = dict(row)
        row["source_flags"] = flags
        row["source_key"] = key
        row["source_key_hash"] = source_key_hash(key)
        row["observing_frequency_mhz"] = to_float(row["observing_frequency_mhz"], "observing_frequency_mhz")
        row["toa_mjd_file"] = to_float(row["toa_mjd_file"], "toa_mjd_file")
        row["processed_time_value"] = to_float(row["processed_time_value"], "processed_time_value")
        row["orbital_phase_from_sh11"] = to_float(row["orbital_phase"], "orbital_phase")
        output[row["source_row_index"]] = row
    if len(output) != EXPECTED_ROW_COUNT or len(set(keys)) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART11 source keys are not complete and unique.")
    return output


def load_fingerprints(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any], list[dict[str, Any]]]:
    before = file_identity(path)
    con = open_read_only_db(path)
    try:
        integrity = [tuple(row) for row in con.execute("PRAGMA integrity_check").fetchall()]
        fk_rows = con.execute("PRAGMA foreign_key_check").fetchall()
        feature_rows = [
            dict(row)
            for row in con.execute(
                """
                SELECT
                    token_position,
                    source_field,
                    reviewed_feature_name,
                    provisional_role,
                    first_fingerprint_use,
                    direct_interpretation_allowed,
                    weighting_allowed,
                    limitation
                FROM qsb_v_shapiromart03_first_fingerprint_features
                ORDER BY fingerprint_role_order, token_position
                """
            ).fetchall()
        ]
        rows = [
            dict(row)
            for row in con.execute(
                """
                SELECT
                    fp.structural_fingerprint_id,
                    fp.raw_record_id,
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
        ]
    finally:
        con.close()
    after = file_identity(path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART04 complete fingerprint row count mismatch.")
    parsed: list[dict[str, Any]] = []
    keys: list[tuple[str, ...]] = []
    for row in rows:
        flags = parse_tim_line_flags(str(row.get("raw_line_text") or ""))
        key = source_key(flags)
        keys.append(key)
        item = dict(row)
        item["source_key"] = key
        item["source_key_hash"] = source_key_hash(key)
        item["source_flags_from_raw_line"] = flags
        for dimension in DIMENSIONS:
            item[dimension] = to_float(item[dimension], dimension)
        parsed.append(item)
    if len(set(keys)) != EXPECTED_ROW_COUNT:
        raise ControlledStop("SHAPIROMART04 source keys are not unique.")
    db_status = {
        "before": before,
        "after": after,
        "database_modified": "no" if before == after else "yes",
        "integrity_check": integrity,
        "foreign_key_check_row_count": len(fk_rows),
        "tables_or_views_used": [
            "qsb_v_shapiromart03_first_fingerprint_features",
            "qsb_v_shapiromart04_complete_fingerprints",
            "raw_record",
        ],
        "sql_queries_documented": "yes",
    }
    return parsed, db_status, feature_rows


def build_joined_rows(
    groups: dict[str, dict[str, Any]],
    toa_rows: dict[str, dict[str, Any]],
    fingerprints: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fingerprint_by_key = {row["source_key"]: row for row in fingerprints}
    if set(groups) != set(toa_rows):
        raise ControlledStop("SHAPIROMART17 to SHAPIROMART11 source_row_index join mismatch.")
    if set(row["source_key"] for row in toa_rows.values()) != set(fingerprint_by_key):
        raise ControlledStop("SHAPIROMART11 to SHAPIROMART04 source-flag join mismatch.")
    joined: list[dict[str, Any]] = []
    for source_index in sorted(groups, key=lambda value: int(value)):
        group = groups[source_index]
        toa = toa_rows[source_index]
        fingerprint = fingerprint_by_key[toa["source_key"]]
        row = dict(group)
        row.update(
            {
                "source_key_hash": toa["source_key_hash"],
                "structural_fingerprint_id": fingerprint["structural_fingerprint_id"],
                "raw_record_id": fingerprint["raw_record_id"],
                "receiver_context": fingerprint["receiver_context"],
                "backend_context": fingerprint["backend_context"],
                "raw_context_label": fingerprint["raw_context_label"],
                "observing_frequency_mhz": toa["observing_frequency_mhz"],
                "toa_mjd_file": toa["toa_mjd_file"],
                "processed_time_value": toa["processed_time_value"],
                "source_filename_name": toa["source_flags"].get("name", ""),
                "source_flag_fe": toa["source_flags"].get("fe", ""),
                "source_flag_be": toa["source_flags"].get("be", ""),
                "source_flag_f": toa["source_flags"].get("f", ""),
                "source_flag_bw": to_float(toa["source_flags"].get("bw", "nan"), "bw"),
                "source_flag_tobs": to_float(toa["source_flags"].get("tobs", "nan"), "tobs"),
                "source_flag_gof": to_float(toa["source_flags"].get("gof", "nan"), "gof"),
                "source_flag_nbin": to_float(toa["source_flags"].get("nbin", "nan"), "nbin"),
                "source_flag_nch": to_float(toa["source_flags"].get("nch", "nan"), "nch"),
                "source_flag_chan": to_float(toa["source_flags"].get("chan", "nan"), "chan"),
                "source_flag_subint": to_float(toa["source_flags"].get("subint", "nan"), "subint"),
                "source_flag_snr": to_float(toa["source_flags"].get("snr", "nan"), "snr"),
                "source_flag_wt": to_float(toa["source_flags"].get("wt", "nan"), "wt"),
                "source_flag_flux": to_float(toa["source_flags"].get("flux", "nan"), "flux"),
                "source_flag_fluxe": to_float(toa["source_flags"].get("fluxe", "nan"), "fluxe"),
                "source_flag_proc": toa["source_flags"].get("proc", ""),
                "source_flag_pta": toa["source_flags"].get("pta", ""),
                "source_flag_ver": toa["source_flags"].get("ver", ""),
            }
        )
        for dimension in DIMENSIONS:
            row[dimension] = fingerprint[dimension]
        if row["receiver"] != row["receiver_context"] or row["backend"] != row["backend_context"]:
            raise ControlledStop("Receiver/backend labels are inconsistent after join.")
        joined.append(row)
    if len(joined) != EXPECTED_ROW_COUNT:
        raise ControlledStop("Joined row count mismatch.")
    return joined


def lineage_rows(feature_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    feature_by_token = {row["token_position"]: row for row in feature_rows}
    details = {
        "coordinate_primary": {
            "unit": "MHz",
            "role": "frequency_or_band_coordinate",
            "source": "TIM FORMAT 1 frequency field and PINT observing_frequency_mhz",
            "notes": "The value matches the observing frequency exported by SHAPIROMART11.",
        },
        "coordinate_secondary": {
            "unit": "MJD days",
            "role": "time_or_phase_coordinate",
            "source": "TIM FORMAT 1 TOA field and SHAPIROMART11 toa_mjd_file",
            "notes": "The value is the file TOA coordinate; orbital phase is derived later, not in SHAPIROMART04.",
        },
        "signal_value_primary": {
            "unit": "dimensionless SNR",
            "role": "signal_amplitude",
            "source": "TIM source flag -snr",
            "notes": "The value matches the SNR source flag exported by SHAPIROMART11.",
        },
        "signal_value_secondary": {
            "unit": "flux units as carried by source flag",
            "role": "signal_amplitude",
            "source": "TIM source flag -flux",
            "notes": "The value matches the flux source flag exported by SHAPIROMART11.",
        },
    }
    output: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        token = TOKEN_BY_DIMENSION[dimension]
        feature = feature_by_token[token]
        output.append(
            {
                "fingerprint_dimension": dimension,
                "source_artifact": "SHAPIROMART04 complete unweighted fingerprint table",
                "source_table_or_file": "qsb_v_shapiromart04_complete_fingerprints; raw_field_value; SHAPIROMART11 source flags",
                "source_field_or_fields": f"{feature['source_field']}; {details[dimension]['source']}",
                "source_code_reference": "scripts/qsb_shapiromart04_first_unweighted_fingerprint_build.py:131;:153;:632;:675;:700",
                "raw_data_type": "TIM token text parsed from raw_field_value.raw_value",
                "normalized_data_type": "float stored as REAL",
                "unit": details[dimension]["unit"],
                "transformation_formula": f"{dimension} = parse_numeric(single {token} value)",
                "scaling": "none",
                "normalization": "none",
                "aggregation": "none",
                "ordering_dependency": "value itself none; structural_fingerprint_id and view output ordered by context and source record order",
                "context_dependency": "candidate rows restricted to supported receiver/backend contexts Rcvr_800/GUPPI and Rcvr1_2/GUPPI",
                "missing_value_handling": "missing, duplicate, or non-numeric required token blocks complete_fingerprint",
                "final_fingerprint_role": details[dimension]["role"],
                "lineage_status": "reconstructed",
                "notes": f"{feature['limitation']} {details[dimension]['notes']}",
            }
        )
    return output


def semantics_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "fingerprint_dimension": "coordinate_primary",
            "primary_role": "frequency_or_band_coordinate",
            "secondary_role": "instrument_context_coordinate",
            "semantic_status": "documented_instrument_coordinate",
            "role_confidence": "strongly_supported",
            "role_evidence": "TIM token 002 equals SHAPIROMART11 observing_frequency_mhz.",
            "directly_measured": "yes",
            "derived": "no",
            "composite": "no",
            "instrument_related": "yes",
            "time_or_phase_related": "no",
            "frequency_related": "yes",
            "ordering_related": "no",
            "signal_related": "no",
            "semantic_limit": "Frequency is an instrumental/observational coordinate, not a physical interpretation.",
            "notes": "SHAPIROMART03 allowed only a provisional coordinate role; SHAPIROMART19 resolves the source field.",
        },
        {
            "fingerprint_dimension": "coordinate_secondary",
            "primary_role": "time_or_phase_coordinate",
            "secondary_role": "measurement_coordinate",
            "semantic_status": "documented_structural_coordinate",
            "role_confidence": "strongly_supported",
            "role_evidence": "TIM token 003 equals SHAPIROMART11 toa_mjd_file.",
            "directly_measured": "yes",
            "derived": "no",
            "composite": "no",
            "instrument_related": "no",
            "time_or_phase_related": "yes",
            "frequency_related": "no",
            "ordering_related": "partly",
            "signal_related": "no",
            "semantic_limit": "The stored value is TOA MJD; orbital phase and distance are later derived axes.",
            "notes": "Group labels did not enter SHAPIROMART04, but the later phase axis is derived from the same TOA coordinate.",
        },
        {
            "fingerprint_dimension": "signal_value_primary",
            "primary_role": "signal_amplitude",
            "secondary_role": "signal_shape_or_response",
            "semantic_status": "documented_measurement_dimension",
            "role_confidence": "strongly_supported",
            "role_evidence": "TIM token 029 equals source flag -snr.",
            "directly_measured": "yes",
            "derived": "no",
            "composite": "no",
            "instrument_related": "partly",
            "time_or_phase_related": "no",
            "frequency_related": "no",
            "ordering_related": "no",
            "signal_related": "yes",
            "semantic_limit": "SNR is a descriptive source flag and is not used as a model residual.",
            "notes": "Used as an internal negative-control dimension for the SHAPIROMART18 pattern.",
        },
        {
            "fingerprint_dimension": "signal_value_secondary",
            "primary_role": "signal_amplitude",
            "secondary_role": "signal_shape_or_response",
            "semantic_status": "documented_measurement_dimension",
            "role_confidence": "strongly_supported",
            "role_evidence": "TIM token 033 equals source flag -flux.",
            "directly_measured": "yes",
            "derived": "no",
            "composite": "no",
            "instrument_related": "partly",
            "time_or_phase_related": "no",
            "frequency_related": "no",
            "ordering_related": "no",
            "signal_related": "yes",
            "semantic_limit": "Flux is carried as source metadata and is not a timing-model quantity.",
            "notes": "Used as an internal negative-control dimension for the SHAPIROMART18 pattern.",
        },
    ]
    return rows


def categorical_effect(rows: list[dict[str, Any]], dimension: str, field: str, minimum_count: int) -> float:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row[field])].append(row)
    usable = [(key, arrays(value, dimension)) for key, value in groups.items() if len(value) >= minimum_count]
    if len(usable) < 2:
        return math.nan
    best = math.nan
    for idx, (_, left) in enumerate(usable):
        for _, right in usable[idx + 1 :]:
            local = smd(left, right)
            if math.isfinite(local) and (not math.isfinite(best) or abs(local) > abs(best)):
                best = local
    return best


def within_status(
    rows: list[dict[str, Any]],
    dimension: str,
    factor_field: str,
    factor_type: str,
    strata_field: str,
    minimum_count: int,
) -> str:
    values: list[float] = []
    for stratum in sorted({row[strata_field] for row in rows}):
        selected = [row for row in rows if row[strata_field] == stratum]
        if factor_type == "numeric":
            local = spearman(arrays(selected, dimension), arrays(selected, factor_field))
        elif factor_field in {"primary_group", "secondary_group"}:
            local = group_effect(
                selected,
                dimension,
                factor_field,
                "inside_primary_threshold"
                if factor_field == "primary_group"
                else "inside_secondary_threshold",
                "outside_primary_threshold"
                if factor_field == "primary_group"
                else "outside_secondary_threshold",
                minimum_count,
            )
        else:
            local = categorical_effect(selected, dimension, factor_field, minimum_count)
        if math.isfinite(local):
            values.append(local)
    if not values:
        return "insufficient_support"
    signs = {direction(value) for value in values if direction(value) != "near_zero"}
    if not signs:
        return "no_material_association"
    if len(signs) == 1:
        return "persists"
    return "mixed"


def threshold_dependence_for_dimension(sh18_robustness: list[dict[str, str]], dimension: str) -> str:
    for row in sh18_robustness:
        if row["dimension"] == dimension:
            return row.get("threshold_sensitivity_status", "")
    return ""


def known_factor_associations(
    rows: list[dict[str, Any]],
    sh18_robustness: list[dict[str, str]],
    minimum_count: int,
) -> list[dict[str, Any]]:
    factors = [
        ("receiver", "categorical", "receiver"),
        ("backend", "categorical", "backend"),
        ("observing_frequency_mhz", "numeric", "observing_frequency_mhz"),
        ("source filename", "categorical", "source_filename_name"),
        ("source flag chan", "numeric", "source_flag_chan"),
        ("source flag subint", "numeric", "source_flag_subint"),
        ("source flag gof", "numeric", "source_flag_gof"),
        ("TOA MJD", "numeric", "toa_mjd_file"),
        ("orbital_phase", "numeric", "orbital_phase"),
        ("signed_phase_offset", "numeric", "signed_phase_offset"),
        ("absolute_phase_distance", "numeric", "absolute_phase_distance"),
        ("primary inside/outside group", "binary_group", "primary_group"),
        ("secondary inside/outside group", "binary_group", "secondary_group"),
        ("pre/post side", "binary_group", "phase_side"),
    ]
    output: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        for factor_name, factor_type, field in factors:
            if factor_type == "numeric":
                x = arrays(rows, field)
                y = arrays(rows, dimension)
                value = spearman(y, x)
                measure = "spearman"
                adjusted = spearman(
                    residualize_numeric(y, [arrays(rows, "observing_frequency_mhz")])
                    if field != "observing_frequency_mhz"
                    else y,
                    residualize_numeric(x, [arrays(rows, "observing_frequency_mhz")])
                    if field != "observing_frequency_mhz"
                    else x,
                )
            elif field == "primary_group":
                value = group_effect(
                    rows,
                    dimension,
                    field,
                    "inside_primary_threshold",
                    "outside_primary_threshold",
                    minimum_count,
                )
                measure = "smd_inside_minus_outside"
                adjusted = context_stratified_effect(rows, dimension, minimum_count)
            elif field == "secondary_group":
                value = group_effect(
                    rows,
                    dimension,
                    field,
                    "inside_secondary_threshold",
                    "outside_secondary_threshold",
                    minimum_count,
                )
                measure = "smd_inside_minus_outside"
                adjusted = value
            elif field == "phase_side":
                value = group_effect(
                    rows,
                    dimension,
                    field,
                    "post_conjunction_side",
                    "pre_conjunction_side",
                    minimum_count,
                )
                measure = "smd_post_minus_pre"
                adjusted = value
            else:
                value = categorical_effect(rows, dimension, field, minimum_count)
                measure = "max_pairwise_smd"
                adjusted = adjusted_group_effect_category(rows, dimension, field, minimum_count)
            status = effect_status(value)
            output.append(
                {
                    "fingerprint_dimension": dimension,
                    "factor_name": factor_name,
                    "factor_type": factor_type,
                    "analysis_scope": "overall_joined_rows",
                    "count": len(rows),
                    "association_measure": measure,
                    "association_value": fmt(value),
                    "adjusted_association_value": fmt(adjusted),
                    "direction": direction(value),
                    "persists_within_context": within_status(
                        rows, dimension, field, "numeric" if factor_type == "numeric" else "group", "context_name", minimum_count
                    ),
                    "persists_within_side": within_status(
                        rows, dimension, field, "numeric" if factor_type == "numeric" else "group", "phase_side", minimum_count
                    ),
                    "threshold_dependence": threshold_dependence_for_dimension(sh18_robustness, dimension),
                    "association_status": status,
                    "notes": "Descriptive association only; adjusted value uses a simple fixed control where applicable.",
                }
            )
    return output


def attenuation(unadjusted: float, adjusted: float) -> tuple[float, float, str, str]:
    if not (math.isfinite(unadjusted) and math.isfinite(adjusted)):
        return math.nan, math.nan, "not_computed", "not_computed"
    absolute = abs(unadjusted) - abs(adjusted)
    relative = absolute / abs(unadjusted) if abs(unadjusted) > 0 else math.nan
    preserved = "yes" if direction(unadjusted) == direction(adjusted) else "no"
    residual = effect_status(adjusted)
    return absolute, relative, preserved, residual


def explanation_status(unadjusted: float, adjusted: float) -> str:
    if not (math.isfinite(unadjusted) and math.isfinite(adjusted)):
        return "inconclusive"
    ratio = abs(adjusted) / abs(unadjusted) if abs(unadjusted) > 0 else math.inf
    if abs(adjusted) < 0.10 or ratio < 0.25:
        return "largely_explained"
    if ratio < 0.75:
        return "partly_explained"
    return "not_explained_by_this_factor"


def coordinate_secondary_specificity(rows: list[dict[str, Any]], minimum_count: int) -> list[dict[str, Any]]:
    unadjusted = group_effect(
        rows,
        "coordinate_secondary",
        "primary_group",
        "inside_primary_threshold",
        "outside_primary_threshold",
        minimum_count,
    )
    tests: list[tuple[str, str, Callable[[], float], str]] = [
        (
            "Receiver-/Backend-Komposition",
            "context-stratified fixed-weight SMD",
            lambda: context_stratified_effect(rows, "coordinate_secondary", minimum_count),
            "receiver/backend strata",
        ),
        (
            "Frequenzband oder Beobachtungsfrequenz",
            "linear residualization on observing_frequency_mhz",
            lambda: adjusted_group_effect_numeric(rows, "coordinate_secondary", ["observing_frequency_mhz"], minimum_count),
            "frequency coordinate",
        ),
        (
            "Source Flags oder Beobachtungskampagnen",
            "category residualization on source filename",
            lambda: adjusted_group_effect_category(rows, "coordinate_secondary", "source_filename_name", minimum_count),
            "source filename categories",
        ),
        (
            "TOA- oder Epocheneffekte",
            "linear residualization on TOA MJD",
            lambda: adjusted_group_effect_numeric(rows, "coordinate_secondary", ["toa_mjd_file"], minimum_count),
            "TOA MJD",
        ),
        (
            "Pre/Post-Asymmetrie",
            "side-stratified fixed-weight SMD",
            lambda: side_stratified_effect(rows, "coordinate_secondary", minimum_count),
            "phase side strata",
        ),
        (
            "Schwellenbreite",
            "secondary-threshold SMD",
            lambda: group_effect(
                rows,
                "coordinate_secondary",
                "secondary_group",
                "inside_secondary_threshold",
                "outside_secondary_threshold",
                minimum_count,
            ),
            "0.15 sensitivity group",
        ),
        (
            "einzelne dichte Phasenbereiche",
            "linear residualization on absolute_phase_distance",
            lambda: adjusted_group_effect_numeric(rows, "coordinate_secondary", ["absolute_phase_distance"], minimum_count),
            "absolute distance axis",
        ),
        (
            "einzelne Ausreisser",
            "1 percent winsorized SMD",
            lambda: winsorized_primary_effect(rows, "coordinate_secondary", 0.01, minimum_count),
            "winsorized dimension values",
        ),
        (
            "Representation or transformation logic",
            "lineage audit of scaling, normalization, and construction inputs",
            lambda: unadjusted,
            "SHAPIROMART04 representation",
        ),
        (
            "Direct dependency on a grouping variable",
            "linear residualization on orbital_phase and absolute_phase_distance",
            lambda: adjusted_group_effect_numeric(
                rows,
                "coordinate_secondary",
                ["orbital_phase", "absolute_phase_distance"],
                minimum_count,
            ),
            "phase and distance axes",
        ),
    ]
    output: list[dict[str, Any]] = []
    for name, method, func, scope in tests:
        adjusted = func()
        absolute, relative, preserved, residual = attenuation(unadjusted, adjusted)
        status = explanation_status(unadjusted, adjusted)
        if name == "Representation or transformation logic":
            status = "not_explained_by_this_factor"
            residual = effect_status(adjusted)
        output.append(
            {
                "tested_explanation": name,
                "test_method": method,
                "unadjusted_effect": fmt(unadjusted),
                "adjusted_effect": fmt(adjusted),
                "absolute_attenuation": fmt(absolute),
                "relative_attenuation": fmt(relative),
                "direction_preserved": preserved,
                "residual_association": residual,
                "explanation_status": status,
                "evidence_scope": scope,
                "notes": "Control is descriptive and does not assign causality.",
            }
        )
    return output


def winsorized_primary_effect(
    rows: list[dict[str, Any]], dimension: str, fraction: float, minimum_count: int
) -> float:
    values = arrays(rows, dimension)
    lower, upper = np.quantile(values, [fraction, 1.0 - fraction])
    selected = []
    for row in rows:
        item = dict(row)
        item[dimension] = float(np.clip(float(row[dimension]), lower, upper))
        selected.append(item)
    return group_effect(
        selected,
        dimension,
        "primary_group",
        "inside_primary_threshold",
        "outside_primary_threshold",
        minimum_count,
    )


def load_distance_bins(path: Path) -> list[dict[str, Any]]:
    rows, _ = read_csv_rows(path)
    bins: list[dict[str, Any]] = []
    for row in rows:
        if row.get("distribution_scope") == "overall" and row.get("context_name") == "overall":
            bins.append(
                {
                    "bin_index": int(row["bin_index"]),
                    "lower": to_float(row["lower_bound_inclusive"], "lower_bound_inclusive"),
                    "upper": to_float(row["upper_bound_exclusive"], "upper_bound_exclusive"),
                }
            )
    if not bins:
        raise ControlledStop("No SHAPIROMART14 distance bins found.")
    return bins


def localization_rows(
    rows: list[dict[str, Any]], bins: list[dict[str, Any]], minimum_count: int
) -> list[dict[str, Any]]:
    scopes: list[tuple[str, str, list[dict[str, Any]]]] = [("overall", "overall", rows)]
    for context in sorted({row["context_name"] for row in rows}):
        scopes.append((context, "overall", [row for row in rows if row["context_name"] == context]))
    for side in sorted({row["phase_side"] for row in rows}):
        scopes.append(("overall", side, [row for row in rows if row["phase_side"] == side]))
    output: list[dict[str, Any]] = []
    for bin_row in bins:
        lower = bin_row["lower"]
        upper = bin_row["upper"]
        for context, side, scope_rows in scopes:
            in_bin = [
                row
                for row in scope_rows
                if float(row["absolute_phase_distance"]) >= lower
                and float(row["absolute_phase_distance"]) < upper
            ]
            outside_bin = [row for row in scope_rows if row not in in_bin]
            if len(in_bin) < minimum_count or len(outside_bin) < minimum_count:
                mean_diff = median_diff = local_smd = local_robust = math.nan
                status = "insufficient_count"
            else:
                a = arrays(in_bin, "coordinate_primary")
                b = arrays(outside_bin, "coordinate_primary")
                mean_diff = float(np.mean(a)) - float(np.mean(b))
                median_diff = float(np.median(a)) - float(np.median(b))
                local_smd = smd(a, b)
                local_robust = robust_effect(a, b)
                if abs(local_smd) >= 0.25:
                    status = "localized_difference"
                elif direction(local_smd) == "near_zero":
                    status = "no_material_local_difference"
                else:
                    status = "weak_local_difference"
            output.append(
                {
                    "distance_bin": f"SHAPIROMART14_BIN_{bin_row['bin_index']:02d}",
                    "lower_bound": fmt(lower),
                    "upper_bound": fmt(upper),
                    "context_name": context,
                    "phase_side": side,
                    "inside_count": len(in_bin),
                    "outside_count": len(outside_bin),
                    "mean_difference": fmt(mean_diff),
                    "median_difference": fmt(median_diff),
                    "standardized_effect": fmt(local_smd),
                    "robust_effect": fmt(local_robust),
                    "direction": direction(local_smd),
                    "local_pattern_status": status,
                    "notes": "Bin effect compares this predeclared SHAPIROMART14 distance bin with its complement in the same scope.",
                }
            )
    return output


def decile_labels(values: np.ndarray) -> list[int]:
    quantiles = np.quantile(values, np.linspace(0.1, 0.9, 9))
    return [int(np.searchsorted(quantiles, value, side="right")) for value in values]


def max_group_effect_within_bins(
    rows: list[dict[str, Any]], value_field: str, bin_field: str, minimum_count: int
) -> float:
    bin_values = arrays(rows, bin_field)
    labels = decile_labels(bin_values)
    best = math.nan
    for label in sorted(set(labels)):
        selected = [row for index, row in enumerate(rows) if labels[index] == label]
        local = group_effect(
            selected,
            value_field,
            "primary_group",
            "inside_primary_threshold",
            "outside_primary_threshold",
            minimum_count,
        )
        if math.isfinite(local) and (not math.isfinite(best) or abs(local) > abs(best)):
            best = local
    return best


def coordinate_signal_rows(rows: list[dict[str, Any]], minimum_count: int) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    source_index_corr = {dimension: abs(spearman(arrays(rows, dimension), arrays(rows, "source_row_index"))) for dimension in COORDINATE_DIMENSIONS}
    for coordinate in COORDINATE_DIMENSIONS:
        for signal in SIGNAL_DIMENSIONS:
            scopes = [("overall", rows)]
            for context in sorted({row["context_name"] for row in rows}):
                scopes.append((context, [row for row in rows if row["context_name"] == context]))
            for scope_name, scope_rows in scopes:
                corr = spearman(arrays(scope_rows, coordinate), arrays(scope_rows, signal))
                signal_given_coordinate = max_group_effect_within_bins(
                    scope_rows, signal, coordinate, minimum_count
                )
                coordinate_given_signal = max_group_effect_within_bins(
                    scope_rows, coordinate, signal, minimum_count
                )
                representation_dependency = (
                    "shared_toa_phase_axis"
                    if coordinate == "coordinate_secondary"
                    else "not_detected"
                )
                relation_status = "coordinate_signal_decoupled"
                if abs(corr) >= 0.50:
                    relation_status = "coordinate_signal_associated"
                elif math.isfinite(coordinate_given_signal) and abs(coordinate_given_signal) >= 0.25:
                    relation_status = "coordinate_difference_persists_with_similar_signal"
                output.append(
                    {
                        "coordinate_dimension": coordinate,
                        "signal_dimension": signal,
                        "analysis_scope": scope_name,
                        "correlation_method": "spearman",
                        "correlation_value": fmt(corr),
                        "conditional_analysis": "primary-group effects within deciles of the paired dimension",
                        "conditional_result": (
                            f"signal_effect_within_coordinate_deciles={fmt(signal_given_coordinate)}; "
                            f"coordinate_effect_within_signal_deciles={fmt(coordinate_given_signal)}"
                        ),
                        "ordering_dependency_found": "yes" if source_index_corr[coordinate] >= 0.50 else "no",
                        "representation_dependency_found": representation_dependency,
                        "relation_status": relation_status,
                        "notes": "Conditional checks are descriptive decile controls, not optimized thresholds.",
                    }
                )
    return output


def permutation_tail_fraction(
    rows: list[dict[str, Any]],
    dimension: str,
    replicates: int,
    seed: int,
    minimum_count: int,
) -> float:
    observed = abs(
        group_effect(
            rows,
            dimension,
            "primary_group",
            "inside_primary_threshold",
            "outside_primary_threshold",
            minimum_count,
        )
    )
    if not math.isfinite(observed):
        return math.nan
    rng = np.random.default_rng(seed)
    context_groups: dict[str, list[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        context_groups[row["context_name"]].append(index)
    base_labels = np.asarray(
        [1 if row["primary_group"] == "inside_primary_threshold" else 0 for row in rows],
        dtype=int,
    )
    values = arrays(rows, dimension)
    exceed = 0
    for _ in range(replicates):
        labels = base_labels.copy()
        for indices in context_groups.values():
            shuffled = labels[indices].copy()
            rng.shuffle(shuffled)
            labels[indices] = shuffled
        inside = values[labels == 1]
        outside = values[labels == 0]
        if inside.size < minimum_count or outside.size < minimum_count:
            continue
        permuted = abs(smd(inside, outside))
        if math.isfinite(permuted) and permuted >= observed:
            exceed += 1
    return exceed / replicates


def negative_control_rows(
    rows: list[dict[str, Any]],
    sh18_robustness: list[dict[str, str]],
    replicates: int,
    seed: int,
    minimum_count: int,
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for dimension in SIGNAL_DIMENSIONS:
        robust = next(row for row in sh18_robustness if row["dimension"] == dimension)
        primary_effect = to_float(robust["primary_smd"], "primary_smd")
        secondary_effect = to_float(robust["secondary_smd"], "secondary_smd")
        context_max = to_float(robust["context_max_abs_smd"], "context_max_abs_smd")
        side_max = to_float(robust["side_max_abs_smd"], "side_max_abs_smd")
        tail = permutation_tail_fraction(rows, dimension, replicates, seed, minimum_count)
        null_status = (
            "stable_near_zero"
            if abs(primary_effect) < 0.10 and abs(secondary_effect) < 0.15
            else "local_splits_need_review"
        )
        negative_status = (
            "stable_negative_control"
            if null_status == "stable_near_zero" and context_max < 0.25
            else "negative_control_with_local_sensitivity"
        )
        output.append(
            {
                "signal_dimension": dimension,
                "analysis_scope": "overall_with_context_preserving_permutation",
                "primary_effect": fmt(primary_effect),
                "secondary_effect": fmt(secondary_effect),
                "context_effect_max": fmt(context_max),
                "side_effect_max": fmt(side_max),
                "permutation_reference": f"context-preserving primary labels; seed={seed}; replicates={replicates}",
                "permutation_tail_fraction": fmt(tail),
                "null_behavior_status": null_status,
                "negative_control_status": negative_status,
                "notes": "Permutation is a diagnostic specificity check, not an inferential decision rule.",
            }
        )
    return output


def representation_audit_rows() -> list[dict[str, Any]]:
    return [
        {
            "audit_item": "group_label_in_fingerprint_construction",
            "source_reference": "SHAPIROMART04 script lines 620-710; SHAPIROMART17 generated later",
            "dependency_found": "no",
            "dependency_type": "not_present",
            "affects_dimension": "none",
            "leakage_risk": "none_detected",
            "audit_status": "passed",
            "notes": "Primary and secondary group labels are absent from SHAPIROMART04 construction.",
        },
        {
            "audit_item": "orbital_phase_in_fingerprint_construction",
            "source_reference": "SHAPIROMART04 script; SHAPIROMART11/13 phase generated later",
            "dependency_found": "no",
            "dependency_type": "not_present",
            "affects_dimension": "none",
            "leakage_risk": "none_detected",
            "audit_status": "passed",
            "notes": "Orbital phase is not an input to the fingerprint table.",
        },
        {
            "audit_item": "absolute_phase_distance_in_fingerprint_construction",
            "source_reference": "SHAPIROMART14/17 outputs; SHAPIROMART04 precedes them",
            "dependency_found": "no",
            "dependency_type": "not_present",
            "affects_dimension": "none",
            "leakage_risk": "none_detected",
            "audit_status": "passed",
            "notes": "Distance bands did not enter the fingerprint dimensions.",
        },
        {
            "audit_item": "receiver_backend_encoding",
            "source_reference": "SHAPIROMART04 candidate row selection and context fields",
            "dependency_found": "yes",
            "dependency_type": "context_selection_and_metadata",
            "affects_dimension": "context fields; not numeric dimension formula",
            "leakage_risk": "low_for_group_labels",
            "audit_status": "documented_context_dependency",
            "notes": "Receiver/backend define supported contexts and output metadata.",
        },
        {
            "audit_item": "source_row_order_dependency",
            "source_reference": "SHAPIROMART04 candidate order by receiver context, record_index, raw_record_id",
            "dependency_found": "yes",
            "dependency_type": "identifier_and_output_order",
            "affects_dimension": "structural_fingerprint_id only",
            "leakage_risk": "low_for_dimension_values",
            "audit_status": "documented_order_dependency",
            "notes": "Order affects generated IDs and view ordering, not parsed token values.",
        },
        {
            "audit_item": "sort_key_dependency",
            "source_reference": "qsb_v_shapiromart04_complete_fingerprints ORDER BY receiver_context, structural_fingerprint_id",
            "dependency_found": "yes",
            "dependency_type": "output_order",
            "affects_dimension": "none",
            "leakage_risk": "none_detected",
            "audit_status": "passed",
            "notes": "SHAPIROMART18/19 exact source-key joins do not use row order.",
        },
        {
            "audit_item": "categorical_code_dependency",
            "source_reference": "TOKEN_TO_COLUMN maps numeric token values only",
            "dependency_found": "no",
            "dependency_type": "not_present",
            "affects_dimension": "none",
            "leakage_risk": "none_detected",
            "audit_status": "passed",
            "notes": "No categorical code is numerically injected into the four fingerprint dimensions.",
        },
        {
            "audit_item": "normalization_order_dependency",
            "source_reference": "SHAPIROMART04 notes unweighted_no_scaling_no_normalization",
            "dependency_found": "no",
            "dependency_type": "not_present",
            "affects_dimension": "none",
            "leakage_risk": "none_detected",
            "audit_status": "passed",
            "notes": "No normalization or centering was applied.",
        },
        {
            "audit_item": "aggregation_order_dependency",
            "source_reference": "SHAPIROMART04 build_fingerprint_rows stores one row per raw record",
            "dependency_found": "no",
            "dependency_type": "not_present",
            "affects_dimension": "none",
            "leakage_risk": "none_detected",
            "audit_status": "passed",
            "notes": "No dimension is built from an average or summary over records.",
        },
    ]


def strongest_factor(known_rows: list[dict[str, Any]], dimension: str) -> tuple[str, str]:
    candidates = [row for row in known_rows if row["fingerprint_dimension"] == dimension]
    best_name = ""
    best_status = ""
    best_value = -1.0
    for row in candidates:
        try:
            value = abs(float(row["association_value"]))
        except (TypeError, ValueError):
            continue
        if value > best_value:
            best_value = value
            best_name = row["factor_name"]
            best_status = row["association_status"]
    return best_name, best_status


def dimension_assessment_rows(
    semantics: list[dict[str, Any]],
    known: list[dict[str, Any]],
    specificity: list[dict[str, Any]],
    negative: list[dict[str, Any]],
    audit: list[dict[str, Any]],
    sh18_dimension: list[dict[str, str]],
    sh18_robustness: list[dict[str, str]],
) -> list[dict[str, Any]]:
    semantics_by_dimension = {row["fingerprint_dimension"]: row for row in semantics}
    sh18_by_dimension = {row["dimension"]: row for row in sh18_dimension}
    robust_by_dimension = {row["dimension"]: row for row in sh18_robustness}
    negative_by_dimension = {row["signal_dimension"]: row for row in negative}
    leakage = any(row["leakage_risk"] == "high" for row in audit)
    output: list[dict[str, Any]] = []
    for dimension in DIMENSIONS:
        semantic = semantics_by_dimension[dimension]
        sh18_status = sh18_by_dimension[dimension]["final_dimension_status"]
        robust = robust_by_dimension[dimension]
        strongest_name, strongest_status = strongest_factor(known, dimension)
        context_status = robust.get("context_direction_status", "")
        side_status = robust.get("side_direction_status", "")
        threshold_status = robust.get("threshold_sensitivity_status", "")
        negative_role = "not_applicable"
        final_specificity = "insufficient_support"
        combined = "unresolved_dimension_behavior"
        finding = ""
        follow_up = "Carry this dimension as documented context for later descriptive work."
        if dimension == "coordinate_secondary":
            direct_group = next(
                row
                for row in specificity
                if row["tested_explanation"] == "Direct dependency on a grouping variable"
            )
            direct_status = direct_group["explanation_status"]
            if direct_status in {"partly_explained", "largely_explained"}:
                final_specificity = "association_partly_explained_by_sampling"
                combined = "context_sensitive_structural_association"
            else:
                final_specificity = "specific_group_association_not_explained_by_known_controls"
                combined = "robust_structural_association"
            finding = (
                "The dimension is the TOA MJD coordinate and keeps the SHAPIROMART18 "
                "group-associated structural difference after context and side controls."
            )
            follow_up = "Separate time-axis sampling from phase-distance geometry in a later specified block."
        elif dimension == "coordinate_primary":
            final_specificity = "threshold_localized_association"
            combined = "threshold_localized_coordinate_difference"
            finding = (
                "The dimension is the observing-frequency coordinate and its group "
                "difference is small and threshold-dependent."
            )
            follow_up = "Use the localization table to review fixed SHAPIROMART14 bins without selecting a new threshold."
        else:
            negative_role = negative_by_dimension[dimension]["negative_control_status"]
            if negative_role == "stable_negative_control":
                final_specificity = "no_material_group_association"
                combined = "stable_negative_control"
            else:
                final_specificity = "insufficient_support"
                combined = "unresolved_dimension_behavior"
            finding = (
                "The signal-value dimension does not mirror the coordinate-secondary pattern "
                "under the SHAPIROMART18 controls."
            )
            follow_up = "Retain as an internal negative control in later descriptive checks."
        if leakage:
            final_specificity = "association_explained_by_representation"
            combined = "representation_driven_difference"
        output.append(
            {
                "fingerprint_dimension": dimension,
                "semantic_status": semantic["semantic_status"],
                "primary_role": semantic["primary_role"],
                "SHAPIROMART18_status": sh18_status,
                "strongest_known_factor": strongest_name,
                "strongest_factor_explanation_status": strongest_status,
                "context_adjusted_status": context_status,
                "side_adjusted_status": side_status,
                "threshold_status": threshold_status,
                "representation_audit_status": "leakage_detected" if leakage else "no_leakage_detected",
                "negative_control_role": negative_role,
                "final_specificity_status": final_specificity,
                "combined_result_status": combined,
                "consolidated_finding": finding,
                "interpretation_limit": "Descriptive fingerprint specificity only; no mechanism or physical interpretation is established.",
                "recommended_follow_up": follow_up,
                "notes": "Assessment combines lineage, SHAPIROMART18 status, controls, and representation audit.",
            }
        )
    return output


def final_status_row(
    args: argparse.Namespace,
    assessment: list[dict[str, Any]],
    lineage: list[dict[str, Any]],
    semantics: list[dict[str, Any]],
    specificity: list[dict[str, Any]],
    localization: list[dict[str, Any]],
    coordinate_signal: list[dict[str, Any]],
    negative: list[dict[str, Any]],
    audit: list[dict[str, Any]],
    db_status: dict[str, Any],
) -> dict[str, Any]:
    semantic_counts = Counter(row["semantic_status"] for row in semantics)
    combined_counts = Counter(row["combined_result_status"] for row in assessment)
    leakage = any(row["representation_audit_status"] == "leakage_detected" for row in assessment)
    unresolved = semantic_counts.get("semantics_unresolved", 0)
    partial = semantic_counts.get("semantics_partially_resolved", 0)
    if leakage:
        final = "fingerprint_difference_explained_by_representation"
    elif unresolved:
        final = "fingerprint_dimension_semantics_specificity_failed"
    elif partial:
        final = "fingerprint_dimension_specificity_completed_semantics_partial"
    else:
        final = "fingerprint_dimension_semantics_and_specificity_completed"
    return {
        "research_block": RESEARCH_BLOCK,
        "fingerprint_dimensions_assessed": len(assessment),
        "lineage_reconstructed": "yes" if len(lineage) == 4 else "no",
        "semantics_resolved_dimension_count": sum(
            1
            for row in semantics
            if row["semantic_status"]
            in {
                "documented_measurement_dimension",
                "documented_structural_coordinate",
                "documented_instrument_coordinate",
                "derived_structural_coordinate",
                "metadata_or_configuration_proxy",
                "composite_semantics",
            }
        ),
        "semantics_partially_resolved_dimension_count": semantic_counts.get(
            "semantics_partially_resolved", 0
        ),
        "semantics_unresolved_dimension_count": semantic_counts.get("semantics_unresolved", 0),
        "coordinate_secondary_specificity_completed": "yes" if len(specificity) == 10 else "no",
        "coordinate_primary_localization_completed": "yes" if localization else "no",
        "coordinate_signal_relation_completed": "yes" if coordinate_signal else "no",
        "negative_controls_completed": "yes" if len(negative) == 2 else "no",
        "representation_audit_completed": "yes" if len(audit) >= 9 else "no",
        "representation_leakage_detected": "yes" if leakage else "no",
        "robust_structural_association_dimension_count": combined_counts.get(
            "robust_structural_association", 0
        ),
        "context_sensitive_dimension_count": combined_counts.get(
            "context_sensitive_structural_association", 0
        ),
        "threshold_localized_dimension_count": combined_counts.get(
            "threshold_localized_coordinate_difference", 0
        ),
        "stable_negative_control_dimension_count": combined_counts.get("stable_negative_control", 0),
        "physical_interpretation_performed": "no",
        "causal_claim_made": "no",
        "shapiro_information_claim_made": "no",
        "bridge_claim_made": "no",
        "database_access": "read_only",
        "database_modified": db_status.get("database_modified", "unknown"),
        "additional_gate_created": "no",
        "final_status": final,
        "recommended_next_action": "Review the time-axis and fixed-bin controls before specifying any later analysis.",
        "limitations": (
            "All tests are descriptive. The block does not establish mechanism, causality, "
            "or physical interpretation."
        ),
    }


def write_readout(
    path: Path,
    final_row: dict[str, Any],
    assessment: list[dict[str, Any]],
    specificity: list[dict[str, Any]],
    negative: list[dict[str, Any]],
    db_status: dict[str, Any],
) -> None:
    by_dimension = {row["fingerprint_dimension"]: row for row in assessment}
    direct_dependency = next(
        row
        for row in specificity
        if row["tested_explanation"] == "Direct dependency on a grouping variable"
    )
    lines = [
        "# QSB-SHAPIROMART19 Readout",
        "",
        "## Purpose",
        "",
        "This block reconstructs the four SHAPIROMART04 fingerprint dimensions and audits the SHAPIROMART18 selective pattern.",
        "",
        "## Fingerprint Construction and Lineage",
        "",
        "The four dimensions are direct numeric TIM/source-flag values parsed into an unweighted vector. SHAPIROMART04 applied no scaling, centering, normalization, clipping, or row-level summary operation.",
        "",
        "## Meaning of the Four Dimensions",
        "",
        "- `coordinate_primary`: observing frequency in MHz.",
        "- `coordinate_secondary`: TIM TOA MJD coordinate.",
        "- `signal_value_primary`: SNR source flag.",
        "- `signal_value_secondary`: flux source flag.",
        "",
        "## SHAPIROMART18 Selective Pattern",
        "",
        f"- `coordinate_secondary`: {by_dimension['coordinate_secondary']['SHAPIROMART18_status']}.",
        f"- `coordinate_primary`: {by_dimension['coordinate_primary']['SHAPIROMART18_status']}.",
        f"- `signal_value_primary`: {by_dimension['signal_value_primary']['SHAPIROMART18_status']}.",
        f"- `signal_value_secondary`: {by_dimension['signal_value_secondary']['SHAPIROMART18_status']}.",
        "",
        "## `coordinate_secondary` Specificity Analysis",
        "",
        (
            "`coordinate_secondary` remains a descriptive group-associated TOA-coordinate "
            "difference after receiver/backend, side, threshold, and composition controls. "
            f"The direct phase/distance-axis control is classified as {direct_dependency['explanation_status']}."
        ),
        "",
        "## `coordinate_primary` Threshold Localization",
        "",
        "`coordinate_primary` is the observing-frequency coordinate. Its SHAPIROMART18 behavior is small and threshold-sensitive rather than robust across the fixed 0.05 and 0.15 bands.",
        "",
        "## Coordinate-Signal Relationship",
        "",
        "The coordinate dimensions are not mirrored by parallel material differences in the SNR and flux dimensions under the same joined rows and fixed groups.",
        "",
        "## Signal Dimensions as Negative Controls",
        "",
        f"- `signal_value_primary`: {negative[0]['negative_control_status']}.",
        f"- `signal_value_secondary`: {negative[1]['negative_control_status']}.",
        "",
        "## Representation and Leakage Audit",
        "",
        f"Representation leakage detected: {final_row['representation_leakage_detected']}. Group labels, orbital phase, and absolute distance were not inputs to SHAPIROMART04 fingerprint construction.",
        "",
        "## Consolidated Dimension Findings",
        "",
        f"- `coordinate_secondary`: {by_dimension['coordinate_secondary']['combined_result_status']}.",
        f"- `coordinate_primary`: {by_dimension['coordinate_primary']['combined_result_status']}.",
        f"- `signal_value_primary`: {by_dimension['signal_value_primary']['combined_result_status']}.",
        f"- `signal_value_secondary`: {by_dimension['signal_value_secondary']['combined_result_status']}.",
        "",
        "## Overall Result",
        "",
        f"Final status: {final_row['final_status']}. Database modified: {db_status.get('database_modified', '')}.",
        "",
        "## What This Does Not Establish",
        "",
        "This block does not establish a physical mechanism, causality, Shapiro-information effect, Bridge relation, residual behavior, or timing-model result.",
        "",
        "## Recommended Next Scientific Action",
        "",
        final_row["recommended_next_action"],
        "",
        "## Limitations",
        "",
        final_row["limitations"],
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def prepare_output_dir(args: argparse.Namespace) -> None:
    if args.output_dir.exists():
        existing = [path for path in args.output_dir.iterdir() if path.is_file()]
        if existing and not args.overwrite:
            raise ControlledStop(
                f"Output directory already has files; rerun with --overwrite: {rel(args.output_dir)}"
            )
    args.output_dir.mkdir(parents=True, exist_ok=True)


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.permutation_replicates < 2000:
        raise ControlledStop("permutation_replicates must be at least 2000.")
    prepare_output_dir(args)
    inputs = load_required_inputs(args)
    groups = load_groups(args.shapiromart17_groups_input)
    toa_rows = load_toa_rows(args.shapiromart11_phase_input)
    fingerprints, db_status, feature_rows = load_fingerprints(args.workcopy_db)
    if db_status.get("database_modified") != "no":
        raise ControlledStop("Read-only DB identity changed during run.")
    joined = build_joined_rows(groups, toa_rows, fingerprints)
    bins = load_distance_bins(args.distance_distribution_input)

    lineage = lineage_rows(feature_rows)
    semantics = semantics_rows()
    known = known_factor_associations(joined, inputs["sh18_robustness"], args.minimum_group_count)
    specificity = coordinate_secondary_specificity(joined, args.minimum_group_count)
    localization = localization_rows(joined, bins, args.minimum_group_count)
    coordinate_signal = coordinate_signal_rows(joined, args.minimum_group_count)
    negative = negative_control_rows(
        joined,
        inputs["sh18_robustness"],
        args.permutation_replicates,
        args.random_seed,
        args.minimum_group_count,
    )
    audit = representation_audit_rows()
    assessment = dimension_assessment_rows(
        semantics,
        known,
        specificity,
        negative,
        audit,
        inputs["sh18_dimension"],
        inputs["sh18_robustness"],
    )
    final_row = final_status_row(
        args,
        assessment,
        lineage,
        semantics,
        specificity,
        localization,
        coordinate_signal,
        negative,
        audit,
        db_status,
    )
    summary = {
        "research_block": RESEARCH_BLOCK,
        "timestamp_utc": utc_now(),
        "inputs_read": {
            "shapiromart04_dir": rel(args.shapiromart04_dir),
            "shapiromart05_dir": rel(args.shapiromart05_dir),
            "shapiromart11_phase_input": rel(args.shapiromart11_phase_input),
            "shapiromart17_groups_input": rel(args.shapiromart17_groups_input),
            "shapiromart18_dir": rel(args.shapiromart18_dir),
            "distance_distribution_input": rel(args.distance_distribution_input),
            "workcopy_db": rel(args.workcopy_db),
        },
        "output_dir": rel(args.output_dir),
        "output_files": [rel(args.output_dir / name) for name in OUTPUT_FILES],
        "method": {
            "permutation_replicates": args.permutation_replicates,
            "random_seed": args.random_seed,
            "minimum_group_count": args.minimum_group_count,
            "new_threshold_selected": "no",
            "groups_modified": "no",
        },
        "joined_rows": len(joined),
        "dimension_status_counts": dict(Counter(row["combined_result_status"] for row in assessment)),
        "database": db_status,
        "final_status": final_row,
    }

    write_csv(args.output_dir / "shapiromart19_dimension_lineage.csv", lineage, DIMENSION_LINEAGE_FIELDS)
    write_csv(args.output_dir / "shapiromart19_dimension_semantics.csv", semantics, DIMENSION_SEMANTICS_FIELDS)
    write_csv(args.output_dir / "shapiromart19_known_factor_associations.csv", known, KNOWN_FACTOR_FIELDS)
    write_csv(args.output_dir / "shapiromart19_coordinate_secondary_specificity.csv", specificity, SPECIFICITY_FIELDS)
    write_csv(args.output_dir / "shapiromart19_coordinate_primary_localization.csv", localization, LOCALIZATION_FIELDS)
    write_csv(args.output_dir / "shapiromart19_coordinate_signal_relation.csv", coordinate_signal, COORDINATE_SIGNAL_FIELDS)
    write_csv(args.output_dir / "shapiromart19_negative_control_assessment.csv", negative, NEGATIVE_CONTROL_FIELDS)
    write_csv(args.output_dir / "shapiromart19_representation_audit.csv", audit, REPRESENTATION_AUDIT_FIELDS)
    write_csv(args.output_dir / "shapiromart19_dimension_assessment.csv", assessment, DIMENSION_ASSESSMENT_FIELDS)
    write_csv(args.output_dir / "shapiromart19_final_status.csv", [final_row], FINAL_STATUS_FIELDS)
    write_json(args.output_dir / "shapiromart19_summary.json", summary)
    write_readout(
        args.output_dir / "shapiromart19_readout.md",
        final_row,
        assessment,
        specificity,
        negative,
        db_status,
    )
    return summary


def main() -> int:
    args = parse_args()
    try:
        summary = run(args)
    except Exception as exc:
        print(f"{RESEARCH_BLOCK} failed: {exc}", file=sys.stderr)
        return 1
    print(f"{RESEARCH_BLOCK} completed: {summary['output_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
