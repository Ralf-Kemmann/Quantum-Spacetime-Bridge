#!/usr/bin/env python3
"""QSB-DWH12D targeted external evidence follow-up in the workcopy.

Default mode is no-live retrieval. In that mode the script uses only existing
DB28/DWH08/DWH10/DWH11 context and keeps unsupported DWH11 open-gap terms open.
Live retrieval is available only when explicitly requested and is restricted to
controlled institutional source URLs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh12d_targeted_external_evidence_followup.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh12d_targeted_external_evidence_followup_readout.md"
SUMMARY_JSON = "dwh12d_targeted_external_evidence_followup_summary.json"
TERM_FOLLOWUP_CSV = "dwh12d_term_evidence_followup.csv"
RETRIEVAL_LOG_CSV = "dwh12d_source_retrieval_log.csv"
STATUS_BY_TOKEN_CSV = "dwh12d_evidence_status_by_token.csv"
REVIEW_UPDATE_CSV = "dwh12d_review_queue_update.csv"
NEXT_STEPS_CSV = "dwh12d_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    TERM_FOLLOWUP_CSV,
    RETRIEVAL_LOG_CSV,
    STATUS_BY_TOKEN_CSV,
    REVIEW_UPDATE_CSV,
    NEXT_STEPS_CSV,
]

DWH12D_TABLES = [
    "dwh12d_targeted_external_evidence_followup",
    "dwh12d_source_retrieval_log",
    "dwh12d_review_queue_update",
    "dwh12d_external_evidence_followup_run_log",
]

DWH12D_VIEWS = [
    "qsb_v_dwh12d_external_evidence_followup_dashboard",
    "qsb_v_dwh12d_evidence_status_by_token",
    "qsb_v_dwh12d_open_gaps",
    "qsb_v_dwh12d_supported_candidates",
    "qsb_v_dwh12d_next_review_actions",
]

DWH11_TABLES = [
    "dwh11_external_evidence_verification",
    "dwh11_external_source_retrieval_log",
    "dwh11_evidence_review_queue",
    "dwh11_external_evidence_run_log",
]

EXPECTED_DWH12D_TERMS = [
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

ALLOWED_SOURCE_DOMAINS = [
    "greenbankobservatory.org",
    "nrao.edu",
    "nanograv.org",
    "ipta4gw.org",
    "atnf.csiro.au",
]

CLAIM_BOUNDARY = (
    "DWH12D is a workcopy-only targeted evidence follow-up for DWH11 open "
    "gaps. It records candidate evidence status only. In no-live mode it does "
    "not retrieve external pages and does not change DWH08/DWH10/DWH11 rows. "
    "It does not read raw TIM/PAR files, does not touch all raw_field_value "
    "rows, does not create bridge/result tables, does not assign final "
    "semantic meaning to TIM columns, does not compute timing/model/statistical "
    "quantities, and does not make physical interpretation statements."
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
            "Refusing to overwrite existing DWH12D output file(s): "
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


def dwh11_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fetch_dwh11_open_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT
            v.token_position,
            v.term,
            v.proposed_role,
            v.verification_status,
            v.evidence_strength,
            v.evidence_source_label,
            v.evidence_url,
            v.retrieval_status,
            v.review_status,
            v.notes,
            q.priority AS dwh11_priority,
            q.blocking_status AS dwh11_blocking_status,
            q.depends_on AS dwh11_depends_on
        FROM dwh11_external_evidence_verification v
        LEFT JOIN dwh11_evidence_review_queue q
          ON q.token_position = v.token_position
         AND q.term = v.term
        WHERE v.verification_status = 'evidence_gap_open'
        ORDER BY
            CASE v.token_position
                WHEN 'tim_token_007' THEN 1
                WHEN 'tim_token_011' THEN 2
                WHEN 'tim_token_017' THEN 3
                WHEN 'tim_token_013' THEN 4
                WHEN 'tim_token_023' THEN 5
                ELSE 9
            END,
            v.term
        """,
    )
    order = {pair: idx for idx, pair in enumerate(EXPECTED_DWH12D_TERMS)}
    return sorted(
        rows,
        key=lambda row: order[(str(row["token_position"]), str(row["term"]))],
    )


def fetch_dwh11_verification_snapshot(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT token_position, term, proposed_role, verification_status,
               evidence_strength, evidence_source_label, evidence_url,
               retrieval_status, review_status, notes
        FROM dwh11_external_evidence_verification
        ORDER BY token_position, term
        """,
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
        if not object_exists(con, "dwh10_block_switch_mapping_refinement", "table"):
            raise RuntimeError("Missing DWH10 table: dwh10_block_switch_mapping_refinement")
        dwh10_count = table_count(con, "dwh10_block_switch_mapping_refinement")
        missing_dwh11 = [
            table for table in DWH11_TABLES
            if not object_exists(con, table, "table")
        ]
        if missing_dwh11:
            raise RuntimeError("Missing DWH11 table(s): " + ", ".join(missing_dwh11))
        dwh11_snapshot = fetch_dwh11_verification_snapshot(con)
        dwh11_open_rows = fetch_dwh11_open_rows(con)
        existing_dwh12d = [
            name for name in [*DWH12D_TABLES, *DWH12D_VIEWS]
            if object_exists(con, name)
        ]
        existing_dwh12d_counts = {
            table: table_count(con, table)
            for table in DWH12D_TABLES
            if object_exists(con, table, "table")
        }

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if dwh10_count != 5:
        raise RuntimeError(f"DWH10 refinement row count must be 5, got {dwh10_count}.")
    if not dwh11_open_rows:
        raise RuntimeError("No DWH11 open gaps found.")
    expected_pairs = set(EXPECTED_DWH12D_TERMS)
    actual_pairs = {
        (str(row["token_position"]), str(row["term"]))
        for row in dwh11_open_rows
    }
    if actual_pairs != expected_pairs:
        raise RuntimeError("DWH11 open-gap terms do not match the DWH12D expected target terms.")
    if existing_dwh12d and not allow_existing:
        raise RuntimeError(
            "DWH12D target object(s) already exist; rerun with --allow-existing "
            "only for controlled empty-object continuation: " + ", ".join(existing_dwh12d)
        )
    nonempty_existing = [
        f"{table}={count}"
        for table, count in existing_dwh12d_counts.items()
        if count > 0
    ]
    if nonempty_existing:
        raise RuntimeError(
            "Refusing to append to nonempty DWH12D table(s): "
            + ", ".join(nonempty_existing)
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "dwh10_refinement_count": dwh10_count,
        "dwh11_verification_count": len(dwh11_snapshot),
        "dwh11_open_gap_count": len(dwh11_open_rows),
        "dwh11_snapshot_digest": dwh11_digest(dwh11_snapshot),
    }


def create_tables(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    statements = [
        f"""
        CREATE TABLE {clause}dwh12d_targeted_external_evidence_followup (
            followup_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            proposed_role TEXT,
            dwh11_status TEXT,
            dwh12d_status TEXT NOT NULL,
            evidence_strength TEXT NOT NULL,
            source_label TEXT,
            source_url TEXT,
            source_type TEXT,
            evidence_summary TEXT,
            retrieval_mode TEXT NOT NULL,
            retrieval_status TEXT NOT NULL,
            retrieved_at_utc TEXT,
            review_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh12d_source_retrieval_log (
            retrieval_id TEXT PRIMARY KEY,
            retrieval_timestamp_utc TEXT,
            source_label TEXT,
            source_url TEXT,
            source_type TEXT,
            retrieval_mode TEXT NOT NULL,
            retrieval_status TEXT NOT NULL,
            term TEXT,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh12d_review_queue_update (
            review_update_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            previous_review_status TEXT,
            new_recommended_status TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            priority TEXT NOT NULL,
            blocking_status TEXT NOT NULL,
            depends_on TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        )
        """,
        f"""
        CREATE TABLE {clause}dwh12d_external_evidence_followup_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            checked_term_count INTEGER,
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
        CREATE VIEW {clause}qsb_v_dwh12d_external_evidence_followup_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'dwh12d_external_evidence_followup_run_log' AS metric_source,
               notes AS dashboard_note
        FROM dwh12d_external_evidence_followup_run_log
        UNION ALL
        SELECT 'followup_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh12d_targeted_external_evidence_followup',
               'One DWH12D row per DWH11 open term.'
        FROM dwh12d_targeted_external_evidence_followup
        UNION ALL
        SELECT 'supported_candidate_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh12d_targeted_external_evidence_followup',
               'Rows with candidate evidence support.'
        FROM dwh12d_targeted_external_evidence_followup
        WHERE dwh12d_status = 'evidence_supported_candidate'
        UNION ALL
        SELECT 'open_gap_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh12d_targeted_external_evidence_followup',
               'Rows that remain open evidence gaps.'
        FROM dwh12d_targeted_external_evidence_followup
        WHERE dwh12d_status IN (
            'evidence_gap_open',
            'source_not_retrieved',
            'source_not_controlled_enough'
        )
        UNION ALL
        SELECT 'conflict_or_mismatch_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh12d_targeted_external_evidence_followup',
               'Rows with evidence conflict or mismatch.'
        FROM dwh12d_targeted_external_evidence_followup
        WHERE dwh12d_status = 'evidence_conflict_or_mismatch'
        UNION ALL
        SELECT 'review_queue_update_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh12d_review_queue_update',
               'Rows requiring continued review action.'
        FROM dwh12d_review_queue_update
        UNION ALL
        SELECT 'retrieval_log_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh12d_source_retrieval_log',
               'Rows recording no-live or live source handling.'
        FROM dwh12d_source_retrieval_log
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DWH12D insertions.'
        FROM dwh12d_external_evidence_followup_run_log
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh12d_evidence_status_by_token AS
        SELECT
            token_position,
            MIN(proposed_role) AS candidate_role,
            COUNT(*) AS checked_term_count,
            SUM(CASE WHEN dwh12d_status = 'evidence_supported_candidate' THEN 1 ELSE 0 END) AS supported_term_count,
            SUM(CASE WHEN dwh12d_status IN (
                'evidence_gap_open',
                'source_not_retrieved',
                'source_not_controlled_enough'
            ) THEN 1 ELSE 0 END) AS open_gap_count,
            SUM(CASE WHEN dwh12d_status = 'evidence_conflict_or_mismatch' THEN 1 ELSE 0 END) AS conflict_count,
            CASE
                WHEN SUM(CASE WHEN dwh12d_status = 'evidence_conflict_or_mismatch' THEN 1 ELSE 0 END) > 0
                THEN 'evidence_conflict_or_mismatch'
                WHEN SUM(CASE WHEN dwh12d_status IN (
                    'evidence_gap_open',
                    'source_not_retrieved',
                    'source_not_controlled_enough'
                ) THEN 1 ELSE 0 END) > 0
                 AND SUM(CASE WHEN dwh12d_status = 'evidence_supported_candidate' THEN 1 ELSE 0 END) > 0
                THEN 'mixed_supported_and_open'
                WHEN SUM(CASE WHEN dwh12d_status IN (
                    'evidence_gap_open',
                    'source_not_retrieved',
                    'source_not_controlled_enough'
                ) THEN 1 ELSE 0 END) > 0
                THEN 'evidence_gaps_open'
                WHEN SUM(CASE WHEN dwh12d_status = 'evidence_supported_candidate' THEN 1 ELSE 0 END) = COUNT(*)
                THEN 'all_checked_terms_supported_as_candidates'
                ELSE 'not_reviewed'
            END AS overall_evidence_status,
            CASE
                WHEN SUM(CASE WHEN dwh12d_status IN (
                    'evidence_gap_open',
                    'source_not_retrieved',
                    'source_not_controlled_enough'
                ) THEN 1 ELSE 0 END) > 0
                THEN 'Continue manual or live controlled source review before any mapping-status update.'
                ELSE 'Human review may consider candidate-only mapping-status update.'
            END AS recommended_next_action
        FROM dwh12d_targeted_external_evidence_followup
        GROUP BY token_position
        ORDER BY token_position
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh12d_open_gaps AS
        SELECT *
        FROM dwh12d_targeted_external_evidence_followup
        WHERE dwh12d_status IN (
            'evidence_gap_open',
            'source_not_retrieved',
            'source_not_controlled_enough'
        )
        ORDER BY token_position, term
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh12d_supported_candidates AS
        SELECT *
        FROM dwh12d_targeted_external_evidence_followup
        WHERE dwh12d_status = 'evidence_supported_candidate'
        ORDER BY token_position, term
        """,
        f"""
        CREATE VIEW {clause}qsb_v_dwh12d_next_review_actions AS
        SELECT
            review_update_id AS action_id,
            token_position,
            term,
            previous_review_status,
            new_recommended_status,
            recommended_action,
            priority,
            blocking_status,
            depends_on,
            notes
        FROM dwh12d_review_queue_update
        ORDER BY
            CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 ELSE 3 END,
            token_position,
            term
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


def load_source_registry(con: sqlite3.Connection) -> list[dict[str, Any]]:
    if not object_exists(con, "db28_external_source_registry", "table"):
        return []
    return fetch_dicts(
        con,
        """
        SELECT source_id, source_name, institution, source_type, official_url,
               relevance_class, tier, retrieval_status
        FROM db28_external_source_registry
        ORDER BY source_id
        """,
    )


def load_assertions_by_term(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    if not object_exists(con, "db28_mapping_assertion_evidence", "table"):
        return {}
    rows = fetch_dicts(
        con,
        """
        SELECT assertion_id, related_token_position, raw_value_or_term,
               proposed_mapping_scope, source_id, evidence_status,
               assertion_status, evidence_summary, evidence_ref, review_status
        FROM db28_mapping_assertion_evidence
        ORDER BY assertion_id
        """,
    )
    return {str(row["raw_value_or_term"]): row for row in rows}


def load_dictionary_seed_by_term(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    if not object_exists(con, "db28_external_dictionary_seed", "table"):
        return {}
    rows = fetch_dicts(
        con,
        """
        SELECT dictionary_seed_id, source_id, entity_type, raw_term,
               candidate_canonical_term, evidence_status, assertion_status,
               evidence_summary, confidence_class
        FROM db28_external_dictionary_seed
        ORDER BY dictionary_seed_id
        """,
    )
    return {str(row["raw_term"]): row for row in rows}


def source_label(source: dict[str, Any]) -> str:
    name = str(source.get("source_name") or "").strip()
    institution = str(source.get("institution") or "").strip()
    return f"{name} / {institution}" if institution else name


def source_matches_url(source: dict[str, Any], url: str | None) -> bool:
    if not url:
        return False
    official_url = str(source.get("official_url") or "")
    return bool(official_url and official_url in url or url in official_url)


def resolve_source_metadata(
    row: dict[str, Any],
    sources: list[dict[str, Any]],
    assertions: dict[str, dict[str, Any]],
    seeds: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    term = str(row["term"])
    for source in sources:
        if source_matches_url(source, row.get("evidence_url")):
            return {
                "source_label": source_label(source),
                "source_url": str(source.get("official_url") or row.get("evidence_url") or ""),
                "source_type": str(source.get("source_type") or "controlled_seed"),
            }
    context = assertions.get(term) or seeds.get(term)
    if context:
        source_id = context.get("source_id")
        for source in sources:
            if source.get("source_id") == source_id:
                return {
                    "source_label": source_label(source),
                    "source_url": str(source.get("official_url") or row.get("evidence_url") or ""),
                    "source_type": str(source.get("source_type") or "controlled_seed"),
                }
    return {
        "source_label": str(row.get("evidence_source_label") or "DWH11 source class"),
        "source_url": str(row.get("evidence_url") or ""),
        "source_type": "controlled_seed",
    }


def db28_context_note(
    term: str,
    assertions: dict[str, dict[str, Any]],
    seeds: dict[str, dict[str, Any]],
) -> str:
    assertion = assertions.get(term)
    if assertion:
        return (
            "DB28 assertion context: "
            f"assertion_status={assertion.get('assertion_status')}; "
            f"evidence_status={assertion.get('evidence_status')}"
        )
    seed = seeds.get(term)
    if seed:
        return (
            "DB28 dictionary-seed context: "
            f"assertion_status={seed.get('assertion_status')}; "
            f"evidence_status={seed.get('evidence_status')}"
        )
    return "No DB28 term-level assertion/seed row found."


def is_controlled_source(source_url: str, source_label_value: str) -> bool:
    value = (source_url + " " + source_label_value).lower()
    return any(domain in value for domain in ALLOWED_SOURCE_DOMAINS)


def role_keywords(proposed_role: str | None) -> list[str]:
    role = str(proposed_role or "")
    if role == "receiver_band_context_candidate":
        return ["receiver", "band"]
    if role == "receiver_backend_context_candidate":
        return ["receiver", "backend", "guppi"]
    if role == "derived_product_or_processing_label_candidate":
        return ["release", "archive", "data", "product", "file", "summary"]
    if role == "numeric_observation_configuration_candidate":
        return ["metadata", "configuration", "format", "sampling", "bandwidth", "frequency"]
    if role == "numeric_configuration_state_candidate":
        return ["metadata", "configuration", "format", "state", "flag", "release"]
    return ["metadata", "documentation"]


def term_forms(term: str) -> list[str]:
    forms = {term.lower(), term.lower().replace("_", " ")}
    for part in term.replace(".", "_").split("_"):
        part = part.strip().lower()
        if len(part) >= 3:
            forms.add(part)
    return sorted(forms, key=len, reverse=True)


def retrieve_controlled_source(source_url: str) -> tuple[str, str]:
    request = urllib.request.Request(
        source_url,
        headers={"User-Agent": "QSB-DWH12D-targeted-evidence/1.0"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        data = response.read(300_000)
        content_type = response.headers.get("Content-Type", "")
    text = data.decode("utf-8", errors="ignore")
    return text, content_type


def classify_live_text(
    term: str,
    proposed_role: str | None,
    text: str,
) -> tuple[str, str, str]:
    lowered = text.lower()
    forms = term_forms(term)
    term_hits = [form for form in forms if form and form in lowered]
    keyword_hits = [word for word in role_keywords(proposed_role) if word in lowered]
    if term.lower() in lowered and keyword_hits:
        return (
            "evidence_supported_candidate",
            "moderate",
            "Controlled source text contains the target term and role-context keyword(s); candidate support only.",
        )
    if term_hits and keyword_hits:
        return (
            "evidence_supported_candidate",
            "weak",
            "Controlled source text contains partial term/context matches; candidate support remains weak.",
        )
    if term_hits:
        return (
            "evidence_gap_open",
            "weak",
            "Controlled source text contains the term but does not clearly support the proposed role.",
        )
    return (
        "evidence_gap_open",
        "none_or_insufficient",
        "Controlled source text was retrieved but did not support the proposed role.",
    )


def live_source_candidates(
    base_source: dict[str, Any],
    token_position: str,
    sources: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    candidates = [base_source]
    desired_ids: list[str]
    if token_position in {"tim_token_007", "tim_token_011"}:
        desired_ids = ["db28_src_gbo_gbt", "db28_src_nanograv_docs"]
    else:
        desired_ids = ["db28_src_ipta_pod", "db28_src_nanograv_docs", "db28_src_psrfits_atnf"]
    seen = {(base_source["source_label"], base_source["source_url"])}
    for source_id in desired_ids:
        for source in sources:
            if source.get("source_id") != source_id:
                continue
            item = {
                "source_label": source_label(source),
                "source_url": str(source.get("official_url") or ""),
                "source_type": str(source.get("source_type") or "documentation"),
            }
            key = (item["source_label"], item["source_url"])
            if key not in seen:
                candidates.append(item)
                seen.add(key)
    return candidates


def no_live_followup_for_row(
    idx: int,
    row: dict[str, Any],
    created_at: str,
    source: dict[str, Any],
    context_note: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    followup = {
        "followup_id": f"dwh12d_followup_{idx:03d}",
        "token_position": row["token_position"],
        "term": row["term"],
        "proposed_role": row["proposed_role"],
        "dwh11_status": row["verification_status"],
        "dwh12d_status": "evidence_gap_open",
        "evidence_strength": "none_or_insufficient",
        "source_label": source["source_label"],
        "source_url": source["source_url"],
        "source_type": source["source_type"],
        "evidence_summary": (
            "DWH12D ran in no-live mode. Existing DB28/DWH11 context is not "
            "sufficient to support the proposed role."
        ),
        "retrieval_mode": "no_live_retrieval",
        "retrieval_status": "not_attempted_no_live",
        "retrieved_at_utc": None,
        "review_status": "needs_external_evidence_review",
        "created_at_utc": created_at,
        "notes": context_note + "; DWH10/DWH11/DWH08 rows were not rewritten.",
    }
    retrieval = {
        "retrieval_id": f"dwh12d_retrieval_{idx:03d}_001",
        "retrieval_timestamp_utc": created_at,
        "source_label": source["source_label"],
        "source_url": source["source_url"],
        "source_type": source["source_type"],
        "retrieval_mode": "no_live_retrieval",
        "retrieval_status": "not_attempted_no_live",
        "term": row["term"],
        "notes": "No external retrieval was attempted; term remains an open evidence gap.",
    }
    return followup, [retrieval]


def live_followup_for_row(
    idx: int,
    row: dict[str, Any],
    created_at: str,
    source: dict[str, Any],
    sources: list[dict[str, Any]],
    context_note: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    best_status = "source_not_retrieved"
    best_strength = "none_or_insufficient"
    best_summary = "No controlled source was retrieved for this term."
    best_source = source
    retrieval_rows: list[dict[str, Any]] = []
    for attempt_idx, candidate in enumerate(
        live_source_candidates(source, str(row["token_position"]), sources),
        start=1,
    ):
        retrieval_status = "not_attempted"
        notes = ""
        if not is_controlled_source(candidate["source_url"], candidate["source_label"]):
            retrieval_status = "source_not_controlled_enough"
            notes = "Source URL/label did not pass the controlled-source allowlist."
            status = "source_not_controlled_enough"
            strength = "none_or_insufficient"
            summary = "The source was not controlled enough for DWH12D use."
        else:
            try:
                text, content_type = retrieve_controlled_source(candidate["source_url"])
                retrieval_status = "retrieved_controlled_source"
                status, strength, summary = classify_live_text(
                    str(row["term"]),
                    row.get("proposed_role"),
                    text,
                )
                notes = f"Retrieved controlled source; content_type={content_type[:80]}."
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                retrieval_status = "retrieval_failed"
                status = "source_not_retrieved"
                strength = "none_or_insufficient"
                summary = "Controlled source retrieval failed; no candidate support recorded."
                notes = f"Retrieval failed: {type(exc).__name__}: {exc}"
        retrieval_rows.append(
            {
                "retrieval_id": f"dwh12d_retrieval_{idx:03d}_{attempt_idx:03d}",
                "retrieval_timestamp_utc": created_at,
                "source_label": candidate["source_label"],
                "source_url": candidate["source_url"],
                "source_type": candidate["source_type"],
                "retrieval_mode": "live_retrieval",
                "retrieval_status": retrieval_status,
                "term": row["term"],
                "notes": notes,
            }
        )
        if status == "evidence_supported_candidate":
            best_status = status
            best_strength = strength
            best_summary = summary
            best_source = candidate
            break
        if best_status == "source_not_retrieved" and status == "evidence_gap_open":
            best_status = status
            best_strength = strength
            best_summary = summary
            best_source = candidate
    followup = {
        "followup_id": f"dwh12d_followup_{idx:03d}",
        "token_position": row["token_position"],
        "term": row["term"],
        "proposed_role": row["proposed_role"],
        "dwh11_status": row["verification_status"],
        "dwh12d_status": best_status,
        "evidence_strength": best_strength,
        "source_label": best_source["source_label"],
        "source_url": best_source["source_url"],
        "source_type": best_source["source_type"],
        "evidence_summary": best_summary,
        "retrieval_mode": "live_retrieval",
        "retrieval_status": (
            "retrieved_controlled_source"
            if best_status in {"evidence_supported_candidate", "evidence_gap_open"}
            else best_status
        ),
        "retrieved_at_utc": created_at,
        "review_status": review_status_for_result(best_status, best_strength),
        "created_at_utc": created_at,
        "notes": context_note + "; support remains candidate-only where present.",
    }
    return followup, retrieval_rows


def review_status_for_result(status: str, strength: str) -> str:
    if status == "evidence_supported_candidate" and strength in {"strong", "moderate"}:
        return "candidate_support_needs_human_review"
    return "needs_external_evidence_review"


def priority_for_token(token_position: str) -> str:
    if token_position in {"tim_token_007", "tim_token_011", "tim_token_017"}:
        return "P1"
    return "P2"


def build_review_updates(
    followup_rows: list[dict[str, Any]],
    dwh11_rows_by_pair: dict[tuple[str, str], dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(followup_rows, start=1):
        status = str(row["dwh12d_status"])
        strength = str(row["evidence_strength"])
        if status == "evidence_supported_candidate" and strength in {"strong", "moderate"}:
            new_status = "candidate_support_needs_human_review"
            action = "Human review may consider candidate-only mapping-status update."
            blocking = "review_required_before_update"
        else:
            new_status = "needs_external_evidence_review"
            action = "Continue manual or live controlled source review before any mapping-status update."
            blocking = "blocks_controlled_definition"
        dwh11_row = dwh11_rows_by_pair[(str(row["token_position"]), str(row["term"]))]
        rows.append(
            {
                "review_update_id": f"dwh12d_review_update_{idx:03d}",
                "token_position": row["token_position"],
                "term": row["term"],
                "previous_review_status": dwh11_row.get("review_status"),
                "new_recommended_status": new_status,
                "recommended_action": action,
                "priority": priority_for_token(str(row["token_position"])),
                "blocking_status": blocking,
                "depends_on": row["source_label"],
                "created_at_utc": created_at,
                "notes": (
                    "DWH12D review update only; DWH11 review queue was not rewritten."
                ),
            }
        )
    return rows


def build_followup_rows(
    con: sqlite3.Connection,
    created_at: str,
    no_live_retrieval: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    dwh11_rows = fetch_dwh11_open_rows(con)
    sources = load_source_registry(con)
    assertions = load_assertions_by_term(con)
    seeds = load_dictionary_seed_by_term(con)
    followup_rows: list[dict[str, Any]] = []
    retrieval_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(dwh11_rows, start=1):
        source = resolve_source_metadata(row, sources, assertions, seeds)
        context_note = db28_context_note(str(row["term"]), assertions, seeds)
        if no_live_retrieval:
            followup, retrieval = no_live_followup_for_row(
                idx,
                row,
                created_at,
                source,
                context_note,
            )
        else:
            followup, retrieval = live_followup_for_row(
                idx,
                row,
                created_at,
                source,
                sources,
                context_note,
            )
        followup_rows.append(followup)
        retrieval_rows.extend(retrieval)
    dwh11_rows_by_pair = {
        (str(row["token_position"]), str(row["term"])): row
        for row in dwh11_rows
    }
    review_update_rows = build_review_updates(
        followup_rows,
        dwh11_rows_by_pair,
        created_at,
    )
    return followup_rows, retrieval_rows, review_update_rows


def insert_run_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    no_live_retrieval: bool,
    live_modified: bool,
    checked_term_count: int,
    supported_candidate_count: int,
    open_gap_count: int,
    conflict_count: int,
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh12d_external_evidence_followup_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            checked_term_count,
            supported_candidate_count,
            open_gap_count,
            conflict_count,
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
                "workcopy_targeted_external_evidence_followup_no_live"
                if no_live_retrieval
                else "workcopy_targeted_external_evidence_followup_live"
            ),
            1 if live_modified else 0,
            1,
            checked_term_count,
            supported_candidate_count,
            open_gap_count,
            conflict_count,
            integrity,
            fk_count,
            "DWH12D recorded candidate evidence status; DWH08/DWH10/DWH11 rows were not rewritten.",
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
    dwh11_snapshot = fetch_dwh11_verification_snapshot(con)
    dwh11_digest_after = dwh11_digest(dwh11_snapshot)
    dwh12d_counts = {table: table_count(con, table) for table in DWH12D_TABLES}
    view_counts = {
        view: table_count(con, view)
        for view in DWH12D_VIEWS
        if object_exists(con, view, "view")
    }
    return {
        "workcopy_integrity_check": integrity,
        "workcopy_foreign_key_violations": fk_violations,
        "foreign_key_violation_count": len(fk_violations),
        "dwh10_refinement_count": table_count(con, "dwh10_block_switch_mapping_refinement"),
        "dwh10_preservation_status": (
            "passed"
            if table_count(con, "dwh10_block_switch_mapping_refinement") == 5
            else "failed"
        ),
        "dwh11_verification_count_before": preflight["dwh11_verification_count"],
        "dwh11_verification_count_after": len(dwh11_snapshot),
        "dwh11_open_gap_count_before": preflight["dwh11_open_gap_count"],
        "dwh11_open_gap_count_after": len(fetch_dwh11_open_rows(con)),
        "dwh11_snapshot_digest_before": preflight["dwh11_snapshot_digest"],
        "dwh11_snapshot_digest_after": dwh11_digest_after,
        "dwh11_preservation_status": (
            "passed"
            if dwh11_digest_after == preflight["dwh11_snapshot_digest"]
            else "failed"
        ),
        "dwh12d_table_counts": dwh12d_counts,
        "dwh12d_view_counts": view_counts,
        "dwh12d_views_queryable": len(view_counts) == len(DWH12D_VIEWS),
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
            "next_step_id": "DWH13_A",
            "next_step_name": "Manual evidence review of supported, weak, and open terms",
            "prerequisite": "DWH12D follow-up rows exist",
            "recommended_action": "Review official source passages manually before changing mapping status.",
            "risk_level": "medium",
            "notes": "Recommended after no-live DWH12D because all terms remain open.",
        },
        {
            "next_step_id": "DWH13_B",
            "next_step_name": "Controlled update of mapping review status for supported candidates only",
            "prerequisite": "One or more DWH12D rows have candidate support after controlled review",
            "recommended_action": "Update only candidate review status in a separate controlled workcopy step.",
            "risk_level": "medium",
            "notes": "Not applicable while all rows are open gaps.",
        },
        {
            "next_step_id": "DWH13_C",
            "next_step_name": "DBeaver/ERD visual check of DWH11/DWH12D evidence layer",
            "prerequisite": "DWH11 and DWH12D views are queryable",
            "recommended_action": "Inspect follow-up tables/views beside DWH10 and DWH11.",
            "risk_level": "low",
            "notes": "Useful immediate audit step.",
        },
        {
            "next_step_id": "DWH13_D",
            "next_step_name": "Design Shapiro-Mart after mapping/evidence groups are separated",
            "prerequisite": "Candidates are separated into supported, open, and conflict groups",
            "recommended_action": "Defer design until the evidence layer is separated by status.",
            "risk_level": "high",
            "notes": "DWH12D no-live mode does not support design work yet.",
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
    no_live_retrieval: bool,
) -> dict[str, Any]:
    followup_rows = fetch_dicts(
        con,
        """
        SELECT token_position, term, proposed_role, dwh11_status, dwh12d_status,
               evidence_strength, source_label, source_url, source_type,
               evidence_summary, retrieval_mode, retrieval_status,
               review_status, notes
        FROM dwh12d_targeted_external_evidence_followup
        ORDER BY followup_id
        """,
    )
    source_rows = fetch_all(con, "dwh12d_source_retrieval_log")
    status_rows = fetch_all(con, "qsb_v_dwh12d_evidence_status_by_token")
    review_rows = fetch_all(con, "qsb_v_dwh12d_next_review_actions")
    supported = [row for row in followup_rows if row["dwh12d_status"] == "evidence_supported_candidate"]
    gaps = [
        row for row in followup_rows
        if row["dwh12d_status"] in {
            "evidence_gap_open",
            "source_not_retrieved",
            "source_not_controlled_enough",
        }
    ]
    conflicts = [
        row for row in followup_rows
        if row["dwh12d_status"] == "evidence_conflict_or_mismatch"
    ]
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH controlled targeted external evidence follow-up in workcopy only",
        "data_substrate_used": str(workcopy_db),
        "retrieval_mode_used": "no_live_retrieval" if no_live_retrieval else "live_retrieval",
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "raw_tim_par_files_read": False,
        "new_isolated_analysis_db_created": False,
        "raw_field_value_bulk_touch_performed": False,
        "bridge_or_result_tables_created": False,
        "dwh08_rows_rewritten": 0,
        "dwh10_rows_rewritten": 0,
        "dwh11_rows_rewritten": 0,
        "terms_followed_up": followup_rows,
        "term_count": len(followup_rows),
        "supported_candidate_count": len(supported),
        "open_gap_count": len(gaps),
        "conflict_count": len(conflicts),
        "retrieval_log_rows": source_rows,
        "retrieval_log_count": len(source_rows),
        "evidence_status_by_token": status_rows,
        "review_queue_updates": review_rows,
        "review_queue_update_count": len(review_rows),
        "next_dwh_steps": next_dwh_steps_rows(),
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
            "dwh10_refinement_count": preflight["dwh10_refinement_count"],
            "dwh11_verification_count": preflight["dwh11_verification_count"],
            "dwh11_open_gap_count": preflight["dwh11_open_gap_count"],
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


def format_term_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; status={dwh12d_status}; strength={evidence_strength}; source={source_label}; retrieval={retrieval_status}".format(**row)
        for row in rows
    )


def format_status_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: checked={checked_term_count}; supported={supported_term_count}; gaps={open_gap_count}; conflicts={conflict_count}; status={overall_evidence_status}".format(**row)
        for row in rows
    )


def format_review_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {action_id}: {token_position}; term={term}; priority={priority}; blocking={blocking_status}; new_status={new_recommended_status}".format(**row)
        for row in rows
    )


def render_readout(summary: dict[str, Any]) -> str:
    live_status = (
        "unchanged"
        if summary["validation"]["live_db_checksum_unchanged"]
        and summary["validation"]["live_db_stat_unchanged"]
        else "changed"
    )
    source_lines = "\n".join(
        "- {source_label}; url={source_url}; type={source_type}; retrieval={retrieval_status}".format(**row)
        for row in summary["retrieval_log_rows"]
    )
    next_lines = "\n".join(
        "- {next_step_id}: {next_step_name}".format(**row)
        for row in summary["next_dwh_steps"]
    )
    supported = [
        row for row in summary["terms_followed_up"]
        if row["dwh12d_status"] == "evidence_supported_candidate"
    ]
    gaps = [
        row for row in summary["terms_followed_up"]
        if row["dwh12d_status"] in {
            "evidence_gap_open",
            "source_not_retrieved",
            "source_not_controlled_enough",
        }
    ]
    conflicts = [
        row for row in summary["terms_followed_up"]
        if row["dwh12d_status"] == "evidence_conflict_or_mismatch"
    ]
    return f"""# QSB-DWH12D Targeted External Evidence Follow-up Readout

## 1. Executive summary

Befund: DWH12D followed up the DWH11 open-gap terms in {summary['retrieval_mode_used']} mode.

- Run ID: `{summary['run_id']}`
- Workcopy DB: `{summary['workcopy_db_path']}`
- Terms followed up: {summary['term_count']}
- Supported candidates: {summary['supported_candidate_count']}
- Open evidence gaps: {summary['open_gap_count']}
- Conflicts or mismatches: {summary['conflict_count']}
- Retrieval log rows: {summary['retrieval_log_count']}
- Review queue update rows: {summary['review_queue_update_count']}

## 2. Workcopy-only principle

DWH12D writes were limited to new DWH12D tables in the workcopy DB. DWH08, DWH10, and DWH11 rows were not rewritten.

## 3. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH12D: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH12D: {live_status}

## 4. Retrieval mode

Retrieval mode used: {summary['retrieval_mode_used']}.

## 5. Terms followed up

{format_term_lines(summary['terms_followed_up'])}

## 6. Evidence sources used

{source_lines}

## 7. Supported candidates

{format_term_lines(supported)}

## 8. Open evidence gaps

{format_term_lines(gaps)}

## 9. Conflicts or mismatches

{format_term_lines(conflicts)}

## 10. Review queue updates

{format_review_lines(summary['review_queue_updates'])}

## 11. Integration with DWH10/DWH11

DWH12D consumes DWH11 open-gap rows as the target set and records follow-up status in DWH12D tables only. DWH10 refinement rows and DWH11 evidence rows are preserved.

## 12. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- DWH10 refinement rows preserved: {summary['validation']['dwh10_preservation_status']}
- DWH11 verification rows preserved: {summary['validation']['dwh11_preservation_status']}
- DWH12D views queryable: {summary['validation']['dwh12d_views_queryable']}

## 13. What DWH12D does not do

DWH12D does not read raw TIM/PAR files, does not create a new isolated analysis DB, does not touch all raw_field_value rows, does not create bridge/result tables, does not assign final semantic meaning to TIM columns, does not compute timing/model/statistical quantities, and does not make physical interpretation statements.

## 14. Recommended DWH13 options

{next_lines}

## 15. Claim boundary

{summary['claim_boundary']}
"""


def render_outputs(summary: dict[str, Any]) -> dict[str, str]:
    return {
        READOUT_MD: render_readout(summary),
        SUMMARY_JSON: pretty_json(summary) + "\n",
        TERM_FOLLOWUP_CSV: csv_text(
            [
                "token_position",
                "term",
                "proposed_role",
                "dwh11_status",
                "dwh12d_status",
                "evidence_strength",
                "source_label",
                "source_url",
                "retrieval_mode",
                "retrieval_status",
                "review_status",
                "notes",
            ],
            summary["terms_followed_up"],
        ),
        RETRIEVAL_LOG_CSV: csv_text(
            [
                "retrieval_timestamp_utc",
                "source_label",
                "source_url",
                "source_type",
                "retrieval_mode",
                "retrieval_status",
                "term",
                "notes",
            ],
            summary["retrieval_log_rows"],
        ),
        STATUS_BY_TOKEN_CSV: csv_text(
            [
                "token_position",
                "candidate_role",
                "checked_term_count",
                "supported_term_count",
                "open_gap_count",
                "conflict_count",
                "overall_evidence_status",
                "recommended_next_action",
            ],
            summary["evidence_status_by_token"],
        ),
        REVIEW_UPDATE_CSV: csv_text(
            [
                "token_position",
                "term",
                "previous_review_status",
                "new_recommended_status",
                "recommended_action",
                "priority",
                "blocking_status",
                "depends_on",
                "notes",
            ],
            summary["review_queue_updates"],
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
    no_live_retrieval: bool,
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
    run_id = "DWH12D_TARGETED_EXTERNAL_EVIDENCE_FOLLOWUP_" + timestamp_for_id()
    output_texts: dict[str, str]

    con = connect_writable(workcopy_db)
    try:
        con.execute("BEGIN IMMEDIATE")
        create_tables(con, allow_existing)
        followup_rows, retrieval_rows, review_update_rows = build_followup_rows(
            con,
            created_at,
            no_live_retrieval,
        )
        if len(followup_rows) != len(EXPECTED_DWH12D_TERMS):
            raise RuntimeError(
                f"Expected {len(EXPECTED_DWH12D_TERMS)} follow-up rows, got {len(followup_rows)}."
            )
        insert_rows(con, "dwh12d_targeted_external_evidence_followup", followup_rows)
        insert_rows(con, "dwh12d_source_retrieval_log", retrieval_rows)
        insert_rows(con, "dwh12d_review_queue_update", review_update_rows)
        create_views(con, allow_existing)

        live_after = db_state(live_db)
        validation_before_log = validate_workcopy(con, preflight, live_before, live_after)
        supported_count = sum(
            1 for row in followup_rows
            if row["dwh12d_status"] == "evidence_supported_candidate"
        )
        open_gap_count = sum(
            1 for row in followup_rows
            if row["dwh12d_status"] in {
                "evidence_gap_open",
                "source_not_retrieved",
                "source_not_controlled_enough",
            }
        )
        conflict_count = sum(
            1 for row in followup_rows
            if row["dwh12d_status"] == "evidence_conflict_or_mismatch"
        )
        insert_run_log(
            con,
            run_id,
            created_at,
            live_db,
            workcopy_db,
            no_live_retrieval,
            not validation_before_log["live_db_checksum_unchanged"]
            or not validation_before_log["live_db_stat_unchanged"],
            len(followup_rows),
            supported_count,
            open_gap_count,
            conflict_count,
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
            no_live_retrieval,
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
        description="QSB-DWH12D targeted evidence follow-up for DWH11 open gaps."
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
        help="Existing output directory for DWH12D reports.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the seven DWH12D report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH12D target objects; never appends to nonempty DWH12D tables.",
    )
    parser.add_argument(
        "--no-live-retrieval",
        action="store_true",
        default=True,
        help="Do not perform live external retrieval; this is the default.",
    )
    parser.add_argument(
        "--live-retrieval",
        dest="no_live_retrieval",
        action="store_false",
        help="Attempt controlled institutional source URL retrieval.",
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
            args.no_live_retrieval,
        )
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
