#!/usr/bin/env python3
"""QSB-SHAPIROMART15 row-level receiver/backend context enrichment.

This script joins the SHAPIROMART13 geometric phase mapping to documented
SHAPIROMART11 row-level receiver/backend flags by the explicit source_row_index
key. It does not infer new receiver/backend semantics, choose thresholds, create
exposure classes, calculate Shapiro delay, inspect residuals, run a fit, open a
database, or create any extra decision mechanism.
"""

from __future__ import annotations

import argparse
import ast
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


RESEARCH_BLOCK = "QSB-SHAPIROMART15"
EXPECTED_ROW_COUNT = 7419

SHAPIROMART_BASE = Path("runs/QSB-SHAPIROMART")
SHAPIROMART11_DIR = SHAPIROMART_BASE / "SHAPIROMART11_CONTROLLED_PINT_RECONSTRUCTION"
SHAPIROMART12_DIR = SHAPIROMART_BASE / "SHAPIROMART12_ORBITAL_PHASE_AXIS_QC"
SHAPIROMART13_DIR = SHAPIROMART_BASE / "SHAPIROMART13_ELL1_GEOMETRIC_PHASE_MAPPING"
DEFAULT_OUTPUT_DIR = SHAPIROMART_BASE / "SHAPIROMART15_ROW_LEVEL_CONTEXT_ENRICHMENT"

DEFAULT_GEOMETRY_INPUT = SHAPIROMART13_DIR / "shapiromart13_phase_geometry_mapping.csv"
DEFAULT_CONTEXT_INPUT = SHAPIROMART11_DIR / "shapiromart11_toa_orbital_phase.csv"
DEFAULT_GEOMETRY_FINAL_STATUS_INPUT = SHAPIROMART13_DIR / "shapiromart13_final_status.csv"
DEFAULT_GEOMETRY_SUMMARY_JSON_INPUT = SHAPIROMART13_DIR / "shapiromart13_summary.json"
DEFAULT_CONTEXT_COUNT_INPUT = SHAPIROMART12_DIR / "shapiromart12_context_phase_coverage.csv"
DEFAULT_CONTEXT_SUMMARY_INPUT = (
    SHAPIROMART13_DIR / "shapiromart13_context_phase_distance_summary.csv"
)

READOUT_MD = "shapiromart15_readout.md"
SUMMARY_JSON = "shapiromart15_summary.json"
CONTEXT_SOURCE_INVENTORY_CSV = "shapiromart15_context_source_inventory.csv"
JOIN_KEY_ASSESSMENT_CSV = "shapiromart15_join_key_assessment.csv"
ROW_LEVEL_CONTEXT_MAPPING_CSV = "shapiromart15_row_level_context_mapping.csv"
ENRICHED_PHASE_GEOMETRY_CSV = "shapiromart15_enriched_phase_geometry.csv"
CONTEXT_COUNT_VALIDATION_CSV = "shapiromart15_context_count_validation.csv"
UNMATCHED_OR_AMBIGUOUS_ROWS_CSV = "shapiromart15_unmatched_or_ambiguous_rows.csv"
FINAL_STATUS_CSV = "shapiromart15_final_status.csv"

OUTPUT_FILES = [
    READOUT_MD,
    SUMMARY_JSON,
    CONTEXT_SOURCE_INVENTORY_CSV,
    JOIN_KEY_ASSESSMENT_CSV,
    ROW_LEVEL_CONTEXT_MAPPING_CSV,
    ENRICHED_PHASE_GEOMETRY_CSV,
    CONTEXT_COUNT_VALIDATION_CSV,
    UNMATCHED_OR_AMBIGUOUS_ROWS_CSV,
    FINAL_STATUS_CSV,
]

ALLOWED_CONTEXTS = {
    "Rcvr_800 / GUPPI": ("Rcvr_800", "GUPPI"),
    "Rcvr1_2 / GUPPI": ("Rcvr1_2", "GUPPI"),
}

EXPECTED_CONTEXT_COUNTS = {
    "Rcvr_800 / GUPPI": 2916,
    "Rcvr1_2 / GUPPI": 4503,
    "overall": EXPECTED_ROW_COUNT,
}

GEOMETRY_REQUIRED_FIELDS = [
    "source_row_index",
    "orbital_phase",
    "phase_origin",
    "phase_origin_role",
    "superior_conjunction_phase",
    "signed_phase_offset",
    "absolute_phase_distance",
    "nearest_reference_point",
    "phase_geometry_status",
    "phase_method",
    "notes",
]

CONTEXT_REQUIRED_FIELDS = [
    "source_row_index",
    "source_filename",
    "observatory",
    "observing_frequency_mhz",
    "toa_mjd_file",
    "orbital_phase",
    "phase_method",
    "calculation_status",
]

CONTEXT_SOURCE_INVENTORY_FIELDS = [
    "source_id",
    "source_path",
    "source_type",
    "row_count",
    "identity_fields",
    "receiver_field",
    "backend_field",
    "uniqueness_status",
    "mapping_status",
    "join_suitability",
    "notes",
]

JOIN_KEY_ASSESSMENT_FIELDS = [
    "join_candidate_id",
    "left_fields",
    "right_fields",
    "left_unique",
    "right_unique",
    "left_null_count",
    "right_null_count",
    "matched_row_count",
    "unmatched_left_count",
    "unmatched_right_count",
    "multiple_match_count",
    "join_status",
    "notes",
]

ROW_LEVEL_CONTEXT_MAPPING_FIELDS = [
    "source_row_index",
    "context_join_key",
    "receiver",
    "backend",
    "context_name",
    "context_source_id",
    "mapping_status",
    "notes",
]

CONTEXT_COUNT_VALIDATION_FIELDS = [
    "context_name",
    "expected_count",
    "observed_count",
    "count_difference",
    "count_match",
    "mapping_complete",
    "notes",
]

UNMATCHED_OR_AMBIGUOUS_ROWS_FIELDS = [
    "source_row_index",
    "join_key",
    "issue_type",
    "candidate_match_count",
    "candidate_contexts",
    "disposition",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "geometry_input_available",
    "context_source_available",
    "documented_join_key_available",
    "join_key_unique",
    "enriched_row_count",
    "expected_row_count",
    "unmatched_row_count",
    "ambiguous_row_count",
    "rcvr_800_count",
    "rcvr1_2_count",
    "context_totals_match",
    "receiver_backend_context_complete",
    "exposure_classes_created",
    "threshold_selected",
    "shapiro_delay_calculated",
    "residual_analysis_performed",
    "model_fit_performed",
    "physical_interpretation_performed",
    "tim_token_003_used",
    "record_index_used_as_time",
    "database_access",
    "database_modified",
    "additional_gate_created",
    "final_status",
    "main_remaining_gap",
    "recommended_next_action",
    "limitations",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Join SHAPIROMART13 phase geometry rows to documented SHAPIROMART11 "
            "row-level receiver/backend context."
        )
    )
    parser.add_argument("--geometry-input", type=Path, default=DEFAULT_GEOMETRY_INPUT)
    parser.add_argument("--context-input", type=Path, default=DEFAULT_CONTEXT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--join-key", default="source_row_index")
    parser.add_argument(
        "--geometry-final-status-input",
        type=Path,
        default=DEFAULT_GEOMETRY_FINAL_STATUS_INPUT,
    )
    parser.add_argument(
        "--geometry-summary-json-input",
        type=Path,
        default=DEFAULT_GEOMETRY_SUMMARY_JSON_INPUT,
    )
    parser.add_argument("--context-count-input", type=Path, default=DEFAULT_CONTEXT_COUNT_INPUT)
    parser.add_argument(
        "--context-summary-input",
        type=Path,
        default=DEFAULT_CONTEXT_SUMMARY_INPUT,
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def read_csv_rows(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def read_single_csv_row(path: Path) -> dict[str, str]:
    rows, _ = read_csv_rows(path)
    if len(rows) != 1:
        raise ValueError(f"Expected exactly one row in {path}, observed {len(rows)}.")
    return rows[0]


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"Expected a JSON object in {path}.")
    return payload


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def validate_output_dir(output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        present = sorted(path.name for path in output_dir.iterdir() if path.is_file())
        if present and not overwrite:
            raise FileExistsError(
                f"Output directory already contains files; use --overwrite: {output_dir}"
            )
        unexpected = sorted(set(present) - set(OUTPUT_FILES))
        if unexpected:
            raise FileExistsError(
                f"Output directory contains files outside the expected set: {unexpected}"
            )
    output_dir.mkdir(parents=True, exist_ok=True)


def require_fields(rows: list[dict[str, str]], fields: list[str], path: Path) -> None:
    if not rows:
        raise ValueError(f"Input has no rows: {path}")
    missing = sorted(set(fields) - set(rows[0].keys()))
    if missing:
        raise ValueError(f"Missing required fields in {path}: {missing}")


def decimal_integer_text(value: str) -> bool:
    return value == str(int(value)) if value.strip() else False


def validate_index_texts(rows: list[dict[str, str]], key: str, label: str) -> None:
    bad_values = [row.get(key, "") for row in rows if not decimal_integer_text(row.get(key, ""))]
    if bad_values:
        raise ValueError(
            f"{label} has non-stable source_row_index text values; examples={bad_values[:5]}"
        )


def validate_geometry_status(path: Path, summary_path: Path) -> dict[str, Any]:
    final_row = read_single_csv_row(path)
    summary = read_json(summary_path)
    expected = {
        "ell1_phase_axis_available": "yes",
        "phase_origin_tasc_supported": "yes",
        "superior_conjunction_mapping_supported": "yes",
        "geometric_phase_distance_generated": "yes",
        "geometric_phase_distance_row_count": str(EXPECTED_ROW_COUNT),
        "exposure_classes_created": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "model_fit_performed": "no",
        "database_access": "none",
        "additional_gate_created": "no",
        "final_status": "ell1_geometric_phase_mapping_supported",
    }
    failures = {
        key: {"expected": value, "observed": final_row.get(key, "")}
        for key, value in expected.items()
        if final_row.get(key, "") != value
    }
    if failures:
        raise ValueError(f"SHAPIROMART13 status validation failed: {failures}")
    return {"final_status": final_row, "summary": summary}


def load_geometry(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    rows, fields = read_csv_rows(path)
    require_fields(rows, GEOMETRY_REQUIRED_FIELDS, path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"Expected {EXPECTED_ROW_COUNT} geometry rows, observed {len(rows)}.")
    validate_index_texts(rows, "source_row_index", "geometry input")
    return rows, fields


def parse_context_flags(raw_flags: str) -> tuple[str, str, str]:
    try:
        parsed = ast.literal_eval(raw_flags)
    except (SyntaxError, ValueError):
        return "", "", "unparsed"
    if not isinstance(parsed, dict):
        return "", "", "unparsed"
    receiver = str(parsed.get("fe", "")).strip()
    backend = str(parsed.get("be", "")).strip()
    if receiver and backend:
        return receiver, backend, "parsed"
    return receiver, backend, "missing_receiver_or_backend"


def context_name(receiver: str, backend: str) -> str:
    return f"{receiver} / {backend}" if receiver and backend else ""


def load_context(path: Path) -> tuple[list[dict[str, Any]], list[str]]:
    rows, fields = read_csv_rows(path)
    require_fields(rows, CONTEXT_REQUIRED_FIELDS, path)
    if len(rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"Expected {EXPECTED_ROW_COUNT} context rows, observed {len(rows)}.")
    validate_index_texts(rows, "source_row_index", "context input")

    parsed_rows: list[dict[str, Any]] = []
    for row in rows:
        receiver, backend, parse_status = parse_context_flags(row["source_filename"])
        name = context_name(receiver, backend)
        mapping_status = (
            "mapped"
            if parse_status == "parsed" and name in ALLOWED_CONTEXTS
            else "unsupported_context"
        )
        parsed = dict(row)
        parsed.update(
            {
                "_receiver": receiver,
                "_backend": backend,
                "_context_name": name,
                "_flag_parse_status": parse_status,
                "_context_mapping_status": mapping_status,
            }
        )
        parsed_rows.append(parsed)
    return parsed_rows, fields


def unique_status(rows: list[dict[str, Any]], key: str) -> tuple[bool, int, int]:
    values = [str(row.get(key, "")) for row in rows]
    null_count = sum(1 for value in values if value == "")
    counts = Counter(values)
    duplicate_value_count = sum(1 for value, count in counts.items() if value and count > 1)
    return duplicate_value_count == 0 and null_count == 0, null_count, duplicate_value_count


def build_context_source_inventory(
    context_rows: list[dict[str, Any]],
    context_path: Path,
    context_count_path: Path,
    context_summary_path: Path,
) -> list[dict[str, Any]]:
    direct_unique, _, duplicate_count = unique_status(context_rows, "source_row_index")
    direct_counts = Counter(row["_context_name"] for row in context_rows)
    direct_count_note = "; ".join(
        f"{name}={direct_counts.get(name, 0)}" for name in ["Rcvr_800 / GUPPI", "Rcvr1_2 / GUPPI"]
    )
    context_count_rows, _ = read_csv_rows(context_count_path)
    context_summary_rows, _ = read_csv_rows(context_summary_path)
    return [
        {
            "source_id": "SHAPIROMART11_TOA_ORBITAL_PHASE",
            "source_path": str(context_path),
            "source_type": "row_level_phase_export",
            "row_count": len(context_rows),
            "identity_fields": "source_row_index",
            "receiver_field": "source_filename.fe",
            "backend_field": "source_filename.be",
            "uniqueness_status": "unique" if direct_unique else f"duplicate_key_count={duplicate_count}",
            "mapping_status": "direct_row_key_available",
            "join_suitability": "selected",
            "notes": (
                "Receiver/backend context is read from documented exported PINT flag "
                f"dictionary fields. Counts: {direct_count_note}."
            ),
        },
        {
            "source_id": "SHAPIROMART12_CONTEXT_PHASE_COVERAGE",
            "source_path": str(context_count_path),
            "source_type": "context_summary_counts",
            "row_count": len(context_count_rows),
            "identity_fields": "context_name",
            "receiver_field": "receiver",
            "backend_field": "backend",
            "uniqueness_status": "context_name_summary",
            "mapping_status": "summary_only",
            "join_suitability": "not_selected_summary_only",
            "notes": "Useful for count validation, not for row-level enrichment.",
        },
        {
            "source_id": "SHAPIROMART13_CONTEXT_PHASE_DISTANCE_SUMMARY",
            "source_path": str(context_summary_path),
            "source_type": "context_distance_summary",
            "row_count": len(context_summary_rows),
            "identity_fields": "context_name",
            "receiver_field": "",
            "backend_field": "",
            "uniqueness_status": "context_name_summary",
            "mapping_status": "summary_only",
            "join_suitability": "not_selected_summary_only",
            "notes": "Useful as prior context summary only, not for row-level enrichment.",
        },
    ]


def build_join_assessment(
    geometry_rows: list[dict[str, str]],
    context_rows: list[dict[str, Any]],
    join_key: str,
) -> tuple[dict[str, Any], dict[str, list[dict[str, Any]]], list[dict[str, Any]]]:
    if join_key != "source_row_index":
        raise ValueError(
            "This script has one documented join path. Pass --join-key source_row_index."
        )
    left_unique, left_null_count, left_duplicate_value_count = unique_status(
        geometry_rows, join_key
    )
    right_unique, right_null_count, right_duplicate_value_count = unique_status(
        context_rows, join_key
    )

    right_by_key: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in context_rows:
        right_by_key[str(row[join_key])].append(row)

    left_keys = [str(row[join_key]) for row in geometry_rows]
    right_keys = [str(row[join_key]) for row in context_rows]
    left_set = set(left_keys)
    right_set = set(right_keys)
    matched_row_count = sum(1 for key in left_keys if len(right_by_key.get(key, [])) == 1)
    unmatched_left_count = sum(1 for key in left_keys if key not in right_set)
    unmatched_right_count = sum(1 for key in right_keys if key not in left_set)
    multiple_match_count = sum(1 for key in left_keys if len(right_by_key.get(key, [])) > 1)

    issue_rows: list[dict[str, Any]] = []
    for left_row in geometry_rows:
        key = str(left_row[join_key])
        candidates = right_by_key.get(key, [])
        if len(candidates) == 1:
            continue
        candidate_contexts = sorted({row.get("_context_name", "") for row in candidates})
        issue_rows.append(
            {
                "source_row_index": left_row["source_row_index"],
                "join_key": key,
                "issue_type": "unmatched" if not candidates else "ambiguous",
                "candidate_match_count": len(candidates),
                "candidate_contexts": ";".join(candidate_contexts),
                "disposition": "not_enriched",
                "notes": "No artificial receiver/backend assignment was made.",
            }
        )

    if not left_unique or not right_unique:
        join_status = "duplicate_join_key"
    elif unmatched_left_count or unmatched_right_count or multiple_match_count:
        join_status = "partial_or_unmatched"
    else:
        join_status = "complete_unique_match"

    assessment = {
        "join_candidate_id": "SOURCE_ROW_INDEX",
        "left_fields": join_key,
        "right_fields": join_key,
        "left_unique": "yes" if left_unique else "no",
        "right_unique": "yes" if right_unique else "no",
        "left_null_count": left_null_count,
        "right_null_count": right_null_count,
        "matched_row_count": matched_row_count,
        "unmatched_left_count": unmatched_left_count,
        "unmatched_right_count": unmatched_right_count,
        "multiple_match_count": multiple_match_count
        + left_duplicate_value_count
        + right_duplicate_value_count,
        "join_status": join_status,
        "notes": (
            "Join uses exact source_row_index text keys; no row-order, fuzzy, "
            "numeric-similarity, tim token, or time-based key was used."
        ),
    }
    return assessment, right_by_key, issue_rows


def build_context_mapping_rows(
    geometry_rows: list[dict[str, str]],
    right_by_key: dict[str, list[dict[str, Any]]],
    join_key: str,
) -> list[dict[str, Any]]:
    mapping_rows: list[dict[str, Any]] = []
    for row in geometry_rows:
        key = str(row[join_key])
        candidates = right_by_key.get(key, [])
        if len(candidates) != 1:
            continue
        candidate = candidates[0]
        mapping_rows.append(
            {
                "source_row_index": row["source_row_index"],
                "context_join_key": key,
                "receiver": candidate["_receiver"],
                "backend": candidate["_backend"],
                "context_name": candidate["_context_name"],
                "context_source_id": "SHAPIROMART11_TOA_ORBITAL_PHASE",
                "mapping_status": candidate["_context_mapping_status"],
                "notes": "Exact source_row_index match to documented row-level context.",
            }
        )
    return mapping_rows


def build_enriched_rows(
    geometry_rows: list[dict[str, str]],
    geometry_fields: list[str],
    mapping_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    mapping_by_source = {row["source_row_index"]: row for row in mapping_rows}
    enriched_rows: list[dict[str, Any]] = []
    for row in geometry_rows:
        mapped = mapping_by_source.get(row["source_row_index"])
        if not mapped:
            continue
        enriched = dict(row)
        enriched.update(
            {
                "receiver": mapped["receiver"],
                "backend": mapped["backend"],
                "context_name": mapped["context_name"],
                "context_source_id": mapped["context_source_id"],
                "context_join_key": mapped["context_join_key"],
                "context_mapping_status": mapped["mapping_status"],
            }
        )
        enriched_rows.append(enriched)
    fields = geometry_fields + [
        "receiver",
        "backend",
        "context_name",
        "context_source_id",
        "context_join_key",
        "context_mapping_status",
    ]
    return enriched_rows, fields


def build_count_validation_rows(mapping_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = Counter(row["context_name"] for row in mapping_rows if row["mapping_status"] == "mapped")
    rows: list[dict[str, Any]] = []
    for name in ["Rcvr_800 / GUPPI", "Rcvr1_2 / GUPPI", "overall"]:
        expected = EXPECTED_CONTEXT_COUNTS[name]
        observed = len(mapping_rows) if name == "overall" else counts.get(name, 0)
        difference = observed - expected
        rows.append(
            {
                "context_name": name,
                "expected_count": expected,
                "observed_count": observed,
                "count_difference": difference,
                "count_match": "yes" if difference == 0 else "no",
                "mapping_complete": "yes" if observed == expected else "no",
                "notes": "Count validation only; no threshold or exposure class assigned.",
            }
        )
    return rows


def determine_final_status(
    join_assessment: dict[str, Any],
    mapping_rows: list[dict[str, Any]],
    issue_rows: list[dict[str, Any]],
    count_validation_rows: list[dict[str, Any]],
) -> str:
    if join_assessment["join_status"] == "duplicate_join_key":
        return "row_level_context_enrichment_inconsistent"
    if join_assessment["matched_row_count"] == 0:
        return "row_level_context_enrichment_unresolved"
    unmatched = sum(1 for row in issue_rows if row["issue_type"] == "unmatched")
    ambiguous = sum(1 for row in issue_rows if row["issue_type"] == "ambiguous")
    totals_match = all(row["count_match"] == "yes" for row in count_validation_rows)
    if len(mapping_rows) == EXPECTED_ROW_COUNT and unmatched == 0 and ambiguous == 0 and totals_match:
        return "row_level_context_enrichment_complete"
    if not totals_match:
        return "row_level_context_enrichment_inconsistent"
    return "row_level_context_enrichment_partial"


def build_final_status_row(
    join_assessment: dict[str, Any],
    mapping_rows: list[dict[str, Any]],
    issue_rows: list[dict[str, Any]],
    count_validation_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    counts = Counter(row["context_name"] for row in mapping_rows if row["mapping_status"] == "mapped")
    unmatched = sum(1 for row in issue_rows if row["issue_type"] == "unmatched")
    ambiguous = sum(1 for row in issue_rows if row["issue_type"] == "ambiguous")
    totals_match = all(row["count_match"] == "yes" for row in count_validation_rows)
    final_status = determine_final_status(
        join_assessment, mapping_rows, issue_rows, count_validation_rows
    )
    if final_status == "row_level_context_enrichment_complete":
        main_gap = ""
        recommended = (
            "Use the enriched row-level mapping as the context-bearing input for a "
            "separately specified later descriptive context symmetry block."
        )
        limitations = (
            "Receiver/backend context is carried from documented SHAPIROMART11 "
            "exported flag fields; no new context semantics were inferred."
        )
    elif final_status == "row_level_context_enrichment_unresolved":
        main_gap = "No documented row-level one-to-one context join was available."
        recommended = "Specify or create a documented row-level context source before enrichment."
        limitations = "No artificial row-level receiver/backend mapping was generated."
    elif final_status == "row_level_context_enrichment_inconsistent":
        main_gap = "Join or context totals were inconsistent."
        recommended = "Audit the documented row identity and context count sources before reuse."
        limitations = "Enrichment result should not be used for context symmetry until resolved."
    else:
        main_gap = "Some rows remain unmatched or ambiguous."
        recommended = "Audit the unmatched or ambiguous row inventory before reuse."
        limitations = "Only uniquely matched rows were enriched."

    return {
        "research_block": RESEARCH_BLOCK,
        "geometry_input_available": "yes",
        "context_source_available": "yes" if mapping_rows else "no",
        "documented_join_key_available": "yes"
        if join_assessment["join_candidate_id"] == "SOURCE_ROW_INDEX"
        else "no",
        "join_key_unique": "yes"
        if join_assessment["left_unique"] == "yes" and join_assessment["right_unique"] == "yes"
        else "no",
        "enriched_row_count": len(mapping_rows),
        "expected_row_count": EXPECTED_ROW_COUNT,
        "unmatched_row_count": unmatched,
        "ambiguous_row_count": ambiguous,
        "rcvr_800_count": counts.get("Rcvr_800 / GUPPI", 0),
        "rcvr1_2_count": counts.get("Rcvr1_2 / GUPPI", 0),
        "context_totals_match": "yes" if totals_match else "no",
        "receiver_backend_context_complete": "yes"
        if len(mapping_rows) == EXPECTED_ROW_COUNT and totals_match
        else "no",
        "exposure_classes_created": "no",
        "threshold_selected": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "model_fit_performed": "no",
        "physical_interpretation_performed": "no",
        "tim_token_003_used": "no",
        "record_index_used_as_time": "no",
        "database_access": "none",
        "database_modified": "no",
        "additional_gate_created": "no",
        "final_status": final_status,
        "main_remaining_gap": main_gap,
        "recommended_next_action": recommended,
        "limitations": limitations,
    }


def build_readout(
    geometry_rows: list[dict[str, str]],
    context_rows: list[dict[str, Any]],
    inventory_rows: list[dict[str, Any]],
    join_assessment: dict[str, Any],
    mapping_rows: list[dict[str, Any]],
    count_validation_rows: list[dict[str, Any]],
    issue_rows: list[dict[str, Any]],
    final_status_row: dict[str, Any],
) -> str:
    context_counts = Counter(row["context_name"] for row in mapping_rows)
    source_lines = [
        (
            f"- {row['source_id']}: status={row['mapping_status']}, "
            f"suitability={row['join_suitability']}, rows={row['row_count']}"
        )
        for row in inventory_rows
    ]
    count_lines = [
        (
            f"- {row['context_name']}: expected={row['expected_count']}, "
            f"observed={row['observed_count']}, match={row['count_match']}"
        )
        for row in count_validation_rows
    ]
    return "\n".join(
        [
            "# SHAPIROMART15 Readout",
            "",
            "## 1. Purpose",
            (
                "Establish a row-level receiver/backend context link for the "
                "SHAPIROMART13 geometric phase mapping using documented existing "
                "row identity."
            ),
            "",
            "## 2. Input Geometry Mapping",
            f"Geometry rows read: {len(geometry_rows)}.",
            "Required geometry fields were present, including source_row_index.",
            "",
            "## 3. Available Context Sources",
            *source_lines,
            "",
            "## 4. Candidate Join Keys",
            (
                f"Selected candidate: {join_assessment['join_candidate_id']}. "
                f"Left unique={join_assessment['left_unique']}; "
                f"right unique={join_assessment['right_unique']}; "
                f"matched rows={join_assessment['matched_row_count']}."
            ),
            (
                "The join used exact source_row_index text values. No row order, "
                "fuzzy match, numeric-similarity match, or time substitute was used."
            ),
            "",
            "## 5. Selected Join Path",
            (
                "SHAPIROMART13 source_row_index was joined to SHAPIROMART11 "
                "source_row_index. Receiver/backend values were copied from "
                "source_filename flag fields fe and be."
            ),
            "",
            "## 6. Row-Level Mapping Result",
            f"Context rows read: {len(context_rows)}.",
            f"Enriched rows: {len(mapping_rows)}.",
            f"Rcvr_800 / GUPPI rows: {context_counts.get('Rcvr_800 / GUPPI', 0)}.",
            f"Rcvr1_2 / GUPPI rows: {context_counts.get('Rcvr1_2 / GUPPI', 0)}.",
            "",
            "## 7. Context Count Validation",
            *count_lines,
            "",
            "## 8. Unmatched or Ambiguous Rows",
            f"Unmatched rows: {final_status_row['unmatched_row_count']}.",
            f"Ambiguous rows: {final_status_row['ambiguous_row_count']}.",
            (
                "The unmatched-or-ambiguous inventory contains only the header "
                "when no such rows exist."
                if not issue_rows
                else "See the unmatched-or-ambiguous inventory for row-level details."
            ),
            "",
            "## 9. Final Status",
            f"final_status = {final_status_row['final_status']}.",
            "",
            "## 10. Recommended Next Action",
            str(final_status_row["recommended_next_action"]),
            "",
            "## 11. Limitations",
            str(final_status_row["limitations"]),
            "threshold_selected = no.",
            "exposure_classes_created = no.",
            "shapiro_delay_calculated = no.",
            "residual_analysis_performed = no.",
            "model_fit_performed = no.",
            "physical_interpretation_performed = no.",
            "additional_gate_created = no.",
            "",
        ]
    )


def build_summary_json(
    args: argparse.Namespace,
    inventory_rows: list[dict[str, Any]],
    join_assessment: dict[str, Any],
    mapping_rows: list[dict[str, Any]],
    count_validation_rows: list[dict[str, Any]],
    issue_rows: list[dict[str, Any]],
    final_status_row: dict[str, Any],
) -> dict[str, Any]:
    context_counts = Counter(row["context_name"] for row in mapping_rows)
    return {
        "research_block": RESEARCH_BLOCK,
        "inputs_read": {
            "geometry_input": str(args.geometry_input),
            "context_input": str(args.context_input),
            "geometry_final_status_input": str(args.geometry_final_status_input),
            "geometry_summary_json_input": str(args.geometry_summary_json_input),
            "context_count_input": str(args.context_count_input),
            "context_summary_input": str(args.context_summary_input),
        },
        "selected_join_key": args.join_key,
        "context_source_inventory": inventory_rows,
        "join_key_assessment": join_assessment,
        "row_level_mapping": {
            "matched_rows": len(mapping_rows),
            "unmatched_rows": final_status_row["unmatched_row_count"],
            "ambiguous_rows": final_status_row["ambiguous_row_count"],
            "context_counts": dict(context_counts),
        },
        "context_count_validation": count_validation_rows,
        "unmatched_or_ambiguous_row_count": len(issue_rows),
        "boundaries": {
            "exposure_classes_created": "no",
            "threshold_selected": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "model_fit_performed": "no",
            "physical_interpretation_performed": "no",
            "tim_token_003_used": "no",
            "record_index_used_as_time": "no",
            "database_access": "none",
            "database_modified": "no",
            "additional_gate_created": "no",
        },
        "final_status": final_status_row,
        "output_dir": str(args.output_dir),
    }


def verify_expected_outputs(output_dir: Path) -> None:
    observed = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    expected = sorted(OUTPUT_FILES)
    if observed != expected:
        raise RuntimeError(
            f"Output file set mismatch. Expected {expected}, observed {observed}."
        )


def validate_no_invalid_phase_values(rows: list[dict[str, str]]) -> None:
    for row in rows:
        orbital_phase = float(row["orbital_phase"])
        signed_offset = float(row["signed_phase_offset"])
        absolute_distance = float(row["absolute_phase_distance"])
        if not (math.isfinite(orbital_phase) and 0.0 <= orbital_phase < 1.0):
            raise ValueError(f"Invalid orbital_phase at source_row_index={row['source_row_index']}")
        if not (math.isfinite(signed_offset) and -0.5 <= signed_offset < 0.5):
            raise ValueError(
                f"Invalid signed_phase_offset at source_row_index={row['source_row_index']}"
            )
        if not (math.isfinite(absolute_distance) and 0.0 <= absolute_distance <= 0.5):
            raise ValueError(
                f"Invalid absolute_phase_distance at source_row_index={row['source_row_index']}"
            )


def main() -> None:
    args = parse_args()
    validate_output_dir(args.output_dir, args.overwrite)
    if args.join_key != "source_row_index":
        raise ValueError(
            "The join key is explicit and must be source_row_index for this block."
        )

    geometry_status = validate_geometry_status(
        args.geometry_final_status_input,
        args.geometry_summary_json_input,
    )
    del geometry_status

    geometry_rows, geometry_fields = load_geometry(args.geometry_input)
    validate_no_invalid_phase_values(geometry_rows)
    context_rows, _ = load_context(args.context_input)
    inventory_rows = build_context_source_inventory(
        context_rows,
        args.context_input,
        args.context_count_input,
        args.context_summary_input,
    )
    join_assessment, right_by_key, issue_rows = build_join_assessment(
        geometry_rows, context_rows, args.join_key
    )
    mapping_rows = build_context_mapping_rows(geometry_rows, right_by_key, args.join_key)
    enriched_rows, enriched_fields = build_enriched_rows(
        geometry_rows, geometry_fields, mapping_rows
    )
    count_validation_rows = build_count_validation_rows(mapping_rows)
    final_status_row = build_final_status_row(
        join_assessment, mapping_rows, issue_rows, count_validation_rows
    )
    readout = build_readout(
        geometry_rows,
        context_rows,
        inventory_rows,
        join_assessment,
        mapping_rows,
        count_validation_rows,
        issue_rows,
        final_status_row,
    )
    summary = build_summary_json(
        args,
        inventory_rows,
        join_assessment,
        mapping_rows,
        count_validation_rows,
        issue_rows,
        final_status_row,
    )

    write_text(args.output_dir / READOUT_MD, readout)
    write_json(args.output_dir / SUMMARY_JSON, summary)
    write_csv(
        args.output_dir / CONTEXT_SOURCE_INVENTORY_CSV,
        inventory_rows,
        CONTEXT_SOURCE_INVENTORY_FIELDS,
    )
    write_csv(
        args.output_dir / JOIN_KEY_ASSESSMENT_CSV,
        [join_assessment],
        JOIN_KEY_ASSESSMENT_FIELDS,
    )
    write_csv(
        args.output_dir / ROW_LEVEL_CONTEXT_MAPPING_CSV,
        mapping_rows,
        ROW_LEVEL_CONTEXT_MAPPING_FIELDS,
    )
    write_csv(args.output_dir / ENRICHED_PHASE_GEOMETRY_CSV, enriched_rows, enriched_fields)
    write_csv(
        args.output_dir / CONTEXT_COUNT_VALIDATION_CSV,
        count_validation_rows,
        CONTEXT_COUNT_VALIDATION_FIELDS,
    )
    write_csv(
        args.output_dir / UNMATCHED_OR_AMBIGUOUS_ROWS_CSV,
        issue_rows,
        UNMATCHED_OR_AMBIGUOUS_ROWS_FIELDS,
    )
    write_csv(args.output_dir / FINAL_STATUS_CSV, [final_status_row], FINAL_STATUS_FIELDS)
    verify_expected_outputs(args.output_dir)


if __name__ == "__main__":
    main()
