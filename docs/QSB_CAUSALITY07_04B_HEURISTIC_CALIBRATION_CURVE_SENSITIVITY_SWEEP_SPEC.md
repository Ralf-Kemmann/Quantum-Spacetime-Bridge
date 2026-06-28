# QSB-CAUSALITY07-04B Heuristic Calibration Curve Sensitivity Sweep Spec

## Purpose

QSB-CAUSALITY07-04B calibrates the heuristic reconstruction rule introduced in QSB-CAUSALITY07-04A. The rule combines a normalized temporal transition-frequency score and a normalized derivative-alignment score:

`S = w_t * S_temporal + w_d * S_derivative`, with `w_t + w_d = 1`.

This block treats the rule as a reduced-model instrument that requires calibration. A single successful working point is not accepted as a stable operating region. The sweep maps parameter choice to reconstruction quality, false-positive behavior, predecessor recovery, cycle recovery, and local grid stability.

## Inputs

The runner reads the QSB-CAUSALITY07-04A reconstruction method and required prior artifacts, including:

- `runs/QSB-CAUSALITY07-04A/independent_transition_reconstruction/pairwise_transition_score_matrix.csv`
- `runs/QSB-CAUSALITY07-04A/independent_transition_reconstruction/predecessor_ranking_matrix.csv`
- `runs/QSB-CAUSALITY07-04A/independent_transition_reconstruction/global_cycle_reconstruction.csv`
- `runs/QSB-CAUSALITY07-04A/independent_transition_reconstruction/edge_ablation_control_matrix.csv`
- `runs/QSB-CAUSALITY07-04A/independent_transition_reconstruction/reconstruction_leakage_audit.csv`
- `runs/QSB-CAUSALITY07-04A/independent_transition_reconstruction/resolved_reconstruction_config.json`
- `data/QSB-CAUSALITY07-04A/reconstruction_rule_registry.json`
- `scripts/run_qsb_causality07_04a_independent_transition_reconstruction.py`

The sweep recomputes the label-blind candidate sectors from the QSB-CAUSALITY07-02 post-transient series using the same QSB-CAUSALITY07-04A reconstruction inputs. Labels and known predecessor identities are used only after reconstruction for evaluation.

## Parameter Grid

The coarse grid is predefined in `data/QSB-CAUSALITY07-04B/heuristic_calibration_config.json`.

- `w_t`: `0.0, 0.1, ..., 1.0`
- `w_d`: `1 - w_t`
- `theta`: `0.00, 0.05, ..., 0.50`

No secondary refinement sweep is used in this block. The grid is not changed after result inspection.

## Reference Edge Sets

Registered positive edges are fixed before the sweep:

- `S0->S1`
- `S1->S2`
- `S2->S3`
- `S3->S4`
- `S4->S0`

All other directed non-self candidate edges are retained as negative or unsupported edges. The edge `S4->S1` is explicitly tracked because QSB-CAUSALITY07-04A classified it as forward-supported at the working point despite zero observed transition count.

## Metrics

For each parameter point, the runner records edge-level, cycle-level, predecessor, artefact, and stability metrics. Undefined divisions are recorded with empty numeric values and explicit status fields rather than substituted values.

The operating-region classes are:

- `exact_cycle_no_extra_edges`
- `exact_cycle_with_extra_edges`
- `partial_cycle`
- `ambiguous_cycle`
- `cycle_not_recovered`
- `insufficient_information`

A candidate stable operating window requires exact recovery of the five registered edges, zero unsupported supported edges, complete top-1 predecessor recovery or an explicit thresholded rule, unique cycle status, neighboring grid-point consistency, and no hidden unit or dimension assumption.

## Unit and Dimension Discipline

Both score components are normalized scores and are treated as unitless and dimensionless after documented normalization. The weights are dimensionless by construction and sum to one. Therefore weighted addition is algebraically permitted inside the normalized score coordinate system.

Counts and ranks are dimensionless counts or ordinal quantities. Model time remains `model_unit_unmapped`; no conversion to seconds is performed. The threshold is dimensionless only as a threshold applied to a documented dimensionless normalized score margin.

## Calibration Rationale

Heuristics are legitimate starting points when a reduced-model reconstruction rule is explicit, reproducible, and bounded by claim discipline. Calibration is required because a working point can succeed for contingent reasons and can still admit artefacts. This block is analogous to a laboratory calibration curve only in the methodological sense that it maps input settings to observed instrument behavior; it is not a laboratory calibration and does not provide independent experimental validation.

The distinction between a working point and a stable operating region is central. A working point is one parameter setting. A stable operating region is a connected portion of the predefined grid where the relevant classification remains locally stable and false-positive behavior is acceptable under the declared rule.

False positives and false negatives are both retained. Raising the threshold may suppress unsupported edges while risking loss of registered edges; lowering it may recover registered edges while admitting unsupported edges. The predefined grid prevents selecting only favorable points after inspection.

`S4->S1` is a critical artefact monitor because its prior support came from derivative alignment rather than observed transition frequency. Geometry-only failure is scientifically informative because it shows that derivative/geometry information alone does not reproduce the full predecessor structure in this reduced setting. Time dependence is not label leakage: explicit model time is a reconstruction input, whereas phase labels, registered cycle order, and known predecessors remain excluded from reconstruction.

## Outputs

The required command is:

```bash
.venv/bin/python \
  scripts/run_qsb_causality07_04b_heuristic_calibration_sweep.py \
  --input-root . \
  --output-dir runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep \
  --overwrite
```

The runner writes exactly ten files in `runs/QSB-CAUSALITY07-04B/heuristic_calibration_sweep/`:

1. `resolved_calibration_config.json`
2. `weight_threshold_sweep.csv`
3. `edge_classification_sweep.csv`
4. `predecessor_metric_sweep.csv`
5. `cycle_reconstruction_sweep.csv`
6. `stable_operating_window.csv`
7. `calibration_decision_summary.csv`
8. `semantic_validation_checks.csv`
9. `run_summary.json`
10. `readout.md`

## Claim Boundary

This block contributes a transparent reduced-model calibration map for the QSB-CAUSALITY07-04A heuristic. It does not claim physical causality, emergent time, universal parameter values, experimental calibration, independent laboratory validation, or global validity beyond this model, dataset, and predefined grid.
