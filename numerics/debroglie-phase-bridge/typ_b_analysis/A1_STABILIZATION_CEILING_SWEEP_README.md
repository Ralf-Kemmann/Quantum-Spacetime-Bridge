# A1 Stabilization-Ceiling Sweep

Sweep the A1 stabilization ceiling while keeping:
- export
- mapping
- focal-unit construction
- A1 core formula

fixed.

Example:

```bash
python a1_stabilization_ceiling_sweep.py \
  --export ./real_local_export_from_npz_negative.json \
  --mapping ./compatibility_local_model_mapping_npz_negative_v1.json \
  --outdir ./results_a1_ceiling_sweep_negative
```

Optional custom grid:

```bash
python a1_stabilization_ceiling_sweep.py \
  --export ./real_local_export_from_npz_negative.json \
  --mapping ./compatibility_local_model_mapping_npz_negative_v1.json \
  --outdir ./results_a1_ceiling_sweep_negative \
  --ceilings 0.85 0.90 0.95 0.99 1.01
```

Outputs:
- `a1_ceiling_sweep_focal_rows.csv`
- `a1_ceiling_sweep_summary.csv`
- `summary.json`
