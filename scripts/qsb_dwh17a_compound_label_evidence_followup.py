#!/usr/bin/env python3
"""QSB-DWH17A: compound-label manual evidence follow-up preparation.

This script creates a focused DWH17A workcopy layer for the two deferred
compound labels only. It does not retrieve internet content, does not promote
compound labels, and does not update existing mapping/status rows.
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


SCRIPT_NAME = "scripts/qsb_dwh17a_compound_label_evidence_followup.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh17a_compound_label_evidence_followup_readout.md"
SUMMARY_JSON = "dwh17a_compound_label_evidence_followup_summary.json"
WORKLIST_CSV = "dwh17a_compound_label_followup_worklist.csv"
SOURCE_STRATEGY_CSV = "dwh17a_compound_label_source_strategy.csv"
DECISION_TEMPLATE_CSV = "dwh17a_compound_label_decision_template.csv"
NEXT_STEPS_CSV = "dwh17a_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    WORKLIST_CSV,
    SOURCE_STRATEGY_CSV,
    DECISION_TEMPLATE_CSV,
    NEXT_STEPS_CSV,
]

DWH17A_TABLES = [
    "dwh17a_compound_label_followup_worklist",
    "dwh17a_compound_label_source_strategy",
    "dwh17a_compound_label_decision_template",
    "dwh17a_compound_label_followup_run_log",
]

DWH17A_VIEWS = [
    "qsb_v_dwh17a_compound_label_dashboard",
    "qsb_v_dwh17a_compound_label_worklist",
    "qsb_v_dwh17a_compound_label_source_strategy",
    "qsb_v_dwh17a_next_compound_actions",
]

REQUIRED_TABLES = [
    "dwh14a_manual_evidence_decision",
    "dwh15a_mapping_review_status_update",
    "dwh15a_mapping_review_status_skip",
]

REQUIRED_VIEWS = [
    "qsb_v_dwh14a_high_priority_decision_status",
    "qsb_v_dwh14a_supported_candidate_terms",
    "qsb_v_dwh14a_open_or_conflict_terms",
    "qsb_v_dwh15a_supported_review_ready_candidates",
    "qsb_v_dwh15a_skipped_deferred_candidates",
]

SUPPORTED_COMPONENTS = {
    ("tim_token_011", "GUPPI"),
    ("tim_token_007", "Rcvr_800"),
    ("tim_token_007", "Rcvr1_2"),
}

COMPOUND_LABELS = [
    {
        "compound_label": "Rcvr_800_GUPPI",
        "token_position": "tim_token_011",
        "component_receiver_label": "Rcvr_800",
        "component_backend_label": "GUPPI",
        "followup_priority": "P1",
    },
    {
        "compound_label": "Rcvr1_2_GUPPI",
        "token_position": "tim_token_011",
        "component_receiver_label": "Rcvr1_2",
        "component_backend_label": "GUPPI",
        "followup_priority": "P1",
    },
]

COMPOUND_PAIRS = {
    (row["token_position"], row["compound_label"]) for row in COMPOUND_LABELS
}

COMPONENT_SUPPORT_STATUS = (
    "Component support exists. Compound-label support is still open."
)

ALLOWED_DECISION_STATUS = (
    "evidence_supported_candidate; evidence_gap_open; "
    "evidence_conflict_or_mismatch; source_not_controlled_enough; "
    "manual_review_deferred"
)

REQUIRED_EVIDENCE_FIELDS = (
    "source_label; source_url_or_local_reference; evidence_excerpt_or_summary; "
    "retrieval_or_access_date; reviewer_note; decision_status"
)

ALLOWED_NEXT_ACTIONS = (
    "promote_compound_to_evidence_supported_candidate; keep_compound_open; "
    "mark_compound_conflict_for_review; defer_compound_review; "
    "request_additional_dataset_source"
)

ACCEPT_CRITERIA = (
    "Direct controlled source explicitly uses the exact compound label or "
    "documents a naming convention that combines receiver label plus GUPPI "
    "backend in the same dataset/pipeline context."
)

REJECT_CRITERIA = (
    "Source only supports Rcvr_800/Rcvr1_2 and GUPPI separately, without "
    "direct compound-label or dataset naming-convention evidence."
)

CLAIM_BOUNDARY = (
    "DWH17A is a workcopy-only preparation layer for manual evidence follow-up "
    "on the two deferred compound labels. Component support exists. "
    "Compound-label support is still open. DWH17A does not promote compound "
    "labels, does not update supported component terms, does not update "
    "map_token_dictionary, does not create bridge/result tables, and does not "
    "perform Shapiro or physics analysis."
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


def ensure_paths(live_db: Path, workcopy_db: Path, output_root: Path) -> None:
    if not live_db.exists() or not live_db.is_file():
        raise FileNotFoundError(f"Live DB file missing: {live_db}")
    if not workcopy_db.exists() or not workcopy_db.is_file():
        raise FileNotFoundError(f"Workcopy DB file missing: {workcopy_db}")
    if not output_root.exists() or not output_root.is_dir():
        raise FileNotFoundError(f"Output root missing: {output_root}")


def ensure_no_outputs(output_root: Path, overwrite: bool) -> None:
    existing = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH17A output file(s): "
            + "; ".join(existing)
        )


def fetch_table_snapshot(con: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(table_name)} ORDER BY 1")


def fetch_supported_component_pairs(con: sqlite3.Connection) -> set[tuple[str, str]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_position, term
        FROM qsb_v_dwh15a_supported_review_ready_candidates
        """,
    )
    return {(str(row["token_position"]), str(row["term"])) for row in rows}


def fetch_skipped_compound_pairs(con: sqlite3.Connection) -> set[tuple[str, str]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_position, term
        FROM qsb_v_dwh15a_skipped_deferred_candidates
        """,
    )
    return {(str(row["token_position"]), str(row["term"])) for row in rows}


def ensure_preconditions(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
    allow_existing: bool,
) -> dict[str, Any]:
    ensure_paths(live_db, workcopy_db, output_root)
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
        missing_views = [view for view in REQUIRED_VIEWS if not object_exists(con, view, "view")]
        supported_pairs = fetch_supported_component_pairs(con)
        skipped_pairs = fetch_skipped_compound_pairs(con)
        snapshots = {
            "dwh14a_manual_evidence_decision": fetch_table_snapshot(con, "dwh14a_manual_evidence_decision"),
            "dwh15a_mapping_review_status_update": fetch_table_snapshot(con, "dwh15a_mapping_review_status_update"),
            "dwh15a_mapping_review_status_skip": fetch_table_snapshot(con, "dwh15a_mapping_review_status_skip"),
        }
        existing_dwh17a = [
            name for name in [*DWH17A_TABLES, *DWH17A_VIEWS]
            if object_exists(con, name)
        ]
        existing_counts = {
            table: table_count(con, table)
            for table in DWH17A_TABLES
            if object_exists(con, table, "table")
        }

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if missing_tables:
        raise RuntimeError("Missing required table(s): " + ", ".join(missing_tables))
    if missing_views:
        raise RuntimeError("Missing required view(s): " + ", ".join(missing_views))
    if supported_pairs != SUPPORTED_COMPONENTS:
        raise RuntimeError("Supported component terms do not match expected set: " + str(sorted(supported_pairs)))
    if skipped_pairs != COMPOUND_PAIRS:
        raise RuntimeError("Deferred compound labels do not match expected set: " + str(sorted(skipped_pairs)))
    if existing_dwh17a and not allow_existing:
        raise RuntimeError(
            "DWH17A target object(s) already exist; rerun with --allow-existing "
            "only for controlled empty-object continuation: " + ", ".join(existing_dwh17a)
        )
    nonempty_existing = [
        f"{table}={count}"
        for table, count in existing_counts.items()
        if count > 0
    ]
    if nonempty_existing:
        raise RuntimeError(
            "Refusing to append to nonempty DWH17A table(s): "
            + ", ".join(nonempty_existing)
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "supported_component_pairs": sorted(supported_pairs),
        "compound_pairs": sorted(skipped_pairs),
        "preservation_counts": {name: len(rows) for name, rows in snapshots.items()},
        "preservation_digests": {name: stable_digest(rows) for name, rows in snapshots.items()},
    }


def create_tables(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    statements = [
        f"""
        CREATE TABLE {clause}dwh17a_compound_label_followup_worklist (
            followup_id TEXT PRIMARY KEY,
            compound_label TEXT NOT NULL,
            token_position TEXT NOT NULL,
            component_receiver_label TEXT NOT NULL,
            component_backend_label TEXT NOT NULL,
            component_support_status TEXT NOT NULL,
            current_compound_status TEXT NOT NULL,
            direct_evidence_need TEXT NOT NULL,
            followup_priority TEXT NOT NULL,
            manual_followup_status TEXT NOT NULL,
            blocking_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh17a_compound_label_source_strategy (
            source_strategy_id TEXT PRIMARY KEY,
            compound_label TEXT NOT NULL,
            preferred_source_category TEXT NOT NULL,
            suggested_source_label TEXT,
            suggested_search_phrase TEXT,
            accept_criteria TEXT NOT NULL,
            reject_criteria TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh17a_compound_label_decision_template (
            decision_template_id TEXT PRIMARY KEY,
            compound_label TEXT NOT NULL,
            allowed_decision_status TEXT NOT NULL,
            required_evidence_fields TEXT NOT NULL,
            required_reviewer_note TEXT NOT NULL,
            allowed_next_actions TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh17a_compound_label_followup_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            compound_label_count INTEGER,
            worklist_row_count INTEGER,
            source_strategy_row_count INTEGER,
            decision_template_row_count INTEGER,
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
        CREATE VIEW {clause}qsb_v_dwh17a_compound_label_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'dwh17a_compound_label_followup_run_log' AS metric_source,
               notes AS dashboard_note
        FROM dwh17a_compound_label_followup_run_log
        UNION ALL
        SELECT 'compound_label_count',
               CAST(compound_label_count AS TEXT),
               'dwh17a_compound_label_followup_run_log',
               'Compound labels in DWH17A scope.'
        FROM dwh17a_compound_label_followup_run_log
        UNION ALL
        SELECT 'worklist_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh17a_compound_label_followup_worklist',
               'One worklist row per compound label.'
        FROM dwh17a_compound_label_followup_worklist
        UNION ALL
        SELECT 'source_strategy_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh17a_compound_label_source_strategy',
               'One source strategy row per compound label.'
        FROM dwh17a_compound_label_source_strategy
        UNION ALL
        SELECT 'decision_template_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh17a_compound_label_decision_template',
               'One decision template row per compound label.'
        FROM dwh17a_compound_label_decision_template
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DWH17A insertion.'
        FROM dwh17a_compound_label_followup_run_log
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh17a_compound_label_worklist AS
        SELECT *
        FROM dwh17a_compound_label_followup_worklist
        ORDER BY compound_label
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh17a_compound_label_source_strategy AS
        SELECT *
        FROM dwh17a_compound_label_source_strategy
        ORDER BY compound_label
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh17a_next_compound_actions AS
        SELECT
            w.compound_label,
            w.token_position,
            w.manual_followup_status,
            w.blocking_status,
            s.preferred_source_category,
            s.suggested_search_phrase,
            'Find direct dataset/pipeline evidence for exact compound-label usage, or keep compound open.' AS recommended_next_action,
            w.notes
        FROM dwh17a_compound_label_followup_worklist w
        JOIN dwh17a_compound_label_source_strategy s
          ON s.compound_label = w.compound_label
        ORDER BY w.compound_label
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


def build_worklist_rows(created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(COMPOUND_LABELS, start=1):
        rows.append(
            {
                "followup_id": f"dwh17a_compound_followup_{idx:03d}",
                "compound_label": item["compound_label"],
                "token_position": item["token_position"],
                "component_receiver_label": item["component_receiver_label"],
                "component_backend_label": item["component_backend_label"],
                "component_support_status": COMPONENT_SUPPORT_STATUS,
                "current_compound_status": "manual_review_deferred",
                "direct_evidence_need": (
                    "Direct dataset, release, pipeline, file-format, local README, "
                    "or institutional metadata evidence for exact compound-label usage."
                ),
                "followup_priority": item["followup_priority"],
                "manual_followup_status": "pending_direct_dataset_evidence",
                "blocking_status": "blocks_compound_label_promotion",
                "created_at_utc": created_at,
                "notes": "Do not promote compound label from component-only support.",
            }
        )
    return rows


def build_source_strategy_rows(created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(COMPOUND_LABELS, start=1):
        label = item["compound_label"]
        rows.append(
            {
                "source_strategy_id": f"dwh17a_source_strategy_{idx:03d}",
                "compound_label": label,
                "preferred_source_category": "institutional_dataset_documentation",
                "suggested_source_label": (
                    "NANOGrav/IPTA/PTA release documentation, local dataset README, "
                    "official release metadata, or pipeline/file-format documentation"
                ),
                "suggested_search_phrase": (
                    f"{label} exact compound label dataset release metadata pipeline README"
                ),
                "accept_criteria": ACCEPT_CRITERIA,
                "reject_criteria": REJECT_CRITERIA,
                "created_at_utc": created_at,
                "notes": "Manual review must cite direct compound-label or naming-convention evidence.",
            }
        )
    return rows


def build_decision_template_rows(created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, item in enumerate(COMPOUND_LABELS, start=1):
        rows.append(
            {
                "decision_template_id": f"dwh17a_decision_template_{idx:03d}",
                "compound_label": item["compound_label"],
                "allowed_decision_status": ALLOWED_DECISION_STATUS,
                "required_evidence_fields": REQUIRED_EVIDENCE_FIELDS,
                "required_reviewer_note": (
                    "Reviewer must state whether direct compound-label evidence exists, "
                    "remains open, conflicts, or requires deferral."
                ),
                "allowed_next_actions": ALLOWED_NEXT_ACTIONS,
                "created_at_utc": created_at,
                "notes": "Template only; DWH17A does not insert manual evidence decisions.",
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
    worklist_count: int,
    source_count: int,
    template_count: int,
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh17a_compound_label_followup_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            compound_label_count,
            worklist_row_count,
            source_strategy_row_count,
            decision_template_row_count,
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
            "workcopy_compound_label_evidence_followup_preparation",
            1 if live_modified else 0,
            1,
            len(COMPOUND_LABELS),
            worklist_count,
            source_count,
            template_count,
            integrity,
            fk_count,
            "DWH17A prepares direct evidence follow-up for compound labels only.",
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
    snapshots = {
        "dwh14a_manual_evidence_decision": fetch_table_snapshot(con, "dwh14a_manual_evidence_decision"),
        "dwh15a_mapping_review_status_update": fetch_table_snapshot(con, "dwh15a_mapping_review_status_update"),
        "dwh15a_mapping_review_status_skip": fetch_table_snapshot(con, "dwh15a_mapping_review_status_skip"),
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
        for name, rows in snapshots.items()
    }
    counts = {table: table_count(con, table) for table in DWH17A_TABLES}
    non_compound_rows = fetch_dicts(
        con,
        """
        SELECT compound_label
        FROM dwh17a_compound_label_followup_worklist
        WHERE compound_label NOT IN ('Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
        """,
    )
    view_counts = {
        view: table_count(con, view)
        for view in DWH17A_VIEWS
        if object_exists(con, view, "view")
    }
    return {
        "workcopy_integrity_check": integrity,
        "workcopy_foreign_key_violations": fk_violations,
        "foreign_key_violation_count": len(fk_violations),
        "dwh17a_table_counts": counts,
        "worklist_count_status": "passed" if counts["dwh17a_compound_label_followup_worklist"] == 2 else "failed",
        "source_strategy_count_status": "passed" if counts["dwh17a_compound_label_source_strategy"] == 2 else "failed",
        "decision_template_count_status": "passed" if counts["dwh17a_compound_label_decision_template"] == 2 else "failed",
        "non_compound_rows": non_compound_rows,
        "non_compound_row_status": "passed" if not non_compound_rows else "failed",
        "preservation": preservation,
        "preservation_status": "passed" if all(row["status"] == "passed" for row in preservation.values()) else "failed",
        "dwh17a_view_counts": view_counts,
        "dwh17a_views_queryable": len(view_counts) == len(DWH17A_VIEWS),
        "live_db_sha256_before": live_before["sha256"],
        "live_db_sha256_after": live_after["sha256"],
        "live_db_stat_before": live_before["stat"],
        "live_db_stat_after": live_after["stat"],
        "live_db_checksum_unchanged": live_before["sha256"] == live_after["sha256"],
        "live_db_stat_unchanged": live_before["stat"] == live_after["stat"],
    }


def fetch_all(con: sqlite3.Connection, source_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(source_name)}")


def next_dwh_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH18_A",
            "next_step_name": "Manual evidence insertion for compound labels after direct dataset evidence is found",
            "prerequisite": "Direct controlled compound-label evidence has been found",
            "recommended_action": "Insert manual evidence decisions for compound labels in a separate controlled step.",
            "risk_level": "medium",
            "notes": "Use only direct compound-label or naming-convention evidence.",
        },
        {
            "next_step_id": "DWH18_B",
            "next_step_name": "Keep compound labels open and proceed to minimal design gate using supported components only",
            "prerequisite": "Compound labels remain open after DWH17A preparation",
            "recommended_action": "Use only supported component terms for any later bounded design gate.",
            "risk_level": "high",
            "notes": "No result tables yet.",
        },
        {
            "next_step_id": "DWH18_C",
            "next_step_name": "DBeaver inspection of compound label worklist",
            "prerequisite": "DWH17A views are queryable",
            "recommended_action": "Inspect DWH17A worklist, source strategy, and next-action views.",
            "risk_level": "low",
            "notes": "Recommended immediate audit step.",
        },
        {
            "next_step_id": "DWH18_D",
            "next_step_name": "Architecture checkpoint note before Shapiro-Mart design",
            "prerequisite": "Compound-label evidence boundary is clear",
            "recommended_action": "Document that component support exists while compound-label support remains open.",
            "risk_level": "low",
            "notes": "Useful before any design-gate planning.",
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
) -> dict[str, Any]:
    worklist_rows = fetch_all(con, "dwh17a_compound_label_followup_worklist")
    strategy_rows = fetch_all(con, "dwh17a_compound_label_source_strategy")
    template_rows = fetch_all(con, "dwh17a_compound_label_decision_template")
    dashboard_rows = fetch_all(con, "qsb_v_dwh17a_compound_label_dashboard")
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH controlled manual evidence follow-up preparation in workcopy only",
        "data_substrate_used": str(workcopy_db),
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "live_retrieval_performed": False,
        "raw_tim_par_files_read": False,
        "map_token_dictionary_updated": False,
        "compound_labels_in_scope": [row["compound_label"] for row in worklist_rows],
        "compound_label_count": len(worklist_rows),
        "component_support_status": COMPONENT_SUPPORT_STATUS,
        "worklist_rows": worklist_rows,
        "source_strategy_rows": strategy_rows,
        "decision_template_rows": template_rows,
        "dashboard_rows": dashboard_rows,
        "next_dwh_steps": next_dwh_steps_rows(),
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
            "supported_component_pairs": preflight["supported_component_pairs"],
            "compound_pairs": preflight["compound_pairs"],
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


def format_worklist_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {compound_label}: receiver={component_receiver_label}; backend={component_backend_label}; status={current_compound_status}; followup={manual_followup_status}".format(**row)
        for row in rows
    )


def format_strategy_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {compound_label}: category={preferred_source_category}; phrase={suggested_search_phrase}".format(**row)
        for row in rows
    )


def format_template_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {compound_label}: decisions={allowed_decision_status}".format(**row)
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
    return f"""# QSB-DWH17A Compound Label Evidence Follow-up Readout

## 1. Executive summary

Befund: DWH17A prepared a focused manual evidence follow-up layer for the two deferred compound labels only.

- Workcopy DB: `{summary['workcopy_db_path']}`
- Compound labels in scope: {summary['compound_label_count']}
- Worklist rows: {len(summary['worklist_rows'])}
- Source strategy rows: {len(summary['source_strategy_rows'])}
- Decision template rows: {len(summary['decision_template_rows'])}

## 2. Workcopy-only principle

DWH17A writes were limited to new DWH17A tables and views in the workcopy DB. It did not update DWH14A/DWH15A rows, supported component terms, or `map_token_dictionary`.

## 3. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH17A: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH17A: {live_status}

## 4. Compound labels in scope

{format_worklist_lines(summary['worklist_rows'])}

## 5. Component support versus compound support

{summary['component_support_status']}

## 6. Manual source strategy

{format_strategy_lines(summary['source_strategy_rows'])}

## 7. Decision template

{format_template_lines(summary['decision_template_rows'])}

## 8. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- Worklist count: {summary['validation']['worklist_count_status']}
- Source strategy count: {summary['validation']['source_strategy_count_status']}
- Decision template count: {summary['validation']['decision_template_count_status']}
- Non-compound row check: {summary['validation']['non_compound_row_status']}
- DWH14A/DWH15A preservation: {summary['validation']['preservation_status']}
- DWH17A views queryable: {summary['validation']['dwh17a_views_queryable']}

## 9. What DWH17_A does not do

DWH17A does not support the compound labels, does not update GUPPI/Rcvr_800/Rcvr1_2, does not update map_token_dictionary, does not perform live retrieval, does not read raw TIM/PAR files, does not create bridge/result tables, does not compute timing/model/statistical quantities, and does not make physical interpretation statements.

## 10. Recommended DWH18 options

{next_lines}

## 11. Claim boundary

{summary['claim_boundary']}
"""


def render_outputs(summary: dict[str, Any]) -> dict[str, str]:
    return {
        READOUT_MD: render_readout(summary),
        SUMMARY_JSON: pretty_json(summary) + "\n",
        WORKLIST_CSV: csv_text(
            [
                "compound_label",
                "token_position",
                "component_receiver_label",
                "component_backend_label",
                "component_support_status",
                "current_compound_status",
                "direct_evidence_need",
                "followup_priority",
                "manual_followup_status",
                "blocking_status",
                "notes",
            ],
            summary["worklist_rows"],
        ),
        SOURCE_STRATEGY_CSV: csv_text(
            [
                "compound_label",
                "preferred_source_category",
                "suggested_source_label",
                "suggested_search_phrase",
                "accept_criteria",
                "reject_criteria",
                "notes",
            ],
            summary["source_strategy_rows"],
        ),
        DECISION_TEMPLATE_CSV: csv_text(
            [
                "compound_label",
                "allowed_decision_status",
                "required_evidence_fields",
                "required_reviewer_note",
                "allowed_next_actions",
                "notes",
            ],
            summary["decision_template_rows"],
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
) -> dict[str, Any]:
    live_before = db_state(live_db)
    preflight = ensure_preconditions(live_db, workcopy_db, output_root, overwrite, allow_existing)
    created_at = utc_now()
    run_id = "DWH17A_COMPOUND_LABEL_EVIDENCE_FOLLOWUP_" + timestamp_for_id()
    output_texts: dict[str, str]

    con = connect_writable(workcopy_db)
    try:
        con.execute("BEGIN IMMEDIATE")
        create_tables(con, allow_existing)
        worklist_rows = build_worklist_rows(created_at)
        source_strategy_rows = build_source_strategy_rows(created_at)
        decision_template_rows = build_decision_template_rows(created_at)
        insert_rows(con, "dwh17a_compound_label_followup_worklist", worklist_rows)
        insert_rows(con, "dwh17a_compound_label_source_strategy", source_strategy_rows)
        insert_rows(con, "dwh17a_compound_label_decision_template", decision_template_rows)
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
            len(worklist_rows),
            len(source_strategy_rows),
            len(decision_template_rows),
            validation_before_log["workcopy_integrity_check"],
            validation_before_log["foreign_key_violation_count"],
        )
        validation = validate_workcopy(con, preflight, live_before, live_after)
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
        description="QSB-DWH17A compound-label manual evidence follow-up preparation."
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
        help="Existing output directory for DWH17A reports.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the six DWH17A report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH17A target objects; never appends to nonempty DWH17A tables.",
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
