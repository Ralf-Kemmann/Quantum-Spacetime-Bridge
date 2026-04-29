# BMC-14d Covariance-Preserving / Structured Null Controls Specification

## Purpose

BMC-14d addresses the strongest remaining Red-Team objection after BMC-14.

BMC-14 showed:

```text
The observed six-edge N=81 reference core was not fully recovered
in any tested feature-randomized null replicate.
```

However, the Red Team noted that the tested nulls were all variants of feature randomization:

```text
featurewise_permutation
rowwise_vector_permutation
family_preserving_row_permutation
```

These null models test whether the observed core depends on the specific feature-to-node assignment, but they do not fully test whether the core could be explained by:

```text
the empirical feature covariance structure
generic weighted-graph structure
degree / strength effects
edge-weight ordering
```

BMC-14d therefore introduces stronger structure-preserving null controls.

---

## 1. Working question

Formal question:

```text
Can the observed N=81 six-edge reference core be reproduced by null models
that preserve stronger statistical or graph-structural properties?
```

Internal image:

```text
Entsteht unser Keim,
wenn nicht die konkrete Suppe erhalten bleibt,
aber die Zutatenmischung und Strukturregeln ähnlich bleiben?
```

Or shorter:

```text
Erzwingt die Zutaten-Kovarianz allein den Klunker?
```

---

## 2. Current reference status

The reference object remains the observed BMC-13a top-strength core:

```text
method_id = top_strength_reference
edge_count = 6
edge_count_target = 81
case_id = baseline_all_features
```

Current chain:

```text
BMC-12f:
  N=81 is stable across tested threshold/gap pairs.

BMC-13a:
  The six-edge N=81 core is fully contained in all tested alternative backbone envelopes.

BMC-14:
  The observed six-edge core is not fully recovered in tested feature-randomized nulls.

Red-Team integration:
  Core identity appears data-specific within tested feature-randomized nulls.
  Core-in-envelope motif is partly pipeline-generic.
  Stronger structure-preserving nulls remain necessary.
```

---

## 3. Why covariance-preserving nulls are needed

The observed feature table may contain correlations among:

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

These correlations could induce stable edge-weight orderings in the reconstructed graph.

A simple feature permutation disrupts some or all of these correlations. Therefore, failure to reproduce the observed core under permutations does not exclude the possibility that:

```text
the observed core is explained by the feature covariance matrix
rather than by the specific node-level relational structure.
```

BMC-14d tests this.

---

## 4. Input data

Primary feature table:

```text
data/bmc12_feature_table_with_derived_from_bmc08c.csv
```

Observed core:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13_backbone_edges.csv
```

Prior null output for comparison:

```text
runs/BMC-14/null_model_feature_control_open/bmc14_null_distribution_summary.csv
```

Feature columns:

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

ID / metadata columns:

```text
node_id
node_family
node_label
origin_tag
comment
```

---

## 5. Null model families in BMC-14d

BMC-14d should include two major families:

```text
A. covariance-preserving feature nulls
B. graph-structured edge nulls
```

The first implementation may focus on A and leave B as optional if runtime or complexity grows.

---

# Part A: Covariance-preserving feature nulls

## 6. Null A1: multivariate Gaussian covariance null

### Definition

Estimate the empirical mean vector and covariance matrix of the selected features:

```text
mu = mean(X)
Sigma = cov(X)
```

Generate synthetic feature vectors:

```text
X_null ~ N(mu, Sigma)
```

for the same number of nodes.

Then assign synthetic feature vectors to the original node IDs.

### Preserves

```text
node count
feature names
empirical mean approximately
empirical covariance approximately
continuous covariance structure
```

### Does not preserve

```text
exact observed feature values
exact node-to-feature assignment
family-specific feature distributions
rank structure
non-Gaussian marginal distributions
```

### Interpretation

If the observed six-edge core is often recovered under this null, then the core may be explainable by the covariance structure alone.

If not, the observed core is not trivially explained by linear feature covariance.

---

## 7. Null A2: covariance-preserving row bootstrap / Gaussian copula option

A more distribution-aware version may preserve rank-like or marginal structure.

Two possible variants:

### A2a: Gaussian copula null

1. Transform each feature to ranks / normal scores.
2. Estimate correlation matrix in normal-score space.
3. Generate correlated normal samples.
4. Transform back using empirical feature quantiles.

### A2b: covariance-preserving bootstrap

1. Estimate covariance.
2. Generate synthetic deviations.
3. Add to empirical mean or resampled base rows.

These are stronger but more complex.

### Recommendation

For BMC-14d first implementation:

```text
Implement A1 multivariate Gaussian covariance null first.
Reserve Gaussian copula for BMC-14e if needed.
```

---

## 8. Null A3: family-block covariance null

Estimate covariance separately within each node_family, then generate synthetic feature vectors per family.

### Preserves

```text
family membership
family-specific means
family-specific covariance approximately
node count per family
```

### Does not preserve

```text
exact node-level feature identity
exact empirical values
```

### Interpretation

This is a stricter covariance null.

It asks:

```text
Can family-level covariance structure alone reproduce the observed core?
```

This is especially important because BMC-14 showed that family-preserving permutations recover up to 3/6 observed core edges.

### Practical warning

If some families have too few rows, their covariance matrices may be singular or unstable.

Fallback options:

```text
diagonal covariance within small families
shrinkage toward global covariance
small ridge regularization
skip family covariance null until sample adequacy is checked
```

---

# Part B: Graph-structured edge nulls

## 9. Null B1: weight-rank preserving edge rewiring

Start from the observed N=81 graph.

Keep:

```text
number of edges = 81
edge weight multiset
```

Randomly assign weights to randomly selected node pairs, excluding self-loops and duplicates.

### Preserves

```text
node set
edge count
edge weight distribution
```

### Does not preserve

```text
degree sequence
local clustering
original edge identities
feature-space origin
```

### Interpretation

Tests whether the observed core can arise from the weight distribution alone.

---

## 10. Null B2: degree-preserving edge rewiring

Start from the observed N=81 graph.

Randomly rewire edges while approximately preserving node degrees.

Then either:

```text
shuffle original weights across rewired edges
```

or

```text
keep rank-assigned weights
```

### Preserves

```text
node set
edge count
approximate degree sequence
optionally weight distribution
```

### Does not preserve

```text
feature-space geometry
original edge identities
specific relational structure
```

### Interpretation

Tests whether degree structure or hub effects can explain the observed top-strength core.

### Practical warning

For sparse small graphs, exact degree-preserving rewiring may be limited.

BMC-14d should report:

```text
successful rewires
failed attempts
degree deviation
```

---

## 11. Initial recommended implementation scope

To keep BMC-14d auditable, the first implementation should include:

```text
A1 global multivariate Gaussian covariance null
A3 family-block covariance null if sample sizes allow
B1 weight-rank preserving edge rewiring
```

The degree-preserving rewiring can be added in a follow-up if implementation becomes too complex.

Recommended first block:

```text
BMC-14d1:
  global_covariance_gaussian_null
  family_covariance_gaussian_null
  weight_rank_edge_rewire_null
```

---

## 12. Reconstruction procedure for feature nulls

For each covariance-based feature-null replicate:

1. Generate null feature table.
2. Standardize selected feature columns.
3. Compute pairwise distances:

```text
d(i,j) = || z_i - z_j ||_2
```

4. Compute weights:

```text
w(i,j) = 1 / (1 + d(i,j))
```

5. Select top N edges:

```text
N = 81
```

6. Extract top-strength core:

```text
k = 6
```

7. Extract alternative envelopes:

```text
mutual_kNN_k3
maximum_spanning_tree
```

8. Compare against observed core.

---

## 13. Reconstruction procedure for edge nulls

For each edge-null replicate:

1. Start from observed N=81 graph.
2. Generate rewired / randomized edge set.
3. Assign weights according to null rule.
4. Sort by weight.
5. Extract top-strength core:

```text
k = 6
```

6. Extract alternative envelopes:

```text
mutual_kNN_k3
maximum_spanning_tree
```

7. Compare against observed core.

---

## 14. Core metrics

Let:

```text
E_obs_core = observed six-edge reference core
E_null_core = null six-edge top-strength core
```

Compute:

```text
observed_core_shared_edges = |E_obs_core ∩ E_null_core|
observed_core_recovery_fraction = observed_core_shared_edges / 6
observed_core_jaccard = |E_obs_core ∩ E_null_core| / |E_obs_core ∪ E_null_core|
```

If both cores have 6 edges:

```text
observed_core_jaccard = shared_edges / (12 - shared_edges)
```

---

## 15. Envelope metrics

For each null method envelope:

```text
observed_core_containment_in_null =
  |E_obs_core ∩ E_null_method| / |E_obs_core|

null_core_self_containment =
  |E_null_core ∩ E_null_method| / |E_null_core|
```

Interpretation:

```text
observed_core_containment_in_null:
  Does the observed core reappear in the null envelope?

null_core_self_containment:
  Is core-in-envelope behavior generic for this null pipeline?
```

---

## 16. Distribution metrics

For each null model and metric, report:

```text
replicate_count
observed_value
null_mean
null_std
null_min
null_q05
null_median
null_q95
null_max
p_like_upper_tail
```

Use:

```text
p_like = (1 + count(null >= observed)) / (R + 1)
```

Interpretation remains diagnostic, not formal proof.

---

## 17. Replicate count

Initial BMC-14d:

```text
replicates = 500
```

Rationale:

```text
BMC-14 used 100 replicates.
Red Team requested higher replicate counts for stronger nulls.
500 is a reasonable first stronger run.
```

If runtime is high, allow config override:

```text
replicates = 100
```

for quick testing.

Final-facing run may use:

```text
replicates = 1000
```

if computationally feasible.

---

## 18. Expected outputs

BMC-14d should write:

```text
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_null_replicate_summary.csv
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_null_method_containment_summary.csv
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_null_distribution_summary.csv
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_readout.md
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_metrics.json
```

Optional:

```text
runs/BMC-14d/covariance_structured_null_controls_open/null_feature_tables/
runs/BMC-14d/covariance_structured_null_controls_open/null_edge_tables/
```

Raw replicate tables should be optional.

---

## 19. Field list: bmc14d_null_replicate_summary.csv

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model name |
| random_seed | integer | Seed used for replicate |
| null_family | string | feature_covariance or edge_structured |
| edge_count_target | integer | Target edge count |
| core_edge_count | integer | Null core size |
| observed_core_shared_edges | integer | Shared edges between observed core and null core |
| observed_core_jaccard | float | Jaccard between observed and null core |
| observed_core_recovery_fraction | float | Fraction of observed core recovered |
| null_core_mean_weight | float | Mean null core edge weight |
| null_core_min_weight | float | Minimum null core edge weight |
| null_core_max_weight | float | Maximum null core edge weight |
| generation_status | string | ok or warning |
| warning_message | string | Diagnostic warning if applicable |

---

## 20. Field list: bmc14d_null_method_containment_summary.csv

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model name |
| null_family | string | feature_covariance or edge_structured |
| method_id | string | Backbone envelope method |
| method_edge_count | integer | Number of method edges |
| observed_core_overlap | integer | Observed core edges present in this null method |
| observed_core_containment_in_null | float | observed_core_overlap / observed_core_size |
| null_core_overlap | integer | Null core edges present in this null method |
| null_core_self_containment | float | null_core_overlap / null_core_size |
| method_mean_weight | float | Mean method edge weight |
| method_min_weight | float | Minimum method edge weight |
| method_max_weight | float | Maximum method edge weight |

---

## 21. Field list: bmc14d_null_distribution_summary.csv

| field | type | description |
|---|---|---|
| null_model_id | string | Null model name |
| null_family | string | feature_covariance or edge_structured |
| metric | string | Metric name |
| replicate_count | integer | Number of valid replicates |
| observed_value | float | Observed comparison value |
| null_mean | float | Mean null value |
| null_std | float | Standard deviation |
| null_min | float | Minimum |
| null_q05 | float | 5 percent quantile |
| null_median | float | Median |
| null_q95 | float | 95 percent quantile |
| null_max | float | Maximum |
| p_like_upper_tail | float | Empirical upper-tail p-like diagnostic |

---

## 22. Interpretation logic

### Strong support for data-specificity

If covariance-preserving and structured graph nulls still do not fully recover the observed core:

```text
max observed_core_shared_edges < 6
```

and observed-core containment in null envelopes remains low, this strengthens the data-specificity interpretation.

### Covariance explanation

If covariance-preserving feature nulls frequently recover many or all observed core edges:

```text
observed_core_shared_edges approaches 6
```

then the observed core may be explainable by feature covariance structure alone.

This would narrow the interpretation.

### Graph-structure explanation

If edge-structured nulls recover the observed core frequently, the core may be driven by generic graph degree/weight structure rather than feature-specific relational geometry.

### Mixed outcome

Possible and likely:

```text
covariance null recovers partial core
edge null recovers little
family covariance recovers more than global covariance
```

This would indicate that the observed core has multiple signal sources.

---

## 23. Allowed statements after BMC-14d

Depending on outcome:

### If strong nulls do not recover the core

Allowed:

```text
The observed N=81 core remains unrecovered under stronger covariance-preserving and structured graph null controls.
```

```text
This further supports data-specificity of the observed core identity within the tested null families.
```

Avoid:

```text
All null explanations have been excluded.
```

### If covariance null partially recovers the core

Allowed:

```text
Covariance-preserving nulls recover part of the observed core, indicating that empirical feature covariance contributes to the reference-core identity.
```

Avoid:

```text
The core is invalid.
```

### If covariance null fully recovers the core

Allowed:

```text
The observed core can be reproduced by covariance-preserving synthetic features, suggesting that the current core identity may be explained by feature covariance structure.
```

Avoid:

```text
The project failed.
```

This would be a useful narrowing result.

---

## 24. Conservative external wording template

> BMC-14d extends the feature-randomized null controls by testing covariance-preserving and structured graph null models. These controls evaluate whether the observed N=81 six-edge reference core can be explained by empirical feature covariance or generic graph edge structure. The result is interpreted as a methodological specificity diagnostic only. Even if the observed core remains unrecovered, this does not establish physical spacetime emergence; it only strengthens the core identity within the tested graph-method pipeline.

---

## 25. Recommended next implementation

Suggested files:

```text
docs/BMC14D_COVARIANCE_STRUCTURED_NULL_CONTROLS_SPEC.md
data/bmc14d_covariance_structured_null_controls_config.yaml
scripts/run_bmc14d_covariance_structured_null_controls.py
```

Suggested output root:

```text
runs/BMC-14d/covariance_structured_null_controls_open/
```

Initial config:

```text
replicates = 500
null_models:
  global_covariance_gaussian
  family_covariance_gaussian
  weight_rank_edge_rewire
```

Optional later:

```text
degree_preserving_edge_rewire
gaussian_copula_covariance_null
noise_perturbation
```

---

## 26. Relationship to future BMC-15

BMC-15 geometry-proxy diagnostics should come only after BMC-14d or equivalent stronger null controls.

BMC-15 candidate metrics:

```text
embedding stress
local dimension proxy
triangle inequality defects
geodesic consistency
component growth
local clustering profile
```

But BMC-15 should not be used to claim physical spacetime unless the methodological core remains robust under stronger null controls.

---

## 27. Final internal summary

```text
BMC-14:
Schuetteln der Features erzeugt nicht unseren Keim.

BMC-14d:
Jetzt pruefen wir,
ob die statistische Zutaten-Kovarianz
oder generische Graphstruktur
den Keim erzwingen kann.
```

Loriot-compatible version:

```text
Der Klunker liegt nicht zufaellig wieder im Topf.
Nun pruefen wir,
ob das Rezept selbst ihn automatisch formt.
```
