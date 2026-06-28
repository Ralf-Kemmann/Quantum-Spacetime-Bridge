# QSB-CAUSALITY07-04C Final Result Note

## Befund

The fine calibration sweep was run with:

```bash
.venv/bin/python scripts/run_qsb_causality07_04c_fine_calibration_sweep.py --input-root . --output-dir runs/QSB-CAUSALITY07-04C/fine_calibration_sweep --overwrite
```

The primary fine grid contained 341 points: `w_t=0.60..0.80` in steps of `0.02` and `theta=0.20..0.50` in steps of `0.01`. The boundary extension grid contained 90 points: `w_t in {0.60, 0.70, 0.80}` and `theta=0.51..0.80` in steps of `0.01`. Total evaluated point count was 431.

The provisional point `(w_t=0.70, w_d=0.30, theta=0.35)` was classified as `exact_cycle_no_extra_edges` and as a robust interior point. It had 0 false positives, 0 false negatives, local stability fraction `1.00000000`, and classification-change distance `13.00000000`.

The primary fine grid contained 314 `exact_cycle_no_extra_edges` points. The run identified 234 robust interior points. The final calibration class was `robust_interior_operating_point_identified`, with final status `fine_calibration_sweep_completed`.

Candidate A, selected by maximum robustness, was:

- `w_t=0.78`
- `w_d=0.22`
- `theta=0.49`
- classification `exact_cycle_no_extra_edges`
- robust interior `yes`
- classification-change distance `31.00000000`
- false-positive distance `23.76972865`
- local stability fraction `1.00000000`

Candidate B, selected by minimum time dependence among robust interior points, was:

- `w_t=0.62`
- `w_d=0.38`
- `theta=0.49`
- classification `exact_cycle_no_extra_edges`
- robust interior `yes`
- classification-change distance `23.00000000`
- false-positive distance `22.02271555`
- local stability fraction `1.00000000`

False-positive points occurred at 27 of 431 evaluated points. The earliest false-positive onset by threshold ordering was `(w_t=0.60, theta=0.20)`. The tracked unsupported edge `S4->S1` was supported at 27 of 431 points.

False-negative points occurred at 2 of 431 evaluated points. The first false-negative onset in the upper-threshold extension was `(w_t=0.60, theta=0.79)`, which also resolved the observed upper-threshold boundary in the evaluated extension.

The semantic validation table contains 47 checks and 0 failed checks. The run directory contains exactly ten files.

## Interpretation

The fine sweep confirms the 04B coarse finding in the refined window: a false-positive-free region persists at higher resolution. The provisional point is not merely an isolated favorable point under the implemented criterion; it has immediate-neighborhood support and is not on the primary sweep boundary.

Candidate A and Candidate B remain distinct. Candidate A favors maximum interior robustness and lies at higher temporal weight. Candidate B favors lower time dependence while still satisfying the robust interior rule.

## Hypothese

Within this reduced-model dataset and score definition, the operating region around the provisional point appears robust under the predefined fine grid. This is an internal calibration finding only.

## Offene Luecke

The result remains limited by reduced-model data, absence of laboratory calibration, absence of an independent experimental dataset, finite predefined grids, heuristic score definition, unmapped model time, and validity only for this dataset and score. The false-negative boundary was only probed by the specified upper-threshold extension, not by an unrestricted search.

## Claim Boundary

This note does not claim physical causality, emergent time, universal parameter values, laboratory validation, independent experimental confirmation, or global applicability. It reports only the QSB-CAUSALITY07-04C fine calibration outputs.
