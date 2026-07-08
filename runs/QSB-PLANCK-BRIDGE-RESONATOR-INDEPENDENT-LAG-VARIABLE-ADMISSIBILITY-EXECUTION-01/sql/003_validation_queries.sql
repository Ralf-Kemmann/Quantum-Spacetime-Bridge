SELECT 'execution_status' AS check_name, execution_status AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01';

SELECT 'candidate_count_total' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_results
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01';

SELECT 'admissible_for_testing' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_results
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01' AND admissibility_decision_class = 'candidate_admissible_for_lag_mechanism_testing';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_admissibility_next_gate
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-ADMISSIBILITY-EXECUTION-01';
