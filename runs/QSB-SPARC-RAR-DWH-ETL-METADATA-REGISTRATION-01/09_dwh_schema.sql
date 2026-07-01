CREATE INDEX idx_artifact_dataset ON qsb_obs_artifact(dataset_id)
CREATE INDEX idx_meta_field_name ON meta_field(canonical_name)
CREATE INDEX idx_mm_galaxy ON qsb_obs_massmodel_point(galaxy_id)
CREATE INDEX idx_qsf_dataset ON qsb_obs_source_file(dataset_id)
CREATE INDEX idx_quantity_kind ON qsb_obs_quantity_definition(quantity_kind)
CREATE INDEX idx_rar_claim ON qsb_obs_rar_point(claim_boundary)
CREATE INDEX idx_rar_galaxy ON qsb_obs_rar_point(galaxy_id)
CREATE INDEX idx_validation_status ON meta_validation_result(validation_status)
CREATE TABLE meta_alias (
          alias_id TEXT PRIMARY KEY, canonical_name TEXT, display_label_de TEXT, language TEXT, alias_status TEXT
        )
CREATE TABLE meta_claim (
          claim_id TEXT PRIMARY KEY, claim_boundary TEXT, claim_text TEXT, claim_status TEXT
        )
CREATE TABLE meta_field (
          field_id TEXT PRIMARY KEY, canonical_name TEXT, quantity_kind TEXT, dimension_vector TEXT,
          display_label_de TEXT, validation_status TEXT, claim_boundary TEXT
        )
CREATE TABLE meta_lineage (
          lineage_id TEXT PRIMARY KEY, dataset_id TEXT, source_id TEXT, source_path TEXT, source_sha256 TEXT,
          lineage_hash TEXT, lineage_role TEXT, validation_status TEXT, claim_boundary TEXT
        )
CREATE TABLE meta_unit (
          unit_id TEXT PRIMARY KEY, unit_symbol TEXT, quantity_kind TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, validation_status TEXT
        )
CREATE TABLE meta_validation_result (
          validation_id TEXT PRIMARY KEY, validation_scope TEXT, validation_rule TEXT,
          validation_status TEXT, observed_value TEXT, expected_value TEXT, notes TEXT
        )
CREATE TABLE qsb_obs_artifact (
          source_artifact_id TEXT PRIMARY KEY, dataset_id TEXT, source_run_id TEXT, file_name TEXT,
          file_path TEXT, size_bytes INTEGER, sha256 TEXT, row_count INTEGER, columns_json TEXT,
          lineage_role TEXT, validation_status TEXT, claim_boundary TEXT
        )
CREATE TABLE qsb_obs_baseline_quantity (
          baseline_quantity_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, run_id TEXT,
          galaxy_id TEXT, quantity_kind TEXT, original_value TEXT, original_unit TEXT,
          calculation_value REAL, calculation_unit TEXT, display_unit TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, lineage_hash TEXT, source_sha256 TEXT, validation_status TEXT,
          claim_boundary TEXT
        )
CREATE TABLE qsb_obs_dataset (
          dataset_id TEXT PRIMARY KEY, run_id TEXT, canonical_name TEXT, source_reference TEXT,
          validation_status TEXT, claim_boundary TEXT
        )
CREATE TABLE qsb_obs_galaxy (
          galaxy_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, validation_status TEXT
        )
CREATE TABLE qsb_obs_massmodel_point (
          massmodel_point_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, run_id TEXT,
          galaxy_id TEXT, radius_kpc REAL, vobs_km_s REAL, vgas_km_s REAL, vdisk_km_s REAL, vbul_km_s REAL,
          gobs_m_s2 REAL, log_gobs REAL, gbar_m_s2 REAL, log_gbar REAL, gbar_status TEXT,
          mass_to_light_assumption_required TEXT, unit_original TEXT, unit_calculation TEXT,
          unit_display TEXT, dimension_vector TEXT, conversion_rule_id TEXT, lineage_hash TEXT,
          source_sha256 TEXT, validation_status TEXT, claim_boundary TEXT
        )
CREATE TABLE qsb_obs_measurement (
          measurement_id TEXT PRIMARY KEY, dataset_id TEXT, source_file_id TEXT, source_artifact_id TEXT,
          run_id TEXT, galaxy_id TEXT, quantity_id TEXT, original_value TEXT, original_unit TEXT,
          calculation_value REAL, calculation_unit TEXT, display_unit TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, lineage_hash TEXT, source_sha256 TEXT, validation_status TEXT,
          claim_boundary TEXT
        )
CREATE TABLE qsb_obs_quantity_definition (
          quantity_id TEXT PRIMARY KEY, canonical_name TEXT, quantity_kind TEXT, unit_original TEXT,
          unit_calculation TEXT, unit_display TEXT, dimension_vector TEXT, conversion_rule_id TEXT,
          validation_status TEXT, claim_boundary TEXT
        )
CREATE TABLE qsb_obs_rar_point (
          rar_point_id TEXT PRIMARY KEY, dataset_id TEXT, source_artifact_id TEXT, run_id TEXT,
          galaxy_id TEXT, gobs_m_s2 REAL, gbar_m_s2 REAL, log_gobs REAL, log_gbar REAL,
          unit_original TEXT, unit_calculation TEXT, unit_display TEXT, dimension_vector TEXT,
          conversion_rule_id TEXT, lineage_hash TEXT, source_sha256 TEXT, validation_status TEXT,
          claim_boundary TEXT
        )
CREATE TABLE qsb_obs_source_file (
          source_file_id TEXT PRIMARY KEY, dataset_id TEXT, file_name TEXT, file_path TEXT,
          size_bytes INTEGER, sha256 TEXT, line_count INTEGER, lineage_role TEXT,
          raw_data_status TEXT, dwh_status TEXT, validation_status TEXT, claim_boundary TEXT
        )
CREATE TABLE qsb_run (
          run_id TEXT PRIMARY KEY, status TEXT, created_utc TEXT, claim_boundary TEXT,
          residual_analysis_executed INTEGER, rbci_v1_evaluated INTEGER, qsb_observable_evaluated INTEGER
        )
CREATE TABLE stg_sparc_massmodels (
          row_id TEXT, galaxy_id TEXT, radius_kpc TEXT, vobs_km_s TEXT, vgas_km_s TEXT,
          vdisk_km_s_ml1 TEXT, vbul_km_s_ml1 TEXT, gobs_m_per_s2 TEXT, log10_gobs TEXT,
          vbar_ml1_km_s_preparatory TEXT, gbar_status TEXT, mass_to_light_assumption_required TEXT,
          claim_boundary TEXT
        )
CREATE TABLE stg_sparc_rar (
          row_id TEXT, log10_gbar_m_per_s2 TEXT, e_log10_gbar TEXT, log10_gobs_m_per_s2 TEXT,
          e_log10_gobs TEXT, gbar_m_per_s2 TEXT, gobs_m_per_s2 TEXT, source_table TEXT, claim_boundary TEXT
        )
CREATE TABLE stg_sparc_rarbins (
          row_number INTEGER PRIMARY KEY, raw_line TEXT, source_file_id TEXT, source_sha256 TEXT
        )
CREATE TABLE stg_sparc_sample (
          row_number INTEGER PRIMARY KEY, raw_line TEXT, source_file_id TEXT, source_sha256 TEXT
        )
CREATE VIEW v_de_sparc_feldnamen AS
        SELECT canonical_name, display_label_de, language, alias_status
        FROM meta_alias
        WHERE language = 'de'
CREATE VIEW v_de_sparc_metadaten AS
        SELECT f.canonical_name, f.display_label_de, f.quantity_kind, f.dimension_vector,
               u.unit_symbol, u.conversion_rule_id, f.validation_status, f.claim_boundary
        FROM meta_field f
        LEFT JOIN meta_unit u ON u.quantity_kind = f.quantity_kind
CREATE VIEW v_qsb_obs_search_sparc_rar AS
        SELECT 'field' AS record_type, canonical_name AS record_id,
               canonical_name || ' ' || display_label_de || ' ' || quantity_kind || ' ' || dimension_vector AS search_text,
               validation_status, claim_boundary
        FROM meta_field
        UNION ALL
        SELECT 'rar_point', rar_point_id,
               COALESCE(galaxy_id, '') || ' Beschleunigung gobs gbar ' || COALESCE(CAST(gobs_m_s2 AS TEXT), '') || ' ' || COALESCE(CAST(gbar_m_s2 AS TEXT), ''),
               validation_status, claim_boundary
        FROM qsb_obs_rar_point
        UNION ALL
        SELECT 'massmodel_point', massmodel_point_id,
               COALESCE(galaxy_id, '') || ' beobachtete Beschleunigung Rotationsgeschwindigkeit Radius ' ||
               COALESCE(CAST(gobs_m_s2 AS TEXT), '') || ' ' || COALESCE(CAST(vobs_km_s AS TEXT), ''),
               validation_status, claim_boundary
        FROM qsb_obs_massmodel_point
CREATE VIEW v_sparc_baseline_quantities AS
        SELECT * FROM qsb_obs_baseline_quantity
CREATE VIEW v_sparc_dataset_lineage AS
        SELECT dataset_id, source_id, source_path, source_sha256, lineage_hash, lineage_role,
               validation_status, claim_boundary
        FROM meta_lineage
CREATE VIEW v_sparc_field_metadata AS
        SELECT canonical_name, quantity_kind, dimension_vector, display_label_de, validation_status, claim_boundary
        FROM meta_field
CREATE VIEW v_sparc_massmodels_gobs_points AS
        SELECT massmodel_point_id, dataset_id, galaxy_id, radius_kpc, vobs_km_s, vgas_km_s,
               vdisk_km_s, vbul_km_s, gobs_m_s2, log_gobs, gbar_status,
               mass_to_light_assumption_required, validation_status, claim_boundary
        FROM qsb_obs_massmodel_point
CREATE VIEW v_sparc_rar_direct_points AS
        SELECT rar_point_id, dataset_id, galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar,
               validation_status, claim_boundary
        FROM qsb_obs_rar_point
CREATE VIEW v_sparc_unit_metadata AS
        SELECT unit_symbol, quantity_kind, dimension_vector, conversion_rule_id, validation_status
        FROM meta_unit
CREATE VIEW v_sparc_validation_status AS
        SELECT validation_scope, validation_rule, validation_status, observed_value, expected_value, notes
        FROM meta_validation_result
