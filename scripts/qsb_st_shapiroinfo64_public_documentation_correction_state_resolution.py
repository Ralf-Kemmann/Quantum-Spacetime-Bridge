#!/usr/bin/env python3
"""QSB-ST ShapiroInfo documentation/correction-state resolution tables.

This script implements the SHAPIROINFO63 specification. It creates
documentation-target, correction-state, semantic-mapping, and provenance
resolution tables only when explicitly executed.

It does not inspect raw artifacts, read TIM/PAR values, perform public web
research, download documentation, compute residuals, perform model fitting,
interpret values physically, make anomaly claims, or make QSB-ST Bridge claims.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_DICTIONARY_SCHEMA_INPUT_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/"
    "SHAPIROINFO57_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE/"
)
DEFAULT_CONTENT_STRUCTURE_INPUT_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO53_TIM_PAR_CONTENT_STRUCTURE_REVIEW/"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/"
    "SHAPIROINFO64_PUBLIC_DOCUMENTATION_CORRECTION_STATE_RESOLUTION/"
)

OUTPUT_FILES = [
    "public_documentation_targets.csv",
    "correction_state_resolution_table.csv",
    "duplicate_parameter_followup_table.csv",
    "semantic_mapping_rules.csv",
    "provenance_resolution_requirements.csv",
    "documentation_resolution_summary.json",
    "public_documentation_correction_state_readout.md",
    "public_documentation_correction_state_config_resolved.json",
]

CLAIM_BOUNDARY = (
    "Claim boundary: this output is documentation-target and correction-state "
    "resolution only. This output does not provide evidence for a physical "
    "Shapiro-information residual. This output does not validate the QSB-ST "
    "Bridge. This output does not establish spacetime, quantum-gravity, "
    "relativistic, or pulsar-timing physics claims. This output does not "
    "interpret TIM or PAR values as physical evidence. No public web research "
    "or documentation download was performed."
)

ALLOWED_PLANNED_STATUS = [
    "documentation_required",
    "documentation_identified",
    "documentation_unavailable",
    "not_applicable",
    "unresolved",
]

ALLOWED_CURRENT_STATUS = [
    "known_from_file",
    "known_from_public_documentation",
    "inferred_from_structure",
    "unresolved",
    "not_applicable",
    "forbidden_to_assume",
]

ALLOWED_DUPLICATE_STATUS = [
    "duplicate_observed",
    "expected_by_convention_unconfirmed",
    "expected_by_convention_documented",
    "unresolved",
    "forbidden_to_interpret",
]

ALLOWED_INTERPRETATION_STATUS = [
    "not_interpreted",
    "documentation_required",
    "unresolved",
    "forbidden_to_infer",
]

ALLOWED_MAPPING_STATUS = [
    "not_performed",
    "documentation_required",
    "source_documentation_identified",
    "source_documentation_unavailable",
    "unresolved",
    "forbidden_to_infer",
]

DOCUMENTATION_TARGETS = [
    (
        "DOC001",
        "tim_file_format",
        "Public documentation for TIM file structure and field conventions.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        True,
        "Required before any safe value-reading gate can assign TIM field meaning.",
    ),
    (
        "DOC002",
        "par_file_format",
        "Public documentation for PAR file structure and parameter conventions.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        True,
        "Required before any safe value-reading gate can assign PAR parameter meaning.",
    ),
    (
        "DOC003",
        "current_public_source_package",
        "Public release documentation for the local ShapiroInfo source package.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        True,
        "No package-level provenance may be assumed silently.",
    ),
    (
        "DOC004",
        "timing_model_tool_conventions",
        "Documentation for timing-model tool conventions used by TIM/PAR artifacts.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        True,
        "Needed before semantic mapping of timing-model fields.",
    ),
    (
        "DOC005",
        "clock_correction_conventions",
        "Documentation for clock-correction convention status.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, the clock correction state must remain unresolved.",
    ),
    (
        "DOC006",
        "ephemeris_conventions",
        "Documentation for ephemeris convention status.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, the ephemeris state must remain unresolved.",
    ),
    (
        "DOC007",
        "DM_dispersion_correction_conventions",
        "Documentation for DM / dispersion correction convention status.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, the DM correction state must remain unresolved.",
    ),
    (
        "DOC008",
        "solarwind_correction_conventions",
        "Documentation for solarwind correction convention status.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, the solarwind correction state must remain unresolved.",
    ),
    (
        "DOC009",
        "noise_model_conventions",
        "Documentation for noise-model convention status.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, the noise-model state must remain unresolved.",
    ),
    (
        "DOC010",
        "backend_jump_system_parameter_conventions",
        "Documentation for backend jump and system parameter conventions.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, backend jump and system states must remain unresolved.",
    ),
    (
        "DOC011",
        "frequency_band_conventions",
        "Documentation for frequency-band convention status.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, frequency-band state must remain unresolved.",
    ),
    (
        "DOC012",
        "profile_template_conventions",
        "Documentation for profile-template convention status.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, profile-template state must remain unresolved.",
    ),
    (
        "DOC013",
        "observatory_backend_receiver_system_conventions",
        "Documentation for observatory, backend, and receiver system conventions.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        False,
        "If unavailable, observatory system state must remain unresolved.",
    ),
    (
        "DOC014",
        "checksum_provenance_quarantine_state",
        "Local upstream checksum, provenance, and quarantine-state documentation.",
        False,
        False,
        "documentation_identified",
        "local_upstream_note",
        True,
        False,
        "Covered by upstream local artifact-control documentation.",
    ),
    (
        "DOC015",
        "duplicate_parameter_conventions",
        "Documentation for duplicate-parameter conventions.",
        True,
        True,
        "documentation_required",
        "public_documentation_required",
        True,
        True,
        "Needed before duplicate parameters can be interpreted by convention.",
    ),
    (
        "DOC016",
        "value_reading_scope_constraints",
        "Documentation of scope constraints before any descriptive value reading.",
        True,
        False,
        "documentation_required",
        "public_documentation_required",
        True,
        True,
        "Direct value reading remains not_opened until a later explicit gate.",
    ),
]

CORRECTION_STATE_FIELDS = [
    ("raw_or_processed_state", "current_public_source_package"),
    ("timing_model_source", "timing_model_tool_conventions"),
    ("timing_model_tool", "timing_model_tool_conventions"),
    ("clock_correction_state", "clock_correction_conventions"),
    ("clock_reference", "clock_correction_conventions"),
    ("ephemeris_state", "ephemeris_conventions"),
    ("ephemeris_reference", "ephemeris_conventions"),
    ("DM_correction_state", "DM_dispersion_correction_conventions"),
    ("solarwind_correction_state", "solarwind_correction_conventions"),
    ("noise_model_state", "noise_model_conventions"),
    ("backend_jump_state", "backend_jump_system_parameter_conventions"),
    ("whitening_state", "noise_model_conventions"),
    ("frequency_band_state", "frequency_band_conventions"),
    ("profile_template_state", "profile_template_conventions"),
    ("observatory_system_state", "observatory_backend_receiver_system_conventions"),
    ("provenance_reference", "checksum_provenance_quarantine_state"),
    ("unresolved_correction_fields", "value_reading_scope_constraints"),
]

DUPLICATE_PARAMETERS = ["ECORR", "T2EFAC", "T2EQUAD"]

SEMANTIC_MAPPING_SCOPES = [
    "tim_column_semantics",
    "par_parameter_semantics",
    "correction_state_semantics",
    "duplicate_parameter_semantics",
    "value_reading_scope",
]

PROVENANCE_ITEMS = [
    (
        "local_generated_outputs",
        "local_generated_output",
        "runs/QSB-ST-SHAPIROINFO/",
        "available_locally",
        "medium",
        "Generated outputs are method artifacts, not physical evidence.",
    ),
    (
        "local_manifest_checksum_notes",
        "local_manifest_or_checksum_note",
        "docs/",
        "available_locally",
        "medium",
        "Local upstream notes may document quarantine and checksum posture.",
    ),
    (
        "public_release_documentation",
        "public_release_documentation",
        "",
        "public_documentation_required",
        "unresolved",
        "Public release documentation is required before semantic mapping.",
    ),
    (
        "timing_tool_documentation",
        "timing_tool_documentation",
        "",
        "public_documentation_required",
        "unresolved",
        "Timing-tool documentation is required before tool-convention mapping.",
    ),
    (
        "correction_state_documentation",
        "public_release_documentation",
        "",
        "public_documentation_required",
        "unresolved",
        "Correction-state documentation remains required.",
    ),
    (
        "duplicate_parameter_documentation",
        "public_release_documentation",
        "",
        "public_documentation_required",
        "unresolved",
        "Duplicate parameters require convention documentation.",
    ),
    (
        "future_value_reading_gate",
        "unresolved",
        "",
        "unresolved",
        "unresolved",
        "Value reading remains not_opened until a later explicit gate.",
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_documentation_targets() -> list[dict[str, Any]]:
    return [
        {
            "target_id": target_id,
            "target_class": target_class,
            "target_description": description,
            "required_for_value_reading": bool_text(required_for_value_reading),
            "required_for_semantic_mapping": bool_text(required_for_semantic_mapping),
            "planned_status": planned_status,
            "source_requirement": source_requirement,
            "unresolved_allowed": bool_text(unresolved_allowed),
            "stop_if_unavailable": bool_text(stop_if_unavailable),
            "notes": notes,
        }
        for (
            target_id,
            target_class,
            description,
            required_for_value_reading,
            required_for_semantic_mapping,
            planned_status,
            source_requirement,
            unresolved_allowed,
            stop_if_unavailable,
            notes,
        ) in DOCUMENTATION_TARGETS
    ]


def build_correction_state_rows() -> list[dict[str, Any]]:
    allowed_values = "|".join(ALLOWED_CURRENT_STATUS)
    return [
        {
            "correction_field": field,
            "current_status": "unresolved",
            "required_for_value_reading": "true",
            "required_for_semantic_mapping": "true",
            "documentation_target_class": target_class,
            "allowed_resolution_values": allowed_values,
            "unresolved_allowed": "true",
            "stop_if_unresolved": "false",
            "provenance_requirement": (
                "public_documentation_required_before_interpretation"
            ),
            "notes": (
                "Unknown is acceptable. Unresolved is acceptable. "
                "Assumed is not acceptable. Silent assumptions are not acceptable."
            ),
        }
        for field, target_class in CORRECTION_STATE_FIELDS
    ]


def build_duplicate_parameter_rows() -> list[dict[str, Any]]:
    return [
        {
            "parameter_name": parameter_name,
            "duplicate_status": "duplicate_observed",
            "required_documentation_target": "duplicate_parameter_conventions",
            "expected_scope_question": (
                "Are duplicate entries expected by timing-tool or release "
                "conventions, and are they scoped by backend, receiver, band, "
                "flag, or data subset?"
            ),
            "interpretation_status": "documentation_required",
            "value_reading_status": "not_opened",
            "required_followup": "public_documentation_required",
            "notes": (
                "Duplicate values are not interpreted physically and are not "
                "selected for fitting."
            ),
        }
        for parameter_name in DUPLICATE_PARAMETERS
    ]


def build_semantic_mapping_rows() -> list[dict[str, Any]]:
    return [
        {
            "mapping_scope": scope,
            "allowed_mapping_source": "source_backed_public_documentation_required",
            "mapping_status": "documentation_required",
            "semantic_claim_allowed": "false",
            "physical_interpretation_allowed": "false",
            "required_provenance": "source_backed_public_documentation_required",
            "notes": (
                "No field or parameter name may be mapped to physical meaning "
                "by intuition alone."
            ),
        }
        for scope in SEMANTIC_MAPPING_SCOPES
    ]


def build_provenance_rows() -> list[dict[str, Any]]:
    return [
        {
            "provenance_item": item,
            "source_type_required": source_type,
            "source_path_or_reference": source_path,
            "current_status": status,
            "provenance_confidence": confidence,
            "semantic_claim_allowed": "false",
            "value_reading_allowed": "false",
            "notes": notes,
        }
        for item, source_type, source_path, status, confidence, notes in PROVENANCE_ITEMS
    ]


def build_summary(
    output_root: Path,
    documentation_targets: list[dict[str, Any]],
    correction_rows: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    unresolved_count = sum(
        1 for row in correction_rows if row["current_status"] == "unresolved"
    )
    return {
        "generated_at_utc": utc_now(),
        "output_root": output_root.as_posix(),
        "documentation_target_count": len(documentation_targets),
        "correction_state_field_count": len(correction_rows),
        "unresolved_correction_state_count": unresolved_count,
        "duplicate_parameter_followup_count": len(duplicate_rows),
        "semantic_mapping_status": "not_performed",
        "direct_value_reading_gate": "not_opened",
        "residual_analysis_gate": "closed",
        "model_fitting_gate": "closed",
        "anomaly_claim_gate": "closed",
        "bridge_claim_gate": "closed",
        "public_web_research_status": "not_performed",
        "documentation_download_status": "not_performed",
        "raw_artifact_access_status": "not_performed",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_config(
    script: str,
    dictionary_schema_input_root: Path,
    content_structure_input_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    return {
        "script": script,
        "dictionary_schema_input_root": dictionary_schema_input_root.as_posix(),
        "content_structure_input_root": content_structure_input_root.as_posix(),
        "output_root": output_root.as_posix(),
        "execution_scope": (
            "documentation_targets_and_correction_state_resolution_only"
        ),
        "public_web_research": "not_performed",
        "documentation_download": "not_performed",
        "raw_artifact_access": "not_performed",
        "direct_value_reading_gate": "not_opened",
        "residual_analysis_gate": "closed",
        "model_fitting_gate": "closed",
        "anomaly_claim_gate": "closed",
        "bridge_claim_gate": "closed",
        "physical_value_interpretation": "forbidden",
        "claim_boundary": CLAIM_BOUNDARY,
    }


def build_readout(
    output_files: list[str],
    documentation_targets: list[dict[str, Any]],
    correction_rows: list[dict[str, Any]],
    duplicate_rows: list[dict[str, Any]],
    semantic_rows: list[dict[str, Any]],
    provenance_rows: list[dict[str, Any]],
) -> str:
    unresolved_count = sum(
        1 for row in correction_rows if row["current_status"] == "unresolved"
    )
    lines = [
        "# QSB-ST SHAPIROINFO64 Documentation/Correction-State Resolution",
        "",
        "## Purpose",
        "",
        "This readout reports documentation-target and correction-state resolution "
        "tables only.",
        "",
        "No public web research or documentation download was performed.",
        "",
        "## Output Files",
        "",
    ]
    lines.extend(f"- {name}" for name in output_files)
    lines.extend(
        [
            "",
            "## Documentation Target Summary",
            "",
            f"Documentation targets: {len(documentation_targets)}",
            "Default planned status: documentation_required except local upstream "
            "checksum/provenance/quarantine state.",
            "",
            "## Correction-State Summary",
            "",
            f"Correction-state fields: {len(correction_rows)}",
            f"Unresolved correction-state fields: {unresolved_count}",
            "Unknown and unresolved states remain acceptable. Silent assumptions "
            "are not acceptable.",
            "",
            "## Duplicate-Parameter Follow-Up Summary",
            "",
            f"Duplicate parameters listed for follow-up: {len(duplicate_rows)}",
            "Duplicate values are not interpreted physically.",
            "",
            "## Semantic Mapping Posture",
            "",
            f"Semantic mapping rule rows: {len(semantic_rows)}",
            "Semantic claim allowed: false",
            "Physical interpretation allowed: false",
            "",
            "## Provenance Posture",
            "",
            f"Provenance requirement rows: {len(provenance_rows)}",
            "Value reading allowed: false by default",
            "",
            "## Stop Conditions",
            "",
            "- Stop if documentation targets cannot be identified.",
            "- Stop if correction-state fields cannot be represented.",
            "- Stop if semantic mapping would require undocumented inference.",
            "- Stop if value reading would require assuming correction-state status.",
            "- Stop if any output begins to frame values as physical evidence.",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(
    output_root: Path,
    script: str,
    dictionary_schema_input_root: Path,
    content_structure_input_root: Path,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)

    documentation_targets = build_documentation_targets()
    correction_rows = build_correction_state_rows()
    duplicate_rows = build_duplicate_parameter_rows()
    semantic_rows = build_semantic_mapping_rows()
    provenance_rows = build_provenance_rows()

    write_csv(
        output_root / "public_documentation_targets.csv",
        [
            "target_id",
            "target_class",
            "target_description",
            "required_for_value_reading",
            "required_for_semantic_mapping",
            "planned_status",
            "source_requirement",
            "unresolved_allowed",
            "stop_if_unavailable",
            "notes",
        ],
        documentation_targets,
    )
    write_csv(
        output_root / "correction_state_resolution_table.csv",
        [
            "correction_field",
            "current_status",
            "required_for_value_reading",
            "required_for_semantic_mapping",
            "documentation_target_class",
            "allowed_resolution_values",
            "unresolved_allowed",
            "stop_if_unresolved",
            "provenance_requirement",
            "notes",
        ],
        correction_rows,
    )
    write_csv(
        output_root / "duplicate_parameter_followup_table.csv",
        [
            "parameter_name",
            "duplicate_status",
            "required_documentation_target",
            "expected_scope_question",
            "interpretation_status",
            "value_reading_status",
            "required_followup",
            "notes",
        ],
        duplicate_rows,
    )
    write_csv(
        output_root / "semantic_mapping_rules.csv",
        [
            "mapping_scope",
            "allowed_mapping_source",
            "mapping_status",
            "semantic_claim_allowed",
            "physical_interpretation_allowed",
            "required_provenance",
            "notes",
        ],
        semantic_rows,
    )
    write_csv(
        output_root / "provenance_resolution_requirements.csv",
        [
            "provenance_item",
            "source_type_required",
            "source_path_or_reference",
            "current_status",
            "provenance_confidence",
            "semantic_claim_allowed",
            "value_reading_allowed",
            "notes",
        ],
        provenance_rows,
    )

    write_json(
        output_root / "documentation_resolution_summary.json",
        build_summary(output_root, documentation_targets, correction_rows, duplicate_rows),
    )
    write_json(
        output_root / "public_documentation_correction_state_config_resolved.json",
        build_config(
            script,
            dictionary_schema_input_root,
            content_structure_input_root,
            output_root,
        ),
    )
    (output_root / "public_documentation_correction_state_readout.md").write_text(
        build_readout(
            OUTPUT_FILES,
            documentation_targets,
            correction_rows,
            duplicate_rows,
            semantic_rows,
            provenance_rows,
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create QSB-ST ShapiroInfo public-documentation and correction-state "
            "resolution tables. This does not inspect raw artifacts, access the "
            "internet, download documentation, open value reading, compute "
            "residuals, or perform model fitting."
        )
    )
    parser.add_argument(
        "--dictionary-schema-input-root",
        type=Path,
        default=DEFAULT_DICTIONARY_SCHEMA_INPUT_ROOT,
        help="Root containing SHAPIROINFO57 dictionary/schema/correction-state outputs.",
    )
    parser.add_argument(
        "--content-structure-input-root",
        type=Path,
        default=DEFAULT_CONTENT_STRUCTURE_INPUT_ROOT,
        help="Root containing SHAPIROINFO53 content-structure outputs.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Output root for SHAPIROINFO64 documentation/correction-state artifacts.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_outputs(
        args.output_root,
        Path(__file__).as_posix(),
        args.dictionary_schema_input_root,
        args.content_structure_input_root,
    )
    print(
        "wrote documentation/correction-state outputs under: "
        f"{args.output_root.as_posix()}"
    )
    print(CLAIM_BOUNDARY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
