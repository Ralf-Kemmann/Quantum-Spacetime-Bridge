#!/usr/bin/env python3
"""QSB-DWH11: external evidence verification layer in the workcopy.

This script records controlled evidence-verification status for the DWH10 five
block-switch token candidates. The default mode is no live retrieval. In that
mode the script uses only existing workcopy DB seed/evidence rows and marks
terms as open evidence gaps when live external verification has not occurred.

It does not modify the live DB, does not read raw TIM/PAR files, does not touch
all raw_field_value rows, does not create bridge/result tables, does not
compute timing/model/statistical quantities, and does not assign final
controlled or physical meaning to TIM columns.
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


SCRIPT_NAME = "scripts/qsb_dwh11_external_evidence_verification.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh11_external_evidence_verification_readout.md"
SUMMARY_JSON = "dwh11_external_evidence_verification_summary.json"
CANDIDATE_VERIFICATION_CSV = "dwh11_candidate_evidence_verification.csv"
RETRIEVAL_LOG_CSV = "dwh11_external_source_retrieval_log.csv"
STATUS_BY_TOKEN_CSV = "dwh11_evidence_status_by_token.csv"
NEXT_REVIEW_ACTIONS_CSV = "dwh11_next_review_actions.csv"
NEXT_STEPS_CSV = "dwh11_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    CANDIDATE_VERIFICATION_CSV,
    RETRIEVAL_LOG_CSV,
    STATUS_BY_TOKEN_CSV,
    NEXT_REVIEW_ACTIONS_CSV,
    NEXT_STEPS_CSV,
]

DWH11_TABLES = [
    "dwh11_external_evidence_verification",
    "dwh11_external_source_retrieval_log",
    "dwh11_evidence_review_queue",
    "dwh11_external_evidence_run_log",
]

DWH11_VIEWS = [
    "qsb_v_dwh11_external_evidence_dashboard",
    "qsb_v_dwh11_evidence_status_by_token",
    "qsb_v_dwh11_open_review_queue",
    "qsb_v_dwh11_next_evidence_actions",
]

DWH08_EXPECTED_COUNTS = {
    "map_token_dictionary": 91,
    "map_token_value_assertion": 10,
    "map_assertion_evidence": 10,
    "map_review_decision": 52,
    "map_evidence_gap": 54,
}

REQUIRED_DWH08_TABLES = list(DWH08_EXPECTED_COUNTS)

FOCUS_TOKENS = [
    "tim_token_007",
    "tim_token_011",
    "tim_token_013",
    "tim_token_017",
    "tim_token_023",
]

TERMS_TO_VERIFY = [
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

SOURCE_FALLBACKS = {
    "receiver": ("GBO / GBT Receiver and Backend Documentation", "https://greenbankobservatory.org/"),
    "backend": ("GBO / GBT Receiver and Backend Documentation", "https://greenbankobservatory.org/"),
    "composite": ("IPTA POD", "https://ipta4gw.org/"),
    "numeric": ("IPTA POD / PSRFITS / release metadata class", "https://ipta4gw.org/"),
}

CLAIM_BOUNDARY = (
    "DWH11 is a workcopy-only controlled evidence-status recording step for "
    "the five DWH10 block-switch token candidates. In no-live mode it uses "
    "existing DB28/DWH08/DWH10 seed rows as context and records live external "
    "verification as not performed. It does not modify the live DB, does not "
    "read raw TIM/PAR files, does not touch all raw_field_value rows, does not "
    "create bridge/result tables, does not verify final semantics, does not "
    "compute timing/model/statistical quantities, and does not make physical "
    "interpretation statements."
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


def is_completable_partial_counts(counts: dict[str, int]) -> bool:
    return counts == {
        "dwh11_external_evidence_verification": len(TERMS_TO_VERIFY),
        "dwh11_external_source_retrieval_log": len(TERMS_TO_VERIFY),
        "dwh11_evidence_review_queue": len(TERMS_TO_VERIFY),
        "dwh11_external_evidence_run_log": 0,
    }


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
            "Refusing to overwrite existing DWH11 output file(s): "
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
        missing_dwh10 = [
            "dwh10_block_switch_mapping_refinement"
            for name in ["dwh10_block_switch_mapping_refinement"]
            if not object_exists(con, name, "table")
        ]
        dwh10_count = (
            table_count(con, "dwh10_block_switch_mapping_refinement")
            if object_exists(con, "dwh10_block_switch_mapping_refinement", "table")
            else None
        )
        missing_dwh08 = [
            table for table in REQUIRED_DWH08_TABLES
            if not object_exists(con, table, "table")
        ]
        dwh08_counts = {
            table: table_count(con, table)
            for table in DWH08_EXPECTED_COUNTS
            if object_exists(con, table, "table")
        }
        existing_dwh11 = [
            name for name in [*DWH11_TABLES, *DWH11_VIEWS]
            if object_exists(con, name)
        ]
        existing_dwh11_rows = {
            table: table_count(con, table)
            for table in DWH11_TABLES
            if object_exists(con, table, "table")
        }

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if missing_dwh10:
        raise RuntimeError("Missing DWH10 table(s): " + ", ".join(missing_dwh10))
    if dwh10_count != 5:
        raise RuntimeError(f"DWH10 refinement row count must be 5, got {dwh10_count}.")
    if missing_dwh08:
        raise RuntimeError("Missing DWH08 map table(s): " + ", ".join(missing_dwh08))
    dwh08_mismatches = [
        f"{table}: expected {expected}, got {dwh08_counts.get(table)}"
        for table, expected in DWH08_EXPECTED_COUNTS.items()
        if dwh08_counts.get(table) != expected
    ]
    if dwh08_mismatches:
        raise RuntimeError("DWH08 map count mismatch: " + "; ".join(dwh08_mismatches))
    resume_partial = is_completable_partial_counts(existing_dwh11_rows)
    if existing_dwh11 and not allow_existing and not resume_partial:
        raise RuntimeError(
            "DWH11 target object(s) already exist; use --allow-existing only "
            "for controlled empty-object continuation: " + ", ".join(existing_dwh11)
        )
    nonempty_existing = [
        f"{table}={count}"
        for table, count in existing_dwh11_rows.items()
        if count > 0
    ]
    if nonempty_existing and not resume_partial:
        raise RuntimeError(
            "Refusing to append to nonempty DWH11 table(s): "
            + ", ".join(nonempty_existing)
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "dwh10_refinement_count": dwh10_count,
        "dwh08_counts_before": dwh08_counts,
        "resume_partial_dwh11": resume_partial,
    }


def create_tables(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    con.executescript(
        f"""
        CREATE TABLE {clause}dwh11_external_evidence_verification (
            verification_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            proposed_role TEXT,
            verification_status TEXT NOT NULL,
            evidence_strength TEXT NOT NULL,
            evidence_source_label TEXT,
            evidence_url TEXT,
            evidence_summary TEXT,
            retrieval_status TEXT NOT NULL,
            retrieved_at_utc TEXT,
            review_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}dwh11_external_source_retrieval_log (
            retrieval_id TEXT PRIMARY KEY,
            retrieval_timestamp_utc TEXT,
            source_label TEXT,
            source_url TEXT,
            retrieval_mode TEXT NOT NULL,
            retrieval_status TEXT NOT NULL,
            term TEXT,
            notes TEXT
        );

        CREATE TABLE {clause}dwh11_evidence_review_queue (
            review_queue_id TEXT PRIMARY KEY,
            token_position TEXT NOT NULL,
            term TEXT NOT NULL,
            recommended_action TEXT NOT NULL,
            priority TEXT NOT NULL,
            blocking_status TEXT NOT NULL,
            depends_on TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}dwh11_external_evidence_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            verified_term_count INTEGER,
            open_gap_count INTEGER,
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
        CREATE VIEW {clause}qsb_v_dwh11_external_evidence_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'dwh11_external_evidence_run_log' AS metric_source,
               notes AS dashboard_note
        FROM dwh11_external_evidence_run_log
        UNION ALL
        SELECT 'verification_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh11_external_evidence_verification',
               'One row per DWH11 requested term.'
        FROM dwh11_external_evidence_verification
        UNION ALL
        SELECT 'evidence_supported_candidate_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh11_external_evidence_verification',
               'Rows with controlled evidence support.'
        FROM dwh11_external_evidence_verification
        WHERE verification_status = 'evidence_supported_candidate'
        UNION ALL
        SELECT 'open_gap_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh11_external_evidence_verification',
               'Rows that remain open evidence gaps.'
        FROM dwh11_external_evidence_verification
        WHERE verification_status = 'evidence_gap_open'
        UNION ALL
        SELECT 'conflict_or_mismatch_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh11_external_evidence_verification',
               'Rows with evidence conflict or mismatch.'
        FROM dwh11_external_evidence_verification
        WHERE verification_status = 'evidence_conflict_or_mismatch'
        UNION ALL
        SELECT 'review_queue_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh11_evidence_review_queue',
               'Rows requiring later evidence review.'
        FROM dwh11_evidence_review_queue
        UNION ALL
        SELECT 'retrieval_log_rows',
               CAST(COUNT(*) AS TEXT),
               'dwh11_external_source_retrieval_log',
               'No-live retrieval log rows.'
        FROM dwh11_external_source_retrieval_log
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DWH11 insertions.'
        FROM dwh11_external_evidence_run_log;

        CREATE VIEW {clause}qsb_v_dwh11_evidence_status_by_token AS
        SELECT
            token_position,
            MIN(proposed_role) AS candidate_role,
            COUNT(*) AS checked_term_count,
            SUM(CASE WHEN verification_status = 'evidence_supported_candidate' THEN 1 ELSE 0 END) AS supported_term_count,
            SUM(CASE WHEN verification_status = 'evidence_gap_open' THEN 1 ELSE 0 END) AS open_gap_count,
            SUM(CASE WHEN verification_status = 'evidence_conflict_or_mismatch' THEN 1 ELSE 0 END) AS conflict_count,
            CASE
                WHEN SUM(CASE WHEN verification_status = 'evidence_conflict_or_mismatch' THEN 1 ELSE 0 END) > 0
                THEN 'evidence_conflict_or_mismatch'
                WHEN SUM(CASE WHEN verification_status = 'evidence_gap_open' THEN 1 ELSE 0 END) > 0
                 AND SUM(CASE WHEN verification_status = 'evidence_supported_candidate' THEN 1 ELSE 0 END) > 0
                THEN 'mixed_supported_and_open'
                WHEN SUM(CASE WHEN verification_status = 'evidence_gap_open' THEN 1 ELSE 0 END) > 0
                THEN 'evidence_gaps_open'
                WHEN SUM(CASE WHEN verification_status = 'evidence_supported_candidate' THEN 1 ELSE 0 END) = COUNT(*)
                THEN 'all_checked_terms_supported'
                ELSE 'not_reviewed'
            END AS overall_evidence_status,
            CASE
                WHEN SUM(CASE WHEN verification_status = 'evidence_gap_open' THEN 1 ELSE 0 END) > 0
                THEN 'Perform targeted live external retrieval or manual source review before controlled mapping update.'
                ELSE 'Human review may consider controlled mapping-status update.'
            END AS recommended_next_action
        FROM dwh11_external_evidence_verification
        GROUP BY token_position
        ORDER BY token_position;

        CREATE VIEW {clause}qsb_v_dwh11_open_review_queue AS
        SELECT *
        FROM dwh11_evidence_review_queue
        ORDER BY
            CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 ELSE 3 END,
            token_position,
            term;

        CREATE VIEW {clause}qsb_v_dwh11_next_evidence_actions AS
        SELECT
            review_queue_id AS action_id,
            token_position,
            term,
            recommended_action,
            priority,
            blocking_status,
            depends_on,
            notes
        FROM dwh11_evidence_review_queue
        ORDER BY
            CASE priority WHEN 'P1' THEN 1 WHEN 'P2' THEN 2 ELSE 3 END,
            token_position,
            term;
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


def load_dwh10_by_token(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_position, proposed_structural_role, evidence_need,
               proposed_controlled_field_name
        FROM dwh10_block_switch_mapping_refinement
        ORDER BY token_position
        """,
    )
    return {str(row["token_position"]): row for row in rows}


def load_source_registry(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    if not object_exists(con, "db28_external_source_registry", "table"):
        return {}
    rows = fetch_dicts(
        con,
        """
        SELECT source_id, source_name, institution, official_url, retrieval_status
        FROM db28_external_source_registry
        ORDER BY source_id
        """,
    )
    return {str(row["source_id"]): row for row in rows}


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
               evidence_status, assertion_status, evidence_summary,
               confidence_class
        FROM db28_external_dictionary_seed
        ORDER BY dictionary_seed_id
        """,
    )
    return {str(row["raw_term"]): row for row in rows}


def term_category(term: str, token_position: str) -> str:
    if token_position in {"tim_token_013", "tim_token_023"}:
        return "numeric"
    if "J0740+6620" in term:
        return "composite"
    if "GUPPI" in term:
        return "backend"
    return "receiver"


def source_label_and_url(
    term: str,
    token_position: str,
    assertions: dict[str, dict[str, Any]],
    seeds: dict[str, dict[str, Any]],
    sources: dict[str, dict[str, Any]],
) -> tuple[str, str, str]:
    row = assertions.get(term) or seeds.get(term)
    if row and row.get("source_id") in sources:
        source = sources[str(row["source_id"])]
        label = f"{source['source_name']} / {source['institution']}"
        return label, str(source["official_url"]), str(row.get("evidence_summary") or "")
    category = term_category(term, token_position)
    label, url = SOURCE_FALLBACKS[category]
    return label, url, "No matching DB28 term-level seed row found; source class retained from controlled source preference."


def build_verification_rows(
    con: sqlite3.Connection,
    created_at: str,
    no_live_retrieval: bool,
) -> list[dict[str, Any]]:
    if not no_live_retrieval:
        raise RuntimeError("Live retrieval is not implemented in this controlled DWH11 runner.")
    dwh10 = load_dwh10_by_token(con)
    assertions = load_assertions_by_term(con)
    seeds = load_dictionary_seed_by_term(con)
    sources = load_source_registry(con)
    rows: list[dict[str, Any]] = []
    for idx, (token_position, term) in enumerate(TERMS_TO_VERIFY, start=1):
        if token_position not in dwh10:
            raise RuntimeError(f"DWH10 token missing for DWH11 term: {token_position} / {term}")
        source_label, source_url, seed_summary = source_label_and_url(
            term,
            token_position,
            assertions,
            seeds,
            sources,
        )
        assertion = assertions.get(term)
        seed = seeds.get(term)
        seed_status = None
        if assertion:
            seed_status = f"db28_assertion_status={assertion['assertion_status']}; db28_evidence_status={assertion['evidence_status']}"
        elif seed:
            seed_status = f"db28_seed_status={seed['assertion_status']}; db28_evidence_status={seed['evidence_status']}"
        else:
            seed_status = "no_db28_term_seed"
        rows.append(
            {
                "verification_id": f"dwh11_verification_{idx:03d}",
                "token_position": token_position,
                "term": term,
                "proposed_role": dwh10[token_position]["proposed_structural_role"],
                "verification_status": "evidence_gap_open",
                "evidence_strength": "none_or_insufficient",
                "evidence_source_label": source_label,
                "evidence_url": source_url,
                "evidence_summary": (
                    "No live external retrieval was performed in DWH11. "
                    "Existing DB28 seed context is not sufficient to verify the candidate term/role. "
                    + seed_summary
                ),
                "retrieval_status": "not_verified_live",
                "retrieved_at_utc": None,
                "review_status": "needs_external_evidence_review",
                "created_at_utc": created_at,
                "notes": f"{seed_status}; no DWH08 map_assertion_evidence row added in no-live mode",
            }
        )
    return rows


def build_retrieval_log_rows(
    verification_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    return [
        {
            "retrieval_id": f"dwh11_retrieval_{idx:03d}",
            "retrieval_timestamp_utc": created_at,
            "source_label": row["evidence_source_label"],
            "source_url": row["evidence_url"],
            "retrieval_mode": "no_live_retrieval",
            "retrieval_status": "not_verified_live",
            "term": row["term"],
            "notes": "No internet/live retrieval was used; verification remains an open evidence gap.",
        }
        for idx, row in enumerate(verification_rows, start=1)
    ]


def priority_for_token(token_position: str) -> str:
    if token_position in {"tim_token_007", "tim_token_011", "tim_token_017"}:
        return "P1"
    return "P2"


def build_review_queue_rows(
    verification_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, row in enumerate(verification_rows, start=1):
        rows.append(
            {
                "review_queue_id": f"dwh11_review_queue_{idx:03d}",
                "token_position": row["token_position"],
                "term": row["term"],
                "recommended_action": (
                    "Perform controlled live external retrieval or manual source review before any mapping-status update."
                ),
                "priority": priority_for_token(row["token_position"]),
                "blocking_status": "blocks_controlled_definition",
                "depends_on": row["evidence_source_label"],
                "created_at_utc": created_at,
                "notes": "Opened because DWH11 ran in no-live mode and did not verify the term externally.",
            }
        )
    return rows


def validate_existing_partial_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    expected_pairs = set(TERMS_TO_VERIFY)
    verification_rows = fetch_dicts(
        con,
        """
        SELECT token_position, term, proposed_role, verification_status,
               evidence_strength, retrieval_status, review_status
        FROM dwh11_external_evidence_verification
        ORDER BY token_position, term
        """,
    )
    actual_pairs = {
        (str(row["token_position"]), str(row["term"]))
        for row in verification_rows
    }
    if actual_pairs != expected_pairs:
        raise RuntimeError("Existing partial DWH11 verification rows do not match requested terms.")
    bad_verification_rows = [
        row for row in verification_rows
        if row["verification_status"] != "evidence_gap_open"
        or row["evidence_strength"] != "none_or_insufficient"
        or row["retrieval_status"] != "not_verified_live"
        or row["review_status"] != "needs_external_evidence_review"
    ]
    if bad_verification_rows:
        raise RuntimeError("Existing partial DWH11 verification rows have unexpected no-live statuses.")

    retrieval_rows = fetch_dicts(
        con,
        """
        SELECT term, retrieval_mode, retrieval_status
        FROM dwh11_external_source_retrieval_log
        ORDER BY retrieval_id
        """,
    )
    if len(retrieval_rows) != len(TERMS_TO_VERIFY):
        raise RuntimeError("Existing partial DWH11 retrieval-log row count is unexpected.")
    if {str(row["term"]) for row in retrieval_rows} != {term for _, term in TERMS_TO_VERIFY}:
        raise RuntimeError("Existing partial DWH11 retrieval-log terms are unexpected.")
    bad_retrieval_rows = [
        row for row in retrieval_rows
        if row["retrieval_mode"] != "no_live_retrieval"
        or row["retrieval_status"] != "not_verified_live"
    ]
    if bad_retrieval_rows:
        raise RuntimeError("Existing partial DWH11 retrieval-log rows have unexpected statuses.")

    review_rows = fetch_dicts(
        con,
        """
        SELECT token_position, term, blocking_status
        FROM dwh11_evidence_review_queue
        ORDER BY token_position, term
        """,
    )
    if len(review_rows) != len(TERMS_TO_VERIFY):
        raise RuntimeError("Existing partial DWH11 review-queue row count is unexpected.")
    review_pairs = {
        (str(row["token_position"]), str(row["term"]))
        for row in review_rows
    }
    if review_pairs != expected_pairs:
        raise RuntimeError("Existing partial DWH11 review-queue rows do not match requested terms.")
    if any(row["blocking_status"] != "blocks_controlled_definition" for row in review_rows):
        raise RuntimeError("Existing partial DWH11 review-queue rows have unexpected blocking status.")

    return verification_rows


def insert_run_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    live_modified: bool,
    verified_term_count: int,
    open_gap_count: int,
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh11_external_evidence_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            verified_term_count,
            open_gap_count,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(live_db),
            str(workcopy_db),
            SCRIPT_NAME,
            "workcopy_external_evidence_verification_no_live",
            1 if live_modified else 0,
            1,
            verified_term_count,
            open_gap_count,
            integrity,
            fk_count,
            "DWH11 ran in no-live retrieval mode; verification rows remain open evidence gaps.",
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
    dwh11_counts = {table: table_count(con, table) for table in DWH11_TABLES}
    view_counts = {view: table_count(con, view) for view in DWH11_VIEWS if object_exists(con, view, "view")}
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
        "dwh08_map_counts": dwh08_preserved,
        "dwh08_preservation_status": (
            "passed"
            if all(item["status"] == "passed" for item in dwh08_preserved.values())
            else "failed"
        ),
        "dwh11_table_counts": dwh11_counts,
        "dwh11_view_counts": view_counts,
        "dwh11_views_queryable": len(view_counts) == len(DWH11_VIEWS),
        "live_db_sha256_before": live_before["sha256"],
        "live_db_sha256_after": live_after["sha256"],
        "live_db_stat_before": live_before["stat"],
        "live_db_stat_after": live_after["stat"],
        "live_db_checksum_unchanged": live_before["sha256"] == live_after["sha256"],
        "live_db_stat_unchanged": live_before["stat"] == live_after["stat"],
    }


def next_dwh_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH12_A",
            "next_step_name": "Controlled update of mapping review statuses for evidence-supported candidates only",
            "prerequisite": "At least one DWH11 candidate has externally verified evidence support",
            "recommended_action": "Promote only evidence-supported candidates in a controlled workcopy step.",
            "risk_level": "medium",
            "notes": "Not recommended until no-live gaps are resolved.",
        },
        {
            "next_step_id": "DWH12_B",
            "next_step_name": "DBeaver/ERD visual check of evidence verification layer",
            "prerequisite": "DWH11 tables/views are present and queryable",
            "recommended_action": "Inspect DWH11 verification and review-queue tables beside DWH10/DWH08.",
            "risk_level": "low",
            "notes": "Useful immediate follow-up for the new verification layer.",
        },
        {
            "next_step_id": "DWH12_C",
            "next_step_name": "Shapiro-Mart design after evidence-supported mapping candidates are separated from gaps",
            "prerequisite": "Evidence-supported mapping candidates are separated from open evidence gaps",
            "recommended_action": "Defer design work until evidence statuses are no longer all open gaps.",
            "risk_level": "high",
            "notes": "DWH11 no-live mode does not support this yet.",
        },
        {
            "next_step_id": "DWH12_D",
            "next_step_name": "Targeted external evidence follow-up for open gaps",
            "prerequisite": "DWH11 open review queue exists",
            "recommended_action": "Perform controlled live retrieval or manual source review for GBO/GBT, IPTA, NANOGrav, PSRFITS, and release metadata classes.",
            "risk_level": "medium",
            "notes": "Recommended next step because all DWH11 terms remain open gaps in no-live mode.",
        },
    ]


def fetch_all(con: sqlite3.Connection, source_name: str) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {quote_identifier(source_name)}")


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
    verification_rows = fetch_dicts(
        con,
        """
        SELECT token_position, term, proposed_role, verification_status,
               evidence_strength, evidence_source_label, evidence_url,
               retrieval_status, review_status, notes
        FROM dwh11_external_evidence_verification
        ORDER BY token_position, term
        """,
    )
    source_rows = fetch_all(con, "dwh11_external_source_retrieval_log")
    status_rows = fetch_all(con, "qsb_v_dwh11_evidence_status_by_token")
    review_rows = fetch_all(con, "qsb_v_dwh11_next_evidence_actions")
    supported = [row for row in verification_rows if row["verification_status"] == "evidence_supported_candidate"]
    gaps = [row for row in verification_rows if row["verification_status"] == "evidence_gap_open"]
    conflicts = [row for row in verification_rows if row["verification_status"] == "evidence_conflict_or_mismatch"]
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH controlled evidence verification in workcopy only",
        "data_substrate_used": str(workcopy_db),
        "live_retrieval_mode_used": "no_live_retrieval" if no_live_retrieval else "live_retrieval_requested",
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "raw_tim_par_files_read": False,
        "new_isolated_analysis_db_created": False,
        "raw_field_value_bulk_touch_performed": False,
        "bridge_or_result_tables_created": False,
        "dwh08_map_assertion_evidence_rows_added": 0,
        "terms_checked": verification_rows,
        "term_count": len(verification_rows),
        "supported_candidate_count": len(supported),
        "open_gap_count": len(gaps),
        "conflict_count": len(conflicts),
        "source_rows_used": source_rows,
        "evidence_status_by_token": status_rows,
        "review_queue_rows": review_rows,
        "review_queue_count": len(review_rows),
        "next_dwh_steps": next_dwh_steps_rows(),
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
            "dwh10_refinement_count": preflight["dwh10_refinement_count"],
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


def format_status_lines(rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        "- {token_position}: checked={checked_term_count}; supported={supported_term_count}; gaps={open_gap_count}; conflicts={conflict_count}; status={overall_evidence_status}".format(**row)
        for row in rows
    )


def format_term_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {token_position}: {term}; status={verification_status}; source={evidence_source_label}; retrieval={retrieval_status}".format(**row)
        for row in rows
    )


def format_review_lines(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "- None."
    return "\n".join(
        "- {action_id}: {token_position}; term={term}; priority={priority}; blocking={blocking_status}; depends_on={depends_on}".format(**row)
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
    next_lines = "\n".join(
        "- {next_step_id}: {next_step_name}".format(**row)
        for row in summary["next_dwh_steps"]
    )
    unique_sources = sorted({row["source_label"] for row in summary["source_rows_used"]})
    source_lines = "\n".join(f"- {source}" for source in unique_sources)
    content = f"""# QSB-DWH11 External Evidence Verification Readout

## 1. Executive summary

Befund: DWH11 recorded evidence-verification status for the DWH10 five-token candidate set in no-live retrieval mode.

- Run ID: `{summary['run_id']}`
- Workcopy DB: `{summary['workcopy_db_path']}`
- Live retrieval mode: {summary['live_retrieval_mode_used']}
- Terms checked: {summary['term_count']}
- Supported candidates: {summary['supported_candidate_count']}
- Open evidence gaps: {summary['open_gap_count']}
- Conflicts or mismatches: {summary['conflict_count']}
- Review queue rows: {summary['review_queue_count']}

## 2. Workcopy-only principle

DWH11 writes were limited to the workcopy DB. Existing DWH08 map_* rows were not rewritten and no DWH08 map_assertion_evidence rows were added in no-live mode.

## 3. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH11: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH11: {live_status}

## 4. Evidence sources used

No live external retrieval was performed. The following controlled source labels were used as source classes from existing DB28 seed/source rows:

{source_lines}

## 5. Verification status by token

{format_status_lines(summary['evidence_status_by_token'])}

## 6. Supported candidates

{format_term_lines([row for row in summary['terms_checked'] if row['verification_status'] == 'evidence_supported_candidate'])}

## 7. Open evidence gaps

{format_term_lines([row for row in summary['terms_checked'] if row['verification_status'] == 'evidence_gap_open'])}

## 8. Conflicts or mismatches

{format_term_lines([row for row in summary['terms_checked'] if row['verification_status'] == 'evidence_conflict_or_mismatch'])}

## 9. Review queue

{format_review_lines(summary['review_queue_rows'])}

## 10. Integration with Mapping/Evidence layer

DWH11 did not add rows to DWH08 `map_assertion_evidence` because no live external evidence was retrieved. Existing DB28/DWH08 seed rows were used only as context for source classes and gap notes.

## 11. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- DWH10 refinement rows preserved: {summary['validation']['dwh10_preservation_status']}
- DWH08 map counts preserved: {'passed' if not dwh08_failed else 'failed: ' + ', '.join(dwh08_failed)}
- DWH11 views queryable: {summary['validation']['dwh11_views_queryable']}

## 12. What DWH11 does not do

DWH11 does not read raw TIM/PAR files, does not create a new isolated analysis DB, does not touch all raw_field_value rows, does not create bridge/result tables, does not assign final physical meaning to TIM columns, does not compute timing/model/statistical quantities, and does not make physical interpretation statements.

## 13. Recommended DWH12 options

{next_lines}

## 14. Claim boundary

{summary['claim_boundary']}
"""
    path.write_text(content, encoding="utf-8")


def write_outputs(con: sqlite3.Connection, output_root: Path, summary: dict[str, Any]) -> None:
    paths = output_paths(output_root)
    write_readout(paths[READOUT_MD], summary)
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    write_csv(
        paths[CANDIDATE_VERIFICATION_CSV],
        [
            "token_position",
            "term",
            "proposed_role",
            "verification_status",
            "evidence_strength",
            "evidence_source_label",
            "evidence_url",
            "retrieval_status",
            "review_status",
            "notes",
        ],
        fetch_dicts(
            con,
            """
            SELECT token_position, term, proposed_role, verification_status,
                   evidence_strength, evidence_source_label, evidence_url,
                   retrieval_status, review_status, notes
            FROM dwh11_external_evidence_verification
            ORDER BY token_position, term
            """,
        ),
    )
    write_csv(
        paths[RETRIEVAL_LOG_CSV],
        [
            "retrieval_timestamp_utc",
            "source_label",
            "source_url",
            "retrieval_mode",
            "retrieval_status",
            "term",
            "notes",
        ],
        fetch_dicts(
            con,
            """
            SELECT retrieval_timestamp_utc, source_label, source_url,
                   retrieval_mode, retrieval_status, term, notes
            FROM dwh11_external_source_retrieval_log
            ORDER BY retrieval_id
            """,
        ),
    )
    write_csv(
        paths[STATUS_BY_TOKEN_CSV],
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
        fetch_all(con, "qsb_v_dwh11_evidence_status_by_token"),
    )
    write_csv(
        paths[NEXT_REVIEW_ACTIONS_CSV],
        [
            "action_id",
            "token_position",
            "term",
            "recommended_action",
            "priority",
            "blocking_status",
            "depends_on",
            "notes",
        ],
        fetch_all(con, "qsb_v_dwh11_next_evidence_actions"),
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
    no_live_retrieval: bool,
) -> dict[str, Any]:
    if not no_live_retrieval:
        raise RuntimeError("DWH11 live retrieval mode is not implemented; rerun with --no-live-retrieval.")
    live_before = db_state(live_db)
    preflight = ensure_preconditions(
        live_db,
        workcopy_db,
        output_root,
        overwrite,
        allow_existing,
    )
    created_at = utc_now()
    run_id = "DWH11_EXTERNAL_EVIDENCE_VERIFICATION_" + timestamp_for_id()

    with connect_writable(workcopy_db) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            if preflight["resume_partial_dwh11"]:
                verification_rows = validate_existing_partial_rows(con)
                create_views(con, True)
            else:
                create_tables(con, allow_existing)
                verification_rows = build_verification_rows(con, created_at, no_live_retrieval)
                if len(verification_rows) != len(TERMS_TO_VERIFY):
                    raise RuntimeError(
                        f"Expected {len(TERMS_TO_VERIFY)} verification rows, got {len(verification_rows)}."
                    )
                retrieval_rows = build_retrieval_log_rows(verification_rows, created_at)
                review_rows = build_review_queue_rows(verification_rows, created_at)
                insert_rows(con, "dwh11_external_evidence_verification", verification_rows)
                insert_rows(con, "dwh11_external_source_retrieval_log", retrieval_rows)
                insert_rows(con, "dwh11_evidence_review_queue", review_rows)
                create_views(con, allow_existing)
            live_after = db_state(live_db)
            validation_before_log = validate_workcopy(con, live_before, live_after)
            supported_count = sum(
                1 for row in verification_rows
                if row["verification_status"] == "evidence_supported_candidate"
            )
            open_gap_count = sum(
                1 for row in verification_rows
                if row["verification_status"] == "evidence_gap_open"
            )
            insert_run_log(
                con,
                run_id,
                created_at,
                live_db,
                workcopy_db,
                not validation_before_log["live_db_checksum_unchanged"]
                or not validation_before_log["live_db_stat_unchanged"],
                supported_count,
                open_gap_count,
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
                no_live_retrieval,
            )
            write_outputs(con, output_root, summary)
            con.commit()
        except Exception:
            con.rollback()
            raise
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QSB-DWH11 controlled evidence-status recording for DWH10 candidates."
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
        help="Existing output directory for DWH11 reports.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the seven DWH11 report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH11 target objects; never appends to nonempty DWH11 tables.",
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
        help="Request live retrieval. This controlled runner refuses it unless implemented later.",
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
