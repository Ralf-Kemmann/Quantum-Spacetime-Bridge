# Focal-Unit Sweep Diagnostics

Run all focal units in one export through the current A1/B1 proxy logic.

Example:

```bash
python focal_unit_sweep_diagnostic.py \
  --export ./real_local_export_from_npz_negative.json \
  --mapping ./compatibility_local_model_mapping_npz_negative_v1.json \
  --outdir ./results_focal_sweep_negative
```

Outputs:
- `focal_unit_sweep.csv`
- `summary.json`

Purpose:
- test whether one focal unit is a special case
- inspect whether A1 collapse or B1 lead is systematic across the export
