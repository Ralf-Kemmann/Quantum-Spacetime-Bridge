# BMC-15b Geometry-Proxy Null Comparison Specification

## Purpose

BMC-15b extends BMC-15a by comparing observed geometry-proxy diagnostics against null-generated graph structures.

BMC-15a established the observed baseline:

```text
N81_full_baseline and larger backbone envelopes show:
  zero direct triangle inequality defects under the tested distance proxy,
  low to moderately low embedding stress,
  stable sparse-scaffold shell-growth proxies for larger envelopes.
```

However, BMC-15a did not test whether these geometry-proxy values are distinctive.

BMC-15b asks:

```text
Are the observed geometry-proxy values special relative to null-generated structures,
or do null graphs show similar geometry-like proxy behavior?
```

Internal image:

```text
Hat unser Klunker wirklich Kristallordnung,
oder sehen auch geschüttelte Klumpen kristallartig aus?
```

---

## 1. Relationship to BMC-15a

BMC-15a:

```text
observed geometry-proxy baseline
```

BMC-15b:

```text
geometry-proxy null comparison
```

BMC-15b must reuse the same distance convention and proxy definitions as BMC-15a:

```text
d(i,j) = -log(w(i,j))
```

with the same safeguards:

```text
positive weights only
epsilon clipping where needed
```

BMC-15b must not introduce new geometry definitions unless explicitly documented.

---

## 2. Scope

### In scope

BMC-15b compares observed and null distributions for:

```text
triangle inequality defect metrics
embedding stress metrics
negative eigenvalue burden
shell-growth dimension proxy
geodesic consistency metrics
graph inventory metrics
```

### Not in scope

BMC-15b does not establish:

```text
physical spacetime emergence
causal structure
continuum geometry
metric tensor reconstruction
physical dimension
```

It remains a methodological geometry-proxy null comparison.

---

## 3. Observed reference values

BMC-15b should use BMC-15a outputs as observed reference values:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_graph_inventory.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_triangle_defect_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_embedding_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_geodesic_consistency_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_shell_growth_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_local_dimension_proxy_summary.csv
```

Primary observed graph comparisons should focus on:

```text
N81_full_baseline
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
threshold_path_consensus_envelope
```

The compact core alone should be treated cautiously because:

```text
top_strength_reference_core:
  6 edges
  9 nodes
  3 components
  largest component = 3
```

It is too small and fragmented for strong standalone geometry interpretation.

---

## 4. Null sources

BMC-15b may use null-generated graph summaries from BMC-14-series runners if available.

However, most BMC-14-series output tables summarize core recovery and method containment, not full null edge tables.

Therefore BMC-15b has two implementation options:

### Option A: regenerate null graphs

Recommended first implementation.

Use the same null-generation logic as BMC-14e/BMC-14d to generate fresh null graphs and compute geometry proxies directly.

Recommended null models:

```text
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
gaussian_copula_feature_null
global_covariance_gaussian
family_covariance_gaussian
weight_rank_edge_rewire
```

### Option B: read saved null edge tables

Only possible if raw null edge tables were written.

This is not assumed.

Recommendation:

```text
BMC-15b should regenerate null graphs with the same seed discipline and null definitions.
```

---

## 5. Recommended initial null models

To keep BMC-15b auditable, the first implementation should include the strongest and most relevant null controls:

```text
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
gaussian_copula_feature_null
global_covariance_gaussian
family_covariance_gaussian
weight_rank_edge_rewire
```

Optional simple nulls from BMC-14:

```text
featurewise_permutation
rowwise_vector_permutation
family_preserving_row_permutation
```

Recommendation for BMC-15b first run:

```text
include BMC-14d and BMC-14e null families first
```

because these are the strongest nulls.

---

## 6. Replicate count

Recommended initial run:

```text
replicates = 200 per null model
```

Reason:

```text
Geometry-proxy diagnostics are heavier than core-overlap diagnostics.
```

If runtime is acceptable:

```text
replicates = 500 per null model
```

Final-facing run may use:

```text
500 or 1000 per null model
```

if computationally feasible.

For quick debugging:

```text
replicates = 20 or 50
```

---

## 7. Null graph objects to compute

For each null replicate, compute geometry-proxy diagnostics for graph objects analogous to BMC-15a.

Recommended:

```text
null_N81_full
null_top_strength_core
null_maximum_spanning_tree
null_mutual_kNN_k3
```

Optional:

```text
null_threshold_path_consensus
```

Practical warning:

```text
threshold_path_consensus may be expensive or ambiguous unless the original BMC-13 consensus logic is reproduced exactly.
```

Recommended first implementation:

```text
null_N81_full
null_top_strength_core
null_maximum_spanning_tree
null_mutual_kNN_k3
```

Observed comparison mapping:

```text
N81_full_baseline            -> null_N81_full
top_strength_reference_core  -> null_top_strength_core
maximum_spanning_tree        -> null_maximum_spanning_tree
mutual_kNN_k3                -> null_mutual_kNN_k3
```

The threshold consensus observed envelope can remain observed-only or be compared later.

---

## 8. Geometry-proxy metrics to compare

### 8.1 Triangle defects

For each null graph:

```text
triangle_mode = edge_only
triangle_mode = shortest_path_completed
```

Metrics:

```text
triangle_count
violation_fraction
max_violation
mean_violation
```

Important:

```text
shortest_path_completed triangle defects are expected to be near zero by construction
```

Therefore primary comparison should focus on:

```text
edge_only triangle defects
```

### 8.2 Embedding stress

For each null graph and dimension:

```text
2D
3D
4D
```

Metrics:

```text
stress_normalized
negative_to_positive_abs_ratio
negative_eigenvalue_fraction
```

Primary comparison:

```text
stress_normalized
negative_to_positive_abs_ratio
```

### 8.3 Shell growth / dimension proxy

For each null graph:

```text
core seed = null top-strength core nodes
```

Compute shell growth from the null core.

Metrics:

```text
effective_dimension_proxy
fit_r2
fit_points
interpretation_label
```

Observed comparison:

```text
observed core seed -> observed envelope
null core seed -> null envelope
```

### 8.4 Geodesic consistency

Compare null envelopes against null_N81_full direct distances.

Metrics:

```text
unreachable_pair_fraction
mean_path_direct_ratio
median_path_direct_ratio
max_path_direct_ratio
mean_path_minus_direct
```

Observed comparison:

```text
observed envelope vs observed N81 full
null envelope vs null N81 full
```

---

## 9. Distribution summary

For each null model, graph type, and metric, report:

```text
null_model_id
graph_id
metric
replicate_count
observed_value
null_mean
null_std
null_min
null_q05
null_median
null_q95
null_max
p_like_lower_tail
p_like_upper_tail
observed_quantile_position
```

Because geometry-proxy metrics can be better when low or high depending on metric:

```text
embedding stress:
  lower is more geometry-like

negative eigenvalue burden:
  lower is more Euclidean-like

triangle violation_fraction:
  lower is more metric-like

fit_r2:
  higher indicates more stable shell-growth fit

effective_dimension_proxy:
  descriptive, not strictly better lower/higher

unreachable_pair_fraction:
  lower is better

mean_path_direct_ratio:
  closer to 1 is better
```

Therefore BMC-15b should report both lower-tail and upper-tail p-like diagnostics.

---

## 10. Interpretation labels

BMC-15b should classify each observed metric relative to the null distribution.

Suggested labels:

```text
observed_more_geometry_like_than_null
observed_null_typical
observed_less_geometry_like_than_null
not_directional
insufficient_null_support
```

Metric direction map:

```text
triangle violation_fraction:
  lower is more geometry-like

embedding stress_normalized:
  lower is more geometry-like

negative_to_positive_abs_ratio:
  lower is more Euclidean-like

fit_r2:
  higher is more stable-proxy-like

unreachable_pair_fraction:
  lower is more connected/consistent

mean_path_direct_ratio:
  closer_to_one is more geodesically consistent
```

For `effective_dimension_proxy`, do not label as more/less geometry-like unless paired with fit quality.

---

## 11. Expected outputs

BMC-15b should write:

```text
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_graph_inventory.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_triangle_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_embedding_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_geodesic_consistency_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_shell_growth_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_local_dimension_proxy_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_observed_vs_null_distribution_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_readout.md
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_metrics.json
```

Optional:

```text
runs/BMC-15b/geometry_proxy_null_comparison_open/null_edge_tables/
```

Raw null edge tables should be optional and controlled by config because they may become large.

---

## 12. Field list: bmc15b_observed_vs_null_distribution_summary.csv

| field | type | description |
|---|---|---|
| null_model_id | string | Null model used |
| graph_id | string | Observed graph ID or comparison graph ID |
| null_graph_id | string | Matching null graph ID |
| metric_group | string | triangle, embedding, geodesic, shell, dimension |
| metric | string | Metric name |
| metric_direction | string | lower_better, higher_better, closer_to_one, not_directional |
| replicate_count | integer | Number of null replicates |
| observed_value | float | Observed BMC-15a value |
| null_mean | float | Null mean |
| null_std | float | Null standard deviation |
| null_min | float | Null minimum |
| null_q05 | float | Null 5 percent quantile |
| null_median | float | Null median |
| null_q95 | float | Null 95 percent quantile |
| null_max | float | Null maximum |
| p_like_lower_tail | float | Empirical lower-tail diagnostic |
| p_like_upper_tail | float | Empirical upper-tail diagnostic |
| observed_quantile_position | float | Fraction of null values <= observed |
| interpretation_label | string | Relative interpretation label |

---

## 13. Field list: bmc15b_null_embedding_summary.csv

Same as BMC-15a with null metadata added.

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model ID |
| null_family | string | Null family |
| graph_id | string | Null graph object ID |
| embedding_dimension | integer | Embedding dimension |
| node_count | integer | Number of embedded nodes |
| stress_normalized | float | Normalized embedding stress |
| negative_to_positive_abs_ratio | float | Negative eigenvalue burden |
| generation_status | string | ok or warning |

---

## 14. Field list: bmc15b_null_triangle_summary.csv

Same as BMC-15a with null metadata added.

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model ID |
| null_family | string | Null family |
| graph_id | string | Null graph object ID |
| triangle_mode | string | edge_only or shortest_path_completed |
| triangle_count | integer | Number of tested triangles |
| violation_fraction | float | Triangle violation fraction |
| max_violation | float | Maximum violation magnitude |
| generation_status | string | ok or warning |

---

## 15. Field list: bmc15b_null_local_dimension_proxy_summary.csv

Same as BMC-15a with null metadata added.

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model ID |
| null_family | string | Null family |
| graph_id | string | Null graph object ID |
| fit_points | integer | Number of fitted shell points |
| effective_dimension_proxy | float | Shell-growth slope |
| fit_r2 | float | Fit quality |
| interpretation_label | string | stable_proxy, weak_proxy, insufficient_points |
| generation_status | string | ok or warning |

---

## 16. Interpretation logic

### Case 1: observed geometry proxies are null-typical

If observed embedding stress, triangle defects, and shell-growth metrics fall inside typical null ranges:

```text
observed geometry-like behavior may be pipeline-generic
```

Interpretation:

```text
BMC-15a geometry-proxy consistency is not distinctive relative to nulls.
```

This does not invalidate the robust core identity, but it limits the geometry reading.

### Case 2: observed geometry proxies are stronger than nulls

If observed graphs show lower stress, fewer defects, better geodesic consistency, or more stable shell growth than nulls:

```text
observed core/envelope geometry-proxy behavior appears distinctive
```

Interpretation:

```text
This supports further relational geometry-proxy investigation.
```

Still not a physical spacetime claim.

### Case 3: mixed result

Likely outcome:

```text
some metrics are distinctive
some are null-typical
some are method-dependent
```

Interpretation:

```text
geometry-like proxy structure is partial and method-dependent
```

This is still useful.

---

## 17. Conservative external wording template

> BMC-15b compares the observed geometry-proxy diagnostics against null-generated graph structures. The aim is to determine whether the low triangle-defect rates, embedding compatibility, and shell-growth proxies observed in BMC-15a are distinctive or typical of the extraction pipeline and null models. The comparison remains methodological: even favorable results would support only geometry-like proxy specificity, not physical spacetime emergence or continuum reconstruction.

---

## 18. Recommended implementation sequence

Suggested files:

```text
docs/BMC15B_GEOMETRY_PROXY_NULL_COMPARISON_SPEC.md
data/bmc15b_geometry_proxy_null_comparison_config.yaml
scripts/run_bmc15b_geometry_proxy_null_comparison.py
```

Suggested output root:

```text
runs/BMC-15b/geometry_proxy_null_comparison_open/
```

Recommended first config:

```text
replicates = 200

null_models:
  global_covariance_gaussian
  family_covariance_gaussian
  weight_rank_edge_rewire
  degree_preserving_edge_rewire
  degree_weightclass_edge_rewire
  gaussian_copula_feature_null

null_graphs:
  null_N81_full
  null_top_strength_core
  null_maximum_spanning_tree
  null_mutual_kNN_k3
```

---

## 19. Recommended next sequence

```text
BMC-15b:
  geometry-proxy null comparison

BMC-15c:
  visualization / layout diagnostic figures

BMC-15d:
  geometry-proxy summary note and Red-Team review
```

BMC-15c should not precede BMC-15b, because visual layouts can be persuasive but methodologically weaker.

---

## 20. Final internal summary

```text
BMC-15a:
Unser Klunker und seine Hüllen zeigen erste Kristallordnungs-Proxys.

BMC-15b:
Jetzt prüfen wir,
ob geschüttelte Klumpen dieselbe Kristallordnung vortäuschen.
```

Loriot-compatible version:

```text
Der Klunker glitzert geordnet.
Nun müssen wir prüfen,
ob die Küchenmaschine auch zufällige Klumpen hübsch zum Glitzern bringt.
```
