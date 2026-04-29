#!/usr/bin/env python3
"""
BMC-15b Geometry-Proxy Null Comparison Runner.

This runner regenerates null graphs using BMC-14d/14e-style null definitions,
computes BMC-15-style geometry proxies, and compares observed BMC-15a values
against null distributions.

No physical spacetime interpretation is inferred.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict, deque
from itertools import combinations
from pathlib import Path
from statistics import mean, median, pstdev, NormalDist
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


def edge_key(row: Dict[str, Any]) -> Edge:
    return norm_edge(str(row["source"]), str(row["target"]))


def proxy_distance(weight: float, eps: float) -> float:
    return -math.log(max(float(weight), eps))


def filter_inventory_rows(rows: Sequence[Dict[str, str]], edge_count: int, case_id: str) -> List[Dict[str, Any]]:
    out = [
        dict(r) for r in rows
        if as_int(r["edge_count_target"]) == edge_count and str(r["case_id"]) == case_id
    ]
    if not out:
        raise ValueError(f"No inventory rows for edge_count_target={edge_count}, case_id={case_id!r}")
    out.sort(key=lambda r: (-as_float(r["weight"], "weight"), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(out, start=1):
        row["edge_rank"] = rank
    return out


def filter_backbone_method(rows: Sequence[Dict[str, str]], method_id: str) -> List[Dict[str, Any]]:
    out = [dict(r) for r in rows if str(r.get("method_id")) == method_id]
    if not out:
        raise ValueError(f"No backbone rows for method_id={method_id!r}")
    out.sort(key=lambda r: (-as_float(r["weight"], "weight"), str(r["source"]), str(r["target"])))
    return out


def nodes_from_edges(rows: Sequence[Dict[str, Any]]) -> List[str]:
    return sorted({str(r["source"]) for r in rows} | {str(r["target"]) for r in rows})


def matrix_from_rows(rows: Sequence[Dict[str, Any]], feature_cols: Sequence[str]) -> np.ndarray:
    return np.array([[as_float(r[col], col) for col in feature_cols] for r in rows], dtype=float)


def rows_with_feature_matrix(template_rows: Sequence[Dict[str, Any]], feature_cols: Sequence[str], X: np.ndarray) -> List[Dict[str, Any]]:
    out = []
    for row, vals in zip(template_rows, X):
        nr = dict(row)
        for col, val in zip(feature_cols, vals):
            nr[col] = float(val)
        out.append(nr)
    return out


def nearest_psd_cov(cov: np.ndarray, ridge: float) -> np.ndarray:
    cov = np.array(cov, dtype=float)
    cov = (cov + cov.T) / 2.0
    return cov + np.eye(cov.shape[0]) * ridge


def clip_matrix_to_observed(Xn: np.ndarray, X: np.ndarray) -> np.ndarray:
    return np.minimum(np.maximum(Xn, X.min(axis=0)), X.max(axis=0))


def generate_global_covariance_rows(rows, feature_cols, seed, ridge, clip):
    rng = np.random.default_rng(seed)
    X = matrix_from_rows(rows, feature_cols)
    mu = X.mean(axis=0)
    cov = nearest_psd_cov(np.cov(X, rowvar=False, ddof=1), ridge)
    Xn = rng.multivariate_normal(mu, cov, size=X.shape[0])
    if clip:
        Xn = clip_matrix_to_observed(Xn, X)
    return rows_with_feature_matrix(rows, feature_cols, Xn), "ok"


def generate_family_covariance_rows(rows, feature_cols, family_col, seed, ridge, min_family_size, fallback, clip):
    rng = np.random.default_rng(seed)
    X_all = matrix_from_rows(rows, feature_cols)
    out = [dict(r) for r in rows]
    warnings = []
    idx_by_family = defaultdict(list)
    for idx, row in enumerate(rows):
        idx_by_family[str(row[family_col])].append(idx)

    for fam, idxs in sorted(idx_by_family.items()):
        X = np.array([[as_float(rows[i][col], col) for col in feature_cols] for i in idxs], dtype=float)
        mu = X.mean(axis=0)
        if len(idxs) >= min_family_size:
            cov = nearest_psd_cov(np.cov(X, rowvar=False, ddof=1), ridge)
        else:
            warnings.append(f"family={fam}:size={len(idxs)} fallback={fallback}")
            if fallback == "diagonal":
                var = np.var(X, axis=0, ddof=0)
                var[var <= 0] = ridge
                cov = np.diag(var + ridge)
            else:
                cov = nearest_psd_cov(np.cov(X_all, rowvar=False, ddof=1), ridge)
        Xn = rng.multivariate_normal(mu, cov, size=len(idxs))
        if clip:
            Xn = np.minimum(np.maximum(Xn, X.min(axis=0)), X.max(axis=0))
        for local_i, row_idx in enumerate(idxs):
            for col, val in zip(feature_cols, Xn[local_i]):
                out[row_idx][col] = float(val)

    return out, "; ".join(warnings) if warnings else "ok"


def rankdata_average(vals: Sequence[float]) -> np.ndarray:
    pairs = sorted((float(v), i) for i, v in enumerate(vals))
    ranks = np.zeros(len(vals), dtype=float)
    pos = 0
    while pos < len(pairs):
        end = pos + 1
        while end < len(pairs) and pairs[end][0] == pairs[pos][0]:
            end += 1
        avg_rank = (pos + 1 + end) / 2.0
        for _, idx in pairs[pos:end]:
            ranks[idx] = avg_rank
        pos = end
    return ranks


def empirical_quantile(sorted_vals: np.ndarray, u: float) -> float:
    if len(sorted_vals) == 1:
        return float(sorted_vals[0])
    u = min(max(float(u), 0.0), 1.0)
    pos = u * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return float(sorted_vals[lo])
    frac = pos - lo
    return float(sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac)


def nearest_psd_corr(corr: np.ndarray, ridge: float) -> np.ndarray:
    corr = np.array(corr, dtype=float)
    corr = (corr + corr.T) / 2.0
    corr += np.eye(corr.shape[0]) * ridge
    vals, vecs = np.linalg.eigh(corr)
    vals = np.maximum(vals, ridge)
    corr_psd = (vecs * vals) @ vecs.T
    d = np.sqrt(np.diag(corr_psd))
    corr_psd = corr_psd / np.outer(d, d)
    return (corr_psd + corr_psd.T) / 2.0


def generate_gaussian_copula_rows(rows, feature_cols, seed, ridge, clip):
    rng = np.random.default_rng(seed)
    nd = NormalDist()
    X = matrix_from_rows(rows, feature_cols)
    n, p = X.shape
    Z = np.zeros((n, p), dtype=float)
    sorted_cols = []
    for j in range(p):
        col = X[:, j]
        ranks = rankdata_average(col)
        u = np.clip((ranks - 0.5) / n, 1e-6, 1 - 1e-6)
        Z[:, j] = np.array([nd.inv_cdf(float(x)) for x in u])
        sorted_cols.append(np.sort(col))
    corr = nearest_psd_corr(np.corrcoef(Z, rowvar=False), ridge)
    Zn = rng.multivariate_normal(np.zeros(p), corr, size=n)
    Xn = np.zeros_like(Zn)
    for j in range(p):
        u = np.array([nd.cdf(float(z)) for z in Zn[:, j]])
        Xn[:, j] = np.array([empirical_quantile(sorted_cols[j], float(x)) for x in u])
    if clip:
        Xn = clip_matrix_to_observed(Xn, X)
    return rows_with_feature_matrix(rows, feature_cols, Xn), "ok"


def standardize_feature_rows(rows, feature_cols):
    means = {}
    stds = {}
    for col in feature_cols:
        vals = [as_float(r[col], col) for r in rows]
        mu = sum(vals) / len(vals)
        var = sum((x - mu) ** 2 for x in vals) / len(vals)
        means[col] = mu
        stds[col] = math.sqrt(var) if var > 0 else 1.0
    out = []
    for row in rows:
        nr = dict(row)
        for col in feature_cols:
            nr[f"z__{col}"] = (as_float(row[col], col) - means[col]) / stds[col]
        out.append(nr)
    return out


def build_edge_table(rows, id_col, feature_cols):
    z_rows = standardize_feature_rows(rows, feature_cols)
    edges = []
    for i in range(len(z_rows)):
        for j in range(i + 1, len(z_rows)):
            a = str(z_rows[i][id_col])
            b = str(z_rows[j][id_col])
            dist2 = sum((float(z_rows[i][f"z__{c}"]) - float(z_rows[j][f"z__{c}"])) ** 2 for c in feature_cols)
            dist = math.sqrt(dist2)
            w = 1.0 / (1.0 + dist)
            edges.append({"source": a, "target": b, "distance": dist, "weight": w})
    edges.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(edges, start=1):
        row["edge_rank"] = rank
    return edges


def select_top_n(edges, n):
    return [dict(e) for e in edges[:n]]


def select_top_strength(edges, k):
    return [dict(e) for e in sorted(edges, key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))[:k]]


def generate_weight_rank_rewire_edges(observed_edges, node_ids, seed):
    rng = random.Random(seed)
    weights = sorted([as_float(r["weight"], "weight") for r in observed_edges], reverse=True)
    all_pairs = [norm_edge(a, b) for i, a in enumerate(node_ids) for b in node_ids[i + 1:]]
    selected = rng.sample(all_pairs, len(weights))
    rows = [{"source": e[0], "target": e[1], "distance": "", "weight": w} for e, w in zip(selected, weights)]
    rows.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(rows, start=1):
        row["edge_rank"] = rank
    return rows, "ok"


def observed_degrees(edges):
    deg = Counter()
    for row in edges:
        deg[str(row["source"])] += 1
        deg[str(row["target"])] += 1
    return deg


def double_edge_rewire(observed_edges, seed, swap_multiplier, max_attempt_multiplier):
    rng = random.Random(seed)
    edges = {edge_key(r) for r in observed_edges}
    edge_list = list(edges)
    target_success = max(1, len(edge_list) * int(swap_multiplier))
    max_attempts = max(target_success, len(edge_list) * int(max_attempt_multiplier))
    successful = 0
    attempts = 0
    duplicate_or_self = 0
    while successful < target_success and attempts < max_attempts:
        attempts += 1
        e1, e2 = rng.sample(edge_list, 2)
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) < 4:
            duplicate_or_self += 1
            continue
        if rng.random() < 0.5:
            n1, n2 = norm_edge(a, d), norm_edge(c, b)
        else:
            n1, n2 = norm_edge(a, c), norm_edge(b, d)
        if n1[0] == n1[1] or n2[0] == n2[1] or n1 == n2 or n1 in edges or n2 in edges:
            duplicate_or_self += 1
            continue
        edges.remove(e1); edges.remove(e2); edges.add(n1); edges.add(n2)
        edge_list = list(edges)
        successful += 1
    return list(edges), {
        "attempted_swaps": attempts,
        "successful_swaps": successful,
        "failed_swaps": attempts - successful,
        "swap_success_fraction": successful / attempts if attempts else 0.0,
        "duplicate_or_self_loop_rejections": duplicate_or_self,
    }


def assign_weights_shuffled(edges, observed_edges, rng):
    weights = [as_float(r["weight"], "weight") for r in observed_edges]
    rng.shuffle(weights)
    rows = [{"source": e[0], "target": e[1], "distance": "", "weight": w} for e, w in zip(edges, weights)]
    rows.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(rows, start=1):
        row["edge_rank"] = rank
    return rows


def assign_weights_weightclass(edges, observed_edges, rng, classes):
    weights = sorted([as_float(r["weight"], "weight") for r in observed_edges], reverse=True)
    classes = max(1, int(classes))
    n = len(weights)
    blocks = []
    for c in range(classes):
        lo = int(round(c * n / classes))
        hi = int(round((c + 1) * n / classes))
        block = weights[lo:hi]
        rng.shuffle(block)
        blocks.append(block)
    shuffled = [w for block in blocks for w in block]
    rng.shuffle(shuffled)
    rows = [{"source": e[0], "target": e[1], "distance": "", "weight": w} for e, w in zip(edges, shuffled)]
    rows.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(rows, start=1):
        row["edge_rank"] = rank
    return rows


def generate_degree_rewire_edges(observed_edges, seed, swap_multiplier, max_attempt_multiplier, weight_assignment, weight_classes=4):
    rng = random.Random(seed + 991)
    rewired, diag = double_edge_rewire(observed_edges, seed, swap_multiplier, max_attempt_multiplier)
    if weight_assignment == "weightclass_shuffle":
        rows = assign_weights_weightclass(rewired, observed_edges, rng, weight_classes)
    else:
        rows = assign_weights_shuffled(rewired, observed_edges, rng)
    orig_deg = observed_degrees(observed_edges)
    new_deg = Counter()
    for e in rewired:
        new_deg[e[0]] += 1; new_deg[e[1]] += 1
    warning = ""
    if len(rewired) != len(observed_edges):
        warning += "edge_count_not_preserved;"
    if orig_deg != new_deg:
        warning += "degree_sequence_not_preserved;"
    return rows, warning if warning else "ok"


def select_mutual_knn(rows, k):
    neighbors = defaultdict(list)
    row_by_edge = {}
    ordered = sorted(rows, key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for row in ordered:
        a, b, w = str(row["source"]), str(row["target"]), float(row["weight"])
        neighbors[a].append((b, w)); neighbors[b].append((a, w))
        row_by_edge[norm_edge(a, b)] = dict(row)
    top_sets = {node: {n for n, _ in sorted(vals, key=lambda x: (-x[1], x[0]))[:k]} for node, vals in neighbors.items()}
    selected = set()
    for a, vals in top_sets.items():
        for b in vals:
            if b in top_sets and a in top_sets[b]:
                selected.add(norm_edge(a, b))
    return sorted([row_by_edge[e] for e in selected], key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))


def select_maximum_spanning_tree(rows):
    ordered = sorted(rows, key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    nodes = nodes_from_edges(ordered)
    parent = {n: n for n in nodes}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[rb] = ra
        return True
    selected = []
    for row in ordered:
        if union(str(row["source"]), str(row["target"])):
            selected.append(dict(row))
        if len(selected) == max(0, len(nodes) - 1):
            break
    return selected


def weighted_adjacency(rows, eps):
    adj = defaultdict(dict)
    for r in rows:
        a, b = str(r["source"]), str(r["target"])
        d = proxy_distance(as_float(r["weight"], "weight"), eps)
        adj[a][b] = min(adj[a].get(b, float("inf")), d)
        adj[b][a] = min(adj[b].get(a, float("inf")), d)
    return adj


def edge_distance_map(rows, eps):
    out = {}
    for r in rows:
        e = edge_key(r)
        d = proxy_distance(as_float(r["weight"], "weight"), eps)
        out[e] = min(out.get(e, float("inf")), d)
    return out


def graph_components(rows):
    nodes = nodes_from_edges(rows)
    if not nodes:
        return 0, 0, 0, []
    adj = {n: set() for n in nodes}
    for r in rows:
        a, b = str(r["source"]), str(r["target"])
        adj[a].add(b); adj[b].add(a)
    seen = set(); comps = []
    for start in nodes:
        if start in seen:
            continue
        q = deque([start]); seen.add(start); comp = set()
        while q:
            cur = q.popleft(); comp.add(cur)
            for nxt in adj.get(cur, set()):
                if nxt not in seen:
                    seen.add(nxt); q.append(nxt)
        comps.append(comp)
    sizes = [len(c) for c in comps]
    return len(nodes), len(comps), max(sizes) if sizes else 0, comps


def dijkstra_all_pairs(rows, eps):
    nodes = nodes_from_edges(rows)
    adj = weighted_adjacency(rows, eps)
    result = {}
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


def triangle_edge_only(graph_id, rows, eps, tol):
    nodes = nodes_from_edges(rows)
    dmap = edge_distance_map(rows, eps)
    triangle_count = 0
    violations = []
    for a, b, c in combinations(nodes, 3):
        keys = [norm_edge(a, b), norm_edge(a, c), norm_edge(b, c)]
        if not all(k in dmap for k in keys):
            continue
        triangle_count += 1
        vals = [dmap[k] for k in keys]
        for i in range(3):
            diff = vals[i] - vals[(i + 1) % 3] - vals[(i + 2) % 3]
            if diff > tol:
                violations.append(diff)
    return {
        "graph_id": graph_id, "triangle_mode": "edge_only",
        "node_count": len(nodes), "triangle_count": triangle_count,
        "violation_count": len(violations),
        "violation_fraction": len(violations) / (triangle_count * 3) if triangle_count else 0.0,
        "mean_violation": mean(violations) if violations else 0.0,
        "max_violation": max(violations) if violations else 0.0,
    }


def triangle_shortest_path(graph_id, rows, eps, tol):
    nodes, dist = dijkstra_all_pairs(rows, eps)
    triangle_count = 0
    violations = []
    for a, b, c in combinations(nodes, 3):
        vals = [dist[(a, b)], dist[(a, c)], dist[(b, c)]]
        if any(not math.isfinite(x) for x in vals):
            continue
        triangle_count += 1
        for i in range(3):
            diff = vals[i] - vals[(i + 1) % 3] - vals[(i + 2) % 3]
            if diff > tol:
                violations.append(diff)
    return {
        "graph_id": graph_id, "triangle_mode": "shortest_path_completed",
        "node_count": len(nodes), "triangle_count": triangle_count,
        "violation_count": len(violations),
        "violation_fraction": len(violations) / (triangle_count * 3) if triangle_count else 0.0,
        "mean_violation": mean(violations) if violations else 0.0,
        "max_violation": max(violations) if violations else 0.0,
    }


def largest_component_rows(rows):
    _, _, _, comps = graph_components(rows)
    if not comps:
        return []
    largest = max(comps, key=len)
    return [r for r in rows if str(r["source"]) in largest and str(r["target"]) in largest]


def distance_matrix_from_shortest_paths(rows, eps):
    nodes, dist = dijkstra_all_pairs(rows, eps)
    n = len(nodes)
    D = np.zeros((n, n), dtype=float)
    finite = []
    for i, a in enumerate(nodes):
        for j, b in enumerate(nodes):
            d = dist[(a, b)]
            if math.isfinite(d):
                D[i, j] = d
                if i != j:
                    finite.append(d)
            else:
                D[i, j] = np.nan
    if np.isnan(D).any():
        fill = max(finite) * 2.0 if finite else 1.0
        D = np.nan_to_num(D, nan=fill, posinf=fill, neginf=0.0)
    return nodes, D


def embedding_summaries(graph_id, rows, eps, dims, use_largest):
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
    eigvals, eigvecs = eigvals[idx], eigvecs[:, idx]
    pos_vals = eigvals[eigvals > 1e-12]
    neg_vals = eigvals[eigvals < -1e-12]
    pos_sum = float(pos_vals.sum()) if len(pos_vals) else 0.0
    neg_abs_sum = float(np.abs(neg_vals).sum()) if len(neg_vals) else 0.0
    neg_ratio = neg_abs_sum / pos_sum if pos_sum > 0 else 0.0
    denom = float(np.sum(D ** 2))
    out = []
    for dim in dims:
        k = min(int(dim), len(pos_vals), n)
        if k <= 0:
            stress_norm = 0.0
        else:
            vals = np.maximum(eigvals[:k], 0.0)
            coords = eigvecs[:, :k] * np.sqrt(vals)
            Dhat = np.sqrt(((coords[:, None, :] - coords[None, :, :]) ** 2).sum(axis=2))
            stress_norm = float(math.sqrt(np.sum((D - Dhat) ** 2) / denom)) if denom > 0 else 0.0
        out.append({
            "graph_id": graph_id,
            "embedding_dimension": dim,
            "node_count": n,
            "stress_normalized": stress_norm,
            "negative_to_positive_abs_ratio": neg_ratio,
            "negative_eigenvalue_fraction": len(neg_vals) / n if n else 0.0,
        })
    return out


def geodesic_consistency(graph_id, envelope_rows, reference_rows, eps):
    ref_dmap = edge_distance_map(reference_rows, eps)
    _, path_dist = dijkstra_all_pairs(envelope_rows, eps)
    pair_count = 0; reachable = 0; ratios = []; diffs = []
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


def core_nodes(rows):
    return set(nodes_from_edges(rows))


def shell_distances(rows, seed_nodes):
    nodes = nodes_from_edges(rows)
    adj = {n: set() for n in nodes}
    for r in rows:
        a, b = str(r["source"]), str(r["target"])
        adj[a].add(b); adj[b].add(a)
    dist = {n: 10**9 for n in nodes}
    q = deque()
    for n in seed_nodes:
        if n in dist:
            dist[n] = 0; q.append(n)
    while q:
        cur = q.popleft()
        for nxt in adj.get(cur, set()):
            if dist[nxt] > dist[cur] + 1:
                dist[nxt] = dist[cur] + 1; q.append(nxt)
    return dist


def local_dimension(graph_id, rows, seed_nodes, min_fit_points):
    dist = shell_distances(rows, seed_nodes)
    shells = sorted({d for d in dist.values() if d < 10**9})
    pts = []
    for shell in shells:
        if shell <= 0:
            continue
        cum = sum(1 for d in dist.values() if d <= shell)
        if cum > 1:
            pts.append((math.log(shell), math.log(cum)))
    if len(pts) < min_fit_points:
        return {"graph_id": graph_id, "fit_points": len(pts), "effective_dimension_proxy": 0.0, "fit_r2": 0.0, "interpretation_label": "insufficient_points"}
    xs = np.array([p[0] for p in pts]); ys = np.array([p[1] for p in pts])
    A = np.vstack([xs, np.ones(len(xs))]).T
    slope, intercept = np.linalg.lstsq(A, ys, rcond=None)[0]
    pred = slope * xs + intercept
    ss_res = float(np.sum((ys - pred) ** 2)); ss_tot = float(np.sum((ys - ys.mean()) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"graph_id": graph_id, "fit_points": len(pts), "effective_dimension_proxy": float(slope), "fit_r2": r2, "interpretation_label": "stable_proxy" if r2 >= 0.8 else "weak_proxy"}


def graph_inventory_row(graph_id, rows, eps):
    weights = [as_float(r["weight"], "weight") for r in rows]
    dists = [proxy_distance(w, eps) for w in weights]
    node_count, comp_count, largest, _ = graph_components(rows)
    return {
        "graph_id": graph_id, "edge_count": len(rows), "node_count": node_count,
        "component_count": comp_count, "largest_component_size": largest,
        "mean_weight": mean(weights) if weights else 0.0,
        "mean_proxy_distance": mean(dists) if dists else 0.0,
    }


def null_graphs_from_top_edges(top_edges, core_k, knn_k):
    return {
        "null_N81_full": list(top_edges),
        "null_top_strength_core": select_top_strength(top_edges, core_k),
        "null_maximum_spanning_tree": select_maximum_spanning_tree(top_edges),
        "null_mutual_kNN_k3": select_mutual_knn(top_edges, knn_k),
    }


def quantile(vals, q):
    xs = sorted(float(v) for v in vals)
    if not xs:
        return 0.0
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def p_lower(vals, obs):
    return (1 + sum(1 for x in vals if x <= obs)) / (len(vals) + 1)


def p_upper(vals, obs):
    return (1 + sum(1 for x in vals if x >= obs)) / (len(vals) + 1)


def observed_quantile(vals, obs):
    return sum(1 for x in vals if x <= obs) / len(vals) if vals else 0.0


def direction_label(metric):
    lower = {"violation_fraction", "max_violation", "stress_normalized", "negative_to_positive_abs_ratio", "negative_eigenvalue_fraction", "unreachable_pair_fraction"}
    higher = {"fit_r2"}
    closer = {"mean_path_direct_ratio", "median_path_direct_ratio"}
    if metric in lower:
        return "lower_better"
    if metric in higher:
        return "higher_better"
    if metric in closer:
        return "closer_to_one"
    return "not_directional"


def interpretation_label(metric, obs, vals):
    if not vals:
        return "insufficient_null_support"
    d = direction_label(metric)
    qpos = observed_quantile(vals, obs)
    if d == "lower_better":
        return "observed_more_geometry_like_than_null" if qpos <= 0.10 else ("observed_less_geometry_like_than_null" if qpos >= 0.90 else "observed_null_typical")
    if d == "higher_better":
        return "observed_more_geometry_like_than_null" if qpos >= 0.90 else ("observed_less_geometry_like_than_null" if qpos <= 0.10 else "observed_null_typical")
    if d == "closer_to_one":
        null_dev = [abs(x - 1.0) for x in vals]
        obs_dev = abs(obs - 1.0)
        qdev = observed_quantile(null_dev, obs_dev)
        return "observed_more_geometry_like_than_null" if qdev <= 0.10 else ("observed_less_geometry_like_than_null" if qdev >= 0.90 else "observed_null_typical")
    return "not_directional"


def summarize_distribution(null_model_id, graph_id, null_graph_id, metric_group, metric, observed_value, vals):
    vals = [float(v) for v in vals]
    return {
        "null_model_id": null_model_id,
        "graph_id": graph_id,
        "null_graph_id": null_graph_id,
        "metric_group": metric_group,
        "metric": metric,
        "metric_direction": direction_label(metric),
        "replicate_count": len(vals),
        "observed_value": observed_value,
        "null_mean": mean(vals) if vals else 0.0,
        "null_std": pstdev(vals) if len(vals) > 1 else 0.0,
        "null_min": min(vals) if vals else 0.0,
        "null_q05": quantile(vals, 0.05),
        "null_median": median(vals) if vals else 0.0,
        "null_q95": quantile(vals, 0.95),
        "null_max": max(vals) if vals else 0.0,
        "p_like_lower_tail": p_lower(vals, observed_value) if vals else 0.0,
        "p_like_upper_tail": p_upper(vals, observed_value) if vals else 0.0,
        "observed_quantile_position": observed_quantile(vals, observed_value),
        "interpretation_label": interpretation_label(metric, observed_value, vals),
    }


def load_observed_metric_tables(cfg, root):
    return {
        "triangle": read_csv(project_path(root, cfg["inputs"]["observed_bmc15_triangle_csv"])),
        "embedding": read_csv(project_path(root, cfg["inputs"]["observed_bmc15_embedding_csv"])),
        "geodesic": read_csv(project_path(root, cfg["inputs"]["observed_bmc15_geodesic_csv"])),
        "dimension": read_csv(project_path(root, cfg["inputs"]["observed_bmc15_dimension_csv"])),
    }


OBS_MAP = {
    "null_N81_full": "N81_full_baseline",
    "null_top_strength_core": "top_strength_reference_core",
    "null_maximum_spanning_tree": "maximum_spanning_tree_envelope",
    "null_mutual_kNN_k3": "mutual_kNN_k3_envelope",
}


def find_observed_value(obs_tables, null_graph_id, metric_group, metric, extra=None):
    graph_id = OBS_MAP[null_graph_id]
    rows = obs_tables[metric_group]
    for r in rows:
        if r.get("graph_id") != graph_id:
            continue
        if metric_group == "triangle":
            if r.get("triangle_mode") != extra:
                continue
        if metric_group == "embedding":
            if int(float(r.get("embedding_dimension"))) != int(extra):
                continue
        return as_float(r[metric], metric)
    return None


def write_readout(path, dist_rows, replicate_count):
    lines = []
    lines.append("# BMC-15b Geometry-Proxy Null Comparison Readout")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- replicates per null model: `{replicate_count}`")
    lines.append("- mode: geometry-proxy null comparison")
    lines.append("- physical interpretation: none")
    lines.append("")
    lines.append("## Selected observed-vs-null distribution results")
    lines.append("")
    lines.append("| null_model_id | graph_id | metric | observed | null_median | null_q05 | null_q95 | label |")
    lines.append("|---|---|---|---:|---:|---:|---:|---|")
    keep_metrics = {"stress_normalized", "negative_to_positive_abs_ratio", "violation_fraction", "fit_r2", "effective_dimension_proxy", "unreachable_pair_fraction", "mean_path_direct_ratio"}
    for r in dist_rows:
        if r["metric"] not in keep_metrics:
            continue
        lines.append(
            "| {null_model_id} | {graph_id} | {metric} | {observed_value:.3f} | {null_median:.3f} | {null_q05:.3f} | {null_q95:.3f} | {interpretation_label} |".format(**r)
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("BMC-15b compares observed geometry-proxy diagnostics against regenerated null graphs. These values remain methodological proxies only and do not establish physical spacetime emergence.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Run BMC-15b geometry-proxy null comparison.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    root = Path.cwd()
    cfg = load_yaml(project_path(root, args.config))

    output_root = project_path(root, cfg["outputs"]["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    feature_rows = read_csv(project_path(root, cfg["inputs"]["feature_table_csv"]))
    inventory_rows = read_csv(project_path(root, cfg["inputs"]["observed_edge_inventory_csv"]))
    observed_edges = filter_inventory_rows(inventory_rows, int(cfg["reference"]["edge_count_target"]), str(cfg["reference"]["case_id"]))
    obs_tables = load_observed_metric_tables(cfg, root)

    id_col = cfg["features"]["id_column"]
    family_col = cfg["features"]["family_column"]
    feature_cols = list(cfg["features"]["feature_columns"])
    node_ids = [str(r[id_col]) for r in feature_rows]
    eps = float(cfg["distance"]["epsilon"])
    tol = float(cfg["distance"]["triangle_tolerance"])
    reps = int(cfg["replicates"]["count"])
    seed_base = int(cfg["replicates"]["random_seed_base"])
    edge_count = int(cfg["reference"]["edge_count_target"])
    core_k = int(cfg["reference"]["core_edge_count"])
    knn_k = int(cfg["methods"]["mutual_knn"]["k"])
    dims = list(cfg["embedding"]["dimensions"])
    use_largest = bool(cfg["embedding"]["use_largest_component_only"])
    min_fit_points = int(cfg["local_dimension"]["min_fit_points"])

    null_model_specs = cfg["null_models"]
    null_models = []
    for name, fam in [
        ("global_covariance_gaussian", "feature_covariance"),
        ("family_covariance_gaussian", "feature_covariance"),
        ("weight_rank_edge_rewire", "edge_structured"),
        ("degree_preserving_edge_rewire", "degree_structured"),
        ("degree_weightclass_edge_rewire", "degree_structured"),
        ("gaussian_copula_feature_null", "copula_feature"),
    ]:
        if null_model_specs[name].get("enabled", True):
            null_models.append((name, fam))

    inv_rows = []
    tri_rows = []
    emb_rows = []
    geo_rows = []
    dim_rows = []

    for model_index, (model, family) in enumerate(null_models):
        spec = null_model_specs[model]
        for rep in range(reps):
            seed = seed_base + model_index * 1000000 + rep
            warning = "ok"

            if model == "global_covariance_gaussian":
                nrows, warning = generate_global_covariance_rows(feature_rows, feature_cols, seed, float(spec.get("ridge", 1e-9)), bool(spec.get("clip_to_observed_minmax", True)))
                top_edges = select_top_n(build_edge_table(nrows, id_col, feature_cols), edge_count)
            elif model == "family_covariance_gaussian":
                nrows, warning = generate_family_covariance_rows(feature_rows, feature_cols, family_col, seed, float(spec.get("ridge", 1e-6)), int(spec.get("min_family_size_for_covariance", 5)), str(spec.get("fallback", "diagonal")), bool(spec.get("clip_to_observed_minmax", True)))
                top_edges = select_top_n(build_edge_table(nrows, id_col, feature_cols), edge_count)
            elif model == "gaussian_copula_feature_null":
                nrows, warning = generate_gaussian_copula_rows(feature_rows, feature_cols, seed, float(spec.get("ridge", 1e-9)), bool(spec.get("clip_to_observed_minmax", True)))
                top_edges = select_top_n(build_edge_table(nrows, id_col, feature_cols), edge_count)
            elif model == "weight_rank_edge_rewire":
                top_edges, warning = generate_weight_rank_rewire_edges(observed_edges, node_ids, seed)
            elif model in ("degree_preserving_edge_rewire", "degree_weightclass_edge_rewire"):
                assignment = str(spec.get("weight_assignment", "shuffle_weights"))
                classes = int(spec.get("weight_classes", 4))
                top_edges, warning = generate_degree_rewire_edges(observed_edges, seed, int(spec.get("swap_multiplier", 20)), int(spec.get("max_attempt_multiplier", 200)), assignment, classes)
            else:
                raise ValueError(model)

            graphs = null_graphs_from_top_edges(top_edges, core_k, knn_k)
            seed_nodes = core_nodes(graphs["null_top_strength_core"])

            for graph_id, rows in graphs.items():
                inv = graph_inventory_row(graph_id, rows, eps)
                inv.update({"replicate_id": rep, "null_model_id": model, "null_family": family, "generation_status": "ok" if warning == "ok" else "warning"})
                inv_rows.append(inv)

                for tri in [triangle_edge_only(graph_id, rows, eps, tol), triangle_shortest_path(graph_id, rows, eps, tol)]:
                    tri.update({"replicate_id": rep, "null_model_id": model, "null_family": family, "generation_status": "ok" if warning == "ok" else "warning"})
                    tri_rows.append(tri)

                for emb in embedding_summaries(graph_id, rows, eps, dims, use_largest):
                    emb.update({"replicate_id": rep, "null_model_id": model, "null_family": family, "generation_status": "ok" if warning == "ok" else "warning"})
                    emb_rows.append(emb)

                dim = local_dimension(graph_id, rows, seed_nodes, min_fit_points)
                dim.update({"replicate_id": rep, "null_model_id": model, "null_family": family, "generation_status": "ok" if warning == "ok" else "warning"})
                dim_rows.append(dim)

            for graph_id in ["null_top_strength_core", "null_maximum_spanning_tree", "null_mutual_kNN_k3"]:
                geo = geodesic_consistency(graph_id, graphs[graph_id], graphs["null_N81_full"], eps)
                geo.update({"replicate_id": rep, "null_model_id": model, "null_family": family, "generation_status": "ok" if warning == "ok" else "warning"})
                geo_rows.append(geo)

    # Distribution summaries
    dist_rows = []

    # triangle: edge_only violation_fraction and max_violation primarily, also shortest_path included
    for model, family in null_models:
        for null_graph_id, obs_graph_id in OBS_MAP.items():
            for tri_mode in ["edge_only", "shortest_path_completed"]:
                for metric in ["violation_fraction", "max_violation"]:
                    vals = [float(r[metric]) for r in tri_rows if r["null_model_id"] == model and r["graph_id"] == null_graph_id and r["triangle_mode"] == tri_mode]
                    obs = find_observed_value(obs_tables, null_graph_id, "triangle", metric, tri_mode)
                    if obs is not None:
                        dist_rows.append(summarize_distribution(model, obs_graph_id, null_graph_id, "triangle", metric, obs, vals))

    # embedding metrics
    for model, family in null_models:
        for null_graph_id, obs_graph_id in OBS_MAP.items():
            for dim in dims:
                for metric in ["stress_normalized", "negative_to_positive_abs_ratio", "negative_eigenvalue_fraction"]:
                    vals = [float(r[metric]) for r in emb_rows if r["null_model_id"] == model and r["graph_id"] == null_graph_id and int(r["embedding_dimension"]) == int(dim)]
                    obs = find_observed_value(obs_tables, null_graph_id, "embedding", metric, dim)
                    if obs is not None:
                        row = summarize_distribution(model, obs_graph_id, null_graph_id, "embedding", metric, obs, vals)
                        row["embedding_dimension"] = dim
                        dist_rows.append(row)

    # geodesic metrics, skip N81_full and map envelope/core comparisons
    for model, family in null_models:
        for null_graph_id in ["null_top_strength_core", "null_maximum_spanning_tree", "null_mutual_kNN_k3"]:
            obs_graph_id = OBS_MAP[null_graph_id]
            for metric in ["unreachable_pair_fraction", "mean_path_direct_ratio", "median_path_direct_ratio", "max_path_direct_ratio"]:
                vals = [float(r[metric]) for r in geo_rows if r["null_model_id"] == model and r["graph_id"] == null_graph_id]
                obs = find_observed_value(obs_tables, null_graph_id, "geodesic", metric, None)
                if obs is not None:
                    dist_rows.append(summarize_distribution(model, obs_graph_id, null_graph_id, "geodesic", metric, obs, vals))

    # dimension metrics
    for model, family in null_models:
        for null_graph_id, obs_graph_id in OBS_MAP.items():
            for metric in ["effective_dimension_proxy", "fit_r2"]:
                vals = [float(r[metric]) for r in dim_rows if r["null_model_id"] == model and r["graph_id"] == null_graph_id]
                obs = find_observed_value(obs_tables, null_graph_id, "dimension", metric, None)
                if obs is not None:
                    dist_rows.append(summarize_distribution(model, obs_graph_id, null_graph_id, "dimension", metric, obs, vals))

    # write outputs
    write_csv(output_root / "bmc15b_null_graph_inventory.csv", inv_rows, [
        "replicate_id","null_model_id","null_family","graph_id","edge_count","node_count","component_count","largest_component_size","mean_weight","mean_proxy_distance","generation_status"
    ])
    write_csv(output_root / "bmc15b_null_triangle_summary.csv", tri_rows, [
        "replicate_id","null_model_id","null_family","graph_id","triangle_mode","node_count","triangle_count","violation_count","violation_fraction","mean_violation","max_violation","generation_status"
    ])
    write_csv(output_root / "bmc15b_null_embedding_summary.csv", emb_rows, [
        "replicate_id","null_model_id","null_family","graph_id","embedding_dimension","node_count","stress_normalized","negative_to_positive_abs_ratio","negative_eigenvalue_fraction","generation_status"
    ])
    write_csv(output_root / "bmc15b_null_geodesic_consistency_summary.csv", geo_rows, [
        "replicate_id","null_model_id","null_family","graph_id","pair_count","reachable_pair_count","unreachable_pair_count","unreachable_pair_fraction","mean_path_direct_ratio","median_path_direct_ratio","max_path_direct_ratio","mean_path_minus_direct","max_path_minus_direct","generation_status"
    ])
    write_csv(output_root / "bmc15b_null_local_dimension_proxy_summary.csv", dim_rows, [
        "replicate_id","null_model_id","null_family","graph_id","fit_points","effective_dimension_proxy","fit_r2","interpretation_label","generation_status"
    ])
    write_csv(output_root / "bmc15b_observed_vs_null_distribution_summary.csv", dist_rows, [
        "null_model_id","graph_id","null_graph_id","metric_group","metric","metric_direction","replicate_count","observed_value","null_mean","null_std","null_min","null_q05","null_median","null_q95","null_max","p_like_lower_tail","p_like_upper_tail","observed_quantile_position","interpretation_label","embedding_dimension"
    ])

    readout = output_root / "bmc15b_readout.md"
    write_readout(readout, dist_rows, reps)

    metrics = {
        "run_id": cfg.get("run_id", "BMC15b_geometry_proxy_null_comparison_open"),
        "replicate_count_per_null_model": reps,
        "null_models": [{"id": m, "family": f} for m, f in null_models],
        "null_graphs": list(OBS_MAP.keys()),
        "distribution_rows": len(dist_rows),
        "interpretation_warning": "Geometry-proxy null comparison only; no physical spacetime claim."
    }
    (output_root / "bmc15b_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-15b geometry-proxy null comparison completed.")
    print(f"Wrote: {output_root / 'bmc15b_null_graph_inventory.csv'}")
    print(f"Wrote: {output_root / 'bmc15b_null_triangle_summary.csv'}")
    print(f"Wrote: {output_root / 'bmc15b_null_embedding_summary.csv'}")
    print(f"Wrote: {output_root / 'bmc15b_null_geodesic_consistency_summary.csv'}")
    print(f"Wrote: {output_root / 'bmc15b_null_local_dimension_proxy_summary.csv'}")
    print(f"Wrote: {output_root / 'bmc15b_observed_vs_null_distribution_summary.csv'}")
    print(f"Wrote: {readout}")
    print(f"Wrote: {output_root / 'bmc15b_metrics.json'}")


if __name__ == "__main__":
    main()
