# BMC-15b Readout / Label Refinement Patch Specification

## Purpose

This patch refines the BMC-15b geometry-proxy null-comparison readout.

It does **not** rerun null models and does **not** change numeric distributions. It only improves:

```text
interpretation labels
tie handling
readout visibility
family-level summary structure
```

## Problem

The first BMC-15b readout can label all-zero tie cases like this:

```text
observed violation_fraction = 0
null_q05 = 0
null_median = 0
null_q95 = 0
label = observed_less_geometry_like_than_null
```

This is a label artifact. If the observed value and the null distribution are effectively identical, the refined label must be:

```text
observed_null_equivalent
```

or conservatively:

```text
observed_null_typical
```

## Tie-handling rule

Use:

```text
tie_tolerance = 1e-12
```

If:

```text
abs(observed_value - null_min) <= tolerance
and abs(observed_value - null_max) <= tolerance
```

then:

```text
interpretation_label_refined = observed_null_equivalent
```

This is especially important for triangle-defect metrics.

## Direction-aware relabeling

For `lower_better` metrics:

```text
observed < null_q05  -> observed_more_geometry_like_than_null
observed > null_q95  -> observed_less_geometry_like_than_null
otherwise            -> observed_null_typical
```

For `higher_better` metrics:

```text
observed > null_q95  -> observed_more_geometry_like_than_null
observed < null_q05  -> observed_less_geometry_like_than_null
otherwise            -> observed_null_typical
```

For `closer_to_one` metrics, the patch should remain conservative unless the full null-vector deviations are available.

For `not_directional` metrics:

```text
not_directional
```

## Readout visibility

The refined readout must expose:

```text
metric_group
triangle_mode if available
embedding_dimension if available
metric_direction
original_interpretation_label
interpretation_label_refined
```

If `triangle_mode` was not present in the source summary, mark:

```text
not_recorded_in_source_summary
```

This is a source-summary limitation, not a new result.

## Null-family grouping

The refined readout groups null models into:

```text
feature_structured_nulls:
  global_covariance_gaussian
  family_covariance_gaussian
  gaussian_copula_feature_null

graph_rewire_nulls:
  weight_rank_edge_rewire
  degree_preserving_edge_rewire
  degree_weightclass_edge_rewire
```

## Main interpretive target

The patch should make the main BMC-15b message visible:

```text
Against graph-rewire nulls, the observed N81 baseline is more embedding-compatible.

Against feature/covariance/copula nulls, observed geometry-proxy values are often null-typical.
```

## Expected outputs

```text
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_observed_vs_null_distribution_summary_refined.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_readout_refined.md
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_refinement_patch_metrics.json
```

The original BMC-15b outputs remain unchanged.

## Conservative interpretation

Allowed:

```text
BMC-15b shows a mixed but informative geometry-proxy null comparison.
The observed N81 baseline is more embedding-compatible than graph-rewire nulls.
Feature/covariance/copula nulls often produce geometry-proxy values in the observed range.
Triangle-defect all-zero cases are null-equivalent, not less geometry-like.
```

Avoid:

```text
BMC-15b proves physical geometry.
All null geometry-proxy explanations are excluded.
The observed structure is uniquely geometric.
```

## Internal summary

```text
Der Klunker glitzert geordneter als Grad-/Kantensortier-Klumpen.
Aber feature-/family-/copula-artige Nullklumpen können ebenfalls ordentlich glitzern.
Die alten all-zero Triangle-Labels waren nur ein Beschriftungskobold.
```
