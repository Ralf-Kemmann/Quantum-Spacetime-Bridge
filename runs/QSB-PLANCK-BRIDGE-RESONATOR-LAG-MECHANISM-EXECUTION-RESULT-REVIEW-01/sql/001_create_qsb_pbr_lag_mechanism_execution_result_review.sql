CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_summary (
  run_id text,
  source_run_id text,
  review_outcome text,
  formal_finding_status text,
  mechanism_status text,
  physical_proxy_status text,
  pure_index_status text,
  claim_status text,
  physical_claim_release text,
  external_readiness text,
  next_gate text,
  secondary_next_gate text,
  tertiary_next_gate text,
  review_timestamp_utc text,
  git_commit text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_test (
  run_id text,
  test_key text,
  source_execution_status text,
  review_status text,
  contribution_to_decision text,
  claim_implication text,
  next_input_need text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_blocked_test (
  run_id text,
  test_key text,
  blocked_reason text,
  claim_implication text,
  next_input_need text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_decision (
  run_id text,
  source_run_id text,
  source_final_decision_class text,
  review_confirmed_decision_class text,
  not_formal_lag_mechanism_candidate_reason text,
  not_physical_proxy_candidate_reason text,
  not_pure_index_construction_reason text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_input_gaps (
  run_id text,
  gap_key text,
  gap_status text,
  why_needed text,
  minimum_required_content text,
  claim_unlocked_if_resolved text,
  claim_still_blocked_after_resolution text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_claim_boundaries (
  run_id text,
  claim_key text,
  claim_text text,
  status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_next_gate (
  run_id text,
  next_gate text,
  secondary_next_gate text,
  tertiary_next_gate text,
  physical_claim_release text,
  execution_authorization text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_recommended_work (
  run_id text,
  recommended_run_id text,
  recommendation_rank text,
  purpose text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_lineage (
  run_id text,
  source_run_id text,
  source_path text,
  source_exists text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_validation (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_lag_mechanismus_execution_review_de;
CREATE VIEW qsb_planck_bridge.v_pbr_lag_mechanismus_execution_review_de AS
SELECT
  run_id AS "Lauf-ID",
  source_run_id AS "Quell-Lauf-ID",
  review_outcome AS "Review-Ergebnis",
  formal_finding_status AS "formaler Befundstatus",
  mechanism_status AS "Mechanismusstatus",
  physical_proxy_status AS "physikalischer Proxy-Status",
  pure_index_status AS "Pure-Index-Status",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate",
  secondary_next_gate AS "sekundärer Gate",
  tertiary_next_gate AS "tertiärer Gate"
FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';
