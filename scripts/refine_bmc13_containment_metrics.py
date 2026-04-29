#!/usr/bin/env python3
"""
BMC-13a containment metrics refinement.

Purpose
-------
Refine BMC-13 interpretation by adding containment metrics to the existing
alternative-backbone summaries.

Why
---
Jaccard overlap can underestimate support when a small reference core is fully
contained inside larger alternative backbones. BMC-13a therefore adds:

  reference_containment = overlap_with_reference_edges / reference_edge_count
  method_containment    = overlap_with_reference_edges / method_edge_count

and analogous consensus-containment fields.

This script does not recompute backbone methods.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"CSV has no rows: {path}")
    return [dict(r) for r in rows]


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def as_int(value: Any) -> int:
    return int(float(value))


def as_float(value: Any) -> float:
    return float(value)


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def label_containment(reference_containment: float, method_containment: float) -> str:
    if reference_containment >= 0.999:
        if method_containment >= 0.75:
            return "reference_core_equivalent"
        return "reference_core_fully_contained"
    if reference_containment >= 0.50:
        return "reference_core_partially_contained"
    return "low_reference_containment"


def refine_rows(rows: Sequence[Dict[str, str]]) -> List[Dict[str, Any]]:
    ref_rows = [r for r in rows if r.get("method_id") == "top_strength_reference"]
    if len(ref_rows) != 1:
        raise ValueError("Expected exactly one top_strength_reference row.")
    reference_edge_count = as_int(ref_rows[0]["edge_count"])

    consensus_rows = [r for r in rows if str(r.get("method_id", "")).startswith("threshold_path_consensus")]
    consensus_edge_count = as_int(consensus_rows[0]["edge_count"]) if consensus_rows else 0

    refined: List[Dict[str, Any]] = []
    for r in rows:
        edge_count = as_int(r["edge_count"])
        overlap_ref = as_int(r["overlap_with_reference_edges"])
        overlap_cons = as_int(r["overlap_with_consensus_edges"])

        reference_containment = safe_div(overlap_ref, reference_edge_count)
        method_containment = safe_div(overlap_ref, edge_count)

        consensus_containment = safe_div(overlap_cons, consensus_edge_count)
        method_vs_consensus_containment = safe_div(overlap_cons, edge_count)

        out = dict(r)
        out.update({
            "reference_edge_count": reference_edge_count,
            "reference_containment": reference_containment,
            "method_containment": method_containment,
            "consensus_edge_count": consensus_edge_count,
            "consensus_containment": consensus_containment,
            "method_vs_consensus_containment": method_vs_consensus_containment,
            "containment_label": label_containment(reference_containment, method_containment),
        })
        refined.append(out)

    return refined


def write_readout(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# BMC-13a Containment Metrics Refinement Readout")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append(
        "BMC-13a refines the BMC-13 readout by adding containment metrics. "
        "This is needed because Jaccard overlap can underestimate support when a small reference core is fully contained inside larger alternative backbones."
    )
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append("| method_id | edges | overlap_ref | reference_containment | method_containment | jaccard_ref | containment_label |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for r in rows:
        lines.append(
            "| {method} | {edges} | {overlap} | {rcont:.3f} | {mcont:.3f} | {jac:.3f} | {label} |".format(
                method=r["method_id"],
                edges=r["edge_count"],
                overlap=r["overlap_with_reference_edges"],
                rcont=float(r["reference_containment"]),
                mcont=float(r["method_containment"]),
                jac=float(r["jaccard_with_reference_edges"]),
                label=r["containment_label"],
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "If reference_containment is 1.000, the full top-strength reference core is contained in that method. "
        "Low Jaccard values may then reflect size asymmetry rather than absence of the reference core."
    )
    lines.append("")
    lines.append("## Updated BMC-13 interpretation")
    lines.append("")
    lines.append(
        "The BMC-13 result should be read as a core-vs-envelope result. "
        "The six-edge top-strength reference core can be fully contained in larger alternative backbone envelopes, even when Jaccard overlap is low."
    )
    lines.append("")
    lines.append("## Conservative wording")
    lines.append("")
    lines.append(
        "BMC-13a supports the interpretation that the small N=81 top-strength reference core is embedded in all tested alternative backbone constructions, while the broader backbone envelope remains method-dependent."
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refine BMC-13 summaries with containment metrics.")
    parser.add_argument(
        "--input",
        default="runs/BMC-13/alternative_backbone_consensus_open/bmc13_method_summary.csv",
        help="Existing BMC-13 method summary CSV.",
    )
    parser.add_argument(
        "--output-root",
        default="runs/BMC-13/alternative_backbone_consensus_open",
        help="Output root for refined BMC-13a files.",
    )
    args = parser.parse_args()

    root = Path.cwd()
    input_path = root / args.input
    output_root = root / args.output_root
    output_root.mkdir(parents=True, exist_ok=True)

    rows = read_csv(input_path)
    refined = refine_rows(rows)

    refined_out = output_root / "bmc13a_method_summary_with_containment.csv"
    readout_out = output_root / "bmc13a_containment_readout.md"
    metrics_out = output_root / "bmc13a_metrics.json"

    fieldnames = [
        "method_id",
        "edge_count",
        "node_count",
        "component_count",
        "largest_component_size",
        "mean_edge_weight",
        "min_edge_weight",
        "max_edge_weight",
        "overlap_with_reference_edges",
        "jaccard_with_reference_edges",
        "reference_edge_count",
        "reference_containment",
        "method_containment",
        "overlap_with_consensus_edges",
        "jaccard_with_consensus_edges",
        "consensus_edge_count",
        "consensus_containment",
        "method_vs_consensus_containment",
        "interpretation_label",
        "containment_label",
    ]

    write_csv(refined_out, refined, fieldnames)
    write_readout(readout_out, refined)

    metrics = {
        "input": str(input_path),
        "output_root": str(output_root),
        "reference_edge_count": refined[0]["reference_edge_count"] if refined else None,
        "consensus_edge_count": refined[0]["consensus_edge_count"] if refined else None,
        "methods": [
            {
                "method_id": r["method_id"],
                "edge_count": r["edge_count"],
                "overlap_with_reference_edges": r["overlap_with_reference_edges"],
                "reference_containment": r["reference_containment"],
                "method_containment": r["method_containment"],
                "containment_label": r["containment_label"],
            }
            for r in refined
        ],
    }
    metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-13a containment refinement completed.")
    print(f"Wrote: {refined_out}")
    print(f"Wrote: {readout_out}")
    print(f"Wrote: {metrics_out}")


if __name__ == "__main__":
    main()
