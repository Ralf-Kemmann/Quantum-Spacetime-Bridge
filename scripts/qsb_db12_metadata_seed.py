#!/usr/bin/env python3
"""QSB-DB12 metadata-only seed script.

This script later creates a metadata-seeded SQLite research database by copying
the empty baseline database and inserting project/control metadata only.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INPUT_DB = Path("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db")
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB13_METADATA_SEED")
DEFAULT_OUTPUT_DB_NAME = "qsb_research_metadata_seed.db"
SCRIPT_PATH = "scripts/qsb_db12_metadata_seed.py"

CLAIM_BOUNDARY_PARTS = [
    "This output does not provide evidence for a physical Shapiro-information residual.",
    "This output does not validate the QSB-ST Bridge.",
    "This output does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, molecular-structure, or C60 physics claims.",
    "No raw artifact contents were inspected.",
    "No TIM/PAR values were read.",
    "No documentation or data files were downloaded.",
    "Metadata seed rows do not authorize physical interpretation.",
]
CLAIM_BOUNDARY = " ".join(CLAIM_BOUNDARY_PARTS)

KNOWN_COMMITS = [
    ("fd01ea7", "Add QSB SQLite DB Browser inspection result note"),
    ("fab3bbf", "Add QSB SQLite DB Browser inspection plan"),
    ("71a9c9c", "Add QSB SQLite empty database inspection result note"),
    ("86c32ca", "Add QSB empty SQLite database creation script"),
    ("1b515b6", "Add QSB SQLite empty database creation plan"),
    ("7b52119", "Add QSB SQLite research database schema SQL"),
    ("32bc8be", "Add QSB SQLite research database schema spec"),
    ("0a38fa5", "Add QSB research database repo lineage schema plan"),
    ("641b35f", "Add QSB-ST ShapiroInfo ETL harmonization method correction"),
    ("4deac54", "Add QSB metadata seed specification"),
    ("070b86d", "Add QSB metadata seed plan"),
]

PROJECT_FILES = [
    (
        "docs/QSB_DB01_RESEARCH_DATABASE_REPO_LINEAGE_SCHEMA_PLAN.md",
        "plan",
        "documentation_note",
        "QSB-DB01",
    ),
    ("docs/QSB_DB02_SQLITE_SCHEMA_SPEC.md", "spec", "documentation_note", "QSB-DB02"),
    ("data/QSB-DB/schema/qsb_research_db_schema.sql", "sql", "schema", "QSB-DB03"),
    (
        "docs/QSB_DB04_SQLITE_EMPTY_DATABASE_CREATION_PLAN.md",
        "plan",
        "documentation_note",
        "QSB-DB04",
    ),
    ("scripts/qsb_db05_create_empty_sqlite_database.py", "python", "script", "QSB-DB05"),
    (
        "docs/QSB_DB07_SQLITE_SCHEMA_INSPECTION_RESULT_NOTE.md",
        "result_note",
        "documentation_note",
        "QSB-DB07",
    ),
    (
        "docs/QSB_DB08_SQLITE_DB_BROWSER_INSPECTION_PLAN.md",
        "plan",
        "documentation_note",
        "QSB-DB08",
    ),
    (
        "docs/QSB_DB09_SQLITE_DB_BROWSER_INSPECTION_EXECUTION_NOTE.md",
        "result_note",
        "documentation_note",
        "QSB-DB09",
    ),
    ("docs/QSB_DB10_METADATA_SEED_PLAN.md", "plan", "documentation_note", "QSB-DB10"),
    ("docs/QSB_DB11_METADATA_SEED_SPEC.md", "spec", "documentation_note", "QSB-DB11"),
    (
        "docs/QSB_ST_SHAPIROINFO74_METHOD_CORRECTION_ETL_HARMONIZATION_AND_TRANSFORMATION_VIEW_DECISION.md",
        "decision_note",
        "documentation_note",
        "SHAPIROINFO74",
    ),
    ("scripts/qsb_db12_metadata_seed.py", "python", "script", "QSB-DB12"),
]

DOCUMENTS = [
    (
        "QSB-DB01 schema plan",
        "plan",
        "QSB-DB01",
        "docs/QSB_DB01_RESEARCH_DATABASE_REPO_LINEAGE_SCHEMA_PLAN.md",
    ),
    (
        "QSB-DB02 SQLite schema specification",
        "spec",
        "QSB-DB02",
        "docs/QSB_DB02_SQLITE_SCHEMA_SPEC.md",
    ),
    (
        "QSB-DB04 empty database creation plan",
        "plan",
        "QSB-DB04",
        "docs/QSB_DB04_SQLITE_EMPTY_DATABASE_CREATION_PLAN.md",
    ),
    (
        "QSB-DB07 schema inspection result note",
        "result_note",
        "QSB-DB07",
        "docs/QSB_DB07_SQLITE_SCHEMA_INSPECTION_RESULT_NOTE.md",
    ),
    (
        "QSB-DB08 DB Browser inspection plan",
        "plan",
        "QSB-DB08",
        "docs/QSB_DB08_SQLITE_DB_BROWSER_INSPECTION_PLAN.md",
    ),
    (
        "QSB-DB09 DB Browser inspection execution note",
        "result_note",
        "QSB-DB09",
        "docs/QSB_DB09_SQLITE_DB_BROWSER_INSPECTION_EXECUTION_NOTE.md",
    ),
    (
        "QSB-DB10 metadata seed plan",
        "plan",
        "QSB-DB10",
        "docs/QSB_DB10_METADATA_SEED_PLAN.md",
    ),
    (
        "QSB-DB11 metadata seed specification",
        "spec",
        "QSB-DB11",
        "docs/QSB_DB11_METADATA_SEED_SPEC.md",
    ),
    (
        "SHAPIROINFO74 ETL harmonization method correction",
        "decision_note",
        "SHAPIROINFO74",
        "docs/QSB_ST_SHAPIROINFO74_METHOD_CORRECTION_ETL_HARMONIZATION_AND_TRANSFORMATION_VIEW_DECISION.md",
    ),
]

SCHEMA_TABLES = [
    "raw_data_source",
    "raw_data",
    "pk_fk_relation_catalog",
    "repo_catalog",
    "git_commit_catalog",
    "project_file_catalog",
    "document_catalog",
    "script_catalog",
    "run_catalog",
    "run_output_catalog",
    "table_catalog",
    "script_table_relation",
    "document_table_relation",
    "field_catalog",
    "raw_token_catalog",
    "etl_transformation_rule",
    "harmonized_value_view_catalog",
    "unit_dimension_catalog",
    "quantity_domain_catalog",
    "quantity_catalog",
    "transformation_rule_catalog",
    "audit_log",
    "quality_check_catalog",
    "quality_check_result",
    "claim_boundary_catalog",
]

DB06_OUTPUTS = [
    ("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db", "sqlite_database"),
    ("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_config_resolved.json", "json_config"),
    ("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_creation_summary.json", "json_summary"),
    ("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_fk_report.csv", "csv_fk_report"),
    ("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_readout.md", "markdown_readout"),
    ("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_schema_indexes.csv", "csv_index_inventory"),
    ("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_schema_tables.csv", "csv_table_inventory"),
]

FK_RELATIONS = [
    ("raw_data", "raw_data_source_id", "raw_data_source", "raw_data_source_id"),
    ("git_commit_catalog", "repo_id", "repo_catalog", "repo_id"),
    ("project_file_catalog", "repo_id", "repo_catalog", "repo_id"),
    ("project_file_catalog", "commit_id", "git_commit_catalog", "commit_id"),
    ("document_catalog", "project_file_id", "project_file_catalog", "project_file_id"),
    ("script_catalog", "project_file_id", "project_file_catalog", "project_file_id"),
    ("run_catalog", "script_id", "script_catalog", "script_id"),
    ("run_catalog", "repo_id", "repo_catalog", "repo_id"),
    ("run_catalog", "commit_id", "git_commit_catalog", "commit_id"),
    ("run_output_catalog", "run_id", "run_catalog", "run_id"),
    ("run_output_catalog", "project_file_id", "project_file_catalog", "project_file_id"),
    ("table_catalog", "created_by_script_id", "script_catalog", "script_id"),
    ("table_catalog", "created_by_run_id", "run_catalog", "run_id"),
    ("table_catalog", "source_raw_data_id", "raw_data", "raw_data_id"),
    ("script_table_relation", "script_id", "script_catalog", "script_id"),
    ("script_table_relation", "table_id", "table_catalog", "table_id"),
    ("script_table_relation", "run_id", "run_catalog", "run_id"),
    ("script_table_relation", "commit_id", "git_commit_catalog", "commit_id"),
    ("document_table_relation", "document_id", "document_catalog", "document_id"),
    ("document_table_relation", "table_id", "table_catalog", "table_id"),
    ("field_catalog", "table_id", "table_catalog", "table_id"),
    ("field_catalog", "raw_data_id", "raw_data", "raw_data_id"),
    ("raw_token_catalog", "raw_data_id", "raw_data", "raw_data_id"),
    ("raw_token_catalog", "field_id", "field_catalog", "field_id"),
    ("etl_transformation_rule", "source_field_id", "field_catalog", "field_id"),
    ("harmonized_value_view_catalog", "created_by_run_id", "run_catalog", "run_id"),
    ("quantity_catalog", "quantity_domain_id", "quantity_domain_catalog", "quantity_domain_id"),
    ("transformation_rule_catalog", "target_quantity_id", "quantity_catalog", "quantity_id"),
    ("quality_check_result", "quality_check_id", "quality_check_catalog", "quality_check_id"),
    ("quality_check_result", "raw_data_id", "raw_data", "raw_data_id"),
    ("quality_check_result", "table_id", "table_catalog", "table_id"),
    ("quality_check_result", "run_id", "run_catalog", "run_id"),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a metadata-only QSB research SQLite database by copying "
            "the empty baseline DB and inserting infrastructure metadata."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help=f"Empty baseline DB path. Default: {DEFAULT_INPUT_DB}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Output root. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--output-db",
        type=Path,
        default=None,
        help=f"Output DB path. Default: <output-root>/{DEFAULT_OUTPUT_DB_NAME}",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only the output DB path if it already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned seed tables and output paths without creating files.",
    )
    return parser.parse_args()


def resolve_output_db(output_root: Path, output_db: Path | None) -> Path:
    if output_db is not None:
        return output_db
    return output_root / DEFAULT_OUTPUT_DB_NAME


def run_dry_run(input_db: Path, output_root: Path, output_db: Path) -> int:
    if not input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {input_db}")
    print("dry_run: true")
    print(f"input_db: {input_db}")
    print(f"output_root: {output_root}")
    print(f"output_db: {output_db}")
    print("planned_seed_tables:")
    for table in [
        "repo_catalog",
        "git_commit_catalog",
        "project_file_catalog",
        "document_catalog",
        "script_catalog",
        "run_catalog",
        "run_output_catalog",
        "table_catalog",
        "script_table_relation",
        "document_table_relation",
        "pk_fk_relation_catalog",
        "claim_boundary_catalog",
        "raw_data_source",
    ]:
        print(f"- {table}")
    print("raw_data_seed_inserted: false")
    print("seed_data_inserted: false")
    return 0


def insert_row(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> int:
    columns = list(values)
    placeholders = ", ".join(["?"] * len(columns))
    quoted = ", ".join(columns)
    sql = f"INSERT INTO {table} ({quoted}) VALUES ({placeholders})"
    cur = conn.execute(sql, [values[column] for column in columns])
    return int(cur.lastrowid)


def try_git_metadata(short_hash: str) -> dict[str, str]:
    try:
        result = subprocess.run(
            [
                "git",
                "show",
                "-s",
                "--format=%H%x1f%an%x1f%ad",
                "--date=iso-strict",
                short_hash,
            ],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.CalledProcessError):
        return {"commit_hash": "unresolved", "commit_author": "unresolved", "commit_date": "unresolved"}
    parts = result.stdout.strip().split("\x1f")
    if len(parts) != 3:
        return {"commit_hash": "unresolved", "commit_author": "unresolved", "commit_date": "unresolved"}
    return {"commit_hash": parts[0], "commit_author": parts[1], "commit_date": parts[2]}


def file_name(path: str) -> str:
    return Path(path).name


def byte_size_if_available(path: str) -> int | None:
    p = Path(path)
    if not p.exists() or not p.is_file():
        return None
    return p.stat().st_size


def seed_metadata(conn: sqlite3.Connection) -> dict[str, int]:
    counts: dict[str, int] = {}

    def bump(table: str, amount: int = 1) -> None:
        counts[table] = counts.get(table, 0) + amount

    repo_id = insert_row(
        conn,
        "repo_catalog",
        {
            "repo_name": "quantum-spacetime-bridge",
            "repo_url": "unresolved",
            "local_root_path": "/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge",
            "default_branch": "unresolved_unless_read_from_git",
            "project_area": "QSB-wide",
            "repo_status": "active",
            "notes": "metadata seed; remote URL and branch are unresolved unless captured from Git in a later gate",
        },
    )
    bump("repo_catalog")

    commit_ids: dict[str, int] = {}
    for short_hash, message in KNOWN_COMMITS:
        git_meta = try_git_metadata(short_hash)
        commit_id = insert_row(
            conn,
            "git_commit_catalog",
            {
                "repo_id": repo_id,
                "commit_hash": git_meta["commit_hash"] if git_meta["commit_hash"] != "unresolved" else short_hash,
                "short_hash": short_hash,
                "commit_message": message,
                "commit_author": git_meta["commit_author"],
                "commit_date": git_meta["commit_date"],
                "branch_name": "unresolved",
                "tag_name": None,
                "is_clean_state": 0,
                "git_status_snapshot": None,
                "notes": "metadata seed; commit metadata captured from local Git when available",
            },
        )
        commit_ids[short_hash] = commit_id
        bump("git_commit_catalog")

    file_ids: dict[str, int] = {}
    for path, file_type, role, block in PROJECT_FILES:
        project_file_id = insert_row(
            conn,
            "project_file_catalog",
            {
                "repo_id": repo_id,
                "commit_id": None,
                "file_path": path,
                "file_name": file_name(path),
                "file_type": file_type,
                "project_role": role,
                "tracking_status": "tracked_or_expected",
                "created_by_block": block,
                "modified_by_block": None,
                "checksum": None,
                "notes": "metadata only; file contents not inserted",
            },
        )
        file_ids[path] = project_file_id
        bump("project_file_catalog")

    document_ids: dict[str, int] = {}
    for title, doc_type, block, path in DOCUMENTS:
        document_id = insert_row(
            conn,
            "document_catalog",
            {
                "project_file_id": file_ids[path],
                "document_title": title,
                "document_type": doc_type,
                "qsb_block_id": block,
                "upstream_block": "metadata_seed_context",
                "downstream_block": "QSB-DB12/QSB-DB13",
                "status": "documented",
                "claim_boundary_level": "infrastructure_metadata_only",
                "tracking_decision": "tracked_documentation",
                "notes": "metadata only; document body text not inserted",
            },
        )
        document_ids[block] = document_id
        bump("document_catalog")

    script_ids: dict[str, int] = {}
    for path, block, purpose in [
        (
            "scripts/qsb_db05_create_empty_sqlite_database.py",
            "QSB-DB05",
            "create empty SQLite research database from schema SQL",
        ),
        (
            "scripts/qsb_db12_metadata_seed.py",
            "QSB-DB12",
            "create metadata-only seeded SQLite research database",
        ),
    ]:
        script_id = insert_row(
            conn,
            "script_catalog",
            {
                "project_file_id": file_ids[path],
                "script_name": file_name(path),
                "script_path": path,
                "script_language": "python",
                "execution_allowed_status": "separately_gated",
                "last_known_commit_hash": "unresolved",
                "purpose": purpose,
                "claim_boundary": "infrastructure metadata only; no physical interpretation",
                "notes": "metadata only; script source code not inserted",
            },
        )
        script_ids[block] = script_id
        bump("script_catalog")

    run_id = insert_row(
        conn,
        "run_catalog",
        {
            "run_block": "QSB-DB06_SQLITE_EMPTY_DATABASE_CREATION_EXECUTION",
            "script_id": script_ids["QSB-DB05"],
            "repo_id": repo_id,
            "commit_id": commit_ids.get("86c32ca"),
            "execution_mode": "empty_database_creation",
            "output_root": "runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/",
            "run_status": "completed",
            "git_status_before": "not_seeded",
            "git_status_after": "not_seeded",
            "raw_access_status": "not_performed",
            "download_status": "not_performed",
            "value_reading_status": "not_performed",
            "claim_boundary_status": "closed",
            "notes": "metadata only; no run output file contents inserted",
        },
    )
    bump("run_catalog")

    for output_path, output_type in DB06_OUTPUTS:
        insert_row(
            conn,
            "run_output_catalog",
            {
                "run_id": run_id,
                "project_file_id": None,
                "output_path": output_path,
                "output_type": output_type,
                "byte_size": byte_size_if_available(output_path),
                "row_count": None,
                "checksum": None,
                "tracked_status": "run_artifact_untracked",
                "notes": "metadata only; output file contents not inserted",
            },
        )
        bump("run_output_catalog")

    table_ids: dict[str, int] = {}
    for table in SCHEMA_TABLES:
        table_id = insert_row(
            conn,
            "table_catalog",
            {
                "table_name": table,
                "table_type": "sqlite_schema_table",
                "storage_type": "sqlite_table",
                "storage_path": "runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db",
                "schema_status": "defined_by_qsb_db03",
                "row_count": None,
                "column_count": None,
                "created_by_script_id": script_ids["QSB-DB05"],
                "created_by_run_id": run_id,
                "source_raw_data_id": None,
                "notes": "schema object metadata only; not scientific table contents",
            },
        )
        table_ids[table] = table_id
        bump("table_catalog")

    script_relations = [
        ("QSB-DB05", "table_catalog", "validates", "validation"),
        ("QSB-DB05", "run_output_catalog", "creates", "summary"),
        ("QSB-DB05", "pk_fk_relation_catalog", "documents", "validation"),
        ("QSB-DB12", "repo_catalog", "creates", "metadata_seed"),
        ("QSB-DB12", "git_commit_catalog", "creates", "metadata_seed"),
        ("QSB-DB12", "project_file_catalog", "creates", "metadata_seed"),
        ("QSB-DB12", "document_catalog", "creates", "metadata_seed"),
        ("QSB-DB12", "script_catalog", "creates", "metadata_seed"),
        ("QSB-DB12", "table_catalog", "creates", "metadata_seed"),
        ("QSB-DB12", "claim_boundary_catalog", "creates", "metadata_seed"),
    ]
    for block, table_name, relation_type, operation_type in script_relations:
        insert_row(
            conn,
            "script_table_relation",
            {
                "script_id": script_ids[block],
                "table_id": table_ids[table_name],
                "relation_type": relation_type,
                "operation_type": operation_type,
                "run_id": run_id if block == "QSB-DB05" else None,
                "commit_id": commit_ids.get("86c32ca") if block == "QSB-DB05" else None,
                "notes": "metadata relationship only",
            },
        )
        bump("script_table_relation")

    doc_relations = [
        ("QSB-DB01", "table_catalog", "specifies"),
        ("QSB-DB02", "raw_data_source", "specifies"),
        ("QSB-DB02", "raw_data", "specifies"),
        ("QSB-DB02", "pk_fk_relation_catalog", "specifies"),
        ("QSB-DB07", "run_output_catalog", "documents"),
        ("QSB-DB10", "repo_catalog", "specifies"),
        ("QSB-DB10", "git_commit_catalog", "specifies"),
        ("QSB-DB10", "project_file_catalog", "specifies"),
        ("QSB-DB10", "claim_boundary_catalog", "specifies"),
        ("QSB-DB11", "script_table_relation", "specifies"),
        ("QSB-DB11", "document_table_relation", "specifies"),
    ]
    for block, table_name, relation_type in doc_relations:
        insert_row(
            conn,
            "document_table_relation",
            {
                "document_id": document_ids[block],
                "table_id": table_ids[table_name],
                "relation_type": relation_type,
                "notes": "documentation-to-table metadata relationship only",
            },
        )
        bump("document_table_relation")

    for source_table, source_column, target_table, target_column in FK_RELATIONS:
        insert_row(
            conn,
            "pk_fk_relation_catalog",
            {
                "source_table": source_table,
                "source_column": source_column,
                "target_table": target_table,
                "target_column": target_column,
                "relation_type": "foreign_key",
                "cardinality": "many_to_one_or_optional",
                "constraint_name": "schema_defined",
                "is_enforced": 1,
                "is_logical_only": 0,
                "join_rule": f"{source_table}.{source_column} -> {target_table}.{target_column}",
                "validity_condition": "QSB-DB03 schema",
                "audit_relevance": "lineage and FK integrity",
                "notes": "relation metadata only; no schema modification",
            },
        )
        bump("pk_fk_relation_catalog")

    for object_type in [
        "database_schema",
        "database_documentation",
        "database_script",
        "empty_database_run_artifact",
        "metadata_seed_artifact",
        "table_catalog_metadata",
        "relation_catalog_metadata",
    ]:
        insert_row(
            conn,
            "claim_boundary_catalog",
            {
                "object_type": object_type,
                "object_id": object_type,
                "claim_level": "infrastructure_metadata_only",
                "physical_interpretation_allowed": 0,
                "residual_analysis_allowed": 0,
                "model_fitting_allowed": 0,
                "bridge_claim_allowed": 0,
                "value_reading_allowed": 0,
                "notes": "Metadata seed rows do not authorize physical interpretation.",
            },
        )
        bump("claim_boundary_catalog")

    source_rows = [
        {
            "source_name": "QSB-DB schema source",
            "source_type": "repository_schema_file",
            "provider_or_project": "QSB",
            "source_url_or_path": "data/QSB-DB/schema/qsb_research_db_schema.sql",
            "source_download_status": "not_applicable",
            "source_reachability_status": "reachable_local_repo_path",
            "source_corruption_status": "not_checked",
            "checksum_status": "not_checked",
            "provenance_confidence": "high",
            "quarantine_status": "not_quarantined",
            "notes": "metadata placeholder only; no raw data content",
        },
        {
            "source_name": "ShapiroInfo public sources local placeholder",
            "source_type": "local_public_source_directory",
            "provider_or_project": "QSB-ST ShapiroInfo",
            "source_url_or_path": "data/QSB-ST-SHAPIROINFO/public_sources/",
            "source_download_status": "local_only_untracked",
            "source_reachability_status": "unresolved_without_raw_access",
            "source_corruption_status": "not_checked",
            "checksum_status": "not_checked",
            "provenance_confidence": "unresolved",
            "quarantine_status": "local_only",
            "notes": "placeholder only; no raw artifact contents inspected",
        },
    ]
    for row in source_rows:
        insert_row(conn, "raw_data_source", row)
        bump("raw_data_source")

    return counts


def table_count(conn: sqlite3.Connection, table: str) -> int:
    return int(conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0])


def all_table_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = []
    for table in SCHEMA_TABLES:
        rows.append({"table_name": table, "row_count": table_count(conn, table)})
    return rows


def foreign_key_violations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = []
    for violation in conn.execute("PRAGMA foreign_key_check"):
        rows.append(
            {
                "table_name": violation[0],
                "rowid": violation[1],
                "referenced_table": violation[2],
                "fk_id": violation[3],
            }
        )
    return rows


def forbidden_marker_hits(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    markers = [".tim", ".par"]
    hits: list[dict[str, Any]] = []
    for table in SCHEMA_TABLES:
        columns = [
            row[1]
            for row in conn.execute(f'PRAGMA table_info("{table}")')
            if str(row[2]).upper() == "TEXT"
        ]
        for column in columns:
            for marker in markers:
                sql = f'SELECT COUNT(*) FROM "{table}" WHERE "{column}" LIKE ?'
                count = int(conn.execute(sql, (f"%{marker}%",)).fetchone()[0])
                if count:
                    hits.append(
                        {
                            "table_name": table,
                            "column_name": column,
                            "marker": marker,
                            "hit_count": count,
                        }
                    )
    return hits


def run_forbidden_content_checks(conn: sqlite3.Connection) -> tuple[list[dict[str, Any]], str]:
    raw_data_count = table_count(conn, "raw_data")
    raw_token_count = table_count(conn, "raw_token_catalog")
    field_count = table_count(conn, "field_catalog")
    physical_auth_count = int(
        conn.execute(
            "SELECT COUNT(*) FROM claim_boundary_catalog "
            "WHERE physical_interpretation_allowed != 0 "
            "OR residual_analysis_allowed != 0 "
            "OR model_fitting_allowed != 0 "
            "OR bridge_claim_allowed != 0 "
            "OR value_reading_allowed != 0"
        ).fetchone()[0]
    )
    marker_hits = forbidden_marker_hits(conn)
    rows = [
        {
            "check_name": "raw_data_row_count",
            "status": "passed" if raw_data_count == 0 else "failed",
            "detail": str(raw_data_count),
        },
        {
            "check_name": "raw_token_row_count",
            "status": "passed" if raw_token_count == 0 else "failed",
            "detail": str(raw_token_count),
        },
        {
            "check_name": "field_catalog_scientific_row_count",
            "status": "passed" if field_count == 0 else "failed",
            "detail": str(field_count),
        },
        {
            "check_name": "claim_boundary_authorization",
            "status": "passed" if physical_auth_count == 0 else "failed",
            "detail": str(physical_auth_count),
        },
        {
            "check_name": "forbidden_marker_scan",
            "status": "passed" if not marker_hits else "failed",
            "detail": json.dumps(marker_hits, sort_keys=True),
        },
    ]
    status = "passed" if all(row["status"] == "passed" for row in rows) else "failed"
    return rows, status


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readout(path: Path, summary: dict[str, Any], insert_counts: dict[str, int]) -> None:
    readout = f"""# QSB-DB13 Metadata Seed Readout

## Purpose

Create a metadata-only seeded SQLite research database from the empty baseline database.

## Paths

- input_db: {summary["input_db_path"]}
- output_db: {summary["output_db_path"]}
- output_root: {summary["output_root"]}

## Seed Mode

- seed_execution_mode: {summary["seed_execution_mode"]}
- metadata_seed_status: {summary["metadata_seed_status"]}
- baseline_db_modified: {summary["baseline_db_modified"]}
- output_db_created: {summary["output_db_created"]}

## Inserted Rows

- inserted_table_count: {summary["inserted_table_count"]}
- inserted_row_count_total: {summary["inserted_row_count_total"]}
- insert_counts: {insert_counts}

## Validation

- fk_validation_status: {summary["fk_validation_status"]}
- forbidden_content_check_status: {summary["forbidden_content_check_status"]}
- raw_data_row_count: {summary["raw_data_row_count"]}
- raw_token_row_count: {summary["raw_token_row_count"]}
- field_catalog_scientific_row_count: {summary["field_catalog_scientific_row_count"]}

## Gates

- raw_artifact_access_status: {summary["raw_artifact_access_status"]}
- tim_par_value_reading_status: {summary["tim_par_value_reading_status"]}
- documentation_download_status: {summary["documentation_download_status"]}
- physical_interpretation_status: {summary["physical_interpretation_status"]}
- residual_analysis_gate: {summary["residual_analysis_gate"]}
- model_fitting_gate: {summary["model_fitting_gate"]}
- bridge_claim_gate: {summary["bridge_claim_gate"]}

## Claim Boundary

{summary["claim_boundary"]}
"""
    path.write_text(readout, encoding="utf-8")


def write_outputs(
    output_root: Path,
    summary: dict[str, Any],
    config: dict[str, Any],
    insert_counts: dict[str, int],
    table_counts: list[dict[str, Any]],
    fk_rows: list[dict[str, Any]],
    forbidden_rows: list[dict[str, Any]],
) -> None:
    write_json(output_root / "metadata_seed_summary.json", summary)
    write_json(output_root / "metadata_seed_config_resolved.json", config)
    write_csv(
        output_root / "metadata_seed_insert_counts.csv",
        ["table_name", "inserted_rows"],
        [{"table_name": key, "inserted_rows": value} for key, value in sorted(insert_counts.items())],
    )
    write_csv(
        output_root / "metadata_seed_table_row_counts.csv",
        ["table_name", "row_count"],
        table_counts,
    )
    write_csv(
        output_root / "metadata_seed_fk_validation.csv",
        ["table_name", "rowid", "referenced_table", "fk_id"],
        fk_rows,
    )
    write_csv(
        output_root / "metadata_seed_forbidden_content_check.csv",
        ["check_name", "status", "detail"],
        forbidden_rows,
    )
    write_readout(output_root / "metadata_seed_readout.md", summary, insert_counts)


def main() -> int:
    args = parse_args()
    input_db = args.input_db
    output_root = args.output_root
    output_db = resolve_output_db(output_root, args.output_db)

    if args.dry_run:
        return run_dry_run(input_db, output_root, output_db)

    if not input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {input_db}")
    if output_db.exists():
        if not args.overwrite:
            raise FileExistsError(
                f"Output DB already exists; rerun with --overwrite to replace it: {output_db}"
            )
        output_db.unlink()

    input_stat_before = input_db.stat()
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_db, output_db)

    conn = sqlite3.connect(output_db)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        try:
            conn.execute("BEGIN")
            insert_counts = seed_metadata(conn)
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        fk_violations = foreign_key_violations(conn)
        forbidden_rows, forbidden_status = run_forbidden_content_checks(conn)
        table_counts = all_table_counts(conn)
        raw_data_count = table_count(conn, "raw_data")
        raw_token_count = table_count(conn, "raw_token_catalog")
        field_count = table_count(conn, "field_catalog")
        input_stat_after = input_db.stat()
        baseline_modified = (
            input_stat_before.st_size != input_stat_after.st_size
            or input_stat_before.st_mtime_ns != input_stat_after.st_mtime_ns
        )
        inserted_total = sum(insert_counts.values())
        fk_status = "passed" if not fk_violations else "failed"
        metadata_status = "completed" if fk_status == "passed" and forbidden_status == "passed" else "failed"

        summary = {
            "generated_at_utc": utc_now(),
            "input_db_path": str(input_db),
            "output_db_path": str(output_db),
            "output_root": str(output_root),
            "metadata_seed_status": metadata_status,
            "baseline_db_modified": baseline_modified,
            "output_db_created": output_db.exists(),
            "seed_execution_mode": "metadata_only",
            "inserted_table_count": len(insert_counts),
            "inserted_row_count_total": inserted_total,
            "insert_counts": insert_counts,
            "fk_validation_status": fk_status,
            "foreign_key_check_violations": fk_violations,
            "forbidden_content_check_status": forbidden_status,
            "forbidden_tables_checked": ["raw_data", "raw_token_catalog", "field_catalog", "claim_boundary_catalog"],
            "raw_data_row_count": raw_data_count,
            "raw_token_row_count": raw_token_count,
            "field_catalog_scientific_row_count": field_count,
            "seed_data_inserted": True,
            "raw_data_seed_inserted": False,
            "raw_artifact_access_status": "not_performed",
            "tim_par_value_reading_status": "not_performed",
            "documentation_download_status": "not_performed",
            "physical_interpretation_status": "forbidden",
            "residual_analysis_gate": "closed",
            "model_fitting_gate": "closed",
            "bridge_claim_gate": "closed",
            "claim_boundary": CLAIM_BOUNDARY,
        }
        config = {
            "script": SCRIPT_PATH,
            "block": "QSB-DB12_METADATA_SEED_SCRIPT",
            "input_db": str(input_db),
            "output_root": str(output_root),
            "output_db": str(output_db),
            "overwrite": bool(args.overwrite),
            "dry_run": bool(args.dry_run),
            "seed_scope": "metadata_only",
            "raw_data_seed": "forbidden",
            "raw_artifact_access": "forbidden",
            "tim_par_value_reading": "forbidden",
            "analytics_data_seed": "forbidden",
            "bridge_claim_gate": "closed",
        }

        write_outputs(output_root, summary, config, insert_counts, table_counts, fk_violations, forbidden_rows)

        print("metadata_seed: complete")
        print(f"output_db: {output_db}")
        print(f"metadata_seed_status: {metadata_status}")
        print(f"inserted_row_count_total: {inserted_total}")
        print(f"fk_validation_status: {fk_status}")
        print(f"forbidden_content_check_status: {forbidden_status}")
        return 0 if metadata_status == "completed" else 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
