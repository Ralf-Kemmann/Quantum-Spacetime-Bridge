#!/usr/bin/env python3
"""Application entry point."""

from __future__ import annotations

import logging
import argparse
from logging.handlers import RotatingFileHandler
from pathlib import Path
from tkinter import messagebox

from src.config import APP_TITLE, APP_VERSION, LOG_PATH, SNAPSHOT_DIR
from src.chart_service import chart_engine_info
from src.language_service import SUPPORTED_LANGUAGES, resolve_start_language
from src.metadata_search import MetadataSearchAdapter, detect_metadata_sources
from src.qsb_database import QSBMetadataDatabase
from src.qsb_gui import run_qsb_browser
from src.read_only_guard import ReadOnlyGuardError, assert_read_only_sql
from src.snapshot_manager import (
    SnapshotInfo,
    create_verified_snapshot,
    resolve_source_database,
    sha256_file,
    use_source_without_snapshot,
)


def configure_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(LOG_PATH, maxBytes=500_000, backupCount=3, encoding="utf-8")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[handler],
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QSB Research Data Browser.")
    parser.add_argument("--database", help="Path to a QSB metadata SQLite database. Overrides QSB_METADATA_DB.")
    parser.add_argument("--create-snapshot", action="store_true", help="Create a verified snapshot and exit unless GUI/list/smoke mode is also requested.")
    parser.add_argument("--snapshot-dir", default=str(SNAPSHOT_DIR), help="Directory for verified snapshot files.")
    parser.add_argument("--overwrite-snapshot", action="store_true", help="Allow replacing a snapshot with the same generated name.")
    parser.add_argument("--no-snapshot", action="store_true", help="Developer diagnostic mode: browse source directly with a visible warning.")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help="Create/reuse a snapshot, verify read-only behavior, introspect views and metadata sources, then exit.",
    )
    parser.add_argument("--list-views", action="store_true", help="List available SQL views and exit.")
    parser.add_argument("--list-tables", action="store_true", help="List available SQL tables and exit.")
    parser.add_argument("--version", action="store_true", help="Show application version and exit.")
    parser.add_argument("--language", choices=SUPPORTED_LANGUAGES, help="Presentation language for this run.")
    parser.add_argument("--list-languages", action="store_true", help="List supported presentation languages and exit.")
    parser.add_argument("--chart-engine-info", action="store_true", help="Report chart engine capabilities and exit.")
    return parser.parse_args()


def prepare_database(args: argparse.Namespace) -> tuple[QSBMetadataDatabase, SnapshotInfo]:
    source = resolve_source_database(args.database)
    if args.no_snapshot:
        info = use_source_without_snapshot(source)
        print("WARNING: --no-snapshot uses the source database directly for developer diagnostics.")
        return QSBMetadataDatabase(info.snapshot_path, immutable=True, manifest=info.manifest), info
    info = create_verified_snapshot(
        source,
        snapshot_dir=Path(args.snapshot_dir),
        overwrite_snapshot=args.overwrite_snapshot,
        repo_root=Path.cwd(),
    )
    return QSBMetadataDatabase(info.snapshot_path, immutable=True, manifest=info.manifest), info


def run_smoke_test(database: QSBMetadataDatabase, snapshot_info: SnapshotInfo, language: str = "de") -> int:
    views = database.list_views()
    tables = database.list_tables()
    sources = detect_metadata_sources(database)
    sample = MetadataSearchAdapter(database, max_results=5).search("Causality07")
    mart_work_packages = database.generic_mart_work_packages()
    result_tables = database.generic_result_tables()
    result_records = database.generic_result_records(limit=25)
    corrcore_status = database.corrcore_visibility_status()
    write_rejected = False
    try:
        assert_read_only_sql("INSERT INTO meta_mart VALUES ('x')")
    except ReadOnlyGuardError:
        write_rejected = True
    sqlite_write_failed = False
    try:
        with database.connect() as conn:
            conn.execute("CREATE TABLE qsb_write_probe(id INTEGER)")
    except Exception:
        sqlite_write_failed = True
    required = [
        "v_de_physikalische_groessen",
        "v_de_lineage",
        "v_de_validierungsergebnisse",
        "v_de_ergebnis_claim_beziehungen",
        "v_de_offene_pruefpunkte",
    ]
    available_required = [view for view in required if view in views]
    for view in available_required:
        database.load_view_page(view, limit=1)
    source_unchanged = sha256_file(snapshot_info.source_path) == snapshot_info.manifest["source_sha256"]
    snapshot_match = snapshot_info.manifest["source_sha256"] == snapshot_info.manifest["snapshot_sha256"]
    print(f"source_database={snapshot_info.source_path}")
    print(f"snapshot_database={snapshot_info.snapshot_path}")
    print(f"manifest={snapshot_info.manifest_path}")
    print(f"snapshot_status={snapshot_info.manifest.get('snapshot_status')}")
    print(f"checksum_match={snapshot_match}")
    print(f"source_unchanged={source_unchanged}")
    print(f"read_only={database.assert_read_only()}")
    print(f"table_count={len(tables)}")
    print(f"view_count={len(views)}")
    print(f"required_german_views={available_required}")
    print(f"write_guard_rejected={write_rejected}")
    print(f"sqlite_write_failed={sqlite_write_failed}")
    print(f"metadata_sources={[source.name for source in sources]}")
    print(f"sample_search_results={len(sample)}")
    print(f"catalog_path_visible={bool(database.database_path.name)}")
    print(f"generic_mart_work_package_rows={mart_work_packages.total_count}")
    print(f"generic_result_table_rows={result_tables.total_count}")
    print(f"generic_result_record_rows={result_records.total_count}")
    for key, value in corrcore_status.items():
        print(f"{key}={value}")
    print(f"language={language}")
    corrcore_required = corrcore_status["corrcore_mart_found"]
    corrcore_ok = not corrcore_required or all(corrcore_status.values())
    ok = snapshot_match and source_unchanged and write_rejected and sqlite_write_failed and bool(views) and corrcore_ok
    print(f"smoke_test_status={'passed' if ok else 'failed'}")
    return 0 if ok else 1


def main() -> None:
    args = parse_args()
    if args.version:
        print(APP_VERSION)
        return
    if args.list_languages:
        for language in SUPPORTED_LANGUAGES:
            print(language)
        return
    if args.chart_engine_info:
        for key, value in chart_engine_info().items():
            print(f"{key}={value}")
        return
    language = resolve_start_language(args.language)
    configure_logging()
    try:
        database, snapshot_info = prepare_database(args)
        if args.create_snapshot and not (args.smoke_test or args.list_views or args.list_tables):
            print(f"snapshot={snapshot_info.snapshot_path}")
            print(f"manifest={snapshot_info.manifest_path}")
            print("snapshot_status=verified")
            return
        if args.list_views:
            for view in database.list_views():
                print(view)
            return
        if args.list_tables:
            for table in database.list_tables():
                print(table)
            return
        if args.smoke_test:
            raise SystemExit(run_smoke_test(database, snapshot_info, language=language))
        run_qsb_browser(database, language=language)
    except Exception:
        logging.getLogger(__name__).exception("Application startup failed")
        messagebox.showerror(APP_TITLE, "Die Anwendung konnte nicht gestartet werden. Details stehen in der Logdatei.")


if __name__ == "__main__":
    main()
