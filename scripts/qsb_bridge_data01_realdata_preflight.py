#!/usr/bin/env python3
"""
QSB-BRIDGE-DATA-01 real-data preflight.

This script performs a no-network, no-download preflight from local static
configuration only. It writes method-level readiness and risk artifacts for a
later DATA-02 decision. It does not make physical validation claims.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/QSB-BRIDGE-DATA-01/preflight_config.json"


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_dicts(path: Path) -> List[Dict[str, str]]:
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


def candidate_by_id(config: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {candidate["candidate_id"]: candidate for candidate in config["candidates"]}


def source_risk(source_type: str) -> str:
    if source_type in {"structural_coordinates", "molecular_graph_bonding_adjacency"}:
        return "high"
    if source_type == "quantum_chemistry_outputs_if_locally_available_later":
        return "medium_to_high"
    return "medium"


def source_recommendation(source_type: str, candidate_id: str) -> str:
    if candidate_id == "h2":
        return "pipeline_sanity_only"
    if source_type in {"structural_coordinates", "molecular_graph_bonding_adjacency"}:
        return "hold_as_reference_or_control_only"
    return "possible_DATA02_candidate_if_local_machine_readable_provenance_is_supplied"


def build_candidate_source_matrix(
    registry_rows: List[Dict[str, str]], config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    candidates = candidate_by_id(config)
    warning = config["carry_forward_warnings"]["qsb_bridge_num_05c"]
    rows: List[Dict[str, Any]] = []
    for row in registry_rows:
        candidate = candidates[row["candidate_id"]]
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "candidate_label": row["candidate_label"],
                "source_type": row["source_type"],
                "ground_truth_geometry": candidate["ground_truth_geometry"],
                "independent_input_candidate": (
                    "yes"
                    if row["source_type"] in candidate["independent_input_candidates"]
                    else "reference_or_control_only"
                ),
                "data_availability_status": row["data_availability_status"],
                "machine_readable_format_status": row["machine_readable_format_status"],
                "provenance_status": row["provenance_status"],
                "geometry_smuggling_risk": source_risk(row["source_type"]),
                "phase_information_availability": row["phase_information_availability"],
                "local_neighborhood_noise_risk": warning,
                "go_no_go_recommendation_for_DATA02": source_recommendation(
                    row["source_type"], row["candidate_id"]
                ),
            }
        )
    return rows


def build_data_field_inventory(registry_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for row in registry_rows:
        rows.append(
            {
                "candidate_id": row["candidate_id"],
                "candidate_label": row["candidate_label"],
                "source_type": row["source_type"],
                "required_fields": row["required_fields"],
                "machine_readable_format_status": row["machine_readable_format_status"],
                "provenance_status": row["provenance_status"],
                "notes": row["notes"],
            }
        )
    return rows


def build_k_proxy_risk_assessment(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    warning = config["carry_forward_warnings"]["qsb_bridge_num_05c"]
    for candidate in config["candidates"]:
        for proxy in config["k_proxy_definitions"]:
            recommendation = proxy["preflight_assessment"]
            if candidate["candidate_id"] == "h2":
                recommendation = "pipeline_sanity_only_no_geometry_recovery_interpretation"
            rows.append(
                {
                    "candidate_id": candidate["candidate_id"],
                    "candidate_label": candidate["candidate_label"],
                    "proxy_id": proxy["proxy_id"],
                    "possible_K_proxy_definition": proxy["description"],
                    "geometry_smuggling_risk": proxy["geometry_smuggling_risk"],
                    "risk_reason": proxy["risk_reason"],
                    "preflight_assessment": recommendation,
                    "local_neighborhood_noise_risk": warning,
                }
            )
    return rows


def build_decisions(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    warning = config["carry_forward_warnings"]["qsb_bridge_num_05c"]
    rows: List[Dict[str, Any]] = []
    for candidate in config["candidates"]:
        if candidate["candidate_id"] == "h2":
            decision = "go_pipeline_sanity_only"
            reason = "Small system can test parsing flow only; no meaningful geometry-recovery interpretation."
        else:
            decision = "hold_for_DATA02_until_local_sources_and_provenance_are_supplied"
            reason = (
                "Candidate needs machine-readable local sources, provenance, and a K proxy "
                "that does not simply re-encode known geometry."
            )
        rows.append(
            {
                "candidate_id": candidate["candidate_id"],
                "candidate_label": candidate["candidate_label"],
                "go_no_go_recommendation_for_DATA02": decision,
                "reason": reason,
                "required_before_DATA02": "; ".join(candidate["uncertainty_requirements"]),
                "local_neighborhood_noise_risk": warning,
                "claim_boundary": config["claim_boundary"],
            }
        )
    return rows


def markdown_table(headers: List[str], rows: List[Dict[str, Any]]) -> str:
    lines = [
        "|" + "|".join(headers) + "|",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    for row in rows:
        values = [str(row.get(header, "")).replace("\n", " ") for header in headers]
        lines.append("|" + "|".join(values) + "|")
    return "\n".join(lines)


def build_readout(
    config: Dict[str, Any],
    summary: Dict[str, Any],
    decisions: List[Dict[str, Any]],
    proxy_rows: List[Dict[str, Any]],
) -> str:
    decision_headers = [
        "candidate_id",
        "candidate_label",
        "go_no_go_recommendation_for_DATA02",
        "reason",
    ]
    proxy_headers = [
        "candidate_id",
        "proxy_id",
        "geometry_smuggling_risk",
        "preflight_assessment",
    ]
    return "\n".join(
        [
            "# QSB-BRIDGE-DATA-01 Run Readout",
            "",
            "## Run",
            "",
            "```text",
            f"block_id: {config['block_id']}",
            f"run_id: {config['run_id']}",
            f"stop_go_outcome: {summary['stop_go_outcome']}",
            f"network_policy: {config['network_policy']}",
            "```",
            "",
            "## Claim Boundary",
            "",
            "DATA-01 is preflight only, with no physical validation claim.",
            "",
            "It does not establish spacetime emergence, physical metric recovery, causal structure, de-Broglie confirmation, real quantum dynamics, or molecular validation.",
            "",
            "## 05C Warning Carried Forward",
            "",
            config["carry_forward_warnings"]["qsb_bridge_num_05c"],
            "",
            "Any later DATA-02 work must report local-neighborhood sensitivity, not only global geometry scores.",
            "",
            "## Candidate Decisions",
            "",
            markdown_table(decision_headers, decisions),
            "",
            "## K Proxy Risk Summary",
            "",
            markdown_table(proxy_headers, proxy_rows),
            "",
            "## Future Result Discussion Requirement",
            "",
            "Create a separate DATA-01 result discussion only after reading these outputs. It must include a human-readable Bauchbild and remain defensive and method-level.",
            "",
            "The Bauchbild should explain DATA-01 as a source-material and lab-notebook precheck: provenance, machine-readable fields, uncertainty, and proxy risks are inspected before any validation-like interpretation is attempted.",
            "",
            "## Download Policy",
            "",
            "No external data were downloaded by this script. The outputs are generated from local static preflight declarations only.",
            "",
        ]
    )


def main() -> None:
    config = load_json(CONFIG_PATH)
    registry_path = project_path(config["source_registry_path"])
    output_dir = project_path(config["output_dir"])
    registry_rows = read_csv_dicts(registry_path)

    candidate_source_rows = build_candidate_source_matrix(registry_rows, config)
    field_inventory_rows = build_data_field_inventory(registry_rows)
    proxy_rows = build_k_proxy_risk_assessment(config)
    decision_rows = build_decisions(config)

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "claim_boundary": config["claim_boundary"],
        "network_policy": config["network_policy"],
        "external_data_downloaded": False,
        "candidate_count": len(config["candidates"]),
        "source_type_count": len(config["source_types"]),
        "candidate_source_rows": len(candidate_source_rows),
        "k_proxy_rows": len(proxy_rows),
        "data_field_inventory_rows": len(field_inventory_rows),
        "decision_rows": len(decision_rows),
        "required_diagnostics": config["required_diagnostics"],
        "qsb_bridge_num_05c_warning": config["carry_forward_warnings"]["qsb_bridge_num_05c"],
        "future_result_discussion_requirement": config["future_result_discussion_requirement"],
        "stop_go_outcome": "hold_for_DATA02_until_local_sources_and_provenance_are_supplied",
        "no_physical_validation_claim": True,
    }

    write_json(output_dir / "summary.json", summary)
    write_json(output_dir / "resolved_config.json", config)
    write_csv(
        output_dir / "candidate_source_matrix.csv",
        [
            "candidate_id",
            "candidate_label",
            "source_type",
            "ground_truth_geometry",
            "independent_input_candidate",
            "data_availability_status",
            "machine_readable_format_status",
            "provenance_status",
            "geometry_smuggling_risk",
            "phase_information_availability",
            "local_neighborhood_noise_risk",
            "go_no_go_recommendation_for_DATA02",
        ],
        candidate_source_rows,
    )
    write_csv(
        output_dir / "k_proxy_risk_assessment.csv",
        [
            "candidate_id",
            "candidate_label",
            "proxy_id",
            "possible_K_proxy_definition",
            "geometry_smuggling_risk",
            "risk_reason",
            "preflight_assessment",
            "local_neighborhood_noise_risk",
        ],
        proxy_rows,
    )
    write_csv(
        output_dir / "data_field_inventory.csv",
        [
            "candidate_id",
            "candidate_label",
            "source_type",
            "required_fields",
            "machine_readable_format_status",
            "provenance_status",
            "notes",
        ],
        field_inventory_rows,
    )
    write_csv(
        output_dir / "realdata_preflight_decision.csv",
        [
            "candidate_id",
            "candidate_label",
            "go_no_go_recommendation_for_DATA02",
            "reason",
            "required_before_DATA02",
            "local_neighborhood_noise_risk",
            "claim_boundary",
        ],
        decision_rows,
    )
    (output_dir / "readout.md").write_text(
        build_readout(config, summary, decision_rows, proxy_rows), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
