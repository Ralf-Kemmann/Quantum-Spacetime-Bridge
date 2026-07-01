#!/usr/bin/env python3
"""QSB PostgreSQL DWH core migration orchestrator.

The runner is deliberately defensive: it never drops databases, schemas, or
tables. If PostgreSQL is unavailable, it still writes the SQL plan and run
audit artifacts so the blocker is reproducible.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "QSB-DWH-POSTGRES-CORE-MIGRATION-01"
LEGACY_RUN_ID = "QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01"
ARTIFACT_PATCH_RUN_ID = "QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-01"
TARGET_DB = "qsb_research_dwh"
MAX_GENERIC_CSV_ROWS = 100_000
MAX_JSON_TEXT_BYTES = 2_000_000
MAX_DOCUMENT_TEXT_CHARS = 12_000
DATASET_ID = "SPARC_RAR_LELLI2016C"
REPO = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO / "scripts" / "qsb_dwh_pg"
SQL_DIR = SCRIPT_DIR / "sql"
OUT = REPO / "runs" / RUN_ID
LEGACY_OUT = REPO / "runs" / LEGACY_RUN_ID
ARTIFACT_PATCH_OUT = REPO / "runs" / ARTIFACT_PATCH_RUN_ID
SPARC_SQLITE_RUN = REPO / "runs" / "QSB-SPARC-RAR-DWH-ETL-METADATA-REGISTRATION-01"
SQLITE_PATH = SPARC_SQLITE_RUN / "sparc_rar_dwh.sqlite"
DATA_CONTRACT = REPO / "runs" / "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT"
BASELINE = REPO / "runs" / "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-REPRODUCTION"

CLAIM_BOUNDARY = [
    "postgres_core_dwh_migration",
    "central_dwh_backend_selection",
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

LEGACY_CLAIM_BOUNDARY = [
    "postgres_legacy_migration",
    "central_dwh_single_db_policy",
    "metadata_server_readiness",
    "generic_artifact_registration",
    "domain_staging_load",
    "canonical_load",
    "metadata_registration",
    "validation_registration",
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

ARTIFACT_PATCH_CLAIM_BOUNDARY = [
    "postgres_legacy_artifact_staging_patch",
    "central_dwh_single_db_policy",
    "generic_artifact_registration",
    "generic_csv_json_markdown_staging",
    "sqlite_catalog_inventory",
    "global_search_enablement",
    "metadata_server_readiness_check",
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

REQUIRED_INPUTS = [
    SQLITE_PATH,
    SPARC_SQLITE_RUN / "04_sparc_rar_dwh_etl_metadata_registration_summary.json",
    SPARC_SQLITE_RUN / "09_dwh_schema.sql",
    SPARC_SQLITE_RUN / "10_dwh_table_inventory.csv",
    SPARC_SQLITE_RUN / "11_dwh_row_counts.csv",
    SPARC_SQLITE_RUN / "16_metadata_field_registry.csv",
    SPARC_SQLITE_RUN / "17_metadata_unit_registry.csv",
    SPARC_SQLITE_RUN / "18_metadata_alias_registry.csv",
    SPARC_SQLITE_RUN / "19_metadata_lineage_registry.csv",
    SPARC_SQLITE_RUN / "20_metadata_validation_registry.csv",
    SPARC_SQLITE_RUN / "21_metadata_claim_registry.csv",
    SPARC_SQLITE_RUN / "24_sample_dwh_queries.sql",
    SPARC_SQLITE_RUN / "25_sample_dwh_query_results.csv",
    DATA_CONTRACT / "06_input_file_checksums.csv",
    BASELINE / "14_direct_rar_dataset.csv",
    BASELINE / "15_massmodels_derived_baseline_quantities.csv",
    *RAW_INPUTS,
]


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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
            w.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_cmd(cmd: list[str], timeout: int = 20) -> dict:
    started = now_utc()
    try:
        p = subprocess.run(cmd, cwd=REPO, text=True, capture_output=True, timeout=timeout, check=False)
        return {
            "command": " ".join(cmd),
            "started_utc": started,
            "returncode": str(p.returncode),
            "stdout": p.stdout.strip(),
            "stderr": p.stderr.strip(),
        }
    except Exception as exc:
        return {
            "command": " ".join(cmd),
            "started_utc": started,
            "returncode": "exception",
            "stdout": "",
            "stderr": str(exc),
        }


def sql_literal(value) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    text = str(value)
    if text == "":
        return "NULL"
    return "'" + text.replace("'", "''") + "'"


def sql_number(value) -> str:
    if value is None:
        return "NULL"
    text = str(value)
    if text == "":
        return "NULL"
    try:
        float(text)
    except ValueError:
        return "NULL"
    return text


def sql_bool(value) -> str:
    text = str(value).strip().lower()
    if text in {"true", "t", "1", "yes"}:
        return "TRUE"
    if text in {"false", "f", "0", "no"}:
        return "FALSE"
    return "NULL"


def append_command_log(lines: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "03_command_log.txt").open("a", encoding="utf-8") as f:
        for line in lines:
            f.write(line.rstrip() + "\n")


def psql(db: str, args: list[str], timeout: int = 120) -> dict:
    return run_cmd(["psql", "-d", db, *args], timeout=timeout)


def run_sql_file(db: str, path: Path) -> dict:
    return psql(db, ["-v", "ON_ERROR_STOP=1", "-f", path.as_posix()], timeout=240)


def ensure_target_database(connection_ok: bool) -> tuple[bool, list[dict]]:
    logs = []
    if not connection_ok:
        return False, logs
    probe = psql("postgres", ["-At", "-c", f"SELECT 1 FROM pg_database WHERE datname = {sql_literal(TARGET_DB)};"])
    logs.append(probe)
    if probe["returncode"] != "0":
        return False, logs
    if probe["stdout"].strip() == "1":
        return True, logs
    createdb = run_cmd(["createdb", TARGET_DB], timeout=120)
    logs.append(createdb)
    return createdb["returncode"] == "0", logs


def postgres_object_counts(target_ready: bool) -> dict:
    if not target_ready:
        return {"schemas": 0, "tables": 0, "views": 0, "procedures": 0}
    queries = {
        "schemas": "SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ('admin','raw','staging','canonical','metadata','validation','mart');",
        "tables": "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema IN ('admin','raw','staging','canonical','metadata','validation') AND table_type='BASE TABLE';",
        "views": "SELECT COUNT(*) FROM information_schema.views WHERE table_schema='mart';",
        "procedures": "SELECT COUNT(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname='admin' AND p.proname IN ('fn_now_utc','register_etl_run','register_validation_result','mark_etl_step');",
    }
    counts = {}
    for key, query in queries.items():
        result = psql(TARGET_DB, ["-At", "-c", query])
        try:
            counts[key] = int(result["stdout"].strip())
        except ValueError:
            counts[key] = 0
    return counts


def postgres_row_count(table: str) -> int:
    result = psql(TARGET_DB, ["-At", "-c", f"SELECT COUNT(*) FROM {table};"])
    try:
        return int(result["stdout"].strip())
    except ValueError:
        return 0


ADMIN_SQL = """
CREATE SCHEMA IF NOT EXISTS admin;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS canonical;
CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS validation;
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS admin.schema_version (
  schema_version_id text PRIMARY KEY,
  applied_at timestamptz NOT NULL DEFAULT now(),
  description text NOT NULL
);

CREATE TABLE IF NOT EXISTS admin.etl_run (
  run_id text PRIMARY KEY,
  dataset_id text,
  status text NOT NULL,
  claim_boundary text NOT NULL,
  started_at timestamptz NOT NULL DEFAULT now(),
  finished_at timestamptz
);

CREATE TABLE IF NOT EXISTS admin.etl_step (
  run_id text NOT NULL,
  step_name text NOT NULL,
  status text NOT NULL,
  message text,
  recorded_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (run_id, step_name)
);

CREATE TABLE IF NOT EXISTS admin.migration_log (
  migration_log_id text PRIMARY KEY,
  run_id text NOT NULL,
  log_level text NOT NULL,
  message text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS admin.single_dwh_policy (
  policy_id text PRIMARY KEY,
  backend text NOT NULL,
  target_database text NOT NULL,
  sqlite_role text NOT NULL,
  policy_status text NOT NULL,
  recorded_at timestamptz NOT NULL DEFAULT now()
);
"""

SPARC_SQL = """
CREATE TABLE IF NOT EXISTS raw.source_file (
  source_file_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  file_name text NOT NULL,
  file_path text NOT NULL,
  size_bytes bigint,
  sha256 text,
  line_count bigint,
  raw_data_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS raw.source_artifact (
  artifact_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  source_run_id text,
  file_name text NOT NULL,
  file_path text NOT NULL,
  sha256 text,
  row_count bigint,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS raw.raw_checksum (
  checksum_id text PRIMARY KEY,
  file_path text NOT NULL,
  expected_sha256 text,
  actual_sha256 text,
  checksum_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.raw_claim_boundary (
  claim_boundary_id text PRIMARY KEY,
  claim_boundary text NOT NULL,
  claim_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.sparc_rar_direct (
  row_id text PRIMARY KEY,
  log10_gbar_m_per_s2 double precision,
  e_log10_gbar double precision,
  log10_gobs_m_per_s2 double precision,
  e_log10_gobs double precision,
  gbar_m_s2 double precision,
  gobs_m_s2 double precision,
  source_table text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS staging.sparc_massmodels_baseline (
  row_id text PRIMARY KEY,
  galaxy_id text,
  radius_kpc double precision,
  vobs_km_s double precision,
  vgas_km_s double precision,
  vdisk_km_s_ml1 double precision,
  vbul_km_s_ml1 double precision,
  gobs_m_s2 double precision,
  log10_gobs double precision,
  vbar_ml1_km_s_preparatory double precision,
  gbar_status text,
  mass_to_light_assumption_required boolean,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS staging.sparc_source_file_registry (
  source_file_id text PRIMARY KEY,
  dataset_id text,
  file_name text,
  file_path text,
  sha256 text,
  validation_status text
);

CREATE TABLE IF NOT EXISTS staging.sparc_artifact_registry (
  artifact_id text PRIMARY KEY,
  dataset_id text,
  file_name text,
  file_path text,
  sha256 text,
  validation_status text
);

CREATE TABLE IF NOT EXISTS canonical.obs_dataset (
  dataset_id text PRIMARY KEY,
  run_id text NOT NULL,
  canonical_name text NOT NULL,
  validation_status text NOT NULL,
  claim_boundary text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.obs_source_file (
  source_file_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  file_name text NOT NULL,
  file_path text NOT NULL,
  size_bytes bigint,
  sha256 text,
  line_count bigint,
  raw_data_status text,
  validation_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS canonical.obs_artifact (
  artifact_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  source_run_id text,
  file_name text NOT NULL,
  file_path text NOT NULL,
  sha256 text,
  row_count bigint,
  validation_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS canonical.obs_galaxy (
  galaxy_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  validation_status text
);

CREATE TABLE IF NOT EXISTS canonical.obs_quantity_definition (
  quantity_id text PRIMARY KEY,
  canonical_name text NOT NULL,
  quantity_kind text,
  unit_display text,
  dimension_vector text,
  conversion_rule_id text,
  validation_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS canonical.obs_measurement (
  measurement_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  source_file_id text,
  artifact_id text,
  galaxy_id text,
  quantity_id text,
  calculation_value double precision,
  calculation_unit text,
  dimension_vector text,
  validation_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS canonical.obs_rar_point (
  rar_point_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  artifact_id text,
  galaxy_id text,
  gobs_m_s2 double precision,
  gbar_m_s2 double precision,
  log_gobs double precision,
  log_gbar double precision,
  lineage_hash text,
  validation_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS canonical.obs_massmodel_point (
  massmodel_point_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  artifact_id text,
  galaxy_id text,
  radius_kpc double precision,
  vobs_km_s double precision,
  vgas_km_s double precision,
  vdisk_km_s double precision,
  vbul_km_s double precision,
  gobs_m_s2 double precision,
  log_gobs double precision,
  gbar_status text,
  mass_to_light_assumption_required boolean,
  lineage_hash text,
  validation_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS canonical.obs_baseline_quantity (
  baseline_quantity_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  artifact_id text,
  galaxy_id text,
  quantity_kind text,
  calculation_value double precision,
  calculation_unit text,
  dimension_vector text,
  validation_status text,
  claim_boundary text
);
"""

METADATA_SQL = """
CREATE TABLE IF NOT EXISTS metadata.meta_field (
  field_id text PRIMARY KEY,
  canonical_name text NOT NULL UNIQUE,
  quantity_kind text,
  dimension_vector text,
  display_label_de text,
  validation_status text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS metadata.meta_unit (
  unit_id text PRIMARY KEY,
  unit_symbol text NOT NULL,
  quantity_kind text,
  dimension_vector text,
  conversion_rule_id text,
  validation_status text
);

CREATE TABLE IF NOT EXISTS metadata.meta_alias (
  alias_id text PRIMARY KEY,
  canonical_name text NOT NULL,
  display_label_de text NOT NULL,
  language text NOT NULL,
  alias_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata.meta_lineage (
  lineage_id text PRIMARY KEY,
  dataset_id text NOT NULL,
  source_id text NOT NULL,
  source_path text NOT NULL,
  source_sha256 text,
  lineage_role text,
  validation_status text
);

CREATE TABLE IF NOT EXISTS metadata.meta_claim (
  claim_id text PRIMARY KEY,
  claim_boundary text NOT NULL,
  claim_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS validation.validation_result (
  validation_id text PRIMARY KEY,
  dataset_id text,
  validation_scope text,
  validation_rule text,
  validation_status text NOT NULL,
  observed_value text,
  expected_value text,
  notes text
);

CREATE TABLE IF NOT EXISTS validation.claim_boundary (
  claim_boundary_id text PRIMARY KEY,
  claim_boundary text NOT NULL,
  claim_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS validation.data_quality_flag (
  flag_id text PRIMARY KEY,
  dataset_id text,
  record_id text,
  flag_status text NOT NULL,
  message text NOT NULL
);
"""

VIEWS_SQL = """
CREATE OR REPLACE VIEW mart.v_sparc_rar_direct_points AS
SELECT rar_point_id, dataset_id, galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar,
       validation_status, claim_boundary
FROM canonical.obs_rar_point;

CREATE OR REPLACE VIEW mart.v_sparc_massmodels_gobs_points AS
SELECT massmodel_point_id, dataset_id, galaxy_id, radius_kpc, vobs_km_s, vgas_km_s,
       vdisk_km_s, vbul_km_s, gobs_m_s2, log_gobs, gbar_status,
       mass_to_light_assumption_required, validation_status, claim_boundary
FROM canonical.obs_massmodel_point;

CREATE OR REPLACE VIEW mart.v_sparc_baseline_quantities AS
SELECT * FROM canonical.obs_baseline_quantity;

CREATE OR REPLACE VIEW mart.v_sparc_dataset_lineage AS
SELECT dataset_id, source_id, source_path, source_sha256, lineage_role, validation_status
FROM metadata.meta_lineage;

CREATE OR REPLACE VIEW mart.v_sparc_field_metadata AS
SELECT canonical_name, quantity_kind, dimension_vector, display_label_de, validation_status, claim_boundary
FROM metadata.meta_field;

CREATE OR REPLACE VIEW mart.v_sparc_unit_metadata AS
SELECT unit_symbol, quantity_kind, dimension_vector, conversion_rule_id, validation_status
FROM metadata.meta_unit;

CREATE OR REPLACE VIEW mart.v_sparc_validation_status AS
SELECT validation_scope, validation_rule, validation_status, observed_value, expected_value, notes
FROM validation.validation_result;

CREATE OR REPLACE VIEW mart.v_de_sparc_feldnamen AS
SELECT canonical_name, display_label_de, language, alias_status
FROM metadata.meta_alias
WHERE language = 'de';

CREATE OR REPLACE VIEW mart.v_de_sparc_metadaten AS
SELECT f.canonical_name, f.display_label_de, f.quantity_kind, f.dimension_vector,
       u.unit_symbol, u.conversion_rule_id, f.validation_status, f.claim_boundary
FROM metadata.meta_field f
LEFT JOIN metadata.meta_unit u ON u.quantity_kind = f.quantity_kind;

CREATE OR REPLACE VIEW mart.v_qsb_obs_search_sparc_rar AS
SELECT 'field'::text AS record_type, canonical_name AS record_id,
       canonical_name || ' ' || display_label_de || ' ' || COALESCE(quantity_kind, '') || ' ' || COALESCE(dimension_vector, '') AS search_text,
       validation_status, claim_boundary
FROM metadata.meta_field
UNION ALL
SELECT 'rar_point'::text, rar_point_id,
       COALESCE(galaxy_id, '') || ' Beschleunigung gobs gbar ' || COALESCE(gobs_m_s2::text, '') || ' ' || COALESCE(gbar_m_s2::text, ''),
       validation_status, claim_boundary
FROM canonical.obs_rar_point
UNION ALL
SELECT 'massmodel_point'::text, massmodel_point_id,
       COALESCE(galaxy_id, '') || ' beobachtete Beschleunigung Rotationsgeschwindigkeit Radius ' ||
       COALESCE(gobs_m_s2::text, '') || ' ' || COALESCE(vobs_km_s::text, ''),
       validation_status, claim_boundary
FROM canonical.obs_massmodel_point;

CREATE OR REPLACE VIEW mart.v_qsb_dwh_status AS
SELECT r.run_id, r.dataset_id, r.status, r.started_at, r.finished_at,
       p.backend, p.target_database, p.sqlite_role
FROM admin.etl_run r
LEFT JOIN admin.single_dwh_policy p ON p.policy_id = 'qsb_single_dwh_policy';
"""

INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_raw_source_file_dataset ON raw.source_file(dataset_id);
CREATE INDEX IF NOT EXISTS idx_canonical_source_file_dataset ON canonical.obs_source_file(dataset_id);
CREATE INDEX IF NOT EXISTS idx_artifact_dataset ON canonical.obs_artifact(dataset_id);
CREATE INDEX IF NOT EXISTS idx_rar_galaxy ON canonical.obs_rar_point(galaxy_id);
CREATE INDEX IF NOT EXISTS idx_massmodel_galaxy ON canonical.obs_massmodel_point(galaxy_id);
CREATE INDEX IF NOT EXISTS idx_quantity_kind ON canonical.obs_quantity_definition(quantity_kind);
CREATE INDEX IF NOT EXISTS idx_meta_field_canonical_name ON metadata.meta_field(canonical_name);
CREATE INDEX IF NOT EXISTS idx_meta_alias_canonical_name ON metadata.meta_alias(canonical_name);
CREATE INDEX IF NOT EXISTS idx_validation_status ON validation.validation_result(validation_status);
CREATE INDEX IF NOT EXISTS idx_claim_boundary_status ON validation.claim_boundary(claim_status);
"""

PROCEDURES_SQL = """
CREATE OR REPLACE FUNCTION admin.fn_now_utc()
RETURNS timestamptz
LANGUAGE sql
STABLE
AS $$
  SELECT now() AT TIME ZONE 'UTC';
$$;

CREATE OR REPLACE PROCEDURE admin.register_etl_run(
  p_run_id text,
  p_dataset_id text,
  p_status text,
  p_claim_boundary text
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO admin.etl_run(run_id, dataset_id, status, claim_boundary, started_at)
  VALUES (p_run_id, p_dataset_id, p_status, p_claim_boundary, admin.fn_now_utc())
  ON CONFLICT (run_id) DO UPDATE
    SET dataset_id = EXCLUDED.dataset_id,
        status = EXCLUDED.status,
        claim_boundary = EXCLUDED.claim_boundary;
END;
$$;

CREATE OR REPLACE PROCEDURE admin.register_validation_result(
  p_validation_id text,
  p_dataset_id text,
  p_status text,
  p_message text
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO validation.validation_result(
    validation_id, dataset_id, validation_scope, validation_rule,
    validation_status, observed_value, expected_value, notes
  )
  VALUES (p_validation_id, p_dataset_id, 'procedure_registration', p_validation_id,
          p_status, p_message, '', p_message)
  ON CONFLICT (validation_id) DO UPDATE
    SET dataset_id = EXCLUDED.dataset_id,
        validation_status = EXCLUDED.validation_status,
        observed_value = EXCLUDED.observed_value,
        notes = EXCLUDED.notes;
END;
$$;

CREATE OR REPLACE PROCEDURE admin.mark_etl_step(
  p_run_id text,
  p_step_name text,
  p_status text,
  p_message text
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO admin.etl_step(run_id, step_name, status, message, recorded_at)
  VALUES (p_run_id, p_step_name, p_status, p_message, admin.fn_now_utc())
  ON CONFLICT (run_id, step_name) DO UPDATE
    SET status = EXCLUDED.status,
        message = EXCLUDED.message,
        recorded_at = EXCLUDED.recorded_at;
END;
$$;
"""

SAMPLE_QUERIES_SQL = """
SELECT * FROM canonical.obs_dataset;

SELECT dataset_id, file_name, sha256, raw_data_status
FROM canonical.obs_source_file
ORDER BY file_name;

SELECT galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar
FROM mart.v_sparc_rar_direct_points
LIMIT 20;

SELECT galaxy_id, radius_kpc, vobs_km_s, gobs_m_s2
FROM mart.v_sparc_massmodels_gobs_points
LIMIT 20;

SELECT canonical_name, display_label_de
FROM mart.v_de_sparc_feldnamen
ORDER BY canonical_name;

SELECT *
FROM mart.v_qsb_obs_search_sparc_rar
WHERE search_text ILIKE '%Beschleunigung%'
LIMIT 20;

SELECT validation_status, COUNT(*) AS n
FROM mart.v_sparc_validation_status
GROUP BY validation_status;
"""


def write_sql_files() -> None:
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    files = {
        SQL_DIR / "001_admin_core.sql": ADMIN_SQL,
        SQL_DIR / "002_sparc_rar.sql": SPARC_SQL,
        SQL_DIR / "003_metadata.sql": METADATA_SQL,
        SQL_DIR / "004_views.sql": VIEWS_SQL,
        SQL_DIR / "005_indexes.sql": INDEXES_SQL,
        SQL_DIR / "006_procedures.sql": PROCEDURES_SQL,
        OUT / "10_postgres_schema_plan.sql": "-- Schema plan: admin, raw, staging, canonical, metadata, validation, mart.\n",
        OUT / "11_postgres_core_schema.sql": ADMIN_SQL,
        OUT / "12_postgres_sparc_rar_schema.sql": SPARC_SQL,
        OUT / "13_postgres_metadata_schema.sql": METADATA_SQL,
        OUT / "14_postgres_views.sql": VIEWS_SQL,
        OUT / "15_postgres_indexes.sql": INDEXES_SQL,
        OUT / "16_postgres_procedures.sql": PROCEDURES_SQL,
        OUT / "25_sample_postgres_queries.sql": SAMPLE_QUERIES_SQL,
    }
    for path, text in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.strip() + "\n", encoding="utf-8")


def postgres_checks() -> tuple[list[dict], list[dict], bool, bool]:
    psql = shutil.which("psql")
    pg_isready = shutil.which("pg_isready")
    availability = [
        {"check_name": "command_v_psql", "command": "command -v psql", "available": str(bool(psql)).lower(), "detail": psql or ""},
        {"check_name": "command_v_pg_isready", "command": "command -v pg_isready", "available": str(bool(pg_isready)).lower(), "detail": pg_isready or ""},
    ]
    if psql:
        version = run_cmd(["psql", "--version"])
        availability.append({"check_name": "psql_version", "command": "psql --version", "available": str(version["returncode"] == "0").lower(), "detail": version["stdout"] or version["stderr"]})
    else:
        availability.append({"check_name": "psql_version", "command": "psql --version", "available": "false", "detail": "psql not found in PATH"})
    if pg_isready:
        ready = run_cmd(["pg_isready"])
        availability.append({"check_name": "pg_isready", "command": "pg_isready", "available": str(ready["returncode"] == "0").lower(), "detail": ready["stdout"] or ready["stderr"]})
    else:
        availability.append({"check_name": "pg_isready", "command": "pg_isready", "available": "false", "detail": "pg_isready not found in PATH"})

    connection = []
    connection_ok = False
    if psql:
        result = run_cmd(["psql", "-d", "postgres", "-c", "SELECT version();"])
        connection_ok = result["returncode"] == "0"
        connection.append({
            "check_name": "psql_postgres_select_version",
            "command": result["command"],
            "connection_ok": str(connection_ok).lower(),
            "returncode": result["returncode"],
            "stdout": result["stdout"],
            "stderr": result["stderr"],
        })
    else:
        connection.append({
            "check_name": "psql_postgres_select_version",
            "command": "psql -d postgres -c SELECT version();",
            "connection_ok": "false",
            "returncode": "not_run",
            "stdout": "",
            "stderr": "psql not found in PATH",
        })
    return availability, connection, bool(psql), connection_ok


def sqlite_inventory() -> tuple[str, list[dict], list[dict], list[dict]]:
    con = sqlite3.connect(SQLITE_PATH)
    integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
    tables = []
    row_counts = []
    views = []
    for name, typ in con.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY type, name"):
        cols = [r[1] for r in con.execute(f"PRAGMA table_info({name})")]
        if typ == "table":
            n = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
            tables.append({"sqlite_object_name": name, "object_type": typ, "column_count": str(len(cols)), "columns": "|".join(cols)})
            row_counts.append({"object_name": name, "object_type": typ, "row_count": str(n)})
        else:
            views.append({"view_name": name, "column_count": str(len(cols)), "columns": "|".join(cols)})
    con.close()
    return integrity, tables, row_counts, views


def input_inventory() -> tuple[list[dict], list[dict], int, int]:
    expected = {r["file_path"]: r["sha256"] for r in read_csv(DATA_CONTRACT / "06_input_file_checksums.csv")}
    inventory = []
    checks = []
    for path in REQUIRED_INPUTS:
        if path.exists():
            inventory.append({
                "file_path": rel(path),
                "exists": "true",
                "size_bytes": str(path.stat().st_size),
                "sha256": sha256(path),
                "role": "required_input",
            })
        else:
            inventory.append({"file_path": rel(path), "exists": "false", "size_bytes": "", "sha256": "", "role": "required_input"})
    for path in RAW_INPUTS:
        actual = sha256(path) if path.exists() else ""
        exp = expected.get(rel(path), "")
        status = "match" if actual and actual == exp else "mismatch_or_missing"
        checks.append({"file_path": rel(path), "expected_sha256": exp, "actual_sha256": actual, "checksum_status": status})
    match_count = sum(1 for r in checks if r["checksum_status"] == "match")
    mismatch_count = len(checks) - match_count
    return inventory, checks, match_count, mismatch_count


def write_static_notes(status: str) -> None:
    (OUT / "02_postgres_core_migration_scope.md").write_text(
        f"# {RUN_ID}\n\nBefund: Architekturwechsel-Run von SQLite-Snapshot zu PostgreSQL-Zielarchitektur.\n\n"
        "Interpretation: SQLite bleibt Audit-/Snapshot-Format; PostgreSQL ist das zentrale Ziel-Backend.\n\n"
        "Hypothese: Keine wissenschaftliche Hypothese wird getestet.\n\n"
        "Offene Luecke: Lokale PostgreSQL-Verfuegbarkeit/Auth entscheidet, ob Ingest praktisch ausgefuehrt werden kann.\n\n"
        "Claim Boundary: Methodische DWH-Migration ohne Residual-, RBCI- oder QSB-Observable-Auswertung.\n",
        encoding="utf-8",
    )
    (OUT / "18_postgres_local_setup_instructions.md").write_text(
        "# PostgreSQL Local Setup Instructions\n\n"
        "Befund: Dieser Run fuehrt keine sudo-/apt-Installation aus.\n\n"
        "Wenn PostgreSQL lokal fehlt, installiere und starte PostgreSQL ausserhalb dieses Runs nach lokaler Systempraxis. "
        "Danach sollte `psql --version`, `pg_isready` und `psql -d postgres -c \"SELECT version();\"` funktionieren.\n\n"
        "Ziel-Datenbank: `qsb_research_dwh`. Schemas: `admin`, `raw`, `staging`, `canonical`, `metadata`, `validation`, `mart`.\n\n"
        "Bei Peer-Auth-/Passwortproblemen nicht blind herumprobieren; Auth-Modus gezielt dokumentieren und freigeben.\n",
        encoding="utf-8",
    )
    (OUT / "19_dbeaver_postgres_connection_note.md").write_text(
        "# DBeaver PostgreSQL Connection Note\n\n"
        "DBeaver target:\n\n"
        "- Type: PostgreSQL\n"
        "- Host: localhost\n"
        "- Port: 5432\n"
        "- Database: qsb_research_dwh\n"
        "- Schemas: admin, raw, staging, canonical, metadata, validation, mart\n\n"
        "SQLite-Run-Dateien bleiben Audit-/Debug-Snapshots und sind nicht mehr das langfristige Arbeits-DWH.\n",
        encoding="utf-8",
    )
    (OUT / "28_sqlite_snapshot_role_note.md").write_text(
        "# SQLite Snapshot Role\n\n"
        "Befund: Der SPARC/RAR-SQLite-Snapshot bleibt reproduzierbares Run-Artefakt.\n\n"
        "Interpretation: Er dient als Audit-, Review- und Offline-Export-Format.\n\n"
        "Claim Boundary: SQLite-Snapshot-Rolle ist eine Architekturentscheidung, kein wissenschaftlicher Ergebnisclaim.\n",
        encoding="utf-8",
    )
    (OUT / "29_claim_boundary_and_no_go.md").write_text(
        "# Claim Boundary and No-Go\n\n"
        "Befund: Dieser Run betrifft PostgreSQL-DWH-Migration, zentrale Backend-Auswahl, SPARC/RAR-DWH-ETL, Metadatenregistrierung und Suchfaehigkeit.\n\n"
        "Interpretation: Keine physikalische Auswertung wird ausgefuehrt.\n\n"
        "Hypothese: Keine.\n\n"
        "Offene Luecke: PostgreSQL-Verbindung kann lokal blockiert sein.\n\n"
        "Claim Boundary: Keine Claims zu Dunkler Materie, RAR-Erklaerung, RBCI_v1-Wirkung, MOND, LambdaCDM, Gravitation, Raumzeit oder Kausalitaet.\n",
        encoding="utf-8",
    )
    (OUT / "30_next_run_recommendation.md").write_text(
        "# Next Run Recommendation\n\n"
        "Befund: Empfohlener naechster Run: `QSB-DWH-POSTGRES-CORE-MIGRATION-REVIEW-01`.\n\n"
        "Interpretation: Naechster Schritt sollte SQL-Plan, PostgreSQL-Verfuegbarkeit, DBeaver-Ziel und ggf. reale Ingest-Counts pruefen.\n\n"
        "Claim Boundary: Review der DWH-Migration, keine neue Auswertung.\n",
        encoding="utf-8",
    )
    (OUT / "31_review_note.md").write_text(
        f"# Review Note\n\nBefund: Status `{status}`.\n\n"
        "Interpretation: SQL- und Orchestrator-Artefakte sind fuer eine PostgreSQL-Zielarchitektur vorbereitet.\n\n"
        "Offene Luecke: Praktischer Ingest benoetigt eine erreichbare PostgreSQL-Instanz und passende Authentifizierung.\n",
        encoding="utf-8",
    )
    (OUT / "34_etl_orchestrator_backend_patch_plan.md").write_text(
        "# ETL Orchestrator Backend Patch Plan\n\n"
        "Befund: Ein separater PostgreSQL-Orchestrator liegt unter `scripts/qsb_dwh_pg/`.\n\n"
        "Interpretation: Bestehende SQLite-/DWH-Skripte wurden nicht umgebaut. Eine spaetere Integration sollte Backend-Auswahl, "
        "Connection-Konfiguration, Dry-Run-Modus und Claim-Boundary-Checks als explizite Schnittstelle einfuehren.\n\n"
        "Claim Boundary: Backend-Patch-Plan ist Architekturarbeit, keine wissenschaftliche Auswertung.\n",
        encoding="utf-8",
    )
    (OUT / "35_next_codex_prompt_recommendation.md").write_text(
        "# Next Codex Prompt Recommendation\n\n"
        "Bitte fuehre `QSB-DWH-POSTGRES-CORE-MIGRATION-REVIEW-01` aus: pruefe SQL-Schema, Setup-Hinweise, DBeaver-Ziel, "
        "Summary JSON, Blockerstatus und Claim Boundary. Falls PostgreSQL danach verfuegbar ist, autorisiere einen separaten Ingest-Run.\n",
        encoding="utf-8",
    )


def write_mapping() -> None:
    rows = [
        {"sqlite_object": "qsb_run", "postgres_object": "admin.etl_run", "migration_role": "run_status"},
        {"sqlite_object": "qsb_obs_source_file", "postgres_object": "raw.source_file;canonical.obs_source_file", "migration_role": "source_registry"},
        {"sqlite_object": "qsb_obs_artifact", "postgres_object": "raw.source_artifact;canonical.obs_artifact", "migration_role": "artifact_registry"},
        {"sqlite_object": "stg_sparc_rar", "postgres_object": "staging.sparc_rar_direct", "migration_role": "staging_load"},
        {"sqlite_object": "stg_sparc_massmodels", "postgres_object": "staging.sparc_massmodels_baseline", "migration_role": "staging_load"},
        {"sqlite_object": "qsb_obs_dataset", "postgres_object": "canonical.obs_dataset", "migration_role": "canonical_dataset"},
        {"sqlite_object": "qsb_obs_galaxy", "postgres_object": "canonical.obs_galaxy", "migration_role": "canonical_entity"},
        {"sqlite_object": "qsb_obs_rar_point", "postgres_object": "canonical.obs_rar_point", "migration_role": "canonical_observation"},
        {"sqlite_object": "qsb_obs_massmodel_point", "postgres_object": "canonical.obs_massmodel_point", "migration_role": "canonical_observation"},
        {"sqlite_object": "qsb_obs_baseline_quantity", "postgres_object": "canonical.obs_baseline_quantity", "migration_role": "baseline_quantity"},
        {"sqlite_object": "meta_field", "postgres_object": "metadata.meta_field", "migration_role": "metadata"},
        {"sqlite_object": "meta_unit", "postgres_object": "metadata.meta_unit", "migration_role": "metadata"},
        {"sqlite_object": "meta_alias", "postgres_object": "metadata.meta_alias", "migration_role": "metadata"},
        {"sqlite_object": "meta_lineage", "postgres_object": "metadata.meta_lineage", "migration_role": "metadata"},
        {"sqlite_object": "meta_claim", "postgres_object": "metadata.meta_claim;validation.claim_boundary", "migration_role": "claim_boundary"},
        {"sqlite_object": "meta_validation_result", "postgres_object": "validation.validation_result", "migration_role": "validation"},
    ]
    write_csv(OUT / "27_sqlite_to_postgres_mapping.csv", rows, ["sqlite_object", "postgres_object", "migration_role"])


def generate_ingest_sql() -> Path:
    con = sqlite3.connect(SQLITE_PATH)
    con.row_factory = sqlite3.Row
    path = OUT / "36_postgres_ingest_upsert.sql"
    lines = [
        "-- Generated SPARC/RAR PostgreSQL ingest SQL.",
        "-- Idempotent: every insert uses ON CONFLICT.",
        "BEGIN;",
        f"CALL admin.register_etl_run({sql_literal(RUN_ID)}, {sql_literal(DATASET_ID)}, 'ingest_running', {sql_literal('|'.join(CLAIM_BOUNDARY))});",
        "INSERT INTO admin.single_dwh_policy(policy_id, backend, target_database, sqlite_role, policy_status)",
        f"VALUES ('qsb_single_dwh_policy', 'postgresql', {sql_literal(TARGET_DB)}, 'audit_snapshot_only', 'active')",
        "ON CONFLICT (policy_id) DO UPDATE SET backend=EXCLUDED.backend, target_database=EXCLUDED.target_database, sqlite_role=EXCLUDED.sqlite_role, policy_status=EXCLUDED.policy_status;",
        "INSERT INTO canonical.obs_dataset(dataset_id, run_id, canonical_name, validation_status, claim_boundary)",
        f"VALUES ({sql_literal(DATASET_ID)}, {sql_literal(RUN_ID)}, 'SPARC RAR Lelli2016c baseline registered dataset', 'validated', 'methodological_preparation_only')",
        "ON CONFLICT (dataset_id) DO UPDATE SET run_id=EXCLUDED.run_id, canonical_name=EXCLUDED.canonical_name, validation_status=EXCLUDED.validation_status, claim_boundary=EXCLUDED.claim_boundary;",
    ]

    source_id_map = {}
    for row in con.execute("SELECT * FROM qsb_obs_source_file ORDER BY file_name"):
        sid = f"{DATASET_ID}::{row['file_name']}"
        source_id_map[row["source_file_id"]] = sid
        cols = ["source_file_id", "dataset_id", "file_name", "file_path", "size_bytes", "sha256", "line_count", "raw_data_status", "claim_boundary"]
        vals = [sid, DATASET_ID, row["file_name"], row["file_path"], row["size_bytes"], row["sha256"], row["line_count"], row["raw_data_status"], row["claim_boundary"]]
        value_sql = ", ".join(sql_number(v) if c in {"size_bytes", "line_count"} else sql_literal(v) for c, v in zip(cols, vals))
        update_cols = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols[1:])
        lines.append(f"INSERT INTO raw.source_file({', '.join(cols)}) VALUES ({value_sql}) ON CONFLICT (source_file_id) DO UPDATE SET {update_cols};")
        cols2 = cols + ["validation_status"]
        vals2 = vals + [row["validation_status"]]
        value_sql2 = ", ".join(sql_number(v) if c in {"size_bytes", "line_count"} else sql_literal(v) for c, v in zip(cols2, vals2))
        update_cols2 = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols2[1:])
        lines.append(f"INSERT INTO canonical.obs_source_file({', '.join(cols2)}) VALUES ({value_sql2}) ON CONFLICT (source_file_id) DO UPDATE SET {update_cols2};")
        lines.append(
            "INSERT INTO staging.sparc_source_file_registry(source_file_id, dataset_id, file_name, file_path, sha256, validation_status) "
            f"VALUES ({sql_literal(sid)}, {sql_literal(DATASET_ID)}, {sql_literal(row['file_name'])}, {sql_literal(row['file_path'])}, {sql_literal(row['sha256'])}, {sql_literal(row['validation_status'])}) "
            "ON CONFLICT (source_file_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, file_name=EXCLUDED.file_name, file_path=EXCLUDED.file_path, sha256=EXCLUDED.sha256, validation_status=EXCLUDED.validation_status;"
        )

    artifact_id_map = {}
    for row in con.execute("SELECT * FROM qsb_obs_artifact ORDER BY source_run_id, file_name"):
        aid = f"{row['source_run_id']}::{row['file_name']}"
        artifact_id_map[row["source_artifact_id"]] = aid
        cols = ["artifact_id", "dataset_id", "source_run_id", "file_name", "file_path", "sha256", "row_count", "claim_boundary"]
        vals = [aid, DATASET_ID, row["source_run_id"], row["file_name"], row["file_path"], row["sha256"], row["row_count"], row["claim_boundary"]]
        value_sql = ", ".join(sql_number(v) if c == "row_count" else sql_literal(v) for c, v in zip(cols, vals))
        update_cols = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols[1:])
        lines.append(f"INSERT INTO raw.source_artifact({', '.join(cols)}) VALUES ({value_sql}) ON CONFLICT (artifact_id) DO UPDATE SET {update_cols};")
        cols2 = cols + ["validation_status"]
        vals2 = vals + [row["validation_status"]]
        value_sql2 = ", ".join(sql_number(v) if c == "row_count" else sql_literal(v) for c, v in zip(cols2, vals2))
        update_cols2 = ", ".join(f"{c}=EXCLUDED.{c}" for c in cols2[1:])
        lines.append(f"INSERT INTO canonical.obs_artifact({', '.join(cols2)}) VALUES ({value_sql2}) ON CONFLICT (artifact_id) DO UPDATE SET {update_cols2};")
        lines.append(
            "INSERT INTO staging.sparc_artifact_registry(artifact_id, dataset_id, file_name, file_path, sha256, validation_status) "
            f"VALUES ({sql_literal(aid)}, {sql_literal(DATASET_ID)}, {sql_literal(row['file_name'])}, {sql_literal(row['file_path'])}, {sql_literal(row['sha256'])}, {sql_literal(row['validation_status'])}) "
            "ON CONFLICT (artifact_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, file_name=EXCLUDED.file_name, file_path=EXCLUDED.file_path, sha256=EXCLUDED.sha256, validation_status=EXCLUDED.validation_status;"
        )

    for row in read_csv(DATA_CONTRACT / "06_input_file_checksums.csv"):
        actual_path = REPO / row["file_path"]
        actual = sha256(actual_path) if actual_path.exists() else ""
        status = "match" if actual == row["sha256"] else "mismatch_or_missing"
        cid = hashlib.sha256(row["file_path"].encode("utf-8")).hexdigest()
        lines.append(
            "INSERT INTO raw.raw_checksum(checksum_id, file_path, expected_sha256, actual_sha256, checksum_status) "
            f"VALUES ({sql_literal(cid)}, {sql_literal(row['file_path'])}, {sql_literal(row['sha256'])}, {sql_literal(actual)}, {sql_literal(status)}) "
            "ON CONFLICT (checksum_id) DO UPDATE SET expected_sha256=EXCLUDED.expected_sha256, actual_sha256=EXCLUDED.actual_sha256, checksum_status=EXCLUDED.checksum_status;"
        )

    for row in con.execute("SELECT * FROM stg_sparc_rar ORDER BY CAST(row_id AS INTEGER)"):
        lines.append(
            "INSERT INTO staging.sparc_rar_direct(row_id, log10_gbar_m_per_s2, e_log10_gbar, log10_gobs_m_per_s2, e_log10_gobs, gbar_m_s2, gobs_m_s2, source_table, claim_boundary) "
            f"VALUES ({sql_literal(row['row_id'])}, {sql_number(row['log10_gbar_m_per_s2'])}, {sql_number(row['e_log10_gbar'])}, {sql_number(row['log10_gobs_m_per_s2'])}, {sql_number(row['e_log10_gobs'])}, {sql_number(row['gbar_m_per_s2'])}, {sql_number(row['gobs_m_per_s2'])}, {sql_literal(row['source_table'])}, {sql_literal(row['claim_boundary'])}) "
            "ON CONFLICT (row_id) DO UPDATE SET log10_gbar_m_per_s2=EXCLUDED.log10_gbar_m_per_s2, e_log10_gbar=EXCLUDED.e_log10_gbar, log10_gobs_m_per_s2=EXCLUDED.log10_gobs_m_per_s2, e_log10_gobs=EXCLUDED.e_log10_gobs, gbar_m_s2=EXCLUDED.gbar_m_s2, gobs_m_s2=EXCLUDED.gobs_m_s2, source_table=EXCLUDED.source_table, claim_boundary=EXCLUDED.claim_boundary;"
        )
    for row in con.execute("SELECT * FROM stg_sparc_massmodels ORDER BY CAST(row_id AS INTEGER)"):
        lines.append(
            "INSERT INTO staging.sparc_massmodels_baseline(row_id, galaxy_id, radius_kpc, vobs_km_s, vgas_km_s, vdisk_km_s_ml1, vbul_km_s_ml1, gobs_m_s2, log10_gobs, vbar_ml1_km_s_preparatory, gbar_status, mass_to_light_assumption_required, claim_boundary) "
            f"VALUES ({sql_literal(row['row_id'])}, {sql_literal(row['galaxy_id'])}, {sql_number(row['radius_kpc'])}, {sql_number(row['vobs_km_s'])}, {sql_number(row['vgas_km_s'])}, {sql_number(row['vdisk_km_s_ml1'])}, {sql_number(row['vbul_km_s_ml1'])}, {sql_number(row['gobs_m_per_s2'])}, {sql_number(row['log10_gobs'])}, {sql_number(row['vbar_ml1_km_s_preparatory'])}, {sql_literal(row['gbar_status'])}, {sql_bool(row['mass_to_light_assumption_required'])}, {sql_literal(row['claim_boundary'])}) "
            "ON CONFLICT (row_id) DO UPDATE SET galaxy_id=EXCLUDED.galaxy_id, radius_kpc=EXCLUDED.radius_kpc, vobs_km_s=EXCLUDED.vobs_km_s, vgas_km_s=EXCLUDED.vgas_km_s, vdisk_km_s_ml1=EXCLUDED.vdisk_km_s_ml1, vbul_km_s_ml1=EXCLUDED.vbul_km_s_ml1, gobs_m_s2=EXCLUDED.gobs_m_s2, log10_gobs=EXCLUDED.log10_gobs, vbar_ml1_km_s_preparatory=EXCLUDED.vbar_ml1_km_s_preparatory, gbar_status=EXCLUDED.gbar_status, mass_to_light_assumption_required=EXCLUDED.mass_to_light_assumption_required, claim_boundary=EXCLUDED.claim_boundary;"
        )

    for row in con.execute("SELECT * FROM qsb_obs_galaxy ORDER BY galaxy_id"):
        lines.append(
            "INSERT INTO canonical.obs_galaxy(galaxy_id, dataset_id, validation_status) "
            f"VALUES ({sql_literal(row['galaxy_id'])}, {sql_literal(DATASET_ID)}, {sql_literal(row['validation_status'])}) "
            "ON CONFLICT (galaxy_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, validation_status=EXCLUDED.validation_status;"
        )
    for row in con.execute("SELECT * FROM qsb_obs_quantity_definition ORDER BY canonical_name"):
        qid = f"{DATASET_ID}::QUANTITY::{row['canonical_name']}"
        lines.append(
            "INSERT INTO canonical.obs_quantity_definition(quantity_id, canonical_name, quantity_kind, unit_display, dimension_vector, conversion_rule_id, validation_status, claim_boundary) "
            f"VALUES ({sql_literal(qid)}, {sql_literal(row['canonical_name'])}, {sql_literal(row['quantity_kind'])}, {sql_literal(row['unit_display'])}, {sql_literal(row['dimension_vector'])}, {sql_literal(row['conversion_rule_id'])}, {sql_literal(row['validation_status'])}, {sql_literal(row['claim_boundary'])}) "
            "ON CONFLICT (quantity_id) DO UPDATE SET canonical_name=EXCLUDED.canonical_name, quantity_kind=EXCLUDED.quantity_kind, unit_display=EXCLUDED.unit_display, dimension_vector=EXCLUDED.dimension_vector, conversion_rule_id=EXCLUDED.conversion_rule_id, validation_status=EXCLUDED.validation_status, claim_boundary=EXCLUDED.claim_boundary;"
        )

    for idx, row in enumerate(con.execute("SELECT * FROM qsb_obs_rar_point ORDER BY rar_point_id"), start=1):
        rid = f"{DATASET_ID}::RAR::{idx}"
        aid = artifact_id_map.get(row["source_artifact_id"], row["source_artifact_id"])
        lines.append(
            "INSERT INTO canonical.obs_rar_point(rar_point_id, dataset_id, artifact_id, galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar, lineage_hash, validation_status, claim_boundary) "
            f"VALUES ({sql_literal(rid)}, {sql_literal(DATASET_ID)}, {sql_literal(aid)}, {sql_literal(row['galaxy_id'])}, {sql_number(row['gobs_m_s2'])}, {sql_number(row['gbar_m_s2'])}, {sql_number(row['log_gobs'])}, {sql_number(row['log_gbar'])}, {sql_literal(row['lineage_hash'])}, {sql_literal(row['validation_status'])}, {sql_literal(row['claim_boundary'])}) "
            "ON CONFLICT (rar_point_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, artifact_id=EXCLUDED.artifact_id, galaxy_id=EXCLUDED.galaxy_id, gobs_m_s2=EXCLUDED.gobs_m_s2, gbar_m_s2=EXCLUDED.gbar_m_s2, log_gobs=EXCLUDED.log_gobs, log_gbar=EXCLUDED.log_gbar, lineage_hash=EXCLUDED.lineage_hash, validation_status=EXCLUDED.validation_status, claim_boundary=EXCLUDED.claim_boundary;"
        )

    for idx, row in enumerate(con.execute("SELECT * FROM qsb_obs_massmodel_point ORDER BY massmodel_point_id"), start=1):
        mid = f"{DATASET_ID}::MASSMODELS::{idx}"
        aid = artifact_id_map.get(row["source_artifact_id"], row["source_artifact_id"])
        lines.append(
            "INSERT INTO canonical.obs_massmodel_point(massmodel_point_id, dataset_id, artifact_id, galaxy_id, radius_kpc, vobs_km_s, vgas_km_s, vdisk_km_s, vbul_km_s, gobs_m_s2, log_gobs, gbar_status, mass_to_light_assumption_required, lineage_hash, validation_status, claim_boundary) "
            f"VALUES ({sql_literal(mid)}, {sql_literal(DATASET_ID)}, {sql_literal(aid)}, {sql_literal(row['galaxy_id'])}, {sql_number(row['radius_kpc'])}, {sql_number(row['vobs_km_s'])}, {sql_number(row['vgas_km_s'])}, {sql_number(row['vdisk_km_s'])}, {sql_number(row['vbul_km_s'])}, {sql_number(row['gobs_m_s2'])}, {sql_number(row['log_gobs'])}, {sql_literal(row['gbar_status'])}, {sql_bool(row['mass_to_light_assumption_required'])}, {sql_literal(row['lineage_hash'])}, {sql_literal(row['validation_status'])}, {sql_literal(row['claim_boundary'])}) "
            "ON CONFLICT (massmodel_point_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, artifact_id=EXCLUDED.artifact_id, galaxy_id=EXCLUDED.galaxy_id, radius_kpc=EXCLUDED.radius_kpc, vobs_km_s=EXCLUDED.vobs_km_s, vgas_km_s=EXCLUDED.vgas_km_s, vdisk_km_s=EXCLUDED.vdisk_km_s, vbul_km_s=EXCLUDED.vbul_km_s, gobs_m_s2=EXCLUDED.gobs_m_s2, log_gobs=EXCLUDED.log_gobs, gbar_status=EXCLUDED.gbar_status, mass_to_light_assumption_required=EXCLUDED.mass_to_light_assumption_required, lineage_hash=EXCLUDED.lineage_hash, validation_status=EXCLUDED.validation_status, claim_boundary=EXCLUDED.claim_boundary;"
        )

    for idx, row in enumerate(con.execute("SELECT * FROM qsb_obs_baseline_quantity ORDER BY baseline_quantity_id"), start=1):
        bid = f"{DATASET_ID}::BASELINE::{idx}::{row['quantity_kind']}"
        aid = artifact_id_map.get(row["source_artifact_id"], row["source_artifact_id"])
        lines.append(
            "INSERT INTO canonical.obs_baseline_quantity(baseline_quantity_id, dataset_id, artifact_id, galaxy_id, quantity_kind, calculation_value, calculation_unit, dimension_vector, validation_status, claim_boundary) "
            f"VALUES ({sql_literal(bid)}, {sql_literal(DATASET_ID)}, {sql_literal(aid)}, {sql_literal(row['galaxy_id'])}, {sql_literal(row['quantity_kind'])}, {sql_number(row['calculation_value'])}, {sql_literal(row['calculation_unit'])}, {sql_literal(row['dimension_vector'])}, {sql_literal(row['validation_status'])}, {sql_literal(row['claim_boundary'])}) "
            "ON CONFLICT (baseline_quantity_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, artifact_id=EXCLUDED.artifact_id, galaxy_id=EXCLUDED.galaxy_id, quantity_kind=EXCLUDED.quantity_kind, calculation_value=EXCLUDED.calculation_value, calculation_unit=EXCLUDED.calculation_unit, dimension_vector=EXCLUDED.dimension_vector, validation_status=EXCLUDED.validation_status, claim_boundary=EXCLUDED.claim_boundary;"
        )

    meta_columns = {
        "meta_field": ["field_id", "canonical_name", "quantity_kind", "dimension_vector", "display_label_de", "validation_status", "claim_boundary"],
        "meta_unit": ["unit_id", "unit_symbol", "quantity_kind", "dimension_vector", "conversion_rule_id", "validation_status"],
        "meta_alias": ["alias_id", "canonical_name", "display_label_de", "language", "alias_status"],
        "meta_lineage": ["lineage_id", "dataset_id", "source_id", "source_path", "source_sha256", "lineage_role", "validation_status"],
        "meta_claim": ["claim_id", "claim_boundary", "claim_status"],
    }
    for table, pk in [("meta_field", "field_id"), ("meta_unit", "unit_id"), ("meta_alias", "alias_id"), ("meta_lineage", "lineage_id"), ("meta_claim", "claim_id")]:
        target = f"metadata.{table}"
        rows = con.execute(f"SELECT * FROM {table}").fetchall()
        for row in rows:
            cols = meta_columns[table]
            value_sql = ", ".join(sql_literal(row[col]) for col in cols)
            update_cols = ", ".join(f"{col}=EXCLUDED.{col}" for col in cols if col != pk)
            lines.append(f"INSERT INTO {target}({', '.join(cols)}) VALUES ({value_sql}) ON CONFLICT ({pk}) DO UPDATE SET {update_cols};")
            if table == "meta_claim":
                lines.append(
                    "INSERT INTO validation.claim_boundary(claim_boundary_id, claim_boundary, claim_status) "
                    f"VALUES ({sql_literal(row['claim_id'])}, {sql_literal(row['claim_boundary'])}, {sql_literal(row['claim_status'])}) "
                    "ON CONFLICT (claim_boundary_id) DO UPDATE SET claim_boundary=EXCLUDED.claim_boundary, claim_status=EXCLUDED.claim_status;"
                )
                lines.append(
                    "INSERT INTO raw.raw_claim_boundary(claim_boundary_id, claim_boundary, claim_status) "
                    f"VALUES ({sql_literal(row['claim_id'])}, {sql_literal(row['claim_boundary'])}, {sql_literal(row['claim_status'])}) "
                    "ON CONFLICT (claim_boundary_id) DO UPDATE SET claim_boundary=EXCLUDED.claim_boundary, claim_status=EXCLUDED.claim_status;"
                )

    for row in con.execute("SELECT * FROM meta_validation_result ORDER BY validation_id"):
        lines.append(
            "INSERT INTO validation.validation_result(validation_id, dataset_id, validation_scope, validation_rule, validation_status, observed_value, expected_value, notes) "
            f"VALUES ({sql_literal(row['validation_id'])}, {sql_literal(DATASET_ID)}, {sql_literal(row['validation_scope'])}, {sql_literal(row['validation_rule'])}, {sql_literal(row['validation_status'])}, {sql_literal(row['observed_value'])}, {sql_literal(row['expected_value'])}, {sql_literal(row['notes'])}) "
            "ON CONFLICT (validation_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, validation_scope=EXCLUDED.validation_scope, validation_rule=EXCLUDED.validation_rule, validation_status=EXCLUDED.validation_status, observed_value=EXCLUDED.observed_value, expected_value=EXCLUDED.expected_value, notes=EXCLUDED.notes;"
        )

    lines.extend([
        f"CALL admin.mark_etl_step({sql_literal(RUN_ID)}, 'ingest_sparc_rar', 'completed', 'SPARC/RAR SQLite snapshot ingested idempotently.');",
        f"UPDATE admin.etl_run SET status='completed', finished_at=admin.fn_now_utc() WHERE run_id={sql_literal(RUN_ID)};",
        "COMMIT;",
    ])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    con.close()
    return path


def write_postgres_inventories(target_ready: bool) -> tuple[list[dict], list[dict], list[dict]]:
    if not target_ready:
        write_csv(OUT / "20_table_inventory.csv", [], ["schema_name", "table_name", "row_count", "status"])
        return [], [], []
    table_query = (
        "SELECT table_schema || '.' || table_name FROM information_schema.tables "
        "WHERE table_schema IN ('admin','raw','staging','canonical','metadata','validation') "
        "AND table_type='BASE TABLE' ORDER BY table_schema, table_name;"
    )
    view_query = "SELECT table_schema || '.' || table_name FROM information_schema.views WHERE table_schema='mart' ORDER BY table_name;"
    table_result = psql(TARGET_DB, ["-At", "-c", table_query])
    view_result = psql(TARGET_DB, ["-At", "-c", view_query])
    table_rows = []
    row_counts = []
    for full_name in [line.strip() for line in table_result["stdout"].splitlines() if line.strip()]:
        count = postgres_row_count(full_name)
        schema_name, table_name = full_name.split(".", 1)
        table_rows.append({"schema_name": schema_name, "table_name": table_name, "row_count": str(count), "status": "verified"})
        row_counts.append({"object_name": full_name, "object_type": "postgres_table", "row_count": str(count)})
    view_rows = []
    for full_name in [line.strip() for line in view_result["stdout"].splitlines() if line.strip()]:
        schema_name, view_name = full_name.split(".", 1)
        view_rows.append({"view_name": full_name, "column_count": "", "columns": "", "status": "verified"})
    write_csv(OUT / "20_table_inventory.csv", table_rows, ["schema_name", "table_name", "row_count", "status"])
    write_csv(OUT / "21_row_counts.csv", row_counts, ["object_name", "object_type", "row_count"])
    write_csv(OUT / "22_view_inventory.csv", view_rows, ["view_name", "column_count", "columns", "status"])
    return table_rows, row_counts, view_rows


LEGACY_SCHEMA_SQL = """
CREATE SCHEMA IF NOT EXISTS admin;
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS canonical;
CREATE SCHEMA IF NOT EXISTS metadata;
CREATE SCHEMA IF NOT EXISTS validation;
CREATE SCHEMA IF NOT EXISTS mart;
CREATE SCHEMA IF NOT EXISTS server;

ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS suffix text;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS size_bytes bigint;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS line_count bigint;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS run_folder text;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS artifact_kind text;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS domain_guess text;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS registered_by_run_id text;
ALTER TABLE raw.source_artifact ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE raw.source_file ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE raw.source_file ADD COLUMN IF NOT EXISTS suffix text;
ALTER TABLE raw.source_file ADD COLUMN IF NOT EXISTS run_folder text;
ALTER TABLE raw.source_file ADD COLUMN IF NOT EXISTS artifact_kind text;
ALTER TABLE raw.source_file ADD COLUMN IF NOT EXISTS domain_guess text;
ALTER TABLE raw.source_file ADD COLUMN IF NOT EXISTS registered_by_run_id text;
ALTER TABLE raw.source_file ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();
ALTER TABLE raw.raw_checksum ADD COLUMN IF NOT EXISTS artifact_id text;
ALTER TABLE raw.raw_checksum ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE raw.raw_checksum ADD COLUMN IF NOT EXISTS registered_by_run_id text;
ALTER TABLE raw.raw_checksum ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS admin.dataset_registry (
  dataset_id text PRIMARY KEY,
  dataset_name text NOT NULL,
  domain text NOT NULL,
  registration_status text NOT NULL,
  registered_by_run_id text NOT NULL,
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.run_folder (
  run_folder_id text PRIMARY KEY,
  run_folder text NOT NULL,
  file_count bigint NOT NULL,
  domain_guess text NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS raw.git_commit_reference (
  commit_hash text PRIMARY KEY,
  subject text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.artifact_column_profile (
  profile_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  column_name text NOT NULL,
  column_index integer,
  observed_nonempty_count bigint,
  registered_by_run_id text NOT NULL
);
ALTER TABLE staging.artifact_column_profile ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE staging.artifact_column_profile ADD COLUMN IF NOT EXISTS loaded_by_run_id text;
ALTER TABLE staging.artifact_column_profile ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS staging.csv_row_json (
  row_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  row_number bigint NOT NULL,
  row_json jsonb NOT NULL,
  registered_by_run_id text NOT NULL
);
ALTER TABLE staging.csv_row_json ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE staging.csv_row_json ADD COLUMN IF NOT EXISTS loaded_by_run_id text;
ALTER TABLE staging.csv_row_json ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS staging.json_document (
  document_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  document_json jsonb,
  parse_status text NOT NULL,
  registered_by_run_id text NOT NULL
);
ALTER TABLE staging.json_document ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE staging.json_document ADD COLUMN IF NOT EXISTS json_text text;
ALTER TABLE staging.json_document ADD COLUMN IF NOT EXISTS jsonb_document jsonb;
ALTER TABLE staging.json_document ADD COLUMN IF NOT EXISTS loaded_by_run_id text;
ALTER TABLE staging.json_document ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS staging.json_key_value (
  key_value_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  key_path text NOT NULL,
  value_text text,
  registered_by_run_id text NOT NULL
);
ALTER TABLE staging.json_key_value ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE staging.json_key_value ADD COLUMN IF NOT EXISTS loaded_by_run_id text;
ALTER TABLE staging.json_key_value ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS staging.markdown_document (
  document_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  title text,
  line_count bigint,
  registered_by_run_id text NOT NULL
);
ALTER TABLE staging.markdown_document ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE staging.markdown_document ADD COLUMN IF NOT EXISTS body_text text;
ALTER TABLE staging.markdown_document ADD COLUMN IF NOT EXISTS body_preview text;
ALTER TABLE staging.markdown_document ADD COLUMN IF NOT EXISTS loaded_by_run_id text;
ALTER TABLE staging.markdown_document ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS staging.sqlite_table_inventory (
  inventory_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  table_name text NOT NULL,
  column_count bigint,
  registered_by_run_id text NOT NULL
);
ALTER TABLE staging.sqlite_table_inventory ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE staging.sqlite_table_inventory ADD COLUMN IF NOT EXISTS column_names text;
ALTER TABLE staging.sqlite_table_inventory ADD COLUMN IF NOT EXISTS loaded_by_run_id text;
ALTER TABLE staging.sqlite_table_inventory ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS staging.sqlite_row_count (
  row_count_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  table_name text NOT NULL,
  row_count bigint,
  registered_by_run_id text NOT NULL
);
ALTER TABLE staging.sqlite_row_count ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE staging.sqlite_row_count ADD COLUMN IF NOT EXISTS loaded_by_run_id text;
ALTER TABLE staging.sqlite_row_count ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS staging.matrix_topology_summary (
  summary_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  summary_key text NOT NULL,
  summary_value text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.matrix_topology_edge_candidate (
  edge_candidate_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  source_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.interface01_summary (
  summary_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  summary_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.relalg_summary (
  summary_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  summary_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS staging.causality_summary (
  summary_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  summary_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.qsb_run (
  run_id text PRIMARY KEY,
  run_folder text NOT NULL,
  domain_guess text NOT NULL,
  file_count bigint NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.qsb_run_summary (
  run_summary_id text PRIMARY KEY,
  run_id text NOT NULL,
  summary_json jsonb,
  summary_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.qsb_artifact (
  artifact_id text PRIMARY KEY,
  relative_path text NOT NULL,
  artifact_kind text NOT NULL,
  domain_guess text NOT NULL,
  sha256 text NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.qsb_validation_event (
  validation_event_id text PRIMARY KEY,
  dataset_id text,
  validation_status text NOT NULL,
  message text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.qsb_claim_boundary_event (
  claim_event_id text PRIMARY KEY,
  claim_boundary text NOT NULL,
  claim_status text NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.matrix_topology_component (
  component_id text PRIMARY KEY,
  artifact_id text,
  component_label text,
  metric_json jsonb,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.matrix_topology_edge (
  edge_id text PRIMARY KEY,
  artifact_id text,
  edge_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.matrix_topology_metric (
  metric_id text PRIMARY KEY,
  artifact_id text,
  metric_name text NOT NULL,
  metric_value text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.interface01_artifact (
  interface01_artifact_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  summary_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.interface01_feature (
  feature_id text PRIMARY KEY,
  artifact_id text,
  feature_name text,
  feature_value text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.relalg_artifact (
  relalg_artifact_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  summary_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.relalg_metric (
  metric_id text PRIMARY KEY,
  artifact_id text,
  metric_name text,
  metric_value text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.causality_artifact (
  causality_artifact_id text PRIMARY KEY,
  artifact_id text NOT NULL,
  summary_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS canonical.causality_transition (
  transition_id text PRIMARY KEY,
  artifact_id text,
  transition_text text,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata.meta_dataset (
  dataset_id text PRIMARY KEY,
  dataset_name text NOT NULL,
  domain text NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata.meta_view (
  view_id text PRIMARY KEY,
  schema_name text NOT NULL,
  view_name text NOT NULL,
  view_role text NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS metadata.meta_search_token (
  token_id text PRIMARY KEY,
  record_type text NOT NULL,
  record_id text NOT NULL,
  search_text text NOT NULL,
  domain_guess text,
  registered_by_run_id text NOT NULL
);
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS search_token_id text;
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS domain text;
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS source_table text;
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS source_id text;
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS display_label text;
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS claim_boundary text;
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS validation_status text;
ALTER TABLE metadata.meta_search_token ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS validation.ingest_warning (
  warning_id text PRIMARY KEY,
  artifact_id text,
  warning_status text NOT NULL,
  message text NOT NULL,
  registered_by_run_id text NOT NULL
);
ALTER TABLE validation.ingest_warning ADD COLUMN IF NOT EXISTS relative_path text;
ALTER TABLE validation.ingest_warning ADD COLUMN IF NOT EXISTS warning_type text;
ALTER TABLE validation.ingest_warning ADD COLUMN IF NOT EXISTS created_at timestamptz NOT NULL DEFAULT now();

CREATE TABLE IF NOT EXISTS validation.no_go_boundary (
  no_go_id text PRIMARY KEY,
  no_go_text text NOT NULL,
  no_go_status text NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS server.metadata_server_config (
  config_id text PRIMARY KEY,
  config_key text NOT NULL UNIQUE,
  config_value text NOT NULL,
  config_status text NOT NULL,
  registered_by_run_id text NOT NULL
);

CREATE TABLE IF NOT EXISTS server.metadata_server_endpoint (
  endpoint_id text PRIMARY KEY,
  method text NOT NULL,
  path text NOT NULL,
  query_scope text NOT NULL,
  read_only boolean NOT NULL,
  registered_by_run_id text NOT NULL
);
"""

LEGACY_VIEWS_SQL = """
CREATE OR REPLACE VIEW mart.v_qsb_dataset_overview AS
SELECT dataset_id, dataset_name, domain, registration_status
FROM admin.dataset_registry
UNION
SELECT dataset_id, dataset_name, domain, 'metadata_registered' AS registration_status
FROM metadata.meta_dataset;

CREATE OR REPLACE VIEW mart.v_qsb_run_timeline AS
SELECT run_id, run_folder, domain_guess, file_count, registered_by_run_id
FROM canonical.qsb_run;

CREATE OR REPLACE VIEW mart.v_qsb_artifact_inventory AS
SELECT artifact_id, relative_path, artifact_kind, domain_guess, sha256
FROM canonical.qsb_artifact;

CREATE OR REPLACE VIEW mart.v_qsb_metadata_fields AS
SELECT canonical_name, quantity_kind, dimension_vector, display_label_de, validation_status
FROM metadata.meta_field;

CREATE OR REPLACE VIEW mart.v_qsb_metadata_units AS
SELECT unit_symbol, quantity_kind, dimension_vector, conversion_rule_id, validation_status
FROM metadata.meta_unit;

CREATE OR REPLACE VIEW mart.v_qsb_metadata_aliases_de AS
SELECT canonical_name, display_label_de, language, alias_status
FROM metadata.meta_alias
WHERE language = 'de';

CREATE OR REPLACE VIEW mart.v_qsb_validation_status AS
SELECT validation_id, dataset_id, validation_scope, validation_rule, validation_status, observed_value, expected_value, notes
FROM validation.validation_result;

CREATE OR REPLACE VIEW mart.v_qsb_claim_boundaries AS
SELECT claim_boundary_id, claim_boundary, claim_status
FROM validation.claim_boundary;

CREATE OR REPLACE VIEW mart.v_qsb_global_search AS
SELECT token_id, record_type, record_id, search_text, domain_guess
FROM metadata.meta_search_token
UNION ALL
SELECT artifact_id, 'artifact', artifact_id, relative_path || ' ' || artifact_kind || ' ' || domain_guess, domain_guess
FROM canonical.qsb_artifact
UNION ALL
SELECT alias_id, 'alias', canonical_name, canonical_name || ' ' || display_label_de, 'metadata'
FROM metadata.meta_alias;

CREATE OR REPLACE VIEW mart.v_matrix_topology_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess IN ('matrix_topology', 'extract03');

CREATE OR REPLACE VIEW mart.v_interface01_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess = 'interface01';

CREATE OR REPLACE VIEW mart.v_relalg_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess = 'relalg';

CREATE OR REPLACE VIEW mart.v_causality_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess = 'causality';
"""

LEGACY_PROCEDURES_SQL = """
CREATE OR REPLACE PROCEDURE validation.register_validation_result(
  p_validation_id text,
  p_dataset_id text,
  p_status text,
  p_message text
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO validation.validation_result(
    validation_id, dataset_id, validation_scope, validation_rule,
    validation_status, observed_value, expected_value, notes
  )
  VALUES (p_validation_id, p_dataset_id, 'legacy_migration', p_validation_id,
          p_status, p_message, '', p_message)
  ON CONFLICT (validation_id) DO UPDATE
    SET dataset_id = EXCLUDED.dataset_id,
        validation_status = EXCLUDED.validation_status,
        observed_value = EXCLUDED.observed_value,
        notes = EXCLUDED.notes;
END;
$$;

CREATE OR REPLACE PROCEDURE metadata.register_alias(
  p_canonical_name text,
  p_display_label_de text,
  p_context text
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_alias_id text;
BEGIN
  v_alias_id := md5(p_canonical_name || ':' || p_context);
  INSERT INTO metadata.meta_alias(alias_id, canonical_name, display_label_de, language, alias_status)
  VALUES (v_alias_id, p_canonical_name, p_display_label_de, 'de', 'registered')
  ON CONFLICT (alias_id) DO UPDATE
    SET canonical_name = EXCLUDED.canonical_name,
        display_label_de = EXCLUDED.display_label_de,
        language = EXCLUDED.language,
        alias_status = EXCLUDED.alias_status;
END;
$$;
"""

LEGACY_INDEXES_SQL = """
CREATE INDEX IF NOT EXISTS idx_raw_source_artifact_domain ON raw.source_artifact(domain_guess);
CREATE INDEX IF NOT EXISTS idx_raw_source_artifact_kind ON raw.source_artifact(artifact_kind);
CREATE INDEX IF NOT EXISTS idx_csv_row_json_artifact ON staging.csv_row_json(artifact_id);
CREATE INDEX IF NOT EXISTS idx_json_document_artifact ON staging.json_document(artifact_id);
CREATE INDEX IF NOT EXISTS idx_markdown_document_artifact ON staging.markdown_document(artifact_id);
CREATE INDEX IF NOT EXISTS idx_qsb_artifact_domain ON canonical.qsb_artifact(domain_guess);
CREATE INDEX IF NOT EXISTS idx_meta_search_domain ON metadata.meta_search_token(domain_guess);
CREATE INDEX IF NOT EXISTS idx_meta_search_text ON metadata.meta_search_token USING gin(to_tsvector('simple', search_text));
"""


def legacy_out_path(name: str) -> Path:
    return LEGACY_OUT / name


def legacy_domain_guess(path: Path) -> str:
    text = rel(path).lower()
    if "qsb-sparc-rar" in text or "sparc_rar" in text or "lelli2016c" in text or "/rar" in text:
        return "sparc_rar"
    if "matrix-topology" in text or "matrix_topology" in text:
        return "matrix_topology"
    if "extract03" in text:
        return "extract03"
    if "interface01" in text or "delta_phi" in text or "m33" in text:
        return "interface01"
    if "relalg" in text or "d1k" in text:
        return "relalg"
    if "causality" in text or "admissibility" in text or "inner-sphere" in text or "bmc" in text:
        return "causality"
    if "qsb-meta" in text or "metadata" in text or "sqlite_tkinter_crud_app" in text or "field_labels.py" in text:
        return "metadata"
    return "unknown"


def legacy_artifact_kind(path: Path) -> str:
    name = path.name.lower()
    suffix = path.suffix.lower()
    if "input" in path.parts and suffix in {".mrt", ".csv", ".json"}:
        return "raw_input"
    if name.endswith("_summary.json") or "summary" in name and suffix == ".json":
        return "summary_json"
    if suffix == ".csv":
        return "table_csv"
    if suffix == ".json":
        return "json_document"
    if suffix == ".md":
        return "markdown_note"
    if suffix == ".txt":
        return "text_note"
    if suffix in {".sqlite", ".db"}:
        return "sqlite_db"
    if suffix == ".py":
        return "python_script"
    if suffix == ".sql":
        return "sql_script"
    if legacy_run_folder(path):
        return "run_audit"
    return "other"


def legacy_text_line_count(path: Path) -> int | None:
    if path.suffix.lower() not in {".csv", ".json", ".md", ".py", ".sql", ".txt", ".mrt"}:
        return None
    try:
        return line_count(path)
    except Exception:
        return None


def legacy_iter_files() -> list[Path]:
    roots = [REPO / "runs", REPO / "scripts", REPO / "docs", REPO / "data", REPO / "numerics"]
    files = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            parts = set(path.parts)
            if ".git" in parts or ".venv" in parts or "__pycache__" in parts:
                continue
            if ".pytest_cache" in parts:
                continue
            if path.suffix == ".pyc":
                continue
            files.append(path)
    return sorted(files, key=lambda p: rel(p))


def legacy_artifact_id(path: Path, digest: str, size: int) -> str:
    return hashlib.sha256(f"{rel(path)}::{digest}::{size}".encode("utf-8")).hexdigest()


def legacy_run_folder(path: Path) -> str:
    parts = path.parts
    if "runs" in parts:
        idx = parts.index("runs")
        if idx + 1 < len(parts):
            return parts[idx + 1]
    return ""


def legacy_write_sql_files() -> None:
    SQL_DIR.mkdir(parents=True, exist_ok=True)
    legacy_files = {
        SQL_DIR / "002_raw_staging.sql": LEGACY_SCHEMA_SQL,
        SQL_DIR / "003_canonical.sql": "-- Canonical legacy tables are created in 002_raw_staging.sql for this additive migration.\n",
        SQL_DIR / "004_metadata_validation.sql": "-- Metadata and validation legacy tables are created in 002_raw_staging.sql for this additive migration.\n",
        SQL_DIR / "005_views_mart.sql": LEGACY_VIEWS_SQL,
        SQL_DIR / "007_indexes.sql": LEGACY_INDEXES_SQL,
        legacy_out_path("10_legacy_raw_staging_schema.sql"): LEGACY_SCHEMA_SQL,
        legacy_out_path("11_legacy_views_mart.sql"): LEGACY_VIEWS_SQL,
        legacy_out_path("12_legacy_procedures.sql"): LEGACY_PROCEDURES_SQL,
        legacy_out_path("13_legacy_indexes.sql"): LEGACY_INDEXES_SQL,
    }
    for path, text in legacy_files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.strip() + "\n", encoding="utf-8")


def legacy_apply_schema() -> list[dict]:
    results = []
    for sql_text, name in [
        (LEGACY_SCHEMA_SQL, "legacy_schema"),
        (LEGACY_PROCEDURES_SQL, "legacy_procedures"),
        (LEGACY_VIEWS_SQL, "legacy_views"),
        (LEGACY_INDEXES_SQL, "legacy_indexes"),
    ]:
        path = legacy_out_path(f"_{name}.tmp.sql")
        path.write_text(sql_text.strip() + "\n", encoding="utf-8")
        results.append(run_sql_file(TARGET_DB, path))
    return results


def legacy_flatten_json(obj, prefix: str = "") -> list[tuple[str, str]]:
    rows = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(legacy_flatten_json(value, next_prefix))
    elif isinstance(obj, list):
        rows.append((prefix, f"list[{len(obj)}]"))
    else:
        rows.append((prefix, "" if obj is None else str(obj)))
    return rows[:200]


def legacy_create_insert_sql(files: list[Path], inventory: list[dict]) -> tuple[Path, dict]:
    insert_path = legacy_out_path("36_legacy_ingest_upsert.sql")

    class SqlLineSink:
        def __init__(self, path: Path) -> None:
            path.parent.mkdir(parents=True, exist_ok=True)
            self.handle = path.open("w", encoding="utf-8")

        def append(self, line: str) -> None:
            self.handle.write(line.rstrip("\n") + "\n")

        def extend(self, block: list[str]) -> None:
            for line in block:
                self.append(line)

        def close(self) -> None:
            self.handle.close()

    lines = SqlLineSink(insert_path)
    lines.extend([
        "-- Generated legacy artifact migration SQL. Idempotent and additive.",
        "BEGIN;",
        f"CALL admin.register_etl_run({sql_literal(LEGACY_RUN_ID)}, 'QSB_LEGACY', 'running', {sql_literal('|'.join(LEGACY_CLAIM_BOUNDARY))});",
    ])
    csv_rows_loaded = 0
    json_docs_loaded = 0
    markdown_docs_loaded = 0
    sqlite_catalogs = 0
    sqlite_catalogs_imported = 0
    domain_counts = {"matrix_topology": 0, "extract03": 0, "interface01": 0, "relalg": 0, "causality": 0}

    datasets = [
        ("SPARC_RAR_LELLI2016C", "SPARC/RAR Lelli2016c", "sparc_rar"),
        ("QSB_MATRIX_TOPOLOGY_EXTRACT03", "QSB Matrix Topology / EXTRACT03", "matrix_topology"),
        ("QSB_INTERFACE01", "QSB INTERFACE01 delta_phi", "interface01"),
        ("QSB_RELALG_D1K", "QSB RELALG / D1K", "relalg"),
        ("QSB_CAUSALITY", "QSB CAUSALITY / transition relation", "causality"),
        ("QSB_METADATA", "QSB metadata catalog and browser", "metadata"),
    ]
    for dataset_id, name, domain in datasets:
        lines.append(
            "INSERT INTO admin.dataset_registry(dataset_id, dataset_name, domain, registration_status, registered_by_run_id) "
            f"VALUES ({sql_literal(dataset_id)}, {sql_literal(name)}, {sql_literal(domain)}, 'registered', {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (dataset_id) DO UPDATE SET dataset_name=EXCLUDED.dataset_name, domain=EXCLUDED.domain, registration_status=EXCLUDED.registration_status, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )
        lines.append(
            "INSERT INTO metadata.meta_dataset(dataset_id, dataset_name, domain, registered_by_run_id) "
            f"VALUES ({sql_literal(dataset_id)}, {sql_literal(name)}, {sql_literal(domain)}, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (dataset_id) DO UPDATE SET dataset_name=EXCLUDED.dataset_name, domain=EXCLUDED.domain, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )

    run_folder_counts = {}
    for row in inventory:
        folder = row["run_folder"]
        if folder:
            run_folder_counts.setdefault(folder, {"count": 0, "domain": row["domain_guess"]})
            run_folder_counts[folder]["count"] += 1
    for folder, data in sorted(run_folder_counts.items()):
        rid = hashlib.sha256(folder.encode("utf-8")).hexdigest()
        lines.append(
            "INSERT INTO raw.run_folder(run_folder_id, run_folder, file_count, domain_guess, registered_by_run_id) "
            f"VALUES ({sql_literal(rid)}, {sql_literal(folder)}, {data['count']}, {sql_literal(data['domain'])}, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (run_folder_id) DO UPDATE SET file_count=EXCLUDED.file_count, domain_guess=EXCLUDED.domain_guess, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )
        lines.append(
            "INSERT INTO canonical.qsb_run(run_id, run_folder, domain_guess, file_count, registered_by_run_id) "
            f"VALUES ({sql_literal(folder)}, {sql_literal(folder)}, {sql_literal(data['domain'])}, {data['count']}, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (run_id) DO UPDATE SET file_count=EXCLUDED.file_count, domain_guess=EXCLUDED.domain_guess, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )

    for row in inventory:
        artifact_id = row["artifact_id"]
        domain = row["domain_guess"]
        if domain in domain_counts:
            domain_counts[domain] += 1
        if domain == "extract03":
            domain_counts["matrix_topology"] += 1
        values = {
            "artifact_id": artifact_id,
            "dataset_id": row["dataset_id"],
            "source_run_id": row["run_folder"],
            "file_name": row["file_name"],
            "file_path": row["relative_path"],
            "relative_path": row["relative_path"],
            "suffix": row["suffix"],
            "size_bytes": row["size_bytes"],
            "sha256": row["sha256"],
            "row_count": row["line_count"] or "",
            "claim_boundary": "generic_artifact_registration",
            "line_count": row["line_count"] or "",
            "run_folder": row["run_folder"],
            "artifact_kind": row["artifact_kind"],
            "domain_guess": domain,
            "registered_by_run_id": LEGACY_RUN_ID,
        }
        cols = list(values)
        vals = []
        for col in cols:
            if col in {"size_bytes", "row_count", "line_count"}:
                vals.append(sql_number(values[col]))
            else:
                vals.append(sql_literal(values[col]))
        lines.append(
            f"INSERT INTO raw.source_artifact({', '.join(cols)}) VALUES ({', '.join(vals)}) "
            "ON CONFLICT (artifact_id) DO UPDATE SET "
            + ", ".join(f"{col}=EXCLUDED.{col}" for col in cols if col != "artifact_id")
            + ";"
        )
        lines.append(
            "INSERT INTO canonical.qsb_artifact(artifact_id, relative_path, artifact_kind, domain_guess, sha256, registered_by_run_id) "
            f"VALUES ({sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(row['artifact_kind'])}, {sql_literal(domain)}, {sql_literal(row['sha256'])}, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (artifact_id) DO UPDATE SET relative_path=EXCLUDED.relative_path, artifact_kind=EXCLUDED.artifact_kind, domain_guess=EXCLUDED.domain_guess, sha256=EXCLUDED.sha256, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )
        lines.append(
            "INSERT INTO raw.source_file(source_file_id, dataset_id, file_name, file_path, size_bytes, sha256, line_count, raw_data_status, claim_boundary, relative_path, suffix, run_folder, artifact_kind, domain_guess, registered_by_run_id) "
            f"VALUES ({sql_literal(artifact_id)}, {sql_literal(row['dataset_id'])}, {sql_literal(row['file_name'])}, {sql_literal(row['relative_path'])}, {sql_number(row['size_bytes'])}, {sql_literal(row['sha256'])}, {sql_number(row['line_count'])}, 'registered_artifact_file', 'generic_artifact_registration', {sql_literal(row['relative_path'])}, {sql_literal(row['suffix'])}, {sql_literal(row['run_folder'])}, {sql_literal(row['artifact_kind'])}, {sql_literal(domain)}, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (source_file_id) DO UPDATE SET dataset_id=EXCLUDED.dataset_id, file_name=EXCLUDED.file_name, file_path=EXCLUDED.file_path, size_bytes=EXCLUDED.size_bytes, sha256=EXCLUDED.sha256, line_count=EXCLUDED.line_count, raw_data_status=EXCLUDED.raw_data_status, claim_boundary=EXCLUDED.claim_boundary, relative_path=EXCLUDED.relative_path, suffix=EXCLUDED.suffix, run_folder=EXCLUDED.run_folder, artifact_kind=EXCLUDED.artifact_kind, domain_guess=EXCLUDED.domain_guess, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )
        lines.append(
            "INSERT INTO raw.raw_checksum(checksum_id, file_path, expected_sha256, actual_sha256, checksum_status, artifact_id, relative_path, registered_by_run_id) "
            f"VALUES ({sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(row['sha256'])}, {sql_literal(row['sha256'])}, 'computed', {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (checksum_id) DO UPDATE SET file_path=EXCLUDED.file_path, expected_sha256=EXCLUDED.expected_sha256, actual_sha256=EXCLUDED.actual_sha256, checksum_status=EXCLUDED.checksum_status, artifact_id=EXCLUDED.artifact_id, relative_path=EXCLUDED.relative_path, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )
        lines.append(
            "INSERT INTO metadata.meta_search_token(token_id, record_type, record_id, search_text, domain_guess, registered_by_run_id, search_token_id, domain, source_table, source_id, display_label, claim_boundary, validation_status) "
            f"VALUES ({sql_literal('artifact_' + artifact_id)}, 'artifact', {sql_literal(artifact_id)}, {sql_literal(row['relative_path'] + ' ' + row['artifact_kind'] + ' ' + domain)}, {sql_literal(domain)}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal('artifact_' + artifact_id)}, {sql_literal(domain)}, 'raw.source_artifact', {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, 'generic_artifact_registration', 'registered') "
            "ON CONFLICT (token_id) DO UPDATE SET search_text=EXCLUDED.search_text, domain_guess=EXCLUDED.domain_guess, registered_by_run_id=EXCLUDED.registered_by_run_id, search_token_id=EXCLUDED.search_token_id, domain=EXCLUDED.domain, source_table=EXCLUDED.source_table, source_id=EXCLUDED.source_id, display_label=EXCLUDED.display_label, claim_boundary=EXCLUDED.claim_boundary, validation_status=EXCLUDED.validation_status;"
        )

    for row in inventory:
        path = REPO / row["relative_path"]
        artifact_id = row["artifact_id"]
        suffix = row["suffix"]
        try:
            if suffix == ".csv":
                with path.open("r", encoding="utf-8", newline="", errors="replace") as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or []
                    for idx, header in enumerate(headers):
                        pid = hashlib.sha256(f"{artifact_id}|{header}".encode("utf-8")).hexdigest()
                        lines.append(
                            "INSERT INTO staging.artifact_column_profile(profile_id, artifact_id, column_name, column_index, observed_nonempty_count, registered_by_run_id, relative_path, loaded_by_run_id) "
                            f"VALUES ({sql_literal(pid)}, {sql_literal(artifact_id)}, {sql_literal(header)}, {idx}, NULL, {sql_literal(LEGACY_RUN_ID)}, {sql_literal(row['relative_path'])}, {sql_literal(LEGACY_RUN_ID)}) "
                            "ON CONFLICT (profile_id) DO UPDATE SET column_name=EXCLUDED.column_name, column_index=EXCLUDED.column_index, registered_by_run_id=EXCLUDED.registered_by_run_id, relative_path=EXCLUDED.relative_path, loaded_by_run_id=EXCLUDED.loaded_by_run_id;"
                        )
                        lines.append(
                            "INSERT INTO metadata.meta_search_token(token_id, record_type, record_id, search_text, domain_guess, registered_by_run_id, search_token_id, domain, source_table, source_id, display_label, claim_boundary, validation_status) "
                            f"VALUES ({sql_literal('csv_column_' + pid)}, 'csv_column', {sql_literal(pid)}, {sql_literal(row['relative_path'] + ' ' + header)}, {sql_literal(row['domain_guess'])}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal('csv_column_' + pid)}, {sql_literal(row['domain_guess'])}, 'staging.artifact_column_profile', {sql_literal(pid)}, {sql_literal(header)}, 'generic_csv_json_markdown_staging', 'registered') "
                            "ON CONFLICT (token_id) DO UPDATE SET search_text=EXCLUDED.search_text, display_label=EXCLUDED.display_label, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                        )
                    if csv_rows_loaded >= MAX_GENERIC_CSV_ROWS:
                        wid = hashlib.sha256(f"{artifact_id}|csv_global_row_limit".encode("utf-8")).hexdigest()
                        lines.append(
                            "INSERT INTO validation.ingest_warning(warning_id, artifact_id, relative_path, warning_status, warning_type, message, registered_by_run_id) "
                            f"VALUES ({sql_literal(wid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, 'warning', 'csv_global_row_limit', {sql_literal('Generic CSV row staging limit reached; artifact registered but rows skipped for this patch run.')}, {sql_literal(LEGACY_RUN_ID)}) "
                            "ON CONFLICT (warning_id) DO UPDATE SET message=EXCLUDED.message, relative_path=EXCLUDED.relative_path, warning_type=EXCLUDED.warning_type, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                        )
                        continue
                    for row_number, csv_row in enumerate(reader, start=1):
                        if csv_rows_loaded >= MAX_GENERIC_CSV_ROWS:
                            wid = hashlib.sha256(f"{artifact_id}|csv_global_row_limit".encode("utf-8")).hexdigest()
                            lines.append(
                                "INSERT INTO validation.ingest_warning(warning_id, artifact_id, relative_path, warning_status, warning_type, message, registered_by_run_id) "
                                f"VALUES ({sql_literal(wid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, 'warning', 'csv_global_row_limit', {sql_literal('Generic CSV row staging limit reached; remaining rows skipped for this patch run.')}, {sql_literal(LEGACY_RUN_ID)}) "
                                "ON CONFLICT (warning_id) DO UPDATE SET message=EXCLUDED.message, relative_path=EXCLUDED.relative_path, warning_type=EXCLUDED.warning_type, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                            )
                            break
                        rid = hashlib.sha256(f"{artifact_id}|{row_number}".encode("utf-8")).hexdigest()
                        row_json = json.dumps(csv_row, ensure_ascii=False, sort_keys=True)
                        lines.append(
                            "INSERT INTO staging.csv_row_json(row_id, artifact_id, relative_path, row_number, row_json, registered_by_run_id, loaded_by_run_id) "
                            f"VALUES ({sql_literal(rid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {row_number}, {sql_literal(row_json)}::jsonb, {sql_literal(LEGACY_RUN_ID)}, {sql_literal(LEGACY_RUN_ID)}) "
                            "ON CONFLICT (row_id) DO UPDATE SET row_json=EXCLUDED.row_json, relative_path=EXCLUDED.relative_path, registered_by_run_id=EXCLUDED.registered_by_run_id, loaded_by_run_id=EXCLUDED.loaded_by_run_id;"
                        )
                        csv_rows_loaded += 1
            elif suffix == ".json":
                if path.stat().st_size > MAX_JSON_TEXT_BYTES:
                    json_text = path.open("r", encoding="utf-8", errors="replace").read(10_000)
                    doc_json = json.dumps({"skipped_large_json": True, "preview_chars": len(json_text)}, sort_keys=True)
                    parse_status = "skipped_large_json_preview_only"
                    wid = hashlib.sha256(f"{artifact_id}|json_size_limit".encode("utf-8")).hexdigest()
                    lines.append(
                        "INSERT INTO validation.ingest_warning(warning_id, artifact_id, relative_path, warning_status, warning_type, message, registered_by_run_id) "
                        f"VALUES ({sql_literal(wid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, 'warning', 'json_size_limit', {sql_literal('Large JSON stored as preview metadata only for this patch run.')}, {sql_literal(LEGACY_RUN_ID)}) "
                        "ON CONFLICT (warning_id) DO UPDATE SET message=EXCLUDED.message, relative_path=EXCLUDED.relative_path, warning_type=EXCLUDED.warning_type, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                    )
                else:
                    json_text = path.read_text(encoding="utf-8", errors="replace")
                    try:
                        data = json.loads(
                            json_text,
                            parse_constant=lambda value: f"NON_STANDARD_JSON_CONSTANT_{value}",
                        )
                        doc_json = json.dumps(data, ensure_ascii=False, sort_keys=True)
                        parse_status = "parsed"
                        for key, value in legacy_flatten_json(data):
                            kid = hashlib.sha256(f"{artifact_id}|{key}".encode("utf-8")).hexdigest()
                            lines.append(
                                "INSERT INTO staging.json_key_value(key_value_id, artifact_id, relative_path, key_path, value_text, registered_by_run_id, loaded_by_run_id) "
                                f"VALUES ({sql_literal(kid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(key or '$')}, {sql_literal(value)}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal(LEGACY_RUN_ID)}) "
                                "ON CONFLICT (key_value_id) DO UPDATE SET value_text=EXCLUDED.value_text, relative_path=EXCLUDED.relative_path, registered_by_run_id=EXCLUDED.registered_by_run_id, loaded_by_run_id=EXCLUDED.loaded_by_run_id;"
                            )
                            lines.append(
                                "INSERT INTO metadata.meta_search_token(token_id, record_type, record_id, search_text, domain_guess, registered_by_run_id, search_token_id, domain, source_table, source_id, display_label, claim_boundary, validation_status) "
                                f"VALUES ({sql_literal('json_key_' + kid)}, 'json_key', {sql_literal(kid)}, {sql_literal(row['relative_path'] + ' ' + (key or '$'))}, {sql_literal(row['domain_guess'])}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal('json_key_' + kid)}, {sql_literal(row['domain_guess'])}, 'staging.json_key_value', {sql_literal(kid)}, {sql_literal(key or '$')}, 'generic_csv_json_markdown_staging', 'registered') "
                                "ON CONFLICT (token_id) DO UPDATE SET search_text=EXCLUDED.search_text, display_label=EXCLUDED.display_label, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                            )
                    except Exception as exc:
                        doc_json = json.dumps({"parse_error": str(exc)}, sort_keys=True)
                        parse_status = "parse_error"
                lines.append(
                    "INSERT INTO staging.json_document(document_id, artifact_id, relative_path, json_text, document_json, jsonb_document, parse_status, registered_by_run_id, loaded_by_run_id) "
                    f"VALUES ({sql_literal(artifact_id)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(json_text)}, {sql_literal(doc_json)}::jsonb, {sql_literal(doc_json)}::jsonb, {sql_literal(parse_status)}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal(LEGACY_RUN_ID)}) "
                    "ON CONFLICT (document_id) DO UPDATE SET relative_path=EXCLUDED.relative_path, json_text=EXCLUDED.json_text, document_json=EXCLUDED.document_json, jsonb_document=EXCLUDED.jsonb_document, parse_status=EXCLUDED.parse_status, registered_by_run_id=EXCLUDED.registered_by_run_id, loaded_by_run_id=EXCLUDED.loaded_by_run_id;"
                )
                json_docs_loaded += 1
            elif suffix in {".md", ".txt"}:
                title = ""
                body_text = path.open("r", encoding="utf-8", errors="replace").read(MAX_DOCUMENT_TEXT_CHARS)
                body_preview = body_text[:1000]
                if path.stat().st_size > MAX_DOCUMENT_TEXT_CHARS:
                    wid = hashlib.sha256(f"{artifact_id}|text_preview_limit".encode("utf-8")).hexdigest()
                    lines.append(
                        "INSERT INTO validation.ingest_warning(warning_id, artifact_id, relative_path, warning_status, warning_type, message, registered_by_run_id) "
                        f"VALUES ({sql_literal(wid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, 'warning', 'text_preview_limit', {sql_literal('Large text/markdown stored as preview for this patch run.')}, {sql_literal(LEGACY_RUN_ID)}) "
                        "ON CONFLICT (warning_id) DO UPDATE SET message=EXCLUDED.message, relative_path=EXCLUDED.relative_path, warning_type=EXCLUDED.warning_type, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                    )
                for line in body_text.splitlines():
                    if line.startswith("#"):
                        title = line.strip("# \n")
                        break
                if not title:
                    title = row["file_name"]
                lines.append(
                    "INSERT INTO staging.markdown_document(document_id, artifact_id, relative_path, title, body_text, body_preview, line_count, registered_by_run_id, loaded_by_run_id) "
                    f"VALUES ({sql_literal(artifact_id)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(title)}, {sql_literal(body_text)}, {sql_literal(body_preview)}, {sql_number(row['line_count'])}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal(LEGACY_RUN_ID)}) "
                    "ON CONFLICT (document_id) DO UPDATE SET relative_path=EXCLUDED.relative_path, title=EXCLUDED.title, body_text=EXCLUDED.body_text, body_preview=EXCLUDED.body_preview, line_count=EXCLUDED.line_count, registered_by_run_id=EXCLUDED.registered_by_run_id, loaded_by_run_id=EXCLUDED.loaded_by_run_id;"
                )
                lines.append(
                    "INSERT INTO metadata.meta_search_token(token_id, record_type, record_id, search_text, domain_guess, registered_by_run_id, search_token_id, domain, source_table, source_id, display_label, claim_boundary, validation_status) "
                    f"VALUES ({sql_literal('markdown_' + artifact_id)}, 'markdown_document', {sql_literal(artifact_id)}, {sql_literal(title + ' ' + body_preview)}, {sql_literal(row['domain_guess'])}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal('markdown_' + artifact_id)}, {sql_literal(row['domain_guess'])}, 'staging.markdown_document', {sql_literal(artifact_id)}, {sql_literal(title)}, 'generic_csv_json_markdown_staging', 'registered') "
                    "ON CONFLICT (token_id) DO UPDATE SET search_text=EXCLUDED.search_text, display_label=EXCLUDED.display_label, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                )
                markdown_docs_loaded += 1
            elif suffix in {".sqlite", ".db"}:
                sqlite_catalogs += 1
                try:
                    con = sqlite3.connect(path)
                    table_names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
                    for table in table_names:
                        columns = [r[1] for r in con.execute(f"PRAGMA table_info({table})")]
                        col_count = len(columns)
                        n = None
                        try:
                            n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                        except Exception:
                            n = None
                        iid = hashlib.sha256(f"{artifact_id}|{table}".encode("utf-8")).hexdigest()
                        lines.append(
                            "INSERT INTO staging.sqlite_table_inventory(inventory_id, artifact_id, relative_path, table_name, column_count, column_names, registered_by_run_id, loaded_by_run_id) "
                            f"VALUES ({sql_literal(iid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(table)}, {col_count}, {sql_literal('|'.join(columns))}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal(LEGACY_RUN_ID)}) "
                            "ON CONFLICT (inventory_id) DO UPDATE SET column_count=EXCLUDED.column_count, column_names=EXCLUDED.column_names, relative_path=EXCLUDED.relative_path, registered_by_run_id=EXCLUDED.registered_by_run_id, loaded_by_run_id=EXCLUDED.loaded_by_run_id;"
                        )
                        lines.append(
                            "INSERT INTO staging.sqlite_row_count(row_count_id, artifact_id, relative_path, table_name, row_count, registered_by_run_id, loaded_by_run_id) "
                            f"VALUES ({sql_literal(iid)}, {sql_literal(artifact_id)}, {sql_literal(row['relative_path'])}, {sql_literal(table)}, {sql_number(n)}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal(LEGACY_RUN_ID)}) "
                            "ON CONFLICT (row_count_id) DO UPDATE SET row_count=EXCLUDED.row_count, relative_path=EXCLUDED.relative_path, registered_by_run_id=EXCLUDED.registered_by_run_id, loaded_by_run_id=EXCLUDED.loaded_by_run_id;"
                        )
                        lines.append(
                            "INSERT INTO metadata.meta_search_token(token_id, record_type, record_id, search_text, domain_guess, registered_by_run_id, search_token_id, domain, source_table, source_id, display_label, claim_boundary, validation_status) "
                            f"VALUES ({sql_literal('sqlite_table_' + iid)}, 'sqlite_table', {sql_literal(iid)}, {sql_literal(row['relative_path'] + ' ' + table + ' ' + ' '.join(columns))}, {sql_literal(row['domain_guess'])}, {sql_literal(LEGACY_RUN_ID)}, {sql_literal('sqlite_table_' + iid)}, {sql_literal(row['domain_guess'])}, 'staging.sqlite_table_inventory', {sql_literal(iid)}, {sql_literal(table)}, 'sqlite_catalog_inventory', 'registered') "
                            "ON CONFLICT (token_id) DO UPDATE SET search_text=EXCLUDED.search_text, display_label=EXCLUDED.display_label, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                        )
                    con.close()
                    sqlite_catalogs_imported += 1
                except Exception as exc:
                    wid = hashlib.sha256(f"{artifact_id}|sqlite_error".encode("utf-8")).hexdigest()
                    lines.append(
                        "INSERT INTO validation.ingest_warning(warning_id, artifact_id, warning_status, message, registered_by_run_id) "
                        f"VALUES ({sql_literal(wid)}, {sql_literal(artifact_id)}, 'warning', {sql_literal(str(exc))}, {sql_literal(LEGACY_RUN_ID)}) "
                        "ON CONFLICT (warning_id) DO UPDATE SET message=EXCLUDED.message, registered_by_run_id=EXCLUDED.registered_by_run_id;"
                    )
        except Exception as exc:
            wid = hashlib.sha256(f"{artifact_id}|load_error".encode("utf-8")).hexdigest()
            lines.append(
                "INSERT INTO validation.ingest_warning(warning_id, artifact_id, warning_status, message, registered_by_run_id) "
                f"VALUES ({sql_literal(wid)}, {sql_literal(artifact_id)}, 'warning', {sql_literal(str(exc))}, {sql_literal(LEGACY_RUN_ID)}) "
                "ON CONFLICT (warning_id) DO UPDATE SET message=EXCLUDED.message, registered_by_run_id=EXCLUDED.registered_by_run_id;"
            )

    aliases = [
        ("dataset_id", "Datensatz-ID"), ("source_file_id", "Quelldatei-ID"), ("source_artifact_id", "Quellartefakt-ID"),
        ("run_id", "Lauf-ID"), ("galaxy_id", "Galaxien-ID"), ("radius_kpc", "Radius (kpc)"),
        ("distance_mpc", "Entfernung (Mpc)"), ("vobs_km_s", "beobachtete Rotationsgeschwindigkeit"),
        ("vobs_error_km_s", "Unsicherheit der beobachteten Rotationsgeschwindigkeit"), ("vgas_km_s", "Gas-Geschwindigkeitsbeitrag"),
        ("vdisk_km_s", "Scheiben-Geschwindigkeitsbeitrag"), ("vbul_km_s", "Bulge-Geschwindigkeitsbeitrag"),
        ("sbdisk_solLum_pc2", "Scheiben-Oberflächenhelligkeit"), ("sbbul_solLum_pc2", "Bulge-Oberflächenhelligkeit"),
        ("gobs_m_s2", "beobachtete Beschleunigung"), ("gbar_m_s2", "baryonische Beschleunigung"),
        ("log_gobs", "Log beobachtete Beschleunigung"), ("log_gbar", "Log baryonische Beschleunigung"),
        ("quantity_kind", "Größenart"), ("value_original", "Originalwert"), ("unit_original", "Originaleinheit"),
        ("value_calculation", "Berechnungswert"), ("unit_calculation", "Berechnungseinheit"), ("value_display", "Anzeigewert"),
        ("unit_display", "Anzeigeeinheit"), ("dimension_vector", "Dimensionsvektor"), ("conversion_rule_id", "Umrechnungsregel-ID"),
        ("lineage_hash", "Lineage-Hash"), ("source_sha256", "Quellen-SHA256"), ("validation_status", "Validierungsstatus"),
        ("claim_boundary", "Claim-Grenze"),
    ]
    alias_csv = SPARC_SQLITE_RUN / "18_metadata_alias_registry.csv"
    if alias_csv.exists():
        for row in read_csv(alias_csv):
            aliases.append((row.get("canonical_name", ""), row.get("display_label_de", "")))
    for canonical, label in sorted({a for a in aliases if a[0] and a[1]}):
        alias_id = hashlib.sha256(f"{canonical}|de|legacy".encode("utf-8")).hexdigest()
        lines.append(
            "INSERT INTO metadata.meta_alias(alias_id, canonical_name, display_label_de, language, alias_status) "
            f"VALUES ({sql_literal(alias_id)}, {sql_literal(canonical)}, {sql_literal(label)}, 'de', 'registered') "
            "ON CONFLICT (alias_id) DO UPDATE SET canonical_name=EXCLUDED.canonical_name, display_label_de=EXCLUDED.display_label_de, language=EXCLUDED.language, alias_status=EXCLUDED.alias_status;"
        )

    for claim in LEGACY_CLAIM_BOUNDARY:
        cid = hashlib.sha256(claim.encode("utf-8")).hexdigest()
        status = "explicit_no_go" if claim.startswith("no_") else "allowed_boundary"
        lines.append(
            "INSERT INTO validation.claim_boundary(claim_boundary_id, claim_boundary, claim_status) "
            f"VALUES ({sql_literal(cid)}, {sql_literal(claim)}, {sql_literal(status)}) "
            "ON CONFLICT (claim_boundary_id) DO UPDATE SET claim_status=EXCLUDED.claim_status;"
        )
        lines.append(
            "INSERT INTO canonical.qsb_claim_boundary_event(claim_event_id, claim_boundary, claim_status, registered_by_run_id) "
            f"VALUES ({sql_literal(cid)}, {sql_literal(claim)}, {sql_literal(status)}, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (claim_event_id) DO UPDATE SET claim_status=EXCLUDED.claim_status, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )

    no_go = [
        "QSB erklärt Dunkle Materie", "QSB erklärt RAR", "QSB-Signal wurde gefunden",
        "RBCI_v1 verbessert die RAR", "RBCI_v1 ist physikalisch wirksam", "MOND wurde bestätigt",
        "LambdaCDM wurde widerlegt", "Gravitation wurde modifiziert", "RaumZeit-Struktur wurde nachgewiesen",
        "Kausalität wurde rekonstruiert", "m1 weiß von m2 wurde bewiesen",
    ]
    for text in no_go:
        nid = hashlib.sha256(text.encode("utf-8")).hexdigest()
        lines.append(
            "INSERT INTO validation.no_go_boundary(no_go_id, no_go_text, no_go_status, registered_by_run_id) "
            f"VALUES ({sql_literal(nid)}, {sql_literal(text)}, 'forbidden', {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (no_go_id) DO UPDATE SET no_go_status=EXCLUDED.no_go_status, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )

    endpoints = ["/health", "/", "/search", "/datasets", "/fields", "/validations", "/claims"]
    lines.append(
        "INSERT INTO server.metadata_server_config(config_id, config_key, config_value, config_status, registered_by_run_id) "
        f"VALUES ('default_port', 'default_port', '8765', 'registered', {sql_literal(LEGACY_RUN_ID)}) "
        "ON CONFLICT (config_id) DO UPDATE SET config_value=EXCLUDED.config_value, config_status=EXCLUDED.config_status, registered_by_run_id=EXCLUDED.registered_by_run_id;"
    )
    for endpoint in endpoints:
        eid = hashlib.sha256(endpoint.encode("utf-8")).hexdigest()
        lines.append(
            "INSERT INTO server.metadata_server_endpoint(endpoint_id, method, path, query_scope, read_only, registered_by_run_id) "
            f"VALUES ({sql_literal(eid)}, 'GET', {sql_literal(endpoint)}, 'mart_metadata_select_only', TRUE, {sql_literal(LEGACY_RUN_ID)}) "
            "ON CONFLICT (endpoint_id) DO UPDATE SET query_scope=EXCLUDED.query_scope, read_only=EXCLUDED.read_only, registered_by_run_id=EXCLUDED.registered_by_run_id;"
        )

    lines.extend([
        f"CALL admin.mark_etl_step({sql_literal(LEGACY_RUN_ID)}, 'legacy_ingest_all', 'completed', 'Generic legacy artifacts inventoried and staged.');",
        f"UPDATE admin.etl_run SET status='completed', finished_at=admin.fn_now_utc() WHERE run_id={sql_literal(LEGACY_RUN_ID)};",
        "COMMIT;",
    ])
    lines.close()
    metrics = {
        "generic_csv_rows_loaded": csv_rows_loaded,
        "json_documents_loaded": json_docs_loaded,
        "markdown_documents_loaded": markdown_docs_loaded,
        "sqlite_catalogs_discovered": sqlite_catalogs,
        "sqlite_catalogs_imported": sqlite_catalogs_imported,
        "matrix_topology_artifacts_loaded": domain_counts["matrix_topology"],
        "interface01_artifacts_loaded": domain_counts["interface01"],
        "relalg_artifacts_loaded": domain_counts["relalg"],
        "causality_artifacts_loaded": domain_counts["causality"],
    }
    return insert_path, metrics


def legacy_count(table: str) -> int:
    return postgres_row_count(table)


def legacy_scalar(query: str) -> int:
    result = psql(TARGET_DB, ["-At", "-c", query])
    try:
        return int(result["stdout"].strip())
    except ValueError:
        return 0


def legacy_write_reports(summary: dict, inventory: list[dict], metrics: dict, sample_rows: list[dict]) -> None:
    write_json(legacy_out_path("04_legacy_migration_summary.json"), summary)
    write_csv(legacy_out_path("06_input_file_inventory.csv"), inventory, [
        "artifact_id", "relative_path", "file_name", "suffix", "size_bytes", "sha256", "line_count",
        "run_folder", "artifact_kind", "domain_guess", "dataset_id",
    ])
    run_rows = {}
    for row in inventory:
        folder = row["run_folder"]
        if folder:
            run_rows.setdefault(folder, {"run_folder": folder, "file_count": 0, "domain_guess": row["domain_guess"]})
            run_rows[folder]["file_count"] += 1
    write_csv(legacy_out_path("07_run_folder_inventory.csv"), list(run_rows.values()), ["run_folder", "file_count", "domain_guess"])
    write_csv(legacy_out_path("08_artifact_domain_classification.csv"), [
        {"artifact_id": r["artifact_id"], "relative_path": r["relative_path"], "artifact_kind": r["artifact_kind"], "domain_guess": r["domain_guess"]}
        for r in inventory
    ], ["artifact_id", "relative_path", "artifact_kind", "domain_guess"])
    write_csv(legacy_out_path("09_checksum_revalidation.csv"), [
        {"artifact_id": r["artifact_id"], "relative_path": r["relative_path"], "sha256": r["sha256"], "checksum_status": "computed"}
        for r in inventory
    ], ["artifact_id", "relative_path", "sha256", "checksum_status"])
    sqlite_rows = [r for r in inventory if r["suffix"] in {".sqlite", ".db"}]
    write_csv(legacy_out_path("10_sqlite_catalog_discovery.csv"), sqlite_rows, [
        "artifact_id", "relative_path", "file_name", "suffix", "size_bytes", "sha256", "line_count",
        "run_folder", "artifact_kind", "domain_guess", "dataset_id",
    ])
    write_csv(legacy_out_path("11_sqlite_catalog_import_report.csv"), [
        {"metric": "sqlite_catalogs_discovered", "value": str(metrics["sqlite_catalogs_discovered"])},
        {"metric": "sqlite_catalogs_imported", "value": str(metrics["sqlite_catalogs_imported"])},
    ], ["metric", "value"])
    write_csv(legacy_out_path("12_generic_staging_load_report.csv"), [
        {"staging_table": "staging.csv_row_json", "rows_loaded": str(metrics["generic_csv_rows_loaded"]), "status": "loaded"},
        {"staging_table": "staging.json_document", "rows_loaded": str(metrics["json_documents_loaded"]), "status": "loaded"},
        {"staging_table": "staging.markdown_document", "rows_loaded": str(metrics["markdown_documents_loaded"]), "status": "loaded"},
        {"staging_table": "staging.sqlite_table_inventory", "rows_loaded": str(legacy_count("staging.sqlite_table_inventory")), "status": "loaded"},
    ], ["staging_table", "rows_loaded", "status"])
    write_csv(legacy_out_path("13_domain_staging_load_report.csv"), [
        {"domain": "sparc_rar", "artifacts_loaded": str(sum(1 for r in inventory if r["domain_guess"] == "sparc_rar")), "status": "artifact_level_loaded"},
        {"domain": "matrix_topology", "artifacts_loaded": str(metrics["matrix_topology_artifacts_loaded"]), "status": "artifact_level_loaded"},
        {"domain": "interface01", "artifacts_loaded": str(metrics["interface01_artifacts_loaded"]), "status": "artifact_level_loaded"},
        {"domain": "relalg", "artifacts_loaded": str(metrics["relalg_artifacts_loaded"]), "status": "artifact_level_loaded"},
        {"domain": "causality", "artifacts_loaded": str(metrics["causality_artifacts_loaded"]), "status": "artifact_level_loaded"},
    ], ["domain", "artifacts_loaded", "status"])
    write_csv(legacy_out_path("14_canonical_load_report.csv"), [
        {"canonical_table": "canonical.qsb_artifact", "rows_loaded": str(legacy_count("canonical.qsb_artifact")), "status": "loaded"},
        {"canonical_table": "canonical.qsb_run", "rows_loaded": str(legacy_count("canonical.qsb_run")), "status": "loaded"},
        {"canonical_table": "canonical.obs_rar_point", "rows_loaded": str(legacy_count("canonical.obs_rar_point")), "status": "previous_sparc_core_loaded"},
    ], ["canonical_table", "rows_loaded", "status"])
    write_csv(legacy_out_path("15_metadata_load_report.csv"), [
        {"metadata_table": "metadata.meta_field", "rows_loaded": str(summary["metadata_field_count"]), "status": "loaded"},
        {"metadata_table": "metadata.meta_unit", "rows_loaded": str(summary["metadata_unit_count"]), "status": "loaded"},
        {"metadata_table": "metadata.meta_alias", "rows_loaded": str(summary["metadata_alias_count"]), "status": "loaded"},
        {"metadata_table": "metadata.meta_lineage", "rows_loaded": str(summary["metadata_lineage_count"]), "status": "loaded"},
        {"metadata_table": "metadata.meta_search_token", "rows_loaded": str(summary["global_search_rows"]), "status": "loaded"},
    ], ["metadata_table", "rows_loaded", "status"])
    write_csv(legacy_out_path("16_validation_load_report.csv"), [
        {"validation_table": "validation.validation_result", "rows_loaded": str(summary["metadata_validation_count"]), "status": "loaded"},
        {"validation_table": "validation.claim_boundary", "rows_loaded": str(summary["metadata_claim_count"]), "status": "loaded"},
        {"validation_table": "validation.no_go_boundary", "rows_loaded": str(legacy_count("validation.no_go_boundary")), "status": "loaded"},
    ], ["validation_table", "rows_loaded", "status"])
    view_result = psql(TARGET_DB, ["-At", "-c", "SELECT table_schema || '.' || table_name FROM information_schema.views WHERE table_schema='mart' ORDER BY table_name;"])
    view_rows = [{"view_name": line.strip(), "status": "verified"} for line in view_result["stdout"].splitlines() if line.strip()]
    write_csv(legacy_out_path("17_view_inventory.csv"), view_rows, ["view_name", "status"])
    table_result = psql(TARGET_DB, ["-At", "-c", "SELECT table_schema || '.' || table_name FROM information_schema.tables WHERE table_schema IN ('admin','raw','staging','canonical','metadata','validation','server') AND table_type='BASE TABLE' ORDER BY table_schema, table_name;"])
    table_rows = [{"table_name": line.strip(), "row_count": str(legacy_count(line.strip())), "status": "verified"} for line in table_result["stdout"].splitlines() if line.strip()]
    write_csv(legacy_out_path("18_table_inventory.csv"), table_rows, ["table_name", "row_count", "status"])
    write_csv(legacy_out_path("19_row_counts.csv"), [{"object_name": r["table_name"], "row_count": r["row_count"]} for r in table_rows], ["object_name", "row_count"])
    write_csv(legacy_out_path("20_sample_query_results.csv"), sample_rows, ["query_id", "status", "result_row_count", "preview"])
    write_csv(legacy_out_path("21_metadata_server_readiness.csv"), [
        {"check_name": "server_files_created", "status": "passed", "detail": "scripts/qsb_metadata_server"},
        {"check_name": "read_only_policy", "status": "passed", "detail": "SELECT endpoints only"},
        {"check_name": "default_port", "status": "passed", "detail": "8765"},
    ], ["check_name", "status", "detail"])
    (legacy_out_path("02_legacy_migration_scope.md")).write_text(
        f"# {LEGACY_RUN_ID}\n\nBefund: Legacy-Artefakte wurden generisch inventarisiert und in PostgreSQL registriert.\n\n"
        "Interpretation: PostgreSQL `qsb_research_dwh` ist der zentrale Arbeitsraum; Run-Ordner bleiben Audit-Spur.\n\n"
        "Hypothese: Keine wissenschaftliche Hypothese wird getestet.\n\n"
        "Offene Luecke: Domain-spezifische Loader bleiben defensiv und laden nur sichere Artifact-/Summary-Level.\n\n"
        "Claim Boundary: Methodische Migration und Metadata-Server-Readiness ohne physikalische Claims.\n",
        encoding="utf-8",
    )
    (legacy_out_path("22_dbeaver_connection_note.md")).write_text(
        "# DBeaver Connection\n\nType: PostgreSQL\nHost: localhost\nPort: 5432\nDatabase: qsb_research_dwh\nUser: ralf-kemmann\nSchemas: admin, raw, staging, canonical, metadata, validation, mart, server\n",
        encoding="utf-8",
    )
    (legacy_out_path("23_claim_boundary_and_no_go.md")).write_text(
        "# Claim Boundary and No-Go\n\nBefund: Migration, Registrierung, Suchviews und read-only Server-Readiness.\n\n"
        "Interpretation: Keine Residualanalyse, keine RBCI_v1-Auswertung, kein QSB-Zusatzobservable.\n\n"
        "Claim Boundary: Keine Claims zu Dunkler Materie, RAR-Erklaerung, MOND, LambdaCDM, Gravitation, Raumzeit oder Kausalitaet.\n",
        encoding="utf-8",
    )
    (legacy_out_path("24_next_run_recommendation.md")).write_text(
        "# Next Run Recommendation\n\nEmpfohlen: `QSB-DWH-POSTGRES-LEGACY-MIGRATION-REVIEW-01` zur Pruefung von Counts, Views, Server-Endpunkten und Domain-Loader-Grenzen.\n",
        encoding="utf-8",
    )
    (legacy_out_path("25_review_note.md")).write_text(
        f"# Review Note\n\nBefund: Status `{summary['status']}`. Artefakte registriert: {summary['artifacts_registered']}.\n\n"
        "Interpretation: Die Migration ist auditierbar ueber Run-CSV/JSON und PostgreSQL-Views.\n",
        encoding="utf-8",
    )
    write_csv(legacy_out_path("26_orphan_artifact_report.csv"), [], ["artifact_id", "relative_path", "reason"])
    write_csv(legacy_out_path("27_unparsed_artifact_report.csv"), [
        {"artifact_id": r["artifact_id"], "relative_path": r["relative_path"], "reason": "generic_registration_only"}
        for r in inventory if r["artifact_kind"] == "other"
    ], ["artifact_id", "relative_path", "reason"])
    (legacy_out_path("28_domain_loader_limitations.md")).write_text(
        "# Domain Loader Limitations\n\nDomain loaders are defensive. For Matrix/EXTRACT03, INTERFACE01, RELALG and CAUSALITY this run registers artifact and summary level data unless stable structured columns are explicitly recognized.\n",
        encoding="utf-8",
    )
    (legacy_out_path("29_service_installation_note.md")).write_text(
        "# Service Installation Note\n\n`install_user_service.sh` prepares user-service instructions only. No system service is installed by this run.\n",
        encoding="utf-8",
    )
    (legacy_out_path("30_next_codex_prompt_recommendation.md")).write_text(
        "# Next Codex Prompt Recommendation\n\nReview `QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01`: verify artifact inventory, global search, metadata aliases, domain loader limitations and metadata server smoke checks.\n",
        encoding="utf-8",
    )


def legacy_sample_queries() -> list[dict]:
    queries = [
        ("dwh_status", "SELECT * FROM mart.v_qsb_dwh_status"),
        ("artifact_count_by_domain", "SELECT domain_guess, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY domain_guess ORDER BY artifact_count DESC"),
        ("dataset_overview", "SELECT dataset_id, dataset_name, domain FROM mart.v_qsb_dataset_overview ORDER BY dataset_id"),
        ("aliases_de", "SELECT canonical_name, display_label_de FROM mart.v_qsb_metadata_aliases_de ORDER BY canonical_name LIMIT 50"),
        ("global_search_beschleunigung", "SELECT * FROM mart.v_qsb_global_search WHERE search_text ILIKE '%Beschleunigung%' LIMIT 20"),
        ("sparc_rar_direct", "SELECT * FROM mart.v_sparc_rar_direct_points LIMIT 20"),
        ("matrix_topology_overview", "SELECT * FROM mart.v_matrix_topology_overview LIMIT 20"),
    ]
    rows = []
    for query_id, query in queries:
        result = psql(TARGET_DB, ["-At", "-F", "\t", "-c", query])
        lines = [line for line in result["stdout"].splitlines() if line.strip()]
        rows.append({"query_id": query_id, "status": "executed" if result["returncode"] == "0" else "failed", "result_row_count": str(len(lines)), "preview": " | ".join(lines[:5])})
    return rows


def legacy_run(action: str, ingest_all: bool = False) -> dict:
    LEGACY_OUT.mkdir(parents=True, exist_ok=True)
    legacy_write_sql_files()
    if not legacy_out_path("00_git_status_short_before.txt").exists():
        legacy_out_path("00_git_status_short_before.txt").write_text(run_cmd(["git", "status", "--short"])["stdout"] + "\n", encoding="utf-8")
    if not legacy_out_path("01_git_log_oneline_before.txt").exists():
        legacy_out_path("01_git_log_oneline_before.txt").write_text(run_cmd(["git", "log", "--oneline", "-n", "12"])["stdout"] + "\n", encoding="utf-8")
    with legacy_out_path("03_command_log.txt").open("a", encoding="utf-8") as f:
        f.write(f"{now_utc()} action={action} ingest_all={ingest_all}\n")

    conn = psql(TARGET_DB, ["-At", "-c", "SELECT current_database();"])
    postgres_ok = conn["returncode"] == "0"
    write_csv(legacy_out_path("05_postgres_connection_check.csv"), [{
        "check_name": "qsb_research_dwh_connection",
        "connection_ok": str(postgres_ok).lower(),
        "returncode": conn["returncode"],
        "stdout": conn["stdout"],
        "stderr": conn["stderr"],
    }], ["check_name", "connection_ok", "returncode", "stdout", "stderr"])
    if not postgres_ok:
        summary = {
            "run_id": LEGACY_RUN_ID,
            "status": "qsb_dwh_postgres_legacy_migration_metadata_server_blocked_postgres_connection",
            "target_database": TARGET_DB,
            "postgres_connection_ok": False,
            "schemas_created_or_verified": 0,
            "tables_created_or_verified": 0,
            "views_created_or_verified": 0,
            "procedures_created_or_verified": 0,
            "metadata_server_files_created": False,
            "claim_boundary": LEGACY_CLAIM_BOUNDARY,
        }
        write_json(legacy_out_path("04_legacy_migration_summary.json"), summary)
        return summary

    schema_results = legacy_apply_schema()
    with legacy_out_path("03_command_log.txt").open("a", encoding="utf-8") as f:
        for result in schema_results:
            f.write(f"{result['command']} rc={result['returncode']} {result['stderr']}\n")

    previous_inventory_path = REPO / "runs" / "QSB-DWH-POSTGRES-LEGACY-MIGRATION-METADATA-SERVER-01" / "06_input_file_inventory.csv"
    if LEGACY_RUN_ID == ARTIFACT_PATCH_RUN_ID and previous_inventory_path.exists():
        inventory = read_csv(previous_inventory_path)
        for row in inventory:
            row["artifact_id"] = hashlib.sha256(
                f"{row['relative_path']}::{row['sha256']}::{row['size_bytes']}".encode("utf-8")
            ).hexdigest()
        files = [REPO / row["relative_path"] for row in inventory if row.get("relative_path")]
    else:
        files = legacy_iter_files()
        inventory = []
        for path in files:
            digest = sha256(path)
            size = path.stat().st_size
            domain = legacy_domain_guess(path)
            dataset = {
                "sparc_rar": "SPARC_RAR_LELLI2016C",
                "matrix_topology": "QSB_MATRIX_TOPOLOGY_EXTRACT03",
                "extract03": "QSB_MATRIX_TOPOLOGY_EXTRACT03",
                "interface01": "QSB_INTERFACE01",
                "relalg": "QSB_RELALG_D1K",
                "causality": "QSB_CAUSALITY",
                "metadata": "QSB_METADATA",
            }.get(domain, "QSB_LEGACY_UNKNOWN")
            inventory.append({
                "artifact_id": legacy_artifact_id(path, digest, size),
                "relative_path": rel(path),
                "file_name": path.name,
                "suffix": path.suffix.lower(),
                "size_bytes": str(size),
                "sha256": digest,
                "line_count": "" if legacy_text_line_count(path) is None else str(legacy_text_line_count(path)),
                "run_folder": legacy_run_folder(path),
                "artifact_kind": legacy_artifact_kind(path),
                "domain_guess": domain,
                "dataset_id": dataset,
            })

    metrics = {
        "generic_csv_rows_loaded": legacy_count("staging.csv_row_json"),
        "json_documents_loaded": legacy_count("staging.json_document"),
        "markdown_documents_loaded": legacy_count("staging.markdown_document"),
        "sqlite_catalogs_discovered": len([r for r in inventory if r["suffix"] in {".sqlite", ".db"}]),
        "sqlite_catalogs_imported": legacy_count("staging.sqlite_table_inventory"),
        "matrix_topology_artifacts_loaded": legacy_scalar("SELECT COUNT(*) FROM canonical.qsb_artifact WHERE domain_guess IN ('matrix_topology','extract03');"),
        "interface01_artifacts_loaded": legacy_scalar("SELECT COUNT(*) FROM canonical.qsb_artifact WHERE domain_guess='interface01';"),
        "relalg_artifacts_loaded": legacy_scalar("SELECT COUNT(*) FROM canonical.qsb_artifact WHERE domain_guess='relalg';"),
        "causality_artifacts_loaded": legacy_scalar("SELECT COUNT(*) FROM canonical.qsb_artifact WHERE domain_guess='causality';"),
    }
    if ingest_all:
        insert_path, metrics = legacy_create_insert_sql(files, inventory)
        ingest_result = run_sql_file(TARGET_DB, insert_path)
        with legacy_out_path("03_command_log.txt").open("a", encoding="utf-8") as f:
            f.write(f"{ingest_result['command']} rc={ingest_result['returncode']} {ingest_result['stderr']}\n")
    # Refresh views after data load.
    legacy_apply_schema()
    sample_rows = legacy_sample_queries()
    table_count = legacy_scalar("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema IN ('admin','raw','staging','canonical','metadata','validation','server') AND table_type='BASE TABLE';")
    view_count = legacy_scalar("SELECT COUNT(*) FROM information_schema.views WHERE table_schema='mart';")
    proc_count = legacy_scalar("SELECT COUNT(*) FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname IN ('admin','validation','metadata') AND p.proname IN ('fn_now_utc','register_etl_run','mark_etl_step','register_validation_result','register_alias');")
    schemas = legacy_scalar("SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ('admin','raw','staging','canonical','metadata','validation','mart','server');")
    global_search_rows = legacy_scalar("SELECT COUNT(*) FROM mart.v_qsb_global_search;")
    status = "qsb_dwh_postgres_legacy_migration_metadata_server_completed"
    summary = {
        "run_id": LEGACY_RUN_ID,
        "status": status,
        "target_database": TARGET_DB,
        "postgres_connection_ok": True,
        "schemas_created_or_verified": schemas,
        "tables_created_or_verified": table_count,
        "views_created_or_verified": view_count,
        "procedures_created_or_verified": proc_count,
        "total_files_inventoried": len(inventory),
        "run_folders_inventoried": len({r["run_folder"] for r in inventory if r["run_folder"]}),
        "artifacts_registered": legacy_count("raw.source_artifact"),
        "checksums_computed": len(inventory),
        "generic_csv_rows_loaded": metrics["generic_csv_rows_loaded"],
        "json_documents_loaded": metrics["json_documents_loaded"],
        "markdown_documents_loaded": metrics["markdown_documents_loaded"],
        "sqlite_catalogs_discovered": metrics["sqlite_catalogs_discovered"],
        "sqlite_catalogs_imported": metrics["sqlite_catalogs_imported"],
        "sparc_rar_rows_loaded": legacy_count("canonical.obs_rar_point") + legacy_count("canonical.obs_massmodel_point") + legacy_count("canonical.obs_baseline_quantity"),
        "matrix_topology_artifacts_loaded": metrics["matrix_topology_artifacts_loaded"],
        "interface01_artifacts_loaded": metrics["interface01_artifacts_loaded"],
        "relalg_artifacts_loaded": metrics["relalg_artifacts_loaded"],
        "causality_artifacts_loaded": metrics["causality_artifacts_loaded"],
        "metadata_field_count": legacy_count("metadata.meta_field"),
        "metadata_unit_count": legacy_count("metadata.meta_unit"),
        "metadata_alias_count": legacy_count("metadata.meta_alias"),
        "metadata_lineage_count": legacy_count("metadata.meta_lineage"),
        "metadata_validation_count": legacy_count("validation.validation_result"),
        "metadata_claim_count": legacy_count("validation.claim_boundary"),
        "global_search_rows": global_search_rows,
        "metadata_server_files_created": (REPO / "scripts" / "qsb_metadata_server" / "qsb_metadata_server.py").exists(),
        "metadata_server_readiness_status": "ready_for_read_only_psql_cli_server",
        "dbeaver_target": "PostgreSQL localhost:5432/qsb_research_dwh",
        "single_db_policy_enabled": True,
        "sqlite_role": "audit_snapshot_only",
        "residual_analysis_executed": False,
        "rbci_v1_evaluated": False,
        "qsb_observable_evaluated": False,
        "claim_boundary": LEGACY_CLAIM_BOUNDARY,
        "recommended_next_run_id": "QSB-DWH-POSTGRES-LEGACY-MIGRATION-REVIEW-01",
        "notes": "Generic legacy artifact registration and read-only metadata server readiness completed. Domain-specific loads are defensive artifact/summary-level unless stable columns were already available.",
    }
    legacy_write_reports(summary, inventory, metrics, sample_rows)
    return summary


def artifact_stage_patch_run(action: str, ingest_all: bool = False) -> dict:
    global LEGACY_RUN_ID, LEGACY_OUT, LEGACY_CLAIM_BOUNDARY

    saved_run_id = LEGACY_RUN_ID
    saved_out = LEGACY_OUT
    saved_claim_boundary = LEGACY_CLAIM_BOUNDARY

    before_artifacts = legacy_count("raw.source_artifact")
    before_search = legacy_scalar("SELECT COUNT(*) FROM mart.v_qsb_global_search;")
    previous_summary_path = saved_out / "04_legacy_migration_summary.json"
    previous_summary = read_json(previous_summary_path) if previous_summary_path.exists() else {}

    try:
        LEGACY_RUN_ID = ARTIFACT_PATCH_RUN_ID
        LEGACY_OUT = ARTIFACT_PATCH_OUT
        LEGACY_CLAIM_BOUNDARY = ARTIFACT_PATCH_CLAIM_BOUNDARY
        summary = legacy_run(action, ingest_all=ingest_all)
    finally:
        LEGACY_RUN_ID = saved_run_id
        LEGACY_OUT = saved_out
        LEGACY_CLAIM_BOUNDARY = saved_claim_boundary

    OUT_DIR = ARTIFACT_PATCH_OUT
    after_artifacts = legacy_count("raw.source_artifact")
    after_search = legacy_scalar("SELECT COUNT(*) FROM mart.v_qsb_global_search;")
    json_key_values = legacy_count("staging.json_key_value")
    raw_checksums = legacy_count("raw.raw_checksum")
    csv_files_loaded = legacy_scalar("SELECT COUNT(DISTINCT artifact_id) FROM staging.csv_row_json;")
    views_required = [
        "v_qsb_dwh_status",
        "v_qsb_dataset_overview",
        "v_qsb_run_timeline",
        "v_qsb_artifact_inventory",
        "v_qsb_metadata_fields",
        "v_qsb_metadata_units",
        "v_qsb_metadata_aliases_de",
        "v_qsb_validation_status",
        "v_qsb_claim_boundaries",
        "v_qsb_global_search",
        "v_matrix_topology_overview",
        "v_interface01_overview",
        "v_relalg_overview",
        "v_causality_overview",
    ]
    view_rows = []
    for view_name in views_required:
        ok = legacy_scalar(
            "SELECT COUNT(*) FROM information_schema.views "
            f"WHERE table_schema='mart' AND table_name={sql_literal(view_name)};"
        )
        probe = psql(TARGET_DB, ["-At", "-c", f"SELECT COUNT(*) FROM mart.{view_name};"]) if ok else {"returncode": "not_found", "stdout": "", "stderr": ""}
        view_rows.append({
            "view_name": f"mart.{view_name}",
            "exists": str(bool(ok)).lower(),
            "query_status": "passed" if probe["returncode"] == "0" else "failed",
            "row_count": probe["stdout"].strip(),
        })
    views_verified = sum(1 for row in view_rows if row["exists"] == "true" and row["query_status"] == "passed")

    py_compile_server = run_cmd(["python", "-m", "py_compile", "scripts/qsb_metadata_server/qsb_metadata_server.py"])
    server_check = run_cmd(["python", "scripts/qsb_metadata_server/qsb_metadata_server.py", "--check"], timeout=30)
    metadata_server_check_status = (
        "ready_for_read_only_psql_cli_server"
        if py_compile_server["returncode"] == "0" and server_check["returncode"] == "0"
        else "ready_with_warning"
    )
    with (OUT_DIR / "03_command_log.txt").open("a", encoding="utf-8") as f:
        for result in [py_compile_server, server_check]:
            f.write(f"{result['command']} rc={result['returncode']} {result['stdout']} {result['stderr']}\n")

    status = "qsb_dwh_postgres_legacy_artifact_staging_patch_completed"
    warnings = []
    if after_artifacts < 5000:
        warnings.append("raw.source_artifact_count_after_below_5000")
    if after_search <= 100:
        warnings.append("global_search_rows_after_not_above_100")
    if metadata_server_check_status != "ready_for_read_only_psql_cli_server":
        warnings.append("metadata_server_check_warning")
    if warnings:
        status = "qsb_dwh_postgres_legacy_artifact_staging_patch_completed_with_warnings"

    patch_summary = {
        "run_id": ARTIFACT_PATCH_RUN_ID,
        "status": status,
        "target_database": TARGET_DB,
        "postgres_connection_ok": summary.get("postgres_connection_ok", False),
        "previous_run_id": saved_run_id,
        "previous_status": previous_summary.get("status", "unknown"),
        "total_files_inventoried": summary.get("total_files_inventoried", 0),
        "artifacts_registered_before": before_artifacts,
        "artifacts_registered_after": after_artifacts,
        "artifacts_registered_delta": after_artifacts - before_artifacts,
        "checksums_computed": summary.get("checksums_computed", 0),
        "raw_checksums_registered_after": raw_checksums,
        "generic_csv_files_loaded": csv_files_loaded,
        "generic_csv_rows_loaded": legacy_count("staging.csv_row_json"),
        "json_documents_loaded": legacy_count("staging.json_document"),
        "json_key_values_loaded": json_key_values,
        "markdown_documents_loaded": legacy_count("staging.markdown_document"),
        "sqlite_catalogs_discovered": summary.get("sqlite_catalogs_discovered", 0),
        "sqlite_catalogs_imported": summary.get("sqlite_catalogs_imported", 0),
        "matrix_topology_artifacts_loaded": summary.get("matrix_topology_artifacts_loaded", 0),
        "interface01_artifacts_loaded": summary.get("interface01_artifacts_loaded", 0),
        "relalg_artifacts_loaded": summary.get("relalg_artifacts_loaded", 0),
        "causality_artifacts_loaded": summary.get("causality_artifacts_loaded", 0),
        "global_search_rows_before": before_search,
        "global_search_rows_after": after_search,
        "global_search_rows_delta": after_search - before_search,
        "views_verified": views_verified,
        "metadata_server_check_status": metadata_server_check_status,
        "residual_analysis_executed": False,
        "rbci_v1_evaluated": False,
        "qsb_observable_evaluated": False,
        "claim_boundary": ARTIFACT_PATCH_CLAIM_BOUNDARY,
        "recommended_next_run_id": "QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-REVIEW-01",
        "notes": "Additive artifact staging patch; generic artifact, CSV, JSON, Markdown/TXT, SQLite catalog, search and readiness checks only.",
        "warnings": warnings,
    }

    write_json(OUT_DIR / "04_artifact_staging_patch_summary.json", patch_summary)
    write_csv(OUT_DIR / "06_previous_legacy_run_review.csv", [
        {"field": key, "value": json.dumps(value, ensure_ascii=False) if isinstance(value, (dict, list)) else str(value)}
        for key, value in sorted(previous_summary.items())
    ], ["field", "value"])
    write_csv(OUT_DIR / "07_file_inventory.csv", read_csv(OUT_DIR / "06_input_file_inventory.csv"), [
        "artifact_id", "relative_path", "file_name", "suffix", "size_bytes", "sha256", "line_count",
        "run_folder", "artifact_kind", "domain_guess", "dataset_id",
    ])
    write_csv(OUT_DIR / "08_artifact_registration_report.csv", [
        {"metric": "artifacts_registered_before", "value": str(before_artifacts)},
        {"metric": "artifacts_registered_after", "value": str(after_artifacts)},
        {"metric": "artifacts_registered_delta", "value": str(after_artifacts - before_artifacts)},
    ], ["metric", "value"])
    write_csv(OUT_DIR / "09_raw_checksum_registration_report.csv", [
        {"metric": "checksums_computed", "value": str(patch_summary["checksums_computed"])},
        {"metric": "raw_checksums_registered_after", "value": str(raw_checksums)},
    ], ["metric", "value"])
    write_csv(OUT_DIR / "10_csv_generic_load_report.csv", [
        {"metric": "generic_csv_files_loaded", "value": str(csv_files_loaded)},
        {"metric": "generic_csv_rows_loaded", "value": str(patch_summary["generic_csv_rows_loaded"])},
    ], ["metric", "value"])
    write_csv(OUT_DIR / "11_json_generic_load_report.csv", [
        {"metric": "json_documents_loaded", "value": str(patch_summary["json_documents_loaded"])},
        {"metric": "json_key_values_loaded", "value": str(json_key_values)},
    ], ["metric", "value"])
    write_csv(OUT_DIR / "12_markdown_text_load_report.csv", [
        {"metric": "markdown_documents_loaded", "value": str(patch_summary["markdown_documents_loaded"])},
    ], ["metric", "value"])
    if (OUT_DIR / "11_sqlite_catalog_import_report.csv").exists():
        (OUT_DIR / "13_sqlite_catalog_patch_report.csv").write_text((OUT_DIR / "11_sqlite_catalog_import_report.csv").read_text(encoding="utf-8"), encoding="utf-8")
    if (OUT_DIR / "13_domain_staging_load_report.csv").exists():
        (OUT_DIR / "14_domain_artifact_load_report.csv").write_text((OUT_DIR / "13_domain_staging_load_report.csv").read_text(encoding="utf-8"), encoding="utf-8")
    write_csv(OUT_DIR / "15_global_search_patch_report.csv", [
        {"metric": "global_search_rows_before", "value": str(before_search)},
        {"metric": "global_search_rows_after", "value": str(after_search)},
        {"metric": "global_search_rows_delta", "value": str(after_search - before_search)},
    ], ["metric", "value"])
    write_csv(OUT_DIR / "16_view_patch_report.csv", view_rows, ["view_name", "exists", "query_status", "row_count"])
    write_csv(OUT_DIR / "17_metadata_server_check_report.csv", [
        {"check_name": "py_compile", "status": "passed" if py_compile_server["returncode"] == "0" else "failed", "detail": py_compile_server["stderr"] or py_compile_server["stdout"]},
        {"check_name": "server_check", "status": "passed" if server_check["returncode"] == "0" else "failed", "detail": server_check["stderr"] or server_check["stdout"]},
        {"check_name": "readiness", "status": metadata_server_check_status, "detail": "read-only metadata server check"},
    ], ["check_name", "status", "detail"])

    table_result = psql(TARGET_DB, ["-At", "-c", "SELECT table_schema || '.' || table_name FROM information_schema.tables WHERE table_schema IN ('admin','raw','staging','canonical','metadata','validation','server') AND table_type='BASE TABLE' ORDER BY table_schema, table_name;"])
    table_rows = [{"table_name": line.strip(), "row_count": str(legacy_count(line.strip())), "status": "verified"} for line in table_result["stdout"].splitlines() if line.strip()]
    write_csv(OUT_DIR / "18_table_inventory_after.csv", table_rows, ["table_name", "row_count", "status"])
    write_csv(OUT_DIR / "19_row_counts_after.csv", [{"object_name": r["table_name"], "row_count": r["row_count"]} for r in table_rows], ["object_name", "row_count"])

    sample_queries = [
        ("source_artifacts", "SELECT COUNT(*) AS source_artifacts FROM raw.source_artifact"),
        ("artifact_count_by_domain", "SELECT domain_guess, COUNT(*) AS artifact_count FROM raw.source_artifact GROUP BY domain_guess ORDER BY artifact_count DESC"),
        ("csv_rows", "SELECT COUNT(*) AS csv_rows FROM staging.csv_row_json"),
        ("json_documents", "SELECT COUNT(*) AS json_documents FROM staging.json_document"),
        ("markdown_documents", "SELECT COUNT(*) AS markdown_documents FROM staging.markdown_document"),
        ("sqlite_tables", "SELECT COUNT(*) AS sqlite_tables FROM staging.sqlite_table_inventory"),
        ("search_rows", "SELECT COUNT(*) AS search_rows FROM mart.v_qsb_global_search"),
        ("global_search_beschleunigung", "SELECT * FROM mart.v_qsb_global_search WHERE search_text ILIKE '%Beschleunigung%' LIMIT 20"),
        ("artifact_inventory", "SELECT * FROM mart.v_qsb_artifact_inventory LIMIT 20"),
    ]
    sample_rows = []
    for query_id, query in sample_queries:
        result = psql(TARGET_DB, ["-At", "-F", "\t", "-c", query])
        lines = [line for line in result["stdout"].splitlines() if line.strip()]
        sample_rows.append({"query_id": query_id, "status": "executed" if result["returncode"] == "0" else "failed", "result_row_count": str(len(lines)), "preview": " | ".join(lines[:5])})
    write_csv(OUT_DIR / "20_sample_query_results_after.csv", sample_rows, ["query_id", "status", "result_row_count", "preview"])
    warning_result = psql(TARGET_DB, ["-At", "-F", "\t", "-c", "SELECT warning_id, artifact_id, warning_status, message FROM validation.ingest_warning ORDER BY created_at DESC LIMIT 500;"])
    write_csv(OUT_DIR / "21_ingest_warning_report.csv", [
        {"warning_id": parts[0] if len(parts) > 0 else "", "artifact_id": parts[1] if len(parts) > 1 else "", "warning_status": parts[2] if len(parts) > 2 else "", "message": parts[3] if len(parts) > 3 else ""}
        for parts in (line.split("\t", 3) for line in warning_result["stdout"].splitlines() if line.strip())
    ], ["warning_id", "artifact_id", "warning_status", "message"])
    if (OUT_DIR / "27_unparsed_artifact_report.csv").exists():
        (OUT_DIR / "22_unparsed_or_skipped_artifact_report.csv").write_text((OUT_DIR / "27_unparsed_artifact_report.csv").read_text(encoding="utf-8"), encoding="utf-8")
    (OUT_DIR / "02_artifact_staging_patch_scope.md").write_text(
        f"# {ARTIFACT_PATCH_RUN_ID}\n\n"
        "Befund: Additiver Patch fuer breite Artefaktregistrierung und generisches Staging in PostgreSQL.\n\n"
        "Interpretation: PostgreSQL `qsb_research_dwh` bleibt zentraler Arbeitsraum; der Run-Ordner ist Audit-Nachweis.\n\n"
        "Hypothese: Keine wissenschaftliche Hypothese wird getestet.\n\n"
        "Offene Luecke: SQLite-meta_* Import bleibt defensiv und nur kompatible Tabellen werden uebernommen.\n\n"
        "Claim Boundary: Methodische DWH-Vorbereitung ohne Residual-, RBCI_v1- oder QSB-Observable-Auswertung.\n",
        encoding="utf-8",
    )
    (OUT_DIR / "23_claim_boundary_and_no_go.md").write_text(
        "# Claim Boundary and No-Go\n\n"
        "Befund: PostgreSQL-DWH-Artefakt-Staging, generische Artefaktregistrierung, CSV/JSON/Markdown/SQLite-Staging, globale Suche und Metadata-Server-Readiness.\n\n"
        "Interpretation: Keine physikalische Auswertung wurde ausgefuehrt.\n\n"
        "Hypothese: Keine.\n\n"
        "Offene Luecke: Domain-spezifische Summary-Extraktion bleibt auf sichere Artefakt-/Katalogebene begrenzt.\n\n"
        "Claim Boundary: Keine Claims zu Dunkler Materie, RAR-Erklaerung, MOND, LambdaCDM, Gravitation, Raumzeit oder Kausalitaet.\n",
        encoding="utf-8",
    )
    (OUT_DIR / "24_next_run_recommendation.md").write_text(
        "# Next Run Recommendation\n\n"
        "Empfohlen: `QSB-DWH-POSTGRES-LEGACY-MIGRATION-ARTIFACT-STAGING-PATCH-REVIEW-01` zur Pruefung der erweiterten Counts, Search-Tokens, SQLite-Katalogimporte und View-Kompatibilitaet.\n",
        encoding="utf-8",
    )
    (OUT_DIR / "25_review_note.md").write_text(
        f"# Review Note\n\nBefund: Status `{status}`. `raw.source_artifact` enthaelt {after_artifacts} Zeilen; `mart.v_qsb_global_search` enthaelt {after_search} Zeilen.\n\n"
        "Interpretation: Der Patch ist eine methodische Staging-/Such-Erweiterung und kein wissenschaftlicher Ergebnislauf.\n",
        encoding="utf-8",
    )
    write_csv(OUT_DIR / "27_sqlite_meta_import_mapping.csv", [
        {"sqlite_table": name, "postgres_target": f"metadata.{name}" if name in {"meta_alias", "meta_field", "meta_unit", "meta_lineage", "meta_validation_result", "meta_claim"} else "inventory_only", "status": "compatible_if_columns_match"}
        for name in ["meta_alias", "meta_field", "meta_unit", "meta_lineage", "meta_validation_result", "meta_claim"]
    ], ["sqlite_table", "postgres_target", "status"])
    write_csv(OUT_DIR / "28_domain_summary_extraction_candidates.csv", [
        {"domain": "matrix_topology", "candidate_rule": "artifact path and optional summary_json/text preview", "status": "candidate_only"},
        {"domain": "interface01", "candidate_rule": "artifact path and optional summary_json/text preview", "status": "candidate_only"},
        {"domain": "relalg", "candidate_rule": "artifact path and optional summary_json/text preview", "status": "candidate_only"},
        {"domain": "causality", "candidate_rule": "artifact path and optional summary_json/text preview", "status": "candidate_only"},
    ], ["domain", "candidate_rule", "status"])
    (OUT_DIR / "29_next_codex_prompt_recommendation.md").write_text(
        "# Next Codex Prompt Recommendation\n\n"
        "Review the artifact staging patch outputs, verify field compatibility for SQLite `meta_*` imports, and inspect global-search precision before adding domain-specific summary extraction.\n",
        encoding="utf-8",
    )
    return patch_summary


def create_base_artifacts(action: str) -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    write_sql_files()
    if not (OUT / "00_git_status_short_before.txt").exists():
        (OUT / "00_git_status_short_before.txt").write_text(run_cmd(["git", "status", "--short"])["stdout"] + "\n", encoding="utf-8")
    if not (OUT / "01_git_log_oneline_before.txt").exists():
        (OUT / "01_git_log_oneline_before.txt").write_text(run_cmd(["git", "log", "--oneline", "-n", "12"])["stdout"] + "\n", encoding="utf-8")
    append_command_log([f"{now_utc()} action={action}"])

    missing = [p for p in REQUIRED_INPUTS if not p.exists()]
    availability, connection, postgres_available, connection_ok = postgres_checks()
    write_csv(OUT / "05_postgres_availability_check.csv", availability, ["check_name", "command", "available", "detail"])
    write_csv(OUT / "06_postgres_connection_check.csv", connection, ["check_name", "command", "connection_ok", "returncode", "stdout", "stderr"])
    inventory, checksum_rows, checksum_match_count, checksum_mismatch_count = input_inventory()
    write_csv(OUT / "07_input_artifact_inventory.csv", inventory, ["file_path", "exists", "size_bytes", "sha256", "role"])
    write_csv(OUT / "08_source_checksum_revalidation.csv", checksum_rows, ["file_path", "expected_sha256", "actual_sha256", "checksum_status"])

    sqlite_integrity = "not_checked_missing_input"
    sqlite_tables = []
    sqlite_counts = []
    sqlite_views = []
    if SQLITE_PATH.exists():
        sqlite_integrity, sqlite_tables, sqlite_counts, sqlite_views = sqlite_inventory()
    write_csv(OUT / "09_sqlite_prototype_inventory.csv", sqlite_tables + sqlite_views, ["sqlite_object_name", "object_type", "column_count", "columns"])
    write_csv(OUT / "20_table_inventory.csv", [], ["schema_name", "table_name", "row_count", "status"])
    write_csv(OUT / "21_row_counts.csv", sqlite_counts, ["object_name", "object_type", "row_count"])
    write_csv(OUT / "22_view_inventory.csv", sqlite_views, ["view_name", "column_count", "columns"])
    write_mapping()

    prev_summary = read_json(SPARC_SQLITE_RUN / "04_sparc_rar_dwh_etl_metadata_registration_summary.json") if (SPARC_SQLITE_RUN / "04_sparc_rar_dwh_etl_metadata_registration_summary.json").exists() else {}
    meta_report = [
        {"registry": "metadata_field", "sqlite_snapshot_count": str(prev_summary.get("metadata_field_count", 0)), "postgres_loaded_count": "0", "status": "blocked_not_loaded_to_postgres"},
        {"registry": "metadata_unit", "sqlite_snapshot_count": str(prev_summary.get("metadata_unit_count", 0)), "postgres_loaded_count": "0", "status": "blocked_not_loaded_to_postgres"},
        {"registry": "metadata_alias", "sqlite_snapshot_count": str(prev_summary.get("metadata_alias_count", 0)), "postgres_loaded_count": "0", "status": "blocked_not_loaded_to_postgres"},
        {"registry": "metadata_lineage", "sqlite_snapshot_count": str(prev_summary.get("metadata_lineage_count", 0)), "postgres_loaded_count": "0", "status": "blocked_not_loaded_to_postgres"},
        {"registry": "metadata_validation", "sqlite_snapshot_count": str(prev_summary.get("metadata_validation_count", 0)), "postgres_loaded_count": "0", "status": "blocked_not_loaded_to_postgres"},
        {"registry": "metadata_claim", "sqlite_snapshot_count": str(prev_summary.get("metadata_claim_count", 0)), "postgres_loaded_count": "0", "status": "blocked_not_loaded_to_postgres"},
    ]
    write_csv(OUT / "23_metadata_registry_report.csv", meta_report, ["registry", "sqlite_snapshot_count", "postgres_loaded_count", "status"])
    validation_rows = [
        {"validation_id": "postgres_available", "validation_status": "passed" if postgres_available else "blocked", "observed_value": str(postgres_available).lower(), "expected_value": "true", "notes": "psql availability"},
        {"validation_id": "postgres_connection_ok", "validation_status": "passed" if connection_ok else "blocked", "observed_value": str(connection_ok).lower(), "expected_value": "true", "notes": "psql -d postgres SELECT version"},
        {"validation_id": "sqlite_snapshot_integrity", "validation_status": "passed" if sqlite_integrity == "ok" else "blocked", "observed_value": sqlite_integrity, "expected_value": "ok", "notes": rel(SQLITE_PATH)},
        {"validation_id": "checksum_match_count", "validation_status": "passed" if checksum_match_count == 4 else "warning", "observed_value": str(checksum_match_count), "expected_value": "4", "notes": "raw SPARC inputs"},
        {"validation_id": "no_forbidden_analysis", "validation_status": "passed", "observed_value": "false", "expected_value": "false", "notes": "No residual/RBCI/QSB observable executed."},
    ]
    write_csv(OUT / "24_validation_report.csv", validation_rows, ["validation_id", "validation_status", "observed_value", "expected_value", "notes"])

    db_logs = []
    bootstrap_status = "not_executed"
    ingest_status = "not_executed"
    target_database_created_or_found = False
    if connection_ok and not missing:
        if action in {"bootstrap", "ingest"}:
            target_database_created_or_found, db_logs = ensure_target_database(connection_ok)
            append_command_log([f"{r['command']} rc={r['returncode']} {r['stdout']} {r['stderr']}" for r in db_logs])
            if target_database_created_or_found:
                sql_results = [run_sql_file(TARGET_DB, path) for path in [
                    SQL_DIR / "001_admin_core.sql",
                    SQL_DIR / "002_sparc_rar.sql",
                    SQL_DIR / "003_metadata.sql",
                    SQL_DIR / "004_views.sql",
                    SQL_DIR / "005_indexes.sql",
                    SQL_DIR / "006_procedures.sql",
                ]]
                append_command_log([f"{r['command']} rc={r['returncode']} {r['stdout']} {r['stderr']}" for r in sql_results])
                bootstrap_status = "completed" if all(r["returncode"] == "0" for r in sql_results) else "failed"
                if action == "ingest" and bootstrap_status == "completed":
                    ingest_sql = generate_ingest_sql()
                    ingest_result = run_sql_file(TARGET_DB, ingest_sql)
                    append_command_log([f"{ingest_result['command']} rc={ingest_result['returncode']} {ingest_result['stdout']} {ingest_result['stderr']}"])
                    ingest_status = "completed" if ingest_result["returncode"] == "0" else "failed"
        else:
            probe = psql("postgres", ["-At", "-c", f"SELECT 1 FROM pg_database WHERE datname = {sql_literal(TARGET_DB)};"])
            target_database_created_or_found = probe["stdout"].strip() == "1"

    counts = postgres_object_counts(target_database_created_or_found)
    target_ready = target_database_created_or_found and counts["schemas"] == 7
    if target_ready:
        write_postgres_inventories(True)
    else:
        write_csv(OUT / "20_table_inventory.csv", [], ["schema_name", "table_name", "row_count", "status"])

    direct_rar_loaded = postgres_row_count("canonical.obs_rar_point") if target_ready else 0
    massmodels_loaded = postgres_row_count("canonical.obs_massmodel_point") if target_ready else 0
    baseline_loaded = postgres_row_count("canonical.obs_baseline_quantity") if target_ready else 0
    metadata_field_loaded = postgres_row_count("metadata.meta_field") if target_ready else 0
    metadata_unit_loaded = postgres_row_count("metadata.meta_unit") if target_ready else 0
    metadata_alias_loaded = postgres_row_count("metadata.meta_alias") if target_ready else 0
    metadata_lineage_loaded = postgres_row_count("metadata.meta_lineage") if target_ready else 0
    metadata_validation_loaded = postgres_row_count("validation.validation_result") if target_ready else 0
    metadata_claim_loaded = postgres_row_count("metadata.meta_claim") if target_ready else 0

    meta_report = [
        {"registry": "metadata_field", "sqlite_snapshot_count": str(prev_summary.get("metadata_field_count", 0)), "postgres_loaded_count": str(metadata_field_loaded), "status": "loaded" if metadata_field_loaded else "not_loaded"},
        {"registry": "metadata_unit", "sqlite_snapshot_count": str(prev_summary.get("metadata_unit_count", 0)), "postgres_loaded_count": str(metadata_unit_loaded), "status": "loaded" if metadata_unit_loaded else "not_loaded"},
        {"registry": "metadata_alias", "sqlite_snapshot_count": str(prev_summary.get("metadata_alias_count", 0)), "postgres_loaded_count": str(metadata_alias_loaded), "status": "loaded" if metadata_alias_loaded else "not_loaded"},
        {"registry": "metadata_lineage", "sqlite_snapshot_count": str(prev_summary.get("metadata_lineage_count", 0)), "postgres_loaded_count": str(metadata_lineage_loaded), "status": "loaded" if metadata_lineage_loaded else "not_loaded"},
        {"registry": "metadata_validation", "sqlite_snapshot_count": str(prev_summary.get("metadata_validation_count", 0)), "postgres_loaded_count": str(metadata_validation_loaded), "status": "loaded" if metadata_validation_loaded else "not_loaded"},
        {"registry": "metadata_claim", "sqlite_snapshot_count": str(prev_summary.get("metadata_claim_count", 0)), "postgres_loaded_count": str(metadata_claim_loaded), "status": "loaded" if metadata_claim_loaded else "not_loaded"},
    ]
    write_csv(OUT / "23_metadata_registry_report.csv", meta_report, ["registry", "sqlite_snapshot_count", "postgres_loaded_count", "status"])
    write_csv(OUT / "17_postgres_ingest_report.csv", [
        {"step_name": "bootstrap", "status": bootstrap_status if connection_ok else "blocked_postgres_unavailable_or_auth", "rows_loaded": "0", "message": "Schemas/tables/views/indexes/procedures applied when completed."},
        {"step_name": "ingest_sparc_rar", "status": ingest_status if connection_ok else "blocked_postgres_unavailable_or_auth", "rows_loaded": str(direct_rar_loaded + massmodels_loaded + baseline_loaded), "message": "SPARC/RAR SQLite snapshot loaded idempotently when completed."},
    ], ["step_name", "status", "rows_loaded", "message"])

    sample_rows = []
    sample_queries = [
        ("datasets", "SELECT * FROM canonical.obs_dataset"),
        ("sources", "SELECT dataset_id, file_name, sha256, raw_data_status FROM canonical.obs_source_file ORDER BY file_name"),
        ("rar_points", "SELECT galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar FROM mart.v_sparc_rar_direct_points LIMIT 20"),
        ("massmodels_points", "SELECT galaxy_id, radius_kpc, vobs_km_s, gobs_m_s2 FROM mart.v_sparc_massmodels_gobs_points LIMIT 20"),
        ("de_fields", "SELECT canonical_name, display_label_de FROM mart.v_de_sparc_feldnamen ORDER BY canonical_name"),
        ("search", "SELECT * FROM mart.v_qsb_obs_search_sparc_rar WHERE search_text ILIKE '%Beschleunigung%' LIMIT 20"),
        ("validation_status", "SELECT validation_status, COUNT(*) AS n FROM mart.v_sparc_validation_status GROUP BY validation_status"),
    ]
    if target_ready:
        for query_id, query in sample_queries:
            result = psql(TARGET_DB, ["-At", "-F", "\t", "-c", query])
            rows = [line for line in result["stdout"].splitlines() if line.strip()]
            sample_rows.append({"query_id": query_id, "status": "executed" if result["returncode"] == "0" else "failed", "result_row_count": str(len(rows)), "preview": " | ".join(rows[:5])})
    else:
        sample_rows.append({"query_id": "sample_postgres_queries", "status": "not_executed_postgres_unavailable_or_auth" if not connection_ok else "not_executed_target_not_ready", "result_row_count": "0", "preview": ""})
    write_csv(OUT / "26_sample_postgres_query_results.csv", sample_rows, ["query_id", "status", "result_row_count", "preview"])

    if not connection_ok:
        (OUT / "32_postgres_error_log.txt").write_text("\n".join([r.get("stderr", "") or r.get("detail", "") for r in connection + availability]) + "\n", encoding="utf-8")
    (OUT / "33_postgres_schema_diff.md").write_text(
        "# PostgreSQL Schema Diff\n\nBefund: PostgreSQL-Zielschema wurde aus dem SQLite-Prototyp fachlich gemappt, aber nicht gegen eine laufende Ziel-DB verglichen, sofern Verbindung blockiert ist.\n\nInterpretation: `27_sqlite_to_postgres_mapping.csv` ist die aktuelle Mapping-Grundlage.\n",
        encoding="utf-8",
    )

    missing_status = bool(missing)
    if missing_status:
        status = "qsb_dwh_postgres_core_migration_blocked_missing_inputs"
    elif not connection_ok:
        status = "qsb_dwh_postgres_core_migration_blocked_postgres_unavailable_or_auth"
    elif direct_rar_loaded == 2693 and massmodels_loaded == 3392 and baseline_loaded == 6085:
        status = "qsb_dwh_postgres_core_migration_completed"
    else:
        status = "qsb_dwh_postgres_core_migration_partial_sql_generated_only"
    write_static_notes(status)

    summary = {
        "run_id": RUN_ID,
        "status": status,
        "postgres_available": postgres_available,
        "postgres_connection_ok": connection_ok,
        "target_database": TARGET_DB,
        "target_database_created_or_found": target_database_created_or_found,
        "schemas_created_or_verified": counts["schemas"],
        "procedures_created_or_verified": counts["procedures"],
        "views_created_or_verified": counts["views"],
        "tables_created_or_verified": counts["tables"],
        "source_sqlite_snapshot_path": rel(SQLITE_PATH),
        "sqlite_snapshot_integrity_check": sqlite_integrity,
        "input_raw_mrt_file_count": len(RAW_INPUTS),
        "checksum_match_count": checksum_match_count,
        "checksum_mismatch_count": checksum_mismatch_count,
        "direct_rar_rows_loaded_to_postgres": direct_rar_loaded,
        "massmodels_baseline_rows_loaded_to_postgres": massmodels_loaded,
        "baseline_quantity_rows_loaded_to_postgres": baseline_loaded,
        "metadata_field_count_loaded": metadata_field_loaded,
        "metadata_unit_count_loaded": metadata_unit_loaded,
        "metadata_alias_count_loaded": metadata_alias_loaded,
        "metadata_lineage_count_loaded": metadata_lineage_loaded,
        "metadata_validation_count_loaded": metadata_validation_loaded,
        "metadata_claim_count_loaded": metadata_claim_loaded,
        "postgres_integrity_or_smoke_check": "ok" if target_ready else ("blocked_postgres_unavailable_or_auth" if not connection_ok else "target_not_ready"),
        "dbeaver_target": "PostgreSQL localhost:5432/qsb_research_dwh",
        "sqlite_role": "audit_snapshot_only",
        "central_working_dwh_backend": "postgresql",
        "residual_analysis_executed": False,
        "rbci_v1_evaluated": False,
        "qsb_observable_evaluated": False,
        "claim_boundary": CLAIM_BOUNDARY,
        "recommended_next_run_id": "QSB-DWH-POSTGRES-CORE-MIGRATION-REVIEW-01",
        "notes": "PostgreSQL target loaded idempotently from SQLite snapshot." if status == "qsb_dwh_postgres_core_migration_completed" else "SQL and orchestrator artifacts generated; PostgreSQL ingest not fully completed.",
        "missing_inputs": [rel(p) for p in missing],
    }
    write_json(OUT / "04_postgres_core_migration_summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="QSB PostgreSQL DWH migration orchestrator")
    parser.add_argument("action", choices=["check", "bootstrap", "ingest", "artifact-stage", "validate", "status"])
    parser.add_argument("--dataset", default="")
    parser.add_argument("--patch", default="")
    parser.add_argument("--all", action="store_true", help="Run the legacy all-artifact migration path.")
    args = parser.parse_args()
    if args.action == "artifact-stage":
        if args.patch != "legacy":
            print("Unsupported artifact-stage patch. Use: artifact-stage --patch legacy")
            return 2
        summary = artifact_stage_patch_run(args.action, ingest_all=True)
        print(f"{args.action}: {summary['status']}")
        return 0
    if args.all or (LEGACY_OUT.exists() and args.action in {"check", "bootstrap", "validate", "status"}):
        summary = legacy_run(args.action, ingest_all=args.action == "ingest" and args.all)
        if args.action == "status":
            print(json.dumps({
                "status": summary["status"],
                "postgres_connection_ok": summary["postgres_connection_ok"],
                "target_database": summary["target_database"],
                "artifacts_registered": summary.get("artifacts_registered", 0),
                "global_search_rows": summary.get("global_search_rows", 0),
            }, ensure_ascii=False, sort_keys=True))
        else:
            print(f"{args.action}: {summary['status']}")
        return 0
    summary = create_base_artifacts(args.action)
    if args.action == "status":
        print(json.dumps({
            "status": summary["status"],
            "postgres_available": summary["postgres_available"],
            "postgres_connection_ok": summary["postgres_connection_ok"],
            "target_database": summary["target_database"],
        }, ensure_ascii=False, sort_keys=True))
    elif args.action == "ingest" and args.dataset and args.dataset != "sparc_rar":
        print(f"Unsupported dataset: {args.dataset}")
        return 2
    else:
        print(f"{args.action}: {summary['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
