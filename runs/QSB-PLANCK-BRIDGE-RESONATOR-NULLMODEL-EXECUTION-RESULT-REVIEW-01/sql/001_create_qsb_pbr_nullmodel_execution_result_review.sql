CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_summary (
  run_id text,
  input_run_id text,
  review_status text,
  review_outcome text,
  formal_finding_status text,
  specificity_status text,
  critical_nullmodel text,
  critical_nullmodel_reproduction text,
  claim_status text,
  physical_claim_release text,
  external_readiness text,
  next_gate text,
  secondary_next_gate text,
  review_timestamp_utc text,
  git_commit text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_family (
  run_id text,
  input_run_id text,
  nullmodel_family text,
  samples_total integer,
  complete_reproduction_count integer,
  complete_reproduction_rate double precision,
  partial_reproduction_count integer,
  rank6_preservation_count integer,
  review_interpretation text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_critical_findings (
  run_id text,
  critical_nullmodel text,
  complete_reproduction_count integer,
  samples_total integer,
  complete_reproduction_rate double precision,
  interpretation text,
  claim_implication text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_specificity (
  run_id text,
  input_run_id text,
  specificity_classification text,
  specificity_de_label text,
  specificity_reason text,
  formal_claim_status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_claim_boundaries (
  run_id text,
  claim_key text,
  status text,
  claim_text text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_next_gate (
  run_id text,
  next_gate text,
  secondary_next_gate text,
  execution_authorization text,
  gate_meaning text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_lineage (
  run_id text,
  source_run_id text,
  source_path text,
  source_exists text,
  source_role text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_result_review_validation (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_nullmodell_result_review_de;
CREATE VIEW qsb_planck_bridge.v_pbr_nullmodell_result_review_de AS
SELECT
  s.run_id AS "Lauf-ID",
  s.review_outcome AS "Review-Ergebnis",
  s.specificity_status AS "Spezifitätsstatus",
  c.critical_nullmodel AS "kritisches Nullmodell",
  c.complete_reproduction_rate AS "Reproduktionsrate",
  s.physical_claim_release AS "physikalische Claim-Freigabe",
  n.next_gate AS "nächster Gate",
  n.secondary_next_gate AS "sekundärer Gate"
FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_summary s
JOIN qsb_planck_bridge.pbr_nullmodel_execution_result_review_critical_findings c ON c.run_id = s.run_id
JOIN qsb_planck_bridge.pbr_nullmodel_execution_result_review_next_gate n ON n.run_id = s.run_id
WHERE s.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
