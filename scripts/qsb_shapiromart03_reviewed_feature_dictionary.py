#!/usr/bin/env python3
"""QSB-SHAPIROMART03: reviewed minimal feature dictionary.

This script creates a compact provisional feature dictionary from the
SHAPIROMART02 numeric-field inspection. It records structural roles only and
does not assign final physical meaning or compute analysis quantities.
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


SCRIPT_NAME = "scripts/qsb_shapiromart03_reviewed_feature_dictionary.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART03_REVIEWED_FEATURE_DICTIONARY"
)

READOUT_MD = "shapiromart03_readout.md"
SUMMARY_JSON = "shapiromart03_summary.json"
DICTIONARY_CSV = "shapiromart03_feature_dictionary.csv"
EXCLUSION_CSV = "shapiromart03_excluded_features.csv"
READINESS_CSV = "shapiromart03_fingerprint_readiness.csv"
NEXT_STEP_CSV = "shapiromart03_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    DICTIONARY_CSV,
    EXCLUSION_CSV,
    READINESS_CSV,
    NEXT_STEP_CSV,
]

TARGET_TABLES = [
    "mart_shapiro_feature_dictionary",
    "mart_shapiro_feature_exclusion",
    "shapiromart03_run_log",
]

TARGET_VIEWS = [
    "qsb_v_shapiromart03_feature_dictionary",
    "qsb_v_shapiromart03_first_fingerprint_features",
    "qsb_v_shapiromart03_excluded_features",
    "qsb_v_shapiromart03_fingerprint_readiness",
]

REQUIRED_TABLES = [
    "mart_shapiro_numeric_field_profile",
    "mart_shapiro_numeric_field_review",
    "mart_shapiro_numeric_field_pair_relation",
]

REQUIRED_VIEWS = [
    "qsb_v_shapiromart02_numeric_field_profiles",
    "qsb_v_shapiromart02_candidate_roles",
    "qsb_v_shapiromart02_first_fingerprint_readiness",
]

SHAPIROMART01_TABLES = [
    "mart_shapiro_observation_context",
    "mart_shapiro_feature_availability",
    "mart_shapiro_comparison_cohort",
    "mart_shapiro_control_gap",
    "shapiromart01_run_log",
]

SHAPIROMART02_TABLES = [
    "mart_shapiro_numeric_field_profile",
    "mart_shapiro_numeric_field_pair_relation",
    "mart_shapiro_numeric_field_review",
    "shapiromart02_run_log",
]

OPEN_COMPOUND_LABELS = ["Rcvr_800_GUPPI", "Rcvr1_2_GUPPI"]

APPROVED_REVIEW_PLAN = [
    {
        "token_position": "tim_token_002",
        "reviewed_feature_name": "coordinate_primary_candidate",
        "provisional_role": "sequence_or_coordinate_candidate",
        "fingerprint_role_order": 1,
        "weighting_allowed": 0,
        "direct_interpretation_allowed": 0,
        "limitation": "Provisional coordinate/index role only; no final physical meaning assigned.",
    },
    {
        "token_position": "tim_token_003",
        "reviewed_feature_name": "coordinate_secondary_candidate",
        "provisional_role": "sequence_or_coordinate_candidate",
        "fingerprint_role_order": 2,
        "weighting_allowed": 0,
        "direct_interpretation_allowed": 0,
        "limitation": "Provisional coordinate/index role only; no final physical meaning assigned.",
    },
    {
        "token_position": "tim_token_029",
        "reviewed_feature_name": "signal_value_primary_candidate",
        "provisional_role": "primary_numeric_signal_candidate",
        "fingerprint_role_order": 3,
        "weighting_allowed": 0,
        "direct_interpretation_allowed": 0,
        "limitation": "Provisional structural signal role only; no direct interpretation allowed.",
    },
    {
        "token_position": "tim_token_033",
        "reviewed_feature_name": "signal_value_secondary_candidate",
        "provisional_role": "secondary_numeric_signal_candidate",
        "fingerprint_role_order": 4,
        "weighting_allowed": 0,
        "direct_interpretation_allowed": 0,
        "limitation": "Provisional structural signal role only; no direct interpretation allowed.",
    },
    {
        "token_position": "tim_token_004",
        "reviewed_feature_name": "uncertainty_or_weight_primary_candidate",
        "provisional_role": "uncertainty_or_weight_candidate",
        "fingerprint_role_order": 5,
        "weighting_allowed": 0,
        "direct_interpretation_allowed": 0,
        "limitation": "May not be used as a numerical weight until its direction and scaling are reviewed.",
    },
    {
        "token_position": "tim_token_031",
        "reviewed_feature_name": "uncertainty_or_weight_secondary_candidate",
        "provisional_role": "uncertainty_or_weight_candidate",
        "fingerprint_role_order": 6,
        "weighting_allowed": 0,
        "direct_interpretation_allowed": 0,
        "limitation": "Auxiliary only; may not be applied numerically as a weight.",
    },
    {
        "token_position": "tim_token_035",
        "reviewed_feature_name": "uncertainty_or_weight_tertiary_candidate",
        "provisional_role": "uncertainty_or_weight_candidate",
        "fingerprint_role_order": 7,
        "weighting_allowed": 0,
        "direct_interpretation_allowed": 0,
        "limitation": "Auxiliary only; may not be applied numerically as a weight.",
    },
]

EXCLUSION_REVIEW_PLAN = [
    {
        "token_position": "tim_token_015",
        "structural_class": "configuration_parameter_candidate",
        "exclusion_reason": "Configuration-like behavior; excluded from first fingerprint feature vector.",
        "possible_future_use": "context control or stratification field",
    },
    {
        "token_position": "tim_token_019",
        "structural_class": "processing_or_control_candidate",
        "exclusion_reason": "Processing/control-like behavior; excluded from first fingerprint feature vector.",
        "possible_future_use": "processing-context control field",
    },
]

UNWEIGHTED_FIRST_FINGERPRINT_TOKENS = [
    "tim_token_002",
    "tim_token_003",
    "tim_token_029",
    "tim_token_033",
]

AUXILIARY_ONLY_TOKENS = [
    "tim_token_004",
    "tim_token_031",
    "tim_token_035",
]

CLAIM_BOUNDARY = (
    "SHAPIROMART03 creates a reviewed provisional feature dictionary only. It "
    "does not assign final physical meaning, apply uncertainty candidates as "
    "weights, compute timing/model/result quantities, promote compound labels, "
    "or make Bridge, Shapiro, or interpretive claims."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def connect_writable(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=rw", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def fetch_dicts(
    con: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql, params).fetchall()]


def object_exists(con: sqlite3.Connection, name: str, object_type: str | None = None) -> bool:
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


def table_count(con: sqlite3.Connection, table_name: str) -> int:
    row = con.execute(
        f"SELECT COUNT(*) AS n FROM {quote_identifier(table_name)}"
    ).fetchone()
    return int(row["n"])


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


def fail(message: str) -> None:
    raise RuntimeError(message)


def stable_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    existing_outputs = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing_outputs and not args.overwrite:
        fail(
            "SHAPIROMART03 output files already exist. Use --overwrite to replace: "
            + "; ".join(existing_outputs)
        )


def validate_required_objects(con: sqlite3.Connection) -> None:
    missing: list[str] = []
    for table in REQUIRED_TABLES:
        if not object_exists(con, table, "table"):
            missing.append(f"table:{table}")
    for view in REQUIRED_VIEWS:
        if not object_exists(con, view, "view"):
            missing.append(f"view:{view}")
    if missing:
        fail("Missing required SHAPIROMART02 inputs: " + "; ".join(missing))


def validate_existing_target_state(con: sqlite3.Connection, allow_existing: bool) -> dict[str, Any]:
    target_state: list[dict[str, Any]] = []
    populated: list[str] = []
    for table in TARGET_TABLES:
        if object_exists(con, table, "table"):
            count = table_count(con, table)
            target_state.append({"table": table, "exists": True, "row_count": count})
            if count > 0:
                populated.append(f"{table}:{count}")
        else:
            target_state.append({"table": table, "exists": False, "row_count": 0})
    if populated and not allow_existing:
        fail(
            "SHAPIROMART03 tables already contain rows. Use --allow-existing "
            "for an explicit rerun: " + "; ".join(populated)
        )
    return {"target_tables": target_state}


def table_counts(con: sqlite3.Connection, tables: list[str]) -> dict[str, int]:
    return {table: table_count(con, table) for table in tables}


def mapping_separation_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(
        fetch_dicts(
            con,
            """
            SELECT 'supported' AS separation_class, term, token_position,
                   dwh14a_decision_status, new_mapping_status, new_review_status
            FROM qsb_v_dwh15a_supported_review_ready_candidates
            WHERE term IN ('GUPPI', 'Rcvr_800', 'Rcvr1_2',
                           'Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
            ORDER BY separation_class, term, token_position
            """,
        )
    )
    rows.extend(
        fetch_dicts(
            con,
            """
            SELECT 'open_or_deferred' AS separation_class, term, token_position,
                   dwh14a_decision_status, skip_reason AS new_mapping_status,
                   notes AS new_review_status
            FROM qsb_v_dwh15a_skipped_deferred_candidates
            WHERE term IN ('GUPPI', 'Rcvr_800', 'Rcvr1_2',
                           'Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
            ORDER BY separation_class, term, token_position
            """,
        )
    )
    return sorted(rows, key=lambda row: (row["separation_class"], row["term"], row["token_position"]))


def load_sm02_roles(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT
            token_position,
            source_field,
            proposed_structural_class,
            approved_for_first_fingerprint,
            approved_role,
            review_status,
            required_followup,
            context_a_count,
            context_b_count
        FROM qsb_v_shapiromart02_candidate_roles
        ORDER BY numeric_field_review_id
        """,
    )
    if len(rows) != 9:
        fail(f"Expected exactly 9 SHAPIROMART02 role rows, found {len(rows)}.")
    return {str(row["token_position"]): row for row in rows}


def validate_scope(role_by_token: dict[str, dict[str, Any]]) -> None:
    expected_tokens = {
        row["token_position"] for row in APPROVED_REVIEW_PLAN
    }.union({row["token_position"] for row in EXCLUSION_REVIEW_PLAN})
    actual_tokens = set(role_by_token)
    if expected_tokens != actual_tokens:
        fail(
            "SHAPIROMART03 token scope mismatch. expected="
            + ",".join(sorted(expected_tokens))
            + " actual="
            + ",".join(sorted(actual_tokens))
        )
    for plan in APPROVED_REVIEW_PLAN:
        row = role_by_token[plan["token_position"]]
        if int(row["approved_for_first_fingerprint"]) != 1:
            fail(f"Approved plan token is not approved in SHAPIROMART02: {plan['token_position']}")
        if int(row["context_a_count"]) <= 0 or int(row["context_b_count"]) <= 0:
            fail(f"Approved token lacks both-context availability: {plan['token_position']}")
    for plan in EXCLUSION_REVIEW_PLAN:
        row = role_by_token[plan["token_position"]]
        if int(row["approved_for_first_fingerprint"]) != 0:
            fail(f"Excluded plan token is approved in SHAPIROMART02: {plan['token_position']}")
        if str(row["proposed_structural_class"]) != plan["structural_class"]:
            fail(f"Excluded token class mismatch: {plan['token_position']}")


def build_dictionary_rows(
    role_by_token: dict[str, dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, plan in enumerate(APPROVED_REVIEW_PLAN, start=1):
        source = role_by_token[plan["token_position"]]
        rows.append(
            {
                "feature_dictionary_id": f"SHAPIROMART03_DICT_{index:03d}",
                "source_field": source["source_field"],
                "token_position": plan["token_position"],
                "reviewed_feature_name": plan["reviewed_feature_name"],
                "provisional_role": plan["provisional_role"],
                "structural_class": source["proposed_structural_class"],
                "approved_for_first_fingerprint": 1,
                "fingerprint_role_order": plan["fingerprint_role_order"],
                "context_a_available": 1 if int(source["context_a_count"]) > 0 else 0,
                "context_b_available": 1 if int(source["context_b_count"]) > 0 else 0,
                "weighting_allowed": plan["weighting_allowed"],
                "direct_interpretation_allowed": plan["direct_interpretation_allowed"],
                "review_status": "reviewed_provisional_role",
                "limitation": plan["limitation"],
                "created_at_utc": created_at,
                "notes": (
                    f"SHAPIROMART02 class={source['proposed_structural_class']}; "
                    f"SHAPIROMART02 role={source['approved_role']}; "
                    "provisional structural dictionary row only."
                ),
            }
        )
    return rows


def build_exclusion_rows(
    role_by_token: dict[str, dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, plan in enumerate(EXCLUSION_REVIEW_PLAN, start=1):
        source = role_by_token[plan["token_position"]]
        rows.append(
            {
                "feature_exclusion_id": f"SHAPIROMART03_EXCL_{index:03d}",
                "source_field": source["source_field"],
                "token_position": plan["token_position"],
                "structural_class": plan["structural_class"],
                "exclusion_reason": plan["exclusion_reason"],
                "excluded_from_first_fingerprint": 1,
                "possible_future_use": plan["possible_future_use"],
                "review_status": "reviewed_exclusion_for_first_fingerprint",
                "created_at_utc": created_at,
                "notes": (
                    f"SHAPIROMART02 review_status={source['review_status']}; "
                    "excluded from first fingerprint feature vector."
                ),
            }
        )
    return rows


def build_readiness_rows(
    dictionary_rows: list[dict[str, Any]],
    exclusion_rows: list[dict[str, Any]],
) -> list[dict[str, str]]:
    unweighted_tokens = [
        row["token_position"]
        for row in dictionary_rows
        if row["token_position"] in UNWEIGHTED_FIRST_FINGERPRINT_TOKENS
    ]
    auxiliary_tokens = [
        row["token_position"]
        for row in dictionary_rows
        if row["token_position"] in AUXILIARY_ONLY_TOKENS
    ]
    weight_application_count = sum(int(row["weighting_allowed"]) for row in dictionary_rows)
    direct_interpretation_count = sum(int(row["direct_interpretation_allowed"]) for row in dictionary_rows)
    accounted = len(dictionary_rows) + len(exclusion_rows)
    readiness = (
        "ready_for_first_unweighted_structural_fingerprint_build"
        if len(dictionary_rows) == 7
        and len(exclusion_rows) == 2
        and len(unweighted_tokens) == 4
        and len(auxiliary_tokens) == 3
        and weight_application_count == 0
        and direct_interpretation_count == 0
        else "blocked_dictionary_validation_mismatch"
    )
    return [
        {
            "readiness_metric": "approved_dictionary_rows",
            "metric_value": str(len(dictionary_rows)),
            "readiness_status": readiness,
            "notes": "Expected exactly 7 reviewed provisional dictionary rows.",
        },
        {
            "readiness_metric": "excluded_rows",
            "metric_value": str(len(exclusion_rows)),
            "readiness_status": readiness,
            "notes": "Expected exactly 2 reviewed exclusion rows.",
        },
        {
            "readiness_metric": "source_fields_accounted_for",
            "metric_value": str(accounted),
            "readiness_status": readiness,
            "notes": "Expected exactly 9 SHAPIROMART02 source fields accounted for.",
        },
        {
            "readiness_metric": "first_unweighted_feature_order",
            "metric_value": ",".join(UNWEIGHTED_FIRST_FINGERPRINT_TOKENS),
            "readiness_status": readiness,
            "notes": "Use these fields for the first unweighted structural fingerprint table.",
        },
        {
            "readiness_metric": "auxiliary_uncertainty_weight_candidates",
            "metric_value": ",".join(AUXILIARY_ONLY_TOKENS),
            "readiness_status": readiness,
            "notes": "Carry as auxiliary fields only; do not apply as numerical weights.",
        },
        {
            "readiness_metric": "weighting_allowed_count",
            "metric_value": str(weight_application_count),
            "readiness_status": readiness,
            "notes": "Must remain 0 for SHAPIROMART03.",
        },
        {
            "readiness_metric": "direct_interpretation_allowed_count",
            "metric_value": str(direct_interpretation_count),
            "readiness_status": readiness,
            "notes": "Must remain 0 for SHAPIROMART03.",
        },
    ]


def build_next_step_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "SHAPIROMART04_RECOMMENDED_001",
            "recommended_next_step": (
                "Build a first unweighted structural fingerprint table using "
                "tim_token_002, tim_token_003, tim_token_029, and tim_token_033; "
                "carry tim_token_004, tim_token_031, and tim_token_035 as "
                "auxiliary uncertainty/weight candidates only."
            ),
            "why_this_step": (
                "The reviewed dictionary now fixes the minimal feature order and "
                "keeps weighting and direct interpretation disabled."
            ),
            "db_write_expected": "yes_in_separate_explicit_task",
            "claim_boundary": "The next build remains structural and unweighted.",
        }
    ]


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS mart_shapiro_feature_dictionary (
            feature_dictionary_id TEXT PRIMARY KEY,
            source_field TEXT NOT NULL,
            token_position TEXT NOT NULL,
            reviewed_feature_name TEXT NOT NULL,
            provisional_role TEXT NOT NULL,
            structural_class TEXT NOT NULL,
            approved_for_first_fingerprint INTEGER NOT NULL,
            fingerprint_role_order INTEGER,
            context_a_available INTEGER NOT NULL,
            context_b_available INTEGER NOT NULL,
            weighting_allowed INTEGER NOT NULL,
            direct_interpretation_allowed INTEGER NOT NULL,
            review_status TEXT NOT NULL,
            limitation TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_feature_exclusion (
            feature_exclusion_id TEXT PRIMARY KEY,
            source_field TEXT NOT NULL,
            token_position TEXT NOT NULL,
            structural_class TEXT NOT NULL,
            exclusion_reason TEXT NOT NULL,
            excluded_from_first_fingerprint INTEGER NOT NULL,
            possible_future_use TEXT,
            review_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS shapiromart03_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            approved_feature_count INTEGER,
            excluded_feature_count INTEGER,
            unresolved_feature_count INTEGER,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT
        );
        """
    )


def clear_target_tables(con: sqlite3.Connection) -> None:
    for table in reversed(TARGET_TABLES):
        if object_exists(con, table, "table"):
            con.execute(f"DELETE FROM {quote_identifier(table)}")


def insert_rows(con: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    columns = ", ".join(quote_identifier(field) for field in fieldnames)
    placeholders = ", ".join("?" for _ in fieldnames)
    con.executemany(
        f"INSERT INTO {quote_identifier(table)} ({columns}) VALUES ({placeholders})",
        [tuple(row[field] for field in fieldnames) for row in rows],
    )


def create_views(con: sqlite3.Connection) -> None:
    for view in TARGET_VIEWS:
        con.execute(f"DROP VIEW IF EXISTS {quote_identifier(view)}")
    con.executescript(
        """
        CREATE VIEW qsb_v_shapiromart03_feature_dictionary AS
        SELECT *
        FROM mart_shapiro_feature_dictionary
        ORDER BY fingerprint_role_order, token_position;

        CREATE VIEW qsb_v_shapiromart03_first_fingerprint_features AS
        SELECT
            feature_dictionary_id,
            token_position,
            source_field,
            reviewed_feature_name,
            provisional_role,
            fingerprint_role_order,
            CASE
              WHEN token_position IN ('tim_token_002', 'tim_token_003',
                                      'tim_token_029', 'tim_token_033')
              THEN 'first_unweighted_feature'
              ELSE 'auxiliary_only_not_weighted'
            END AS first_fingerprint_use,
            weighting_allowed,
            direct_interpretation_allowed,
            limitation
        FROM mart_shapiro_feature_dictionary
        WHERE approved_for_first_fingerprint = 1
        ORDER BY fingerprint_role_order;

        CREATE VIEW qsb_v_shapiromart03_excluded_features AS
        SELECT *
        FROM mart_shapiro_feature_exclusion
        ORDER BY token_position;

        CREATE VIEW qsb_v_shapiromart03_fingerprint_readiness AS
        SELECT 'approved_dictionary_rows' AS readiness_metric,
               CAST(COUNT(*) AS TEXT) AS metric_value,
               CASE WHEN COUNT(*) = 7 THEN 'pass' ELSE 'fail' END AS readiness_status,
               'Expected exactly 7 dictionary rows.' AS notes
        FROM mart_shapiro_feature_dictionary
        UNION ALL
        SELECT 'excluded_rows',
               CAST(COUNT(*) AS TEXT),
               CASE WHEN COUNT(*) = 2 THEN 'pass' ELSE 'fail' END,
               'Expected exactly 2 exclusion rows.'
        FROM mart_shapiro_feature_exclusion
        UNION ALL
        SELECT 'source_fields_accounted_for',
               CAST((
                   SELECT COUNT(DISTINCT source_field)
                   FROM (
                     SELECT source_field FROM mart_shapiro_feature_dictionary
                     UNION ALL
                     SELECT source_field FROM mart_shapiro_feature_exclusion
                   )
               ) AS TEXT),
               CASE WHEN (
                   SELECT COUNT(DISTINCT source_field)
                   FROM (
                     SELECT source_field FROM mart_shapiro_feature_dictionary
                     UNION ALL
                     SELECT source_field FROM mart_shapiro_feature_exclusion
                   )
               ) = 9 THEN 'pass' ELSE 'fail' END,
               'Expected exactly 9 accounted SHAPIROMART02 source fields.'
        UNION ALL
        SELECT 'first_unweighted_feature_order',
               GROUP_CONCAT(token_position, ','),
               CASE WHEN GROUP_CONCAT(token_position, ',') =
                         'tim_token_002,tim_token_003,tim_token_029,tim_token_033'
                    THEN 'pass' ELSE 'fail' END,
               'Fields for the first unweighted structural fingerprint table.'
        FROM (
          SELECT token_position
          FROM mart_shapiro_feature_dictionary
          WHERE token_position IN ('tim_token_002', 'tim_token_003',
                                   'tim_token_029', 'tim_token_033')
          ORDER BY fingerprint_role_order
        )
        UNION ALL
        SELECT 'auxiliary_uncertainty_weight_candidates',
               GROUP_CONCAT(token_position, ','),
               CASE WHEN GROUP_CONCAT(token_position, ',') =
                         'tim_token_004,tim_token_031,tim_token_035'
                    THEN 'pass' ELSE 'fail' END,
               'Carried only as auxiliary fields; not applied as weights.'
        FROM (
          SELECT token_position
          FROM mart_shapiro_feature_dictionary
          WHERE token_position IN ('tim_token_004', 'tim_token_031',
                                   'tim_token_035')
          ORDER BY fingerprint_role_order
        )
        UNION ALL
        SELECT 'weighting_allowed_count',
               CAST(SUM(weighting_allowed) AS TEXT),
               CASE WHEN SUM(weighting_allowed) = 0 THEN 'pass' ELSE 'fail' END,
               'No uncertainty/weight candidate may be applied numerically here.'
        FROM mart_shapiro_feature_dictionary
        UNION ALL
        SELECT 'direct_interpretation_allowed_count',
               CAST(SUM(direct_interpretation_allowed) AS TEXT),
               CASE WHEN SUM(direct_interpretation_allowed) = 0 THEN 'pass' ELSE 'fail' END,
               'No direct interpretation is allowed by this dictionary.'
        FROM mart_shapiro_feature_dictionary;
        """
    )


def query_rows(con: sqlite3.Connection, table_or_view: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(table_or_view)} ORDER BY 1")


def validate_new_objects(con: sqlite3.Connection) -> dict[str, Any]:
    missing: list[str] = []
    table_counts_result: dict[str, int] = {}
    view_counts: dict[str, int] = {}
    for table in TARGET_TABLES:
        if not object_exists(con, table, "table"):
            missing.append(f"table:{table}")
        else:
            table_counts_result[table] = table_count(con, table)
    for view in TARGET_VIEWS:
        if not object_exists(con, view, "view"):
            missing.append(f"view:{view}")
        else:
            view_counts[view] = table_count(con, view)
    if missing:
        fail("Missing SHAPIROMART03 objects: " + "; ".join(missing))
    return {"table_counts": table_counts_result, "view_counts": view_counts}


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def write_readout(
    path: Path,
    summary: dict[str, Any],
    dictionary_rows: list[dict[str, Any]],
    exclusion_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    next_step_rows: list[dict[str, str]],
) -> None:
    first_order = [
        row["token_position"]
        for row in dictionary_rows
        if row["token_position"] in UNWEIGHTED_FIRST_FINGERPRINT_TOKENS
    ]
    auxiliary = [
        row["token_position"]
        for row in dictionary_rows
        if row["token_position"] in AUXILIARY_ONLY_TOKENS
    ]
    readiness_summary = "; ".join(
        f"{row['readiness_metric']}={row['metric_value']}:{row['readiness_status']}"
        for row in readiness_rows
    )
    lines = [
        "# QSB-SHAPIROMART03 Reviewed Minimal Feature Dictionary",
        "",
        "## 1. Executive summary",
        "",
        (
            "Befund: SHAPIROMART03 created a compact reviewed provisional feature "
            "dictionary for the first structural fingerprint step."
        ),
        "",
        f"- Approved dictionary rows: {len(dictionary_rows)}",
        f"- Excluded feature rows: {len(exclusion_rows)}",
        f"- Accounted source fields: {len(dictionary_rows) + len(exclusion_rows)}",
        f"- First unweighted field order: {', '.join(first_order)}",
        f"- Auxiliary uncertainty/weight candidates: {', '.join(auxiliary)}",
        "",
        "## 2. Approved fields and reviewed provisional roles",
        "",
    ]
    for row in dictionary_rows:
        lines.append(
            "- {token_position}: name={reviewed_feature_name}; role={provisional_role}; "
            "order={fingerprint_role_order}; weighting_allowed={weighting_allowed}; "
            "direct_interpretation_allowed={direct_interpretation_allowed}".format(**row)
        )
    lines.extend(
        [
            "",
            "## 3. Excluded fields",
            "",
        ]
    )
    for row in exclusion_rows:
        lines.append(
            "- {token_position}: class={structural_class}; reason={exclusion_reason}; "
            "future_use={possible_future_use}".format(**row)
        )
    lines.extend(
        [
            "",
            "## 4. Uncertainty/weight usability",
            "",
            (
                "The uncertainty/weight candidates are included in the dictionary "
                "as auxiliary fields only. They are not numerically usable as "
                "weights in SHAPIROMART03."
            ),
            "",
            "## 5. Exact minimal first fingerprint field order",
            "",
            ", ".join(first_order),
            "",
            "Carry only as auxiliary fields, without applying weights:",
            "",
            ", ".join(auxiliary),
            "",
            "## 6. What remains blocked",
            "",
            (
                "A first fingerprint table is not yet built. Weighting, direct "
                "interpretation, and any physical role remain blocked pending a "
                "separate explicit build/review step."
            ),
            "",
            "## 7. Single next concrete step",
            "",
            next_step_rows[0]["recommended_next_step"],
            "",
            "## 8. Validation and claim boundary",
            "",
            f"- Live DB unchanged: {summary['validation']['live_db_unchanged']}",
            f"- Workcopy DB modified: {summary['validation']['workcopy_db_modified']}",
            f"- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}",
            f"- Workcopy foreign-key violations: {summary['validation']['workcopy_foreign_key_violation_count']}",
            f"- SHAPIROMART01 counts preserved: {summary['validation']['shapiromart01_counts_preserved']}",
            f"- SHAPIROMART02 counts preserved: {summary['validation']['shapiromart02_counts_preserved']}",
            f"- Compound labels not promoted: {summary['validation']['compound_labels_not_promoted']}",
            f"- Readiness summary: {readiness_summary}",
            "",
            CLAIM_BOUNDARY,
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(
    output_root: Path,
    summary: dict[str, Any],
    dictionary_rows: list[dict[str, Any]],
    exclusion_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    next_step_rows: list[dict[str, str]],
) -> None:
    paths = output_paths(output_root)
    write_csv(
        paths[DICTIONARY_CSV],
        dictionary_rows,
        [
            "feature_dictionary_id",
            "source_field",
            "token_position",
            "reviewed_feature_name",
            "provisional_role",
            "structural_class",
            "approved_for_first_fingerprint",
            "fingerprint_role_order",
            "context_a_available",
            "context_b_available",
            "weighting_allowed",
            "direct_interpretation_allowed",
            "review_status",
            "limitation",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[EXCLUSION_CSV],
        exclusion_rows,
        [
            "feature_exclusion_id",
            "source_field",
            "token_position",
            "structural_class",
            "exclusion_reason",
            "excluded_from_first_fingerprint",
            "possible_future_use",
            "review_status",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[READINESS_CSV],
        readiness_rows,
        ["readiness_metric", "metric_value", "readiness_status", "notes"],
    )
    write_csv(
        paths[NEXT_STEP_CSV],
        next_step_rows,
        [
            "next_step_id",
            "recommended_next_step",
            "why_this_step",
            "db_write_expected",
            "claim_boundary",
        ],
    )
    write_json(paths[SUMMARY_JSON], summary)
    write_readout(paths[READOUT_MD], summary, dictionary_rows, exclusion_rows, readiness_rows, next_step_rows)


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)

    with connect_readonly(args.live_db) as live_con:
        live_integrity = integrity_check(live_con)
        live_fk = foreign_key_violations(live_con)
        if live_integrity != "ok":
            fail(f"Live DB integrity_check failed: {live_integrity}")
        if live_fk:
            fail(f"Live DB foreign-key violations: {len(live_fk)}")

    created_at = utc_now()
    run_id = "SHAPIROMART03_RUN_001"

    with connect_writable(args.workcopy_db) as con:
        validate_required_objects(con)
        existing_target_state = validate_existing_target_state(con, args.allow_existing)
        pre_integrity = integrity_check(con)
        pre_fk = foreign_key_violations(con)
        if pre_integrity != "ok":
            fail(f"Workcopy DB integrity_check failed before run: {pre_integrity}")
        if pre_fk:
            fail(f"Workcopy DB foreign-key violations before run: {len(pre_fk)}")

        before_sm01_counts = table_counts(con, SHAPIROMART01_TABLES)
        before_sm02_counts = table_counts(con, SHAPIROMART02_TABLES)
        before_mapping_digest = stable_digest(mapping_separation_rows(con))

        role_by_token = load_sm02_roles(con)
        validate_scope(role_by_token)
        dictionary_rows = build_dictionary_rows(role_by_token, created_at)
        exclusion_rows = build_exclusion_rows(role_by_token, created_at)
        readiness_rows = build_readiness_rows(dictionary_rows, exclusion_rows)
        next_step_rows = build_next_step_rows()

        if len(dictionary_rows) != 7:
            fail(f"Expected 7 dictionary rows, built {len(dictionary_rows)}.")
        if len(exclusion_rows) != 2:
            fail(f"Expected 2 exclusion rows, built {len(exclusion_rows)}.")
        accounted_fields = {
            row["source_field"] for row in dictionary_rows
        }.union({row["source_field"] for row in exclusion_rows})
        source_scope = {row["source_field"] for row in role_by_token.values()}
        if accounted_fields != source_scope:
            fail("Not all SHAPIROMART02 source fields are accounted for exactly.")
        if any(int(row["weighting_allowed"]) != 0 for row in dictionary_rows):
            fail("A weighting_allowed flag is nonzero.")
        if any(int(row["direct_interpretation_allowed"]) != 0 for row in dictionary_rows):
            fail("A direct_interpretation_allowed flag is nonzero.")

        try:
            con.execute("BEGIN")
            create_tables(con)
            if args.allow_existing:
                clear_target_tables(con)
            insert_rows(con, "mart_shapiro_feature_dictionary", dictionary_rows)
            insert_rows(con, "mart_shapiro_feature_exclusion", exclusion_rows)
            insert_rows(
                con,
                "shapiromart03_run_log",
                [
                    {
                        "run_id": run_id,
                        "run_timestamp_utc": created_at,
                        "approved_feature_count": len(dictionary_rows),
                        "excluded_feature_count": len(exclusion_rows),
                        "unresolved_feature_count": 0,
                        "live_db_modified": 0,
                        "workcopy_db_modified": 1,
                        "integrity_check_result": "pending_post_commit_validation",
                        "foreign_key_violation_count": -1,
                        "notes": CLAIM_BOUNDARY,
                    }
                ],
            )
            create_views(con)
            con.commit()
        except Exception:
            con.rollback()
            raise

        post_integrity = integrity_check(con)
        post_fk = foreign_key_violations(con)
        if post_integrity != "ok":
            fail(f"Workcopy DB integrity_check failed after run: {post_integrity}")
        if post_fk:
            fail(f"Workcopy DB foreign-key violations after run: {len(post_fk)}")
        con.execute(
            """
            UPDATE shapiromart03_run_log
            SET integrity_check_result = ?,
                foreign_key_violation_count = ?
            WHERE run_id = ?
            """,
            (post_integrity, len(post_fk), run_id),
        )
        con.commit()

        new_object_validation = validate_new_objects(con)
        db_dictionary_rows = query_rows(con, "mart_shapiro_feature_dictionary")
        db_exclusion_rows = query_rows(con, "mart_shapiro_feature_exclusion")
        db_readiness_rows = query_rows(con, "qsb_v_shapiromart03_fingerprint_readiness")
        db_run_log_rows = query_rows(con, "shapiromart03_run_log")

        after_sm01_counts = table_counts(con, SHAPIROMART01_TABLES)
        after_sm02_counts = table_counts(con, SHAPIROMART02_TABLES)
        after_mapping_rows = mapping_separation_rows(con)
        after_mapping_digest = stable_digest(after_mapping_rows)
        supported_terms_after = {
            str(row["term"])
            for row in after_mapping_rows
            if row["separation_class"] == "supported"
        }

    live_after = db_state(args.live_db)
    workcopy_after = db_state(args.workcopy_db)
    live_unchanged = live_before == live_after
    workcopy_modified = workcopy_before != workcopy_after
    if not live_unchanged:
        fail("Live DB checksum/stat changed during SHAPIROMART03.")
    if not workcopy_modified:
        fail("Workcopy DB was not modified; expected SHAPIROMART03 rows/objects.")

    sm01_preserved = before_sm01_counts == after_sm01_counts
    sm02_preserved = before_sm02_counts == after_sm02_counts
    mapping_preserved = before_mapping_digest == after_mapping_digest
    compound_not_promoted = not any(label in supported_terms_after for label in OPEN_COMPOUND_LABELS)
    if not sm01_preserved:
        fail("SHAPIROMART01 counts changed.")
    if not sm02_preserved:
        fail("SHAPIROMART02 counts changed.")
    if not mapping_preserved:
        fail("Supported/open mapping separation changed.")
    if not compound_not_promoted:
        fail("Compound label appeared in supported mapping terms.")

    summary: dict[str, Any] = {
        "script_name": SCRIPT_NAME,
        "task": "QSB-SHAPIROMART03",
        "paths": {
            "live_db": str(args.live_db),
            "workcopy_db": str(args.workcopy_db),
            "output_root": str(args.output_root),
        },
        "counts": {
            "approved_feature_count": len(db_dictionary_rows),
            "excluded_feature_count": len(db_exclusion_rows),
            "unresolved_feature_count": 0,
            "source_fields_accounted_for": len({row["source_field"] for row in db_dictionary_rows + db_exclusion_rows}),
            "first_unweighted_feature_count": len(UNWEIGHTED_FIRST_FINGERPRINT_TOKENS),
            "auxiliary_feature_count": len(AUXILIARY_ONLY_TOKENS),
        },
        "validation": {
            "live_integrity_check": live_integrity,
            "live_foreign_key_violation_count": len(live_fk),
            "live_db_unchanged": live_unchanged,
            "workcopy_db_modified": workcopy_modified,
            "workcopy_integrity_check": post_integrity,
            "workcopy_foreign_key_violation_count": len(post_fk),
            "existing_target_state": existing_target_state,
            "new_objects": new_object_validation,
            "shapiromart01_counts_before": before_sm01_counts,
            "shapiromart01_counts_after": after_sm01_counts,
            "shapiromart01_counts_preserved": sm01_preserved,
            "shapiromart02_counts_before": before_sm02_counts,
            "shapiromart02_counts_after": after_sm02_counts,
            "shapiromart02_counts_preserved": sm02_preserved,
            "mapping_separation_preserved": mapping_preserved,
            "compound_labels_not_promoted": compound_not_promoted,
            "live_db_state_before": live_before,
            "live_db_state_after": live_after,
            "workcopy_db_state_before": workcopy_before,
            "workcopy_db_state_after": workcopy_after,
        },
        "feature_dictionary_rows": db_dictionary_rows,
        "feature_exclusion_rows": db_exclusion_rows,
        "fingerprint_readiness_rows": db_readiness_rows,
        "next_step_rows": next_step_rows,
        "run_log_rows": db_run_log_rows,
        "workcopy_modified_objects": TARGET_TABLES + TARGET_VIEWS,
        "claim_boundary": CLAIM_BOUNDARY,
    }

    write_outputs(
        args.output_root,
        summary,
        db_dictionary_rows,
        db_exclusion_rows,
        db_readiness_rows,
        next_step_rows,
    )
    return {"summary": summary, "output_files": output_paths(args.output_root)}


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create the SHAPIROMART03 reviewed provisional feature dictionary "
            "from SHAPIROMART02 workcopy rows."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing SHAPIROMART03 output files.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow an explicit rerun over existing SHAPIROMART03 target tables.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    summary = result["summary"]
    counts = summary["counts"]
    print("QSB-SHAPIROMART03 reviewed feature dictionary complete.")
    print(f"Approved feature rows: {counts['approved_feature_count']}")
    print(f"Excluded feature rows: {counts['excluded_feature_count']}")
    print(f"Source fields accounted for: {counts['source_fields_accounted_for']}")
    print(f"First unweighted features: {counts['first_unweighted_feature_count']}")
    print(f"Auxiliary fields: {counts['auxiliary_feature_count']}")
    print(f"Live DB unchanged: {summary['validation']['live_db_unchanged']}")
    print(f"Workcopy DB modified: {summary['validation']['workcopy_db_modified']}")
    print(f"Output root: {summary['paths']['output_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
