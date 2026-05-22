#!/usr/bin/env python3
"""QSB-ST COMP01-WIFM01B diagnostic metric sensitivity sweep runner."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "PyYAML is required to read the WIFM01B config. Activate the project environment or install PyYAML."
    ) from exc


REQUIRED_TOP_LEVEL_KEYS = [
    "block_id",
    "route_name",
    "sweep_version",
    "run_id",
    "output_dir",
    "curated_variants_only",
    "phase_period",
    "baseline_source",
    "stability_thresholds",
    "base_coordinate_scales",
    "base_weights",
    "weight_variants",
    "scale_variants",
    "claim_boundary",
    "output_files",
]

REQUIRED_BASELINE_SUMMARY = {
    "fingerprint_count": 10,
    "comparison_pair_count": 5,
    "all_expected_behaviors_met": True,
    "warning_review_count": 0,
}

REQUIRED_CASE_FAMILIES = {
    "same_relational_identity",
    "phase_wrap_equivalent",
    "same_looking_not_same_delta_k",
    "same_looking_not_same_slope_intercept",
    "mixed_ambiguity_case",
}

REQUIRED_LABELS = {
    "metric_equivalent_expected",
    "phase_wrap_corrected_by_circular_metric",
    "noncompact_difference_preserved",
    "local_shape_difference_preserved",
    "mixed_ambiguity_preserved",
    "diagnostic_warning_review_needed",
}

ALLOWED_STABILITY_LABELS = {
    "baseline_reference",
    "stable_expected_behavior_preserved",
    "sensitivity_warning_review_needed",
    "expected_ambiguity_shift",
    "diagnostic_failure_review_needed",
}

ALLOWED_OUTPUT_NAMES = {
    "summary_json",
    "readout_md",
    "sweep_variant_summary_csv",
    "pair_metric_sweep_long_csv",
    "case_family_stability_summary_csv",
    "label_stability_summary_csv",
    "phase_wrap_stability_summary_csv",
    "noncompact_separation_stability_summary_csv",
    "ambiguity_stability_summary_csv",
    "resolved_config_json",
}

WEIGHT_KEYS = [
    "delta_k",
    "delta_phase",
    "slope_diff",
    "intercept_diff",
    "amplitude_diff",
]

SCALE_KEYS = [
    "delta_k",
    "slope_diff",
    "intercept_diff",
    "amplitude_diff",
]

PAIR_FIELDS = [
    "variant_id",
    "pair_id",
    "case_family",
    "expected_relation",
    "naive_phase_delta",
    "circular_phase_delta",
    "naive_metric_distance",
    "circular_metric_distance",
    "distance_delta_naive_minus_circular",
    "diagnostic_decision_label",
    "baseline_decision_label",
    "label_changed_from_baseline",
    "distance_shift_from_baseline",
    "diagnostic_reason",
    "claim_boundary",
]

VARIANT_FIELDS = [
    "variant_id",
    "variant_family",
    "variant_description",
    "weight_delta_k",
    "weight_delta_phase",
    "weight_slope_diff",
    "weight_intercept_diff",
    "weight_amplitude_diff",
    "scale_delta_k",
    "scale_slope_diff",
    "scale_intercept_diff",
    "scale_amplitude_diff",
    "all_expected_behaviors_met",
    "warning_review_count",
    "phase_wrap_corrected_count",
    "noncompact_separation_preserved_count",
    "mixed_ambiguity_preserved_count",
    "stability_label",
    "claim_boundary",
]

CASE_FAMILY_FIELDS = [
    "case_family",
    "variant_count",
    "stable_variant_count",
    "changed_label_variant_count",
    "warning_variant_count",
    "baseline_label",
    "observed_labels",
    "stability_summary",
    "claim_boundary",
]

LABEL_FIELDS = [
    "diagnostic_decision_label",
    "baseline_count",
    "min_count_across_variants",
    "max_count_across_variants",
    "variant_count_with_label",
    "interpretation_boundary",
]

METRIC_SUMMARY_FIELDS = [
    "metric",
    "value",
    "interpretation_boundary",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run WIFM01B diagnostic weight/scale sensitivity sweep over WIFM01 toy fingerprints."
    )
    parser.add_argument("--config", required=True, help="Path to WIFM01B YAML config.")
    return parser.parse_args()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def resolve_path(root: Path, value: str | None) -> Path:
    if not value:
        raise SystemExit("Config path value is required.")
    path = Path(value)
    return path if path.is_absolute() else root / path


def read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing YAML file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"YAML did not parse to a mapping: {path}")
    return data


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"Missing JSON file: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"JSON did not parse to a mapping: {path}")
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"Missing CSV file: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def safe_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return number


def required_float(value: Any, label: str) -> float:
    number = safe_float(value)
    if number is None:
        raise SystemExit(f"{label} must be numeric")
    return number


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True)
    return str(value)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_cell(row.get(field, "")) for field in fields})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def validate_wifm01b_config(config: dict[str, Any], output_dir: Path, root: Path) -> None:
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in config]
    if missing:
        raise SystemExit(f"Missing required WIFM01B config keys: {missing}")

    if config.get("block_id") != "QSB-ST-COMP01-WIFM01B":
        raise SystemExit("block_id must be QSB-ST-COMP01-WIFM01B")
    if config.get("sweep_version") != "wifm01b_weight_scale_sensitivity_v1":
        raise SystemExit("Unexpected sweep_version")
    if config.get("curated_variants_only") is not True:
        raise SystemExit("First WIFM01B runner requires curated_variants_only: true")

    expected_output_dir = root / "runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open"
    if output_dir.resolve() != expected_output_dir.resolve():
        raise SystemExit(f"Output directory must be {expected_output_dir}")

    output_files = config.get("output_files") or {}
    if set(output_files) != ALLOWED_OUTPUT_NAMES:
        raise SystemExit("output_files must contain exactly the allowed WIFM01B output keys")

    validate_weights(config.get("base_weights"), "base_weights")
    validate_scales(config.get("base_coordinate_scales"), "base_coordinate_scales")
    validate_thresholds(config.get("stability_thresholds"))

    if not isinstance(config.get("weight_variants"), list) or not config["weight_variants"]:
        raise SystemExit("weight_variants must be a non-empty list")
    if not isinstance(config.get("scale_variants"), list) or not config["scale_variants"]:
        raise SystemExit("scale_variants must be a non-empty list")


def validate_thresholds(thresholds: Any) -> None:
    if not isinstance(thresholds, dict):
        raise SystemExit("stability_thresholds must be a mapping")
    for key in [
        "near_zero_distance",
        "noncompact_separation_min",
        "ambiguity_min_distance",
        "ambiguity_max_distance",
    ]:
        if required_float(thresholds.get(key), f"stability_thresholds.{key}") < 0:
            raise SystemExit(f"stability_thresholds.{key} must be non-negative")


def validate_weights(weights: Any, label: str) -> None:
    if not isinstance(weights, dict):
        raise SystemExit(f"{label} must be a mapping")
    for key in WEIGHT_KEYS:
        if required_float(weights.get(key), f"{label}.{key}") < 0:
            raise SystemExit(f"{label}.{key} must be non-negative")


def validate_scales(scales: Any, label: str) -> None:
    if not isinstance(scales, dict):
        raise SystemExit(f"{label} must be a mapping")
    for key in SCALE_KEYS:
        if required_float(scales.get(key), f"{label}.{key}") == 0:
            raise SystemExit(f"{label}.{key} must be non-zero")


def validate_baseline_config(config: dict[str, Any]) -> None:
    for key in ["toy_fingerprints", "toy_pairs", "thresholds", "phase_period"]:
        if key not in config:
            raise SystemExit(f"Baseline WIFM01 config missing key: {key}")
    fingerprints = config.get("toy_fingerprints")
    pairs = config.get("toy_pairs")
    if not isinstance(fingerprints, list) or not fingerprints:
        raise SystemExit("Baseline toy_fingerprints must be a non-empty list")
    if not isinstance(pairs, list) or not pairs:
        raise SystemExit("Baseline toy_pairs must be a non-empty list")
    fingerprint_ids = {row.get("fingerprint_id") for row in fingerprints if isinstance(row, dict)}
    families = {str(row.get("case_family")) for row in pairs if isinstance(row, dict)}
    missing_families = REQUIRED_CASE_FAMILIES - families
    if missing_families:
        raise SystemExit(f"Baseline toy_pairs missing families: {sorted(missing_families)}")
    for index, pair in enumerate(pairs):
        for field in ["pair_id", "left_fingerprint_id", "right_fingerprint_id", "case_family", "expected_relation"]:
            if field not in pair:
                raise SystemExit(f"Baseline toy_pairs[{index}] missing {field}")
        for field in ["left_fingerprint_id", "right_fingerprint_id"]:
            if pair[field] not in fingerprint_ids:
                raise SystemExit(f"Baseline toy_pairs[{index}] references unknown {field}: {pair[field]}")


def validate_baseline_summary(summary: dict[str, Any], expected_block_id: str) -> None:
    if summary.get("block_id") != expected_block_id:
        raise SystemExit(f"Baseline summary block_id must be {expected_block_id}")
    for key, expected in REQUIRED_BASELINE_SUMMARY.items():
        if summary.get(key) != expected:
            raise SystemExit(f"Baseline summary {key} must be {expected!r}, got {summary.get(key)!r}")


def validate_baseline_pair_metrics(rows: list[dict[str, str]], internal_baseline_rows: list[dict[str, Any]]) -> None:
    csv_by_pair = {row["pair_id"]: row for row in rows}
    for row in internal_baseline_rows:
        pair_id = str(row["pair_id"])
        if pair_id not in csv_by_pair:
            raise SystemExit(f"Baseline pair metrics missing pair_id: {pair_id}")
        csv_label = csv_by_pair[pair_id].get("diagnostic_decision_label")
        if csv_label != row["diagnostic_decision_label"]:
            raise SystemExit(f"Baseline label mismatch for {pair_id}: {csv_label} vs {row['diagnostic_decision_label']}")


def normalized_delta(left: Any, right: Any, scale: Any) -> float:
    scale_value = required_float(scale, "normalization scale")
    if scale_value == 0:
        raise SystemExit("Normalization scale must be non-zero")
    left_value = required_float(left, "left fingerprint coordinate")
    right_value = required_float(right, "right fingerprint coordinate")
    return (left_value - right_value) / scale_value


def phase_delta(left: Any, right: Any, phase_period: float) -> tuple[float, float]:
    left_value = required_float(left, "left delta_phase")
    right_value = required_float(right, "right delta_phase")
    naive_phase_delta = abs(left_value - right_value)
    reduced = naive_phase_delta % phase_period
    circular_phase_delta = min(reduced, phase_period - reduced)
    return naive_phase_delta, circular_phase_delta


def weighted_distance(
    delta_k_component: float,
    phase_component: float,
    slope_diff_component: float,
    intercept_diff_component: float,
    amplitude_diff_component: float,
    weights: dict[str, Any],
) -> float:
    value = (
        required_float(weights["delta_k"], "weights.delta_k") * delta_k_component**2
        + required_float(weights["delta_phase"], "weights.delta_phase") * phase_component**2
        + required_float(weights["slope_diff"], "weights.slope_diff") * slope_diff_component**2
        + required_float(weights["intercept_diff"], "weights.intercept_diff") * intercept_diff_component**2
        + required_float(weights["amplitude_diff"], "weights.amplitude_diff") * amplitude_diff_component**2
    )
    return math.sqrt(value)


def diagnostic_label(
    case_family: str,
    delta_k_component: float,
    slope_diff_component: float,
    intercept_diff_component: float,
    naive_phase_delta: float,
    circular_phase_delta: float,
    naive_metric_distance: float,
    circular_metric_distance: float,
    thresholds: dict[str, Any],
) -> tuple[str, str]:
    near_zero = required_float(thresholds.get("near_zero_distance"), "near_zero_distance")
    noncompact_min = required_float(thresholds.get("noncompact_separation_min"), "noncompact_separation_min")
    ambiguity_min = required_float(thresholds.get("ambiguity_min_distance"), "ambiguity_min_distance")
    ambiguity_max = required_float(thresholds.get("ambiguity_max_distance"), "ambiguity_max_distance")

    if case_family == "same_relational_identity":
        if circular_metric_distance <= near_zero:
            return "metric_equivalent_expected", "circular distance is at or below near-zero threshold"
        return "diagnostic_warning_review_needed", "same_relational_identity was not near zero"
    if case_family == "phase_wrap_equivalent":
        if circular_phase_delta < naive_phase_delta and circular_metric_distance < naive_metric_distance:
            return "phase_wrap_corrected_by_circular_metric", "circular phase handling reduces phase and metric distance"
        return "diagnostic_warning_review_needed", "phase wrap was not corrected by circular metric"
    if case_family == "same_looking_not_same_delta_k":
        if abs(delta_k_component) >= noncompact_min:
            return "noncompact_difference_preserved", "delta_k component preserves non-compact separation"
        return "diagnostic_warning_review_needed", "delta_k component did not reach separation threshold"
    if case_family == "same_looking_not_same_slope_intercept":
        local_norm = math.sqrt(slope_diff_component**2 + intercept_diff_component**2)
        if local_norm >= noncompact_min:
            return "local_shape_difference_preserved", "slope/intercept components preserve local separation"
        return "diagnostic_warning_review_needed", "local slope/intercept norm did not reach threshold"
    if case_family == "mixed_ambiguity_case":
        if ambiguity_min <= circular_metric_distance <= ambiguity_max:
            return "mixed_ambiguity_preserved", "circular metric distance remains inside ambiguity band"
        return "diagnostic_warning_review_needed", "mixed case fell outside ambiguity band"
    return "diagnostic_warning_review_needed", "unknown case family"


def build_pair_rows(
    baseline_config: dict[str, Any],
    variant: dict[str, Any],
    thresholds: dict[str, Any],
    phase_period: float,
) -> list[dict[str, Any]]:
    fingerprints = {row["fingerprint_id"]: row for row in baseline_config["toy_fingerprints"]}
    scales = variant["coordinate_scales"]
    weights = variant["weights"]
    claim_boundary = "diagnostic fingerprint metric sensitivity only; no physical metric or identity claim"

    rows: list[dict[str, Any]] = []
    for pair in baseline_config["toy_pairs"]:
        left = fingerprints[pair["left_fingerprint_id"]]
        right = fingerprints[pair["right_fingerprint_id"]]
        delta_k_component = normalized_delta(left["delta_k"], right["delta_k"], scales["delta_k"])
        slope_diff_component = normalized_delta(left["slope_diff"], right["slope_diff"], scales["slope_diff"])
        intercept_diff_component = normalized_delta(left["intercept_diff"], right["intercept_diff"], scales["intercept_diff"])
        amplitude_diff_component = normalized_delta(left["amplitude_diff"], right["amplitude_diff"], scales["amplitude_diff"])
        naive_phase_delta, circular_phase_delta = phase_delta(left["delta_phase"], right["delta_phase"], phase_period)
        naive_metric_distance = weighted_distance(
            delta_k_component,
            naive_phase_delta,
            slope_diff_component,
            intercept_diff_component,
            amplitude_diff_component,
            weights,
        )
        circular_metric_distance = weighted_distance(
            delta_k_component,
            circular_phase_delta,
            slope_diff_component,
            intercept_diff_component,
            amplitude_diff_component,
            weights,
        )
        label, reason = diagnostic_label(
            str(pair["case_family"]),
            delta_k_component,
            slope_diff_component,
            intercept_diff_component,
            naive_phase_delta,
            circular_phase_delta,
            naive_metric_distance,
            circular_metric_distance,
            thresholds,
        )
        rows.append(
            {
                "variant_id": variant["variant_id"],
                "pair_id": pair["pair_id"],
                "case_family": pair["case_family"],
                "expected_relation": pair["expected_relation"],
                "naive_phase_delta": naive_phase_delta,
                "circular_phase_delta": circular_phase_delta,
                "naive_metric_distance": naive_metric_distance,
                "circular_metric_distance": circular_metric_distance,
                "distance_delta_naive_minus_circular": naive_metric_distance - circular_metric_distance,
                "diagnostic_decision_label": label,
                "diagnostic_reason": reason,
                "claim_boundary": claim_boundary,
                "_delta_k_component": delta_k_component,
                "_slope_diff_component": slope_diff_component,
                "_intercept_diff_component": intercept_diff_component,
                "_amplitude_diff_component": amplitude_diff_component,
            }
        )
    return rows


def stats(values: list[float]) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    return min(values), max(values), sum(values) / len(values)


def make_variant_list(config: dict[str, Any]) -> list[dict[str, Any]]:
    base_scales = dict(config["base_coordinate_scales"])
    base_weights = dict(config["base_weights"])
    variants: list[dict[str, Any]] = []

    for index, item in enumerate(config["weight_variants"]):
        weights = dict(item.get("weights") or {})
        validate_weights(weights, f"weight_variants[{index}].weights")
        variants.append(
            {
                "variant_id": item["variant_id"],
                "variant_family": item.get("variant_family", "weight"),
                "variant_description": item.get("variant_description", ""),
                "weights": weights,
                "coordinate_scales": dict(base_scales),
            }
        )

    for index, item in enumerate(config["scale_variants"]):
        scales = dict(item.get("coordinate_scales") or {})
        validate_scales(scales, f"scale_variants[{index}].coordinate_scales")
        variants.append(
            {
                "variant_id": item["variant_id"],
                "variant_family": item.get("variant_family", "scale"),
                "variant_description": item.get("variant_description", ""),
                "weights": dict(base_weights),
                "coordinate_scales": scales,
            }
        )

    variant_ids = [str(row["variant_id"]) for row in variants]
    duplicates = sorted({variant_id for variant_id in variant_ids if variant_ids.count(variant_id) > 1})
    if duplicates:
        raise SystemExit(f"Duplicate variant_id values: {duplicates}")
    return variants


def summarize_variant(variant: dict[str, Any], rows: list[dict[str, Any]], thresholds: dict[str, Any]) -> dict[str, Any]:
    families = {str(row["case_family"]) for row in rows}
    missing_families = REQUIRED_CASE_FAMILIES - families
    phase_rows = [row for row in rows if row["case_family"] == "phase_wrap_equivalent"]
    same_rows = [row for row in rows if row["case_family"] == "same_relational_identity"]
    noncompact_rows = [
        row
        for row in rows
        if row["case_family"] in {"same_looking_not_same_delta_k", "same_looking_not_same_slope_intercept"}
    ]
    ambiguity_rows = [row for row in rows if row["case_family"] == "mixed_ambiguity_case"]

    phase_corrected_count = sum(
        1
        for row in phase_rows
        if float(row["circular_phase_delta"]) < float(row["naive_phase_delta"])
        and float(row["circular_metric_distance"]) < float(row["naive_metric_distance"])
    )
    noncompact_preserved_count = sum(
        1
        for row in noncompact_rows
        if row["diagnostic_decision_label"] in {"noncompact_difference_preserved", "local_shape_difference_preserved"}
    )
    ambiguity_preserved_count = sum(
        1 for row in ambiguity_rows if row["diagnostic_decision_label"] == "mixed_ambiguity_preserved"
    )
    warning_review_count = sum(1 for row in rows if row["diagnostic_decision_label"] == "diagnostic_warning_review_needed")
    all_expected_behaviors_met = all(row["diagnostic_decision_label"] == row["expected_relation"] for row in rows)
    near_zero = required_float(thresholds.get("near_zero_distance"), "near_zero_distance")
    same_identity_near_zero = bool(same_rows) and all(float(row["circular_metric_distance"]) <= near_zero for row in same_rows)

    hard_failure = (
        bool(missing_families)
        or phase_corrected_count != len(phase_rows)
        or not same_identity_near_zero
        or noncompact_preserved_count != len(noncompact_rows)
    )
    mixed_changed = any(row["diagnostic_decision_label"] != row["expected_relation"] for row in ambiguity_rows)
    baseline_variant = variant["variant_id"] in {"baseline_equal_weights", "baseline_scales"}

    if hard_failure:
        stability_label = "diagnostic_failure_review_needed"
    elif baseline_variant and all_expected_behaviors_met and warning_review_count == 0:
        stability_label = "baseline_reference"
    elif all_expected_behaviors_met and warning_review_count == 0:
        stability_label = "stable_expected_behavior_preserved"
    elif mixed_changed and warning_review_count == 0:
        stability_label = "expected_ambiguity_shift"
    elif warning_review_count > 0:
        stability_label = "sensitivity_warning_review_needed"
    else:
        stability_label = "sensitivity_warning_review_needed"

    if stability_label not in ALLOWED_STABILITY_LABELS:
        raise SystemExit(f"Unexpected stability label: {stability_label}")

    return {
        "variant_id": variant["variant_id"],
        "variant_family": variant["variant_family"],
        "variant_description": variant["variant_description"],
        "weight_delta_k": variant["weights"]["delta_k"],
        "weight_delta_phase": variant["weights"]["delta_phase"],
        "weight_slope_diff": variant["weights"]["slope_diff"],
        "weight_intercept_diff": variant["weights"]["intercept_diff"],
        "weight_amplitude_diff": variant["weights"]["amplitude_diff"],
        "scale_delta_k": variant["coordinate_scales"]["delta_k"],
        "scale_slope_diff": variant["coordinate_scales"]["slope_diff"],
        "scale_intercept_diff": variant["coordinate_scales"]["intercept_diff"],
        "scale_amplitude_diff": variant["coordinate_scales"]["amplitude_diff"],
        "all_expected_behaviors_met": all_expected_behaviors_met,
        "warning_review_count": warning_review_count,
        "phase_wrap_corrected_count": phase_corrected_count,
        "noncompact_separation_preserved_count": noncompact_preserved_count,
        "mixed_ambiguity_preserved_count": ambiguity_preserved_count,
        "stability_label": stability_label,
        "claim_boundary": "variant stability label is diagnostic only",
        "_phase_wrap_case_count": len(phase_rows),
        "_noncompact_case_count": len(noncompact_rows),
        "_mixed_ambiguity_case_count": len(ambiguity_rows),
        "_missing_families": sorted(missing_families),
    }


def attach_baseline_columns(
    rows: list[dict[str, Any]],
    baseline_labels: dict[str, str],
    baseline_distances: dict[str, float],
) -> list[dict[str, Any]]:
    output_rows = []
    for row in rows:
        pair_id = str(row["pair_id"])
        baseline_label = baseline_labels.get(pair_id, "")
        baseline_distance = baseline_distances.get(pair_id)
        distance_shift = None if baseline_distance is None else float(row["circular_metric_distance"]) - baseline_distance
        next_row = dict(row)
        next_row["baseline_decision_label"] = baseline_label
        next_row["label_changed_from_baseline"] = bool(baseline_label and row["diagnostic_decision_label"] != baseline_label)
        next_row["distance_shift_from_baseline"] = distance_shift
        output_rows.append(next_row)
    return output_rows


def build_case_family_stability_rows(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        grouped[str(row["case_family"])].append(row)

    rows = []
    for case_family in sorted(grouped):
        case_rows = grouped[case_family]
        by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in case_rows:
            by_variant[str(row["variant_id"])].append(row)
        variant_count = len(by_variant)
        stable_variant_count = sum(
            1
            for rows_for_variant in by_variant.values()
            if all(row["diagnostic_decision_label"] == row["expected_relation"] for row in rows_for_variant)
        )
        changed_label_variant_count = sum(
            1
            for rows_for_variant in by_variant.values()
            if any(row["label_changed_from_baseline"] for row in rows_for_variant)
        )
        warning_variant_count = sum(
            1
            for rows_for_variant in by_variant.values()
            if any(row["diagnostic_decision_label"] == "diagnostic_warning_review_needed" for row in rows_for_variant)
        )
        label_counter = Counter(str(row["diagnostic_decision_label"]) for row in case_rows)
        baseline_label = str(case_rows[0].get("baseline_decision_label", ""))
        summary = (
            "expected diagnostic behavior preserved across all variants"
            if stable_variant_count == variant_count and warning_variant_count == 0
            else "one or more variants require diagnostic review"
        )
        rows.append(
            {
                "case_family": case_family,
                "variant_count": variant_count,
                "stable_variant_count": stable_variant_count,
                "changed_label_variant_count": changed_label_variant_count,
                "warning_variant_count": warning_variant_count,
                "baseline_label": baseline_label,
                "observed_labels": dict(sorted(label_counter.items())),
                "stability_summary": summary,
                "claim_boundary": "case-family stability is diagnostic only",
            }
        )
    return rows


def build_label_stability_rows(
    pair_rows: list[dict[str, Any]],
    baseline_rows: list[dict[str, Any]],
    variant_ids: list[str],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, int]]]:
    baseline_counts = Counter(str(row["diagnostic_decision_label"]) for row in baseline_rows)
    counts_by_variant: dict[str, Counter[str]] = {}
    for variant_id in variant_ids:
        counts_by_variant[variant_id] = Counter(
            str(row["diagnostic_decision_label"]) for row in pair_rows if row["variant_id"] == variant_id
        )

    labels = sorted(REQUIRED_LABELS | set(baseline_counts) | {label for counts in counts_by_variant.values() for label in counts})
    rows = []
    ranges: dict[str, dict[str, int]] = {}
    for label in labels:
        values = [counts_by_variant[variant_id].get(label, 0) for variant_id in variant_ids]
        min_value = min(values) if values else 0
        max_value = max(values) if values else 0
        variant_count_with_label = sum(1 for value in values if value > 0)
        ranges[label] = {
            "baseline_count": baseline_counts.get(label, 0),
            "min": min_value,
            "max": max_value,
            "variant_count_with_label": variant_count_with_label,
        }
        rows.append(
            {
                "diagnostic_decision_label": label,
                "baseline_count": baseline_counts.get(label, 0),
                "min_count_across_variants": min_value,
                "max_count_across_variants": max_value,
                "variant_count_with_label": variant_count_with_label,
                "interpretation_boundary": "label stability is diagnostic only",
            }
        )
    return rows, ranges


def build_phase_wrap_stability_rows(pair_rows: list[dict[str, Any]], variant_ids: list[str]) -> list[dict[str, Any]]:
    phase_rows = [row for row in pair_rows if row["case_family"] == "phase_wrap_equivalent"]
    by_variant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in phase_rows:
        by_variant[str(row["variant_id"])].append(row)
    corrected_variant_count = sum(
        1
        for rows in by_variant.values()
        if rows
        and all(
            float(row["circular_phase_delta"]) < float(row["naive_phase_delta"])
            and float(row["circular_metric_distance"]) < float(row["naive_metric_distance"])
            for row in rows
        )
    )
    distance_deltas = [float(row["distance_delta_naive_minus_circular"]) for row in phase_rows]
    min_delta, max_delta, mean_delta = stats(distance_deltas)
    boundary = "phase-wrap stability is diagnostic only"
    return [
        {"metric": "variant_count", "value": len(variant_ids), "interpretation_boundary": boundary},
        {"metric": "phase_wrap_variant_count", "value": len(by_variant), "interpretation_boundary": boundary},
        {"metric": "phase_wrap_corrected_variant_count", "value": corrected_variant_count, "interpretation_boundary": boundary},
        {
            "metric": "phase_wrap_correction_failure_count",
            "value": len(variant_ids) - corrected_variant_count,
            "interpretation_boundary": boundary,
        },
        {"metric": "min_distance_delta_naive_minus_circular", "value": min_delta, "interpretation_boundary": boundary},
        {"metric": "max_distance_delta_naive_minus_circular", "value": max_delta, "interpretation_boundary": boundary},
        {"metric": "mean_distance_delta_naive_minus_circular", "value": mean_delta, "interpretation_boundary": boundary},
    ]


def build_noncompact_stability_rows(variant_rows: list[dict[str, Any]], variant_count: int) -> list[dict[str, Any]]:
    preserved_counts = [int(row["noncompact_separation_preserved_count"]) for row in variant_rows]
    case_counts = [int(row["_noncompact_case_count"]) for row in variant_rows]
    boundary = "non-compact separation stability is diagnostic only"
    return [
        {"metric": "variant_count", "value": variant_count, "interpretation_boundary": boundary},
        {
            "metric": "noncompact_separation_case_count_per_variant",
            "value": case_counts[0] if case_counts and len(set(case_counts)) == 1 else json.dumps(case_counts),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "noncompact_separation_preserved_min",
            "value": min(preserved_counts) if preserved_counts else None,
            "interpretation_boundary": boundary,
        },
        {
            "metric": "noncompact_separation_preserved_max",
            "value": max(preserved_counts) if preserved_counts else None,
            "interpretation_boundary": boundary,
        },
        {
            "metric": "noncompact_separation_failure_variant_count",
            "value": sum(1 for row in variant_rows if row["noncompact_separation_preserved_count"] != row["_noncompact_case_count"]),
            "interpretation_boundary": boundary,
        },
    ]


def build_ambiguity_stability_rows(variant_rows: list[dict[str, Any]], variant_count: int) -> list[dict[str, Any]]:
    preserved_counts = [int(row["mixed_ambiguity_preserved_count"]) for row in variant_rows]
    case_counts = [int(row["_mixed_ambiguity_case_count"]) for row in variant_rows]
    boundary = "mixed ambiguity stability is diagnostic only"
    return [
        {"metric": "variant_count", "value": variant_count, "interpretation_boundary": boundary},
        {
            "metric": "mixed_ambiguity_case_count_per_variant",
            "value": case_counts[0] if case_counts and len(set(case_counts)) == 1 else json.dumps(case_counts),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "mixed_ambiguity_preserved_count_min",
            "value": min(preserved_counts) if preserved_counts else None,
            "interpretation_boundary": boundary,
        },
        {
            "metric": "mixed_ambiguity_preserved_count_max",
            "value": max(preserved_counts) if preserved_counts else None,
            "interpretation_boundary": boundary,
        },
        {
            "metric": "ambiguity_warning_variant_count",
            "value": sum(
                1
                for row in variant_rows
                if row["mixed_ambiguity_preserved_count"] != row["_mixed_ambiguity_case_count"]
                or row["warning_review_count"] > 0
            ),
            "interpretation_boundary": boundary,
        },
    ]


def build_summary(
    config: dict[str, Any],
    baseline_summary: dict[str, Any],
    variant_rows: list[dict[str, Any]],
    label_ranges: dict[str, dict[str, int]],
    output_files: dict[str, str],
) -> dict[str, Any]:
    claims = dict(config["claim_boundary"])
    variant_count = len(variant_rows)
    return {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "sweep_version": config["sweep_version"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "baseline_source_block_id": config["baseline_source"]["block_id"],
        "baseline_source_summary": {
            "block_id": baseline_summary.get("block_id"),
            "run_id": baseline_summary.get("run_id"),
            "metric_version": baseline_summary.get("metric_version"),
            "fingerprint_count": baseline_summary.get("fingerprint_count"),
            "comparison_pair_count": baseline_summary.get("comparison_pair_count"),
            "case_family_count": baseline_summary.get("case_family_count"),
            "all_expected_behaviors_met": baseline_summary.get("all_expected_behaviors_met"),
            "warning_review_count": baseline_summary.get("warning_review_count"),
        },
        "variant_count": variant_count,
        "weight_variant_count": len(config["weight_variants"]),
        "scale_variant_count": len(config["scale_variants"]),
        "curated_variants_only": config["curated_variants_only"],
        "case_family_count": len(REQUIRED_CASE_FAMILIES),
        "comparison_pair_count_per_variant": baseline_summary.get("comparison_pair_count"),
        "all_variants_expected_behaviors_met": all(row["all_expected_behaviors_met"] for row in variant_rows),
        "variant_warning_review_count": sum(1 for row in variant_rows if row["warning_review_count"] > 0),
        "variant_failure_review_count": sum(
            1 for row in variant_rows if row["stability_label"] == "diagnostic_failure_review_needed"
        ),
        "phase_wrap_all_variants_corrected": all(
            row["phase_wrap_corrected_count"] == row["_phase_wrap_case_count"] for row in variant_rows
        ),
        "noncompact_separation_all_variants_preserved": all(
            row["noncompact_separation_preserved_count"] == row["_noncompact_case_count"] for row in variant_rows
        ),
        "mixed_ambiguity_all_variants_preserved": all(
            row["mixed_ambiguity_preserved_count"] == row["_mixed_ambiguity_case_count"] for row in variant_rows
        ),
        "stability_label_counts": dict(Counter(str(row["stability_label"]) for row in variant_rows)),
        "diagnostic_decision_label_count_ranges": label_ranges,
        "specificity_established": False,
        "phase_is_physical": False,
        "phase_is_synthetic_diagnostic": True,
        "physical_metric_established": False,
        "physical_compact_dimensions_established": False,
        "hilbert_space_reconstruction": False,
        "bridge_confirmation": False,
        "mastermind_status": claims.get("mastermind_status", "parked_not_implemented"),
        "knuth_status": claims.get("knuth_status", "parked_not_implemented"),
        "manifold_status": claims.get("manifold_status", "parked_not_implemented"),
        "claim_boundary": claims,
        "output_files": output_files,
    }


def write_readout(path: Path, summary: dict[str, Any], output_files: dict[str, str]) -> None:
    lines = [
        "# QSB-ST COMP01-WIFM01B Minimal Metric Sensitivity Sweep — Readout",
        "",
        "## 1. Purpose",
        "WIFM01B is diagnostic only. It runs curated weight/scale variants over the WIFM01 toy fingerprints.",
        "",
        "## 2. Baseline input",
        f"- baseline_source_block_id: {summary['baseline_source_block_id']}",
        f"- comparison_pair_count_per_variant: {summary['comparison_pair_count_per_variant']}",
        "",
        "## 3. Sweep variants",
        f"- curated_variants_only: {format_cell(summary['curated_variants_only'])}",
        f"- variant_count: {summary['variant_count']}",
        f"- weight_variant_count: {summary['weight_variant_count']}",
        f"- scale_variant_count: {summary['scale_variant_count']}",
        "",
        "## 4. Stability checks",
        f"- all_variants_expected_behaviors_met: {format_cell(summary['all_variants_expected_behaviors_met'])}",
        f"- variant_warning_review_count: {summary['variant_warning_review_count']}",
        f"- variant_failure_review_count: {summary['variant_failure_review_count']}",
        f"- stability_label_counts: {json.dumps(summary['stability_label_counts'], sort_keys=True)}",
        "",
        "## 5. Phase-wrap stability",
        f"- phase_wrap_all_variants_corrected: {format_cell(summary['phase_wrap_all_variants_corrected'])}",
        "",
        "## 6. Non-compact separation stability",
        f"- noncompact_separation_all_variants_preserved: {format_cell(summary['noncompact_separation_all_variants_preserved'])}",
        "",
        "## 7. Mixed ambiguity stability",
        f"- mixed_ambiguity_all_variants_preserved: {format_cell(summary['mixed_ambiguity_all_variants_preserved'])}",
        "",
        "## 8. Befund",
        "The sweep output is a synthetic diagnostic sensitivity artifact.",
        "It reports whether WIFM01 toy behavior remains stable under explicit curated weight and scale variants.",
        "",
        "## 9. Interpretation",
        "No physical metric is established.",
        "No physical compact dimensions are established.",
        "No Hilbert-space reconstruction is made.",
        "No Bridge confirmation is made.",
        "No diagnostic specificity is established.",
        "",
        "## 10. Hypothese",
        "If the toy behavior remains stable across curated variants, circular phase handling may be methodologically useful inside this diagnostic toy setting.",
        "",
        "## 11. Offene Lücke",
        "- no real data",
        "- no broad control set",
        "- no adversarial case expansion",
        "- no validation of a physical model",
        "- identity space remains open",
        "",
        "## 12. Claim Boundary",
        "- specificity_established: false",
        "- phase_is_physical: false",
        "- phase_is_synthetic_diagnostic: true",
        "- physical_metric_established: false",
        "- physical_compact_dimensions_established: false",
        "- hilbert_space_reconstruction: false",
        "- bridge_confirmation: false",
        "- Mastermind, Knuth, and manifold remain parked",
        "",
        "## 13. Files created",
    ]
    lines.extend(f"- {value}" for value in output_files.values())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def output_paths(config: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    return {key: output_dir / name for key, name in config["output_files"].items()}


def main() -> None:
    args = parse_args()
    root = repo_root()
    config_path = resolve_path(root, args.config)
    config = read_yaml(config_path)
    output_dir = resolve_path(root, config.get("output_dir"))
    validate_wifm01b_config(config, output_dir, root)

    baseline_source = config["baseline_source"]
    baseline_config_path = resolve_path(root, baseline_source.get("config_path"))
    baseline_summary_path = resolve_path(root, baseline_source.get("output_summary"))
    baseline_pair_metrics_path = resolve_path(root, baseline_source.get("output_pair_metrics"))

    baseline_config = read_yaml(baseline_config_path)
    baseline_summary = read_json(baseline_summary_path)
    baseline_pair_metric_rows = read_csv_rows(baseline_pair_metrics_path)
    validate_baseline_config(baseline_config)
    validate_baseline_summary(baseline_summary, baseline_source["block_id"])

    variants = make_variant_list(config)
    phase_period = required_float(config["phase_period"], "phase_period")
    thresholds = config["stability_thresholds"]
    baseline_variant = {
        "variant_id": "baseline_internal_reference",
        "variant_family": "baseline",
        "variant_description": "Internal baseline reference from WIFM01 weights and scales.",
        "weights": dict(config["base_weights"]),
        "coordinate_scales": dict(config["base_coordinate_scales"]),
    }
    baseline_pair_rows = build_pair_rows(baseline_config, baseline_variant, thresholds, phase_period)
    validate_baseline_pair_metrics(baseline_pair_metric_rows, baseline_pair_rows)
    baseline_labels = {str(row["pair_id"]): str(row["diagnostic_decision_label"]) for row in baseline_pair_rows}
    baseline_distances = {str(row["pair_id"]): float(row["circular_metric_distance"]) for row in baseline_pair_rows}

    all_pair_rows: list[dict[str, Any]] = []
    variant_summary_rows: list[dict[str, Any]] = []
    for variant in variants:
        rows = build_pair_rows(baseline_config, variant, thresholds, phase_period)
        rows = attach_baseline_columns(rows, baseline_labels, baseline_distances)
        all_pair_rows.extend(rows)
        variant_summary_rows.append(summarize_variant(variant, rows, thresholds))

    variant_ids = [str(variant["variant_id"]) for variant in variants]
    case_family_rows = build_case_family_stability_rows(all_pair_rows)
    label_rows, label_ranges = build_label_stability_rows(all_pair_rows, baseline_pair_rows, variant_ids)
    phase_rows = build_phase_wrap_stability_rows(all_pair_rows, variant_ids)
    noncompact_rows = build_noncompact_stability_rows(variant_summary_rows, len(variant_ids))
    ambiguity_rows = build_ambiguity_stability_rows(variant_summary_rows, len(variant_ids))

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = output_paths(config, output_dir)
    created_output_files = {key: str(path) for key, path in paths.items()}
    summary = build_summary(config, baseline_summary, variant_summary_rows, label_ranges, created_output_files)

    write_json(paths["summary_json"], summary)
    write_readout(paths["readout_md"], summary, created_output_files)
    write_csv(paths["sweep_variant_summary_csv"], VARIANT_FIELDS, variant_summary_rows)
    write_csv(paths["pair_metric_sweep_long_csv"], PAIR_FIELDS, all_pair_rows)
    write_csv(paths["case_family_stability_summary_csv"], CASE_FAMILY_FIELDS, case_family_rows)
    write_csv(paths["label_stability_summary_csv"], LABEL_FIELDS, label_rows)
    write_csv(paths["phase_wrap_stability_summary_csv"], METRIC_SUMMARY_FIELDS, phase_rows)
    write_csv(paths["noncompact_separation_stability_summary_csv"], METRIC_SUMMARY_FIELDS, noncompact_rows)
    write_csv(paths["ambiguity_stability_summary_csv"], METRIC_SUMMARY_FIELDS, ambiguity_rows)
    write_json(
        paths["resolved_config_json"],
        {
            "original_wifm01b_config": config,
            "baseline_wifm01_config_path": str(baseline_config_path),
            "baseline_wifm01_summary_path": str(baseline_summary_path),
            "baseline_wifm01_pair_metrics_path": str(baseline_pair_metrics_path),
            "resolved_output_directory": str(output_dir),
            "variant_definitions": variants,
            "claim_boundary": config["claim_boundary"],
            "created_output_files": created_output_files,
        },
    )

    print("WIFM01B sensitivity sweep complete")
    print(f"output_dir: {output_dir}")
    print(f"variant_count: {summary['variant_count']}")
    print(f"all_variants_expected_behaviors_met: {format_cell(summary['all_variants_expected_behaviors_met'])}")
    print(f"variant_warning_review_count: {summary['variant_warning_review_count']}")


if __name__ == "__main__":
    main()
