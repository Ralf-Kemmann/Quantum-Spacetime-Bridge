#!/usr/bin/env python3
"""QSB-ST COMP01-WIFM01C diagnostic adversarial/ambiguity stress runner."""

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
        "PyYAML is required to read the WIFM01C config. Activate the project environment or install PyYAML."
    ) from exc


REQUIRED_TOP_LEVEL_KEYS = [
    "block_id",
    "route_name",
    "stress_version",
    "run_id",
    "output_dir",
    "input_mode",
    "phase_period",
    "baseline_source",
    "coordinate_scales",
    "weights",
    "stress_thresholds",
    "stress_fingerprints",
    "stress_pairs",
    "claim_boundary",
    "output_files",
]

REQUIRED_STRESS_FAMILIES = {
    "phase_agrees_delta_k_conflicts",
    "phase_wrap_agrees_shape_conflicts",
    "many_small_differences_accumulate",
    "amplitude_conflict_phase_agrees",
    "ambiguous_balanced_conflict",
    "overcleaning_probe",
    "near_identity_control",
    "baseline_reference_replay",
}

EXPLICIT_STRESS_FAMILIES = REQUIRED_STRESS_FAMILIES - {"baseline_reference_replay"}

BASELINE_LABEL_BY_FAMILY = {
    "same_relational_identity": "metric_equivalent_expected",
    "phase_wrap_equivalent": "phase_wrap_corrected_by_circular_metric",
    "same_looking_not_same_delta_k": "noncompact_difference_preserved",
    "same_looking_not_same_slope_intercept": "local_shape_difference_preserved",
    "mixed_ambiguity_case": "mixed_ambiguity_preserved",
}

EXPECTED_LABEL_BY_STRESS_FAMILY = {
    "phase_agrees_delta_k_conflicts": "adversarial_phase_agreement_noncompact_conflict",
    "phase_wrap_agrees_shape_conflicts": "adversarial_wrap_with_shape_conflict",
    "many_small_differences_accumulate": "cumulative_small_difference_warning",
    "amplitude_conflict_phase_agrees": "amplitude_shape_conflict_warning",
    "ambiguous_balanced_conflict": "ambiguous_multi_channel_review",
    "overcleaning_probe": "overcleaning_risk_detected",
    "near_identity_control": "metric_equivalent_expected",
}

ADVERSARIAL_LABELS = {
    "adversarial_phase_agreement_noncompact_conflict",
    "adversarial_wrap_with_shape_conflict",
    "cumulative_small_difference_warning",
    "amplitude_shape_conflict_warning",
    "ambiguous_multi_channel_review",
    "overcleaning_risk_detected",
}

CLEAN_BASELINE_LABELS = {
    "metric_equivalent_expected",
    "phase_wrap_corrected_by_circular_metric",
}

REQUIRED_BASELINE_SUMMARY = {
    "fingerprint_count": 10,
    "comparison_pair_count": 5,
    "all_expected_behaviors_met": True,
    "warning_review_count": 0,
}

REQUIRED_WIFM01B_SUMMARY = {
    "variant_count": 19,
    "all_variants_expected_behaviors_met": True,
    "variant_warning_review_count": 0,
    "variant_failure_review_count": 0,
}

ALLOWED_OUTPUT_NAMES = {
    "summary_json",
    "readout_md",
    "stress_fingerprint_input_table_csv",
    "stress_pair_metric_comparison_csv",
    "case_family_stress_summary_csv",
    "label_stress_summary_csv",
    "overcleaning_risk_summary_csv",
    "adversarial_channel_conflict_summary_csv",
    "baseline_replay_summary_csv",
    "resolved_config_json",
}

FINGERPRINT_FIELDS = [
    "fingerprint_id",
    "case_family",
    "case_role",
    "delta_k",
    "delta_phase",
    "slope_diff",
    "intercept_diff",
    "amplitude_diff",
    "expected_relation",
    "adversarial_intent",
    "notes",
]

PAIR_FIELDS = [
    "pair_id",
    "left_fingerprint_id",
    "right_fingerprint_id",
    "case_family",
    "expected_relation",
    "naive_phase_delta",
    "circular_phase_delta",
    "delta_k_component",
    "slope_diff_component",
    "intercept_diff_component",
    "amplitude_diff_component",
    "noncompact_conflict_norm",
    "cumulative_difference_norm",
    "naive_metric_distance",
    "circular_metric_distance",
    "distance_delta_naive_minus_circular",
    "diagnostic_decision_label",
    "expected_adversarial_behavior_met",
    "overcleaning_risk_flag",
    "diagnostic_reason",
    "claim_boundary",
]

CASE_FAMILY_FIELDS = [
    "case_family",
    "pair_count",
    "expected_label",
    "observed_labels",
    "expected_adversarial_behavior_met",
    "overcleaning_risk_count",
    "diagnostic_warning_count",
    "stress_interpretation",
    "claim_boundary",
]

LABEL_FIELDS = [
    "diagnostic_decision_label",
    "count",
    "case_families",
    "expected_or_unexpected",
    "interpretation_boundary",
]

SUMMARY_FIELDS = [
    "metric",
    "value",
    "interpretation_boundary",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run WIFM01C diagnostic adversarial/ambiguity stress cases."
    )
    parser.add_argument("--config", required=True, help="Path to WIFM01C YAML config.")
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


def validate_config(config: dict[str, Any], output_dir: Path, root: Path) -> None:
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in config]
    if missing:
        raise SystemExit(f"Missing required WIFM01C config keys: {missing}")
    if config.get("block_id") != "QSB-ST-COMP01-WIFM01C":
        raise SystemExit("block_id must be QSB-ST-COMP01-WIFM01C")
    if config.get("stress_version") != "wifm01c_adversarial_ambiguity_stress_v1":
        raise SystemExit("Unexpected stress_version")
    if config.get("input_mode") != "inline_adversarial_synthetic_cases":
        raise SystemExit("input_mode must be inline_adversarial_synthetic_cases")

    expected_output_dir = root / "runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open"
    if output_dir.resolve() != expected_output_dir.resolve():
        raise SystemExit(f"Output directory must be {expected_output_dir}")

    output_files = config.get("output_files") or {}
    if set(output_files) != ALLOWED_OUTPUT_NAMES:
        raise SystemExit("output_files must contain exactly the allowed WIFM01C output keys")

    validate_scales(config.get("coordinate_scales"), "coordinate_scales")
    validate_weights(config.get("weights"), "weights")
    validate_thresholds(config.get("stress_thresholds"))
    validate_stress_fingerprints(config.get("stress_fingerprints"))
    validate_stress_pairs(config.get("stress_pairs"), config.get("stress_fingerprints"))


def validate_scales(scales: Any, label: str) -> None:
    if not isinstance(scales, dict):
        raise SystemExit(f"{label} must be a mapping")
    for key in ["delta_k", "slope_diff", "intercept_diff", "amplitude_diff"]:
        if required_float(scales.get(key), f"{label}.{key}") == 0:
            raise SystemExit(f"{label}.{key} must be non-zero")


def validate_weights(weights: Any, label: str) -> None:
    if not isinstance(weights, dict):
        raise SystemExit(f"{label} must be a mapping")
    for key in ["delta_k", "delta_phase", "slope_diff", "intercept_diff", "amplitude_diff"]:
        if required_float(weights.get(key), f"{label}.{key}") < 0:
            raise SystemExit(f"{label}.{key} must be non-negative")


def validate_thresholds(thresholds: Any) -> None:
    if not isinstance(thresholds, dict):
        raise SystemExit("stress_thresholds must be a mapping")
    for key in [
        "near_zero_distance",
        "strong_channel_conflict_min",
        "moderate_channel_difference_min",
        "cumulative_warning_distance_min",
        "cumulative_warning_distance_max",
        "ambiguity_min_distance",
        "ambiguity_max_distance",
        "overcleaning_conflict_min",
    ]:
        if required_float(thresholds.get(key), f"stress_thresholds.{key}") < 0:
            raise SystemExit(f"stress_thresholds.{key} must be non-negative")


def validate_stress_fingerprints(rows: Any) -> None:
    if not isinstance(rows, list) or not rows:
        raise SystemExit("stress_fingerprints must be a non-empty list")
    for index, row in enumerate(rows):
        missing = [field for field in FINGERPRINT_FIELDS if field not in row]
        if missing:
            raise SystemExit(f"stress_fingerprints[{index}] missing fields: {missing}")
        for field in ["delta_k", "delta_phase", "slope_diff", "intercept_diff", "amplitude_diff"]:
            required_float(row.get(field), f"stress_fingerprints[{index}].{field}")
    families = {str(row.get("case_family")) for row in rows}
    missing_families = EXPLICIT_STRESS_FAMILIES - families
    if missing_families:
        raise SystemExit(f"stress_fingerprints missing families: {sorted(missing_families)}")


def validate_stress_pairs(rows: Any, fingerprints: Any) -> None:
    if not isinstance(rows, list) or not rows:
        raise SystemExit("stress_pairs must be a non-empty list")
    fingerprint_ids = {row.get("fingerprint_id") for row in fingerprints if isinstance(row, dict)}
    families = set()
    for index, row in enumerate(rows):
        for field in ["pair_id", "left_fingerprint_id", "right_fingerprint_id", "case_family", "expected_relation"]:
            if field not in row:
                raise SystemExit(f"stress_pairs[{index}] missing {field}")
        families.add(str(row["case_family"]))
        for field in ["left_fingerprint_id", "right_fingerprint_id"]:
            if row[field] not in fingerprint_ids:
                raise SystemExit(f"stress_pairs[{index}] references unknown {field}: {row[field]}")
        expected = EXPECTED_LABEL_BY_STRESS_FAMILY.get(str(row["case_family"]))
        if expected and row["expected_relation"] != expected:
            raise SystemExit(f"stress_pairs[{index}] expected_relation must be {expected}")
    missing_families = EXPLICIT_STRESS_FAMILIES - families
    if missing_families:
        raise SystemExit(f"stress_pairs missing families: {sorted(missing_families)}")


def validate_baseline_summary(summary: dict[str, Any]) -> None:
    for key, expected in REQUIRED_BASELINE_SUMMARY.items():
        if summary.get(key) != expected:
            raise SystemExit(f"WIFM01 summary {key} must be {expected!r}, got {summary.get(key)!r}")


def validate_wifm01b_summary(summary: dict[str, Any]) -> None:
    for key, expected in REQUIRED_WIFM01B_SUMMARY.items():
        if summary.get(key) != expected:
            raise SystemExit(f"WIFM01B summary {key} must be {expected!r}, got {summary.get(key)!r}")


def validate_baseline_config(config: dict[str, Any]) -> None:
    for key in ["toy_fingerprints", "toy_pairs"]:
        if key not in config:
            raise SystemExit(f"WIFM01 baseline config missing {key}")
    fingerprint_ids = {row.get("fingerprint_id") for row in config["toy_fingerprints"] if isinstance(row, dict)}
    for index, pair in enumerate(config["toy_pairs"]):
        for field in ["pair_id", "left_fingerprint_id", "right_fingerprint_id", "case_family", "expected_relation"]:
            if field not in pair:
                raise SystemExit(f"WIFM01 baseline toy_pairs[{index}] missing {field}")
        for field in ["left_fingerprint_id", "right_fingerprint_id"]:
            if pair[field] not in fingerprint_ids:
                raise SystemExit(f"WIFM01 baseline toy_pairs[{index}] references unknown {field}: {pair[field]}")
        expected = BASELINE_LABEL_BY_FAMILY.get(str(pair["case_family"]))
        if expected != pair["expected_relation"]:
            raise SystemExit(f"WIFM01 baseline pair expected_relation mismatch for {pair['pair_id']}")


def validate_baseline_pair_metrics(rows: list[dict[str, str]]) -> None:
    by_family = {row.get("case_family"): row.get("diagnostic_decision_label") for row in rows}
    for case_family, expected_label in BASELINE_LABEL_BY_FAMILY.items():
        if by_family.get(case_family) != expected_label:
            raise SystemExit(f"WIFM01 baseline pair metrics mismatch for {case_family}")


def normalized_delta(left: Any, right: Any, scale: Any) -> float:
    scale_value = required_float(scale, "normalization scale")
    if scale_value == 0:
        raise SystemExit("Normalization scale must be non-zero")
    return (required_float(left, "left coordinate") - required_float(right, "right coordinate")) / scale_value


def phase_delta(left: Any, right: Any, phase_period: float) -> tuple[float, float]:
    naive_phase_delta = abs(required_float(left, "left delta_phase") - required_float(right, "right delta_phase"))
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


def wifm01_label(
    original_case_family: str,
    delta_k_component: float,
    slope_diff_component: float,
    intercept_diff_component: float,
    naive_phase_delta: float,
    circular_phase_delta: float,
    naive_metric_distance: float,
    circular_metric_distance: float,
    thresholds: dict[str, Any],
) -> tuple[str, str]:
    near_zero = required_float(thresholds["near_zero_distance"], "near_zero_distance")
    noncompact_min = required_float(thresholds["noncompact_separation_min"], "noncompact_separation_min")
    ambiguity_min = required_float(thresholds["ambiguity_min_distance"], "ambiguity_min_distance")
    ambiguity_max = required_float(thresholds["ambiguity_max_distance"], "ambiguity_max_distance")

    if original_case_family == "same_relational_identity":
        if circular_metric_distance <= near_zero:
            return "metric_equivalent_expected", "baseline replay remained near zero"
        return "diagnostic_warning_review_needed", "baseline same identity replay was not near zero"
    if original_case_family == "phase_wrap_equivalent":
        if circular_phase_delta < naive_phase_delta and circular_metric_distance < naive_metric_distance:
            return "phase_wrap_corrected_by_circular_metric", "baseline phase wrap replay remained corrected"
        return "diagnostic_warning_review_needed", "baseline phase wrap replay was not corrected"
    if original_case_family == "same_looking_not_same_delta_k":
        if abs(delta_k_component) >= noncompact_min:
            return "noncompact_difference_preserved", "baseline delta_k replay preserved separation"
        return "diagnostic_warning_review_needed", "baseline delta_k replay lost separation"
    if original_case_family == "same_looking_not_same_slope_intercept":
        local_norm = math.sqrt(slope_diff_component**2 + intercept_diff_component**2)
        if local_norm >= noncompact_min:
            return "local_shape_difference_preserved", "baseline local-shape replay preserved separation"
        return "diagnostic_warning_review_needed", "baseline local-shape replay lost separation"
    if original_case_family == "mixed_ambiguity_case":
        if ambiguity_min <= circular_metric_distance <= ambiguity_max:
            return "mixed_ambiguity_preserved", "baseline mixed ambiguity replay remained in ambiguity band"
        return "diagnostic_warning_review_needed", "baseline mixed ambiguity replay left ambiguity band"
    return "diagnostic_warning_review_needed", "unknown baseline replay case family"


def stress_label(row: dict[str, Any], thresholds: dict[str, Any]) -> tuple[str, str]:
    case_family = str(row["case_family"])
    near_zero = required_float(thresholds["near_zero_distance"], "near_zero_distance")
    strong_min = required_float(thresholds["strong_channel_conflict_min"], "strong_channel_conflict_min")
    moderate_min = required_float(thresholds["moderate_channel_difference_min"], "moderate_channel_difference_min")
    cumulative_min = required_float(thresholds["cumulative_warning_distance_min"], "cumulative_warning_distance_min")
    cumulative_max = required_float(thresholds["cumulative_warning_distance_max"], "cumulative_warning_distance_max")
    ambiguity_min = required_float(thresholds["ambiguity_min_distance"], "ambiguity_min_distance")
    ambiguity_max = required_float(thresholds["ambiguity_max_distance"], "ambiguity_max_distance")
    overcleaning_min = required_float(thresholds["overcleaning_conflict_min"], "overcleaning_conflict_min")

    delta_k = abs(float(row["delta_k_component"]))
    slope = abs(float(row["slope_diff_component"]))
    intercept = abs(float(row["intercept_diff_component"]))
    amplitude = abs(float(row["amplitude_diff_component"]))
    circular_phase = float(row["circular_phase_delta"])
    naive_phase = float(row["naive_phase_delta"])
    circular_metric = float(row["circular_metric_distance"])
    noncompact_norm = float(row["noncompact_conflict_norm"])
    cumulative_norm = float(row["cumulative_difference_norm"])
    local_shape_norm = math.sqrt(slope**2 + intercept**2)

    if case_family == "near_identity_control":
        all_components_small = all(
            value <= moderate_min for value in [delta_k, circular_phase, slope, intercept, amplitude]
        )
        if circular_metric <= near_zero or all_components_small:
            return "metric_equivalent_expected", "near-identity control remained equivalent"
        return "diagnostic_warning_review_needed", "near-identity control exceeded equivalence conditions"

    if case_family == "phase_agrees_delta_k_conflicts":
        if circular_phase <= moderate_min and delta_k >= strong_min:
            return (
                "adversarial_phase_agreement_noncompact_conflict",
                "phase agreement did not erase strong delta_k conflict",
            )
        return "diagnostic_warning_review_needed", "phase/delta_k adversarial condition was not met"

    if case_family == "phase_wrap_agrees_shape_conflicts":
        if circular_phase < naive_phase and local_shape_norm >= strong_min:
            return (
                "adversarial_wrap_with_shape_conflict",
                "phase wrap was corrected while local-shape conflict remained visible",
            )
        return "diagnostic_warning_review_needed", "wrap/shape adversarial condition was not met"

    if case_family == "many_small_differences_accumulate":
        noncompact_values = [delta_k, slope, intercept, amplitude]
        if all(value < strong_min for value in noncompact_values) and cumulative_min <= cumulative_norm <= cumulative_max:
            return (
                "cumulative_small_difference_warning",
                "distributed moderate differences accumulated into review band",
            )
        return "diagnostic_warning_review_needed", "cumulative warning condition was not met"

    if case_family == "amplitude_conflict_phase_agrees":
        if circular_phase <= moderate_min and amplitude >= strong_min:
            return (
                "amplitude_shape_conflict_warning",
                "phase agreement did not erase strong amplitude conflict",
            )
        return "diagnostic_warning_review_needed", "amplitude conflict condition was not met"

    if case_family == "ambiguous_balanced_conflict":
        if ambiguity_min <= circular_metric <= ambiguity_max and noncompact_norm >= moderate_min:
            return (
                "ambiguous_multi_channel_review",
                "balanced compact/non-compact signals remained review-like",
            )
        return "diagnostic_warning_review_needed", "balanced ambiguity condition was not met"

    if case_family == "overcleaning_probe":
        if circular_phase < naive_phase and noncompact_norm >= overcleaning_min:
            return (
                "overcleaning_risk_detected",
                "phase wrap correction coexists with strong noncompact conflict",
            )
        return "diagnostic_warning_review_needed", "over-cleaning probe condition was not met"

    return "diagnostic_warning_review_needed", "unknown stress case family"


def compute_pair_row(
    pair: dict[str, Any],
    left: dict[str, Any],
    right: dict[str, Any],
    config: dict[str, Any],
    thresholds: dict[str, Any],
    baseline_replay: bool,
) -> dict[str, Any]:
    scales = config["coordinate_scales"]
    weights = config["weights"]
    phase_period = required_float(config["phase_period"], "phase_period")
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
    noncompact_conflict_norm = math.sqrt(
        delta_k_component**2
        + slope_diff_component**2
        + intercept_diff_component**2
        + amplitude_diff_component**2
    )
    cumulative_difference_norm = math.sqrt(
        delta_k_component**2
        + circular_phase_delta**2
        + slope_diff_component**2
        + intercept_diff_component**2
        + amplitude_diff_component**2
    )
    row = {
        "pair_id": pair["pair_id"],
        "left_fingerprint_id": pair["left_fingerprint_id"],
        "right_fingerprint_id": pair["right_fingerprint_id"],
        "case_family": pair["case_family"],
        "expected_relation": pair["expected_relation"],
        "naive_phase_delta": naive_phase_delta,
        "circular_phase_delta": circular_phase_delta,
        "delta_k_component": delta_k_component,
        "slope_diff_component": slope_diff_component,
        "intercept_diff_component": intercept_diff_component,
        "amplitude_diff_component": amplitude_diff_component,
        "noncompact_conflict_norm": noncompact_conflict_norm,
        "cumulative_difference_norm": cumulative_difference_norm,
        "naive_metric_distance": naive_metric_distance,
        "circular_metric_distance": circular_metric_distance,
        "distance_delta_naive_minus_circular": naive_metric_distance - circular_metric_distance,
        "claim_boundary": "diagnostic adversarial stress metric only; no physical metric or identity claim",
    }
    if baseline_replay:
        label, reason = wifm01_label(
            pair["_original_case_family"],
            delta_k_component,
            slope_diff_component,
            intercept_diff_component,
            naive_phase_delta,
            circular_phase_delta,
            naive_metric_distance,
            circular_metric_distance,
            config["_baseline_thresholds"],
        )
    else:
        label, reason = stress_label(row, thresholds)
    row["diagnostic_decision_label"] = label
    row["diagnostic_reason"] = reason
    row["expected_adversarial_behavior_met"] = label == pair["expected_relation"]
    row["overcleaning_risk_flag"] = is_overcleaning_risk(row)
    row["_baseline_replay"] = baseline_replay
    return row


def is_overcleaning_risk(row: dict[str, Any]) -> bool:
    if row["diagnostic_decision_label"] == "overcleaning_risk_detected":
        return True
    conflict_families = {"overcleaning_probe", "phase_wrap_agrees_shape_conflicts"}
    if row["case_family"] not in conflict_families:
        return False
    strong_conflict = float(row["noncompact_conflict_norm"]) >= 0.5
    clean_wrap_label = row["diagnostic_decision_label"] == "phase_wrap_corrected_by_circular_metric"
    return bool(strong_conflict and clean_wrap_label)


def build_explicit_pair_rows(config: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    fingerprints = {row["fingerprint_id"]: row for row in config["stress_fingerprints"]}
    rows = []
    for pair in config["stress_pairs"]:
        rows.append(
            compute_pair_row(
                pair,
                fingerprints[pair["left_fingerprint_id"]],
                fingerprints[pair["right_fingerprint_id"]],
                config,
                config["stress_thresholds"],
                baseline_replay=False,
            )
        )
    return [dict(row) for row in config["stress_fingerprints"]], rows


def build_baseline_replay_rows(
    config: dict[str, Any],
    baseline_config: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    original_fingerprints = {row["fingerprint_id"]: row for row in baseline_config["toy_fingerprints"]}
    replay_fingerprints = []
    replay_by_id = {}
    for original in baseline_config["toy_fingerprints"]:
        replay = {
            "fingerprint_id": f"baseline_reference_replay__{original['fingerprint_id']}",
            "case_family": "baseline_reference_replay",
            "case_role": original.get("case_role", ""),
            "delta_k": original["delta_k"],
            "delta_phase": original["delta_phase"],
            "slope_diff": original["slope_diff"],
            "intercept_diff": original["intercept_diff"],
            "amplitude_diff": original["amplitude_diff"],
            "expected_relation": original["expected_relation"],
            "adversarial_intent": "baseline replay should preserve original WIFM01 behavior",
            "notes": f"baseline replay of {original['case_family']}",
            "_original_fingerprint_id": original["fingerprint_id"],
        }
        replay_fingerprints.append(replay)
        replay_by_id[original["fingerprint_id"]] = replay

    replay_pairs = []
    for pair in baseline_config["toy_pairs"]:
        expected = BASELINE_LABEL_BY_FAMILY[str(pair["case_family"])]
        replay_pair = {
            "pair_id": f"baseline_reference_replay__{pair['pair_id']}",
            "left_fingerprint_id": replay_by_id[pair["left_fingerprint_id"]]["fingerprint_id"],
            "right_fingerprint_id": replay_by_id[pair["right_fingerprint_id"]]["fingerprint_id"],
            "case_family": "baseline_reference_replay",
            "expected_relation": expected,
            "_original_case_family": pair["case_family"],
        }
        left = original_fingerprints[pair["left_fingerprint_id"]]
        right = original_fingerprints[pair["right_fingerprint_id"]]
        replay_pairs.append(
            compute_pair_row(
                replay_pair,
                left,
                right,
                config,
                config["stress_thresholds"],
                baseline_replay=True,
            )
        )
    return replay_fingerprints, replay_pairs


def build_case_family_summary(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        grouped[str(row["case_family"])].append(row)
    rows = []
    for case_family in sorted(grouped):
        case_rows = grouped[case_family]
        expected_labels = sorted({str(row["expected_relation"]) for row in case_rows})
        observed = Counter(str(row["diagnostic_decision_label"]) for row in case_rows)
        all_expected = all(bool(row["expected_adversarial_behavior_met"]) for row in case_rows)
        warning_count = sum(1 for row in case_rows if row["diagnostic_decision_label"] == "diagnostic_warning_review_needed")
        overcleaning_count = sum(1 for row in case_rows if row["overcleaning_risk_flag"])
        interpretation = (
            "expected diagnostic stress behavior met"
            if all_expected
            else "one or more stress pairs require implementation review"
        )
        rows.append(
            {
                "case_family": case_family,
                "pair_count": len(case_rows),
                "expected_label": expected_labels[0] if len(expected_labels) == 1 else json.dumps(expected_labels),
                "observed_labels": dict(sorted(observed.items())),
                "expected_adversarial_behavior_met": all_expected,
                "overcleaning_risk_count": overcleaning_count,
                "diagnostic_warning_count": warning_count,
                "stress_interpretation": interpretation,
                "claim_boundary": "case-family stress summary is diagnostic only",
            }
        )
    return rows


def build_label_summary(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        grouped[str(row["diagnostic_decision_label"])].append(row)
    rows = []
    for label in sorted(grouped):
        label_rows = grouped[label]
        families = sorted({str(row["case_family"]) for row in label_rows})
        expected = all(row["diagnostic_decision_label"] == row["expected_relation"] for row in label_rows)
        rows.append(
            {
                "diagnostic_decision_label": label,
                "count": len(label_rows),
                "case_families": families,
                "expected_or_unexpected": "expected" if expected else "unexpected",
                "interpretation_boundary": "label count is diagnostic only",
            }
        )
    return rows


def build_overcleaning_summary(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    overcleaning_rows = [row for row in pair_rows if row["case_family"] == "overcleaning_probe"]
    phase_wrap_clean_without_warning = [
        row
        for row in pair_rows
        if row["case_family"] in {"overcleaning_probe", "phase_wrap_agrees_shape_conflicts"}
        and row["diagnostic_decision_label"] == "phase_wrap_corrected_by_circular_metric"
        and float(row["noncompact_conflict_norm"]) >= 0.5
    ]
    unexpected_clean = [
        row
        for row in pair_rows
        if row["case_family"] not in {"near_identity_control", "baseline_reference_replay"}
        and row["diagnostic_decision_label"] in CLEAN_BASELINE_LABELS
    ]
    boundary = "over-cleaning risk summary is diagnostic only"
    return [
        {"metric": "total_pair_count", "value": len(pair_rows), "interpretation_boundary": boundary},
        {"metric": "overcleaning_probe_pair_count", "value": len(overcleaning_rows), "interpretation_boundary": boundary},
        {
            "metric": "overcleaning_risk_detected_count",
            "value": sum(1 for row in overcleaning_rows if row["diagnostic_decision_label"] == "overcleaning_risk_detected"),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "phase_wrap_label_without_conflict_warning_count",
            "value": len(phase_wrap_clean_without_warning),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "expected_overcleaning_warning_count",
            "value": len(overcleaning_rows),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "unexpected_overcleaning_clean_label_count",
            "value": len(unexpected_clean),
            "interpretation_boundary": boundary,
        },
    ]


def build_adversarial_conflict_summary(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    adversarial_rows = [
        row for row in pair_rows if row["case_family"] not in {"near_identity_control", "baseline_reference_replay"}
    ]
    boundary = "adversarial channel-conflict summary is diagnostic only"
    return [
        {"metric": "adversarial_pair_count", "value": len(adversarial_rows), "interpretation_boundary": boundary},
        {
            "metric": "phase_agreement_noncompact_conflict_count",
            "value": sum(1 for row in pair_rows if row["diagnostic_decision_label"] == "adversarial_phase_agreement_noncompact_conflict"),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "wrap_with_shape_conflict_count",
            "value": sum(1 for row in pair_rows if row["diagnostic_decision_label"] == "adversarial_wrap_with_shape_conflict"),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "cumulative_small_difference_warning_count",
            "value": sum(1 for row in pair_rows if row["diagnostic_decision_label"] == "cumulative_small_difference_warning"),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "amplitude_shape_conflict_warning_count",
            "value": sum(1 for row in pair_rows if row["diagnostic_decision_label"] == "amplitude_shape_conflict_warning"),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "ambiguous_multi_channel_review_count",
            "value": sum(1 for row in pair_rows if row["diagnostic_decision_label"] == "ambiguous_multi_channel_review"),
            "interpretation_boundary": boundary,
        },
    ]


def build_baseline_replay_summary(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    replay_rows = [row for row in pair_rows if row["case_family"] == "baseline_reference_replay"]
    boundary = "baseline replay summary is diagnostic only"
    return [
        {"metric": "baseline_replay_pair_count", "value": len(replay_rows), "interpretation_boundary": boundary},
        {
            "metric": "baseline_replay_expected_behavior_met_count",
            "value": sum(1 for row in replay_rows if row["expected_adversarial_behavior_met"]),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "baseline_replay_warning_count",
            "value": sum(1 for row in replay_rows if row["diagnostic_decision_label"] == "diagnostic_warning_review_needed"),
            "interpretation_boundary": boundary,
        },
        {
            "metric": "baseline_replay_failure_count",
            "value": sum(1 for row in replay_rows if not row["expected_adversarial_behavior_met"]),
            "interpretation_boundary": boundary,
        },
    ]


def build_summary(config: dict[str, Any], pair_rows: list[dict[str, Any]], output_files: dict[str, str]) -> dict[str, Any]:
    claims = dict(config["claim_boundary"])
    label_counts = Counter(str(row["diagnostic_decision_label"]) for row in pair_rows)
    case_family_label_map = {
        family: dict(Counter(str(row["diagnostic_decision_label"]) for row in rows))
        for family, rows in group_by(pair_rows, "case_family").items()
    }
    baseline_rows = [row for row in pair_rows if row["case_family"] == "baseline_reference_replay"]
    adversarial_rows = [
        row for row in pair_rows if row["case_family"] not in {"near_identity_control", "baseline_reference_replay"}
    ]
    unexpected_clean = [
        row
        for row in adversarial_rows
        if row["diagnostic_decision_label"] in CLEAN_BASELINE_LABELS
    ]
    expected_met_count = sum(1 for row in pair_rows if row["expected_adversarial_behavior_met"])
    expected_count = len(pair_rows)
    strong_conflict_labels = {
        "adversarial_phase_agreement_noncompact_conflict",
        "adversarial_wrap_with_shape_conflict",
        "amplitude_shape_conflict_warning",
        "overcleaning_risk_detected",
    }
    return {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "stress_version": config["stress_version"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stress_fingerprint_count": config["_stress_fingerprint_output_count"],
        "stress_pair_count": len(pair_rows),
        "case_family_count": len({row["case_family"] for row in pair_rows}),
        "baseline_replay_pair_count": len(baseline_rows),
        "adversarial_pair_count": len(adversarial_rows),
        "expected_adversarial_behaviors_met": expected_met_count == expected_count,
        "expected_adversarial_behavior_count": expected_count,
        "expected_adversarial_behavior_met_count": expected_met_count,
        "overcleaning_risk_case_count": sum(1 for row in pair_rows if row["case_family"] == "overcleaning_probe"),
        "overcleaning_risk_detected_count": label_counts.get("overcleaning_risk_detected", 0),
        "unexpected_overcleaning_clean_label_count": len(unexpected_clean),
        "diagnostic_warning_review_count": sum(
            1
            for row in pair_rows
            if row["diagnostic_decision_label"] == "diagnostic_warning_review_needed"
            and row["expected_relation"] != "diagnostic_warning_review_needed"
        ),
        "diagnostic_failure_review_count": sum(1 for row in pair_rows if not row["expected_adversarial_behavior_met"]),
        "diagnostic_decision_label_counts": dict(sorted(label_counts.items())),
        "case_family_label_map": case_family_label_map,
        "strong_conflict_case_count": sum(1 for row in pair_rows if row["diagnostic_decision_label"] in strong_conflict_labels),
        "cumulative_warning_case_count": label_counts.get("cumulative_small_difference_warning", 0),
        "ambiguity_review_case_count": label_counts.get("ambiguous_multi_channel_review", 0),
        "baseline_replay_expected_behavior_met": all(row["expected_adversarial_behavior_met"] for row in baseline_rows),
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


def group_by(rows: list[dict[str, Any]], field: str) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[field])].append(row)
    return dict(grouped)


def write_readout(path: Path, summary: dict[str, Any], output_files: dict[str, str]) -> None:
    lines = [
        "# QSB-ST COMP01-WIFM01C Adversarial / Ambiguity Stress Cases — Readout",
        "",
        "## 1. Purpose",
        "WIFM01C is diagnostic stress testing only.",
        "Expected adversarial warnings are allowed, and warning labels are not automatically failures.",
        "",
        "## 2. Baseline context",
        f"- baseline_replay_pair_count: {summary['baseline_replay_pair_count']}",
        f"- baseline_replay_expected_behavior_met: {format_cell(summary['baseline_replay_expected_behavior_met'])}",
        "",
        "## 3. Stress case families",
        f"- stress_pair_count: {summary['stress_pair_count']}",
        f"- case_family_count: {summary['case_family_count']}",
        "",
        "## 4. Metric and warning logic",
        "The runner uses WIFM-style circular phase distance, weighted diagnostic distance, noncompact conflict norm, and cumulative difference norm.",
        "Expected adversarial labels are diagnostic outcomes, not implementation failures.",
        "",
        "## 5. Adversarial conflict results",
        f"- adversarial_pair_count: {summary['adversarial_pair_count']}",
        f"- strong_conflict_case_count: {summary['strong_conflict_case_count']}",
        f"- cumulative_warning_case_count: {summary['cumulative_warning_case_count']}",
        f"- ambiguity_review_case_count: {summary['ambiguity_review_case_count']}",
        "",
        "## 6. Overcleaning risk results",
        f"- overcleaning_risk_case_count: {summary['overcleaning_risk_case_count']}",
        f"- overcleaning_risk_detected_count: {summary['overcleaning_risk_detected_count']}",
        f"- unexpected_overcleaning_clean_label_count: {summary['unexpected_overcleaning_clean_label_count']}",
        "",
        "## 7. Baseline replay results",
        f"- baseline_replay_expected_behavior_met: {format_cell(summary['baseline_replay_expected_behavior_met'])}",
        "",
        "## 8. Befund",
        f"- expected_adversarial_behaviors_met: {format_cell(summary['expected_adversarial_behaviors_met'])}",
        f"- diagnostic_warning_review_count: {summary['diagnostic_warning_review_count']}",
        f"- diagnostic_failure_review_count: {summary['diagnostic_failure_review_count']}",
        f"- diagnostic_decision_label_counts: {json.dumps(summary['diagnostic_decision_label_counts'], sort_keys=True)}",
        "",
        "## 9. Interpretation",
        "The output is a synthetic diagnostic stress artifact.",
        "No physical metric is established. No physical compact dimensions are established.",
        "No Hilbert-space reconstruction is made. No Bridge confirmation is made. No diagnostic specificity is made.",
        "",
        "## 10. Hypothese",
        "A WIFM diagnostic metric may be useful if it preserves adversarial warnings while retaining near-identity sanity behavior in the toy setting.",
        "",
        "## 11. Offene Lücke",
        "- no real data",
        "- no broad control set",
        "- no physical model validation",
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
    validate_config(config, output_dir, root)

    baseline_source = config["baseline_source"]
    wifm01_config_path = resolve_path(root, baseline_source.get("wifm01_config"))
    wifm01_summary_path = resolve_path(root, baseline_source.get("wifm01_summary"))
    wifm01_pair_metrics_path = resolve_path(root, baseline_source.get("wifm01_pair_metrics"))
    wifm01b_summary_path = resolve_path(root, baseline_source.get("wifm01b_summary"))

    baseline_config = read_yaml(wifm01_config_path)
    wifm01_summary = read_json(wifm01_summary_path)
    wifm01_pair_metrics = read_csv_rows(wifm01_pair_metrics_path)
    wifm01b_summary = read_json(wifm01b_summary_path)
    validate_baseline_config(baseline_config)
    validate_baseline_summary(wifm01_summary)
    validate_baseline_pair_metrics(wifm01_pair_metrics)
    validate_wifm01b_summary(wifm01b_summary)

    config["_baseline_thresholds"] = baseline_config["thresholds"]
    explicit_fingerprints, explicit_pair_rows = build_explicit_pair_rows(config)
    replay_fingerprints, replay_pair_rows = build_baseline_replay_rows(config, baseline_config)
    fingerprint_rows = explicit_fingerprints + replay_fingerprints
    pair_rows = explicit_pair_rows + replay_pair_rows
    config["_stress_fingerprint_output_count"] = len(fingerprint_rows)

    families = {str(row["case_family"]) for row in pair_rows}
    missing_families = REQUIRED_STRESS_FAMILIES - families
    if missing_families:
        raise SystemExit(f"Output pair rows missing stress families: {sorted(missing_families)}")

    case_family_rows = build_case_family_summary(pair_rows)
    label_rows = build_label_summary(pair_rows)
    overcleaning_rows = build_overcleaning_summary(pair_rows)
    adversarial_rows = build_adversarial_conflict_summary(pair_rows)
    baseline_replay_rows = build_baseline_replay_summary(pair_rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = output_paths(config, output_dir)
    created_output_files = {key: str(path) for key, path in paths.items()}
    summary = build_summary(config, pair_rows, created_output_files)

    write_json(paths["summary_json"], summary)
    write_readout(paths["readout_md"], summary, created_output_files)
    write_csv(paths["stress_fingerprint_input_table_csv"], FINGERPRINT_FIELDS, fingerprint_rows)
    write_csv(paths["stress_pair_metric_comparison_csv"], PAIR_FIELDS, pair_rows)
    write_csv(paths["case_family_stress_summary_csv"], CASE_FAMILY_FIELDS, case_family_rows)
    write_csv(paths["label_stress_summary_csv"], LABEL_FIELDS, label_rows)
    write_csv(paths["overcleaning_risk_summary_csv"], SUMMARY_FIELDS, overcleaning_rows)
    write_csv(paths["adversarial_channel_conflict_summary_csv"], SUMMARY_FIELDS, adversarial_rows)
    write_csv(paths["baseline_replay_summary_csv"], SUMMARY_FIELDS, baseline_replay_rows)
    write_json(
        paths["resolved_config_json"],
        {
            "original_wifm01c_config": config,
            "baseline_wifm01_config_path": str(wifm01_config_path),
            "baseline_wifm01_summary_path": str(wifm01_summary_path),
            "baseline_wifm01b_summary_path": str(wifm01b_summary_path),
            "resolved_output_directory": str(output_dir),
            "stress_family_definitions": sorted(REQUIRED_STRESS_FAMILIES),
            "claim_boundary": config["claim_boundary"],
            "created_output_files": created_output_files,
        },
    )

    print("WIFM01C adversarial stress runner complete")
    print(f"output_dir: {output_dir}")
    print(f"stress_pair_count: {summary['stress_pair_count']}")
    print(f"expected_adversarial_behaviors_met: {format_cell(summary['expected_adversarial_behaviors_met'])}")
    print(f"diagnostic_failure_review_count: {summary['diagnostic_failure_review_count']}")


if __name__ == "__main__":
    main()
