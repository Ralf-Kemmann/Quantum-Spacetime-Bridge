# QSB-RELALG-NULL01-MIN

Minimal deterministic synthetic nullmodel control run after
`QSB-RELALG-LOOP01-MIN`.

This package creates a sandbox-only run under `runs/QSB-RELALG-NULL01-MIN/`.
It reads the passed LOOP01-MIN artifacts and does not modify prerequisite runs,
production DWH files, Source-Hub content, or project schemas.

## Purpose

NULL01-MIN applies a compact deterministic nullmodel ladder to the passed
LOOP01-MIN synthetic C-layer loop phase baseline. The run checks whether the
loop-phase layer responds to controlled synthetic changes in phase structure,
orientation structure, labels, source coherence, and thresholds.

## Prerequisites

Required prerequisite files:

- `runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json`
- `runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json`
- `runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json`
- `runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json`
- `runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_next_step_gate.json`
- `runs/QSB-RELALG-LOOP01-MIN/qsb_relalg_loop01_min_validation_report.json`

The builder also reads the actual LOOP01-MIN config, synthetic state, pair
relation, loop catalog, and loop phase result artifacts.

## How To Run

```bash
python scripts/qsb_relalg_null01_min/null01_min.py
```

## Replay Protection

The default command refuses to overwrite an existing
`runs/QSB-RELALG-NULL01-MIN/` directory. To regenerate only the NULL01-MIN
outputs:

```bash
python scripts/qsb_relalg_null01_min/null01_min.py --force
```

The `--force` option does not delete or modify prerequisite runs.

## Outputs

- `qsb_relalg_null01_min_config.json`
- `qsb_relalg_null01_min_prerequisite_report.json`
- `qsb_relalg_null01_min_baseline_summary.csv`
- `qsb_relalg_null01_min_nullmodel_registry.csv`
- `qsb_relalg_null01_min_nullmodel_pair_relations.csv`
- `qsb_relalg_null01_min_nullmodel_loop_results.csv`
- `qsb_relalg_null01_min_nullmodel_comparison.csv`
- `qsb_relalg_null01_min_invalid_controls.csv`
- `qsb_relalg_null01_min_threshold_report.csv`
- `qsb_relalg_null01_min_orientation_report.csv`
- `qsb_relalg_null01_min_claim_boundary_report.md`
- `qsb_relalg_null01_min_next_step_gate.json`
- `qsb_relalg_null01_min_manifest.json`
- `qsb_relalg_null01_min_validation_report.json`
- `QSB-RELALG-NULL01-MIN_RUN_SUMMARY.md`

## Nullmodels

- `N00 baseline_replay_control`: replays the LOOP01-MIN baseline from read input.
- `N01 label_permutation_control`: permutes labels while preserving the C-layer phase multiset.
- `N02 global_rephase_control`: applies deterministic local rephasing consistent with AX01/GAUGE01.
- `N03 phase_scrambled_magnitude_preserved`: preserves magnitudes while deterministically scrambling ordered-pair phases.
- `N04 orientation_destroyed_real_positive`: replaces active complex relations with positive magnitudes.
- `N05 conjugate_flip_control`: conjugates active C-layer relation values.
- `N06 threshold_injected_invalid`: forces one ordered pair below the declared thresholds.
- `N07 source_mixed_invalid`: assigns one ordered pair a mixed source label.

## Not Tested

The run does not execute REAL01, source eligibility review, real-data analysis,
plotting, extended nullmodel design, production DWH mutation, Source-Hub
mutation, or schema changes.

## Claim Boundaries

NULL01-MIN is a synthetic nullmodel control run. It introduces no restricted
interpretive claim. See the generated claim-boundary report for explicit
excluded interpretations.

## Next-Step Gate

If validation passes, the next authorized step is
`QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY`. Full real-data execution,
interpretation, and claim steps remain blocked in the gate.
