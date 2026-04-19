#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import replace
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any

import numpy as np

from dpb.k0_n0_reference import BaseConfig, NullSpec, run_k0, run_n0


PAIR_KEYS = [
    "d03_minus_d01",
    "d03_minus_d12",
    "d02_minus_d13",
]


def parse_float_list(text: str) -> list[float]:
    return [float(x.strip()) for x in text.split(",") if x.strip()]


def parse_int_list(text: str) -> list[int]:
    return [int(x.strip()) for x in text.split(",") if x.strip()]


def get_field(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def safe_float(x: Any) -> float | None:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def total_pairs(n_nodes: int) -> int:
    return n_nodes * (n_nodes - 1) // 2


def theta_interval_index(theta: float, theta_crit: list[float]) -> int:
    for i, tc in enumerate(theta_crit):
        if theta < tc:
            return i
    return len(theta_crit)


def summarize_result(result: Any, n_nodes: int) -> dict[str, Any]:
    cc = get_field(result, "connected_components", []) or []
    connected_pairs = get_field(result, "connected_pairs", []) or []
    disconnected_pairs = get_field(result, "disconnected_pairs", []) or []
    std_pairs = get_field(result, "standard_pairs", {}) or {}
    theta_crit = [float(x) for x in (get_field(result, "theta_crit", []) or [])]
    graph_diameter = safe_float(get_field(result, "graph_diameter", None))

    largest_cc = max((len(c) for c in cc), default=0)
    n_edges = len(connected_pairs)
    n_cc = len(cc)
    pair_total = total_pairs(n_nodes)
    connected_pair_fraction = n_edges / pair_total if pair_total else None
    defined_pair_count = sum(std_pairs.get(k) is not None for k in PAIR_KEYS)

    return {
        "theta": safe_float(get_field(get_field(result, "config"), "theta", None))
        if not isinstance(get_field(result, "config"), dict)
        else safe_float(get_field(result, "config", {}).get("theta")),
        "theta_crit": theta_crit,
        "theta_interval_index": None,
        "n_edges": n_edges,
        "n_components": n_cc,
        "largest_component_size": largest_cc,
        "connected_pair_fraction": connected_pair_fraction,
        "graph_diameter": graph_diameter,
        "connected_pairs": connected_pairs,
        "disconnected_pairs": disconnected_pairs,
        "fully_connected": n_cc == 1,
        "fragmented": n_cc > 1,
        "defined_pair_count": defined_pair_count,
        "standard_pairs": {k: safe_float(std_pairs.get(k)) for k in PAIR_KEYS},
    }


def stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "n": 0,
            "mean": None,
            "median": None,
            "pstdev": None,
            "min": None,
            "max": None,
        }
    return {
        "n": len(values),
        "mean": mean(values),
        "median": median(values),
        "pstdev": pstdev(values) if len(values) > 1 else 0.0,
        "min": min(values),
        "max": max(values),
    }


def signed_stats(values: list[float]) -> dict[str, Any]:
    base = stats(values)
    if not values:
        base.update({"neg_frac": None, "zero_frac": None, "pos_frac": None})
        return base
    n = len(values)
    neg = sum(v < 0 for v in values)
    zero = sum(v == 0 for v in values)
    pos = sum(v > 0 for v in values)
    base.update({
        "neg_frac": neg / n,
        "zero_frac": zero / n,
        "pos_frac": pos / n,
    })
    return base


def empirical_percentile(ref: float | None, values: list[float]) -> float | None:
    if ref is None or not values:
        return None
    le = sum(v <= ref for v in values)
    return le / len(values)


def topology_label(summary: dict[str, Any]) -> str:
    return f"cc{summary['n_components']}_e{summary['n_edges']}_diam{summary['graph_diameter']}"


def make_interval_representatives(theta_crit: list[float], theta_max: float) -> list[dict[str, Any]]:
    theta_crit = sorted(float(x) for x in theta_crit)
    intervals: list[dict[str, Any]] = []

    if not theta_crit:
        return [{
            "theta_min": 0.0,
            "theta_max": theta_max,
            "theta_rep": theta_max / 2.0,
            "window_width_decades": None,
        }]

    # first interval: (0, tc1)
    first = theta_crit[0]
    intervals.append({
        "theta_min": 0.0,
        "theta_max": first,
        "theta_rep": first / 2.0,
        "window_width_decades": None,
    })

    # middle intervals
    for a, b in zip(theta_crit[:-1], theta_crit[1:]):
        rep = math.sqrt(a * b)
        intervals.append({
            "theta_min": a,
            "theta_max": b,
            "theta_rep": rep,
            "window_width_decades": math.log10(b / a) if a > 0 else None,
        })

    # last interval: (last, theta_max)
    last = theta_crit[-1]
    if theta_max > last:
        rep = math.sqrt(last * theta_max)
        intervals.append({
            "theta_min": last,
            "theta_max": theta_max,
            "theta_rep": rep,
            "window_width_decades": math.log10(theta_max / last) if last > 0 else None,
        })

    return intervals


def build_config_from_args(args: argparse.Namespace, theta: float) -> BaseConfig:
    return BaseConfig(
        mode=args.mode,
        p=np.array(parse_float_list(args.p), dtype=float),
        m=args.m,
        t=args.t,
        L=args.L,
        theta=theta,
        hbar=args.hbar,
        c=args.c,
        ell0=args.ell0,
        s_min=args.s_min,
        epsilon=args.epsilon,
        F=args.F,
        weight="uniform",
    )


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(
        description="T.1.1*: K0 exact theta map + N0 theta ensemble aggregation"
    )
    ap.add_argument("--mode", choices=["free", "force"], required=True)
    ap.add_argument("--p", required=True, help='Comma-separated list, e.g. "-1.5,-0.5,0.5,1.5"')
    ap.add_argument("--m", type=float, required=True)
    ap.add_argument("--t", type=float, required=True)
    ap.add_argument("--L", type=float, required=True)
    ap.add_argument("--F", type=float, default=0.0)
    ap.add_argument("--hbar", type=float, default=1.0)
    ap.add_argument("--c", type=float, default=1.0)
    ap.add_argument("--ell0", type=float, default=1.0)
    ap.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    ap.add_argument("--theta-min", type=float, default=1e-3)
    ap.add_argument("--theta-max", type=float, default=1e-1)
    ap.add_argument("--theta-points", type=int, default=100)
    ap.add_argument("--theta-ref", type=float, default=0.03)
    ap.add_argument("--seeds", required=True, help='Comma-separated list, e.g. "1,2,3,4,5"')
    ap.add_argument("--outdir", default="results/t1")
    args = ap.parse_args()

    p_list = parse_float_list(args.p)
    seeds = parse_int_list(args.seeds)
    n_nodes = len(p_list)

    outdir = Path(args.outdir)
    k0_dir = outdir / "k0_reference_theta_map"
    n0_dir = outdir / "n0_theta_ensemble"
    cmp_dir = outdir / "k0_vs_n0_theta"

    theta_grid = np.geomspace(args.theta_min, args.theta_max, args.theta_points).astype(float).tolist()

    # -------------------------
    # K.0 exact reference map
    # -------------------------
    k0_ref_cfg = build_config_from_args(args, args.theta_ref)
    k0_ref_result = run_k0(k0_ref_cfg)
    k0_theta_crit = sorted(float(x) for x in get_field(k0_ref_result, "theta_crit", []))
    k0_intervals = make_interval_representatives(k0_theta_crit, args.theta_max)

    k0_interval_rows = []
    for interval in k0_intervals:
        cfg = build_config_from_args(args, interval["theta_rep"])
        res = run_k0(cfg)
        s = summarize_result(res, n_nodes)
        s["theta_interval_index"] = theta_interval_index(interval["theta_rep"], s["theta_crit"])
        row = {
            **interval,
            **s,
            "topology_label": topology_label(s),
        }
        k0_interval_rows.append(row)

    # K.0 on common theta grid
    k0_grid_rows = []
    for theta in theta_grid:
        cfg = build_config_from_args(args, theta)
        res = run_k0(cfg)
        s = summarize_result(res, n_nodes)
        s["theta_interval_index"] = theta_interval_index(theta, s["theta_crit"])
        s["theta"] = theta
        s["topology_label"] = topology_label(s)
        k0_grid_rows.append(s)

    # -------------------------
    # N.0 runs on common theta grid
    # -------------------------
    n0_runs = []
    aggregate_rows = []

    for seed in seeds:
        seed_rows = []
        null_spec = NullSpec(null_mode="random_phase", seed=seed)
        for theta in theta_grid:
            cfg = build_config_from_args(args, theta)
            res = run_n0(cfg, null_spec)
            s = summarize_result(res, n_nodes)
            s["theta_interval_index"] = theta_interval_index(theta, s["theta_crit"])
            s["theta"] = theta
            s["seed"] = seed
            s["topology_label"] = topology_label(s)
            seed_rows.append(s)
        n0_runs.append({"seed": seed, "rows": seed_rows})

    # aggregate by theta index
    for idx, theta in enumerate(theta_grid):
        rows = [run["rows"][idx] for run in n0_runs]

        fully_connected_frac = sum(r["fully_connected"] for r in rows) / len(rows)
        fragmented_frac = sum(r["fragmented"] for r in rows) / len(rows)

        n_edges_vals = [float(r["n_edges"]) for r in rows]
        n_comp_vals = [float(r["n_components"]) for r in rows]
        lcc_vals = [float(r["largest_component_size"]) for r in rows]
        cpf_vals = [float(r["connected_pair_fraction"]) for r in rows]
        diam_vals = [float(r["graph_diameter"]) for r in rows if r["graph_diameter"] is not None]
        interval_idx_vals = [float(r["theta_interval_index"]) for r in rows]

        pair_stats = {}
        for key in PAIR_KEYS:
            defined_vals = [r["standard_pairs"][key] for r in rows if r["standard_pairs"][key] is not None]
            pair_stats[key] = {
                "defined_fraction": len(defined_vals) / len(rows),
                "stats_defined_only": signed_stats([float(v) for v in defined_vals]),
            }

        aggregate_rows.append({
            "theta": theta,
            "fully_connected_fraction": fully_connected_frac,
            "fragmented_fraction": fragmented_frac,
            "n_edges": stats(n_edges_vals),
            "n_components": stats(n_comp_vals),
            "largest_component_size": stats(lcc_vals),
            "connected_pair_fraction": stats(cpf_vals),
            "graph_diameter": stats(diam_vals),
            "theta_interval_index": stats(interval_idx_vals),
            "pair_stats": pair_stats,
        })

    # -------------------------
    # K.0 vs N.0 comparison on common grid
    # -------------------------
    comparison_rows = []
    csv_rows = []

    for k0_row, agg_row in zip(k0_grid_rows, aggregate_rows):
        cmp_entry = {
            "theta": k0_row["theta"],
            "k0": {
                "n_edges": k0_row["n_edges"],
                "n_components": k0_row["n_components"],
                "graph_diameter": k0_row["graph_diameter"],
                "largest_component_size": k0_row["largest_component_size"],
                "connected_pair_fraction": k0_row["connected_pair_fraction"],
                "defined_pair_count": k0_row["defined_pair_count"],
                "standard_pairs": k0_row["standard_pairs"],
                "theta_interval_index": k0_row["theta_interval_index"],
                "topology_label": k0_row["topology_label"],
            },
            "n0": {
                "fully_connected_fraction": agg_row["fully_connected_fraction"],
                "fragmented_fraction": agg_row["fragmented_fraction"],
                "mean_n_edges": agg_row["n_edges"]["mean"],
                "mean_n_components": agg_row["n_components"]["mean"],
                "mean_graph_diameter": agg_row["graph_diameter"]["mean"],
                "mean_largest_component_size": agg_row["largest_component_size"]["mean"],
                "mean_connected_pair_fraction": agg_row["connected_pair_fraction"]["mean"],
                "theta_interval_index_mean": agg_row["theta_interval_index"]["mean"],
                "pair_stats": agg_row["pair_stats"],
            },
            "k0_pair_percentiles": {},
        }

        for key in PAIR_KEYS:
            ref_val = k0_row["standard_pairs"][key]
            n0_vals = [
                run["rows"][k0_grid_rows.index(k0_row)]["standard_pairs"][key]
                for run in n0_runs
                if run["rows"][k0_grid_rows.index(k0_row)]["standard_pairs"][key] is not None
            ]
            n0_vals = [float(v) for v in n0_vals]
            cmp_entry["k0_pair_percentiles"][key] = empirical_percentile(ref_val, n0_vals)

        comparison_rows.append(cmp_entry)

        csv_rows.append({
            "theta": k0_row["theta"],
            "k0_n_edges": k0_row["n_edges"],
            "k0_n_components": k0_row["n_components"],
            "k0_graph_diameter": k0_row["graph_diameter"],
            "n0_fully_connected_fraction": agg_row["fully_connected_fraction"],
            "n0_fragmented_fraction": agg_row["fragmented_fraction"],
            "n0_mean_n_edges": agg_row["n_edges"]["mean"],
            "n0_mean_n_components": agg_row["n_components"]["mean"],
            "n0_mean_graph_diameter": agg_row["graph_diameter"]["mean"],
            "n0_d03_minus_d01_defined_fraction": agg_row["pair_stats"]["d03_minus_d01"]["defined_fraction"],
            "n0_d03_minus_d12_defined_fraction": agg_row["pair_stats"]["d03_minus_d12"]["defined_fraction"],
            "n0_d02_minus_d13_defined_fraction": agg_row["pair_stats"]["d02_minus_d13"]["defined_fraction"],
            "k0_d03_minus_d01_percentile": cmp_entry["k0_pair_percentiles"]["d03_minus_d01"],
            "k0_d03_minus_d12_percentile": cmp_entry["k0_pair_percentiles"]["d03_minus_d12"],
            "k0_d02_minus_d13_percentile": cmp_entry["k0_pair_percentiles"]["d02_minus_d13"],
        })

    # -------------------------
    # Write outputs
    # -------------------------
    write_json(k0_dir / "k0_theta_intervals.json", k0_interval_rows)
    write_json(k0_dir / "k0_theta_grid.json", k0_grid_rows)
    np.savez(
        k0_dir / "k0_theta_curves.npz",
        theta_grid=np.array(theta_grid, dtype=float),
        n_edges=np.array([r["n_edges"] for r in k0_grid_rows], dtype=float),
        n_components=np.array([r["n_components"] for r in k0_grid_rows], dtype=float),
        graph_diameter=np.array([r["graph_diameter"] for r in k0_grid_rows], dtype=float),
        connected_pair_fraction=np.array([r["connected_pair_fraction"] for r in k0_grid_rows], dtype=float),
    )
    write_text(
        k0_dir / "k0_theta_summary.txt",
        "\n".join([
            "=== K.0 exact theta intervals ===",
            f"mode: {args.mode}",
            f"theta_ref: {args.theta_ref}",
            f"theta_crit: {k0_theta_crit}",
            f"n_intervals: {len(k0_interval_rows)}",
        ]),
    )

    write_json(n0_dir / "n0_theta_runs.json", n0_runs)
    write_json(n0_dir / "n0_theta_aggregate.json", aggregate_rows)
    np.savez(
        n0_dir / "n0_theta_curves.npz",
        theta_grid=np.array(theta_grid, dtype=float),
        fully_connected_fraction=np.array([r["fully_connected_fraction"] for r in aggregate_rows], dtype=float),
        fragmented_fraction=np.array([r["fragmented_fraction"] for r in aggregate_rows], dtype=float),
        mean_n_edges=np.array([r["n_edges"]["mean"] for r in aggregate_rows], dtype=float),
        mean_graph_diameter=np.array([r["graph_diameter"]["mean"] for r in aggregate_rows], dtype=float),
    )
    write_text(
        n0_dir / "n0_theta_summary.txt",
        "\n".join([
            "=== N.0 theta ensemble aggregation ===",
            f"n_seeds: {len(seeds)}",
            f"theta_grid: [{args.theta_min}, {args.theta_max}] with {args.theta_points} points",
            f"seeds: {seeds}",
        ]),
    )

    write_json(cmp_dir / "k0_vs_n0_theta_report.json", comparison_rows)

    csv_path = cmp_dir / "k0_vs_n0_theta_tables.csv"
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        writer.writeheader()
        writer.writerows(csv_rows)

    write_text(
        cmp_dir / "k0_vs_n0_theta_summary.txt",
        "\n".join([
            "=== K.0 vs N.0 theta comparison ===",
            f"mode: {args.mode}",
            f"theta_ref: {args.theta_ref}",
            f"n_seeds: {len(seeds)}",
            f"output_root: {outdir}",
        ]),
    )

    print("T.1.1* completed.")
    print(f"K.0 intervals: {k0_dir / 'k0_theta_intervals.json'}")
    print(f"N.0 aggregate: {n0_dir / 'n0_theta_aggregate.json'}")
    print(f"K.0 vs N.0 report: {cmp_dir / 'k0_vs_n0_theta_report.json'}")


if __name__ == "__main__":
    main()
