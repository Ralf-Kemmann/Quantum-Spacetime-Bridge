#!/usr/bin/env python3
from __future__ import annotations

import argparse, csv, json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: PyYAML. Install with: python3 -m pip install pyyaml") from exc

Edge = Tuple[str, str]

def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config is not a mapping: {path}")
    return data

def project_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else root / p

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

def norm_edge(a: str, b: str) -> Edge:
    x, y = sorted((str(a), str(b)))
    return (x, y)

def edge_key(row: Dict[str, Any]) -> Edge:
    return norm_edge(str(row["source"]), str(row["target"]))

def as_float(value: Any) -> float:
    return float(value)

def as_int(value: Any) -> int:
    return int(float(value))

def sorted_edges(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted([dict(r) for r in rows], key=lambda r: (-as_float(r["weight"]), str(r["source"]), str(r["target"])))

def filter_rows(rows: Sequence[Dict[str, str]], edge_count: int, case_id: str) -> List[Dict[str, Any]]:
    out = [dict(r) for r in rows if as_int(r["edge_count_target"]) == edge_count and str(r["case_id"]) == case_id]
    if not out:
        raise ValueError(f"No rows for edge_count={edge_count}, case_id={case_id}")
    ordered = sorted_edges(out)
    for idx, row in enumerate(ordered, start=1):
        row["edge_rank_in_source"] = idx
    return ordered

def select_top_strength(rows: Sequence[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    return sorted_edges(rows)[:k]

def select_mutual_knn(rows: Sequence[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    ordered = sorted_edges(rows)
    neighbors: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    row_by_edge: Dict[Edge, Dict[str, Any]] = {}
    for row in ordered:
        a, b, w = str(row["source"]), str(row["target"]), as_float(row["weight"])
        neighbors[a].append((b, w))
        neighbors[b].append((a, w))
        row_by_edge[norm_edge(a, b)] = dict(row)
    top_sets: Dict[str, Set[str]] = {}
    for node, vals in neighbors.items():
        top_sets[node] = {n for n, _ in sorted(vals, key=lambda x: (-x[1], x[0]))[:k]}
    selected: Set[Edge] = set()
    for a, vals in top_sets.items():
        for b in vals:
            if b in top_sets and a in top_sets[b]:
                selected.add(norm_edge(a, b))
    return sorted_edges([row_by_edge[e] for e in selected])

def select_maximum_spanning_tree(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = sorted_edges(rows)
    nodes = sorted({str(r["source"]) for r in ordered} | {str(r["target"]) for r in ordered})
    parent = {n: n for n in nodes}
    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a: str, b: str) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[rb] = ra
        return True
    selected: List[Dict[str, Any]] = []
    for row in ordered:
        if union(str(row["source"]), str(row["target"])):
            selected.append(dict(row))
        if len(selected) == max(0, len(nodes) - 1):
            break
    return selected

def select_threshold_path_consensus(all_rows: Sequence[Dict[str, str]], case_id: str, edge_counts: Sequence[int], minimum_presence_count: int, reference_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    presence: Dict[Edge, int] = defaultdict(int)
    reference_by_edge = {edge_key(r): dict(r) for r in reference_rows}
    for n in edge_counts:
        for row in filter_rows(all_rows, n, case_id):
            presence[edge_key(row)] += 1
    selected = [e for e, c in presence.items() if c >= minimum_presence_count and e in reference_by_edge]
    return sorted_edges([reference_by_edge[e] for e in selected])

def edge_set(rows: Sequence[Dict[str, Any]]) -> Set[Edge]:
    return {edge_key(r) for r in rows}

def graph_components(rows: Sequence[Dict[str, Any]]) -> Tuple[int, int, int]:
    nodes = sorted({str(r["source"]) for r in rows} | {str(r["target"]) for r in rows})
    if not nodes:
        return 0, 0, 0
    adj: Dict[str, Set[str]] = {n: set() for n in nodes}
    for row in rows:
        a, b = str(row["source"]), str(row["target"])
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen: Set[str] = set()
    sizes: List[int] = []
    for start in nodes:
        if start in seen:
            continue
        q = deque([start]); seen.add(start); size = 0
        while q:
            cur = q.popleft(); size += 1
            for nxt in adj.get(cur, set()):
                if nxt not in seen:
                    seen.add(nxt); q.append(nxt)
        sizes.append(size)
    return len(nodes), len(sizes), max(sizes) if sizes else 0

def jaccard(a: Set[Edge], b: Set[Edge]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0

def method_summary(method_id: str, rows: Sequence[Dict[str, Any]], reference_edges: Set[Edge], consensus_edges: Set[Edge], high_min: float, moderate_min: float) -> Dict[str, Any]:
    edges = edge_set(rows)
    weights = [as_float(r["weight"]) for r in rows]
    node_count, component_count, largest_component = graph_components(rows)
    jac_ref = jaccard(edges, reference_edges)
    jac_cons = jaccard(edges, consensus_edges)
    if method_id == "top_strength_reference":
        label = "reference"
    elif jac_ref >= high_min or jac_cons >= high_min:
        label = "high_overlap"
    elif jac_ref >= moderate_min or jac_cons >= moderate_min:
        label = "moderate_overlap"
    else:
        label = "low_overlap"
    return {
        "method_id": method_id,
        "edge_count": len(edges),
        "node_count": node_count,
        "component_count": component_count,
        "largest_component_size": largest_component,
        "mean_edge_weight": sum(weights) / len(weights) if weights else 0.0,
        "min_edge_weight": min(weights) if weights else 0.0,
        "max_edge_weight": max(weights) if weights else 0.0,
        "overlap_with_reference_edges": len(edges & reference_edges),
        "jaccard_with_reference_edges": jac_ref,
        "overlap_with_consensus_edges": len(edges & consensus_edges),
        "jaccard_with_consensus_edges": jac_cons,
        "interpretation_label": label,
    }

def pairwise_summary(method_edges: Dict[str, Set[Edge]]) -> List[Dict[str, Any]]:
    ids = sorted(method_edges)
    out: List[Dict[str, Any]] = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            ea, eb = method_edges[a], method_edges[b]
            union = ea | eb
            shared = ea & eb
            out.append({"method_a": a, "method_b": b, "edges_a": len(ea), "edges_b": len(eb), "shared_edges": len(shared), "union_edges": len(union), "jaccard": len(shared) / len(union) if union else 0.0})
    return out

def write_readout(path: Path, summary_rows: Sequence[Dict[str, Any]], pair_rows: Sequence[Dict[str, Any]]) -> None:
    lines = ["# BMC-13 Alternative Backbone / Consensus-Backbone Readout", "", "## Run", "", "- mode: alternative backbone diagnostics from existing BMC-12e edge inventory", "- focus: N=81, baseline_all_features", "", "## Befund", "", "| method_id | edges | nodes | components | largest_component | jaccard_ref | jaccard_consensus | label |", "|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in summary_rows:
        lines.append(f"| {r['method_id']} | {r['edge_count']} | {r['node_count']} | {r['component_count']} | {r['largest_component_size']} | {float(r['jaccard_with_reference_edges']):.3f} | {float(r['jaccard_with_consensus_edges']):.3f} | {r['interpretation_label']} |")
    lines += ["", "## Pairwise overlap", "", "| method_a | method_b | shared_edges | jaccard |", "|---|---|---:|---:|"]
    for r in pair_rows:
        lines.append(f"| {r['method_a']} | {r['method_b']} | {r['shared_edges']} | {float(r['jaccard']):.3f} |")
    lines += ["", "## Interpretation", "", "High overlap across conceptually different extraction rules would support method-crossing persistence of the N=81 sparse/local anchor. Low overlap would indicate that the current anchor is specific to the top-strength extraction family.", "", "## Hypothesis", "", "If alternative methods recover a shared core, the N=81 anchor may represent a persistent relational locality-backbone candidate rather than only a top-strength artifact.", "", "## Open gap", "", "BMC-13 remains a graph-method diagnostic. It does not establish physical spacetime emergence or geometry reconstruction.", ""]
    path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMC-13 alternative backbone consensus diagnostics.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    cfg = load_yaml(project_path(root, args.config))
    input_csv = project_path(root, cfg["inputs"]["bmc12e_edge_inventory_csv"])
    output_root = project_path(root, cfg["outputs"]["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    all_rows = read_csv(input_csv)
    edge_count = int(cfg["focus"]["reference_edge_count"])
    case_id = str(cfg["focus"]["reference_case_id"])
    sparse_path_counts = [int(x) for x in cfg["focus"]["sparse_path_edge_counts"]]
    reference_rows_all = filter_rows(all_rows, edge_count, case_id)

    method_rows: Dict[str, List[Dict[str, Any]]] = {}
    if cfg["methods"]["top_strength_reference"].get("enabled", True):
        k = int(cfg["methods"]["top_strength_reference"].get("k_reference_edges", 6))
        method_rows["top_strength_reference"] = select_top_strength(reference_rows_all, k)
    if cfg["methods"]["mutual_knn"].get("enabled", True):
        k = int(cfg["methods"]["mutual_knn"].get("k", 3))
        method_rows[f"mutual_kNN_k{k}"] = select_mutual_knn(reference_rows_all, k)
    if cfg["methods"]["maximum_spanning_tree"].get("enabled", True):
        method_rows["maximum_spanning_tree"] = select_maximum_spanning_tree(reference_rows_all)
    if cfg["methods"]["threshold_path_consensus"].get("enabled", True):
        mpc = int(cfg["methods"]["threshold_path_consensus"].get("minimum_presence_count", len(sparse_path_counts)))
        method_rows[f"threshold_path_consensus_min{mpc}"] = select_threshold_path_consensus(all_rows, case_id, sparse_path_counts, mpc, reference_rows_all)

    if "top_strength_reference" not in method_rows:
        raise ValueError("top_strength_reference must be enabled.")

    reference_edges = edge_set(method_rows["top_strength_reference"])
    consensus_id = next((m for m in method_rows if m.startswith("threshold_path_consensus")), None)
    consensus_edges = edge_set(method_rows[consensus_id]) if consensus_id else set()
    high_min = float(cfg["interpretation"].get("high_overlap_jaccard_min", 0.60))
    moderate_min = float(cfg["interpretation"].get("moderate_overlap_jaccard_min", 0.30))

    edge_output_rows: List[Dict[str, Any]] = []
    for method_id, rows in method_rows.items():
        for row in rows:
            edge_output_rows.append({"method_id": method_id, "edge_count_target": edge_count, "case_id": case_id, "source": row["source"], "target": row["target"], "weight": row["weight"], "edge_rank_in_source": row.get("edge_rank_in_source", ""), "selected_by_method": "true"})

    summary_rows = sorted([method_summary(mid, rows, reference_edges, consensus_edges, high_min, moderate_min) for mid, rows in method_rows.items()], key=lambda r: str(r["method_id"]))
    method_edges = {mid: edge_set(rows) for mid, rows in method_rows.items()}
    pair_rows = pairwise_summary(method_edges)

    edges_out = output_root / "bmc13_backbone_edges.csv"
    summary_out = output_root / "bmc13_method_summary.csv"
    pair_out = output_root / "bmc13_pairwise_overlap_summary.csv"
    readout_out = output_root / "bmc13_readout.md"
    metrics_out = output_root / "bmc13_metrics.json"

    write_csv(edges_out, edge_output_rows, ["method_id", "edge_count_target", "case_id", "source", "target", "weight", "edge_rank_in_source", "selected_by_method"])
    write_csv(summary_out, summary_rows, ["method_id", "edge_count", "node_count", "component_count", "largest_component_size", "mean_edge_weight", "min_edge_weight", "max_edge_weight", "overlap_with_reference_edges", "jaccard_with_reference_edges", "overlap_with_consensus_edges", "jaccard_with_consensus_edges", "interpretation_label"])
    write_csv(pair_out, pair_rows, ["method_a", "method_b", "edges_a", "edges_b", "shared_edges", "union_edges", "jaccard"])
    write_readout(readout_out, summary_rows, pair_rows)
    metrics_out.write_text(json.dumps({"run_id": cfg.get("run_id", "BMC13_alternative_backbone_consensus_open"), "input_csv": str(input_csv), "output_root": str(output_root), "focus": {"edge_count_target": edge_count, "case_id": case_id, "sparse_path_edge_counts": sparse_path_counts}, "methods": sorted(method_rows.keys()), "method_edge_counts": {mid: len(rows) for mid, rows in method_rows.items()}, "summary_rows": summary_rows}, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-13 alternative backbone / consensus diagnostics completed.")
    print(f"Wrote: {edges_out}")
    print(f"Wrote: {summary_out}")
    print(f"Wrote: {pair_out}")
    print(f"Wrote: {readout_out}")
    print(f"Wrote: {metrics_out}")

if __name__ == "__main__":
    main()
