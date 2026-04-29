# BMC-12 Feature Leave-One-Out Specification

## Purpose

BMC-12 tests whether the current local graph anchor

```text
BMC09d_threshold_tau_03
```

is broadly supported by the feature set or dominated by one individual feature.

This is a methodological dominance analysis, not a physical proof.

The test repeats the BMC-09d-style threshold graph construction after removing one feature at a time from the standardized feature space.

---

## Current project anchor

The current working anchor is:

```text
threshold_tau_03
tau = 0.30
graph construction = threshold / local weighted graph
status in BMC-09d = backbone_result_recovered
```

Null-model context:

- BMC-10 Gaussian null model did not reproduce the anchor.
- BMC-11 covariance-preserving null model did not reproduce the anchor.
- BMC-12 therefore asks a different question:
  Is the anchor collectively supported, or mostly carried by one feature?

---

## Input files

Expected project-root relative paths:

```text
data/bmc08a_real_units_feature_table.csv
```

or another CSV with at least the required feature columns.

The default feature columns are:

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

A node identifier column is also required. The default expected column is:

```text
node_id
```

If the local table uses another identifier name, update the YAML configuration.

---

## Mathematical construction

For each analysis case:

1. Select a feature subset.
2. Z-standardize each selected feature over all nodes.
3. Compute Euclidean pair distances:

```text
d(i,j) = || z_i - z_j ||_2
```

4. Convert distances into weights:

```text
w(i,j) = 1 / (1 + d(i,j))
```

5. Build an undirected threshold graph using:

```text
w(i,j) >= tau
```

with default:

```text
tau = 0.30
```

---

## Leave-one-out cases

The runner performs:

| case_id | feature set |
|---|---|
| baseline_all_features | all configured features |
| drop_feature_mode_frequency | all except feature_mode_frequency |
| drop_feature_length_scale | all except feature_length_scale |
| drop_feature_shape_factor | all except feature_shape_factor |
| drop_feature_spectral_index | all except feature_spectral_index |

---

## Output files

The runner writes to:

```text
runs/BMC-12/feature_leaveoneout_open/
```

Expected outputs:

```text
bmc12_feature_leaveoneout_summary.csv
bmc12_feature_leaveoneout_edges.csv
bmc12_feature_leaveoneout_metrics.json
bmc12_feature_leaveoneout_readout.md
```

---

## Metrics

For each case the runner reports:

| field | type | description |
|---|---|---|
| case_id | string | Baseline or leave-one-out case identifier |
| dropped_feature | string or null | Feature removed in this case |
| feature_count | integer | Number of active features |
| node_count | integer | Number of nodes |
| edge_count | integer | Number of threshold edges |
| density | float | Undirected graph density |
| component_count | integer | Number of connected components |
| largest_component_size | integer | Number of nodes in largest connected component |
| mean_degree | float | Mean node degree |
| median_degree | float | Median node degree |
| min_degree | integer | Minimum node degree |
| max_degree | integer | Maximum node degree |
| mean_weight_edges | float or null | Mean retained edge weight |
| median_weight_edges | float or null | Median retained edge weight |
| min_weight_edges | float or null | Minimum retained edge weight |
| max_weight_edges | float or null | Maximum retained edge weight |
| delta_edge_count_vs_baseline | integer or null | Change in edge count relative to baseline |
| delta_density_vs_baseline | float or null | Change in density relative to baseline |
| delta_component_count_vs_baseline | integer or null | Change in component count relative to baseline |
| edge_retention_vs_baseline | float or null | Fraction of baseline edges retained |
| new_edge_fraction_vs_baseline | float or null | Fraction of case edges not present in baseline |
| provisional_dominance_reading | string | Conservative dominance classification |

---

## Dominance reading

The runner does not assign physical meaning.

It assigns only a provisional methodological reading:

```text
stable_under_drop
moderately_sensitive_to_drop
strongly_sensitive_to_drop
fragmentation_sensitive_to_drop
```

Interpretation rule:

- If dropping a feature leaves the graph close to baseline, the anchor is not dominated by that feature.
- If dropping a feature strongly changes edge count, density, component count, or baseline-edge retention, that feature is a dominance candidate.
- If all drops are disruptive, the anchor may be collectively fragile.
- If no drop is disruptive, the anchor is collectively robust at this diagnostic level.

---

## Defensive interpretation template

### Befund

BMC-12 measures how strongly the threshold_tau_03 local graph depends on each individual feature.

### Interpretation

A strong change after dropping one feature indicates feature-level dominance or fragility.

### Hypothesis

If one feature dominates, the BMC09d anchor may reflect a feature-specific structure rather than a distributed relational pattern.

### Open gap

Even if BMC-12 is stable, this does not prove physical content. It only strengthens the methodological claim that the local anchor is not trivially single-feature driven.

---

## Run command

From the project root:

```bash
python3 scripts/run_bmc12_feature_leaveoneout.py \
  --config data/bmc12_feature_leaveoneout_config.yaml
```
