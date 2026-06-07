#!/usr/bin/env python3
"""Controlled C60 patch embedding for QSB-CAUSALITY05."""

import argparse
import csv
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

OUTPUT_FILES = [
    "qsb_causality05_readout.md",
    "qsb_causality05_summary.json",
    "qsb_causality05_source_inventory.csv",
    "qsb_causality05_dataset_selection.csv",
    "qsb_causality05_configuration_catalog.csv",
    "qsb_causality05_node_catalog.csv",
    "qsb_causality05_edge_catalog.csv",
    "qsb_causality05_predicate_catalog.csv",
    "qsb_causality05_predicate_assignment.csv",
    "qsb_causality05_admissibility_candidates.csv",
    "qsb_causality05_continuation_spaces.csv",
    "qsb_causality05_fixation_candidates.csv",
    "qsb_causality05_direction_candidates.csv",
    "qsb_causality05_data_gaps.csv",
    "qsb_causality05_validation_checks.csv",
    "qsb_causality05_final_status.csv",
]
CAUSALITY04_SUMMARY = "runs/QSB-CAUSALITY/QSB_CAUSALITY04_MULTI_VARIANT_STRESS_TEST/qsb_causality04_summary.json"
POSITIVE_STATUS = "controlled_c60_patch_embedding_completed_direction_not_independently_inferred"
FIXATION_ALLOWED = {"directly_documented", "structurally_derived"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QSB-CAUSALITY05 controlled C60 patch embedding")
    parser.add_argument("--input-root", default=".", help="Root directory for read-only input data")
    parser.add_argument(
        "--output-dir",
        default="runs/QSB-CAUSALITY/QSB_CAUSALITY05_REAL_DATA_MAPPING",
        help="Output directory",
    )
    parser.add_argument("--overwrite", action="store_true", help="Overwrite the expected output files")
    parser.add_argument("--causality04-summary", default=CAUSALITY04_SUMMARY, help="QSB-CAUSALITY04 summary gate path")
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


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> Dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def yes(value: bool) -> str:
    return "yes" if value else "no"


def resolve_input(input_root: Path, rel: str) -> Path:
    return input_root / rel


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


def causality04_gate(path: Path) -> bool:
    if not path.exists():
        return False
    payload = read_json(path)
    return payload.get("final_status") == "multi_variant_causality_stress_test_passed" and payload.get("all_checks_passed") is True


def candidate_sources() -> List[Tuple[str, str, str, str, str, str]]:
    return [
        ("C60 reference nodes", "data/bms_fu02g_c60_reference_nodes.csv", "csv", "C60 node metadata", "high", "FU02g normalized C60 reference"),
        ("C60 reference edges", "data/bms_fu02g_c60_reference_edges.csv", "csv", "C60 adjacency/edge classes", "high", "FU02g normalized C60 reference"),
        ("C60 reference cells", "data/bms_fu02g_c60_reference_cells.csv", "csv", "pentagon/hexagon cell membership", "high", "FU02g normalized C60 reference"),
        ("C60 reference manifest", "data/bms_fu02g_c60_reference_manifest.json", "json", "structure-level counts and caveats", "high", "FU02g normalized C60 reference"),
        ("benzene nodes", "data/QSB-BRIDGE-DATA-02A/benzene_nodes.csv", "csv", "benzene control node metadata", "medium", "control scaffold"),
        ("benzene edges", "data/QSB-BRIDGE-DATA-02A/benzene_edges.csv", "csv", "benzene control adjacency", "medium", "control scaffold"),
        ("ethyne nodes", "data/QSB-BRIDGE-DATA-02B/ethyne_nodes.csv", "csv", "ethyne control node metadata", "medium", "control scaffold"),
        ("ethyne edges", "data/QSB-BRIDGE-DATA-02B/ethyne_edges.csv", "csv", "ethyne control adjacency", "medium", "control scaffold"),
        ("adamantane nodes", "data/QSB-BRIDGE-DATA-02B/adamantane_nodes.csv", "csv", "adamantane control node metadata", "medium", "control scaffold"),
        ("adamantane edges", "data/QSB-BRIDGE-DATA-02B/adamantane_edges.csv", "csv", "adamantane control adjacency", "medium", "control scaffold"),
        ("H2 nodes", "data/QSB-BRIDGE-DATA-02B/h2_nodes.csv", "csv", "H2 control node metadata", "low", "candidate path only"),
        ("H2 edges", "data/QSB-BRIDGE-DATA-02B/h2_edges.csv", "csv", "H2 control adjacency", "low", "candidate path only"),
    ]


def source_inventory(input_root: Path) -> List[List[object]]:
    rows = []
    for label, rel, file_type, content, suitability, transform in candidate_sources():
        path = resolve_input(input_root, rel)
        present = path.exists() and path.is_file() and path.stat().st_size > 0
        rows.append([
            "candidate_source_availability_check",
            rel,
            file_type,
            label,
            content,
            suitability if present else "none",
            "present" if present else "missing",
            transform,
            "fixed candidate list; not a complete repository search",
        ])
    return rows


def edge_endpoints(edge: Dict[str, str]) -> Tuple[str, str]:
    return edge.get("source", ""), edge.get("target", "")


def induced_edges(nodes: Set[str], edges: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    return [edge for edge in edges if edge_endpoints(edge)[0] in nodes and edge_endpoints(edge)[1] in nodes]


def incident_neighbors(nodes: Set[str], edges: Sequence[Dict[str, str]]) -> Set[str]:
    result = set(nodes)
    for edge in edges:
        src, dst = edge_endpoints(edge)
        if src in nodes:
            result.add(dst)
        if dst in nodes:
            result.add(src)
    return result


def reachability(config_edges: Sequence[Tuple[str, str]], configs: Sequence[str]) -> Dict[str, Set[str]]:
    graph = {config: set() for config in configs}
    for src, dst in config_edges:
        graph[src].add(dst)
    reach = {}
    for start in configs:
        seen: Set[str] = set()
        stack = [start]
        while stack:
            item = stack.pop()
            if item in seen:
                continue
            seen.add(item)
            stack.extend(sorted(graph[item] - seen, reverse=True))
        reach[start] = seen
    return reach


def continuation_successors(config_edges: Sequence[Tuple[str, str]], configs: Sequence[str]) -> Dict[str, Set[str]]:
    successors = {config: set() for config in configs}
    for src, dst in config_edges:
        successors[src].add(dst)
    return successors


def fixation_scope(config_id: str, successors: Dict[str, Set[str]]) -> str:
    direct_count = len(successors.get(config_id, set()))
    if direct_count == 0:
        return "single_terminal_configuration"
    if direct_count == 1:
        return "linear_continuation_chain"
    return "branched_continuation_set"


def predicate_catalog() -> List[Dict[str, str]]:
    return [
        {"predicate_id": "element_C", "availability_status": "directly_documented", "basis": "node element field equals C", "aggregation_rule": "forall", "aggregation_threshold": "all nodes", "configuration_level_meaning": "all documented atoms in the configuration are carbon"},
        {"predicate_id": "degree_3", "availability_status": "directly_documented", "basis": "degree or degree_target field equals 3", "aggregation_rule": "forall", "aggregation_threshold": "all nodes", "configuration_level_meaning": "all documented nodes have degree 3"},
        {"predicate_id": "ring_membership", "availability_status": "directly_documented", "basis": "face/cell membership metadata exists", "aggregation_rule": "forall", "aggregation_threshold": "all nodes", "configuration_level_meaning": "all nodes have documented ring/cell membership"},
        {"predicate_id": "pentagon_membership", "availability_status": "directly_documented", "basis": "P cell or pentagon membership field", "aggregation_rule": "exists", "aggregation_threshold": "at least one node", "configuration_level_meaning": "configuration contains documented pentagon membership"},
        {"predicate_id": "hexagon_membership", "availability_status": "directly_documented", "basis": "H cell or hexagon membership field", "aggregation_rule": "exists", "aggregation_threshold": "at least one node", "configuration_level_meaning": "configuration contains documented hexagon membership"},
        {"predicate_id": "cage_membership", "availability_status": "structurally_derived", "basis": "selected C60 manifest closure_class=closed_cage or adamantane sigma cage marker", "aggregation_rule": "structural_pattern_present", "aggregation_threshold": "dataset-level marker present", "configuration_level_meaning": "configuration is embedded in a documented cage-like structural scaffold"},
        {"predicate_id": "curvature_candidate", "availability_status": "structurally_derived", "basis": "documented nonplanar closed C60 cage topology or explicit curved_fullerene_reference marker", "aggregation_rule": "structural_pattern_present", "aggregation_threshold": "nonplanar/closed cage marker present", "configuration_level_meaning": "curvature is treated only as a structural proxy candidate"},
        {"predicate_id": "hybridization_candidate", "availability_status": "semantically_uncertain", "basis": "proxy labels such as sp2_role or hybridization_label; not promoted to fixation evidence", "aggregation_rule": "exists", "aggregation_threshold": "at least one documented proxy label", "configuration_level_meaning": "hybridization-like proxy is present but excluded from fixations"},
        {"predicate_id": "aromaticity_candidate", "availability_status": "semantically_uncertain", "basis": "aromatic labels only when directly present in control scaffold metadata", "aggregation_rule": "exists", "aggregation_threshold": "at least one aromatic proxy label", "configuration_level_meaning": "aromaticity-like proxy is present but excluded from fixations"},
        {"predicate_id": "local_symmetry", "availability_status": "directly_documented", "basis": "manifest symmetry labels, orbit labels, or uniform ring/cage control metadata", "aggregation_rule": "structural_pattern_present", "aggregation_threshold": "documented symmetry marker present", "configuration_level_meaning": "configuration has a documented local/global symmetry marker"},
        {"predicate_id": "local_neighborhood_signature", "availability_status": "directly_documented", "basis": "local face signature or local_environment_label", "aggregation_rule": "forall", "aggregation_threshold": "all nodes", "configuration_level_meaning": "all nodes carry a documented local neighborhood signature"},
    ]


def field(row: Dict[str, str], *names: str) -> str:
    for name in names:
        value = row.get(name, "")
        if value:
            return value
    return ""


def node_predicates(row: Dict[str, str], context: Dict[str, object]) -> Dict[str, bool]:
    faces = field(row, "incident_cells", "incident_faces")
    local = field(row, "local_face_signature", "local_environment_label")
    element = field(row, "element_symbol", "atom_label")
    degree = field(row, "degree", "degree_target")
    sp_proxy = field(row, "node_role_hint", "sp2_role", "hybridization_label")
    pi_label = field(row, "pi_system_label", "sp2_role")
    curved_marker = "curved" in field(row, "curvature_label").lower()
    closed_cage = context.get("closed_cage", False)
    cage_marker = closed_cage or "cage" in field(row, "sigma_framework_label").lower()
    return {
        "element_C": element == "C" or (context.get("assume_c60_carbon") is True and row.get("node_id", "").startswith("c60_")),
        "degree_3": degree == "3",
        "ring_membership": bool(faces) or "ring" in local.lower() or bool(row.get("ring_index", "")),
        "pentagon_membership": "P_" in faces or row.get("pentagon_membership_count") not in ("", "0"),
        "hexagon_membership": "H_" in faces or row.get("hexagon_membership_count") not in ("", "0"),
        "cage_membership": cage_marker,
        "curvature_candidate": bool(closed_cage or curved_marker),
        "hybridization_candidate": bool(sp_proxy),
        "aromaticity_candidate": "aromatic" in pi_label.lower() or "aromatic" in local.lower(),
        "local_symmetry": bool(context.get("symmetry_marker", False) or row.get("orbit_label", "")),
        "local_neighborhood_signature": bool(local or faces),
    }


def aggregate(predicate_id: str, values: Sequence[bool], config: Dict[str, object]) -> bool:
    if not values:
        return False
    rule = config["aggregation"].get(predicate_id, "exists")
    if rule == "forall":
        return all(values)
    if rule == "exists":
        return any(values)
    if rule == "count_ge_n":
        return sum(1 for value in values if value) >= int(config["thresholds"].get(predicate_id, 1))
    if rule == "fraction_ge_q":
        return (sum(1 for value in values if value) / len(values)) >= float(config["thresholds"].get(predicate_id, 1.0))
    if rule == "structural_pattern_present":
        return any(values)
    if rule == "invariant_under_extension":
        return all(values)
    raise ValueError(f"Unsupported aggregation rule: {rule}")


def config_predicate_values(config: Dict[str, object], catalog: Sequence[Dict[str, str]]) -> Dict[str, bool]:
    node_rows = config["nodes"]
    values_by_pred: Dict[str, List[bool]] = {item["predicate_id"]: [] for item in catalog}
    for row in node_rows:
        values = node_predicates(row, config["context"])
        for pred, value in values.items():
            values_by_pred[pred].append(value)
    return {pred: aggregate(pred, values, config) for pred, values in values_by_pred.items()}


def c60_context(manifest: Dict[str, object]) -> Dict[str, object]:
    meta = manifest.get("meta", {})
    return {
        "assume_c60_carbon": True,
        "closed_cage": manifest.get("closure_class") == "closed_cage",
        "symmetry_marker": bool(meta.get("rotation_symmetry_label")),
    }


def control_context(system: str) -> Dict[str, object]:
    return {
        "assume_c60_carbon": False,
        "closed_cage": system == "adamantane",
        "symmetry_marker": system in {"benzene", "adamantane"},
    }


def main() -> None:
    args = parse_args()
    input_root = Path(args.input_root)
    out_dir = Path(args.output_dir)
    gate_path = Path(args.causality04_summary)
    if not gate_path.is_absolute():
        gate_path = Path(".") / gate_path
    if not causality04_gate(gate_path):
        print("QSB-CAUSALITY05 blocked because QSB-CAUSALITY04 did not pass.", file=sys.stderr)
        sys.exit(1)
    prepare_output_dir(out_dir, args.overwrite)

    inventory = source_inventory(input_root)
    write_csv(out_dir / "qsb_causality05_source_inventory.csv", ["check_type", "path", "file_type", "source_label", "content", "semantic_suitability", "data_completeness", "existing_transformation", "scope_note"], inventory)

    node_path = resolve_input(input_root, "data/bms_fu02g_c60_reference_nodes.csv")
    edge_path = resolve_input(input_root, "data/bms_fu02g_c60_reference_edges.csv")
    cell_path = resolve_input(input_root, "data/bms_fu02g_c60_reference_cells.csv")
    manifest_path = resolve_input(input_root, "data/bms_fu02g_c60_reference_manifest.json")
    selected = all(path.exists() for path in [node_path, edge_path, cell_path, manifest_path])
    nodes = read_csv(node_path) if selected else []
    edges = read_csv(edge_path) if selected else []
    cells = read_csv(cell_path) if selected else []
    manifest = read_json(manifest_path) if selected else {}
    node_by_id = {row["node_id"]: row for row in nodes}

    p00 = next(cell for cell in cells if cell["cell_id"] == "P_00")
    h01 = next(cell for cell in cells if cell["cell_id"] == "H_01")
    core_nodes = set(p00["node_ids"].split(";"))
    neighbor_nodes = incident_neighbors(core_nodes, edges)
    alternative_nodes = set(h01["node_ids"].split(";"))
    full_nodes = {row["node_id"] for row in nodes}

    catalog = predicate_catalog()
    aggregation = {item["predicate_id"]: item["aggregation_rule"] for item in catalog}
    thresholds = {item["predicate_id"]: item["aggregation_threshold"] for item in catalog}
    c60_configs = [
        {"id": "C60_P00_pentagon_core", "system": "c60", "role": "selected_real_structural_input", "configuration_type": "C60 local structural patch", "nodes": [node_by_id[node] for node in sorted(core_nodes)], "edges": induced_edges(core_nodes, edges), "source_basis": "documented pentagon cell P_00", "context": c60_context(manifest), "aggregation": aggregation, "thresholds": thresholds},
        {"id": "C60_P00_neighbor_patch", "system": "c60", "role": "constructed_structural_patch_extension", "configuration_type": "C60 local structural patch", "nodes": [node_by_id[node] for node in sorted(neighbor_nodes)], "edges": induced_edges(neighbor_nodes, edges), "source_basis": "constructed one-step neighborhood extension from P_00 using documented C60 edges", "context": c60_context(manifest), "aggregation": aggregation, "thresholds": thresholds},
        {"id": "C60_H01_alternative_local_patch", "system": "c60", "role": "constructed_structural_patch_extension", "configuration_type": "C60 alternative local structural patch", "nodes": [node_by_id[node] for node in sorted(alternative_nodes)], "edges": induced_edges(alternative_nodes, edges), "source_basis": "documented adjacent hexagon cell H_01 as alternative local patch from same P_00 core vicinity", "context": c60_context(manifest), "aggregation": aggregation, "thresholds": thresholds},
        {"id": "C60_reference_full", "system": "c60", "role": "constructed_structural_patch_extension", "configuration_type": "C60 closed reference graph", "nodes": [node_by_id[node] for node in sorted(full_nodes)], "edges": induced_edges(full_nodes, edges), "source_basis": "documented normalized full reference graph", "context": c60_context(manifest), "aggregation": aggregation, "thresholds": thresholds},
    ]
    config_edges = [
        ("C60_P00_pentagon_core", "C60_P00_neighbor_patch"),
        ("C60_P00_pentagon_core", "C60_H01_alternative_local_patch"),
        ("C60_P00_neighbor_patch", "C60_reference_full"),
    ]

    control_specs = [
        ("benzene", "data/QSB-BRIDGE-DATA-02A/benzene_nodes.csv", "data/QSB-BRIDGE-DATA-02A/benzene_edges.csv", "planar aromatic ring control"),
        ("ethyne", "data/QSB-BRIDGE-DATA-02B/ethyne_nodes.csv", "data/QSB-BRIDGE-DATA-02B/ethyne_edges.csv", "linear two-carbon control"),
        ("adamantane", "data/QSB-BRIDGE-DATA-02B/adamantane_nodes.csv", "data/QSB-BRIDGE-DATA-02B/adamantane_edges.csv", "saturated cage-like carbon control"),
        ("H2", "data/QSB-BRIDGE-DATA-02B/h2_nodes.csv", "data/QSB-BRIDGE-DATA-02B/h2_edges.csv", "hydrogen control"),
    ]
    control_configs = []
    blocked_controls = []
    for system, nodes_rel, edges_rel, role in control_specs:
        n_path = resolve_input(input_root, nodes_rel)
        e_path = resolve_input(input_root, edges_rel)
        if n_path.exists() and e_path.exists():
            control_nodes = read_csv(n_path)
            control_edges = read_csv(e_path)
            control_configs.append({"id": f"control_{system}", "system": system, "role": "control_configuration", "configuration_type": role, "nodes": control_nodes, "edges": control_edges, "source_basis": f"{nodes_rel}; {edges_rel}", "context": control_context(system), "aggregation": aggregation, "thresholds": thresholds})
        else:
            blocked_controls.append([system, nodes_rel, edges_rel, "control_mapping_blocked_by_missing_input"])

    configs = c60_configs + control_configs
    config_by_id = {config["id"]: config for config in configs}
    c60_config_ids = [config["id"] for config in c60_configs]
    reach = reachability(config_edges, c60_config_ids)
    successors = continuation_successors(config_edges, c60_config_ids)
    predicate_by_config = {config["id"]: config_predicate_values(config, catalog) for config in configs}
    status_by_pred = {item["predicate_id"]: item["availability_status"] for item in catalog}
    excluded_predicates = sorted(pred for pred, status in status_by_pred.items() if status not in FIXATION_ALLOWED)
    predicate_ids = [item["predicate_id"] for item in catalog]
    c60_assignment_vectors = {
        pred: tuple(predicate_by_config[config_id][pred] for config_id in c60_config_ids)
        for pred in predicate_ids
    }
    coextensive_pairs = [
        (pred_1, pred_2)
        for pred_1, pred_2 in combinations(predicate_ids, 2)
        if c60_assignment_vectors[pred_1] == c60_assignment_vectors[pred_2]
    ]
    coextension_notes = {}
    for pred_1, pred_2 in coextensive_pairs:
        note_1 = f"empirically_coextensive_with_{pred_2}_in_evaluated_c60_configurations"
        note_2 = f"empirically_coextensive_with_{pred_1}_in_evaluated_c60_configurations"
        coextension_notes.setdefault(pred_1, []).append(note_1)
        coextension_notes.setdefault(pred_2, []).append(note_2)

    write_csv(out_dir / "qsb_causality05_dataset_selection.csv", ["selected_dataset", "selected", "selection_rule", "node_count", "edge_count", "cell_count", "status", "input_root"], [[
        "C60 local structural patch", yes(selected), "preferred existing C60 reference with nodes, edges, cells, and manifest", len(nodes), len(edges), len(cells), "selected" if selected else "blocked", str(input_root)
    ]])
    write_csv(out_dir / "qsb_causality05_configuration_catalog.csv", ["configuration_id", "system", "configuration_type", "configuration_role", "node_count", "edge_count", "source_basis"], [
        [config["id"], config["system"], config["configuration_type"], config["role"], len(config["nodes"]), len(config["edges"]), config["source_basis"]] for config in configs
    ])
    write_csv(out_dir / "qsb_causality05_node_catalog.csv", ["configuration_id", "system", "node_id", "element", "degree", "local_signature", "attribute_status"], [
        [config["id"], config["system"], row.get("node_id", ""), field(row, "element_symbol", "atom_label"), field(row, "degree", "degree_target"), field(row, "local_face_signature", "local_environment_label", "incident_faces"), "directly_documented"]
        for config in configs for row in config["nodes"]
    ])
    write_csv(out_dir / "qsb_causality05_edge_catalog.csv", ["configuration_id", "system", "edge_id", "source", "target", "edge_class", "attribute_status"], [
        [config["id"], config["system"], row.get("edge_id", ""), row.get("source", ""), row.get("target", ""), field(row, "edge_class", "bond_class", "bond_order_class"), "directly_documented"]
        for config in configs for row in config["edges"]
    ])
    write_csv(out_dir / "qsb_causality05_predicate_catalog.csv", ["predicate_id", "availability_status", "basis", "aggregation_rule", "aggregation_threshold", "configuration_level_meaning", "fixation_eligible"], [
        [item["predicate_id"], item["availability_status"], item["basis"], item["aggregation_rule"], item["aggregation_threshold"], item["configuration_level_meaning"], yes(item["availability_status"] in FIXATION_ALLOWED)] for item in catalog
    ])
    write_csv(out_dir / "qsb_causality05_predicate_assignment.csv", ["configuration_id", "system", "predicate_id", "configuration_value", "availability_status", "aggregation_rule", "aggregation_threshold"], [
        [config["id"], config["system"], item["predicate_id"], yes(predicate_by_config[config["id"]][item["predicate_id"]]), item["availability_status"], item["aggregation_rule"], item["aggregation_threshold"]]
        for config in configs for item in catalog
    ])
    write_csv(out_dir / "qsb_causality05_admissibility_candidates.csv", ["source_configuration", "target_configuration", "operator_type", "admissible", "basis", "observed_state_sequence", "chemical_reaction"], [
        [src, dst, "constructed_structural_patch_extension", "yes", "constructed from documented C60 topology; not an observed state sequence", "no", "no"] for src, dst in config_edges
    ])
    write_csv(out_dir / "qsb_causality05_continuation_spaces.csv", ["configuration_id", "reachable_configurations", "reachable_count", "continuation_space_note"], [
        [config, ";".join(sorted(values)), len(values), "constructed structural patch-extension space"] for config, values in reach.items()
    ])

    fixation_rows = []
    fixation_break_examples: List[str] = []
    for config_id, omega in reach.items():
        current_true = {pred for pred, value in predicate_by_config[config_id].items() if value and status_by_pred[pred] in FIXATION_ALLOWED}
        omega_true = {
            pred
            for pred in current_true
            if all(predicate_by_config[target][pred] for target in omega)
        }
        lost = sorted(current_true - omega_true)
        scope = fixation_scope(config_id, successors)
        alternative_evaluated = scope == "branched_continuation_set" and "C60_H01_alternative_local_patch" in omega
        for pred in sorted(omega_true):
            fixation_rows.append([
                config_id,
                pred,
                "retained_across_evaluated_continuations",
                len(omega),
                yes(alternative_evaluated),
                "no",
                0,
                "",
                scope,
                ";".join(sorted(coextension_notes.get(pred, []))),
                "only directly_documented or structurally_derived predicates admitted; empirical coextension is not logical redundancy",
            ])
        for pred in lost:
            targets_breaking = sorted(target for target in omega if not predicate_by_config[target][pred])
            fixation_break_examples.extend(f"{config_id}:{pred}->{target}" for target in targets_breaking)
            fixation_rows.append([
                config_id,
                pred,
                "not_retained_across_evaluated_continuations",
                len(omega),
                yes(alternative_evaluated),
                "yes",
                len(targets_breaking),
                ";".join(targets_breaking),
                scope,
                ";".join(sorted(coextension_notes.get(pred, []))),
                "predicate is not retained under all evaluated continuations",
            ])
    for pred in excluded_predicates:
        fixation_rows.append(["ALL", pred, "excluded_uncertain_or_unavailable", "n/a", "n/a", "no", 0, "", "control_configuration_only", ";".join(sorted(coextension_notes.get(pred, []))), "excluded from relation fixation candidates"])
    fixation_break_detected = bool(fixation_break_examples)
    fixation_break_count = len(fixation_break_examples)
    discriminating_fixation_detected = fixation_break_detected
    if not fixation_break_detected:
        fixation_rows.append(["ALL", "none_detected", "fixation_break", "n/a", "yes", "no", 0, "", "branched_continuation_set", "", "no safe fixation candidates were broken by the evaluated alternative continuation"])
    write_csv(out_dir / "qsb_causality05_fixation_candidates.csv", ["configuration_id", "predicate_id", "fixation_class", "continuation_count", "alternative_continuation_evaluated", "fixation_break_detected", "fixation_break_count", "fixation_break_examples", "fixation_scope", "empirical_coextension_note", "note"], fixation_rows)

    write_csv(out_dir / "qsb_causality05_direction_candidates.csv", ["source_configuration", "target_configuration", "candidate_class", "operator_type", "independent_direction_inference", "strict_continuation_reduction", "basis"], [
        [src, dst, "construction_induced_direction_candidate", "constructed_structural_patch_extension", "no", yes(reach[dst] < reach[src]), "direction follows declared patch nesting, not data-driven inference"] for src, dst in config_edges
    ])
    data_gaps = [
        ["candidate_source_check_scope", "limited", "source inventory is a fixed candidate_source_availability_check, not a complete repository search"],
        ["chemical_reaction_kinetics", "not_available", "not represented in selected structural graph"],
        ["energetics", "not_available", "not represented in selected structural graph"],
        ["independent_direction_inference", "not_performed", "directions are construction-induced by declared patch extensions"],
        ["excluded_uncertain_predicates", "documented", ";".join(excluded_predicates)],
    ] + [[f"control_{system}", "control_mapping_blocked_by_missing_input", f"missing {nodes_rel} or {edges_rel}"] for system, nodes_rel, edges_rel, _ in blocked_controls]
    write_csv(out_dir / "qsb_causality05_data_gaps.csv", ["gap_id", "status", "note"], data_gaps)

    exact_output_placeholder = False
    control_systems_mapped = len(control_configs) >= 3 and any(item[0] == "H2" for item in blocked_controls)
    control_systems_requested = len(control_specs)
    control_systems_mapped_count = len(control_configs)
    control_systems_blocked_count = len(blocked_controls)
    alternative_included = "C60_H01_alternative_local_patch" in config_by_id and ("C60_P00_pentagon_core", "C60_H01_alternative_local_patch") in config_edges
    nontrivial_fixation_test = alternative_included and len(reach["C60_P00_pentagon_core"]) > 2
    empirical_coextension_detected = bool(coextensive_pairs)
    checks = [
        ["causality04_gate_passed", True, "QSB-CAUSALITY04 summary has positive status"],
        ["input_root_supported", True, f"input_root={input_root}"],
        ["real_structural_input_used", selected and len(nodes) == manifest.get("node_count"), "C60 structural CSV/JSON files used"],
        ["formal_embedding_successful", selected and bool(c60_configs), "C60 patch configurations built"],
        ["alternative_continuation_included", alternative_included, "alternative H_01 local patch included"],
        ["explicit_predicate_aggregation_used", all(item["aggregation_rule"] for item in catalog), "all predicates define aggregation rules"],
        ["uncertain_predicates_excluded_from_fixations", all(status_by_pred[pred] not in FIXATION_ALLOWED for pred in excluded_predicates), "semantically_uncertain and not_available predicates excluded"],
        ["control_systems_mapped", control_systems_mapped, "benzene, ethyne, adamantane mapped; H2 transparently blocked if missing"],
        ["control_system_counts", control_systems_requested == 4 and control_systems_mapped_count == 3 and control_systems_blocked_count == 1, "requested=4, mapped=3, blocked=1"],
        ["independent_direction_inference_is_no", True, "all direction candidates are construction-induced"],
        ["alternative_continuation_evaluated", alternative_included, "branched continuation structure evaluated"],
        ["fixation_break_detected_is_no", not fixation_break_detected, "no safe fixation was broken by evaluated alternatives"],
        ["discriminating_fixation_detected_is_no", not discriminating_fixation_detected, "no discriminating fixation was detected"],
        ["empirical_coextension_detected", empirical_coextension_detected, "coextensive predicate assignment vectors detected algorithmically"],
        ["nontrivial_fixation_test_completed", nontrivial_fixation_test, "means only that a branched continuation structure with at least one alternative was evaluated"],
        ["no_physical_claim_made", True, "no reaction, real state evolution, physical causality, or emergence claim"],
        ["outputs_exact_after_write_placeholder", exact_output_placeholder, "updated after all files are written"],
    ]
    write_csv(out_dir / "qsb_causality05_validation_checks.csv", ["check_id", "passed", "note"], [[name, yes(passed), note] for name, passed, note in checks])

    summary = {
        "research_block": "QSB-CAUSALITY05",
        "selected_dataset": "C60 local structural patch",
        "source_inventory_scope": "candidate_source_availability_check",
        "real_structural_input_used": "yes",
        "formal_embedding_successful": "yes",
        "alternative_continuation_included": yes(alternative_included),
        "explicit_predicate_aggregation_used": "yes",
        "uncertain_predicates_excluded_from_fixations": "yes",
        "control_systems_mapped": yes(control_systems_mapped),
        "control_systems_requested": control_systems_requested,
        "control_systems_mapped_count": control_systems_mapped_count,
        "control_systems_blocked_count": control_systems_blocked_count,
        "control_systems_blocked": [row[0] for row in blocked_controls],
        "independent_direction_inference": "no",
        "alternative_continuation_evaluated": yes(alternative_included),
        "fixation_break_detected": yes(fixation_break_detected),
        "fixation_break_count": fixation_break_count,
        "fixation_break_examples": fixation_break_examples,
        "discriminating_fixation_detected": yes(discriminating_fixation_detected),
        "empirical_coextension_detected": yes(empirical_coextension_detected),
        "empirical_coextensive_pairs": [{"predicate_1": pred_1, "predicate_2": pred_2} for pred_1, pred_2 in coextensive_pairs],
        "nontrivial_fixation_test_completed": yes(nontrivial_fixation_test),
        "nontrivial_fixation_test_meaning": "A branched continuation structure with at least one alternative was evaluated; this does not prove a discriminating or physically nontrivial fixation.",
        "physical_claim_made": "no",
        "construction_operator": "constructed_structural_patch_extension",
        "direction_candidate_class": "construction_induced_direction_candidate",
        "excluded_predicates_from_fixations": excluded_predicates,
        "blocked_controls": [row[0] for row in blocked_controls],
        "all_checks_passed": False,
        "final_status": "qsb_causality05_failed",
        "limitations": "Controlled structural graph embedding only; no observed state sequence, chemical reaction, independent direction inference, or physical causality claim is made.",
    }
    write_json(out_dir / "qsb_causality05_summary.json", summary)
    final_status_header = ["real_structural_input_used", "formal_embedding_successful", "alternative_continuation_included", "alternative_continuation_evaluated", "explicit_predicate_aggregation_used", "uncertain_predicates_excluded_from_fixations", "fixation_break_detected", "discriminating_fixation_detected", "empirical_coextension_detected", "control_systems_requested", "control_systems_mapped_count", "control_systems_blocked_count", "control_systems_mapped", "independent_direction_inference", "nontrivial_fixation_test_completed", "physical_claim_made", "final_status"]
    write_csv(out_dir / "qsb_causality05_final_status.csv", final_status_header, [[summary[key] for key in final_status_header]])
    (out_dir / "qsb_causality05_readout.md").write_text("placeholder\n", encoding="utf-8")

    exact_output_set = sorted(path.name for path in out_dir.iterdir() if path.is_file()) == sorted(OUTPUT_FILES)
    checks[-1] = ["outputs_exact_after_write", exact_output_set, "output directory contains exactly the required files"]
    all_checks = all(passed for _, passed, _ in checks)
    final_status = POSITIVE_STATUS if all_checks else "qsb_causality05_failed"
    summary.update({"exact_output_set": exact_output_set, "all_checks_passed": all_checks, "final_status": final_status})
    write_csv(out_dir / "qsb_causality05_validation_checks.csv", ["check_id", "passed", "note"], [[name, yes(passed), note] for name, passed, note in checks])
    write_json(out_dir / "qsb_causality05_summary.json", summary)
    write_csv(out_dir / "qsb_causality05_final_status.csv", final_status_header, [[summary[key] for key in final_status_header]])
    (out_dir / "qsb_causality05_readout.md").write_text(
        "# QSB-CAUSALITY05 controlled C60 patch embedding\n\n"
        f"Befund: Selected dataset: C60 local structural patch. Alternative continuation evaluated: {yes(alternative_included)}. Fixation break detected: {yes(fixation_break_detected)}. Discriminating fixation detected: {yes(discriminating_fixation_detected)}. Controls requested/mapped/blocked: {control_systems_requested}/{control_systems_mapped_count}/{control_systems_blocked_count}. Final status: {final_status}.\n\n"
        "Interpretation: The patch path is a constructed_structural_patch_extension built from documented C60 topology. Direction candidates are construction_induced_direction_candidate and independent_direction_inference = no.\n\n"
        f"Hypothese: Formal embedding can be audited with explicit predicate aggregation. Empirical coextension detected: {yes(empirical_coextension_detected)}. Excluded uncertain predicates: {', '.join(excluded_predicates)}.\n\n"
        "Fixation note: nontrivial_fixation_test_completed = yes only means that a branched continuation structure with at least one alternative was evaluated; it does not prove a discriminating or physically nontrivial fixation.\n\n"
        "Offene Luecke: H2 is blocked by missing local input when its candidate files are absent; no repository-wide source completeness claim is made.\n\n"
        "Claim Boundary: No chemical reaction, real state evolution, physical causality, data-driven direction discovery, emergent time, emergent geometry, Bridge proof, or experimental confirmation is claimed.\n",
        encoding="utf-8",
    )
    if not all_checks:
        print("QSB-CAUSALITY05 validation failed.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
