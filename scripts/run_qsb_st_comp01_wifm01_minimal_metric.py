#!/usr/bin/env python3
"""QSB-ST COMP01-WIFM01 minimal diagnostic fingerprint metric runner."""

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
        "PyYAML is required to read the WIFM01 config. Activate the project environment or install PyYAML."
    ) from exc


REQUIRED_TOP_LEVEL_KEYS = [
    "block_id",
    "route_name",
    "metric_version",
    "run_id",
    "output_dir",
    "input_mode",
    "phase_period",
    "coordinate_scales",
    "weights",
    "thresholds",
    "toy_fingerprints",
    "toy_pairs",
    "claim_boundary",
    "output_files",
]

REQUIRED_CASE_FAMILIES = {
    "same_relational_identity",
    "phase_wrap_equivalent",
    "same_looking_not_same_delta_k",
    "same_looking_not_same_slope_intercept",
    "mixed_ambiguity_case",
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
    "naive_phase_component",
    "circular_phase_component",
    "naive_metric_distance",
    "circular_metric_distance",
    "distance_delta_naive_minus_circular",
    "diagnostic_decision_label",
    "diagnostic_reason",
    "claim_boundary",
]

CASE_FAMILY_FIELDS = [
    "case_family",
    "pair_count",
    "diagnostic_decision_label_counts",
    "expected_behavior_met",
    "diagnostic_reason_summary",
    "claim_boundary",
]

COMPONENT_FIELDS = [
    "component_name",
    "component_type",
    "compact",
    "scale",
    "weight",
    "pair_count",
    "min_abs_component",
    "max_abs_component",
    "mean_abs_component",
    "interpretation_boundary",
]

PHASE_SUMMARY_FIELDS = [
    "metric",
    "value",
    "interpretation_boundary",
]

ALLOWED_OUTPUT_NAMES = {
    "summary_json",
    "readout_md",
    "fingerprint_input_table_csv",
    "pair_metric_comparison_csv",
    "case_family_summary_csv",
    "metric_component_summary_csv",
    "naive_vs_circular_phase_summary_csv",
    "resolved_config_json",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run WIFM01 minimal diagnostic metric over inline synthetic relational fingerprints."
    )
    parser.add_argument("--config", required=True, help="Path to WIFM01 YAML config.")
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
        raise SystemExit(f"Missing config file: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Config did not parse to a mapping: {path}")
    return data


def validate_config(config: dict[str, Any], output_dir: Path, root: Path) -> None:
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in config]
    if missing:
        raise SystemExit(f"Missing required config keys: {missing}")
    if config.get("input_mode") != "inline_synthetic_cases":
        raise SystemExit("WIFM01 first runner only supports input_mode: inline_synthetic_cases")

    expected_output_dir = root / "runs/QSB-ST-COMP01-WIFM01/minimal_metric_open"
    if output_dir.resolve() != expected_output_dir.resolve():
        raise SystemExit(f"Output directory must be {expected_output_dir}")

    scales = config.get("coordinate_scales") or {}
    weights = config.get("weights") or {}
    for key in ["delta_k", "slope_diff", "intercept_diff", "amplitude_diff"]:
        if safe_float(scales.get(key)) is None or safe_float(scales.get(key)) == 0:
            raise SystemExit(f"coordinate_scales.{key} must be explicit and non-zero")
    for key in ["delta_k", "delta_phase", "slope_diff", "intercept_diff", "amplitude_diff"]:
        if safe_float(weights.get(key)) is None:
            raise SystemExit(f"weights.{key} must be explicit")

    output_files = config.get("output_files") or {}
    if set(output_files) != ALLOWED_OUTPUT_NAMES:
        raise SystemExit("output_files must contain exactly the allowed WIFM01 output keys")


def validate_fingerprints(rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise SystemExit("toy_fingerprints must not be empty")
    for index, row in enumerate(rows):
        missing = [field for field in FINGERPRINT_FIELDS if field not in row]
        if missing:
            raise SystemExit(f"toy_fingerprints[{index}] missing fields: {missing}")
        for field in ["delta_k", "delta_phase", "slope_diff", "intercept_diff", "amplitude_diff"]:
            if safe_float(row.get(field)) is None:
                raise SystemExit(f"toy_fingerprints[{index}].{field} must be numeric")

    families = {str(row.get("case_family")) for row in rows}
    missing_families = REQUIRED_CASE_FAMILIES - families
    if missing_families:
        raise SystemExit(f"Missing toy fingerprint families: {sorted(missing_families)}")

    counts = Counter(str(row.get("case_family")) for row in rows)
    too_few = {family: count for family, count in counts.items() if family in REQUIRED_CASE_FAMILIES and count < 2}
    if too_few:
        raise SystemExit(f"Each required family needs at least two fingerprints: {too_few}")


def validate_pairs(rows: list[dict[str, Any]], fingerprints: dict[str, dict[str, Any]]) -> None:
    if not rows:
        raise SystemExit("toy_pairs must not be empty")
    for index, row in enumerate(rows):
        missing = [field for field in ["pair_id", "left_fingerprint_id", "right_fingerprint_id", "case_family", "expected_relation"] if field not in row]
        if missing:
            raise SystemExit(f"toy_pairs[{index}] missing fields: {missing}")
        for field in ["left_fingerprint_id", "right_fingerprint_id"]:
            if row[field] not in fingerprints:
                raise SystemExit(f"toy_pairs[{index}] references unknown {field}: {row[field]}")

    families = {str(row.get("case_family")) for row in rows}
    missing_families = REQUIRED_CASE_FAMILIES - families
    if missing_families:
        raise SystemExit(f"Missing toy pair families: {sorted(missing_families)}")


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


def normalized_delta(left: Any, right: Any, scale: Any) -> float:
    scale_value = safe_float(scale)
    if scale_value is None or scale_value == 0:
        raise SystemExit("Normalization scale must be numeric and non-zero")
    left_value = safe_float(left)
    right_value = safe_float(right)
    if left_value is None or right_value is None:
        raise SystemExit("Fingerprint coordinate must be numeric")
    return (left_value - right_value) / scale_value


def phase_delta(left: Any, right: Any, phase_period: float) -> tuple[float, float]:
    left_value = safe_float(left)
    right_value = safe_float(right)
    if left_value is None or right_value is None:
        raise SystemExit("delta_phase must be numeric")
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
        safe_float(weights["delta_k"]) * delta_k_component**2
        + safe_float(weights["delta_phase"]) * phase_component**2
        + safe_float(weights["slope_diff"]) * slope_diff_component**2
        + safe_float(weights["intercept_diff"]) * intercept_diff_component**2
        + safe_float(weights["amplitude_diff"]) * amplitude_diff_component**2
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
    near_zero = safe_float(thresholds.get("near_zero_distance")) or 0.0
    noncompact_min = safe_float(thresholds.get("noncompact_separation_min")) or 0.0
    ambiguity_min = safe_float(thresholds.get("ambiguity_min_distance")) or 0.0
    ambiguity_max = safe_float(thresholds.get("ambiguity_max_distance")) or 0.0

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


def build_pair_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    fingerprints = {row["fingerprint_id"]: row for row in config["toy_fingerprints"]}
    scales = config["coordinate_scales"]
    weights = config["weights"]
    thresholds = config["thresholds"]
    phase_period = float(config["phase_period"])
    claim_boundary = "diagnostic fingerprint metric only; no physical metric or identity claim"

    rows: list[dict[str, Any]] = []
    for pair in config["toy_pairs"]:
        left = fingerprints[pair["left_fingerprint_id"]]
        right = fingerprints[pair["right_fingerprint_id"]]
        delta_k_component = normalized_delta(left["delta_k"], right["delta_k"], scales["delta_k"])
        slope_diff_component = normalized_delta(left["slope_diff"], right["slope_diff"], scales["slope_diff"])
        intercept_diff_component = normalized_delta(left["intercept_diff"], right["intercept_diff"], scales["intercept_diff"])
        amplitude_diff_component = normalized_delta(left["amplitude_diff"], right["amplitude_diff"], scales["amplitude_diff"])
        naive_phase_delta, circular_phase_delta = phase_delta(left["delta_phase"], right["delta_phase"], phase_period)
        naive_phase_component = naive_phase_delta
        circular_phase_component = circular_phase_delta
        naive_metric_distance = weighted_distance(
            delta_k_component,
            naive_phase_component,
            slope_diff_component,
            intercept_diff_component,
            amplitude_diff_component,
            weights,
        )
        circular_metric_distance = weighted_distance(
            delta_k_component,
            circular_phase_component,
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
                "naive_phase_component": naive_phase_component,
                "circular_phase_component": circular_phase_component,
                "naive_metric_distance": naive_metric_distance,
                "circular_metric_distance": circular_metric_distance,
                "distance_delta_naive_minus_circular": naive_metric_distance - circular_metric_distance,
                "diagnostic_decision_label": label,
                "diagnostic_reason": reason,
                "claim_boundary": claim_boundary,
            }
        )
    return rows


def build_case_family_rows(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pair_rows:
        grouped[str(row["case_family"])].append(row)

    rows = []
    for case_family in sorted(grouped):
        case_rows = grouped[case_family]
        label_counts = dict(Counter(str(row["diagnostic_decision_label"]) for row in case_rows))
        expected_behavior_met = all(row["diagnostic_decision_label"] == row["expected_relation"] for row in case_rows)
        rows.append(
            {
                "case_family": case_family,
                "pair_count": len(case_rows),
                "diagnostic_decision_label_counts": label_counts,
                "expected_behavior_met": expected_behavior_met,
                "diagnostic_reason_summary": "; ".join(str(row["diagnostic_reason"]) for row in case_rows),
                "claim_boundary": "case-family summary is diagnostic only",
            }
        )
    return rows


def stats(values: list[float]) -> tuple[float | None, float | None, float | None]:
    if not values:
        return None, None, None
    return min(values), max(values), sum(values) / len(values)


def build_component_rows(pair_rows: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    components = [
        ("delta_k", "noncompact", False, config["coordinate_scales"]["delta_k"], config["weights"]["delta_k"], "delta_k_component"),
        ("delta_phase_naive", "compact_baseline", True, 1.0, config["weights"]["delta_phase"], "naive_phase_component"),
        ("delta_phase_circular", "compact_circular", True, 1.0, config["weights"]["delta_phase"], "circular_phase_component"),
        ("slope_diff", "noncompact", False, config["coordinate_scales"]["slope_diff"], config["weights"]["slope_diff"], "slope_diff_component"),
        ("intercept_diff", "noncompact", False, config["coordinate_scales"]["intercept_diff"], config["weights"]["intercept_diff"], "intercept_diff_component"),
        ("amplitude_diff", "noncompact", False, config["coordinate_scales"]["amplitude_diff"], config["weights"]["amplitude_diff"], "amplitude_diff_component"),
    ]
    rows = []
    for name, component_type, compact, scale, weight, source_field in components:
        values = [abs(float(row[source_field])) for row in pair_rows]
        min_value, max_value, mean_value = stats(values)
        rows.append(
            {
                "component_name": name,
                "component_type": component_type,
                "compact": compact,
                "scale": scale,
                "weight": weight,
                "pair_count": len(pair_rows),
                "min_abs_component": min_value,
                "max_abs_component": max_value,
                "mean_abs_component": mean_value,
                "interpretation_boundary": "diagnostic metric component only",
            }
        )
    return rows


def build_phase_summary(pair_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    phase_rows = [row for row in pair_rows if row["case_family"] == "phase_wrap_equivalent"]
    phase_wrap_corrected_count = sum(
        1
        for row in phase_rows
        if float(row["circular_phase_delta"]) < float(row["naive_phase_delta"])
        and float(row["circular_metric_distance"]) < float(row["naive_metric_distance"])
    )
    naive_phase_values = [float(row["naive_phase_delta"]) for row in pair_rows]
    circular_phase_values = [float(row["circular_phase_delta"]) for row in pair_rows]
    distance_delta_values = [float(row["distance_delta_naive_minus_circular"]) for row in pair_rows]
    _, max_naive_phase, mean_naive_phase = stats(naive_phase_values)
    _, max_circular_phase, mean_circular_phase = stats(circular_phase_values)
    _, max_distance_delta, mean_distance_delta = stats(distance_delta_values)
    boundary = "naive-vs-circular phase comparison is diagnostic only"
    return [
        {"metric": "phase_wrap_case_count", "value": len(phase_rows), "interpretation_boundary": boundary},
        {"metric": "phase_wrap_corrected_count", "value": phase_wrap_corrected_count, "interpretation_boundary": boundary},
        {"metric": "max_naive_phase_delta", "value": max_naive_phase, "interpretation_boundary": boundary},
        {"metric": "max_circular_phase_delta", "value": max_circular_phase, "interpretation_boundary": boundary},
        {"metric": "mean_naive_phase_delta", "value": mean_naive_phase, "interpretation_boundary": boundary},
        {"metric": "mean_circular_phase_delta", "value": mean_circular_phase, "interpretation_boundary": boundary},
        {"metric": "max_distance_delta_naive_minus_circular", "value": max_distance_delta, "interpretation_boundary": boundary},
        {"metric": "mean_distance_delta_naive_minus_circular", "value": mean_distance_delta, "interpretation_boundary": boundary},
    ]


def label_counts(pair_rows: list[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(str(row["diagnostic_decision_label"]) for row in pair_rows))


def build_summary(config: dict[str, Any], pair_rows: list[dict[str, Any]], output_files: dict[str, str]) -> dict[str, Any]:
    phase_rows = [row for row in pair_rows if row["case_family"] == "phase_wrap_equivalent"]
    phase_wrap_corrected_count = sum(
        1
        for row in phase_rows
        if float(row["circular_phase_delta"]) < float(row["naive_phase_delta"])
        and float(row["circular_metric_distance"]) < float(row["naive_metric_distance"])
    )
    noncompact_rows = [row for row in pair_rows if row["case_family"] in {"same_looking_not_same_delta_k", "same_looking_not_same_slope_intercept"}]
    noncompact_preserved = sum(
        1
        for row in noncompact_rows
        if row["diagnostic_decision_label"] in {"noncompact_difference_preserved", "local_shape_difference_preserved"}
    )
    ambiguity_rows = [row for row in pair_rows if row["case_family"] == "mixed_ambiguity_case"]
    ambiguity_preserved = sum(1 for row in ambiguity_rows if row["diagnostic_decision_label"] == "mixed_ambiguity_preserved")
    distance_deltas = [float(row["distance_delta_naive_minus_circular"]) for row in pair_rows]
    min_delta, max_delta, mean_delta = stats(distance_deltas)
    claims = dict(config["claim_boundary"])
    return {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "metric_version": config["metric_version"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "fingerprint_count": len(config["toy_fingerprints"]),
        "comparison_pair_count": len(pair_rows),
        "case_family_count": len({row["case_family"] for row in pair_rows}),
        "coordinate_names": ["delta_k", "delta_phase", "slope_diff", "intercept_diff", "amplitude_diff"],
        "compact_coordinates": ["delta_phase"],
        "noncompact_coordinates": ["delta_k", "slope_diff", "intercept_diff", "amplitude_diff"],
        "coordinate_scales": config["coordinate_scales"],
        "weights": config["weights"],
        "phase_period": config["phase_period"],
        "phase_wrap_case_count": len(phase_rows),
        "phase_wrap_corrected_count": phase_wrap_corrected_count,
        "noncompact_separation_case_count": len(noncompact_rows),
        "noncompact_separation_preserved_count": noncompact_preserved,
        "mixed_ambiguity_case_count": len(ambiguity_rows),
        "mixed_ambiguity_preserved_count": ambiguity_preserved,
        "naive_vs_circular_distance_delta_summary": {
            "min": min_delta,
            "max": max_delta,
            "mean": mean_delta,
        },
        "diagnostic_decision_label_counts": label_counts(pair_rows),
        "all_expected_behaviors_met": all(row["diagnostic_decision_label"] == row["expected_relation"] for row in pair_rows),
        "warning_review_count": sum(1 for row in pair_rows if row["diagnostic_decision_label"] == "diagnostic_warning_review_needed"),
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
        "runner_scope": "synthetic diagnostic minimal wave identity fingerprint metric",
        "claim_boundary": claims,
        "output_files": output_files,
    }


def write_readout(path: Path, summary: dict[str, Any], output_files: dict[str, str]) -> None:
    lines = [
        "# QSB-ST COMP01-WIFM01 Minimal Wave Identity Fingerprint Metric — Readout",
        "",
        "## 1. Purpose",
        "WIFM01 is diagnostic only. It compares naive and circular phase handling for tiny relational fingerprint toy cases.",
        "",
        "## 2. Inputs",
        f"- fingerprint_count: {summary['fingerprint_count']}",
        f"- comparison_pair_count: {summary['comparison_pair_count']}",
        f"- case_family_count: {summary['case_family_count']}",
        "",
        "## 3. Metric definition",
        "The metric compares relational wave-pair fingerprints in Fingerprint-Raum.",
        "Fingerprint-Raum is measurement/projection space. Identitäts-Raum remains open.",
        "Phase is compact and uses circular distance for the circular metric variant.",
        "",
        "## 4. Toy cases",
        "- same_relational_identity",
        "- phase_wrap_equivalent",
        "- same_looking_not_same_delta_k",
        "- same_looking_not_same_slope_intercept",
        "- mixed_ambiguity_case",
        "",
        "## 5. Naive vs circular phase comparison",
        f"- phase_wrap_case_count: {summary['phase_wrap_case_count']}",
        f"- phase_wrap_corrected_count: {summary['phase_wrap_corrected_count']}",
        f"- distance_delta_summary: {json.dumps(summary['naive_vs_circular_distance_delta_summary'], sort_keys=True)}",
        "",
        "## 6. Befund",
        f"- all_expected_behaviors_met: {format_cell(summary['all_expected_behaviors_met'])}",
        f"- warning_review_count: {summary['warning_review_count']}",
        f"- diagnostic_decision_label_counts: {json.dumps(summary['diagnostic_decision_label_counts'], sort_keys=True)}",
        "",
        "## 7. Interpretation",
        "The output is a diagnostic toy metric check. No physical metric is established.",
        "No physical compact dimensions are established. No Hilbert-space reconstruction is made. No Bridge confirmation is made.",
        "",
        "## 8. Hypothese",
        "A circular phase metric can handle wrap-equivalent diagnostic fingerprints more coherently than a naive phase delta in this toy setup.",
        "",
        "## 9. Offene Lücke",
        "- no real data",
        "- no diagnostic specificity",
        "- no physical phase reconstruction",
        "- no physical spacetime geometry",
        "- no Lorentzian metric",
        "- identity space remains open",
        "",
        "## 10. Claim Boundary",
        "- specificity_established: false",
        "- phase_is_physical: false",
        "- phase_is_synthetic_diagnostic: true",
        "- physical_metric_established: false",
        "- physical_compact_dimensions_established: false",
        "- hilbert_space_reconstruction: false",
        "- bridge_confirmation: false",
        "- Mastermind, Knuth, and manifold remain parked",
        "",
        "## 11. Files created",
    ]
    lines.extend(f"- {value}" for value in output_files.values())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = repo_root()
    config_path = resolve_path(root, args.config)
    config = read_yaml(config_path)
    output_dir = resolve_path(root, config.get("output_dir"))
    validate_config(config, output_dir, root)
    validate_fingerprints(config["toy_fingerprints"])
    fingerprints = {row["fingerprint_id"]: row for row in config["toy_fingerprints"]}
    validate_pairs(config["toy_pairs"], fingerprints)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_config = config["output_files"]
    output_paths = {key: output_dir / name for key, name in output_config.items()}

    fingerprint_rows = [dict(row) for row in config["toy_fingerprints"]]
    pair_rows = build_pair_rows(config)
    case_rows = build_case_family_rows(pair_rows)
    component_rows = build_component_rows(pair_rows, config)
    phase_summary_rows = build_phase_summary(pair_rows)
    output_files = {key: str(path) for key, path in output_paths.items()}
    summary = build_summary(config, pair_rows, output_files)

    write_csv(output_paths["fingerprint_input_table_csv"], FINGERPRINT_FIELDS, fingerprint_rows)
    write_csv(output_paths["pair_metric_comparison_csv"], PAIR_FIELDS, pair_rows)
    write_csv(output_paths["case_family_summary_csv"], CASE_FAMILY_FIELDS, case_rows)
    write_csv(output_paths["metric_component_summary_csv"], COMPONENT_FIELDS, component_rows)
    write_csv(output_paths["naive_vs_circular_phase_summary_csv"], PHASE_SUMMARY_FIELDS, phase_summary_rows)
    write_json(output_paths["summary_json"], summary)
    write_readout(output_paths["readout_md"], summary, output_files)
    resolved_config = {
        "original_config": config,
        "resolved_input_mode": config["input_mode"],
        "output_directory": str(output_dir),
        "coordinate_scales": config["coordinate_scales"],
        "weights": config["weights"],
        "claim_boundary": config["claim_boundary"],
        "created_output_files": output_files,
    }
    write_json(output_paths["resolved_config_json"], resolved_config)

    print("WIFM01 minimal metric runner complete")
    print(f"output_dir: {output_dir}")
    print(f"fingerprint_count: {summary['fingerprint_count']}")
    print(f"comparison_pair_count: {summary['comparison_pair_count']}")
    print(f"all_expected_behaviors_met: {format_cell(summary['all_expected_behaviors_met'])}")


if __name__ == "__main__":
    main()
