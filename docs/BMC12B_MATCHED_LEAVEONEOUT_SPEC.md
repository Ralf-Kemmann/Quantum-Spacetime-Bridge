# BMC-12b Matched Leave-One-Out Specification

## Purpose

BMC-12b extends BMC-12a.

BMC-12a used a fixed threshold:

```text
tau = 0.30
```

After dropping one feature, the feature space becomes lower-dimensional. With Euclidean distances this tends to make many node pairs closer, so the fixed-threshold graph can become denser. BMC-12a therefore showed no baseline-edge loss, but substantial densification.

BMC-12b corrects this comparison problem by using matched graph size.

For each leave-one-out feature subset, the runner selects the top weighted edges so that the number of retained edges matches the all-feature baseline edge count.

Default matching mode:

```text
edge_count
```

with baseline edge count determined from the all-feature fixed-tau baseline.

---

## Current anchor

```text
BMC09d_threshold_tau_03
```

Operational baseline for BMC-12b:

```text
all configured features
tau = 0.30
baseline edge count = computed from data
```

In the current BMC-12a run this baseline was:

```text
edges = 82
components = 1
density = 0.3550
```

BMC-12b should recompute this from the input table rather than hard-code it.

---

## Input files

Expected project-root relative paths:

```text
data/bmc12_feature_table_with_derived.csv
```

Required columns:

```text
node_id
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

The runner can also derive missing BMC-08c-style columns in memory from:

```text
feature_shape_factor = max(L_major_raw, L_minor_raw) / min(L_major_raw, L_minor_raw)
feature_spectral_index = m_ref_raw
```

but the preferred input for BMC-12b is the already materialized BMC-12 table.

---

## Mathematical construction

For each case:

1. Select active features.
2. Z-standardize active features.
3. Compute all pairwise Euclidean distances:

```text
d(i,j) = || z_i - z_j ||_2
```

4. Convert distances into weights:

```text
w(i,j) = 1 / (1 + d(i,j))
```

5. For the baseline case, retain edges satisfying:

```text
w(i,j) >= tau
```

6. For each leave-one-out case, sort all possible pair edges by descending weight and retain the top N edges, where:

```text
N = baseline edge count
```

Tie handling:

If multiple edges share the cutoff weight, the runner uses deterministic ordering by:

```text
weight descending, source ascending, target ascending
```

This avoids hidden randomness.

---

## Cases

| case_id | feature set | matching |
|---|---|---|
| baseline_all_features_fixed_tau | all features | fixed tau |
| matched_drop_feature_mode_frequency | all except feature_mode_frequency | top N baseline edges |
| matched_drop_feature_length_scale | all except feature_length_scale | top N baseline edges |
| matched_drop_feature_shape_factor | all except feature_shape_factor | top N baseline edges |
| matched_drop_feature_spectral_index | all except feature_spectral_index | top N baseline edges |

---

## Output directory

```text
runs/BMC-12b/matched_leaveoneout_open/
```

Expected outputs:

```text
bmc12b_matched_leaveoneout_summary.csv
bmc12b_matched_leaveoneout_edges.csv
bmc12b_matched_leaveoneout_metrics.json
bmc12b_matched_leaveoneout_readout.md
```

---

## Field list

| field | type | description |
|---|---|---|
| case_id | string | Case identifier |
| dropped_feature | string or empty | Removed feature in leave-one-out case |
| matching_mode | string | fixed_tau or matched_edge_count |
| active_features | string | Pipe-separated active feature list |
| feature_count | integer | Number of active features |
| node_count | integer | Number of nodes |
| edge_count | integer | Retained edge count |
| density | float | Undirected graph density |
| component_count | integer | Number of connected components |
| largest_component_size | integer | Size of largest component |
| mean_degree | float | Mean node degree |
| median_degree | float | Median node degree |
| min_degree | integer | Minimum node degree |
| max_degree | integer | Maximum node degree |
| cutoff_weight | float or empty | Minimum retained edge weight |
| baseline_edge_overlap_count | integer or empty | Number of retained edges also present in baseline |
| baseline_edge_overlap_fraction | float or empty | Fraction of baseline edges recovered |
| jaccard_vs_baseline | float or empty | Edge-set Jaccard similarity versus baseline |
| new_edge_count_vs_baseline | integer or empty | Number of retained edges not present in baseline |
| component_delta_vs_baseline | integer or empty | Component count change relative to baseline |
| provisional_structure_reading | string | Conservative structural classification |

---

## Conservative structure reading

The runner assigns only a methodological reading:

```text
baseline_reference
high_structure_retention
moderate_structure_retention
low_structure_retention
fragmentation_under_matched_size
```

Default thresholds:

```text
high overlap >= 0.75
moderate overlap >= 0.50
fragmentation if component count increases
```

These are diagnostic thresholds, not physical decision rules.

---

## Interpretation template

### Befund

BMC-12b compares leave-one-out feature subsets at matched edge count relative to the all-feature baseline.

### Interpretation

If baseline-edge overlap remains high, the local graph structure is not strongly dependent on the dropped feature. If overlap falls strongly, that feature contributes substantially to the ordering of local similarities.

### Hypothesis

Features whose removal creates low matched-overlap may encode important separation information for the BMC09d threshold_tau_03 anchor.

### Open gap

Matched edge count controls graph size, but it does not test all possible thresholds or all graph observables. A later extension may sweep matched densities or compare backbone-localization labels directly if the original BMC-09d backbone-arm logic is imported.

---

## Run command

From project root:

```bash
python3 scripts/run_bmc12b_matched_leaveoneout.py \
  --config data/bmc12b_matched_leaveoneout_config.yaml
```
