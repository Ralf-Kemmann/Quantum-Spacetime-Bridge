# QSB-RELALG-GAUGE01

Synthetic rephasing invariance test for the AX01 canonical Level-1 reference
case.

This package creates a sandbox-only run under `runs/QSB-RELALG-GAUGE01/`.
It uses deterministic synthetic complex vectors only. It does not use real data
and does not mutate prerequisite runs or production files.

## Inputs

Required prerequisite gates:

- `runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json`
- `runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json`
- `runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_ax01_readiness_gate.json`
- `runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json`
- `runs/QSB-RELALG-AX01/qsb_relalg_ax01_next_step_gate.json`

AX01 must authorize only `QSB-RELALG-GAUGE01` and keep LOOP01, NULL01, and
REAL01 blocked.

## Run

```bash
python scripts/qsb_relalg_gauge01/gauge01.py
```

Replay protection refuses to overwrite an existing run directory. To regenerate
only `runs/QSB-RELALG-GAUGE01/`:

```bash
python scripts/qsb_relalg_gauge01/gauge01.py --force
```

## Outputs

- `qsb_relalg_gauge01_config.json`
- `qsb_relalg_gauge01_synthetic_states.csv`
- `qsb_relalg_gauge01_rephasing_cases.csv`
- `qsb_relalg_gauge01_pair_relations.csv`
- `qsb_relalg_gauge01_pair_relation_invariance.csv`
- `qsb_relalg_gauge01_loop_phase_invariance.csv`
- `qsb_relalg_gauge01_invalid_loop_controls.csv`
- `qsb_relalg_gauge01_result_note.md`
- `qsb_relalg_gauge01_claim_boundary_report.md`
- `qsb_relalg_gauge01_next_step_gate.json`
- `qsb_relalg_gauge01_manifest.json`
- `qsb_relalg_gauge01_validation_report.json`
- `QSB-RELALG-GAUGE01_RUN_SUMMARY.md`

## Validation

The builder implements V01-V22, including prerequisite gate checks,
normalization checks, pair transformation checks, magnitude invariance checks,
valid loop phase circular-delta checks, blocked invalid controls, claim scanning,
manifest checks, and replay-protection reporting.

## Claim Boundary

GAUGE01 is a synthetic rephasing invariance test only. It is not LOOP01, NULL01,
REAL01, or an interpretive step.

## Next Step

If validation passes, the next authorized step is `QSB-RELALG-LOOP01-DESIGN`.
`QSB-RELALG-LOOP01-EXECUTION`, `QSB-RELALG-NULL01`, and
`QSB-RELALG-REAL01` remain blocked.
