-- QSB-DB03
-- SQLite research database schema.
-- Generated from QSB-DB02 SQLite Schema Specification.
-- Schema-only, no data.
-- No raw artifact access.
-- No TIM/PAR value reading.
-- No physical interpretation.
-- This database is an audit-capable research-data backbone, not an interpretation engine.
-- Quarantine is preservation, not deletion.
-- Everything is preserved, but not everything is released into analytics.
-- The raw-data layer is not an analytics table.
-- This schema does not provide evidence for a physical Shapiro-information residual.
-- This schema does not validate the QSB-ST Bridge.
-- Physical interpretation, residual analysis, model fitting, and Bridge claims remain gated elsewhere.

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Source and raw-data staging.
CREATE TABLE IF NOT EXISTS raw_data_source (
    raw_data_source_id INTEGER PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    provider_or_project TEXT,
    source_url_or_path TEXT,
    source_release TEXT,
    source_version TEXT,
    source_access_date TEXT,
    source_download_status TEXT NOT NULL DEFAULT 'not_downloaded',
    source_reachability_status TEXT NOT NULL DEFAULT 'unresolved',
    source_corruption_status TEXT NOT NULL DEFAULT 'not_checked',
    checksum_status TEXT NOT NULL DEFAULT 'not_checked',
    license_or_usage_note TEXT,
    provenance_confidence TEXT NOT NULL DEFAULT 'unresolved',
    quarantine_status TEXT NOT NULL DEFAULT 'not_quarantined',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(source_name, source_release, source_version)
);

CREATE INDEX IF NOT EXISTS idx_raw_data_source_name
    ON raw_data_source(source_name);
CREATE INDEX IF NOT EXISTS idx_raw_data_source_provider
    ON raw_data_source(provider_or_project);
CREATE INDEX IF NOT EXISTS idx_raw_data_source_status
    ON raw_data_source(source_download_status, source_reachability_status, quarantine_status);

CREATE TABLE IF NOT EXISTS raw_data (
    raw_data_id INTEGER PRIMARY KEY,
    raw_data_source_id INTEGER NOT NULL,
    raw_artifact_id TEXT,
    source_local_file_id TEXT,
    source_local_record_id TEXT,
    source_local_measurement_id TEXT,
    source_record_hash TEXT,
    raw_record_position TEXT,
    raw_object_type TEXT,
    raw_file_type TEXT,
    raw_ingest_status TEXT NOT NULL DEFAULT 'not_ingested',
    raw_parse_status TEXT NOT NULL DEFAULT 'not_parsed',
    raw_quality_status TEXT NOT NULL DEFAULT 'not_checked',
    blank_check_status TEXT NOT NULL DEFAULT 'not_checked',
    special_character_check_status TEXT NOT NULL DEFAULT 'not_checked',
    datatype_check_status TEXT NOT NULL DEFAULT 'not_checked',
    unit_detection_status TEXT NOT NULL DEFAULT 'not_checked',
    scale_detection_status TEXT NOT NULL DEFAULT 'not_checked',
    harmonization_status TEXT NOT NULL DEFAULT 'not_harmonized',
    etl_release_status TEXT NOT NULL DEFAULT 'not_released',
    quarantine_status TEXT NOT NULL DEFAULT 'not_quarantined',
    quarantine_reason TEXT,
    retry_possible INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (raw_data_source_id) REFERENCES raw_data_source(raw_data_source_id),
    UNIQUE(raw_data_source_id, source_local_file_id, source_local_record_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_data_source
    ON raw_data(raw_data_source_id);
CREATE INDEX IF NOT EXISTS idx_raw_data_artifact
    ON raw_data(raw_artifact_id);
CREATE INDEX IF NOT EXISTS idx_raw_data_status
    ON raw_data(raw_ingest_status, raw_parse_status, harmonization_status, quarantine_status);
CREATE INDEX IF NOT EXISTS idx_raw_data_file_record
    ON raw_data(source_local_file_id, source_local_record_id);

-- Relation catalog.
CREATE TABLE IF NOT EXISTS pk_fk_relation_catalog (
    relation_id INTEGER PRIMARY KEY,
    source_table TEXT NOT NULL,
    source_column TEXT NOT NULL,
    target_table TEXT NOT NULL,
    target_column TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    cardinality TEXT,
    constraint_name TEXT,
    is_enforced INTEGER NOT NULL DEFAULT 1,
    is_logical_only INTEGER NOT NULL DEFAULT 0,
    join_rule TEXT,
    validity_condition TEXT,
    audit_relevance TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_pk_fk_relation
    ON pk_fk_relation_catalog(source_table, source_column, target_table, target_column);
CREATE INDEX IF NOT EXISTS idx_pk_fk_relation_target
    ON pk_fk_relation_catalog(target_table, target_column);
CREATE INDEX IF NOT EXISTS idx_pk_fk_relation_type
    ON pk_fk_relation_catalog(relation_type, is_enforced, is_logical_only);

-- Repository and Git lineage.
CREATE TABLE IF NOT EXISTS repo_catalog (
    repo_id INTEGER PRIMARY KEY,
    repo_name TEXT NOT NULL,
    repo_url TEXT,
    local_root_path TEXT,
    default_branch TEXT,
    project_area TEXT,
    repo_status TEXT NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(repo_name, local_root_path)
);

CREATE INDEX IF NOT EXISTS idx_repo_catalog_url
    ON repo_catalog(repo_url);
CREATE INDEX IF NOT EXISTS idx_repo_catalog_status
    ON repo_catalog(repo_status, project_area);

CREATE TABLE IF NOT EXISTS git_commit_catalog (
    commit_id INTEGER PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    commit_hash TEXT NOT NULL,
    short_hash TEXT,
    commit_message TEXT,
    commit_author TEXT,
    commit_date TEXT,
    branch_name TEXT,
    tag_name TEXT,
    is_clean_state INTEGER NOT NULL DEFAULT 0,
    git_status_snapshot TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_id) REFERENCES repo_catalog(repo_id),
    UNIQUE(repo_id, commit_hash)
);

CREATE INDEX IF NOT EXISTS idx_git_commit_repo
    ON git_commit_catalog(repo_id);
CREATE INDEX IF NOT EXISTS idx_git_commit_short_hash
    ON git_commit_catalog(short_hash);
CREATE INDEX IF NOT EXISTS idx_git_commit_date
    ON git_commit_catalog(commit_date);
CREATE INDEX IF NOT EXISTS idx_git_commit_branch
    ON git_commit_catalog(branch_name, tag_name);

-- Project files and documents.
CREATE TABLE IF NOT EXISTS project_file_catalog (
    project_file_id INTEGER PRIMARY KEY,
    repo_id INTEGER,
    commit_id INTEGER,
    file_path TEXT NOT NULL,
    file_name TEXT,
    file_type TEXT,
    project_role TEXT,
    tracking_status TEXT NOT NULL DEFAULT 'unknown',
    created_by_block TEXT,
    modified_by_block TEXT,
    checksum TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (repo_id) REFERENCES repo_catalog(repo_id),
    FOREIGN KEY (commit_id) REFERENCES git_commit_catalog(commit_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_project_file_repo_path_commit
    ON project_file_catalog(repo_id, file_path, commit_id);
CREATE INDEX IF NOT EXISTS idx_project_file_repo
    ON project_file_catalog(repo_id);
CREATE INDEX IF NOT EXISTS idx_project_file_commit
    ON project_file_catalog(commit_id);
CREATE INDEX IF NOT EXISTS idx_project_file_path
    ON project_file_catalog(file_path);
CREATE INDEX IF NOT EXISTS idx_project_file_role_status
    ON project_file_catalog(project_role, tracking_status);

CREATE TABLE IF NOT EXISTS document_catalog (
    document_id INTEGER PRIMARY KEY,
    project_file_id INTEGER NOT NULL,
    document_title TEXT,
    document_type TEXT,
    qsb_block_id TEXT,
    upstream_block TEXT,
    downstream_block TEXT,
    status TEXT,
    claim_boundary_level TEXT,
    tracking_decision TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (project_file_id) REFERENCES project_file_catalog(project_file_id),
    UNIQUE(project_file_id)
);

CREATE INDEX IF NOT EXISTS idx_document_file
    ON document_catalog(project_file_id);
CREATE INDEX IF NOT EXISTS idx_document_block
    ON document_catalog(qsb_block_id);
CREATE INDEX IF NOT EXISTS idx_document_type_status
    ON document_catalog(document_type, status);
CREATE INDEX IF NOT EXISTS idx_document_claim_boundary
    ON document_catalog(claim_boundary_level);

-- Scripts, runs, outputs, and tables.
CREATE TABLE IF NOT EXISTS script_catalog (
    script_id INTEGER PRIMARY KEY,
    project_file_id INTEGER NOT NULL,
    script_name TEXT,
    script_path TEXT,
    script_language TEXT,
    execution_allowed_status TEXT NOT NULL DEFAULT 'not_reviewed',
    last_known_commit_hash TEXT,
    purpose TEXT,
    claim_boundary TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (project_file_id) REFERENCES project_file_catalog(project_file_id),
    UNIQUE(project_file_id)
);

CREATE INDEX IF NOT EXISTS idx_script_file
    ON script_catalog(project_file_id);
CREATE INDEX IF NOT EXISTS idx_script_path
    ON script_catalog(script_path);
CREATE INDEX IF NOT EXISTS idx_script_name
    ON script_catalog(script_name);
CREATE INDEX IF NOT EXISTS idx_script_execution_status
    ON script_catalog(execution_allowed_status);

CREATE TABLE IF NOT EXISTS run_catalog (
    run_id INTEGER PRIMARY KEY,
    run_block TEXT,
    script_id INTEGER,
    repo_id INTEGER,
    commit_id INTEGER,
    run_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_mode TEXT,
    output_root TEXT,
    run_status TEXT NOT NULL DEFAULT 'not_started',
    git_status_before TEXT,
    git_status_after TEXT,
    raw_access_status TEXT NOT NULL DEFAULT 'not_performed',
    download_status TEXT NOT NULL DEFAULT 'not_performed',
    value_reading_status TEXT NOT NULL DEFAULT 'not_performed',
    claim_boundary_status TEXT NOT NULL DEFAULT 'closed',
    notes TEXT,
    FOREIGN KEY (script_id) REFERENCES script_catalog(script_id),
    FOREIGN KEY (repo_id) REFERENCES repo_catalog(repo_id),
    FOREIGN KEY (commit_id) REFERENCES git_commit_catalog(commit_id)
);

CREATE INDEX IF NOT EXISTS idx_run_block
    ON run_catalog(run_block);
CREATE INDEX IF NOT EXISTS idx_run_script
    ON run_catalog(script_id);
CREATE INDEX IF NOT EXISTS idx_run_repo_commit
    ON run_catalog(repo_id, commit_id);
CREATE INDEX IF NOT EXISTS idx_run_status
    ON run_catalog(run_status, claim_boundary_status);
CREATE INDEX IF NOT EXISTS idx_run_access_gates
    ON run_catalog(raw_access_status, download_status, value_reading_status);

CREATE TABLE IF NOT EXISTS run_output_catalog (
    run_output_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    project_file_id INTEGER,
    output_path TEXT,
    output_type TEXT,
    byte_size INTEGER,
    row_count INTEGER,
    checksum TEXT,
    tracked_status TEXT NOT NULL DEFAULT 'run_artifact',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES run_catalog(run_id),
    FOREIGN KEY (project_file_id) REFERENCES project_file_catalog(project_file_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_run_output_path
    ON run_output_catalog(run_id, output_path);
CREATE INDEX IF NOT EXISTS idx_run_output_run
    ON run_output_catalog(run_id);
CREATE INDEX IF NOT EXISTS idx_run_output_file
    ON run_output_catalog(project_file_id);
CREATE INDEX IF NOT EXISTS idx_run_output_type_status
    ON run_output_catalog(output_type, tracked_status);

CREATE TABLE IF NOT EXISTS table_catalog (
    table_id INTEGER PRIMARY KEY,
    table_name TEXT NOT NULL,
    table_type TEXT,
    storage_type TEXT,
    storage_path TEXT,
    schema_status TEXT NOT NULL DEFAULT 'not_reviewed',
    row_count INTEGER,
    column_count INTEGER,
    created_by_script_id INTEGER,
    created_by_run_id INTEGER,
    source_raw_data_id INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (created_by_script_id) REFERENCES script_catalog(script_id),
    FOREIGN KEY (created_by_run_id) REFERENCES run_catalog(run_id),
    FOREIGN KEY (source_raw_data_id) REFERENCES raw_data(raw_data_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_table_storage
    ON table_catalog(table_name, storage_type, storage_path);
CREATE INDEX IF NOT EXISTS idx_table_name
    ON table_catalog(table_name);
CREATE INDEX IF NOT EXISTS idx_table_created_by_script
    ON table_catalog(created_by_script_id);
CREATE INDEX IF NOT EXISTS idx_table_created_by_run
    ON table_catalog(created_by_run_id);
CREATE INDEX IF NOT EXISTS idx_table_source_raw_data
    ON table_catalog(source_raw_data_id);
CREATE INDEX IF NOT EXISTS idx_table_schema_status
    ON table_catalog(schema_status, storage_type);

-- Script-table and document-table relations.
CREATE TABLE IF NOT EXISTS script_table_relation (
    script_table_relation_id INTEGER PRIMARY KEY,
    script_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    operation_type TEXT,
    run_id INTEGER,
    commit_id INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (script_id) REFERENCES script_catalog(script_id),
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id),
    FOREIGN KEY (run_id) REFERENCES run_catalog(run_id),
    FOREIGN KEY (commit_id) REFERENCES git_commit_catalog(commit_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_script_table_relation
    ON script_table_relation(script_id, table_id, relation_type, run_id);
CREATE INDEX IF NOT EXISTS idx_script_table_script
    ON script_table_relation(script_id);
CREATE INDEX IF NOT EXISTS idx_script_table_table
    ON script_table_relation(table_id);
CREATE INDEX IF NOT EXISTS idx_script_table_run_commit
    ON script_table_relation(run_id, commit_id);
CREATE INDEX IF NOT EXISTS idx_script_table_operation
    ON script_table_relation(operation_type);

CREATE TABLE IF NOT EXISTS document_table_relation (
    document_table_relation_id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    relation_type TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES document_catalog(document_id),
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_document_table_relation
    ON document_table_relation(document_id, table_id, relation_type);
CREATE INDEX IF NOT EXISTS idx_document_table_document
    ON document_table_relation(document_id);
CREATE INDEX IF NOT EXISTS idx_document_table_table
    ON document_table_relation(table_id);
CREATE INDEX IF NOT EXISTS idx_document_table_relation_type
    ON document_table_relation(relation_type);

-- Fields and raw tokens.
CREATE TABLE IF NOT EXISTS field_catalog (
    field_id INTEGER PRIMARY KEY,
    table_id INTEGER,
    raw_data_id INTEGER,
    field_name TEXT,
    field_position INTEGER,
    raw_type TEXT,
    inferred_type TEXT,
    harmonized_type TEXT,
    semantic_status TEXT NOT NULL DEFAULT 'unresolved',
    correction_state_relevance TEXT,
    unit_status TEXT NOT NULL DEFAULT 'not_checked',
    scale_status TEXT NOT NULL DEFAULT 'not_checked',
    missingness_status TEXT NOT NULL DEFAULT 'not_checked',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id),
    FOREIGN KEY (raw_data_id) REFERENCES raw_data(raw_data_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_field_table_position
    ON field_catalog(table_id, field_position);
CREATE INDEX IF NOT EXISTS idx_field_table
    ON field_catalog(table_id);
CREATE INDEX IF NOT EXISTS idx_field_raw_data
    ON field_catalog(raw_data_id);
CREATE INDEX IF NOT EXISTS idx_field_name
    ON field_catalog(field_name);
CREATE INDEX IF NOT EXISTS idx_field_semantic_status
    ON field_catalog(semantic_status, correction_state_relevance);
CREATE INDEX IF NOT EXISTS idx_field_unit_scale_missingness
    ON field_catalog(unit_status, scale_status, missingness_status);

CREATE TABLE IF NOT EXISTS raw_token_catalog (
    raw_token_id INTEGER PRIMARY KEY,
    raw_data_id INTEGER NOT NULL,
    field_id INTEGER,
    source_local_record_id TEXT,
    raw_token TEXT,
    token_position TEXT,
    token_type_guess TEXT,
    parse_status TEXT NOT NULL DEFAULT 'not_parsed',
    quarantine_status TEXT NOT NULL DEFAULT 'not_quarantined',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_data_id) REFERENCES raw_data(raw_data_id),
    FOREIGN KEY (field_id) REFERENCES field_catalog(field_id)
);

CREATE INDEX IF NOT EXISTS idx_raw_token_raw_data
    ON raw_token_catalog(raw_data_id);
CREATE INDEX IF NOT EXISTS idx_raw_token_field
    ON raw_token_catalog(field_id);
CREATE INDEX IF NOT EXISTS idx_raw_token_record
    ON raw_token_catalog(source_local_record_id);
CREATE INDEX IF NOT EXISTS idx_raw_token_status
    ON raw_token_catalog(parse_status, quarantine_status);

-- ETL and harmonization.
CREATE TABLE IF NOT EXISTS etl_transformation_rule (
    etl_rule_id INTEGER PRIMARY KEY,
    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    source_field_id INTEGER,
    target_field_name TEXT,
    transformation_expression TEXT,
    cast_rule TEXT,
    mapping_rule TEXT,
    unit_before TEXT,
    unit_after TEXT,
    scale_rule TEXT,
    missing_value_rule TEXT,
    blank_handling_rule TEXT,
    special_character_rule TEXT,
    provenance_status TEXT NOT NULL DEFAULT 'unresolved',
    reversible_flag INTEGER NOT NULL DEFAULT 0,
    allowed_for_analytics INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (source_field_id) REFERENCES field_catalog(field_id),
    UNIQUE(rule_name)
);

CREATE INDEX IF NOT EXISTS idx_etl_rule_source_field
    ON etl_transformation_rule(source_field_id);
CREATE INDEX IF NOT EXISTS idx_etl_rule_type
    ON etl_transformation_rule(rule_type);
CREATE INDEX IF NOT EXISTS idx_etl_rule_provenance
    ON etl_transformation_rule(provenance_status, allowed_for_analytics);
CREATE INDEX IF NOT EXISTS idx_etl_rule_target_field
    ON etl_transformation_rule(target_field_name);

CREATE TABLE IF NOT EXISTS harmonized_value_view_catalog (
    view_id INTEGER PRIMARY KEY,
    view_name TEXT NOT NULL,
    view_type TEXT,
    source_table_ids TEXT,
    transformation_rule_set TEXT,
    blind_descriptive_status TEXT NOT NULL DEFAULT 'not_reviewed',
    interpretation_status TEXT NOT NULL DEFAULT 'closed',
    created_by_run_id INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (created_by_run_id) REFERENCES run_catalog(run_id),
    UNIQUE(view_name)
);

CREATE INDEX IF NOT EXISTS idx_harmonized_view_run
    ON harmonized_value_view_catalog(created_by_run_id);
CREATE INDEX IF NOT EXISTS idx_harmonized_view_status
    ON harmonized_value_view_catalog(blind_descriptive_status, interpretation_status);
CREATE INDEX IF NOT EXISTS idx_harmonized_view_type
    ON harmonized_value_view_catalog(view_type);

-- Unit, quantity, and transformation-view catalogs.
CREATE TABLE IF NOT EXISTS unit_dimension_catalog (
    unit_id INTEGER PRIMARY KEY,
    unit_symbol TEXT NOT NULL,
    si_unit TEXT,
    dimension_expression TEXT,
    conversion_rule TEXT,
    source_status TEXT NOT NULL DEFAULT 'unresolved',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_unit_symbol_dimension
    ON unit_dimension_catalog(unit_symbol, dimension_expression);
CREATE INDEX IF NOT EXISTS idx_unit_si_unit
    ON unit_dimension_catalog(si_unit);
CREATE INDEX IF NOT EXISTS idx_unit_source_status
    ON unit_dimension_catalog(source_status);

CREATE TABLE IF NOT EXISTS quantity_domain_catalog (
    quantity_domain_id INTEGER PRIMARY KEY,
    domain_name TEXT NOT NULL,
    domain_type TEXT,
    description TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(domain_name)
);

CREATE INDEX IF NOT EXISTS idx_quantity_domain_type
    ON quantity_domain_catalog(domain_type);

CREATE TABLE IF NOT EXISTS quantity_catalog (
    quantity_id INTEGER PRIMARY KEY,
    quantity_domain_id INTEGER,
    symbol TEXT,
    quantity_name TEXT,
    si_unit TEXT,
    dimension_expression TEXT,
    observer_dependence TEXT,
    primitive_or_derived TEXT,
    description TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (quantity_domain_id) REFERENCES quantity_domain_catalog(quantity_domain_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_quantity_domain_symbol
    ON quantity_catalog(quantity_domain_id, symbol);
CREATE INDEX IF NOT EXISTS idx_quantity_domain
    ON quantity_catalog(quantity_domain_id);
CREATE INDEX IF NOT EXISTS idx_quantity_symbol
    ON quantity_catalog(symbol);
CREATE INDEX IF NOT EXISTS idx_quantity_name
    ON quantity_catalog(quantity_name);
CREATE INDEX IF NOT EXISTS idx_quantity_unit_dimension
    ON quantity_catalog(si_unit, dimension_expression);

CREATE TABLE IF NOT EXISTS transformation_rule_catalog (
    transformation_rule_id INTEGER PRIMARY KEY,
    rule_name TEXT NOT NULL,
    source_quantity_ids TEXT,
    target_quantity_id INTEGER,
    formula_expression TEXT,
    required_constants TEXT,
    validity_conditions TEXT,
    unit_check_status TEXT NOT NULL DEFAULT 'not_checked',
    invertible_flag INTEGER NOT NULL DEFAULT 0,
    direction TEXT,
    assumption_level TEXT,
    source_status TEXT NOT NULL DEFAULT 'unresolved',
    claim_boundary TEXT NOT NULL DEFAULT 'no_physical_validation_claim',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (target_quantity_id) REFERENCES quantity_catalog(quantity_id),
    UNIQUE(rule_name)
);

CREATE INDEX IF NOT EXISTS idx_transformation_target_quantity
    ON transformation_rule_catalog(target_quantity_id);
CREATE INDEX IF NOT EXISTS idx_transformation_source_status
    ON transformation_rule_catalog(source_status);
CREATE INDEX IF NOT EXISTS idx_transformation_unit_check
    ON transformation_rule_catalog(unit_check_status);
CREATE INDEX IF NOT EXISTS idx_transformation_direction
    ON transformation_rule_catalog(direction);

-- Audit and quality.
CREATE TABLE IF NOT EXISTS audit_log (
    audit_id INTEGER PRIMARY KEY,
    action_type TEXT NOT NULL,
    object_type TEXT,
    object_id TEXT,
    related_rule_id TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor TEXT,
    status TEXT,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_audit_action_type
    ON audit_log(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_object
    ON audit_log(object_type, object_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp
    ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_status
    ON audit_log(status);

CREATE TABLE IF NOT EXISTS quality_check_catalog (
    quality_check_id INTEGER PRIMARY KEY,
    check_name TEXT NOT NULL,
    check_type TEXT,
    target_table TEXT,
    target_field TEXT,
    check_expression TEXT,
    severity TEXT,
    stop_if_failed INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(check_name)
);

CREATE INDEX IF NOT EXISTS idx_quality_check_target
    ON quality_check_catalog(target_table, target_field);
CREATE INDEX IF NOT EXISTS idx_quality_check_type
    ON quality_check_catalog(check_type);
CREATE INDEX IF NOT EXISTS idx_quality_check_severity
    ON quality_check_catalog(severity, stop_if_failed);

CREATE TABLE IF NOT EXISTS quality_check_result (
    quality_check_result_id INTEGER PRIMARY KEY,
    quality_check_id INTEGER NOT NULL,
    raw_data_id INTEGER,
    table_id INTEGER,
    run_id INTEGER,
    result_status TEXT NOT NULL,
    result_detail TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (quality_check_id) REFERENCES quality_check_catalog(quality_check_id),
    FOREIGN KEY (raw_data_id) REFERENCES raw_data(raw_data_id),
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id),
    FOREIGN KEY (run_id) REFERENCES run_catalog(run_id)
);

CREATE INDEX IF NOT EXISTS idx_quality_result_check
    ON quality_check_result(quality_check_id);
CREATE INDEX IF NOT EXISTS idx_quality_result_raw_data
    ON quality_check_result(raw_data_id);
CREATE INDEX IF NOT EXISTS idx_quality_result_table
    ON quality_check_result(table_id);
CREATE INDEX IF NOT EXISTS idx_quality_result_run
    ON quality_check_result(run_id);
CREATE INDEX IF NOT EXISTS idx_quality_result_status
    ON quality_check_result(result_status);

-- Claim boundaries.
CREATE TABLE IF NOT EXISTS claim_boundary_catalog (
    claim_boundary_id INTEGER PRIMARY KEY,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    claim_level TEXT,
    physical_interpretation_allowed INTEGER NOT NULL DEFAULT 0,
    residual_analysis_allowed INTEGER NOT NULL DEFAULT 0,
    model_fitting_allowed INTEGER NOT NULL DEFAULT 0,
    bridge_claim_allowed INTEGER NOT NULL DEFAULT 0,
    value_reading_allowed INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(object_type, object_id)
);

CREATE INDEX IF NOT EXISTS idx_claim_boundary_level
    ON claim_boundary_catalog(claim_level);
CREATE INDEX IF NOT EXISTS idx_claim_boundary_object
    ON claim_boundary_catalog(object_type, object_id);
CREATE INDEX IF NOT EXISTS idx_claim_boundary_flags
    ON claim_boundary_catalog(
        physical_interpretation_allowed,
        residual_analysis_allowed,
        model_fitting_allowed,
        bridge_claim_allowed,
        value_reading_allowed
    );

COMMIT;
