SELECT 'sample_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_nullmodel_sample_results
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01';

SELECT 'families' AS check_name, count(DISTINCT nullmodel_family)::text AS value
FROM qsb_planck_bridge.pbr_nullmodel_sample_results
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01';

SELECT 'physical_claim_release' AS check_name, physical_claim_release AS value
FROM qsb_planck_bridge.pbr_nullmodel_specificity_classification
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01';

SELECT 'specificity_classification' AS check_name, specificity_classification AS value
FROM qsb_planck_bridge.pbr_nullmodel_specificity_classification
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01';
