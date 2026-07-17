# QSB/PBR Literature Metadata DB Target Review 01

## Run Summary

run_id: `QSB-PBR-LITERATURE-METADATA-DB-TARGET-REVIEW-01`

previous_package: `runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/`

previous_status: `blocked_requires_human_db_target`

final_status: `db_target_review_recommends_two_db_architecture`

db_write_status: `no_db_write_occurred`

sqlite_open_mode: `file:path?mode=ro`

claim_boundary: `literature_context_only_no_internal_evidence_no_mechanism_claim`

physical_claim_release: `blocked_no_physics_claim`

mechanism_claim_release: `blocked_no_mechanism_claim`

## Befund

All required DB candidates existed and were opened read-only. Optional comparison DBs were also inspected read-only.

The required candidates classify as:

| candidate | classification | literature data target | metadata registration target | execute |
|---|---|---:|---:|---:|
| `qsb_research_dwh_target_workcopy_dwh03.db` | `active_dwh_workcopy_candidate` | `requires_human_approval` | `no` | `requires_human_approval` |
| `qsb_metadata_catalog_meta02.sqlite` | `metadata_catalog_candidate` | `no` | `requires_human_approval` | `requires_human_approval` |
| `qsb_metadata_catalog_corrcore01.sqlite` | `metadata_catalog_candidate` | `no` | `requires_human_approval` | `requires_human_approval` |

Optional comparison DBs classify as:

| candidate | classification | target use |
|---|---|---|
| `qsb_research_dwh_current_for_erd.db` | `erd_or_readout_copy_not_target` | not a target |
| `qsb_research_consolidated_snapshot.db` | `stale_snapshot_requires_review` | comparison only |
| `qsb_research_metadata_seed.db` | `seed_or_template_not_target` | not a target |

## Evidence Summary

The DWH workcopy is large and contains DWH-like table families: 5 raw-like objects, 26 core/mart-like objects, 14 source-like objects, and a `claim_boundary_catalog`.

META02 contains 22 metadata-server-like `meta_*` tables, including `meta_alias`, `meta_field`, `meta_source`, `meta_lineage`, `meta_object`, `meta_object_version`, `meta_validation_rule`, `meta_vocabulary`, `meta_vocabulary_entry`, and `meta_work_package`.

CORRCORE01 also contains 22 metadata-server-like `meta_*` tables with similar structure, but its path and row counts indicate a domain/run-specific catalog update.

## Interpretation

The previous single `--db` importer target is too coarse for the observed architecture. Literature rows and metadata-server registration belong to different target layers.

Recommended target architecture:

```text
literature_data_db = runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db
metadata_registration_db = runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite
importer_change_required = true
required_importer_change = add --data-db PATH_TO_DWH --metadata-db PATH_TO_METADATA_CATALOG --mode dry-run|execute
```

No importer change was implemented in this review.

## Hypothese

If the human approves this two-DB architecture, a later importer patch can keep literature data insertion and metadata catalog registration separate, with separate dry-run validation for each target.

## Offene Lücke

- Human architecture approval is required.
- Human confirmation is required before any execute import.
- The importer still has a single `--db` interface.
- This review does not validate write compatibility because no write transaction was allowed.

## Claim Boundary

This review makes no physics or mechanism claim. Literature metadata remains context/search-space metadata only and does not become QSB/PBR internal evidence.
