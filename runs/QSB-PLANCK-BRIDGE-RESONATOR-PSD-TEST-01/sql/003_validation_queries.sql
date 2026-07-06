-- Validation queries for QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01

SELECT current_database() AS db, current_user AS db_user, current_schema() AS current_schema;

SELECT *
FROM qsb_planck_bridge.v_pbr_psd_test01_summary;

SELECT
    'run_exists' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_test_run
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01';

SELECT
    'input_hashes_match' AS check_name,
    CASE WHEN COUNT(*) = 3 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_test_input_lineage
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01'
  AND hash_match IS TRUE;

SELECT
    'psd_gate_has_boolean_result' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_test_gate_result
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01'
  AND psd_pass IN (true, false);

SELECT
    'psd_gate_result_claim_boundary' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_test_gate_result
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01'
  AND claim_status = 'formal_admissibility_result_only'
  AND physical_claim_release = 'blocked_no_physics_claim';

SELECT
    'eigenvalue_report_metrics_present' AS check_name,
    CASE WHEN COUNT(*) >= 7 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_test_eigenvalue_report
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01'
  AND metric IN (
      'n',
      'lambda_min',
      'lambda_max',
      'negative_eigenvalue_count',
      'negative_eigenvalue_mass',
      'tolerance',
      'psd_pass',
      'admissibility_result'
  );

SELECT
    'physical_claim_release_blocked' AS check_name,
    CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_test_gate_result
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01'
  AND physical_claim_release = 'blocked_no_physics_claim';

SELECT
    'claim_boundaries_blocked' AS check_name,
    CASE WHEN COUNT(*) >= 4 THEN 'pass' ELSE 'fail' END AS result,
    COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_psd_test_claim_boundary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01'
  AND boundary_type = 'blocked_claim'
  AND release_status LIKE 'blocked%';

SELECT *
FROM qsb_planck_bridge.v_pbr_psd_test01_gate_result;

SELECT *
FROM qsb_planck_bridge.v_pbr_psd_test01_claim_boundary
ORDER BY boundary_type, boundary_id;
