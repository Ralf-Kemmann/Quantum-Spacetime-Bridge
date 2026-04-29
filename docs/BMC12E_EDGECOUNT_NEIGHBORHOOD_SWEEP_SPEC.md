# BMC-12e Edge-Count Neighborhood Sweep Specification

## Purpose

BMC-12e tests whether the BMC-12c matched leave-one-out retention pattern is local to the single graph-size point

```text
N_edges = 81
```

or whether it persists in a neighborhood around the BMC09d reference graph size.

BMC-12c established the reconciled reference result at N=81:

```text
baseline_all_features_fixed_tau: 3/3 retained
drop feature_mode_frequency:     1/3 retained
drop feature_length_scale:       1/3 retained
drop feature_shape_factor:       1/3 retained
drop feature_spectral_index:     2/3 retained
```

Red-team feedback identified the single edge-count point as a major limitation. BMC-12e therefore varies the matched edge count.

---

## Edge-count neighborhood

Default sweep:

```text
N = 70, 75, 81, 87, 92
```

These values are centered around the BMC09d reference size:

```text
N_ref = 81
```

---

## Input source

BMC-12e must use the reconciled BMC08c-compatible feature table:

```text
data/bmc12_feature_table_with_derived_from_bmc08c.csv
```

This supersedes earlier BMC08a-like BMC-12 inputs.

Reference node metadata:

```text
data/bmc09d_threshold_hybrid_inputs/threshold_tau_03/node_metadata_real.csv
```

Established backbone runner:

```text
scripts/bmc07_backbone_variation_runner.py
```

---

## Feature set

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

Leave-one-out cases:

```text
baseline_all_features
drop_feature_mode_frequency
drop_feature_length_scale
drop_feature_shape_factor
drop_feature_spectral_index
```

For each edge count N, each case is converted into a top-N graph.

---

## Graph construction

For each case:

1. Select active features.
2. Z-standardize active features.
3. Compute all pairwise Euclidean distances:

```text
d(i,j) = ||z_i - z_j||_2
```

4. Convert distances into weights:

```text
w(i,j) = 1 / (1 + d(i,j))
```

5. Sort all possible undirected pairs by:

```text
weight descending, source ascending, target ascending
```

6. Retain the top N edges.

This is deterministic and avoids hidden randomness.

---

## Backbone decision logic

BMC-12e reuses the established BMC07/BMC09d backbone runner and decision thresholds:

```yaml
decision:
  arrangement_signal_min: 0.05
  dominance_gap_min: 0.03
  minimum_repeat_count: 50
  minimum_arm_edge_count: 2
```

Backbone variants:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

---

## Generated inputs

BMC-12e writes old-runner-compatible input folders:

```text
data/bmc12e_edgecount_sweep_inputs/N_<N>/<case_id>/
```

Each folder contains:

```text
baseline_relational_table_real.csv
node_metadata_real.csv
```

Generated runner configs:

```text
data/bmc12e_edgecount_sweep_configs/N_<N>/<case_id>.yaml
```

Important legacy convention:

The old `bmc07_backbone_variation_runner.py` expects input paths in its config to be relative to the project `data/` directory.

---

## Output directories

The old runner writes per-case outputs under the legacy `data/runs/...` convention.

BMC-12e final collected outputs are written to:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/
```

Expected final files:

```text
bmc12e_edgecount_sweep_decision_summary.csv
bmc12e_edgecount_sweep_variant_summary.csv
bmc12e_edgecount_sweep_readout.md
bmc12e_metrics.json
```

---

## Field list: decision summary

| field | type | description |
|---|---|---|
| edge_count_target | integer | Matched top-N edge count |
| case_id | string | Baseline or leave-one-out case |
| dropped_feature | string | Removed feature, empty for baseline |
| variant_count | integer | Number of backbone variants |
| retained_variant_count | integer | Count retaining reference decision |
| retained_fraction | float | retained_variant_count / variant_count |
| failed_variant_count | integer | Variants not retaining reference decision |
| all_variants_retained | boolean string | true if all variants retain reference |
| any_failure | boolean string | true if at least one variant fails |
| bmc12e_decision_status | string | decision_retained / decision_partially_retained / decision_not_retained |

---

## Reference decision

A variant is retained if:

```text
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

Decision status:

```text
decision_retained
```

All variants retained.

```text
decision_partially_retained
```

At least one but not all variants retained.

```text
decision_not_retained
```

No variants retained.

---

## Interpretation rule

### If the N=81 BMC-12c pattern persists across neighboring N

The feature-retention pattern is less likely to be a single graph-size artifact.

### If the pattern changes strongly across neighboring N

The BMC-12c result should be interpreted as a local decision-point result.

### If the all-feature baseline fails near N

The original BMC09d anchor may be strongly graph-size specific. This would not invalidate BMC09d but would narrow its interpretation.

---

## Conservative interpretation template

### Befund

BMC-12e tests matched leave-one-out decision retention across a neighborhood of edge counts around the BMC09d reference size.

### Interpretation

Stable patterns across N support the robustness of the BMC-12c feature-sensitivity observation. Strong changes across N indicate graph-size sensitivity.

### Hypothesis

If the variant-retention pattern repeats across N, the BMC09d feature sensitivity may reflect a stable graph-neighborhood property rather than a single top-N artifact.

### Open gap

Even if stable across N, this remains a methodological diagnostic and does not establish physical content.
