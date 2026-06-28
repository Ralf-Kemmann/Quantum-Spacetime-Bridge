# QSB-ARTIFACT01-DWH-B

Sandbox-only visualization artifact registry dry run for existing
QSB-EXTRACT03 PNG heatmaps.

This package creates a standalone SQLite registry under
`runs/QSB-ARTIFACT01-DWH-B/`. It does not mutate a production DWH, Source-Hub,
EXTRACT, META, MAP01, ARTIFACT01-A, or any existing project schema. It does not
move, rewrite, delete, overwrite, or regenerate input PNG files.

## Input Roots

- `runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization/`
- `runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/`

## Files

- `schema.sql` defines the local artifact registry tables and views.
- `qsb_artifact01_dwh_b.py` registers expected PNG heatmaps, computes hashes
  and sizes, records lineage, claim boundaries, reviews, caption indexes,
  exports, relations, and validation results.

## Run

```bash
python scripts/qsb_artifact01_dwh_b/qsb_artifact01_dwh_b.py
```

The builder refuses to overwrite
`runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz.sqlite` unless called with
`--force`. The `--force` mode deletes only files inside
`runs/QSB-ARTIFACT01-DWH-B/` and never touches input PNG files.

Expected generated files:

- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz.sqlite`
- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz_seed_manifest.json`
- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz_validation_report.json`
- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz_registry_report.md`
- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz_claim_risk_report.md`
- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz_downloads_report.md`
- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz_gallery_index.md`
- `runs/QSB-ARTIFACT01-DWH-B/QSB-ARTIFACT01-DWH-B_RUN_SUMMARY.md`

## Claim Boundary

This is a visualization artifact metadata registry dry run only. The heatmaps
are internal review artifacts and presentation candidates, not physical proof.
No public publishing is authorized.
