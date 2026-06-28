# QSB-META-RELALG-SYNC-MIN

## Purpose

`QSB-META-RELALG-SYNC-MIN` registers recently completed RELALG artifacts in the central QSB metadata catalog.

This is metadata registration only. It does not recompute RELALG results, alter source runs, create scientific claims beyond bounded catalog statements, or unlock REAL01 or physics-claim paths.

## Target Metadata DB

```text
runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite
```

The script uses the existing metadata schema and never creates, alters, drops, or deletes tables or rows.

## Registered Inputs

- `QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED`
- `QSB-RELALG-SYNTH-D1K-BRIDGE`
- `QSB-RELALG-SYNTH-D1K-LOOP-MIN`
- D1K and D1F source CSVs used by the synthetic bridge
- German D1K phase source view SQL when present

## Modes

Default mode is dry-run:

```bash
python scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py --dry-run
```

Apply mode writes deterministic `INSERT OR REPLACE` rows after schema and status prechecks pass:

```bash
python scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py --apply
```

Replay protection refuses to overwrite the output directory unless `--force` is supplied:

```bash
python scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py --dry-run --force
python scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py --apply --force
```

## Generated Outputs

Outputs are written under:

```text
runs/QSB-META-RELALG-SYNC-MIN/
```

Artifacts:

- `qsb_meta_relalg_sync_min_plan.csv`
- `qsb_meta_relalg_sync_min_inserted_or_updated_rows.csv`
- `qsb_meta_relalg_sync_min_precheck.json`
- `qsb_meta_relalg_sync_min_validation_report.json`
- `qsb_meta_relalg_sync_min_next_step_gate.json`
- `qsb_meta_relalg_sync_min_manifest.json`
- `qsb_meta_relalg_sync_min_readout.md`
- `qsb_meta_relalg_sync_min_summary.json`
- `qsb_meta_relalg_sync_min_sql_preview.sql`
- `qsb_meta_relalg_sync_min_before_counts.json`
- `qsb_meta_relalg_sync_min_after_counts.json`

## Claim Boundary

Registered claims are bounded metadata statements only:

- REAL01 authorized export attempt: no export rows, no `Phi_ABC`, no staging/execution/interpretation/physics claim.
- SYNTH-D1K bridge: synthetic diagnostic C-layer only, not REAL01 evidence and not a physical phase or C-layer source.
- SYNTH-D1K loop-min: source-native star-like topology with zero closed triples; no loop-phase interpretation and no missing-edge inference.

## Validation

Run from the repository root:

```bash
python -m py_compile scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py
python scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py --dry-run
python -m json.tool runs/QSB-META-RELALG-SYNC-MIN/qsb_meta_relalg_sync_min_validation_report.json
python -m json.tool runs/QSB-META-RELALG-SYNC-MIN/qsb_meta_relalg_sync_min_next_step_gate.json
python scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py --dry-run
python scripts/qsb_meta_relalg_sync_min/qsb_meta_relalg_sync_min.py --apply --force
python -m json.tool runs/QSB-META-RELALG-SYNC-MIN/qsb_meta_relalg_sync_min_summary.json
git diff --check
git status --short
```

The second dry-run without `--force` is expected to refuse overwrite.
