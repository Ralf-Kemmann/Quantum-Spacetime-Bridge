#!/usr/bin/env python3
"""Run QSB-CAUSALITY06B-04 inner-sphere ET admissibility checks."""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any


RUN_ID = "QSB-CAUSALITY06B-04_first_inner_sphere_et_admissibility"
FINAL_STATUS = "first_inner_sphere_et_admissibility_run_completed"
RULE_GROUPS = [
    "R1 Redox Consistency",
    "R2 Chloride and Bridge Consistency",
    "R3 Coordination and Association Consistency",
    "R4 State-Change Coherence",
]
OUTPUT_FILES = [
    "resolved_config.json",
    "validated_state_records.json",
    "transition_results.csv",
    "transition_results.json",
    "direction_comparison_summary.csv",
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
    "chloride_bridge_consistent",
    "chloride_bridge_reason",
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
    "reverse_assessment",
]
VALIDATION_MODE = "internal_schema_constraint_subset"
INTERNAL_VALIDATION_SCOPE = [
    "required_run_fields",
    "state_id_coverage",
    "selected_controlled_vocabularies",
    "selected_cross_field_constraints",
    "IS01_S2_bridge_constraints",
    "IS01_S3_optionality_constraints",
    "IS01_S4_product_constraints",
]
INTERNAL_VALIDATION_DOES_NOT_COVER = [
    "complete_draft_2020_12_semantics",
    "all_nested_required_constraints",
    "all_additional_properties_constraints",
    "all_conditional_schema_branches",
    "complete_metadata_validation",
]
DATA_STATUS_FLAGS = {
    "data_status": "curated_source_bound_candidate_state_data",
    "raw_experimental_measurement_data": False,
    "directly_time_resolved_trajectory": False,
    "mechanistic_reference_decomposition": True,
}


class RunError(RuntimeError):
    """Raised for input, validation, or output failures."""


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


def schema_enums(schema: dict[str, Any], def_name: str) -> dict[str, set[Any]]:
    properties = schema["$defs"][def_name]["properties"]
    return {
        key: set(value["enum"])
        for key, value in properties.items()
        if isinstance(value, dict) and "enum" in value
    }


def validate_state_bundle(bundle: dict[str, Any], schema: dict[str, Any]) -> list[dict[str, Any]]:
    records = bundle.get("records")
    if not isinstance(records, list):
        raise RunError("state record bundle must contain a records array")
    if len(records) != 5:
        raise RunError(f"expected 5 state records, found {len(records)}")

    expected_ids = {"IS01_S0", "IS01_S1", "IS01_S2", "IS01_S3", "IS01_S4"}
    observed_ids = {record.get("state_id") for record in records}
    if observed_ids != expected_ids:
        raise RunError(f"state_id set mismatch: {sorted(observed_ids)}")

    root_required = set(schema["required"])
    schema_projection = {key: bundle.get(key) for key in root_required}
    schema_projection["records"] = records
    for key in root_required:
        if key not in schema_projection or schema_projection[key] is None:
            raise RunError(f"schema-required root key missing: {key}")

    record_schema = schema["$defs"]["candidate_state_record"]
    record_allowed = set(record_schema["properties"])
    record_required = set(record_schema["required"])
    chemical_enums = schema_enums(schema, "chemical_features")
    species_enums = schema_enums(schema, "species_status")
    pathway_enums = schema_enums(schema, "pathway_evidence")

    for record in records:
        unknown_keys = set(record) - record_allowed
        if unknown_keys:
            raise RunError(f"{record.get('state_id')}: unexpected record keys {sorted(unknown_keys)}")
        missing = record_required - set(record)
        if missing:
            raise RunError(f"{record.get('state_id')}: missing required keys {sorted(missing)}")

        cf = record["chemical_features"]
        for key, allowed in chemical_enums.items():
            if cf.get(key) not in allowed:
                raise RunError(f"{record['state_id']}: invalid chemical_features.{key}")

        species = record["species_status"]
        for key, allowed in species_enums.items():
            if species.get(key) not in allowed:
                raise RunError(f"{record['state_id']}: invalid species_status.{key}")

        evidence = record["pathway_evidence"]
        for key, allowed in pathway_enums.items():
            if evidence.get(key) not in allowed:
                raise RunError(f"{record['state_id']}: invalid pathway_evidence.{key}")

        leakage = record["leakage_controls"]
        for key, value in leakage.items():
            if key == "chemical_features_as_future_direction_inputs_potentially_allowed":
                expected = True
            elif key == "future_use_requires_separate_admissibility_specification":
                expected = True
            else:
                expected = False
            if value is not expected:
                raise RunError(f"{record['state_id']}: leakage control {key} is not {expected}")

        validate_cross_field(record)

    return records


def validate_cross_field(record: dict[str, Any]) -> None:
    state_id = record["state_id"]
    cf = record["chemical_features"]

    if cf["shared_chloride_bridge_status"] == "present":
        if cf["co_chloride_bond_status"] != "retained_in_bridged_configuration":
            raise RunError(f"{state_id}: present bridge without retained Co-Cl")
        if cf["cr_chloride_bond_status"] != "bridge_coordination_present":
            raise RunError(f"{state_id}: present bridge without Cr bridge coordination")

    if cf["electron_transfer_balance"] == "transferred_Cr_to_Co":
        if cf["co_oxidation_state"] != "+2" or cf["cr_oxidation_state"] != "+3":
            raise RunError(f"{state_id}: transferred ET without paired oxidation states")

    if cf["ligand_transfer_balance"] == "chloride_on_Cr":
        if cf["cr_chloride_bond_status"] not in {"bound_terminal_product", "bridge_coordination_present"}:
            raise RunError(f"{state_id}: chloride_on_Cr without Cr-Cl bond")

    if state_id == "IS01_S3":
        controls = record.get("optional_state_controls", {})
        if record["state_representation_status"] != "optional_formal_state":
            raise RunError("IS01_S3: state_representation_status must be optional_formal_state")
        if record["reference_order_metadata"]["included_in_full_reference_path"] is not True:
            raise RunError("IS01_S3: full reference path inclusion must be true")
        if record["reference_order_metadata"]["included_in_minimal_reference_path"] is not False:
            raise RunError("IS01_S3: minimal reference path inclusion must be false")
        if controls.get("IS01_S3_required_as_discrete_species") is not False:
            raise RunError("IS01_S3: required-as-discrete-species flag must be false")
        if controls.get("post_et_bridge_persistence_required") is not False:
            raise RunError("IS01_S3: post-ET bridge persistence flag must be false")


def validate_candidates(bundle: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = bundle.get("transition_candidates")
    if not isinstance(candidates, list):
        raise RunError("transition candidate bundle must contain transition_candidates")
    if len(candidates) != 5:
        raise RunError(f"expected 5 transition candidates, found {len(candidates)}")
    required = {
        "transition_id",
        "source_state_id",
        "target_state_id",
        "candidate_role",
        "included_in_full_reference_path",
        "included_in_minimal_reference_path",
        "reference_order_metadata_only",
    }
    for candidate in candidates:
        missing = required - set(candidate)
        if missing:
            raise RunError(f"{candidate.get('transition_id')}: missing candidate keys {sorted(missing)}")
        if candidate["reference_order_metadata_only"] is not True:
            raise RunError(f"{candidate['transition_id']}: reference_order_metadata_only must be true")
    return candidates


def redox_consistency(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    oxidation_changed = (
        s["co_oxidation_state"] != t["co_oxidation_state"]
        or s["cr_oxidation_state"] != t["cr_oxidation_state"]
    )
    completed = t["electron_transfer_balance"] == "transferred_Cr_to_Co"
    paired_forward = (
        s["co_oxidation_state"] == "+3"
        and s["cr_oxidation_state"] == "+2"
        and t["co_oxidation_state"] == "+2"
        and t["cr_oxidation_state"] == "+3"
    )
    paired_unchanged_product = (
        s["co_oxidation_state"] == "+2"
        and s["cr_oxidation_state"] == "+3"
        and t["co_oxidation_state"] == "+2"
        and t["cr_oxidation_state"] == "+3"
        and completed
    )
    if completed and (paired_forward or paired_unchanged_product):
        return True, "completed Cr-to-Co ET is paired with CoIII/CrII to CoII/CrIII or retained product-side oxidation states"
    if completed and not (paired_forward or paired_unchanged_product):
        return False, "completed ET is not paired with the declared Co and Cr oxidation-state pattern"
    if oxidation_changed:
        return False, "oxidation states changed without a completed transferred_Cr_to_Co target state"
    if t["electron_transfer_balance"] == "transfer_candidate":
        return True, "oxidation states unchanged; transfer_candidate is admissible for bridge-mediated preparation"
    return True, "oxidation states unchanged; admissible for association, bridge, or separation-only step"


def chloride_bridge_consistency(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    if t["shared_chloride_bridge_status"] == "present":
        if s["co_chloride_bond_status"] not in {"bound_terminal", "retained_in_bridged_configuration"}:
            return False, "bridge target lacks a compatible source Co-Cl position"
        if s["cr_chloride_bond_status"] not in {"approaching_or_substitution_ready", "bridge_coordination_present"}:
            return False, "bridge formation lacks Cr coordination access"
        if t["co_chloride_bond_status"] != "retained_in_bridged_configuration":
            return False, "present bridge requires retained Co-Cl configuration"
        if t["cr_chloride_bond_status"] != "bridge_coordination_present":
            return False, "present bridge requires Cr bridge coordination"

    if t["ligand_transfer_balance"] == "chloride_on_Cr":
        if t["cr_chloride_bond_status"] not in {"bound_terminal_product", "bridge_coordination_present"}:
            return False, "chloride_on_Cr target lacks Cr-Cl bonding"

    chloride_disappeared = (
        s["co_chloride_bond_status"] in {"bound_terminal", "retained_in_bridged_configuration"}
        and t["co_chloride_bond_status"] in {"released", "absent"}
        and t["cr_chloride_bond_status"] == "absent"
        and t["shared_chloride_bridge_status"] == "absent"
    )
    if chloride_disappeared:
        return False, "chloride was removed from Co without bridge or Cr-Cl product representation"

    if (
        t["co_chloride_bond_status"] == "bound_terminal"
        and t["cr_chloride_bond_status"] == "bound_terminal_product"
    ):
        return False, "terminal chloride cannot be fully terminal on both centers"

    return True, "chloride, bridge, and Cr-Cl target features are mutually coherent"


def coordination_consistency(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    if t["shared_chloride_bridge_status"] == "present":
        if s["metal_pair_association_status"] not in {"encounter_associated", "bridged"}:
            return False, "bridge target requires prior association or bridge-capable source state"
        if s["cr_coordination_vacancy_or_substitution_readiness"] not in {
            "substitution_ready",
            "vacancy_available_or_exchange_accessible",
        }:
            return False, "bridge target lacks CrII substitution access in source features"
        if t["metal_pair_association_status"] == "separated":
            return False, "bridged target cannot remain separated"

    if s["metal_pair_association_status"] == "product_separated" and t["shared_chloride_bridge_status"] == "present":
        return False, "product-separated source cannot directly form a bridge without modeled reassociation"

    if (
        s["metal_pair_association_status"] == "product_separated"
        and t["metal_pair_association_status"] in {"dissociating", "bridged"}
    ):
        return False, "product-separated source cannot jump back to associated post-transfer state in this record pair"

    return True, "association and coordination-access features support the declared structural change"


def state_change_coherence(src: dict[str, Any], tgt: dict[str, Any]) -> tuple[bool, str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    changed = [key for key in sorted(s) if s[key] != t[key]]
    if not changed:
        return False, "no chemical_features changed"
    if (
        s["electron_transfer_balance"] == "transferred_Cr_to_Co"
        and t["electron_transfer_balance"] in {"not_transferred", "transfer_candidate"}
    ):
        return False, "comparison would undo completed ET within the declared two-record transition"
    if (
        s["ligand_transfer_balance"] == "chloride_on_Cr"
        and t["ligand_transfer_balance"] in {"chloride_on_Co", "shared_bridge"}
    ):
        return False, "comparison would undo chloride transfer within the declared two-record transition"
    return True, f"{len(changed)} chemical feature(s) changed coherently; IS01_S3 is not required"


def assess_pair(src: dict[str, Any], tgt: dict[str, Any]) -> dict[str, Any]:
    redox_ok, redox_reason = redox_consistency(src, tgt)
    chloride_ok, chloride_reason = chloride_bridge_consistency(src, tgt)
    coordination_ok, coordination_reason = coordination_consistency(src, tgt)
    state_ok, state_reason = state_change_coherence(src, tgt)
    admissible = redox_ok and chloride_ok and coordination_ok and state_ok
    return {
        "redox_consistent": redox_ok,
        "redox_reason": redox_reason,
        "chloride_bridge_consistent": chloride_ok,
        "chloride_bridge_reason": chloride_reason,
        "coordination_consistent": coordination_ok,
        "coordination_reason": coordination_reason,
        "state_change_coherent": state_ok,
        "state_change_reason": state_reason,
        "admissible": admissible,
    }


def reverse_external_condition_reasons(
    src: dict[str, Any], tgt: dict[str, Any], reverse_result: dict[str, Any]
) -> list[str]:
    s = src["chemical_features"]
    t = tgt["chemical_features"]
    if reverse_result["admissible"]:
        return ["none"]
    reasons = []
    product_to_pre_et = (
        s["electron_transfer_balance"] == "transferred_Cr_to_Co"
        and t["electron_transfer_balance"] in {"not_transferred", "transfer_candidate"}
    )
    if product_to_pre_et:
        reasons.append("reverse_redox_reagents_or_potential_required")

    product_reassociation = (
        s["metal_pair_association_status"] == "product_separated"
        and t["metal_pair_association_status"] in {"dissociating", "bridged", "encounter_associated"}
    )
    if product_reassociation:
        reasons.append("product_reassociation_required")

    chloride_back_transfer = (
        s["ligand_transfer_balance"] == "chloride_on_Cr"
        and t["ligand_transfer_balance"] in {"chloride_transfer_candidate", "shared_bridge", "chloride_on_Co"}
    )
    if chloride_back_transfer:
        reasons.append("chloride_back_transfer_conditions_required")

    coordination_reactivation = (
        s["cr_coordination_vacancy_or_substitution_readiness"] == "not_available"
        and t["cr_coordination_vacancy_or_substitution_readiness"]
        in {"substitution_ready", "vacancy_available_or_exchange_accessible"}
    )
    if coordination_reactivation:
        reasons.append("coordination_reactivation_required")

    return reasons or ["none"]


def classify_result(forward: bool, reverse: bool, external: bool) -> tuple[str, str]:
    if not forward:
        return "chemically_inadmissible_transition_candidate", "forward_inadmissible"
    if external:
        return "chemically_admissible_transition_candidate", "reverse_requires_external_conditions"
    if reverse:
        return "chemically_admissible_transition_candidate", "admissible_but_direction_not_qualified"
    return "chemically_admissible_transition_candidate", "directionally_asymmetric_under_declared_rules"


def reverse_assessment(reverse: bool, external: bool) -> str:
    if reverse:
        return "reverse_chemically_admissible_under_declared_rules"
    if external:
        return "reverse_requires_external_reagents_or_conditions"
    return "reverse_chemically_inadmissible_under_declared_rules"


def build_results(records: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_state_id = {record["state_id"]: record for record in records}
    results = []
    for candidate in candidates:
        source = by_state_id[candidate["source_state_id"]]
        target = by_state_id[candidate["target_state_id"]]
        forward = assess_pair(source, target)
        reverse = assess_pair(target, source)
        external_reasons = reverse_external_condition_reasons(target, source, reverse)
        external = external_reasons != ["none"]
        forward_status, comparison_class = classify_result(forward["admissible"], reverse["admissible"], external)
        row = {
            "transition_id": candidate["transition_id"],
            "source_state_id": candidate["source_state_id"],
            "target_state_id": candidate["target_state_id"],
            "redox_consistent": forward["redox_consistent"],
            "redox_reason": forward["redox_reason"],
            "chloride_bridge_consistent": forward["chloride_bridge_consistent"],
            "chloride_bridge_reason": forward["chloride_bridge_reason"],
            "coordination_consistent": forward["coordination_consistent"],
            "coordination_reason": forward["coordination_reason"],
            "state_change_coherent": forward["state_change_coherent"],
            "state_change_reason": forward["state_change_reason"],
            "forward_admissible": forward["admissible"],
            "reverse_admissible": reverse["admissible"],
            "reverse_requires_external_conditions": external,
            "reverse_external_condition_reasons": external_reasons,
            "forward_transition_status": forward_status,
            "direction_comparison_class": comparison_class,
            "reverse_assessment": reverse_assessment(reverse["admissible"], external),
            "reverse_rule_results": reverse,
            "reference_order_metadata_only": candidate["reference_order_metadata_only"],
        }
        results.append(row)
    return results


def build_alias_rows(results: list[dict[str, Any]], alias_bundle: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    alias_map = {
        item["canonical_field_name"]: item["display_alias"]
        for item in alias_bundle["aliases"]
    }
    localized_columns = [alias_map.get(column, column) for column in RESULT_COLUMNS]
    rows = []
    for result in results:
        localized = {}
        for canonical, display in zip(RESULT_COLUMNS, localized_columns):
            value = result[canonical]
            if isinstance(value, list):
                value = "|".join(value)
            localized[display] = value
        rows.append(localized)
    return rows, localized_columns


def build_summary(results: list[dict[str, Any]], records: list[dict[str, Any]], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    comparison_counts = Counter(result["direction_comparison_class"] for result in results)
    status_counts = Counter(result["forward_transition_status"] for result in results)
    return {
        "run_id": RUN_ID,
        **DATA_STATUS_FLAGS,
        "state_record_count": len(records),
        "transition_candidate_count": len(candidates),
        "validation_mode": VALIDATION_MODE,
        "internal_validation_passed": True,
        "full_jsonschema_validation_performed": False,
        "full_jsonschema_validation_passed": "not_applicable",
        "internal_validation_scope": INTERNAL_VALIDATION_SCOPE,
        "internal_validation_does_not_cover": INTERNAL_VALIDATION_DOES_NOT_COVER,
        "forward_admissible_count": sum(1 for result in results if result["forward_admissible"]),
        "forward_inadmissible_count": sum(1 for result in results if not result["forward_admissible"]),
        "directionally_asymmetric_count": comparison_counts["directionally_asymmetric_under_declared_rules"],
        "bidirectionally_admissible_count": comparison_counts["admissible_but_direction_not_qualified"],
        "reverse_external_conditions_count": comparison_counts["reverse_requires_external_conditions"],
        "not_assessed_count": comparison_counts["not_assessed"] + status_counts["not_assessed"],
        "physical_causality_claimed": False,
        "formal_directional_asymmetry_is_physical_causality": False,
        "formal_directional_asymmetry_is_thermodynamic_irreversibility": False,
        "formal_directional_asymmetry_is_kinetic_inaccessibility": False,
        "IS01_S3_required_as_discrete_species": False,
        "localized_aliases_used_as_logic_inputs": False,
        "final_status": FINAL_STATUS,
    }


def build_readout(results: list[dict[str, Any]], summary: dict[str, Any]) -> str:
    admissible = [f"{r['transition_id']} {r['source_state_id']} -> {r['target_state_id']}" for r in results if r["forward_admissible"]]
    reverse_ok = [r["transition_id"] for r in results if r["reverse_admissible"]]
    reverse_external = [r["transition_id"] for r in results if r["reverse_requires_external_conditions"]]
    not_assessed = [r["transition_id"] for r in results if r["direction_comparison_class"] == "not_assessed"]
    lines = [
        "# QSB-CAUSALITY06B-04 Readout",
        "",
        "## Befund",
        "",
        "The runner assessed five declared inner-sphere ET transition candidates and their reverse comparisons under the four CAUSALITY06B-03 rule groups.",
        "The run used an internal validator covering the declared run-critical subset of schema constraints. A complete Draft 2020-12 JSON Schema validation was not performed because the required validator package was unavailable in the active environment.",
        "The input records are curated, source-bound candidate-state data derived from documented species, product and tracer evidence, and mechanistic interpretation. They are not raw experimental measurements and do not constitute a directly time-resolved trajectory.",
        "",
        f"Forward-admissible transitions: {', '.join(admissible) if admissible else 'none'}.",
        f"Reverse-admissible transition IDs: {', '.join(reverse_ok) if reverse_ok else 'none'}.",
        f"Reverse comparisons requiring external conditions: {', '.join(reverse_external) if reverse_external else 'none'}.",
        f"Not-assessed transition IDs: {', '.join(not_assessed) if not_assessed else 'none'}.",
        "",
        "## Interpretation",
        "",
        "The results describe internal chemical consistency under declared record features and rules only.",
        "",
        "## Hypothese",
        "",
        "The source-bound state decomposition remains usable as a constrained test case for a later audited admissibility workflow.",
        "",
        "## Offene Luecke",
        "",
        "The records are not a directly observed frame-by-frame trajectory, and no independent causal reconstruction is performed.",
        "",
        "## Claim Boundary",
        "",
        "Formal admissibility does not establish thermodynamic favorability. Formal admissibility does not establish kinetic accessibility. Formal directional asymmetry does not establish physical causality. IS01_S3 remains optional. Localized aliases are presentation metadata only.",
        "",
        f"final_status = {summary['final_status']}",
    ]
    return "\n".join(lines) + "\n"


def run(args: argparse.Namespace) -> None:
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    if output_dir.exists():
        if not args.overwrite:
            raise RunError(f"output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "schema": input_root / "data/QSB-CAUSALITY06B-02/candidate_state_record_schema.json",
        "state_records": input_root / "data/QSB-CAUSALITY06B-04/inner_sphere_et_state_records.json",
        "transition_candidates": input_root / "data/QSB-CAUSALITY06B-04/transition_candidates.json",
        "field_aliases_de": input_root / "data/QSB-CAUSALITY06B-04/field_aliases_de.json",
        "source_inventory": input_root / "data/QSB-CAUSALITY06B-04/source_inventory.md",
    }

    schema = load_json(paths["schema"])
    state_bundle = load_json(paths["state_records"])
    candidate_bundle = load_json(paths["transition_candidates"])
    alias_bundle = load_json(paths["field_aliases_de"])

    if alias_bundle.get("localized_aliases_used_as_logic_inputs") is not False:
        raise RunError("alias bundle must declare localized_aliases_used_as_logic_inputs = false")

    records = validate_state_bundle(state_bundle, schema)
    candidates = validate_candidates(candidate_bundle)
    results = build_results(records, candidates)
    summary = build_summary(results, records, candidates)

    resolved_config = {
        "run_id": RUN_ID,
        **DATA_STATUS_FLAGS,
        "input_paths": {key: str(value) for key, value in paths.items()},
        "schema_version": state_bundle.get("schema_version"),
        "validation_mode": VALIDATION_MODE,
        "internal_validation_passed": True,
        "full_jsonschema_validation_performed": False,
        "full_jsonschema_validation_passed": "not_applicable",
        "internal_validation_scope": INTERNAL_VALIDATION_SCOPE,
        "internal_validation_does_not_cover": INTERNAL_VALIDATION_DOES_NOT_COVER,
        "rule_group_names": RULE_GROUPS,
        "leakage_flags": {
            "reference_order_used_as_direction_input": False,
            "evidence_metadata_used_as_direction_input": False,
            "descriptive_labels_used_as_direction_input": False,
            "localized_aliases_used_as_logic_inputs": False,
        },
        "alias_view": {
            "language_code": alias_bundle["language_code"],
            "view_name": alias_bundle["view_name"],
            "canonical_field_names_remain_language_neutral": alias_bundle["canonical_field_names_remain_language_neutral"],
            "schema_change_required_for_new_language": alias_bundle["schema_change_required_for_new_language"],
        },
        "formal_directional_asymmetry_is_physical_causality": False,
        "formal_directional_asymmetry_is_thermodynamic_irreversibility": False,
        "formal_directional_asymmetry_is_kinetic_inaccessibility": False,
    }

    write_json(output_dir / "resolved_config.json", resolved_config)
    write_json(output_dir / "validated_state_records.json", {"records": records})
    csv_results = []
    for result in results:
        csv_row = dict(result)
        csv_row["reverse_external_condition_reasons"] = "|".join(result["reverse_external_condition_reasons"])
        csv_results.append(csv_row)
    write_csv(output_dir / "transition_results.csv", csv_results, RESULT_COLUMNS)
    write_json(output_dir / "transition_results.json", {"run_id": RUN_ID, "transition_results": results})

    grouped = Counter((r["forward_transition_status"], r["direction_comparison_class"]) for r in results)
    summary_rows = [
        {
            "forward_transition_status": status,
            "direction_comparison_class": klass,
            "count": count,
        }
        for (status, klass), count in sorted(grouped.items())
    ]
    write_csv(
        output_dir / "direction_comparison_summary.csv",
        summary_rows,
        ["forward_transition_status", "direction_comparison_class", "count"],
    )

    alias_rows, alias_columns = build_alias_rows(results, alias_bundle)
    write_csv(output_dir / "german_alias_view.csv", alias_rows, alias_columns)
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(build_readout(results, summary), encoding="utf-8")

    actual_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_outputs != sorted(OUTPUT_FILES):
        raise RunError(f"output file set mismatch: {actual_outputs}")

    if summary["final_status"] != FINAL_STATUS:
        raise RunError("final status mismatch")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".", help="Repository root containing data/ and docs/.")
    parser.add_argument(
        "--output-dir",
        default="runs/QSB-CAUSALITY06B-04/first_inner_sphere_et_admissibility",
        help="Output directory for the eight run artifacts.",
    )
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
