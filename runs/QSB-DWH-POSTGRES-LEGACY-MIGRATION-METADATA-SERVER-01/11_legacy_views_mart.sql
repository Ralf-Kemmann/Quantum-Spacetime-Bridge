CREATE OR REPLACE VIEW mart.v_qsb_dataset_overview AS
SELECT dataset_id, dataset_name, domain, registration_status
FROM admin.dataset_registry
UNION
SELECT dataset_id, dataset_name, domain, 'metadata_registered' AS registration_status
FROM metadata.meta_dataset;

CREATE OR REPLACE VIEW mart.v_qsb_run_timeline AS
SELECT run_id, run_folder, domain_guess, file_count, registered_by_run_id
FROM canonical.qsb_run;

CREATE OR REPLACE VIEW mart.v_qsb_artifact_inventory AS
SELECT artifact_id, relative_path, artifact_kind, domain_guess, sha256
FROM canonical.qsb_artifact;

CREATE OR REPLACE VIEW mart.v_qsb_metadata_fields AS
SELECT canonical_name, quantity_kind, dimension_vector, display_label_de, validation_status
FROM metadata.meta_field;

CREATE OR REPLACE VIEW mart.v_qsb_metadata_units AS
SELECT unit_symbol, quantity_kind, dimension_vector, conversion_rule_id, validation_status
FROM metadata.meta_unit;

CREATE OR REPLACE VIEW mart.v_qsb_metadata_aliases_de AS
SELECT canonical_name, display_label_de, language, alias_status
FROM metadata.meta_alias
WHERE language = 'de';

CREATE OR REPLACE VIEW mart.v_qsb_validation_status AS
SELECT validation_id, dataset_id, validation_scope, validation_rule, validation_status, observed_value, expected_value, notes
FROM validation.validation_result;

CREATE OR REPLACE VIEW mart.v_qsb_claim_boundaries AS
SELECT claim_boundary_id, claim_boundary, claim_status
FROM validation.claim_boundary;

CREATE OR REPLACE VIEW mart.v_qsb_global_search AS
SELECT token_id, record_type, record_id, search_text, domain_guess
FROM metadata.meta_search_token
UNION ALL
SELECT artifact_id, 'artifact', artifact_id, relative_path || ' ' || artifact_kind || ' ' || domain_guess, domain_guess
FROM canonical.qsb_artifact
UNION ALL
SELECT alias_id, 'alias', canonical_name, canonical_name || ' ' || display_label_de, 'metadata'
FROM metadata.meta_alias;

CREATE OR REPLACE VIEW mart.v_matrix_topology_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess IN ('matrix_topology', 'extract03');

CREATE OR REPLACE VIEW mart.v_interface01_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess = 'interface01';

CREATE OR REPLACE VIEW mart.v_relalg_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess = 'relalg';

CREATE OR REPLACE VIEW mart.v_causality_overview AS
SELECT a.artifact_id, a.relative_path, a.artifact_kind, a.sha256
FROM canonical.qsb_artifact a
WHERE a.domain_guess = 'causality';
