# Block B — Small Parameter Robustness

This script runs the small Block B grid over:
- a1_stabilization_ceiling: 0.85, 0.95
- a1_neighbor_min: 3, 4
- b1_conflict_penalty: 1.0, 1.25

for every focal unit in one launchable export.

Example:

```bash
python block_b_small_parameter_robustness.py   --export ./real_local_export_from_npz_negative.json   --mapping ./compatibility_local_model_mapping_npz_negative_v1.json   --outdir ./results_block_b_negative   --label negative
```
