# NPZ to Local Export Converter

This converter bridges the project matrix artifacts to the real-export runner.

Current first-pass mapping choice:
- source carrier: `kbar`
- support strength: `abs(kbar_ij)`
- support sector: `sign(kbar_ij)` mapped to `-1/+1`
- pair-unit selection:
  - default: `G[i,j] != 0`
- immediate neighbors:
  - pair-units sharing one endpoint

Example:

```bash
python convert_npz_to_local_export.py \
  --input ./results/a1_probe/k0/negative/matrices.npz \
  --output ./real_local_export_from_npz.json
```

Then run:

```bash
python run_compatibility_first_pass_real_export.py \
  --config ./compatibility_real_export_run_config_example.json \
  --outdir ./results_real_export_example
```

with:
- `raw_export_path` pointed to the generated JSON
- `mapping_path` pointed to your mapping JSON
