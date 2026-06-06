#!/usr/bin/env python3
"""QSB-SHAPIROMART09 Step 2 exact-token mapping assessment.

This script checks whether local SHAPIROMART07/08 evidence, local TIM
structure documentation, and the DB/parser toolchain establish the complete
chain from a concrete TIM data-line position to the internal token
``tim_token_003`` and then to a documented semantic role.

The live DB and workcopy DB are opened read-only. The script creates no DB
tables or views, changes no DB files, does not inspect raw TIM/PAR value
content, and does not compute timing, phase, model, delay, geometry, exposure,
or physical quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart09_exact_token_mapping_assessment.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/"
    "SHAPIROMART09_DATASET_SPECIFIC_TIM_FORMAT_EVIDENCE_ACQUISITION"
)

SHAPIROMART07_CANDIDATE_CSV = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART07_TIMESTAMP_PHASE_SEMANTIC_RESOLUTION/"
    "shapiromart07_candidate_review.csv"
)
SHAPIROMART08_SUMMARY_JSON = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART08_PAR_TIM_SEMANTIC_EVIDENCE_REVIEW/"
    "shapiromart08_summary.json"
)
SHAPIROMART08_CANDIDATE_EVIDENCE_CSV = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART08_PAR_TIM_SEMANTIC_EVIDENCE_REVIEW/"
    "shapiromart08_candidate_evidence.csv"
)
SHAPIROINFO53_TIM_SUMMARY_JSON = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO53_TIM_PAR_CONTENT_STRUCTURE_REVIEW/"
    "tim_content_structure_summary.json"
)
SHAPIROINFO53_TIM_COLUMN_COUNTS_CSV = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO53_TIM_PAR_CONTENT_STRUCTURE_REVIEW/"
    "tim_column_count_distribution.csv"
)
SHAPIROINFO53_TIM_ROW_FORMAT_CSV = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO53_TIM_PAR_CONTENT_STRUCTURE_REVIEW/"
    "tim_row_format_inventory.csv"
)
LOCAL_QUARANTINE_MANIFEST = Path(
    "data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/"
    "j0740_6620_quarantine_download_manifest_2026_05_29.yaml"
)
LOCAL_MANUAL_EVIDENCE_CSV = Path(
    "data/QSB-ST-SHAPIROINFO/manual_evidence/dwh14a_high_priority_manual_evidence.csv"
)
SHAPIROINFO55_RESULT_NOTE = Path(
    "docs/QSB_ST_SHAPIROINFO55_TIM_PAR_CONTENT_STRUCTURE_REVIEW_RESULT_NOTE.md"
)
SHAPIROINFO57_SPEC = Path(
    "docs/QSB_ST_SHAPIROINFO57_TIM_PAR_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_SPEC.md"
)

READOUT_MD = "shapiromart09_mapping_assessment_readout.md"
SUMMARY_JSON = "shapiromart09_mapping_assessment_summary.json"
SOURCE_IDENTITY_CSV = "shapiromart09_source_identity.csv"
FORMAT_IDENTITY_CSV = "shapiromart09_format_identity.csv"
TOKEN_POSITION_MAPPING_CSV = "shapiromart09_token_position_mapping.csv"
PARSER_WRITER_ALIGNMENT_CSV = "shapiromart09_parser_writer_alignment.csv"
MAPPING_CONSISTENCY_CSV = "shapiromart09_mapping_consistency.csv"
MAPPING_SCOPE_CSV = "shapiromart09_mapping_scope.csv"
STEP2_STATUS_CSV = "shapiromart09_step2_status.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    SOURCE_IDENTITY_CSV,
    FORMAT_IDENTITY_CSV,
    TOKEN_POSITION_MAPPING_CSV,
    PARSER_WRITER_ALIGNMENT_CSV,
    MAPPING_CONSISTENCY_CSV,
    MAPPING_SCOPE_CSV,
    STEP2_STATUS_CSV,
]

SOURCE_IDENTITY_FIELDS = [
    "source_id",
    "source_path",
    "source_type",
    "source_scope",
    "dataset_specific",
    "tool_specific",
    "software_name",
    "software_version",
    "relevance_status",
    "notes",
]
FORMAT_IDENTITY_FIELDS = [
    "source_id",
    "described_line_type",
    "tokenization_rule",
    "indexing_basis",
    "optional_fields_present",
    "format_variant",
    "applies_to_dataset",
    "evidence_class",
    "notes",
]
TOKEN_POSITION_MAPPING_FIELDS = [
    "candidate_name",
    "internal_token",
    "raw_position",
    "normalized_position",
    "source_id",
    "documented_field_name",
    "documented_semantic_role",
    "mapping_chain",
    "mapping_class",
    "mapping_strength",
    "notes",
]
PARSER_WRITER_ALIGNMENT_FIELDS = [
    "source_id",
    "parser_or_writer",
    "code_reference",
    "parsing_branch",
    "field_order_documented",
    "version_match",
    "dataset_format_match",
    "alignment_status",
    "notes",
]
MAPPING_CONSISTENCY_FIELDS = [
    "candidate_name",
    "source_count",
    "agreeing_source_count",
    "conflicting_source_count",
    "version_mismatch_count",
    "format_mismatch_count",
    "consistency_status",
    "notes",
]
MAPPING_SCOPE_FIELDS = [
    "candidate_name",
    "applies_to_all_records",
    "applies_to_line_type",
    "applies_to_files",
    "software_version_scope",
    "configuration_scope",
    "scope_status",
    "notes",
]
STEP2_STATUS_FIELDS = [
    "candidate_name",
    "first_reviewed",
    "exact_mapping_found",
    "documented_semantic_role",
    "strongest_mapping_class",
    "assessment_status",
    "promotion_evaluated",
    "promotion_applied",
    "main_remaining_gap",
    "recommended_final_review",
]

EXPECTED_CANDIDATES = [
    "raw_field_value.tim_token_003",
    "raw_record.record_index",
    "core_observation_record_link.raw_record_id",
    "raw_field_value.tim_token_001",
]

TARGET_CANDIDATE = "raw_field_value.tim_token_003"
TARGET_TOKEN = "tim_token_003"
MAIN_REMAINING_GAP = (
    "No inspected local or toolchain source maps the normalized data-line "
    "token position 3 / internal token tim_token_003 to a documented semantic "
    "role such as observation_time, pulse_phase, toa_value, frequency, "
    "uncertainty, site_or_observatory, flag_or_metadata, or other documented "
    "role."
)
METHOD_BOUNDARY = (
    "This step assesses documentary and parser/toolchain evidence only. It "
    "does not infer semantics from numeric behavior, compute physical "
    "quantities, or apply promotion."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def fail(message: str) -> None:
    raise RuntimeError(message)


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def fetch_dicts(
    con: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql, params).fetchall()]


def object_exists(
    con: sqlite3.Connection,
    name: str,
    object_type: str | None = None,
) -> bool:
    if object_type is None:
        row = con.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE name = ?
              AND type IN ('table', 'view')
            """,
            (name,),
        ).fetchone()
    else:
        row = con.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE name = ?
              AND type = ?
            """,
            (name, object_type),
        ).fetchone()
    return row is not None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_stat(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {"size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def db_state(path: Path) -> dict[str, Any]:
    return {"sha256": file_sha256(path), "stat": file_stat(path)}


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


def db_checks(con: sqlite3.Connection) -> dict[str, Any]:
    fk_rows = foreign_key_violations(con)
    return {
        "integrity_check": integrity_check(con),
        "foreign_key_violation_count": len(fk_rows),
        "foreign_key_violations": fk_rows,
    }


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_candidate(row: dict[str, Any]) -> str:
    return f"{row['source_table']}.{row['source_field_or_token']}"


def load_candidates(con: sqlite3.Connection) -> list[dict[str, Any]]:
    if not object_exists(con, "qsb_v_shapiromart07_candidate_review", "view"):
        fail("Missing qsb_v_shapiromart07_candidate_review.")
    rows = fetch_dicts(
        con,
        """
        SELECT
            review_rank,
            source_table,
            source_field_or_token,
            candidate_class,
            selected_for_resolution,
            review_status,
            documented_semantic_evidence,
            semantic_evidence_source
        FROM qsb_v_shapiromart07_candidate_review
        ORDER BY
            CASE
                WHEN source_table = 'raw_field_value'
                 AND source_field_or_token = 'tim_token_003' THEN 0
                ELSE 1
            END,
            review_rank,
            source_table,
            source_field_or_token
        """,
    )
    names = [normalize_candidate(row) for row in rows]
    if names != EXPECTED_CANDIDATES:
        fail(f"Unexpected SHAPIROMART07 candidate order/set: {names}")
    return rows


def query_line_type_counts(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT line_type, token_count, COUNT(*) AS record_count
        FROM raw_record
        GROUP BY line_type, token_count
        ORDER BY line_type, token_count
        """,
    )


def query_db21_target_distribution(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            r.line_type,
            r.token_count,
            fv.field_name,
            fv.field_index,
            COUNT(*) AS record_count
        FROM db21_tim_raw_field_value fv
        JOIN db21_tim_raw_record r
          ON r.tim_record_id = fv.tim_record_id
        WHERE fv.field_name = ?
        GROUP BY r.line_type, r.token_count, fv.field_name, fv.field_index
        ORDER BY r.line_type, r.token_count, fv.field_index
        """,
        (TARGET_TOKEN,),
    )


def query_workcopy_target_distribution(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            rr.line_type,
            rr.token_count,
            fv.field_name,
            fv.token_position,
            COUNT(*) AS record_count
        FROM raw_field_value fv
        JOIN raw_record rr
          ON rr.raw_record_id = fv.raw_record_id
        WHERE fv.field_name = ?
        GROUP BY rr.line_type, rr.token_count, fv.field_name, fv.token_position
        ORDER BY rr.line_type, rr.token_count, fv.token_position
        """,
        (TARGET_TOKEN,),
    )


def query_source_inventory(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            source_path,
            relative_path,
            source_file_name,
            source_file_extension,
            source_file_size_bytes,
            source_file_mtime_utc,
            source_file_hash_sha256,
            source_type,
            structure_kind,
            line_count,
            selected_for_db21_tim_ingest,
            parse_status,
            quality_status,
            quarantine_status
        FROM db21_par_tim_source_inventory
        WHERE source_type = 'TIM'
        ORDER BY selected_for_db21_tim_ingest DESC, relative_path
        """,
    )


def query_ingest_run(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            ingest_run_id,
            script_path,
            block_name,
            selected_tim_relative_path,
            tim_raw_record_count,
            tim_raw_field_value_count,
            tim_comment_line_count,
            tim_malformed_or_short_line_count,
            run_status,
            stop_reason
        FROM db21_tim_ingest_run
        ORDER BY ingest_timestamp_utc
        """,
    )


def query_map_token_dictionary(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            line_family,
            token_position,
            proposed_structural_name,
            controlled_field_name,
            structural_role,
            mapping_status,
            review_status,
            notes
        FROM map_token_dictionary
        WHERE token_position = ?
        ORDER BY line_family
        """,
        (TARGET_TOKEN,),
    )


def query_db23_staging(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            line_type_scope,
            token_position,
            field_name,
            staging_field_name,
            staging_data_class,
            inclusion_status,
            mapping_status,
            mapping_basis,
            candidate_role_label,
            needs_mapping_flag
        FROM db23_tim_staging_field_map
        WHERE field_name = ?
        ORDER BY line_type_scope
        """,
        (TARGET_TOKEN,),
    )


def query_db23_roles(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            line_type_scope,
            token_position,
            field_name,
            candidate_role_label,
            candidate_role_basis,
            evidence_class,
            present_count,
            coverage_fraction,
            source_recommendation
        FROM db23_tim_token_role_candidate
        WHERE field_name = ?
        ORDER BY line_type_scope
        """,
        (TARGET_TOKEN,),
    )


def query_db26_seed(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            line_family,
            token_position,
            proposed_structural_name,
            structural_role_candidate,
            mapping_status,
            confidence_class,
            evidence_summary
        FROM db26_field_dictionary_seed
        WHERE token_position = ?
        ORDER BY line_family
        """,
        (TARGET_TOKEN,),
    )


def query_review_decisions(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT decision_status, decision_priority, decision_text, notes
        FROM map_review_decision
        WHERE token_dictionary_id IN (
            SELECT token_dictionary_id
            FROM map_token_dictionary
            WHERE token_position = ?
        )
        ORDER BY review_decision_id
        """,
        (TARGET_TOKEN,),
    )


def query_manual_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT decision_status, evidence_strength, source_label,
               evidence_summary, next_action
        FROM dwh14a_manual_evidence_decision
        WHERE token_position = ?
           OR term = ?
        ORDER BY manual_evidence_decision_id
        """,
        (TARGET_TOKEN, TARGET_TOKEN),
    )


def query_status_update_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT dwh14a_decision_status, dwh14a_evidence_strength,
               new_mapping_status, new_review_status, safe_to_promote
        FROM dwh15a_mapping_review_status_update
        WHERE token_position = ?
           OR term = ?
        ORDER BY mapping_review_update_id
        """,
        (TARGET_TOKEN, TARGET_TOKEN),
    )


def query_assertion_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT evidence_status, assertion_status, evidence_summary,
               evidence_ref, review_status
        FROM db28_mapping_assertion_evidence
        WHERE related_token_position = ?
        ORDER BY assertion_id
        """,
        (TARGET_TOKEN,),
    )


def find_line(path: Path, text: str) -> int | None:
    if not path.exists():
        return None
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(),
        start=1,
    ):
        if text in line:
            return line_number
    return None


def code_reference(path: Path, text: str) -> str:
    line = find_line(path, text)
    return f"{path}:{line}" if line is not None else f"{path}:line_not_found"


def source_row(
    source_id: str,
    source_path: str | Path,
    source_type: str,
    source_scope: str,
    dataset_specific: str,
    tool_specific: str,
    software_name: str,
    relevance_status: str,
    notes: str,
    software_version: str = "not_recorded",
) -> dict[str, str]:
    return {
        "source_id": source_id,
        "source_path": str(source_path),
        "source_type": source_type,
        "source_scope": source_scope,
        "dataset_specific": dataset_specific,
        "tool_specific": tool_specific,
        "software_name": software_name,
        "software_version": software_version,
        "relevance_status": relevance_status,
        "notes": notes,
    }


def build_source_identity_rows(
    selected_tim_path: str,
    shapiromart08_summary: dict[str, Any],
) -> list[dict[str, str]]:
    inspected_count = len(shapiromart08_summary.get("inspected_files", []))
    return [
        source_row(
            "SRC_SHAPIROMART07_CANDIDATE_REVIEW_OUTPUT",
            SHAPIROMART07_CANDIDATE_CSV,
            "prior_run_output_csv",
            "local_shapiromart_output",
            "yes",
            "yes",
            "qsb_shapiromart07_timestamp_phase_semantic_resolution.py",
            "used",
            "Provides the four reviewed SHAPIROMART07 candidates and first-reviewed order.",
        ),
        source_row(
            "SRC_SHAPIROMART08_SUMMARY_OUTPUT",
            SHAPIROMART08_SUMMARY_JSON,
            "prior_run_output_json",
            "local_shapiromart_output",
            "yes",
            "yes",
            "qsb_shapiromart08_par_tim_semantic_evidence_review.py",
            "used",
            f"Summarizes Step 1 evidence review; inspected_files_count={inspected_count}.",
        ),
        source_row(
            "SRC_SHAPIROMART08_CANDIDATE_EVIDENCE_OUTPUT",
            SHAPIROMART08_CANDIDATE_EVIDENCE_CSV,
            "prior_run_output_csv",
            "local_shapiromart_output",
            "yes",
            "yes",
            "qsb_shapiromart08_par_tim_semantic_evidence_review.py",
            "used",
            "Documents that Step 1 found no exact local time/phase support for tim_token_003.",
        ),
        source_row(
            "SRC_WORKCOPY_QSB_V_SHAPIROMART07_CANDIDATE_REVIEW",
            "workcopy_db:qsb_v_shapiromart07_candidate_review",
            "db_view",
            "local_workcopy_db",
            "yes",
            "yes",
            "QSB workcopy DB",
            "used",
            "Read-only DB view used to reproduce the candidate set and ordering.",
        ),
        source_row(
            "SRC_WORKCOPY_DB21_INGEST_RUN",
            "workcopy_db:db21_tim_ingest_run",
            "db_table",
            "local_workcopy_db",
            "yes",
            "yes",
            "QSB DB21 ingest",
            "used",
            "Identifies the selected TIM source and DB21 parser script path.",
        ),
        source_row(
            "SRC_WORKCOPY_DB21_RAW_FIELD_VALUES",
            "workcopy_db:db21_tim_raw_record;db21_tim_raw_field_value",
            "db_table",
            "local_workcopy_db",
            "yes",
            "yes",
            "QSB DB21 ingest",
            "used",
            "Documents DB21 field_index and line-type counts without reading raw values.",
        ),
        source_row(
            "SRC_WORKCOPY_RAW_FIELD_VALUE",
            "workcopy_db:raw_record;raw_field_value",
            "db_table",
            "local_workcopy_db",
            "yes",
            "yes",
            "QSB DWH05 workcopy migration",
            "used",
            "Documents workcopy token_position offset caused by raw_line_text pseudo-field.",
        ),
        source_row(
            "SRC_DB21_PARSER_CODE",
            "scripts/qsb_db21_par_tim_joinability_first_timing_ingest.py",
            "parser_code",
            "local_toolchain_code",
            "yes",
            "yes",
            "QSB DB21 parser",
            "used",
            "Shows whitespace tokenization and one-based internal tim_token labels.",
        ),
        source_row(
            "SRC_DWH05_MIGRATION_CODE",
            "scripts/qsb_dwh05_raw_core_migration_dry_run.py",
            "migration_code",
            "local_toolchain_code",
            "yes",
            "yes",
            "QSB DWH05 migration",
            "used",
            "Shows raw_field_value.token_position is migrated from DB21 field_index.",
        ),
        source_row(
            "SRC_DB22_PROFILING_CODE",
            "scripts/qsb_db22_tim_structure_profiling.py",
            "profiling_code",
            "local_toolchain_code",
            "yes",
            "yes",
            "QSB DB22 profiler",
            "used",
            "Shows normalized field_position maps tim_token_003 to position 3.",
        ),
        source_row(
            "SRC_DB23_STAGING_TABLES",
            "workcopy_db:db23_tim_staging_field_map;db23_tim_token_role_candidate",
            "db_tables",
            "local_workcopy_db",
            "yes",
            "yes",
            "QSB DB23 staging",
            "used",
            "Documents data_line token_position=3 and unresolved semantic mapping.",
        ),
        source_row(
            "SRC_DB26_DICTIONARY_SEED_TABLE",
            "workcopy_db:db26_field_dictionary_seed;map_token_dictionary",
            "db_tables",
            "local_workcopy_db",
            "yes",
            "yes",
            "QSB DB26 dictionary seed",
            "used",
            "Documents structural seed status only; no controlled field name.",
        ),
        source_row(
            "SRC_MAPPING_REVIEW_TABLES",
            "workcopy_db:map_review_decision;dwh14a_manual_evidence_decision;"
            "dwh15a_mapping_review_status_update;db28_mapping_assertion_evidence",
            "db_tables",
            "local_workcopy_db",
            "yes",
            "yes",
            "QSB mapping review tables",
            "used",
            "Documents no safe promotion or exact manual token evidence for tim_token_003.",
        ),
        source_row(
            "SRC_SHAPIROINFO53_TIM_STRUCTURE_OUTPUT",
            SHAPIROINFO53_TIM_SUMMARY_JSON,
            "local_run_output_json",
            "local_dataset_structure_output",
            "yes",
            "no",
            "qsb_st_shapiroinfo53_tim_par_content_structure_review.py",
            "context_only",
            "Provides TIM line/column structure context but not token semantic roles.",
        ),
        source_row(
            "SRC_SHAPIROINFO53_TIM_COLUMN_COUNTS_OUTPUT",
            SHAPIROINFO53_TIM_COLUMN_COUNTS_CSV,
            "local_run_output_csv",
            "local_dataset_structure_output",
            "yes",
            "no",
            "qsb_st_shapiroinfo53_tim_par_content_structure_review.py",
            "context_only",
            "Provides 41-column data-like row count context.",
        ),
        source_row(
            "SRC_SHAPIROINFO53_TIM_ROW_FORMAT_OUTPUT",
            SHAPIROINFO53_TIM_ROW_FORMAT_CSV,
            "local_run_output_csv",
            "local_dataset_structure_output",
            "yes",
            "no",
            "qsb_st_shapiroinfo53_tim_par_content_structure_review.py",
            "context_only",
            "Provides TIM row-class count context.",
        ),
        source_row(
            "SRC_LOCAL_QUARANTINE_MANIFEST",
            LOCAL_QUARANTINE_MANIFEST,
            "local_manifest_yaml",
            "local_dataset_provenance",
            "yes",
            "no",
            "SHAPIROINFO34 local manifest",
            "context_only",
            f"Identifies downloaded TIM source path; selected DB21 path={selected_tim_path}.",
        ),
        source_row(
            "SRC_LOCAL_MANUAL_EVIDENCE_CSV",
            LOCAL_MANUAL_EVIDENCE_CSV,
            "local_manual_evidence_csv",
            "local_mapping_evidence",
            "yes",
            "no",
            "manual evidence record",
            "used",
            "Checked for tim_token_003 rows; none found in local manual evidence CSV.",
        ),
        source_row(
            "SRC_SHAPIROINFO55_RESULT_NOTE",
            SHAPIROINFO55_RESULT_NOTE,
            "local_documentation_md",
            "local_dataset_structure_note",
            "yes",
            "no",
            "SHAPIROINFO55 note",
            "context_only",
            "Documents content-structure only and forbids physical value interpretation.",
        ),
        source_row(
            "SRC_SHAPIROINFO57_SCHEMA_SPEC",
            SHAPIROINFO57_SPEC,
            "local_documentation_md",
            "local_method_spec",
            "yes",
            "no",
            "SHAPIROINFO57 spec",
            "context_only",
            "Specifies that later TIM schema maps may record positions but need source-backed semantics.",
        ),
    ]


def db21_distribution_note(rows: list[dict[str, Any]]) -> str:
    parts = []
    for row in rows:
        parts.append(
            f"{row['line_type']} token_count={row['token_count']} "
            f"field_index={row['field_index']} rows={row['record_count']}"
        )
    return "; ".join(parts) if parts else "no db21 rows"


def workcopy_distribution_note(rows: list[dict[str, Any]]) -> str:
    parts = []
    for row in rows:
        parts.append(
            f"{row['line_type']} token_count={row['token_count']} "
            f"token_position={row['token_position']} rows={row['record_count']}"
        )
    return "; ".join(parts) if parts else "no workcopy rows"


def build_format_identity_rows(
    db21_rows: list[dict[str, Any]],
    workcopy_rows: list[dict[str, Any]],
    line_type_counts: list[dict[str, Any]],
    tim_summary: dict[str, Any],
    tim_column_rows: list[dict[str, str]],
    tim_row_format_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    line_counts = "; ".join(
        f"{row['line_type']}:{row['token_count']}={row['record_count']}"
        for row in line_type_counts
    )
    column_counts = "; ".join(
        f"{row.get('apparent_column_count')} columns={row.get('row_count')}"
        for row in tim_column_rows
    ) or "not_available"
    row_formats = "; ".join(
        f"{row.get('line_class')}={row.get('count')}"
        for row in tim_row_format_rows
    ) or "not_available"
    return [
        {
            "source_id": "SRC_DB21_PARSER_CODE",
            "described_line_type": "data_line",
            "tokenization_rule": "line.strip().split(); data_line if len(tokens) >= 5 and a digit occurs in the stripped line",
            "indexing_basis": "tim_token labels use enumerate(tokens, start=1); DB21 field_index is one-based after a raw_line_text pseudo-field",
            "optional_fields_present": "comment_line, blank_line, and malformed_or_short_line branches retained separately; no optional semantic flags documented",
            "format_variant": "DB21 stored variants: " + line_counts,
            "applies_to_dataset": "yes",
            "evidence_class": "exact_indirect_mapping",
            "notes": "Exact for position-to-token naming; does not document a semantic role.",
        },
        {
            "source_id": "SRC_WORKCOPY_DB21_RAW_FIELD_VALUES",
            "described_line_type": "data_line and comment_line",
            "tokenization_rule": "stored DB21 parser output, raw values not inspected by this script",
            "indexing_basis": "field_index includes raw_line_text as field_index 1; tim_token_003 appears at DB21 field_index 4",
            "optional_fields_present": "non-data line branches present",
            "format_variant": db21_distribution_note(db21_rows),
            "applies_to_dataset": "yes",
            "evidence_class": "exact_indirect_mapping",
            "notes": "Shows the raw-field offset that must be normalized before comparing to token_position=3 tables.",
        },
        {
            "source_id": "SRC_DWH05_MIGRATION_CODE",
            "described_line_type": "migrated raw_field_value rows",
            "tokenization_rule": "does not tokenize; copies DB21 field_index into raw_field_value.token_position",
            "indexing_basis": "raw_field_value.token_position=4 for tim_token_003 because raw_line_text is counted",
            "optional_fields_present": "not_applicable",
            "format_variant": workcopy_distribution_note(workcopy_rows),
            "applies_to_dataset": "yes",
            "evidence_class": "exact_indirect_mapping",
            "notes": "Explains why workcopy token_position differs from normalized data-token position.",
        },
        {
            "source_id": "SRC_DB22_PROFILING_CODE",
            "described_line_type": "all_lines, data_line, comment_line, malformed_or_short_line, blank_line",
            "tokenization_rule": "profiles DB21 stored field names; field_position(raw_line_text)=0 and field_position(tim_token_003)=3",
            "indexing_basis": "normalized token_position parsed from tim_token suffix",
            "optional_fields_present": "line scopes separated before staging",
            "format_variant": "data_line normalized position 3 is separate from comment_line normalized position 3",
            "applies_to_dataset": "yes",
            "evidence_class": "exact_indirect_mapping",
            "notes": "Exact for normalized token position; no semantic role is assigned.",
        },
        {
            "source_id": "SRC_DB23_STAGING_TABLES",
            "described_line_type": "data_line",
            "tokenization_rule": "uses DB22 normalized token_position and field_name",
            "indexing_basis": "data_line token_position=3, field_name=tim_token_003",
            "optional_fields_present": "comment_line row also present and scoped separately",
            "format_variant": "data_line staging row has mapping_status=structural_candidate_unmapped_semantics",
            "applies_to_dataset": "yes",
            "evidence_class": "no_mapping_found",
            "notes": "This is the strongest local table for the target token and it explicitly leaves semantics unmapped.",
        },
        {
            "source_id": "SRC_SHAPIROINFO53_TIM_STRUCTURE_OUTPUT",
            "described_line_type": "data_like",
            "tokenization_rule": "whitespace delimiter hint",
            "indexing_basis": "column counts only; no exact role indexing",
            "optional_fields_present": "2-column and 41-column data-like rows reported; row class inventory reported",
            "format_variant": (
                f"tim_files_found={tim_summary.get('tim_files_found', 'not_available')}; "
                f"total_tim_lines={tim_summary.get('total_tim_lines', 'not_available')}; "
                f"column_counts={column_counts}; row_formats={row_formats}"
            ),
            "applies_to_dataset": "yes",
            "evidence_class": "general_format_context_only",
            "notes": "Dataset-specific content structure context; no token-to-role mapping.",
        },
        {
            "source_id": "SRC_LOCAL_QUARANTINE_MANIFEST",
            "described_line_type": "not_parsed_by_manifest",
            "tokenization_rule": "not_applicable",
            "indexing_basis": "not_applicable",
            "optional_fields_present": "not_applicable",
            "format_variant": "manifest identifies source files and notes parsed=false",
            "applies_to_dataset": "yes",
            "evidence_class": "general_format_context_only",
            "notes": "Useful for source identity only.",
        },
    ]


def first_data_line_count(db21_rows: list[dict[str, Any]]) -> int:
    for row in db21_rows:
        if row.get("line_type") == "data_line":
            return int(row.get("record_count") or 0)
    return 0


def build_token_position_mapping_rows(
    db21_rows: list[dict[str, Any]],
    workcopy_rows: list[dict[str, Any]],
    db23_staging: list[dict[str, Any]],
    db23_roles: list[dict[str, Any]],
    db26_seed: list[dict[str, Any]],
    manual_file_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    data_db23 = next(
        (row for row in db23_staging if row.get("line_type_scope") == "data_line"),
        {},
    )
    data_role = next(
        (row for row in db23_roles if row.get("line_type_scope") == "data_line"),
        {},
    )
    data_seed = next(
        (row for row in db26_seed if row.get("line_family") == "data_line"),
        {},
    )
    manual_hits = [
        row
        for row in manual_file_rows
        if row.get("token_position") == TARGET_TOKEN or row.get("term") == TARGET_TOKEN
    ]
    data_count = first_data_line_count(db21_rows)
    return [
        {
            "candidate_name": TARGET_CANDIDATE,
            "internal_token": TARGET_TOKEN,
            "raw_position": "DB21 field_index=4 after raw_line_text pseudo-field; generated from data token_index=3",
            "normalized_position": "data_token_1_based=3",
            "source_id": "SRC_DB21_PARSER_CODE",
            "documented_field_name": TARGET_TOKEN,
            "documented_semantic_role": "unresolved",
            "mapping_chain": "TIM line -> whitespace tokens -> enumerate(tokens,start=1) -> tim_token_003; no role assignment in parser",
            "mapping_class": "no_mapping_found",
            "mapping_strength": "position_exact_role_missing",
            "notes": f"DB21 data_line rows at target field={data_count}. Parser documents naming, not semantics.",
        },
        {
            "candidate_name": TARGET_CANDIDATE,
            "internal_token": TARGET_TOKEN,
            "raw_position": "workcopy raw_field_value.token_position=4",
            "normalized_position": "data_token_1_based=3 after subtracting raw_line_text pseudo-field",
            "source_id": "SRC_DWH05_MIGRATION_CODE",
            "documented_field_name": TARGET_TOKEN,
            "documented_semantic_role": "unresolved",
            "mapping_chain": "DB21 field_index -> DWH05 raw_field_value.token_position; field_name remains tim_token_003; no semantic field role",
            "mapping_class": "no_mapping_found",
            "mapping_strength": "position_offset_explained_role_missing",
            "notes": "The raw workcopy position must not be silently equated with TIM column position without the documented offset.",
        },
        {
            "candidate_name": TARGET_CANDIDATE,
            "internal_token": TARGET_TOKEN,
            "raw_position": f"DB23 data_line token_position={data_db23.get('token_position', 'not_found')}",
            "normalized_position": "data_token_1_based=3",
            "source_id": "SRC_DB23_STAGING_TABLES",
            "documented_field_name": str(data_db23.get("staging_field_name") or TARGET_TOKEN),
            "documented_semantic_role": "unresolved",
            "mapping_chain": (
                "DB22 field_position(tim_token_003)=3 -> DB23 data_line staging row; "
                f"mapping_status={data_db23.get('mapping_status', 'not_found')}; "
                f"candidate_role_label={data_role.get('candidate_role_label', 'not_found')}"
            ),
            "mapping_class": "no_mapping_found",
            "mapping_strength": "local_structural_mapping_semantic_gap",
            "notes": str(data_db23.get("mapping_basis") or "No data_line DB23 staging row found.")[:800],
        },
        {
            "candidate_name": TARGET_CANDIDATE,
            "internal_token": TARGET_TOKEN,
            "raw_position": "DB26 data_line token_position=tim_token_003",
            "normalized_position": "data_token_1_based=3 by token label suffix",
            "source_id": "SRC_DB26_DICTIONARY_SEED_TABLE",
            "documented_field_name": str(data_seed.get("proposed_structural_name") or TARGET_TOKEN),
            "documented_semantic_role": "unresolved",
            "mapping_chain": (
                "DB23 structural staging -> DB26 dictionary seed; "
                f"structural_role_candidate={data_seed.get('structural_role_candidate', 'not_found')}; "
                f"mapping_status={data_seed.get('mapping_status', 'not_found')}"
            ),
            "mapping_class": "no_mapping_found",
            "mapping_strength": "structural_seed_only",
            "notes": "Structural seed is not a documented semantic role.",
        },
        {
            "candidate_name": TARGET_CANDIDATE,
            "internal_token": TARGET_TOKEN,
            "raw_position": "not_documented_for_tim_token_003",
            "normalized_position": "not_documented",
            "source_id": "SRC_SHAPIROINFO53_TIM_STRUCTURE_OUTPUT",
            "documented_field_name": "not_documented",
            "documented_semantic_role": "unresolved",
            "mapping_chain": "Local TIM content-structure outputs document row/column counts only; no token role mapping",
            "mapping_class": "general_format_context_only",
            "mapping_strength": "format_context_only",
            "notes": "Context supports that a 41-token data-like format exists; it does not assign field meaning.",
        },
        {
            "candidate_name": TARGET_CANDIDATE,
            "internal_token": TARGET_TOKEN,
            "raw_position": "not_found_in_manual_evidence",
            "normalized_position": "not_found_in_manual_evidence",
            "source_id": "SRC_LOCAL_MANUAL_EVIDENCE_CSV",
            "documented_field_name": "not_documented",
            "documented_semantic_role": "unresolved",
            "mapping_chain": "Manual evidence CSV checked for tim_token_003/token term; no row found",
            "mapping_class": "no_mapping_found",
            "mapping_strength": "manual_evidence_absent",
            "notes": f"manual_file_hits={len(manual_hits)}",
        },
    ]


def build_parser_writer_alignment_rows() -> list[dict[str, str]]:
    db21_script = Path("scripts/qsb_db21_par_tim_joinability_first_timing_ingest.py")
    dwh05_script = Path("scripts/qsb_dwh05_raw_core_migration_dry_run.py")
    db22_script = Path("scripts/qsb_db22_tim_structure_profiling.py")
    db23_script = Path("scripts/qsb_db23_tim_staging_field_map.py")
    db26_script = Path("scripts/qsb_db26_mapping_gap_triage_field_dictionary_seed.py")
    return [
        {
            "source_id": "SRC_DB21_PARSER_CODE",
            "parser_or_writer": "DB21 TIM raw ingest parser",
            "code_reference": code_reference(db21_script, "for token_index, token in enumerate(tokens, start=1)"),
            "parsing_branch": "classify_tim_line returns data_line when len(tokens) >= 5 and the stripped line contains a digit",
            "field_order_documented": "yes; raw_line_text pseudo-field first, then tim_token_001, tim_token_002, tim_token_003",
            "version_match": "local_toolchain_version_not_recorded_but_script_path_matches_ingest_run",
            "dataset_format_match": "yes; selected DB21 TIM source is J0740+6620.cfr+19.tim",
            "alignment_status": "position_to_internal_token_aligned_semantic_role_missing",
            "notes": "Parser branch supplies token names only.",
        },
        {
            "source_id": "SRC_DWH05_MIGRATION_CODE",
            "parser_or_writer": "DWH05 raw_field_value migration",
            "code_reference": code_reference(dwh05_script, "CAST(field_index AS TEXT)"),
            "parsing_branch": "migration copies DB21 db21_tim_raw_field_value rows",
            "field_order_documented": "yes; token_position is copied from DB21 field_index and therefore includes raw_line_text",
            "version_match": "local_toolchain_version_not_recorded",
            "dataset_format_match": "yes; workcopy rows are migrated from DB21 TIM field values",
            "alignment_status": "offset_documented_semantic_role_missing",
            "notes": "Explains raw workcopy token_position=4 for tim_token_003.",
        },
        {
            "source_id": "SRC_DB22_PROFILING_CODE",
            "parser_or_writer": "DB22 token-position profiler",
            "code_reference": code_reference(db22_script, "def field_position(field_name: str)"),
            "parsing_branch": "profiles DB21 stored field names by line_type_scope",
            "field_order_documented": "yes; raw_line_text=0 and tim_token_NNN maps to integer NNN",
            "version_match": "local_toolchain_version_not_recorded",
            "dataset_format_match": "yes; DB22 profiles DB21 tables for the selected TIM source",
            "alignment_status": "normalized_position_aligned_semantic_role_missing",
            "notes": "Provides the normalized token_position used by DB23.",
        },
        {
            "source_id": "SRC_DB23_STAGING_TABLES",
            "parser_or_writer": "DB23 staging mapper",
            "code_reference": code_reference(db23_script, "gap_note\": \"Token position has structural role candidate only"),
            "parsing_branch": "uses DB22 line_type_scope, token_position, and field_name",
            "field_order_documented": "yes; data_line token_position=3 for tim_token_003",
            "version_match": "local_toolchain_version_not_recorded",
            "dataset_format_match": "yes; staging rows are DB-backed for the same workcopy",
            "alignment_status": "structural_mapping_only",
            "notes": "DB23 marks the target row as structural_candidate_unmapped_semantics.",
        },
        {
            "source_id": "SRC_DB26_DICTIONARY_SEED_TABLE",
            "parser_or_writer": "DB26 dictionary seed builder",
            "code_reference": code_reference(db26_script, "return \"variable_token\", \"seed_only\", 1, \"medium\""),
            "parsing_branch": "data_line variable token seed branch",
            "field_order_documented": "yes; token label is retained as tim_token_003",
            "version_match": "local_toolchain_version_not_recorded",
            "dataset_format_match": "yes; DB26 seed rows derive from DB23/DB23A local tables",
            "alignment_status": "dictionary_seed_only",
            "notes": "Seed status requires review before any semantic use.",
        },
    ]


def build_consistency_rows(mapping_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    semantic_sources = [
        row
        for row in mapping_rows
        if row["source_id"]
        in {
            "SRC_DB21_PARSER_CODE",
            "SRC_DWH05_MIGRATION_CODE",
            "SRC_DB23_STAGING_TABLES",
            "SRC_DB26_DICTIONARY_SEED_TABLE",
            "SRC_LOCAL_MANUAL_EVIDENCE_CSV",
        }
    ]
    return [
        {
            "candidate_name": TARGET_CANDIDATE,
            "source_count": str(len(mapping_rows)),
            "agreeing_source_count": str(len(semantic_sources)),
            "conflicting_source_count": "0",
            "version_mismatch_count": "0",
            "format_mismatch_count": "0",
            "consistency_status": "consistent_unresolved",
            "notes": (
                "Sources agree after normalizing the raw_line_text offset: data-token position 3 maps to "
                "tim_token_003. No source supplies a documented semantic role. Comment-line rows are scoped "
                "separately and are not used as data-line role evidence."
            ),
        }
    ]


def build_scope_rows(
    selected_tim_path: str,
    data_line_count: int,
    ingest_runs: list[dict[str, Any]],
) -> list[dict[str, str]]:
    run = ingest_runs[0] if ingest_runs else {}
    return [
        {
            "candidate_name": TARGET_CANDIDATE,
            "applies_to_all_records": f"position_only_for_{data_line_count}_data_line_records; semantic_role_no",
            "applies_to_line_type": "data_line with 41 tokens; comment_line target token is context-scoped separately",
            "applies_to_files": selected_tim_path or "selected_tim_path_not_found",
            "software_version_scope": "local DB21/DWH05/DB22/DB23 scripts; versions not recorded in source rows",
            "configuration_scope": (
                f"DB21 ingest_run_id={run.get('ingest_run_id', 'not_found')}; "
                f"stop_reason={run.get('stop_reason', 'not_found')}"
            ),
            "scope_status": "position_scope_supported_semantic_scope_unresolved",
            "notes": "The role gap blocks exact token-role support even where position coverage is complete.",
        }
    ]


def build_status_rows() -> list[dict[str, str]]:
    return [
        {
            "candidate_name": TARGET_CANDIDATE,
            "first_reviewed": "yes",
            "exact_mapping_found": "no",
            "documented_semantic_role": "unresolved",
            "strongest_mapping_class": "no_mapping_found",
            "assessment_status": "exact_token_role_unresolved",
            "promotion_evaluated": "no",
            "promotion_applied": "no",
            "main_remaining_gap": MAIN_REMAINING_GAP,
            "recommended_final_review": (
                "Use this unresolved mapping assessment in the single SHAPIROMART09 final decision; "
                "do not apply promotion in Step 2."
            ),
        }
    ]


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_readout(
    path: Path,
    summary: dict[str, Any],
    source_rows: list[dict[str, str]],
    format_rows: list[dict[str, str]],
    mapping_rows: list[dict[str, str]],
    alignment_rows: list[dict[str, str]],
    consistency_rows: list[dict[str, str]],
    scope_rows: list[dict[str, str]],
    status_rows: list[dict[str, str]],
) -> None:
    status = status_rows[0]
    consistency = consistency_rows[0]
    scope = scope_rows[0]
    lines = [
        "# QSB-SHAPIROMART09 Step 2 Exact-Token Mapping Assessment",
        "",
        "## 1. Zweck",
        "",
        (
            "This readout documents whether the local evidence chain connects the concrete "
            "TIM data-line position, internal token `tim_token_003`, and a documented field role."
        ),
        "",
        f"Methodische Grenze: {METHOD_BOUNDARY}",
        "",
        "## 2. verwendete Evidenzquellen",
        "",
        f"- Source rows recorded: {len(source_rows)}",
        f"- First reviewed candidate: {summary['first_reviewed_candidate']}",
        f"- Considered SHAPIROMART07 candidates: {', '.join(summary['considered_candidates'])}",
        f"- Selected TIM source: {summary['selected_tim_source_path']}",
        "",
        "## 3. gepruefte Formatidentitaet",
        "",
    ]
    for row in format_rows:
        lines.append(
            f"- {row['source_id']}: {row['described_line_type']}; "
            f"class={row['evidence_class']}; {row['notes']}"
        )
    lines.extend(
        [
            "",
            "## 4. exakte Tokenpositionspruefung",
            "",
            (
                "DB21 creates `tim_token_003` from the third whitespace data token, but DB21 "
                "also stores `raw_line_text` as field index 1. Therefore the workcopy "
                "`raw_field_value.token_position` value is 4 while the normalized data-token "
                "position is 3."
            ),
            "",
        ]
    )
    for row in mapping_rows:
        lines.append(
            f"- {row['source_id']}: normalized={row['normalized_position']}; "
            f"role={row['documented_semantic_role']}; class={row['mapping_class']}; "
            f"{row['mapping_strength']}"
        )
    lines.extend(
        [
            "",
            "## 5. Parser-/Writer-Abgleich",
            "",
        ]
    )
    for row in alignment_rows:
        lines.append(
            f"- {row['parser_or_writer']}: {row['alignment_status']} "
            f"({row['code_reference']})"
        )
    lines.extend(
        [
            "",
            "## 6. Konsistenz und Reichweite",
            "",
            f"- Consistency status: {consistency['consistency_status']}",
            f"- Conflicting source count: {consistency['conflicting_source_count']}",
            f"- Scope status: {scope['scope_status']}",
            f"- Applies to line type: {scope['applies_to_line_type']}",
            "",
            "## 7. Assessment fuer tim_token_003",
            "",
            f"- exact_mapping_found: {status['exact_mapping_found']}",
            f"- documented_semantic_role: {status['documented_semantic_role']}",
            f"- strongest_mapping_class: {status['strongest_mapping_class']}",
            f"- assessment_status: {status['assessment_status']}",
            f"- promotion_evaluated: {status['promotion_evaluated']}",
            f"- promotion_applied: {status['promotion_applied']}",
            "",
            "## 8. verbleibende Evidenzluecke",
            "",
            f"- {status['main_remaining_gap']}",
            "",
            "## 9. Vorbereitung der einen SHAPIROMART09-Abschlussentscheidung",
            "",
            (
                "Step 2 supplies an unresolved exact-token-role assessment. The later "
                "SHAPIROMART09 closing decision should use this row together with any "
                "other Step 9 evidence and should keep promotion disabled unless a new "
                "source-backed exact role relation is documented."
            ),
            "",
            "## 10. Limitationen",
            "",
            "- Software versions are not recorded in the inspected local script or DB rows.",
            "- General TIM/TOA convention context was not used as exact role support.",
            "- The raw TIM file body was not broadly searched by this script; DB-backed structure and local documented outputs were used.",
            "- No semantic role was inferred from numeric values, monotonicity, distribution, or value ranges.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    if not args.repo_root.exists():
        fail(f"Repo root not found: {args.repo_root}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    existing_outputs = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing_outputs and not args.overwrite:
        fail(
            "SHAPIROMART09 Step 2 output files already exist. Use --overwrite "
            "to replace only the expected files: " + "; ".join(existing_outputs)
        )


def validate_no_unexpected_outputs(output_root: Path) -> dict[str, Any]:
    expected = set(OUTPUT_FILENAMES)
    actual = {path.name for path in output_root.iterdir() if path.is_file()}
    unexpected = sorted(actual - expected)
    missing = sorted(expected - actual)
    return {
        "expected_output_count": len(expected),
        "actual_output_count": len(actual),
        "missing_outputs": missing,
        "unexpected_outputs": unexpected,
        "passed": not missing and not unexpected,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
    created_at = utc_now()

    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)

    with connect_readonly(args.live_db) as live_con, connect_readonly(args.workcopy_db) as work_con:
        live_checks_before = db_checks(live_con)
        workcopy_checks_before = db_checks(work_con)
        candidates = load_candidates(work_con)
        candidate_names = [normalize_candidate(row) for row in candidates]
        line_type_counts = query_line_type_counts(work_con)
        db21_target_rows = query_db21_target_distribution(work_con)
        workcopy_target_rows = query_workcopy_target_distribution(work_con)
        source_inventory = query_source_inventory(work_con)
        ingest_runs = query_ingest_run(work_con)
        map_token_rows = query_map_token_dictionary(work_con)
        db23_staging = query_db23_staging(work_con)
        db23_roles = query_db23_roles(work_con)
        db26_seed = query_db26_seed(work_con)
        review_decisions = query_review_decisions(work_con)
        manual_db_rows = query_manual_rows(work_con)
        status_update_rows = query_status_update_rows(work_con)
        assertion_rows = query_assertion_rows(work_con)
        live_checks_after = db_checks(live_con)
        workcopy_checks_after = db_checks(work_con)

    live_after = db_state(args.live_db)
    workcopy_after = db_state(args.workcopy_db)

    if live_before != live_after:
        fail("Live DB changed during read-only assessment.")
    if workcopy_before != workcopy_after:
        fail("Workcopy DB changed during read-only assessment.")
    if live_checks_before["integrity_check"] != "ok" or live_checks_after["integrity_check"] != "ok":
        fail("Live DB integrity_check did not return ok.")
    if workcopy_checks_before["integrity_check"] != "ok" or workcopy_checks_after["integrity_check"] != "ok":
        fail("Workcopy DB integrity_check did not return ok.")
    if live_checks_before["foreign_key_violation_count"] or live_checks_after["foreign_key_violation_count"]:
        fail("Live DB foreign_key_check found violations.")
    if workcopy_checks_before["foreign_key_violation_count"] or workcopy_checks_after["foreign_key_violation_count"]:
        fail("Workcopy DB foreign_key_check found violations.")

    shapiromart08_summary = read_json(args.repo_root / SHAPIROMART08_SUMMARY_JSON)
    tim_summary = read_json(args.repo_root / SHAPIROINFO53_TIM_SUMMARY_JSON)
    tim_column_rows = read_csv_rows(args.repo_root / SHAPIROINFO53_TIM_COLUMN_COUNTS_CSV)
    tim_row_format_rows = read_csv_rows(args.repo_root / SHAPIROINFO53_TIM_ROW_FORMAT_CSV)
    manual_file_rows = read_csv_rows(args.repo_root / LOCAL_MANUAL_EVIDENCE_CSV)

    selected_tim = next(
        (row for row in source_inventory if int(row.get("selected_for_db21_tim_ingest") or 0) == 1),
        source_inventory[0] if source_inventory else {},
    )
    selected_tim_path = str(selected_tim.get("source_path") or selected_tim.get("relative_path") or "")

    source_rows = build_source_identity_rows(selected_tim_path, shapiromart08_summary)
    format_rows = build_format_identity_rows(
        db21_target_rows,
        workcopy_target_rows,
        line_type_counts,
        tim_summary,
        tim_column_rows,
        tim_row_format_rows,
    )
    mapping_rows = build_token_position_mapping_rows(
        db21_target_rows,
        workcopy_target_rows,
        db23_staging,
        db23_roles,
        db26_seed,
        manual_file_rows,
    )
    alignment_rows = build_parser_writer_alignment_rows()
    consistency_rows = build_consistency_rows(mapping_rows)
    scope_rows = build_scope_rows(
        selected_tim_path,
        first_data_line_count(db21_target_rows),
        ingest_runs,
    )
    status_rows = build_status_rows()

    validation = {
        "live_db_before": {
            "state": live_before,
            "checks": live_checks_before,
        },
        "live_db_after": {
            "state": live_after,
            "checks": live_checks_after,
        },
        "workcopy_db_before": {
            "state": workcopy_before,
            "checks": workcopy_checks_before,
        },
        "workcopy_db_after": {
            "state": workcopy_after,
            "checks": workcopy_checks_after,
        },
        "live_db_unchanged": live_before == live_after,
        "workcopy_db_unchanged": workcopy_before == workcopy_after,
        "exactly_4_shapiromart07_candidates_considered": candidate_names == EXPECTED_CANDIDATES,
        "tim_token_003_first_reviewed": candidate_names[0] == TARGET_CANDIDATE,
        "db_write_attempted": False,
        "physical_quantities_computed": False,
        "promotion_evaluated": False,
        "promotion_applied": False,
        "semantics_from_numeric_behavior_used": False,
        "raw_tim_file_body_broad_search_used": False,
    }

    summary: dict[str, Any] = {
        "script": SCRIPT_NAME,
        "run_timestamp_utc": created_at,
        "live_db": str(args.live_db),
        "workcopy_db": str(args.workcopy_db),
        "repo_root": str(args.repo_root),
        "output_root": str(args.output_root),
        "first_reviewed_candidate": candidate_names[0],
        "considered_candidates": candidate_names,
        "candidate_review_count": len(candidate_names),
        "selected_tim_source_path": selected_tim_path,
        "selected_tim_source_inventory": selected_tim,
        "db21_ingest_runs": ingest_runs,
        "line_type_counts": line_type_counts,
        "db21_tim_token_003_distribution": db21_target_rows,
        "workcopy_tim_token_003_distribution": workcopy_target_rows,
        "map_token_dictionary_rows": map_token_rows,
        "db23_staging_rows": db23_staging,
        "db23_role_rows": db23_roles,
        "db26_seed_rows": db26_seed,
        "map_review_decision_rows": review_decisions,
        "manual_db_rows_for_target": manual_db_rows,
        "status_update_rows_for_target": status_update_rows,
        "assertion_rows_for_target": assertion_rows,
        "exact_mappings_found": 0,
        "strongest_mapping_class": status_rows[0]["strongest_mapping_class"],
        "assessment_status_for_tim_token_003": status_rows[0]["assessment_status"],
        "documented_semantic_role_for_tim_token_003": status_rows[0]["documented_semantic_role"],
        "main_remaining_gap": MAIN_REMAINING_GAP,
        "recommended_final_review": status_rows[0]["recommended_final_review"],
        "method_boundary": METHOD_BOUNDARY,
        "validation": validation,
        "warnings": [
            "Position-to-token naming is supported, but token-to-semantic-role mapping is not.",
            "raw_field_value.token_position counts raw_line_text; normalized data-token position is 3.",
            "General TIM/TOA context was treated as context only.",
            "No conflict file was created because no conflicting exact role mapping was found.",
        ],
    }

    paths = output_paths(args.output_root)
    write_readout(
        paths[READOUT_MD],
        summary,
        source_rows,
        format_rows,
        mapping_rows,
        alignment_rows,
        consistency_rows,
        scope_rows,
        status_rows,
    )
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_csv(paths[SOURCE_IDENTITY_CSV], source_rows, SOURCE_IDENTITY_FIELDS)
    write_csv(paths[FORMAT_IDENTITY_CSV], format_rows, FORMAT_IDENTITY_FIELDS)
    write_csv(paths[TOKEN_POSITION_MAPPING_CSV], mapping_rows, TOKEN_POSITION_MAPPING_FIELDS)
    write_csv(paths[PARSER_WRITER_ALIGNMENT_CSV], alignment_rows, PARSER_WRITER_ALIGNMENT_FIELDS)
    write_csv(paths[MAPPING_CONSISTENCY_CSV], consistency_rows, MAPPING_CONSISTENCY_FIELDS)
    write_csv(paths[MAPPING_SCOPE_CSV], scope_rows, MAPPING_SCOPE_FIELDS)
    write_csv(paths[STEP2_STATUS_CSV], status_rows, STEP2_STATUS_FIELDS)

    output_validation = validate_no_unexpected_outputs(args.output_root)
    if not output_validation["passed"]:
        fail(f"Output validation failed: {output_validation}")
    summary["validation"]["output_files"] = output_validation
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QSB-SHAPIROMART09 Step 2 exact-token mapping assessment."
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the expected SHAPIROMART09 Step 2 output files.",
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
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
