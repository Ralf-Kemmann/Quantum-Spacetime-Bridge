#!/usr/bin/env python3
"""QSB-ST-COMP01-D1e synthetic collision-aware wave identity profile runner."""

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


RESIDUAL_PROFILE_ORDER = [
    "equal_weights",
    "spectral_dominant",
    "phase_dominant",
    "local_dominant",
    "spectral_off",
    "phase_off",
    "local_off",
]

PROFILE_PAIR_FIELDS = [
    "pair_id",
    "wave_id_i",
    "wave_id_j",
    "control_family",
    "coordinate_profile_vector",
    "angular_phase_profile_vector",
    "local_response_profile_vector",
    "residual_weight_profile_vector",
    "rank_stability_profile_vector",
    "collision_profile_vector",
    "control_response_profile_vector",
    "profile_distance_raw",
    "profile_distance_collision_penalized",
    "total_collision_penalty",
    "profile_collision",
    "residual_collision",
    "delta_vector_collision",
    "ambiguity_warning",
    "control_profile_mimicry_warning",
    "residual_matched_profile_warning",
    "adversarial_profile_warning",
    "near_duplicate_reference_max",
    "rank_shift_max",
    "rank_shift_mean",
    "decision_status",
    "warning_flags",
    "interpretation_note",
]

PROFILE_COMPONENT_FIELDS = [
    "pair_id",
    "component_name",
    "component_weight",
    "component_value",
    "component_vector",
    "interpretation_note",
]

COLLISION_PENALTY_FIELDS = [
    "pair_id",
    "control_family",
    "profile_collision_penalty",
    "residual_collision_penalty",
    "delta_vector_collision_penalty",
    "ambiguity_penalty",
    "control_mimicry_penalty",
    "residual_matched_penalty",
    "adversarial_penalty",
    "total_collision_penalty",
    "profile_distance_raw",
    "profile_distance_collision_penalized",
    "warning_flags",
]

CONTROL_RESPONSE_FIELDS = [
    "control_family",
    "pair_count",
    "min_profile_distance_raw",
    "max_profile_distance_raw",
    "mean_profile_distance_raw",
    "min_profile_distance_collision_penalized",
    "max_profile_distance_collision_penalized",
    "mean_profile_distance_collision_penalized",
    "control_profile_mimicry_warnings_count",
    "residual_matched_profile_warnings_count",
    "adversarial_profile_warnings_count",
    "collision_penalty_applied_count",
    "decision_statuses",
    "warning_flags",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D1e collision-aware wave identity profile diagnostic."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1e_collision_aware_wave_identity_profile_config.yaml",
    )
    return parser.parse_args()


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a mapping: {path}")
    return data


def wrap_minus_pi_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def as_float(value: Any, warnings: list[str]) -> float:
    if value is None or value == "":
        warnings.append("missing_value")
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        warnings.append("missing_value")
        return 0.0


def normalized_delta(value: float) -> float:
    return value / (1.0 + value)


def safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def euclidean_norm(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values))


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


def build_waves(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    epsilon = float(config["normalization"]["epsilon"])
    waves: dict[str, dict[str, Any]] = {}
    for wave in config["synthetic_waves"]:
        warnings: list[str] = []
        k = as_float(wave.get("k"), warnings)
        a = as_float(wave.get("A"), warnings)
        b = as_float(wave.get("B"), warnings)
        r = math.sqrt(a * a + b * b)
        phi_base = math.atan2(b, a)
        phi = as_float(wave.get("phase_override", phi_base), warnings)
        phi_wrapped = wrap_minus_pi_pi(phi)
        if abs(phi - phi_wrapped) > epsilon:
            warnings.append("phi_wrapped")
        slope = b * k
        intercept = a
        amplitude_balance = a - b
        denom = max(abs(a) + abs(b), epsilon)
        if denom <= epsilon:
            warnings.append("near_zero_denominator")
        normalized_amplitude_balance = amplitude_balance / denom
        local_response_norm = math.sqrt(intercept * intercept + slope * slope)
        waves[wave["wave_id"]] = {
            "wave_id": wave["wave_id"],
            "family": wave.get("family", ""),
            "k": k,
            "A": a,
            "B": b,
            "R": r,
            "phi": phi,
            "phi_wrapped": phi_wrapped,
            "slope": slope,
            "intercept": intercept,
            "amplitude_balance": amplitude_balance,
            "normalized_amplitude_balance": normalized_amplitude_balance,
            "local_response_norm": local_response_norm,
            "warning_flags": sorted(set(warnings)),
        }
    return waves


def residual_for_weight_set(
    pair: dict[str, Any],
    weight_set: dict[str, Any],
    epsilon: float,
) -> float:
    spectral_component = pair["delta_k"] / max(
        abs(pair["k_i"]), abs(pair["k_j"]), epsilon
    )
    phase_gradient_delta = abs((pair["phi_i"] * pair["k_i"]) - (pair["phi_j"] * pair["k_j"]))
    phase_component = safe_mean(
        [
            pair["wrapped_delta_phi_abs"] / math.pi,
            phase_gradient_delta / (1.0 + phase_gradient_delta),
        ]
    )
    local_component = safe_mean(
        [
            normalized_delta(pair["delta_intercept"]),
            normalized_delta(pair["delta_slope"]),
        ]
    )
    weights = [
        float(weight_set.get("spectral_component", 0.0)),
        float(weight_set.get("phase_component", 0.0)),
        float(weight_set.get("local_component", 0.0)),
    ]
    weight_sum = sum(weights)
    if weight_sum <= epsilon:
        return 0.0
    return (
        weights[0] * spectral_component
        + weights[1] * phase_component
        + weights[2] * local_component
    ) / weight_sum


def build_initial_pair_rows(
    config: dict[str, Any], waves: dict[str, dict[str, Any]]
) -> list[dict[str, Any]]:
    epsilon = float(config["normalization"]["epsilon"])
    rows: list[dict[str, Any]] = []
    for pair in config["pair_definitions"]:
        warnings: list[str] = []
        wave_i = waves.get(pair["wave_id_i"])
        wave_j = waves.get(pair["wave_id_j"])
        if wave_i is None or wave_j is None:
            warnings.append("missing_value")
            continue

        phi_delta = wrap_minus_pi_pi(wave_i["phi_wrapped"] - wave_j["phi_wrapped"])
        if abs((wave_i["phi_wrapped"] - wave_j["phi_wrapped"]) - phi_delta) > epsilon:
            warnings.append("phi_wrapped")
        delta_k = abs(wave_i["k"] - wave_j["k"])
        delta_r = abs(wave_i["R"] - wave_j["R"])
        delta_a = abs(wave_i["A"] - wave_j["A"])
        delta_b = abs(wave_i["B"] - wave_j["B"])
        delta_slope = abs(wave_i["slope"] - wave_j["slope"])
        delta_intercept = abs(wave_i["intercept"] - wave_j["intercept"])
        delta_balance = abs(
            wave_i["normalized_amplitude_balance"] - wave_j["normalized_amplitude_balance"]
        )
        local_response_norm_delta = abs(
            wave_i["local_response_norm"] - wave_j["local_response_norm"]
        )
        wrapped_delta_phi_abs = abs(phi_delta)
        coordinate_vector = [
            normalized_delta(delta_k),
            normalized_delta(delta_r),
            normalized_delta(delta_a),
            normalized_delta(delta_b),
            normalized_delta(delta_slope),
            normalized_delta(delta_intercept),
            normalized_delta(delta_balance),
            normalized_delta(local_response_norm_delta),
        ]
        angular_vector = [
            wrapped_delta_phi_abs / math.pi,
            1.0 - abs(math.cos(phi_delta)),
            abs(math.sin(phi_delta)),
        ]
        local_response_vector = [
            normalized_delta(delta_slope),
            normalized_delta(delta_intercept),
            normalized_delta(delta_balance),
            normalized_delta(local_response_norm_delta),
        ]
        row: dict[str, Any] = {
            "pair_id": pair["pair_id"],
            "wave_id_i": pair["wave_id_i"],
            "wave_id_j": pair["wave_id_j"],
            "control_family": pair["control_family"],
            "k_i": wave_i["k"],
            "k_j": wave_j["k"],
            "phi_i": wave_i["phi_wrapped"],
            "phi_j": wave_j["phi_wrapped"],
            "delta_k": delta_k,
            "delta_R": delta_r,
            "wrapped_delta_phi_abs": wrapped_delta_phi_abs,
            "cos_delta_phi": math.cos(phi_delta),
            "sin_delta_phi": math.sin(phi_delta),
            "delta_A": delta_a,
            "delta_B": delta_b,
            "delta_slope": delta_slope,
            "delta_intercept": delta_intercept,
            "delta_balance": delta_balance,
            "local_response_norm_delta": local_response_norm_delta,
            "coordinate_profile_vector": coordinate_vector,
            "angular_phase_profile_vector": angular_vector,
            "local_response_profile_vector": local_response_vector,
            "delta_vector_norm": euclidean_norm(
                [
                    delta_k,
                    delta_r,
                    wrapped_delta_phi_abs,
                    delta_a,
                    delta_b,
                    delta_slope,
                    delta_intercept,
                    delta_balance,
                    local_response_norm_delta,
                ]
            ),
            "warning_flags": sorted(set(warnings + wave_i["warning_flags"] + wave_j["warning_flags"])),
        }
        residuals = {
            weight_set["weight_set_id"]: residual_for_weight_set(row, weight_set, epsilon)
            for weight_set in config["weight_sets"]
        }
        row["residuals_by_weight"] = residuals
        row["residual_weight_profile_vector"] = [
            residuals[weight_set_id] for weight_set_id in RESIDUAL_PROFILE_ORDER
        ]
        rows.append(row)
    return rows


def add_rank_stability(rows: list[dict[str, Any]]) -> None:
    ranks_by_weight: dict[str, dict[str, int]] = {}
    for weight_set_id in RESIDUAL_PROFILE_ORDER:
        ordered = sorted(
            rows,
            key=lambda row: (row["residuals_by_weight"][weight_set_id], row["pair_id"]),
        )
        ranks_by_weight[weight_set_id] = {
            row["pair_id"]: index + 1 for index, row in enumerate(ordered)
        }

    pair_count = max(len(rows), 1)
    for row in rows:
        ranks = {
            weight_set_id: ranks_by_weight[weight_set_id][row["pair_id"]]
            for weight_set_id in RESIDUAL_PROFILE_ORDER
        }
        equal_rank = ranks["equal_weights"]
        shifts = [abs(rank - equal_rank) for rank in ranks.values()]
        row["residual_ranks_by_weight"] = ranks
        row["rank_shift_max"] = max(shifts)
        row["rank_shift_mean"] = safe_mean([float(shift) for shift in shifts])
        row["rank_stability_profile_vector"] = {
            "residual_rank_equal_weights": ranks["equal_weights"],
            "residual_rank_spectral_dominant": ranks["spectral_dominant"],
            "residual_rank_phase_dominant": ranks["phase_dominant"],
            "residual_rank_local_dominant": ranks["local_dominant"],
            "residual_rank_spectral_off": ranks["spectral_off"],
            "residual_rank_phase_off": ranks["phase_off"],
            "residual_rank_local_off": ranks["local_off"],
            "rank_shift_max": row["rank_shift_max"],
            "rank_shift_mean": row["rank_shift_mean"],
        }
        row["rank_stability_component"] = safe_mean(
            [float(shift) / pair_count for shift in shifts]
        )


def add_raw_profile_distance(rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    weights = config["profile_component_weights"]
    for row in rows:
        coordinate_component = safe_mean(row["coordinate_profile_vector"])
        angular_component = safe_mean(row["angular_phase_profile_vector"])
        local_response_component = safe_mean(row["local_response_profile_vector"])
        residual_component = safe_mean(
            [normalized_delta(value) for value in row["residual_weight_profile_vector"]]
        )
        rank_component = row["rank_stability_component"]
        collision_component = 0.0
        control_response_component = 0.0
        component_values = {
            "coordinate_profile": coordinate_component,
            "angular_phase_profile": angular_component,
            "local_response_profile": local_response_component,
            "residual_weight_profile": residual_component,
            "rank_stability_profile": rank_component,
            "collision_profile": collision_component,
            "control_response_profile": control_response_component,
        }
        row["component_values"] = component_values
        row["profile_distance_raw"] = sum(
            float(weights.get(component_name, 0.0)) * component_value
            for component_name, component_value in component_values.items()
        )


def residual_profiles_close(
    left: dict[str, Any], right: dict[str, Any], threshold: float
) -> bool:
    return all(
        abs(left["residuals_by_weight"][weight_id] - right["residuals_by_weight"][weight_id])
        <= threshold
        for weight_id in RESIDUAL_PROFILE_ORDER
    )


def delta_vectors_close(
    left: dict[str, Any], right: dict[str, Any], threshold: float
) -> bool:
    left_vector = [
        left["delta_k"],
        left["delta_R"],
        left["wrapped_delta_phi_abs"],
        left["delta_A"],
        left["delta_B"],
        left["delta_slope"],
        left["delta_intercept"],
        left["delta_balance"],
        left["local_response_norm_delta"],
    ]
    right_vector = [
        right["delta_k"],
        right["delta_R"],
        right["wrapped_delta_phi_abs"],
        right["delta_A"],
        right["delta_B"],
        right["delta_slope"],
        right["delta_intercept"],
        right["delta_balance"],
        right["local_response_norm_delta"],
    ]
    return euclidean_norm([l - r for l, r in zip(left_vector, right_vector)]) <= threshold


def add_collision_and_control_flags(rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    norm = config["normalization"]
    collision_threshold = float(norm["collision_distance_threshold"])
    residual_threshold = float(norm["residual_collision_threshold"])
    exact_family = config.get("audit", {}).get("exact_duplicate_family", "exact_duplicate")
    control_families = set(config.get("audit", {}).get("control_families", []))
    near_reference_families = set(
        config.get("audit", {}).get("near_duplicate_reference_families", [])
    )
    exact_rows = [row for row in rows if row["control_family"] == exact_family]
    exact_residuals = exact_rows[0]["residuals_by_weight"] if exact_rows else {}

    near_reference_values = [
        row["profile_distance_raw"]
        for row in rows
        if row["control_family"] in near_reference_families
    ]
    near_duplicate_reference_max = max(near_reference_values) if near_reference_values else 0.0

    residual_matched_reference = next(
        (row for row in rows if row["control_family"] == "combined_near_duplicate_decoy"),
        None,
    )

    for row in rows:
        is_exact = row["control_family"] == exact_family
        residual_matches_exact = False
        if exact_residuals:
            residual_matches_exact = any(
                abs(row["residuals_by_weight"][weight_id] - exact_residuals.get(weight_id, 0.0))
                <= residual_threshold
                for weight_id in RESIDUAL_PROFILE_ORDER
            )

        residual_matches_non_exact = any(
            row["pair_id"] != other["pair_id"]
            and other["control_family"] != exact_family
            and residual_profiles_close(row, other, residual_threshold)
            for other in rows
        )
        delta_matches_non_exact = any(
            row["pair_id"] != other["pair_id"]
            and other["control_family"] != exact_family
            and delta_vectors_close(row, other, collision_threshold)
            for other in rows
        )

        row["near_duplicate_reference_max"] = near_duplicate_reference_max
        row["profile_collision"] = (
            not is_exact and row["profile_distance_raw"] <= collision_threshold
        )
        row["residual_collision"] = (
            not is_exact and (residual_matches_exact or residual_matches_non_exact)
        )
        row["delta_vector_collision"] = (
            not is_exact
            and (row["delta_vector_norm"] <= collision_threshold or delta_matches_non_exact)
        )
        row["ambiguity_warning"] = any(
            [
                row["profile_collision"],
                row["residual_collision"],
                row["delta_vector_collision"],
            ]
        )
        row["control_profile_mimicry_warning"] = (
            row["control_family"] in control_families
            and row["profile_distance_raw"] <= near_duplicate_reference_max
        )
        row["residual_matched_profile_warning"] = False
        if row["control_family"] == "residual_matched_decoy":
            residual_match = False
            if residual_matched_reference is not None:
                residual_match = residual_profiles_close(
                    row, residual_matched_reference, residual_threshold
                )
            row["residual_matched_profile_warning"] = (
                residual_match or row["profile_distance_raw"] <= near_duplicate_reference_max
            )
        row["adversarial_profile_warning"] = False
        if row["control_family"] == "adversarial_near_duplicate":
            row["adversarial_profile_warning"] = (
                row["profile_distance_raw"] <= near_duplicate_reference_max
                or row["rank_shift_max"] <= 1
            )
        row["collision_profile_vector"] = {
            "profile_collision": row["profile_collision"],
            "residual_collision": row["residual_collision"],
            "delta_vector_collision": row["delta_vector_collision"],
            "ambiguity_warning": row["ambiguity_warning"],
        }
        row["control_response_profile_vector"] = {
            "control_profile_mimicry_warning": row["control_profile_mimicry_warning"],
            "residual_matched_profile_warning": row["residual_matched_profile_warning"],
            "adversarial_profile_warning": row["adversarial_profile_warning"],
            "near_duplicate_reference_max": near_duplicate_reference_max,
        }


def add_penalties_and_decisions(rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    penalty_weights = config["collision_penalty_weights"]
    exact_family = config.get("audit", {}).get("exact_duplicate_family", "exact_duplicate")
    collision_threshold = float(config["normalization"]["collision_distance_threshold"])

    for row in rows:
        row["profile_collision_penalty"] = (
            float(penalty_weights["profile_collision_penalty"])
            if row["profile_collision"]
            else 0.0
        )
        row["residual_collision_penalty"] = (
            float(penalty_weights["residual_collision_penalty"])
            if row["residual_collision"]
            else 0.0
        )
        row["delta_vector_collision_penalty"] = (
            float(penalty_weights["delta_vector_collision_penalty"])
            if row["delta_vector_collision"]
            else 0.0
        )
        row["ambiguity_penalty"] = (
            float(penalty_weights["ambiguity_penalty"])
            if row["ambiguity_warning"]
            else 0.0
        )
        row["control_mimicry_penalty"] = (
            float(penalty_weights["control_mimicry_penalty"])
            if row["control_profile_mimicry_warning"]
            else 0.0
        )
        row["residual_matched_penalty"] = (
            float(penalty_weights["residual_matched_penalty"])
            if row["residual_matched_profile_warning"]
            else 0.0
        )
        row["adversarial_penalty"] = (
            float(penalty_weights["adversarial_penalty"])
            if row["adversarial_profile_warning"]
            else 0.0
        )
        row["total_collision_penalty"] = sum(
            [
                row["profile_collision_penalty"],
                row["residual_collision_penalty"],
                row["delta_vector_collision_penalty"],
                row["ambiguity_penalty"],
                row["control_mimicry_penalty"],
                row["residual_matched_penalty"],
                row["adversarial_penalty"],
            ]
        )
        row["profile_distance_collision_penalized"] = (
            row["profile_distance_raw"] + row["total_collision_penalty"]
        )

        flags = list(row.get("warning_flags", []))
        if row["wrapped_delta_phi_abs"] > 0.0:
            flags.append("phi_wrapped")
        for flag_name in [
            "profile_collision",
            "residual_collision",
            "delta_vector_collision",
            "ambiguity_warning",
            "control_profile_mimicry_warning",
            "residual_matched_profile_warning",
            "adversarial_profile_warning",
        ]:
            if row[flag_name]:
                flags.append(flag_name)
        if row["total_collision_penalty"] > 0.0:
            flags.append("collision_penalty_applied")
        row["warning_flags"] = sorted(set(flags))

        if row["control_family"] == exact_family:
            row["decision_status"] = (
                "exact_duplicate_sanity_pass"
                if row["profile_distance_raw"] <= collision_threshold
                else "exact_duplicate_sanity_fail"
            )
        elif row["control_profile_mimicry_warning"]:
            row["decision_status"] = "control_profile_mimicry_warning"
        elif row["residual_matched_profile_warning"]:
            row["decision_status"] = "residual_matched_profile_warning"
        elif row["adversarial_profile_warning"]:
            row["decision_status"] = "adversarial_profile_warning"
        elif row["profile_collision"]:
            row["decision_status"] = "profile_collision_warning"
        elif row["residual_collision"]:
            row["decision_status"] = "residual_collision_warning"
        elif row["delta_vector_collision"]:
            row["decision_status"] = "delta_vector_collision_warning"
        elif row["total_collision_penalty"] > 0.0:
            row["decision_status"] = "collision_penalty_applied"
        else:
            row["decision_status"] = "profile_separation_candidate"
        row["interpretation_note"] = (
            "Synthetic diagnostic profile row; no physical identity or specificity claim."
        )


def build_component_rows(rows: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    weights = config["profile_component_weights"]
    component_rows: list[dict[str, Any]] = []
    for row in rows:
        component_vectors = {
            "coordinate_profile": row["coordinate_profile_vector"],
            "angular_phase_profile": row["angular_phase_profile_vector"],
            "local_response_profile": row["local_response_profile_vector"],
            "residual_weight_profile": row["residual_weight_profile_vector"],
            "rank_stability_profile": row["rank_stability_profile_vector"],
            "collision_profile": row["collision_profile_vector"],
            "control_response_profile": row["control_response_profile_vector"],
        }
        component_values = {
            **row["component_values"],
            "collision_profile": safe_mean(
                [1.0 if value else 0.0 for value in row["collision_profile_vector"].values()]
            ),
            "control_response_profile": safe_mean(
                [
                    1.0 if row["control_profile_mimicry_warning"] else 0.0,
                    1.0 if row["residual_matched_profile_warning"] else 0.0,
                    1.0 if row["adversarial_profile_warning"] else 0.0,
                ]
            ),
        }
        for component_name in [
            "coordinate_profile",
            "angular_phase_profile",
            "local_response_profile",
            "residual_weight_profile",
            "rank_stability_profile",
            "collision_profile",
            "control_response_profile",
        ]:
            component_rows.append(
                {
                    "pair_id": row["pair_id"],
                    "component_name": component_name,
                    "component_weight": float(weights.get(component_name, 0.0)),
                    "component_value": component_values[component_name],
                    "component_vector": component_vectors[component_name],
                    "interpretation_note": "Diagnostic component only.",
                }
            )
    return component_rows


def build_control_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["control_family"]].append(row)

    control_rows: list[dict[str, Any]] = []
    for family in sorted(grouped):
        family_rows = grouped[family]
        raw_values = [row["profile_distance_raw"] for row in family_rows]
        penalized_values = [
            row["profile_distance_collision_penalized"] for row in family_rows
        ]
        warning_flags = sorted(
            {flag for row in family_rows for flag in row.get("warning_flags", [])}
        )
        control_rows.append(
            {
                "control_family": family,
                "pair_count": len(family_rows),
                "min_profile_distance_raw": min(raw_values),
                "max_profile_distance_raw": max(raw_values),
                "mean_profile_distance_raw": mean(raw_values),
                "min_profile_distance_collision_penalized": min(penalized_values),
                "max_profile_distance_collision_penalized": max(penalized_values),
                "mean_profile_distance_collision_penalized": mean(penalized_values),
                "control_profile_mimicry_warnings_count": sum(
                    1 for row in family_rows if row["control_profile_mimicry_warning"]
                ),
                "residual_matched_profile_warnings_count": sum(
                    1 for row in family_rows if row["residual_matched_profile_warning"]
                ),
                "adversarial_profile_warnings_count": sum(
                    1 for row in family_rows if row["adversarial_profile_warning"]
                ),
                "collision_penalty_applied_count": sum(
                    1 for row in family_rows if row["total_collision_penalty"] > 0.0
                ),
                "decision_statuses": sorted(
                    {row["decision_status"] for row in family_rows}
                ),
                "warning_flags": warning_flags,
            }
        )
    return control_rows


def build_summary(rows: list[dict[str, Any]], config: dict[str, Any], generated_files: list[str]) -> dict[str, Any]:
    raw_values = [row["profile_distance_raw"] for row in rows]
    penalized_values = [row["profile_distance_collision_penalized"] for row in rows]
    decision_counts = Counter(row["decision_status"] for row in rows)
    exact_rows = [
        row
        for row in rows
        if row["control_family"] == config.get("audit", {}).get("exact_duplicate_family", "exact_duplicate")
    ]
    return {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "output_dir": config["output_dir"],
        "pair_count": len(rows),
        "specificity_established": False,
        "stable_candidate_metrics": [],
        "exact_duplicate_sanity_passed": all(
            row["decision_status"] == "exact_duplicate_sanity_pass" for row in exact_rows
        ),
        "profile_collision_count": sum(1 for row in rows if row["profile_collision"]),
        "residual_collision_count": sum(1 for row in rows if row["residual_collision"]),
        "delta_vector_collision_count": sum(1 for row in rows if row["delta_vector_collision"]),
        "ambiguity_warning_count": sum(1 for row in rows if row["ambiguity_warning"]),
        "control_profile_mimicry_warnings_count": sum(
            1 for row in rows if row["control_profile_mimicry_warning"]
        ),
        "residual_matched_profile_warnings_count": sum(
            1 for row in rows if row["residual_matched_profile_warning"]
        ),
        "adversarial_profile_warnings_count": sum(
            1 for row in rows if row["adversarial_profile_warning"]
        ),
        "collision_penalty_applied_count": sum(
            1 for row in rows if row["total_collision_penalty"] > 0.0
        ),
        "min_profile_distance_raw": min(raw_values) if raw_values else 0.0,
        "mean_profile_distance_raw": mean(raw_values) if raw_values else 0.0,
        "max_profile_distance_raw": max(raw_values) if raw_values else 0.0,
        "min_profile_distance_collision_penalized": min(penalized_values)
        if penalized_values
        else 0.0,
        "mean_profile_distance_collision_penalized": mean(penalized_values)
        if penalized_values
        else 0.0,
        "max_profile_distance_collision_penalized": max(penalized_values)
        if penalized_values
        else 0.0,
        "decision_status_counts": dict(sorted(decision_counts.items())),
        "generated_files": generated_files,
        "claim_boundary": config.get("metadata", {}).get(
            "claim_boundary", "synthetic diagnostic collision-aware profile only"
        ),
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    text = f"""# QSB-ST-COMP01-D1e Collision-Aware Wave Identity Profile Readout

## Befund

D1e is a synthetic diagnostic collision-aware profile run. It evaluated {summary["pair_count"]} configured synthetic wave pairs.

`specificity_established`: {str(summary["specificity_established"]).lower()}

`exact_duplicate_sanity_passed`: {str(summary["exact_duplicate_sanity_passed"]).lower()}

`profile_distance_raw`: min={summary["min_profile_distance_raw"]:.12g}, mean={summary["mean_profile_distance_raw"]:.12g}, max={summary["max_profile_distance_raw"]:.12g}

`profile_distance_collision_penalized`: min={summary["min_profile_distance_collision_penalized"]:.12g}, mean={summary["mean_profile_distance_collision_penalized"]:.12g}, max={summary["max_profile_distance_collision_penalized"]:.12g}

`control_profile_mimicry_warnings_count`: {summary["control_profile_mimicry_warnings_count"]}

`residual_matched_profile_warnings_count`: {summary["residual_matched_profile_warnings_count"]}

`adversarial_profile_warnings_count`: {summary["adversarial_profile_warnings_count"]}

`collision_penalty_applied_count`: {summary["collision_penalty_applied_count"]}

## Interpretation

The `wave_identity_profile` is a diagnostic profile, not a physical identity proof. The run reports raw profile distance together with collision-penalized distance so that collision, mimicry, residual-matched, and adversarial warnings remain visible.

The profile output does not validate a physical Bridge and does not establish diagnostic specificity.

## Hypothese

A collision-aware multi-component profile may be a better diagnostic search axis than a standalone residual when control response and collision penalties are reported beside the raw profile distance.

This remains a synthetic diagnostic hypothesis.

## Offene Lücke

- No real data.
- No physical validation.
- No diagnostic specificity is established.
- No physical manifold.
- No Lorentzian metric.
- No physical time.
- No physical wavefunction claim.
- No Pauli claim.
- No spin-statistics claim.
- No Bridge validation.

## Claim Boundary

The manifold language denotes a diagnostic coordinate space of synthetic wave-pattern descriptors.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

`psi` is a diagnostic pattern object here, not automatically a physical wavefunction.

`wave_identity_residual` is a diagnostic distinguishability construct, not a physical observable by itself.

`wave_identity_profile` is a diagnostic profile concept, not a proof of physical identity.

Collision-aware profile distance is a methodological diagnostic construct, not a physical distance.

Collision penalties are methodological warning terms, not physical forces or interactions.

Control mimicry warnings are methodological warnings, not failures of physics.

“wave-Pauli” is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

Type-like similarity is not the same as relational identity.

Spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

Phase drift is used here as a structure-internal pattern marker, not as physical time delay.

`tau` is not physical time.

`tau` is not proper time.

`tau` is not a universal clock.

COMP01-D1e does not attach `D(A,B)`.

COMP01-D1e does not construct `S_rel2`.

COMP01-D1e does not derive a Lorentzian metric.

COMP01-D1e does not validate a physical Bridge.

COMP01-D1e does not establish diagnostic specificity.

This is synthetic diagnostic collision-aware profile run output only.

## Machine-readable status

```yaml
block_id: {summary["block_id"]}
run_id: {summary["run_id"]}
pair_count: {summary["pair_count"]}
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed: {str(summary["exact_duplicate_sanity_passed"]).lower()}
profile_collision_count: {summary["profile_collision_count"]}
residual_collision_count: {summary["residual_collision_count"]}
delta_vector_collision_count: {summary["delta_vector_collision_count"]}
ambiguity_warning_count: {summary["ambiguity_warning_count"]}
control_profile_mimicry_warnings_count: {summary["control_profile_mimicry_warnings_count"]}
residual_matched_profile_warnings_count: {summary["residual_matched_profile_warnings_count"]}
adversarial_profile_warnings_count: {summary["adversarial_profile_warnings_count"]}
collision_penalty_applied_count: {summary["collision_penalty_applied_count"]}
min_profile_distance_raw: {summary["min_profile_distance_raw"]:.12g}
mean_profile_distance_raw: {summary["mean_profile_distance_raw"]:.12g}
max_profile_distance_raw: {summary["max_profile_distance_raw"]:.12g}
min_profile_distance_collision_penalized: {summary["min_profile_distance_collision_penalized"]:.12g}
mean_profile_distance_collision_penalized: {summary["mean_profile_distance_collision_penalized"]:.12g}
max_profile_distance_collision_penalized: {summary["max_profile_distance_collision_penalized"]:.12g}
```
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = read_config(config_path)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    waves = build_waves(config)
    pair_rows = build_initial_pair_rows(config, waves)
    add_rank_stability(pair_rows)
    add_raw_profile_distance(pair_rows, config)
    add_collision_and_control_flags(pair_rows, config)
    add_penalties_and_decisions(pair_rows, config)

    generated_files = [
        "summary.json",
        "readout.md",
        "profile_pair_summary.csv",
        "profile_component_summary.csv",
        "collision_penalty_summary.csv",
        "control_response_summary.csv",
        "resolved_config.json",
    ]

    component_rows = build_component_rows(pair_rows, config)
    control_rows = build_control_rows(pair_rows)
    summary = build_summary(pair_rows, config, generated_files)

    write_csv(output_dir / "profile_pair_summary.csv", pair_rows, PROFILE_PAIR_FIELDS)
    write_csv(
        output_dir / "profile_component_summary.csv",
        component_rows,
        PROFILE_COMPONENT_FIELDS,
    )
    write_csv(
        output_dir / "collision_penalty_summary.csv",
        pair_rows,
        COLLISION_PENALTY_FIELDS,
    )
    write_csv(
        output_dir / "control_response_summary.csv",
        control_rows,
        CONTROL_RESPONSE_FIELDS,
    )
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / "readout.md", summary)

    print(f"Wrote D1e collision-aware wave identity profile outputs to {output_dir}")


if __name__ == "__main__":
    main()
