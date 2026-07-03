BEGIN;

CREATE SCHEMA IF NOT EXISTS qsb_metadata;

CREATE TABLE IF NOT EXISTS qsb_metadata.scale_mapping_note01_metadata_integration_run (
    integration_run_id text PRIMARY KEY,
    source_run_id text NOT NULL,
    work_package text NOT NULL,
    metadata_scope text NOT NULL,
    object_count integer NOT NULL,
    field_count integer NOT NULL DEFAULT 0,
    lineage_edge_count integer NOT NULL DEFAULT 0,
    claim_boundary_count integer NOT NULL DEFAULT 0,
    validation_result_count integer NOT NULL DEFAULT 0,
    physical_claim_status text NOT NULL,
    review_status text NOT NULL,
    all_metadata_validations_passed boolean DEFAULT false,
    claim_boundary text NOT NULL,
    inserted_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS qsb_metadata.scale_mapping_note01_catalog_object (
    object_qualified_name text PRIMARY KEY,
    object_type text NOT NULL,
    qsb_domain text NOT NULL,
    semantic_role text NOT NULL,
    description text NOT NULL,
    lineage_note text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.scale_mapping_note01_field_metadata (
    object_qualified_name text NOT NULL,
    field_name text NOT NULL,
    data_type text NOT NULL,
    qsb_domain text NOT NULL,
    semantic_role text NOT NULL,
    display_label_de text NOT NULL,
    description text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL,
    PRIMARY KEY (object_qualified_name, field_name)
);

CREATE TABLE IF NOT EXISTS qsb_metadata.scale_mapping_note01_lineage_edge (
    lineage_edge_id text PRIMARY KEY,
    source_ref text NOT NULL,
    target_ref text NOT NULL,
    transformation_role text NOT NULL,
    description text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.scale_mapping_note01_claim_boundary_metadata (
    boundary_id text PRIMARY KEY,
    scope_type text NOT NULL,
    scope_key text NOT NULL,
    allowed_claim text NOT NULL,
    forbidden_claim text NOT NULL,
    claim_status text NOT NULL,
    physical_claim_release text NOT NULL,
    review_status text NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_metadata.scale_mapping_note01_validation_result (
    validation_id text PRIMARY KEY,
    integration_run_id text NOT NULL,
    validation_scope text NOT NULL,
    check_name text NOT NULL,
    expected_value text NOT NULL,
    actual_value text NOT NULL,
    passed boolean NOT NULL,
    severity text NOT NULL,
    created_at timestamptz DEFAULT now()
);

INSERT INTO qsb_metadata.scale_mapping_note01_metadata_integration_run (
    integration_run_id, source_run_id, work_package, metadata_scope, object_count,
    physical_claim_status, review_status, claim_boundary
) VALUES (
    'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01', 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01', 'scale_mapping_note_01_mapping_definitions_claim_boundaries', 9,
    'blocked_no_physics_claim', 'requires_dimensional_and_physical_review',
    'Metadata integration registers scale mapping provenance, dimensions, and claim boundaries only; it does not release physics claims.'
)
ON CONFLICT (integration_run_id) DO UPDATE SET
    object_count = EXCLUDED.object_count,
    physical_claim_status = EXCLUDED.physical_claim_status,
    review_status = EXCLUDED.review_status,
    claim_boundary = EXCLUDED.claim_boundary;

INSERT INTO qsb_metadata.scale_mapping_note01_catalog_object (
    object_qualified_name, object_type, qsb_domain, semantic_role, description, lineage_note,
    claim_status, physical_claim_release, review_status
) VALUES
('qsb_scale_mapping.scale_mapping_run', 'table', 'scale_mapping_metadata', 'scale_mapping_registry', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.scale_mapping_run.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.mapping_definition', 'table', 'scale_mapping_metadata', 'scale_mapping_registry', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.mapping_definition.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.variable_registry', 'table', 'scale_mapping_metadata', 'scale_mapping_registry', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.variable_registry.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.special_case', 'table', 'scale_mapping_metadata', 'scale_mapping_registry', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.special_case.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.claim_boundary', 'table', 'scale_mapping_metadata', 'scale_mapping_registry', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.claim_boundary.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.dimensional_check', 'table', 'scale_mapping_metadata', 'scale_mapping_registry', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.dimensional_check.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.scale_mapping_validation_result', 'table', 'scale_mapping_metadata', 'scale_mapping_registry', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.scale_mapping_validation_result.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.v_planck_bridge_scale_mapping_claim_boundary', 'view', 'scale_mapping_metadata', 'claim_boundary_review_view', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.v_planck_bridge_scale_mapping_claim_boundary.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('qsb_scale_mapping.v_planck_bridge_scale_mapping_dashboard', 'view', 'scale_mapping_metadata', 'dashboard_view', 'Metadata object for Scale Mapping Note 01: qsb_scale_mapping.v_planck_bridge_scale_mapping_dashboard.', 'Registered from QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review')
ON CONFLICT (object_qualified_name) DO UPDATE SET
    object_type = EXCLUDED.object_type,
    qsb_domain = EXCLUDED.qsb_domain,
    semantic_role = EXCLUDED.semantic_role,
    description = EXCLUDED.description,
    lineage_note = EXCLUDED.lineage_note,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;

INSERT INTO qsb_metadata.scale_mapping_note01_field_metadata (
    object_qualified_name, field_name, data_type, qsb_domain, semantic_role, display_label_de, description,
    claim_status, physical_claim_release, review_status
)
SELECT
    c.table_schema || '.' || c.table_name AS object_qualified_name,
    c.column_name AS field_name,
    c.data_type,
    'scale_mapping_metadata' AS qsb_domain,
    CASE
        WHEN c.column_name LIKE '%claim%' OR c.column_name IN ('allowed_claim','forbidden_claim','physical_claim_release','review_status') THEN 'claim_boundary_control'
        WHEN c.column_name LIKE '%dimension%' THEN 'dimensional_control'
        WHEN c.column_name LIKE '%formula%' OR c.column_name LIKE '%expression%' THEN 'mapping_formula'
        WHEN c.column_name LIKE '%id' OR c.column_name IN ('run_id','mapping_id','variable_key') THEN 'identifier'
        ELSE 'technical_descriptor'
    END AS semantic_role,
    CASE c.column_name
        WHEN 'mapping_id' THEN 'Mapping-ID'
        WHEN 'mapping_level' THEN 'Mapping-Ebene'
        WHEN 'mapping_name' THEN 'Mapping-Name'
        WHEN 'mapping_formula' THEN 'Mapping-Formel'
        WHEN 'mapping_condition' THEN 'Matching-Bedingung'
        WHEN 'qsb_interpretation' THEN 'QSB-Interpretation'
        WHEN 'dimensional_status' THEN 'Dimensionsstatus'
        WHEN 'physical_claim_release' THEN 'Physik-Claim-Freigabe'
        WHEN 'review_status' THEN 'Review-Status'
        ELSE c.column_name
    END AS display_label_de,
    'Field metadata registered for Scale Mapping Note 01 DWH object ' || c.table_schema || '.' || c.table_name || '.' || c.column_name || '.' AS description,
    CASE
        WHEN c.column_name LIKE '%claim%' OR c.column_name IN ('allowed_claim','forbidden_claim','physical_claim_release','review_status') THEN 'claim_control_field'
        WHEN c.column_name LIKE '%dimension%' THEN 'dimension_control_field'
        ELSE 'metadata_field'
    END AS claim_status,
    'blocked_no_physics_claim' AS physical_claim_release,
    'requires_dimensional_and_physical_review' AS review_status
FROM information_schema.columns c
JOIN qsb_metadata.scale_mapping_note01_catalog_object o
    ON o.object_qualified_name = c.table_schema || '.' || c.table_name
WHERE c.table_schema = 'qsb_scale_mapping'
ON CONFLICT (object_qualified_name, field_name) DO UPDATE SET
    data_type = EXCLUDED.data_type,
    qsb_domain = EXCLUDED.qsb_domain,
    semantic_role = EXCLUDED.semantic_role,
    display_label_de = EXCLUDED.display_label_de,
    description = EXCLUDED.description,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;

INSERT INTO qsb_metadata.scale_mapping_note01_lineage_edge VALUES
('SM-LIN-001', 'artifact:QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01.md', 'qsb_scale_mapping.scale_mapping_run', 'note_to_run_manifest', 'Registers note hash, counts, and claim boundary.', 'lineage_registered', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('SM-LIN-002', 'data:scale_mapping_definitions.csv', 'qsb_scale_mapping.mapping_definition', 'definition_import', 'Registers the two mapping definitions beta_B and Xi_CS.', 'lineage_registered', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('SM-LIN-003', 'data:scale_mapping_variable_registry.csv', 'qsb_scale_mapping.variable_registry', 'variable_registration', 'Registers dimensions and semantic roles of variables.', 'lineage_registered', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('SM-LIN-004', 'data:scale_mapping_claim_boundaries.csv', 'qsb_scale_mapping.claim_boundary', 'claim_boundary_registration', 'Registers allowed and forbidden claims for mappings.', 'lineage_registered', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('SM-LIN-005', 'sql:validate_planck_bridge_scale_mapping_note01_import.sql', 'qsb_scale_mapping.scale_mapping_validation_result', 'validation_to_registry', 'Registers import and dimensional validation outcomes.', 'lineage_registered', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review'),
('SM-LIN-006', 'qsb_scale_mapping.*', 'qsb_metadata.scale_mapping_note01_*', 'metadata_integration', 'Registers catalog, field metadata, lineage and claim boundary metadata.', 'lineage_registered', 'blocked_no_physics_claim', 'requires_dimensional_and_physical_review')
ON CONFLICT (lineage_edge_id) DO UPDATE SET
    source_ref = EXCLUDED.source_ref,
    target_ref = EXCLUDED.target_ref,
    transformation_role = EXCLUDED.transformation_role,
    description = EXCLUDED.description,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;

INSERT INTO qsb_metadata.scale_mapping_note01_claim_boundary_metadata
(boundary_id, scope_type, scope_key, allowed_claim, forbidden_claim, claim_status, physical_claim_release, review_status)
SELECT claim_boundary_id, scope_type, scope_key, allowed_claim, forbidden_claim, claim_status, physical_claim_release, review_status
FROM qsb_scale_mapping.claim_boundary
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-IMPORT-01'
ON CONFLICT (boundary_id) DO UPDATE SET
    allowed_claim = EXCLUDED.allowed_claim,
    forbidden_claim = EXCLUDED.forbidden_claim,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status;

UPDATE qsb_metadata.scale_mapping_note01_metadata_integration_run
SET
    field_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_field_metadata),
    lineage_edge_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_lineage_edge),
    claim_boundary_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata),
    validation_result_count = (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_validation_result)
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01';

CREATE OR REPLACE VIEW qsb_metadata.v_planck_bridge_scale_mapping_note01_metadata_search AS
SELECT
    'catalog_object' AS metadata_scope,
    object_qualified_name AS qualified_name,
    NULL::text AS field_name,
    object_type,
    qsb_domain,
    semantic_role,
    description,
    lineage_note,
    claim_status,
    physical_claim_release,
    review_status,
    concat_ws(' | ', object_qualified_name, object_type, qsb_domain, semantic_role, description, lineage_note, claim_status, physical_claim_release, review_status) AS search_text
FROM qsb_metadata.scale_mapping_note01_catalog_object
UNION ALL
SELECT
    'field', object_qualified_name, field_name, 'field', qsb_domain, semantic_role, description, NULL::text,
    claim_status, physical_claim_release, review_status,
    concat_ws(' | ', object_qualified_name, field_name, data_type, qsb_domain, semantic_role, display_label_de, description, claim_status, physical_claim_release, review_status)
FROM qsb_metadata.scale_mapping_note01_field_metadata
UNION ALL
SELECT
    'claim_boundary', scope_key, NULL::text, scope_type, 'scale_mapping_claim_boundary', 'claim_boundary', allowed_claim, NULL::text,
    claim_status, physical_claim_release, review_status,
    concat_ws(' | ', scope_type, scope_key, allowed_claim, forbidden_claim, claim_status, physical_claim_release, review_status)
FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata
UNION ALL
SELECT
    'lineage', target_ref, NULL::text, 'lineage_edge', 'scale_mapping_lineage', transformation_role, description, source_ref || ' -> ' || target_ref,
    claim_status, physical_claim_release, review_status,
    concat_ws(' | ', source_ref, target_ref, transformation_role, description, claim_status, physical_claim_release, review_status)
FROM qsb_metadata.scale_mapping_note01_lineage_edge;

CREATE OR REPLACE VIEW qsb_metadata.v_planck_bridge_scale_mapping_note01_metadata_dashboard AS
SELECT
    r.integration_run_id,
    r.source_run_id,
    r.work_package,
    r.metadata_scope,
    (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_catalog_object) AS object_count,
    (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_field_metadata) AS field_count,
    (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_lineage_edge) AS lineage_edge_count,
    (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_claim_boundary_metadata) AS claim_boundary_count,
    (SELECT count(*) FROM qsb_metadata.scale_mapping_note01_validation_result) AS validation_result_count,
    r.physical_claim_status,
    r.review_status,
    r.all_metadata_validations_passed,
    r.claim_boundary
FROM qsb_metadata.scale_mapping_note01_metadata_integration_run r
WHERE r.integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-SCALE-MAPPING-NOTE01-METADATA-INTEGRATION-01';

COMMIT;
