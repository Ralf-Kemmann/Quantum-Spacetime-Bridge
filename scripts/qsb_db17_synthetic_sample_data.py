#!/usr/bin/env python3
"""QSB-DB17 synthetic sample data script.

This script is designed for a later QSB-DB18 execution block. It copies the
metadata-seeded QSB SQLite database into a new run artifact and inserts only
controlled synthetic sample rows for database browsing and ETL-path testing.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_PATH = "scripts/qsb_db17_synthetic_sample_data.py"
BLOCK_NAME = "QSB-DB17_SYNTHETIC_SAMPLE_DATA_SCRIPT"
DEFAULT_INPUT_DB = Path("runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db")
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA")
DEFAULT_OUTPUT_DB_NAME = "qsb_research_synthetic_sample.db"

CLAIM_BOUNDARY = (
    "This output does not provide evidence for a physical Shapiro-information residual. "
    "This output does not validate the QSB-ST Bridge. "
    "This output does not establish spacetime, quantum-gravity, relativistic, "
    "pulsar-timing, molecular-structure, or C60 physics claims. "
    "No raw artifact contents were inspected. No TIM/PAR values were read. "
    "No documentation or data files were downloaded. Synthetic sample rows do not "
    "authorize physical interpretation. Synthetic sample rows are infrastructure test data only."
)

SYNTHETIC_TABLES = [
    "raw_data_source",
    "raw_data",
    "field_catalog",
    "raw_token_catalog",
    "etl_transformation_rule",
    "quality_check_catalog",
    "quality_check_result",
    "harmonized_value_view_catalog",
    "claim_boundary_catalog",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a synthetic-only QSB research SQLite database by copying the "
            "metadata-seeded DB and inserting controlled infrastructure test rows."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help=f"Metadata-seeded input DB. Default: {DEFAULT_INPUT_DB}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Output root. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--output-db",
        type=Path,
        default=None,
        help=f"Output DB path. Default: <output-root>/{DEFAULT_OUTPUT_DB_NAME}",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the output DB path if it already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned synthetic sample tables and output paths without creating files.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def resolve_output_db(output_root: Path, output_db: Path | None) -> Path:
    return output_db if output_db is not None else output_root / DEFAULT_OUTPUT_DB_NAME


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def insert_row(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> int:
    columns = list(values)
    placeholders = ", ".join(["?"] * len(columns))
    quoted = ", ".join(columns)
    sql = f"INSERT INTO {table} ({quoted}) VALUES ({placeholders})"
    cur = conn.execute(sql, [values[column] for column in columns])
    return int(cur.lastrowid)


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])


def all_table_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    tables = [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
    ]
    return [{"table_name": table, "row_count": table_count(conn, table)} for table in tables]


def foreign_key_violations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {
            "table_name": row[0],
            "rowid": row[1],
            "referenced_table": row[2],
            "fk_id": row[3],
        }
        for row in rows
    ]


def get_table_id(conn: sqlite3.Connection, table_name: str) -> int | None:
    row = conn.execute(
        "SELECT table_id FROM table_catalog WHERE table_name = ?",
        (table_name,),
    ).fetchone()
    return int(row[0]) if row else None


def run_dry_run(input_db: Path, output_root: Path, output_db: Path) -> int:
    if not input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {input_db}")
    print(f"block: {BLOCK_NAME}")
    print("dry_run: true")
    print(f"input_db: {input_db}")
    print(f"output_root: {output_root}")
    print(f"output_db: {output_db}")
    print("planned_synthetic_sample_tables:")
    for table in SYNTHETIC_TABLES:
        print(f"- {table}")
    print("sample_execution_mode: synthetic_only")
    print("raw_artifact_access_status: not_performed")
    print("tim_par_value_reading_status: not_performed")
    print("documentation_download_status: not_performed")
    print("bridge_claim_gate: closed")
    return 0


def bump(counts: dict[str, int], table: str, amount: int = 1) -> None:
    counts[table] = counts.get(table, 0) + amount


def seed_synthetic_sample(conn: sqlite3.Connection) -> dict[str, int]:
    counts: dict[str, int] = {}
    raw_data_table_id = get_table_id(conn, "raw_data")

    source_id = insert_row(
        conn,
        "raw_data_source",
        {
            "source_name": "synthetic_qsb_db_test_source",
            "source_type": "synthetic_test_source",
            "provider_or_project": "QSB-DB",
            "source_url_or_path": "synthetic://qsb-db/sample-data/v1",
            "source_release": "synthetic_sample_v1",
            "source_version": "1.0",
            "source_access_date": "2026-06-02",
            "source_download_status": "not_applicable",
            "source_reachability_status": "synthetic_internal",
            "source_corruption_status": "not_applicable",
            "checksum_status": "not_applicable",
            "license_or_usage_note": "synthetic internal test data only",
            "provenance_confidence": "synthetic_controlled",
            "quarantine_status": "not_quarantined",
            "notes": "synthetic_only database infrastructure test source; no raw external data",
        },
    )
    bump(counts, "raw_data_source")

    raw_cases = [
        (
            "clean_numeric_sample",
            "synthetic_record_001",
            "synthetic_measurement_001",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "checked_synthetic",
                "blank_check_status": "passed",
                "special_character_check_status": "passed",
                "datatype_check_status": "passed",
                "unit_detection_status": "synthetic_unit_detected",
                "scale_detection_status": "passed",
                "harmonization_status": "rule_defined",
                "etl_release_status": "harmonization_ready",
                "quarantine_status": "not_quarantined",
                "retry_possible": 1,
            },
        ),
        (
            "blank_value_sample",
            "synthetic_record_002",
            "synthetic_measurement_002",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "checked_synthetic",
                "blank_check_status": "flagged",
                "special_character_check_status": "passed",
                "datatype_check_status": "unresolved_blank",
                "unit_detection_status": "not_applicable",
                "scale_detection_status": "not_applicable",
                "harmonization_status": "needs_missing_value_rule",
                "etl_release_status": "raw_only",
                "quarantine_status": "not_quarantined",
                "retry_possible": 1,
            },
        ),
        (
            "special_character_sample",
            "synthetic_record_003",
            "synthetic_measurement_003",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "checked_synthetic",
                "blank_check_status": "passed",
                "special_character_check_status": "flagged",
                "datatype_check_status": "passed_text",
                "unit_detection_status": "not_applicable",
                "scale_detection_status": "not_applicable",
                "harmonization_status": "rule_defined",
                "etl_release_status": "harmonization_ready",
                "quarantine_status": "not_quarantined",
                "retry_possible": 1,
            },
        ),
        (
            "string_numeric_cast_sample",
            "synthetic_record_004",
            "synthetic_measurement_004",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "checked_synthetic",
                "blank_check_status": "passed",
                "special_character_check_status": "passed",
                "datatype_check_status": "cast_required",
                "unit_detection_status": "synthetic_unit_detected",
                "scale_detection_status": "passed",
                "harmonization_status": "rule_defined",
                "etl_release_status": "harmonization_ready",
                "quarantine_status": "not_quarantined",
                "retry_possible": 1,
            },
        ),
        (
            "scale_normalization_sample",
            "synthetic_record_005",
            "synthetic_measurement_005",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "checked_synthetic",
                "blank_check_status": "passed",
                "special_character_check_status": "passed",
                "datatype_check_status": "passed",
                "unit_detection_status": "synthetic_unit_detected",
                "scale_detection_status": "scale_rule_required",
                "harmonization_status": "rule_defined",
                "etl_release_status": "harmonization_ready",
                "quarantine_status": "not_quarantined",
                "retry_possible": 1,
            },
        ),
        (
            "missing_value_sample",
            "synthetic_record_006",
            "synthetic_measurement_006",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "checked_synthetic",
                "blank_check_status": "flagged",
                "special_character_check_status": "passed",
                "datatype_check_status": "missing_marker_detected",
                "unit_detection_status": "not_applicable",
                "scale_detection_status": "not_applicable",
                "harmonization_status": "needs_missing_value_rule",
                "etl_release_status": "raw_only",
                "quarantine_status": "not_quarantined",
                "retry_possible": 1,
            },
        ),
        (
            "quarantine_candidate_sample",
            "synthetic_record_007",
            "synthetic_measurement_007",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "flagged_synthetic",
                "blank_check_status": "passed",
                "special_character_check_status": "flagged",
                "datatype_check_status": "unresolved",
                "unit_detection_status": "unresolved",
                "scale_detection_status": "unresolved",
                "harmonization_status": "blocked_by_quality",
                "etl_release_status": "quarantined",
                "quarantine_status": "quarantined_synthetic",
                "quarantine_reason": "synthetic_quality_stop_condition",
                "retry_possible": 1,
            },
        ),
        (
            "harmonization_ready_sample",
            "synthetic_record_008",
            "synthetic_measurement_008",
            {
                "raw_ingest_status": "synthetic_loaded",
                "raw_parse_status": "parsed_synthetic",
                "raw_quality_status": "checked_synthetic",
                "blank_check_status": "passed",
                "special_character_check_status": "passed",
                "datatype_check_status": "passed",
                "unit_detection_status": "synthetic_unit_detected",
                "scale_detection_status": "passed",
                "harmonization_status": "synthetic_harmonized",
                "etl_release_status": "synthetic_harmonized",
                "quarantine_status": "not_quarantined",
                "retry_possible": 1,
            },
        ),
    ]

    raw_data_ids: dict[str, int] = {}
    for idx, (case_name, record_id, measurement_id, statuses) in enumerate(raw_cases, start=1):
        values = {
            "raw_data_source_id": source_id,
            "raw_artifact_id": "synthetic_artifact_v1",
            "source_local_file_id": "synthetic_file_v1",
            "source_local_record_id": record_id,
            "source_local_measurement_id": measurement_id,
            "raw_record_position": str(idx),
            "raw_object_type": "synthetic_record",
            "raw_file_type": "synthetic_inline_test",
            "notes": f"{case_name}; synthetic_only; not_physical_data",
        }
        values.update(statuses)
        raw_data_ids[case_name] = insert_row(conn, "raw_data", values)
        bump(counts, "raw_data")

    field_specs = [
        ("sample_id", 1, "text", "text", "text", "not_applicable", "not_applicable", "required"),
        (
            "sample_numeric_value",
            2,
            "mixed_text_numeric",
            "real_or_castable_text",
            "real",
            "synthetic_unit",
            "scale_checked",
            "nullable_synthetic",
        ),
        ("sample_text_value", 3, "text", "text", "text", "not_applicable", "not_applicable", "nullable_synthetic"),
        (
            "sample_unit",
            4,
            "text",
            "unit_marker",
            "synthetic_unit_marker",
            "synthetic_unit_detected",
            "not_applicable",
            "nullable_synthetic",
        ),
        (
            "sample_status",
            5,
            "text",
            "status_marker",
            "status_marker",
            "not_applicable",
            "not_applicable",
            "required",
        ),
        (
            "sample_missing_marker",
            6,
            "text",
            "missing_marker",
            "missing_marker",
            "not_applicable",
            "not_applicable",
            "test_case",
        ),
        (
            "sample_scale_marker",
            7,
            "text",
            "scale_marker",
            "scale_marker",
            "not_applicable",
            "scale_rule_required",
            "nullable_synthetic",
        ),
    ]
    field_ids: dict[str, int] = {}
    for name, position, raw_type, inferred_type, harmonized_type, unit_status, scale_status, missingness in field_specs:
        field_ids[name] = insert_row(
            conn,
            "field_catalog",
            {
                "table_id": raw_data_table_id,
                "field_name": name,
                "field_position": position,
                "raw_type": raw_type,
                "inferred_type": inferred_type,
                "harmonized_type": harmonized_type,
                "semantic_status": "synthetic_controlled",
                "correction_state_relevance": "not_applicable_synthetic",
                "unit_status": unit_status,
                "scale_status": scale_status,
                "missingness_status": missingness,
                "notes": "synthetic_only field catalog infrastructure test",
            },
        )
        bump(counts, "field_catalog")

    token_specs = [
        ("clean_numeric_sample", "sample_numeric_value", "42.0", "synthetic_numeric", "synthetic_parsed", "not_quarantined"),
        ("blank_value_sample", "sample_missing_marker", "", "synthetic_blank", "synthetic_flagged", "not_quarantined"),
        ("missing_value_sample", "sample_missing_marker", "NULL", "synthetic_missing", "synthetic_flagged", "not_quarantined"),
        (
            "string_numeric_cast_sample",
            "sample_numeric_value",
            "1.23E+03",
            "synthetic_cast_candidate",
            "synthetic_parsed",
            "not_quarantined",
        ),
        (
            "special_character_sample",
            "sample_text_value",
            "value_with_äöü",
            "synthetic_text",
            "synthetic_flagged",
            "not_quarantined",
        ),
        (
            "string_numeric_cast_sample",
            "sample_text_value",
            "needs_cast_17",
            "synthetic_cast_candidate",
            "synthetic_unresolved",
            "not_quarantined",
        ),
        (
            "missing_value_sample",
            "sample_missing_marker",
            "synthetic_missing",
            "synthetic_missing",
            "synthetic_flagged",
            "not_quarantined",
        ),
        (
            "scale_normalization_sample",
            "sample_scale_marker",
            "scale_x1000",
            "synthetic_scale_marker",
            "synthetic_flagged",
            "not_quarantined",
        ),
        (
            "quarantine_candidate_sample",
            "sample_status",
            "quarantine_candidate",
            "synthetic_status",
            "synthetic_unresolved",
            "quarantined_synthetic",
        ),
        (
            "harmonization_ready_sample",
            "sample_status",
            "harmonization_ready",
            "synthetic_status",
            "synthetic_parsed",
            "not_quarantined",
        ),
    ]
    for idx, (case_name, field_name, token, type_guess, parse_status, quarantine_status) in enumerate(token_specs, start=1):
        insert_row(
            conn,
            "raw_token_catalog",
            {
                "raw_data_id": raw_data_ids[case_name],
                "field_id": field_ids[field_name],
                "source_local_record_id": f"synthetic_record_{idx:03d}",
                "raw_token": token,
                "token_position": str(idx),
                "token_type_guess": type_guess,
                "parse_status": parse_status,
                "quarantine_status": quarantine_status,
                "notes": "synthetic_only; no_TIM_PAR_content; no raw artifact value",
            },
        )
        bump(counts, "raw_token_catalog")

    etl_specs = [
        (
            "cast_text_to_real_synthetic",
            "cast",
            field_ids["sample_numeric_value"],
            "sample_numeric_value_real",
            "CAST synthetic text numeric token to REAL",
            {"cast_rule": "text_to_real_synthetic"},
            0,
        ),
        (
            "blank_to_missing_marker_synthetic",
            "missing_value_handling",
            field_ids["sample_missing_marker"],
            "sample_missing_marker",
            "map blank synthetic token to synthetic_missing",
            {"missing_value_rule": "blank_to_synthetic_missing"},
            0,
        ),
        (
            "special_character_preservation_rule_synthetic",
            "special_character_cleanup",
            field_ids["sample_text_value"],
            "sample_text_value",
            "preserve unicode marker while flagging special characters",
            {"special_character_rule": "preserve_and_flag"},
            1,
        ),
        (
            "scale_factor_1000_synthetic",
            "scale_normalization",
            field_ids["sample_scale_marker"],
            "sample_numeric_value_scaled",
            "synthetic_value / 1000",
            {"scale_rule": "divide_by_1000_synthetic"},
            1,
        ),
        (
            "synthetic_unit_to_si_placeholder",
            "unit_harmonization",
            field_ids["sample_unit"],
            "sample_unit_si_placeholder",
            "map synthetic_unit to synthetic_si_placeholder",
            {"unit_before": "synthetic_unit", "unit_after": "synthetic_si_placeholder"},
            0,
        ),
        (
            "quarantine_flag_rule_synthetic",
            "quality_gate",
            field_ids["sample_status"],
            "sample_status",
            "if unresolved datatype and unresolved unit then quarantine_synthetic",
            {"mapping_rule": "synthetic_quality_stop_condition"},
            0,
        ),
    ]
    for rule_name, rule_type, source_field_id, target_field, expression, extra, reversible in etl_specs:
        values = {
            "rule_name": rule_name,
            "rule_type": rule_type,
            "source_field_id": source_field_id,
            "target_field_name": target_field,
            "transformation_expression": expression,
            "provenance_status": "synthetic_controlled",
            "reversible_flag": reversible,
            "allowed_for_analytics": 0,
            "notes": "synthetic_only ETL rule metadata; not a scientific transformation",
        }
        values.update(extra)
        insert_row(conn, "etl_transformation_rule", values)
        bump(counts, "etl_transformation_rule")

    check_specs = [
        ("check_blank_marker_synthetic", "blank_marker", "raw_data", "blank_check_status", "blank marker synthetic check", 0),
        (
            "check_numeric_cast_possible_synthetic",
            "numeric_cast",
            "raw_token_catalog",
            "raw_token",
            "synthetic numeric cast possible check",
            0,
        ),
        (
            "check_special_character_presence_synthetic",
            "special_character",
            "raw_token_catalog",
            "raw_token",
            "synthetic special character presence check",
            0,
        ),
        ("check_scale_marker_synthetic", "scale_marker", "raw_data", "scale_detection_status", "synthetic scale marker check", 0),
        (
            "check_quarantine_reason_required_synthetic",
            "quarantine_reason",
            "raw_data",
            "quarantine_reason",
            "synthetic quarantine reason required check",
            1,
        ),
    ]
    quality_check_ids: dict[str, int] = {}
    for check_name, check_type, target_table, target_field, expression, stop_if_failed in check_specs:
        quality_check_ids[check_name] = insert_row(
            conn,
            "quality_check_catalog",
            {
                "check_name": check_name,
                "check_type": check_type,
                "target_table": target_table,
                "target_field": target_field,
                "check_expression": expression,
                "severity": "synthetic_test",
                "stop_if_failed": stop_if_failed,
                "notes": "synthetic_only quality check definition",
            },
        )
        bump(counts, "quality_check_catalog")

    result_specs = [
        ("check_numeric_cast_possible_synthetic", "clean_numeric_sample", "passed", "passed numeric cast check"),
        ("check_blank_marker_synthetic", "blank_value_sample", "flagged", "flagged blank marker"),
        (
            "check_special_character_presence_synthetic",
            "special_character_sample",
            "flagged",
            "flagged special character presence",
        ),
        ("check_numeric_cast_possible_synthetic", "string_numeric_cast_sample", "passed", "passed cast possible"),
        ("check_scale_marker_synthetic", "scale_normalization_sample", "flagged", "flagged scale marker"),
        (
            "check_quarantine_reason_required_synthetic",
            "quarantine_candidate_sample",
            "passed",
            "passed quarantine reason required",
        ),
        ("check_numeric_cast_possible_synthetic", "harmonization_ready_sample", "passed", "passed synthetic readiness check"),
    ]
    for check_name, case_name, status, detail in result_specs:
        insert_row(
            conn,
            "quality_check_result",
            {
                "quality_check_id": quality_check_ids[check_name],
                "raw_data_id": raw_data_ids[case_name],
                "table_id": raw_data_table_id,
                "result_status": status,
                "result_detail": detail,
                "notes": "synthetic_only quality check result; not a scientific result",
            },
        )
        bump(counts, "quality_check_result")

    insert_row(
        conn,
        "harmonized_value_view_catalog",
        {
            "view_name": "synthetic_harmonized_sample_view",
            "view_type": "synthetic_test_view",
            "source_table_ids": "raw_data,field_catalog,raw_token_catalog,etl_transformation_rule,quality_check_result",
            "transformation_rule_set": "synthetic_sample_rule_set_v1",
            "blind_descriptive_status": "synthetic_only",
            "interpretation_status": "not_opened",
            "notes": "synthetic view metadata only; no SQL view created by this step",
        },
    )
    bump(counts, "harmonized_value_view_catalog")

    for object_type in [
        "synthetic_sample_source",
        "synthetic_raw_data_rows",
        "synthetic_raw_tokens",
        "synthetic_etl_rules",
        "synthetic_quality_checks",
        "synthetic_harmonized_view_metadata",
    ]:
        insert_row(
            conn,
            "claim_boundary_catalog",
            {
                "object_type": object_type,
                "object_id": f"{object_type}_v1",
                "claim_level": "synthetic_infrastructure_only",
                "physical_interpretation_allowed": 0,
                "residual_analysis_allowed": 0,
                "model_fitting_allowed": 0,
                "bridge_claim_allowed": 0,
                "value_reading_allowed": 0,
                "notes": "synthetic_only claim boundary; physical interpretation forbidden",
            },
        )
        bump(counts, "claim_boundary_catalog")

    return counts


def scalar(conn: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> int:
    return int(conn.execute(sql, params).fetchone()[0])


def run_forbidden_content_checks(conn: sqlite3.Connection) -> tuple[list[dict[str, str]], str, str]:
    rows: list[dict[str, str]] = []

    def add(check_name: str, ok: bool, detail: str) -> None:
        rows.append({"check_name": check_name, "status": "passed" if ok else "failed", "detail": detail})

    token_forbidden = scalar(
        conn,
        """
        SELECT COUNT(*) FROM raw_token_catalog
        WHERE notes LIKE '%synthetic_only%'
          AND (
            lower(raw_token) LIKE '%.tim%'
            OR lower(raw_token) LIKE '%.par%'
            OR lower(raw_token) LIKE '%c60%'
            OR lower(raw_token) LIKE '%residual%'
            OR lower(raw_token) LIKE '%model%'
          )
        """,
    )
    add("no_real_tim_par_c60_residual_model_tokens", token_forbidden == 0, f"forbidden_token_count={token_forbidden}")

    analytics_rules = scalar(
        conn,
        "SELECT COUNT(*) FROM etl_transformation_rule WHERE rule_name LIKE '%_synthetic' AND allowed_for_analytics != 0",
    )
    add("no_analytics_enabled_synthetic_rules", analytics_rules == 0, f"analytics_enabled_rules={analytics_rules}")

    open_claims = scalar(
        conn,
        """
        SELECT COUNT(*) FROM claim_boundary_catalog
        WHERE object_type LIKE 'synthetic_%'
          AND (
            physical_interpretation_allowed != 0
            OR residual_analysis_allowed != 0
            OR model_fitting_allowed != 0
            OR bridge_claim_allowed != 0
            OR value_reading_allowed != 0
          )
        """,
    )
    add("no_open_synthetic_claim_boundaries", open_claims == 0, f"open_claim_boundary_rows={open_claims}")

    synthetic_source_count = scalar(
        conn,
        "SELECT COUNT(*) FROM raw_data_source WHERE source_name = 'synthetic_qsb_db_test_source' AND notes LIKE '%synthetic%'",
    )
    add("synthetic_source_labeled", synthetic_source_count == 1, f"synthetic_source_count={synthetic_source_count}")

    unlabeled_raw_data = scalar(
        conn,
        """
        SELECT COUNT(*) FROM raw_data
        WHERE raw_artifact_id = 'synthetic_artifact_v1'
          AND (notes NOT LIKE '%synthetic_only%' OR notes NOT LIKE '%not_physical_data%')
        """,
    )
    add("synthetic_raw_data_labeled", unlabeled_raw_data == 0, f"unlabeled_raw_data_rows={unlabeled_raw_data}")

    unlabeled_tokens = scalar(
        conn,
        "SELECT COUNT(*) FROM raw_token_catalog WHERE notes LIKE '%synthetic_only%' AND notes NOT LIKE '%no_TIM_PAR_content%'",
    )
    add("synthetic_tokens_labeled", unlabeled_tokens == 0, f"unlabeled_token_rows={unlabeled_tokens}")

    status = "passed" if all(row["status"] == "passed" for row in rows) else "failed"
    synthetic_label_status = "passed" if rows[-3]["status"] == rows[-2]["status"] == rows[-1]["status"] == "passed" else "failed"
    return rows, status, synthetic_label_status


def write_readout(path: Path, summary: dict[str, Any], insert_counts: dict[str, int]) -> None:
    lines = [
        "# QSB-DB18 Synthetic Sample Data Readout",
        "",
        "## Purpose",
        "",
        "Create a synthetic-only SQLite research database artifact for browsing infrastructure behavior.",
        "",
        "## Inputs and Outputs",
        "",
        f"- input_db: {summary['input_db_path']}",
        f"- output_db: {summary['output_db_path']}",
        f"- sample_execution_mode: {summary['sample_execution_mode']}",
        "",
        "## Inserted Row Counts",
        "",
    ]
    for table, count in sorted(insert_counts.items()):
        lines.append(f"- {table}: {count}")
    lines.extend(
        [
            "",
            "## Validation",
            "",
            f"- fk_validation_status: {summary['fk_validation_status']}",
            f"- forbidden_content_check_status: {summary['forbidden_content_check_status']}",
            f"- synthetic_label_check_status: {summary['synthetic_label_check_status']}",
            f"- metadata_db_modified: {summary['metadata_db_modified']}",
            "",
            "## Boundary",
            "",
            f"- raw_artifact_access_status: {summary['raw_artifact_access_status']}",
            f"- tim_par_value_reading_status: {summary['tim_par_value_reading_status']}",
            f"- documentation_download_status: {summary['documentation_download_status']}",
            f"- physical_interpretation_status: {summary['physical_interpretation_status']}",
            f"- residual_analysis_gate: {summary['residual_analysis_gate']}",
            f"- model_fitting_gate: {summary['model_fitting_gate']}",
            f"- bridge_claim_gate: {summary['bridge_claim_gate']}",
            "",
            CLAIM_BOUNDARY,
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(
    output_root: Path,
    summary: dict[str, Any],
    config: dict[str, Any],
    insert_counts: dict[str, int],
    table_counts: list[dict[str, Any]],
    fk_rows: list[dict[str, Any]],
    forbidden_rows: list[dict[str, str]],
) -> None:
    write_json(output_root / "synthetic_sample_summary.json", summary)
    write_json(output_root / "synthetic_sample_config_resolved.json", config)
    write_csv(
        output_root / "synthetic_sample_insert_counts.csv",
        ["table_name", "inserted_rows"],
        [{"table_name": key, "inserted_rows": value} for key, value in sorted(insert_counts.items())],
    )
    write_csv(
        output_root / "synthetic_sample_table_row_counts.csv",
        ["table_name", "row_count"],
        table_counts,
    )
    write_csv(
        output_root / "synthetic_sample_fk_validation.csv",
        ["table_name", "rowid", "referenced_table", "fk_id"],
        fk_rows,
    )
    write_csv(
        output_root / "synthetic_sample_forbidden_content_check.csv",
        ["check_name", "status", "detail"],
        forbidden_rows,
    )
    write_readout(output_root / "synthetic_sample_readout.md", summary, insert_counts)


def main() -> int:
    args = parse_args()
    input_db = args.input_db
    output_root = args.output_root
    output_db = resolve_output_db(output_root, args.output_db)

    if args.dry_run:
        return run_dry_run(input_db, output_root, output_db)

    if not input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {input_db}")
    if output_db.exists():
        if not args.overwrite:
            raise FileExistsError(
                f"Output DB already exists; rerun with --overwrite to replace it: {output_db}"
            )
        output_db.unlink()

    input_stat_before = input_db.stat()
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_db, output_db)

    conn = sqlite3.connect(output_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        try:
            conn.execute("BEGIN")
            insert_counts = seed_synthetic_sample(conn)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        fk_violations = foreign_key_violations(conn)
        forbidden_rows, forbidden_status, synthetic_label_status = run_forbidden_content_checks(conn)
        table_counts = all_table_counts(conn)
        input_stat_after = input_db.stat()
        metadata_db_modified = (
            input_stat_before.st_size != input_stat_after.st_size
            or input_stat_before.st_mtime_ns != input_stat_after.st_mtime_ns
        )
        inserted_total = sum(insert_counts.values())
        fk_status = "passed" if not fk_violations else "failed"
        sample_status = (
            "completed"
            if fk_status == "passed"
            and forbidden_status == "passed"
            and synthetic_label_status == "passed"
            and not metadata_db_modified
            else "failed"
        )

        summary = {
            "generated_at_utc": utc_now(),
            "input_db_path": str(input_db),
            "output_db_path": str(output_db),
            "output_root": str(output_root),
            "synthetic_sample_status": sample_status,
            "metadata_db_modified": metadata_db_modified,
            "output_db_created": output_db.exists(),
            "sample_execution_mode": "synthetic_only",
            "inserted_table_count": len(insert_counts),
            "inserted_row_count_total": inserted_total,
            "insert_counts": insert_counts,
            "fk_validation_status": fk_status,
            "foreign_key_check_violations": fk_violations,
            "forbidden_content_check_status": forbidden_status,
            "synthetic_label_check_status": synthetic_label_status,
            "forbidden_tables_checked": [
                "raw_data_source",
                "raw_data",
                "raw_token_catalog",
                "etl_transformation_rule",
                "claim_boundary_catalog",
            ],
            "raw_data_row_count": table_count(conn, "raw_data"),
            "raw_token_row_count": table_count(conn, "raw_token_catalog"),
            "field_catalog_row_count": table_count(conn, "field_catalog"),
            "synthetic_source_count": scalar(
                conn,
                "SELECT COUNT(*) FROM raw_data_source WHERE source_name = 'synthetic_qsb_db_test_source'",
            ),
            "synthetic_raw_data_count": scalar(
                conn,
                "SELECT COUNT(*) FROM raw_data WHERE raw_artifact_id = 'synthetic_artifact_v1'",
            ),
            "synthetic_raw_token_count": scalar(
                conn,
                "SELECT COUNT(*) FROM raw_token_catalog WHERE notes LIKE '%synthetic_only%'",
            ),
            "synthetic_etl_rule_count": scalar(
                conn,
                "SELECT COUNT(*) FROM etl_transformation_rule WHERE rule_name LIKE '%_synthetic'",
            ),
            "synthetic_quality_check_count": scalar(
                conn,
                "SELECT COUNT(*) FROM quality_check_catalog WHERE check_name LIKE '%_synthetic'",
            ),
            "synthetic_quality_result_count": scalar(
                conn,
                "SELECT COUNT(*) FROM quality_check_result WHERE notes LIKE '%synthetic_only%'",
            ),
            "real_data_ingestion": False,
            "c60_value_ingestion": False,
            "analytics_data_ingestion": False,
            "raw_artifact_access_status": "not_performed",
            "tim_par_value_reading_status": "not_performed",
            "documentation_download_status": "not_performed",
            "physical_interpretation_status": "forbidden",
            "residual_analysis_gate": "closed",
            "model_fitting_gate": "closed",
            "bridge_claim_gate": "closed",
            "claim_boundary": CLAIM_BOUNDARY,
        }
        config = {
            "script": SCRIPT_PATH,
            "block": BLOCK_NAME,
            "input_db": str(input_db),
            "output_root": str(output_root),
            "output_db": str(output_db),
            "overwrite": bool(args.overwrite),
            "dry_run": bool(args.dry_run),
            "sample_scope": "synthetic_only",
            "raw_artifact_access": "forbidden",
            "tim_par_value_reading": "forbidden",
            "real_data_ingestion": "forbidden",
            "c60_value_ingestion": "forbidden",
            "analytics_data_ingestion": "forbidden",
            "bridge_claim_gate": "closed",
        }

        write_outputs(output_root, summary, config, insert_counts, table_counts, fk_violations, forbidden_rows)

        print("synthetic_sample: complete")
        print(f"output_db: {output_db}")
        print(f"synthetic_sample_status: {sample_status}")
        print(f"inserted_row_count_total: {inserted_total}")
        print(f"fk_validation_status: {fk_status}")
        print(f"forbidden_content_check_status: {forbidden_status}")
        print(f"synthetic_label_check_status: {synthetic_label_status}")
        return 0 if sample_status == "completed" else 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
