#!/usr/bin/env python3
"""QSB-ST-COMP01-D1g synthetic warning-driver decomposition.

This runner reads the existing D1f robustness sweep outputs. It does not
rerun D1f and does not introduce a new identity score.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required for this runner. Install PyYAML or run in the "
        "project environment where yaml is available."
    ) from exc


WARNING_TYPES = [
    "ambiguity_warning",
    "control_profile_mimicry_warning",
    "residual_matched_profile_warning",
    "adversarial_profile_warning",
    "profile_weight_sensitivity_warning",
    "penalty_weight_sensitivity_warning",
    "kernel_size_sensitivity_warning",
    "null_family_overlap_warning",
    "decoy_success_warning",
    "control_overlap_warning",
]

COUNT_SUMMARY_KEYS = {
    "ambiguity_warning": "ambiguity_warning_count",
    "control_profile_mimicry_warning": "control_profile_mimicry_warnings_count",
    "residual_matched_profile_warning": "residual_matched_profile_warnings_count",
    "adversarial_profile_warning": "adversarial_profile_warnings_count",
    "profile_weight_sensitivity_warning": "profile_weight_sensitivity_warnings_count",
    "penalty_weight_sensitivity_warning": "penalty_weight_sensitivity_warnings_count",
    "kernel_size_sensitivity_warning": "kernel_size_sensitivity_warnings_count",
    "null_family_overlap_warning": "null_family_overlap_warnings_count",
    "decoy_success_warning": "decoy_success_warnings_count",
    "control_overlap_warning": "control_overlap_warnings_count",
}

WARNING_TYPE_FIELDS = [
    "warning_type",
    "row_count",
    "warning_count",
    "warning_rate",
    "comparison_reference",
    "comparison_count",
    "interpretation_note",
]

DECOY_FIELDS = [
    "decoy_family",
    "row_count",
    "warning_count_total",
    "warning_rate",
    "decoy_success_warnings_count",
    "decoy_success_rate",
    "control_overlap_warnings_count",
    "control_overlap_rate",
    "null_family_overlap_warnings_count",
    "null_family_overlap_rate",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "mean_profile_separation_margin",
    "dominant_warning_type",
    "dominant_warning_rate",
    "failure_mode_label",
    "decision_status",
    "interpretation_note",
]

NULL_FIELDS = [
    "null_family",
    "row_count",
    "warning_count_total",
    "warning_rate",
    "null_family_overlap_warnings_count",
    "null_family_overlap_rate",
    "control_overlap_rate",
    "decoy_success_rate",
    "dominant_decoy_family",
    "dominant_warning_type",
    "dominant_warning_rate",
    "failure_mode_label",
    "decision_status",
    "interpretation_note",
]

PROFILE_WEIGHT_FIELDS = [
    "profile_weight_set_id",
    "row_count",
    "warning_count_total",
    "warning_rate",
    "profile_weight_sensitivity_warnings_count",
    "profile_weight_sensitivity_rate",
    "decoy_success_rate",
    "control_overlap_rate",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "sensitivity_rank",
    "failure_mode_label",
    "decision_status",
    "interpretation_note",
]

PENALTY_WEIGHT_FIELDS = [
    "penalty_weight_set_id",
    "row_count",
    "warning_count_total",
    "warning_rate",
    "penalty_weight_sensitivity_warnings_count",
    "penalty_weight_sensitivity_rate",
    "decoy_success_rate",
    "control_overlap_rate",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "mean_penalty_gap",
    "sensitivity_rank",
    "failure_mode_label",
    "decision_status",
    "interpretation_note",
]

KERNEL_FIELDS = [
    "kernel_size_label",
    "kernel_size",
    "row_count",
    "warning_count_total",
    "warning_rate",
    "kernel_size_sensitivity_warnings_count",
    "kernel_size_sensitivity_rate",
    "decoy_success_rate",
    "control_overlap_rate",
    "stable_candidate_count",
    "fragile_candidate_count",
    "stable_candidate_rate",
    "fragile_candidate_rate",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "failure_mode_label",
    "decision_status",
    "interpretation_note",
]

INTERACTION_FIELDS = [
    "interaction_axis",
    "interaction_value",
    "row_count",
    "warning_count_total",
    "interaction_warning_rate",
    "decoy_success_rate",
    "control_overlap_rate",
    "null_family_overlap_rate",
    "dominant_warning_type",
    "dominant_warning_rate",
    "failure_mode_label",
    "decision_status",
    "interpretation_note",
]

STABLE_FRAGILE_FIELDS = [
    "category",
    "row_count",
    "rate",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "mean_decoy_success_rate",
    "mean_control_overlap_rate",
    "dominant_decoy_family",
    "dominant_null_family",
    "dominant_profile_weight_set_id",
    "dominant_penalty_weight_set_id",
    "dominant_kernel_size_label",
    "interpretation_note",
]

RULE_FIELDS = [
    "rule_id",
    "description",
    "decision_table_label",
    "failure_mode_label",
    "severity",
    "conditions_summary",
    "interpretation_note",
]

CLASSIFICATION_FIELDS = [
    "case_id",
    "decoy_family",
    "null_family",
    "profile_weight_set_id",
    "penalty_weight_set_id",
    "kernel_size_label",
    "parameter_sweep_family",
    "matched_rule_ids",
    "decision_table_label",
    "failure_mode_label",
    "severity",
    "major_warning_count",
    "profile_distance_raw",
    "profile_distance_collision_penalized",
    "penalty_gap",
    "control_overlap_rate",
    "decoy_success_rate",
    "stable_candidate",
    "fragile_candidate",
    "interpretation_note",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D1g warning-driver decomposition on existing D1f outputs."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1g_warning_driver_decomposition_config.yaml",
    )
    return parser.parse_args()


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a mapping: {path}")
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    text = str(value).strip().lower()
    return text in {"true", "1", "yes", "y"}


def to_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def to_int(value: Any, default: int = 0) -> int:
    if value is None or value == "":
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def safe_rate(count: int, row_count: int) -> float:
    return count / row_count if row_count else 0.0


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    if isinstance(value, (list, dict)):
        return json.dumps(value, sort_keys=True, ensure_ascii=False)
    return str(value)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fields})


def warning_flag(row: dict[str, Any], warning_type: str) -> bool:
    if warning_type == "decoy_success_warning":
        return to_float(row.get("decoy_success_rate")) > 0.0
    if warning_type == "control_overlap_warning":
        return to_float(row.get("control_overlap_rate")) > 0.0
    return parse_bool(row.get(warning_type))


def enrich_rows(rows: list[dict[str, str]], major_flags: list[str]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for raw in rows:
        row: dict[str, Any] = dict(raw)
        row["decoy_success_warning"] = to_float(row.get("decoy_success_rate")) > 0.0
        row["control_overlap_warning"] = to_float(row.get("control_overlap_rate")) > 0.0
        row["profile_distance_raw_value"] = to_float(row.get("profile_distance_raw"))
        row["profile_distance_collision_penalized_value"] = to_float(
            row.get("profile_distance_collision_penalized")
        )
        row["profile_separation_margin_value"] = to_float(
            row.get("profile_separation_margin")
        )
        row["penalty_gap_value"] = (
            row["profile_distance_collision_penalized_value"]
            - row["profile_distance_raw_value"]
        )
        row["warning_count_total_value"] = to_int(row.get("warning_count_total"))
        row["major_warning_count"] = sum(
            1 for flag in major_flags if warning_flag(row, flag)
        )
        row["stable_candidate"] = row["major_warning_count"] == 0
        row["fragile_candidate"] = row["major_warning_count"] > 0
        enriched.append(row)
    return enriched


def top_counter_value(counter: Counter[str]) -> str:
    return counter.most_common(1)[0][0] if counter else ""


def dominant_warning(rows: list[dict[str, Any]]) -> tuple[str, float]:
    if not rows:
        return "", 0.0
    counts = {
        warning_type: sum(1 for row in rows if warning_flag(row, warning_type))
        for warning_type in WARNING_TYPES
    }
    warning_type, count = max(counts.items(), key=lambda item: (item[1], item[0]))
    return warning_type, safe_rate(count, len(rows))


def classify_rate(
    rate: float,
    high: float,
    medium: float,
    high_label: str,
    medium_label: str,
    low_label: str = "warning_driver_identified",
) -> str:
    if rate >= high:
        return high_label
    if rate >= medium:
        return medium_label
    return low_label


def failure_label_from_rows(rows: list[dict[str, Any]]) -> str:
    dominant, rate = dominant_warning(rows)
    if rate == 0:
        return "stable_under_tested_stress_candidate"
    mapping = {
        "control_profile_mimicry_warning": "false_accept_region_overlap_driven",
        "null_family_overlap_warning": "null_family_overlap_driven",
        "decoy_success_warning": "decoy_overlap_driven",
        "profile_weight_sensitivity_warning": "profile_weight_driven",
        "penalty_weight_sensitivity_warning": "penalty_weight_driven",
        "kernel_size_sensitivity_warning": "kernel_size_driven",
        "residual_matched_profile_warning": "residual_matched_decoy_driven",
        "adversarial_profile_warning": "adversarial_decoy_driven",
        "control_overlap_warning": "impostor_overlap_driven",
        "ambiguity_warning": "representation_instability_driven",
    }
    return mapping.get(dominant, "multi_driver_instability")


def decision_status_from_failure(label: str, rate: float) -> str:
    if label == "stable_under_tested_stress_candidate":
        return "stable_under_tested_stress_candidate"
    if rate >= 0.5:
        return "multi_driver_instability_warning"
    if "null_family" in label:
        return "null_family_overlap_driver_warning"
    if "decoy" in label:
        return "decoy_overlap_driver_warning"
    if "profile_weight" in label:
        return "profile_weight_driver_warning"
    if "penalty" in label:
        return "penalty_weight_driver_warning"
    if "kernel" in label:
        return "kernel_size_driver_warning"
    return "warning_driver_identified"


def summarize_group(
    rows: list[dict[str, Any]],
    key: str,
    fields: list[str],
    row_builder,
) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key, ""))].append(row)
    result = [row_builder(group_key, group_rows) for group_key, group_rows in groups.items()]
    return sorted(result, key=lambda item: str(item.get(fields[0], "")))


def count_flag(rows: list[dict[str, Any]], flag: str) -> int:
    return sum(1 for row in rows if warning_flag(row, flag))


def mean_field(rows: list[dict[str, Any]], field: str) -> float:
    return safe_mean([to_float(row.get(field)) for row in rows])


def build_warning_type_summary(
    rows: list[dict[str, Any]], summary: dict[str, Any]
) -> list[dict[str, Any]]:
    result = []
    for warning_type in WARNING_TYPES:
        count = count_flag(rows, warning_type)
        summary_key = COUNT_SUMMARY_KEYS.get(warning_type)
        comparison_count = summary.get(summary_key, count)
        result.append(
            {
                "warning_type": warning_type,
                "row_count": len(rows),
                "warning_count": count,
                "warning_rate": safe_rate(count, len(rows)),
                "comparison_reference": "D1f summary.json",
                "comparison_count": comparison_count,
                "interpretation_note": (
                    "Methodological warning-driver count; no specificity or proof claim."
                ),
            }
        )
    return sorted(result, key=lambda row: (-to_int(row["warning_count"]), row["warning_type"]))


def build_decoy_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def make(decoy: str, group: list[dict[str, Any]]) -> dict[str, Any]:
        dominant, dom_rate = dominant_warning(group)
        failure = failure_label_from_rows(group)
        warning_total = sum(to_int(row.get("warning_count_total")) for row in group)
        row_count = len(group)
        return {
            "decoy_family": decoy,
            "row_count": row_count,
            "warning_count_total": warning_total,
            "warning_rate": safe_rate(warning_total, row_count * len(WARNING_TYPES)),
            "decoy_success_warnings_count": count_flag(group, "decoy_success_warning"),
            "decoy_success_rate": safe_rate(count_flag(group, "decoy_success_warning"), row_count),
            "control_overlap_warnings_count": count_flag(group, "control_overlap_warning"),
            "control_overlap_rate": safe_rate(count_flag(group, "control_overlap_warning"), row_count),
            "null_family_overlap_warnings_count": count_flag(group, "null_family_overlap_warning"),
            "null_family_overlap_rate": safe_rate(count_flag(group, "null_family_overlap_warning"), row_count),
            "mean_profile_distance_raw": mean_field(group, "profile_distance_raw"),
            "mean_profile_distance_collision_penalized": mean_field(
                group, "profile_distance_collision_penalized"
            ),
            "mean_profile_separation_margin": mean_field(group, "profile_separation_margin"),
            "dominant_warning_type": dominant,
            "dominant_warning_rate": dom_rate,
            "failure_mode_label": failure,
            "decision_status": decision_status_from_failure(failure, dom_rate),
            "interpretation_note": (
                "Decoy-family diagnostic driver summary; not a physical category."
            ),
        }

    return summarize_group(rows, "decoy_family", DECOY_FIELDS, make)


def build_null_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    def make(null_family: str, group: list[dict[str, Any]]) -> dict[str, Any]:
        dominant, dom_rate = dominant_warning(group)
        failure = failure_label_from_rows(group)
        warning_total = sum(to_int(row.get("warning_count_total")) for row in group)
        row_count = len(group)
        overlap_rows = [row for row in group if warning_flag(row, "null_family_overlap_warning")]
        return {
            "null_family": null_family,
            "row_count": row_count,
            "warning_count_total": warning_total,
            "warning_rate": safe_rate(warning_total, row_count * len(WARNING_TYPES)),
            "null_family_overlap_warnings_count": count_flag(group, "null_family_overlap_warning"),
            "null_family_overlap_rate": safe_rate(count_flag(group, "null_family_overlap_warning"), row_count),
            "control_overlap_rate": safe_rate(count_flag(group, "control_overlap_warning"), row_count),
            "decoy_success_rate": safe_rate(count_flag(group, "decoy_success_warning"), row_count),
            "dominant_decoy_family": top_counter_value(
                Counter(row.get("decoy_family", "") for row in overlap_rows or group)
            ),
            "dominant_warning_type": dominant,
            "dominant_warning_rate": dom_rate,
            "failure_mode_label": failure,
            "decision_status": decision_status_from_failure(failure, dom_rate),
            "interpretation_note": "Null-family overlap summary; diagnostic control only.",
        }

    return summarize_group(rows, "null_family", NULL_FIELDS, make)


def add_sensitivity_ranks(rows: list[dict[str, Any]], rate_key: str) -> list[dict[str, Any]]:
    ordered = sorted(rows, key=lambda row: (-to_float(row.get(rate_key)), str(row)))
    for index, row in enumerate(ordered, start=1):
        row["sensitivity_rank"] = index
    return sorted(ordered, key=lambda row: str(row.get(next(iter(row)), "")))


def build_profile_weight_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for profile_id, group in sorted(group_rows(rows, "profile_weight_set_id").items()):
        dominant, dom_rate = dominant_warning(group)
        failure = failure_label_from_rows(group)
        warning_total = sum(to_int(row.get("warning_count_total")) for row in group)
        row_count = len(group)
        profile_count = count_flag(group, "profile_weight_sensitivity_warning")
        result.append(
            {
                "profile_weight_set_id": profile_id,
                "row_count": row_count,
                "warning_count_total": warning_total,
                "warning_rate": safe_rate(warning_total, row_count * len(WARNING_TYPES)),
                "profile_weight_sensitivity_warnings_count": profile_count,
                "profile_weight_sensitivity_rate": safe_rate(profile_count, row_count),
                "decoy_success_rate": safe_rate(count_flag(group, "decoy_success_warning"), row_count),
                "control_overlap_rate": safe_rate(count_flag(group, "control_overlap_warning"), row_count),
                "mean_profile_distance_raw": mean_field(group, "profile_distance_raw"),
                "mean_profile_distance_collision_penalized": mean_field(
                    group, "profile_distance_collision_penalized"
                ),
                "failure_mode_label": failure,
                "decision_status": decision_status_from_failure(failure, dom_rate),
                "interpretation_note": (
                    "Profile-weight driver summary; weight sensitivity is methodological."
                ),
            }
        )
    return add_sensitivity_ranks(result, "profile_weight_sensitivity_rate")


def build_penalty_weight_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for penalty_id, group in sorted(group_rows(rows, "penalty_weight_set_id").items()):
        dominant, dom_rate = dominant_warning(group)
        failure = failure_label_from_rows(group)
        warning_total = sum(to_int(row.get("warning_count_total")) for row in group)
        row_count = len(group)
        penalty_count = count_flag(group, "penalty_weight_sensitivity_warning")
        result.append(
            {
                "penalty_weight_set_id": penalty_id,
                "row_count": row_count,
                "warning_count_total": warning_total,
                "warning_rate": safe_rate(warning_total, row_count * len(WARNING_TYPES)),
                "penalty_weight_sensitivity_warnings_count": penalty_count,
                "penalty_weight_sensitivity_rate": safe_rate(penalty_count, row_count),
                "decoy_success_rate": safe_rate(count_flag(group, "decoy_success_warning"), row_count),
                "control_overlap_rate": safe_rate(count_flag(group, "control_overlap_warning"), row_count),
                "mean_profile_distance_raw": mean_field(group, "profile_distance_raw"),
                "mean_profile_distance_collision_penalized": mean_field(
                    group, "profile_distance_collision_penalized"
                ),
                "mean_penalty_gap": safe_mean([row["penalty_gap_value"] for row in group]),
                "failure_mode_label": failure,
                "decision_status": decision_status_from_failure(failure, dom_rate),
                "interpretation_note": (
                    "Penalty-weight driver summary; penalties are warning terms only."
                ),
            }
        )
    return add_sensitivity_ranks(result, "penalty_weight_sensitivity_rate")


def build_kernel_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for kernel_label, group in sorted(group_rows(rows, "kernel_size_label").items()):
        dominant, dom_rate = dominant_warning(group)
        failure = failure_label_from_rows(group)
        warning_total = sum(to_int(row.get("warning_count_total")) for row in group)
        row_count = len(group)
        stable = sum(1 for row in group if row["stable_candidate"])
        fragile = row_count - stable
        kernel_count = count_flag(group, "kernel_size_sensitivity_warning")
        result.append(
            {
                "kernel_size_label": kernel_label,
                "kernel_size": group[0].get("kernel_size", ""),
                "row_count": row_count,
                "warning_count_total": warning_total,
                "warning_rate": safe_rate(warning_total, row_count * len(WARNING_TYPES)),
                "kernel_size_sensitivity_warnings_count": kernel_count,
                "kernel_size_sensitivity_rate": safe_rate(kernel_count, row_count),
                "decoy_success_rate": safe_rate(count_flag(group, "decoy_success_warning"), row_count),
                "control_overlap_rate": safe_rate(count_flag(group, "control_overlap_warning"), row_count),
                "stable_candidate_count": stable,
                "fragile_candidate_count": fragile,
                "stable_candidate_rate": safe_rate(stable, row_count),
                "fragile_candidate_rate": safe_rate(fragile, row_count),
                "mean_profile_distance_raw": mean_field(group, "profile_distance_raw"),
                "mean_profile_distance_collision_penalized": mean_field(
                    group, "profile_distance_collision_penalized"
                ),
                "failure_mode_label": failure,
                "decision_status": decision_status_from_failure(failure, dom_rate),
                "interpretation_note": (
                    "Kernel-size sensitivity is synthetic and methodological only."
                ),
            }
        )
    return result


def group_rows(rows: list[dict[str, Any]], key: str) -> dict[str, list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[str(row.get(key, ""))].append(row)
    return groups


def build_interaction_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    axes = [
        ("decoy_family x null_family", ("decoy_family", "null_family")),
        ("decoy_family x profile_weight_set_id", ("decoy_family", "profile_weight_set_id")),
        ("decoy_family x penalty_weight_set_id", ("decoy_family", "penalty_weight_set_id")),
        ("kernel_size_label x decoy_family", ("kernel_size_label", "decoy_family")),
        ("parameter_sweep_family x decoy_family", ("parameter_sweep_family", "decoy_family")),
    ]
    result = []
    for axis_name, keys in axes:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            value = " | ".join(str(row.get(key, "")) for key in keys)
            groups[value].append(row)
        for value, group in groups.items():
            dominant, dom_rate = dominant_warning(group)
            failure = failure_label_from_rows(group)
            warning_total = sum(to_int(row.get("warning_count_total")) for row in group)
            row_count = len(group)
            result.append(
                {
                    "interaction_axis": axis_name,
                    "interaction_value": value,
                    "row_count": row_count,
                    "warning_count_total": warning_total,
                    "interaction_warning_rate": safe_rate(
                        warning_total, row_count * len(WARNING_TYPES)
                    ),
                    "decoy_success_rate": safe_rate(
                        count_flag(group, "decoy_success_warning"), row_count
                    ),
                    "control_overlap_rate": safe_rate(
                        count_flag(group, "control_overlap_warning"), row_count
                    ),
                    "null_family_overlap_rate": safe_rate(
                        count_flag(group, "null_family_overlap_warning"), row_count
                    ),
                    "dominant_warning_type": dominant,
                    "dominant_warning_rate": dom_rate,
                    "failure_mode_label": failure,
                    "decision_status": decision_status_from_failure(failure, dom_rate),
                    "interpretation_note": (
                        "Interaction driver summary for diagnostic decomposition."
                    ),
                }
            )
    return sorted(
        result,
        key=lambda row: (
            str(row["interaction_axis"]),
            -to_float(row["interaction_warning_rate"]),
            str(row["interaction_value"]),
        ),
    )


def build_stable_fragile_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for category, predicate in [
        ("stable_candidate", lambda row: row["stable_candidate"]),
        ("fragile_candidate", lambda row: row["fragile_candidate"]),
    ]:
        group = [row for row in rows if predicate(row)]
        row_count = len(group)
        result.append(
            {
                "category": category,
                "row_count": row_count,
                "rate": safe_rate(row_count, len(rows)),
                "mean_profile_distance_raw": mean_field(group, "profile_distance_raw"),
                "mean_profile_distance_collision_penalized": mean_field(
                    group, "profile_distance_collision_penalized"
                ),
                "mean_decoy_success_rate": mean_field(group, "decoy_success_rate"),
                "mean_control_overlap_rate": mean_field(group, "control_overlap_rate"),
                "dominant_decoy_family": top_counter_value(
                    Counter(row.get("decoy_family", "") for row in group)
                ),
                "dominant_null_family": top_counter_value(
                    Counter(row.get("null_family", "") for row in group)
                ),
                "dominant_profile_weight_set_id": top_counter_value(
                    Counter(row.get("profile_weight_set_id", "") for row in group)
                ),
                "dominant_penalty_weight_set_id": top_counter_value(
                    Counter(row.get("penalty_weight_set_id", "") for row in group)
                ),
                "dominant_kernel_size_label": top_counter_value(
                    Counter(row.get("kernel_size_label", "") for row in group)
                ),
                "interpretation_note": (
                    "Stable means no major warning under tested stress, not identity proof."
                    if category == "stable_candidate"
                    else "Fragile means at least one major warning under tested stress."
                ),
            }
        )
    return result


def conditions_summary(conditions: dict[str, Any]) -> str:
    return json.dumps(conditions, sort_keys=True, ensure_ascii=False)


def build_rule_rows(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "rule_id": rule["rule_id"],
            "description": rule.get("description", ""),
            "decision_table_label": rule["decision_table_label"],
            "failure_mode_label": rule["failure_mode_label"],
            "severity": rule["severity"],
            "conditions_summary": conditions_summary(rule.get("conditions", {})),
            "interpretation_note": (
                "Transparent methodological decision table rule, not a physical law."
            ),
        }
        for rule in rules
    ]


def condition_matches(row: dict[str, Any], conditions: dict[str, Any]) -> bool:
    if "min_active_major_warning_flags" in conditions:
        if row["major_warning_count"] < int(conditions["min_active_major_warning_flags"]):
            return False
    if "any_true" in conditions:
        if not any(warning_flag(row, flag) for flag in conditions["any_true"]):
            return False
    if "all_false" in conditions:
        if any(warning_flag(row, flag) for flag in conditions["all_false"]):
            return False
    if "profile_weight_set_id_equals" in conditions:
        if row.get("profile_weight_set_id") != conditions["profile_weight_set_id_equals"]:
            return False
    if "profile_weight_set_id_in" in conditions:
        if row.get("profile_weight_set_id") not in conditions["profile_weight_set_id_in"]:
            return False
    if "penalty_weight_set_id_equals" in conditions:
        if row.get("penalty_weight_set_id") != conditions["penalty_weight_set_id_equals"]:
            return False
    if conditions.get("requires_penalty_gap_positive"):
        if row["penalty_gap_value"] <= 0.0:
            return False
    return True


def classify_row(row: dict[str, Any], rules: list[dict[str, Any]]) -> dict[str, Any]:
    severity_rank = {"inconclusive": 0, "low": 1, "medium": 2, "high": 3}
    rule_priority = {
        "DT005_coordinate_dominant_open_door": 100,
        "DT002_false_accept_region_warning": 90,
        "DT006_collision_penalty_off_open_door": 80,
        "DT008_penalty_cosmetic_lock": 70,
        "DT003_impostor_distribution_overlap": 60,
        "DT001_multi_driver_instability": 50,
        "DT009_kernel_shift_warning": 40,
        "DT007_control_response_low_open_door": 30,
        "DT004_representation_instability": 20,
        "DT010_stable_under_tested_stress_candidate": 10,
    }
    matched = []
    best = {
        "decision_table_label": "inconclusive",
        "failure_mode_label": "inconclusive",
        "severity": "inconclusive",
        "priority": -1,
    }
    for rule in rules:
        if condition_matches(row, rule.get("conditions", {})):
            matched.append(rule["rule_id"])
            rank = severity_rank[rule["severity"]]
            priority = rule_priority.get(rule["rule_id"], 0)
            best_rank = severity_rank[best["severity"]]
            if rank > best_rank or (rank == best_rank and priority > best["priority"]):
                best = {
                    "decision_table_label": rule["decision_table_label"],
                    "failure_mode_label": rule["failure_mode_label"],
                    "severity": rule["severity"],
                    "priority": priority,
                }
    return {
        "case_id": row.get("case_id", ""),
        "decoy_family": row.get("decoy_family", ""),
        "null_family": row.get("null_family", ""),
        "profile_weight_set_id": row.get("profile_weight_set_id", ""),
        "penalty_weight_set_id": row.get("penalty_weight_set_id", ""),
        "kernel_size_label": row.get("kernel_size_label", ""),
        "parameter_sweep_family": row.get("parameter_sweep_family", ""),
        "matched_rule_ids": ";".join(matched),
        "decision_table_label": best["decision_table_label"],
        "failure_mode_label": best["failure_mode_label"],
        "severity": best["severity"],
        "major_warning_count": row["major_warning_count"],
        "profile_distance_raw": row.get("profile_distance_raw", ""),
        "profile_distance_collision_penalized": row.get(
            "profile_distance_collision_penalized", ""
        ),
        "penalty_gap": row["penalty_gap_value"],
        "control_overlap_rate": row.get("control_overlap_rate", ""),
        "decoy_success_rate": row.get("decoy_success_rate", ""),
        "stable_candidate": row["stable_candidate"],
        "fragile_candidate": row["fragile_candidate"],
        "interpretation_note": (
            "Decision-table classification is methodological and diagnostic only."
        ),
    }


def compute_consistency(
    rows: list[dict[str, Any]], summary: dict[str, Any], config: dict[str, Any]
) -> tuple[bool, list[str]]:
    warnings: list[str] = []
    case_count = summary.get("case_count")
    if case_count is None:
        raise SystemExit("D1f summary.json is missing case_count.")
    if len(rows) != int(case_count):
        warnings.append(f"case row count {len(rows)} != summary case_count {case_count}")
    reference_count = config.get("d1f_reference", {}).get("case_count")
    if reference_count is not None and len(rows) != int(reference_count):
        warnings.append(
            f"case row count {len(rows)} != configured reference case_count {reference_count}"
        )
    if parse_bool(summary.get("specificity_established")):
        warnings.append("summary specificity_established is not false")
    if any(parse_bool(row.get("specificity_established")) for row in rows):
        warnings.append("at least one case row has specificity_established true")
    for warning_type, summary_key in COUNT_SUMMARY_KEYS.items():
        if summary_key not in summary:
            continue
        actual = count_flag(rows, warning_type)
        expected = int(summary[summary_key])
        if actual != expected:
            warnings.append(f"{warning_type} count {actual} != summary {expected}")
    actual_warning_total = sum(to_int(row.get("warning_count_total")) for row in rows)
    if actual_warning_total != int(summary.get("warning_count_total", actual_warning_total)):
        warnings.append(
            f"warning_count_total rows {actual_warning_total} != summary "
            f"{summary.get('warning_count_total')}"
        )
    return not warnings, warnings


def top_by_rate(rows: list[dict[str, Any]], label_key: str, rate_key: str) -> tuple[str, float]:
    if not rows:
        return "", 0.0
    top = max(rows, key=lambda row: (to_float(row.get(rate_key)), str(row.get(label_key))))
    return str(top.get(label_key, "")), to_float(top.get(rate_key))


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    status = "\n".join(f"{key}: {json.dumps(value)}" for key, value in summary.items())
    path.write_text(
        "\n".join(
            [
                "# QSB-ST-COMP01-D1g Warning Driver Decomposition and Failure-Mode Analysis Readout",
                "",
                "## Befund",
                "",
                "D1g is a Warning-Driver-Decomposition on existing D1f data.",
                "",
                "D1g does not rerun D1f and does not introduce a new identity score.",
                "",
                f"`case_count`: {summary['case_count']}",
                f"`specificity_established`: {str(summary['specificity_established']).lower()}",
                f"`top_warning_type`: {summary['top_warning_type']} ({summary['top_warning_count']})",
                f"`top_decoy_family`: {summary['top_decoy_family']}",
                f"`top_null_family`: {summary['top_null_family']}",
                f"`top_profile_weight_set`: {summary['top_profile_weight_set']}",
                f"`top_penalty_weight_set`: {summary['top_penalty_weight_set']}",
                f"`top_kernel_size_label`: {summary['top_kernel_size_label']}",
                f"`stable_candidate_count`: {summary['stable_candidate_count']}",
                f"`fragile_candidate_count`: {summary['fragile_candidate_count']}",
                f"`dominant_failure_mode_label`: {summary['dominant_failure_mode_label']}",
                "",
                "## Interpretation",
                "",
                "The decomposition reads the D1f warning return as a methodological pattern involving false accept region, impostor distribution overlap, representation instability, and threshold fragility. These terms are diagnostic language only.",
                "",
                "The decision table reports transparent rule-based classifications for warning combinations. It is not a blackbox and not an ML classifier.",
                "",
                "## Hypothese",
                "",
                "Future work may reduce instability by redesigning profile-component orchestration, penalty behavior, null filters, and decoy-resistance checks. This remains a diagnostic hypothesis.",
                "",
                "## Offene Lücke",
                "",
                "- no real data",
                "- no physical validation",
                "- no diagnostic specificity is established",
                "- no physical manifold",
                "- no Lorentzian structure",
                "- no physical time",
                "- no Pauli claim",
                "- no Bridge validation",
                "",
                "## Claim Boundary",
                "",
                "D1g is a synthetic diagnostic warning-driver decomposition only.",
                "",
                "It does not introduce a new identity score.",
                "",
                "It does not rerun D1f.",
                "",
                "Failure-mode labels are methodological diagnostic labels, not physical categories.",
                "",
                "Decision tables are transparent methodological classification rules, not physical laws.",
                "",
                "The manifold language is not a physical spacetime manifold.",
                "",
                "This does not validate a physical Bridge, does not derive a Lorentz metric, does not recover physical time, and does not claim fermionic Pauli exclusion.",
                "",
                "## Machine-readable status",
                "",
                "```yaml",
                status,
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = read_config(config_path)
    output_dir = Path(config["output_dir"])
    input_files = config["input_files"]
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = json.loads(Path(input_files["d1f_summary"]).read_text(encoding="utf-8"))
    case_rows_raw = read_csv_rows(Path(input_files["case_profile_summary"]))

    # Read the remaining D1f summaries to verify their availability without rewriting them.
    for key in [
        "profile_weight_summary",
        "decoy_family_summary",
        "kernel_size_summary",
        "null_family_summary",
        "warning_stability_summary",
    ]:
        read_csv_rows(Path(input_files[key]))

    major_flags = list(config.get("major_warning_flags", []))
    rows = enrich_rows(case_rows_raw, major_flags)
    input_consistency_passed, input_consistency_warnings = compute_consistency(
        rows, summary, config
    )

    warning_type_rows = build_warning_type_summary(rows, summary)
    decoy_rows = build_decoy_summary(rows)
    null_rows = build_null_summary(rows)
    profile_weight_rows = build_profile_weight_summary(rows)
    penalty_weight_rows = build_penalty_weight_summary(rows)
    kernel_rows = build_kernel_summary(rows)
    interaction_rows = build_interaction_summary(rows)
    stable_fragile_rows = build_stable_fragile_summary(rows)
    rule_rows = build_rule_rows(config.get("decision_table_rules", []))
    classification_rows = [
        classify_row(row, config.get("decision_table_rules", [])) for row in rows
    ]

    generated_files = [
        "summary.json",
        "readout.md",
        "warning_type_summary.csv",
        "decoy_driver_summary.csv",
        "null_family_driver_summary.csv",
        "profile_weight_driver_summary.csv",
        "penalty_weight_driver_summary.csv",
        "kernel_size_driver_summary.csv",
        "interaction_driver_summary.csv",
        "stable_fragile_case_summary.csv",
        "decision_table_rules.csv",
        "decision_table_case_classification.csv",
        "resolved_config.json",
    ]

    write_csv(output_dir / "warning_type_summary.csv", warning_type_rows, WARNING_TYPE_FIELDS)
    write_csv(output_dir / "decoy_driver_summary.csv", decoy_rows, DECOY_FIELDS)
    write_csv(output_dir / "null_family_driver_summary.csv", null_rows, NULL_FIELDS)
    write_csv(
        output_dir / "profile_weight_driver_summary.csv",
        profile_weight_rows,
        PROFILE_WEIGHT_FIELDS,
    )
    write_csv(
        output_dir / "penalty_weight_driver_summary.csv",
        penalty_weight_rows,
        PENALTY_WEIGHT_FIELDS,
    )
    write_csv(output_dir / "kernel_size_driver_summary.csv", kernel_rows, KERNEL_FIELDS)
    write_csv(
        output_dir / "interaction_driver_summary.csv",
        interaction_rows,
        INTERACTION_FIELDS,
    )
    write_csv(
        output_dir / "stable_fragile_case_summary.csv",
        stable_fragile_rows,
        STABLE_FRAGILE_FIELDS,
    )
    write_csv(output_dir / "decision_table_rules.csv", rule_rows, RULE_FIELDS)
    write_csv(
        output_dir / "decision_table_case_classification.csv",
        classification_rows,
        CLASSIFICATION_FIELDS,
    )

    top_warning = warning_type_rows[0]
    top_decoy_family, top_decoy_warning_rate = top_by_rate(
        decoy_rows, "decoy_family", "warning_rate"
    )
    top_null_family, top_null_overlap_rate = top_by_rate(
        null_rows, "null_family", "null_family_overlap_rate"
    )
    top_profile_weight_set, top_profile_weight_warning_rate = top_by_rate(
        profile_weight_rows,
        "profile_weight_set_id",
        "profile_weight_sensitivity_rate",
    )
    top_penalty_weight_set, top_penalty_warning_rate = top_by_rate(
        penalty_weight_rows,
        "penalty_weight_set_id",
        "penalty_weight_sensitivity_rate",
    )
    top_kernel_size_label, top_kernel_warning_rate = top_by_rate(
        kernel_rows, "kernel_size_label", "kernel_size_sensitivity_rate"
    )
    stable_candidate_count = sum(1 for row in rows if row["stable_candidate"])
    fragile_candidate_count = len(rows) - stable_candidate_count
    severity_counts = Counter(row["severity"] for row in classification_rows)
    failure_counts = Counter(row["failure_mode_label"] for row in classification_rows)
    dominant_failure_mode_label = top_counter_value(failure_counts)

    out_summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "input_run_id": summary.get("run_id", "collision_aware_profile_robustness_sweep_open"),
        "output_dir": config["output_dir"],
        "case_count": len(rows),
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_introduce_new_identity_score": True,
        "input_consistency_passed": input_consistency_passed,
        "input_consistency_warnings": input_consistency_warnings,
        "warning_type_count": len(WARNING_TYPES),
        "top_warning_type": top_warning["warning_type"],
        "top_warning_count": top_warning["warning_count"],
        "top_warning_rate": top_warning["warning_rate"],
        "top_decoy_family": top_decoy_family,
        "top_decoy_warning_rate": top_decoy_warning_rate,
        "top_null_family": top_null_family,
        "top_null_overlap_rate": top_null_overlap_rate,
        "top_profile_weight_set": top_profile_weight_set,
        "top_profile_weight_warning_rate": top_profile_weight_warning_rate,
        "top_penalty_weight_set": top_penalty_weight_set,
        "top_penalty_warning_rate": top_penalty_warning_rate,
        "top_kernel_size_label": top_kernel_size_label,
        "top_kernel_warning_rate": top_kernel_warning_rate,
        "stable_candidate_count": stable_candidate_count,
        "fragile_candidate_count": fragile_candidate_count,
        "stable_candidate_rate": safe_rate(stable_candidate_count, len(rows)),
        "fragile_candidate_rate": safe_rate(fragile_candidate_count, len(rows)),
        "decision_table_rule_count": len(rule_rows),
        "decision_table_high_severity_count": severity_counts.get("high", 0),
        "decision_table_medium_severity_count": severity_counts.get("medium", 0),
        "decision_table_low_severity_count": severity_counts.get("low", 0),
        "dominant_failure_mode_label": dominant_failure_mode_label,
        "generated_files": generated_files,
        "claim_boundary": config.get("metadata", {}).get(
            "claim_boundary", "synthetic diagnostic warning-driver decomposition only"
        ),
    }

    (output_dir / "summary.json").write_text(
        json.dumps(out_summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_readout(output_dir / "readout.md", out_summary)
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True), encoding="utf-8"
    )

    print(json.dumps(out_summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
