# A1 Ceiling + Neighbor-Count Sweep

Jointly sweep:
- `a1_stabilization_ceiling`
- `neighbor_min`

with the reformed anti-stabilization rule:

```text
late_stage iff (a1_score >= ceiling) AND (neighbor_count >= neighbor_min)
```

Example:

```bash
python A1_ceiling_neighborcount_sweep.py   --export ./real_local_export_from_npz_negative.json   --mapping ./compatibility_local_model_mapping_npz_negative_v1.json   --outdir ./results_a1_ceiling_neighborcount_sweep_negative
```

Outputs:
- `a1_ceiling_neighborcount_focal_rows.csv`
- `a1_ceiling_neighborcount_summary.csv`
- `summary.json`
