# QSB-BRIDGE-NUM-05A Geometric Validation & Hostile Controls Spec

## 1. Purpose

QSB-BRIDGE-NUM-05A tests whether magnitude-derived distance and graph diagnostics can separate controlled geometric baselines from hostile controls.

This block follows the Red-Team roadmap in:

```text
docs/QSB_BRIDGE_NEXT_AFTER_RED_TEAM_2026_05_12.md
```

It is a method-level validation and failure-boundary block. It is not a physical validation block.

## 2. Claim Boundary

05A does not validate QSB physically.

It does not show:

```text
spacetime emergence
physical metric recovery
causal structure
de-Broglie confirmation
physical geometry reconstruction
```

All readouts are synthetic control diagnostics. A hostile control matching or outperforming a geometric baseline is a possible negative finding and must be reported as such.

## 3. Geometric Baselines

Geometric baselines use known coordinates so that distance-like diagnostics can be compared to a known synthetic geometry:

```text
baseline_1d_ring
baseline_2d_torus_grid
baseline_random_geometric
```

For each baseline, a coordinate distance matrix `G_ij` is built first. The magnitude matrix is then:

```text
|K_ij| = exp(-G_ij / l0)
|K_ii| = 1
```

The reconstructed distance-like matrix is:

```text
D_ij = -l0 * log(max(|K_ij|, epsilon))
```

## 4. Hostile Controls

Hostile controls are reported separately from geometric baselines:

```text
control_distribution_matched_random_magnitude
control_non_geometric_block_matrix
control_near_degenerate_magnitude
control_node_permutation
control_gaussian_magnitude_perturbation
```

The node permutation control is expected to preserve invariant diagnostics when compared after undoing the permutation. Other hostile controls may expose false positives or fragility.

## 5. Diagnostics

Core diagnostics:

```text
coordinate_distance_correlation
shortest_path_distance_error_vs_known_geometry
nearest_neighbor_recall_vs_known_geometry
triangle_inequality_violation_rate
distance_stress
threshold_graph_edge_count
threshold_graph_jaccard
false_positive_geometry_score
control_gap_vs_geometric_baseline
```

Sensitivity diagnostics:

```text
tau_sensitivity_summary
l0_sensitivity_summary
n_sensitivity_summary
```

## 6. Planned Outputs

Static files:

```text
docs/QSB_BRIDGE_NUM_05A_GEOMETRIC_VALIDATION_HOSTILE_CONTROLS_SPEC.md
data/qsb_bridge_num_05a_geometric_validation_config.yaml
scripts/run_qsb_bridge_num_05a_geometric_validation.py
docs/QSB_BRIDGE_NUM_05A_RESULT_NOTE.md
```

Run artifacts:

```text
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/summary.json
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/readout.md
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/variant_summary.csv
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/control_summary.csv
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/pairwise_or_matrix_diagnostics.csv
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/parameter_sweep_summary.csv
runs/QSB-BRIDGE-NUM-05A/geometric_validation_hostile_controls_open/resolved_config.json
```

## 7. Stop/Go Criteria

Go criteria:

```text
geometric baselines outperform hostile controls on predefined geometry-validation diagnostics
node permutation invariance passes
distribution-matched and block controls are reported separately and do not receive the same geometry score as true baselines
tau/l0/n sweeps are documented
claim boundary remains intact
```

Stop or revise criteria:

```text
hostile controls score as well as geometric baselines
diagnostics depend strongly on arbitrary tau or l0 choices
near-degenerate magnitudes create unstable readouts
n scaling changes conclusions qualitatively
known geometry cannot be separated from distribution-matched non-geometry
```

## 8. Failure Interpretation

Failure is informative. It means the method boundary has been reached for the tested control family or parameter region.

Allowed failure interpretations:

```text
The diagnostic is too weak for this control family.
The parameter region is unstable.
The construction is too circular to support broader use.
The method requires stronger controls before real-data preflight.
The diagnostic should be demoted or removed.
```

Disallowed interpretations:

```text
The physical idea is proven.
The physical idea is disproven.
The method is physically validated.
The hostile control can be ignored because it is inconvenient.
```
