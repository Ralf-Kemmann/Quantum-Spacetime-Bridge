#!/usr/bin/env python3
"""QSB-DB05 empty SQLite database creator.

Creates an empty QSB research database from the committed QSB-DB03 schema SQL
when explicitly executed. The database is an audit-capable research-data
backbone, not an interpretation engine.
"""

from __future__ import annotations

import argparse
import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_SCHEMA_PATH = Path("data/QSB-DB/schema/qsb_research_db_schema.sql")
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB06_EMPTY_DATABASE")
DEFAULT_DATABASE_NAME = "qsb_research_empty.db"

REQUIRED_TABLES = [
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

CLAIM_BOUNDARY_PARTS = [
    "This output does not provide evidence for a physical Shapiro-information residual.",
    "This output does not validate the QSB-ST Bridge.",
    "This output does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, or molecular-structure physics claims.",
    "No raw artifact contents were inspected.",
    "No TIM/PAR values were read.",
    "No documentation or data files were downloaded.",
    "Seed data were not inserted.",
]

CLAIM_BOUNDARY = " ".join(CLAIM_BOUNDARY_PARTS)


def utc_now() -> str:
    """Return a compact UTC timestamp for generated metadata."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def resolve_database_path(output_root: Path, database_path: Path | None) -> Path:
    if database_path is not None:
        return database_path
    return output_root / DEFAULT_DATABASE_NAME


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create an empty QSB research SQLite database from the QSB-DB03 "
            "schema SQL and write schema inspection run artifacts."
        )
    )
    parser.add_argument(
        "--schema-path",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help=f"Schema SQL path. Default: {DEFAULT_SCHEMA_PATH}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Output directory. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--database-path",
        type=Path,
        default=None,
        help=(
            "Database path. Default: <output-root>/"
            f"{DEFAULT_DATABASE_NAME}"
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Delete and recreate the target database path if it already exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Resolve paths and validate schema path existence without outputs.",
    )
    return parser.parse_args()


def read_schema(schema_path: Path) -> str:
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema path does not exist: {schema_path}")
    if not schema_path.is_file():
        raise FileNotFoundError(f"Schema path is not a file: {schema_path}")
    return schema_path.read_text(encoding="utf-8")


def connect_and_apply_schema(database_path: Path, schema: str) -> sqlite3.Connection:
    conn = sqlite3.connect(database_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(schema)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def fetch_tables(conn: sqlite3.Connection) -> list[str]:
    return [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
    ]


def fetch_indexes(conn: sqlite3.Connection) -> list[str]:
    return [
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='index' AND name NOT LIKE 'sqlite_%' "
            "ORDER BY name"
        )
    ]


def fetch_table_rows(conn: sqlite3.Connection, tables: list[str]) -> list[dict[str, Any]]:
    rows = []
    for table in tables:
        count = conn.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        columns = conn.execute(f'PRAGMA table_info("{table}")').fetchall()
        rows.append(
            {
                "table_name": table,
                "row_count": count,
                "column_count": len(columns),
            }
        )
    return rows


def fetch_index_rows(conn: sqlite3.Connection, tables: list[str]) -> list[dict[str, Any]]:
    rows = []
    for table in tables:
        for index in conn.execute(f'PRAGMA index_list("{table}")'):
            rows.append(
                {
                    "table_name": table,
                    "index_name": index[1],
                    "unique_flag": index[2],
                    "origin": index[3],
                    "partial": index[4],
                }
            )
    return sorted(rows, key=lambda item: (item["table_name"], item["index_name"]))


def fetch_fk_rows(conn: sqlite3.Connection, tables: list[str]) -> list[dict[str, Any]]:
    rows = []
    for table in tables:
        for fk in conn.execute(f'PRAGMA foreign_key_list("{table}")'):
            rows.append(
                {
                    "table_name": table,
                    "fk_id": fk[0],
                    "seq": fk[1],
                    "referenced_table": fk[2],
                    "from_column": fk[3],
                    "to_column": fk[4],
                    "on_update": fk[5],
                    "on_delete": fk[6],
                    "match": fk[7],
                }
            )
    return sorted(rows, key=lambda item: (item["table_name"], item["fk_id"], item["seq"]))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_readout(
    path: Path,
    summary: dict[str, Any],
    overwrite: bool,
) -> None:
    text = f"""# QSB-DB06 Empty SQLite Database Creation Readout

## Purpose

Create an empty SQLite research database from the committed QSB-DB03 schema SQL.

The database is an audit-capable research-data backbone, not an interpretation engine.

## Paths

- schema_path: {summary["schema_path"]}
- database_path: {summary["database_path"]}
- output_root: {summary["output_root"]}

## Schema Validation

- sqlite_validation_status: {summary["sqlite_validation_status"]}
- table_count: {summary["table_count"]}
- index_count: {summary["index_count"]}
- missing_tables: {summary["missing_tables"]}
- total user row count: {summary["user_row_count_total"]}
- overwrite: {overwrite}

## Boundary Status

- seed_data_inserted: {summary["seed_data_inserted"]}
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
    path.write_text(text, encoding="utf-8")


def write_outputs(
    output_root: Path,
    summary: dict[str, Any],
    config: dict[str, Any],
    table_rows: list[dict[str, Any]],
    index_rows: list[dict[str, Any]],
    fk_rows: list[dict[str, Any]],
    overwrite: bool,
) -> None:
    write_json(output_root / "sqlite_empty_database_creation_summary.json", summary)
    write_json(output_root / "sqlite_empty_database_config_resolved.json", config)
    write_csv(
        output_root / "sqlite_empty_database_schema_tables.csv",
        ["table_name", "row_count", "column_count"],
        table_rows,
    )
    write_csv(
        output_root / "sqlite_empty_database_schema_indexes.csv",
        ["table_name", "index_name", "unique_flag", "origin", "partial"],
        index_rows,
    )
    write_csv(
        output_root / "sqlite_empty_database_fk_report.csv",
        [
            "table_name",
            "fk_id",
            "seq",
            "referenced_table",
            "from_column",
            "to_column",
            "on_update",
            "on_delete",
            "match",
        ],
        fk_rows,
    )
    write_readout(output_root / "sqlite_empty_database_readout.md", summary, overwrite)


def run_dry_run(schema_path: Path, output_root: Path, database_path: Path) -> int:
    read_schema(schema_path)
    print("dry_run: true")
    print(f"schema_path: {schema_path}")
    print(f"output_root: {output_root}")
    print(f"database_path: {database_path}")
    print("database_file_created: false")
    print("seed_data_inserted: false")
    return 0


def main() -> int:
    args = parse_args()
    schema_path = args.schema_path
    output_root = args.output_root
    database_path = resolve_database_path(output_root, args.database_path)

    if args.dry_run:
        return run_dry_run(schema_path, output_root, database_path)

    schema = read_schema(schema_path)
    output_root.mkdir(parents=True, exist_ok=True)

    if database_path.exists():
        if not args.overwrite:
            raise FileExistsError(
                f"Database path already exists; rerun with --overwrite to replace it: "
                f"{database_path}"
            )
        database_path.unlink()

    conn = connect_and_apply_schema(database_path, schema)
    try:
        tables = fetch_tables(conn)
        indexes = fetch_indexes(conn)
        missing_tables = sorted(set(REQUIRED_TABLES) - set(tables))
        table_rows = fetch_table_rows(conn, tables)
        index_rows = fetch_index_rows(conn, tables)
        fk_rows = fetch_fk_rows(conn, tables)
        user_row_count_total = sum(int(row["row_count"]) for row in table_rows)
        validation_status = (
            "passed"
            if not missing_tables and user_row_count_total == 0
            else "failed"
        )

        summary = {
            "generated_at_utc": utc_now(),
            "schema_path": str(schema_path),
            "database_path": str(database_path),
            "output_root": str(output_root),
            "sqlite_validation_status": validation_status,
            "table_count": len(tables),
            "index_count": len(indexes),
            "missing_tables": missing_tables,
            "user_row_count_total": user_row_count_total,
            "database_file_created": database_path.exists(),
            "seed_data_inserted": False,
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
            "script": "scripts/qsb_db05_create_empty_sqlite_database.py",
            "block": "QSB-DB05_SQLITE_EMPTY_DATABASE_CREATION_SCRIPT",
            "schema_path": str(schema_path),
            "database_path": str(database_path),
            "output_root": str(output_root),
            "overwrite": bool(args.overwrite),
            "dry_run": bool(args.dry_run),
            "required_tables": REQUIRED_TABLES,
            "execution_scope": "empty_database_creation_only",
            "seed_data_insertion": "forbidden",
            "raw_artifact_access": "forbidden",
            "tim_par_value_reading": "forbidden",
            "physical_interpretation": "forbidden",
        }

        write_outputs(
            output_root,
            summary,
            config,
            table_rows,
            index_rows,
            fk_rows,
            bool(args.overwrite),
        )

        print("sqlite_empty_database_creation: complete")
        print(f"database_path: {database_path}")
        print(f"table_count: {len(tables)}")
        print(f"index_count: {len(indexes)}")
        print(f"missing_tables: {missing_tables}")
        print(f"user_row_count_total: {user_row_count_total}")
        if validation_status != "passed":
            return 1
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
