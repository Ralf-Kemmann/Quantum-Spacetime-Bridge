\
#!/usr/bin/env python3
"""
BMC-15h — Structured Specificity Extension Runner

Purpose
-------
Compare the canonical BMC/N81-derived graph object against structured null
families and ask whether null objects reproduce the same compact-core and
envelope behavior seen in the BMC-15e/f/g line.

This runner is deliberately conservative:
  * it produces diagnostics, not proof-level conclusions;
  * it writes a manifest and warnings file;
  * it records missing optional inputs instead of silently pretending they exist;
  * it keeps all paths and parameters visible through a YAML config.

Install target:
  scripts/run_bmc15h_structured_specificity_extension.py

Typical usage:
  python scripts/run_bmc15h_structured_specificity_extension.py \
    --config data/bmc15h_structured_specificity_extension_config.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "Missing dependency: PyYAML. Install in the project venv, e.g. `pip install pyyaml`."
    ) from exc


Node = str
EdgeKey = Tuple[Node, Node]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def norm_edge(a: Any, b: Any) -> EdgeKey:
    sa, sb = str(a), str(b)
    if sa <= sb:
        return (sa, sb)
    return (sb, sa)


@dataclass(frozen=True)
class WeightedEdge:
    source: Node
    target: Node
    weight: float

    @property
    def key(self) -> EdgeKey:
        return norm_edge(self.source, self.target)


class WarningCollector:
    def __init__(self) -> None:
        self.rows: List[Dict[str, Any]] = []
        self._n = 0

    def add(
        self,
        severity: str,
        message: str,
        *,
        object_role: Optional[str] = None,
        null_family: Optional[str] = None,
        null_repeat: Optional[int] = None,
        construction_family: Optional[str] = None,
        affected_output: Optional[str] = None,
    ) -> None:
        self._n += 1
        self.rows.append(
            {
                "warning_id": f"W{self._n:05d}",
                "severity": severity,
                "object_role": object_role,
                "null_family": null_family,
                "null_repeat": null_repeat,
                "construction_family": construction_family,
                "message": message,
                "affected_output": affected_output,
            }
        )


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config did not parse as a YAML mapping: {path}")
    return data


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def resolve_path(repo_root: Path, maybe_path: Optional[str]) -> Optional[Path]:
    if maybe_path is None:
        return None
    p = Path(maybe_path).expanduser()
    if p.is_absolute():
        return p
    return repo_root / p


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv_dicts(path: Path, rows: List[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})


def parse_float(value: Any, *, fallback: Optional[float] = None) -> Optional[float]:
    if value is None or value == "":
        return fallback
    try:
        x = float(value)
        if math.isnan(x):
            return fallback
        return x
    except (TypeError, ValueError):
        return fallback


def load_weighted_edges(path: Path, columns: Dict[str, str]) -> List[WeightedEdge]:
    rows = read_csv_dicts(path)
    src_col = columns.get("source", "source")
    tgt_col = columns.get("target", "target")
    w_col = columns.get("weight", "weight")

    edges: Dict[EdgeKey, WeightedEdge] = {}
    missing = {src_col, tgt_col, w_col} - set(rows[0].keys() if rows else [])
    if missing:
        raise ValueError(f"{path} missing required columns: {sorted(missing)}")

    for r in rows:
        if not r.get(src_col) or not r.get(tgt_col):
            continue
        w = parse_float(r.get(w_col))
        if w is None:
            continue
        e = WeightedEdge(str(r[src_col]), str(r[tgt_col]), float(w))
        if e.source == e.target:
            continue
        # Keep the largest absolute weight if duplicate undirected edge occurs.
        old = edges.get(e.key)
        if old is None or abs(e.weight) > abs(old.weight):
            edges[e.key] = e
    return list(edges.values())


def load_edge_keys(path: Path, columns: Dict[str, str]) -> Set[EdgeKey]:
    rows = read_csv_dicts(path)
    src_col = columns.get("source", "source")
    tgt_col = columns.get("target", "target")
    if rows and (src_col not in rows[0] or tgt_col not in rows[0]):
        raise ValueError(f"{path} missing required columns: {src_col}, {tgt_col}")
    return {
        norm_edge(r[src_col], r[tgt_col])
        for r in rows
        if r.get(src_col) and r.get(tgt_col) and str(r[src_col]) != str(r[tgt_col])
    }


def load_node_families(path: Path, node_col: str, family_col: str) -> Dict[Node, str]:
    rows = read_csv_dicts(path)
    if rows and (node_col not in rows[0] or family_col not in rows[0]):
        raise ValueError(f"{path} missing columns needed for feature shuffle: {node_col}, {family_col}")
    out: Dict[Node, str] = {}
    for r in rows:
        if r.get(node_col):
            out[str(r[node_col])] = str(r.get(family_col, "UNKNOWN"))
    return out


def all_nodes(edges: Iterable[WeightedEdge]) -> Set[Node]:
    nodes: Set[Node] = set()
    for e in edges:
        nodes.add(e.source)
        nodes.add(e.target)
    return nodes


def edge_map(edges: Iterable[WeightedEdge]) -> Dict[EdgeKey, WeightedEdge]:
    return {e.key: e for e in edges}


def sorted_by_strength(edges: Iterable[WeightedEdge]) -> List[WeightedEdge]:
    return sorted(edges, key=lambda e: (-abs(e.weight), e.source, e.target))


def adjacency_from_edges(edge_keys: Iterable[EdgeKey]) -> Dict[Node, Set[Node]]:
    adj: Dict[Node, Set[Node]] = defaultdict(set)
    for a, b in edge_keys:
        if a == b:
            continue
        adj[a].add(b)
        adj[b].add(a)
    return adj


def connected_components(edge_keys: Iterable[EdgeKey], nodes: Optional[Set[Node]] = None) -> List[Set[Node]]:
    adj = adjacency_from_edges(edge_keys)
    all_n = set(nodes or set())
    all_n.update(adj.keys())
    seen: Set[Node] = set()
    comps: List[Set[Node]] = []
    for start in sorted(all_n):
        if start in seen:
            continue
        comp: Set[Node] = set()
        q: deque[Node] = deque([start])
        seen.add(start)
        while q:
            x = q.popleft()
            comp.add(x)
            for y in adj.get(x, set()):
                if y not in seen:
                    seen.add(y)
                    q.append(y)
        comps.append(comp)
    return comps


def graph_density(edge_count: int, node_count: int) -> float:
    denom = node_count * (node_count - 1) / 2
    return float(edge_count / denom) if denom > 0 else 0.0


def maximum_spanning_tree_edges(edges: List[WeightedEdge]) -> Set[EdgeKey]:
    parent: Dict[Node, Node] = {}

    def find(x: Node) -> Node:
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(a: Node, b: Node) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[rb] = ra
        return True

    chosen: Set[EdgeKey] = set()
    for e in sorted_by_strength(edges):
        if union(e.source, e.target):
            chosen.add(e.key)
    return chosen


def construct_envelopes(edges: List[WeightedEdge], cfg: Dict[str, Any]) -> Dict[Tuple[str, str], Set[EdgeKey]]:
    out: Dict[Tuple[str, str], Set[EdgeKey]] = {}
    strength_sorted = sorted_by_strength(edges)

    top_cfg = cfg.get("top_strength", {})
    if top_cfg.get("enabled", False):
        for n in top_cfg.get("edge_counts", []):
            n_int = int(n)
            out[("top_strength", f"top_edges_{n_int}")] = {e.key for e in strength_sorted[:n_int]}

    thr_cfg = cfg.get("threshold", {})
    if thr_cfg.get("enabled", False):
        for thr in thr_cfg.get("thresholds", []):
            t = float(thr)
            out[("threshold", f"abs_weight_ge_{t:g}")] = {e.key for e in edges if abs(e.weight) >= t}

    knn_cfg = cfg.get("mutual_knn", {})
    if knn_cfg.get("enabled", False):
        per_node: Dict[Node, List[WeightedEdge]] = defaultdict(list)
        for e in edges:
            per_node[e.source].append(e)
            per_node[e.target].append(e)
        top_neighbors: Dict[Tuple[Node, int], Set[Node]] = {}
        for node, es in per_node.items():
            ranked = sorted(es, key=lambda e: (-abs(e.weight), e.source, e.target))
            for k in knn_cfg.get("k_values", []):
                ki = int(k)
                neigh: Set[Node] = set()
                for e in ranked[:ki]:
                    neigh.add(e.target if e.source == node else e.source)
                top_neighbors[(node, ki)] = neigh
        for k in knn_cfg.get("k_values", []):
            ki = int(k)
            chosen: Set[EdgeKey] = set()
            for e in edges:
                if e.target in top_neighbors.get((e.source, ki), set()) and e.source in top_neighbors.get((e.target, ki), set()):
                    chosen.add(e.key)
            out[("mutual_knn", f"k_{ki}")] = chosen

    mst_cfg = cfg.get("maximum_spanning_tree", {})
    if mst_cfg.get("enabled", False):
        out[("maximum_spanning_tree", "abs_weight_mst")] = maximum_spanning_tree_edges(edges)

    return out


def make_reference_core(
    core_edges: Set[EdgeKey],
    canonical_edges: List[WeightedEdge],
    max_edges: Optional[int],
    sort_by_abs_weight: bool,
) -> Set[EdgeKey]:
    if max_edges is None:
        return set(core_edges)
    weights = edge_map(canonical_edges)
    ranked = list(core_edges)
    if sort_by_abs_weight:
        ranked.sort(key=lambda k: (-abs(weights[k].weight) if k in weights else 0.0, k[0], k[1]))
    else:
        ranked.sort()
    return set(ranked[: int(max_edges)])


def relabel_edges_by_mapping(edges: List[WeightedEdge], mapping: Dict[Node, Node]) -> List[WeightedEdge]:
    out: Dict[EdgeKey, WeightedEdge] = {}
    for e in edges:
        a = mapping.get(e.source, e.source)
        b = mapping.get(e.target, e.target)
        if a == b:
            continue
        new = WeightedEdge(a, b, e.weight)
        old = out.get(new.key)
        if old is None or abs(new.weight) > abs(old.weight):
            out[new.key] = new
    return list(out.values())


def degree_weight_preserving_rewire(
    edges: List[WeightedEdge],
    rng: random.Random,
    edge_swap_fraction: float,
    max_swap_attempt_multiplier: int,
    preserve_weight_multiset: bool,
) -> List[WeightedEdge]:
    current_keys = [e.key for e in edges]
    weights = [e.weight for e in edges]
    edge_set = set(current_keys)
    n_swaps_target = max(1, int(round(len(current_keys) * edge_swap_fraction)))
    max_attempts = max(100, n_swaps_target * int(max_swap_attempt_multiplier))
    swaps = 0
    attempts = 0

    while swaps < n_swaps_target and attempts < max_attempts and len(current_keys) >= 2:
        attempts += 1
        i, j = rng.sample(range(len(current_keys)), 2)
        a, b = current_keys[i]
        c, d = current_keys[j]
        if len({a, b, c, d}) < 4:
            continue
        if rng.random() < 0.5:
            e1, e2 = norm_edge(a, d), norm_edge(c, b)
        else:
            e1, e2 = norm_edge(a, c), norm_edge(b, d)
        if e1[0] == e1[1] or e2[0] == e2[1] or e1 == e2:
            continue
        if e1 in edge_set or e2 in edge_set:
            continue
        edge_set.remove(current_keys[i])
        edge_set.remove(current_keys[j])
        edge_set.add(e1)
        edge_set.add(e2)
        current_keys[i], current_keys[j] = e1, e2
        swaps += 1

    if preserve_weight_multiset:
        rng.shuffle(weights)
    return [WeightedEdge(a, b, float(w)) for (a, b), w in zip(current_keys, weights)]


def feature_structured_shuffle(
    edges: List[WeightedEdge],
    node_families: Dict[Node, str],
    rng: random.Random,
    mode: str,
    preserve_weight_multiset: bool,
) -> List[WeightedEdge]:
    nodes = sorted(all_nodes(edges))
    if not node_families:
        shuffled = nodes[:]
        rng.shuffle(shuffled)
        mapping = dict(zip(nodes, shuffled))
    elif mode == "within_family":
        mapping: Dict[Node, Node] = {}
        fam_to_nodes: Dict[str, List[Node]] = defaultdict(list)
        for n in nodes:
            fam_to_nodes[node_families.get(n, "UNKNOWN")].append(n)
        for fam_nodes in fam_to_nodes.values():
            shuffled = fam_nodes[:]
            rng.shuffle(shuffled)
            mapping.update(dict(zip(fam_nodes, shuffled)))
    elif mode == "across_family":
        shuffled = nodes[:]
        rng.shuffle(shuffled)
        mapping = dict(zip(nodes, shuffled))
    else:
        raise ValueError(f"Unsupported feature shuffle mode: {mode}")

    relabeled = relabel_edges_by_mapping(edges, mapping)
    if preserve_weight_multiset:
        weights = [e.weight for e in edges]
        rng.shuffle(weights)
        keys = [e.key for e in relabeled]
        return [WeightedEdge(a, b, float(w)) for (a, b), w in zip(keys, weights[: len(keys)])]
    return relabeled


def core_seeded_decoy(
    edges: List[WeightedEdge],
    reference_core: Set[EdgeKey],
    rng: random.Random,
    seed_edge_count: int,
    seed_weight_quantile: float,
    preserve_global_edge_count: bool,
) -> List[WeightedEdge]:
    # Simple first-pass decoy: randomize weights over the graph, then overwrite
    # a selected seed with high-quantile weights.
    nodes = sorted(all_nodes(edges))
    if len(nodes) < 2:
        return edges[:]
    weights = sorted([e.weight for e in edges], key=abs)
    q_idx = min(len(weights) - 1, max(0, int(round((len(weights) - 1) * seed_weight_quantile))))
    high_weights = sorted(weights[q_idx:], key=lambda w: -abs(w))
    if not high_weights:
        high_weights = weights[-1:]

    existing = set(e.key for e in edges)
    decoy_keys = set(existing)
    seed_nodes = rng.sample(nodes, min(len(nodes), max(3, seed_edge_count)))
    possible_seed = [norm_edge(a, b) for i, a in enumerate(seed_nodes) for b in seed_nodes[i + 1 :]]
    rng.shuffle(possible_seed)
    chosen_seed = possible_seed[:seed_edge_count]

    for k in chosen_seed:
        decoy_keys.add(k)

    if preserve_global_edge_count:
        non_seed = list(decoy_keys - set(chosen_seed))
        rng.shuffle(non_seed)
        while len(chosen_seed) + len(non_seed) > len(edges):
            non_seed.pop()
        final_keys = set(chosen_seed).union(non_seed)
    else:
        final_keys = decoy_keys

    final_keys_list = sorted(final_keys)
    rng.shuffle(weights)
    w_by_key: Dict[EdgeKey, float] = {}
    for k, w in zip(final_keys_list, weights * ((len(final_keys_list) // len(weights)) + 1)):
        w_by_key[k] = float(w)
    for idx, k in enumerate(chosen_seed):
        w_by_key[k] = float(high_weights[idx % len(high_weights)])

    return [WeightedEdge(a, b, w_by_key[(a, b)]) for a, b in final_keys_list]


def core_metrics(
    run_id: str,
    object_role: str,
    null_family: str,
    null_repeat: Optional[int],
    seed: Optional[int],
    construction_family: str,
    construction_variant: str,
    envelope_edges: Set[EdgeKey],
    graph_edges: List[WeightedEdge],
    reference_core: Set[EdgeKey],
    warning_count: int,
) -> Dict[str, Any]:
    retained_edges = envelope_edges.intersection(reference_core)
    ref_nodes = {n for e in reference_core for n in e}
    retained_nodes = {n for e in retained_edges for n in e}
    comps = connected_components(retained_edges, nodes=retained_nodes)
    largest = max((len(c) for c in comps), default=0)
    weights = edge_map(graph_edges)
    retained_weights = [weights[k].weight for k in retained_edges if k in weights]

    return {
        "run_id": run_id,
        "object_role": object_role,
        "null_family": null_family,
        "null_repeat": null_repeat,
        "seed": seed,
        "construction_family": construction_family,
        "construction_variant": construction_variant,
        "perturbation_family": None,
        "perturbation_strength": None,
        "core_edge_retention": len(retained_edges) / len(reference_core) if reference_core else 0.0,
        "core_node_retention": len(retained_nodes) / len(ref_nodes) if ref_nodes else 0.0,
        "core_connected": bool(len(comps) == 1 and len(retained_nodes) > 0),
        "core_component_count": len(comps),
        "core_largest_component_fraction": largest / len(retained_nodes) if retained_nodes else 0.0,
        "core_mean_weight": sum(retained_weights) / len(retained_weights) if retained_weights else None,
        "core_weight_rank_stability": None,
        "warning_count": warning_count,
    }


def envelope_metrics(
    run_id: str,
    object_role: str,
    null_family: str,
    null_repeat: Optional[int],
    seed: Optional[int],
    construction_family: str,
    construction_variant: str,
    envelope_edges: Set[EdgeKey],
    reference_core: Set[EdgeKey],
    real_envelope_edges: Optional[Set[EdgeKey]],
    warning_count: int,
) -> Dict[str, Any]:
    env_nodes = {n for e in envelope_edges for n in e}
    ref_nodes = {n for e in reference_core for n in e}
    retained_core_edges = envelope_edges.intersection(reference_core)
    retained_core_nodes = {n for e in retained_core_edges for n in e}
    comps = connected_components(envelope_edges, nodes=env_nodes)
    overlap = None
    jaccard = None
    if real_envelope_edges is not None:
        inter = len(envelope_edges.intersection(real_envelope_edges))
        union = len(envelope_edges.union(real_envelope_edges))
        overlap = inter
        jaccard = inter / union if union else 1.0

    return {
        "run_id": run_id,
        "object_role": object_role,
        "null_family": null_family,
        "null_repeat": null_repeat,
        "seed": seed,
        "construction_family": construction_family,
        "construction_variant": construction_variant,
        "envelope_node_count": len(env_nodes),
        "envelope_edge_count": len(envelope_edges),
        "envelope_density": graph_density(len(envelope_edges), len(env_nodes)),
        "envelope_connected": bool(len(comps) == 1 and len(env_nodes) > 0),
        "envelope_component_count": len(comps),
        "envelope_core_edge_containment": len(retained_core_edges) / len(reference_core) if reference_core else 0.0,
        "envelope_core_node_containment": len(retained_core_nodes) / len(ref_nodes) if ref_nodes else 0.0,
        "envelope_edge_overlap_to_real": overlap,
        "envelope_jaccard_to_real": jaccard,
        "warning_count": warning_count,
    }


def numeric_values(rows: List[Dict[str, Any]], metric: str) -> List[float]:
    out: List[float] = []
    for r in rows:
        v = r.get(metric)
        try:
            if v is not None and v != "":
                out.append(float(v))
        except (TypeError, ValueError):
            pass
    return out


def mean(xs: List[float]) -> Optional[float]:
    return sum(xs) / len(xs) if xs else None


def median(xs: List[float]) -> Optional[float]:
    if not xs:
        return None
    s = sorted(xs)
    mid = len(s) // 2
    if len(s) % 2:
        return s[mid]
    return (s[mid - 1] + s[mid]) / 2.0


def std(xs: List[float]) -> Optional[float]:
    if len(xs) < 2:
        return 0.0 if len(xs) == 1 else None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def interpretation_label(exceedance: Optional[float], n: int, thresholds: Dict[str, Any]) -> str:
    min_n = int(thresholds.get("min_null_repeats_for_label", 30))
    if exceedance is None or n < min_n:
        return "inconclusive_due_to_warnings_or_scope"
    low = float(thresholds.get("exceedance_low", 0.05))
    high = float(thresholds.get("exceedance_high", 0.50))
    if exceedance <= low:
        return "real_exceeds_tested_null_family"
    if exceedance >= high:
        return "null_reproduces_core_behavior"
    return "mixed_family_dependent_result"


def summarize_real_vs_null(
    run_id: str,
    core_rows: List[Dict[str, Any]],
    env_rows: List[Dict[str, Any]],
    config: Dict[str, Any],
) -> List[Dict[str, Any]]:
    all_rows = core_rows + env_rows
    metrics = config.get("comparison", {}).get("metrics", [])
    directions = config.get("comparison", {}).get("directions", {})
    thresholds = config.get("interpretation_thresholds", {})

    real_by_key: Dict[Tuple[str, str, str], Dict[str, Any]] = {}
    null_groups: Dict[Tuple[str, str, str, str], List[Dict[str, Any]]] = defaultdict(list)

    for row in all_rows:
        cf = str(row.get("construction_family"))
        cv = str(row.get("construction_variant"))
        role = row.get("object_role")
        if role == "real":
            real_by_key[(cf, cv, "canonical")] = row
        elif role == "null":
            nf = str(row.get("null_family"))
            null_groups[(cf, cv, nf, "null")].append(row)

    summary: List[Dict[str, Any]] = []
    for (cf, cv, nf, _), nrows in sorted(null_groups.items()):
        real = real_by_key.get((cf, cv, "canonical"))
        if real is None:
            continue
        for metric in metrics:
            rv_raw = real.get(metric)
            try:
                real_value = float(rv_raw)
            except (TypeError, ValueError):
                continue
            xs = numeric_values(nrows, metric)
            if not xs:
                continue
            direction = directions.get(metric, "higher_is_more_core_like")
            if direction == "higher_is_more_core_like":
                exceed = sum(1 for x in xs if x >= real_value) / len(xs)
                rank = 1 + sum(1 for x in xs if x > real_value)
            elif direction == "lower_is_more_core_like":
                exceed = sum(1 for x in xs if x <= real_value) / len(xs)
                rank = 1 + sum(1 for x in xs if x < real_value)
            else:
                m = mean(xs) or 0.0
                dist = abs(real_value - m)
                exceed = sum(1 for x in xs if abs(x - m) >= dist) / len(xs)
                rank = None

            xmean = mean(xs)
            xmed = median(xs)
            summary.append(
                {
                    "run_id": run_id,
                    "metric_name": metric,
                    "construction_family": cf,
                    "construction_variant": cv,
                    "null_family": nf,
                    "real_value": real_value,
                    "null_mean": xmean,
                    "null_median": xmed,
                    "null_std": std(xs),
                    "null_min": min(xs),
                    "null_max": max(xs),
                    "real_minus_null_mean": real_value - xmean if xmean is not None else None,
                    "real_minus_null_median": real_value - xmed if xmed is not None else None,
                    "empirical_exceedance_fraction": exceed,
                    "real_rank_position": rank,
                    "n_null_repeats": len(xs),
                    "comparison_direction": direction,
                    "interpretation_label": interpretation_label(exceed, len(xs), thresholds),
                }
            )
    return summary


def build_null_objects(
    canonical_edges: List[WeightedEdge],
    node_families: Dict[Node, str],
    cfg: Dict[str, Any],
    seed_base: int,
    warnings: WarningCollector,
) -> List[Tuple[str, int, int, List[WeightedEdge]]]:
    out: List[Tuple[str, int, int, List[WeightedEdge]]] = []
    nf_cfg = cfg.get("null_families", {})

    a = nf_cfg.get("degree_weight_preserving_rewire", {})
    if a.get("enabled", False):
        for repeat in range(int(a.get("repeats", 50))):
            seed = seed_base + 100000 + repeat
            rng = random.Random(seed)
            obj = degree_weight_preserving_rewire(
                canonical_edges,
                rng,
                float(a.get("edge_swap_fraction", 0.25)),
                int(a.get("max_swap_attempt_multiplier", 20)),
                bool(a.get("preserve_weight_multiset", True)),
            )
            out.append(("degree_weight_preserving_rewire", repeat, seed, obj))

    b = nf_cfg.get("feature_structured_shuffle", {})
    if b.get("enabled", False):
        if not node_families:
            warnings.add(
                "warning",
                "feature_structured_shuffle is enabled but no node family metadata is available; using unrestricted node shuffle fallback.",
                null_family="feature_structured_shuffle",
            )
        for repeat in range(int(b.get("repeats", 50))):
            seed = seed_base + 200000 + repeat
            rng = random.Random(seed)
            obj = feature_structured_shuffle(
                canonical_edges,
                node_families,
                rng,
                str(b.get("shuffle_mode", "within_family")),
                bool(b.get("preserve_weight_multiset", True)),
            )
            out.append(("feature_structured_shuffle", repeat, seed, obj))

    c = nf_cfg.get("core_seeded_decoy", {})
    if c.get("enabled", False):
        reference_core = set()
        for repeat in range(int(c.get("repeats", 50))):
            seed = seed_base + 300000 + repeat
            rng = random.Random(seed)
            obj = core_seeded_decoy(
                canonical_edges,
                reference_core,
                rng,
                int(c.get("seed_edge_count", 6)),
                float(c.get("seed_weight_quantile", 0.90)),
                bool(c.get("preserve_global_edge_count", True)),
            )
            out.append(("core_seeded_decoy", repeat, seed, obj))

    return out


CORE_FIELDNAMES = [
    "run_id",
    "object_role",
    "null_family",
    "null_repeat",
    "seed",
    "construction_family",
    "construction_variant",
    "perturbation_family",
    "perturbation_strength",
    "core_edge_retention",
    "core_node_retention",
    "core_connected",
    "core_component_count",
    "core_largest_component_fraction",
    "core_mean_weight",
    "core_weight_rank_stability",
    "warning_count",
]

ENVELOPE_FIELDNAMES = [
    "run_id",
    "object_role",
    "null_family",
    "null_repeat",
    "seed",
    "construction_family",
    "construction_variant",
    "envelope_node_count",
    "envelope_edge_count",
    "envelope_density",
    "envelope_connected",
    "envelope_component_count",
    "envelope_core_edge_containment",
    "envelope_core_node_containment",
    "envelope_edge_overlap_to_real",
    "envelope_jaccard_to_real",
    "warning_count",
]

SUMMARY_FIELDNAMES = [
    "run_id",
    "metric_name",
    "construction_family",
    "construction_variant",
    "null_family",
    "real_value",
    "null_mean",
    "null_median",
    "null_std",
    "null_min",
    "null_max",
    "real_minus_null_mean",
    "real_minus_null_median",
    "empirical_exceedance_fraction",
    "real_rank_position",
    "n_null_repeats",
    "comparison_direction",
    "interpretation_label",
]

NULL_INV_FIELDNAMES = [
    "run_id",
    "null_family",
    "null_repeat",
    "seed",
    "node_count",
    "edge_count",
    "density",
    "connected",
    "component_count",
]


def run(config_path: Path) -> int:
    config = load_yaml(config_path)
    run_cfg = config.get("run", {})
    run_id = str(run_cfg.get("run_id", "BMC15h_structured_specificity_extension_open"))
    repo_root = resolve_path(Path.cwd(), run_cfg.get("repo_root", ".")) or Path.cwd()
    repo_root = repo_root.resolve()
    output_dir = resolve_path(repo_root, run_cfg.get("output_dir")) or (
        repo_root / "runs/BMC-15h/structured_specificity_extension_open"
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    warnings = WarningCollector()

    inputs = config.get("inputs", {})
    columns = config.get("columns", {})
    canonical_path = resolve_path(repo_root, inputs.get("canonical_edge_table"))
    core_path = resolve_path(repo_root, inputs.get("reference_core_edges"))
    if canonical_path is None or not canonical_path.exists():
        raise FileNotFoundError(f"Canonical edge table not found: {canonical_path}")
    if core_path is None or not core_path.exists():
        raise FileNotFoundError(f"Reference core edge table not found: {core_path}")

    canonical_edges = load_weighted_edges(canonical_path, columns)
    if not canonical_edges:
        raise ValueError(f"No usable weighted edges loaded from {canonical_path}")

    raw_core = load_edge_keys(core_path, columns)
    reference_core = make_reference_core(
        raw_core,
        canonical_edges,
        config.get("reference_core", {}).get("max_edges"),
        bool(config.get("reference_core", {}).get("sort_by_abs_weight", True)),
    )
    if not reference_core:
        raise ValueError(f"No usable reference-core edges loaded from {core_path}")

    node_families: Dict[Node, str] = {}
    node_metadata_path = resolve_path(repo_root, inputs.get("node_metadata"))
    if node_metadata_path and node_metadata_path.exists():
        try:
            node_families = load_node_families(
                node_metadata_path,
                str(columns.get("node_id", "node_id")),
                str(config.get("null_families", {}).get("feature_structured_shuffle", {}).get("family_column", columns.get("family", "family"))),
            )
        except Exception as exc:
            warnings.add("warning", f"Could not load node metadata for feature shuffles: {exc}")
    else:
        warnings.add("warning", f"Node metadata not found: {node_metadata_path}", affected_output="feature_structured_shuffle")

    # Optional reference envelope files are inventoried only in this first runner;
    # canonical comparisons use internally reconstructed envelopes with matching
    # construction labels.
    for ref in inputs.get("reference_envelopes", []) or []:
        p = resolve_path(repo_root, ref.get("path"))
        if p is None or not p.exists():
            warnings.add("info", f"Optional reference envelope file not found: {p}", affected_output=ref.get("label"))

    construction_cfg = config.get("construction_families", {})
    real_envs = construct_envelopes(canonical_edges, construction_cfg)

    core_rows: List[Dict[str, Any]] = []
    env_rows: List[Dict[str, Any]] = []
    inv_rows: List[Dict[str, Any]] = []

    for (cf, cv), env_edges in sorted(real_envs.items()):
        core_rows.append(
            core_metrics(
                run_id,
                "real",
                "canonical",
                None,
                None,
                cf,
                cv,
                env_edges,
                canonical_edges,
                reference_core,
                len(warnings.rows),
            )
        )
        env_rows.append(
            envelope_metrics(
                run_id,
                "real",
                "canonical",
                None,
                None,
                cf,
                cv,
                env_edges,
                reference_core,
                env_edges,
                len(warnings.rows),
            )
        )

    null_objects = build_null_objects(
        canonical_edges,
        node_families,
        config,
        int(run_cfg.get("random_seed_base", 1508001)),
        warnings,
    )

    for null_family, repeat, seed, null_edges in null_objects:
        null_nodes = all_nodes(null_edges)
        comps = connected_components([e.key for e in null_edges], nodes=null_nodes)
        inv_rows.append(
            {
                "run_id": run_id,
                "null_family": null_family,
                "null_repeat": repeat,
                "seed": seed,
                "node_count": len(null_nodes),
                "edge_count": len(null_edges),
                "density": graph_density(len(null_edges), len(null_nodes)),
                "connected": bool(len(comps) == 1 and len(null_nodes) > 0),
                "component_count": len(comps),
            }
        )
        null_envs = construct_envelopes(null_edges, construction_cfg)
        for (cf, cv), env_edges in sorted(null_envs.items()):
            real_env = real_envs.get((cf, cv))
            core_rows.append(
                core_metrics(
                    run_id,
                    "null",
                    null_family,
                    repeat,
                    seed,
                    cf,
                    cv,
                    env_edges,
                    null_edges,
                    reference_core,
                    len(warnings.rows),
                )
            )
            env_rows.append(
                envelope_metrics(
                    run_id,
                    "null",
                    null_family,
                    repeat,
                    seed,
                    cf,
                    cv,
                    env_edges,
                    reference_core,
                    real_env,
                    len(warnings.rows),
                )
            )

    summary_rows = summarize_real_vs_null(run_id, core_rows, env_rows, config)

    outputs = config.get("outputs", {})
    write_csv_dicts(output_dir / outputs.get("core_metrics_csv", "bmc15h_core_metrics.csv"), core_rows, CORE_FIELDNAMES)
    write_csv_dicts(output_dir / outputs.get("envelope_metrics_csv", "bmc15h_envelope_metrics.csv"), env_rows, ENVELOPE_FIELDNAMES)
    write_csv_dicts(output_dir / outputs.get("real_vs_null_summary_csv", "bmc15h_real_vs_null_summary.csv"), summary_rows, SUMMARY_FIELDNAMES)
    write_csv_dicts(output_dir / outputs.get("null_family_inventory_csv", "bmc15h_null_family_inventory.csv"), inv_rows, NULL_INV_FIELDNAMES)

    manifest = {
        "run_id": run_id,
        "created_at": utc_now_iso(),
        "script_name": Path(__file__).name,
        "config_path": str(config_path),
        "output_dir": str(output_dir),
        "input_files": {
            "canonical_edge_table": str(canonical_path),
            "node_metadata": str(node_metadata_path) if node_metadata_path else None,
            "reference_core_edges": str(core_path),
        },
        "null_families": sorted({r["null_family"] for r in inv_rows}),
        "construction_families": sorted({r["construction_family"] for r in core_rows}),
        "perturbation_families": [],
        "seeds": sorted({r["seed"] for r in inv_rows if r.get("seed") is not None}),
        "repeats_per_family": {
            nf: sum(1 for r in inv_rows if r["null_family"] == nf)
            for nf in sorted({r["null_family"] for r in inv_rows})
        },
        "row_counts": {
            "core_metrics": len(core_rows),
            "envelope_metrics": len(env_rows),
            "real_vs_null_summary": len(summary_rows),
            "null_family_inventory": len(inv_rows),
            "warnings": len(warnings.rows),
        },
        "warnings_file": str(output_dir / outputs.get("warnings_json", "bmc15h_warnings.json")),
        "notes": (
            "BMC-15h structured specificity diagnostic. Results are construction-qualified "
            "and must not be interpreted as proof of physical geometry."
        ),
    }

    with (output_dir / outputs.get("run_manifest_json", "bmc15h_run_manifest.json")).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    with (output_dir / outputs.get("warnings_json", "bmc15h_warnings.json")).open("w", encoding="utf-8") as f:
        json.dump(warnings.rows, f, indent=2, ensure_ascii=False)

    write_yaml(output_dir / outputs.get("resolved_config_yaml", "bmc15h_config_resolved.yaml"), config)

    print(f"BMC-15h run completed: {run_id}")
    print(f"Output directory: {output_dir}")
    print(f"Core metric rows: {len(core_rows)}")
    print(f"Envelope metric rows: {len(env_rows)}")
    print(f"Summary rows: {len(summary_rows)}")
    print(f"Warnings: {len(warnings.rows)}")

    return 0


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run BMC-15h structured specificity diagnostic.")
    parser.add_argument(
        "--config",
        required=True,
        help="Path to data/bmc15h_structured_specificity_extension_config.yaml",
    )
    args = parser.parse_args(argv)
    return run(Path(args.config).expanduser().resolve())


if __name__ == "__main__":
    raise SystemExit(main())
