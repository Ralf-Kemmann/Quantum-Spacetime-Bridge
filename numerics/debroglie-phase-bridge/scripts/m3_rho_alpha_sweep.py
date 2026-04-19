#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from dpb.k0_n0_reference import (
    BaseConfig,
    WrongDispersionSpec,
    KernelMapSpec,
    run_k0,
    run_n1a,
    run_with_kernel_map,
)


def parse_float_list(text: str) -> np.ndarray:
    return np.array([float(x.strip()) for x in text.split(",") if x.strip()], dtype=float)


def build_alpha_grid(alpha_min: float, alpha_max: float, alpha_step: float) -> list[float]:
    n = int(round((alpha_max - alpha_min) / alpha_step))
    vals = [alpha_min + i * alpha_step for i in range(n + 1)]
    return [round(v, 10) for v in vals]


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


def prepare_weighted_adjacency(G: np.ndarray) -> np.ndarray:
    W = np.asarray(G, dtype=float).copy()
    np.fill_diagonal(W, 0.0)
    W = 0.5 * (W + W.T)
    W[W < 0.0] = 0.0
    return W


def largest_eigenvalue(W: np.ndarray) -> float | None:
    if W.size == 0:
        return None
    vals = np.linalg.eigvalsh(W)
    return float(vals[-1])


def normalized_laplacian_lambda2(W: np.ndarray) -> float | None:
    n = W.shape[0]
    if n < 2:
        return None
    degrees = W.sum(axis=1)
    inv_sqrt = np.zeros_like(degrees, dtype=float)
    mask = degrees > 0.0
    inv_sqrt[mask] = 1.0 / np.sqrt(degrees[mask])
    S = np.diag(inv_sqrt)
    L = np.eye(n) - S @ W @ S
    vals = np.linalg.eigvalsh(L)
    if len(vals) < 2:
        return None
    return float(vals[1])


def weighted_clustering_onnela(W: np.ndarray) -> float | None:
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


def compute_weighted_spectrum(result, eps: float) -> dict[str, float | None]:
    result_abs = result
    result_pos = run_with_kernel_map(result, KernelMapSpec("positive"))
    result_neg = run_with_kernel_map(result, KernelMapSpec("negative"))

    W_abs = prepare_weighted_adjacency(result_abs.G)
    W_pos = prepare_weighted_adjacency(result_pos.G)
    W_neg = prepare_weighted_adjacency(result_neg.G)

    lmax_abs = largest_eigenvalue(W_abs)
    lmax_pos = largest_eigenvalue(W_pos)
    lmax_neg = largest_eigenvalue(W_neg)

    rho_pos = None if lmax_abs is None else float(lmax_pos / max(lmax_abs, eps))
    rho_neg = None if lmax_abs is None else float(lmax_neg / max(lmax_abs, eps))
    chi = None if lmax_abs is None else float((lmax_neg - lmax_pos) / max(lmax_abs, eps))

    return {
        "lmax_abs": lmax_abs,
        "lmax_pos": lmax_pos,
        "lmax_neg": lmax_neg,
        "rho_pos": rho_pos,
        "rho_neg": rho_neg,
        "chi": chi,
        "lambda2_abs": normalized_laplacian_lambda2(W_abs),
        "lambda2_pos": normalized_laplacian_lambda2(W_pos),
        "lambda2_neg": normalized_laplacian_lambda2(W_neg),
        "weighted_clustering_abs": weighted_clustering_onnela(W_abs),
        "weighted_clustering_pos": weighted_clustering_onnela(W_pos),
        "weighted_clustering_neg": weighted_clustering_onnela(W_neg),
    }


def run_alpha_case(cfg: BaseConfig, alpha: float):
    if abs(alpha - 1.0) < 1e-12:
        return run_k0(cfg)
    return run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", alpha))


def main() -> None:
    ap = argparse.ArgumentParser(description="M.3 — alpha sweep for rho, chi, lambda2 and weighted clustering.")
    ap.add_argument("--mode", choices=["free", "force"], default="free")
    ap.add_argument("--p", default="-1.5,-0.5,0.5,1.5")
    ap.add_argument("--m", type=float, default=1.0)
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--L", type=float, default=10.0)
    ap.add_argument("--theta", type=float, default=0.03)
    ap.add_argument("--alpha-min", type=float, default=0.3)
    ap.add_argument("--alpha-max", type=float, default=3.0)
    ap.add_argument("--alpha-step", type=float, default=0.1)
    ap.add_argument("--hbar", type=float, default=1.0)
    ap.add_argument("--c", type=float, default=1.0)
    ap.add_argument("--ell0", type=float, default=1.0)
    ap.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    ap.add_argument("--F", type=float, default=0.0)
    ap.add_argument("--spectral-epsilon", type=float, default=1e-12)
    ap.add_argument("--outdir", default="results/m3_alpha_sweep")
    args = ap.parse_args()

    cfg = build_config(args)
    cfg.validate()

    alphas = build_alpha_grid(args.alpha_min, args.alpha_max, args.alpha_step)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []
    for alpha in alphas:
        result = run_alpha_case(cfg, alpha)
        payload = {
            "alpha": float(alpha),
            "run_kind": result.run_kind,
            "p": cfg.p.tolist(),
            "t": cfg.t,
            "L": cfg.L,
            **compute_weighted_spectrum(result, args.spectral_epsilon),
        }
        rows.append(payload)

    json_path = outdir / "m3_alpha_sweep.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    csv_path = outdir / "m3_alpha_sweep.csv"
    fieldnames = [
        "alpha",
        "run_kind",
        "lmax_abs",
        "lmax_pos",
        "lmax_neg",
        "rho_pos",
        "rho_neg",
        "chi",
        "lambda2_abs",
        "lambda2_pos",
        "lambda2_neg",
        "weighted_clustering_abs",
        "weighted_clustering_pos",
        "weighted_clustering_neg",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

    def extremum_of(key: str, mode: str):
        vals = [(r["alpha"], r[key]) for r in rows if r[key] is not None]
        if not vals:
            return None
        if mode == "max":
            return max(vals, key=lambda x: x[1])
        return min(vals, key=lambda x: x[1])

    summary_lines = [
        "=== M.3 alpha sweep ===",
        f"p: {cfg.p.tolist()}",
        f"mode: {cfg.mode}",
        f"m={cfg.m}, t={cfg.t}, L={cfg.L}, theta={cfg.theta}, F={cfg.F}",
        f"alpha_range: [{args.alpha_min}, {args.alpha_max}] step {args.alpha_step}",
        "",
        "Primary quantities:",
        "- rho_pos = lmax_pos / lmax_abs",
        "- rho_neg = lmax_neg / lmax_abs",
        "- chi = (lmax_neg - lmax_pos) / lmax_abs",
        "",
        "Secondary quantities:",
        "- lambda2_abs / lambda2_pos / lambda2_neg",
        "- weighted_clustering_abs / pos / neg",
        "",
        f"chi_max: {extremum_of('chi', 'max')}",
        f"chi_min: {extremum_of('chi', 'min')}",
        f"weighted_clustering_abs_max: {extremum_of('weighted_clustering_abs', 'max')}",
        f"lambda2_abs_min: {extremum_of('lambda2_abs', 'min')}",
        f"lambda2_abs_max: {extremum_of('lambda2_abs', 'max')}",
        "",
        f"Wrote CSV: {csv_path}",
        f"Wrote JSON: {json_path}",
    ]
    (outdir / "summary.txt").write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    print(f"Wrote M.3 sweep to: {outdir}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Summary: {outdir / 'summary.txt'}")


if __name__ == "__main__":
    main()
