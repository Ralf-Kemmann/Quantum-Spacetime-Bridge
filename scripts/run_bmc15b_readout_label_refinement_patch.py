#!/usr/bin/env python3
"""
BMC-15b Readout / Label Refinement Patch.

Reads:
  runs/BMC-15b/geometry_proxy_null_comparison_open/
    bmc15b_observed_vs_null_distribution_summary.csv

Writes:
  bmc15b_observed_vs_null_distribution_summary_refined.csv
  bmc15b_readout_refined.md
  bmc15b_refinement_patch_metrics.json

This patch does not rerun null models and does not modify original outputs.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence


FEATURE_STRUCTURED = {
    "global_covariance_gaussian",
    "family_covariance_gaussian",
    "gaussian_copula_feature_null",
}

GRAPH_REWIRE = {
    "weight_rank_edge_rewire",
    "degree_preserving_edge_rewire",
    "degree_weightclass_edge_rewire",
}


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return [dict(r) for r in csv.DictReader(f)]


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def f(row: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        x = float(row.get(key, default))
        return x if math.isfinite(x) else default
    except Exception:
        return default


def family_group(model: str) -> str:
    if model in FEATURE_STRUCTURED:
        return "feature_structured_nulls"
    if model in GRAPH_REWIRE:
        return "graph_rewire_nulls"
    return "other_nulls"


def refine_label(row: Dict[str, Any], tol: float) -> str:
    obs = f(row, "observed_value")
    nmin = f(row, "null_min")
    q05 = f(row, "null_q05")
    med = f(row, "null_median")
    q95 = f(row, "null_q95")
    nmax = f(row, "null_max")
    direction = row.get("metric_direction", "not_directional")

    # All-null tie: observed equals the whole null support.
    if abs(obs - nmin) <= tol and abs(obs - nmax) <= tol:
        return "observed_null_equivalent"

    # Central degenerate tie.
    if abs(obs - med) <= tol and abs(q05 - q95) <= tol:
        return "observed_null_equivalent"

    if direction == "lower_better":
        if obs < q05 - tol:
            return "observed_more_geometry_like_than_null"
        if obs > q95 + tol:
            return "observed_less_geometry_like_than_null"
        return "observed_null_typical"

    if direction == "higher_better":
        if obs > q95 + tol:
            return "observed_more_geometry_like_than_null"
        if obs < q05 - tol:
            return "observed_less_geometry_like_than_null"
        return "observed_null_typical"

    if direction == "closer_to_one":
        # Full null deviations are not in the summary, so avoid overclaiming.
        return "observed_null_typical"

    return "not_directional"


def refine_rows(rows: Sequence[Dict[str, str]], tol: float) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        nr: Dict[str, Any] = dict(r)
        nr["null_family_group"] = family_group(str(r.get("null_model_id", "")))
        nr["triangle_mode_refined"] = (
            r.get("triangle_mode", "") if r.get("triangle_mode", "") else
            ("not_recorded_in_source_summary" if r.get("metric_group") == "triangle" else "")
        )
        emb = r.get("embedding_dimension", "")
        nr["embedding_dimension_refined"] = str(int(float(emb))) if emb not in ("", None) else ""
        nr["original_interpretation_label"] = r.get("interpretation_label", "")
        nr["interpretation_label_refined"] = refine_label(r, tol)
        out.append(nr)
    return out


def counts_by(rows: Sequence[Dict[str, Any]], group_key: str) -> Dict[str, Dict[str, int]]:
    d = defaultdict(Counter)
    for r in rows:
        d[str(r.get(group_key, ""))][str(r.get("interpretation_label_refined", ""))] += 1
    return {k: dict(v) for k, v in d.items()}


def fmt(x: Any) -> str:
    try:
        return f"{float(x):.3f}"
    except Exception:
        return str(x)


def selected_embedding(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        r for r in rows
        if r.get("metric_group") == "embedding"
        and r.get("metric") in {"stress_normalized", "negative_to_positive_abs_ratio"}
        and r.get("graph_id") in {"N81_full_baseline", "maximum_spanning_tree_envelope", "mutual_kNN_k3_envelope"}
    ]


def selected_triangle(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        r for r in rows
        if r.get("metric_group") == "triangle"
        and r.get("metric") == "violation_fraction"
        and r.get("graph_id") == "N81_full_baseline"
    ]


def selected_geodesic(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        r for r in rows
        if r.get("metric_group") == "geodesic"
        and r.get("metric") in {"unreachable_pair_fraction", "mean_path_direct_ratio"}
        and r.get("graph_id") in {"maximum_spanning_tree_envelope", "mutual_kNN_k3_envelope"}
    ]


def write_readout(path: Path, rows: Sequence[Dict[str, Any]], metrics: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines += [
        "# BMC-15b Geometry-Proxy Null Comparison Refined Readout",
        "",
        "## Patch purpose",
        "",
        "This readout refines labels and table visibility for the existing BMC-15b run.",
        "",
        "It does not rerun null models and does not change numeric null distributions.",
        "",
        "## Label refinement",
        "",
        "All-zero observed/null tie cases are now labeled as:",
        "",
        "```text",
        "observed_null_equivalent",
        "```",
        "",
        "rather than as less geometry-like.",
        "",
        "## Label counts by null-family group",
        "",
        "| null_family_group | more_geometry_like | null_typical | null_equivalent | less_geometry_like | not_directional |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for group, c in metrics["label_counts_by_family_group"].items():
        lines.append(
            f"| {group} | "
            f"{c.get('observed_more_geometry_like_than_null', 0)} | "
            f"{c.get('observed_null_typical', 0)} | "
            f"{c.get('observed_null_equivalent', 0)} | "
            f"{c.get('observed_less_geometry_like_than_null', 0)} | "
            f"{c.get('not_directional', 0)} |"
        )

    lines += [
        "",
        "## Key embedding comparison rows",
        "",
        "| null_model_id | group | graph_id | dim | metric | observed | null_median | null_q05 | null_q95 | refined_label |",
        "|---|---|---|---:|---|---:|---:|---:|---:|---|",
    ]

    for r in selected_embedding(rows):
        lines.append(
            f"| {r['null_model_id']} | {r['null_family_group']} | {r['graph_id']} | "
            f"{r.get('embedding_dimension_refined','')} | {r['metric']} | "
            f"{fmt(r.get('observed_value'))} | {fmt(r.get('null_median'))} | "
            f"{fmt(r.get('null_q05'))} | {fmt(r.get('null_q95'))} | "
            f"{r['interpretation_label_refined']} |"
        )

    lines += [
        "",
        "## N81 triangle comparison rows",
        "",
        "| null_model_id | group | graph_id | triangle_mode | observed | null_median | null_q05 | null_q95 | refined_label |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]

    for r in selected_triangle(rows):
        lines.append(
            f"| {r['null_model_id']} | {r['null_family_group']} | {r['graph_id']} | "
            f"{r['triangle_mode_refined']} | {fmt(r.get('observed_value'))} | "
            f"{fmt(r.get('null_median'))} | {fmt(r.get('null_q05'))} | "
            f"{fmt(r.get('null_q95'))} | {r['interpretation_label_refined']} |"
        )

    lines += [
        "",
        "## Selected geodesic consistency rows",
        "",
        "| null_model_id | group | graph_id | metric | observed | null_median | null_q05 | null_q95 | refined_label |",
        "|---|---|---|---|---:|---:|---:|---:|---|",
    ]

    for r in selected_geodesic(rows):
        lines.append(
            f"| {r['null_model_id']} | {r['null_family_group']} | {r['graph_id']} | "
            f"{r['metric']} | {fmt(r.get('observed_value'))} | "
            f"{fmt(r.get('null_median'))} | {fmt(r.get('null_q05'))} | "
            f"{fmt(r.get('null_q95'))} | {r['interpretation_label_refined']} |"
        )

    lines += [
        "",
        "## Refined interpretation",
        "",
        "BMC-15b remains mixed but informative.",
        "",
        "The observed N81 baseline and selected envelopes are generally more embedding-compatible than graph-rewire nulls, especially weight-rank, degree-preserving, and degree/weightclass rewiring controls.",
        "",
        "Against feature-structured nulls, especially family covariance and Gaussian copula feature nulls, the observed geometry-proxy values are often null-typical.",
        "",
        "Triangle-defect all-zero cases should be interpreted as null-equivalent rather than less geometry-like.",
        "",
        "## Conservative statement",
        "",
        "> BMC-15b suggests that the observed geometry-proxy behavior is not merely a generic consequence of graph rewiring or degree/weight-rank structure, but feature/family/correlation structure can itself generate similar geometry-proxy values. Thus the geometry-proxy signal is informative but not uniquely specific. The result remains methodological and does not establish physical spacetime emergence.",
        "",
        "## Internal summary",
        "",
        "```text",
        "Der Klunker glitzert geordneter als Grad-/Kantensortier-Klumpen.",
        "Aber feature-/family-/copula-artige Nullklumpen können ebenfalls ordentlich glitzern.",
        "Die alten all-zero Triangle-Labels waren ein Beschriftungskobold.",
        "```",
        "",
    ]

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refine BMC-15b readout labels.")
    parser.add_argument(
        "--input",
        default="runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_observed_vs_null_distribution_summary.csv",
    )
    parser.add_argument(
        "--output-dir",
        default="runs/BMC-15b/geometry_proxy_null_comparison_open",
    )
    parser.add_argument("--tie-tolerance", type=float, default=1e-12)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    rows = read_csv(input_path)
    refined = refine_rows(rows, args.tie_tolerance)

    refined_csv = output_dir / "bmc15b_observed_vs_null_distribution_summary_refined.csv"
    refined_readout = output_dir / "bmc15b_readout_refined.md"
    metrics_path = output_dir / "bmc15b_refinement_patch_metrics.json"

    fieldnames = list(refined[0].keys()) if refined else []
    write_csv(refined_csv, refined, fieldnames)

    metrics = {
        "input": str(input_path),
        "output_refined_csv": str(refined_csv),
        "output_refined_readout": str(refined_readout),
        "row_count": len(refined),
        "tie_tolerance": args.tie_tolerance,
        "label_counts_by_family_group": counts_by(refined, "null_family_group"),
        "label_counts_by_null_model": counts_by(refined, "null_model_id"),
        "note": "Refinement only; original BMC-15b numeric distributions unchanged.",
    }

    write_readout(refined_readout, refined, metrics)
    metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-15b readout / label refinement patch completed.")
    print(f"Wrote: {refined_csv}")
    print(f"Wrote: {refined_readout}")
    print(f"Wrote: {metrics_path}")


if __name__ == "__main__":
    main()
