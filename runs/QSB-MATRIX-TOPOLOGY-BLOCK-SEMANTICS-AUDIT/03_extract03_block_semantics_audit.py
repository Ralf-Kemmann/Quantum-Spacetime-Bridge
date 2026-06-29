#!/usr/bin/env python3
"""Audit Pair-ID index semantics for matrix topology clique blocks."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


RUN_ID = "QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT"
RUN_DIR = Path("runs") / RUN_ID

SOURCE_EDGE_FILE = Path(
    "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/"
    "16_edge_candidate_result.csv"
)
CLOSURE_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json")
DEGREE_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/05_degree_summary.csv")
COMPONENT_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/06_component_summary.csv")
TRIANGLE_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/07_triangle_candidates.csv")
BLOCK_STRUCTURE_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json"
)
BLOCK_STRUCTURE_CLIQUE_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/05_component_clique_audit.csv"
)
BLOCK_STRUCTURE_DEGREE_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/06_node_degree_expectation_audit.csv"
)

CLAIM_BOUNDARY = (
    "Purely structural graph-theoretic and index-semantic audit. No claim is made "
    "about physical geometry, spacetime, metric structure, gravitation, causality, "
    "dynamics, experimental validation, or physical emergence."
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


def parse_pair_id(pair_id: str) -> tuple[int, int]:
    parts = pair_id.split("|")
    if len(parts) != 2:
        raise ValueError(f"Pair-ID does not have i|j form: {pair_id}")
    try:
        return int(parts[0]), int(parts[1])
    except ValueError as exc:
        raise ValueError(f"Pair-ID indices are not integer-parseable: {pair_id}") from exc


def pair_sort_key(pair_id: str) -> tuple[int, int]:
    return parse_pair_id(pair_id)


def pair_id(i: int, j: int) -> str:
    return f"{i}|{j}"


def semicolon_join(values: list[object]) -> str:
    return ";".join(str(value) for value in values)


def load_components() -> tuple[list[dict[str, object]], dict[str, int]]:
    components: list[dict[str, object]] = []
    node_to_component: dict[str, int] = {}
    for row in read_csv_rows(COMPONENT_SUMMARY_SOURCE):
        component_id = int(row["component_id"])
        nodes = sorted((node for node in row["nodes"].split(";") if node), key=pair_sort_key)
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
                raise ValueError(f"Pair-ID appears in multiple components: {node}")
            node_to_component[node] = component_id
    components.sort(key=lambda item: int(item["component_id"]))
    return components, node_to_component


def load_edge_file_nodes_and_candidate_edges() -> tuple[set[str], set[tuple[str, str]]]:
    nodes: set[str] = set()
    candidate_edges: set[tuple[str, str]] = set()
    for row in read_csv_rows(SOURCE_EDGE_FILE):
        a = row["pair_a"]
        b = row["pair_b"]
        nodes.add(a)
        nodes.add(b)
        if row["edge_candidate_flag"] == "1":
            candidate_edges.add(tuple(sorted((a, b), key=pair_sort_key)))
    return nodes, candidate_edges


def load_degree_summary() -> dict[str, dict[str, str]]:
    return {row["pair_id"]: row for row in read_csv_rows(DEGREE_SUMMARY_SOURCE)}


def expected_directed_pairs_for_abs_delta(indices: list[int], abs_delta: int) -> list[str]:
    expected: list[str] = []
    index_set = set(indices)
    for i in indices:
        j = i + abs_delta
        if j in index_set:
            expected.append(pair_id(i, j))
            expected.append(pair_id(j, i))
    return sorted(expected, key=pair_sort_key)


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)

    closure_summary = read_json(CLOSURE_SUMMARY_SOURCE)
    block_structure_summary = read_json(BLOCK_STRUCTURE_SUMMARY_SOURCE)
    _triangle_rows = read_csv_rows(TRIANGLE_SOURCE)
    _block_clique_rows = read_csv_rows(BLOCK_STRUCTURE_CLIQUE_SOURCE)
    _block_degree_rows = read_csv_rows(BLOCK_STRUCTURE_DEGREE_SOURCE)

    components, node_to_component = load_components()
    edge_file_nodes, candidate_edges = load_edge_file_nodes_and_candidate_edges()
    degree_summary = load_degree_summary()

    component_nodes = set(node_to_component)
    if edge_file_nodes != component_nodes:
        missing_from_components = sorted(edge_file_nodes - component_nodes, key=pair_sort_key)
        missing_from_edge_file = sorted(component_nodes - edge_file_nodes, key=pair_sort_key)
        raise ValueError(
            "Pair-ID universe mismatch. "
            f"Missing from components: {missing_from_components}; "
            f"missing from edge file: {missing_from_edge_file}"
        )

    parsed_nodes: dict[str, dict[str, object]] = {}
    indices_counter: Counter[int] = Counter()
    for node in sorted(component_nodes, key=pair_sort_key):
        i, j = parse_pair_id(node)
        if j > i:
            orientation = "forward"
        elif j < i:
            orientation = "backward"
        else:
            orientation = "diagonal"
        parsed_nodes[node] = {
            "pair_id": node,
            "i": i,
            "j": j,
            "delta": j - i,
            "abs_delta": abs(j - i),
            "orientation": orientation,
            "min_index": min(i, j),
            "max_index": max(i, j),
        }
        indices_counter[i] += 1
        indices_counter[j] += 1

    indices_present = sorted(indices_counter)
    min_index_global = min(indices_present)
    max_index_global = max(indices_present)
    full_interval_indices = list(range(min_index_global, max_index_global + 1))
    index_count = len(full_interval_indices)
    interval_is_contiguous = indices_present == full_interval_indices

    node_rows: list[dict[str, object]] = []
    for node in sorted(component_nodes, key=pair_sort_key):
        degree_row = degree_summary.get(node, {})
        parsed = parsed_nodes[node]
        node_rows.append(
            {
                "pair_id": node,
                "component_id": node_to_component[node],
                "i": parsed["i"],
                "j": parsed["j"],
                "delta": parsed["delta"],
                "abs_delta": parsed["abs_delta"],
                "orientation": parsed["orientation"],
                "min_index": parsed["min_index"],
                "max_index": parsed["max_index"],
                "candidate_degree": degree_row.get("candidate_degree", ""),
                "triangle_participation": degree_row.get("triangle_participation", ""),
            }
        )

    component_profile_rows: list[dict[str, object]] = []
    component_to_abs_delta_map: dict[str, int | None] = {}
    component_sizes_match_flags: list[bool] = []
    all_components_single_abs_delta_flags: list[bool] = []

    for component in components:
        component_id = int(component["component_id"])
        nodes = list(component["nodes"])
        component_size = int(component["component_size"])
        component_semantics = [parsed_nodes[node] for node in nodes]
        abs_delta_values = sorted({int(item["abs_delta"]) for item in component_semantics})
        delta_values = sorted({int(item["delta"]) for item in component_semantics})
        orientations = Counter(str(item["orientation"]) for item in component_semantics)
        min_indices = [int(item["min_index"]) for item in component_semantics]
        max_indices = [int(item["max_index"]) for item in component_semantics]
        dominant_abs_delta = abs_delta_values[0] if len(abs_delta_values) == 1 else None
        expected_size = (
            2 * (index_count - dominant_abs_delta)
            if dominant_abs_delta is not None
            else ""
        )
        size_matches = expected_size == component_size
        is_single_abs_delta_block = len(abs_delta_values) == 1
        component_to_abs_delta_map[str(component_id)] = dominant_abs_delta
        all_components_single_abs_delta_flags.append(is_single_abs_delta_block)
        component_sizes_match_flags.append(bool(size_matches))
        component_profile_rows.append(
            {
                "component_id": component_id,
                "component_size": component_size,
                "nodes": semicolon_join(nodes),
                "unique_abs_delta_values": semicolon_join(abs_delta_values),
                "unique_delta_values": semicolon_join(delta_values),
                "min_abs_delta": min(abs_delta_values),
                "max_abs_delta": max(abs_delta_values),
                "forward_count": orientations["forward"],
                "backward_count": orientations["backward"],
                "diagonal_count": orientations["diagonal"],
                "min_index_min": min(min_indices),
                "max_index_max": max(max_indices),
                "is_single_abs_delta_block": str(is_single_abs_delta_block).lower(),
                "dominant_abs_delta": dominant_abs_delta if dominant_abs_delta is not None else "",
                "expected_size_for_abs_delta_on_index_range": expected_size,
                "size_matches_abs_delta_rule": str(size_matches).lower(),
            }
        )

    distance_rule_rows: list[dict[str, object]] = []
    distance_rule_flags: list[bool] = []
    for component in components:
        component_id = int(component["component_id"])
        nodes = sorted(list(component["nodes"]), key=pair_sort_key)
        dominant_abs_delta = component_to_abs_delta_map[str(component_id)]
        expected_nodes = (
            expected_directed_pairs_for_abs_delta(full_interval_indices, dominant_abs_delta)
            if dominant_abs_delta is not None
            else []
        )
        observed_set = set(nodes)
        expected_set = set(expected_nodes)
        missing = sorted(expected_set - observed_set, key=pair_sort_key)
        extra = sorted(observed_set - expected_set, key=pair_sort_key)
        distance_rule_complete = (
            dominant_abs_delta is not None
            and len(missing) == 0
            and len(extra) == 0
        )
        distance_rule_flags.append(distance_rule_complete)
        distance_rule_rows.append(
            {
                "component_id": component_id,
                "dominant_abs_delta": dominant_abs_delta if dominant_abs_delta is not None else "",
                "component_size": len(nodes),
                "expected_pair_ids": semicolon_join(expected_nodes),
                "observed_pair_ids": semicolon_join(nodes),
                "missing_pair_ids": semicolon_join(missing),
                "extra_pair_ids": semicolon_join(extra),
                "distance_rule_complete": str(distance_rule_complete).lower(),
            }
        )

    orientation_rows: list[dict[str, object]] = []
    orientation_asymmetry_count = 0
    for i in full_interval_indices:
        for j in full_interval_indices:
            if i >= j:
                continue
            forward_pair = pair_id(i, j)
            backward_pair = pair_id(j, i)
            has_forward = forward_pair in component_nodes
            has_backward = backward_pair in component_nodes
            is_symmetric = has_forward and has_backward
            if not is_symmetric:
                orientation_asymmetry_count += 1
            orientation_rows.append(
                {
                    "abs_delta": j - i,
                    "unordered_pair": f"{i}|{j}",
                    "forward_pair_id": forward_pair,
                    "backward_pair_id": backward_pair,
                    "has_forward": str(has_forward).lower(),
                    "has_backward": str(has_backward).lower(),
                    "is_orientation_symmetric": str(is_symmetric).lower(),
                    "component_id_forward": node_to_component.get(forward_pair, ""),
                    "component_id_backward": node_to_component.get(backward_pair, ""),
                }
            )

    orientation_symmetric_pair_count = len(orientation_rows) - orientation_asymmetry_count
    all_unordered_pairs_orientation_symmetric = orientation_asymmetry_count == 0

    expected_all_directed_pairs = [
        pair_id(i, j)
        for i in full_interval_indices
        for j in full_interval_indices
        if i != j
    ]
    expected_all_directed_pairs.sort(key=pair_sort_key)
    covers_all_directed_non_diagonal_pairs = (
        interval_is_contiguous and set(expected_all_directed_pairs) == component_nodes
    )
    abs_delta_values_present = sorted(
        {int(parsed["abs_delta"]) for parsed in parsed_nodes.values()}
    )

    index_profile_rows = [
        {
            "min_index_global": min_index_global,
            "max_index_global": max_index_global,
            "index_count": index_count,
            "indices_present": semicolon_join(indices_present),
            "abs_delta_values_present": semicolon_join(abs_delta_values_present),
            "total_directed_non_diagonal_pairs_expected": index_count * (index_count - 1),
            "total_pair_ids_observed": len(component_nodes),
            "covers_all_directed_non_diagonal_pairs": str(
                covers_all_directed_non_diagonal_pairs
            ).lower(),
        }
    ]

    write_csv(
        RUN_DIR / "05_pair_id_semantics_by_node.csv",
        [
            "pair_id",
            "component_id",
            "i",
            "j",
            "delta",
            "abs_delta",
            "orientation",
            "min_index",
            "max_index",
            "candidate_degree",
            "triangle_participation",
        ],
        node_rows,
    )
    write_csv(
        RUN_DIR / "06_component_semantics_profile.csv",
        [
            "component_id",
            "component_size",
            "nodes",
            "unique_abs_delta_values",
            "unique_delta_values",
            "min_abs_delta",
            "max_abs_delta",
            "forward_count",
            "backward_count",
            "diagonal_count",
            "min_index_min",
            "max_index_max",
            "is_single_abs_delta_block",
            "dominant_abs_delta",
            "expected_size_for_abs_delta_on_index_range",
            "size_matches_abs_delta_rule",
        ],
        component_profile_rows,
    )
    write_csv(
        RUN_DIR / "07_component_distance_rule_audit.csv",
        [
            "component_id",
            "dominant_abs_delta",
            "component_size",
            "expected_pair_ids",
            "observed_pair_ids",
            "missing_pair_ids",
            "extra_pair_ids",
            "distance_rule_complete",
        ],
        distance_rule_rows,
    )
    write_csv(
        RUN_DIR / "08_orientation_symmetry_audit.csv",
        [
            "abs_delta",
            "unordered_pair",
            "forward_pair_id",
            "backward_pair_id",
            "has_forward",
            "has_backward",
            "is_orientation_symmetric",
            "component_id_forward",
            "component_id_backward",
        ],
        orientation_rows,
    )
    write_csv(
        RUN_DIR / "09_index_interval_profile.csv",
        [
            "min_index_global",
            "max_index_global",
            "index_count",
            "indices_present",
            "abs_delta_values_present",
            "total_directed_non_diagonal_pairs_expected",
            "total_pair_ids_observed",
            "covers_all_directed_non_diagonal_pairs",
        ],
        index_profile_rows,
    )

    all_components_single_abs_delta = all(all_components_single_abs_delta_flags)
    component_sizes_match_abs_delta_rule = all(component_sizes_match_flags)
    all_components_match_distance_rule = all(distance_rule_flags)
    semantic_status = (
        "blocks_correspond_to_directed_pair_index_distance_classes"
        if all_components_single_abs_delta
        and all_components_match_distance_rule
        and component_sizes_match_abs_delta_rule
        and all_unordered_pairs_orientation_symmetric
        and covers_all_directed_non_diagonal_pairs
        else "block_semantics_requires_review"
    )

    component_sizes = [int(component["component_size"]) for component in components]
    summary = {
        "run_id": RUN_ID,
        "source_edge_file": str(SOURCE_EDGE_FILE),
        "closure_component_source": str(COMPONENT_SUMMARY_SOURCE),
        "block_structure_summary_source": str(BLOCK_STRUCTURE_SUMMARY_SOURCE),
        "node_count": len(component_nodes),
        "component_count": len(components),
        "component_sizes": component_sizes,
        "min_index_global": min_index_global,
        "max_index_global": max_index_global,
        "index_count": index_count,
        "indices_present": indices_present,
        "abs_delta_values_present": abs_delta_values_present,
        "covers_all_directed_non_diagonal_pairs": covers_all_directed_non_diagonal_pairs,
        "all_components_single_abs_delta": all_components_single_abs_delta,
        "component_to_abs_delta_map": component_to_abs_delta_map,
        "component_sizes_match_abs_delta_rule": component_sizes_match_abs_delta_rule,
        "all_components_match_distance_rule": all_components_match_distance_rule,
        "all_unordered_pairs_orientation_symmetric": all_unordered_pairs_orientation_symmetric,
        "orientation_symmetric_pair_count": orientation_symmetric_pair_count,
        "orientation_asymmetry_count": orientation_asymmetry_count,
        "semantic_status": semantic_status,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (RUN_DIR / "04_block_semantics_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    review_note = f"""# QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT

## Source basis

This review uses the EXTRACT03 edge-candidate file, the matrix topology closure-test component and degree summaries, and the prior block-structure audit outputs listed in `02_block_semantics_audit_scope.md`.

## Method

Each Pair-ID was parsed as integer `i|j`. The audit derived `delta`, `abs_delta`, orientation, and index interval fields for every node, then tested whether each confirmed clique block corresponds to exactly one absolute index-distance class. It also checked whether each class contains all directed Pair-IDs for that distance over the observed index interval and whether every unordered index pair has both orientations.

## Results

- Node count: {summary["node_count"]}
- Component count: {summary["component_count"]}
- Component sizes: {summary["component_sizes"]}
- Index interval: {summary["min_index_global"]}..{summary["max_index_global"]}
- Indices present: {summary["indices_present"]}
- abs_delta values present: {summary["abs_delta_values_present"]}
- Component to abs_delta map: {summary["component_to_abs_delta_map"]}
- Covers all directed non-diagonal pairs: {summary["covers_all_directed_non_diagonal_pairs"]}
- All components single abs_delta: {summary["all_components_single_abs_delta"]}
- Component sizes match `2*(index_count-d)`: {summary["component_sizes_match_abs_delta_rule"]}
- All components match distance rule: {summary["all_components_match_distance_rule"]}
- All unordered pairs orientation-symmetric: {summary["all_unordered_pairs_orientation_symmetric"]}
- Orientation symmetric pair count: {summary["orientation_symmetric_pair_count"]}
- Orientation asymmetry count: {summary["orientation_asymmetry_count"]}
- Semantic status: `{summary["semantic_status"]}`

## Interpretation

The complete disjoint clique blocks are not only abstract graph components under this audit. They correspond to directed Pair-ID distance classes `abs(i-j)=d` inside the observed index interval 0..6. The block sizes follow the internal index rule `2*(7-d)` for `d=1..6`.

This is an internal relational / index-semantic ordering of the candidate graph. It is not a physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Claim boundary

The semantics described here are limited to Pair-ID parsing and graph/component membership over the audited files. This note makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.

## Next-step gate

Any later use of the distance-class description should cite this run directory and preserve the index-semantic claim boundary. Further interpretation would require separate evidence and separate review.
"""
    (RUN_DIR / "10_block_semantics_review_note.md").write_text(review_note, encoding="utf-8")

    if closure_summary.get("node_count") != len(component_nodes):
        raise ValueError("Node count differs from closure summary")
    if block_structure_summary.get("block_structure_status") != "complete_disjoint_clique_blocks_confirmed":
        raise ValueError("Prior block-structure audit is not confirmed")
    if block_structure_summary.get("node_count") != len(component_nodes):
        raise ValueError("Node count differs from block-structure summary")
    if block_structure_summary.get("candidate_edge_count") != len(candidate_edges):
        raise ValueError("Candidate edge count differs from block-structure summary")


if __name__ == "__main__":
    main()
