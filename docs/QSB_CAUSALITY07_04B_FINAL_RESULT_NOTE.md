# QSB-CAUSALITY07-04B Final Result Note

## Befund

The required sweep was run with:

```bash
.venv/bin/python scripts/run_qsb_causality07_04b_heuristic_calibration_sweep.py --input-root . --output-dir runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep --overwrite
```

The sweep evaluated 121 parameter points: 11 temporal weights times 11 direction thresholds. The weight grid was `0.0` through `1.0` in steps of `0.1`; the threshold grid was `0.00` through `0.50` in steps of `0.05`. No secondary refinement sweep was used.

At the QSB-CAUSALITY07-04A working point (`w_t=0.7`, `w_d=0.3`, `theta=0.20`), the registered five-edge cycle was recovered and top-1 predecessor recovery was `1.00000000`. The same point retained one false-positive supported edge, and the tracked unsupported edge `S4->S1` was supported.

Across the full grid:

- `exact_cycle_no_extra_edges`: 46 points.
- `exact_cycle_with_extra_edges`: 64 points.
- `ambiguous_cycle`: 10 points.
- `cycle_not_recovered`: 1 point.
- `S4->S1` was supported at 75 of 121 points.
- The minimum `w_t` for exact cycle recovery was `0.1`.
- The minimum `w_t` for top-1 predecessor recovery of `1.0` was `0.3`.
- The minimum `w_t` for zero false positives was `0.3`.

At the current threshold `theta=0.20`, the geometry-only point (`w_t=0.0`) was classified as `ambiguous_cycle`, with top-1 predecessor recovery `0.6` and 4 false positives. The time-only point (`w_t=1.0`) was classified as `exact_cycle_no_extra_edges`, with top-1 predecessor recovery `1.0` and 0 false positives.

The runner wrote exactly ten run-output files in `runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep/`. The semantic validation table contains 47 checks and 0 failed checks.

## Interpretation

The calibration sweep reproduces the QSB-CAUSALITY07-04A working-point result but also confirms the review concern: the working point is not false-positive-free because `S4->S1` remains supported.

The predefined grid identifies a connected false-positive-free region under the implemented stability rule. The primary calibration class recorded in `calibration_decision_summary.csv` is `stable_false_positive_free_operating_window_identified`, with final status `heuristic_calibration_sweep_completed`.

The geometry-only result is not sufficient for full reconstruction in this sweep. The improvement from `w_t=0.0` to larger temporal weights indicates that explicit model-time transition information materially affects reconstruction. This is time dependence, not label leakage, because phase labels and known predecessor identities are not used as reconstruction inputs.

## Hypothese

Within this reduced model and this predefined grid, the heuristic appears to have a parameter region in which the registered five-edge cycle is recovered and unsupported supported edges are suppressed. This should be treated as an internal calibration finding for this dataset, not as a universal parameter prescription.

## Offene Luecke

The block remains limited by reduced-model data, absence of laboratory calibration, absence of an independent experimental dataset, a heuristic score definition, a finite parameter grid, unmapped model time, and a partly conventional state-space metric. The result does not determine whether the same operating region would survive a different model, different observable projection, or independent data source.

## Claim Boundary

This note does not claim physical causality, spacetime emergence, emergent time, universal threshold values, universal weight values, laboratory validation, or global reconstruction uniqueness. It reports only the behavior of the declared QSB-CAUSALITY07-04B calibration sweep on the stated reduced-model artifacts.
