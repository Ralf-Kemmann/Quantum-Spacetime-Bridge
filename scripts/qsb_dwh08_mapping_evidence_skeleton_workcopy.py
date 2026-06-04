#!/usr/bin/env python3
"""QSB-DWH08: mapping/evidence target skeleton in the workcopy.

This script adds a minimal target map_* layer to the DWH workcopy database and
populates it from existing DB26/DB27/DB28 mapping and evidence artifacts already
inside that same workcopy. The live DB is opened read-only for protection and
validation only.

It does not read raw TIM/PAR files, does not use report exports as input, does
not create bridge/result tables, does not compute timing/model/statistical
quantities, and does not assign final controlled meanings to unresolved TIM
columns.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh08_mapping_evidence_skeleton_workcopy.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh08_mapping_evidence_skeleton_readout.md"
SUMMARY_JSON = "dwh08_mapping_evidence_skeleton_summary.json"
TABLE_COUNTS_CSV = "dwh08_mapping_evidence_table_counts.csv"
TOKEN_DICTIONARY_PREVIEW_CSV = "dwh08_token_dictionary_preview.csv"
EVIDENCE_GAP_PREVIEW_CSV = "dwh08_evidence_gap_preview.csv"
NEXT_DWH_STEPS_CSV = "dwh08_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    TABLE_COUNTS_CSV,
    TOKEN_DICTIONARY_PREVIEW_CSV,
    EVIDENCE_GAP_PREVIEW_CSV,
    NEXT_DWH_STEPS_CSV,
]

MAP_TABLES = [
    "map_token_dictionary",
    "map_token_value_assertion",
    "map_assertion_evidence",
    "map_review_decision",
    "map_evidence_gap",
]

TARGET_TABLES = [
    *MAP_TABLES,
    "dwh08_mapping_evidence_run_log",
]

TARGET_VIEWS = [
    "qsb_v_dwh08_mapping_evidence_dashboard",
    "qsb_v_dwh08_token_dictionary_status",
    "qsb_v_dwh08_open_evidence_gaps",
    "qsb_v_dwh08_next_mapping_actions",
]

INDEXES = [
    (
        "idx_dwh08_map_token_dictionary_family_position",
        "map_token_dictionary(line_family, token_position)",
    ),
    (
        "idx_dwh08_map_token_value_assertion_dictionary",
        "map_token_value_assertion(token_dictionary_id)",
    ),
    (
        "idx_dwh08_map_assertion_evidence_value_assertion",
        "map_assertion_evidence(token_value_assertion_id)",
    ),
    (
        "idx_dwh08_map_review_decision_dictionary",
        "map_review_decision(token_dictionary_id)",
    ),
    (
        "idx_dwh08_map_review_decision_evidence",
        "map_review_decision(evidence_id)",
    ),
    (
        "idx_dwh08_map_evidence_gap_dictionary",
        "map_evidence_gap(token_dictionary_id)",
    ),
]

DWH05_EXPECTED_COUNTS = {
    "core_source_registry": 1,
    "core_dataset": 1,
    "core_observation": 1,
    "raw_source_file": 2,
    "raw_ingest_run": 2,
    "raw_record": 11395,
    "raw_field_value": 471874,
    "core_observation_record_link": 11395,
}

DWH06_DIMENSION_TABLES = [
    "dim_science_object",
    "dim_telescope",
    "dim_receiver",
    "dim_backend",
    "dim_time_context",
    "dim_processing_context",
    "dim_quality_status",
]

DICTIONARY_SOURCE_PREFERENCE = [
    "db26_field_dictionary_seed",
    "qsb_v_db26_field_dictionary_seed",
    "db27_mapping_work_packet",
    "qsb_v_db27_first_mapping_work_packet",
]

REVIEW_SOURCE_PREFERENCE = [
    "db27_manual_mapping_priority",
    "db27_mapping_work_packet",
    "qsb_v_db27_first_mapping_work_packet",
]

ASSERTION_SOURCE_PREFERENCE = [
    "db28_mapping_assertion_evidence",
    "qsb_v_db28_mapping_assertion_evidence",
]

TOKEN_LINK_SOURCE_PREFERENCE = [
    "db28_db27_token_evidence_link",
    "qsb_v_db28_db27_token_evidence_link",
]

CANONICAL_SOURCE_PREFERENCE = [
    "qsb_v_db28_dictionary_seed",
    "db28_dictionary_seed",
    "db28_external_dictionary_seed",
]

DB28_GAP_SOURCE_PREFERENCE = [
    "qsb_v_db28_external_evidence_gap",
    "db28_open_external_evidence_gap",
]

CLAIM_BOUNDARY = (
    "DWH08 is a workcopy-only mapping/evidence schema integration step. It "
    "creates target map_* tables and views, then copies conservative structural "
    "dictionary, review, assertion/evidence, and gap rows from existing DB26, "
    "DB27, and DB28 objects inside the workcopy. It does not modify the live DB, "
    "does not read raw TIM/PAR files, does not use report exports as input, does "
    "not create bridge/result tables, does not compute timing/model/statistical "
    "quantities, and does not assign final controlled meanings to unresolved "
    "TIM columns."
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


def first_existing(con: sqlite3.Connection, names: list[str]) -> str | None:
    for name in names:
        if object_exists(con, name):
            return name
    return None


def source_count(con: sqlite3.Connection, source_name: str | None) -> int:
    if source_name is None:
        return 0
    return table_count(con, source_name)


def make_target_id(prefix: str, source_id: Any) -> str:
    source_text = "unknown" if source_id is None else str(source_id)
    fragment = re.sub(r"[^A-Za-z0-9_]+", "_", source_text.strip())
    fragment = re.sub(r"_+", "_", fragment).strip("_")
    return f"{prefix}{fragment or 'unknown'}"


def note_join(parts: list[Any]) -> str:
    return "; ".join(str(part) for part in parts if part not in (None, ""))


def dictionary_key(line_family: Any, token_position: Any) -> tuple[str | None, str | None]:
    family = None if line_family is None else str(line_family)
    token = None if token_position is None else str(token_position)
    return (family, token)


def lookup_dictionary_id(
    dictionary_ids_by_key: dict[tuple[str | None, str | None], str],
    line_family: Any,
    token_position: Any,
) -> str | None:
    key = dictionary_key(line_family, token_position)
    if key in dictionary_ids_by_key:
        return dictionary_ids_by_key[key]
    data_line_key = dictionary_key("data_line", token_position)
    if data_line_key in dictionary_ids_by_key:
        return dictionary_ids_by_key[data_line_key]
    return None


def ensure_no_outputs(output_root: Path, overwrite: bool) -> None:
    existing = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH08 output file(s): "
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
        missing_dwh05 = [
            table for table in DWH05_EXPECTED_COUNTS
            if not object_exists(con, table, "table")
        ]
        dwh05_counts = {
            table: table_count(con, table)
            for table in DWH05_EXPECTED_COUNTS
            if object_exists(con, table, "table")
        }
        empty_dwh05 = [
            table for table, count in dwh05_counts.items()
            if count <= 0
        ]
        missing_dwh06 = [
            table for table in DWH06_DIMENSION_TABLES
            if not object_exists(con, table, "table")
        ]
        dwh06_counts = {
            table: table_count(con, table)
            for table in DWH06_DIMENSION_TABLES
            if object_exists(con, table, "table")
        }
        existing_targets = [
            name for name in [*TARGET_TABLES, *TARGET_VIEWS]
            if object_exists(con, name)
        ]
        existing_target_rows = {
            table: table_count(con, table)
            for table in TARGET_TABLES
            if object_exists(con, table, "table")
        }
        dictionary_source = first_existing(con, DICTIONARY_SOURCE_PREFERENCE)
        review_source = first_existing(con, REVIEW_SOURCE_PREFERENCE)
        assertion_source = first_existing(con, ASSERTION_SOURCE_PREFERENCE)
        token_link_source = first_existing(con, TOKEN_LINK_SOURCE_PREFERENCE)
        canonical_source = first_existing(con, CANONICAL_SOURCE_PREFERENCE)
        db28_gap_source = first_existing(con, DB28_GAP_SOURCE_PREFERENCE)
        db26_gap_source = (
            "db26_mapping_gap_triage"
            if object_exists(con, "db26_mapping_gap_triage")
            else None
        )

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if missing_dwh05:
        raise RuntimeError("Missing DWH05 raw/core table(s): " + ", ".join(missing_dwh05))
    if empty_dwh05:
        raise RuntimeError("DWH05 raw/core table(s) have no migrated rows: " + ", ".join(empty_dwh05))
    if missing_dwh06:
        raise RuntimeError("Missing DWH06 dimension table(s): " + ", ".join(missing_dwh06))
    if existing_targets and not allow_existing:
        raise RuntimeError(
            "DWH08 target object(s) already exist; use --allow-existing only "
            "for controlled empty-object continuation: " + ", ".join(existing_targets)
        )
    nonempty_existing_targets = [
        f"{table}={count}"
        for table, count in existing_target_rows.items()
        if count > 0
    ]
    if nonempty_existing_targets:
        raise RuntimeError(
            "Refusing to append to nonempty DWH08 target table(s): "
            + ", ".join(nonempty_existing_targets)
        )
    if dictionary_source is None:
        raise RuntimeError(
            "No usable DB26/DB27 dictionary source found in the workcopy."
        )
    if review_source is None:
        raise RuntimeError("No usable DB27 review/worklist source found in the workcopy.")

    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "dwh05_counts_before": dwh05_counts,
        "dwh06_counts_before": dwh06_counts,
        "source_objects_selected": {
            "dictionary_source": dictionary_source,
            "db26_gap_source": db26_gap_source,
            "review_source": review_source,
            "assertion_source": assertion_source,
            "token_link_source": token_link_source,
            "canonical_source": canonical_source,
            "db28_gap_source": db28_gap_source,
        },
    }


def create_tables_and_indexes(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    con.executescript(
        f"""
        CREATE TABLE {clause}map_token_dictionary (
            token_dictionary_id TEXT PRIMARY KEY,
            line_family TEXT,
            token_position TEXT,
            proposed_structural_name TEXT,
            controlled_field_name TEXT,
            structural_role TEXT,
            mapping_status TEXT NOT NULL,
            review_status TEXT NOT NULL,
            source_legacy_object TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}map_token_value_assertion (
            token_value_assertion_id TEXT PRIMARY KEY,
            token_dictionary_id TEXT REFERENCES map_token_dictionary(token_dictionary_id),
            raw_value TEXT,
            proposed_canonical_value TEXT,
            assertion_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            source_legacy_object TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}map_assertion_evidence (
            evidence_id TEXT PRIMARY KEY,
            token_value_assertion_id TEXT REFERENCES map_token_value_assertion(token_value_assertion_id),
            evidence_source_label TEXT,
            evidence_term TEXT,
            evidence_summary TEXT,
            evidence_status TEXT NOT NULL,
            review_status TEXT NOT NULL,
            source_legacy_object TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}map_review_decision (
            review_decision_id TEXT PRIMARY KEY,
            token_dictionary_id TEXT REFERENCES map_token_dictionary(token_dictionary_id),
            evidence_id TEXT REFERENCES map_assertion_evidence(evidence_id),
            decision_status TEXT NOT NULL,
            decision_priority TEXT,
            decision_text TEXT,
            source_legacy_object TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}map_evidence_gap (
            evidence_gap_id TEXT PRIMARY KEY,
            token_dictionary_id TEXT REFERENCES map_token_dictionary(token_dictionary_id),
            gap_type TEXT NOT NULL,
            gap_severity TEXT,
            raw_value_or_term TEXT,
            required_external_source TEXT,
            blocking_status TEXT NOT NULL,
            source_legacy_object TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE {clause}dwh08_mapping_evidence_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            created_table_count INTEGER,
            inserted_dictionary_rows INTEGER,
            inserted_value_assertion_rows INTEGER,
            inserted_evidence_rows INTEGER,
            inserted_review_rows INTEGER,
            inserted_gap_rows INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT
        );
        """
    )
    index_clause = "IF NOT EXISTS " if allow_existing else ""
    for index_name, target_sql in INDEXES:
        con.execute(f"CREATE INDEX {index_clause}{index_name} ON {target_sql}")


def create_views(con: sqlite3.Connection, allow_existing: bool) -> None:
    clause = "IF NOT EXISTS " if allow_existing else ""
    con.executescript(
        f"""
        CREATE VIEW {clause}qsb_v_dwh08_token_dictionary_status AS
        SELECT
            d.token_dictionary_id,
            d.line_family,
            d.token_position,
            d.proposed_structural_name,
            d.controlled_field_name,
            d.structural_role,
            d.mapping_status,
            d.review_status,
            d.source_legacy_object,
            COUNT(DISTINCT v.token_value_assertion_id) AS value_assertion_count,
            COUNT(DISTINCT e.evidence_id) AS evidence_count,
            COUNT(DISTINCT r.review_decision_id) AS review_decision_count,
            COUNT(DISTINCT g.evidence_gap_id) AS evidence_gap_count,
            d.notes
        FROM map_token_dictionary AS d
        LEFT JOIN map_token_value_assertion AS v
          ON v.token_dictionary_id = d.token_dictionary_id
        LEFT JOIN map_assertion_evidence AS e
          ON e.token_value_assertion_id = v.token_value_assertion_id
        LEFT JOIN map_review_decision AS r
          ON r.token_dictionary_id = d.token_dictionary_id
        LEFT JOIN map_evidence_gap AS g
          ON g.token_dictionary_id = d.token_dictionary_id
        GROUP BY
            d.token_dictionary_id,
            d.line_family,
            d.token_position,
            d.proposed_structural_name,
            d.controlled_field_name,
            d.structural_role,
            d.mapping_status,
            d.review_status,
            d.source_legacy_object,
            d.notes
        ORDER BY d.line_family, d.token_position, d.token_dictionary_id;

        CREATE VIEW {clause}qsb_v_dwh08_open_evidence_gaps AS
        SELECT
            g.evidence_gap_id,
            g.gap_type,
            g.gap_severity,
            g.blocking_status,
            g.raw_value_or_term,
            g.required_external_source,
            d.token_dictionary_id,
            d.line_family,
            d.token_position,
            d.proposed_structural_name,
            g.source_legacy_object,
            g.notes
        FROM map_evidence_gap AS g
        LEFT JOIN map_token_dictionary AS d
          ON d.token_dictionary_id = g.token_dictionary_id
        ORDER BY
            CASE g.gap_severity
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
                WHEN 'info' THEN 4
                ELSE 5
            END,
            d.line_family,
            d.token_position,
            g.evidence_gap_id;

        CREATE VIEW {clause}qsb_v_dwh08_mapping_evidence_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'dwh08_mapping_evidence_run_log' AS metric_source,
               notes AS dashboard_note
        FROM dwh08_mapping_evidence_run_log
        UNION ALL
        SELECT 'map_token_dictionary_rows',
               CAST(COUNT(*) AS TEXT),
               'map_token_dictionary',
               'Target dictionary rows copied from DB26 or fallback DB27 source.'
        FROM map_token_dictionary
        UNION ALL
        SELECT 'map_token_value_assertion_rows',
               CAST(COUNT(*) AS TEXT),
               'map_token_value_assertion',
               'Value assertions created only from explicit DB28 assertion rows.'
        FROM map_token_value_assertion
        UNION ALL
        SELECT 'map_assertion_evidence_rows',
               CAST(COUNT(*) AS TEXT),
               'map_assertion_evidence',
               'Evidence rows copied from DB28 assertion/evidence seeds.'
        FROM map_assertion_evidence
        UNION ALL
        SELECT 'map_review_decision_rows',
               CAST(COUNT(*) AS TEXT),
               'map_review_decision',
               'Pending/proposed review rows copied from DB27 priority/worklist data.'
        FROM map_review_decision
        UNION ALL
        SELECT 'map_evidence_gap_rows',
               CAST(COUNT(*) AS TEXT),
               'map_evidence_gap',
               'Open mapping and external-evidence gap rows copied from DB26/DB28.'
        FROM map_evidence_gap
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DWH08 insertions.'
        FROM dwh08_mapping_evidence_run_log;

        CREATE VIEW {clause}qsb_v_dwh08_next_mapping_actions AS
        SELECT
            'gap_' || g.evidence_gap_id AS action_id,
            'resolve_evidence_gap' AS action_type,
            CASE g.gap_severity
                WHEN 'high' THEN 'P1'
                WHEN 'medium' THEN 'P2'
                WHEN 'low' THEN 'P3'
                ELSE 'P4'
            END AS action_priority,
            g.gap_type AS action_scope,
            COALESCE(g.required_external_source, 'manual mapping review') AS required_input,
            'pending' AS action_status,
            d.token_position,
            g.raw_value_or_term,
            g.notes,
            CASE g.gap_severity
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
                ELSE 4
            END AS sort_priority
        FROM map_evidence_gap AS g
        LEFT JOIN map_token_dictionary AS d
          ON d.token_dictionary_id = g.token_dictionary_id
        UNION ALL
        SELECT
            'review_' || r.review_decision_id AS action_id,
            'review_mapping_decision' AS action_type,
            CASE
                WHEN r.decision_priority LIKE '%tier_1%' THEN 'P1'
                WHEN r.decision_priority LIKE '%tier_2%' THEN 'P2'
                WHEN r.decision_priority LIKE '%tier_3%' THEN 'P3'
                ELSE 'P4'
            END AS action_priority,
            r.decision_status AS action_scope,
            COALESCE(r.decision_text, 'review mapping decision') AS required_input,
            'pending' AS action_status,
            d.token_position,
            NULL AS raw_value_or_term,
            r.notes,
            CASE
                WHEN r.decision_priority LIKE '%tier_1%' THEN 1
                WHEN r.decision_priority LIKE '%tier_2%' THEN 2
                WHEN r.decision_priority LIKE '%tier_3%' THEN 3
                ELSE 4
            END AS sort_priority
        FROM map_review_decision AS r
        LEFT JOIN map_token_dictionary AS d
          ON d.token_dictionary_id = r.token_dictionary_id
        ORDER BY sort_priority, token_position, action_id;
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


def load_dictionary_rows(
    con: sqlite3.Connection,
    source_name: str,
    created_at: str,
) -> tuple[list[dict[str, Any]], dict[tuple[str | None, str | None], str]]:
    source_sql = quote_identifier(source_name)
    rows: list[dict[str, Any]] = []
    dictionary_ids_by_key: dict[tuple[str | None, str | None], str] = {}

    if source_name in {"db26_field_dictionary_seed", "qsb_v_db26_field_dictionary_seed"}:
        source_rows = fetch_dicts(
            con,
            f"""
            SELECT dictionary_seed_id, line_family, token_position,
                   proposed_structural_name, structural_role_candidate,
                   mapping_status, evidence_source, evidence_summary,
                   manual_review_required, confidence_class
            FROM {source_sql}
            ORDER BY line_family, token_position, dictionary_seed_id
            """,
        )
        for row in source_rows:
            token_dictionary_id = make_target_id(
                "dwh08_dict__", row["dictionary_seed_id"]
            )
            review_status = (
                "needs_review"
                if int(row["manual_review_required"] or 0) == 1
                else "context_or_audit_seed"
            )
            rows.append(
                {
                    "token_dictionary_id": token_dictionary_id,
                    "line_family": row["line_family"],
                    "token_position": row["token_position"],
                    "proposed_structural_name": row["proposed_structural_name"],
                    "controlled_field_name": None,
                    "structural_role": row["structural_role_candidate"],
                    "mapping_status": row["mapping_status"] or "seed_only",
                    "review_status": review_status,
                    "source_legacy_object": source_name,
                    "created_at_utc": created_at,
                    "notes": note_join(
                        [
                            f"source_id={row['dictionary_seed_id']}",
                            f"evidence_source={row['evidence_source']}",
                            f"confidence_class={row['confidence_class']}",
                            row["evidence_summary"],
                        ]
                    ),
                }
            )
            dictionary_ids_by_key.setdefault(
                dictionary_key(row["line_family"], row["token_position"]),
                token_dictionary_id,
            )
        return rows, dictionary_ids_by_key

    source_rows = fetch_dicts(
        con,
        f"""
        SELECT work_packet_id, token_position, proposed_structural_name,
               review_status, required_manual_decision, packet_label
        FROM {source_sql}
        ORDER BY token_position, work_packet_id
        """,
    )
    for row in source_rows:
        token_dictionary_id = make_target_id("dwh08_dict__", row["work_packet_id"])
        rows.append(
            {
                "token_dictionary_id": token_dictionary_id,
                "line_family": "data_line",
                "token_position": row["token_position"],
                "proposed_structural_name": row["proposed_structural_name"],
                "controlled_field_name": None,
                "structural_role": "block_switch_token",
                "mapping_status": "needs_manual_mapping",
                "review_status": row["review_status"] or "proposed",
                "source_legacy_object": source_name,
                "created_at_utc": created_at,
                "notes": note_join(
                    [
                        f"source_id={row['work_packet_id']}",
                        f"packet_label={row['packet_label']}",
                        row["required_manual_decision"],
                    ]
                ),
            }
        )
        dictionary_ids_by_key.setdefault(
            dictionary_key("data_line", row["token_position"]),
            token_dictionary_id,
        )
    return rows, dictionary_ids_by_key


def load_canonical_lookup(
    con: sqlite3.Connection,
    source_name: str | None,
) -> dict[str, str | None]:
    if source_name is None:
        return {}
    rows = fetch_dicts(
        con,
        f"""
        SELECT raw_term, candidate_canonical_term
        FROM {quote_identifier(source_name)}
        ORDER BY raw_term
        """,
    )
    return {
        str(row["raw_term"]): row["candidate_canonical_term"]
        for row in rows
        if row["raw_term"] is not None
    }


def load_source_label_lookup(con: sqlite3.Connection) -> dict[str, str]:
    if not object_exists(con, "db28_external_source_registry", "table"):
        return {}
    rows = fetch_dicts(
        con,
        """
        SELECT source_id, source_name, institution
        FROM db28_external_source_registry
        ORDER BY source_id
        """,
    )
    return {
        str(row["source_id"]): note_join([row["source_name"], row["institution"]])
        for row in rows
        if row["source_id"] is not None
    }


def load_token_link_lookup(
    con: sqlite3.Connection,
    source_name: str | None,
) -> dict[str, dict[str, Any]]:
    if source_name is None:
        return {}
    rows = fetch_dicts(
        con,
        f"""
        SELECT token_position, linked_evidence_terms, evidence_status,
               mapping_readiness, recommended_next_action
        FROM {quote_identifier(source_name)}
        ORDER BY token_position
        """,
    )
    return {
        str(row["token_position"]): row
        for row in rows
        if row["token_position"] is not None
    }


def load_value_assertion_and_evidence_rows(
    con: sqlite3.Connection,
    assertion_source: str | None,
    canonical_source: str | None,
    token_link_source: str | None,
    dictionary_ids_by_key: dict[tuple[str | None, str | None], str],
    created_at: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if assertion_source is None:
        return [], []

    canonical_by_raw_term = load_canonical_lookup(con, canonical_source)
    source_labels = load_source_label_lookup(con)
    token_links = load_token_link_lookup(con, token_link_source)

    source_rows = fetch_dicts(
        con,
        f"""
        SELECT assertion_id, related_token_position, raw_value_or_term,
               proposed_mapping_scope, source_id, evidence_status,
               assertion_status, evidence_summary, evidence_ref,
               review_status, created_at_utc
        FROM {quote_identifier(assertion_source)}
        ORDER BY related_token_position, raw_value_or_term, assertion_id
        """,
    )
    value_rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []

    for row in source_rows:
        token_value_assertion_id = make_target_id(
            "dwh08_val__", row["assertion_id"]
        )
        token_dictionary_id = lookup_dictionary_id(
            dictionary_ids_by_key,
            "data_line",
            row["related_token_position"],
        )
        token_link = token_links.get(str(row["related_token_position"]))
        value_rows.append(
            {
                "token_value_assertion_id": token_value_assertion_id,
                "token_dictionary_id": token_dictionary_id,
                "raw_value": row["raw_value_or_term"],
                "proposed_canonical_value": canonical_by_raw_term.get(
                    str(row["raw_value_or_term"])
                ),
                "assertion_status": row["assertion_status"] or "candidate_mapping_evidence",
                "evidence_status": row["evidence_status"] or "needs_review",
                "source_legacy_object": assertion_source,
                "created_at_utc": created_at,
                "notes": note_join(
                    [
                        f"source_id={row['assertion_id']}",
                        f"proposed_mapping_scope={row['proposed_mapping_scope']}",
                        f"review_status={row['review_status']}",
                        f"token_link_readiness={token_link['mapping_readiness']}"
                        if token_link
                        else None,
                    ]
                ),
            }
        )
        evidence_rows.append(
            {
                "evidence_id": make_target_id("dwh08_evidence__", row["assertion_id"]),
                "token_value_assertion_id": token_value_assertion_id,
                "evidence_source_label": source_labels.get(
                    str(row["source_id"]), row["source_id"]
                ),
                "evidence_term": row["raw_value_or_term"],
                "evidence_summary": row["evidence_summary"],
                "evidence_status": row["evidence_status"] or "needs_review",
                "review_status": row["review_status"] or "needs_review",
                "source_legacy_object": assertion_source,
                "created_at_utc": created_at,
                "notes": note_join(
                    [
                        f"source_id={row['source_id']}",
                        f"evidence_ref={row['evidence_ref']}",
                        f"linked_terms={token_link['linked_evidence_terms']}"
                        if token_link
                        else None,
                    ]
                ),
            }
        )
    return value_rows, evidence_rows


def load_review_rows(
    con: sqlite3.Connection,
    review_source: str,
    dictionary_ids_by_key: dict[tuple[str | None, str | None], str],
    created_at: str,
) -> list[dict[str, Any]]:
    source_sql = quote_identifier(review_source)
    rows: list[dict[str, Any]] = []

    if review_source == "db27_manual_mapping_priority":
        source_rows = fetch_dicts(
            con,
            f"""
            SELECT priority_id, queue_id, queue_type, token_position, line_family,
                   issue_summary, required_decision, blocking_status,
                   source_priority, priority_score, priority_tier,
                   prioritization_reason
            FROM {source_sql}
            ORDER BY priority_score DESC, priority_tier, token_position, priority_id
            """,
        )
        for row in source_rows:
            token_dictionary_id = lookup_dictionary_id(
                dictionary_ids_by_key,
                row["line_family"],
                row["token_position"],
            )
            rows.append(
                {
                    "review_decision_id": make_target_id(
                        "dwh08_review__", row["priority_id"]
                    ),
                    "token_dictionary_id": token_dictionary_id,
                    "evidence_id": None,
                    "decision_status": "pending_review",
                    "decision_priority": note_join(
                        [
                            row["priority_tier"],
                            f"score={row['priority_score']}",
                            f"source_priority={row['source_priority']}",
                        ]
                    ),
                    "decision_text": row["required_decision"] or row["issue_summary"],
                    "source_legacy_object": review_source,
                    "created_at_utc": created_at,
                    "notes": note_join(
                        [
                            f"queue_id={row['queue_id']}",
                            f"queue_type={row['queue_type']}",
                            f"blocking_status={row['blocking_status']}",
                            row["prioritization_reason"],
                            row["issue_summary"],
                        ]
                    ),
                }
            )
        return rows

    source_rows = fetch_dicts(
        con,
        f"""
        SELECT work_packet_id, token_position, proposed_structural_name,
               required_manual_decision, review_status, packet_label
        FROM {source_sql}
        ORDER BY token_position, work_packet_id
        """,
    )
    for row in source_rows:
        token_dictionary_id = lookup_dictionary_id(
            dictionary_ids_by_key,
            "data_line",
            row["token_position"],
        )
        rows.append(
            {
                "review_decision_id": make_target_id(
                    "dwh08_review__", row["work_packet_id"]
                ),
                "token_dictionary_id": token_dictionary_id,
                "evidence_id": None,
                "decision_status": row["review_status"] or "proposed",
                "decision_priority": "first_mapping_work_packet",
                "decision_text": row["required_manual_decision"],
                "source_legacy_object": review_source,
                "created_at_utc": created_at,
                "notes": note_join(
                    [
                        f"packet_label={row['packet_label']}",
                        f"proposed_structural_name={row['proposed_structural_name']}",
                    ]
                ),
            }
        )
    return rows


def blocking_status_from_db26_gap(row: dict[str, Any]) -> str:
    triage_status = row.get("triage_status")
    severity = row.get("gap_severity")
    if triage_status in {"needs_manual_mapping", "candidate_for_dictionary_seed"}:
        return "blocks_controlled_definition"
    if severity in {"high", "medium"} and triage_status not in {
        "retained_for_audit",
        "immediate_context_only",
    }:
        return "blocks_controlled_definition"
    if triage_status in {"retained_for_audit", "immediate_context_only"}:
        return "does_not_block_controlled_definition"
    return "needs_review"


def load_gap_rows(
    con: sqlite3.Connection,
    db26_gap_source: str | None,
    db28_gap_source: str | None,
    dictionary_ids_by_key: dict[tuple[str | None, str | None], str],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if db26_gap_source is not None:
        source_rows = fetch_dicts(
            con,
            f"""
            SELECT triage_id, source_gap_type, line_family, token_position,
                   source_field_name, gap_severity, triage_status,
                   evidence_summary, recommended_next_action
            FROM {quote_identifier(db26_gap_source)}
            ORDER BY
                CASE gap_severity
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                    WHEN 'info' THEN 4
                    ELSE 5
                END,
                line_family,
                token_position,
                triage_id
            """,
        )
        for row in source_rows:
            token_dictionary_id = lookup_dictionary_id(
                dictionary_ids_by_key,
                row["line_family"],
                row["token_position"],
            )
            rows.append(
                {
                    "evidence_gap_id": make_target_id(
                        "dwh08_gap__", row["triage_id"]
                    ),
                    "token_dictionary_id": token_dictionary_id,
                    "gap_type": row["source_gap_type"] or row["triage_status"] or "mapping_gap",
                    "gap_severity": row["gap_severity"],
                    "raw_value_or_term": row["source_field_name"],
                    "required_external_source": None,
                    "blocking_status": blocking_status_from_db26_gap(row),
                    "source_legacy_object": db26_gap_source,
                    "created_at_utc": created_at,
                    "notes": note_join(
                        [
                            f"triage_status={row['triage_status']}",
                            row["recommended_next_action"],
                            row["evidence_summary"],
                        ]
                    ),
                }
            )

    if db28_gap_source is not None:
        source_rows = fetch_dicts(
            con,
            f"""
            SELECT gap_id, related_token_position, raw_value_or_term,
                   gap_type, gap_severity, required_external_source,
                   blocking_status, recommended_next_action
            FROM {quote_identifier(db28_gap_source)}
            ORDER BY
                CASE gap_severity
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                    ELSE 4
                END,
                related_token_position,
                raw_value_or_term,
                gap_id
            """,
        )
        for row in source_rows:
            token_dictionary_id = lookup_dictionary_id(
                dictionary_ids_by_key,
                "data_line",
                row["related_token_position"],
            )
            rows.append(
                {
                    "evidence_gap_id": make_target_id("dwh08_gap__", row["gap_id"]),
                    "token_dictionary_id": token_dictionary_id,
                    "gap_type": row["gap_type"] or "external_evidence_gap",
                    "gap_severity": row["gap_severity"],
                    "raw_value_or_term": row["raw_value_or_term"],
                    "required_external_source": row["required_external_source"],
                    "blocking_status": row["blocking_status"] or "needs_review",
                    "source_legacy_object": db28_gap_source,
                    "created_at_utc": created_at,
                    "notes": row["recommended_next_action"],
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
    inserted_counts: dict[str, int],
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh08_mapping_evidence_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            created_table_count,
            inserted_dictionary_rows,
            inserted_value_assertion_rows,
            inserted_evidence_rows,
            inserted_review_rows,
            inserted_gap_rows,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(live_db),
            str(workcopy_db),
            SCRIPT_NAME,
            "workcopy_mapping_evidence_skeleton",
            1 if live_modified else 0,
            1,
            len(TARGET_TABLES),
            inserted_counts["dictionary"],
            inserted_counts["value_assertion"],
            inserted_counts["evidence"],
            inserted_counts["review"],
            inserted_counts["gap"],
            integrity,
            fk_count,
            "DWH08 created and populated the minimal target map_* layer in the workcopy only.",
        ),
    )


def validate_workcopy(
    con: sqlite3.Connection,
    live_before: dict[str, Any],
    live_after: dict[str, Any],
) -> dict[str, Any]:
    integrity = integrity_check(con)
    fk_violations = foreign_key_violations(con)
    table_counts = {table: table_count(con, table) for table in TARGET_TABLES}
    view_counts = {view: table_count(con, view) for view in TARGET_VIEWS}
    dwh05_counts = {table: table_count(con, table) for table in DWH05_EXPECTED_COUNTS}
    dwh06_counts = {table: table_count(con, table) for table in DWH06_DIMENSION_TABLES}
    dwh05_preserved = {
        table: {
            "expected": expected,
            "actual": dwh05_counts[table],
            "status": "passed" if dwh05_counts[table] == expected else "failed",
        }
        for table, expected in DWH05_EXPECTED_COUNTS.items()
    }
    dwh06_preserved = {
        table: {
            "expected_minimum": 1,
            "actual": dwh06_counts[table],
            "status": "passed" if dwh06_counts[table] >= 1 else "failed",
        }
        for table in DWH06_DIMENSION_TABLES
    }
    return {
        "workcopy_integrity_check": integrity,
        "workcopy_foreign_key_violations": fk_violations,
        "foreign_key_violation_count": len(fk_violations),
        "target_table_counts": table_counts,
        "target_view_counts": view_counts,
        "dwh05_raw_core_row_counts": dwh05_preserved,
        "dwh06_dimension_row_counts": dwh06_preserved,
        "live_db_sha256_before": live_before["sha256"],
        "live_db_sha256_after": live_after["sha256"],
        "live_db_stat_before": live_before["stat"],
        "live_db_stat_after": live_after["stat"],
        "live_db_checksum_unchanged": live_before["sha256"] == live_after["sha256"],
        "live_db_stat_unchanged": live_before["stat"] == live_after["stat"],
    }


def target_table_count_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    roles = {
        "map_token_dictionary": "target_dictionary",
        "map_token_value_assertion": "target_value_assertion",
        "map_assertion_evidence": "target_evidence",
        "map_review_decision": "target_review",
        "map_evidence_gap": "target_gap",
        "dwh08_mapping_evidence_run_log": "run_log",
    }
    return [
        {
            "table_name": table,
            "row_count": table_count(con, table),
            "table_role": roles[table],
            "notes": "DWH08 target/workcopy table.",
        }
        for table in TARGET_TABLES
    ]


def preview_rows(
    con: sqlite3.Connection,
    source_name: str,
    limit: int,
) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        f"SELECT * FROM {quote_identifier(source_name)} LIMIT ?",
        (limit,),
    )


def source_object_counts(
    con: sqlite3.Connection,
    selected_sources: dict[str, str | None],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for source_name in selected_sources.values():
        if source_name is not None and source_name not in counts:
            counts[source_name] = source_count(con, source_name)
    return counts


def build_summary(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    preflight: dict[str, Any],
    validation: dict[str, Any],
    inserted_counts: dict[str, int],
) -> dict[str, Any]:
    selected_sources = preflight["source_objects_selected"]
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH controlled workcopy implementation",
        "data_substrate_used": str(workcopy_db),
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "raw_tim_par_files_read": False,
        "report_exports_used_as_input": False,
        "new_isolated_analysis_db_created": False,
        "bridge_or_result_tables_created": False,
        "target_tables_created": TARGET_TABLES,
        "target_views_created": TARGET_VIEWS,
        "source_objects_selected": selected_sources,
        "source_object_counts": source_object_counts(con, selected_sources),
        "inserted_row_counts": inserted_counts,
        "target_table_counts": validation["target_table_counts"],
        "target_view_counts": validation["target_view_counts"],
        "preflight": {
            "live_integrity_check": preflight["live_integrity"],
            "live_foreign_key_violation_count": preflight["live_fk_count"],
            "workcopy_integrity_check": preflight["work_integrity"],
            "workcopy_foreign_key_violation_count": preflight["work_fk_count"],
        },
        "validation": validation,
        "token_dictionary_preview": preview_rows(
            con,
            "qsb_v_dwh08_token_dictionary_status",
            10,
        ),
        "evidence_gap_preview": preview_rows(
            con,
            "qsb_v_dwh08_open_evidence_gaps",
            10,
        ),
        "recommended_dwh09_options": next_dwh_steps_rows(),
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_query_csv(
    con: sqlite3.Connection,
    path: Path,
    sql: str,
    params: tuple[Any, ...] = (),
) -> None:
    cur = con.execute(sql, params)
    columns = [description[0] for description in cur.description]
    rows = cur.fetchall()
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[column] for column in columns])


def next_dwh_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "option_id": "DWH09_A",
            "option_name": "ERD export / visual inspection for Mapping/Evidence layer",
            "prerequisite": "DWH08 target map_* layer exists and views are queryable",
            "recommended_action": "Create a focused ERD/readout for map_* tables and FK direction.",
            "risk_level": "low",
            "notes": "Recommended first because the new target layer should be visually inspected before refinement.",
        },
        {
            "option_id": "DWH09_B",
            "option_name": "External evidence verification for receiver/backend/telescope terms",
            "prerequisite": "DWH08 gap rows identify required external source classes",
            "recommended_action": "Verify receiver/backend/telescope terms against approved external sources.",
            "risk_level": "medium",
            "notes": "Do not promote terms to controlled definitions without reviewed evidence.",
        },
        {
            "option_id": "DWH09_C",
            "option_name": "Controlled mapping refinement for first 5 block-switch tokens only",
            "prerequisite": "DWH08 first-token review decisions remain bounded to DB27 work packet scope",
            "recommended_action": "Refine only tim_token_007, tim_token_011, tim_token_013, tim_token_017, and tim_token_023.",
            "risk_level": "medium",
            "notes": "Keeps the next mapping step narrow and auditable.",
        },
        {
            "option_id": "DWH09_D",
            "option_name": "Bridge relation skeleton only after mapping/evidence layer passes visual inspection",
            "prerequisite": "Mapping/Evidence ERD and review screens accepted",
            "recommended_action": "Defer bridge/result skeletons until target mapping/evidence structure is accepted.",
            "risk_level": "high",
            "notes": "DWH08 intentionally does not create bridge or result tables.",
        },
    ]


def format_preview_lines(rows: list[dict[str, Any]], fields: list[str]) -> str:
    lines: list[str] = []
    for row in rows:
        parts = [f"{field}={row.get(field)}" for field in fields]
        lines.append("- " + "; ".join(parts))
    return "\n".join(lines) if lines else "- No rows."


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    source_lines = [
        f"- {label}: `{source}`"
        for label, source in summary["source_objects_selected"].items()
        if source is not None
    ]
    count_lines = [
        f"- {table}: {count}"
        for table, count in summary["target_table_counts"].items()
    ]
    dictionary_preview = format_preview_lines(
        summary["token_dictionary_preview"],
        [
            "line_family",
            "token_position",
            "mapping_status",
            "review_status",
            "value_assertion_count",
            "evidence_gap_count",
        ],
    )
    gap_preview = format_preview_lines(
        summary["evidence_gap_preview"],
        [
            "gap_type",
            "gap_severity",
            "blocking_status",
            "token_position",
            "raw_value_or_term",
        ],
    )
    dwh09_lines = [
        f"- {row['option_id']}: {row['option_name']}"
        for row in summary["recommended_dwh09_options"]
    ]
    live_status = (
        "unchanged"
        if summary["validation"]["live_db_checksum_unchanged"]
        and summary["validation"]["live_db_stat_unchanged"]
        else "changed"
    )
    dwh05_failed = [
        table for table, item in summary["validation"]["dwh05_raw_core_row_counts"].items()
        if item["status"] != "passed"
    ]
    dwh06_failed = [
        table for table, item in summary["validation"]["dwh06_dimension_row_counts"].items()
        if item["status"] != "passed"
    ]
    content = f"""# QSB-DWH08 Mapping/Evidence Skeleton Readout

## 1. Executive summary

Befund: DWH08 created the minimal target Mapping/Evidence layer in the workcopy database and populated it from existing DB26/DB27/DB28 database objects.

- Run ID: `{summary['run_id']}`
- Workcopy DB: `{summary['workcopy_db_path']}`
- Target table count: {len(summary['target_tables_created'])}
- Inserted dictionary rows: {summary['inserted_row_counts']['dictionary']}
- Inserted value assertion rows: {summary['inserted_row_counts']['value_assertion']}
- Inserted evidence rows: {summary['inserted_row_counts']['evidence']}
- Inserted review rows: {summary['inserted_row_counts']['review']}
- Inserted gap rows: {summary['inserted_row_counts']['gap']}

## 2. Workcopy-only principle

All schema and row insertions were made only in `{summary['workcopy_db_path']}`. The live database was opened read-only for validation and protection checks.

## 3. Live DB protection

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['preflight']['live_integrity_check']}
- Live foreign-key violations before DWH08: {summary['preflight']['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH08: {live_status}

## 4. Target map_* tables created

{chr(10).join(f'- `{table}`' for table in summary['target_tables_created'])}

## 5. Source legacy mapping/evidence objects used

{chr(10).join(source_lines)}

## 6. Inserted row counts

{chr(10).join(count_lines)}

## 7. Token dictionary preview

{dictionary_preview}

## 8. Evidence gap preview

{gap_preview}

## 9. Validation results

- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}
- Workcopy foreign-key violation count: {summary['validation']['foreign_key_violation_count']}
- DWH05 raw/core preservation: {'passed' if not dwh05_failed else 'failed: ' + ', '.join(dwh05_failed)}
- DWH06 dimension preservation: {'passed' if not dwh06_failed else 'failed: ' + ', '.join(dwh06_failed)}
- DWH08 views queryable: {len(summary['target_view_counts'])} of {len(TARGET_VIEWS)}

## 10. What DWH08 does not do

DWH08 does not read raw TIM/PAR files, does not use CSV/JSON/MD report exports as input, does not create bridge/result tables, does not populate value assertions from all raw_field_value rows, does not compute timing/model/statistical quantities, and does not assign final controlled meanings to unresolved TIM columns.

## 11. Recommended DWH09 options

{chr(10).join(dwh09_lines)}

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
        paths[TABLE_COUNTS_CSV],
        ["table_name", "row_count", "table_role", "notes"],
        target_table_count_rows(con),
    )
    write_query_csv(
        con,
        paths[TOKEN_DICTIONARY_PREVIEW_CSV],
        """
        SELECT token_dictionary_id, line_family, token_position,
               proposed_structural_name, controlled_field_name, structural_role,
               mapping_status, review_status, source_legacy_object,
               value_assertion_count, evidence_count, review_decision_count,
               evidence_gap_count
        FROM qsb_v_dwh08_token_dictionary_status
        LIMIT 20
        """,
    )
    write_query_csv(
        con,
        paths[EVIDENCE_GAP_PREVIEW_CSV],
        """
        SELECT evidence_gap_id, gap_type, gap_severity, blocking_status,
               raw_value_or_term, required_external_source, token_dictionary_id,
               line_family, token_position, source_legacy_object
        FROM qsb_v_dwh08_open_evidence_gaps
        LIMIT 20
        """,
    )
    write_csv(
        paths[NEXT_DWH_STEPS_CSV],
        [
            "option_id",
            "option_name",
            "prerequisite",
            "recommended_action",
            "risk_level",
            "notes",
        ],
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
    run_id = "DWH08_MAPPING_EVIDENCE_SKELETON_" + timestamp_for_id()
    selected_sources = preflight["source_objects_selected"]

    with connect_writable(workcopy_db) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            create_tables_and_indexes(con, allow_existing)
            dictionary_rows, dictionary_ids_by_key = load_dictionary_rows(
                con,
                selected_sources["dictionary_source"],
                created_at,
            )
            insert_rows(con, "map_token_dictionary", dictionary_rows)

            value_rows, evidence_rows = load_value_assertion_and_evidence_rows(
                con,
                selected_sources["assertion_source"],
                selected_sources["canonical_source"],
                selected_sources["token_link_source"],
                dictionary_ids_by_key,
                created_at,
            )
            insert_rows(con, "map_token_value_assertion", value_rows)
            insert_rows(con, "map_assertion_evidence", evidence_rows)

            review_rows = load_review_rows(
                con,
                selected_sources["review_source"],
                dictionary_ids_by_key,
                created_at,
            )
            insert_rows(con, "map_review_decision", review_rows)

            gap_rows = load_gap_rows(
                con,
                selected_sources["db26_gap_source"],
                selected_sources["db28_gap_source"],
                dictionary_ids_by_key,
                created_at,
            )
            insert_rows(con, "map_evidence_gap", gap_rows)
            create_views(con, allow_existing)

            live_after = db_state(live_db)
            validation_before_log = validate_workcopy(con, live_before, live_after)
            inserted_counts = {
                "dictionary": len(dictionary_rows),
                "value_assertion": len(value_rows),
                "evidence": len(evidence_rows),
                "review": len(review_rows),
                "gap": len(gap_rows),
            }
            insert_run_log(
                con,
                run_id,
                created_at,
                live_db,
                workcopy_db,
                not validation_before_log["live_db_checksum_unchanged"]
                or not validation_before_log["live_db_stat_unchanged"],
                inserted_counts,
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
                inserted_counts,
            )
            write_outputs(con, output_root, summary)
            con.commit()
        except Exception:
            con.rollback()
            raise
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "QSB-DWH08 workcopy-only Mapping/Evidence target skeleton over the "
            "DWH03/DWH05/DWH06 workcopy DB."
        )
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
        help="Existing output directory for DWH08 report files.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the six DWH08 report files if they already exist.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow empty existing DWH08 target objects; never appends to nonempty target tables.",
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
