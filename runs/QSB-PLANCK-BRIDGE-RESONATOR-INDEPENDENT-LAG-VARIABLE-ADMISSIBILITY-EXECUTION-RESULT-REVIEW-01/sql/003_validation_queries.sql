SELECT 'review_outcome' AS check_name, review_outcome AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';

SELECT 'candidate_count_total' AS check_name, candidate_count_total AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';

SELECT 'dominant_blocker' AS check_name, dominant_blocker AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_result_review_next_gate
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-RESULT-REVIEW-01';
