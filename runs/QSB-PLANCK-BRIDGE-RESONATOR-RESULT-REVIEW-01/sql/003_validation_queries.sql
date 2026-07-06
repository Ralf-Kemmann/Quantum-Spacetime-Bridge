-- Validation queries for QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01

SELECT current_database() AS db, current_user AS db_user, current_schema() AS current_schema;

SELECT *
FROM qsb_planck_bridge.v_pbr_result_review01_summary;

SELECT 'run_exists' AS check_name,
       CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_run
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

SELECT 'summary_exists' AS check_name,
       CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_summary
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

SELECT 'physical_claim_release_blocked' AS check_name,
       CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_summary
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01'
  AND physical_claim_release = 'blocked_no_physics_claim';

SELECT 'claim_status_result_review_only' AS check_name,
       CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_summary
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01'
  AND claim_status = 'result_review_only';

SELECT 'next_gate_nullmodel_design_required' AS check_name,
       CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_summary
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01'
  AND next_gate = 'nullmodel_design_required';

SELECT 'blocked_claims_present' AS check_name,
       CASE WHEN COUNT(*) >= 5 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_blocked_claim
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01'
  AND physical_claim_release = 'blocked_no_physics_claim';

SELECT 'recommended_next_tests_present' AS check_name,
       CASE WHEN COUNT(*) >= 7 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_next_test
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01';

SELECT 'external_physics_claim_blocked' AS check_name,
       CASE WHEN COUNT(*) = 1 THEN 'pass' ELSE 'fail' END AS result,
       COUNT(*) AS observed_count
FROM qsb_planck_bridge.pbr_result_review_external_readiness
WHERE review_run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01'
  AND communication_item = 'external_physics_claim'
  AND readiness = 'blocked';

SELECT * FROM qsb_planck_bridge.v_pbr_result_review01_formal_findings ORDER BY finding_id;
SELECT * FROM qsb_planck_bridge.v_pbr_result_review01_construction_bound_findings ORDER BY finding_id;
SELECT * FROM qsb_planck_bridge.v_pbr_result_review01_blocked_claims ORDER BY blocked_claim_id;
SELECT * FROM qsb_planck_bridge.v_pbr_result_review01_next_tests ORDER BY test_id;
SELECT * FROM qsb_planck_bridge.v_pbr_result_review01_external_readiness ORDER BY item_id;
