CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_scout_summary (
  run_id text,
  run_type text,
  execution_status text,
  claim_status text,
  physical_claim_release text,
  input_gate text,
  source_final_decision_class text,
  scout_decision text,
  next_gate text,
  repo_scout_status text,
  dwh_scout_status text,
  candidate_count text,
  repo_artifact_match_count text,
  dwh_artifact_match_count text,
  pre_existing_modified_review_run text,
  git_head text,
  created_at_utc text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_repo_inventory (
  run_id text,
  source_path text,
  matched_terms text,
  artifact_kind text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_dwh_inventory (
  run_id text,
  object_type text,
  table_schema text,
  table_name text,
  column_name text,
  matched_reason text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_candidate_variables (
  run_id text,
  candidate_id text,
  source_type text,
  source_path_or_table text,
  candidate_variable_name text,
  candidate_category text,
  artifact_level text,
  pair_mappable text,
  has_i_j_or_pair_id text,
  has_lag text,
  has_units text,
  has_dimension_metadata text,
  has_source_lineage text,
  upstream_generation_stage text,
  derived_from_index_order text,
  derived_from_lag_or_abs_lag text,
  derived_from_pair_id text,
  non_alias_evidence text,
  alias_risk_level text,
  independence_status text,
  review_need text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_lineage_assessment (
  run_id text,
  candidate_id text,
  source_path_or_table text,
  has_source_lineage text,
  lineage_assessment text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_alias_risk (
  run_id text,
  candidate_id text,
  candidate_variable_name text,
  alias_reference text,
  alias_risk_level text,
  independence_status text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_physical_proxy_sources (
  run_id text,
  proxy_family text,
  candidate_status text,
  source_path_or_table text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_pair_mapping_readiness (
  run_id text,
  candidate_id text,
  pair_mappable text,
  mapping_readiness text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_gap_update (
  run_id text,
  gap_key text,
  gap_status text,
  why_needed text,
  update_note text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_deep_research_handoff (
  run_id text,
  question_id text,
  handoff_question text,
  evidence_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_claim_boundaries (
  run_id text,
  claim_key text,
  claim_text text,
  status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_next_gate (
  run_id text,
  next_gate text,
  secondary_next_gate text,
  execution_authorization text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_input_artifact_enrichment_validation (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_input_artefakt_scout_de;
CREATE VIEW qsb_planck_bridge.v_pbr_input_artefakt_scout_de AS
SELECT
  run_id AS "Lauf-ID",
  run_type AS "Lauftyp",
  execution_status AS "Ausführungsstatus",
  scout_decision AS "Scout-Entscheidung",
  repo_scout_status AS "Repo-Scout-Status",
  dwh_scout_status AS "DWH-Scout-Status",
  candidate_count AS "Kandidatenanzahl",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate"
FROM qsb_planck_bridge.pbr_input_artifact_enrichment_scout_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
