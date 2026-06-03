#!/usr/bin/env python3
"""QSB-DWH03: raw/core target skeleton in a workcopy DB only.

This script copies the live consolidated QSB Research DB to a dedicated DWH03
workcopy and creates only the first Raw / Entrance and Core / Observation
target skeleton tables in that workcopy. The live DB is opened read-only for
preflight checks and checksum comparison.

No raw TIM/PAR files are read, no CSV/JSON/MD artifacts are used as input
substrate, no legacy data is migrated into the skeleton tables, no full target
DWH schema is created, and no scientific quantities or statistical outputs are
computed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh03_target_schema_workcopy_raw_core_skeleton.py"
DEFAULT_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")
DEFAULT_WORKCOPY_DB = (
    DEFAULT_OUTPUT_ROOT / "qsb_research_dwh_target_workcopy_dwh03.db"
)

READOUT_MD = "dwh03_target_schema_workcopy_readout.md"
SUMMARY_JSON = "dwh03_target_schema_workcopy_summary.json"
DDL_SQL = "dwh03_raw_core_ddl.sql"
TABLE_CATALOG_CSV = "dwh03_raw_core_table_catalog.csv"
FIELD_CATALOG_CSV = "dwh03_raw_core_field_catalog.csv"
PK_FK_CATALOG_CSV = "dwh03_raw_core_pk_fk_catalog.csv"
VALIDATION_CSV = "dwh03_workcopy_validation_report.csv"
NEXT_QUESTIONS_CSV = "dwh03_next_migration_questions.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    DDL_SQL,
    TABLE_CATALOG_CSV,
    FIELD_CATALOG_CSV,
    PK_FK_CATALOG_CSV,
    VALIDATION_CSV,
    NEXT_QUESTIONS_CSV,
]

DWH02_GOVERNANCE_TABLES = [
    "audit_schema_version",
    "audit_migration_log",
    "audit_rebuild_manifest",
    "audit_view_dependency",
    "dwh02_governance_run_log",
]

NEW_TABLES = [
    "dwh03_workcopy_run_log",
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
]

SKELETON_TABLES = [
    "core_source_registry",
    "core_dataset",
    "core_observation",
    "core_observation_record_link",
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
]

RECOMMENDED_DWH04_OPTION = (
    "Option C: ERD export and visual inspection of workcopy before any dry-run "
    "data movement."
)

CLAIM_BOUNDARY = (
    "DWH03 is a workcopy-only target-schema skeleton proposal. It copies the "
    "live DB to a workcopy, creates empty raw/core skeleton tables there, and "
    "validates the workcopy graph. It does not modify the live DB, does not "
    "migrate legacy data, does not create dimension/mapping/bridge/result "
    "tables, and does not make scientific interpretation claims."
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


@dataclass(frozen=True)
class TableSpec:
    table_name: str
    layer: str
    purpose: str
    grain: str
    primary_key: str
    row_count_expected: int
    implementation_status: str
    notes: str


@dataclass(frozen=True)
class FkSpec:
    source_table: str
    source_field: str
    target_table: str
    target_field: str
    fk_status: str
    index_name: str
    relationship_description: str
    erd_slice: str
    notes: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def timestamp_for_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


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


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


def row_count(con: sqlite3.Connection, table_name: str) -> int:
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


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def ensure_preconditions(
    live_db: Path,
    output_root: Path,
    workcopy_db: Path,
    overwrite: bool,
    overwrite_workcopy: bool,
) -> dict[str, Any]:
    if not live_db.exists():
        raise FileNotFoundError(f"Live DB does not exist: {live_db}")
    if not live_db.is_file():
        raise ValueError(f"Live DB path is not a file: {live_db}")
    if live_db.stat().st_size <= 0:
        raise ValueError(f"Live DB is empty: {live_db}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    if workcopy_db.exists() and not overwrite_workcopy:
        raise FileExistsError(
            "Refusing to overwrite existing DWH03 workcopy DB: "
            + str(workcopy_db)
        )
    existing_outputs = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing_outputs and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH03 output file(s): "
            + "; ".join(existing_outputs)
        )

    with connect_readonly(live_db) as con:
        live_integrity = integrity_check(con)
        live_fk_violations = foreign_key_violations(con)
        missing_governance = [
            table for table in DWH02_GOVERNANCE_TABLES
            if not object_exists(con, table, "table")
        ]
        dashboard_exists = object_exists(con, "qsb_v_dwh02_governance_dashboard", "view")
        dashboard_row_count = (
            row_count(con, "qsb_v_dwh02_governance_dashboard")
            if dashboard_exists
            else None
        )
        live_target_collisions = [
            table for table in NEW_TABLES
            if object_exists(con, table)
        ]

    if live_integrity != "ok":
        raise RuntimeError(f"Live DB integrity_check failed: {live_integrity}")
    if live_fk_violations:
        raise RuntimeError(
            f"Live DB foreign_key_check returned {len(live_fk_violations)} violation(s)."
        )
    if missing_governance:
        raise RuntimeError(
            "Required DWH02 governance table(s) missing in live DB: "
            + ", ".join(missing_governance)
        )
    if not dashboard_exists:
        raise RuntimeError("qsb_v_dwh02_governance_dashboard is missing in live DB.")
    if dashboard_row_count is None:
        raise RuntimeError("qsb_v_dwh02_governance_dashboard could not be queried.")
    if live_target_collisions:
        raise RuntimeError(
            "Requested DWH03 target table name(s) already exist in live DB and "
            "would collide in the workcopy: " + ", ".join(live_target_collisions)
        )

    return {
        "live_integrity": live_integrity,
        "live_fk_violation_count": len(live_fk_violations),
        "dwh02_dashboard_row_count": dashboard_row_count,
    }


def table_specs() -> list[TableSpec]:
    return [
        TableSpec("dwh03_workcopy_run_log", "DWH03 Workcopy Metadata", "Records the DWH03 workcopy skeleton run.", "One row per DWH03 workcopy creation run.", "run_id", 1, "created_in_workcopy", "Only metadata table populated in DWH03."),
        TableSpec("core_source_registry", "Core / Observation-Centered Layer", "Conformed source authority and source registry anchor.", "One row per source registry entry.", "source_registry_id", 0, "skeleton_created_empty", "No source rows migrated in DWH03."),
        TableSpec("core_dataset", "Core / Observation-Centered Layer", "Dataset/snapshot object linked to a source registry entry.", "One row per dataset or dataset snapshot.", "dataset_id", 0, "skeleton_created_empty", "References core_source_registry."),
        TableSpec("core_observation", "Core / Observation-Centered Layer", "Central observation anchor for future facts and lineage links.", "One row per future observation anchor.", "observation_id", 0, "skeleton_created_empty", "Dimension references remain TEXT placeholders in DWH03."),
        TableSpec("core_observation_record_link", "Core / Observation-Centered Layer", "Many-to-many bridge between future observations and raw records.", "One row per observation-to-raw-record link.", "observation_record_link_id", 0, "skeleton_created_empty", "References core_observation and raw_record."),
        TableSpec("raw_source_file", "Raw / Entrance Layer", "Source-file entrance object for raw payload references.", "One row per source file reference.", "raw_source_file_id", 0, "skeleton_created_empty", "References core source/dataset when known."),
        TableSpec("raw_ingest_run", "Raw / Entrance Layer", "Raw ingest run metadata scoped to one raw source file.", "One row per raw ingest run.", "ingest_run_id", 0, "skeleton_created_empty", "No ingest data migrated in DWH03."),
        TableSpec("raw_record", "Raw / Entrance Layer", "Raw line/record object preserving source-local order and lineage.", "One row per raw record.", "raw_record_id", 0, "skeleton_created_empty", "References raw_ingest_run and raw_source_file."),
        TableSpec("raw_field_value", "Raw / Entrance Layer", "Raw token/field value object before semantic commitment.", "One row per field/token value.", "raw_field_value_id", 0, "skeleton_created_empty", "References raw_record."),
    ]


def field_specs() -> list[FieldSpec]:
    f = FieldSpec
    return [
        f("dwh03_workcopy_run_log", "run_id", "TEXT", "no", "primary_key", "Stable DWH03 workcopy run identifier.", "", "Generated by DWH03 script.", "Expected one row."),
        f("dwh03_workcopy_run_log", "run_timestamp_utc", "TEXT", "yes", "audit_timestamp", "UTC timestamp for the workcopy run.", "", "Generated by DWH03 script.", "ISO-8601 UTC text."),
        f("dwh03_workcopy_run_log", "live_db_path", "TEXT", "yes", "lineage_attribute", "Path to the protected live DB.", "", "DWH03 --db argument.", "Live DB opened read-only."),
        f("dwh03_workcopy_run_log", "workcopy_db_path", "TEXT", "yes", "lineage_attribute", "Path to the DWH03 workcopy DB.", "", "DWH03 --workcopy-db or default path.", "Workcopy receives skeleton DDL."),
        f("dwh03_workcopy_run_log", "script_name", "TEXT", "yes", "audit_attribute", "Script path for the workcopy run.", "", "DWH03 script constant.", "No code hidden."),
        f("dwh03_workcopy_run_log", "operation_mode", "TEXT", "yes", "audit_status", "Operation mode label.", "", "Set to workcopy_raw_core_skeleton.", "Workcopy/proposal only."),
        f("dwh03_workcopy_run_log", "live_db_modified", "INTEGER", "yes", "flag", "Whether live DB was modified.", "", "Must be 0.", "Confirmed by checksum before/after."),
        f("dwh03_workcopy_run_log", "workcopy_db_modified", "INTEGER", "yes", "flag", "Whether workcopy DB was modified.", "", "Must be 1.", "Skeleton DDL applied to workcopy."),
        f("dwh03_workcopy_run_log", "created_table_count", "INTEGER", "yes", "measure_count", "Number of DWH03 tables created in workcopy.", "", "Script count.", "Expected 9 including run log."),
        f("dwh03_workcopy_run_log", "created_index_count", "INTEGER", "yes", "measure_count", "Number of DWH03 indexes created in workcopy.", "", "Script count.", "Expected 11."),
        f("dwh03_workcopy_run_log", "integrity_check_result", "TEXT", "yes", "validation_result", "Workcopy integrity_check result.", "", "PRAGMA integrity_check.", "Expected ok."),
        f("dwh03_workcopy_run_log", "foreign_key_violation_count", "INTEGER", "yes", "validation_result", "Workcopy FK violation count.", "", "PRAGMA foreign_key_check.", "Expected 0."),
        f("dwh03_workcopy_run_log", "notes", "TEXT", "yes", "note", "Defensive run note.", "", "Generated by DWH03 script.", "No scientific claim."),
        f("core_source_registry", "source_registry_id", "TEXT", "no", "primary_key", "Stable source registry identifier.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("core_source_registry", "source_name", "TEXT", "no", "descriptor", "Human-readable source name.", "", "Future migration from source registry/source inventory.", "NOT NULL."),
        f("core_source_registry", "institution", "TEXT", "yes", "descriptor", "Institution or authority label.", "", "Future evidence/source mapping.", "Optional."),
        f("core_source_registry", "source_type", "TEXT", "no", "classification", "Source type classification.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("core_source_registry", "official_url", "TEXT", "yes", "lineage_attribute", "Official source URL when available.", "", "Future external/source registry mapping.", "Reference only."),
        f("core_source_registry", "citation_note", "TEXT", "yes", "note", "Citation note.", "", "Future evidence/source mapping.", "No payload embedding."),
        f("core_source_registry", "license_note", "TEXT", "yes", "note", "License note.", "", "Future evidence/source mapping.", "No payload embedding."),
        f("core_source_registry", "retrieval_status", "TEXT", "no", "status", "Retrieval or availability status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("core_source_registry", "source_status", "TEXT", "no", "status", "Lifecycle status for the source entry.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("core_source_registry", "created_at_utc", "TEXT", "no", "audit_timestamp", "UTC creation timestamp.", "", "Future migration run timestamp.", "NOT NULL."),
        f("core_source_registry", "updated_at_utc", "TEXT", "yes", "audit_timestamp", "UTC update timestamp.", "", "Future migration/update run timestamp.", "Optional."),
        f("core_dataset", "dataset_id", "TEXT", "no", "primary_key", "Stable dataset identifier.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("core_dataset", "source_registry_id", "TEXT", "no", "foreign_key", "Source registry owning the dataset.", "core_source_registry(source_registry_id)", "Future migration from source registry/source inventory.", "Declared FK."),
        f("core_dataset", "dataset_name", "TEXT", "no", "descriptor", "Dataset name.", "", "Future dataset/snapshot mapping.", "NOT NULL."),
        f("core_dataset", "dataset_version", "TEXT", "yes", "descriptor", "Dataset version string.", "", "Future dataset/snapshot mapping.", "Optional."),
        f("core_dataset", "release_label", "TEXT", "yes", "descriptor", "Release or snapshot label.", "", "Future dataset/snapshot mapping.", "Optional."),
        f("core_dataset", "dataset_type", "TEXT", "yes", "classification", "Dataset type.", "", "Future controlled vocabulary.", "Optional."),
        f("core_dataset", "object_id", "TEXT", "yes", "future_dimension_key", "Science object placeholder.", "future dim_science_object(science_object_id)", "Future dimension skeleton or mapping phase.", "Future FK only."),
        f("core_dataset", "dataset_status", "TEXT", "no", "status", "Dataset lifecycle status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("core_dataset", "created_at_utc", "TEXT", "no", "audit_timestamp", "UTC creation timestamp.", "", "Future migration run timestamp.", "NOT NULL."),
        f("core_dataset", "updated_at_utc", "TEXT", "yes", "audit_timestamp", "UTC update timestamp.", "", "Future migration/update run timestamp.", "Optional."),
        f("core_observation", "observation_id", "TEXT", "no", "primary_key", "Stable observation anchor.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("core_observation", "dataset_id", "TEXT", "no", "foreign_key", "Dataset containing the observation.", "core_dataset(dataset_id)", "Future observation migration.", "Declared FK."),
        f("core_observation", "object_id", "TEXT", "yes", "future_dimension_key", "Science object placeholder.", "future dim_science_object(science_object_id)", "Future dimension skeleton or mapping phase.", "Future FK only."),
        f("core_observation", "telescope_id", "TEXT", "yes", "future_dimension_key", "Telescope placeholder.", "future dim_telescope(telescope_id)", "Future dimension skeleton.", "Future FK only."),
        f("core_observation", "receiver_id", "TEXT", "yes", "future_dimension_key", "Receiver placeholder.", "future dim_receiver(receiver_id)", "Future dimension skeleton.", "Future FK only."),
        f("core_observation", "backend_id", "TEXT", "yes", "future_dimension_key", "Backend placeholder.", "future dim_backend(backend_id)", "Future dimension skeleton.", "Future FK only."),
        f("core_observation", "time_context_id", "TEXT", "yes", "future_dimension_key", "Time-context placeholder.", "future dim_time_context(time_context_id)", "Future dimension skeleton.", "Future FK only."),
        f("core_observation", "processing_context_id", "TEXT", "yes", "future_dimension_key", "Processing-context placeholder.", "future dim_processing_context(processing_context_id)", "Future dimension skeleton.", "Future FK only."),
        f("core_observation", "quality_status_id", "TEXT", "yes", "future_dimension_key", "Quality-status placeholder.", "future dim_quality_status(quality_status_id)", "Future dimension skeleton.", "Future FK only."),
        f("core_observation", "observation_label", "TEXT", "yes", "descriptor", "Human-readable observation label.", "", "Future observation migration.", "Optional."),
        f("core_observation", "observation_status", "TEXT", "no", "status", "Observation lifecycle status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("core_observation", "created_at_utc", "TEXT", "no", "audit_timestamp", "UTC creation timestamp.", "", "Future migration run timestamp.", "NOT NULL."),
        f("core_observation", "updated_at_utc", "TEXT", "yes", "audit_timestamp", "UTC update timestamp.", "", "Future migration/update run timestamp.", "Optional."),
        f("raw_source_file", "raw_source_file_id", "TEXT", "no", "primary_key", "Stable raw source file identifier.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("raw_source_file", "source_registry_id", "TEXT", "yes", "foreign_key", "Source registry associated with the file.", "core_source_registry(source_registry_id)", "Future source/file migration.", "Declared nullable FK."),
        f("raw_source_file", "dataset_id", "TEXT", "yes", "foreign_key", "Dataset associated with the file.", "core_dataset(dataset_id)", "Future source/file migration.", "Declared nullable FK."),
        f("raw_source_file", "source_path", "TEXT", "yes", "lineage_attribute", "Source path or URI reference.", "", "Future raw/source inventory mapping.", "Reference only."),
        f("raw_source_file", "source_filename", "TEXT", "no", "descriptor", "Source filename.", "", "Future raw/source inventory mapping.", "NOT NULL."),
        f("raw_source_file", "source_format", "TEXT", "yes", "classification", "Source format label.", "", "Future controlled vocabulary.", "Optional."),
        f("raw_source_file", "checksum_sha256", "TEXT", "yes", "lineage_attribute", "Payload checksum.", "", "Future manifest/checksum mapping.", "Optional."),
        f("raw_source_file", "size_bytes", "INTEGER", "yes", "lineage_attribute", "Payload size in bytes.", "", "Future source inventory mapping.", "Optional."),
        f("raw_source_file", "ingest_status", "TEXT", "no", "status", "Ingest lifecycle status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("raw_source_file", "created_at_utc", "TEXT", "no", "audit_timestamp", "UTC creation timestamp.", "", "Future migration run timestamp.", "NOT NULL."),
        f("raw_ingest_run", "ingest_run_id", "TEXT", "no", "primary_key", "Stable raw ingest run identifier.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("raw_ingest_run", "raw_source_file_id", "TEXT", "no", "foreign_key", "Source file ingested by the run.", "raw_source_file(raw_source_file_id)", "Future ingest/run mapping.", "Declared FK."),
        f("raw_ingest_run", "script_id", "TEXT", "yes", "future_audit_key", "Script placeholder.", "future audit_script(script_id)", "Future audit skeleton.", "Future FK only."),
        f("raw_ingest_run", "run_timestamp_utc", "TEXT", "no", "audit_timestamp", "UTC ingest run timestamp.", "", "Future ingest/run mapping.", "NOT NULL."),
        f("raw_ingest_run", "ingest_mode", "TEXT", "no", "classification", "Ingest mode.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("raw_ingest_run", "record_count", "INTEGER", "yes", "measure_count", "Record count from ingest.", "", "Future migration/run metadata.", "Optional."),
        f("raw_ingest_run", "field_value_count", "INTEGER", "yes", "measure_count", "Field value count from ingest.", "", "Future migration/run metadata.", "Optional."),
        f("raw_ingest_run", "status", "TEXT", "no", "status", "Ingest run status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("raw_ingest_run", "notes", "TEXT", "yes", "note", "Ingest run note.", "", "Future migration/run note.", "No scientific claim."),
        f("raw_record", "raw_record_id", "TEXT", "no", "primary_key", "Stable raw record identifier.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("raw_record", "ingest_run_id", "TEXT", "no", "foreign_key", "Ingest run that produced the record.", "raw_ingest_run(ingest_run_id)", "Future raw record migration.", "Declared FK."),
        f("raw_record", "raw_source_file_id", "TEXT", "no", "foreign_key", "Source file containing the record.", "raw_source_file(raw_source_file_id)", "Future raw record migration.", "Declared FK."),
        f("raw_record", "record_index", "INTEGER", "no", "lineage_attribute", "Source-local record order.", "", "Future raw record migration.", "NOT NULL."),
        f("raw_record", "raw_line_text", "TEXT", "yes", "raw_value", "Raw line text or reference text.", "", "Future raw record migration.", "No semantic assignment."),
        f("raw_record", "line_type", "TEXT", "yes", "classification", "Source-local line type.", "", "Future mapping/review.", "Optional."),
        f("raw_record", "token_count", "INTEGER", "yes", "measure_count", "Token count from raw parsing.", "", "Future raw record migration.", "Optional."),
        f("raw_record", "lineage_key", "TEXT", "yes", "lineage_attribute", "Composite lineage key.", "", "Future raw record migration.", "Preserve source-local lineage."),
        f("raw_record", "record_status", "TEXT", "no", "status", "Raw record lifecycle status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("raw_record", "created_at_utc", "TEXT", "no", "audit_timestamp", "UTC creation timestamp.", "", "Future migration run timestamp.", "NOT NULL."),
        f("raw_field_value", "raw_field_value_id", "TEXT", "no", "primary_key", "Stable raw field value identifier.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("raw_field_value", "raw_record_id", "TEXT", "no", "foreign_key", "Raw record containing the field value.", "raw_record(raw_record_id)", "Future raw field migration.", "Declared FK."),
        f("raw_field_value", "token_position", "TEXT", "yes", "lineage_attribute", "Source-local token position.", "", "Future token migration.", "TEXT per DWH03 requirement."),
        f("raw_field_value", "field_name", "TEXT", "yes", "lineage_attribute", "Source-local field name.", "", "Future token migration.", "Optional."),
        f("raw_field_value", "raw_value", "TEXT", "yes", "raw_value", "Raw value text.", "", "Future token migration.", "No canonicalization."),
        f("raw_field_value", "value_type_guess", "TEXT", "yes", "classification", "Non-binding type guess.", "", "Future parser hint.", "Hint only."),
        f("raw_field_value", "lineage_key", "TEXT", "yes", "lineage_attribute", "Composite lineage key.", "", "Future raw field migration.", "Preserve source-local lineage."),
        f("raw_field_value", "field_status", "TEXT", "no", "status", "Field value lifecycle status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("raw_field_value", "created_at_utc", "TEXT", "no", "audit_timestamp", "UTC creation timestamp.", "", "Future migration run timestamp.", "NOT NULL."),
        f("core_observation_record_link", "observation_record_link_id", "TEXT", "no", "primary_key", "Stable observation-record link identifier.", "", "Future DWH migration generated ID.", "Skeleton only."),
        f("core_observation_record_link", "observation_id", "TEXT", "no", "foreign_key", "Observation anchor.", "core_observation(observation_id)", "Future observation/raw linking.", "Declared FK."),
        f("core_observation_record_link", "raw_record_id", "TEXT", "no", "foreign_key", "Raw record linked to the observation.", "raw_record(raw_record_id)", "Future observation/raw linking.", "Declared FK."),
        f("core_observation_record_link", "link_status", "TEXT", "no", "status", "Link lifecycle status.", "", "Future controlled vocabulary.", "NOT NULL."),
        f("core_observation_record_link", "mapping_confidence", "TEXT", "yes", "review_status", "Textual mapping confidence/status.", "", "Future mapping/review layer.", "No numeric inference."),
        f("core_observation_record_link", "created_at_utc", "TEXT", "no", "audit_timestamp", "UTC creation timestamp.", "", "Future migration run timestamp.", "NOT NULL."),
    ]


def fk_specs() -> list[FkSpec]:
    f = FkSpec
    return [
        f("core_dataset", "source_registry_id", "core_source_registry", "source_registry_id", "declared_fk", "idx_dwh03_core_dataset_source_registry_id", "Dataset rows must link to a conformed source registry entry.", "02 Core Observation Star", "Mandatory FK."),
        f("core_observation", "dataset_id", "core_dataset", "dataset_id", "declared_fk", "idx_dwh03_core_observation_dataset_id", "Observation rows must link to a dataset.", "02 Core Observation Star", "Mandatory FK."),
        f("raw_source_file", "source_registry_id", "core_source_registry", "source_registry_id", "declared_fk", "idx_dwh03_raw_source_file_source_registry_id", "Raw source files can link to source registry entries.", "01 Raw / Entrance Layer", "Nullable FK."),
        f("raw_source_file", "dataset_id", "core_dataset", "dataset_id", "declared_fk", "idx_dwh03_raw_source_file_dataset_id", "Raw source files can link to datasets.", "01 Raw / Entrance Layer", "Nullable FK."),
        f("raw_ingest_run", "raw_source_file_id", "raw_source_file", "raw_source_file_id", "declared_fk", "idx_dwh03_raw_ingest_run_raw_source_file_id", "Ingest runs must link to a raw source file.", "01 Raw / Entrance Layer", "Mandatory FK."),
        f("raw_record", "ingest_run_id", "raw_ingest_run", "ingest_run_id", "declared_fk", "idx_dwh03_raw_record_ingest_run_id", "Raw records must link to an ingest run.", "01 Raw / Entrance Layer", "Mandatory FK."),
        f("raw_record", "raw_source_file_id", "raw_source_file", "raw_source_file_id", "declared_fk", "idx_dwh03_raw_record_raw_source_file_id", "Raw records must link to a raw source file.", "01 Raw / Entrance Layer", "Mandatory FK."),
        f("raw_field_value", "raw_record_id", "raw_record", "raw_record_id", "declared_fk", "idx_dwh03_raw_field_value_raw_record_id", "Raw field values must link to raw records.", "01 Raw / Entrance Layer", "Mandatory FK."),
        f("raw_field_value", "token_position", "", "", "lookup_index_only", "idx_dwh03_raw_field_value_token_position", "Token-position lookup for future mapping dry-runs.", "04 Token Mapping / Evidence Layer", "Index only; no FK."),
        f("core_observation_record_link", "observation_id", "core_observation", "observation_id", "declared_fk", "idx_dwh03_core_observation_record_link_observation_id", "Observation-record links must link to observation anchors.", "02 Core Observation Star", "Mandatory FK."),
        f("core_observation_record_link", "raw_record_id", "raw_record", "raw_record_id", "declared_fk", "idx_dwh03_core_observation_record_link_raw_record_id", "Observation-record links must link to raw records.", "02 Core Observation Star", "Mandatory FK."),
        f("core_observation", "telescope_id", "dim_telescope", "telescope_id", "future_fk_placeholder", "", "Observation telescope context waits for dimension skeleton.", "03 Instrument / Time / Processing Snowflake", "Plain TEXT in DWH03."),
        f("core_observation", "receiver_id", "dim_receiver", "receiver_id", "future_fk_placeholder", "", "Observation receiver context waits for dimension skeleton.", "03 Instrument / Time / Processing Snowflake", "Plain TEXT in DWH03."),
        f("core_observation", "backend_id", "dim_backend", "backend_id", "future_fk_placeholder", "", "Observation backend context waits for dimension skeleton.", "03 Instrument / Time / Processing Snowflake", "Plain TEXT in DWH03."),
        f("core_observation", "time_context_id", "dim_time_context", "time_context_id", "future_fk_placeholder", "", "Observation time context waits for dimension skeleton.", "03 Instrument / Time / Processing Snowflake", "Plain TEXT in DWH03."),
        f("core_observation", "processing_context_id", "dim_processing_context", "processing_context_id", "future_fk_placeholder", "", "Observation processing context waits for dimension skeleton.", "03 Instrument / Time / Processing Snowflake", "Plain TEXT in DWH03."),
        f("core_observation", "quality_status_id", "dim_quality_status", "quality_status_id", "future_fk_placeholder", "", "Observation quality status waits for dimension skeleton.", "03 Instrument / Time / Processing Snowflake", "Plain TEXT in DWH03."),
    ]


def ddl_statements() -> list[str]:
    return [
        """
CREATE TABLE dwh03_workcopy_run_log (
    run_id TEXT PRIMARY KEY,
    run_timestamp_utc TEXT,
    live_db_path TEXT,
    workcopy_db_path TEXT,
    script_name TEXT,
    operation_mode TEXT,
    live_db_modified INTEGER,
    workcopy_db_modified INTEGER,
    created_table_count INTEGER,
    created_index_count INTEGER,
    integrity_check_result TEXT,
    foreign_key_violation_count INTEGER,
    notes TEXT,
    CHECK (live_db_modified IN (0, 1)),
    CHECK (workcopy_db_modified IN (0, 1))
)""",
        """
CREATE TABLE core_source_registry (
    source_registry_id TEXT PRIMARY KEY,
    source_name TEXT NOT NULL,
    institution TEXT,
    source_type TEXT NOT NULL,
    official_url TEXT,
    citation_note TEXT,
    license_note TEXT,
    retrieval_status TEXT NOT NULL,
    source_status TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT
)""",
        """
CREATE TABLE core_dataset (
    dataset_id TEXT PRIMARY KEY,
    source_registry_id TEXT NOT NULL REFERENCES core_source_registry(source_registry_id),
    dataset_name TEXT NOT NULL,
    dataset_version TEXT,
    release_label TEXT,
    dataset_type TEXT,
    object_id TEXT,
    dataset_status TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT
)""",
        """
CREATE TABLE core_observation (
    observation_id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL REFERENCES core_dataset(dataset_id),
    object_id TEXT,
    telescope_id TEXT,
    receiver_id TEXT,
    backend_id TEXT,
    time_context_id TEXT,
    processing_context_id TEXT,
    quality_status_id TEXT,
    observation_label TEXT,
    observation_status TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    updated_at_utc TEXT
)""",
        """
CREATE TABLE raw_source_file (
    raw_source_file_id TEXT PRIMARY KEY,
    source_registry_id TEXT REFERENCES core_source_registry(source_registry_id),
    dataset_id TEXT REFERENCES core_dataset(dataset_id),
    source_path TEXT,
    source_filename TEXT NOT NULL,
    source_format TEXT,
    checksum_sha256 TEXT,
    size_bytes INTEGER,
    ingest_status TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
)""",
        """
CREATE TABLE raw_ingest_run (
    ingest_run_id TEXT PRIMARY KEY,
    raw_source_file_id TEXT NOT NULL REFERENCES raw_source_file(raw_source_file_id),
    script_id TEXT,
    run_timestamp_utc TEXT NOT NULL,
    ingest_mode TEXT NOT NULL,
    record_count INTEGER,
    field_value_count INTEGER,
    status TEXT NOT NULL,
    notes TEXT
)""",
        """
CREATE TABLE raw_record (
    raw_record_id TEXT PRIMARY KEY,
    ingest_run_id TEXT NOT NULL REFERENCES raw_ingest_run(ingest_run_id),
    raw_source_file_id TEXT NOT NULL REFERENCES raw_source_file(raw_source_file_id),
    record_index INTEGER NOT NULL,
    raw_line_text TEXT,
    line_type TEXT,
    token_count INTEGER,
    lineage_key TEXT,
    record_status TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
)""",
        """
CREATE TABLE raw_field_value (
    raw_field_value_id TEXT PRIMARY KEY,
    raw_record_id TEXT NOT NULL REFERENCES raw_record(raw_record_id),
    token_position TEXT,
    field_name TEXT,
    raw_value TEXT,
    value_type_guess TEXT,
    lineage_key TEXT,
    field_status TEXT NOT NULL,
    created_at_utc TEXT NOT NULL
)""",
        """
CREATE TABLE core_observation_record_link (
    observation_record_link_id TEXT PRIMARY KEY,
    observation_id TEXT NOT NULL REFERENCES core_observation(observation_id),
    raw_record_id TEXT NOT NULL REFERENCES raw_record(raw_record_id),
    link_status TEXT NOT NULL,
    mapping_confidence TEXT,
    created_at_utc TEXT NOT NULL
)""",
    ]


def index_statements() -> list[str]:
    return [
        "CREATE INDEX idx_dwh03_core_dataset_source_registry_id ON core_dataset(source_registry_id)",
        "CREATE INDEX idx_dwh03_core_observation_dataset_id ON core_observation(dataset_id)",
        "CREATE INDEX idx_dwh03_raw_source_file_source_registry_id ON raw_source_file(source_registry_id)",
        "CREATE INDEX idx_dwh03_raw_source_file_dataset_id ON raw_source_file(dataset_id)",
        "CREATE INDEX idx_dwh03_raw_ingest_run_raw_source_file_id ON raw_ingest_run(raw_source_file_id)",
        "CREATE INDEX idx_dwh03_raw_record_ingest_run_id ON raw_record(ingest_run_id)",
        "CREATE INDEX idx_dwh03_raw_record_raw_source_file_id ON raw_record(raw_source_file_id)",
        "CREATE INDEX idx_dwh03_raw_field_value_raw_record_id ON raw_field_value(raw_record_id)",
        "CREATE INDEX idx_dwh03_raw_field_value_token_position ON raw_field_value(token_position)",
        "CREATE INDEX idx_dwh03_core_observation_record_link_observation_id ON core_observation_record_link(observation_id)",
        "CREATE INDEX idx_dwh03_core_observation_record_link_raw_record_id ON core_observation_record_link(raw_record_id)",
    ]


def render_ddl_file() -> str:
    lines = [
        "-- QSB-DWH03 Raw/Core skeleton DDL for workcopy DB only.",
        "-- No legacy data migration is performed by this DDL.",
        "PRAGMA foreign_keys = ON;",
        "",
    ]
    for statement in ddl_statements():
        lines.append(statement.strip() + ";")
        lines.append("")
    for statement in index_statements():
        lines.append(statement + ";")
    lines.append("")
    return "\n".join(lines)


def create_workcopy_schema(con: sqlite3.Connection) -> None:
    for statement in ddl_statements():
        con.execute(statement)
    for statement in index_statements():
        con.execute(statement)


def insert_run_log(
    con: sqlite3.Connection,
    run_id: str,
    created_at: str,
    live_db: Path,
    workcopy_db: Path,
) -> None:
    con.execute(
        """
        INSERT INTO dwh03_workcopy_run_log (
            run_id,
            run_timestamp_utc,
            live_db_path,
            workcopy_db_path,
            script_name,
            operation_mode,
            live_db_modified,
            workcopy_db_modified,
            created_table_count,
            created_index_count,
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
            "workcopy_raw_core_skeleton",
            0,
            1,
            len(NEW_TABLES),
            len(index_statements()),
            "pending",
            -1,
            "DWH03 workcopy skeleton row inserted; no legacy data migrated.",
        ),
    )


def update_run_log_validation(
    con: sqlite3.Connection,
    run_id: str,
    integrity: str,
    fk_violation_count: int,
) -> None:
    con.execute(
        """
        UPDATE dwh03_workcopy_run_log
        SET integrity_check_result = ?,
            foreign_key_violation_count = ?,
            notes = ?
        WHERE run_id = ?
        """,
        (
            integrity,
            fk_violation_count,
            "DWH03 workcopy validation passed; skeleton tables remain empty.",
            run_id,
        ),
    )


def inspect_fks(con: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for table in NEW_TABLES:
        rows = con.execute(f"PRAGMA foreign_key_list({quote_identifier(table)})").fetchall()
        result[table] = [dict(row) for row in rows]
    return result


def inspect_indexes(con: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for table in NEW_TABLES:
        rows = con.execute(f"PRAGMA index_list({quote_identifier(table)})").fetchall()
        result[table] = [dict(row) for row in rows]
    return result


def validation_rows(
    live_db: Path,
    workcopy_db: Path,
    live_sha_before: str,
    live_sha_after: str,
    live_validation: dict[str, Any],
    workcopy_validation: dict[str, Any],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    def add(name: str, scope: str, expected: str, actual: str, status: str, notes: str) -> None:
        rows.append(
            {
                "check_name": name,
                "check_scope": scope,
                "expected_result": expected,
                "actual_result": actual,
                "status": status,
                "notes": notes,
            }
        )

    add("live_db_integrity_check", str(live_db), "ok", live_validation["integrity"], "passed" if live_validation["integrity"] == "ok" else "failed", "Live DB opened read-only.")
    add("live_db_foreign_key_check", str(live_db), "0", str(live_validation["fk_violation_count"]), "passed" if live_validation["fk_violation_count"] == 0 else "failed", "Live DB opened read-only.")
    add("live_db_checksum_unchanged", str(live_db), live_sha_before, live_sha_after, "passed" if live_sha_before == live_sha_after else "failed", "Confirms DWH03 did not modify the live DB file.")
    add("workcopy_db_exists", str(workcopy_db), "exists", "exists" if workcopy_db.exists() else "missing", "passed" if workcopy_db.exists() else "failed", "Workcopy is the only DB modified by DWH03.")
    add("workcopy_integrity_check", str(workcopy_db), "ok", workcopy_validation["integrity"], "passed" if workcopy_validation["integrity"] == "ok" else "failed", "Workcopy validation after skeleton DDL.")
    add("workcopy_foreign_key_check", str(workcopy_db), "0", str(workcopy_validation["fk_violation_count"]), "passed" if workcopy_validation["fk_violation_count"] == 0 else "failed", "Workcopy FK validation after skeleton DDL.")
    for table in NEW_TABLES:
        exists = table in workcopy_validation["tables_found"]
        add("workcopy_table_exists", table, "exists", "exists" if exists else "missing", "passed" if exists else "failed", "DWH03 required table existence check.")
    for table, expected in workcopy_validation["expected_counts"].items():
        actual = workcopy_validation["row_counts"].get(table)
        add("workcopy_table_row_count", table, str(expected), str(actual), "passed" if actual == expected else "failed", "Skeleton tables must be empty except the run log.")
    add("workcopy_index_count", str(workcopy_db), str(len(index_statements())), str(workcopy_validation["dwh03_index_count"]), "passed" if workcopy_validation["dwh03_index_count"] == len(index_statements()) else "failed", "Recommended DWH03 indexes.")
    return rows


def validate_workcopy(con: sqlite3.Connection) -> dict[str, Any]:
    integrity = integrity_check(con)
    fk_violations = foreign_key_violations(con)
    tables_found = [
        table for table in NEW_TABLES
        if object_exists(con, table, "table")
    ]
    expected_counts = {
        "dwh03_workcopy_run_log": 1,
        "core_source_registry": 0,
        "core_dataset": 0,
        "core_observation": 0,
        "core_observation_record_link": 0,
        "raw_source_file": 0,
        "raw_ingest_run": 0,
        "raw_record": 0,
        "raw_field_value": 0,
    }
    row_counts = {
        table: row_count(con, table)
        for table in NEW_TABLES
        if object_exists(con, table, "table")
    }
    index_info = inspect_indexes(con)
    dwh03_index_count = sum(
        1
        for rows in index_info.values()
        for row in rows
        if str(row.get("name", "")).startswith("idx_dwh03_")
    )
    return {
        "integrity": integrity,
        "fk_violation_count": len(fk_violations),
        "tables_found": tables_found,
        "expected_counts": expected_counts,
        "row_counts": row_counts,
        "fk_info": inspect_fks(con),
        "index_info": index_info,
        "dwh03_index_count": dwh03_index_count,
    }


def copy_live_to_workcopy(live_db: Path, workcopy_db: Path, overwrite_workcopy: bool) -> None:
    if workcopy_db.exists():
        if not overwrite_workcopy:
            raise FileExistsError(f"Workcopy DB already exists: {workcopy_db}")
        workcopy_db.unlink()
    shutil.copy2(live_db, workcopy_db)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def table_catalog_rows(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = []
    for spec in table_specs():
        actual = row_count(con, spec.table_name)
        rows.append(
            {
                "table_name": spec.table_name,
                "layer": spec.layer,
                "purpose": spec.purpose,
                "grain": spec.grain,
                "primary_key": spec.primary_key,
                "row_count_expected": spec.row_count_expected,
                "row_count_actual": actual,
                "implementation_status": spec.implementation_status,
                "notes": spec.notes,
            }
        )
    return rows


def field_catalog_rows() -> list[dict[str, Any]]:
    return [
        {
            "table_name": spec.table_name,
            "field_name": spec.field_name,
            "field_type": spec.field_type,
            "nullable": spec.nullable,
            "field_role": spec.field_role,
            "field_description": spec.field_description,
            "fk_target": spec.fk_target,
            "source_or_future_mapping_rule": spec.source_or_future_mapping_rule,
            "notes": spec.notes,
        }
        for spec in field_specs()
    ]


def pk_fk_catalog_rows() -> list[dict[str, Any]]:
    return [
        {
            "source_table": spec.source_table,
            "source_field": spec.source_field,
            "target_table": spec.target_table,
            "target_field": spec.target_field,
            "fk_status": spec.fk_status,
            "index_name": spec.index_name,
            "relationship_description": spec.relationship_description,
            "erd_slice": spec.erd_slice,
            "notes": spec.notes,
        }
        for spec in fk_specs()
    ]


def next_migration_questions() -> list[dict[str, str]]:
    return [
        {
            "question_id": "DWH03_Q01",
            "question_rank": "1",
            "question_text": "Should DWH04 export ERD slices before any dry-run data movement?",
            "related_table": "all DWH03 raw/core tables",
            "related_phase": "DWH04 Option C",
            "blocking_status": "recommended_before_data_dry_run",
            "recommended_next_action": "Create ERD export and visually inspect FK readability.",
        },
        {
            "question_id": "DWH03_Q02",
            "question_rank": "2",
            "question_text": "Which source registry rows should seed core_source_registry in a dry-run?",
            "related_table": "core_source_registry",
            "related_phase": "DWH04 Option B",
            "blocking_status": "blocks_raw_core_population_plan",
            "recommended_next_action": "Define source-registry mapping from existing DB objects without reading raw files.",
        },
        {
            "question_id": "DWH03_Q03",
            "question_rank": "3",
            "question_text": "What is the first stable observation anchor rule for core_observation?",
            "related_table": "core_observation",
            "related_phase": "DWH04 Option B",
            "blocking_status": "blocks_observation_migration_dry_run",
            "recommended_next_action": "Specify observation grain and source-local lineage key rules.",
        },
        {
            "question_id": "DWH03_Q04",
            "question_rank": "4",
            "question_text": "Should dimension placeholders become real dimension skeleton tables before raw/core migration?",
            "related_table": "core_observation",
            "related_phase": "DWH04 Option A",
            "blocking_status": "architecture_choice",
            "recommended_next_action": "Decide whether to create dim_* skeletons before dry-run population.",
        },
        {
            "question_id": "DWH03_Q05",
            "question_rank": "5",
            "question_text": "How should qsb_v dependencies be parsed into audit_view_dependency beyond DWH02 seed rows?",
            "related_table": "audit_view_dependency",
            "related_phase": "DWH04 Option D",
            "blocking_status": "needed_for_view_governance",
            "recommended_next_action": "Build a deterministic view dependency parser for sqlite_master SQL.",
        },
    ]


def markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        values = [str(row.get(column, "")).replace("|", "/") for column in columns]
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def render_readout(
    live_db: Path,
    workcopy_db: Path,
    live_validation: dict[str, Any],
    workcopy_validation: dict[str, Any],
    validation_report: list[dict[str, str]],
    live_sha_before: str,
    live_sha_after: str,
) -> str:
    table_rows = [
        {
            "table": table,
            "rows": workcopy_validation["row_counts"].get(table, "missing"),
            "expected": workcopy_validation["expected_counts"].get(table, ""),
        }
        for table in NEW_TABLES
    ]
    index_rows = []
    for table, rows in workcopy_validation["index_info"].items():
        for row in rows:
            name = str(row.get("name", ""))
            if name.startswith("idx_dwh03_"):
                index_rows.append({"table": table, "index": name, "unique": row.get("unique", "")})
    lines = [
        "# QSB-DWH03 Target Schema Workcopy Readout",
        "",
        f"Generated at UTC: {utc_now()}",
        f"Script: `{SCRIPT_NAME}`",
        f"Live DB: `{live_db}`",
        f"Workcopy DB: `{workcopy_db}`",
        "",
        "## 1. Executive summary",
        "",
        (
            "DWH03 created a workcopy of the live Research DWH and added only "
            "the Raw / Entrance and Core / Observation-centered target skeleton "
            "tables. The new target skeleton tables remain empty; only the "
            "DWH03 workcopy run log contains one row."
        ),
        "",
        "## 2. Workcopy principle",
        "",
        (
            "The workcopy is a target-schema prototype for testing table shape, "
            "FK graph readability, indexes, and future migration planning before "
            "any live target-schema change."
        ),
        "",
        "## 3. Live DB protection",
        "",
        f"Live DB integrity_check: `{live_validation['integrity']}`",
        f"Live DB foreign_key_check count: `{live_validation['fk_violation_count']}`",
        f"Live DB checksum before: `{live_sha_before}`",
        f"Live DB checksum after: `{live_sha_after}`",
        f"Live DB modified by DWH03: `{str(live_sha_before != live_sha_after).lower()}`",
        "",
        "## 4. Tables created in DWH03 workcopy",
        "",
        markdown_table(table_rows, ["table", "rows", "expected"]),
        "",
        "## 5. Raw / Entrance skeleton",
        "",
        "- `raw_source_file`: file-level entrance object with source/dataset references.",
        "- `raw_ingest_run`: ingest-run metadata for one raw source file.",
        "- `raw_record`: source-local raw record/line skeleton.",
        "- `raw_field_value`: raw token/field value skeleton before semantic commitment.",
        "",
        "## 6. Core / Observation skeleton",
        "",
        "- `core_source_registry`: source authority and registry anchor.",
        "- `core_dataset`: dataset/snapshot object linked to source registry.",
        "- `core_observation`: central observation anchor with future dimension placeholders.",
        "- `core_observation_record_link`: explicit observation-to-raw-record link table.",
        "",
        "## 7. FK and index design",
        "",
        (
            f"DWH03 created {workcopy_validation['dwh03_index_count']} DWH03 "
            "indexes for declared FK columns and token-position lookup."
        ),
        "",
        markdown_table(index_rows, ["table", "index", "unique"]) if index_rows else "No DWH03 indexes found.",
        "",
        "## 8. Validation results",
        "",
        f"Workcopy integrity_check: `{workcopy_validation['integrity']}`",
        f"Workcopy foreign_key_check count: `{workcopy_validation['fk_violation_count']}`",
        "",
        markdown_table(validation_report, ["check_name", "check_scope", "expected_result", "actual_result", "status"]),
        "",
        "## 9. ERD expectation",
        "",
        (
            "The expected ERD should show source registry -> dataset -> "
            "observation, source registry/dataset -> raw_source_file -> "
            "raw_ingest_run -> raw_record -> raw_field_value, and the "
            "core_observation_record_link table connecting observations to raw "
            "records. Dimension columns in core_observation should remain visibly "
            "unresolved placeholders until DWH04 or later."
        ),
        "",
        "## 10. What DWH03 does not do",
        "",
        "- It does not modify the live DB.",
        "- It does not migrate data from legacy DBXX tables.",
        "- It does not create dimensions, mapping/evidence, bridge, result, or full audit target tables.",
        "- It does not compute scientific quantities or statistical outputs.",
        "",
        "## 11. Recommended DWH04 options",
        "",
        "- Option A: Dimension skeleton in workcopy.",
        "- Option B: Raw/Core migration dry-run into workcopy with row-count parity.",
        "- Option C: ERD export and visual inspection of workcopy.",
        "- Option D: Full view dependency parser seed expansion.",
        "",
        f"Recommended next option: {RECOMMENDED_DWH04_OPTION}",
        "",
        "## 12. Claim boundary",
        "",
        CLAIM_BOUNDARY,
        "",
    ]
    return "\n".join(lines)


def write_outputs(
    output_root: Path,
    live_db: Path,
    workcopy_db: Path,
    live_validation: dict[str, Any],
    workcopy_validation: dict[str, Any],
    validation_report: list[dict[str, str]],
    table_catalog: list[dict[str, Any]],
    live_sha_before: str,
    live_sha_after: str,
) -> None:
    paths = output_paths(output_root)
    summary = {
        "input_live_db_path": str(live_db),
        "live_db_modified": live_sha_before != live_sha_after,
        "workcopy_db_path": str(workcopy_db),
        "created_tables": NEW_TABLES,
        "created_index_count": workcopy_validation["dwh03_index_count"],
        "live_integrity_check": live_validation["integrity"],
        "live_foreign_key_violation_count": live_validation["fk_violation_count"],
        "workcopy_integrity_check": workcopy_validation["integrity"],
        "workcopy_foreign_key_violation_count": workcopy_validation["fk_violation_count"],
        "new_table_row_counts": workcopy_validation["row_counts"],
        "recommended_dwh04_option": RECOMMENDED_DWH04_OPTION,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    paths[READOUT_MD].write_text(
        render_readout(
            live_db,
            workcopy_db,
            live_validation,
            workcopy_validation,
            validation_report,
            live_sha_before,
            live_sha_after,
        ),
        encoding="utf-8",
    )
    paths[SUMMARY_JSON].write_text(pretty_json(summary) + "\n", encoding="utf-8")
    paths[DDL_SQL].write_text(render_ddl_file(), encoding="utf-8")
    write_csv(
        paths[TABLE_CATALOG_CSV],
        [
            "table_name",
            "layer",
            "purpose",
            "grain",
            "primary_key",
            "row_count_expected",
            "row_count_actual",
            "implementation_status",
            "notes",
        ],
        table_catalog,
    )
    write_csv(
        paths[FIELD_CATALOG_CSV],
        [
            "table_name",
            "field_name",
            "field_type",
            "nullable",
            "field_role",
            "field_description",
            "fk_target",
            "source_or_future_mapping_rule",
            "notes",
        ],
        field_catalog_rows(),
    )
    write_csv(
        paths[PK_FK_CATALOG_CSV],
        [
            "source_table",
            "source_field",
            "target_table",
            "target_field",
            "fk_status",
            "index_name",
            "relationship_description",
            "erd_slice",
            "notes",
        ],
        pk_fk_catalog_rows(),
    )
    write_csv(
        paths[VALIDATION_CSV],
        [
            "check_name",
            "check_scope",
            "expected_result",
            "actual_result",
            "status",
            "notes",
        ],
        validation_report,
    )
    write_csv(
        paths[NEXT_QUESTIONS_CSV],
        [
            "question_id",
            "question_rank",
            "question_text",
            "related_table",
            "related_phase",
            "blocking_status",
            "recommended_next_action",
        ],
        next_migration_questions(),
    )


def execute(args: argparse.Namespace) -> int:
    live_db = Path(args.db)
    output_root = Path(args.output_root)
    workcopy_db = Path(args.workcopy_db)
    preflight = ensure_preconditions(
        live_db=live_db,
        output_root=output_root,
        workcopy_db=workcopy_db,
        overwrite=args.overwrite,
        overwrite_workcopy=args.overwrite_workcopy,
    )
    live_sha_before = file_sha256(live_db)
    copy_live_to_workcopy(live_db, workcopy_db, args.overwrite_workcopy)
    run_id = f"DWH03_WORKCOPY_RAW_CORE_SKELETON_{timestamp_for_id()}"
    created_at = utc_now()

    with connect_writable(workcopy_db) as con:
        con.execute("BEGIN")
        try:
            create_workcopy_schema(con)
            insert_run_log(con, run_id, created_at, live_db, workcopy_db)
            workcopy_validation = validate_workcopy(con)
            if (
                workcopy_validation["integrity"] != "ok"
                or workcopy_validation["fk_violation_count"] != 0
                or set(workcopy_validation["tables_found"]) != set(NEW_TABLES)
            ):
                raise RuntimeError("Workcopy validation failed before commit.")
            update_run_log_validation(
                con,
                run_id,
                workcopy_validation["integrity"],
                workcopy_validation["fk_violation_count"],
            )
            workcopy_validation = validate_workcopy(con)
            table_catalog = table_catalog_rows(con)
            con.commit()
        except Exception:
            con.rollback()
            raise

    live_sha_after = file_sha256(live_db)
    with connect_readonly(live_db) as live_con:
        live_validation = {
            "integrity": integrity_check(live_con),
            "fk_violation_count": len(foreign_key_violations(live_con)),
            "dwh02_dashboard_row_count": preflight["dwh02_dashboard_row_count"],
        }
    with connect_readonly(workcopy_db) as work_con:
        workcopy_validation = validate_workcopy(work_con)
    validation_report = validation_rows(
        live_db,
        workcopy_db,
        live_sha_before,
        live_sha_after,
        live_validation,
        workcopy_validation,
    )
    if any(row["status"] != "passed" for row in validation_report):
        raise RuntimeError("DWH03 validation report contains failed checks.")
    write_outputs(
        output_root,
        live_db,
        workcopy_db,
        live_validation,
        workcopy_validation,
        validation_report,
        table_catalog,
        live_sha_before,
        live_sha_after,
    )

    print(f"Live DB: {live_db}")
    print(f"Live DB modified: {live_sha_before != live_sha_after}")
    print(f"Workcopy DB: {workcopy_db}")
    print(f"Created tables in workcopy: {len(NEW_TABLES)}")
    print(f"Created indexes in workcopy: {workcopy_validation['dwh03_index_count']}")
    print(f"Live integrity_check: {live_validation['integrity']}")
    print(f"Live FK violations: {live_validation['fk_violation_count']}")
    print(f"Workcopy integrity_check: {workcopy_validation['integrity']}")
    print(f"Workcopy FK violations: {workcopy_validation['fk_violation_count']}")
    print(f"Wrote {len(OUTPUT_FILENAMES)} DWH03 output files to {output_root}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a DWH03 workcopy of the live QSB Research DB and add the "
            "raw/core target skeleton tables only to that workcopy."
        )
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to live consolidated Research DB.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Directory for DWH03 report outputs.")
    parser.add_argument("--workcopy-db", default=str(DEFAULT_WORKCOPY_DB), help="Path for the DWH03 workcopy DB.")
    parser.add_argument("--overwrite", action="store_true", help="Allow controlled regeneration of DWH03 report outputs only.")
    parser.add_argument("--overwrite-workcopy", action="store_true", help="Allow controlled replacement of the DWH03 workcopy DB.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        return execute(parse_args(sys.argv[1:] if argv is None else argv))
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
