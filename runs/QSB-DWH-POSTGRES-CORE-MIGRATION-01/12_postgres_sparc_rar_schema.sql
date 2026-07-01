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
