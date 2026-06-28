# QSB-ARTIFACT01-DWH-A

Sandbox-only artifact registry dry run for QSB-MAP01-DWH-A generated outputs.

This package creates a standalone SQLite registry under
`runs/QSB-ARTIFACT01-DWH-A/`. It does not mutate a production DWH,
Source-Hub, EXTRACT, META, MAP01, or any existing project schema.

## Files

- `schema.sql` defines the local artifact registry tables and views.
- `qsb_artifact01_dwh_a.py` registers existing QSB-MAP01-DWH-A output files,
  computes hashes and sizes, records lineage, claim boundaries, reviews, text
  index excerpts, exports, relations, and validation results.

## Run

```bash
python scripts/qsb_artifact01_dwh_a/qsb_artifact01_dwh_a.py
```

The builder refuses to overwrite
`runs/QSB-ARTIFACT01-DWH-A/qsb_artifact01.sqlite` unless called with
`--force`. The `--force` mode deletes only files inside
`runs/QSB-ARTIFACT01-DWH-A/` and never touches input artifacts.

Expected generated files:

- `runs/QSB-ARTIFACT01-DWH-A/qsb_artifact01.sqlite`
- `runs/QSB-ARTIFACT01-DWH-A/qsb_artifact01_seed_manifest.json`
- `runs/QSB-ARTIFACT01-DWH-A/qsb_artifact01_validation_report.json`
- `runs/QSB-ARTIFACT01-DWH-A/qsb_artifact01_registry_report.md`
- `runs/QSB-ARTIFACT01-DWH-A/qsb_artifact01_claim_risk_report.md`
- `runs/QSB-ARTIFACT01-DWH-A/qsb_artifact01_downloads_report.md`
- `runs/QSB-ARTIFACT01-DWH-A/QSB-ARTIFACT01-DWH-A_RUN_SUMMARY.md`

## Claim Boundary

This is an artifact metadata registry dry run only. It contains no physical
confirmation, no spacetime claim, no causality claim, no RELALG computation,
and no public download authorization.
