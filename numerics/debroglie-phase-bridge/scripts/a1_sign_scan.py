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
    write_result_artifacts,
)


def parse_float_list(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def build_config(args: argparse.Namespace, theta: float) -> BaseConfig:
    return BaseConfig(
        mode=args.mode,
        p=np.array(parse_float_list(args.p), dtype=float),
        m=args.m,
        t=args.t,
        L=args.L,
        theta=float(theta),
        hbar=args.hbar,
        c=args.c,
        ell0=args.ell0,
        s_min=args.s_min,
        epsilon=args.epsilon,
        F=args.F,
        weight="uniform",
    )


def topology_label(result) -> str:
    return f"cc{len(result.connected_components)}_e{len(result.connected_pairs)}_diam{result.graph_diameter}"


def summarize_result(case_name: str, theta: float, kernel_mode: str, result) -> dict:
    return {
        "case": case_name,
        "theta": theta,
        "kernel_mode": kernel_mode,
        "n_edges": len(result.connected_pairs),
        "n_components": len(result.connected_components),
        "graph_diameter": result.graph_diameter,
        "defined_pair_fraction": sum(v is not None for v in result.standard_pairs.values()) / 3.0,
        "topology_label": topology_label(result),
        "theta_crit": [float(x) for x in result.theta_crit],
        "connected_components": result.connected_components,
        "standard_pairs": result.standard_pairs,
    }


def run_base_case(case_name: str, cfg: BaseConfig, alpha_low: float, alpha_high: float):
    if case_name == "k0":
        return run_k0(cfg)
    if case_name == "n1a_alpha_0p5":
        return run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", alpha_low))
    if case_name == "n1a_alpha_2p0":
        return run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", alpha_high))
    raise ValueError(f"Unknown case: {case_name}")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="A.1.4.1: scan abs/positive/negative kernel maps over multiple theta values."
    )
    ap.add_argument("--mode", choices=["free", "force"], default="free")
    ap.add_argument("--p", default="-1.5,-0.5,0.5,1.5")
    ap.add_argument("--m", type=float, default=1.0)
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--L", type=float, default=10.0)
    ap.add_argument("--thetas", default="0.026,0.03,0.035,0.04")
    ap.add_argument("--alpha-low", type=float, default=0.5)
    ap.add_argument("--alpha-high", type=float, default=2.0)
    ap.add_argument("--hbar", type=float, default=1.0)
    ap.add_argument("--c", type=float, default=1.0)
    ap.add_argument("--ell0", type=float, default=1.0)
    ap.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    ap.add_argument("--F", type=float, default=0.0)
    ap.add_argument("--outdir", default="results/a1_sign_scan")
    args = ap.parse_args()

    thetas = parse_float_list(args.thetas)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cases = ["k0", "n1a_alpha_0p5", "n1a_alpha_2p0"]
    kernel_modes = ["abs", "positive", "negative"]

    rows = []
    nested_results = []

    for theta in thetas:
        cfg = build_config(args, theta)
        theta_block = {"theta": theta, "cases": {}}

        for case_name in cases:
            base_result = run_base_case(case_name, cfg, args.alpha_low, args.alpha_high)
            case_block = {}

            for kernel_mode in kernel_modes:
                if kernel_mode == "abs":
                    result = base_result
                else:
                    result = run_with_kernel_map(base_result, KernelMapSpec(kernel_mode))

                case_outdir = outdir / case_name / f"theta_{theta}" / kernel_mode
                write_result_artifacts(result, case_outdir)

                row = summarize_result(case_name, theta, kernel_mode, result)
                rows.append(row)
                case_block[kernel_mode] = row

            theta_block["cases"][case_name] = case_block

        nested_results.append(theta_block)

    # CSV
    csv_path = outdir / "a1_sign_scan.csv"
    fieldnames = [
        "case",
        "theta",
        "kernel_mode",
        "n_edges",
        "n_components",
        "graph_diameter",
        "defined_pair_fraction",
        "topology_label",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row[k] for k in fieldnames})

    # JSON
    json_path = outdir / "a1_sign_scan.json"
    with json_path.open("w", encoding="utf-8") as f:
        json.dump(nested_results, f, indent=2)

    # Summary text
    summary_lines = [
        "=== A.1.4.1 sign-preserving scan ===",
        f"mode: {args.mode}",
        f"p: {parse_float_list(args.p)}",
        f"m={args.m}, t={args.t}, L={args.L}, F={args.F}",
        f"thetas: {thetas}",
        f"alpha_low: {args.alpha_low}",
        f"alpha_high: {args.alpha_high}",
        "",
        "Cases:",
        "- k0",
        f"- n1a_alpha_0p5 (alpha={args.alpha_low})",
        f"- n1a_alpha_2p0 (alpha={args.alpha_high})",
        "",
        "Kernel modes:",
        "- abs",
        "- positive",
        "- negative",
        "",
        f"Wrote CSV: {csv_path}",
        f"Wrote JSON: {json_path}",
    ]
    (outdir / "summary.txt").write_text("\n".join(summary_lines), encoding="utf-8")

    print(f"Wrote scan to: {outdir}")
    print(f"CSV: {csv_path}")
    print(f"JSON: {json_path}")
    print(f"Summary: {outdir / 'summary.txt'}")


if __name__ == "__main__":
    main()
