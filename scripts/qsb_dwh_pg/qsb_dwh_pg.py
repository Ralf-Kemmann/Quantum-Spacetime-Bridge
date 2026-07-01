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
TARGET_DB = "qsb_research_dwh"
DATASET_ID = "SPARC_RAR_LELLI2016C"
REPO = Path(__file__).resolve().parents[2]
SCRIPT_DIR = REPO / "scripts" / "qsb_dwh_pg"
SQL_DIR = SCRIPT_DIR / "sql"
OUT = REPO / "runs" / RUN_ID
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
    parser.add_argument("action", choices=["check", "bootstrap", "ingest", "validate", "status"])
    parser.add_argument("--dataset", default="")
    args = parser.parse_args()
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
