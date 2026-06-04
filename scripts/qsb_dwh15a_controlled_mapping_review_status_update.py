#!/usr/bin/env python3
"""QSB-DWH15A: controlled mapping-review status update layer.

Default mode is additive only: DWH15A records review-ready candidate status in
new DWH15A tables/views and does not rewrite DWH10/DWH13/DWH14A or DWH08
mapping rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh15a_controlled_mapping_review_status_update.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh15a_controlled_mapping_review_status_update_readout.md"
SUMMARY_JSON = "dwh15a_controlled_mapping_review_status_update_summary.json"
UPDATED_CSV = "dwh15a_updated_mapping_review_status.csv"
SKIPPED_CSV = "dwh15a_skipped_mapping_review_status.csv"
AUDIT_CSV = "dwh15a_mapping_status_audit.csv"
NEXT_STEPS_CSV = "dwh15a_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    UPDATED_CSV,
    SKIPPED_CSV,
    AUDIT_CSV,
    NEXT_STEPS_CSV,
]

DWH15A_TABLES = [
    "dwh15a_mapping_review_status_update",
    "dwh15a_mapping_review_status_skip",
    "dwh15a_mapping_review_status_update_run_log",
]

DWH15A_VIEWS = [
    "qsb_v_dwh15a_mapping_review_update_dashboard",
    "qsb_v_dwh15a_supported_review_ready_candidates",
    "qsb_v_dwh15a_skipped_deferred_candidates",
    "qsb_v_dwh15a_next_mapping_actions",
]

REQUIRED_TABLES = [
    "dwh14a_manual_evidence_decision",
    "dwh14a_manual_evidence_rejection_log",
    "dwh14a_manual_evidence_insertion_run_log",
    "dwh10_block_switch_mapping_refinement",
    "map_token_dictionary",
    "dwh13_manual_evidence_worklist",
]

REQUIRED_DWH14A_VIEWS = [
    "qsb_v_dwh14a_supported_candidate_terms",
    "qsb_v_dwh14a_open_or_conflict_terms",
]

EXPECTED_SUPPORTED_TERMS = {
    ("tim_token_011", "GUPPI"),
    ("tim_token_007", "Rcvr_800"),
    ("tim_token_007", "Rcvr1_2"),
}

EXPECTED_SKIPPED_TERMS = {
    ("tim_token_011", "Rcvr_800_GUPPI"),
    ("tim_token_011", "Rcvr1_2_GUPPI"),
}

TERM_ORDER = {
    ("tim_token_011", "GUPPI"): 1,
    ("tim_token_007", "Rcvr_800"): 2,
    ("tim_token_007", "Rcvr1_2"): 3,
    ("tim_token_011", "Rcvr_800_GUPPI"): 4,
    ("tim_token_011", "Rcvr1_2_GUPPI"): 5,
}

NEW_MAPPING_STATUS = "candidate_supported"
NEW_REVIEW_STATUS = "review_ready_supported_candidate"
UPDATE_ACTION = "additive_status_mark_only"
SKIP_REASON = "manual_review_deferred_needs_direct_dataset_evidence"

CLAIM_BOUNDARY = (
    "DWH15A is a workcopy-only controlled mapping-review update layer. In "
    "default additive mode it records review-ready candidate status for "
    "DWH14A supported candidate rows and skip rows for deferred terms. It does "
    "not assign final semantic meaning, does not perform Bridge/result "
    "modeling, does not evaluate Shapiro questions, and does not perform "
    "physics analysis."
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


def stable_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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


def ensure_no_outputs(output_root: Path, overwrite: bool) -> None:
    existing = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH15A output file(s): "
            + "; ".join(existing)
        )


def dwh14a_preview_view(con: sqlite3.Connection) -> str:
    if object_exists(con, "qsb_v_dwh14a_mapping_review_status_preview", "view"):
        return "qsb_v_dwh14a_mapping_review_status_preview"
    if object_exists(con, "qsb_v_dwh14a_high_priority_decision_status", "view"):
        return "qsb_v_dwh14a_high_priority_decision_status"
    raise RuntimeError(
        "Missing DWH14A mapping preview view. Expected qsb_v_dwh14a_mapping_review_status_preview "
        "or qsb_v_dwh14a_high_priority_decision_status."
    )


def fetch_table_snapshot(con: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(table_name)} ORDER BY 1")


def fetch_preview_rows(con: sqlite3.Connection, preview_view: str) -> list[dict[str, Any]]:
    return sorted(
        fetch_dicts(
            con,
            f"""
            SELECT token_position, term, proposed_role,
                   dwh14a_decision_status, evidence_strength,
                   proposed_next_mapping_status, safe_to_promote, notes
            FROM {quote_identifier(preview_view)}
            """,
        ),
        key=lambda row: TERM_ORDER.get((str(row["token_position"]), str(row["term"])), 99),
    )


def fetch_decision_by_pair(con: sqlite3.Connection) -> dict[tuple[str, str], dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT manual_evidence_decision_id, token_position, term,
               decision_status, evidence_strength, next_action
        FROM dwh14a_manual_evidence_decision
        ORDER BY manual_evidence_decision_id
        """,
    )
    return {(str(row["token_position"]), str(row["term"])): row for row in rows}


def fetch_refinement_by_token(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_dictionary_id, token_position, block_a_value, block_b_value,
               review_status
        FROM dwh10_block_switch_mapping_refinement
        ORDER BY token_position
        """,
    )
    return {str(row["token_position"]): row for row in rows}


def fetch_dictionary_status_by_id(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_dictionary_id, mapping_status, review_status
        FROM map_token_dictionary
        ORDER BY token_dictionary_id
        """,
    )
    return {str(row["token_dictionary_id"]): row for row in rows}


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
        missing_tables = [table for table in REQUIRED_TABLES if not object_exists(con, table, "table")]
        missing_views = [view for view in REQUIRED_DWH14A_VIEWS if not object_exists(con, view, "view")]
        preview_view = dwh14a_preview_view(con)
        preview_rows = fetch_preview_rows(con, preview_view)
        dwh14a_decisions = fetch_table_snapshot(con, "dwh14a_manual_evidence_decision")
        dwh14a_rejections = fetch_table_snapshot(con, "dwh14a_manual_evidence_rejection_log")
        dwh14a_run_log = fetch_table_snapshot(con, "dwh14a_manual_evidence_insertion_run_log")
        dwh10_snapshot = fetch_table_snapshot(con, "dwh10_block_switch_mapping_refinement")
        dwh13_snapshot = fetch_table_snapshot(con, "dwh13_manual_evidence_worklist")
        existing_dwh15a = [
            name for name in [*DWH15A_TABLES, *DWH15A_VIEWS]
            if object_exists(con, name)
        ]
        existing_counts = {
            table: table_count(con, table)
            for table in DWH15A_TABLES
            if object_exists(con, table, "table")
        }

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if missing_tables:
        raise RuntimeError("Missing required table(s): " + ", ".join(missing_tables))
    if missing_views:
        raise RuntimeError("Missing required DWH14A view(s): " + ", ".join(missing_views))
    supported_pairs = {
        (str(row["token_position"]), str(row["term"]))
        for row in preview_rows
        if row["dwh14a_decision_status"] == "evidence_supported_candidate"
        and int(row["safe_to_promote"] or 0) == 1
    }
    skipped_pairs = {
        (str(row["token_position"]), str(row["term"]))
        for row in preview_rows
        if (str(row["token_position"]), str(row["term"])) in EXPECTED_SKIPPED_TERMS
        and int(row["safe_to_promote"] or 0) == 0
    }
    if supported_pairs != EXPECTED_SUPPORTED_TERMS:
        raise RuntimeError(
            "DWH14A supported safe-to-promote terms do not match expected set: "
            + str(sorted(supported_pairs))
        )
    if skipped_pairs != EXPECTED_SKIPPED_TERMS:
        raise RuntimeError(
            "DWH14A deferred/open terms do not match expected skip set: "
            + str(sorted(skipped_pairs))
        )
    if existing_dwh15a and not allow_existing:
        raise RuntimeError(
            "DWH15A target object(s) already exist; rerun with --allow-existing "
            "only for controlled empty-object continuation: " + ", ".join(existing_dwh15a)
        )
    nonempty_existing = [
        f"{table}={count}"
        for table, count in existing_counts.items()
        if count > 0
    ]
    if nonempty_existing:
        raise RuntimeError(
            "Refusing to append to nonempty DWH15A table(s): "
            + ", ".join(nonempty_existing)
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "preview_view": preview_view,
        "supported_candidate_input_count": len(supported_pairs),
        "skipped_candidate_input_count": len(skipped_pairs),
        "preservation_counts": {
            "dwh14a_manual_evidence_decision": len(dwh14a_decisions),
            "dwh14a_manual_evidence_rejection_log": len(dwh14a_rejections),
            "dwh14a_manual_evidence_insertion_run_log": len(dwh14a_run_log),
            "dwh10_block_switch_mapping_refinement": len(dwh10_snapshot),
            "dwh13_manual_evidence_worklist": len(dwh13_snapshot),
        },
        "preservation_digests": {
            "dwh14a_manual_evidence_decision": stable_digest(dwh14a_decisions),
            "dwh14a_manual_evidence_rejection_log": stable_digest(dwh14a_rejections),
            "dwh14a_manual_evidence_insertion_run_log": stable_digest(dwh14a_run_log),
            "dwh10_block_switch_mapping_refinement": stable_digest(dwh10_snapshot),
            "dwh13_manual_evidence_worklist": stable_digest(dwh13_snapshot),
        },
    }


def create_tables(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    statements = [
        f"""
        CREATE TABLE {clause}dwh15a_mapping_review_status_update (
            mapping_review_update_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            token_dictionary_id TEXT,
            previous_mapping_status TEXT,
            previous_review_status TEXT,
            dwh14a_decision_status TEXT NOT NULL,
            dwh14a_evidence_strength TEXT NOT NULL,
            new_mapping_status TEXT NOT NULL,
            new_review_status TEXT NOT NULL,
            update_action TEXT NOT NULL,
            safe_to_promote INTEGER NOT NULL,
            source_decision_id TEXT NOT NULL,
            updated_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh15a_mapping_review_status_skip (
            mapping_review_skip_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            skip_reason TEXT NOT NULL,
            dwh14a_decision_status TEXT,
            dwh14a_evidence_strength TEXT,
            safe_to_promote INTEGER,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh15a_mapping_review_status_update_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            supported_candidate_input_count INTEGER,
            updated_candidate_count INTEGER,
            skipped_candidate_count INTEGER,
            forbidden_update_count INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT
        )
        """,
    ]
    for statement in statements:
        con.execute(statement)


def create_views(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    statements = [
        f"""
        CREATE VIEW {clause}qsb_v_dwh15a_mapping_review_update_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'dwh15a_mapping_review_status_update_run_log' AS metric_source,
               notes AS dashboard_note
        FROM dwh15a_mapping_review_status_update_run_log
        UNION ALL
        SELECT 'supported_candidate_input_count',
               CAST(supported_candidate_input_count AS TEXT),
               'dwh15a_mapping_review_status_update_run_log',
               'DWH14A supported safe-to-promote input rows.'
        FROM dwh15a_mapping_review_status_update_run_log
        UNION ALL
        SELECT 'updated_candidate_count',
               CAST(updated_candidate_count AS TEXT),
               'dwh15a_mapping_review_status_update',
               'Additive DWH15A review-ready candidate rows.'
        FROM dwh15a_mapping_review_status_update_run_log
        UNION ALL
        SELECT 'skipped_candidate_count',
               CAST(skipped_candidate_count AS TEXT),
               'dwh15a_mapping_review_status_skip',
               'Deferred/open candidate rows skipped.'
        FROM dwh15a_mapping_review_status_update_run_log
        UNION ALL
        SELECT 'forbidden_update_count',
               CAST(forbidden_update_count AS TEXT),
               'DWH15A validation',
               'Rows outside the allowed supported set that would have been updated.'
        FROM dwh15a_mapping_review_status_update_run_log
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DWH15A insertions.'
        FROM dwh15a_mapping_review_status_update_run_log
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh15a_supported_review_ready_candidates AS
        SELECT *
        FROM dwh15a_mapping_review_status_update
        ORDER BY
            CASE term
                WHEN 'GUPPI' THEN 1
                WHEN 'Rcvr_800' THEN 2
                WHEN 'Rcvr1_2' THEN 3
                ELSE 9
            END
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh15a_skipped_deferred_candidates AS
        SELECT *
        FROM dwh15a_mapping_review_status_skip
        ORDER BY term
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh15a_next_mapping_actions AS
        SELECT
            token_position,
            term,
            new_mapping_status AS candidate_mapping_status,
            new_review_status AS candidate_review_status,
            update_action,
            'Inspect DWH15A additive status before any later direct mapping-status update.' AS recommended_next_action,
            notes
        FROM dwh15a_mapping_review_status_update
        UNION ALL
        SELECT
            token_position,
            term,
            'not_updated',
            'manual_review_still_open',
            'skip',
            'Collect direct dataset evidence before considering status update.',
            notes
        FROM dwh15a_mapping_review_status_skip
        ORDER BY token_position, term
        """,
    ]
    for statement in statements:
        con.execute(statement)


def insert_rows(con: sqlite3.Connection, table_name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    column_sql = ", ".join(quote_identifier(column) for column in columns)
    sql = f"INSERT INTO {quote_identifier(table_name)} ({column_sql}) VALUES ({placeholders})"
    con.executemany(sql, [[row[column] for column in columns] for row in rows])


def build_update_and_skip_rows(
    con: sqlite3.Connection,
    preview_rows: list[dict[str, Any]],
    created_at: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    decisions = fetch_decision_by_pair(con)
    refinements = fetch_refinement_by_token(con)
    dictionary_status = fetch_dictionary_status_by_id(con)
    update_rows: list[dict[str, Any]] = []
    skip_rows: list[dict[str, Any]] = []
    forbidden_update_count = 0
    for row in preview_rows:
        pair = (str(row["token_position"]), str(row["term"]))
        decision = decisions.get(pair)
        if pair in EXPECTED_SUPPORTED_TERMS:
            if row["dwh14a_decision_status"] != "evidence_supported_candidate" or int(row["safe_to_promote"] or 0) != 1:
                forbidden_update_count += 1
                continue
            refinement = refinements.get(str(row["token_position"]), {})
            token_dictionary_id = refinement.get("token_dictionary_id")
            map_status = dictionary_status.get(str(token_dictionary_id), {}) if token_dictionary_id else {}
            update_rows.append(
                {
                    "mapping_review_update_id": f"dwh15a_mapping_review_update_{len(update_rows) + 1:03d}",
                    "token_position": row["token_position"],
                    "term": row["term"],
                    "token_dictionary_id": token_dictionary_id,
                    "previous_mapping_status": map_status.get("mapping_status"),
                    "previous_review_status": map_status.get("review_status") or refinement.get("review_status"),
                    "dwh14a_decision_status": row["dwh14a_decision_status"],
                    "dwh14a_evidence_strength": row["evidence_strength"],
                    "new_mapping_status": NEW_MAPPING_STATUS,
                    "new_review_status": NEW_REVIEW_STATUS,
                    "update_action": UPDATE_ACTION,
                    "safe_to_promote": 1,
                    "source_decision_id": decision["manual_evidence_decision_id"] if decision else "missing_decision_id",
                    "updated_at_utc": created_at,
                    "notes": "Additive DWH15A candidate review status only; existing mapping rows were not rewritten.",
                }
            )
        elif pair in EXPECTED_SKIPPED_TERMS:
            skip_rows.append(
                {
                    "mapping_review_skip_id": f"dwh15a_mapping_review_skip_{len(skip_rows) + 1:03d}",
                    "token_position": row["token_position"],
                    "term": row["term"],
                    "skip_reason": SKIP_REASON,
                    "dwh14a_decision_status": row["dwh14a_decision_status"],
                    "dwh14a_evidence_strength": row["evidence_strength"],
                    "safe_to_promote": int(row["safe_to_promote"] or 0),
                    "created_at_utc": created_at,
                    "notes": "Skipped by rule: compound label remains deferred/open and was not updated.",
                }
            )
        elif int(row["safe_to_promote"] or 0) == 1:
            forbidden_update_count += 1
    if len(update_rows) != 3:
        raise RuntimeError(f"Expected exactly 3 DWH15A update rows, got {len(update_rows)}.")
    if len(skip_rows) != 2:
        raise RuntimeError(f"Expected exactly 2 DWH15A skip rows, got {len(skip_rows)}.")
    if forbidden_update_count:
        raise RuntimeError(f"Forbidden update candidate count is nonzero: {forbidden_update_count}.")
    return update_rows, skip_rows, forbidden_update_count


def ensure_direct_update_is_safe(update_rows: list[dict[str, Any]], skip_rows: list[dict[str, Any]]) -> None:
    supported_ids = {row["token_dictionary_id"] for row in update_rows if row["token_dictionary_id"]}
    skipped_tokens = {row["token_position"] for row in skip_rows}
    unsafe_ids = {
        row["token_dictionary_id"]
        for row in update_rows
        if row["token_position"] in skipped_tokens and row["token_dictionary_id"]
    }
    if unsafe_ids:
        raise RuntimeError(
            "Direct map update is unsafe because supported and deferred terms share token dictionary context: "
            + ", ".join(sorted(unsafe_ids))
        )
    if len(supported_ids) != len(update_rows):
        raise RuntimeError("Direct map update requires unique token_dictionary_id for every update row.")


def apply_direct_map_update(con: sqlite3.Connection, update_rows: list[dict[str, Any]], skip_rows: list[dict[str, Any]]) -> None:
    ensure_direct_update_is_safe(update_rows, skip_rows)
    for row in update_rows:
        con.execute(
            """
            UPDATE map_token_dictionary
            SET mapping_status = ?,
                review_status = ?
            WHERE token_dictionary_id = ?
            """,
            (NEW_MAPPING_STATUS, NEW_REVIEW_STATUS, row["token_dictionary_id"]),
        )
    changed = con.execute("SELECT changes()").fetchone()
    _ = changed


def insert_run_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    live_modified: bool,
    supported_input_count: int,
    updated_count: int,
    skipped_count: int,
    forbidden_count: int,
    integrity: str,
    fk_count: int,
    apply_direct_map_update_flag: bool,
) -> None:
    con.execute(
        """
        INSERT INTO dwh15a_mapping_review_status_update_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            supported_candidate_input_count,
            updated_candidate_count,
            skipped_candidate_count,
            forbidden_update_count,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(live_db),
            str(workcopy_db),
            SCRIPT_NAME,
            (
                "workcopy_controlled_mapping_review_update_direct"
                if apply_direct_map_update_flag
                else "workcopy_controlled_mapping_review_update_additive_only"
            ),
            1 if live_modified else 0,
            1,
            supported_input_count,
            updated_count,
            skipped_count,
            forbidden_count,
            integrity,
            fk_count,
            "DWH15A recorded controlled candidate review status; default mode is additive only.",
        ),
    )


def validate_workcopy(
    con: sqlite3.Connection,
    preflight: dict[str, Any],
    live_before: dict[str, Any],
    live_after: dict[str, Any],
) -> dict[str, Any]:
    integrity = integrity_check(con)
    fk_violations = foreign_key_violations(con)
    after_snapshots = {
        "dwh14a_manual_evidence_decision": fetch_table_snapshot(con, "dwh14a_manual_evidence_decision"),
        "dwh14a_manual_evidence_rejection_log": fetch_table_snapshot(con, "dwh14a_manual_evidence_rejection_log"),
        "dwh14a_manual_evidence_insertion_run_log": fetch_table_snapshot(con, "dwh14a_manual_evidence_insertion_run_log"),
        "dwh10_block_switch_mapping_refinement": fetch_table_snapshot(con, "dwh10_block_switch_mapping_refinement"),
        "dwh13_manual_evidence_worklist": fetch_table_snapshot(con, "dwh13_manual_evidence_worklist"),
    }
    preservation = {
        name: {
            "count_before": preflight["preservation_counts"][name],
            "count_after": len(rows),
            "digest_before": preflight["preservation_digests"][name],
            "digest_after": stable_digest(rows),
            "status": (
                "passed"
                if preflight["preservation_counts"][name] == len(rows)
                and preflight["preservation_digests"][name] == stable_digest(rows)
                else "failed"
            ),
        }
        for name, rows in after_snapshots.items()
    }
    counts = {table: table_count(con, table) for table in DWH15A_TABLES}
    forbidden_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM dwh15a_mapping_review_status_update
        WHERE (token_position, term) NOT IN (
            SELECT 'tim_token_011', 'GUPPI'
            UNION ALL SELECT 'tim_token_007', 'Rcvr_800'
            UNION ALL SELECT 'tim_token_007', 'Rcvr1_2'
        )
        """,
    )
    view_counts = {
        view: table_count(con, view)
        for view in DWH15A_VIEWS
        if object_exists(con, view, "view")
    }
    return {
        "workcopy_integrity_check": integrity,
        "workcopy_foreign_key_violations": fk_violations,
        "foreign_key_violation_count": len(fk_violations),
        "dwh15a_table_counts": counts,
        "exact_update_count_status": "passed" if counts["dwh15a_mapping_review_status_update"] == 3 else "failed",
        "exact_skip_count_status": "passed" if counts["dwh15a_mapping_review_status_skip"] == 2 else "failed",
        "forbidden_update_rows": forbidden_rows,
        "forbidden_update_count": len(forbidden_rows),
        "forbidden_update_status": "passed" if not forbidden_rows else "failed",
        "preservation": preservation,
        "preservation_status": "passed" if all(item["status"] == "passed" for item in preservation.values()) else "failed",
        "dwh15a_view_counts": view_counts,
        "dwh15a_views_queryable": len(view_counts) == len(DWH15A_VIEWS),
        "live_db_sha256_before": live_before["sha256"],
        "live_db_sha256_after": live_after["sha256"],
        "live_db_stat_before": live_before["stat"],
        "live_db_stat_after": live_after["stat"],
        "live_db_checksum_unchanged": live_before["sha256"] == live_after["sha256"],
        "live_db_stat_unchanged": live_before["stat"] == live_after["stat"],
    }


def fetch_all(con: sqlite3.Connection, source_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(source_name)}")


def audit_rows(
    update_rows: list[dict[str, Any]],
    skip_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in update_rows:
        rows.append(
            {
                "audit_id": f"dwh15a_audit_{len(rows) + 1:03d}",
                "term": row["term"],
                "token_position": row["token_position"],
                "action_type": "additive_status_mark",
                "old_status": row["previous_review_status"],
                "new_status": row["new_review_status"],
                "source_decision_id": row["source_decision_id"],
                "notes": row["notes"],
            }
        )
    for row in skip_rows:
        rows.append(
            {
                "audit_id": f"dwh15a_audit_{len(rows) + 1:03d}",
                "term": row["term"],
                "token_position": row["token_position"],
                "action_type": "skip_deferred",
                "old_status": row["dwh14a_decision_status"],
                "new_status": "not_updated",
                "source_decision_id": "",
                "notes": row["notes"],
            }
        )
    return rows


def next_dwh_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH16_A",
            "next_step_name": "DBeaver inspection of DWH15A supported/open candidate separation",
            "prerequisite": "DWH15A tables and views are queryable",
            "recommended_action": "Inspect supported review-ready rows and skipped deferred compound labels.",
            "risk_level": "low",
            "notes": "Recommended immediate audit step.",
        },
        {
            "next_step_id": "DWH16_B",
            "next_step_name": "Manual evidence follow-up for compound labels",
            "prerequisite": "DWH15A skipped compound rows exist",
            "recommended_action": "Collect direct dataset evidence for Rcvr_800_GUPPI and Rcvr1_2_GUPPI.",
            "risk_level": "medium",
            "notes": "Needed before compound labels can move beyond open/deferred status.",
        },
        {
            "next_step_id": "DWH16_C",
            "next_step_name": "Shapiro-Mart minimal design gate after review",
            "prerequisite": "Supported/open candidate separation has been reviewed",
            "recommended_action": "Draft only the question design gate, not calculations.",
            "risk_level": "high",
            "notes": "Do not start design until evidence separation is accepted.",
        },
        {
            "next_step_id": "DWH16_D",
            "next_step_name": "Bridge/result skeleton after explicit question design",
            "prerequisite": "A Shapiro-Mart question design exists and is bounded",
            "recommended_action": "Defer any skeleton until the design question is explicit.",
            "risk_level": "high",
            "notes": "DWH15A does not support bridge/result construction.",
        },
    ]


def build_summary(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    preflight: dict[str, Any],
    validation: dict[str, Any],
    apply_direct_map_update_flag: bool,
    audit: list[dict[str, Any]],
) -> dict[str, Any]:
    update_rows = fetch_all(con, "dwh15a_mapping_review_status_update")
    skip_rows = fetch_all(con, "dwh15a_mapping_review_status_skip")
    dashboard_rows = fetch_all(con, "qsb_v_dwh15a_mapping_review_update_dashboard")
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH controlled mapping-review update in workcopy only",
        "data_substrate_used": str(workcopy_db),
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "update_mode": "direct_map_update" if apply_direct_map_update_flag else "additive_only",
        "dwh14a_preview_view_used": preflight["preview_view"],
        "updated_candidates": update_rows,
        "updated_candidate_count": len(update_rows),
        "skipped_candidates": skip_rows,
        "skipped_candidate_count": len(skip_rows),
        "forbidden_update_count": validation["forbidden_update_count"],
        "dashboard_rows": dashboard_rows,
        "audit_rows": audit,
        "next_dwh_steps": next_dwh_steps_rows(),
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
            "supported_candidate_input_count": preflight["supported_candidate_input_count"],
        },
        "validation": validation,
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }


def csv_text(fieldnames: list[str], rows: list[dict[str, Any]]) -> str:
    handle = io.StringIO()
    writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return handle.getvalue()


def format_update_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; new_mapping_status={new_mapping_status}; new_review_status={new_review_status}; action={update_action}".format(**row)
        for row in rows
    )


def format_skip_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; reason={skip_reason}; status={dwh14a_decision_status}; safe_to_promote={safe_to_promote}".format(**row)
        for row in rows
    )


def render_readout(summary: dict[str, Any]) -> str:
    live_status = (
        "unchanged"
        if summary["validation"]["live_db_checksum_unchanged"]
        and summary["validation"]["live_db_stat_unchanged"]
        else "changed"
    )
    next_lines = "\n".join(
        "- {next_step_id}: {next_step_name}".format(**row)
        for row in summary["next_dwh_steps"]
    )
    return f"""# QSB-DWH15A Controlled Mapping Review Status Update Readout

## 1. Executive summary

Befund: DWH15A recorded additive mapping-review status for the three DWH14A supported, safe-to-promote candidate terms and skipped the two deferred compound labels.

- Run ID: `{summary['run_id']}`
- Workcopy DB: `{summary['workcopy_db_path']}`
- Update mode: {summary['update_mode']}
- Updated candidate count: {summary['updated_candidate_count']}
- Skipped candidate count: {summary['skipped_candidate_count']}
- Forbidden update count: {summary['forbidden_update_count']}

## 2. Workcopy-only principle

DWH15A writes were limited to new DWH15A tables and views in the workcopy DB. Existing DWH10, DWH13, DWH14A, and mapping dictionary rows were preserved in additive-only mode.

## 3. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH15A: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH15A: {live_status}

## 4. Supported candidates selected

{format_update_lines(summary['updated_candidates'])}

## 5. Deferred candidates skipped

{format_skip_lines(summary['skipped_candidates'])}

## 6. Mapping status update mode

Mode used: {summary['update_mode']}. DWH14A preview source used: `{summary['dwh14a_preview_view_used']}`.

## 7. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- Exact update count: {summary['validation']['exact_update_count_status']}
- Exact skip count: {summary['validation']['exact_skip_count_status']}
- Forbidden update check: {summary['validation']['forbidden_update_status']}
- Upstream preservation: {summary['validation']['preservation_status']}
- DWH15A views queryable: {summary['validation']['dwh15a_views_queryable']}

## 8. What DWH15_A does not do

DWH15A does not assign final semantic meaning, does not update deferred/open terms, does not perform live retrieval, does not read raw TIM/PAR files, does not create bridge/result tables, does not compute timing/model/statistical quantities, and does not make physical interpretation statements.

## 9. Recommended DWH16 options

{next_lines}

## 10. Claim boundary

{summary['claim_boundary']}
"""


def render_outputs(summary: dict[str, Any]) -> dict[str, str]:
    return {
        READOUT_MD: render_readout(summary),
        SUMMARY_JSON: pretty_json(summary) + "\n",
        UPDATED_CSV: csv_text(
            [
                "token_position",
                "term",
                "previous_mapping_status",
                "previous_review_status",
                "dwh14a_decision_status",
                "dwh14a_evidence_strength",
                "new_mapping_status",
                "new_review_status",
                "update_action",
                "safe_to_promote",
                "notes",
            ],
            summary["updated_candidates"],
        ),
        SKIPPED_CSV: csv_text(
            [
                "token_position",
                "term",
                "skip_reason",
                "dwh14a_decision_status",
                "dwh14a_evidence_strength",
                "safe_to_promote",
                "notes",
            ],
            summary["skipped_candidates"],
        ),
        AUDIT_CSV: csv_text(
            [
                "audit_id",
                "term",
                "token_position",
                "action_type",
                "old_status",
                "new_status",
                "source_decision_id",
                "notes",
            ],
            summary["audit_rows"],
        ),
        NEXT_STEPS_CSV: csv_text(
            [
                "next_step_id",
                "next_step_name",
                "prerequisite",
                "recommended_action",
                "risk_level",
                "notes",
            ],
            summary["next_dwh_steps"],
        ),
    }


def write_outputs(output_root: Path, output_texts: dict[str, str]) -> None:
    for name in OUTPUT_FILENAMES:
        (output_root / name).write_text(output_texts[name], encoding="utf-8")


def execute(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
    allow_existing: bool,
    apply_direct_map_update_flag: bool,
) -> dict[str, Any]:
    live_before = db_state(live_db)
    preflight = ensure_preconditions(live_db, workcopy_db, output_root, overwrite, allow_existing)
    created_at = utc_now()
    run_id = "DWH15A_CONTROLLED_MAPPING_REVIEW_UPDATE_" + timestamp_for_id()
    output_texts: dict[str, str]

    con = connect_writable(workcopy_db)
    try:
        con.execute("BEGIN IMMEDIATE")
        create_tables(con, allow_existing)
        preview_rows = fetch_preview_rows(con, preflight["preview_view"])
        update_rows, skip_rows, forbidden_count = build_update_and_skip_rows(con, preview_rows, created_at)
        if apply_direct_map_update_flag:
            apply_direct_map_update(con, update_rows, skip_rows)
            for row in update_rows:
                row["update_action"] = "direct_map_update"
                row["notes"] = "DWH15A direct map update was applied after safety checks."
        insert_rows(con, "dwh15a_mapping_review_status_update", update_rows)
        insert_rows(con, "dwh15a_mapping_review_status_skip", skip_rows)
        create_views(con, allow_existing)

        live_after = db_state(live_db)
        validation_before_log = validate_workcopy(con, preflight, live_before, live_after)
        insert_run_log(
            con,
            run_id,
            created_at,
            live_db,
            workcopy_db,
            not validation_before_log["live_db_checksum_unchanged"]
            or not validation_before_log["live_db_stat_unchanged"],
            preflight["supported_candidate_input_count"],
            len(update_rows),
            len(skip_rows),
            forbidden_count,
            validation_before_log["workcopy_integrity_check"],
            validation_before_log["foreign_key_violation_count"],
            apply_direct_map_update_flag,
        )
        validation = validate_workcopy(con, preflight, live_before, live_after)
        audit = audit_rows(update_rows, skip_rows)
        summary = build_summary(
            con,
            run_id,
            created_at,
            live_db,
            workcopy_db,
            output_root,
            preflight,
            validation,
            apply_direct_map_update_flag,
            audit,
        )
        output_texts = render_outputs(summary)
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()

    write_outputs(output_root, output_texts)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QSB-DWH15A controlled mapping-review status update for supported candidates."
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
        help="Existing output directory for DWH15A reports.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the six DWH15A report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH15A target objects; never appends to nonempty DWH15A tables.",
    )
    parser.add_argument(
        "--apply-direct-map-update",
        action="store_true",
        help="Attempt direct map_token_dictionary update after strict safety checks.",
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
            args.apply_direct_map_update,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
