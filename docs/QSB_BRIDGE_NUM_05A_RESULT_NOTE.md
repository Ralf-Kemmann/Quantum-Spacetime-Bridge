# QSB-BRIDGE-NUM-05A Result Note

## 1. Purpose

QSB-BRIDGE-NUM-05A tests synthetic geometric baselines against hostile controls. It is a method-level diagnostic block only.

## 2. Stop/Go Outcome

```text
stop_go_outcome: go_with_documented_boundaries
geometric_baseline_mean_score: 1.0
hostile_control_mean_score: 0.524862368919
minimum_control_gap_vs_baseline: 0.223289764739
node_permutation_invariance_passed: True
```

## 3. Geometric Baselines

|family_id|coordinate_distance_correlation|nearest_neighbor_recall_vs_known_geometry|distance_stress|false_positive_geometry_score|
|---|---|---|---|---|
|baseline_1d_ring|1.0|1.0|0.0|1.0|
|baseline_2d_torus_grid|1.0|1.0|0.0|1.0|
|baseline_random_geometric|1.0|1.0|0.0|1.0|

## 4. Hostile Controls

|family_id|false_positive_geometry_score|control_gap_vs_geometric_baseline|
|---|---|---|
|control_distribution_matched_random_magnitude|0.405281677106|0.594718322894|
|control_non_geometric_block_matrix|0.303490701015|0.696509298985|
|control_near_degenerate_magnitude|0.138829231215|0.861170768785|
|control_node_permutation|1.0|0.0|
|control_gaussian_magnitude_perturbation|0.776710235261|0.223289764739|

## 5. Interpretation

Geometric baselines and hostile controls are reported separately. Hostile-control success is a possible negative finding and should tighten the method boundary.

## 6. Claim Boundary

05A does not physically validate QSB. It does not establish spacetime emergence, physical metric recovery, causal structure, physical geometry reconstruction, or de-Broglie confirmation.
