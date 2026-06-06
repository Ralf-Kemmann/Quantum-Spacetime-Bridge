#!/usr/bin/env python3
"""QSB-SHAPIROMART17 threshold consolidation and comparison-group preparation.

This block selects diagnostic threshold values only from the existing
SHAPIROMART14 candidate inventory, using SHAPIROMART16 context reanalysis
metrics and SHAPIROMART15 row-level context. It prepares inside/outside
comparison groups for later work, but does not compare fingerprints, calculate
Shapiro delay, inspect residuals, run a model fit, make a physical
interpretation, open a database, or create any extra decision mechanism.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any


RESEARCH_BLOCK = "QSB-SHAPIROMART17"
EXPECTED_ROW_COUNT = 7419
EXPECTED_CANDIDATE_COUNT = 27
EXPECTED_RCVR_800_COUNT = 2916
EXPECTED_RCVR1_2_COUNT = 4503

MINIMUM_TOTAL_INSIDE = 100
MINIMUM_CONTEXT_INSIDE = 40
MINIMUM_SIDE_INSIDE_PER_CONTEXT = 15
EXTREME_CONTEXT_IMBALANCE = 0.50

COMPOSITION_COMPARABLE_MAX = 0.05
COMPOSITION_MILD_MAX = 0.10
COMPOSITION_MODERATE_MAX = 0.20

SHAPIROMART_BASE = Path("runs/QSB-SHAPIROMART")
SHAPIROMART14_DIR = SHAPIROMART_BASE / "SHAPIROMART14_CONJUNCTION_DISTANCE_SAMPLING_SYMMETRY"
SHAPIROMART15_DIR = SHAPIROMART_BASE / "SHAPIROMART15_ROW_LEVEL_CONTEXT_ENRICHMENT"
SHAPIROMART16_DIR = SHAPIROMART_BASE / "SHAPIROMART16_CONTEXT_ENRICHED_SAMPLING_SYMMETRY"
DEFAULT_OUTPUT_DIR = (
    SHAPIROMART_BASE / "SHAPIROMART17_THRESHOLD_CONSOLIDATION_EXPOSURE_PREPARATION"
)

DEFAULT_CANDIDATE_INPUT = SHAPIROMART14_DIR / "shapiromart14_threshold_candidate_inventory.csv"
DEFAULT_CONTEXT_REANALYSIS_INPUT = (
    SHAPIROMART16_DIR / "shapiromart16_threshold_candidate_context_reanalysis.csv"
)
DEFAULT_ENRICHED_GEOMETRY_INPUT = (
    SHAPIROMART15_DIR / "shapiromart15_enriched_phase_geometry.csv"
)

READOUT_MD = "shapiromart17_readout.md"
SUMMARY_JSON = "shapiromart17_summary.json"
CANDIDATE_CONSOLIDATION_CSV = "shapiromart17_candidate_consolidation.csv"
THRESHOLD_SHORTLIST_CSV = "shapiromart17_threshold_shortlist.csv"
THRESHOLD_DECISION_CSV = "shapiromart17_threshold_decision.csv"
PREPARED_GROUPS_CSV = "shapiromart17_prepared_exposure_groups.csv"
GROUP_BALANCE_CSV = "shapiromart17_group_balance_summary.csv"
DECISION_RATIONALE_CSV = "shapiromart17_decision_rationale.csv"
FINAL_STATUS_CSV = "shapiromart17_final_status.csv"

OUTPUT_FILES = [
    READOUT_MD,
    SUMMARY_JSON,
    CANDIDATE_CONSOLIDATION_CSV,
    THRESHOLD_SHORTLIST_CSV,
    THRESHOLD_DECISION_CSV,
    PREPARED_GROUPS_CSV,
    GROUP_BALANCE_CSV,
    DECISION_RATIONALE_CSV,
    FINAL_STATUS_CSV,
]

CONTEXTS = ["overall", "Rcvr_800 / GUPPI", "Rcvr1_2 / GUPPI"]
ROW_CONTEXTS = ["Rcvr_800 / GUPPI", "Rcvr1_2 / GUPPI"]

CANDIDATE_CONSOLIDATION_FIELDS = [
    "candidate_id",
    "threshold_type",
    "threshold_value",
    "original_rationale",
    "total_count_inside",
    "total_fraction_inside",
    "rcvr_800_count_inside",
    "rcvr1_2_count_inside",
    "minimum_context_count",
    "rcvr_800_negative_count",
    "rcvr_800_positive_count",
    "rcvr1_2_negative_count",
    "rcvr1_2_positive_count",
    "minimum_side_count",
    "overall_normalized_imbalance",
    "rcvr_800_normalized_imbalance",
    "rcvr1_2_normalized_imbalance",
    "context_dominance_ratio",
    "context_mix_status",
    "candidate_stability_status",
    "anomaly_overlap",
    "geometric_simplicity",
    "redundancy_group",
    "exclusion_reason",
    "consolidation_status",
    "notes",
]

THRESHOLD_SHORTLIST_FIELDS = [
    "shortlist_rank",
    "candidate_id",
    "threshold_type",
    "threshold_value",
    "total_count_inside",
    "minimum_context_count",
    "minimum_side_count",
    "maximum_context_imbalance",
    "context_dominance_ratio",
    "candidate_stability_status",
    "geometric_simplicity",
    "main_strength",
    "main_limitation",
    "shortlist_status",
    "notes",
]

THRESHOLD_DECISION_FIELDS = [
    "decision_role",
    "candidate_id",
    "threshold_type",
    "threshold_value",
    "selected",
    "selection_rank",
    "selection_basis",
    "total_count_inside",
    "total_fraction_inside",
    "rcvr_800_count_inside",
    "rcvr1_2_count_inside",
    "minimum_context_count",
    "minimum_side_count",
    "overall_normalized_imbalance",
    "rcvr_800_normalized_imbalance",
    "rcvr1_2_normalized_imbalance",
    "context_dominance_ratio",
    "context_mix_status",
    "candidate_stability_status",
    "comparison_role",
    "decision_status",
    "notes",
]

PREPARED_GROUPS_FIELDS = [
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
    "threshold_source_candidate_id",
    "grouping_rule",
    "group_preparation_status",
    "notes",
]

GROUP_BALANCE_FIELDS = [
    "decision_role",
    "threshold_value",
    "scope",
    "context_name",
    "total_count",
    "inside_count",
    "outside_count",
    "inside_fraction",
    "pre_inside_count",
    "post_inside_count",
    "inside_normalized_imbalance",
    "context_share_inside",
    "context_share_outside",
    "context_composition_difference",
    "composition_status",
    "balance_status",
    "notes",
]

DECISION_RATIONALE_FIELDS = [
    "rationale_order",
    "criterion",
    "selected_candidate_value",
    "best_alternative_value",
    "selected_candidate_assessment",
    "alternative_assessment",
    "decision_effect",
    "evidence_source",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "candidate_count_input",
    "candidate_count_consolidated",
    "shortlist_created",
    "shortlist_count",
    "primary_threshold_selected",
    "primary_threshold_value",
    "secondary_threshold_selected",
    "secondary_threshold_value",
    "selection_based_only_on_sampling_and_robustness",
    "prepared_group_rows",
    "expected_group_rows",
    "all_rows_grouped",
    "receiver_backend_context_preserved",
    "primary_group_balance_assessed",
    "context_composition_assessed",
    "exposure_analysis_performed",
    "fingerprint_comparison_performed",
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Consolidate SHAPIROMART14/16 threshold candidates and prepare "
            "row-level inside/outside comparison groups."
        )
    )
    parser.add_argument("--candidate-input", type=Path, default=DEFAULT_CANDIDATE_INPUT)
    parser.add_argument(
        "--context-reanalysis-input",
        type=Path,
        default=DEFAULT_CONTEXT_REANALYSIS_INPUT,
    )
    parser.add_argument(
        "--enriched-geometry-input",
        type=Path,
        default=DEFAULT_ENRICHED_GEOMETRY_INPUT,
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--max-shortlist-size", type=int, default=5)
    parser.add_argument("--allow-secondary-threshold", action=argparse.BooleanOptionalAction, default=True)
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


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader), list(reader.fieldnames or [])


def read_single_csv_row(path: Path) -> dict[str, str]:
    rows, _ = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected one row in {path}, observed {len(rows)}.")
    return rows[0]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected JSON object in {path}.")
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
                f"Output directory contains files outside expected set: {unexpected}"
            )
    output_dir.mkdir(parents=True, exist_ok=True)


def require_fields(rows: list[dict[str, str]], fields: list[str], path: Path) -> None:
    if not rows:
        raise ValueError(f"Input has no rows: {path}")
    missing = sorted(set(fields) - set(rows[0].keys()))
    if missing:
        raise ValueError(f"Missing required fields in {path}: {missing}")


def validate_upstream_inputs() -> dict[str, Any]:
    sh14_final = read_single_csv_row(SHAPIROMART14_DIR / "shapiromart14_final_status.csv")
    sh14_summary = read_json(SHAPIROMART14_DIR / "shapiromart14_summary.json")
    sh15_final = read_single_csv_row(SHAPIROMART15_DIR / "shapiromart15_final_status.csv")
    sh15_counts, _ = read_csv_rows(SHAPIROMART15_DIR / "shapiromart15_context_count_validation.csv")
    sh16_final = read_single_csv_row(SHAPIROMART16_DIR / "shapiromart16_final_status.csv")
    sh16_summary = read_json(SHAPIROMART16_DIR / "shapiromart16_summary.json")
    read_csv_rows(SHAPIROMART14_DIR / "shapiromart14_absolute_distance_distribution.csv")
    read_csv_rows(SHAPIROMART14_DIR / "shapiromart14_signed_offset_distribution.csv")
    read_csv_rows(SHAPIROMART14_DIR / "shapiromart14_symmetry_band_summary.csv")
    read_csv_rows(SHAPIROMART14_DIR / "shapiromart14_sampling_anomaly_inventory.csv")
    read_csv_rows(SHAPIROMART16_DIR / "shapiromart16_context_symmetry_band_summary.csv")
    read_csv_rows(SHAPIROMART16_DIR / "shapiromart16_context_asymmetry_contribution.csv")
    read_csv_rows(SHAPIROMART16_DIR / "shapiromart16_context_sampling_anomaly_inventory.csv")

    checks = {
        "sh14_candidate_catalogued": sh14_final.get("threshold_candidates_catalogued", ""),
        "sh14_threshold_selected": sh14_final.get("threshold_selected", ""),
        "sh15_rows": sh15_final.get("enriched_row_count", ""),
        "sh15_unmatched": sh15_final.get("unmatched_row_count", ""),
        "sh15_ambiguous": sh15_final.get("ambiguous_row_count", ""),
        "sh16_candidate_count": sh16_final.get("threshold_candidate_count", ""),
        "sh16_threshold_selected": sh16_final.get("threshold_selected", ""),
    }
    expected = {
        "sh14_candidate_catalogued": "yes",
        "sh14_threshold_selected": "no",
        "sh15_rows": str(EXPECTED_ROW_COUNT),
        "sh15_unmatched": "0",
        "sh15_ambiguous": "0",
        "sh16_candidate_count": str(EXPECTED_CANDIDATE_COUNT),
        "sh16_threshold_selected": "no",
    }
    failures = {
        key: {"expected": expected[key], "observed": checks.get(key, "")}
        for key in expected
        if checks.get(key, "") != expected[key]
    }
    if failures:
        raise ValueError(f"Upstream status validation failed: {failures}")
    if any(row.get("count_match", "") != "yes" for row in sh15_counts):
        raise ValueError("SHAPIROMART15 context count validation contains mismatch.")
    return {
        "shapiromart14_final": sh14_final,
        "shapiromart14_summary": sh14_summary,
        "shapiromart15_final": sh15_final,
        "shapiromart15_counts": sh15_counts,
        "shapiromart16_final": sh16_final,
        "shapiromart16_summary": sh16_summary,
    }


def load_candidates(
    candidate_input: Path, context_reanalysis_input: Path
) -> list[dict[str, Any]]:
    sh14_rows, _ = read_csv_rows(candidate_input)
    sh16_rows, _ = read_csv_rows(context_reanalysis_input)
    if len(sh14_rows) != EXPECTED_CANDIDATE_COUNT:
        raise ValueError(f"Expected {EXPECTED_CANDIDATE_COUNT} candidates in SHAPIROMART14.")
    if len(sh16_rows) != EXPECTED_CANDIDATE_COUNT:
        raise ValueError(f"Expected {EXPECTED_CANDIDATE_COUNT} candidates in SHAPIROMART16.")
    by_id = {row["candidate_id"]: row for row in sh16_rows}
    if set(row["candidate_id"] for row in sh14_rows) != set(by_id):
        raise ValueError("Candidate id sets differ between SHAPIROMART14 and SHAPIROMART16.")

    merged: list[dict[str, Any]] = []
    for row in sh14_rows:
        context = by_id[row["candidate_id"]]
        value14 = float(row["threshold_value"])
        value16 = float(context["threshold_value"])
        if not math.isclose(value14, value16, rel_tol=0.0, abs_tol=1e-15):
            raise ValueError(f"Threshold mismatch for {row['candidate_id']}.")
        merged.append(
            {
                **row,
                "_context": context,
                "_threshold": value16,
                "_total_count": int(context["overall_count_inside"]),
                "_rcvr_800_count": int(context["rcvr_800_count_inside"]),
                "_rcvr1_2_count": int(context["rcvr1_2_count_inside"]),
                "_min_context": int(context["minimum_context_count"]),
                "_rcvr_800_neg": int(context["rcvr_800_negative_count"]),
                "_rcvr_800_pos": int(context["rcvr_800_positive_count"]),
                "_rcvr1_2_neg": int(context["rcvr1_2_negative_count"]),
                "_rcvr1_2_pos": int(context["rcvr1_2_positive_count"]),
                "_min_side": int(context["minimum_side_count"]),
                "_overall_imbalance": float(row["normalized_imbalance"]),
                "_rcvr_800_imbalance": float(context["rcvr_800_normalized_imbalance"]),
                "_rcvr1_2_imbalance": float(context["rcvr1_2_normalized_imbalance"]),
                "_dominance": float(context["context_dominance_ratio"]),
                "_stability": context["candidate_stability_status"],
                "_context_mix": context["context_mix_status"],
            }
        )
    return merged


def load_enriched_rows(path: Path) -> list[dict[str, Any]]:
    rows, _ = read_csv_rows(path)
    require_fields(rows, ENRICHED_REQUIRED_FIELDS, path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"Expected {EXPECTED_ROW_COUNT} enriched rows.")
    if len(set(row["source_row_index"] for row in rows)) != EXPECTED_ROW_COUNT:
        raise ValueError("source_row_index values are not unique.")
    status_counts = Counter(row["context_mapping_status"] for row in rows)
    if set(status_counts) != {"mapped"}:
        raise ValueError(f"Unexpected context mapping statuses: {dict(status_counts)}")
    counts = Counter(row["context_name"] for row in rows)
    if counts.get("Rcvr_800 / GUPPI", 0) != EXPECTED_RCVR_800_COUNT:
        raise ValueError("Rcvr_800 / GUPPI row count mismatch.")
    if counts.get("Rcvr1_2 / GUPPI", 0) != EXPECTED_RCVR1_2_COUNT:
        raise ValueError("Rcvr1_2 / GUPPI row count mismatch.")

    parsed: list[dict[str, Any]] = []
    for row in rows:
        absolute = float(row["absolute_phase_distance"])
        signed = float(row["signed_phase_offset"])
        if not (math.isfinite(absolute) and 0.0 <= absolute <= 0.5):
            raise ValueError(f"Invalid absolute distance at source_row_index={row['source_row_index']}")
        if not (math.isfinite(signed) and -0.5 <= signed < 0.5):
            raise ValueError(f"Invalid signed offset at source_row_index={row['source_row_index']}")
        parsed_row = dict(row)
        parsed_row["_absolute"] = absolute
        parsed_row["_signed"] = signed
        parsed.append(parsed_row)
    return parsed


def geometric_simplicity(candidate: dict[str, Any]) -> str:
    threshold_type = candidate["threshold_type"]
    threshold = candidate["_threshold"]
    simple_values = {0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25}
    if threshold_type == "predefined_geometric_band" and any(
        math.isclose(threshold, value, rel_tol=0.0, abs_tol=1e-12) for value in simple_values
    ):
        return "simple_predefined_geometric_band"
    if threshold_type.startswith("empirical_quantile"):
        return "empirical_quantile"
    if threshold_type.startswith("local_density"):
        return "density_feature_edge"
    if threshold_type.startswith("strong_adjacent"):
        return "adjacent_density_change_edge"
    return "other_existing_candidate"


def redundancy_groups(candidates: list[dict[str, Any]]) -> dict[str, str]:
    groups: dict[str, str] = {}
    by_value: dict[str, list[dict[str, Any]]] = {}
    for candidate in candidates:
        key = fmt_float(candidate["_threshold"])
        by_value.setdefault(key, []).append(candidate)
    for index, (key, rows) in enumerate(sorted(by_value.items(), key=lambda item: float(item[0])), 1):
        group_id = f"threshold_value_group_{index:02d}"
        for row in rows:
            groups[row["candidate_id"]] = group_id
    return groups


def anomaly_overlap(candidate: dict[str, Any]) -> str:
    if candidate["_stability"] in {"context_dominated", "too_sparse_in_one_context", "side_imbalanced"}:
        return "context_reanalysis_limitation"
    if candidate["suitability_status"] in {"sampling_imbalanced", "too_sparse", "context_dominated"}:
        return "shapiromart14_candidate_limitation"
    return "none_detected"


def exclusion_reason(candidate: dict[str, Any]) -> str:
    if candidate["_stability"] in {"context_dominated", "too_sparse_in_one_context", "not_recommended"}:
        return f"excluded_by_stability_status={candidate['_stability']}"
    if candidate["_total_count"] < MINIMUM_TOTAL_INSIDE:
        return "total_count_below_minimum"
    if candidate["_min_context"] < MINIMUM_CONTEXT_INSIDE:
        return "context_count_below_minimum"
    if candidate["_min_side"] < MINIMUM_SIDE_INSIDE_PER_CONTEXT:
        return "context_side_count_below_minimum"
    if max(candidate["_rcvr_800_imbalance"], candidate["_rcvr1_2_imbalance"]) > EXTREME_CONTEXT_IMBALANCE:
        return "extreme_context_side_imbalance"
    return ""


def selection_score(candidate: dict[str, Any]) -> float:
    score = 0.0
    if candidate["_stability"] == "context_robust":
        score += 100.0
    elif candidate["_stability"] == "context_usable_with_imbalance":
        score += 45.0
    if geometric_simplicity(candidate) == "simple_predefined_geometric_band":
        score += 35.0
    elif geometric_simplicity(candidate) == "density_feature_edge":
        score += 15.0
    elif geometric_simplicity(candidate) == "empirical_quantile":
        score += 8.0
    if candidate["_context_mix"] == "balanced_context_mix":
        score += 18.0
    elif candidate["_context_mix"] == "mild_context_dominance":
        score += 6.0
    inside_fraction = candidate["_total_count"] / EXPECTED_ROW_COUNT
    if 0.20 <= inside_fraction <= 0.40:
        score += 20.0
    elif 0.10 <= inside_fraction < 0.20 or 0.40 < inside_fraction <= 0.50:
        score += 8.0
    elif inside_fraction > 0.80:
        score -= 30.0
    score -= 100.0 * max(candidate["_rcvr_800_imbalance"], candidate["_rcvr1_2_imbalance"])
    score -= 60.0 * max(0.0, candidate["_dominance"] - 0.55)
    if candidate["suitability_status"] == "redundant" or candidate["_stability"] == "redundant":
        score -= 40.0
    return score


def build_consolidation(candidates: list[dict[str, Any]], max_shortlist_size: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups = redundancy_groups(candidates)
    eligible: list[dict[str, Any]] = []
    consolidation_rows: list[dict[str, Any]] = []
    seen_values: set[str] = set()
    for candidate in candidates:
        exclusion = exclusion_reason(candidate)
        value_key = fmt_float(candidate["_threshold"])
        repeated_value = value_key in seen_values
        seen_values.add(value_key)
        redundant = (
            repeated_value
            or candidate["suitability_status"] == "redundant"
            or candidate["_stability"] == "redundant"
        )
        if exclusion:
            if "side" in exclusion or "imbalance" in exclusion:
                status = "not_shortlisted_imbalanced"
            elif "count" in exclusion:
                status = "not_shortlisted_sparse"
            else:
                status = "not_shortlisted_context_unstable"
        elif redundant:
            status = "not_shortlisted_redundant"
        else:
            status = "eligible_pending_shortlist"
            eligible.append(candidate)
        row = consolidation_row(candidate, groups[candidate["candidate_id"]], exclusion, status)
        consolidation_rows.append(row)

    ranked = sorted(
        eligible,
        key=lambda c: (
            -selection_score(c),
            0 if geometric_simplicity(c) == "simple_predefined_geometric_band" else 1,
            c["_threshold"],
        ),
    )
    shortlist_candidates = ranked[:max_shortlist_size]
    shortlist_ids = {candidate["candidate_id"] for candidate in shortlist_candidates}
    updated_rows: list[dict[str, Any]] = []
    for row in consolidation_rows:
        if row["candidate_id"] in shortlist_ids:
            row = dict(row)
            row["consolidation_status"] = "shortlisted"
            row["notes"] = "Included in deterministic shortlist."
        elif row["consolidation_status"] == "eligible_pending_shortlist":
            row = dict(row)
            row["consolidation_status"] = "not_shortlisted_low_incremental_value"
            row["notes"] = "Eligible, but lower rank after robustness, balance, mix, simplicity, and redundancy review."
        updated_rows.append(row)
    return updated_rows, shortlist_candidates


def consolidation_row(candidate: dict[str, Any], group_id: str, exclusion: str, status: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate["candidate_id"],
        "threshold_type": candidate["threshold_type"],
        "threshold_value": candidate["threshold_value"],
        "original_rationale": candidate["rationale"],
        "total_count_inside": candidate["_total_count"],
        "total_fraction_inside": candidate["total_fraction_inside"],
        "rcvr_800_count_inside": candidate["_rcvr_800_count"],
        "rcvr1_2_count_inside": candidate["_rcvr1_2_count"],
        "minimum_context_count": candidate["_min_context"],
        "rcvr_800_negative_count": candidate["_rcvr_800_neg"],
        "rcvr_800_positive_count": candidate["_rcvr_800_pos"],
        "rcvr1_2_negative_count": candidate["_rcvr1_2_neg"],
        "rcvr1_2_positive_count": candidate["_rcvr1_2_pos"],
        "minimum_side_count": candidate["_min_side"],
        "overall_normalized_imbalance": fmt_float(candidate["_overall_imbalance"]),
        "rcvr_800_normalized_imbalance": fmt_float(candidate["_rcvr_800_imbalance"]),
        "rcvr1_2_normalized_imbalance": fmt_float(candidate["_rcvr1_2_imbalance"]),
        "context_dominance_ratio": fmt_float(candidate["_dominance"]),
        "context_mix_status": candidate["_context_mix"],
        "candidate_stability_status": candidate["_stability"],
        "anomaly_overlap": anomaly_overlap(candidate),
        "geometric_simplicity": geometric_simplicity(candidate),
        "redundancy_group": group_id,
        "exclusion_reason": exclusion,
        "consolidation_status": status,
        "notes": "Consolidated from existing SHAPIROMART14 and SHAPIROMART16 candidate fields.",
    }


def maximum_context_imbalance(candidate: dict[str, Any]) -> float:
    return max(candidate["_rcvr_800_imbalance"], candidate["_rcvr1_2_imbalance"])


def shortlist_rows(shortlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rank, candidate in enumerate(shortlist, 1):
        strength = "context robust with sufficient counts"
        if geometric_simplicity(candidate) == "simple_predefined_geometric_band":
            strength += "; simple predefined geometry"
        limitation = "mild context mix shift" if candidate["_context_mix"] != "balanced_context_mix" else "not the only robust candidate"
        if maximum_context_imbalance(candidate) > 0.25:
            limitation = "one context has moderate side imbalance"
        rows.append(
            {
                "shortlist_rank": rank,
                "candidate_id": candidate["candidate_id"],
                "threshold_type": candidate["threshold_type"],
                "threshold_value": candidate["threshold_value"],
                "total_count_inside": candidate["_total_count"],
                "minimum_context_count": candidate["_min_context"],
                "minimum_side_count": candidate["_min_side"],
                "maximum_context_imbalance": fmt_float(maximum_context_imbalance(candidate)),
                "context_dominance_ratio": fmt_float(candidate["_dominance"]),
                "candidate_stability_status": candidate["_stability"],
                "geometric_simplicity": geometric_simplicity(candidate),
                "main_strength": strength,
                "main_limitation": limitation,
                "shortlist_status": "shortlisted",
                "notes": "Shortlist rank is based only on sampling robustness and interpretability criteria.",
            }
        )
    return rows


def choose_primary(shortlist: list[dict[str, Any]]) -> dict[str, Any]:
    for candidate in shortlist:
        if (
            candidate["_stability"] == "context_robust"
            and geometric_simplicity(candidate) == "simple_predefined_geometric_band"
            and 0.20 <= candidate["_total_count"] / EXPECTED_ROW_COUNT <= 0.40
            and maximum_context_imbalance(candidate) <= 0.25
            and candidate["_context_mix"] == "balanced_context_mix"
        ):
            return candidate
    if not shortlist:
        raise ValueError("No shortlist candidate available for primary selection.")
    return shortlist[0]


def choose_secondary(shortlist: list[dict[str, Any]], primary: dict[str, Any], allow_secondary: bool) -> dict[str, Any] | None:
    if not allow_secondary:
        return None
    primary_value = primary["_threshold"]
    for candidate in shortlist:
        if candidate["candidate_id"] == primary["candidate_id"]:
            continue
        if (
            candidate["_stability"] == "context_robust"
            and geometric_simplicity(candidate) == "simple_predefined_geometric_band"
            and candidate["_threshold"] >= primary_value * 2.0
            and candidate["_threshold"] <= 0.20
            and candidate["_min_side"] >= MINIMUM_SIDE_INSIDE_PER_CONTEXT
        ):
            return candidate
    return None


def decision_rows(primary: dict[str, Any], secondary: dict[str, Any] | None) -> list[dict[str, Any]]:
    rows = [decision_row("primary", primary, 1, "main comparison threshold")]
    if secondary is not None:
        rows.append(decision_row("secondary_sensitivity", secondary, 2, "broader sensitivity threshold"))
    return rows


def decision_row(role: str, candidate: dict[str, Any], rank: int, comparison_role: str) -> dict[str, Any]:
    basis = (
        "Selected by context robustness, sufficient per-context and per-side counts, "
        "controlled side imbalance, context mix, geometric simplicity, and redundancy review."
    )
    return {
        "decision_role": role,
        "candidate_id": candidate["candidate_id"],
        "threshold_type": candidate["threshold_type"],
        "threshold_value": candidate["threshold_value"],
        "selected": "yes",
        "selection_rank": rank,
        "selection_basis": basis,
        "total_count_inside": candidate["_total_count"],
        "total_fraction_inside": candidate["total_fraction_inside"],
        "rcvr_800_count_inside": candidate["_rcvr_800_count"],
        "rcvr1_2_count_inside": candidate["_rcvr1_2_count"],
        "minimum_context_count": candidate["_min_context"],
        "minimum_side_count": candidate["_min_side"],
        "overall_normalized_imbalance": fmt_float(candidate["_overall_imbalance"]),
        "rcvr_800_normalized_imbalance": fmt_float(candidate["_rcvr_800_imbalance"]),
        "rcvr1_2_normalized_imbalance": fmt_float(candidate["_rcvr1_2_imbalance"]),
        "context_dominance_ratio": fmt_float(candidate["_dominance"]),
        "context_mix_status": candidate["_context_mix"],
        "candidate_stability_status": candidate["_stability"],
        "comparison_role": comparison_role,
        "decision_status": "selected_for_group_preparation",
        "notes": "Selection is a diagnostic sampling decision only.",
    }


def prepare_groups(
    rows: list[dict[str, Any]], primary: dict[str, Any], secondary: dict[str, Any] | None
) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    primary_threshold = primary["_threshold"]
    secondary_threshold = secondary["_threshold"] if secondary is not None else None
    for row in rows:
        absolute = float(row["_absolute"])
        primary_group = (
            "inside_primary_threshold"
            if absolute <= primary_threshold
            else "outside_primary_threshold"
        )
        if secondary_threshold is None:
            secondary_group = "not_applicable"
            secondary_text = ""
        else:
            secondary_group = (
                "inside_secondary_threshold"
                if absolute <= secondary_threshold
                else "outside_secondary_threshold"
            )
            secondary_text = fmt_float(secondary_threshold)
        output.append(
            {
                "source_row_index": row["source_row_index"],
                "orbital_phase": row["orbital_phase"],
                "signed_phase_offset": row["signed_phase_offset"],
                "absolute_phase_distance": row["absolute_phase_distance"],
                "receiver": row["receiver"],
                "backend": row["backend"],
                "context_name": row["context_name"],
                "primary_threshold": fmt_float(primary_threshold),
                "primary_group": primary_group,
                "secondary_threshold": secondary_text,
                "secondary_group": secondary_group,
                "threshold_source_candidate_id": primary["candidate_id"],
                "grouping_rule": "inside uses absolute_phase_distance <= primary threshold; outside uses > primary threshold",
                "group_preparation_status": "prepared",
                "notes": "Technical comparison-group preparation only.",
            }
        )
    return output


def composition_status(difference: float) -> str:
    if difference < COMPOSITION_COMPARABLE_MAX:
        return "composition_comparable"
    if difference < COMPOSITION_MILD_MAX:
        return "mild_composition_shift"
    if difference < COMPOSITION_MODERATE_MAX:
        return "moderate_composition_shift"
    return "strong_composition_shift"


def balance_status(imbalance: float) -> str:
    if imbalance <= 0.10:
        return "approximately_balanced"
    if imbalance <= 0.25:
        return "mildly_imbalanced"
    if imbalance <= 0.50:
        return "moderately_imbalanced"
    return "strongly_imbalanced"


def build_group_balance(
    rows: list[dict[str, Any]], primary: dict[str, Any], secondary: dict[str, Any] | None
) -> list[dict[str, Any]]:
    decisions = [("primary", primary)]
    if secondary is not None:
        decisions.append(("secondary_sensitivity", secondary))
    output: list[dict[str, Any]] = []
    for role, candidate in decisions:
        threshold = candidate["_threshold"]
        inside_all = [row for row in rows if float(row["_absolute"]) <= threshold]
        outside_all = [row for row in rows if float(row["_absolute"]) > threshold]
        inside_shares = {
            context: sum(1 for row in inside_all if row["context_name"] == context) / max(len(inside_all), 1)
            for context in ROW_CONTEXTS
        }
        outside_shares = {
            context: sum(1 for row in outside_all if row["context_name"] == context) / max(len(outside_all), 1)
            for context in ROW_CONTEXTS
        }
        max_comp_diff = max(
            abs(inside_shares[context] - outside_shares[context]) for context in ROW_CONTEXTS
        )
        for context in CONTEXTS:
            selected = rows if context == "overall" else [row for row in rows if row["context_name"] == context]
            inside = [row for row in selected if float(row["_absolute"]) <= threshold]
            outside = [row for row in selected if float(row["_absolute"]) > threshold]
            pre = sum(1 for row in inside if float(row["_signed"]) < 0.0)
            post = sum(1 for row in inside if float(row["_signed"]) > 0.0)
            imbalance = abs(pre - post) / max(pre + post, 1)
            if context == "overall":
                share_inside = "1"
                share_outside = "1"
                comp_diff = max_comp_diff
            else:
                share_inside = float_fraction_text(inside_shares[context])
                share_outside = float_fraction_text(outside_shares[context])
                comp_diff = abs(inside_shares[context] - outside_shares[context])
            output.append(
                {
                    "decision_role": role,
                    "threshold_value": candidate["threshold_value"],
                    "scope": context,
                    "context_name": context,
                    "total_count": len(selected),
                    "inside_count": len(inside),
                    "outside_count": len(outside),
                    "inside_fraction": fraction_text(len(inside), len(selected)),
                    "pre_inside_count": pre,
                    "post_inside_count": post,
                    "inside_normalized_imbalance": fmt_float(imbalance),
                    "context_share_inside": share_inside,
                    "context_share_outside": share_outside,
                    "context_composition_difference": float_fraction_text(comp_diff),
                    "composition_status": composition_status(comp_diff),
                    "balance_status": balance_status(imbalance),
                    "notes": "Balance summary for prepared inside/outside comparison groups.",
                }
            )
    return output


def rationale_rows(primary: dict[str, Any], shortlist: list[dict[str, Any]], secondary: dict[str, Any] | None) -> list[dict[str, Any]]:
    alternative = next((candidate for candidate in shortlist if candidate["candidate_id"] != primary["candidate_id"]), None)
    alt_value = alternative["threshold_value"] if alternative else ""
    alt_label = alternative["candidate_id"] if alternative else "none"
    rows = [
        (
            "context robustness",
            primary["_stability"],
            alternative["_stability"] if alternative else "",
            "kept primary ahead of less direct alternatives",
            "SHAPIROMART16 threshold candidate context reanalysis",
        ),
        (
            "per-context count",
            f"min_context={primary['_min_context']}",
            f"{alt_label} min_context={alternative['_min_context']}" if alternative else "",
            "selected candidate has sufficient rows in both contexts",
            "SHAPIROMART16 threshold candidate context reanalysis",
        ),
        (
            "pre/post side count",
            f"min_side={primary['_min_side']}",
            f"{alt_label} min_side={alternative['_min_side']}" if alternative else "",
            "selected candidate has non-empty side support in both contexts",
            "SHAPIROMART16 threshold candidate context reanalysis",
        ),
        (
            "side balance",
            f"max_context_imbalance={fmt_float(maximum_context_imbalance(primary))}",
            f"{alt_label} max_context_imbalance={fmt_float(maximum_context_imbalance(alternative))}" if alternative else "",
            "selected candidate has low context-side imbalance",
            "SHAPIROMART16 threshold candidate context reanalysis",
        ),
        (
            "geometric simplicity",
            geometric_simplicity(primary),
            geometric_simplicity(alternative) if alternative else "",
            "simple predefined band preferred over empirical or density-edge values",
            "SHAPIROMART14 threshold candidate inventory",
        ),
        (
            "secondary diagnostic scale",
            secondary["threshold_value"] if secondary else "not selected",
            primary["threshold_value"],
            "secondary kept as broader sensitivity threshold only" if secondary else "no secondary threshold selected",
            "SHAPIROMART17 deterministic selection rules",
        ),
    ]
    output: list[dict[str, Any]] = []
    for index, (criterion, selected_assessment, alt_assessment, effect, source) in enumerate(rows, 1):
        output.append(
            {
                "rationale_order": index,
                "criterion": criterion,
                "selected_candidate_value": primary["threshold_value"],
                "best_alternative_value": alt_value,
                "selected_candidate_assessment": selected_assessment,
                "alternative_assessment": alt_assessment,
                "decision_effect": effect,
                "evidence_source": source,
                "notes": "Decision uses sampling and robustness fields only.",
            }
        )
    return output


def final_status_row(
    candidates: list[dict[str, Any]],
    consolidation: list[dict[str, Any]],
    shortlist: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    prepared: list[dict[str, Any]],
    group_balance: list[dict[str, Any]],
    primary: dict[str, Any] | None,
    secondary: dict[str, Any] | None,
) -> dict[str, Any]:
    if primary is None:
        status = "no_threshold_selected_from_current_candidates"
    elif len(prepared) != EXPECTED_ROW_COUNT:
        status = "threshold_selected_exposure_preparation_partial"
    elif len(candidates) != EXPECTED_CANDIDATE_COUNT or len(consolidation) != EXPECTED_CANDIDATE_COUNT:
        status = "threshold_consolidation_failed"
    else:
        status = "threshold_selected_and_exposure_comparison_prepared"
    receiver_context_preserved = all(row.get("context_name") in ROW_CONTEXTS for row in prepared)
    return {
        "research_block": RESEARCH_BLOCK,
        "candidate_count_input": len(candidates),
        "candidate_count_consolidated": len(consolidation),
        "shortlist_created": "yes" if shortlist else "no",
        "shortlist_count": len(shortlist),
        "primary_threshold_selected": "yes" if primary is not None else "no",
        "primary_threshold_value": primary["threshold_value"] if primary is not None else "",
        "secondary_threshold_selected": "yes" if secondary is not None else "no",
        "secondary_threshold_value": secondary["threshold_value"] if secondary is not None else "",
        "selection_based_only_on_sampling_and_robustness": "yes",
        "prepared_group_rows": len(prepared),
        "expected_group_rows": EXPECTED_ROW_COUNT,
        "all_rows_grouped": "yes" if len(prepared) == EXPECTED_ROW_COUNT else "no",
        "receiver_backend_context_preserved": "yes" if receiver_context_preserved else "no",
        "primary_group_balance_assessed": "yes" if any(row["decision_role"] == "primary" for row in group_balance) else "no",
        "context_composition_assessed": "yes" if group_balance else "no",
        "exposure_analysis_performed": "no",
        "fingerprint_comparison_performed": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "model_fit_performed": "no",
        "physical_interpretation_performed": "no",
        "database_access": "none",
        "additional_gate_created": "no",
        "final_status": status,
        "recommended_next_action": "Use the prepared comparison groups in a separately specified analysis block.",
        "limitations": "This block selects diagnostic thresholds from sampling and robustness criteria only; no later comparison has been performed.",
    }


def build_readout(
    consolidation: list[dict[str, Any]],
    shortlist: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    group_balance: list[dict[str, Any]],
    final_row: dict[str, Any],
) -> str:
    primary = next(row for row in decisions if row["decision_role"] == "primary")
    secondary = next((row for row in decisions if row["decision_role"] == "secondary_sensitivity"), None)
    shortlist_lines = [
        f"- {row['candidate_id']}: threshold={row['threshold_value']}, status={row['candidate_stability_status']}"
        for row in shortlist
    ]
    primary_balances = [row for row in group_balance if row["decision_role"] == "primary"]
    balance_lines = [
        (
            f"- {row['context_name']}: inside={row['inside_count']}, outside={row['outside_count']}, "
            f"pre_inside={row['pre_inside_count']}, post_inside={row['post_inside_count']}, "
            f"composition={row['composition_status']}"
        )
        for row in primary_balances
    ]
    robust_count = sum(1 for row in consolidation if row["candidate_stability_status"] == "context_robust")
    redundant_count = sum(1 for row in consolidation if row["consolidation_status"] == "not_shortlisted_redundant")
    return "\n".join(
        [
            "# SHAPIROMART17 Readout",
            "",
            "## 1. Purpose",
            "Consolidate existing threshold candidates and prepare row-level inside/outside comparison groups.",
            "",
            "## 2. Input Evidence Basis",
            "Inputs are limited to SHAPIROMART14 candidate diagnostics, SHAPIROMART15 enriched geometry, and SHAPIROMART16 context reanalysis.",
            "",
            "## 3. Candidate Consolidation",
            f"Candidates consolidated: {len(consolidation)}. Context robust candidates: {robust_count}.",
            "",
            "## 4. Exclusion and Redundancy Review",
            f"Redundant candidates not shortlisted: {redundant_count}. Minimums used: total >= 100, context >= 40, side per context >= 15.",
            "",
            "## 5. Threshold Shortlist",
            *shortlist_lines,
            "",
            "## 6. Primary Threshold Decision",
            f"Primary diagnostic threshold: {primary['threshold_value']} from {primary['candidate_id']}.",
            "Selection basis: sampling robustness, context balance, side support, simple predefined geometry, and low redundancy.",
            "",
            "## 7. Optional Secondary Sensitivity Threshold",
            (
                f"Secondary sensitivity threshold: {secondary['threshold_value']} from {secondary['candidate_id']}."
                if secondary
                else "No secondary sensitivity threshold was selected."
            ),
            "",
            "## 8. Prepared Comparison Groups",
            f"Prepared group rows: {final_row['prepared_group_rows']}. Rule: absolute_phase_distance <= primary threshold is inside.",
            "",
            "## 9. Group Balance and Context Composition",
            *balance_lines,
            "",
            "## 10. Consolidated Result",
            f"final_status = {final_row['final_status']}.",
            "",
            "## 11. Next Scientific Analysis",
            str(final_row["recommended_next_action"]),
            "",
            "## 12. Limitations",
            str(final_row["limitations"]),
            "exposure_analysis_performed = no.",
            "fingerprint_comparison_performed = no.",
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
    consolidation: list[dict[str, Any]],
    shortlist: list[dict[str, Any]],
    decisions: list[dict[str, Any]],
    prepared: list[dict[str, Any]],
    group_balance: list[dict[str, Any]],
    final_row: dict[str, Any],
) -> dict[str, Any]:
    primary = next(row for row in decisions if row["decision_role"] == "primary")
    secondary = next((row for row in decisions if row["decision_role"] == "secondary_sensitivity"), None)
    prepared_counts = Counter(row["primary_group"] for row in prepared)
    status_counts = Counter(row["consolidation_status"] for row in consolidation)
    return {
        "research_block": RESEARCH_BLOCK,
        "inputs_read": {
            "candidate_input": str(args.candidate_input),
            "context_reanalysis_input": str(args.context_reanalysis_input),
            "enriched_geometry_input": str(args.enriched_geometry_input),
        },
        "fixed_minimums": {
            "minimum_total_inside": MINIMUM_TOTAL_INSIDE,
            "minimum_context_inside": MINIMUM_CONTEXT_INSIDE,
            "minimum_side_inside_per_context": MINIMUM_SIDE_INSIDE_PER_CONTEXT,
        },
        "candidate_count": len(consolidation),
        "consolidation_status_counts": dict(status_counts),
        "shortlist": shortlist,
        "decision": {
            "primary": primary,
            "secondary_sensitivity": secondary,
        },
        "prepared_group_counts": dict(prepared_counts),
        "primary_group_balance": [row for row in group_balance if row["decision_role"] == "primary"],
        "boundaries": {
            "selection_based_only_on_sampling_and_robustness": "yes",
            "exposure_analysis_performed": "no",
            "fingerprint_comparison_performed": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "model_fit_performed": "no",
            "physical_interpretation_performed": "no",
            "database_access": "none",
            "additional_gate_created": "no",
        },
        "final_status": final_row,
        "output_dir": str(args.output_dir),
    }


def verify_outputs(output_dir: Path) -> None:
    observed = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    expected = sorted(OUTPUT_FILES)
    if observed != expected:
        raise RuntimeError(f"Output file set mismatch. Expected {expected}, observed {observed}.")


def main() -> None:
    args = parse_args()
    if args.max_shortlist_size < 1 or args.max_shortlist_size > 5:
        raise ValueError("--max-shortlist-size must be between 1 and 5.")
    validate_output_dir(args.output_dir, args.overwrite)
    validate_upstream_inputs()

    candidates = load_candidates(args.candidate_input, args.context_reanalysis_input)
    enriched_rows = load_enriched_rows(args.enriched_geometry_input)
    consolidation, shortlist_candidates = build_consolidation(candidates, args.max_shortlist_size)
    primary = choose_primary(shortlist_candidates)
    secondary = choose_secondary(shortlist_candidates, primary, args.allow_secondary_threshold)
    decisions = decision_rows(primary, secondary)
    prepared = prepare_groups(enriched_rows, primary, secondary)
    group_balance = build_group_balance(enriched_rows, primary, secondary)
    rationale = rationale_rows(primary, shortlist_candidates, secondary)
    final_row = final_status_row(
        candidates,
        consolidation,
        shortlist_candidates,
        decisions,
        prepared,
        group_balance,
        primary,
        secondary,
    )
    readout = build_readout(consolidation, shortlist_rows(shortlist_candidates), decisions, group_balance, final_row)
    summary = build_summary(
        args,
        consolidation,
        shortlist_rows(shortlist_candidates),
        decisions,
        prepared,
        group_balance,
        final_row,
    )

    write_text(args.output_dir / READOUT_MD, readout)
    write_json(args.output_dir / SUMMARY_JSON, summary)
    write_csv(args.output_dir / CANDIDATE_CONSOLIDATION_CSV, consolidation, CANDIDATE_CONSOLIDATION_FIELDS)
    write_csv(args.output_dir / THRESHOLD_SHORTLIST_CSV, shortlist_rows(shortlist_candidates), THRESHOLD_SHORTLIST_FIELDS)
    write_csv(args.output_dir / THRESHOLD_DECISION_CSV, decisions, THRESHOLD_DECISION_FIELDS)
    write_csv(args.output_dir / PREPARED_GROUPS_CSV, prepared, PREPARED_GROUPS_FIELDS)
    write_csv(args.output_dir / GROUP_BALANCE_CSV, group_balance, GROUP_BALANCE_FIELDS)
    write_csv(args.output_dir / DECISION_RATIONALE_CSV, rationale, DECISION_RATIONALE_FIELDS)
    write_csv(args.output_dir / FINAL_STATUS_CSV, [final_row], FINAL_STATUS_FIELDS)
    verify_outputs(args.output_dir)


if __name__ == "__main__":
    main()
