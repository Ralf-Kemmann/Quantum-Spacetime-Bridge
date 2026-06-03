#!/usr/bin/env python3
"""QSB-DWH06: dimension skeleton in the DWH03/DWH05 workcopy.

This script expands the DWH workcopy target schema by adding governed
dimension skeleton tables and placeholder seed rows. It modifies only the
workcopy DB. The live DB is opened read-only for protection checks.

It does not read raw TIM/PAR files, does not use generated reports as input
substrate, does not migrate new raw data, does not resolve final TIM/PAR
semantics, and does not compute physical, timing, residual, delay, model, or
statistical quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh06_dimension_skeleton_workcopy.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh06_dimension_skeleton_readout.md"
SUMMARY_JSON = "dwh06_dimension_skeleton_summary.json"
TABLE_CATALOG_CSV = "dwh06_dimension_table_catalog.csv"
FIELD_CATALOG_CSV = "dwh06_dimension_field_catalog.csv"
SEED_ROWS_CSV = "dwh06_dimension_seed_rows.csv"
LINK_STATUS_CSV = "dwh06_core_observation_dimension_link_status.csv"
FK_REPORT_CSV = "dwh06_dimension_fk_validation_report.csv"
NEXT_STEPS_CSV = "dwh06_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    TABLE_CATALOG_CSV,
    FIELD_CATALOG_CSV,
    SEED_ROWS_CSV,
    LINK_STATUS_CSV,
    FK_REPORT_CSV,
    NEXT_STEPS_CSV,
]

REQUIRED_WORKCOPY_TABLES = [
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
    "dwh05_migration_dry_run_log",
]

REQUIRED_DWH05_VIEWS = [
    "qsb_v_dwh05_raw_core_migration_dashboard",
    "qsb_v_dwh05_parity_status",
]

DIMENSION_TABLES = [
    "dim_science_object",
    "dim_telescope",
    "dim_receiver",
    "dim_backend",
    "dim_time_context",
    "dim_processing_context",
    "dim_quality_status",
]

ALL_CREATED_TABLES = [*DIMENSION_TABLES, "dwh06_dimension_run_log"]

DWH06_VIEWS = [
    "qsb_v_dwh06_dimension_dashboard",
    "qsb_v_dwh06_observation_dimension_link_status",
    "qsb_v_dwh06_dimension_seed_rows",
    "qsb_v_dwh06_next_dimension_actions",
]

INDEX_STATEMENTS = [
    "CREATE INDEX idx_dwh06_dim_receiver_telescope_id ON dim_receiver(telescope_id)",
    "CREATE INDEX idx_dwh06_dim_backend_telescope_id ON dim_backend(telescope_id)",
    "CREATE INDEX idx_dwh06_dim_science_object_object_name ON dim_science_object(object_name)",
    "CREATE INDEX idx_dwh06_dim_quality_status_quality_class ON dim_quality_status(quality_class)",
    "CREATE INDEX idx_dwh06_core_observation_object_id ON core_observation(object_id)",
    "CREATE INDEX idx_dwh06_core_observation_telescope_id ON core_observation(telescope_id)",
    "CREATE INDEX idx_dwh06_core_observation_receiver_id ON core_observation(receiver_id)",
    "CREATE INDEX idx_dwh06_core_observation_backend_id ON core_observation(backend_id)",
    "CREATE INDEX idx_dwh06_core_observation_time_context_id ON core_observation(time_context_id)",
    "CREATE INDEX idx_dwh06_core_observation_processing_context_id ON core_observation(processing_context_id)",
    "CREATE INDEX idx_dwh06_core_observation_quality_status_id ON core_observation(quality_status_id)",
]

CLAIM_BOUNDARY = (
    "DWH06 is a workcopy-only dimension skeleton step. It creates governed "
    "dimension tables and placeholder seed rows, then validates that current "
    "core_observation context values can link to those rows. It does not modify "
    "the live DB, does not verify external evidence, does not resolve final "
    "TIM/PAR semantics, and does not make scientific interpretation claims."
)


@dataclass(frozen=True)
class FieldSpec:
    table_name: str
    field_name: str
    field_type: str
    nullable: str
    field_role: str
    field_description: str
    fk_target: str
    source_or_future_mapping_rule: str
    notes: str


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
    return int(
        con.execute(
            f"SELECT COUNT(*) AS n FROM {quote_identifier(table_name)}"
        ).fetchone()["n"]
    )


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
            "Refusing to overwrite existing DWH06 output file(s): "
            + "; ".join(existing)
        )


def ensure_preconditions(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
    allow_existing: bool,
) -> dict[str, Any]:
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
        missing_tables = [
            table for table in REQUIRED_WORKCOPY_TABLES
            if not object_exists(con, table, "table")
        ]
        missing_views = [
            view for view in REQUIRED_DWH05_VIEWS
            if not object_exists(con, view, "view")
        ]
        for view in REQUIRED_DWH05_VIEWS:
            if object_exists(con, view, "view"):
                table_count(con, view)
        existing_dwh06_tables = [
            table for table in ALL_CREATED_TABLES
            if object_exists(con, table, "table")
        ]
        existing_dwh06_views = [
            view for view in DWH06_VIEWS
            if object_exists(con, view, "view")
        ]
        observation_count = table_count(con, "core_observation") if object_exists(con, "core_observation", "table") else 0

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if missing_tables:
        raise RuntimeError("Missing required workcopy table(s): " + ", ".join(missing_tables))
    if missing_views:
        raise RuntimeError("Missing required DWH05 view(s): " + ", ".join(missing_views))
    existing = sorted(set(existing_dwh06_tables + existing_dwh06_views))
    if existing and not allow_existing:
        raise RuntimeError(
            "DWH06 objects already exist; use --allow-existing only for "
            "controlled re-inspection: " + ", ".join(existing)
        )
    if existing and allow_existing:
        raise RuntimeError(
            "--allow-existing re-inspection is intentionally not destructive; "
            "this first-run script does not append to existing DWH06 objects."
        )
    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "core_observation_count": observation_count,
    }


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE dim_science_object (
            object_id TEXT PRIMARY KEY,
            object_name TEXT NOT NULL,
            object_type TEXT NOT NULL,
            catalog_id TEXT,
            sky_position_ref TEXT,
            object_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE dim_telescope (
            telescope_id TEXT PRIMARY KEY,
            telescope_name TEXT NOT NULL,
            institution TEXT,
            site_name TEXT,
            telescope_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE dim_receiver (
            receiver_id TEXT PRIMARY KEY,
            telescope_id TEXT REFERENCES dim_telescope(telescope_id),
            raw_receiver_name TEXT,
            canonical_receiver_name TEXT,
            frequency_low_mhz REAL,
            frequency_high_mhz REAL,
            receiver_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE dim_backend (
            backend_id TEXT PRIMARY KEY,
            telescope_id TEXT REFERENCES dim_telescope(telescope_id),
            raw_backend_name TEXT,
            canonical_backend_name TEXT,
            backend_type TEXT,
            backend_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE dim_time_context (
            time_context_id TEXT PRIMARY KEY,
            time_system TEXT,
            mjd_start TEXT,
            mjd_end TEXT,
            clock_context TEXT,
            ephemeris_context TEXT,
            barycentric_context TEXT,
            time_context_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE dim_processing_context (
            processing_context_id TEXT PRIMARY KEY,
            pipeline_name TEXT,
            pipeline_version TEXT,
            processing_label TEXT,
            product_type TEXT,
            processing_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE dim_quality_status (
            quality_status_id TEXT PRIMARY KEY,
            quality_class TEXT NOT NULL,
            quality_flag TEXT,
            quarantine_status TEXT,
            anomaly_status TEXT,
            quality_status TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE dwh06_dimension_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            created_dimension_table_count INTEGER,
            inserted_dimension_row_count INTEGER,
            updated_core_observation_count INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT,
            CHECK (live_db_modified IN (0, 1)),
            CHECK (workcopy_db_modified IN (0, 1))
        );
        """
    )
    for statement in INDEX_STATEMENTS:
        con.execute(statement)


def insert_seed_rows(con: sqlite3.Connection, created_at: str) -> None:
    con.execute(
        """
        INSERT INTO dim_science_object (
            object_id,
            object_name,
            object_type,
            catalog_id,
            sky_position_ref,
            object_status,
            evidence_status,
            created_at_utc,
            notes
        )
        VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?)
        """,
        (
            "J0740+6620",
            "J0740+6620",
            "pulsar_candidate_context_from_dataset_label",
            "unresolved_catalog_reference",
            "dry_run_imported_from_dataset_context",
            "pending_external_catalog_verification",
            created_at,
            "derived from existing core_dataset/core_observation object_id, not final source catalog mapping",
        ),
    )
    con.execute(
        """
        INSERT INTO dim_telescope (
            telescope_id,
            telescope_name,
            institution,
            site_name,
            telescope_status,
            evidence_status,
            created_at_utc,
            notes
        )
        VALUES (?, ?, NULL, NULL, ?, ?, ?, ?)
        """,
        (
            "unresolved_placeholder",
            "unresolved_placeholder",
            "pending_mapping",
            "missing_external_evidence",
            created_at,
            "placeholder row for DWH05 core_observation telescope_id; no final telescope mapping",
        ),
    )
    con.execute(
        """
        INSERT INTO dim_receiver (
            receiver_id,
            telescope_id,
            raw_receiver_name,
            canonical_receiver_name,
            frequency_low_mhz,
            frequency_high_mhz,
            receiver_status,
            evidence_status,
            created_at_utc,
            notes
        )
        VALUES (?, ?, ?, ?, NULL, NULL, ?, ?, ?, ?)
        """,
        (
            "unresolved_placeholder",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "pending_mapping",
            "missing_external_evidence",
            created_at,
            "placeholder row for DWH05 core_observation receiver_id; no final receiver mapping",
        ),
    )
    con.execute(
        """
        INSERT INTO dim_backend (
            backend_id,
            telescope_id,
            raw_backend_name,
            canonical_backend_name,
            backend_type,
            backend_status,
            evidence_status,
            created_at_utc,
            notes
        )
        VALUES (?, ?, ?, ?, NULL, ?, ?, ?, ?)
        """,
        (
            "unresolved_placeholder",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "pending_mapping",
            "missing_external_evidence",
            created_at,
            "placeholder row for DWH05 core_observation backend_id; no final backend mapping",
        ),
    )
    con.execute(
        """
        INSERT INTO dim_time_context (
            time_context_id,
            time_system,
            mjd_start,
            mjd_end,
            clock_context,
            ephemeris_context,
            barycentric_context,
            time_context_status,
            evidence_status,
            created_at_utc,
            notes
        )
        VALUES (?, NULL, NULL, NULL, NULL, NULL, NULL, ?, ?, ?, ?)
        """,
        (
            "unresolved_placeholder",
            "pending_mapping",
            "missing_external_evidence",
            created_at,
            "placeholder row for DWH05 core_observation time_context_id; no time conversion or resolution",
        ),
    )
    con.execute(
        """
        INSERT INTO dim_processing_context (
            processing_context_id,
            pipeline_name,
            pipeline_version,
            processing_label,
            product_type,
            processing_status,
            evidence_status,
            created_at_utc,
            notes
        )
        VALUES (?, NULL, NULL, NULL, NULL, ?, ?, ?, ?)
        """,
        (
            "unresolved_placeholder",
            "pending_mapping",
            "missing_external_evidence",
            created_at,
            "placeholder row for DWH05 core_observation processing_context_id; no final processing context mapping",
        ),
    )
    con.execute(
        """
        INSERT INTO dim_quality_status (
            quality_status_id,
            quality_class,
            quality_flag,
            quarantine_status,
            anomaly_status,
            quality_status,
            evidence_status,
            created_at_utc,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "dry_run_unreviewed",
            "dry_run_unreviewed",
            "dry_run_unreviewed",
            "not_reviewed",
            "not_reviewed",
            "pending_review",
            "internal_dry_run_status",
            created_at,
            "dry-run quality status row for migrated core_observation; not final review",
        ),
    )


def create_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE VIEW qsb_v_dwh06_observation_dimension_link_status AS
        SELECT
            co.observation_id,
            co.object_id,
            CASE WHEN dso.object_id IS NOT NULL THEN 'linked' ELSE 'missing' END AS object_link_status,
            co.telescope_id,
            CASE WHEN dt.telescope_id IS NOT NULL THEN 'linked' ELSE 'missing' END AS telescope_link_status,
            co.receiver_id,
            CASE WHEN dr.receiver_id IS NOT NULL THEN 'linked' ELSE 'missing' END AS receiver_link_status,
            co.backend_id,
            CASE WHEN db.backend_id IS NOT NULL THEN 'linked' ELSE 'missing' END AS backend_link_status,
            co.time_context_id,
            CASE WHEN dtc.time_context_id IS NOT NULL THEN 'linked' ELSE 'missing' END AS time_context_link_status,
            co.processing_context_id,
            CASE WHEN dpc.processing_context_id IS NOT NULL THEN 'linked' ELSE 'missing' END AS processing_link_status,
            co.quality_status_id,
            CASE WHEN dqs.quality_status_id IS NOT NULL THEN 'linked' ELSE 'missing' END AS quality_link_status,
            CASE
                WHEN dso.object_id IS NOT NULL
                 AND dt.telescope_id IS NOT NULL
                 AND dr.receiver_id IS NOT NULL
                 AND db.backend_id IS NOT NULL
                 AND dtc.time_context_id IS NOT NULL
                 AND dpc.processing_context_id IS NOT NULL
                 AND dqs.quality_status_id IS NOT NULL
                THEN 'fully_linked'
                ELSE 'missing_dimension_link'
            END AS overall_dimension_link_status
        FROM core_observation AS co
        LEFT JOIN dim_science_object AS dso
          ON dso.object_id = co.object_id
        LEFT JOIN dim_telescope AS dt
          ON dt.telescope_id = co.telescope_id
        LEFT JOIN dim_receiver AS dr
          ON dr.receiver_id = co.receiver_id
        LEFT JOIN dim_backend AS db
          ON db.backend_id = co.backend_id
        LEFT JOIN dim_time_context AS dtc
          ON dtc.time_context_id = co.time_context_id
        LEFT JOIN dim_processing_context AS dpc
          ON dpc.processing_context_id = co.processing_context_id
        LEFT JOIN dim_quality_status AS dqs
          ON dqs.quality_status_id = co.quality_status_id;

        CREATE VIEW qsb_v_dwh06_dimension_seed_rows AS
        SELECT
            'dim_science_object' AS dimension_name,
            object_id AS dimension_id,
            object_name AS display_label,
            object_status AS status,
            evidence_status,
            notes
        FROM dim_science_object
        UNION ALL
        SELECT
            'dim_telescope',
            telescope_id,
            telescope_name,
            telescope_status,
            evidence_status,
            notes
        FROM dim_telescope
        UNION ALL
        SELECT
            'dim_receiver',
            receiver_id,
            COALESCE(canonical_receiver_name, raw_receiver_name, receiver_id),
            receiver_status,
            evidence_status,
            notes
        FROM dim_receiver
        UNION ALL
        SELECT
            'dim_backend',
            backend_id,
            COALESCE(canonical_backend_name, raw_backend_name, backend_id),
            backend_status,
            evidence_status,
            notes
        FROM dim_backend
        UNION ALL
        SELECT
            'dim_time_context',
            time_context_id,
            time_context_id,
            time_context_status,
            evidence_status,
            notes
        FROM dim_time_context
        UNION ALL
        SELECT
            'dim_processing_context',
            processing_context_id,
            COALESCE(processing_label, processing_context_id),
            processing_status,
            evidence_status,
            notes
        FROM dim_processing_context
        UNION ALL
        SELECT
            'dim_quality_status',
            quality_status_id,
            quality_class,
            quality_status,
            evidence_status,
            notes
        FROM dim_quality_status;

        CREATE VIEW qsb_v_dwh06_next_dimension_actions AS
        SELECT
            'DWH07_ACTION_01' AS action_id,
            'external evidence verification for telescope/receiver/backend' AS next_action,
            'pending' AS action_status,
            'Needed before replacing unresolved_placeholder rows with reviewed instrument dimensions.' AS notes
        UNION ALL
        SELECT
            'DWH07_ACTION_02',
            'create mapping/evidence target skeleton',
            'pending',
            'Needed before token-level semantic mapping or evidence review migration.'
        UNION ALL
        SELECT
            'DWH07_ACTION_03',
            'decide when to rebuild core_observation with enforced FK constraints',
            'pending',
            'SQLite requires controlled table rebuild to add FKs to existing placeholder columns.'
        UNION ALL
        SELECT
            'DWH07_ACTION_04',
            'create ERD slice for core + dimensions',
            'pending',
            'Visual inspection should show core_observation context links to dim_* tables.'
        UNION ALL
        SELECT
            'DWH07_ACTION_05',
            'plan bridge/result skeleton only after mapping/evidence layer is stable',
            'pending',
            'Bridge/result tables remain out of scope until mapping/evidence governance exists.';

        CREATE VIEW qsb_v_dwh06_dimension_dashboard AS
        SELECT
            run.run_id,
            run.created_dimension_table_count AS dimension_table_count,
            run.inserted_dimension_row_count AS dimension_seed_row_count,
            (SELECT COUNT(*) FROM core_observation) AS core_observation_count,
            (
                SELECT COUNT(*)
                FROM qsb_v_dwh06_observation_dimension_link_status
                WHERE overall_dimension_link_status = 'fully_linked'
            ) AS fully_linked_observation_count,
            (
                SELECT
                    SUM(
                        CASE WHEN object_link_status = 'missing' THEN 1 ELSE 0 END
                      + CASE WHEN telescope_link_status = 'missing' THEN 1 ELSE 0 END
                      + CASE WHEN receiver_link_status = 'missing' THEN 1 ELSE 0 END
                      + CASE WHEN backend_link_status = 'missing' THEN 1 ELSE 0 END
                      + CASE WHEN time_context_link_status = 'missing' THEN 1 ELSE 0 END
                      + CASE WHEN processing_link_status = 'missing' THEN 1 ELSE 0 END
                      + CASE WHEN quality_link_status = 'missing' THEN 1 ELSE 0 END
                    )
                FROM qsb_v_dwh06_observation_dimension_link_status
            ) AS missing_dimension_link_count,
            run.integrity_check_result,
            run.foreign_key_violation_count
        FROM dwh06_dimension_run_log AS run
        ORDER BY run.run_timestamp_utc DESC, run.run_id DESC;
        """
    )


def insert_run_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    live_modified: bool,
    integrity: str,
    fk_count: int,
) -> None:
    con.execute(
        """
        INSERT INTO dwh06_dimension_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            created_dimension_table_count,
            inserted_dimension_row_count,
            updated_core_observation_count,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(live_db),
            str(workcopy_db),
            SCRIPT_NAME,
            "workcopy_dimension_skeleton",
            1 if live_modified else 0,
            1,
            len(DIMENSION_TABLES),
            sum(table_count(con, table) for table in DIMENSION_TABLES),
            0,
            integrity,
            fk_count,
            "DWH06 created dimension skeleton tables and placeholder seed rows in the workcopy only; core_observation was not rebuilt.",
        ),
    )


def validate_workcopy(con: sqlite3.Connection) -> dict[str, Any]:
    integrity = integrity_check(con)
    fk = foreign_key_violations(con)
    table_counts = {table: table_count(con, table) for table in ALL_CREATED_TABLES}
    view_counts = {
        view: table_count(con, view)
        for view in DWH06_VIEWS
        if object_exists(con, view, "view")
    }
    link_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_dwh06_observation_dimension_link_status
        ORDER BY observation_id
        """,
    )
    seed_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_dwh06_dimension_seed_rows
        ORDER BY dimension_name, dimension_id
        """,
    )
    dashboard_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_dwh06_dimension_dashboard
        LIMIT 1
        """,
    )
    return {
        "integrity": integrity,
        "fk_violations": fk,
        "table_counts": table_counts,
        "view_counts": view_counts,
        "link_rows": link_rows,
        "seed_rows": seed_rows,
        "dashboard": dashboard_rows[0] if dashboard_rows else {},
    }


def table_catalog_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    specs = [
        ("dim_science_object", "Dimensions / Context Layer", "Science object dimension skeleton.", "One row per governed object placeholder or reviewed object.", "object_id", "created_seeded"),
        ("dim_telescope", "Dimensions / Context Layer", "Telescope dimension skeleton.", "One row per telescope placeholder or reviewed telescope.", "telescope_id", "created_seeded"),
        ("dim_receiver", "Dimensions / Context Layer", "Receiver dimension skeleton linked to telescope where known.", "One row per receiver placeholder or reviewed receiver.", "receiver_id", "created_seeded"),
        ("dim_backend", "Dimensions / Context Layer", "Backend dimension skeleton linked to telescope where known.", "One row per backend placeholder or reviewed backend.", "backend_id", "created_seeded"),
        ("dim_time_context", "Dimensions / Context Layer", "Time context dimension skeleton.", "One row per time context placeholder or reviewed time context.", "time_context_id", "created_seeded"),
        ("dim_processing_context", "Dimensions / Context Layer", "Processing context dimension skeleton.", "One row per processing placeholder or reviewed processing context.", "processing_context_id", "created_seeded"),
        ("dim_quality_status", "Dimensions / Context Layer", "Quality status dimension skeleton.", "One row per governed quality/review status.", "quality_status_id", "created_seeded"),
        ("dwh06_dimension_run_log", "DWH06 Workcopy Metadata", "DWH06 run metadata.", "One row per DWH06 dimension skeleton run.", "run_id", "created_seeded"),
    ]
    return [
        {
            "table_name": table,
            "layer": layer,
            "purpose": purpose,
            "grain": grain,
            "primary_key": pk,
            "row_count_actual": table_count(con, table),
            "implementation_status": status,
            "notes": "Workcopy-only; live DB unchanged.",
        }
        for table, layer, purpose, grain, pk, status in specs
    ]


def field_specs() -> list[FieldSpec]:
    rows: list[FieldSpec] = []

    def add(table: str, fields: list[tuple[str, str, str, str, str, str, str, str]]) -> None:
        for item in fields:
            rows.append(FieldSpec(table, *item))

    common = "Created by DWH06 skeleton; future mapping/evidence layer may refine this row."
    add("dim_science_object", [
        ("object_id", "TEXT", "no", "primary_key", "Science object identifier.", "", "Existing core_observation.object_id.", common),
        ("object_name", "TEXT", "no", "descriptor", "Display object name.", "", "Existing dataset/observation label.", common),
        ("object_type", "TEXT", "no", "classification", "Defensive object type/context label.", "", "DWH06 seed rule.", "Not final catalog classification."),
        ("catalog_id", "TEXT", "yes", "lineage_attribute", "External catalog identifier placeholder.", "", "Future external verification.", "Unresolved in DWH06."),
        ("sky_position_ref", "TEXT", "yes", "payload_reference", "Reference for sky-position source if later reviewed.", "", "Future external verification.", "NULL in DWH06 seed."),
        ("object_status", "TEXT", "no", "status", "Object lifecycle status.", "", "DWH06 seed rule.", common),
        ("evidence_status", "TEXT", "no", "status", "Evidence status.", "", "DWH06 seed rule.", common),
        ("created_at_utc", "TEXT", "no", "audit_timestamp", "Creation timestamp.", "", "DWH06 run timestamp.", common),
        ("notes", "TEXT", "yes", "note", "Defensive note.", "", "DWH06 seed rule.", common),
    ])
    add("dim_telescope", [
        ("telescope_id", "TEXT", "no", "primary_key", "Telescope identifier.", "", "Existing core_observation.telescope_id.", common),
        ("telescope_name", "TEXT", "no", "descriptor", "Telescope display name.", "", "DWH06 placeholder seed.", "Not final telescope mapping."),
        ("institution", "TEXT", "yes", "descriptor", "Institution placeholder.", "", "Future external verification.", "NULL in DWH06 seed."),
        ("site_name", "TEXT", "yes", "descriptor", "Site placeholder.", "", "Future external verification.", "NULL in DWH06 seed."),
        ("telescope_status", "TEXT", "no", "status", "Telescope mapping status.", "", "DWH06 seed rule.", common),
        ("evidence_status", "TEXT", "no", "status", "Evidence status.", "", "DWH06 seed rule.", common),
        ("created_at_utc", "TEXT", "no", "audit_timestamp", "Creation timestamp.", "", "DWH06 run timestamp.", common),
        ("notes", "TEXT", "yes", "note", "Defensive note.", "", "DWH06 seed rule.", common),
    ])
    add("dim_receiver", [
        ("receiver_id", "TEXT", "no", "primary_key", "Receiver identifier.", "", "Existing core_observation.receiver_id.", common),
        ("telescope_id", "TEXT", "yes", "foreign_key", "Parent telescope.", "dim_telescope(telescope_id)", "DWH06 placeholder seed.", "Declared FK."),
        ("raw_receiver_name", "TEXT", "yes", "raw_label", "Raw receiver label placeholder.", "", "Future mapping/evidence layer.", "Unresolved in DWH06."),
        ("canonical_receiver_name", "TEXT", "yes", "descriptor", "Canonical receiver placeholder.", "", "Future mapping/evidence layer.", "Unresolved in DWH06."),
        ("frequency_low_mhz", "REAL", "yes", "future_measure", "Future lower frequency bound.", "", "Future evidence only.", "Not populated in DWH06."),
        ("frequency_high_mhz", "REAL", "yes", "future_measure", "Future upper frequency bound.", "", "Future evidence only.", "Not populated in DWH06."),
        ("receiver_status", "TEXT", "no", "status", "Receiver mapping status.", "", "DWH06 seed rule.", common),
        ("evidence_status", "TEXT", "no", "status", "Evidence status.", "", "DWH06 seed rule.", common),
        ("created_at_utc", "TEXT", "no", "audit_timestamp", "Creation timestamp.", "", "DWH06 run timestamp.", common),
        ("notes", "TEXT", "yes", "note", "Defensive note.", "", "DWH06 seed rule.", common),
    ])
    add("dim_backend", [
        ("backend_id", "TEXT", "no", "primary_key", "Backend identifier.", "", "Existing core_observation.backend_id.", common),
        ("telescope_id", "TEXT", "yes", "foreign_key", "Parent telescope.", "dim_telescope(telescope_id)", "DWH06 placeholder seed.", "Declared FK."),
        ("raw_backend_name", "TEXT", "yes", "raw_label", "Raw backend label placeholder.", "", "Future mapping/evidence layer.", "Unresolved in DWH06."),
        ("canonical_backend_name", "TEXT", "yes", "descriptor", "Canonical backend placeholder.", "", "Future mapping/evidence layer.", "Unresolved in DWH06."),
        ("backend_type", "TEXT", "yes", "classification", "Backend type placeholder.", "", "Future mapping/evidence layer.", "NULL in DWH06 seed."),
        ("backend_status", "TEXT", "no", "status", "Backend mapping status.", "", "DWH06 seed rule.", common),
        ("evidence_status", "TEXT", "no", "status", "Evidence status.", "", "DWH06 seed rule.", common),
        ("created_at_utc", "TEXT", "no", "audit_timestamp", "Creation timestamp.", "", "DWH06 run timestamp.", common),
        ("notes", "TEXT", "yes", "note", "Defensive note.", "", "DWH06 seed rule.", common),
    ])
    add("dim_time_context", [
        ("time_context_id", "TEXT", "no", "primary_key", "Time-context identifier.", "", "Existing core_observation.time_context_id.", common),
        ("time_system", "TEXT", "yes", "descriptor", "Time system placeholder.", "", "Future mapping/evidence layer.", "No time conversion in DWH06."),
        ("mjd_start", "TEXT", "yes", "raw_or_future_value", "Future start MJD text.", "", "Future mapping/evidence layer.", "Not populated in DWH06."),
        ("mjd_end", "TEXT", "yes", "raw_or_future_value", "Future end MJD text.", "", "Future mapping/evidence layer.", "Not populated in DWH06."),
        ("clock_context", "TEXT", "yes", "descriptor", "Clock context placeholder.", "", "Future mapping/evidence layer.", "Not populated in DWH06."),
        ("ephemeris_context", "TEXT", "yes", "descriptor", "Ephemeris context placeholder.", "", "Future mapping/evidence layer.", "Not populated in DWH06."),
        ("barycentric_context", "TEXT", "yes", "descriptor", "Barycentric context placeholder.", "", "Future mapping/evidence layer.", "Not populated in DWH06."),
        ("time_context_status", "TEXT", "no", "status", "Time-context mapping status.", "", "DWH06 seed rule.", common),
        ("evidence_status", "TEXT", "no", "status", "Evidence status.", "", "DWH06 seed rule.", common),
        ("created_at_utc", "TEXT", "no", "audit_timestamp", "Creation timestamp.", "", "DWH06 run timestamp.", common),
        ("notes", "TEXT", "yes", "note", "Defensive note.", "", "DWH06 seed rule.", common),
    ])
    add("dim_processing_context", [
        ("processing_context_id", "TEXT", "no", "primary_key", "Processing context identifier.", "", "Existing core_observation.processing_context_id.", common),
        ("pipeline_name", "TEXT", "yes", "descriptor", "Pipeline name placeholder.", "", "Future processing metadata.", "NULL in DWH06 seed."),
        ("pipeline_version", "TEXT", "yes", "descriptor", "Pipeline version placeholder.", "", "Future processing metadata.", "NULL in DWH06 seed."),
        ("processing_label", "TEXT", "yes", "descriptor", "Processing label placeholder.", "", "Future processing metadata.", "NULL in DWH06 seed."),
        ("product_type", "TEXT", "yes", "classification", "Product type placeholder.", "", "Future processing metadata.", "NULL in DWH06 seed."),
        ("processing_status", "TEXT", "no", "status", "Processing mapping status.", "", "DWH06 seed rule.", common),
        ("evidence_status", "TEXT", "no", "status", "Evidence status.", "", "DWH06 seed rule.", common),
        ("created_at_utc", "TEXT", "no", "audit_timestamp", "Creation timestamp.", "", "DWH06 run timestamp.", common),
        ("notes", "TEXT", "yes", "note", "Defensive note.", "", "DWH06 seed rule.", common),
    ])
    add("dim_quality_status", [
        ("quality_status_id", "TEXT", "no", "primary_key", "Quality status identifier.", "", "Existing core_observation.quality_status_id.", common),
        ("quality_class", "TEXT", "no", "classification", "Quality class.", "", "DWH06 seed rule.", common),
        ("quality_flag", "TEXT", "yes", "status", "Quality flag.", "", "DWH06 seed rule.", common),
        ("quarantine_status", "TEXT", "yes", "status", "Quarantine status.", "", "DWH06 seed rule.", common),
        ("anomaly_status", "TEXT", "yes", "status", "Anomaly status.", "", "DWH06 seed rule.", common),
        ("quality_status", "TEXT", "no", "status", "Quality lifecycle status.", "", "DWH06 seed rule.", common),
        ("evidence_status", "TEXT", "no", "status", "Evidence status.", "", "DWH06 seed rule.", common),
        ("created_at_utc", "TEXT", "no", "audit_timestamp", "Creation timestamp.", "", "DWH06 run timestamp.", common),
        ("notes", "TEXT", "yes", "note", "Defensive note.", "", "DWH06 seed rule.", common),
    ])
    add("dwh06_dimension_run_log", [
        ("run_id", "TEXT", "no", "primary_key", "DWH06 run identifier.", "", "Generated by DWH06 script.", "Workcopy metadata only."),
        ("run_timestamp_utc", "TEXT", "yes", "audit_timestamp", "Run timestamp.", "", "Generated by DWH06 script.", "UTC text."),
        ("live_db_path", "TEXT", "yes", "lineage_attribute", "Live DB path.", "", "DWH06 --live-db.", "Live DB opened read-only."),
        ("workcopy_db_path", "TEXT", "yes", "lineage_attribute", "Workcopy DB path.", "", "DWH06 --workcopy-db.", "Only workcopy modified."),
        ("script_name", "TEXT", "yes", "audit_attribute", "Script name.", "", "DWH06 constant.", "No hidden code."),
        ("operation_mode", "TEXT", "yes", "audit_status", "Operation mode.", "", "DWH06 constant.", "Workcopy-only."),
        ("live_db_modified", "INTEGER", "yes", "flag", "Whether live DB changed.", "", "Checksum comparison.", "Expected 0."),
        ("workcopy_db_modified", "INTEGER", "yes", "flag", "Whether workcopy changed.", "", "DWH06 script.", "Expected 1."),
        ("created_dimension_table_count", "INTEGER", "yes", "measure_count", "Dimension table count.", "", "DWH06 script.", "Expected 7."),
        ("inserted_dimension_row_count", "INTEGER", "yes", "measure_count", "Dimension seed row count.", "", "DWH06 script.", "Expected 7."),
        ("updated_core_observation_count", "INTEGER", "yes", "measure_count", "Updated core observation rows.", "", "DWH06 script.", "Expected 0."),
        ("integrity_check_result", "TEXT", "yes", "validation_result", "Workcopy integrity result.", "", "PRAGMA integrity_check.", "Expected ok."),
        ("foreign_key_violation_count", "INTEGER", "yes", "validation_result", "Workcopy FK violation count.", "", "PRAGMA foreign_key_check.", "Expected 0."),
        ("notes", "TEXT", "yes", "note", "Run note.", "", "DWH06 script.", "No scientific claim."),
    ])
    return rows


def field_catalog_rows() -> list[dict[str, Any]]:
    return [
        {
            "table_name": item.table_name,
            "field_name": item.field_name,
            "field_type": item.field_type,
            "nullable": item.nullable,
            "field_role": item.field_role,
            "field_description": item.field_description,
            "fk_target": item.fk_target,
            "source_or_future_mapping_rule": item.source_or_future_mapping_rule,
            "notes": item.notes,
        }
        for item in field_specs()
    ]


def seed_rows_for_csv(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_dwh06_dimension_seed_rows
        ORDER BY dimension_name, dimension_id
        """,
    )
    return [
        {
            "dimension_table": row["dimension_name"],
            "dimension_id": row["dimension_id"],
            "display_label": row["display_label"],
            "seed_status": row["status"],
            "evidence_status": row["evidence_status"],
            "source_basis": source_basis_for_dimension(row["dimension_name"]),
            "notes": row["notes"],
        }
        for row in rows
    ]


def source_basis_for_dimension(dimension_name: str) -> str:
    mapping = {
        "dim_science_object": "core_dataset/core_observation object_id",
        "dim_telescope": "core_observation telescope_id placeholder",
        "dim_receiver": "core_observation receiver_id placeholder",
        "dim_backend": "core_observation backend_id placeholder",
        "dim_time_context": "core_observation time_context_id placeholder",
        "dim_processing_context": "core_observation processing_context_id placeholder",
        "dim_quality_status": "core_observation quality_status_id placeholder",
    }
    return mapping.get(dimension_name, "DWH06 seed rule")


def link_status_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_dwh06_observation_dimension_link_status
        ORDER BY observation_id
        """,
    )
    return [
        {
            "observation_id": row["observation_id"],
            "object_link_status": row["object_link_status"],
            "telescope_link_status": row["telescope_link_status"],
            "receiver_link_status": row["receiver_link_status"],
            "backend_link_status": row["backend_link_status"],
            "time_context_link_status": row["time_context_link_status"],
            "processing_link_status": row["processing_link_status"],
            "quality_link_status": row["quality_link_status"],
            "overall_dimension_link_status": row["overall_dimension_link_status"],
            "notes": "Validation view only; core_observation table definition was not rebuilt.",
        }
        for row in rows
    ]


def build_validation_report(
    live_db: Path,
    workcopy_db: Path,
    live_before: dict[str, Any],
    live_after: dict[str, Any],
    validation: dict[str, Any],
) -> list[dict[str, Any]]:
    seed_count = sum(validation["table_counts"][table] for table in DIMENSION_TABLES)
    link_rows = validation["link_rows"]
    all_linked = all(row["overall_dimension_link_status"] == "fully_linked" for row in link_rows)
    view_ok = all(view in validation["view_counts"] for view in DWH06_VIEWS)

    def row(name: str, scope: str, expected: str, actual: str, ok: bool, notes: str) -> dict[str, Any]:
        return {
            "check_name": name,
            "check_scope": scope,
            "expected_result": expected,
            "actual_result": actual,
            "status": "passed" if ok else "failed",
            "notes": notes,
        }

    rows = [
        row("live_db_checksum_unchanged", str(live_db), live_before["sha256"], live_after["sha256"], live_before["sha256"] == live_after["sha256"], "Live DB opened read-only."),
        row("live_db_size_unchanged", str(live_db), str(live_before["stat"]["size_bytes"]), str(live_after["stat"]["size_bytes"]), live_before["stat"]["size_bytes"] == live_after["stat"]["size_bytes"], "File stat size check."),
        row("workcopy_integrity_check", str(workcopy_db), "ok", validation["integrity"], validation["integrity"] == "ok", "Workcopy integrity after DWH06."),
        row("workcopy_foreign_key_check", str(workcopy_db), "0", str(len(validation["fk_violations"])), not validation["fk_violations"], "Declared dim_receiver/dim_backend FKs should be clean."),
        row("dimension_table_count", "workcopy", str(len(DIMENSION_TABLES)), str(sum(1 for table in DIMENSION_TABLES if table in validation["table_counts"])), all(table in validation["table_counts"] for table in DIMENSION_TABLES), "Seven dimension tables expected."),
        row("dimension_seed_row_count", "workcopy", "7", str(seed_count), seed_count == 7, "One governed placeholder/pending row per dimension table."),
        row("core_observation_dimension_links", "qsb_v_dwh06_observation_dimension_link_status", "all fully_linked", pretty_json(link_rows), all_linked, "Validation view links existing core_observation values to dimension rows."),
        row("dwh06_views_queryable", "workcopy", "4", str(len(validation["view_counts"])), view_ok, "DWH06 dashboard, link status, seed rows, and next actions views are queryable."),
    ]
    return rows


def next_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH07_A",
            "next_step_name": "ERD export and visual inspection for core + dimension skeleton",
            "prerequisite": "DWH06 dimension links fully linked and FK validation clean",
            "recommended_action": "Generate a focused ERD slice showing core_observation and all dim_* context tables.",
            "risk_level": "low",
            "notes": "Recommended next step because the schema was expanded and should be visually inspected before more layers.",
        },
        {
            "next_step_id": "DWH07_B",
            "next_step_name": "Mapping/Evidence target skeleton in workcopy",
            "prerequisite": "Core + dimension ERD accepted",
            "recommended_action": "Create map_token_dictionary, map_token_role, value assertion, evidence, review, and gap skeletons.",
            "risk_level": "medium",
            "notes": "Needed before TIM/PAR token role migration.",
        },
        {
            "next_step_id": "DWH07_C",
            "next_step_name": "Rebuild core_observation with enforced dimension FKs in a fresh workcopy",
            "prerequisite": "Decision to enforce dimension FKs at SQLite schema level",
            "recommended_action": "Create a fresh workcopy and rebuild core_observation with FK clauses in a controlled script.",
            "risk_level": "high",
            "notes": "SQLite cannot add these FK constraints in place without table rebuild.",
        },
        {
            "next_step_id": "DWH07_D",
            "next_step_name": "External evidence verification for telescope/receiver/backend before mapping skeleton",
            "prerequisite": "Decision to resolve instrument placeholders before token mapping",
            "recommended_action": "Use approved external evidence workflow; do not infer final mappings from placeholder text.",
            "risk_level": "medium",
            "notes": "DWH06 intentionally seeds missing_external_evidence statuses.",
        },
    ]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for item in rows:
            writer.writerow(item)


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for item in rows:
        values = [str(item.get(column, "")).replace("|", "/") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def render_readout(
    live_db: Path,
    workcopy_db: Path,
    table_catalog: list[dict[str, Any]],
    seed_rows: list[dict[str, Any]],
    link_rows: list[dict[str, Any]],
    validation_report: list[dict[str, Any]],
    live_modified: bool,
) -> str:
    lines = [
        "# QSB-DWH06 Dimension Skeleton Readout",
        "",
        f"Generated at UTC: {utc_now()}",
        f"Script: `{SCRIPT_NAME}`",
        f"Live DB: `{live_db}`",
        f"Workcopy DB: `{workcopy_db}`",
        "",
        "## 1. Executive summary",
        "",
        (
            "DWH06 created the first governed dimension skeleton in the DWH03/DWH05 "
            "workcopy. It added seven dim_* tables, inserted one placeholder or "
            "pending seed row per dimension, and validated that existing "
            "core_observation context values now resolve through dimension rows."
        ),
        "",
        "## 2. Workcopy-only dimension skeleton principle",
        "",
        "Only the workcopy DB was modified. The live DB was opened read-only for integrity, FK, checksum, and file-stat protection checks.",
        "",
        "## 3. Live DB protection",
        "",
        f"Live DB modified by DWH06: `{str(live_modified).lower()}`",
        "",
        "## 4. Dimension tables created",
        "",
        markdown_table(table_catalog, ["table_name", "row_count_actual", "implementation_status", "notes"]),
        "",
        "## 5. Dimension seed rows",
        "",
        markdown_table(seed_rows, ["dimension_table", "dimension_id", "display_label", "seed_status", "evidence_status"]),
        "",
        "## 6. Observation-to-dimension link validation",
        "",
        markdown_table(link_rows, ["observation_id", "object_link_status", "telescope_link_status", "receiver_link_status", "backend_link_status", "time_context_link_status", "processing_link_status", "quality_link_status", "overall_dimension_link_status"]),
        "",
        "## 7. FK/integrity validation",
        "",
        markdown_table(validation_report, ["check_name", "check_scope", "expected_result", "actual_result", "status"]),
        "",
        "## 8. ERD expectation after DWH06",
        "",
        (
            "A focused ERD should now show core_observation values resolving to "
            "dim_science_object, dim_telescope, dim_receiver, dim_backend, "
            "dim_time_context, dim_processing_context, and dim_quality_status. "
            "Because core_observation was not rebuilt, the links are validated "
            "by views and indexes rather than enforced as SQLite FK clauses."
        ),
        "",
        "## 9. What DWH06 does not do",
        "",
        "- It does not modify the live DB.",
        "- It does not read raw TIM/PAR files.",
        "- It does not verify external source evidence.",
        "- It does not resolve final telescope, receiver, backend, time, or quality semantics.",
        "- It does not rebuild core_observation with enforced dimension FKs.",
        "- It does not create mapping/evidence, bridge, or result target layers.",
        "",
        "## 10. Recommended DWH07 options",
        "",
        "- Option A: ERD export and visual inspection for core + dimension skeleton.",
        "- Option B: Mapping/Evidence target skeleton in workcopy.",
        "- Option C: Rebuild core_observation with enforced dimension FKs in a fresh workcopy.",
        "- Option D: External evidence verification for telescope/receiver/backend before mapping skeleton.",
        "",
        "Recommended next option: Option A, because the dimension skeleton should be visually inspected before adding the mapping/evidence layer.",
        "",
        "## 11. Claim boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ]
    return "\n".join(lines)


def write_reports(
    output_root: Path,
    live_db: Path,
    workcopy_db: Path,
    validation: dict[str, Any],
    validation_report: list[dict[str, Any]],
    live_modified: bool,
    con: sqlite3.Connection,
) -> None:
    paths = output_paths(output_root)
    table_catalog = table_catalog_rows(con)
    seed_rows = seed_rows_for_csv(con)
    link_rows = link_status_rows(con)
    summary = {
        "live_db_path": str(live_db),
        "live_db_modified": live_modified,
        "workcopy_db_path": str(workcopy_db),
        "dimension_tables_created": DIMENSION_TABLES,
        "dimension_seed_row_count": sum(validation["table_counts"][table] for table in DIMENSION_TABLES),
        "updated_core_observation_count": 0,
        "workcopy_integrity_check": validation["integrity"],
        "workcopy_foreign_key_violation_count": len(validation["fk_violations"]),
        "fully_linked_observation_count": validation["dashboard"].get("fully_linked_observation_count"),
        "missing_dimension_link_count": validation["dashboard"].get("missing_dimension_link_count"),
        "recommended_dwh07_option": "Option A: ERD export and visual inspection for core + dimension skeleton",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    paths[READOUT_MD].write_text(
        render_readout(live_db, workcopy_db, table_catalog, seed_rows, link_rows, validation_report, live_modified),
        encoding="utf-8",
    )
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    write_csv(
        paths[TABLE_CATALOG_CSV],
        ["table_name", "layer", "purpose", "grain", "primary_key", "row_count_actual", "implementation_status", "notes"],
        table_catalog,
    )
    write_csv(
        paths[FIELD_CATALOG_CSV],
        ["table_name", "field_name", "field_type", "nullable", "field_role", "field_description", "fk_target", "source_or_future_mapping_rule", "notes"],
        field_catalog_rows(),
    )
    write_csv(
        paths[SEED_ROWS_CSV],
        ["dimension_table", "dimension_id", "display_label", "seed_status", "evidence_status", "source_basis", "notes"],
        seed_rows,
    )
    write_csv(
        paths[LINK_STATUS_CSV],
        ["observation_id", "object_link_status", "telescope_link_status", "receiver_link_status", "backend_link_status", "time_context_link_status", "processing_link_status", "quality_link_status", "overall_dimension_link_status", "notes"],
        link_rows,
    )
    write_csv(
        paths[FK_REPORT_CSV],
        ["check_name", "check_scope", "expected_result", "actual_result", "status", "notes"],
        validation_report,
    )
    write_csv(
        paths[NEXT_STEPS_CSV],
        ["next_step_id", "next_step_name", "prerequisite", "recommended_action", "risk_level", "notes"],
        next_steps_rows(),
    )


def execute_dwh06(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    preflight: dict[str, Any],
) -> dict[str, Any]:
    del preflight
    live_before = db_state(live_db)
    run_id = f"DWH06_DIMENSION_SKELETON_{timestamp_for_id()}"
    created_at = utc_now()

    with connect_writable(workcopy_db) as con:
        try:
            con.execute("BEGIN")
            create_tables(con)
            insert_seed_rows(con, created_at)
            create_views(con)
            interim_integrity = integrity_check(con)
            interim_fk = len(foreign_key_violations(con))
            live_mid = db_state(live_db)
            insert_run_log(
                con,
                run_id,
                created_at,
                live_db,
                workcopy_db,
                live_mid["sha256"] != live_before["sha256"],
                interim_integrity,
                interim_fk,
            )
            validation = validate_workcopy(con)
            if validation["integrity"] != "ok" or validation["fk_violations"]:
                raise RuntimeError("DWH06 workcopy validation failed before commit.")
            if validation["dashboard"].get("missing_dimension_link_count") not in (0, None):
                raise RuntimeError("DWH06 dimension link validation found missing links before commit.")
            live_after = db_state(live_db)
            validation_report = build_validation_report(live_db, workcopy_db, live_before, live_after, validation)
            if any(row["status"] != "passed" for row in validation_report):
                raise RuntimeError("DWH06 validation report contains failed checks before commit.")
            write_reports(output_root, live_db, workcopy_db, validation, validation_report, live_after["sha256"] != live_before["sha256"], con)
            con.commit()
        except Exception:
            con.rollback()
            raise

    live_after = db_state(live_db)
    with connect_readonly(workcopy_db) as con:
        validation = validate_workcopy(con)
        validation_report = build_validation_report(live_db, workcopy_db, live_before, live_after, validation)
    return {
        "live_before": live_before,
        "live_after": live_after,
        "live_modified": live_before["sha256"] != live_after["sha256"],
        "validation": validation,
        "validation_report": validation_report,
    }


def run(args: argparse.Namespace) -> int:
    live_db = Path(args.live_db)
    workcopy_db = Path(args.workcopy_db)
    output_root = Path(args.output_root)
    preflight = ensure_preconditions(
        live_db,
        workcopy_db,
        output_root,
        args.overwrite,
        args.allow_existing,
    )
    result = execute_dwh06(live_db, workcopy_db, output_root, preflight)
    validation = result["validation"]
    print(f"Live DB modified: {result['live_modified']}")
    print(f"Workcopy DB: {workcopy_db}")
    print(f"Dimension tables: {len(DIMENSION_TABLES)}")
    print(f"Dimension seed rows: {sum(validation['table_counts'][table] for table in DIMENSION_TABLES)}")
    print(f"Updated core_observation rows: 0")
    print(f"Fully linked observations: {validation['dashboard'].get('fully_linked_observation_count')}")
    print(f"Missing dimension links: {validation['dashboard'].get('missing_dimension_link_count')}")
    print(f"Workcopy integrity_check: {validation['integrity']}")
    print(f"Workcopy FK violations: {len(validation['fk_violations'])}")
    print(f"Wrote {len(OUTPUT_FILENAMES)} DWH06 output files to {output_root}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create QSB-DWH06 governed dimension skeleton tables in the DWH03/DWH05 "
            "workcopy only and validate core_observation dimension links."
        )
    )
    parser.add_argument("--live-db", default=str(DEFAULT_LIVE_DB), help="Path to live Research DWH DB opened read-only.")
    parser.add_argument("--workcopy-db", default=str(DEFAULT_WORKCOPY_DB), help="Path to DWH03/DWH05 workcopy DB to modify.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Directory for DWH06 report outputs.")
    parser.add_argument("--overwrite", action="store_true", help="Allow controlled regeneration of DWH06 report outputs only.")
    parser.add_argument("--allow-existing", action="store_true", help="Allow controlled re-inspection if DWH06 objects already exist.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parse_args(sys.argv[1:] if argv is None else argv))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
