CREATE OR REPLACE VIEW mart.v_sparc_rar_direct_points AS
SELECT rar_point_id, dataset_id, galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar,
       validation_status, claim_boundary
FROM canonical.obs_rar_point;

CREATE OR REPLACE VIEW mart.v_sparc_massmodels_gobs_points AS
SELECT massmodel_point_id, dataset_id, galaxy_id, radius_kpc, vobs_km_s, vgas_km_s,
       vdisk_km_s, vbul_km_s, gobs_m_s2, log_gobs, gbar_status,
       mass_to_light_assumption_required, validation_status, claim_boundary
FROM canonical.obs_massmodel_point;

CREATE OR REPLACE VIEW mart.v_sparc_baseline_quantities AS
SELECT * FROM canonical.obs_baseline_quantity;

CREATE OR REPLACE VIEW mart.v_sparc_dataset_lineage AS
SELECT dataset_id, source_id, source_path, source_sha256, lineage_role, validation_status
FROM metadata.meta_lineage;

CREATE OR REPLACE VIEW mart.v_sparc_field_metadata AS
SELECT canonical_name, quantity_kind, dimension_vector, display_label_de, validation_status, claim_boundary
FROM metadata.meta_field;

CREATE OR REPLACE VIEW mart.v_sparc_unit_metadata AS
SELECT unit_symbol, quantity_kind, dimension_vector, conversion_rule_id, validation_status
FROM metadata.meta_unit;

CREATE OR REPLACE VIEW mart.v_sparc_validation_status AS
SELECT validation_scope, validation_rule, validation_status, observed_value, expected_value, notes
FROM validation.validation_result;

CREATE OR REPLACE VIEW mart.v_de_sparc_feldnamen AS
SELECT canonical_name, display_label_de, language, alias_status
FROM metadata.meta_alias
WHERE language = 'de';

CREATE OR REPLACE VIEW mart.v_de_sparc_metadaten AS
SELECT f.canonical_name, f.display_label_de, f.quantity_kind, f.dimension_vector,
       u.unit_symbol, u.conversion_rule_id, f.validation_status, f.claim_boundary
FROM metadata.meta_field f
LEFT JOIN metadata.meta_unit u ON u.quantity_kind = f.quantity_kind;

CREATE OR REPLACE VIEW mart.v_qsb_obs_search_sparc_rar AS
SELECT 'field'::text AS record_type, canonical_name AS record_id,
       canonical_name || ' ' || display_label_de || ' ' || COALESCE(quantity_kind, '') || ' ' || COALESCE(dimension_vector, '') AS search_text,
       validation_status, claim_boundary
FROM metadata.meta_field
UNION ALL
SELECT 'rar_point'::text, rar_point_id,
       COALESCE(galaxy_id, '') || ' Beschleunigung gobs gbar ' || COALESCE(gobs_m_s2::text, '') || ' ' || COALESCE(gbar_m_s2::text, ''),
       validation_status, claim_boundary
FROM canonical.obs_rar_point
UNION ALL
SELECT 'massmodel_point'::text, massmodel_point_id,
       COALESCE(galaxy_id, '') || ' beobachtete Beschleunigung Rotationsgeschwindigkeit Radius ' ||
       COALESCE(gobs_m_s2::text, '') || ' ' || COALESCE(vobs_km_s::text, ''),
       validation_status, claim_boundary
FROM canonical.obs_massmodel_point;

CREATE OR REPLACE VIEW mart.v_qsb_dwh_status AS
SELECT r.run_id, r.dataset_id, r.status, r.started_at, r.finished_at,
       p.backend, p.target_database, p.sqlite_role
FROM admin.etl_run r
LEFT JOIN admin.single_dwh_policy p ON p.policy_id = 'qsb_single_dwh_policy';
