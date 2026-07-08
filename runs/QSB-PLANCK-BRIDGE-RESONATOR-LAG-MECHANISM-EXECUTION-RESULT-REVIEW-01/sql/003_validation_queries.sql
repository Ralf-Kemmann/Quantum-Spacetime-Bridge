SELECT 'review_outcome' AS check_name, review_outcome AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';

SELECT 'confirmed_decision' AS check_name, review_confirmed_decision_class AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_decision
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_next_gate
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01';

SELECT 'primary_next_run' AS check_name, recommended_run_id AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_execution_result_review_recommended_work
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-RESULT-REVIEW-01' AND recommendation_rank = 'primary';
