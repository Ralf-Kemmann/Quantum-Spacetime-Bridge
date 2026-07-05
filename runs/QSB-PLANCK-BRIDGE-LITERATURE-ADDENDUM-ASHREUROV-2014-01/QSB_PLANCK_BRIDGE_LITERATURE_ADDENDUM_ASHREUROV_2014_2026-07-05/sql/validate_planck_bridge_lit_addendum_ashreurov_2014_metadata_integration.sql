-- Validate metadata integration for QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01

BEGIN;
DELETE FROM qsb_metadata.lit_addendum_ashreurov_2014_validation_result WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';

INSERT INTO qsb_metadata.lit_addendum_ashreurov_2014_validation_result VALUES
('VAL-ASHREUROV-SOURCE-COUNT', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'source_import', 'source_count_matches_manifest', '1', (SELECT COUNT(*)::TEXT FROM qsb_literature.reference_source WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'), (SELECT COUNT(*) = 1 FROM qsb_literature.reference_source WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'), 'error'),
('VAL-ASHREUROV-CLAIMMAP-COUNT', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'source_import', 'claim_map_count_matches_manifest', '1', (SELECT COUNT(*)::TEXT FROM qsb_literature.reference_claim_map WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'), (SELECT COUNT(*) = 1 FROM qsb_literature.reference_claim_map WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'), 'error'),
('VAL-ASHREUROV-CLAIMS-BLOCKED', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'claim_boundary', 'all_metadata_claims_blocked', 'blocked_no_physics_claim only', (SELECT COALESCE(MIN(physical_claim_release),'missing') FROM qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), (SELECT COUNT(*) = 4 AND MIN(physical_claim_release) = 'blocked_no_physics_claim' AND MAX(physical_claim_release) = 'blocked_no_physics_claim' FROM qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), 'error'),
('VAL-ASHREUROV-CATALOG', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'metadata_catalog', 'catalog_objects_registered', '4', (SELECT COUNT(*)::TEXT FROM qsb_metadata.lit_addendum_ashreurov_2014_catalog_object WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), (SELECT COUNT(*) = 4 FROM qsb_metadata.lit_addendum_ashreurov_2014_catalog_object WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), 'error'),
('VAL-ASHREUROV-FIELDS', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'metadata_fields', 'fields_registered', '> 0', (SELECT COUNT(*)::TEXT FROM qsb_metadata.lit_addendum_ashreurov_2014_field_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), (SELECT COUNT(*) > 0 FROM qsb_metadata.lit_addendum_ashreurov_2014_field_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), 'error'),
('VAL-ASHREUROV-LINEAGE', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'metadata_lineage', 'lineage_edges_registered', '4', (SELECT COUNT(*)::TEXT FROM qsb_metadata.lit_addendum_ashreurov_2014_lineage_edge WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), (SELECT COUNT(*) = 4 FROM qsb_metadata.lit_addendum_ashreurov_2014_lineage_edge WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'), 'error');

UPDATE qsb_metadata.lit_addendum_ashreurov_2014_metadata_integration_run
SET validation_result_count = (SELECT COUNT(*) FROM qsb_metadata.lit_addendum_ashreurov_2014_validation_result WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'),
    all_metadata_validations_passed = (SELECT bool_and(passed) FROM qsb_metadata.lit_addendum_ashreurov_2014_validation_result WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01')
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';
COMMIT;

SELECT * FROM qsb_metadata.v_planck_bridge_lit_addendum_ashreurov_2014_metadata_dashboard;

SELECT validation_scope, check_name, expected_value, actual_value, passed, severity
FROM qsb_metadata.lit_addendum_ashreurov_2014_validation_result
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'
ORDER BY validation_scope, check_name;

SELECT metadata_scope, COUNT(*) AS rows
FROM qsb_metadata.v_planck_bridge_lit_addendum_ashreurov_2014_metadata_search
GROUP BY metadata_scope
ORDER BY metadata_scope;

SELECT scope_type, scope_key, physical_claim_release, review_status
FROM qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'
ORDER BY scope_type, scope_key;
