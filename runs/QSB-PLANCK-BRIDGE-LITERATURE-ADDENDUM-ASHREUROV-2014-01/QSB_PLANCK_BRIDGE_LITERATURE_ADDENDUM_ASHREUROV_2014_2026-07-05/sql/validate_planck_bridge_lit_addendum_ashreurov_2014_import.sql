-- Validate QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01

BEGIN;
CREATE SCHEMA IF NOT EXISTS qsb_literature;
COMMIT;

WITH summary AS (
    SELECT
        r.run_id,
        r.work_package,
        r.source_entry_count,
        COUNT(DISTINCT s.bib_key) AS actual_source_count,
        r.claim_map_count,
        COUNT(DISTINCT c.claim_map_id) AS actual_claim_map_count,
        MIN(s.physical_claim_release) AS physical_claim_release,
        MIN(c.review_status) AS review_status,
        r.claim_boundary
    FROM qsb_literature.litnote_run r
    LEFT JOIN qsb_literature.reference_source s ON s.run_id = r.run_id
    LEFT JOIN qsb_literature.reference_claim_map c ON c.run_id = r.run_id
    WHERE r.run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'
    GROUP BY r.run_id, r.work_package, r.source_entry_count, r.claim_map_count, r.claim_boundary
)
SELECT * FROM summary;

WITH checks AS (
    SELECT 'source_import' AS validation_scope, 'source_count_matches_manifest' AS check_name, '1' AS expected_value,
           COUNT(*)::TEXT AS actual_value, COUNT(*) = 1 AS passed, 'error' AS severity
    FROM qsb_literature.reference_source WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'
    UNION ALL
    SELECT 'claim_boundary', 'claim_map_count_matches_manifest', '1', COUNT(*)::TEXT, COUNT(*) = 1, 'error'
    FROM qsb_literature.reference_claim_map WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'
    UNION ALL
    SELECT 'claim_boundary', 'all_references_claim_blocked', 'blocked_no_physics_claim only', COALESCE(MIN(physical_claim_release),'missing'),
           COUNT(*) = 1 AND MIN(physical_claim_release) = 'blocked_no_physics_claim' AND MAX(physical_claim_release) = 'blocked_no_physics_claim', 'error'
    FROM qsb_literature.reference_source WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'
    UNION ALL
    SELECT 'review_gate', 'human_literature_review_required', 'registered_requires_human_literature_review', COALESCE(MIN(review_status),'missing'),
           COUNT(*) = 1 AND MIN(review_status) = 'registered_requires_human_literature_review', 'error'
    FROM qsb_literature.reference_claim_map WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'
)
SELECT * FROM checks ORDER BY validation_scope, check_name;

SELECT * FROM qsb_literature.v_planck_bridge_lit_addendum_ashreurov_2014_claim_boundary;
