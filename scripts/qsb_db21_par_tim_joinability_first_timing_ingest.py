#!/usr/bin/env python3
"""QSB-DB21 PAR/TIM joinability and first TIM raw ingest.

This script copies the DB20 real rawdata contact database into a DB21 output
database, inventories real PAR/TIM source files, ingests the first deterministic
TIM source as raw text records, stores token values as text, and creates
joinability scaffolding. It does not perform timing analysis, residual analysis,
model fitting, statistical inference, Shapiro confirmation, QSB validation, or
Bridge claims.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCK_NAME = "QSB-DB21_PAR_TIM_JOINABILITY_FIRST_TIM_INGEST"
SCRIPT_PATH = Path("scripts/qsb_db21_par_tim_joinability_first_timing_ingest.py")
DEFAULT_INPUT_DB = Path(
    "runs/QSB-DB/QSB_DB20_FIRST_REAL_RAWDATA_CONTACT/qsb_research_real_rawdata_contact.db"
)
DEFAULT_SOURCE_ROOT = Path("data/QSB-ST-SHAPIROINFO/public_sources")
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB21_PAR_TIM_JOINABILITY_FIRST_TIM_INGEST")
DEFAULT_OUTPUT_DB_NAME = "qsb_research_par_tim_joinability.db"

READOUT_NAME = "db21_par_tim_joinability_readout.md"
SUMMARY_NAME = "db21_par_tim_joinability_summary.json"
SOURCE_INVENTORY_NAME = "QSB_DB21_PAR_TIM_source_inventory.csv"
FIELD_INVENTORY_NAME = "QSB_DB21_PAR_TIM_field_inventory.csv"
JOINABILITY_NAME = "QSB_DB21_PAR_TIM_joinability_matrix.csv"
TABLE_COUNTS_NAME = "QSB_DB21_PAR_TIM_table_counts.csv"

CLAIM_BOUNDARY = (
    "DB21 is PAR/TIM rawdata ingest and joinability scaffolding only. It does "
    "not perform timing analysis, residual analysis, model fitting, statistical "
    "inference, Shapiro confirmation, QSB validation, physical interpretation, "
    "or Bridge confirmation."
)


@dataclass
class SourceFile:
    source_family_label: str
    object_label_candidate: str
    source_path: Path
    relative_path: str
    source_file_name: str
    source_file_extension: str
    source_file_size_bytes: int
    source_file_mtime_utc: str
    source_file_hash_sha256: str
    source_type: str
    structure_kind: str
    readability_status: str
    line_count: int
    blank_line_count: int
    nonblank_line_count: int
    first_structural_lines: str
    db20_selected_for_ingest: int
    quarantine_status: str
    anomaly_status: str
    source_inventory_id: int | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy DB20 to DB21, inventory PAR/TIM files, ingest one deterministic "
            "TIM file as raw text, create joinability tables/views, and write readouts."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help=f"DB20 input DB. Default: {DEFAULT_INPUT_DB}",
    )
    parser.add_argument(
        "--source-root",
        type=Path,
        default=DEFAULT_SOURCE_ROOT,
        help=f"Real source root. Default: {DEFAULT_SOURCE_ROOT}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"DB21 output root. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--output-db",
        type=Path,
        default=None,
        help=f"Output DB path. Default: <output-root>/{DEFAULT_OUTPUT_DB_NAME}",
    )
    parser.add_argument(
        "--tim-source-file",
        type=Path,
        default=None,
        help=(
            "Optional TIM file to ingest. Relative paths are resolved against --source-root. "
            "Default is deterministic smallest readable matching-family TIM."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite DB21 non-DB output artifacts if they already exist. The DB is never overwritten.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print selected sources and output paths without creating files.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def path_mtime_utc(path: Path) -> str:
    return (
        datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()


def output_db_path(output_root: Path, output_db: Path | None) -> Path:
    return output_db if output_db is not None else output_root / DEFAULT_OUTPUT_DB_NAME


def output_csv_root(output_root: Path) -> Path:
    return output_root.parent


def compact_snippet(line: str, limit: int = 160) -> str:
    text = " ".join(line.strip().split())
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def source_family_label(relative_path: str) -> str:
    parts = Path(relative_path).parts
    return parts[0] if parts else "source_root"


def object_label_candidate(path: Path) -> str:
    name = path.name
    for marker in ["J0740+6620", "j0740_6620", "J0740_6620"]:
        if marker.lower() in name.lower():
            return "J0740+6620"
    if "+" in name:
        return name.split(".")[0]
    return path.stem


def classify_source_type(suffix: str) -> str:
    if suffix == ".par":
        return "PAR"
    if suffix == ".tim":
        return "TIM"
    return "OTHER"


def structure_kind_for(suffix: str) -> str:
    if suffix == ".par":
        return "line_based_parameter_key_value_like"
    if suffix == ".tim":
        return "line_based_timing_whitespace_records"
    return "unknown"


def read_text_shape(path: Path) -> tuple[str, int, int, int, str]:
    line_count = 0
    blank_count = 0
    first_lines: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line_count += 1
            line = raw_line.rstrip("\n")
            if line.strip():
                if len(first_lines) < 5:
                    first_lines.append(compact_snippet(line))
            else:
                blank_count += 1
    return "readable_text", line_count, blank_count, line_count - blank_count, " || ".join(first_lines)


def db20_source_inventory(input_db: Path) -> dict[str, dict[str, Any]]:
    inventory: dict[str, dict[str, Any]] = {}
    con = sqlite3.connect(input_db)
    try:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            """
            SELECT *
            FROM qsb_v_db20_source_inventory
            WHERE source_extension IN ('.par', '.tim')
            """
        ).fetchall()
        for row in rows:
            inventory[str(row["relative_path"])] = dict(row)
    finally:
        con.close()
    return inventory


def discover_par_tim_sources(source_root: Path, input_db: Path) -> list[SourceFile]:
    db20_inventory = db20_source_inventory(input_db)
    sources: list[SourceFile] = []
    for path in sorted(source_root.rglob("*"), key=lambda p: p.as_posix()):
        if not path.is_file() or path.suffix.lower() not in {".par", ".tim"}:
            continue
        relative_path = path.relative_to(source_root).as_posix()
        stat = path.stat()
        readability_status, line_count, blank_count, nonblank_count, first_lines = read_text_shape(path)
        db20_row = db20_inventory.get(relative_path, {})
        source_type = classify_source_type(path.suffix.lower())
        sources.append(
            SourceFile(
                source_family_label=source_family_label(relative_path),
                object_label_candidate=object_label_candidate(path),
                source_path=path,
                relative_path=relative_path,
                source_file_name=path.name,
                source_file_extension=path.suffix.lower(),
                source_file_size_bytes=int(stat.st_size),
                source_file_mtime_utc=str(db20_row.get("source_file_mtime_utc") or path_mtime_utc(path)),
                source_file_hash_sha256=str(db20_row.get("source_file_hash_sha256") or sha256_file(path)),
                source_type=source_type,
                structure_kind=str(db20_row.get("structure_kind") or structure_kind_for(path.suffix.lower())),
                readability_status=readability_status,
                line_count=int(db20_row.get("line_count") or line_count),
                blank_line_count=int(db20_row.get("blank_line_count") or blank_count),
                nonblank_line_count=int(db20_row.get("nonblank_line_count") or nonblank_count),
                first_structural_lines=first_lines,
                db20_selected_for_ingest=int(db20_row.get("selected_for_ingest") or 0),
                quarantine_status=str(db20_row.get("quarantine_status") or "not_quarantined"),
                anomaly_status="not_evaluated",
            )
        )
    return sources


def select_tim_source(sources: list[SourceFile], requested: Path | None, source_root: Path) -> SourceFile:
    tim_sources = [source for source in sources if source.source_type == "TIM" and source.readability_status == "readable_text"]
    if requested is not None:
        requested_path = requested if requested.is_absolute() else source_root / requested
        resolved = requested_path.resolve()
        for source in tim_sources:
            if source.source_path.resolve() == resolved or source.relative_path == requested.as_posix():
                return source
        raise FileNotFoundError(f"Requested TIM source not found or not readable: {requested}")

    preferred = [
        source
        for source in tim_sources
        if source.source_family_label == "j0740_6620" and source.object_label_candidate == "J0740+6620"
    ]
    candidates = preferred if preferred else tim_sources
    candidates.sort(key=lambda source: (source.source_file_size_bytes, source.relative_path))
    if not candidates:
        raise RuntimeError("No TIM source available for DB21.")
    return candidates[0]


def ensure_no_output_collision(paths: list[Path], output_db: Path, overwrite: bool) -> None:
    if output_db.exists():
        raise FileExistsError(f"DB21 output DB already exists: {output_db}")
    existing = [path for path in paths if path.exists() and path != output_db]
    if existing and not overwrite:
        joined = "\n".join(path.as_posix() for path in existing)
        raise FileExistsError(f"DB21 output artifact(s) already exist:\n{joined}")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def insert_row(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> int:
    columns = list(values)
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
    cursor = conn.execute(sql, [values[column] for column in columns])
    return int(cursor.lastrowid)


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS db21_par_tim_source_inventory (
            source_inventory_id INTEGER PRIMARY KEY,
            source_family_label TEXT NOT NULL,
            object_label_candidate TEXT,
            source_path TEXT NOT NULL,
            relative_path TEXT NOT NULL UNIQUE,
            source_file_name TEXT NOT NULL,
            source_file_extension TEXT NOT NULL,
            source_file_size_bytes INTEGER NOT NULL,
            source_file_mtime_utc TEXT NOT NULL,
            source_file_hash_sha256 TEXT NOT NULL,
            source_type TEXT NOT NULL,
            structure_kind TEXT NOT NULL,
            readability_status TEXT NOT NULL,
            line_count INTEGER NOT NULL,
            blank_line_count INTEGER NOT NULL,
            nonblank_line_count INTEGER NOT NULL,
            first_structural_lines TEXT,
            db20_selected_for_ingest INTEGER NOT NULL DEFAULT 0,
            selected_for_db21_tim_ingest INTEGER NOT NULL DEFAULT 0,
            parse_status TEXT NOT NULL,
            quality_status TEXT NOT NULL,
            quarantine_status TEXT NOT NULL,
            anomaly_status TEXT NOT NULL,
            lineage_key TEXT NOT NULL UNIQUE,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db21_tim_ingest_run (
            ingest_run_id TEXT PRIMARY KEY,
            ingest_timestamp_utc TEXT NOT NULL,
            script_path TEXT NOT NULL,
            block_name TEXT NOT NULL,
            input_db_path TEXT NOT NULL,
            output_db_path TEXT NOT NULL,
            source_root_path TEXT NOT NULL,
            selected_tim_source_inventory_id INTEGER NOT NULL,
            selected_tim_relative_path TEXT NOT NULL,
            tim_raw_record_count INTEGER NOT NULL DEFAULT 0,
            tim_raw_field_value_count INTEGER NOT NULL DEFAULT 0,
            tim_comment_line_count INTEGER NOT NULL DEFAULT 0,
            tim_blank_line_count INTEGER NOT NULL DEFAULT 0,
            tim_malformed_or_short_line_count INTEGER NOT NULL DEFAULT 0,
            flagged_line_count INTEGER NOT NULL DEFAULT 0,
            quarantine_candidate_count INTEGER NOT NULL DEFAULT 0,
            anomaly_candidate_count INTEGER NOT NULL DEFAULT 0,
            foreign_key_violation_count INTEGER NOT NULL DEFAULT 0,
            run_status TEXT NOT NULL,
            stop_reason TEXT NOT NULL,
            claim_boundary TEXT NOT NULL,
            warnings_json TEXT NOT NULL DEFAULT '[]',
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (selected_tim_source_inventory_id)
                REFERENCES db21_par_tim_source_inventory(source_inventory_id)
        );

        CREATE TABLE IF NOT EXISTS db21_tim_raw_record (
            tim_record_id TEXT PRIMARY KEY,
            ingest_run_id TEXT NOT NULL,
            source_inventory_id INTEGER NOT NULL,
            source_family_label TEXT NOT NULL,
            source_path TEXT NOT NULL,
            source_file_name TEXT NOT NULL,
            record_index INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            line_type TEXT NOT NULL,
            raw_line_text TEXT NOT NULL,
            raw_line_hash_sha256 TEXT NOT NULL,
            token_count INTEGER NOT NULL,
            parse_status TEXT NOT NULL,
            quality_status TEXT NOT NULL,
            quarantine_status TEXT NOT NULL,
            anomaly_status TEXT NOT NULL,
            lineage_key TEXT NOT NULL UNIQUE,
            ingest_timestamp_utc TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (ingest_run_id) REFERENCES db21_tim_ingest_run(ingest_run_id),
            FOREIGN KEY (source_inventory_id)
                REFERENCES db21_par_tim_source_inventory(source_inventory_id)
        );

        CREATE TABLE IF NOT EXISTS db21_tim_raw_field_value (
            tim_field_value_id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL,
            ingest_run_id TEXT NOT NULL,
            source_inventory_id INTEGER NOT NULL,
            tim_record_id TEXT NOT NULL,
            record_index INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            field_index INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            raw_value_text TEXT NOT NULL,
            raw_value_hash_sha256 TEXT NOT NULL,
            parse_status TEXT NOT NULL,
            quality_status TEXT NOT NULL,
            quarantine_status TEXT NOT NULL,
            anomaly_status TEXT NOT NULL,
            lineage_key TEXT NOT NULL UNIQUE,
            ingest_timestamp_utc TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (ingest_run_id) REFERENCES db21_tim_ingest_run(ingest_run_id),
            FOREIGN KEY (source_inventory_id)
                REFERENCES db21_par_tim_source_inventory(source_inventory_id),
            FOREIGN KEY (tim_record_id) REFERENCES db21_tim_raw_record(tim_record_id)
        );

        CREATE TABLE IF NOT EXISTS db21_par_tim_field_inventory (
            field_inventory_id INTEGER PRIMARY KEY,
            source_inventory_id INTEGER NOT NULL,
            source_type TEXT NOT NULL,
            source_family_label TEXT NOT NULL,
            source_file_name TEXT NOT NULL,
            field_index INTEGER,
            field_name TEXT NOT NULL,
            occurrence_count INTEGER NOT NULL,
            first_line_number INTEGER,
            sample_raw_value_text TEXT,
            parse_status TEXT NOT NULL,
            quality_status TEXT NOT NULL,
            quarantine_status TEXT NOT NULL,
            anomaly_status TEXT NOT NULL,
            lineage_key TEXT NOT NULL UNIQUE,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (source_inventory_id)
                REFERENCES db21_par_tim_source_inventory(source_inventory_id)
        );

        CREATE TABLE IF NOT EXISTS db21_par_tim_joinability (
            joinability_id INTEGER PRIMARY KEY,
            source_family_label TEXT NOT NULL,
            par_source_inventory_id INTEGER,
            tim_source_inventory_id INTEGER,
            par_relative_path TEXT,
            tim_relative_path TEXT,
            same_source_family_label INTEGER NOT NULL,
            matching_object_label_candidate INTEGER NOT NULL,
            par_file_present INTEGER NOT NULL,
            tim_file_present INTEGER NOT NULL,
            shared_directory_context INTEGER NOT NULL,
            direct_record_level_join_available INTEGER NOT NULL DEFAULT 0,
            joinability_status TEXT NOT NULL,
            joinability_notes TEXT NOT NULL,
            lineage_key TEXT NOT NULL UNIQUE,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (par_source_inventory_id)
                REFERENCES db21_par_tim_source_inventory(source_inventory_id),
            FOREIGN KEY (tim_source_inventory_id)
                REFERENCES db21_par_tim_source_inventory(source_inventory_id)
        );

        CREATE TABLE IF NOT EXISTS db21_tim_quality_flag (
            quality_flag_id INTEGER PRIMARY KEY,
            ingest_run_id TEXT NOT NULL,
            source_inventory_id INTEGER NOT NULL,
            tim_record_id TEXT,
            tim_field_value_id INTEGER,
            flag_scope TEXT NOT NULL,
            flag_type TEXT NOT NULL,
            flag_status TEXT NOT NULL,
            flag_severity TEXT NOT NULL,
            flag_note TEXT,
            lineage_key TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (ingest_run_id) REFERENCES db21_tim_ingest_run(ingest_run_id),
            FOREIGN KEY (source_inventory_id)
                REFERENCES db21_par_tim_source_inventory(source_inventory_id),
            FOREIGN KEY (tim_record_id) REFERENCES db21_tim_raw_record(tim_record_id),
            FOREIGN KEY (tim_field_value_id)
                REFERENCES db21_tim_raw_field_value(tim_field_value_id)
        );
        """
    )


def create_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP VIEW IF EXISTS qsb_v_db21_par_tim_source_inventory;
        CREATE VIEW qsb_v_db21_par_tim_source_inventory AS
        SELECT
            source_inventory_id,
            source_family_label,
            object_label_candidate,
            relative_path,
            source_file_name,
            source_file_extension,
            source_file_size_bytes,
            source_file_mtime_utc,
            source_type,
            structure_kind,
            readability_status,
            line_count,
            blank_line_count,
            nonblank_line_count,
            db20_selected_for_ingest,
            selected_for_db21_tim_ingest,
            parse_status,
            quality_status,
            quarantine_status,
            anomaly_status,
            lineage_key
        FROM db21_par_tim_source_inventory;

        DROP VIEW IF EXISTS qsb_v_db21_tim_raw_records;
        CREATE VIEW qsb_v_db21_tim_raw_records AS
        SELECT
            tim_record_id,
            ingest_run_id,
            source_inventory_id,
            source_family_label,
            source_file_name,
            record_index,
            line_number,
            line_type,
            raw_line_text,
            token_count,
            parse_status,
            quality_status,
            quarantine_status,
            anomaly_status,
            lineage_key
        FROM db21_tim_raw_record;

        DROP VIEW IF EXISTS qsb_v_db21_tim_raw_field_values;
        CREATE VIEW qsb_v_db21_tim_raw_field_values AS
        SELECT
            tim_field_value_id,
            field_id,
            ingest_run_id,
            source_inventory_id,
            tim_record_id,
            record_index,
            line_number,
            field_index,
            field_name,
            raw_value_text,
            raw_value_hash_sha256,
            parse_status,
            quality_status,
            quarantine_status,
            anomaly_status,
            lineage_key
        FROM db21_tim_raw_field_value;

        DROP VIEW IF EXISTS qsb_v_db21_par_tim_field_inventory;
        CREATE VIEW qsb_v_db21_par_tim_field_inventory AS
        SELECT
            fi.field_inventory_id,
            si.relative_path,
            fi.source_type,
            fi.source_family_label,
            fi.source_file_name,
            fi.field_index,
            fi.field_name,
            fi.occurrence_count,
            fi.first_line_number,
            fi.sample_raw_value_text,
            fi.parse_status,
            fi.quality_status,
            fi.quarantine_status,
            fi.anomaly_status,
            fi.lineage_key
        FROM db21_par_tim_field_inventory fi
        JOIN db21_par_tim_source_inventory si
          ON si.source_inventory_id = fi.source_inventory_id;

        DROP VIEW IF EXISTS qsb_v_db21_par_tim_joinability;
        CREATE VIEW qsb_v_db21_par_tim_joinability AS
        SELECT
            source_family_label,
            par_relative_path,
            tim_relative_path,
            same_source_family_label,
            matching_object_label_candidate,
            par_file_present,
            tim_file_present,
            shared_directory_context,
            direct_record_level_join_available,
            joinability_status,
            joinability_notes,
            lineage_key
        FROM db21_par_tim_joinability;

        DROP VIEW IF EXISTS qsb_v_db21_measurement_reality_dashboard;
        CREATE VIEW qsb_v_db21_measurement_reality_dashboard AS
        SELECT 'par_file_count' AS metric_name, COUNT(*) AS metric_value
        FROM db21_par_tim_source_inventory
        WHERE source_type = 'PAR'
        UNION ALL
        SELECT 'tim_file_count', COUNT(*)
        FROM db21_par_tim_source_inventory
        WHERE source_type = 'TIM'
        UNION ALL
        SELECT 'ingested_tim_file_count', COUNT(*)
        FROM db21_par_tim_source_inventory
        WHERE selected_for_db21_tim_ingest = 1
        UNION ALL
        SELECT 'tim_raw_record_count', COUNT(*)
        FROM db21_tim_raw_record
        UNION ALL
        SELECT 'tim_raw_field_value_count', COUNT(*)
        FROM db21_tim_raw_field_value
        UNION ALL
        SELECT 'tim_comment_line_count', COUNT(*)
        FROM db21_tim_raw_record
        WHERE line_type = 'comment_line'
        UNION ALL
        SELECT 'tim_blank_line_count', COUNT(*)
        FROM db21_tim_raw_record
        WHERE line_type = 'blank_line'
        UNION ALL
        SELECT 'tim_malformed_or_short_line_count', COUNT(*)
        FROM db21_tim_raw_record
        WHERE line_type = 'malformed_or_short_line'
        UNION ALL
        SELECT 'par_tim_joinability_pair_count', COUNT(*)
        FROM db21_par_tim_joinability
        UNION ALL
        SELECT 'source_family_joinable_count', COUNT(*)
        FROM db21_par_tim_joinability
        WHERE joinability_status = 'source_family_joinable'
        UNION ALL
        SELECT 'foreign_key_violation_count', COALESCE(MAX(foreign_key_violation_count), 0)
        FROM db21_tim_ingest_run;

        DROP VIEW IF EXISTS qsb_v_db21_first_human_tim_readout;
        CREATE VIEW qsb_v_db21_first_human_tim_readout AS
        SELECT
            si.relative_path AS tim_relative_path,
            rr.line_number,
            rr.line_type,
            fv.field_index,
            fv.field_name,
            substr(fv.raw_value_text, 1, 160) AS raw_value_text,
            fv.parse_status,
            fv.quality_status,
            fv.quarantine_status,
            fv.anomaly_status,
            fv.lineage_key
        FROM db21_tim_raw_field_value fv
        JOIN db21_tim_raw_record rr
          ON rr.tim_record_id = fv.tim_record_id
        JOIN db21_par_tim_source_inventory si
          ON si.source_inventory_id = fv.source_inventory_id
        ORDER BY rr.record_index, fv.field_index;
        """
    )


def lineage(source_family: str, file_label: str, run_id: str, record_index: int, field_label: str) -> str:
    return f"SRC::{source_family}::FILE::{file_label}::RUN::{run_id}::REC::{record_index}::FIELD::{field_label}"


def classify_tim_line(line: str) -> tuple[str, str, str, str, str]:
    stripped = line.strip()
    if not stripped:
        return "blank_line", "blank_line", "blank_line_flagged", "quarantine_candidate", "not_evaluated"
    upper = stripped.upper()
    if stripped.startswith("#") or stripped.startswith("//") or stripped.startswith(";") or upper == "C" or upper.startswith("C "):
        return "comment_line", "parsed_comment_line", "source_flagged_raw_preserved", "quarantine_candidate", "source_flag_marker_present"
    tokens = stripped.split()
    if len(tokens) >= 5 and any(char.isdigit() for char in stripped):
        return "data_line", "parsed_whitespace_token_line", "raw_preserved", "not_quarantined", "not_evaluated"
    if len(tokens) < 5:
        return "malformed_or_short_line", "malformed_or_short_line", "structure_flagged", "quarantine_candidate", "structure_flagged"
    return "unknown_line", "unknown_line", "raw_preserved_unclassified", "not_quarantined", "not_evaluated"


def add_quality_flag(
    conn: sqlite3.Connection,
    *,
    ingest_run_id: str,
    source_inventory_id: int,
    tim_record_id: str | None,
    tim_field_value_id: int | None,
    flag_scope: str,
    flag_type: str,
    flag_status: str,
    flag_severity: str,
    flag_note: str,
    lineage_key: str,
    created_at_utc: str,
) -> None:
    insert_row(
        conn,
        "db21_tim_quality_flag",
        {
            "ingest_run_id": ingest_run_id,
            "source_inventory_id": source_inventory_id,
            "tim_record_id": tim_record_id,
            "tim_field_value_id": tim_field_value_id,
            "flag_scope": flag_scope,
            "flag_type": flag_type,
            "flag_status": flag_status,
            "flag_severity": flag_severity,
            "flag_note": flag_note,
            "lineage_key": lineage_key,
            "created_at_utc": created_at_utc,
        },
    )


def insert_sources(conn: sqlite3.Connection, sources: list[SourceFile], selected_tim: SourceFile, created_at: str, run_id: str) -> None:
    for source in sources:
        parse_status = "metadata_inventory_readable_text"
        quality_status = "source_inventory_preserved"
        quarantine_status = source.quarantine_status
        anomaly_status = source.anomaly_status
        source_lineage = lineage(source.source_family_label, source.source_file_name, run_id, 0, "SOURCE_FILE")
        source.source_inventory_id = insert_row(
            conn,
            "db21_par_tim_source_inventory",
            {
                "source_family_label": source.source_family_label,
                "object_label_candidate": source.object_label_candidate,
                "source_path": source.source_path.as_posix(),
                "relative_path": source.relative_path,
                "source_file_name": source.source_file_name,
                "source_file_extension": source.source_file_extension,
                "source_file_size_bytes": source.source_file_size_bytes,
                "source_file_mtime_utc": source.source_file_mtime_utc,
                "source_file_hash_sha256": source.source_file_hash_sha256,
                "source_type": source.source_type,
                "structure_kind": source.structure_kind,
                "readability_status": source.readability_status,
                "line_count": source.line_count,
                "blank_line_count": source.blank_line_count,
                "nonblank_line_count": source.nonblank_line_count,
                "first_structural_lines": source.first_structural_lines,
                "db20_selected_for_ingest": source.db20_selected_for_ingest,
                "selected_for_db21_tim_ingest": 1 if source.relative_path == selected_tim.relative_path else 0,
                "parse_status": parse_status,
                "quality_status": quality_status,
                "quarantine_status": quarantine_status,
                "anomaly_status": anomaly_status,
                "lineage_key": source_lineage,
                "created_at_utc": created_at,
            },
        )


def ingest_tim(conn: sqlite3.Connection, selected_tim: SourceFile, run_id: str, timestamp: str) -> dict[str, int]:
    if selected_tim.source_inventory_id is None:
        raise ValueError("Selected TIM source has no DB source_inventory_id.")

    counters = Counter()
    with selected_tim.source_path.open("r", encoding="utf-8", errors="replace") as handle:
        for record_index, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\n")
            tokens = line.strip().split() if line.strip() else []
            line_type, parse_status, quality_status, quarantine_status, anomaly_status = classify_tim_line(line)
            if selected_tim.quarantine_status != "not_quarantined" and quarantine_status == "not_quarantined":
                quarantine_status = selected_tim.quarantine_status
            record_id = (
                f"DB21_TIM_REC_{selected_tim.source_inventory_id}_{record_index:08d}_"
                f"{sha256_text(selected_tim.relative_path + ':' + str(record_index))[:12]}"
            )
            record_lineage = lineage(
                selected_tim.source_family_label,
                selected_tim.source_file_name,
                run_id,
                record_index,
                "RECORD",
            )
            insert_row(
                conn,
                "db21_tim_raw_record",
                {
                    "tim_record_id": record_id,
                    "ingest_run_id": run_id,
                    "source_inventory_id": selected_tim.source_inventory_id,
                    "source_family_label": selected_tim.source_family_label,
                    "source_path": selected_tim.source_path.as_posix(),
                    "source_file_name": selected_tim.source_file_name,
                    "record_index": record_index,
                    "line_number": record_index,
                    "line_type": line_type,
                    "raw_line_text": line,
                    "raw_line_hash_sha256": sha256_text(line),
                    "token_count": len(tokens),
                    "parse_status": parse_status,
                    "quality_status": quality_status,
                    "quarantine_status": quarantine_status,
                    "anomaly_status": anomaly_status,
                    "lineage_key": record_lineage,
                    "ingest_timestamp_utc": timestamp,
                    "created_at_utc": timestamp,
                },
            )
            counters["tim_raw_record_count"] += 1
            counters[f"{line_type}_count"] += 1
            if quality_status != "raw_preserved" or quarantine_status != "not_quarantined" or anomaly_status != "not_evaluated":
                counters["flagged_line_count"] += 1
            if quarantine_status != "not_quarantined":
                counters["quarantine_candidate_count"] += 1
            if anomaly_status != "not_evaluated":
                counters["anomaly_candidate_count"] += 1

            if line_type in {"blank_line", "comment_line", "malformed_or_short_line"} or selected_tim.quarantine_status != "not_quarantined":
                add_quality_flag(
                    conn,
                    ingest_run_id=run_id,
                    source_inventory_id=selected_tim.source_inventory_id,
                    tim_record_id=record_id,
                    tim_field_value_id=None,
                    flag_scope="record",
                    flag_type="source_context_or_structure_flag",
                    flag_status="retained",
                    flag_severity="audit_flag",
                    flag_note=f"line_type={line_type}; source_quarantine_status={selected_tim.quarantine_status}",
                    lineage_key=record_lineage,
                    created_at_utc=timestamp,
                )

            field_items = [("raw_line_text", line)] + [
                (f"tim_token_{token_index:03d}", token)
                for token_index, token in enumerate(tokens, start=1)
            ]
            for field_index, (field_name, raw_value_text) in enumerate(field_items, start=1):
                field_id = f"{field_index:04d}_{field_name}"
                field_lineage = lineage(
                    selected_tim.source_family_label,
                    selected_tim.source_file_name,
                    run_id,
                    record_index,
                    field_id,
                )
                field_quality_status = quality_status
                if raw_value_text == "":
                    field_quality_status = "blank_value_flagged"
                field_value_id = insert_row(
                    conn,
                    "db21_tim_raw_field_value",
                    {
                        "field_id": field_id,
                        "ingest_run_id": run_id,
                        "source_inventory_id": selected_tim.source_inventory_id,
                        "tim_record_id": record_id,
                        "record_index": record_index,
                        "line_number": record_index,
                        "field_index": field_index,
                        "field_name": field_name,
                        "raw_value_text": raw_value_text,
                        "raw_value_hash_sha256": sha256_text(raw_value_text),
                        "parse_status": parse_status,
                        "quality_status": field_quality_status,
                        "quarantine_status": quarantine_status,
                        "anomaly_status": anomaly_status,
                        "lineage_key": field_lineage,
                        "ingest_timestamp_utc": timestamp,
                        "created_at_utc": timestamp,
                    },
                )
                counters["tim_raw_field_value_count"] += 1
                if raw_value_text == "":
                    add_quality_flag(
                        conn,
                        ingest_run_id=run_id,
                        source_inventory_id=selected_tim.source_inventory_id,
                        tim_record_id=record_id,
                        tim_field_value_id=field_value_id,
                        flag_scope="field_value",
                        flag_type="blank_value",
                        flag_status="retained",
                        flag_severity="audit_flag",
                        flag_note="Blank raw field value retained.",
                        lineage_key=field_lineage,
                        created_at_utc=timestamp,
                    )
    return dict(counters)


def add_par_field_inventory(conn: sqlite3.Connection, input_db: Path, sources: list[SourceFile], timestamp: str, run_id: str) -> None:
    par_sources = {source.relative_path: source for source in sources if source.source_type == "PAR"}
    if not par_sources:
        return
    src_con = sqlite3.connect(input_db)
    try:
        src_con.row_factory = sqlite3.Row
        for relative_path, source in par_sources.items():
            if source.source_inventory_id is None:
                continue
            rows = src_con.execute(
                """
                SELECT field_name,
                       MIN(field_index) AS field_index,
                       COUNT(*) AS occurrence_count,
                       MIN(line_number) AS first_line_number,
                       MIN(raw_value_text) AS sample_raw_value_text,
                       MIN(parse_status) AS parse_status,
                       MIN(quality_status) AS quality_status,
                       MIN(quarantine_status) AS quarantine_status,
                       MIN(anomaly_status) AS anomaly_status
                FROM qsb_v_db20_raw_field_values
                WHERE relative_path = ?
                GROUP BY field_name
                ORDER BY MIN(field_index), field_name
                """,
                (relative_path,),
            ).fetchall()
            for row in rows:
                field_name = str(row["field_name"])
                field_lineage = lineage(
                    source.source_family_label,
                    source.source_file_name,
                    run_id,
                    int(row["first_line_number"] or 0),
                    f"PAR_FIELD::{field_name}",
                )
                insert_row(
                    conn,
                    "db21_par_tim_field_inventory",
                    {
                        "source_inventory_id": source.source_inventory_id,
                        "source_type": "PAR",
                        "source_family_label": source.source_family_label,
                        "source_file_name": source.source_file_name,
                        "field_index": row["field_index"],
                        "field_name": field_name,
                        "occurrence_count": row["occurrence_count"],
                        "first_line_number": row["first_line_number"],
                        "sample_raw_value_text": row["sample_raw_value_text"],
                        "parse_status": row["parse_status"],
                        "quality_status": row["quality_status"],
                        "quarantine_status": row["quarantine_status"],
                        "anomaly_status": row["anomaly_status"],
                        "lineage_key": field_lineage,
                        "created_at_utc": timestamp,
                    },
                )
    finally:
        src_con.close()


def add_tim_field_inventory(conn: sqlite3.Connection, selected_tim: SourceFile, timestamp: str, run_id: str) -> None:
    if selected_tim.source_inventory_id is None:
        return
    rows = conn.execute(
        """
        SELECT field_name,
               MIN(field_index) AS field_index,
               COUNT(*) AS occurrence_count,
               MIN(line_number) AS first_line_number,
               MIN(raw_value_text) AS sample_raw_value_text,
               MIN(parse_status) AS parse_status,
               MIN(quality_status) AS quality_status,
               MIN(quarantine_status) AS quarantine_status,
               MIN(anomaly_status) AS anomaly_status
        FROM db21_tim_raw_field_value
        WHERE source_inventory_id = ?
        GROUP BY field_name
        ORDER BY MIN(field_index), field_name
        """,
        (selected_tim.source_inventory_id,),
    ).fetchall()
    for row in rows:
        field_name = str(row[0])
        field_lineage = lineage(
            selected_tim.source_family_label,
            selected_tim.source_file_name,
            run_id,
            int(row[3] or 0),
            f"TIM_FIELD::{field_name}",
        )
        insert_row(
            conn,
            "db21_par_tim_field_inventory",
            {
                "source_inventory_id": selected_tim.source_inventory_id,
                "source_type": "TIM",
                "source_family_label": selected_tim.source_family_label,
                "source_file_name": selected_tim.source_file_name,
                "field_index": row[1],
                "field_name": field_name,
                "occurrence_count": row[2],
                "first_line_number": row[3],
                "sample_raw_value_text": row[4],
                "parse_status": row[5],
                "quality_status": row[6],
                "quarantine_status": row[7],
                "anomaly_status": row[8],
                "lineage_key": field_lineage,
                "created_at_utc": timestamp,
            },
        )


def add_joinability(conn: sqlite3.Connection, sources: list[SourceFile], timestamp: str, run_id: str) -> None:
    par_sources = [source for source in sources if source.source_type == "PAR"]
    tim_sources = [source for source in sources if source.source_type == "TIM"]
    for par_source in par_sources:
        for tim_source in tim_sources:
            same_family = int(par_source.source_family_label == tim_source.source_family_label)
            object_match = int(par_source.object_label_candidate == tim_source.object_label_candidate)
            par_dir = str(Path(par_source.relative_path).parent)
            tim_dir = str(Path(tim_source.relative_path).parent)
            shared_context = int(par_dir == tim_dir or Path(par_dir).parent == Path(tim_dir).parent)
            if same_family and object_match:
                status = "source_family_joinable"
            elif shared_context:
                status = "file_context_joinable"
            else:
                status = "unknown"
            notes = (
                "Joinability is documented at source-family/file-context level only; "
                "no direct record-level key was identified or asserted."
            )
            join_lineage = lineage(
                par_source.source_family_label,
                f"{par_source.source_file_name}__{tim_source.source_file_name}",
                run_id,
                0,
                "PAR_TIM_JOINABILITY",
            )
            insert_row(
                conn,
                "db21_par_tim_joinability",
                {
                    "source_family_label": par_source.source_family_label,
                    "par_source_inventory_id": par_source.source_inventory_id,
                    "tim_source_inventory_id": tim_source.source_inventory_id,
                    "par_relative_path": par_source.relative_path,
                    "tim_relative_path": tim_source.relative_path,
                    "same_source_family_label": same_family,
                    "matching_object_label_candidate": object_match,
                    "par_file_present": 1,
                    "tim_file_present": 1,
                    "shared_directory_context": shared_context,
                    "direct_record_level_join_available": 0,
                    "joinability_status": status,
                    "joinability_notes": notes,
                    "lineage_key": join_lineage,
                    "created_at_utc": timestamp,
                },
            )


def table_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return [
        {"table_name": row[0], "row_count": int(conn.execute(f'SELECT COUNT(*) FROM \"{row[0]}\"').fetchone()[0])}
        for row in rows
    ]


def foreign_key_violations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table_name": row[0], "rowid": row[1], "referenced_table": row[2], "fk_id": row[3]}
        for row in rows
    ]


def view_rows(conn: sqlite3.Connection, view: str) -> list[dict[str, Any]]:
    cur = conn.execute(f"SELECT * FROM {view}")
    columns = [item[0] for item in cur.description]
    return [dict(zip(columns, row)) for row in cur.fetchall()]


def write_readout(
    path: Path,
    summary: dict[str, Any],
    dashboard: list[dict[str, Any]],
    human_rows: list[dict[str, Any]],
) -> None:
    dashboard_lines = [f"- {row['metric_name']}: {row['metric_value']}" for row in dashboard]
    sample_lines = [
        "| tim_relative_path | line_number | line_type | field_name | raw_value_text | parse_status | quality_status |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in human_rows[:20]:
        raw_value = str(row["raw_value_text"]).replace("|", "\\|")
        if len(raw_value) > 80:
            raw_value = raw_value[:77] + "..."
        sample_lines.append(
            "| "
            + " | ".join(
                [
                    str(row["tim_relative_path"]),
                    str(row["line_number"]),
                    str(row["line_type"]),
                    str(row["field_name"]),
                    raw_value,
                    str(row["parse_status"]),
                    str(row["quality_status"]),
                ]
            )
            + " |"
        )
    text = "\n".join(
        [
            "# QSB-DB21 PAR/TIM Joinability and First TIM Ingest Readout",
            "",
            "## Befund",
            "",
            f"- Input DB copied from `{summary['input_db_path']}`.",
            f"- Output DB written to `{summary['output_db_path']}`.",
            f"- Selected TIM source: `{summary['selected_tim_source_file']}`.",
            f"- Matching existing PAR source family: {summary['selected_tim_matches_par_family']}.",
            *dashboard_lines,
            "",
            "## Interpretation",
            "",
            "DB21 extends DB20 from PAR-only rawdata contact to PAR/TIM source handling. "
            "TIM records are retained as raw lines, and whitespace tokens are stored as "
            "raw text fields. PAR/TIM joinability is represented only at source-family "
            "and file-context level.",
            "",
            "## Hypothese",
            "",
            "No scientific hypothesis is tested here. DB21 prepares a database substrate "
            "for later gated data-analytic work.",
            "",
            "## Offene Lücke",
            "",
            "- No direct record-level PAR/TIM join key was identified or asserted.",
            "- TIM token names are positional raw token labels, not physical column semantics.",
            "- Quarantine context is preserved as status metadata and does not discard rows.",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## First Human TIM Readout",
            "",
            *sample_lines,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def dry_run(args: argparse.Namespace, output_db: Path) -> int:
    if not args.input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {args.input_db}")
    if not args.source_root.exists():
        raise FileNotFoundError(f"Source root does not exist: {args.source_root}")
    sources = discover_par_tim_sources(args.source_root, args.input_db)
    tim_sources = [source for source in sources if source.source_type == "TIM"]
    if not tim_sources:
        print("No TIM source available for DB21.")
        return 1
    selected_tim = select_tim_source(sources, args.tim_source_file, args.source_root)
    print(f"block: {BLOCK_NAME}")
    print("dry_run: true")
    print(f"input_db: {args.input_db}")
    print(f"output_db: {output_db}")
    print(f"par_file_count: {sum(1 for source in sources if source.source_type == 'PAR')}")
    print(f"tim_file_count: {sum(1 for source in sources if source.source_type == 'TIM')}")
    print(f"selected_tim_source: {selected_tim.relative_path}")
    print("claim_boundary:", CLAIM_BOUNDARY)
    return 0


def run(args: argparse.Namespace) -> int:
    output_root = args.output_root
    output_db = output_db_path(output_root, args.output_db)
    csv_root = output_csv_root(output_root)
    readout_path = output_root / READOUT_NAME
    summary_path = output_root / SUMMARY_NAME
    source_inventory_path = csv_root / SOURCE_INVENTORY_NAME
    field_inventory_path = csv_root / FIELD_INVENTORY_NAME
    joinability_path = csv_root / JOINABILITY_NAME
    table_counts_path = csv_root / TABLE_COUNTS_NAME

    if args.dry_run:
        return dry_run(args, output_db)

    if not args.input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {args.input_db}")
    if not args.source_root.exists():
        raise FileNotFoundError(f"Source root does not exist: {args.source_root}")

    sources = discover_par_tim_sources(args.source_root, args.input_db)
    if not any(source.source_type == "TIM" for source in sources):
        print("No TIM source available for DB21.")
        return 1
    selected_tim = select_tim_source(sources, args.tim_source_file, args.source_root)

    output_root.mkdir(parents=True, exist_ok=True)
    csv_root.mkdir(parents=True, exist_ok=True)
    ensure_no_output_collision(
        [output_db, readout_path, summary_path, source_inventory_path, field_inventory_path, joinability_path, table_counts_path],
        output_db,
        args.overwrite,
    )

    timestamp = utc_now()
    run_suffix = sha256_text(selected_tim.relative_path)[:10]
    run_id = "DB21_" + timestamp.replace("-", "").replace(":", "") + "_" + run_suffix

    shutil.copy2(args.input_db, output_db)
    conn = sqlite3.connect(output_db)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        create_schema(conn)
        create_views(conn)
        insert_sources(conn, sources, selected_tim, timestamp, run_id)

        if selected_tim.source_inventory_id is None:
            raise ValueError("Selected TIM source was not inserted into DB21 source inventory.")
        insert_row(
            conn,
            "db21_tim_ingest_run",
            {
                "ingest_run_id": run_id,
                "ingest_timestamp_utc": timestamp,
                "script_path": SCRIPT_PATH.as_posix(),
                "block_name": BLOCK_NAME,
                "input_db_path": args.input_db.as_posix(),
                "output_db_path": output_db.as_posix(),
                "source_root_path": args.source_root.as_posix(),
                "selected_tim_source_inventory_id": selected_tim.source_inventory_id,
                "selected_tim_relative_path": selected_tim.relative_path,
                "run_status": "running",
                "stop_reason": "not_stopped",
                "claim_boundary": CLAIM_BOUNDARY,
                "warnings_json": "[]",
                "created_at_utc": timestamp,
            },
        )

        counts = ingest_tim(conn, selected_tim, run_id, timestamp)
        add_par_field_inventory(conn, args.input_db, sources, timestamp, run_id)
        add_tim_field_inventory(conn, selected_tim, timestamp, run_id)
        add_joinability(conn, sources, timestamp, run_id)

        fk_rows = foreign_key_violations(conn)
        conn.execute(
            """
            UPDATE db21_tim_ingest_run
            SET tim_raw_record_count = ?,
                tim_raw_field_value_count = ?,
                tim_comment_line_count = ?,
                tim_blank_line_count = ?,
                tim_malformed_or_short_line_count = ?,
                flagged_line_count = ?,
                quarantine_candidate_count = ?,
                anomaly_candidate_count = ?,
                foreign_key_violation_count = ?,
                run_status = ?,
                stop_reason = ?
            WHERE ingest_run_id = ?
            """,
            (
                counts.get("tim_raw_record_count", 0),
                counts.get("tim_raw_field_value_count", 0),
                counts.get("comment_line_count", 0),
                counts.get("blank_line_count", 0),
                counts.get("malformed_or_short_line_count", 0),
                counts.get("flagged_line_count", 0),
                counts.get("quarantine_candidate_count", 0),
                counts.get("anomaly_candidate_count", 0),
                len(fk_rows),
                "completed",
                "completed_par_tim_joinability_first_tim_ingest",
                run_id,
            ),
        )
        conn.commit()

        dashboard = view_rows(conn, "qsb_v_db21_measurement_reality_dashboard")
        source_rows = view_rows(conn, "qsb_v_db21_par_tim_source_inventory")
        field_rows = view_rows(conn, "qsb_v_db21_par_tim_field_inventory")
        join_rows = view_rows(conn, "qsb_v_db21_par_tim_joinability")
        human_rows = view_rows(conn, "qsb_v_db21_first_human_tim_readout")[:30]
        table_rows = table_counts(conn)
    finally:
        conn.close()

    par_file_count = sum(1 for source in sources if source.source_type == "PAR")
    tim_file_count = sum(1 for source in sources if source.source_type == "TIM")
    selected_tim_matches_par_family = any(
        source.source_type == "PAR"
        and source.source_family_label == selected_tim.source_family_label
        and source.object_label_candidate == selected_tim.object_label_candidate
        for source in sources
    )
    join_status = join_rows[0]["joinability_status"] if join_rows else "unknown"
    join_notes = join_rows[0]["joinability_notes"] if join_rows else "No PAR/TIM joinability row was created."
    summary = {
        "block_name": BLOCK_NAME,
        "script_path": SCRIPT_PATH.as_posix(),
        "input_db_path": args.input_db.as_posix(),
        "output_db_path": output_db.as_posix(),
        "output_root": output_root.as_posix(),
        "csv_output_root": csv_root.as_posix(),
        "source_root_path": args.source_root.as_posix(),
        "ingest_run_id": run_id,
        "ingest_timestamp_utc": timestamp,
        "par_file_count": par_file_count,
        "tim_file_count": tim_file_count,
        "ingested_tim_file_count": 1,
        "selected_tim_source_file": selected_tim.relative_path,
        "selected_tim_matches_par_family": selected_tim_matches_par_family,
        "selected_tim_structure": {
            "line_count": selected_tim.line_count,
            "blank_line_count": selected_tim.blank_line_count,
            "nonblank_line_count": selected_tim.nonblank_line_count,
            "first_structural_lines": selected_tim.first_structural_lines,
        },
        "tim_raw_record_count": counts.get("tim_raw_record_count", 0),
        "tim_raw_field_value_count": counts.get("tim_raw_field_value_count", 0),
        "tim_comment_line_count": counts.get("comment_line_count", 0),
        "tim_blank_line_count": counts.get("blank_line_count", 0),
        "tim_malformed_or_short_line_count": counts.get("malformed_or_short_line_count", 0),
        "flagged_line_count": counts.get("flagged_line_count", 0),
        "quarantine_candidate_count": counts.get("quarantine_candidate_count", 0),
        "anomaly_candidate_count": counts.get("anomaly_candidate_count", 0),
        "par_tim_joinability_status": join_status,
        "par_tim_joinability_notes": join_notes,
        "foreign_key_violation_count": len(fk_rows),
        "foreign_key_violations": fk_rows,
        "claim_boundary": CLAIM_BOUNDARY,
        "limitations": [
            "No timing analysis was performed.",
            "No residual analysis was performed.",
            "No model fitting was performed.",
            "No statistical inference was performed.",
            "No Shapiro confirmation, QSB validation, or Bridge claim is made.",
        ],
    }

    write_csv(source_inventory_path, list(source_rows[0].keys()) if source_rows else [], source_rows)
    write_csv(field_inventory_path, list(field_rows[0].keys()) if field_rows else [], field_rows)
    write_csv(joinability_path, list(join_rows[0].keys()) if join_rows else [], join_rows)
    write_csv(table_counts_path, ["table_name", "row_count"], table_rows)
    write_json(summary_path, summary)
    write_readout(readout_path, summary, dashboard, human_rows)

    print(f"block: {BLOCK_NAME}")
    print(f"output_db: {output_db}")
    print(f"selected_tim_source_file: {selected_tim.relative_path}")
    print(f"par_file_count: {par_file_count}")
    print(f"tim_file_count: {tim_file_count}")
    print(f"tim_raw_record_count: {counts.get('tim_raw_record_count', 0)}")
    print(f"tim_raw_field_value_count: {counts.get('tim_raw_field_value_count', 0)}")
    print(f"foreign_key_violation_count: {len(fk_rows)}")
    print("claim_boundary:", CLAIM_BOUNDARY)
    return 0


def main() -> int:
    return run(parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
