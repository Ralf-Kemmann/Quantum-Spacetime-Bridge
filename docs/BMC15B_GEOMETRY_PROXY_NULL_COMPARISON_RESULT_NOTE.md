# BMC-15b Geometry-Proxy Null Comparison Result Note

## Purpose

BMC-15b extends BMC-15a by comparing observed geometry-proxy diagnostics against regenerated null graph structures.

BMC-15a established an observed geometry-proxy baseline:

```text
N81_full_baseline and larger envelopes showed:
  no direct triangle inequality defects under the tested proxy distance,
  low to moderately low embedding stress,
  stable sparse-scaffold shell-growth proxies for larger envelopes.
```

BMC-15b asks:

```text
Are these geometry-proxy values distinctive,
or do null-generated graph structures show similar proxy behavior?
```

Important:

```text
BMC-15b is a geometry-proxy null comparison.
It is not a physical spacetime reconstruction.
```

Internal image:

```text
Der Klunker glitzert geordnet.
Nun prüfen wir,
ob die Küchenmaschine auch zufällige Klumpen hübsch zum Glitzern bringt.
```

---

## 1. Inputs and run status

BMC-15b used the BMC-15a observed geometry-proxy output as reference and regenerated null graph structures using BMC-14d/BMC-14e-style null definitions.

Null models:

```text
global_covariance_gaussian
family_covariance_gaussian
weight_rank_edge_rewire
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
gaussian_copula_feature_null
```

Replicates:

```text
200 per null model
```

Null graph objects:

```text
null_N81_full
null_top_strength_core
null_maximum_spanning_tree
null_mutual_kNN_k3
```

Observed comparison graph objects:

```text
N81_full_baseline
top_strength_reference_core
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
```

The observed threshold-path consensus envelope was not part of the first null comparison, because the BMC-13 consensus logic was not reproduced in BMC-15b.

---

## 2. Patch / refinement status

The first BMC-15b readout contained a label artifact for all-zero triangle-defect cases.

Problem:

```text
observed violation_fraction = 0
null_median = 0
null_q05 = 0
null_q95 = 0
original label sometimes = observed_less_geometry_like_than_null
```

This is not a valid interpretation. If the observed value and the null distribution are equal, the result is null-equivalent.

A readout / label refinement patch was applied.

Patch outputs:

```text
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_observed_vs_null_distribution_summary_refined.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_readout_refined.md
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_refinement_patch_metrics.json
```

The patch did not rerun the null models and did not alter the numeric null distributions.

It only refined:

```text
tie handling
interpretation labels
readout visibility
null-family grouping
```

---

## 3. Null-family grouping

For interpretation, BMC-15b separates nulls into two major groups.

### 3.1 Feature-structured nulls

```text
global_covariance_gaussian
family_covariance_gaussian
gaussian_copula_feature_null
```

These preserve or regenerate feature-space structure, covariance, family covariance, or rank/correlation structure.

### 3.2 Graph-rewire nulls

```text
weight_rank_edge_rewire
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
```

These preserve graph-level or edge-weight/degree structure but remove the original feature-space relational identity.

This distinction is essential for the BMC-15b interpretation.

---

## 4. Refined label counts

The refined readout produced the following label counts by null-family group:

| null_family_group | more_geometry_like | null_typical | null_equivalent | less_geometry_like | not_directional |
|---|---:|---:|---:|---:|---:|
| feature_structured_nulls | 4 | 135 | 58 | 1 | 18 |
| graph_rewire_nulls | 78 | 63 | 60 | 0 | 15 |

### Interpretation

The observed structure is frequently more geometry-like than graph-rewire nulls.

Against feature-structured nulls, the observed structure is usually null-typical or null-equivalent.

Short version:

```text
Gegen Graph-Rewire-Nulls: oft besser.
Gegen Feature-Nulls: meist typisch/äquivalent.
```

---

## 5. Main embedding result

The strongest BMC-15b signal appears in embedding compatibility.

The observed N81 full baseline is substantially more embedding-compatible than graph-rewire nulls.

### 5.1 Weight-rank edge rewiring

For `weight_rank_edge_rewire`, N81 full baseline embedding stress:

| dimension | observed stress | null median stress | refined label |
|---:|---:|---:|---|
| 2D | 0.107 | 0.356 | observed_more_geometry_like_than_null |
| 3D | 0.063 | 0.232 | observed_more_geometry_like_than_null |
| 4D | 0.061 | 0.169 | observed_more_geometry_like_than_null |

Negative-to-positive eigenvalue burden:

| dimension | observed | null median | refined label |
|---:|---:|---:|---|
| 2D | 0.081 | 0.290 | observed_more_geometry_like_than_null |
| 3D | 0.081 | 0.290 | observed_more_geometry_like_than_null |
| 4D | 0.081 | 0.290 | observed_more_geometry_like_than_null |

### 5.2 Degree-preserving edge rewiring

For `degree_preserving_edge_rewire`, N81 full baseline embedding stress:

| dimension | observed stress | null median stress | refined label |
|---:|---:|---:|---|
| 2D | 0.107 | 0.361 | observed_more_geometry_like_than_null |
| 3D | 0.063 | 0.234 | observed_more_geometry_like_than_null |
| 4D | 0.061 | 0.167 | observed_more_geometry_like_than_null |

Negative-to-positive eigenvalue burden:

| dimension | observed | null median | refined label |
|---:|---:|---:|---|
| 2D | 0.081 | 0.267 | observed_more_geometry_like_than_null |
| 3D | 0.081 | 0.267 | observed_more_geometry_like_than_null |
| 4D | 0.081 | 0.267 | observed_more_geometry_like_than_null |

### 5.3 Degree + weightclass edge rewiring

For `degree_weightclass_edge_rewire`, N81 full baseline embedding stress:

| dimension | observed stress | null median stress | refined label |
|---:|---:|---:|---|
| 2D | 0.107 | 0.358 | observed_more_geometry_like_than_null |
| 3D | 0.063 | 0.230 | observed_more_geometry_like_than_null |
| 4D | 0.061 | 0.163 | observed_more_geometry_like_than_null |

Negative-to-positive eigenvalue burden:

| dimension | observed | null median | refined label |
|---:|---:|---:|---|
| 2D | 0.081 | 0.268 | observed_more_geometry_like_than_null |
| 3D | 0.081 | 0.268 | observed_more_geometry_like_than_null |
| 4D | 0.081 | 0.268 | observed_more_geometry_like_than_null |

### Interpretation

The observed N81 baseline is not merely geometry-like because it is a weighted graph, a degree-structured graph, or a weight-rank structured graph.

Against these graph-rewire nulls, the observed N81 baseline is consistently more embedding-compatible.

Allowed:

```text
The observed N81 full baseline is substantially more embedding-compatible than graph-rewire nulls under the tested proxy diagnostics.
```

Avoid:

```text
This proves physical geometry.
```

---

## 6. Feature-structured nulls: mixed / null-typical result

Against feature-structured nulls, the observed geometry-proxy behavior is much less distinctive.

### 6.1 Global covariance Gaussian

For `global_covariance_gaussian`, the observed N81 baseline is partly better and partly null-typical.

Example:

```text
N81_full_baseline 3D stress:
  observed = 0.063
  null median = 0.095
  label = observed_more_geometry_like_than_null
```

But many related metrics are null-typical.

### 6.2 Family covariance Gaussian

For `family_covariance_gaussian`, most observed embedding values are null-typical.

Example:

```text
N81_full_baseline 3D stress:
  observed = 0.063
  null median = 0.050
  label = observed_null_typical
```

A single row was labeled less geometry-like:

```text
maximum_spanning_tree_envelope 4D stress:
  observed = 0.056
  null q95 = 0.056
  label = observed_less_geometry_like_than_null
```

This should not be overinterpreted. It is a boundary-level result in a large diagnostic table.

### 6.3 Gaussian copula feature null

For `gaussian_copula_feature_null`, observed values are generally null-typical.

Example:

```text
N81_full_baseline 3D stress:
  observed = 0.063
  null median = 0.081
  label = observed_null_typical
```

### Interpretation

Feature-space, family, covariance, and rank-correlation structure can itself generate geometry-like proxy behavior.

Therefore, BMC-15b does not support a claim that the geometry-proxy signal is uniquely specific to the observed graph.

Allowed:

```text
Feature/family/correlation-structured nulls often produce geometry-proxy values in the observed range.
```

Avoid:

```text
The geometry-like signal is unique to the observed structure.
```

---

## 7. Triangle defects after label refinement

The refined readout corrects the all-zero triangle issue.

For many feature-structured nulls:

```text
observed = 0
null_median = 0
null_q05 = 0
null_q95 = 0
refined label = observed_null_equivalent
```

This is the correct interpretation.

For graph-rewire nulls, some edge-only triangle-defect comparisons show the observed N81 baseline as better:

```text
weight_rank_edge_rewire:
  observed = 0
  null_median approx. 0.038
  label = observed_more_geometry_like_than_null

degree_preserving_edge_rewire:
  observed = 0
  null_median approx. 0.037
  label = observed_more_geometry_like_than_null

degree_weightclass_edge_rewire:
  observed = 0
  null_median approx. 0.038
  label = observed_more_geometry_like_than_null
```

But because the refined source summary does not preserve `triangle_mode`, the readout marks:

```text
triangle_mode = not_recorded_in_source_summary
```

### Interpretation

The triangle result is usable but should be described conservatively:

```text
All-zero observed/null cases are null-equivalent.
Some graph-rewire triangle-defect comparisons suggest the observed N81 baseline has fewer direct triangle defects than rewired nulls.
```

Avoid overclaiming because:

```text
triangle_mode was not preserved in the summarized source table
shortest-path-completed triangle consistency is partly tautological
```

---

## 8. Geodesic consistency

Selected geodesic consistency rows show mostly null-typical results.

### Maximum spanning tree envelope

Unreachable-pair fraction:

```text
observed = 0
null_median = 0
label = observed_null_equivalent
```

Mean path/direct ratio is null-typical across tested null families.

### mutual_kNN_k3 envelope

Unreachable-pair fraction and mean path/direct ratio are generally null-typical.

### Interpretation

BMC-15b does not show a strong distinctive geodesic-consistency signal in the selected summary rows.

Allowed:

```text
Selected geodesic-consistency metrics are mostly null-typical or null-equivalent.
```

Avoid:

```text
Observed geodesic consistency is uniquely better than nulls.
```

---

## 9. Main BMC-15b finding

BMC-15b is mixed but informative.

### Positive / distinctive side

The observed N81 full baseline and selected envelopes are generally more embedding-compatible than graph-rewire nulls.

This is especially clear for:

```text
weight_rank_edge_rewire
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
```

and for metrics:

```text
stress_normalized
negative_to_positive_abs_ratio
```

### Limiting / null-typical side

Against feature-structured nulls:

```text
global_covariance_gaussian
family_covariance_gaussian
gaussian_copula_feature_null
```

the observed geometry-proxy values are often null-typical.

### Corrected triangle interpretation

All-zero triangle-defect cases should be read as:

```text
observed_null_equivalent
```

not:

```text
observed_less_geometry_like_than_null
```

---

## 10. Strongest current interpretation

The strongest current interpretation is:

> BMC-15b suggests that the observed geometry-proxy behavior is not merely a generic consequence of graph rewiring or degree/weight-rank structure. The observed N81 full baseline and selected envelopes are generally more embedding-compatible than graph-rewire nulls, with lower normalized embedding stress and lower negative-eigenvalue burden. However, feature/family/correlation-structured nulls often generate geometry-proxy values in the observed range. Thus the geometry-proxy signal is informative but not uniquely specific. Triangle-defect all-zero cases are null-equivalent and should not be interpreted as less geometry-like.

Short version:

```text
Observed geometry-proxy behavior beats graph-rewire nulls.
It does not clearly beat feature/family/correlation nulls.
```

Internal version:

```text
Der Klunker glitzert geordneter als Grad-/Kantensortier-Klumpen.
Aber feature-/family-/copula-artige Nullklumpen können ebenfalls ordentlich glitzern.
```

---

## 11. How BMC-15b updates the project chain

Before BMC-15b:

```text
BMC-15a:
  observed geometry-proxy baseline is favorable
```

After BMC-15b:

```text
BMC-15b:
  geometry-proxy favorability is not fully generic to graph-rewire nulls
  but is partly reproduced by feature-structured nulls
```

Updated chain:

```text
BMC-12f:
  N=81 threshold/gap robust

BMC-13a:
  core embedded in method-dependent envelopes

BMC-14 series:
  observed core identity robust against tested null families

BMC-15a:
  observed envelopes show geometry-like proxy consistency

BMC-15b:
  embedding geometry-proxy signal is stronger than graph-rewire nulls
  but often null-typical against feature/family/correlation nulls
```

---

## 12. What BMC-15b strengthens

BMC-15b strengthens:

```text
The observed geometry-proxy behavior is not merely an artifact of arbitrary graph rewiring, degree preservation, or weight-rank structure.
```

It also strengthens the more nuanced interpretation:

```text
Feature/family/correlation structure contributes strongly to geometry-like proxy behavior.
```

This fits the earlier BMC-14 chain, where family-preserving and family-covariance nulls were also the strongest partial recoverers of the observed core.

---

## 13. What BMC-15b does not prove

BMC-15b does not prove:

```text
physical spacetime emergence
```

It does not prove:

```text
a physical metric
```

It does not prove:

```text
continuum reconstruction
```

It does not prove:

```text
physical dimension
```

It does not prove:

```text
unique geometry-like structure
```

It does not prove:

```text
all feature-structured null explanations are excluded
```

---

## 14. Allowed statements after BMC-15b

Allowed:

```text
BMC-15b provides a geometry-proxy null comparison.
```

```text
The observed N81 baseline is more embedding-compatible than graph-rewire nulls.
```

```text
Feature/family/correlation-structured nulls often produce geometry-proxy values in the observed range.
```

```text
The geometry-proxy signal is informative but not uniquely specific.
```

```text
All-zero triangle-defect comparisons are null-equivalent.
```

```text
The result remains methodological and does not establish physical spacetime emergence.
```

Avoid:

```text
BMC-15b proves emergent spacetime.
```

```text
The observed structure is uniquely geometric.
```

```text
All null geometry-proxy explanations are excluded.
```

```text
Feature-structured nulls fail.
```

```text
Embedding compatibility proves physical geometry.
```

---

## 15. Conservative external wording

A suitable research-note paragraph:

> BMC-15b compares the observed geometry-proxy diagnostics against regenerated null graph structures. The observed N81 full baseline and selected envelopes are substantially more embedding-compatible than graph-rewire nulls, including weight-rank, degree-preserving, and degree/weight-class rewiring controls. This is reflected in lower normalized embedding stress and lower negative-eigenvalue burden. However, feature-structured nulls, including family-covariance and Gaussian-copula feature nulls, often produce geometry-proxy values in the observed range. Thus, the geometry-proxy signal is informative but not uniquely specific. Triangle-defect all-zero cases are interpreted as null-equivalent rather than less geometry-like. These results remain methodological and do not establish physical spacetime emergence or continuum geometry.

---

## 16. Recommended next step

Two reasonable next steps exist.

### Option A: BMC-15c visualization / layout diagnostics

Purpose:

```text
Create cautious visual layouts for observed vs null graph families
```

Focus:

```text
N81_full_baseline observed layout
representative graph-rewire null layout
representative feature-structured null layout
stress comparison
core/envelope overlay
```

This should be clearly labeled as visualization, not proof.

### Option B: BMC-15d Red-Team integration

Purpose:

```text
Ask external critics whether BMC-15b has been interpreted conservatively enough.
```

Recommended before public-facing use.

### Recommendation

Do:

```text
BMC-15d Red-Team integration
```

before making any strong visual or publication-facing geometry claims.

If creating visuals, keep them explicitly illustrative.

---

## 17. File anchors

BMC-15b specification:

```text
docs/BMC15B_GEOMETRY_PROXY_NULL_COMPARISON_SPEC.md
```

BMC-15b config:

```text
data/bmc15b_geometry_proxy_null_comparison_config.yaml
```

BMC-15b runner:

```text
scripts/run_bmc15b_geometry_proxy_null_comparison.py
```

BMC-15b refinement patch spec:

```text
docs/BMC15B_READOUT_LABEL_REFINEMENT_PATCH_SPEC.md
```

BMC-15b refinement patch runner:

```text
scripts/run_bmc15b_readout_label_refinement_patch.py
```

BMC-15b outputs:

```text
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_graph_inventory.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_triangle_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_embedding_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_geodesic_consistency_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_null_local_dimension_proxy_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_observed_vs_null_distribution_summary.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_observed_vs_null_distribution_summary_refined.csv
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_readout.md
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_readout_refined.md
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_metrics.json
runs/BMC-15b/geometry_proxy_null_comparison_open/bmc15b_refinement_patch_metrics.json
```

This result note:

```text
docs/BMC15B_GEOMETRY_PROXY_NULL_COMPARISON_RESULT_NOTE.md
```

---

## 18. Consolidated status after BMC-15b

### Befund

The observed N81 full baseline and selected envelopes are generally more embedding-compatible than graph-rewire nulls, with lower embedding stress and lower negative-eigenvalue burden. Against feature-structured nulls, observed geometry-proxy values are often null-typical. All-zero triangle-defect cases are null-equivalent after label refinement.

### Interpretation

The geometry-proxy signal is informative but not uniquely specific. It is not merely a generic consequence of graph rewiring or degree/weight-rank structure, but feature/family/correlation structure can generate similar geometry-like proxy behavior.

### Hypothesis

The robust N81 core/envelope structure may carry geometry-like organization partly rooted in feature/family/correlation structure rather than in generic graph topology alone.

### Open gap

Further Red-Team review, cautious visualization, and possibly stronger feature/family-structured geometry-proxy controls remain open.
