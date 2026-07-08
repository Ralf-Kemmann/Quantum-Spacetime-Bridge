CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_summary (
  run_id text,
  run_type text,
  execution_status text,
  final_admissibility_status text,
  claim_status text,
  physical_claim_release text,
  input_scout_run_id text,
  input_design_run_id text,
  input_scout_decision text,
  candidate_count_total text,
  candidate_count_admissible_for_testing text,
  candidate_count_lineage_repair text,
  candidate_count_metadata_repair text,
  candidate_count_rejected_alias_lag text,
  candidate_count_rejected_alias_pair_or_index text,
  candidate_count_rejected_not_pair_mappable text,
  candidate_count_rejected_not_independent text,
  candidate_count_red_team_review text,
  candidate_count_unknown_or_blocked text,
  lineage_commit_status text,
  pre_existing_modified_files_detected text,
  next_gate text,
  secondary_next_gate text,
  no_lag_mechanism_tests_executed text,
  no_nullmodels_executed text,
  git_head text,
  created_at_utc text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_input_lineage (
  run_id text,
  input_run_id text,
  input_kind text,
  input_status text,
  input_decision text,
  lineage_commit_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_results (
  run_id text,
  candidate_id text,
  source_type text,
  source_path_or_table text,
  candidate_variable_name text,
  candidate_category text,
  artifact_level text,
  alias_risk_level text,
  input_independence_status text,
  criteria_pass_count text,
  criteria_fail_count text,
  criteria_unknown_count text,
  critical_failures text,
  admissibility_decision_class text,
  allowed_next_use text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_criteria_results (
  run_id text,
  candidate_id text,
  criterion_name text,
  criterion_status text,
  criterion_evidence text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_alias_flags (
  run_id text,
  candidate_id text,
  alias_flag text,
  alias_flag_status text,
  alias_evidence text,
  alias_risk_level text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_deterministic_alias_check (
  run_id text,
  candidate_id text,
  value_series_status text,
  deterministic_alias_check_status text,
  r2_lag text,
  r2_abs_lag text,
  lookup_accuracy_pair_id text,
  lookup_accuracy_index_order text,
  residual_entropy text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_scramble_feasibility (
  run_id text,
  candidate_id text,
  scramble_test_feasible text,
  required_source_values_present text,
  required_mapping_present text,
  expected_blocker text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_source_lineage_audit (
  run_id text,
  candidate_id text,
  source_artifact_present text,
  generation_rule_present text,
  transformation_chain_complete text,
  derived_from_lag_flag text,
  derived_from_pair_id_flag text,
  derived_from_index_flag text,
  lineage_score text,
  lineage_decision text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_pair_mapping_audit (
  run_id text,
  candidate_id text,
  pair_mapping_status text,
  pair_mapping_coverage_status text,
  directed_pair_support text,
  mapping_uses_lag_as_value_source text,
  mapping_uses_pair_id_as_value_source text,
  mapping_decision text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_information_gain_feasibility (
  run_id text,
  candidate_id text,
  information_gain_test_feasible text,
  candidate_values_available text,
  lag_values_available text,
  minimum_data_requirements_met text,
  information_gain_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_directionality_audit (
  run_id text,
  candidate_id text,
  directionality_documented text,
  directionality_class text,
  ij_reversal_behavior_available text,
  absolute_value_risk text,
  directionality_decision text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_unit_dimension_audit (
  run_id text,
  candidate_id text,
  unit_present text,
  dimension_vector_present text,
  dimensionless_reason_present text,
  metadata_decision text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_decision_summary (
  run_id text,
  admissibility_decision_class text,
  candidate_count text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_category_summary (
  run_id text,
  category text,
  count_total text,
  count_admissible_for_testing text,
  count_rejected text,
  count_repair_required text,
  count_red_team_review text,
  dominant_blocker text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_rejected_summary (
  run_id text,
  candidate_id text,
  source_type text,
  source_path_or_table text,
  candidate_variable_name text,
  candidate_category text,
  artifact_level text,
  alias_risk_level text,
  input_independence_status text,
  criteria_pass_count text,
  criteria_fail_count text,
  criteria_unknown_count text,
  critical_failures text,
  admissibility_decision_class text,
  allowed_next_use text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_repair_required_summary (
  run_id text,
  candidate_id text,
  source_type text,
  source_path_or_table text,
  candidate_variable_name text,
  candidate_category text,
  artifact_level text,
  alias_risk_level text,
  input_independence_status text,
  criteria_pass_count text,
  criteria_fail_count text,
  criteria_unknown_count text,
  critical_failures text,
  admissibility_decision_class text,
  allowed_next_use text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_red_team_summary (
  run_id text,
  candidate_id text,
  source_type text,
  source_path_or_table text,
  candidate_variable_name text,
  candidate_category text,
  artifact_level text,
  alias_risk_level text,
  input_independence_status text,
  criteria_pass_count text,
  criteria_fail_count text,
  criteria_unknown_count text,
  critical_failures text,
  admissibility_decision_class text,
  allowed_next_use text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_claim_boundaries (
  run_id text,
  claim_key text,
  claim_text text,
  status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_next_gate (
  run_id text,
  next_gate text,
  secondary_next_gate text,
  execution_authorization text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_validation (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_unabhaengige_lag_variable_zulassung_de;
CREATE VIEW qsb_planck_bridge.v_pbr_unabhaengige_lag_variable_zulassung_de AS
SELECT
  r.run_id AS "Lauf-ID",
  r.candidate_id AS "Kandidaten-ID",
  r.candidate_variable_name AS "Kandidatenvariable",
  r.candidate_category AS "Kandidatenkategorie",
  r.source_path_or_table AS "Quelle",
  r.alias_risk_level AS "Alias-Risiko",
  r.input_independence_status AS "Unabhängigkeitsstatus",
  r.criteria_pass_count AS "Kriterien bestanden",
  r.criteria_fail_count AS "Kriterien gescheitert",
  r.critical_failures AS "kritische Fehler",
  r.admissibility_decision_class AS "Zulassungsentscheidung",
  r.allowed_next_use AS "erlaubte nächste Verwendung",
  r.claim_implication AS "Claim-Folge",
  r.physical_claim_release AS "physikalische Claim-Freigabe",
  s.next_gate AS "nächster Gate"
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_results r
JOIN qsb_planck_bridge.pbr_independent_lag_variable_admissibility_summary s ON s.run_id = r.run_id
WHERE r.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01';
