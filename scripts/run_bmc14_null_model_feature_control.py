#!/usr/bin/env python3
"""
BMC-14 Null-Model / Randomized Feature-Control Runner.

This runner tests whether the observed BMC-13a N=81 six-edge reference core
reappears under feature-randomized null controls.

It is deliberately conservative:
- no physical interpretation is inferred;
- results are empirical diagnostics;
- p-like values are descriptive, not formal proof.

Null models:
A) featurewise_permutation
B) rowwise_vector_permutation
C) family_preserving_row_permutation
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from collections import defaultdict, deque
from pathlib import Path
from statistics import mean, median, pstdev
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


def edge_set(rows: Sequence[Dict[str, Any]]) -> Set[Edge]:
    return {edge_key(r) for r in rows}


def safe_float(value: Any, *, field: str) -> float:
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(f"Could not parse numeric field {field!r}: {value!r}") from exc
    if not math.isfinite(x):
        raise ValueError(f"Non-finite numeric field {field!r}: {value!r}")
    return x


def load_observed_core(path: Path, method_id: str) -> Set[Edge]:
    rows = read_csv(path)
    selected = [r for r in rows if r.get("method_id") == method_id]
    if not selected:
        raise ValueError(f"No observed core edges found for method_id={method_id!r} in {path}")
    return edge_set(selected)


def standardize_feature_rows(rows: Sequence[Dict[str, Any]], feature_cols: Sequence[str]) -> List[Dict[str, Any]]:
    means: Dict[str, float] = {}
    stds: Dict[str, float] = {}

    for col in feature_cols:
        vals = [safe_float(r[col], field=col) for r in rows]
        mu = sum(vals) / len(vals)
        var = sum((x - mu) ** 2 for x in vals) / len(vals)
        sd = math.sqrt(var)
        if sd == 0:
            sd = 1.0
        means[col] = mu
        stds[col] = sd

    out: List[Dict[str, Any]] = []
    for r in rows:
        nr = dict(r)
        for col in feature_cols:
            nr[f"z__{col}"] = (safe_float(r[col], field=col) - means[col]) / stds[col]
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
                da = float(z_rows[i][f"z__{col}"])
                db = float(z_rows[j][f"z__{col}"])
                dist2 += (da - db) ** 2
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
    return [dict(e) for e in edges[:k]]


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
        vals_sorted = sorted(vals, key=lambda x: (-x[1], x[0]))
        top_sets[node] = {n for n, _ in vals_sorted[:k]}

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


def permute_featurewise(rows: Sequence[Dict[str, str]], feature_cols: Sequence[str], rng: random.Random) -> List[Dict[str, Any]]:
    out = [dict(r) for r in rows]
    for col in feature_cols:
        vals = [r[col] for r in rows]
        rng.shuffle(vals)
        for r, v in zip(out, vals):
            r[col] = v
    return out


def permute_rowwise(rows: Sequence[Dict[str, str]], feature_cols: Sequence[str], rng: random.Random) -> List[Dict[str, Any]]:
    vectors = [{col: r[col] for col in feature_cols} for r in rows]
    rng.shuffle(vectors)
    out = [dict(r) for r in rows]
    for r, vec in zip(out, vectors):
        for col in feature_cols:
            r[col] = vec[col]
    return out


def permute_family_preserving(rows: Sequence[Dict[str, str]], feature_cols: Sequence[str], family_col: str, rng: random.Random) -> List[Dict[str, Any]]:
    out = [dict(r) for r in rows]
    indices_by_family: Dict[str, List[int]] = defaultdict(list)
    for idx, r in enumerate(rows):
        indices_by_family[str(r[family_col])].append(idx)

    for _, indices in indices_by_family.items():
        vectors = [{col: rows[idx][col] for col in feature_cols} for idx in indices]
        rng.shuffle(vectors)
        for idx, vec in zip(indices, vectors):
            for col in feature_cols:
                out[idx][col] = vec[col]
    return out


def make_null_rows(null_model_id: str, rows: Sequence[Dict[str, str]], feature_cols: Sequence[str], family_col: str, rng: random.Random) -> List[Dict[str, Any]]:
    if null_model_id == "featurewise_permutation":
        return permute_featurewise(rows, feature_cols, rng)
    if null_model_id == "rowwise_vector_permutation":
        return permute_rowwise(rows, feature_cols, rng)
    if null_model_id == "family_preserving_row_permutation":
        return permute_family_preserving(rows, feature_cols, family_col, rng)
    raise ValueError(f"Unknown null model: {null_model_id}")


def quantile(vals: Sequence[float], q: float) -> float:
    if not vals:
        return 0.0
    xs = sorted(vals)
    pos = q * (len(xs) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1.0 - frac) + xs[hi] * frac


def p_like_upper(null_vals: Sequence[float], observed_value: float) -> float:
    return (1 + sum(1 for x in null_vals if x >= observed_value)) / (len(null_vals) + 1)


def summarize_distribution(null_model_id: str, metric: str, vals: Sequence[float], observed_value: float) -> Dict[str, Any]:
    vals_list = [float(v) for v in vals]
    return {
        "null_model_id": null_model_id,
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
    lines.append("# BMC-14 Null-Model Feature-Control Readout")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- replicates per null model: `{replicate_count}`")
    lines.append("- focus: observed BMC-13a six-edge N=81 reference core")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append("| null_model_id | metric | null_mean | null_median | null_q95 | null_max | p_like_upper_tail |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for r in distribution_rows:
        lines.append(
            "| {model} | {metric} | {mean:.3f} | {med:.3f} | {q95:.3f} | {mx:.3f} | {p:.3f} |".format(
                model=r["null_model_id"],
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
    lines.append(
        "Low observed-core recovery under nulls supports data-specificity of the observed reference core. "
        "High null-core self-containment indicates that core-in-envelope behavior can be pipeline-generic."
    )
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(
        "If the observed six-edge core is rarely recovered under feature-randomized controls, it may represent a specific relational structure within the tested graph-method pipeline."
    )
    lines.append("")
    lines.append("## Open gap")
    lines.append("")
    lines.append(
        "BMC-14 remains a null-model graph diagnostic. It does not establish physical spacetime emergence, causal geometry, or continuum reconstruction."
    )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMC-14 null-model feature-control diagnostics.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    cfg = load_yaml(project_path(root, args.config))

    feature_table = project_path(root, cfg["inputs"]["feature_table_csv"])
    observed_core_path = project_path(root, cfg["inputs"]["observed_core_edges_csv"])
    output_root = project_path(root, cfg["outputs"]["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    id_col = cfg["features"]["id_column"]
    family_col = cfg["features"]["family_column"]
    feature_cols = list(cfg["features"]["feature_columns"])

    edge_count_target = int(cfg["reference"]["edge_count_target"])
    core_edge_count = int(cfg["reference"]["core_edge_count"])
    observed_core_method_id = str(cfg["reference"]["observed_core_method_id"])

    replicate_count = int(cfg["replicates"]["count"])
    seed_base = int(cfg["replicates"]["random_seed_base"])

    input_rows = read_csv(feature_table)
    observed_core = load_observed_core(observed_core_path, observed_core_method_id)
    observed_core_size = len(observed_core)
    if observed_core_size != core_edge_count:
        raise ValueError(f"Observed core size {observed_core_size} differs from config core_edge_count {core_edge_count}")

    null_models = [
        name for name, spec in cfg["null_models"].items()
        if bool(spec.get("enabled", True))
    ]

    method_specs = cfg["methods"]
    method_containment_rows: List[Dict[str, Any]] = []
    replicate_rows: List[Dict[str, Any]] = []

    for null_model_index, null_model_id in enumerate(null_models):
        for rep in range(replicate_count):
            seed = seed_base + null_model_index * 100000 + rep
            rng = random.Random(seed)

            null_rows = make_null_rows(null_model_id, input_rows, feature_cols, family_col, rng)
            all_edges = build_edge_table(null_rows, id_col, feature_cols)
            top_n_edges = select_top_n(all_edges, edge_count_target)
            null_core_rows = select_top_strength(top_n_edges, core_edge_count)
            null_core = edge_set(null_core_rows)

            shared_obs_core = len(observed_core & null_core)
            obs_jac = jaccard(observed_core, null_core)
            obs_recovery = shared_obs_core / observed_core_size if observed_core_size else 0.0
            core_mean, core_min, core_max = weights_summary(null_core_rows)

            replicate_rows.append({
                "replicate_id": rep,
                "null_model_id": null_model_id,
                "random_seed": seed,
                "edge_count_target": edge_count_target,
                "core_edge_count": core_edge_count,
                "observed_core_shared_edges": shared_obs_core,
                "observed_core_jaccard": obs_jac,
                "observed_core_recovery_fraction": obs_recovery,
                "null_core_mean_weight": core_mean,
                "null_core_min_weight": core_min,
                "null_core_max_weight": core_max,
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
                method_edges = edge_set(mrows)
                obs_overlap = len(observed_core & method_edges)
                null_overlap = len(null_core & method_edges)
                mmean, mmin, mmax = weights_summary(mrows)
                node_count, component_count, largest_component_size = graph_components(mrows)

                method_containment_rows.append({
                    "replicate_id": rep,
                    "null_model_id": null_model_id,
                    "random_seed": seed,
                    "method_id": method_id,
                    "method_edge_count": len(method_edges),
                    "method_node_count": node_count,
                    "method_component_count": component_count,
                    "method_largest_component_size": largest_component_size,
                    "observed_core_overlap": obs_overlap,
                    "observed_core_containment_in_null": obs_overlap / observed_core_size if observed_core_size else 0.0,
                    "null_core_overlap": null_overlap,
                    "null_core_self_containment": null_overlap / len(null_core) if null_core else 0.0,
                    "method_mean_weight": mmean,
                    "method_min_weight": mmin,
                    "method_max_weight": mmax,
                })

    distribution_rows: List[Dict[str, Any]] = []

    replicate_metrics = [
        "observed_core_shared_edges",
        "observed_core_jaccard",
        "observed_core_recovery_fraction",
    ]
    for null_model_id in null_models:
        rows = [r for r in replicate_rows if r["null_model_id"] == null_model_id]
        for metric in replicate_metrics:
            vals = [float(r[metric]) for r in rows]
            observed_value = 1.0 if metric in ("observed_core_jaccard", "observed_core_recovery_fraction") else float(core_edge_count)
            distribution_rows.append(summarize_distribution(null_model_id, metric, vals, observed_value))

    method_metrics = [
        "observed_core_containment_in_null",
        "null_core_self_containment",
    ]
    for null_model_id in null_models:
        model_rows = [r for r in method_containment_rows if r["null_model_id"] == null_model_id]
        method_ids = sorted({str(r["method_id"]) for r in model_rows})
        for method_id in method_ids:
            rows = [r for r in model_rows if r["method_id"] == method_id]
            for metric in method_metrics:
                vals = [float(r[metric]) for r in rows]
                distribution_rows.append(summarize_distribution(f"{null_model_id}::{method_id}", metric, vals, 1.0))

    replicate_out = output_root / "bmc14_null_replicate_summary.csv"
    method_out = output_root / "bmc14_null_method_containment_summary.csv"
    dist_out = output_root / "bmc14_null_distribution_summary.csv"
    readout_out = output_root / "bmc14_readout.md"
    metrics_out = output_root / "bmc14_metrics.json"

    write_csv(
        replicate_out,
        replicate_rows,
        [
            "replicate_id",
            "null_model_id",
            "random_seed",
            "edge_count_target",
            "core_edge_count",
            "observed_core_shared_edges",
            "observed_core_jaccard",
            "observed_core_recovery_fraction",
            "null_core_mean_weight",
            "null_core_min_weight",
            "null_core_max_weight",
        ],
    )
    write_csv(
        method_out,
        method_containment_rows,
        [
            "replicate_id",
            "null_model_id",
            "random_seed",
            "method_id",
            "method_edge_count",
            "method_node_count",
            "method_component_count",
            "method_largest_component_size",
            "observed_core_overlap",
            "observed_core_containment_in_null",
            "null_core_overlap",
            "null_core_self_containment",
            "method_mean_weight",
            "method_min_weight",
            "method_max_weight",
        ],
    )
    write_csv(
        dist_out,
        distribution_rows,
        [
            "null_model_id",
            "metric",
            "replicate_count",
            "observed_value",
            "null_mean",
            "null_std",
            "null_min",
            "null_q05",
            "null_median",
            "null_q95",
            "null_max",
            "p_like_upper_tail",
        ],
    )
    write_readout(readout_out, distribution_rows, replicate_count)

    metrics = {
        "run_id": cfg.get("run_id", "BMC14_null_model_feature_control_open"),
        "feature_table": str(feature_table),
        "observed_core_edges": str(observed_core_path),
        "output_root": str(output_root),
        "null_models": null_models,
        "replicate_count_per_null_model": replicate_count,
        "edge_count_target": edge_count_target,
        "core_edge_count": core_edge_count,
        "observed_core_size": observed_core_size,
        "replicate_rows": len(replicate_rows),
        "method_containment_rows": len(method_containment_rows),
        "distribution_rows": len(distribution_rows),
    }
    metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-14 null-model feature-control completed.")
    print(f"Wrote: {replicate_out}")
    print(f"Wrote: {method_out}")
    print(f"Wrote: {dist_out}")
    print(f"Wrote: {readout_out}")
    print(f"Wrote: {metrics_out}")


if __name__ == "__main__":
    main()
