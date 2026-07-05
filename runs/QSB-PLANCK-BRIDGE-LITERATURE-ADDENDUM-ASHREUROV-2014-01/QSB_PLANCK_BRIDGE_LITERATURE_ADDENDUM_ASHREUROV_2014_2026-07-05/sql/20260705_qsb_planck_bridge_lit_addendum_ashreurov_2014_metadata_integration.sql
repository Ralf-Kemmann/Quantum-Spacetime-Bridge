-- QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01
-- Idempotent metadata integration for Ashtekar/Reuter/Rovelli 2014 literature addendum.

BEGIN;

CREATE SCHEMA IF NOT EXISTS qsb_metadata;

CREATE TABLE IF NOT EXISTS qsb_metadata.lit_addendum_ashreurov_2014_metadata_integration_run (
    integration_run_id TEXT PRIMARY KEY,
    source_run_id TEXT NOT NULL,
    work_package TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata_scope TEXT NOT NULL,
    object_count INTEGER NOT NULL DEFAULT 0,
    field_count INTEGER NOT NULL DEFAULT 0,
    lineage_edge_count INTEGER NOT NULL DEFAULT 0,
    claim_boundary_count INTEGER NOT NULL DEFAULT 0,
    validation_result_count INTEGER NOT NULL DEFAULT 0,
    physical_claim_status TEXT NOT NULL,
    review_status TEXT NOT NULL,
    all_metadata_validations_passed BOOLEAN NOT NULL DEFAULT FALSE,
    claim_boundary TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.lit_addendum_ashreurov_2014_catalog_object (
    object_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL,
    object_qualified_name TEXT NOT NULL,
    object_type TEXT NOT NULL,
    qsb_domain TEXT NOT NULL,
    semantic_role TEXT NOT NULL,
    description TEXT NOT NULL,
    lineage_note TEXT,
    claim_status TEXT NOT NULL,
    physical_claim_release TEXT NOT NULL,
    review_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.lit_addendum_ashreurov_2014_field_metadata (
    field_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL,
    object_qualified_name TEXT NOT NULL,
    field_name TEXT NOT NULL,
    data_type TEXT NOT NULL,
    qsb_domain TEXT NOT NULL,
    semantic_role TEXT NOT NULL,
    description TEXT NOT NULL,
    claim_status TEXT NOT NULL,
    physical_claim_release TEXT NOT NULL,
    review_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.lit_addendum_ashreurov_2014_lineage_edge (
    lineage_edge_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL,
    source_object TEXT NOT NULL,
    target_object TEXT NOT NULL,
    transformation_role TEXT NOT NULL,
    description TEXT NOT NULL,
    claim_status TEXT NOT NULL,
    physical_claim_release TEXT NOT NULL,
    review_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata (
    boundary_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL,
    scope_type TEXT NOT NULL,
    scope_key TEXT NOT NULL,
    allowed_claim TEXT NOT NULL,
    forbidden_claim TEXT NOT NULL,
    physical_claim_release TEXT NOT NULL,
    review_status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.lit_addendum_ashreurov_2014_validation_result (
    validation_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL,
    validation_scope TEXT NOT NULL,
    check_name TEXT NOT NULL,
    expected_value TEXT NOT NULL,
    actual_value TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    severity TEXT NOT NULL
);

INSERT INTO qsb_metadata.lit_addendum_ashreurov_2014_metadata_integration_run (
    integration_run_id, source_run_id, work_package, created_at, metadata_scope,
    physical_claim_status, review_status, claim_boundary
) VALUES (
    'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01',
    'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01',
    'QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01',
    '2026-07-05T00:00:00+02:00',
    'literature_addendum_ashreurov_2014_dynamic_geometry_planck_regime',
    'blocked_no_physics_claim',
    'registered_requires_human_literature_review',
    'Metadata integration registers literature provenance and claim boundaries only; it does not release physics claims.'
)
ON CONFLICT (integration_run_id) DO UPDATE SET
    source_run_id = EXCLUDED.source_run_id,
    work_package = EXCLUDED.work_package,
    metadata_scope = EXCLUDED.metadata_scope,
    physical_claim_status = EXCLUDED.physical_claim_status,
    review_status = EXCLUDED.review_status,
    claim_boundary = EXCLUDED.claim_boundary;

DELETE FROM qsb_metadata.lit_addendum_ashreurov_2014_catalog_object WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';
INSERT INTO qsb_metadata.lit_addendum_ashreurov_2014_catalog_object VALUES
('OBJ-ASHREUROV-RUN', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'qsb_literature.litnote_run', 'table', 'literature_metadata', 'run_manifest', 'Run-level manifest for the Ashtekar/Reuter/Rovelli 2014 addendum.', 'Derived from literature_addendum_manifest.json and BibTeX source.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('OBJ-ASHREUROV-SOURCE', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'qsb_literature.reference_source', 'table', 'literature_metadata', 'bibliographic_source_registry', 'Bibliographic source registry entry for Ashtekar/Reuter/Rovelli 2014.', 'Derived from uploaded PDF and addendum BibTeX.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('OBJ-ASHREUROV-CLAIMMAP', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'qsb_literature.reference_claim_map', 'table', 'literature_claim_boundary', 'claim_mapping_registry', 'Claim mapping for the Ashtekar/Reuter/Rovelli 2014 addendum.', 'Maps source to allowed and forbidden QSB claims.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('OBJ-ASHREUROV-VIEW', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'qsb_literature.v_planck_bridge_lit_addendum_ashreurov_2014_claim_boundary', 'view', 'literature_claim_boundary', 'claim_boundary_review_view', 'Human-readable review view for the Ashtekar/Reuter/Rovelli 2014 addendum.', 'Derived by joining reference_source and reference_claim_map.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review');

DELETE FROM qsb_metadata.lit_addendum_ashreurov_2014_field_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';
INSERT INTO qsb_metadata.lit_addendum_ashreurov_2014_field_metadata (
    field_id, integration_run_id, object_qualified_name, field_name, data_type,
    qsb_domain, semantic_role, description, claim_status, physical_claim_release, review_status
)
SELECT
    'FIELD-ASHREUROV-' || regexp_replace(c.table_schema || '-' || c.table_name || '-' || c.column_name, '[^a-zA-Z0-9]+', '-', 'g') AS field_id,
    'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01',
    c.table_schema || '.' || c.table_name AS object_qualified_name,
    c.column_name,
    c.data_type,
    CASE WHEN c.column_name IN ('supports','does_not_support','allowed_claim','forbidden_claim','claim_status','physical_claim_release','review_status') THEN 'literature_claim_boundary' ELSE 'literature_metadata' END,
    CASE
        WHEN c.column_name IN ('run_id','bib_key','claim_map_id') THEN 'identifier'
        WHEN c.column_name IN ('supports','does_not_support','allowed_claim','forbidden_claim','claim_status','physical_claim_release','review_status') THEN 'claim_boundary_control'
        WHEN c.column_name IN ('title','authors','year','arxiv_id','doi','url','publisher','booktitle') THEN 'bibliographic_descriptor'
        ELSE 'technical_descriptor'
    END,
    'Field metadata registered for Ashtekar/Reuter/Rovelli 2014 addendum object ' || c.table_schema || '.' || c.table_name || '.' || c.column_name || '.',
    CASE WHEN c.column_name IN ('supports','does_not_support','allowed_claim','forbidden_claim','claim_status','physical_claim_release','review_status') THEN 'claim_control_field' ELSE 'metadata_field' END,
    'blocked_no_physics_claim',
    'registered_requires_human_literature_review'
FROM information_schema.columns c
WHERE c.table_schema = 'qsb_literature'
  AND c.table_name IN ('litnote_run','reference_source','reference_claim_map','v_planck_bridge_lit_addendum_ashreurov_2014_claim_boundary');

DELETE FROM qsb_metadata.lit_addendum_ashreurov_2014_lineage_edge WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';
INSERT INTO qsb_metadata.lit_addendum_ashreurov_2014_lineage_edge VALUES
('LINEAGE-ASHREUROV-PDF-BIB', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'source:From_general_relativity_to_quantum_gravi-1.pdf', 'qsb_planck_bridge_lit_addendum_ashreurov_2014.bib', 'bibliographic_abstraction', 'Uploaded PDF metadata is abstracted into a BibTeX addendum entry.', 'lineage_registered', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('LINEAGE-ASHREUROV-BIB-SOURCE', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'qsb_planck_bridge_lit_addendum_ashreurov_2014.bib', 'qsb_literature.reference_source', 'source_registry_import', 'BibTeX source is imported into qsb_literature.reference_source.', 'lineage_registered', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('LINEAGE-ASHREUROV-CLAIMMAP', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'data/literature_addendum_claim_map.csv', 'qsb_literature.reference_claim_map', 'claim_mapping_import', 'Claim map is imported into qsb_literature.reference_claim_map.', 'lineage_registered', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('LINEAGE-ASHREUROV-VIEW', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'qsb_literature.reference_source + qsb_literature.reference_claim_map', 'qsb_literature.v_planck_bridge_lit_addendum_ashreurov_2014_claim_boundary', 'relational_view_join', 'Source registry and claim map are joined for human claim-boundary review.', 'lineage_registered', 'blocked_no_physics_claim', 'registered_requires_human_literature_review');

DELETE FROM qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';
INSERT INTO qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata VALUES
('BOUNDARY-ASHREUROV-WORKPACKAGE', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'work_package', 'QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01', 'The paper may motivate QSB to treat spacetime geometry as dynamic and Planck-regime short-distance structure as non-classical.', 'It does not release physical claims about QSB or Planck-Bridge-Resonators.', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('BOUNDARY-ASHREUROV-SOURCE', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'source', 'ashtekar_reuter_rovelli2014_from_gr_to_quantum_gravity', 'The source may be used as a broad overview anchor for LQG, Asymptotic Safety, quantum geometry, and suitable-limit recovery of GR.', 'It must not be used as a direct evidence anchor for the QSB resonator entity.', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('BOUNDARY-ASHREUROV-POLYMER', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'concept', 'lqg_polymer_like_geometry_quanta', 'The polymer-like LQG language may be registered as a structural analogy to non-pointlike relational geometry carriers.', 'It must not be equated with strings or QSB Planck-Bridge-Resonators.', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('BOUNDARY-ASHREUROV-SCALEGATE', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01', 'concept', 'planck_regime_first_gate', 'The source may motivate the methodological rule: check Planck-regime scale and short-distance structure before emergent classical geometry claims.', 'It does not validate any particular QSB scale gate as physically real.', 'blocked_no_physics_claim', 'registered_requires_human_literature_review');

UPDATE qsb_metadata.lit_addendum_ashreurov_2014_metadata_integration_run
SET object_count = (SELECT COUNT(*) FROM qsb_metadata.lit_addendum_ashreurov_2014_catalog_object WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'),
    field_count = (SELECT COUNT(*) FROM qsb_metadata.lit_addendum_ashreurov_2014_field_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'),
    lineage_edge_count = (SELECT COUNT(*) FROM qsb_metadata.lit_addendum_ashreurov_2014_lineage_edge WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01'),
    claim_boundary_count = (SELECT COUNT(*) FROM qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01')
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';

CREATE OR REPLACE VIEW qsb_metadata.v_planck_bridge_lit_addendum_ashreurov_2014_metadata_search AS
SELECT 'catalog_object' AS metadata_scope, object_qualified_name AS qualified_name, NULL::TEXT AS field_name, object_type, qsb_domain, semantic_role, description, lineage_note, claim_status, physical_claim_release, review_status,
       object_qualified_name || ' | ' || object_type || ' | ' || qsb_domain || ' | ' || semantic_role || ' | ' || description || ' | ' || COALESCE(lineage_note,'') AS search_text
FROM qsb_metadata.lit_addendum_ashreurov_2014_catalog_object
UNION ALL
SELECT 'field', object_qualified_name, field_name, 'field', qsb_domain, semantic_role, description, NULL::TEXT, claim_status, physical_claim_release, review_status,
       object_qualified_name || ' | ' || field_name || ' | ' || data_type || ' | ' || qsb_domain || ' | ' || semantic_role || ' | ' || description
FROM qsb_metadata.lit_addendum_ashreurov_2014_field_metadata
UNION ALL
SELECT 'lineage', target_object, NULL::TEXT, 'lineage_edge', 'literature_lineage', transformation_role, description, source_object || ' -> ' || target_object, claim_status, physical_claim_release, review_status,
       source_object || ' | ' || target_object || ' | ' || transformation_role || ' | ' || description
FROM qsb_metadata.lit_addendum_ashreurov_2014_lineage_edge
UNION ALL
SELECT 'claim_boundary', scope_key, NULL::TEXT, scope_type, 'literature_claim_boundary', 'claim_boundary', allowed_claim, forbidden_claim, 'claim_boundary_registered', physical_claim_release, review_status,
       scope_type || ' | ' || scope_key || ' | ' || allowed_claim || ' | ' || forbidden_claim || ' | ' || physical_claim_release || ' | ' || review_status
FROM qsb_metadata.lit_addendum_ashreurov_2014_claim_boundary_metadata;

CREATE OR REPLACE VIEW qsb_metadata.v_planck_bridge_lit_addendum_ashreurov_2014_metadata_dashboard AS
SELECT * FROM qsb_metadata.lit_addendum_ashreurov_2014_metadata_integration_run
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-METADATA-INTEGRATION-01';

COMMIT;
