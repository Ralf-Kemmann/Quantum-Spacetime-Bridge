#!/usr/bin/env python3
"""Run QSB-CAUSALITY06B-06 second inner-sphere ET case."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any


RUN_ID = "QSB-CAUSALITY06B-06_second_inner_sphere_case"
CASE_ID = "oxalate_cobalt_tetraamine_inner_sphere_et"
FINAL_STATUS = "second_inner_sphere_et_case_completed"
OUTPUT_FILES = [
    "resolved_config.json",
    "validated_oxalate_state_records.json",
    "oxalate_transition_results.csv",
    "oxalate_transition_results.json",
    "cross_case_rule_transfer.csv",
    "german_alias_view.csv",
    "run_summary.json",
    "readout.md",
]
RESULT_COLUMNS = [
    "transition_id",
    "source_state_id",
    "target_state_id",
    "redox_consistent",
    "redox_reason",
    "bridging_ligand_consistent",
    "bridging_ligand_reason",
    "coordination_consistent",
    "coordination_reason",
    "state_change_coherent",
    "state_change_reason",
    "forward_admissible",
    "reverse_admissible",
    "reverse_requires_external_conditions",
    "reverse_external_condition_reasons",
    "forward_transition_status",
    "direction_comparison_class",
]
CROSS_CASE_COMPARISON_MODE = "structured_manual_rule_classification"
CROSS_CASE_TRANSFER_BASED_ON = "implemented_rule_structure_and_declared_case_constraints"


class RunError(RuntimeError):
    """Raised for validation or run failures."""


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def validate_records(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    records = bundle.get("records", [])
    if len(records) != 5:
        raise RunError(f"expected 5 oxalate records, found {len(records)}")
    expected_ids = {"OX01_S0", "OX01_S1", "OX01_S2", "OX01_S3", "OX01_S4"}
    if {record.get("state_id") for record in records} != expected_ids:
        raise RunError("oxalate state_id coverage mismatch")
    required_features = {
        "electron_acceptor_oxidation_state",
        "electron_donor_oxidation_state",
        "bridge_ligand_identity",
        "bridge_mode",
        "acceptor_bridge_bond_status",
        "donor_bridge_bond_status",
        "shared_bridge_status",
        "donor_coordination_accessibility",
        "center_pair_association_status",
        "electron_transfer_balance",
        "bridge_ligand_transfer_balance",
        "acceptor_coordination_environment",
        "donor_coordination_environment",
        "product_separation_status",
        "substitution_lability_pattern",
    }
    for record in records:
        cf = record["chemical_features"]
        missing = required_features - set(cf)
        if missing:
            raise RunError(f"{record['state_id']} missing chemical features {sorted(missing)}")
        if cf["bridge_ligand_identity"] != "oxalate":
            raise RunError(f"{record['state_id']} bridge_ligand_identity must be oxalate")
        if cf["shared_bridge_status"] == "present":
            if cf["bridge_mode"] != "doubly_chelated_bridge":
                raise RunError(f"{record['state_id']} present bridge without doubly chelated bridge mode")
            if cf["acceptor_bridge_bond_status"] != "retained_in_doubly_chelated_bridge":
                raise RunError(f"{record['state_id']} present bridge without acceptor retention")
            if cf["donor_bridge_bond_status"] != "doubly_chelated_bridge_coordination_present":
                raise RunError(f"{record['state_id']} present bridge without donor bridge coordination")
        if cf["electron_transfer_balance"] == "transferred_donor_to_acceptor":
            if cf["electron_acceptor_oxidation_state"] != "+2" or cf["electron_donor_oxidation_state"] != "+3":
                raise RunError(f"{record['state_id']} completed ET without paired role oxidation states")
        if record["state_id"] == "OX01_S3":
            controls = record.get("optional_state_controls", {})
            if controls.get("post_ET_bridge_persistence_required") is not False:
                raise RunError("OX01_S3 post_ET_bridge_persistence_required must be false")
            if controls.get("OX01_S3_required_as_discrete_species") is not False:
                raise RunError("OX01_S3_required_as_discrete_species must be false")
    return records


def validate_candidates(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = bundle.get("transition_candidates", [])
    if len(candidates) != 5:
        raise RunError(f"expected 5 oxalate transition candidates, found {len(candidates)}")
    for candidate in candidates:
        if candidate.get("reference_order_metadata_only") is not True:
            raise RunError(f"{candidate.get('transition_id')} reference order must be metadata only")
    return candidates


def redox_consistency(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    oxidation_changed = (
        s["electron_acceptor_oxidation_state"] != t["electron_acceptor_oxidation_state"]
        or s["electron_donor_oxidation_state"] != t["electron_donor_oxidation_state"]
    )
    completed = t["electron_transfer_balance"] == "transferred_donor_to_acceptor"
    paired_forward = (
        s["electron_acceptor_oxidation_state"] == "+3"
        and s["electron_donor_oxidation_state"] == "+2"
        and t["electron_acceptor_oxidation_state"] == "+2"
        and t["electron_donor_oxidation_state"] == "+3"
    )
    paired_product_side = (
        s["electron_acceptor_oxidation_state"] == "+2"
        and s["electron_donor_oxidation_state"] == "+3"
        and t["electron_acceptor_oxidation_state"] == "+2"
        and t["electron_donor_oxidation_state"] == "+3"
        and completed
    )
    if completed and (paired_forward or paired_product_side):
        return True, "completed donor-to-acceptor ET has paired acceptor reduction and donor oxidation"
    if completed:
        return False, "completed donor-to-acceptor ET lacks paired role oxidation-state change"
    if oxidation_changed:
        return False, "role oxidation states changed without completed transferred_donor_to_acceptor target"
    return True, "role oxidation states unchanged; admissible for association or bridge preparation"


def bridging_ligand_consistency(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    if t["shared_bridge_status"] == "present":
        if s["acceptor_bridge_bond_status"] not in {"bound_terminal_or_chelated_acceptor", "retained_in_doubly_chelated_bridge"}:
            return False, "bridge formation lacks compatible acceptor-side oxalate binding"
        if s["donor_bridge_bond_status"] not in {"approaching_or_chelation_ready", "doubly_chelated_bridge_coordination_present"}:
            return False, "bridge formation lacks donor-side chelation access"
        if t["bridge_mode"] != "doubly_chelated_bridge":
            return False, "present oxalate bridge requires doubly_chelated_bridge mode"
        if t["acceptor_bridge_bond_status"] != "retained_in_doubly_chelated_bridge":
            return False, "present oxalate bridge requires acceptor bridge retention"
        if t["donor_bridge_bond_status"] != "doubly_chelated_bridge_coordination_present":
            return False, "present oxalate bridge requires donor bridge coordination"
    if t["bridge_ligand_transfer_balance"] == "oxalate_on_donor_product":
        if t["donor_bridge_bond_status"] != "product_chelate_coordination_present":
            return False, "oxalate_on_donor_product requires product chelate coordination"
    disappeared = (
        s["acceptor_bridge_bond_status"] in {"bound_terminal_or_chelated_acceptor", "retained_in_doubly_chelated_bridge"}
        and t["acceptor_bridge_bond_status"] == "released_or_reduced_acceptor_side"
        and t["donor_bridge_bond_status"] == "absent"
        and t["shared_bridge_status"] == "absent"
    )
    if disappeared:
        return False, "oxalate was released from acceptor side without bridge or donor-product chelate"
    return True, "bridging-ligand features are coherent for oxalate bridge or product-chelate representation"


def coordination_consistency(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    if t["bridge_mode"] == "doubly_chelated_bridge":
        if s["center_pair_association_status"] not in {"encounter_associated", "bridged"}:
            return False, "doubly chelated bridge requires associated or bridge-capable source"
        if s["donor_coordination_accessibility"] != "aqua_sites_available_or_exchange_accessible":
            return False, "doubly chelated bridge requires donor coordination accessibility"
        if t["center_pair_association_status"] == "separated":
            return False, "bridged target cannot remain separated"
    if s["center_pair_association_status"] == "product_separated" and t["bridge_mode"] == "doubly_chelated_bridge":
        return False, "product-separated source cannot directly return to doubly chelated bridge without reassociation"
    return True, "coordination and association features support the structural change"


def state_change_coherence(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    changed = [key for key in s if s[key] != t[key]]
    if not changed:
        return False, "no generalized chemical feature changed"
    if s["electron_transfer_balance"] == "transferred_donor_to_acceptor" and t["electron_transfer_balance"] in {"not_transferred", "transfer_candidate"}:
        return False, "comparison would undo completed donor-to-acceptor ET"
    if s["bridge_ligand_transfer_balance"] == "oxalate_on_donor_product" and t["bridge_ligand_transfer_balance"] in {"oxalate_transfer_candidate", "oxalate_on_acceptor", "shared_oxalate_bridge"}:
        return False, "comparison would undo oxalate product-side assignment"
    return True, f"{len(changed)} generalized chemical feature(s) changed; OX01_S3 is optional"


def assess_pair(src: dict[str, Any], tgt: dict[str, Any]) -> dict[str, Any]:
    redox_ok, redox_reason = redox_consistency(src, tgt)
    bridge_ok, bridge_reason = bridging_ligand_consistency(src, tgt)
    coord_ok, coord_reason = coordination_consistency(src, tgt)
    state_ok, state_reason = state_change_coherence(src, tgt)
    admissible = redox_ok and bridge_ok and coord_ok and state_ok
    return {
        "redox_consistent": redox_ok,
        "redox_reason": redox_reason,
        "bridging_ligand_consistent": bridge_ok,
        "bridging_ligand_reason": bridge_reason,
        "coordination_consistent": coord_ok,
        "coordination_reason": coord_reason,
        "state_change_coherent": state_ok,
        "state_change_reason": state_reason,
        "admissible": admissible,
    }


def reverse_external_reasons(src: dict[str, Any], tgt: dict[str, Any], reverse: dict[str, Any]) -> list[str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    if reverse["admissible"]:
        return ["none"]
    reasons = []
    if s["electron_transfer_balance"] == "transferred_donor_to_acceptor" and t["electron_transfer_balance"] in {"not_transferred", "transfer_candidate"}:
        reasons.append("reverse_redox_reagents_or_potential_required")
    if s["center_pair_association_status"] == "product_separated" and t["center_pair_association_status"] in {"dissociating", "bridged", "encounter_associated"}:
        reasons.append("product_reassociation_required")
    if s["bridge_ligand_transfer_balance"] == "oxalate_on_donor_product" and t["bridge_ligand_transfer_balance"] in {"oxalate_transfer_candidate", "shared_oxalate_bridge", "oxalate_on_acceptor"}:
        reasons.append("oxalate_back_transfer_conditions_required")
    if s["donor_coordination_accessibility"] == "not_available_after_donor_oxidation" and t["donor_coordination_accessibility"] == "aqua_sites_available_or_exchange_accessible":
        reasons.append("coordination_reactivation_required")
    return reasons or ["none"]


def classify(forward: bool, reverse: bool, external: bool) -> tuple[str, str]:
    if not forward:
        return "chemically_inadmissible_transition_candidate", "forward_inadmissible"
    if external:
        return "chemically_admissible_transition_candidate", "reverse_requires_external_conditions"
    if reverse:
        return "chemically_admissible_transition_candidate", "admissible_but_direction_not_qualified"
    return "chemically_admissible_transition_candidate", "directionally_asymmetric_under_declared_rules"


def build_results(records: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_id = {record["state_id"]: record for record in records}
    rows = []
    for candidate in candidates:
        src = by_id[candidate["source_state_id"]]
        tgt = by_id[candidate["target_state_id"]]
        forward = assess_pair(src, tgt)
        reverse = assess_pair(tgt, src)
        reasons = reverse_external_reasons(tgt, src, reverse)
        external = reasons != ["none"]
        status, comparison = classify(forward["admissible"], reverse["admissible"], external)
        row = {
            "transition_id": candidate["transition_id"],
            "source_state_id": candidate["source_state_id"],
            "target_state_id": candidate["target_state_id"],
            **{key: forward[key] for key in [
                "redox_consistent", "redox_reason", "bridging_ligand_consistent", "bridging_ligand_reason",
                "coordination_consistent", "coordination_reason", "state_change_coherent", "state_change_reason"
            ]},
            "forward_admissible": forward["admissible"],
            "reverse_admissible": reverse["admissible"],
            "reverse_requires_external_conditions": external,
            "reverse_external_condition_reasons": reasons,
            "forward_transition_status": status,
            "direction_comparison_class": comparison,
            "reverse_rule_results": reverse,
        }
        rows.append(row)
    return rows


def cross_case_transfer_rows() -> list[dict[str, Any]]:
    return [
        {
            "rule_group": "R1 Redox Consistency",
            "chloride_case_form": "CrII_to_CoIII role-paired redox check",
            "oxalate_case_form": "electron_donor_center_to_electron_acceptor_center role-paired redox check",
            "shared_core_description": "Paired donor oxidation and acceptor reduction are required for completed ET.",
            "case_specific_extension_description": "none",
            "transfer_class": "unchanged_transfer",
            "case_specific_patch_required": False,
            "classification_basis": "implemented_rule_structure",
            "reason": "The oxidation-state rule is transferred on donor/acceptor roles.",
        },
        {
            "rule_group": "R2 Bridging-Ligand Consistency",
            "chloride_case_form": "chloride_bridge_consistency",
            "oxalate_case_form": "bridging_ligand_consistency with oxalate chelation fields",
            "shared_core_description": "Bridge formation requires a compatible starting ligand bond, access at the second center, coherent shared-bridge fields, and coherent product-side ligand binding.",
            "case_specific_extension_description": "Oxalate requires chelation-specific bond-state and product-chelate conditions including doubly_chelated_bridge, retained_in_doubly_chelated_bridge, doubly_chelated_bridge_coordination_present, and product_chelate_coordination_present.",
            "transfer_class": "case_specific_extension",
            "case_specific_patch_required": True,
            "classification_basis": "manual_structured_comparison",
            "reason": "The bridge-consistency core transfers, but the oxalate case requires chelation-specific bond-state and product-chelate conditions beyond the chloride implementation.",
        },
        {
            "rule_group": "R3 Coordination and Association Consistency",
            "chloride_case_form": "association and coordination-access check",
            "oxalate_case_form": "association and donor chelation-access check",
            "shared_core_description": "Separated-to-associated-to-bridged progression requires association and coordination accessibility.",
            "case_specific_extension_description": "Oxalate adds chelation-specific coordination-accessibility and bridge-geometry requirements, including aqua_sites_available_or_exchange_accessible for doubly chelated bridge formation.",
            "transfer_class": "case_specific_extension",
            "case_specific_patch_required": True,
            "classification_basis": "manual_structured_comparison",
            "reason": "The coordination/association core transfers, but the oxalate case adds chelation-specific coordination-accessibility and bridge-geometry requirements.",
        },
        {
            "rule_group": "R4 State-Change Coherence",
            "chloride_case_form": "chemical-feature change and optional S3 handling",
            "oxalate_case_form": "generalized chemical-feature change and optional OX01_S3 handling",
            "shared_core_description": "A real chemical-feature change is required; optional post-ET state handling is preserved.",
            "case_specific_extension_description": "none",
            "transfer_class": "unchanged_transfer",
            "case_specific_patch_required": False,
            "classification_basis": "implemented_rule_structure",
            "reason": "The metadata exclusion and optional post-ET state logic are unchanged.",
        },
    ]


def serialize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        item = dict(row)
        item["reverse_external_condition_reasons"] = "|".join(row["reverse_external_condition_reasons"])
        out.append(item)
    return out


def alias_rows(rows: list[dict[str, Any]], alias_bundle: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    amap = {entry["canonical_field_name"]: entry["display_alias"] for entry in alias_bundle["aliases"]}
    columns = [amap.get(column, column) for column in RESULT_COLUMNS]
    out = []
    for row in serialize_rows(rows):
        out.append({display: row[canonical] for canonical, display in zip(RESULT_COLUMNS, columns)})
    return out, columns


def build_summary(records: list[dict[str, Any]], candidates: list[dict[str, Any]], results: list[dict[str, Any]], transfer_rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter(row["direction_comparison_class"] for row in results)
    patch_count = sum(1 for row in transfer_rows if row["case_specific_patch_required"])
    rule_count = len(transfer_rows)
    shared_core_preserved = all(row["transfer_class"] != "not_transferable" for row in transfer_rows)
    if shared_core_preserved and patch_count == 0:
        transfer_assessment = "shared_core_transferred_without_case_specific_patch"
    elif shared_core_preserved and 0 < patch_count < rule_count:
        transfer_assessment = "shared_core_transferred_with_limited_case_specific_extension"
    elif shared_core_preserved and patch_count >= rule_count:
        transfer_assessment = "case_specific_patch_dominant"
    else:
        transfer_assessment = "transfer_inconclusive"
    return {
        "run_id": RUN_ID,
        "case_id": CASE_ID,
        "data_status": "curated_source_bound_candidate_state_data",
        "state_record_count": len(records),
        "transition_candidate_count": len(candidates),
        "forward_admissible_count": sum(1 for row in results if row["forward_admissible"]),
        "forward_inadmissible_count": sum(1 for row in results if not row["forward_admissible"]),
        "bidirectionally_admissible_count": counts["admissible_but_direction_not_qualified"],
        "reverse_external_conditions_count": counts["reverse_requires_external_conditions"],
        "not_assessed_count": counts["not_assessed"],
        "cross_case_comparison_mode": CROSS_CASE_COMPARISON_MODE,
        "automatic_rule_equivalence_analysis_performed": False,
        "formal_rule_equivalence_proven": False,
        "chloride_transition_result_file_used": False,
        "cross_case_transfer_based_on": CROSS_CASE_TRANSFER_BASED_ON,
        "shared_rule_core_preserved": shared_core_preserved,
        "case_specific_patch_required": patch_count > 0,
        "case_specific_patch_count": patch_count,
        "transfer_assessment": transfer_assessment,
        "case_identity_used_as_direction_input": False,
        "localized_aliases_used_as_logic_inputs": False,
        "physical_causality_claimed": False,
        "final_status": FINAL_STATUS,
    }


def build_readout(results: list[dict[str, Any]], transfer_rows: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    forward = [f"{r['transition_id']} {r['source_state_id']} -> {r['target_state_id']}" for r in results if r["forward_admissible"]]
    reverse_ok = [r["transition_id"] for r in results if r["reverse_admissible"]]
    unchanged = [r["rule_group"] for r in transfer_rows if r["transfer_class"] == "unchanged_transfer"]
    extended = [r["rule_group"] for r in transfer_rows if r["transfer_class"] == "case_specific_extension"]
    return "\n".join([
        "# QSB-CAUSALITY06B-06 Readout",
        "",
        "## Befund",
        "",
        "The run evaluated a second independent curated oxalate-bridged inner-sphere ET case.",
        f"Forward-admissible transitions: {', '.join(forward)}.",
        f"Reverse-admissible transition IDs: {', '.join(reverse_ok) if reverse_ok else 'none'}.",
        f"Rules transferred unchanged: {', '.join(unchanged)}.",
        f"Rules requiring limited oxalate/chelation extensions: {', '.join(extended)}.",
        "",
        "## Interpretation",
        "",
        f"Transfer assessment: {summary['transfer_assessment']}. The shared four-rule architecture remains usable, with explicit limited extensions for two rule groups.",
        f"cross_case_comparison_mode = {summary['cross_case_comparison_mode']}",
        "The cross-case comparison is a structured classification of implemented rule forms and declared case-specific conditions.",
        "automatic_rule_equivalence_analysis_performed = false",
        "formal_rule_equivalence_proven = false",
        "",
        "## Hypothese",
        "",
        "The shared donor/acceptor redox and state-change core can be represented with generalized fields for this curated case, while bridge-ligand and coordination checks require explicit oxalate/chelation extensions.",
        "",
        "## Offene Luecke",
        "",
        "The records are not raw measurements and do not resolve every intermediate state.",
        "",
        "## Claim Boundary",
        "",
        "Rule transfer across two cases does not establish universal generalizability. No automatic rule equivalence was proven. Formal admissibility does not establish thermodynamic favorability, kinetic accessibility, irreversibility, or physical causality. Localized aliases are presentation metadata only.",
        "",
        f"final_status = {summary['final_status']}",
        "",
    ])


def run(args: argparse.Namespace) -> None:
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            raise RunError(f"output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "state_records": input_root / "data/QSB-CAUSALITY06B-06/oxalate_case_state_records.json",
        "transition_candidates": input_root / "data/QSB-CAUSALITY06B-06/oxalate_transition_candidates.json",
        "field_aliases_de": input_root / "data/QSB-CAUSALITY06B-06/field_aliases_de.json",
        "source_inventory": input_root / "data/QSB-CAUSALITY06B-06/source_inventory.md",
    }
    state_bundle = load_json(paths["state_records"])
    candidate_bundle = load_json(paths["transition_candidates"])
    alias_bundle = load_json(paths["field_aliases_de"])
    records = validate_records(state_bundle)
    candidates = validate_candidates(candidate_bundle)
    results = build_results(records, candidates)
    transfer_rows = cross_case_transfer_rows()
    summary = build_summary(records, candidates, results, transfer_rows)
    resolved = {
        "run_id": RUN_ID,
        "case_id": CASE_ID,
        "data_status": "curated_source_bound_candidate_state_data",
        "cross_case_comparison_mode": CROSS_CASE_COMPARISON_MODE,
        "automatic_rule_equivalence_analysis_performed": False,
        "formal_rule_equivalence_proven": False,
        "chloride_transition_result_file_used": False,
        "cross_case_transfer_based_on": CROSS_CASE_TRANSFER_BASED_ON,
        "rule_groups": ["R1 Redox Consistency", "R2 Bridging-Ligand Consistency", "R3 Coordination and Association Consistency", "R4 State-Change Coherence"],
        "validation_mode": "internal_schema_constraint_subset",
        "internal_validation_passed": True,
        "full_jsonschema_validation_performed": False,
        "validation_scope": ["required_generalized_chemical_fields", "state_id_coverage", "OX01_S3_optionality", "bridge_ligand_consistency_constraints"],
        "leakage_flags": {
            "reference_order_used_as_direction_input": False,
            "evidence_metadata_used_as_direction_input": False,
            "descriptive_labels_used_as_direction_input": False,
            "case_identity_used_as_direction_input": False,
            "localized_aliases_used_as_logic_inputs": False,
        },
        "source_files": {key: str(value) for key, value in paths.items()},
    }
    write_json(output_dir / "resolved_config.json", resolved)
    write_json(output_dir / "validated_oxalate_state_records.json", {"records": records})
    write_csv(output_dir / "oxalate_transition_results.csv", serialize_rows(results), RESULT_COLUMNS)
    write_json(output_dir / "oxalate_transition_results.json", {"run_id": RUN_ID, "transition_results": results})
    write_csv(
        output_dir / "cross_case_rule_transfer.csv",
        transfer_rows,
        [
            "rule_group",
            "chloride_case_form",
            "oxalate_case_form",
            "shared_core_description",
            "case_specific_extension_description",
            "transfer_class",
            "case_specific_patch_required",
            "classification_basis",
            "reason",
        ],
    )
    german_rows, german_columns = alias_rows(results, alias_bundle)
    write_csv(output_dir / "german_alias_view.csv", german_rows, german_columns)
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(build_readout(results, transfer_rows, summary), encoding="utf-8")
    actual = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual != sorted(OUTPUT_FILES):
        raise RunError(f"output file set mismatch: {actual}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".", help="Repository root containing data/ and runs/.")
    parser.add_argument("--output-dir", default="runs/QSB-CAUSALITY06B-06/second_inner_sphere_case", help="Output directory for eight run files.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output directory.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        run(args)
    except RunError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
