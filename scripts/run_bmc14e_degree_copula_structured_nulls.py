#!/usr/bin/env python3
"""
BMC-14e Degree-Preserving / Copula Structured Nulls Runner.

Null models:
1. degree_preserving_edge_rewire
2. degree_weightclass_edge_rewire
3. gaussian_copula_feature_null

Purpose:
Test whether the observed BMC-13a six-edge N=81 core can be reproduced by
degree/hub-preserving graph nulls or rank/correlation-preserving feature nulls.

No physical interpretation is inferred by this script.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import Counter, defaultdict, deque
from pathlib import Path
from statistics import mean, median, pstdev
from typing import Any, Dict, List, Sequence, Set, Tuple

import numpy as np
from statistics import NormalDist

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


def edge_set(rows: Sequence[Dict[str, Any]]) -> Set[Edge]:
    return {edge_key(r) for r in rows}


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


def load_observed_core(path: Path, method_id: str) -> Set[Edge]:
    rows = read_csv(path)
    selected = [r for r in rows if r.get("method_id") == method_id]
    if not selected:
        raise ValueError(f"No observed core edges found for method_id={method_id!r} in {path}")
    return edge_set(selected)


def filter_inventory_rows(rows: Sequence[Dict[str, str]], edge_count: int, case_id: str) -> List[Dict[str, Any]]:
    out = [
        dict(r)
        for r in rows
        if as_int(r["edge_count_target"]) == edge_count and str(r["case_id"]) == case_id
    ]
    if not out:
        raise ValueError(f"No observed inventory rows for edge_count={edge_count}, case_id={case_id}")
    out.sort(key=lambda r: (-as_float(r["weight"], "weight"), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(out, start=1):
        row["edge_rank"] = rank
    return out


def matrix_from_rows(rows: Sequence[Dict[str, Any]], feature_cols: Sequence[str]) -> np.ndarray:
    return np.array([[as_float(r[col], col) for col in feature_cols] for r in rows], dtype=float)


def rows_with_feature_matrix(template_rows: Sequence[Dict[str, Any]], feature_cols: Sequence[str], X: np.ndarray) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row, vals in zip(template_rows, X):
        nr = dict(row)
        for col, value in zip(feature_cols, vals):
            nr[col] = float(value)
        out.append(nr)
    return out


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
    return float(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac)


def nearest_psd_corr(corr: np.ndarray, ridge: float) -> np.ndarray:
    corr = np.array(corr, dtype=float)
    corr = (corr + corr.T) / 2.0
    corr = corr + np.eye(corr.shape[0]) * ridge
    vals, vecs = np.linalg.eigh(corr)
    vals = np.maximum(vals, ridge)
    corr_psd = (vecs * vals) @ vecs.T
    d = np.sqrt(np.diag(corr_psd))
    corr_psd = corr_psd / np.outer(d, d)
    corr_psd = (corr_psd + corr_psd.T) / 2.0
    return corr_psd


def generate_gaussian_copula_rows(
    rows: Sequence[Dict[str, Any]],
    feature_cols: Sequence[str],
    seed: int,
    ridge: float,
    clip: bool,
) -> Tuple[List[Dict[str, Any]], str]:
    rng = np.random.default_rng(seed)
    nd = NormalDist()
    X = matrix_from_rows(rows, feature_cols)
    n, p = X.shape

    Z = np.zeros((n, p), dtype=float)
    sorted_cols: List[np.ndarray] = []
    for j in range(p):
        col = X[:, j]
        ranks = rankdata_average(col)
        u = (ranks - 0.5) / n
        u = np.clip(u, 1e-6, 1 - 1e-6)
        Z[:, j] = np.array([nd.inv_cdf(float(x)) for x in u])
        sorted_cols.append(np.sort(col))

    corr = nearest_psd_corr(np.corrcoef(Z, rowvar=False), ridge)
    Zn = rng.multivariate_normal(np.zeros(p), corr, size=n)
    Xn = np.zeros_like(Zn)
    for j in range(p):
        u = np.array([nd.cdf(float(z)) for z in Zn[:, j]])
        Xn[:, j] = np.array([empirical_quantile(sorted_cols[j], float(x)) for x in u])

    if clip:
        mins = X.min(axis=0)
        maxs = X.max(axis=0)
        Xn = np.minimum(np.maximum(Xn, mins), maxs)

    return rows_with_feature_matrix(rows, feature_cols, Xn), "ok"


def standardize_feature_rows(rows: Sequence[Dict[str, Any]], feature_cols: Sequence[str]) -> List[Dict[str, Any]]:
    means: Dict[str, float] = {}
    stds: Dict[str, float] = {}
    for col in feature_cols:
        vals = [as_float(r[col], col) for r in rows]
        mu = sum(vals) / len(vals)
        var = sum((x - mu) ** 2 for x in vals) / len(vals)
        sd = math.sqrt(var) if var > 0 else 1.0
        means[col] = mu
        stds[col] = sd

    out: List[Dict[str, Any]] = []
    for row in rows:
        nr = dict(row)
        for col in feature_cols:
            nr[f"z__{col}"] = (as_float(row[col], col) - means[col]) / stds[col]
        out.append(nr)
    return out


def build_edge_table(rows: Sequence[Dict[str, Any]], id_col: str, feature_cols: Sequence[str]) -> List[Dict[str, Any]]:
    z_rows = standardize_feature_rows(rows, feature_cols)
    edges: List[Dict[str, Any]] = []
    for i in range(len(z_rows)):
        for j in range(i + 1, len(z_rows)):
            a = str(z_rows[i][id_col])
            b = str(z_rows[j][id_col])
            dist2 = 0.0
            for col in feature_cols:
                dist2 += (float(z_rows[i][f"z__{col}"]) - float(z_rows[j][f"z__{col}"])) ** 2
            dist = math.sqrt(dist2)
            weight = 1.0 / (1.0 + dist)
            edges.append({"source": a, "target": b, "distance": dist, "weight": weight})
    edges.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, edge in enumerate(edges, start=1):
        edge["edge_rank"] = rank
    return edges


def select_top_n(edges: Sequence[Dict[str, Any]], n: int) -> List[Dict[str, Any]]:
    return [dict(e) for e in edges[:n]]


def select_top_strength(edges: Sequence[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    ordered = sorted(edges, key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    return [dict(e) for e in ordered[:k]]


def observed_degrees(edges: Sequence[Dict[str, Any]]) -> Counter:
    deg = Counter()
    for row in edges:
        deg[str(row["source"])] += 1
        deg[str(row["target"])] += 1
    return deg


def double_edge_rewire(
    observed_edges: Sequence[Dict[str, Any]],
    seed: int,
    swap_multiplier: int,
    max_attempt_multiplier: int,
) -> Tuple[List[Edge], Dict[str, Any]]:
    rng = random.Random(seed)
    edges: Set[Edge] = {edge_key(r) for r in observed_edges}
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
            n1 = norm_edge(a, d)
            n2 = norm_edge(c, b)
        else:
            n1 = norm_edge(a, c)
            n2 = norm_edge(b, d)

        if n1[0] == n1[1] or n2[0] == n2[1] or n1 == n2:
            duplicate_or_self += 1
            continue

        if n1 in edges or n2 in edges:
            duplicate_or_self += 1
            continue

        edges.remove(e1)
        edges.remove(e2)
        edges.add(n1)
        edges.add(n2)
        edge_list = list(edges)
        successful += 1

    failed = attempts - successful
    return list(edges), {
        "attempted_swaps": attempts,
        "successful_swaps": successful,
        "failed_swaps": failed,
        "swap_success_fraction": successful / attempts if attempts else 0.0,
        "duplicate_or_self_loop_rejections": duplicate_or_self,
    }


def assign_weights_shuffled(edges: Sequence[Edge], observed_edges: Sequence[Dict[str, Any]], rng: random.Random) -> List[Dict[str, Any]]:
    weights = [as_float(r["weight"], "weight") for r in observed_edges]
    rng.shuffle(weights)
    rows: List[Dict[str, Any]] = []
    for edge, weight in zip(edges, weights):
        rows.append({"source": edge[0], "target": edge[1], "distance": "", "weight": weight})
    rows.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(rows, start=1):
        row["edge_rank"] = rank
    return rows


def assign_weights_ranked(edges: Sequence[Edge], observed_edges: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    weights = sorted([as_float(r["weight"], "weight") for r in observed_edges], reverse=True)
    edges_sorted = sorted(edges)
    rows: List[Dict[str, Any]] = []
    for edge, weight in zip(edges_sorted, weights):
        rows.append({"source": edge[0], "target": edge[1], "distance": "", "weight": weight})
    rows.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(rows, start=1):
        row["edge_rank"] = rank
    return rows


def assign_weights_weightclass(edges: Sequence[Edge], observed_edges: Sequence[Dict[str, Any]], rng: random.Random, classes: int) -> List[Dict[str, Any]]:
    # Degree structure is preserved by rewiring. Weight classes are preserved as counts in the weight pool.
    # Assignment remains random across rewired edges, but weights are shuffled in class blocks.
    weights = sorted([as_float(r["weight"], "weight") for r in observed_edges], reverse=True)
    classes = max(1, int(classes))
    blocks: List[List[float]] = []
    n = len(weights)
    for c in range(classes):
        lo = int(round(c * n / classes))
        hi = int(round((c + 1) * n / classes))
        block = weights[lo:hi]
        rng.shuffle(block)
        blocks.append(block)
    shuffled_weights = [w for block in blocks for w in block]
    rng.shuffle(shuffled_weights)
    rows: List[Dict[str, Any]] = []
    for edge, weight in zip(edges, shuffled_weights):
        rows.append({"source": edge[0], "target": edge[1], "distance": "", "weight": weight})
    rows.sort(key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for rank, row in enumerate(rows, start=1):
        row["edge_rank"] = rank
    return rows


def generate_degree_rewire_edges(
    observed_edges: Sequence[Dict[str, Any]],
    seed: int,
    swap_multiplier: int,
    max_attempt_multiplier: int,
    weight_assignment: str,
    weight_classes: int = 4,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any], str]:
    rng = random.Random(seed + 991)
    rewired_edges, diag = double_edge_rewire(observed_edges, seed, swap_multiplier, max_attempt_multiplier)

    if weight_assignment == "rank_assign_weights":
        rows = assign_weights_ranked(rewired_edges, observed_edges)
    elif weight_assignment == "weightclass_shuffle":
        rows = assign_weights_weightclass(rewired_edges, observed_edges, rng, weight_classes)
    else:
        rows = assign_weights_shuffled(rewired_edges, observed_edges, rng)

    orig_deg = observed_degrees(observed_edges)
    new_deg = Counter()
    for e in rewired_edges:
        new_deg[e[0]] += 1
        new_deg[e[1]] += 1

    edge_count_preserved = len(rewired_edges) == len(observed_edges)
    degree_preserved = orig_deg == new_deg
    warning = ""
    if not edge_count_preserved:
        warning += "edge_count_not_preserved;"
    if not degree_preserved:
        warning += "degree_sequence_not_preserved;"
    if diag["successful_swaps"] < max(1, len(observed_edges)):
        warning += "low_swap_count;"

    diag.update({
        "edge_count_preserved": str(edge_count_preserved).lower(),
        "degree_sequence_preserved": str(degree_preserved).lower(),
        "warning_message": warning,
    })
    return rows, diag, warning if warning else "ok"


def select_mutual_knn(rows: Sequence[Dict[str, Any]], k: int) -> List[Dict[str, Any]]:
    neighbors: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
    row_by_edge: Dict[Edge, Dict[str, Any]] = {}
    ordered = sorted(rows, key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
    for row in ordered:
        a, b, w = str(row["source"]), str(row["target"]), float(row["weight"])
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

    return sorted([row_by_edge[e] for e in selected], key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))


def select_maximum_spanning_tree(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ordered = sorted(rows, key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])))
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
    return len(nodes), len(sizes), max(sizes) if sizes else 0


def weights_summary(rows: Sequence[Dict[str, Any]]) -> Tuple[float, float, float]:
    vals = [float(r["weight"]) for r in rows]
    if not vals:
        return 0.0, 0.0, 0.0
    return sum(vals) / len(vals), min(vals), max(vals)


def jaccard(a: Set[Edge], b: Set[Edge]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def quantile(vals: Sequence[float], q: float) -> float:
    xs = sorted(float(v) for v in vals)
    if not xs:
        return 0.0
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def p_like_upper(null_vals: Sequence[float], observed_value: float) -> float:
    return (1 + sum(1 for x in null_vals if x >= observed_value)) / (len(null_vals) + 1)


def summarize_distribution(null_model_id: str, null_family: str, metric: str, vals: Sequence[float], observed_value: float) -> Dict[str, Any]:
    vals_list = [float(v) for v in vals]
    return {
        "null_model_id": null_model_id,
        "null_family": null_family,
        "metric": metric,
        "replicate_count": len(vals_list),
        "observed_value": observed_value,
        "null_mean": mean(vals_list) if vals_list else 0.0,
        "null_std": pstdev(vals_list) if len(vals_list) > 1 else 0.0,
        "null_min": min(vals_list) if vals_list else 0.0,
        "null_q05": quantile(vals_list, 0.05),
        "null_median": median(vals_list) if vals_list else 0.0,
        "null_q95": quantile(vals_list, 0.95),
        "null_max": max(vals_list) if vals_list else 0.0,
        "p_like_upper_tail": p_like_upper(vals_list, observed_value),
    }


def write_readout(path: Path, distribution_rows: Sequence[Dict[str, Any]], replicate_count: int) -> None:
    lines: List[str] = []
    lines.append("# BMC-14e Degree-Preserving / Copula Structured Nulls Readout")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- replicates per null model: `{replicate_count}`")
    lines.append("- focus: observed BMC-13a six-edge N=81 reference core")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append("| null_model_id | null_family | metric | null_mean | null_median | null_q95 | null_max | p_like_upper_tail |")
    lines.append("|---|---|---|---:|---:|---:|---:|---:|")
    for r in distribution_rows:
        lines.append(
            "| {model} | {family} | {metric} | {mean:.3f} | {med:.3f} | {q95:.3f} | {mx:.3f} | {p:.3f} |".format(
                model=r["null_model_id"],
                family=r["null_family"],
                metric=r["metric"],
                mean=float(r["null_mean"]),
                med=float(r["null_median"]),
                q95=float(r["null_q95"]),
                mx=float(r["null_max"]),
                p=float(r["p_like_upper_tail"]),
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("BMC-14e tests whether the observed core can be explained by degree/hub structure or by rank-correlation feature structure.")
    lines.append("")
    lines.append("## Open gap")
    lines.append("")
    lines.append("This remains a structured null-model diagnostic. It does not establish physical spacetime emergence, causal geometry, or continuum reconstruction.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMC-14e degree/coplay structured null controls.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    cfg = load_yaml(project_path(root, args.config))

    feature_table = project_path(root, cfg["inputs"]["feature_table_csv"])
    observed_core_path = project_path(root, cfg["inputs"]["observed_core_edges_csv"])
    observed_inventory_path = project_path(root, cfg["inputs"]["observed_edge_inventory_csv"])
    output_root = project_path(root, cfg["outputs"]["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    id_col = cfg["features"]["id_column"]
    feature_cols = list(cfg["features"]["feature_columns"])

    edge_count_target = int(cfg["reference"]["edge_count_target"])
    core_edge_count = int(cfg["reference"]["core_edge_count"])
    observed_case_id = str(cfg["reference"]["observed_case_id"])
    observed_core_method_id = str(cfg["reference"]["observed_core_method_id"])

    replicate_count = int(cfg["replicates"]["count"])
    seed_base = int(cfg["replicates"]["random_seed_base"])

    feature_rows = read_csv(feature_table)
    observed_core = load_observed_core(observed_core_path, observed_core_method_id)
    observed_core_size = len(observed_core)
    if observed_core_size != core_edge_count:
        raise ValueError(f"Observed core size {observed_core_size} differs from config core_edge_count {core_edge_count}")

    inventory_rows = read_csv(observed_inventory_path)
    observed_n81_edges = filter_inventory_rows(inventory_rows, edge_count_target, observed_case_id)

    null_specs = cfg["null_models"]
    null_models: List[Tuple[str, str]] = []
    if null_specs["degree_preserving_edge_rewire"].get("enabled", True):
        null_models.append(("degree_preserving_edge_rewire", "degree_structured"))
    if null_specs["degree_weightclass_edge_rewire"].get("enabled", True):
        null_models.append(("degree_weightclass_edge_rewire", "degree_structured"))
    if null_specs["gaussian_copula_feature_null"].get("enabled", True):
        null_models.append(("gaussian_copula_feature_null", "copula_feature"))

    method_specs = cfg["methods"]
    replicate_rows: List[Dict[str, Any]] = []
    method_rows: List[Dict[str, Any]] = []
    rewire_diag_rows: List[Dict[str, Any]] = []

    for model_index, (null_model_id, null_family) in enumerate(null_models):
        for rep in range(replicate_count):
            seed = seed_base + model_index * 1000000 + rep
            status = "ok"
            warning = ""

            if null_model_id == "gaussian_copula_feature_null":
                spec = null_specs[null_model_id]
                null_feature_rows, warning = generate_gaussian_copula_rows(
                    feature_rows,
                    feature_cols,
                    seed,
                    float(spec.get("ridge", 1e-9)),
                    bool(spec.get("clip_to_observed_minmax", True)),
                )
                all_edges = build_edge_table(null_feature_rows, id_col, feature_cols)
                top_n_edges = select_top_n(all_edges, edge_count_target)

            elif null_model_id in ("degree_preserving_edge_rewire", "degree_weightclass_edge_rewire"):
                spec = null_specs[null_model_id]
                assignment = str(spec.get("weight_assignment", "shuffle_weights"))
                classes = int(spec.get("weight_classes", 4))
                top_n_edges, diag, warning = generate_degree_rewire_edges(
                    observed_n81_edges,
                    seed,
                    int(spec.get("swap_multiplier", 20)),
                    int(spec.get("max_attempt_multiplier", 200)),
                    assignment,
                    weight_classes=classes,
                )
                rewire_diag_rows.append({
                    "replicate_id": rep,
                    "null_model_id": null_model_id,
                    "random_seed": seed,
                    "attempted_swaps": diag["attempted_swaps"],
                    "successful_swaps": diag["successful_swaps"],
                    "failed_swaps": diag["failed_swaps"],
                    "swap_success_fraction": diag["swap_success_fraction"],
                    "duplicate_or_self_loop_rejections": diag["duplicate_or_self_loop_rejections"],
                    "edge_count_preserved": diag["edge_count_preserved"],
                    "degree_sequence_preserved": diag["degree_sequence_preserved"],
                    "warning_message": diag["warning_message"],
                })
            else:
                raise ValueError(f"Unknown null model: {null_model_id}")

            if warning and warning != "ok":
                status = "warning"

            null_core_rows = select_top_strength(top_n_edges, core_edge_count)
            null_core = edge_set(null_core_rows)
            shared = len(observed_core & null_core)
            cmean, cmin, cmax = weights_summary(null_core_rows)

            replicate_rows.append({
                "replicate_id": rep,
                "null_model_id": null_model_id,
                "random_seed": seed,
                "null_family": null_family,
                "edge_count_target": edge_count_target,
                "core_edge_count": core_edge_count,
                "observed_core_shared_edges": shared,
                "observed_core_jaccard": jaccard(observed_core, null_core),
                "observed_core_recovery_fraction": shared / observed_core_size if observed_core_size else 0.0,
                "null_core_mean_weight": cmean,
                "null_core_min_weight": cmin,
                "null_core_max_weight": cmax,
                "generation_status": status,
                "warning_message": warning if warning else "",
            })

            methods: Dict[str, List[Dict[str, Any]]] = {}
            if method_specs["top_strength_reference"].get("enabled", True):
                k = int(method_specs["top_strength_reference"].get("k_reference_edges", core_edge_count))
                methods["top_strength_reference"] = select_top_strength(top_n_edges, k)
            if method_specs["mutual_knn"].get("enabled", True):
                k = int(method_specs["mutual_knn"].get("k", 3))
                methods[f"mutual_kNN_k{k}"] = select_mutual_knn(top_n_edges, k)
            if method_specs["maximum_spanning_tree"].get("enabled", True):
                methods["maximum_spanning_tree"] = select_maximum_spanning_tree(top_n_edges)

            for method_id, mrows in methods.items():
                medges = edge_set(mrows)
                obs_overlap = len(observed_core & medges)
                null_overlap = len(null_core & medges)
                mmean, mmin, mmax = weights_summary(mrows)
                node_count, comp_count, largest = graph_components(mrows)
                method_rows.append({
                    "replicate_id": rep,
                    "null_model_id": null_model_id,
                    "random_seed": seed,
                    "null_family": null_family,
                    "method_id": method_id,
                    "method_edge_count": len(medges),
                    "method_node_count": node_count,
                    "method_component_count": comp_count,
                    "method_largest_component_size": largest,
                    "observed_core_overlap": obs_overlap,
                    "observed_core_containment_in_null": obs_overlap / observed_core_size if observed_core_size else 0.0,
                    "null_core_overlap": null_overlap,
                    "null_core_self_containment": null_overlap / len(null_core) if null_core else 0.0,
                    "method_mean_weight": mmean,
                    "method_min_weight": mmin,
                    "method_max_weight": mmax,
                })

    distribution_rows: List[Dict[str, Any]] = []

    replicate_metrics = ["observed_core_shared_edges", "observed_core_jaccard", "observed_core_recovery_fraction"]
    for null_model_id, null_family in null_models:
        rows = [r for r in replicate_rows if r["null_model_id"] == null_model_id]
        for metric in replicate_metrics:
            vals = [float(r[metric]) for r in rows]
            observed_value = float(core_edge_count) if metric == "observed_core_shared_edges" else 1.0
            distribution_rows.append(summarize_distribution(null_model_id, null_family, metric, vals, observed_value))

    method_metrics = ["observed_core_containment_in_null", "null_core_self_containment"]
    for null_model_id, null_family in null_models:
        model_rows = [r for r in method_rows if r["null_model_id"] == null_model_id]
        method_ids = sorted({str(r["method_id"]) for r in model_rows})
        for method_id in method_ids:
            rows = [r for r in model_rows if r["method_id"] == method_id]
            for metric in method_metrics:
                vals = [float(r[metric]) for r in rows]
                distribution_rows.append(summarize_distribution(f"{null_model_id}::{method_id}", null_family, metric, vals, 1.0))

    replicate_out = output_root / "bmc14e_null_replicate_summary.csv"
    method_out = output_root / "bmc14e_null_method_containment_summary.csv"
    dist_out = output_root / "bmc14e_null_distribution_summary.csv"
    rewire_out = output_root / "bmc14e_rewire_diagnostics.csv"
    readout_out = output_root / "bmc14e_readout.md"
    metrics_out = output_root / "bmc14e_metrics.json"

    write_csv(
        replicate_out,
        replicate_rows,
        [
            "replicate_id", "null_model_id", "random_seed", "null_family",
            "edge_count_target", "core_edge_count",
            "observed_core_shared_edges", "observed_core_jaccard", "observed_core_recovery_fraction",
            "null_core_mean_weight", "null_core_min_weight", "null_core_max_weight",
            "generation_status", "warning_message",
        ],
    )
    write_csv(
        method_out,
        method_rows,
        [
            "replicate_id", "null_model_id", "random_seed", "null_family",
            "method_id", "method_edge_count", "method_node_count", "method_component_count", "method_largest_component_size",
            "observed_core_overlap", "observed_core_containment_in_null",
            "null_core_overlap", "null_core_self_containment",
            "method_mean_weight", "method_min_weight", "method_max_weight",
        ],
    )
    write_csv(
        dist_out,
        distribution_rows,
        [
            "null_model_id", "null_family", "metric", "replicate_count", "observed_value",
            "null_mean", "null_std", "null_min", "null_q05", "null_median", "null_q95", "null_max", "p_like_upper_tail",
        ],
    )
    write_csv(
        rewire_out,
        rewire_diag_rows,
        [
            "replicate_id", "null_model_id", "random_seed", "attempted_swaps", "successful_swaps",
            "failed_swaps", "swap_success_fraction", "duplicate_or_self_loop_rejections",
            "edge_count_preserved", "degree_sequence_preserved", "warning_message",
        ],
    )
    write_readout(readout_out, distribution_rows, replicate_count)

    metrics = {
        "run_id": cfg.get("run_id", "BMC14e_degree_copula_structured_nulls_open"),
        "feature_table": str(feature_table),
        "observed_core_edges": str(observed_core_path),
        "observed_edge_inventory": str(observed_inventory_path),
        "output_root": str(output_root),
        "null_models": [{"id": n, "family": f} for n, f in null_models],
        "replicate_count_per_null_model": replicate_count,
        "edge_count_target": edge_count_target,
        "core_edge_count": core_edge_count,
        "observed_core_size": observed_core_size,
        "replicate_rows": len(replicate_rows),
        "method_containment_rows": len(method_rows),
        "rewire_diagnostic_rows": len(rewire_diag_rows),
        "distribution_rows": len(distribution_rows),
    }
    metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-14e degree-preserving / copula structured nulls completed.")
    print(f"Wrote: {replicate_out}")
    print(f"Wrote: {method_out}")
    print(f"Wrote: {dist_out}")
    print(f"Wrote: {rewire_out}")
    print(f"Wrote: {readout_out}")
    print(f"Wrote: {metrics_out}")


if __name__ == "__main__":
    main()
