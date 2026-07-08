CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_execution_summary (
  run_id text,
  source_run_id text,
  execution_status text,
  claim_status text,
  physical_claim_release text,
  input_specificity_classification text,
  input_critical_nullmodel text,
  input_critical_reproduction_rate double precision,
  final_decision_class text,
  decision_rationale text,
  next_gate text,
  created_at_utc text,
  git_commit text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_test_results (
  run_id text,
  source_run_id text,
  test_id text,
  test_key text,
  deutscher_testname text,
  execution_status text,
  input_artifact text,
  seed integer,
  sample_count integer,
  rank6_preserved_rate double precision,
  lag_structure_preserved_rate double precision,
  order_dependence_score double precision,
  label_dependence_score double precision,
  shift_orbit_consistency text,
  shift_commutator_norm double precision,
  toeplitz_fit_score double precision,
  lag_explained_variance_ratio double precision,
  independent_variable_available boolean,
  independent_variable_name text,
  lag_reconstruction_accuracy double precision,
  physical_proxy_available boolean,
  physical_proxy_name text,
  proxy_lag_correlation double precision,
  nullmodel_appropriateness_class text,
  decision_signal text,
  decision_class text,
  specificity_relation text,
  claim_implication text,
  physical_claim_release text,
  next_gate text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_index_relabeling (
  run_id text,
  sample_id text,
  seed integer,
  structure_preserved_under_relabeling boolean,
  label_permutation text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_order_scrambling (
  run_id text,
  sample_id text,
  seed integer,
  scrambled_order text,
  rank6_preserved text,
  lag_structure_preserved text,
  collapse_score double precision,
  lag_structure_distance text,
  antiparallelity_preserved text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_independent_lag_variable (
  run_id text,
  test_key text,
  execution_status text,
  independent_variable_available boolean,
  independent_variable_name text,
  lag_reconstruction_accuracy double precision,
  lag_proxy_correlation double precision,
  lag_proxy_rank_correlation double precision,
  lag_proxy_mutual_information_or_group_score double precision,
  decision_signal text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_shift_operator (
  run_id text,
  test_key text,
  execution_status text,
  shift_operator_constructed text,
  shift_orbit_consistency text,
  shift_commutator_norm double precision,
  shift_class_reproduction_score double precision,
  translation_invariance_score double precision,
  decision_signal text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_toeplitz_dependency (
  run_id text,
  test_key text,
  execution_status text,
  toeplitz_fit_score double precision,
  within_lag_variance_mean double precision,
  between_lag_variance double precision,
  lag_explained_variance_ratio double precision,
  toeplitz_residual_norm double precision,
  scrambled_toeplitz_fit_score_mean double precision,
  decision_signal text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_physical_proxy (
  run_id text,
  test_key text,
  execution_status text,
  physical_proxy_available boolean,
  physical_proxy_name text,
  physical_proxy_source_artifact text,
  proxy_lag_correlation double precision,
  proxy_lag_monotonicity_score double precision,
  proxy_group_reproduction_rate double precision,
  proxy_independence_assessment text,
  proxy_status text,
  claim_implication text,
  decision_signal text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_nullmodel_operationalization (
  run_id text,
  test_key text,
  execution_status text,
  lag_preserving_nullmodel_role text,
  overpreservation_risk text,
  hypothesis_preservation_score double precision,
  nullmodel_appropriateness_class text,
  review_conclusion text,
  decision_signal text,
  critical_reproduction_rate double precision
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_decision (
  run_id text,
  final_decision_class text,
  decision_rationale text,
  order_dependence_score double precision,
  toeplitz_fit_score double precision,
  shift_class_reproduction_score double precision,
  independent_variable_available boolean,
  physical_proxy_available boolean,
  claim_status text,
  physical_claim_release text,
  next_gate text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_claim_boundaries (
  run_id text,
  claim_key text,
  status text,
  claim_text text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_lineage (
  run_id text,
  source_run_id text,
  source_path text,
  source_role text,
  sha256 text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_lag_mechanism_validation_results (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_lag_mechanismus_ergebnis_de;
CREATE VIEW qsb_planck_bridge.v_pbr_lag_mechanismus_ergebnis_de AS
SELECT
  run_id AS "Lauf-ID",
  source_run_id AS "Quell-Lauf-ID",
  test_id AS "Test-ID",
  test_key AS "Test-Schlüssel",
  deutscher_testname AS "deutscher Testname",
  execution_status AS "Ausführungsstatus",
  input_artifact AS "Eingangsartefakt",
  seed AS "Zufalls-Seed",
  sample_count AS "Anzahl Proben",
  rank6_preserved_rate AS "Rang-6-Erhaltungsrate",
  lag_structure_preserved_rate AS "Lag-Struktur-Erhaltungsrate",
  order_dependence_score AS "Ordnungsabhängigkeitswert",
  label_dependence_score AS "Label-Abhängigkeitswert",
  shift_orbit_consistency AS "Shift-Orbit-Konsistenz",
  shift_commutator_norm AS "Shift-Kommutatornorm",
  toeplitz_fit_score AS "Toeplitz-Anpassungswert",
  lag_explained_variance_ratio AS "Lag-erklärte Varianz",
  independent_variable_available AS "unabhängige Lag-Variable verfügbar",
  independent_variable_name AS "unabhängige Lag-Variable",
  lag_reconstruction_accuracy AS "Lag-Rekonstruktionsgenauigkeit",
  physical_proxy_available AS "physikalischer Proxy verfügbar",
  physical_proxy_name AS "physikalischer Proxy",
  proxy_lag_correlation AS "Proxy-Lag-Korrelation",
  nullmodel_appropriateness_class AS "Nullmodell-Angemessenheitsklasse",
  decision_signal AS "Entscheidungssignal",
  decision_class AS "Entscheidungsklasse",
  specificity_relation AS "Spezifitätsbezug",
  claim_implication AS "Claim-Folge",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate"
FROM qsb_planck_bridge.pbr_lag_mechanism_test_results
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
