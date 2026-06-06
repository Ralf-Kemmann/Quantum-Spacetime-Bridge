#!/usr/bin/env python3
"""QSB-SHAPIROMART12 orbital phase axis quality control.

This script describes and checks the SHAPIROMART11 exported orbital-phase
axis. It reads only SHAPIROMART11 artifacts, performs no model fit, no residual
analysis, no database access, and no physical interpretation.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import math
import statistics
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart12_orbital_phase_axis_qc.py"

SHAPIROMART11_DIR = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART11_CONTROLLED_PINT_RECONSTRUCTION"
)
DEFAULT_PHASE_CSV = SHAPIROMART11_DIR / "shapiromart11_toa_orbital_phase.csv"
DEFAULT_OUTPUT_DIR = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART12_ORBITAL_PHASE_AXIS_QC"
)
DEFAULT_FINAL_STATUS_11 = SHAPIROMART11_DIR / "shapiromart11_final_status.csv"
DEFAULT_PHASE_ASSESSMENT_11 = SHAPIROMART11_DIR / "shapiromart11_orbital_phase_assessment.csv"
DEFAULT_INPUT_IDENTITY_11 = SHAPIROMART11_DIR / "shapiromart11_input_identity.csv"
DEFAULT_SUMMARY_11 = SHAPIROMART11_DIR / "shapiromart11_summary.json"

EXPECTED_ROW_COUNT = 7419
SUPPORTED_CONTEXTS = [
    ("Rcvr_800 / GUPPI", "Rcvr_800", "GUPPI"),
    ("Rcvr1_2 / GUPPI", "Rcvr1_2", "GUPPI"),
]

READOUT_MD = "shapiromart12_readout.md"
SUMMARY_JSON = "shapiromart12_summary.json"
PHASE_AXIS_QC_CSV = "shapiromart12_phase_axis_qc.csv"
PHASE_DISTRIBUTION_CSV = "shapiromart12_phase_distribution.csv"
PHASE_BIN_COUNTS_CSV = "shapiromart12_phase_bin_counts.csv"
CONTEXT_PHASE_COVERAGE_CSV = "shapiromart12_context_phase_coverage.csv"
ANOMALY_INVENTORY_CSV = "shapiromart12_anomaly_inventory.csv"
FINAL_STATUS_CSV = "shapiromart12_final_status.csv"

OUTPUT_FILES = [
    READOUT_MD,
    SUMMARY_JSON,
    PHASE_AXIS_QC_CSV,
    PHASE_DISTRIBUTION_CSV,
    PHASE_BIN_COUNTS_CSV,
    CONTEXT_PHASE_COVERAGE_CSV,
    ANOMALY_INVENTORY_CSV,
    FINAL_STATUS_CSV,
]

PHASE_AXIS_QC_FIELDS = [
    "research_block",
    "input_phase_file",
    "expected_row_count",
    "observed_row_count",
    "valid_phase_count",
    "finite_phase_count",
    "non_finite_phase_count",
    "in_range_phase_count",
    "out_of_range_phase_count",
    "missing_phase_count",
    "unique_source_row_count",
    "duplicate_source_row_count",
    "duplicate_complete_row_count",
    "phase_min",
    "phase_max",
    "phase_mean",
    "phase_median",
    "phase_std",
    "phase_method_consistent",
    "model_name_consistent",
    "tasc_consistent",
    "pb_consistent",
    "qc_status",
    "notes",
]

PHASE_DISTRIBUTION_FIELDS = [
    "distribution_scope",
    "context_name",
    "toa_count",
    "phase_min",
    "phase_max",
    "phase_mean",
    "phase_median",
    "phase_std",
    "occupied_bin_count",
    "empty_bin_count",
    "phase_coverage_fraction",
    "densest_bin_index",
    "densest_bin_count",
    "sparsest_occupied_bin_index",
    "sparsest_occupied_bin_count",
    "maximum_bin_fraction",
    "distribution_status",
    "notes",
]

PHASE_BIN_COUNT_FIELDS = [
    "distribution_scope",
    "context_name",
    "bin_count_total",
    "bin_index",
    "lower_bound_inclusive",
    "upper_bound_exclusive",
    "observed_count",
    "observed_fraction",
    "uniform_reference_count",
    "deviation_from_uniform_count",
    "standardized_deviation",
    "coverage_status",
    "notes",
]

CONTEXT_PHASE_COVERAGE_FIELDS = [
    "context_name",
    "receiver",
    "backend",
    "mapping_status",
    "toa_count",
    "valid_phase_count",
    "occupied_bin_count",
    "empty_bin_count",
    "phase_coverage_fraction",
    "phase_min",
    "phase_max",
    "densest_bin_index",
    "densest_bin_count",
    "sparsest_occupied_bin_index",
    "sparsest_occupied_bin_count",
    "main_gap",
    "notes",
]

ANOMALY_FIELDS = [
    "anomaly_id",
    "anomaly_type",
    "severity",
    "affected_count",
    "affected_fraction",
    "affected_scope",
    "evidence_field",
    "disposition",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "phase_axis_input_available",
    "expected_row_count",
    "observed_row_count",
    "all_phases_finite",
    "all_phases_in_range",
    "source_row_indices_unique",
    "phase_method_consistent",
    "model_name_consistent",
    "tasc_consistent",
    "pb_consistent",
    "overall_phase_coverage_supported",
    "receiver_backend_coverage_assessed",
    "anomalies_found",
    "high_severity_anomalies_found",
    "phase_axis_quality_status",
    "shapiro_interpretation_performed",
    "conjunction_assignment_performed",
    "exposure_classes_created",
    "model_fit_performed",
    "residual_analysis_performed",
    "database_access",
    "additional_gate_created",
    "recommended_next_action",
    "limitations",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    raise RuntimeError(message)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_single_csv_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        fail(f"Expected exactly one row in {path}, found {len(rows)}.")
    return rows[0]


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


def safe_float(value: str) -> float | None:
    if value is None or str(value).strip() == "":
        return None
    try:
        parsed = float(value)
    except Exception:
        return None
    return parsed


def bool_text(value: bool) -> str:
    return "yes" if value else "no"


def fraction(count: int, total: int) -> str:
    if total == 0:
        return "0"
    return f"{count / total:.12g}"


def parse_context(row: dict[str, str]) -> tuple[str, str, str, str]:
    try:
        flags = ast.literal_eval(row.get("source_filename", ""))
        if not isinstance(flags, dict):
            return "", "", "", "unresolved"
    except Exception:
        return "", "", "", "unresolved"
    receiver = str(flags.get("fe", ""))
    backend = str(flags.get("be", ""))
    combined = str(flags.get("f", ""))
    for context_name, supported_receiver, supported_backend in SUPPORTED_CONTEXTS:
        if receiver == supported_receiver and backend == supported_backend:
            return context_name, receiver, backend, "supported"
    if receiver or backend or combined:
        return f"{receiver} / {backend}".strip(" /"), receiver, backend, "unresolved"
    return "", receiver, backend, "unresolved"


def validate_inputs(args: argparse.Namespace) -> dict[str, Any]:
    required = [
        args.phase_csv,
        DEFAULT_FINAL_STATUS_11,
        DEFAULT_PHASE_ASSESSMENT_11,
        DEFAULT_INPUT_IDENTITY_11,
        DEFAULT_SUMMARY_11,
    ]
    for path in required:
        if not path.exists():
            fail(f"Required input is missing: {path}")
    final_11 = read_single_csv_row(DEFAULT_FINAL_STATUS_11)
    phase_assessment_11 = read_single_csv_row(DEFAULT_PHASE_ASSESSMENT_11)
    if final_11.get("final_status") != "orbital_phase_axis_reconstructed":
        fail("SHAPIROMART11 final status does not support phase-axis QC.")
    if final_11.get("orbital_phase_exported") != "yes":
        fail("SHAPIROMART11 phase export is not marked yes.")
    if phase_assessment_11.get("phase_generated") != "yes":
        fail("SHAPIROMART11 phase assessment does not mark phase generation yes.")
    with DEFAULT_SUMMARY_11.open("r", encoding="utf-8") as handle:
        summary_11 = json.load(handle)
    final_status_keys = [
        "research_block",
        "official_pair_used",
        "pint_available",
        "model_loaded",
        "toas_loaded",
        "ell1_model_confirmed",
        "tasc_available",
        "pb_available",
        "model_consistent_time_available",
        "orbital_phase_generated",
        "orbital_phase_exported",
        "final_status",
    ]
    filtered_final_11 = {key: final_11.get(key, "") for key in final_status_keys}
    filtered_summary_status = {
        key: summary_11.get("final_status", {}).get(key, "") for key in final_status_keys
    }
    return {
        "final_status_11": filtered_final_11,
        "phase_assessment_11": phase_assessment_11,
        "input_identity_11": read_csv_rows(DEFAULT_INPUT_IDENTITY_11),
        "summary_11_status": filtered_summary_status,
    }


def ensure_output_targets(output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        files = [path.name for path in output_dir.iterdir() if path.is_file()]
        unexpected = sorted(set(files) - set(OUTPUT_FILES))
        if unexpected:
            fail("Unexpected existing file(s) in output directory: " + "; ".join(unexpected))
        existing = sorted(set(files) & set(OUTPUT_FILES))
        if existing and not overwrite:
            fail(
                "SHAPIROMART12 output file(s) already exist. Re-run with --overwrite "
                "to replace only these files: " + "; ".join(existing)
            )


def coverage_status(count: int, expected: float) -> str:
    if count == 0:
        return "empty"
    if expected <= 0:
        return "sparse"
    if count < 0.25 * expected:
        return "sparse"
    if count < 0.75 * expected:
        return "moderately_populated"
    return "well_populated"


def bin_index(phase: float, bin_count: int) -> int:
    return min(int(phase * bin_count), bin_count - 1)


def numeric_stats(values: list[float]) -> dict[str, str]:
    if not values:
        return {
            "phase_min": "",
            "phase_max": "",
            "phase_mean": "",
            "phase_median": "",
            "phase_std": "",
        }
    return {
        "phase_min": f"{min(values):.17g}",
        "phase_max": f"{max(values):.17g}",
        "phase_mean": f"{statistics.fmean(values):.17g}",
        "phase_median": f"{statistics.median(values):.17g}",
        "phase_std": f"{statistics.pstdev(values):.17g}" if len(values) > 1 else "0",
    }


def distribution_for_values(
    values: list[float], bin_count: int, scope: str, context_name: str
) -> tuple[dict[str, Any], list[dict[str, Any]], list[int]]:
    total = len(values)
    counts = [0 for _ in range(bin_count)]
    for value in values:
        if 0 <= value < 1 and math.isfinite(value):
            counts[bin_index(value, bin_count)] += 1
    expected = total / bin_count if bin_count else 0.0
    bin_rows: list[dict[str, Any]] = []
    for index, count in enumerate(counts):
        lower = index / bin_count
        upper = (index + 1) / bin_count
        deviation = count - expected
        standardized = deviation / math.sqrt(expected) if expected > 0 else 0.0
        bin_rows.append(
            {
                "distribution_scope": scope,
                "context_name": context_name,
                "bin_count_total": bin_count,
                "bin_index": index,
                "lower_bound_inclusive": f"{lower:.12g}",
                "upper_bound_exclusive": f"{upper:.12g}",
                "observed_count": count,
                "observed_fraction": fraction(count, total),
                "uniform_reference_count": f"{expected:.12g}",
                "deviation_from_uniform_count": f"{deviation:.12g}",
                "standardized_deviation": f"{standardized:.12g}",
                "coverage_status": coverage_status(count, expected),
                "notes": "Uniform reference is descriptive only; no significance claim is made.",
            }
        )
    occupied = [idx for idx, count in enumerate(counts) if count > 0]
    densest_count = max(counts) if counts else 0
    densest_index = counts.index(densest_count) if counts else ""
    sparse_pairs = [(idx, counts[idx]) for idx in occupied]
    sparsest_index, sparsest_count = min(sparse_pairs, key=lambda item: item[1]) if sparse_pairs else ("", "")
    stats = numeric_stats(values)
    distribution_status = "coverage_complete" if len(occupied) == bin_count else "coverage_gaps_present"
    row = {
        "distribution_scope": scope,
        "context_name": context_name,
        "toa_count": total,
        "phase_min": stats["phase_min"],
        "phase_max": stats["phase_max"],
        "phase_mean": stats["phase_mean"],
        "phase_median": stats["phase_median"],
        "phase_std": stats["phase_std"],
        "occupied_bin_count": len(occupied),
        "empty_bin_count": bin_count - len(occupied),
        "phase_coverage_fraction": fraction(len(occupied), bin_count),
        "densest_bin_index": densest_index,
        "densest_bin_count": densest_count,
        "sparsest_occupied_bin_index": sparsest_index,
        "sparsest_occupied_bin_count": sparsest_count,
        "maximum_bin_fraction": fraction(densest_count, total),
        "distribution_status": distribution_status,
        "notes": "Descriptive bin coverage over orbital phase [0,1).",
    }
    return row, bin_rows, counts


def anomaly_row(
    anomaly_id: str,
    anomaly_type: str,
    severity: str,
    count: int,
    total: int,
    scope: str,
    field: str,
    disposition: str,
    notes: str,
) -> dict[str, Any]:
    return {
        "anomaly_id": anomaly_id,
        "anomaly_type": anomaly_type,
        "severity": severity,
        "affected_count": count,
        "affected_fraction": fraction(count, total),
        "affected_scope": scope,
        "evidence_field": field,
        "disposition": disposition,
        "notes": notes,
    }


def analyze_rows(rows: list[dict[str, str]], bin_count: int) -> dict[str, Any]:
    observed = len(rows)
    header = list(rows[0].keys()) if rows else []
    required_columns = [
        "source_row_index",
        "source_filename",
        "observatory",
        "observing_frequency_mhz",
        "toa_mjd_file",
        "toa_time_scale",
        "processed_time_value",
        "processed_time_scale",
        "orbital_phase",
        "phase_method",
        "model_name",
        "tasc_value",
        "pb_value",
        "calculation_status",
        "notes",
    ]
    missing_columns = [column for column in required_columns if column not in header]
    if missing_columns:
        fail("Phase CSV is missing required columns: " + "; ".join(missing_columns))

    source_indices: list[int] = []
    unreadable_phase_count = 0
    missing_phase_count = 0
    missing_toa_count = 0
    missing_method_model_count = 0
    finite_values: list[float] = []
    valid_in_range_values: list[float] = []
    non_finite_count = 0
    out_of_range_count = 0
    exact_zero_count = 0
    near_one_count = 0
    parsed_context_rows: list[tuple[dict[str, str], str, str, str, str, float | None]] = []
    parse_context_unresolved_count = 0
    unreadable_source_index_count = 0

    for row in rows:
        try:
            source_indices.append(int(row.get("source_row_index", "")))
        except Exception:
            unreadable_source_index_count += 1
        phase_raw = row.get("orbital_phase", "")
        phase = safe_float(phase_raw)
        if str(phase_raw).strip() == "":
            missing_phase_count += 1
        elif phase is None:
            unreadable_phase_count += 1
        else:
            if not math.isfinite(phase):
                non_finite_count += 1
            else:
                finite_values.append(phase)
                if phase == 0:
                    exact_zero_count += 1
                if phase >= 0.999999:
                    near_one_count += 1
                if 0 <= phase < 1:
                    valid_in_range_values.append(phase)
                else:
                    out_of_range_count += 1
        if not row.get("toa_mjd_file") or not row.get("processed_time_value"):
            missing_toa_count += 1
        if not row.get("phase_method") or not row.get("model_name"):
            missing_method_model_count += 1
        context_name, receiver, backend, status = parse_context(row)
        if status != "supported":
            parse_context_unresolved_count += 1
        parsed_context_rows.append((row, context_name, receiver, backend, status, phase))

    duplicate_source_row_count = observed - len(set(source_indices))
    duplicate_complete_row_count = observed - len(set(tuple(row.get(column, "") for column in header) for row in rows))
    duplicate_phase_count = len(finite_values) - len(set(f"{value:.17g}" for value in finite_values))

    methods = {row.get("phase_method", "") for row in rows if row.get("phase_method", "")}
    models = {row.get("model_name", "") for row in rows if row.get("model_name", "")}
    tascs = {row.get("tasc_value", "") for row in rows if row.get("tasc_value", "")}
    pbs = {row.get("pb_value", "") for row in rows if row.get("pb_value", "")}
    toa_scales = {row.get("toa_time_scale", "") for row in rows if row.get("toa_time_scale", "")}
    processed_scales = {row.get("processed_time_scale", "") for row in rows if row.get("processed_time_scale", "")}

    overall_distribution, overall_bins, overall_counts = distribution_for_values(
        valid_in_range_values, bin_count, "overall", "all_toas"
    )

    distribution_rows = [overall_distribution]
    bin_rows = list(overall_bins)
    context_rows: list[dict[str, Any]] = []
    context_value_map: dict[str, list[float]] = defaultdict(list)
    context_receiver_backend: dict[str, tuple[str, str, str]] = {}
    for _, context_name, receiver, backend, status, phase in parsed_context_rows:
        if status == "supported" and phase is not None and math.isfinite(phase) and 0 <= phase < 1:
            context_value_map[context_name].append(phase)
            context_receiver_backend[context_name] = (receiver, backend, status)

    for context_name, receiver, backend in SUPPORTED_CONTEXTS:
        values = context_value_map.get(context_name, [])
        distribution, context_bins, counts = distribution_for_values(
            values, bin_count, "receiver_backend_context", context_name
        )
        distribution_rows.append(distribution)
        bin_rows.extend(context_bins)
        context_rows.append(
            {
                "context_name": context_name,
                "receiver": receiver,
                "backend": backend,
                "mapping_status": "supported" if values else "unresolved",
                "toa_count": len(values),
                "valid_phase_count": len(values),
                "occupied_bin_count": distribution["occupied_bin_count"],
                "empty_bin_count": distribution["empty_bin_count"],
                "phase_coverage_fraction": distribution["phase_coverage_fraction"],
                "phase_min": distribution["phase_min"],
                "phase_max": distribution["phase_max"],
                "densest_bin_index": distribution["densest_bin_index"],
                "densest_bin_count": distribution["densest_bin_count"],
                "sparsest_occupied_bin_index": distribution["sparsest_occupied_bin_index"],
                "sparsest_occupied_bin_count": distribution["sparsest_occupied_bin_count"],
                "main_gap": "" if values else "No supported rows found for this context in SHAPIROMART11 export.",
                "notes": "Context taken from exported PINT flag dictionary fields fe and be; no DB access.",
            }
        )

    expected_uniform = observed / bin_count if bin_count else 0.0
    empty_bin_count = sum(1 for count in overall_counts if count == 0)
    extreme_concentration_count = sum(
        1
        for count in overall_counts
        if expected_uniform > 0
        and count > 0
        and (count >= 2 * expected_uniform or abs((count - expected_uniform) / math.sqrt(expected_uniform)) >= 3)
    )
    context_gap_count = parse_context_unresolved_count

    all_finite = non_finite_count == 0 and unreadable_phase_count == 0 and missing_phase_count == 0
    all_in_range = out_of_range_count == 0 and len(valid_in_range_values) == len(finite_values)
    indices_unique = duplicate_source_row_count == 0 and unreadable_source_index_count == 0
    method_consistent = len(methods) == 1
    model_consistent = len(models) == 1
    tasc_consistent = len(tascs) == 1
    pb_consistent = len(pbs) == 1
    technical_valid = (
        observed == EXPECTED_ROW_COUNT
        and all_finite
        and all_in_range
        and indices_unique
        and method_consistent
        and model_consistent
        and tasc_consistent
        and pb_consistent
    )

    anomalies: list[dict[str, Any]] = [
        anomaly_row("A001", "missing_values", "high" if missing_phase_count else "info", missing_phase_count, observed, "phase_axis", "orbital_phase", "resolved_if_zero", "Missing orbital_phase values."),
        anomaly_row("A002", "non_finite_values", "high" if non_finite_count else "info", non_finite_count, observed, "phase_axis", "orbital_phase", "resolved_if_zero", "Non-finite orbital_phase values."),
        anomaly_row("A003", "out_of_range_phases", "high" if out_of_range_count else "info", out_of_range_count, observed, "phase_axis", "orbital_phase", "resolved_if_zero", "Values outside 0 <= orbital_phase < 1."),
        anomaly_row("A004", "duplicate_row_indices", "high" if duplicate_source_row_count else "info", duplicate_source_row_count, observed, "phase_axis", "source_row_index", "resolved_if_zero", "Duplicate source_row_index values."),
        anomaly_row("A005", "duplicate_complete_rows", "moderate" if duplicate_complete_row_count else "info", duplicate_complete_row_count, observed, "phase_axis", "complete_row", "documented", "Duplicate complete CSV rows."),
        anomaly_row("A006", "inconsistent_phase_methods", "high" if not method_consistent else "info", observed if not method_consistent else 0, observed, "phase_axis", "phase_method", "resolved_if_zero", f"Observed methods: {sorted(methods)}"),
        anomaly_row("A007", "inconsistent_model_names", "high" if not model_consistent else "info", observed if not model_consistent else 0, observed, "phase_axis", "model_name", "resolved_if_zero", f"Observed model names: {sorted(models)}"),
        anomaly_row("A008", "inconsistent_tasc", "high" if not tasc_consistent else "info", observed if not tasc_consistent else 0, observed, "phase_axis", "tasc_value", "resolved_if_zero", f"Observed TASC values: {sorted(tascs)}"),
        anomaly_row("A009", "inconsistent_pb", "high" if not pb_consistent else "info", observed if not pb_consistent else 0, observed, "phase_axis", "pb_value", "resolved_if_zero", f"Observed PB values: {sorted(pbs)}"),
        anomaly_row("A010", "unexpected_toa_scale_changes", "moderate" if len(toa_scales) != 1 else "info", observed if len(toa_scales) != 1 else 0, observed, "phase_axis", "toa_time_scale", "resolved_if_zero", f"Observed TOA scales: {sorted(toa_scales)}"),
        anomaly_row("A011", "unexpected_processed_time_scale_changes", "moderate" if len(processed_scales) != 1 else "info", observed if len(processed_scales) != 1 else 0, observed, "phase_axis", "processed_time_scale", "resolved_if_zero", f"Observed processed scales: {sorted(processed_scales)}"),
        anomaly_row("A012", "bins_with_zero_coverage", "low" if empty_bin_count else "info", empty_bin_count, bin_count, "overall_distribution", "phase_bin_counts", "documented", "Empty orbital phase bins in the overall descriptive histogram."),
        anomaly_row("A013", "bins_with_extreme_concentration", "moderate" if extreme_concentration_count else "info", extreme_concentration_count, bin_count, "overall_distribution", "phase_bin_counts", "documented", "Bins with count >= 2x uniform reference or standardized deviation magnitude >= 3."),
        anomaly_row("A014", "receiver_backend_context_gaps", "moderate" if context_gap_count else "info", context_gap_count, observed, "receiver_backend_context", "source_filename", "resolved_if_zero", "Rows not mapped to supported receiver/backend contexts from exported flags."),
        anomaly_row("A015", "parsing_anomalies", "high" if unreadable_phase_count or unreadable_source_index_count else "info", unreadable_phase_count + unreadable_source_index_count, observed, "phase_axis", "orbital_phase;source_row_index", "resolved_if_zero", "Unreadable numeric phase values or source row indices."),
        anomaly_row("A016", "missing_toa_values", "high" if missing_toa_count else "info", missing_toa_count, observed, "phase_axis", "toa_mjd_file;processed_time_value", "resolved_if_zero", "Missing TOA or processed time values."),
        anomaly_row("A017", "missing_model_or_method_fields", "high" if missing_method_model_count else "info", missing_method_model_count, observed, "phase_axis", "phase_method;model_name", "resolved_if_zero", "Missing phase method or model name fields."),
        anomaly_row("A018", "duplicate_phase_values", "low" if duplicate_phase_count else "info", duplicate_phase_count, observed, "phase_axis", "orbital_phase", "documented", "Duplicate phase values compared as formatted decimal strings."),
        anomaly_row("A019", "values_numerically_near_one", "info", near_one_count, observed, "phase_axis", "orbital_phase", "documented", "Values with orbital_phase >= 0.999999."),
        anomaly_row("A020", "exact_zero_values", "info", exact_zero_count, observed, "phase_axis", "orbital_phase", "documented", "Values exactly equal to zero."),
    ]
    high_anomalies = [row for row in anomalies if row["severity"] == "high" and int(row["affected_count"]) > 0]
    coverage_anomalies = empty_bin_count > 0 or extreme_concentration_count > 0
    if not technical_valid:
        qc_status = "qc_failed" if high_anomalies else "qc_partial"
    elif coverage_anomalies:
        qc_status = "qc_passed_with_coverage_anomalies"
    else:
        qc_status = "qc_passed"

    stats = numeric_stats(valid_in_range_values)
    qc_row = {
        "research_block": "QSB-SHAPIROMART12",
        "input_phase_file": str(DEFAULT_PHASE_CSV),
        "expected_row_count": EXPECTED_ROW_COUNT,
        "observed_row_count": observed,
        "valid_phase_count": len(valid_in_range_values),
        "finite_phase_count": len(finite_values),
        "non_finite_phase_count": non_finite_count,
        "in_range_phase_count": len(valid_in_range_values),
        "out_of_range_phase_count": out_of_range_count,
        "missing_phase_count": missing_phase_count,
        "unique_source_row_count": len(set(source_indices)),
        "duplicate_source_row_count": duplicate_source_row_count,
        "duplicate_complete_row_count": duplicate_complete_row_count,
        "phase_min": stats["phase_min"],
        "phase_max": stats["phase_max"],
        "phase_mean": stats["phase_mean"],
        "phase_median": stats["phase_median"],
        "phase_std": stats["phase_std"],
        "phase_method_consistent": bool_text(method_consistent),
        "model_name_consistent": bool_text(model_consistent),
        "tasc_consistent": bool_text(tasc_consistent),
        "pb_consistent": bool_text(pb_consistent),
        "qc_status": qc_status,
        "notes": "Technical descriptive QC only; no physical interpretation.",
    }
    final_row = {
        "research_block": "QSB-SHAPIROMART12",
        "phase_axis_input_available": "yes",
        "expected_row_count": EXPECTED_ROW_COUNT,
        "observed_row_count": observed,
        "all_phases_finite": bool_text(all_finite),
        "all_phases_in_range": bool_text(all_in_range),
        "source_row_indices_unique": bool_text(indices_unique),
        "phase_method_consistent": bool_text(method_consistent),
        "model_name_consistent": bool_text(model_consistent),
        "tasc_consistent": bool_text(tasc_consistent),
        "pb_consistent": bool_text(pb_consistent),
        "overall_phase_coverage_supported": "yes" if overall_distribution["occupied_bin_count"] else "no",
        "receiver_backend_coverage_assessed": "yes" if context_gap_count == 0 else "partial",
        "anomalies_found": bool_text(any(int(row["affected_count"]) > 0 for row in anomalies)),
        "high_severity_anomalies_found": bool_text(bool(high_anomalies)),
        "phase_axis_quality_status": qc_status,
        "shapiro_interpretation_performed": "no",
        "conjunction_assignment_performed": "no",
        "exposure_classes_created": "no",
        "model_fit_performed": "no",
        "residual_analysis_performed": "no",
        "database_access": "none",
        "additional_gate_created": "no",
        "recommended_next_action": "Use this QC inventory to decide whether additional descriptive sampling review is needed before any later analysis.",
        "limitations": "Descriptive technical QC only; no physical interpretation, exposure classes, or conjunction assignment.",
    }
    return {
        "qc_row": qc_row,
        "distribution_rows": distribution_rows,
        "bin_rows": bin_rows,
        "context_rows": context_rows,
        "anomaly_rows": anomalies,
        "final_row": final_row,
        "metrics": {
            "observed": observed,
            "finite_phase_fraction": fraction(len(finite_values), observed),
            "in_range_phase_fraction": fraction(len(valid_in_range_values), observed),
            "unique_source_row_fraction": fraction(len(set(source_indices)), observed),
            "occupied_phase_bin_fraction": overall_distribution["phase_coverage_fraction"],
            "maximum_bin_fraction": overall_distribution["maximum_bin_fraction"],
            "minimum_nonzero_bin_fraction": fraction(
                min(count for count in overall_counts if count > 0) if any(overall_counts) else 0,
                observed,
            ),
            "context_specific_occupied_bin_fraction": {
                row["context_name"]: row["phase_coverage_fraction"] for row in context_rows
            },
            "phase_method_values": sorted(methods),
            "model_name_values": sorted(models),
            "tasc_values": sorted(tascs),
            "pb_values": sorted(pbs),
            "empty_bin_count": empty_bin_count,
            "extreme_concentration_bin_count": extreme_concentration_count,
        },
    }


def build_readout(
    timestamp: str,
    args: argparse.Namespace,
    analysis: dict[str, Any],
    input_context: dict[str, Any],
) -> str:
    qc = analysis["qc_row"]
    final = analysis["final_row"]
    overall = analysis["distribution_rows"][0]
    contexts = "\n".join(
        f"- {row['context_name']}: mapping_status={row['mapping_status']}, "
        f"toa_count={row['toa_count']}, occupied_bins={row['occupied_bin_count']}, "
        f"empty_bins={row['empty_bin_count']}"
        for row in analysis["context_rows"]
    )
    anomaly_lines = "\n".join(
        f"- {row['anomaly_id']} {row['anomaly_type']}: severity={row['severity']}, "
        f"affected_count={row['affected_count']}"
        for row in analysis["anomaly_rows"]
        if int(row["affected_count"]) > 0
    )
    return f"""# QSB-SHAPIROMART12 Orbital Phase Axis QC

## 1. Purpose

Describe and check the technical quality and coverage of the SHAPIROMART11
orbital-phase axis for J0740+6620.

## 2. Input Identity

```text
input_phase_file = {args.phase_csv}
expected_row_count = {EXPECTED_ROW_COUNT}
observed_row_count = {qc['observed_row_count']}
timestamp_utc = {timestamp}
```

SHAPIROMART11 status used for boundary control:

```text
final_status = {input_context['final_status_11'].get('final_status', '')}
phase_method = {input_context['phase_assessment_11'].get('phase_method', '')}
phase_zero_definition = ELL1 TASC ascending-node epoch only
```

## 3. Row And Completeness Check

```text
valid_phase_count = {qc['valid_phase_count']}
finite_phase_count = {qc['finite_phase_count']}
missing_phase_count = {qc['missing_phase_count']}
unique_source_row_count = {qc['unique_source_row_count']}
duplicate_source_row_count = {qc['duplicate_source_row_count']}
duplicate_complete_row_count = {qc['duplicate_complete_row_count']}
```

## 4. Phase Range And Numeric Validity

```text
phase_min = {qc['phase_min']}
phase_max = {qc['phase_max']}
phase_mean = {qc['phase_mean']}
phase_median = {qc['phase_median']}
phase_std = {qc['phase_std']}
all_phases_in_range = {final['all_phases_in_range']}
```

## 5. Overall Phase Distribution

The range [0,1) was divided into {args.bin_count} equal-width bins. Coverage
status thresholds are: empty when count is 0; sparse when count is below 25%
of the descriptive uniform reference; moderately_populated when count is below
75% of that reference; well_populated otherwise. Bins with count at least 2x
the uniform reference or standardized deviation magnitude at least 3 are listed
as descriptive concentration findings only.

```text
occupied_bin_count = {overall['occupied_bin_count']}
empty_bin_count = {overall['empty_bin_count']}
phase_coverage_fraction = {overall['phase_coverage_fraction']}
densest_bin_index = {overall['densest_bin_index']}
densest_bin_count = {overall['densest_bin_count']}
sparsest_occupied_bin_index = {overall['sparsest_occupied_bin_index']}
sparsest_occupied_bin_count = {overall['sparsest_occupied_bin_count']}
```

## 6. Receiver/Backend Phase Coverage

{contexts}

Context mapping was read from exported PINT flag dictionaries (`fe` and `be`)
and limited to the documented contexts Rcvr_800/GUPPI and Rcvr1_2/GUPPI.

## 7. Technical Anomaly Inventory

{anomaly_lines if anomaly_lines else 'No nonzero technical anomaly rows.'}

## 8. Quality-Control Result

```text
phase_axis_quality_status = {final['phase_axis_quality_status']}
anomalies_found = {final['anomalies_found']}
high_severity_anomalies_found = {final['high_severity_anomalies_found']}
additional_gate_created = no
```

## 9. What This Does Not Establish

This QC does not assign phase 0 to conjunction, does not create exposure
classes, does not compute Shapiro delay, does not run residual analysis, does
not fit or modify the timing model, and does not make a physical interpretation
of phase coverage.

## 10. Recommended Next Action

{final['recommended_next_action']}

## 11. Limitations

{final['limitations']}
"""


def run(args: argparse.Namespace) -> dict[str, Any]:
    if args.bin_count <= 0:
        fail("--bin-count must be positive.")
    input_context = validate_inputs(args)
    ensure_output_targets(args.output_dir, args.overwrite)
    rows = read_csv_rows(args.phase_csv)
    analysis = analyze_rows(rows, args.bin_count)
    timestamp = utc_now()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / PHASE_AXIS_QC_CSV, [analysis["qc_row"]], PHASE_AXIS_QC_FIELDS)
    write_csv(args.output_dir / PHASE_DISTRIBUTION_CSV, analysis["distribution_rows"], PHASE_DISTRIBUTION_FIELDS)
    write_csv(args.output_dir / PHASE_BIN_COUNTS_CSV, analysis["bin_rows"], PHASE_BIN_COUNT_FIELDS)
    write_csv(args.output_dir / CONTEXT_PHASE_COVERAGE_CSV, analysis["context_rows"], CONTEXT_PHASE_COVERAGE_FIELDS)
    write_csv(args.output_dir / ANOMALY_INVENTORY_CSV, analysis["anomaly_rows"], ANOMALY_FIELDS)
    write_csv(args.output_dir / FINAL_STATUS_CSV, [analysis["final_row"]], FINAL_STATUS_FIELDS)
    readout = build_readout(timestamp, args, analysis, input_context)
    (args.output_dir / READOUT_MD).write_text(readout, encoding="utf-8")
    summary = {
        "research_block": "QSB-SHAPIROMART12",
        "script": SCRIPT_NAME,
        "timestamp_utc": timestamp,
        "input_phase_file": str(args.phase_csv),
        "output_dir": str(args.output_dir),
        "bin_count": args.bin_count,
        "coverage_thresholds": {
            "empty": "count == 0",
            "sparse": "0 < count < 0.25 * uniform_reference_count",
            "moderately_populated": "0.25 * reference <= count < 0.75 * reference",
            "well_populated": "count >= 0.75 * reference",
            "descriptive_concentration": "count >= 2 * reference or abs(standardized_deviation) >= 3",
        },
        "inputs": input_context,
        "phase_axis_qc": analysis["qc_row"],
        "phase_distribution": analysis["distribution_rows"],
        "context_phase_coverage": analysis["context_rows"],
        "metrics": analysis["metrics"],
        "final_status": analysis["final_row"],
        "boundaries": {
            "shapiro_interpretation_performed": "no",
            "conjunction_assignment_performed": "no",
            "exposure_classes_created": "no",
            "model_fit_performed": "no",
            "residual_analysis_performed": "no",
            "database_access": "none",
            "additional_gate_created": "no",
        },
    }
    write_json(args.output_dir / SUMMARY_JSON, summary)
    return {
        "result": analysis["final_row"]["phase_axis_quality_status"],
        "observed_row_count": analysis["qc_row"]["observed_row_count"],
        "finite_phase_count": analysis["qc_row"]["finite_phase_count"],
        "in_range_phase_count": analysis["qc_row"]["in_range_phase_count"],
        "output_dir": str(args.output_dir),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Describe and quality-check the SHAPIROMART11 orbital phase axis."
    )
    parser.add_argument("--phase-csv", type=Path, default=DEFAULT_PHASE_CSV)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--bin-count", type=int, default=20)
    parser.add_argument("--receiver-context-input", type=Path, default=None)
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
