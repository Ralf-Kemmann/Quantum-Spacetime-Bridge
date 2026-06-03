#!/usr/bin/env python3
"""QSB-DWH02: Phase 0/1 governance foundation.

This script performs the minimal additive governance step for the consolidated
QSB Research DB. It creates a timestamped backup before writing, adds only
DWH02 governance/audit objects, seeds Phase 0/1 governance rows, validates the
database, and exports DB-backed readout files.

It does not read raw TIM/PAR files, does not use generated CSV/JSON/MD files as
data substrate, does not create an isolated analysis DB, does not migrate data,
does not create the full target DWH schema, and does not compute physical,
timing, residual, delay, model, or statistical quantities.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh02_governance_foundation.py"
DEFAULT_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

DWH01_SCRIPT = Path("scripts/qsb_dwh01_target_research_dwh_schema_spec.py")
DWH01_EXPECTED_OUTPUTS = [
    "dwh01_target_research_dwh_schema_spec.md",
    "dwh01_target_research_dwh_schema_spec.json",
    "dwh01_target_table_design.csv",
    "dwh01_target_pk_fk_design.csv",
    "dwh01_migration_phase_plan.csv",
]

READOUT_MD = "dwh02_governance_foundation_readout.md"
SUMMARY_JSON = "dwh02_governance_foundation_summary.json"
TABLE_COUNTS_CSV = "dwh02_governance_table_counts.csv"
SCHEMA_VERSION_CSV = "dwh02_schema_version_snapshot.csv"
MIGRATION_LOG_CSV = "dwh02_migration_log_snapshot.csv"
VIEW_DEPENDENCY_CSV = "dwh02_view_dependency_seed.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    TABLE_COUNTS_CSV,
    SCHEMA_VERSION_CSV,
    MIGRATION_LOG_CSV,
    VIEW_DEPENDENCY_CSV,
]

GOVERNANCE_TABLES = [
    "audit_schema_version",
    "audit_migration_log",
    "audit_rebuild_manifest",
    "audit_view_dependency",
    "dwh02_governance_run_log",
]

DWH02_VIEWS = [
    "qsb_v_dwh02_schema_version_status",
    "qsb_v_dwh02_migration_status",
    "qsb_v_dwh02_rebuild_status",
    "qsb_v_dwh02_governance_dashboard",
    "qsb_v_dwh02_next_governance_actions",
]

KEY_CURRENT_VIEWS = [
    "qsb_v_db25_report_ready_snapshot",
    "qsb_v_db26_mapping_dashboard",
    "qsb_v_db27_mapping_priority_dashboard",
    "qsb_v_db28_dictionary_evidence_dashboard",
]

ARCHITECTURE_NAME = (
    "observation_centered_modified_star_snowflake_with_bridge_result_layer_"
    "and_audit_provenance_sidecar"
)

CLAIM_BOUNDARY = (
    "DWH02 is a governance foundation step. It creates additive audit/schema "
    "governance objects, records a backup-backed Phase 0/1 migration row, and "
    "exports DB-backed governance reports. It does not test a Bridge relation, "
    "does not migrate target DWH data, does not create the full target DWH "
    "schema, and does not make physical-interpretation claims."
)


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


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def expected_output_paths(output_root: Path) -> list[Path]:
    return [output_root / name for name in OUTPUT_FILENAMES]


def get_git_head() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return "unknown"
    value = result.stdout.strip()
    return value or "unknown"


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    result = []
    for row in rows:
        result.append(
            {
                "table": row[0],
                "rowid": row[1],
                "parent": row[2],
                "fkid": row[3],
            }
        )
    return result


def list_objects(con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        con,
        """
        SELECT type, name
        FROM sqlite_master
        WHERE type IN ('table', 'view')
          AND name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """,
    )


def row_count(con: sqlite3.Connection, object_name: str) -> int:
    return int(
        con.execute(
            f"SELECT COUNT(*) AS n FROM {quote_identifier(object_name)}"
        ).fetchone()["n"]
    )


def ensure_preconditions(
    db_path: Path,
    output_root: Path,
    overwrite: bool,
    allow_existing: bool,
) -> dict[str, Any]:
    if not db_path.exists():
        raise FileNotFoundError(f"Input DB does not exist: {db_path}")
    if not db_path.is_file():
        raise ValueError(f"Input DB path is not a file: {db_path}")
    if db_path.stat().st_size <= 0:
        raise ValueError(f"Input DB is empty: {db_path}")
    if not os.access(db_path, os.W_OK):
        raise PermissionError(f"Input DB is not writable: {db_path}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    if not DWH01_SCRIPT.exists():
        raise FileNotFoundError(f"Required DWH01 script missing: {DWH01_SCRIPT}")

    missing_dwh01 = [
        str(output_root / name)
        for name in DWH01_EXPECTED_OUTPUTS
        if not (output_root / name).exists()
    ]
    if missing_dwh01:
        raise FileNotFoundError(
            "Expected DWH01 reference output(s) missing: " + "; ".join(missing_dwh01)
        )

    existing_outputs = [str(path) for path in expected_output_paths(output_root) if path.exists()]
    if existing_outputs and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH02 output file(s): "
            + "; ".join(existing_outputs)
        )

    with connect_readonly(db_path) as con:
        pre_integrity = integrity_check(con)
        pre_fk_violations = foreign_key_violations(con)
        objects = list_objects(con)
        existing_governance_tables = [
            name for name in GOVERNANCE_TABLES if object_exists(con, name, "table")
        ]
        existing_dwh02_views = [
            name for name in DWH02_VIEWS if object_exists(con, name, "view")
        ]

    if pre_integrity != "ok":
        raise RuntimeError(f"Pre-write integrity_check failed: {pre_integrity}")
    if pre_fk_violations:
        raise RuntimeError(
            f"Pre-write foreign_key_check returned {len(pre_fk_violations)} violation(s)."
        )
    blocking_existing = [
        name for name in ("audit_schema_version", "audit_migration_log")
        if name in existing_governance_tables
    ]
    if blocking_existing and not allow_existing:
        raise RuntimeError(
            "Governance table(s) already exist; use --allow-existing only for "
            "controlled re-inspection: " + ", ".join(blocking_existing)
        )
    other_existing = existing_governance_tables + existing_dwh02_views
    if other_existing and not allow_existing:
        raise RuntimeError(
            "DWH02 governance object(s) already exist; use --allow-existing only "
            "for controlled re-inspection: " + ", ".join(sorted(set(other_existing)))
        )

    return {
        "pre_integrity": pre_integrity,
        "pre_fk_violation_count": len(pre_fk_violations),
        "existing_object_count": len(objects),
        "existing_table_count": sum(1 for item in objects if item["type"] == "table"),
        "existing_view_count": sum(1 for item in objects if item["type"] == "view"),
        "existing_governance_tables": existing_governance_tables,
        "existing_dwh02_views": existing_dwh02_views,
        "will_write": not other_existing,
    }


def create_backup(db_path: Path, timestamp: str) -> Path:
    backup_path = db_path.with_name(f"{db_path.stem}.pre_dwh02_{timestamp}.bak.db")
    if backup_path.exists():
        raise FileExistsError(f"Backup path already exists: {backup_path}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE dwh02_governance_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            input_db_path TEXT,
            backup_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            db_modified INTEGER,
            created_table_count INTEGER,
            created_view_count INTEGER,
            inserted_row_count INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT,
            CHECK (db_modified IN (0, 1))
        );

        CREATE TABLE audit_schema_version (
            schema_version_id TEXT PRIMARY KEY,
            schema_version_label TEXT,
            architecture_name TEXT,
            schema_status TEXT,
            based_on_db_path TEXT,
            based_on_git_head TEXT,
            dwh01_reference TEXT,
            created_by_run_id TEXT,
            created_at_utc TEXT,
            notes TEXT,
            FOREIGN KEY (created_by_run_id)
                REFERENCES dwh02_governance_run_log(run_id)
        );

        CREATE TABLE audit_migration_log (
            migration_id TEXT PRIMARY KEY,
            schema_version_id TEXT,
            phase_id TEXT,
            migration_label TEXT,
            migration_status TEXT,
            writes_db INTEGER,
            backup_db_path TEXT,
            rollback_plan TEXT,
            validation_status TEXT,
            applied_by_run_id TEXT,
            applied_at_utc TEXT,
            notes TEXT,
            CHECK (writes_db IN (0, 1)),
            FOREIGN KEY (schema_version_id)
                REFERENCES audit_schema_version(schema_version_id),
            FOREIGN KEY (applied_by_run_id)
                REFERENCES dwh02_governance_run_log(run_id)
        );

        CREATE TABLE audit_rebuild_manifest (
            rebuild_manifest_id TEXT PRIMARY KEY,
            schema_version_id TEXT,
            rebuild_scope TEXT,
            rebuild_status TEXT,
            required_inputs TEXT,
            required_scripts TEXT,
            known_gaps TEXT,
            next_required_action TEXT,
            created_by_run_id TEXT,
            created_at_utc TEXT,
            FOREIGN KEY (schema_version_id)
                REFERENCES audit_schema_version(schema_version_id),
            FOREIGN KEY (created_by_run_id)
                REFERENCES dwh02_governance_run_log(run_id)
        );

        CREATE TABLE audit_view_dependency (
            view_dependency_id TEXT PRIMARY KEY,
            schema_version_id TEXT,
            view_name TEXT,
            depends_on_object TEXT,
            dependency_type TEXT,
            dependency_status TEXT,
            parser_status TEXT,
            notes TEXT,
            created_by_run_id TEXT,
            created_at_utc TEXT,
            FOREIGN KEY (schema_version_id)
                REFERENCES audit_schema_version(schema_version_id),
            FOREIGN KEY (created_by_run_id)
                REFERENCES dwh02_governance_run_log(run_id)
        );
        """
    )


def create_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE VIEW qsb_v_dwh02_schema_version_status AS
        SELECT
            schema_version_id,
            schema_version_label,
            architecture_name,
            schema_status,
            based_on_git_head,
            created_at_utc
        FROM audit_schema_version
        ORDER BY created_at_utc, schema_version_id;

        CREATE VIEW qsb_v_dwh02_migration_status AS
        SELECT
            migration_id,
            phase_id,
            migration_label,
            migration_status,
            validation_status,
            backup_db_path,
            rollback_plan
        FROM audit_migration_log
        ORDER BY applied_at_utc, migration_id;

        CREATE VIEW qsb_v_dwh02_rebuild_status AS
        SELECT
            rebuild_manifest_id,
            rebuild_scope,
            rebuild_status,
            known_gaps,
            next_required_action
        FROM audit_rebuild_manifest
        ORDER BY created_at_utc, rebuild_manifest_id;

        CREATE VIEW qsb_v_dwh02_governance_dashboard AS
        SELECT
            run.run_id,
            (SELECT COUNT(*) FROM audit_schema_version) AS schema_version_count,
            (SELECT COUNT(*) FROM audit_migration_log) AS migration_log_count,
            (SELECT COUNT(*) FROM audit_rebuild_manifest) AS rebuild_manifest_count,
            (SELECT COUNT(*) FROM audit_view_dependency) AS view_dependency_seed_count,
            run.created_table_count,
            run.created_view_count,
            run.integrity_check_result,
            run.foreign_key_violation_count
        FROM dwh02_governance_run_log AS run
        ORDER BY run.run_timestamp_utc DESC, run.run_id DESC;

        CREATE VIEW qsb_v_dwh02_next_governance_actions AS
        SELECT
            '01' AS action_id,
            'create target raw/core schema in workcopy only' AS next_action,
            'pending' AS action_status,
            'Use backup/workcopy discipline before creating raw/core target tables.' AS notes
        UNION ALL
        SELECT
            '02',
            'build full view dependency parser',
            'pending',
            'DWH02 seeds only selected qsb_v dependencies and does not parse full SQL.'
        UNION ALL
        SELECT
            '03',
            'define reproducible rebuild path',
            'pending',
            'Specify source inventory, scripts, manifests, and replay limitations before rebuild tests.'
        UNION ALL
        SELECT
            '04',
            'create ERD export from target schema',
            'pending',
            'Export DWH slices after target raw/core/audit objects exist in a workcopy.'
        UNION ALL
        SELECT
            '05',
            'implement row-count parity checks for migration phases',
            'pending',
            'Compare current staging/history row counts to target migration outputs with documented exceptions.';
        """
    )


def insert_seed_rows(
    con: sqlite3.Connection,
    db_path: Path,
    backup_path: Path,
    timestamp: str,
    created_at: str,
    git_head: str,
) -> dict[str, Any]:
    run_id = f"DWH02_GOVERNANCE_RUN_{timestamp}"
    schema_version_id = f"QSB_DWH_SCHEMA_V0_1_PROPOSED_{timestamp}"
    migration_id = f"DWH02_PHASE_0_1_GOVERNANCE_FOUNDATION_{timestamp}"
    rebuild_manifest_id = f"DWH02_REBUILD_MANIFEST_SEED_{timestamp}"

    con.execute(
        """
        INSERT INTO dwh02_governance_run_log (
            run_id,
            run_timestamp_utc,
            input_db_path,
            backup_db_path,
            script_name,
            operation_mode,
            db_modified,
            created_table_count,
            created_view_count,
            inserted_row_count,
            integrity_check_result,
            foreign_key_violation_count,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            created_at,
            str(db_path),
            str(backup_path),
            SCRIPT_NAME,
            "phase_0_1_governance_foundation",
            1,
            len(GOVERNANCE_TABLES),
            len(DWH02_VIEWS),
            0,
            "pending",
            -1,
            "Initial row inserted before post-write validation.",
        ),
    )
    con.execute(
        """
        INSERT INTO audit_schema_version (
            schema_version_id,
            schema_version_label,
            architecture_name,
            schema_status,
            based_on_db_path,
            based_on_git_head,
            dwh01_reference,
            created_by_run_id,
            created_at_utc,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            schema_version_id,
            "qsb_research_dwh_target_v0_1_proposed",
            ARCHITECTURE_NAME,
            "proposed_governance_foundation",
            str(db_path),
            git_head,
            "dwh01_target_research_dwh_schema_spec",
            run_id,
            created_at,
            "Initial governance foundation row; target DWH schema not yet created.",
        ),
    )
    con.execute(
        """
        INSERT INTO audit_migration_log (
            migration_id,
            schema_version_id,
            phase_id,
            migration_label,
            migration_status,
            writes_db,
            backup_db_path,
            rollback_plan,
            validation_status,
            applied_by_run_id,
            applied_at_utc,
            notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            migration_id,
            schema_version_id,
            "Phase_0_1",
            "create_governance_foundation",
            "applied",
            1,
            str(backup_path),
            "restore pre_dwh02 backup",
            "pending",
            run_id,
            created_at,
            "Phase 0/1 governance foundation: backup plus minimal audit governance tables and views.",
        ),
    )
    con.execute(
        """
        INSERT INTO audit_rebuild_manifest (
            rebuild_manifest_id,
            schema_version_id,
            rebuild_scope,
            rebuild_status,
            required_inputs,
            required_scripts,
            known_gaps,
            next_required_action,
            created_by_run_id,
            created_at_utc
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            rebuild_manifest_id,
            schema_version_id,
            "full_research_dwh_rebuild",
            "not_yet_available",
            "consolidated SQLite snapshot plus future approved raw/source inventory references",
            "DB20-DB28, DWH01, and future DWH migration scripts",
            "Full reproducible rebuild path is not yet implemented.",
            "define rebuild path from raw source inventory and DB20-DB28/DWH01 scripts.",
            run_id,
            created_at,
        ),
    )

    inserted_row_count = 4
    dependency_rows: list[dict[str, str]] = []
    for index, view_name in enumerate(KEY_CURRENT_VIEWS, start=1):
        if object_exists(con, view_name, "view"):
            dependency_id = f"DWH02_VIEW_DEPENDENCY_SEED_{timestamp}_{index:02d}"
            row = {
                "view_dependency_id": dependency_id,
                "schema_version_id": schema_version_id,
                "view_name": view_name,
                "depends_on_object": "seed_only_unparsed_sql",
                "dependency_type": "current_qsb_v_seed",
                "dependency_status": "seed_only_needs_full_parser",
                "parser_status": "not_parsed",
                "notes": "Seed row only; full SQL dependency parser is a later governance action.",
                "created_by_run_id": run_id,
                "created_at_utc": created_at,
            }
            con.execute(
                """
                INSERT INTO audit_view_dependency (
                    view_dependency_id,
                    schema_version_id,
                    view_name,
                    depends_on_object,
                    dependency_type,
                    dependency_status,
                    parser_status,
                    notes,
                    created_by_run_id,
                    created_at_utc
                )
                VALUES (
                    :view_dependency_id,
                    :schema_version_id,
                    :view_name,
                    :depends_on_object,
                    :dependency_type,
                    :dependency_status,
                    :parser_status,
                    :notes,
                    :created_by_run_id,
                    :created_at_utc
                )
                """,
                row,
            )
            dependency_rows.append(row)
            inserted_row_count += 1

    con.execute(
        """
        UPDATE dwh02_governance_run_log
        SET inserted_row_count = ?
        WHERE run_id = ?
        """,
        (inserted_row_count, run_id),
    )
    return {
        "run_id": run_id,
        "schema_version_id": schema_version_id,
        "migration_id": migration_id,
        "rebuild_manifest_id": rebuild_manifest_id,
        "dependency_seed_count": len(dependency_rows),
        "inserted_row_count": inserted_row_count,
    }


def validate_post_write(con: sqlite3.Connection) -> dict[str, Any]:
    post_integrity = integrity_check(con)
    fk_violations = foreign_key_violations(con)
    missing_tables = [
        name for name in GOVERNANCE_TABLES if not object_exists(con, name, "table")
    ]
    missing_views = [name for name in DWH02_VIEWS if not object_exists(con, name, "view")]
    table_counts = {name: row_count(con, name) for name in GOVERNANCE_TABLES}
    view_probe_counts = {name: row_count(con, name) for name in DWH02_VIEWS}
    all_ok = (
        post_integrity == "ok"
        and not fk_violations
        and not missing_tables
        and not missing_views
    )
    return {
        "integrity_check_result": post_integrity,
        "foreign_key_violation_count": len(fk_violations),
        "missing_tables": missing_tables,
        "missing_views": missing_views,
        "table_counts": table_counts,
        "view_probe_counts": view_probe_counts,
        "validation_status": "passed" if all_ok else "failed",
    }


def mark_validation(
    con: sqlite3.Connection,
    run_id: str,
    migration_id: str,
    validation: dict[str, Any],
) -> None:
    con.execute(
        """
        UPDATE dwh02_governance_run_log
        SET integrity_check_result = ?,
            foreign_key_violation_count = ?,
            notes = ?
        WHERE run_id = ?
        """,
        (
            validation["integrity_check_result"],
            validation["foreign_key_violation_count"],
            "Post-write validation passed."
            if validation["validation_status"] == "passed"
            else "Post-write validation failed; inspect DWH02 readout.",
            run_id,
        ),
    )
    con.execute(
        """
        UPDATE audit_migration_log
        SET validation_status = ?,
            notes = ?
        WHERE migration_id = ?
        """,
        (
            validation["validation_status"],
            "Post-write integrity, FK, object-existence, and DWH02 view-query checks passed."
            if validation["validation_status"] == "passed"
            else "Post-write validation did not pass; inspect DWH02 readout.",
            migration_id,
        ),
    )


def collect_snapshots(con: sqlite3.Connection) -> dict[str, Any]:
    table_counts = []
    for name in GOVERNANCE_TABLES:
        table_counts.append(
            {
                "object_name": name,
                "object_type": "table",
                "row_count": row_count(con, name),
            }
        )
    for name in DWH02_VIEWS:
        table_counts.append(
            {
                "object_name": name,
                "object_type": "view",
                "row_count": row_count(con, name),
            }
        )
    return {
        "table_counts": table_counts,
        "schema_versions": fetch_dicts(
            con,
            """
            SELECT *
            FROM audit_schema_version
            ORDER BY created_at_utc, schema_version_id
            """,
        ),
        "migration_logs": fetch_dicts(
            con,
            """
            SELECT *
            FROM audit_migration_log
            ORDER BY applied_at_utc, migration_id
            """,
        ),
        "view_dependencies": fetch_dicts(
            con,
            """
            SELECT *
            FROM audit_view_dependency
            ORDER BY created_at_utc, view_dependency_id
            """,
        ),
        "view_rows": {
            name: fetch_dicts(
                con,
                f"SELECT * FROM {quote_identifier(name)} LIMIT 5",
            )
            for name in DWH02_VIEWS
        },
    }


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = ["note"]
        rows = [{"note": "no rows"}]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def render_readout(
    db_path: Path,
    backup_path: Path | None,
    preflight: dict[str, Any],
    seed: dict[str, Any] | None,
    validation: dict[str, Any],
    snapshots: dict[str, Any],
    mode: str,
) -> str:
    lines: list[str] = []
    lines.append("# QSB-DWH02 Governance Foundation Readout")
    lines.append("")
    lines.append(f"Generated at UTC: {utc_now()}")
    lines.append(f"Script: `{SCRIPT_NAME}`")
    lines.append(f"Input DB: `{db_path}`")
    lines.append(f"Operation mode: `{mode}`")
    lines.append(f"DB modified: `{str(mode == 'write').lower()}`")
    lines.append(f"Backup DB: `{backup_path if backup_path else 'not_created_reinspection_mode'}`")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append(
        f"Pre-write integrity check was `{preflight['pre_integrity']}` with "
        f"{preflight['pre_fk_violation_count']} FK violation(s). "
        f"The preflight inventory saw {preflight['existing_table_count']} tables "
        f"and {preflight['existing_view_count']} views."
    )
    lines.append("")
    if seed:
        lines.append(
            f"DWH02 created {len(GOVERNANCE_TABLES)} governance tables, "
            f"{len(DWH02_VIEWS)} qsb_v_dwh02_* views, and inserted "
            f"{seed['inserted_row_count']} governance seed row(s)."
        )
        lines.append(
            f"Schema version row: `{seed['schema_version_id']}`. "
            f"Migration row: `{seed['migration_id']}`."
        )
    else:
        lines.append(
            "No DB write was performed because --allow-existing re-inspection mode was used."
        )
    lines.append("")
    lines.append(
        f"Post-write/readback integrity check is `{validation['integrity_check_result']}` "
        f"with {validation['foreign_key_violation_count']} FK violation(s). "
        f"Validation status: `{validation['validation_status']}`."
    )
    lines.append("")
    lines.append("Governance object counts:")
    lines.append("")
    lines.append("| Object | Type | Rows |")
    lines.append("| --- | --- | --- |")
    for row in snapshots["table_counts"]:
        lines.append(f"| {row['object_name']} | {row['object_type']} | {row['row_count']} |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The consolidated DB now has a minimal audit governance foundation for "
        "schema-version tracking, migration logging, rebuild-readiness status, "
        "and seed-level view dependency tracking. This is sufficient for Phase "
        "0/1 governance before any raw/core target schema or data migration step."
    )
    lines.append("")
    lines.append("## Hypothese")
    lines.append("")
    lines.append(
        "A future Phase 2 workcopy implementation can use these governance tables "
        "as stable anchors for target raw/core DDL, row-count parity checks, ERD "
        "exports, and rebuild planning."
    )
    lines.append("")
    lines.append("## Offene Luecke")
    lines.append("")
    lines.append("- The target raw/core schema is not created yet.")
    lines.append("- The view dependency table contains seed rows only; a full SQL dependency parser remains a future task.")
    lines.append("- The reproducible rebuild path is not implemented yet.")
    lines.append("- Row-count parity checks for migration phases are not implemented yet.")
    lines.append("")
    lines.append("## qsb_v_dwh02 dashboard first rows")
    lines.append("")
    for view_name in DWH02_VIEWS:
        lines.append(f"### {view_name}")
        rows = snapshots["view_rows"][view_name]
        if not rows:
            lines.append("")
            lines.append("No rows.")
            lines.append("")
            continue
        headers = list(rows[0].keys())
        lines.append("")
        lines.append("| " + " | ".join(headers) + " |")
        lines.append("| " + " | ".join("---" for _ in headers) + " |")
        for row in rows:
            values = [str(row.get(header, "")).replace("|", "/") for header in headers]
            lines.append("| " + " | ".join(values) + " |")
        lines.append("")
    lines.append("## Claim Boundary")
    lines.append("")
    lines.append(CLAIM_BOUNDARY)
    lines.append("")
    return "\n".join(lines)


def write_reports(
    output_root: Path,
    db_path: Path,
    backup_path: Path | None,
    preflight: dict[str, Any],
    seed: dict[str, Any] | None,
    validation: dict[str, Any],
    snapshots: dict[str, Any],
    mode: str,
) -> None:
    paths = output_paths(output_root)
    summary = {
        "input_db_path": str(db_path),
        "db_modified": mode == "write",
        "backup_db_path": str(backup_path) if backup_path else None,
        "created_governance_tables": GOVERNANCE_TABLES if mode == "write" else [],
        "created_qsb_v_dwh02_views": DWH02_VIEWS if mode == "write" else [],
        "schema_version_id": seed["schema_version_id"] if seed else None,
        "migration_id": seed["migration_id"] if seed else None,
        "rebuild_manifest_status": (
            snapshots["view_rows"]["qsb_v_dwh02_rebuild_status"][0]["rebuild_status"]
            if snapshots["view_rows"]["qsb_v_dwh02_rebuild_status"]
            else None
        ),
        "view_dependency_seed_count": row_count_from_snapshot(
            snapshots["table_counts"], "audit_view_dependency"
        ),
        "integrity_check_result": validation["integrity_check_result"],
        "foreign_key_violation_count": validation["foreign_key_violation_count"],
        "validation_status": validation["validation_status"],
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_text(
        paths[READOUT_MD],
        render_readout(db_path, backup_path, preflight, seed, validation, snapshots, mode),
    )
    write_text(paths[SUMMARY_JSON], pretty_json(summary) + "\n")
    write_csv(paths[TABLE_COUNTS_CSV], snapshots["table_counts"])
    write_csv(paths[SCHEMA_VERSION_CSV], snapshots["schema_versions"])
    write_csv(paths[MIGRATION_LOG_CSV], snapshots["migration_logs"])
    write_csv(paths[VIEW_DEPENDENCY_CSV], snapshots["view_dependencies"])


def row_count_from_snapshot(rows: list[dict[str, Any]], object_name: str) -> int:
    for row in rows:
        if row["object_name"] == object_name:
            return int(row["row_count"])
    return 0


def execute_write(db_path: Path, timestamp: str) -> tuple[Path, dict[str, Any], dict[str, Any], dict[str, Any]]:
    backup_path = create_backup(db_path, timestamp)
    created_at = utc_now()
    git_head = get_git_head()
    with connect_writable(db_path) as con:
        try:
            con.execute("BEGIN")
            create_tables(con)
            create_views(con)
            seed = insert_seed_rows(
                con=con,
                db_path=db_path,
                backup_path=backup_path,
                timestamp=timestamp,
                created_at=created_at,
                git_head=git_head,
            )
            validation = validate_post_write(con)
            mark_validation(con, seed["run_id"], seed["migration_id"], validation)
            validation = validate_post_write(con)
            snapshots = collect_snapshots(con)
            if validation["validation_status"] != "passed":
                raise RuntimeError("Post-write validation failed before commit.")
            con.commit()
        except Exception:
            con.rollback()
            raise
    return backup_path, seed, validation, snapshots


def execute_reinspection(db_path: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    with connect_readonly(db_path) as con:
        validation = validate_post_write(con)
        snapshots = collect_snapshots(con)
    return validation, snapshots


def run(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    output_root = Path(args.output_root)
    preflight = ensure_preconditions(
        db_path=db_path,
        output_root=output_root,
        overwrite=args.overwrite,
        allow_existing=args.allow_existing,
    )
    timestamp = timestamp_for_id()
    if preflight["will_write"]:
        backup_path, seed, validation, snapshots = execute_write(db_path, timestamp)
        mode = "write"
    else:
        validation, snapshots = execute_reinspection(db_path)
        backup_path = None
        seed = None
        mode = "reinspection"

    write_reports(
        output_root=output_root,
        db_path=db_path,
        backup_path=backup_path,
        preflight=preflight,
        seed=seed,
        validation=validation,
        snapshots=snapshots,
        mode=mode,
    )
    print(f"DWH02 operation mode: {mode}")
    print(f"Input DB: {db_path}")
    print(f"DB modified: {mode == 'write'}")
    print(f"Backup DB: {backup_path if backup_path else 'not_created_reinspection_mode'}")
    print(f"Integrity check: {validation['integrity_check_result']}")
    print(f"FK violations: {validation['foreign_key_violation_count']}")
    print(f"Validation status: {validation['validation_status']}")
    print(f"Wrote {len(OUTPUT_FILENAMES)} DWH02 output files to {output_root}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create the QSB-DWH02 Phase 0/1 governance foundation in the "
            "consolidated QSB Research DB."
        )
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to consolidated SQLite DB.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Directory for DWH02 reports.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow controlled regeneration of DWH02 report files only.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow controlled re-inspection if DWH02 governance objects already exist.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
        return run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
