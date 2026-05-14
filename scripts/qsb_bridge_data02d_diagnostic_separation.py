#!/usr/bin/env python3
"""
QSB-BRIDGE-DATA-02D diagnostic separation.

This runner computes deterministic synthetic/reference-style scaffold
diagnostics for DATA-02B originals and DATA-02C controls. It uses local inputs
only, does not use coordinates, and makes no real-data, molecular, physical, or
spacetime-emergence validation claim.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/QSB-BRIDGE-DATA-02D/diagnostic_separation_config.json"


SIGNAL_SOURCES = {
    "topology_signature_diagnostic": "topology-derived signal",
    "degree_distribution_diagnostic": "degree-derived signal",
    "bond_order_distribution_diagnostic": "bond-order-derived signal",
    "hybridization_distribution_diagnostic": "label-derived signal",
    "sigma_pi_organization_diagnostic": "sigma/pi-derived signal",
    "local_environment_consistency_diagnostic": "combined scaffold signal",
    "combined_bonding_organization_score": "combined scaffold signal",
}

CLAIM_BOUNDARY = (
    "synthetic scaffold diagnostic only; not real-data validation, molecular validation, "
    "physical validation, spacetime emergence, or proof of electronic-configuration recognition"
)


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: List[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def group_rows(rows: Sequence[Dict[str, str]], field: str) -> Dict[str, List[Dict[str, str]]]:
    grouped: Dict[str, List[Dict[str, str]]] = {}
    for row in rows:
        grouped.setdefault(row[field], []).append(row)
    return dict(sorted(grouped.items()))


def count_values(rows: Sequence[Mapping[str, str]], field: str) -> Dict[str, int]:
    return dict(sorted(Counter(str(row.get(field, "")) for row in rows).items()))


def normalized_similarity(left: Mapping[str, int], right: Mapping[str, int]) -> float:
    left_total = sum(left.values())
    right_total = sum(right.values())
    if left_total == 0 and right_total == 0:
        return 1.0
    keys = set(left) | set(right)
    distance = sum(abs(left.get(key, 0) / max(left_total, 1) - right.get(key, 0) / max(right_total, 1)) for key in keys)
    return round(max(0.0, 1.0 - 0.5 * distance), 6)


def bool_similarity(left: Any, right: Any) -> float:
    return 1.0 if left == right else 0.0


def node_key(row: Mapping[str, str]) -> str:
    return row.get("global_node_id") or row.get("source_global_node_id") or row.get("node_id", "")


def edge_endpoints(edge: Mapping[str, str], prefer_original: bool = False) -> Tuple[str, str]:
    if prefer_original and edge.get("source_original") and edge.get("target_original"):
        return tuple(sorted((edge["source_original"], edge["target_original"])))
    source = edge.get("global_source") or edge.get("source")
    target = edge.get("global_target") or edge.get("target")
    return tuple(sorted((str(source), str(target))))


def degree_distribution(nodes: Sequence[Mapping[str, str]], edges: Sequence[Mapping[str, str]], prefer_original: bool) -> Dict[str, int]:
    degree = Counter()
    for edge in edges:
        source, target = edge_endpoints(edge, prefer_original=prefer_original)
        degree[source] += 1
        degree[target] += 1
    counts = Counter()
    for node in nodes:
        key = node.get("source_global_node_id") if prefer_original else node_key(node)
        counts[str(degree[str(key)])] += 1
    return dict(sorted(counts.items()))


def edge_set(edges: Sequence[Mapping[str, str]], prefer_original: bool) -> set[Tuple[str, str]]:
    return {edge_endpoints(edge, prefer_original=prefer_original) for edge in edges}


def jaccard_similarity(left: set[Tuple[str, str]], right: set[Tuple[str, str]]) -> float:
    if not left and not right:
        return 1.0
    return round(len(left & right) / len(left | right), 6)


def incident_bond_counts(nodes: Sequence[Mapping[str, str]], edges: Sequence[Mapping[str, str]], prefer_original: bool) -> Dict[str, Counter[str]]:
    by_node: Dict[str, Counter[str]] = {str(node.get("source_global_node_id") if prefer_original else node_key(node)): Counter() for node in nodes}
    for edge in edges:
        source, target = edge_endpoints(edge, prefer_original=prefer_original)
        label = str(edge.get("bond_order_class", ""))
        by_node.setdefault(source, Counter())[label] += 1
        by_node.setdefault(target, Counter())[label] += 1
    return by_node


def local_environment_distribution(
    nodes: Sequence[Mapping[str, str]], edges: Sequence[Mapping[str, str]], prefer_original: bool
) -> Dict[str, int]:
    degree_counts = Counter()
    for edge in edges:
        source, target = edge_endpoints(edge, prefer_original=prefer_original)
        degree_counts[source] += 1
        degree_counts[target] += 1
    incident = incident_bond_counts(nodes, edges, prefer_original=prefer_original)
    env = Counter()
    for node in nodes:
        key = str(node.get("source_global_node_id") if prefer_original else node_key(node))
        bond_sig = ";".join(f"{label}:{count}" for label, count in sorted(incident.get(key, {}).items()))
        env_key = "|".join(
            [
                f"degree={degree_counts[key]}",
                f"hybridization={node.get('hybridization_label', '')}",
                f"topology={node.get('topology_class', '')}",
                f"pi={node.get('pi_system_label', '')}",
                f"sigma={node.get('sigma_framework_label', '')}",
                f"bonds={bond_sig}",
            ]
        )
        env[env_key] += 1
    return dict(sorted(env.items()))


def signature(nodes: Sequence[Mapping[str, str]], edges: Sequence[Mapping[str, str]], prefer_original: bool = False) -> Dict[str, Any]:
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "degree_distribution": degree_distribution(nodes, edges, prefer_original=prefer_original),
        "topology_class_counts": count_values(nodes, "topology_class"),
        "bond_order_counts": count_values(edges, "bond_order_class"),
        "hybridization_counts": count_values(nodes, "hybridization_label"),
        "node_pi_counts": count_values(nodes, "pi_system_label"),
        "node_sigma_counts": count_values(nodes, "sigma_framework_label"),
        "edge_pi_counts": count_values(edges, "pi_system_label"),
        "edge_sigma_counts": count_values(edges, "sigma_framework_label"),
        "edge_set": edge_set(edges, prefer_original=prefer_original),
        "local_environment_counts": local_environment_distribution(nodes, edges, prefer_original=prefer_original),
    }


def component_scores(original: Mapping[str, Any], candidate: Mapping[str, Any]) -> Dict[str, float]:
    count_gate = 0.5 * bool_similarity(original["node_count"], candidate["node_count"]) + 0.5 * bool_similarity(
        original["edge_count"], candidate["edge_count"]
    )
    topology = 0.45 * jaccard_similarity(original["edge_set"], candidate["edge_set"]) + 0.35 * normalized_similarity(
        original["topology_class_counts"], candidate["topology_class_counts"]
    ) + 0.20 * count_gate
    sigma_pi_parts = [
        normalized_similarity(original["node_pi_counts"], candidate["node_pi_counts"]),
        normalized_similarity(original["node_sigma_counts"], candidate["node_sigma_counts"]),
        normalized_similarity(original["edge_pi_counts"], candidate["edge_pi_counts"]),
        normalized_similarity(original["edge_sigma_counts"], candidate["edge_sigma_counts"]),
    ]
    return {
        "topology_signature_diagnostic": round(topology, 6),
        "degree_distribution_diagnostic": normalized_similarity(
            original["degree_distribution"], candidate["degree_distribution"]
        ),
        "bond_order_distribution_diagnostic": normalized_similarity(original["bond_order_counts"], candidate["bond_order_counts"]),
        "hybridization_distribution_diagnostic": normalized_similarity(
            original["hybridization_counts"], candidate["hybridization_counts"]
        ),
        "sigma_pi_organization_diagnostic": round(sum(sigma_pi_parts) / len(sigma_pi_parts), 6),
        "local_environment_consistency_diagnostic": normalized_similarity(
            original["local_environment_counts"], candidate["local_environment_counts"]
        ),
    }


def combined_score(scores: Mapping[str, float], weights: Mapping[str, float]) -> float:
    return round(sum(scores[key] * weight for key, weight in weights.items()), 6)


def likely_signal_source(scores: Mapping[str, float]) -> str:
    low_components = [key for key, value in scores.items() if value < 0.999999]
    if not low_components:
        return "combined scaffold signal"
    lowest = min(scores[key] for key in low_components)
    tied = [key for key in low_components if scores[key] == lowest]
    if len(tied) > 1:
        return "combined scaffold signal"
    return SIGNAL_SOURCES[tied[0]]


def bool_text(value: bool) -> str:
    return "True" if value else "False"


def data02c_warning(control_id: str, row: Mapping[str, str], carried_ids: set[str], generic_warning: str) -> str:
    flags = []
    if control_id in carried_ids:
        flags.append("explicit_high_risk_or_low_contrast_case_from_DATA02C")
    if row.get("negative_finding_flag") == "True":
        flags.append("DATA02C_negative_finding_flag")
    if row.get("highest_risk_mimic_control") == "True":
        flags.append("DATA02C_highest_risk_mimic_control")
    if row.get("lowest_original_control_coherence_contrast") == "True":
        flags.append("DATA02C_lowest_original_control_coherence_contrast")
    if not flags:
        return ""
    return f"{generic_warning}; " + "; ".join(flags)


def interpretation(delta: float, threshold: float, mimic_threshold: float) -> str:
    if delta <= mimic_threshold:
        return "zero_or_low_delta_control_mimicry_boundary"
    if delta < threshold:
        return "below_threshold_low_contrast_boundary"
    return "passes_configured_scaffold_separation_threshold"


def main() -> None:
    config = load_json(CONFIG_PATH)
    inputs = {key: project_path(value) for key, value in config["input_dependencies"].items()}
    for key, path in inputs.items():
        if not path.exists():
            raise FileNotFoundError(f"Missing required input {key}: {path}")

    original_nodes = read_csv(inputs["carbon_ladder_nodes"])
    original_edges = read_csv(inputs["carbon_ladder_edges"])
    control_nodes = read_csv(inputs["control_nodes"])
    control_edges = read_csv(inputs["control_edges"])
    data02b_manifest = load_json(inputs["carbon_bonding_organization_manifest"])
    data02c_manifest = load_json(inputs["control_ensemble_manifest"])
    data02c_coherence = read_csv(inputs["data02c_organization_coherence_summary"])

    weights = config["component_weights"]
    weight_sum = round(sum(weights.values()), 10)
    if weight_sum != 1.0:
        raise ValueError(f"Component weights must sum to 1.0, got {weight_sum}")

    data_dir = project_path(config["data_dir"])
    run_dir = project_path(config["output_dir"])
    data_dir.mkdir(parents=True, exist_ok=True)
    run_dir.mkdir(parents=True, exist_ok=True)

    originals_by_system = group_rows(original_nodes, "system_id")
    original_edges_by_system = group_rows(original_edges, "system_id")
    controls_by_id = group_rows(control_nodes, "control_id")
    control_edges_by_id = group_rows(control_edges, "control_id")
    coherence_by_control = {row["control_id"]: row for row in data02c_coherence}
    carried_ids = set(config["highest_risk_controls_carried_from_DATA02C"])

    original_signatures = {
        system: signature(originals_by_system[system], original_edges_by_system[system])
        for system in sorted(originals_by_system)
    }

    original_summary: List[Dict[str, Any]] = []
    for system, sig in original_signatures.items():
        scores = {key: 1.0 for key in weights}
        original_summary.append(
            {
                "original_system_id": system,
                "node_count": sig["node_count"],
                "edge_count": sig["edge_count"],
                "degree_distribution": json.dumps(sig["degree_distribution"], sort_keys=True),
                "component_score_topology": 1.0,
                "component_score_degree": 1.0,
                "component_score_bond_order": 1.0,
                "component_score_hybridization": 1.0,
                "component_score_sigma_pi": 1.0,
                "component_score_local_environment": 1.0,
                "combined_bonding_organization_score": combined_score(scores, weights),
                "likely_signal_source": "combined scaffold signal",
                "interpretation_boundary": CLAIM_BOUNDARY,
            }
        )

    control_summary: List[Dict[str, Any]] = []
    separation_rows: List[Dict[str, Any]] = []
    threshold = float(config["separation_threshold"])
    mimic_threshold = float(config["mimic_risk_delta_threshold"])

    for control_id, nodes in sorted(controls_by_id.items()):
        if control_id not in control_edges_by_id:
            raise ValueError(f"Control has nodes but no edge group: {control_id}")
        source_system = nodes[0]["source_system_id"]
        family_id = nodes[0]["control_family_id"]
        if source_system not in original_signatures:
            raise ValueError(f"Unknown source system for control {control_id}: {source_system}")
        candidate_sig = signature(nodes, control_edges_by_id[control_id], prefer_original=True)
        scores = component_scores(original_signatures[source_system], candidate_sig)
        control_score = combined_score(scores, weights)
        original_score = 1.0
        delta = round(original_score - control_score, 6)
        mimic = delta <= mimic_threshold or control_id in carried_ids
        source = likely_signal_source(scores)
        boundary = interpretation(delta, threshold, mimic_threshold)
        warning = data02c_warning(control_id, coherence_by_control.get(control_id, {}), carried_ids, config["data02c_mimic_warning"])

        control_summary.append(
            {
                "control_id": control_id,
                "original_system_id": source_system,
                "control_family_id": family_id,
                "node_count": candidate_sig["node_count"],
                "edge_count": candidate_sig["edge_count"],
                "degree_distribution": json.dumps(candidate_sig["degree_distribution"], sort_keys=True),
                "component_score_topology": scores["topology_signature_diagnostic"],
                "component_score_degree": scores["degree_distribution_diagnostic"],
                "component_score_bond_order": scores["bond_order_distribution_diagnostic"],
                "component_score_hybridization": scores["hybridization_distribution_diagnostic"],
                "component_score_sigma_pi": scores["sigma_pi_organization_diagnostic"],
                "component_score_local_environment": scores["local_environment_consistency_diagnostic"],
                "combined_bonding_organization_score": control_score,
                "likely_signal_source": source,
                "mimic_risk_flag": bool_text(mimic),
                "interpretation_boundary": boundary,
            }
        )
        separation_rows.append(
            {
                "original_system_id": source_system,
                "control_id": control_id,
                "control_family_id": family_id,
                "original_combined_score": original_score,
                "control_combined_score": control_score,
                "original_control_delta": delta,
                "separation_pass_flag": bool_text(delta >= threshold),
                "mimic_risk_flag": bool_text(mimic),
                "likely_signal_source": source,
                "control_warning_carried_from_DATA02C": warning,
                "interpretation_boundary": boundary,
            }
        )

    lowest_row = min(separation_rows, key=lambda row: (float(row["original_control_delta"]), row["control_id"]))
    highest_risk_rows = [
        row for row in control_summary if row["control_id"] == lowest_row["control_id"] or row["control_id"] in carried_ids
    ]
    highest_risk_output = []
    separation_by_control = {row["control_id"]: row for row in separation_rows}
    for row in sorted(highest_risk_rows, key=lambda item: (float(separation_by_control[item["control_id"]]["original_control_delta"]), item["control_id"])):
        sep = separation_by_control[row["control_id"]]
        highest_risk_output.append(
            {
                "control_id": row["control_id"],
                "original_system_id": row["original_system_id"],
                "control_family_id": row["control_family_id"],
                "component_score_topology": row["component_score_topology"],
                "component_score_degree": row["component_score_degree"],
                "component_score_bond_order": row["component_score_bond_order"],
                "component_score_hybridization": row["component_score_hybridization"],
                "component_score_sigma_pi": row["component_score_sigma_pi"],
                "component_score_local_environment": row["component_score_local_environment"],
                "combined_bonding_organization_score": row["combined_bonding_organization_score"],
                "original_control_delta": sep["original_control_delta"],
                "mimic_risk_flag": sep["mimic_risk_flag"],
                "possible_negative_finding": bool_text(sep["mimic_risk_flag"] == "True" or sep["separation_pass_flag"] == "False"),
                "interpretation_boundary": sep["interpretation_boundary"],
            }
        )

    component_rows = [
        {
            "component_id": component_id,
            "component_weight": weight,
            "signal_type": SIGNAL_SOURCES[component_id],
            "risk_boundary": CLAIM_BOUNDARY,
            "included_in_combined_score": "True",
        }
        for component_id, weight in weights.items()
    ]

    proxy_rows = [
        {
            "diagnostic_or_proxy_id": "topology_signature_diagnostic",
            "risk_type": "scaffold/topology-derived",
            "risk_level": "medium_to_high",
            "interpretation_boundary": "topology score is scaffold/topology-derived; not real-data validation and not physical validation",
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        },
        {
            "diagnostic_or_proxy_id": "degree_distribution_diagnostic",
            "risk_type": "scaffold/degree-derived",
            "risk_level": "medium_to_high",
            "interpretation_boundary": "degree score is scaffold/degree-derived; not real-data validation and not physical validation",
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        },
        {
            "diagnostic_or_proxy_id": "bond_order_distribution_diagnostic",
            "risk_type": "label/scaffold-derived",
            "risk_level": "high",
            "interpretation_boundary": "bond-order score is label/scaffold-derived; not real-data validation and not physical validation",
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        },
        {
            "diagnostic_or_proxy_id": "hybridization_distribution_diagnostic",
            "risk_type": "label/scaffold-derived",
            "risk_level": "high",
            "interpretation_boundary": "hybridization score is label/scaffold-derived; not real-data validation and not physical validation",
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        },
        {
            "diagnostic_or_proxy_id": "sigma_pi_organization_diagnostic",
            "risk_type": "label/scaffold-derived",
            "risk_level": "high",
            "interpretation_boundary": "sigma/pi score is label/scaffold-derived; not real-data validation and not physical validation",
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        },
        {
            "diagnostic_or_proxy_id": "local_environment_consistency_diagnostic",
            "risk_type": "label/topology/degree scaffold-derived",
            "risk_level": "high",
            "interpretation_boundary": "local environment score is synthetic scaffold diagnostic; not real-data validation and not physical validation",
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        },
        {
            "diagnostic_or_proxy_id": "combined_bonding_organization_score",
            "risk_type": "synthetic scaffold diagnostic",
            "risk_level": "high",
            "interpretation_boundary": "combined score is synthetic scaffold diagnostic; not real-data validation and not physical validation",
            "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
            "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        },
    ]

    pass_count = sum(1 for row in separation_rows if row["separation_pass_flag"] == "True")
    fail_count = len(separation_rows) - pass_count
    possible_negative = fail_count > 0 or any(row["mimic_risk_flag"] == "True" for row in separation_rows)
    stop_go = (
        "revise_diagnostics_due_to_control_mimicry"
        if possible_negative
        else "go_diagnostic_separation_with_documented_boundaries"
    )
    family_count = len({row["control_family_id"] for row in control_summary})

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "stop_go_outcome": stop_go,
        "external_data_downloaded": False,
        "source_blocks": ["QSB-BRIDGE-DATA-02B", "QSB-BRIDGE-DATA-02C"],
        "original_system_count": len(originals_by_system),
        "control_count": len(controls_by_id),
        "control_family_count": family_count,
        "separation_threshold": threshold,
        "separation_pass_count": pass_count,
        "separation_fail_count": fail_count,
        "highest_risk_mimic_control": highest_risk_output[0],
        "lowest_original_control_delta": {
            "control_id": lowest_row["control_id"],
            "original_system_id": lowest_row["original_system_id"],
            "original_control_delta": lowest_row["original_control_delta"],
        },
        "possible_negative_finding_present": possible_negative,
        "no_realdata_validation_claim": True,
        "no_molecular_validation_claim": True,
        "no_physical_validation_claim": True,
        "no_spacetime_emergence_claim": True,
        "no_electronic_configuration_recognition_claim": True,
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "data02c_mimic_warning": config["data02c_mimic_warning"],
    }

    manifest = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": CLAIM_BOUNDARY,
        "external_data_downloaded": False,
        "input_dependencies": config["input_dependencies"],
        "diagnostic_families": config["diagnostic_families"],
        "component_weights": weights,
        "separation_threshold": threshold,
        "data02c_low_contrast_warning": config["data02c_mimic_warning"],
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
        "source_block_claim_boundaries": {
            "DATA02B": data02b_manifest.get("claim_boundary", ""),
            "DATA02C": data02c_manifest.get("claim_boundary", ""),
        },
    }

    readout = f"""# QSB-BRIDGE-DATA-02D Diagnostic Separation Readout

## Purpose
Run a synthetic/reference-style scaffold diagnostic separation between DATA-02B originals and DATA-02C controls.

## Inputs
- data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv
- data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv
- data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json
- data/QSB-BRIDGE-DATA-02C/control_nodes.csv
- data/QSB-BRIDGE-DATA-02C/control_edges.csv
- data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json
- runs/QSB-BRIDGE-DATA-02C/control_ensembles_open/organization_coherence_summary.csv

## Befund
Original systems: {len(originals_by_system)}. Controls: {len(controls_by_id)} across {family_count} families.
Separation threshold: {threshold}. Pass count: {pass_count}. Fail count: {fail_count}.
Lowest original/control delta: {lowest_row['original_control_delta']} for {lowest_row['control_id']}.
Highest-risk mimic row: {highest_risk_output[0]['control_id']}.
Possible negative finding present: {possible_negative}.

## Interpretation
The diagnostic separates only under transparent scaffold scoring rules. Low or zero delta is treated as control mimicry or a boundary finding, not as a nuisance result.

## Hypothese
Under synthetic scaffold/control conditions, label, topology, degree, sigma/pi, and local-environment diagnostics can be used to test separability, while exposing cases where controls mimic originals.

## Offene Luecke
Missing: real molecular data, measured normal modes, spectral data, QC matrix outputs, inorganic comparison systems, and real K_ij proxies.

## Claim Boundary
No real-data validation, no molecular validation, no physical validation, no spacetime emergence, no physical metric recovery, no causal structure, no de-Broglie confirmation, no real quantum dynamics, and no proof that electronic configurations or bonding organization are recognized.

Warnings carried forward:
- {config['qsb_bridge_num_05c_warning']}
- {config['data02c_mimic_warning']}

## Machine-readable outputs list
- summary.json
- original_diagnostic_summary.csv
- control_diagnostic_summary.csv
- original_vs_control_separation.csv
- highest_risk_mimic_diagnostic.csv
- diagnostic_component_weights.csv
- proxy_risk_summary.csv
- resolved_config.json
- data mirror: diagnostic_manifest.json
"""

    original_fields = [
        "original_system_id",
        "node_count",
        "edge_count",
        "degree_distribution",
        "component_score_topology",
        "component_score_degree",
        "component_score_bond_order",
        "component_score_hybridization",
        "component_score_sigma_pi",
        "component_score_local_environment",
        "combined_bonding_organization_score",
        "likely_signal_source",
        "interpretation_boundary",
    ]
    control_fields = [
        "control_id",
        "original_system_id",
        "control_family_id",
        "node_count",
        "edge_count",
        "degree_distribution",
        "component_score_topology",
        "component_score_degree",
        "component_score_bond_order",
        "component_score_hybridization",
        "component_score_sigma_pi",
        "component_score_local_environment",
        "combined_bonding_organization_score",
        "likely_signal_source",
        "mimic_risk_flag",
        "interpretation_boundary",
    ]
    separation_fields = [
        "original_system_id",
        "control_id",
        "control_family_id",
        "original_combined_score",
        "control_combined_score",
        "original_control_delta",
        "separation_pass_flag",
        "mimic_risk_flag",
        "likely_signal_source",
        "control_warning_carried_from_DATA02C",
        "interpretation_boundary",
    ]
    mimic_fields = [
        "control_id",
        "original_system_id",
        "control_family_id",
        "component_score_topology",
        "component_score_degree",
        "component_score_bond_order",
        "component_score_hybridization",
        "component_score_sigma_pi",
        "component_score_local_environment",
        "combined_bonding_organization_score",
        "original_control_delta",
        "mimic_risk_flag",
        "possible_negative_finding",
        "interpretation_boundary",
    ]
    component_fields = ["component_id", "component_weight", "signal_type", "risk_boundary", "included_in_combined_score"]
    proxy_fields = [
        "diagnostic_or_proxy_id",
        "risk_type",
        "risk_level",
        "interpretation_boundary",
        "qsb_bridge_num_05c_warning",
        "data02c_low_contrast_warning",
    ]

    for target_dir in [run_dir, data_dir]:
        write_csv(target_dir / "original_diagnostic_summary.csv", original_fields, original_summary)
        write_csv(target_dir / "control_diagnostic_summary.csv", control_fields, control_summary)
        write_csv(target_dir / "original_vs_control_separation.csv", separation_fields, separation_rows)
        write_csv(target_dir / "highest_risk_mimic_diagnostic.csv", mimic_fields, highest_risk_output)
        write_csv(target_dir / "diagnostic_component_weights.csv", component_fields, component_rows)

    write_csv(run_dir / "proxy_risk_summary.csv", proxy_fields, proxy_rows)
    write_json(run_dir / "summary.json", summary)
    write_json(run_dir / "resolved_config.json", config)
    write_json(data_dir / "diagnostic_manifest.json", manifest)
    (run_dir / "readout.md").write_text(readout, encoding="utf-8")


if __name__ == "__main__":
    main()
