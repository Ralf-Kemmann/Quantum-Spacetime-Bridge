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
