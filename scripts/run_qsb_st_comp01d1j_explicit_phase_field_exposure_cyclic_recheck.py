#!/usr/bin/env python3
"""QSB-ST-COMP01-D1j explicit phase-field exposure and cyclic recheck."""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter
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


INVENTORY_FIELDS = [
    "source_file",
    "source_type",
    "row_count",
    "phase_source_available",
    "detected_phase_columns",
    "proxy_phase_columns",
    "detected_phase_text_mentions",
    "phase_source_label",
    "phase_exposure_mode",
    "decision_status",
    "interpretation_note",
]

EXPOSURE_FIELDS = [
    "phase_source_label",
    "phase_exposure_mode",
    "explicit_phase_source_available",
    "explicit_phase_recheck_possible",
    "detected_phase_columns",
    "detected_proxy_phase_columns",
    "detected_phase_text_mentions",
    "deterministic_synthetic_phase_extension_needed",
    "decision_status",
    "interpretation_note",
]

RECHECK_FIELDS = [
    "recheck_mode",
    "baseline_cyclic_phase_source",
    "explicit_phase_source_available",
    "explicit_phase_recheck_possible",
    "false_accept_warning_count",
    "exclusion_success_rate",
    "exclusion_failure_rate",
    "stable_candidate_cyclic_count",
    "fragile_candidate_cyclic_count",
    "stable_candidate_loss_rate",
    "overstrictness_warning_count",
    "remaining_intrusion_warning_count",
    "spectrum_matched_null_intrusion_count",
    "adversarial_near_duplicate_intrusion_count",
    "kernel_size_8_artifact_warning_count",
    "decision_status",
    "interpretation_note",
]

COMPARISON_FIELDS = [
    "case_id",
    "baseline_cyclic_phase_source",
    "baseline_cyclic_phase_proxy_distance",
    "explicit_phase_cyclic_distance",
    "proxy_vs_explicit_phase_distance_delta",
    "false_accept_warning_proxy",
    "false_accept_warning_explicit",
    "exclusion_success_proxy",
    "exclusion_success_explicit",
    "stable_candidate_proxy",
    "stable_candidate_explicit",
    "fragile_candidate_proxy",
    "fragile_candidate_explicit",
    "decision_status",
    "interpretation_note",
]

OVERSTRICTNESS_FIELDS = [
    "metric_name",
    "baseline_proxy_value",
    "explicit_phase_value",
    "explicit_phase_recheck_possible",
    "decision_status",
    "interpretation_note",
]

INTRUSION_FIELDS = [
    "intrusion_group",
    "baseline_proxy_count",
    "explicit_phase_count",
    "explicit_phase_recheck_possible",
    "decision_status",
    "interpretation_note",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D1j explicit phase-field exposure and cyclic geometry recheck."
    )
    parser.add_argument(
        "--config",
        default=(
            "data/qsb_st_comp01d1j_explicit_phase_field_exposure_cyclic_recheck_config.yaml"
        ),
    )
    return parser.parse_args()


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a mapping: {path}")
    return data


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_csv_header(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


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


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fieldnames})


def bool_from_csv(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    return float(value)


def wrap_minus_pi_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def path_type(name: str) -> str:
    if name.endswith("_summary"):
        return "json_summary"
    if name.endswith("_readout"):
        return "readout"
    if name.endswith("_cases") or name.endswith("_profiles"):
        return "case_csv"
    if "comparison" in name:
        return "comparison_csv"
    if name.endswith("_config"):
        return "config_text"
    if name.endswith("_runner"):
        return "generator_script_text"
    if name.endswith("_doc"):
        return "plan_doc"
    return "source"


def source_columns(path: Path) -> tuple[int | None, list[str]]:
    if path.suffix == ".csv":
        rows = read_csv_rows(path)
        return len(rows), list(rows[0].keys()) if rows else read_csv_header(path)
    return None, []


def text_mentions(path: Path, terms: list[str]) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [term for term in terms if term in text]


def inspect_sources(config: dict[str, Any]) -> list[dict[str, Any]]:
    phase_terms = list(config["phase_like_fields_to_search"])
    text_terms = list(dict.fromkeys(phase_terms + config.get("text_hint_terms", [])))
    explicit_names = set()
    for pair in config["explicit_phase_column_sets"]:
        explicit_names.add(pair["item_i"])
        explicit_names.add(pair["item_j"])
    explicit_names.update(config["explicit_distance_columns"])
    explicit_names.discard("cyclic_phase_distance")
    explicit_names.discard("cyclic_phase_source")
    explicit_names.discard("cyclic_phase_proxy")
    proxy_names = set(config["proxy_phase_columns"])

    rows: list[dict[str, Any]] = []
    for key, raw_path in config["input_files"].items():
        path = Path(raw_path)
        row_count, columns = source_columns(path)
        detected_explicit_columns = [name for name in columns if name in explicit_names]
        detected_proxy_columns = [name for name in columns if name in proxy_names]
        mentions = text_mentions(path, text_terms)
        rows.append(
            {
                "source_file": str(path),
                "source_type": path_type(key),
                "row_count": row_count,
                "phase_source_available": bool(detected_explicit_columns),
                "detected_phase_columns": detected_explicit_columns,
                "proxy_phase_columns": detected_proxy_columns,
                "detected_phase_text_mentions": mentions,
                "phase_source_label": (
                    "explicit_phase_like_columns"
                    if detected_explicit_columns
                    else "cyclic_phase_proxy_or_text_hint_only"
                    if detected_proxy_columns or mentions
                    else "none_detected"
                ),
                "phase_exposure_mode": (
                    "existing_generator_phase"
                    if detected_explicit_columns
                    else "unavailable_proxy_only"
                ),
                "decision_status": (
                    "explicit_phase_source_available_candidate"
                    if detected_explicit_columns
                    else "explicit_phase_source_missing_warning"
                ),
                "interpretation_note": (
                    "Source inspection only; explicit synthetic phase columns are diagnostic only."
                    if detected_explicit_columns
                    else "No explicit emitted phase columns found in this source."
                ),
            }
        )
    return rows


def aggregate_inventory(inventory_rows: list[dict[str, Any]]) -> dict[str, Any]:
    detected_phase_columns: list[str] = []
    detected_proxy_columns: list[str] = []
    detected_text_mentions: list[str] = []
    for row in inventory_rows:
        detected_phase_columns.extend(row["detected_phase_columns"])
        detected_proxy_columns.extend(row["proxy_phase_columns"])
        detected_text_mentions.extend(row["detected_phase_text_mentions"])
    return {
        "detected_phase_columns": sorted(set(detected_phase_columns)),
        "detected_proxy_phase_columns": sorted(set(detected_proxy_columns)),
        "detected_phase_text_mentions": sorted(set(detected_text_mentions)),
    }


def explicit_phase_pair(config: dict[str, Any], columns: set[str]) -> tuple[str, str, str] | None:
    for pair in config["explicit_phase_column_sets"]:
        item_i = pair["item_i"]
        item_j = pair["item_j"]
        if item_i in columns and item_j in columns:
            return pair["label"], item_i, item_j
    return None


def compute_explicit_case_rows(
    config: dict[str, Any],
    d1h_rows: list[dict[str, str]],
    candidate_rows: list[dict[str, str]],
    candidate_columns: set[str],
) -> list[dict[str, Any]]:
    pair = explicit_phase_pair(config, candidate_columns)
    if pair is None:
        return []

    _label, item_i, item_j = pair
    threshold = float(config["recheck_thresholds"]["normalized_angular_acceptance_distance_max"])
    candidate_by_case = {row["case_id"]: row for row in candidate_rows if row.get("case_id")}
    rows: list[dict[str, Any]] = []
    for d1h_row in d1h_rows:
        case_id = d1h_row["case_id"]
        source_row = candidate_by_case.get(case_id)
        if not source_row:
            continue
        phi_i = float(source_row[item_i])
        phi_j = float(source_row[item_j])
        delta = phi_i - phi_j
        delta_wrapped = wrap_minus_pi_pi(delta)
        distance = abs(delta_wrapped) / math.pi
        explicit_stable = distance <= threshold
        explicit_fragile = not explicit_stable
        proxy_distance = float_or_none(d1h_row.get("cyclic_phase_distance"))
        proxy_stable = bool_from_csv(d1h_row.get("stable_candidate_cyclic"))
        proxy_fragile = bool_from_csv(d1h_row.get("fragile_candidate_cyclic"))
        proxy_false_accept = bool_from_csv(d1h_row.get("cyclic_false_accept_warning"))
        explicit_false_accept = bool_from_csv(d1h_row.get("current_false_accept_warning")) and not explicit_stable
        proxy_exclusion_success = bool_from_csv(d1h_row.get("exclusion_success_flag"))
        explicit_exclusion_success = bool_from_csv(d1h_row.get("current_false_accept_warning")) and explicit_stable
        rows.append(
            {
                "case_id": case_id,
                "baseline_cyclic_phase_source": d1h_row.get("cyclic_phase_source", ""),
                "baseline_cyclic_phase_proxy_distance": proxy_distance,
                "explicit_phase_cyclic_distance": distance,
                "proxy_vs_explicit_phase_distance_delta": (
                    None if proxy_distance is None else distance - proxy_distance
                ),
                "false_accept_warning_proxy": proxy_false_accept,
                "false_accept_warning_explicit": explicit_false_accept,
                "exclusion_success_proxy": proxy_exclusion_success,
                "exclusion_success_explicit": explicit_exclusion_success,
                "stable_candidate_proxy": proxy_stable,
                "stable_candidate_explicit": explicit_stable,
                "fragile_candidate_proxy": proxy_fragile,
                "fragile_candidate_explicit": explicit_fragile,
                "decision_status": "explicit_phase_geometry_recheck_candidate",
                "interpretation_note": (
                    "Explicit phase-like diagnostic comparison only; no physical phase claim."
                ),
            }
        )
    return rows


def comparison_placeholder(d1h_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    row = d1h_rows[0]
    return [
        {
            "case_id": row["case_id"],
            "baseline_cyclic_phase_source": row.get("cyclic_phase_source", "cyclic_phase_proxy"),
            "baseline_cyclic_phase_proxy_distance": row.get("cyclic_phase_distance", ""),
            "explicit_phase_cyclic_distance": None,
            "proxy_vs_explicit_phase_distance_delta": None,
            "false_accept_warning_proxy": bool_from_csv(row.get("cyclic_false_accept_warning")),
            "false_accept_warning_explicit": None,
            "exclusion_success_proxy": bool_from_csv(row.get("exclusion_success_flag")),
            "exclusion_success_explicit": None,
            "stable_candidate_proxy": bool_from_csv(row.get("stable_candidate_cyclic")),
            "stable_candidate_explicit": None,
            "fragile_candidate_proxy": bool_from_csv(row.get("fragile_candidate_cyclic")),
            "fragile_candidate_explicit": None,
            "decision_status": "proxy_vs_explicit_phase_comparison_not_possible",
            "interpretation_note": "Explicit phase source missing; no proxy-vs-explicit case comparison performed.",
        }
    ]


def count_true(rows: list[dict[str, Any]], field: str) -> int:
    return sum(1 for row in rows if bool_from_csv(row.get(field)))


def mean_bool(rows: list[dict[str, Any]], field: str) -> float | None:
    if not rows:
        return None
    return mean(1.0 if bool_from_csv(row.get(field)) else 0.0 for row in rows)


def build_recheck_rows(
    d1h_summary: dict[str, Any],
    d1i_summary: dict[str, Any],
    explicit_source_available: bool,
    explicit_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not explicit_source_available:
        return [
            {
                "recheck_mode": "baseline_proxy_recheck",
                "baseline_cyclic_phase_source": d1h_summary["cyclic_phase_source"],
                "explicit_phase_source_available": False,
                "explicit_phase_recheck_possible": False,
                "false_accept_warning_count": d1h_summary["cyclic_false_accept_warning_count"],
                "exclusion_success_rate": d1h_summary["exclusion_success_rate"],
                "exclusion_failure_rate": d1h_summary["exclusion_failure_rate"],
                "stable_candidate_cyclic_count": d1h_summary["stable_candidate_cyclic_count"],
                "fragile_candidate_cyclic_count": d1h_summary["fragile_candidate_cyclic_count"],
                "stable_candidate_loss_rate": None,
                "overstrictness_warning_count": d1i_summary["overstrictness_warning_count"],
                "remaining_intrusion_warning_count": d1i_summary["remaining_intrusion_warning_count"],
                "spectrum_matched_null_intrusion_count": d1h_summary[
                    "spectrum_matched_null_intrusion_count"
                ],
                "adversarial_near_duplicate_intrusion_count": d1h_summary[
                    "adversarial_near_duplicate_intrusion_count"
                ],
                "kernel_size_8_artifact_warning_count": d1h_summary[
                    "kernel_size_8_artifact_warning_count"
                ],
                "decision_status": "baseline_proxy_only",
                "interpretation_note": "D1h proxy baseline retained for comparison; explicit recheck not possible.",
            },
            {
                "recheck_mode": "explicit_phase_recheck",
                "baseline_cyclic_phase_source": d1h_summary["cyclic_phase_source"],
                "explicit_phase_source_available": False,
                "explicit_phase_recheck_possible": False,
                "false_accept_warning_count": None,
                "exclusion_success_rate": None,
                "exclusion_failure_rate": None,
                "stable_candidate_cyclic_count": None,
                "fragile_candidate_cyclic_count": None,
                "stable_candidate_loss_rate": None,
                "overstrictness_warning_count": None,
                "remaining_intrusion_warning_count": None,
                "spectrum_matched_null_intrusion_count": None,
                "adversarial_near_duplicate_intrusion_count": None,
                "kernel_size_8_artifact_warning_count": None,
                "decision_status": "explicit_phase_source_missing_warning",
                "interpretation_note": "Explicit phase source missing; no explicit-phase cyclic geometry recheck.",
            },
            {
                "recheck_mode": "cos_sin_embedding_recheck",
                "baseline_cyclic_phase_source": d1h_summary["cyclic_phase_source"],
                "explicit_phase_source_available": False,
                "explicit_phase_recheck_possible": False,
                "false_accept_warning_count": None,
                "exclusion_success_rate": None,
                "exclusion_failure_rate": None,
                "stable_candidate_cyclic_count": None,
                "fragile_candidate_cyclic_count": None,
                "stable_candidate_loss_rate": None,
                "overstrictness_warning_count": None,
                "remaining_intrusion_warning_count": None,
                "spectrum_matched_null_intrusion_count": None,
                "adversarial_near_duplicate_intrusion_count": None,
                "kernel_size_8_artifact_warning_count": None,
                "decision_status": "explicit_phase_source_missing_warning",
                "interpretation_note": "Cos/sin embedding requires explicit phase-like fields.",
            },
            {
                "recheck_mode": "wrapped_scalar_recheck",
                "baseline_cyclic_phase_source": d1h_summary["cyclic_phase_source"],
                "explicit_phase_source_available": False,
                "explicit_phase_recheck_possible": False,
                "false_accept_warning_count": None,
                "exclusion_success_rate": None,
                "exclusion_failure_rate": None,
                "stable_candidate_cyclic_count": None,
                "fragile_candidate_cyclic_count": None,
                "stable_candidate_loss_rate": None,
                "overstrictness_warning_count": None,
                "remaining_intrusion_warning_count": None,
                "spectrum_matched_null_intrusion_count": None,
                "adversarial_near_duplicate_intrusion_count": None,
                "kernel_size_8_artifact_warning_count": None,
                "decision_status": "explicit_phase_source_missing_warning",
                "interpretation_note": "Wrapped scalar recheck requires explicit phase-like fields.",
            },
        ]

    false_accept_count = count_true(explicit_rows, "false_accept_warning_explicit")
    stable_count = count_true(explicit_rows, "stable_candidate_explicit")
    fragile_count = count_true(explicit_rows, "fragile_candidate_explicit")
    exclusion_success_rate = mean_bool(explicit_rows, "exclusion_success_explicit")
    exclusion_failure_rate = None if exclusion_success_rate is None else 1.0 - exclusion_success_rate
    proxy_stable_count = count_true(explicit_rows, "stable_candidate_proxy")
    stable_loss_count = sum(
        1
        for row in explicit_rows
        if bool_from_csv(row.get("stable_candidate_proxy"))
        and not bool_from_csv(row.get("stable_candidate_explicit"))
    )
    stable_loss_rate = None if proxy_stable_count == 0 else stable_loss_count / proxy_stable_count
    return [
        {
            "recheck_mode": "explicit_phase_recheck",
            "baseline_cyclic_phase_source": d1h_summary["cyclic_phase_source"],
            "explicit_phase_source_available": True,
            "explicit_phase_recheck_possible": True,
            "false_accept_warning_count": false_accept_count,
            "exclusion_success_rate": exclusion_success_rate,
            "exclusion_failure_rate": exclusion_failure_rate,
            "stable_candidate_cyclic_count": stable_count,
            "fragile_candidate_cyclic_count": fragile_count,
            "stable_candidate_loss_rate": stable_loss_rate,
            "overstrictness_warning_count": int(
                stable_loss_rate is not None
                and stable_loss_rate
                > float(d1i_summary.get("mean_stable_candidate_loss_rate", 0.0))
            ),
            "remaining_intrusion_warning_count": None,
            "spectrum_matched_null_intrusion_count": None,
            "adversarial_near_duplicate_intrusion_count": None,
            "kernel_size_8_artifact_warning_count": None,
            "decision_status": "explicit_phase_geometry_recheck_candidate",
            "interpretation_note": "Explicit phase-like diagnostic recheck only; no physical phase claim.",
        }
    ]


def build_overstrictness_rows(
    d1h_summary: dict[str, Any],
    d1i_summary: dict[str, Any],
    explicit_source_available: bool,
    explicit_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not explicit_source_available:
        return [
            {
                "metric_name": "stable_candidate_loss_rate_explicit",
                "baseline_proxy_value": d1i_summary["mean_stable_candidate_loss_rate"],
                "explicit_phase_value": None,
                "explicit_phase_recheck_possible": False,
                "decision_status": "explicit_phase_source_missing_warning",
                "interpretation_note": "Explicit overstrictness cannot be evaluated without explicit phase-like fields.",
            },
            {
                "metric_name": "explicit_phase_overstrictness_warning",
                "baseline_proxy_value": d1i_summary["overstrictness_warning_count"],
                "explicit_phase_value": None,
                "explicit_phase_recheck_possible": False,
                "decision_status": "explicit_phase_source_missing_warning",
                "interpretation_note": "D1i overstrictness remains the active audit anchor.",
            },
        ]
    proxy_stable = count_true(explicit_rows, "stable_candidate_proxy")
    lost_stable = sum(
        1
        for row in explicit_rows
        if bool_from_csv(row.get("stable_candidate_proxy"))
        and not bool_from_csv(row.get("stable_candidate_explicit"))
    )
    loss_rate = None if proxy_stable == 0 else lost_stable / proxy_stable
    warning_rate = float(d1i_summary.get("mean_stable_candidate_loss_rate", 0.0))
    warning = loss_rate is not None and loss_rate > warning_rate
    return [
        {
            "metric_name": "stable_candidate_loss_rate_explicit",
            "baseline_proxy_value": d1i_summary["mean_stable_candidate_loss_rate"],
            "explicit_phase_value": loss_rate,
            "explicit_phase_recheck_possible": True,
            "decision_status": (
                "explicit_phase_overstrictness_warning"
                if warning
                else "stable_retention_supported_candidate"
            ),
            "interpretation_note": "Stable retention diagnostic comparison only.",
        },
        {
            "metric_name": "explicit_phase_overstrictness_warning",
            "baseline_proxy_value": d1i_summary["overstrictness_warning_count"],
            "explicit_phase_value": int(warning),
            "explicit_phase_recheck_possible": True,
            "decision_status": (
                "explicit_phase_overstrictness_warning"
                if warning
                else "stable_retention_supported_candidate"
            ),
            "interpretation_note": "Overstrictness diagnostic comparison only.",
        },
    ]


def build_remaining_intrusion_rows(
    d1h_summary: dict[str, Any],
    d1h_rows: list[dict[str, str]],
    explicit_source_available: bool,
) -> list[dict[str, Any]]:
    baseline_counts = {
        "spectrum_matched_null": d1h_summary["spectrum_matched_null_intrusion_count"],
        "adversarial_near_duplicate_sweep": d1h_summary[
            "adversarial_near_duplicate_intrusion_count"
        ],
        "local_response_dominant": d1h_summary["local_response_dominant_warning_count"],
        "strong_collision_penalties": sum(
            1
            for row in d1h_rows
            if row.get("penalty_weight_set_id") == "strong_collision_penalties"
            and bool_from_csv(row.get("cyclic_false_accept_warning"))
        ),
        "kernel_size_8": d1h_summary["kernel_size_8_artifact_warning_count"],
        "impostor_overlap_warning": d1h_summary["impostor_overlap_warning_count"],
    }
    rows: list[dict[str, Any]] = []
    for name, baseline_count in baseline_counts.items():
        rows.append(
            {
                "intrusion_group": name,
                "baseline_proxy_count": baseline_count,
                "explicit_phase_count": None,
                "explicit_phase_recheck_possible": explicit_source_available,
                "decision_status": (
                    "explicit_phase_remaining_intrusion_recheck_pending"
                    if explicit_source_available
                    else "explicit_phase_source_missing_warning"
                ),
                "interpretation_note": (
                    "Remaining intrusion should be rechecked under explicit phase-like fields."
                    if explicit_source_available
                    else "Explicit phase source missing; baseline proxy intrusion count retained."
                ),
            }
        )
    return rows


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# QSB-ST-COMP01-D1j Explicit Phase-Field Exposure and Cyclic Geometry Recheck Readout",
        "",
        "## Befund",
        "",
        f"run_id: {summary['run_id']}",
        f"case_count: {summary['case_count']}",
        f"specificity_established: {str(summary['specificity_established']).lower()}",
        f"explicit_phase_source_available: {str(summary['explicit_phase_source_available']).lower()}",
        f"detected_phase_columns: {summary['detected_phase_columns']}",
        f"detected_phase_text_mentions: {summary['detected_phase_text_mentions']}",
        f"phase_source_label: {summary['phase_source_label']}",
        f"phase_exposure_mode: {summary['phase_exposure_mode']}",
        f"explicit_phase_recheck_possible: {str(summary['explicit_phase_recheck_possible']).lower()}",
        f"deterministic_synthetic_phase_extension_needed: {str(summary['deterministic_synthetic_phase_extension_needed']).lower()}",
        "",
        "D1j does not rerun D1f.",
        "D1j does not modify D1f, D1g, D1h, or D1i outputs.",
        "D1j does not introduce a physical phase.",
        "D1j does not introduce a physical manifold.",
        "D1j does not introduce a new identity score.",
        "D1j does not implement Mastermind.",
        "",
        "## Interpretation",
        "",
        (
            "No explicit emitted phase-like source fields were available in the inspected "
            "D1f/D1h outputs, so the cyclic geometry recheck cannot move beyond the D1h "
            "cyclic_phase_proxy baseline in this run."
            if not summary["explicit_phase_source_available"]
            else "Explicit emitted phase-like fields were available for diagnostic recheck."
        ),
        "",
        "The D1i finding explicit_phase_source_missing remains the active source-transparency anchor.",
        "",
        "## Hypothese",
        "",
        "A later explicit phase-field exposure layer may reduce proxy-dependence uncertainty if it emits transparent synthetic phase-like fields.",
        "",
        "## Offene Lücke",
        "",
        "- no real data",
        "- no diagnostic specificity established",
        "- no physical phase reconstruction",
        "- no physical manifold",
        "- no Lorentzian structure",
        "- no physical time",
        "- no Pauli claim",
        "- Mastermind remains parked",
        "",
        "## Claim Boundary",
        "",
        "cyclic_phase_proxy is diagnostic only.",
        "Explicit synthetic phase-like fields, if later exposed, are diagnostic synthetic fields.",
        "They are not physical phase reconstruction.",
        "Cyclic-coordinate and cylindrical language denotes a diagnostic coordinate model.",
        "It is not a physical spacetime manifold.",
        "It is not a Hilbert-space reconstruction.",
        "It is not a Lorentzian geometry.",
        "It is not a physical phase space.",
        "D1j does not establish diagnostic specificity.",
        "D1j does not claim fermionic Pauli exclusion.",
        "D1j does not invoke quantum spin-statistics.",
        "D1j does not derive a Lorentzian metric.",
        "D1j does not validate a physical Bridge.",
        "This is synthetic diagnostic explicit phase-field exposure and cyclic geometry recheck only.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = read_config(config_path)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = {key: Path(value) for key, value in config["input_files"].items()}
    d1f_summary = read_json(inputs["d1f_summary"])
    d1h_summary = read_json(inputs["d1h_summary"])
    d1i_summary = read_json(inputs["d1i_summary"])
    d1h_rows = read_csv_rows(inputs["d1h_cyclic_region_cases"])
    d1f_rows = read_csv_rows(inputs["d1f_case_profiles"])

    case_counts = {
        "d1f_summary": int(d1f_summary["case_count"]),
        "d1h_summary": int(d1h_summary["case_count"]),
        "d1i_summary": int(d1i_summary["case_count"]),
        "d1f_case_rows": len(d1f_rows),
        "d1h_case_rows": len(d1h_rows),
    }
    input_consistency_passed = len(set(case_counts.values())) == 1
    case_count = int(d1h_summary["case_count"])

    inventory_rows = inspect_sources(config)
    inventory = aggregate_inventory(inventory_rows)
    detected_phase_columns = inventory["detected_phase_columns"]
    detected_proxy_phase_columns = inventory["detected_proxy_phase_columns"]
    detected_phase_text_mentions = inventory["detected_phase_text_mentions"]
    explicit_source_available = bool(detected_phase_columns)

    d1h_columns = set(d1h_rows[0].keys()) if d1h_rows else set()
    d1f_columns = set(d1f_rows[0].keys()) if d1f_rows else set()
    explicit_rows = []
    if explicit_phase_pair(config, d1h_columns):
        explicit_rows = compute_explicit_case_rows(config, d1h_rows, d1h_rows, d1h_columns)
    elif explicit_phase_pair(config, d1f_columns):
        explicit_rows = compute_explicit_case_rows(config, d1h_rows, d1f_rows, d1f_columns)

    explicit_phase_recheck_possible = bool(explicit_rows)
    if explicit_source_available:
        phase_exposure_mode = "existing_generator_phase"
        phase_source_label = "explicit_phase_like_columns"
    elif detected_phase_text_mentions:
        phase_exposure_mode = "reconstructed_from_existing_synthetic_parameters_candidate"
        phase_source_label = "cyclic_phase_proxy_with_generator_phase_text_mentions"
    else:
        phase_exposure_mode = "unavailable_proxy_only"
        phase_source_label = "cyclic_phase_proxy_only"
    deterministic_extension_needed = not explicit_phase_recheck_possible

    if explicit_phase_recheck_possible:
        comparison_rows = explicit_rows
    else:
        comparison_rows = comparison_placeholder(d1h_rows)

    recheck_rows = build_recheck_rows(
        d1h_summary, d1i_summary, explicit_source_available, explicit_rows
    )
    overstrictness_rows = build_overstrictness_rows(
        d1h_summary, d1i_summary, explicit_source_available, explicit_rows
    )
    remaining_intrusion_rows = build_remaining_intrusion_rows(
        d1h_summary, d1h_rows, explicit_source_available
    )

    exposure_rows = [
        {
            "phase_source_label": phase_source_label,
            "phase_exposure_mode": phase_exposure_mode,
            "explicit_phase_source_available": explicit_source_available,
            "explicit_phase_recheck_possible": explicit_phase_recheck_possible,
            "detected_phase_columns": detected_phase_columns,
            "detected_proxy_phase_columns": detected_proxy_phase_columns,
            "detected_phase_text_mentions": detected_phase_text_mentions,
            "deterministic_synthetic_phase_extension_needed": deterministic_extension_needed,
            "decision_status": (
                "explicit_phase_source_available_candidate"
                if explicit_source_available
                else "explicit_phase_source_missing_warning"
            ),
            "interpretation_note": (
                "Explicit emitted phase-like fields available for diagnostic recheck."
                if explicit_source_available
                else "Explicit phase source missing; no fake phase generated."
            ),
        }
    ]

    generated_files = list(config["planned_outputs"])
    explicit_recheck_row = next(
        (row for row in recheck_rows if row["recheck_mode"] == "explicit_phase_recheck"),
        {},
    )
    baseline_proxy_false_accept = int(d1h_summary["cyclic_false_accept_warning_count"])
    explicit_false_accept = explicit_recheck_row.get("false_accept_warning_count")
    explicit_success_rate = explicit_recheck_row.get("exclusion_success_rate")
    explicit_stable_count = explicit_recheck_row.get("stable_candidate_cyclic_count")
    explicit_loss_rate = explicit_recheck_row.get("stable_candidate_loss_rate")

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "output_dir": config["output_dir"],
        "case_count": case_count,
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1f_outputs": True,
        "does_not_modify_d1g_outputs": True,
        "does_not_modify_d1h_outputs": True,
        "does_not_modify_d1i_outputs": True,
        "does_not_introduce_physical_phase": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "does_not_implement_mastermind": True,
        "mastermind_status": config["metadata"]["mastermind_status"],
        "input_consistency_passed": input_consistency_passed,
        "input_case_counts": case_counts,
        "baseline_cyclic_phase_source": d1h_summary["cyclic_phase_source"],
        "baseline_proxy_false_accept_warning_count": baseline_proxy_false_accept,
        "baseline_proxy_exclusion_success_rate": d1h_summary["exclusion_success_rate"],
        "baseline_proxy_stable_candidate_count": d1h_summary["stable_candidate_cyclic_count"],
        "explicit_phase_source_available": explicit_source_available,
        "detected_phase_columns": detected_phase_columns,
        "detected_proxy_phase_columns": detected_proxy_phase_columns,
        "detected_phase_text_mentions": detected_phase_text_mentions,
        "phase_source_label": phase_source_label,
        "phase_exposure_mode": phase_exposure_mode,
        "explicit_phase_recheck_possible": explicit_phase_recheck_possible,
        "deterministic_synthetic_phase_extension_needed": deterministic_extension_needed,
        "explicit_false_accept_warning_count": explicit_false_accept,
        "explicit_exclusion_success_rate": explicit_success_rate,
        "explicit_stable_candidate_count": explicit_stable_count,
        "explicit_stable_candidate_loss_rate": explicit_loss_rate,
        "phase_source_validation_status": (
            "explicit_phase_source_available"
            if explicit_source_available
            else "explicit_phase_source_missing"
        ),
        "phase_source_decision_status": (
            "explicit_phase_source_available_candidate"
            if explicit_source_available
            else "explicit_phase_source_missing_warning"
        ),
        "cyclic_geometry_recheck_decision_status": (
            "explicit_phase_geometry_recheck_candidate"
            if explicit_phase_recheck_possible
            else "explicit_phase_recheck_not_possible"
        ),
        "d1i_proxy_dependence_warning_count": d1i_summary["proxy_dependence_warning_count"],
        "d1i_threshold_sensitivity_warning_count": d1i_summary[
            "threshold_sensitivity_warning_count"
        ],
        "d1i_overstrictness_warning_count": d1i_summary["overstrictness_warning_count"],
        "d1i_remaining_intrusion_warning_count": d1i_summary[
            "remaining_intrusion_warning_count"
        ],
        "generated_files": generated_files,
        "claim_boundary": (
            "synthetic diagnostic explicit phase-field exposure and cyclic geometry recheck only"
        ),
    }

    write_csv(output_dir / "explicit_phase_source_inventory.csv", inventory_rows, INVENTORY_FIELDS)
    write_csv(output_dir / "phase_field_exposure_summary.csv", exposure_rows, EXPOSURE_FIELDS)
    write_csv(
        output_dir / "explicit_phase_cyclic_recheck_summary.csv",
        recheck_rows,
        RECHECK_FIELDS,
    )
    write_csv(
        output_dir / "proxy_vs_explicit_phase_comparison.csv",
        comparison_rows,
        COMPARISON_FIELDS,
    )
    write_csv(
        output_dir / "explicit_phase_overstrictness_summary.csv",
        overstrictness_rows,
        OVERSTRICTNESS_FIELDS,
    )
    write_csv(
        output_dir / "explicit_phase_remaining_intrusion_summary.csv",
        remaining_intrusion_rows,
        INTRUSION_FIELDS,
    )

    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / "readout.md", summary)

    status_counts = Counter(row["decision_status"] for row in recheck_rows)
    print(
        json.dumps(
            {
                "run_id": config["run_id"],
                "output_dir": config["output_dir"],
                "case_count": case_count,
                "explicit_phase_source_available": explicit_source_available,
                "explicit_phase_recheck_possible": explicit_phase_recheck_possible,
                "decision_status_counts": dict(sorted(status_counts.items())),
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
