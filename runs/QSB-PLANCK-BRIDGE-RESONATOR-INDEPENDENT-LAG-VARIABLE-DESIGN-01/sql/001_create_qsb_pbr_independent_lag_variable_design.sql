CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_design_summary (
  run_id text,
  run_type text,
  design_status text,
  execution_status text,
  claim_status text,
  physical_claim_release text,
  input_scout_run_id text,
  input_scout_status text,
  input_scout_decision text,
  input_scout_candidate_count text,
  input_scout_repo_artifact_match_count text,
  input_scout_dwh_artifact_match_count text,
  lineage_commit_status text,
  pre_existing_modified_files_detected text,
  pre_existing_modified_files text,
  next_gate text,
  secondary_next_gate text,
  no_tests_executed text,
  no_nullmodels_executed text,
  git_head text,
  created_at_utc text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_input_scout_lineage (
  run_id text,
  input_scout_run_id text,
  input_file text,
  input_status text,
  input_scout_decision text,
  candidate_count text,
  alias_high_count text,
  proxy_family_count text,
  gap_count text,
  lineage_commit_status text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_independence_criteria (
  run_id text,
  criterion_key text,
  deutscher_name text,
  criterion_definition text,
  required_evidence text,
  design_status text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_alias_rules (
  run_id text,
  flag_key text,
  deutscher_name text,
  detection_rule text,
  required_evidence text,
  claim_implication text,
  recommended_action text,
  design_status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_classification_schema (
  run_id text,
  candidate_class text,
  class_definition text,
  allowed_status text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_test_design (
  run_id text,
  test_key text,
  purpose text,
  required_later_metrics text,
  execution_status text,
  design_status text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_decision_logic (
  run_id text,
  decision_class text,
  required_conditions text,
  blocking_conditions text,
  allowed_next_use text,
  claim_implication text,
  physical_claim_release text,
  design_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_source_lineage_requirements (
  run_id text,
  requirement_key text,
  requirement_text text,
  blocking_if_missing text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_pair_mapping_requirements (
  run_id text,
  requirement_key text,
  requirement_text text,
  blocking_if_missing text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_unit_dimension_requirements (
  run_id text,
  requirement_key text,
  requirement_text text,
  blocking_if_missing text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_phase_response_rule (
  run_id text,
  rule_key text,
  rule_text text,
  upstream_basis text,
  required_new_evidence text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_deep_research_handoff (
  run_id text,
  question_id text,
  handoff_question text,
  evidence_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_claim_boundaries (
  run_id text,
  claim_key text,
  claim_text text,
  status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_next_gate (
  run_id text,
  next_gate text,
  secondary_next_gate text,
  execution_authorization text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_validation (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_unabhaengige_lag_variable_design_de;
CREATE VIEW qsb_planck_bridge.v_pbr_unabhaengige_lag_variable_design_de AS
SELECT
  s.run_id AS "Lauf-ID",
  s.design_status AS "Designstatus",
  s.execution_status AS "Ausführungsstatus",
  s.input_scout_run_id AS "Quell-Scout",
  s.input_scout_decision AS "Scout-Entscheidung",
  c.criterion_key AS "Kriterium",
  c.deutscher_name AS "deutscher Kriterienname",
  a.flag_key AS "Alias-Regel",
  cl.candidate_class AS "Kandidatenklasse",
  t.test_key AS "Testdesign",
  d.decision_class AS "Entscheidungsklasse",
  d.claim_implication AS "Claim-Folge",
  s.physical_claim_release AS "physikalische Claim-Freigabe",
  s.next_gate AS "nächster Gate",
  s.secondary_next_gate AS "sekundärer Gate"
FROM qsb_planck_bridge.pbr_independent_lag_variable_design_summary s
LEFT JOIN qsb_planck_bridge.pbr_independent_lag_variable_independence_criteria c ON c.run_id = s.run_id
LEFT JOIN qsb_planck_bridge.pbr_independent_lag_variable_alias_rules a ON a.run_id = s.run_id
LEFT JOIN qsb_planck_bridge.pbr_independent_lag_variable_classification_schema cl ON cl.run_id = s.run_id
LEFT JOIN qsb_planck_bridge.pbr_independent_lag_variable_test_design t ON t.run_id = s.run_id
LEFT JOIN qsb_planck_bridge.pbr_independent_lag_variable_decision_logic d ON d.run_id = s.run_id
WHERE s.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
