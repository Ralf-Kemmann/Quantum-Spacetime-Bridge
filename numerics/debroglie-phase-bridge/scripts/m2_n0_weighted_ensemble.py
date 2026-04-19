#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import statistics
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

import numpy as np

from dpb.k0_n0_reference import (
    BaseConfig,
    NullSpec,
    WrongDispersionSpec,
    KernelMapSpec,
    run_k0,
    run_n0,
    run_n1a,
    run_with_kernel_map,
)


@dataclass
class WeightedMeasureSpec:
    clustering_mode: str = "onnela"
    use_zero_diagonal: bool = True
    length_epsilon: float = 1e-12

    def validate(self) -> None:
        if self.clustering_mode != "onnela":
            raise ValueError("Only clustering_mode='onnela' is supported.")
        if self.length_epsilon <= 0 or not np.isfinite(self.length_epsilon):
            raise ValueError("length_epsilon must be positive and finite.")


def parse_float_list(text: str) -> np.ndarray:
    return np.array([float(x.strip()) for x in text.split(",") if x.strip()], dtype=float)


def parse_int_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def jsonable(v: Any) -> Any:
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, (np.floating, np.integer)):
        return v.item()
    if isinstance(v, dict):
        return {k: jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    return v


def build_config(args: argparse.Namespace) -> BaseConfig:
    return BaseConfig(
        mode=args.mode,
        p=parse_float_list(args.p),
        m=args.m,
        t=args.t,
        L=args.L,
        theta=args.theta,
        hbar=args.hbar,
        c=args.c,
        ell0=args.ell0,
        s_min=args.s_min,
        epsilon=args.epsilon,
        F=args.F,
        weight="uniform",
    )


def prepare_weighted_adjacency(G: np.ndarray, spec: WeightedMeasureSpec) -> np.ndarray:
    spec.validate()
    W = np.asarray(G, dtype=float).copy()
    if spec.use_zero_diagonal:
        np.fill_diagonal(W, 0.0)
    W = 0.5 * (W + W.T)
    W[W < 0.0] = 0.0
    return W


def compute_natural_connectivity(W: np.ndarray) -> float | None:
    if W.size == 0:
        return None
    eigvals = np.linalg.eigvalsh(W)
    return float(np.log(np.mean(np.exp(eigvals))))


def compute_weighted_clustering_onnela(W: np.ndarray) -> float | None:
    n = W.shape[0]
    if n == 0:
        return None
    offdiag = W.copy()
    np.fill_diagonal(offdiag, 0.0)
    wmax = float(np.max(offdiag))
    if wmax <= 0.0:
        return 0.0

    Wn = offdiag / wmax
    ci_vals: list[float] = []

    for i in range(n):
        neighbors = [j for j in range(n) if j != i and Wn[i, j] > 0.0]
        k_i = len(neighbors)
        if k_i < 2:
            ci_vals.append(0.0)
            continue

        tri_sum = 0.0
        for a in range(k_i):
            j = neighbors[a]
            for b in range(a + 1, k_i):
                k = neighbors[b]
                if Wn[j, k] <= 0.0:
                    continue
                tri_sum += (Wn[i, j] * Wn[i, k] * Wn[j, k]) ** (1.0 / 3.0)

        ci_vals.append(float((2.0 * tri_sum) / (k_i * (k_i - 1))))

    return float(np.mean(ci_vals))


def compute_global_efficiency(W: np.ndarray, spec: WeightedMeasureSpec) -> float | None:
    n = W.shape[0]
    if n == 0:
        return None

    D = np.full((n, n), np.inf, dtype=float)
    np.fill_diagonal(D, 0.0)

    for i in range(n):
        for j in range(n):
            if i != j and W[i, j] > 0.0:
                D[i, j] = 1.0 / max(float(W[i, j]), spec.length_epsilon)

    for k in range(n):
        for i in range(n):
            dik = D[i, k]
            if not np.isfinite(dik):
                continue
            for j in range(n):
                alt = dik + D[k, j]
                if alt < D[i, j]:
                    D[i, j] = alt

    total = 0.0
    count = 0
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            count += 1
            if np.isfinite(D[i, j]) and D[i, j] > 0.0:
                total += 1.0 / D[i, j]

    if count == 0:
        return None
    return float(total / count)


def compute_weighted_measures(G: np.ndarray, spec: WeightedMeasureSpec) -> dict[str, float | None]:
    W = prepare_weighted_adjacency(G, spec)
    return {
        "natural_connectivity": compute_natural_connectivity(W),
        "weighted_clustering": compute_weighted_clustering_onnela(W),
        "global_efficiency": compute_global_efficiency(W, spec),
    }


def apply_kernel_mode(base_result, kernel_mode: str):
    if kernel_mode == "abs":
        return base_result
    return run_with_kernel_map(base_result, KernelMapSpec(kernel_mode=kernel_mode))


def summarize_result(case_name: str, kernel_mode: str, result, measures: dict[str, float | None], seed: int | None = None) -> dict[str, Any]:
    payload = {
        "case": case_name,
        "run_kind": result.run_kind,
        "kernel_mode": kernel_mode,
        "theta": float(result.config.theta),
        "natural_connectivity": measures["natural_connectivity"],
        "weighted_clustering": measures["weighted_clustering"],
        "global_efficiency": measures["global_efficiency"],
    }
    if seed is not None:
        payload["seed"] = int(seed)
    return payload


def write_single_result(target: Path, payload: dict[str, Any]) -> None:
    target.mkdir(parents=True, exist_ok=True)
    with (target / "weighted_measures.json").open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    lines = [
        f"case: {payload['case']}",
        f"run_kind: {payload['run_kind']}",
        f"kernel_mode: {payload['kernel_mode']}",
        f"theta: {payload['theta']}",
    ]
    if "seed" in payload:
        lines.append(f"seed: {payload['seed']}")
    lines.extend([
        f"natural_connectivity: {payload['natural_connectivity']}",
        f"weighted_clustering: {payload['weighted_clustering']}",
        f"global_efficiency: {payload['global_efficiency']}",
    ])
    (target / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def aggregate_values(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"n": 0, "mean": None, "median": None, "pstdev": None, "min": None, "max": None}
    return {
        "n": len(values),
        "mean": float(statistics.fmean(values)),
        "median": float(statistics.median(values)),
        "pstdev": float(statistics.pstdev(values)) if len(values) > 1 else 0.0,
        "min": float(min(values)),
        "max": float(max(values)),
    }


def empirical_percentile(values: list[float], ref: float | None) -> float | None:
    if ref is None or not values:
        return None
    count = sum(v <= ref for v in values)
    return float(count / len(values))


def main() -> None:
    ap = argparse.ArgumentParser(description="M.2.4.1 weighted-measures ensemble for N.0 plus comparison to K.0 and N.1a.")
    ap.add_argument("--mode", choices=["free", "force"], default="free")
    ap.add_argument("--p", default="-1.5,-0.5,0.5,1.5")
    ap.add_argument("--m", type=float, default=1.0)
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--L", type=float, default=10.0)
    ap.add_argument("--theta", type=float, default=0.03)
    ap.add_argument("--seeds", default="11,22,33,44,55,66,77,88,99,111")
    ap.add_argument("--alpha-low", type=float, default=0.5)
    ap.add_argument("--alpha-high", type=float, default=2.0)
    ap.add_argument("--hbar", type=float, default=1.0)
    ap.add_argument("--c", type=float, default=1.0)
    ap.add_argument("--ell0", type=float, default=1.0)
    ap.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    ap.add_argument("--F", type=float, default=0.0)
    ap.add_argument("--length-epsilon", type=float, default=1e-12)
    ap.add_argument("--outdir", default="results/m2_ensemble")
    args = ap.parse_args()

    cfg = build_config(args)
    cfg.validate()
    seeds = parse_int_list(args.seeds)

    spec = WeightedMeasureSpec("onnela", True, args.length_epsilon)
    spec.validate()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    base_refs = {
        "k0": run_k0(cfg),
        "n1a_alpha_0p5": run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", args.alpha_low)),
        "n1a_alpha_2p0": run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", args.alpha_high)),
    }

    ref_rows: list[dict[str, Any]] = []
    for case_name, base_result in base_refs.items():
        for kernel_mode in ["abs", "positive", "negative"]:
            result = apply_kernel_mode(base_result, kernel_mode)
            measures = compute_weighted_measures(result.G, spec)
            payload = summarize_result(case_name, kernel_mode, result, measures)
            payload["weighted_measure_spec"] = jsonable(asdict(spec))
            payload["wrong_dispersion_spec"] = None if result.wrong_dispersion_spec is None else jsonable(asdict(result.wrong_dispersion_spec))
            ref_rows.append(payload)
            write_single_result(outdir / case_name / kernel_mode, payload)

    n0_rows: list[dict[str, Any]] = []
    for seed in seeds:
        base_n0 = run_n0(cfg, NullSpec(null_mode="random_phase", seed=seed))
        for kernel_mode in ["abs", "positive", "negative"]:
            result = apply_kernel_mode(base_n0, kernel_mode)
            measures = compute_weighted_measures(result.G, spec)
            payload = summarize_result("n0", kernel_mode, result, measures, seed=seed)
            payload["weighted_measure_spec"] = jsonable(asdict(spec))
            payload["null_spec"] = jsonable(asdict(result.null_spec)) if result.null_spec is not None else None
            n0_rows.append(payload)
            write_single_result(outdir / "n0" / f"seed_{seed}" / kernel_mode, payload)

    aggregate_rows: list[dict[str, Any]] = []
    for kernel_mode in ["abs", "positive", "negative"]:
        kernel_rows = [r for r in n0_rows if r["kernel_mode"] == kernel_mode]
        for measure in ["natural_connectivity", "weighted_clustering", "global_efficiency"]:
            vals = [float(r[measure]) for r in kernel_rows if r[measure] is not None]
            agg = aggregate_values(vals)

            k0_ref = next((r[measure] for r in ref_rows if r["case"] == "k0" and r["kernel_mode"] == kernel_mode), None)
            a05_ref = next((r[measure] for r in ref_rows if r["case"] == "n1a_alpha_0p5" and r["kernel_mode"] == kernel_mode), None)
            a20_ref = next((r[measure] for r in ref_rows if r["case"] == "n1a_alpha_2p0" and r["kernel_mode"] == kernel_mode), None)

            aggregate_rows.append({
                "kernel_mode": kernel_mode,
                "measure": measure,
                **agg,
                "k0_reference": k0_ref,
                "k0_empirical_percentile": empirical_percentile(vals, None if k0_ref is None else float(k0_ref)),
                "n1a_alpha_0p5_reference": a05_ref,
                "n1a_alpha_0p5_empirical_percentile": empirical_percentile(vals, None if a05_ref is None else float(a05_ref)),
                "n1a_alpha_2p0_reference": a20_ref,
                "n1a_alpha_2p0_empirical_percentile": empirical_percentile(vals, None if a20_ref is None else float(a20_ref)),
            })

    comparisons = outdir / "comparisons"
    comparisons.mkdir(parents=True, exist_ok=True)

    with (comparisons / "m2_n0_ensemble_refs.json").open("w", encoding="utf-8") as f:
        json.dump(ref_rows, f, indent=2)
    with (comparisons / "m2_n0_ensemble_seed_rows.json").open("w", encoding="utf-8") as f:
        json.dump(n0_rows, f, indent=2)
    with (comparisons / "m2_n0_ensemble_aggregate.json").open("w", encoding="utf-8") as f:
        json.dump(aggregate_rows, f, indent=2)

    with (comparisons / "m2_n0_ensemble_seed_rows.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case", "seed", "kernel_mode", "theta", "natural_connectivity", "weighted_clustering", "global_efficiency"])
        writer.writeheader()
        for r in n0_rows:
            writer.writerow({k: r[k] for k in ["case", "seed", "kernel_mode", "theta", "natural_connectivity", "weighted_clustering", "global_efficiency"]})

    with (comparisons / "m2_n0_ensemble_aggregate.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "kernel_mode",
                "measure",
                "n",
                "mean",
                "median",
                "pstdev",
                "min",
                "max",
                "k0_reference",
                "k0_empirical_percentile",
                "n1a_alpha_0p5_reference",
                "n1a_alpha_0p5_empirical_percentile",
                "n1a_alpha_2p0_reference",
                "n1a_alpha_2p0_empirical_percentile",
            ],
        )
        writer.writeheader()
        writer.writerows(aggregate_rows)

    summary_lines = [
        "=== M.2.4.1 weighted-measures ensemble for N.0 ===",
        f"p: {cfg.p.tolist()}",
        f"mode: {cfg.mode}",
        f"m={cfg.m}, t={cfg.t}, L={cfg.L}, theta={cfg.theta}, F={cfg.F}",
        f"seeds: {seeds}",
        f"alpha_low: {args.alpha_low}",
        f"alpha_high: {args.alpha_high}",
        "",
        "Measures:",
        "- natural_connectivity",
        "- weighted_clustering (Onnela)",
        "- global_efficiency",
        "",
        "Fixed references:",
        "- k0",
        f"- n1a_alpha_0p5 (alpha={args.alpha_low})",
        f"- n1a_alpha_2p0 (alpha={args.alpha_high})",
        "",
        f"Wrote aggregate CSV: {comparisons / 'm2_n0_ensemble_aggregate.csv'}",
        f"Wrote aggregate JSON: {comparisons / 'm2_n0_ensemble_aggregate.json'}",
    ]
    (comparisons / "m2_n0_ensemble_summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Wrote M.2.4.1 ensemble results to: {outdir}")
    print(f"Aggregate CSV: {comparisons / 'm2_n0_ensemble_aggregate.csv'}")
    print(f"Aggregate JSON: {comparisons / 'm2_n0_ensemble_aggregate.json'}")
    print(f"Summary: {comparisons / 'm2_n0_ensemble_summary.txt'}")


if __name__ == "__main__":
    main()
