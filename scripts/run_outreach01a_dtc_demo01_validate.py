#!/usr/bin/env python3
"""Validate OUTREACH01A-DTC-DEMO01 synthetic state-identity records."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path


OUTPUT_FILES = [
    "validated_records.json",
    "validation_results.csv",
    "german_alias_view.csv",
    "demonstrator_summary.json",
    "readout.md",
    "compact_contact_table.md",
]

REQUIRED_IDS = ["DTC_A", "DTC_B", "BOUNDARY_AB"]
VALIDATION_MODE = "internal_schema_constraint_subset"
FULL_JSONSCHEMA_VALIDATION_PERFORMED = False
FULL_JSONSCHEMA_VALIDATION_PASSED = "not_applicable"


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path.name for path in output_dir.iterdir() if path.is_file()]
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output dir: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")


def validate_with_jsonschema(schema: dict, records_payload: dict) -> tuple[str, bool, list[str]]:
    _schema = schema
    valid, messages = subset_schema_validate(records_payload)
    return VALIDATION_MODE, valid, messages


def subset_schema_validate(records_payload: dict) -> tuple[bool, list[str]]:
    messages: list[str] = []
    required_top = [
        "demonstrator_id",
        "data_status",
        "models_reported_laser_experiment",
        "experimental_data_used",
        "physical_prediction_present",
        "time_crystal_mechanism_explained",
        "contact_message_present",
        "contact_sent",
        "records",
    ]
    for field in required_top:
        if field not in records_payload:
            messages.append(f"missing top-level field: {field}")
    if not isinstance(records_payload.get("records"), list):
        messages.append("records is not a list")
        return False, messages

    required_record_fields = [
        "record_id",
        "record_type",
        "state_class",
        "dynamic_equivalence_class",
        "temporal_phase_offset",
        "drive_period_units",
        "domain_id",
        "boundary_role",
        "observable_signature",
        "observable_similarity",
        "full_state_identity",
        "equivalence_basis",
        "uncertainty_status",
        "evidence_status",
        "demonstrator_controls",
    ]
    for record in records_payload["records"]:
        for field in required_record_fields:
            if field not in record:
                messages.append(f"{record.get('record_id', '<unknown>')}: missing {field}")
    return not messages, messages


def record_map(records_payload: dict) -> dict:
    return {record["record_id"]: record for record in records_payload["records"]}


def check_cross_record_rules(records_payload: dict) -> tuple[bool, list[str], dict]:
    messages: list[str] = []
    records = records_payload["records"]
    by_id = record_map(records_payload)
    if len(records) != 3:
        messages.append("record_count != 3")
    if sorted(by_id) != sorted(REQUIRED_IDS):
        messages.append("required record ids do not match DTC_A, DTC_B, BOUNDARY_AB")

    a = by_id.get("DTC_A")
    b = by_id.get("DTC_B")
    boundary = by_id.get("BOUNDARY_AB")
    if a and b:
        if a["state_class"] != b["state_class"]:
            messages.append("DTC_A and DTC_B do not share state_class")
        if a["dynamic_equivalence_class"] != b["dynamic_equivalence_class"]:
            messages.append("DTC_A and DTC_B do not share dynamic_equivalence_class")
        if a["record_id"] == b["record_id"]:
            messages.append("DTC_A and DTC_B have same record_id")
        if a["domain_id"] == b["domain_id"]:
            messages.append("DTC_A and DTC_B have same domain_id")
        if b["drive_period_units"] - a["drive_period_units"] != 1:
            messages.append("drive_period_units shift is not exactly 1")
        if b["temporal_phase_offset"] - a["temporal_phase_offset"] != 1:
            messages.append("temporal_phase_offset shift is not exactly 1")
    if boundary:
        if boundary["record_type"] != "boundary_configuration":
            messages.append("BOUNDARY_AB is not boundary_configuration")
        if not ("DOMAIN_A" in boundary["domain_id"] and "DOMAIN_B" in boundary["domain_id"]):
            messages.append("BOUNDARY_AB domain_id does not reference DOMAIN_A and DOMAIN_B")
        if boundary["boundary_role"] == "none":
            messages.append("BOUNDARY_AB boundary_role is none")
        if boundary["dynamic_equivalence_class"] == "DTC_EQ_CLASS_01":
            messages.append("BOUNDARY_AB assigned to DTC_EQ_CLASS_01")

    controls = records_payload.get("leakage_controls", {})
    if controls.get("target_group_identity_used_as_logic_input") is not False:
        messages.append("target_group_identity_used_as_logic_input is not false")
    if controls.get("localized_aliases_used_as_logic_inputs") is not False:
        messages.append("localized_aliases_used_as_logic_inputs is not false")
    if controls.get("preferred_boundary_representation_forced") is not False:
        messages.append("preferred_boundary_representation_forced is not false")

    facts = {
        "record_count": len(records),
        "state_configuration_count": sum(1 for record in records if record["record_type"] == "state_configuration"),
        "boundary_configuration_count": sum(1 for record in records if record["record_type"] == "boundary_configuration"),
        "dynamic_equivalence_pair_present": bool(a and b and a["dynamic_equivalence_class"] == b["dynamic_equivalence_class"]),
        "one_drive_period_phase_shift_present": bool(a and b and b["drive_period_units"] - a["drive_period_units"] == 1 and b["temporal_phase_offset"] - a["temporal_phase_offset"] == 1),
        "distinct_domains_present": bool(a and b and a["domain_id"] != b["domain_id"]),
        "separate_boundary_record_present": bool(boundary and boundary["record_type"] == "boundary_configuration"),
        "preferred_boundary_representation_forced": controls.get("preferred_boundary_representation_forced"),
    }
    return not messages, messages, facts


def per_record_results(records_payload: dict, schema_valid: bool, cross_valid: bool, validation_mode: str, messages: list[str]) -> list[dict]:
    message_text = "passed" if not messages else "; ".join(messages)
    internal_validation_passed = schema_valid and cross_valid
    return [
        {
            "record_id": record["record_id"],
            "schema_valid": str(schema_valid).lower(),
            "cross_record_valid": str(cross_valid).lower(),
            "validation_mode": validation_mode,
            "internal_validation_passed": str(internal_validation_passed).lower(),
            "full_jsonschema_validation_performed": str(FULL_JSONSCHEMA_VALIDATION_PERFORMED).lower(),
            "full_jsonschema_validation_passed": FULL_JSONSCHEMA_VALIDATION_PASSED,
            "validation_messages": message_text,
        }
        for record in records_payload["records"]
    ]


def display_value(field: str, value: object, aliases: dict) -> str:
    value_aliases = aliases.get("value_aliases", {})
    value_text = str(value)
    alias = value_aliases.get(field, {}).get(value_text)
    if alias is None:
        return value_text
    return f"{alias} (`{value_text}`)"


def make_alias_view(records: list[dict], aliases: dict) -> tuple[list[dict], list[str]]:
    alias_map = aliases["aliases"]
    fields = [
        "record_id",
        "record_type",
        "state_class",
        "dynamic_equivalence_class",
        "temporal_phase_offset",
        "drive_period_units",
        "domain_id",
        "boundary_role",
        "observable_signature",
        "observable_similarity",
        "full_state_identity",
        "equivalence_basis",
        "uncertainty_status",
        "evidence_status",
    ]
    headers = [alias_map[field] for field in fields]
    rows = []
    for record in records:
        rows.append({alias_map[field]: display_value(field, record[field], aliases) for field in fields})
    return rows, headers


def make_readout(summary: dict) -> str:
    return "\n".join(
        [
            "# OUTREACH01A-DTC-DEMO01 Readout",
            "",
            "## Befund",
            "",
            f"- Final status: `{summary['final_status']}`.",
            f"- Record count: `{summary['record_count']}`.",
            f"- Dynamic equivalence pair present: `{str(summary['dynamic_equivalence_pair_present']).lower()}`.",
            f"- One drive-period phase shift present: `{str(summary['one_drive_period_phase_shift_present']).lower()}`.",
            f"- Separate boundary record present: `{str(summary['separate_boundary_record_present']).lower()}`.",
            f"- Validation mode: `{summary['validation_mode']}`.",
            f"- Internal validation passed: `{str(summary['internal_validation_passed']).lower()}`.",
            f"- Full JSON Schema validation performed: `{str(summary['full_jsonschema_validation_performed']).lower()}`.",
            f"- Complete Draft 2020-12 validation result: `{summary['full_jsonschema_validation_passed']}`.",
            "",
            "## Validation Scope",
            "",
            "The demonstrator was checked with an internal validator covering the declared schema-critical and cross-record constraints. A complete Draft 2020-12 JSON Schema validation was not performed because the required validator package was unavailable in the active environment.",
            "",
            "## Interpretation",
            "",
            "`DTC_A` and `DTC_B` are synthetic state-configuration records with a shared declared dynamic equivalence class and different temporal phase offsets and domains. They are not the same record and do not establish full-state identity.",
            "",
            "## Human-Readable Value Aliases",
            "",
            "- `state_configuration`: Zustandskonfiguration.",
            "- `boundary_configuration`: Grenzkonfiguration.",
            "- `DTC_EQ_CLASS_01`: Dynamische Äquivalenzklasse 01.",
            "- `not_experimental`: nicht experimentell.",
            "",
            "## Boundary Representation",
            "",
            "`BOUNDARY_AB` is represented as a separate boundary record so that a later technical question can ask whether this is adequate, too strong, or incomplete. The boundary representation is an open option, not a validated ontology.",
            "",
            "## Presentation Gap",
            "",
            f"- english_presentation_view_required_for_contact_package = {str(summary['english_presentation_view_required_for_contact_package']).lower()}",
            f"- english_presentation_view_created = {str(summary['english_presentation_view_created']).lower()}",
            "",
            "## Claim Boundary",
            "",
            "This demonstrator is synthetic, is not a model of the reported laser experiment, uses no experimental data, makes no physical prediction, explains no time-crystal mechanism, and creates or sends no contact message.",
            "",
        ]
    )


def make_contact_table(records: list[dict], aliases: dict) -> str:
    columns = [
        ("Record-ID", "record_id"),
        ("Record-Typ", "record_type"),
        ("Zustandsklasse", "state_class"),
        ("Dynamische Äquivalenz", "dynamic_equivalence_class"),
        ("Phasenverschiebung", "temporal_phase_offset"),
        ("Domäne", "domain_id"),
        ("Rolle der Grenzstruktur", "boundary_role"),
        ("Evidenzstatus", "evidence_status"),
    ]
    lines = [
        "# Compact Contact Table",
        "",
        "| " + " | ".join(header for header, _field in columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for record in records:
        lines.append("| " + " | ".join(display_value(field, record[field], aliases) for _header, field in columns) + " |")
    lines.extend(
        [
            "",
            "1. Synthetischer Methodendemonstrator.",
            "2. Kein Modell des realen Lasersystems.",
            "3. Grenzobjekt ist eine offene Repräsentationsoption.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OUTREACH01A-DTC-DEMO01 synthetic demonstrator records.")
    parser.add_argument("--input-root", required=True, help="Repository root containing data/OUTREACH01A-DTC-DEMO01.")
    parser.add_argument("--output-dir", required=True, help="Output directory for exactly six run outputs.")
    parser.add_argument("--overwrite", action="store_true", help="Replace expected output files if present.")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    prepare_output_dir(output_dir, args.overwrite)

    data_dir = root / "data" / "OUTREACH01A-DTC-DEMO01"
    schema = load_json(data_dir / "dtc_state_identity_schema.json")
    records_payload = load_json(data_dir / "dtc_state_identity_records.json")
    aliases = load_json(data_dir / "field_aliases_de.json")

    validation_mode, schema_valid, schema_messages = validate_with_jsonschema(schema, records_payload)
    cross_valid, cross_messages, facts = check_cross_record_rules(records_payload)
    validation_messages = schema_messages + cross_messages
    internal_validation_passed = schema_valid and cross_valid
    validation_passed = internal_validation_passed
    localized_value_aliases_present = bool(aliases.get("value_aliases"))

    final_status = "minimal_synthetic_dtc_state_identity_demonstrator_validated"
    if not (
        internal_validation_passed
        and facts["record_count"] == 3
        and facts["dynamic_equivalence_pair_present"]
        and facts["one_drive_period_phase_shift_present"]
        and facts["distinct_domains_present"]
        and facts["separate_boundary_record_present"]
        and facts["preferred_boundary_representation_forced"] is False
        and records_payload["models_reported_laser_experiment"] is False
        and records_payload["experimental_data_used"] is False
        and records_payload["physical_prediction_present"] is False
    ):
        final_status = "minimal_synthetic_dtc_state_identity_demonstrator_inconclusive"

    summary = {
        "demonstrator_id": records_payload["demonstrator_id"],
        "data_status": records_payload["data_status"],
        "record_count": facts["record_count"],
        "state_configuration_count": facts["state_configuration_count"],
        "boundary_configuration_count": facts["boundary_configuration_count"],
        "dynamic_equivalence_pair_present": facts["dynamic_equivalence_pair_present"],
        "one_drive_period_phase_shift_present": facts["one_drive_period_phase_shift_present"],
        "distinct_domains_present": facts["distinct_domains_present"],
        "separate_boundary_record_present": facts["separate_boundary_record_present"],
        "preferred_boundary_representation_forced": facts["preferred_boundary_representation_forced"],
        "models_reported_laser_experiment": records_payload["models_reported_laser_experiment"],
        "experimental_data_used": records_payload["experimental_data_used"],
        "physical_prediction_present": records_payload["physical_prediction_present"],
        "time_crystal_mechanism_explained": records_payload["time_crystal_mechanism_explained"],
        "validation_mode": validation_mode,
        "internal_validation_passed": internal_validation_passed,
        "full_jsonschema_validation_performed": FULL_JSONSCHEMA_VALIDATION_PERFORMED,
        "full_jsonschema_validation_passed": FULL_JSONSCHEMA_VALIDATION_PASSED,
        "validation_passed": validation_passed,
        "validation_passed_scope": VALIDATION_MODE,
        "localized_value_aliases_present": localized_value_aliases_present,
        "canonical_field_names_remain_language_neutral": aliases["canonical_field_names_remain_language_neutral"],
        "canonical_controlled_values_remain_language_neutral": aliases["canonical_controlled_values_remain_language_neutral"],
        "localized_field_aliases_used_as_logic_inputs": aliases["localized_field_aliases_used_as_logic_inputs"],
        "localized_value_aliases_used_as_logic_inputs": aliases["localized_value_aliases_used_as_logic_inputs"],
        "localized_aliases_used_as_keys": aliases["localized_aliases_used_as_keys"],
        "localized_aliases_used_in_joins": aliases["localized_aliases_used_in_joins"],
        "english_presentation_view_required_for_contact_package": True,
        "english_presentation_view_created": False,
        "contact_message_present": records_payload["contact_message_present"],
        "contact_sent": records_payload["contact_sent"],
        "final_status": final_status,
    }

    validated_payload = {
        "validation_mode": validation_mode,
        "internal_validation_passed": internal_validation_passed,
        "full_jsonschema_validation_performed": FULL_JSONSCHEMA_VALIDATION_PERFORMED,
        "full_jsonschema_validation_passed": FULL_JSONSCHEMA_VALIDATION_PASSED,
        "schema_valid": schema_valid,
        "cross_record_valid": cross_valid,
        "validation_passed": validation_passed,
        "validation_passed_scope": VALIDATION_MODE,
        "localized_value_aliases_present": localized_value_aliases_present,
        "records": records_payload["records"],
        "method_statements": records_payload.get("method_statements", []),
        "leakage_controls": records_payload.get("leakage_controls", {}),
    }
    write_json(output_dir / "validated_records.json", validated_payload)
    write_csv(
        output_dir / "validation_results.csv",
        per_record_results(records_payload, schema_valid, cross_valid, validation_mode, validation_messages),
        [
            "record_id",
            "schema_valid",
            "cross_record_valid",
            "validation_mode",
            "internal_validation_passed",
            "full_jsonschema_validation_performed",
            "full_jsonschema_validation_passed",
            "validation_messages",
        ],
    )
    alias_rows, alias_headers = make_alias_view(records_payload["records"], aliases)
    write_csv(output_dir / "german_alias_view.csv", alias_rows, alias_headers)
    write_json(output_dir / "demonstrator_summary.json", summary)
    (output_dir / "readout.md").write_text(make_readout(summary), encoding="utf-8")
    (output_dir / "compact_contact_table.md").write_text(make_contact_table(records_payload["records"], aliases), encoding="utf-8")

    actual_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_outputs != sorted(OUTPUT_FILES):
        raise SystemExit(f"output file set mismatch: {actual_outputs}")
    return 0 if final_status == "minimal_synthetic_dtc_state_identity_demonstrator_validated" else 2


if __name__ == "__main__":
    raise SystemExit(main())
