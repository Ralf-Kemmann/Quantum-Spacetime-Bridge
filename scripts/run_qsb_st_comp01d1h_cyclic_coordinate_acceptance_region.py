#!/usr/bin/env python3
"""QSB-ST-COMP01-D1h synthetic cyclic-coordinate acceptance-region analysis.

This runner reads existing D1f and D1g outputs. It does not rerun D1f,
does not modify D1g outputs, and does not introduce a physical manifold or
new identity score.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
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


CASE_FIELDS = [
    "run_id",
    "case_id",
    "decoy_family",
    "null_family",
    "profile_weight_set_id",
    "penalty_weight_set_id",
    "kernel_size_label",
    "current_decision_table_label",
    "current_failure_mode_label",
    "cyclic_phase_distance",
    "cyclic_phase_source",
    "cyclic_phase_band",
    "cyclic_region_label",
    "cylindrical_region_label",
    "cyclic_linear_balance",
    "profile_distance_raw",
    "profile_distance_collision_penalized",
    "penalty_gap",
    "control_overlap_rate",
    "decoy_success_rate",
    "cyclic_acceptance_distance",
    "cyclic_acceptance_region_member",
    "current_false_accept_warning",
    "cyclic_false_accept_warning",
    "impostor_overlap_warning",
    "spectrum_matched_null_exclusion_warning",
    "adversarial_near_duplicate_exclusion_warning",
    "local_response_dominant_exclusion_warning",
    "cosmetic_penalty_lock_warning",
    "kernel_size_8_artifact_warning",
    "phase_wrap_distance_warning",
    "stable_candidate_current",
    "stable_candidate_cyclic",
    "fragile_candidate_current",
    "fragile_candidate_cyclic",
    "warning_count_current",
    "warning_count_cyclic",
    "warning_delta_current_to_cyclic",
    "exclusion_success_flag",
    "exclusion_failure_flag",
    "decision_status",
    "warning_flags",
    "interpretation_note",
]

COMPARISON_FIELDS = [
    "metric_name",
    "current_value",
    "cyclic_value",
    "delta_cyclic_minus_current",
    "interpretation_note",
]

IMPOSTOR_FIELDS = [
    "grouping_axis",
    "grouping_value",
    "row_count",
    "current_false_accept_warning_count",
    "cyclic_false_accept_warning_count",
    "exclusion_success_count",
    "exclusion_failure_count",
    "exclusion_success_rate",
    "exclusion_failure_rate",
    "mean_cyclic_acceptance_distance",
    "dominant_decision_status",
    "interpretation_note",
]

DECISION_FIELDS = [
    "decision_status",
    "row_count",
    "rate",
    "high_risk_count",
    "medium_risk_count",
    "low_risk_count",
    "interpretation_note",
]

KERNEL_FIELDS = [
    "kernel_size_label",
    "row_count",
    "cyclic_false_accept_warning_count",
    "cyclic_false_accept_warning_rate",
    "kernel_size_8_artifact_warning_count",
    "mean_cyclic_acceptance_distance",
    "stable_candidate_cyclic_count",
    "fragile_candidate_cyclic_count",
    "interpretation_note",
]

CYCLIC_WARNING_FLAGS = [
    "cyclic_false_accept_warning",
    "impostor_overlap_warning",
    "spectrum_matched_null_exclusion_warning",
    "adversarial_near_duplicate_exclusion_warning",
    "local_response_dominant_exclusion_warning",
    "cosmetic_penalty_lock_warning",
    "kernel_size_8_artifact_warning",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D1h cyclic-coordinate acceptance-region analysis."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1h_cyclic_coordinate_acceptance_region_config.yaml",
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
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


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


def safe_rate(count: int, total: int) -> float:
    return count / total if total else 0.0


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


def wrap_minus_pi_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def stable_int(text: str) -> int:
    return int(hashlib.md5(text.encode("utf-8")).hexdigest()[:12], 16)


def cyclic_phase_distance(row: dict[str, Any]) -> tuple[float, str]:
    candidates = [
        "wrapped_delta_phi_abs",
        "cyclic_phase_proxy",
        "angular_phase_distance",
        "phase_distance",
    ]
    for field in candidates:
        if row.get(field) not in (None, ""):
            raw = abs(to_float(row.get(field)))
            if field == "wrapped_delta_phi_abs":
                return min(raw / math.pi, 1.0), field
            return min(abs(wrap_minus_pi_pi(raw)) / math.pi, 1.0), field

    profile_distance_raw = to_float(row.get("profile_distance_raw"))
    seed_text = f"{row.get('case_id', '')}{row.get('decoy_family', '')}{row.get('null_family', '')}"
    hash_angle = 2.0 * math.pi * ((stable_int(seed_text) % 1_000_000) / 1_000_000.0)
    proxy = wrap_minus_pi_pi(hash_angle + (2.0 * math.pi * profile_distance_raw))
    return abs(wrap_minus_pi_pi(proxy)) / math.pi, "cyclic_phase_proxy"


def phase_band(distance: float, thresholds: dict[str, Any]) -> str:
    if distance <= to_float(thresholds["cyclic_phase_small"]):
        return "small"
    if distance <= to_float(thresholds["cyclic_phase_medium"]):
        return "medium"
    if distance <= to_float(thresholds["cyclic_phase_large"]):
        return "large"
    return "outer"


def label_contains_any(value: str, fragments: list[str]) -> bool:
    text = value.lower()
    return any(fragment in text for fragment in fragments)


def join_inputs(
    d1f_rows: list[dict[str, str]], d1g_rows: list[dict[str, str]]
) -> tuple[list[dict[str, Any]], list[str]]:
    warnings: list[str] = []
    d1f_by_case = {row["case_id"]: row for row in d1f_rows}
    joined: list[dict[str, Any]] = []
    missing = 0
    for d1g in d1g_rows:
        case_id = d1g.get("case_id", "")
        d1f = d1f_by_case.get(case_id)
        if d1f is None:
            missing += 1
            continue
        row: dict[str, Any] = dict(d1f)
        row.update(d1g)
        joined.append(row)
    if missing:
        warnings.append(f"missing_d1f_join_rows: {missing}")
    if len(joined) != len(d1g_rows):
        warnings.append(f"joined_rows: {len(joined)} d1g_rows: {len(d1g_rows)}")
    if len(joined) < 9000:
        raise SystemExit(
            f"Input consistency failure: joined only {len(joined)} rows; expected at least 9000."
        )
    return joined, warnings


def current_false_accept(row: dict[str, Any]) -> bool:
    label_text = " ".join(
        [
            str(row.get("decision_table_label", "")),
            str(row.get("failure_mode_label", "")),
        ]
    )
    fragile = parse_bool(row.get("fragile_candidate"))
    control_overlap_rate = to_float(row.get("control_overlap_rate"))
    return label_contains_any(label_text, ["false_accept", "impostor", "overlap"]) or (
        fragile and control_overlap_rate > 0.0
    )


def current_impostor_overlap(row: dict[str, Any]) -> bool:
    label_text = " ".join(
        [
            str(row.get("decision_table_label", "")),
            str(row.get("failure_mode_label", "")),
        ]
    )
    return label_contains_any(label_text, ["impostor", "overlap"]) or to_float(
        row.get("control_overlap_rate")
    ) > 0.0


def decide_status(row: dict[str, Any], input_consistency_passed: bool) -> str:
    if not input_consistency_passed:
        return "failed_input_consistency_check"
    if row["spectrum_matched_null_exclusion_warning"]:
        return "spectrum_matched_null_intrusion_warning"
    if row["adversarial_near_duplicate_exclusion_warning"]:
        return "adversarial_near_duplicate_intrusion_warning"
    if row["cosmetic_penalty_lock_warning"]:
        return "cosmetic_penalty_lock_warning"
    if row["kernel_size_8_artifact_warning"]:
        return "kernel_size_8_artifact_warning"
    if row["local_response_dominant_exclusion_warning"]:
        return "local_response_open_door_warning"
    if row["phase_wrap_distance_warning"]:
        return "phase_wrap_distance_warning"
    if row["cyclic_false_accept_warning"]:
        return "cyclic_false_accept_warning"
    if row["exclusion_success_flag"]:
        return "cyclic_region_reduces_false_accept_candidate"
    if row["stable_candidate_current"] and row["fragile_candidate_cyclic"]:
        return "cyclic_region_overstrict_warning"
    if row["stable_candidate_cyclic"]:
        return "stable_under_cyclic_region_candidate"
    if row["current_false_accept_warning"] and not row["exclusion_success_flag"]:
        return "cyclic_region_no_improvement_warning"
    if row["fragile_candidate_cyclic"]:
        return "fragile_under_cyclic_region"
    return "inconclusive"


def enrich_cases(
    rows: list[dict[str, Any]],
    config: dict[str, Any],
    input_consistency_passed: bool,
) -> list[dict[str, Any]]:
    thresholds = config["thresholds"]
    targets = config["targeted_driver_checks"]
    acceptance_threshold = to_float(thresholds["cyclic_acceptance_distance_threshold"])
    penalty_threshold = to_float(thresholds["penalty_gap_positive_threshold"])
    profile_distance_low = to_float(thresholds["profile_distance_low"])
    result: list[dict[str, Any]] = []
    for row in rows:
        profile_raw = to_float(row.get("profile_distance_raw"))
        profile_penalized = to_float(row.get("profile_distance_collision_penalized"))
        penalty_gap = max(profile_penalized - profile_raw, to_float(row.get("penalty_gap")))
        control_overlap_rate = to_float(row.get("control_overlap_rate"))
        decoy_success_rate = to_float(row.get("decoy_success_rate"))
        cyclic_distance, phase_source = cyclic_phase_distance(row)
        cyclic_distance_value = (
            0.45 * cyclic_distance
            + 0.35 * profile_raw
            + 0.10 * control_overlap_rate
            + 0.10 * decoy_success_rate
        )
        member = cyclic_distance_value <= acceptance_threshold
        stable_current = parse_bool(row.get("stable_candidate"))
        fragile_current = parse_bool(row.get("fragile_candidate"))
        current_false = current_false_accept(row)
        cyclic_false = member and fragile_current
        impostor_overlap = (
            member
            and row.get("decoy_family") != "exact_duplicate"
            and str(row.get("null_family", "")) != ""
        )
        spectrum_warning = (
            row.get("null_family") == targets["spectrum_matched_null_exclusion"] and member
        )
        adversarial_warning = (
            row.get("decoy_family") == targets["adversarial_near_duplicate_exclusion"]
            and member
        )
        local_warning = (
            row.get("profile_weight_set_id") == targets["local_response_dominant_exclusion"]
            and member
            and fragile_current
        )
        cosmetic_warning = penalty_gap > penalty_threshold and cyclic_false
        kernel8_warning = (
            row.get("kernel_size_label") == targets["kernel_size_8_artifact"]
            and cyclic_false
        )
        phase_wrap_warning = cyclic_distance <= to_float(
            thresholds["cyclic_phase_small"]
        ) and profile_raw > profile_distance_low
        current_warning_min = sum(
            [
                fragile_current,
                current_false,
                str(row.get("severity", "")).lower() == "high",
            ]
        )
        current_warning_count = max(to_int(row.get("major_warning_count")), current_warning_min)
        cyclic_warning_count = sum(
            [
                cyclic_false,
                impostor_overlap,
                spectrum_warning,
                adversarial_warning,
                local_warning,
                cosmetic_warning,
                kernel8_warning,
            ]
        )
        stable_cyclic = not any(
            [
                cyclic_false,
                impostor_overlap,
                spectrum_warning,
                adversarial_warning,
                local_warning,
                cosmetic_warning,
                kernel8_warning,
                phase_wrap_warning,
            ]
        )
        fragile_cyclic = not stable_cyclic
        exclusion_success = current_false and not member
        exclusion_failure = current_false and member
        warning_flags = [
            name
            for name, active in [
                ("current_false_accept_warning", current_false),
                ("cyclic_false_accept_warning", cyclic_false),
                ("impostor_overlap_warning", impostor_overlap),
                ("spectrum_matched_null_exclusion_warning", spectrum_warning),
                ("adversarial_near_duplicate_exclusion_warning", adversarial_warning),
                ("local_response_dominant_exclusion_warning", local_warning),
                ("cosmetic_penalty_lock_warning", cosmetic_warning),
                ("kernel_size_8_artifact_warning", kernel8_warning),
                ("phase_wrap_distance_warning", phase_wrap_warning),
                ("exclusion_success_flag", exclusion_success),
                ("exclusion_failure_flag", exclusion_failure),
            ]
            if active
        ]
        out = {
            "run_id": config["run_id"],
            "case_id": row.get("case_id", ""),
            "decoy_family": row.get("decoy_family", ""),
            "null_family": row.get("null_family", ""),
            "profile_weight_set_id": row.get("profile_weight_set_id", ""),
            "penalty_weight_set_id": row.get("penalty_weight_set_id", ""),
            "kernel_size_label": row.get("kernel_size_label", ""),
            "current_decision_table_label": row.get("decision_table_label", ""),
            "current_failure_mode_label": row.get("failure_mode_label", ""),
            "cyclic_phase_distance": cyclic_distance,
            "cyclic_phase_source": phase_source,
            "cyclic_phase_band": phase_band(cyclic_distance, thresholds),
            "cyclic_region_label": "inside_cyclic_region" if member else "outside_cyclic_region",
            "cylindrical_region_label": (
                f"{phase_band(cyclic_distance, thresholds)}_phase__"
                f"{'accepted' if member else 'excluded'}"
            ),
            "cyclic_linear_balance": cyclic_distance - profile_raw,
            "profile_distance_raw": profile_raw,
            "profile_distance_collision_penalized": profile_penalized,
            "penalty_gap": penalty_gap,
            "control_overlap_rate": control_overlap_rate,
            "decoy_success_rate": decoy_success_rate,
            "cyclic_acceptance_distance": cyclic_distance_value,
            "cyclic_acceptance_region_member": member,
            "current_false_accept_warning": current_false,
            "cyclic_false_accept_warning": cyclic_false,
            "impostor_overlap_warning": impostor_overlap,
            "spectrum_matched_null_exclusion_warning": spectrum_warning,
            "adversarial_near_duplicate_exclusion_warning": adversarial_warning,
            "local_response_dominant_exclusion_warning": local_warning,
            "cosmetic_penalty_lock_warning": cosmetic_warning,
            "kernel_size_8_artifact_warning": kernel8_warning,
            "phase_wrap_distance_warning": phase_wrap_warning,
            "stable_candidate_current": stable_current,
            "stable_candidate_cyclic": stable_cyclic,
            "fragile_candidate_current": fragile_current,
            "fragile_candidate_cyclic": fragile_cyclic,
            "warning_count_current": current_warning_count,
            "warning_count_cyclic": cyclic_warning_count,
            "warning_delta_current_to_cyclic": cyclic_warning_count - current_warning_count,
            "exclusion_success_flag": exclusion_success,
            "exclusion_failure_flag": exclusion_failure,
            "warning_flags": ";".join(warning_flags),
            "interpretation_note": (
                "Synthetic diagnostic cyclic-coordinate acceptance-region analysis only."
            ),
        }
        out["decision_status"] = decide_status(out, input_consistency_passed)
        result.append(out)
    return result


def count_bool(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if parse_bool(row.get(field)))


def mean_field(rows: list[dict[str, Any]], field: str) -> float:
    return safe_mean([to_float(row.get(field)) for row in rows])


def build_comparison_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    current_impostor_count = sum(
        1
        for row in rows
        if parse_bool(row["current_false_accept_warning"])
        or label_contains_any(
            f"{row['current_decision_table_label']} {row['current_failure_mode_label']}",
            ["impostor", "overlap"],
        )
    )
    metric_pairs = [
        (
            "stable_candidate_count",
            count_bool(rows, "stable_candidate_current"),
            count_bool(rows, "stable_candidate_cyclic"),
        ),
        (
            "fragile_candidate_count",
            count_bool(rows, "fragile_candidate_current"),
            count_bool(rows, "fragile_candidate_cyclic"),
        ),
        (
            "false_accept_warning_count",
            count_bool(rows, "current_false_accept_warning"),
            count_bool(rows, "cyclic_false_accept_warning"),
        ),
        (
            "impostor_overlap_warning_count",
            current_impostor_count,
            count_bool(rows, "impostor_overlap_warning"),
        ),
        (
            "spectrum_matched_null_intrusion_count",
            sum(
                1
                for row in rows
                if row["null_family"] == "spectrum_matched_null"
                and parse_bool(row["current_false_accept_warning"])
            ),
            count_bool(rows, "spectrum_matched_null_exclusion_warning"),
        ),
        (
            "adversarial_near_duplicate_intrusion_count",
            sum(
                1
                for row in rows
                if row["decoy_family"] == "adversarial_near_duplicate_sweep"
                and parse_bool(row["current_false_accept_warning"])
            ),
            count_bool(rows, "adversarial_near_duplicate_exclusion_warning"),
        ),
        (
            "local_response_dominant_warning_count",
            sum(
                1
                for row in rows
                if row["profile_weight_set_id"] == "local_response_dominant"
                and parse_bool(row["current_false_accept_warning"])
            ),
            count_bool(rows, "local_response_dominant_exclusion_warning"),
        ),
        (
            "cosmetic_penalty_lock_warning_count",
            sum(
                1
                for row in rows
                if to_float(row["penalty_gap"]) > 0
                and parse_bool(row["current_false_accept_warning"])
            ),
            count_bool(rows, "cosmetic_penalty_lock_warning"),
        ),
        (
            "kernel_size_8_artifact_warning_count",
            sum(
                1
                for row in rows
                if row["kernel_size_label"] == "kernel_size_8"
                and parse_bool(row["current_false_accept_warning"])
            ),
            count_bool(rows, "kernel_size_8_artifact_warning"),
        ),
        (
            "mean_warning_count",
            mean_field(rows, "warning_count_current"),
            mean_field(rows, "warning_count_cyclic"),
        ),
        (
            "mean_profile_distance_raw",
            mean_field(rows, "profile_distance_raw"),
            mean_field(rows, "profile_distance_raw"),
        ),
        (
            "mean_cyclic_acceptance_distance",
            "",
            mean_field(rows, "cyclic_acceptance_distance"),
        ),
    ]
    result = []
    for name, current_value, cyclic_value in metric_pairs:
        delta = (
            ""
            if current_value == ""
            else to_float(cyclic_value) - to_float(current_value)
        )
        result.append(
            {
                "metric_name": name,
                "current_value": current_value,
                "cyclic_value": cyclic_value,
                "delta_cyclic_minus_current": delta,
                "interpretation_note": (
                    "Current-vs-cyclic diagnostic comparison only; no proof claim."
                ),
            }
        )
    return result


def dominant_status(rows: list[dict[str, Any]]) -> str:
    counter = Counter(row["decision_status"] for row in rows)
    return counter.most_common(1)[0][0] if counter else ""


def build_impostor_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    axes: list[tuple[str, dict[str, list[dict[str, Any]]]]] = []
    for field, axis in [
        ("decoy_family", "decoy_family"),
        ("null_family", "null_family"),
    ]:
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            groups[str(row[field])].append(row)
        axes.append((axis, groups))
    combined: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        combined[f"{row['decoy_family']} | {row['null_family']}"].append(row)
    axes.append(("decoy_family x null_family", combined))

    result = []
    for axis, groups in axes:
        for value, group in sorted(groups.items()):
            success_count = count_bool(group, "exclusion_success_flag")
            failure_count = count_bool(group, "exclusion_failure_flag")
            row_count = len(group)
            result.append(
                {
                    "grouping_axis": axis,
                    "grouping_value": value,
                    "row_count": row_count,
                    "current_false_accept_warning_count": count_bool(
                        group, "current_false_accept_warning"
                    ),
                    "cyclic_false_accept_warning_count": count_bool(
                        group, "cyclic_false_accept_warning"
                    ),
                    "exclusion_success_count": success_count,
                    "exclusion_failure_count": failure_count,
                    "exclusion_success_rate": safe_rate(success_count, row_count),
                    "exclusion_failure_rate": safe_rate(failure_count, row_count),
                    "mean_cyclic_acceptance_distance": mean_field(
                        group, "cyclic_acceptance_distance"
                    ),
                    "dominant_decision_status": dominant_status(group),
                    "interpretation_note": (
                        "Impostor-exclusion grouping summary; diagnostic only."
                    ),
                }
            )
    return result


def status_severity(status: str) -> str:
    if status in {
        "spectrum_matched_null_intrusion_warning",
        "adversarial_near_duplicate_intrusion_warning",
        "cosmetic_penalty_lock_warning",
        "cyclic_false_accept_warning",
    }:
        return "high"
    if status in {
        "kernel_size_8_artifact_warning",
        "local_response_open_door_warning",
        "phase_wrap_distance_warning",
        "cyclic_region_no_improvement_warning",
        "cyclic_region_overstrict_warning",
        "fragile_under_cyclic_region",
    }:
        return "medium"
    return "low"


def build_decision_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["decision_status"]].append(row)
    result = []
    for status, group in sorted(groups.items()):
        severity = status_severity(status)
        row_count = len(group)
        result.append(
            {
                "decision_status": status,
                "row_count": row_count,
                "rate": safe_rate(row_count, len(rows)),
                "high_risk_count": row_count if severity == "high" else 0,
                "medium_risk_count": row_count if severity == "medium" else 0,
                "low_risk_count": row_count if severity == "low" else 0,
                "interpretation_note": (
                    "Cyclic decision table summary; methodological labels only."
                ),
            }
        )
    return result


def build_kernel_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[row["kernel_size_label"]].append(row)
    result = []
    for label, group in sorted(groups.items()):
        row_count = len(group)
        cyclic_false = count_bool(group, "cyclic_false_accept_warning")
        result.append(
            {
                "kernel_size_label": label,
                "row_count": row_count,
                "cyclic_false_accept_warning_count": cyclic_false,
                "cyclic_false_accept_warning_rate": safe_rate(cyclic_false, row_count),
                "kernel_size_8_artifact_warning_count": count_bool(
                    group, "kernel_size_8_artifact_warning"
                ),
                "mean_cyclic_acceptance_distance": mean_field(
                    group, "cyclic_acceptance_distance"
                ),
                "stable_candidate_cyclic_count": count_bool(
                    group, "stable_candidate_cyclic"
                ),
                "fragile_candidate_cyclic_count": count_bool(
                    group, "fragile_candidate_cyclic"
                ),
                "interpretation_note": (
                    "Kernel-size cyclic sensitivity is synthetic and methodological only."
                ),
            }
        )
    return result


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    status_lines = "\n".join(
        f"{key}: {json.dumps(value)}" for key, value in summary.items()
    )
    text = "\n".join(
        [
            "# QSB-ST-COMP01-D1h Cyclic-Coordinate Acceptance-Region Readout",
            "",
            "## Befund",
            "",
            "D1h is a synthetic diagnostic cyclic-coordinate acceptance-region analysis layer.",
            "",
            "D1h does not rerun D1f.",
            "",
            "D1h does not modify D1g outputs.",
            "",
            "D1h does not introduce a physical manifold.",
            "",
            "D1h does not introduce a new identity score.",
            "",
            f"`case_count`: {summary['case_count']}",
            f"`specificity_established`: {str(summary['specificity_established']).lower()}",
            f"`cyclic_phase_source`: {summary['cyclic_phase_source']}",
            f"`current_false_accept_warning_count`: {summary['current_false_accept_warning_count']}",
            f"`cyclic_false_accept_warning_count`: {summary['cyclic_false_accept_warning_count']}",
            f"`exclusion_success_count`: {summary['exclusion_success_count']}",
            f"`exclusion_failure_count`: {summary['exclusion_failure_count']}",
            f"`spectrum_matched_null_intrusion_count`: {summary['spectrum_matched_null_intrusion_count']}",
            f"`adversarial_near_duplicate_intrusion_count`: {summary['adversarial_near_duplicate_intrusion_count']}",
            f"`local_response_dominant_warning_count`: {summary['local_response_dominant_warning_count']}",
            f"`cosmetic_penalty_lock_warning_count`: {summary['cosmetic_penalty_lock_warning_count']}",
            f"`kernel_size_8_artifact_warning_count`: {summary['kernel_size_8_artifact_warning_count']}",
            "",
            "## Interpretation",
            "",
            "The cyclic-coordinate layer compares current D1g false-accept behavior with a diagnostic cyclic acceptance region. If raw phase fields are absent, `cyclic_phase_proxy` is diagnostic only.",
            "",
            "The targeted checks report `spectrum_matched_null`, `adversarial_near_duplicate_sweep`, `local_response_dominant`, `strong_collision_penalties`, and `kernel_size_8` behavior.",
            "",
            "## Hypothese",
            "",
            "A phase-aware cyclic acceptance model may help diagnose whether false-accept overlap is partly a geometry issue. This is a synthetic diagnostic hypothesis.",
            "",
            "## Offene Luecke",
            "",
            "- no real data",
            "- no physical validation",
            "- no diagnostic specificity established",
            "- no physical manifold",
            "- no Lorentzian metric",
            "- no physical time",
            "- no Pauli claim",
            "- no Bridge validation",
            "",
            "## Claim Boundary",
            "",
            "Cyclic-coordinate and cylindrical language is diagnostic only.",
            "",
            "This is not a physical manifold, not a Hilbert-space reconstruction, not a Lorentzian geometry, and not physical phase space.",
            "",
            "The analysis does not validate a physical Bridge and does not claim fermionic Pauli exclusion.",
            "",
            "## Machine-readable status",
            "",
            "```yaml",
            status_lines,
            "```",
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = read_config(Path(args.config))
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    input_files = config["input_files"]
    d1f_summary = json.loads(Path(input_files["d1f_summary"]).read_text(encoding="utf-8"))
    d1g_summary = json.loads(Path(input_files["d1g_summary"]).read_text(encoding="utf-8"))
    d1f_rows = read_csv_rows(Path(input_files["d1f_case_profile_summary"]))
    d1g_rows = read_csv_rows(Path(input_files["d1g_decision_table_case_classification"]))

    # Read the driver summaries to ensure declared inputs exist without altering them.
    for key in [
        "d1g_decoy_driver_summary",
        "d1g_null_family_driver_summary",
        "d1g_profile_weight_driver_summary",
        "d1g_penalty_weight_driver_summary",
        "d1g_kernel_size_driver_summary",
    ]:
        read_csv_rows(Path(input_files[key]))

    joined_rows, join_warnings = join_inputs(d1f_rows, d1g_rows)
    consistency_warnings = list(join_warnings)
    if len(joined_rows) != int(d1f_summary.get("case_count", -1)):
        consistency_warnings.append("joined row count differs from D1f summary")
    if len(joined_rows) != int(d1g_summary.get("case_count", -1)):
        consistency_warnings.append("joined row count differs from D1g summary")
    if parse_bool(d1f_summary.get("specificity_established")) or parse_bool(
        d1g_summary.get("specificity_established")
    ):
        consistency_warnings.append("upstream specificity_established is not false")
    input_consistency_passed = not consistency_warnings

    case_rows = enrich_cases(joined_rows, config, input_consistency_passed)
    comparison_rows = build_comparison_rows(case_rows)
    impostor_rows = build_impostor_rows(case_rows)
    decision_rows = build_decision_rows(case_rows)
    kernel_rows = build_kernel_rows(case_rows)

    generated_files = [
        "summary.json",
        "readout.md",
        "cyclic_region_case_summary.csv",
        "cyclic_vs_current_region_summary.csv",
        "impostor_exclusion_summary.csv",
        "decision_table_cyclic_summary.csv",
        "kernel_size_cyclic_sensitivity_summary.csv",
        "resolved_config.json",
    ]

    write_csv(output_dir / "cyclic_region_case_summary.csv", case_rows, CASE_FIELDS)
    write_csv(
        output_dir / "cyclic_vs_current_region_summary.csv",
        comparison_rows,
        COMPARISON_FIELDS,
    )
    write_csv(output_dir / "impostor_exclusion_summary.csv", impostor_rows, IMPOSTOR_FIELDS)
    write_csv(
        output_dir / "decision_table_cyclic_summary.csv",
        decision_rows,
        DECISION_FIELDS,
    )
    write_csv(
        output_dir / "kernel_size_cyclic_sensitivity_summary.csv",
        kernel_rows,
        KERNEL_FIELDS,
    )

    phase_sources = Counter(row["cyclic_phase_source"] for row in case_rows)
    cyclic_phase_source = (
        phase_sources.most_common(1)[0][0] if len(phase_sources) == 1 else "mixed_phase_or_proxy"
    )
    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "input_run_id_d1f": d1f_summary.get("run_id"),
        "input_run_id_d1g": d1g_summary.get("run_id"),
        "output_dir": config["output_dir"],
        "case_count": len(case_rows),
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1g_outputs": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "input_consistency_passed": input_consistency_passed,
        "input_consistency_warnings": consistency_warnings,
        "cyclic_phase_source": cyclic_phase_source,
        "cyclic_acceptance_region_member_count": count_bool(
            case_rows, "cyclic_acceptance_region_member"
        ),
        "cyclic_false_accept_warning_count": count_bool(
            case_rows, "cyclic_false_accept_warning"
        ),
        "current_false_accept_warning_count": count_bool(
            case_rows, "current_false_accept_warning"
        ),
        "impostor_overlap_warning_count": count_bool(
            case_rows, "impostor_overlap_warning"
        ),
        "spectrum_matched_null_intrusion_count": count_bool(
            case_rows, "spectrum_matched_null_exclusion_warning"
        ),
        "adversarial_near_duplicate_intrusion_count": count_bool(
            case_rows, "adversarial_near_duplicate_exclusion_warning"
        ),
        "local_response_dominant_warning_count": count_bool(
            case_rows, "local_response_dominant_exclusion_warning"
        ),
        "cosmetic_penalty_lock_warning_count": count_bool(
            case_rows, "cosmetic_penalty_lock_warning"
        ),
        "kernel_size_8_artifact_warning_count": count_bool(
            case_rows, "kernel_size_8_artifact_warning"
        ),
        "exclusion_success_count": count_bool(case_rows, "exclusion_success_flag"),
        "exclusion_failure_count": count_bool(case_rows, "exclusion_failure_flag"),
        "exclusion_success_rate": safe_rate(
            count_bool(case_rows, "exclusion_success_flag"),
            max(
                count_bool(case_rows, "exclusion_success_flag")
                + count_bool(case_rows, "exclusion_failure_flag"),
                1,
            ),
        ),
        "exclusion_failure_rate": safe_rate(
            count_bool(case_rows, "exclusion_failure_flag"),
            max(
                count_bool(case_rows, "exclusion_success_flag")
                + count_bool(case_rows, "exclusion_failure_flag"),
                1,
            ),
        ),
        "stable_candidate_current_count": count_bool(case_rows, "stable_candidate_current"),
        "fragile_candidate_current_count": count_bool(case_rows, "fragile_candidate_current"),
        "stable_candidate_cyclic_count": count_bool(case_rows, "stable_candidate_cyclic"),
        "fragile_candidate_cyclic_count": count_bool(case_rows, "fragile_candidate_cyclic"),
        "mean_cyclic_acceptance_distance": mean_field(
            case_rows, "cyclic_acceptance_distance"
        ),
        "mean_warning_count_current": mean_field(case_rows, "warning_count_current"),
        "mean_warning_count_cyclic": mean_field(case_rows, "warning_count_cyclic"),
        "mean_warning_delta_current_to_cyclic": mean_field(
            case_rows, "warning_delta_current_to_cyclic"
        ),
        "decision_status_counts": dict(
            sorted(Counter(row["decision_status"] for row in case_rows).items())
        ),
        "generated_files": generated_files,
        "claim_boundary": config["metadata"]["claim_boundary"],
    }

    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    write_readout(output_dir / "readout.md", summary)
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
