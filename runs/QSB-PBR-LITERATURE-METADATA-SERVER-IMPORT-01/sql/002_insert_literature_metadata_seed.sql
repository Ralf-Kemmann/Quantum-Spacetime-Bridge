-- QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01
-- Seed insert placeholder.
-- Use scripts/import_literature_metadata.py for CSV-backed dry-run or execution.
-- Do not execute until a human selects the DB target.

BEGIN;

-- CSV inputs:
-- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv
-- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_mechanism_tags.csv
-- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_claim_boundaries.csv
-- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_import_manifest.csv

-- Import policy:
-- 1. Do not overwrite existing rows without explicit merge logic and validation.
-- 2. Roll back if any validation query fails.
-- 3. Preserve all zero-support claim-boundary flags.

COMMIT;
