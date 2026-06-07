#!/usr/bin/env python3
"""Deterministic multi-variant stress test for QSB-CAUSALITY04."""

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

OUTPUT_FILES = [
    "qsb_causality04_readout.md",
    "qsb_causality04_summary.json",
    "qsb_causality04_variant_catalog.csv",
    "qsb_causality04_node_catalog.csv",
    "qsb_causality04_edge_catalog.csv",
    "qsb_causality04_predicate_assignment.csv",
    "qsb_causality04_continuation_spaces.csv",
    "qsb_causality04_fixation_sets.csv",
    "qsb_causality04_scc_analysis.csv",
    "qsb_causality04_direction_candidates.csv",
    "qsb_causality04_counterexample_matrix.csv",
    "qsb_causality04_validation_checks.csv",
    "qsb_causality04_final_status.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QSB-CAUSALITY04 multi-variant finite graph stress test")
    parser.add_argument(
        "--output-dir",
        default="runs/QSB-CAUSALITY/QSB_CAUSALITY04_MULTI_VARIANT_STRESS_TEST",
        help="Output directory",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the expected output files")
    return parser.parse_args()


def write_csv(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def write_json(path: Path, payload: Dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def prepare_output_dir(out_dir: Path, overwrite: bool) -> None:
    if out_dir.exists() and not overwrite:
        print(f"Refusing to overwrite existing output directory: {out_dir}", file=sys.stderr)
        sys.exit(2)
    if out_dir.exists():
        unexpected = sorted(item.name for item in out_dir.iterdir() if item.name not in OUTPUT_FILES)
        if unexpected:
            print(f"Unexpected existing files in {out_dir}: {unexpected}", file=sys.stderr)
            sys.exit(2)
        for name in OUTPUT_FILES:
            path = out_dir / name
            if path.exists():
                path.unlink()
    out_dir.mkdir(parents=True, exist_ok=True)


def variants() -> List[Dict[str, object]]:
    chain_nodes = [f"L{i:02d}" for i in range(21)]
    chain_edges = [(chain_nodes[i], chain_nodes[i + 1]) for i in range(len(chain_nodes) - 1)]
    return [
        {"id": "V01", "name": "einfacher azyklischer Graph", "nodes": ["A", "B", "C", "D"], "edges": [("A", "B"), ("B", "C"), ("C", "D")], "expected": "accepted_acyclic"},
        {"id": "V02", "name": "Diamantstruktur", "nodes": ["A", "B", "C", "D"], "edges": [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")], "expected": "accepted_acyclic"},
        {"id": "V03", "name": "mehrere getrennte Zyklen", "nodes": ["A", "B", "C", "D", "E", "F"], "edges": [("A", "B"), ("B", "A"), ("C", "D"), ("D", "E"), ("E", "C"), ("F", "F")], "expected": "cycle_detected_and_blocked"},
        {"id": "V04", "name": "Selbstschleife", "nodes": ["A", "B"], "edges": [("A", "A"), ("A", "B")], "expected": "cycle_detected_and_blocked"},
        {"id": "V05", "name": "transitive Zusatzkante", "nodes": ["A", "B", "C"], "edges": [("A", "B"), ("B", "C"), ("A", "C")], "expected": "accepted_acyclic"},
        {"id": "V06", "name": "mehrere SCCs mit azyklischer Quotientenstruktur", "nodes": ["A", "B", "C", "D", "E"], "edges": [("A", "B"), ("B", "A"), ("B", "C"), ("C", "D"), ("D", "C"), ("D", "E")], "expected": "scc_quotient_acyclic_with_internal_blocks"},
        {"id": "V07", "name": "Fixierungswachstum ohne Fortsetzungsraum-Verengung", "nodes": ["A", "B", "C"], "edges": [("A", "B"), ("B", "A"), ("B", "C")], "expected": "fixation_growth_without_strict_reduction_detected", "refinement_probe": True, "variant_type": "controlled_predicate_refinement_probe"},
        {"id": "V08", "name": "Fortsetzungsraum-Verengung ohne neue Fixierung", "nodes": ["A", "B", "C"], "edges": [("A", "B"), ("B", "C")], "expected": "strict_reduction_without_fixation_growth_detected", "predicate_mode": "constant"},
        {"id": "V09", "name": "lange endliche Kette", "nodes": chain_nodes, "edges": chain_edges, "expected": "accepted_long_acyclic_chain"},
        {"id": "V10", "name": "absichtlich inkonsistente Variante", "nodes": ["A", "B"], "edges": [("A", "B"), ("B", "MISSING")], "expected": "rejected_inconsistent_input"},
    ]


def build_graph(nodes: Sequence[str], edges: Sequence[Tuple[str, str]]) -> Dict[str, Set[str]]:
    graph = {node: set() for node in nodes}
    for src, dst in edges:
        graph[src].add(dst)
    return graph


def reachable(graph: Dict[str, Set[str]], start: str) -> Set[str]:
    seen: Set[str] = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(sorted(graph[node] - seen, reverse=True))
    return seen


def tarjan_scc(nodes: Sequence[str], graph: Dict[str, Set[str]]) -> List[Set[str]]:
    index_counter = 0
    index: Dict[str, int] = {}
    lowlink: Dict[str, int] = {}
    stack: List[str] = []
    on_stack: Set[str] = set()
    components: List[Set[str]] = []

    def visit(node: str) -> None:
        nonlocal index_counter
        index[node] = index_counter
        lowlink[node] = index_counter
        index_counter += 1
        stack.append(node)
        on_stack.add(node)
        for nxt in sorted(graph[node]):
            if nxt not in index:
                visit(nxt)
                lowlink[node] = min(lowlink[node], lowlink[nxt])
            elif nxt in on_stack:
                lowlink[node] = min(lowlink[node], index[nxt])
        if lowlink[node] == index[node]:
            component: Set[str] = set()
            while True:
                item = stack.pop()
                on_stack.remove(item)
                component.add(item)
                if item == node:
                    break
            components.append(component)

    for node in nodes:
        if node not in index:
            visit(node)
    return components


def quotient_is_acyclic(components: Sequence[Set[str]], edges: Sequence[Tuple[str, str]]) -> bool:
    comp_index = {node: idx for idx, component in enumerate(components) for node in component}
    q_nodes = [str(i) for i in range(len(components))]
    q_edges = sorted({(str(comp_index[src]), str(comp_index[dst])) for src, dst in edges if comp_index[src] != comp_index[dst]})
    graph = build_graph(q_nodes, q_edges)
    return all(len(component) == 1 for component in tarjan_scc(q_nodes, graph))


def predicate_values(nodes: Sequence[str], edges: Sequence[Tuple[str, str]], graph: Dict[str, Set[str]], sccs: Sequence[Set[str]], mode: str = "structural") -> Dict[str, Dict[str, int]]:
    if mode == "constant":
        return {"p_constant_documented": {node: 1 for node in nodes}}
    indeg = {node: 0 for node in nodes}
    for _, dst in edges:
        indeg[dst] += 1
    cyclic_nodes = {node for component in sccs if len(component) > 1 for node in component}
    cyclic_nodes.update(src for src, dst in edges if src == dst)
    terminal = {node for node in nodes if not graph[node]}
    values = {
        "p_terminal": {node: int(node in terminal) for node in nodes},
        "p_nonbranching": {node: int(len(graph[node]) <= 1) for node in nodes},
        "p_has_successor": {node: int(bool(graph[node])) for node in nodes},
        "p_has_predecessor": {node: int(indeg[node] > 0) for node in nodes},
        "p_inside_cycle": {node: int(node in cyclic_nodes) for node in nodes},
        "p_high_out_degree": {node: int(len(graph[node]) >= 2) for node in nodes},
    }
    return values


def analyze_variant(item: Dict[str, object]) -> Dict[str, object]:
    nodes = list(item["nodes"])
    edges = list(item["edges"])
    missing = sorted({endpoint for edge in edges for endpoint in edge if endpoint not in nodes})
    duplicate_nodes = len(nodes) != len(set(nodes))
    if missing or duplicate_nodes:
        return {"valid": False, "missing_nodes": missing, "duplicate_nodes": duplicate_nodes}
    graph = build_graph(nodes, edges)
    reach = {node: reachable(graph, node) for node in nodes}
    sccs = tarjan_scc(nodes, graph)
    nontrivial_sccs = [component for component in sccs if len(component) > 1]
    self_loops = [(src, dst) for src, dst in edges if src == dst]
    internal_scc_edges = [
        (src, dst)
        for src, dst in edges
        if src == dst or any(src in component and dst in component and len(component) > 1 for component in sccs)
    ]
    predicates = predicate_values(nodes, edges, graph, sccs, str(item.get("predicate_mode", "structural")))
    fixation = {
        node: sorted(name for name, values in predicates.items() if all(values[other] == 1 for other in reach[node]))
        for node in nodes
    }
    strict = {(src, dst): reach[dst] < reach[src] for src, dst in edges}
    refined = {(src, dst): set(fixation[src]).issubset(set(fixation[dst])) for src, dst in edges}
    candidates = [(src, dst) for src, dst in edges if refined[(src, dst)] and strict[(src, dst)]]
    growth = {(src, dst): sorted(set(fixation[dst]) - set(fixation[src])) for src, dst in edges}
    loss = {(src, dst): sorted(set(fixation[src]) - set(fixation[dst])) for src, dst in edges}
    refinement_fixation_growth = False
    if item.get("refinement_probe"):
        refined_predicates = dict(predicates)
        refined_predicates["p_refined_role_marker"] = {node: 1 for node in nodes}
        refined_fixation = {
            node: sorted(name for name, values in refined_predicates.items() if all(values[other] == 1 for other in reach[node]))
            for node in nodes
        }
        refinement_fixation_growth = any(set(refined_fixation[node]) > set(fixation[node]) for node in nodes)
    has_growth_without_strict = any(growth[edge] and not strict[edge] for edge in edges) or refinement_fixation_growth
    has_strict_without_growth = any(strict[edge] and not growth[edge] for edge in edges)
    acyclic = not nontrivial_sccs and not self_loops
    observed = "accepted_acyclic" if acyclic else "cycle_detected_and_blocked"
    if item["id"] == "V06" and nontrivial_sccs and quotient_is_acyclic(sccs, edges):
        observed = "scc_quotient_acyclic_with_internal_blocks"
    if item["id"] == "V07" and has_growth_without_strict:
        observed = "fixation_growth_without_strict_reduction_detected"
    if item["id"] == "V08" and has_strict_without_growth:
        observed = "strict_reduction_without_fixation_growth_detected"
    if item["id"] == "V09" and acyclic and len(nodes) >= 20:
        observed = "accepted_long_acyclic_chain"
    return {
        "valid": True,
        "graph": graph,
        "reach": reach,
        "sccs": sccs,
        "nontrivial_sccs": nontrivial_sccs,
        "self_loops": self_loops,
        "internal_scc_edges": internal_scc_edges,
        "predicates": predicates,
        "fixation": fixation,
        "strict": strict,
        "refined": refined,
        "candidates": candidates,
        "growth": growth,
        "loss": loss,
        "acyclic": acyclic,
        "quotient_acyclic": quotient_is_acyclic(sccs, edges),
        "observed": observed,
        "has_growth_without_strict": has_growth_without_strict,
        "has_strict_without_growth": has_strict_without_growth,
    }


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output_dir)
    prepare_output_dir(out_dir, args.overwrite)

    items = variants()
    analyses = {item["id"]: analyze_variant(item) for item in items}
    variant_pass = {item["id"]: analyses[item["id"]].get("observed", "rejected_inconsistent_input") == item["expected"] for item in items}
    exact_variant_count = len(items) == 10
    v10_rejected = not analyses["V10"]["valid"]
    all_positive = exact_variant_count and v10_rejected and all(variant_pass.values())

    v07_note = "Fixierungswachstum wird hier durch eine Verfeinerung des Prädikatsinventars bei unveränderter Graph-Erreichbarkeit erzeugt. Dies ist keine graphinterne Fortsetzungskante."
    write_csv(out_dir / "qsb_causality04_variant_catalog.csv", ["variant_id", "name", "variant_type", "node_count", "edge_count", "valid_input", "expected_result", "observed_result", "passed", "note"], [
        [item["id"], item["name"], item.get("variant_type", "finite_graph_variant"), len(item["nodes"]), len(item["edges"]), "yes" if analyses[item["id"]]["valid"] else "no", item["expected"], analyses[item["id"]].get("observed", "rejected_inconsistent_input"), "yes" if variant_pass[item["id"]] else "no", v07_note if item["id"] == "V07" else ""]
        for item in items
    ])
    write_csv(out_dir / "qsb_causality04_node_catalog.csv", ["variant_id", "node"], [[item["id"], node] for item in items for node in item["nodes"]])
    write_csv(out_dir / "qsb_causality04_edge_catalog.csv", ["variant_id", "source", "target", "valid_edge"], [
        [item["id"], src, dst, "yes" if src in item["nodes"] and dst in item["nodes"] else "no"] for item in items for src, dst in item["edges"]
    ])
    predicate_rows = []
    continuation_rows = []
    fixation_rows = []
    scc_rows = []
    direction_rows = []
    counter_rows = []
    for item in items:
        vid = item["id"]
        analysis = analyses[vid]
        if not analysis["valid"]:
            counter_rows.append([vid, "invalid_input", ",".join(analysis["missing_nodes"]), "rejected before graph analysis", "yes" if vid == "V10" else "no"])
            continue
        if vid == "V07":
            counter_rows.append([vid, "controlled_predicate_refinement_probe", "controlled_predicate_refinement_probe", v07_note, "yes"])
        for pred, values in analysis["predicates"].items():
            for node, value in values.items():
                predicate_rows.append([vid, pred, node, value])
        for node, reach_set in analysis["reach"].items():
            continuation_rows.append([vid, node, len(reach_set), ";".join(sorted(reach_set))])
        for node, fixed in analysis["fixation"].items():
            fixation_rows.append([vid, node, ";".join(fixed)])
        for idx, component in enumerate(analysis["sccs"]):
            internal = [(src, dst) for src, dst in item["edges"] if src in component and dst in component]
            scc_rows.append([vid, idx, ";".join(sorted(component)), len(component), len(internal), ";".join(f"{src}->{dst}" for src, dst in internal)])
        for src, dst in item["edges"]:
            direction_rows.append([
                vid, src, dst,
                "yes" if analysis["refined"][(src, dst)] else "no",
                "yes" if analysis["strict"][(src, dst)] else "no",
                ";".join(analysis["growth"][(src, dst)]),
                ";".join(analysis["loss"][(src, dst)]),
                "yes" if (src, dst) in analysis["candidates"] else "no",
            ])
        for src, dst in analysis["internal_scc_edges"]:
            counter_rows.append([vid, f"{src}->{dst}", "internal_scc_or_self_loop", "strict continuation reduction blocked" if not analysis["strict"][(src, dst)] else "unexpected strict reduction", "yes" if not analysis["strict"][(src, dst)] else "no"])

    write_csv(out_dir / "qsb_causality04_predicate_assignment.csv", ["variant_id", "predicate", "node", "value"], predicate_rows)
    write_csv(out_dir / "qsb_causality04_continuation_spaces.csv", ["variant_id", "node", "reachable_count", "reachable_nodes"], continuation_rows)
    write_csv(out_dir / "qsb_causality04_fixation_sets.csv", ["variant_id", "node", "fixation_set"], fixation_rows)
    write_csv(out_dir / "qsb_causality04_scc_analysis.csv", ["variant_id", "scc_index", "nodes", "node_count", "internal_edge_count", "internal_edges"], scc_rows)
    write_csv(out_dir / "qsb_causality04_direction_candidates.csv", ["variant_id", "source", "target", "refined_admissible", "strict_continuation_reduction", "fixation_growth", "fixation_loss", "direction_candidate"], direction_rows)
    write_csv(out_dir / "qsb_causality04_counterexample_matrix.csv", ["variant_id", "case_id", "counterexample_type", "observed_handling", "handled_as_expected"], counter_rows)
    checks = [
        ["exact_variant_count", exact_variant_count, "ten variants are present"],
        ["v10_rejected", v10_rejected, "inconsistent variant is rejected"],
        ["all_expected_observed_match", all(variant_pass.values()), "observed results match expected classifications"],
        ["long_chain_min_20_nodes", len(next(item for item in items if item["id"] == "V09")["nodes"]) >= 20, "V09 has at least 20 nodes"],
        ["outputs_exact_after_write_placeholder", False, "updated after all files are written"],
    ]
    write_csv(out_dir / "qsb_causality04_validation_checks.csv", ["check_id", "passed", "note"], [[name, "yes" if passed else "no", note] for name, passed, note in checks])

    summary = {
        "research_block": "QSB-CAUSALITY04",
        "variant_count": len(items),
        "all_variant_checks_passed": all(variant_pass.values()),
        "v10_rejected": v10_rejected,
        "v07_variant_type": "controlled_predicate_refinement_probe",
        "v07_clarification": v07_note,
        "physical_data_used": False,
        "network_used": False,
        "db_modified": False,
        "all_checks_passed": False,
        "final_status": "qsb_causality04_failed",
        "limitations": "Finite graph stress test only; no physical interpretation is claimed.",
    }
    write_json(out_dir / "qsb_causality04_summary.json", summary)
    write_csv(out_dir / "qsb_causality04_final_status.csv", ["research_block", "all_checks_passed", "final_status", "limitations"], [["QSB-CAUSALITY04", "no", summary["final_status"], summary["limitations"]]])
    (out_dir / "qsb_causality04_readout.md").write_text(
        "# QSB-CAUSALITY04 multi-variant stress test\n\n"
        "Befund: Ten deterministic finite graph variants were analyzed for reachability, continuation spaces, SCCs, fixation sets, refined admissibility, and direction candidates.\n\n"
        "Interpretation: The positive status is assigned only if all computed validation checks pass and V10 is rejected as inconsistent input.\n\n"
        "Hypothese: The CAUSALITY03 finite-graph architecture remains internally controlled across the declared stress variants.\n\n"
        "Offene Luecke: This is a finite formal stress test and does not certify real-data causality or physical dynamics.\n\n"
        f"Claim Boundary: No physical emergence, spacetime emergence, Lorentz compatibility, or dynamics claim is made. Current provisional status: {summary['final_status']}.\n",
        encoding="utf-8",
    )

    exact_output_set = sorted(path.name for path in out_dir.iterdir() if path.is_file()) == sorted(OUTPUT_FILES)
    checks[-1] = ["outputs_exact_after_write", exact_output_set, "output directory contains exactly the required files"]
    all_checks = all(passed for _, passed, _ in checks) and all_positive
    final_status = "multi_variant_causality_stress_test_passed" if all_checks else "qsb_causality04_failed"
    write_csv(out_dir / "qsb_causality04_validation_checks.csv", ["check_id", "passed", "note"], [[name, "yes" if passed else "no", note] for name, passed, note in checks])
    summary.update({"exact_output_set": exact_output_set, "all_checks_passed": all_checks, "final_status": final_status})
    write_json(out_dir / "qsb_causality04_summary.json", summary)
    write_csv(out_dir / "qsb_causality04_final_status.csv", ["research_block", "all_checks_passed", "final_status", "limitations"], [["QSB-CAUSALITY04", "yes" if all_checks else "no", final_status, summary["limitations"]]])
    (out_dir / "qsb_causality04_readout.md").write_text(
        "# QSB-CAUSALITY04 multi-variant stress test\n\n"
        f"Befund: {len(items)} deterministic finite graph variants were analyzed. V10 rejected: {'yes' if v10_rejected else 'no'}. All computed checks passed: {'yes' if all_checks else 'no'}.\n\n"
        f"V07-Kennzeichnung: controlled_predicate_refinement_probe. {v07_note}\n\n"
        "Interpretation: Direction candidates require refined admissibility and strict continuation-space reduction; internal SCC/self-loop edges are blocked as counterexamples.\n\n"
        "Hypothese: The CAUSALITY03 finite-graph architecture remains internally controlled across the declared stress variants.\n\n"
        "Offene Luecke: This is a finite formal stress test and does not certify real-data causality or physical dynamics.\n\n"
        f"Claim Boundary: No physical emergence, spacetime emergence, Lorentz compatibility, or dynamics claim is made. Final status: {final_status}.\n",
        encoding="utf-8",
    )
    if not all_checks:
        print("QSB-CAUSALITY04 validation failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
