# QSB-BRIDGE-NUM-04A Phase-Sensitive Toy Diagnostic Spec

## 1. Purpose

QSB-BRIDGE-NUM-04A defines a small reproducible toy diagnostic for the magnitude/phase separation discussed in:

```text
docs/QSB_BRIDGE_SYNTH_02E_HUMAN_READABLE_MATHEMATICAL_BRIDGE_NOTE.md
data/qsb_bridge_synth_02e_math_bridge_concept_map.csv
docs/QSB_BRIDGE_SYNTH_02A_RESULT_SUMMARY.md
docs/QSB_BRIDGE_SYNTH_02C_PUBLIC_CAUTIOUS_SUMMARY.md
```

The diagnostic illustrates the methodological split:

```text
Magnitude |K_ij| -> distance-like readout
Phase phi_ij    -> phase-sensitive / interference-like diagnostic
```

It is a toy diagnostic only. It is not a physical proof and does not establish spacetime emergence, physical metric recovery, causal structure, or de-Broglie confirmation.

## 2. Toy Object

The run uses `n = 12` nodes. Nodes are indexed `0` to `11`.

The fixed base distance is the circular index distance:

```text
base_distance_ij = min(|i - j|, n - |i - j|)
```

The fixed magnitude matrix is:

```text
A_ij = exp(-base_distance_ij / l0)
l0 = 2.0
A_ii = 1.0
```

Each complex toy relation is:

```text
K_ij = A_ij * exp(i * phi_ij)
```

For every phase variant, `A_ij` remains identical. Only `phi_ij` changes.

## 3. Phase Variants

The run computes five phase variants:

```text
phase_zero
phase_linear_gradient
phase_random_low
phase_random_high
phase_vortex_like
```

Hermiticity is enforced by construction:

```text
K_ji = conjugate(K_ij)
A_ji = A_ij
phi_ji = -phi_ij
```

The random variants use fixed seeds recorded in the config and resolved run config.

## 4. Magnitude-Only Diagnostics

The distance-like readout is:

```text
D_ij = -l0 * log(max(|K_ij|, epsilon))
```

The magnitude-only diagnostics are:

```text
mean_abs_K
mean_distance
std_distance
distance_matrix_max_abs_diff_vs_phase_zero
distance_rank_order_changed_vs_phase_zero
magnitude_graph_edge_count_at_tau
magnitude_graph_edge_jaccard_vs_phase_zero
```

The threshold graph uses:

```text
tau = 0.35 on |K_ij|
```

Because all phase variants share the same `A_ij`, these diagnostics are expected to remain invariant up to floating point tolerance.

## 5. Phase-Sensitive Toy Diagnostics

The phase-sensitive diagnostics are:

```text
I_i = | sum_{j != i} A_ij * exp(i * phi_ij) |
closure_ijk = angle(K_ij * K_jk * K_ki)
mean_cos_phase = mean(cos(phi_ij))
mean_abs_sin_phase = mean(abs(sin(phi_ij)))
```

The variant summary reports aggregate values of the node-wise interference-like readout and triangle closure readout. The pairwise CSV records the per-pair phase, magnitude, distance-like value, and threshold-edge flag for each variant.

## 6. Acceptance Criteria

The intended acceptance readout is:

```text
magnitude_invariance_passed = true
all_hermitian_checks_passed = true
phase_sensitive_diagnostics_changed = true
max_distance_diff_across_phase_variants = 0.0 within tolerance
max_graph_jaccard_loss = 0.0 within tolerance
```

CSV outputs must parse with Python's standard `csv` module. The result note and run readout must avoid the protected overclaim phrases listed in the acceptance block.

## 7. Claim Boundary

QSB-BRIDGE-NUM-04A is a toy diagnostic.

It does not prove:

```text
QSB
physical emergence
spacetime emergence
physical metric recovery
causal structure
de-Broglie physics
```

Protected boundaries:

```text
K_ij and d_ij are toy objects in this run.
D_ij is a distance-like construction, not a spacetime metric.
Phase-sensitive toy diagnostics are interference-like diagnostics, not real quantum dynamics.
Magnitude invariance does not establish spacetime emergence.
Phase response does not establish de-Broglie physics.
Geometry Proxy remains Proxy.
The integrated bridge map remains methodological.
```
