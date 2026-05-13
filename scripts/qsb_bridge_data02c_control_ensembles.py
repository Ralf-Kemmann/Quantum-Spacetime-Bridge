#!/usr/bin/env python3
"""
QSB-BRIDGE-DATA-02C control ensembles.

This script instantiates deterministic synthetic/reference-style controls for
the DATA-02B carbon bonding-organization ladder. It uses no network access and
downloads no external data.
"""

from __future__ import annotations

import csv
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/QSB-BRIDGE-DATA-02C/control_ensemble_config.json"


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: List[str], rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def group_by_system(rows: Sequence[Dict[str, str]]) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row["system_id"], []).append(row)
    return grouped


def shuffle_values(values: Sequence[str], rng: random.Random) -> List[str]:
    out = list(values)
    if len(set(out)) > 1:
        for _ in range(8):
            shuffled = list(out)
            rng.shuffle(shuffled)
            if shuffled != out:
                return shuffled
    return out


def degree_distribution(nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    degree = Counter()
    for edge in edges:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    return dict(sorted(Counter(str(degree[node["global_node_id"]]) for node in nodes).items()))


def counts(rows: Sequence[Dict[str, Any]], field: str) -> Dict[str, int]:
    return dict(sorted(Counter(str(row[field]) for row in rows).items()))


def source_signature(nodes: Sequence[Dict[str, str]], edges: Sequence[Dict[str, str]]) -> Dict[str, Any]:
    control_nodes = [{"global_node_id": row["global_node_id"]} for row in nodes]
    control_edges = [
        {
            "source": row.get("global_source", row["source"]),
            "target": row.get("global_target", row["target"]),
        }
        for row in edges
    ]
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "degree_distribution": degree_distribution(control_nodes, control_edges),
        "hybridization_counts": counts(nodes, "hybridization_label"),
        "bond_order_counts": counts(edges, "bond_order_class"),
        "topology_class_counts": counts(nodes, "topology_class"),
        "node_pi_counts": counts(nodes, "pi_system_label"),
        "node_sigma_counts": counts(nodes, "sigma_framework_label"),
        "edge_pi_counts": counts(edges, "pi_system_label"),
        "edge_sigma_counts": counts(edges, "sigma_framework_label"),
    }


def prefixed_node(control_id: str, family_id: str, source_system: str, row: Dict[str, str]) -> Dict[str, Any]:
    return {
        "control_id": control_id,
        "control_family_id": family_id,
        "source_system_id": source_system,
        "global_node_id": f"{control_id}:{row['node_id']}",
        "source_global_node_id": row["global_node_id"],
        "node_id": row["node_id"],
        "atom_label": row["atom_label"],
        "hybridization_label": row["hybridization_label"],
        "hydrogen_count_metadata": row["hydrogen_count_metadata"],
        "saturation_label": row["saturation_label"],
        "pi_system_label": row["pi_system_label"],
        "sigma_framework_label": row["sigma_framework_label"],
        "topology_class": row["topology_class"],
        "x_ref": row["x_ref"],
        "y_ref": row["y_ref"],
        "z_ref": row["z_ref"],
        "control_transform_note": "source scaffold copied before control transform",
        "claim_role": "synthetic_control_only",
    }


def prefixed_edge(
    control_id: str, family_id: str, source_system: str, row: Dict[str, str], source: str, target: str
) -> Dict[str, Any]:
    return {
        "control_id": control_id,
        "control_family_id": family_id,
        "source_system_id": source_system,
        "global_edge_id": f"{control_id}:{row['edge_id']}",
        "source_global_edge_id": row["global_edge_id"],
        "source": source,
        "target": target,
        "source_original": row["global_source"],
        "target_original": row["global_target"],
        "bond_order_class": row["bond_order_class"],
        "bond_order_proxy": row["bond_order_proxy"],
        "hybridization_pair": row["hybridization_pair"],
        "pi_system_label": row["pi_system_label"],
        "sigma_framework_label": row["sigma_framework_label"],
        "control_transform_note": "source scaffold copied before control transform",
        "reference_control_role": "synthetic_control_only",
    }


def make_base_control(
    control_id: str,
    family_id: str,
    system: str,
    nodes: Sequence[Dict[str, str]],
    edges: Sequence[Dict[str, str]],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    node_rows = [prefixed_node(control_id, family_id, system, row) for row in nodes]
    node_map = {row["source_global_node_id"]: row["global_node_id"] for row in node_rows}
    edge_rows = [
        prefixed_edge(control_id, family_id, system, row, node_map[row["global_source"]], node_map[row["global_target"]])
        for row in edges
    ]
    return node_rows, edge_rows


def random_edge_pairs(node_ids: Sequence[str], edge_count: int, rng: random.Random) -> List[Tuple[str, str]]:
    possible = [(a, b) for idx, a in enumerate(node_ids) for b in node_ids[idx + 1 :]]
    if edge_count > len(possible):
        return []
    rng.shuffle(possible)
    return sorted(possible[:edge_count])


def degree_preserving_pairs(
    node_ids: Sequence[str], original_edges: Sequence[Tuple[str, str]], rng: random.Random
) -> List[Tuple[str, str]]:
    edges = {tuple(sorted(edge)) for edge in original_edges}
    if len(edges) < 2:
        return sorted(edges)
    for _ in range(500):
        e1, e2 = rng.sample(sorted(edges), 2)
        a, b = e1
        c, d = e2
        if len({a, b, c, d}) < 4:
            continue
        if rng.random() < 0.5:
            n1, n2 = tuple(sorted((a, c))), tuple(sorted((b, d)))
        else:
            n1, n2 = tuple(sorted((a, d))), tuple(sorted((b, c)))
        if n1[0] == n1[1] or n2[0] == n2[1] or n1 in edges or n2 in edges or n1 == n2:
            continue
        edges.remove(e1)
        edges.remove(e2)
        edges.add(n1)
        edges.add(n2)
    return sorted(edges)


def apply_control_transform(
    family_id: str,
    control_id: str,
    system: str,
    nodes: Sequence[Dict[str, str]],
    edges: Sequence[Dict[str, str]],
    all_nodes: Sequence[Dict[str, str]],
    all_edges: Sequence[Dict[str, str]],
    next_system_nodes: Sequence[Dict[str, str]],
    next_system_edges: Sequence[Dict[str, str]],
    rng: random.Random,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    out_nodes, out_edges = make_base_control(control_id, family_id, system, nodes, edges)
    note = family_id

    if family_id == "hybridization_label_shuffle_control":
        labels = shuffle_values([row["hybridization_label"] for row in all_nodes], rng)
        for idx, row in enumerate(out_nodes):
            row["hybridization_label"] = labels[idx % len(labels)]
            row["control_transform_note"] = "hybridization labels drawn from deterministic global shuffle"

    elif family_id == "bond_order_shuffle_control":
        labels = shuffle_values([row["bond_order_class"] for row in all_edges], rng)
        for idx, row in enumerate(out_edges):
            row["bond_order_class"] = labels[idx % len(labels)]
            row["control_transform_note"] = "bond-order labels drawn from deterministic global shuffle"

    elif family_id == "sigma_pi_label_shuffle_control":
        node_pi = shuffle_values([row["pi_system_label"] for row in all_nodes], rng)
        node_sigma = shuffle_values([row["sigma_framework_label"] for row in all_nodes], rng)
        edge_pi = shuffle_values([row["pi_system_label"] for row in all_edges], rng)
        edge_sigma = shuffle_values([row["sigma_framework_label"] for row in all_edges], rng)
        for idx, row in enumerate(out_nodes):
            row["pi_system_label"] = node_pi[idx % len(node_pi)]
            row["sigma_framework_label"] = node_sigma[idx % len(node_sigma)]
            row["control_transform_note"] = "sigma/pi node labels drawn from deterministic global shuffle"
        for idx, row in enumerate(out_edges):
            row["pi_system_label"] = edge_pi[idx % len(edge_pi)]
            row["sigma_framework_label"] = edge_sigma[idx % len(edge_sigma)]
            row["control_transform_note"] = "sigma/pi edge labels drawn from deterministic global shuffle"

    elif family_id == "topology_matched_random_control":
        node_ids = [row["global_node_id"] for row in out_nodes]
        pairs = random_edge_pairs(node_ids, len(out_edges), rng)
        for row in out_nodes:
            row["topology_class"] = "topology_matched_random_control"
            row["control_transform_note"] = "node labels retained but topology class marked randomized"
        for idx, row in enumerate(out_edges):
            if pairs:
                row["source"], row["target"] = pairs[idx]
            row["global_edge_id"] = f"{control_id}:rand_e_{idx:04d}"
            row["source_original"] = row["source_original"]
            row["target_original"] = row["target_original"]
            row["control_transform_note"] = "edge endpoints randomized with node and edge counts preserved"

    elif family_id == "carbon_skeleton_degree_control":
        original_pairs = [(row["source"], row["target"]) for row in out_edges]
        pairs = degree_preserving_pairs([row["global_node_id"] for row in out_nodes], original_pairs, rng)
        for row in out_nodes:
            row["topology_class"] = "degree_preserving_randomized_topology"
            row["control_transform_note"] = "degree sequence target preserved; topology class marked randomized"
        for idx, row in enumerate(out_edges):
            row["source"], row["target"] = pairs[idx]
            row["global_edge_id"] = f"{control_id}:deg_e_{idx:04d}"
            row["control_transform_note"] = "edge endpoints degree-preserving rewired where possible"

    elif family_id == "within_system_label_shuffle":
        h = shuffle_values([row["hybridization_label"] for row in out_nodes], rng)
        pi = shuffle_values([row["pi_system_label"] for row in out_nodes], rng)
        sigma = shuffle_values([row["sigma_framework_label"] for row in out_nodes], rng)
        bonds = shuffle_values([row["bond_order_class"] for row in out_edges], rng)
        for idx, row in enumerate(out_nodes):
            row["hybridization_label"] = h[idx % len(h)]
            row["pi_system_label"] = pi[idx % len(pi)]
            row["sigma_framework_label"] = sigma[idx % len(sigma)]
            row["control_transform_note"] = "within-system node labels shuffled"
        for idx, row in enumerate(out_edges):
            row["bond_order_class"] = bonds[idx % len(bonds)]
            row["control_transform_note"] = "within-system bond labels shuffled"

    elif family_id == "cross_system_label_swap":
        for idx, row in enumerate(out_nodes):
            donor = next_system_nodes[idx % len(next_system_nodes)]
            row["hybridization_label"] = donor["hybridization_label"]
            row["hydrogen_count_metadata"] = donor["hydrogen_count_metadata"]
            row["saturation_label"] = donor["saturation_label"]
            row["pi_system_label"] = donor["pi_system_label"]
            row["sigma_framework_label"] = donor["sigma_framework_label"]
            row["control_transform_note"] = "node labels swapped from next source system"
        for idx, row in enumerate(out_edges):
            donor = next_system_edges[idx % len(next_system_edges)]
            row["bond_order_class"] = donor["bond_order_class"]
            row["bond_order_proxy"] = donor["bond_order_proxy"]
            row["hybridization_pair"] = donor["hybridization_pair"]
            row["pi_system_label"] = donor["pi_system_label"]
            row["sigma_framework_label"] = donor["sigma_framework_label"]
            row["control_transform_note"] = "edge labels swapped from next source system"

    elif family_id == "topology_preserving_label_randomization":
        node_hybrid = [row["hybridization_label"] for row in all_nodes]
        node_pi = [row["pi_system_label"] for row in all_nodes]
        node_sigma = [row["sigma_framework_label"] for row in all_nodes]
        edge_bond = [row["bond_order_class"] for row in all_edges]
        for row in out_nodes:
            row["hybridization_label"] = rng.choice(node_hybrid)
            row["pi_system_label"] = rng.choice(node_pi)
            row["sigma_framework_label"] = rng.choice(node_sigma)
            row["control_transform_note"] = "topology preserved; labels randomized from global scaffold pools"
        for row in out_edges:
            row["bond_order_class"] = rng.choice(edge_bond)
            row["control_transform_note"] = "topology preserved; edge labels randomized from global scaffold pools"

    else:
        for row in out_nodes:
            row["control_transform_note"] = note
        for row in out_edges:
            row["control_transform_note"] = note

    return out_nodes, out_edges


def exact_node_match_fraction(source_nodes: Sequence[Dict[str, str]], control_nodes: Sequence[Dict[str, Any]], fields: Sequence[str]) -> float:
    source_by_id = {row["global_node_id"]: row for row in source_nodes}
    if not control_nodes:
        return 0.0
    total = 0
    same = 0
    for row in control_nodes:
        src = source_by_id.get(row["source_global_node_id"])
        if src is None:
            continue
        for field in fields:
            total += 1
            if str(row[field]) == str(src[field]):
                same += 1
    return same / total if total else 0.0


def exact_edge_match_fraction(source_edges: Sequence[Dict[str, str]], control_edges: Sequence[Dict[str, Any]], fields: Sequence[str]) -> float:
    source_by_id = {row["global_edge_id"]: row for row in source_edges}
    if not control_edges:
        return 0.0
    total = 0
    same = 0
    for row in control_edges:
        src = source_by_id.get(row["source_global_edge_id"])
        if src is None:
            continue
        for field in fields:
            total += 1
            if str(row[field]) == str(src[field]):
                same += 1
    return same / total if total else 0.0


def validate_control(
    control_id: str,
    family_id: str,
    system: str,
    source_nodes: Sequence[Dict[str, str]],
    source_edges: Sequence[Dict[str, str]],
    control_nodes: Sequence[Dict[str, Any]],
    control_edges: Sequence[Dict[str, Any]],
    family_meta: Dict[str, str],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    source_sig = source_signature(source_nodes, source_edges)
    control_sig = source_signature(control_nodes, control_edges)
    node_count_preserved = source_sig["node_count"] == control_sig["node_count"]
    edge_count_preserved = source_sig["edge_count"] == control_sig["edge_count"]
    degree_preserved = source_sig["degree_distribution"] == control_sig["degree_distribution"]
    hybrid_counts_preserved = source_sig["hybridization_counts"] == control_sig["hybridization_counts"]
    bond_counts_preserved = source_sig["bond_order_counts"] == control_sig["bond_order_counts"]
    topology_preserved = source_sig["topology_class_counts"] == control_sig["topology_class_counts"]
    sigma_pi_preserved = (
        source_sig["node_pi_counts"] == control_sig["node_pi_counts"]
        and source_sig["node_sigma_counts"] == control_sig["node_sigma_counts"]
        and source_sig["edge_pi_counts"] == control_sig["edge_pi_counts"]
        and source_sig["edge_sigma_counts"] == control_sig["edge_sigma_counts"]
    )

    topology_component = 1.0 if degree_preserved and topology_preserved else (0.5 if node_count_preserved and edge_count_preserved else 0.0)
    hybridization_component = exact_node_match_fraction(source_nodes, control_nodes, ["hybridization_label"])
    bond_order_component = exact_edge_match_fraction(source_edges, control_edges, ["bond_order_class"])
    sigma_node = exact_node_match_fraction(source_nodes, control_nodes, ["pi_system_label", "sigma_framework_label"])
    sigma_edge = exact_edge_match_fraction(source_edges, control_edges, ["pi_system_label", "sigma_framework_label"])
    sigma_pi_component = (sigma_node + sigma_edge) / 2.0
    score = round((topology_component + hybridization_component + bond_order_component + sigma_pi_component) / 4.0, 6)
    contrast = round(1.0 - score, 6)

    negative = score >= 0.85
    if family_id in {"hybridization_label_shuffle_control", "within_system_label_shuffle"} and hybridization_component >= 0.99:
        negative = True
    if family_id in {"bond_order_shuffle_control", "within_system_label_shuffle"} and bond_order_component >= 0.99:
        negative = True
    if family_id == "carbon_skeleton_degree_control" and topology_component >= 0.99:
        negative = True

    label_risk = "high" if family_id in {
        "hybridization_label_shuffle_control",
        "bond_order_shuffle_control",
        "sigma_pi_label_shuffle_control",
        "within_system_label_shuffle",
        "cross_system_label_swap",
        "topology_preserving_label_randomization",
    } else "medium"
    boundary = (
        "possible negative finding: control may mimic or preserve organization too easily"
        if negative
        else family_meta["interpretation_boundary"]
    )

    validation = {
        "control_id": control_id,
        "source_system_id": system,
        "control_family_id": family_id,
        "node_count_preserved": node_count_preserved,
        "edge_count_preserved": edge_count_preserved,
        "degree_distribution_preserved": degree_preserved,
        "hybridization_counts_preserved": hybrid_counts_preserved,
        "bond_order_counts_preserved": bond_counts_preserved,
        "topology_class_preserved": topology_preserved,
        "sigma_pi_labels_preserved": sigma_pi_preserved,
        "organization_coherence_score": score,
        "label_smuggling_risk": label_risk,
        "control_interpretation_boundary": boundary,
    }
    coherence = {
        "control_id": control_id,
        "source_system_id": system,
        "control_family_id": family_id,
        "topology_component": round(topology_component, 6),
        "hybridization_component": round(hybridization_component, 6),
        "bond_order_component": round(bond_order_component, 6),
        "sigma_pi_component": round(sigma_pi_component, 6),
        "organization_coherence_score": score,
        "original_control_coherence_contrast": contrast,
        "negative_finding_flag": negative,
        "highest_risk_mimic_control": False,
        "lowest_original_control_coherence_contrast": False,
        "notes": boundary,
    }
    return validation, coherence


def family_summary_rows(config: Dict[str, Any], systems: Sequence[str]) -> List[Dict[str, Any]]:
    return [
        {
            "control_family_id": family["control_family_id"],
            "control_distinction": family["control_distinction"],
            "control_count": len(systems),
            "systems_included": ";".join(systems),
            "preservation_target": family["preservation_target"],
            "destruction_target": family["destruction_target"],
            "interpretation_boundary": family["interpretation_boundary"],
        }
        for family in config["control_families"]
    ]


def proxy_risk_rows(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    risks = [
        ("hybridization_label_shuffle_control", "label_smuggling", "high", "Label recognition is not organization recognition."),
        ("bond_order_shuffle_control", "bond_label_circularity", "high", "Bond labels can encode the target distinction."),
        ("sigma_pi_label_shuffle_control", "sigma_pi_label_circularity", "high", "Sigma/pi labels are metadata, not independent evidence."),
        ("topology_matched_random_control", "topology_circularity", "medium", "Random topology controls are scaffold controls, not molecular alternatives."),
        ("carbon_skeleton_degree_control", "degree_only_mimicry", "high", "Degree preservation can mimic local organization."),
        ("coordinate_distance_reference_kernel", "reference_control_only", "high", "Coordinate-derived channels are not independent evidence."),
        ("graph_distance_reference_kernel", "reference_control_only", "high", "Graph-derived channels are not independent evidence."),
    ]
    return [
        {
            "proxy_or_control_id": rid,
            "risk_type": risk_type,
            "risk_level": level,
            "interpretation_boundary": boundary,
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        }
        for rid, risk_type, level, boundary in risks
    ]


def bool_text(value: Any) -> str:
    return str(bool(value)).lower()


def mark_global_findings(coherence_rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not coherence_rows:
        return {
            "highest_risk_mimic_control": None,
            "lowest_original_control_coherence_contrast": None,
            "possible_negative_finding_present": False,
        }
    highest = max(coherence_rows, key=lambda row: (row["organization_coherence_score"], -row["original_control_coherence_contrast"], row["control_id"]))
    lowest = min(coherence_rows, key=lambda row: (row["original_control_coherence_contrast"], -row["organization_coherence_score"], row["control_id"]))
    for row in coherence_rows:
        row["highest_risk_mimic_control"] = row["control_id"] == highest["control_id"]
        row["lowest_original_control_coherence_contrast"] = row["control_id"] == lowest["control_id"]
    return {
        "highest_risk_mimic_control": {
            "control_id": highest["control_id"],
            "source_system_id": highest["source_system_id"],
            "control_family_id": highest["control_family_id"],
            "organization_coherence_score": highest["organization_coherence_score"],
            "original_control_coherence_contrast": highest["original_control_coherence_contrast"],
        },
        "lowest_original_control_coherence_contrast": {
            "control_id": lowest["control_id"],
            "source_system_id": lowest["source_system_id"],
            "control_family_id": lowest["control_family_id"],
            "organization_coherence_score": lowest["organization_coherence_score"],
            "original_control_coherence_contrast": lowest["original_control_coherence_contrast"],
        },
        "possible_negative_finding_present": any(bool(row["negative_finding_flag"]) for row in coherence_rows),
    }


def markdown_table(headers: List[str], rows: List[Dict[str, Any]]) -> str:
    lines = ["|" + "|".join(headers) + "|", "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("|" + "|".join(str(row.get(header, "")).replace("\n", " ") for header in headers) + "|")
    return "\n".join(lines)


def build_readout(summary: Dict[str, Any]) -> str:
    mimic = summary["highest_risk_mimic_control"]
    lowest = summary["lowest_original_control_coherence_contrast"]
    return "\n".join(
        [
            "# QSB-BRIDGE-DATA-02C Run Readout",
            "",
            "## Run",
            "",
            "```text",
            f"block_id: {summary['block_id']}",
            f"run_id: {summary['run_id']}",
            f"fixed_seed: {summary['fixed_seed']}",
            f"stop_go_outcome: {summary['stop_go_outcome']}",
            f"external_data_downloaded: {str(summary['external_data_downloaded']).lower()}",
            f"control_count: {summary['control_count']}",
            "```",
            "",
            "## Claim Boundary",
            "",
            "DATA-02C is a synthetic/reference-style control ensemble only.",
            "",
            "It is not real-data validation, molecular validation, or physical validation.",
            "",
            "## Highest-Risk Mimic Control",
            "",
            "```text",
            f"highest_risk_mimic_control: {mimic}",
            f"lowest_original_control_coherence_contrast: {lowest}",
            f"possible_negative_finding_present: {summary['possible_negative_finding_present']}",
            "```",
            "",
            "Successful controls are treated as possible negative findings if they mimic or erase the original organization too easily.",
            "",
            "## Control Families",
            "",
            markdown_table(
                ["control_family_id", "control_count", "control_distinction", "destruction_target"],
                summary["control_family_summary_preview"],
            ),
            "",
            "## 05C Warning Carried Forward",
            "",
            summary["qsb_bridge_num_05c_warning"],
            "",
            "## Future Result Discussion Requirement",
            "",
            summary["future_result_discussion_requirement"],
            "",
        ]
    )


def main() -> None:
    config = load_json(CONFIG_PATH)
    fixed_seed = int(config["fixed_seed"])
    inputs = config["input_dependencies"]
    nodes = read_csv(project_path(inputs["carbon_ladder_nodes"]))
    edges = read_csv(project_path(inputs["carbon_ladder_edges"]))
    manifest = load_json(project_path(inputs["carbon_bonding_organization_manifest"]))
    data_dir = project_path(config["data_dir"])
    output_dir = project_path(config["output_dir"])

    nodes_by_system = group_by_system(nodes)
    edges_by_system = group_by_system(edges)
    systems = sorted(nodes_by_system)
    all_control_nodes: List[Dict[str, Any]] = []
    all_control_edges: List[Dict[str, Any]] = []
    validation_rows: List[Dict[str, Any]] = []
    coherence_rows: List[Dict[str, Any]] = []

    family_by_id = {family["control_family_id"]: family for family in config["control_families"]}
    for family_idx, family in enumerate(config["control_families"]):
        family_id = family["control_family_id"]
        for system_idx, system in enumerate(systems):
            control_id = f"{family_id}__{system}"
            rng = random.Random(fixed_seed + 1000 * family_idx + system_idx)
            next_system = systems[(system_idx + 1) % len(systems)]
            cnodes, cedges = apply_control_transform(
                family_id,
                control_id,
                system,
                nodes_by_system[system],
                edges_by_system[system],
                nodes,
                edges,
                nodes_by_system[next_system],
                edges_by_system[next_system],
                rng,
            )
            validation, coherence = validate_control(
                control_id,
                family_id,
                system,
                nodes_by_system[system],
                edges_by_system[system],
                cnodes,
                cedges,
                family_by_id[family_id],
            )
            all_control_nodes.extend(cnodes)
            all_control_edges.extend(cedges)
            validation_rows.append(validation)
            coherence_rows.append(coherence)

    global_findings = mark_global_findings(coherence_rows)
    family_rows = family_summary_rows(config, systems)
    risk_rows = proxy_risk_rows(config)
    control_count = len(validation_rows)

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": config["claim_boundary"],
        "external_data_downloaded": False,
        "network_policy": config["network_policy"],
        "fixed_seed": fixed_seed,
        "input_dependencies": inputs,
        "source_manifest_block_id": manifest.get("block_id", ""),
        "control_count": control_count,
        "control_family_count": len(config["control_families"]),
        "source_system_count": len(systems),
        "source_systems": systems,
        "stop_go_outcome": "go_control_ensembles_generated_with_deterministic_seed",
        "no_realdata_validation_claim": True,
        "no_molecular_validation_claim": True,
        "no_physical_validation_claim": True,
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
        "highest_risk_mimic_control": global_findings["highest_risk_mimic_control"],
        "lowest_original_control_coherence_contrast": global_findings["lowest_original_control_coherence_contrast"],
        "possible_negative_finding_present": global_findings["possible_negative_finding_present"],
        "control_family_summary_preview": family_rows,
    }
    ensemble_manifest = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": config["claim_boundary"],
        "external_data_downloaded": False,
        "fixed_seed": fixed_seed,
        "input_dependencies": inputs,
        "control_families": config["control_families"],
        "control_count": control_count,
        "systems": systems,
        "tables": {
            "control_nodes": f"{config['data_dir']}/control_nodes.csv",
            "control_edges": f"{config['data_dir']}/control_edges.csv",
            "control_family_summary": f"{config['data_dir']}/control_family_summary.csv",
            "control_validation_summary": f"{config['data_dir']}/control_validation_summary.csv",
        },
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
        "highest_risk_mimic_control": global_findings["highest_risk_mimic_control"],
        "lowest_original_control_coherence_contrast": global_findings["lowest_original_control_coherence_contrast"],
        "possible_negative_finding_present": global_findings["possible_negative_finding_present"],
    }

    node_fields = [
        "control_id",
        "control_family_id",
        "source_system_id",
        "global_node_id",
        "source_global_node_id",
        "node_id",
        "atom_label",
        "hybridization_label",
        "hydrogen_count_metadata",
        "saturation_label",
        "pi_system_label",
        "sigma_framework_label",
        "topology_class",
        "x_ref",
        "y_ref",
        "z_ref",
        "control_transform_note",
        "claim_role",
    ]
    edge_fields = [
        "control_id",
        "control_family_id",
        "source_system_id",
        "global_edge_id",
        "source_global_edge_id",
        "source",
        "target",
        "source_original",
        "target_original",
        "bond_order_class",
        "bond_order_proxy",
        "hybridization_pair",
        "pi_system_label",
        "sigma_framework_label",
        "control_transform_note",
        "reference_control_role",
    ]
    family_fields = [
        "control_family_id",
        "control_distinction",
        "control_count",
        "systems_included",
        "preservation_target",
        "destruction_target",
        "interpretation_boundary",
    ]
    validation_fields = [
        "control_id",
        "source_system_id",
        "control_family_id",
        "node_count_preserved",
        "edge_count_preserved",
        "degree_distribution_preserved",
        "hybridization_counts_preserved",
        "bond_order_counts_preserved",
        "topology_class_preserved",
        "sigma_pi_labels_preserved",
        "organization_coherence_score",
        "label_smuggling_risk",
        "control_interpretation_boundary",
    ]
    coherence_fields = [
        "control_id",
        "source_system_id",
        "control_family_id",
        "topology_component",
        "hybridization_component",
        "bond_order_component",
        "sigma_pi_component",
        "organization_coherence_score",
        "original_control_coherence_contrast",
        "negative_finding_flag",
        "highest_risk_mimic_control",
        "lowest_original_control_coherence_contrast",
        "notes",
    ]
    risk_fields = [
        "proxy_or_control_id",
        "risk_type",
        "risk_level",
        "interpretation_boundary",
        "qsb_bridge_num_05c_warning",
    ]

    write_json(data_dir / "control_ensemble_manifest.json", ensemble_manifest)
    write_csv(data_dir / "control_nodes.csv", node_fields, all_control_nodes)
    write_csv(data_dir / "control_edges.csv", edge_fields, all_control_edges)
    write_csv(data_dir / "control_family_summary.csv", family_fields, family_rows)
    write_csv(data_dir / "control_validation_summary.csv", validation_fields, validation_rows)

    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "resolved_config.json", config)
    write_csv(output_dir / "control_family_summary.csv", family_fields, family_rows)
    write_csv(output_dir / "control_validation_summary.csv", validation_fields, validation_rows)
    write_csv(output_dir / "organization_coherence_summary.csv", coherence_fields, coherence_rows)
    write_csv(output_dir / "proxy_risk_summary.csv", risk_fields, risk_rows)
    (output_dir / "readout.md").write_text(build_readout(summary), encoding="utf-8")


if __name__ == "__main__":
    main()
