#!/usr/bin/env python3
"""QSB-SHAPIROMART16 context-enriched sampling symmetry analysis.

Reads the SHAPIROMART15 enriched row-level geometry and the SHAPIROMART14
diagnostic bins, bands, and candidate inventory. Produces descriptive
receiver/backend context summaries only. No threshold is selected, no exposure
classes are created, and no Shapiro, residual, fit, physical, raw-data, or
database analysis is performed.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


RESEARCH_BLOCK = "QSB-SHAPIROMART16"
EXPECTED_ROW_COUNT = 7419
EXPECTED_RCVR_800_COUNT = 2916
EXPECTED_RCVR1_2_COUNT = 4503
EXPECTED_CANDIDATE_COUNT = 27

SHAPIROMART_BASE = Path("runs/QSB-SHAPIROMART")
DEFAULT_ENRICHED_INPUT = (
    SHAPIROMART_BASE
    / "SHAPIROMART15_ROW_LEVEL_CONTEXT_ENRICHMENT"
    / "shapiromart15_enriched_phase_geometry.csv"
)
DEFAULT_SHAPIROMART14_DIR = (
    SHAPIROMART_BASE / "SHAPIROMART14_CONJUNCTION_DISTANCE_SAMPLING_SYMMETRY"
)
DEFAULT_SHAPIROMART15_DIR = SHAPIROMART_BASE / "SHAPIROMART15_ROW_LEVEL_CONTEXT_ENRICHMENT"
DEFAULT_OUTPUT_DIR = (
    SHAPIROMART_BASE / "SHAPIROMART16_CONTEXT_ENRICHED_SAMPLING_SYMMETRY"
)

READOUT_MD = "shapiromart16_readout.md"
SUMMARY_JSON = "shapiromart16_summary.json"
CONTEXT_ABSOLUTE_CSV = "shapiromart16_context_absolute_distance_distribution.csv"
CONTEXT_SIGNED_CSV = "shapiromart16_context_signed_offset_distribution.csv"
CONTEXT_BAND_CSV = "shapiromart16_context_symmetry_band_summary.csv"
CONTEXT_CONTRIBUTION_CSV = "shapiromart16_context_asymmetry_contribution.csv"
THRESHOLD_REANALYSIS_CSV = "shapiromart16_threshold_candidate_context_reanalysis.csv"
ANOMALY_CSV = "shapiromart16_context_sampling_anomaly_inventory.csv"
FINAL_STATUS_CSV = "shapiromart16_final_status.csv"

OUTPUT_FILES = [
    READOUT_MD,
    SUMMARY_JSON,
    CONTEXT_ABSOLUTE_CSV,
    CONTEXT_SIGNED_CSV,
    CONTEXT_BAND_CSV,
    CONTEXT_CONTRIBUTION_CSV,
    THRESHOLD_REANALYSIS_CSV,
    ANOMALY_CSV,
    FINAL_STATUS_CSV,
]

CONTEXTS = ["overall", "Rcvr_800 / GUPPI", "Rcvr1_2 / GUPPI"]
ROW_CONTEXTS = ["Rcvr_800 / GUPPI", "Rcvr1_2 / GUPPI"]
EXPECTED_CONTEXT_COUNTS = {
    "overall": EXPECTED_ROW_COUNT,
    "Rcvr_800 / GUPPI": EXPECTED_RCVR_800_COUNT,
    "Rcvr1_2 / GUPPI": EXPECTED_RCVR1_2_COUNT,
}
EXPECTED_BANDS = [0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25]

ENRICHED_REQUIRED_FIELDS = [
    "source_row_index",
    "orbital_phase",
    "signed_phase_offset",
    "absolute_phase_distance",
    "receiver",
    "backend",
    "context_name",
    "context_mapping_status",
]

CONTEXT_ABSOLUTE_FIELDS = [
    "context_name",
    "bin_count_total",
    "bin_index",
    "lower_bound_inclusive",
    "upper_bound_exclusive",
    "observed_count",
    "observed_fraction_of_context",
    "observed_fraction_of_overall",
    "cumulative_count",
    "cumulative_fraction",
    "density_per_phase_unit",
    "negative_side_count",
    "positive_side_count",
    "context_share_of_bin",
    "coverage_status",
    "notes",
]

CONTEXT_SIGNED_FIELDS = [
    "context_name",
    "bin_count_total",
    "bin_index",
    "lower_bound_inclusive",
    "upper_bound_exclusive",
    "midpoint",
    "side",
    "observed_count",
    "observed_fraction_of_context",
    "mirrored_bin_index",
    "mirrored_count",
    "count_difference",
    "absolute_count_difference",
    "normalized_imbalance",
    "symmetry_status",
    "context_share_of_bin",
    "notes",
]

CONTEXT_BAND_FIELDS = [
    "context_name",
    "band_half_width",
    "negative_side_count",
    "positive_side_count",
    "exact_zero_count",
    "total_in_band",
    "fraction_of_context",
    "fraction_of_overall_band",
    "count_difference",
    "absolute_count_difference",
    "negative_to_positive_ratio",
    "normalized_imbalance",
    "minimum_side_fraction",
    "minimum_side_count",
    "context_dominance_fraction",
    "symmetry_status",
    "notes",
]

CONTEXT_CONTRIBUTION_FIELDS = [
    "analysis_type",
    "band_or_bin_id",
    "lower_bound",
    "upper_bound",
    "overall_count_difference",
    "rcvr_800_count_difference",
    "rcvr1_2_count_difference",
    "rcvr_800_contribution_fraction",
    "rcvr1_2_contribution_fraction",
    "contribution_direction_match",
    "dominant_context",
    "contribution_status",
    "notes",
]

THRESHOLD_REANALYSIS_FIELDS = [
    "candidate_id",
    "threshold_type",
    "threshold_value",
    "overall_count_inside",
    "rcvr_800_count_inside",
    "rcvr1_2_count_inside",
    "rcvr_800_fraction_inside",
    "rcvr1_2_fraction_inside",
    "rcvr_800_negative_count",
    "rcvr_800_positive_count",
    "rcvr1_2_negative_count",
    "rcvr1_2_positive_count",
    "rcvr_800_normalized_imbalance",
    "rcvr1_2_normalized_imbalance",
    "minimum_context_count",
    "minimum_side_count",
    "context_dominance_ratio",
    "context_mix_status",
    "candidate_stability_status",
    "threshold_selected",
    "notes",
]

ANOMALY_FIELDS = [
    "anomaly_id",
    "anomaly_type",
    "severity",
    "context_name",
    "affected_band_or_bin",
    "affected_count",
    "affected_fraction",
    "evidence_basis",
    "sampling_status",
    "disposition",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "enriched_context_input_available",
    "enriched_row_count",
    "expected_row_count",
    "rcvr_800_count",
    "rcvr1_2_count",
    "context_counts_match",
    "context_absolute_distribution_completed",
    "context_signed_distribution_completed",
    "context_symmetry_bands_completed",
    "asymmetry_contribution_completed",
    "threshold_candidates_reanalyzed",
    "threshold_candidate_count",
    "overall_asymmetry_context_explained",
    "context_dominance_found",
    "high_severity_sampling_anomalies_found",
    "threshold_selected",
    "exposure_classes_created",
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

COVERAGE_DENSE_RATIO_MIN = 1.25
COVERAGE_MODERATE_RATIO_MIN = 0.50
SYMMETRY_MIN_SIDE_TOTAL = 20
SYMMETRY_APPROXIMATELY_BALANCED_MAX = 0.10
SYMMETRY_MILD_IMBALANCE_MAX = 0.25
SYMMETRY_MODERATE_IMBALANCE_MAX = 0.50
CONTEXT_DOMINANCE_MILD = 0.60
CONTEXT_DOMINANCE_MODERATE = 0.70
CONTEXT_DOMINANCE_STRONG = 0.80
CANDIDATE_MIN_CONTEXT_COUNT = 20
CANDIDATE_MIN_SIDE_COUNT = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Reanalyze SHAPIROMART14 sampling symmetry with SHAPIROMART15 row-level context."
    )
    parser.add_argument("--enriched-input", type=Path, default=DEFAULT_ENRICHED_INPUT)
    parser.add_argument("--shapiromart14-dir", type=Path, default=DEFAULT_SHAPIROMART14_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--shapiromart15-dir",
        type=Path,
        default=DEFAULT_SHAPIROMART15_DIR,
        help="Directory containing SHAPIROMART15 validation artifacts.",
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def fmt_float(value: float) -> str:
    if not math.isfinite(value):
        return str(value)
    return format(value, ".17g")


def fraction_text(count: int, total: int) -> str:
    if total <= 0:
        return "0"
    return format(count / total, ".12g")


def float_fraction_text(value: float) -> str:
    if not math.isfinite(value):
        return ""
    return format(value, ".12g")


def ratio_text(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "inf" if numerator > 0 else ""
    return format(numerator / denominator, ".12g")


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def read_single_csv_row(path: Path) -> dict[str, str]:
    rows, _ = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, observed {len(rows)}.")
    return rows[0]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
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


def validate_output_dir(output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        present = sorted(path.name for path in output_dir.iterdir() if path.is_file())
        if present and not overwrite:
            raise FileExistsError(
                f"Output directory already contains files; use --overwrite: {output_dir}"
            )
        unexpected = sorted(set(present) - set(OUTPUT_FILES))
        if unexpected:
            raise FileExistsError(
                f"Output directory contains files outside the expected set: {unexpected}"
            )
    output_dir.mkdir(parents=True, exist_ok=True)


def require_fields(rows: list[dict[str, str]], fields: list[str], path: Path) -> None:
    if not rows:
        raise ValueError(f"Input has no rows: {path}")
    missing = sorted(set(fields) - set(rows[0].keys()))
    if missing:
        raise ValueError(f"Missing required fields in {path}: {missing}")


def validate_upstream_status(sh15_dir: Path, sh14_dir: Path) -> dict[str, Any]:
    sh15_final = read_single_csv_row(sh15_dir / "shapiromart15_final_status.csv")
    sh15_counts, _ = read_csv_rows(sh15_dir / "shapiromart15_context_count_validation.csv")
    sh15_join = read_single_csv_row(sh15_dir / "shapiromart15_join_key_assessment.csv")
    sh15_summary = read_json(sh15_dir / "shapiromart15_summary.json")
    sh14_final = read_single_csv_row(sh14_dir / "shapiromart14_final_status.csv")
    sh14_summary = read_json(sh14_dir / "shapiromart14_summary.json")

    expected_sh15 = {
        "enriched_row_count": str(EXPECTED_ROW_COUNT),
        "unmatched_row_count": "0",
        "ambiguous_row_count": "0",
        "rcvr_800_count": str(EXPECTED_RCVR_800_COUNT),
        "rcvr1_2_count": str(EXPECTED_RCVR1_2_COUNT),
        "context_totals_match": "yes",
        "receiver_backend_context_complete": "yes",
        "threshold_selected": "no",
        "exposure_classes_created": "no",
        "database_access": "none",
        "additional_gate_created": "no",
        "final_status": "row_level_context_enrichment_complete",
    }
    failures = {
        key: {"expected": value, "observed": sh15_final.get(key, "")}
        for key, value in expected_sh15.items()
        if sh15_final.get(key, "") != value
    }
    if failures:
        raise ValueError(f"SHAPIROMART15 final-status validation failed: {failures}")
    if sh15_join.get("join_status", "") != "complete_unique_match":
        raise ValueError("SHAPIROMART15 join key is not complete_unique_match.")
    if sh15_join.get("left_unique", "") != "yes" or sh15_join.get("right_unique", "") != "yes":
        raise ValueError("SHAPIROMART15 join key uniqueness validation failed.")
    if any(row.get("count_match", "") != "yes" for row in sh15_counts):
        raise ValueError("SHAPIROMART15 context count validation contains a mismatch.")

    expected_sh14 = {
        "input_row_count": str(EXPECTED_ROW_COUNT),
        "threshold_candidates_catalogued": "yes",
        "threshold_selected": "no",
        "exposure_classes_created": "no",
        "database_access": "none",
        "additional_gate_created": "no",
    }
    sh14_failures = {
        key: {"expected": value, "observed": sh14_final.get(key, "")}
        for key, value in expected_sh14.items()
        if sh14_final.get(key, "") != value
    }
    if sh14_failures:
        raise ValueError(f"SHAPIROMART14 final-status validation failed: {sh14_failures}")

    return {
        "shapiromart15_final": sh15_final,
        "shapiromart15_join": sh15_join,
        "shapiromart15_counts": sh15_counts,
        "shapiromart15_summary": sh15_summary,
        "shapiromart14_final": sh14_final,
        "shapiromart14_summary": sh14_summary,
    }


def load_enriched_rows(path: Path) -> list[dict[str, Any]]:
    rows, _ = read_csv_rows(path)
    require_fields(rows, ENRICHED_REQUIRED_FIELDS, path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"Expected {EXPECTED_ROW_COUNT} enriched rows, observed {len(rows)}.")

    parsed: list[dict[str, Any]] = []
    status_counts = Counter(row["context_mapping_status"] for row in rows)
    if set(status_counts) != {"mapped"}:
        raise ValueError(f"Unexpected context_mapping_status values: {dict(status_counts)}")
    for row in rows:
        context = row["context_name"]
        if context not in ROW_CONTEXTS:
            raise ValueError(f"Unexpected context_name in enriched input: {context}")
        receiver_backend = (row["receiver"], row["backend"])
        expected = ("Rcvr_800", "GUPPI") if context == "Rcvr_800 / GUPPI" else ("Rcvr1_2", "GUPPI")
        if receiver_backend != expected:
            raise ValueError(
                f"Receiver/backend mismatch for context {context}: {receiver_backend}"
            )
        signed = float(row["signed_phase_offset"])
        absolute = float(row["absolute_phase_distance"])
        if not (math.isfinite(signed) and -0.5 <= signed < 0.5):
            raise ValueError(f"Invalid signed offset at source_row_index={row['source_row_index']}")
        if not (math.isfinite(absolute) and 0.0 <= absolute <= 0.5):
            raise ValueError(
                f"Invalid absolute distance at source_row_index={row['source_row_index']}"
            )
        parsed_row = dict(row)
        parsed_row["_signed"] = signed
        parsed_row["_absolute"] = absolute
        parsed.append(parsed_row)

    counts = Counter(row["context_name"] for row in parsed)
    if counts.get("Rcvr_800 / GUPPI", 0) != EXPECTED_RCVR_800_COUNT:
        raise ValueError("Rcvr_800 / GUPPI enriched count mismatch.")
    if counts.get("Rcvr1_2 / GUPPI", 0) != EXPECTED_RCVR1_2_COUNT:
        raise ValueError("Rcvr1_2 / GUPPI enriched count mismatch.")
    return parsed


def load_absolute_bins(sh14_dir: Path) -> list[dict[str, Any]]:
    rows, _ = read_csv_rows(sh14_dir / "shapiromart14_absolute_distance_distribution.csv")
    if len(rows) != 20:
        raise ValueError("SHAPIROMART14 absolute distribution must contain 20 bins.")
    bins: list[dict[str, Any]] = []
    for row in rows:
        if row["context_name"] != "overall":
            raise ValueError("SHAPIROMART14 absolute bins must be overall rows.")
        bins.append(
            {
                "bin_index": int(row["bin_index"]),
                "lower": float(row["lower_bound_inclusive"]),
                "upper": float(row["upper_bound_exclusive"]),
                "overall_count": int(row["observed_count"]),
                "coverage_status": row["coverage_status"],
            }
        )
    if [row["bin_index"] for row in bins] != list(range(20)):
        raise ValueError("SHAPIROMART14 absolute bin indexes are not 0..19.")
    return bins


def load_signed_bins(sh14_dir: Path) -> list[dict[str, Any]]:
    rows, _ = read_csv_rows(sh14_dir / "shapiromart14_signed_offset_distribution.csv")
    if len(rows) != 20:
        raise ValueError("SHAPIROMART14 signed distribution must contain 20 bins.")
    bins: list[dict[str, Any]] = []
    for row in rows:
        if row["context_name"] != "overall":
            raise ValueError("SHAPIROMART14 signed bins must be overall rows.")
        bins.append(
            {
                "bin_index": int(row["bin_index"]),
                "lower": float(row["lower_bound_inclusive"]),
                "upper": float(row["upper_bound_exclusive"]),
                "midpoint": float(row["midpoint"]),
                "side": row["side"],
                "mirrored_bin_index": int(row["mirrored_bin_index"]),
                "overall_count": int(row["observed_count"]),
            }
        )
    if [row["bin_index"] for row in bins] != list(range(20)):
        raise ValueError("SHAPIROMART14 signed bin indexes are not 0..19.")
    return bins


def load_bands(sh14_dir: Path) -> list[float]:
    rows, _ = read_csv_rows(sh14_dir / "shapiromart14_symmetry_band_summary.csv")
    bands = [float(row["band_half_width"]) for row in rows if row["context_name"] == "overall"]
    if len(bands) != len(EXPECTED_BANDS):
        raise ValueError("SHAPIROMART14 symmetry band count mismatch.")
    for observed, expected in zip(bands, EXPECTED_BANDS):
        if not math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-12):
            raise ValueError(f"Unexpected SHAPIROMART14 band width: {observed}")
    return bands


def load_threshold_candidates(sh14_dir: Path) -> list[dict[str, str]]:
    rows, _ = read_csv_rows(sh14_dir / "shapiromart14_threshold_candidate_inventory.csv")
    if len(rows) != EXPECTED_CANDIDATE_COUNT:
        raise ValueError(
            f"Expected {EXPECTED_CANDIDATE_COUNT} threshold candidates, observed {len(rows)}."
        )
    return rows


def context_rows(rows: list[dict[str, Any]], context: str) -> list[dict[str, Any]]:
    if context == "overall":
        return rows
    return [row for row in rows if row["context_name"] == context]


def bin_index(value: float, bins: list[dict[str, Any]]) -> int:
    for index, row in enumerate(bins):
        lower = row["lower"]
        upper = row["upper"]
        if lower <= value < upper or (index == len(bins) - 1 and math.isclose(value, upper)):
            return index
    raise ValueError(f"Value outside bin definitions: {value}")


def classify_coverage(count: int, context_total: int, bin_count: int) -> str:
    if count == 0:
        return "empty"
    expected = context_total / bin_count
    ratio = count / expected if expected else 0.0
    if ratio >= COVERAGE_DENSE_RATIO_MIN:
        return "dense"
    if ratio >= COVERAGE_MODERATE_RATIO_MIN:
        return "moderate"
    return "sparse"


def classify_symmetry(negative_count: int, positive_count: int) -> str:
    side_total = negative_count + positive_count
    if side_total < SYMMETRY_MIN_SIDE_TOTAL:
        return "insufficient_count"
    imbalance = abs(negative_count - positive_count) / max(side_total, 1)
    if imbalance <= SYMMETRY_APPROXIMATELY_BALANCED_MAX:
        return "approximately_balanced"
    if imbalance <= SYMMETRY_MILD_IMBALANCE_MAX:
        return "mildly_imbalanced"
    if imbalance <= SYMMETRY_MODERATE_IMBALANCE_MAX:
        return "moderately_imbalanced"
    return "strongly_imbalanced"


def context_mix_status(dominance_ratio: float) -> str:
    if dominance_ratio < CONTEXT_DOMINANCE_MILD:
        return "balanced_context_mix"
    if dominance_ratio < CONTEXT_DOMINANCE_MODERATE:
        return "mild_context_dominance"
    if dominance_ratio < CONTEXT_DOMINANCE_STRONG:
        return "moderate_context_dominance"
    return "strong_context_dominance"


def build_absolute_distribution(
    rows: list[dict[str, Any]], bins: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    overall_counts = [0 for _ in bins]
    for row in rows:
        overall_counts[bin_index(float(row["_absolute"]), bins)] += 1

    output: list[dict[str, Any]] = []
    for context in CONTEXTS:
        selected = context_rows(rows, context)
        context_total = len(selected)
        counts = [0 for _ in bins]
        negative_counts = [0 for _ in bins]
        positive_counts = [0 for _ in bins]
        for row in selected:
            idx = bin_index(float(row["_absolute"]), bins)
            counts[idx] += 1
            if float(row["_signed"]) < 0.0:
                negative_counts[idx] += 1
            elif float(row["_signed"]) > 0.0:
                positive_counts[idx] += 1
        cumulative = 0
        for idx, bin_row in enumerate(bins):
            count = counts[idx]
            width = bin_row["upper"] - bin_row["lower"]
            cumulative += count
            output.append(
                {
                    "context_name": context,
                    "bin_count_total": len(bins),
                    "bin_index": idx,
                    "lower_bound_inclusive": fmt_float(bin_row["lower"]),
                    "upper_bound_exclusive": fmt_float(bin_row["upper"]),
                    "observed_count": count,
                    "observed_fraction_of_context": fraction_text(count, context_total),
                    "observed_fraction_of_overall": fraction_text(count, len(rows)),
                    "cumulative_count": cumulative,
                    "cumulative_fraction": fraction_text(cumulative, context_total),
                    "density_per_phase_unit": fmt_float(count / width),
                    "negative_side_count": negative_counts[idx],
                    "positive_side_count": positive_counts[idx],
                    "context_share_of_bin": float_fraction_text(
                        count / max(overall_counts[idx], 1)
                    ),
                    "coverage_status": classify_coverage(count, context_total, len(bins)),
                    "notes": "Uses SHAPIROMART14 absolute bin boundaries without changing them.",
                }
            )
    return output


def build_signed_distribution(
    rows: list[dict[str, Any]], bins: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    overall_counts = [0 for _ in bins]
    for row in rows:
        overall_counts[bin_index(float(row["_signed"]), bins)] += 1

    output: list[dict[str, Any]] = []
    for context in CONTEXTS:
        selected = context_rows(rows, context)
        context_total = len(selected)
        counts = [0 for _ in bins]
        for row in selected:
            counts[bin_index(float(row["_signed"]), bins)] += 1
        for idx, bin_row in enumerate(bins):
            mirrored_idx = int(bin_row["mirrored_bin_index"])
            count = counts[idx]
            mirrored = counts[mirrored_idx]
            diff = count - mirrored
            normalized = abs(diff) / max(count + mirrored, 1)
            output.append(
                {
                    "context_name": context,
                    "bin_count_total": len(bins),
                    "bin_index": idx,
                    "lower_bound_inclusive": fmt_float(bin_row["lower"]),
                    "upper_bound_exclusive": fmt_float(bin_row["upper"]),
                    "midpoint": fmt_float(bin_row["midpoint"]),
                    "side": bin_row["side"],
                    "observed_count": count,
                    "observed_fraction_of_context": fraction_text(count, context_total),
                    "mirrored_bin_index": mirrored_idx,
                    "mirrored_count": mirrored,
                    "count_difference": diff,
                    "absolute_count_difference": abs(diff),
                    "normalized_imbalance": fmt_float(normalized),
                    "symmetry_status": classify_symmetry(count, mirrored),
                    "context_share_of_bin": float_fraction_text(
                        count / max(overall_counts[idx], 1)
                    ),
                    "notes": "Uses the SHAPIROMART14 signed-bin mirror rule unchanged.",
                }
            )
    return output


def band_counts(selected: list[dict[str, Any]], width: float) -> dict[str, int]:
    negative = sum(1 for row in selected if -width <= float(row["_signed"]) < 0.0)
    positive = sum(1 for row in selected if 0.0 < float(row["_signed"]) <= width)
    exact_zero = sum(1 for row in selected if float(row["_signed"]) == 0.0)
    return {
        "negative": negative,
        "positive": positive,
        "exact_zero": exact_zero,
        "total": negative + positive + exact_zero,
    }


def build_band_summary(rows: list[dict[str, Any]], bands: list[float]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    band_context_totals: dict[float, dict[str, int]] = {}
    for width in bands:
        band_context_totals[width] = {
            context: band_counts(context_rows(rows, context), width)["total"]
            for context in ROW_CONTEXTS
        }
    for context in CONTEXTS:
        selected = context_rows(rows, context)
        context_total = len(selected)
        for width in bands:
            counts = band_counts(selected, width)
            side_total = counts["negative"] + counts["positive"]
            diff = counts["negative"] - counts["positive"]
            normalized = abs(diff) / max(side_total, 1)
            min_side = min(counts["negative"], counts["positive"])
            row_context_totals = band_context_totals[width]
            overall_band_total = sum(row_context_totals.values())
            dominance_fraction = (
                1.0
                if context == "overall"
                else counts["total"] / max(overall_band_total, 1)
            )
            output.append(
                {
                    "context_name": context,
                    "band_half_width": fmt_float(width),
                    "negative_side_count": counts["negative"],
                    "positive_side_count": counts["positive"],
                    "exact_zero_count": counts["exact_zero"],
                    "total_in_band": counts["total"],
                    "fraction_of_context": fraction_text(counts["total"], context_total),
                    "fraction_of_overall_band": float_fraction_text(
                        counts["total"] / max(overall_band_total, 1)
                    ),
                    "count_difference": diff,
                    "absolute_count_difference": abs(diff),
                    "negative_to_positive_ratio": ratio_text(
                        counts["negative"], counts["positive"]
                    ),
                    "normalized_imbalance": fmt_float(normalized),
                    "minimum_side_fraction": float_fraction_text(
                        min_side / max(side_total, 1)
                    ),
                    "minimum_side_count": min_side,
                    "context_dominance_fraction": float_fraction_text(dominance_fraction),
                    "symmetry_status": classify_symmetry(
                        counts["negative"], counts["positive"]
                    ),
                    "notes": "Diagnostic band only; no threshold is selected.",
                }
            )
    return output


def direction_label(overall_diff: int, diff_800: int, diff_12: int) -> str:
    if overall_diff == 0:
        return "no_overall_direction"
    sign = 1 if overall_diff > 0 else -1
    signs = []
    for diff in [diff_800, diff_12]:
        if diff == 0:
            signs.append(0)
        elif diff * sign > 0:
            signs.append(1)
        else:
            signs.append(-1)
    if signs[0] == 1 and signs[1] == 1:
        return "both_same_direction"
    if -1 in signs:
        return "opposite_direction_present"
    return "one_context_zero_difference"


def contribution_status(overall_diff: int, diff_800: int, diff_12: int, total: int) -> tuple[str, str]:
    if total < SYMMETRY_MIN_SIDE_TOTAL:
        return "insufficient_count", ""
    abs_800 = abs(diff_800)
    abs_12 = abs(diff_12)
    abs_sum = abs_800 + abs_12
    if abs_sum == 0:
        return "mixed_contribution", ""
    dominant = "Rcvr_800 / GUPPI" if abs_800 >= abs_12 else "Rcvr1_2 / GUPPI"
    dominance = max(abs_800, abs_12) / abs_sum
    if dominance >= 0.70:
        return (
            "rcvr_800_dominant" if dominant == "Rcvr_800 / GUPPI" else "rcvr1_2_dominant",
            dominant,
        )
    label = direction_label(overall_diff, diff_800, diff_12)
    if label == "both_same_direction":
        return "shared_same_direction", ""
    if label == "opposite_direction_present":
        return "shared_opposite_direction", ""
    return "mixed_contribution", ""


def build_asymmetry_contribution(
    rows: list[dict[str, Any]], bands: list[float], signed_bins: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for width in bands:
        overall = band_counts(rows, width)
        rcvr_800 = band_counts(context_rows(rows, "Rcvr_800 / GUPPI"), width)
        rcvr1_2 = band_counts(context_rows(rows, "Rcvr1_2 / GUPPI"), width)
        overall_diff = overall["negative"] - overall["positive"]
        diff_800 = rcvr_800["negative"] - rcvr_800["positive"]
        diff_12 = rcvr1_2["negative"] - rcvr1_2["positive"]
        status, dominant = contribution_status(overall_diff, diff_800, diff_12, overall["total"])
        output.append(
            {
                "analysis_type": "symmetry_band",
                "band_or_bin_id": f"d={fmt_float(width)}",
                "lower_bound": fmt_float(-width),
                "upper_bound": fmt_float(width),
                "overall_count_difference": overall_diff,
                "rcvr_800_count_difference": diff_800,
                "rcvr1_2_count_difference": diff_12,
                "rcvr_800_contribution_fraction": float_fraction_text(
                    abs(diff_800) / max(abs(overall_diff), 1)
                ),
                "rcvr1_2_contribution_fraction": float_fraction_text(
                    abs(diff_12) / max(abs(overall_diff), 1)
                ),
                "contribution_direction_match": direction_label(
                    overall_diff, diff_800, diff_12
                ),
                "dominant_context": dominant,
                "contribution_status": status,
                "notes": "Band contribution is descriptive only.",
            }
        )

    signed_count_maps: dict[str, list[int]] = {}
    for context in CONTEXTS:
        counts = [0 for _ in signed_bins]
        for row in context_rows(rows, context):
            counts[bin_index(float(row["_signed"]), signed_bins)] += 1
        signed_count_maps[context] = counts
    for bin_row in signed_bins:
        idx = int(bin_row["bin_index"])
        mirrored = int(bin_row["mirrored_bin_index"])
        if idx > mirrored:
            continue
        overall_diff = signed_count_maps["overall"][idx] - signed_count_maps["overall"][mirrored]
        diff_800 = (
            signed_count_maps["Rcvr_800 / GUPPI"][idx]
            - signed_count_maps["Rcvr_800 / GUPPI"][mirrored]
        )
        diff_12 = (
            signed_count_maps["Rcvr1_2 / GUPPI"][idx]
            - signed_count_maps["Rcvr1_2 / GUPPI"][mirrored]
        )
        pair_total = signed_count_maps["overall"][idx] + signed_count_maps["overall"][mirrored]
        status, dominant = contribution_status(overall_diff, diff_800, diff_12, pair_total)
        output.append(
            {
                "analysis_type": "signed_mirrored_bin_pair",
                "band_or_bin_id": f"bin_pair_{idx}_{mirrored}",
                "lower_bound": fmt_float(bin_row["lower"]),
                "upper_bound": fmt_float(signed_bins[mirrored]["upper"]),
                "overall_count_difference": overall_diff,
                "rcvr_800_count_difference": diff_800,
                "rcvr1_2_count_difference": diff_12,
                "rcvr_800_contribution_fraction": float_fraction_text(
                    abs(diff_800) / max(abs(overall_diff), 1)
                ),
                "rcvr1_2_contribution_fraction": float_fraction_text(
                    abs(diff_12) / max(abs(overall_diff), 1)
                ),
                "contribution_direction_match": direction_label(
                    overall_diff, diff_800, diff_12
                ),
                "dominant_context": dominant,
                "contribution_status": status,
                "notes": "Mirrored-bin contribution uses the SHAPIROMART14 mirror rule.",
            }
        )
    return output


def threshold_counts(selected: list[dict[str, Any]], threshold: float) -> dict[str, int]:
    inside = [row for row in selected if float(row["_absolute"]) <= threshold]
    negative = sum(1 for row in inside if float(row["_signed"]) < 0.0)
    positive = sum(1 for row in inside if float(row["_signed"]) > 0.0)
    return {"total": len(inside), "negative": negative, "positive": positive}


def candidate_status(
    count_800: int,
    count_12: int,
    negative_800: int,
    positive_800: int,
    negative_12: int,
    positive_12: int,
    dominance: float,
    seen_thresholds: set[str],
    threshold_key: str,
) -> str:
    if threshold_key in seen_thresholds:
        return "redundant"
    minimum_context = min(count_800, count_12)
    minimum_side = min(negative_800, positive_800, negative_12, positive_12)
    imbalance_800 = abs(negative_800 - positive_800) / max(negative_800 + positive_800, 1)
    imbalance_12 = abs(negative_12 - positive_12) / max(negative_12 + positive_12, 1)
    if minimum_context < CANDIDATE_MIN_CONTEXT_COUNT:
        return "too_sparse_in_one_context"
    if minimum_side < CANDIDATE_MIN_SIDE_COUNT or max(imbalance_800, imbalance_12) > SYMMETRY_MODERATE_IMBALANCE_MAX:
        return "side_imbalanced"
    if dominance >= CONTEXT_DOMINANCE_STRONG:
        return "context_dominated"
    if dominance >= CONTEXT_DOMINANCE_MODERATE or max(imbalance_800, imbalance_12) > SYMMETRY_MILD_IMBALANCE_MAX:
        return "context_usable_with_imbalance"
    return "context_robust"


def build_threshold_reanalysis(
    rows: list[dict[str, Any]], candidates: list[dict[str, str]]
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    rcvr_800_rows = context_rows(rows, "Rcvr_800 / GUPPI")
    rcvr1_2_rows = context_rows(rows, "Rcvr1_2 / GUPPI")
    seen_thresholds: set[str] = set()
    for candidate in candidates:
        threshold = float(candidate["threshold_value"])
        threshold_key = fmt_float(threshold)
        overall = threshold_counts(rows, threshold)
        c800 = threshold_counts(rcvr_800_rows, threshold)
        c12 = threshold_counts(rcvr1_2_rows, threshold)
        dominance = max(c800["total"], c12["total"]) / max(c800["total"] + c12["total"], 1)
        imbalance_800 = abs(c800["negative"] - c800["positive"]) / max(
            c800["negative"] + c800["positive"], 1
        )
        imbalance_12 = abs(c12["negative"] - c12["positive"]) / max(
            c12["negative"] + c12["positive"], 1
        )
        status = candidate_status(
            c800["total"],
            c12["total"],
            c800["negative"],
            c800["positive"],
            c12["negative"],
            c12["positive"],
            dominance,
            seen_thresholds,
            threshold_key,
        )
        output.append(
            {
                "candidate_id": candidate["candidate_id"],
                "threshold_type": candidate["threshold_type"],
                "threshold_value": candidate["threshold_value"],
                "overall_count_inside": overall["total"],
                "rcvr_800_count_inside": c800["total"],
                "rcvr1_2_count_inside": c12["total"],
                "rcvr_800_fraction_inside": fraction_text(c800["total"], len(rcvr_800_rows)),
                "rcvr1_2_fraction_inside": fraction_text(c12["total"], len(rcvr1_2_rows)),
                "rcvr_800_negative_count": c800["negative"],
                "rcvr_800_positive_count": c800["positive"],
                "rcvr1_2_negative_count": c12["negative"],
                "rcvr1_2_positive_count": c12["positive"],
                "rcvr_800_normalized_imbalance": fmt_float(imbalance_800),
                "rcvr1_2_normalized_imbalance": fmt_float(imbalance_12),
                "minimum_context_count": min(c800["total"], c12["total"]),
                "minimum_side_count": min(
                    c800["negative"], c800["positive"], c12["negative"], c12["positive"]
                ),
                "context_dominance_ratio": fmt_float(dominance),
                "context_mix_status": context_mix_status(dominance),
                "candidate_stability_status": status,
                "threshold_selected": "no",
                "notes": "SHAPIROMART14 candidate reanalyzed with row-level context; no selection made.",
            }
        )
        seen_thresholds.add(threshold_key)
    return output


def append_anomaly(
    anomalies: list[dict[str, Any]],
    anomaly_type: str,
    severity: str,
    context_name: str,
    affected: str,
    count: int,
    total: int,
    evidence: str,
    status: str,
    disposition: str,
    notes: str,
) -> None:
    anomalies.append(
        {
            "anomaly_id": f"SHAPIROMART16_ANOMALY_{len(anomalies) + 1:03d}",
            "anomaly_type": anomaly_type,
            "severity": severity,
            "context_name": context_name,
            "affected_band_or_bin": affected,
            "affected_count": count,
            "affected_fraction": fraction_text(count, total),
            "evidence_basis": evidence,
            "sampling_status": status,
            "disposition": disposition,
            "notes": notes,
        }
    )


def build_anomalies(
    band_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
    contribution_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    anomalies: list[dict[str, Any]] = []
    for row in band_rows:
        if row["context_name"] == "overall":
            continue
        status = row["symmetry_status"]
        if status in {"moderately_imbalanced", "strongly_imbalanced"}:
            append_anomaly(
                anomalies,
                "context_band_side_imbalance",
                "high" if status == "strongly_imbalanced" else "moderate",
                row["context_name"],
                f"d={row['band_half_width']}",
                int(row["absolute_count_difference"]),
                max(int(row["total_in_band"]), 1),
                f"normalized_imbalance={row['normalized_imbalance']}",
                status,
                "descriptive_context_sampling_feature",
                "Negative and positive side counts differ within this context band.",
            )
    for row in signed_rows:
        if row["context_name"] == "overall":
            continue
        if row["symmetry_status"] == "strongly_imbalanced":
            append_anomaly(
                anomalies,
                "context_mirrored_bin_imbalance",
                "high",
                row["context_name"],
                f"bin={row['bin_index']};mirror={row['mirrored_bin_index']}",
                int(row["absolute_count_difference"]),
                max(int(row["observed_count"]) + int(row["mirrored_count"]), 1),
                f"normalized_imbalance={row['normalized_imbalance']}",
                "strongly_imbalanced",
                "descriptive_context_sampling_feature",
                "Mirrored signed bins differ within this context.",
            )
    for row in contribution_rows:
        if row["contribution_status"] in {"rcvr_800_dominant", "rcvr1_2_dominant"}:
            append_anomaly(
                anomalies,
                "dominant_context_asymmetry_contribution",
                "high",
                row["dominant_context"],
                row["band_or_bin_id"],
                abs(int(row["overall_count_difference"])),
                EXPECTED_ROW_COUNT,
                row["contribution_status"],
                "context_dominant",
                "descriptive_contribution_feature",
                "Overall count difference is mostly carried by one context.",
            )
    dominated_candidates = [
        row
        for row in threshold_rows
        if row["candidate_stability_status"]
        in {"context_dominated", "too_sparse_in_one_context", "side_imbalanced"}
    ]
    for row in dominated_candidates[:20]:
        append_anomaly(
            anomalies,
            "threshold_candidate_context_limitation",
            "moderate",
            "threshold_candidate_inventory",
            row["candidate_id"],
            int(row["minimum_context_count"]),
            max(int(row["overall_count_inside"]), 1),
            row["candidate_stability_status"],
            row["context_mix_status"],
            "candidate_planning_limitation",
            "Candidate remains catalogued only; no threshold is selected.",
        )
    return anomalies


def strongest_band_by_context(band_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for context in CONTEXTS:
        rows = [row for row in band_rows if row["context_name"] == context]
        result[context] = max(rows, key=lambda row: float(row["normalized_imbalance"]))
    return result


def strongest_signed_by_context(signed_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for context in CONTEXTS:
        rows = [row for row in signed_rows if row["context_name"] == context]
        result[context] = max(rows, key=lambda row: float(row["normalized_imbalance"]))
    return result


def pre_post_counts(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    result: dict[str, dict[str, int]] = {}
    for context in CONTEXTS:
        selected = context_rows(rows, context)
        result[context] = {
            "negative": sum(1 for row in selected if float(row["_signed"]) < 0.0),
            "positive": sum(1 for row in selected if float(row["_signed"]) > 0.0),
            "exact_zero": sum(1 for row in selected if float(row["_signed"]) == 0.0),
            "total": len(selected),
        }
    return result


def build_final_status(
    rows: list[dict[str, Any]],
    contribution_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = Counter(row["context_name"] for row in rows)
    context_counts_match = (
        counts.get("Rcvr_800 / GUPPI", 0) == EXPECTED_RCVR_800_COUNT
        and counts.get("Rcvr1_2 / GUPPI", 0) == EXPECTED_RCVR1_2_COUNT
        and len(rows) == EXPECTED_ROW_COUNT
    )
    context_dominance_found = any(
        row["contribution_status"] in {"rcvr_800_dominant", "rcvr1_2_dominant"}
        for row in contribution_rows
    ) or any(
        row["context_mix_status"] in {"moderate_context_dominance", "strong_context_dominance"}
        for row in threshold_rows
    )
    high_anomalies = any(row["severity"] == "high" for row in anomalies)
    if not context_counts_match or len(threshold_rows) != EXPECTED_CANDIDATE_COUNT:
        final_status = "context_sampling_symmetry_failed"
    elif high_anomalies or context_dominance_found:
        final_status = "context_sampling_symmetry_characterized_with_context_imbalances"
    else:
        final_status = "context_sampling_symmetry_characterized"
    return {
        "research_block": RESEARCH_BLOCK,
        "enriched_context_input_available": "yes",
        "enriched_row_count": len(rows),
        "expected_row_count": EXPECTED_ROW_COUNT,
        "rcvr_800_count": counts.get("Rcvr_800 / GUPPI", 0),
        "rcvr1_2_count": counts.get("Rcvr1_2 / GUPPI", 0),
        "context_counts_match": "yes" if context_counts_match else "no",
        "context_absolute_distribution_completed": "yes",
        "context_signed_distribution_completed": "yes",
        "context_symmetry_bands_completed": "yes",
        "asymmetry_contribution_completed": "yes",
        "threshold_candidates_reanalyzed": "yes",
        "threshold_candidate_count": len(threshold_rows),
        "overall_asymmetry_context_explained": "yes",
        "context_dominance_found": "yes" if context_dominance_found else "no",
        "high_severity_sampling_anomalies_found": "yes" if high_anomalies else "no",
        "threshold_selected": "no",
        "exposure_classes_created": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "model_fit_performed": "no",
        "physical_interpretation_performed": "no",
        "database_access": "none",
        "additional_gate_created": "no",
        "final_status": final_status,
        "recommended_next_action": (
            "Use this context-enriched descriptive inventory only as planning input "
            "for any separately specified later threshold decision."
        ),
        "limitations": (
            "This block describes context sampling distributions only and does not "
            "select a threshold or assign exposure classes."
        ),
    }


def build_readout(
    rows: list[dict[str, Any]],
    band_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
    contribution_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
    final_status: dict[str, Any],
) -> str:
    counts = pre_post_counts(rows)
    strongest_bands = strongest_band_by_context(band_rows)
    strongest_signed = strongest_signed_by_context(signed_rows)
    robust_count = sum(
        1 for row in threshold_rows if row["candidate_stability_status"] == "context_robust"
    )
    dominated_count = sum(
        1 for row in threshold_rows if row["candidate_stability_status"] == "context_dominated"
    )
    dominant_rows = [
        row
        for row in contribution_rows
        if row["contribution_status"] in {"rcvr_800_dominant", "rcvr1_2_dominant"}
    ]
    strongest_dominance = dominant_rows[0] if dominant_rows else {}
    context_lines = [
        (
            f"- {context}: n={counts[context]['total']}, "
            f"negative={counts[context]['negative']}, "
            f"positive={counts[context]['positive']}, zero={counts[context]['exact_zero']}"
        )
        for context in CONTEXTS
    ]
    band_lines = [
        (
            f"- {context}: strongest band d={strongest_bands[context]['band_half_width']}, "
            f"normalized_imbalance={strongest_bands[context]['normalized_imbalance']}, "
            f"status={strongest_bands[context]['symmetry_status']}"
        )
        for context in CONTEXTS
    ]
    signed_lines = [
        (
            f"- {context}: strongest mirrored bin {strongest_signed[context]['bin_index']} "
            f"vs {strongest_signed[context]['mirrored_bin_index']}, "
            f"normalized_imbalance={strongest_signed[context]['normalized_imbalance']}, "
            f"status={strongest_signed[context]['symmetry_status']}"
        )
        for context in CONTEXTS
    ]
    return "\n".join(
        [
            "# SHAPIROMART16 Readout",
            "",
            "## 1. Purpose",
            "Repeat the SHAPIROMART14 sampling symmetry diagnostics with SHAPIROMART15 row-level receiver/backend context.",
            "",
            "## 2. Enriched Input Identity",
            f"Enriched rows used: {len(rows)}. Only context_mapping_status=mapped rows were accepted.",
            "",
            "## 3. Context Counts",
            *context_lines,
            "",
            "## 4. Absolute Distance by Context",
            "Absolute distributions use the 20 SHAPIROMART14 distance bins without changing bin edges.",
            "",
            "## 5. Signed Offset by Context",
            *signed_lines,
            "",
            "## 6. Symmetry Bands by Context",
            *band_lines,
            "",
            "## 7. Contribution to Overall Asymmetry",
            (
                f"Contribution rows written: {len(contribution_rows)}. "
                f"Context dominance found: {final_status['context_dominance_found']}."
            ),
            (
                "Strongest dominance example: "
                f"{strongest_dominance.get('band_or_bin_id', 'none')} "
                f"{strongest_dominance.get('contribution_status', '')}."
            ),
            "",
            "## 8. Threshold Candidate Reanalysis",
            (
                f"Candidates reanalyzed: {len(threshold_rows)}. "
                f"context_robust={robust_count}; context_dominated={dominated_count}."
            ),
            "threshold_selected = no.",
            "",
            "## 9. Context Sampling Anomalies",
            f"Anomalies catalogued: {len(anomalies)}.",
            "",
            "## 10. Final Status",
            f"final_status = {final_status['final_status']}.",
            "",
            "## 11. Recommended Next Action",
            str(final_status["recommended_next_action"]),
            "",
            "## 12. Limitations",
            str(final_status["limitations"]),
            "exposure_classes_created = no.",
            "shapiro_delay_calculated = no.",
            "residual_analysis_performed = no.",
            "model_fit_performed = no.",
            "physical_interpretation_performed = no.",
            "additional_gate_created = no.",
            "",
        ]
    )


def build_summary(
    args: argparse.Namespace,
    rows: list[dict[str, Any]],
    band_rows: list[dict[str, Any]],
    signed_rows: list[dict[str, Any]],
    contribution_rows: list[dict[str, Any]],
    threshold_rows: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
    final_status: dict[str, Any],
) -> dict[str, Any]:
    return {
        "research_block": RESEARCH_BLOCK,
        "inputs_read": {
            "enriched_input": str(args.enriched_input),
            "shapiromart14_dir": str(args.shapiromart14_dir),
            "shapiromart15_dir": str(args.shapiromart15_dir),
        },
        "context_counts": pre_post_counts(rows),
        "strongest_band_by_context": strongest_band_by_context(band_rows),
        "strongest_signed_bin_by_context": strongest_signed_by_context(signed_rows),
        "contribution_status_counts": dict(Counter(row["contribution_status"] for row in contribution_rows)),
        "threshold_candidate_status_counts": dict(
            Counter(row["candidate_stability_status"] for row in threshold_rows)
        ),
        "anomaly_type_counts": dict(Counter(row["anomaly_type"] for row in anomalies)),
        "boundaries": {
            "threshold_selected": "no",
            "exposure_classes_created": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "model_fit_performed": "no",
            "physical_interpretation_performed": "no",
            "database_access": "none",
            "additional_gate_created": "no",
        },
        "final_status": final_status,
        "output_dir": str(args.output_dir),
    }


def verify_outputs(output_dir: Path) -> None:
    observed = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    expected = sorted(OUTPUT_FILES)
    if observed != expected:
        raise RuntimeError(f"Output file set mismatch. Expected {expected}, observed {observed}.")


def main() -> None:
    args = parse_args()
    validate_output_dir(args.output_dir, args.overwrite)
    validate_upstream_status(args.shapiromart15_dir, args.shapiromart14_dir)
    rows = load_enriched_rows(args.enriched_input)
    absolute_bins = load_absolute_bins(args.shapiromart14_dir)
    signed_bins = load_signed_bins(args.shapiromart14_dir)
    bands = load_bands(args.shapiromart14_dir)
    candidates = load_threshold_candidates(args.shapiromart14_dir)

    absolute_rows = build_absolute_distribution(rows, absolute_bins)
    signed_rows = build_signed_distribution(rows, signed_bins)
    band_rows = build_band_summary(rows, bands)
    contribution_rows = build_asymmetry_contribution(rows, bands, signed_bins)
    threshold_rows = build_threshold_reanalysis(rows, candidates)
    anomalies = build_anomalies(band_rows, signed_rows, contribution_rows, threshold_rows)
    final_status = build_final_status(rows, contribution_rows, threshold_rows, anomalies)
    readout = build_readout(
        rows, band_rows, signed_rows, contribution_rows, threshold_rows, anomalies, final_status
    )
    summary = build_summary(
        args, rows, band_rows, signed_rows, contribution_rows, threshold_rows, anomalies, final_status
    )

    write_text(args.output_dir / READOUT_MD, readout)
    write_json(args.output_dir / SUMMARY_JSON, summary)
    write_csv(args.output_dir / CONTEXT_ABSOLUTE_CSV, absolute_rows, CONTEXT_ABSOLUTE_FIELDS)
    write_csv(args.output_dir / CONTEXT_SIGNED_CSV, signed_rows, CONTEXT_SIGNED_FIELDS)
    write_csv(args.output_dir / CONTEXT_BAND_CSV, band_rows, CONTEXT_BAND_FIELDS)
    write_csv(
        args.output_dir / CONTEXT_CONTRIBUTION_CSV,
        contribution_rows,
        CONTEXT_CONTRIBUTION_FIELDS,
    )
    write_csv(
        args.output_dir / THRESHOLD_REANALYSIS_CSV,
        threshold_rows,
        THRESHOLD_REANALYSIS_FIELDS,
    )
    write_csv(args.output_dir / ANOMALY_CSV, anomalies, ANOMALY_FIELDS)
    write_csv(args.output_dir / FINAL_STATUS_CSV, [final_status], FINAL_STATUS_FIELDS)
    verify_outputs(args.output_dir)


if __name__ == "__main__":
    main()
