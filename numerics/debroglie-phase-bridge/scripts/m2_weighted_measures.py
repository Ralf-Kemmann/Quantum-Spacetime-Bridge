#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
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
    Ci_vals = []

    for i in range(n):
        neighbors = [j for j in range(n) if j != i and Wn[i, j] > 0.0]
        k_i = len(neighbors)
        if k_i < 2:
            Ci_vals.append(0.0)
            continue

        tri_sum = 0.0
        for a in range(k_i):
            j = neighbors[a]
            for b in range(a + 1, k_i):
                k = neighbors[b]
                if Wn[j, k] <= 0.0:
                    continue
                tri_sum += (Wn[i, j] * Wn[i, k] * Wn[j, k]) ** (1.0 / 3.0)

        Ci = (2.0 * tri_sum) / (k_i * (k_i - 1))
        Ci_vals.append(float(Ci))

    return float(np.mean(Ci_vals))


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


def summarize_case(case_name: str, kernel_mode: str, base_result, measures: dict[str, float | None]) -> dict[str, Any]:
    return {
        "case": case_name,
        "run_kind": base_result.run_kind,
        "kernel_mode": kernel_mode,
        "theta": float(base_result.config.theta),
        "natural_connectivity": measures["natural_connectivity"],
        "weighted_clustering": measures["weighted_clustering"],
        "global_efficiency": measures["global_efficiency"],
    }


def write_single_result(outdir: Path, case_name: str, kernel_mode: str, result_payload: dict[str, Any]) -> None:
    target = outdir / case_name / kernel_mode
    target.mkdir(parents=True, exist_ok=True)
    with (target / "weighted_measures.json").open("w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2)
    lines = [
        f"case: {case_name}",
        f"run_kind: {result_payload['run_kind']}",
        f"kernel_mode: {kernel_mode}",
        f"theta: {result_payload['theta']}",
        f"natural_connectivity: {result_payload['natural_connectivity']}",
        f"weighted_clustering: {result_payload['weighted_clustering']}",
        f"global_efficiency: {result_payload['global_efficiency']}",
    ]
    (target / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="M.2.2 weighted-measures helper on abs / positive / negative kernels.")
    ap.add_argument("--mode", choices=["free", "force"], default="free")
    ap.add_argument("--p", default="-1.5,-0.5,0.5,1.5")
    ap.add_argument("--m", type=float, default=1.0)
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--L", type=float, default=10.0)
    ap.add_argument("--theta", type=float, default=0.03)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--alpha-low", type=float, default=0.5)
    ap.add_argument("--alpha-high", type=float, default=2.0)
    ap.add_argument("--hbar", type=float, default=1.0)
    ap.add_argument("--c", type=float, default=1.0)
    ap.add_argument("--ell0", type=float, default=1.0)
    ap.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    ap.add_argument("--F", type=float, default=0.0)
    ap.add_argument("--length-epsilon", type=float, default=1e-12)
    ap.add_argument("--outdir", default="results/m2")
    args = ap.parse_args()

    cfg = build_config(args)
    cfg.validate()

    spec = WeightedMeasureSpec("onnela", True, args.length_epsilon)
    spec.validate()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    base_cases = {
        "k0": run_k0(cfg),
        "n0": run_n0(cfg, NullSpec(null_mode="random_phase", seed=args.seed)),
        "n1a_alpha_0p5": run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", args.alpha_low)),
        "n1a_alpha_2p0": run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", args.alpha_high)),
    }

    rows = []

    for case_name, base_result in base_cases.items():
        for kernel_mode in ["abs", "positive", "negative"]:
            result = base_result if kernel_mode == "abs" else run_with_kernel_map(base_result, KernelMapSpec(kernel_mode))
            measures = compute_weighted_measures(result.G, spec)
            payload = summarize_case(case_name, kernel_mode, result, measures)
            payload["weighted_measure_spec"] = jsonable(asdict(spec))
            payload["null_spec"] = None if result.null_spec is None else jsonable(asdict(result.null_spec))
            payload["wrong_dispersion_spec"] = None if result.wrong_dispersion_spec is None else jsonable(asdict(result.wrong_dispersion_spec))
            rows.append(payload)
            write_single_result(outdir, case_name, kernel_mode, payload)

    comparisons = outdir / "comparisons"
    comparisons.mkdir(parents=True, exist_ok=True)

    csv_path = comparisons / "m2_weighted_measures.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["case", "run_kind", "kernel_mode", "theta", "natural_connectivity", "weighted_clustering", "global_efficiency"])
        writer.writeheader()
        for r in rows:
            writer.writerow({k: r[k] for k in ["case", "run_kind", "kernel_mode", "theta", "natural_connectivity", "weighted_clustering", "global_efficiency"]})

    json_path = comparisons / "m2_weighted_measures.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    summary_lines = [
        "=== M.2.2 weighted measures ===",
        f"p: {cfg.p.tolist()}",
        f"mode: {cfg.mode}",
        f"m={cfg.m}, t={cfg.t}, L={cfg.L}, theta={cfg.theta}, F={cfg.F}",
        f"seed: {args.seed}",
        f"alpha_low: {args.alpha_low}",
        f"alpha_high: {args.alpha_high}",
        "",
        "Measures:",
        "- natural_connectivity",
        "- weighted_clustering (Onnela)",
        "- global_efficiency",
        "",
        f"Wrote CSV: {csv_path}",
        f"Wrote JSON: {json_path}",
    ]
    (comparisons / "m2_summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Wrote weighted-measures results to: {outdir}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Summary: {comparisons / 'm2_summary.txt'}")


if __name__ == "__main__":
    main()
