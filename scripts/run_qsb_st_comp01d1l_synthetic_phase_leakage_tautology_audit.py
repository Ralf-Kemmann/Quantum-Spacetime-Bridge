#!/usr/bin/env python3
"""QSB-ST-COMP01-D1l synthetic phase leakage and tautology audit."""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter
from pathlib import Path
from statistics import mean, pstdev
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required for this runner. Install PyYAML or run in the "
        "project environment where yaml is available."
    ) from exc


GENERATED_FILES = [
    "summary.json",
    "readout.md",
    "leakage_taxonomy_summary.csv",
    "construction_variant_summary.csv",
    "component_ablation_summary.csv",
    "shuffled_input_summary.csv",
    "family_blind_summary.csv",
    "threshold_weight_sweep_summary.csv",
    "proxy_exposed_mismatch_localization.csv",
    "resolved_config.json",
]

LEAKAGE_FIELDS = [
    "run_id",
    "leakage_risk_type",
    "warning",
    "evidence_metric",
    "evidence_value",
    "decision_status",
    "interpretation_note",
]

CONSTRUCTION_FIELDS = [
    "run_id",
    "construction_variant_id",
    "case_count",
    "false_accept_warning_exposed_count",
    "exclusion_success_exposed_rate",
    "stable_candidate_exposed_count",
    "fragile_candidate_exposed_count",
    "stable_candidate_loss_rate_exposed",
    "exposed_phase_overstrictness_warning_count",
    "remaining_intrusion_warning_count",
    "proxy_vs_exposed_phase_mismatch_count",
    "proxy_vs_exposed_phase_mismatch_rate",
    "survives_baseline_like_cleanliness",
    "construction_dependence_warning",
    "decision_status",
    "interpretation_note",
]

ABLATION_FIELDS = [
    "run_id",
    "ablated_component",
    "case_count",
    "false_accept_warning_exposed_count",
    "exclusion_success_exposed_rate",
    "stable_candidate_exposed_count",
    "fragile_candidate_exposed_count",
    "stable_candidate_loss_rate_exposed",
    "remaining_intrusion_warning_count",
    "survives_ablation",
    "component_ablation_failure_warning",
    "decision_status",
    "interpretation_note",
]

SHUFFLE_FIELDS = [
    "run_id",
    "shuffled_component",
    "shuffle_mode",
    "seed",
    "case_count",
    "false_accept_warning_exposed_count",
    "stable_candidate_exposed_count",
    "remaining_intrusion_warning_count",
    "survives_shuffle",
    "shuffled_input_suspicion",
    "shuffled_input_failure_warning",
    "decision_status",
    "interpretation_note",
]

FAMILY_BLIND_FIELDS = [
    "run_id",
    "blind_field_removed",
    "family_field_used_in_construction",
    "case_count",
    "false_accept_warning_exposed_count",
    "stable_candidate_exposed_count",
    "remaining_intrusion_warning_count",
    "survives_family_blindness",
    "target_family_leakage_warning",
    "decision_status",
    "interpretation_note",
]

THRESHOLD_FIELDS = [
    "run_id",
    "threshold_variant_id",
    "cyclic_acceptance_distance_threshold",
    "cyclic_phase_weight",
    "profile_distance_weight",
    "control_overlap_weight",
    "decoy_success_weight",
    "case_count",
    "false_accept_warning_exposed_count",
    "stable_candidate_exposed_count",
    "remaining_intrusion_warning_count",
    "threshold_leakage_warning",
    "overclean_result_warning",
    "decision_status",
    "interpretation_note",
]

MISMATCH_FIELDS = [
    "run_id",
    "case_id",
    "mismatch_type",
    "proxy_vs_exposed_phase_distance_delta",
    "baseline_cyclic_phase_proxy_distance",
    "exposed_phase_cyclic_distance",
    "false_accept_warning_proxy",
    "false_accept_warning_exposed",
    "stable_candidate_proxy",
    "stable_candidate_exposed",
    "decoy_family",
    "null_family",
    "kernel_size_label",
    "profile_weight_set_id",
    "penalty_weight_set_id",
    "interpretation_note",
]

PHASE_COMPONENTS = [
    "profile_distance_raw",
    "control_overlap_rate",
    "profile_distance_collision_penalized",
    "decoy_success_rate",
    "penalty_gap",
]

DIRECT_ACCEPTANCE_COMPONENTS = {
    "profile_distance_raw",
    "control_overlap_rate",
    "decoy_success_rate",
}

LABEL_OR_DECISION_FIELDS = {
    "current_false_accept_warning",
    "cyclic_false_accept_warning",
    "false_accept_warning_proxy",
    "false_accept_warning_exposed",
    "stable_candidate_proxy",
    "stable_candidate_exposed",
    "fragile_candidate_proxy",
    "fragile_candidate_exposed",
    "decision_status",
    "warning_flags",
}

FAMILY_FIELDS = {
    "decoy_family",
    "null_family",
    "profile_weight_set_id",
    "penalty_weight_set_id",
    "kernel_size_label",
}

BASE_THRESHOLD = 0.20
BASE_CYCLIC_WEIGHT = 0.45
BASE_PROFILE_WEIGHT = 0.35
BASE_CONTROL_WEIGHT = 0.10
BASE_DECOY_WEIGHT = 0.10
BASE_STABLE_LOSS_WARNING_RATE = 0.10
SHUFFLE_SEED = 1729


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run D1l synthetic phase leakage and tautology audit."
    )
    parser.add_argument(
        "--config",
        default="data/qsb_st_comp01d1l_synthetic_phase_leakage_tautology_audit_config.yaml",
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


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def safe_float(value: Any, default: float = 0.0) -> float:
    if value is None or value == "":
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if math.isfinite(number) else default


def safe_bool(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def positive(value: Any) -> float:
    return max(0.0, safe_float(value))


def soft_normalize(value: Any) -> float:
    number = safe_float(value)
    return number / (1.0 + abs(number))


def minmax_normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    min_value = min(values)
    max_value = max(values)
    span = max_value - min_value
    if span == 0:
        return [0.0 for _ in values]
    return [(value - min_value) / span for value in values]


def zscore_normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    center = mean(values)
    scale = pstdev(values) or 1.0
    return [soft_normalize((value - center) / scale) for value in values]


def rank_normalize(values: list[float]) -> list[float]:
    if not values:
        return []
    sorted_pairs = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0 for _ in values]
    denominator = max(1, len(values) - 1)
    for rank, (_, index) in enumerate(sorted_pairs):
        ranks[index] = rank / denominator
    return ranks


def deterministic_shuffle(values: list[Any], seed: int) -> list[Any]:
    shuffled = list(values)
    random.Random(seed).shuffle(shuffled)
    return shuffled


def deterministic_group_shuffle(values: list[Any], groups: list[str], seed: int) -> list[Any]:
    grouped_indices: dict[str, list[int]] = {}
    for index, group in enumerate(groups):
        grouped_indices.setdefault(group, []).append(index)
    result = list(values)
    rng = random.Random(seed)
    for indices in grouped_indices.values():
        group_values = [values[index] for index in indices]
        rng.shuffle(group_values)
        for index, value in zip(indices, group_values):
            result[index] = value
    return result


def wrap_angle(value: float) -> float:
    return math.atan2(math.sin(value), math.cos(value))


def format_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        if not math.isfinite(value):
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


def rate(numerator: int, denominator: int) -> float | None:
    return None if denominator == 0 else numerator / denominator


def pearson(values_a: list[float], values_b: list[float]) -> float | None:
    if len(values_a) != len(values_b) or len(values_a) < 2:
        return None
    mean_a = mean(values_a)
    mean_b = mean(values_b)
    numerator = sum((a - mean_a) * (b - mean_b) for a, b in zip(values_a, values_b))
    denom_a = math.sqrt(sum((a - mean_a) ** 2 for a in values_a))
    denom_b = math.sqrt(sum((b - mean_b) ** 2 for b in values_b))
    if denom_a == 0 or denom_b == 0:
        return None
    return numerator / (denom_a * denom_b)


def value_column(rows: list[dict[str, Any]], field: str) -> list[float]:
    return [safe_float(row.get(field)) for row in rows]


def prepare_columns(rows: list[dict[str, Any]]) -> dict[str, dict[str, list[float]]]:
    raw: dict[str, list[float]] = {}
    for field in PHASE_COMPONENTS:
        raw[field] = value_column(rows, field)
    return {
        "raw": raw,
        "soft": {field: [soft_normalize(value) for value in values] for field, values in raw.items()},
        "minmax": {field: minmax_normalize(values) for field, values in raw.items()},
        "zscore": {field: zscore_normalize(values) for field, values in raw.items()},
        "rank": {field: rank_normalize(values) for field, values in raw.items()},
        "monotone": {
            field: minmax_normalize([math.log1p(max(0.0, value)) for value in values])
            for field, values in raw.items()
        },
    }


def component(
    columns: dict[str, dict[str, list[float]]],
    field: str,
    index: int,
    mode: str = "soft",
    overrides: dict[str, list[float]] | None = None,
) -> float:
    if overrides and field in overrides:
        return safe_float(overrides[field][index])
    return columns.get(mode, columns["soft"]).get(field, [0.0])[index]


def compute_phase_fields(
    phi_i_a: float,
    phi_i_b: float,
    phi_j_a: float,
    phi_j_b: float,
) -> dict[str, float]:
    phi_i = math.atan2(phi_i_b, phi_i_a)
    phi_j = math.atan2(phi_j_b, phi_j_a)
    delta_phi_raw = phi_i - phi_j
    delta_phi_wrapped = wrap_angle(delta_phi_raw)
    wrapped_delta_phi_abs = abs(delta_phi_wrapped)
    normalized_angular_distance = wrapped_delta_phi_abs / math.pi
    return {
        "phi_i": phi_i,
        "phi_j": phi_j,
        "delta_phi_raw": delta_phi_raw,
        "delta_phi_wrapped": delta_phi_wrapped,
        "wrapped_delta_phi_abs": wrapped_delta_phi_abs,
        "normalized_angular_distance": normalized_angular_distance,
        "exposed_phase_cyclic_distance": normalized_angular_distance,
    }


def phase_for_variant(
    variant_id: str,
    index: int,
    row: dict[str, Any],
    rows: list[dict[str, Any]],
    columns: dict[str, dict[str, list[float]]],
    overrides: dict[str, list[float]] | None = None,
) -> dict[str, float]:
    mode = "soft"
    if variant_id == "normalized_rank_component_construction":
        mode = "rank"
    elif variant_id == "zscore_component_construction":
        mode = "zscore"
    elif variant_id == "monotone_transform_component_construction":
        mode = "monotone"
    elif variant_id == "noise_jittered_component_construction":
        jitter = 0.01 * math.sin((index + 1) * 12.9898)
        overrides = dict(overrides or {})
        overrides["profile_distance_raw"] = [
            value + 0.01 * math.sin((i + 1) * 12.9898)
            for i, value in enumerate(columns["soft"]["profile_distance_raw"])
        ]
        overrides["control_overlap_rate"] = [
            value + 0.01 * math.cos((i + 1) * 7.233)
            for i, value in enumerate(columns["soft"]["control_overlap_rate"])
        ]
        _ = jitter

    profile_raw = component(columns, "profile_distance_raw", index, mode, overrides)
    control = component(columns, "control_overlap_rate", index, mode, overrides)
    collision = component(
        columns, "profile_distance_collision_penalized", index, mode, overrides
    )
    decoy = component(columns, "decoy_success_rate", index, mode, overrides)
    penalty = component(columns, "penalty_gap", index, mode, overrides)
    penalty_positive = max(0.0, penalty)

    if variant_id in {
        "baseline_d1k_construction",
        "normalized_rank_component_construction",
        "zscore_component_construction",
        "monotone_transform_component_construction",
        "noise_jittered_component_construction",
    }:
        return compute_phase_fields(profile_raw, control, collision, decoy + penalty_positive)
    if variant_id == "alternate_pair_1_profile_vs_control":
        return compute_phase_fields(profile_raw, control, profile_raw, collision)
    if variant_id == "alternate_pair_2_penalty_vs_decoy":
        return compute_phase_fields(penalty_positive, decoy, collision, profile_raw)
    if variant_id == "alternate_pair_3_collision_vs_profile":
        return compute_phase_fields(collision, profile_raw, control, decoy)
    if variant_id == "swapped_phi_i_phi_j_construction":
        return compute_phase_fields(collision, decoy + penalty_positive, profile_raw, control)
    if variant_id == "sign_flipped_component_construction":
        return compute_phase_fields(profile_raw, -control, collision, -(decoy + penalty_positive))
    if variant_id == "use_phase_components_not_used_in_acceptance_distance":
        return compute_phase_fields(collision, penalty_positive, penalty_positive, collision)
    return compute_phase_fields(profile_raw, control, collision, decoy + penalty_positive)


def targeted_intrusion_warning(row: dict[str, Any], config: dict[str, Any], false_accept: bool) -> bool:
    if not false_accept:
        return False
    families = config["targeted_intrusion_families"]
    return any(
        [
            row.get("null_family") == families["spectrum_matched_null"],
            row.get("decoy_family") == families["adversarial_near_duplicate"],
            row.get("profile_weight_set_id") == families["local_response_dominant"],
            row.get("penalty_weight_set_id") == families["strong_collision_penalties"],
            row.get("kernel_size_label") == families["kernel_size_8"],
            row.get("impostor_overlap_warning") == "true",
            row.get("penalty_weight_set_id") == families["cosmetic_penalty_lock"],
            row.get("null_family") == families["phase_randomized_null"],
            row.get("decoy_family") == families["phase_jittered_decoy"],
        ]
    )


def compute_acceptance_metrics(
    rows: list[dict[str, Any]],
    distances: list[float],
    config: dict[str, Any],
    threshold: float = BASE_THRESHOLD,
    cyclic_phase_weight: float = BASE_CYCLIC_WEIGHT,
    profile_distance_weight: float = BASE_PROFILE_WEIGHT,
    control_overlap_weight: float = BASE_CONTROL_WEIGHT,
    decoy_success_weight: float = BASE_DECOY_WEIGHT,
) -> dict[str, Any]:
    case_count = len(rows)
    current_false_accept_count = 0
    exclusion_success_count = 0
    false_accept_count = 0
    stable_count = 0
    fragile_count = 0
    remaining_intrusion_count = 0
    spectrum_count = 0
    adversarial_count = 0
    kernel_count = 0
    current_stable_count = 0
    current_stable_but_fragile = 0
    mismatch_count = 0
    per_case: list[dict[str, Any]] = []

    for row, exposed_distance in zip(rows, distances):
        profile_raw = safe_float(row.get("profile_distance_raw"))
        control = safe_float(row.get("control_overlap_rate"))
        decoy = safe_float(row.get("decoy_success_rate"))
        current_false_accept = safe_bool(row.get("current_false_accept_warning"))
        false_accept_proxy = safe_bool(row.get("false_accept_warning_proxy"))
        stable_proxy = safe_bool(row.get("stable_candidate_proxy"))
        stable_current = safe_bool(row.get("stable_candidate_current"))
        acceptance_distance = (
            cyclic_phase_weight * exposed_distance
            + profile_distance_weight * profile_raw
            + control_overlap_weight * control
            + decoy_success_weight * decoy
        )
        false_accept = current_false_accept and acceptance_distance <= threshold
        remaining_intrusion = targeted_intrusion_warning(row, config, false_accept)
        stable = not false_accept and not remaining_intrusion
        fragile = not stable
        if current_false_accept:
            current_false_accept_count += 1
            if not false_accept:
                exclusion_success_count += 1
        if false_accept:
            false_accept_count += 1
        if stable:
            stable_count += 1
        if fragile:
            fragile_count += 1
        if remaining_intrusion:
            remaining_intrusion_count += 1
        if false_accept and row.get("null_family") == config["targeted_intrusion_families"][
            "spectrum_matched_null"
        ]:
            spectrum_count += 1
        if false_accept and row.get("decoy_family") == config["targeted_intrusion_families"][
            "adversarial_near_duplicate"
        ]:
            adversarial_count += 1
        if false_accept and row.get("kernel_size_label") == config["targeted_intrusion_families"][
            "kernel_size_8"
        ]:
            kernel_count += 1
        if stable_current:
            current_stable_count += 1
            if fragile:
                current_stable_but_fragile += 1
        if false_accept_proxy != false_accept or stable_proxy != stable:
            mismatch_count += 1
        per_case.append(
            {
                "case_id": row["case_id"],
                "false_accept_warning_exposed": false_accept,
                "stable_candidate_exposed": stable,
                "remaining_intrusion_warning": remaining_intrusion,
                "exposed_phase_cyclic_distance": exposed_distance,
                "cyclic_acceptance_distance_exposed": acceptance_distance,
            }
        )

    stable_loss_rate = rate(current_stable_but_fragile, current_stable_count) or 0.0
    overstrict = stable_loss_rate > BASE_STABLE_LOSS_WARNING_RATE
    return {
        "case_count": case_count,
        "false_accept_warning_exposed_count": false_accept_count,
        "exclusion_success_exposed_rate": rate(exclusion_success_count, current_false_accept_count),
        "stable_candidate_exposed_count": stable_count,
        "fragile_candidate_exposed_count": fragile_count,
        "stable_candidate_loss_rate_exposed": stable_loss_rate,
        "exposed_phase_overstrictness_warning_count": int(overstrict),
        "remaining_intrusion_warning_count": remaining_intrusion_count,
        "spectrum_matched_null_intrusion_count": spectrum_count,
        "adversarial_near_duplicate_intrusion_count": adversarial_count,
        "kernel_size_8_artifact_warning_count": kernel_count,
        "proxy_vs_exposed_phase_mismatch_count": mismatch_count,
        "proxy_vs_exposed_phase_mismatch_rate": rate(mismatch_count, case_count),
        "per_case": per_case,
    }


def baseline_clean(metrics: dict[str, Any]) -> bool:
    return (
        metrics["false_accept_warning_exposed_count"] == 0
        and metrics["remaining_intrusion_warning_count"] == 0
        and metrics["stable_candidate_exposed_count"] == metrics["case_count"]
    )


def decision_for_cleanliness(labels: dict[str, str], is_clean: bool, warning_label: str) -> str:
    return labels["leakage_audit_supported_candidate"] if is_clean else labels[warning_label]


def make_variant_distances(
    variant_id: str,
    rows: list[dict[str, Any]],
    columns: dict[str, dict[str, list[float]]],
    overrides: dict[str, list[float]] | None = None,
) -> list[float]:
    distances = []
    for index, row in enumerate(rows):
        fields = phase_for_variant(variant_id, index, row, rows, columns, overrides)
        distances.append(fields["exposed_phase_cyclic_distance"])
    return distances


def ablation_overrides(
    ablated_component: str,
    columns: dict[str, dict[str, list[float]]],
) -> tuple[str, dict[str, list[float]] | None]:
    zeroes = [0.0 for _ in columns["soft"]["profile_distance_raw"]]
    if ablated_component == "remove_all_direct_acceptance_components":
        return "baseline_d1k_construction", {
            field: zeroes
            for field in [
                "profile_distance_raw",
                "control_overlap_rate",
                "decoy_success_rate",
            ]
        }
    if ablated_component == "use_phase_components_not_used_in_acceptance_distance":
        return "use_phase_components_not_used_in_acceptance_distance", None
    field = ablated_component.removeprefix("remove_")
    return "baseline_d1k_construction", {field: zeroes}


def shuffle_overrides(
    shuffle_mode: str,
    rows: list[dict[str, Any]],
    columns: dict[str, dict[str, list[float]]],
    seed: int,
) -> dict[str, list[float]]:
    overrides: dict[str, list[float]] = {}
    groups_decoy = [str(row.get("decoy_family", "")) for row in rows]
    groups_null = [str(row.get("null_family", "")) for row in rows]
    soft = columns["soft"]
    if shuffle_mode == "shuffle_phi_i_source_component":
        overrides["profile_distance_raw"] = deterministic_shuffle(
            soft["profile_distance_raw"], seed
        )
    elif shuffle_mode == "shuffle_phi_j_source_component":
        overrides["profile_distance_collision_penalized"] = deterministic_shuffle(
            soft["profile_distance_collision_penalized"], seed
        )
    elif shuffle_mode == "shuffle_A_component_within_family":
        overrides["profile_distance_raw"] = deterministic_group_shuffle(
            soft["profile_distance_raw"], groups_decoy, seed
        )
    elif shuffle_mode == "shuffle_B_component_within_family":
        overrides["control_overlap_rate"] = deterministic_group_shuffle(
            soft["control_overlap_rate"], groups_null, seed
        )
    elif shuffle_mode == "shuffle_components_across_families":
        for offset, field in enumerate(PHASE_COMPONENTS):
            overrides[field] = deterministic_shuffle(soft[field], seed + offset)
    elif shuffle_mode == "permute_case_id_alignment":
        for offset, field in enumerate(
            ["profile_distance_collision_penalized", "decoy_success_rate", "penalty_gap"]
        ):
            overrides[field] = deterministic_shuffle(soft[field], seed + 10 + offset)
    elif shuffle_mode == "preserve_marginal_distribution_shuffle":
        for offset, field in enumerate(["profile_distance_raw", "control_overlap_rate"]):
            overrides[field] = deterministic_shuffle(soft[field], seed + 20 + offset)
    elif shuffle_mode == "preserve_family_distribution_shuffle":
        for offset, field in enumerate(["profile_distance_raw", "control_overlap_rate"]):
            overrides[field] = deterministic_group_shuffle(soft[field], groups_decoy, seed + 30 + offset)
    return overrides


def build_failure_outputs(
    config: dict[str, Any],
    output_dir: Path,
    reason: str,
    case_count: int,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "output_dir": config["output_dir"],
        "case_count": case_count,
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1f_outputs": True,
        "does_not_modify_d1h_outputs": True,
        "does_not_modify_d1k_outputs": True,
        "does_not_introduce_physical_phase": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "does_not_implement_mastermind": True,
        "input_consistency_passed": False,
        "d1k_false_accept_warning_exposed_count": None,
        "d1k_stable_candidate_exposed_count": None,
        "d1k_remaining_intrusion_warning_count": None,
        "d1k_proxy_vs_exposed_phase_mismatch_rate": None,
        "direct_feature_leakage_warning": False,
        "label_leakage_warning": False,
        "proxy_leakage_warning": False,
        "target_family_leakage_warning": False,
        "threshold_leakage_warning": False,
        "construction_feedback_leakage_warning": False,
        "tautology_warning": False,
        "overclean_result_warning": False,
        "construction_dependence_warning": False,
        "component_ablation_failure_warning": False,
        "shuffled_input_failure_warning": False,
        "family_blind_failure_warning": False,
        "leakage_warning_count": 0,
        "tautology_warning_count": 0,
        "construction_warning_count": 0,
        "audit_supported_candidate_count": 0,
        "mastermind_status": "parked_not_implemented",
        "phase_is_physical": False,
        "phase_is_synthetic_diagnostic": True,
        "generated_files": GENERATED_FILES,
        "claim_boundary": config["metadata"]["claim_boundary"],
        "abort_reason": reason,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (output_dir / "readout.md").write_text(
        "# QSB-ST-COMP01-D1l Synthetic Phase Leakage and Tautology Audit Readout\n\n"
        "## Befund\n\n"
        f"Run aborted defensively: {reason}\n\n"
        "specificity_established: false\n"
        "phase_is_physical: false\n\n"
        "## Interpretation\n\nInput consistency failed; no partial audit is interpreted.\n\n"
        "## Hypothese\n\nA consistent input set may allow leakage and tautology audit.\n\n"
        "## Offene Luecke\n\nNo physical phase, no physical manifold, no specificity.\n\n"
        "## Claim Boundary\n\nD1l does not introduce a physical phase.\n"
        "D1l does not implement Mastermind.\n\n"
        "## Machine-readable status\n\n```yaml\nspecificity_established: false\n```\n",
        encoding="utf-8",
    )
    write_csv(output_dir / "leakage_taxonomy_summary.csv", [], LEAKAGE_FIELDS)
    write_csv(output_dir / "construction_variant_summary.csv", [], CONSTRUCTION_FIELDS)
    write_csv(output_dir / "component_ablation_summary.csv", [], ABLATION_FIELDS)
    write_csv(output_dir / "shuffled_input_summary.csv", [], SHUFFLE_FIELDS)
    write_csv(output_dir / "family_blind_summary.csv", [], FAMILY_BLIND_FIELDS)
    write_csv(output_dir / "threshold_weight_sweep_summary.csv", [], THRESHOLD_FIELDS)
    write_csv(output_dir / "proxy_exposed_mismatch_localization.csv", [], MISMATCH_FIELDS)
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def count_candidate_rows(*row_sets: list[dict[str, Any]]) -> int:
    return sum(
        1
        for rows in row_sets
        for row in rows
        if str(row.get("decision_status", "")).endswith("_candidate")
    )


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# QSB-ST-COMP01-D1l Synthetic Phase Leakage and Tautology Audit Readout",
        "",
        "## Befund",
        "",
        "D1l is a synthetic diagnostic leakage/tautology/construction-dependence audit.",
        f"run_id: {summary['run_id']}",
        f"case_count: {summary['case_count']}",
        f"specificity_established: {str(summary['specificity_established']).lower()}",
        f"d1k_false_accept_warning_exposed_count: {summary['d1k_false_accept_warning_exposed_count']}",
        f"d1k_stable_candidate_exposed_count: {summary['d1k_stable_candidate_exposed_count']}",
        f"d1k_remaining_intrusion_warning_count: {summary['d1k_remaining_intrusion_warning_count']}",
        f"d1k_proxy_vs_exposed_phase_mismatch_rate: {summary['d1k_proxy_vs_exposed_phase_mismatch_rate']}",
        f"direct_feature_leakage_warning: {str(summary['direct_feature_leakage_warning']).lower()}",
        f"label_leakage_warning: {str(summary['label_leakage_warning']).lower()}",
        f"proxy_leakage_warning: {str(summary['proxy_leakage_warning']).lower()}",
        f"target_family_leakage_warning: {str(summary['target_family_leakage_warning']).lower()}",
        f"threshold_leakage_warning: {str(summary['threshold_leakage_warning']).lower()}",
        f"construction_feedback_leakage_warning: {str(summary['construction_feedback_leakage_warning']).lower()}",
        f"tautology_warning: {str(summary['tautology_warning']).lower()}",
        f"overclean_result_warning: {str(summary['overclean_result_warning']).lower()}",
        f"construction_dependence_warning: {str(summary['construction_dependence_warning']).lower()}",
        f"component_ablation_failure_warning: {str(summary['component_ablation_failure_warning']).lower()}",
        f"shuffled_input_failure_warning: {str(summary['shuffled_input_failure_warning']).lower()}",
        f"family_blind_failure_warning: {str(summary['family_blind_failure_warning']).lower()}",
        f"phase_is_synthetic_diagnostic: {str(summary['phase_is_synthetic_diagnostic']).lower()}",
        f"phase_is_physical: {str(summary['phase_is_physical']).lower()}",
        "",
        "D1l does not rerun D1f.",
        "D1l does not modify D1f/D1h/D1k outputs.",
        "D1l does not introduce a physical phase.",
        "D1l does not introduce a physical manifold.",
        "D1l does not introduce a new identity score.",
        "D1l does not implement Mastermind or Knuth role-permutation diagnostics.",
        "",
        "## Interpretation",
        "",
        "The D1k all-clean baseline is treated as audit-triggering, not as specificity.",
        "Leakage warnings, tautology warnings, and construction-dependence warnings are methodological safety signals.",
        "Ablation, shuffle, family-blind, and threshold findings compare hostile variants against the D1k exposed phase baseline.",
        "",
        "## Hypothese",
        "",
        "If the exposed phase survives hostile audits, it may become a stronger synthetic diagnostic coordinate candidate.",
        "If it fails hostile audits, it remains a useful but construction-dependent diagnostic classifier layer.",
        "",
        "## Offene Luecke",
        "",
        "- no real data",
        "- no diagnostic specificity established",
        "- no physical phase reconstruction",
        "- no physical manifold",
        "- no Bridge confirmation",
        "- no Lorentz metric",
        "- no physical time",
        "- no Pauli claim",
        "- Mastermind / Knuth / role-permutation remains parked",
        "",
        "## Claim Boundary",
        "",
        "D1l audits leakage, tautology, construction-dependence, and overclean behavior only.",
        "The exposed phase-like fields are diagnostic synthetic fields.",
        "phase_is_physical remains false.",
        "They are not physical phase reconstruction.",
        "D1l does not introduce a physical phase.",
        "D1l does not introduce a physical manifold.",
        "D1l does not validate a physical Bridge.",
        "D1l does not derive a Lorentz metric.",
        "D1l does not introduce physical time.",
        "D1l does not claim fermionic Pauli exclusion.",
        "D1l does not establish diagnostic specificity.",
        "",
        "## Machine-readable status",
        "",
        "```yaml",
        f"block_id: {summary['block_id']}",
        f"run_id: {summary['run_id']}",
        f"case_count: {summary['case_count']}",
        "specificity_established: false",
        f"overclean_result_warning: {str(summary['overclean_result_warning']).lower()}",
        f"tautology_warning: {str(summary['tautology_warning']).lower()}",
        f"leakage_warning_count: {summary['leakage_warning_count']}",
        f"construction_warning_count: {summary['construction_warning_count']}",
        "phase_is_physical: false",
        "phase_is_synthetic_diagnostic: true",
        "mastermind_status: parked_not_implemented",
        "```",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    config = read_config(Path(args.config))
    run_id = config["run_id"]
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    labels = config["decision_labels"]

    inputs = {name: Path(path) for name, path in config["input_files"].items()}
    d1f_rows = read_csv(inputs["d1f_case_profile_summary"])
    d1h_rows = read_csv(inputs["d1h_cyclic_region_case_summary"])
    d1k_rows = read_csv(inputs["d1k_phase_exposed_case_profile_summary"])
    d1h_summary = read_json(inputs["d1h_summary"])
    d1k_summary = read_json(inputs["d1k_summary"])

    d1f_by_case = {row["case_id"]: row for row in d1f_rows}
    d1h_by_case = {row["case_id"]: row for row in d1h_rows}
    d1k_by_case = {row["case_id"]: row for row in d1k_rows}
    matched_ids = sorted(set(d1f_by_case) & set(d1h_by_case) & set(d1k_by_case))
    input_consistency_passed = len(matched_ids) >= 9000 and len(matched_ids) == int(
        d1k_summary["case_count"]
    )
    if not input_consistency_passed:
        build_failure_outputs(
            config,
            output_dir,
            f"matched case count below threshold or summary mismatch: matched={len(matched_ids)}",
            len(matched_ids),
        )
        return

    rows: list[dict[str, Any]] = []
    for case_id in matched_ids:
        merged = dict(d1f_by_case[case_id])
        merged.update(d1h_by_case[case_id])
        d1k = d1k_by_case[case_id]
        merged["false_accept_warning_proxy"] = d1k.get("false_accept_warning_proxy", "")
        merged["false_accept_warning_exposed"] = d1k.get("false_accept_warning_exposed", "")
        merged["stable_candidate_proxy"] = d1k.get("stable_candidate_proxy", "")
        merged["stable_candidate_exposed"] = d1k.get("stable_candidate_exposed", "")
        merged["fragile_candidate_proxy"] = d1k.get("fragile_candidate_proxy", "")
        merged["fragile_candidate_exposed"] = d1k.get("fragile_candidate_exposed", "")
        merged["baseline_cyclic_phase_proxy_distance"] = d1k.get(
            "baseline_cyclic_phase_proxy_distance", ""
        )
        merged["exposed_phase_cyclic_distance"] = d1k.get(
            "exposed_phase_cyclic_distance", ""
        )
        merged["proxy_vs_exposed_phase_distance_delta"] = d1k.get(
            "proxy_vs_exposed_phase_distance_delta", ""
        )
        merged["phase_construction_inputs"] = d1k.get("phase_construction_inputs", "")
        rows.append(merged)

    columns = prepare_columns(rows)
    case_count = len(rows)
    phase_inputs_text = rows[0].get("phase_construction_inputs", "")
    phase_inputs = set()
    try:
        parsed_inputs = json.loads(phase_inputs_text)
        if isinstance(parsed_inputs, list):
            phase_inputs = {str(item) for item in parsed_inputs}
    except json.JSONDecodeError:
        phase_inputs = set(PHASE_COMPONENTS)
    if not phase_inputs:
        phase_inputs = set(PHASE_COMPONENTS)

    construction_rows: list[dict[str, Any]] = []
    construction_metrics_by_id: dict[str, dict[str, Any]] = {}
    for variant_id in config["audit_families"]["construction_variants"]:
        distances = make_variant_distances(variant_id, rows, columns)
        metrics = compute_acceptance_metrics(rows, distances, config)
        is_clean = baseline_clean(metrics)
        construction_warning = not is_clean
        construction_metrics_by_id[variant_id] = metrics
        construction_rows.append(
            {
                "run_id": run_id,
                "construction_variant_id": variant_id,
                "case_count": metrics["case_count"],
                "false_accept_warning_exposed_count": metrics[
                    "false_accept_warning_exposed_count"
                ],
                "exclusion_success_exposed_rate": metrics["exclusion_success_exposed_rate"],
                "stable_candidate_exposed_count": metrics["stable_candidate_exposed_count"],
                "fragile_candidate_exposed_count": metrics["fragile_candidate_exposed_count"],
                "stable_candidate_loss_rate_exposed": metrics[
                    "stable_candidate_loss_rate_exposed"
                ],
                "exposed_phase_overstrictness_warning_count": metrics[
                    "exposed_phase_overstrictness_warning_count"
                ],
                "remaining_intrusion_warning_count": metrics["remaining_intrusion_warning_count"],
                "proxy_vs_exposed_phase_mismatch_count": metrics[
                    "proxy_vs_exposed_phase_mismatch_count"
                ],
                "proxy_vs_exposed_phase_mismatch_rate": metrics[
                    "proxy_vs_exposed_phase_mismatch_rate"
                ],
                "survives_baseline_like_cleanliness": is_clean,
                "construction_dependence_warning": construction_warning,
                "decision_status": decision_for_cleanliness(
                    labels, is_clean, "construction_dependence_warning"
                ),
                "interpretation_note": (
                    "Construction variant remains all-clean."
                    if is_clean
                    else "Construction variant breaks the D1k all-clean baseline."
                ),
            }
        )

    ablation_rows: list[dict[str, Any]] = []
    for ablation_id in config["audit_families"]["component_ablations"]:
        variant_id, overrides = ablation_overrides(ablation_id, columns)
        distances = make_variant_distances(variant_id, rows, columns, overrides)
        metrics = compute_acceptance_metrics(rows, distances, config)
        survives = baseline_clean(metrics)
        failure = not survives
        ablation_rows.append(
            {
                "run_id": run_id,
                "ablated_component": ablation_id,
                "case_count": metrics["case_count"],
                "false_accept_warning_exposed_count": metrics[
                    "false_accept_warning_exposed_count"
                ],
                "exclusion_success_exposed_rate": metrics["exclusion_success_exposed_rate"],
                "stable_candidate_exposed_count": metrics["stable_candidate_exposed_count"],
                "fragile_candidate_exposed_count": metrics["fragile_candidate_exposed_count"],
                "stable_candidate_loss_rate_exposed": metrics[
                    "stable_candidate_loss_rate_exposed"
                ],
                "remaining_intrusion_warning_count": metrics["remaining_intrusion_warning_count"],
                "survives_ablation": survives,
                "component_ablation_failure_warning": failure,
                "decision_status": decision_for_cleanliness(
                    labels, survives, "component_ablation_failure_warning"
                ),
                "interpretation_note": (
                    "All-clean effect survives component ablation."
                    if survives
                    else "All-clean effect depends on the ablated component set."
                ),
            }
        )

    shuffled_rows: list[dict[str, Any]] = []
    for offset, shuffle_id in enumerate(config["audit_families"]["shuffled_inputs"]):
        seed = SHUFFLE_SEED + offset
        overrides = shuffle_overrides(shuffle_id, rows, columns, seed)
        distances = make_variant_distances(
            "baseline_d1k_construction", rows, columns, overrides
        )
        metrics = compute_acceptance_metrics(rows, distances, config)
        survives = baseline_clean(metrics)
        suspicion = survives
        shuffled_rows.append(
            {
                "run_id": run_id,
                "shuffled_component": shuffle_id,
                "shuffle_mode": shuffle_id,
                "seed": seed,
                "case_count": metrics["case_count"],
                "false_accept_warning_exposed_count": metrics[
                    "false_accept_warning_exposed_count"
                ],
                "stable_candidate_exposed_count": metrics["stable_candidate_exposed_count"],
                "remaining_intrusion_warning_count": metrics["remaining_intrusion_warning_count"],
                "survives_shuffle": survives,
                "shuffled_input_suspicion": suspicion,
                "shuffled_input_failure_warning": suspicion,
                "decision_status": (
                    labels["shuffled_input_failure_warning"]
                    if suspicion
                    else labels["leakage_audit_supported_candidate"]
                ),
                "interpretation_note": (
                    "All-clean effect survives shuffled inputs; this is suspicious."
                    if suspicion
                    else "Shuffling disrupts all-clean behavior; case alignment matters."
                ),
            }
        )

    family_rows: list[dict[str, Any]] = []
    for blind_id in config["audit_families"]["family_blind"]:
        field = blind_id.removeprefix("build_without_")
        family_field_used = field in phase_inputs or (
            blind_id == "build_without_any_control_family_identity_field"
            and bool(phase_inputs & FAMILY_FIELDS)
        )
        survives = not family_field_used
        target_warning = family_field_used
        family_rows.append(
            {
                "run_id": run_id,
                "blind_field_removed": blind_id,
                "family_field_used_in_construction": family_field_used,
                "case_count": case_count,
                "false_accept_warning_exposed_count": d1k_summary[
                    "false_accept_warning_exposed_count"
                ],
                "stable_candidate_exposed_count": d1k_summary[
                    "stable_candidate_exposed_count"
                ],
                "remaining_intrusion_warning_count": d1k_summary[
                    "remaining_intrusion_warning_count"
                ],
                "survives_family_blindness": survives,
                "target_family_leakage_warning": target_warning,
                "decision_status": (
                    labels["target_family_leakage_warning"]
                    if target_warning
                    else (
                        labels["decoy_blind_supported_candidate"]
                        if "decoy" in blind_id
                        else labels["null_family_blind_supported_candidate"]
                        if "null" in blind_id
                        else labels["leakage_audit_supported_candidate"]
                    )
                ),
                "interpretation_note": (
                    "Family identity field is not used by D1k phase construction."
                    if not family_field_used
                    else "Family identity appears in phase construction inputs."
                ),
            }
        )

    threshold_rows: list[dict[str, Any]] = []
    threshold_clean_count = 0
    threshold_total = 0
    baseline_distances = make_variant_distances("baseline_d1k_construction", rows, columns)
    for threshold in config["threshold_weight_sweep"][
        "cyclic_acceptance_distance_thresholds"
    ]:
        for cyclic_weight in config["threshold_weight_sweep"]["cyclic_phase_weights"]:
            profile_weight = max(0.0, 0.80 - float(cyclic_weight))
            metrics = compute_acceptance_metrics(
                rows,
                baseline_distances,
                config,
                threshold=float(threshold),
                cyclic_phase_weight=float(cyclic_weight),
                profile_distance_weight=profile_weight,
                control_overlap_weight=0.10,
                decoy_success_weight=0.10,
            )
            is_clean = baseline_clean(metrics)
            threshold_total += 1
            threshold_clean_count += int(is_clean)
            threshold_rows.append(
                {
                    "run_id": run_id,
                    "threshold_variant_id": f"threshold_{threshold}_phase_weight_{cyclic_weight}",
                    "cyclic_acceptance_distance_threshold": threshold,
                    "cyclic_phase_weight": cyclic_weight,
                    "profile_distance_weight": profile_weight,
                    "control_overlap_weight": 0.10,
                    "decoy_success_weight": 0.10,
                    "case_count": metrics["case_count"],
                    "false_accept_warning_exposed_count": metrics[
                        "false_accept_warning_exposed_count"
                    ],
                    "stable_candidate_exposed_count": metrics[
                        "stable_candidate_exposed_count"
                    ],
                    "remaining_intrusion_warning_count": metrics[
                        "remaining_intrusion_warning_count"
                    ],
                    "threshold_leakage_warning": False,
                    "overclean_result_warning": is_clean,
                    "decision_status": (
                        labels["overclean_result_warning"]
                        if is_clean
                        else labels["threshold_leakage_warning"]
                    ),
                    "interpretation_note": (
                        "Sweep variant remains all-clean; overclean behavior must be audited."
                        if is_clean
                        else "Sweep variant breaks all-clean behavior."
                    ),
                }
            )
    threshold_success_rate = rate(threshold_clean_count, threshold_total) or 0.0
    threshold_leakage_warning = 0.0 < threshold_success_rate < 0.30
    if threshold_leakage_warning:
        for row in threshold_rows:
            row["threshold_leakage_warning"] = True
            if not row["overclean_result_warning"]:
                row["decision_status"] = labels["threshold_leakage_warning"]

    mismatch_rows: list[dict[str, Any]] = []
    for row in rows:
        false_proxy = safe_bool(row.get("false_accept_warning_proxy"))
        false_exposed = safe_bool(row.get("false_accept_warning_exposed"))
        stable_proxy = safe_bool(row.get("stable_candidate_proxy"))
        stable_exposed = safe_bool(row.get("stable_candidate_exposed"))
        mismatch_types = []
        if false_proxy != false_exposed:
            mismatch_types.append("false_accept_warning_mismatch")
        if stable_proxy != stable_exposed:
            mismatch_types.append("stable_candidate_mismatch")
        if not mismatch_types:
            continue
        mismatch_rows.append(
            {
                "run_id": run_id,
                "case_id": row["case_id"],
                "mismatch_type": ";".join(mismatch_types),
                "proxy_vs_exposed_phase_distance_delta": row.get(
                    "proxy_vs_exposed_phase_distance_delta", ""
                ),
                "baseline_cyclic_phase_proxy_distance": row.get(
                    "baseline_cyclic_phase_proxy_distance", ""
                ),
                "exposed_phase_cyclic_distance": row.get(
                    "exposed_phase_cyclic_distance", ""
                ),
                "false_accept_warning_proxy": false_proxy,
                "false_accept_warning_exposed": false_exposed,
                "stable_candidate_proxy": stable_proxy,
                "stable_candidate_exposed": stable_exposed,
                "decoy_family": row.get("decoy_family", ""),
                "null_family": row.get("null_family", ""),
                "kernel_size_label": row.get("kernel_size_label", ""),
                "profile_weight_set_id": row.get("profile_weight_set_id", ""),
                "penalty_weight_set_id": row.get("penalty_weight_set_id", ""),
                "interpretation_note": "Proxy-vs-exposed mismatch case for D1l localization.",
            }
        )
    mismatch_rows.sort(
        key=lambda item: abs(safe_float(item["proxy_vs_exposed_phase_distance_delta"])),
        reverse=True,
    )

    baseline_metrics = construction_metrics_by_id["baseline_d1k_construction"]
    proxy_distances = [
        safe_float(row.get("baseline_cyclic_phase_proxy_distance")) for row in rows
    ]
    exposed_distances = [safe_float(row.get("exposed_phase_cyclic_distance")) for row in rows]
    proxy_exposed_corr = pearson(proxy_distances, exposed_distances)

    direct_feature_leakage_warning = bool(phase_inputs & DIRECT_ACCEPTANCE_COMPONENTS)
    label_leakage_warning = bool(phase_inputs & LABEL_OR_DECISION_FIELDS)
    proxy_leakage_warning = bool(
        (proxy_exposed_corr is not None and abs(proxy_exposed_corr) > 0.95)
        or d1k_summary["proxy_vs_exposed_phase_mismatch_rate"]
        < config["thresholds"]["leakage_warning_mismatch_rate_low"]
    )
    target_family_leakage_warning = bool(phase_inputs & FAMILY_FIELDS)
    construction_feedback_leakage_warning = True
    overclean_result_warning = (
        d1k_summary["false_accept_warning_exposed_count"]
        == config["thresholds"]["overclean_false_accept_count"]
        and d1k_summary["remaining_intrusion_warning_count"]
        == config["thresholds"]["overclean_intrusion_count"]
        and d1k_summary["stable_candidate_exposed_count"] == case_count
    )
    construction_dependence_warning = any(
        row["construction_dependence_warning"] for row in construction_rows
    )
    component_ablation_failure_warning = any(
        row["component_ablation_failure_warning"] for row in ablation_rows
    )
    shuffled_input_failure_warning = any(
        row["shuffled_input_failure_warning"] for row in shuffled_rows
    )
    family_blind_failure_warning = any(
        row["target_family_leakage_warning"] for row in family_rows
    )
    tautology_warning = bool(
        direct_feature_leakage_warning
        or overclean_result_warning
        or component_ablation_failure_warning
    )

    leakage_rows = [
        {
            "run_id": run_id,
            "leakage_risk_type": "direct_feature_leakage",
            "warning": direct_feature_leakage_warning,
            "evidence_metric": "phase_inputs_overlap_acceptance_inputs",
            "evidence_value": sorted(phase_inputs & DIRECT_ACCEPTANCE_COMPONENTS),
            "decision_status": (
                labels["direct_feature_leakage_warning"]
                if direct_feature_leakage_warning
                else labels["leakage_audit_supported_candidate"]
            ),
            "interpretation_note": "D1k phase inputs overlap downstream acceptance inputs.",
        },
        {
            "run_id": run_id,
            "leakage_risk_type": "label_leakage",
            "warning": label_leakage_warning,
            "evidence_metric": "label_fields_in_phase_inputs",
            "evidence_value": sorted(phase_inputs & LABEL_OR_DECISION_FIELDS),
            "decision_status": (
                labels["label_leakage_warning"]
                if label_leakage_warning
                else labels["leakage_audit_supported_candidate"]
            ),
            "interpretation_note": "No classification label should be used for phase construction.",
        },
        {
            "run_id": run_id,
            "leakage_risk_type": "proxy_leakage",
            "warning": proxy_leakage_warning,
            "evidence_metric": "proxy_exposed_correlation",
            "evidence_value": proxy_exposed_corr,
            "decision_status": (
                labels["proxy_leakage_warning"]
                if proxy_leakage_warning
                else labels["leakage_audit_supported_candidate"]
            ),
            "interpretation_note": "Proxy leakage is warned if exposed phase closely tracks proxy.",
        },
        {
            "run_id": run_id,
            "leakage_risk_type": "target_family_leakage",
            "warning": target_family_leakage_warning,
            "evidence_metric": "family_fields_in_phase_inputs",
            "evidence_value": sorted(phase_inputs & FAMILY_FIELDS),
            "decision_status": (
                labels["target_family_leakage_warning"]
                if target_family_leakage_warning
                else labels["leakage_audit_supported_candidate"]
            ),
            "interpretation_note": "Family identity fields should not drive the phase layer.",
        },
        {
            "run_id": run_id,
            "leakage_risk_type": "threshold_leakage",
            "warning": threshold_leakage_warning,
            "evidence_metric": "threshold_success_rate",
            "evidence_value": threshold_success_rate,
            "decision_status": (
                labels["threshold_leakage_warning"]
                if threshold_leakage_warning
                else labels["leakage_audit_supported_candidate"]
            ),
            "interpretation_note": "Threshold leakage is warned for a narrow successful threshold window.",
        },
        {
            "run_id": run_id,
            "leakage_risk_type": "construction_feedback_leakage",
            "warning": construction_feedback_leakage_warning,
            "evidence_metric": "post_d1h_d1i_d1j_design_caution",
            "evidence_value": True,
            "decision_status": labels["construction_feedback_leakage_warning"],
            "interpretation_note": "D1k was designed after known proxy and threshold failures.",
        },
        {
            "run_id": run_id,
            "leakage_risk_type": "overclean_result_warning",
            "warning": overclean_result_warning,
            "evidence_metric": "d1k_all_clean_baseline",
            "evidence_value": {
                "false_accepts": d1k_summary["false_accept_warning_exposed_count"],
                "remaining_intrusions": d1k_summary["remaining_intrusion_warning_count"],
                "stable_candidates": d1k_summary["stable_candidate_exposed_count"],
            },
            "decision_status": (
                labels["overclean_result_warning"]
                if overclean_result_warning
                else labels["leakage_audit_supported_candidate"]
            ),
            "interpretation_note": "The D1k all-clean result itself triggers audit escalation.",
        },
    ]

    leakage_warning_count = sum(1 for row in leakage_rows if row["warning"])
    tautology_warning_count = int(tautology_warning)
    construction_warning_count = sum(
        [
            int(construction_dependence_warning),
            int(component_ablation_failure_warning),
            int(shuffled_input_failure_warning),
            int(family_blind_failure_warning),
            int(threshold_leakage_warning),
        ]
    )
    audit_supported_candidate_count = count_candidate_rows(
        leakage_rows,
        construction_rows,
        ablation_rows,
        shuffled_rows,
        family_rows,
        threshold_rows,
    )

    summary = {
        "block_id": config["block_id"],
        "run_id": run_id,
        "output_dir": config["output_dir"],
        "case_count": case_count,
        "specificity_established": False,
        "does_not_rerun_d1f": True,
        "does_not_modify_d1f_outputs": True,
        "does_not_modify_d1h_outputs": True,
        "does_not_modify_d1k_outputs": True,
        "does_not_introduce_physical_phase": True,
        "does_not_introduce_physical_manifold": True,
        "does_not_introduce_new_identity_score": True,
        "does_not_implement_mastermind": True,
        "input_consistency_passed": True,
        "d1k_false_accept_warning_exposed_count": d1k_summary[
            "false_accept_warning_exposed_count"
        ],
        "d1k_stable_candidate_exposed_count": d1k_summary[
            "stable_candidate_exposed_count"
        ],
        "d1k_remaining_intrusion_warning_count": d1k_summary[
            "remaining_intrusion_warning_count"
        ],
        "d1k_proxy_vs_exposed_phase_mismatch_rate": d1k_summary[
            "proxy_vs_exposed_phase_mismatch_rate"
        ],
        "direct_feature_leakage_warning": direct_feature_leakage_warning,
        "label_leakage_warning": label_leakage_warning,
        "proxy_leakage_warning": proxy_leakage_warning,
        "target_family_leakage_warning": target_family_leakage_warning,
        "threshold_leakage_warning": threshold_leakage_warning,
        "construction_feedback_leakage_warning": construction_feedback_leakage_warning,
        "tautology_warning": tautology_warning,
        "overclean_result_warning": overclean_result_warning,
        "construction_dependence_warning": construction_dependence_warning,
        "component_ablation_failure_warning": component_ablation_failure_warning,
        "shuffled_input_failure_warning": shuffled_input_failure_warning,
        "family_blind_failure_warning": family_blind_failure_warning,
        "leakage_warning_count": leakage_warning_count,
        "tautology_warning_count": tautology_warning_count,
        "construction_warning_count": construction_warning_count,
        "audit_supported_candidate_count": audit_supported_candidate_count,
        "mastermind_status": "parked_not_implemented",
        "phase_is_physical": False,
        "phase_is_synthetic_diagnostic": True,
        "generated_files": GENERATED_FILES,
        "claim_boundary": config["metadata"]["claim_boundary"],
    }

    write_csv(output_dir / "leakage_taxonomy_summary.csv", leakage_rows, LEAKAGE_FIELDS)
    write_csv(
        output_dir / "construction_variant_summary.csv",
        construction_rows,
        CONSTRUCTION_FIELDS,
    )
    write_csv(output_dir / "component_ablation_summary.csv", ablation_rows, ABLATION_FIELDS)
    write_csv(output_dir / "shuffled_input_summary.csv", shuffled_rows, SHUFFLE_FIELDS)
    write_csv(output_dir / "family_blind_summary.csv", family_rows, FAMILY_BLIND_FIELDS)
    write_csv(
        output_dir / "threshold_weight_sweep_summary.csv",
        threshold_rows,
        THRESHOLD_FIELDS,
    )
    write_csv(
        output_dir / "proxy_exposed_mismatch_localization.csv",
        mismatch_rows,
        MISMATCH_FIELDS,
    )
    (output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_readout(output_dir / "readout.md", summary)
    (output_dir / "resolved_config.json").write_text(
        json.dumps(config, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
