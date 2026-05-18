#!/usr/bin/env python3
"""
QSB-ST-LIC01 tau/epsilon phase-response minimal runner.

Synthetic diagnostic runner only. It does not construct physical time,
proper time, a Lorentzian metric, or empirical validation.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np
import yaml

DEFAULT_CONFIG = Path("data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml")
CONTROL_FAMILIES = [
    "structured_local_phase_response",
    "global_phase_shift",
    "random_phase",
    "amplitude_preserved_phase_randomized",
    "label_shuffle",
]
SPECIFICITY_CONTROL_FAMILIES = [
    "global_phase_shift",
    "random_phase",
    "amplitude_preserved_phase_randomized",
    "label_shuffle",
]
STRUCTURED_REFERENCE_FAMILY = "structured_local_phase_response"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run QSB-ST-LIC01 synthetic tau/epsilon phase-response diagnostic."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=None)
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)
    if not isinstance(cfg, dict):
        raise ValueError(f"Config did not parse to a dictionary: {path}")
    return cfg


def require_keys(cfg: Dict[str, Any], keys: Iterable[str]) -> None:
    missing = [key for key in keys if key not in cfg]
    if missing:
        raise ValueError(f"Missing required top-level config keys: {missing}")


def validate_epsilon_values(epsilon_values: List[float]) -> List[float]:
    eps = [float(value) for value in epsilon_values]
    if 0.0 not in eps:
        raise ValueError("epsilon_values must include 0.0")
    if sorted(eps) != eps:
        raise ValueError("epsilon_values must be sorted")
    for value in eps:
        if value != 0.0 and -value not in eps:
            raise ValueError(f"epsilon_values must be symmetric; missing {-value}")
    return eps


def build_synthetic_kernel(seed: int) -> Tuple[List[str], np.ndarray]:
    """Build a small deterministic complex reference kernel."""
    rng = np.random.default_rng(seed)
    node_ids = [f"N_{idx:02d}" for idx in range(8)]
    n = len(node_ids)
    angles = np.linspace(0.0, 2.0 * math.pi, n, endpoint=False)
    kernel = np.zeros((n, n), dtype=np.complex128)

    for i in range(n):
        for j in range(n):
            circular_distance = min(abs(i - j), n - abs(i - j))
            amplitude = math.exp(-0.55 * circular_distance)
            phase = angles[i] - angles[j]
            kernel[i, j] = amplitude * np.exp(1j * phase)

    # Tiny deterministic real texture breaks perfect degeneracy without hidden data.
    texture = rng.normal(loc=0.0, scale=0.015, size=(n, n))
    texture = (texture + texture.T) / 2.0
    kernel = kernel + texture.astype(np.complex128)
    np.fill_diagonal(kernel, 1.0 + 0.0j)
    return node_ids, kernel


def local_phase_perturbation(kernel: np.ndarray, source_idx: int, epsilon: float) -> np.ndarray:
    """Apply a local source-centered phase perturbation."""
    perturbed = kernel.copy()
    phase = np.exp(1j * epsilon)
    perturbed[source_idx, :] = perturbed[source_idx, :] * phase
    perturbed[:, source_idx] = perturbed[:, source_idx] * np.conj(phase)
    perturbed[source_idx, source_idx] = kernel[source_idx, source_idx]
    return perturbed


def global_phase_shift(kernel: np.ndarray, epsilon: float) -> np.ndarray:
    """Apply a uniform phase factor to the whole synthetic kernel."""
    return kernel * np.exp(1j * epsilon)


def random_phase_perturbation(
    kernel: np.ndarray,
    source_idx: int,
    epsilon: float,
    random_phase_basis: np.ndarray,
) -> np.ndarray:
    """Apply a deterministic source-indexed random phase perturbation."""
    phase_field = random_phase_basis[source_idx]
    return kernel * np.exp(1j * epsilon * phase_field)


def amplitude_preserved_phase_randomized(
    kernel: np.ndarray,
    source_idx: int,
    epsilon: float,
    randomized_phase_basis: np.ndarray,
) -> np.ndarray:
    """Preserve amplitudes while applying a deterministic randomized phase field."""
    amplitude = np.abs(kernel)
    base_phase = np.angle(kernel)
    phase_field = randomized_phase_basis[source_idx]
    return amplitude * np.exp(1j * (base_phase + epsilon * phase_field))


def label_shuffle_perturbation(
    kernel: np.ndarray,
    source_idx: int,
    epsilon: float,
    permutation: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, int]:
    """Apply the local perturbation after a deterministic label permutation."""
    shuffled_kernel = kernel[np.ix_(permutation, permutation)]
    perturbed = local_phase_perturbation(shuffled_kernel, source_idx, epsilon)
    target_permutation = np.arange(len(permutation))
    return shuffled_kernel, perturbed, int(target_permutation[source_idx])


def target_observable(kernel: np.ndarray, target_idx: int) -> np.ndarray:
    """Return concatenated real/imag row+column observable around target."""
    row = kernel[target_idx, :]
    col = kernel[:, target_idx]
    complex_values = np.concatenate([row, col])
    return np.concatenate([complex_values.real, complex_values.imag])


def response_value(
    baseline_kernel: np.ndarray,
    perturbed_kernel: np.ndarray,
    target_idx: int,
    norm_family: str,
) -> float:
    before = target_observable(baseline_kernel, target_idx)
    after = target_observable(perturbed_kernel, target_idx)
    delta = after - before
    if norm_family == "l2":
        return float(np.linalg.norm(delta, ord=2))
    if norm_family == "l1":
        return float(np.linalg.norm(delta, ord=1))
    if norm_family == "linf":
        return float(np.linalg.norm(delta, ord=np.inf))
    raise ValueError(f"Unsupported response_norm: {norm_family}")


def build_control_perturbation(
    control_family: str,
    baseline_kernel: np.ndarray,
    source_idx: int,
    target_idx: int,
    epsilon: float,
    random_phase_basis: np.ndarray,
    randomized_phase_basis: np.ndarray,
    label_permutation: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, int]:
    response_baseline = baseline_kernel
    response_target_idx = target_idx

    if control_family == "structured_local_phase_response":
        perturbed = local_phase_perturbation(baseline_kernel, source_idx, epsilon)
    elif control_family == "global_phase_shift":
        perturbed = global_phase_shift(baseline_kernel, epsilon)
    elif control_family == "random_phase":
        perturbed = random_phase_perturbation(
            baseline_kernel,
            source_idx,
            epsilon,
            random_phase_basis,
        )
    elif control_family == "amplitude_preserved_phase_randomized":
        perturbed = amplitude_preserved_phase_randomized(
            baseline_kernel,
            source_idx,
            epsilon,
            randomized_phase_basis,
        )
    elif control_family == "label_shuffle":
        response_baseline = baseline_kernel[np.ix_(label_permutation, label_permutation)]
        perturbed = local_phase_perturbation(response_baseline, source_idx, epsilon)
    else:
        raise ValueError(f"Unsupported control family: {control_family}")

    return response_baseline, perturbed, response_target_idx


def estimate_global_phase_angle(matrix: np.ndarray, eta: float) -> Tuple[float, str]:
    mask = np.abs(matrix) > eta
    if not bool(np.any(mask)):
        return 0.0, "phase_angle_degenerate"
    phase_sum = np.sum(matrix[mask])
    if abs(phase_sum) <= eta:
        return 0.0, "phase_angle_degenerate"
    return float(np.angle(phase_sum)), "phase_angle_estimated"


def globally_center_matrix(matrix: np.ndarray, eta: float) -> Tuple[np.ndarray, float, str, float]:
    angle, status = estimate_global_phase_angle(matrix, eta)
    centered = matrix * np.exp(-1j * angle)
    norm_delta = float(np.linalg.norm(centered - matrix, ord="fro"))
    return centered, angle, status, norm_delta


def normalize(values: np.ndarray, eta: float) -> np.ndarray:
    max_abs = float(np.max(np.abs(values))) if values.size else 0.0
    return values / (max_abs + eta)


def minmax(values: np.ndarray, eta: float) -> np.ndarray:
    if values.size == 0:
        return values
    vmin = float(np.min(values))
    vmax = float(np.max(values))
    return (values - vmin) / (vmax - vmin + eta)


def central_slope(response_by_epsilon: Dict[float, float], h: float) -> float:
    if h not in response_by_epsilon or -h not in response_by_epsilon:
        raise ValueError(f"central slope requires epsilon +/- {h}")
    return float((response_by_epsilon[h] - response_by_epsilon[-h]) / (2.0 * h))


def trapezoid_integral(eps: List[float], values: List[float]) -> float:
    y_values = np.asarray(values, dtype=float)
    x_values = np.asarray(eps, dtype=float)
    if hasattr(np, "trapezoid"):
        return float(np.trapezoid(y_values, x_values))
    return float(np.trapz(y_values, x_values))


def summarize_pair_response(
    values: Dict[float, float],
    epsilon_values: List[float],
    finite_difference_epsilon: float,
    eta: float,
) -> Tuple[float, float, float, float]:
    slope = central_slope(values, finite_difference_epsilon)
    positive_small_response = values[finite_difference_epsilon]
    rho_tau = float(positive_small_response / (abs(finite_difference_epsilon) + eta))
    integral = trapezoid_integral(epsilon_values, [values[eps] for eps in epsilon_values])
    peak_epsilon = max(epsilon_values, key=lambda eps: values[eps])
    return slope, integral, float(peak_epsilon), rho_tau


def control_status_label(control_family: str, mean_ratio: float, max_ratio: float) -> str:
    if control_family == STRUCTURED_REFERENCE_FAMILY:
        return "structured_reference"
    if mean_ratio >= 0.9 or max_ratio >= 0.9:
        return "control_close_to_structured_warning"
    if mean_ratio <= 0.25 and max_ratio <= 0.25:
        return "control_lower_than_structured"
    return "control_computed"


def pearson_correlation(x_values: np.ndarray, y_values: np.ndarray) -> float | None:
    if x_values.size == 0 or y_values.size == 0:
        return None
    if float(np.std(x_values)) == 0.0 or float(np.std(y_values)) == 0.0:
        return None
    value = float(np.corrcoef(x_values, y_values)[0, 1])
    if not math.isfinite(value):
        return None
    return value


def rank_desc_by_pair(rows: List[Dict[str, Any]], value_key: str) -> Dict[Tuple[str, str], int]:
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            -float(row[value_key]),
            str(row["source_id"]),
            str(row["target_id"]),
        ),
    )
    return {
        (str(row["source_id"]), str(row["target_id"])): rank
        for rank, row in enumerate(sorted_rows, start=1)
    }


def family_warning_text(
    family: str,
    specificity_warning_status: str,
    small_kernel_audit_status: str,
) -> str:
    if family == STRUCTURED_REFERENCE_FAMILY:
        return "structured reference row; no specificity is claimed by this audit"
    if family == "label_shuffle":
        return "small synthetic system ambiguity; diagnostic specificity not established"
    if specificity_warning_status in {
        "control_mean_exceeds_reference_warning",
        "control_mean_close_to_reference_warning",
    }:
        return "diagnostic specificity not established"
    if small_kernel_audit_status == "small_kernel_caution":
        return "small-kernel caution; control mean lower than reference in this audit"
    return "control mean lower than reference in this audit"


def specificity_status_label(
    control_family: str,
    mean_ratio: float,
    max_ratio: float,
    rank_separation_score: float,
) -> str:
    if mean_ratio > 1.0 or max_ratio > 1.0:
        return "control_exceeds_reference_warning"
    if control_family == "label_shuffle":
        return "small_kernel_ambiguity_warning"
    if mean_ratio >= 0.9 or max_ratio >= 0.9:
        return "control_close_to_reference_warning"
    if 0.4 <= rank_separation_score <= 0.6:
        return "specificity_weak_or_inconclusive"
    if mean_ratio < 0.5 and max_ratio < 0.8 and rank_separation_score > 0.75:
        return "specificity_supported_in_tested_controls"
    return "specificity_weak_or_inconclusive"


def build_observable_normalization_audit(
    control_pair_values: Dict[str, Dict[Tuple[str, str], Dict[str, float]]],
    node_ids: List[str],
    normalization_family: str,
    eta: float,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]]]:
    structured_values = control_pair_values[STRUCTURED_REFERENCE_FAMILY]
    structured_mean = float(
        np.mean([value["rho_tau"] for value in structured_values.values()])
    )

    summary_rows: List[Dict[str, Any]] = []
    raw_control_rows: List[Dict[str, Any]] = []
    rank_change_rows: List[Dict[str, Any]] = []
    warning_rows: List[Dict[str, Any]] = []

    for family in CONTROL_FAMILIES:
        family_values = control_pair_values[family]
        family_rows = [
            {
                "family": family,
                "source_id": source_id,
                "target_id": target_id,
                "rho_tau_raw": float(family_values[(source_id, target_id)]["rho_tau"]),
                "tau_rel_candidate": float(family_values[(source_id, target_id)]["tau_rel_candidate"]),
            }
            for source_id in node_ids
            for target_id in node_ids
        ]
        raw_ranks = rank_desc_by_pair(family_rows, "rho_tau_raw")
        tau_ranks = rank_desc_by_pair(family_rows, "tau_rel_candidate")
        rho_array = np.asarray([row["rho_tau_raw"] for row in family_rows], dtype=float)
        tau_array = np.asarray([row["tau_rel_candidate"] for row in family_rows], dtype=float)
        raw_rank_array = np.asarray(list(raw_ranks.values()), dtype=float)

        if family == STRUCTURED_REFERENCE_FAMILY:
            specificity_warning_status = "structured_reference"
        else:
            rho_mean = float(np.mean(rho_array))
            if rho_mean >= structured_mean:
                specificity_warning_status = "control_mean_exceeds_reference_warning"
            elif rho_mean >= 0.9 * structured_mean:
                specificity_warning_status = "control_mean_close_to_reference_warning"
            else:
                specificity_warning_status = "control_mean_lower_than_reference"

        if family == "global_phase_shift":
            if float(np.mean(rho_array)) >= 0.9 * structured_mean:
                global_phase_audit_status = "global_phase_sensitive_warning"
            else:
                global_phase_audit_status = "global_phase_not_dominant_in_this_audit"
        else:
            global_phase_audit_status = "not_applicable"

        if family == "label_shuffle":
            small_kernel_audit_status = "small_kernel_label_shuffle_ambiguous"
        elif len(family_rows) <= 64:
            small_kernel_audit_status = "small_kernel_caution"
        else:
            small_kernel_audit_status = "kernel_size_not_flagged"

        warning = family_warning_text(
            family=family,
            specificity_warning_status=specificity_warning_status,
            small_kernel_audit_status=small_kernel_audit_status,
        )

        top_pair = min(
            family_rows,
            key=lambda row: (
                -float(row["rho_tau_raw"]),
                str(row["source_id"]),
                str(row["target_id"]),
            ),
        )
        summary_rows.append(
            {
                "family": family,
                "pair_count": len(family_rows),
                "rho_tau_raw_min": f"{float(np.min(rho_array)):.12g}",
                "rho_tau_raw_max": f"{float(np.max(rho_array)):.12g}",
                "rho_tau_raw_mean": f"{float(np.mean(rho_array)):.12g}",
                "rho_tau_raw_median": f"{float(np.median(rho_array)):.12g}",
                "rho_tau_raw_std": f"{float(np.std(rho_array)):.12g}",
                "rho_tau_raw_q25": f"{float(np.quantile(rho_array, 0.25)):.12g}",
                "rho_tau_raw_q75": f"{float(np.quantile(rho_array, 0.75)):.12g}",
                "tau_rel_min": f"{float(np.min(tau_array)):.12g}",
                "tau_rel_max": f"{float(np.max(tau_array)):.12g}",
                "tau_rel_mean": f"{float(np.mean(tau_array)):.12g}",
                "tau_rel_median": f"{float(np.median(tau_array)):.12g}",
                "tau_rel_std": f"{float(np.std(tau_array)):.12g}",
                "normalization_family": normalization_family,
                "rank_mean": f"{float(np.mean(raw_rank_array)):.12g}",
                "rank_median": f"{float(np.median(raw_rank_array)):.12g}",
                "rank_top_pair": f"{top_pair['source_id']}->{top_pair['target_id']}",
                "global_phase_audit_status": global_phase_audit_status,
                "small_kernel_audit_status": small_kernel_audit_status,
                "specificity_warning_status": specificity_warning_status,
                "warning": warning,
            }
        )

        if specificity_warning_status in {
            "control_mean_exceeds_reference_warning",
            "control_mean_close_to_reference_warning",
        }:
            warning_rows.append(
                {
                    "warning_type": specificity_warning_status,
                    "family": family,
                    "source_id": "",
                    "target_id": "",
                    "rho_tau_raw": f"{float(np.mean(rho_array)):.12g}",
                    "tau_rel_candidate": f"{float(np.mean(tau_array)):.12g}",
                    "detail": warning,
                }
            )
        if family == "label_shuffle":
            warning_rows.append(
                {
                    "warning_type": "small_kernel_label_shuffle_ambiguous",
                    "family": family,
                    "source_id": "",
                    "target_id": "",
                    "rho_tau_raw": f"{float(np.mean(rho_array)):.12g}",
                    "tau_rel_candidate": f"{float(np.mean(tau_array)):.12g}",
                    "detail": "label-shuffle control remains ambiguous in the current 8-node synthetic kernel",
                }
            )

        for row in family_rows:
            pair_key = (str(row["source_id"]), str(row["target_id"]))
            raw_rank = raw_ranks[pair_key]
            tau_rank = tau_ranks[pair_key]
            rank_delta = tau_rank - raw_rank
            rank_delta_abs = abs(rank_delta)
            rank_flip_warning = rank_delta_abs >= 16
            status = "observable_normalization_audit_pair_computed"
            raw_control_rows.append(
                {
                    "family": family,
                    "source_id": row["source_id"],
                    "target_id": row["target_id"],
                    "rho_tau_raw": f"{row['rho_tau_raw']:.12g}",
                    "tau_rel_candidate": f"{row['tau_rel_candidate']:.12g}",
                    "raw_rank_desc": raw_rank,
                    "tau_rank_desc": tau_rank,
                    "rank_delta": rank_delta,
                    "normalization_family": normalization_family,
                    "status": status,
                }
            )
            rank_change_rows.append(
                {
                    "family": family,
                    "source_id": row["source_id"],
                    "target_id": row["target_id"],
                    "rho_tau_raw": f"{row['rho_tau_raw']:.12g}",
                    "tau_rel_candidate": f"{row['tau_rel_candidate']:.12g}",
                    "raw_rank_desc": raw_rank,
                    "tau_rank_desc": tau_rank,
                    "rank_delta": rank_delta,
                    "rank_delta_abs": rank_delta_abs,
                    "rank_flip_warning": str(rank_flip_warning).lower(),
                    "status": status,
                }
            )
            if rank_flip_warning:
                warning_rows.append(
                    {
                        "warning_type": "normalization_rank_flip_warning",
                        "family": family,
                        "source_id": row["source_id"],
                        "target_id": row["target_id"],
                        "rho_tau_raw": f"{row['rho_tau_raw']:.12g}",
                        "tau_rel_candidate": f"{row['tau_rel_candidate']:.12g}",
                        "detail": f"rank_delta_abs={rank_delta_abs}",
                    }
                )

    return summary_rows, raw_control_rows, rank_change_rows, warning_rows


def global_phase_warning_after_label(original_mean: float, centered_mean: float, eta: float) -> str:
    if centered_mean < 0.5 * original_mean:
        return "global_phase_warning_reduced"
    if centered_mean >= 0.9 * original_mean:
        return "global_phase_warning_persists"
    if abs(original_mean) <= eta and abs(centered_mean) <= eta:
        return "global_phase_warning_inconclusive"
    return "global_phase_warning_inconclusive"


def probe_status_label(
    family: str,
    warning_after: str,
    original_mean: float,
    centered_mean: float,
    structured_centered_mean: float,
    eta: float,
) -> str:
    if centered_mean < 0.1 * original_mean and family == STRUCTURED_REFERENCE_FAMILY:
        return "structured_response_collapsed_warning"
    if family == "global_phase_shift" and warning_after == "global_phase_warning_reduced":
        return "global_phase_warning_reduced_probe"
    if family == "global_phase_shift" and warning_after == "global_phase_warning_persists":
        return "global_phase_warning_persists_probe"
    if family != STRUCTURED_REFERENCE_FAMILY and centered_mean >= 0.9 * structured_centered_mean:
        return "control_still_exceeds_reference_warning"
    if abs(centered_mean) <= eta:
        return "phase_angle_degenerate_warning"
    return "probe_computed"


def specificity_after_centering_label(
    family: str,
    probe_status: str,
    warning_after: str,
) -> str:
    if probe_status == "structured_response_collapsed_warning":
        return "structured_response_global_phase_dominated_warning"
    if family == "global_phase_shift" and warning_after == "global_phase_warning_reduced":
        return "specificity_not_established_global_phase_reduced_only"
    return "specificity_not_established"


def build_global_phase_invariant_probe(
    node_ids: List[str],
    baseline_kernel: np.ndarray,
    epsilon_values: List[float],
    finite_difference_epsilon: float,
    eta: float,
    norm_family: str,
    random_phase_basis: np.ndarray,
    randomized_phase_basis: np.ndarray,
    label_permutation: np.ndarray,
    control_pair_values: Dict[str, Dict[Tuple[str, str], Dict[str, float]]],
    global_phase_audit_status: str,
    specificity_status_labels: Dict[str, str],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, str], List[str], bool]:
    centered_pair_values: Dict[str, Dict[Tuple[str, str], Dict[str, float]]] = {}
    diagnostics_rows: List[Dict[str, Any]] = []

    for family in CONTROL_FAMILIES:
        centered_pair_values[family] = {}
        family_centered_inverse: List[float] = []
        family_pair_records: List[Dict[str, Any]] = []

        for source_idx, source_id in enumerate(node_ids):
            for target_idx, target_id in enumerate(node_ids):
                centered_response_by_epsilon: Dict[float, float] = {}
                original_response_by_epsilon: Dict[float, float] = {}
                diagnostic_accumulator: Dict[float, Dict[str, List[float]]] = {}

                for epsilon in epsilon_values:
                    response_baseline, perturbed, response_target_idx = build_control_perturbation(
                        control_family=family,
                        baseline_kernel=baseline_kernel,
                        source_idx=source_idx,
                        target_idx=target_idx,
                        epsilon=epsilon,
                        random_phase_basis=random_phase_basis,
                        randomized_phase_basis=randomized_phase_basis,
                        label_permutation=label_permutation,
                    )
                    original_response = response_value(
                        response_baseline,
                        perturbed,
                        response_target_idx,
                        norm_family,
                    )
                    centered_baseline, baseline_angle, baseline_status, baseline_norm_delta = globally_center_matrix(
                        response_baseline,
                        eta,
                    )
                    centered_perturbed, perturbed_angle, perturbed_status, perturbed_norm_delta = globally_center_matrix(
                        perturbed,
                        eta,
                    )
                    centered_response = response_value(
                        centered_baseline,
                        centered_perturbed,
                        response_target_idx,
                        norm_family,
                    )

                    original_response_by_epsilon[epsilon] = original_response
                    centered_response_by_epsilon[epsilon] = centered_response
                    values = diagnostic_accumulator.setdefault(
                        epsilon,
                        {
                            "angle": [],
                            "norm_delta": [],
                            "before": [],
                            "after": [],
                            "degenerate": [],
                        },
                    )
                    values["angle"].append(float(perturbed_angle - baseline_angle))
                    values["norm_delta"].append(float((baseline_norm_delta + perturbed_norm_delta) / 2.0))
                    values["before"].append(original_response)
                    values["after"].append(centered_response)
                    values["degenerate"].append(
                        1.0
                        if baseline_status == "phase_angle_degenerate"
                        or perturbed_status == "phase_angle_degenerate"
                        else 0.0
                    )

                _, _, _, rho_tau_centered = summarize_pair_response(
                    centered_response_by_epsilon,
                    epsilon_values,
                    finite_difference_epsilon,
                    eta,
                )
                family_centered_inverse.append(1.0 / (rho_tau_centered + eta))
                pair_key = (source_id, target_id)
                family_pair_records.append(
                    {
                        "source_id": source_id,
                        "target_id": target_id,
                        "rho_tau_centered": rho_tau_centered,
                    }
                )

                if source_idx == 0 and target_idx == 0:
                    for epsilon, values in diagnostic_accumulator.items():
                        status = "global_phase_centering_diagnostic_computed"
                        if any(value > 0.0 for value in values["degenerate"]):
                            status = "phase_angle_degenerate_warning"
                        diagnostics_rows.append(
                            {
                                "family": family,
                                "epsilon": f"{epsilon:.12g}",
                                "global_phase_angle_estimate": f"{float(np.mean(values['angle'])):.12g}",
                                "phase_centering_norm_delta": f"{float(np.mean(values['norm_delta'])):.12g}",
                                "response_before_centering": f"{float(np.mean(values['before'])):.12g}",
                                "response_after_centering": f"{float(np.mean(values['after'])):.12g}",
                                "status": status,
                            }
                        )

        tau_rel_centered = minmax(np.asarray(family_centered_inverse, dtype=float), eta=eta)
        for idx, record in enumerate(family_pair_records):
            pair_key = (str(record["source_id"]), str(record["target_id"]))
            centered_pair_values[family][pair_key] = {
                "rho_tau_centered": float(record["rho_tau_centered"]),
                "tau_rel_centered": float(tau_rel_centered[idx]),
            }

    structured_centered_mean = float(
        np.mean([
            value["rho_tau_centered"]
            for value in centered_pair_values[STRUCTURED_REFERENCE_FAMILY].values()
        ])
    )
    summary_rows: List[Dict[str, Any]] = []
    pairwise_rows: List[Dict[str, Any]] = []
    status_labels: Dict[str, str] = {}
    warnings: List[str] = []
    global_phase_warning_reduced = False

    for family in CONTROL_FAMILIES:
        original_values = control_pair_values[family]
        centered_values = centered_pair_values[family]
        original_rho_array = np.asarray(
            [value["rho_tau"] for value in original_values.values()],
            dtype=float,
        )
        centered_rho_array = np.asarray(
            [value["rho_tau_centered"] for value in centered_values.values()],
            dtype=float,
        )
        original_mean = float(np.mean(original_rho_array))
        centered_mean = float(np.mean(centered_rho_array))
        mean_delta = centered_mean - original_mean
        mean_ratio = float(centered_mean / (original_mean + eta))

        if family == "global_phase_shift":
            warning_before = global_phase_audit_status
            warning_after = global_phase_warning_after_label(original_mean, centered_mean, eta)
            global_phase_warning_reduced = warning_after == "global_phase_warning_reduced"
        else:
            warning_before = "not_applicable"
            warning_after = "family_specific_probe_reported"

        specificity_before = (
            "structured_reference"
            if family == STRUCTURED_REFERENCE_FAMILY
            else specificity_status_labels.get(family, "specificity_not_established")
        )
        probe_status = probe_status_label(
            family=family,
            warning_after=warning_after,
            original_mean=original_mean,
            centered_mean=centered_mean,
            structured_centered_mean=structured_centered_mean,
            eta=eta,
        )
        specificity_after = specificity_after_centering_label(
            family=family,
            probe_status=probe_status,
            warning_after=warning_after,
        )
        warning = ""
        if probe_status != "probe_computed":
            warning = "probe warning retained; diagnostic specificity not established"
        elif family != STRUCTURED_REFERENCE_FAMILY:
            warning = "control probe reported; diagnostic specificity not established"
        else:
            warning = "structured reference probe reported; no specificity claim"

        status_labels[family] = probe_status
        if warning:
            warnings.append(f"{family}: {warning}")

        summary_rows.append(
            {
                "family": family,
                "pair_count": len(original_values),
                "rho_tau_original_mean": f"{original_mean:.12g}",
                "rho_tau_centered_mean": f"{centered_mean:.12g}",
                "rho_tau_mean_delta": f"{mean_delta:.12g}",
                "rho_tau_mean_ratio": f"{mean_ratio:.12g}",
                "global_phase_warning_before": warning_before,
                "global_phase_warning_after": warning_after,
                "specificity_status_before": specificity_before,
                "specificity_status_after": specificity_after,
                "probe_status": probe_status,
                "warning": warning,
            }
        )

        for source_id in node_ids:
            for target_id in node_ids:
                pair_key = (source_id, target_id)
                original = original_values[pair_key]
                centered = centered_values[pair_key]
                rho_delta = centered["rho_tau_centered"] - original["rho_tau"]
                tau_delta = centered["tau_rel_centered"] - original["tau_rel_candidate"]
                pairwise_rows.append(
                    {
                        "family": family,
                        "source_id": source_id,
                        "target_id": target_id,
                        "rho_tau_original": f"{original['rho_tau']:.12g}",
                        "rho_tau_centered": f"{centered['rho_tau_centered']:.12g}",
                        "rho_tau_delta": f"{rho_delta:.12g}",
                        "tau_rel_original": f"{original['tau_rel_candidate']:.12g}",
                        "tau_rel_centered": f"{centered['tau_rel_centered']:.12g}",
                        "tau_rel_delta": f"{tau_delta:.12g}",
                        "global_phase_centering_applied": "true",
                        "status": "global_phase_invariant_probe_pair_computed",
                    }
                )

    return (
        summary_rows,
        pairwise_rows,
        diagnostics_rows,
        status_labels,
        warnings,
        global_phase_warning_reduced,
    )


RESIDUAL_CONTROL_FAMILIES = [
    "random_phase",
    "amplitude_preserved_phase_randomized",
    "label_shuffle",
]


def residual_warning_type(control_family: str, mean_ratio: float) -> str:
    if control_family == "random_phase":
        if mean_ratio >= 1.0:
            return "random_phase_exceeds_reference_warning"
        if mean_ratio >= 0.9:
            return "random_phase_close_to_reference_warning"
        return "random_phase_below_reference_but_specificity_still_open"
    if control_family == "amplitude_preserved_phase_randomized":
        if mean_ratio >= 1.0:
            return "amplitude_preserved_phase_randomized_exceeds_reference_warning"
        if mean_ratio >= 0.9:
            return "amplitude_preserved_phase_randomized_close_to_reference_warning"
        return "amplitude_preserved_phase_randomized_below_reference_but_specificity_still_open"
    if control_family == "label_shuffle":
        if mean_ratio >= 1.0:
            return "label_shuffle_exceeds_reference_warning"
        if mean_ratio >= 0.9:
            return "label_shuffle_close_to_reference_warning"
        return "label_shuffle_below_reference_but_small_kernel_ambiguous"
    raise ValueError(f"Unsupported residual control family: {control_family}")


def residual_likely_failure_mode(control_family: str) -> str:
    if control_family == "random_phase":
        return "generic_phase_sensitivity_or_seed_instability"
    if control_family == "amplitude_preserved_phase_randomized":
        return "amplitude_support_dominance_or_phase_organization_not_separating"
    if control_family == "label_shuffle":
        return "small_kernel_identity_or_distributional_ambiguity"
    raise ValueError(f"Unsupported residual control family: {control_family}")


def residual_recommended_next_probe(control_family: str) -> str:
    if control_family == "random_phase":
        return "seed_sensitivity_sweep"
    if control_family == "amplitude_preserved_phase_randomized":
        return "magnitude_phase_component_separation"
    if control_family == "label_shuffle":
        return "larger_kernel_or_multiple_label_shuffle_stability"
    raise ValueError(f"Unsupported residual control family: {control_family}")


def centered_probe_values_by_family(
    global_phase_probe_pairwise_rows: List[Dict[str, Any]],
) -> Dict[str, Dict[Tuple[str, str], Dict[str, float]]]:
    values: Dict[str, Dict[Tuple[str, str], Dict[str, float]]] = {}
    for row in global_phase_probe_pairwise_rows:
        family = str(row["family"])
        pair_key = (str(row["source_id"]), str(row["target_id"]))
        values.setdefault(family, {})[pair_key] = {
            "rho_tau_centered": float(row["rho_tau_centered"]),
            "tau_rel_centered": float(row["tau_rel_centered"]),
        }
    return values


def top_quartile_keys(pair_values: Dict[Tuple[str, str], Dict[str, float]]) -> set[Tuple[str, str]]:
    sorted_items = sorted(
        pair_values.items(),
        key=lambda item: (-float(item[1]["rho_tau_centered"]), item[0][0], item[0][1]),
    )
    count = max(1, len(sorted_items) // 4)
    return {pair_key for pair_key, _ in sorted_items[:count]}


def family_correlation_status(correlation: float | None, rank_overlap_top_quartile: float) -> str:
    if correlation is None:
        return "correlation_degenerate_warning"
    if correlation >= 0.8 or rank_overlap_top_quartile >= 0.5:
        return "high_pattern_mimicry_warning"
    if correlation >= 0.4:
        return "moderate_pattern_similarity"
    return "low_pattern_similarity"


def build_residual_control_warning_analysis(
    global_phase_probe_pairwise_rows: List[Dict[str, Any]],
    node_ids: List[str],
    eta: float,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, str], List[str]]:
    centered_values = centered_probe_values_by_family(global_phase_probe_pairwise_rows)
    structured_values = centered_values[STRUCTURED_REFERENCE_FAMILY]
    structured_rho = np.asarray(
        [
            structured_values[(source_id, target_id)]["rho_tau_centered"]
            for source_id in node_ids
            for target_id in node_ids
        ],
        dtype=float,
    )
    structured_tau = np.asarray(
        [
            structured_values[(source_id, target_id)]["tau_rel_centered"]
            for source_id in node_ids
            for target_id in node_ids
        ],
        dtype=float,
    )
    structured_mean = float(np.mean(structured_rho))
    structured_max = float(np.max(structured_rho))

    summary_rows: List[Dict[str, Any]] = []
    pairwise_rows: List[Dict[str, Any]] = []
    correlation_rows: List[Dict[str, Any]] = []
    status_labels: Dict[str, str] = {}
    warnings: List[str] = []

    for control_family in RESIDUAL_CONTROL_FAMILIES:
        control_values = centered_values[control_family]
        control_rho_values: List[float] = []
        control_tau_values: List[float] = []
        reference_higher_count = 0

        for source_id in node_ids:
            for target_id in node_ids:
                pair_key = (source_id, target_id)
                structured = structured_values[pair_key]
                control = control_values[pair_key]
                rho_structured = structured["rho_tau_centered"]
                rho_control = control["rho_tau_centered"]
                tau_structured = structured["tau_rel_centered"]
                tau_control = control["tau_rel_centered"]
                rho_delta = rho_structured - rho_control
                rho_ratio = rho_control / (rho_structured + eta)
                tau_delta = tau_structured - tau_control
                warning = ""

                if rho_structured > rho_control:
                    reference_higher_count += 1
                    pattern_status = "reference_higher"
                elif rho_control > rho_structured:
                    pattern_status = "control_higher"
                    warning = "residual control remains above structured reference for this pair"
                else:
                    pattern_status = "equal"
                    warning = "residual control equals structured reference for this pair"

                control_rho_values.append(rho_control)
                control_tau_values.append(tau_control)
                pairwise_rows.append(
                    {
                        "control_family": control_family,
                        "source_id": source_id,
                        "target_id": target_id,
                        "rho_tau_structured": f"{rho_structured:.12g}",
                        "rho_tau_control": f"{rho_control:.12g}",
                        "rho_tau_delta": f"{rho_delta:.12g}",
                        "rho_tau_ratio": f"{rho_ratio:.12g}",
                        "tau_rel_structured": f"{tau_structured:.12g}",
                        "tau_rel_control": f"{tau_control:.12g}",
                        "tau_rel_delta": f"{tau_delta:.12g}",
                        "pattern_status": pattern_status,
                        "warning": warning,
                    }
                )

        control_rho = np.asarray(control_rho_values, dtype=float)
        control_tau = np.asarray(control_tau_values, dtype=float)
        mean_ratio = float(np.mean(control_rho) / (structured_mean + eta))
        max_ratio = float(np.max(control_rho) / (structured_max + eta))
        pattern_correlation = pearson_correlation(structured_rho, control_rho)
        rank_separation_score = float(reference_higher_count / len(control_rho_values))
        warning_type = residual_warning_type(control_family, mean_ratio)
        likely_failure_mode = residual_likely_failure_mode(control_family)
        recommended_next_probe = residual_recommended_next_probe(control_family)
        warning_parts = ["diagnostic specificity not established"]
        if mean_ratio >= 0.9:
            warning_parts.append("residual control remains close/exceeds reference")
        if pattern_correlation is None:
            warning_parts.append("pairwise pattern correlation undefined")
        elif pattern_correlation >= 0.8:
            warning_parts.append("pattern_mimicry_warning")
        if control_family == "label_shuffle":
            warning_parts.append("small-kernel ambiguity")
            warning_parts.append("label stability not yet tested")
        if control_family == "random_phase":
            warning_parts.append("seed sensitivity not yet tested")
        warning_text = "; ".join(warning_parts)

        status_labels[control_family] = warning_type
        warnings.append(f"{control_family}: {warning_text}")
        summary_rows.append(
            {
                "control_family": control_family,
                "pair_count": len(control_rho_values),
                "rho_tau_centered_mean": f"{float(np.mean(control_rho)):.12g}",
                "rho_tau_centered_max": f"{float(np.max(control_rho)):.12g}",
                "tau_rel_centered_mean": f"{float(np.mean(control_tau)):.12g}",
                "structured_reference_mean": f"{structured_mean:.12g}",
                "mean_ratio_to_reference": f"{mean_ratio:.12g}",
                "max_ratio_to_reference": f"{max_ratio:.12g}",
                "pairwise_pattern_correlation_to_reference": "" if pattern_correlation is None else f"{pattern_correlation:.12g}",
                "rank_separation_score": f"{rank_separation_score:.12g}",
                "residual_warning_type": warning_type,
                "likely_failure_mode": likely_failure_mode,
                "recommended_next_probe": recommended_next_probe,
                "warning": warning_text,
            }
        )

    comparison_families = [STRUCTURED_REFERENCE_FAMILY] + RESIDUAL_CONTROL_FAMILIES
    for idx, family_a in enumerate(comparison_families):
        for family_b in comparison_families[idx + 1:]:
            values_a = centered_values[family_a]
            values_b = centered_values[family_b]
            rho_a = np.asarray(
                [
                    values_a[(source_id, target_id)]["rho_tau_centered"]
                    for source_id in node_ids
                    for target_id in node_ids
                ],
                dtype=float,
            )
            rho_b = np.asarray(
                [
                    values_b[(source_id, target_id)]["rho_tau_centered"]
                    for source_id in node_ids
                    for target_id in node_ids
                ],
                dtype=float,
            )
            tau_a = np.asarray(
                [
                    values_a[(source_id, target_id)]["tau_rel_centered"]
                    for source_id in node_ids
                    for target_id in node_ids
                ],
                dtype=float,
            )
            tau_b = np.asarray(
                [
                    values_b[(source_id, target_id)]["tau_rel_centered"]
                    for source_id in node_ids
                    for target_id in node_ids
                ],
                dtype=float,
            )
            rho_correlation = pearson_correlation(rho_a, rho_b)
            tau_correlation = pearson_correlation(tau_a, tau_b)
            top_a = top_quartile_keys(values_a)
            top_b = top_quartile_keys(values_b)
            rank_overlap = float(len(top_a.intersection(top_b)) / max(1, len(top_a)))
            interpretation_status = family_correlation_status(rho_correlation, rank_overlap)
            warning = ""
            if interpretation_status == "high_pattern_mimicry_warning":
                warning = "pattern mimicry warning; diagnostic specificity not established"
            elif interpretation_status == "correlation_degenerate_warning":
                warning = "correlation degenerate; diagnostic specificity not established"
            elif family_a == STRUCTURED_REFERENCE_FAMILY or family_b == STRUCTURED_REFERENCE_FAMILY:
                warning = "structured-control comparison remains method-level only"

            correlation_rows.append(
                {
                    "family_a": family_a,
                    "family_b": family_b,
                    "pair_count": len(rho_a),
                    "rho_tau_pattern_correlation": "" if rho_correlation is None else f"{rho_correlation:.12g}",
                    "tau_rel_pattern_correlation": "" if tau_correlation is None else f"{tau_correlation:.12g}",
                    "rank_overlap_top_quartile": f"{rank_overlap:.12g}",
                    "interpretation_status": interpretation_status,
                    "warning": warning,
                }
            )

    return summary_rows, pairwise_rows, correlation_rows, status_labels, warnings


def compute_control_family(
    control_family: str,
    node_ids: List[str],
    baseline_kernel: np.ndarray,
    epsilon_values: List[float],
    finite_difference_epsilon: float,
    eta: float,
    norm_family: str,
    normalization_family: str,
    random_phase_basis: np.ndarray,
    randomized_phase_basis: np.ndarray,
    label_permutation: np.ndarray,
) -> Tuple[List[Dict[str, Any]], np.ndarray]:
    records: List[Dict[str, Any]] = []
    inverse_candidates: List[float] = []
    n = len(node_ids)

    for source_idx, source_id in enumerate(node_ids):
        for target_idx, target_id in enumerate(node_ids):
            response_by_epsilon: Dict[float, float] = {}
            for epsilon in epsilon_values:
                response_baseline, perturbed, response_target_idx = build_control_perturbation(
                    control_family=control_family,
                    baseline_kernel=baseline_kernel,
                    source_idx=source_idx,
                    target_idx=target_idx,
                    epsilon=epsilon,
                    random_phase_basis=random_phase_basis,
                    randomized_phase_basis=randomized_phase_basis,
                    label_permutation=label_permutation,
                )

                response_by_epsilon[epsilon] = response_value(
                    response_baseline,
                    perturbed,
                    response_target_idx,
                    norm_family,
                )

            slope, integral, peak_epsilon, rho_tau = summarize_pair_response(
                response_by_epsilon,
                epsilon_values,
                finite_difference_epsilon,
                eta,
            )
            inverse_candidates.append(1.0 / (rho_tau + eta))
            records.append(
                {
                    "control_family": control_family,
                    "source_id": source_id,
                    "target_id": target_id,
                    "epsilon_min": min(epsilon_values),
                    "epsilon_max": max(epsilon_values),
                    "response_slope": slope,
                    "response_integral": integral,
                    "response_peak_epsilon": peak_epsilon,
                    "rho_tau": rho_tau,
                    "normalization_family": normalization_family,
                    "status": "synthetic_control_pairwise_score_computed",
                }
            )

    if len(records) != n * n:
        raise ValueError(f"{control_family} produced {len(records)} rows, expected {n * n}")
    tau_candidates = minmax(np.asarray(inverse_candidates, dtype=float), eta=eta)
    return records, tau_candidates


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.generic):
        return value.item()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def main() -> None:
    args = parse_args()
    cfg = load_config(args.config)
    require_keys(
        cfg,
        [
            "block", "claim_boundary", "baseline", "perturbation", "response",
            "distance", "interval_candidate", "controls", "outputs", "acceptance",
            "reproducibility",
        ],
    )

    epsilon_values = validate_epsilon_values(cfg["perturbation"]["epsilon_values"])
    eta = float(cfg["response"].get("eta", 1.0e-12))
    norm_family = str(cfg["response"].get("response_norm", "l2"))
    finite_difference_epsilon = float(cfg["response"].get("finite_difference_epsilon", 0.005))
    seed = int(cfg["reproducibility"].get("random_seed", 17052026))
    output_dir = args.output_dir if args.output_dir is not None else Path(cfg["outputs"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    node_ids, baseline_kernel = build_synthetic_kernel(seed=seed)

    if cfg["baseline"].get("require_square_kernel", True):
        if baseline_kernel.ndim != 2 or baseline_kernel.shape[0] != baseline_kernel.shape[1]:
            raise ValueError("Synthetic baseline kernel is not square")
    if cfg["baseline"].get("require_finite_values", True):
        if not np.isfinite(baseline_kernel.real).all() or not np.isfinite(baseline_kernel.imag).all():
            raise ValueError("Synthetic baseline kernel contains non-finite values")

    per_pair_response: Dict[Tuple[str, str], Dict[float, float]] = {}
    all_response_values: List[float] = []

    for source_idx, source_id in enumerate(node_ids):
        for target_idx, target_id in enumerate(node_ids):
            key = (source_id, target_id)
            per_pair_response[key] = {}
            for epsilon in epsilon_values:
                perturbed = local_phase_perturbation(baseline_kernel, source_idx, epsilon)
                raw = response_value(baseline_kernel, perturbed, target_idx, norm_family)
                per_pair_response[key][epsilon] = raw
                all_response_values.append(raw)

    normalized_values = normalize(np.asarray(all_response_values, dtype=float), eta=eta).tolist()
    norm_iter = iter(normalized_values)
    sweep_rows: List[Dict[str, Any]] = []

    for source_id in node_ids:
        for target_id in node_ids:
            for epsilon in epsilon_values:
                raw = per_pair_response[(source_id, target_id)][epsilon]
                sweep_rows.append(
                    {
                        "source_id": source_id,
                        "target_id": target_id,
                        "epsilon": f"{epsilon:.12g}",
                        "response_value": f"{raw:.12g}",
                        "response_value_normalized": f"{float(next(norm_iter)):.12g}",
                        "observable_family": cfg["response"]["observable_family"],
                        "perturbation_family": cfg["perturbation"]["perturbation_family"],
                        "status": "synthetic_response_computed",
                    }
                )

    raw_pair_records: List[Dict[str, Any]] = []
    rho_values: List[float] = []
    inverse_candidates: List[float] = []

    for source_id in node_ids:
        for target_id in node_ids:
            values = per_pair_response[(source_id, target_id)]
            slope = central_slope(values, finite_difference_epsilon)
            positive_small_response = values[finite_difference_epsilon]
            rho_tau = float(positive_small_response / (abs(finite_difference_epsilon) + eta))
            integral = trapezoid_integral(epsilon_values, [values[eps] for eps in epsilon_values])
            peak_epsilon = max(epsilon_values, key=lambda eps: values[eps])
            rho_values.append(rho_tau)
            inverse_candidates.append(1.0 / (rho_tau + eta))
            raw_pair_records.append(
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "epsilon_min": min(epsilon_values),
                    "epsilon_max": max(epsilon_values),
                    "response_slope": slope,
                    "response_integral": integral,
                    "response_peak_epsilon": peak_epsilon,
                    "rho_tau": rho_tau,
                    "normalization_family": cfg["response"]["normalization_family"],
                    "status": "synthetic_pairwise_score_computed",
                }
            )

    tau_candidates = minmax(np.asarray(inverse_candidates, dtype=float), eta=eta)
    pairwise_rows: List[Dict[str, Any]] = []
    tau_matrix_rows: List[Dict[str, Any]] = []

    for idx, record in enumerate(raw_pair_records):
        tau_rel_candidate = float(tau_candidates[idx])
        pairwise_rows.append(
            {
                "source_id": record["source_id"],
                "target_id": record["target_id"],
                "epsilon_min": f"{record['epsilon_min']:.12g}",
                "epsilon_max": f"{record['epsilon_max']:.12g}",
                "response_slope": f"{record['response_slope']:.12g}",
                "response_integral": f"{record['response_integral']:.12g}",
                "response_peak_epsilon": f"{record['response_peak_epsilon']:.12g}",
                "rho_tau": f"{record['rho_tau']:.12g}",
                "tau_rel_candidate": f"{tau_rel_candidate:.12g}",
                "normalization_family": record["normalization_family"],
                "status": record["status"],
            }
        )
        tau_matrix_rows.append(
            {
                "source_id": record["source_id"],
                "target_id": record["target_id"],
                "tau_rel_candidate": f"{tau_rel_candidate:.12g}",
                "rho_tau": f"{record['rho_tau']:.12g}",
                "distance_D": "",
                "S_rel2_candidate": "",
                "c_eff": "",
                "status": "tau_rel_candidate_synthetic_only",
            }
        )

    control_rng = np.random.default_rng(seed + 101)
    random_phase_basis = control_rng.uniform(
        low=-math.pi,
        high=math.pi,
        size=(len(node_ids), len(node_ids), len(node_ids)),
    )
    randomized_phase_basis = control_rng.uniform(
        low=-math.pi,
        high=math.pi,
        size=(len(node_ids), len(node_ids), len(node_ids)),
    )
    label_permutation = control_rng.permutation(len(node_ids))

    control_pairwise_rows: List[Dict[str, Any]] = []
    control_summary_rows: List[Dict[str, Any]] = []
    control_pair_values: Dict[str, Dict[Tuple[str, str], Dict[str, float]]] = {}
    control_status_labels: Dict[str, str] = {}
    control_warnings: List[str] = []
    structured_reference_mean: float | None = None
    structured_reference_max: float | None = None

    for control_family in CONTROL_FAMILIES:
        control_records, control_tau_candidates = compute_control_family(
            control_family=control_family,
            node_ids=node_ids,
            baseline_kernel=baseline_kernel,
            epsilon_values=epsilon_values,
            finite_difference_epsilon=finite_difference_epsilon,
            eta=eta,
            norm_family=norm_family,
            normalization_family=cfg["response"]["normalization_family"],
            random_phase_basis=random_phase_basis,
            randomized_phase_basis=randomized_phase_basis,
            label_permutation=label_permutation,
        )

        rho_control = np.asarray([record["rho_tau"] for record in control_records], dtype=float)
        tau_control = np.asarray(control_tau_candidates, dtype=float)
        if control_family == "structured_local_phase_response":
            structured_reference_mean = float(np.mean(rho_control))
            structured_reference_max = float(np.max(rho_control))
        if structured_reference_mean is None or structured_reference_max is None:
            raise ValueError("Structured reference must be computed before controls")

        mean_ratio = float(np.mean(rho_control) / (structured_reference_mean + eta))
        max_ratio = float(np.max(rho_control) / (structured_reference_max + eta))
        status_label = control_status_label(control_family, mean_ratio, max_ratio)
        warning = ""
        if control_family == "label_shuffle":
            warning = "Small synthetic systems can make label-shuffle controls ambiguous; interpret as a label/identity diagnostic only."
        elif status_label == "control_close_to_structured_warning":
            warning = "Control response is close to structured reference; diagnostic specificity is not established for this control."

        control_status_labels[control_family] = status_label
        if warning:
            control_warnings.append(f"{control_family}: {warning}")

        for idx, record in enumerate(control_records):
            pair_key = (str(record["source_id"]), str(record["target_id"]))
            control_pair_values.setdefault(control_family, {})[pair_key] = {
                "rho_tau": float(record["rho_tau"]),
                "tau_rel_candidate": float(control_tau_candidates[idx]),
            }
            control_pairwise_rows.append(
                {
                    "control_family": record["control_family"],
                    "source_id": record["source_id"],
                    "target_id": record["target_id"],
                    "epsilon_min": f"{record['epsilon_min']:.12g}",
                    "epsilon_max": f"{record['epsilon_max']:.12g}",
                    "response_slope": f"{record['response_slope']:.12g}",
                    "response_integral": f"{record['response_integral']:.12g}",
                    "response_peak_epsilon": f"{record['response_peak_epsilon']:.12g}",
                    "rho_tau": f"{record['rho_tau']:.12g}",
                    "tau_rel_candidate": f"{float(control_tau_candidates[idx]):.12g}",
                    "normalization_family": record["normalization_family"],
                    "status": record["status"],
                }
            )

        control_summary_rows.append(
            {
                "control_family": control_family,
                "pair_count": len(control_records),
                "rho_tau_min": f"{float(np.min(rho_control)):.12g}",
                "rho_tau_max": f"{float(np.max(rho_control)):.12g}",
                "rho_tau_mean": f"{float(np.mean(rho_control)):.12g}",
                "rho_tau_std": f"{float(np.std(rho_control)):.12g}",
                "tau_rel_candidate_min": f"{float(np.min(tau_control)):.12g}",
                "tau_rel_candidate_max": f"{float(np.max(tau_control)):.12g}",
                "tau_rel_candidate_mean": f"{float(np.mean(tau_control)):.12g}",
                "structured_reference_mean_ratio": f"{mean_ratio:.12g}",
                "structured_reference_max_ratio": f"{max_ratio:.12g}",
                "status": status_label,
                "warning": warning,
            }
        )

    reference_pair_values = control_pair_values[STRUCTURED_REFERENCE_FAMILY]
    specificity_pairwise_rows: List[Dict[str, Any]] = []
    specificity_summary_rows: List[Dict[str, Any]] = []
    specificity_status_labels: Dict[str, str] = {}
    specificity_warnings: List[str] = []

    for control_family in SPECIFICITY_CONTROL_FAMILIES:
        control_values = control_pair_values[control_family]
        reference_rho_values: List[float] = []
        control_rho_values: List[float] = []
        reference_tau_values: List[float] = []
        control_tau_values: List[float] = []
        reference_higher_count = 0

        for source_id in node_ids:
            for target_id in node_ids:
                pair_key = (source_id, target_id)
                ref = reference_pair_values[pair_key]
                ctrl = control_values[pair_key]
                rho_ref = ref["rho_tau"]
                rho_ctrl = ctrl["rho_tau"]
                tau_ref = ref["tau_rel_candidate"]
                tau_ctrl = ctrl["tau_rel_candidate"]
                rho_delta = rho_ref - rho_ctrl
                tau_delta = tau_ref - tau_ctrl
                rho_ratio = rho_ctrl / (rho_ref + eta)
                if rho_ref > rho_ctrl:
                    reference_higher_count += 1
                    pattern_status = "reference_higher"
                elif rho_ctrl > rho_ref:
                    pattern_status = "control_higher"
                else:
                    pattern_status = "equal"

                reference_rho_values.append(rho_ref)
                control_rho_values.append(rho_ctrl)
                reference_tau_values.append(tau_ref)
                control_tau_values.append(tau_ctrl)
                specificity_pairwise_rows.append(
                    {
                        "source_id": source_id,
                        "target_id": target_id,
                        "control_family": control_family,
                        "rho_tau_reference": f"{rho_ref:.12g}",
                        "rho_tau_control": f"{rho_ctrl:.12g}",
                        "rho_tau_delta": f"{rho_delta:.12g}",
                        "rho_tau_ratio": f"{rho_ratio:.12g}",
                        "tau_rel_reference": f"{tau_ref:.12g}",
                        "tau_rel_control": f"{tau_ctrl:.12g}",
                        "tau_rel_delta": f"{tau_delta:.12g}",
                        "pattern_status": pattern_status,
                    }
                )

        ref_rho_array = np.asarray(reference_rho_values, dtype=float)
        ctrl_rho_array = np.asarray(control_rho_values, dtype=float)
        ref_mean = float(np.mean(ref_rho_array))
        ctrl_mean = float(np.mean(ctrl_rho_array))
        ref_max = float(np.max(ref_rho_array))
        ctrl_max = float(np.max(ctrl_rho_array))
        mean_ratio = float(ctrl_mean / (ref_mean + eta))
        max_ratio = float(ctrl_max / (ref_max + eta))
        rank_separation_score = float(reference_higher_count / len(reference_rho_values))
        pattern_correlation = pearson_correlation(ref_rho_array, ctrl_rho_array)
        status_label = specificity_status_label(
            control_family,
            mean_ratio,
            max_ratio,
            rank_separation_score,
        )

        warning_parts: List[str] = []
        if pattern_correlation is None:
            warning_parts.append("pairwise pattern correlation undefined because at least one vector has zero variance")
        if status_label != "specificity_supported_in_tested_controls":
            warning_parts.append("synthetic specificity remains conservative/open for this control")
        if control_family == "label_shuffle":
            warning_parts.append("small synthetic systems can make label-shuffle specificity ambiguous")

        warning_text = "; ".join(warning_parts)
        specificity_status_labels[control_family] = status_label
        if warning_text:
            specificity_warnings.append(f"{control_family}: {warning_text}")

        specificity_summary_rows.append(
            {
                "control_family": control_family,
                "reference_family": STRUCTURED_REFERENCE_FAMILY,
                "pair_count": len(reference_rho_values),
                "rho_tau_reference_mean": f"{ref_mean:.12g}",
                "rho_tau_control_mean": f"{ctrl_mean:.12g}",
                "rho_tau_mean_delta": f"{(ref_mean - ctrl_mean):.12g}",
                "rho_tau_mean_ratio": f"{mean_ratio:.12g}",
                "rho_tau_reference_max": f"{ref_max:.12g}",
                "rho_tau_control_max": f"{ctrl_max:.12g}",
                "rho_tau_max_delta": f"{(ref_max - ctrl_max):.12g}",
                "rho_tau_max_ratio": f"{max_ratio:.12g}",
                "pairwise_pattern_correlation": "" if pattern_correlation is None else f"{pattern_correlation:.12g}",
                "rank_separation_score": f"{rank_separation_score:.12g}",
                "specificity_status": status_label,
                "warning": warning_text,
            }
        )

    (
        observable_audit_summary_rows,
        observable_raw_control_rows,
        normalization_rank_change_rows,
        warning_row_report_rows,
    ) = build_observable_normalization_audit(
        control_pair_values=control_pair_values,
        node_ids=node_ids,
        normalization_family=cfg["response"]["normalization_family"],
        eta=eta,
    )
    observable_normalization_audit_summary_file = "observable_normalization_audit_summary.csv"
    observable_raw_control_table_file = "observable_raw_control_table.csv"
    normalization_rank_change_table_file = "normalization_rank_change_table.csv"
    warning_row_report_file = "warning_row_report.csv"
    observable_audit_warnings = [
        f"{row['family']}: {row['warning']}"
        for row in observable_audit_summary_rows
        if row["warning"]
    ]
    global_phase_audit_status = next(
        row["global_phase_audit_status"]
        for row in observable_audit_summary_rows
        if row["family"] == "global_phase_shift"
    )
    small_kernel_audit_status = "small_kernel_caution_present"
    if any(
        row["small_kernel_audit_status"] == "small_kernel_label_shuffle_ambiguous"
        for row in observable_audit_summary_rows
    ):
        small_kernel_audit_status = "small_kernel_label_shuffle_ambiguous_present"

    (
        global_phase_probe_summary_rows,
        global_phase_probe_pairwise_rows,
        global_phase_centering_diagnostics_rows,
        global_phase_probe_status_labels,
        global_phase_probe_warnings,
        global_phase_warning_reduced,
    ) = build_global_phase_invariant_probe(
        node_ids=node_ids,
        baseline_kernel=baseline_kernel,
        epsilon_values=epsilon_values,
        finite_difference_epsilon=finite_difference_epsilon,
        eta=eta,
        norm_family=norm_family,
        random_phase_basis=random_phase_basis,
        randomized_phase_basis=randomized_phase_basis,
        label_permutation=label_permutation,
        control_pair_values=control_pair_values,
        global_phase_audit_status=global_phase_audit_status,
        specificity_status_labels=specificity_status_labels,
    )
    global_phase_invariant_probe_summary_file = "global_phase_invariant_probe_summary.csv"
    global_phase_invariant_pairwise_response_file = "global_phase_invariant_pairwise_response.csv"
    global_phase_centering_diagnostics_file = "global_phase_centering_diagnostics.csv"

    (
        residual_control_summary_rows,
        residual_control_pairwise_rows,
        residual_control_correlation_rows,
        residual_control_status_labels,
        residual_control_warnings,
    ) = build_residual_control_warning_analysis(
        global_phase_probe_pairwise_rows=global_phase_probe_pairwise_rows,
        node_ids=node_ids,
        eta=eta,
    )
    residual_control_warning_summary_file = "residual_control_warning_summary.csv"
    residual_control_pairwise_comparison_file = "residual_control_pairwise_comparison.csv"
    residual_control_family_correlation_file = "residual_control_family_correlation.csv"
    residual_control_seed_sensitivity_file = "not_generated"
    residual_control_label_stability_file = "not_generated"

    csv_files = cfg["outputs"]["csv_files"]
    write_csv(
        output_dir / csv_files["response_sweep"],
        sweep_rows,
        ["source_id", "target_id", "epsilon", "response_value", "response_value_normalized", "observable_family", "perturbation_family", "status"],
    )
    write_csv(
        output_dir / csv_files["pairwise_response"],
        pairwise_rows,
        ["source_id", "target_id", "epsilon_min", "epsilon_max", "response_slope", "response_integral", "response_peak_epsilon", "rho_tau", "tau_rel_candidate", "normalization_family", "status"],
    )
    write_csv(
        output_dir / csv_files["tau_rel_candidate_matrix"],
        tau_matrix_rows,
        ["source_id", "target_id", "tau_rel_candidate", "rho_tau", "distance_D", "S_rel2_candidate", "c_eff", "status"],
    )
    control_pairwise_file = "control_pairwise_response.csv"
    control_summary_file = "control_summary.csv"
    write_csv(
        output_dir / control_pairwise_file,
        control_pairwise_rows,
        [
            "control_family", "source_id", "target_id", "epsilon_min", "epsilon_max",
            "response_slope", "response_integral", "response_peak_epsilon",
            "rho_tau", "tau_rel_candidate", "normalization_family", "status",
        ],
    )
    write_csv(
        output_dir / control_summary_file,
        control_summary_rows,
        [
            "control_family", "pair_count", "rho_tau_min", "rho_tau_max",
            "rho_tau_mean", "rho_tau_std", "tau_rel_candidate_min",
            "tau_rel_candidate_max", "tau_rel_candidate_mean",
            "structured_reference_mean_ratio", "structured_reference_max_ratio",
            "status", "warning",
        ],
    )
    specificity_contrast_summary_file = "specificity_contrast_summary.csv"
    specificity_pairwise_contrast_file = "specificity_pairwise_contrast.csv"
    write_csv(
        output_dir / specificity_contrast_summary_file,
        specificity_summary_rows,
        [
            "control_family", "reference_family", "pair_count",
            "rho_tau_reference_mean", "rho_tau_control_mean",
            "rho_tau_mean_delta", "rho_tau_mean_ratio",
            "rho_tau_reference_max", "rho_tau_control_max",
            "rho_tau_max_delta", "rho_tau_max_ratio",
            "pairwise_pattern_correlation", "rank_separation_score",
            "specificity_status", "warning",
        ],
    )
    write_csv(
        output_dir / specificity_pairwise_contrast_file,
        specificity_pairwise_rows,
        [
            "source_id", "target_id", "control_family",
            "rho_tau_reference", "rho_tau_control", "rho_tau_delta",
            "rho_tau_ratio", "tau_rel_reference", "tau_rel_control",
            "tau_rel_delta", "pattern_status",
        ],
    )
    write_csv(
        output_dir / observable_normalization_audit_summary_file,
        observable_audit_summary_rows,
        [
            "family", "pair_count", "rho_tau_raw_min", "rho_tau_raw_max",
            "rho_tau_raw_mean", "rho_tau_raw_median", "rho_tau_raw_std",
            "rho_tau_raw_q25", "rho_tau_raw_q75", "tau_rel_min",
            "tau_rel_max", "tau_rel_mean", "tau_rel_median", "tau_rel_std",
            "normalization_family", "rank_mean", "rank_median",
            "rank_top_pair", "global_phase_audit_status",
            "small_kernel_audit_status", "specificity_warning_status",
            "warning",
        ],
    )
    write_csv(
        output_dir / observable_raw_control_table_file,
        observable_raw_control_rows,
        [
            "family", "source_id", "target_id", "rho_tau_raw",
            "tau_rel_candidate", "raw_rank_desc", "tau_rank_desc",
            "rank_delta", "normalization_family", "status",
        ],
    )
    write_csv(
        output_dir / normalization_rank_change_table_file,
        normalization_rank_change_rows,
        [
            "family", "source_id", "target_id", "rho_tau_raw",
            "tau_rel_candidate", "raw_rank_desc", "tau_rank_desc",
            "rank_delta", "rank_delta_abs", "rank_flip_warning", "status",
        ],
    )
    write_csv(
        output_dir / warning_row_report_file,
        warning_row_report_rows,
        [
            "warning_type", "family", "source_id", "target_id",
            "rho_tau_raw", "tau_rel_candidate", "detail",
        ],
    )
    write_csv(
        output_dir / global_phase_invariant_probe_summary_file,
        global_phase_probe_summary_rows,
        [
            "family", "pair_count", "rho_tau_original_mean",
            "rho_tau_centered_mean", "rho_tau_mean_delta",
            "rho_tau_mean_ratio", "global_phase_warning_before",
            "global_phase_warning_after", "specificity_status_before",
            "specificity_status_after", "probe_status", "warning",
        ],
    )
    write_csv(
        output_dir / global_phase_invariant_pairwise_response_file,
        global_phase_probe_pairwise_rows,
        [
            "family", "source_id", "target_id", "rho_tau_original",
            "rho_tau_centered", "rho_tau_delta", "tau_rel_original",
            "tau_rel_centered", "tau_rel_delta",
            "global_phase_centering_applied", "status",
        ],
    )
    write_csv(
        output_dir / global_phase_centering_diagnostics_file,
        global_phase_centering_diagnostics_rows,
        [
            "family", "epsilon", "global_phase_angle_estimate",
            "phase_centering_norm_delta", "response_before_centering",
            "response_after_centering", "status",
        ],
    )
    write_csv(
        output_dir / residual_control_warning_summary_file,
        residual_control_summary_rows,
        [
            "control_family", "pair_count", "rho_tau_centered_mean",
            "rho_tau_centered_max", "tau_rel_centered_mean",
            "structured_reference_mean", "mean_ratio_to_reference",
            "max_ratio_to_reference", "pairwise_pattern_correlation_to_reference",
            "rank_separation_score", "residual_warning_type",
            "likely_failure_mode", "recommended_next_probe", "warning",
        ],
    )
    write_csv(
        output_dir / residual_control_pairwise_comparison_file,
        residual_control_pairwise_rows,
        [
            "control_family", "source_id", "target_id", "rho_tau_structured",
            "rho_tau_control", "rho_tau_delta", "rho_tau_ratio",
            "tau_rel_structured", "tau_rel_control", "tau_rel_delta",
            "pattern_status", "warning",
        ],
    )
    write_csv(
        output_dir / residual_control_family_correlation_file,
        residual_control_correlation_rows,
        [
            "family_a", "family_b", "pair_count",
            "rho_tau_pattern_correlation", "tau_rel_pattern_correlation",
            "rank_overlap_top_quartile", "interpretation_status", "warning",
        ],
    )

    resolved_config = {
        "config_path": str(args.config),
        "output_dir": str(output_dir),
        "resolved": cfg,
        "synthetic_node_ids": node_ids,
        "synthetic_kernel_shape": list(baseline_kernel.shape),
    }
    (output_dir / "config_resolved.json").write_text(
        json.dumps(resolved_config, indent=2, ensure_ascii=False, default=json_default),
        encoding="utf-8",
    )

    rho_array = np.asarray(rho_values, dtype=float)
    tau_array = np.asarray([float(row["tau_rel_candidate"]) for row in pairwise_rows], dtype=float)
    summary = {
        "block_id": cfg["block"]["block_id"],
        "run_id": cfg["block"]["run_id"],
        "status": "synthetic_minimal_run_completed",
        "construction_route": cfg["block"]["construction_route"],
        "baseline_source": cfg["baseline"]["source_mode"],
        "perturbation_family": cfg["perturbation"]["perturbation_family"],
        "observable_family": cfg["response"]["observable_family"],
        "epsilon_values": epsilon_values,
        "pair_count": len(pairwise_rows),
        "sweep_row_count": len(sweep_rows),
        "tau_rel_constructed": True,
        "S_rel2_constructed": False,
        "output_dir": str(output_dir),
        "synthetic_node_count": len(node_ids),
        "rho_tau_min": float(np.min(rho_array)),
        "rho_tau_max": float(np.max(rho_array)),
        "rho_tau_mean": float(np.mean(rho_array)),
        "tau_rel_candidate_min": float(np.min(tau_array)),
        "tau_rel_candidate_max": float(np.max(tau_array)),
        "tau_rel_candidate_mean": float(np.mean(tau_array)),
        "controls_implemented": CONTROL_FAMILIES,
        "control_family_count": len(CONTROL_FAMILIES),
        "control_pairwise_response_file": control_pairwise_file,
        "control_summary_file": control_summary_file,
        "structured_reference_family": STRUCTURED_REFERENCE_FAMILY,
        "control_status_labels": control_status_labels,
        "control_warnings": control_warnings,
        "specificity_contrast_summary_file": specificity_contrast_summary_file,
        "specificity_pairwise_contrast_file": specificity_pairwise_contrast_file,
        "specificity_reference_family": STRUCTURED_REFERENCE_FAMILY,
        "specificity_control_families": SPECIFICITY_CONTROL_FAMILIES,
        "specificity_status_labels": specificity_status_labels,
        "specificity_warnings": specificity_warnings,
        "specificity_established": False,
        "observable_normalization_audit_summary_file": observable_normalization_audit_summary_file,
        "observable_raw_control_table_file": observable_raw_control_table_file,
        "normalization_rank_change_table_file": normalization_rank_change_table_file,
        "warning_row_report_file": warning_row_report_file,
        "observable_audit_family_count": len(observable_audit_summary_rows),
        "observable_audit_pair_row_count": len(observable_raw_control_rows),
        "normalization_rank_change_row_count": len(normalization_rank_change_rows),
        "observable_audit_warnings": observable_audit_warnings,
        "normalization_audit_status": "observable_normalization_audit_completed_no_specificity_claim",
        "global_phase_audit_status": global_phase_audit_status,
        "small_kernel_audit_status": small_kernel_audit_status,
        "audit_established_specificity": False,
        "global_phase_invariant_probe_summary_file": global_phase_invariant_probe_summary_file,
        "global_phase_invariant_pairwise_response_file": global_phase_invariant_pairwise_response_file,
        "global_phase_centering_diagnostics_file": global_phase_centering_diagnostics_file,
        "global_phase_probe_family_count": len(global_phase_probe_summary_rows),
        "global_phase_probe_pair_row_count": len(global_phase_probe_pairwise_rows),
        "global_phase_centering_diagnostics_row_count": len(global_phase_centering_diagnostics_rows),
        "global_phase_probe_status_labels": global_phase_probe_status_labels,
        "global_phase_probe_warnings": global_phase_probe_warnings,
        "global_phase_warning_reduced": global_phase_warning_reduced,
        "global_phase_probe_established_specificity": False,
        "residual_control_warning_summary_file": residual_control_warning_summary_file,
        "residual_control_pairwise_comparison_file": residual_control_pairwise_comparison_file,
        "residual_control_family_correlation_file": residual_control_family_correlation_file,
        "residual_control_seed_sensitivity_file": residual_control_seed_sensitivity_file,
        "residual_control_label_stability_file": residual_control_label_stability_file,
        "residual_control_family_count": len(residual_control_summary_rows),
        "residual_control_pairwise_row_count": len(residual_control_pairwise_rows),
        "residual_control_family_correlation_row_count": len(residual_control_correlation_rows),
        "residual_control_status_labels": residual_control_status_labels,
        "residual_control_warnings": residual_control_warnings,
        "residual_control_established_specificity": False,
        "claim_boundary": "Synthetic phase-response diagnostic only. tau_rel_candidate is not physical time; no Lorentzian metric, spacetime validation, or physical validation is claimed.",
        "warnings": [
            "Synthetic reference kernel only; no real-data or physical validation.",
            "rho_tau is a diagnostic response-strength score.",
            "tau_rel_candidate is a normalized monotone transform of response strength.",
            "S_rel2_candidate is intentionally not constructed in this minimal run.",
            "The first control suite is synthetic and diagnostic only; it does not establish physical time, proper time, Lorentz metric behavior, spacetime emergence, or physical Bridge validation.",
            "The LIC01-F specificity layer compares raw rho_tau contrasts and does not establish diagnostic specificity when controls remain close to reference.",
            "Small synthetic systems can make label-shuffle controls ambiguous.",
        ],
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    readout = f"""# QSB-ST-LIC01 Tau/Epsilon Phase-Response Minimal Run

## Befund

The synthetic LIC01 minimal runner completed successfully.

- block_id: `{summary['block_id']}`
- run_id: `{summary['run_id']}`
- status: `{summary['status']}`
- synthetic_node_count: `{summary['synthetic_node_count']}`
- pair_count: `{summary['pair_count']}`
- sweep_row_count: `{summary['sweep_row_count']}`
- epsilon_values: `{summary['epsilon_values']}`
- tau_rel_constructed: `{summary['tau_rel_constructed']}`
- S_rel2_constructed: `{summary['S_rel2_constructed']}`

Output files:

```text
summary.json
readout.md
config_resolved.json
{csv_files['pairwise_response']}
{csv_files['response_sweep']}
{csv_files['tau_rel_candidate_matrix']}
{control_pairwise_file}
{control_summary_file}
{specificity_contrast_summary_file}
{specificity_pairwise_contrast_file}
{observable_normalization_audit_summary_file}
{observable_raw_control_table_file}
{normalization_rank_change_table_file}
{warning_row_report_file}
{global_phase_invariant_probe_summary_file}
{global_phase_invariant_pairwise_response_file}
{global_phase_centering_diagnostics_file}
{residual_control_warning_summary_file}
{residual_control_pairwise_comparison_file}
{residual_control_family_correlation_file}
```

## Interpretation

The run shows that, under a fixed synthetic reference kernel and a controlled
local phase perturbation, pairwise response scores can be computed reproducibly.

The produced `rho_tau(A,B)` values are response-strength diagnostics.
The produced `tau_rel_candidate(A,B)` values are normalized monotone transforms
of those response scores.

## Hypothese

If this response construction remains stable under explicit control families,
parameter variation, and later distance-comparison tests, it may become a useful
internal relational-delay diagnostic companion to an existing distance-like
quantity `D(A,B)`.

## Offene Lücke

This minimal runner does not yet implement the full control suite listed in the
config. It does not attach an existing distance field `D(A,B)`. It does not
construct `S_rel2_candidate`. It does not test uniqueness, invariance, Lorentz
compatibility, or empirical relevance.

## Control Readout

### Control families implemented

The runner computed the following synthetic control families:

```text
{chr(10).join(f"- {family}: {control_status_labels[family]}" for family in CONTROL_FAMILIES)}
```

### Control summary

The control outputs are:

```text
{control_pairwise_file}
{control_summary_file}
```

`{control_pairwise_file}` contains `{len(control_pairwise_rows)}` rows.
`{control_summary_file}` contains `{len(control_summary_rows)}` rows.

### Control warnings

```text
{chr(10).join(f"- {warning}" for warning in control_warnings) if control_warnings else "- No control warnings were emitted."}
```

### Control interpretation boundary

Under the tested synthetic control families, the LIC01 tau/epsilon response
diagnostic can be compared against global, random, phase-randomized, and
label-shuffled controls. These controls test synthetic diagnostic specificity
only. They do not prove physical time, proper time, a Lorentz metric, spacetime
emergence, a physical Bridge, or experimental/real-data validation.

## Specificity Readout

### Specificity contrast outputs

The LIC01-F specificity layer writes:

```text
{specificity_contrast_summary_file}
{specificity_pairwise_contrast_file}
```

`{specificity_contrast_summary_file}` contains `{len(specificity_summary_rows)}` rows.
`{specificity_pairwise_contrast_file}` contains `{len(specificity_pairwise_rows)}` rows.

### Specificity summary

Reference family:

```text
{STRUCTURED_REFERENCE_FAMILY}
```

Control status labels:

```text
{chr(10).join(f"- {family}: {specificity_status_labels[family]}" for family in SPECIFICITY_CONTROL_FAMILIES)}
```

The LIC01-F specificity layer compares structured reference response against
tested synthetic controls using raw `rho_tau` contrasts, pairwise deltas,
pattern correlation, and rank separation. `tau_rel_candidate` is reported as a
secondary diagnostic contrast and is not used alone for specificity.

### Specificity warnings

```text
{chr(10).join(f"- {warning}" for warning in specificity_warnings) if specificity_warnings else "- No specificity warnings were emitted."}
```

### Specificity interpretation boundary

Specificity comparison is now available. Specificity is only supported when
controls are clearly separated from the structured reference. If controls remain
close to the reference, specificity remains open. No physical interpretation is
made from this synthetic contrast layer.

## Observable / Normalization Audit Readout

### Audit outputs

The LIC01-G audit layer writes:

```text
{observable_normalization_audit_summary_file}
{observable_raw_control_table_file}
{normalization_rank_change_table_file}
{warning_row_report_file}
```

`{observable_normalization_audit_summary_file}` contains `{len(observable_audit_summary_rows)}` rows.
`{observable_raw_control_table_file}` contains `{len(observable_raw_control_rows)}` rows.
`{normalization_rank_change_table_file}` contains `{len(normalization_rank_change_rows)}` rows.
`{warning_row_report_file}` contains `{len(warning_row_report_rows)}` rows.

### Raw response audit

The audit reports raw `rho_tau` response values by family before the final
`tau_rel_candidate` normalization. It compares each control family against
`{STRUCTURED_REFERENCE_FAMILY}` at the diagnostic level only.

### Normalization rank-change audit

The audit ranks `rho_tau` and `tau_rel_candidate` separately within each
family. It reports rank deltas and flags pair rows where the absolute rank
change is at least 16.

### Global phase audit

Global phase audit status:

```text
{global_phase_audit_status}
```

The global phase check is an audit field for the synthetic control warning. It
does not turn `tau_rel_candidate` into a physical time observable.

### Small-kernel caution

Small-kernel audit status:

```text
{small_kernel_audit_status}
```

The current synthetic kernel has `{len(node_ids)}` nodes and `{len(pairwise_rows)}` source-target
pairs. Label-shuffle behavior is therefore treated as small-system ambiguous
unless later larger-kernel diagnostics resolve it.

### Audit interpretation boundary

The audit does not establish specificity. It reports whether raw response,
normalization, rank changes, global phase behavior, or small-kernel effects may
explain the warning.

The LIC01-G audit reports raw response, normalization, rank-change,
global-phase, and small-kernel diagnostics for the current tau/epsilon control
warning. It is a synthetic diagnostic audit only and makes no physical Bridge,
spacetime, Lorentz, experimental, real-data, physical time, or proper-time
claim.

## Global-Phase-Invariant Observable Probe Readout

### Probe outputs

The LIC01-H probe layer writes:

```text
{global_phase_invariant_probe_summary_file}
{global_phase_invariant_pairwise_response_file}
{global_phase_centering_diagnostics_file}
```

`{global_phase_invariant_probe_summary_file}` contains `{len(global_phase_probe_summary_rows)}` rows.
`{global_phase_invariant_pairwise_response_file}` contains `{len(global_phase_probe_pairwise_rows)}` rows.
`{global_phase_centering_diagnostics_file}` contains `{len(global_phase_centering_diagnostics_rows)}` rows.

### Global phase centering definition

For each baseline or perturbed matrix, the probe estimates a global phase angle
as `angle(sum(matrix entries with abs(entry) > eta))`. If the sum is numerically
near zero, the angle is set to `0.0` and the row is marked as a degenerate phase
angle case.

The centered matrix is computed as:

```text
centered_matrix = matrix * exp(-1j * global_phase_angle)
```

The probe then applies the same response logic as the existing runner to the
centered baseline and centered perturbed matrices.

### Before/after summary

The probe reports original and centered `rho_tau` means by family, plus pairwise
before/after `rho_tau` and probe-level `tau_rel_centered` values. The centered
candidate values are minmax-normalized per family as a diagnostic probe only.
They do not replace `tau_rel_candidate`.

### Global phase warning status

Global phase warning reduced:

```text
{global_phase_warning_reduced}
```

Global phase probe status labels:

```text
{chr(10).join(f"- {family}: {global_phase_probe_status_labels[family]}" for family in CONTROL_FAMILIES)}
```

### Specificity interpretation boundary

The probe tests whether global phase centering reduces the global_phase_shift
warning. It does not establish physical time, Lorentz structure, or diagnostic
specificity by itself.

`global_phase_probe_established_specificity` remains `False`.

The LIC01-H probe reports whether global phase centering reduces the
global_phase_shift warning in the current synthetic tau/epsilon diagnostic. It
does not construct `D(A,B)`, does not construct `S_rel2`, and does not create an
interval-like object.

## Residual Control Warning Analysis Readout

### Residual controls analyzed

The LIC01-I residual-control analysis separates the following controls after
global phase centering:

```text
{chr(10).join(f"- {family}: {residual_control_status_labels[family]}" for family in RESIDUAL_CONTROL_FAMILIES)}
```

### Residual warning summary

The residual-control outputs are:

```text
{residual_control_warning_summary_file}
{residual_control_pairwise_comparison_file}
{residual_control_family_correlation_file}
```

`{residual_control_warning_summary_file}` contains `{len(residual_control_summary_rows)}` rows.
`{residual_control_pairwise_comparison_file}` contains `{len(residual_control_pairwise_rows)}` rows.
`{residual_control_family_correlation_file}` contains `{len(residual_control_correlation_rows)}` rows.

Optional seed and label stability outputs were not generated in this run:

```text
{residual_control_seed_sensitivity_file}
{residual_control_label_stability_file}
```

### Cross-control pattern comparison

The analysis compares the centered pairwise response pattern for
`structured_local_phase_response`, `random_phase`,
`amplitude_preserved_phase_randomized`, and `label_shuffle`. It reports
pairwise pattern correlation and top-quartile rank overlap for all six
undirected family pairs.

### Remaining specificity boundary

The residual control analysis separates random_phase, amplitude-preserved
phase-randomized, and label-shuffle warnings after global phase centering. It
does not establish physical time, Lorentz structure, or diagnostic specificity
by itself.

`residual_control_established_specificity` remains `False`.

### Recommended next probes

Recommended residual follow-ups are:

```text
- random_phase: seed_sensitivity_sweep
- amplitude_preserved_phase_randomized: magnitude_phase_component_separation
- label_shuffle: larger_kernel_or_multiple_label_shuffle_stability
```

No `D(A,B)` attachment, `S_rel2` construction, or interval-like object should be
introduced before residual controls are resolved by predefined criteria.

## Claim Boundary

This is a synthetic diagnostic construction only.

`tau_rel_candidate` is not physical time.
`c_eff` is not the physical speed of light.
No Lorentzian metric is derived.
No spacetime validation is claimed.
No experimental or real-data validation is claimed.
"""
    (output_dir / "readout.md").write_text(readout, encoding="utf-8")

    print("QSB-ST-LIC01 synthetic tau/epsilon phase-response run completed.")
    print(f"config: {args.config}")
    print(f"output_dir: {output_dir}")
    print(f"nodes: {len(node_ids)}")
    print(f"pair_count: {len(pairwise_rows)}")
    print(f"sweep_row_count: {len(sweep_rows)}")
    print(f"rho_tau_min: {summary['rho_tau_min']:.12g}")
    print(f"rho_tau_max: {summary['rho_tau_max']:.12g}")
    print(f"tau_rel_candidate_min: {summary['tau_rel_candidate_min']:.12g}")
    print(f"tau_rel_candidate_max: {summary['tau_rel_candidate_max']:.12g}")
    print("claim_boundary: synthetic diagnostic only; no physical time or validation claim.")


if __name__ == "__main__":
    main()
