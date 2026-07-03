# QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01

This package registers the Compton-Schwarzschild scale mapping note as a DWH-ready, metadata-ready QSB work package.

## Work package

```text
QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01
```

## Core idea

Two complementary mapping levels are registered:

```text
Level 1: beta_B = r_s / lambda_C
Level 2: Xi_CS = c_comp^2 / c_schwarz^2
```

The mappings are treated as algebraic scale gates only.

## Claim status

```text
claim_status = scale_mapping_candidate
physical_claim_release = blocked_no_physics_claim
review_status = requires_dimensional_and_physical_review
```

## Package content

- `QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01.md`
- `data/scale_mapping_manifest.json`
- `data/scale_mapping_definitions.csv`
- `data/scale_mapping_variable_registry.csv`
- `data/scale_mapping_special_cases.csv`
- `data/scale_mapping_claim_boundaries.csv`
- `data/dimensional_checks.csv`
- `scripts/validate_scale_mapping_dimensions.py`
- `sql/20260703_qsb_planck_bridge_scale_mapping_note01_import.sql`
- `sql/validate_planck_bridge_scale_mapping_note01_import.sql`
- `sql/20260703_qsb_planck_bridge_scale_mapping_note01_metadata_integration.sql`
- `sql/validate_planck_bridge_scale_mapping_note01_metadata_integration.sql`

## Recommended execution order

1. Run the Python dimensional validator.
2. Import into PostgreSQL.
3. Validate import.
4. Run metadata integration.
5. Validate metadata integration.
6. Commit the run folder with `git add -f` if `runs/` is ignored.
