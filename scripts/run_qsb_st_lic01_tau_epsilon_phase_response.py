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
    return float(np.trapezoid(np.asarray(values, dtype=float), np.asarray(eps, dtype=float)))


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
        "claim_boundary": "Synthetic phase-response diagnostic only. tau_rel_candidate is not physical time; no Lorentzian metric, spacetime validation, or physical validation is claimed.",
        "warnings": [
            "Synthetic reference kernel only; no real-data or physical validation.",
            "rho_tau is a diagnostic response-strength score.",
            "tau_rel_candidate is a normalized monotone transform of response strength.",
            "S_rel2_candidate is intentionally not constructed in this minimal run.",
            "Some planned controls are listed in config but not implemented in this minimal runner.",
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
