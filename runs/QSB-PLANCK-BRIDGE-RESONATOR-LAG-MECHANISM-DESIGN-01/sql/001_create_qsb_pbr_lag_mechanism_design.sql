CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_design_summary (
  run_id text,
  source_run_id text,
  design_status text,
  execution_status text,
  claim_status text,
  physical_claim_release text,
  input_specificity_classification text,
  input_critical_nullmodel text,
  input_critical_reproduction_rate double precision,
  next_gate text,
  secondary_next_gate text,
  created_at_utc text,
  git_commit text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_test_family_spec (
  test_id text,
  test_key text,
  deutscher_testname text,
  purpose_de text,
  core_question_de text,
  preserved_quantities text,
  perturbed_quantities text,
  required_input_artifacts text,
  required_metrics text,
  expected_diagnostics text,
  admissibility_criteria text,
  decision_rule text,
  failure_modes text,
  claim_implication_if_pass text,
  claim_implication_if_fail text,
  execution_authorization_status text,
  next_gate_implication text,
  run_id text,
  source_run_id text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_decision_cases (
  run_id text,
  case_id text,
  lag_structure_status text,
  meaning_de text,
  allowed_conclusion_de text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_required_inputs (
  run_id text,
  test_key text,
  required_input_artifacts text,
  input_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_required_metrics (
  run_id text,
  test_key text,
  required_metrics text,
  metric_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_claim_boundaries (
  run_id text,
  claim_key text,
  claim_text text,
  status text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_next_gate_decision (
  run_id text,
  next_gate text,
  secondary_next_gate text,
  execution_authorization text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_failure_modes (
  run_id text,
  test_key text,
  failure_modes text,
  mitigation_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_validation_results (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_lag_mechanismus_design_de;
CREATE VIEW qsb_planck_bridge.v_pbr_lag_mechanismus_design_de AS
SELECT
  run_id AS "Lauf-ID",
  source_run_id AS "Quell-Lauf-ID",
  test_id AS "Test-ID",
  test_key AS "Test-Schlüssel",
  deutscher_testname AS "deutscher Testname",
  purpose_de AS "Zweck",
  core_question_de AS "Kernfrage",
  preserved_quantities AS "erhaltene Größen",
  perturbed_quantities AS "gestörte Größen",
  required_input_artifacts AS "erforderliche Eingangsartefakte",
  required_metrics AS "erforderliche Metriken",
  expected_diagnostics AS "erwartete Diagnostik",
  admissibility_criteria AS "Zulässigkeitskriterien",
  decision_rule AS "Entscheidungsregel",
  failure_modes AS "Fehlermodi",
  claim_implication_if_pass AS "Claim-Folge bei Bestehen",
  claim_implication_if_fail AS "Claim-Folge bei Scheitern",
  execution_authorization_status AS "Ausführungsfreigabe",
  next_gate_implication AS "nächster Gate"
FROM qsb_planck_bridge.pbr_lag_mechanism_test_family_spec
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
