#!/usr/bin/env python3
"""Reproducible visualization layer for the EXTRACT03 candidate graph."""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/qsb_matrix_topology_closure_viz_mpl")

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap


RUN_ID = "QSB-MATRIX-TOPOLOGY-CLOSURE-VIZ"
SOURCE_EDGE_FILE = (
    "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/"
    "16_edge_candidate_result.csv"
)
CLOSURE_SUMMARY_SOURCE = "runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json"
DEGREE_SUMMARY_SOURCE = "runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/05_degree_summary.csv"
COMPONENT_SUMMARY_SOURCE = "runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/06_component_summary.csv"
TRIANGLE_SOURCE = "runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/07_triangle_candidates.csv"
REVIEW_NOTE_SOURCE = "runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/08_closure_review_note.md"
CLAIM_BOUNDARY = (
    "Visualization-only structural graph-theoretic review layer. No claim is "
    "made about physical geometry, spacetime, metric structure, gravitation, "
    "causality, dynamics, experimental validation, or physical emergence."
)


def edge_key(node_a: str, node_b: str) -> tuple[str, str]:
    return tuple(sorted((node_a, node_b)))


def read_candidate_graph(source_path: Path) -> tuple[list[str], set[tuple[str, str]]]:
    nodes: set[str] = set()
    candidate_edges: set[tuple[str, str]] = set()

    with source_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            node_a = row["pair_a"]
            node_b = row["pair_b"]
            nodes.add(node_a)
            nodes.add(node_b)
            if row["edge_candidate_flag"] == "1":
                candidate_edges.add(edge_key(node_a, node_b))

    return sorted(nodes), candidate_edges


def read_degree_summary(source_path: Path) -> dict[str, dict[str, int]]:
    degree_summary: dict[str, dict[str, int]] = {}
    with source_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            degree_summary[row["pair_id"]] = {
                "candidate_degree": int(row["candidate_degree"]),
                "triangle_participation": int(row["triangle_participation"]),
            }
    return degree_summary


def read_component_summary(source_path: Path) -> list[dict[str, object]]:
    components: list[dict[str, object]] = []
    with source_path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            nodes = sorted(node for node in row["nodes"].split(";") if node)
            components.append(
                {
                    "component_id": int(row["component_id"]),
                    "component_size": int(row["component_size"]),
                    "nodes": nodes,
                }
            )
    return sorted(components, key=lambda item: int(item["component_id"]))


def build_matrix(node_order: list[str], candidate_edges: set[tuple[str, str]]) -> list[list[int]]:
    matrix: list[list[int]] = []
    for row_node in node_order:
        row_values = []
        for col_node in node_order:
            if row_node == col_node:
                row_values.append(0)
            else:
                row_values.append(1 if edge_key(row_node, col_node) in candidate_edges else 0)
        matrix.append(row_values)
    return matrix


def write_matrix_csv(output_path: Path, node_order: list[str], matrix: list[list[int]]) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["pair_id", *node_order])
        for pair_id, row_values in zip(node_order, matrix):
            writer.writerow([pair_id, *row_values])


def write_component_order_csv(
    output_path: Path,
    component_order: list[tuple[int, str]],
    degree_summary: dict[str, dict[str, int]],
) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "order_index",
                "component_id",
                "pair_id",
                "candidate_degree",
                "triangle_participation",
            ],
            lineterminator="\n",
        )
        writer.writeheader()
        for order_index, (component_id, pair_id) in enumerate(component_order, start=1):
            degree_row = degree_summary[pair_id]
            writer.writerow(
                {
                    "order_index": order_index,
                    "component_id": component_id,
                    "pair_id": pair_id,
                    "candidate_degree": degree_row["candidate_degree"],
                    "triangle_participation": degree_row["triangle_participation"],
                }
            )


def save_heatmap(
    output_path: Path,
    matrix: list[list[int]],
    node_order: list[str],
    title: str,
    component_sizes: list[int] | None = None,
) -> None:
    fig_width = 11.0
    fig_height = 10.0
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=180)
    cmap = ListedColormap(["#f7f7f7", "#2f5d8c"])
    image = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=1, interpolation="nearest")

    ax.set_title(title, fontsize=12, pad=12)
    ax.set_xlabel("Pair ID", fontsize=10)
    ax.set_ylabel("Pair ID", fontsize=10)
    ax.set_xticks(range(len(node_order)))
    ax.set_yticks(range(len(node_order)))
    ax.set_xticklabels(node_order, rotation=90, fontsize=5)
    ax.set_yticklabels(node_order, fontsize=5)
    ax.tick_params(length=0)

    if component_sizes:
        boundary = 0
        for size in component_sizes[:-1]:
            boundary += size
            ax.axhline(boundary - 0.5, color="#111111", linewidth=0.7)
            ax.axvline(boundary - 0.5, color="#111111", linewidth=0.7)

    colorbar = fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04, ticks=[0, 1])
    colorbar.ax.set_yticklabels(["0", "1"])
    colorbar.set_label("Candidate edge flag", fontsize=9)

    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def write_summary(output_path: Path, summary: dict[str, object]) -> None:
    output_path.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def write_review_note(output_path: Path, summary: dict[str, object]) -> None:
    text = f"""# QSB-MATRIX-TOPOLOGY-CLOSURE-VIZ Review Note

## Source Basis

Primary edge source:

`{SOURCE_EDGE_FILE}`

Context sources:

- `{CLOSURE_SUMMARY_SOURCE}`
- `{DEGREE_SUMMARY_SOURCE}`
- `{COMPONENT_SUMMARY_SOURCE}`
- `{TRIANGLE_SOURCE}`
- `{REVIEW_NOTE_SOURCE}`

The source and context artifacts are read-only inputs for this visualization
run. The existing Closure-Test artifacts are not modified.

## Visualization Method

The script builds a binary undirected candidate-adjacency matrix from
`edge_candidate_flag == 1` rows. It writes one matrix in lexicographic Pair-ID
order and one matrix in component order from the Closure-Test component
summary. Heatmaps are rendered with `matplotlib` using a binary color scale
and deterministic node ordering.

## What the Sorted Heatmap Shows

`{summary["sorted_heatmap_file"]}` shows the 42x42 candidate-adjacency matrix
under lexicographic Pair-ID ordering. This view documents the complete binary
candidate relation pattern in a stable order.

## What the Component-Ordered Heatmap Shows

`{summary["component_ordered_heatmap_file"]}` shows the same candidate matrix
after grouping nodes by the Closure-Test connected components. Component
boundary lines mark the reported component sizes: {summary["component_sizes"]}.
The visible blocks are graph-theoretic candidate-graph components.

## Interpretation

The visualizations provide a human-readable review layer for the relational
candidate graph. They support inspection of candidate-edge distribution,
component grouping, and adjacency block structure. They do not add stronger
claims beyond the structural graph-theoretic Closure-Test outputs.

## Claim Boundary

{CLAIM_BOUNDARY}

## Next-Step Gate

Any later step that attempts stronger interpretation must use separate,
explicit validation and must not infer physical geometry, spacetime, metric
structure, gravitation, causality, dynamics, experimental validation, or
physical emergence from these visualization artifacts.
"""
    output_path.write_text(text, encoding="utf-8")


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    run_dir = repo_root / "runs" / RUN_ID

    edge_source_path = repo_root / SOURCE_EDGE_FILE
    closure_summary_path = repo_root / CLOSURE_SUMMARY_SOURCE
    degree_summary_path = repo_root / DEGREE_SUMMARY_SOURCE
    component_summary_path = repo_root / COMPONENT_SUMMARY_SOURCE

    closure_summary = json.loads(closure_summary_path.read_text(encoding="utf-8"))
    sorted_node_order, candidate_edges = read_candidate_graph(edge_source_path)
    degree_summary = read_degree_summary(degree_summary_path)
    components = read_component_summary(component_summary_path)

    sorted_matrix = build_matrix(sorted_node_order, candidate_edges)
    write_matrix_csv(
        run_dir / "04_candidate_adjacency_matrix_sorted.csv",
        sorted_node_order,
        sorted_matrix,
    )
    save_heatmap(
        run_dir / "05_candidate_adjacency_heatmap_sorted.png",
        sorted_matrix,
        sorted_node_order,
        "EXTRACT03 Candidate Adjacency Matrix (Sorted Pair IDs)",
    )

    component_order_pairs = [
        (int(component["component_id"]), node)
        for component in components
        for node in component["nodes"]
    ]
    component_node_order = [pair_id for _, pair_id in component_order_pairs]
    component_matrix = build_matrix(component_node_order, candidate_edges)
    component_sizes = [int(component["component_size"]) for component in components]

    write_component_order_csv(
        run_dir / "06_component_order_node_order.csv",
        component_order_pairs,
        degree_summary,
    )
    write_matrix_csv(
        run_dir / "07_candidate_adjacency_matrix_component_ordered.csv",
        component_node_order,
        component_matrix,
    )
    save_heatmap(
        run_dir / "08_candidate_adjacency_heatmap_component_ordered.png",
        component_matrix,
        component_node_order,
        "EXTRACT03 Candidate Adjacency Matrix (Component Order)",
        component_sizes=component_sizes,
    )

    summary = {
        "run_id": RUN_ID,
        "source_edge_file": SOURCE_EDGE_FILE,
        "closure_summary_source": CLOSURE_SUMMARY_SOURCE,
        "node_count": closure_summary["node_count"],
        "candidate_edge_count": closure_summary["candidate_edge_count"],
        "component_count": closure_summary["component_count"],
        "component_sizes": component_sizes,
        "triangle_count": closure_summary["triangle_count"],
        "global_closure_ratio": closure_summary["global_closure_ratio"],
        "sorted_heatmap_file": "05_candidate_adjacency_heatmap_sorted.png",
        "component_ordered_heatmap_file": "08_candidate_adjacency_heatmap_component_ordered.png",
        "claim_boundary": CLAIM_BOUNDARY,
    }

    write_summary(run_dir / "09_closure_viz_summary.json", summary)
    write_review_note(run_dir / "10_closure_visual_review_note.md", summary)


if __name__ == "__main__":
    main()
