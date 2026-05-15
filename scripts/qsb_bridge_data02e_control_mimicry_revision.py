#!/usr/bin/env python3
"""
QSB-BRIDGE-DATA-02E control mimicry revision.

This runner uses only local DATA-02D outputs and computes deterministic,
synthetic/reference-style mimicry diagnostics. It does not download external
data, does not use coordinates, and does not use geometry-derived K_ij.
"""

from __future__ import annotations

import csv
import json
import shutil
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any, Dict, Iterable, List, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "data/QSB-BRIDGE-DATA-02E/control_mimicry_revision_config.json"

COMPONENT_FIELDS = {
    "topology_signature_diagnostic": "component_score_topology",
    "degree_distribution_diagnostic": "component_score_degree",
    "bond_order_distribution_diagnostic": "component_score_bond_order",
    "hybridization_distribution_diagnostic": "component_score_hybridization",
    "sigma_pi_organization_diagnostic": "component_score_sigma_pi",
    "local_environment_consistency_diagnostic": "component_score_local_environment",
}

LABEL_COMPONENT_FIELDS = [
    "component_score_bond_order",
    "component_score_hybridization",
    "component_score_sigma_pi",
    "component_score_local_environment",
]

CLAIM_BOUNDARY = (
    "synthetic/reference-style diagnostic only; no real-data validation, no molecular "
    "validation, no physical validation, no spacetime emergence, no physical metric "
    "recovery, no causal structure, no de-Broglie confirmation, no real quantum "
    "dynamics, no proof that electronic configurations are recognized, and no proof "
    "that bonding organization is physically recognized"
)

DATA02D_BOUNDARY = (
    "DATA-02D separation result is a synthetic scaffold diagnostic; failed controls "
    "remain boundary findings rather than validation evidence"
)


def project_path(value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else ROOT / path


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames))
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def as_bool(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def round6(value: float) -> float:
    return round(value, 6)


def classify_level(value: float, low: float, high: float, low_label: str, mid_label: str, high_label: str) -> str:
    if value <= low:
        return low_label
    if value >= high:
        return high_label
    return mid_label


def label_control_family(control_family_id: str) -> bool:
    family = control_family_id.lower()
    return "label_shuffle" in family or "label_randomization" in family or "within_system" in family


def load_inputs(config: Mapping[str, Any]) -> Dict[str, Any]:
    inputs = {name: project_path(path) for name, path in config["primary_inputs"].items()}
    missing = [str(path.relative_to(ROOT)) for path in inputs.values() if not path.exists()]
    if missing:
        return {"missing": missing, "inputs": inputs}
    return {
        "missing": [],
        "inputs": inputs,
        "data02d_summary": read_json(inputs["data02d_summary"]),
        "original_rows": read_csv(inputs["original_diagnostic_summary"]),
        "control_rows": read_csv(inputs["control_diagnostic_summary"]),
        "separation_rows": read_csv(inputs["original_vs_control_separation"]),
        "highest_risk_rows": read_csv(inputs["highest_risk_mimic_diagnostic"]),
        "weight_rows": read_csv(inputs["diagnostic_component_weights"]),
        "proxy_rows": read_csv(inputs["proxy_risk_summary"]),
    }


def component_weights(weight_rows: Sequence[Mapping[str, str]]) -> Dict[str, float]:
    weights = {
        COMPONENT_FIELDS[row["component_id"]]: as_float(row["component_weight"])
        for row in weight_rows
        if row.get("component_id") in COMPONENT_FIELDS
    }
    total = sum(weights.values())
    if total <= 0:
        raise SystemExit("DATA-02D component weights are missing or zero")
    return {field: weight / total for field, weight in weights.items()}


def weighted_control_destruction(row: Mapping[str, Any], weights: Mapping[str, float]) -> float:
    # Transparent rule: component_damage_i = 1 - control_component_score_i.
    # The final score is the DATA-02D-weighted mean of component damage.
    return round6(sum((1.0 - as_float(row.get(field))) * weight for field, weight in weights.items()))


def label_uniformity_risk(row: Mapping[str, Any], high_risk_threshold: float) -> float:
    if not label_control_family(str(row.get("control_family_id", ""))):
        return 0.0
    retained = [as_float(row.get(field)) for field in LABEL_COMPONENT_FIELDS]
    if retained and min(retained) >= high_risk_threshold:
        return 1.0
    return round6(sum(score for score in retained if score >= high_risk_threshold) / max(len(retained), 1))


def failure_mode(row: Mapping[str, Any]) -> str:
    modes: List[str] = []
    if as_float(row.get("label_uniformity_risk_score")) >= 0.95:
        modes.append("label_uniformity_or_shuffle_degeneracy")
    if as_float(row.get("topology_preservation_risk_score")) >= 0.95:
        modes.append("topology_preservation")
    if as_float(row.get("degree_preservation_risk_score")) >= 0.95:
        modes.append("degree_preservation")
    if as_float(row.get("local_environment_reuse_risk_score")) >= 0.95:
        modes.append("local_environment_reuse")
    if as_float(row.get("control_destruction_effectiveness_score")) <= 0.15:
        modes.append("low_control_destruction_effectiveness")
    return "+".join(modes) if modes else "unclassified_mimic_mode"


def revision_focus(mode: str, family: str) -> str:
    if "label_uniformity" in mode:
        return "separate label-shuffle adequacy from scaffold separation; flag uniform-label controls"
    if "local_environment" in mode:
        return "add local-environment reuse inventory before changing combined scores"
    if "topology" in mode or "degree" in mode:
        return "separate topology and degree preservation from label-derived diagnostic response"
    if "low_control_destruction" in mode:
        return "classify weak controls before using them as separation evidence"
    return f"inspect unclassified mimic mode in {family}"


def build_inventory(
    control_rows: Sequence[Mapping[str, str]],
    separation_rows: Sequence[Mapping[str, str]],
    weights: Mapping[str, float],
    config: Mapping[str, Any],
) -> List[Dict[str, Any]]:
    control_by_id = {row["control_id"]: row for row in control_rows}
    rows: List[Dict[str, Any]] = []
    for sep in separation_rows:
        control = control_by_id[sep["control_id"]]
        merged: Dict[str, Any] = {**control, **sep}
        destruction = weighted_control_destruction(merged, weights)
        label_risk = label_uniformity_risk(merged, as_float(config["high_risk_threshold"]))
        topology_risk = as_float(merged.get("component_score_topology"))
        degree_risk = as_float(merged.get("component_score_degree"))
        local_risk = as_float(merged.get("component_score_local_environment"))
        delta = as_float(merged.get("original_control_delta"))
        degenerate = (
            destruction <= as_float(config["degenerate_control_threshold"])
            or delta <= as_float(config["mimic_threshold"])
            or (label_risk >= as_float(config["high_risk_threshold"]) and label_control_family(merged["control_family_id"]))
        )
        mimic_risk = as_bool(merged.get("mimic_risk_flag")) or not as_bool(merged.get("separation_pass_flag")) or degenerate
        out = {
            "control_id": merged["control_id"],
            "original_system_id": merged["original_system_id"],
            "control_family_id": merged["control_family_id"],
            "original_control_delta": round6(delta),
            "separation_pass_flag": as_bool(merged.get("separation_pass_flag")),
            "mimic_risk_flag": mimic_risk,
            "data02d_interpretation_boundary": DATA02D_BOUNDARY,
            "component_score_topology": as_float(merged.get("component_score_topology")),
            "component_score_degree": as_float(merged.get("component_score_degree")),
            "component_score_bond_order": as_float(merged.get("component_score_bond_order")),
            "component_score_hybridization": as_float(merged.get("component_score_hybridization")),
            "component_score_sigma_pi": as_float(merged.get("component_score_sigma_pi")),
            "component_score_local_environment": as_float(merged.get("component_score_local_environment")),
            "combined_bonding_organization_score": as_float(merged.get("combined_bonding_organization_score")),
            "control_destruction_effectiveness_score": destruction,
            "label_uniformity_risk_score": label_risk,
            "topology_preservation_risk_score": round6(topology_risk),
            "degree_preservation_risk_score": round6(degree_risk),
            "local_environment_reuse_risk_score": round6(local_risk),
            "degenerate_control_flag": degenerate,
            "interpretation_boundary": CLAIM_BOUNDARY,
        }
        out["failure_mode_label"] = failure_mode(out) if not out["separation_pass_flag"] or degenerate else "separated_control"
        out["recommended_revision_focus"] = revision_focus(out["failure_mode_label"], out["control_family_id"])
        rows.append(out)
    return rows


def build_destruction_summary(inventory: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for row in inventory:
        score = as_float(row["control_destruction_effectiveness_score"])
        level = classify_level(score, 0.15, 0.35, "low_or_degenerate", "moderate", "strong")
        if as_bool(row["degenerate_control_flag"]):
            likely_reason = row["failure_mode_label"]
        elif score >= 0.35:
            likely_reason = "control_changed_weighted_component_set"
        else:
            likely_reason = "partial_scaffold_preservation"
        rows.append(
            {
                "control_id": row["control_id"],
                "original_system_id": row["original_system_id"],
                "control_family_id": row["control_family_id"],
                "original_control_delta": row["original_control_delta"],
                "control_destruction_effectiveness_score": score,
                "degenerate_control_flag": row["degenerate_control_flag"],
                "destruction_effectiveness_level": level,
                "likely_reason": likely_reason,
                "interpretation_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def build_specificity_summary(
    inventory: Sequence[Mapping[str, Any]], weight_rows: Sequence[Mapping[str, str]]
) -> List[Dict[str, Any]]:
    weight_by_component = {row["component_id"]: as_float(row["component_weight"]) for row in weight_rows}
    rows: List[Dict[str, Any]] = []
    pass_rows = [row for row in inventory if as_bool(row["separation_pass_flag"])]
    fail_rows = [row for row in inventory if not as_bool(row["separation_pass_flag"])]
    for component, field in COMPONENT_FIELDS.items():
        pass_damage = [1.0 - as_float(row[field]) for row in pass_rows]
        fail_damage = [1.0 - as_float(row[field]) for row in fail_rows]
        mean_pass = round6(mean(pass_damage)) if pass_damage else 0.0
        mean_fail = round6(mean(fail_damage)) if fail_damage else 0.0
        gap = round6(mean_pass - mean_fail)
        score = round6(max(0.0, gap))
        rows.append(
            {
                "diagnostic_component": component,
                "component_weight": weight_by_component.get(component, 0.0),
                "mean_pass_control_damage": mean_pass,
                "mean_fail_control_damage": mean_fail,
                "specificity_gap": gap,
                "diagnostic_specificity_score": score,
                "specificity_level": classify_level(score, 0.05, 0.2, "low", "moderate", "high"),
                "recommended_revision_focus": (
                    "failed controls preserve this component too well"
                    if score < 0.05
                    else "retain as candidate separator with boundary checks"
                ),
                "interpretation_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def build_family_summary(inventory: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[str, List[Mapping[str, Any]]] = defaultdict(list)
    for row in inventory:
        grouped[str(row["control_family_id"])].append(row)
    rows: List[Dict[str, Any]] = []
    for family in sorted(grouped):
        family_rows = grouped[family]
        control_count = len(family_rows)
        fail_count = sum(1 for row in family_rows if not as_bool(row["separation_pass_flag"]))
        mimic_count = sum(1 for row in family_rows if as_bool(row["mimic_risk_flag"]))
        degenerate_count = sum(1 for row in family_rows if as_bool(row["degenerate_control_flag"]))
        mean_delta = round6(mean(as_float(row["original_control_delta"]) for row in family_rows))
        min_delta = round6(min(as_float(row["original_control_delta"]) for row in family_rows))
        mean_destruction = round6(mean(as_float(row["control_destruction_effectiveness_score"]) for row in family_rows))
        mean_label = round6(mean(as_float(row["label_uniformity_risk_score"]) for row in family_rows))
        mean_topology = round6(mean(as_float(row["topology_preservation_risk_score"]) for row in family_rows))
        mean_degree = round6(mean(as_float(row["degree_preservation_risk_score"]) for row in family_rows))
        mean_local = round6(mean(as_float(row["local_environment_reuse_risk_score"]) for row in family_rows))
        if fail_count or degenerate_count >= max(1, control_count // 2):
            risk_level = "high"
        elif mimic_count:
            risk_level = "medium"
        else:
            risk_level = "low"
        rows.append(
            {
                "control_family_id": family,
                "control_count": control_count,
                "separation_fail_count": fail_count,
                "mimic_risk_count": mimic_count,
                "degenerate_control_count": degenerate_count,
                "mean_original_control_delta": mean_delta,
                "min_original_control_delta": min_delta,
                "mean_control_destruction_effectiveness_score": mean_destruction,
                "mean_label_uniformity_risk_score": mean_label,
                "mean_topology_preservation_risk_score": mean_topology,
                "mean_degree_preservation_risk_score": mean_degree,
                "mean_local_environment_reuse_risk_score": mean_local,
                "family_risk_level": risk_level,
                "recommended_revision_focus": revision_focus(
                    "+".join(sorted({str(row["failure_mode_label"]) for row in family_rows})), family
                ),
                "interpretation_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def build_recommendations(family_rows: Sequence[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    high_rows = [row for row in family_rows if row["family_risk_level"] == "high"]
    for index, row in enumerate(high_rows, start=1):
        rows.append(
            {
                "recommendation_id": f"DATA02E-REV-{index:02d}",
                "priority": "high" if index == 1 else "medium",
                "target_failure_mode": "control_mimicry_or_degenerate_control",
                "target_control_family": row["control_family_id"],
                "proposed_revision": row["recommended_revision_focus"],
                "rationale": (
                    f"{row['separation_fail_count']} failed controls and "
                    f"{row['degenerate_control_count']} degenerate controls in this family"
                ),
                "expected_effect": "make mimic modes explicit before any stronger diagnostic is attempted",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    if not rows:
        rows.append(
            {
                "recommendation_id": "DATA02E-REV-01",
                "priority": "boundary",
                "target_failure_mode": "no_failed_controls_detected",
                "target_control_family": "all",
                "proposed_revision": "retain boundary checks and avoid upgrading claims",
                "rationale": "no failed controls were detected in the current input",
                "expected_effect": "keep synthetic/reference-style boundaries visible",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        )
    return rows


def build_proxy_risk_summary(config: Mapping[str, Any]) -> List[Dict[str, Any]]:
    warning = f"{config['qsb_bridge_num_05c_warning']} | {config['data02c_mimic_warning']}"
    return [
        {
            "diagnostic_or_concept": "control_destruction_effectiveness_score",
            "signal_source": "DATA-02D component scores and weights",
            "risk_type": "control adequacy can be circular if it only reuses the combined score",
            "circularity_risk": "medium",
            "mimicry_risk": "high for low-delta controls",
            "claim_boundary": CLAIM_BOUNDARY,
            "warning_carried_forward": warning,
        },
        {
            "diagnostic_or_concept": "diagnostic_specificity_score",
            "signal_source": "pass/fail split and component damage gaps",
            "risk_type": "specificity may be tuned to known controls",
            "circularity_risk": "medium",
            "mimicry_risk": "high when failed controls preserve components",
            "claim_boundary": CLAIM_BOUNDARY,
            "warning_carried_forward": warning,
        },
        {
            "diagnostic_or_concept": "label_uniformity_risk_score",
            "signal_source": "label-derived component retention",
            "risk_type": "uniform labels can make label shuffles weak",
            "circularity_risk": "low",
            "mimicry_risk": "high for within-system label shuffles",
            "claim_boundary": CLAIM_BOUNDARY,
            "warning_carried_forward": warning,
        },
        {
            "diagnostic_or_concept": "topology_degree_local_reuse_risks",
            "signal_source": "topology, degree, and local-environment component retention",
            "risk_type": "controls may preserve the scaffold they are supposed to disturb",
            "circularity_risk": "medium",
            "mimicry_risk": "high for topology-preserving controls",
            "claim_boundary": CLAIM_BOUNDARY,
            "warning_carried_forward": warning,
        },
    ]


def stop_go_outcome(failed: Sequence[Mapping[str, Any]], recommendations: Sequence[Mapping[str, Any]]) -> str:
    if not failed:
        return "go_no_mimic_failures_detected_but_boundary_kept"
    if any(row["failure_mode_label"] == "unclassified_mimic_mode" for row in failed):
        return "revise_due_to_unclassified_mimic_modes"
    if recommendations:
        return "go_revision_targets_identified_with_documented_boundaries"
    return "revise_due_to_unclassified_mimic_modes"


def write_readout(
    path: Path,
    summary: Mapping[str, Any],
    config: Mapping[str, Any],
    output_names: Sequence[str],
) -> None:
    text = f"""# QSB-BRIDGE-DATA-02E Control Mimicry Revision Readout

## Purpose

DATA-02E analyzes why DATA-02D controls passed or failed. It is a synthetic/reference-style diagnostic revision block, not a larger validation step.

## Inputs

Primary inputs are local DATA-02D outputs from `runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open/`. No external data were downloaded. No coordinates or geometry-derived `K_ij` were used.

## Befund

- controls analyzed: {summary['control_count_analyzed']}
- failed controls from DATA-02D: {summary['failed_control_count']}
- degenerate controls classified: {summary['degenerate_control_count']}
- high-risk control families: {summary['high_risk_family_count']}
- lowest original/control delta: {summary['lowest_original_control_delta']}
- primary revision target: {summary['primary_revision_target']}
- stop/go outcome: {summary['stop_go_outcome']}

The DATA-02D warning is carried forward: {config['data02d_mimic_warning']}.
The QSB-BRIDGE-NUM-05C warning is carried forward: {config['qsb_bridge_num_05c_warning']}.

## Interpretation

DATA-02E analyzes why DATA-02D controls passed or failed. DATA-02E does not prove physical recognition. Degenerate controls are not discarded; they are classified as a boundary/failure mode. Persistent mimicry is a valid negative/boundary finding. Any improved diagnostic must avoid merely tuning to the known controls.

## Hypothese

The current failed controls appear to preserve one or more diagnostic scaffold features: labels, topology, degree distribution, local environment, or the combined weighted component set. Adamantane within-system label shuffle remains the key zero-delta fake passport case.

## Offene Luecke

The block classifies mimic modes using DATA-02D component scores. It does not independently establish which synthetic scaffold feature should be physically preferred, and it does not prove that any real bonding or electronic structure has been recognized.

## Consequences for next blocks

Next blocks should inspect failed controls explicitly, avoid hiding mimicry behind aggregate scores, flag weak or degenerate controls, and keep persistent mimicry as a reportable boundary finding.

## Claim Boundary

DATA-02E provides no:

- real-data validation
- molecular validation
- physical validation
- spacetime emergence
- physical metric recovery
- causal structure
- de-Broglie confirmation
- real quantum dynamics
- proof that electronic configurations are recognized
- proof that bonding organization is physically recognized

## Machine-readable outputs list

"""
    text += "".join(f"- `{name}`\n" for name in output_names)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def missing_input_summary(config: Mapping[str, Any], missing: Sequence[str]) -> Dict[str, Any]:
    return {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "stop_go_outcome": "stop_due_to_missing_DATA02D_inputs",
        "external_data_downloaded": False,
        "source_blocks": config["source_blocks"],
        "missing_inputs": list(missing),
        "possible_negative_finding_present": True,
        "no_realdata_validation_claim": True,
        "no_molecular_validation_claim": True,
        "no_physical_validation_claim": True,
        "no_spacetime_emergence_claim": True,
        "no_electronic_configuration_recognition_claim": True,
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "data02c_mimic_warning": config["data02c_mimic_warning"],
        "data02d_mimic_warning": config["data02d_mimic_warning"],
    }


def main() -> None:
    config = read_json(CONFIG_PATH)
    run_dir = project_path(config["run_output_dir"])
    data_dir = project_path(config["data_output_dir"])
    run_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    loaded = load_inputs(config)
    if loaded["missing"]:
        summary = missing_input_summary(config, loaded["missing"])
        write_json(run_dir / "summary.json", summary)
        write_json(run_dir / "resolved_config.json", config)
        raise SystemExit(f"Missing DATA-02D inputs: {loaded['missing']}")

    weights = component_weights(loaded["weight_rows"])
    inventory = build_inventory(loaded["control_rows"], loaded["separation_rows"], weights, config)
    failed = [row for row in inventory if not as_bool(row["separation_pass_flag"])]
    destruction_rows = build_destruction_summary(inventory)
    specificity_rows = build_specificity_summary(inventory, loaded["weight_rows"])
    family_rows = build_family_summary(inventory)
    recommendation_rows = build_recommendations(family_rows)
    proxy_rows = build_proxy_risk_summary(config)

    high_risk_families = [row for row in family_rows if row["family_risk_level"] == "high"]
    degenerate_rows = [row for row in inventory if as_bool(row["degenerate_control_flag"])]
    lowest_row = min(inventory, key=lambda row: as_float(row["original_control_delta"]))
    highest_degenerate = (
        min(degenerate_rows, key=lambda row: as_float(row["control_destruction_effectiveness_score"]))
        if degenerate_rows
        else {}
    )
    primary_target = (
        loaded["data02d_summary"].get("highest_risk_mimic_control", {}).get("control_id")
        or lowest_row["control_id"]
    )
    outcome = stop_go_outcome(failed, recommendation_rows)

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "stop_go_outcome": outcome,
        "external_data_downloaded": False,
        "source_blocks": config["source_blocks"],
        "data02d_stop_go_outcome": loaded["data02d_summary"].get("stop_go_outcome"),
        "data02d_separation_pass_count": loaded["data02d_summary"].get("separation_pass_count"),
        "data02d_separation_fail_count": loaded["data02d_summary"].get("separation_fail_count"),
        "data02d_highest_risk_mimic_control": primary_target,
        "control_count_analyzed": len(inventory),
        "failed_control_count": len(failed),
        "degenerate_control_count": len(degenerate_rows),
        "high_risk_family_count": len(high_risk_families),
        "lowest_original_control_delta": {
            "control_id": lowest_row["control_id"],
            "original_system_id": lowest_row["original_system_id"],
            "original_control_delta": lowest_row["original_control_delta"],
        },
        "highest_degenerate_control": {
            "control_id": highest_degenerate.get("control_id"),
            "original_system_id": highest_degenerate.get("original_system_id"),
            "control_family_id": highest_degenerate.get("control_family_id"),
            "control_destruction_effectiveness_score": highest_degenerate.get("control_destruction_effectiveness_score"),
        },
        "primary_revision_target": primary_target,
        "possible_negative_finding_present": True,
        "no_realdata_validation_claim": True,
        "no_molecular_validation_claim": True,
        "no_physical_validation_claim": True,
        "no_spacetime_emergence_claim": True,
        "no_electronic_configuration_recognition_claim": True,
        "qsb_bridge_num_05c_warning": config["qsb_bridge_num_05c_warning"],
        "data02c_mimic_warning": config["data02c_mimic_warning"],
        "data02d_mimic_warning": config["data02d_mimic_warning"],
    }

    inventory_fields = [
        "control_id",
        "original_system_id",
        "control_family_id",
        "original_control_delta",
        "separation_pass_flag",
        "mimic_risk_flag",
        "data02d_interpretation_boundary",
        "component_score_topology",
        "component_score_degree",
        "component_score_bond_order",
        "component_score_hybridization",
        "component_score_sigma_pi",
        "component_score_local_environment",
        "combined_bonding_organization_score",
        "control_destruction_effectiveness_score",
        "label_uniformity_risk_score",
        "topology_preservation_risk_score",
        "degree_preservation_risk_score",
        "local_environment_reuse_risk_score",
        "degenerate_control_flag",
        "failure_mode_label",
        "recommended_revision_focus",
        "interpretation_boundary",
    ]
    destruction_fields = [
        "control_id",
        "original_system_id",
        "control_family_id",
        "original_control_delta",
        "control_destruction_effectiveness_score",
        "degenerate_control_flag",
        "destruction_effectiveness_level",
        "likely_reason",
        "interpretation_boundary",
    ]
    specificity_fields = [
        "diagnostic_component",
        "component_weight",
        "mean_pass_control_damage",
        "mean_fail_control_damage",
        "specificity_gap",
        "diagnostic_specificity_score",
        "specificity_level",
        "recommended_revision_focus",
        "interpretation_boundary",
    ]
    family_fields = [
        "control_family_id",
        "control_count",
        "separation_fail_count",
        "mimic_risk_count",
        "degenerate_control_count",
        "mean_original_control_delta",
        "min_original_control_delta",
        "mean_control_destruction_effectiveness_score",
        "mean_label_uniformity_risk_score",
        "mean_topology_preservation_risk_score",
        "mean_degree_preservation_risk_score",
        "mean_local_environment_reuse_risk_score",
        "family_risk_level",
        "recommended_revision_focus",
        "interpretation_boundary",
    ]
    recommendation_fields = [
        "recommendation_id",
        "priority",
        "target_failure_mode",
        "target_control_family",
        "proposed_revision",
        "rationale",
        "expected_effect",
        "claim_boundary",
    ]
    proxy_fields = [
        "diagnostic_or_concept",
        "signal_source",
        "risk_type",
        "circularity_risk",
        "mimicry_risk",
        "claim_boundary",
        "warning_carried_forward",
    ]

    outputs = {
        "summary.json": summary,
        "resolved_config.json": config,
        "control_mimic_failure_inventory.csv": (inventory_fields, inventory),
        "control_destruction_effectiveness_summary.csv": (destruction_fields, destruction_rows),
        "diagnostic_specificity_summary.csv": (specificity_fields, specificity_rows),
        "mimic_family_risk_summary.csv": (family_fields, family_rows),
        "revision_recommendation_summary.csv": (recommendation_fields, recommendation_rows),
        "proxy_risk_summary.csv": (proxy_fields, proxy_rows),
    }

    write_json(run_dir / "summary.json", summary)
    write_json(run_dir / "resolved_config.json", config)
    write_csv(run_dir / "control_mimic_failure_inventory.csv", inventory_fields, inventory)
    write_csv(run_dir / "control_destruction_effectiveness_summary.csv", destruction_fields, destruction_rows)
    write_csv(run_dir / "diagnostic_specificity_summary.csv", specificity_fields, specificity_rows)
    write_csv(run_dir / "mimic_family_risk_summary.csv", family_fields, family_rows)
    write_csv(run_dir / "revision_recommendation_summary.csv", recommendation_fields, recommendation_rows)
    write_csv(run_dir / "proxy_risk_summary.csv", proxy_fields, proxy_rows)
    write_readout(run_dir / "readout.md", summary, config, list(outputs.keys()) + ["readout.md"])

    manifest = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "source_run_dir": "runs/QSB-BRIDGE-DATA-02D/diagnostic_separation_open",
        "generated_run_dir": config["run_output_dir"],
        "external_data_downloaded": False,
        "data_mirrors": [
            "control_mimic_failure_inventory.csv",
            "control_destruction_effectiveness_summary.csv",
            "diagnostic_specificity_summary.csv",
            "mimic_family_risk_summary.csv",
            "revision_recommendation_summary.csv",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(data_dir / "control_mimicry_revision_manifest.json", manifest)
    for name in manifest["data_mirrors"]:
        shutil.copyfile(run_dir / name, data_dir / name)

    print(f"Wrote DATA-02E run outputs to {run_dir.relative_to(ROOT)}")
    print(f"stop_go_outcome: {summary['stop_go_outcome']}")


if __name__ == "__main__":
    main()
