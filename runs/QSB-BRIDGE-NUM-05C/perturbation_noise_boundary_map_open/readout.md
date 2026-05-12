# QSB-BRIDGE-NUM-05C Run Readout

## Run

```text
block_id: QSB-BRIDGE-NUM-05C
run_id: perturbation_noise_boundary_map_open
earliest_sensitive_breakdown_family: magnitude_gaussian_noise_sweep
earliest_sensitive_breakdown_noise_level: 0.02
stop_go_outcome: revise_or_bound_before_real_data
```

## Boundary Map Intuition

05C does not try to prove the scanner. It pushes the synthetic magnitude and phase readouts until they bend, wobble, or break. A breakdown is not an embarrassment in this block; it is the boundary being mapped.

The earliest sensitive family is the first warning light. It marks the perturbation type that reaches a configured failure condition at the lowest noise level.

## Breakdown Threshold Summary

|perturbation_family|breakdown_threshold_estimate|breakdown_condition_met|breakdown_reasons|earliest_sensitive_breakdown_family|
|---|---|---|---|---|
|combined_magnitude_phase_perturbation|0.05|True|geometry_score;nearest_neighbor_recall|False|
|correlated_phase_noise_sweep||False||False|
|edge_dropout_missing_correlation_perturbation|0.05|True|geometry_score;distance_stress;magnetic_low_eigenvalue_shift;hostile_control_gap|False|
|magnitude_gaussian_noise_sweep|0.02|True|nearest_neighbor_recall|True|
|magnitude_multiplicative_noise_sweep|0.05|True|geometry_score;nearest_neighbor_recall|False|
|phase_gaussian_noise_sweep|0.2|True|magnetic_low_eigenvalue_shift|False|
|rank_order_near_degeneracy_perturbation|0.75|True|nearest_neighbor_recall|False|

## Main Findings

- Breakdown or instability is treated as a valid negative finding.
- The earliest sensitive breakdown family is explicitly reported.
- Magnitude, phase, and combined perturbation families are reported separately.
- All thresholds are synthetic method-level thresholds, not physical constants.

## Future Result Discussion Requirement

A separate 05C result discussion should add a human-readable Bauchbild explaining the boundary map in project language.

## Claim Boundary

05C is synthetic and method-level. It does not physically validate QSB or claim spacetime emergence, physical metric recovery, causal structure, de-Broglie confirmation, or real quantum dynamics.
