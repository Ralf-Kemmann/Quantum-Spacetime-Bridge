# QSB/PBR Literature Metadata Two-DB Importer Patch 01

## Run Summary

run_id: `QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01`

final_status: `two_db_importer_patch_dry_run_passed`

modified_importer: `runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py`

literature_data_db: `runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db`

metadata_registration_db: `runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite`

dry_run_strategy: `copy_to_tmp_and_write_copies_only`

metadata_registration_status: `metadata_registration_planned_requires_schema_mapping_review`

real_db_targets_unchanged: `true`

execution_import_authorized: `false`

claim_boundary: `literature_context_only_no_internal_evidence_no_mechanism_claim`

physical_claim_release: `blocked_no_physics_claim`

mechanism_claim_release: `blocked_no_mechanism_claim`

## Befund

The importer now supports the two-DB CLI contract:

```text
--data-db PATH_TO_DWH --metadata-db PATH_TO_METADATA_CATALOG --seed PATH --mode dry-run
```

The required dry-run was executed against the approved real target paths, but the importer copied both targets to `/tmp` and wrote only to those temporary copies. The real target SHA256 and mtime values remained unchanged.

The deprecated single-DB dry-run mode remains available for compatibility and emits:

```text
single_db_mode_deprecated_for_two_db_architecture
```

Execute mode is blocked in this patch run and emits:

```text
execution_import_authorized=false
```

## Interpretation

The two-DB importer patch is ready for human review as a dry-run design. It is not an execution authorization and does not perform any real DWH or metadata-catalog import.

Metadata registration is deliberately handled as a dry-run plan table in the copied metadata DB. Exact `meta_*` insert mapping is deferred because the catalog schema has strong domain constraints and should not be guessed.

## Hypothese

A later, separately authorized metadata schema mapping review can translate the registration plan into real `meta_object`, `meta_field`, `meta_alias`, lineage, validation, vocabulary, and work-package rows.

## Offene Lücke

- No real import has been executed.
- No real `meta_*` rows have been inserted.
- Execute mode remains blocked pending separate human authorization.
- Temporary dry-run DB copies live under `/tmp` and are referenced in `data/two_db_dry_run_target_integrity.csv`.

## Next Command

```bash
git diff -- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py
```

## Claim Boundary

Literature rows remain context and search-space metadata only. They are not internal evidence for QSB/PBR and do not authorize physical or mechanistic claims.
