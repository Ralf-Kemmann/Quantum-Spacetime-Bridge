#!/usr/bin/env python3
"""
QSB-BRIDGE-DATA-02B carbon bonding-organization scaffold.

This script generates synthetic/reference-style scaffold tables only. It uses
no network access and downloads no external data.

Primary representation: carbon skeleton only. Hydrogen and saturation are
metadata rather than graph nodes.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_config.json"


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


def build_ethyne() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    nodes = [
        {
            "node_id": "Eth_00",
            "system_id": "ethyne",
            "atom_label": "C",
            "carbon_index": 0,
            "hybridization_label": "sp",
            "hydrogen_count_metadata": 1,
            "saturation_label": "unsaturated",
            "pi_system_label": "linear_triple_bond_pi_pair",
            "sigma_framework_label": "linear_sigma_axis",
            "x_ref": -0.5,
            "y_ref": 0.0,
            "z_ref": 0.0,
            "claim_role": "synthetic_reference_control_only",
        },
        {
            "node_id": "Eth_01",
            "system_id": "ethyne",
            "atom_label": "C",
            "carbon_index": 1,
            "hybridization_label": "sp",
            "hydrogen_count_metadata": 1,
            "saturation_label": "unsaturated",
            "pi_system_label": "linear_triple_bond_pi_pair",
            "sigma_framework_label": "linear_sigma_axis",
            "x_ref": 0.5,
            "y_ref": 0.0,
            "z_ref": 0.0,
            "claim_role": "synthetic_reference_control_only",
        },
    ]
    edges = [
        {
            "edge_id": "Eth_e_00",
            "system_id": "ethyne",
            "source": "Eth_00",
            "target": "Eth_01",
            "bond_order_class": "triple",
            "bond_order_proxy": 3.0,
            "hybridization_pair": "sp_sp",
            "pi_system_label": "linear_triple_bond_pi_pair",
            "sigma_framework_label": "linear_sigma_axis",
            "reference_control_role": "synthetic_reference_control_only",
        }
    ]
    return nodes, edges


def build_adamantane() -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    bridgeheads = {
        "Ada_00": (1.0, 1.0, 1.0),
        "Ada_01": (1.0, -1.0, -1.0),
        "Ada_02": (-1.0, 1.0, -1.0),
        "Ada_03": (-1.0, -1.0, 1.0),
    }
    bridge_pairs = [
        ("Ada_00", "Ada_01"),
        ("Ada_00", "Ada_02"),
        ("Ada_00", "Ada_03"),
        ("Ada_01", "Ada_02"),
        ("Ada_01", "Ada_03"),
        ("Ada_02", "Ada_03"),
    ]

    nodes: List[Dict[str, Any]] = []
    for idx, (node_id, coord) in enumerate(bridgeheads.items()):
        nodes.append(
            {
                "node_id": node_id,
                "system_id": "adamantane",
                "atom_label": "C",
                "carbon_index": idx,
                "hybridization_label": "sp3",
                "hydrogen_count_metadata": 1,
                "saturation_label": "saturated",
                "pi_system_label": "none",
                "sigma_framework_label": "diamondoid_sigma_cage",
                "degree_target": 3,
                "local_environment_label": "bridgehead_CH",
                "x_ref": coord[0],
                "y_ref": coord[1],
                "z_ref": coord[2],
                "claim_role": "synthetic_reference_control_only",
            }
        )

    edges: List[Dict[str, Any]] = []
    for pair_idx, (left, right) in enumerate(bridge_pairs):
        left_coord = bridgeheads[left]
        right_coord = bridgeheads[right]
        middle = (
            0.5 * (left_coord[0] + right_coord[0]),
            0.5 * (left_coord[1] + right_coord[1]),
            0.5 * (left_coord[2] + right_coord[2]),
        )
        ch2_id = f"Ada_{pair_idx + 4:02d}"
        nodes.append(
            {
                "node_id": ch2_id,
                "system_id": "adamantane",
                "atom_label": "C",
                "carbon_index": pair_idx + 4,
                "hybridization_label": "sp3",
                "hydrogen_count_metadata": 2,
                "saturation_label": "saturated",
                "pi_system_label": "none",
                "sigma_framework_label": "diamondoid_sigma_cage",
                "degree_target": 2,
                "local_environment_label": "secondary_CH2",
                "x_ref": middle[0],
                "y_ref": middle[1],
                "z_ref": middle[2],
                "claim_role": "synthetic_reference_control_only",
            }
        )
        for endpoint in [left, right]:
            edge_id = f"Ada_e_{len(edges):02d}"
            edges.append(
                {
                    "edge_id": edge_id,
                    "system_id": "adamantane",
                    "source": endpoint,
                    "target": ch2_id,
                    "bond_order_class": "single",
                    "bond_order_proxy": 1.0,
                    "hybridization_pair": "sp3_sp3",
                    "pi_system_label": "none",
                    "sigma_framework_label": "diamondoid_sigma_cage",
                    "reference_control_role": "synthetic_reference_control_only",
                }
            )
    return nodes, edges


def degree_distribution(nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]]) -> Dict[str, int]:
    degree = Counter()
    for edge in edges:
        degree[edge["source"]] += 1
        degree[edge["target"]] += 1
    return dict(sorted(Counter(str(degree[node["node_id"]]) for node in nodes).items()))


def validate_system(
    system_id: str,
    nodes: Sequence[Dict[str, Any]],
    edges: Sequence[Dict[str, Any]],
    expected: Dict[str, Any],
) -> Dict[str, Any]:
    degrees = degree_distribution(nodes, edges)
    validation = {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "degree_distribution": degrees,
        "passed": True,
    }
    validation["passed"] = (
        len(nodes) == expected["node_count"]
        and len(edges) == expected["edge_count"]
        and degrees == expected["degree_distribution"]
    )
    if "hybridization" in expected:
        hybridizations = Counter(node["hybridization_label"] for node in nodes)
        validation["hybridization_counts"] = dict(sorted(hybridizations.items()))
        validation["passed"] = validation["passed"] and set(hybridizations) == {expected["hybridization"]}
    if system_id == "ethyne":
        bond_classes = Counter(edge["bond_order_class"] for edge in edges)
        validation["bond_order_class_counts"] = dict(sorted(bond_classes.items()))
        validation["passed"] = validation["passed"] and bond_classes == Counter({expected["bond_class"]: 1})
    if system_id == "adamantane":
        pi_labels = Counter(node["pi_system_label"] for node in nodes)
        sigma_labels = Counter(node["sigma_framework_label"] for node in nodes)
        h_counts = Counter(str(node["hydrogen_count_metadata"]) for node in nodes)
        validation["pi_system_label_counts"] = dict(sorted(pi_labels.items()))
        validation["sigma_framework_label_counts"] = dict(sorted(sigma_labels.items()))
        validation["hydrogen_count_metadata_counts"] = dict(sorted(h_counts.items()))
        validation["passed"] = (
            validation["passed"]
            and pi_labels == Counter({expected["pi_system_label"]: len(nodes)})
            and sigma_labels == Counter({expected["sigma_framework_label"]: len(nodes)})
            and h_counts == Counter({"1": 4, "2": 6})
        )
    return validation


def convert_benzene_nodes(rows: Sequence[Dict[str, str]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "global_node_id": f"benzene:{row['node_id']}",
                "node_id": row["node_id"],
                "system_id": "benzene",
                "atom_label": row["atom_label"],
                "hybridization_label": "sp2",
                "hydrogen_count_metadata": 1,
                "saturation_label": "aromatic_unsaturated",
                "pi_system_label": "planar_aromatic_pi_ring",
                "sigma_framework_label": "planar_ring_sigma_framework",
                "topology_class": "planar_aromatic_ring",
                "x_ref": row["x_ref"],
                "y_ref": row["y_ref"],
                "z_ref": row["z_ref"],
                "claim_role": "synthetic_reference_control_only_from_DATA02A",
            }
        )
    return out


def convert_benzene_edges(rows: Sequence[Dict[str, str]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "global_edge_id": f"benzene:{row['edge_id']}",
                "edge_id": row["edge_id"],
                "system_id": "benzene",
                "source": row["source"],
                "target": row["target"],
                "global_source": f"benzene:{row['source']}",
                "global_target": f"benzene:{row['target']}",
                "bond_order_class": "aromatic",
                "bond_order_proxy": row["bond_order_proxy"],
                "hybridization_pair": "sp2_sp2",
                "pi_system_label": "planar_aromatic_pi_ring",
                "sigma_framework_label": "planar_ring_sigma_framework",
                "reference_control_role": "synthetic_reference_control_only_from_DATA02A",
            }
        )
    return out


def convert_c60_nodes(rows: Sequence[Dict[str, str]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "global_node_id": f"c60:{row['node_id']}",
                "node_id": row["node_id"],
                "system_id": "c60",
                "atom_label": row["atom_label"],
                "hybridization_label": "sp2",
                "hydrogen_count_metadata": 0,
                "saturation_label": "unsaturated_fullerene_sp2",
                "pi_system_label": "curved_fullerene_pi_network",
                "sigma_framework_label": "curved_fullerene_sigma_cage",
                "topology_class": "curved_fullerene_cage",
                "x_ref": row["x_ref"],
                "y_ref": row["y_ref"],
                "z_ref": row["z_ref"],
                "claim_role": "synthetic_reference_control_only_from_DATA02A",
            }
        )
    return out


def convert_c60_edges(rows: Sequence[Dict[str, str]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "global_edge_id": f"c60:{row['edge_id']}",
                "edge_id": row["edge_id"],
                "system_id": "c60",
                "source": row["source"],
                "target": row["target"],
                "global_source": f"c60:{row['source']}",
                "global_target": f"c60:{row['target']}",
                "bond_order_class": row["bond_class"],
                "bond_order_proxy": row["bond_order_proxy"],
                "hybridization_pair": "sp2_sp2",
                "pi_system_label": "curved_fullerene_pi_network",
                "sigma_framework_label": "curved_fullerene_sigma_cage",
                "reference_control_role": "synthetic_reference_control_only_from_DATA02A",
            }
        )
    return out


def local_nodes_to_ladder(rows: Sequence[Dict[str, Any]], topology_class: str) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "global_node_id": f"{row['system_id']}:{row['node_id']}",
                "node_id": row["node_id"],
                "system_id": row["system_id"],
                "atom_label": row["atom_label"],
                "hybridization_label": row["hybridization_label"],
                "hydrogen_count_metadata": row["hydrogen_count_metadata"],
                "saturation_label": row["saturation_label"],
                "pi_system_label": row["pi_system_label"],
                "sigma_framework_label": row["sigma_framework_label"],
                "topology_class": topology_class,
                "x_ref": row["x_ref"],
                "y_ref": row["y_ref"],
                "z_ref": row["z_ref"],
                "claim_role": row["claim_role"],
            }
        )
    return out


def local_edges_to_ladder(rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for row in rows:
        out.append(
            {
                "global_edge_id": f"{row['system_id']}:{row['edge_id']}",
                "edge_id": row["edge_id"],
                "system_id": row["system_id"],
                "source": row["source"],
                "target": row["target"],
                "global_source": f"{row['system_id']}:{row['source']}",
                "global_target": f"{row['system_id']}:{row['target']}",
                "bond_order_class": row["bond_order_class"],
                "bond_order_proxy": row["bond_order_proxy"],
                "hybridization_pair": row["hybridization_pair"],
                "pi_system_label": row["pi_system_label"],
                "sigma_framework_label": row["sigma_framework_label"],
                "reference_control_role": row["reference_control_role"],
            }
        )
    return out


def validate_ladder_system(nodes: Sequence[Dict[str, Any]], edges: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    systems = sorted({row["system_id"] for row in nodes})
    out: Dict[str, Any] = {}
    for system in systems:
        node_rows = [row for row in nodes if row["system_id"] == system]
        edge_rows = [row for row in edges if row["system_id"] == system]
        deg = Counter()
        for edge in edge_rows:
            deg[edge["source"]] += 1
            deg[edge["target"]] += 1
        out[system] = {
            "node_count": len(node_rows),
            "edge_count": len(edge_rows),
            "degree_distribution": dict(sorted(Counter(str(deg[node["node_id"]]) for node in node_rows).items())),
            "hybridization_counts": dict(sorted(Counter(node["hybridization_label"] for node in node_rows).items())),
            "bond_order_class_counts": dict(sorted(Counter(edge["bond_order_class"] for edge in edge_rows).items())),
            "pi_system_label_counts": dict(sorted(Counter(node["pi_system_label"] for node in node_rows).items())),
            "sigma_framework_label_counts": dict(sorted(Counter(node["sigma_framework_label"] for node in node_rows).items())),
            "topology_class_counts": dict(sorted(Counter(node["topology_class"] for node in node_rows).items())),
        }
    return out


def rows_for_counts(counter: Counter[str], field_name: str, system_id: str) -> List[Dict[str, Any]]:
    return [
        {"system_id": system_id, field_name: key, "count": value}
        for key, value in sorted(counter.items())
    ]


def build_family_summary(
    config: Dict[str, Any], validation: Dict[str, Any]
) -> List[Dict[str, Any]]:
    family_system = {
        "ethyne_linear_sp_reference": "ethyne",
        "ethyne_triple_bond_proxy": "ethyne",
        "benzene_planar_sp2_reference": "benzene",
        "benzene_aromatic_uniform_proxy": "benzene",
        "c60_curved_sp2_cage_reference": "c60",
        "c60_bond_class_environment_proxy": "c60",
        "adamantane_sp3_cage_reference": "adamantane",
        "adamantane_sigma_framework_proxy": "adamantane",
    }
    rows = []
    for family in config["families"]:
        system = family_system.get(family, "control")
        if system == "control":
            rows.append(
                {
                    "family_id": family,
                    "system_id": "control",
                    "node_count": "declared_control_family",
                    "edge_count": "declared_control_family",
                    "degree_distribution": "declared_control_family",
                    "bonding_organization_contrast_summary": "declared_control_no_null_ensemble_yet",
                    "proxy_smuggling_risk": "label_or_topology_control_must_be_instantiated_before_use",
                }
            )
        else:
            v = validation[system]
            rows.append(
                {
                    "family_id": family,
                    "system_id": system,
                    "node_count": v["node_count"],
                    "edge_count": v["edge_count"],
                    "degree_distribution": json.dumps(v["degree_distribution"], sort_keys=True),
                    "bonding_organization_contrast_summary": "method_level_carbon_skeleton_ladder_scaffold_only",
                    "proxy_smuggling_risk": "synthetic_reference_control_or_label_proxy_only",
                }
            )
    return rows


def build_hybridization_summary(validation: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for system, payload in sorted(validation.items()):
        for label, count in payload["hybridization_counts"].items():
            rows.append(
                {
                    "system_id": system,
                    "hybridization_label": label,
                    "count": count,
                    "claim_role": "synthetic_scaffold_metadata_only",
                }
            )
    return rows


def build_bond_organization_summary(validation: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for system, payload in sorted(validation.items()):
        for label, count in payload["bond_order_class_counts"].items():
            rows.append(
                {
                    "system_id": system,
                    "summary_type": "bond_order_class",
                    "label": label,
                    "count": count,
                    "claim_role": "synthetic_scaffold_metadata_only",
                }
            )
        for label, count in payload["pi_system_label_counts"].items():
            rows.append(
                {
                    "system_id": system,
                    "summary_type": "pi_system_label",
                    "label": label,
                    "count": count,
                    "claim_role": "synthetic_scaffold_metadata_only",
                }
            )
        for label, count in payload["sigma_framework_label_counts"].items():
            rows.append(
                {
                    "system_id": system,
                    "summary_type": "sigma_framework_label",
                    "label": label,
                    "count": count,
                    "claim_role": "synthetic_scaffold_metadata_only",
                }
            )
    return rows


def build_topology_summary(validation: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = []
    for system, payload in sorted(validation.items()):
        for topology, count in payload["topology_class_counts"].items():
            rows.append(
                {
                    "system_id": system,
                    "topology_class": topology,
                    "node_count": payload["node_count"],
                    "edge_count": payload["edge_count"],
                    "degree_distribution": json.dumps(payload["degree_distribution"], sort_keys=True),
                    "claim_role": "synthetic_reference_scaffold_only",
                }
            )
    return rows


def build_proxy_risk_summary(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        {
            "proxy_id": proxy["proxy_id"],
            "intended_use": proxy["intended_use"],
            "smuggling_risk": proxy["smuggling_risk"],
            "claim_boundary": proxy["claim_boundary"],
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        }
        for proxy in config["proxy_families"]
    ]


def markdown_table(headers: List[str], rows: List[Dict[str, Any]]) -> str:
    lines = [
        "|" + "|".join(headers) + "|",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        lines.append("|" + "|".join(str(row.get(header, "")).replace("\n", " ") for header in headers) + "|")
    return "\n".join(lines)


def build_readout(summary: Dict[str, Any], proxy_rows: List[Dict[str, Any]]) -> str:
    validation = summary["validation"]
    headers = ["proxy_id", "intended_use", "smuggling_risk", "claim_boundary"]
    return "\n".join(
        [
            "# QSB-BRIDGE-DATA-02B Run Readout",
            "",
            "## Run",
            "",
            "```text",
            f"block_id: {summary['block_id']}",
            f"run_id: {summary['run_id']}",
            f"stop_go_outcome: {summary['stop_go_outcome']}",
            f"external_data_downloaded: {str(summary['external_data_downloaded']).lower()}",
            "```",
            "",
            "## Claim Boundary",
            "",
            "DATA-02B is a synthetic/reference-style scaffold only.",
            "",
            "It is not real-data validation, molecular validation, or physical validation.",
            "",
            "## Representation",
            "",
            "Primary graph nodes are carbon skeleton atoms only. Hydrogen and saturation are metadata, not primary graph nodes.",
            "",
            "## System Checks",
            "",
            "```text",
            f"ethyne: {validation['ethyne']}",
            f"benzene: {validation['benzene']}",
            f"c60: {validation['c60']}",
            f"adamantane: {validation['adamantane']}",
            "```",
            "",
            "## Proxy Risk Summary",
            "",
            markdown_table(headers, proxy_rows),
            "",
            "Coordinate- and graph-derived kernels are reference/control only. Label-derived proxies are synthetic and circular if over-read.",
            "",
            "## 05C Warning Carried Forward",
            "",
            summary["qsb_bridge_num_05c_warning"],
            "",
            "## Future Result Discussion Requirement",
            "",
            "Create a separate DATA-02B result discussion only after reading these outputs. It must include a human-readable Bauchbild and remain scaffold-only, defensive, and method-level.",
            "",
        ]
    )


def main() -> None:
    config = load_json(CONFIG_PATH)
    data_dir = project_path(config["data_dir"])
    output_dir = project_path(config["output_dir"])
    sources = config["data02a_sources"]

    ethyne_nodes, ethyne_edges = build_ethyne()
    adamantane_nodes, adamantane_edges = build_adamantane()

    benzene_nodes_a = read_csv(project_path(sources["benzene_nodes"]))
    benzene_edges_a = read_csv(project_path(sources["benzene_edges"]))
    c60_nodes_a = read_csv(project_path(sources["c60_nodes"]))
    c60_edges_a = read_csv(project_path(sources["c60_edges"]))

    ladder_nodes = []
    ladder_edges = []
    ladder_nodes.extend(local_nodes_to_ladder(ethyne_nodes, "linear_sp_carbon_wire"))
    ladder_edges.extend(local_edges_to_ladder(ethyne_edges))
    ladder_nodes.extend(convert_benzene_nodes(benzene_nodes_a))
    ladder_edges.extend(convert_benzene_edges(benzene_edges_a))
    ladder_nodes.extend(convert_c60_nodes(c60_nodes_a))
    ladder_edges.extend(convert_c60_edges(c60_edges_a))
    ladder_nodes.extend(local_nodes_to_ladder(adamantane_nodes, "saturated_sp3_diamondoid_cage"))
    ladder_edges.extend(local_edges_to_ladder(adamantane_edges))

    validation = validate_ladder_system(ladder_nodes, ladder_edges)
    ethyne_validation = validate_system("ethyne", ethyne_nodes, ethyne_edges, config["expected_checks"]["ethyne"])
    adamantane_validation = validate_system(
        "adamantane", adamantane_nodes, adamantane_edges, config["expected_checks"]["adamantane"]
    )
    validation["ethyne"]["specific_checks"] = ethyne_validation
    validation["adamantane"]["specific_checks"] = adamantane_validation

    expected = config["expected_checks"]
    benzene_passed = (
        validation["benzene"]["node_count"] == expected["benzene"]["node_count"]
        and validation["benzene"]["edge_count"] == expected["benzene"]["edge_count"]
        and validation["benzene"]["degree_distribution"] == expected["benzene"]["degree_distribution"]
        and validation["benzene"]["hybridization_counts"] == {"sp2": 6}
        and validation["benzene"]["bond_order_class_counts"] == {"aromatic": 6}
    )
    c60_passed = (
        validation["c60"]["node_count"] == expected["c60"]["node_count"]
        and validation["c60"]["edge_count"] == expected["c60"]["edge_count"]
        and validation["c60"]["degree_distribution"] == expected["c60"]["degree_distribution"]
        and validation["c60"]["bond_order_class_counts"] == expected["c60"]["bond_class_counts"]
    )
    all_passed = ethyne_validation["passed"] and benzene_passed and c60_passed and adamantane_validation["passed"]
    stop_go_outcome = (
        "go_scaffold_generated_with_carbon_skeleton_checks"
        if all_passed
        else "revise_scaffold_before_use"
    )

    proxy_rows = build_proxy_risk_summary(config)
    family_rows = build_family_summary(config, validation)
    hybridization_rows = build_hybridization_summary(validation)
    bond_rows = build_bond_organization_summary(validation)
    topology_rows = build_topology_summary(validation)

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": config["claim_boundary"],
        "external_data_downloaded": False,
        "network_policy": config["network_policy"],
        "primary_representation": config["primary_representation"],
        "hydrogen_policy": config["hydrogen_policy"],
        "stop_go_outcome": stop_go_outcome,
        "no_realdata_validation_claim": True,
        "no_molecular_validation_claim": True,
        "no_physical_validation_claim": True,
        "system_count": len(validation),
        "validation": validation,
        "benzene_source": sources["benzene_nodes"],
        "c60_source": sources["c60_nodes"],
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
    }

    manifest = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": config["claim_boundary"],
        "external_data_downloaded": False,
        "primary_representation": config["primary_representation"],
        "hydrogen_policy": config["hydrogen_policy"],
        "systems": config["systems"],
        "families": config["families"],
        "proxy_families": config["proxy_families"],
        "tables": {
            "ethyne_nodes": f"{config['data_dir']}/ethyne_nodes.csv",
            "ethyne_edges": f"{config['data_dir']}/ethyne_edges.csv",
            "adamantane_nodes": f"{config['data_dir']}/adamantane_nodes.csv",
            "adamantane_edges": f"{config['data_dir']}/adamantane_edges.csv",
            "carbon_ladder_nodes": f"{config['data_dir']}/carbon_ladder_nodes.csv",
            "carbon_ladder_edges": f"{config['data_dir']}/carbon_ladder_edges.csv",
        },
        "data02a_sources": sources,
        "validation": validation,
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
    }

    write_csv(
        data_dir / "ethyne_nodes.csv",
        [
            "node_id",
            "system_id",
            "atom_label",
            "carbon_index",
            "hybridization_label",
            "hydrogen_count_metadata",
            "saturation_label",
            "pi_system_label",
            "sigma_framework_label",
            "x_ref",
            "y_ref",
            "z_ref",
            "claim_role",
        ],
        ethyne_nodes,
    )
    write_csv(
        data_dir / "ethyne_edges.csv",
        [
            "edge_id",
            "system_id",
            "source",
            "target",
            "bond_order_class",
            "bond_order_proxy",
            "hybridization_pair",
            "pi_system_label",
            "sigma_framework_label",
            "reference_control_role",
        ],
        ethyne_edges,
    )
    write_csv(
        data_dir / "adamantane_nodes.csv",
        [
            "node_id",
            "system_id",
            "atom_label",
            "carbon_index",
            "hybridization_label",
            "hydrogen_count_metadata",
            "saturation_label",
            "pi_system_label",
            "sigma_framework_label",
            "degree_target",
            "local_environment_label",
            "x_ref",
            "y_ref",
            "z_ref",
            "claim_role",
        ],
        adamantane_nodes,
    )
    write_csv(
        data_dir / "adamantane_edges.csv",
        [
            "edge_id",
            "system_id",
            "source",
            "target",
            "bond_order_class",
            "bond_order_proxy",
            "hybridization_pair",
            "pi_system_label",
            "sigma_framework_label",
            "reference_control_role",
        ],
        adamantane_edges,
    )
    write_csv(
        data_dir / "carbon_ladder_nodes.csv",
        [
            "global_node_id",
            "node_id",
            "system_id",
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
            "claim_role",
        ],
        ladder_nodes,
    )
    write_csv(
        data_dir / "carbon_ladder_edges.csv",
        [
            "global_edge_id",
            "edge_id",
            "system_id",
            "source",
            "target",
            "global_source",
            "global_target",
            "bond_order_class",
            "bond_order_proxy",
            "hybridization_pair",
            "pi_system_label",
            "sigma_framework_label",
            "reference_control_role",
        ],
        ladder_edges,
    )
    write_json(data_dir / "carbon_bonding_organization_manifest.json", manifest)

    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "resolved_config.json", config)
    write_csv(
        output_dir / "carbon_ladder_family_summary.csv",
        [
            "family_id",
            "system_id",
            "node_count",
            "edge_count",
            "degree_distribution",
            "bonding_organization_contrast_summary",
            "proxy_smuggling_risk",
        ],
        family_rows,
    )
    write_csv(
        output_dir / "hybridization_summary.csv",
        ["system_id", "hybridization_label", "count", "claim_role"],
        hybridization_rows,
    )
    write_csv(
        output_dir / "bond_organization_summary.csv",
        ["system_id", "summary_type", "label", "count", "claim_role"],
        bond_rows,
    )
    write_csv(
        output_dir / "topology_summary.csv",
        ["system_id", "topology_class", "node_count", "edge_count", "degree_distribution", "claim_role"],
        topology_rows,
    )
    write_csv(
        output_dir / "proxy_risk_summary.csv",
        ["proxy_id", "intended_use", "smuggling_risk", "claim_boundary", "qsb_bridge_num_05c_warning"],
        proxy_rows,
    )
    (output_dir / "readout.md").write_text(build_readout(summary, proxy_rows), encoding="utf-8")


if __name__ == "__main__":
    main()
