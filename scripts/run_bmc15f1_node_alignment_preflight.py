#!/usr/bin/env python3
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


def graph_union_nodes(graph_dir: Path) -> set[str]:
    nodes: set[str] = set()
    for p in sorted(graph_dir.glob("*_edges.csv")):
        df = pd.read_csv(p)
        if {"source", "target"}.issubset(df.columns):
            nodes |= set(df["source"].astype(str))
            nodes |= set(df["target"].astype(str))
    return nodes


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit candidate inputs for BMC-15f.1 node alignment.")
    parser.add_argument("--graph-dir", default="runs/BMC-15/geometry_proxy_diagnostics_open/graph_objects")
    parser.add_argument("--outdir", default="runs/BMC-15f1/node_alignment_preflight_open")
    parser.add_argument(
        "--candidates",
        nargs="*",
        default=[
            "data/baseline_relational_table_real.csv",
            "data/baseline_relational_table_real_bmc08b.csv",
            "data/baseline_relational_table_real_bmc08c.csv",
            "data/bmc08c_real_units_feature_table.csv",
            "data/bmc08a_real_units_feature_table.csv",
            "data/bmc08b_real_units_feature_table.csv",
        ],
    )
    args = parser.parse_args()

    graph_dir = Path(args.graph_dir)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    gnodes = graph_union_nodes(graph_dir)
    if not gnodes:
        raise SystemExit(f"No graph-object nodes found under {graph_dir}")

    rows = []
    for cand in args.candidates:
        p = Path(cand)
        row = {
            "candidate_path": str(p),
            "candidate_exists": p.exists(),
            "candidate_kind": "",
            "candidate_node_count": "",
            "graph_union_node_count": len(gnodes),
            "missing_nodes_vs_graph_union": "",
            "extra_nodes_vs_graph_union": "",
            "exact_match": False,
            "recommendation": "",
        }

        if not p.exists():
            row["recommendation"] = "missing_file"
            rows.append(row)
            continue

        try:
            kind, cnodes = infer_nodes_from_csv(p)
            missing = sorted(gnodes - cnodes)
            extra = sorted(cnodes - gnodes)
            exact = not missing and not extra
            row.update({
                "candidate_kind": kind,
                "candidate_node_count": len(cnodes),
                "missing_nodes_vs_graph_union": json.dumps(missing, ensure_ascii=False),
                "extra_nodes_vs_graph_union": json.dumps(extra, ensure_ascii=False),
                "exact_match": exact,
                "recommendation": "use_for_bmc15f1" if exact else "not_exact_match_inspect",
            })
        except Exception as exc:
            row["recommendation"] = f"error: {exc}"
        rows.append(row)

    df = pd.DataFrame(rows)
    csv_path = outdir / "node_alignment_candidates.csv"
    df.to_csv(csv_path, index=False)

    lines = []
    lines.append("# BMC-15f.1 Node-Alignment Preflight Readout\n")
    lines.append(f"- Graph object directory: `{graph_dir}`")
    lines.append(f"- Graph union node count: `{len(gnodes)}`")
    lines.append("")
    lines.append("## Candidate summary\n")
    lines.append("| Candidate | Exists | Kind | Nodes | Exact match | Recommendation |")
    lines.append("|---|---:|---|---:|---:|---|")
    for _, r in df.iterrows():
        lines.append(
            f"| `{r['candidate_path']}` | {r['candidate_exists']} | `{r['candidate_kind']}` | "
            f"{r['candidate_node_count']} | {r['exact_match']} | `{r['recommendation']}` |"
        )
    lines.append("")
    lines.append("## Methodological boundary\n")
    lines.append("This preflight only compares node sets. It does not recompute envelope diagnostics.")
    lines.append("")

    readout_path = outdir / "readout.md"
    readout_path.write_text("\n".join(lines), encoding="utf-8")

    print("BMC-15f.1 node-alignment preflight complete.")
    print(f"CSV: {csv_path}")
    print(f"Readout: {readout_path}")
    print(df.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
