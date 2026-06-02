#!/usr/bin/env python3
"""QSB-DB23 TIM staging field map / token role candidates.

This script copies the DB22 TIM structure profiling database to a DB23 output
database and builds conservative staging maps from DB22 profiling views only.
It does not read raw TIM/PAR source files, assign physical meaning to TIM
columns, compute TOAs, residuals, delays, physical timing parameters, model
quantities, perform statistical inference, or make Shapiro/QSB/Bridge claims.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCK_NAME = "QSB-DB23_TIM_STAGING_FIELD_MAP"
SCRIPT_PATH = Path("scripts/qsb_db23_tim_staging_field_map.py")
DEFAULT_INPUT_DB = Path("runs/QSB-DB/QSB_DB22_TIM_STRUCTURE_PROFILING/qsb_research_tim_structure_profile.db")
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB23_TIM_STAGING_FIELD_MAP")
DEFAULT_OUTPUT_DB_NAME = "qsb_research_tim_staging_field_map.db"

READOUT_NAME = "readout.md"
SUMMARY_NAME = "summary.json"
TOKEN_ROLE_CANDIDATES_NAME = "token_role_candidates.csv"
STAGING_FIELD_MAP_NAME = "staging_field_map.csv"
MAPPING_GAP_REPORT_NAME = "mapping_gap_report.csv"
TABLE_COUNTS_NAME = "table_counts.csv"

CLAIM_BOUNDARY = (
    "DB23 is a conservative TIM staging field-map step based only on DB22 "
    "structural profiling. It does not assign physical meaning to TIM columns, "
    "compute TOAs, residuals, delays, physical timing parameters, or model "
    "quantities. It does not perform statistical inference, Shapiro confirmation, "
    "QSB validation, Bridge evidence claims, or physical interpretation."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy DB22 to DB23 and create conservative TIM token role candidates, "
            "staging field maps, record-family maps, mapping gaps, and decision logs from DB22 views."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help=f"DB22 input DB. Default: {DEFAULT_INPUT_DB}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"DB23 output root. Default: {DEFAULT_OUTPUT_ROOT}",
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
        help="Overwrite non-DB DB23 export artifacts if they already exist. The DB is never overwritten.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Check DB22 source views and planned output paths without creating files.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def output_db_path(output_root: Path, output_db: Path | None) -> Path:
    return output_db if output_db is not None else output_root / DEFAULT_OUTPUT_DB_NAME


def ensure_no_output_collision(paths: list[Path], output_db: Path, overwrite: bool) -> None:
    if output_db.exists():
        raise FileExistsError(f"DB23 output DB already exists: {output_db}")
    existing = [path for path in paths if path != output_db and path.exists()]
    if existing and not overwrite:
        joined = "\n".join(path.as_posix() for path in existing)
        raise FileExistsError(f"DB23 output artifact(s) already exist:\n{joined}")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def insert_row(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> int:
    columns = list(values)
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    cur = conn.execute(sql, [values[column] for column in columns])
    return int(cur.lastrowid)


def table_rows(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cur = conn.execute(query, params)
    columns = [item[0] for item in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def required_view_counts(conn: sqlite3.Connection) -> dict[str, int]:
    views = [
        "qsb_v_db22_tim_line_type_counts",
        "qsb_v_db22_tim_token_count_distribution",
        "qsb_v_db22_tim_token_position_profile",
        "qsb_v_db22_tim_staging_eligibility",
        "qsb_v_db22_tim_pattern_notes",
        "qsb_v_db22_measurement_reality_dashboard",
    ]
    return {view: int(conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0]) for view in views}


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS db23_tim_token_role_candidate (
            token_role_candidate_id INTEGER PRIMARY KEY,
            line_type_scope TEXT NOT NULL,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            candidate_role_label TEXT NOT NULL,
            candidate_role_basis TEXT NOT NULL,
            evidence_class TEXT NOT NULL,
            present_count INTEGER NOT NULL,
            coverage_fraction REAL NOT NULL,
            distinct_value_count INTEGER NOT NULL,
            numeric_like_count INTEGER NOT NULL,
            text_like_count INTEGER NOT NULL,
            low_variance_flag TEXT NOT NULL,
            source_recommendation TEXT NOT NULL,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db23_tim_staging_field_map (
            staging_field_map_id INTEGER PRIMARY KEY,
            line_type_scope TEXT NOT NULL,
            record_family_label TEXT,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            staging_field_name TEXT NOT NULL,
            staging_data_class TEXT NOT NULL,
            inclusion_status TEXT NOT NULL,
            mapping_status TEXT NOT NULL,
            mapping_basis TEXT NOT NULL,
            candidate_role_label TEXT NOT NULL,
            present_count INTEGER NOT NULL,
            coverage_fraction REAL NOT NULL,
            needs_mapping_flag INTEGER NOT NULL,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db23_tim_record_family_map (
            record_family_map_id INTEGER PRIMARY KEY,
            token_count INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            record_count INTEGER NOT NULL,
            record_fraction REAL NOT NULL,
            family_label TEXT NOT NULL,
            map_role TEXT NOT NULL,
            staging_scope TEXT NOT NULL,
            map_note TEXT NOT NULL,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db23_tim_mapping_gap (
            mapping_gap_id INTEGER PRIMARY KEY,
            gap_scope TEXT NOT NULL,
            line_type_scope TEXT,
            token_position INTEGER,
            field_name TEXT,
            gap_type TEXT NOT NULL,
            gap_severity TEXT NOT NULL,
            gap_note TEXT NOT NULL,
            recommended_next_action TEXT NOT NULL,
            supporting_count INTEGER,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db23_tim_staging_decision_log (
            staging_decision_log_id INTEGER PRIMARY KEY,
            decision_key TEXT NOT NULL UNIQUE,
            decision_scope TEXT NOT NULL,
            decision_status TEXT NOT NULL,
            decision_basis TEXT NOT NULL,
            affected_row_count INTEGER,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );
        """
    )


def create_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP VIEW IF EXISTS qsb_v_db23_tim_token_role_candidates;
        CREATE VIEW qsb_v_db23_tim_token_role_candidates AS
        SELECT
            line_type_scope,
            token_position,
            field_name,
            candidate_role_label,
            candidate_role_basis,
            evidence_class,
            present_count,
            coverage_fraction,
            distinct_value_count,
            numeric_like_count,
            text_like_count,
            low_variance_flag,
            source_recommendation,
            claim_boundary
        FROM db23_tim_token_role_candidate
        ORDER BY line_type_scope, token_position, field_name;

        DROP VIEW IF EXISTS qsb_v_db23_tim_record_families;
        CREATE VIEW qsb_v_db23_tim_record_families AS
        SELECT
            token_count,
            line_type,
            record_count,
            record_fraction,
            family_label,
            map_role,
            staging_scope,
            map_note,
            claim_boundary
        FROM db23_tim_record_family_map
        ORDER BY record_count DESC, token_count, line_type;

        DROP VIEW IF EXISTS qsb_v_db23_tim_staging_field_map;
        CREATE VIEW qsb_v_db23_tim_staging_field_map AS
        SELECT
            line_type_scope,
            record_family_label,
            token_position,
            field_name,
            staging_field_name,
            staging_data_class,
            inclusion_status,
            mapping_status,
            mapping_basis,
            candidate_role_label,
            present_count,
            coverage_fraction,
            needs_mapping_flag,
            claim_boundary
        FROM db23_tim_staging_field_map
        ORDER BY line_type_scope, token_position, field_name;

        DROP VIEW IF EXISTS qsb_v_db23_tim_mapping_gaps;
        CREATE VIEW qsb_v_db23_tim_mapping_gaps AS
        SELECT
            gap_scope,
            line_type_scope,
            token_position,
            field_name,
            gap_type,
            gap_severity,
            gap_note,
            recommended_next_action,
            supporting_count,
            claim_boundary
        FROM db23_tim_mapping_gap
        ORDER BY gap_severity DESC, gap_scope, token_position;

        DROP VIEW IF EXISTS qsb_v_db23_tim_staging_preview;
        CREATE VIEW qsb_v_db23_tim_staging_preview AS
        SELECT
            sfm.line_type_scope,
            sfm.record_family_label,
            sfm.token_position,
            sfm.field_name,
            sfm.staging_field_name,
            sfm.staging_data_class,
            sfm.inclusion_status,
            sfm.mapping_status,
            sfm.candidate_role_label,
            sfm.coverage_fraction,
            sfm.claim_boundary
        FROM db23_tim_staging_field_map sfm
        WHERE sfm.line_type_scope IN ('data_line', 'comment_line')
        ORDER BY sfm.line_type_scope, sfm.token_position
        LIMIT 200;

        DROP VIEW IF EXISTS qsb_v_db23_measurement_reality_dashboard;
        CREATE VIEW qsb_v_db23_measurement_reality_dashboard AS
        SELECT 'token_role_candidate_count' AS metric_name, COUNT(*) AS metric_value
        FROM db23_tim_token_role_candidate
        UNION ALL
        SELECT 'staging_field_map_count', COUNT(*)
        FROM db23_tim_staging_field_map
        UNION ALL
        SELECT 'record_family_map_count', COUNT(*)
        FROM db23_tim_record_family_map
        UNION ALL
        SELECT 'mapping_gap_count', COUNT(*)
        FROM db23_tim_mapping_gap
        UNION ALL
        SELECT 'decision_log_count', COUNT(*)
        FROM db23_tim_staging_decision_log
        UNION ALL
        SELECT 'included_staging_field_count', COUNT(*)
        FROM db23_tim_staging_field_map
        WHERE inclusion_status = 'include_in_staging_candidate'
        UNION ALL
        SELECT 'needs_mapping_field_count', COUNT(*)
        FROM db23_tim_staging_field_map
        WHERE needs_mapping_flag = 1
        UNION ALL
        SELECT 'context_only_field_count', COUNT(*)
        FROM db23_tim_staging_field_map
        WHERE inclusion_status = 'context_only'
        UNION ALL
        SELECT 'foreign_key_violation_count', 0;
        """
    )


def candidate_role(row: dict[str, Any]) -> tuple[str, str, str]:
    scope = row["line_type_scope"]
    field_name = row["field_name"]
    recommendation = row["recommendation"]
    numeric_like = int(row["numeric_like_count"])
    text_like = int(row["text_like_count"])
    low_var = row["constant_or_low_variance_flag"]
    distinct_count = int(row["distinct_value_count"])

    if field_name == "raw_line_text":
        return (
            "raw_line_preservation",
            "Full raw line is preserved for audit and replay context.",
            "raw_text_audit",
        )
    if scope in {"comment_line", "malformed_or_short_line", "blank_line"}:
        return (
            f"{scope}_context_token",
            "Line-type scope is context/source-flag/short/blank, not a data staging token.",
            "context_structure",
        )
    if recommendation == "stable_token_position" or low_var == "low_variance_or_constant":
        return (
            "stable_positional_marker_candidate",
            "High coverage with low distinct-value count in DB22 profiling.",
            "structural_low_variance",
        )
    if numeric_like > text_like:
        return (
            "numeric_like_positional_token_candidate",
            "Numeric-like count exceeds text-like count in DB22 profiling.",
            "structural_numeric_like",
        )
    if text_like >= numeric_like and distinct_count > 1:
        return (
            "text_like_positional_token_candidate",
            "Text-like count is dominant or tied in DB22 profiling.",
            "structural_text_like",
        )
    return (
        "unresolved_positional_token_candidate",
        "Structural evidence is insufficient for a narrower role candidate.",
        "unresolved_structure",
    )


def staging_data_class(row: dict[str, Any], role_label: str) -> str:
    if role_label == "raw_line_preservation":
        return "raw_text_line"
    if "numeric_like" in role_label:
        return "raw_text_numeric_like"
    if "stable" in role_label:
        return "raw_text_low_variance_marker"
    if "context" in role_label:
        return "raw_text_context"
    if "text_like" in role_label:
        return "raw_text_text_like"
    return "raw_text_unmapped"


def inclusion_and_mapping(row: dict[str, Any], role_label: str) -> tuple[str, str, int, str]:
    recommendation = row["recommendation"]
    scope = row["line_type_scope"]
    if row["field_name"] == "raw_line_text":
        return (
            "include_as_audit_raw_line",
            "mapped_as_raw_line_only",
            1,
            "Full raw line is retained but not decomposed into semantics.",
        )
    if recommendation == "staging_ready_candidate" and scope == "data_line":
        return (
            "include_in_staging_candidate",
            "structural_candidate_unmapped_semantics",
            1,
            "High-coverage data-line token, but semantic mapping is not assigned.",
        )
    if recommendation == "stable_token_position" and scope == "data_line":
        return (
            "include_in_staging_candidate",
            "stable_marker_candidate_unmapped_semantics",
            1,
            "Stable data-line token position can be staged as raw marker text only.",
        )
    if recommendation == "context_only" or "context" in role_label:
        return (
            "context_only",
            "context_mapping_only",
            0,
            "Context/source-flag-like token retained outside data staging candidate set.",
        )
    if recommendation == "malformed_or_short_context":
        return (
            "retain_as_quality_context",
            "quality_context_only",
            0,
            "Short/blank/malformed context retained with no staging semantics.",
        )
    if recommendation == "optional_token_position":
        return (
            "optional_staging_candidate",
            "optional_structural_candidate_unmapped_semantics",
            1,
            "High or partial coverage token retained as optional structural candidate.",
        )
    return (
        "needs_mapping_before_staging",
        "unmapped",
        1,
        "Explicit mapping needed before analytical staging.",
    )


def staging_field_name(scope: str, field_name: str) -> str:
    safe_scope = scope.replace("_line", "")
    return f"db23_{safe_scope}_{field_name}"


def create_record_family_maps(conn: sqlite3.Connection, created_at: str) -> list[dict[str, Any]]:
    rows = table_rows(conn, "SELECT * FROM qsb_v_db22_tim_token_count_distribution")
    output: list[dict[str, Any]] = []
    for row in rows:
        line_type = row["line_type"]
        if line_type == "data_line":
            map_role = "data_record_family_candidate"
            staging_scope = "data_line_staging_candidate"
        elif line_type == "comment_line":
            map_role = "context_record_family"
            staging_scope = "context_only"
        elif line_type in {"blank_line", "malformed_or_short_line"}:
            map_role = "quality_context_record_family"
            staging_scope = "quality_context_only"
        else:
            map_role = "unknown_record_family"
            staging_scope = "unknown"
        values = {
            "token_count": row["token_count"],
            "line_type": line_type,
            "record_count": row["record_count"],
            "record_fraction": row["record_fraction"],
            "family_label": row["family_label"],
            "map_role": map_role,
            "staging_scope": staging_scope,
            "map_note": row["family_note"],
            "claim_boundary": CLAIM_BOUNDARY,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db23_tim_record_family_map", values)
        output.append(values)
    return output


def create_token_maps(conn: sqlite3.Connection, created_at: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    query = """
        SELECT
            p.line_type_scope,
            p.token_position,
            p.field_name,
            p.present_count,
            p.blank_count,
            p.distinct_value_count,
            p.example_values,
            p.numeric_like_count,
            p.text_like_count,
            p.constant_or_low_variance_flag,
            p.coverage_fraction,
            e.recommendation,
            e.recommendation_reason
        FROM qsb_v_db22_tim_token_position_profile p
        JOIN qsb_v_db22_tim_staging_eligibility e
          ON e.line_type_scope = p.line_type_scope
         AND e.field_name = p.field_name
        WHERE p.line_type_scope IN ('data_line', 'comment_line', 'malformed_or_short_line', 'blank_line')
        ORDER BY p.line_type_scope, p.token_position, p.field_name
    """
    source_rows = table_rows(conn, query)
    role_rows: list[dict[str, Any]] = []
    map_rows: list[dict[str, Any]] = []
    family_by_scope = {
        "data_line": "dominant_41_token_data_family",
        "comment_line": "dominant_44_token_source_flag_family",
        "malformed_or_short_line": "short_header_or_malformed_context_family",
        "blank_line": "blank_line_family",
    }
    for row in source_rows:
        role_label, basis, evidence_class = candidate_role(row)
        role_values = {
            "line_type_scope": row["line_type_scope"],
            "token_position": row["token_position"],
            "field_name": row["field_name"],
            "candidate_role_label": role_label,
            "candidate_role_basis": basis,
            "evidence_class": evidence_class,
            "present_count": row["present_count"],
            "coverage_fraction": row["coverage_fraction"],
            "distinct_value_count": row["distinct_value_count"],
            "numeric_like_count": row["numeric_like_count"],
            "text_like_count": row["text_like_count"],
            "low_variance_flag": row["constant_or_low_variance_flag"],
            "source_recommendation": row["recommendation"],
            "claim_boundary": CLAIM_BOUNDARY,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db23_tim_token_role_candidate", role_values)
        role_rows.append(role_values)

        inclusion_status, mapping_status, needs_mapping_flag, mapping_basis = inclusion_and_mapping(row, role_label)
        map_values = {
            "line_type_scope": row["line_type_scope"],
            "record_family_label": family_by_scope.get(row["line_type_scope"], "unknown_family"),
            "token_position": row["token_position"],
            "field_name": row["field_name"],
            "staging_field_name": staging_field_name(row["line_type_scope"], row["field_name"]),
            "staging_data_class": staging_data_class(row, role_label),
            "inclusion_status": inclusion_status,
            "mapping_status": mapping_status,
            "mapping_basis": mapping_basis,
            "candidate_role_label": role_label,
            "present_count": row["present_count"],
            "coverage_fraction": row["coverage_fraction"],
            "needs_mapping_flag": needs_mapping_flag,
            "claim_boundary": CLAIM_BOUNDARY,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db23_tim_staging_field_map", map_values)
        map_rows.append(map_values)
    return role_rows, map_rows


def create_mapping_gaps(conn: sqlite3.Connection, map_rows: list[dict[str, Any]], created_at: str) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    needs_mapping = [row for row in map_rows if row["needs_mapping_flag"] == 1]
    context_rows = [row for row in map_rows if row["inclusion_status"] in {"context_only", "retain_as_quality_context"}]
    raw_line_rows = [row for row in map_rows if row["field_name"] == "raw_line_text"]
    for row in needs_mapping:
        severity = "medium"
        if row["line_type_scope"] == "data_line" and row["inclusion_status"] in {"include_in_staging_candidate", "needs_mapping_before_staging"}:
            severity = "high"
        gap = {
            "gap_scope": "token_position",
            "line_type_scope": row["line_type_scope"],
            "token_position": row["token_position"],
            "field_name": row["field_name"],
            "gap_type": "unassigned_semantic_mapping",
            "gap_severity": severity,
            "gap_note": "Token position has structural role candidate only; no physical or semantic TIM-column meaning assigned.",
            "recommended_next_action": "Define explicit field dictionary before analytical staging.",
            "supporting_count": row["present_count"],
            "claim_boundary": CLAIM_BOUNDARY,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db23_tim_mapping_gap", gap)
        gaps.append(gap)
    for label, rows, note in [
        ("context_only_retention", context_rows, "Context/quality rows are retained but not data-staging fields."),
        ("raw_line_audit_only", raw_line_rows, "Raw line fields are audit carriers and not mapped to interpreted columns."),
    ]:
        gap = {
            "gap_scope": "group",
            "line_type_scope": None,
            "token_position": None,
            "field_name": None,
            "gap_type": label,
            "gap_severity": "info",
            "gap_note": note,
            "recommended_next_action": "Keep as audit/context material unless later mapping gate requires change.",
            "supporting_count": len(rows),
            "claim_boundary": CLAIM_BOUNDARY,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db23_tim_mapping_gap", gap)
        gaps.append(gap)
    return gaps


def create_decision_log(
    conn: sqlite3.Connection,
    role_rows: list[dict[str, Any]],
    map_rows: list[dict[str, Any]],
    family_rows: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    counts = Counter(row["inclusion_status"] for row in map_rows)
    decisions = [
        {
            "decision_key": "db22_only_substrate",
            "decision_scope": "data_substrate",
            "decision_status": "accepted",
            "decision_basis": "DB23 queried DB22 profiling views only; raw source files were not read.",
            "affected_row_count": None,
        },
        {
            "decision_key": "physical_semantics_closed",
            "decision_scope": "claim_boundary",
            "decision_status": "closed",
            "decision_basis": CLAIM_BOUNDARY,
            "affected_row_count": None,
        },
        {
            "decision_key": "role_candidates_structural_only",
            "decision_scope": "token_role_candidates",
            "decision_status": "accepted",
            "decision_basis": "Candidate labels are structural, positional, and evidence-class labels only.",
            "affected_row_count": len(role_rows),
        },
        {
            "decision_key": "include_data_staging_candidates_raw_text",
            "decision_scope": "staging_field_map",
            "decision_status": "accepted",
            "decision_basis": "Data-line structural candidates are included as raw text fields requiring later mapping.",
            "affected_row_count": counts.get("include_in_staging_candidate", 0),
        },
        {
            "decision_key": "retain_context_outside_data_staging",
            "decision_scope": "context_mapping",
            "decision_status": "accepted",
            "decision_basis": "Comment/source-flag, blank, and malformed/short context rows are retained separately.",
            "affected_row_count": counts.get("context_only", 0) + counts.get("retain_as_quality_context", 0),
        },
        {
            "decision_key": "mapping_gaps_open",
            "decision_scope": "mapping_gap",
            "decision_status": "open",
            "decision_basis": "Explicit field dictionary is still required before analytical staging.",
            "affected_row_count": len(gap_rows),
        },
        {
            "decision_key": "record_families_preserved",
            "decision_scope": "record_family_map",
            "decision_status": "accepted",
            "decision_basis": "DB22 token-count families are represented as staging scopes.",
            "affected_row_count": len(family_rows),
        },
    ]
    for decision in decisions:
        values = {
            **decision,
            "claim_boundary": CLAIM_BOUNDARY,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db23_tim_staging_decision_log", values)
    return decisions


def foreign_key_violations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table_name": row[0], "rowid": row[1], "referenced_table": row[2], "fk_id": row[3]}
        for row in rows
    ]


def table_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [
        {"table_name": row[0], "row_count": int(conn.execute(f'SELECT COUNT(*) FROM \"{row[0]}\"').fetchone()[0])}
        for row in rows
    ]


def write_readout(path: Path, summary: dict[str, Any], preview_rows: list[dict[str, Any]], gap_rows: list[dict[str, Any]]) -> None:
    preview_lines = [
        "| line_type_scope | token_position | field_name | staging_field_name | inclusion_status | mapping_status |",
        "| --- | ---: | --- | --- | --- | --- |",
    ]
    for row in preview_rows[:16]:
        preview_lines.append(
            "| "
            + " | ".join(
                [
                    str(row["line_type_scope"]),
                    str(row["token_position"]),
                    str(row["field_name"]),
                    str(row["staging_field_name"]),
                    str(row["inclusion_status"]),
                    str(row["mapping_status"]),
                ]
            )
            + " |"
        )
    gap_lines = [
        "| gap_type | line_type_scope | token_position | field_name | severity | note |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for row in gap_rows[:12]:
        note = str(row["gap_note"]).replace("|", "\\|")
        if len(note) > 90:
            note = note[:87] + "..."
        gap_lines.append(
            "| "
            + " | ".join(
                [
                    str(row["gap_type"]),
                    str(row.get("line_type_scope") or ""),
                    str(row.get("token_position") or ""),
                    str(row.get("field_name") or ""),
                    str(row["gap_severity"]),
                    note,
                ]
            )
            + " |"
        )
    text = "\n".join(
        [
            "# QSB-DB23 TIM Staging Field Map Readout",
            "",
            "## Befund",
            "",
            f"- Input DB copied from `{summary['input_db_path']}`.",
            f"- Output DB written to `{summary['output_db_path']}`.",
            f"- Token role candidates: {summary['token_role_candidate_count']}",
            f"- Staging field map rows: {summary['staging_field_map_count']}",
            f"- Record family map rows: {summary['record_family_map_count']}",
            f"- Mapping gaps: {summary['mapping_gap_count']}",
            f"- DB-only substrate: {summary['file_fallback_used'] == 'no'}.",
            f"- Foreign key violations: {summary['foreign_key_violation_count']}",
            "",
            "## Interpretation",
            "",
            "DB23 converts DB22 structural profiling into a conservative raw-text staging map. "
            "Candidate roles describe structure only: positional numeric-like, text-like, stable marker, "
            "context token, raw-line preservation, or unresolved mapping.",
            "",
            "## Hypothese",
            "",
            "No scientific hypothesis is tested here. DB23 prepares a mapping scaffold for later gated staging work.",
            "",
            "## Offene Lücke",
            "",
            "- TIM token positions still need an explicit field dictionary before analytical use.",
            "- Staging fields remain raw text and do not carry physical column semantics.",
            "- Context/source-flag and malformed/short rows remain represented separately.",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## Staging Preview",
            "",
            *preview_lines,
            "",
            "## Mapping Gaps",
            "",
            *gap_lines,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def dry_run(args: argparse.Namespace, output_db: Path) -> int:
    if not args.input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {args.input_db}")
    con = sqlite3.connect(args.input_db)
    try:
        counts = required_view_counts(con)
    finally:
        con.close()
    print(f"block: {BLOCK_NAME}")
    print("dry_run: true")
    print(f"input_db: {args.input_db}")
    print(f"output_db: {output_db}")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print("claim_boundary:", CLAIM_BOUNDARY)
    return 0


def run(args: argparse.Namespace) -> int:
    output_root = args.output_root
    output_db = output_db_path(output_root, args.output_db)
    readout_path = output_root / READOUT_NAME
    summary_path = output_root / SUMMARY_NAME
    token_role_path = output_root / TOKEN_ROLE_CANDIDATES_NAME
    staging_map_path = output_root / STAGING_FIELD_MAP_NAME
    gap_report_path = output_root / MAPPING_GAP_REPORT_NAME
    table_counts_path = output_root / TABLE_COUNTS_NAME

    if args.dry_run:
        return dry_run(args, output_db)

    if not args.input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {args.input_db}")

    output_root.mkdir(parents=True, exist_ok=True)
    ensure_no_output_collision(
        [output_db, readout_path, summary_path, token_role_path, staging_map_path, gap_report_path, table_counts_path],
        output_db,
        args.overwrite,
    )

    created_at = utc_now()
    shutil.copy2(args.input_db, output_db)
    conn = sqlite3.connect(output_db)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        view_counts = required_view_counts(conn)
        create_schema(conn)
        create_views(conn)
        family_rows = create_record_family_maps(conn, created_at)
        role_rows, map_rows = create_token_maps(conn, created_at)
        gap_rows = create_mapping_gaps(conn, map_rows, created_at)
        decision_rows = create_decision_log(conn, role_rows, map_rows, family_rows, gap_rows, created_at)
        conn.commit()
        fk_rows = foreign_key_violations(conn)
        token_role_export = table_rows(conn, "SELECT * FROM qsb_v_db23_tim_token_role_candidates")
        staging_map_export = table_rows(conn, "SELECT * FROM qsb_v_db23_tim_staging_field_map")
        gap_export = table_rows(conn, "SELECT * FROM qsb_v_db23_tim_mapping_gaps")
        preview_rows = table_rows(conn, "SELECT * FROM qsb_v_db23_tim_staging_preview LIMIT 40")
        dashboard_rows = table_rows(conn, "SELECT * FROM qsb_v_db23_measurement_reality_dashboard")
        counts_rows = table_counts(conn)
    finally:
        conn.close()

    role_counts = Counter(row["candidate_role_label"] for row in role_rows)
    inclusion_counts = Counter(row["inclusion_status"] for row in map_rows)
    gap_counts = Counter(row["gap_type"] for row in gap_rows)
    summary = {
        "block_name": BLOCK_NAME,
        "script_path": SCRIPT_PATH.as_posix(),
        "input_db_path": args.input_db.as_posix(),
        "output_db_path": output_db.as_posix(),
        "output_root": output_root.as_posix(),
        "created_at_utc": created_at,
        "file_fallback_used": "no",
        "file_fallback_reason": "",
        "required_db22_view_counts": view_counts,
        "token_role_candidate_count": len(role_rows),
        "staging_field_map_count": len(map_rows),
        "record_family_map_count": len(family_rows),
        "mapping_gap_count": len(gap_rows),
        "decision_log_count": len(decision_rows),
        "candidate_role_counts": dict(role_counts),
        "inclusion_status_counts": dict(inclusion_counts),
        "mapping_gap_counts": dict(gap_counts),
        "dashboard": dashboard_rows,
        "foreign_key_violation_count": len(fk_rows),
        "foreign_key_violations": fk_rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "limitations": [
            "No raw TIM/PAR source files were read.",
            "No physical meaning was assigned to TIM token positions.",
            "No TOAs, residuals, delays, physical timing parameters, or model quantities were computed.",
            "No statistical inference, Shapiro confirmation, QSB validation, Bridge evidence claim, or physical interpretation was performed.",
        ],
    }

    write_csv(token_role_path, list(token_role_export[0].keys()) if token_role_export else [], token_role_export)
    write_csv(staging_map_path, list(staging_map_export[0].keys()) if staging_map_export else [], staging_map_export)
    write_csv(gap_report_path, list(gap_export[0].keys()) if gap_export else [], gap_export)
    write_csv(table_counts_path, ["table_name", "row_count"], counts_rows)
    write_json(summary_path, summary)
    write_readout(readout_path, summary, preview_rows, gap_export)

    print(f"block: {BLOCK_NAME}")
    print(f"output_db: {output_db}")
    print(f"token_role_candidate_count: {len(role_rows)}")
    print(f"staging_field_map_count: {len(map_rows)}")
    print(f"mapping_gap_count: {len(gap_rows)}")
    print(f"foreign_key_violation_count: {len(fk_rows)}")
    print("claim_boundary:", CLAIM_BOUNDARY)
    return 0


def main() -> int:
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
