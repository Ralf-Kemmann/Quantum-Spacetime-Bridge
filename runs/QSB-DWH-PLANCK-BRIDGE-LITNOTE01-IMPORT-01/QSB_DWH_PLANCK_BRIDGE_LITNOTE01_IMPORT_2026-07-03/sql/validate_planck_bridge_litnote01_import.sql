-- Validation queries for QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01

SELECT run_id, work_package, source_entry_count, claim_map_count, physical_claim_status, claim_boundary
FROM qsb_literature.litnote_run
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01';

SELECT pillar_label, COUNT(*) AS reference_count
FROM qsb_literature.reference_source
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
GROUP BY pillar_label
ORDER BY pillar_label;

SELECT physical_claim_release, COUNT(*) AS rows
FROM qsb_literature.reference_source
WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
GROUP BY physical_claim_release;

SELECT *
FROM qsb_literature.v_planck_bridge_litnote01_claim_boundary;
