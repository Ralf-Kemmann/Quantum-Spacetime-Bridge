# QSB-BRIDGE-NUM-05C Perturbation / Noise Boundary Map Spec

## 1. Purpose

QSB-BRIDGE-NUM-05C maps synthetic perturbation boundaries for the magnitude-derived and phase-aware diagnostics used in 05A and 05B.

This block asks where the method-level scanner begins to bend, wobble, or break under controlled noise. Breakdown or instability is a valid negative finding.

## 2. Perturbation Families

Magnitude-side perturbations:

```text
magnitude_gaussian_noise_sweep
magnitude_multiplicative_noise_sweep
rank_order_near_degeneracy_perturbation
edge_dropout_missing_correlation_perturbation
```

Phase-side perturbations:

```text
phase_gaussian_noise_sweep
correlated_phase_noise_sweep
```

Combined perturbation:

```text
combined_magnitude_phase_perturbation
```

## 3. Diagnostics

Magnitude and geometry diagnostics:

```text
geometry_score_vs_noise
hostile_control_gap_vs_noise
nearest_neighbor_recall_vs_noise
rank_order_stability_vs_noise
threshold_graph_jaccard_vs_noise
distance_stress_vs_noise
```

Phase and spectral diagnostics:

```text
loop_flux_rms_vs_phase_noise
magnetic_laplacian_low_eigenvalue_shift_vs_noise
spectral_gap_shift_vs_noise
```

Boundary diagnostic:

```text
breakdown_threshold_estimate
earliest_sensitive_breakdown_family
```

The earliest / most sensitive breakdown family is the perturbation family that reaches a configured breakdown condition at the lowest noise level.

## 4. Breakdown Conditions

A row is marked as broken if one or more configured conditions is reached:

```text
geometry_score <= minimum_geometry_score
nearest_neighbor_recall <= minimum_nearest_neighbor_recall
rank_order_stability <= minimum_rank_order_stability
threshold_graph_jaccard <= minimum_threshold_graph_jaccard
distance_stress >= maximum_distance_stress
loop_flux_rms >= maximum_loop_flux_rms
magnetic_low_eigenvalue_shift >= maximum_low_eigenvalue_shift
```

The thresholds are synthetic method-level thresholds, not physical constants.

## 5. Planned Outputs

Static files:

```text
docs/QSB_BRIDGE_NUM_05C_PERTURBATION_NOISE_BOUNDARY_MAP_SPEC.md
data/qsb_bridge_num_05c_perturbation_noise_boundary_config.yaml
scripts/run_qsb_bridge_num_05c_perturbation_noise_boundary_map.py
docs/QSB_BRIDGE_NUM_05C_RESULT_NOTE.md
```

Run artifacts:

```text
runs/QSB-BRIDGE-NUM-05C/perturbation_noise_boundary_map_open/summary.json
runs/QSB-BRIDGE-NUM-05C/perturbation_noise_boundary_map_open/readout.md
runs/QSB-BRIDGE-NUM-05C/perturbation_noise_boundary_map_open/magnitude_noise_sweep_summary.csv
runs/QSB-BRIDGE-NUM-05C/perturbation_noise_boundary_map_open/phase_noise_sweep_summary.csv
runs/QSB-BRIDGE-NUM-05C/perturbation_noise_boundary_map_open/combined_noise_sweep_summary.csv
runs/QSB-BRIDGE-NUM-05C/perturbation_noise_boundary_map_open/breakdown_threshold_summary.csv
runs/QSB-BRIDGE-NUM-05C/perturbation_noise_boundary_map_open/resolved_config.json
```

## 6. Future Discussion Requirement

After 05C is run, a separate result discussion note should add a human-readable Bauchbild. It should explain that the method is not being proven; the scanner is being pushed until its readouts bend, wobble, or break.

## 7. Claim Boundary

05C is a synthetic method-level boundary map. It does not physically validate QSB, show spacetime emergence, recover a physical metric, derive causal structure, confirm de-Broglie physics, or demonstrate real quantum dynamics.
