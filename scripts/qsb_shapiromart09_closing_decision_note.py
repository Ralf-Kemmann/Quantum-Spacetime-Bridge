#!/usr/bin/env python3
"""QSB-SHAPIROMART09 closing decision note.

This script consolidates existing SHAPIROMART08 and SHAPIROMART09 Step 2
outputs into the single SHAPIROMART09 closing decision. It performs no DB
access, no raw-data inspection, no new evidence search, no data analysis, and
no promotion.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart09_closing_decision_note.py"
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/"
    "SHAPIROMART09_DATASET_SPECIFIC_TIM_FORMAT_EVIDENCE_ACQUISITION"
)

SHAPIROMART08_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART08_PAR_TIM_SEMANTIC_EVIDENCE_REVIEW"
)
SHAPIROMART09_ROOT = DEFAULT_OUTPUT_ROOT

SHAPIROMART08_SUMMARY_JSON = SHAPIROMART08_ROOT / "shapiromart08_summary.json"
SHAPIROMART08_SELECTED_STATUS_CSV = (
    SHAPIROMART08_ROOT / "shapiromart08_selected_candidate_status.csv"
)
SHAPIROMART09_MAPPING_SUMMARY_JSON = (
    SHAPIROMART09_ROOT / "shapiromart09_mapping_assessment_summary.json"
)
SHAPIROMART09_STEP2_STATUS_CSV = SHAPIROMART09_ROOT / "shapiromart09_step2_status.csv"
SHAPIROMART09_SOURCE_IDENTITY_CSV = (
    SHAPIROMART09_ROOT / "shapiromart09_source_identity.csv"
)
SHAPIROMART09_MAPPING_CONSISTENCY_CSV = (
    SHAPIROMART09_ROOT / "shapiromart09_mapping_consistency.csv"
)

SCRIPT_08 = Path("scripts/qsb_shapiromart08_par_tim_semantic_evidence_review.py")
SCRIPT_09_STEP2 = Path("scripts/qsb_shapiromart09_exact_token_mapping_assessment.py")

CLOSING_NOTE_MD = "shapiromart09_closing_decision_note.md"
CLOSING_SUMMARY_JSON = "shapiromart09_closing_decision_summary.json"
CLOSING_DECISION_CSV = "shapiromart09_closing_decision.csv"

CLOSING_OUTPUT_FILENAMES = [
    CLOSING_NOTE_MD,
    CLOSING_SUMMARY_JSON,
    CLOSING_DECISION_CSV,
]

DECISION_FIELDS = [
    "research_block",
    "decision_type",
    "first_reviewed_candidate",
    "candidates_reviewed",
    "sources_inspected",
    "exact_mappings_found",
    "strongest_mapping_class",
    "prior_semantic_status",
    "mapping_assessment_status",
    "documented_semantic_role",
    "exact_token_semantic_support_sufficient",
    "promotion_allowed",
    "promotion_applied",
    "final_status",
    "record_index_role",
    "geometry_axis_available",
    "exposure_axis_available",
    "shapiro_anchor_available",
    "conflict_found",
    "main_remaining_gap",
    "recommended_future_action",
    "additional_gate_created",
]

TARGET_CANDIDATE = "raw_field_value.tim_token_003"
RECORD_INDEX_CANDIDATE = "raw_record.record_index"

RECOMMENDED_FUTURE_ACTION = (
    "Obtain dataset-specific format, parser, writer, or toolchain "
    "documentation that maps normalized data-line position 3 / tim_token_003 "
    "explicitly to a documented semantic role."
)

MAIN_REMAINING_GAP_FALLBACK = (
    "Dataset-specific documentation is still needed for the exact "
    "position-to-semantic-role relation for normalized data-line position 3 / "
    "tim_token_003."
)

PROHIBITED_PROMOTIONS = [
    "observation_time",
    "pulse_phase",
    "toa_value",
    "geometry_axis",
    "exposure_axis",
    "shapiro_related_comparison_anchor",
]

INPUT_OUTPUT_PATHS = [
    SHAPIROMART08_SUMMARY_JSON,
    SHAPIROMART08_SELECTED_STATUS_CSV,
    SHAPIROMART09_MAPPING_SUMMARY_JSON,
    SHAPIROMART09_STEP2_STATUS_CSV,
    SHAPIROMART09_SOURCE_IDENTITY_CSV,
    SHAPIROMART09_MAPPING_CONSISTENCY_CSV,
]

SOURCE_FILE_PATHS = [SCRIPT_08, SCRIPT_09_STEP2]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    raise RuntimeError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": file_sha256(path),
    }


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def closing_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in CLOSING_OUTPUT_FILENAMES}


def ensure_inputs_and_targets(args: argparse.Namespace) -> None:
    if not args.output_root.exists():
        fail(f"Output root does not exist: {args.output_root}")
    for path in INPUT_OUTPUT_PATHS + SOURCE_FILE_PATHS:
        if not path.exists():
            fail(f"Required input is missing: {path}")
    existing = [
        str(path)
        for path in closing_paths(args.output_root).values()
        if path.exists()
    ]
    if existing and not args.overwrite_closing_files:
        fail(
            "Closing output file(s) already exist. Re-run with "
            "--overwrite-closing-files to replace only these files: "
            + "; ".join(existing)
        )


def script_read_record(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    record = file_record(path)
    record["line_count"] = len(text.splitlines())
    return record


def single_row(rows: list[dict[str, str]], label: str) -> dict[str, str]:
    if len(rows) != 1:
        fail(f"Expected exactly one row in {label}, found {len(rows)}.")
    return rows[0]


def candidate_status(
    shapiromart08_summary: dict[str, Any],
    candidate: str,
) -> dict[str, Any]:
    for row in shapiromart08_summary.get("candidate_statuses", []):
        if row.get("candidate") == candidate:
            return row
    fail(f"Candidate status not found in SHAPIROMART08 summary: {candidate}")


def expect_equal(actual: Any, expected: Any, label: str) -> dict[str, Any]:
    passed = str(actual) == str(expected)
    if not passed:
        fail(f"{label} mismatch: expected {expected!r}, actual {actual!r}")
    return {
        "check": label,
        "expected": expected,
        "actual": actual,
        "passed": True,
    }


def derive_decision(
    shapiromart08_summary: dict[str, Any],
    shapiromart08_selected: dict[str, str],
    shapiromart09_summary: dict[str, Any],
    shapiromart09_status: dict[str, str],
    source_identity_rows: list[dict[str, str]],
    consistency_row: dict[str, str],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    validations: list[dict[str, Any]] = []

    prior_candidate_status = candidate_status(shapiromart08_summary, TARGET_CANDIDATE)
    record_index_status = candidate_status(shapiromart08_summary, RECORD_INDEX_CANDIDATE)

    validations.append(
        expect_equal(
            shapiromart08_summary.get("candidate_reviewed_first"),
            TARGET_CANDIDATE,
            "SHAPIROMART08 first reviewed candidate",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_summary.get("first_reviewed_candidate"),
            TARGET_CANDIDATE,
            "SHAPIROMART09 Step 2 first reviewed candidate",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_status.get("first_reviewed"),
            "yes",
            "tim_token_003 first checked in Step 2 status",
        )
    )
    validations.append(
        expect_equal(
            shapiromart08_summary.get("candidate_review_count"),
            4,
            "SHAPIROMART08 candidate count",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_summary.get("candidate_review_count"),
            4,
            "SHAPIROMART09 candidate count",
        )
    )
    validations.append(
        expect_equal(
            prior_candidate_status.get("final_status"),
            "insufficient_semantic_evidence",
            "SHAPIROMART08 target semantic status",
        )
    )
    validations.append(
        expect_equal(
            shapiromart08_selected.get("promotion_allowed"),
            "no",
            "SHAPIROMART08 promotion allowed",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_summary.get("exact_mappings_found"),
            0,
            "SHAPIROMART09 exact mappings found",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_summary.get("strongest_mapping_class"),
            "no_mapping_found",
            "SHAPIROMART09 strongest mapping class",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_status.get("assessment_status"),
            "exact_token_role_unresolved",
            "SHAPIROMART09 assessment status",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_status.get("documented_semantic_role"),
            "unresolved",
            "SHAPIROMART09 documented semantic role",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_status.get("promotion_applied"),
            "no",
            "SHAPIROMART09 promotion applied",
        )
    )
    validations.append(
        expect_equal(
            shapiromart09_status.get("promotion_evaluated"),
            "no",
            "SHAPIROMART09 promotion evaluated",
        )
    )
    validations.append(
        expect_equal(
            record_index_status.get("documented_role"),
            "record_order_only",
            "record_index retained role",
        )
    )

    conflict_count = str(consistency_row.get("conflicting_source_count", "0"))
    validations.append(
        expect_equal(conflict_count, "0", "SHAPIROMART09 conflicting source count")
    )

    sources_inspected = len(source_identity_rows)
    validations.append(
        expect_equal(sources_inspected, 20, "SHAPIROMART09 source identity row count")
    )

    main_remaining_gap = (
        shapiromart09_status.get("main_remaining_gap")
        or shapiromart09_summary.get("main_remaining_gap")
        or MAIN_REMAINING_GAP_FALLBACK
    )

    decision = {
        "research_block": "QSB-SHAPIROMART09",
        "decision_type": "closing_decision",
        "first_reviewed_candidate": TARGET_CANDIDATE,
        "candidates_reviewed": str(shapiromart08_summary.get("candidate_review_count")),
        "sources_inspected": str(sources_inspected),
        "exact_mappings_found": str(shapiromart09_summary.get("exact_mappings_found")),
        "strongest_mapping_class": str(shapiromart09_summary.get("strongest_mapping_class")),
        "prior_semantic_status": str(prior_candidate_status.get("final_status")),
        "mapping_assessment_status": str(shapiromart09_status.get("assessment_status")),
        "documented_semantic_role": str(shapiromart09_status.get("documented_semantic_role")),
        "exact_token_semantic_support_sufficient": "no",
        "promotion_allowed": "no",
        "promotion_applied": "no",
        "final_status": "exact_token_role_unresolved",
        "record_index_role": str(record_index_status.get("documented_role")),
        "geometry_axis_available": "no",
        "exposure_axis_available": "no",
        "shapiro_anchor_available": "no",
        "conflict_found": "no",
        "main_remaining_gap": main_remaining_gap,
        "recommended_future_action": RECOMMENDED_FUTURE_ACTION,
        "additional_gate_created": "no",
    }

    expected_decision_values = {
        "exact_token_semantic_support_sufficient": "no",
        "promotion_allowed": "no",
        "promotion_applied": "no",
        "final_status": "exact_token_role_unresolved",
        "record_index_role": "record_order_only",
        "geometry_axis_available": "no",
        "exposure_axis_available": "no",
        "shapiro_anchor_available": "no",
        "conflict_found": "no",
        "additional_gate_created": "no",
    }
    for key, expected in expected_decision_values.items():
        validations.append(expect_equal(decision[key], expected, f"closing decision {key}"))

    return decision, validations


def write_markdown(path: Path, decision: dict[str, str]) -> None:
    lines = [
        "# QSB-SHAPIROMART09 Closing Decision Note",
        "",
        "## 1. Purpose",
        "",
        (
            "This note closes SHAPIROMART09 by consolidating the existing "
            "SHAPIROMART08 semantic review and SHAPIROMART09 Step 2 exact-token "
            "mapping assessment."
        ),
        "",
        "No new evidence search, raw-data inspection, DB access, analysis, or promotion was performed.",
        "",
        "## 2. Evidence Basis",
        "",
        "- SHAPIROMART08 final status for `raw_field_value.tim_token_003`: `insufficient_semantic_evidence`.",
        "- SHAPIROMART08 promotion allowed: `no`.",
        "- SHAPIROMART09 Step 2 sources inspected/recorded: `20`.",
        "- SHAPIROMART09 Step 2 exact mappings found: `0`.",
        "- SHAPIROMART09 Step 2 strongest mapping class: `no_mapping_found`.",
        "- SHAPIROMART09 Step 2 assessment status: `exact_token_role_unresolved`.",
        "",
        "## 3. Consolidated Finding",
        "",
        (
            "The available local and toolchain evidence supports reconstruction from "
            "normalized data-line position to the internal token `tim_token_003`, "
            "but it does not support a documented mapping from that token to "
            "observation time, phase, TOA, or another geometry-relevant semantic role."
        ),
        "",
        "`raw_record.record_index` remains supported only as `record_order_only`.",
        "",
        "## 4. Closing Decision",
        "",
        f"- exact_token_semantic_support_sufficient: `{decision['exact_token_semantic_support_sufficient']}`",
        f"- promotion_allowed: `{decision['promotion_allowed']}`",
        f"- promotion_applied: `{decision['promotion_applied']}`",
        f"- final_status: `{decision['final_status']}`",
        f"- additional_gate_created: `{decision['additional_gate_created']}`",
        "",
        "`tim_token_003` is not promoted to observation time, pulse phase, TOA value, a geometry axis, an exposure axis, or a Shapiro-related comparison anchor.",
        "",
        "## 5. Consequence for the Geometry Axis",
        "",
        (
            "Therefore, `tim_token_003` remains unresolved and is not promoted. "
            "The geometry and exposure axes remain unavailable through this candidate."
        ),
        "",
        "## 6. Remaining Evidence Gap",
        "",
        f"{decision['main_remaining_gap']}",
        "",
        "## 7. Re-opening Condition",
        "",
        (
            "This path should be re-opened only if new local or external documentary "
            "evidence becomes available that gives an exact position-to-role mapping "
            "for normalized data-line position 3 / `tim_token_003`."
        ),
        "",
        "## 8. Limitations",
        "",
        "- Database access: none.",
        "- Database modified: no.",
        "- Raw TIM/PAR files read: no.",
        "- Internet use: no.",
        "- Physical quantities calculated: no.",
        "- Software or tool versions remained undocumented in the inspected local evidence.",
        "- No additional gate was created.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def build_summary(
    decision: dict[str, str],
    validations: list[dict[str, Any]],
    input_records_before: list[dict[str, Any]],
    source_file_records_before: list[dict[str, Any]],
    source_file_records_read: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "block_identity": {
            "research_block": "QSB-SHAPIROMART09",
            "decision_type": "closing_decision",
            "script": SCRIPT_NAME,
            "generated_at_utc": utc_now(),
        },
        "source_outputs_used": [record["path"] for record in input_records_before],
        "source_files_read": [record["path"] for record in source_file_records_read],
        "source_file_read_records": source_file_records_read,
        "compact_evidence_summary": {
            "position_to_internal_token_reconstructable": "yes",
            "token_to_semantic_role_documented": "no",
            "exact_mappings_found": decision["exact_mappings_found"],
            "strongest_mapping_class": decision["strongest_mapping_class"],
            "conflict_found": decision["conflict_found"],
            "record_index_role": decision["record_index_role"],
        },
        "final_decision": decision,
        "prohibited_promotions": PROHIBITED_PROMOTIONS,
        "retained_record_order_only_role": {
            "candidate": RECORD_INDEX_CANDIDATE,
            "role": decision["record_index_role"],
            "not_interpreted_as": [
                "physical_time",
                "phase",
                "geometry_axis",
                "exposure_axis",
            ],
        },
        "remaining_evidence_gap": decision["main_remaining_gap"],
        "future_reopening_condition": (
            "New local or external documentary evidence must provide an exact "
            "position-to-role mapping for normalized data-line position 3 / "
            "tim_token_003."
        ),
        "validation_results": {
            "checks": validations,
            "all_passed": all(row["passed"] for row in validations),
            "database_access": "none",
            "database_modified": "no",
            "raw_files_read": "no",
            "internet_used": "no",
            "physical_quantities_calculated": "no",
            "promotion_performed": "no",
            "additional_gate_created": decision["additional_gate_created"],
            "input_records_before": input_records_before,
            "source_file_records_before": source_file_records_before,
        },
        "limitations": [
            "This closing note uses only existing SHAPIROMART08 and SHAPIROMART09 Step 2 outputs.",
            "No DB integrity or FK checks were run because no DB was opened.",
            "Software or tool versions were not documented in the inspected local sources.",
            "The path may be re-opened only with new exact position-to-role documentary evidence.",
        ],
    }


def validate_inputs_unchanged(
    before: list[dict[str, Any]],
    after: list[dict[str, Any]],
    label: str,
) -> dict[str, Any]:
    passed = before == after
    if not passed:
        fail(f"{label} changed while writing closing outputs.")
    return {"check": f"{label} unchanged", "passed": True}


def validate_closing_outputs(output_root: Path) -> dict[str, Any]:
    expected = set(CLOSING_OUTPUT_FILENAMES)
    actual = {
        path.name
        for path in output_root.glob("shapiromart09_closing_decision*")
        if path.is_file()
    }
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    if missing or unexpected:
        fail(f"Closing output validation failed: missing={missing}; unexpected={unexpected}")
    return {
        "check": "exactly three closing files generated",
        "passed": True,
        "expected_closing_files": sorted(expected),
        "actual_closing_files": sorted(actual),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs_and_targets(args)

    input_records_before = [file_record(path) for path in INPUT_OUTPUT_PATHS]
    source_file_records_before = [file_record(path) for path in SOURCE_FILE_PATHS]
    source_file_records_read = [script_read_record(path) for path in SOURCE_FILE_PATHS]

    shapiromart08_summary = read_json(SHAPIROMART08_SUMMARY_JSON)
    shapiromart08_selected = single_row(
        read_csv_rows(SHAPIROMART08_SELECTED_STATUS_CSV),
        str(SHAPIROMART08_SELECTED_STATUS_CSV),
    )
    shapiromart09_summary = read_json(SHAPIROMART09_MAPPING_SUMMARY_JSON)
    shapiromart09_status = single_row(
        read_csv_rows(SHAPIROMART09_STEP2_STATUS_CSV),
        str(SHAPIROMART09_STEP2_STATUS_CSV),
    )
    source_identity_rows = read_csv_rows(SHAPIROMART09_SOURCE_IDENTITY_CSV)
    consistency_row = single_row(
        read_csv_rows(SHAPIROMART09_MAPPING_CONSISTENCY_CSV),
        str(SHAPIROMART09_MAPPING_CONSISTENCY_CSV),
    )

    decision, validations = derive_decision(
        shapiromart08_summary,
        shapiromart08_selected,
        shapiromart09_summary,
        shapiromart09_status,
        source_identity_rows,
        consistency_row,
    )

    paths = closing_paths(args.output_root)
    write_markdown(paths[CLOSING_NOTE_MD], decision)
    write_csv(paths[CLOSING_DECISION_CSV], [decision], DECISION_FIELDS)

    input_records_after = [file_record(path) for path in INPUT_OUTPUT_PATHS]
    source_file_records_after = [file_record(path) for path in SOURCE_FILE_PATHS]
    validations.append(
        validate_inputs_unchanged(
            input_records_before,
            input_records_after,
            "source outputs",
        )
    )
    validations.append(
        validate_inputs_unchanged(
            source_file_records_before,
            source_file_records_after,
            "source scripts",
        )
    )
    summary = build_summary(
        decision,
        validations,
        input_records_before,
        source_file_records_before,
        source_file_records_read,
    )
    paths[CLOSING_SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )

    validations.append(validate_closing_outputs(args.output_root))
    summary = build_summary(
        decision,
        validations,
        input_records_before,
        source_file_records_before,
        source_file_records_read,
    )
    paths[CLOSING_SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create the QSB-SHAPIROMART09 closing decision note."
    )
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite-closing-files",
        action="store_true",
        help="Replace only the three SHAPIROMART09 closing-decision files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary["final_decision"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
