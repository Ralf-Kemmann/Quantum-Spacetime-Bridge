-- QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01 validation queries.
-- Run inside the same transaction as any execute import. Roll back on any failure.

BEGIN;

SELECT 'source_count' AS check_name, COUNT(*) AS actual, 23 AS expected
FROM qsb_literature_source;

SELECT 'internal_evidence_flag_all_zero' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_claim_boundary
WHERE internal_evidence_flag <> 0;

SELECT 'mechanism_claim_support_all_zero' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_claim_boundary
WHERE mechanism_claim_support <> 0;

SELECT 'physical_claim_support_all_zero' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_claim_boundary
WHERE physical_claim_support <> 0;

SELECT 'sources_without_tags' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_source s
WHERE NOT EXISTS (
  SELECT 1 FROM qsb_literature_mechanism_tag t
  WHERE t.literature_id = s.literature_id
);

SELECT 'missing_source_class' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_source
WHERE source_class IS NULL OR source_class = '';

SELECT 'missing_author_cluster' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_source
WHERE author_cluster IS NULL OR author_cluster = '';

SELECT 'missing_theory_cluster' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_source
WHERE theory_cluster IS NULL OR theory_cluster = '';

SELECT 'missing_allowed_use' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_claim_boundary
WHERE allowed_use IS NULL OR allowed_use = '';

SELECT 'forbidden_phrases_in_claim_fields' AS check_name, COUNT(*) AS actual, 0 AS expected
FROM qsb_literature_claim_boundary
WHERE lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%supports qsb%'
   OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%proves qsb%'
   OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%confirms mechanism%'
   OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%evidence for qsb%'
   OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%physical discovery%';

ROLLBACK;
