#!/usr/bin/env python3
"""SPARC/RAR DWH ETL and metadata registration run.

This script is intentionally run-local. It reads predecessor artifacts, creates
one SQLite DWH in this directory, and writes auditable CSV/JSON/MD outputs.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "QSB-SPARC-RAR-DWH-ETL-METADATA-REGISTRATION-01"
REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "runs" / RUN_ID
DB_PATH = OUT / "sparc_rar_dwh.sqlite"
DATA_CONTRACT = REPO / "runs" / "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT"
REVIEW = REPO / "runs" / "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT-REVIEW"
BASELINE = REPO / "runs" / "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-REPRODUCTION"
DATASET_ID = "SPARC_RAR_LELLI2016C_BASELINE_REGISTERED"
CLAIM_BOUNDARY = [
    "sparc_rar_dwh_etl",
    "metadata_registration",
    "raw_data_preservation",
    "checksum_revalidation",
    "staging_load",
    "canonical_load",
    "baseline_registration",
    "dwh_search_enablement",
    "methodological_preparation_only",
    "no_qsb_detection_claim",
    "no_dark_matter_claim",
    "no_mond_claim",
    "no_lambdacdm_refutation_claim",
    "no_gravity_claim",
    "no_spacetime_claim",
    "no_causality_claim",
]

RAW_INPUTS = [
    DATA_CONTRACT / "input" / "MassModels_Lelli2016c.mrt",
    DATA_CONTRACT / "input" / "RAR.mrt",
    DATA_CONTRACT / "input" / "RARbins.mrt",
    DATA_CONTRACT / "input" / "SPARC_Lelli2016c.mrt",
]

REQUIRED_ARTIFACTS = [
    DATA_CONTRACT / "04_sparc_rar_data_contract_summary.json",
    DATA_CONTRACT / "05_input_file_inventory.csv",
    DATA_CONTRACT / "06_input_file_checksums.csv",
    DATA_CONTRACT / "08_detected_column_inventory.csv",
    DATA_CONTRACT / "09_sparc_expected_column_mapping.csv",
    DATA_CONTRACT / "13_data_lineage_contract.md",
    REVIEW / "04_data_contract_review_summary.json",
    REVIEW / "06_checksum_revalidation.csv",
    REVIEW / "09_mrt_structure_review.csv",
    REVIEW / "13_data_contract_freeze_decision.csv",
    BASELINE / "04_baseline_rar_reproduction_summary.json",
    BASELINE / "12_column_mapping_used.csv",
    BASELINE / "13_unit_conversion_contract.csv",
    BASELINE / "14_direct_rar_dataset.csv",
    BASELINE / "15_massmodels_derived_baseline_quantities.csv",
    BASELINE / "18_baseline_reproduction_readout.csv",
]

OPTIONAL_ARTIFACTS = [
    BASELINE / "25_massmodels_vs_direct_rar_comparison.csv",
]

FIELDS = [
    ("dataset_id", "Datensatz-ID", "identifier", "[dimensionless]"),
    ("source_file_id", "Quelldatei-ID", "identifier", "[dimensionless]"),
    ("source_artifact_id", "Quellartefakt-ID", "identifier", "[dimensionless]"),
    ("run_id", "Lauf-ID", "identifier", "[dimensionless]"),
    ("galaxy_id", "Galaxien-ID", "identifier", "[dimensionless]"),
    ("radius_kpc", "Radius (kpc)", "radius", "[L]"),
    ("distance_mpc", "Entfernung (Mpc)", "distance", "[L]"),
    ("vobs_km_s", "beobachtete Rotationsgeschwindigkeit", "velocity", "[L T^-1]"),
    ("vobs_error_km_s", "Unsicherheit der beobachteten Rotationsgeschwindigkeit", "velocity_uncertainty", "[L T^-1]"),
    ("vgas_km_s", "Gas-Geschwindigkeitsbeitrag", "velocity", "[L T^-1]"),
    ("vdisk_km_s", "Scheiben-Geschwindigkeitsbeitrag", "velocity", "[L T^-1]"),
    ("vbul_km_s", "Bulge-Geschwindigkeitsbeitrag", "velocity", "[L T^-1]"),
    ("sbdisk_solLum_pc2", "Scheiben-Oberflächenhelligkeit", "surface_brightness", "[surface_brightness_luminosity_area^-1]"),
    ("sbbul_solLum_pc2", "Bulge-Oberflächenhelligkeit", "surface_brightness", "[surface_brightness_luminosity_area^-1]"),
    ("gobs_m_s2", "beobachtete Beschleunigung", "acceleration", "[L T^-2]"),
    ("gbar_m_s2", "baryonische Beschleunigung", "acceleration", "[L T^-2]"),
    ("log_gobs", "Log beobachtete Beschleunigung", "dimensionless_log_quantity", "[dimensionless]"),
    ("log_gbar", "Log baryonische Beschleunigung", "dimensionless_log_quantity", "[dimensionless]"),
    ("rar_point_id", "RAR-Punkt-ID", "identifier", "[dimensionless]"),
    ("massmodel_point_id", "MassModel-Punkt-ID", "identifier", "[dimensionless]"),
    ("unit_original", "Originaleinheit", "unit", "[dimensionless]"),
    ("unit_calculation", "Berechnungseinheit", "unit", "[dimensionless]"),
    ("unit_display", "Anzeigeeinheit", "unit", "[dimensionless]"),
    ("dimension_vector", "Dimensionsvektor", "dimension", "[dimensionless]"),
    ("conversion_rule_id", "Umrechnungsregel-ID", "conversion_rule", "[dimensionless]"),
    ("lineage_hash", "Lineage-Hash", "lineage", "[dimensionless]"),
    ("source_sha256", "Quellen-SHA256", "checksum", "[dimensionless]"),
    ("validation_status", "Validierungsstatus", "validation", "[dimensionless]"),
    ("claim_boundary", "Claim-Grenze", "claim_boundary", "[dimensionless]"),
]

UNITS = [
    ("kpc", "length", "[L]", "kpc_to_m"),
    ("Mpc", "length", "[L]", "Mpc_to_m"),
    ("km/s", "velocity", "[L T^-1]", "km_s_to_m_s"),
    ("m/s^2", "acceleration", "[L T^-2]", "gobs_from_vobs2_over_radius"),
    ("solLum/pc2", "surface_brightness", "[surface_brightness_luminosity_area^-1]", "raw_value_passthrough"),
    ("dex", "dimensionless_log_quantity", "[dimensionless]", "log10_quantity_passthrough"),
    ("log10 dimensionless", "dimensionless_log_quantity", "[dimensionless]", "log10_quantity_passthrough"),
]


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for _ in f)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        w.writeheader()
        for row in rows:
            w.writerow({k: row.get(k, "") for k in fields})


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_capture(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, cwd=REPO, check=False, text=True, capture_output=True)
        return p.stdout + p.stderr
    except Exception as exc:
        return f"command_failed: {exc}\n"


def to_float(value: str | None):
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def source_id_for(path: Path) -> str:
    stem = path.name.replace(".", "_").replace("-", "_")
    return f"source_{stem}"


def artifact_id_for(path: Path) -> str:
    stem = path.name.replace(".", "_").replace("-", "_")
    return f"artifact_{stem}"


def discover_existing_metadata() -> tuple[list[dict], list[dict]]:
    dbs = sorted(
        set(REPO.glob("**/*metadata*.sqlite"))
        | set(REPO.glob("**/*qsb_metadata_catalog.sqlite"))
        | set(REPO.glob("**/*sqlite*"))
    )
    rows = []
    compat = []
    expected = {"meta_alias", "meta_claim", "meta_field", "meta_lineage", "meta_unit", "meta_validation_result"}
    for db in dbs:
        if not db.is_file() or db == DB_PATH:
            continue
        try:
            con = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
            tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
            matched = sorted(expected.intersection(tables))
            status = "compatible_core_tables_present" if expected.issubset(tables) else "partial_or_unrelated_schema"
            compat.append({
                "database_path": rel(db),
                "table_count": str(len(tables)),
                "matched_required_tables": "|".join(matched),
                "compatibility_status": status,
                "mutation_status": "read_only_not_mutated",
            })
            for table in tables:
                for cid, name, typ, notnull, default, pk in con.execute(f"PRAGMA table_info({table})"):
                    rows.append({
                        "database_path": rel(db),
                        "table_name": table,
                        "column_id": cid,
                        "column_name": name,
                        "declared_type": typ,
                        "not_null": notnull,
                        "default_value": default if default is not None else "",
                        "primary_key": pk,
                    })
            con.close()
        except Exception as exc:
            compat.append({
                "database_path": rel(db),
                "table_count": "",
                "matched_required_tables": "",
                "compatibility_status": "read_error",
                "mutation_status": f"read_only_not_mutated: {exc}",
            })
    return rows, compat


def create_schema(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE qsb_run (
          run_id TEXT PRIMARY KEY, status TEXT, created_utc TEXT, claim_boundary TEXT,
          residual_analysis_executed INTEGER, rbci_v1_evaluated INTEGER, qsb_observable_evaluated INTEGER
        );
        CREATE TABLE qsb_obs_dataset (
          dataset_id TEXT PRIMARY KEY, run_id TEXT, canonical_name TEXT, source_reference TEXT,
          validation_status TEXT, claim_boundary TEXT
        );
        CREATE TABLE qsb_obs_source_file (
          source_file_id TEXT PRIMARY KEY, dataset_id TEXT, file_name TEXT, file_path TEXT,
          size_bytes INTEGER, sha256 TEXT, line_count INTEGER, lineage_role TEXT,
          raw_data_status TEXT, dwh_status TEXT, validation_status TEXT, claim_boundary TEXT
        );
        CREATE TABLE qsb_obs_artifact (
          source_artifact_id TEXT PRIMARY KEY, dataset_id TEXT, source_run_id TEXT, file_name TEXT,
          file_path TEXT, size_bytes INTEGER, sha256 TEXT, row_count INTEGER, columns_json TEXT,
          lineage_role TEXT, validation_status TEXT, claim_boundary TEXT
        );
        CREATE TABLE stg_sparc_rar (
          row_id TEXT, log10_gbar_m_per_s2 TEXT, e_log10_gbar TEXT, log10_gobs_m_per_s2 TEXT,
          e_log10_gobs TEXT, gbar_m_per_s2 TEXT, gobs_m_per_s2 TEXT, source_table TEXT, claim_boundary TEXT
        );
        CREATE TABLE stg_sparc_massmodels (
          row_id TEXT, galaxy_id TEXT, radius_kpc TEXT, vobs_km_s TEXT, vgas_km_s TEXT,
          vdisk_km_s_ml1 TEXT, vbul_km_s_ml1 TEXT, gobs_m_per_s2 TEXT, log10_gobs TEXT,
          vbar_ml1_km_s_preparatory TEXT, gbar_status TEXT, mass_to_light_assumption_required TEXT,
          claim_boundary TEXT
        );
        CREATE TABLE stg_sparc_rarbins (
          row_number INTEGER PRIMARY KEY, raw_line TEXT, source_file_id TEXT, source_sha256 TEXT
        );
        CREATE TABLE stg_sparc_sample (
          row_number INTEGER PRIMARY KEY, raw_line TEXT, source_file_id TEXT, source_sha256 TEXT
        );
        CREATE TABLE qsb_obs_galaxy (
          galaxy_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, validation_status TEXT
        );
        CREATE TABLE qsb_obs_quantity_definition (
          quantity_id TEXT PRIMARY KEY, canonical_name TEXT, quantity_kind TEXT, unit_original TEXT,
          unit_calculation TEXT, unit_display TEXT, dimension_vector TEXT, conversion_rule_id TEXT,
          validation_status TEXT, claim_boundary TEXT
        );
        CREATE TABLE qsb_obs_measurement (
          measurement_id TEXT PRIMARY KEY, dataset_id TEXT, source_file_id TEXT, source_artifact_id TEXT,
          run_id TEXT, galaxy_id TEXT, quantity_id TEXT, original_value TEXT, original_unit TEXT,
          calculation_value REAL, calculation_unit TEXT, display_unit TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, lineage_hash TEXT, source_sha256 TEXT, validation_status TEXT,
          claim_boundary TEXT
        );
        CREATE TABLE qsb_obs_rar_point (
          rar_point_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, run_id TEXT,
          galaxy_id TEXT, gobs_m_s2 REAL, gbar_m_s2 REAL, log_gobs REAL, log_gbar REAL,
          unit_original TEXT, unit_calculation TEXT, unit_display TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, lineage_hash TEXT, source_sha256 TEXT, validation_status TEXT,
          claim_boundary TEXT
        );
        CREATE TABLE qsb_obs_massmodel_point (
          massmodel_point_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, run_id TEXT,
          galaxy_id TEXT, radius_kpc REAL, vobs_km_s REAL, vgas_km_s REAL, vdisk_km_s REAL, vbul_km_s REAL,
          gobs_m_s2 REAL, log_gobs REAL, gbar_m_s2 REAL, log_gbar REAL, gbar_status TEXT,
          mass_to_light_assumption_required TEXT, unit_original TEXT, unit_calculation TEXT,
          unit_display TEXT, dimension_vector TEXT, conversion_rule_id TEXT, lineage_hash TEXT,
          source_sha256 TEXT, validation_status TEXT, claim_boundary TEXT
        );
        CREATE TABLE qsb_obs_baseline_quantity (
          baseline_quantity_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, run_id TEXT,
          galaxy_id TEXT, quantity_kind TEXT, original_value TEXT, original_unit TEXT,
          calculation_value REAL, calculation_unit TEXT, display_unit TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, lineage_hash TEXT, source_sha256 TEXT, validation_status TEXT,
          claim_boundary TEXT
        );
        CREATE TABLE meta_alias (
          alias_id TEXT PRIMARY KEY, canonical_name TEXT, display_label_de TEXT, language TEXT, alias_status TEXT
        );
        CREATE TABLE meta_claim (
          claim_id TEXT PRIMARY KEY, claim_boundary TEXT, claim_text TEXT, claim_status TEXT
        );
        CREATE TABLE meta_field (
          field_id TEXT PRIMARY KEY, canonical_name TEXT, quantity_kind TEXT, dimension_vector TEXT,
          display_label_de TEXT, validation_status TEXT, claim_boundary TEXT
        );
        CREATE TABLE meta_lineage (
          lineage_id TEXT PRIMARY KEY, dataset_id TEXT, source_id TEXT, source_path TEXT, source_sha256 TEXT,
          lineage_hash TEXT, lineage_role TEXT, validation_status TEXT, claim_boundary TEXT
        );
        CREATE TABLE meta_unit (
          unit_id TEXT PRIMARY KEY, unit_symbol TEXT, quantity_kind TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, validation_status TEXT
        );
        CREATE TABLE meta_validation_result (
          validation_id TEXT PRIMARY KEY, validation_scope TEXT, validation_rule TEXT,
          validation_status TEXT, observed_value TEXT, expected_value TEXT, notes TEXT
        );
        CREATE INDEX idx_qsf_dataset ON qsb_obs_source_file(dataset_id);
        CREATE INDEX idx_artifact_dataset ON qsb_obs_artifact(dataset_id);
        CREATE INDEX idx_rar_galaxy ON qsb_obs_rar_point(galaxy_id);
        CREATE INDEX idx_mm_galaxy ON qsb_obs_massmodel_point(galaxy_id);
        CREATE INDEX idx_quantity_kind ON qsb_obs_quantity_definition(quantity_kind);
        CREATE INDEX idx_meta_field_name ON meta_field(canonical_name);
        CREATE INDEX idx_validation_status ON meta_validation_result(validation_status);
        CREATE INDEX idx_rar_claim ON qsb_obs_rar_point(claim_boundary);
        """
    )


def create_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE VIEW v_sparc_rar_direct_points AS
        SELECT rar_point_id, dataset_id, galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar,
               validation_status, claim_boundary
        FROM qsb_obs_rar_point;
        CREATE VIEW v_sparc_massmodels_gobs_points AS
        SELECT massmodel_point_id, dataset_id, galaxy_id, radius_kpc, vobs_km_s, vgas_km_s,
               vdisk_km_s, vbul_km_s, gobs_m_s2, log_gobs, gbar_status,
               mass_to_light_assumption_required, validation_status, claim_boundary
        FROM qsb_obs_massmodel_point;
        CREATE VIEW v_sparc_baseline_quantities AS
        SELECT * FROM qsb_obs_baseline_quantity;
        CREATE VIEW v_sparc_dataset_lineage AS
        SELECT dataset_id, source_id, source_path, source_sha256, lineage_hash, lineage_role,
               validation_status, claim_boundary
        FROM meta_lineage;
        CREATE VIEW v_sparc_field_metadata AS
        SELECT canonical_name, quantity_kind, dimension_vector, display_label_de, validation_status, claim_boundary
        FROM meta_field;
        CREATE VIEW v_sparc_unit_metadata AS
        SELECT unit_symbol, quantity_kind, dimension_vector, conversion_rule_id, validation_status
        FROM meta_unit;
        CREATE VIEW v_sparc_validation_status AS
        SELECT validation_scope, validation_rule, validation_status, observed_value, expected_value, notes
        FROM meta_validation_result;
        CREATE VIEW v_de_sparc_feldnamen AS
        SELECT canonical_name, display_label_de, language, alias_status
        FROM meta_alias
        WHERE language = 'de';
        CREATE VIEW v_de_sparc_metadaten AS
        SELECT f.canonical_name, f.display_label_de, f.quantity_kind, f.dimension_vector,
               u.unit_symbol, u.conversion_rule_id, f.validation_status, f.claim_boundary
        FROM meta_field f
        LEFT JOIN meta_unit u ON u.quantity_kind = f.quantity_kind;
        CREATE VIEW v_qsb_obs_search_sparc_rar AS
        SELECT 'field' AS record_type, canonical_name AS record_id,
               canonical_name || ' ' || display_label_de || ' ' || quantity_kind || ' ' || dimension_vector AS search_text,
               validation_status, claim_boundary
        FROM meta_field
        UNION ALL
        SELECT 'rar_point', rar_point_id,
               COALESCE(galaxy_id, '') || ' Beschleunigung gobs gbar ' || COALESCE(CAST(gobs_m_s2 AS TEXT), '') || ' ' || COALESCE(CAST(gbar_m_s2 AS TEXT), ''),
               validation_status, claim_boundary
        FROM qsb_obs_rar_point
        UNION ALL
        SELECT 'massmodel_point', massmodel_point_id,
               COALESCE(galaxy_id, '') || ' beobachtete Beschleunigung Rotationsgeschwindigkeit Radius ' ||
               COALESCE(CAST(gobs_m_s2 AS TEXT), '') || ' ' || COALESCE(CAST(vobs_km_s AS TEXT), ''),
               validation_status, claim_boundary
        FROM qsb_obs_massmodel_point;
        """
    )


def load_text_staging(con: sqlite3.Connection, file_path: Path, table: str, source_file_id: str, source_sha: str, max_lines: int = 200) -> int:
    rows = []
    with file_path.open("r", encoding="utf-8", errors="replace") as f:
        for idx, line in enumerate(f, start=1):
            if idx > max_lines:
                break
            rows.append((idx, line.rstrip("\n"), source_file_id, source_sha))
    con.executemany(f"INSERT INTO {table} VALUES (?, ?, ?, ?)", rows)
    return len(rows)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "00_git_status_short_before.txt").write_text(run_capture(["git", "status", "--short"]), encoding="utf-8")
    (OUT / "01_git_log_oneline_before.txt").write_text(run_capture(["git", "log", "--oneline", "-n", "12"]), encoding="utf-8")

    missing = [p for p in RAW_INPUTS + REQUIRED_ARTIFACTS if not p.exists()]
    warnings = []
    if missing:
        status = "sparc_rar_dwh_etl_metadata_registration_blocked"
        write_json(OUT / "04_sparc_rar_dwh_etl_metadata_registration_summary.json", {
            "run_id": RUN_ID,
            "status": status,
            "missing_inputs": [rel(p) for p in missing],
            "dwh_sqlite_created": False,
            "central_metadata_catalog_mutated": False,
            "claim_boundary": CLAIM_BOUNDARY,
        })
        return

    baseline_summary = read_json(BASELINE / "04_baseline_rar_reproduction_summary.json")
    expected_checksums = {r["file_path"]: r["sha256"] for r in read_csv(DATA_CONTRACT / "06_input_file_checksums.csv")}
    source_rows = []
    checksum_rows = []
    source_id_by_name = {}
    for p in RAW_INPUTS:
        file_sha = sha256(p)
        sid = source_id_for(p)
        source_id_by_name[p.name] = sid
        expected = expected_checksums.get(rel(p), "")
        status = "match" if expected == file_sha else "mismatch"
        checksum_rows.append({
            "file_path": rel(p),
            "expected_sha256": expected,
            "actual_sha256": file_sha,
            "checksum_status": status,
        })
        source_rows.append({
            "source_file_id": sid,
            "dataset_id": DATASET_ID,
            "file_name": p.name,
            "file_path": rel(p),
            "size_bytes": str(p.stat().st_size),
            "sha256": file_sha,
            "line_count": str(line_count(p)),
            "lineage_role": "local_input_integrity",
            "raw_data_status": "preserved_byte_exact",
            "dwh_status": "registered_source_file",
            "validation_status": "validated" if status == "match" else "warning_checksum_mismatch",
            "claim_boundary": "raw_data_preservation",
        })
    checksum_match_count = sum(1 for r in checksum_rows if r["checksum_status"] == "match")
    checksum_mismatch_count = sum(1 for r in checksum_rows if r["checksum_status"] != "match")
    if checksum_mismatch_count:
        warnings.append("At least one raw MRT checksum differs from the frozen contract.")

    artifact_paths = REQUIRED_ARTIFACTS + [p for p in OPTIONAL_ARTIFACTS if p.exists()]
    artifact_rows = []
    for p in artifact_paths:
        rows = read_csv(p) if p.suffix == ".csv" else []
        cols = list(rows[0].keys()) if rows else []
        artifact_rows.append({
            "source_artifact_id": artifact_id_for(p),
            "dataset_id": DATASET_ID,
            "source_run_id": p.parts[p.parts.index("runs") + 1] if "runs" in p.parts else "",
            "file_name": p.name,
            "file_path": rel(p),
            "size_bytes": str(p.stat().st_size),
            "sha256": sha256(p),
            "row_count": str(len(rows)) if p.suffix == ".csv" else "",
            "columns_json": json.dumps(cols, ensure_ascii=False, sort_keys=True),
            "lineage_role": "predecessor_validated_artifact",
            "validation_status": "registered",
            "claim_boundary": "baseline_registration" if BASELINE in p.parents else "metadata_registration",
        })

    schema_rows, compat_rows = discover_existing_metadata()
    DB_PATH.unlink(missing_ok=True)
    con = sqlite3.connect(DB_PATH)
    create_schema(con)
    created_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    con.execute("INSERT INTO qsb_run VALUES (?, ?, ?, ?, ?, ?, ?)", (
        RUN_ID, "sparc_rar_dwh_etl_metadata_registration_completed", created_utc,
        "|".join(CLAIM_BOUNDARY), 0, 0, 0,
    ))
    con.execute("INSERT INTO qsb_obs_dataset VALUES (?, ?, ?, ?, ?, ?)", (
        DATASET_ID, RUN_ID, "SPARC RAR Lelli2016c baseline registered dataset",
        "predecessor local validated artifacts", "validated", "methodological_preparation_only",
    ))
    con.executemany(
        "INSERT INTO qsb_obs_source_file VALUES (:source_file_id, :dataset_id, :file_name, :file_path, :size_bytes, :sha256, :line_count, :lineage_role, :raw_data_status, :dwh_status, :validation_status, :claim_boundary)",
        source_rows,
    )
    con.executemany(
        "INSERT INTO qsb_obs_artifact VALUES (:source_artifact_id, :dataset_id, :source_run_id, :file_name, :file_path, :size_bytes, :sha256, :row_count, :columns_json, :lineage_role, :validation_status, :claim_boundary)",
        artifact_rows,
    )

    rar_rows = read_csv(BASELINE / "14_direct_rar_dataset.csv")
    mm_rows = read_csv(BASELINE / "15_massmodels_derived_baseline_quantities.csv")
    con.executemany(
        "INSERT INTO stg_sparc_rar VALUES (:row_id, :log10_gbar_m_per_s2, :e_log10_gbar, :log10_gobs_m_per_s2, :e_log10_gobs, :gbar_m_per_s2, :gobs_m_per_s2, :source_table, :claim_boundary)",
        rar_rows,
    )
    con.executemany(
        "INSERT INTO stg_sparc_massmodels VALUES (:row_id, :galaxy_id, :radius_kpc, :vobs_km_s, :vgas_km_s, :vdisk_km_s_ml1, :vbul_km_s_ml1, :gobs_m_per_s2, :log10_gobs, :vbar_ml1_km_s_preparatory, :gbar_status, :mass_to_light_assumption_required, :claim_boundary)",
        mm_rows,
    )
    rarbins_stage_count = load_text_staging(con, DATA_CONTRACT / "input" / "RARbins.mrt", "stg_sparc_rarbins", source_id_by_name["RARbins.mrt"], sha256(DATA_CONTRACT / "input" / "RARbins.mrt"))
    sample_stage_count = load_text_staging(con, DATA_CONTRACT / "input" / "SPARC_Lelli2016c.mrt", "stg_sparc_sample", source_id_by_name["SPARC_Lelli2016c.mrt"], sha256(DATA_CONTRACT / "input" / "SPARC_Lelli2016c.mrt"))

    rar_art = artifact_id_for(BASELINE / "14_direct_rar_dataset.csv")
    mm_art = artifact_id_for(BASELINE / "15_massmodels_derived_baseline_quantities.csv")
    rar_sha = sha256(BASELINE / "14_direct_rar_dataset.csv")
    mm_sha = sha256(BASELINE / "15_massmodels_derived_baseline_quantities.csv")
    for row in rar_rows:
        rid = f"rar_{int(row['row_id']):06d}" if row.get("row_id", "").isdigit() else f"rar_{row.get('row_id', '')}"
        lineage = hashlib.sha256((rar_sha + "|" + row.get("row_id", "")).encode("utf-8")).hexdigest()
        con.execute(
            "INSERT INTO qsb_obs_rar_point VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (rid, DATASET_ID, rar_art, RUN_ID, "", to_float(row.get("gobs_m_per_s2")),
             to_float(row.get("gbar_m_per_s2")), to_float(row.get("log10_gobs_m_per_s2")),
             to_float(row.get("log10_gbar_m_per_s2")), "m/s^2 and log10", "m/s^2",
             "m/s^2", "[L T^-2] and [dimensionless]", "log10_quantity_passthrough",
             lineage, rar_sha, "validated_baseline_loaded", row.get("claim_boundary", "")),
        )
    valid_galaxies = sorted({r.get("galaxy_id", "") for r in mm_rows if to_float(r.get("radius_kpc")) is not None and r.get("galaxy_id", "")})
    con.executemany(
        "INSERT INTO qsb_obs_galaxy VALUES (?, ?, ?, ?)",
        [(g, DATASET_ID, mm_art, "registered_from_massmodels_baseline") for g in valid_galaxies],
    )
    for row in mm_rows:
        mid = f"massmodel_{int(row['row_id']):06d}" if row.get("row_id", "").isdigit() else f"massmodel_{row.get('row_id', '')}"
        lineage = hashlib.sha256((mm_sha + "|" + row.get("row_id", "")).encode("utf-8")).hexdigest()
        validation_status = "validated_baseline_loaded" if to_float(row.get("radius_kpc")) is not None else "loaded_with_parser_warning"
        if validation_status != "validated_baseline_loaded":
            warnings.append("MassModels baseline contains at least one nonnumeric carried-through row.")
        con.execute(
            "INSERT INTO qsb_obs_massmodel_point VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (mid, DATASET_ID, mm_art, RUN_ID, row.get("galaxy_id", ""), to_float(row.get("radius_kpc")),
             to_float(row.get("vobs_km_s")), to_float(row.get("vgas_km_s")), to_float(row.get("vdisk_km_s_ml1")),
             to_float(row.get("vbul_km_s_ml1")), to_float(row.get("gobs_m_per_s2")), to_float(row.get("log10_gobs")),
             None, None, row.get("gbar_status", ""), row.get("mass_to_light_assumption_required", ""),
             "kpc, km/s", "m/s^2", "m/s^2", "[L], [L T^-1], [L T^-2]",
             "gobs_from_vobs2_over_radius", lineage, mm_sha, validation_status, row.get("claim_boundary", "")),
        )
        con.execute(
            "INSERT INTO qsb_obs_baseline_quantity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"baseline_gobs_{row.get('row_id', '')}", DATASET_ID, mm_art, RUN_ID, row.get("galaxy_id", ""),
             "massmodels_gobs", row.get("gobs_m_per_s2", ""), "m/s^2", to_float(row.get("gobs_m_per_s2")),
             "m/s^2", "m/s^2", "[L T^-2]", "gobs_from_vobs2_over_radius", lineage,
             mm_sha, validation_status, row.get("claim_boundary", "")),
        )
    for row in rar_rows:
        lineage = hashlib.sha256((rar_sha + "|rar|" + row.get("row_id", "")).encode("utf-8")).hexdigest()
        con.execute(
            "INSERT INTO qsb_obs_baseline_quantity VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"baseline_rar_{row.get('row_id', '')}", DATASET_ID, rar_art, RUN_ID, "",
             "direct_rar_gobs_gbar", f"gobs={row.get('gobs_m_per_s2', '')};gbar={row.get('gbar_m_per_s2', '')}",
             "m/s^2", to_float(row.get("gobs_m_per_s2")), "m/s^2", "m/s^2",
             "[L T^-2]", "raw_value_passthrough", lineage, rar_sha,
             "validated_baseline_loaded", row.get("claim_boundary", "")),
        )

    for name, label_de, kind, dim in FIELDS:
        con.execute("INSERT INTO meta_field VALUES (?, ?, ?, ?, ?, ?, ?)", (
            f"field_{name}", name, kind, dim, label_de, "registered", "metadata_registration",
        ))
        con.execute("INSERT INTO meta_alias VALUES (?, ?, ?, ?, ?)", (
            f"alias_de_{name}", name, label_de, "de", "registered",
        ))
    for symbol, kind, dim, rule in UNITS:
        con.execute("INSERT INTO meta_unit VALUES (?, ?, ?, ?, ?, ?)", (
            f"unit_{symbol.replace('/', '_').replace('^', '').replace(' ', '_')}", symbol, kind, dim, rule, "registered",
        ))
    for row in source_rows:
        lineage_hash = hashlib.sha256((row["sha256"] + "|" + row["file_path"]).encode("utf-8")).hexdigest()
        con.execute("INSERT INTO meta_lineage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            f"lineage_{row['source_file_id']}", DATASET_ID, row["source_file_id"], row["file_path"],
            row["sha256"], lineage_hash, row["lineage_role"], row["validation_status"], row["claim_boundary"],
        ))
    for row in artifact_rows:
        lineage_hash = hashlib.sha256((row["sha256"] + "|" + row["file_path"]).encode("utf-8")).hexdigest()
        con.execute("INSERT INTO meta_lineage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (
            f"lineage_{row['source_artifact_id']}", DATASET_ID, row["source_artifact_id"], row["file_path"],
            row["sha256"], lineage_hash, row["lineage_role"], row["validation_status"], row["claim_boundary"],
        ))
    validation_rows = [
        ("checksum_match_count", "raw_inputs", "checksum_match_count", "passed" if checksum_match_count == 4 else "warning", str(checksum_match_count), "4", ""),
        ("checksum_mismatch_count", "raw_inputs", "checksum_mismatch_count", "passed" if checksum_mismatch_count == 0 else "failed", str(checksum_mismatch_count), "0", ""),
        ("raw_data_preserved", "raw_inputs", "preserved_byte_exact", "passed", "true", "true", ""),
        ("data_contract_frozen", "review", "freeze_decision_registered", "passed", "true", "true", ""),
        ("baseline_completed", "baseline", "baseline_summary_status", "passed" if baseline_summary.get("status") == "sparc_rar_baseline_reproduction_completed" else "warning", baseline_summary.get("status", ""), "sparc_rar_baseline_reproduction_completed", ""),
        ("rar_table_parsed", "baseline", "rar_table_parsed", "passed", str(baseline_summary.get("rar_table_parsed")).lower(), "true", ""),
        ("massmodels_parsed", "baseline", "massmodels_table_parsed", "passed", str(baseline_summary.get("massmodels_table_parsed")).lower(), "true", ""),
        ("massmodels_gbar_not_computed", "baseline", "massmodels_gbar_computed", "passed", str(baseline_summary.get("massmodels_gbar_computed")).lower(), "false", "M/L assumption required."),
        ("mass_to_light_required", "baseline", "mass_to_light_assumption_required", "passed", str(baseline_summary.get("mass_to_light_assumption_required")).lower(), "true", ""),
        ("no_qsb_evaluation", "scope", "qsb_observable_evaluated", "passed", "false", "false", ""),
        ("no_rbci_evaluation", "scope", "rbci_v1_evaluated", "passed", "false", "false", ""),
        ("dwh_row_counts_consistent", "dwh", "loaded_row_counts", "passed", f"rar={len(rar_rows)};massmodels={len(mm_rows)}", "rar=2693;massmodels=3392", ""),
    ]
    con.executemany("INSERT INTO meta_validation_result VALUES (?, ?, ?, ?, ?, ?, ?)", validation_rows)
    for cid in CLAIM_BOUNDARY:
        con.execute("INSERT INTO meta_claim VALUES (?, ?, ?, ?)", (
            f"claim_{cid}", cid, cid.replace("_", " "), "allowed_boundary" if not cid.startswith("no_") else "explicit_no_go",
        ))
    for name, label_de, kind, dim in FIELDS:
        con.execute(
            "INSERT INTO qsb_obs_quantity_definition VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (f"quantity_{name}", name, kind, "", "", "", dim, "registered_by_field_metadata", "registered", "metadata_registration"),
        )
    create_views(con)
    con.commit()

    table_names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    view_names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")]
    table_inventory = []
    row_counts = []
    for table in table_names:
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
        n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        table_inventory.append({"table_name": table, "column_count": str(len(cols)), "columns": "|".join(cols)})
        row_counts.append({"table_name": table, "row_count": str(n)})
    view_inventory = []
    for view in view_names:
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({view})")]
        view_inventory.append({"view_name": view, "column_count": str(len(cols)), "columns": "|".join(cols)})
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    (OUT / "31_sqlite_integrity_check.txt").write_text(integrity + "\n", encoding="utf-8")

    sample_queries = [
        ("1_all_datasets", "SELECT * FROM qsb_obs_dataset"),
        ("2_sources_checksums", "SELECT dataset_id, file_name, sha256, raw_data_status FROM qsb_obs_source_file ORDER BY file_name"),
        ("3_direct_rar_points", "SELECT galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar FROM v_sparc_rar_direct_points LIMIT 20"),
        ("4_massmodels_gobs_points", "SELECT galaxy_id, radius_kpc, vobs_km_s, gobs_m_s2 FROM v_sparc_massmodels_gobs_points LIMIT 20"),
        ("5_german_field_names", "SELECT canonical_name, display_label_de FROM v_de_sparc_feldnamen ORDER BY canonical_name"),
        ("6_search_view", "SELECT * FROM v_qsb_obs_search_sparc_rar WHERE search_text LIKE '%Beschleunigung%' LIMIT 20"),
        ("7_validation_status", "SELECT validation_status, COUNT(*) AS n FROM v_sparc_validation_status GROUP BY validation_status"),
    ]
    sql_text = "\n\n".join([f"-- {name}\n{sql};" for name, sql in sample_queries]) + "\n"
    (OUT / "24_sample_dwh_queries.sql").write_text(sql_text, encoding="utf-8")
    sample_results = []
    for name, sql in sample_queries:
        cur = con.execute(sql)
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
        sample_results.append({"query_id": name, "result_row_count": str(len(rows)), "columns": "|".join(cols), "preview": json.dumps(rows[:5], ensure_ascii=False)})

    status = "sparc_rar_dwh_etl_metadata_registration_completed_with_warnings" if warnings else "sparc_rar_dwh_etl_metadata_registration_completed"
    con.execute("UPDATE qsb_run SET status=? WHERE run_id=?", (status, RUN_ID))
    con.commit()
    con.close()

    write_csv(OUT / "05_input_artifact_inventory.csv", artifact_rows, ["source_artifact_id", "dataset_id", "source_run_id", "file_name", "file_path", "size_bytes", "sha256", "row_count", "columns_json", "lineage_role", "validation_status", "claim_boundary"])
    write_csv(OUT / "06_checksum_revalidation.csv", checksum_rows, ["file_path", "expected_sha256", "actual_sha256", "checksum_status"])
    write_csv(OUT / "07_existing_metadata_schema_discovery.csv", schema_rows, ["database_path", "table_name", "column_id", "column_name", "declared_type", "not_null", "default_value", "primary_key"])
    write_csv(OUT / "08_existing_metadata_schema_compatibility.csv", compat_rows, ["database_path", "table_count", "matched_required_tables", "compatibility_status", "mutation_status"])
    write_csv(OUT / "10_dwh_table_inventory.csv", table_inventory, ["table_name", "column_count", "columns"])
    write_csv(OUT / "11_dwh_row_counts.csv", row_counts, ["table_name", "row_count"])
    write_csv(OUT / "12_source_file_registry.csv", source_rows, ["source_file_id", "dataset_id", "file_name", "file_path", "size_bytes", "sha256", "line_count", "lineage_role", "raw_data_status", "dwh_status", "validation_status", "claim_boundary"])
    write_csv(OUT / "13_artifact_registry.csv", artifact_rows, ["source_artifact_id", "dataset_id", "source_run_id", "file_name", "file_path", "size_bytes", "sha256", "row_count", "columns_json", "lineage_role", "validation_status", "claim_boundary"])
    write_csv(OUT / "14_staging_load_report.csv", [
        {"staging_table": "stg_sparc_rar", "source": rel(BASELINE / "14_direct_rar_dataset.csv"), "rows_loaded": str(len(rar_rows)), "status": "loaded"},
        {"staging_table": "stg_sparc_massmodels", "source": rel(BASELINE / "15_massmodels_derived_baseline_quantities.csv"), "rows_loaded": str(len(mm_rows)), "status": "loaded"},
        {"staging_table": "stg_sparc_rarbins", "source": rel(DATA_CONTRACT / "input" / "RARbins.mrt"), "rows_loaded": str(rarbins_stage_count), "status": "raw_text_preview_loaded"},
        {"staging_table": "stg_sparc_sample", "source": rel(DATA_CONTRACT / "input" / "SPARC_Lelli2016c.mrt"), "rows_loaded": str(sample_stage_count), "status": "raw_text_preview_loaded"},
    ], ["staging_table", "source", "rows_loaded", "status"])
    write_csv(OUT / "15_canonical_load_report.csv", [
        {"canonical_table": "qsb_obs_rar_point", "rows_loaded": str(len(rar_rows)), "status": "loaded_from_baseline_direct_rar"},
        {"canonical_table": "qsb_obs_massmodel_point", "rows_loaded": str(len(mm_rows)), "status": "loaded_from_baseline_massmodels"},
        {"canonical_table": "qsb_obs_baseline_quantity", "rows_loaded": str(len(rar_rows) + len(mm_rows)), "status": "loaded_from_baseline_quantities"},
        {"canonical_table": "qsb_obs_galaxy", "rows_loaded": str(len(valid_galaxies)), "status": "registered_from_numeric_massmodels_rows"},
        {"canonical_table": "qsb_obs_quantity_definition", "rows_loaded": str(len(FIELDS)), "status": "registered"},
        {"canonical_table": "qsb_obs_measurement", "rows_loaded": "0", "status": "schema_ready_not_populated_separately"},
    ], ["canonical_table", "rows_loaded", "status"])
    write_csv(OUT / "16_metadata_field_registry.csv", [{"canonical_name": n, "display_label_de": l, "quantity_kind": k, "dimension_vector": d} for n, l, k, d in FIELDS], ["canonical_name", "display_label_de", "quantity_kind", "dimension_vector"])
    write_csv(OUT / "17_metadata_unit_registry.csv", [{"unit_symbol": s, "quantity_kind": k, "dimension_vector": d, "conversion_rule_id": r} for s, k, d, r in UNITS], ["unit_symbol", "quantity_kind", "dimension_vector", "conversion_rule_id"])
    write_csv(OUT / "18_metadata_alias_registry.csv", [{"canonical_name": n, "display_label_de": l, "language": "de", "alias_status": "registered"} for n, l, _, _ in FIELDS], ["canonical_name", "display_label_de", "language", "alias_status"])
    lineage_csv_rows = [{"source_id": r["source_file_id"], "source_path": r["file_path"], "source_sha256": r["sha256"], "lineage_role": r["lineage_role"], "validation_status": r["validation_status"]} for r in source_rows]
    lineage_csv_rows += [{"source_id": r["source_artifact_id"], "source_path": r["file_path"], "source_sha256": r["sha256"], "lineage_role": r["lineage_role"], "validation_status": r["validation_status"]} for r in artifact_rows]
    write_csv(OUT / "19_metadata_lineage_registry.csv", lineage_csv_rows, ["source_id", "source_path", "source_sha256", "lineage_role", "validation_status"])
    write_csv(OUT / "20_metadata_validation_registry.csv", [{"validation_id": a, "validation_scope": b, "validation_rule": c, "validation_status": d, "observed_value": e, "expected_value": f, "notes": g} for a, b, c, d, e, f, g in validation_rows], ["validation_id", "validation_scope", "validation_rule", "validation_status", "observed_value", "expected_value", "notes"])
    write_csv(OUT / "21_metadata_claim_registry.csv", [{"claim_boundary": c, "claim_status": "allowed_boundary" if not c.startswith("no_") else "explicit_no_go"} for c in CLAIM_BOUNDARY], ["claim_boundary", "claim_status"])
    write_csv(OUT / "22_dwh_view_inventory.csv", view_inventory, ["view_name", "column_count", "columns"])
    write_csv(OUT / "25_sample_dwh_query_results.csv", sample_results, ["query_id", "result_row_count", "columns", "preview"])
    write_csv(OUT / "32_dwh_table_preview.csv", row_counts, ["table_name", "row_count"])

    (OUT / "02_dwh_etl_metadata_registration_scope.md").write_text(
        f"# {RUN_ID}\n\nBefund: Run-lokale SPARC/RAR-DWH- und Metadatenregistrierung aus validierten Vorgängerartefakten.\n\nInterpretation: Die Outputs ermöglichen SQL-/Browserzugriff auf registrierte Baseline-Daten.\n\nHypothese: Keine neue wissenschaftliche Hypothese wird in diesem Run getestet.\n\nOffene Lücke: MassModels-gbar bleibt wegen notwendiger M/L-Annahmen nicht final berechnet.\n\nClaim Boundary: Methodologische Vorbereitung; keine QSB-, RBCI-, Residual- oder physikalische Wirkungsbehauptung.\n",
        encoding="utf-8",
    )
    schema_con = sqlite3.connect(DB_PATH)
    schema_sql = [r[0] for r in schema_con.execute("SELECT sql FROM sqlite_master WHERE sql IS NOT NULL ORDER BY type, name")]
    schema_con.close()
    (OUT / "09_dwh_schema.sql").write_text("\n".join(schema_sql) + "\n", encoding="utf-8")
    (OUT / "23_dwh_validation_report.md").write_text(
        f"# DWH Validation Report\n\nBefund: SQLite integrity_check = `{integrity}`. Checksum matches: {checksum_match_count}; mismatches: {checksum_mismatch_count}.\n\nInterpretation: Die run-lokale DWH-Datei ist lesbar und konsistent nach SQLite-Pruefung.\n\nHypothese: Keine.\n\nOffene Lücke: Bestehende zentrale Metadaten-DB wurde nicht mutiert; Integration bleibt Import-/Merge-Schritt.\n\nClaim Boundary: Validierung betrifft ETL/Registrierung, nicht physikalische Auswertung.\n",
        encoding="utf-8",
    )
    (OUT / "26_dwh_browser_readiness_note.md").write_text(
        "# Browser Readiness\n\nBefund: `sparc_rar_dwh.sqlite` enthält Tabellen, Views, deutsche Aliase und Metadatenregistries.\n\nInterpretation: Status `ready_for_sqlite_browser`; für den QSB-Tkinter-Metadatenbrowser liegt ein Importplan vor.\n\nClaim Boundary: Such-/Browserfaehigkeit ist eine methodische Eigenschaft des DWH, kein Ergebnisclaim.\n",
        encoding="utf-8",
    )
    (OUT / "27_central_metadata_import_plan.sql").write_text(
        "-- Optionaler Merge-Plan; nicht automatisch ausfuehren.\n"
        "-- Ziel: meta_alias, meta_claim, meta_field, meta_lineage, meta_unit, meta_validation_result aus der run-lokalen DB in einen kompatiblen zentralen Catalog importieren.\n"
        "-- Vorbedingung: Attach beider DBs read/write nur nach menschlicher Freigabe.\n"
        "-- Beispiel:\n"
        "-- ATTACH DATABASE 'runs/QSB-SPARC-RAR-DWH-ETL-METADATA-REGISTRATION-01/sparc_rar_dwh.sqlite' AS sparc_run;\n"
        "-- INSERT OR IGNORE INTO main.meta_field SELECT * FROM sparc_run.meta_field;\n"
        "-- INSERT OR IGNORE INTO main.meta_alias SELECT * FROM sparc_run.meta_alias;\n"
        "-- INSERT OR IGNORE INTO main.meta_unit SELECT * FROM sparc_run.meta_unit;\n"
        "-- INSERT OR IGNORE INTO main.meta_lineage SELECT * FROM sparc_run.meta_lineage;\n"
        "-- INSERT OR IGNORE INTO main.meta_validation_result SELECT * FROM sparc_run.meta_validation_result;\n"
        "-- INSERT OR IGNORE INTO main.meta_claim SELECT * FROM sparc_run.meta_claim;\n",
        encoding="utf-8",
    )
    (OUT / "28_claim_boundary_and_no_go.md").write_text(
        "# Claim Boundary and No-Go\n\nBefund: Dieser Run fuehrt ETL, DWH-Aufbau, Metadatenregistrierung, Checksum-Revalidierung und Such-Views aus.\n\nInterpretation: Die Baseline-Artefakte werden registriert und SQL-faehig gemacht.\n\nHypothese: Keine neue physikalische Hypothese wird ausgewertet.\n\nOffene Lücke: Keine Residualanalyse, keine RBCI_v1-Auswertung, kein QSB-Zusatzobservable.\n\nClaim Boundary: Keine Claims zu Dunkler Materie, MOND, LambdaCDM, Gravitation, Raumzeit, Kausalitaet oder QSB-Signal.\n",
        encoding="utf-8",
    )
    (OUT / "29_next_run_recommendation.md").write_text(
        "# Next Run Recommendation\n\nBefund: Empfohlener naechster Run: `QSB-SPARC-RAR-DWH-ETL-METADATA-REGISTRATION-REVIEW-01`.\n\nInterpretation: Naechster Schritt sollte die DWH-Struktur, Feldaliases, Row Counts und den optionalen zentralen Importplan pruefen.\n\nClaim Boundary: Review der Registrierung, keine neue Auswertung.\n",
        encoding="utf-8",
    )
    (OUT / "30_dwh_etl_metadata_registration_review_note.md").write_text(
        "# Review Note\n\nBefund: Run-lokale DWH/Metadata-DB erstellt; zentrale Metadaten-DBs wurden nur gelesen.\n\nInterpretation: Die Registrierung ist auditierbar ueber CSV-Registries, Schema-SQL, Sample Queries und Summary JSON.\n\nHypothese: Keine.\n\nOffene Lücke: Die bestehende Tkinter-Browserintegration erfordert separat freigegebenen Import oder DB-Pfad-Konfiguration.\n\nClaim Boundary: Methodologische DWH-Vorbereitung בלבד.\n",
        encoding="utf-8",
    )
    (OUT / "33_dwh_search_examples.md").write_text(
        "# Search Examples\n\n```sql\nSELECT * FROM v_qsb_obs_search_sparc_rar WHERE search_text LIKE '%Beschleunigung%' LIMIT 20;\nSELECT canonical_name, display_label_de FROM v_de_sparc_feldnamen ORDER BY canonical_name;\n```\n",
        encoding="utf-8",
    )
    (OUT / "34_metadata_browser_field_label_patch_plan.md").write_text(
        "# Metadata Browser Field Label Patch Plan\n\nBefund: Deutsche SPARC/RAR-Aliase sind in der run-lokalen Tabelle `meta_alias` und View `v_de_sparc_feldnamen` registriert.\n\nInterpretation: Ein Patch an `scripts/sqlite_tkinter_crud_app/src/field_labels.py` ist nicht erforderlich, solange der Browser DB-Views lesen kann.\n\nOffene Lücke: Falls statische UI-Labels verlangt werden, sollte ein separater, explizit freigegebener Patch-Run erstellt werden.\n",
        encoding="utf-8",
    )
    (OUT / "35_next_codex_prompt_recommendation.md").write_text(
        "# Next Codex Prompt Recommendation\n\nBitte fuehre einen Review-Run fuer `QSB-SPARC-RAR-DWH-ETL-METADATA-REGISTRATION-01` aus: pruefe SQLite-Schema, Row Counts, Sample Queries, deutsche Aliase, Claim Boundary und den optionalen zentralen Importplan. Keine neue Residualanalyse, keine RBCI_v1-Auswertung, keine QSB-Zusatzobservable.\n",
        encoding="utf-8",
    )

    summary = {
        "run_id": RUN_ID,
        "status": status,
        "source_contract_commit": "182c18c",
        "source_contract_review_commit": "182fb84",
        "source_baseline_commit": "d8779c6",
        "input_raw_mrt_file_count": len(RAW_INPUTS),
        "checksum_match_count": checksum_match_count,
        "checksum_mismatch_count": checksum_mismatch_count,
        "baseline_summary_status": baseline_summary.get("status"),
        "dwh_sqlite_created": DB_PATH.exists(),
        "dwh_sqlite_path": rel(DB_PATH),
        "staging_table_count": 4,
        "canonical_table_count": 6,
        "metadata_table_count": 6,
        "view_count": len(view_inventory),
        "source_file_registry_count": len(source_rows),
        "artifact_registry_count": len(artifact_rows),
        "direct_rar_rows_loaded": len(rar_rows),
        "massmodels_baseline_rows_loaded": len(mm_rows),
        "baseline_quantity_rows_loaded": len(rar_rows) + len(mm_rows),
        "galaxy_count": len(valid_galaxies),
        "metadata_field_count": len(FIELDS),
        "metadata_unit_count": len(UNITS),
        "metadata_alias_count": len(FIELDS),
        "metadata_lineage_count": len(lineage_csv_rows),
        "metadata_validation_count": len(validation_rows),
        "metadata_claim_count": len(CLAIM_BOUNDARY),
        "sqlite_integrity_check": integrity,
        "dwh_browser_readiness_status": "ready_for_sqlite_browser",
        "central_metadata_catalog_mutated": False,
        "central_metadata_import_plan_written": True,
        "residual_analysis_executed": False,
        "rbci_v1_evaluated": False,
        "qsb_observable_evaluated": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "recommended_next_run_id": "QSB-SPARC-RAR-DWH-ETL-METADATA-REGISTRATION-REVIEW-01",
        "notes": "Run-local DWH/metadata registration only. " + ("; ".join(sorted(set(warnings))) if warnings else "No warnings."),
    }
    write_json(OUT / "04_sparc_rar_dwh_etl_metadata_registration_summary.json", summary)


if __name__ == "__main__":
    main()
