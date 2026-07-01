SELECT * FROM canonical.obs_dataset;

SELECT dataset_id, file_name, sha256, raw_data_status
FROM canonical.obs_source_file
ORDER BY file_name;

SELECT galaxy_id, gobs_m_s2, gbar_m_s2, log_gobs, log_gbar
FROM mart.v_sparc_rar_direct_points
LIMIT 20;

SELECT galaxy_id, radius_kpc, vobs_km_s, gobs_m_s2
FROM mart.v_sparc_massmodels_gobs_points
LIMIT 20;

SELECT canonical_name, display_label_de
FROM mart.v_de_sparc_feldnamen
ORDER BY canonical_name;

SELECT *
FROM mart.v_qsb_obs_search_sparc_rar
WHERE search_text ILIKE '%Beschleunigung%'
LIMIT 20;

SELECT validation_status, COUNT(*) AS n
FROM mart.v_sparc_validation_status
GROUP BY validation_status;
