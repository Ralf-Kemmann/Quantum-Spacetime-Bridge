#!/usr/bin/env python3
"""QSB-DWH13: manual evidence review preparation in the workcopy only.

This script creates a compact manual-review worklist for DWH12D open evidence
gaps. It uses only existing workcopy DB tables as input, performs no live
retrieval, and does not rewrite DWH08/DWH10/DWH11/DWH12D rows.
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


SCRIPT_NAME = "scripts/qsb_dwh13_manual_evidence_review.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh13_manual_evidence_review_readout.md"
SUMMARY_JSON = "dwh13_manual_evidence_review_summary.json"
WORKLIST_CSV = "dwh13_manual_evidence_worklist.csv"
SOURCE_STRATEGY_CSV = "dwh13_manual_source_strategy.csv"
DECISION_TEMPLATE_CSV = "dwh13_review_decision_template.csv"
NEXT_STEPS_CSV = "dwh13_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    WORKLIST_CSV,
    SOURCE_STRATEGY_CSV,
    DECISION_TEMPLATE_CSV,
    NEXT_STEPS_CSV,
]

DWH13_TABLES = [
    "dwh13_manual_evidence_worklist",
    "dwh13_manual_source_strategy",
    "dwh13_review_decision_template",
    "dwh13_manual_evidence_review_run_log",
]

DWH13_VIEWS = [
    "qsb_v_dwh13_manual_evidence_dashboard",
    "qsb_v_dwh13_high_priority_terms",
    "qsb_v_dwh13_review_decision_template",
    "qsb_v_dwh13_next_manual_actions",
]

REQUIRED_UPSTREAM_TABLES = [
    "dwh10_block_switch_mapping_refinement",
    "dwh11_external_evidence_verification",
    "dwh11_evidence_review_queue",
    "dwh12d_targeted_external_evidence_followup",
    "dwh12d_review_queue_update",
]

EXPECTED_OPEN_TERMS = [
    ("tim_token_007", "Rcvr_800"),
    ("tim_token_007", "Rcvr1_2"),
    ("tim_token_011", "GUPPI"),
    ("tim_token_011", "Rcvr_800_GUPPI"),
    ("tim_token_011", "Rcvr1_2_GUPPI"),
    ("tim_token_017", "J0740+6620.Rcvr_800.GUPPI.12y.x.sum.sm"),
    ("tim_token_017", "J0740+6620.Rcvr1_2.GUPPI.12y.x.sum.sm"),
    ("tim_token_013", "3.125"),
    ("tim_token_013", "12.5"),
    ("tim_token_023", "2"),
    ("tim_token_023", "8"),
]

HIGH_PRIORITY_TERMS = {
    "GUPPI",
    "Rcvr_800",
    "Rcvr1_2",
    "Rcvr_800_GUPPI",
    "Rcvr1_2_GUPPI",
}

MEDIUM_PRIORITY_TERMS = {
    "J0740+6620.Rcvr_800.GUPPI.12y.x.sum.sm",
    "J0740+6620.Rcvr1_2.GUPPI.12y.x.sum.sm",
    "3.125",
    "12.5",
}

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
    "keep_open_gap; prepare_candidate_status_update; mark_conflict_for_review; "
    "defer_manual_review"
)

CLAIM_BOUNDARY = (
    "DWH13 is a workcopy-only manual evidence review preparation layer for "
    "DWH12D open evidence gaps. It creates review worklist, source strategy, "
    "and decision-template rows only. It performs no live retrieval, does not "
    "read raw TIM/PAR files, does not create bridge/result tables, does not "
    "assign final semantic meaning to TIM columns, does not compute timing or "
    "model quantities, and does not make physical interpretation statements."
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


def dwh12d_digest(rows: list[dict[str, Any]]) -> str:
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
            "Refusing to overwrite existing DWH13 output file(s): "
            + "; ".join(existing)
        )


def fetch_dwh12d_snapshot(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT followup_id, token_position, term, proposed_role, dwh11_status,
               dwh12d_status, evidence_strength, source_label, source_url,
               source_type, retrieval_mode, retrieval_status, review_status, notes
        FROM dwh12d_targeted_external_evidence_followup
        ORDER BY followup_id
        """,
    )


def fetch_dwh12d_open_terms(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_position, term, proposed_role, dwh12d_status,
               evidence_strength, source_label, source_url, source_type,
               review_status, notes
        FROM dwh12d_targeted_external_evidence_followup
        WHERE dwh12d_status IN (
            'evidence_gap_open',
            'source_not_retrieved',
            'source_not_controlled_enough'
        )
        ORDER BY token_position, term
        """,
    )
    order = {pair: idx for idx, pair in enumerate(EXPECTED_OPEN_TERMS)}
    return sorted(
        rows,
        key=lambda row: order[(str(row["token_position"]), str(row["term"]))],
    )


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
        missing = [
            table for table in REQUIRED_UPSTREAM_TABLES
            if not object_exists(con, table, "table")
        ]
        if missing:
            raise RuntimeError("Missing upstream table(s): " + ", ".join(missing))
        dwh10_count = table_count(con, "dwh10_block_switch_mapping_refinement")
        dwh12d_snapshot = fetch_dwh12d_snapshot(con)
        open_rows = fetch_dwh12d_open_terms(con)
        existing_dwh13 = [
            name for name in [*DWH13_TABLES, *DWH13_VIEWS]
            if object_exists(con, name)
        ]
        existing_counts = {
            table: table_count(con, table)
            for table in DWH13_TABLES
            if object_exists(con, table, "table")
        }

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if dwh10_count != 5:
        raise RuntimeError(f"DWH10 refinement row count must be 5, got {dwh10_count}.")
    if not open_rows:
        raise RuntimeError("No DWH12D open gaps found.")
    expected_pairs = set(EXPECTED_OPEN_TERMS)
    actual_pairs = {
        (str(row["token_position"]), str(row["term"]))
        for row in open_rows
    }
    if actual_pairs != expected_pairs:
        raise RuntimeError("DWH12D open terms do not match expected DWH13 terms.")
    if existing_dwh13 and not allow_existing:
        raise RuntimeError(
            "DWH13 target object(s) already exist; rerun with --allow-existing "
            "only for controlled empty-object continuation: " + ", ".join(existing_dwh13)
        )
    nonempty_existing = [
        f"{table}={count}"
        for table, count in existing_counts.items()
        if count > 0
    ]
    if nonempty_existing:
        raise RuntimeError(
            "Refusing to append to nonempty DWH13 table(s): "
            + ", ".join(nonempty_existing)
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "dwh10_refinement_count": dwh10_count,
        "dwh12d_followup_count": len(dwh12d_snapshot),
        "dwh12d_open_term_count": len(open_rows),
        "dwh12d_snapshot_digest": dwh12d_digest(dwh12d_snapshot),
    }


def create_tables(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    statements = [
        f"""
        CREATE TABLE {clause}dwh13_manual_evidence_worklist (
            manual_review_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            proposed_role TEXT,
            dwh12d_status TEXT,
            evidence_priority TEXT NOT NULL,
            source_category TEXT NOT NULL,
            suggested_source_query TEXT,
            manual_review_status TEXT NOT NULL,
            blocking_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh13_manual_source_strategy (
            source_strategy_id TEXT PRIMARY KEY,
            term TEXT NOT NULL,
            preferred_source_category TEXT NOT NULL,
            source_priority TEXT NOT NULL,
            suggested_source_label TEXT,
            suggested_search_phrase TEXT,
            accept_criteria TEXT NOT NULL,
            reject_criteria TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh13_review_decision_template (
            review_template_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            allowed_decision_status TEXT NOT NULL,
            required_evidence_fields TEXT NOT NULL,
            required_reviewer_note TEXT NOT NULL,
            allowed_next_actions TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh13_manual_evidence_review_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            open_term_count INTEGER,
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
        CREATE VIEW {clause}qsb_v_dwh13_manual_evidence_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'dwh13_manual_evidence_review_run_log' AS metric_source,
               notes AS dashboard_note
        FROM dwh13_manual_evidence_review_run_log
        UNION ALL
        SELECT 'open_term_count',
               CAST(open_term_count AS TEXT),
               'dwh13_manual_evidence_review_run_log',
               'DWH12D open terms used for DWH13 manual-review preparation.'
        FROM dwh13_manual_evidence_review_run_log
        UNION ALL
        SELECT 'worklist_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh13_manual_evidence_worklist',
               'One manual-review worklist row per open term.'
        FROM dwh13_manual_evidence_worklist
        UNION ALL
        SELECT 'source_strategy_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh13_manual_source_strategy',
               'One source-strategy row per open term.'
        FROM dwh13_manual_source_strategy
        UNION ALL
        SELECT 'decision_template_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh13_review_decision_template',
               'One decision-template row per open term.'
        FROM dwh13_review_decision_template
        UNION ALL
        SELECT 'high_priority_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh13_manual_evidence_worklist',
               'Manual-review rows marked high priority.'
        FROM dwh13_manual_evidence_worklist
        WHERE evidence_priority = 'high'
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DWH13 insertions.'
        FROM dwh13_manual_evidence_review_run_log
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh13_high_priority_terms AS
        SELECT *
        FROM dwh13_manual_evidence_worklist
        WHERE evidence_priority = 'high'
        ORDER BY
            CASE term
                WHEN 'GUPPI' THEN 1
                WHEN 'Rcvr_800' THEN 2
                WHEN 'Rcvr1_2' THEN 3
                WHEN 'Rcvr_800_GUPPI' THEN 4
                WHEN 'Rcvr1_2_GUPPI' THEN 5
                ELSE 9
            END
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh13_review_decision_template AS
        SELECT
            t.review_template_id,
            t.token_position,
            t.term,
            w.evidence_priority,
            w.source_category,
            t.allowed_decision_status,
            t.required_evidence_fields,
            t.required_reviewer_note,
            t.allowed_next_actions,
            t.notes
        FROM dwh13_review_decision_template t
        JOIN dwh13_manual_evidence_worklist w
          ON w.token_position = t.token_position
         AND w.term = t.term
        ORDER BY
            CASE w.evidence_priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            t.token_position,
            t.term
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh13_next_manual_actions AS
        SELECT
            w.manual_review_id AS action_id,
            w.token_position,
            w.term,
            w.evidence_priority,
            w.source_category,
            s.suggested_source_label,
            s.suggested_search_phrase,
            w.manual_review_status,
            w.blocking_status,
            'Collect controlled source evidence and record one allowed decision status.' AS next_action
        FROM dwh13_manual_evidence_worklist w
        JOIN dwh13_manual_source_strategy s
          ON s.term = w.term
        ORDER BY
            CASE w.evidence_priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END,
            w.token_position,
            w.term
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


def evidence_priority(term: str) -> str:
    if term in HIGH_PRIORITY_TERMS:
        return "high"
    if term in MEDIUM_PRIORITY_TERMS:
        return "medium"
    return "low_context"


def source_category(term: str, proposed_role: str | None) -> str:
    if term == "GUPPI":
        return "official_backend_documentation"
    if term.startswith("Rcvr") and "GUPPI" in term:
        return "official_backend_documentation"
    if term.startswith("Rcvr"):
        return "official_receiver_documentation"
    if term.startswith("J0740+6620"):
        return "pulsar_timing_release_notes"
    if term in {"3.125", "12.5"}:
        return "data_format_or_pipeline_documentation"
    role = str(proposed_role or "")
    if role == "numeric_configuration_state_candidate":
        return "institutional_dataset_documentation"
    return "institutional_dataset_documentation"


def suggested_source_label(term: str, category: str) -> str:
    if category in {"official_receiver_documentation", "official_backend_documentation"}:
        return "Green Bank Observatory / GBT official receiver and backend documentation"
    if category == "pulsar_timing_release_notes":
        return "NANOGrav or IPTA official release notes for the relevant J0740+6620 product"
    if category == "data_format_or_pipeline_documentation":
        return "Institutional pulsar timing data format or processing documentation"
    return "Official dataset release documentation from IPTA, NANOGrav, or institutional archive"


def suggested_search_phrase(term: str, category: str) -> str:
    if category == "official_receiver_documentation":
        return f"{term} GBT receiver official documentation"
    if category == "official_backend_documentation":
        return f"{term} GBT backend GUPPI official documentation"
    if category == "pulsar_timing_release_notes":
        return f"{term} official pulsar timing release notes"
    if category == "data_format_or_pipeline_documentation":
        return f"{term} pulsar timing data format pipeline metadata official documentation"
    return f"{term} official dataset release metadata"


def accept_criteria(category: str) -> str:
    base = "Controlled source clearly links the term to the proposed role as a candidate mapping context."
    if category == "official_receiver_documentation":
        return base + " Receiver naming or receiver-band usage must be explicit."
    if category == "official_backend_documentation":
        return base + " Backend/GUPPI naming or receiver-backend combined usage must be explicit."
    if category == "pulsar_timing_release_notes":
        return base + " Release-product or file-label usage must be explicit."
    if category == "data_format_or_pipeline_documentation":
        return base + " Numeric field role must be documented as metadata or pipeline configuration."
    return base + " Dataset-state meaning must be documented by an institutional source."


def reject_criteria() -> str:
    return (
        "Unsupported page, informal mention, term-only hit without role context, "
        "or source that cannot be tied to an institutional documentation source."
    )


def build_worklist_rows(
    open_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(open_rows, start=1):
        term = str(row["term"])
        category = source_category(term, row.get("proposed_role"))
        rows.append(
            {
                "manual_review_id": f"dwh13_manual_review_{idx:03d}",
                "token_position": row["token_position"],
                "term": term,
                "proposed_role": row["proposed_role"],
                "dwh12d_status": row["dwh12d_status"],
                "evidence_priority": evidence_priority(term),
                "source_category": category,
                "suggested_source_query": suggested_search_phrase(term, category),
                "manual_review_status": "pending_manual_review",
                "blocking_status": "blocks_semantic_promotion",
                "created_at_utc": created_at,
                "notes": "DWH13 worklist only; no source was retrieved and no support was assigned.",
            }
        )
    return rows


def build_source_strategy_rows(open_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(open_rows, start=1):
        term = str(row["term"])
        category = source_category(term, row.get("proposed_role"))
        priority = evidence_priority(term)
        rows.append(
            {
                "source_strategy_id": f"dwh13_source_strategy_{idx:03d}",
                "term": term,
                "preferred_source_category": category,
                "source_priority": priority,
                "suggested_source_label": suggested_source_label(term, category),
                "suggested_search_phrase": suggested_search_phrase(term, category),
                "accept_criteria": accept_criteria(category),
                "reject_criteria": reject_criteria(),
                "notes": "Manual reviewer must record controlled source reference before changing evidence status.",
            }
        )
    return rows


def build_decision_template_rows(open_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(open_rows, start=1):
        rows.append(
            {
                "review_template_id": f"dwh13_review_template_{idx:03d}",
                "token_position": row["token_position"],
                "term": row["term"],
                "allowed_decision_status": ALLOWED_DECISION_STATUS,
                "required_evidence_fields": REQUIRED_EVIDENCE_FIELDS,
                "required_reviewer_note": (
                    "Reviewer must state why the controlled source supports, leaves open, "
                    "conflicts with, or defers the candidate role."
                ),
                "allowed_next_actions": ALLOWED_NEXT_ACTIONS,
                "notes": "Template constrains manual review decisions; it does not apply a decision.",
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
    open_term_count: int,
    worklist_row_count: int,
    source_strategy_row_count: int,
    decision_template_row_count: int,
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh13_manual_evidence_review_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            open_term_count,
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
            "workcopy_manual_evidence_review_preparation",
            1 if live_modified else 0,
            1,
            open_term_count,
            worklist_row_count,
            source_strategy_row_count,
            decision_template_row_count,
            integrity,
            fk_count,
            "DWH13 creates manual review structures only; no evidence support assigned.",
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
    dwh12d_snapshot = fetch_dwh12d_snapshot(con)
    digest_after = dwh12d_digest(dwh12d_snapshot)
    dwh13_counts = {table: table_count(con, table) for table in DWH13_TABLES}
    view_counts = {
        view: table_count(con, view)
        for view in DWH13_VIEWS
        if object_exists(con, view, "view")
    }
    return {
        "workcopy_integrity_check": integrity,
        "workcopy_foreign_key_violations": fk_violations,
        "foreign_key_violation_count": len(fk_violations),
        "dwh12d_followup_count_before": preflight["dwh12d_followup_count"],
        "dwh12d_followup_count_after": len(dwh12d_snapshot),
        "dwh12d_snapshot_digest_before": preflight["dwh12d_snapshot_digest"],
        "dwh12d_snapshot_digest_after": digest_after,
        "dwh12d_preservation_status": (
            "passed" if digest_after == preflight["dwh12d_snapshot_digest"] else "failed"
        ),
        "dwh13_table_counts": dwh13_counts,
        "dwh13_expected_counts_status": (
            "passed"
            if dwh13_counts["dwh13_manual_evidence_worklist"] == 11
            and dwh13_counts["dwh13_manual_source_strategy"] == 11
            and dwh13_counts["dwh13_review_decision_template"] == 11
            else "failed"
        ),
        "dwh13_view_counts": view_counts,
        "dwh13_views_queryable": len(view_counts) == len(DWH13_VIEWS),
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
            "next_step_id": "DWH14_A",
            "next_step_name": "Manual evidence insertion for high-priority terms after human review",
            "prerequisite": "Reviewer has controlled source notes for high-priority terms",
            "recommended_action": "Insert manual evidence decisions in a separate controlled workcopy step.",
            "risk_level": "medium",
            "notes": "Recommended next step because DWH13 only prepares the worklist.",
        },
        {
            "next_step_id": "DWH14_B",
            "next_step_name": "DBeaver-assisted manual review session and reviewer notes",
            "prerequisite": "DWH13 worklist and decision-template views are queryable",
            "recommended_action": "Use the DWH13 views to guide human review and note capture.",
            "risk_level": "low",
            "notes": "Good companion step for manual inspection.",
        },
        {
            "next_step_id": "DWH14_C",
            "next_step_name": "Controlled update of mapping review statuses after evidence entry",
            "prerequisite": "Manual evidence decisions have been inserted and reviewed",
            "recommended_action": "Update only mapping review status, and only for candidate-supported terms.",
            "risk_level": "medium",
            "notes": "Not applicable before evidence entries exist.",
        },
        {
            "next_step_id": "DWH14_D",
            "next_step_name": "Shapiro-Mart design after supported/open/conflict separation",
            "prerequisite": "Candidates are separated into supported, open, and conflict groups",
            "recommended_action": "Defer design until evidence decisions exist.",
            "risk_level": "high",
            "notes": "DWH13 does not support design work.",
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
    worklist_rows = fetch_all(con, "dwh13_manual_evidence_worklist")
    source_rows = fetch_all(con, "dwh13_manual_source_strategy")
    template_rows = fetch_all(con, "dwh13_review_decision_template")
    dashboard_rows = fetch_all(con, "qsb_v_dwh13_manual_evidence_dashboard")
    high_rows = fetch_all(con, "qsb_v_dwh13_high_priority_terms")
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH manual evidence review preparation in workcopy only",
        "data_substrate_used": str(workcopy_db),
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "internet_retrieval_performed": False,
        "raw_tim_par_files_read": False,
        "report_outputs_used_as_input": False,
        "new_isolated_analysis_db_created": False,
        "bridge_or_result_tables_created": False,
        "manual_review_terms": worklist_rows,
        "manual_review_term_count": len(worklist_rows),
        "high_priority_terms": high_rows,
        "high_priority_count": len(high_rows),
        "source_strategy_rows": source_rows,
        "source_strategy_row_count": len(source_rows),
        "decision_template_rows": template_rows,
        "decision_template_row_count": len(template_rows),
        "dashboard_rows": dashboard_rows,
        "next_dwh_steps": next_dwh_steps_rows(),
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
            "dwh10_refinement_count": preflight["dwh10_refinement_count"],
            "dwh12d_followup_count": preflight["dwh12d_followup_count"],
            "dwh12d_open_term_count": preflight["dwh12d_open_term_count"],
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
        "- {token_position}: {term}; priority={evidence_priority}; category={source_category}; status={manual_review_status}".format(**row)
        for row in rows
    )


def format_strategy_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {term}: category={preferred_source_category}; source={suggested_source_label}".format(**row)
        for row in rows
    )


def format_template_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; statuses={allowed_decision_status}".format(**row)
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
    return f"""# QSB-DWH13 Manual Evidence Review Readout

## 1. Executive summary

Befund: DWH13 created a manual evidence review preparation layer for the 11 DWH12D open evidence-gap terms.

- Run ID: `{summary['run_id']}`
- Workcopy DB: `{summary['workcopy_db_path']}`
- Manual review terms: {summary['manual_review_term_count']}
- High-priority terms: {summary['high_priority_count']}
- Source strategy rows: {summary['source_strategy_row_count']}
- Decision template rows: {summary['decision_template_row_count']}

## 2. Workcopy-only principle

DWH13 writes were limited to new DWH13 tables in the workcopy DB. DWH10, DWH11, and DWH12D rows were not rewritten.

## 3. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH13: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH13: {live_status}

## 4. Manual review scope

{format_worklist_lines(summary['manual_review_terms'])}

## 5. High-priority terms

{format_worklist_lines(summary['high_priority_terms'])}

## 6. Source strategy

{format_strategy_lines(summary['source_strategy_rows'])}

## 7. Review decision template

{format_template_lines(summary['decision_template_rows'])}

## 8. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- DWH12D followup rows preserved: {summary['validation']['dwh12d_preservation_status']}
- DWH13 expected row counts: {summary['validation']['dwh13_expected_counts_status']}
- DWH13 views queryable: {summary['validation']['dwh13_views_queryable']}

## 9. What DWH13 does not do

DWH13 does not perform live internet retrieval, does not read raw TIM/PAR files, does not use CSV/JSON/MD report outputs as input, does not create a new isolated analysis DB, does not create bridge/result tables, does not assign final semantic meaning to TIM columns, does not compute timing/model/statistical quantities, and does not make physical interpretation statements.

## 10. Recommended DWH14 options

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
                "token_position",
                "term",
                "proposed_role",
                "evidence_priority",
                "source_category",
                "suggested_source_query",
                "manual_review_status",
                "blocking_status",
                "notes",
            ],
            summary["manual_review_terms"],
        ),
        SOURCE_STRATEGY_CSV: csv_text(
            [
                "term",
                "preferred_source_category",
                "source_priority",
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
                "token_position",
                "term",
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
    preflight = ensure_preconditions(
        live_db,
        workcopy_db,
        output_root,
        overwrite,
        allow_existing,
    )
    created_at = utc_now()
    run_id = "DWH13_MANUAL_EVIDENCE_REVIEW_" + timestamp_for_id()
    output_texts: dict[str, str]

    con = connect_writable(workcopy_db)
    try:
        con.execute("BEGIN IMMEDIATE")
        create_tables(con, allow_existing)
        open_rows = fetch_dwh12d_open_terms(con)
        worklist_rows = build_worklist_rows(open_rows, created_at)
        source_strategy_rows = build_source_strategy_rows(open_rows)
        decision_template_rows = build_decision_template_rows(open_rows)
        insert_rows(con, "dwh13_manual_evidence_worklist", worklist_rows)
        insert_rows(con, "dwh13_manual_source_strategy", source_strategy_rows)
        insert_rows(con, "dwh13_review_decision_template", decision_template_rows)
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
            len(open_rows),
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
        description="QSB-DWH13 manual evidence review preparation for DWH12D open terms."
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
        help="Existing output directory for DWH13 reports.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the six DWH13 report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH13 target objects; never appends to nonempty DWH13 tables.",
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
