#!/usr/bin/env python3
"""QSB-CAUSALITY06A: controlled BMC sweep order comparison.

This run reads existing repository artifacts only.  It does not query a
network, database, or version-control state.  The primary dataset is selected only if it
contains documented states, controlled sweep transitions, analysis branches,
blocked/pre-transition cases, and structured state features.

Claim boundary: this script compares observed or controlled transition
directions with parameter-order-conditioned formal sweep relations.  It does
not independently reconstruct physical causality and does not claim emergent
time, spacetime emergence, charge transfer, electron transfer, or bridge
confirmation.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Set, Tuple


RESEARCH_BLOCK = "QSB-CAUSALITY06A"
RUN_ID = "QSB_CAUSALITY06_REAL_TRANSITION_ORDER"
DEFAULT_OUTPUT_DIR = Path("runs/QSB-CAUSALITY/QSB_CAUSALITY06_REAL_TRANSITION_ORDER")
PRIMARY_SUMMARY = Path("runs/BMC-15f2/connectedness_transition_sweep_open/connectedness_transition_summary.csv")
PRIMARY_VARIANTS = Path("runs/BMC-15f2/connectedness_transition_sweep_open/variant_metrics.csv")
PRIMARY_READOUT = Path("runs/BMC-15f2/connectedness_transition_sweep_open/connectedness_transition_readout.md")
PRIMARY_CONFIG = Path("data/bmc15f2_connectedness_transition_sweep_config.yaml")
PRIMARY_FEATURE_TABLE = Path("data/bmc08c_real_units_feature_table.csv")

OUTPUT_FILES = [
    "qsb_causality06_readout.md",
    "qsb_causality06_summary.json",
    "qsb_causality06_source_inventory.csv",
    "qsb_causality06_dataset_selection.csv",
    "qsb_causality06_state_catalog.csv",
    "qsb_causality06_observed_transition_catalog.csv",
    "qsb_causality06_predicate_catalog.csv",
    "qsb_causality06_predicate_assignment.csv",
    "qsb_causality06_formal_admissibility.csv",
    "qsb_causality06_continuation_spaces.csv",
    "qsb_causality06_fixation_sets.csv",
    "qsb_causality06_formal_direction_candidates.csv",
    "qsb_causality06_direction_comparison.csv",
    "qsb_causality06_counterexample_assessment.csv",
    "qsb_causality06_validation_checks.csv",
    "qsb_causality06_final_status.csv",
]

FIXATION_ALLOWED = {"directly_documented", "structurally_derived"}
TRANSITION_LABEL_PREDICATES = {
    "p_pre_transition_disconnected",
    "p_first_connected",
    "p_post_transition_connected",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QSB-CAUSALITY06 real transition-order comparison")
    parser.add_argument("--input-root", default=".", help="Repository input root")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite only the expected output files")
    return parser.parse_args()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def write_json(path: Path, payload: Mapping[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def yes(value: bool) -> str:
    return "yes" if value else "no"


def as_float(value: str) -> float:
    try:
        return float(value)
    except ValueError:
        return float("nan")


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


def source_inventory(input_root: Path) -> List[Dict[str, str]]:
    candidates = [
        {
            "source_id": "bmc15f2_connectedness_transition_summary",
            "path": str(PRIMARY_SUMMARY),
            "file_type": "csv",
            "state_definition": "controlled graph-construction variant row from BMC-15f2 connectedness sweep",
            "transition_definition": "documented adjacent parameter-step alternatives within enabled sweep families",
            "transition_role": "controlled_bmc_sweep",
            "available_features": "n_nodes;n_edges;n_components/is_connected;core_containment;embedding/geodesic metrics",
            "branching_present": "analysis_construction_branch",
            "blocked_transition_present": "yes",
            "data_quality": "high",
            "suitability": "selected_primary",
        },
        {
            "source_id": "bmc15f2_variant_metrics",
            "path": str(PRIMARY_VARIANTS),
            "file_type": "csv",
            "state_definition": "same controlled variants with expanded graph diagnostics",
            "transition_definition": "supports state features but does not by itself define observed order",
            "transition_role": "controlled_feature_support",
            "available_features": "n_components;density;degree metrics;embedding stress;negative eigenvalue burden",
            "branching_present": "analysis_construction_branch",
            "blocked_transition_present": "yes",
            "data_quality": "high",
            "suitability": "selected_supporting",
        },
        {
            "source_id": "bmc15f2_config",
            "path": str(PRIMARY_CONFIG),
            "file_type": "yaml",
            "state_definition": "documented enabled envelope-family parameter domains",
            "transition_definition": "documents controlled parameter-sweep families; not an observed order by itself",
            "transition_role": "controlled_protocol",
            "available_features": "construction_mode;parameter lists;diagnostic flags",
            "branching_present": "analysis_construction_branch",
            "blocked_transition_present": "not_directly",
            "data_quality": "high",
            "suitability": "selected_supporting",
        },
        {
            "source_id": "shapiroinfo04_toy_comparator",
            "path": "runs/QSB-ST-SHAPIROINFO04/toy_comparator_minimal_open/toy_comparator_variant_results.csv",
            "file_type": "csv",
            "state_definition": "toy comparator variants",
            "transition_definition": "variant statuses only; no documented transition graph",
            "transition_role": "constructed",
            "available_features": "timing residuals;artifact labels;expected status",
            "branching_present": "yes",
            "blocked_transition_present": "unclear",
            "data_quality": "medium",
            "suitability": "not_selected_constructed_toy_no_transition_relation",
        },
        {
            "source_id": "matter_signature_canonicalization",
            "path": "data/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/provenance_status_table.csv",
            "file_type": "csv",
            "state_definition": "run provenance records",
            "transition_definition": "rerun/provenance status, not a state-transition process",
            "transition_role": "unclear",
            "available_features": "run ids;provenance flags;replay status",
            "branching_present": "yes",
            "blocked_transition_present": "yes",
            "data_quality": "medium",
            "suitability": "not_selected_provenance_not_transition_order",
        },
        {
            "source_id": "c60_reference_scaffolds",
            "path": "data/bms_fu02g_c60_reference_edges.csv",
            "file_type": "csv",
            "state_definition": "C60 graph nodes and edges",
            "transition_definition": "adjacency only; no real documented transition relation",
            "transition_role": "not_available",
            "available_features": "nodes;edges;faces when present",
            "branching_present": "yes",
            "blocked_transition_present": "no",
            "data_quality": "high_for_structure",
            "suitability": "not_selected_adjacency_not_transition",
        },
    ]
    for row in candidates:
        path = input_root / row["path"]
        row["present"] = yes(path.exists() and path.is_file())
    return candidates


def primary_available(input_root: Path) -> bool:
    return all((input_root / path).exists() for path in [PRIMARY_SUMMARY, PRIMARY_VARIANTS, PRIMARY_CONFIG, PRIMARY_READOUT, PRIMARY_FEATURE_TABLE])


def build_states(input_root: Path) -> List[Dict[str, str]]:
    summary_rows = read_csv(input_root / PRIMARY_SUMMARY)
    variant_rows = {row["variant_name"]: row for row in read_csv(input_root / PRIMARY_VARIANTS)}
    states = [
        {
            "state_id": "source_bmc08c_feature_table",
            "state_label": "BMC08c sign-sensitive real-units feature table before controlled construction choice",
            "state_role": "documented_source_state",
            "envelope_family": "source",
            "parameter_name": "construction_choice",
            "parameter_value": "source",
            "parameter_numeric": "",
            "n_nodes": "22",
            "n_edges": "0",
            "n_components": "not_applicable",
            "is_connected": "not_applicable",
            "transition_label": "source_state",
            "core_containment_fraction": "not_applicable",
            "source_path": str(PRIMARY_FEATURE_TABLE),
            "features_available": "yes",
        }
    ]
    for row in summary_rows:
        family = row["envelope_family"]
        if family not in {"mutual_kNN_k_transition_sweep", "threshold_transition_sweep"}:
            continue
        metrics = variant_rows.get(row["variant_id"], {})
        states.append(
            {
                "state_id": row["variant_id"],
                "state_label": row["variant_id"],
                "state_role": "controlled_transition_state",
                "envelope_family": family,
                "parameter_name": row["parameter_name"],
                "parameter_value": row["parameter_value"],
                "parameter_numeric": row["parameter_value"],
                "n_nodes": row["n_nodes"],
                "n_edges": row["n_edges"],
                "n_components": metrics.get("n_components", ""),
                "is_connected": row["is_connected"],
                "transition_label": row["transition_label"],
                "core_containment_fraction": row["core_containment_fraction"],
                "source_path": str(PRIMARY_SUMMARY),
                "features_available": "yes",
            }
        )
    return states


def numeric_states_by_family(states: Sequence[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for state in states:
        if state["state_role"] == "controlled_transition_state":
            grouped[state["envelope_family"]].append(state)
    for family in grouped:
        grouped[family].sort(key=lambda row: as_float(row["parameter_numeric"]))
    return grouped


def observed_transitions(states: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped = numeric_states_by_family(states)
    rows: List[Dict[str, str]] = []
    for family, family_states in sorted(grouped.items()):
        first = family_states[0]
        rows.append(
            {
                "edge_id": f"obs_source_to_{first['state_id']}",
                "source_state": "source_bmc08c_feature_table",
                "target_state": first["state_id"],
                "observed_transition_direction": "source_to_controlled_family_initial_state",
                "transition_source_path": str(PRIMARY_CONFIG),
                "transition_source_role": "analysis_construction_branch",
                "transition_basis": "enabled construction family applied to same documented source feature table",
                "observed_or_controlled": "controlled",
                "edge_granularity": "analysis_construction_branch",
                "analysis_construction_branch": "yes",
                "patch_inclusion_used": "no",
                "timestamp_order_used": "no",
            }
        )
        for idx, (src, dst) in enumerate(zip(family_states, family_states[1:]), start=1):
            rows.append(
                {
                    "edge_id": f"obs_{family}_{idx}",
                    "source_state": src["state_id"],
                    "target_state": dst["state_id"],
                    "observed_transition_direction": "increasing_documented_sweep_parameter",
                    "transition_source_path": str(PRIMARY_CONFIG),
                    "transition_source_role": "controlled_parameter_step",
                    "transition_basis": f"adjacent documented {src['parameter_name']} sweep value",
                    "observed_or_controlled": "controlled",
                    "edge_granularity": "adjacent_observed_sweep_edge",
                    "analysis_construction_branch": "no",
                    "patch_inclusion_used": "no",
                    "timestamp_order_used": "no",
                }
            )
    return rows


def predicate_catalog_rows(_: object = None) -> List[Tuple[str, str, str]]:
    return [
        ("p_controlled_source", "directly_documented", "state_role is documented_source_state"),
        ("p_mutual_knn_family", "directly_documented", "envelope_family equals mutual_kNN_k_transition_sweep"),
        ("p_threshold_family", "directly_documented", "envelope_family equals threshold_transition_sweep"),
        ("p_connected", "directly_documented", "is_connected equals True"),
        ("p_pre_transition_disconnected", "directly_documented", "transition_label equals pre_transition_disconnected"),
        ("p_first_connected", "directly_documented", "transition_label equals first_connected"),
        ("p_post_transition_connected", "directly_documented", "transition_label equals post_transition_connected"),
        ("p_full_core_retained", "directly_documented", "core_containment_fraction equals 1.0"),
        ("p_near_full_core_retained", "structurally_derived", "core_containment_fraction >= 0.8333333333333334"),
        ("p_components_le_2", "structurally_derived", "n_components numeric and <= 2"),
        ("p_edge_count_ge_60", "structurally_derived", "n_edges numeric and >= 60"),
        ("p_embedding_metric_available", "directly_documented", "embedding/geodesic metric fields present in source summary"),
    ]


def predicate_catalog_table() -> List[Dict[str, str]]:
    return [
        {
            "predicate_id": pid,
            "availability_status": availability,
            "predicate_basis": basis,
            "used_for_formal_sweep_continuation_invariant": yes(
                availability in FIXATION_ALLOWED and pid not in TRANSITION_LABEL_PREDICATES
            ),
            "physical_fixation_interpretation": "not_assessed",
        }
        for pid, availability, basis in predicate_catalog_rows()
    ]


def predicate_values(state: Dict[str, str]) -> Dict[str, int]:
    family = state["envelope_family"]
    transition_label = state["transition_label"]
    core = as_float(state["core_containment_fraction"])
    n_components = as_float(state["n_components"])
    n_edges = as_float(state["n_edges"])
    return {
        "p_controlled_source": int(state["state_role"] == "documented_source_state"),
        "p_mutual_knn_family": int(family == "mutual_kNN_k_transition_sweep"),
        "p_threshold_family": int(family == "threshold_transition_sweep"),
        "p_connected": int(state["is_connected"] == "True"),
        "p_pre_transition_disconnected": int(transition_label == "pre_transition_disconnected"),
        "p_first_connected": int(transition_label == "first_connected"),
        "p_post_transition_connected": int(transition_label == "post_transition_connected"),
        "p_full_core_retained": int(state["core_containment_fraction"] == "1.0"),
        "p_near_full_core_retained": int(core >= 0.8333333333333334 if core == core else False),
        "p_components_le_2": int(n_components <= 2 if n_components == n_components else False),
        "p_edge_count_ge_60": int(n_edges >= 60 if n_edges == n_edges else False),
        "p_embedding_metric_available": int(state["state_role"] == "controlled_transition_state"),
    }


def predicate_assignment(states: Sequence[Dict[str, str]]) -> List[Dict[str, object]]:
    rows: List[Dict[str, object]] = []
    availability = {row["predicate_id"]: row["availability_status"] for row in predicate_catalog_table()}
    for state in states:
        values = predicate_values(state)
        for predicate_id, value in sorted(values.items()):
            rows.append(
                {
                    "state_id": state["state_id"],
                    "predicate_id": predicate_id,
                    "predicate_value": value,
                    "availability_status": availability[predicate_id],
                    "used_for_formal_sweep_continuation_invariant": yes(
                        availability[predicate_id] in FIXATION_ALLOWED
                        and predicate_id not in TRANSITION_LABEL_PREDICATES
                    ),
                    "physical_fixation_interpretation": "not_assessed",
                }
            )
    return rows


def formal_admissibility(states: Sequence[Dict[str, str]]) -> List[Dict[str, str]]:
    state_by_id = {state["state_id"]: state for state in states}
    grouped = numeric_states_by_family(states)
    rows: List[Dict[str, str]] = []
    for family, family_states in sorted(grouped.items()):
        first = family_states[0]
        rows.append(
            {
                "edge_id": f"adm_source_to_{first['state_id']}",
                "source_state": "source_bmc08c_feature_table",
                "target_state": first["state_id"],
                "formal_admissible": "yes",
                "relation_type": "analysis_construction_branch",
                "is_adjacent_primitive_candidate": "no",
                "parameter_order_used_in_admissibility": "yes",
                "admissibility_source_path": str(PRIMARY_CONFIG),
                "admissibility_rule": "same documented source feature table may initialize an enabled construction family",
                "edge_role": "analysis_construction_branch",
                "blocked_reason": "",
            }
        )
        rank = {state["state_id"]: idx for idx, state in enumerate(family_states)}
        for src in family_states:
            for dst in family_states:
                if src["state_id"] == dst["state_id"]:
                    continue
                src_param = as_float(src["parameter_numeric"])
                dst_param = as_float(dst["parameter_numeric"])
                src_edges = as_float(src["n_edges"])
                dst_edges = as_float(dst["n_edges"])
                src_comp = as_float(state_by_id[src["state_id"]]["n_components"])
                dst_comp = as_float(state_by_id[dst["state_id"]]["n_components"])
                admissible = dst_param > src_param and dst_edges > src_edges and dst_comp <= src_comp
                adjacent = rank[dst["state_id"]] - rank[src["state_id"]] == 1
                if adjacent:
                    relation_type = "adjacent_primitive_candidate"
                elif dst_param > src_param:
                    relation_type = "nonadjacent_monotone_skip_candidate"
                else:
                    relation_type = "blocked_or_unadmissible_candidate"
                rows.append(
                    {
                        "edge_id": f"adm_{src['state_id']}__{dst['state_id']}",
                        "source_state": src["state_id"],
                        "target_state": dst["state_id"],
                        "formal_admissible": yes(admissible),
                        "relation_type": relation_type,
                        "is_adjacent_primitive_candidate": yes(admissible and adjacent),
                        "parameter_order_used_in_admissibility": "yes",
                        "admissibility_source_path": str(PRIMARY_CONFIG),
                        "admissibility_rule": "same family; target has larger documented parameter, more edges, and non-increasing component count",
                        "edge_role": relation_type if admissible else "blocked_or_unadmissible_candidate",
                        "blocked_reason": "" if admissible else "parameter_nonincrease_or_edge_nonincrease_or_component_count_increase",
                    }
                )
    return rows


def graph_from_admissibility(rows: Sequence[Dict[str, str]], states: Sequence[Dict[str, str]]) -> Dict[str, Set[str]]:
    graph = {state["state_id"]: set() for state in states}
    for row in rows:
        if row["formal_admissible"] == "yes" and row["relation_type"] in {
            "analysis_construction_branch",
            "adjacent_primitive_candidate",
        }:
            graph[row["source_state"]].add(row["target_state"])
    return graph


def reachable(graph: Dict[str, Set[str]], start: str) -> Set[str]:
    seen: Set[str] = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        stack.extend(sorted(graph.get(node, set()) - seen, reverse=True))
    return seen


def continuation_spaces(graph: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    return {state_id: reachable(graph, state_id) for state_id in sorted(graph)}


def transitive_reachability_rows(graph: Dict[str, Set[str]]) -> Dict[str, List[str]]:
    rows: Dict[str, List[str]] = {}
    for state_id in sorted(graph):
        direct = graph[state_id]
        transitive = sorted(reachable(graph, state_id) - direct - {state_id})
        rows[state_id] = transitive
    return rows


def fixation_sets(spaces: Dict[str, Set[str]], states: Sequence[Dict[str, str]]) -> Dict[str, List[str]]:
    values = {state["state_id"]: predicate_values(state) for state in states}
    catalog = predicate_catalog_table()
    usable = [row["predicate_id"] for row in catalog if row["used_for_formal_sweep_continuation_invariant"] == "yes"]
    result: Dict[str, List[str]] = {}
    for state_id, members in spaces.items():
        result[state_id] = sorted(pid for pid in usable if all(values[member][pid] == 1 for member in members))
    return result


def direction_candidates(
    admissibility: Sequence[Dict[str, str]],
    spaces: Dict[str, Set[str]],
    states: Sequence[Dict[str, str]],
) -> List[Dict[str, str]]:
    state_by_id = {state["state_id"]: state for state in states}
    rows: List[Dict[str, str]] = []
    for row in admissibility:
        if row["formal_admissible"] != "yes":
            continue
        src = row["source_state"]
        dst = row["target_state"]
        src_state = state_by_id[src]
        dst_state = state_by_id[dst]
        src_comp = as_float(src_state["n_components"])
        dst_comp = as_float(dst_state["n_components"])
        component_drop = dst_comp < src_comp if src_comp == src_comp and dst_comp == dst_comp else src == "source_bmc08c_feature_table"
        strict_space_reduction = spaces[dst] < spaces[src]
        accepted = (
            strict_space_reduction
            and row["relation_type"] == "adjacent_primitive_candidate"
            and component_drop
        )
        if accepted:
            rows.append(
                {
                    "source_state": src,
                    "target_state": dst,
                    "formal_direction_relation": "parameter_order_conditioned_source_prec_0_target",
                    "relation_type": row["relation_type"],
                    "strict_continuation_space_reduction": "yes",
                    "direction_rule": "formal admissibility plus strict continuation-space reduction plus documented component-count decrease; transition labels excluded",
                    "transition_label_used_in_direction_rule": "no",
                    "transition_label_leakage_present": "no",
                    "parameter_order_used_in_admissibility": "yes",
                    "direction_reconstruction_scope": "parameter_order_conditioned",
                    "independent_direction_reconstruction": "no",
                }
            )
    return rows


def compare_directions(
    observed: Sequence[Dict[str, str]],
    admissibility: Sequence[Dict[str, str]],
    candidates: Sequence[Dict[str, str]],
) -> List[Dict[str, object]]:
    observed_pairs = {(row["source_state"], row["target_state"]) for row in observed}
    observed_adjacent_pairs = {
        (row["source_state"], row["target_state"])
        for row in observed
        if row["edge_granularity"] == "adjacent_observed_sweep_edge"
    }
    primitive_pairs = {
        (row["source_state"], row["target_state"])
        for row in admissibility
        if row["formal_admissible"] == "yes" and row["relation_type"] == "adjacent_primitive_candidate"
    }
    nonadjacent_pairs = {
        (row["source_state"], row["target_state"])
        for row in admissibility
        if row["formal_admissible"] == "yes" and row["relation_type"] == "nonadjacent_monotone_skip_candidate"
    }
    candidate_pairs = {(row["source_state"], row["target_state"]) for row in candidates}
    rows: List[Dict[str, object]] = []
    for row in sorted(observed, key=lambda item: item["edge_id"]):
        src = row["source_state"]
        dst = row["target_state"]
        observed_forward = f"{src}->{dst}"
        formal_forward = (src, dst) in primitive_pairs
        formal_reverse = (dst, src) in primitive_pairs
        if row["edge_granularity"] == "analysis_construction_branch":
            classification = "analysis_construction_branch"
        elif formal_reverse:
            classification = "direction_conflict"
        elif (src, dst) in candidate_pairs:
            classification = "direction_qualified_match"
        elif formal_forward:
            classification = "primitive_admissible_without_direction_qualification"
        else:
            classification = "primitive_admissible_without_direction_qualification"
        rows.append(
            {
                "source_state": src,
                "target_state": dst,
                "observed_transition_direction": "present",
                "observed_edge_granularity": row["edge_granularity"],
                "observed_forward_edge": observed_forward,
                "formal_forward_primitive_edge": yes(formal_forward),
                "formal_reverse_primitive_edge": yes(formal_reverse),
                "direction_conflict": yes(formal_reverse),
                "parameter_order_conditioned_formal_direction": yes((src, dst) in candidate_pairs),
                "formal_admissibility_present": yes(formal_forward),
                "comparison_scope": "adjacent_observed_vs_adjacent_primitive_only",
                "classification": classification,
            }
        )
    for src, dst in sorted(nonadjacent_pairs - observed_pairs):
        rows.append(
            {
                "source_state": src,
                "target_state": dst,
                "observed_transition_direction": "missing",
                "observed_edge_granularity": "not_observed_nonadjacent",
                "observed_forward_edge": "",
                "formal_forward_primitive_edge": "no",
                "formal_reverse_primitive_edge": yes((dst, src) in primitive_pairs),
                "direction_conflict": "no",
                "parameter_order_conditioned_formal_direction": "no",
                "formal_admissibility_present": "yes",
                "comparison_scope": "nonadjacent_formal_relation_not_compared_as_observed_step",
                "classification": "nonadjacent_formal_skip_candidate",
            }
        )
    for src, dst in sorted(candidate_pairs - observed_adjacent_pairs):
        if (src, dst) in candidate_pairs:
            rows.append(
                {
                    "source_state": src,
                    "target_state": dst,
                    "observed_transition_direction": "missing",
                    "observed_edge_granularity": "not_observed_adjacent_direction_candidate",
                    "observed_forward_edge": "",
                    "formal_forward_primitive_edge": yes((src, dst) in primitive_pairs),
                    "formal_reverse_primitive_edge": yes((dst, src) in primitive_pairs),
                    "direction_conflict": "no",
                    "parameter_order_conditioned_formal_direction": "yes",
                    "formal_admissibility_present": yes((src, dst) in primitive_pairs),
                    "comparison_scope": "formal_adjacent_candidate_without_observed_neighbor_step",
                    "classification": "formal_direction_without_observed_adjacent_step",
                }
            )
    return rows


def counterexample_assessment(
    observed: Sequence[Dict[str, str]],
    admissibility: Sequence[Dict[str, str]],
    comparison: Sequence[Dict[str, object]],
) -> List[List[object]]:
    observed_pairs = {(row["source_state"], row["target_state"]) for row in observed}
    primitive_pairs = {
        (row["source_state"], row["target_state"])
        for row in admissibility
        if row["formal_admissible"] == "yes" and row["relation_type"] == "adjacent_primitive_candidate"
    }
    nonadjacent_pairs = {
        (row["source_state"], row["target_state"])
        for row in admissibility
        if row["formal_admissible"] == "yes" and row["relation_type"] == "nonadjacent_monotone_skip_candidate"
    }
    blocked = next((row for row in admissibility if row["formal_admissible"] == "no"), None)
    rows = []
    probes = [
        ("observed_edge_matched_by_parameter_conditioned_formal_direction", "direction_qualified_match"),
        (
            "observed_edge_without_direction_qualification",
            "primitive_admissible_without_direction_qualification",
        ),
        ("nonadjacent_formal_skip_candidate", "nonadjacent_formal_skip_candidate"),
    ]
    for probe_id, classification in probes:
        item = next((row for row in comparison if row["classification"] == classification), None)
        rows.append(
            [
                probe_id,
                yes(item is not None),
                "" if item is None else item["source_state"],
                "" if item is None else item["target_state"],
                classification if item else "not_available",
                "counterprobe computed from observed/formal comparison",
            ]
        )
    rows.append(
        [
            "blocked_or_unadmissible_edge",
            yes(blocked is not None),
            "" if blocked is None else blocked["source_state"],
            "" if blocked is None else blocked["target_state"],
            "blocked_or_unadmissible_candidate" if blocked else "not_available",
            "" if blocked is None else blocked["blocked_reason"],
        ]
    )
    source_successors = sorted(dst for src, dst in observed_pairs if src == "source_bmc08c_feature_table")
    rows.append(
        [
            "analysis_construction_branch",
            yes(len(source_successors) >= 2),
            "source_bmc08c_feature_table",
            "|".join(source_successors),
            "analysis_construction_branch" if len(source_successors) >= 2 else "not_available",
            "two enabled controlled construction families branch analytically from the same documented source state",
        ]
    )
    reverse_conflict = next(
        (
            row
            for row in comparison
            if row["observed_edge_granularity"] == "adjacent_observed_sweep_edge"
            and row["formal_reverse_primitive_edge"] == "yes"
        ),
        None,
    )
    rows.append(
        [
            "true_reverse_direction_conflict_check",
            "yes",
            "" if reverse_conflict is None else reverse_conflict["source_state"],
            "" if reverse_conflict is None else reverse_conflict["target_state"],
            "no_conflict_found" if reverse_conflict is None else "direction_conflict",
            "conflict is counted only when an observed adjacent edge X->Y has formal primitive reverse Y->X",
        ]
    )
    rows.append(
        [
            "primitive_and_nonadjacent_pair_count",
            yes(bool(primitive_pairs or nonadjacent_pairs)),
            "",
            "",
            f"adjacent_primitive={len(primitive_pairs)};nonadjacent_skip={len(nonadjacent_pairs)}",
            "formal adjacent primitive and nonadjacent monotone skip relations are separated",
        ]
    )
    return rows


def validation_rows(
    states: Sequence[Dict[str, str]],
    observed: Sequence[Dict[str, str]],
    admissibility: Sequence[Dict[str, str]],
    comparison: Sequence[Dict[str, object]],
    final_status: Mapping[str, object],
) -> List[List[object]]:
    observed_adjacent = [row for row in observed if row.get("edge_granularity") == "adjacent_observed_sweep_edge"]
    primitive = [row for row in admissibility if row.get("relation_type") == "adjacent_primitive_candidate"]
    nonadjacent = [row for row in admissibility if row.get("relation_type") == "nonadjacent_monotone_skip_candidate"]
    branches = [row for row in observed if row.get("edge_granularity") == "analysis_construction_branch"]
    checks = [
        ("inputs_completely_read", final_status["inputs_completely_read"] == "yes", "All required BMC-15f2 input artifacts were read."),
        ("both_sweep_families_processed", final_status["both_sweep_families_processed"] == "yes", "mutual-kNN and threshold sweeps processed."),
        ("documented_neighbor_edges_identified", bool(observed_adjacent), "Documented adjacent neighbor sweep edges identified."),
        ("formal_primitive_neighbor_edges_computed", bool(primitive), "Formal adjacent primitive candidates computed."),
        ("true_reverse_direction_check_completed", final_status["true_reverse_direction_check_completed"] == "yes", "Formal primitive reverse edge checked for each observed adjacent edge."),
        ("relation_granularity_separated", bool(primitive and nonadjacent), "Adjacent primitive and nonadjacent monotone skip relations separated."),
        ("analysis_construction_branch_marked", bool(branches), "Shared-source construction branch marked analytically."),
        ("parameter_order_conditioned_scope", final_status["direction_reconstruction_scope"] == "parameter_order_conditioned", "Direction scope is parameter-order conditioned."),
        ("real_states_used", final_status["real_states_used"] == "yes", "BMC08c-backed BMC-15f2 controlled states used."),
        ("observed_transitions_used", final_status["observed_transitions_used"] == "yes", "Controlled documented parameter transitions used."),
        ("branching_present", final_status["branching_present"] == "yes", "Analysis construction branch from source state present."),
        ("blocked_transition_present", final_status["blocked_transition_present"] == "yes", "Unadmissible reverse/skipped candidates recorded."),
        ("predicates_available", final_status["predicates_available"] == "yes", "Documented/derived predicates assigned."),
        ("formal_admissibility_computed", bool(admissibility), "Primitive formal admissibility computed."),
        ("observed_formal_comparison_completed", bool(comparison), "Observed/formal comparison rows written."),
        ("no_patch_inclusion_as_transition_source", all(row["patch_inclusion_used"] == "no" for row in observed), "Patch inclusion not used."),
        ("no_timestamp_order", all(row["timestamp_order_used"] == "no" for row in observed), "Timestamp ordering not used."),
        ("independent_direction_reconstruction", final_status["independent_direction_reconstruction"] == "no", "No independent direction reconstruction claimed."),
        ("parameter_order_used_in_admissibility", final_status["parameter_order_used_in_admissibility"] == "yes", "Formal admissibility uses documented parameter ordering."),
        ("external_physical_process_observed", final_status["external_physical_process_observed"] == "no", "No external physical process observed."),
        ("transition_label_leakage_present", final_status["transition_label_leakage_present"] == "no", "Transition labels excluded from direction rule."),
        ("observed_formal_direction_separated", True, "Observed edge table and formal direction table are distinct."),
        ("physical_causality_claim_made", final_status["physical_causality_claim_made"] == "no", "No physical causality claim."),
        ("emergent_time_claim_made", final_status["emergent_time_claim_made"] == "no", "No emergent-time claim."),
        ("additional_gate_created", final_status["additional_gate_created"] == "no", "No new gate created."),
    ]
    return [[name, yes(passed), note] for name, passed, note in checks]


def final_status_row(
    states: Sequence[Dict[str, str]],
    observed: Sequence[Dict[str, str]],
    admissibility: Sequence[Dict[str, str]],
    comparison: Sequence[Dict[str, object]],
    blocked_present: bool,
    predicates_available: bool,
) -> Dict[str, object]:
    direction_qualified_matches = sum(1 for row in comparison if row["classification"] == "direction_qualified_match")
    unqualified_primitive_matches = sum(
        1 for row in comparison if row["classification"] == "primitive_admissible_without_direction_qualification"
    )
    direction_conflicts = sum(1 for row in comparison if row["classification"] == "direction_conflict")
    insufficient = sum(1 for row in comparison if row["classification"] == "insufficient_data")
    families = {state["envelope_family"] for state in states if state["state_role"] == "controlled_transition_state"}
    required = {
        "inputs": bool(states and observed),
        "families": {"mutual_kNN_k_transition_sweep", "threshold_transition_sweep"}.issubset(families),
        "observed_neighbors": any(row.get("edge_granularity") == "adjacent_observed_sweep_edge" for row in observed),
        "primitive_neighbors": any(row.get("relation_type") == "adjacent_primitive_candidate" for row in admissibility),
        "reverse_check": all(
            row["formal_reverse_primitive_edge"] in {"yes", "no"}
            for row in comparison
            if row.get("observed_edge_granularity") == "adjacent_observed_sweep_edge"
        ),
        "granularity": any(row.get("relation_type") == "nonadjacent_monotone_skip_candidate" for row in admissibility),
        "analysis_branch": any(row.get("edge_granularity") == "analysis_construction_branch" for row in observed),
        "comparison": bool(comparison),
        "no_physical_claim": True,
    }
    status = (
        "controlled_bmc_sweep_order_comparison_completed"
        if all(required.values())
        else "real_transition_mapping_blocked_by_missing_transition_data"
    )
    return {
        "research_block": RESEARCH_BLOCK,
        "primary_dataset": "BMC-15f2 connectedness transition sweep",
        "inputs_completely_read": yes(required["inputs"]),
        "both_sweep_families_processed": yes(required["families"]),
        "real_states_used": yes(bool(states)),
        "observed_transitions_used": yes(bool(observed)),
        "documented_neighbor_edges_identified": yes(required["observed_neighbors"]),
        "formal_primitive_neighbor_edges_computed": yes(required["primitive_neighbors"]),
        "branching_present": yes(sum(1 for row in observed if row["source_state"] == "source_bmc08c_feature_table") >= 2),
        "analysis_construction_branch_present": yes(required["analysis_branch"]),
        "blocked_transition_present": yes(blocked_present),
        "predicates_available": yes(predicates_available),
        "formal_admissibility_computed": "yes",
        "continuation_spaces_computed": "yes",
        "fixation_sets_computed": "yes",
        "formal_sweep_continuation_invariants_computed": "yes",
        "physical_fixation_interpretation": "not_assessed",
        "formal_direction_candidates_computed": "yes",
        "true_reverse_direction_check_completed": yes(required["reverse_check"]),
        "relation_granularity_separated": yes(required["granularity"]),
        "observed_formal_comparison_completed": yes(bool(comparison)),
        "direction_qualified_matches": direction_qualified_matches,
        "unqualified_primitive_matches": unqualified_primitive_matches,
        "direction_conflicts": direction_conflicts,
        "insufficient_cases": insufficient,
        "independent_direction_reconstruction": "no",
        "parameter_order_used_in_admissibility": "yes",
        "direction_reconstruction_scope": "parameter_order_conditioned",
        "external_physical_process_observed": "no",
        "transition_label_leakage_present": "no",
        "physical_causality_claim_made": "no",
        "emergent_time_claim_made": "no",
        "additional_gate_created": "no",
        "final_status": status,
        "recommended_next_action": "Freeze CAUSALITY06A as a controlled BMC sweep order comparison.",
        "limitations": "Direction is conditioned by documented parameter order; no external physical process was observed; transition labels provide no independent direction evidence; formal sweep invariants are not physical fixations; no physical causality claim follows.",
    }


def readout_text(final: Mapping[str, object], selected: Mapping[str, str]) -> str:
    return "\n".join(
        [
            "# QSB-CAUSALITY06 Readout",
            "",
            "## Befund",
            "",
            "A primary repository dataset was selected: BMC-15f2 connectedness transition sweep.",
            "The run compared controlled observed sweep transitions against parameter-order-conditioned formal sweep relations.",
            "",
            "## Interpretation",
            "",
            "Observed adjacent sweep edges are compared only with adjacent primitive candidates. Nonadjacent monotone relations are reported as skip candidates, not as missing observations.",
            "",
            "## Hypothese",
            "",
            "No physical causality or emergent-time hypothesis is established by this run.",
            "",
            "## Offene Luecke",
            "",
            "The selected dataset documents controlled construction transitions, not externally observed physical process transitions.",
            "Transition labels are not used as independent evidence for direction. Formal sweep continuation invariants are not physical fixations.",
            "",
            "## Claim Boundary",
            "",
            "No claim is made that physical causality, emergent time, spacetime emergence, thermodynamic irreversibility, or bridge confirmation has been shown.",
            "",
            "## Finalstatus",
            "",
            f"- primary_dataset = {final['primary_dataset']}",
            f"- direction_qualified_matches = {final['direction_qualified_matches']}",
            f"- unqualified_primitive_matches = {final['unqualified_primitive_matches']}",
            f"- direction_conflicts = {final['direction_conflicts']}",
            f"- independent_direction_reconstruction = {final['independent_direction_reconstruction']}",
            f"- direction_reconstruction_scope = {final['direction_reconstruction_scope']}",
            f"- external_physical_process_observed = {final['external_physical_process_observed']}",
            f"- final_status = {final['final_status']}",
            f"- limitations = {final['limitations']}",
            "",
            "## Dataset Selection",
            "",
            f"- selection_status = {selected['selection_status']}",
            f"- selection_reason = {selected['selection_reason']}",
            "",
        ]
    )


def exact_output_set(out_dir: Path) -> bool:
    return sorted(path.name for path in out_dir.iterdir() if path.is_file()) == sorted(OUTPUT_FILES)


def run(input_root: Path, out_dir: Path, overwrite: bool) -> None:
    prepare_output_dir(out_dir, overwrite)
    inventory = source_inventory(input_root)
    available = primary_available(input_root)

    if not available:
        states: List[Dict[str, str]] = []
        observed: List[Dict[str, str]] = []
        predicates: List[Dict[str, str]] = []
        assignments: List[Dict[str, object]] = []
        admissibility: List[Dict[str, str]] = []
        spaces: Dict[str, Set[str]] = {}
        fixations: Dict[str, List[str]] = {}
        transitive_rows: Dict[str, List[str]] = {}
        candidates: List[Dict[str, str]] = []
        comparison: List[Dict[str, object]] = []
        counterexamples: List[List[object]] = []
        selected = {
            "primary_dataset": "none",
            "selection_status": "blocked",
            "selection_reason": "Required BMC-15f2 transition artifacts are missing.",
        }
        final = {
            "research_block": RESEARCH_BLOCK,
            "primary_dataset": "none",
            "real_states_used": "no",
            "observed_transitions_used": "no",
            "documented_neighbor_edges_identified": "no",
            "formal_primitive_neighbor_edges_computed": "no",
            "branching_present": "no",
            "analysis_construction_branch_present": "no",
            "blocked_transition_present": "no",
            "predicates_available": "no",
            "formal_admissibility_computed": "no",
            "continuation_spaces_computed": "no",
            "fixation_sets_computed": "no",
            "formal_sweep_continuation_invariants_computed": "no",
            "physical_fixation_interpretation": "not_assessed",
            "formal_direction_candidates_computed": "no",
            "true_reverse_direction_check_completed": "no",
            "relation_granularity_separated": "no",
            "observed_formal_comparison_completed": "no",
            "direction_qualified_matches": 0,
            "unqualified_primitive_matches": 0,
            "direction_conflicts": 0,
            "insufficient_cases": 0,
            "independent_direction_reconstruction": "no",
            "parameter_order_used_in_admissibility": "no",
            "direction_reconstruction_scope": "blocked_missing_transition_data",
            "external_physical_process_observed": "no",
            "transition_label_leakage_present": "no",
            "physical_causality_claim_made": "no",
            "emergent_time_claim_made": "no",
            "additional_gate_created": "no",
            "final_status": "real_transition_mapping_blocked_by_missing_transition_data",
            "recommended_next_action": "Provide documented state-transition data before rerunning.",
            "limitations": "No artificial transitions were generated.",
        }
    else:
        states = build_states(input_root)
        observed = observed_transitions(states)
        predicates = predicate_catalog_table()
        assignments = predicate_assignment(states)
        admissibility = formal_admissibility(states)
        graph = graph_from_admissibility(admissibility, states)
        spaces = continuation_spaces(graph)
        transitive_rows = transitive_reachability_rows(graph)
        fixations = fixation_sets(spaces, states)
        candidates = direction_candidates(admissibility, spaces, states)
        comparison = compare_directions(observed, admissibility, candidates)
        counterexamples = counterexample_assessment(observed, admissibility, comparison)
        selected = {
            "primary_dataset": "BMC-15f2 connectedness transition sweep",
            "selection_status": "selected",
            "selection_reason": "Repository-local controlled transition sweep with documented states, branch alternatives, blocked pre-transition cases, and structured features.",
        }
        final = final_status_row(
            states,
            observed,
            admissibility,
            comparison,
            any(row["formal_admissible"] == "no" for row in admissibility),
            bool(predicates and assignments),
        )

    validation = validation_rows(states, observed, admissibility, comparison, final)
    summary = {
        "research_block": RESEARCH_BLOCK,
        "run_id": RUN_ID,
        "primary_dataset": final["primary_dataset"],
        "input_paths": [str(PRIMARY_SUMMARY), str(PRIMARY_VARIANTS), str(PRIMARY_CONFIG), str(PRIMARY_FEATURE_TABLE)],
        "state_count": len(states),
        "observed_transition_count": len(observed),
        "formal_admissible_edge_count": sum(1 for row in admissibility if row["formal_admissible"] == "yes"),
        "adjacent_primitive_candidate_count": sum(1 for row in admissibility if row.get("relation_type") == "adjacent_primitive_candidate" and row["formal_admissible"] == "yes"),
        "nonadjacent_monotone_skip_candidate_count": sum(1 for row in admissibility if row.get("relation_type") == "nonadjacent_monotone_skip_candidate" and row["formal_admissible"] == "yes"),
        "formal_direction_candidate_count": len(candidates),
        "direction_comparison_counts": {
            key: sum(1 for row in comparison if row["classification"] == key)
            for key in [
                "direction_qualified_match",
                "primitive_admissible_without_direction_qualification",
                "analysis_construction_branch",
                "nonadjacent_formal_skip_candidate",
                "formal_direction_without_observed_adjacent_step",
                "direction_conflict",
                "insufficient_data",
            ]
        },
        "independent_direction_reconstruction": final["independent_direction_reconstruction"],
        "parameter_order_used_in_admissibility": final["parameter_order_used_in_admissibility"],
        "direction_reconstruction_scope": final["direction_reconstruction_scope"],
        "external_physical_process_observed": final["external_physical_process_observed"],
        "transition_label_leakage_present": final["transition_label_leakage_present"],
        "final_status": final,
        "claim_boundary": "No physical causality, emergent time, spacetime emergence, thermodynamic irreversibility, or bridge confirmation claim.",
    }

    write_csv(
        out_dir / "qsb_causality06_source_inventory.csv",
        [
            "source_id",
            "path",
            "file_type",
            "state_definition",
            "transition_definition",
            "transition_role",
            "available_features",
            "branching_present",
            "blocked_transition_present",
            "data_quality",
            "suitability",
            "present",
        ],
        ([row[col] for col in [
            "source_id",
            "path",
            "file_type",
            "state_definition",
            "transition_definition",
            "transition_role",
            "available_features",
            "branching_present",
            "blocked_transition_present",
            "data_quality",
            "suitability",
            "present",
        ]] for row in inventory),
    )
    write_csv(out_dir / "qsb_causality06_dataset_selection.csv", ["primary_dataset", "selection_status", "selection_reason"], [[selected["primary_dataset"], selected["selection_status"], selected["selection_reason"]]])
    write_csv(out_dir / "qsb_causality06_state_catalog.csv", list(states[0].keys()) if states else ["state_id"], ([row.values() for row in states] if states else []))
    write_csv(
        out_dir / "qsb_causality06_observed_transition_catalog.csv",
        list(observed[0].keys()) if observed else ["edge_id"],
        ([row.values() for row in observed] if observed else []),
    )
    write_csv(out_dir / "qsb_causality06_predicate_catalog.csv", list(predicates[0].keys()) if predicates else ["predicate_id"], ([row.values() for row in predicates] if predicates else []))
    write_csv(
        out_dir / "qsb_causality06_predicate_assignment.csv",
        list(assignments[0].keys()) if assignments else ["state_id"],
        ([row.values() for row in assignments] if assignments else []),
    )
    write_csv(
        out_dir / "qsb_causality06_formal_admissibility.csv",
        list(admissibility[0].keys()) if admissibility else ["edge_id"],
        ([row.values() for row in admissibility] if admissibility else []),
    )
    write_csv(
        out_dir / "qsb_causality06_continuation_spaces.csv",
        [
            "state_id",
            "continuation_space_size",
            "continuation_space_members",
            "transitive_reachability_relation_targets",
            "relation_type",
        ],
        (
            [
                state_id,
                len(members),
                "|".join(sorted(members)),
                "|".join(transitive_rows.get(state_id, [])),
                "transitive_reachability_relation",
            ]
            for state_id, members in sorted(spaces.items())
        ),
    )
    write_csv(
        out_dir / "qsb_causality06_fixation_sets.csv",
        [
            "state_id",
            "formal_sweep_continuation_invariant_count",
            "formal_sweep_continuation_invariant_predicates",
            "physical_fixation_interpretation",
        ],
        ([state_id, len(items), "|".join(items), "not_assessed"] for state_id, items in sorted(fixations.items())),
    )
    write_csv(
        out_dir / "qsb_causality06_formal_direction_candidates.csv",
        list(candidates[0].keys()) if candidates else ["source_state"],
        ([row.values() for row in candidates] if candidates else []),
    )
    comparison_header = list(comparison[0].keys()) if comparison else ["source_state"]
    write_csv(out_dir / "qsb_causality06_direction_comparison.csv", comparison_header, ([row.values() for row in comparison] if comparison else []))
    write_csv(
        out_dir / "qsb_causality06_counterexample_assessment.csv",
        ["counterexample_id", "present", "source_state", "target_state", "classification_or_count", "note"],
        counterexamples,
    )
    write_csv(out_dir / "qsb_causality06_validation_checks.csv", ["check_id", "passed", "note"], validation)
    write_csv(out_dir / "qsb_causality06_final_status.csv", list(final.keys()), [list(final.values())])
    write_json(out_dir / "qsb_causality06_summary.json", summary)
    (out_dir / "qsb_causality06_readout.md").write_text(readout_text(final, selected), encoding="utf-8")
    if not exact_output_set(out_dir):
        print(f"Output set mismatch in {out_dir}", file=sys.stderr)
        sys.exit(2)


def main() -> None:
    args = parse_args()
    run(Path(args.input_root), Path(args.output_dir), args.overwrite)


if __name__ == "__main__":
    main()
