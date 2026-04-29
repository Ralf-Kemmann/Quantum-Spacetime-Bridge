# BMC-14 Null-Model / Randomized Feature-Control Specification

## Purpose

BMC-14 addresses the next major methodological objection after BMC-13/13a.

BMC-13/13a showed that the compact six-edge N=81 top-strength reference core is fully contained in all tested alternative backbone constructions.

This supports a core-vs-envelope interpretation:

```text
The hard N=81 reference core persists,
while the broader envelope remains method-dependent.
```

However, the next skeptical question is:

```text
Would a comparable six-edge core also appear in randomized or non-specific relational structures?
```

BMC-14 therefore introduces null-model controls.

---

## 1. Working question

Formal question:

```text
Is the observed N=81 reference core more specific than comparable cores generated from randomized feature-space controls?
```

Internal image:

```text
Ist unser Keim ein echter Kristallisationskeim,
oder bildet jede geschüttelte Beziehungssuppe ähnliche Klümpchen?
```

---

## 2. Current reference object

The reference object is the BMC-13/13a compact core:

```text
method_id = top_strength_reference
edge_count = 6
reference_edge_count = 6
```

From BMC-13a:

```text
reference_containment = 1.000
```

in all tested alternative methods.

This six-edge core is treated as the observed reference core.

Important:

```text
The reference core is a graph-method diagnostic object,
not a physical spacetime object.
```

---

## 3. Input data

Primary feature input:

```text
data/bmc12_feature_table_with_derived_from_bmc08c.csv
```

Relevant feature columns:

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

Metadata columns to preserve:

```text
node_id
node_family
node_label
origin_tag
comment
```

Reference graph / core inputs:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13_backbone_edges.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13a_method_summary_with_containment.csv
```

---

## 4. What remains fixed?

### Fixed

```text
node_id set
node count
feature column names
feature marginal distributions
standardization procedure
edge-count target N=81
top_strength_reference k=6
alternative backbone methods
random seed list
```

### Not fixed in nulls

Depending on null model:

```text
feature-to-node assignment
feature correlations
cross-feature row structure
edge weights
edge rankings
reference-core overlap
```

---

## 5. Proposed null models

### Null model A: independent feature-wise permutation

Each feature column is independently permuted across nodes.

Preserves:

```text
individual feature distributions
node count
feature names
```

Breaks:

```text
within-row feature combinations
feature correlations
original feature-to-node structure
```

Interpretation:

```text
Tests whether the observed core depends on the specific joint feature assignment.
```

### Null model B: row-wise feature-vector permutation

Entire feature vectors are permuted across node IDs.

Preserves:

```text
within-row feature correlations
joint feature vectors
feature marginal distributions
```

Breaks:

```text
feature vector to original node identity
family-specific assignment
```

Interpretation:

```text
Tests whether the observed core depends on which node carries which complete feature vector.
```

### Null model C: family-preserving row permutation

Feature vectors are permuted only within each node_family.

Preserves:

```text
node_family distribution
family-level feature structure
within-row feature correlations
```

Breaks:

```text
specific node-to-feature assignment inside each family
```

Interpretation:

```text
A stricter null model that keeps family structure but randomizes identities within families.
```

### Optional future null model D: noise perturbation

Small noise is added to standardized feature values.

This should likely be BMC-14b, not the first BMC-14a block.

---

## 6. Graph reconstruction under nulls

For each null replicate:

1. Build a permuted feature table.
2. Standardize the same selected feature columns.
3. Compute pairwise distances:

```text
d(i,j) = || z_i - z_j ||_2
```

4. Compute weights:

```text
w(i,j) = 1 / (1 + d(i,j))
```

5. Select the top N edges:

```text
N = 81
```

6. Extract the null top-strength reference core:

```text
k = 6
```

7. Extract alternative null backbones using the same methods as BMC-13.

---

## 7. Metrics

### 7.1 Overlap with observed reference core

Let:

```text
E_obs_core = observed six-edge reference core
E_null_core = six-edge top-strength core in a null replicate
```

Compute:

```text
shared_edges = |E_obs_core ∩ E_null_core|
jaccard      = |E_obs_core ∩ E_null_core| / |E_obs_core ∪ E_null_core|
```

Because both sets have six edges:

```text
jaccard = shared_edges / (12 - shared_edges)
```

### 7.2 Observed-core containment in null envelope

For each null method envelope:

```text
reference_containment_in_null =
  |E_obs_core ∩ E_null_method| / |E_obs_core|
```

This asks:

```text
How much of the observed core reappears inside null-generated structures?
```

### 7.3 Null-core internal containment

For each null replicate, compute whether the null top-strength core is contained inside its own null alternative methods:

```text
null_reference_containment =
  |E_null_core ∩ E_null_method| / |E_null_core|
```

This asks:

```text
Is full core containment a generic property of this pipeline?
```

This distinction is critical:

```text
Does the observed core reappear under nulls?
Does any null core also show full containment under null methods?
```

---

## 8. Suggested replicate count

Initial BMC-14a:

```text
replicates = 100
```

If results are borderline:

```text
replicates = 500 or 1000
```

Use wording:

```text
empirical rank / null comparison
```

not:

```text
formal statistical proof
```

unless replicate counts and assumptions are expanded.

---

## 9. Empirical rank / p-like diagnostics

For a metric `M`, compare observed value `M_obs` to null values:

```text
M_null[1], ..., M_null[R]
```

A simple empirical upper-tail p-like value:

```text
p_like = (1 + count(M_null >= M_obs)) / (R + 1)
```

This is not a formal proof, but gives a useful diagnostic.

---

## 10. Expected output files

BMC-14 should write:

```text
runs/BMC-14/null_model_feature_control_open/bmc14_null_replicate_summary.csv
runs/BMC-14/null_model_feature_control_open/bmc14_null_method_containment_summary.csv
runs/BMC-14/null_model_feature_control_open/bmc14_null_distribution_summary.csv
runs/BMC-14/null_model_feature_control_open/bmc14_readout.md
runs/BMC-14/null_model_feature_control_open/bmc14_metrics.json
```

Optional:

```text
runs/BMC-14/null_model_feature_control_open/null_feature_tables/
runs/BMC-14/null_model_feature_control_open/null_edge_tables/
```

For storage economy, raw replicate tables may be optional or controlled by config.

---

## 11. Field list: bmc14_null_replicate_summary.csv

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model name |
| random_seed | integer | Seed used for replicate |
| edge_count_target | integer | Target edge count, default 81 |
| core_edge_count | integer | Null core size, default 6 |
| observed_core_shared_edges | integer | Shared edges between observed core and null core |
| observed_core_jaccard | float | Jaccard between observed core and null core |
| observed_core_recovery_fraction | float | shared_edges / observed_core_size |
| null_core_mean_weight | float | Mean weight of null core edges |
| null_core_min_weight | float | Minimum weight of null core edges |
| null_core_max_weight | float | Maximum weight of null core edges |

---

## 12. Field list: bmc14_null_method_containment_summary.csv

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model name |
| method_id | string | Null backbone method |
| method_edge_count | integer | Edge count of method output |
| observed_core_overlap | integer | Observed core edges present in this null method |
| observed_core_containment_in_null | float | observed_core_overlap / observed_core_size |
| null_core_overlap | integer | Null top-strength core edges present in this null method |
| null_core_self_containment | float | null_core_overlap / null_core_size |
| method_mean_weight | float | Mean edge weight in null method |
| method_min_weight | float | Minimum edge weight in null method |
| method_max_weight | float | Maximum edge weight in null method |

---

## 13. Field list: bmc14_null_distribution_summary.csv

| field | type | description |
|---|---|---|
| null_model_id | string | Null model name |
| metric | string | Metric name |
| replicate_count | integer | Number of replicates |
| observed_value | float | Observed BMC-13a value where applicable |
| null_mean | float | Mean of null values |
| null_std | float | Standard deviation of null values |
| null_min | float | Minimum null value |
| null_q05 | float | 5 percent quantile |
| null_median | float | Median null value |
| null_q95 | float | 95 percent quantile |
| null_max | float | Maximum null value |
| p_like_upper_tail | float | Empirical upper-tail p-like diagnostic |

---

## 14. Interpretation logic

### Strong specificity support

If null models rarely recover observed core edges:

```text
observed_core_recovery_fraction near 0 in most nulls
```

and if observed BMC-13a containment is stronger than null internal containment patterns, then BMC-14 supports specificity of the observed core.

### Weak specificity support

If null models commonly recover the same observed core or comparable containment patterns, then the observed BMC-13a result may be a generic consequence of the pipeline or feature distributions.

### Mixed result

If the observed core does not reappear under nulls, but null cores commonly self-contain in their own method envelopes, then:

```text
core containment may be pipeline-generic,
but the specific observed core may still be data-specific.
```

---

## 15. Conservative interpretation template

### Befund

BMC-14 compares the observed N=81 six-edge reference core against feature-randomized null controls.

### Interpretation

Low recovery of the observed core under nulls supports data-specificity of the reference core. High null self-containment would indicate that core-in-envelope behavior may be a generic property of the extraction pipeline.

### Hypothesis

The observed core may represent a specific relational structure if it is rarely reproduced under null feature assignments.

### Open gap

BMC-14 remains a graph-method and null-model diagnostic. It does not establish physical spacetime emergence, causal geometry, or continuum reconstruction.

---

## 16. Allowed statements after BMC-14, depending on outcome

### If null recovery is low

Allowed:

```text
The observed N=81 reference core is rarely recovered under the tested feature-randomized null controls.
```

```text
This supports data-specificity of the compact relational core within the tested null-model family.
```

Avoid:

```text
The core is physically real spacetime structure.
```

### If null recovery is high

Allowed:

```text
Comparable cores can arise under the tested null controls.
```

```text
The current core-containment result may reflect generic pipeline behavior rather than data-specific relational structure.
```

Avoid:

```text
The project failed.
```

because this would simply narrow the interpretation and guide the next control.

---

## 17. Recommended first implementation: BMC-14a

BMC-14a should implement:

```text
null_model_A_featurewise_permutation
null_model_B_rowwise_vector_permutation
null_model_C_family_preserving_row_permutation
```

with:

```text
replicates = 100
edge_count_target = 81
core_edge_count = 6
random_seed_base = 14000
```

BMC-14a should produce summary distributions, not only individual replicate rows.

---

## 18. Repo placement

Specification:

```text
docs/BMC14_NULL_MODEL_FEATURE_CONTROL_SPEC.md
```

Suggested config:

```text
data/bmc14_null_model_feature_control_config.yaml
```

Suggested runner:

```text
scripts/run_bmc14_null_model_feature_control.py
```

Suggested outputs:

```text
runs/BMC-14/null_model_feature_control_open/
```

---

## 19. Final note

BMC-14 is a high-value control because it tests whether the BMC-13a core-vs-envelope result is data-specific or pipeline-generic.

Internal one-line version:

```text
Jetzt schütteln wir die Beziehungssuppe und schauen,
ob derselbe Keim wieder von allein auftaucht.
```
