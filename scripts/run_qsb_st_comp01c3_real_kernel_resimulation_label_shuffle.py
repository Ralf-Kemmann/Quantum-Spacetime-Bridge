#!/usr/bin/env python3
"""
QSB-ST-COMP01-C3 real kernel resimulation label-shuffle scanner.

Synthetic diagnostic scanner only. Psi is a diagnostic pattern object here,
not automatically a physical wavefunction. real_imag_proxy is a diagnostic
component split, not a physical derivation. Component-resolved psi channels
are diagnostic decomposition channels, not physical observables by themselves.
Identity-sensitive contrasts are diagnostic control checks, not physical
observables by themselves. Kernel-level label_shuffle controls are diagnostic
control families, not physical control families. Spectrum-/distribution-matched
controls are methodological null controls, not physical validation tests.
Psi-overlap is a compatibility observable, not automatically a quantum
measurement probability. Tau is not physical time, not proper time, and not a
universal clock. COMP01-C3 does not attach D(A,B), does not construct S_rel2,
does not derive a Lorentzian metric, does not validate a physical Bridge, and
does not establish diagnostic specificity yet.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np

BLOCK = "QSB-ST-COMP01C3"
STATUS = "COMP01C3_real_kernel_resimulation_label_shuffle_implemented_and_run_checked"
CONFIG_PATH = Path("data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml")
COMP01_PATH = Path("scripts/run_qsb_st_comp01_correlation_compatibility_scanner.py")
COMP01B_PATH = Path("scripts/run_qsb_st_comp01b_component_resolved_compatibility.py")
OUTPUT_DIR = Path("runs/QSB-ST-COMP01C3/real_kernel_resimulation_controls_open")
COMPARISON_FOCUS = "structured_local_phase_response_vs_true_label_shuffle_kernel_resimulation"
CONTROL_FAMILY = "true_label_shuffle_kernel_resimulation"
CONTROL_MODE = "kernel_node_label_permutation_fixed_structured_reference"
COMPONENT_SPLIT_MODE = "real_imag_proxy"
ETA = 1e-12
PAIR_COUNT_EXPECTED = 64
TOP_QUARTILE_COUNT = 16
SHUFFLE_SEEDS = list(range(2000, 2020))
PRIMARY_CANDIDATE_METRICS = [
    "sin_sin_overlap",
    "component_resolved_relative_phase_similarity",
]
RANK_CORRELATION_CANDIDATE_THRESHOLD = 0.5
TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD = 0.5
STRONG_RANK_CORRELATION_THRESHOLD = 0.3
STRONG_TOP_QUARTILE_OVERLAP_THRESHOLD = 0.35
MIMIC_RANK_CORRELATION_THRESHOLD = 0.8
MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD = 0.75
SEED_FIELDS = [
    "metric_name",
    "control_family",
    "control_mode",
    "shuffle_seed",
    "permutation_checksum",
    "component_split_mode",
    "pair_count",
    "mean_structured",
    "mean_control",
    "mean_abs_delta",
    "small_delta_threshold",
    "rank_correlation",
    "top_quartile_overlap",
    "identity_sensitive_signal",
    "candidate_signal_status",
    "warning",
]
FEASIBILITY_FIELDS = [
    "control_family",
    "control_mode",
    "feasibility_status",
    "run_status",
    "matched_property",
    "reason",
    "recommended_followup",
    "warning",
]
DECISION_FIELDS = [
    "metric_name",
    "tested_control_families",
    "stable_control_families",
    "failed_control_families",
    "candidate_signal_count_true_label_shuffle",
    "seed_count_true_label_shuffle",
    "candidate_signal_fraction_true_label_shuffle",
    "mean_rank_correlation_true_label_shuffle",
    "std_rank_correlation_true_label_shuffle",
    "mean_top_quartile_overlap_true_label_shuffle",
    "std_top_quartile_overlap_true_label_shuffle",
    "decision_status",
    "recommended_followup",
    "specificity_status",
    "warning",
]
CLAIM_BOUNDARY = (
    "synthetic kernel-level label_shuffle diagnostic control only; "
    "kernel-level label_shuffle controls are diagnostic control families, not "
    "physical control families; Spectrum-/distribution-matched controls are "
    "methodological null controls, not physical validation tests; "
    "real_imag_proxy is a diagnostic component split, not a physical "
    "derivation; psi is diagnostic pattern object, not physical wavefunction; "
    "component-resolved psi channels are diagnostic decomposition channels, "
    "not physical observables by themselves; identity-sensitive contrasts are "
    "diagnostic control checks, not physical observables by themselves; "
    "psi-overlap is a compatibility observable, not automatically a quantum "
    "measurement probability; tau is not physical time, not proper time, and "
    "not a universal clock; COMP01-C3 does not attach D(A,B), does not "
    "construct S_rel2, does not derive a Lorentzian metric, does not validate "
    "a physical Bridge, and does not establish diagnostic specificity yet; "
    "this is synthetic diagnostic work only."
)

PairId = Tuple[str, str]


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module spec: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_config_value(cfg: Dict[str, Any], path: Iterable[str], default: Any) -> Any:
    current: Any = cfg
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def permutation_checksum(permutation: np.ndarray) -> str:
    encoded = ",".join(map(str, permutation.tolist())).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def rank_descending(values: Dict[PairId, float]) -> Tuple[Dict[PairId, float], bool]:
    sorted_items = sorted(values.items(), key=lambda item: (-item[1], item[0][0], item[0][1]))
    ranks: Dict[PairId, float] = {}
    tie_found = False
    idx = 0
    while idx < len(sorted_items):
        jdx = idx + 1
        while jdx < len(sorted_items) and sorted_items[jdx][1] == sorted_items[idx][1]:
            jdx += 1
        if jdx - idx > 1:
            tie_found = True
        rank_value = (idx + 1 + jdx) / 2.0
        for pair, _value in sorted_items[idx:jdx]:
            ranks[pair] = rank_value
        idx = jdx
    return ranks, tie_found


def pearson_rank_correlation(
    structured_ranks: Sequence[float],
    control_ranks: Sequence[float],
) -> Optional[float]:
    rank_s = np.asarray(structured_ranks, dtype=float)
    rank_c = np.asarray(control_ranks, dtype=float)
    std_s = float(np.std(rank_s))
    std_c = float(np.std(rank_c))
    if std_s <= ETA or std_c <= ETA:
        return None
    centered_s = rank_s - float(np.mean(rank_s))
    centered_c = rank_c - float(np.mean(rank_c))
    corr = float(np.mean(centered_s * centered_c) / (std_s * std_c))
    if not math.isfinite(corr):
        return None
    return corr


def format_float(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.12g}"


def joined_warnings(parts: Iterable[str]) -> str:
    clean = [part for part in parts if part]
    return ";".join(dict.fromkeys(clean))


def compute_pair_metric_values(
    node_ids: Sequence[str],
    kernel: np.ndarray,
    comp01: Any,
    comp01b: Any,
    eta: float,
) -> Tuple[Dict[str, Dict[PairId, float]], List[str]]:
    metric_values: Dict[str, Dict[PairId, float]] = {
        metric: {} for metric in PRIMARY_CANDIDATE_METRICS
    }
    warnings: List[str] = []
    for source_idx, source_id in enumerate(node_ids):
        psi_i = comp01.psi_fingerprint(kernel, source_idx)
        for target_idx, target_id in enumerate(node_ids):
            psi_j = comp01.psi_fingerprint(kernel, target_idx)
            values, warning = comp01b.compute_component_metrics(psi_i, psi_j, eta)
            pair = (source_id, target_id)
            for metric in PRIMARY_CANDIDATE_METRICS:
                metric_values[metric][pair] = float(values[metric])
            if warning:
                warnings.append(warning)
    return metric_values, warnings


def seed_status(
    identity_signal: bool,
    rank_correlation: Optional[float],
    top_quartile_overlap: float,
    mean_abs_delta: float,
    small_delta_threshold: float,
) -> str:
    if rank_correlation is None:
        return "undefined_seed"
    if identity_signal:
        return "identity_sensitive_candidate_seed"
    if (
        rank_correlation >= MIMIC_RANK_CORRELATION_THRESHOLD
        and top_quartile_overlap >= MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "label_shuffle_mimic_warning_seed"
    if (
        rank_correlation < RANK_CORRELATION_CANDIDATE_THRESHOLD
        or top_quartile_overlap <= TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD
    ) and mean_abs_delta <= small_delta_threshold:
        return "rank_shift_without_magnitude_warning_seed"
    return "inconclusive_seed"


def decision_status(
    candidate_signal_fraction: float,
    mean_rank_correlation: Optional[float],
    mean_top_quartile_overlap: float,
) -> str:
    if mean_rank_correlation is None:
        return "inconclusive_control_result"
    if (
        candidate_signal_fraction >= 0.8
        and mean_rank_correlation < STRONG_RANK_CORRELATION_THRESHOLD
        and mean_top_quartile_overlap <= STRONG_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "strong_candidate_survives_true_label_shuffle"
    if (
        candidate_signal_fraction >= 0.6
        and mean_rank_correlation < RANK_CORRELATION_CANDIDATE_THRESHOLD
        and mean_top_quartile_overlap <= TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD
    ):
        return "candidate_survives_true_label_shuffle"
    if (
        mean_rank_correlation >= MIMIC_RANK_CORRELATION_THRESHOLD
        and mean_top_quartile_overlap >= MIMIC_TOP_QUARTILE_OVERLAP_THRESHOLD
    ):
        return "label_shuffle_mimic_warning"
    return "inconclusive_control_result"


def recommended_followup(status: str) -> str:
    if status == "strong_candidate_survives_true_label_shuffle":
        return "proceed_to_spectrum_distribution_matched_controls"
    if status == "candidate_survives_true_label_shuffle":
        return "inspect_with_spectrum_distribution_matched_controls"
    if status == "label_shuffle_mimic_warning":
        return "redesign_or_deprioritize_metric"
    return "inspect_but_do_not_promote_metric"


def mean_optional(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return float(np.mean(clean))


def std_optional(values: Sequence[Optional[float]]) -> Optional[float]:
    clean = [value for value in values if value is not None]
    if not clean:
        return None
    return float(np.std(clean))


def compute_seed_metric_row(
    metric: str,
    seed: int,
    checksum: str,
    structured_values: Dict[PairId, float],
    control_values: Dict[PairId, float],
    structured_ranks: Dict[PairId, float],
    structured_tie: bool,
) -> Dict[str, Any]:
    pairs = sorted(set(structured_values) & set(control_values))
    control_ranks, control_tie = rank_descending({pair: control_values[pair] for pair in pairs})
    rank_correlation = pearson_rank_correlation(
        [structured_ranks[pair] for pair in pairs],
        [control_ranks[pair] for pair in pairs],
    )
    structured_top = {
        pair for pair in pairs if structured_ranks[pair] <= TOP_QUARTILE_COUNT
    }
    control_top = {
        pair for pair in pairs if control_ranks[pair] <= TOP_QUARTILE_COUNT
    }
    top_overlap = len(structured_top & control_top) / float(TOP_QUARTILE_COUNT)
    structured_mean = float(np.mean([structured_values[pair] for pair in pairs]))
    control_mean = float(np.mean([control_values[pair] for pair in pairs]))
    abs_deltas = [abs(structured_values[pair] - control_values[pair]) for pair in pairs]
    mean_abs_delta = float(np.mean(abs_deltas))
    small_delta_threshold = max(
        ETA,
        0.05 * max(abs(structured_mean), abs(control_mean), ETA),
    )
    identity_signal = (
        mean_abs_delta > small_delta_threshold
        and rank_correlation is not None
        and rank_correlation < RANK_CORRELATION_CANDIDATE_THRESHOLD
        and top_overlap <= TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD
    )
    warnings: List[str] = []
    if structured_tie or control_tie:
        warnings.append("rank_tie_warning")
    if rank_correlation is None:
        warnings.append("undefined_rank_warning")
    return {
        "metric_name": metric,
        "control_family": CONTROL_FAMILY,
        "control_mode": CONTROL_MODE,
        "shuffle_seed": seed,
        "permutation_checksum": checksum,
        "component_split_mode": COMPONENT_SPLIT_MODE,
        "pair_count": len(pairs),
        "mean_structured": structured_mean,
        "mean_control": control_mean,
        "mean_abs_delta": mean_abs_delta,
        "small_delta_threshold": small_delta_threshold,
        "rank_correlation": rank_correlation,
        "top_quartile_overlap": top_overlap,
        "identity_sensitive_signal": identity_signal,
        "candidate_signal_status": seed_status(
            identity_signal,
            rank_correlation,
            top_overlap,
            mean_abs_delta,
            small_delta_threshold,
        ),
        "warning": joined_warnings(warnings),
    }


def build_decision_rows(seed_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for metric in PRIMARY_CANDIDATE_METRICS:
        metric_rows = [row for row in seed_rows if row["metric_name"] == metric]
        candidate_count = sum(
            1
            for row in metric_rows
            if row["candidate_signal_status"] == "identity_sensitive_candidate_seed"
        )
        seed_count = len(metric_rows)
        candidate_fraction = candidate_count / float(seed_count)
        rank_corrs = [row["rank_correlation"] for row in metric_rows]
        top_overlaps = [float(row["top_quartile_overlap"]) for row in metric_rows]
        mean_rank_corr = mean_optional(rank_corrs)
        mean_top_overlap = float(np.mean(top_overlaps))
        status = decision_status(candidate_fraction, mean_rank_corr, mean_top_overlap)
        stable = CONTROL_FAMILY if status in {
            "strong_candidate_survives_true_label_shuffle",
            "candidate_survives_true_label_shuffle",
        } else ""
        failed = "" if stable else CONTROL_FAMILY
        rows.append(
            {
                "metric_name": metric,
                "tested_control_families": CONTROL_FAMILY,
                "stable_control_families": stable,
                "failed_control_families": failed,
                "candidate_signal_count_true_label_shuffle": candidate_count,
                "seed_count_true_label_shuffle": seed_count,
                "candidate_signal_fraction_true_label_shuffle": candidate_fraction,
                "mean_rank_correlation_true_label_shuffle": mean_rank_corr,
                "std_rank_correlation_true_label_shuffle": std_optional(rank_corrs),
                "mean_top_quartile_overlap_true_label_shuffle": mean_top_overlap,
                "std_top_quartile_overlap_true_label_shuffle": float(np.std(top_overlaps)),
                "decision_status": status,
                "recommended_followup": recommended_followup(status),
                "specificity_status": "specificity_not_established",
                "warning": joined_warnings(str(row["warning"]) for row in metric_rows),
            }
        )
    return rows


def build_feasibility_rows() -> List[Dict[str, str]]:
    return [
        {
            "control_family": "true_label_shuffle_kernel_resimulation",
            "control_mode": CONTROL_MODE,
            "feasibility_status": "feasible",
            "run_status": "run",
            "matched_property": "kernel_node_label_permutation",
            "reason": "P K P^T node-label permutation was generated per seed with fixed structured reference.",
            "recommended_followup": "inspect_seed_decisions_then_add_distribution_and_spectrum_controls",
            "warning": "kernel_isomorphism_limitation_warning",
        },
        {
            "control_family": "distribution_matched_label_shuffle",
            "control_mode": "distribution_matched_control_feasibility",
            "feasibility_status": "planned_not_run",
            "run_status": "not_run_feasibility_only",
            "matched_property": "metric_distribution",
            "reason": "Distribution-matched control is planned but not run in this minimal C3 implementation.",
            "recommended_followup": "implement_distribution_matched_control_if_true_label_shuffle_survives",
            "warning": "",
        },
        {
            "control_family": "spectrum_matched_label_shuffle",
            "control_mode": "spectrum_matched_control_feasibility",
            "feasibility_status": "planned_not_run",
            "run_status": "not_run_feasibility_only",
            "matched_property": "kernel_spectrum",
            "reason": "Spectrum-matched control is planned but not run in this minimal C3 implementation.",
            "recommended_followup": "implement_spectrum_matched_control_if_true_label_shuffle_survives",
            "warning": "",
        },
    ]


def write_csv(path: Path, fields: Sequence[str], rows: Sequence[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fields))
        writer.writeheader()
        for row in rows:
            formatted = {
                key: format_float(value) if isinstance(value, float) else value
                for key, value in row.items()
            }
            writer.writerow(formatted)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_readout(
    path: Path,
    decision_rows: Sequence[Dict[str, Any]],
    feasibility_rows: Sequence[Dict[str, str]],
    stable_metrics: Sequence[str],
    failed_metrics: Sequence[str],
    mimic_metrics: Sequence[str],
) -> None:
    decision_lines = [
        f"- {row['metric_name']}: {row['decision_status']}, "
        f"candidate_signal_fraction={row['candidate_signal_fraction_true_label_shuffle']}"
        for row in decision_rows
    ]
    feasibility_lines = [
        f"- {row['control_family']}: {row['feasibility_status']}, {row['run_status']}"
        for row in feasibility_rows
    ]
    text = f"""# QSB-ST-COMP01-C3 Real Kernel Resimulation Label-Shuffle Readout

## Purpose

The COMP01-C3 scanner tests whether the two COMP01-C2-stable candidate metrics remain stable under deterministic kernel-level node-label permutation controls. This is a synthetic diagnostic kernel-level control, not a physical control family. It does not establish physical wavefunctions, physical time, Lorentz structure, D(A,B), S_rel2, or Bridge validation.

## Control family

{CONTROL_FAMILY}

## Control mode

{CONTROL_MODE}

The control kernel is generated as P K P^T from the structured synthetic kernel for each seed. Pair identities are kept fixed against the structured reference. This is a kernel-level diagnostic control because the fingerprint and component metrics are recomputed from the permuted kernel, not from permuted metric values. Limitation: a pure matrix permutation preserves isomorphic kernel structure and remains a minimal synthetic control.

## Component split mode

{COMPONENT_SPLIT_MODE}

real_imag_proxy is a diagnostic component split, not a physical derivation.

## Candidate metrics

{chr(10).join(f"- {metric}" for metric in PRIMARY_CANDIDATE_METRICS)}

## Output files

- {OUTPUT_DIR / "real_kernel_label_shuffle_seed_summary.csv"}
- {OUTPUT_DIR / "control_family_feasibility_summary.csv"}
- {OUTPUT_DIR / "candidate_metric_control_decision.csv"}
- {OUTPUT_DIR / "summary.json"}
- {OUTPUT_DIR / "readout.md"}
- {OUTPUT_DIR / "config_resolved.json"}

## Kernel-level label_shuffle summary

{chr(10).join(decision_lines)}

## Candidate movement

- stable_candidate_metrics: {list(stable_metrics)}
- failed_or_inconclusive_metrics: {list(failed_metrics)}
- label_shuffle_mimic_warning_metrics: {list(mimic_metrics)}

## Feasibility notes for harder controls

{chr(10).join(feasibility_lines)}

## Warnings

- The structured reference is fixed.
- The operation used is P K P^T with fixed pair identities.
- A pure permutation preserves isomorphic kernel structure and remains a limited diagnostic control.

## Claim Boundary

{CLAIM_BOUNDARY}
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    comp01 = load_module("comp01_runner", COMP01_PATH)
    comp01b = load_module("comp01b_runner", COMP01B_PATH)
    lic01 = comp01.load_lic01_module()
    cfg = lic01.load_config(CONFIG_PATH)
    eta = float(get_config_value(cfg, ["response", "eta"], ETA))
    seed = int(get_config_value(cfg, ["reproducibility", "random_seed"], 17052026))
    node_ids, base_kernel = lic01.build_synthetic_kernel(seed)
    if COMPONENT_SPLIT_MODE != "real_imag_proxy":
        raise SystemExit("component_split_mode must be real_imag_proxy")

    structured_metric_values, _structured_warnings = compute_pair_metric_values(
        node_ids, base_kernel, comp01, comp01b, eta
    )
    structured_ranks: Dict[str, Dict[PairId, float]] = {}
    structured_ties: Dict[str, bool] = {}
    for metric in PRIMARY_CANDIDATE_METRICS:
        structured_ranks[metric], structured_ties[metric] = rank_descending(
            structured_metric_values[metric]
        )

    seed_rows: List[Dict[str, Any]] = []
    for shuffle_seed in SHUFFLE_SEEDS:
        rng = np.random.default_rng(shuffle_seed)
        permutation = rng.permutation(len(node_ids))
        checksum = permutation_checksum(permutation)
        control_kernel = base_kernel[np.ix_(permutation, permutation)]
        control_metric_values, _control_warnings = compute_pair_metric_values(
            node_ids, control_kernel, comp01, comp01b, eta
        )
        for metric in PRIMARY_CANDIDATE_METRICS:
            seed_rows.append(
                compute_seed_metric_row(
                    metric,
                    shuffle_seed,
                    checksum,
                    structured_metric_values[metric],
                    control_metric_values[metric],
                    structured_ranks[metric],
                    structured_ties[metric],
                )
            )

    feasibility_rows = build_feasibility_rows()
    decision_rows = build_decision_rows(seed_rows)
    stable_metrics = [
        str(row["metric_name"])
        for row in decision_rows
        if row["decision_status"]
        in {
            "strong_candidate_survives_true_label_shuffle",
            "candidate_survives_true_label_shuffle",
        }
    ]
    mimic_metrics = [
        str(row["metric_name"])
        for row in decision_rows
        if row["decision_status"] == "label_shuffle_mimic_warning"
    ]
    failed_metrics = [
        str(row["metric_name"])
        for row in decision_rows
        if row["metric_name"] not in stable_metrics and row["metric_name"] not in mimic_metrics
    ]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv(OUTPUT_DIR / "real_kernel_label_shuffle_seed_summary.csv", SEED_FIELDS, seed_rows)
    write_csv(
        OUTPUT_DIR / "control_family_feasibility_summary.csv",
        FEASIBILITY_FIELDS,
        feasibility_rows,
    )
    write_csv(
        OUTPUT_DIR / "candidate_metric_control_decision.csv",
        DECISION_FIELDS,
        decision_rows,
    )

    summary = {
        "block": BLOCK,
        "status": STATUS,
        "output_dir": str(OUTPUT_DIR),
        "comparison_focus": COMPARISON_FOCUS,
        "control_family": CONTROL_FAMILY,
        "control_mode": CONTROL_MODE,
        "component_split_mode": COMPONENT_SPLIT_MODE,
        "seed_count": len(SHUFFLE_SEEDS),
        "shuffle_seeds": SHUFFLE_SEEDS,
        "pair_count": PAIR_COUNT_EXPECTED,
        "primary_metric_count": len(PRIMARY_CANDIDATE_METRICS),
        "real_kernel_label_shuffle_seed_summary_row_count": len(seed_rows),
        "control_family_feasibility_summary_row_count": len(feasibility_rows),
        "candidate_metric_control_decision_row_count": len(decision_rows),
        "primary_candidate_metrics": PRIMARY_CANDIDATE_METRICS,
        "stable_candidate_metrics": stable_metrics,
        "failed_or_inconclusive_metrics": failed_metrics,
        "label_shuffle_mimic_warning_metrics": mimic_metrics,
        "specificity_established": False,
        "tau_model_constructed": False,
        "D_AB_attached": False,
        "S_rel2_constructed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(OUTPUT_DIR / "summary.json", summary)

    config = {
        "block": BLOCK,
        "output_dir": str(OUTPUT_DIR),
        "comparison_focus": COMPARISON_FOCUS,
        "control_family": CONTROL_FAMILY,
        "control_mode": CONTROL_MODE,
        "component_split_mode": COMPONENT_SPLIT_MODE,
        "primary_candidate_metrics": PRIMARY_CANDIDATE_METRICS,
        "seed_count": len(SHUFFLE_SEEDS),
        "shuffle_seeds": SHUFFLE_SEEDS,
        "pair_count_expected": PAIR_COUNT_EXPECTED,
        "top_quartile_count": TOP_QUARTILE_COUNT,
        "rank_correlation_method": "pearson_on_descending_value_ranks",
        "ranking_method": "deterministic_average_rank_descending",
        "small_delta_threshold_rule": (
            "max(1e-12, 0.05 * max(abs(mean_structured), "
            "abs(mean_control), 1e-12))"
        ),
        "rank_correlation_candidate_threshold": RANK_CORRELATION_CANDIDATE_THRESHOLD,
        "top_quartile_overlap_candidate_threshold": TOP_QUARTILE_OVERLAP_CANDIDATE_THRESHOLD,
        "strong_rank_correlation_threshold": STRONG_RANK_CORRELATION_THRESHOLD,
        "strong_top_quartile_overlap_threshold": STRONG_TOP_QUARTILE_OVERLAP_THRESHOLD,
        "permutation_checksum_method": "sha256_first16_of_permutation_csv",
        "specificity_default": False,
    }
    write_json(OUTPUT_DIR / "config_resolved.json", config)
    write_readout(
        OUTPUT_DIR / "readout.md",
        decision_rows,
        feasibility_rows,
        stable_metrics,
        failed_metrics,
        mimic_metrics,
    )

    print(STATUS)
    print(f"output_dir: {OUTPUT_DIR}")
    print(f"control_family: {CONTROL_FAMILY}")
    print(f"control_mode: {CONTROL_MODE}")
    print(f"seed_count: {len(SHUFFLE_SEEDS)}")
    print(f"real_kernel_label_shuffle_seed_summary_row_count: {len(seed_rows)}")
    print(f"control_family_feasibility_summary_row_count: {len(feasibility_rows)}")
    print(f"candidate_metric_control_decision_row_count: {len(decision_rows)}")
    print(f"stable_candidate_metrics: {stable_metrics}")
    print(f"failed_or_inconclusive_metrics: {failed_metrics}")
    print(f"label_shuffle_mimic_warning_metrics: {mimic_metrics}")
    print("specificity_established: False")


if __name__ == "__main__":
    main()
