# QSB-BRIDGE-NUM-04A Run Readout

## Run

```text
block_id: QSB-BRIDGE-NUM-04A
run_id: phase_sensitive_toy_open
n_nodes: 12
l0: 2.0
tau: 0.35
```

## Purpose

This run is a deterministic toy diagnostic for the methodological separation between a magnitude-only distance-like readout and phase-sensitive toy diagnostics.

It uses one fixed magnitude matrix `A_ij` across all variants and changes only `phi_ij`.

## Main Readout

```text
magnitude_invariance_passed: True
all_hermitian_checks_passed: True
phase_sensitive_diagnostics_changed: True
max_distance_diff_across_phase_variants: 0.0
max_graph_jaccard_loss: 0.0
```

## Variant Summary

|variant_id|mean_distance|distance_matrix_max_abs_diff_vs_phase_zero|magnitude_graph_edge_jaccard_vs_phase_zero|mean_node_interference|mean_abs_closure|mean_cos_phase|mean_abs_sin_phase|
|---|---|---|---|---|---|---|---|
|phase_zero|3.272727272727|0.0|1.0|2.879708154154|0.0|1.0|0.0|
|phase_linear_gradient|3.272727272727|0.0|1.0|1.103476752661|0.0|-0.063110018477|0.671297423888|
|phase_random_low|3.272727272727|0.0|1.0|2.827919705346|0.316292951989|0.977956114545|0.181826787427|
|phase_random_high|3.272727272727|0.0|1.0|0.999396001369|1.518731401775|0.28302493528|0.775858080908|
|phase_vortex_like|3.272727272727|0.0|1.0|0.254297970924|1.038188679196|-0.513915018687|0.519019437453|

## Main Findings

- All variants share the same magnitude matrix A_ij, so the distance-like diagnostics are invariant within the configured tolerance.
- The threshold graph at tau=0.35 is unchanged across phase variants.
- The phase-sensitive toy diagnostics change across the tested phase patterns.
- The readout is methodological and toy-level only.

## Claim Boundary

This is a toy diagnostic. `K_ij` and `D_ij` are toy objects in this run. `D_ij` is a distance-like construction, not a spacetime metric. The phase-sensitive diagnostics are interference-like toy diagnostics, not real quantum dynamics. The magnitude invariance readout and phase response readout do not establish physical emergence, metric recovery, causal structure, or de-Broglie confirmation.
