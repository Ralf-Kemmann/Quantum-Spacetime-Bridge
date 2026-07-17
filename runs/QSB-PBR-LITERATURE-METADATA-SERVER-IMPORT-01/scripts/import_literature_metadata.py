#!/usr/bin/env python3
"""Dry-run or execute a SQLite import for prepared literature metadata.

Default mode is dry-run. The script never writes unless --mode execute is used.
It is intentionally conservative because this run has no approved DB target.
"""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


RUN_DIR = Path("runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01")
CLAIM_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS qsb_literature_source (
          literature_id TEXT PRIMARY KEY,
          source_key TEXT UNIQUE NOT NULL,
          title TEXT NOT NULL,
          authors TEXT NOT NULL,
          year INTEGER,
          venue TEXT,
          doi TEXT,
          arxiv_id TEXT,
          source_url TEXT,
          source_type TEXT,
          source_class TEXT,
          author_cluster TEXT,
          theory_cluster TEXT,
          green_status TEXT,
          risk_status TEXT,
          verification_status TEXT,
          discovery_channel TEXT,
          notes TEXT
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_mechanism_tag (
          literature_id TEXT NOT NULL,
          mechanism_tag TEXT NOT NULL,
          tag_role TEXT,
          PRIMARY KEY (literature_id, mechanism_tag)
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_claim_boundary (
          literature_id TEXT PRIMARY KEY,
          internal_evidence_flag INTEGER NOT NULL DEFAULT 0,
          mechanism_claim_support INTEGER NOT NULL DEFAULT 0,
          physical_claim_support INTEGER NOT NULL DEFAULT 0,
          allowed_use TEXT NOT NULL,
          forbidden_use TEXT NOT NULL,
          claim_boundary TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_qsb_mapping (
          literature_id TEXT NOT NULL,
          qsb_structure_tag TEXT NOT NULL,
          mapping_kind TEXT,
          mapping_strength TEXT,
          mapping_notes TEXT,
          PRIMARY KEY (literature_id, qsb_structure_tag)
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_import_manifest (
          import_id TEXT PRIMARY KEY,
          run_id TEXT NOT NULL,
          source_report_path TEXT,
          source_report_sha256 TEXT,
          import_timestamp_utc TEXT,
          db_target TEXT,
          schema_action TEXT,
          row_count_sources INTEGER,
          row_count_tags INTEGER,
          row_count_claim_boundaries INTEGER,
          validation_status TEXT,
          claim_boundary TEXT
        );
        """
    )


def insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT OR ABORT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    conn.executemany(sql, [[row[column] for column in columns] for row in rows])


def validate(conn: sqlite3.Connection) -> list[str]:
    failures: list[str] = []
    checks = [
        ("source_count", "SELECT COUNT(*) FROM qsb_literature_source", 23),
        ("claim_boundary_count", "SELECT COUNT(*) FROM qsb_literature_claim_boundary", 23),
        ("nonzero_internal_evidence", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE internal_evidence_flag <> 0", 0),
        ("nonzero_mechanism_claim", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE mechanism_claim_support <> 0", 0),
        ("nonzero_physical_claim", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE physical_claim_support <> 0", 0),
        ("wrong_claim_boundary", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE claim_boundary <> ?", 0),
    ]
    for name, sql, expected in checks:
        params = (CLAIM_BOUNDARY,) if "?" in sql else ()
        actual = conn.execute(sql, params).fetchone()[0]
        if actual != expected:
            failures.append(f"{name}: expected {expected}, observed {actual}")
    missing_tags = conn.execute(
        """
        SELECT COUNT(*)
        FROM qsb_literature_source s
        WHERE NOT EXISTS (
          SELECT 1 FROM qsb_literature_mechanism_tag t
          WHERE t.literature_id = s.literature_id
        )
        """
    ).fetchone()[0]
    if missing_tags != 0:
        failures.append(f"sources_without_tags: expected 0, observed {missing_tags}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--seed", default=str(RUN_DIR / "data" / "literature_source_seed.csv"))
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    args = parser.parse_args()

    db_path = Path(args.db)
    data_dir = Path(args.seed).parent
    sources = read_csv(Path(args.seed))
    tags = read_csv(data_dir / "literature_mechanism_tags.csv")
    boundaries = read_csv(data_dir / "literature_claim_boundaries.csv")
    manifest = read_csv(data_dir / "literature_import_manifest.csv")

    if args.mode == "dry-run":
        conn = sqlite3.connect(":memory:")
    else:
        conn = sqlite3.connect(db_path)

    try:
        conn.execute("BEGIN")
        create_tables(conn)
        insert_rows(conn, "qsb_literature_source", sources)
        insert_rows(conn, "qsb_literature_mechanism_tag", tags)
        insert_rows(conn, "qsb_literature_claim_boundary", boundaries)
        insert_rows(conn, "qsb_literature_import_manifest", manifest)
        failures = validate(conn)
        if failures:
            conn.rollback()
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        if args.mode == "execute":
            conn.commit()
            print(f"PASS: executed and validated import into {db_path}")
        else:
            conn.rollback()
            print("PASS: dry-run validation passed; transaction rolled back")
        return 0
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
