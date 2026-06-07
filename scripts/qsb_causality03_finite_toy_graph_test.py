#!/usr/bin/env python3
"""Deterministic finite toy-graph test for QSB-CAUSALITY03."""

import argparse
import csv
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

NODES = ["X0", "X1", "X2", "X3", "X4", "X5"]
EDGES_VARIANT_A = [
    ("X0", "X1"),
    ("X0", "X2"),
    ("X1", "X3"),
    ("X1", "X4"),
    ("X2", "X4"),
    ("X3", "X5"),
    ("X4", "X5"),
]
EDGES_VARIANT_B = EDGES_VARIANT_A + [("X4", "X1")]
EXPECTED_OUTPUT_FILES = [
    "qsb_causality03_readout.md",
    "qsb_causality03_summary.json",
    "qsb_causality03_node_catalog.csv",
    "qsb_causality03_edge_catalog.csv",
    "qsb_causality03_predicate_assignment.csv",
    "qsb_causality03_continuation_spaces.csv",
    "qsb_causality03_fixation_sets.csv",
    "qsb_causality03_refined_admissibility.csv",
    "qsb_causality03_direction_candidates.csv",
    "qsb_causality03_counterexample_assessment.csv",
    "qsb_causality03_final_status.csv",
]

PREDICATES = {
    "f_A": {"X0": 1, "X1": 1, "X2": 1, "X3": 1, "X4": 0, "X5": 0},
    "f_B": {"X0": 0, "X1": 1, "X2": 0, "X3": 1, "X4": 1, "X5": 1},
    "f_C": {"X0": 1, "X1": 1, "X2": 1, "X3": 0, "X4": 1, "X5": 1},
    "f_D": {node: 1 for node in NODES},
    "f_E": {"X0": 0, "X1": 1, "X2": 0, "X3": 1, "X4": 1, "X5": 1},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Finite toy graph test for QSB-CAUSALITY03")
    parser.add_argument("--output-dir", default="runs/QSB-CAUSALITY/QSB_CAUSALITY03_FINITE_TOY_GRAPH", help="Output directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing output files")
    return parser.parse_args()


def build_graph(edges: List[Tuple[str, str]]) -> Dict[str, Set[str]]:
    graph = {node: set() for node in NODES}
    for a, b in edges:
        graph[a].add(b)
    return graph


def reachable(graph: Dict[str, Set[str]], start: str) -> Set[str]:
    seen = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        for nxt in graph[node]:
            if nxt not in seen:
                stack.append(nxt)
    return seen


def compute_reachability(graph: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    return {node: reachable(graph, node) for node in NODES}


def tarjan_scc(graph: Dict[str, Set[str]]) -> List[Set[str]]:
    index_counter = 0
    index = {}
    lowlink = {}
    stack = []
    on_stack = set()
    components = []

    def visit(node: str) -> None:
        nonlocal index_counter
        index[node] = index_counter
        lowlink[node] = index_counter
        index_counter += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in graph[node]:
            if nxt not in index:
                visit(nxt)
                lowlink[node] = min(lowlink[node], lowlink[nxt])
            elif nxt in on_stack:
                lowlink[node] = min(lowlink[node], index[nxt])
        if lowlink[node] == index[node]:
            component = set()
            while True:
                w = stack.pop()
                on_stack.remove(w)
                component.add(w)
                if w == node:
                    break
            components.append(component)

    for node in NODES:
        if node not in index:
            visit(node)
    return components


def fixation_sets(reachability: Dict[str, Set[str]], predicates: Dict[str, Dict[str, int]]) -> Dict[str, List[str]]:
    fixation = {}
    for node in NODES:
        fixed = [name for name, values in predicates.items() if all(values.get(y, 0) == 1 for y in reachability[node])]
        fixation[node] = fixed
    return fixation


def strict_reduction_map(reachability: Dict[str, Set[str]], edges: List[Tuple[str, str]]) -> Dict[Tuple[str, str], bool]:
    return {(src, dst): (reachability[dst] < reachability[src]) for src, dst in edges}


def refined_admissibility(fixation: Dict[str, List[str]], edges: List[Tuple[str, str]]) -> Dict[Tuple[str, str], bool]:
    return {(src, dst): set(fixation[src]).issubset(set(fixation[dst])) for src, dst in edges}


def direction_candidates(edges: List[Tuple[str, str]], refined: Dict[Tuple[str, str], bool], strict: Dict[Tuple[str, str], bool]) -> List[Dict[str, object]]:
    return [{"source": src, "target": dst, "reason": "refined admissible and strictly reduced"} for src, dst in edges if refined[(src, dst)] and strict[(src, dst)]]


def write_csv(path: Path, header: List[str], rows: Iterable[List[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, payload: Dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def remove_expected_outputs(out_dir: Path) -> None:
    for name in EXPECTED_OUTPUT_FILES:
        path = out_dir / name
        if path.exists():
            path.unlink()


def output_set_is_exact(out_dir: Path) -> bool:
    if not out_dir.exists():
        return False
    return sorted(path.name for path in out_dir.iterdir() if path.is_file()) == sorted(EXPECTED_OUTPUT_FILES)


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)

    if out_dir.exists() and not args.overwrite:
        print(f"Refusing to overwrite existing output directory: {out_dir}", file=sys.stderr)
        sys.exit(2)

    if out_dir.exists() and args.overwrite:
        unexpected = [item.name for item in out_dir.iterdir() if item.name not in EXPECTED_OUTPUT_FILES]
        if unexpected:
            print(f"Unexpected existing files in {out_dir}: {unexpected}", file=sys.stderr)
            sys.exit(2)
        remove_expected_outputs(out_dir)

    out_dir.mkdir(parents=True, exist_ok=True)

    graph_a = build_graph(EDGES_VARIANT_A)
    graph_b = build_graph(EDGES_VARIANT_B)
    reach_a = compute_reachability(graph_a)
    reach_b = compute_reachability(graph_b)
    scc_a = tarjan_scc(graph_a)
    scc_b = tarjan_scc(graph_b)
    nontrivial_sccs = [component for component in scc_b if len(component) > 1]
    internal_cycle_edges = [edge for edge in EDGES_VARIANT_B if any(set(edge).issubset(component) for component in nontrivial_sccs)]

    fixation_a = fixation_sets(reach_a, PREDICATES)
    fixation_b = fixation_sets(reach_b, PREDICATES)
    refined_a = refined_admissibility(fixation_a, EDGES_VARIANT_A)
    refined_b = refined_admissibility(fixation_b, EDGES_VARIANT_B)
    strict_a = strict_reduction_map(reach_a, EDGES_VARIANT_A)
    strict_b = strict_reduction_map(reach_b, EDGES_VARIANT_B)

    candidates_a = direction_candidates(EDGES_VARIANT_A, refined_a, strict_a)
    candidates_b = direction_candidates(EDGES_VARIANT_B, refined_b, strict_b)

    predicate_assignments = {name: tuple(values[node] for node in NODES) for name, values in PREDICATES.items()}
    redundant_predicate_pairs = [(name1, name2) for name1, name2 in combinations(predicate_assignments, 2) if predicate_assignments[name1] == predicate_assignments[name2]]
    universally_true_predicate_detected = any(all(value == 1 for value in values.values()) for values in PREDICATES.values())

    fixation_loss_found = [(node, predicate) for node in NODES for predicate in PREDICATES if predicate in fixation_a[node] and predicate not in fixation_b[node]]

    check_variant_a_acyclic = all(len(component) == 1 for component in scc_a)
    check_variant_b_cycle_detected = bool(nontrivial_sccs)
    check_all_variant_a_edges_strictly_reduce = all(strict_a[edge] for edge in EDGES_VARIANT_A)
    check_all_internal_scc_edges_blocked = all(not strict_b[edge] for edge in internal_cycle_edges)
    check_fixation_sets_computed = bool(fixation_a and fixation_b)
    check_fixation_loss_detected = bool(fixation_loss_found)
    check_redundancy_detected = bool(redundant_predicate_pairs)
    check_tau_not_used_for_direction = True
    check_exact_output_set = False
    checks = {
        "check_variant_a_acyclic": check_variant_a_acyclic,
        "check_variant_b_cycle_detected": check_variant_b_cycle_detected,
        "check_all_variant_a_edges_strictly_reduce": check_all_variant_a_edges_strictly_reduce,
        "check_all_internal_scc_edges_blocked": check_all_internal_scc_edges_blocked,
        "check_fixation_sets_computed": check_fixation_sets_computed,
        "check_fixation_loss_detected": check_fixation_loss_detected,
        "check_redundancy_detected": check_redundancy_detected,
        "check_tau_not_used_for_direction": check_tau_not_used_for_direction,
        "check_exact_output_set": check_exact_output_set,
    }
    all_checks_passed = all(checks.values())

    counterexample_rows = []
    for edge in internal_cycle_edges:
        counterexample_rows.append(["B", edge[0], edge[1], "cycle-edge", "strict reduction is blocked within SCC", "yes" if not strict_b[edge] else "no"])
    if not counterexample_rows:
        counterexample_rows.append(["B", "X4", "X1", "cycle-edge", "no internal SCC edge detected", "n/a"])

    summary = {
        "research_block": "QSB-CAUSALITY03",
        "variant_a_nodes": len(NODES),
        "variant_a_edges": len(EDGES_VARIANT_A),
        "variant_b_nodes": len(NODES),
        "variant_b_edges": len(EDGES_VARIANT_B),
        "continuation_spaces_computed": True,
        "fixation_sets_computed": check_fixation_sets_computed,
        "refined_admissibility_computed": True,
        "direction_candidates_computed": True,
        "variant_a_acyclic": check_variant_a_acyclic,
        "variant_b_cycle_detected": check_variant_b_cycle_detected,
        "all_variant_a_edges_strictly_reduce": check_all_variant_a_edges_strictly_reduce,
        "nontrivial_scc_count_variant_b": len(nontrivial_sccs),
        "internal_cycle_edge_count": len(internal_cycle_edges),
        "strict_reduction_blocks_cycle_edges": check_all_internal_scc_edges_blocked,
        "fixation_loss_detected": check_fixation_loss_detected,
        "fixation_losses": [{"node": node, "predicate": predicate} for node, predicate in fixation_loss_found],
        "redundant_fixation_detected": check_redundancy_detected,
        "redundant_predicate_pairs": [{"predicate_1": name1, "predicate_2": name2} for name1, name2 in redundant_predicate_pairs],
        "universally_true_predicate_detected": universally_true_predicate_detected,
        "universally_true_predicates": [name for name, values in PREDICATES.items() if all(value == 1 for value in values.values())],
        "tau_used_for_direction": False,
        "physical_data_used": False,
        "physical_claim_made": False,
        "additional_gate_created": False,
        "all_checks_passed": all_checks_passed,
        "exact_output_set": False,
        "final_status": "finite_toy_graph_framework_test_passed_with_counterexample" if all_checks_passed else "finite_toy_graph_framework_test_failed",
        "limitations": "Deterministic finite toy-graph test only; no physical interpretation is claimed.",
    }

    write_csv(out_dir / "qsb_causality03_node_catalog.csv", ["node"], [[node] for node in NODES])
    write_csv(out_dir / "qsb_causality03_edge_catalog.csv", ["variant", "source", "target"], [("A", src, dst) for src, dst in EDGES_VARIANT_A] + [("B", src, dst) for src, dst in EDGES_VARIANT_B])
    write_csv(out_dir / "qsb_causality03_predicate_assignment.csv", ["predicate", "node", "value"], [[name, node, value] for name, values in PREDICATES.items() for node, value in values.items()])
    write_csv(out_dir / "qsb_causality03_continuation_spaces.csv", ["variant", "node", "reachable_nodes"], [["A", node, ",".join(sorted(reach_a[node]))] for node in NODES] + [["B", node, ",".join(sorted(reach_b[node]))] for node in NODES])
    write_csv(out_dir / "qsb_causality03_fixation_sets.csv", ["variant", "node", "fixation_set"], [["A", node, ",".join(sorted(fixation_a[node]))] for node in NODES] + [["B", node, ",".join(sorted(fixation_b[node]))] for node in NODES])
    write_csv(out_dir / "qsb_causality03_refined_admissibility.csv", ["variant", "source", "target", "refined_admissible"], [["A", src, dst, "yes" if refined_a[(src, dst)] else "no"] for src, dst in EDGES_VARIANT_A] + [["B", src, dst, "yes" if refined_b[(src, dst)] else "no"] for src, dst in EDGES_VARIANT_B])
    write_csv(out_dir / "qsb_causality03_direction_candidates.csv", ["variant", "source", "target", "reason"], [["A", item["source"], item["target"], item["reason"]] for item in candidates_a] + [["B", item["source"], item["target"], item["reason"]] for item in candidates_b])
    write_csv(out_dir / "qsb_causality03_counterexample_assessment.csv", ["variant", "source", "target", "status", "note", "evidence"], counterexample_rows)

    final_status_header = [
        "research_block", "variant_a_nodes", "variant_a_edges", "variant_b_nodes", "variant_b_edges",
        "continuation_spaces_computed", "fixation_sets_computed", "refined_admissibility_computed", "direction_candidates_computed",
        "variant_a_acyclic", "variant_b_cycle_detected", "strict_reduction_blocks_cycle_edges", "redundant_fixation_detected",
        "tau_used_for_direction", "physical_data_used", "physical_claim_made", "additional_gate_created", "final_status", "limitations",
    ]
    final_status_row = [
        summary["research_block"], summary["variant_a_nodes"], summary["variant_a_edges"], summary["variant_b_nodes"], summary["variant_b_edges"],
        "yes" if summary["continuation_spaces_computed"] else "no", "yes" if summary["fixation_sets_computed"] else "no",
        "yes" if summary["refined_admissibility_computed"] else "no", "yes" if summary["direction_candidates_computed"] else "no",
        "yes" if summary["variant_a_acyclic"] else "no", "yes" if summary["variant_b_cycle_detected"] else "no",
        "yes" if summary["strict_reduction_blocks_cycle_edges"] else "no", "yes" if summary["redundant_fixation_detected"] else "no",
        "yes" if summary["tau_used_for_direction"] else "no", "yes" if summary["physical_data_used"] else "no",
        "yes" if summary["physical_claim_made"] else "no", "yes" if summary["additional_gate_created"] else "no",
        summary["final_status"], summary["limitations"],
    ]
    write_csv(out_dir / "qsb_causality03_final_status.csv", final_status_header, [final_status_row])
    write_json(out_dir / "qsb_causality03_summary.json", summary)

    fixation_loss_lines = [
        f"- {node}: {predicate}" for node, predicate in fixation_loss_found
    ] or ["- none"]
    redundant_pair_lines = [
        f"- {name1} / {name2}" for name1, name2 in redundant_predicate_pairs
    ] or ["- none"]
    universally_true_lines = [
        f"- {name}" for name, values in PREDICATES.items() if all(value == 1 for value in values.values())
    ] or ["- none"]

    def build_readout() -> List[str]:
        return [
        "# QSB-CAUSALITY03 finite toy graph test",
        "",
        "This run uses only six deterministic nodes and two finite variants of the toy graph.",
        "Variant A is acyclic; Variant B adds the cycle edge to create a nontrivial SCC class.",
        "The script computes reachability, fixation sets, refined admissibility, and direction candidates without any physical data.",
        "",
        "## Derived checks",
        f"- all_checks_passed: {'yes' if summary['all_checks_passed'] else 'no'}",
        f"- variant_a_acyclic: {'yes' if summary['variant_a_acyclic'] else 'no'}",
        f"- variant_b_cycle_detected: {'yes' if summary['variant_b_cycle_detected'] else 'no'}",
        f"- all_variant_a_edges_strictly_reduce: {'yes' if summary['all_variant_a_edges_strictly_reduce'] else 'no'}",
        f"- nontrivial_scc_count_variant_b: {summary['nontrivial_scc_count_variant_b']}",
        f"- internal_cycle_edge_count: {summary['internal_cycle_edge_count']}",
        f"- strict_reduction_blocks_cycle_edges: {'yes' if summary['strict_reduction_blocks_cycle_edges'] else 'no'}",
        f"- fixation_loss_detected: {'yes' if summary['fixation_loss_detected'] else 'no'}",
        f"- redundant_fixation_detected: {'yes' if summary['redundant_fixation_detected'] else 'no'}",
        f"- universally_true_predicate_detected: {'yes' if summary['universally_true_predicate_detected'] else 'no'}",
        f"- tau_used_for_direction: {'yes' if summary['tau_used_for_direction'] else 'no'}",
        f"- exact_output_set: {'yes' if summary['exact_output_set'] else 'no'}",
        f"- final_status: {summary['final_status']}",
        "",
        "## Predicate observations",
        "- f_D is universally true and therefore detected as a universally true predicate.",
        "- f_B and f_E are identical assignments, so redundant predicate pairs are detected algorithmically.",
        "- Fixation losses are computed by comparing F_A and F_B node by node.",
        "",
        "## Fixation losses",
        *fixation_loss_lines,
        "",
        "## Redundant predicate pairs",
        *redundant_pair_lines,
        "",
        "## Universally true predicates",
        *universally_true_lines,
        ]

    readout = build_readout()
    (out_dir / "qsb_causality03_readout.md").write_text("\n".join(readout) + "\n", encoding="utf-8")

    summary["exact_output_set"] = output_set_is_exact(out_dir)
    summary["check_exact_output_set"] = summary["exact_output_set"]
    checks["check_exact_output_set"] = summary["exact_output_set"]
    summary["all_checks_passed"] = all(checks.values())
    summary["final_status"] = "finite_toy_graph_framework_test_passed_with_counterexample" if summary["all_checks_passed"] else "finite_toy_graph_framework_test_failed"

    final_status_row = [
        summary["research_block"], summary["variant_a_nodes"], summary["variant_a_edges"], summary["variant_b_nodes"], summary["variant_b_edges"],
        "yes" if summary["continuation_spaces_computed"] else "no", "yes" if summary["fixation_sets_computed"] else "no",
        "yes" if summary["refined_admissibility_computed"] else "no", "yes" if summary["direction_candidates_computed"] else "no",
        "yes" if summary["variant_a_acyclic"] else "no", "yes" if summary["variant_b_cycle_detected"] else "no",
        "yes" if summary["strict_reduction_blocks_cycle_edges"] else "no", "yes" if summary["redundant_fixation_detected"] else "no",
        "yes" if summary["tau_used_for_direction"] else "no", "yes" if summary["physical_data_used"] else "no",
        "yes" if summary["physical_claim_made"] else "no", "yes" if summary["additional_gate_created"] else "no",
        summary["final_status"], summary["limitations"],
    ]
    write_csv(out_dir / "qsb_causality03_final_status.csv", final_status_header, [final_status_row])
    write_json(out_dir / "qsb_causality03_summary.json", summary)
    readout = build_readout()
    (out_dir / "qsb_causality03_readout.md").write_text("\n".join(readout) + "\n", encoding="utf-8")

    if not summary["all_checks_passed"]:
        print("Derived checks did not all pass.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
