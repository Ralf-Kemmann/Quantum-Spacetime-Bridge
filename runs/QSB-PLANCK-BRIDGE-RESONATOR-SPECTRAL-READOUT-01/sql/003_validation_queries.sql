-- Validation queries for QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01

SELECT current_database() AS db, current_user AS db_user, current_schema() AS current_schema;

SELECT *
FROM qsb_planck_bridge.v_pbr_spectral_readout01_summary;

SELECT
    'run_exists' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_spectral_readout_run
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

SELECT
    'input_hash_matches' AS check_name,
    CASE WHEN COUNT(*) = 3 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_spectral_readout_input_lineage
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01'
  AND hash_match IS TRUE;

SELECT
    'rank_is_six' AS check_name,
    CASE WHEN rank_tol_1e_10 = 6 THEN 'pass' ELSE 'fail' END AS result,
    rank_tol_1e_10 AS observed_value
FROM qsb_planck_bridge.pbr_spectral_readout_result
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

SELECT
    'nullity_is_36' AS check_name,
    CASE WHEN nullity = 36 THEN 'pass' ELSE 'fail' END AS result,
    nullity AS observed_value
FROM qsb_planck_bridge.pbr_spectral_readout_result
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01';

SELECT
    'parallel_count_is_70' AS check_name,
    CASE WHEN observed_count = 70 THEN 'pass' ELSE 'fail' END AS result,
    observed_count AS observed_value
FROM qsb_planck_bridge.pbr_spectral_readout_parallel_counts
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01'
  AND metric = 'parallel_count';

SELECT
    'antiparallel_count_is_91' AS check_name,
    CASE WHEN observed_count = 91 THEN 'pass' ELSE 'fail' END AS result,
    observed_count AS observed_value
FROM qsb_planck_bridge.pbr_spectral_readout_parallel_counts
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01'
  AND metric = 'antiparallel_count';

SELECT
    'physical_claim_release_blocked' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_spectral_readout_result
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01'
  AND physical_claim_release = 'blocked_no_physics_claim';

SELECT
    'claim_boundaries_blocked' AS check_name,
    CASE WHEN COUNT(*) >= 4 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_spectral_readout_claim_boundary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01'
  AND boundary_type = 'blocked_claim'
  AND release_status LIKE 'blocked%';

SELECT *
FROM qsb_planck_bridge.v_pbr_spectral_readout01_lag_class_summary
ORDER BY abs_lag;

SELECT *
FROM qsb_planck_bridge.v_pbr_spectral_readout01_parallel_counts
ORDER BY metric;

SELECT *
FROM qsb_planck_bridge.v_pbr_spectral_readout01_claim_boundary
ORDER BY boundary_type, boundary_id;

