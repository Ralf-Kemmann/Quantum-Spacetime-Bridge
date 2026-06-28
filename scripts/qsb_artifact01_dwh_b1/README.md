# QSB-ARTIFACT01-DWH-B1

Sandbox-only visualization panel artifact registry dry run for the QSB-EXTRACT03
VIZ02 combined topology panel PNG.

This package creates a standalone SQLite registry under
`runs/QSB-ARTIFACT01-DWH-B1/`. It does not mutate a production DWH, Source-Hub,
EXTRACT, META, MAP01, ARTIFACT01-A/B, or any existing project schema. It does
not move, delete, rewrite, overwrite, or regenerate the input PNG.

## Input

Required PNG:

- `runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix/20_combined_topology_organized_matrix_panel.png`

Optional prior registry:

- `runs/QSB-ARTIFACT01-DWH-B/qsb_artifact01_viz.sqlite`

When the prior B registry exists, this dry run records `panel_of` relations as
external relation references to the five VIZ02 component-ordered heatmap
artifact IDs. The prior B registry is not modified.

## Run

```bash
python scripts/qsb_artifact01_dwh_b1/qsb_artifact01_dwh_b1.py
```

The builder refuses to overwrite
`runs/QSB-ARTIFACT01-DWH-B1/qsb_artifact01_viz_panel.sqlite` unless called with
`--force`. The `--force` mode deletes only files inside
`runs/QSB-ARTIFACT01-DWH-B1/` and never touches the input PNG or prior B
registry.

## Expected Outputs

- `runs/QSB-ARTIFACT01-DWH-B1/qsb_artifact01_viz_panel.sqlite`
- `runs/QSB-ARTIFACT01-DWH-B1/qsb_artifact01_viz_panel_seed_manifest.json`
- `runs/QSB-ARTIFACT01-DWH-B1/qsb_artifact01_viz_panel_validation_report.json`
- `runs/QSB-ARTIFACT01-DWH-B1/qsb_artifact01_viz_panel_registry_report.md`
- `runs/QSB-ARTIFACT01-DWH-B1/qsb_artifact01_viz_panel_claim_risk_report.md`
- `runs/QSB-ARTIFACT01-DWH-B1/qsb_artifact01_viz_panel_downloads_report.md`
- `runs/QSB-ARTIFACT01-DWH-B1/QSB-ARTIFACT01-DWH-B1_RUN_SUMMARY.md`

## Claim Boundary

The combined panel is a high-risk presentation-style visual overview artifact.
It is for internal review and orientation only, not physical proof. No public
publishing is authorized.
