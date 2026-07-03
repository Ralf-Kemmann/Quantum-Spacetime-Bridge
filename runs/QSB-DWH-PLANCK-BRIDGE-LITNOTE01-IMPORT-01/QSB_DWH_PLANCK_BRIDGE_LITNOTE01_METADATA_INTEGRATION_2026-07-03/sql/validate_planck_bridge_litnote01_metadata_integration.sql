-- Validation queries for QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01

SELECT *
FROM qsb_metadata.v_planck_bridge_litnote01_metadata_dashboard;

SELECT validation_scope, check_name, expected_value, actual_value, passed, severity
FROM qsb_metadata.litnote01_validation_result
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
ORDER BY validation_id;

SELECT metadata_scope, COUNT(*) AS rows
FROM qsb_metadata.v_planck_bridge_litnote01_metadata_search
GROUP BY metadata_scope
ORDER BY metadata_scope;

SELECT object_qualified_name, COUNT(*) AS field_count
FROM qsb_metadata.litnote01_field_metadata
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
GROUP BY object_qualified_name
ORDER BY object_qualified_name;

SELECT scope_type, scope_key, physical_claim_release, review_status
FROM qsb_metadata.litnote01_claim_boundary_metadata
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
ORDER BY scope_type, scope_key;

SELECT *
FROM qsb_metadata.v_planck_bridge_litnote01_metadata_search
WHERE search_text ILIKE '%Planck%'
ORDER BY metadata_scope, qualified_name
LIMIT 25;
