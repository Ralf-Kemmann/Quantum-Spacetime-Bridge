# QSB-BRIDGE-NUM-05A Run Readout

## Run

```text
block_id: QSB-BRIDGE-NUM-05A
run_id: geometric_validation_hostile_controls_open
geometric_baseline_count: 3
hostile_control_count: 5
stop_go_outcome: go_with_documented_boundaries
```

## Geometric Baselines

|family_id|coordinate_distance_correlation|nearest_neighbor_recall_vs_known_geometry|distance_stress|false_positive_geometry_score|
|---|---|---|---|---|
|baseline_1d_ring|1.0|1.0|0.0|1.0|
|baseline_2d_torus_grid|1.0|1.0|0.0|1.0|
|baseline_random_geometric|1.0|1.0|0.0|1.0|

## Hostile Controls

|family_id|coordinate_distance_correlation|nearest_neighbor_recall_vs_known_geometry|distance_stress|false_positive_geometry_score|control_gap_vs_geometric_baseline|
|---|---|---|---|---|---|
|control_distribution_matched_random_magnitude|0.023213482252|0.180555555556|0.468057850865|0.405281677106|0.594718322894|
|control_non_geometric_block_matrix|0.368175304547|0.25|6.25462712189|0.303490701015|0.696509298985|
|control_near_degenerate_magnitude|-0.064680048747|0.083333333333|3.153563317154|0.138829231215|0.861170768785|
|control_node_permutation|1.0|1.0|0.0|1.0|0.0|
|control_gaussian_magnitude_perturbation|0.851582864308|0.673611111111|0.206341079773|0.776710235261|0.223289764739|

## Main Findings

- Geometric baselines and hostile controls are reported separately.
- Node permutation is treated as an invariance control, not as a hostile failure.
- Hostile-control success is treated as a possible negative finding.
- All readouts remain synthetic and method-level.

## Failure Interpretation

Hostile-control success is treated as a possible negative finding. If a hostile control approaches or exceeds the geometric baseline score, the diagnostic boundary is tightened rather than explained away.

## Claim Boundary

This is a synthetic method-level diagnostic block. It does not physically validate QSB, does not show spacetime emergence, does not recover a physical metric, does not derive causal structure, and does not confirm de-Broglie physics.
