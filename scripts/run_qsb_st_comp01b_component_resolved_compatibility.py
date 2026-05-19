#!/usr/bin/env python3
"""
QSB-ST-COMP01-B component-resolved compatibility inspection scanner.

Synthetic diagnostic scanner only. Psi is a diagnostic pattern object here,
not automatically a physical wavefunction. Component-resolved psi channels
are diagnostic decomposition channels, not physical observables by themselves.
Tau is not physical time, proper time, or a universal clock. COMP01-B does
not attach D(A,B), does not construct S_rel2, and does not establish
diagnostic specificity yet.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import numpy as np

CONFIG_PATH = Path("data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml")
COMP01_RUNNER_PATH = Path("scripts/run_qsb_st_comp01_correlation_compatibility_scanner.py")
OUTPUT_DIR = Path("runs/QSB-ST-COMP01B/component_resolved_compatibility_open")
COMPONENT_SPLIT_MODE = "real_imag_proxy"

STRUCTURED_FAMILY = "structured_local_phase_response"
CONTROL_FAMILIES = [
    "global_phase_shift",
    "random_phase",
    "amplitude_preserved_phase_randomized",
    "label_shuffle",
]
FAMILIES = [STRUCTURED_FAMILY] + CONTROL_FAMILIES
METRICS = [
    "cos_cos_overlap",
    "sin_sin_overlap",
    "cos_sin_cross_overlap",
    "sin_cos_cross_overlap",
    "component_balance_ratio",
    "component_asymmetry_delta",
    "component_resolved_relative_phase_similarity",
    "component_resolved_local_pattern_correlation",
]
PAIRWISE_FIELDS = [
    "family",
    "source_id",
    "target_id",
    "cos_cos_overlap",
    "sin_sin_overlap",
    "cos_sin_cross_overlap",
    "sin_cos_cross_overlap",
    "component_balance_ratio",
    "component_asymmetry_delta",
    "component_resolved_relative_phase_similarity",
    "component_resolved_local_pattern_correlation",
    "component_split_mode",
    "control_status",
    "warning",
]
FAMILY_SUMMARY_FIELDS = [
    "family",
    "pair_count",
    "cos_cos_overlap_mean",
    "sin_sin_overlap_mean",
    "cos_sin_cross_overlap_mean",
    "sin_cos_cross_overlap_mean",
    "component_balance_ratio_mean",
    "component_asymmetry_delta_mean",
    "component_resolved_relative_phase_similarity_mean",
    "component_resolved_local_pattern_correlation_mean",
    "component_split_mode",
    "structured_vs_control_separation_status",
    "warning",
]
CONTRAST_FIELDS = [
    "control_family",
    "metric_name",
    "structured_mean",
    "control_mean",
    "delta",
    "ratio",
    "effect_direction",
    "separation_status",
    "warning",
]
CLAIM_BOUNDARY = (
    "Synthetic diagnostic component-resolved compatibility scanner only; psi "
    "is a diagnostic pattern object, not physical wavefunction; component "
    "channels are diagnostic decomposition channels, not physical observables "
    "by themselves; psi-overlap is a compatibility observable, not "
    "automatically a quantum measurement probability; tau is not physical "
    "time, not proper time, and not a universal clock; COMP01-B does not "
    "attach D(A,B), does not construct S_rel2, does not derive a Lorentzian "
    "metric, does not validate a physical Bridge, and does not establish "
    "diagnostic specificity yet."
)


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


def component_split(psi: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Return real/imag diagnostic proxy components for a complex fingerprint."""
    return psi.real.astype(float), psi.imag.astype(float)


def vector_overlap(vec_a: np.ndarray, vec_b: np.ndarray, eta: float) -> Tuple[float, str]:
    norm_a = float(np.linalg.norm(vec_a))
    norm_b = float(np.linalg.norm(vec_b))
    warning = ""
    if norm_a <= eta or norm_b <= eta:
        warning = "zero_norm_warning"
    value = abs(float(np.dot(vec_a, vec_b))) / (norm_a * norm_b + eta)
    return float(value), warning


def component_balance(vec_c: np.ndarray, vec_s: np.ndarray, eta: float) -> Tuple[float, str]:
    norm_c = float(np.linalg.norm(vec_c))
    norm_s = float(np.linalg.norm(vec_s))
    warning = ""
    if norm_c <= eta or norm_s <= eta:
        warning = "zero_norm_warning"
    value = (norm_c - norm_s) / (norm_c + norm_s + eta)
    return float(value), warning


def component_phase_pattern(vec_c: np.ndarray, vec_s: np.ndarray, eta: float) -> Tuple[np.ndarray, str]:
    support = (np.abs(vec_c) > eta) | (np.abs(vec_s) > eta)
    if not bool(np.any(support)):
        return np.zeros_like(vec_c, dtype=float), "metric_degenerate_warning"
    phase = np.arctan2(vec_s, vec_c)
    reference_idx = int(np.flatnonzero(support)[0])
    centered = np.angle(np.exp(1j * (phase - phase[reference_idx])))
    return centered, ""


def component_relative_phase_similarity(
    c_i: np.ndarray,
    s_i: np.ndarray,
    c_j: np.ndarray,
    s_j: np.ndarray,
    eta: float,
) -> Tuple[float, str]:
    phase_i, warning_i = component_phase_pattern(c_i, s_i, eta)
    phase_j, warning_j = component_phase_pattern(c_j, s_j, eta)
    support_i = (np.abs(c_i) > eta) | (np.abs(s_i) > eta)
    support_j = (np.abs(c_j) > eta) | (np.abs(s_j) > eta)
    support = support_i & support_j
    if not bool(np.any(support)):
        return 0.0, "metric_degenerate_warning"
    value = float(np.mean(np.cos(phase_i[support] - phase_j[support])))
    warning = ";".join(part for part in [warning_i, warning_j] if part)
    return value, warning


def component_local_pattern_correlation(
    c_i: np.ndarray,
    s_i: np.ndarray,
    c_j: np.ndarray,
    s_j: np.ndarray,
    eta: float,
) -> Tuple[float, str]:
    vec_i = np.concatenate([c_i, s_i])
    vec_j = np.concatenate([c_j, s_j])
    std_i = float(np.std(vec_i))
    std_j = float(np.std(vec_j))
    if std_i <= eta or std_j <= eta:
        return 0.0, "metric_degenerate_warning"
    corr = float(np.corrcoef(vec_i, vec_j)[0, 1])
    if not math.isfinite(corr):
        return 0.0, "metric_degenerate_warning"
    return corr, ""


def compute_component_metrics(
    psi_i: np.ndarray,
    psi_j: np.ndarray,
    eta: float,
) -> Tuple[Dict[str, float], str]:
    c_i, s_i = component_split(psi_i)
    c_j, s_j = component_split(psi_j)
    warnings = ["component_proxy_warning"]

    o_cc, warning = vector_overlap(c_i, c_j, eta)
    if warning:
        warnings.append(f"cos_cos_overlap:{warning}")
    o_ss, warning = vector_overlap(s_i, s_j, eta)
    if warning:
        warnings.append(f"sin_sin_overlap:{warning}")
    o_cs, warning = vector_overlap(c_i, s_j, eta)
    if warning:
        warnings.append(f"cos_sin_cross_overlap:{warning}")
    o_sc, warning = vector_overlap(s_i, c_j, eta)
    if warning:
        warnings.append(f"sin_cos_cross_overlap:{warning}")

    balance_i, warning_i = component_balance(c_i, s_i, eta)
    balance_j, warning_j = component_balance(c_j, s_j, eta)
    if warning_i or warning_j:
        warnings.append("component_balance_ratio:zero_norm_warning")
    balance_pair = 0.5 * (balance_i + balance_j)

    relative_phase, warning = component_relative_phase_similarity(c_i, s_i, c_j, s_j, eta)
    if warning:
        warnings.append(f"component_resolved_relative_phase_similarity:{warning}")
    local_corr, warning = component_local_pattern_correlation(c_i, s_i, c_j, s_j, eta)
    if warning:
        warnings.append(f"component_resolved_local_pattern_correlation:{warning}")

    values = {
        "cos_cos_overlap": o_cc,
        "sin_sin_overlap": o_ss,
        "cos_sin_cross_overlap": o_cs,
        "sin_cos_cross_overlap": o_sc,
        "component_balance_ratio": balance_pair,
        "component_asymmetry_delta": (o_cc + o_ss) - (o_cs + o_sc),
        "component_resolved_relative_phase_similarity": relative_phase,
        "component_resolved_local_pattern_correlation": local_corr,
    }
    return values, ";".join(warnings)


def write_csv(path: Path, fieldnames: List[str], rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def mean_metric(rows: List[Dict[str, Any]], metric: str) -> float:
    values = [float(row[metric]) for row in rows]
    return float(sum(values) / len(values)) if values else 0.0


def classify_contrast(structured_mean: float, control_mean: float, eta: float) -> Tuple[str, str]:
    delta = structured_mean - control_mean
    if not math.isfinite(structured_mean) or not math.isfinite(control_mean):
        return "undefined", "undefined_contrast_warning"
    if structured_mean > control_mean * 1.10:
        return "structured_greater", "structured_separates_from_control_candidate"
    if control_mean > structured_mean:
        return "control_greater", "control_exceeds_or_matches_structured_warning"
    if abs(delta) <= 0.10 * max(abs(structured_mean), abs(control_mean), eta):
        return "near_equal", "near_equal_no_separation"
    return "structured_greater", "weak_or_inconclusive_separation"


def format_float(value: float) -> str:
    return f"{value:.12g}"


def build_readout(
    summary: Dict[str, Any],
    contrast_rows: List[Dict[str, Any]],
    output_files: List[str],
) -> str:
    moved = [
        f"{row['metric_name']} vs {row['control_family']}"
        for row in contrast_rows
        if row["separation_status"] == "structured_separates_from_control_candidate"
    ]
    control_warnings = [
        f"{row['metric_name']} vs {row['control_family']}"
        for row in contrast_rows
        if row["separation_status"] == "control_exceeds_or_matches_structured_warning"
    ]
    near_equal = [
        f"{row['metric_name']} vs {row['control_family']}"
        for row in contrast_rows
        if row["separation_status"] == "near_equal_no_separation"
    ]
    return f"""# QSB-ST-COMP01-B Component-Resolved Compatibility Inspection Readout

## Purpose

The COMP01-B scanner tests diagnostic component-resolved psi(i)-psi(j)
compatibility candidates against synthetic controls. Component channels are
diagnostic decomposition channels, not physical observables by themselves. It
does not establish physical wavefunctions, physical time, Lorentz structure,
D(A,B), S_rel2, or Bridge validation.

## Input basis

- Config: `{CONFIG_PATH}`
- COMP01 scanner functions reused without modifying COMP01 outputs: `{COMP01_RUNNER_PATH}`
- Family count: {summary['family_count']}
- Pair count per family: {summary['pair_count']}
- Total pairwise rows: {summary['pairwise_row_count']}

## Component split mode

`{summary['component_split_mode']}`

The scanner uses the real part of the complex fingerprint as a cosine-like /
in-phase proxy and the imaginary part as a sine-like / quadrature proxy.

For pair values, `component_balance_ratio` is the mean of the source and target
single-fingerprint balance values.

## Component metrics

```text
{chr(10).join(summary['metrics'])}
```

## Output files

```text
{chr(10).join(output_files)}
```

## First-pass component contrast summary

```text
best_candidate_metrics: {summary['best_candidate_metrics']}
warning_metrics: {summary['warning_metrics']}
specificity_established: {summary['specificity_established']}
```

## Candidate movement

Metrics with `structured_separates_from_control_candidate`:

```text
{chr(10).join(moved) if moved else 'none'}
```

Metrics with `control_exceeds_or_matches_structured_warning`:

```text
{chr(10).join(control_warnings) if control_warnings else 'none'}
```

Metrics with `near_equal_no_separation`:

```text
{chr(10).join(near_equal) if near_equal else 'none'}
```

## Warnings

- Component split mode is a diagnostic `real_imag_proxy`.
- No tau model is constructed.
- No physical combined score is defined.
- Controls are first-pass synthetic controls only.
- Candidate movement is not a specificity claim.

## Claim Boundary

Psi is a diagnostic pattern object here, not automatically a physical
wavefunction.

Component-resolved psi channels are diagnostic decomposition channels, not
physical observables by themselves.

Psi-overlap is a compatibility observable, not automatically a quantum
measurement probability.

Tau is not physical time.

Tau is not proper time.

Tau is not a universal clock.

COMP01-B does not attach D(A,B).

COMP01-B does not construct S_rel2.

COMP01-B does not derive a Lorentzian metric.

COMP01-B does not validate a physical Bridge.

COMP01-B does not establish diagnostic specificity yet.

This is synthetic diagnostic work only.
"""


def main() -> None:
    comp01 = load_module("comp01_runner", COMP01_RUNNER_PATH)
    lic01 = comp01.load_lic01_module()
    cfg = lic01.load_config(CONFIG_PATH)
    eta = float(get_config_value(cfg, ["response", "eta"], 1.0e-12))
    seed = int(get_config_value(cfg, ["reproducibility", "random_seed"], 17052026))

    node_ids, base_kernel = lic01.build_synthetic_kernel(seed)
    family_kernels = comp01.build_family_kernels(base_kernel, seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pairwise_rows: List[Dict[str, Any]] = []
    for family in FAMILIES:
        kernel = family_kernels[family]
        control_status = "structured_reference" if family == STRUCTURED_FAMILY else "control"
        for source_idx, source_id in enumerate(node_ids):
            psi_i = comp01.psi_fingerprint(kernel, source_idx)
            for target_idx, target_id in enumerate(node_ids):
                psi_j = comp01.psi_fingerprint(kernel, target_idx)
                metrics, warning = compute_component_metrics(psi_i, psi_j, eta)
                row: Dict[str, Any] = {
                    "family": family,
                    "source_id": source_id,
                    "target_id": target_id,
                    "component_split_mode": COMPONENT_SPLIT_MODE,
                    "control_status": control_status,
                    "warning": warning,
                }
                row.update({metric: format_float(metrics[metric]) for metric in METRICS})
                pairwise_rows.append(row)

    rows_by_family = {
        family: [row for row in pairwise_rows if row["family"] == family] for family in FAMILIES
    }

    family_summary_rows: List[Dict[str, Any]] = []
    family_means: Dict[str, Dict[str, float]] = {}
    for family in FAMILIES:
        means = {metric: mean_metric(rows_by_family[family], metric) for metric in METRICS}
        family_means[family] = means
        row: Dict[str, Any] = {
            "family": family,
            "pair_count": len(rows_by_family[family]),
            "component_split_mode": COMPONENT_SPLIT_MODE,
            "structured_vs_control_separation_status": (
                "structured_reference_baseline" if family == STRUCTURED_FAMILY else "pending_contrast"
            ),
            "warning": "component_proxy_warning",
        }
        for metric in METRICS:
            row[f"{metric}_mean"] = format_float(means[metric])
        family_summary_rows.append(row)

    contrast_rows: List[Dict[str, Any]] = []
    structured_means = family_means[STRUCTURED_FAMILY]
    for control_family in CONTROL_FAMILIES:
        for metric in METRICS:
            structured_mean = structured_means[metric]
            control_mean = family_means[control_family][metric]
            delta = structured_mean - control_mean
            ratio = structured_mean / (control_mean + eta)
            direction, status = classify_contrast(structured_mean, control_mean, eta)
            contrast_rows.append(
                {
                    "control_family": control_family,
                    "metric_name": metric,
                    "structured_mean": format_float(structured_mean),
                    "control_mean": format_float(control_mean),
                    "delta": format_float(delta),
                    "ratio": format_float(ratio),
                    "effect_direction": direction,
                    "separation_status": status,
                    "warning": "" if status.endswith("_candidate") else status,
                }
            )

    statuses_by_family = {family: [] for family in CONTROL_FAMILIES}
    for row in contrast_rows:
        statuses_by_family[row["control_family"]].append(row["separation_status"])
    for row in family_summary_rows:
        family = row["family"]
        if family == STRUCTURED_FAMILY:
            continue
        statuses = statuses_by_family[family]
        if any(status == "control_exceeds_or_matches_structured_warning" for status in statuses):
            row["structured_vs_control_separation_status"] = "control_close_to_reference_warning"
        elif any(status == "structured_separates_from_control_candidate" for status in statuses):
            row["structured_vs_control_separation_status"] = (
                "metric_specific_separation_candidate"
            )
        elif all(status == "near_equal_no_separation" for status in statuses):
            row["structured_vs_control_separation_status"] = "no_clear_separation"
        else:
            row["structured_vs_control_separation_status"] = "separation_reported"

    pairwise_file = OUTPUT_DIR / "component_compatibility_pairwise.csv"
    family_summary_file = OUTPUT_DIR / "component_compatibility_family_summary.csv"
    contrast_file = OUTPUT_DIR / "component_compatibility_control_contrast.csv"
    summary_file = OUTPUT_DIR / "summary.json"
    readout_file = OUTPUT_DIR / "readout.md"
    config_file = OUTPUT_DIR / "config_resolved.json"

    write_csv(pairwise_file, PAIRWISE_FIELDS, pairwise_rows)
    write_csv(family_summary_file, FAMILY_SUMMARY_FIELDS, family_summary_rows)
    write_csv(contrast_file, CONTRAST_FIELDS, contrast_rows)

    best_candidate_metrics = sorted(
        {
            row["metric_name"]
            for row in contrast_rows
            if row["separation_status"] == "structured_separates_from_control_candidate"
        }
    )
    warning_metrics = sorted(
        {
            f"{row['metric_name']}:{row['control_family']}"
            for row in contrast_rows
            if row["separation_status"]
            in {
                "control_exceeds_or_matches_structured_warning",
                "near_equal_no_separation",
            }
        }
    )

    output_files = [
        str(pairwise_file),
        str(family_summary_file),
        str(contrast_file),
        str(summary_file),
        str(readout_file),
        str(config_file),
    ]
    summary = {
        "block": "QSB-ST-COMP01B",
        "status": "COMP01B_component_resolved_compatibility_inspection_implemented_and_run_checked",
        "input_basis": {
            "config": str(CONFIG_PATH),
            "comp01_runner_reused_without_modification": str(COMP01_RUNNER_PATH),
            "synthetic_kernel_source": "LIC01 build_synthetic_kernel(seed) via COMP01 basis",
            "psi_representation": "complex row/column local relational fingerprint",
            "component_split": "real part as cosine-like proxy; imaginary part as sine-like proxy",
        },
        "output_dir": str(OUTPUT_DIR),
        "pair_count": len(node_ids) * len(node_ids),
        "family_count": len(FAMILIES),
        "metric_count": len(METRICS),
        "pairwise_row_count": len(pairwise_rows),
        "family_summary_row_count": len(family_summary_rows),
        "control_contrast_row_count": len(contrast_rows),
        "families": FAMILIES,
        "metrics": METRICS,
        "component_split_mode": COMPONENT_SPLIT_MODE,
        "best_candidate_metrics": best_candidate_metrics,
        "warning_metrics": warning_metrics,
        "specificity_established": False,
        "tau_model_constructed": False,
        "D_AB_attached": False,
        "S_rel2_constructed": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }

    summary_file.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    readout_file.write_text(build_readout(summary, contrast_rows, output_files), encoding="utf-8")
    config_resolved = {
        "source_config": str(CONFIG_PATH),
        "output_dir": str(OUTPUT_DIR),
        "eta": eta,
        "random_seed": seed,
        "families": FAMILIES,
        "metrics": METRICS,
        "component_split_mode": COMPONENT_SPLIT_MODE,
        "pair_count": len(node_ids) * len(node_ids),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    config_file.write_text(json.dumps(config_resolved, indent=2, sort_keys=True), encoding="utf-8")

    print("QSB-ST-COMP01-B component-resolved compatibility inspection completed.")
    print(f"output_dir: {OUTPUT_DIR}")
    print(f"component_split_mode: {COMPONENT_SPLIT_MODE}")
    print(f"pairwise_row_count: {len(pairwise_rows)}")
    print(f"family_summary_row_count: {len(family_summary_rows)}")
    print(f"control_contrast_row_count: {len(contrast_rows)}")
    print(f"best_candidate_metrics: {best_candidate_metrics}")
    print(f"warning_metrics: {warning_metrics}")
    print("specificity_established: False")
    print("claim_boundary: synthetic diagnostic work only; no physical time or Bridge validation.")


if __name__ == "__main__":
    main()
