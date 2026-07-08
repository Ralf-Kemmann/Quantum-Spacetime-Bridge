SELECT 'design_status' AS check_name, design_status AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_design_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';

SELECT 'criterion_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_independence_criteria
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';

SELECT 'alias_rule_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_alias_rules
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';

SELECT 'test_design_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_test_design
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM qsb_planck_bridge.pbr_independent_lag_variable_next_gate
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INDEPENDENT-LAG-VARIABLE-DESIGN-01';
