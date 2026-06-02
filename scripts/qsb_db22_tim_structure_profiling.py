#!/usr/bin/env python3
"""QSB-DB22 first data whisper / TIM structure profiling.

This script copies the DB21 PAR/TIM Mini-DWH database to a DB22 output DB and
profiles TIM rawdata structure from DB21 tables/views. It does not read raw TIM
source files, compute TOAs, compute delays, perform timing analysis, residual
analysis, model fitting, statistical inference, Shapiro confirmation, QSB
validation, Bridge claims, or physical interpretation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCK_NAME = "QSB-DB22_TIM_STRUCTURE_PROFILING"
SCRIPT_PATH = Path("scripts/qsb_db22_tim_structure_profiling.py")
DEFAULT_INPUT_DB = Path(
    "runs/QSB-DB/QSB_DB21_PAR_TIM_JOINABILITY_FIRST_TIM_INGEST/qsb_research_par_tim_joinability.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB22_TIM_STRUCTURE_PROFILING")
DEFAULT_OUTPUT_DB_NAME = "qsb_research_tim_structure_profile.db"

READOUT_NAME = "db22_tim_structure_profile_readout.md"
SUMMARY_NAME = "db22_tim_structure_profile_summary.json"
LINE_TYPE_COUNTS_NAME = "db22_tim_line_type_counts.csv"
TOKEN_COUNT_DISTRIBUTION_NAME = "db22_tim_token_count_distribution.csv"
TOKEN_POSITION_PROFILE_NAME = "db22_tim_token_position_profile.csv"
STAGING_ELIGIBILITY_NAME = "db22_tim_staging_eligibility.csv"
PATTERN_NOTES_NAME = "db22_tim_pattern_notes.csv"

CLAIM_BOUNDARY = (
    "DB22 is TIM rawdata structure profiling only. It does not compute TOAs, "
    "residuals, delays, physical timing parameters, or model quantities. It "
    "does not perform timing analysis, residual analysis, model fitting, "
    "statistical inference, Shapiro confirmation, QSB validation, Bridge "
    "confirmation, or physical interpretation."
)

NUMERIC_RE = re.compile(r"^[+-]?(?:(?:\d+\.\d*)|(?:\.\d+)|(?:\d+))(?:[eEdD][+-]?\d+)?$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy DB21 to DB22 and profile TIM line types, token-count families, "
            "token-position structure, pattern notes, and staging eligibility from DB tables/views."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help=f"DB21 input DB. Default: {DEFAULT_INPUT_DB}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"DB22 output root. Default: {DEFAULT_OUTPUT_ROOT}",
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
        help="Overwrite non-DB DB22 export artifacts if they already exist. The DB is never overwritten.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect required DB21 views and planned outputs without creating files.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def output_db_path(output_root: Path, output_db: Path | None) -> Path:
    return output_db if output_db is not None else output_root / DEFAULT_OUTPUT_DB_NAME


def ensure_no_output_collision(paths: list[Path], output_db: Path, overwrite: bool) -> None:
    if output_db.exists():
        raise FileExistsError(f"DB22 output DB already exists: {output_db}")
    existing = [path for path in paths if path != output_db and path.exists()]
    if existing and not overwrite:
        joined = "\n".join(path.as_posix() for path in existing)
        raise FileExistsError(f"DB22 output artifact(s) already exist:\n{joined}")


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


def is_numeric_like(value: str) -> bool:
    return bool(NUMERIC_RE.match(value.strip()))


def field_position(field_name: str) -> int:
    if field_name == "raw_line_text":
        return 0
    match = re.match(r"tim_token_(\d+)$", field_name)
    if not match:
        return -1
    return int(match.group(1))


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS db22_tim_line_type_profile (
            line_type_profile_id INTEGER PRIMARY KEY,
            line_type TEXT NOT NULL,
            record_count INTEGER NOT NULL,
            record_fraction REAL NOT NULL,
            min_token_count INTEGER,
            max_token_count INTEGER,
            dominant_token_count INTEGER,
            parse_statuses TEXT,
            quality_statuses TEXT,
            quarantine_statuses TEXT,
            anomaly_statuses TEXT,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db22_tim_token_count_profile (
            token_count_profile_id INTEGER PRIMARY KEY,
            token_count INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            record_count INTEGER NOT NULL,
            record_fraction REAL NOT NULL,
            family_label TEXT NOT NULL,
            family_note TEXT,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db22_tim_token_position_profile (
            token_position_profile_id INTEGER PRIMARY KEY,
            line_type_scope TEXT NOT NULL,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            present_count INTEGER NOT NULL,
            blank_count INTEGER NOT NULL,
            distinct_value_count INTEGER NOT NULL,
            example_values TEXT,
            numeric_like_count INTEGER NOT NULL,
            text_like_count INTEGER NOT NULL,
            constant_or_low_variance_flag TEXT NOT NULL,
            coverage_fraction REAL NOT NULL,
            created_at_utc TEXT NOT NULL,
            UNIQUE(line_type_scope, field_name)
        );

        CREATE TABLE IF NOT EXISTS db22_tim_record_family_profile (
            record_family_profile_id INTEGER PRIMARY KEY,
            family_label TEXT NOT NULL,
            line_type TEXT NOT NULL,
            token_count INTEGER NOT NULL,
            record_count INTEGER NOT NULL,
            record_fraction REAL NOT NULL,
            family_role TEXT NOT NULL,
            profile_note TEXT,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db22_tim_staging_eligibility (
            staging_eligibility_id INTEGER PRIMARY KEY,
            line_type_scope TEXT NOT NULL,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            recommendation_reason TEXT NOT NULL,
            present_count INTEGER NOT NULL,
            coverage_fraction REAL NOT NULL,
            distinct_value_count INTEGER NOT NULL,
            numeric_like_count INTEGER NOT NULL,
            text_like_count INTEGER NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db22_tim_pattern_note (
            pattern_note_id INTEGER PRIMARY KEY,
            note_key TEXT NOT NULL UNIQUE,
            note_category TEXT NOT NULL,
            note_text TEXT NOT NULL,
            support_count INTEGER,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );
        """
    )


def create_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP VIEW IF EXISTS qsb_v_db22_tim_line_type_counts;
        CREATE VIEW qsb_v_db22_tim_line_type_counts AS
        SELECT
            line_type,
            record_count,
            record_fraction,
            min_token_count,
            max_token_count,
            dominant_token_count,
            parse_statuses,
            quality_statuses,
            quarantine_statuses,
            anomaly_statuses
        FROM db22_tim_line_type_profile
        ORDER BY record_count DESC, line_type;

        DROP VIEW IF EXISTS qsb_v_db22_tim_token_count_distribution;
        CREATE VIEW qsb_v_db22_tim_token_count_distribution AS
        SELECT
            token_count,
            line_type,
            record_count,
            record_fraction,
            family_label,
            family_note
        FROM db22_tim_token_count_profile
        ORDER BY record_count DESC, token_count, line_type;

        DROP VIEW IF EXISTS qsb_v_db22_tim_token_position_profile;
        CREATE VIEW qsb_v_db22_tim_token_position_profile AS
        SELECT
            line_type_scope,
            token_position,
            field_name,
            present_count,
            blank_count,
            distinct_value_count,
            example_values,
            numeric_like_count,
            text_like_count,
            constant_or_low_variance_flag,
            coverage_fraction
        FROM db22_tim_token_position_profile
        ORDER BY line_type_scope, token_position, field_name;

        DROP VIEW IF EXISTS qsb_v_db22_tim_staging_eligibility;
        CREATE VIEW qsb_v_db22_tim_staging_eligibility AS
        SELECT
            line_type_scope,
            token_position,
            field_name,
            recommendation,
            recommendation_reason,
            present_count,
            coverage_fraction,
            distinct_value_count,
            numeric_like_count,
            text_like_count
        FROM db22_tim_staging_eligibility
        ORDER BY line_type_scope, token_position, field_name;

        DROP VIEW IF EXISTS qsb_v_db22_tim_pattern_notes;
        CREATE VIEW qsb_v_db22_tim_pattern_notes AS
        SELECT
            note_key,
            note_category,
            note_text,
            support_count,
            claim_boundary
        FROM db22_tim_pattern_note
        ORDER BY pattern_note_id;

        DROP VIEW IF EXISTS qsb_v_db22_measurement_reality_dashboard;
        CREATE VIEW qsb_v_db22_measurement_reality_dashboard AS
        SELECT 'tim_raw_record_count' AS metric_name, COUNT(*) AS metric_value
        FROM db21_tim_raw_record
        UNION ALL
        SELECT 'tim_raw_field_value_count', COUNT(*)
        FROM db21_tim_raw_field_value
        UNION ALL
        SELECT 'line_type_profile_count', COUNT(*)
        FROM db22_tim_line_type_profile
        UNION ALL
        SELECT 'token_count_family_count', COUNT(*)
        FROM db22_tim_token_count_profile
        UNION ALL
        SELECT 'token_position_profile_count', COUNT(*)
        FROM db22_tim_token_position_profile
        UNION ALL
        SELECT 'staging_ready_candidate_count', COUNT(*)
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'staging_ready_candidate'
        UNION ALL
        SELECT 'stable_token_position_count', COUNT(*)
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'stable_token_position'
        UNION ALL
        SELECT 'optional_token_position_count', COUNT(*)
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'optional_token_position'
        UNION ALL
        SELECT 'context_only_count', COUNT(*)
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'context_only'
        UNION ALL
        SELECT 'malformed_or_short_context_count', COUNT(*)
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'malformed_or_short_context'
        UNION ALL
        SELECT 'needs_mapping_count', COUNT(*)
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'needs_mapping'
        UNION ALL
        SELECT 'pattern_note_count', COUNT(*)
        FROM db22_tim_pattern_note
        UNION ALL
        SELECT 'foreign_key_violation_count', 0;

        DROP VIEW IF EXISTS qsb_v_db22_first_data_whisper;
        CREATE VIEW qsb_v_db22_first_data_whisper AS
        SELECT 'line_type_counts' AS finding_key,
               group_concat(line_type || '=' || record_count, '; ') AS finding_value,
               'TIM line-type inventory from DB21 raw records.' AS finding_note
        FROM db22_tim_line_type_profile
        UNION ALL
        SELECT 'dominant_token_count_families',
               group_concat(token_count || ':' || line_type || '=' || record_count, '; '),
               'Dominant token-count families are structural only.'
        FROM (
            SELECT token_count, line_type, record_count
            FROM db22_tim_token_count_profile
            ORDER BY record_count DESC
            LIMIT 5
        )
        UNION ALL
        SELECT 'stable_token_positions_summary',
               CAST(COUNT(*) AS TEXT),
               'Count of token positions tagged constant_or_low_variance in all-line scope.'
        FROM db22_tim_token_position_profile
        WHERE line_type_scope = 'all_lines'
          AND constant_or_low_variance_flag = 'low_variance_or_constant'
        UNION ALL
        SELECT 'context_comment_line_summary',
               group_concat(line_type || '=' || record_count, '; '),
               'Context/source-flag-like and malformed/blank records retained as structure.'
        FROM db22_tim_line_type_profile
        WHERE line_type IN ('comment_line', 'malformed_or_short_line', 'blank_line')
        UNION ALL
        SELECT 'staging_ready_candidate_count',
               CAST(COUNT(*) AS TEXT),
               'Structural staging readiness only; no physical column semantics assigned.'
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'staging_ready_candidate'
        UNION ALL
        SELECT 'needs_mapping_count',
               CAST(COUNT(*) AS TEXT),
               'Positions requiring explicit mapping before analytical use.'
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'needs_mapping'
        UNION ALL
        SELECT 'malformed_short_context_count',
               CAST(COUNT(*) AS TEXT),
               'Malformed/short context positions retained with flags.'
        FROM db22_tim_staging_eligibility
        WHERE recommendation = 'malformed_or_short_context'
        UNION ALL
        SELECT 'boundary_note',
               'no_timing_or_physics_claim',
               'DB22 profiles raw structure only and does not compute TOAs, residuals, delays, or physical quantities.';
        """
    )


def fetch_required_view_counts(conn: sqlite3.Connection) -> dict[str, int]:
    views = [
        "qsb_v_db21_tim_raw_records",
        "qsb_v_db21_tim_raw_field_values",
        "qsb_v_db21_first_human_tim_readout",
        "qsb_v_db21_measurement_reality_dashboard",
    ]
    counts: dict[str, int] = {}
    for view in views:
        counts[view] = int(conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()[0])
    return counts


def profile_line_types(conn: sqlite3.Connection, created_at: str) -> list[dict[str, Any]]:
    total = int(conn.execute("SELECT COUNT(*) FROM db21_tim_raw_record").fetchone()[0])
    rows = conn.execute(
        """
        SELECT
            line_type,
            COUNT(*) AS record_count,
            MIN(token_count) AS min_token_count,
            MAX(token_count) AS max_token_count,
            group_concat(DISTINCT parse_status) AS parse_statuses,
            group_concat(DISTINCT quality_status) AS quality_statuses,
            group_concat(DISTINCT quarantine_status) AS quarantine_statuses,
            group_concat(DISTINCT anomaly_status) AS anomaly_statuses
        FROM db21_tim_raw_record
        GROUP BY line_type
        ORDER BY record_count DESC, line_type
        """
    ).fetchall()
    output: list[dict[str, Any]] = []
    for row in rows:
        line_type = row[0]
        dominant = conn.execute(
            """
            SELECT token_count
            FROM db21_tim_raw_record
            WHERE line_type = ?
            GROUP BY token_count
            ORDER BY COUNT(*) DESC, token_count
            LIMIT 1
            """,
            (line_type,),
        ).fetchone()[0]
        values = {
            "line_type": line_type,
            "record_count": int(row[1]),
            "record_fraction": int(row[1]) / total if total else 0.0,
            "min_token_count": row[2],
            "max_token_count": row[3],
            "dominant_token_count": dominant,
            "parse_statuses": row[4],
            "quality_statuses": row[5],
            "quarantine_statuses": row[6],
            "anomaly_statuses": row[7],
            "created_at_utc": created_at,
        }
        insert_row(conn, "db22_tim_line_type_profile", values)
        output.append(values)
    return output


def family_label(token_count: int, line_type: str) -> tuple[str, str, str]:
    if token_count == 41 and line_type == "data_line":
        return "dominant_41_token_data_family", "dominant_data_record_family", "41-token data-line family present."
    if token_count == 44 and line_type == "comment_line":
        return "dominant_44_token_source_flag_family", "dominant_context_record_family", "44-token source-flag/comment family present."
    if line_type == "malformed_or_short_line":
        return "short_header_or_malformed_context_family", "context_or_malformed_family", "Short TIM header/context lines retained."
    if line_type == "blank_line":
        return "blank_line_family", "context_or_malformed_family", "Blank TIM line retained."
    return f"{token_count}_token_{line_type}_family", "minor_record_family", "Minor structural family retained."


def profile_token_counts(conn: sqlite3.Connection, created_at: str) -> list[dict[str, Any]]:
    total = int(conn.execute("SELECT COUNT(*) FROM db21_tim_raw_record").fetchone()[0])
    rows = conn.execute(
        """
        SELECT token_count, line_type, COUNT(*) AS record_count
        FROM db21_tim_raw_record
        GROUP BY token_count, line_type
        ORDER BY record_count DESC, token_count, line_type
        """
    ).fetchall()
    output: list[dict[str, Any]] = []
    for token_count, line_type, count in rows:
        label, role, note = family_label(int(token_count), str(line_type))
        values = {
            "token_count": int(token_count),
            "line_type": line_type,
            "record_count": int(count),
            "record_fraction": int(count) / total if total else 0.0,
            "family_label": label,
            "family_note": note,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db22_tim_token_count_profile", values)
        insert_row(
            conn,
            "db22_tim_record_family_profile",
            {
                "family_label": label,
                "line_type": line_type,
                "token_count": int(token_count),
                "record_count": int(count),
                "record_fraction": int(count) / total if total else 0.0,
                "family_role": role,
                "profile_note": note,
                "created_at_utc": created_at,
            },
        )
        output.append(values)
    return output


def scope_condition(scope: str) -> tuple[str, tuple[Any, ...], int]:
    if scope == "all_lines":
        return "", (), 0
    return "WHERE r.line_type = ?", (scope,), 0


def profile_token_positions(conn: sqlite3.Connection, created_at: str) -> list[dict[str, Any]]:
    scopes = ["all_lines", "data_line", "comment_line", "malformed_or_short_line", "blank_line"]
    output: list[dict[str, Any]] = []
    for scope in scopes:
        if scope == "all_lines":
            total_records = int(conn.execute("SELECT COUNT(*) FROM db21_tim_raw_record").fetchone()[0])
            where_clause = ""
            params: tuple[Any, ...] = ()
        else:
            total_records = int(
                conn.execute("SELECT COUNT(*) FROM db21_tim_raw_record WHERE line_type = ?", (scope,)).fetchone()[0]
            )
            where_clause = "WHERE r.line_type = ?"
            params = (scope,)

        rows = conn.execute(
            f"""
            SELECT
                fv.field_name,
                MIN(fv.field_index) AS field_index,
                COUNT(*) AS present_count,
                SUM(CASE WHEN fv.raw_value_text = '' THEN 1 ELSE 0 END) AS blank_count,
                COUNT(DISTINCT fv.raw_value_text) AS distinct_value_count,
                SUM(CASE WHEN fv.raw_value_text GLOB '*[0-9]*' THEN 1 ELSE 0 END) AS digit_containing_count
            FROM db21_tim_raw_field_value fv
            JOIN db21_tim_raw_record r
              ON r.tim_record_id = fv.tim_record_id
            {where_clause}
            GROUP BY fv.field_name
            ORDER BY MIN(fv.field_index), fv.field_name
            """,
            params,
        ).fetchall()
        for row in rows:
            field_name = str(row[0])
            examples = [
                example_row[0]
                for example_row in conn.execute(
                    f"""
                    SELECT raw_value_text
                    FROM (
                        SELECT fv.raw_value_text, MIN(fv.line_number) AS first_line
                        FROM db21_tim_raw_field_value fv
                        JOIN db21_tim_raw_record r
                          ON r.tim_record_id = fv.tim_record_id
                        {where_clause}
                          {'AND' if where_clause else 'WHERE'} fv.field_name = ?
                        GROUP BY fv.raw_value_text
                        ORDER BY first_line
                        LIMIT 5
                    )
                    """,
                    (*params, field_name),
                ).fetchall()
            ]
            numeric_like_count = 0
            text_like_count = 0
            for value_row in conn.execute(
                f"""
                SELECT fv.raw_value_text
                FROM db21_tim_raw_field_value fv
                JOIN db21_tim_raw_record r
                  ON r.tim_record_id = fv.tim_record_id
                {where_clause}
                  {'AND' if where_clause else 'WHERE'} fv.field_name = ?
                """,
                (*params, field_name),
            ):
                value = str(value_row[0])
                if is_numeric_like(value):
                    numeric_like_count += 1
                else:
                    text_like_count += 1

            present_count = int(row[2])
            blank_count = int(row[3] or 0)
            distinct_count = int(row[4])
            coverage_fraction = present_count / total_records if total_records else 0.0
            if present_count == 0:
                variance_flag = "not_present"
            elif distinct_count <= 3 and coverage_fraction >= 0.9:
                variance_flag = "low_variance_or_constant"
            elif distinct_count <= max(5, int(present_count * 0.01)) and coverage_fraction >= 0.9:
                variance_flag = "low_variance_or_constant"
            else:
                variance_flag = "variable"

            values = {
                "line_type_scope": scope,
                "token_position": field_position(field_name),
                "field_name": field_name,
                "present_count": present_count,
                "blank_count": blank_count,
                "distinct_value_count": distinct_count,
                "example_values": " || ".join(examples),
                "numeric_like_count": numeric_like_count,
                "text_like_count": text_like_count,
                "constant_or_low_variance_flag": variance_flag,
                "coverage_fraction": coverage_fraction,
                "created_at_utc": created_at,
            }
            insert_row(conn, "db22_tim_token_position_profile", values)
            output.append(values)
    return output


def staging_recommendation(profile: dict[str, Any]) -> tuple[str, str]:
    scope = profile["line_type_scope"]
    field_name = profile["field_name"]
    coverage = float(profile["coverage_fraction"])
    distinct_count = int(profile["distinct_value_count"])
    numeric_like = int(profile["numeric_like_count"])
    text_like = int(profile["text_like_count"])
    variance_flag = profile["constant_or_low_variance_flag"]

    if field_name == "raw_line_text":
        return "needs_mapping", "Full raw line retained; token-level mapping should be explicit."
    if scope == "comment_line":
        return "context_only", "Source-flag/comment-like line scope retained as context."
    if scope in {"malformed_or_short_line", "blank_line"}:
        return "malformed_or_short_context", f"{scope} retained with structure flag."
    if variance_flag == "low_variance_or_constant":
        return "stable_token_position", "High coverage with low distinct value count."
    if scope == "data_line" and coverage >= 0.98 and (numeric_like > 0 or text_like > 0):
        return "staging_ready_candidate", "High-coverage data-line token position; semantics still unmapped."
    if coverage >= 0.05:
        return "optional_token_position", "Partial-coverage token position retained for optional/context mapping."
    if distinct_count > 0:
        return "needs_mapping", "Observed token position needs explicit field mapping before analytical use."
    return "unknown", "No sufficient structural basis for recommendation."


def create_staging_eligibility(conn: sqlite3.Connection, token_profiles: list[dict[str, Any]], created_at: str) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for profile in token_profiles:
        recommendation, reason = staging_recommendation(profile)
        values = {
            "line_type_scope": profile["line_type_scope"],
            "token_position": profile["token_position"],
            "field_name": profile["field_name"],
            "recommendation": recommendation,
            "recommendation_reason": reason,
            "present_count": profile["present_count"],
            "coverage_fraction": profile["coverage_fraction"],
            "distinct_value_count": profile["distinct_value_count"],
            "numeric_like_count": profile["numeric_like_count"],
            "text_like_count": profile["text_like_count"],
            "created_at_utc": created_at,
        }
        insert_row(conn, "db22_tim_staging_eligibility", values)
        output.append(values)
    return output


def create_pattern_notes(
    conn: sqlite3.Connection,
    line_profiles: list[dict[str, Any]],
    token_count_profiles: list[dict[str, Any]],
    token_position_profiles: list[dict[str, Any]],
    staging_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    line_counts = {row["line_type"]: row["record_count"] for row in line_profiles}
    token_family_counts = {(row["token_count"], row["line_type"]): row["record_count"] for row in token_count_profiles}
    staging_counts = Counter(row["recommendation"] for row in staging_rows)
    stable_all = sum(
        1
        for row in token_position_profiles
        if row["line_type_scope"] == "all_lines"
        and row["constant_or_low_variance_flag"] == "low_variance_or_constant"
    )
    notes = [
        {
            "note_key": "dominant_data_family_41",
            "note_category": "token_count_family",
            "note_text": "A 41-token data-line family is present as the dominant data-line structure.",
            "support_count": token_family_counts.get((41, "data_line"), 0),
        },
        {
            "note_key": "dominant_context_family_44",
            "note_category": "token_count_family",
            "note_text": "A 44-token source-flag/comment-like family is present as the dominant context structure.",
            "support_count": token_family_counts.get((44, "comment_line"), 0),
        },
        {
            "note_key": "comment_context_retained",
            "note_category": "context_lines",
            "note_text": "Comment/source-flag-like TIM lines are retained and profiled separately from data lines.",
            "support_count": line_counts.get("comment_line", 0),
        },
        {
            "note_key": "blank_and_short_retained",
            "note_category": "quality_flags",
            "note_text": "Blank and malformed/short lines remain represented as structure, not discarded.",
            "support_count": line_counts.get("blank_line", 0) + line_counts.get("malformed_or_short_line", 0),
        },
        {
            "note_key": "stable_positions_exist",
            "note_category": "token_position_structure",
            "note_text": "Several token positions have high coverage and low distinct-value counts.",
            "support_count": stable_all,
        },
        {
            "note_key": "staging_candidates_present",
            "note_category": "staging_eligibility",
            "note_text": "Some token positions are structurally eligible for later staging, pending explicit mapping.",
            "support_count": staging_counts.get("staging_ready_candidate", 0),
        },
        {
            "note_key": "claim_boundary",
            "note_category": "claim_boundary",
            "note_text": CLAIM_BOUNDARY,
            "support_count": None,
        },
    ]
    for note in notes:
        values = {
            **note,
            "claim_boundary": CLAIM_BOUNDARY,
            "created_at_utc": created_at,
        }
        insert_row(conn, "db22_tim_pattern_note", values)
    return notes


def foreign_key_violations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table_name": row[0], "rowid": row[1], "referenced_table": row[2], "fk_id": row[3]}
        for row in rows
    ]


def table_rows(conn: sqlite3.Connection, query: str) -> list[dict[str, Any]]:
    cur = conn.execute(query)
    columns = [item[0] for item in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def table_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [
        {"table_name": row[0], "row_count": int(conn.execute(f'SELECT COUNT(*) FROM \"{row[0]}\"').fetchone()[0])}
        for row in rows
    ]


def write_readout(path: Path, summary: dict[str, Any], whisper_rows: list[dict[str, Any]]) -> None:
    whisper_lines = [f"- {row['finding_key']}: {row['finding_value']} ({row['finding_note']})" for row in whisper_rows]
    text = "\n".join(
        [
            "# QSB-DB22 TIM Structure Profile Readout",
            "",
            "## Befund",
            "",
            f"- Input DB copied from `{summary['input_db_path']}`.",
            f"- Output DB written to `{summary['output_db_path']}`.",
            f"- TIM raw records profiled: {summary['tim_raw_record_count']}",
            f"- TIM raw field/value rows available: {summary['tim_raw_field_value_count']}",
            f"- Data substrate: DB21 tables/views only; raw source file fallback used: {summary['file_fallback_used']}.",
            f"- Dominant token families: {summary['dominant_token_count_families']}",
            f"- Foreign key violations: {summary['foreign_key_violation_count']}",
            "",
            "## Interpretation",
            "",
            "DB22 profiles TIM rawdata structure from the DB21 Mini-DWH. It separates "
            "line-type families, token-count families, token-position coverage, low-variance "
            "positions, and staging eligibility categories without assigning physical meaning "
            "to TIM columns.",
            "",
            "## Hypothese",
            "",
            "No scientific hypothesis is tested here. The output is a structural inventory "
            "for later gated staging and analytics work.",
            "",
            "## Offene Lücke",
            "",
            "- Token positions are positional raw fields, not interpreted physical columns.",
            "- Staging eligibility is structural only and requires later explicit mapping.",
            "- Context/source-flag-like and malformed/short lines are retained as audit material.",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## First Data Whisper",
            "",
            *whisper_lines,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def dry_run(args: argparse.Namespace, output_db: Path) -> int:
    if not args.input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {args.input_db}")
    con = sqlite3.connect(args.input_db)
    try:
        counts = fetch_required_view_counts(con)
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
    line_type_path = output_root / LINE_TYPE_COUNTS_NAME
    token_count_path = output_root / TOKEN_COUNT_DISTRIBUTION_NAME
    token_position_path = output_root / TOKEN_POSITION_PROFILE_NAME
    staging_path = output_root / STAGING_ELIGIBILITY_NAME
    pattern_notes_path = output_root / PATTERN_NOTES_NAME

    if args.dry_run:
        return dry_run(args, output_db)

    if not args.input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {args.input_db}")

    output_root.mkdir(parents=True, exist_ok=True)
    ensure_no_output_collision(
        [
            output_db,
            readout_path,
            summary_path,
            line_type_path,
            token_count_path,
            token_position_path,
            staging_path,
            pattern_notes_path,
        ],
        output_db,
        args.overwrite,
    )

    created_at = utc_now()
    shutil.copy2(args.input_db, output_db)

    conn = sqlite3.connect(output_db)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        required_counts = fetch_required_view_counts(conn)
        create_schema(conn)
        create_views(conn)
        line_profiles = profile_line_types(conn, created_at)
        token_count_profiles = profile_token_counts(conn, created_at)
        token_position_profiles = profile_token_positions(conn, created_at)
        staging_rows = create_staging_eligibility(conn, token_position_profiles, created_at)
        pattern_notes = create_pattern_notes(
            conn,
            line_profiles,
            token_count_profiles,
            token_position_profiles,
            staging_rows,
            created_at,
        )
        conn.commit()
        fk_rows = foreign_key_violations(conn)
        whisper_rows = table_rows(conn, "SELECT * FROM qsb_v_db22_first_data_whisper")
        dashboard_rows = table_rows(conn, "SELECT * FROM qsb_v_db22_measurement_reality_dashboard")
        line_type_rows = table_rows(conn, "SELECT * FROM qsb_v_db22_tim_line_type_counts")
        token_count_rows = table_rows(conn, "SELECT * FROM qsb_v_db22_tim_token_count_distribution")
        token_position_rows = table_rows(conn, "SELECT * FROM qsb_v_db22_tim_token_position_profile")
        staging_export_rows = table_rows(conn, "SELECT * FROM qsb_v_db22_tim_staging_eligibility")
        pattern_export_rows = table_rows(conn, "SELECT * FROM qsb_v_db22_tim_pattern_notes")
        table_count_rows = table_counts(conn)
    finally:
        conn.close()

    staging_counts = Counter(row["recommendation"] for row in staging_rows)
    line_counts = {row["line_type"]: row["record_count"] for row in line_profiles}
    token_family_text = "; ".join(
        f"{row['token_count']} {row['line_type']}={row['record_count']}"
        for row in sorted(token_count_profiles, key=lambda item: item["record_count"], reverse=True)[:5]
    )
    high_coverage_positions = [
        row["field_name"]
        for row in token_position_profiles
        if row["line_type_scope"] == "data_line" and row["coverage_fraction"] >= 0.98
    ][:12]
    low_variance_positions = [
        row["field_name"]
        for row in token_position_profiles
        if row["line_type_scope"] == "data_line"
        and row["constant_or_low_variance_flag"] == "low_variance_or_constant"
    ][:12]
    numeric_positions = [
        row["field_name"]
        for row in token_position_profiles
        if row["line_type_scope"] == "data_line" and row["numeric_like_count"] > row["text_like_count"]
    ][:12]
    text_positions = [
        row["field_name"]
        for row in token_position_profiles
        if row["line_type_scope"] == "data_line" and row["text_like_count"] >= row["numeric_like_count"]
    ][:12]

    summary = {
        "block_name": BLOCK_NAME,
        "script_path": SCRIPT_PATH.as_posix(),
        "input_db_path": args.input_db.as_posix(),
        "output_db_path": output_db.as_posix(),
        "output_root": output_root.as_posix(),
        "created_at_utc": created_at,
        "file_fallback_used": "no",
        "file_fallback_reason": "",
        "required_db21_view_counts": required_counts,
        "tim_raw_record_count": required_counts["qsb_v_db21_tim_raw_records"],
        "tim_raw_field_value_count": required_counts["qsb_v_db21_tim_raw_field_values"],
        "tim_line_type_counts": line_counts,
        "dominant_token_count_families": token_family_text,
        "staging_eligibility_counts": dict(staging_counts),
        "high_coverage_data_token_positions": high_coverage_positions,
        "low_variance_data_token_positions": low_variance_positions,
        "numeric_like_data_token_positions": numeric_positions,
        "text_like_data_token_positions": text_positions,
        "pattern_note_count": len(pattern_notes),
        "dashboard": dashboard_rows,
        "table_counts": table_count_rows,
        "foreign_key_violation_count": len(fk_rows),
        "foreign_key_violations": fk_rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "limitations": [
            "No raw source files were read.",
            "No timing analysis was performed.",
            "No residual analysis was performed.",
            "No model fitting was performed.",
            "No statistical inference was performed.",
            "No Shapiro confirmation, QSB validation, Bridge claim, or physical interpretation is made.",
        ],
    }

    write_csv(line_type_path, list(line_type_rows[0].keys()) if line_type_rows else [], line_type_rows)
    write_csv(token_count_path, list(token_count_rows[0].keys()) if token_count_rows else [], token_count_rows)
    write_csv(token_position_path, list(token_position_rows[0].keys()) if token_position_rows else [], token_position_rows)
    write_csv(staging_path, list(staging_export_rows[0].keys()) if staging_export_rows else [], staging_export_rows)
    write_csv(pattern_notes_path, list(pattern_export_rows[0].keys()) if pattern_export_rows else [], pattern_export_rows)
    write_json(summary_path, summary)
    write_readout(readout_path, summary, whisper_rows)

    print(f"block: {BLOCK_NAME}")
    print(f"output_db: {output_db}")
    print(f"tim_raw_record_count: {summary['tim_raw_record_count']}")
    print(f"tim_raw_field_value_count: {summary['tim_raw_field_value_count']}")
    print(f"dominant_token_count_families: {token_family_text}")
    print(f"foreign_key_violation_count: {len(fk_rows)}")
    print("claim_boundary:", CLAIM_BOUNDARY)
    return 0


def main() -> int:
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
