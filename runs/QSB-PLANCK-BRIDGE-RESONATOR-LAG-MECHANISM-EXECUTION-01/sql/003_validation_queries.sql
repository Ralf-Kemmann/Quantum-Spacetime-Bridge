SELECT 'execution_status' AS check_name, execution_status AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_execution_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';

SELECT 'test_family_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_test_results
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';

SELECT 'final_decision_class' AS check_name, final_decision_class AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_decision
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';

SELECT 'physical_claim_release' AS check_name, physical_claim_release AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_decision
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01';
