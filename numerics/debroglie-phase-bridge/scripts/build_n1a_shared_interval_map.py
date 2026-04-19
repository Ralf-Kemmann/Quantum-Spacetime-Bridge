#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from dpb.k0_n0_reference import BaseConfig, WrongDispersionSpec, run_k0, run_n1a


PAIR_KEYS = ["d03_minus_d01", "d03_minus_d12", "d02_minus_d13"]


def parse_float_list(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def safe_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def topology_label(n_edges: int, n_components: int, graph_diameter: float | None) -> str:
    return f"cc{n_components}_e{n_edges}_diam{graph_diameter}"


def connected_components_list(result: Any) -> list[list[int]]:
    cc = getattr(result, "connected_components", None)
    if cc is None and isinstance(result, dict):
        cc = result.get("connected_components", [])
    elif cc is None:
        cc = []
    return [list(map(int, c)) for c in cc]


def summarize_result(result: Any) -> dict[str, Any]:
    cc = connected_components_list(result)
    connected_pairs = getattr(result, "connected_pairs", None)
    if connected_pairs is None and isinstance(result, dict):
        connected_pairs = result.get("connected_pairs", [])
    elif connected_pairs is None:
        connected_pairs = []
    disconnected_pairs = getattr(result, "disconnected_pairs", None)
    if disconnected_pairs is None and isinstance(result, dict):
        disconnected_pairs = result.get("disconnected_pairs", [])
    elif disconnected_pairs is None:
        disconnected_pairs = []
    graph_diameter = safe_float(getattr(result, "graph_diameter", None))
    if graph_diameter is None and isinstance(result, dict):
        graph_diameter = safe_float(result.get("graph_diameter"))
    std_pairs = getattr(result, "standard_pairs", None)
    if std_pairs is None and isinstance(result, dict):
        std_pairs = result.get("standard_pairs", {})
    elif std_pairs is None:
        std_pairs = {}
    theta_crit = getattr(result, "theta_crit", None)
    if theta_crit is None and isinstance(result, dict):
        theta_crit = result.get("theta_crit", [])
    elif theta_crit is None:
        theta_crit = []
    cfg = getattr(result, "config", None)
    theta_val = safe_float(getattr(cfg, "theta", None)) if cfg is not None else None

    largest_component = max((len(c) for c in cc), default=0)
    defined_pair_count = sum(std_pairs.get(k) is not None for k in PAIR_KEYS)

    return {
        "theta": theta_val,
        "theta_crit": [float(x) for x in theta_crit],
        "n_edges": int(len(connected_pairs)),
        "n_components": int(len(cc)),
        "largest_component_size": int(largest_component),
        "graph_diameter": graph_diameter,
        "connected_pairs": [list(map(int, p)) for p in connected_pairs],
        "disconnected_pairs": [list(map(int, p)) for p in disconnected_pairs],
        "defined_pair_count": int(defined_pair_count),
        "defined_pair_fraction": defined_pair_count / 3.0,
        "standard_pairs": {k: safe_float(std_pairs.get(k)) for k in PAIR_KEYS},
    }


def make_intervals(theta_crit: list[float], theta_upper: float) -> list[dict[str, Any]]:
    crit = sorted(float(x) for x in theta_crit)
    intervals: list[dict[str, Any]] = []

    if not crit:
        rep = theta_upper / 2.0
        return [{
            "theta_min": 0.0,
            "theta_max": theta_upper,
            "theta_rep": rep,
            "window_width_decades": None,
        }]

    first = crit[0]
    intervals.append({
        "theta_min": 0.0,
        "theta_max": first,
        "theta_rep": first / 2.0,
        "window_width_decades": None,
    })

    for a, b in zip(crit[:-1], crit[1:]):
        rep = math.sqrt(a * b)
        intervals.append({
            "theta_min": a,
            "theta_max": b,
            "theta_rep": rep,
            "window_width_decades": math.log10(b / a) if a > 0 else None,
        })

    if theta_upper > crit[-1]:
        a = crit[-1]
        b = theta_upper
        rep = math.sqrt(a * b)
        intervals.append({
            "theta_min": a,
            "theta_max": b,
            "theta_rep": rep,
            "window_width_decades": math.log10(b / a) if a > 0 else None,
        })

    return intervals


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


def run_case(case_name: str, args: argparse.Namespace, theta: float):
    cfg = build_config(args, theta)
    if case_name == "k0":
        return run_k0(cfg)
    if case_name == "a05":
        return run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", args.alpha_low))
    if case_name == "a20":
        return run_n1a(cfg, WrongDispersionSpec("scaled_quadratic", args.alpha_high))
    raise ValueError(f"Unknown case: {case_name}")


def exact_interval_map(case_name: str, args: argparse.Namespace, theta_ref: float, theta_upper: float) -> dict[str, Any]:
    ref_result = run_case(case_name, args, theta_ref)
    ref_summary = summarize_result(ref_result)
    theta_crit = ref_summary["theta_crit"]
    intervals = make_intervals(theta_crit, theta_upper)

    rows = []
    for interval in intervals:
        rep = interval["theta_rep"]
        res = run_case(case_name, args, rep)
        s = summarize_result(res)
        rows.append({
            **interval,
            **s,
            "topology_label": topology_label(s["n_edges"], s["n_components"], s["graph_diameter"]),
        })

    return {
        "case": case_name,
        "theta_ref": theta_ref,
        "theta_upper": theta_upper,
        "theta_crit": theta_crit,
        "intervals": rows,
    }


def sampled_case_rows(case_name: str, args: argparse.Namespace, thetas: list[float]) -> list[dict[str, Any]]:
    rows = []
    for theta in thetas:
        res = run_case(case_name, args, theta)
        s = summarize_result(res)
        rows.append({
            "case": case_name,
            "theta": theta,
            **s,
            "topology_label": topology_label(s["n_edges"], s["n_components"], s["graph_diameter"]),
        })
    return rows


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Build shared interval map and comparison table for K.0 and wrong-dispersion controls."
    )
    ap.add_argument("--mode", choices=["free"], default="free")
    ap.add_argument("--p", default="-1.5,-0.5,0.5,1.5")
    ap.add_argument("--m", type=float, default=1.0)
    ap.add_argument("--t", type=float, default=1.0)
    ap.add_argument("--L", type=float, default=10.0)
    ap.add_argument("--theta-ref", type=float, default=0.03)
    ap.add_argument("--theta-upper", type=float, default=0.06)
    ap.add_argument("--thetas", default="0.02,0.026,0.03,0.035,0.04,0.045")
    ap.add_argument("--alpha-low", type=float, default=0.5)
    ap.add_argument("--alpha-high", type=float, default=2.0)
    ap.add_argument("--hbar", type=float, default=1.0)
    ap.add_argument("--c", type=float, default=1.0)
    ap.add_argument("--ell0", type=float, default=1.0)
    ap.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    ap.add_argument("--F", type=float, default=0.0)
    ap.add_argument("--outdir", default="results/n1a_scan/interval_map")
    args = ap.parse_args()

    thetas = parse_float_list(args.thetas)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    k0_map = exact_interval_map("k0", args, args.theta_ref, args.theta_upper)
    a05_map = exact_interval_map("a05", args, args.theta_ref, args.theta_upper)
    a20_map = exact_interval_map("a20", args, args.theta_ref, args.theta_upper)

    write_json(outdir / "k0_theta_intervals_t1.json", k0_map)
    write_json(outdir / "n1a_alpha_0p5_theta_intervals_t1.json", a05_map)
    write_json(outdir / "n1a_alpha_2p0_theta_intervals_t1.json", a20_map)

    k0_rows = sampled_case_rows("k0", args, thetas)
    a05_rows = sampled_case_rows("a05", args, thetas)
    a20_rows = sampled_case_rows("a20", args, thetas)

    comparison_rows = []
    for i, theta in enumerate(thetas):
        comparison_rows.append({
            "theta": theta,
            "k0": k0_rows[i],
            "n1a_alpha_0p5": a05_rows[i],
            "n1a_alpha_2p0": a20_rows[i],
        })

    write_json(outdir / "theta_comparison.json", comparison_rows)

    csv_path = outdir / "theta_comparison.csv"
    fieldnames = [
        "theta",
        "k0_n_edges", "k0_n_components", "k0_graph_diameter", "k0_defined_pair_fraction", "k0_topology",
        "a05_n_edges", "a05_n_components", "a05_graph_diameter", "a05_defined_pair_fraction", "a05_topology",
        "a20_n_edges", "a20_n_components", "a20_graph_diameter", "a20_defined_pair_fraction", "a20_topology",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in comparison_rows:
            k0 = row["k0"]
            a05 = row["n1a_alpha_0p5"]
            a20 = row["n1a_alpha_2p0"]
            writer.writerow({
                "theta": row["theta"],
                "k0_n_edges": k0["n_edges"],
                "k0_n_components": k0["n_components"],
                "k0_graph_diameter": k0["graph_diameter"],
                "k0_defined_pair_fraction": k0["defined_pair_fraction"],
                "k0_topology": k0["topology_label"],
                "a05_n_edges": a05["n_edges"],
                "a05_n_components": a05["n_components"],
                "a05_graph_diameter": a05["graph_diameter"],
                "a05_defined_pair_fraction": a05["defined_pair_fraction"],
                "a05_topology": a05["topology_label"],
                "a20_n_edges": a20["n_edges"],
                "a20_n_components": a20["n_components"],
                "a20_graph_diameter": a20["graph_diameter"],
                "a20_defined_pair_fraction": a20["defined_pair_fraction"],
                "a20_topology": a20["topology_label"],
            })

    summary_lines = [
        "=== N.1a.4.1 Shared interval map and comparison table ===",
        f"mode: {args.mode}",
        f"p: {parse_float_list(args.p)}",
        f"m={args.m}, t={args.t}, L={args.L}, F={args.F}",
        f"theta_ref: {args.theta_ref}",
        f"theta_upper: {args.theta_upper}",
        f"sampled_thetas: {thetas}",
        f"alpha_low: {args.alpha_low}",
        f"alpha_high: {args.alpha_high}",
        "",
        "Critical values:",
        f"K.0: {k0_map['theta_crit']}",
        f"N.1a alpha=0.5: {a05_map['theta_crit']}",
        f"N.1a alpha=2.0: {a20_map['theta_crit']}",
        "",
        "Working reading:",
        "alpha=2.0 should shift early transitions left.",
        "alpha=0.5 should shift early transitions right.",
        "K.0 should lie between both wrong-dispersion controls.",
    ]
    write_text(outdir / "summary.txt", "\n".join(summary_lines))

    print("N.1a.4.1 completed.")
    print(f"Wrote: {outdir / 'k0_theta_intervals_t1.json'}")
    print(f"Wrote: {outdir / 'n1a_alpha_0p5_theta_intervals_t1.json'}")
    print(f"Wrote: {outdir / 'n1a_alpha_2p0_theta_intervals_t1.json'}")
    print(f"Wrote: {outdir / 'theta_comparison.csv'}")
    print(f"Wrote: {outdir / 'summary.txt'}")


if __name__ == "__main__":
    main()
