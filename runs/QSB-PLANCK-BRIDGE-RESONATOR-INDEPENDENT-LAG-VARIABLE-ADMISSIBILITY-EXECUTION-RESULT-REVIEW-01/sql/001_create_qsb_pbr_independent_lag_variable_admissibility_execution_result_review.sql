CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_summary (
  run_id text,
  run_type text,
  source_run_id text,
  review_outcome text,
  confirmed_execution_status text,
  confirmed_final_admissibility_status text,
  candidate_count_total text,
  candidate_count_admissible_for_testing text,
  dominant_blocker text,
  dominant_blocker_count text,
  lineage_repair_candidate_count text,
  metadata_repair_candidate_count text,
  mechanism_testing_readiness text,
  claim_status text,
  physical_claim_release text,
  external_readiness text,
  next_gate text,
  secondary_next_gate text,
  tertiary_next_gate text,
  lineage_commit_status text,
  pre_existing_modified_files_detected text,
  git_head text,
  created_at_utc text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_lineage (
  run_id text,
  source_run_id text,
  source_status text,
  source_execution_status text,
  source_validation_pass_count text,
  source_validation_fail_count text,
  lineage_commit_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_results (
  run_id text,
  review_question text,
  review_answer text,
  interpretation_boundary text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_blockers (
  run_id text,
  blocker_key text,
  blocker_count text,
  blocker_role text,
  review_interpretation text,
  next_action text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_repair_candidates (
  run_id text,
  candidate_id text,
  candidate_variable_name text,
  repair_type text,
  source_type text,
  source_path_or_table text,
  current_decision_class text,
  repair_need text,
  minimum_repair_requirement text,
  allowed_next_use_after_repair text,
  claim_boundary text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_not_pair_mappable (
  run_id text,
  rejected_not_pair_mappable_count text,
  interpretation text,
  next_action text,
  claim_implication text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_claim_boundaries (
  run_id text,
  claim_key text,
  claim_text text,
  status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_deep_research_boundary (
  run_id text,
  deep_research_status text,
  deep_research_role text,
  deep_research_cannot_replace_internal_lineage text,
  deep_research_cannot_confirm_current_matrix_proxy text,
  allowed_use text,
  not_allowed_use text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_next_gate (
  run_id text,
  next_gate text,
  secondary_next_gate text,
  tertiary_next_gate text,
  physical_claim_release text,
  execution_authorization text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_recommended_work (
  run_id text,
  recommended_run_id text,
  priority text,
  rationale text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_validation (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_unabhaengige_lag_variable_zulassung_review_de;
CREATE VIEW qsb_planck_bridge.v_pbr_unabhaengige_lag_variable_zulassung_review_de AS
SELECT
  run_id AS "Lauf-ID",
  source_run_id AS "Quell-Lauf-ID",
  review_outcome AS "Review-Ergebnis",
  candidate_count_total AS "Kandidaten gesamt",
  candidate_count_admissible_for_testing AS "sofort zugelassen",
  dominant_blocker AS "dominanter Blocker",
  dominant_blocker_count AS "Blocker-Anzahl",
  lineage_repair_candidate_count AS "Lineage-Reparaturkandidaten",
  metadata_repair_candidate_count AS "Metadaten-Reparaturkandidaten",
  mechanism_testing_readiness AS "Mechanismus-Testbereitschaft",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate",
  secondary_next_gate AS "sekundärer Gate",
  tertiary_next_gate AS "tertiärer Gate"
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
