# QSB-RELALG-SYNTH-D1K-BRIDGE

## Purpose

`QSB-RELALG-SYNTH-D1K-BRIDGE` builds a minimal synthetic bridge from the D1K deterministic synthetic phase-field exposure table into a RELALG-compatible ordered-pair C-layer export.

This is a synthetic diagnostic bridge only. It is not REAL01, not a physical phase source, not a physical C-layer source, and not evidence for physical Bridge validation or any spacetime, metric, gravity, or causal claim.

## Inputs

- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv`
- `runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv`

Optional German metadata linkage files are referenced when present:

- `scripts/sqlite_views/v_de_d1k_phase_source_status.sql`
- `scripts/sqlite_views/register_v_de_d1k_phase_source_status_metadata.sql`

## Generated Outputs

The script writes outputs under:

- `runs/QSB-RELALG-SYNTH-D1K-BRIDGE/`

Required artifacts:

- `qsb_relalg_synth_d1k_bridge_c_layer.csv`
- `qsb_relalg_synth_d1k_bridge_preflight.csv`
- `qsb_relalg_synth_d1k_bridge_validation_report.json`
- `qsb_relalg_synth_d1k_bridge_next_step_gate.json`
- `qsb_relalg_synth_d1k_bridge_manifest.json`
- `qsb_relalg_synth_d1k_bridge_claim_boundary.md`
- `qsb_relalg_synth_d1k_bridge_readout.md`
- `qsb_relalg_synth_d1k_bridge_summary.json`

## C-Layer Convention

The exported ordered-pair relation uses:

```text
C_AB = exp(i * delta_phi_wrapped)
```

Mappings:

- `A_id = D1F.wave_id_i`
- `B_id = D1F.wave_id_j`
- `source_pair_id = D1F.pair_id`
- `source_case_id = case_id`
- `C_real = D1K.cos_delta_phi`
- `C_imag = D1K.sin_delta_phi`
- `C_abs = sqrt(C_real^2 + C_imag^2)`
- `C_arg = D1K.delta_phi_wrapped`

## Claim Boundary

Every generated artifact is bounded by:

- synthetic diagnostic only
- not REAL01 evidence
- not a physical phase source
- not a physical C-layer source
- no physical Bridge validation
- no spacetime, metric, gravity, or causal claim

The C-layer rows carry:

- `evidence_class = synthetic_diagnostic_c_layer_from_d1k`
- `allowed_use = synthetic RELALG loop/nullmodel/control tests only`
- `blocked_use = REAL01 evidence; physical phase claim; physical C-layer source; Bridge validation; spacetime/metric/gravity interpretation`
- `claim_boundary = synthetic diagnostic D1K-to-RELALG bridge only`

## Why This Is Not REAL01

The source phase fields are D1K deterministic synthetic diagnostic exposure rows. The bridge does not read REAL01 rows, does not mutate REAL01 files, and does not authorize REAL01 staging, execution, interpretation, or physics claims.

## Run And Validate

Run from the repository root:

```bash
python scripts/qsb_relalg_synth_d1k_bridge/relalg_synth_d1k_bridge.py
```

The default run refuses to overwrite an existing output directory. To intentionally replace the run output directory:

```bash
python scripts/qsb_relalg_synth_d1k_bridge/relalg_synth_d1k_bridge.py --force
```

Local validation commands:

```bash
python -m py_compile scripts/qsb_relalg_synth_d1k_bridge/relalg_synth_d1k_bridge.py
python scripts/qsb_relalg_synth_d1k_bridge/relalg_synth_d1k_bridge.py
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_validation_report.json
python -m json.tool runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_next_step_gate.json
python scripts/qsb_relalg_synth_d1k_bridge/relalg_synth_d1k_bridge.py
git diff --check
git status --short
```

The second normal script run is expected to refuse overwrite unless `--force` is supplied.

## German Metadata Linkage

The optional German D1K SQL view metadata records how phase-source status is exposed for German-language inspection. Linking these files in the manifest and readout helps keep the synthetic phase-source boundary visible across both code output and metadata review surfaces. Their absence does not fail this bridge run.
