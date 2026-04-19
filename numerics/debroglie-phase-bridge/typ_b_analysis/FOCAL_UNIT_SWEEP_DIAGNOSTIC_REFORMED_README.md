# Focal-Unit Sweep Diagnostics — Reformed A1

This sweep uses the reformed A1 anti-stabilization rule:

```text
late_stage iff (a1_score >= a1_stabilization_ceiling) AND (neighbor_count >= a1_neighbor_min)
```

Example:

```bash
python focal_unit_sweep_diagnostic_reformed.py   --export ./real_local_export_from_npz_negative.json   --mapping ./compatibility_local_model_mapping_npz_negative_v1.json   --outdir ./results_focal_sweep_negative_reformed
```
