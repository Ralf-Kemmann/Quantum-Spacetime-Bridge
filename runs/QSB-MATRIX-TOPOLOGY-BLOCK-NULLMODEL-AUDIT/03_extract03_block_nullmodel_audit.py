#!/usr/bin/env python3
"""Run graph-theoretic nullmodel audits for the confirmed QSB block structure."""

from __future__ import annotations

import csv
import json
import math
import random
import statistics
from collections import Counter
from pathlib import Path
from typing import Iterable


RUN_ID = "QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT"
RUN_DIR = Path("runs") / RUN_ID

SOURCE_EDGE_FILE = Path(
    "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/"
    "16_edge_candidate_result.csv"
)
CLOSURE_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json")
BLOCK_STRUCTURE_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json"
)
BLOCK_SEMANTICS_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json"
)
PAIR_SEMANTICS_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/05_pair_id_semantics_by_node.csv"
)
COMPONENT_SEMANTICS_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/06_component_semantics_profile.csv"
)
STRENGTH_SUMMARY_CONTEXT_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE/04_block_strength_summary.json"
)

GNM_SEED = 20260629
DEGREE_PRESERVING_SEED = 20260630
SEMANTIC_BLOCK_SEED = 20260631
GNM_TRIALS = 10000
DEGREE_PRESERVING_TRIALS = 2000
EDGE_SWAP_ATTEMPTS_PER_TRIAL = 5000
SEMANTIC_BLOCK_RANDOMIZATION_TRIALS = 10000
OBSERVED_COMPONENT_PATTERN = [12, 10, 8, 6, 4, 2]
BOUNDARY = "graph-theoretic_nullmodel_only_no_physics_claim"
CLAIM_BOUNDARY = (
    "Purely structural graph-theoretic, index-semantic, and statistically descriptive "
    "nullmodel audit. Nullmodels only describe rarity under tested graph controls. "
    "No claim is made about physical geometry, spacetime, metric structure, "
    "gravitation, causality, dynamics, experimental validation, or physical emergence."
)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def pair_sort_key(pair_id: str) -> tuple[int, int]:
    left, right = pair_id.split("|")
    return int(left), int(right)


def bool_text(value: bool) -> str:
    return str(value).lower()


def semicolon_join(values: Iterable[object]) -> str:
    return ";".join(str(value) for value in values)


def quantile(values: list[float], fraction: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[int(position)]
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def stats(values: list[float]) -> dict[str, float | None]:
    return {
        "min": min(values) if values else None,
        "q1": quantile(values, 0.25),
        "median": statistics.median(values) if values else None,
        "mean": statistics.fmean(values) if values else None,
        "q3": quantile(values, 0.75),
        "max": max(values) if values else None,
        "std": statistics.pstdev(values) if values else None,
    }


class GraphUniverse:
    def __init__(
        self,
        nodes: list[str],
        all_edges: list[tuple[int, int]],
        observed_edge_ids: set[int],
        semantic_edge_ids: set[int],
    ) -> None:
        self.nodes = nodes
        self.n = len(nodes)
        self.all_mask = (1 << self.n) - 1
        self.all_edges = all_edges
        self.edge_id_by_pair = {edge: index for index, edge in enumerate(all_edges)}
        self.observed_edge_ids = observed_edge_ids
        self.semantic_edge_ids = semantic_edge_ids
        self.semantic_edge_id_mask = [index in semantic_edge_ids for index in range(len(all_edges))]

    def edge_id(self, a: int, b: int) -> int:
        if a > b:
            a, b = b, a
        return self.edge_id_by_pair[(a, b)]


def load_universe() -> tuple[GraphUniverse, dict[str, dict[str, int]], list[int]]:
    pair_semantics: dict[str, dict[str, int]] = {}
    for row in read_csv_rows(PAIR_SEMANTICS_SOURCE):
        pair_semantics[row["pair_id"]] = {
            "component_id": int(row["component_id"]),
            "abs_delta": int(row["abs_delta"]),
        }
    nodes = sorted(pair_semantics, key=pair_sort_key)
    node_index = {node: index for index, node in enumerate(nodes)}
    all_edges: list[tuple[int, int]] = []
    observed_pairs: set[tuple[int, int]] = set()

    for row in read_csv_rows(SOURCE_EDGE_FILE):
        a = node_index[row["pair_a"]]
        b = node_index[row["pair_b"]]
        edge = (a, b) if a < b else (b, a)
        all_edges.append(edge)
        if row["edge_candidate_flag"] == "1":
            observed_pairs.add(edge)
    all_edges.sort()
    edge_id_by_pair = {edge: index for index, edge in enumerate(all_edges)}
    observed_edge_ids = {edge_id_by_pair[edge] for edge in observed_pairs}
    semantic_edge_ids = {
        index
        for index, (a, b) in enumerate(all_edges)
        if pair_semantics[nodes[a]]["abs_delta"] == pair_semantics[nodes[b]]["abs_delta"]
    }
    node_abs_delta = [pair_semantics[node]["abs_delta"] for node in nodes]
    return GraphUniverse(nodes, all_edges, observed_edge_ids, semantic_edge_ids), pair_semantics, node_abs_delta


def graph_metrics(universe: GraphUniverse, edge_ids: set[int]) -> dict[str, object]:
    n = universe.n
    adj = [0] * n
    degrees = [0] * n
    for edge_id in edge_ids:
        a, b = universe.all_edges[edge_id]
        adj[a] |= 1 << b
        adj[b] |= 1 << a
        degrees[a] += 1
        degrees[b] += 1

    seen = 0
    component_sizes: list[int] = []
    component_edge_counts: list[int] = []
    for start in range(n):
        bit = 1 << start
        if seen & bit:
            continue
        queue = [start]
        seen |= bit
        component_mask = bit
        for node in queue:
            neighbors = adj[node] & ~seen
            while neighbors:
                next_bit = neighbors & -neighbors
                neighbor = next_bit.bit_length() - 1
                seen |= next_bit
                component_mask |= next_bit
                queue.append(neighbor)
                neighbors ^= next_bit
        size = component_mask.bit_count()
        component_sizes.append(size)
        component_edge_counts.append(
            sum(degrees[node] for node in range(n) if component_mask & (1 << node)) // 2
        )

    triangles = 0
    for edge_id in edge_ids:
        a, b = universe.all_edges[edge_id]
        if a > b:
            a, b = b, a
        greater_than_b_mask = universe.all_mask ^ ((1 << (b + 1)) - 1)
        triangles += (adj[a] & adj[b] & greater_than_b_mask).bit_count()

    connected_triples = sum(degree * (degree - 1) // 2 for degree in degrees)
    closed_triples = 3 * triangles
    open_wedges = connected_triples - closed_triples
    closure_ratio = closed_triples / connected_triples if connected_triples else 0.0
    sorted_sizes = sorted(component_sizes, reverse=True)
    all_components_are_cliques = all(
        edge_count == size * (size - 1) // 2
        for size, edge_count in zip(component_sizes, component_edge_counts)
    )
    component_sizes_match = sorted_sizes == OBSERVED_COMPONENT_PATTERN
    semantic_within = sum(1 for edge_id in edge_ids if universe.semantic_edge_id_mask[edge_id])
    semantic_cross = len(edge_ids) - semantic_within
    matches_exact_semantic = edge_ids == universe.semantic_edge_ids
    return {
        "node_count": n,
        "possible_edge_count": len(universe.all_edges),
        "edge_count": len(edge_ids),
        "component_count": len(component_sizes),
        "component_sizes_sorted_desc": sorted_sizes,
        "largest_component_size": sorted_sizes[0] if sorted_sizes else 0,
        "triangle_count": triangles,
        "connected_triple_count": connected_triples,
        "closed_triple_count": closed_triples,
        "open_wedge_count": open_wedges,
        "global_closure_ratio": closure_ratio,
        "all_components_are_cliques": all_components_are_cliques,
        "component_sizes_match_observed_pattern": component_sizes_match,
        "complete_disjoint_clique_blocks_confirmed": all_components_are_cliques and component_sizes_match,
        "semantic_within_block_edge_count": semantic_within,
        "semantic_cross_block_edge_count": semantic_cross,
        "all_candidate_edges_within_semantic_blocks": semantic_cross == 0,
        "all_edges_within_semantic_blocks": semantic_cross == 0,
        "matches_exact_semantic_block_edge_set": matches_exact_semantic,
    }


def sample_row(trial_id: int, metrics: dict[str, object], accepted_swaps: int | None = None) -> dict[str, object]:
    row = {
        "trial_id": trial_id,
        "edge_count": metrics["edge_count"],
        "component_count": metrics["component_count"],
        "component_sizes_sorted_desc": semicolon_join(metrics["component_sizes_sorted_desc"]),
        "largest_component_size": metrics["largest_component_size"],
        "triangle_count": metrics["triangle_count"],
        "connected_triple_count": metrics["connected_triple_count"],
        "closed_triple_count": metrics["closed_triple_count"],
        "open_wedge_count": metrics["open_wedge_count"],
        "global_closure_ratio": metrics["global_closure_ratio"],
        "semantic_within_block_edge_count": metrics["semantic_within_block_edge_count"],
        "semantic_cross_block_edge_count": metrics["semantic_cross_block_edge_count"],
        "all_edges_within_semantic_blocks": bool_text(bool(metrics["all_edges_within_semantic_blocks"])),
        "all_components_are_cliques": bool_text(bool(metrics["all_components_are_cliques"])),
        "component_sizes_match_observed_pattern": bool_text(bool(metrics["component_sizes_match_observed_pattern"])),
        "complete_disjoint_clique_blocks_confirmed": bool_text(bool(metrics["complete_disjoint_clique_blocks_confirmed"])),
        "matches_exact_semantic_block_edge_set": bool_text(bool(metrics["matches_exact_semantic_block_edge_set"])),
    }
    if accepted_swaps is not None:
        row["accepted_swaps"] = accepted_swaps
    return row


def summarize_trials(
    observed: dict[str, object],
    samples: list[dict[str, object]],
    trial_count: int,
) -> list[dict[str, object]]:
    metric_names = [
        "triangle_count",
        "global_closure_ratio",
        "open_wedge_count",
        "semantic_cross_block_edge_count",
        "semantic_within_block_edge_count",
        "largest_component_size",
        "component_count",
    ]
    rows: list[dict[str, object]] = []
    for metric in metric_names:
        values = [float(sample[metric]) for sample in samples]
        observed_value = float(observed[metric])
        s = stats(values)
        ge_count = sum(1 for value in values if value >= observed_value)
        le_count = sum(1 for value in values if value <= observed_value)
        eq_count = sum(1 for value in values if value == observed_value)
        rows.append(
            {
                "metric": metric,
                "observed_value": observed[metric],
                "trial_count": trial_count,
                "min": s["min"],
                "q1": s["q1"],
                "median": s["median"],
                "mean": s["mean"],
                "q3": s["q3"],
                "max": s["max"],
                "std": s["std"],
                "ge_observed_count": ge_count,
                "le_observed_count": le_count,
                "eq_observed_count": eq_count,
                "empirical_p_ge_observed": (ge_count + 1) / (trial_count + 1),
                "empirical_p_le_observed": (le_count + 1) / (trial_count + 1),
                "empirical_p_eq_observed": (eq_count + 1) / (trial_count + 1),
                "upper_bound_p_if_zero_hits": 1 / (trial_count + 1) if eq_count == 0 else "",
            }
        )
    return rows


def pvalue_row(nullmodel: str, test_name: str, observed_value: object, comparison: str, hit_count: int, trial_count: int) -> dict[str, object]:
    return {
        "nullmodel": nullmodel,
        "test_name": test_name,
        "observed_value": observed_value,
        "comparison": comparison,
        "hit_count": hit_count,
        "trial_count": trial_count,
        "empirical_p_with_plus_one": (hit_count + 1) / (trial_count + 1),
        "zero_hit_upper_bound": 1 / (trial_count + 1) if hit_count == 0 else "",
        "interpretation_boundary": BOUNDARY,
    }


def run_gnm(universe: GraphUniverse, observed: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    rng = random.Random(GNM_SEED)
    all_edge_ids = list(range(len(universe.all_edges)))
    samples: list[dict[str, object]] = []
    raw_metrics: list[dict[str, object]] = []
    for trial_id in range(1, GNM_TRIALS + 1):
        edge_ids = set(rng.sample(all_edge_ids, int(observed["edge_count"])))
        metrics = graph_metrics(universe, edge_ids)
        raw_metrics.append(metrics)
        samples.append(sample_row(trial_id, metrics))
    summary = summarize_trials(observed, raw_metrics, GNM_TRIALS)
    hits = {
        "triangle_ge": sum(1 for item in raw_metrics if item["triangle_count"] >= observed["triangle_count"]),
        "closure_ge": sum(1 for item in raw_metrics if item["global_closure_ratio"] >= observed["global_closure_ratio"]),
        "open_wedge_le": sum(1 for item in raw_metrics if item["open_wedge_count"] <= observed["open_wedge_count"]),
        "semantic_cross_le": sum(1 for item in raw_metrics if item["semantic_cross_block_edge_count"] <= observed["semantic_cross_block_edge_count"]),
        "semantic_within_ge": sum(1 for item in raw_metrics if item["semantic_within_block_edge_count"] >= observed["semantic_within_block_edge_count"]),
        "complete_blocks": sum(1 for item in raw_metrics if item["complete_disjoint_clique_blocks_confirmed"]),
        "exact_semantic": sum(1 for item in raw_metrics if item["matches_exact_semantic_block_edge_set"]),
    }
    return samples, summary, raw_metrics, hits


def attempt_swap(universe: GraphUniverse, edge_ids: set[int], edge_list: list[int], rng: random.Random) -> bool:
    if len(edge_list) < 2:
        return False
    index1, index2 = rng.sample(range(len(edge_list)), 2)
    edge1 = edge_list[index1]
    edge2 = edge_list[index2]
    a, b = universe.all_edges[edge1]
    c, d = universe.all_edges[edge2]
    if len({a, b, c, d}) < 4:
        return False
    if rng.randrange(2) == 0:
        new_pairs = [(a, d), (c, b)]
    else:
        new_pairs = [(a, c), (b, d)]
    normalized: list[tuple[int, int]] = []
    for x, y in new_pairs:
        if x == y:
            return False
        if x > y:
            x, y = y, x
        normalized.append((x, y))
    if normalized[0] == normalized[1]:
        return False
    try:
        new_edge1 = universe.edge_id(*normalized[0])
        new_edge2 = universe.edge_id(*normalized[1])
    except KeyError:
        return False
    old_edges = {edge1, edge2}
    if (new_edge1 in edge_ids and new_edge1 not in old_edges) or (
        new_edge2 in edge_ids and new_edge2 not in old_edges
    ):
        return False
    edge_ids.remove(edge1)
    edge_ids.remove(edge2)
    edge_ids.add(new_edge1)
    edge_ids.add(new_edge2)
    edge_list[index1] = new_edge1
    edge_list[index2] = new_edge2
    return True


def run_degree_preserving(universe: GraphUniverse, observed: dict[str, object]) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]], dict[str, int]]:
    rng = random.Random(DEGREE_PRESERVING_SEED)
    samples: list[dict[str, object]] = []
    raw_metrics: list[dict[str, object]] = []
    for trial_id in range(1, DEGREE_PRESERVING_TRIALS + 1):
        edge_ids = set(universe.observed_edge_ids)
        edge_list = sorted(edge_ids)
        accepted_swaps = 0
        for _ in range(EDGE_SWAP_ATTEMPTS_PER_TRIAL):
            if attempt_swap(universe, edge_ids, edge_list, rng):
                accepted_swaps += 1
        metrics = graph_metrics(universe, edge_ids)
        raw_metrics.append(metrics)
        samples.append(sample_row(trial_id, metrics, accepted_swaps=accepted_swaps))
    summary = summarize_trials(observed, raw_metrics, DEGREE_PRESERVING_TRIALS)
    hits = {
        "triangle_ge": sum(1 for item in raw_metrics if item["triangle_count"] >= observed["triangle_count"]),
        "closure_ge": sum(1 for item in raw_metrics if item["global_closure_ratio"] >= observed["global_closure_ratio"]),
        "open_wedge_le": sum(1 for item in raw_metrics if item["open_wedge_count"] <= observed["open_wedge_count"]),
        "semantic_cross_le": sum(1 for item in raw_metrics if item["semantic_cross_block_edge_count"] <= observed["semantic_cross_block_edge_count"]),
        "semantic_within_ge": sum(1 for item in raw_metrics if item["semantic_within_block_edge_count"] >= observed["semantic_within_block_edge_count"]),
        "complete_blocks": sum(1 for item in raw_metrics if item["complete_disjoint_clique_blocks_confirmed"]),
        "exact_semantic": sum(1 for item in raw_metrics if item["matches_exact_semantic_block_edge_set"]),
    }
    return samples, summary, raw_metrics, hits


def run_semantic_block_randomization(universe: GraphUniverse, node_abs_delta: list[int]) -> tuple[dict[str, object], dict[str, int]]:
    rng = random.Random(SEMANTIC_BLOCK_SEED)
    nodes = list(range(universe.n))
    block_sizes = OBSERVED_COMPONENT_PATTERN
    semantic_within_values: list[int] = []
    semantic_cross_values: list[int] = []
    exact_match_count = 0
    for _ in range(SEMANTIC_BLOCK_RANDOMIZATION_TRIALS):
        shuffled = nodes[:]
        rng.shuffle(shuffled)
        edge_ids: set[int] = set()
        offset = 0
        for size in block_sizes:
            block = shuffled[offset : offset + size]
            offset += size
            for i, a in enumerate(block):
                for b in block[i + 1 :]:
                    edge_ids.add(universe.edge_id(a, b))
        semantic_within = sum(1 for edge_id in edge_ids if universe.semantic_edge_id_mask[edge_id])
        semantic_cross = len(edge_ids) - semantic_within
        semantic_within_values.append(semantic_within)
        semantic_cross_values.append(semantic_cross)
        if edge_ids == universe.semantic_edge_ids:
            exact_match_count += 1
    within_stats = stats([float(value) for value in semantic_within_values])
    cross_stats = stats([float(value) for value in semantic_cross_values])
    observed_within = len(universe.semantic_edge_ids)
    observed_cross = 0
    row = {
        "trial_count": SEMANTIC_BLOCK_RANDOMIZATION_TRIALS,
        "observed_semantic_within_block_edge_count": observed_within,
        "observed_semantic_cross_block_edge_count": observed_cross,
        "semantic_within_min": within_stats["min"],
        "semantic_within_median": within_stats["median"],
        "semantic_within_mean": within_stats["mean"],
        "semantic_within_max": within_stats["max"],
        "semantic_cross_min": cross_stats["min"],
        "semantic_cross_median": cross_stats["median"],
        "semantic_cross_mean": cross_stats["mean"],
        "semantic_cross_max": cross_stats["max"],
        "exact_semantic_block_match_count": exact_match_count,
        "empirical_p_exact_semantic_match": (exact_match_count + 1)
        / (SEMANTIC_BLOCK_RANDOMIZATION_TRIALS + 1),
        "upper_bound_p_exact_semantic_match_if_zero_hits": (
            1 / (SEMANTIC_BLOCK_RANDOMIZATION_TRIALS + 1)
            if exact_match_count == 0
            else ""
        ),
    }
    hits = {
        "exact_semantic": exact_match_count,
        "semantic_within_ge": sum(1 for value in semantic_within_values if value >= observed_within),
        "semantic_cross_le": sum(1 for value in semantic_cross_values if value <= observed_cross),
    }
    return row, hits


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    closure_summary = read_json(CLOSURE_SUMMARY_SOURCE)
    block_structure_summary = read_json(BLOCK_STRUCTURE_SUMMARY_SOURCE)
    block_semantics_summary = read_json(BLOCK_SEMANTICS_SUMMARY_SOURCE)
    _component_semantics_rows = read_csv_rows(COMPONENT_SEMANTICS_SOURCE)
    strength_context_present = STRENGTH_SUMMARY_CONTEXT_SOURCE.exists()

    if block_structure_summary.get("block_structure_status") != "complete_disjoint_clique_blocks_confirmed":
        raise ValueError("Prior block-structure audit is not confirmed")
    if block_semantics_summary.get("semantic_status") != "blocks_correspond_to_directed_pair_index_distance_classes":
        raise ValueError("Prior block-semantics audit is not confirmed")

    universe, _pair_semantics, node_abs_delta = load_universe()
    observed = graph_metrics(universe, universe.observed_edge_ids)

    observed_row = {
        "node_count": observed["node_count"],
        "possible_edge_count": observed["possible_edge_count"],
        "edge_count": observed["edge_count"],
        "component_count": observed["component_count"],
        "component_sizes_sorted_desc": semicolon_join(observed["component_sizes_sorted_desc"]),
        "largest_component_size": observed["largest_component_size"],
        "triangle_count": observed["triangle_count"],
        "connected_triple_count": observed["connected_triple_count"],
        "closed_triple_count": observed["closed_triple_count"],
        "open_wedge_count": observed["open_wedge_count"],
        "global_closure_ratio": observed["global_closure_ratio"],
        "all_components_are_cliques": bool_text(bool(observed["all_components_are_cliques"])),
        "component_sizes_match_observed_pattern": bool_text(bool(observed["component_sizes_match_observed_pattern"])),
        "complete_disjoint_clique_blocks_confirmed": bool_text(bool(observed["complete_disjoint_clique_blocks_confirmed"])),
        "semantic_within_block_edge_count": observed["semantic_within_block_edge_count"],
        "semantic_cross_block_edge_count": observed["semantic_cross_block_edge_count"],
        "all_candidate_edges_within_semantic_blocks": bool_text(bool(observed["all_candidate_edges_within_semantic_blocks"])),
        "matches_exact_semantic_block_edge_set": bool_text(bool(observed["matches_exact_semantic_block_edge_set"])),
    }
    write_csv(
        RUN_DIR / "05_observed_graph_metrics.csv",
        list(observed_row.keys()),
        [observed_row],
    )

    gnm_samples, gnm_summary, _gnm_raw, gnm_hits = run_gnm(universe, observed)
    write_csv(
        RUN_DIR / "06_nullmodel_gnm_samples.csv",
        [
            "trial_id",
            "edge_count",
            "component_count",
            "component_sizes_sorted_desc",
            "largest_component_size",
            "triangle_count",
            "connected_triple_count",
            "closed_triple_count",
            "open_wedge_count",
            "global_closure_ratio",
            "semantic_within_block_edge_count",
            "semantic_cross_block_edge_count",
            "all_edges_within_semantic_blocks",
            "all_components_are_cliques",
            "component_sizes_match_observed_pattern",
            "complete_disjoint_clique_blocks_confirmed",
            "matches_exact_semantic_block_edge_set",
        ],
        gnm_samples,
    )
    write_csv(
        RUN_DIR / "07_nullmodel_gnm_summary.csv",
        [
            "metric",
            "observed_value",
            "trial_count",
            "min",
            "q1",
            "median",
            "mean",
            "q3",
            "max",
            "std",
            "ge_observed_count",
            "le_observed_count",
            "eq_observed_count",
            "empirical_p_ge_observed",
            "empirical_p_le_observed",
            "empirical_p_eq_observed",
            "upper_bound_p_if_zero_hits",
        ],
        gnm_summary,
    )

    degree_samples, degree_summary, _degree_raw, degree_hits = run_degree_preserving(universe, observed)
    write_csv(
        RUN_DIR / "08_nullmodel_degree_preserving_samples.csv",
        [
            "trial_id",
            "edge_count",
            "component_count",
            "component_sizes_sorted_desc",
            "largest_component_size",
            "triangle_count",
            "connected_triple_count",
            "closed_triple_count",
            "open_wedge_count",
            "global_closure_ratio",
            "semantic_within_block_edge_count",
            "semantic_cross_block_edge_count",
            "all_edges_within_semantic_blocks",
            "all_components_are_cliques",
            "component_sizes_match_observed_pattern",
            "complete_disjoint_clique_blocks_confirmed",
            "matches_exact_semantic_block_edge_set",
            "accepted_swaps",
        ],
        degree_samples,
    )
    write_csv(
        RUN_DIR / "09_nullmodel_degree_preserving_summary.csv",
        [
            "metric",
            "observed_value",
            "trial_count",
            "min",
            "q1",
            "median",
            "mean",
            "q3",
            "max",
            "std",
            "ge_observed_count",
            "le_observed_count",
            "eq_observed_count",
            "empirical_p_ge_observed",
            "empirical_p_le_observed",
            "empirical_p_eq_observed",
            "upper_bound_p_if_zero_hits",
        ],
        degree_summary,
    )

    semantic_block_row, semantic_block_hits = run_semantic_block_randomization(universe, node_abs_delta)
    write_csv(
        RUN_DIR / "10_semantic_block_randomization_summary.csv",
        [
            "trial_count",
            "observed_semantic_within_block_edge_count",
            "observed_semantic_cross_block_edge_count",
            "semantic_within_min",
            "semantic_within_median",
            "semantic_within_mean",
            "semantic_within_max",
            "semantic_cross_min",
            "semantic_cross_median",
            "semantic_cross_mean",
            "semantic_cross_max",
            "exact_semantic_block_match_count",
            "empirical_p_exact_semantic_match",
            "upper_bound_p_exact_semantic_match_if_zero_hits",
        ],
        [semantic_block_row],
    )

    pvalue_rows = [
        pvalue_row("gnm_fixed_edge_count", "triangle_count", observed["triangle_count"], ">= observed", gnm_hits["triangle_ge"], GNM_TRIALS),
        pvalue_row("gnm_fixed_edge_count", "global_closure_ratio", observed["global_closure_ratio"], ">= observed", gnm_hits["closure_ge"], GNM_TRIALS),
        pvalue_row("gnm_fixed_edge_count", "open_wedge_count", observed["open_wedge_count"], "<= observed", gnm_hits["open_wedge_le"], GNM_TRIALS),
        pvalue_row("gnm_fixed_edge_count", "semantic_cross_block_edge_count", observed["semantic_cross_block_edge_count"], "<= observed", gnm_hits["semantic_cross_le"], GNM_TRIALS),
        pvalue_row("gnm_fixed_edge_count", "semantic_within_block_edge_count", observed["semantic_within_block_edge_count"], ">= observed", gnm_hits["semantic_within_ge"], GNM_TRIALS),
        pvalue_row("gnm_fixed_edge_count", "complete_disjoint_clique_blocks_confirmed", True, "== true", gnm_hits["complete_blocks"], GNM_TRIALS),
        pvalue_row("gnm_fixed_edge_count", "matches_exact_semantic_block_edge_set", True, "== true", gnm_hits["exact_semantic"], GNM_TRIALS),
        pvalue_row("degree_preserving_edge_swaps", "triangle_count", observed["triangle_count"], ">= observed", degree_hits["triangle_ge"], DEGREE_PRESERVING_TRIALS),
        pvalue_row("degree_preserving_edge_swaps", "global_closure_ratio", observed["global_closure_ratio"], ">= observed", degree_hits["closure_ge"], DEGREE_PRESERVING_TRIALS),
        pvalue_row("degree_preserving_edge_swaps", "open_wedge_count", observed["open_wedge_count"], "<= observed", degree_hits["open_wedge_le"], DEGREE_PRESERVING_TRIALS),
        pvalue_row("degree_preserving_edge_swaps", "semantic_cross_block_edge_count", observed["semantic_cross_block_edge_count"], "<= observed", degree_hits["semantic_cross_le"], DEGREE_PRESERVING_TRIALS),
        pvalue_row("degree_preserving_edge_swaps", "semantic_within_block_edge_count", observed["semantic_within_block_edge_count"], ">= observed", degree_hits["semantic_within_ge"], DEGREE_PRESERVING_TRIALS),
        pvalue_row("degree_preserving_edge_swaps", "complete_disjoint_clique_blocks_confirmed", True, "== true", degree_hits["complete_blocks"], DEGREE_PRESERVING_TRIALS),
        pvalue_row("degree_preserving_edge_swaps", "matches_exact_semantic_block_edge_set", True, "== true", degree_hits["exact_semantic"], DEGREE_PRESERVING_TRIALS),
        pvalue_row("semantic_block_randomization", "exact_semantic_block_match", True, "== true", semantic_block_hits["exact_semantic"], SEMANTIC_BLOCK_RANDOMIZATION_TRIALS),
        pvalue_row("semantic_block_randomization", "semantic_within_block_edge_count", observed["semantic_within_block_edge_count"], ">= observed", semantic_block_hits["semantic_within_ge"], SEMANTIC_BLOCK_RANDOMIZATION_TRIALS),
        pvalue_row("semantic_block_randomization", "semantic_cross_block_edge_count", observed["semantic_cross_block_edge_count"], "<= observed", semantic_block_hits["semantic_cross_le"], SEMANTIC_BLOCK_RANDOMIZATION_TRIALS),
    ]
    write_csv(
        RUN_DIR / "11_nullmodel_pvalue_report.csv",
        [
            "nullmodel",
            "test_name",
            "observed_value",
            "comparison",
            "hit_count",
            "trial_count",
            "empirical_p_with_plus_one",
            "zero_hit_upper_bound",
            "interpretation_boundary",
        ],
        pvalue_rows,
    )

    nullmodel_status = (
        "observed_block_structure_rare_under_tested_nullmodels"
        if gnm_hits["complete_blocks"] <= 1
        and gnm_hits["exact_semantic"] <= 1
        and degree_hits["exact_semantic"] <= 1
        else "nullmodel_results_require_review"
    )
    summary = {
        "run_id": RUN_ID,
        "source_edge_file": str(SOURCE_EDGE_FILE),
        "closure_summary_source": str(CLOSURE_SUMMARY_SOURCE),
        "block_structure_summary_source": str(BLOCK_STRUCTURE_SUMMARY_SOURCE),
        "block_semantics_summary_source": str(BLOCK_SEMANTICS_SUMMARY_SOURCE),
        "strength_profile_context_source": str(STRENGTH_SUMMARY_CONTEXT_SOURCE) if strength_context_present else "",
        "random_seeds": {
            "gnm": GNM_SEED,
            "degree_preserving": DEGREE_PRESERVING_SEED,
            "semantic_block_randomization": SEMANTIC_BLOCK_SEED,
        },
        "observed_node_count": observed["node_count"],
        "observed_possible_edge_count": observed["possible_edge_count"],
        "observed_edge_count": observed["edge_count"],
        "observed_component_sizes": observed["component_sizes_sorted_desc"],
        "observed_triangle_count": observed["triangle_count"],
        "observed_global_closure_ratio": observed["global_closure_ratio"],
        "observed_open_wedge_count": observed["open_wedge_count"],
        "observed_complete_disjoint_clique_blocks_confirmed": observed["complete_disjoint_clique_blocks_confirmed"],
        "observed_semantic_within_block_edge_count": observed["semantic_within_block_edge_count"],
        "observed_semantic_cross_block_edge_count": observed["semantic_cross_block_edge_count"],
        "gnm_trials": GNM_TRIALS,
        "gnm_hits_complete_disjoint_clique_blocks": gnm_hits["complete_blocks"],
        "gnm_hits_exact_semantic_block_edge_set": gnm_hits["exact_semantic"],
        "gnm_empirical_p_complete_disjoint_clique_blocks_plus_one": (gnm_hits["complete_blocks"] + 1) / (GNM_TRIALS + 1),
        "gnm_empirical_p_exact_semantic_block_edge_set_plus_one": (gnm_hits["exact_semantic"] + 1) / (GNM_TRIALS + 1),
        "degree_preserving_trials": DEGREE_PRESERVING_TRIALS,
        "degree_preserving_edge_swap_attempts_per_trial": EDGE_SWAP_ATTEMPTS_PER_TRIAL,
        "degree_preserving_hits_complete_disjoint_clique_blocks": degree_hits["complete_blocks"],
        "degree_preserving_hits_exact_semantic_block_edge_set": degree_hits["exact_semantic"],
        "degree_preserving_empirical_p_complete_disjoint_clique_blocks_plus_one": (degree_hits["complete_blocks"] + 1) / (DEGREE_PRESERVING_TRIALS + 1),
        "degree_preserving_empirical_p_exact_semantic_block_edge_set_plus_one": (degree_hits["exact_semantic"] + 1) / (DEGREE_PRESERVING_TRIALS + 1),
        "semantic_block_randomization_trials": SEMANTIC_BLOCK_RANDOMIZATION_TRIALS,
        "semantic_block_randomization_exact_semantic_match_count": semantic_block_hits["exact_semantic"],
        "semantic_block_randomization_empirical_p_exact_semantic_match_plus_one": (semantic_block_hits["exact_semantic"] + 1) / (SEMANTIC_BLOCK_RANDOMIZATION_TRIALS + 1),
        "nullmodel_status": nullmodel_status,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (RUN_DIR / "04_nullmodel_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    review_note = f"""# QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT

## Source basis

This run uses the EXTRACT03 edge-candidate table and the confirmed closure, block-structure, and block-semantics audit summaries listed in `02_block_nullmodel_audit_scope.md`. Strength-profile context was present: {strength_context_present}.

## Method

The observed candidate graph was reconstructed as an undirected graph on the 42 Pair-ID nodes. Three graph-theoretic controls were run with deterministic seeds: fixed edge-count `G(n,m)`, degree-preserving double-edge swaps, and fixed block-size semantic randomization.

## Observed graph

The observed graph has {observed["node_count"]} nodes, {observed["possible_edge_count"]} possible undirected edges, {observed["edge_count"]} candidate edges, component sizes {observed["component_sizes_sorted_desc"]}, {observed["triangle_count"]} triangles, {observed["open_wedge_count"]} open wedges, and global closure ratio {observed["global_closure_ratio"]}.

## Nullmodel 1: fixed edge count G(n,m)

Trials: {GNM_TRIALS}. Hits for complete disjoint clique blocks: {gnm_hits["complete_blocks"]}. Hits for exact semantic block edge set: {gnm_hits["exact_semantic"]}. Plus-one p-values are reported in `11_nullmodel_pvalue_report.csv`.

## Nullmodel 2: degree-preserving edge swaps

Trials: {DEGREE_PRESERVING_TRIALS}. Edge-swap attempts per trial: {EDGE_SWAP_ATTEMPTS_PER_TRIAL}. Hits for complete disjoint clique blocks: {degree_hits["complete_blocks"]}. Hits for exact semantic block edge set: {degree_hits["exact_semantic"]}.

## Nullmodel 3: semantic block randomization

Trials: {SEMANTIC_BLOCK_RANDOMIZATION_TRIALS}. Exact semantic block match count: {semantic_block_hits["exact_semantic"]}. This control preserves the six block sizes and clique construction while randomizing node assignment.

## Results

The nullmodel status is `{nullmodel_status}`. Zero-hit tests are not reported as `p=0`; plus-one estimates and zero-hit upper bounds are reported.

## Interpretation

This run tests rarity under the specified graph-theoretic nullmodels. The result is only as strong as those nullmodels. It does not establish a general rarity proof outside these controls.

## Claim boundary

This is a structural, graph-theoretic, index-semantic, and statistically descriptive audit only. It makes no physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Next-step gate

Any later use of these results should cite the tested nullmodels, trial counts, deterministic seeds, and plus-one p-value convention. Further interpretation requires separate evidence and separate review.
"""
    (RUN_DIR / "12_nullmodel_review_note.md").write_text(review_note, encoding="utf-8")

    notes = f"""# QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT Distribution Notes

- GNM trials: {GNM_TRIALS}
- Degree-preserving trials: {DEGREE_PRESERVING_TRIALS}
- Semantic block randomization trials: {SEMANTIC_BLOCK_RANDOMIZATION_TRIALS}
- Summary distributions are tabulated in `07_nullmodel_gnm_summary.csv`, `09_nullmodel_degree_preserving_summary.csv`, and `10_semantic_block_randomization_summary.csv`.
- All p-value reports use plus-one empirical estimates; zero-hit cases include `1/(trial_count+1)` as an upper-bound-style reporting field.
- These notes are graph-theoretic only and make no physics claim.
"""
    (RUN_DIR / "13_nullmodel_metric_distribution_notes.md").write_text(notes, encoding="utf-8")

    if closure_summary.get("node_count") != observed["node_count"]:
        raise ValueError("Observed node count differs from closure summary")
    if closure_summary.get("candidate_edge_count") != observed["edge_count"]:
        raise ValueError("Observed edge count differs from closure summary")
    if closure_summary.get("triangle_count") != observed["triangle_count"]:
        raise ValueError("Observed triangle count differs from closure summary")


if __name__ == "__main__":
    main()
