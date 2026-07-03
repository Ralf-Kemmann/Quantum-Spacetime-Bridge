BEGIN;

DELETE FROM qsb_scale_mapping.scale_mapping_validation_result
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01';

WITH checks AS (
    SELECT 'VAL-MAP-COUNT' AS validation_id, 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01' AS run_id, 'source_import' AS validation_scope,
           'mapping_definition_count_matches_manifest' AS check_name,
           (SELECT mapping_definition_count::text FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01') AS expected_value,
           (SELECT count(*)::text FROM qsb_scale_mapping.mapping_definition WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01') AS actual_value,
           ((SELECT mapping_definition_count FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01') = (SELECT count(*) FROM qsb_scale_mapping.mapping_definition WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01')) AS passed,
           'error' AS severity
    UNION ALL
    SELECT 'VAL-VAR-COUNT','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','source_import','variable_count_matches_manifest',
           (SELECT variable_count::text FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           (SELECT count(*)::text FROM qsb_scale_mapping.variable_registry WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           ((SELECT variable_count FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01') = (SELECT count(*) FROM qsb_scale_mapping.variable_registry WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01')),
           'error'
    UNION ALL
    SELECT 'VAL-SC-COUNT','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','source_import','special_case_count_matches_manifest',
           (SELECT special_case_count::text FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           (SELECT count(*)::text FROM qsb_scale_mapping.special_case WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           ((SELECT special_case_count FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01') = (SELECT count(*) FROM qsb_scale_mapping.special_case WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01')),
           'error'
    UNION ALL
    SELECT 'VAL-CB-COUNT','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','claim_boundary','claim_boundary_count_matches_manifest',
           (SELECT claim_boundary_count::text FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           (SELECT count(*)::text FROM qsb_scale_mapping.claim_boundary WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           ((SELECT claim_boundary_count FROM qsb_scale_mapping.scale_mapping_run WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01') = (SELECT count(*) FROM qsb_scale_mapping.claim_boundary WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01')),
           'error'
    UNION ALL
    SELECT 'VAL-CLAIM-BLOCKED','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','claim_boundary','all_rows_claim_blocked','blocked_no_physics_claim only',
           (SELECT string_agg(DISTINCT physical_claim_release, ', ' ORDER BY physical_claim_release) FROM (
                SELECT physical_claim_release FROM qsb_scale_mapping.mapping_definition WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
                UNION ALL SELECT physical_claim_release FROM qsb_scale_mapping.claim_boundary WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
                UNION ALL SELECT physical_claim_release FROM qsb_scale_mapping.special_case WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
            ) s),
           NOT EXISTS (
                SELECT 1 FROM (
                    SELECT physical_claim_release FROM qsb_scale_mapping.mapping_definition WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
                    UNION ALL SELECT physical_claim_release FROM qsb_scale_mapping.claim_boundary WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
                    UNION ALL SELECT physical_claim_release FROM qsb_scale_mapping.special_case WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
                ) s WHERE physical_claim_release <> 'blocked_no_physics_claim'
           ),
           'error'
    UNION ALL
    SELECT 'VAL-DIM-PASS','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01','dimensional_analysis','all_dimensional_checks_passed','all pass',
           (SELECT string_agg(DISTINCT status, ', ' ORDER BY status) FROM qsb_scale_mapping.dimensional_check WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           NOT EXISTS (SELECT 1 FROM qsb_scale_mapping.dimensional_check WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01' AND status <> 'pass'),
           'error'
)
INSERT INTO qsb_scale_mapping.scale_mapping_validation_result
(validation_id, run_id, validation_scope, check_name, expected_value, actual_value, passed, severity)
SELECT validation_id, run_id, validation_scope, check_name, expected_value, actual_value, passed, severity
FROM checks;

COMMIT;

SELECT * FROM qsb_scale_mapping.v_planck_bridge_scale_mapping_dashboard;

SELECT validation_scope, check_name, expected_value, actual_value, passed, severity
FROM qsb_scale_mapping.scale_mapping_validation_result
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
ORDER BY validation_id;

SELECT mapping_id, mapping_level, mapping_name, dimensional_status, claim_status, physical_claim_release, review_status
FROM qsb_scale_mapping.mapping_definition
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
ORDER BY mapping_level, mapping_id;

SELECT * FROM qsb_scale_mapping.v_planck_bridge_scale_mapping_claim_boundary
ORDER BY mapping_level, mapping_id;
