#!/usr/bin/env python3
"""
BMC-15e Geometry-Control Nulls Runner

Purpose
-------
Generate explicitly geometry-created control graphs and compare their geometry-proxy
diagnostics against observed BMC-15 graph objects.

This runner is intentionally conservative:
- It does not claim physical geometry.
- It does not test causal or Lorentzian structure.
- It does not delete or overwrite existing outputs unless the target file is rewritten
  as part of the current run directory.
- It writes transparent CSV/JSON/Markdown readouts.

Expected config
---------------
data/bmc15e_geometry_control_nulls_config.yaml

Main outputs
------------
runs/BMC-15e/geometry_control_nulls_open/
  summary.json
  geometry_control_metrics.csv
  family_summary.csv
  observed_position_summary.csv
  readout.md

Input expectations
------------------
The runner tries to load observed graph objects from `input.observed_graphs_dir`.

Supported edge-list file candidates per graph object:
  <object>.csv
  <object>_edges.csv
  edges_<object>.csv
  <object>.tsv
  <object>_edges.tsv

Expected edge-list columns, flexible:
  source / src / i / node_i / u
  target / dst / j / node_j / v
  weight / w / similarity / strength  [optional]

If no observed graph-object file is found, the runner can still generate a
minimal observed-object shell only if enough metadata are available. In normal
repo use, provide explicit observed graph edges.

Dependencies
------------
Required:
  numpy
  pandas
  pyyaml
  networkx

Optional:
  scikit-learn, scipy

Embedding stress is implemented with sklearn.manifold.MDS if available.
If sklearn is unavailable, stress values are reported as NaN and marked in readout.
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


# -----------------------------
# Data structures
# -----------------------------

@dataclass
class GraphObject:
    name: str
    graph: nx.Graph


@dataclass
class ControlSpec:
    family: str
    dimension: int
    weight_mode: str
    replicate: int


# -----------------------------
# Utility
# -----------------------------

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


# -----------------------------
# Observed graph loading
# -----------------------------

SOURCE_COLS = ["source", "src", "i", "node_i", "u", "from"]
TARGET_COLS = ["target", "dst", "j", "node_j", "v", "to"]
WEIGHT_COLS = ["weight", "w", "similarity", "strength", "edge_weight", "value"]


def find_col(cols: Iterable[str], candidates: List[str]) -> Optional[str]:
    lower = {c.lower(): c for c in cols}
    for cand in candidates:
        if cand.lower() in lower:
            return lower[cand.lower()]
    return None


def load_edge_list(path: Path, object_name: str) -> nx.Graph:
    sep = "\t" if path.suffix.lower() == ".tsv" else ","
    df = pd.read_csv(path, sep=sep)

    src_col = find_col(df.columns, SOURCE_COLS)
    dst_col = find_col(df.columns, TARGET_COLS)
    w_col = find_col(df.columns, WEIGHT_COLS)

    if src_col is None or dst_col is None:
        raise ValueError(
            f"Could not identify source/target columns in {path}. "
            f"Columns found: {list(df.columns)}"
        )

    g = nx.Graph(name=object_name)
    for _, row in df.iterrows():
        u = str(row[src_col])
        v = str(row[dst_col])
        if u == v:
            continue
        w = safe_float(row[w_col], 1.0) if w_col else 1.0
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


def load_observed_graphs(config: Dict[str, Any]) -> List[GraphObject]:
    graph_dir = Path(config["input"]["observed_graphs_dir"]).expanduser()
    object_names = as_list(config.get("graph_objects", []))

    if not graph_dir.exists():
        raise FileNotFoundError(
            f"Observed graph directory not found: {graph_dir}\n"
            "Expected edge lists under input.observed_graphs_dir."
        )

    objects: List[GraphObject] = []
    missing: List[str] = []

    for name in object_names:
        p = find_graph_file(graph_dir, str(name))
        if p is None:
            missing.append(str(name))
            continue
        g = load_edge_list(p, str(name))
        objects.append(GraphObject(name=str(name), graph=g))

    if missing:
        print("WARNING: Missing observed graph files for:", ", ".join(missing), file=sys.stderr)

    if not objects:
        raise RuntimeError(
            f"No observed graph objects could be loaded from {graph_dir}. "
            "Provide edge-list CSV/TSV files for at least one graph object."
        )

    return objects


# -----------------------------
# Geometry-control generation
# -----------------------------

def sample_points(n: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    return rng.random((n, dim))


def pairwise_distances(points: np.ndarray) -> np.ndarray:
    diff = points[:, None, :] - points[None, :, :]
    return np.sqrt(np.sum(diff * diff, axis=2))


def complete_pair_indices(n: int) -> List[Tuple[int, int]]:
    return [(i, j) for i in range(n) for j in range(i + 1, n)]


def build_graph_from_edges(nodes: List[str], edge_pairs: List[Tuple[int, int]], weights: List[float]) -> nx.Graph:
    g = nx.Graph()
    g.add_nodes_from(nodes)
    for (i, j), w in zip(edge_pairs, weights):
        g.add_edge(nodes[i], nodes[j], weight=float(w))
    return g


def observed_weight_ranks(g: nx.Graph) -> List[float]:
    weights = [safe_float(d.get("weight", 1.0), 1.0) for _, _, d in g.edges(data=True)]
    weights = sorted(weights, reverse=True)
    return weights


def assign_rank_remap_weights(edge_pairs: List[Tuple[int, int]], geom_scores: List[float], observed_weights: List[float]) -> List[float]:
    # Highest geometry score gets highest observed weight.
    m = len(edge_pairs)
    if not observed_weights:
        return [1.0] * m
    weights = observed_weights[:m]
    if len(weights) < m:
        weights += [weights[-1]] * (m - len(weights))

    order = np.argsort(np.array(geom_scores))[::-1]
    out = np.zeros(m, dtype=float)
    for rank, idx in enumerate(order):
        out[idx] = float(weights[rank])
    return out.tolist()


def select_top_pairs_by_score(scores: np.ndarray, edge_count: int) -> Tuple[List[Tuple[int, int]], List[float]]:
    n = scores.shape[0]
    pairs = complete_pair_indices(n)
    vals = [float(scores[i, j]) for i, j in pairs]
    order = np.argsort(np.array(vals))[::-1]
    chosen_idx = order[:edge_count]
    return [pairs[i] for i in chosen_idx], [vals[i] for i in chosen_idx]


def soft_geometric_kernel_graph(
    observed: nx.Graph,
    dim: int,
    weight_mode: str,
    rng: np.random.Generator,
    kernel: str = "exp_negative_distance",
    scale_mode: str = "median_distance",
) -> nx.Graph:
    nodes = list(observed.nodes())
    n = len(nodes)
    e = observed.number_of_edges()
    pts = sample_points(n, dim, rng)
    dist = pairwise_distances(pts)

    upper = dist[np.triu_indices(n, 1)]
    scale = float(np.median(upper)) if scale_mode == "median_distance" and upper.size else 1.0
    if scale <= 0:
        scale = 1.0

    if kernel == "exp_negative_squared_distance":
        scores = np.exp(-(dist ** 2) / (scale ** 2))
    elif kernel == "inverse_one_plus_distance":
        scores = 1.0 / (1.0 + dist)
    else:
        scores = np.exp(-dist / scale)

    np.fill_diagonal(scores, -np.inf)
    pairs, geom_scores = select_top_pairs_by_score(scores, e)

    if weight_mode == "observed_rank_remap":
        weights = assign_rank_remap_weights(pairs, geom_scores, observed_weight_ranks(observed))
    elif weight_mode == "unweighted":
        weights = [1.0] * len(pairs)
    else:
        weights = geom_scores

    return build_graph_from_edges(nodes, pairs, weights)


def random_geometric_graph_top_pairs(
    observed: nx.Graph,
    dim: int,
    weight_mode: str,
    rng: np.random.Generator,
) -> nx.Graph:
    # Auditable RGG-style control: select nearest pairs until edge count matches.
    nodes = list(observed.nodes())
    n = len(nodes)
    e = observed.number_of_edges()
    pts = sample_points(n, dim, rng)
    dist = pairwise_distances(pts)
    scores = -dist
    np.fill_diagonal(scores, -np.inf)
    pairs, geom_scores = select_top_pairs_by_score(scores, e)

    if weight_mode == "observed_rank_remap":
        weights = assign_rank_remap_weights(pairs, geom_scores, observed_weight_ranks(observed))
    elif weight_mode == "unweighted":
        weights = [1.0] * len(pairs)
    else:
        weights = [float(-s) for s in geom_scores]

    return build_graph_from_edges(nodes, pairs, weights)


def make_connected_prefer(
    generator_fn,
    observed: nx.Graph,
    dim: int,
    weight_mode: str,
    rng: np.random.Generator,
    max_attempts: int,
    prefer_connected: bool,
    **kwargs,
) -> Tuple[nx.Graph, int, bool]:
    last_g: Optional[nx.Graph] = None
    for attempt in range(1, max_attempts + 1):
        g = generator_fn(observed, dim, weight_mode, rng, **kwargs)
        last_g = g
        if not prefer_connected or nx.is_connected(g):
            return g, attempt, bool(nx.is_connected(g))
    assert last_g is not None
    return last_g, max_attempts, bool(nx.is_connected(last_g))


# -----------------------------
# Diagnostics
# -----------------------------

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
        # Convert similarity-like weight to distance-like cost.
        # Larger weights mean closer relation.
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
    # O(n^3), okay for small/medium N. Transparent > clever here.
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

    # sklearn normalized_stress exists only in newer versions, so compute manually.
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
    # Simple proxy: coefficient of variation of finite non-zero geodesic distances.
    vals = dist[np.triu_indices(dist.shape[0], 1)]
    vals = vals[np.isfinite(vals)]
    vals = vals[vals > 0]
    if vals.size == 0:
        return float("nan")
    mean = vals.mean()
    return float(vals.std(ddof=0) / mean) if mean > 0 else float("nan")


def local_dimension_proxy(g: nx.Graph) -> float:
    # Very cautious proxy: log(N) / log(avg shortest-path radius-ish).
    # It is not a physical dimension.
    h = largest_component_subgraph(g)
    n = h.number_of_nodes()
    if n < 3:
        return float("nan")
    lengths = dict(nx.all_pairs_shortest_path_length(h))
    vals = []
    for u, lu in lengths.items():
        finite = [v for v in lu.values() if v > 0]
        if finite:
            vals.append(np.mean(finite))
    if not vals:
        return float("nan")
    avg_dist = float(np.mean(vals))
    if avg_dist <= 1.0:
        return float("nan")
    return float(np.log(n) / np.log(avg_dist + 1.0))


def compute_diagnostics(
    g: nx.Graph,
    embedding_dims: List[int],
    random_state: int,
    disconnected_policy: str,
) -> Dict[str, Any]:
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


# -----------------------------
# Comparison and summaries
# -----------------------------

def classify_position(
    observed_value: float,
    control_values: np.ndarray,
    metric_name: str,
    directional_metrics: Dict[str, str],
    tie_tol: float,
    all_zero_label: str,
) -> str:
    vals = control_values[np.isfinite(control_values)]
    if not np.isfinite(observed_value) or vals.size == 0:
        return "not_directional"

    direction = directional_metrics.get(metric_name, directional_metrics.get(metric_name.split("_")[0], "not_directional"))
    if direction == "not_directional":
        return "not_directional"

    vmin = float(np.min(vals))
    vmax = float(np.max(vals))

    if abs(observed_value) <= tie_tol and abs(vmin) <= tie_tol and abs(vmax) <= tie_tol:
        return all_zero_label

    if vmin - tie_tol <= observed_value <= vmax + tie_tol:
        return "observed_within_geometry_control_range"

    if direction == "lower_is_more_geometry_like":
        if observed_value < vmin - tie_tol:
            return "observed_more_geometry_like_than_geometry_controls"
        if observed_value > vmax + tie_tol:
            return "observed_less_geometry_like_than_geometry_controls"

    if direction == "higher_is_more_geometry_like":
        if observed_value > vmax + tie_tol:
            return "observed_more_geometry_like_than_geometry_controls"
        if observed_value < vmin - tie_tol:
            return "observed_less_geometry_like_than_geometry_controls"

    return "observed_outside_geometry_control_range"


def metric_columns(df: pd.DataFrame) -> List[str]:
    prefixes = [
        "triangle_defects",
        "negative_eigenvalue_burden",
        "negative_eigenvalue_count",
        "geodesic_consistency_error",
        "local_dimension_proxy",
        "embedding_stress_",
    ]
    cols = []
    for c in df.columns:
        if any(c == p or c.startswith(p) for p in prefixes):
            cols.append(c)
    return cols


def summarize_family(metrics_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    mcols = metric_columns(metrics_df)
    group_cols = ["observed_object", "control_family", "dimension", "weight_mode"]

    for keys, sub in metrics_df.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, keys))
        base["n_replicates"] = int(len(sub))
        base["connected_rate"] = float(sub["is_connected"].mean()) if "is_connected" in sub else float("nan")
        base["median_n_edges"] = float(sub["n_edges"].median()) if "n_edges" in sub else float("nan")
        for m in mcols:
            vals = pd.to_numeric(sub[m], errors="coerce")
            base[f"{m}_median"] = float(vals.median()) if vals.notna().any() else float("nan")
            base[f"{m}_iqr"] = float(vals.quantile(0.75) - vals.quantile(0.25)) if vals.notna().any() else float("nan")
            base[f"{m}_min"] = float(vals.min()) if vals.notna().any() else float("nan")
            base[f"{m}_max"] = float(vals.max()) if vals.notna().any() else float("nan")
        rows.append(base)
    return pd.DataFrame(rows)


def compare_observed_to_controls(
    observed_metrics: Dict[str, Dict[str, Any]],
    control_df: pd.DataFrame,
    config: Dict[str, Any],
) -> pd.DataFrame:
    tie_tol = float(config.get("labeling", {}).get("tie_tolerance", 1e-12))
    all_zero_label = str(config.get("labeling", {}).get("all_zero_tie_label", "observed_geometry_control_equivalent"))
    directional = dict(config.get("labeling", {}).get("directional_metrics", {}))

    rows = []
    mcols = metric_columns(control_df)
    group_cols = ["observed_object", "control_family", "dimension", "weight_mode"]

    for keys, sub in control_df.groupby(group_cols, dropna=False):
        observed_object = keys[0]
        obs = observed_metrics.get(observed_object, {})
        for m in mcols:
            obs_val = safe_float(obs.get(m, float("nan")))
            controls = pd.to_numeric(sub[m], errors="coerce").to_numpy(dtype=float)
            label = classify_position(obs_val, controls, m, directional, tie_tol, all_zero_label)
            finite = controls[np.isfinite(controls)]
            rows.append({
                "observed_object": observed_object,
                "control_family": keys[1],
                "dimension": keys[2],
                "weight_mode": keys[3],
                "metric": m,
                "observed_value": obs_val,
                "control_min": float(np.min(finite)) if finite.size else float("nan"),
                "control_median": float(np.median(finite)) if finite.size else float("nan"),
                "control_max": float(np.max(finite)) if finite.size else float("nan"),
                "control_n": int(finite.size),
                "position_label": label,
            })

    return pd.DataFrame(rows)


# -----------------------------
# Readout
# -----------------------------

def write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")


def write_readout(
    path: Path,
    config: Dict[str, Any],
    observed_objects: List[GraphObject],
    metrics_df: pd.DataFrame,
    family_df: pd.DataFrame,
    position_df: pd.DataFrame,
    warnings: List[str],
) -> None:
    lines = []
    lines.append("# BMC-15e Geometry-Control Nulls — Readout\n")
    lines.append(f"- Generated: `{now_iso()}`")
    lines.append(f"- Run ID: `{config.get('run_id', 'unknown')}`")
    lines.append(f"- Output directory: `{config.get('output', {}).get('output_dir', '')}`")
    lines.append("")
    lines.append("## Scope\n")
    lines.append("This is a geometry-proxy comparison against explicitly geometry-generated control graphs.")
    lines.append("It does not test physical spacetime emergence, causal structure, Lorentzian signature, or a physical metric.")
    lines.append("")
    lines.append("## Observed graph objects loaded\n")
    lines.append("| Object | Nodes | Edges | Connected |")
    lines.append("|---|---:|---:|---|")
    for obj in observed_objects:
        s = graph_summary(obj.graph)
        lines.append(f"| `{obj.name}` | {s['n_nodes']} | {s['n_edges']} | {s['is_connected']} |")
    lines.append("")
    lines.append("## Control metrics\n")
    lines.append(f"- Control metric rows: `{len(metrics_df)}`")
    lines.append(f"- Family summary rows: `{len(family_df)}`")
    lines.append(f"- Observed-position rows: `{len(position_df)}`")
    lines.append("")
    lines.append("## Position label counts\n")
    if not position_df.empty:
        counts = position_df["position_label"].value_counts().reset_index()
        counts.columns = ["position_label", "count"]
        lines.append("| Label | Count |")
        lines.append("|---|---:|")
        for _, r in counts.iterrows():
            lines.append(f"| `{r['position_label']}` | {int(r['count'])} |")
    else:
        lines.append("No position labels computed.")
    lines.append("")
    lines.append("## Warnings\n")
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Conservative interpretation template\n")
    lines.append("BMC-15e positions the observed relational graph objects against explicitly geometry-generated controls.")
    lines.append("Any similarity to geometry controls remains a geometry-proxy observation only.")
    lines.append("No physical geometry, causal structure, Lorentzian signature, or spacetime emergence is established.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------
# Main runner
# -----------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Run BMC-15e Geometry-Control Nulls MVP.")
    parser.add_argument(
        "--config",
        default="data/bmc15e_geometry_control_nulls_config.yaml",
        help="Path to YAML config.",
    )
    args = parser.parse_args()

    config_path = Path(args.config).expanduser()
    config = load_yaml(config_path)

    outdir = Path(config["output"]["output_dir"]).expanduser()
    ensure_dir(outdir)

    seed = int(config.get("random", {}).get("seed", config.get("random_seed", 15015)))
    n_reps = int(config.get("random", {}).get("n_replicates", config.get("n_replicates", 200)))
    max_attempts = int(config.get("random", {}).get("max_generation_attempts", 2000))
    embedding_dims = as_list(config.get("embedding", {}).get("dimensions", [2, 3, 4]))
    embedding_dims = [int(x) for x in embedding_dims]
    disconnected_policy = str(config.get("embedding", {}).get("disconnected_policy", "largest_component"))

    rng = np.random.default_rng(seed)

    warnings: List[str] = []
    if not SKLEARN_AVAILABLE:
        warnings.append("scikit-learn unavailable: embedding stress metrics will be NaN.")
    if not SCIPY_AVAILABLE:
        warnings.append("scipy unavailable: using networkx shortest paths fallback.")

    observed_objects = load_observed_graphs(config)

    # Observed diagnostics computed directly here for same-code comparison.
    observed_metrics: Dict[str, Dict[str, Any]] = {}
    for i, obj in enumerate(observed_objects):
        observed_metrics[obj.name] = compute_diagnostics(
            obj.graph,
            embedding_dims=embedding_dims,
            random_state=seed + 100000 + i * 100,
            disconnected_policy=disconnected_policy,
        )

    metric_rows: List[Dict[str, Any]] = []

    families = as_list(config.get("control_families", []))
    for fam in families:
        if not fam.get("enabled", False):
            continue
        family_name = str(fam.get("name", "unknown_family"))
        dims = [int(x) for x in as_list(fam.get("dimensions", [2]))]
        weight_modes = [str(x) for x in as_list(fam.get("weight_modes", ["unweighted"]))]
        matching = fam.get("matching", {}) or {}
        prefer_connected = str(matching.get("connected", "prefer_true")) == "prefer_true"
        params = fam.get("generator_params", {}) or {}

        for obj in observed_objects:
            for dim in dims:
                for weight_mode in weight_modes:
                    for rep in range(n_reps):
                        rep_seed = int(rng.integers(0, 2**31 - 1))
                        rep_rng = np.random.default_rng(rep_seed)

                        if family_name == "soft_geometric_kernel":
                            g_control, attempts, connected = make_connected_prefer(
                                soft_geometric_kernel_graph,
                                obj.graph,
                                dim,
                                weight_mode,
                                rep_rng,
                                max_attempts=max_attempts,
                                prefer_connected=prefer_connected,
                                kernel=str(params.get("kernel", "exp_negative_distance")),
                                scale_mode=str(params.get("scale_mode", "median_distance")),
                            )
                        elif family_name == "random_geometric_graph":
                            g_control, attempts, connected = make_connected_prefer(
                                random_geometric_graph_top_pairs,
                                obj.graph,
                                dim,
                                weight_mode,
                                rep_rng,
                                max_attempts=max_attempts,
                                prefer_connected=prefer_connected,
                            )
                        else:
                            warnings.append(f"Skipping unsupported control family: {family_name}")
                            continue

                        diag = compute_diagnostics(
                            g_control,
                            embedding_dims=embedding_dims,
                            random_state=rep_seed,
                            disconnected_policy=disconnected_policy,
                        )
                        row: Dict[str, Any] = {
                            "run_id": config.get("run_id", ""),
                            "observed_object": obj.name,
                            "control_family": family_name,
                            "dimension": dim,
                            "weight_mode": weight_mode,
                            "replicate": rep,
                            "replicate_seed": rep_seed,
                            "generation_attempts": attempts,
                            "connected_after_generation": connected,
                        }
                        row.update(diag)
                        metric_rows.append(row)

    metrics_df = pd.DataFrame(metric_rows)
    family_df = summarize_family(metrics_df) if not metrics_df.empty else pd.DataFrame()
    position_df = compare_observed_to_controls(observed_metrics, metrics_df, config) if not metrics_df.empty else pd.DataFrame()

    # Write outputs
    metrics_path = outdir / "geometry_control_metrics.csv"
    family_path = outdir / "family_summary.csv"
    position_path = outdir / "observed_position_summary.csv"
    summary_path = outdir / "summary.json"
    readout_path = outdir / "readout.md"

    metrics_df.to_csv(metrics_path, index=False)
    family_df.to_csv(family_path, index=False)
    position_df.to_csv(position_path, index=False)

    summary = {
        "run_id": config.get("run_id", ""),
        "generated_at": now_iso(),
        "config_path": str(config_path),
        "output_dir": str(outdir),
        "n_observed_objects_loaded": len(observed_objects),
        "observed_objects": [
            {"name": obj.name, **graph_summary(obj.graph)}
            for obj in observed_objects
        ],
        "n_control_metric_rows": int(len(metrics_df)),
        "n_family_summary_rows": int(len(family_df)),
        "n_observed_position_rows": int(len(position_df)),
        "sklearn_available": SKLEARN_AVAILABLE,
        "scipy_available": SCIPY_AVAILABLE,
        "warnings": sorted(set(warnings)),
        "claim_boundary": (
            "Geometry-proxy comparison only. No physical geometry, causal structure, "
            "Lorentzian signature, or spacetime emergence is established."
        ),
    }
    write_json(summary_path, summary)
    write_readout(readout_path, config, observed_objects, metrics_df, family_df, position_df, sorted(set(warnings)))

    print("BMC-15e Geometry-Control Nulls complete.")
    print(f"Output directory: {outdir}")
    print(f"Metrics: {metrics_path}")
    print(f"Family summary: {family_path}")
    print(f"Observed position summary: {position_path}")
    print(f"Summary: {summary_path}")
    print(f"Readout: {readout_path}")
    if warnings:
        print("Warnings:")
        for w in sorted(set(warnings)):
            print(f"  - {w}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
