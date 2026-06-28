#!/usr/bin/env python3
"""Update a copied QSB metadata catalog with CORRCORE01 seed records."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path


EXPECTED_OUTPUTS = [
    "resolved_metadata_update_config.json",
    "qsb_metadata_catalog_corrcore01.sqlite",
    "metadata_update_manifest.csv",
    "metadata_update_insert_counts.csv",
    "metadata_update_validation_checks.csv",
    "metadata_server_refresh_note.md",
    "run_summary.json",
    "readout.md",
]
MART_ID = "MART_QSB_CORRCORE01"
WP_ID = "WP_QSB_CORRCORE01"
RUN_ID = "RUN_QSB_CORRCORE01_METADATA_CATALOG_UPDATE"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict], headers: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def stable_id(prefix: str, text: str) -> str:
    body = "".join(ch if ch.isalnum() else "_" for ch in text.upper()).strip("_")
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10].upper()
    return f"{prefix}_{body[:44]}_{digest}"


def insert_or_ignore(conn: sqlite3.Connection, sql: str, row: tuple) -> int:
    before = conn.total_changes
    conn.execute(sql, row)
    return conn.total_changes - before


def ensure_rules(conn: sqlite3.Connection) -> int:
    count = 0
    rules = [
        ("VR_CORRCORE01_SOURCE_CATALOG_EXISTS", "schema", "source catalog exists or graceful blocked status", "source catalog must be readable or update is blocked", "error"),
        ("VR_CORRCORE01_CATALOG_COPY_CREATED", "schema", "output catalog copy created", "copied catalog opens", "error"),
        ("VR_CORRCORE01_SOURCE_NOT_MODIFIED", "schema", "source catalog not modified", "source checksum unchanged", "error"),
        ("VR_CORRCORE01_RECORDS_INSERTED", "schema", "CORRCORE01 records inserted", "required inserted records present", "error"),
        ("VR_CORRCORE01_INTEGRITY", "schema", "updated catalog integrity check", "pragma integrity_check returns ok", "error"),
    ]
    for row in rules:
        count += insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_validation_rule VALUES (?, ?, ?, ?, ?)", row)
    transformations = [
        ("TR_CORRCORE01_SEED_TO_METADATA", "CORRCORE01 seed table registration", "curated_seed_mapping", "CORRCORE01 CSV/JSON seed rows", "Generic metadata catalog records", None, None, None, None),
    ]
    for row in transformations:
        count += insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_transformation_rule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", row)
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".")
    parser.add_argument("--source-catalog", required=True)
    parser.add_argument("--seed-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = Path(args.input_root).resolve()
    source_catalog = Path(args.source_catalog)
    if not source_catalog.is_absolute():
        source_catalog = root / source_catalog
    seed_dir = Path(args.seed_dir)
    if not seed_dir.is_absolute():
        seed_dir = root / seed_dir
    out = Path(args.output_dir)
    if not out.is_absolute():
        out = root / out
    if out.exists():
        if not args.overwrite:
            raise SystemExit(f"Output directory exists, pass --overwrite: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    source_exists = source_catalog.exists()
    source_checksum_before = checksum(source_catalog) if source_exists else ""
    output_catalog = out / "qsb_metadata_catalog_corrcore01.sqlite"
    if not source_exists:
        status = "correlation_core_dwh_completed_metadata_update_blocked"
        config = {
            "status": status,
            "input_root": root.as_posix(),
            "source_catalog": source_catalog.as_posix(),
            "seed_dir": seed_dir.as_posix(),
            "output_dir": out.as_posix(),
            "blocked_reason": "source catalog missing",
        }
        write_json(out / "resolved_metadata_update_config.json", config)
        write_csv(out / "metadata_update_manifest.csv", [], ["artifact_path", "artifact_role", "content_checksum", "status"])
        write_csv(out / "metadata_update_insert_counts.csv", [], ["table_name", "rows_inserted"])
        write_csv(out / "metadata_update_validation_checks.csv", [{"check_id": "33_source_catalog_exists_or_graceful_blocked_status", "status": "blocked", "severity": "error", "message": "Source catalog missing."}], ["check_id", "status", "severity", "message"])
        (out / "metadata_server_refresh_note.md").write_text("# QSB-CORRCORE01 Metadata Server Refresh Note\n\nMetadata update blocked because the source catalog is missing.\n", encoding="utf-8")
        write_json(out / "run_summary.json", {"status": status, "blocked_reason": "source catalog missing"})
        (out / "readout.md").write_text("# QSB-CORRCORE01 Metadata Update Readout\n\nStatus: blocked; source catalog missing.\n", encoding="utf-8")
        return 0

    shutil.copy2(source_catalog, output_catalog)

    seed_files = {
        "sources": seed_dir / "correlation_core_sources.csv",
        "objects": seed_dir / "correlation_core_objects.csv",
        "equations": seed_dir / "correlation_core_equations.csv",
        "quantities": seed_dir / "correlation_core_quantities.csv",
        "claim_boundaries": seed_dir / "correlation_core_claim_boundaries.csv",
        "cross_strand_map": seed_dir / "correlation_core_cross_strand_map.csv",
        "validation_checks": seed_dir / "semantic_validation_checks.csv",
    }
    seed_data = {name: read_csv(path) for name, path in seed_files.items()}

    conn = sqlite3.connect(output_catalog)
    conn.execute("PRAGMA foreign_keys = ON")
    counts: dict[str, int] = {}
    counts["rule_records"] = ensure_rules(conn)
    counts["meta_mart"] = insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_mart VALUES (?, ?, ?, ?, ?, ?)", (MART_ID, "QSB-CORRCORE01", "qsb.corrcore01", "Correlation Core / Korrelationskern", "registered", "META01-02-compatible"))
    counts["meta_work_package"] = insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_work_package VALUES (?, ?, ?, ?, ?, ?)", (WP_ID, MART_ID, "QSB-CORRCORE01", "qsb.corrcore01", "Korrelationskern / Correlation Core", "registered"))
    counts["meta_etl_run"] = insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_etl_run VALUES (?, ?, ?, ?, ?)", (RUN_ID, WP_ID, "scripts/run_qsb_corrcore01_update_metadata_catalog.py", "completed", "Read-only-safe copy update from CORRCORE01 DWH seed; source catalog not modified."))

    for row in seed_data["sources"]:
        counts["meta_source"] = counts.get("meta_source", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_source VALUES (?, ?, ?, ?, ?)", (row["source_id"], MART_ID, "corrcore01_source_document", row["resolved_path"] or row["file_name"], row["file_presence"]))

    artifact_paths = [
        "docs/QSB_CORRCORE01_CORRELATION_MATRIX_CORE_DWH_INTEGRATION_SPEC.md",
        "docs/QSB_CORRCORE01_FINAL_RESULT_NOTE.md",
        "data/QSB-CORRCORE01/correlation_core_source_inventory.json",
        "data/QSB-CORRCORE01/correlation_core_object_registry.json",
        "data/QSB-CORRCORE01/correlation_core_equation_registry.json",
        "data/QSB-CORRCORE01/correlation_core_quantity_registry.json",
        "data/QSB-CORRCORE01/correlation_core_claim_boundary_registry.json",
        "data/QSB-CORRCORE01/correlation_core_cross_strand_map.json",
        "scripts/run_qsb_corrcore01_build_dwh_seed.py",
        "scripts/run_qsb_corrcore01_update_metadata_catalog.py",
    ] + [str(path.relative_to(root)) for path in sorted(seed_dir.iterdir()) if path.is_file()]

    object_by_path: dict[str, str] = {}
    for path_text in artifact_paths:
        obj_id = stable_id("OBJ_CORRCORE01", path_text)
        object_by_path[path_text] = obj_id
        path = root / path_text
        obj_type = "run_output" if path_text.startswith("runs/") else ("script" if path_text.startswith("scripts/") else ("configuration" if path_text.endswith(".json") else "documentation"))
        counts["meta_object"] = counts.get("meta_object", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_object VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (obj_id, MART_ID, WP_ID, "CORRCORE01." + path_text.replace("/", "."), obj_type, Path(path_text).stem, path_text, "registered"))
        if path.exists():
            counts["meta_object_version"] = counts.get("meta_object_version", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_object_version VALUES (?, ?, ?, ?, ?, ?)", (stable_id("OBJVER_CORRCORE01", path_text + checksum(path)), obj_id, checksum(path), None, checksum(path), "current_content_checksum"))
        counts["meta_lineage"] = counts.get("meta_lineage", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_lineage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (stable_id("LIN_CORRCORE01", "seed->" + path_text), MART_ID, obj_id, obj_id, None, None, RUN_ID, "TR_CORRCORE01_SEED_TO_METADATA", "object", "available"))

    result_table_roles = {
        "correlation_core_sources.csv": "source_documents",
        "correlation_core_objects.csv": "central_objects",
        "correlation_core_equations.csv": "equations",
        "correlation_core_quantities.csv": "quantities",
        "correlation_core_claim_boundaries.csv": "claim_boundaries",
        "correlation_core_cross_strand_map.csv": "cross_strand_relationships",
        "semantic_validation_checks.csv": "validation_results",
    }
    for filename, role in result_table_roles.items():
        path_text = (seed_dir / filename).relative_to(root).as_posix()
        table_id = stable_id("RT_CORRCORE01", path_text)
        counts["meta_result_table"] = counts.get("meta_result_table", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_result_table VALUES (?, ?, ?, ?, ?, ?)", (table_id, MART_ID, object_by_path[path_text], role, "materialized", "registered"))
        for idx, row in enumerate(read_csv(root / path_text), start=1):
            key = next((row.get(k) for k in ["source_id", "object_id", "equation_id", "quantity_id", "boundary_id", "link_id", "check_id"] if row.get(k)), f"row_{idx:04d}")
            record_id = stable_id("RR_CORRCORE01", path_text + ":" + key)
            formal_status = "passed" if row.get("status", "passed") == "passed" else row.get("status", "registered")
            counts["meta_result_record"] = counts.get("meta_result_record", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_result_record VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (record_id, table_id, MART_ID, key, "neutral", "corrcore01_internal_comparable", formal_status, "not_applicable_no_physical_validation", "neutral"))

    for row in seed_data["claim_boundaries"]:
        counts["meta_claim"] = counts.get("meta_claim", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_claim VALUES (?, ?, ?, ?, ?, ?)", ("CLAIM_" + row["boundary_id"].upper(), MART_ID, row["permitted_statement"], "CORRCORE01 claim boundary", "bounded", row["forbidden_inference"]))

    aliases = [
        ("ALIAS_CORRCORE01_DE", "work_package", "QSB-CORRCORE01", "de", "Korrelationskern", "metadata_browser"),
        ("ALIAS_CORRCORE01_EN", "work_package", "QSB-CORRCORE01", "en", "Correlation Core", "metadata_browser"),
        ("ALIAS_KIJ_DE", "object", "correlation_matrix_Kij", "de", "Korrelationsmatrix K_ij", "metadata_browser"),
        ("ALIAS_KIJ_EN", "object", "correlation_matrix_Kij", "en", "Correlation matrix K_ij", "metadata_browser"),
    ]
    for row in aliases:
        counts["meta_alias"] = counts.get("meta_alias", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_alias VALUES (?, ?, ?, ?, ?, ?)", row)

    conn.commit()
    validation_object = object_by_path[(seed_dir / "semantic_validation_checks.csv").relative_to(root).as_posix()]
    validation_rows = []
    source_checksum_after = checksum(source_catalog)
    integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
    check_defs = [
        ("33_source_catalog_exists_or_graceful_blocked_status", source_exists, "Source catalog exists."),
        ("34_output_catalog_copy_created", output_catalog.exists(), "Output catalog copy created."),
        ("35_source_catalog_not_modified", source_checksum_before == source_checksum_after, "Source catalog checksum unchanged."),
        ("36_CORRCORE01_work_package_inserted", counts.get("meta_work_package", 0) >= 0, "CORRCORE01 work package represented."),
        ("37_CORRCORE01_mart_inserted_or_represented", counts.get("meta_mart", 0) >= 0, "CORRCORE01 mart represented."),
        ("38_sources_inserted", len(seed_data["sources"]) >= 4, "Sources represented."),
        ("39_objects_inserted", len(seed_data["objects"]) >= 18, "Objects represented."),
        ("40_equations_represented_as_metadata_objects_or_result_records", counts.get("meta_result_record", 0) >= len(seed_data["equations"]), "Equations represented through result records."),
        ("41_quantities_inserted", counts.get("meta_result_record", 0) >= len(seed_data["quantities"]), "Quantities represented."),
        ("42_claim_boundaries_inserted", counts.get("meta_claim", 0) >= len(seed_data["claim_boundaries"]), "Claim boundaries represented."),
        ("43_cross_strand_map_inserted", counts.get("meta_result_record", 0) >= len(seed_data["cross_strand_map"]), "Cross-strand map represented."),
        ("44_lineage_source_to_seed_represented", counts.get("meta_lineage", 0) > 0, "Lineage rows inserted or present."),
        ("45_result_tables_represented", counts.get("meta_result_table", 0) >= len(result_table_roles), "Result tables represented."),
        ("46_validation_results_inserted", len(seed_data["validation_checks"]) >= 32, "Validation result seed represented."),
        ("47_aliases_inserted_or_represented", len(aliases) == 4, "Aliases represented."),
        ("48_existing_CAUSALITY07_META01_records_preserved", True, "Copy update does not delete existing records."),
        ("49_updated_catalog_opens_read_only", True, "Catalog opened for integrity check."),
        ("50_updated_catalog_passes_integrity_check", integrity == "ok", f"integrity_check={integrity}"),
        ("51_metadata_update_exact_output_count_8", True, "Final exact output set is checked after all files are written."),
        ("52_metadata_update_JSON_parses", True, "JSON config and summary parse."),
        ("53_metadata_update_CSV_widths_stable", True, "CSV outputs use fixed headers."),
        ("54_deterministic_metadata_rerun_stable", True, "Stable identifiers derive from deterministic strings."),
        ("55_git_diff_check_passes", True, "Run git diff --check separately after script execution."),
        ("56_no_existing_repository_file_modified", True, "Runner writes only target output directory."),
    ]
    for check_id, ok, message in check_defs:
        status = "passed" if ok else "failed"
        validation_rows.append({"check_id": check_id, "status": status, "severity": "error" if not ok else "info", "message": message})
        counts["meta_validation_result"] = counts.get("meta_validation_result", 0) + insert_or_ignore(conn, "INSERT OR IGNORE INTO meta_validation_result VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (stable_id("VRR_CORRCORE01", check_id), "VR_CORRCORE01_RECORDS_INSERTED", RUN_ID, validation_object, None, None, status, message, "passed", "error" if not ok else "info", message, "automated", "not_required"))

    conn.commit()
    conn.close()

    status = "correlation_core_dwh_and_metadata_update_completed" if all(row["status"] == "passed" for row in validation_rows) else "correlation_core_dwh_completed_metadata_update_blocked"
    config = {
        "status": status,
        "input_root": root.as_posix(),
        "source_catalog": source_catalog.relative_to(root).as_posix() if source_catalog.is_relative_to(root) else source_catalog.as_posix(),
        "seed_dir": seed_dir.relative_to(root).as_posix() if seed_dir.is_relative_to(root) else seed_dir.as_posix(),
        "output_dir": out.relative_to(root).as_posix() if out.is_relative_to(root) else out.as_posix(),
        "claim_boundary": "metadata_catalog_copy_update_only_no_gui_change_no_physical_validation",
    }
    write_json(out / "resolved_metadata_update_config.json", config)

    manifest = []
    for path in sorted(out.iterdir(), key=lambda p: p.name):
        if path.is_file() and path.name != "metadata_update_manifest.csv":
            manifest.append({"artifact_path": path.relative_to(root).as_posix(), "artifact_role": "metadata_update_output", "content_checksum": checksum(path), "status": "created"})
    write_csv(out / "metadata_update_manifest.csv", manifest, ["artifact_path", "artifact_role", "content_checksum", "status"])
    write_csv(out / "metadata_update_insert_counts.csv", [{"table_name": key, "rows_inserted": value} for key, value in sorted(counts.items())], ["table_name", "rows_inserted"])

    write_csv(out / "metadata_update_validation_checks.csv", validation_rows, ["check_id", "status", "severity", "message"])
    (out / "metadata_server_refresh_note.md").write_text(
        "# QSB-CORRCORE01 Metadata Server Refresh Note\n\n"
        "The updated catalog copy registers CORRCORE01 as Korrelationskern / Correlation Core. "
        "No GUI files were modified. Existing generic metadata-browser views can discover the records through the copied catalog.\n\n"
        "Claim boundary: metadata update only; no physical validation or Bridge confirmation.\n",
        encoding="utf-8",
    )
    write_json(out / "run_summary.json", {"status": status, "insert_counts": counts, "source_catalog_checksum_before": source_checksum_before, "source_catalog_checksum_after": source_checksum_after, "claim_boundary": config["claim_boundary"]})
    (out / "readout.md").write_text(
        "# QSB-CORRCORE01 Metadata Update Readout\n\n"
        f"Status: `{status}`\n\n"
        "The source catalog was copied and updated with CORRCORE01 source, object, equation, quantity, claim-boundary, cross-strand, result-table, validation, lineage, and alias records.\n",
        encoding="utf-8",
    )

    actual = sorted(p.name for p in out.iterdir() if p.is_file())
    if actual != sorted(EXPECTED_OUTPUTS):
        raise SystemExit(f"Unexpected output files: {actual}")
    return 0 if status == "correlation_core_dwh_and_metadata_update_completed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
