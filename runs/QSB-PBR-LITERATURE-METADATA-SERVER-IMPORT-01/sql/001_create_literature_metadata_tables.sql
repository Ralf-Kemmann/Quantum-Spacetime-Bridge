-- QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01
-- Prepare-only DDL draft. Do not execute until a human selects the DB target.
-- Claim boundary: literature_context_only_no_internal_evidence_no_mechanism_claim

BEGIN;

CREATE TABLE IF NOT EXISTS qsb_literature_source (
  literature_id TEXT PRIMARY KEY,
  source_key TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  authors TEXT NOT NULL,
  year INTEGER,
  venue TEXT,
  doi TEXT,
  arxiv_id TEXT,
  source_url TEXT,
  source_type TEXT,
  source_class TEXT,
  author_cluster TEXT,
  theory_cluster TEXT,
  green_status TEXT,
  risk_status TEXT,
  verification_status TEXT,
  discovery_channel TEXT,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS qsb_literature_mechanism_tag (
  literature_id TEXT NOT NULL,
  mechanism_tag TEXT NOT NULL,
  tag_role TEXT,
  PRIMARY KEY (literature_id, mechanism_tag)
);

CREATE TABLE IF NOT EXISTS qsb_literature_claim_boundary (
  literature_id TEXT PRIMARY KEY,
  internal_evidence_flag INTEGER NOT NULL DEFAULT 0 CHECK (internal_evidence_flag = 0),
  mechanism_claim_support INTEGER NOT NULL DEFAULT 0 CHECK (mechanism_claim_support = 0),
  physical_claim_support INTEGER NOT NULL DEFAULT 0 CHECK (physical_claim_support = 0),
  allowed_use TEXT NOT NULL,
  forbidden_use TEXT NOT NULL,
  claim_boundary TEXT NOT NULL CHECK (claim_boundary = 'literature_context_only_no_internal_evidence_no_mechanism_claim')
);

CREATE TABLE IF NOT EXISTS qsb_literature_qsb_mapping (
  literature_id TEXT NOT NULL,
  qsb_structure_tag TEXT NOT NULL,
  mapping_kind TEXT,
  mapping_strength TEXT,
  mapping_notes TEXT,
  PRIMARY KEY (literature_id, qsb_structure_tag)
);

CREATE TABLE IF NOT EXISTS qsb_literature_import_manifest (
  import_id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL,
  source_report_path TEXT,
  source_report_sha256 TEXT,
  import_timestamp_utc TEXT,
  db_target TEXT,
  schema_action TEXT,
  row_count_sources INTEGER,
  row_count_tags INTEGER,
  row_count_claim_boundaries INTEGER,
  validation_status TEXT,
  claim_boundary TEXT
);

COMMIT;
