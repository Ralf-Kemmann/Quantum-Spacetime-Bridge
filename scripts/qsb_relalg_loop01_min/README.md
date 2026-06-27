# QSB-RELALG-LOOP01-MIN

Minimal deterministic synthetic loop diagnostic run after `QSB-RELALG-GAUGE01`.

This package creates a sandbox-only run under `runs/QSB-RELALG-LOOP01-MIN/`.
It uses synthetic normalized complex vectors only. It does not use real data and
does not mutate prerequisite runs, production DWH files, or Source-Hub content.

## Inputs

Required prerequisite files:

- `runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json`
- `runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json`
- `runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json`
- `runs/QSB-RELALG-AX01/qsb_relalg_ax01_next_step_gate.json`
- `runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json`
- `runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_next_step_gate.json`

Required statuses:

- `PREAX01-SYNTH validation_status = pass`
- `AX01-TERM validation_status = pass`
- `AX01 validation_status = pass`
- `GAUGE01 validation_status = pass`
- `GAUGE01 gauge01_status = synthetic_rephasing_invariance_passed`

The GAUGE01 gate may record `QSB-RELALG-LOOP01-DESIGN` as the previous next
step. This run records the human re-scope to `QSB-RELALG-LOOP01-MIN` in the
manifest and run summary.

## Run

```bash
python scripts/qsb_relalg_loop01_min/loop01_min.py
```

Replay protection refuses to overwrite an existing run directory. To regenerate
only `runs/QSB-RELALG-LOOP01-MIN/`:

```bash
python scripts/qsb_relalg_loop01_min/loop01_min.py --force
```

## Outputs

- `qsb_relalg_loop01_min_config.json`
- `qsb_relalg_loop01_min_synthetic_states.csv`
- `qsb_relalg_loop01_min_pair_relations.csv`
- `qsb_relalg_loop01_min_loop_catalog.csv`
- `qsb_relalg_loop01_min_loop_phase_results.csv`
- `qsb_relalg_loop01_min_orientation_reversal_checks.csv`
- `qsb_relalg_loop01_min_invalid_loop_controls.csv`
- `qsb_relalg_loop01_min_source_coherence_checks.csv`
- `qsb_relalg_loop01_min_threshold_checks.csv`
- `qsb_relalg_loop01_min_claim_boundary_report.md`
- `qsb_relalg_loop01_min_manifest.json`
- `qsb_relalg_loop01_min_validation_report.json`
- `qsb_relalg_loop01_min_next_step_gate.json`
- `QSB-RELALG-LOOP01-MIN_RUN_SUMMARY.md`

## Diagnostic Contract

The run computes ordered pair relations `C_AB = <psi_A | psi_B>` and reference
magnitudes `K_AB = |C_AB|`. For each valid ordered triple `(A, B, C)`, it
computes `P_ABC = C_AB * C_BC * C_CA` and `Phi_ABC = arg(P_ABC)` from the
C-layer product only.

Invalid controls are blocked and do not produce active `Phi_ABC` values:

- repeated node
- missing relation
- mixed source space
- pair threshold failure
- product threshold failure
- K-only phase attempt

## Claim Boundary

LOOP01-MIN is a formal synthetic diagnostic only. It does not perform NULL01,
REAL01, real-data analysis, plotting, physical interpretation, or production
mutation.
