# QSB-RELALG-AX01-TERM

Minimal terminology and definition contract draft builder.

This package is the authorized follow-up to `QSB-RELALG-PREAX01-SYNTH`. It
creates a terminology contract only. It does not write full AX01 and does not
run GAUGE01, LOOP01, NULL01, REAL01, RELALG computation, or real-data analysis.

## Required Gate

The builder reads:

- `runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json`
- `runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_ax01_readiness_gate.json`

It refuses to continue unless PREAX01-SYNTH has `validation_status=pass` and
authorizes `QSB-RELALG-AX01-TERM`.

## Run

```bash
python scripts/qsb_relalg_ax01_term/ax01_term.py
```

Optional input override:

```bash
python scripts/qsb_relalg_ax01_term/ax01_term.py \
  --preax01-dir runs/QSB-RELALG-PREAX01-SYNTH
```

The builder refuses to overwrite `runs/QSB-RELALG-AX01-TERM/` unless called
with `--force`.

## Outputs

- `qsb_relalg_ax01_term.md`
- `qsb_relalg_ax01_term_definitions.csv`
- `qsb_relalg_ax01_term_symbols.csv`
- `qsb_relalg_ax01_term_transform_rules.csv`
- `qsb_relalg_ax01_term_loop_validity_rules.csv`
- `qsb_relalg_ax01_term_threshold_policy.csv`
- `qsb_relalg_ax01_term_source_coherence_rules.csv`
- `qsb_relalg_ax01_term_forbidden_claims.csv`
- `qsb_relalg_ax01_term_ax01_readiness_gate.json`
- `qsb_relalg_ax01_term_claim_boundary_report.md`
- `qsb_relalg_ax01_term_manifest.json`
- `qsb_relalg_ax01_term_validation_report.json`
- `QSB-RELALG-AX01-TERM_RUN_SUMMARY.md`

## Claim Boundary

This is a terminology contract only. It introduces no physical, spacetime,
causality, gravity-mechanism, theory-confirmation, visual-evidence, reviewer
agreement, RELALG-computation, or real-data-analysis claim.
