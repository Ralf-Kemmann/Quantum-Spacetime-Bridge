#!/usr/bin/env python3
"""QSB-DWH05: raw/core migration dry-run into the DWH03 workcopy.

This script performs a controlled migration dry-run into the DWH03 workcopy DB
only. It migrates existing DB20/DB21 raw/source structures already present in
the copied workcopy database into the DWH03 raw/core target skeleton, validates
row-count parity and FK integrity, and writes DB-backed reports.

It does not modify the live DB, does not read raw TIM/PAR files, does not use
CSV/JSON/MD reports as input substrate, does not create a separate analysis DB,
does not delete or alter legacy DBXX tables, does not compute physical,
timing, residual, delay, model, or statistical quantities, and does not assign
final physical meaning to unresolved TIM tokens.
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


SCRIPT_NAME = "scripts/qsb_dwh05_raw_core_migration_dry_run.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh05_raw_core_migration_dry_run_readout.md"
SUMMARY_JSON = "dwh05_raw_core_migration_dry_run_summary.json"
SOURCE_MAP_CSV = "dwh05_source_to_core_dataset_map.csv"
RAW_SOURCE_FILE_CSV = "dwh05_raw_source_file_migration.csv"
RAW_RECORD_PARITY_CSV = "dwh05_raw_record_migration_parity.csv"
RAW_FIELD_PARITY_CSV = "dwh05_raw_field_value_migration_parity.csv"
OBS_LINK_PARITY_CSV = "dwh05_core_observation_record_link_parity.csv"
FK_REPORT_CSV = "dwh05_fk_validation_report.csv"
NEXT_STEPS_CSV = "dwh05_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    SOURCE_MAP_CSV,
    RAW_SOURCE_FILE_CSV,
    RAW_RECORD_PARITY_CSV,
    RAW_FIELD_PARITY_CSV,
    OBS_LINK_PARITY_CSV,
    FK_REPORT_CSV,
    NEXT_STEPS_CSV,
]

TARGET_TABLES = [
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
]

DWH03_REQUIRED_TABLES = [
    "dwh03_workcopy_run_log",
    *TARGET_TABLES,
]

DWH05_VIEWS = [
    "qsb_v_dwh05_raw_core_migration_dashboard",
    "qsb_v_dwh05_raw_record_lineage_sample",
    "qsb_v_dwh05_observation_record_link_status",
    "qsb_v_dwh05_parity_status",
]

SOURCE_REGISTRY_ID = "SRCREG::j0740_6620"
DATASET_ID = "DATASET::j0740_6620"
OBSERVATION_ID = "OBS::j0740_6620::par_tim_context"

CLAIM_BOUNDARY = (
    "DWH05 is a workcopy-only raw/core migration dry-run. It tests whether "
    "legacy DB20/DB21 source inventory, raw records, and raw field values can "
    "be loaded into the DWH03 raw/core skeleton with row-count parity and FK "
    "integrity. It does not modify the live DB, does not read raw TIM/PAR "
    "files, does not resolve physical semantics, and does not make scientific "
    "interpretation claims."
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
            "Refusing to overwrite existing DWH05 output file(s): "
            + "; ".join(existing)
        )


def ensure_preconditions(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
    allow_existing_target_data: bool,
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
        missing_skeleton = [
            table for table in DWH03_REQUIRED_TABLES
            if not object_exists(con, table, "table")
        ]
        if missing_skeleton:
            raise RuntimeError("Missing DWH03 skeleton table(s): " + ", ".join(missing_skeleton))
        skeleton_counts = {table: table_count(con, table) for table in DWH03_REQUIRED_TABLES}
        existing_target_counts = {table: skeleton_counts[table] for table in TARGET_TABLES}
        legacy_presence = inspect_legacy_presence(con)

    if work_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {work_integrity}")
    if work_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(work_fk)} row(s).")
    if skeleton_counts["dwh03_workcopy_run_log"] != 1:
        raise RuntimeError(
            "Expected dwh03_workcopy_run_log = 1 before DWH05; found "
            + str(skeleton_counts["dwh03_workcopy_run_log"])
        )
    non_empty_targets = {
        table: count for table, count in existing_target_counts.items() if count != 0
    }
    if non_empty_targets and not allow_existing_target_data:
        raise RuntimeError(
            "Target raw/core skeleton tables already contain data; use "
            "--allow-existing-target-data only for controlled re-inspection: "
            + pretty_json(non_empty_targets)
        )
    if not legacy_presence["db21_tim_raw_record"]["exists"]:
        raise RuntimeError("Required TIM raw record source db21_tim_raw_record is missing.")
    if not legacy_presence["db21_tim_raw_field_value"]["exists"]:
        raise RuntimeError("Required TIM raw field value source db21_tim_raw_field_value is missing.")
    if not legacy_presence["db21_par_tim_source_inventory"]["exists"]:
        raise RuntimeError("Required DB21 source inventory db21_par_tim_source_inventory is missing.")

    return {
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "work_integrity": work_integrity,
        "work_fk_count": len(work_fk),
        "skeleton_counts": skeleton_counts,
        "legacy_presence": legacy_presence,
        "target_had_existing_data": bool(non_empty_targets),
    }


def inspect_legacy_presence(con: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    candidates = [
        "qsb_v_db21_par_tim_source_inventory",
        "db21_par_tim_source_inventory",
        "qsb_v_db21_tim_raw_records",
        "db21_tim_raw_record",
        "qsb_v_db21_tim_raw_field_values",
        "db21_tim_raw_field_value",
        "db20_rawdata_file_inventory",
        "db20_rawdata_ingest_run",
        "db20_rawdata_record",
        "db20_rawdata_field_value",
    ]
    result: dict[str, dict[str, Any]] = {}
    for name in candidates:
        row = con.execute(
            """
            SELECT type
            FROM sqlite_master
            WHERE name = ?
              AND type IN ('table', 'view')
            """,
            (name,),
        ).fetchone()
        if row:
            count = table_count(con, name)
            result[name] = {"exists": True, "type": row["type"], "row_count": count}
        else:
            result[name] = {"exists": False, "type": None, "row_count": None}
    return result


def create_metadata_table_and_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE dwh05_migration_dry_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            live_db_path TEXT,
            workcopy_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            migrated_source_file_count INTEGER,
            migrated_ingest_run_count INTEGER,
            migrated_raw_record_count INTEGER,
            migrated_raw_field_value_count INTEGER,
            observation_record_link_count INTEGER,
            source_record_count INTEGER,
            source_field_value_count INTEGER,
            record_parity_status TEXT,
            field_value_parity_status TEXT,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT,
            CHECK (live_db_modified IN (0, 1)),
            CHECK (workcopy_db_modified IN (0, 1))
        );

        CREATE VIEW qsb_v_dwh05_raw_core_migration_dashboard AS
        SELECT
            run_id,
            migrated_source_file_count,
            migrated_ingest_run_count,
            migrated_raw_record_count,
            migrated_raw_field_value_count,
            observation_record_link_count,
            source_record_count,
            source_field_value_count,
            record_parity_status,
            field_value_parity_status,
            integrity_check_result,
            foreign_key_violation_count
        FROM dwh05_migration_dry_run_log
        ORDER BY run_timestamp_utc DESC, run_id DESC;

        CREATE VIEW qsb_v_dwh05_raw_record_lineage_sample AS
        SELECT
            rsf.raw_source_file_id,
            rsf.source_filename,
            rir.ingest_run_id,
            rr.raw_record_id,
            rr.record_index,
            rr.line_type,
            rr.lineage_key AS raw_record_lineage_key,
            (
                SELECT COUNT(*)
                FROM raw_field_value AS rfv
                WHERE rfv.raw_record_id = rr.raw_record_id
            ) AS field_value_count,
            (
                SELECT rfv.raw_field_value_id
                FROM raw_field_value AS rfv
                WHERE rfv.raw_record_id = rr.raw_record_id
                ORDER BY rfv.raw_field_value_id
                LIMIT 1
            ) AS sample_raw_field_value_id,
            (
                SELECT rfv.raw_value
                FROM raw_field_value AS rfv
                WHERE rfv.raw_record_id = rr.raw_record_id
                ORDER BY rfv.raw_field_value_id
                LIMIT 1
            ) AS sample_raw_value
        FROM raw_record AS rr
        JOIN raw_ingest_run AS rir
          ON rir.ingest_run_id = rr.ingest_run_id
        JOIN raw_source_file AS rsf
          ON rsf.raw_source_file_id = rr.raw_source_file_id
        ORDER BY rr.raw_record_id
        LIMIT 5;

        CREATE VIEW qsb_v_dwh05_observation_record_link_status AS
        SELECT
            co.observation_id,
            co.observation_label,
            COUNT(corl.observation_record_link_id) AS link_count,
            (SELECT COUNT(*) FROM raw_record) AS target_raw_record_count,
            CASE
                WHEN COUNT(corl.observation_record_link_id) = (SELECT COUNT(*) FROM raw_record)
                THEN 'passed'
                ELSE 'failed'
            END AS link_parity_status
        FROM core_observation AS co
        LEFT JOIN core_observation_record_link AS corl
          ON corl.observation_id = co.observation_id
        GROUP BY co.observation_id, co.observation_label;

        CREATE VIEW qsb_v_dwh05_parity_status AS
        SELECT
            'raw_record' AS parity_scope,
            source_record_count AS source_count,
            migrated_raw_record_count AS target_count,
            record_parity_status AS parity_status
        FROM dwh05_migration_dry_run_log
        UNION ALL
        SELECT
            'raw_field_value',
            source_field_value_count,
            migrated_raw_field_value_count,
            field_value_parity_status
        FROM dwh05_migration_dry_run_log
        UNION ALL
        SELECT
            'observation_record_link',
            migrated_raw_record_count,
            observation_record_link_count,
            CASE
                WHEN migrated_raw_record_count = observation_record_link_count
                THEN 'passed'
                ELSE 'failed'
            END
        FROM dwh05_migration_dry_run_log;
        """
    )


def migrate_core_rows(con: sqlite3.Connection, created_at: str) -> None:
    con.execute(
        """
        INSERT INTO core_source_registry (
            source_registry_id,
            source_name,
            institution,
            source_type,
            official_url,
            citation_note,
            license_note,
            retrieval_status,
            source_status,
            created_at_utc,
            updated_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            SOURCE_REGISTRY_ID,
            "j0740_6620 public source bundle",
            "unknown_or_external_public_source",
            "public_source_bundle",
            None,
            None,
            None,
            "local_untracked_source_present",
            "dry_run_imported_from_legacy_db",
            created_at,
        ),
    )
    con.execute(
        """
        INSERT INTO core_dataset (
            dataset_id,
            source_registry_id,
            dataset_name,
            dataset_version,
            release_label,
            dataset_type,
            object_id,
            dataset_status,
            created_at_utc,
            updated_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            DATASET_ID,
            SOURCE_REGISTRY_ID,
            "J0740+6620 PAR/TIM dataset",
            "legacy_db20_db21_snapshot",
            "local_public_source_bundle",
            "par_tim_source_family",
            "J0740+6620",
            "dry_run_imported_from_legacy_db",
            created_at,
        ),
    )
    con.execute(
        """
        INSERT INTO core_observation (
            observation_id,
            dataset_id,
            object_id,
            telescope_id,
            receiver_id,
            backend_id,
            time_context_id,
            processing_context_id,
            quality_status_id,
            observation_label,
            observation_status,
            created_at_utc,
            updated_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
        """,
        (
            OBSERVATION_ID,
            DATASET_ID,
            "J0740+6620",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "unresolved_placeholder",
            "dry_run_unreviewed",
            "J0740+6620 PAR/TIM raw context",
            "dry_run_context_placeholder",
            created_at,
        ),
    )


def migrate_raw_source_files(con: sqlite3.Connection, created_at: str) -> None:
    con.execute(
        """
        INSERT INTO raw_source_file (
            raw_source_file_id,
            source_registry_id,
            dataset_id,
            source_path,
            source_filename,
            source_format,
            checksum_sha256,
            size_bytes,
            ingest_status,
            created_at_utc
        )
        SELECT
            'RAWFILE::db21_par_tim_source_inventory::' || source_inventory_id,
            ?,
            ?,
            source_path,
            source_file_name,
            source_file_extension,
            source_file_hash_sha256,
            source_file_size_bytes,
            'dry_run_imported_from_legacy_db',
            ?
        FROM db21_par_tim_source_inventory
        WHERE source_type IN ('TIM', 'PAR')
        ORDER BY source_inventory_id
        """,
        (SOURCE_REGISTRY_ID, DATASET_ID, created_at),
    )


def migrate_ingest_runs(con: sqlite3.Connection) -> None:
    con.execute(
        """
        INSERT INTO raw_ingest_run (
            ingest_run_id,
            raw_source_file_id,
            script_id,
            run_timestamp_utc,
            ingest_mode,
            record_count,
            field_value_count,
            status,
            notes
        )
        SELECT
            'INGRUN::db21_tim_raw_record::' || ingest_run_id,
            'RAWFILE::db21_par_tim_source_inventory::' || source_inventory_id,
            'scripts/qsb_db21_par_tim_joinability_first_timing_ingest.py',
            MIN(ingest_timestamp_utc),
            'legacy_db21_tim_raw_ingest',
            COUNT(*),
            (
                SELECT COUNT(*)
                FROM db21_tim_raw_field_value AS fv
                WHERE fv.ingest_run_id = rr.ingest_run_id
            ),
            'dry_run_imported_from_legacy_db',
            'TIM ingest run mapped from db21_tim_raw_record.'
        FROM db21_tim_raw_record AS rr
        GROUP BY ingest_run_id, source_inventory_id
        ORDER BY ingest_run_id, source_inventory_id
        """
    )
    if object_exists(con, "db20_rawdata_record", "table"):
        con.execute(
            """
            INSERT INTO raw_ingest_run (
                ingest_run_id,
                raw_source_file_id,
                script_id,
                run_timestamp_utc,
                ingest_mode,
                record_count,
                field_value_count,
                status,
                notes
            )
            SELECT
                'INGRUN::db20_rawdata_record::' || r.ingest_run_id,
                'RAWFILE::db21_par_tim_source_inventory::' || inv.source_inventory_id,
                'scripts/qsb_db20_first_real_rawdata_contact.py',
                MIN(r.ingest_timestamp_utc),
                'legacy_db20_par_raw_ingest',
                COUNT(*),
                (
                    SELECT COUNT(*)
                    FROM db20_rawdata_field_value AS fv
                    WHERE fv.ingest_run_id = r.ingest_run_id
                ),
                'dry_run_imported_from_legacy_db',
                'PAR ingest run mapped from db20_rawdata_record.'
            FROM db20_rawdata_record AS r
            JOIN db21_par_tim_source_inventory AS inv
              ON inv.source_file_name = r.source_file_name
            GROUP BY r.ingest_run_id, inv.source_inventory_id
            ORDER BY r.ingest_run_id, inv.source_inventory_id
            """
        )


def migrate_raw_records(con: sqlite3.Connection, created_at: str) -> None:
    con.execute(
        """
        INSERT INTO raw_record (
            raw_record_id,
            ingest_run_id,
            raw_source_file_id,
            record_index,
            raw_line_text,
            line_type,
            token_count,
            lineage_key,
            record_status,
            created_at_utc
        )
        SELECT
            'RAWREC::db21_tim_raw_record::' || tim_record_id,
            'INGRUN::db21_tim_raw_record::' || ingest_run_id,
            'RAWFILE::db21_par_tim_source_inventory::' || source_inventory_id,
            record_index,
            raw_line_text,
            line_type,
            token_count,
            lineage_key,
            'dry_run_imported_from_legacy_db',
            ?
        FROM db21_tim_raw_record
        ORDER BY source_inventory_id, record_index, tim_record_id
        """,
        (created_at,),
    )
    if object_exists(con, "db20_rawdata_record", "table"):
        con.execute(
            """
            INSERT INTO raw_record (
                raw_record_id,
                ingest_run_id,
                raw_source_file_id,
                record_index,
                raw_line_text,
                line_type,
                token_count,
                lineage_key,
                record_status,
                created_at_utc
            )
            SELECT
                'RAWREC::db20_rawdata_record::' || r.record_id,
                'INGRUN::db20_rawdata_record::' || r.ingest_run_id,
                'RAWFILE::db21_par_tim_source_inventory::' || inv.source_inventory_id,
                r.record_index,
                r.raw_record_text,
                r.record_structure_class,
                (
                    SELECT COUNT(*)
                    FROM db20_rawdata_field_value AS fv
                    WHERE fv.record_id = r.record_id
                ),
                r.lineage_key,
                'dry_run_imported_from_legacy_db',
                ?
            FROM db20_rawdata_record AS r
            JOIN db21_par_tim_source_inventory AS inv
              ON inv.source_file_name = r.source_file_name
            ORDER BY r.source_file_id, r.record_index, r.record_id
            """,
            (created_at,),
        )


def migrate_raw_field_values(con: sqlite3.Connection, created_at: str) -> None:
    con.execute(
        """
        INSERT INTO raw_field_value (
            raw_field_value_id,
            raw_record_id,
            token_position,
            field_name,
            raw_value,
            value_type_guess,
            lineage_key,
            field_status,
            created_at_utc
        )
        SELECT
            'RAWFLD::db21_tim_raw_field_value::' || tim_field_value_id,
            'RAWREC::db21_tim_raw_record::' || tim_record_id,
            CAST(field_index AS TEXT),
            field_name,
            raw_value_text,
            NULL,
            lineage_key,
            'dry_run_imported_from_legacy_db',
            ?
        FROM db21_tim_raw_field_value
        ORDER BY tim_field_value_id
        """,
        (created_at,),
    )
    if object_exists(con, "db20_rawdata_field_value", "table"):
        con.execute(
            """
            INSERT INTO raw_field_value (
                raw_field_value_id,
                raw_record_id,
                token_position,
                field_name,
                raw_value,
                value_type_guess,
                lineage_key,
                field_status,
                created_at_utc
            )
            SELECT
                'RAWFLD::db20_rawdata_field_value::' || field_value_id,
                'RAWREC::db20_rawdata_record::' || record_id,
                CAST(field_index AS TEXT),
                field_name,
                raw_value_text,
                NULL,
                lineage_key,
                'dry_run_imported_from_legacy_db',
                ?
            FROM db20_rawdata_field_value
            ORDER BY field_value_id
            """,
            (created_at,),
        )


def migrate_observation_links(con: sqlite3.Connection, created_at: str) -> None:
    con.execute(
        """
        INSERT INTO core_observation_record_link (
            observation_record_link_id,
            observation_id,
            raw_record_id,
            link_status,
            mapping_confidence,
            created_at_utc
        )
        SELECT
            'OBSLINK::' || ? || '::' || raw_record_id,
            ?,
            raw_record_id,
            'dry_run_context_link',
            'dry_run_placeholder',
            ?
        FROM raw_record
        ORDER BY raw_record_id
        """,
        (OBSERVATION_ID, OBSERVATION_ID, created_at),
    )


def source_record_count(con: sqlite3.Connection) -> int:
    count = table_count(con, "db21_tim_raw_record")
    if object_exists(con, "db20_rawdata_record", "table"):
        count += table_count(con, "db20_rawdata_record")
    return count


def source_field_value_count(con: sqlite3.Connection) -> int:
    count = table_count(con, "db21_tim_raw_field_value")
    if object_exists(con, "db20_rawdata_field_value", "table"):
        count += table_count(con, "db20_rawdata_field_value")
    return count


def insert_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
    live_modified: bool,
    integrity: str,
    fk_count: int,
) -> None:
    source_records = source_record_count(con)
    source_fields = source_field_value_count(con)
    migrated_records = table_count(con, "raw_record")
    migrated_fields = table_count(con, "raw_field_value")
    con.execute(
        """
        INSERT INTO dwh05_migration_dry_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            migrated_source_file_count,
            migrated_ingest_run_count,
            migrated_raw_record_count,
            migrated_raw_field_value_count,
            observation_record_link_count,
            source_record_count,
            source_field_value_count,
            record_parity_status,
            field_value_parity_status,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(live_db),
            str(workcopy_db),
            SCRIPT_NAME,
            "workcopy_raw_core_migration_dry_run",
            1 if live_modified else 0,
            1,
            table_count(con, "raw_source_file"),
            table_count(con, "raw_ingest_run"),
            migrated_records,
            migrated_fields,
            table_count(con, "core_observation_record_link"),
            source_records,
            source_fields,
            "passed" if migrated_records == source_records else "failed",
            "passed" if migrated_fields == source_fields else "failed",
            integrity,
            fk_count,
            "DWH05 dry-run migrated DB20/DB21 raw/core structures into the workcopy target skeleton only.",
        ),
    )


def validate_workcopy(con: sqlite3.Connection) -> dict[str, Any]:
    integrity = integrity_check(con)
    fk = foreign_key_violations(con)
    counts = {table: table_count(con, table) for table in TARGET_TABLES}
    counts["dwh05_migration_dry_run_log"] = (
        table_count(con, "dwh05_migration_dry_run_log")
        if object_exists(con, "dwh05_migration_dry_run_log", "table")
        else 0
    )
    views = {
        view: object_exists(con, view, "view")
        for view in DWH05_VIEWS
    }
    view_counts = {
        view: table_count(con, view)
        for view, exists in views.items()
        if exists
    }
    return {
        "integrity": integrity,
        "fk_violations": fk,
        "counts": counts,
        "views": views,
        "view_counts": view_counts,
        "source_record_count": source_record_count(con),
        "source_field_value_count": source_field_value_count(con),
    }


def collect_report_rows(con: sqlite3.Connection, legacy_presence: dict[str, dict[str, Any]]) -> dict[str, Any]:
    source_map = [
        {
            "source_family": "j0740_6620",
            "source_registry_id": SOURCE_REGISTRY_ID,
            "dataset_id": DATASET_ID,
            "observation_id": OBSERVATION_ID,
            "source_status": "dry_run_imported_from_legacy_db",
            "mapping_status": "passed",
            "notes": "Single source registry, dataset, and observation context row created for DB20/DB21 PAR/TIM raw context.",
        }
    ]
    raw_source_files = fetch_dicts(
        con,
        """
        SELECT
            'db21_par_tim_source_inventory' AS legacy_source_table,
            CAST(source_inventory_id AS TEXT) AS legacy_source_id,
            'RAWFILE::db21_par_tim_source_inventory::' || source_inventory_id AS raw_source_file_id,
            source_file_name AS source_filename,
            source_file_extension AS source_format,
            line_count,
            CASE
                WHEN EXISTS (
                    SELECT 1
                    FROM raw_source_file AS rsf
                    WHERE rsf.raw_source_file_id = 'RAWFILE::db21_par_tim_source_inventory::' || db21_par_tim_source_inventory.source_inventory_id
                )
                THEN 'migrated'
                ELSE 'missing'
            END AS migration_status,
            'Source-file row migrated from DB21 consolidated source inventory.' AS notes
        FROM db21_par_tim_source_inventory
        WHERE source_type IN ('TIM', 'PAR')
        ORDER BY source_inventory_id
        """,
    )
    record_parity = [
        parity_row(
            con,
            "db21_tim_raw_record",
            table_count(con, "db21_tim_raw_record"),
            "raw_record",
            target_count_by_prefix(con, "raw_record", "raw_record_id", "RAWREC::db21_tim_raw_record::"),
            "TIM records migrated from DB21.",
        )
    ]
    if legacy_presence["db20_rawdata_record"]["exists"]:
        record_parity.append(
            parity_row(
                con,
                "db20_rawdata_record",
                table_count(con, "db20_rawdata_record"),
                "raw_record",
                target_count_by_prefix(con, "raw_record", "raw_record_id", "RAWREC::db20_rawdata_record::"),
                "PAR records migrated from DB20.",
            )
        )
    field_parity = [
        parity_row(
            con,
            "db21_tim_raw_field_value",
            table_count(con, "db21_tim_raw_field_value"),
            "raw_field_value",
            target_count_by_prefix(con, "raw_field_value", "raw_field_value_id", "RAWFLD::db21_tim_raw_field_value::"),
            "TIM field values migrated from DB21.",
            legacy_count_key="legacy_field_value_count",
            target_count_key="target_field_value_count",
        )
    ]
    if legacy_presence["db20_rawdata_field_value"]["exists"]:
        field_parity.append(
            parity_row(
                con,
                "db20_rawdata_field_value",
                table_count(con, "db20_rawdata_field_value"),
                "raw_field_value",
                target_count_by_prefix(con, "raw_field_value", "raw_field_value_id", "RAWFLD::db20_rawdata_field_value::"),
                "PAR field values migrated from DB20.",
                legacy_count_key="legacy_field_value_count",
                target_count_key="target_field_value_count",
            )
        )
    obs_link = [
        {
            "observation_id": OBSERVATION_ID,
            "target_raw_record_count": table_count(con, "raw_record"),
            "link_count": table_count(con, "core_observation_record_link"),
            "parity_status": "passed"
            if table_count(con, "raw_record") == table_count(con, "core_observation_record_link")
            else "failed",
            "notes": "One dry-run observation-record link expected for each migrated raw_record.",
        }
    ]
    dashboard = fetch_dicts(con, "SELECT * FROM qsb_v_dwh05_raw_core_migration_dashboard LIMIT 1")
    lineage_sample = fetch_dicts(con, "SELECT * FROM qsb_v_dwh05_raw_record_lineage_sample LIMIT 5")
    obs_status = fetch_dicts(con, "SELECT * FROM qsb_v_dwh05_observation_record_link_status LIMIT 5")
    parity_status = fetch_dicts(con, "SELECT * FROM qsb_v_dwh05_parity_status")
    return {
        "source_map": source_map,
        "raw_source_files": raw_source_files,
        "record_parity": record_parity,
        "field_parity": field_parity,
        "obs_link": obs_link,
        "dashboard": dashboard,
        "lineage_sample": lineage_sample,
        "obs_status": obs_status,
        "parity_status": parity_status,
    }


def target_count_by_prefix(con: sqlite3.Connection, table: str, field: str, prefix: str) -> int:
    return int(
        con.execute(
            f"""
            SELECT COUNT(*) AS n
            FROM {quote_identifier(table)}
            WHERE {quote_identifier(field)} LIKE ?
            """,
            (prefix + "%",),
        ).fetchone()["n"]
    )


def parity_row(
    con: sqlite3.Connection,
    legacy_table: str,
    legacy_count: int,
    target_table: str,
    target_count: int,
    notes: str,
    legacy_count_key: str = "legacy_record_count",
    target_count_key: str = "target_record_count",
) -> dict[str, Any]:
    return {
        "legacy_source_table": legacy_table,
        legacy_count_key: legacy_count,
        "target_table": target_table,
        target_count_key: target_count,
        "parity_status": "passed" if legacy_count == target_count else "failed",
        "notes": notes,
    }


def build_fk_report(
    live_db: Path,
    workcopy_db: Path,
    live_before: dict[str, Any],
    live_after: dict[str, Any],
    validation: dict[str, Any],
    report_rows: dict[str, Any],
) -> list[dict[str, Any]]:
    record_parity = all(row["parity_status"] == "passed" for row in report_rows["record_parity"])
    field_parity = all(row["parity_status"] == "passed" for row in report_rows["field_parity"])
    link_parity = all(row["parity_status"] == "passed" for row in report_rows["obs_link"])

    def row(name: str, scope: str, expected: str, actual: str, ok: bool, notes: str) -> dict[str, Any]:
        return {
            "check_name": name,
            "check_scope": scope,
            "expected_result": expected,
            "actual_result": actual,
            "status": "passed" if ok else "failed",
            "notes": notes,
        }

    return [
        row("live_db_checksum_unchanged", str(live_db), live_before["sha256"], live_after["sha256"], live_before["sha256"] == live_after["sha256"], "Live DB was opened read-only and must remain unchanged."),
        row("live_db_file_stat_size_unchanged", str(live_db), str(live_before["stat"]["size_bytes"]), str(live_after["stat"]["size_bytes"]), live_before["stat"]["size_bytes"] == live_after["stat"]["size_bytes"], "Size check complements checksum check."),
        row("workcopy_integrity_check", str(workcopy_db), "ok", validation["integrity"], validation["integrity"] == "ok", "Workcopy integrity after DWH05 dry-run."),
        row("workcopy_foreign_key_check", str(workcopy_db), "0", str(len(validation["fk_violations"])), not validation["fk_violations"], "No unresolved FK references expected."),
        row("target_raw_record_parity", "raw_record", "source_count == target_count", "passed" if record_parity else "failed", record_parity, "DB21 TIM plus DB20 PAR raw records compared to target raw_record rows."),
        row("target_raw_field_value_parity", "raw_field_value", "source_count == target_count", "passed" if field_parity else "failed", field_parity, "DB21 TIM plus DB20 PAR field values compared to target raw_field_value rows."),
        row("observation_record_link_parity", "core_observation_record_link", "link_count == raw_record_count", "passed" if link_parity else "failed", link_parity, "One observation-record link per migrated raw_record."),
        row("dwh05_views_queryable", "workcopy", "all views queryable", pretty_json(validation["view_counts"]), all(view in validation["view_counts"] for view in DWH05_VIEWS), "DWH05 dashboard/readout views exist and can be queried."),
    ]


def next_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH06_A",
            "next_step_name": "Dimension skeleton in workcopy",
            "prerequisite": "DWH05 row-count parity and FK validation passed",
            "recommended_action": "Create dim_science_object, dim_telescope, dim_receiver, dim_backend, dim_time_context, dim_processing_context, and dim_quality_status skeletons in the workcopy.",
            "risk_level": "medium",
            "notes": "Keeps unresolved receiver/backend/time placeholders out of final semantics until reviewed.",
        },
        {
            "next_step_id": "DWH06_B",
            "next_step_name": "Mapping/Evidence target skeleton in workcopy",
            "prerequisite": "Raw/core dry-run accepted as structurally stable",
            "recommended_action": "Create map_token_dictionary, map_token_role, map_token_value_assertion, map_external_source, map_assertion_evidence, map_review_decision, and map_evidence_gap skeletons.",
            "risk_level": "medium",
            "notes": "Useful before resolving TIM token roles.",
        },
        {
            "next_step_id": "DWH06_C",
            "next_step_name": "Raw/Core migration refinement if parity gaps appear",
            "prerequisite": "Any DWH05 parity gap or lineage ambiguity",
            "recommended_action": "Adjust deterministic ID mapping and source selection in a new workcopy run.",
            "risk_level": "medium",
            "notes": "Fallback path; do not mutate the live DB.",
        },
        {
            "next_step_id": "DWH06_D",
            "next_step_name": "Commit/compare DWH05 script first",
            "prerequisite": "Repository governance decision",
            "recommended_action": "Compare DWH05 script and outputs before extending target skeleton layers.",
            "risk_level": "low",
            "notes": "No git action is performed by this script.",
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
    legacy_presence: dict[str, dict[str, Any]],
    validation: dict[str, Any],
    report_rows: dict[str, Any],
    fk_report: list[dict[str, Any]],
    live_modified: bool,
) -> str:
    legacy_used = [
        "db21_par_tim_source_inventory",
        "db21_tim_raw_record",
        "db21_tim_raw_field_value",
    ]
    if legacy_presence["db20_rawdata_record"]["exists"]:
        legacy_used.append("db20_rawdata_record")
    if legacy_presence["db20_rawdata_field_value"]["exists"]:
        legacy_used.append("db20_rawdata_field_value")
    lineage_sample = report_rows["lineage_sample"][:1]
    lines = [
        "# QSB-DWH05 Raw/Core Migration Dry-Run Readout",
        "",
        f"Generated at UTC: {utc_now()}",
        f"Script: `{SCRIPT_NAME}`",
        f"Live DB: `{live_db}`",
        f"Workcopy DB: `{workcopy_db}`",
        "",
        "## 1. Executive summary",
        "",
        (
            "DWH05 populated the DWH03 workcopy raw/core skeleton from legacy "
            "DB20/DB21 structures already present in the workcopy. The dry-run "
            "loaded source registry, dataset, observation context, raw source "
            "files, ingest runs, raw records, raw field values, and "
            "observation-record links, then checked row-count parity and FK "
            "integrity."
        ),
        "",
        f"Live DB modified: `{str(live_modified).lower()}`",
        f"Workcopy integrity_check: `{validation['integrity']}`",
        f"Workcopy foreign_key_check count: `{len(validation['fk_violations'])}`",
        "",
        "## 2. Workcopy-only migration principle",
        "",
        (
            "Only the DWH03 workcopy DB was modified. The live DB was opened "
            "read-only for protection checks and checksum/file-stat comparison."
        ),
        "",
        "## 3. Live DB protection",
        "",
        f"Live DB checksum/stat unchanged: `{str(not live_modified).lower()}`",
        "",
        "## 4. Legacy source inventory used",
        "",
        ", ".join(legacy_used),
        "",
        "Legacy source availability:",
        "",
        markdown_table(
            [
                {
                    "object": name,
                    "exists": info["exists"],
                    "rows": info["row_count"],
                }
                for name, info in legacy_presence.items()
            ],
            ["object", "exists", "rows"],
        ),
        "",
        "## 5. Core source/dataset/observation rows created",
        "",
        markdown_table(report_rows["source_map"], ["source_family", "source_registry_id", "dataset_id", "observation_id", "mapping_status"]),
        "",
        "## 6. Raw source file migration",
        "",
        markdown_table(report_rows["raw_source_files"], ["legacy_source_table", "legacy_source_id", "raw_source_file_id", "source_filename", "line_count", "migration_status"]),
        "",
        "## 7. Raw ingest run migration",
        "",
        f"Migrated raw_ingest_run rows: `{validation['counts']['raw_ingest_run']}`",
        "",
        "## 8. Raw record migration parity",
        "",
        markdown_table(report_rows["record_parity"], ["legacy_source_table", "legacy_record_count", "target_table", "target_record_count", "parity_status"]),
        "",
        "## 9. Raw field value migration parity",
        "",
        markdown_table(report_rows["field_parity"], ["legacy_source_table", "legacy_field_value_count", "target_table", "target_field_value_count", "parity_status"]),
        "",
        "## 10. Observation-record link parity",
        "",
        markdown_table(report_rows["obs_link"], ["observation_id", "target_raw_record_count", "link_count", "parity_status"]),
        "",
        "## 11. FK/integrity validation",
        "",
        markdown_table(fk_report, ["check_name", "check_scope", "expected_result", "actual_result", "status"]),
        "",
        "## 12. Lineage sample",
        "",
        markdown_table(lineage_sample, list(lineage_sample[0].keys()) if lineage_sample else ["note"]),
        "",
        "## 13. What DWH05 does not do",
        "",
        "- It does not modify the live DB.",
        "- It does not read raw TIM/PAR files.",
        "- It does not resolve receiver/backend/time or physical token semantics.",
        "- It does not create dimension, mapping/evidence, bridge, or result target layers.",
        "- It does not compute physical quantities or statistical inference.",
        "",
        "## 14. Recommended DWH06 options",
        "",
        "- Option A: Dimension skeleton in workcopy.",
        "- Option B: Mapping/Evidence target skeleton in workcopy.",
        "- Option C: Raw/Core migration refinement if parity gaps appear.",
        "- Option D: Commit/compare DWH05 script first.",
        "",
        "Recommended next option: Option A or B, with Option A preferred if the next goal is to replace unresolved core_observation placeholders with governed dimension rows.",
        "",
        "## 15. Claim boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ]
    return "\n".join(lines)


def write_reports(
    output_root: Path,
    live_db: Path,
    workcopy_db: Path,
    legacy_presence: dict[str, dict[str, Any]],
    validation: dict[str, Any],
    report_rows: dict[str, Any],
    fk_report: list[dict[str, Any]],
    live_modified: bool,
) -> None:
    paths = output_paths(output_root)
    summary = {
        "live_db_path": str(live_db),
        "live_db_modified": live_modified,
        "workcopy_db_path": str(workcopy_db),
        "legacy_source_tables_used": [
            row["legacy_source_table"] for row in report_rows["record_parity"]
        ] + [
            row["legacy_source_table"] for row in report_rows["field_parity"]
        ],
        "core_source_registry_count": validation["counts"]["core_source_registry"],
        "core_dataset_count": validation["counts"]["core_dataset"],
        "core_observation_count": validation["counts"]["core_observation"],
        "raw_source_file_count": validation["counts"]["raw_source_file"],
        "raw_ingest_run_count": validation["counts"]["raw_ingest_run"],
        "raw_record_count": validation["counts"]["raw_record"],
        "raw_field_value_count": validation["counts"]["raw_field_value"],
        "observation_record_link_count": validation["counts"]["core_observation_record_link"],
        "source_record_count": validation["source_record_count"],
        "source_field_value_count": validation["source_field_value_count"],
        "workcopy_integrity_check": validation["integrity"],
        "workcopy_foreign_key_violation_count": len(validation["fk_violations"]),
        "record_parity": report_rows["record_parity"],
        "field_value_parity": report_rows["field_parity"],
        "observation_record_link_parity": report_rows["obs_link"],
        "lineage_sample": report_rows["lineage_sample"][:1],
        "recommended_dwh06_option": "Option A: Dimension skeleton in workcopy",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    paths[READOUT_MD].write_text(
        render_readout(
            live_db,
            workcopy_db,
            legacy_presence,
            validation,
            report_rows,
            fk_report,
            live_modified,
        ),
        encoding="utf-8",
    )
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    write_csv(
        paths[SOURCE_MAP_CSV],
        [
            "source_family",
            "source_registry_id",
            "dataset_id",
            "observation_id",
            "source_status",
            "mapping_status",
            "notes",
        ],
        report_rows["source_map"],
    )
    write_csv(
        paths[RAW_SOURCE_FILE_CSV],
        [
            "legacy_source_table",
            "legacy_source_id",
            "raw_source_file_id",
            "source_filename",
            "source_format",
            "line_count",
            "migration_status",
            "notes",
        ],
        report_rows["raw_source_files"],
    )
    write_csv(
        paths[RAW_RECORD_PARITY_CSV],
        [
            "legacy_source_table",
            "legacy_record_count",
            "target_table",
            "target_record_count",
            "parity_status",
            "notes",
        ],
        report_rows["record_parity"],
    )
    write_csv(
        paths[RAW_FIELD_PARITY_CSV],
        [
            "legacy_source_table",
            "legacy_field_value_count",
            "target_table",
            "target_field_value_count",
            "parity_status",
            "notes",
        ],
        report_rows["field_parity"],
    )
    write_csv(
        paths[OBS_LINK_PARITY_CSV],
        [
            "observation_id",
            "target_raw_record_count",
            "link_count",
            "parity_status",
            "notes",
        ],
        report_rows["obs_link"],
    )
    write_csv(
        paths[FK_REPORT_CSV],
        [
            "check_name",
            "check_scope",
            "expected_result",
            "actual_result",
            "status",
            "notes",
        ],
        fk_report,
    )
    write_csv(
        paths[NEXT_STEPS_CSV],
        [
            "next_step_id",
            "next_step_name",
            "prerequisite",
            "recommended_action",
            "risk_level",
            "notes",
        ],
        next_steps_rows(),
    )


def live_state(path: Path) -> dict[str, Any]:
    return {
        "sha256": file_sha256(path),
        "stat": file_stat(path),
    }


def execute_migration(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    preflight: dict[str, Any],
) -> dict[str, Any]:
    live_before = live_state(live_db)
    run_id = f"DWH05_RAW_CORE_MIGRATION_DRY_RUN_{timestamp_for_id()}"
    created_at = utc_now()
    with connect_writable(workcopy_db) as con:
        try:
            con.execute("BEGIN")
            create_metadata_table_and_views(con)
            migrate_core_rows(con, created_at)
            migrate_raw_source_files(con, created_at)
            migrate_ingest_runs(con)
            migrate_raw_records(con, created_at)
            migrate_raw_field_values(con, created_at)
            migrate_observation_links(con, created_at)
            interim_integrity = integrity_check(con)
            interim_fk_count = len(foreign_key_violations(con))
            live_mid = live_state(live_db)
            insert_log(
                con,
                run_id,
                created_at,
                live_db,
                workcopy_db,
                live_mid["sha256"] != live_before["sha256"],
                interim_integrity,
                interim_fk_count,
            )
            validation = validate_workcopy(con)
            if validation["integrity"] != "ok" or validation["fk_violations"]:
                raise RuntimeError("Workcopy validation failed before commit.")
            if validation["counts"]["raw_record"] != validation["source_record_count"]:
                raise RuntimeError("Raw record parity failed before commit.")
            if validation["counts"]["raw_field_value"] != validation["source_field_value_count"]:
                raise RuntimeError("Raw field value parity failed before commit.")
            if validation["counts"]["core_observation_record_link"] != validation["counts"]["raw_record"]:
                raise RuntimeError("Observation-record link parity failed before commit.")
            report_rows = collect_report_rows(con, preflight["legacy_presence"])
            live_after = live_state(live_db)
            fk_report = build_fk_report(live_db, workcopy_db, live_before, live_after, validation, report_rows)
            if any(row["status"] != "passed" for row in fk_report):
                raise RuntimeError("DWH05 validation report contains failed checks before commit.")
            con.commit()
        except Exception:
            con.rollback()
            raise

    live_after = live_state(live_db)
    with connect_readonly(workcopy_db) as con:
        validation = validate_workcopy(con)
        report_rows = collect_report_rows(con, preflight["legacy_presence"])
    fk_report = build_fk_report(live_db, workcopy_db, live_before, live_after, validation, report_rows)
    live_modified = live_before["sha256"] != live_after["sha256"]
    write_reports(output_root, live_db, workcopy_db, preflight["legacy_presence"], validation, report_rows, fk_report, live_modified)
    return {
        "live_before": live_before,
        "live_after": live_after,
        "live_modified": live_modified,
        "validation": validation,
        "report_rows": report_rows,
        "fk_report": fk_report,
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
        args.allow_existing_target_data,
    )
    result = execute_migration(live_db, workcopy_db, output_root, preflight)
    validation = result["validation"]
    print(f"Live DB modified: {result['live_modified']}")
    print(f"Workcopy DB: {workcopy_db}")
    print(f"core_source_registry: {validation['counts']['core_source_registry']}")
    print(f"core_dataset: {validation['counts']['core_dataset']}")
    print(f"core_observation: {validation['counts']['core_observation']}")
    print(f"raw_source_file: {validation['counts']['raw_source_file']}")
    print(f"raw_ingest_run: {validation['counts']['raw_ingest_run']}")
    print(f"raw_record: {validation['counts']['raw_record']}")
    print(f"raw_field_value: {validation['counts']['raw_field_value']}")
    print(f"core_observation_record_link: {validation['counts']['core_observation_record_link']}")
    print(f"Workcopy integrity_check: {validation['integrity']}")
    print(f"Workcopy FK violations: {len(validation['fk_violations'])}")
    print(f"Wrote {len(OUTPUT_FILENAMES)} DWH05 output files to {output_root}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Perform QSB-DWH05 raw/core migration dry-run into the DWH03 "
            "workcopy only, with row-count parity and FK validation."
        )
    )
    parser.add_argument("--live-db", default=str(DEFAULT_LIVE_DB), help="Path to live Research DWH DB opened read-only.")
    parser.add_argument("--workcopy-db", default=str(DEFAULT_WORKCOPY_DB), help="Path to DWH03 workcopy DB to modify.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Directory for DWH05 report outputs.")
    parser.add_argument("--overwrite", action="store_true", help="Allow controlled regeneration of DWH05 report outputs only.")
    parser.add_argument(
        "--allow-existing-target-data",
        action="store_true",
        help="Allow controlled re-inspection if target raw/core tables already contain data.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parse_args(sys.argv[1:] if argv is None else argv))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
