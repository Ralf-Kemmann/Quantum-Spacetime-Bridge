#!/usr/bin/env python3
"""Validate the IDSPACE/CPNS04 minimal schema scaffold.

This runner validates only schema/example consistency. It does not compute
physical results and does not quantify real degeneracy.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


BLOCK_ID = "QSB-ST-IDSPACE-CPNS06"
RUN_ID = "minimal_schema_validation_open"
RUNNER_NAME = "run_qsb_st_idspace_cpns06_minimal_schema_validation.py"

SCHEMA_PATH = Path("data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json")
EXAMPLES_PATH = Path("data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json")
RUN_DIR = Path("runs/QSB-ST-IDSPACE-CPNS06/minimal_schema_validation_open")
SUMMARY_PATH = RUN_DIR / "summary.json"
READOUT_PATH = RUN_DIR / "readout.md"

REQUIRED_OBJECT_GROUPS = [
    "identity_space_record",
    "fingerprint_object_record",
    "transform_class_record",
    "equivalence_decision_record",
    "cpns_degeneracy_record",
    "ambiguity_class_record",
    "claim_boundary_flags",
]

REQUIRED_DECISION_STATES = [
    "same_identity_candidate",
    "different_identity_candidate",
    "ambiguous_unresolved",
    "invalid_outside_scope",
]

REQUIRED_FALSE_FLAGS = [
    "bridge_confirmation",
    "diagnostic_specificity_claim",
    "physical_validation",
    "wifm01e_opened",
    "wifm02_opened",
    "bridge_nature_02_opened",
]

DEGENERACY_VALUE_FIELDS = [
    "alternative_count",
    "degeneracy_lower_bound",
    "degeneracy_upper_bound",
    "entropy_value",
]

PLACEHOLDER_DEGENERACY_STATUSES = {
    "unresolved_degeneracy",
    "invalid_degeneracy_measurement",
}


def load_json(path: Path, failed_checks: list[str]) -> Any | None:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:  # pragma: no cover - failure path is summarized.
        failed_checks.append(f"json_parse_failed:{path}:{exc}")
        return None


def walk_dicts(obj: Any):
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from walk_dicts(value)
    elif isinstance(obj, list):
        for value in obj:
            yield from walk_dicts(value)


def validate_schema(schema: Any, checks: dict[str, bool], failed_checks: list[str]) -> None:
    if not isinstance(schema, dict):
        failed_checks.append("schema_not_object")
        checks["schema_is_object"] = False
        return

    object_groups = schema.get("object_groups")
    checks["schema_has_object_groups"] = isinstance(object_groups, dict)
    if not isinstance(object_groups, dict):
        failed_checks.append("missing_object_groups")
        return

    missing_groups = [group for group in REQUIRED_OBJECT_GROUPS if group not in object_groups]
    checks["required_object_groups_present"] = not missing_groups
    if missing_groups:
        failed_checks.append(f"missing_object_groups:{','.join(missing_groups)}")

    fields_ok = True
    for group_name in REQUIRED_OBJECT_GROUPS:
        group = object_groups.get(group_name)
        if not isinstance(group, dict):
            fields_ok = False
            continue
        fields = group.get("fields")
        if not isinstance(fields, dict) or not fields:
            fields_ok = False
            failed_checks.append(f"missing_fields:{group_name}")
            continue
        for field_name, field_spec in fields.items():
            if not isinstance(field_spec, dict):
                fields_ok = False
                failed_checks.append(f"field_spec_not_object:{group_name}.{field_name}")
                continue
            for required_key in ("type", "required", "description"):
                if required_key not in field_spec:
                    fields_ok = False
                    failed_checks.append(
                        f"field_missing_{required_key}:{group_name}.{field_name}"
                    )
    checks["object_group_fields_complete"] = fields_ok


def collect_decision_states(examples: Any) -> list[str]:
    states: set[str] = set()
    for item in walk_dicts(examples):
        state = item.get("decision_state")
        if isinstance(state, str):
            states.add(state)
    return sorted(states)


def validate_boundary_flags(
    examples: Any,
    checks: dict[str, bool],
    failed_checks: list[str],
) -> dict[str, Any]:
    dicts = list(walk_dicts(examples))
    status: dict[str, Any] = {}
    all_ok = True
    for flag in REQUIRED_FALSE_FLAGS:
        values = [item.get(flag) for item in dicts if flag in item]
        present = bool(values)
        all_false = present and all(value is False for value in values)
        status[flag] = {
            "present": present,
            "all_false": all_false,
            "occurrence_count": len(values),
        }
        if not present:
            all_ok = False
            failed_checks.append(f"missing_boundary_flag:{flag}")
        elif not all_false:
            all_ok = False
            failed_checks.append(f"boundary_flag_not_false:{flag}:{values}")
    checks["boundary_flags_present_and_false"] = all_ok
    return status


def validate_examples(
    examples: Any,
    schema: Any,
    checks: dict[str, bool],
    failed_checks: list[str],
    warning_checks: list[str],
) -> tuple[list[str], bool, bool, str]:
    if not isinstance(examples, dict):
        failed_checks.append("examples_not_object")
        checks["examples_is_object"] = False
        return [], False, False, "invalid_examples_object"

    example_list = examples.get("examples")
    checks["examples_list_present"] = isinstance(example_list, list)
    if not isinstance(example_list, list):
        failed_checks.append("examples_list_missing")
        return [], False, False, "invalid_examples_list"

    every_example_has_decision = True
    for example in example_list:
        if not isinstance(example, dict) or not isinstance(
            example.get("equivalence_decision_record"), dict
        ):
            every_example_has_decision = False
    checks["each_example_has_equivalence_decision_record"] = every_example_has_decision
    if not every_example_has_decision:
        failed_checks.append("example_missing_equivalence_decision_record")

    decision_states_found = collect_decision_states(examples)
    missing_states = [
        state for state in REQUIRED_DECISION_STATES if state not in decision_states_found
    ]
    checks["required_decision_states_present"] = not missing_states
    if missing_states:
        failed_checks.append(f"missing_decision_states:{','.join(missing_states)}")

    allowed_states = set()
    try:
        allowed_states = set(
            schema["object_groups"]["equivalence_decision_record"]["fields"][
                "decision_state"
            ]["allowed_values"]
        )
    except Exception:
        failed_checks.append("schema_missing_decision_state_allowed_values")

    unknown_states = [state for state in decision_states_found if state not in allowed_states]
    checks["decision_states_match_schema"] = not unknown_states
    if unknown_states:
        failed_checks.append(f"unknown_decision_states:{','.join(unknown_states)}")

    ambiguity_valid_state = "ambiguous_unresolved" in decision_states_found
    checks["ambiguity_valid_state"] = ambiguity_valid_state
    if not ambiguity_valid_state:
        failed_checks.append("ambiguity_state_missing")

    successful_identity_resolution_states = {
        "same_identity_candidate",
        "different_identity_candidate",
    }
    invalid_outside_scope_handled_as_non_success = (
        "invalid_outside_scope" in decision_states_found
        and "invalid_outside_scope" not in successful_identity_resolution_states
    )
    checks["invalid_outside_scope_handled_as_non_success"] = (
        invalid_outside_scope_handled_as_non_success
    )
    if not invalid_outside_scope_handled_as_non_success:
        failed_checks.append("invalid_outside_scope_not_handled_as_non_success")

    degeneracy_records = [
        item for item in walk_dicts(examples) if "degeneracy_status" in item
    ]
    measured_records: list[str] = []
    invalid_status_records: list[str] = []
    for record in degeneracy_records:
        record_id = str(record.get("cpns_record_id", "unknown_cpns_record"))
        if any(record.get(field) is not None for field in DEGENERACY_VALUE_FIELDS):
            measured_records.append(record_id)
        status = record.get("degeneracy_status")
        if status not in PLACEHOLDER_DEGENERACY_STATUSES:
            invalid_status_records.append(record_id)

    no_measured_degeneracy = not measured_records and not invalid_status_records
    checks["no_measured_real_degeneracy"] = no_measured_degeneracy
    if measured_records:
        failed_checks.append(f"measured_degeneracy_values_present:{','.join(measured_records)}")
    if invalid_status_records:
        failed_checks.append(
            f"non_placeholder_degeneracy_status:{','.join(invalid_status_records)}"
        )

    if degeneracy_records and no_measured_degeneracy:
        warning_checks.append(
            "degeneracy_readouts_are_placeholders_only:not_real_degeneracy_measurements"
        )

    return (
        decision_states_found,
        ambiguity_valid_state,
        invalid_outside_scope_handled_as_non_success,
        "placeholder_status_only" if no_measured_degeneracy else "invalid_or_measured",
    )


def write_outputs(summary: dict[str, Any]) -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    failed = summary["failed_checks"]
    warnings = summary["warning_checks"]
    readout = [
        "# QSB-ST-IDSPACE-CPNS06 Minimal Schema Validation Readout",
        "",
        "## Purpose",
        "",
        "Validate CPNS04 schema/example consistency only.",
        "",
        "## Inputs",
        "",
    ]
    for path in summary["inputs"]:
        readout.append(f"- `{path}`")
    readout.extend(
        [
            "",
            "## Checks",
            "",
        ]
    )
    for name, passed in summary["checks"].items():
        readout.append(f"- `{name}`: {passed}")
    readout.extend(
        [
            "",
            "## Result",
            "",
            f"- passed: {summary['passed']}",
            f"- decision_states_found: {', '.join(summary['decision_states_found'])}",
            f"- ambiguity_valid_state: {summary['ambiguity_valid_state']}",
            "- invalid_outside_scope_handled_as_non_success: "
            f"{summary['invalid_outside_scope_handled_as_non_success']}",
            f"- degeneracy_measurement_status: {summary['degeneracy_measurement_status']}",
            "",
            "## Warnings",
            "",
        ]
    )
    if warnings:
        for warning in warnings:
            readout.append(f"- `{warning}`")
    else:
        readout.append("- none")
    readout.extend(
        [
            "",
            "## Failed Checks",
            "",
        ]
    )
    if failed:
        for item in failed:
            readout.append(f"- `{item}`")
    else:
        readout.append("- none")
    readout.extend(
        [
            "",
            "## Claim Boundary",
            "",
            "- No Bridge confirmation.",
            "- No diagnostic specificity claim.",
            "- No physical validation.",
            "- No proof of wave identity.",
            "- No physical spacetime claim.",
            "- No WIFM01E default.",
            "- No WIFM02 opening.",
            "- No BRIDGE-NATURE-02 opening.",
            "",
            "## Next step",
            "",
            "Review this validation result before any later schema or runner extension.",
            "",
        ]
    )
    READOUT_PATH.write_text("\n".join(readout), encoding="utf-8")


def main() -> int:
    failed_checks: list[str] = []
    warning_checks: list[str] = []
    checks: dict[str, bool] = {}

    schema = load_json(SCHEMA_PATH, failed_checks)
    examples = load_json(EXAMPLES_PATH, failed_checks)
    checks["schema_json_parse"] = schema is not None
    checks["examples_json_parse"] = examples is not None

    if schema is not None:
        validate_schema(schema, checks, failed_checks)

    boundary_flags_status: dict[str, Any] = {}
    decision_states_found: list[str] = []
    ambiguity_valid_state = False
    invalid_outside_scope_handled_as_non_success = False
    degeneracy_measurement_status = "not_checked"

    if schema is not None and examples is not None:
        boundary_flags_status = validate_boundary_flags(examples, checks, failed_checks)
        (
            decision_states_found,
            ambiguity_valid_state,
            invalid_outside_scope_handled_as_non_success,
            degeneracy_measurement_status,
        ) = validate_examples(examples, schema, checks, failed_checks, warning_checks)

    passed = not failed_checks and all(checks.values())

    summary = {
        "block_id": BLOCK_ID,
        "runner_name": RUNNER_NAME,
        "run_id": RUN_ID,
        "inputs": [str(SCHEMA_PATH), str(EXAMPLES_PATH)],
        "outputs": [str(SUMMARY_PATH), str(READOUT_PATH)],
        "checks": checks,
        "passed": passed,
        "failed_checks": failed_checks,
        "warning_checks": warning_checks,
        "decision_states_found": decision_states_found,
        "boundary_flags_status": boundary_flags_status,
        "ambiguity_valid_state": ambiguity_valid_state,
        "invalid_outside_scope_handled_as_non_success": (
            invalid_outside_scope_handled_as_non_success
        ),
        "degeneracy_measurement_status": degeneracy_measurement_status,
        "bridge_confirmation": False,
        "diagnostic_specificity_claim": False,
        "physical_validation": False,
        "wifm01e_opened": False,
        "wifm02_opened": False,
        "bridge_nature_02_opened": False,
        "claim_boundary": [
            "schema_example_consistency_only",
            "no_physical_results",
            "no_real_degeneracy_quantification",
            "no_bridge_confirmation",
            "no_diagnostic_specificity_claim",
            "no_physical_validation",
            "no_wifm01e_default",
            "no_wifm02_opening",
            "no_bridge_nature_02_opening",
        ],
    }

    write_outputs(summary)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
