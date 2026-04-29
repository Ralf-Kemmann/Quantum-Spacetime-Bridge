#!/usr/bin/env python3
"""
BMC-15e.2 node-aligned geometry-control preflight.

This audit checks whether the canonical BMC-08c 22-node sign-sensitive feature table
matches the BMC-15 graph-object node space and records current BMC-15e metadata.

It does not regenerate geometry controls.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


SOURCE_COLS = ["source", "src", "i", "node_i", "u", "from"]
TARGET_COLS = ["target", "dst", "j", "node_j", "v", "to"]
NODE_ID_COLS = ["node", "node_id", "id", "name", "label"]


def find_col(cols: Iterable[str], candidates: list[str]) -> Optional[str]:
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def infer_nodes_from_csv(path: Path) -> tuple[str, set[str]]:
    df = pd.read_csv(path)
    src = find_col(df.columns, SOURCE_COLS)
    dst = find_col(df.columns, TARGET_COLS)
    if src and dst:
        return "edge_table", set(df[src].astype(str)) | set(df[dst].astype(str))

    node_col = find_col(df.columns, NODE_ID_COLS)
    if node_col is None:
        node_col = df.columns[0]
    return "wide_or_node_table", set(df[node_col].astype(str))


def read_graph_object_nodes(edge_path: Path) -> set[str]:
    df = pd.read_csv(edge_path)
    if not {"source", "target"}.issubset(df.columns):
        return set()
    return set(df["source"].astype(str)) | set(df["target"].astype(str))


def json_list(values: Iterable[str]) -> str:
    return json.dumps(sorted(values), ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="BMC-15e.2 node-alignment preflight audit.")
    parser.add_argument("--canonical-input", default="data/bmc08c_real_units_feature_table.csv")
    parser.add_argument("--graph-dir", default="runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects")
    parser.add_argument("--bmc15e-summary", default="runs/BMC-15e/geometry_control_nulls_open/summary.json")
    parser.add_argument("--outdir", default="runs/BMC-15e2/node_aligned_geometry_control_preflight_open")
    args = parser.parse_args()

    canonical_path = Path(args.canonical_input)
    graph_dir = Path(args.graph_dir)
    bmc15e_summary_path = Path(args.bmc15e_summary)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    rows = []

    canonical_nodes: set[str] = set()
    canonical_kind = ""
    if canonical_path.exists():
        canonical_kind, canonical_nodes = infer_nodes_from_csv(canonical_path)

    def add_row(
        object_name: str,
        object_kind: str,
        path: Path,
        exists: bool,
        nodes: Optional[set[str]],
        notes: str = "",
    ) -> None:
        if nodes is None:
            node_count = ""
            missing = ""
            extra = ""
            exact = ""
        else:
            node_count = len(nodes)
            missing = json_list(canonical_nodes - nodes) if canonical_nodes else ""
            extra = json_list(nodes - canonical_nodes) if canonical_nodes else ""
            exact = (nodes == canonical_nodes) if canonical_nodes else ""
        rows.append({
            "object_name": object_name,
            "object_kind": object_kind,
            "path": str(path),
            "exists": exists,
            "node_count": node_count,
            "missing_vs_canonical": missing,
            "extra_vs_canonical": extra,
            "exact_match_canonical": exact,
            "notes": notes,
        })

    add_row(
        "canonical_bmc08c_feature_table",
        "canonical_feature_table",
        canonical_path,
        canonical_path.exists(),
        canonical_nodes if canonical_path.exists() else None,
        f"inferred_kind={canonical_kind}" if canonical_path.exists() else "missing",
    )

    graph_union: set[str] = set()
    if graph_dir.exists():
        for edge_path in sorted(graph_dir.glob("*_edges.csv")):
            nodes = read_graph_object_nodes(edge_path)
            graph_union |= nodes
            add_row(edge_path.stem.replace("_edges", ""), "graph_object", edge_path, True, nodes)
    add_row("graph_object_union", "graph_union", graph_dir, graph_dir.exists(), graph_union if graph_union else None)

    summary_notes = []
    if bmc15e_summary_path.exists():
        try:
            summary = json.loads(bmc15e_summary_path.read_text(encoding="utf-8"))
            for key in [
                "run_id",
                "n_observed_graphs",
                "n_control_metric_rows",
                "n_family_summary_rows",
                "n_observed_position_rows",
                "warnings",
                "claim_boundary",
            ]:
                if key in summary:
                    summary_notes.append(f"{key}={summary[key]}")
            # Also capture observed graph metadata if present.
            for meta_key in ["observed_graphs_loaded", "observed_objects_loaded", "observed_graph_objects"]:
                if isinstance(summary.get(meta_key), dict):
                    for name, info in summary[meta_key].items():
                        summary_notes.append(f"{meta_key}.{name}={info}")
        except Exception as exc:
            summary_notes.append(f"error_reading_summary={exc}")
    else:
        summary_notes.append("missing")

    add_row(
        "current_bmc15e_summary",
        "bmc15e_summary",
        bmc15e_summary_path,
        bmc15e_summary_path.exists(),
        None,
        "; ".join(summary_notes),
    )

    df = pd.DataFrame(rows)
    csv_path = outdir / "node_alignment_summary.csv"
    df.to_csv(csv_path, index=False)

    exact_graph_objects = df[df["object_kind"].eq("graph_object")]["exact_match_canonical"].tolist()
    all_graph_exact = bool(exact_graph_objects) and all(x is True or str(x) == "True" for x in exact_graph_objects)
    union_exact = df[(df["object_kind"] == "graph_union")]["exact_match_canonical"].astype(str).eq("True").any()

    if not canonical_nodes:
        decision = "stop_missing_canonical_input"
    elif not union_exact:
        decision = "stop_graph_union_not_canonical"
    elif all_graph_exact:
        decision = "alignment_verified_all_graph_objects_match_canonical"
    else:
        decision = "partial_alignment_graph_union_matches_but_some_objects_are_subgraphs"

    readout = []
    readout.append("# BMC-15e.2 Node-Aligned Geometry-Control Preflight Readout\n")
    readout.append(f"- Canonical input: `{canonical_path}`")
    readout.append(f"- Canonical exists: `{canonical_path.exists()}`")
    readout.append(f"- Canonical node count: `{len(canonical_nodes) if canonical_nodes else ''}`")
    readout.append(f"- Graph object directory: `{graph_dir}`")
    readout.append(f"- BMC-15e summary: `{bmc15e_summary_path}`")
    readout.append(f"- Decision: `{decision}`")
    readout.append("")
    readout.append("## Canonical nodes\n")
    for node in sorted(canonical_nodes):
        readout.append(f"- `{node}`")
    readout.append("")
    readout.append("## Audit table\n")
    readout.append("| Object | Kind | Exists | Nodes | Exact canonical match | Notes |")
    readout.append("|---|---|---:|---:|---:|---|")
    for _, r in df.iterrows():
        notes = str(r["notes"]).replace("|", "/")
        readout.append(
            f"| `{r['object_name']}` | `{r['object_kind']}` | {r['exists']} | "
            f"{r['node_count']} | {r['exact_match_canonical']} | {notes} |"
        )
    readout.append("")
    readout.append("## Interpretation boundary\n")
    readout.append("This preflight audits node alignment only. It does not regenerate geometry controls.")
    readout.append("")
    readout.append("## Suggested next action\n")
    if decision == "alignment_verified_all_graph_objects_match_canonical":
        readout.append("Existing graph-object node alignment is verified. Decide whether BMC-15e.2 should be an audit-certified note or a provenance rerun.")
    elif decision == "partial_alignment_graph_union_matches_but_some_objects_are_subgraphs":
        readout.append("Graph union matches canonical nodes, but some graph objects are subgraphs. This may be expected for core objects. Inspect before rerun.")
    else:
        readout.append("Do not rerun BMC-15e.2 until the mismatch is resolved.")

    readout_path = outdir / "readout.md"
    readout_path.write_text("\n".join(readout), encoding="utf-8")

    print("BMC-15e.2 node-alignment preflight complete.")
    print(f"CSV: {csv_path}")
    print(f"Readout: {readout_path}")
    print(f"Decision: {decision}")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
