#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path

import numpy as np

from dpb.k0_n0_reference import BaseConfig, WrongDispersionSpec, KernelMapSpec, run_k0, run_n1a, run_with_kernel_map, write_result_artifacts


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


def summarize_row(case_name: str, kernel_mode: str, result) -> dict:
    return {
        "case": case_name,
        "kernel_mode": kernel_mode,
        "theta": result.config.theta,
        "n_edges": len(result.connected_pairs),
        "n_components": len(result.connected_components),
        "graph_diameter": result.graph_diameter,
        "defined_pair_fraction": sum(v is not None for v in result.standard_pairs.values()) / 3.0,
        "topology_label": f"cc{len(result.connected_components)}_e{len(result.connected_pairs)}_diam{result.graph_diameter}",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Small A.1 helper: compare abs/positive/negative kernel maps.")
    ap.add_argument("--mode", choices=["free", "force"], default="free")
    ap.add_argument("--p", default="-1.5,-0.5,0.5,1.5")
    ap.add_argument("--m", type=float, default=1.0)
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--L", type=float, default=10.0)
    ap.add_argument("--theta", type=float, default=0.03)
    ap.add_argument("--alpha", type=float, default=2.0)
    ap.add_argument("--hbar", type=float, default=1.0)
    ap.add_argument("--c", type=float, default=1.0)
    ap.add_argument("--ell0", type=float, default=1.0)
    ap.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    ap.add_argument("--F", type=float, default=0.0)
    ap.add_argument("--outdir", default="results/a1_probe")
    args = ap.parse_args()

    cfg = build_config(args)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    base_cases = {
        "k0": run_k0(cfg),
        "n1a_alpha": run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", args.alpha)),
    }

    rows = []
    for case_name, base in base_cases.items():
        for mode in ["abs", "positive", "negative"]:
            res = run_with_kernel_map(base, KernelMapSpec(mode))
            write_result_artifacts(res, outdir / case_name / mode)
            rows.append(summarize_row(case_name, mode, res))

    with (outdir / "a1_kernel_comparison.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["case", "kernel_mode", "theta", "n_edges", "n_components", "graph_diameter", "defined_pair_fraction", "topology_label"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote A.1 probe results to: {outdir}")


if __name__ == "__main__":
    main()
