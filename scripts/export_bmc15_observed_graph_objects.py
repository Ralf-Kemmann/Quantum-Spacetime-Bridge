#!/usr/bin/env python3
"""
export_bmc15_observed_graph_objects.py

BMC-15e preflight exporter.

Purpose
-------
BMC-15 geometry-proxy diagnostics stored summary files, but did not export
per-graph edge-list CSV files under:

  runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/

The BMC-15e runner needs those observed graph objects as explicit edge lists.

This script reads:
  runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_metrics.json

and exports the graph objects listed there by using the referenced source CSVs:
  edge_inventory_csv
  backbone_edges_csv

No new numerics are introduced. This is an I/O/export preflight only.

Exported files
--------------
runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects/
  N81_full_baseline_edges.csv
  top_strength_reference_core_edges.csv
  maximum_spanning_tree_envelope_edges.csv
  mutual_kNN_k3_envelope_edges.csv
  threshold_path_consensus_envelope_edges.csv

Each output edge list has columns:
  source,target,weight,distance,source_graph,source_file,export_rule
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Iterable, Optional

import pandas as pd


REQUIRED_EDGE_COLUMNS = ["source", "target", "weight"]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def require_columns(df: pd.DataFrame, cols: Iterable[str], label: str) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}. Found: {list(df.columns)}")


def normalize_edges(df: pd.DataFrame, source_graph: str, source_file: Path, export_rule: str) -> pd.DataFrame:
    require_columns(df, ["source", "target", "weight"], source_graph)

    out = pd.DataFrame()
    out["source"] = df["source"].astype(str)
    out["target"] = df["target"].astype(str)
    out["weight"] = pd.to_numeric(df["weight"], errors="coerce")

    if "distance" in df.columns:
        out["distance"] = pd.to_numeric(df["distance"], errors="coerce")
    else:
        out["distance"] = pd.NA

    out["source_graph"] = source_graph
    out["source_file"] = str(source_file)
    out["export_rule"] = export_rule

    # Drop self loops and invalid weights conservatively.
    out = out[out["source"] != out["target"]].copy()
    out = out[out["weight"].notna()].copy()

    # Canonicalize undirected duplicates by sorted endpoint pair.
    a = out[["source", "target"]].min(axis=1)
    b = out[["source", "target"]].max(axis=1)
    out["_u"] = a
    out["_v"] = b
    out = out.sort_values(["_u", "_v", "weight"], ascending=[True, True, False])
    out = out.drop_duplicates(["_u", "_v"], keep="first")
    out = out.drop(columns=["_u", "_v"])

    return out.reset_index(drop=True)


def export_csv(df: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def filter_edge_inventory_for_n81(edge_inventory: pd.DataFrame) -> pd.DataFrame:
    require_columns(
        edge_inventory,
        ["edge_count_target", "case_id", "source", "target", "weight"],
        "edge_inventory_csv",
    )
    sub = edge_inventory[
        (pd.to_numeric(edge_inventory["edge_count_target"], errors="coerce") == 81)
        & (edge_inventory["case_id"].astype(str) == "baseline_all_features")
    ].copy()

    if sub.empty:
        raise ValueError(
            "Could not find edge_inventory rows for edge_count_target=81 and case_id=baseline_all_features."
        )

    return sub


def filter_backbone(backbone: pd.DataFrame, method_id: str) -> pd.DataFrame:
    require_columns(
        backbone,
        ["method_id", "edge_count_target", "case_id", "source", "target", "weight", "selected_by_method"],
        "backbone_edges_csv",
    )

    selected = backbone["selected_by_method"]
    if selected.dtype != bool:
        selected = selected.astype(str).str.lower().isin(["true", "1", "yes", "y"])

    sub = backbone[
        (backbone["method_id"].astype(str) == method_id)
        & (pd.to_numeric(backbone["edge_count_target"], errors="coerce") == 81)
        & (backbone["case_id"].astype(str) == "baseline_all_features")
        & selected
    ].copy()

    if sub.empty:
        raise ValueError(f"Could not find selected backbone rows for method_id={method_id!r}.")

    return sub


def infer_method_for_graph(graph_name: str) -> Optional[str]:
    mapping: Dict[str, str] = {
        "top_strength_reference_core": "top_strength_reference",
        "maximum_spanning_tree_envelope": "maximum_spanning_tree",
        "mutual_kNN_k3_envelope": "mutual_kNN_k3",
        "threshold_path_consensus_envelope": "threshold_path_consensus_min3",
    }
    return mapping.get(graph_name)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export BMC-15 observed graph objects as edge-list CSV files.")
    parser.add_argument(
        "--metrics",
        default="runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_metrics.json",
        help="Path to bmc15_metrics.json.",
    )
    parser.add_argument(
        "--outdir",
        default="runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects",
        help="Output directory for exported graph-object edge lists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect and report, but do not write files.",
    )
    args = parser.parse_args()

    metrics_path = Path(args.metrics).expanduser().resolve()
    outdir = Path(args.outdir).expanduser().resolve()

    if not metrics_path.exists():
        raise SystemExit(f"Metrics file not found: {metrics_path}")

    metrics = read_json(metrics_path)
    graphs = metrics.get("graphs", [])
    if not isinstance(graphs, list) or not graphs:
        raise SystemExit("No graph list found in bmc15_metrics.json under key 'graphs'.")

    edge_inventory_path = Path(metrics.get("edge_inventory_csv", "")).expanduser()
    backbone_edges_path = Path(metrics.get("backbone_edges_csv", "")).expanduser()

    if not edge_inventory_path.exists():
        raise SystemExit(f"edge_inventory_csv not found: {edge_inventory_path}")
    if not backbone_edges_path.exists():
        raise SystemExit(f"backbone_edges_csv not found: {backbone_edges_path}")

    edge_inventory = pd.read_csv(edge_inventory_path)
    backbone = pd.read_csv(backbone_edges_path)

    print("BMC-15e preflight export")
    print(f"metrics: {metrics_path}")
    print(f"edge_inventory_csv: {edge_inventory_path}")
    print(f"backbone_edges_csv: {backbone_edges_path}")
    print(f"outdir: {outdir}")
    print(f"dry_run: {args.dry_run}")
    print()

    summary_rows = []

    for graph_name in graphs:
        graph_name = str(graph_name)

        if graph_name == "N81_full_baseline":
            raw = filter_edge_inventory_for_n81(edge_inventory)
            export_rule = "edge_inventory: edge_count_target=81, case_id=baseline_all_features"
            source_file = edge_inventory_path
        else:
            method_id = infer_method_for_graph(graph_name)
            if method_id is None:
                print(f"WARNING: no export rule for graph {graph_name}; skipping.")
                continue
            raw = filter_backbone(backbone, method_id)
            export_rule = f"backbone_edges: method_id={method_id}, edge_count_target=81, case_id=baseline_all_features, selected_by_method=True"
            source_file = backbone_edges_path

        edges = normalize_edges(raw, graph_name, source_file, export_rule)
        out_path = outdir / f"{graph_name}_edges.csv"

        print(f"{graph_name}:")
        print(f"  raw rows: {len(raw)}")
        print(f"  exported edges: {len(edges)}")
        print(f"  output: {out_path}")
        print(f"  rule: {export_rule}")
        print()

        if not args.dry_run:
            export_csv(edges, out_path)

        summary_rows.append(
            {
                "graph_name": graph_name,
                "raw_rows": len(raw),
                "exported_edges": len(edges),
                "output_path": str(out_path),
                "source_file": str(source_file),
                "export_rule": export_rule,
            }
        )

    summary = pd.DataFrame(summary_rows)
    if not args.dry_run:
        summary_path = outdir / "bmc15_graph_object_export_summary.csv"
        summary.to_csv(summary_path, index=False)

        readout_path = outdir / "bmc15_graph_object_export_readout.md"
        lines = []
        lines.append("# BMC-15 Observed Graph Object Export Readout\n")
        lines.append("This is an I/O preflight export for BMC-15e.")
        lines.append("")
        lines.append("No new numerics are introduced. Existing BMC-15 source references are converted into explicit edge-list CSV files.")
        lines.append("")
        lines.append("## Exported graph objects\n")
        lines.append("| Graph object | Exported edges | Source |")
        lines.append("|---|---:|---|")
        for row in summary_rows:
            lines.append(f"| `{row['graph_name']}` | {row['exported_edges']} | `{Path(row['source_file']).name}` |")
        lines.append("")
        lines.append("## Claim boundary\n")
        lines.append("These files are graph-object exports only. They do not add evidence, recompute metrics, or change BMC-15 interpretations.")
        lines.append("")
        readout_path.write_text("\n".join(lines), encoding="utf-8")

        print(f"summary: {summary_path}")
        print(f"readout: {readout_path}")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
