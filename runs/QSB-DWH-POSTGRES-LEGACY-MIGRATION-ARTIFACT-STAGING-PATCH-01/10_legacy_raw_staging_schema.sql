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
