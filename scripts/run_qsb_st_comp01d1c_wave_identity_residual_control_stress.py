#!/usr/bin/env python3
"""QSB-ST-COMP01-D1c control-stress and weight-sensitivity runner.

The runner uses synthetic wave-pair definitions only. It extends the D1b
transparent residual calculation across multiple explicit weight sets and
harder synthetic controls.
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
except ImportError as exc:  # pragma: no cover - environment dependent
    raise SystemExit(
        "PyYAML is required for this scanner. Install PyYAML or run in the "
        "project environment where yaml is available."
    ) from exc


NON_CONTROL_FAMILIES = {
    "exact_duplicate",
    "simple_near_duplicate",
    "small_delta_k_decoy",
    "small_phase_drift_decoy",
    "amplitude_preserved_perturbation",
    "combined_near_duplicate_decoy",
}

NEAR_DUPLICATE_FAMILIES = {
    "simple_near_duplicate",
    "small_delta_k_decoy",
    "small_phase_drift_decoy",
    "amplitude_preserved_perturbation",
    "combined_near_duplicate_decoy",
}

PAIR_FIELDNAMES = [
    "weight_set_id",
    "spectral_weight",
    "phase_weight",
    "local_weight",
    "pair_id",
    "wave_id_i",
    "wave_id_j",
    "control_family",
    "control_seed",
    "k_i",
    "k_j",
    "delta_k",
    "relative_k_shift",
    "k_ratio",
    "phase_i",
    "phase_j",
    "relative_phase_drift",
    "phase_gradient_delta",
    "A_i",
    "A_j",
    "B_i",
    "B_j",
    "intercept_i",
    "intercept_j",
    "delta_intercept_ij",
    "intercept_similarity",
    "slope_i",
    "slope_j",
    "delta_slope_ij",
    "slope_similarity",
    "slope_intercept_balance",
    "local_linear_response_overlap",
    "spectral_component",
    "phase_component",
    "local_component",
    "spectral_identity_distance",
    "wave_identity_residual",
    "residual_rank_within_weight_set",
    "residual_shift_vs_equal_weights",
    "control_reference_ratio",
    "control_mimicry_warning",
    "residual_matched_warning",
    "weight_sensitivity_flag",
    "decision_status",
    "warning_flags",
    "interpretation_note",
]

CONTROL_FAMILY_FIELDNAMES = [
    "control_family",
    "weight_set_id",
    "pair_count",
    "min_wave_identity_residual",
    "max_wave_identity_residual",
    "mean_wave_identity_residual",
    "control_mimicry_warnings_count",
    "residual_matched_warnings_count",
    "weight_sensitivity_warnings_count",
    "decision_statuses",
    "warning_flags",
]

WEIGHT_SET_FIELDNAMES = [
    "weight_set_id",
    "spectral_weight",
    "phase_weight",
    "local_weight",
    "row_count",
    "min_wave_identity_residual",
    "max_wave_identity_residual",
    "mean_wave_identity_residual",
    "control_mimicry_warnings_count",
    "residual_matched_warnings_count",
    "weight_sensitivity_warnings_count",
    "exact_duplicate_sanity_passed",
]

DECISION_FIELDNAMES = [
    "decision_status",
    "count",
    "control_families",
    "weight_sets",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the QSB-ST-COMP01-D1c residual control-stress scanner."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1c_wave_identity_residual_control_stress_config.yaml",
        help="Path to the D1c YAML config.",
    )
    return parser.parse_args()


def read_config(config_path: Path) -> dict[str, Any]:
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise SystemExit(f"Config must be a YAML mapping: {config_path}")
    return config


def as_float(value: Any, warnings: list[str]) -> float:
    if value is None or value == "":
        warnings.append("missing_value")
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        warnings.append("missing_value")
        return math.nan


def finite_or_zero(value: float, warnings: list[str]) -> float:
    if math.isnan(value) or math.isinf(value):
        warnings.append("missing_value")
        return 0.0
    return value


def wrap_minus_pi_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def similarity_from_delta(delta: float, similarity_scale: float, epsilon: float, warnings: list[str]) -> float:
    scale = abs(similarity_scale)
    if scale <= epsilon:
        warnings.append("near_zero_denominator")
        scale = epsilon
    return 1.0 / (1.0 + abs(delta) / scale)


def normalized_fraction(value: float) -> float:
    return value / (1.0 + value)


def normalized_weights(weight_set: dict[str, Any]) -> tuple[dict[str, float], list[str]]:
    warnings: list[str] = []
    weights = {
        "spectral_component": float(weight_set.get("spectral_component", 0.0)),
        "phase_component": float(weight_set.get("phase_component", 0.0)),
        "local_component": float(weight_set.get("local_component", 0.0)),
    }
    weight_sum = sum(weights.values())
    if weight_sum <= 0.0:
        warnings.append("weight_sum_not_positive")
        return {
            "spectral_component": 1.0 / 3.0,
            "phase_component": 1.0 / 3.0,
            "local_component": 1.0 / 3.0,
        }, warnings
    return {key: value / weight_sum for key, value in weights.items()}, warnings


def compute_components(
    pair: dict[str, Any],
    epsilon: float,
    similarity_scale: float,
    warnings: list[str],
) -> dict[str, Any]:
    wave_i = pair.get("wave_i", {})
    wave_j = pair.get("wave_j", {})

    k_i = finite_or_zero(as_float(wave_i.get("k"), warnings), warnings)
    k_j = finite_or_zero(as_float(wave_j.get("k"), warnings), warnings)
    phase_i = finite_or_zero(as_float(wave_i.get("phase"), warnings), warnings)
    phase_j = finite_or_zero(as_float(wave_j.get("phase"), warnings), warnings)
    a_i = finite_or_zero(as_float(wave_i.get("A"), warnings), warnings)
    a_j = finite_or_zero(as_float(wave_j.get("A"), warnings), warnings)
    b_i = finite_or_zero(as_float(wave_i.get("B"), warnings), warnings)
    b_j = finite_or_zero(as_float(wave_j.get("B"), warnings), warnings)

    delta_k = abs(k_i - k_j)
    relative_k_shift = delta_k / max(abs(k_i), abs(k_j), epsilon)
    if abs(k_j) <= epsilon:
        k_ratio = None
        warnings.append("k_ratio_undefined")
    else:
        k_ratio = k_i / k_j

    phase_delta_raw = phase_i - phase_j
    phase_delta_wrapped = wrap_minus_pi_pi(phase_delta_raw)
    if abs(phase_delta_wrapped - phase_delta_raw) > epsilon:
        warnings.append("phase_wrapped")
    relative_phase_drift = abs(phase_delta_wrapped)
    phase_gradient_delta = abs((phase_i * k_i) - (phase_j * k_j))

    intercept_i = a_i
    intercept_j = a_j
    delta_intercept_ij = abs(intercept_i - intercept_j)
    slope_i = b_i * k_i
    slope_j = b_j * k_j
    delta_slope_ij = abs(slope_i - slope_j)

    intercept_similarity = similarity_from_delta(
        delta_intercept_ij, similarity_scale, epsilon, warnings
    )
    slope_similarity = similarity_from_delta(
        delta_slope_ij, similarity_scale, epsilon, warnings
    )
    slope_intercept_balance = abs(delta_slope_ij - delta_intercept_ij)
    local_linear_response_overlap = (intercept_similarity + slope_similarity) / 2.0

    spectral_component = relative_k_shift
    phase_component = (
        (relative_phase_drift / math.pi)
        + (phase_gradient_delta / (1.0 + phase_gradient_delta))
    ) / 2.0
    local_component = (
        normalized_fraction(delta_intercept_ij)
        + normalized_fraction(delta_slope_ij)
    ) / 2.0

    return {
        "wave_id_i": wave_i.get("wave_id", ""),
        "wave_id_j": wave_j.get("wave_id", ""),
        "k_i": k_i,
        "k_j": k_j,
        "delta_k": delta_k,
        "relative_k_shift": relative_k_shift,
        "k_ratio": k_ratio,
        "phase_i": phase_i,
        "phase_j": phase_j,
        "relative_phase_drift": relative_phase_drift,
        "phase_gradient_delta": phase_gradient_delta,
        "A_i": a_i,
        "A_j": a_j,
        "B_i": b_i,
        "B_j": b_j,
        "intercept_i": intercept_i,
        "intercept_j": intercept_j,
        "delta_intercept_ij": delta_intercept_ij,
        "intercept_similarity": intercept_similarity,
        "slope_i": slope_i,
        "slope_j": slope_j,
        "delta_slope_ij": delta_slope_ij,
        "slope_similarity": slope_similarity,
        "slope_intercept_balance": slope_intercept_balance,
        "local_linear_response_overlap": local_linear_response_overlap,
        "spectral_component": spectral_component,
        "phase_component": phase_component,
        "local_component": local_component,
        "spectral_identity_distance": spectral_component,
    }


def compute_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    normalization = config.get("normalization", {})
    epsilon = float(normalization.get("epsilon", 1.0e-12))
    similarity_scale = float(normalization.get("similarity_scale", 1.0))

    base_rows: list[dict[str, Any]] = []
    for weight_set in config.get("weight_sets", []):
        weight_set_id = str(weight_set.get("weight_set_id", ""))
        weights, weight_warnings = normalized_weights(weight_set)
        for pair in config.get("synthetic_wave_pairs", []):
            warnings = list(weight_warnings)
            components = compute_components(pair, epsilon, similarity_scale, warnings)
            residual = (
                weights["spectral_component"] * components["spectral_component"]
                + weights["phase_component"] * components["phase_component"]
                + weights["local_component"] * components["local_component"]
            )
            base_rows.append(
                {
                    "weight_set_id": weight_set_id,
                    "spectral_weight": weights["spectral_component"],
                    "phase_weight": weights["phase_component"],
                    "local_weight": weights["local_component"],
                    "pair_id": pair.get("pair_id", ""),
                    "control_family": pair.get("control_family", ""),
                    "control_seed": pair.get("control_seed", ""),
                    **components,
                    "wave_identity_residual": residual,
                    "residual_rank_within_weight_set": None,
                    "residual_shift_vs_equal_weights": None,
                    "control_reference_ratio": None,
                    "control_mimicry_warning": False,
                    "residual_matched_warning": False,
                    "weight_sensitivity_flag": False,
                    "decision_status": "",
                    "warning_flags": warnings,
                    "interpretation_note": "",
                }
            )

    add_derived_fields(base_rows, config)
    return base_rows


def add_derived_fields(rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    thresholds = config.get("decision_thresholds", {})
    epsilon = float(config.get("normalization", {}).get("epsilon", 1.0e-12))
    near_zero_residual_max = float(thresholds.get("near_zero_residual_max", 1.0e-9))
    near_duplicate_residual_max = float(thresholds.get("near_duplicate_residual_max", 0.15))
    control_mimicry_ratio_warning = float(
        thresholds.get("control_mimicry_ratio_warning", 0.85)
    )
    residual_matched_delta_max = float(thresholds.get("residual_matched_delta_max", 0.02))
    weight_sensitivity_shift_warning = float(
        thresholds.get("weight_sensitivity_shift_warning", 0.10)
    )

    equal_residual_by_pair = {
        row["pair_id"]: row["wave_identity_residual"]
        for row in rows
        if row["weight_set_id"] == "equal_weights"
    }

    combined_reference_by_weight = {
        row["weight_set_id"]: row["wave_identity_residual"]
        for row in rows
        if row["control_family"] == "combined_near_duplicate_decoy"
    }

    rows_by_weight: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_weight[row["weight_set_id"]].append(row)

    for weight_set_id, weight_rows in rows_by_weight.items():
        sorted_rows = sorted(
            weight_rows,
            key=lambda item: (item["wave_identity_residual"], item["pair_id"]),
        )
        for rank, row in enumerate(sorted_rows, start=1):
            row["residual_rank_within_weight_set"] = rank

        non_control_residuals = [
            row["wave_identity_residual"]
            for row in weight_rows
            if row["control_family"] in NON_CONTROL_FAMILIES
        ]
        mean_non_control_residual = (
            mean(non_control_residuals) if non_control_residuals else 0.0
        )
        ratio_denominator = max(mean_non_control_residual, epsilon)

        for row in weight_rows:
            residual = row["wave_identity_residual"]
            equal_residual = equal_residual_by_pair.get(row["pair_id"])
            if equal_residual is None:
                row["warning_flags"].append("missing_value")
                residual_shift = None
            else:
                residual_shift = residual - equal_residual
            row["residual_shift_vs_equal_weights"] = residual_shift
            row["weight_sensitivity_flag"] = bool(
                residual_shift is not None
                and abs(residual_shift) >= weight_sensitivity_shift_warning
            )

            if row["control_family"] not in NON_CONTROL_FAMILIES:
                ratio = residual / ratio_denominator
                row["control_reference_ratio"] = ratio
                row["control_mimicry_warning"] = ratio >= control_mimicry_ratio_warning

            if row["control_family"] == "residual_matched_decoy":
                reference = combined_reference_by_weight.get(weight_set_id)
                if reference is None:
                    row["warning_flags"].append("residual_matched_reference_missing")
                else:
                    row["residual_matched_warning"] = (
                        abs(residual - reference) <= residual_matched_delta_max
                    )

            if row["control_mimicry_warning"]:
                row["warning_flags"].append("control_mimicry_warning")
            if row["residual_matched_warning"]:
                row["warning_flags"].append("residual_matched_warning")
            if row["weight_sensitivity_flag"]:
                row["warning_flags"].append("weight_sensitivity_flag")

            family = row["control_family"]
            if family == "exact_duplicate":
                if residual <= near_zero_residual_max:
                    row["decision_status"] = "duplicate_sanity_pass"
                    row["interpretation_note"] = "Exact duplicate remains near zero."
                else:
                    row["decision_status"] = "duplicate_sanity_fail"
                    row["interpretation_note"] = "Exact duplicate is not near zero."
            elif family == "residual_matched_decoy":
                if row["residual_matched_warning"]:
                    row["decision_status"] = "residual_matched_decoy_warning"
                    row["interpretation_note"] = "Residual-matched decoy is close to the configured reference."
                elif residual > near_zero_residual_max:
                    row["decision_status"] = "near_duplicate_decoy_detected"
                    row["interpretation_note"] = "Residual-matched decoy is detectable but not reference-matched."
                else:
                    row["decision_status"] = "inconclusive"
                    row["interpretation_note"] = "Residual-matched decoy is not separated from zero."
            elif family == "adversarial_near_duplicate":
                if residual <= near_duplicate_residual_max:
                    row["decision_status"] = "adversarial_decoy_warning"
                    row["interpretation_note"] = "Adversarial near-duplicate remains small enough to warn."
                else:
                    row["decision_status"] = "near_duplicate_decoy_detected"
                    row["interpretation_note"] = "Adversarial near-duplicate is detected."
            elif row["control_mimicry_warning"]:
                row["decision_status"] = "control_mimicry_warning"
                row["interpretation_note"] = "Control residual meets the mimicry warning ratio."
            elif row["weight_sensitivity_flag"]:
                row["decision_status"] = "weight_sensitive_residual_warning"
                row["interpretation_note"] = "Residual is sensitive to this weight set."
            elif family in NEAR_DUPLICATE_FAMILIES:
                if residual > near_zero_residual_max:
                    row["decision_status"] = "near_duplicate_decoy_detected"
                    row["interpretation_note"] = "Near-duplicate residual is non-zero."
                else:
                    row["decision_status"] = "inconclusive"
                    row["interpretation_note"] = "Near-duplicate residual is not separated from zero."
            else:
                row["decision_status"] = "inconclusive"
                row["interpretation_note"] = "No stronger diagnostic decision rule was triggered."

            row["warning_flags"] = sorted(set(row["warning_flags"]))


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return ""
        return f"{value:.12g}"
    if isinstance(value, list):
        return ";".join(str(item) for item in value)
    return str(value)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: format_value(row.get(field)) for field in fieldnames})


def build_control_family_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[(row["control_family"], row["weight_set_id"])].append(row)
    result = []
    for (control_family, weight_set_id), group_rows in sorted(grouped.items()):
        residuals = [row["wave_identity_residual"] for row in group_rows]
        warnings = sorted(
            {
                warning
                for row in group_rows
                for warning in row.get("warning_flags", [])
                if warning
            }
        )
        result.append(
            {
                "control_family": control_family,
                "weight_set_id": weight_set_id,
                "pair_count": len(group_rows),
                "min_wave_identity_residual": min(residuals),
                "max_wave_identity_residual": max(residuals),
                "mean_wave_identity_residual": mean(residuals),
                "control_mimicry_warnings_count": sum(
                    1 for row in group_rows if row["control_mimicry_warning"]
                ),
                "residual_matched_warnings_count": sum(
                    1 for row in group_rows if row["residual_matched_warning"]
                ),
                "weight_sensitivity_warnings_count": sum(
                    1 for row in group_rows if row["weight_sensitivity_flag"]
                ),
                "decision_statuses": ";".join(
                    sorted({row["decision_status"] for row in group_rows})
                ),
                "warning_flags": ";".join(warnings),
            }
        )
    return result


def build_weight_set_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["weight_set_id"]].append(row)
    result = []
    for weight_set_id, group_rows in sorted(grouped.items()):
        residuals = [row["wave_identity_residual"] for row in group_rows]
        exact_rows = [
            row for row in group_rows if row["control_family"] == "exact_duplicate"
        ]
        result.append(
            {
                "weight_set_id": weight_set_id,
                "spectral_weight": group_rows[0]["spectral_weight"],
                "phase_weight": group_rows[0]["phase_weight"],
                "local_weight": group_rows[0]["local_weight"],
                "row_count": len(group_rows),
                "min_wave_identity_residual": min(residuals),
                "max_wave_identity_residual": max(residuals),
                "mean_wave_identity_residual": mean(residuals),
                "control_mimicry_warnings_count": sum(
                    1 for row in group_rows if row["control_mimicry_warning"]
                ),
                "residual_matched_warnings_count": sum(
                    1 for row in group_rows if row["residual_matched_warning"]
                ),
                "weight_sensitivity_warnings_count": sum(
                    1 for row in group_rows if row["weight_sensitivity_flag"]
                ),
                "exact_duplicate_sanity_passed": bool(
                    exact_rows
                    and all(
                        row["decision_status"] == "duplicate_sanity_pass"
                        for row in exact_rows
                    )
                ),
            }
        )
    return result


def build_decision_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(row["decision_status"] for row in rows)
    families_by_status: dict[str, set[str]] = defaultdict(set)
    weights_by_status: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        status = row["decision_status"]
        families_by_status[status].add(row["control_family"])
        weights_by_status[status].add(row["weight_set_id"])
    return [
        {
            "decision_status": status,
            "count": counts[status],
            "control_families": ";".join(sorted(families_by_status[status])),
            "weight_sets": ";".join(sorted(weights_by_status[status])),
        }
        for status in sorted(counts)
    ]


def build_summary(
    config: dict[str, Any],
    rows: list[dict[str, Any]],
    generated_files: list[str],
) -> dict[str, Any]:
    residuals = [row["wave_identity_residual"] for row in rows]
    decision_counts = Counter(row["decision_status"] for row in rows)
    exact_rows = [row for row in rows if row["control_family"] == "exact_duplicate"]
    pair_count = len(config.get("synthetic_wave_pairs", []))
    weight_set_count = len(config.get("weight_sets", []))
    return {
        "block_id": config.get("block_id", "QSB-ST-COMP01D1C"),
        "run_id": config.get("run_id", "wave_identity_residual_control_stress_open"),
        "output_dir": config.get(
            "output_dir",
            "runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open",
        ),
        "pair_count": pair_count,
        "weight_set_count": weight_set_count,
        "row_count": len(rows),
        "expected_row_count": pair_count * weight_set_count,
        "control_families": sorted({row["control_family"] for row in rows}),
        "weight_sets": [weight["weight_set_id"] for weight in config.get("weight_sets", [])],
        "specificity_established": False,
        "stable_candidate_metrics": [],
        "claim_boundary": (
            "synthetic diagnostic control-stress and weight-sensitivity only; "
            "wave_identity_residual is a diagnostic residual, not a physical observable; "
            "no physical time, no Pauli claim, no Lorentzian metric, and no physical Bridge validation."
        ),
        "decision_status_counts": dict(sorted(decision_counts.items())),
        "control_mimicry_warnings_count": sum(
            1 for row in rows if row["control_mimicry_warning"]
        ),
        "residual_matched_warnings_count": sum(
            1 for row in rows if row["residual_matched_warning"]
        ),
        "weight_sensitivity_warnings_count": sum(
            1 for row in rows if row["weight_sensitivity_flag"]
        ),
        "exact_duplicate_sanity_passed_all_weight_sets": bool(
            exact_rows
            and all(row["decision_status"] == "duplicate_sanity_pass" for row in exact_rows)
        ),
        "min_wave_identity_residual": min(residuals) if residuals else None,
        "mean_wave_identity_residual": mean(residuals) if residuals else None,
        "max_wave_identity_residual": max(residuals) if residuals else None,
        "generated_files": generated_files,
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# QSB-ST-COMP01-D1c Wave Identity Residual Control-Stress Readout",
        "",
        "## Befund",
        "",
        "D1c is a synthetic diagnostic control-stress and weight-sensitivity run.",
        "",
        f"- pair_count: {summary['pair_count']}",
        f"- weight_set_count: {summary['weight_set_count']}",
        f"- row_count: {summary['row_count']}",
        f"- expected_row_count: {summary['expected_row_count']}",
        f"- specificity_established: {summary['specificity_established']}",
        f"- exact_duplicate_sanity_passed_all_weight_sets: {summary['exact_duplicate_sanity_passed_all_weight_sets']}",
        f"- control_mimicry_warnings_count: {summary['control_mimicry_warnings_count']}",
        f"- residual_matched_warnings_count: {summary['residual_matched_warnings_count']}",
        f"- weight_sensitivity_warnings_count: {summary['weight_sensitivity_warnings_count']}",
        f"- min_wave_identity_residual: {summary['min_wave_identity_residual']}",
        f"- mean_wave_identity_residual: {summary['mean_wave_identity_residual']}",
        f"- max_wave_identity_residual: {summary['max_wave_identity_residual']}",
        "",
        "## Interpretation",
        "",
        "The wave_identity_residual is a diagnostic residual, not a physical observable. "
        "This run checks whether the residual changes under explicit weight sets and "
        "whether synthetic controls produce mimicry warnings. The phase_gradient_delta "
        "field uses the same simple synthetic proxy rule as D1b: "
        "abs((phase_i * k_i) - (phase_j * k_j)).",
        "",
        "## Hypothese",
        "",
        "If later refinements keep exact duplicates near zero while reducing control mimicry "
        "under harder controls, the residual may remain useful as a diagnostic search axis.",
        "",
        "## Offene Lücke",
        "",
        "This run uses synthetic pairs only. It does not validate a physical Bridge. "
        "It does not make a Pauli claim. It does not derive a Lorentzian metric. "
        "It does not introduce physical time. It does not use real data.",
        "",
        "## Claim Boundary",
        "",
        "- psi is a diagnostic pattern object here, not automatically a physical wavefunction.",
        "- wave_identity_residual is a diagnostic distinguishability construct, not a physical observable by itself.",
        "- weight sensitivity is a methodological stress test, not a physical parameter fit.",
        "- control mimicry warnings are methodological warnings, not physical findings.",
        "- wave-Pauli is a heuristic internal analogy only.",
        "- It does not claim fermionic Pauli exclusion.",
        "- It does not invoke quantum spin-statistics.",
        "- It does not assert a physical exclusion principle.",
        "- type-like similarity is not the same as relational identity.",
        "- spectral shift is used here as a diagnostic analogy, not as cosmological redshift.",
        "- phase drift is used here as a structure-internal pattern marker, not as physical time delay.",
        "- tau is not physical time.",
        "- tau is not proper time.",
        "- tau is not a universal clock.",
        "- COMP01-D1c does not attach D(A,B).",
        "- COMP01-D1c does not construct S_rel2.",
        "- COMP01-D1c does not validate a physical Bridge.",
        "- COMP01-D1c does not establish diagnostic specificity.",
        "- This is synthetic diagnostic control-stress work only.",
        "",
        "## Machine-readable status",
        "",
        "```json",
        json.dumps(
            {
                "block_id": summary["block_id"],
                "run_id": summary["run_id"],
                "specificity_established": summary["specificity_established"],
                "exact_duplicate_sanity_passed_all_weight_sets": summary[
                    "exact_duplicate_sanity_passed_all_weight_sets"
                ],
                "control_mimicry_warnings_count": summary[
                    "control_mimicry_warnings_count"
                ],
                "residual_matched_warnings_count": summary[
                    "residual_matched_warnings_count"
                ],
                "weight_sensitivity_warnings_count": summary[
                    "weight_sensitivity_warnings_count"
                ],
            },
            indent=2,
            sort_keys=True,
        ),
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = read_config(config_path)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = compute_rows(config)
    control_family_rows = build_control_family_summary(rows)
    weight_set_rows = build_weight_set_summary(rows)
    decision_rows = build_decision_summary(rows)

    generated_files = [
        "summary.json",
        "readout.md",
        "pair_weight_sweep_summary.csv",
        "control_family_summary.csv",
        "weight_set_summary.csv",
        "decision_summary.csv",
        "resolved_config.json",
    ]
    summary = build_summary(config, rows, generated_files)

    write_csv(output_dir / "pair_weight_sweep_summary.csv", rows, PAIR_FIELDNAMES)
    write_csv(
        output_dir / "control_family_summary.csv",
        control_family_rows,
        CONTROL_FAMILY_FIELDNAMES,
    )
    write_csv(
        output_dir / "weight_set_summary.csv",
        weight_set_rows,
        WEIGHT_SET_FIELDNAMES,
    )
    write_csv(output_dir / "decision_summary.csv", decision_rows, DECISION_FIELDNAMES)
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / "readout.md", summary)

    print(
        "QSB-ST-COMP01D1C control-stress runner complete: "
        f"{summary['row_count']} rows, output_dir={output_dir}"
    )


if __name__ == "__main__":
    main()
