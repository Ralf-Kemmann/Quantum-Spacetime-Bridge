#!/usr/bin/env python3
"""Reproducible graph-level closure test for EXTRACT03 candidate edges."""

from __future__ import annotations

import csv
import itertools
import json
from collections import deque
from pathlib import Path


RUN_ID = "QSB-MATRIX-TOPOLOGY-CLOSURE-TEST"
SOURCE_FILE = (
    "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/"
    "16_edge_candidate_result.csv"
)
CLAIM_BOUNDARY = (
    "Purely structural graph-theoretic closure test. No claim is made about "
    "physical geometry, spacetime, metric structure, gravitation, causality, "
    "dynamics, experimental validation, or physical emergence."
)


def pair_sort_key(pair_id: str) -> tuple[int, ...] | tuple[str]:
    parts = pair_id.split("|")
    try:
        return tuple(int(part) for part in parts)
    except ValueError:
        return (pair_id,)


def edge_key(node_a: str, node_b: str) -> tuple[str, str]:
    return tuple(sorted((node_a, node_b), key=pair_sort_key))


def read_graph(source_path: Path):
    nodes: set[str] = set()
    candidate_edges: dict[tuple[str, str], float] = {}
    edge_candidate_rows_total = 0
    non_candidate_edge_count = 0

    with source_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            edge_candidate_rows_total += 1
            node_a = row["pair_a"]
            node_b = row["pair_b"]
            nodes.add(node_a)
            nodes.add(node_b)

            if row["edge_candidate_flag"] == "1":
                candidate_edges[edge_key(node_a, node_b)] = float(row["strength"])
            else:
                non_candidate_edge_count += 1

    adjacency = {node: set() for node in nodes}
    for node_a, node_b in candidate_edges:
        adjacency[node_a].add(node_b)
        adjacency[node_b].add(node_a)

    return nodes, candidate_edges, adjacency, edge_candidate_rows_total, non_candidate_edge_count


def connected_components(nodes: set[str], adjacency: dict[str, set[str]]) -> list[list[str]]:
    remaining = set(nodes)
    components: list[list[str]] = []

    while remaining:
        start = min(remaining, key=pair_sort_key)
        queue = deque([start])
        remaining.remove(start)
        component = []

        while queue:
            node = queue.popleft()
            component.append(node)
            for neighbor in sorted(adjacency[node], key=pair_sort_key):
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    queue.append(neighbor)

        components.append(sorted(component, key=pair_sort_key))

    return sorted(components, key=lambda item: (-len(item), pair_sort_key(item[0])))


def find_triangles(nodes: set[str], candidate_edges: dict[tuple[str, str], float]):
    triangles = []
    for node_a, node_b, node_c in itertools.combinations(sorted(nodes, key=pair_sort_key), 3):
        edge_ab = edge_key(node_a, node_b)
        edge_ac = edge_key(node_a, node_c)
        edge_bc = edge_key(node_b, node_c)
        if edge_ab in candidate_edges and edge_ac in candidate_edges and edge_bc in candidate_edges:
            strengths = [
                candidate_edges[edge_ab],
                candidate_edges[edge_ac],
                candidate_edges[edge_bc],
            ]
            triangles.append(
                {
                    "node_a": node_a,
                    "node_b": node_b,
                    "node_c": node_c,
                    "edge_ab_strength": strengths[0],
                    "edge_ac_strength": strengths[1],
                    "edge_bc_strength": strengths[2],
                    "min_strength": min(strengths),
                    "mean_strength": sum(strengths) / 3.0,
                }
            )
    return triangles


def write_degree_summary(output_path: Path, degrees: dict[str, int], triangle_nodes: set[str]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["pair_id", "candidate_degree", "triangle_participation"],
            lineterminator="\n",
        )
        writer.writeheader()
        for node in sorted(degrees, key=pair_sort_key):
            writer.writerow(
                {
                    "pair_id": node,
                    "candidate_degree": degrees[node],
                    "triangle_participation": 1 if node in triangle_nodes else 0,
                }
            )


def write_component_summary(output_path: Path, components: list[list[str]]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["component_id", "component_size", "nodes"],
            lineterminator="\n",
        )
        writer.writeheader()
        for index, component in enumerate(components, start=1):
            writer.writerow(
                {
                    "component_id": index,
                    "component_size": len(component),
                    "nodes": ";".join(component),
                }
            )


def write_triangle_candidates(output_path: Path, triangles: list[dict[str, object]]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "node_a",
                "node_b",
                "node_c",
                "edge_ab_strength",
                "edge_ac_strength",
                "edge_bc_strength",
                "min_strength",
                "mean_strength",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for triangle in triangles:
            writer.writerow(triangle)


def write_review_note(output_path: Path, summary: dict[str, object]) -> None:
    text = f"""# QSB-MATRIX-TOPOLOGY-CLOSURE-TEST Review Note

## Source Basis

Primary source file:

`{SOURCE_FILE}`

Only rows with `edge_candidate_flag == 1` are used as candidate edges. All
`pair_a` and `pair_b` IDs appearing in the file are included as graph nodes.
The source file is read-only for this run.

## Method

The test builds an undirected candidate graph from EXTRACT03 Pair-Pair rows.
It computes connected components, node degrees, connected triples, triangles,
closed triples, open wedges, and the global closure ratio. Triangle output is
deterministically sorted by Pair-ID order.

## Results

- node_count: {summary["node_count"]}
- possible_undirected_edges: {summary["possible_undirected_edges"]}
- edge_candidate_rows_total: {summary["edge_candidate_rows_total"]}
- candidate_edge_count: {summary["candidate_edge_count"]}
- non_candidate_edge_count: {summary["non_candidate_edge_count"]}
- candidate_edge_density: {summary["candidate_edge_density"]}
- component_count: {summary["component_count"]}
- largest_component_size: {summary["largest_component_size"]}
- degree_min: {summary["degree_min"]}
- degree_max: {summary["degree_max"]}
- degree_mean: {summary["degree_mean"]}
- connected_triple_count: {summary["connected_triple_count"]}
- triangle_count: {summary["triangle_count"]}
- closed_triple_count: {summary["closed_triple_count"]}
- open_wedge_count: {summary["open_wedge_count"]}
- global_closure_ratio: {summary["global_closure_ratio"]}
- triangle_participating_node_count: {summary["triangle_participating_node_count"]}
- closure_status: {summary["closure_status"]}

## Interpretation

The result reports whether EXTRACT03 candidate edges contain graph-theoretic
closed triples. If `closure_status` is `closed_triples_detected`, this means
only that relational closure candidates were found in the undirected
candidate graph. If `closure_status` is `no_closed_triples_detected`, this
means no such graph-theoretic closed triples were found under this test.

## Claim Boundary

{CLAIM_BOUNDARY}

## Next-Step Gate

Any later step that attempts stronger interpretation must remain gated on
separate, explicit validation. This run does not certify physical geometry,
metric structure, causality, gravitation, dynamics, experimental validation,
or spacetime emergence.
"""
    output_path.write_text(text, encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run_dir = repo_root / "runs" / RUN_ID
    source_path = repo_root / SOURCE_FILE

    (
        nodes,
        candidate_edges,
        adjacency,
        edge_candidate_rows_total,
        non_candidate_edge_count,
    ) = read_graph(source_path)

    node_count = len(nodes)
    possible_undirected_edges = node_count * (node_count - 1) // 2
    candidate_edge_count = len(candidate_edges)
    candidate_edge_density = (
        candidate_edge_count / possible_undirected_edges
        if possible_undirected_edges > 0
        else 0.0
    )

    degrees = {node: len(adjacency[node]) for node in nodes}
    degree_values = list(degrees.values())
    degree_min = min(degree_values) if degree_values else 0
    degree_max = max(degree_values) if degree_values else 0
    degree_mean = sum(degree_values) / node_count if node_count > 0 else 0.0

    components = connected_components(nodes, adjacency)
    triangles = find_triangles(nodes, candidate_edges)
    triangle_nodes = {
        node
        for triangle in triangles
        for node in (triangle["node_a"], triangle["node_b"], triangle["node_c"])
    }

    connected_triple_count = sum(degree * (degree - 1) // 2 for degree in degree_values)
    triangle_count = len(triangles)
    closed_triple_count = 3 * triangle_count
    open_wedge_count = connected_triple_count - closed_triple_count
    global_closure_ratio = (
        closed_triple_count / connected_triple_count
        if connected_triple_count > 0
        else 0.0
    )
    closure_status = (
        "closed_triples_detected"
        if triangle_count > 0
        else "no_closed_triples_detected"
    )

    summary = {
        "run_id": RUN_ID,
        "source_file": SOURCE_FILE,
        "claim_boundary": CLAIM_BOUNDARY,
        "node_count": node_count,
        "possible_undirected_edges": possible_undirected_edges,
        "edge_candidate_rows_total": edge_candidate_rows_total,
        "candidate_edge_count": candidate_edge_count,
        "non_candidate_edge_count": non_candidate_edge_count,
        "candidate_edge_density": candidate_edge_density,
        "component_count": len(components),
        "largest_component_size": len(components[0]) if components else 0,
        "degree_min": degree_min,
        "degree_max": degree_max,
        "degree_mean": degree_mean,
        "connected_triple_count": connected_triple_count,
        "triangle_count": triangle_count,
        "closed_triple_count": closed_triple_count,
        "open_wedge_count": open_wedge_count,
        "global_closure_ratio": global_closure_ratio,
        "triangle_participating_node_count": len(triangle_nodes),
        "closure_status": closure_status,
    }

    (run_dir / "04_closure_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_degree_summary(run_dir / "05_degree_summary.csv", degrees, triangle_nodes)
    write_component_summary(run_dir / "06_component_summary.csv", components)
    write_triangle_candidates(run_dir / "07_triangle_candidates.csv", triangles)
    write_review_note(run_dir / "08_closure_review_note.md", summary)


if __name__ == "__main__":
    main()
