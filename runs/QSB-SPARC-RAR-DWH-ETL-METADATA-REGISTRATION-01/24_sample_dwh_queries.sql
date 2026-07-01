-- 1_all_datasets
SELECT * FROM qsb_obs_dataset;

-- 2_sources_checksums
SELECT dataset_id, file_name, sha256, raw_data_status FROM qsb_obs_source_file ORDER BY file_name;

-- 3_direct_rar_points
SELECT galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar FROM v_sparc_rar_direct_points LIMIT 20;

-- 4_massmodels_gobs_points
SELECT galaxy_id, radius_kpc, vobs_km_s, gobs_m_s2 FROM v_sparc_massmodels_gobs_points LIMIT 20;

-- 5_german_field_names
SELECT canonical_name, display_label_de FROM v_de_sparc_feldnamen ORDER BY canonical_name;

-- 6_search_view
SELECT * FROM v_qsb_obs_search_sparc_rar WHERE search_text LIKE '%Beschleunigung%' LIMIT 20;

-- 7_validation_status
SELECT validation_status, COUNT(*) AS n FROM v_sparc_validation_status GROUP BY validation_status;
