SELECT 'design_status' AS check_name, design_status AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_design_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';

SELECT 'test_family_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_test_family_spec
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';

SELECT 'decision_case_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_decision_cases
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM qsb_planck_bridge.pbr_lag_mechanism_next_gate_decision
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01';
