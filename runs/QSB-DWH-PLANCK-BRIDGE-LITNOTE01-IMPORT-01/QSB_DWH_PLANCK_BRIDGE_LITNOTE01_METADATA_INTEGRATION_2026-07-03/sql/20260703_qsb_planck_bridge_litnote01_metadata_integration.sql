-- QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01
-- Non-destructive PostgreSQL metadata integration for QSB Literature Note 01.
-- Purpose: register qsb_literature.* objects, fields, lineage, claim boundaries, and validation metadata.
-- Claim boundary: metadata integration only; no physics claims are released.

BEGIN;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'qsb_literature' AND table_name = 'reference_source'
    ) THEN
        RAISE EXCEPTION 'Required table qsb_literature.reference_source not found. Run the literature import first.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'qsb_literature' AND table_name = 'reference_claim_map'
    ) THEN
        RAISE EXCEPTION 'Required table qsb_literature.reference_claim_map not found. Run the literature import first.';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = 'qsb_literature' AND table_name = 'litnote_run'
    ) THEN
        RAISE EXCEPTION 'Required table qsb_literature.litnote_run not found. Run the literature import first.';
    END IF;
END $$;

CREATE SCHEMA IF NOT EXISTS qsb_metadata;

CREATE TABLE IF NOT EXISTS qsb_metadata.litnote01_metadata_integration_run (
    integration_run_id TEXT PRIMARY KEY,
    source_run_id TEXT NOT NULL,
    work_package TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata_scope TEXT NOT NULL,
    source_schema TEXT NOT NULL,
    target_schema TEXT NOT NULL,
    object_count INTEGER NOT NULL,
    expected_object_count INTEGER NOT NULL,
    field_count INTEGER NOT NULL DEFAULT 0,
    lineage_edge_count INTEGER NOT NULL DEFAULT 0,
    claim_boundary_count INTEGER NOT NULL DEFAULT 0,
    validation_result_count INTEGER NOT NULL DEFAULT 0,
    physical_claim_status TEXT NOT NULL CHECK (physical_claim_status IN ('blocked_no_physics_claim','review_required','released')),
    review_status TEXT NOT NULL,
    claim_boundary TEXT NOT NULL,
    integration_note TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qsb_metadata.litnote01_catalog_object (
    object_key TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL REFERENCES qsb_metadata.litnote01_metadata_integration_run(integration_run_id) ON UPDATE CASCADE,
    source_run_id TEXT NOT NULL,
    work_package TEXT NOT NULL,
    object_schema TEXT NOT NULL,
    object_name TEXT NOT NULL,
    object_qualified_name TEXT NOT NULL,
    object_type TEXT NOT NULL,
    qsb_domain TEXT NOT NULL,
    object_role TEXT NOT NULL,
    description TEXT NOT NULL,
    claim_status TEXT NOT NULL,
    physical_claim_release TEXT NOT NULL CHECK (physical_claim_release = 'blocked_no_physics_claim'),
    review_status TEXT NOT NULL,
    lineage_note TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (object_schema, object_name)
);

CREATE TABLE IF NOT EXISTS qsb_metadata.litnote01_field_metadata (
    field_key TEXT PRIMARY KEY,
    object_key TEXT NOT NULL REFERENCES qsb_metadata.litnote01_catalog_object(object_key) ON UPDATE CASCADE,
    integration_run_id TEXT NOT NULL REFERENCES qsb_metadata.litnote01_metadata_integration_run(integration_run_id) ON UPDATE CASCADE,
    object_qualified_name TEXT NOT NULL,
    column_name TEXT NOT NULL,
    ordinal_position INTEGER NOT NULL,
    data_type TEXT NOT NULL,
    is_nullable TEXT NOT NULL,
    semantic_role TEXT NOT NULL,
    canonical_label_de TEXT NOT NULL,
    description TEXT NOT NULL,
    is_identifier BOOLEAN NOT NULL DEFAULT FALSE,
    is_lineage_field BOOLEAN NOT NULL DEFAULT FALSE,
    is_claim_control_field BOOLEAN NOT NULL DEFAULT FALSE,
    is_source_reference_field BOOLEAN NOT NULL DEFAULT FALSE,
    physical_claim_release TEXT NOT NULL CHECK (physical_claim_release = 'blocked_no_physics_claim'),
    review_status TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (object_qualified_name, column_name)
);

CREATE TABLE IF NOT EXISTS qsb_metadata.litnote01_lineage_edge (
    lineage_edge_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL REFERENCES qsb_metadata.litnote01_metadata_integration_run(integration_run_id) ON UPDATE CASCADE,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,
    transformation_type TEXT NOT NULL,
    transformation_note TEXT NOT NULL,
    source_run_id TEXT NOT NULL,
    work_package TEXT NOT NULL,
    physical_claim_release TEXT NOT NULL CHECK (physical_claim_release = 'blocked_no_physics_claim'),
    review_status TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS qsb_metadata.litnote01_claim_boundary_metadata (
    boundary_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL REFERENCES qsb_metadata.litnote01_metadata_integration_run(integration_run_id) ON UPDATE CASCADE,
    scope_type TEXT NOT NULL,
    scope_key TEXT NOT NULL,
    scope_label TEXT NOT NULL,
    allowed_claim_scope TEXT NOT NULL,
    forbidden_claim_scope TEXT NOT NULL,
    qsb_connection_scope TEXT NOT NULL,
    physical_claim_release TEXT NOT NULL CHECK (physical_claim_release = 'blocked_no_physics_claim'),
    review_status TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (scope_type, scope_key)
);

CREATE TABLE IF NOT EXISTS qsb_metadata.litnote01_validation_result (
    validation_id TEXT PRIMARY KEY,
    integration_run_id TEXT NOT NULL REFERENCES qsb_metadata.litnote01_metadata_integration_run(integration_run_id) ON UPDATE CASCADE,
    validation_scope TEXT NOT NULL,
    check_name TEXT NOT NULL,
    expected_value TEXT NOT NULL,
    actual_value TEXT NOT NULL,
    passed BOOLEAN NOT NULL,
    severity TEXT NOT NULL,
    validation_note TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO qsb_metadata.litnote01_metadata_integration_run (
    integration_run_id, source_run_id, work_package, created_at, metadata_scope,
    source_schema, target_schema, object_count, expected_object_count,
    physical_claim_status, review_status, claim_boundary, integration_note
) VALUES (
    'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01',
    'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01',
    'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01',
    '2026-07-03T00:00:00+02:00',
    'literature_note_01_bibliography_claim_mapping',
    'qsb_literature',
    'qsb_metadata',
    4,
    4,
    'blocked_no_physics_claim',
    'registered_requires_human_literature_review',
    'Metadata integration registers literature provenance and claim boundaries only; it does not release physics claims.',
    'Registers catalog objects, fields, lineage, claim boundaries, validation results, and metadata search views for Literature Note 01.'
)
ON CONFLICT (integration_run_id) DO UPDATE SET
    object_count = EXCLUDED.object_count,
    expected_object_count = EXCLUDED.expected_object_count,
    physical_claim_status = EXCLUDED.physical_claim_status,
    review_status = EXCLUDED.review_status,
    claim_boundary = EXCLUDED.claim_boundary,
    integration_note = EXCLUDED.integration_note,
    registered_at = NOW();

INSERT INTO qsb_metadata.litnote01_catalog_object (
    object_key, integration_run_id, source_run_id, work_package,
    object_schema, object_name, object_qualified_name, object_type,
    qsb_domain, object_role, description, claim_status, physical_claim_release,
    review_status, lineage_note
) VALUES
('qsb_literature.litnote_run', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'qsb_literature', 'litnote_run', 'qsb_literature.litnote_run', 'table', 'literature_metadata', 'run_manifest', 'Run-level manifest for Literature Note 01 import, including source hash, counts, and claim boundary.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review', 'Derived from literature_run_manifest.json and qsb_planck_bridge_resonator_litnote01.bib.'),
('qsb_literature.reference_source', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'qsb_literature', 'reference_source', 'qsb_literature.reference_source', 'table', 'literature_metadata', 'bibliographic_source_registry', 'Bibliographic source registry for Planck Bridge Literature Note 01.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review', 'Derived from literature_sources.csv and BibTeX source file.'),
('qsb_literature.reference_claim_map', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'qsb_literature', 'reference_claim_map', 'qsb_literature.reference_claim_map', 'table', 'literature_metadata', 'claim_boundary_registry', 'Reference-level mapping of supported, unsupported, allowed, and forbidden claim scopes.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review', 'Derived from literature_claim_map.csv.'),
('qsb_literature.v_planck_bridge_litnote01_claim_boundary', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'qsb_literature', 'v_planck_bridge_litnote01_claim_boundary', 'qsb_literature.v_planck_bridge_litnote01_claim_boundary', 'view', 'literature_metadata', 'claim_boundary_review_view', 'Human-readable review view joining literature sources with claim boundaries and review status.', 'metadata_registration_only', 'blocked_no_physics_claim', 'registered_requires_human_literature_review', 'Derived by joining qsb_literature.reference_source and qsb_literature.reference_claim_map.')
ON CONFLICT (object_key) DO UPDATE SET
    object_role = EXCLUDED.object_role,
    description = EXCLUDED.description,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status,
    lineage_note = EXCLUDED.lineage_note,
    registered_at = NOW();

INSERT INTO qsb_metadata.litnote01_field_metadata (
    field_key, object_key, integration_run_id, object_qualified_name,
    column_name, ordinal_position, data_type, is_nullable, semantic_role,
    canonical_label_de, description, is_identifier, is_lineage_field,
    is_claim_control_field, is_source_reference_field, physical_claim_release, review_status
)
SELECT
    c.table_schema || '.' || c.table_name || '.' || c.column_name AS field_key,
    c.table_schema || '.' || c.table_name AS object_key,
    'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01' AS integration_run_id,
    c.table_schema || '.' || c.table_name AS object_qualified_name,
    c.column_name,
    c.ordinal_position,
    c.data_type,
    c.is_nullable,
    CASE
        WHEN c.column_name IN ('run_id','work_package','bib_key','claim_map_id','pillar_id') THEN 'identifier'
        WHEN c.column_name IN ('source_file','source_sha256','source_bib_file','lineage_note','registered_at','created_at') THEN 'lineage'
        WHEN c.column_name IN ('claim_status','physical_claim_release','physical_claim_status','review_status','claim_boundary','allowed_claim','forbidden_claim','supports','does_not_support','qsb_connection') THEN 'claim_boundary_control'
        WHEN c.column_name IN ('title','authors','year','journal','booktitle','publisher','doi','arxiv_id','url','isbn','keywords','note') THEN 'bibliographic_descriptor'
        ELSE 'technical_descriptor'
    END AS semantic_role,
    CASE c.column_name
        WHEN 'run_id' THEN 'Run-ID'
        WHEN 'work_package' THEN 'Arbeitspaket'
        WHEN 'bib_key' THEN 'BibTeX-Schlüssel'
        WHEN 'claim_map_id' THEN 'Claim-Mapping-ID'
        WHEN 'pillar_id' THEN 'Literatursäulen-ID'
        WHEN 'pillar_label' THEN 'Literatursäule'
        WHEN 'title' THEN 'Titel'
        WHEN 'authors' THEN 'Autorinnen/Autoren'
        WHEN 'year' THEN 'Jahr'
        WHEN 'journal' THEN 'Zeitschrift'
        WHEN 'booktitle' THEN 'Buchtitel/Sammelband'
        WHEN 'publisher' THEN 'Verlag'
        WHEN 'doi' THEN 'DOI'
        WHEN 'arxiv_id' THEN 'arXiv-ID'
        WHEN 'url' THEN 'URL'
        WHEN 'keywords' THEN 'Schlagworte'
        WHEN 'supports' THEN 'Stützt'
        WHEN 'does_not_support' THEN 'Stützt nicht'
        WHEN 'qsb_connection' THEN 'QSB-Anschluss'
        WHEN 'allowed_claim' THEN 'Erlaubter Claim'
        WHEN 'forbidden_claim' THEN 'Verbotener Claim'
        WHEN 'claim_status' THEN 'Claim-Status'
        WHEN 'physical_claim_release' THEN 'Physik-Claim-Freigabe'
        WHEN 'review_status' THEN 'Review-Status'
        WHEN 'source_file' THEN 'Quelldatei'
        WHEN 'source_sha256' THEN 'Quell-SHA256'
        ELSE c.column_name
    END AS canonical_label_de,
    'Field metadata registered for Literature Note 01 DWH object ' || c.table_schema || '.' || c.table_name || '.' || c.column_name || '.' AS description,
    (c.column_name IN ('run_id','work_package','bib_key','claim_map_id','pillar_id')) AS is_identifier,
    (c.column_name IN ('source_file','source_sha256','source_bib_file','lineage_note','registered_at','created_at')) AS is_lineage_field,
    (c.column_name IN ('claim_status','physical_claim_release','physical_claim_status','review_status','claim_boundary','allowed_claim','forbidden_claim','supports','does_not_support','qsb_connection')) AS is_claim_control_field,
    (c.column_name IN ('doi','arxiv_id','url','isbn','source_file','source_sha256')) AS is_source_reference_field,
    'blocked_no_physics_claim' AS physical_claim_release,
    'registered_requires_human_literature_review' AS review_status
FROM information_schema.columns c
WHERE c.table_schema = 'qsb_literature'
  AND c.table_name IN ('litnote_run', 'reference_source', 'reference_claim_map', 'v_planck_bridge_litnote01_claim_boundary')
ON CONFLICT (field_key) DO UPDATE SET
    ordinal_position = EXCLUDED.ordinal_position,
    data_type = EXCLUDED.data_type,
    is_nullable = EXCLUDED.is_nullable,
    semantic_role = EXCLUDED.semantic_role,
    canonical_label_de = EXCLUDED.canonical_label_de,
    description = EXCLUDED.description,
    is_identifier = EXCLUDED.is_identifier,
    is_lineage_field = EXCLUDED.is_lineage_field,
    is_claim_control_field = EXCLUDED.is_claim_control_field,
    is_source_reference_field = EXCLUDED.is_source_reference_field,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status,
    registered_at = NOW();

INSERT INTO qsb_metadata.litnote01_lineage_edge (
    lineage_edge_id, integration_run_id, source_node, target_node,
    transformation_type, transformation_note, source_run_id, work_package,
    physical_claim_release, review_status
) VALUES
('LITNOTE01-LIN-001', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'artifact:qsb_planck_bridge_resonator_litnote01.bib', 'qsb_literature.litnote_run', 'manifest_registration', 'Registers source BibTeX file, SHA256, expected counts, and claim boundary.', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('LITNOTE01-LIN-002', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'artifact:literature_sources.csv', 'qsb_literature.reference_source', 'csv_to_dwh_reference_registry', 'Loads bibliographic source rows into DWH reference registry.', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('LITNOTE01-LIN-003', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'artifact:literature_claim_map.csv', 'qsb_literature.reference_claim_map', 'csv_to_dwh_claim_boundary_registry', 'Loads claim-mapping rows into DWH claim-boundary registry.', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('LITNOTE01-LIN-004', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'qsb_literature.reference_source + qsb_literature.reference_claim_map', 'qsb_literature.v_planck_bridge_litnote01_claim_boundary', 'relational_view_join', 'Joins source registry and claim map for human review of allowed/forbidden claims.', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'blocked_no_physics_claim', 'registered_requires_human_literature_review'),
('LITNOTE01-LIN-005', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'sql:validate_planck_bridge_litnote01_import.sql', 'qsb_metadata.litnote01_validation_result', 'validation_to_metadata_registry', 'Registers metadata validation outcomes for audit and global search.', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'blocked_no_physics_claim', 'registered_requires_human_literature_review')
ON CONFLICT (lineage_edge_id) DO UPDATE SET
    transformation_note = EXCLUDED.transformation_note,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status,
    registered_at = NOW();

INSERT INTO qsb_metadata.litnote01_claim_boundary_metadata (
    boundary_id, integration_run_id, scope_type, scope_key, scope_label,
    allowed_claim_scope, forbidden_claim_scope, qsb_connection_scope,
    physical_claim_release, review_status
) VALUES (
    'LITNOTE01-BOUNDARY-GLOBAL',
    'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01',
    'work_package',
    'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01',
    'Literature Note 01 global claim boundary',
    'The literature may motivate the interface question and structure the QSB search space.',
    'The literature does not prove the existence of a Planck-Bridge-Resonator and does not release physics claims.',
    'QSB registers the Planck-Bridge-Resonator as a formal, testable interface candidate only.',
    'blocked_no_physics_claim',
    'registered_requires_human_literature_review'
)
ON CONFLICT (scope_type, scope_key) DO UPDATE SET
    allowed_claim_scope = EXCLUDED.allowed_claim_scope,
    forbidden_claim_scope = EXCLUDED.forbidden_claim_scope,
    qsb_connection_scope = EXCLUDED.qsb_connection_scope,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status,
    registered_at = NOW();

INSERT INTO qsb_metadata.litnote01_claim_boundary_metadata (
    boundary_id, integration_run_id, scope_type, scope_key, scope_label,
    allowed_claim_scope, forbidden_claim_scope, qsb_connection_scope,
    physical_claim_release, review_status
)
SELECT
    'LITNOTE01-BOUNDARY-PILLAR-' || regexp_replace(lower(s.pillar_id), '[^a-z0-9_]+', '_', 'g') AS boundary_id,
    'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01' AS integration_run_id,
    'literature_pillar' AS scope_type,
    s.pillar_id AS scope_key,
    s.pillar_label AS scope_label,
    string_agg(DISTINCT c.supports, ' | ' ORDER BY c.supports) AS allowed_claim_scope,
    string_agg(DISTINCT c.does_not_support, ' | ' ORDER BY c.does_not_support) AS forbidden_claim_scope,
    string_agg(DISTINCT c.qsb_connection, ' | ' ORDER BY c.qsb_connection) AS qsb_connection_scope,
    'blocked_no_physics_claim' AS physical_claim_release,
    'registered_requires_human_literature_review' AS review_status
FROM qsb_literature.reference_source s
JOIN qsb_literature.reference_claim_map c USING (bib_key)
WHERE s.run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
GROUP BY s.pillar_id, s.pillar_label
ON CONFLICT (scope_type, scope_key) DO UPDATE SET
    scope_label = EXCLUDED.scope_label,
    allowed_claim_scope = EXCLUDED.allowed_claim_scope,
    forbidden_claim_scope = EXCLUDED.forbidden_claim_scope,
    qsb_connection_scope = EXCLUDED.qsb_connection_scope,
    physical_claim_release = EXCLUDED.physical_claim_release,
    review_status = EXCLUDED.review_status,
    registered_at = NOW();

DELETE FROM qsb_metadata.litnote01_validation_result
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01';

INSERT INTO qsb_metadata.litnote01_validation_result (
    validation_id, integration_run_id, validation_scope, check_name,
    expected_value, actual_value, passed, severity, validation_note
)
SELECT 'LITNOTE01-META-VAL-001', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'source_import', 'source_count_matches_manifest', '14', COUNT(*)::TEXT, COUNT(*) = 14, 'error', 'Reference source count must match Literature Note 01 manifest.'
FROM qsb_literature.reference_source
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
UNION ALL
SELECT 'LITNOTE01-META-VAL-002', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'source_import', 'claim_map_count_matches_manifest', '14', COUNT(*)::TEXT, COUNT(*) = 14, 'error', 'Claim map count must match Literature Note 01 manifest.'
FROM qsb_literature.reference_claim_map
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
UNION ALL
SELECT 'LITNOTE01-META-VAL-003', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'claim_boundary', 'all_references_claim_blocked', 'blocked_no_physics_claim only', COALESCE(string_agg(DISTINCT physical_claim_release, ', '), 'none'), bool_and(physical_claim_release = 'blocked_no_physics_claim'), 'error', 'No reference may release a physics claim.'
FROM qsb_literature.reference_source
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
UNION ALL
SELECT 'LITNOTE01-META-VAL-004', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'metadata_catalog', 'catalog_objects_registered', '4', COUNT(*)::TEXT, COUNT(*) = 4, 'error', 'Four literature DWH objects must be registered in the metadata catalog.'
FROM qsb_metadata.litnote01_catalog_object
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
UNION ALL
SELECT 'LITNOTE01-META-VAL-005', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'metadata_fields', 'fields_registered', '> 0', COUNT(*)::TEXT, COUNT(*) > 0, 'error', 'Field-level metadata must be registered from information_schema.'
FROM qsb_metadata.litnote01_field_metadata
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
UNION ALL
SELECT 'LITNOTE01-META-VAL-006', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'metadata_lineage', 'lineage_edges_registered', '5', COUNT(*)::TEXT, COUNT(*) = 5, 'error', 'Five lineage edges are expected for import, tables, claim view, and validation metadata.'
FROM qsb_metadata.litnote01_lineage_edge
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
UNION ALL
SELECT 'LITNOTE01-META-VAL-007', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01', 'metadata_claim_boundary', 'claim_boundaries_registered', '>= 5', COUNT(*)::TEXT, COUNT(*) >= 5, 'error', 'Global plus pillar-level claim boundaries must be registered.'
FROM qsb_metadata.litnote01_claim_boundary_metadata
WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01';

UPDATE qsb_metadata.litnote01_metadata_integration_run r
SET
    field_count = f.cnt,
    lineage_edge_count = l.cnt,
    claim_boundary_count = b.cnt,
    validation_result_count = v.cnt,
    registered_at = NOW()
FROM
    (SELECT COUNT(*) AS cnt FROM qsb_metadata.litnote01_field_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01') f,
    (SELECT COUNT(*) AS cnt FROM qsb_metadata.litnote01_lineage_edge WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01') l,
    (SELECT COUNT(*) AS cnt FROM qsb_metadata.litnote01_claim_boundary_metadata WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01') b,
    (SELECT COUNT(*) AS cnt FROM qsb_metadata.litnote01_validation_result WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01') v
WHERE r.integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01';

CREATE OR REPLACE VIEW qsb_metadata.v_planck_bridge_litnote01_metadata_search AS
SELECT
    'catalog_object'::TEXT AS metadata_scope,
    o.object_qualified_name AS qualified_name,
    NULL::TEXT AS field_name,
    o.object_type,
    o.qsb_domain,
    o.object_role AS semantic_role,
    o.description AS description,
    o.lineage_note AS lineage_note,
    o.claim_status,
    o.physical_claim_release,
    o.review_status,
    concat_ws(' | ', o.object_qualified_name, o.object_type, o.qsb_domain, o.object_role, o.description, o.lineage_note, o.claim_status, o.physical_claim_release, o.review_status) AS search_text
FROM qsb_metadata.litnote01_catalog_object o
UNION ALL
SELECT
    'field'::TEXT AS metadata_scope,
    f.object_qualified_name AS qualified_name,
    f.column_name AS field_name,
    'field'::TEXT AS object_type,
    'literature_metadata'::TEXT AS qsb_domain,
    f.semantic_role,
    f.description,
    NULL::TEXT AS lineage_note,
    CASE WHEN f.is_claim_control_field THEN 'claim_control_field' ELSE 'metadata_field' END AS claim_status,
    f.physical_claim_release,
    f.review_status,
    concat_ws(' | ', f.object_qualified_name, f.column_name, f.data_type, f.semantic_role, f.canonical_label_de, f.description, f.physical_claim_release, f.review_status) AS search_text
FROM qsb_metadata.litnote01_field_metadata f
UNION ALL
SELECT
    'claim_boundary'::TEXT AS metadata_scope,
    b.scope_key AS qualified_name,
    NULL::TEXT AS field_name,
    b.scope_type AS object_type,
    'literature_claim_boundary'::TEXT AS qsb_domain,
    'claim_boundary'::TEXT AS semantic_role,
    b.scope_label AS description,
    NULL::TEXT AS lineage_note,
    'claim_boundary_registered'::TEXT AS claim_status,
    b.physical_claim_release,
    b.review_status,
    concat_ws(' | ', b.scope_type, b.scope_key, b.scope_label, b.allowed_claim_scope, b.forbidden_claim_scope, b.qsb_connection_scope, b.physical_claim_release, b.review_status) AS search_text
FROM qsb_metadata.litnote01_claim_boundary_metadata b
UNION ALL
SELECT
    'lineage'::TEXT AS metadata_scope,
    e.target_node AS qualified_name,
    NULL::TEXT AS field_name,
    'lineage_edge'::TEXT AS object_type,
    'literature_lineage'::TEXT AS qsb_domain,
    e.transformation_type AS semantic_role,
    e.transformation_note AS description,
    e.source_node || ' -> ' || e.target_node AS lineage_note,
    'lineage_registered'::TEXT AS claim_status,
    e.physical_claim_release,
    e.review_status,
    concat_ws(' | ', e.source_node, e.target_node, e.transformation_type, e.transformation_note, e.physical_claim_release, e.review_status) AS search_text
FROM qsb_metadata.litnote01_lineage_edge e;

CREATE OR REPLACE VIEW qsb_metadata.v_planck_bridge_litnote01_metadata_dashboard AS
SELECT
    r.integration_run_id,
    r.source_run_id,
    r.work_package,
    r.metadata_scope,
    r.object_count,
    r.field_count,
    r.lineage_edge_count,
    r.claim_boundary_count,
    r.validation_result_count,
    r.physical_claim_status,
    r.review_status,
    bool_and(v.passed) AS all_metadata_validations_passed,
    r.claim_boundary
FROM qsb_metadata.litnote01_metadata_integration_run r
LEFT JOIN qsb_metadata.litnote01_validation_result v USING (integration_run_id)
WHERE r.integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
GROUP BY
    r.integration_run_id, r.source_run_id, r.work_package, r.metadata_scope,
    r.object_count, r.field_count, r.lineage_edge_count, r.claim_boundary_count,
    r.validation_result_count, r.physical_claim_status, r.review_status, r.claim_boundary;

DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM qsb_metadata.litnote01_validation_result
        WHERE integration_run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01'
          AND passed = FALSE
          AND severity = 'error'
    ) THEN
        RAISE EXCEPTION 'Metadata integration validation failed. See qsb_metadata.litnote01_validation_result.';
    END IF;
END $$;

COMMIT;
