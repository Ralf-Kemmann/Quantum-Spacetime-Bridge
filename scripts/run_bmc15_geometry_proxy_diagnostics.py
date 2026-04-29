#!/usr/bin/env python3
"""
BMC-15 Geometry-Proxy Diagnostics Runner.

BMC-15a observed baseline only.

Purpose
-------
Test whether the robust N=81 core/envelope structure exhibits geometry-like
proxy behavior.

Important
---------
This script does not infer physical spacetime emergence, causal geometry,
metric tensors, or continuum reconstruction. It only computes diagnostic
proxies on observed graph objects.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict, deque
from itertools import combinations
from pathlib import Path
from statistics import mean, median
from typing import Any, Dict, List, Sequence, Set, Tuple

import numpy as np

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


def as_float(value: Any, field: str = "") -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(f"Could not parse numeric field {field!r}: {value!r}") from exc
    if not math.isfinite(x):
        raise ValueError(f"Non-finite numeric field {field!r}: {value!r}")
    return x


def as_int(value: Any) -> int:
    return int(float(value))


def norm_edge(a: str, b: str) -> Edge:
    x, y = sorted((str(a), str(b)))
    return (x, y)


def proxy_distance(weight: float, eps: float) -> float:
    w = max(float(weight), eps)
    return -math.log(w)


def edge_key(row: Dict[str, Any]) -> Edge:
    return norm_edge(str(row["source"]), str(row["target"]))


def filter_inventory_rows(rows: Sequence[Dict[str, str]], edge_count: int, case_id: str) -> List[Dict[str, Any]]:
    out = []
    for r in rows:
        if as_int(r["edge_count_target"]) == edge_count and str(r["case_id"]) == case_id:
            out.append(dict(r))
    if not out:
        raise ValueError(f"No inventory rows for edge_count_target={edge_count}, case_id={case_id!r}")
    out.sort(key=lambda r: (-as_float(r["weight"], "weight"), str(r["source"]), str(r["target"])))
    return out


def filter_backbone_method(rows: Sequence[Dict[str, str]], method_id: str) -> List[Dict[str, Any]]:
    out = [dict(r) for r in rows if str(r.get("method_id")) == method_id]
    if not out:
        raise ValueError(f"No backbone rows for method_id={method_id!r}")
    out.sort(key=lambda r: (-as_float(r["weight"], "weight"), str(r["source"]), str(r["target"])))
    return out


def build_graph_objects(
    inventory_rows: Sequence[Dict[str, str]],
    backbone_rows: Sequence[Dict[str, str]],
    edge_count: int,
    case_id: str,
    include: Sequence[str],
) -> Dict[str, Dict[str, Any]]:
    graphs: Dict[str, Dict[str, Any]] = {}

    if "N81_full_baseline" in include:
        rows = filter_inventory_rows(inventory_rows, edge_count, case_id)
        graphs["N81_full_baseline"] = {
            "graph_id": "N81_full_baseline",
            "source": "edge_inventory",
            "method_id": "baseline_all_features",
            "rows": rows,
        }

    method_map = {
        "top_strength_reference_core": "top_strength_reference",
        "maximum_spanning_tree_envelope": "maximum_spanning_tree",
        "mutual_kNN_k3_envelope": "mutual_kNN_k3",
        "threshold_path_consensus_envelope": "threshold_path_consensus_min3",
    }

    for graph_id, method_id in method_map.items():
        if graph_id in include:
            rows = filter_backbone_method(backbone_rows, method_id)
            graphs[graph_id] = {
                "graph_id": graph_id,
                "source": "bmc13_backbone_edges",
                "method_id": method_id,
                "rows": rows,
            }

    return graphs


def nodes_from_edges(rows: Sequence[Dict[str, Any]]) -> List[str]:
    return sorted({str(r["source"]) for r in rows} | {str(r["target"]) for r in rows})


def weighted_adjacency(rows: Sequence[Dict[str, Any]], eps: float) -> Dict[str, Dict[str, float]]:
    adj: Dict[str, Dict[str, float]] = defaultdict(dict)
    for r in rows:
        a = str(r["source"])
        b = str(r["target"])
        d = proxy_distance(as_float(r["weight"], "weight"), eps)
        adj[a][b] = min(adj[a].get(b, float("inf")), d)
        adj[b][a] = min(adj[b].get(a, float("inf")), d)
    return adj


def edge_distance_map(rows: Sequence[Dict[str, Any]], eps: float) -> Dict[Edge, float]:
    out: Dict[Edge, float] = {}
    for r in rows:
        e = edge_key(r)
        d = proxy_distance(as_float(r["weight"], "weight"), eps)
        out[e] = min(out.get(e, float("inf")), d)
    return out


def graph_components(rows: Sequence[Dict[str, Any]]) -> Tuple[int, int, int, List[Set[str]]]:
    nodes = nodes_from_edges(rows)
    if not nodes:
        return 0, 0, 0, []
    adj: Dict[str, Set[str]] = {n: set() for n in nodes}
    for r in rows:
        a = str(r["source"])
        b = str(r["target"])
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)

    seen: Set[str] = set()
    comps: List[Set[str]] = []
    for start in nodes:
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
        comp: Set[str] = set()
        while q:
            cur = q.popleft()
            comp.add(cur)
            for nxt in adj.get(cur, set()):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        comps.append(comp)
    sizes = [len(c) for c in comps]
    return len(nodes), len(comps), max(sizes) if sizes else 0, comps


def graph_inventory_row(graph: Dict[str, Any], eps: float) -> Dict[str, Any]:
    rows = graph["rows"]
    weights = [as_float(r["weight"], "weight") for r in rows]
    dists = [proxy_distance(w, eps) for w in weights]
    node_count, comp_count, largest, _ = graph_components(rows)
    return {
        "graph_id": graph["graph_id"],
        "source": graph["source"],
        "method_id": graph["method_id"],
        "edge_count": len(rows),
        "node_count": node_count,
        "component_count": comp_count,
        "largest_component_size": largest,
        "mean_weight": mean(weights) if weights else 0.0,
        "min_weight": min(weights) if weights else 0.0,
        "max_weight": max(weights) if weights else 0.0,
        "mean_proxy_distance": mean(dists) if dists else 0.0,
        "min_proxy_distance": min(dists) if dists else 0.0,
        "max_proxy_distance": max(dists) if dists else 0.0,
    }


def triangle_edge_only(graph_id: str, rows: Sequence[Dict[str, Any]], eps: float, tol: float) -> Dict[str, Any]:
    nodes = nodes_from_edges(rows)
    dmap = edge_distance_map(rows, eps)
    triangle_count = 0
    violations: List[float] = []
    rel_violations: List[float] = []

    for a, b, c in combinations(nodes, 3):
        e_ab, e_ac, e_bc = norm_edge(a, b), norm_edge(a, c), norm_edge(b, c)
        if e_ab not in dmap or e_ac not in dmap or e_bc not in dmap:
            continue
        ds = [(dmap[e_ab], dmap[e_ac], dmap[e_bc])]
        triangle_count += 1
        vals = [dmap[e_ab], dmap[e_ac], dmap[e_bc]]
        # test all three triangle inequalities
        for i in range(3):
            x = vals[i]
            y = vals[(i + 1) % 3]
            z = vals[(i + 2) % 3]
            diff = x - y - z
            if diff > tol:
                violations.append(diff)
                rel_violations.append(diff / max(x, tol))

    return {
        "graph_id": graph_id,
        "triangle_mode": "edge_only",
        "node_count": len(nodes),
        "triangle_count": triangle_count,
        "violation_count": len(violations),
        "violation_fraction": len(violations) / (triangle_count * 3) if triangle_count else 0.0,
        "mean_violation": mean(violations) if violations else 0.0,
        "max_violation": max(violations) if violations else 0.0,
        "mean_relative_violation": mean(rel_violations) if rel_violations else 0.0,
        "max_relative_violation": max(rel_violations) if rel_violations else 0.0,
    }


def dijkstra_all_pairs(rows: Sequence[Dict[str, Any]], eps: float) -> Tuple[List[str], Dict[Tuple[str, str], float]]:
    nodes = nodes_from_edges(rows)
    adj = weighted_adjacency(rows, eps)
    result: Dict[Tuple[str, str], float] = {}

    for start in nodes:
        unvisited = set(nodes)
        dist = {n: float("inf") for n in nodes}
        dist[start] = 0.0
        while unvisited:
            cur = min(unvisited, key=lambda n: dist[n])
            if not math.isfinite(dist[cur]):
                break
            unvisited.remove(cur)
            for nxt, w in adj.get(cur, {}).items():
                if nxt in unvisited:
                    nd = dist[cur] + w
                    if nd < dist[nxt]:
                        dist[nxt] = nd
        for n in nodes:
            result[(start, n)] = dist[n]
    return nodes, result


def triangle_shortest_path(graph_id: str, rows: Sequence[Dict[str, Any]], eps: float, tol: float) -> Dict[str, Any]:
    nodes, dist = dijkstra_all_pairs(rows, eps)
    triangle_count = 0
    violations: List[float] = []
    rel_violations: List[float] = []

    for a, b, c in combinations(nodes, 3):
        vals = [dist[(a, b)], dist[(a, c)], dist[(b, c)]]
        if any(not math.isfinite(x) for x in vals):
            continue
        triangle_count += 1
        for i in range(3):
            x = vals[i]
            y = vals[(i + 1) % 3]
            z = vals[(i + 2) % 3]
            diff = x - y - z
            if diff > tol:
                violations.append(diff)
                rel_violations.append(diff / max(x, tol))

    return {
        "graph_id": graph_id,
        "triangle_mode": "shortest_path_completed",
        "node_count": len(nodes),
        "triangle_count": triangle_count,
        "violation_count": len(violations),
        "violation_fraction": len(violations) / (triangle_count * 3) if triangle_count else 0.0,
        "mean_violation": mean(violations) if violations else 0.0,
        "max_violation": max(violations) if violations else 0.0,
        "mean_relative_violation": mean(rel_violations) if rel_violations else 0.0,
        "max_relative_violation": max(rel_violations) if rel_violations else 0.0,
    }


def largest_component_rows(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    _, _, _, comps = graph_components(rows)
    if not comps:
        return []
    largest = max(comps, key=len)
    return [r for r in rows if str(r["source"]) in largest and str(r["target"]) in largest]


def distance_matrix_from_shortest_paths(rows: Sequence[Dict[str, Any]], eps: float) -> Tuple[List[str], np.ndarray]:
    nodes, dist = dijkstra_all_pairs(rows, eps)
    n = len(nodes)
    D = np.zeros((n, n), dtype=float)
    finite_vals: List[float] = []
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            d = dist[(a, b)]
            if math.isfinite(d):
                D[i, j] = d
                if i != j:
                    finite_vals.append(d)
            else:
                D[i, j] = np.nan
    if np.isnan(D).any():
        fill = max(finite_vals) * 2.0 if finite_vals else 1.0
        D = np.nan_to_num(D, nan=fill, posinf=fill, neginf=0.0)
    return nodes, D


def classical_mds_embedding_summary(graph_id: str, rows: Sequence[Dict[str, Any]], eps: float, dims: Sequence[int], use_largest: bool) -> List[Dict[str, Any]]:
    rows_used = largest_component_rows(rows) if use_largest else list(rows)
    if not rows_used:
        return []

    nodes, D = distance_matrix_from_shortest_paths(rows_used, eps)
    n = len(nodes)
    if n < 2:
        return []

    J = np.eye(n) - np.ones((n, n)) / n
    B = -0.5 * J @ (D ** 2) @ J
    eigvals, eigvecs = np.linalg.eigh(B)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]

    pos_vals = eigvals[eigvals > 1e-12]
    neg_vals = eigvals[eigvals < -1e-12]
    pos_sum = float(pos_vals.sum()) if len(pos_vals) else 0.0
    neg_abs_sum = float(np.abs(neg_vals).sum()) if len(neg_vals) else 0.0
    neg_ratio = neg_abs_sum / pos_sum if pos_sum > 0 else 0.0

    out: List[Dict[str, Any]] = []
    denom = float(np.sum(D ** 2))
    for dim in dims:
        k = min(int(dim), len(pos_vals), n)
        if k <= 0:
            stress_raw = float("nan")
            stress_norm = float("nan")
        else:
            vals = np.maximum(eigvals[:k], 0.0)
            coords = eigvecs[:, :k] * np.sqrt(vals)
            Dhat = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2))
            diff = D - Dhat
            stress_raw = float(math.sqrt(np.sum(diff ** 2)))
            stress_norm = float(math.sqrt(np.sum(diff ** 2) / denom)) if denom > 0 else 0.0

        out.append({
            "graph_id": graph_id,
            "distance_mode": "shortest_path_largest_component" if use_largest else "shortest_path_all_nodes",
            "embedding_dimension": dim,
            "node_count": n,
            "stress_raw": stress_raw,
            "stress_normalized": stress_norm,
            "positive_eigenvalue_count": int(len(pos_vals)),
            "negative_eigenvalue_count": int(len(neg_vals)),
            "negative_eigenvalue_fraction": int(len(neg_vals)) / n if n else 0.0,
            "positive_eigenvalue_sum": pos_sum,
            "negative_eigenvalue_abs_sum": neg_abs_sum,
            "negative_to_positive_abs_ratio": neg_ratio,
        })
    return out


def geodesic_consistency(
    graph_id: str,
    envelope_rows: Sequence[Dict[str, Any]],
    reference_graph_id: str,
    reference_rows: Sequence[Dict[str, Any]],
    eps: float,
) -> Dict[str, Any]:
    ref_dmap = edge_distance_map(reference_rows, eps)
    _, path_dist = dijkstra_all_pairs(envelope_rows, eps)

    pair_count = 0
    reachable = 0
    ratios: List[float] = []
    diffs: List[float] = []

    for (a, b), d_direct in ref_dmap.items():
        pair_count += 1
        d_path = path_dist.get((a, b), float("inf"))
        if math.isfinite(d_path):
            reachable += 1
            ratios.append(d_path / d_direct if d_direct > 0 else 1.0)
            diffs.append(d_path - d_direct)

    unreachable = pair_count - reachable
    return {
        "graph_id": graph_id,
        "direct_reference_graph_id": reference_graph_id,
        "pair_count": pair_count,
        "reachable_pair_count": reachable,
        "unreachable_pair_count": unreachable,
        "unreachable_pair_fraction": unreachable / pair_count if pair_count else 0.0,
        "mean_path_direct_ratio": mean(ratios) if ratios else 0.0,
        "median_path_direct_ratio": median(ratios) if ratios else 0.0,
        "max_path_direct_ratio": max(ratios) if ratios else 0.0,
        "mean_path_minus_direct": mean(diffs) if diffs else 0.0,
        "max_path_minus_direct": max(diffs) if diffs else 0.0,
    }


def core_nodes_from_rows(rows: Sequence[Dict[str, Any]]) -> Set[str]:
    return set(nodes_from_edges(rows))


def unweighted_shells(rows: Sequence[Dict[str, Any]], seed_nodes: Set[str]) -> Dict[str, int]:
    nodes = nodes_from_edges(rows)
    adj: Dict[str, Set[str]] = {n: set() for n in nodes}
    for r in rows:
        a = str(r["source"])
        b = str(r["target"])
        adj[a].add(b)
        adj[b].add(a)

    dist: Dict[str, int] = {n: 10**9 for n in nodes}
    q = deque()
    for n in seed_nodes:
        if n in dist:
            dist[n] = 0
            q.append(n)

    while q:
        cur = q.popleft()
        for nxt in adj.get(cur, set()):
            if dist[nxt] > dist[cur] + 1:
                dist[nxt] = dist[cur] + 1
                q.append(nxt)
    return dist


def induced_edge_count(rows: Sequence[Dict[str, Any]], node_subset: Set[str]) -> int:
    return sum(1 for r in rows if str(r["source"]) in node_subset and str(r["target"]) in node_subset)


def induced_components(rows: Sequence[Dict[str, Any]], node_subset: Set[str]) -> Tuple[int, int]:
    sub_edges = [r for r in rows if str(r["source"]) in node_subset and str(r["target"]) in node_subset]
    if not node_subset:
        return 0, 0
    adj: Dict[str, Set[str]] = {n: set() for n in node_subset}
    for r in sub_edges:
        a = str(r["source"])
        b = str(r["target"])
        adj[a].add(b)
        adj[b].add(a)
    seen: Set[str] = set()
    sizes: List[int] = []
    for start in sorted(node_subset):
        if start in seen:
            continue
        q = deque([start])
        seen.add(start)
        size = 0
        while q:
            cur = q.popleft()
            size += 1
            for nxt in adj.get(cur, set()):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        sizes.append(size)
    return len(sizes), max(sizes) if sizes else 0


def shell_growth_rows(graph_id: str, rows: Sequence[Dict[str, Any]], seed_nodes: Set[str]) -> List[Dict[str, Any]]:
    dist = unweighted_shells(rows, seed_nodes)
    finite_shells = sorted({d for d in dist.values() if d < 10**9})
    out: List[Dict[str, Any]] = []
    reached: Set[str] = set()
    prev_reached: Set[str] = set()

    for shell in finite_shells:
        shell_nodes = {n for n, d in dist.items() if d == shell}
        reached |= shell_nodes
        crossing = 0
        if shell > 0:
            for r in rows:
                a = str(r["source"])
                b = str(r["target"])
                if (a in prev_reached and b in shell_nodes) or (b in prev_reached and a in shell_nodes):
                    crossing += 1
        comp_count, largest = induced_components(rows, reached)
        out.append({
            "graph_id": graph_id,
            "center_mode": "core_node_set",
            "shell_index": shell,
            "new_nodes": len(shell_nodes),
            "cumulative_nodes": len(reached),
            "new_edges_crossing_shell": crossing,
            "cumulative_edges_induced": induced_edge_count(rows, reached),
            "component_count_induced": comp_count,
            "largest_component_size_induced": largest,
        })
        prev_reached = set(reached)
    return out


def local_dimension_proxy(graph_id: str, shell_rows: Sequence[Dict[str, Any]], min_fit_points: int) -> Dict[str, Any]:
    pts = []
    for r in shell_rows:
        shell = int(r["shell_index"])
        cum = int(r["cumulative_nodes"])
        if shell > 0 and cum > 1:
            pts.append((math.log(shell), math.log(cum)))
    if len(pts) < min_fit_points:
        return {
            "graph_id": graph_id,
            "center_mode": "core_node_set",
            "radius_type": "hop",
            "fit_points": len(pts),
            "effective_dimension_proxy": 0.0,
            "fit_r2": 0.0,
            "interpretation_label": "insufficient_points",
        }

    xs = np.array([p[0] for p in pts], dtype=float)
    ys = np.array([p[1] for p in pts], dtype=float)
    A = np.vstack([xs, np.ones(len(xs))]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    pred = slope * xs + intercept
    ss_res = float(np.sum((ys - pred) ** 2))
    ss_tot = float(np.sum((ys - ys.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    label = "stable_proxy" if r2 >= 0.8 else "weak_proxy"
    return {
        "graph_id": graph_id,
        "center_mode": "core_node_set",
        "radius_type": "hop",
        "fit_points": len(pts),
        "effective_dimension_proxy": float(slope),
        "fit_r2": r2,
        "interpretation_label": label,
    }


def write_readout(path: Path, inventory: Sequence[Dict[str, Any]], triangle_rows: Sequence[Dict[str, Any]], embedding_rows: Sequence[Dict[str, Any]], dimension_rows: Sequence[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# BMC-15 Geometry-Proxy Diagnostics Readout")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append("- mode: observed geometry-proxy baseline")
    lines.append("- physical interpretation: none")
    lines.append("")
    lines.append("## Graph inventory")
    lines.append("")
    lines.append("| graph_id | edges | nodes | components | largest_component | mean_weight | mean_proxy_distance |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for r in inventory:
        lines.append(
            "| {graph_id} | {edge_count} | {node_count} | {component_count} | {largest_component_size} | {mean_weight:.3f} | {mean_proxy_distance:.3f} |".format(**r)
        )
    lines.append("")
    lines.append("## Triangle defects")
    lines.append("")
    lines.append("| graph_id | mode | triangles | violation_fraction | max_violation |")
    lines.append("|---|---|---:|---:|---:|")
    for r in triangle_rows:
        lines.append(
            "| {graph_id} | {triangle_mode} | {triangle_count} | {violation_fraction:.3f} | {max_violation:.3g} |".format(**r)
        )
    lines.append("")
    lines.append("## Embedding stress")
    lines.append("")
    lines.append("| graph_id | dim | nodes | stress_normalized | negative_to_positive_abs_ratio |")
    lines.append("|---|---:|---:|---:|---:|")
    for r in embedding_rows:
        lines.append(
            "| {graph_id} | {embedding_dimension} | {node_count} | {stress_normalized:.3f} | {negative_to_positive_abs_ratio:.3f} |".format(**r)
        )
    lines.append("")
    lines.append("## Local dimension proxy")
    lines.append("")
    lines.append("| graph_id | fit_points | effective_dimension_proxy | fit_r2 | label |")
    lines.append("|---|---:|---:|---:|---|")
    for r in dimension_rows:
        lines.append(
            "| {graph_id} | {fit_points} | {effective_dimension_proxy:.3f} | {fit_r2:.3f} | {interpretation_label} |".format(**r)
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("BMC-15a reports geometry-like proxy diagnostics only. These values do not establish physical spacetime emergence, causal geometry, or continuum reconstruction.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMC-15 geometry-proxy diagnostics.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    cfg = load_yaml(project_path(root, args.config))

    inventory_path = project_path(root, cfg["inputs"]["edge_inventory_csv"])
    backbone_path = project_path(root, cfg["inputs"]["backbone_edges_csv"])
    output_root = project_path(root, cfg["outputs"]["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    edge_count = int(cfg["reference"]["edge_count_target"])
    case_id = str(cfg["reference"]["case_id"])
    core_method_id = str(cfg["reference"]["core_method_id"])

    eps = float(cfg["distance"].get("epsilon", 1e-12))
    tol = float(cfg["distance"].get("triangle_tolerance", 1e-12))
    include_graphs = list(cfg["graphs"]["include"])
    dims = list(cfg["embedding"].get("dimensions", [2, 3, 4]))
    use_largest = bool(cfg["embedding"].get("use_largest_component_only", True))
    min_fit_points = int(cfg["local_dimension"].get("min_fit_points", 3))

    inventory_rows_raw = read_csv(inventory_path)
    backbone_rows_raw = read_csv(backbone_path)
    graphs = build_graph_objects(inventory_rows_raw, backbone_rows_raw, edge_count, case_id, include_graphs)

    if "top_strength_reference_core" not in graphs:
        core_rows = filter_backbone_method(backbone_rows_raw, core_method_id)
    else:
        core_rows = graphs["top_strength_reference_core"]["rows"]
    seed_nodes = core_nodes_from_rows(core_rows)

    graph_inventory: List[Dict[str, Any]] = []
    triangle_rows: List[Dict[str, Any]] = []
    embedding_rows: List[Dict[str, Any]] = []
    geodesic_rows: List[Dict[str, Any]] = []
    shell_rows_all: List[Dict[str, Any]] = []
    dimension_rows: List[Dict[str, Any]] = []

    for graph_id, graph in graphs.items():
        rows = graph["rows"]
        graph_inventory.append(graph_inventory_row(graph, eps))

        if cfg["diagnostics"].get("triangle_defects", True):
            triangle_rows.append(triangle_edge_only(graph_id, rows, eps, tol))
            triangle_rows.append(triangle_shortest_path(graph_id, rows, eps, tol))

        if cfg["diagnostics"].get("embedding_stress", True):
            embedding_rows.extend(classical_mds_embedding_summary(graph_id, rows, eps, dims, use_largest))

        if cfg["diagnostics"].get("shell_growth", True):
            srows = shell_growth_rows(graph_id, rows, seed_nodes)
            shell_rows_all.extend(srows)
            if cfg["diagnostics"].get("local_dimension_proxy", True):
                dimension_rows.append(local_dimension_proxy(graph_id, srows, min_fit_points))

    if cfg["diagnostics"].get("geodesic_consistency", True) and "N81_full_baseline" in graphs:
        ref_graph = graphs["N81_full_baseline"]
        for graph_id, graph in graphs.items():
            if graph_id == "N81_full_baseline":
                continue
            geodesic_rows.append(geodesic_consistency(graph_id, graph["rows"], "N81_full_baseline", ref_graph["rows"], eps))

    graph_inventory_out = output_root / "bmc15_graph_inventory.csv"
    triangle_out = output_root / "bmc15_triangle_defect_summary.csv"
    embedding_out = output_root / "bmc15_embedding_summary.csv"
    geodesic_out = output_root / "bmc15_geodesic_consistency_summary.csv"
    shell_out = output_root / "bmc15_shell_growth_summary.csv"
    dim_out = output_root / "bmc15_local_dimension_proxy_summary.csv"
    readout_out = output_root / "bmc15_readout.md"
    metrics_out = output_root / "bmc15_metrics.json"

    write_csv(graph_inventory_out, graph_inventory, [
        "graph_id", "source", "method_id", "edge_count", "node_count", "component_count",
        "largest_component_size", "mean_weight", "min_weight", "max_weight",
        "mean_proxy_distance", "min_proxy_distance", "max_proxy_distance",
    ])
    write_csv(triangle_out, triangle_rows, [
        "graph_id", "triangle_mode", "node_count", "triangle_count", "violation_count",
        "violation_fraction", "mean_violation", "max_violation",
        "mean_relative_violation", "max_relative_violation",
    ])
    write_csv(embedding_out, embedding_rows, [
        "graph_id", "distance_mode", "embedding_dimension", "node_count", "stress_raw",
        "stress_normalized", "positive_eigenvalue_count", "negative_eigenvalue_count",
        "negative_eigenvalue_fraction", "positive_eigenvalue_sum",
        "negative_eigenvalue_abs_sum", "negative_to_positive_abs_ratio",
    ])
    write_csv(geodesic_out, geodesic_rows, [
        "graph_id", "direct_reference_graph_id", "pair_count", "reachable_pair_count",
        "unreachable_pair_count", "unreachable_pair_fraction", "mean_path_direct_ratio",
        "median_path_direct_ratio", "max_path_direct_ratio", "mean_path_minus_direct",
        "max_path_minus_direct",
    ])
    write_csv(shell_out, shell_rows_all, [
        "graph_id", "center_mode", "shell_index", "new_nodes", "cumulative_nodes",
        "new_edges_crossing_shell", "cumulative_edges_induced",
        "component_count_induced", "largest_component_size_induced",
    ])
    write_csv(dim_out, dimension_rows, [
        "graph_id", "center_mode", "radius_type", "fit_points", "effective_dimension_proxy",
        "fit_r2", "interpretation_label",
    ])

    write_readout(readout_out, graph_inventory, triangle_rows, embedding_rows, dimension_rows)

    metrics = {
        "run_id": cfg.get("run_id", "BMC15_geometry_proxy_diagnostics_open"),
        "mode": "observed_geometry_proxy_baseline",
        "edge_inventory_csv": str(inventory_path),
        "backbone_edges_csv": str(backbone_path),
        "output_root": str(output_root),
        "graph_count": len(graphs),
        "graphs": list(graphs.keys()),
        "core_seed_node_count": len(seed_nodes),
        "diagnostics": cfg["diagnostics"],
        "distance_proxy": cfg["distance"]["proxy"],
        "interpretation_warning": "Geometry-proxy diagnostics only; no physical spacetime claim.",
    }
    metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-15 geometry-proxy diagnostics completed.")
    print(f"Wrote: {graph_inventory_out}")
    print(f"Wrote: {triangle_out}")
    print(f"Wrote: {embedding_out}")
    print(f"Wrote: {geodesic_out}")
    print(f"Wrote: {shell_out}")
    print(f"Wrote: {dim_out}")
    print(f"Wrote: {readout_out}")
    print(f"Wrote: {metrics_out}")


if __name__ == "__main__":
    main()
