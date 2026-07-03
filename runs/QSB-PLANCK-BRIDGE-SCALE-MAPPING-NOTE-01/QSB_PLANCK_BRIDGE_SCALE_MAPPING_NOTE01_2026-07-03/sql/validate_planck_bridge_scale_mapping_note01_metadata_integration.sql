BEGIN;

DELETE FROM qsb_metadata.scale_mapping_note01_validation_result
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01';

WITH checks AS (
    SELECT 'META-VAL-OBJECTS' AS validation_id, 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01' AS integration_run_id, 'metadata_catalog' AS validation_scope,
           'catalog_objects_registered' AS check_name, '9' AS expected_value,
           (SELECT count(*)::text FROM qsb_metadata.scale_mapping_note01_catalog_object) AS actual_value,
           ((SELECT count(*) FROM qsb_metadata.scale_mapping_note01_catalog_object) = 9) AS passed,
           'error' AS severity
    UNION ALL
    SELECT 'META-VAL-FIELDS','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01','metadata_fields','fields_registered','> 0',
           (SELECT count(*)::text FROM qsb_metadata.scale_mapping_note01_field_metadata),
           ((SELECT count(*) FROM qsb_metadata.scale_mapping_note01_field_metadata) > 0),
           'error'
    UNION ALL
    SELECT 'META-VAL-LINEAGE','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01','metadata_lineage','lineage_edges_registered','6',
           (SELECT count(*)::text FROM qsb_metadata.scale_mapping_note01_lineage_edge),
           ((SELECT count(*) FROM qsb_metadata.scale_mapping_note01_lineage_edge) = 6),
           'error'
    UNION ALL
    SELECT 'META-VAL-CB','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01','metadata_claim_boundary','claim_boundaries_registered','4',
           (SELECT count(*)::text FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata),
           ((SELECT count(*) FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata) = 4),
           'error'
    UNION ALL
    SELECT 'META-VAL-CLAIM-BLOCK','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01','claim_boundary','all_metadata_claims_blocked','blocked_no_physics_claim only',
           (SELECT string_agg(DISTINCT physical_claim_release, ', ' ORDER BY physical_claim_release) FROM (
                SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_catalog_object
                UNION ALL SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_field_metadata
                UNION ALL SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_lineage_edge
                UNION ALL SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata
            ) s),
           NOT EXISTS (
                SELECT 1 FROM (
                    SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_catalog_object
                    UNION ALL SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_field_metadata
                    UNION ALL SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_lineage_edge
                    UNION ALL SELECT physical_claim_release FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata
                ) s WHERE physical_claim_release <> 'blocked_no_physics_claim'
           ),
           'error'
    UNION ALL
    SELECT 'META-VAL-IMPORT-PASSED','QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01','source_import','source_validation_all_passed','all true',
           (SELECT coalesce(bool_and(passed)::text, 'false') FROM qsb_scale_mapping.scale_mapping_validation_result WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           (SELECT coalesce(bool_and(passed), false) FROM qsb_scale_mapping.scale_mapping_validation_result WHERE run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'),
           'error'
)
INSERT INTO qsb_metadata.scale_mapping_note01_validation_result
(validation_id, integration_run_id, validation_scope, check_name, expected_value, actual_value, passed, severity)
SELECT validation_id, integration_run_id, validation_scope, check_name, expected_value, actual_value, passed, severity
FROM checks;

UPDATE qsb_metadata.scale_mapping_note01_metadata_integration_run
SET
    field_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_field_metadata),
    lineage_edge_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_lineage_edge),
    claim_boundary_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata),
    validation_result_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_validation_result WHERE integration_run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01'),
    all_metadata_validations_passed = (SELECT bool_and(passed) FROM qsb_metadata.scale_mapping_note01_validation_result WHERE integration_run_id='QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01')
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01';

COMMIT;

SELECT * FROM qsb_metadata.v_planck_bridge_scale_mapping_note01_metadata_dashboard;

SELECT validation_scope, check_name, expected_value, actual_value, passed, severity
FROM qsb_metadata.scale_mapping_note01_validation_result
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01'
ORDER BY validation_id;

SELECT metadata_scope, count(*) AS rows
FROM qsb_metadata.v_planck_bridge_scale_mapping_note01_metadata_search
GROUP BY metadata_scope
ORDER BY metadata_scope;

SELECT scope_type, scope_key, physical_claim_release, review_status
FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata
ORDER BY scope_type, scope_key;
