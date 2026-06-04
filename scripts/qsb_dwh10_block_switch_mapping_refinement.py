#!/usr/bin/env python3
"""QSB-DWH10: controlled refinement for five block-switch tokens.

This script adds a small DWH10 refinement layer to the DWH workcopy database
for exactly five structurally important block-switch tokens. It uses only
existing workcopy DB tables/views as input. The live DB is opened read-only for
protection and validation checks.

It does not read raw TIM/PAR files, does not use report exports as input, does
not touch all raw_field_value rows, does not create bridge/result tables, does
not verify external evidence, and does not assign final controlled or physical
meaning to TIM columns.
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


SCRIPT_NAME = "scripts/qsb_dwh10_block_switch_mapping_refinement.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh10_block_switch_mapping_refinement_readout.md"
SUMMARY_JSON = "dwh10_block_switch_mapping_refinement_summary.json"
TOKEN_REFINEMENT_CSV = "dwh10_block_switch_token_refinement.csv"
VALUE_PAIRS_CSV = "dwh10_block_switch_value_pairs.csv"
REVIEW_ACTIONS_CSV = "dwh10_mapping_review_actions.csv"
NEXT_STEPS_CSV = "dwh10_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    TOKEN_REFINEMENT_CSV,
    VALUE_PAIRS_CSV,
    REVIEW_ACTIONS_CSV,
    NEXT_STEPS_CSV,
]

DWH10_TABLES = [
    "dwh10_block_switch_mapping_refinement",
    "dwh10_block_switch_refinement_run_log",
]

DWH10_VIEWS = [
    "qsb_v_dwh10_block_switch_refinement",
    "qsb_v_dwh10_review_actions",
    "qsb_v_dwh10_next_mapping_questions",
]

DWH05_EXPECTED_COUNTS = {
    "raw_record": 11395,
    "raw_field_value": 471874,
    "core_observation_record_link": 11395,
}

DWH08_EXPECTED_COUNTS = {
    "map_token_dictionary": 91,
    "map_token_value_assertion": 10,
    "map_assertion_evidence": 10,
    "map_review_decision": 52,
    "map_evidence_gap": 54,
}

REQUIRED_DWH08_TABLES = [
    *DWH08_EXPECTED_COUNTS.keys(),
    "dwh08_mapping_evidence_run_log",
]

FOCUS_TOKENS = [
    "tim_token_007",
    "tim_token_011",
    "tim_token_013",
    "tim_token_017",
    "tim_token_023",
]

REFINEMENT_SPECS = {
    "tim_token_007": {
        "proposed_structural_role": "receiver_band_context_candidate",
        "proposed_controlled_field_name": "receiver_context_raw",
        "mapping_confidence": "structural_high_semantic_pending",
        "evidence_need": "external_receiver_or_band_definition_required",
    },
    "tim_token_011": {
        "proposed_structural_role": "receiver_backend_context_candidate",
        "proposed_controlled_field_name": "receiver_backend_context_raw",
        "mapping_confidence": "structural_high_semantic_pending",
        "evidence_need": "external_receiver_backend_definition_required",
    },
    "tim_token_013": {
        "proposed_structural_role": "numeric_observation_configuration_candidate",
        "proposed_controlled_field_name": "observation_config_numeric_013",
        "mapping_confidence": "structural_medium_semantic_pending",
        "evidence_need": "external_data_format_or_observation_config_required",
    },
    "tim_token_017": {
        "proposed_structural_role": "derived_product_or_processing_label_candidate",
        "proposed_controlled_field_name": "product_processing_label_raw",
        "mapping_confidence": "structural_high_semantic_pending",
        "evidence_need": "external_product_label_or_pipeline_context_required",
    },
    "tim_token_023": {
        "proposed_structural_role": "numeric_configuration_state_candidate",
        "proposed_controlled_field_name": "observation_config_numeric_023",
        "mapping_confidence": "structural_medium_semantic_pending",
        "evidence_need": "external_data_format_or_observation_config_required",
    },
}

CLAIM_BOUNDARY = (
    "DWH10 is a workcopy-only controlled mapping-refinement step for exactly "
    "five structurally important block-switch tokens. It records proposed "
    "structural roles, cautious controlled field-name candidates, block A/B "
    "values, evidence needs, and manual review actions. It does not modify the "
    "live DB, does not read raw TIM/PAR files, does not use report exports as "
    "input, does not touch all raw_field_value rows, does not create "
    "bridge/result tables, does not verify external evidence, does not compute "
    "timing/model/statistical quantities, and does not assign final controlled "
    "or physical meaning to TIM columns."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def timestamp_for_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


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
    return {
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def db_state(path: Path) -> dict[str, Any]:
    return {
        "sha256": file_sha256(path),
        "stat": file_stat(path),
    }


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


def ensure_no_outputs(output_root: Path, overwrite: bool) -> None:
    existing = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH10 output file(s): "
            + "; ".join(existing)
        )


def ensure_path_preconditions(live_db: Path, workcopy_db: Path, output_root: Path) -> None:
    if not live_db.exists():
        raise FileNotFoundError(f"Live DB does not exist: {live_db}")
    if not live_db.is_file():
        raise ValueError(f"Live DB path is not a file: {live_db}")
    if not workcopy_db.exists():
        raise FileNotFoundError(f"Workcopy DB does not exist: {workcopy_db}")
    if not workcopy_db.is_file():
        raise ValueError(f"Workcopy DB path is not a file: {workcopy_db}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")


def source_work_packet_name(con: sqlite3.Connection) -> str:
    if object_exists(con, "db27_mapping_work_packet", "table"):
        return "db27_mapping_work_packet"
    if object_exists(con, "qsb_v_db27_first_mapping_work_packet", "view"):
        return "qsb_v_db27_first_mapping_work_packet"
    raise RuntimeError("No DB27 first mapping work-packet source found in workcopy.")


def ensure_preconditions(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
    allow_existing: bool,
) -> dict[str, Any]:
    ensure_path_preconditions(live_db, workcopy_db, output_root)
    ensure_no_outputs(output_root, overwrite)

    with connect_readonly(live_db) as con:
        live_integrity = integrity_check(con)
        live_fk = foreign_key_violations(con)
    if live_integrity != "ok":
        raise RuntimeError(f"Live DB integrity_check failed: {live_integrity}")
    if live_fk:
        raise RuntimeError(f"Live DB foreign_key_check returned {len(live_fk)} row(s).")

    with connect_readonly(workcopy_db) as con:
        work_integrity = integrity_check(con)
        work_fk = foreign_key_violations(con)
        missing_dwh05 = [
            table for table in DWH05_EXPECTED_COUNTS
            if not object_exists(con, table, "table")
        ]
        dwh05_counts = {
            table: table_count(con, table)
            for table in DWH05_EXPECTED_COUNTS
            if object_exists(con, table, "table")
        }
        missing_dwh08 = [
            table for table in REQUIRED_DWH08_TABLES
            if not object_exists(con, table, "table")
        ]
        dwh08_counts = {
            table: table_count(con, table)
            for table in DWH08_EXPECTED_COUNTS
            if object_exists(con, table, "table")
        }
        existing_dwh10 = [
            name for name in [*DWH10_TABLES, *DWH10_VIEWS]
            if object_exists(con, name)
        ]
        existing_dwh10_table_rows = {
            table: table_count(con, table)
            for table in DWH10_TABLES
            if object_exists(con, table, "table")
        }
        work_packet_source = source_work_packet_name(con)

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if missing_dwh05:
        raise RuntimeError("Missing DWH05 raw/core table(s): " + ", ".join(missing_dwh05))
    dwh05_mismatches = [
        f"{table}: expected {expected}, got {dwh05_counts.get(table)}"
        for table, expected in DWH05_EXPECTED_COUNTS.items()
        if dwh05_counts.get(table) != expected
    ]
    if dwh05_mismatches:
        raise RuntimeError("DWH05 raw/core count mismatch: " + "; ".join(dwh05_mismatches))
    if missing_dwh08:
        raise RuntimeError("Missing DWH08 map table(s): " + ", ".join(missing_dwh08))
    dwh08_mismatches = [
        f"{table}: expected {expected}, got {dwh08_counts.get(table)}"
        for table, expected in DWH08_EXPECTED_COUNTS.items()
        if dwh08_counts.get(table) != expected
    ]
    if dwh08_mismatches:
        raise RuntimeError("DWH08 map count mismatch: " + "; ".join(dwh08_mismatches))
    if existing_dwh10 and not allow_existing:
        raise RuntimeError(
            "DWH10 target object(s) already exist; use --allow-existing only "
            "for controlled empty-object continuation: " + ", ".join(existing_dwh10)
        )
    nonempty_existing = [
        f"{table}={count}"
        for table, count in existing_dwh10_table_rows.items()
        if count > 0
    ]
    if nonempty_existing:
        raise RuntimeError(
            "Refusing to append to nonempty DWH10 table(s): "
            + ", ".join(nonempty_existing)
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "dwh05_counts_before": dwh05_counts,
        "dwh08_counts_before": dwh08_counts,
        "work_packet_source": work_packet_source,
    }


def create_tables(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    con.executescript(
        f"""
        CREATE TABLE {clause}dwh10_block_switch_mapping_refinement (
            refinement_id TEXT PRIMARY KEY,
            token_dictionary_id TEXT,
            token_position TEXT NOT NULL,
            block_a_value TEXT,
            block_b_value TEXT,
            proposed_structural_role TEXT NOT NULL,
            proposed_controlled_field_name TEXT,
            mapping_confidence TEXT NOT NULL,
            evidence_need TEXT NOT NULL,
            review_status TEXT NOT NULL,
            source_basis TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}dwh10_block_switch_refinement_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            refined_token_count INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT
        );
        """
    )


def create_views(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    con.executescript(
        f"""
        CREATE VIEW {clause}qsb_v_dwh10_block_switch_refinement AS
        SELECT
            refinement_id,
            token_dictionary_id,
            token_position,
            block_a_value,
            block_b_value,
            proposed_structural_role,
            proposed_controlled_field_name,
            mapping_confidence,
            evidence_need,
            review_status,
            source_basis,
            notes
        FROM dwh10_block_switch_mapping_refinement
        ORDER BY token_position;

        CREATE VIEW {clause}qsb_v_dwh10_review_actions AS
        SELECT
            'dwh10_action_' || substr(token_position, -3) AS action_id,
            token_position,
            CASE evidence_need
                WHEN 'external_receiver_or_band_definition_required'
                THEN 'Verify receiver/band context before any controlled definition promotion.'
                WHEN 'external_receiver_backend_definition_required'
                THEN 'Verify receiver/backend composite context before controlled definition promotion.'
                WHEN 'external_product_label_or_pipeline_context_required'
                THEN 'Verify product label or pipeline context before controlled definition promotion.'
                ELSE 'Verify data-format or observation-configuration evidence before controlled definition promotion.'
            END AS recommended_action,
            CASE mapping_confidence
                WHEN 'structural_high_semantic_pending' THEN 'P1'
                ELSE 'P2'
            END AS priority,
            evidence_need AS depends_on,
            notes
        FROM dwh10_block_switch_mapping_refinement
        ORDER BY
            CASE mapping_confidence
                WHEN 'structural_high_semantic_pending' THEN 1
                ELSE 2
            END,
            token_position;

        CREATE VIEW {clause}qsb_v_dwh10_next_mapping_questions AS
        SELECT
            'dwh10_question_' || substr(token_position, -3) AS question_id,
            token_position,
            'Which external source is sufficient to review ' || proposed_controlled_field_name || '?' AS question_text,
            evidence_need AS required_evidence_class,
            review_status,
            'manual_mapping_review' AS expected_decision_type
        FROM dwh10_block_switch_mapping_refinement
        ORDER BY token_position;
        """
    )


def insert_rows(con: sqlite3.Connection, table_name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    column_sql = ", ".join(quote_identifier(column) for column in columns)
    sql = f"INSERT INTO {quote_identifier(table_name)} ({column_sql}) VALUES ({placeholders})"
    con.executemany(sql, [[row[column] for column in columns] for row in rows])


def load_dictionary_by_token(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    placeholders = ", ".join("?" for _ in FOCUS_TOKENS)
    rows = fetch_dicts(
        con,
        f"""
        SELECT token_position, token_dictionary_id, proposed_structural_name,
               structural_role, mapping_status, review_status
        FROM map_token_dictionary
        WHERE line_family = 'data_line'
          AND token_position IN ({placeholders})
        ORDER BY token_position
        """,
        tuple(FOCUS_TOKENS),
    )
    return {str(row["token_position"]): row for row in rows}


def load_work_packet_by_token(
    con: sqlite3.Connection,
    source_name: str,
) -> dict[str, dict[str, Any]]:
    placeholders = ", ".join("?" for _ in FOCUS_TOKENS)
    rows = fetch_dicts(
        con,
        f"""
        SELECT token_position, block_a_value, block_b_value, relation_type,
               block_a_count, block_b_count, proposed_structural_name,
               review_status
        FROM {quote_identifier(source_name)}
        WHERE token_position IN ({placeholders})
        ORDER BY token_position
        """,
        tuple(FOCUS_TOKENS),
    )
    by_token = {str(row["token_position"]): row for row in rows}
    missing = [token for token in FOCUS_TOKENS if token not in by_token]
    if missing:
        raise RuntimeError("DWH10 source work packet missing token(s): " + ", ".join(missing))
    return by_token


def build_refinement_rows(
    con: sqlite3.Connection,
    work_packet_source: str,
    created_at: str,
) -> list[dict[str, Any]]:
    dictionaries = load_dictionary_by_token(con)
    packets = load_work_packet_by_token(con, work_packet_source)
    rows: list[dict[str, Any]] = []
    for idx, token in enumerate(FOCUS_TOKENS, start=1):
        spec = REFINEMENT_SPECS[token]
        packet = packets[token]
        dictionary = dictionaries.get(token)
        link_status = (
            "map_token_dictionary_linked"
            if dictionary is not None
            else "mapping_dictionary_link_missing"
        )
        rows.append(
            {
                "refinement_id": f"dwh10_block_switch_refinement_{idx:03d}",
                "token_dictionary_id": dictionary["token_dictionary_id"] if dictionary else None,
                "token_position": token,
                "block_a_value": packet["block_a_value"],
                "block_b_value": packet["block_b_value"],
                "proposed_structural_role": spec["proposed_structural_role"],
                "proposed_controlled_field_name": spec["proposed_controlled_field_name"],
                "mapping_confidence": spec["mapping_confidence"],
                "evidence_need": spec["evidence_need"],
                "review_status": "proposed_for_manual_review",
                "source_basis": "DB23B two-block signature plus DWH08 map_token_dictionary",
                "created_at_utc": created_at,
                "notes": (
                    f"{link_status}; source_work_packet={work_packet_source}; "
                    f"relation_type={packet['relation_type']}; "
                    f"block_counts={packet['block_a_count']} vs {packet['block_b_count']}; "
                    "candidate only; semantic verification remains pending"
                ),
            }
        )
    return rows


def insert_run_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    live_modified: bool,
    refined_token_count: int,
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh10_block_switch_refinement_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            refined_token_count,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(live_db),
            str(workcopy_db),
            SCRIPT_NAME,
            "workcopy_block_switch_mapping_refinement",
            1 if live_modified else 0,
            1,
            refined_token_count,
            integrity,
            fk_count,
            "DWH10 added five controlled block-switch refinement candidate rows in the workcopy only.",
        ),
    )


def validate_workcopy(
    con: sqlite3.Connection,
    live_before: dict[str, Any],
    live_after: dict[str, Any],
) -> dict[str, Any]:
    integrity = integrity_check(con)
    fk_violations = foreign_key_violations(con)
    dwh08_counts = {table: table_count(con, table) for table in DWH08_EXPECTED_COUNTS}
    dwh08_preserved = {
        table: {
            "expected": expected,
            "actual": dwh08_counts[table],
            "status": "passed" if dwh08_counts[table] == expected else "failed",
        }
        for table, expected in DWH08_EXPECTED_COUNTS.items()
    }
    dwh10_counts = {table: table_count(con, table) for table in DWH10_TABLES}
    view_counts = {view: table_count(con, view) for view in DWH10_VIEWS if object_exists(con, view, "view")}
    return {
        "workcopy_integrity_check": integrity,
        "workcopy_foreign_key_violations": fk_violations,
        "foreign_key_violation_count": len(fk_violations),
        "dwh08_map_counts": dwh08_preserved,
        "dwh08_preservation_status": (
            "passed"
            if all(item["status"] == "passed" for item in dwh08_preserved.values())
            else "failed"
        ),
        "dwh10_table_counts": dwh10_counts,
        "dwh10_view_counts": view_counts,
        "exactly_five_refinement_rows": dwh10_counts["dwh10_block_switch_mapping_refinement"] == 5,
        "dwh10_views_queryable": len(view_counts) == len(DWH10_VIEWS),
        "live_db_sha256_before": live_before["sha256"],
        "live_db_sha256_after": live_after["sha256"],
        "live_db_stat_before": live_before["stat"],
        "live_db_stat_after": live_after["stat"],
        "live_db_checksum_unchanged": live_before["sha256"] == live_after["sha256"],
        "live_db_stat_unchanged": live_before["stat"] == live_after["stat"],
    }


def query_rows(con: sqlite3.Connection, source_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(source_name)}")


def next_dwh_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH11_A",
            "next_step_name": "External evidence verification for receiver/backend/telescope/product-label terms",
            "prerequisite": "DWH10 candidate rows present and review actions accepted",
            "recommended_action": "Verify receiver/backend/telescope/product-label terms against approved external sources before any controlled definition promotion.",
            "risk_level": "medium",
            "notes": "Recommended first because DWH10 evidence_need values remain unresolved.",
        },
        {
            "next_step_id": "DWH11_B",
            "next_step_name": "DBeaver/ERD visual check of DWH10 refinement rows",
            "prerequisite": "DWH10 tables and views queryable",
            "recommended_action": "Inspect DWH10 rows beside the DWH08 Mapping/Evidence layer.",
            "risk_level": "low",
            "notes": "Useful if the new refinement table should be visually accepted before external verification.",
        },
        {
            "next_step_id": "DWH11_C",
            "next_step_name": "Controlled update of map_token_dictionary review_status after external evidence",
            "prerequisite": "External evidence verification has passed for the relevant token candidate",
            "recommended_action": "Update DWH08 dictionary review status only in a controlled follow-up workcopy step.",
            "risk_level": "medium",
            "notes": "DWH10 intentionally leaves DWH08 rows unchanged.",
        },
        {
            "next_step_id": "DWH11_D",
            "next_step_name": "Shapiro-Mart design only after mapping/evidence refinement has evidence status",
            "prerequisite": "Mapping/evidence candidates have reviewed evidence status",
            "recommended_action": "Defer Shapiro-Mart design until mapping/evidence refinement is evidence-backed.",
            "risk_level": "high",
            "notes": "DWH10 does not perform physics analysis or Bridge/Result modeling.",
        },
    ]


def review_action_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT action_id, token_position, recommended_action, priority, depends_on, notes
        FROM qsb_v_dwh10_review_actions
        ORDER BY priority, token_position
        """,
    )


def value_pair_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            token_position,
            block_a_value,
            block_b_value,
            'different' AS relation_type,
            source_basis,
            notes
        FROM dwh10_block_switch_mapping_refinement
        ORDER BY token_position
        """,
    )


def build_summary(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    preflight: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    refinement_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_dwh10_block_switch_refinement
        ORDER BY token_position
        """,
    )
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH controlled workcopy refinement",
        "data_substrate_used": str(workcopy_db),
        "source_work_packet": preflight["work_packet_source"],
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "raw_tim_par_files_read": False,
        "report_exports_used_as_input": False,
        "new_isolated_analysis_db_created": False,
        "bridge_or_result_tables_created": False,
        "raw_field_value_bulk_touch_performed": False,
        "target_tables_created": DWH10_TABLES,
        "target_views_created": DWH10_VIEWS,
        "refined_token_count": len(refinement_rows),
        "refinement_rows": refinement_rows,
        "value_pairs": value_pair_rows(con),
        "review_actions": review_action_rows(con),
        "next_dwh_steps": next_dwh_steps_rows(),
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
            "dwh05_counts_before": preflight["dwh05_counts_before"],
            "dwh08_counts_before": preflight["dwh08_counts_before"],
        },
        "validation": validation,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def format_refinement_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        "- {token_position}: {proposed_structural_role}; {block_a_value} -> {block_b_value}; evidence_need={evidence_need}".format(**row)
        for row in rows
    )


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    live_status = (
        "unchanged"
        if summary["validation"]["live_db_checksum_unchanged"]
        and summary["validation"]["live_db_stat_unchanged"]
        else "changed"
    )
    dwh08_failed = [
        table for table, item in summary["validation"]["dwh08_map_counts"].items()
        if item["status"] != "passed"
    ]
    value_pair_lines = "\n".join(
        "- {token_position}: {block_a_value} -> {block_b_value}".format(**row)
        for row in summary["value_pairs"]
    )
    role_lines = "\n".join(
        "- {token_position}: {proposed_structural_role}; proposed field={proposed_controlled_field_name}; confidence={mapping_confidence}".format(**row)
        for row in summary["refinement_rows"]
    )
    evidence_lines = "\n".join(
        "- {token_position}: {evidence_need}".format(**row)
        for row in summary["refinement_rows"]
    )
    action_lines = "\n".join(
        "- {action_id}: {token_position}; {recommended_action}; priority={priority}".format(**row)
        for row in summary["review_actions"]
    )
    next_lines = "\n".join(
        "- {next_step_id}: {next_step_name}".format(**row)
        for row in summary["next_dwh_steps"]
    )
    content = f"""# QSB-DWH10 Block-Switch Mapping Refinement Readout

## 1. Executive summary

Befund: DWH10 added a small workcopy-only refinement table for exactly five block-switch token candidates.

- Run ID: `{summary['run_id']}`
- Workcopy DB: `{summary['workcopy_db_path']}`
- Source work-packet object: `{summary['source_work_packet']}`
- Refined token count: {summary['refined_token_count']}
- DWH08 preservation: {summary['validation']['dwh08_preservation_status']}

## 2. Workcopy-only principle

All DWH10 DB writes were limited to `{summary['workcopy_db_path']}`. Existing DWH08 map_* rows were preserved unchanged; DWH10 rows were added beside them.

## 3. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH10: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH10: {live_status}

## 4. Five block-switch tokens refined

{format_refinement_lines(summary['refinement_rows'])}

## 5. Block A/B value pairs

{value_pair_lines}

## 6. Proposed structural roles

{role_lines}

## 7. Evidence needs

{evidence_lines}

## 8. Review actions

{action_lines}

## 9. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- DWH08 map counts preserved: {'passed' if not dwh08_failed else 'failed: ' + ', '.join(dwh08_failed)}
- DWH10 refinement rows exactly five: {summary['validation']['exactly_five_refinement_rows']}
- DWH10 views queryable: {summary['validation']['dwh10_views_queryable']}

## 10. What DWH10 does not do

DWH10 does not read raw TIM/PAR files, does not use CSV/JSON/MD report outputs as input, does not touch all raw_field_value rows, does not create bridge/result tables, does not verify external evidence, does not resolve telescope/receiver/backend semantics as verified, does not compute timing/model/statistical quantities, and does not assign final physical meaning to TIM columns.

## 11. Recommended DWH11 options

{next_lines}

## 12. Claim boundary

{summary['claim_boundary']}
"""
    path.write_text(content, encoding="utf-8")


def write_outputs(
    con: sqlite3.Connection,
    output_root: Path,
    summary: dict[str, Any],
) -> None:
    paths = output_paths(output_root)
    write_readout(paths[READOUT_MD], summary)
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    write_csv(
        paths[TOKEN_REFINEMENT_CSV],
        [
            "token_position",
            "token_dictionary_id",
            "block_a_value",
            "block_b_value",
            "proposed_structural_role",
            "proposed_controlled_field_name",
            "mapping_confidence",
            "evidence_need",
            "review_status",
            "notes",
        ],
        fetch_dicts(
            con,
            """
            SELECT token_position, token_dictionary_id, block_a_value, block_b_value,
                   proposed_structural_role, proposed_controlled_field_name,
                   mapping_confidence, evidence_need, review_status, notes
            FROM qsb_v_dwh10_block_switch_refinement
            ORDER BY token_position
            """,
        ),
    )
    write_csv(
        paths[VALUE_PAIRS_CSV],
        ["token_position", "block_a_value", "block_b_value", "relation_type", "source_basis", "notes"],
        value_pair_rows(con),
    )
    write_csv(
        paths[REVIEW_ACTIONS_CSV],
        ["action_id", "token_position", "recommended_action", "priority", "depends_on", "notes"],
        review_action_rows(con),
    )
    write_csv(
        paths[NEXT_STEPS_CSV],
        ["next_step_id", "next_step_name", "prerequisite", "recommended_action", "risk_level", "notes"],
        next_dwh_steps_rows(),
    )


def execute(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
    allow_existing: bool,
) -> dict[str, Any]:
    live_before = db_state(live_db)
    preflight = ensure_preconditions(
        live_db,
        workcopy_db,
        output_root,
        overwrite,
        allow_existing,
    )
    created_at = utc_now()
    run_id = "DWH10_BLOCK_SWITCH_MAPPING_REFINEMENT_" + timestamp_for_id()

    with connect_writable(workcopy_db) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            create_tables(con, allow_existing)
            refinement_rows = build_refinement_rows(
                con,
                preflight["work_packet_source"],
                created_at,
            )
            if len(refinement_rows) != 5:
                raise RuntimeError(f"Expected exactly 5 refinement rows, got {len(refinement_rows)}.")
            insert_rows(con, "dwh10_block_switch_mapping_refinement", refinement_rows)
            create_views(con, allow_existing)
            live_after = db_state(live_db)
            validation_before_log = validate_workcopy(con, live_before, live_after)
            insert_run_log(
                con,
                run_id,
                created_at,
                live_db,
                workcopy_db,
                not validation_before_log["live_db_checksum_unchanged"]
                or not validation_before_log["live_db_stat_unchanged"],
                len(refinement_rows),
                validation_before_log["workcopy_integrity_check"],
                validation_before_log["foreign_key_violation_count"],
            )
            validation = validate_workcopy(con, live_before, live_after)
            summary = build_summary(
                con,
                run_id,
                created_at,
                live_db,
                workcopy_db,
                output_root,
                preflight,
                validation,
            )
            write_outputs(con, output_root, summary)
            con.commit()
        except Exception:
            con.rollback()
            raise
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QSB-DWH10 controlled refinement for five block-switch token candidates."
    )
    parser.add_argument(
        "--live-db",
        type=Path,
        default=DEFAULT_LIVE_DB,
        help="Path to the live consolidated SQLite DB; opened read-only.",
    )
    parser.add_argument(
        "--workcopy-db",
        type=Path,
        default=DEFAULT_WORKCOPY_DB,
        help="Path to the writable DWH target workcopy SQLite DB.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Existing output directory for DWH10 reports.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the six DWH10 report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH10 target objects; never appends to nonempty DWH10 tables.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = execute(
            args.live_db,
            args.workcopy_db,
            args.output_root,
            args.overwrite,
            args.allow_existing,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
