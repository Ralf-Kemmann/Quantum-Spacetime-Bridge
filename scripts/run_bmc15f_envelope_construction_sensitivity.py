#!/usr/bin/env python3
"""
BMC-15f Envelope-Construction Sensitivity Runner

Purpose
-------
Test whether BMC-15 geometry-proxy behavior is stable under changes in
envelope/backbone construction.

This is a robustness/sensitivity runner:
- It varies envelope construction methods and parameters.
- It computes graph summaries and geometry-proxy diagnostics.
- It compares variant edge sets to BMC-15 reference objects.
- It checks containment of the compact reference core where available.

It does NOT:
- claim physical geometry
- test causal/Lorentzian structure
- infer spacetime emergence
- overwrite original BMC-15 outputs

Expected config
---------------
data/bmc15f_envelope_construction_sensitivity_config.yaml

Main outputs
------------
runs/BMC-15f/envelope_construction_sensitivity_open/
  summary.json
  variant_metrics.csv
  family_summary.csv
  stability_summary.csv
  edge_overlap_summary.csv
  core_containment_summary.csv
  readout.md

Input expectations
------------------
The runner primarily uses:
  input.relational_matrix_path
  input.reference_graphs_dir

It accepts relational tables in either of these forms:

1) Edge table:
   source,target,weight
   source,target,distance,weight
   source,target,similarity

2) Wide numeric feature table:
   node_id plus numeric feature columns
   In this case, the runner builds a similarity matrix from standardized feature vectors.

For the current QSB/BMC workflow, the preferred input is usually an edge-like relational table.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml

try:
    import networkx as nx
except Exception as exc:  # pragma: no cover
    raise SystemExit("Missing dependency: networkx. Install with: pip install networkx") from exc

try:
    from sklearn.manifold import MDS
    SKLEARN_AVAILABLE = True
except Exception:
    MDS = None
    SKLEARN_AVAILABLE = False

try:
    from scipy.sparse.csgraph import shortest_path as scipy_shortest_path
    SCIPY_AVAILABLE = True
except Exception:
    scipy_shortest_path = None
    SCIPY_AVAILABLE = False


SOURCE_COLS = ["source", "src", "i", "node_i", "u", "from"]
TARGET_COLS = ["target", "dst", "j", "node_j", "v", "to"]
WEIGHT_COLS = ["weight", "w", "similarity", "strength", "edge_weight", "value"]
DISTANCE_COLS = ["distance", "dist", "dissimilarity", "cost"]
NODE_ID_COLS = ["node", "node_id", "id", "name", "label"]


@dataclass
class ReferenceGraph:
    name: str
    graph: nx.Graph
    path: Optional[Path] = None


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def as_list(x: Any) -> List[Any]:
    if x is None:
        return []
    if isinstance(x, list):
        return x
    return [x]


def find_col(cols: Iterable[str], candidates: List[str]) -> Optional[str]:
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def safe_float(x: Any, default: float = float("nan")) -> float:
    try:
        return float(x)
    except Exception:
        return default


def edge_key(u: Any, v: Any) -> Tuple[str, str]:
    a, b = str(u), str(v)
    return (a, b) if a <= b else (b, a)


def graph_edge_set(g: nx.Graph) -> set[Tuple[str, str]]:
    return {edge_key(u, v) for u, v in g.edges()}


def largest_component_subgraph(g: nx.Graph) -> nx.Graph:
    if g.number_of_nodes() == 0:
        return g.copy()
    if nx.is_connected(g):
        return g.copy()
    comps = sorted(nx.connected_components(g), key=len, reverse=True)
    return g.subgraph(comps[0]).copy()


def graph_summary(g: nx.Graph) -> Dict[str, Any]:
    n = g.number_of_nodes()
    e = g.number_of_edges()
    comps = nx.number_connected_components(g) if n > 0 else 0
    deg = np.array([d for _, d in g.degree()], dtype=float) if n > 0 else np.array([])
    return {
        "n_nodes": int(n),
        "n_edges": int(e),
        "n_components": int(comps),
        "is_connected": bool(comps == 1 and n > 0),
        "avg_degree": float(deg.mean()) if deg.size else float("nan"),
        "degree_std": float(deg.std(ddof=0)) if deg.size else float("nan"),
        "degree_max": float(deg.max()) if deg.size else float("nan"),
        "density": float(nx.density(g)) if n > 1 else float("nan"),
    }


def complete_pair_indices(n: int) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


# ---------------------------------------------------------------------
# Loading reference graph objects
# ---------------------------------------------------------------------

def load_edge_list(path: Path, object_name: str) -> nx.Graph:
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    df = pd.read_csv(path, sep=sep)

    src_col = find_col(df.columns, SOURCE_COLS)
    dst_col = find_col(df.columns, TARGET_COLS)
    w_col = find_col(df.columns, WEIGHT_COLS)
    dist_col = find_col(df.columns, DISTANCE_COLS)

    if src_col is None or dst_col is None:
        raise ValueError(
            f"Could not identify source/target columns in {path}. Columns found: {list(df.columns)}"
        )

    g = nx.Graph(name=object_name)
    for _, row in df.iterrows():
        u = str(row[src_col])
        v = str(row[dst_col])
        if u == v:
            continue
        if w_col is not None:
            w = safe_float(row[w_col], 1.0)
        elif dist_col is not None:
            d = max(safe_float(row[dist_col], 1.0), 1e-12)
            w = 1.0 / d
        else:
            w = 1.0
        g.add_edge(u, v, weight=float(w))
    return g


def find_graph_file(graph_dir: Path, object_name: str) -> Optional[Path]:
    candidates = [
        graph_dir / f"{object_name}.csv",
        graph_dir / f"{object_name}_edges.csv",
        graph_dir / f"edges_{object_name}.csv",
        graph_dir / f"{object_name}.tsv",
        graph_dir / f"{object_name}_edges.tsv",
        graph_dir / f"edges_{object_name}.tsv",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_reference_graphs(config: Dict[str, Any]) -> Dict[str, ReferenceGraph]:
    graph_dir = Path(config["input"]["reference_graphs_dir"]).expanduser()
    names = list(dict.fromkeys(as_list(config.get("reference_objects", [])) + [config.get("core_reference", {}).get("object_name", "")]))
    names = [str(n) for n in names if str(n).strip()]

    refs: Dict[str, ReferenceGraph] = {}
    if not graph_dir.exists():
        print(f"WARNING: reference graph directory not found: {graph_dir}", file=sys.stderr)
        return refs

    for name in names:
        p = find_graph_file(graph_dir, name)
        if p is None:
            print(f"WARNING: reference graph file not found for {name} under {graph_dir}", file=sys.stderr)
            continue
        g = load_edge_list(p, name)
        refs[name] = ReferenceGraph(name=name, graph=g, path=p)
    return refs


# ---------------------------------------------------------------------
# Relational input handling
# ---------------------------------------------------------------------

@dataclass
class RelationalInput:
    nodes: List[str]
    similarity: np.ndarray
    distance: np.ndarray
    source_kind: str


def standardize_features(x: np.ndarray) -> np.ndarray:
    x = x.astype(float)
    mean = np.nanmean(x, axis=0)
    std = np.nanstd(x, axis=0)
    std[std == 0] = 1.0
    z = (x - mean) / std
    z = np.nan_to_num(z, nan=0.0)
    return z


def load_relational_input(path: Path) -> RelationalInput:
    if not path.exists():
        raise FileNotFoundError(f"Relational input not found: {path}")

    df = pd.read_csv(path)
    src_col = find_col(df.columns, SOURCE_COLS)
    dst_col = find_col(df.columns, TARGET_COLS)
    w_col = find_col(df.columns, WEIGHT_COLS)
    dist_col = find_col(df.columns, DISTANCE_COLS)

    if src_col is not None and dst_col is not None:
        nodes = sorted(set(df[src_col].astype(str)) | set(df[dst_col].astype(str)))
        idx = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        sim = np.zeros((n, n), dtype=float)
        dist = np.full((n, n), np.inf, dtype=float)
        np.fill_diagonal(dist, 0.0)

        for _, row in df.iterrows():
            u = str(row[src_col])
            v = str(row[dst_col])
            if u == v:
                continue
            i, j = idx[u], idx[v]

            if w_col is not None:
                w = safe_float(row[w_col], float("nan"))
                if not math.isfinite(w):
                    continue
                d = 1.0 / max(abs(w), 1e-12)
            elif dist_col is not None:
                d = safe_float(row[dist_col], float("nan"))
                if not math.isfinite(d):
                    continue
                w = 1.0 / max(abs(d), 1e-12)
            else:
                w = 1.0
                d = 1.0

            sim[i, j] = sim[j, i] = max(sim[i, j], float(w))
            dist[i, j] = dist[j, i] = min(dist[i, j], float(d))

        # Fill missing distances from similarity if needed.
        missing = ~np.isfinite(dist)
        derived = np.where(sim > 0, 1.0 / np.maximum(np.abs(sim), 1e-12), np.inf)
        dist[missing] = derived[missing]
        return RelationalInput(nodes=nodes, similarity=sim, distance=dist, source_kind="edge_table")

    # Wide table fallback.
    node_col = find_col(df.columns, NODE_ID_COLS)
    if node_col is None:
        node_col = df.columns[0]
    nodes = df[node_col].astype(str).tolist()
    num = df.select_dtypes(include=[np.number]).copy()
    if num.empty:
        raise ValueError(
            f"Could not interpret {path} as edge table or numeric feature table. "
            f"Columns: {list(df.columns)}"
        )
    z = standardize_features(num.to_numpy(dtype=float))
    diff = z[:, None, :] - z[None, :, :]
    dist = np.sqrt(np.sum(diff * diff, axis=2))
    sim = 1.0 / (1.0 + dist)
    np.fill_diagonal(sim, 0.0)
    np.fill_diagonal(dist, 0.0)
    return RelationalInput(nodes=nodes, similarity=sim, distance=dist, source_kind="wide_feature_table")


# ---------------------------------------------------------------------
# Envelope construction
# ---------------------------------------------------------------------

def graph_from_index_edges(nodes: List[str], pairs: List[Tuple[int, int]], weights: List[float]) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(nodes)
    for (i, j), w in zip(pairs, weights):
        if i == j:
            continue
        g.add_edge(nodes[i], nodes[j], weight=float(w))
    return g


def mutual_knn_graph(rel: RelationalInput, k: int) -> nx.Graph:
    sim = rel.similarity.copy()
    n = len(rel.nodes)
    np.fill_diagonal(sim, -np.inf)

    neighbor_sets = []
    for i in range(n):
        order = np.argsort(sim[i])[::-1]
        order = [j for j in order if math.isfinite(sim[i, j]) and sim[i, j] > 0]
        neighbor_sets.append(set(order[:k]))

    pairs = []
    weights = []
    for i in range(n):
        for j in range(i + 1, n):
            if j in neighbor_sets[i] and i in neighbor_sets[j]:
                pairs.append((i, j))
                weights.append(float(max(sim[i, j], sim[j, i])))
    return graph_from_index_edges(rel.nodes, pairs, weights)


def directed_knn_symmetrized_graph(rel: RelationalInput, k: int) -> nx.Graph:
    # Algorithmic directed kNN union, symmetrized for the current undirected proxy diagnostics.
    sim = rel.similarity.copy()
    n = len(rel.nodes)
    np.fill_diagonal(sim, -np.inf)
    edge_scores: Dict[Tuple[int, int], float] = {}
    for i in range(n):
        order = np.argsort(sim[i])[::-1]
        order = [j for j in order if math.isfinite(sim[i, j]) and sim[i, j] > 0]
        for j in order[:k]:
            key = (i, j) if i < j else (j, i)
            edge_scores[key] = max(edge_scores.get(key, -np.inf), float(sim[i, j]))
    pairs = list(edge_scores.keys())
    weights = [edge_scores[p] for p in pairs]
    return graph_from_index_edges(rel.nodes, pairs, weights)


def threshold_top_fraction_graph(rel: RelationalInput, top_fraction: float) -> nx.Graph:
    sim = rel.similarity.copy()
    n = len(rel.nodes)
    pairs = complete_pair_indices(n)
    vals = np.array([sim[i, j] for i, j in pairs], dtype=float)
    valid = np.where(np.isfinite(vals) & (vals > 0))[0]
    if valid.size == 0:
        return graph_from_index_edges(rel.nodes, [], [])
    m = max(1, int(round(len(pairs) * float(top_fraction))))
    m = min(m, valid.size)
    order = valid[np.argsort(vals[valid])[::-1]][:m]
    chosen = [pairs[int(i)] for i in order]
    weights = [float(vals[int(i)]) for i in order]
    return graph_from_index_edges(rel.nodes, chosen, weights)


def spanning_tree_graph(rel: RelationalInput, mode: str) -> nx.Graph:
    base = nx.Graph()
    base.add_nodes_from(rel.nodes)
    n = len(rel.nodes)

    for i, j in complete_pair_indices(n):
        sim = float(rel.similarity[i, j])
        d = float(rel.distance[i, j])
        if not math.isfinite(sim) or sim <= 0:
            continue
        if mode == "minimum_distance_spanning_tree":
            tree_weight = d if math.isfinite(d) else 1.0 / max(abs(sim), 1e-12)
        else:
            # networkx maximum_spanning_tree maximizes this.
            tree_weight = sim
        base.add_edge(rel.nodes[i], rel.nodes[j], weight=sim, tree_weight=tree_weight)

    if base.number_of_edges() == 0:
        return base

    if mode == "minimum_distance_spanning_tree":
        # Use minimum spanning tree over tree_weight, keep original similarity as weight.
        t = nx.minimum_spanning_tree(base, weight="tree_weight")
    else:
        t = nx.maximum_spanning_tree(base, weight="tree_weight")

    g = nx.Graph()
    g.add_nodes_from(rel.nodes)
    for u, v, d in t.edges(data=True):
        g.add_edge(u, v, weight=float(d.get("weight", 1.0)))
    return g


def path_consensus_graph(rel: RelationalInput, path_depth: int, consensus_threshold: float) -> nx.Graph:
    # Transparent toy path-consensus proxy:
    # Start from top direct similarities, compute common-neighborhood support in a directed kNN-like graph,
    # keep edges whose normalized support exceeds threshold.
    n = len(rel.nodes)
    k = max(2, int(path_depth))
    seed = directed_knn_symmetrized_graph(rel, k=k)
    neigh = {node: set(seed.neighbors(node)) for node in seed.nodes()}
    pairs = []
    weights = []
    for i, j in complete_pair_indices(n):
        u, v = rel.nodes[i], rel.nodes[j]
        common = len(neigh.get(u, set()) & neigh.get(v, set()))
        denom = max(1, min(len(neigh.get(u, set())), len(neigh.get(v, set()))))
        support = common / denom
        if support >= float(consensus_threshold) and rel.similarity[i, j] > 0:
            pairs.append((i, j))
            weights.append(float(rel.similarity[i, j]))
    return graph_from_index_edges(rel.nodes, pairs, weights)


def construct_variants(config: Dict[str, Any], rel: RelationalInput) -> List[Tuple[str, str, Dict[str, Any], nx.Graph]]:
    variants: List[Tuple[str, str, Dict[str, Any], nx.Graph]] = []

    for fam in as_list(config.get("envelope_families", [])):
        if not fam.get("enabled", False):
            continue
        name = str(fam.get("name", "unknown_family"))
        mode = str(fam.get("construction_mode", name))
        params = fam.get("parameters", {}) or {}

        if mode == "mutual_kNN":
            for k in as_list(params.get("k", [])):
                k = int(k)
                g = mutual_knn_graph(rel, k=k)
                variants.append((name, f"{name}_k{k}", {"k": k, "construction_mode": mode}, g))

        elif mode == "directed_kNN":
            for k in as_list(params.get("k", [])):
                k = int(k)
                g = directed_knn_symmetrized_graph(rel, k=k)
                variants.append((name, f"{name}_k{k}", {"k": k, "construction_mode": mode, "direction_note": "algorithmic_neighbor_direction_not_causal"}, g))

        elif mode == "top_fraction_threshold":
            for top_fraction in as_list(params.get("top_fraction", [])):
                tf = float(top_fraction)
                g = threshold_top_fraction_graph(rel, top_fraction=tf)
                variants.append((name, f"{name}_top_fraction_{tf:g}", {"top_fraction": tf, "construction_mode": mode}, g))

        elif mode == "spanning_tree":
            for tree_mode in as_list(params.get("modes", [])):
                tree_mode = str(tree_mode)
                g = spanning_tree_graph(rel, mode=tree_mode)
                variants.append((name, f"{name}_{tree_mode}", {"mode": tree_mode, "construction_mode": mode}, g))

        elif mode == "path_consensus":
            for depth in as_list(params.get("path_depth", [])):
                for threshold in as_list(params.get("consensus_threshold", [])):
                    d = int(depth)
                    th = float(threshold)
                    g = path_consensus_graph(rel, path_depth=d, consensus_threshold=th)
                    variants.append((name, f"{name}_depth{d}_thr{th:g}", {"path_depth": d, "consensus_threshold": th, "construction_mode": mode}, g))

        else:
            print(f"WARNING: unsupported envelope construction mode: {mode} (family {name})", file=sys.stderr)

    return variants


# ---------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------

def pairwise_distances(points: np.ndarray) -> np.ndarray:
    diff = points[:, None, :] - points[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=2))


def all_pairs_distance_matrix(g: nx.Graph, disconnected_policy: str = "largest_component") -> Tuple[np.ndarray, List[str], str]:
    h = g
    policy_note = "as_is"

    if g.number_of_nodes() == 0:
        return np.zeros((0, 0)), [], "empty"

    if not nx.is_connected(g):
        if disconnected_policy == "largest_component":
            h = largest_component_subgraph(g)
            policy_note = "largest_component"
        else:
            policy_note = "disconnected_with_infinite"

    nodes = list(h.nodes())
    n = len(nodes)
    idx = {node: i for i, node in enumerate(nodes)}
    mat = np.full((n, n), np.inf, dtype=float)
    np.fill_diagonal(mat, 0.0)

    for u, v, d in h.edges(data=True):
        w = safe_float(d.get("weight", 1.0), 1.0)
        cost = 1.0 / max(abs(w), 1e-12)
        i, j = idx[u], idx[v]
        mat[i, j] = min(mat[i, j], cost)
        mat[j, i] = min(mat[j, i], cost)

    if SCIPY_AVAILABLE:
        dist = scipy_shortest_path(mat, directed=False, unweighted=False)
    else:
        lengths = dict(nx.all_pairs_dijkstra_path_length(h, weight=lambda u, v, d: 1.0 / max(abs(safe_float(d.get("weight", 1.0), 1.0)), 1e-12)))
        dist = np.full((n, n), np.inf, dtype=float)
        np.fill_diagonal(dist, 0.0)
        for u, lu in lengths.items():
            for v, val in lu.items():
                dist[idx[u], idx[v]] = val

    return dist, nodes, policy_note


def triangle_defect_count(dist: np.ndarray, tol: float = 1e-12) -> int:
    n = dist.shape[0]
    if n < 3:
        return 0
    defects = 0
    for i in range(n):
        for j in range(n):
            dij = dist[i, j]
            if not np.isfinite(dij):
                continue
            for k in range(n):
                if i == j or j == k or i == k:
                    continue
                if not np.isfinite(dist[i, k]) or not np.isfinite(dist[k, j]):
                    continue
                if dij > dist[i, k] + dist[k, j] + tol:
                    defects += 1
    return int(defects)


def classical_mds_negative_eigen_burden(dist: np.ndarray) -> Tuple[float, int]:
    n = dist.shape[0]
    if n < 2 or not np.all(np.isfinite(dist)):
        return float("nan"), 0

    d2 = dist ** 2
    j = np.eye(n) - np.ones((n, n)) / n
    b = -0.5 * j @ d2 @ j
    eigvals = np.linalg.eigvalsh(b)
    neg = eigvals[eigvals < -1e-10]
    total_abs = np.sum(np.abs(eigvals))
    burden = float(np.sum(np.abs(neg)) / total_abs) if total_abs > 0 else 0.0
    return burden, int(len(neg))


def normalized_embedding_stress(dist: np.ndarray, dim: int, random_state: int) -> float:
    n = dist.shape[0]
    if n <= dim or n < 3:
        return float("nan")
    if not SKLEARN_AVAILABLE:
        return float("nan")
    if not np.all(np.isfinite(dist)):
        return float("nan")

    mds = MDS(
        n_components=dim,
        dissimilarity="precomputed",
        random_state=random_state,
        n_init=4,
        max_iter=300,
        eps=1e-6,
        init="random",
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn.manifold._mds")
        coords = mds.fit_transform(dist)

    emb_dist = pairwise_distances(coords)
    tri = np.triu_indices(n, 1)
    denom = np.sum(dist[tri] ** 2)
    if denom <= 0:
        return float("nan")
    stress = np.sqrt(np.sum((dist[tri] - emb_dist[tri]) ** 2) / denom)
    return float(stress)


def geodesic_consistency_error(dist: np.ndarray) -> float:
    vals = dist[np.triu_indices(dist.shape[0], 1)]
    vals = vals[np.isfinite(vals)]
    vals = vals[vals > 0]
    if vals.size == 0:
        return float("nan")
    mean = vals.mean()
    return float(vals.std(ddof=0) / mean) if mean > 0 else float("nan")


def local_dimension_proxy(g: nx.Graph) -> float:
    h = largest_component_subgraph(g)
    n = h.number_of_nodes()
    if n < 3:
        return float("nan")
    lengths = dict(nx.all_pairs_shortest_path_length(h))
    vals = []
    for _, lu in lengths.items():
        finite = [v for v in lu.values() if v > 0]
        if finite:
            vals.append(np.mean(finite))
    if not vals:
        return float("nan")
    avg_dist = float(np.mean(vals))
    if avg_dist <= 1.0:
        return float("nan")
    return float(np.log(n) / np.log(avg_dist + 1.0))


def compute_diagnostics(g: nx.Graph, embedding_dims: List[int], random_state: int, disconnected_policy: str) -> Dict[str, Any]:
    summary = graph_summary(g)
    dist, dist_nodes, policy_note = all_pairs_distance_matrix(g, disconnected_policy=disconnected_policy)
    tri_defects = triangle_defect_count(dist)
    neg_burden, neg_count = classical_mds_negative_eigen_burden(dist)

    out: Dict[str, Any] = dict(summary)
    out.update({
        "distance_node_count": int(len(dist_nodes)),
        "distance_policy": policy_note,
        "triangle_defects": tri_defects,
        "negative_eigenvalue_burden": neg_burden,
        "negative_eigenvalue_count": neg_count,
        "geodesic_consistency_error": geodesic_consistency_error(dist),
        "local_dimension_proxy": local_dimension_proxy(g),
    })

    for dim in embedding_dims:
        out[f"embedding_stress_{dim}d"] = normalized_embedding_stress(dist, dim, random_state=random_state + dim)

    return out


# ---------------------------------------------------------------------
# Overlap, containment, stability
# ---------------------------------------------------------------------

def edge_jaccard(a: nx.Graph, b: nx.Graph) -> float:
    ea = graph_edge_set(a)
    eb = graph_edge_set(b)
    if not ea and not eb:
        return float("nan")
    union = ea | eb
    inter = ea & eb
    return float(len(inter) / len(union)) if union else float("nan")


def containment(reference_small: nx.Graph, target: nx.Graph) -> Tuple[int, int, float]:
    small = graph_edge_set(reference_small)
    large = graph_edge_set(target)
    if not small:
        return 0, 0, float("nan")
    inter = small & large
    return len(inter), len(small), float(len(inter) / len(small))


def metric_columns(df: pd.DataFrame) -> List[str]:
    prefixes = [
        "triangle_defects",
        "negative_eigenvalue_burden",
        "negative_eigenvalue_count",
        "geodesic_consistency_error",
        "local_dimension_proxy",
        "embedding_stress_",
    ]
    return [c for c in df.columns if any(c == p or c.startswith(p) for p in prefixes)]


def classify_stability(values: pd.Series, thresholds: Dict[str, Any]) -> Tuple[str, float]:
    vals = pd.to_numeric(values, errors="coerce").dropna()
    if len(vals) < 2:
        return "insufficient_values", float("nan")
    mean = float(vals.mean())
    std = float(vals.std(ddof=0))
    if abs(mean) < 1e-12:
        cv = 0.0 if std < 1e-12 else float("inf")
    else:
        cv = abs(std / mean)
    stable_max = float(thresholds.get("stable_cv_max", 0.10))
    moderate_max = float(thresholds.get("moderately_stable_cv_max", 0.25))
    if cv <= stable_max:
        return "stable_across_variants", cv
    if cv <= moderate_max:
        return "moderately_stable_across_variants", cv
    return "parameter_sensitive", cv


def summarize_family(metrics_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    mcols = metric_columns(metrics_df)
    for family, sub in metrics_df.groupby("envelope_family", dropna=False):
        row: Dict[str, Any] = {
            "envelope_family": family,
            "variant_count": int(len(sub)),
            "connected_count": int(sub["is_connected"].sum()),
            "connected_rate": float(sub["is_connected"].mean()),
            "median_n_edges": float(sub["n_edges"].median()),
            "min_n_edges": int(sub["n_edges"].min()),
            "max_n_edges": int(sub["n_edges"].max()),
        }
        for m in mcols:
            vals = pd.to_numeric(sub[m], errors="coerce")
            row[f"{m}_median"] = float(vals.median()) if vals.notna().any() else float("nan")
            row[f"{m}_iqr"] = float(vals.quantile(0.75) - vals.quantile(0.25)) if vals.notna().any() else float("nan")
            row[f"{m}_min"] = float(vals.min()) if vals.notna().any() else float("nan")
            row[f"{m}_max"] = float(vals.max()) if vals.notna().any() else float("nan")
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_stability(metrics_df: pd.DataFrame, thresholds: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    mcols = metric_columns(metrics_df)
    for family, sub in metrics_df.groupby("envelope_family", dropna=False):
        for m in mcols:
            label, cv = classify_stability(sub[m], thresholds)
            vals = pd.to_numeric(sub[m], errors="coerce")
            rows.append({
                "envelope_family": family,
                "metric": m,
                "variant_count": int(len(sub)),
                "finite_count": int(vals.notna().sum()),
                "mean": float(vals.mean()) if vals.notna().any() else float("nan"),
                "std": float(vals.std(ddof=0)) if vals.notna().any() else float("nan"),
                "cv": cv,
                "stability_label": label,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------
# Readout
# ---------------------------------------------------------------------

def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_readout(
    path: Path,
    config: Dict[str, Any],
    rel: RelationalInput,
    metrics_df: pd.DataFrame,
    family_df: pd.DataFrame,
    stability_df: pd.DataFrame,
    edge_overlap_df: pd.DataFrame,
    core_df: pd.DataFrame,
    warnings_list: List[str],
) -> None:
    lines = []
    lines.append("# BMC-15f Envelope-Construction Sensitivity — Readout\n")
    lines.append(f"- Generated: `{now_iso()}`")
    lines.append(f"- Run ID: `{config.get('run_id', 'unknown')}`")
    lines.append(f"- Output directory: `{config.get('output', {}).get('output_dir', '')}`")
    lines.append("")
    lines.append("## Scope\n")
    lines.append("This is an envelope/backbone construction sensitivity diagnostic.")
    lines.append("It does not test physical spacetime emergence, causal structure, Lorentzian signature, or a physical metric.")
    lines.append("")
    lines.append("## Input\n")
    lines.append(f"- Relational input source kind: `{rel.source_kind}`")
    lines.append(f"- Nodes: `{len(rel.nodes)}`")
    lines.append("")
    lines.append("## Variant summary\n")
    lines.append(f"- Variant metric rows: `{len(metrics_df)}`")
    lines.append(f"- Family summary rows: `{len(family_df)}`")
    lines.append(f"- Stability rows: `{len(stability_df)}`")
    lines.append(f"- Edge-overlap rows: `{len(edge_overlap_df)}`")
    lines.append(f"- Core-containment rows: `{len(core_df)}`")
    lines.append("")
    lines.append("## Family connectedness\n")
    if not family_df.empty:
        lines.append("| Envelope family | Variants | Connected rate | Median edges | Edge range |")
        lines.append("|---|---:|---:|---:|---|")
        for _, r in family_df.iterrows():
            lines.append(
                f"| `{r['envelope_family']}` | {int(r['variant_count'])} | "
                f"{float(r['connected_rate']):.3f} | {float(r['median_n_edges']):.1f} | "
                f"{int(r['min_n_edges'])}–{int(r['max_n_edges'])} |"
            )
    else:
        lines.append("No family summary generated.")
    lines.append("")
    lines.append("## Stability label counts\n")
    if not stability_df.empty:
        counts = stability_df["stability_label"].value_counts().reset_index()
        counts.columns = ["stability_label", "count"]
        lines.append("| Label | Count |")
        lines.append("|---|---:|")
        for _, r in counts.iterrows():
            lines.append(f"| `{r['stability_label']}` | {int(r['count'])} |")
    else:
        lines.append("No stability summary generated.")
    lines.append("")
    lines.append("## Warnings\n")
    if warnings_list:
        for w in sorted(set(warnings_list)):
            lines.append(f"- {w}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Conservative interpretation template\n")
    lines.append("BMC-15f tests whether geometry-proxy diagnostics are stable under envelope construction variants.")
    lines.append("Stability supports construction-robustness of the proxy readout, not physical geometry.")
    lines.append("Sensitivity indicates method-dependence that must qualify any envelope-level interpretation.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Run BMC-15f Envelope-Construction Sensitivity MVP.")
    parser.add_argument(
        "--config",
        default="data/bmc15f_envelope_construction_sensitivity_config.yaml",
        help="Path to YAML config.",
    )
    args = parser.parse_args()

    config_path = Path(args.config).expanduser()
    config = load_yaml(config_path)

    outdir = Path(config["output"]["output_dir"]).expanduser()
    ensure_dir(outdir)

    seed = int(config.get("random", {}).get("seed", 15016))
    embedding_dims = [int(x) for x in as_list(config.get("embedding", {}).get("dimensions", [2, 3, 4]))]
    disconnected_policy = str(config.get("embedding", {}).get("disconnected_policy", "largest_component"))

    warnings_list: List[str] = []
    if not SKLEARN_AVAILABLE:
        warnings_list.append("scikit-learn unavailable: embedding stress metrics will be NaN.")
    if not SCIPY_AVAILABLE:
        warnings_list.append("scipy unavailable: using networkx shortest paths fallback.")

    rel_path = Path(config["input"]["relational_matrix_path"]).expanduser()
    rel = load_relational_input(rel_path)

    refs = load_reference_graphs(config)
    variants = construct_variants(config, rel)

    if not variants:
        raise RuntimeError("No envelope variants were generated. Check envelope_families config.")

    core_ref_cfg = config.get("core_reference", {}) or {}
    core_ref_name = str(core_ref_cfg.get("object_name", ""))
    core_ref = refs.get(core_ref_name) if core_ref_cfg.get("enabled", False) else None

    metric_rows: List[Dict[str, Any]] = []
    overlap_rows: List[Dict[str, Any]] = []
    core_rows: List[Dict[str, Any]] = []

    for idx, (family, variant_name, params, g) in enumerate(variants):
        diag = compute_diagnostics(
            g,
            embedding_dims=embedding_dims,
            random_state=seed + idx * 100,
            disconnected_policy=disconnected_policy,
        )
        row: Dict[str, Any] = {
            "run_id": config.get("run_id", ""),
            "envelope_family": family,
            "variant_name": variant_name,
            "variant_parameters_json": json.dumps(params, sort_keys=True),
        }
        row.update(diag)
        metric_rows.append(row)

        for ref_name, ref in refs.items():
            if ref_name == core_ref_name:
                continue
            overlap_rows.append({
                "variant_name": variant_name,
                "envelope_family": family,
                "reference_object": ref_name,
                "reference_edges": ref.graph.number_of_edges(),
                "variant_edges": g.number_of_edges(),
                "edge_jaccard": edge_jaccard(ref.graph, g),
            })

        if core_ref is not None:
            inter, total, frac = containment(core_ref.graph, g)
            core_rows.append({
                "variant_name": variant_name,
                "envelope_family": family,
                "core_reference": core_ref_name,
                "core_edges_total": total,
                "core_edges_contained": inter,
                "core_containment_fraction": frac,
            })

    metrics_df = pd.DataFrame(metric_rows)
    family_df = summarize_family(metrics_df)
    stability_df = summarize_stability(metrics_df, config.get("stability", {}).get("dispersion_thresholds", {}) or {})
    edge_overlap_df = pd.DataFrame(overlap_rows)
    core_df = pd.DataFrame(core_rows)

    metrics_path = outdir / "variant_metrics.csv"
    family_path = outdir / "family_summary.csv"
    stability_path = outdir / "stability_summary.csv"
    edge_overlap_path = outdir / "edge_overlap_summary.csv"
    core_path = outdir / "core_containment_summary.csv"
    summary_path = outdir / "summary.json"
    readout_path = outdir / "readout.md"

    metrics_df.to_csv(metrics_path, index=False)
    family_df.to_csv(family_path, index=False)
    stability_df.to_csv(stability_path, index=False)
    edge_overlap_df.to_csv(edge_overlap_path, index=False)
    core_df.to_csv(core_path, index=False)

    summary = {
        "run_id": config.get("run_id", ""),
        "generated_at": now_iso(),
        "config_path": str(config_path),
        "output_dir": str(outdir),
        "relational_input_path": str(rel_path),
        "relational_input_kind": rel.source_kind,
        "n_nodes": len(rel.nodes),
        "n_variants": len(metrics_df),
        "n_envelope_families": int(metrics_df["envelope_family"].nunique()) if not metrics_df.empty else 0,
        "reference_graphs_loaded": {name: {"path": str(ref.path), **graph_summary(ref.graph)} for name, ref in refs.items()},
        "sklearn_available": SKLEARN_AVAILABLE,
        "scipy_available": SCIPY_AVAILABLE,
        "warnings": sorted(set(warnings_list)),
        "claim_boundary": (
            "Envelope-construction sensitivity only. No physical geometry, causal structure, "
            "Lorentzian signature, or spacetime emergence is established."
        ),
    }
    write_json(summary_path, summary)
    write_readout(readout_path, config, rel, metrics_df, family_df, stability_df, edge_overlap_df, core_df, warnings_list)

    print("BMC-15f Envelope-Construction Sensitivity complete.")
    print(f"Output directory: {outdir}")
    print(f"Variant metrics: {metrics_path}")
    print(f"Family summary: {family_path}")
    print(f"Stability summary: {stability_path}")
    print(f"Edge overlap summary: {edge_overlap_path}")
    print(f"Core containment summary: {core_path}")
    print(f"Summary: {summary_path}")
    print(f"Readout: {readout_path}")
    if warnings_list:
        print("Warnings:")
        for w in sorted(set(warnings_list)):
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
