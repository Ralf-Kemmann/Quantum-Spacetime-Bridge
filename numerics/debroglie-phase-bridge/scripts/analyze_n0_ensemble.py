#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any

PAIR_KEYS = [
    "d03_minus_d01",
    "d03_minus_d12",
    "d02_minus_d13",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "n_defined": 0,
            "mean": None,
            "median": None,
            "pstdev": None,
            "min": None,
            "max": None,
            "neg_frac": None,
            "zero_frac": None,
            "pos_frac": None,
        }
    neg = sum(v < 0 for v in values)
    zero = sum(v == 0 for v in values)
    pos = sum(v > 0 for v in values)
    n = len(values)
    return {
        "n_defined": n,
        "mean": mean(values),
        "median": median(values),
        "pstdev": pstdev(values) if n > 1 else 0.0,
        "min": min(values),
        "max": max(values),
        "neg_frac": neg / n,
        "zero_frac": zero / n,
        "pos_frac": pos / n,
    }


def empirical_percentile(ref: float | None, values: list[float]) -> float | None:
    if ref is None or not values:
        return None
    le = sum(v <= ref for v in values)
    return le / len(values)


def theta_interval_index(theta: float, theta_crit: list[float]) -> int:
    """
    Returns:
      0  if theta < first critical value
      k  if theta lies between critical values k and k+1 (1-based intervals)
      n  if theta > last critical value
    """
    for i, tc in enumerate(theta_crit):
        if theta < tc:
            return i
    return len(theta_crit)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze N.0 ensemble_summary.json against optional K.0 reference result.json"
    )
    parser.add_argument(
        "--ensemble",
        required=True,
        help="Path to ensemble_summary.json",
    )
    parser.add_argument(
        "--reference",
        required=False,
        help="Optional path to K.0 result.json",
    )
    parser.add_argument(
        "--out",
        required=False,
        help="Optional output JSON path",
    )
    args = parser.parse_args()

    ensemble_path = Path(args.ensemble)
    ensemble = load_json(ensemble_path)
    results = ensemble["results"]

    if not results:
        raise SystemExit("No runs found in ensemble_summary.json")

    theta = results[0]["config"]["theta"]
    n_runs = len(results)

    n_edges = [len(r["connected_pairs"]) for r in results]
    n_components = [len(r["connected_components"]) for r in results]
    largest_cc = [max(len(cc) for cc in r["connected_components"]) for r in results]
    connected_pair_frac = [len(r["connected_pairs"]) / 6.0 for r in results]  # N=4 fixed here
    diameters = [r["graph_diameter"] for r in results]

    fully_connected = sum(len(r["connected_components"]) == 1 for r in results)
    fragmented = sum(len(r["connected_components"]) > 1 for r in results)

    theta_positions = [theta_interval_index(theta, r["theta_crit"]) for r in results]

    pair_values: dict[str, list[float]] = {k: [] for k in PAIR_KEYS}
    pair_defined_frac: dict[str, float] = {}

    for key in PAIR_KEYS:
        defined_count = 0
        for r in results:
            v = r["standard_pairs"][key]
            if v is not None:
                defined_count += 1
                pair_values[key].append(v)
        pair_defined_frac[key] = defined_count / n_runs

    report: dict[str, Any] = {
        "n_runs": n_runs,
        "theta": theta,
        "seeds": ensemble.get("seeds", []),
        "connectivity": {
            "fully_connected_count": fully_connected,
            "fully_connected_frac": fully_connected / n_runs,
            "fragmented_count": fragmented,
            "fragmented_frac": fragmented / n_runs,
            "n_edges": safe_stats(n_edges),
            "n_components": safe_stats(n_components),
            "largest_component_size": safe_stats(largest_cc),
            "connected_pair_fraction": safe_stats(connected_pair_frac),
            "graph_diameter": safe_stats([float(d) for d in diameters]),
        },
        "theta_structure": {
            "interval_index_stats": safe_stats([float(x) for x in theta_positions]),
            "interval_indices": theta_positions,
        },
        "standard_pairs": {},
    }

    ref = None
    if args.reference:
        ref = load_json(Path(args.reference))

    for key in PAIR_KEYS:
        stats = safe_stats(pair_values[key])
        entry: dict[str, Any] = {
            "defined_fraction": pair_defined_frac[key],
            "stats_defined_only": stats,
        }

        if ref is not None:
            ref_val = ref["standard_pairs"].get(key)
            entry["reference_value"] = ref_val
            entry["reference_empirical_percentile"] = empirical_percentile(
                ref_val, pair_values[key]
            )
        report["standard_pairs"][key] = entry

    # Console summary
    print("=== K.0/N.0.5 Ensemble Report ===")
    print(f"n_runs: {report['n_runs']}")
    print(f"theta: {report['theta']}")
    print(
        f"fully_connected: {report['connectivity']['fully_connected_count']} / {report['n_runs']}"
    )
    print(
        f"fragmented: {report['connectivity']['fragmented_count']} / {report['n_runs']}"
    )
    print(
        f"mean n_edges: {report['connectivity']['n_edges']['mean']:.3f}"
        if report["connectivity"]["n_edges"]["mean"] is not None
        else "mean n_edges: None"
    )
    print(
        f"mean graph_diameter: {report['connectivity']['graph_diameter']['mean']:.3f}"
        if report["connectivity"]["graph_diameter"]["mean"] is not None
        else "mean graph_diameter: None"
    )
    print()

    for key in PAIR_KEYS:
        entry = report["standard_pairs"][key]
        print(f"[{key}]")
        print(f"  defined_fraction: {entry['defined_fraction']:.3f}")
        s = entry["stats_defined_only"]
        print(f"  mean: {s['mean']}")
        print(f"  median: {s['median']}")
        print(f"  pstdev: {s['pstdev']}")
        print(f"  min/max: {s['min']} / {s['max']}")
        print(
            f"  sign fractions (-/0/+): {s['neg_frac']} / {s['zero_frac']} / {s['pos_frac']}"
        )
        if "reference_value" in entry:
            print(f"  reference_value: {entry['reference_value']}")
            print(
                f"  reference_empirical_percentile: {entry['reference_empirical_percentile']}"
            )
        print()

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Saved report to: {out_path}")


if __name__ == "__main__":
    main()
