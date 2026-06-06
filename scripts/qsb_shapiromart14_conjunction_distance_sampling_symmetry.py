#!/usr/bin/env python3
"""QSB-SHAPIROMART14 conjunction-distance sampling symmetry.

This block is descriptive only. It reads SHAPIROMART13 phase-distance artifacts
and SHAPIROMART12 summary-only context artifacts, computes overall conjunction
distance and signed-offset sampling summaries, and does not create exposure
classes, select a threshold, fit a model, inspect residuals, calculate a
Shapiro delay, open a database, or read raw TIM/PAR files.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


RESEARCH_BLOCK = "QSB-SHAPIROMART14"
EXPECTED_ROW_COUNT = 7419

SHAPIROMART_BASE = Path("runs/QSB-SHAPIROMART")
SHAPIROMART13_DIR = SHAPIROMART_BASE / "SHAPIROMART13_ELL1_GEOMETRIC_PHASE_MAPPING"
SHAPIROMART12_DIR = SHAPIROMART_BASE / "SHAPIROMART12_ORBITAL_PHASE_AXIS_QC"
DEFAULT_OUTPUT_DIR = (
    SHAPIROMART_BASE / "SHAPIROMART14_CONJUNCTION_DISTANCE_SAMPLING_SYMMETRY"
)

DEFAULT_MAPPING_INPUT = SHAPIROMART13_DIR / "shapiromart13_phase_geometry_mapping.csv"
DEFAULT_PHASE_DISTANCE_QC_INPUT = SHAPIROMART13_DIR / "shapiromart13_phase_distance_qc.csv"
DEFAULT_CONTEXT_SUMMARY_INPUT = (
    SHAPIROMART13_DIR / "shapiromart13_context_phase_distance_summary.csv"
)
DEFAULT_FINAL_STATUS_INPUT = SHAPIROMART13_DIR / "shapiromart13_final_status.csv"
DEFAULT_SUMMARY_JSON_INPUT = SHAPIROMART13_DIR / "shapiromart13_summary.json"
DEFAULT_CONTEXT_COVERAGE_INPUT = (
    SHAPIROMART12_DIR / "shapiromart12_context_phase_coverage.csv"
)
DEFAULT_SHAPIROMART12_FINAL_STATUS_INPUT = (
    SHAPIROMART12_DIR / "shapiromart12_final_status.csv"
)

READOUT_MD = "shapiromart14_readout.md"
SUMMARY_JSON = "shapiromart14_summary.json"
ABSOLUTE_DISTRIBUTION_CSV = "shapiromart14_absolute_distance_distribution.csv"
SIGNED_DISTRIBUTION_CSV = "shapiromart14_signed_offset_distribution.csv"
SYMMETRY_BAND_CSV = "shapiromart14_symmetry_band_summary.csv"
CONTEXT_SYMMETRY_CSV = "shapiromart14_context_symmetry_summary.csv"
ANOMALY_CSV = "shapiromart14_sampling_anomaly_inventory.csv"
THRESHOLD_CANDIDATE_CSV = "shapiromart14_threshold_candidate_inventory.csv"
FINAL_STATUS_CSV = "shapiromart14_final_status.csv"
ABSOLUTE_DISTRIBUTION_PNG = "shapiromart14_absolute_distance_distribution.png"
SIGNED_DISTRIBUTION_PNG = "shapiromart14_signed_offset_distribution.png"

DEFAULT_OUTPUT_FILES = [
    READOUT_MD,
    SUMMARY_JSON,
    ABSOLUTE_DISTRIBUTION_CSV,
    SIGNED_DISTRIBUTION_CSV,
    SYMMETRY_BAND_CSV,
    CONTEXT_SYMMETRY_CSV,
    ANOMALY_CSV,
    THRESHOLD_CANDIDATE_CSV,
    FINAL_STATUS_CSV,
]

PNG_OUTPUT_FILES = [
    ABSOLUTE_DISTRIBUTION_PNG,
    SIGNED_DISTRIBUTION_PNG,
]

ALLOWED_INPUT_FILENAMES = {
    "shapiromart13_phase_geometry_mapping.csv",
    "shapiromart13_phase_distance_qc.csv",
    "shapiromart13_context_phase_distance_summary.csv",
    "shapiromart13_final_status.csv",
    "shapiromart13_summary.json",
    "shapiromart12_context_phase_coverage.csv",
    "shapiromart12_final_status.csv",
}

MAPPING_FIELDS = [
    "source_row_index",
    "orbital_phase",
    "phase_origin",
    "phase_origin_role",
    "superior_conjunction_phase",
    "signed_phase_offset",
    "absolute_phase_distance",
    "nearest_reference_point",
    "phase_geometry_status",
    "phase_method",
    "notes",
]

ABSOLUTE_DISTRIBUTION_FIELDS = [
    "distribution_scope",
    "context_name",
    "bin_count_total",
    "bin_index",
    "lower_bound_inclusive",
    "upper_bound_exclusive",
    "observed_count",
    "observed_fraction",
    "cumulative_count",
    "cumulative_fraction",
    "density_per_phase_unit",
    "negative_side_count",
    "positive_side_count",
    "coverage_status",
    "notes",
]

SIGNED_DISTRIBUTION_FIELDS = [
    "distribution_scope",
    "context_name",
    "bin_count_total",
    "bin_index",
    "lower_bound_inclusive",
    "upper_bound_exclusive",
    "midpoint",
    "side",
    "observed_count",
    "observed_fraction",
    "mirrored_bin_index",
    "mirrored_count",
    "count_difference",
    "absolute_count_difference",
    "normalized_imbalance",
    "symmetry_status",
    "notes",
]

SYMMETRY_BAND_FIELDS = [
    "context_name",
    "band_half_width",
    "negative_side_count",
    "positive_side_count",
    "exact_zero_count",
    "total_in_band",
    "fraction_of_context",
    "count_difference",
    "absolute_count_difference",
    "negative_to_positive_ratio",
    "normalized_imbalance",
    "minimum_side_fraction",
    "symmetry_status",
    "notes",
]

CONTEXT_SYMMETRY_FIELDS = [
    "context_name",
    "toa_count",
    "negative_side_total",
    "positive_side_total",
    "exact_zero_count",
    "median_signed_offset",
    "median_absolute_distance",
    "mean_absolute_distance",
    "minimum_absolute_distance",
    "maximum_absolute_distance",
    "most_balanced_band",
    "most_balanced_normalized_imbalance",
    "most_imbalanced_band",
    "most_imbalanced_normalized_imbalance",
    "context_coverage_status",
    "notes",
]

ANOMALY_FIELDS = [
    "anomaly_id",
    "anomaly_type",
    "severity",
    "context_name",
    "affected_range",
    "affected_count",
    "affected_fraction",
    "evidence_basis",
    "possible_sampling_explanation",
    "disposition",
    "notes",
]

THRESHOLD_CANDIDATE_FIELDS = [
    "candidate_id",
    "threshold_type",
    "threshold_value",
    "rationale",
    "total_count_inside",
    "total_fraction_inside",
    "negative_side_count",
    "positive_side_count",
    "normalized_imbalance",
    "rcvr_800_count",
    "rcvr1_2_count",
    "minimum_context_count",
    "local_density_context",
    "stability_note",
    "suitability_status",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "input_geometry_axis_available",
    "input_row_count",
    "absolute_distance_distribution_completed",
    "signed_offset_distribution_completed",
    "symmetry_analysis_completed",
    "receiver_backend_symmetry_assessed",
    "sampling_anomalies_found",
    "high_severity_sampling_anomalies_found",
    "threshold_candidates_catalogued",
    "exposure_classes_created",
    "threshold_selected",
    "shapiro_delay_calculated",
    "residual_analysis_performed",
    "model_fit_performed",
    "physical_interpretation_performed",
    "database_access",
    "additional_gate_created",
    "final_status",
    "recommended_next_action",
    "limitations",
]

GEOMETRIC_BAND_WIDTHS = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25]
QUANTILE_FRACTIONS = [0.05, 0.10, 0.20, 0.25, 0.33, 0.50]
REQUIRED_CONTEXTS = ["overall", "Rcvr_800 / GUPPI", "Rcvr1_2 / GUPPI"]

# Predeclared descriptive thresholds. They are diagnostics only.
COVERAGE_DENSE_RATIO_MIN = 1.25
COVERAGE_MODERATE_RATIO_MIN = 0.50
SYMMETRY_MIN_TOTAL_COUNT = 20
SYMMETRY_APPROXIMATELY_BALANCED_MAX = 0.10
SYMMETRY_MILD_IMBALANCE_MAX = 0.25
SYMMETRY_MODERATE_IMBALANCE_MAX = 0.50
ANOMALY_DENSE_RATIO_MIN = 1.75
ANOMALY_SPARSE_RATIO_MAX = 0.25
ANOMALY_ABRUPT_DIFF_RATIO_MIN = 0.75


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Descriptively characterize conjunction-distance and signed-offset "
            "sampling symmetry from SHAPIROMART13 phase-distance outputs."
        )
    )
    parser.add_argument("--mapping-input", type=Path, default=DEFAULT_MAPPING_INPUT)
    parser.add_argument(
        "--phase-distance-qc-input",
        type=Path,
        default=DEFAULT_PHASE_DISTANCE_QC_INPUT,
    )
    parser.add_argument(
        "--context-summary-input",
        type=Path,
        default=DEFAULT_CONTEXT_SUMMARY_INPUT,
    )
    parser.add_argument("--final-status-input", type=Path, default=DEFAULT_FINAL_STATUS_INPUT)
    parser.add_argument("--summary-json-input", type=Path, default=DEFAULT_SUMMARY_JSON_INPUT)
    parser.add_argument(
        "--context-phase-coverage-input",
        type=Path,
        default=DEFAULT_CONTEXT_COVERAGE_INPUT,
    )
    parser.add_argument(
        "--shapiromart12-final-status-input",
        type=Path,
        default=DEFAULT_SHAPIROMART12_FINAL_STATUS_INPUT,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--absolute-bin-count", type=int, default=20)
    parser.add_argument("--signed-bin-count", type=int, default=20)
    parser.add_argument(
        "--symmetry-band-widths",
        default=",".join(fmt_float(value) for value in GEOMETRIC_BAND_WIDTHS),
        help="Comma-separated diagnostic half-widths, not exposure thresholds.",
    )
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument(
        "--write-png",
        action="store_true",
        help="Optionally write diagnostic PNG histograms. Disabled by default.",
    )
    return parser.parse_args()


def fmt_float(value: float) -> str:
    if not math.isfinite(value):
        return str(value)
    return format(value, ".17g")


def fraction_text(count: int, total: int) -> str:
    if total <= 0:
        return "0"
    return format(count / total, ".12g")


def ratio_text(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "inf" if numerator > 0 else ""
    return format(numerator / denominator, ".12g")


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    ensure_allowed_input(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_single_csv_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, observed {len(rows)}.")
    return rows[0]


def read_json(path: Path) -> dict[str, Any]:
    ensure_allowed_input(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return payload


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def ensure_allowed_input(path: Path) -> None:
    if path.name not in ALLOWED_INPUT_FILENAMES:
        raise ValueError(f"Input filename is outside the SHAPIROMART14 allowed list: {path}")
    if not path.exists():
        raise FileNotFoundError(path)


def parse_band_widths(raw_value: str) -> list[float]:
    widths: list[float] = []
    for part in raw_value.split(","):
        stripped = part.strip()
        if not stripped:
            continue
        value = float(stripped)
        if not math.isfinite(value) or value <= 0.0 or value > 0.5:
            raise ValueError(f"Invalid symmetry band half-width: {stripped}")
        widths.append(value)
    if not widths:
        raise ValueError("At least one symmetry band half-width is required.")
    return widths


def validate_output_dir(output_dir: Path, expected_files: list[str], overwrite: bool) -> None:
    if output_dir.exists():
        present_files = sorted(path.name for path in output_dir.iterdir() if path.is_file())
        if present_files and not overwrite:
            raise FileExistsError(
                f"Output directory already contains files; use --overwrite: {output_dir}"
            )
        unexpected = sorted(set(present_files) - set(expected_files))
        if unexpected:
            raise FileExistsError(
                f"Output directory contains files outside the expected output set: {unexpected}"
            )
    output_dir.mkdir(parents=True, exist_ok=True)


def require_fields(rows: list[dict[str, str]], required_fields: list[str], path: Path) -> None:
    if not rows:
        raise ValueError(f"Input has no rows: {path}")
    missing = sorted(set(required_fields) - set(rows[0].keys()))
    if missing:
        raise ValueError(f"Missing required fields in {path}: {missing}")


def cyclic_offset(phase: float, superior_conjunction_phase: float = 0.25) -> float:
    return ((phase - superior_conjunction_phase + 0.5) % 1.0) - 0.5


def float_field(row: dict[str, str], field: str) -> float:
    value = float(row[field])
    if not math.isfinite(value):
        raise ValueError(f"Non-finite value in field {field}.")
    return value


def load_and_validate_mapping(path: Path) -> list[dict[str, Any]]:
    rows = read_csv_rows(path)
    require_fields(rows, MAPPING_FIELDS, path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"Expected {EXPECTED_ROW_COUNT} mapping rows, observed {len(rows)}.")

    source_indices: list[str] = []
    parsed_rows: list[dict[str, Any]] = []
    for row in rows:
        source_indices.append(row["source_row_index"])
        phase = float_field(row, "orbital_phase")
        signed_offset = float_field(row, "signed_phase_offset")
        absolute_distance = float_field(row, "absolute_phase_distance")
        superior_phase = float_field(row, "superior_conjunction_phase")

        if not 0.0 <= phase < 1.0:
            raise ValueError(f"orbital_phase out of range at row {row['source_row_index']}.")
        if not math.isclose(superior_phase, 0.25, rel_tol=0.0, abs_tol=1e-15):
            raise ValueError("superior_conjunction_phase must be 0.25.")
        if not -0.5 <= signed_offset < 0.5:
            raise ValueError(f"signed_phase_offset out of range at row {row['source_row_index']}.")
        if not 0.0 <= absolute_distance <= 0.5:
            raise ValueError(
                f"absolute_phase_distance out of range at row {row['source_row_index']}."
            )
        expected_offset = cyclic_offset(phase, superior_phase)
        if not math.isclose(signed_offset, expected_offset, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(
                f"signed_phase_offset formula mismatch at row {row['source_row_index']}."
            )
        if not math.isclose(absolute_distance, abs(signed_offset), rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(
                f"absolute_phase_distance mismatch at row {row['source_row_index']}."
            )
        parsed_rows.append(
            {
                "source_row_index": row["source_row_index"],
                "orbital_phase": phase,
                "signed_phase_offset": signed_offset,
                "absolute_phase_distance": absolute_distance,
            }
        )

    if len(set(source_indices)) != len(source_indices):
        raise ValueError("source_row_index values are not unique.")
    return parsed_rows


def validate_status_inputs(
    qc_path: Path,
    context_summary_path: Path,
    final_status_path: Path,
    summary_json_path: Path,
    context_coverage_path: Path,
    shapiromart12_final_status_path: Path,
) -> dict[str, Any]:
    qc_row = read_single_csv_row(qc_path)
    final_row = read_single_csv_row(final_status_path)
    summary = read_json(summary_json_path)
    context_rows = read_csv_rows(context_summary_path)
    context_coverage_rows = read_csv_rows(context_coverage_path)
    shapiromart12_final = read_single_csv_row(shapiromart12_final_status_path)

    expected_qc_pairs = {
        "expected_row_count": str(EXPECTED_ROW_COUNT),
        "observed_row_count": str(EXPECTED_ROW_COUNT),
        "valid_signed_offset_count": str(EXPECTED_ROW_COUNT),
        "valid_absolute_distance_count": str(EXPECTED_ROW_COUNT),
        "all_values_finite": "yes",
        "all_values_in_range": "yes",
        "source_row_indices_unique": "yes",
        "qc_status": "phase_distance_qc_passed",
    }
    failed_qc = {
        key: {"expected": expected, "observed": qc_row.get(key, "")}
        for key, expected in expected_qc_pairs.items()
        if qc_row.get(key, "") != expected
    }
    if failed_qc:
        raise ValueError(f"SHAPIROMART13 phase-distance QC validation failed: {failed_qc}")

    expected_final_pairs = {
        "ell1_phase_axis_available": "yes",
        "phase_origin_tasc_supported": "yes",
        "superior_conjunction_mapping_supported": "yes",
        "geometric_phase_distance_generated": "yes",
        "geometric_phase_distance_row_count": str(EXPECTED_ROW_COUNT),
        "exposure_classes_created": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "model_fit_performed": "no",
        "database_access": "none",
        "additional_gate_created": "no",
        "final_status": "ell1_geometric_phase_mapping_supported",
    }
    failed_final = {
        key: {"expected": expected, "observed": final_row.get(key, "")}
        for key, expected in expected_final_pairs.items()
        if final_row.get(key, "") != expected
    }
    if failed_final:
        raise ValueError(f"SHAPIROMART13 final-status validation failed: {failed_final}")

    if shapiromart12_final.get("observed_row_count", "") != str(EXPECTED_ROW_COUNT):
        raise ValueError("SHAPIROMART12 final status does not report the expected row count.")

    by_context = {row.get("context_name", ""): row for row in context_rows}
    coverage_by_context = {row.get("context_name", ""): row for row in context_coverage_rows}
    missing_contexts = sorted(set(REQUIRED_CONTEXTS) - set(by_context.keys()))
    missing_coverage = sorted(set(REQUIRED_CONTEXTS[1:]) - set(coverage_by_context.keys()))
    if missing_contexts:
        raise ValueError(f"SHAPIROMART13 context summary is missing: {missing_contexts}")
    if missing_coverage:
        raise ValueError(f"SHAPIROMART12 context coverage is missing: {missing_coverage}")

    context_total = sum(int(by_context[name]["toa_count"]) for name in REQUIRED_CONTEXTS[1:])
    coverage_total = sum(int(coverage_by_context[name]["toa_count"]) for name in REQUIRED_CONTEXTS[1:])
    if context_total != EXPECTED_ROW_COUNT or coverage_total != EXPECTED_ROW_COUNT:
        raise ValueError(
            "Receiver/backend summary totals do not sum to the expected row count."
        )

    return {
        "qc": qc_row,
        "final_status_13": final_row,
        "summary_13": summary,
        "context_rows": context_rows,
        "context_by_name": by_context,
        "context_coverage_rows": context_coverage_rows,
        "context_coverage_by_name": coverage_by_context,
        "shapiromart12_final": shapiromart12_final,
    }


def classify_coverage(count: int, expected_count: float) -> str:
    if count == 0:
        return "empty"
    ratio = count / expected_count if expected_count else 0.0
    if ratio >= COVERAGE_DENSE_RATIO_MIN:
        return "dense"
    if ratio >= COVERAGE_MODERATE_RATIO_MIN:
        return "moderate"
    return "sparse"


def classify_symmetry(negative_count: int, positive_count: int) -> str:
    total = negative_count + positive_count
    if total < SYMMETRY_MIN_TOTAL_COUNT:
        return "insufficient_count"
    imbalance = abs(negative_count - positive_count) / max(total, 1)
    if imbalance <= SYMMETRY_APPROXIMATELY_BALANCED_MAX:
        return "approximately_balanced"
    if imbalance <= SYMMETRY_MILD_IMBALANCE_MAX:
        return "mildly_imbalanced"
    if imbalance <= SYMMETRY_MODERATE_IMBALANCE_MAX:
        return "moderately_imbalanced"
    return "strongly_imbalanced"


def absolute_bin_index(value: float, bin_count: int) -> int:
    width = 0.5 / bin_count
    return min(int(value / width), bin_count - 1)


def signed_bin_index(value: float, bin_count: int) -> int:
    width = 1.0 / bin_count
    return min(max(int((value + 0.5) / width), 0), bin_count - 1)


def build_absolute_distribution(
    rows: list[dict[str, Any]], bin_count: int
) -> list[dict[str, Any]]:
    width = 0.5 / bin_count
    total = len(rows)
    expected = total / bin_count
    counts = [0 for _ in range(bin_count)]
    negative_counts = [0 for _ in range(bin_count)]
    positive_counts = [0 for _ in range(bin_count)]

    for row in rows:
        index = absolute_bin_index(float(row["absolute_phase_distance"]), bin_count)
        counts[index] += 1
        offset = float(row["signed_phase_offset"])
        if offset < 0.0:
            negative_counts[index] += 1
        elif offset > 0.0:
            positive_counts[index] += 1

    output_rows: list[dict[str, Any]] = []
    cumulative = 0
    for index, count in enumerate(counts):
        lower = index * width
        upper = (index + 1) * width
        cumulative += count
        note = (
            "Coverage status uses count divided by the equal-width descriptive "
            "reference count; per-row receiver/backend context is not present in "
            "the allowed mapping input."
        )
        output_rows.append(
            {
                "distribution_scope": "overall",
                "context_name": "overall",
                "bin_count_total": bin_count,
                "bin_index": index,
                "lower_bound_inclusive": fmt_float(lower),
                "upper_bound_exclusive": fmt_float(upper),
                "observed_count": count,
                "observed_fraction": fraction_text(count, total),
                "cumulative_count": cumulative,
                "cumulative_fraction": fraction_text(cumulative, total),
                "density_per_phase_unit": fmt_float(count / width),
                "negative_side_count": negative_counts[index],
                "positive_side_count": positive_counts[index],
                "coverage_status": classify_coverage(count, expected),
                "notes": note,
            }
        )
    return output_rows


def signed_side(lower: float, upper: float) -> str:
    if lower <= 0.0 < upper:
        return "crossing_bin"
    if upper <= 0.0:
        return "pre_conjunction"
    return "post_conjunction"


def build_signed_distribution(
    rows: list[dict[str, Any]], bin_count: int
) -> list[dict[str, Any]]:
    width = 1.0 / bin_count
    total = len(rows)
    counts = [0 for _ in range(bin_count)]
    for row in rows:
        counts[signed_bin_index(float(row["signed_phase_offset"]), bin_count)] += 1

    output_rows: list[dict[str, Any]] = []
    for index, count in enumerate(counts):
        lower = -0.5 + index * width
        upper = lower + width
        midpoint = lower + width / 2.0
        mirrored_index = bin_count - 1 - index
        mirrored_count = counts[mirrored_index]
        difference = count - mirrored_count
        pair_total = count + mirrored_count
        normalized = abs(difference) / max(pair_total, 1)
        output_rows.append(
            {
                "distribution_scope": "overall",
                "context_name": "overall",
                "bin_count_total": bin_count,
                "bin_index": index,
                "lower_bound_inclusive": fmt_float(lower),
                "upper_bound_exclusive": fmt_float(upper),
                "midpoint": fmt_float(midpoint),
                "side": signed_side(lower, upper),
                "observed_count": count,
                "observed_fraction": fraction_text(count, total),
                "mirrored_bin_index": mirrored_index,
                "mirrored_count": mirrored_count,
                "count_difference": difference,
                "absolute_count_difference": abs(difference),
                "normalized_imbalance": fmt_float(normalized),
                "symmetry_status": classify_symmetry(count, mirrored_count),
                "notes": (
                    "pre_conjunction and post_conjunction are phase-direction "
                    "descriptors only."
                ),
            }
        )
    return output_rows


def build_symmetry_band_rows(
    rows: list[dict[str, Any]], band_widths: list[float]
) -> list[dict[str, Any]]:
    total_context = len(rows)
    offsets = [float(row["signed_phase_offset"]) for row in rows]
    output_rows: list[dict[str, Any]] = []
    for width in band_widths:
        negative_count = sum(1 for value in offsets if -width <= value < 0.0)
        positive_count = sum(1 for value in offsets if 0.0 < value <= width)
        exact_zero_count = sum(1 for value in offsets if value == 0.0)
        total_in_band = negative_count + positive_count + exact_zero_count
        side_total = negative_count + positive_count
        difference = negative_count - positive_count
        normalized = abs(difference) / max(side_total, 1)
        minimum_side_fraction = min(negative_count, positive_count) / max(side_total, 1)
        output_rows.append(
            {
                "context_name": "overall",
                "band_half_width": fmt_float(width),
                "negative_side_count": negative_count,
                "positive_side_count": positive_count,
                "exact_zero_count": exact_zero_count,
                "total_in_band": total_in_band,
                "fraction_of_context": fraction_text(total_in_band, total_context),
                "count_difference": difference,
                "absolute_count_difference": abs(difference),
                "negative_to_positive_ratio": ratio_text(negative_count, positive_count),
                "normalized_imbalance": fmt_float(normalized),
                "minimum_side_fraction": fmt_float(minimum_side_fraction),
                "symmetry_status": classify_symmetry(negative_count, positive_count),
                "notes": (
                    "Overall row-level band check from signed_phase_offset; exact "
                    "zero values are counted separately from side counts."
                ),
            }
        )
    return output_rows


def band_extrema(
    symmetry_rows: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any]]:
    usable = [
        row
        for row in symmetry_rows
        if row["context_name"] == "overall"
        and row["symmetry_status"] != "insufficient_count"
    ]
    if not usable:
        return {}, {}
    return (
        min(usable, key=lambda row: float(row["normalized_imbalance"])),
        max(usable, key=lambda row: float(row["normalized_imbalance"])),
    )


def build_context_summary_rows(
    rows: list[dict[str, Any]],
    status_payload: dict[str, Any],
    symmetry_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    offsets = [float(row["signed_phase_offset"]) for row in rows]
    distances = [float(row["absolute_phase_distance"]) for row in rows]
    most_balanced, most_imbalanced = band_extrema(symmetry_rows)
    output_rows: list[dict[str, Any]] = [
        {
            "context_name": "overall",
            "toa_count": len(rows),
            "negative_side_total": sum(1 for value in offsets if value < 0.0),
            "positive_side_total": sum(1 for value in offsets if value > 0.0),
            "exact_zero_count": sum(1 for value in offsets if value == 0.0),
            "median_signed_offset": fmt_float(statistics.median(offsets)),
            "median_absolute_distance": fmt_float(statistics.median(distances)),
            "mean_absolute_distance": fmt_float(statistics.fmean(distances)),
            "minimum_absolute_distance": fmt_float(min(distances)),
            "maximum_absolute_distance": fmt_float(max(distances)),
            "most_balanced_band": most_balanced.get("band_half_width", ""),
            "most_balanced_normalized_imbalance": most_balanced.get(
                "normalized_imbalance", ""
            ),
            "most_imbalanced_band": most_imbalanced.get("band_half_width", ""),
            "most_imbalanced_normalized_imbalance": most_imbalanced.get(
                "normalized_imbalance", ""
            ),
            "context_coverage_status": "complete_from_mapping",
            "notes": "Overall row-level symmetry is fully characterized from SHAPIROMART13 mapping rows.",
        }
    ]

    context_by_name = status_payload["context_by_name"]
    coverage_by_name = status_payload["context_coverage_by_name"]
    for context_name in REQUIRED_CONTEXTS[1:]:
        context_row = context_by_name[context_name]
        coverage_row = coverage_by_name.get(context_name, {})
        output_rows.append(
            {
                "context_name": context_name,
                "toa_count": context_row.get("toa_count", ""),
                "negative_side_total": "",
                "positive_side_total": "",
                "exact_zero_count": context_row.get("exact_conjunction_count", ""),
                "median_signed_offset": "",
                "median_absolute_distance": context_row.get(
                    "median_absolute_phase_distance", ""
                ),
                "mean_absolute_distance": context_row.get("mean_absolute_phase_distance", ""),
                "minimum_absolute_distance": context_row.get(
                    "minimum_absolute_phase_distance", ""
                ),
                "maximum_absolute_distance": context_row.get(
                    "maximum_absolute_phase_distance", ""
                ),
                "most_balanced_band": "",
                "most_balanced_normalized_imbalance": "",
                "most_imbalanced_band": "",
                "most_imbalanced_normalized_imbalance": "",
                "context_coverage_status": "summary_only_row_context_unavailable",
                "notes": (
                    "Receiver/backend summary total is available"
                    f" (coverage_fraction={coverage_row.get('phase_coverage_fraction', '')}), "
                    "but per-row context is absent from the allowed SHAPIROMART13 mapping, "
                    "so side totals and band symmetry are not recalculated."
                ),
            }
        )
    return output_rows


def range_label(row: dict[str, Any]) -> str:
    return f"[{row['lower_bound_inclusive']}, {row['upper_bound_exclusive']})"


def build_anomaly_inventory(
    absolute_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
    symmetry_rows: list[dict[str, Any]],
    total_count: int,
) -> list[dict[str, Any]]:
    expected_abs = total_count / len(absolute_rows)
    anomalies: list[dict[str, Any]] = []

    def append(
        anomaly_type: str,
        severity: str,
        affected_range: str,
        affected_count: int,
        evidence_basis: str,
        disposition: str,
        notes: str,
    ) -> None:
        anomalies.append(
            {
                "anomaly_id": f"SHAPIROMART14_ANOMALY_{len(anomalies) + 1:03d}",
                "anomaly_type": anomaly_type,
                "severity": severity,
                "context_name": "overall",
                "affected_range": affected_range,
                "affected_count": affected_count,
                "affected_fraction": fraction_text(affected_count, total_count),
                "evidence_basis": evidence_basis,
                "possible_sampling_explanation": "compatible_with_targeted_sampling",
                "disposition": disposition,
                "notes": notes,
            }
        )

    for row in absolute_rows:
        count = int(row["observed_count"])
        ratio = count / expected_abs if expected_abs else 0.0
        if ratio >= ANOMALY_DENSE_RATIO_MIN:
            append(
                "extreme_dense_absolute_distance_bin",
                "high" if ratio >= 2.5 else "moderate",
                range_label(row),
                count,
                f"bin_count_ratio_to_equal_width_reference={fmt_float(ratio)}",
                "descriptive_sampling_feature",
                "Dense bin only; no physical interpretation is assigned.",
            )
        if count == 0:
            append(
                "empty_absolute_distance_bin",
                "moderate",
                range_label(row),
                0,
                "observed_count=0",
                "descriptive_sampling_gap",
                "Empty bin in absolute phase distance.",
            )
        elif ratio <= ANOMALY_SPARSE_RATIO_MAX:
            append(
                "sparse_absolute_distance_bin",
                "moderate",
                range_label(row),
                count,
                f"bin_count_ratio_to_equal_width_reference={fmt_float(ratio)}",
                "descriptive_sampling_gap",
                "Sparse occupied bin only; no effect claim is made.",
            )

    for previous, current in zip(absolute_rows, absolute_rows[1:]):
        previous_count = int(previous["observed_count"])
        current_count = int(current["observed_count"])
        difference = abs(current_count - previous_count)
        diff_ratio = difference / expected_abs if expected_abs else 0.0
        if diff_ratio >= ANOMALY_ABRUPT_DIFF_RATIO_MIN:
            append(
                "abrupt_neighbor_density_change",
                "high" if diff_ratio >= 1.5 else "moderate",
                f"{range_label(previous)} -> {range_label(current)}",
                difference,
                f"absolute_neighbor_count_difference={difference}",
                "descriptive_density_transition",
                "Neighboring absolute-distance bin counts differ strongly.",
            )

    for row in signed_rows:
        if row["symmetry_status"] == "strongly_imbalanced":
            append(
                "strong_signed_mirror_bin_imbalance",
                "high",
                range_label(row),
                int(row["absolute_count_difference"]),
                (
                    "signed_bin_mirror_normalized_imbalance="
                    f"{row['normalized_imbalance']}"
                ),
                "descriptive_side_imbalance",
                "Mirrored signed-offset bins differ strongly.",
            )

    for row in symmetry_rows:
        if row["symmetry_status"] == "strongly_imbalanced":
            append(
                "strong_symmetric_band_imbalance",
                "high",
                f"band_half_width={row['band_half_width']}",
                int(row["absolute_count_difference"]),
                f"band_normalized_imbalance={row['normalized_imbalance']}",
                "descriptive_side_imbalance",
                "Negative and positive side counts differ strongly in this diagnostic band.",
            )
        if int(row["total_in_band"]) < SYMMETRY_MIN_TOTAL_COUNT:
            append(
                "very_low_small_band_count",
                "moderate",
                f"band_half_width={row['band_half_width']}",
                int(row["total_in_band"]),
                f"total_in_band={row['total_in_band']}",
                "descriptive_count_limitation",
                "Very small near-conjunction count limits descriptive comparison.",
            )

    anomalies.append(
        {
            "anomaly_id": f"SHAPIROMART14_ANOMALY_{len(anomalies) + 1:03d}",
            "anomaly_type": "receiver_backend_band_symmetry_not_recomputable",
            "severity": "moderate",
            "context_name": "Rcvr_800 / GUPPI; Rcvr1_2 / GUPPI",
            "affected_range": "all diagnostic bands",
            "affected_count": total_count,
            "affected_fraction": "1",
            "evidence_basis": "allowed SHAPIROMART13 mapping lacks per-row receiver/backend fields",
            "possible_sampling_explanation": "",
            "disposition": "input_granularity_limitation",
            "notes": (
                "Summary receiver/backend totals are available, but row-level "
                "context symmetry cannot be recalculated from the allowed files."
            ),
        }
    )
    return anomalies


def empirical_quantile_nearest_rank(values: list[float], fraction: float) -> float:
    if not values:
        raise ValueError("Cannot compute quantile for an empty list.")
    sorted_values = sorted(values)
    index = max(0, math.ceil(fraction * len(sorted_values)) - 1)
    return sorted_values[min(index, len(sorted_values) - 1)]


def candidate_counts(rows: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
    inside = [row for row in rows if float(row["absolute_phase_distance"]) <= threshold]
    negative = sum(1 for row in inside if float(row["signed_phase_offset"]) < 0.0)
    positive = sum(1 for row in inside if float(row["signed_phase_offset"]) > 0.0)
    normalized = abs(negative - positive) / max(negative + positive, 1)
    return {
        "total": len(inside),
        "negative": negative,
        "positive": positive,
        "normalized": normalized,
    }


def local_density_note(threshold: float, absolute_rows: list[dict[str, Any]]) -> str:
    for row in absolute_rows:
        lower = float(row["lower_bound_inclusive"])
        upper = float(row["upper_bound_exclusive"])
        if lower <= threshold <= upper:
            return (
                f"bin={row['bin_index']};count={row['observed_count']};"
                f"density_per_phase_unit={row['density_per_phase_unit']}"
            )
    return "outside_absolute_distribution_bins"


def suitability_status(
    counts: dict[str, Any], threshold: float, seen_totals: set[int]
) -> str:
    total = int(counts["total"])
    normalized = float(counts["normalized"])
    if threshold <= 0.0 or threshold > 0.5:
        return "not_recommended"
    if total < SYMMETRY_MIN_TOTAL_COUNT:
        return "too_sparse"
    if total in seen_totals:
        return "redundant"
    if normalized > SYMMETRY_MILD_IMBALANCE_MAX:
        return "sampling_imbalanced"
    return "descriptively_viable"


def build_threshold_candidates(
    rows: list[dict[str, Any]],
    absolute_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    distances = [float(row["absolute_phase_distance"]) for row in rows]
    candidate_specs: list[tuple[str, float, str]] = []

    for width in GEOMETRIC_BAND_WIDTHS:
        candidate_specs.append(
            (
                "predefined_geometric_band",
                width,
                "Predeclared diagnostic band half-width; not selected as a threshold.",
            )
        )

    for fraction in QUANTILE_FRACTIONS:
        value = empirical_quantile_nearest_rank(distances, fraction)
        candidate_specs.append(
            (
                f"empirical_quantile_{int(fraction * 100)}pct",
                value,
                (
                    f"Nearest-rank empirical absolute-distance quantile at "
                    f"{format(fraction, '.0%')}."
                ),
            )
        )

    counts = [int(row["observed_count"]) for row in absolute_rows]
    for index in range(1, len(absolute_rows) - 1):
        previous_count = counts[index - 1]
        current_count = counts[index]
        next_count = counts[index + 1]
        upper_edge = float(absolute_rows[index]["upper_bound_exclusive"])
        if current_count > previous_count and current_count > next_count:
            candidate_specs.append(
                (
                    "local_density_maximum_edge",
                    upper_edge,
                    f"Local maximum absolute-distance bin at index {index}.",
                )
            )
        if current_count < previous_count and current_count < next_count:
            candidate_specs.append(
                (
                    "local_density_minimum_edge",
                    upper_edge,
                    f"Local minimum absolute-distance bin at index {index}.",
                )
            )

    expected = len(rows) / len(absolute_rows)
    adjacent_diffs: list[tuple[int, int, float]] = []
    for index in range(len(absolute_rows) - 1):
        difference = abs(counts[index + 1] - counts[index])
        if difference / expected >= ANOMALY_ABRUPT_DIFF_RATIO_MIN:
            edge = float(absolute_rows[index]["upper_bound_exclusive"])
            adjacent_diffs.append((index, difference, edge))
    for index, difference, edge in sorted(adjacent_diffs, key=lambda item: (-item[1], item[0]))[:5]:
        candidate_specs.append(
            (
                "strong_adjacent_density_change_edge",
                edge,
                (
                    "Strong adjacent absolute-distance count difference at "
                    f"edge after bin {index}; difference={difference}."
                ),
            )
        )

    output_rows: list[dict[str, Any]] = []
    seen_totals: set[int] = set()
    seen_thresholds: set[str] = set()
    for threshold_type, threshold, rationale in candidate_specs:
        key = fmt_float(threshold)
        counts_inside = candidate_counts(rows, threshold)
        status = suitability_status(counts_inside, threshold, seen_totals)
        if key in seen_thresholds and status == "descriptively_viable":
            status = "redundant"
        output_rows.append(
            {
                "candidate_id": f"SHAPIROMART14_CANDIDATE_{len(output_rows) + 1:03d}",
                "threshold_type": threshold_type,
                "threshold_value": fmt_float(threshold),
                "rationale": rationale,
                "total_count_inside": counts_inside["total"],
                "total_fraction_inside": fraction_text(int(counts_inside["total"]), len(rows)),
                "negative_side_count": counts_inside["negative"],
                "positive_side_count": counts_inside["positive"],
                "normalized_imbalance": fmt_float(float(counts_inside["normalized"])),
                "rcvr_800_count": "",
                "rcvr1_2_count": "",
                "minimum_context_count": "",
                "local_density_context": local_density_note(threshold, absolute_rows),
                "stability_note": (
                    "Overall row-level count is available; receiver/backend composition "
                    "requires per-row context not present in allowed SHAPIROMART13 mapping."
                ),
                "suitability_status": status,
                "notes": "Catalogued for later planning only; no threshold is selected.",
            }
        )
        seen_thresholds.add(key)
        seen_totals.add(int(counts_inside["total"]))
    return output_rows


def final_status_value(
    symmetry_rows: list[dict[str, Any]], context_summary_rows: list[dict[str, Any]]
) -> str:
    context_partial = any(
        row["context_coverage_status"] == "summary_only_row_context_unavailable"
        for row in context_summary_rows
    )
    if context_partial:
        return "sampling_symmetry_partially_characterized"
    statuses = {row["symmetry_status"] for row in symmetry_rows}
    if statuses <= {"approximately_balanced", "mildly_imbalanced"}:
        return "sampling_symmetry_characterized"
    return "sampling_symmetry_characterized_with_imbalances"


def build_final_status_row(
    rows: list[dict[str, Any]],
    absolute_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
    symmetry_rows: list[dict[str, Any]],
    context_summary_rows: list[dict[str, Any]],
    anomaly_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    del absolute_rows
    del signed_rows
    final_status = final_status_value(symmetry_rows, context_summary_rows)
    return {
        "research_block": RESEARCH_BLOCK,
        "input_geometry_axis_available": "yes",
        "input_row_count": len(rows),
        "absolute_distance_distribution_completed": "yes",
        "signed_offset_distribution_completed": "yes",
        "symmetry_analysis_completed": "overall_yes_receiver_backend_partial",
        "receiver_backend_symmetry_assessed": "partial",
        "sampling_anomalies_found": "yes" if anomaly_rows else "no",
        "high_severity_sampling_anomalies_found": "yes"
        if any(row["severity"] == "high" for row in anomaly_rows)
        else "no",
        "threshold_candidates_catalogued": "yes" if threshold_rows else "no",
        "exposure_classes_created": "no",
        "threshold_selected": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "model_fit_performed": "no",
        "physical_interpretation_performed": "no",
        "database_access": "none",
        "additional_gate_created": "no",
        "final_status": final_status,
        "recommended_next_action": (
            "For receiver/backend band symmetry, create a separately specified "
            "per-row context-bearing artifact from approved upstream outputs before "
            "any later threshold decision."
        ),
        "limitations": (
            "Receiver/backend side totals and diagnostic bands cannot be recomputed "
            "from the allowed summary context files because the SHAPIROMART13 "
            "mapping does not carry per-row receiver/backend context."
        ),
    }


def top_ranges(
    absolute_rows: list[dict[str, Any]], reverse: bool, limit: int = 3
) -> list[str]:
    eligible = [row for row in absolute_rows if int(row["observed_count"]) > 0]
    sorted_rows = sorted(
        eligible,
        key=lambda row: (int(row["observed_count"]), -int(row["bin_index"])),
        reverse=reverse,
    )
    return [
        f"{range_label(row)} count={row['observed_count']}" for row in sorted_rows[:limit]
    ]


def overall_symmetry_label(symmetry_rows: list[dict[str, Any]]) -> str:
    statuses = [row["symmetry_status"] for row in symmetry_rows]
    if "strongly_imbalanced" in statuses:
        return "strongly_imbalanced_in_at_least_one_band"
    if "moderately_imbalanced" in statuses:
        return "moderately_imbalanced_in_at_least_one_band"
    if "mildly_imbalanced" in statuses:
        return "mildly_imbalanced_in_at_least_one_band"
    return "approximately_balanced_in_all_sufficient_bands"


def strongest_band_imbalance(symmetry_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(symmetry_rows, key=lambda row: float(row["normalized_imbalance"]))


def build_readout(
    rows: list[dict[str, Any]],
    absolute_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
    symmetry_rows: list[dict[str, Any]],
    context_summary_rows: list[dict[str, Any]],
    anomaly_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
    final_status_row: dict[str, Any],
) -> str:
    offsets = [float(row["signed_phase_offset"]) for row in rows]
    distances = [float(row["absolute_phase_distance"]) for row in rows]
    negative_total = sum(1 for value in offsets if value < 0.0)
    positive_total = sum(1 for value in offsets if value > 0.0)
    zero_total = sum(1 for value in offsets if value == 0.0)
    strongest = strongest_band_imbalance(symmetry_rows)

    band_lines = [
        (
            f"- d={row['band_half_width']}: negative={row['negative_side_count']}, "
            f"positive={row['positive_side_count']}, "
            f"normalized_imbalance={row['normalized_imbalance']}, "
            f"status={row['symmetry_status']}"
        )
        for row in symmetry_rows
    ]
    context_lines = [
        (
            f"- {row['context_name']}: n={row['toa_count']}, "
            f"coverage_status={row['context_coverage_status']}, "
            f"median_abs={row['median_absolute_distance']}"
        )
        for row in context_summary_rows
    ]
    anomaly_lines = [
        (
            f"- {row['anomaly_id']}: {row['anomaly_type']} "
            f"({row['severity']}), range={row['affected_range']}"
        )
        for row in anomaly_rows[:10]
    ]

    return "\n".join(
        [
            "# SHAPIROMART14 Readout",
            "",
            "## 1. Purpose",
            (
                "Describe the distribution of absolute phase distance and signed "
                "phase offset relative to superior conjunction, and catalogue "
                "sampling symmetry diagnostics before any later classification."
            ),
            "",
            "## 2. Input Geometry Axis",
            f"Input mapping rows: {len(rows)}.",
            "signed_phase_offset = ((orbital_phase - 0.25 + 0.5) mod 1.0) - 0.5.",
            "absolute_phase_distance = abs(signed_phase_offset).",
            (
                "The negative and positive sides are phase-direction descriptors "
                "only, not spatial distances or effect indicators."
            ),
            "",
            "## 3. Absolute Conjunction-Distance Distribution",
            (
                "Coverage status is descriptive: empty has zero rows; sparse is "
                f"< {fmt_float(COVERAGE_MODERATE_RATIO_MIN)} of the equal-width "
                "reference count; moderate is below the dense cutoff; dense is "
                f">= {fmt_float(COVERAGE_DENSE_RATIO_MIN)} of that reference count."
            ),
            f"Most populated regions: {'; '.join(top_ranges(absolute_rows, True))}.",
            f"Sparsest occupied regions: {'; '.join(top_ranges(absolute_rows, False))}.",
            f"Absolute-distance range: {fmt_float(min(distances))} to {fmt_float(max(distances))}.",
            "",
            "## 4. Signed Offset Distribution",
            (
                f"Overall signed side counts: negative={negative_total}, "
                f"positive={positive_total}, exact_zero={zero_total}."
            ),
            (
                "Mirrored signed bins compare bin i with bin_count - 1 - i. "
                "The bin containing zero is marked as crossing_bin."
            ),
            "",
            "## 5. Overall Sampling Symmetry",
            (
                "Symmetry statuses are descriptive: insufficient_count if side "
                f"total < {SYMMETRY_MIN_TOTAL_COUNT}; approximately_balanced if "
                f"normalized imbalance <= {fmt_float(SYMMETRY_APPROXIMATELY_BALANCED_MAX)}; "
                f"mildly_imbalanced if <= {fmt_float(SYMMETRY_MILD_IMBALANCE_MAX)}; "
                f"moderately_imbalanced if <= {fmt_float(SYMMETRY_MODERATE_IMBALANCE_MAX)}; "
                "otherwise strongly_imbalanced."
            ),
            *band_lines,
            (
                f"Strongest diagnostic band imbalance: d={strongest['band_half_width']}, "
                f"normalized_imbalance={strongest['normalized_imbalance']}, "
                f"status={strongest['symmetry_status']}."
            ),
            "",
            "## 6. Receiver/Backend Symmetry",
            *context_lines,
            (
                "Receiver/backend totals sum to 7419 in the allowed summary "
                "context files. Per-row receiver/backend context is not present in "
                "the allowed SHAPIROMART13 mapping, so receiver/backend side totals "
                "and band symmetry are partially characterized only."
            ),
            "",
            "## 7. Sampling Concentrations and Gaps",
            *anomaly_lines,
            (
                "Possible sampling explanations are recorded only as "
                "compatible_with_targeted_sampling where applicable."
            ),
            "",
            "## 8. Threshold Candidate Inventory",
            (
                f"Catalogued candidates: {len(threshold_rows)}. Sources include "
                "predefined diagnostic bands, empirical nearest-rank quantiles, "
                "local density extrema, and strong adjacent density changes."
            ),
            "Receiver/backend candidate composition is left blank because per-row context is unavailable in the allowed mapping.",
            "",
            "## 9. What Was Not Selected",
            "threshold_selected = no.",
            "exposure_classes_created = no.",
            "shapiro_delay_calculated = no.",
            "residual_analysis_performed = no.",
            "model_fit_performed = no.",
            "physical_interpretation_performed = no.",
            "additional_gate_created = no.",
            "",
            "## 10. Final Status",
            f"final_status = {final_status_row['final_status']}.",
            "",
            "## 11. Recommended Next Action",
            str(final_status_row["recommended_next_action"]),
            "",
            "## 12. Limitations",
            str(final_status_row["limitations"]),
            "",
        ]
    )


def build_summary_json(
    args: argparse.Namespace,
    band_widths: list[float],
    rows: list[dict[str, Any]],
    absolute_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
    symmetry_rows: list[dict[str, Any]],
    context_summary_rows: list[dict[str, Any]],
    anomaly_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
    final_status_row: dict[str, Any],
    status_payload: dict[str, Any],
) -> dict[str, Any]:
    offsets = [float(row["signed_phase_offset"]) for row in rows]
    densest = sorted(
        absolute_rows, key=lambda row: int(row["observed_count"]), reverse=True
    )[:3]
    sparsest = sorted(
        [row for row in absolute_rows if int(row["observed_count"]) > 0],
        key=lambda row: int(row["observed_count"]),
    )[:3]
    strongest = strongest_band_imbalance(symmetry_rows)
    signed_status_counts = Counter(row["symmetry_status"] for row in signed_rows)
    band_status_counts = Counter(row["symmetry_status"] for row in symmetry_rows)
    anomaly_type_counts = Counter(row["anomaly_type"] for row in anomaly_rows)

    return {
        "research_block": RESEARCH_BLOCK,
        "inputs_read": {
            "mapping_input": str(args.mapping_input),
            "phase_distance_qc_input": str(args.phase_distance_qc_input),
            "context_summary_input": str(args.context_summary_input),
            "final_status_input": str(args.final_status_input),
            "summary_json_input": str(args.summary_json_input),
            "context_phase_coverage_input": str(args.context_phase_coverage_input),
            "shapiromart12_final_status_input": str(
                args.shapiromart12_final_status_input
            ),
        },
        "parameters": {
            "absolute_bin_count": args.absolute_bin_count,
            "signed_bin_count": args.signed_bin_count,
            "symmetry_band_widths": [fmt_float(value) for value in band_widths],
            "write_png": bool(args.write_png),
        },
        "input_validation": {
            "expected_row_count": EXPECTED_ROW_COUNT,
            "observed_row_count": len(rows),
            "signed_offsets_finite": True,
            "absolute_distances_finite": True,
            "values_in_range": True,
            "receiver_backend_summary_total": sum(
                int(status_payload["context_by_name"][name]["toa_count"])
                for name in REQUIRED_CONTEXTS[1:]
            ),
            "context_rows_present": REQUIRED_CONTEXTS,
            "per_row_receiver_backend_context_available": False,
        },
        "absolute_distribution": {
            "status": "completed",
            "densest_regions": [
                {"range": range_label(row), "count": row["observed_count"]}
                for row in densest
            ],
            "sparsest_occupied_regions": [
                {"range": range_label(row), "count": row["observed_count"]}
                for row in sparsest
            ],
        },
        "signed_distribution": {
            "status": "completed",
            "negative_side_total": sum(1 for value in offsets if value < 0.0),
            "positive_side_total": sum(1 for value in offsets if value > 0.0),
            "exact_zero_count": sum(1 for value in offsets if value == 0.0),
            "symmetry_status_counts": dict(signed_status_counts),
        },
        "symmetry_bands": {
            "status": "overall_completed_receiver_backend_partial",
            "overall_status": overall_symmetry_label(symmetry_rows),
            "band_status_counts": dict(band_status_counts),
            "strongest_sampling_imbalance": {
                "band_half_width": strongest["band_half_width"],
                "normalized_imbalance": strongest["normalized_imbalance"],
                "symmetry_status": strongest["symmetry_status"],
            },
        },
        "receiver_backend_symmetry": {
            "status": "partial",
            "context_summary": context_summary_rows,
            "limitation": final_status_row["limitations"],
        },
        "sampling_anomalies": {
            "count": len(anomaly_rows),
            "high_severity_count": sum(1 for row in anomaly_rows if row["severity"] == "high"),
            "type_counts": dict(anomaly_type_counts),
        },
        "threshold_candidates": {
            "count": len(threshold_rows),
            "threshold_selected": "no",
            "exposure_classes_created": "no",
        },
        "boundaries": {
            "exposure_classes_created": "no",
            "threshold_selected": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "model_fit_performed": "no",
            "physical_interpretation_performed": "no",
            "database_access": "none",
            "additional_gate_created": "no",
        },
        "final_status": final_status_row,
        "output_dir": str(args.output_dir),
    }


def write_optional_pngs(
    output_dir: Path,
    absolute_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
) -> None:
    try:
        import matplotlib.pyplot as plt  # type: ignore
    except Exception as exc:
        raise RuntimeError("matplotlib is required when --write-png is set.") from exc

    absolute_lefts = [float(row["lower_bound_inclusive"]) for row in absolute_rows]
    absolute_width = float(absolute_rows[0]["upper_bound_exclusive"]) - float(
        absolute_rows[0]["lower_bound_inclusive"]
    )
    absolute_counts = [int(row["observed_count"]) for row in absolute_rows]
    plt.figure()
    plt.bar(absolute_lefts, absolute_counts, width=absolute_width, align="edge")
    plt.xlim(0.0, 0.5)
    plt.xlabel("absolute phase distance to superior conjunction")
    plt.ylabel("TOA count")
    plt.title("J0740+6620 Conjunction-Distance Sampling")
    plt.tight_layout()
    plt.savefig(output_dir / ABSOLUTE_DISTRIBUTION_PNG)
    plt.close()

    signed_lefts = [float(row["lower_bound_inclusive"]) for row in signed_rows]
    signed_width = float(signed_rows[0]["upper_bound_exclusive"]) - float(
        signed_rows[0]["lower_bound_inclusive"]
    )
    signed_counts = [int(row["observed_count"]) for row in signed_rows]
    plt.figure()
    plt.bar(signed_lefts, signed_counts, width=signed_width, align="edge")
    plt.axvline(0.0)
    plt.xlim(-0.5, 0.5)
    plt.xlabel("signed phase offset from superior conjunction")
    plt.ylabel("TOA count")
    plt.title("J0740+6620 Pre/Post-Conjunction Sampling")
    plt.tight_layout()
    plt.savefig(output_dir / SIGNED_DISTRIBUTION_PNG)
    plt.close()


def verify_expected_outputs(output_dir: Path, expected_files: list[str]) -> None:
    observed = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    expected = sorted(expected_files)
    if observed != expected:
        raise RuntimeError(
            f"Output file set mismatch. Expected {expected}, observed {observed}."
        )


def main() -> None:
    args = parse_args()
    if args.absolute_bin_count <= 0:
        raise ValueError("--absolute-bin-count must be positive.")
    if args.signed_bin_count <= 0:
        raise ValueError("--signed-bin-count must be positive.")
    band_widths = parse_band_widths(args.symmetry_band_widths)
    expected_files = list(DEFAULT_OUTPUT_FILES)
    if args.write_png:
        expected_files.extend(PNG_OUTPUT_FILES)
    validate_output_dir(args.output_dir, expected_files, args.overwrite)

    rows = load_and_validate_mapping(args.mapping_input)
    status_payload = validate_status_inputs(
        args.phase_distance_qc_input,
        args.context_summary_input,
        args.final_status_input,
        args.summary_json_input,
        args.context_phase_coverage_input,
        args.shapiromart12_final_status_input,
    )

    absolute_rows = build_absolute_distribution(rows, args.absolute_bin_count)
    signed_rows = build_signed_distribution(rows, args.signed_bin_count)
    symmetry_rows = build_symmetry_band_rows(rows, band_widths)
    context_summary_rows = build_context_summary_rows(rows, status_payload, symmetry_rows)
    anomaly_rows = build_anomaly_inventory(
        absolute_rows, signed_rows, symmetry_rows, len(rows)
    )
    threshold_rows = build_threshold_candidates(rows, absolute_rows)
    final_status_row = build_final_status_row(
        rows,
        absolute_rows,
        signed_rows,
        symmetry_rows,
        context_summary_rows,
        anomaly_rows,
        threshold_rows,
    )
    readout = build_readout(
        rows,
        absolute_rows,
        signed_rows,
        symmetry_rows,
        context_summary_rows,
        anomaly_rows,
        threshold_rows,
        final_status_row,
    )
    summary = build_summary_json(
        args,
        band_widths,
        rows,
        absolute_rows,
        signed_rows,
        symmetry_rows,
        context_summary_rows,
        anomaly_rows,
        threshold_rows,
        final_status_row,
        status_payload,
    )

    write_text(args.output_dir / READOUT_MD, readout)
    write_json(args.output_dir / SUMMARY_JSON, summary)
    write_csv(
        args.output_dir / ABSOLUTE_DISTRIBUTION_CSV,
        absolute_rows,
        ABSOLUTE_DISTRIBUTION_FIELDS,
    )
    write_csv(
        args.output_dir / SIGNED_DISTRIBUTION_CSV,
        signed_rows,
        SIGNED_DISTRIBUTION_FIELDS,
    )
    write_csv(args.output_dir / SYMMETRY_BAND_CSV, symmetry_rows, SYMMETRY_BAND_FIELDS)
    write_csv(
        args.output_dir / CONTEXT_SYMMETRY_CSV,
        context_summary_rows,
        CONTEXT_SYMMETRY_FIELDS,
    )
    write_csv(args.output_dir / ANOMALY_CSV, anomaly_rows, ANOMALY_FIELDS)
    write_csv(
        args.output_dir / THRESHOLD_CANDIDATE_CSV,
        threshold_rows,
        THRESHOLD_CANDIDATE_FIELDS,
    )
    write_csv(args.output_dir / FINAL_STATUS_CSV, [final_status_row], FINAL_STATUS_FIELDS)
    if args.write_png:
        write_optional_pngs(args.output_dir, absolute_rows, signed_rows)

    verify_expected_outputs(args.output_dir, expected_files)


if __name__ == "__main__":
    main()
