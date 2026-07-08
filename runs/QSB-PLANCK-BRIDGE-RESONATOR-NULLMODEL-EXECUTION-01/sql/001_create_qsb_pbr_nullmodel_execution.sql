CREATE SCHEMA IF NOT EXISTS qsb_planck_bridge;

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_summary (
  run_id text,
  source_run_id text,
  matrix_id text,
  matrix_source text,
  execution_status text,
  executed_at_utc text,
  samples_per_family integer,
  nullmodel_family_count integer,
  sample_total text,
  specificity_classification text,
  specificity_reason text,
  claim_status text,
  physical_claim_release text,
  next_gate text,
  git_commit text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_sample_results (
  run_id text,
  source_run_id text,
  matrix_id text,
  matrix_source text,
  nullmodel_family text,
  nullmodel_name text,
  sample_id integer,
  seed integer,
  samples_per_family integer,
  execution_status text,
  executed_at_utc text,
  code_version text,
  git_commit text,
  psd_pass boolean,
  lambda_min double precision,
  lambda_max double precision,
  eigenvalue_tolerance double precision,
  rank_tol_1e_10 integer,
  rank_tolerance double precision,
  nullity integer,
  trace double precision,
  eigenvalue_profile text,
  eigen_profile_distance double precision,
  spectral_gap_distance double precision,
  rank6_preserved boolean,
  psd_and_rank_preserved boolean,
  directed_pair_feature_count integer,
  lag_class_count integer,
  lag_class_structure_preserved boolean,
  lag_axis_collapse_score double precision,
  within_lag_similarity double precision,
  between_lag_separation double precision,
  directed_pair_consistency double precision,
  plus_minus_k_antiparallel_score double precision,
  antiparallelity_preserved boolean,
  lag_structure_distance double precision,
  lag_structure_reproduction_class text,
  complete_structure_reproduction boolean,
  partial_structure_reproduction boolean,
  parallel_count integer,
  antiparallel_count integer
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_family_summary (
  run_id text,
  nullmodel_family text,
  sample_count integer,
  complete_reproduction_count integer,
  partial_reproduction_count integer,
  null_reproduction_rate double precision,
  rank6_rate text,
  psd_and_rank_rate text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_spectral_core_metrics (
  run_id text,
  source_run_id text,
  matrix_id text,
  matrix_source text,
  nullmodel_family text,
  nullmodel_name text,
  sample_id integer,
  seed integer,
  samples_per_family integer,
  execution_status text,
  executed_at_utc text,
  code_version text,
  git_commit text,
  psd_pass boolean,
  lambda_min double precision,
  lambda_max double precision,
  eigenvalue_tolerance double precision,
  rank_tol_1e_10 integer,
  rank_tolerance double precision,
  nullity integer,
  trace double precision,
  eigenvalue_profile text,
  eigen_profile_distance double precision,
  spectral_gap_distance double precision,
  rank6_preserved boolean,
  psd_and_rank_preserved boolean
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_lag_class_metrics (
  run_id text,
  source_run_id text,
  matrix_id text,
  matrix_source text,
  nullmodel_family text,
  nullmodel_name text,
  sample_id integer,
  seed integer,
  samples_per_family integer,
  execution_status text,
  executed_at_utc text,
  code_version text,
  git_commit text,
  directed_pair_feature_count integer,
  lag_class_count integer,
  lag_class_structure_preserved boolean,
  lag_axis_collapse_score double precision,
  within_lag_similarity double precision,
  between_lag_separation double precision,
  directed_pair_consistency double precision,
  plus_minus_k_antiparallel_score double precision,
  antiparallelity_preserved boolean,
  lag_structure_distance double precision,
  lag_structure_reproduction_class text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_comparison_metrics (
  run_id text,
  nullmodel_family text,
  observed_value text,
  null_mean double precision,
  null_std double precision,
  null_min double precision,
  null_max double precision,
  rank_z_score double precision,
  eigen_profile_z_score double precision,
  lag_structure_z_score double precision,
  empirical_p_value double precision,
  null_reproduction_rate double precision,
  complete_structure_reproduction boolean,
  partial_structure_reproduction boolean,
  critical_nullmodel_reproduction boolean
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_specificity_classification (
  run_id text,
  specificity_classification text,
  specificity_label_de text,
  specificity_reason text,
  critical_nullmodel text,
  strengthening_nullmodel text,
  formal_claim_status text,
  physical_claim_release text,
  next_gate text,
  external_readiness text,
  reviewer_risk text,
  red_team_status text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_claim_boundaries (
  run_id text,
  boundary_id text,
  claim_key text,
  status text,
  claim_text text,
  physical_claim_release text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_lineage (
  run_id text,
  source_run_id text,
  input_id text,
  source_path text,
  sha256 text,
  lineage_bundle_sha256 text
);

CREATE TABLE IF NOT EXISTS qsb_planck_bridge.pbr_nullmodel_execution_validation_results (
  run_id text,
  check_name text,
  status text,
  detail text
);

DROP VIEW IF EXISTS qsb_planck_bridge.v_pbr_nullmodell_ergebnis_de;
CREATE VIEW qsb_planck_bridge.v_pbr_nullmodell_ergebnis_de AS
SELECT
  s.run_id AS "Lauf-ID",
  s.source_run_id AS "Quell-Lauf-ID",
  s.matrix_id AS "Matrix-ID",
  s.matrix_source AS "Matrix-Herkunft",
  s.nullmodel_family AS "Nullmodell-Familie",
  s.nullmodel_name AS "Nullmodell-Name",
  s.sample_id AS "Nullmodell-Probe-ID",
  s.seed AS "Zufalls-Seed",
  s.samples_per_family AS "Anzahl-Proben",
  s.execution_status AS "Ausführungsstatus",
  s.executed_at_utc AS "Ausführungszeitpunkt",
  s.code_version AS "Code-Version",
  s.git_commit AS "Git-Commit",
  s.psd_pass AS "PSD-bestanden",
  s.lambda_min AS "kleinster Eigenwert",
  s.lambda_max AS "größter Eigenwert",
  s.eigenvalue_tolerance AS "Eigenwert-Toleranz",
  s.rank_tol_1e_10 AS "Rang",
  s.rank_tolerance AS "Rang-Toleranz",
  s.nullity AS "Nullität",
  s.trace AS "Spur",
  s.eigen_profile_distance AS "Eigenprofil-Abstand",
  s.spectral_gap_distance AS "Spektrallücken-Abstand",
  s.rank6_preserved AS "Rang-6-erhalten",
  s.psd_and_rank_preserved AS "PSD-und-Rang-erhalten",
  s.directed_pair_feature_count AS "Anzahl gerichteter Paarfeatures",
  s.lag_class_count AS "Anzahl Lag-Klassen",
  s.lag_class_structure_preserved AS "Lag-Klassen-Struktur erhalten",
  s.lag_axis_collapse_score AS "Lag-Achsen-Kollapswert",
  s.within_lag_similarity AS "Innerhalb-Lag-Ähnlichkeit",
  s.between_lag_separation AS "Zwischen-Lag-Trennung",
  s.directed_pair_consistency AS "Gerichtete-Paar-Konsistenz",
  s.plus_minus_k_antiparallel_score AS "Plus-Minus-k-Antiparallelitätswert",
  s.antiparallelity_preserved AS "Antiparallelität erhalten",
  s.lag_structure_distance AS "Lag-Struktur-Abstand",
  s.lag_structure_reproduction_class AS "Lag-Struktur-Reproduktion",
  s.complete_structure_reproduction AS "vollständige Strukturreproduktion",
  s.partial_structure_reproduction AS "teilweise Strukturreproduktion",
  c.specificity_classification AS "Spezifitätsstufe",
  c.specificity_reason AS "Spezifitätsbegründung",
  c.critical_nullmodel AS "kritisches Nullmodell",
  c.strengthening_nullmodel AS "stärkendes Nullmodell",
  c.formal_claim_status AS "formaler Claim-Status",
  c.physical_claim_release AS "physikalische Claim-Freigabe",
  c.next_gate AS "nächster Gate",
  c.external_readiness AS "externe Kommunikationsreife",
  c.reviewer_risk AS "Reviewer-Risiko",
  c.red_team_status AS "Red-Team-Status"
FROM qsb_planck_bridge.pbr_nullmodel_sample_results s
CROSS JOIN qsb_planck_bridge.pbr_nullmodel_specificity_classification c
WHERE s.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01' AND c.run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01';
