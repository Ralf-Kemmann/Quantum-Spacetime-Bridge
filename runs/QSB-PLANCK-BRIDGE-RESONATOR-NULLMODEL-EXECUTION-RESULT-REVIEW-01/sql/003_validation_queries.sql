SELECT 'review_outcome' AS check_name, review_outcome AS value
FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';

SELECT 'critical_nullmodel' AS check_name, critical_nullmodel AS value
FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_critical_findings
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';

SELECT 'specificity_classification' AS check_name, specificity_classification AS value
FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_specificity
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM qsb_planck_bridge.pbr_nullmodel_execution_result_review_next_gate
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01';
