# QSB-MAP01-DWH-A

Sandbox-only SQLite mart and Mermaid export dry run for QSB-MAP01.

This package creates a standalone SQLite database under `runs/QSB-MAP01-DWH-A/`.
It does not mutate a production DWH, Source-Hub schema, EXTRACT tables, or
existing project data.

## Files

- `schema.sql` defines the local mart tables and views.
- `qsb_map01_dwh_a.py` seeds canonical DWH-style records, generates Mermaid and
  Markdown outputs from SQLite content, and writes validation records.

## Run

```bash
python scripts/qsb_map01_dwh_a/qsb_map01_dwh_a.py
```

Expected generated files:

- `runs/QSB-MAP01-DWH-A/qsb_map01.sqlite`
- `runs/QSB-MAP01-DWH-A/qsb_map01_seed_manifest.json`
- `runs/QSB-MAP01-DWH-A/qsb_map01_validation_report.json`
- `runs/QSB-MAP01-DWH-A/qsb_map01.mmd`
- `runs/QSB-MAP01-DWH-A/qsb_map01.md`
- `runs/QSB-MAP01-DWH-A/qsb_map01_claim_boundary_report.md`
- `runs/QSB-MAP01-DWH-A/QSB-MAP01-DWH-A_RUN_SUMMARY.md`

## Claim Boundary

This is a metadata and structure dry run only. It contains no physical
confirmation, no spacetime claim, no causality claim, and no RELALG computation.
