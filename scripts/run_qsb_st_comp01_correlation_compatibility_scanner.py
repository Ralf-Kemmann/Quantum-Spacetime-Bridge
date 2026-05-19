#!/usr/bin/env python3
"""
QSB-ST-COMP01 minimal correlation compatibility scanner.

Synthetic diagnostic scanner only. Psi is a diagnostic pattern object here,
not automatically a physical wavefunction. Tau is not physical time, proper
time, or a universal clock. COMP01 does not attach D(A,B), does not construct
S_rel2, and does not establish diagnostic specificity yet.
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
LIC01_RUNNER_PATH = Path("scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py")
OUTPUT_DIR = Path("runs/QSB-ST-COMP01/correlation_compatibility_scanner_open")

STRUCTURED_FAMILY = "structured_local_phase_response"
CONTROL_FAMILIES = [
    "global_phase_shift",
    "random_phase",
    "amplitude_preserved_phase_randomized",
    "label_shuffle",
]
FAMILIES = [STRUCTURED_FAMILY] + CONTROL_FAMILIES
METRICS = [
    "normalized_overlap",
    "magnitude_support_overlap",
    "phase_alignment",
    "relative_phase_pattern_similarity",
    "local_pattern_correlation",
]
PAIRWISE_FIELDS = [
    "family",
    "source_id",
    "target_id",
    "normalized_overlap",
    "magnitude_support_overlap",
    "phase_alignment",
    "relative_phase_pattern_similarity",
    "local_pattern_correlation",
    "compatibility_score_candidate",
    "control_status",
    "warning",
]
FAMILY_SUMMARY_FIELDS = [
    "family",
    "pair_count",
    "normalized_overlap_mean",
    "magnitude_support_overlap_mean",
    "phase_alignment_mean",
    "relative_phase_pattern_similarity_mean",
    "local_pattern_correlation_mean",
    "compatibility_score_candidate_mean",
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
    "Synthetic diagnostic compatibility scanner only; psi is a diagnostic "
    "pattern object, not physical wavefunction; psi-overlap is a compatibility "
    "observable, not automatically a quantum measurement probability; tau is "
    "not physical time, not proper time, and not a universal clock; COMP01 "
    "does not attach D(A,B), does not construct S_rel2, does not derive a "
    "Lorentzian metric, does not validate a physical Bridge, and does not "
    "establish diagnostic specificity yet."
)


def load_lic01_module() -> Any:
    spec = importlib.util.spec_from_file_location("lic01_runner", LIC01_RUNNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load LIC01 runner spec: {LIC01_RUNNER_PATH}")
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


def build_family_kernels(
    base_kernel: np.ndarray,
    seed: int,
) -> Dict[str, np.ndarray]:
    rng = np.random.default_rng(seed + 101)
    n = base_kernel.shape[0]
    random_phase = rng.uniform(-math.pi, math.pi, size=(n, n))
    randomized_phase = rng.uniform(-math.pi, math.pi, size=(n, n))
    permutation = np.array([2, 5, 1, 7, 0, 6, 3, 4], dtype=int)

    kernels = {
        STRUCTURED_FAMILY: base_kernel.copy(),
        "global_phase_shift": base_kernel * np.exp(1j * 0.731),
        "random_phase": base_kernel * np.exp(1j * random_phase),
        "amplitude_preserved_phase_randomized": np.abs(base_kernel)
        * np.exp(1j * randomized_phase),
        "label_shuffle": base_kernel[np.ix_(permutation, permutation)],
    }
    return kernels


def psi_fingerprint(kernel: np.ndarray, idx: int) -> np.ndarray:
    """Return a local complex row/column diagnostic fingerprint for node idx."""
    return np.concatenate([kernel[idx, :], kernel[:, idx]])


def normalized_overlap(psi_i: np.ndarray, psi_j: np.ndarray, eta: float) -> Tuple[float, str]:
    norm_i = float(np.linalg.norm(psi_i))
    norm_j = float(np.linalg.norm(psi_j))
    warning = ""
    if norm_i <= eta or norm_j <= eta:
        warning = "zero_norm_warning"
    value = abs(np.vdot(psi_i, psi_j)) / (norm_i * norm_j + eta)
    return float(value), warning


def magnitude_support_overlap(
    psi_i: np.ndarray, psi_j: np.ndarray, eta: float
) -> Tuple[float, str]:
    mag_i = np.abs(psi_i)
    mag_j = np.abs(psi_j)
    norm_i = float(np.linalg.norm(mag_i))
    norm_j = float(np.linalg.norm(mag_j))
    warning = ""
    if norm_i <= eta or norm_j <= eta:
        warning = "zero_magnitude_warning"
    value = float(np.dot(mag_i, mag_j) / (norm_i * norm_j + eta))
    return value, warning


def phase_alignment(psi_i: np.ndarray, psi_j: np.ndarray, eta: float) -> Tuple[float, str]:
    mask = (np.abs(psi_i) > eta) & (np.abs(psi_j) > eta)
    if not bool(np.any(mask)):
        return 0.0, "empty_shared_support_warning"
    phase_delta = np.angle(psi_i[mask]) - np.angle(psi_j[mask])
    return float(np.mean(np.cos(phase_delta))), ""


def centered_phase_pattern(psi: np.ndarray, eta: float) -> Tuple[np.ndarray, str]:
    mask = np.abs(psi) > eta
    if not bool(np.any(mask)):
        return np.zeros_like(psi, dtype=float), "empty_support_warning"
    reference_idx = int(np.flatnonzero(mask)[0])
    centered = psi * np.exp(-1j * np.angle(psi[reference_idx]))
    return np.angle(centered), ""


def relative_phase_pattern_similarity(
    psi_i: np.ndarray, psi_j: np.ndarray, eta: float
) -> Tuple[float, str]:
    phase_i, warning_i = centered_phase_pattern(psi_i, eta)
    phase_j, warning_j = centered_phase_pattern(psi_j, eta)
    mask = (np.abs(psi_i) > eta) & (np.abs(psi_j) > eta)
    if not bool(np.any(mask)):
        return 0.0, "empty_shared_support_warning"
    phase_delta = phase_i[mask] - phase_j[mask]
    warning = ";".join(part for part in [warning_i, warning_j] if part)
    return float(np.mean(np.cos(phase_delta))), warning


def local_pattern_correlation(psi_i: np.ndarray, psi_j: np.ndarray, eta: float) -> Tuple[float, str]:
    vec_i = np.concatenate([psi_i.real, psi_i.imag])
    vec_j = np.concatenate([psi_j.real, psi_j.imag])
    std_i = float(np.std(vec_i))
    std_j = float(np.std(vec_j))
    if std_i <= eta or std_j <= eta:
        return 0.0, "metric_degenerate_warning"
    corr = float(np.corrcoef(vec_i, vec_j)[0, 1])
    if not math.isfinite(corr):
        return 0.0, "metric_degenerate_warning"
    return corr, ""


def compute_metrics(psi_i: np.ndarray, psi_j: np.ndarray, eta: float) -> Tuple[Dict[str, float], str]:
    metric_values: Dict[str, float] = {}
    warnings: List[str] = []
    functions = {
        "normalized_overlap": normalized_overlap,
        "magnitude_support_overlap": magnitude_support_overlap,
        "phase_alignment": phase_alignment,
        "relative_phase_pattern_similarity": relative_phase_pattern_similarity,
        "local_pattern_correlation": local_pattern_correlation,
    }
    for name, func in functions.items():
        value, warning = func(psi_i, psi_j, eta)
        metric_values[name] = value
        if warning:
            warnings.append(f"{name}:{warning}")
    warnings.append("not_defined_candidate")
    return metric_values, ";".join(warnings)


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
    return f"""# QSB-ST-COMP01 Correlation Compatibility Scanner Readout

## Purpose

The COMP01 scanner tests diagnostic psi(i)-psi(j) compatibility candidates
against synthetic controls. It does not establish physical wavefunctions,
physical time, Lorentz structure, D(A,B), S_rel2, or Bridge validation.

## Input basis

- Config: `{CONFIG_PATH}`
- LIC01 runner functions reused without modifying LIC01 outputs: `{LIC01_RUNNER_PATH}`
- Family count: {summary['family_count']}
- Pair count per family: {summary['pair_count']}
- Total pairwise rows: {summary['pairwise_row_count']}

## Candidate metrics

```text
{chr(10).join(summary['metrics'])}
```

`compatibility_score_candidate` is not defined in this minimal scanner.

## Output files

```text
{chr(10).join(output_files)}
```

## First-pass contrast summary

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

- No tau model is constructed.
- No combined compatibility score is defined.
- Controls are first-pass synthetic controls only.
- Candidate movement is not a specificity claim.

## Claim Boundary

Psi is a diagnostic pattern object here, not automatically a physical
wavefunction.

Psi-overlap is a compatibility observable, not automatically a quantum
measurement probability.

Tau is not physical time.

Tau is not proper time.

Tau is not a universal clock.

COMP01 does not attach D(A,B).

COMP01 does not construct S_rel2.

COMP01 does not derive a Lorentzian metric.

COMP01 does not validate a physical Bridge.

COMP01 does not establish diagnostic specificity yet.

This is synthetic diagnostic work only.
"""


def main() -> None:
    lic01 = load_lic01_module()
    cfg = lic01.load_config(CONFIG_PATH)
    eta = float(get_config_value(cfg, ["response", "eta"], 1.0e-12))
    seed = int(get_config_value(cfg, ["reproducibility", "random_seed"], 17052026))

    node_ids, base_kernel = lic01.build_synthetic_kernel(seed)
    family_kernels = build_family_kernels(base_kernel, seed)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    pairwise_rows: List[Dict[str, Any]] = []
    for family in FAMILIES:
        kernel = family_kernels[family]
        control_status = "structured_reference" if family == STRUCTURED_FAMILY else "control"
        for source_idx, source_id in enumerate(node_ids):
            psi_i = psi_fingerprint(kernel, source_idx)
            for target_idx, target_id in enumerate(node_ids):
                psi_j = psi_fingerprint(kernel, target_idx)
                metrics, warning = compute_metrics(psi_i, psi_j, eta)
                row: Dict[str, Any] = {
                    "family": family,
                    "source_id": source_id,
                    "target_id": target_id,
                    "compatibility_score_candidate": "not_defined",
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
        family_summary_rows.append(
            {
                "family": family,
                "pair_count": len(rows_by_family[family]),
                "normalized_overlap_mean": format_float(means["normalized_overlap"]),
                "magnitude_support_overlap_mean": format_float(
                    means["magnitude_support_overlap"]
                ),
                "phase_alignment_mean": format_float(means["phase_alignment"]),
                "relative_phase_pattern_similarity_mean": format_float(
                    means["relative_phase_pattern_similarity"]
                ),
                "local_pattern_correlation_mean": format_float(
                    means["local_pattern_correlation"]
                ),
                "compatibility_score_candidate_mean": "not_defined",
                "structured_vs_control_separation_status": (
                    "structured_reference_baseline"
                    if family == STRUCTURED_FAMILY
                    else "pending_contrast"
                ),
                "warning": "not_defined_candidate",
            }
        )

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

    pairwise_file = OUTPUT_DIR / "compatibility_scanner_pairwise.csv"
    family_summary_file = OUTPUT_DIR / "compatibility_family_summary.csv"
    contrast_file = OUTPUT_DIR / "compatibility_control_contrast.csv"
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
        "block": "QSB-ST-COMP01",
        "status": "COMP01_minimal_scanner_implemented_and_run_checked",
        "input_basis": {
            "config": str(CONFIG_PATH),
            "lic01_runner_reused_without_modification": str(LIC01_RUNNER_PATH),
            "psi_representation": "complex row/column local relational fingerprint",
            "synthetic_kernel_source": "LIC01 build_synthetic_kernel(seed)",
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
        "pair_count": len(node_ids) * len(node_ids),
        "claim_boundary": CLAIM_BOUNDARY,
    }
    config_file.write_text(json.dumps(config_resolved, indent=2, sort_keys=True), encoding="utf-8")

    print("QSB-ST-COMP01 correlation compatibility scanner completed.")
    print(f"output_dir: {OUTPUT_DIR}")
    print(f"pairwise_row_count: {len(pairwise_rows)}")
    print(f"family_summary_row_count: {len(family_summary_rows)}")
    print(f"control_contrast_row_count: {len(contrast_rows)}")
    print(f"best_candidate_metrics: {best_candidate_metrics}")
    print(f"warning_metrics: {warning_metrics}")
    print("specificity_established: False")
    print("claim_boundary: synthetic diagnostic work only; no physical time or Bridge validation.")


if __name__ == "__main__":
    main()
