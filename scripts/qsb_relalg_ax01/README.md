# QSB-RELALG-AX01

Minimal formal contract draft builder.

This package creates a sandbox-only AX01 formal contract under
`runs/QSB-RELALG-AX01/`. It reads the passed PREAX01-SYNTH and AX01-TERM gates
and refuses to run if prerequisites are missing or not passed.

## Purpose

AX01 defines symbols, admissibility rules, C/K layer separation, transformation
rules, loop-phase admissibility, threshold policy, source-coherence policy, and
the next-step gate.

It does not perform numerical RELALG computation, loop diagnostics, nullmodel
execution, synthetic GAUGE01 test generation, or real-data analysis.

## Inputs

- `runs/QSB-RELALG-PREAX01-SYNTH/`
- `runs/QSB-RELALG-AX01-TERM/`

Required gates:

- PREAX01-SYNTH validation status: `pass`
- AX01-TERM validation status: `pass`
- AX01-TERM next authorized step: `QSB-RELALG-AX01`

## Run

```bash
python scripts/qsb_relalg_ax01/ax01.py
```

Replay protection refuses to overwrite an existing run directory. To regenerate
only `runs/QSB-RELALG-AX01/`:

```bash
python scripts/qsb_relalg_ax01/ax01.py --force
```

## Outputs

- `qsb_relalg_ax01_contract.md`
- `qsb_relalg_ax01_definitions.csv`
- `qsb_relalg_ax01_symbol_table.csv`
- `qsb_relalg_ax01_admissibility_rules.csv`
- `qsb_relalg_ax01_transformation_rules.csv`
- `qsb_relalg_ax01_threshold_policy.csv`
- `qsb_relalg_ax01_orientation_arg_policy.csv`
- `qsb_relalg_ax01_source_coherence_rules.csv`
- `qsb_relalg_ax01_forbidden_claims.csv`
- `qsb_relalg_ax01_next_step_gate.json`
- `qsb_relalg_ax01_claim_boundary_report.md`
- `qsb_relalg_ax01_manifest.json`
- `qsb_relalg_ax01_validation_report.json`
- `QSB-RELALG-AX01_RUN_SUMMARY.md`

## Validation Rules

The builder implements V01-V22, including prerequisite gate checks, required
file checks, mandatory symbol checks, C/K separation, C-layer Phi admissibility,
threshold blocking, orientation/arg/source-coherence gates, next-step gate
checks, claim scanning, and no-computation assertions.

## Claim Boundaries

AX01 is a formal contract draft only. It introduces no restricted interpretive
claim and does not use visual artifacts or reviewer agreement as evidence.

## Blocked Next Steps

Only `QSB-RELALG-GAUGE01` is authorized as the next draft/test-design step
after human review. `QSB-RELALG-LOOP01`, `QSB-RELALG-NULL01`, and
`QSB-RELALG-REAL01` remain blocked.
