# QSB DWH Planck Bridge Literature Note 01 — Metadata Integration

**Run:** `QSB-DWH-PLANCK-BRIDGE-LITNOTE01-METADATA-INTEGRATION-01`  
**Source run:** `QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01`  
**Work package:** `QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01`

This patch completes the missing metadata integration for the already imported Literature Note 01 bibliography and claim map.

It does **not** release physics claims. The metadata status remains:

```text
blocked_no_physics_claim
registered_requires_human_literature_review
```

## What it adds

Schema:

```sql
qsb_metadata
```

Tables:

```sql
qsb_metadata.litnote01_metadata_integration_run
qsb_metadata.litnote01_catalog_object
qsb_metadata.litnote01_field_metadata
qsb_metadata.litnote01_lineage_edge
qsb_metadata.litnote01_claim_boundary_metadata
qsb_metadata.litnote01_validation_result
```

Views:

```sql
qsb_metadata.v_planck_bridge_litnote01_metadata_search
qsb_metadata.v_planck_bridge_litnote01_metadata_dashboard
```

## Required precondition

The literature import must already be present:

```sql
qsb_literature.litnote_run
qsb_literature.reference_source
qsb_literature.reference_claim_map
qsb_literature.v_planck_bridge_litnote01_claim_boundary
```

## Run

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/runs/QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01/QSB_DWH_PLANCK_BRIDGE_LITNOTE01_IMPORT_2026-07-03

# copy/unzip this metadata package here or into the parent run directory
psql -v ON_ERROR_STOP=1 -f sql/20260703_qsb_planck_bridge_litnote01_metadata_integration.sql
psql -v ON_ERROR_STOP=1 -f sql/validate_planck_bridge_litnote01_metadata_integration.sql | tee validation/validate_planck_bridge_litnote01_metadata_integration.log
```

## DBeaver checks

```sql
SELECT *
FROM qsb_metadata.v_planck_bridge_litnote01_metadata_dashboard;
```

```sql
SELECT *
FROM qsb_metadata.v_planck_bridge_litnote01_metadata_search
WHERE search_text ILIKE '%Planck%';
```

## Claim boundary

This patch registers the literature import into metadata/lineage/search. It does not interpret the literature as proof of QSB or as evidence for an existing Planck-Bridge-Resonator.
