-- QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01
-- Metadata server registration draft.
-- Existing repository patterns include metadata.meta_alias and qsb_metadata.* variants.
-- This run is blocked until a human selects the target metadata schema.

BEGIN;

-- Registration source:
-- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv
-- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_field_aliases.csv

-- Required registration columns:
-- table_name, field_name, canonical_name, de_label, en_label, description_de,
-- description_en, data_type, allowed_values, lineage_note, claim_boundary_note

-- Target choice required before execution:
-- Option A: metadata.meta_field / metadata.meta_alias
-- Option B: qsb_metadata domain-specific catalog tables
-- Option C: SQLite metadata snapshot tables

COMMIT;
