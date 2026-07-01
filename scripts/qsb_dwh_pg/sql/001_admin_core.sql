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
