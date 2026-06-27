# QSB-RELALG-PREAX01-SYNTH

Team review synthesis and AX01 readiness gate generator.

This package consumes the PREAX01 reviewer response file and creates a
deterministic synthesis package under:

- `runs/QSB-RELALG-PREAX01-SYNTH/`

It does not write the full AX01 contract and does not implement GAUGE01,
LOOP01, NULL01, or REAL01.

## Input

Default input:

```bash
runs/QSB-RELALG-PREAX01-SYNTH/input/2026_06_26TeamAntworten.md
```

If the review file is elsewhere, pass it explicitly:

```bash
python scripts/qsb_relalg_preax01_synth/preax01_synth.py \
  --input path/to/2026_06_26TeamAntworten.md
```

If the input is missing, the builder fails clearly and does not fabricate
reviewer content.

## Run

```bash
python scripts/qsb_relalg_preax01_synth/preax01_synth.py \
  --input runs/QSB-RELALG-PREAX01-SYNTH/input/2026_06_26TeamAntworten.md
```

Replay protection refuses to overwrite:

- `runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth.md`

Use `--force` only when replacing files inside the SYNTH run directory:

```bash
python scripts/qsb_relalg_preax01_synth/preax01_synth.py \
  --input runs/QSB-RELALG-PREAX01-SYNTH/input/2026_06_26TeamAntworten.md \
  --force
```

## Outputs

- `qsb_relalg_preax01_synth.md`
- `qsb_relalg_preax01_consensus_matrix.csv`
- `qsb_relalg_preax01_conflict_matrix.csv`
- `qsb_relalg_preax01_required_definitions.csv`
- `qsb_relalg_preax01_forbidden_terms.csv`
- `qsb_relalg_preax01_next_steps.csv`
- `qsb_relalg_preax01_ax01_readiness_gate.json`
- `qsb_relalg_preax01_claim_boundary_report.md`
- `qsb_relalg_preax01_synth_manifest.json`
- `qsb_relalg_preax01_synth_validation_report.json`
- `QSB-RELALG-PREAX01-SYNTH_RUN_SUMMARY.md`

## Claim Boundary

This is a formal review synthesis and readiness gate only. It introduces no
physical, spacetime, causality, RELALG-computation, or QSB-confirmation claim.
