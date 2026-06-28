PRAGMA foreign_keys = ON;

CREATE TABLE meta_mart (
    mart_id TEXT PRIMARY KEY,
    mart_code TEXT NOT NULL UNIQUE,
    canonical_namespace TEXT NOT NULL UNIQUE CHECK (canonical_namespace = lower(canonical_namespace)),
    mart_name TEXT NOT NULL,
    scope_status TEXT NOT NULL,
    schema_version TEXT NOT NULL
);

CREATE TABLE meta_work_package (
    work_package_id TEXT PRIMARY KEY,
    mart_id TEXT NOT NULL REFERENCES meta_mart(mart_id),
    work_package_code TEXT NOT NULL UNIQUE,
    canonical_namespace TEXT NOT NULL UNIQUE CHECK (canonical_namespace = lower(canonical_namespace)),
    work_package_name TEXT NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE meta_source (
    source_id TEXT PRIMARY KEY,
    mart_id TEXT NOT NULL REFERENCES meta_mart(mart_id),
    source_type TEXT NOT NULL,
    source_reference TEXT NOT NULL,
    source_record_id_status TEXT NOT NULL
);

CREATE TABLE meta_object (
    object_id TEXT PRIMARY KEY,
    mart_id TEXT NOT NULL REFERENCES meta_mart(mart_id),
    work_package_id TEXT REFERENCES meta_work_package(work_package_id),
    object_code TEXT NOT NULL,
    object_type TEXT NOT NULL,
    canonical_name TEXT NOT NULL,
    repository_path TEXT,
    status TEXT NOT NULL,
    UNIQUE (mart_id, object_code)
);

CREATE TABLE meta_object_version (
    object_version_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES meta_object(object_id),
    object_version TEXT NOT NULL,
    schema_version TEXT,
    content_checksum TEXT,
    status TEXT NOT NULL,
    UNIQUE (object_id, object_version)
);

CREATE TABLE meta_transformation_rule (
    transformation_rule_id TEXT PRIMARY KEY,
    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    input_semantics TEXT NOT NULL,
    output_semantics TEXT NOT NULL,
    expression TEXT,
    source_unit_id TEXT,
    calculation_unit_id TEXT,
    dimension_vector TEXT,
    CHECK (rule_type <> 'unit_conversion' OR (source_unit_id IS NOT NULL AND calculation_unit_id IS NOT NULL))
);

CREATE TABLE meta_unit (
    unit_id TEXT PRIMARY KEY,
    unit_symbol TEXT NOT NULL,
    unit_name TEXT NOT NULL,
    unit_system TEXT NOT NULL,
    scale_to_coherent_si REAL,
    coherent_si_unit_id TEXT,
    is_coherent_si INTEGER NOT NULL CHECK (is_coherent_si IN (0, 1)),
    unit_status TEXT NOT NULL,
    CHECK (unit_status = 'model_unit_unmapped' OR coherent_si_unit_id IS NOT NULL)
);

CREATE TABLE meta_quantity_kind (
    quantity_kind_id TEXT PRIMARY KEY,
    quantity_kind TEXT NOT NULL UNIQUE,
    german_label TEXT,
    dimension_vector TEXT,
    dimension_status TEXT NOT NULL,
    CHECK (dimension_status <> 'resolved' OR dimension_vector IS NOT NULL)
);

CREATE TABLE meta_field (
    field_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES meta_object(object_id),
    canonical_field_name TEXT NOT NULL,
    data_type TEXT NOT NULL,
    nullable INTEGER NOT NULL CHECK (nullable IN (0, 1)),
    key_role TEXT NOT NULL,
    derivation_class TEXT NOT NULL CHECK (derivation_class IN (
        'direct_copy', 'renamed_copy', 'unit_conversion', 'normalized_value',
        'derived_expression', 'constant_with_rule', 'lookup_mapping',
        'aggregation', 'classification', 'presentation_alias'
    )),
    dependency_status TEXT NOT NULL CHECK (dependency_status IN ('declared', 'not_applicable', 'missing')),
    source_object_ids TEXT,
    source_field_ids TEXT,
    transformation_rule_id TEXT REFERENCES meta_transformation_rule(transformation_rule_id),
    quantity_kind_id TEXT REFERENCES meta_quantity_kind(quantity_kind_id),
    unit_original_id TEXT REFERENCES meta_unit(unit_id),
    unit_calculation_id TEXT REFERENCES meta_unit(unit_id),
    unit_display_id TEXT REFERENCES meta_unit(unit_id),
    dimension_vector TEXT,
    unit_status TEXT NOT NULL,
    dimension_status TEXT NOT NULL,
    UNIQUE (object_id, canonical_field_name),
    CHECK (derivation_class = 'presentation_alias' OR quantity_kind_id IS NOT NULL),
    CHECK (derivation_class <> 'derived_expression' OR dependency_status = 'declared'),
    CHECK (unit_status = 'model_unit_unmapped' OR unit_calculation_id IS NOT NULL),
    CHECK (dimension_status LIKE '%unmapped' OR dimension_vector IS NOT NULL)
);

CREATE TABLE meta_key (
    key_id TEXT PRIMARY KEY,
    object_id TEXT NOT NULL REFERENCES meta_object(object_id),
    key_name TEXT NOT NULL,
    key_type TEXT NOT NULL CHECK (key_type IN ('primary', 'foreign', 'unique', 'natural', 'surrogate')),
    field_order TEXT NOT NULL,
    referenced_object_id TEXT REFERENCES meta_object(object_id),
    identity_scope TEXT NOT NULL,
    CHECK (key_type <> 'foreign' OR referenced_object_id IS NOT NULL)
);

CREATE TABLE meta_etl_run (
    run_id TEXT PRIMARY KEY,
    work_package_id TEXT NOT NULL REFERENCES meta_work_package(work_package_id),
    runner_path TEXT NOT NULL,
    run_status TEXT NOT NULL,
    execution_identity_note TEXT NOT NULL
);

CREATE TABLE meta_validation_rule (
    validation_rule_id TEXT PRIMARY KEY,
    validation_layer TEXT NOT NULL CHECK (validation_layer IN (
        'schema', 'syntax', 'referential_integrity', 'unit_conversion',
        'unit_algebra', 'dimension', 'formal_mathematics', 'numerical',
        'physical_assumption', 'physical_boundary_condition',
        'physical_plausibility', 'evidence', 'claim_boundary'
    )),
    rule_name TEXT NOT NULL,
    expected_condition TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical'))
);

CREATE TABLE meta_validation_result (
    validation_result_id TEXT PRIMARY KEY,
    validation_rule_id TEXT NOT NULL REFERENCES meta_validation_rule(validation_rule_id),
    run_id TEXT NOT NULL REFERENCES meta_etl_run(run_id),
    object_id TEXT NOT NULL REFERENCES meta_object(object_id),
    field_id TEXT REFERENCES meta_field(field_id),
    record_id TEXT,
    status TEXT NOT NULL CHECK (status IN ('passed', 'failed', 'warning', 'not_applicable', 'not_tested', 'requires_human_review')),
    observed_value TEXT,
    expected_value TEXT,
    severity TEXT NOT NULL CHECK (severity IN ('info', 'warning', 'error', 'critical')),
    message TEXT NOT NULL,
    reviewer_type TEXT NOT NULL,
    human_review_state TEXT NOT NULL
);

CREATE TABLE meta_lineage (
    lineage_id TEXT PRIMARY KEY,
    mart_id TEXT NOT NULL REFERENCES meta_mart(mart_id),
    source_object_id TEXT NOT NULL,
    target_object_id TEXT NOT NULL REFERENCES meta_object(object_id),
    source_field_id TEXT,
    target_field_id TEXT REFERENCES meta_field(field_id),
    run_id TEXT NOT NULL REFERENCES meta_etl_run(run_id),
    transformation_rule_id TEXT REFERENCES meta_transformation_rule(transformation_rule_id),
    lineage_scope TEXT NOT NULL CHECK (lineage_scope IN ('object', 'field', 'record')),
    lineage_status TEXT NOT NULL CHECK (lineage_status IN ('available', 'not_available', 'not_implemented', 'requires_human_review')),
    CHECK (lineage_scope <> 'field' OR target_field_id IS NOT NULL)
);

CREATE TABLE meta_record_lineage (
    record_lineage_id TEXT PRIMARY KEY,
    lineage_id TEXT NOT NULL REFERENCES meta_lineage(lineage_id),
    lineage_mode TEXT NOT NULL CHECK (lineage_mode IN ('materialized', 'reconstructable', 'aggregate_membership', 'not_applicable')),
    source_record_key TEXT,
    target_record_key TEXT,
    selection_predicate TEXT,
    membership_checksum TEXT,
    CHECK (lineage_mode <> 'materialized' OR (source_record_key IS NOT NULL AND target_record_key IS NOT NULL)),
    CHECK (lineage_mode <> 'aggregate_membership' OR (selection_predicate IS NOT NULL OR source_record_key IS NOT NULL))
);

CREATE TABLE meta_result_table (
    result_table_id TEXT PRIMARY KEY,
    mart_id TEXT NOT NULL REFERENCES meta_mart(mart_id),
    object_id TEXT NOT NULL REFERENCES meta_object(object_id),
    table_role TEXT NOT NULL,
    record_lineage_mode TEXT NOT NULL CHECK (record_lineage_mode IN ('materialized', 'reconstructable', 'aggregate_membership', 'not_applicable')),
    status TEXT NOT NULL,
    CHECK (record_lineage_mode <> 'not_applicable')
);

CREATE TABLE meta_result_record (
    result_record_id TEXT PRIMARY KEY,
    result_table_id TEXT NOT NULL REFERENCES meta_result_table(result_table_id),
    mart_id TEXT NOT NULL REFERENCES meta_mart(mart_id),
    source_result_key TEXT NOT NULL,
    result_class TEXT NOT NULL CHECK (result_class IN ('supports', 'neutral', 'contradicts', 'inconclusive', 'not_comparable', 'invalidated')),
    comparability_status TEXT NOT NULL,
    formal_validation_status TEXT NOT NULL,
    physical_validation_status TEXT NOT NULL,
    evidence_class TEXT NOT NULL CHECK (evidence_class IN ('supports', 'neutral', 'contradicts', 'inconclusive', 'not_comparable', 'invalidated'))
);

CREATE TABLE meta_claim (
    claim_id TEXT PRIMARY KEY,
    mart_id TEXT NOT NULL REFERENCES meta_mart(mart_id),
    claim_text TEXT NOT NULL,
    claim_scope TEXT NOT NULL,
    claim_status TEXT NOT NULL CHECK (claim_status IN ('draft', 'bounded', 'rejected', 'requires_human_review', 'draft_without_evidence')),
    boundary_statement TEXT NOT NULL
);

CREATE TABLE meta_claim_result_link (
    claim_result_link_id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL REFERENCES meta_claim(claim_id),
    result_record_id TEXT NOT NULL REFERENCES meta_result_record(result_record_id),
    relation_type TEXT NOT NULL CHECK (relation_type IN ('supports', 'contradicts', 'qualifies', 'limits', 'context_only')),
    link_status TEXT NOT NULL
);

CREATE TABLE meta_vocabulary (
    vocabulary_id TEXT PRIMARY KEY,
    vocabulary_name TEXT NOT NULL UNIQUE,
    namespace_owner TEXT NOT NULL,
    vocabulary_version TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'deprecated', 'rejected'))
);

CREATE TABLE meta_vocabulary_entry (
    vocabulary_entry_id TEXT PRIMARY KEY,
    vocabulary_id TEXT NOT NULL REFERENCES meta_vocabulary(vocabulary_id),
    canonical_code TEXT NOT NULL,
    english_label TEXT NOT NULL,
    german_alias TEXT,
    definition TEXT NOT NULL,
    entry_status TEXT NOT NULL CHECK (entry_status IN ('draft', 'active', 'deprecated', 'rejected')),
    introduced_version TEXT NOT NULL,
    deprecated_version TEXT,
    replacement_code TEXT,
    human_review_status TEXT NOT NULL,
    UNIQUE (vocabulary_id, canonical_code),
    CHECK (entry_status <> 'active' OR human_review_status <> 'auto_detected')
);

CREATE TABLE meta_alias (
    alias_id TEXT PRIMARY KEY,
    canonical_object_type TEXT NOT NULL,
    canonical_object_id TEXT NOT NULL,
    language_code TEXT NOT NULL,
    alias_text TEXT NOT NULL,
    presentation_scope TEXT NOT NULL,
    CHECK (language_code <> ''),
    UNIQUE (canonical_object_type, canonical_object_id, language_code, presentation_scope)
);
