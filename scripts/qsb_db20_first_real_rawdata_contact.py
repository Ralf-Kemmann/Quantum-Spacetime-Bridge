#!/usr/bin/env python3
"""QSB-DB20 first real rawdata contact and mini-DWH ingest.

This script copies the DB18 synthetic sample database into a DB20 output
database, inventories real local source files, ingests a deterministic raw
TIM/PAR-like representative as raw text, and adds audit-oriented DB20 tables
and views. It does not perform residual analysis, model fitting, statistical
inference, or physical interpretation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCK_NAME = "QSB-DB20_FIRST_REAL_RAWDATA_CONTACT"
SCRIPT_PATH = Path("scripts/qsb_db20_first_real_rawdata_contact.py")
DEFAULT_INPUT_DB = Path(
    "runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db"
)
DEFAULT_SOURCE_ROOT = Path("data/QSB-ST-SHAPIROINFO/public_sources")
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB20_FIRST_REAL_RAWDATA_CONTACT")
DEFAULT_OUTPUT_DB_NAME = "qsb_research_real_rawdata_contact.db"

READOUT_NAME = "db20_real_rawdata_contact_readout.md"
SUMMARY_NAME = "db20_real_rawdata_contact_summary.json"
SOURCE_INVENTORY_NAME = "db20_real_rawdata_source_inventory.csv"
TABLE_COUNTS_NAME = "db20_real_rawdata_table_counts.csv"

TEXT_EXTENSIONS = {
    ".csv",
    ".json",
    ".log",
    ".md",
    ".par",
    ".sha256",
    ".tim",
    ".tsv",
    ".txt",
    ".yaml",
    ".yml",
}
INGEST_CANDIDATE_EXTENSIONS = {".par", ".tim"}
SNIPPET_LIMIT = 160

CLAIM_BOUNDARY = (
    "DB20 is a rawdata contact and audit-representation step only. It does not "
    "validate QSB, ShapiroInfo, the Bridge, or any physical hypothesis. It does "
    "not perform residual analysis, model fitting, statistical inference, or "
    "physical interpretation."
)


@dataclass
class SourceFile:
    path: Path
    relative_path: str
    source_id: str
    source_label: str
    file_name: str
    extension: str
    size_bytes: int | None
    mtime_utc: str | None
    sha256: str | None = None
    apparent_type: str = "unknown"
    readability_status: str = "not_checked"
    line_count: int | None = None
    blank_line_count: int | None = None
    nonblank_line_count: int | None = None
    first_structural_lines: list[str] = field(default_factory=list)
    structure_kind: str = "metadata_only"
    ingest_candidate_status: str = "not_candidate"
    selected_for_ingest: int = 0
    quarantine_status: str = "not_quarantined"
    quarantine_note: str = ""
    warning: str = ""
    db_file_id: int | None = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Copy DB18, inventory real raw source files, ingest raw text records "
            "into DB20 audit tables, create views, and write DB20 readouts."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help=f"DB18 base DB. Default: {DEFAULT_INPUT_DB}",
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
        help=f"DB20 output root. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    parser.add_argument(
        "--output-db",
        type=Path,
        default=None,
        help=f"Output DB path. Default: <output-root>/{DEFAULT_OUTPUT_DB_NAME}",
    )
    parser.add_argument(
        "--source-file",
        type=Path,
        action="append",
        default=[],
        help=(
            "Optional real source file to ingest. May be supplied more than once. "
            "Relative paths are resolved against --source-root."
        ),
    )
    parser.add_argument(
        "--ingest-all-candidates",
        action="store_true",
        help="Ingest all readable .par/.tim candidates instead of the first deterministic candidate.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite DB20 output files if they already exist.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned paths and candidate selection without creating files.",
    )
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def mtime_utc(path: Path) -> str | None:
    try:
        return (
            datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )
    except OSError:
        return None


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


def apparent_type(extension: str) -> str:
    if extension == ".par":
        return "parameter_text"
    if extension == ".tim":
        return "timing_text"
    if extension in {".yaml", ".yml"}:
        return "yaml_metadata_text"
    if extension == ".json":
        return "json_text"
    if extension in {".md", ".txt", ".log"}:
        return "plain_text"
    if extension == ".sha256":
        return "checksum_text"
    if extension == ".csv":
        return "csv_text"
    if extension == ".tsv":
        return "tsv_text"
    if extension:
        return "unsupported_by_extension"
    return "unsupported_no_extension"


def structure_kind(extension: str) -> str:
    if extension == ".par":
        return "line_based_parameter_key_value_like"
    if extension == ".tim":
        return "line_based_timing_whitespace_records"
    if extension in {".yaml", ".yml"}:
        return "metadata_key_value_text"
    if extension == ".sha256":
        return "checksum_line_text"
    if extension in TEXT_EXTENSIONS:
        return "line_based_text"
    return "metadata_only"


def source_label_for(relative_path: str) -> str:
    parts = Path(relative_path).parts
    return parts[0] if parts else "source_root"


def snippet(line: str) -> str:
    compact = " ".join(line.strip().split())
    if len(compact) <= SNIPPET_LIMIT:
        return compact
    return compact[: SNIPPET_LIMIT - 3] + "..."


def scan_text_shape(path: Path) -> tuple[str, int | None, int | None, int | None, list[str], str]:
    line_count = 0
    blank_line_count = 0
    first_lines: list[str] = []
    warning = ""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                line_count += 1
                raw_line = line.rstrip("\n")
                if not raw_line.strip():
                    blank_line_count += 1
                elif len(first_lines) < 5:
                    first_lines.append(snippet(raw_line))
    except OSError as exc:
        return "read_failed", None, None, None, [], f"{type(exc).__name__}: {exc}"

    nonblank_line_count = line_count - blank_line_count
    return "readable_text", line_count, blank_line_count, nonblank_line_count, first_lines, warning


def parse_simple_manifest_flags(path: Path) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """Extract simple YAML-like flags without requiring a YAML dependency."""
    top_level: dict[str, str] = {}
    by_local_path: dict[str, dict[str, str]] = {}
    keys_of_interest = {
        "quarantine_status",
        "analysis_allowed",
        "par_tim_ingestion_allowed",
        "sidecar_population_allowed",
        "adapter_execution_allowed",
        "residual_calculation_allowed",
        "raw_data_commit_allowed",
    }
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return top_level, by_local_path

    for raw_line in lines:
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip().lstrip("-").strip()
        value = value.strip().strip('"').strip("'")
        if key in keys_of_interest:
            top_level[key] = value
        elif key == "local_path" and value:
            by_local_path[value] = dict(top_level)
    return top_level, by_local_path


def quarantine_context(source_root: Path) -> dict[str, dict[str, str]]:
    context: dict[str, dict[str, str]] = {}
    manifest_paths = sorted(
        [
            path
            for path in source_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".yaml", ".yml"}
        ],
        key=lambda p: p.as_posix(),
    )
    for manifest_path in manifest_paths:
        top_level, by_local_path = parse_simple_manifest_flags(manifest_path)
        if not top_level:
            continue
        for local_path, flags in by_local_path.items():
            path_obj = Path(local_path)
            try:
                rel = path_obj.relative_to(source_root)
            except ValueError:
                try:
                    rel = path_obj.relative_to(Path("."))
                except ValueError:
                    rel = path_obj
                try:
                    rel = rel.relative_to(source_root)
                except ValueError:
                    pass
            context[rel.as_posix()] = {
                "manifest_path": manifest_path.as_posix(),
                **flags,
            }
    return context


def inventory_sources(source_root: Path) -> list[SourceFile]:
    quarantine_by_path = quarantine_context(source_root)
    files: list[SourceFile] = []
    for path in sorted([p for p in source_root.rglob("*") if p.is_file()], key=lambda p: p.as_posix()):
        try:
            relative_path = path.relative_to(source_root).as_posix()
        except ValueError:
            relative_path = path.as_posix()
        extension = path.suffix.lower()
        source_label = source_label_for(relative_path)
        size_bytes: int | None
        try:
            size_bytes = path.stat().st_size
        except OSError:
            size_bytes = None

        source = SourceFile(
            path=path,
            relative_path=relative_path,
            source_id=source_label,
            source_label=source_label,
            file_name=path.name,
            extension=extension,
            size_bytes=size_bytes,
            mtime_utc=mtime_utc(path),
            apparent_type=apparent_type(extension),
            structure_kind=structure_kind(extension),
        )

        try:
            source.sha256 = sha256_file(path)
        except OSError as exc:
            source.warning = f"sha256_failed: {type(exc).__name__}: {exc}"

        if extension in TEXT_EXTENSIONS:
            (
                source.readability_status,
                source.line_count,
                source.blank_line_count,
                source.nonblank_line_count,
                source.first_structural_lines,
                read_warning,
            ) = scan_text_shape(path)
            if read_warning:
                source.warning = "; ".join([part for part in [source.warning, read_warning] if part])
        else:
            source.readability_status = "unsupported_by_extension"

        if extension in INGEST_CANDIDATE_EXTENSIONS and source.readability_status == "readable_text":
            source.ingest_candidate_status = "candidate_tim_par_text"

        qctx = quarantine_by_path.get(relative_path)
        if qctx:
            source.quarantine_status = "source_quarantine_context"
            flags = [
                f"manifest={qctx.get('manifest_path', '')}",
                f"quarantine_status={qctx.get('quarantine_status', '')}",
                f"analysis_allowed={qctx.get('analysis_allowed', '')}",
                f"par_tim_ingestion_allowed={qctx.get('par_tim_ingestion_allowed', '')}",
                f"residual_calculation_allowed={qctx.get('residual_calculation_allowed', '')}",
            ]
            source.quarantine_note = "; ".join(flag for flag in flags if not flag.endswith("="))

        files.append(source)
    return files


def select_ingest_files(
    inventory: list[SourceFile],
    source_root: Path,
    requested_files: list[Path],
    ingest_all_candidates: bool,
) -> list[SourceFile]:
    by_path = {source.path.resolve(): source for source in inventory}
    by_relative = {source.relative_path: source for source in inventory}

    if requested_files:
        selected: list[SourceFile] = []
        for requested in requested_files:
            candidate_path = requested if requested.is_absolute() else source_root / requested
            resolved = candidate_path.resolve()
            source = by_path.get(resolved)
            if source is None:
                source = by_relative.get(requested.as_posix())
            if source is None:
                raise FileNotFoundError(f"Requested source file not inventoried: {requested}")
            if source.readability_status != "readable_text":
                raise ValueError(f"Requested source file is not readable text: {source.relative_path}")
            selected.append(source)
        return selected

    candidates = [
        source
        for source in inventory
        if source.ingest_candidate_status == "candidate_tim_par_text" and source.size_bytes is not None
    ]
    candidates.sort(key=lambda source: (int(source.size_bytes or 0), source.relative_path))
    if ingest_all_candidates:
        return candidates
    return candidates[:1]


def ensure_no_existing_outputs(output_paths: list[Path], overwrite: bool) -> None:
    existing = [path for path in output_paths if path.exists()]
    if existing and not overwrite:
        joined = "\n".join(path.as_posix() for path in existing)
        raise FileExistsError(
            "DB20 output file(s) already exist. Use --overwrite only when replacing "
            f"DB20 outputs intentionally:\n{joined}"
        )


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def source_inventory_rows(inventory: list[SourceFile]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in sorted(inventory, key=lambda item: item.relative_path):
        rows.append(
            {
                "db20_source_file_id": source.db_file_id,
                "source_id": source.source_id,
                "source_label": source.source_label,
                "source_path": source.path.as_posix(),
                "relative_path": source.relative_path,
                "source_file_name": source.file_name,
                "source_extension": source.extension,
                "source_file_size_bytes": source.size_bytes,
                "source_file_mtime_utc": source.mtime_utc,
                "source_file_hash_sha256": source.sha256,
                "apparent_type": source.apparent_type,
                "structure_kind": source.structure_kind,
                "readability_status": source.readability_status,
                "line_count": source.line_count,
                "blank_line_count": source.blank_line_count,
                "nonblank_line_count": source.nonblank_line_count,
                "first_structural_lines": " || ".join(source.first_structural_lines),
                "ingest_candidate_status": source.ingest_candidate_status,
                "selected_for_ingest": source.selected_for_ingest,
                "quarantine_status": source.quarantine_status,
                "quarantine_note": source.quarantine_note,
                "warning": source.warning,
            }
        )
    return rows


def insert_row(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> int:
    columns = list(values)
    placeholders = ", ".join(["?"] * len(columns))
    quoted = ", ".join(columns)
    sql = f"INSERT INTO {table} ({quoted}) VALUES ({placeholders})"
    cursor = conn.execute(sql, [values[column] for column in columns])
    return int(cursor.lastrowid)


def create_db20_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS db20_rawdata_file_inventory (
            source_file_id INTEGER PRIMARY KEY,
            source_id TEXT NOT NULL,
            source_label TEXT NOT NULL,
            source_path TEXT NOT NULL,
            relative_path TEXT NOT NULL UNIQUE,
            source_file_name TEXT NOT NULL,
            source_extension TEXT,
            source_file_size_bytes INTEGER,
            source_file_mtime_utc TEXT,
            source_file_hash_sha256 TEXT,
            apparent_type TEXT,
            structure_kind TEXT,
            readability_status TEXT NOT NULL,
            line_count INTEGER,
            blank_line_count INTEGER,
            nonblank_line_count INTEGER,
            first_structural_lines TEXT,
            ingest_candidate_status TEXT NOT NULL,
            selected_for_ingest INTEGER NOT NULL DEFAULT 0,
            quarantine_status TEXT NOT NULL DEFAULT 'not_quarantined',
            quarantine_note TEXT,
            warning TEXT,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db20_rawdata_ingest_run (
            ingest_run_id TEXT PRIMARY KEY,
            ingest_timestamp_utc TEXT NOT NULL,
            script_path TEXT NOT NULL,
            block_name TEXT NOT NULL,
            input_db_path TEXT NOT NULL,
            output_db_path TEXT NOT NULL,
            source_root_path TEXT NOT NULL,
            selection_mode TEXT NOT NULL,
            selected_file_count INTEGER NOT NULL,
            inventoried_file_count INTEGER NOT NULL,
            raw_record_count INTEGER NOT NULL DEFAULT 0,
            raw_field_value_count INTEGER NOT NULL DEFAULT 0,
            blank_value_count INTEGER NOT NULL DEFAULT 0,
            malformed_or_flagged_count INTEGER NOT NULL DEFAULT 0,
            quarantine_candidate_count INTEGER NOT NULL DEFAULT 0,
            anomaly_candidate_count INTEGER NOT NULL DEFAULT 0,
            foreign_key_violation_count INTEGER NOT NULL DEFAULT 0,
            run_status TEXT NOT NULL,
            stop_reason TEXT NOT NULL,
            claim_boundary TEXT NOT NULL,
            warnings_json TEXT NOT NULL DEFAULT '[]',
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS db20_rawdata_record (
            record_id TEXT PRIMARY KEY,
            ingest_run_id TEXT NOT NULL,
            source_file_id INTEGER NOT NULL,
            source_id TEXT NOT NULL,
            source_label TEXT NOT NULL,
            source_path TEXT NOT NULL,
            source_file_name TEXT NOT NULL,
            record_index INTEGER NOT NULL,
            line_number INTEGER NOT NULL,
            raw_record_text TEXT NOT NULL,
            raw_record_hash_sha256 TEXT NOT NULL,
            record_length_chars INTEGER NOT NULL,
            record_structure_class TEXT NOT NULL,
            parse_status TEXT NOT NULL,
            quality_status TEXT NOT NULL,
            quarantine_status TEXT NOT NULL,
            anomaly_status TEXT NOT NULL,
            lineage_key TEXT NOT NULL UNIQUE,
            ingest_timestamp_utc TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (ingest_run_id) REFERENCES db20_rawdata_ingest_run(ingest_run_id),
            FOREIGN KEY (source_file_id) REFERENCES db20_rawdata_file_inventory(source_file_id)
        );

        CREATE TABLE IF NOT EXISTS db20_rawdata_field_value (
            field_value_id INTEGER PRIMARY KEY,
            field_id TEXT NOT NULL,
            ingest_run_id TEXT NOT NULL,
            source_file_id INTEGER NOT NULL,
            record_id TEXT NOT NULL,
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
            FOREIGN KEY (ingest_run_id) REFERENCES db20_rawdata_ingest_run(ingest_run_id),
            FOREIGN KEY (source_file_id) REFERENCES db20_rawdata_file_inventory(source_file_id),
            FOREIGN KEY (record_id) REFERENCES db20_rawdata_record(record_id)
        );

        CREATE TABLE IF NOT EXISTS db20_rawdata_quality_flag (
            quality_flag_id INTEGER PRIMARY KEY,
            ingest_run_id TEXT NOT NULL,
            source_file_id INTEGER NOT NULL,
            record_id TEXT,
            field_value_id INTEGER,
            flag_scope TEXT NOT NULL,
            flag_type TEXT NOT NULL,
            flag_status TEXT NOT NULL,
            flag_severity TEXT NOT NULL,
            flag_note TEXT,
            lineage_key TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (ingest_run_id) REFERENCES db20_rawdata_ingest_run(ingest_run_id),
            FOREIGN KEY (source_file_id) REFERENCES db20_rawdata_file_inventory(source_file_id),
            FOREIGN KEY (record_id) REFERENCES db20_rawdata_record(record_id),
            FOREIGN KEY (field_value_id) REFERENCES db20_rawdata_field_value(field_value_id)
        );
        """
    )


def create_db20_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP VIEW IF EXISTS qsb_v_db20_source_inventory;
        CREATE VIEW qsb_v_db20_source_inventory AS
        SELECT
            source_file_id,
            source_id,
            source_label,
            source_path,
            relative_path,
            source_file_name,
            source_extension,
            source_file_size_bytes,
            source_file_mtime_utc,
            source_file_hash_sha256,
            apparent_type,
            structure_kind,
            readability_status,
            line_count,
            blank_line_count,
            nonblank_line_count,
            ingest_candidate_status,
            selected_for_ingest,
            quarantine_status,
            quarantine_note,
            warning
        FROM db20_rawdata_file_inventory;

        DROP VIEW IF EXISTS qsb_v_db20_raw_records;
        CREATE VIEW qsb_v_db20_raw_records AS
        SELECT
            r.record_id,
            r.ingest_run_id,
            r.source_file_id,
            f.relative_path,
            r.source_file_name,
            r.record_index,
            r.line_number,
            r.raw_record_text,
            r.record_structure_class,
            r.parse_status,
            r.quality_status,
            r.quarantine_status,
            r.anomaly_status,
            r.lineage_key
        FROM db20_rawdata_record r
        JOIN db20_rawdata_file_inventory f
          ON f.source_file_id = r.source_file_id;

        DROP VIEW IF EXISTS qsb_v_db20_raw_field_values;
        CREATE VIEW qsb_v_db20_raw_field_values AS
        SELECT
            fv.field_value_id,
            fv.field_id,
            fv.ingest_run_id,
            fv.source_file_id,
            f.relative_path,
            fv.record_id,
            fv.record_index,
            fv.line_number,
            fv.field_index,
            fv.field_name,
            fv.raw_value_text,
            fv.raw_value_hash_sha256,
            fv.parse_status,
            fv.quality_status,
            fv.quarantine_status,
            fv.anomaly_status,
            fv.lineage_key
        FROM db20_rawdata_field_value fv
        JOIN db20_rawdata_file_inventory f
          ON f.source_file_id = fv.source_file_id;

        DROP VIEW IF EXISTS qsb_v_db20_quality_dashboard;
        CREATE VIEW qsb_v_db20_quality_dashboard AS
        SELECT
            'record' AS object_scope,
            parse_status,
            quality_status,
            quarantine_status,
            anomaly_status,
            COUNT(*) AS object_count
        FROM db20_rawdata_record
        GROUP BY parse_status, quality_status, quarantine_status, anomaly_status
        UNION ALL
        SELECT
            'field_value' AS object_scope,
            parse_status,
            quality_status,
            quarantine_status,
            anomaly_status,
            COUNT(*) AS object_count
        FROM db20_rawdata_field_value
        GROUP BY parse_status, quality_status, quarantine_status, anomaly_status;

        DROP VIEW IF EXISTS qsb_v_db20_measurement_reality_dashboard;
        CREATE VIEW qsb_v_db20_measurement_reality_dashboard AS
        SELECT 'inventoried_file_count' AS metric_name, COUNT(*) AS metric_value
        FROM db20_rawdata_file_inventory
        UNION ALL
        SELECT 'ingested_file_count', COUNT(*)
        FROM db20_rawdata_file_inventory
        WHERE selected_for_ingest = 1
        UNION ALL
        SELECT 'raw_record_count', COUNT(*)
        FROM db20_rawdata_record
        UNION ALL
        SELECT 'raw_field_value_count', COUNT(*)
        FROM db20_rawdata_field_value
        UNION ALL
        SELECT 'blank_value_count', COUNT(*)
        FROM db20_rawdata_field_value
        WHERE raw_value_text = ''
        UNION ALL
        SELECT 'malformed_or_flagged_count', COUNT(*)
        FROM db20_rawdata_quality_flag
        WHERE flag_type IN (
            'blank_record',
            'blank_value',
            'malformed_like',
            'source_flag_marker_present',
            'source_quarantine_context'
        )
        UNION ALL
        SELECT 'quarantine_candidate_count', COUNT(*)
        FROM db20_rawdata_record
        WHERE quarantine_status <> 'not_quarantined'
        UNION ALL
        SELECT 'anomaly_candidate_count', COUNT(*)
        FROM db20_rawdata_record
        WHERE anomaly_status <> 'not_evaluated'
        UNION ALL
        SELECT 'foreign_key_violation_count', COALESCE(MAX(foreign_key_violation_count), 0)
        FROM db20_rawdata_ingest_run;

        DROP VIEW IF EXISTS qsb_v_db20_first_human_readout;
        CREATE VIEW qsb_v_db20_first_human_readout AS
        SELECT
            f.relative_path,
            r.record_index,
            r.line_number,
            fv.field_index,
            fv.field_name,
            substr(fv.raw_value_text, 1, 160) AS raw_value_text,
            fv.parse_status,
            fv.quality_status,
            fv.quarantine_status,
            fv.anomaly_status,
            fv.lineage_key
        FROM db20_rawdata_field_value fv
        JOIN db20_rawdata_record r
          ON r.record_id = fv.record_id
        JOIN db20_rawdata_file_inventory f
          ON f.source_file_id = fv.source_file_id
        ORDER BY f.relative_path, r.record_index, fv.field_index;
        """
    )


def row_structure(source: SourceFile, line: str) -> tuple[str, str, str, str, str]:
    stripped = line.strip()
    if not stripped:
        return (
            "blank",
            "blank_record",
            "blank_record_flagged",
            "quarantine_candidate" if source.quarantine_status == "not_quarantined" else source.quarantine_status,
            "not_evaluated",
        )

    if source.extension == ".par":
        name, value = parse_par_parameter(line)
        if name and value != "":
            return (
                "par_key_value_like",
                "parsed_key_value_like",
                "raw_preserved",
                source.quarantine_status,
                "not_evaluated",
            )
        if name and value == "":
            return (
                "par_key_with_blank_value",
                "parsed_key_blank_value",
                "blank_value_flagged",
                "quarantine_candidate" if source.quarantine_status == "not_quarantined" else source.quarantine_status,
                "not_evaluated",
            )
        return (
            "malformed_like",
            "malformed_like",
            "malformed_flagged",
            "quarantine_candidate" if source.quarantine_status == "not_quarantined" else source.quarantine_status,
            "structure_flagged",
        )

    if source.extension == ".tim":
        tokens = stripped.split()
        upper = stripped.upper()
        source_flag = upper == "C" or upper.startswith("C ") or " -CUT " in f" {upper} "
        if source_flag:
            return (
                "tim_source_flagged_or_cut_like",
                "parsed_source_flagged_record_like",
                "source_flagged_raw_preserved",
                "quarantine_candidate" if source.quarantine_status == "not_quarantined" else source.quarantine_status,
                "source_flag_marker_present",
            )
        if any(char.isalpha() for char in stripped) and not any(char.isdigit() for char in stripped):
            return (
                "tim_header_like",
                "parsed_header_like",
                "raw_preserved",
                source.quarantine_status,
                "not_evaluated",
            )
        if len(tokens) >= 2 and any(char.isdigit() for char in stripped):
            return (
                "tim_data_like",
                "parsed_whitespace_record_like",
                "raw_preserved",
                source.quarantine_status,
                "not_evaluated",
            )
        return (
            "malformed_like",
            "malformed_like",
            "malformed_flagged",
            "quarantine_candidate" if source.quarantine_status == "not_quarantined" else source.quarantine_status,
            "structure_flagged",
        )

    return (
        "text_line",
        "parsed_line_text",
        "raw_preserved",
        source.quarantine_status,
        "not_evaluated",
    )


def parse_par_parameter(line: str) -> tuple[str | None, str]:
    stripped = line.strip()
    if not stripped:
        return None, ""
    if "=" in stripped:
        name, value = stripped.split("=", 1)
        return name.strip() or None, value.strip()
    if ":" in stripped:
        name, value = stripped.split(":", 1)
        return name.strip() or None, value.strip()
    parts = stripped.split(maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip() or None, parts[1].strip()
    if len(parts) == 1:
        return parts[0].strip() or None, ""
    return None, ""


def field_rows_for_line(source: SourceFile, line: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = [("raw_line_text", line)]
    stripped = line.strip()
    if not stripped:
        return rows

    if source.extension == ".par":
        name, value = parse_par_parameter(line)
        if name is not None:
            rows.append(("par_parameter_name", name))
            rows.append((name, value))
            for token_index, token in enumerate(value.split(), start=1):
                rows.append((f"par_value_token_{token_index:03d}", token))
            return rows

    tokens = stripped.split()
    for token_index, token in enumerate(tokens, start=1):
        rows.append((f"token_{token_index:03d}", token))
    if source.extension == ".tim":
        option_index = 0
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token.startswith("-"):
                option_index += 1
                value = ""
                if index + 1 < len(tokens) and not tokens[index + 1].startswith("-"):
                    value = tokens[index + 1]
                field_name = f"tim_option_{token.lstrip('-') or option_index}"
                rows.append((field_name, value))
            index += 1
    return rows


def lineage_key(
    source_label: str,
    file_label: str,
    ingest_run_id: str,
    record_index: int,
    field_label: str,
) -> str:
    return (
        f"SRC::{source_label}::FILE::{file_label}::RUN::{ingest_run_id}"
        f"::REC::{record_index}::FIELD::{field_label}"
    )


def safe_field_label(name: str, field_index: int) -> str:
    compact = "_".join(name.strip().split()) or "blank_field_name"
    return f"{field_index:04d}_{compact}"


def add_quality_flag(
    conn: sqlite3.Connection,
    *,
    ingest_run_id: str,
    source_file_id: int,
    record_id: str | None,
    field_value_id: int | None,
    flag_scope: str,
    flag_type: str,
    flag_status: str,
    flag_severity: str,
    flag_note: str,
    lineage: str,
    created_at_utc: str,
) -> None:
    insert_row(
        conn,
        "db20_rawdata_quality_flag",
        {
            "ingest_run_id": ingest_run_id,
            "source_file_id": source_file_id,
            "record_id": record_id,
            "field_value_id": field_value_id,
            "flag_scope": flag_scope,
            "flag_type": flag_type,
            "flag_status": flag_status,
            "flag_severity": flag_severity,
            "flag_note": flag_note,
            "lineage_key": lineage,
            "created_at_utc": created_at_utc,
        },
    )


def ingest_file(
    conn: sqlite3.Connection,
    source: SourceFile,
    ingest_run_id: str,
    ingest_timestamp_utc: str,
) -> dict[str, int]:
    if source.db_file_id is None:
        raise ValueError(f"Missing DB file id for source: {source.relative_path}")

    counts = {
        "raw_record_count": 0,
        "raw_field_value_count": 0,
        "blank_value_count": 0,
        "malformed_or_flagged_count": 0,
        "quarantine_candidate_count": 0,
        "anomaly_candidate_count": 0,
    }

    with source.path.open("r", encoding="utf-8", errors="replace") as handle:
        for record_index, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\n")
            (
                record_structure_class,
                parse_status,
                quality_status,
                quarantine_status,
                anomaly_status,
            ) = row_structure(source, line)
            record_id = (
                f"DB20_REC_{source.db_file_id}_{record_index:08d}_"
                f"{sha256_text(source.relative_path + ':' + str(record_index))[:12]}"
            )
            record_lineage = lineage_key(
                source.source_label,
                source.file_name,
                ingest_run_id,
                record_index,
                "RECORD",
            )
            insert_row(
                conn,
                "db20_rawdata_record",
                {
                    "record_id": record_id,
                    "ingest_run_id": ingest_run_id,
                    "source_file_id": source.db_file_id,
                    "source_id": source.source_id,
                    "source_label": source.source_label,
                    "source_path": source.path.as_posix(),
                    "source_file_name": source.file_name,
                    "record_index": record_index,
                    "line_number": record_index,
                    "raw_record_text": line,
                    "raw_record_hash_sha256": sha256_text(line),
                    "record_length_chars": len(line),
                    "record_structure_class": record_structure_class,
                    "parse_status": parse_status,
                    "quality_status": quality_status,
                    "quarantine_status": quarantine_status,
                    "anomaly_status": anomaly_status,
                    "lineage_key": record_lineage,
                    "ingest_timestamp_utc": ingest_timestamp_utc,
                    "created_at_utc": ingest_timestamp_utc,
                },
            )
            counts["raw_record_count"] += 1
            if quarantine_status != "not_quarantined":
                counts["quarantine_candidate_count"] += 1
            if anomaly_status != "not_evaluated":
                counts["anomaly_candidate_count"] += 1
            if (
                parse_status in {"blank_record", "malformed_like"}
                or quality_status != "raw_preserved"
                or anomaly_status != "not_evaluated"
                or quarantine_status != "not_quarantined"
            ):
                counts["malformed_or_flagged_count"] += 1

            if source.quarantine_status != "not_quarantined":
                add_quality_flag(
                    conn,
                    ingest_run_id=ingest_run_id,
                    source_file_id=source.db_file_id,
                    record_id=record_id,
                    field_value_id=None,
                    flag_scope="record",
                    flag_type="source_quarantine_context",
                    flag_status=source.quarantine_status,
                    flag_severity="context",
                    flag_note=source.quarantine_note,
                    lineage=record_lineage,
                    created_at_utc=ingest_timestamp_utc,
                )
            if parse_status == "blank_record":
                add_quality_flag(
                    conn,
                    ingest_run_id=ingest_run_id,
                    source_file_id=source.db_file_id,
                    record_id=record_id,
                    field_value_id=None,
                    flag_scope="record",
                    flag_type="blank_record",
                    flag_status="retained",
                    flag_severity="audit_flag",
                    flag_note="Blank raw record retained.",
                    lineage=record_lineage,
                    created_at_utc=ingest_timestamp_utc,
                )
            if parse_status == "malformed_like":
                add_quality_flag(
                    conn,
                    ingest_run_id=ingest_run_id,
                    source_file_id=source.db_file_id,
                    record_id=record_id,
                    field_value_id=None,
                    flag_scope="record",
                    flag_type="malformed_like",
                    flag_status="retained",
                    flag_severity="audit_flag",
                    flag_note="Malformed-like raw record retained without deletion.",
                    lineage=record_lineage,
                    created_at_utc=ingest_timestamp_utc,
                )
            if anomaly_status == "source_flag_marker_present":
                add_quality_flag(
                    conn,
                    ingest_run_id=ingest_run_id,
                    source_file_id=source.db_file_id,
                    record_id=record_id,
                    field_value_id=None,
                    flag_scope="record",
                    flag_type="source_flag_marker_present",
                    flag_status="retained",
                    flag_severity="source_flag",
                    flag_note="Source record contains a structural flag marker such as C or -cut.",
                    lineage=record_lineage,
                    created_at_utc=ingest_timestamp_utc,
                )

            for field_index, (field_name, raw_value_text) in enumerate(field_rows_for_line(source, line), start=1):
                field_label = safe_field_label(field_name, field_index)
                value_quality_status = "raw_preserved"
                value_parse_status = parse_status
                value_anomaly_status = anomaly_status
                value_quarantine_status = quarantine_status
                if raw_value_text == "":
                    value_quality_status = "blank_value_flagged"
                    counts["blank_value_count"] += 1

                field_lineage = lineage_key(
                    source.source_label,
                    source.file_name,
                    ingest_run_id,
                    record_index,
                    field_label,
                )
                field_value_id = insert_row(
                    conn,
                    "db20_rawdata_field_value",
                    {
                        "field_id": field_label,
                        "ingest_run_id": ingest_run_id,
                        "source_file_id": source.db_file_id,
                        "record_id": record_id,
                        "record_index": record_index,
                        "line_number": record_index,
                        "field_index": field_index,
                        "field_name": field_name,
                        "raw_value_text": raw_value_text,
                        "raw_value_hash_sha256": sha256_text(raw_value_text),
                        "parse_status": value_parse_status,
                        "quality_status": value_quality_status,
                        "quarantine_status": value_quarantine_status,
                        "anomaly_status": value_anomaly_status,
                        "lineage_key": field_lineage,
                        "ingest_timestamp_utc": ingest_timestamp_utc,
                        "created_at_utc": ingest_timestamp_utc,
                    },
                )
                counts["raw_field_value_count"] += 1
                if raw_value_text == "":
                    add_quality_flag(
                        conn,
                        ingest_run_id=ingest_run_id,
                        source_file_id=source.db_file_id,
                        record_id=record_id,
                        field_value_id=field_value_id,
                        flag_scope="field_value",
                        flag_type="blank_value",
                        flag_status="retained",
                        flag_severity="audit_flag",
                        flag_note="Blank raw field value retained.",
                        lineage=field_lineage,
                        created_at_utc=ingest_timestamp_utc,
                    )

    return counts


def all_table_counts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    counts: list[dict[str, Any]] = []
    for (table_name,) in rows:
        row_count = conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
        counts.append({"table_name": table_name, "row_count": int(row_count)})
    return counts


def dashboard_rows(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return [
        {"metric_name": row[0], "metric_value": int(row[1])}
        for row in conn.execute(
            "SELECT metric_name, metric_value FROM qsb_v_db20_measurement_reality_dashboard ORDER BY metric_name"
        )
    ]


def quality_dashboard_rows(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    return [
        {
            "object_scope": row[0],
            "parse_status": row[1],
            "quality_status": row[2],
            "quarantine_status": row[3],
            "anomaly_status": row[4],
            "object_count": int(row[5]),
        }
        for row in conn.execute(
            """
            SELECT object_scope, parse_status, quality_status, quarantine_status,
                   anomaly_status, object_count
            FROM qsb_v_db20_quality_dashboard
            ORDER BY object_scope, parse_status, quality_status, quarantine_status, anomaly_status
            """
        )
    ]


def foreign_key_violations(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {
            "table_name": row[0],
            "rowid": row[1],
            "referenced_table": row[2],
            "fk_id": row[3],
        }
        for row in rows
    ]


def write_readout(
    path: Path,
    *,
    input_db: Path,
    output_db: Path,
    source_root: Path,
    inventory: list[SourceFile],
    selected_sources: list[SourceFile],
    summary: dict[str, Any],
    human_rows: list[dict[str, Any]],
) -> None:
    selected_lines = [
        (
            f"- `{source.relative_path}` ({source.size_bytes} bytes, "
            f"{source.structure_kind}, quarantine_status={source.quarantine_status})"
        )
        for source in selected_sources
    ]
    if not selected_lines:
        selected_lines = ["- none"]

    inventory_lines = [
        f"- inventoried files: {summary['inventoried_file_count']}",
        f"- ingested files: {summary['ingested_file_count']}",
        f"- raw records: {summary['raw_record_count']}",
        f"- raw field values: {summary['raw_field_value_count']}",
        f"- blank values: {summary['blank_value_count']}",
        f"- malformed or flagged objects: {summary['malformed_or_flagged_count']}",
        f"- quarantine candidate/context records: {summary['quarantine_candidate_count']}",
        f"- anomaly candidate/context records: {summary['anomaly_candidate_count']}",
        f"- foreign key violations: {summary['foreign_key_violation_count']}",
    ]

    sample_lines = [
        "| relative_path | line_number | field_name | raw_value_text | parse_status | quality_status | quarantine_status |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for row in human_rows:
        raw_value = str(row["raw_value_text"]).replace("|", "\\|")
        if len(raw_value) > 80:
            raw_value = raw_value[:77] + "..."
        sample_lines.append(
            "| "
            + " | ".join(
                [
                    str(row["relative_path"]),
                    str(row["line_number"]),
                    str(row["field_name"]),
                    raw_value,
                    str(row["parse_status"]),
                    str(row["quality_status"]),
                    str(row["quarantine_status"]),
                ]
            )
            + " |"
        )

    text = "\n".join(
        [
            "# QSB-DB20 First Real Rawdata Contact Readout",
            "",
            "## Befund",
            "",
            f"- Input DB copied from `{input_db.as_posix()}`.",
            f"- Output DB written to `{output_db.as_posix()}`.",
            f"- Source root inspected: `{source_root.as_posix()}`.",
            *inventory_lines,
            "",
            "Selected ingest source(s):",
            *selected_lines,
            "",
            "The source inventory includes all discovered files under the DB20 source root. "
            "The default deterministic selection ingests the smallest readable TIM/PAR-like "
            "representative unless source files are supplied by CLI.",
            "",
            "## Interpretation",
            "",
            "DB20 establishes first real rawdata contact by storing raw records and raw "
            "field/value objects as text with provenance, hashes, timestamps, IDs, status "
            "flags, and composite lineage keys. Quarantine-context flags found in the local "
            "manifest are retained instead of being used to discard records.",
            "",
            "## Hypothese",
            "",
            "No scientific hypothesis is tested here. The working hypothesis for later "
            "infrastructure work is only that this rawdata layer can support auditable "
            "downstream ETL and descriptive review from the database.",
            "",
            "## Offene Lücke",
            "",
            "- This run does not certify physical interpretation, residual behavior, model fit, or statistical inference.",
            "- The local manifest flags include quarantine-only context from an earlier download step; DB20 preserves that context in status fields.",
            "- The default run ingests the deterministic first representative; additional readable TIM/PAR files can be ingested by CLI in a separate explicit run.",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## First Human Readout Sample",
            "",
            *sample_lines,
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def dry_run(args: argparse.Namespace, output_db: Path) -> int:
    if not args.input_db.exists():
        raise FileNotFoundError(f"DB18 base DB not found: {args.input_db}")
    if not args.source_root.exists():
        print("No real rawdata source available for DB20.")
        return 1
    inventory = inventory_sources(args.source_root)
    if not inventory:
        print("No real rawdata source available for DB20.")
        return 1
    selected = select_ingest_files(
        inventory,
        args.source_root,
        args.source_file,
        args.ingest_all_candidates,
    )
    print(f"block: {BLOCK_NAME}")
    print("dry_run: true")
    print(f"input_db: {args.input_db}")
    print(f"source_root: {args.source_root}")
    print(f"output_root: {args.output_root}")
    print(f"output_db: {output_db}")
    print(f"inventoried_file_count: {len(inventory)}")
    print("selected_ingest_files:")
    for source in selected:
        print(f"- {source.relative_path} ({source.size_bytes} bytes)")
    print("claim_boundary:", CLAIM_BOUNDARY)
    return 0


def run(args: argparse.Namespace) -> int:
    input_db = args.input_db
    output_root = args.output_root
    output_db = output_db_path(output_root, args.output_db)
    readout_path = output_root / READOUT_NAME
    summary_path = output_root / SUMMARY_NAME
    source_inventory_path = output_root / SOURCE_INVENTORY_NAME
    table_counts_path = output_root / TABLE_COUNTS_NAME

    if args.dry_run:
        return dry_run(args, output_db)

    if not input_db.exists():
        raise FileNotFoundError(f"DB18 base DB not found: {input_db}")
    if not args.source_root.exists():
        print("No real rawdata source available for DB20.")
        return 1

    inventory = inventory_sources(args.source_root)
    if not inventory:
        print("No real rawdata source available for DB20.")
        return 1

    selected_sources = select_ingest_files(
        inventory,
        args.source_root,
        args.source_file,
        args.ingest_all_candidates,
    )
    if not selected_sources:
        raise RuntimeError(
            "No readable TIM/PAR-like candidate was available for DB20 ingest. "
            "Unsupported or compressed files were inventoried but not ingested."
        )
    selected_paths = {source.relative_path for source in selected_sources}
    for source in inventory:
        source.selected_for_ingest = 1 if source.relative_path in selected_paths else 0

    output_paths = [output_db, readout_path, summary_path, source_inventory_path, table_counts_path]
    output_root.mkdir(parents=True, exist_ok=True)
    ensure_no_existing_outputs(output_paths, args.overwrite)

    ingest_timestamp_utc = utc_now()
    run_suffix = hashlib.sha256(
        "|".join(source.relative_path for source in selected_sources).encode("utf-8")
    ).hexdigest()[:10]
    ingest_run_id = (
        "DB20_"
        + ingest_timestamp_utc.replace("-", "").replace(":", "").replace("Z", "Z")
        + "_"
        + run_suffix
    )
    selection_mode = (
        "explicit_source_file"
        if args.source_file
        else "all_candidates"
        if args.ingest_all_candidates
        else "first_deterministic_smallest_readable_tim_par"
    )

    shutil.copy2(input_db, output_db)

    warnings: list[str] = []
    conn = sqlite3.connect(output_db)
    try:
        conn.execute("PRAGMA foreign_keys=ON")
        create_db20_schema(conn)
        create_db20_views(conn)

        for source in inventory:
            source.db_file_id = insert_row(
                conn,
                "db20_rawdata_file_inventory",
                {
                    "source_id": source.source_id,
                    "source_label": source.source_label,
                    "source_path": source.path.as_posix(),
                    "relative_path": source.relative_path,
                    "source_file_name": source.file_name,
                    "source_extension": source.extension,
                    "source_file_size_bytes": source.size_bytes,
                    "source_file_mtime_utc": source.mtime_utc,
                    "source_file_hash_sha256": source.sha256,
                    "apparent_type": source.apparent_type,
                    "structure_kind": source.structure_kind,
                    "readability_status": source.readability_status,
                    "line_count": source.line_count,
                    "blank_line_count": source.blank_line_count,
                    "nonblank_line_count": source.nonblank_line_count,
                    "first_structural_lines": " || ".join(source.first_structural_lines),
                    "ingest_candidate_status": source.ingest_candidate_status,
                    "selected_for_ingest": source.selected_for_ingest,
                    "quarantine_status": source.quarantine_status,
                    "quarantine_note": source.quarantine_note,
                    "warning": source.warning,
                    "created_at_utc": ingest_timestamp_utc,
                },
            )
            if source.warning:
                warnings.append(f"{source.relative_path}: {source.warning}")

        insert_row(
            conn,
            "db20_rawdata_ingest_run",
            {
                "ingest_run_id": ingest_run_id,
                "ingest_timestamp_utc": ingest_timestamp_utc,
                "script_path": SCRIPT_PATH.as_posix(),
                "block_name": BLOCK_NAME,
                "input_db_path": input_db.as_posix(),
                "output_db_path": output_db.as_posix(),
                "source_root_path": args.source_root.as_posix(),
                "selection_mode": selection_mode,
                "selected_file_count": len(selected_sources),
                "inventoried_file_count": len(inventory),
                "run_status": "running",
                "stop_reason": "not_stopped",
                "claim_boundary": CLAIM_BOUNDARY,
                "warnings_json": json.dumps(warnings, sort_keys=True),
                "created_at_utc": ingest_timestamp_utc,
            },
        )

        aggregate_counts = {
            "raw_record_count": 0,
            "raw_field_value_count": 0,
            "blank_value_count": 0,
            "malformed_or_flagged_count": 0,
            "quarantine_candidate_count": 0,
            "anomaly_candidate_count": 0,
        }
        for source in selected_sources:
            counts = ingest_file(conn, source, ingest_run_id, ingest_timestamp_utc)
            for key, value in counts.items():
                aggregate_counts[key] += value

        fk_violations = foreign_key_violations(conn)
        conn.execute(
            """
            UPDATE db20_rawdata_ingest_run
            SET raw_record_count = ?,
                raw_field_value_count = ?,
                blank_value_count = ?,
                malformed_or_flagged_count = ?,
                quarantine_candidate_count = ?,
                anomaly_candidate_count = ?,
                foreign_key_violation_count = ?,
                run_status = ?,
                stop_reason = ?,
                warnings_json = ?
            WHERE ingest_run_id = ?
            """,
            (
                aggregate_counts["raw_record_count"],
                aggregate_counts["raw_field_value_count"],
                aggregate_counts["blank_value_count"],
                aggregate_counts["malformed_or_flagged_count"],
                aggregate_counts["quarantine_candidate_count"],
                aggregate_counts["anomaly_candidate_count"],
                len(fk_violations),
                "completed",
                "completed_first_real_rawdata_contact",
                json.dumps(warnings, sort_keys=True),
                ingest_run_id,
            ),
        )
        conn.commit()

        table_counts = all_table_counts(conn)
        dashboard = dashboard_rows(conn)
        quality_dashboard = quality_dashboard_rows(conn)
        human_rows = [
            {
                "relative_path": row[0],
                "line_number": row[1],
                "field_name": row[2],
                "raw_value_text": row[3],
                "parse_status": row[4],
                "quality_status": row[5],
                "quarantine_status": row[6],
            }
            for row in conn.execute(
                """
                SELECT relative_path, line_number, field_name, raw_value_text,
                       parse_status, quality_status, quarantine_status
                FROM qsb_v_db20_first_human_readout
                LIMIT 24
                """
            )
        ]
    finally:
        conn.close()

    summary = {
        "block_name": BLOCK_NAME,
        "script_path": SCRIPT_PATH.as_posix(),
        "input_db_path": input_db.as_posix(),
        "input_db_size_bytes": input_db.stat().st_size,
        "output_db_path": output_db.as_posix(),
        "output_root": output_root.as_posix(),
        "source_root_path": args.source_root.as_posix(),
        "ingest_run_id": ingest_run_id,
        "ingest_timestamp_utc": ingest_timestamp_utc,
        "selection_mode": selection_mode,
        "inventoried_file_count": len(inventory),
        "selected_ingest_files": [
            {
                "relative_path": source.relative_path,
                "source_file_size_bytes": source.size_bytes,
                "source_file_mtime_utc": source.mtime_utc,
                "source_file_hash_sha256": source.sha256,
                "structure_kind": source.structure_kind,
                "quarantine_status": source.quarantine_status,
                "quarantine_note": source.quarantine_note,
            }
            for source in selected_sources
        ],
        "ingested_file_count": len(selected_sources),
        "raw_record_count": aggregate_counts["raw_record_count"],
        "raw_field_value_count": aggregate_counts["raw_field_value_count"],
        "blank_value_count": aggregate_counts["blank_value_count"],
        "malformed_or_flagged_count": aggregate_counts["malformed_or_flagged_count"],
        "quarantine_candidate_count": aggregate_counts["quarantine_candidate_count"],
        "anomaly_candidate_count": aggregate_counts["anomaly_candidate_count"],
        "foreign_key_violation_count": len(fk_violations),
        "foreign_key_violations": fk_violations,
        "dashboard": dashboard,
        "quality_dashboard": quality_dashboard,
        "warnings": warnings,
        "stop_reason": "completed_first_real_rawdata_contact",
        "claim_boundary": CLAIM_BOUNDARY,
        "limitations": [
            "No residual analysis was performed.",
            "No model fitting was performed.",
            "No statistical inference was performed.",
            "No physical meaning or Bridge confirmation is claimed.",
            "Raw values were preserved as text for audit-oriented downstream work.",
        ],
    }

    write_csv(
        source_inventory_path,
        [
            "db20_source_file_id",
            "source_id",
            "source_label",
            "source_path",
            "relative_path",
            "source_file_name",
            "source_extension",
            "source_file_size_bytes",
            "source_file_mtime_utc",
            "source_file_hash_sha256",
            "apparent_type",
            "structure_kind",
            "readability_status",
            "line_count",
            "blank_line_count",
            "nonblank_line_count",
            "first_structural_lines",
            "ingest_candidate_status",
            "selected_for_ingest",
            "quarantine_status",
            "quarantine_note",
            "warning",
        ],
        source_inventory_rows(inventory),
    )
    write_csv(table_counts_path, ["table_name", "row_count"], table_counts)
    write_json(summary_path, summary)
    write_readout(
        readout_path,
        input_db=input_db,
        output_db=output_db,
        source_root=args.source_root,
        inventory=inventory,
        selected_sources=selected_sources,
        summary=summary,
        human_rows=human_rows,
    )

    print(f"block: {BLOCK_NAME}")
    print(f"output_db: {output_db}")
    print(f"readout: {readout_path}")
    print(f"summary: {summary_path}")
    print(f"source_inventory: {source_inventory_path}")
    print(f"table_counts: {table_counts_path}")
    print(f"inventoried_file_count: {len(inventory)}")
    print(f"ingested_file_count: {len(selected_sources)}")
    print(f"raw_record_count: {aggregate_counts['raw_record_count']}")
    print(f"raw_field_value_count: {aggregate_counts['raw_field_value_count']}")
    print(f"foreign_key_violation_count: {len(fk_violations)}")
    print("claim_boundary:", CLAIM_BOUNDARY)
    return 0


def main() -> int:
    args = parse_args()
    return run(args)


if __name__ == "__main__":
    raise SystemExit(main())
