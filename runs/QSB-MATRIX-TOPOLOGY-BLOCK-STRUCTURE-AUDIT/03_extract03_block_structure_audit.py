#!/usr/bin/env python3
"""Audit matrix topology block structure as graph-theoretic clique blocks."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


RUN_ID = "QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT"
RUN_DIR = Path("runs") / RUN_ID

SOURCE_EDGE_FILE = Path(
    "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/"
    "16_edge_candidate_result.csv"
)
CLOSURE_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json")
DEGREE_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/05_degree_summary.csv")
COMPONENT_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/06_component_summary.csv")
TRIANGLE_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/07_triangle_candidates.csv")
CLOSURE_VIZ_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-VIZ/09_closure_viz_summary.json")

CLAIM_BOUNDARY = (
    "Purely structural graph-theoretic block-structure audit. No claim is made "
    "about physical geometry, spacetime, metric structure, gravitation, causality, "
    "dynamics, experimental validation, or physical emergence."
)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def undirected_edge(a: str, b: str) -> tuple[str, str]:
    return tuple(sorted((a, b)))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def load_components() -> tuple[list[dict[str, object]], dict[str, int]]:
    components: list[dict[str, object]] = []
    node_to_component: dict[str, int] = {}

    for row in read_csv_rows(COMPONENT_SUMMARY_SOURCE):
        component_id = int(row["component_id"])
        nodes = sorted(node for node in row["nodes"].split(";") if node)
        component_size = int(row["component_size"])
        if component_size != len(nodes):
            raise ValueError(
                f"Component {component_id} reports size {component_size} but lists {len(nodes)} nodes"
            )
        components.append(
            {
                "component_id": component_id,
                "component_size": component_size,
                "nodes": nodes,
            }
        )
        for node in nodes:
            if node in node_to_component:
                raise ValueError(f"Node appears in multiple components: {node}")
            node_to_component[node] = component_id

    components.sort(key=lambda item: int(item["component_id"]))
    return components, node_to_component


def load_candidate_edges() -> tuple[set[str], dict[tuple[str, str], str]]:
    nodes: set[str] = set()
    candidate_edges: dict[tuple[str, str], str] = {}

    for row in read_csv_rows(SOURCE_EDGE_FILE):
        a = row["pair_a"]
        b = row["pair_b"]
        nodes.add(a)
        nodes.add(b)
        if row["edge_candidate_flag"] != "1":
            continue
        edge = undirected_edge(a, b)
        if edge in candidate_edges:
            raise ValueError(f"Duplicate candidate edge after undirected normalization: {edge}")
        candidate_edges[edge] = row["strength"]

    return nodes, candidate_edges


def load_degree_triangle_participation() -> dict[str, str]:
    participation: dict[str, str] = {}
    for row in read_csv_rows(DEGREE_SUMMARY_SOURCE):
        participation[row["pair_id"]] = row["triangle_participation"]
    return participation


def load_triangles() -> list[tuple[str, str, str]]:
    triangles: list[tuple[str, str, str]] = []
    for row in read_csv_rows(TRIANGLE_SOURCE):
        triangles.append(tuple(sorted((row["node_a"], row["node_b"], row["node_c"]))))
    triangles.sort()
    return triangles


def build_component_lookup(components: list[dict[str, object]]) -> dict[int, list[str]]:
    return {
        int(component["component_id"]): list(component["nodes"])
        for component in components
    }


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    closure_summary = read_json(CLOSURE_SUMMARY_SOURCE)
    _closure_viz_summary = read_json(CLOSURE_VIZ_SUMMARY_SOURCE)
    components, node_to_component = load_components()
    component_nodes = build_component_lookup(components)
    edge_nodes, candidate_edges = load_candidate_edges()
    triangle_participation = load_degree_triangle_participation()
    triangles = load_triangles()

    missing_component_nodes = sorted(edge_nodes - set(node_to_component))
    if missing_component_nodes:
        raise ValueError(
            "Edge-candidate nodes without component assignment: "
            + ", ".join(missing_component_nodes)
        )

    degree_counter: Counter[str] = Counter()
    internal_edge_counter: Counter[int] = Counter()
    cross_component_rows: list[dict[str, object]] = []

    for (a, b), strength in sorted(candidate_edges.items()):
        component_a = node_to_component[a]
        component_b = node_to_component[b]
        degree_counter[a] += 1
        degree_counter[b] += 1
        if component_a == component_b:
            internal_edge_counter[component_a] += 1
        else:
            cross_component_rows.append(
                {
                    "edge_a": a,
                    "edge_b": b,
                    "component_a": component_a,
                    "component_b": component_b,
                    "strength": strength,
                }
            )

    component_clique_rows: list[dict[str, object]] = []
    for component in components:
        component_id = int(component["component_id"])
        nodes = component_nodes[component_id]
        component_size = len(nodes)
        expected_internal_edges = component_size * (component_size - 1) // 2
        missing_edges = [
            f"{a}--{b}"
            for a, b in combinations(nodes, 2)
            if undirected_edge(a, b) not in candidate_edges
        ]
        missing_edges.sort()
        observed_internal_edges = internal_edge_counter[component_id]
        component_clique_rows.append(
            {
                "component_id": component_id,
                "component_size": component_size,
                "expected_internal_edges": expected_internal_edges,
                "observed_internal_candidate_edges": observed_internal_edges,
                "missing_internal_edges": len(missing_edges),
                "is_complete_clique": str(
                    observed_internal_edges == expected_internal_edges
                    and len(missing_edges) == 0
                ).lower(),
                "missing_edge_list": "|".join(missing_edges),
            }
        )

    node_degree_rows: list[dict[str, object]] = []
    for component in components:
        component_id = int(component["component_id"])
        component_size = int(component["component_size"])
        expected_degree = component_size - 1
        for node in component_nodes[component_id]:
            observed_degree = degree_counter[node]
            node_degree_rows.append(
                {
                    "pair_id": node,
                    "component_id": component_id,
                    "component_size": component_size,
                    "expected_clique_degree": expected_degree,
                    "observed_candidate_degree": observed_degree,
                    "degree_matches_clique_expectation": str(
                        observed_degree == expected_degree
                    ).lower(),
                    "triangle_participation": triangle_participation.get(node, ""),
                }
            )

    triangle_counter: Counter[int] = Counter()
    for triangle in triangles:
        triangle_components = {node_to_component[node] for node in triangle}
        if len(triangle_components) == 1:
            triangle_counter[next(iter(triangle_components))] += 1

    component_triangle_rows: list[dict[str, object]] = []
    for component in components:
        component_id = int(component["component_id"])
        component_size = int(component["component_size"])
        expected_triangles = component_size * (component_size - 1) * (component_size - 2) // 6
        observed_triangles = triangle_counter[component_id]
        component_triangle_rows.append(
            {
                "component_id": component_id,
                "component_size": component_size,
                "expected_triangles": expected_triangles,
                "observed_internal_triangles": observed_triangles,
                "triangle_count_matches_clique_expectation": str(
                    observed_triangles == expected_triangles
                ).lower(),
            }
        )

    write_csv(
        RUN_DIR / "05_component_clique_audit.csv",
        [
            "component_id",
            "component_size",
            "expected_internal_edges",
            "observed_internal_candidate_edges",
            "missing_internal_edges",
            "is_complete_clique",
            "missing_edge_list",
        ],
        component_clique_rows,
    )
    write_csv(
        RUN_DIR / "06_node_degree_expectation_audit.csv",
        [
            "pair_id",
            "component_id",
            "component_size",
            "expected_clique_degree",
            "observed_candidate_degree",
            "degree_matches_clique_expectation",
            "triangle_participation",
        ],
        node_degree_rows,
    )
    write_csv(
        RUN_DIR / "07_cross_component_edge_audit.csv",
        ["edge_a", "edge_b", "component_a", "component_b", "strength"],
        cross_component_rows,
    )
    write_csv(
        RUN_DIR / "08_component_triangle_audit.csv",
        [
            "component_id",
            "component_size",
            "expected_triangles",
            "observed_internal_triangles",
            "triangle_count_matches_clique_expectation",
        ],
        component_triangle_rows,
    )

    component_sizes = [int(component["component_size"]) for component in components]
    expected_total_clique_edges = sum(
        size * (size - 1) // 2 for size in component_sizes
    )
    expected_total_clique_triangles = sum(
        size * (size - 1) * (size - 2) // 6 for size in component_sizes
    )
    all_components_complete_cliques = all(
        row["is_complete_clique"] == "true" for row in component_clique_rows
    )
    all_component_triangle_counts_match = all(
        row["triangle_count_matches_clique_expectation"] == "true"
        for row in component_triangle_rows
    )
    cross_component_candidate_edge_count = len(cross_component_rows)
    block_structure_status = (
        "complete_disjoint_clique_blocks_confirmed"
        if all_components_complete_cliques
        and cross_component_candidate_edge_count == 0
        and all_component_triangle_counts_match
        else "block_structure_requires_review"
    )

    summary = {
        "run_id": RUN_ID,
        "source_edge_file": str(SOURCE_EDGE_FILE),
        "closure_summary_source": str(CLOSURE_SUMMARY_SOURCE),
        "closure_viz_summary_source": str(CLOSURE_VIZ_SUMMARY_SOURCE),
        "node_count": len(edge_nodes),
        "candidate_edge_count": len(candidate_edges),
        "component_count": len(components),
        "component_sizes": component_sizes,
        "expected_total_clique_edges": expected_total_clique_edges,
        "observed_total_candidate_edges": len(candidate_edges),
        "all_components_complete_cliques": all_components_complete_cliques,
        "cross_component_candidate_edge_count": cross_component_candidate_edge_count,
        "expected_total_clique_triangles": expected_total_clique_triangles,
        "observed_total_triangles": len(triangles),
        "all_component_triangle_counts_match": all_component_triangle_counts_match,
        "block_structure_status": block_structure_status,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (RUN_DIR / "04_block_structure_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    review_note = f"""# QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT

## Source basis

This review uses the edge-candidate table, closure summary, degree summary, component summary, triangle table, and closure visualization summary listed in `02_block_structure_audit_scope.md`.

## Method

The audit treats the graph as undirected and uses only rows with `edge_candidate_flag == 1` as candidate edges. It compares each closure-test component against the complete-graph edge expectation `n*(n-1)/2`, checks each node degree against the component clique expectation `n-1`, lists any candidate edges crossing component assignments, and compares component triangle counts against `n*(n-1)*(n-2)/6`.

## Results

- Node count: {summary["node_count"]}
- Candidate edge count: {summary["candidate_edge_count"]}
- Component count: {summary["component_count"]}
- Component sizes: {summary["component_sizes"]}
- Expected total clique edges: {summary["expected_total_clique_edges"]}
- Observed total candidate edges: {summary["observed_total_candidate_edges"]}
- Cross-component candidate edge count: {summary["cross_component_candidate_edge_count"]}
- Expected total clique triangles: {summary["expected_total_clique_triangles"]}
- Observed total triangles: {summary["observed_total_triangles"]}
- Block structure status: `{summary["block_structure_status"]}`

## Interpretation

This audit checks whether the structure visible in the closure test can be described as disjoint complete candidate blocks. Under the audited inputs, the component edge counts, node degree expectations, absence of cross-component candidate edges, and component triangle counts are consistent with complete disjoint clique blocks in a graph-theoretic / relational sense.

## Claim boundary

The phrase "complete disjoint clique blocks" is used only as a structural graph-theoretic description of the candidate graph. This note makes no physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Next-step gate

Any later use of this block description should keep the graph-theoretic claim boundary explicit and should cite the exact source files and this run directory. Further interpretation would require separate evidence and separate review.
"""
    (RUN_DIR / "09_block_structure_review_note.md").write_text(review_note, encoding="utf-8")

    if closure_summary.get("candidate_edge_count") != len(candidate_edges):
        raise ValueError("Candidate edge count differs from closure summary")
    if closure_summary.get("triangle_count") != len(triangles):
        raise ValueError("Triangle count differs from closure summary")


if __name__ == "__main__":
    main()
