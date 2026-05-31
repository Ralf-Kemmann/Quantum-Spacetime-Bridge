#!/usr/bin/env python3
"""QSB-ST ShapiroInfo TIM/PAR dictionary, schema, and correction-state layer.

This script implements the SHAPIROINFO57 method-layer specification. It reads
generated content-structure outputs by default and produces dictionary/schema
and correction-state run artifacts only when explicitly executed.

It does not perform physical value interpretation, residual_search,
model_fitting, anomaly claims, or QSB-ST Bridge confirmation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_CONTENT_STRUCTURE_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO53_TIM_PAR_CONTENT_STRUCTURE_REVIEW/"
)
DEFAULT_RAW_STRUCTURE_INVENTORY_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO39_RAW_STRUCTURE_INVENTORY/"
)
DEFAULT_RAW_INPUT_ROOT = Path("data/QSB-ST-SHAPIROINFO/public_sources/")
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/"
    "SHAPIROINFO57_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE/"
)

TIM_COLUMN_DISTRIBUTION = "tim_column_count_distribution.csv"
TIM_ROW_FORMAT = "tim_row_format_inventory.csv"
TIM_SUMMARY = "tim_content_structure_summary.json"
PAR_PARAMETER_INVENTORY = "par_parameter_name_inventory.csv"
PAR_PREFIX_GROUPS = "par_parameter_prefix_groups.csv"
PAR_VALUE_FORMAT_CLASSES = "par_value_format_classes.csv"
PAR_SUMMARY = "par_content_structure_summary.json"
RAW_STRUCTURE_TABLE = "raw_structure_inventory_table.csv"

OUTPUT_FILES = [
    "tim_schema_map.csv",
    "tim_schema_summary.json",
    "par_field_dictionary.csv",
    "par_prefix_group_dictionary.csv",
    "par_duplicate_parameter_report.csv",
    "correction_state_template.csv",
    "correction_state_summary.json",
    "provenance_requirements.csv",
    "field_dictionary_schema_correction_state_readout.md",
    "field_dictionary_schema_correction_state_config_resolved.json",
]

CLAIM_BOUNDARY = (
    "Claim boundary: this output is dictionary/schema/correction-state only. "
    "It does not provide evidence for a physical Shapiro-information residual. "
    "It does not validate the QSB-ST Bridge. It does not establish spacetime, "
    "quantum-gravity, relativistic, or pulsar-timing physics claims. It does "
    "not interpret TIM or PAR values as physical evidence."
)

CORRECTION_STATE_FIELDS = [
    "raw_or_processed_state",
    "timing_model_source",
    "timing_model_tool",
    "clock_correction_state",
    "clock_reference",
    "ephemeris_state",
    "ephemeris_reference",
    "DM_correction_state",
    "solarwind_correction_state",
    "noise_model_state",
    "backend_jump_state",
    "whitening_state",
    "frequency_band_state",
    "profile_template_state",
    "observatory_system_state",
    "provenance_reference",
    "unresolved_correction_fields",
]

ALLOWED_CORRECTION_STATE_VALUES = [
    "known_from_file",
    "known_from_public_documentation",
    "inferred_from_structure",
    "unresolved",
    "not_applicable",
    "forbidden_to_assume",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle)), []
    except OSError as exc:
        return [], [f"csv_read_failed: {path}: {type(exc).__name__}: {exc}"]


def read_json_object(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"json_read_failed: {path}: {type(exc).__name__}: {exc}"]


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def parameter_prefix_group(parameter_name: str) -> str:
    if "_" in parameter_name:
        prefix = parameter_name.split("_", 1)[0]
        return prefix or "ungrouped"
    match = re.match(r"^[A-Za-z]+", parameter_name)
    if match:
        return match.group(0)
    return "ungrouped"


def dominant_column_pattern(rows: list[dict[str, str]]) -> dict[str, str] | None:
    if not rows:
        return None
    return sorted(
        rows,
        key=lambda row: (
            -as_int(row.get("row_count")),
            -as_int(row.get("apparent_column_count")),
            row.get("relative_path", ""),
        ),
    )[0]


def build_tim_schema_map(
    content_structure_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any], list[str]]:
    distribution_path = content_structure_root / TIM_COLUMN_DISTRIBUTION
    row_format_path = content_structure_root / TIM_ROW_FORMAT
    summary_path = content_structure_root / TIM_SUMMARY

    distribution_rows, warnings = read_csv_rows(distribution_path)
    row_format_rows, row_format_warnings = read_csv_rows(row_format_path)
    tim_summary, summary_warnings = read_json_object(summary_path)
    warnings.extend(row_format_warnings)
    warnings.extend(summary_warnings)

    dominant = dominant_column_pattern(distribution_rows)
    dominant_count = as_int(dominant.get("apparent_column_count")) if dominant else 0
    dominant_rows = as_int(dominant.get("row_count")) if dominant else 0
    dominant_relative_path = dominant.get("relative_path", "") if dominant else ""

    delimiter_hints = tim_summary.get("delimiter_hints") or {}
    delimiter_hint = "unresolved"
    if isinstance(delimiter_hints, dict) and delimiter_hints:
        delimiter_hint = sorted(
            delimiter_hints.items(), key=lambda item: (-as_int(item[1]), item[0])
        )[0][0]

    schema_rows: list[dict[str, Any]] = []
    for row in distribution_rows:
        apparent_column_count = as_int(row.get("apparent_column_count"))
        row_count = as_int(row.get("row_count"))
        semantic_status = (
            "public_documentation_required"
            if apparent_column_count == dominant_count
            else "unresolved"
        )
        schema_rows.append(
            {
                "source_file": TIM_COLUMN_DISTRIBUTION,
                "relative_path": row.get("relative_path", ""),
                "row_class": "data_like",
                "apparent_column_count": apparent_column_count,
                "column_position": "",
                "observed_token_format_class": "unresolved_by_dictionary_layer",
                "missing_value_marker_present": "unresolved",
                "delimiter_hint": delimiter_hint,
                "row_count_for_column_count": row_count,
                "example_token_snippet_capped": "",
                "schema_confidence": "medium",
                "semantic_status": semantic_status,
                "provenance_source_type": "observed_in_content_structure_output",
                "provenance_source_path": distribution_path.as_posix(),
                "provenance_source_reference": "column_count_distribution",
            }
        )

    if dominant_count > 0:
        for column_position in range(1, dominant_count + 1):
            schema_rows.append(
                {
                    "source_file": TIM_COLUMN_DISTRIBUTION,
                    "relative_path": dominant_relative_path,
                    "row_class": "data_like",
                    "apparent_column_count": dominant_count,
                    "column_position": column_position,
                    "observed_token_format_class": "unresolved_by_dictionary_layer",
                    "missing_value_marker_present": "unresolved",
                    "delimiter_hint": delimiter_hint,
                    "row_count_for_column_count": dominant_rows,
                    "example_token_snippet_capped": "",
                    "schema_confidence": "medium",
                    "semantic_status": "public_documentation_required",
                    "provenance_source_type": "observed_in_content_structure_output",
                    "provenance_source_path": distribution_path.as_posix(),
                    "provenance_source_reference": "dominant_column_position",
                }
            )

    secondary_patterns = [
        {
            "apparent_column_count": as_int(row.get("apparent_column_count")),
            "row_count": as_int(row.get("row_count")),
        }
        for row in distribution_rows
        if dominant is None
        or as_int(row.get("apparent_column_count")) != dominant_count
        or as_int(row.get("row_count")) != dominant_rows
    ]

    row_class_counts = {
        row.get("line_class", ""): as_int(row.get("count")) for row in row_format_rows
    }
    summary = {
        "generated_at_utc": utc_now(),
        "content_structure_root": content_structure_root.as_posix(),
        "output_root": "",
        "tim_schema_records": len(schema_rows),
        "dominant_column_count": dominant_count,
        "dominant_column_count_rows": dominant_rows,
        "secondary_column_count_patterns": secondary_patterns,
        "row_class_counts": row_class_counts,
        "semantic_mapping_status": "not_performed",
        "physical_value_interpretation": "forbidden",
        "residual_search": "forbidden",
        "model_fitting": "forbidden",
        "bridge_claim_gate": "closed",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return schema_rows, summary, warnings


def build_par_outputs(
    content_structure_root: Path,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any],
    list[str],
]:
    parameter_path = content_structure_root / PAR_PARAMETER_INVENTORY
    prefix_path = content_structure_root / PAR_PREFIX_GROUPS
    summary_path = content_structure_root / PAR_SUMMARY

    parameter_rows_in, warnings = read_csv_rows(parameter_path)
    prefix_rows_in, prefix_warnings = read_csv_rows(prefix_path)
    par_summary, summary_warnings = read_json_object(summary_path)
    warnings.extend(prefix_warnings)
    warnings.extend(summary_warnings)

    parameter_rows: list[dict[str, Any]] = []
    duplicate_rows: list[dict[str, Any]] = []
    for row in parameter_rows_in:
        parameter_name = row.get("parameter_name", "")
        prefix_group = parameter_prefix_group(parameter_name)
        occurrence_count = as_int(row.get("occurrence_count"))
        duplicate_flag = str(row.get("duplicate_flag", "")).lower() == "true"
        parameter_rows.append(
            {
                "source_file": PAR_PARAMETER_INVENTORY,
                "relative_path": row.get("relative_path", ""),
                "parameter_name": parameter_name,
                "prefix_group": prefix_group,
                "separator_type": row.get("separator_type", "unknown"),
                "value_format_class": row.get("value_format_class", "mixed_or_unknown"),
                "occurrence_count": occurrence_count,
                "duplicate_flag": str(duplicate_flag).lower(),
                "raw_value_presence_flag": "present_as_uninterpreted_text",
                "documentation_status": "observed_in_file",
                "semantic_status": "name_observed",
                "correction_state_relevance": "unresolved",
                "provenance_requirement": (
                    "public_documentation_required_before_interpretation"
                ),
            }
        )
        if duplicate_flag or occurrence_count > 1:
            duplicate_rows.append(
                {
                    "relative_path": row.get("relative_path", ""),
                    "parameter_name": parameter_name,
                    "occurrence_count": occurrence_count,
                    "duplicate_flag": str(duplicate_flag).lower(),
                    "semantic_status": "name_observed",
                    "required_followup": (
                        "public_documentation_required_before_interpretation"
                    ),
                }
            )

    prefix_rows: list[dict[str, Any]] = []
    for row in prefix_rows_in:
        prefix_rows.append(
            {
                "relative_path": row.get("relative_path", ""),
                "prefix_group": row.get("prefix_group", ""),
                "parameter_count": as_int(row.get("parameter_count")),
                "semantic_status": "lexical_group_observed",
                "documentation_status": "observed_in_file",
                "provenance_requirement": (
                    "public_documentation_required_before_interpretation"
                ),
            }
        )

    return parameter_rows, prefix_rows, duplicate_rows, par_summary, warnings


def build_correction_state_template() -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field_name in CORRECTION_STATE_FIELDS:
        rows.append(
            {
                "correction_state_field": field_name,
                "current_state": "unresolved",
                "allowed_values": "|".join(ALLOWED_CORRECTION_STATE_VALUES),
                "provenance_requirement": (
                    "public_documentation_required_before_value_reading"
                ),
                "assumption_policy": "forbidden_to_assume",
                "note": "Unknown is acceptable. Silent assumptions are not acceptable.",
            }
        )

    summary = {
        "generated_at_utc": utc_now(),
        "correction_state_fields_defined": len(rows),
        "unresolved_default_count": len(rows),
        "correction_state_layer_status": "template_created",
        "value_reading_gate_status": "not_opened",
        "physical_value_interpretation": "forbidden",
        "residual_search": "forbidden",
        "model_fitting": "forbidden",
        "bridge_claim_gate": "closed",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return rows, summary


def build_provenance_requirements(
    content_structure_root: Path,
) -> list[dict[str, Any]]:
    entries = [
        (
            "tim_schema_map",
            "observed_in_content_structure_output",
            content_structure_root / TIM_COLUMN_DISTRIBUTION,
            "medium",
            "Column-count patterns are structural only; semantic names require public documentation.",
        ),
        (
            "par_field_dictionary",
            "observed_in_content_structure_output",
            content_structure_root / PAR_PARAMETER_INVENTORY,
            "medium",
            "Parameter names are observed labels only; physical meaning is not assigned.",
        ),
        (
            "par_prefix_group_dictionary",
            "observed_in_content_structure_output",
            content_structure_root / PAR_PREFIX_GROUPS,
            "medium",
            "Prefix groups are lexical only.",
        ),
        (
            "par_duplicate_parameter_report",
            "observed_in_content_structure_output",
            content_structure_root / PAR_PARAMETER_INVENTORY,
            "medium",
            "Duplicate flags are structural only.",
        ),
        (
            "correction_state_template",
            "public_release_documentation_required",
            "",
            "unresolved",
            "Correction state defaults to unresolved. Silent assumptions are not acceptable.",
        ),
    ]

    rows = []
    for artifact_class, source_type, source_path, confidence, note in entries:
        rows.append(
            {
                "artifact_class": artifact_class,
                "provenance_source_type": source_type,
                "provenance_source_path": (
                    source_path.as_posix() if isinstance(source_path, Path) else source_path
                ),
                "provenance_confidence": confidence,
                "provenance_note": note,
                "semantic_claim_allowed": "false",
            }
        )
    return rows


def build_readout(
    warnings: list[str],
    tim_summary: dict[str, Any],
    par_summary: dict[str, Any],
    correction_summary: dict[str, Any],
    content_structure_root: Path,
) -> str:
    unresolved_items = [
        "TIM column semantic names require public documentation.",
        "PAR parameter meanings require public documentation.",
        "Correction-state fields default to unresolved.",
        "Value-reading gate is not opened.",
    ]
    stop_conditions = [
        "Stop if TIM columns cannot be mapped without undocumented assumptions.",
        "Stop if PAR parameter names require semantic overreach.",
        "Stop if correction-state fields cannot be represented.",
        "Stop if any output begins to frame values as evidence.",
    ]

    lines = [
        "# QSB-ST SHAPIROINFO57 Field Dictionary / Schema / Correction-State Readout",
        "",
        "## Purpose",
        "",
        "This readout reports dictionary, schema-map, correction-state, and provenance setup only.",
        "",
        "## Input Outputs Reviewed",
        "",
        f"- {content_structure_root.as_posix()}",
        "",
        "## TIM Schema-Map Summary",
        "",
        f"TIM schema records: {tim_summary.get('tim_schema_records')}",
        f"Dominant column count: {tim_summary.get('dominant_column_count')}",
        f"Dominant column-count rows: {tim_summary.get('dominant_column_count_rows')}",
        "Semantic mapping status: not_performed",
        "",
        "## PAR Dictionary Summary",
        "",
        f"PAR files found: {par_summary.get('par_files_found', 'unresolved')}",
        f"Total PAR lines: {par_summary.get('total_par_lines', 'unresolved')}",
        f"Total parameter-like lines: {par_summary.get('total_parameter_like_lines', 'unresolved')}",
        f"Unique parameter names: {par_summary.get('unique_parameter_names', 'unresolved')}",
        f"Duplicate parameter name count: {par_summary.get('duplicate_parameter_name_count', 'unresolved')}",
        "",
        "## Correction-State Summary",
        "",
        f"Correction-state fields defined: {correction_summary['correction_state_fields_defined']}",
        f"Unresolved default count: {correction_summary['unresolved_default_count']}",
        "Unknown is acceptable.",
        "Silent assumptions are not acceptable.",
        "",
        "## Unresolved Items",
        "",
    ]
    lines.extend([f"- {item}" for item in unresolved_items])
    lines.extend(["", "## Stop Conditions", ""])
    lines.extend([f"- {item}" for item in stop_conditions])
    lines.extend(["", "## Warnings", ""])
    lines.extend([f"- {warning}" for warning in warnings] or ["- none"])
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "This output does not provide evidence for a physical Shapiro-information residual.",
            "This output does not validate the QSB-ST Bridge.",
            "This output does not establish spacetime, quantum-gravity, relativistic, or pulsar-timing physics claims.",
            "This output does not interpret TIM or PAR values as physical evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    content_structure_root: Path,
    raw_structure_inventory_root: Path,
    raw_input_root: Path,
    output_root: Path,
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    warnings: list[str] = []

    tim_schema_rows, tim_summary, tim_warnings = build_tim_schema_map(
        content_structure_root
    )
    warnings.extend(tim_warnings)
    tim_summary["output_root"] = output_root.as_posix()

    (
        par_dictionary_rows,
        par_prefix_rows,
        duplicate_rows,
        par_summary,
        par_warnings,
    ) = build_par_outputs(content_structure_root)
    warnings.extend(par_warnings)

    correction_rows, correction_summary = build_correction_state_template()
    provenance_rows = build_provenance_requirements(content_structure_root)

    config = {
        "script": Path(__file__).as_posix(),
        "content_structure_root": content_structure_root.as_posix(),
        "raw_structure_inventory_root": raw_structure_inventory_root.as_posix(),
        "raw_input_root": raw_input_root.as_posix(),
        "output_root": output_root.as_posix(),
        "execution_scope": "dictionary_schema_correction_state_only",
        "physical_value_interpretation": "forbidden",
        "residual_search": "forbidden",
        "model_fitting": "forbidden",
        "anomaly_claims": "forbidden",
        "bridge_claim_gate": "closed",
        "raw_artifact_modification": "forbidden",
        "output_files": OUTPUT_FILES,
        "claim_boundary": CLAIM_BOUNDARY,
    }

    write_csv(
        output_root / "tim_schema_map.csv",
        [
            "source_file",
            "relative_path",
            "row_class",
            "apparent_column_count",
            "column_position",
            "observed_token_format_class",
            "missing_value_marker_present",
            "delimiter_hint",
            "row_count_for_column_count",
            "example_token_snippet_capped",
            "schema_confidence",
            "semantic_status",
            "provenance_source_type",
            "provenance_source_path",
            "provenance_source_reference",
        ],
        tim_schema_rows,
    )
    write_json(output_root / "tim_schema_summary.json", tim_summary)
    write_csv(
        output_root / "par_field_dictionary.csv",
        [
            "source_file",
            "relative_path",
            "parameter_name",
            "prefix_group",
            "separator_type",
            "value_format_class",
            "occurrence_count",
            "duplicate_flag",
            "raw_value_presence_flag",
            "documentation_status",
            "semantic_status",
            "correction_state_relevance",
            "provenance_requirement",
        ],
        par_dictionary_rows,
    )
    write_csv(
        output_root / "par_prefix_group_dictionary.csv",
        [
            "relative_path",
            "prefix_group",
            "parameter_count",
            "semantic_status",
            "documentation_status",
            "provenance_requirement",
        ],
        par_prefix_rows,
    )
    write_csv(
        output_root / "par_duplicate_parameter_report.csv",
        [
            "relative_path",
            "parameter_name",
            "occurrence_count",
            "duplicate_flag",
            "semantic_status",
            "required_followup",
        ],
        duplicate_rows,
    )
    write_csv(
        output_root / "correction_state_template.csv",
        [
            "correction_state_field",
            "current_state",
            "allowed_values",
            "provenance_requirement",
            "assumption_policy",
            "note",
        ],
        correction_rows,
    )
    write_json(output_root / "correction_state_summary.json", correction_summary)
    write_csv(
        output_root / "provenance_requirements.csv",
        [
            "artifact_class",
            "provenance_source_type",
            "provenance_source_path",
            "provenance_confidence",
            "provenance_note",
            "semantic_claim_allowed",
        ],
        provenance_rows,
    )
    readout = build_readout(
        warnings, tim_summary, par_summary, correction_summary, content_structure_root
    )
    (output_root / "field_dictionary_schema_correction_state_readout.md").write_text(
        readout, encoding="utf-8"
    )
    write_json(
        output_root / "field_dictionary_schema_correction_state_config_resolved.json",
        config,
    )


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a dictionary/schema/correction-state layer from generated "
            "QSB-ST ShapiroInfo content-structure outputs."
        )
    )
    parser.add_argument(
        "--content-structure-root",
        default=DEFAULT_CONTENT_STRUCTURE_ROOT.as_posix(),
        help="Root containing SHAPIROINFO53 content-structure outputs.",
    )
    parser.add_argument(
        "--raw-structure-inventory-root",
        default=DEFAULT_RAW_STRUCTURE_INVENTORY_ROOT.as_posix(),
        help="Root containing SHAPIROINFO39 raw-structure inventory outputs.",
    )
    parser.add_argument(
        "--raw-input-root",
        default=DEFAULT_RAW_INPUT_ROOT.as_posix(),
        help="Local raw input root. Not read by default by this script.",
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT.as_posix(),
        help="Output root for dictionary/schema/correction-state run artifacts.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    write_outputs(
        content_structure_root=Path(args.content_structure_root),
        raw_structure_inventory_root=Path(args.raw_structure_inventory_root),
        raw_input_root=Path(args.raw_input_root),
        output_root=Path(args.output_root),
    )
    print(f"wrote dictionary/schema/correction-state outputs under: {args.output_root}")
    print(CLAIM_BOUNDARY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
