#!/usr/bin/env python3
"""QSB-ST-COMP01-D1f synthetic collision-aware profile robustness sweep."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
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
    "sweep_seed",
    "kernel_size_label",
    "kernel_size",
    "parameter_sweep_family",
    "decoy_family",
    "null_family",
    "profile_weight_set_id",
    "penalty_weight_set_id",
    "pair_id",
    "wave_id_i",
    "wave_id_j",
    "control_family",
    "k_shift_level",
    "phase_drift_level",
    "amplitude_perturbation_level",
    "slope_perturbation_level",
    "noise_level",
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
    "profile_weight_sensitivity_warning",
    "penalty_weight_sensitivity_warning",
    "kernel_size_sensitivity_warning",
    "null_family_overlap_warning",
    "warning_count_total",
    "warning_count_reduction_vs_d1c",
    "warning_count_reduction_vs_d1d",
    "warning_count_reduction_vs_d1e",
    "profile_separation_margin",
    "control_overlap_rate",
    "decoy_success_rate",
    "exact_duplicate_sanity_passed",
    "specificity_established",
    "decision_status",
    "warning_flags",
    "interpretation_note",
]

PROFILE_WEIGHT_FIELDS = [
    "profile_weight_set_id",
    "row_count",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "warning_count_total",
    "profile_weight_sensitivity_warnings_count",
    "decoy_success_rate_mean",
    "control_overlap_rate_mean",
    "decision_statuses",
]

DECOY_FIELDS = [
    "decoy_family",
    "row_count",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "warning_count_total",
    "decoy_success_rate_mean",
    "control_overlap_rate_mean",
    "residual_matched_profile_warnings_count",
    "adversarial_profile_warnings_count",
    "decision_statuses",
]

KERNEL_FIELDS = [
    "kernel_size_label",
    "kernel_size",
    "row_count",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "warning_count_total",
    "kernel_size_sensitivity_warnings_count",
    "decoy_success_rate_mean",
    "control_overlap_rate_mean",
    "decision_statuses",
]

NULL_FIELDS = [
    "null_family",
    "row_count",
    "mean_profile_distance_raw",
    "mean_profile_distance_collision_penalized",
    "warning_count_total",
    "null_family_overlap_warnings_count",
    "decoy_success_rate_mean",
    "control_overlap_rate_mean",
    "decision_statuses",
]

WARNING_FIELDS = [
    "warning_type",
    "count",
    "rate",
    "comparison_reference",
    "comparison_count",
    "warning_count_reduction_vs_reference",
    "interpretation_note",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D1f collision-aware profile robustness sweep."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1f_collision_aware_profile_robustness_sweep_config.yaml",
    )
    return parser.parse_args()


def read_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise SystemExit(f"Config must be a mapping: {path}")
    return data


def stable_int(text: str) -> int:
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:16], 16)


def stable_random(*parts: Any) -> random.Random:
    return random.Random(stable_int("|".join(str(part) for part in parts)))


def wrap_minus_pi_pi(value: float) -> float:
    return (value + math.pi) % (2.0 * math.pi) - math.pi


def normalized_delta(value: float) -> float:
    return abs(value) / (1.0 + abs(value))


def safe_mean(values: list[float]) -> float:
    return mean(values) if values else 0.0


def as_float(value: Any) -> float:
    return float(value)


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


def wave_features(wave: dict[str, float], epsilon: float) -> dict[str, float]:
    k = wave["k"]
    a = wave["A"]
    b = wave["B"]
    phase = wave["phase"]
    r = math.sqrt(a * a + b * b)
    phi_wrapped = wrap_minus_pi_pi(phase)
    slope = b * k
    intercept = a
    balance = a - b
    denom = max(abs(a) + abs(b), epsilon)
    return {
        "k": k,
        "A": a,
        "B": b,
        "R": r,
        "phi": phase,
        "phi_wrapped": phi_wrapped,
        "slope": slope,
        "intercept": intercept,
        "amplitude_balance": balance,
        "normalized_amplitude_balance": balance / denom,
        "local_response_norm": math.sqrt(intercept * intercept + slope * slope),
    }


def apply_null_family(
    wave: dict[str, float],
    base: dict[str, float],
    null_family: str,
    rng: random.Random,
    scale: float,
    level: dict[str, Any],
) -> dict[str, float]:
    if null_family == "random_parameter_null":
        wave["k"] += rng.uniform(-0.16, 0.16) * scale
        wave["A"] += rng.uniform(-0.25, 0.25) * scale
        wave["B"] += rng.uniform(-0.25, 0.25) * scale
        wave["phase"] += rng.uniform(-0.70, 0.70) * scale
    elif null_family == "distribution_matched_null":
        wave["k"] += rng.uniform(-level["k_shift"], level["k_shift"]) * scale
        wave["A"] += rng.uniform(-level["amplitude_perturbation"], level["amplitude_perturbation"]) * scale
        wave["B"] += rng.uniform(-level["slope_perturbation"], level["slope_perturbation"]) * scale
        wave["phase"] += rng.uniform(-level["phase_drift"], level["phase_drift"]) * scale
    elif null_family == "spectrum_matched_null":
        wave["k"] = base["k"] + rng.uniform(-0.01, 0.01) * scale
        wave["A"] += rng.uniform(-0.22, 0.22) * scale
        wave["B"] += rng.uniform(-0.22, 0.22) * scale
    elif null_family == "phase_randomized_null":
        wave["phase"] = rng.uniform(-math.pi, math.pi)
    elif null_family == "amplitude_preserved_null":
        radius = math.sqrt(base["A"] * base["A"] + base["B"] * base["B"])
        theta = math.atan2(base["B"], base["A"]) + rng.uniform(-0.45, 0.45) * scale
        wave["A"] = radius * math.cos(theta)
        wave["B"] = radius * math.sin(theta)
    elif null_family == "label_shuffle_null":
        wave["A"], wave["B"] = wave["B"], wave["A"]
        wave["phase"] += 0.25 * scale
    elif null_family == "profile_shuffle_null":
        wave["k"] = max(0.05, base["B"] + rng.uniform(-0.04, 0.04) * scale)
        wave["B"] = max(-1.5, min(1.5, base["k"] + rng.uniform(-0.10, 0.10) * scale))
    elif null_family == "control_family_permutation_null":
        wave["k"] += rng.choice([-1.0, 1.0]) * level["k_shift"] * 0.7 * scale
        wave["phase"] -= rng.choice([-1.0, 1.0]) * level["phase_drift"] * 0.5 * scale
    return wave


def build_wave_j(
    base_wave: dict[str, Any],
    decoy_family: str,
    null_family: str,
    seed: int,
    kernel: dict[str, Any],
    level: dict[str, Any],
    case_key: str,
) -> dict[str, float]:
    base = {
        "k": as_float(base_wave["k"]),
        "A": as_float(base_wave["A"]),
        "B": as_float(base_wave["B"]),
        "phase": as_float(base_wave.get("phase_override", 0.0)),
    }
    scale = as_float(kernel["synthetic_scale_factor"])
    k_shift = as_float(level["k_shift"]) * scale
    phase_drift = as_float(level["phase_drift"]) * scale
    amp = as_float(level["amplitude_perturbation"]) * scale
    slope_shift = as_float(level["slope_perturbation"]) * scale
    noise = as_float(level["noise_level"]) * scale
    rng = stable_random(seed, kernel["kernel_size_label"], level["parameter_sweep_family"], decoy_family, null_family, case_key)
    wave = dict(base)

    if decoy_family == "exact_duplicate":
        return wave
    if decoy_family == "simple_near_duplicate":
        wave["k"] += 0.5 * k_shift
        wave["phase"] += 0.5 * phase_drift
        wave["A"] += 0.3 * amp
        wave["B"] += 0.3 * slope_shift
    elif decoy_family == "residual_matched_decoy_sweep":
        wave["k"] += 0.45 * k_shift
        wave["phase"] += 0.35 * phase_drift
        wave["A"] -= 0.55 * amp
        wave["B"] += 0.55 * slope_shift
    elif decoy_family == "adversarial_near_duplicate_sweep":
        wave["k"] += 0.25 * k_shift
        wave["phase"] -= 0.25 * phase_drift
        wave["A"] += 0.25 * amp
        wave["B"] -= 0.25 * slope_shift
    elif decoy_family == "profile_matched_decoy":
        wave["k"] += 0.20 * k_shift
        wave["phase"] += 0.15 * phase_drift
        wave["A"] += 0.85 * amp
        wave["B"] -= 0.35 * slope_shift
    elif decoy_family == "rank_stability_matched_decoy":
        wave["k"] += 0.35 * k_shift
        wave["phase"] += 0.20 * phase_drift
        wave["A"] += 0.75 * amp
        wave["B"] -= 0.75 * slope_shift
    elif decoy_family == "collision_penalty_evading_decoy":
        wave["k"] += 0.10 * k_shift
        wave["phase"] += 0.10 * phase_drift
        wave["A"] += 0.10 * amp
        wave["B"] -= 0.10 * slope_shift
    elif decoy_family == "angular_phase_matched_decoy":
        wave["k"] += 1.1 * k_shift
        wave["phase"] += 0.02 * phase_drift
        wave["A"] -= 1.0 * amp
        wave["B"] += 0.9 * slope_shift
    elif decoy_family == "local_response_matched_decoy":
        wave["k"] += 1.2 * k_shift
        wave["phase"] += 0.8 * phase_drift
        wave["A"] += 0.03 * amp
        target_slope = base["B"] * base["k"]
        wave["B"] = target_slope / max(wave["k"], 0.05)
    elif decoy_family == "multi_component_matched_decoy":
        wave["k"] += 0.18 * k_shift
        wave["phase"] += 0.18 * phase_drift
        wave["A"] += 0.18 * amp
        wave["B"] += 0.18 * slope_shift

    if noise:
        wave["k"] += rng.uniform(-noise, noise)
        wave["A"] += rng.uniform(-noise, noise)
        wave["B"] += rng.uniform(-noise, noise)
        wave["phase"] += rng.uniform(-noise, noise)

    return apply_null_family(wave, base, null_family, rng, scale, level)


def pair_components(
    base_features: dict[str, float],
    test_features: dict[str, float],
    epsilon: float,
) -> dict[str, Any]:
    phi_delta = wrap_minus_pi_pi(base_features["phi_wrapped"] - test_features["phi_wrapped"])
    delta_k = abs(base_features["k"] - test_features["k"])
    delta_r = abs(base_features["R"] - test_features["R"])
    delta_a = abs(base_features["A"] - test_features["A"])
    delta_b = abs(base_features["B"] - test_features["B"])
    delta_slope = abs(base_features["slope"] - test_features["slope"])
    delta_intercept = abs(base_features["intercept"] - test_features["intercept"])
    delta_balance = abs(
        base_features["normalized_amplitude_balance"]
        - test_features["normalized_amplitude_balance"]
    )
    local_response_delta = abs(
        base_features["local_response_norm"] - test_features["local_response_norm"]
    )
    coordinate_vector = [
        normalized_delta(delta_k),
        normalized_delta(delta_r),
        normalized_delta(delta_a),
        normalized_delta(delta_b),
        normalized_delta(delta_slope),
        normalized_delta(delta_intercept),
        normalized_delta(delta_balance),
        normalized_delta(local_response_delta),
    ]
    angular_vector = [
        abs(phi_delta) / math.pi,
        1.0 - abs(math.cos(phi_delta)),
        abs(math.sin(phi_delta)),
    ]
    local_vector = [
        normalized_delta(delta_slope),
        normalized_delta(delta_intercept),
        normalized_delta(delta_balance),
        normalized_delta(local_response_delta),
    ]
    spectral_component = delta_k / max(abs(base_features["k"]), abs(test_features["k"]), epsilon)
    phase_gradient_delta = abs(
        (base_features["phi_wrapped"] * base_features["k"])
        - (test_features["phi_wrapped"] * test_features["k"])
    )
    phase_component = safe_mean(
        [abs(phi_delta) / math.pi, phase_gradient_delta / (1.0 + phase_gradient_delta)]
    )
    local_component = safe_mean([normalized_delta(delta_intercept), normalized_delta(delta_slope)])
    residual_proxy = safe_mean([spectral_component, phase_component, local_component])
    delta_norm = math.sqrt(
        sum(
            value * value
            for value in [
                delta_k,
                delta_r,
                abs(phi_delta),
                delta_a,
                delta_b,
                delta_slope,
                delta_intercept,
                delta_balance,
                local_response_delta,
            ]
        )
    )
    return {
        "coordinate_component": safe_mean(coordinate_vector),
        "angular_phase_component": safe_mean(angular_vector),
        "local_response_component": safe_mean(local_vector),
        "residual_weight_component": normalized_delta(residual_proxy),
        "rank_stability_component": normalized_delta(residual_proxy),
        "collision_component": 0.0,
        "control_response_component": 0.0,
        "residual_proxy": residual_proxy,
        "delta_vector_norm": delta_norm,
    }


def raw_profile_distance(components: dict[str, Any], weight_set: dict[str, Any], epsilon: float) -> float:
    weights = {
        "coordinate_profile": as_float(weight_set["coordinate_profile"]),
        "angular_phase_profile": as_float(weight_set["angular_phase_profile"]),
        "local_response_profile": as_float(weight_set["local_response_profile"]),
        "residual_weight_profile": as_float(weight_set["residual_weight_profile"]),
        "rank_stability_profile": as_float(weight_set["rank_stability_profile"]),
        "collision_profile": as_float(weight_set["collision_profile"]),
        "control_response_profile": as_float(weight_set["control_response_profile"]),
    }
    values = {
        "coordinate_profile": components["coordinate_component"],
        "angular_phase_profile": components["angular_phase_component"],
        "local_response_profile": components["local_response_component"],
        "residual_weight_profile": components["residual_weight_component"],
        "rank_stability_profile": components["rank_stability_component"],
        "collision_profile": components["collision_component"],
        "control_response_profile": components["control_response_component"],
    }
    weight_sum = sum(weights.values())
    if weight_sum <= epsilon:
        return 0.0
    return sum(weights[name] * values[name] for name in weights) / weight_sum


def choose_null_family(
    null_families: list[dict[str, Any]], seed: int, parameter_family: str, decoy_family: str
) -> str:
    index = stable_int(f"{seed}|{parameter_family}|{decoy_family}") % len(null_families)
    return str(null_families[index]["null_family"])


def initial_rows(config: dict[str, Any]) -> list[dict[str, Any]]:
    norm = config["normalization"]
    epsilon = as_float(norm["epsilon"])
    base_wave = config["base_wave"]
    base_features = wave_features(
        {
            "k": as_float(base_wave["k"]),
            "A": as_float(base_wave["A"]),
            "B": as_float(base_wave["B"]),
            "phase": as_float(base_wave.get("phase_override", 0.0)),
        },
        epsilon,
    )
    rows: list[dict[str, Any]] = []
    counter = 0
    for seed in config["sweep_seeds"]:
        for kernel in config["kernel_sizes"]:
            for level in config["parameter_levels"]:
                for profile_weights in config["profile_weight_sets"]:
                    for penalty_weights in config["penalty_weight_sets"]:
                        for decoy in config["decoy_families"]:
                            decoy_family = decoy["decoy_family"]
                            null_family = choose_null_family(
                                config["null_families"],
                                int(seed),
                                level["parameter_sweep_family"],
                                decoy_family,
                            )
                            case_key = (
                                f"{seed}__{kernel['kernel_size_label']}__"
                                f"{level['parameter_sweep_family']}__"
                                f"{profile_weights['profile_weight_set_id']}__"
                                f"{penalty_weights['penalty_weight_set_id']}__"
                                f"{decoy_family}"
                            )
                            case_id = f"case_{counter:05d}"
                            wave_j = build_wave_j(
                                base_wave,
                                decoy_family,
                                null_family,
                                int(seed),
                                kernel,
                                level,
                                case_key,
                            )
                            test_features = wave_features(wave_j, epsilon)
                            components = pair_components(base_features, test_features, epsilon)
                            raw_distance = raw_profile_distance(components, profile_weights, epsilon)
                            row = {
                                "run_id": config["run_id"],
                                "case_id": case_id,
                                "sweep_seed": int(seed),
                                "kernel_size_label": kernel["kernel_size_label"],
                                "kernel_size": int(kernel["kernel_size"]),
                                "parameter_sweep_family": level["parameter_sweep_family"],
                                "decoy_family": decoy_family,
                                "decoy_role": decoy.get("role", ""),
                                "null_family": null_family,
                                "profile_weight_set_id": profile_weights["profile_weight_set_id"],
                                "penalty_weight_set_id": penalty_weights["penalty_weight_set_id"],
                                "pair_id": f"pair_{case_id}_{decoy_family}",
                                "wave_id_i": base_wave["wave_id"],
                                "wave_id_j": f"{base_wave['wave_id']}_{decoy_family}_{case_id}",
                                "control_family": decoy_family,
                                "k_shift_level": level["parameter_sweep_family"],
                                "phase_drift_level": level["parameter_sweep_family"],
                                "amplitude_perturbation_level": level["parameter_sweep_family"],
                                "slope_perturbation_level": level["parameter_sweep_family"],
                                "noise_level": as_float(level["noise_level"]),
                                "profile_distance_raw": raw_distance,
                                "residual_proxy": components["residual_proxy"],
                                "delta_vector_norm": components["delta_vector_norm"],
                                "profile_weight_sensitivity_warning": False,
                                "penalty_weight_sensitivity_warning": False,
                                "kernel_size_sensitivity_warning": False,
                                "specificity_established": False,
                                "interpretation_note": (
                                    "Synthetic diagnostic robustness case only."
                                ),
                                "_penalty_weights": penalty_weights,
                            }
                            rows.append(row)
                            counter += 1
    return rows


def apply_case_flags(rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    norm = config["normalization"]
    collision_threshold = as_float(norm["collision_distance_threshold"])
    residual_threshold = as_float(norm["residual_collision_threshold"])
    overlap_multiplier = as_float(norm.get("near_duplicate_overlap_multiplier", 1.0))

    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            row["sweep_seed"],
            row["kernel_size_label"],
            row["parameter_sweep_family"],
            row["profile_weight_set_id"],
            row["penalty_weight_set_id"],
        )
        grouped[key].append(row)

    for family_rows in grouped.values():
        near_values = [
            row["profile_distance_raw"]
            for row in family_rows
            if row["decoy_family"] == "simple_near_duplicate"
        ]
        near_max = (max(near_values) if near_values else 0.0) * overlap_multiplier
        for row in family_rows:
            is_exact = row["decoy_family"] == "exact_duplicate"
            is_non_exact = not is_exact
            raw_distance = row["profile_distance_raw"]
            row["near_duplicate_reference_max"] = near_max
            row["profile_collision"] = is_non_exact and raw_distance <= collision_threshold
            row["residual_collision"] = (
                is_non_exact
                and (
                    row["residual_proxy"] <= residual_threshold
                    or raw_distance <= residual_threshold
                )
            )
            row["delta_vector_collision"] = (
                is_non_exact and row["delta_vector_norm"] <= collision_threshold
            )
            row["ambiguity_warning"] = (
                row["profile_collision"]
                or row["residual_collision"]
                or row["delta_vector_collision"]
                or (is_non_exact and near_max > 0 and raw_distance <= near_max * 0.25)
            )
            row["control_profile_mimicry_warning"] = (
                is_non_exact and near_max > 0 and raw_distance <= near_max
            )
            row["residual_matched_profile_warning"] = (
                row["decoy_family"]
                in {"residual_matched_decoy_sweep", "profile_matched_decoy"}
                and (row["control_profile_mimicry_warning"] or row["residual_collision"])
            )
            row["adversarial_profile_warning"] = (
                row["decoy_family"]
                in {
                    "adversarial_near_duplicate_sweep",
                    "collision_penalty_evading_decoy",
                    "multi_component_matched_decoy",
                }
                and (
                    row["control_profile_mimicry_warning"]
                    or (not row["ambiguity_warning"] and near_max > 0 and raw_distance <= near_max * 0.75)
                )
            )
            row["null_family_overlap_warning"] = (
                is_non_exact and near_max > 0 and raw_distance <= near_max
            )
            row["profile_separation_margin"] = raw_distance - near_max
            row["control_overlap_rate"] = 1.0 if row["control_profile_mimicry_warning"] or row["null_family_overlap_warning"] else 0.0
            row["decoy_success_rate"] = (
                1.0
                if row["decoy_role"] == "harder_decoy"
                and (
                    row["control_profile_mimicry_warning"]
                    or row["residual_matched_profile_warning"]
                    or row["adversarial_profile_warning"]
                    or row["null_family_overlap_warning"]
                )
                else 0.0
            )
            row["exact_duplicate_sanity_passed"] = (
                raw_distance <= collision_threshold if is_exact else False
            )


def apply_penalties(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        weights = row["_penalty_weights"]
        row["profile_collision_penalty"] = as_float(weights["profile_collision_penalty"]) if row["profile_collision"] else 0.0
        row["residual_collision_penalty"] = as_float(weights["residual_collision_penalty"]) if row["residual_collision"] else 0.0
        row["delta_vector_collision_penalty"] = as_float(weights["delta_vector_collision_penalty"]) if row["delta_vector_collision"] else 0.0
        row["ambiguity_penalty"] = as_float(weights["ambiguity_penalty"]) if row["ambiguity_warning"] else 0.0
        row["control_mimicry_penalty"] = as_float(weights["control_mimicry_penalty"]) if row["control_profile_mimicry_warning"] else 0.0
        row["residual_matched_penalty"] = as_float(weights["residual_matched_penalty"]) if row["residual_matched_profile_warning"] else 0.0
        row["adversarial_penalty"] = as_float(weights["adversarial_penalty"]) if row["adversarial_profile_warning"] else 0.0
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


def mark_range_warning(
    rows: list[dict[str, Any]], key_fields: list[str], value_field: str, flag_field: str
) -> None:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[tuple(row[field] for field in key_fields)].append(row)
    for group_rows in grouped.values():
        values = [row[value_field] for row in group_rows]
        flag = max(values) - min(values) > 0.10
        if flag:
            for row in group_rows:
                row[flag_field] = True


def finalize_rows(rows: list[dict[str, Any]], config: dict[str, Any]) -> None:
    mark_range_warning(
        rows,
        [
            "sweep_seed",
            "kernel_size_label",
            "parameter_sweep_family",
            "decoy_family",
            "null_family",
            "penalty_weight_set_id",
        ],
        "profile_distance_raw",
        "profile_weight_sensitivity_warning",
    )
    mark_range_warning(
        rows,
        [
            "sweep_seed",
            "kernel_size_label",
            "parameter_sweep_family",
            "decoy_family",
            "null_family",
            "profile_weight_set_id",
        ],
        "profile_distance_collision_penalized",
        "penalty_weight_sensitivity_warning",
    )
    mark_range_warning(
        rows,
        [
            "sweep_seed",
            "parameter_sweep_family",
            "decoy_family",
            "null_family",
            "profile_weight_set_id",
            "penalty_weight_set_id",
        ],
        "profile_distance_collision_penalized",
        "kernel_size_sensitivity_warning",
    )
    refs = config["reference_thresholds"]
    d1c_reference = int(refs["d1c_control_mimicry_warnings_count"])
    d1d_reference = int(refs["d1d_residual_collision_count"]) + int(refs["d1d_delta_vector_collision_count"])
    d1e_reference = (
        int(refs["d1e_control_profile_mimicry_warnings_count"])
        + int(refs["d1e_residual_collision_count"])
        + int(refs["d1e_delta_vector_collision_count"])
    )
    for row in rows:
        decoy_success_warning = row["decoy_success_rate"] > 0.0
        control_overlap_warning = row["control_overlap_rate"] > 0.0
        warnings = {
            "profile_collision": row["profile_collision"],
            "residual_collision": row["residual_collision"],
            "delta_vector_collision": row["delta_vector_collision"],
            "ambiguity_warning": row["ambiguity_warning"],
            "control_profile_mimicry_warning": row["control_profile_mimicry_warning"],
            "residual_matched_profile_warning": row["residual_matched_profile_warning"],
            "adversarial_profile_warning": row["adversarial_profile_warning"],
            "profile_weight_sensitivity_warning": row["profile_weight_sensitivity_warning"],
            "penalty_weight_sensitivity_warning": row["penalty_weight_sensitivity_warning"],
            "kernel_size_sensitivity_warning": row["kernel_size_sensitivity_warning"],
            "null_family_overlap_warning": row["null_family_overlap_warning"],
            "decoy_success_warning": decoy_success_warning,
            "control_overlap_warning": control_overlap_warning,
        }
        row["warning_count_total"] = sum(1 for value in warnings.values() if value)
        row["warning_count_reduction_vs_d1c"] = d1c_reference - row["warning_count_total"]
        row["warning_count_reduction_vs_d1d"] = d1d_reference - row["warning_count_total"]
        row["warning_count_reduction_vs_d1e"] = d1e_reference - row["warning_count_total"]
        if row["decoy_family"] == "exact_duplicate":
            row["decision_status"] = (
                "exact_duplicate_sanity_pass"
                if row["exact_duplicate_sanity_passed"]
                else "exact_duplicate_sanity_fail"
            )
        elif decoy_success_warning:
            row["decision_status"] = "decoy_success_warning"
        elif row["null_family_overlap_warning"]:
            row["decision_status"] = "null_family_overlap_warning"
        elif row["profile_weight_sensitivity_warning"]:
            row["decision_status"] = "profile_weight_sensitivity_warning"
        elif row["penalty_weight_sensitivity_warning"]:
            row["decision_status"] = "penalty_weight_sensitivity_warning"
        elif row["kernel_size_sensitivity_warning"]:
            row["decision_status"] = "kernel_size_sensitivity_warning"
        elif row["warning_count_total"] > d1e_reference:
            row["decision_status"] = "warning_reduction_unstable_warning"
        elif row["warning_count_total"] <= d1e_reference:
            row["decision_status"] = "warning_reduction_stable_candidate"
        else:
            row["decision_status"] = "inconclusive"
        row["warning_flags"] = sorted(name for name, value in warnings.items() if value)
        row.pop("_penalty_weights", None)


def summarize_group(
    rows: list[dict[str, Any]], group_field: str, fieldnames: list[str]
) -> list[dict[str, Any]]:
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row[group_field]].append(row)
    output = []
    for key in sorted(grouped):
        group_rows = grouped[key]
        base = {
            group_field: key,
            "row_count": len(group_rows),
            "mean_profile_distance_raw": mean(row["profile_distance_raw"] for row in group_rows),
            "mean_profile_distance_collision_penalized": mean(
                row["profile_distance_collision_penalized"] for row in group_rows
            ),
            "warning_count_total": sum(row["warning_count_total"] for row in group_rows),
            "decoy_success_rate_mean": mean(row["decoy_success_rate"] for row in group_rows),
            "control_overlap_rate_mean": mean(row["control_overlap_rate"] for row in group_rows),
            "decision_statuses": sorted({row["decision_status"] for row in group_rows}),
        }
        if group_field == "profile_weight_set_id":
            base["profile_weight_sensitivity_warnings_count"] = sum(
                1 for row in group_rows if row["profile_weight_sensitivity_warning"]
            )
        if group_field == "decoy_family":
            base["residual_matched_profile_warnings_count"] = sum(
                1 for row in group_rows if row["residual_matched_profile_warning"]
            )
            base["adversarial_profile_warnings_count"] = sum(
                1 for row in group_rows if row["adversarial_profile_warning"]
            )
        if group_field == "kernel_size_label":
            base["kernel_size"] = group_rows[0]["kernel_size"]
            base["kernel_size_sensitivity_warnings_count"] = sum(
                1 for row in group_rows if row["kernel_size_sensitivity_warning"]
            )
        if group_field == "null_family":
            base["null_family_overlap_warnings_count"] = sum(
                1 for row in group_rows if row["null_family_overlap_warning"]
            )
        output.append(base)
    return [{field: row.get(field) for field in fieldnames} for row in output]


def warning_summary_rows(rows: list[dict[str, Any]], config: dict[str, Any]) -> list[dict[str, Any]]:
    total = len(rows)
    refs = config["reference_thresholds"]
    warning_specs = [
        ("profile_collision", "D1e residual/collision warning proxy", refs["d1e_residual_collision_count"]),
        ("residual_collision", "D1d residual collision", refs["d1d_residual_collision_count"]),
        ("delta_vector_collision", "D1d delta-vector collision", refs["d1d_delta_vector_collision_count"]),
        ("ambiguity_warning", "D1e residual/collision warning proxy", refs["d1e_residual_collision_count"]),
        ("control_profile_mimicry_warning", "D1c control mimicry", refs["d1c_control_mimicry_warnings_count"]),
        ("residual_matched_profile_warning", "D1e residual collision", refs["d1e_residual_collision_count"]),
        ("adversarial_profile_warning", "D1e profile warnings", refs["d1e_control_profile_mimicry_warnings_count"]),
        ("profile_weight_sensitivity_warning", "D1f internal", 0),
        ("penalty_weight_sensitivity_warning", "D1f internal", 0),
        ("kernel_size_sensitivity_warning", "D1f internal", 0),
        ("null_family_overlap_warning", "D1f internal", 0),
    ]
    output = []
    for warning_type, reference, comparison in warning_specs:
        count = sum(1 for row in rows if row.get(warning_type))
        output.append(
            {
                "warning_type": warning_type,
                "count": count,
                "rate": count / total if total else 0.0,
                "comparison_reference": reference,
                "comparison_count": int(comparison),
                "warning_count_reduction_vs_reference": int(comparison) - count,
                "interpretation_note": "Diagnostic warning count only; no proof claim.",
            }
        )
    return output


def build_summary(rows: list[dict[str, Any]], config: dict[str, Any], generated_files: list[str]) -> dict[str, Any]:
    decision_counts = Counter(row["decision_status"] for row in rows)
    exact_rows = [row for row in rows if row["decoy_family"] == "exact_duplicate"]
    return {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "output_dir": config["output_dir"],
        "case_count": len(rows),
        "expected_case_count": (
            len(config["sweep_seeds"])
            * len(config["kernel_sizes"])
            * len(config["parameter_levels"])
            * len(config["profile_weight_sets"])
            * len(config["penalty_weight_sets"])
            * len(config["decoy_families"])
        ),
        "specificity_established": False,
        "stable_candidate_metrics": [],
        "exact_duplicate_sanity_passed_all": all(
            row["exact_duplicate_sanity_passed"] for row in exact_rows
        ),
        "warning_count_total": sum(row["warning_count_total"] for row in rows),
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
        "profile_weight_sensitivity_warnings_count": sum(
            1 for row in rows if row["profile_weight_sensitivity_warning"]
        ),
        "penalty_weight_sensitivity_warnings_count": sum(
            1 for row in rows if row["penalty_weight_sensitivity_warning"]
        ),
        "kernel_size_sensitivity_warnings_count": sum(
            1 for row in rows if row["kernel_size_sensitivity_warning"]
        ),
        "null_family_overlap_warnings_count": sum(
            1 for row in rows if row["null_family_overlap_warning"]
        ),
        "decoy_success_warnings_count": sum(
            1 for row in rows if row["decoy_success_rate"] > 0.0
        ),
        "control_overlap_warnings_count": sum(
            1 for row in rows if row["control_overlap_rate"] > 0.0
        ),
        "mean_profile_distance_raw": mean(row["profile_distance_raw"] for row in rows),
        "mean_profile_distance_collision_penalized": mean(
            row["profile_distance_collision_penalized"] for row in rows
        ),
        "mean_decoy_success_rate": mean(row["decoy_success_rate"] for row in rows),
        "mean_control_overlap_rate": mean(row["control_overlap_rate"] for row in rows),
        "decision_status_counts": dict(sorted(decision_counts.items())),
        "generated_files": generated_files,
        "claim_boundary": config.get("metadata", {}).get(
            "claim_boundary",
            "synthetic diagnostic collision-aware profile robustness sweep only",
        ),
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    stability_text = (
        "The sweep keeps D1e's reduced warning situation under pressure, but "
        "the warning counts must be read as diagnostic robustness signals only."
    )
    text = f"""# QSB-ST-COMP01-D1f Collision-Aware Profile Robustness Sweep Readout

## Befund

D1f is a synthetic diagnostic robustness / parameter-sweep run.

`case_count`: {summary["case_count"]}

`expected_case_count`: {summary["expected_case_count"]}

`specificity_established`: false

`exact_duplicate_sanity_passed_all`: {str(summary["exact_duplicate_sanity_passed_all"]).lower()}

Warning counts:

```yaml
warning_count_total: {summary["warning_count_total"]}
profile_collision_count: {summary["profile_collision_count"]}
residual_collision_count: {summary["residual_collision_count"]}
delta_vector_collision_count: {summary["delta_vector_collision_count"]}
ambiguity_warning_count: {summary["ambiguity_warning_count"]}
control_profile_mimicry_warnings_count: {summary["control_profile_mimicry_warnings_count"]}
residual_matched_profile_warnings_count: {summary["residual_matched_profile_warnings_count"]}
adversarial_profile_warnings_count: {summary["adversarial_profile_warnings_count"]}
profile_weight_sensitivity_warnings_count: {summary["profile_weight_sensitivity_warnings_count"]}
penalty_weight_sensitivity_warnings_count: {summary["penalty_weight_sensitivity_warnings_count"]}
kernel_size_sensitivity_warnings_count: {summary["kernel_size_sensitivity_warnings_count"]}
null_family_overlap_warnings_count: {summary["null_family_overlap_warnings_count"]}
decoy_success_warnings_count: {summary["decoy_success_warnings_count"]}
control_overlap_warnings_count: {summary["control_overlap_warnings_count"]}
```

Mean diagnostic distances:

```yaml
mean_profile_distance_raw: {summary["mean_profile_distance_raw"]:.12g}
mean_profile_distance_collision_penalized: {summary["mean_profile_distance_collision_penalized"]:.12g}
mean_decoy_success_rate: {summary["mean_decoy_success_rate"]:.12g}
mean_control_overlap_rate: {summary["mean_control_overlap_rate"]:.12g}
```

## Interpretation

{stability_text}

The readout does not establish diagnostic specificity. It reports whether warning behavior remains low, rises, or shifts under broader synthetic stress.

## Hypothese

A collision-aware `wave_identity_profile` may remain useful as a diagnostic search axis if future review finds that warning reductions are stable across parameter sweeps, harder decoys, weight variation, kernel-size scaling, and independent null families.

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

`wave_identity_profile` is a diagnostic profile concept, not a proof of physical identity.

Collision-aware profile distance is a methodological diagnostic construct, not a physical distance.

Collision penalties are methodological warning terms, not physical forces or interactions.

Parameter sweeps are robustness tests, not physical parameter fitting.

Kernel-size scaling is a methodological robustness test, not a physical system-size claim.

Null families are diagnostic controls, not physical ensembles.

Control mimicry warnings are methodological warnings, not failures of physics.

COMP01-D1f does not validate a physical Bridge.

COMP01-D1f does not derive a Lorentzian metric.

COMP01-D1f does not establish diagnostic specificity.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

“wave-Pauli” is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

## Machine-readable status

```yaml
block_id: {summary["block_id"]}
run_id: {summary["run_id"]}
case_count: {summary["case_count"]}
expected_case_count: {summary["expected_case_count"]}
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed_all: {str(summary["exact_duplicate_sanity_passed_all"]).lower()}
warning_count_total: {summary["warning_count_total"]}
profile_collision_count: {summary["profile_collision_count"]}
residual_collision_count: {summary["residual_collision_count"]}
delta_vector_collision_count: {summary["delta_vector_collision_count"]}
ambiguity_warning_count: {summary["ambiguity_warning_count"]}
control_profile_mimicry_warnings_count: {summary["control_profile_mimicry_warnings_count"]}
residual_matched_profile_warnings_count: {summary["residual_matched_profile_warnings_count"]}
adversarial_profile_warnings_count: {summary["adversarial_profile_warnings_count"]}
profile_weight_sensitivity_warnings_count: {summary["profile_weight_sensitivity_warnings_count"]}
penalty_weight_sensitivity_warnings_count: {summary["penalty_weight_sensitivity_warnings_count"]}
kernel_size_sensitivity_warnings_count: {summary["kernel_size_sensitivity_warnings_count"]}
null_family_overlap_warnings_count: {summary["null_family_overlap_warnings_count"]}
decoy_success_warnings_count: {summary["decoy_success_warnings_count"]}
mean_profile_distance_raw: {summary["mean_profile_distance_raw"]:.12g}
mean_profile_distance_collision_penalized: {summary["mean_profile_distance_collision_penalized"]:.12g}
mean_decoy_success_rate: {summary["mean_decoy_success_rate"]:.12g}
mean_control_overlap_rate: {summary["mean_control_overlap_rate"]:.12g}
```
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    config_path = Path(args.config)
    config = read_config(config_path)
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = initial_rows(config)
    apply_case_flags(rows, config)
    apply_penalties(rows)
    finalize_rows(rows, config)

    generated_files = [
        "summary.json",
        "readout.md",
        "case_profile_summary.csv",
        "profile_weight_summary.csv",
        "decoy_family_summary.csv",
        "kernel_size_summary.csv",
        "null_family_summary.csv",
        "warning_stability_summary.csv",
        "resolved_config.json",
    ]

    summary = build_summary(rows, config, generated_files)
    write_csv(output_dir / "case_profile_summary.csv", rows, CASE_FIELDS)
    write_csv(
        output_dir / "profile_weight_summary.csv",
        summarize_group(rows, "profile_weight_set_id", PROFILE_WEIGHT_FIELDS),
        PROFILE_WEIGHT_FIELDS,
    )
    write_csv(
        output_dir / "decoy_family_summary.csv",
        summarize_group(rows, "decoy_family", DECOY_FIELDS),
        DECOY_FIELDS,
    )
    write_csv(
        output_dir / "kernel_size_summary.csv",
        summarize_group(rows, "kernel_size_label", KERNEL_FIELDS),
        KERNEL_FIELDS,
    )
    write_csv(
        output_dir / "null_family_summary.csv",
        summarize_group(rows, "null_family", NULL_FIELDS),
        NULL_FIELDS,
    )
    write_csv(
        output_dir / "warning_stability_summary.csv",
        warning_summary_rows(rows, config),
        WARNING_FIELDS,
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
    print(f"Wrote D1f robustness sweep outputs to {output_dir}")


if __name__ == "__main__":
    main()
