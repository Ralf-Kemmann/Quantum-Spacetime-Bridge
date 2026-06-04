#!/usr/bin/env python3
"""QSB-DWH14A: controlled manual evidence insertion in the workcopy.

The default execution requires an explicit human-reviewed CSV input file. If
the input file is missing, no database writes occur. Template mode creates only
the manual evidence CSV template and never creates DWH14A database objects.
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


SCRIPT_NAME = "scripts/qsb_dwh14a_manual_evidence_insertion.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")
DEFAULT_MANUAL_EVIDENCE_CSV = Path(
    "data/QSB-ST-SHAPIROINFO/manual_evidence/"
    "dwh14a_high_priority_manual_evidence.csv"
)

MISSING_INPUT_MESSAGE = (
    "Manual evidence input file missing. DWH14_A requires human-reviewed evidence before insertion."
)

READOUT_MD = "dwh14a_manual_evidence_insertion_readout.md"
SUMMARY_JSON = "dwh14a_manual_evidence_insertion_summary.json"
INSERTED_CSV = "dwh14a_inserted_manual_evidence.csv"
REJECTED_CSV = "dwh14a_rejected_manual_evidence_rows.csv"
PREVIEW_CSV = "dwh14a_mapping_review_status_preview.csv"
NEXT_STEPS_CSV = "dwh14a_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    INSERTED_CSV,
    REJECTED_CSV,
    PREVIEW_CSV,
    NEXT_STEPS_CSV,
]

DWH14A_TABLES = [
    "dwh14a_manual_evidence_decision",
    "dwh14a_manual_evidence_rejection_log",
    "dwh14a_manual_evidence_insertion_run_log",
]

DWH14A_VIEWS = [
    "qsb_v_dwh14a_manual_evidence_dashboard",
    "qsb_v_dwh14a_high_priority_decision_status",
    "qsb_v_dwh14a_supported_candidate_terms",
    "qsb_v_dwh14a_open_or_conflict_terms",
    "qsb_v_dwh14a_next_review_actions",
]

REQUIRED_UPSTREAM_TABLES = [
    "dwh13_manual_evidence_worklist",
    "dwh13_manual_source_strategy",
    "dwh13_review_decision_template",
    "dwh12d_targeted_external_evidence_followup",
    "dwh12d_review_queue_update",
    "dwh10_block_switch_mapping_refinement",
]

REQUIRED_INPUT_FIELDS = [
    "token_position",
    "term",
    "proposed_role",
    "decision_status",
    "evidence_strength",
    "source_label",
    "source_url_or_local_reference",
    "evidence_summary",
    "access_or_review_date",
    "reviewer_note",
    "reviewer_name_or_initials",
    "next_action",
]

ALLOWED_DECISION_STATUS = {
    "evidence_supported_candidate",
    "evidence_gap_open",
    "evidence_conflict_or_mismatch",
    "source_not_controlled_enough",
    "manual_review_deferred",
}

ALLOWED_EVIDENCE_STRENGTH = {
    "strong",
    "moderate",
    "weak",
    "none_or_insufficient",
    "conflict",
}

ALLOWED_NEXT_ACTION = {
    "keep_candidate_open",
    "promote_to_evidence_supported_candidate",
    "keep_as_evidence_gap",
    "mark_conflict_for_review",
    "defer_review",
    "request_additional_source",
}

FORBIDDEN_LOWER_SUBSTRINGS = {
    "final_verified_semantics",
    "proven",
    "validated",
    "validated_physics",
    "confirms_bridge",
    "bridge_confirmed",
    "physical_evidence",
    "shapiro_confirmed",
    "bridge" + " confirmed",
    "final" + " verified" + " semantics",
    "physical" + " evidence",
}

CLAIM_BOUNDARY = (
    "DWH14A is a workcopy-only controlled insertion layer for explicit "
    "human-reviewed evidence decisions on DWH13 high-priority terms. It does "
    "not perform live retrieval, automatic evidence verification, final "
    "semantic assignment, Bridge/result modeling, or physics analysis. It does "
    "not rewrite DWH10/DWH12D/DWH13 rows by default; it records decisions and "
    "preview views only."
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
            "Refusing to overwrite existing DWH14A output file(s): "
            + "; ".join(existing)
        )


def fetch_high_priority_terms(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT token_position, term, proposed_role, evidence_priority,
               source_category, manual_review_status, blocking_status
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
    )


def fetch_table_snapshot(con: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(table_name)} ORDER BY 1")


def ensure_template_preconditions(live_db: Path, workcopy_db: Path, output_root: Path) -> dict[str, Any]:
    ensure_path_preconditions(live_db, workcopy_db, output_root)
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
        if not object_exists(con, "dwh13_manual_evidence_worklist", "table"):
            raise RuntimeError("Missing DWH13 worklist table.")
        high_terms = fetch_high_priority_terms(con)
    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if len(high_terms) != 5:
        raise RuntimeError(f"Expected 5 high-priority DWH13 terms, got {len(high_terms)}.")
    return {"high_terms": high_terms}


def ensure_preconditions(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    manual_evidence_csv: Path,
    overwrite: bool,
    allow_existing: bool,
) -> dict[str, Any]:
    ensure_path_preconditions(live_db, workcopy_db, output_root)
    ensure_no_outputs(output_root, overwrite)
    if not manual_evidence_csv.exists():
        raise FileNotFoundError(MISSING_INPUT_MESSAGE)
    if not manual_evidence_csv.is_file():
        raise ValueError(f"Manual evidence input path is not a file: {manual_evidence_csv}")
    if manual_evidence_csv.stat().st_size == 0:
        raise ValueError(f"Manual evidence input file is empty: {manual_evidence_csv}")

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
        high_terms = fetch_high_priority_terms(con)
        snapshots = {
            "dwh10_block_switch_mapping_refinement": fetch_table_snapshot(
                con, "dwh10_block_switch_mapping_refinement"
            ),
            "dwh12d_targeted_external_evidence_followup": fetch_table_snapshot(
                con, "dwh12d_targeted_external_evidence_followup"
            ),
            "dwh13_manual_evidence_worklist": fetch_table_snapshot(
                con, "dwh13_manual_evidence_worklist"
            ),
        }
        existing_dwh14a = [
            name for name in [*DWH14A_TABLES, *DWH14A_VIEWS]
            if object_exists(con, name)
        ]
        existing_counts = {
            table: table_count(con, table)
            for table in DWH14A_TABLES
            if object_exists(con, table, "table")
        }

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if len(high_terms) != 5:
        raise RuntimeError(f"Expected 5 high-priority DWH13 terms, got {len(high_terms)}.")
    if existing_dwh14a and not allow_existing:
        raise RuntimeError(
            "DWH14A target object(s) already exist; rerun with --allow-existing "
            "only for controlled empty-object continuation: " + ", ".join(existing_dwh14a)
        )
    nonempty_existing = [
        f"{table}={count}"
        for table, count in existing_counts.items()
        if count > 0
    ]
    if nonempty_existing:
        raise RuntimeError(
            "Refusing to append to nonempty DWH14A table(s): "
            + ", ".join(nonempty_existing)
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "high_terms": high_terms,
        "upstream_counts": {name: len(rows) for name, rows in snapshots.items()},
        "upstream_digests": {name: stable_digest(rows) for name, rows in snapshots.items()},
    }


def write_template(manual_evidence_csv: Path, high_terms: list[dict[str, Any]]) -> None:
    if manual_evidence_csv.exists():
        raise FileExistsError(f"Manual evidence template already exists: {manual_evidence_csv}")
    manual_evidence_csv.parent.mkdir(parents=True, exist_ok=True)
    with manual_evidence_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUIRED_INPUT_FIELDS)
        writer.writeheader()
        for row in high_terms:
            writer.writerow(
                {
                    "token_position": row["token_position"],
                    "term": row["term"],
                    "proposed_role": row["proposed_role"],
                    "decision_status": "manual_review_deferred",
                    "evidence_strength": "none_or_insufficient",
                    "source_label": "",
                    "source_url_or_local_reference": "",
                    "evidence_summary": "",
                    "access_or_review_date": "",
                    "reviewer_note": "",
                    "reviewer_name_or_initials": "",
                    "next_action": "defer_review",
                }
            )


def create_template(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    manual_evidence_csv: Path,
) -> dict[str, Any]:
    live_before = db_state(live_db)
    work_before = db_state(workcopy_db)
    preflight = ensure_template_preconditions(live_db, workcopy_db, output_root)
    write_template(manual_evidence_csv, preflight["high_terms"])
    live_after = db_state(live_db)
    work_after = db_state(workcopy_db)
    return {
        "template_created": True,
        "manual_evidence_csv": str(manual_evidence_csv),
        "template_row_count": len(preflight["high_terms"]),
        "live_db_checksum_unchanged": live_before["sha256"] == live_after["sha256"],
        "live_db_stat_unchanged": live_before["stat"] == live_after["stat"],
        "workcopy_db_checksum_unchanged": work_before["sha256"] == work_after["sha256"],
        "workcopy_db_stat_unchanged": work_before["stat"] == work_after["stat"],
        "notes": "Template mode created only the manual evidence CSV; no DB writes were performed.",
    }


def create_tables(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    statements = [
        f"""
        CREATE TABLE {clause}dwh14a_manual_evidence_decision (
            manual_evidence_decision_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            proposed_role TEXT,
            decision_status TEXT NOT NULL,
            evidence_strength TEXT NOT NULL,
            source_label TEXT NOT NULL,
            source_url_or_local_reference TEXT NOT NULL,
            evidence_summary TEXT NOT NULL,
            access_or_review_date TEXT NOT NULL,
            reviewer_note TEXT NOT NULL,
            reviewer_name_or_initials TEXT NOT NULL,
            next_action TEXT NOT NULL,
            inserted_at_utc TEXT NOT NULL,
            source_input_file TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh14a_manual_evidence_rejection_log (
            rejection_id TEXT PRIMARY KEY,
            token_position TEXT,
            term TEXT,
            rejection_reason TEXT NOT NULL,
            raw_row_json TEXT,
            rejected_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh14a_manual_evidence_insertion_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            manual_input_file TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            input_row_count INTEGER,
            inserted_decision_count INTEGER,
            rejected_row_count INTEGER,
            supported_candidate_count INTEGER,
            open_gap_count INTEGER,
            conflict_count INTEGER,
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
        CREATE VIEW {clause}qsb_v_dwh14a_manual_evidence_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'dwh14a_manual_evidence_insertion_run_log' AS metric_source,
               notes AS dashboard_note
        FROM dwh14a_manual_evidence_insertion_run_log
        UNION ALL
        SELECT 'input_row_count',
               CAST(input_row_count AS TEXT),
               'dwh14a_manual_evidence_insertion_run_log',
               'Manual evidence CSV rows read.'
        FROM dwh14a_manual_evidence_insertion_run_log
        UNION ALL
        SELECT 'inserted_decision_count',
               CAST(inserted_decision_count AS TEXT),
               'dwh14a_manual_evidence_insertion_run_log',
               'Rows accepted into DWH14A manual evidence decisions.'
        FROM dwh14a_manual_evidence_insertion_run_log
        UNION ALL
        SELECT 'rejected_row_count',
               CAST(rejected_row_count AS TEXT),
               'dwh14a_manual_evidence_insertion_run_log',
               'Rows rejected before decision insertion.'
        FROM dwh14a_manual_evidence_insertion_run_log
        UNION ALL
        SELECT 'supported_candidate_count',
               CAST(supported_candidate_count AS TEXT),
               'dwh14a_manual_evidence_insertion_run_log',
               'Accepted rows with candidate support status.'
        FROM dwh14a_manual_evidence_insertion_run_log
        UNION ALL
        SELECT 'open_gap_count',
               CAST(open_gap_count AS TEXT),
               'dwh14a_manual_evidence_insertion_run_log',
               'Accepted rows that remain open or deferred.'
        FROM dwh14a_manual_evidence_insertion_run_log
        UNION ALL
        SELECT 'conflict_count',
               CAST(conflict_count AS TEXT),
               'dwh14a_manual_evidence_insertion_run_log',
               'Accepted conflict rows.'
        FROM dwh14a_manual_evidence_insertion_run_log
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DWH14A insertions.'
        FROM dwh14a_manual_evidence_insertion_run_log
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh14a_high_priority_decision_status AS
        SELECT
            w.token_position,
            w.term,
            w.proposed_role,
            w.manual_review_status AS dwh13_manual_review_status,
            w.blocking_status AS dwh13_blocking_status,
            d.decision_status AS dwh14a_decision_status,
            d.evidence_strength,
            d.source_label,
            d.next_action,
            CASE
                WHEN d.decision_status = 'evidence_supported_candidate'
                 AND d.next_action = 'promote_to_evidence_supported_candidate'
                THEN 'candidate_supported_review_ready'
                WHEN d.decision_status = 'evidence_conflict_or_mismatch'
                THEN 'conflict_review_required'
                WHEN d.decision_status IS NULL
                THEN 'no_manual_decision_inserted'
                ELSE 'manual_review_open'
            END AS proposed_next_mapping_status,
            CASE
                WHEN d.decision_status = 'evidence_supported_candidate'
                 AND d.next_action = 'promote_to_evidence_supported_candidate'
                THEN 1 ELSE 0
            END AS safe_to_promote,
            d.notes
        FROM dwh13_manual_evidence_worklist w
        LEFT JOIN dwh14a_manual_evidence_decision d
          ON d.token_position = w.token_position
         AND d.term = w.term
        WHERE w.evidence_priority = 'high'
        ORDER BY
            CASE w.term
                WHEN 'GUPPI' THEN 1
                WHEN 'Rcvr_800' THEN 2
                WHEN 'Rcvr1_2' THEN 3
                WHEN 'Rcvr_800_GUPPI' THEN 4
                WHEN 'Rcvr1_2_GUPPI' THEN 5
                ELSE 9
            END
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh14a_supported_candidate_terms AS
        SELECT *
        FROM dwh14a_manual_evidence_decision
        WHERE decision_status = 'evidence_supported_candidate'
        ORDER BY token_position, term
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh14a_open_or_conflict_terms AS
        SELECT *
        FROM dwh14a_manual_evidence_decision
        WHERE decision_status IN (
            'evidence_gap_open',
            'evidence_conflict_or_mismatch',
            'source_not_controlled_enough',
            'manual_review_deferred'
        )
        ORDER BY token_position, term
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh14a_next_review_actions AS
        SELECT
            token_position,
            term,
            decision_status,
            evidence_strength,
            next_action,
            CASE
                WHEN decision_status = 'evidence_supported_candidate'
                 AND next_action = 'promote_to_evidence_supported_candidate'
                THEN 'Prepare controlled mapping review status update in DWH15.'
                WHEN decision_status = 'evidence_conflict_or_mismatch'
                THEN 'Review conflict before any mapping status update.'
                WHEN decision_status = 'manual_review_deferred'
                THEN 'Continue manual review before insertion can affect mapping review.'
                ELSE 'Keep candidate open or request additional source review.'
            END AS recommended_next_action,
            notes
        FROM dwh14a_manual_evidence_decision
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


def row_contains_forbidden_text(row: dict[str, str]) -> str | None:
    combined = " ".join(str(value or "") for value in row.values()).lower()
    for forbidden in sorted(FORBIDDEN_LOWER_SUBSTRINGS):
        if forbidden in combined:
            return forbidden
    return None


def normalize_row(row: dict[str, Any]) -> dict[str, str]:
    return {key: str(value or "").strip() for key, value in row.items()}


def read_manual_input(path: Path) -> tuple[list[dict[str, str]], list[dict[str, Any]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("Manual evidence input file has no header row.")
        missing_fields = [field for field in REQUIRED_INPUT_FIELDS if field not in reader.fieldnames]
        if missing_fields:
            raise ValueError(
                "Manual evidence input file lacks required field(s): "
                + ", ".join(missing_fields)
            )
        raw_rows = [normalize_row(row) for row in reader]
    if not raw_rows:
        raise ValueError("Manual evidence input file has no data rows.")

    high_pair_order = {pair: idx for idx, pair in enumerate([
        ("tim_token_011", "GUPPI"),
        ("tim_token_007", "Rcvr_800"),
        ("tim_token_007", "Rcvr1_2"),
        ("tim_token_011", "Rcvr_800_GUPPI"),
        ("tim_token_011", "Rcvr1_2_GUPPI"),
    ])}
    sorted_rows = sorted(
        raw_rows,
        key=lambda row: high_pair_order.get(
            (row.get("token_position", ""), row.get("term", "")),
            99,
        ),
    )
    return sorted_rows, raw_rows


def validate_manual_rows(
    rows: list[dict[str, str]],
    high_terms: list[dict[str, Any]],
    created_at: str,
    source_input_file: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    high_by_pair = {
        (str(row["token_position"]), str(row["term"])): row
        for row in high_terms
    }
    inserted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    seen_pairs: set[tuple[str, str]] = set()
    for idx, row in enumerate(rows, start=1):
        reasons: list[str] = []
        pair = (row.get("token_position", ""), row.get("term", ""))
        if pair not in high_by_pair:
            reasons.append("term_not_in_dwh13_high_priority_worklist")
        elif pair in seen_pairs:
            reasons.append("duplicate_high_priority_term")
        else:
            seen_pairs.add(pair)
        for field in REQUIRED_INPUT_FIELDS:
            if not row.get(field):
                reasons.append(f"missing_required_value:{field}")
        if row.get("decision_status") not in ALLOWED_DECISION_STATUS:
            reasons.append("decision_status_not_allowed")
        if row.get("evidence_strength") not in ALLOWED_EVIDENCE_STRENGTH:
            reasons.append("evidence_strength_not_allowed")
        if row.get("next_action") not in ALLOWED_NEXT_ACTION:
            reasons.append("next_action_not_allowed")
        forbidden = row_contains_forbidden_text(row)
        if forbidden:
            reasons.append(f"forbidden_text:{forbidden}")
        if (
            row.get("decision_status") == "evidence_supported_candidate"
            and row.get("next_action") != "promote_to_evidence_supported_candidate"
        ):
            reasons.append("supported_candidate_requires_promotion_preview_action")
        if (
            row.get("decision_status") != "evidence_supported_candidate"
            and row.get("next_action") == "promote_to_evidence_supported_candidate"
        ):
            reasons.append("promotion_preview_action_requires_supported_candidate_status")
        if reasons:
            rejected.append(
                {
                    "rejection_id": f"dwh14a_rejection_{idx:03d}",
                    "token_position": row.get("token_position"),
                    "term": row.get("term"),
                    "rejection_reason": "; ".join(reasons),
                    "raw_row_json": pretty_json(row),
                    "rejected_at_utc": created_at,
                    "notes": "Rejected before DB decision insertion.",
                }
            )
            continue
        inserted.append(
            {
                "manual_evidence_decision_id": f"dwh14a_manual_evidence_decision_{len(inserted) + 1:03d}",
                "token_position": row["token_position"],
                "term": row["term"],
                "proposed_role": row["proposed_role"],
                "decision_status": row["decision_status"],
                "evidence_strength": row["evidence_strength"],
                "source_label": row["source_label"],
                "source_url_or_local_reference": row["source_url_or_local_reference"],
                "evidence_summary": row["evidence_summary"],
                "access_or_review_date": row["access_or_review_date"],
                "reviewer_note": row["reviewer_note"],
                "reviewer_name_or_initials": row["reviewer_name_or_initials"],
                "next_action": row["next_action"],
                "inserted_at_utc": created_at,
                "source_input_file": str(source_input_file),
                "notes": "Manual evidence decision inserted as candidate evidence status only.",
            }
        )
    if rejected:
        raise ValueError(
            "Manual evidence input contains rejected row(s); refusing DB writes. "
            + f"Rejected count: {len(rejected)}."
        )
    if not inserted:
        raise ValueError("Manual evidence input yielded no insertable rows.")
    return inserted, rejected


def status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    supported = sum(1 for row in rows if row["decision_status"] == "evidence_supported_candidate")
    conflict = sum(1 for row in rows if row["decision_status"] == "evidence_conflict_or_mismatch")
    open_gap = sum(
        1 for row in rows
        if row["decision_status"] in {
            "evidence_gap_open",
            "source_not_controlled_enough",
            "manual_review_deferred",
        }
    )
    return {
        "supported_candidate_count": supported,
        "open_gap_count": open_gap,
        "conflict_count": conflict,
    }


def insert_run_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    manual_input_file: Path,
    live_modified: bool,
    input_row_count: int,
    inserted_count: int,
    rejected_count: int,
    counts: dict[str, int],
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh14a_manual_evidence_insertion_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            manual_input_file,
            live_db_modified,
            workcopy_db_modified,
            input_row_count,
            inserted_decision_count,
            rejected_row_count,
            supported_candidate_count,
            open_gap_count,
            conflict_count,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(live_db),
            str(workcopy_db),
            SCRIPT_NAME,
            "workcopy_controlled_manual_evidence_insertion",
            str(manual_input_file),
            1 if live_modified else 0,
            1,
            input_row_count,
            inserted_count,
            rejected_count,
            counts["supported_candidate_count"],
            counts["open_gap_count"],
            counts["conflict_count"],
            integrity,
            fk_count,
            "DWH14A inserted manual evidence decisions; upstream rows were not rewritten.",
        ),
    )


def validate_workcopy(
    con: sqlite3.Connection,
    preflight: dict[str, Any],
    live_before: dict[str, Any],
    live_after: dict[str, Any],
    input_row_count: int,
    inserted_count: int,
    rejected_count: int,
) -> dict[str, Any]:
    integrity = integrity_check(con)
    fk_violations = foreign_key_violations(con)
    upstream_after = {
        "dwh10_block_switch_mapping_refinement": fetch_table_snapshot(
            con, "dwh10_block_switch_mapping_refinement"
        ),
        "dwh12d_targeted_external_evidence_followup": fetch_table_snapshot(
            con, "dwh12d_targeted_external_evidence_followup"
        ),
        "dwh13_manual_evidence_worklist": fetch_table_snapshot(
            con, "dwh13_manual_evidence_worklist"
        ),
    }
    upstream_counts_after = {name: len(rows) for name, rows in upstream_after.items()}
    upstream_digests_after = {name: stable_digest(rows) for name, rows in upstream_after.items()}
    upstream_preserved = {
        name: {
            "count_before": preflight["upstream_counts"][name],
            "count_after": upstream_counts_after[name],
            "digest_before": preflight["upstream_digests"][name],
            "digest_after": upstream_digests_after[name],
            "status": (
                "passed"
                if preflight["upstream_counts"][name] == upstream_counts_after[name]
                and preflight["upstream_digests"][name] == upstream_digests_after[name]
                else "failed"
            ),
        }
        for name in preflight["upstream_counts"]
    }
    dwh14a_counts = {table: table_count(con, table) for table in DWH14A_TABLES}
    view_counts = {
        view: table_count(con, view)
        for view in DWH14A_VIEWS
        if object_exists(con, view, "view")
    }
    inserted_terms = fetch_dicts(
        con,
        """
        SELECT d.token_position, d.term
        FROM dwh14a_manual_evidence_decision d
        LEFT JOIN dwh13_manual_evidence_worklist w
          ON w.token_position = d.token_position
         AND w.term = d.term
         AND w.evidence_priority = 'high'
        WHERE w.manual_review_id IS NULL
        """,
    )
    forbidden_accepted = fetch_dicts(
        con,
        """
        SELECT manual_evidence_decision_id, token_position, term
        FROM dwh14a_manual_evidence_decision
        WHERE lower(decision_status) IN (
            'final_verified_semantics',
            'proven',
            'validated_physics',
            'confirms_bridge',
            'bridge_confirmed',
            'physical_evidence',
            'shapiro_confirmed'
        )
        """,
    )
    return {
        "workcopy_integrity_check": integrity,
        "workcopy_foreign_key_violations": fk_violations,
        "foreign_key_violation_count": len(fk_violations),
        "input_row_accounting_status": (
            "passed" if input_row_count == inserted_count + rejected_count else "failed"
        ),
        "inserted_terms_outside_high_priority": inserted_terms,
        "inserted_terms_scope_status": "passed" if not inserted_terms else "failed",
        "forbidden_accepted_rows": forbidden_accepted,
        "forbidden_acceptance_status": "passed" if not forbidden_accepted else "failed",
        "upstream_preservation": upstream_preserved,
        "upstream_preservation_status": (
            "passed"
            if all(item["status"] == "passed" for item in upstream_preserved.values())
            else "failed"
        ),
        "dwh14a_table_counts": dwh14a_counts,
        "dwh14a_view_counts": view_counts,
        "dwh14a_views_queryable": len(view_counts) == len(DWH14A_VIEWS),
        "live_db_sha256_before": live_before["sha256"],
        "live_db_sha256_after": live_after["sha256"],
        "live_db_stat_before": live_before["stat"],
        "live_db_stat_after": live_after["stat"],
        "live_db_checksum_unchanged": live_before["sha256"] == live_after["sha256"],
        "live_db_stat_unchanged": live_before["stat"] == live_after["stat"],
    }


def fetch_all(con: sqlite3.Connection, source_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(source_name)}")


def mapping_preview_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT
            token_position,
            term,
            dwh13_manual_review_status AS previous_status,
            dwh14a_decision_status,
            proposed_next_mapping_status,
            safe_to_promote,
            notes
        FROM qsb_v_dwh14a_high_priority_decision_status
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
    )


def next_dwh_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH15_A",
            "next_step_name": "Controlled mapping review status update for evidence-supported candidates only",
            "prerequisite": "DWH14A has candidate-supported terms with promotion preview action",
            "recommended_action": "Update mapping review status only in a separate controlled workcopy step.",
            "risk_level": "medium",
            "notes": "Use only rows marked safe_to_promote in DWH14A preview.",
        },
        {
            "next_step_id": "DWH15_B",
            "next_step_name": "Manual evidence follow-up for remaining open high-priority terms",
            "prerequisite": "One or more high-priority terms remain open or deferred",
            "recommended_action": "Collect additional controlled source evidence and rerun a new controlled insertion step.",
            "risk_level": "medium",
            "notes": "Keep unsupported terms open.",
        },
        {
            "next_step_id": "DWH15_C",
            "next_step_name": "DBeaver inspection of DWH14A manual evidence decisions",
            "prerequisite": "DWH14A tables and views are queryable",
            "recommended_action": "Inspect inserted decisions, rejection log, and mapping review preview.",
            "risk_level": "low",
            "notes": "Useful immediate audit step.",
        },
        {
            "next_step_id": "DWH15_D",
            "next_step_name": "Shapiro-Mart design after stable candidate separation",
            "prerequisite": "Supported/open/conflict candidate separation is stable",
            "recommended_action": "Defer design work until evidence status groups are stable.",
            "risk_level": "high",
            "notes": "DWH14A insertion alone does not support design work.",
        },
    ]


def build_summary(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    manual_input_file: Path,
    preflight: dict[str, Any],
    validation: dict[str, Any],
    input_row_count: int,
) -> dict[str, Any]:
    inserted_rows = fetch_all(con, "dwh14a_manual_evidence_decision")
    rejected_rows = fetch_all(con, "dwh14a_manual_evidence_rejection_log")
    preview_rows = mapping_preview_rows(con)
    counts = status_counts(inserted_rows)
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH controlled manual-evidence insertion in workcopy only",
        "data_substrate_used": str(workcopy_db),
        "manual_evidence_input_file": str(manual_input_file),
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "live_retrieval_performed": False,
        "raw_tim_par_files_read": False,
        "report_outputs_used_as_evidence_input": False,
        "bridge_or_result_tables_created": False,
        "input_row_count": input_row_count,
        "inserted_rows": inserted_rows,
        "inserted_decision_count": len(inserted_rows),
        "rejected_rows": rejected_rows,
        "rejected_row_count": len(rejected_rows),
        "supported_candidate_count": counts["supported_candidate_count"],
        "open_gap_count": counts["open_gap_count"],
        "conflict_count": counts["conflict_count"],
        "mapping_review_status_preview": preview_rows,
        "next_dwh_steps": next_dwh_steps_rows(),
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
            "high_priority_term_count": len(preflight["high_terms"]),
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


def format_decision_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; status={decision_status}; strength={evidence_strength}; next_action={next_action}".format(**row)
        for row in rows
    )


def format_rejection_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; reason={rejection_reason}".format(**row)
        for row in rows
    )


def format_preview_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; previous={previous_status}; dwh14a={dwh14a_decision_status}; next={proposed_next_mapping_status}; safe_to_promote={safe_to_promote}".format(**row)
        for row in rows
    )


def render_readout(summary: dict[str, Any]) -> str:
    live_status = (
        "unchanged"
        if summary["validation"]["live_db_checksum_unchanged"]
        and summary["validation"]["live_db_stat_unchanged"]
        else "changed"
    )
    supported = [
        row for row in summary["inserted_rows"]
        if row["decision_status"] == "evidence_supported_candidate"
    ]
    open_or_conflict = [
        row for row in summary["inserted_rows"]
        if row["decision_status"] != "evidence_supported_candidate"
    ]
    next_lines = "\n".join(
        "- {next_step_id}: {next_step_name}".format(**row)
        for row in summary["next_dwh_steps"]
    )
    return f"""# QSB-DWH14A Manual Evidence Insertion Readout

## 1. Executive summary

Befund: DWH14A inserted controlled manual evidence decisions from an explicit human-reviewed CSV input file.

- Run ID: `{summary['run_id']}`
- Workcopy DB: `{summary['workcopy_db_path']}`
- Input rows: {summary['input_row_count']}
- Inserted decisions: {summary['inserted_decision_count']}
- Rejected rows: {summary['rejected_row_count']}
- Supported candidates: {summary['supported_candidate_count']}
- Open/deferred rows: {summary['open_gap_count']}
- Conflict rows: {summary['conflict_count']}

## 2. Workcopy-only principle

DWH14A writes were limited to DWH14A decision, rejection, run-log tables, and DWH14A views in the workcopy DB. DWH10, DWH12D, and DWH13 rows were not rewritten.

## 3. Manual evidence input file

- Input file: `{summary['manual_evidence_input_file']}`
- Report outputs were not used as evidence input.

## 4. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH14A: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH14A: {live_status}

## 5. Inserted manual evidence decisions

{format_decision_lines(summary['inserted_rows'])}

## 6. Rejected rows

{format_rejection_lines(summary['rejected_rows'])}

## 7. Supported candidates

{format_decision_lines(supported)}

## 8. Open/conflict/deferred terms

{format_decision_lines(open_or_conflict)}

## 9. Mapping review status preview

{format_preview_lines(summary['mapping_review_status_preview'])}

## 10. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- Input row accounting: {summary['validation']['input_row_accounting_status']}
- Inserted terms scope: {summary['validation']['inserted_terms_scope_status']}
- Forbidden acceptance check: {summary['validation']['forbidden_acceptance_status']}
- Upstream row preservation: {summary['validation']['upstream_preservation_status']}
- DWH14A views queryable: {summary['validation']['dwh14a_views_queryable']}

## 11. What DWH14A does not do

DWH14A does not perform live internet retrieval, does not automatically verify evidence, does not assign final semantic meaning, does not create bridge/result tables, does not compute timing/model/statistical quantities, and does not make physical interpretation statements.

## 12. Recommended DWH15 options

{next_lines}

## 13. Claim boundary

{summary['claim_boundary']}
"""


def render_outputs(summary: dict[str, Any]) -> dict[str, str]:
    return {
        READOUT_MD: render_readout(summary),
        SUMMARY_JSON: pretty_json(summary) + "\n",
        INSERTED_CSV: csv_text(
            [
                "token_position",
                "term",
                "decision_status",
                "evidence_strength",
                "source_label",
                "source_url_or_local_reference",
                "access_or_review_date",
                "next_action",
                "notes",
            ],
            summary["inserted_rows"],
        ),
        REJECTED_CSV: csv_text(
            [
                "token_position",
                "term",
                "rejection_reason",
                "notes",
            ],
            summary["rejected_rows"],
        ),
        PREVIEW_CSV: csv_text(
            [
                "token_position",
                "term",
                "previous_status",
                "dwh14a_decision_status",
                "proposed_next_mapping_status",
                "safe_to_promote",
                "notes",
            ],
            summary["mapping_review_status_preview"],
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
    manual_evidence_csv: Path,
    overwrite: bool,
    allow_existing: bool,
) -> dict[str, Any]:
    live_before = db_state(live_db)
    preflight = ensure_preconditions(
        live_db,
        workcopy_db,
        output_root,
        manual_evidence_csv,
        overwrite,
        allow_existing,
    )
    input_rows, raw_rows = read_manual_input(manual_evidence_csv)
    created_at = utc_now()
    run_id = "DWH14A_MANUAL_EVIDENCE_INSERTION_" + timestamp_for_id()
    inserted_rows, rejected_rows = validate_manual_rows(
        input_rows,
        preflight["high_terms"],
        created_at,
        manual_evidence_csv,
    )
    output_texts: dict[str, str]

    con = connect_writable(workcopy_db)
    try:
        con.execute("BEGIN IMMEDIATE")
        create_tables(con, allow_existing)
        insert_rows(con, "dwh14a_manual_evidence_decision", inserted_rows)
        insert_rows(con, "dwh14a_manual_evidence_rejection_log", rejected_rows)
        create_views(con, allow_existing)

        live_after = db_state(live_db)
        counts = status_counts(inserted_rows)
        validation_before_log = validate_workcopy(
            con,
            preflight,
            live_before,
            live_after,
            len(raw_rows),
            len(inserted_rows),
            len(rejected_rows),
        )
        insert_run_log(
            con,
            run_id,
            created_at,
            live_db,
            workcopy_db,
            manual_evidence_csv,
            not validation_before_log["live_db_checksum_unchanged"]
            or not validation_before_log["live_db_stat_unchanged"],
            len(raw_rows),
            len(inserted_rows),
            len(rejected_rows),
            counts,
            validation_before_log["workcopy_integrity_check"],
            validation_before_log["foreign_key_violation_count"],
        )
        validation = validate_workcopy(
            con,
            preflight,
            live_before,
            live_after,
            len(raw_rows),
            len(inserted_rows),
            len(rejected_rows),
        )
        summary = build_summary(
            con,
            run_id,
            created_at,
            live_db,
            workcopy_db,
            output_root,
            manual_evidence_csv,
            preflight,
            validation,
            len(raw_rows),
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
        description="QSB-DWH14A controlled manual evidence insertion for high-priority terms."
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
        help="Existing output directory for DWH14A reports.",
    )
    parser.add_argument(
        "--manual-evidence-csv",
        type=Path,
        default=DEFAULT_MANUAL_EVIDENCE_CSV,
        help="Explicit human-reviewed manual evidence CSV input.",
    )
    parser.add_argument(
        "--create-template",
        action="store_true",
        help="Create the manual evidence CSV template only; no DB writes.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting DWH14A report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH14A target objects; never appends to nonempty DWH14A tables.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.create_template:
            result = create_template(
                args.live_db,
                args.workcopy_db,
                args.output_root,
                args.manual_evidence_csv,
            )
            print(pretty_json(result))
            print(f"Template path: {args.manual_evidence_csv}")
            return 0
        summary = execute(
            args.live_db,
            args.workcopy_db,
            args.output_root,
            args.manual_evidence_csv,
            args.overwrite,
            args.allow_existing,
        )
    except FileNotFoundError as exc:
        if str(exc) == MISSING_INPUT_MESSAGE:
            print(MISSING_INPUT_MESSAGE, file=sys.stderr)
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
