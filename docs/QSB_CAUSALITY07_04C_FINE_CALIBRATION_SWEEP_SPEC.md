# QSB-CAUSALITY07-04C Fine Calibration Sweep Spec

## Purpose

QSB-CAUSALITY07-04C refines the QSB-CAUSALITY07-04B coarse stable operating region. It is a calibration-refinement block, not a new causal inference block.

The coarse sweep was insufficient for final calibration because its grid spacing was too broad to determine whether an apparently stable point was interior, near a boundary, or accidentally favorable. The 04B stable region also touched grid boundaries, so the upper threshold behavior required a limited extension beyond `theta=0.50`.

## Inputs

The runner reads the QSB-CAUSALITY07-04B outputs and configuration:

- `runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep/weight_threshold_sweep.csv`
- `runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep/stable_operating_window.csv`
- `runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep/calibration_decision_summary.csv`
- `runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep/run_summary.json`
- `data/QSB-CAUSALITY07-04B/heuristic_calibration_config.json`
- `data/QSB-CAUSALITY07-04B/calibration_metric_registry.json`
- `scripts/run_qsb_causality07_04b_heuristic_calibration_sweep.py`

The script reuses the 04B reconstruction functions so that the fine sweep remains comparable with the coarse sweep.

## Predefined Grids

The primary fine grid is:

- `w_t` from `0.60` to `0.80` in steps of `0.02`
- `w_d = 1 - w_t`
- `theta` from `0.20` to `0.50` in steps of `0.01`

The boundary extension grid is:

- `w_t in {0.60, 0.70, 0.80}`
- `theta` from `0.51` to `0.80` in steps of `0.01`

The extension grid is used only to test upper-threshold behavior and is not a replacement for the primary fine grid. The grids are fixed in `data/QSB-CAUSALITY07-04C/fine_calibration_sweep_config.json` before execution.

## Reference Point

The reference point is:

- `w_t = 0.70`
- `w_d = 0.30`
- `theta = 0.35`

It is tracked explicitly and classified as `interior`, `near-boundary`, `boundary`, `unstable`, or `not_in_stable_region` from the computed metrics.

## Metrics

For each parameter point, the run records edge metrics, cycle metrics, predecessor metrics, and local stability metrics. Local stability includes orthogonal and diagonal neighbor agreement, classification-change distance, distance to false-positive points, distance to false-negative points, distance to ambiguous-cycle points, and sweep-boundary status.

Interior depth matters because grid-boundary points can appear stable without observed evidence on all sides. Neighboring-point stability matters because isolated success does not define an operating region. False-positive and false-negative boundaries are both retained because suppressing unsupported edges is not useful if registered cycle edges disappear.

## Robust Interior Criterion

A robust interior operating point must satisfy all of the following:

- exact cycle recovered
- no extra supported edges
- top-1 predecessor recovery equals `1.0`
- cycle unique
- not on a grid boundary
- at least 4 orthogonal neighbors share the same classification where available
- at least 6 of 8 total immediate neighbors share the same classification
- minimum distance to a classification change is at least 2 fine-grid steps
- no unsupported edge appears in the immediate neighborhood
- no true cycle edge disappears in the immediate neighborhood

Boundary points are rejected as robust interior points.

## Candidate Selection

Candidate A maximizes robustness: distance to classification boundary, local stability fraction, distance to false-positive onset, and distance to false-negative onset. Tie-breakers are closeness to the provisional point, lower threshold, then lower time weight.

Candidate B minimizes time dependence among robust interior points. Tie-breakers are greatest boundary distance, highest local stability fraction, and lowest threshold.

These candidates represent different scientific goals and are not merged. Minimum time dependence is not identical to maximum robustness because lower temporal weight may sit closer to a boundary even when it remains admissible.

## Unit and Dimension Discipline

Weights are dimensionless. Thresholds are dimensionless only because they are applied to documented normalized dimensionless score margins. Counts are dimensionless counts. Ranks are ordinal and dimensionless. Model time remains `model_unit_unmapped`; no conversion to seconds is performed.

The weighted score remains dimensionless because both components are normalized dimensionless scores and the weights are dimensionless with sum one. No mixed-unit addition is introduced.

## Outputs

The required command is:

```bash
.venv/bin/python \
  scripts/run_qsb_causality07_04c_fine_calibration_sweep.py \
  --input-root . \
  --output-dir runs/QSB-CAUSALITY07-04C/fine_calibration_sweep \
  --overwrite
```

The runner writes exactly ten files in `runs/QSB-CAUSALITY07-04C/fine_calibration_sweep/`.

## Claim Boundary

This block reports calibration behavior for one reduced-model dataset, one heuristic score, and one predefined fine grid. It does not claim physical causality, emergent time, universal parameter values, laboratory calibration, or independent experimental validation.
