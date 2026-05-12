# QSB-BRIDGE-NUM-04A Result Note

## 1. Purpose

QSB-BRIDGE-NUM-04A records a small deterministic toy diagnostic for the magnitude/phase separation described in QSB-BRIDGE-SYNTH-02E.

The run keeps `|K_ij|` fixed and varies only `phi_ij`.

## 2. Files

```text
data/qsb_bridge_num_04a_phase_sensitive_toy_config.yaml
scripts/run_qsb_bridge_num_04a_phase_sensitive_toy.py
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/summary.json
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/readout.md
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_variant_summary.csv
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_pairwise_diagnostics.csv
runs/QSB-BRIDGE-NUM-04A/phase_sensitive_toy_open/phase_toy_config_resolved.json
```

## 3. Result

```text
magnitude_invariance_passed: True
all_hermitian_checks_passed: True
phase_sensitive_diagnostics_changed: True
max_distance_diff_across_phase_variants: 0.0
max_graph_jaccard_loss: 0.0
```

The magnitude-only distance-like diagnostics remain invariant across the tested phase variants because the magnitude matrix is unchanged. The phase-sensitive toy diagnostics vary across phase patterns.

## 4. Variant Summary

|variant_id|mean_distance|distance_matrix_max_abs_diff_vs_phase_zero|magnitude_graph_edge_jaccard_vs_phase_zero|mean_node_interference|mean_abs_closure|mean_cos_phase|mean_abs_sin_phase|
|---|---|---|---|---|---|---|---|
|phase_zero|3.272727272727|0.0|1.0|2.879708154154|0.0|1.0|0.0|
|phase_linear_gradient|3.272727272727|0.0|1.0|1.103476752661|0.0|-0.063110018477|0.671297423888|
|phase_random_low|3.272727272727|0.0|1.0|2.827919705346|0.316292951989|0.977956114545|0.181826787427|
|phase_random_high|3.272727272727|0.0|1.0|0.999396001369|1.518731401775|0.28302493528|0.775858080908|
|phase_vortex_like|3.272727272727|0.0|1.0|0.254297970924|1.038188679196|-0.513915018687|0.519019437453|

## 5. Claim Boundary

04A is a toy diagnostic. It does not make a physical proof claim. `K_ij` and `D_ij` are toy objects here. `D_ij` is distance-like only. Phase-sensitive readouts are toy interference-like readouts, not real quantum dynamics. Magnitude invariance does not support a physical emergence claim. Phase response does not support a de-Broglie confirmation claim. Geometry Proxy remains Proxy. The integrated bridge map remains methodological.
