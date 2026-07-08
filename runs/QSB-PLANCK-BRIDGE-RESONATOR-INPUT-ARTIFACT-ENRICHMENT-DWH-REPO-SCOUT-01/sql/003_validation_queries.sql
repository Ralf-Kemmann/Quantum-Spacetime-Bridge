SELECT 'scout_decision' AS check_name, scout_decision AS value
FROM qsb_planck_bridge.pbr_input_artifact_enrichment_scout_summary
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';

SELECT 'candidate_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_input_artifact_enrichment_candidate_variables
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';

SELECT 'proxy_family_count' AS check_name, count(*)::text AS value
FROM qsb_planck_bridge.pbr_input_artifact_enrichment_physical_proxy_sources
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';

SELECT 'next_gate' AS check_name, next_gate AS value
FROM qsb_planck_bridge.pbr_input_artifact_enrichment_next_gate
WHERE run_id = 'QSB-PLANCK-BRIDGE-RESONATOR-INPUT-ARTIFACT-ENRICHMENT-DWH-REPO-SCOUT-01';
