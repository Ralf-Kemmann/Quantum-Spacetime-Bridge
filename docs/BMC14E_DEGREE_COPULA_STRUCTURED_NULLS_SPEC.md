# BMC-14e Degree-Preserving / Copula Structured Nulls Specification

## Purpose

BMC-14e continues the BMC-14 null-control sequence after BMC-14d.

BMC-14d showed that the observed six-edge N=81 reference core was not fully recovered under:

```text
global_covariance_gaussian
family_covariance_gaussian
weight_rank_edge_rewire
```

The strongest remaining methodological objections are now:

```text
1. The observed core might be explainable by degree / hub structure.
2. The observed core might be explainable by rank/correlation structure not captured by Gaussian covariance nulls.
```

BMC-14e therefore adds:

```text
degree-preserving graph nulls
degree + weight-class structured graph nulls
Gaussian copula / rank-correlation feature nulls
```

Internal image:

```text
Ist der Klunker vielleicht nur ein Hub-/Grad-Trick
oder ein Rang-Korrelations-Trick?
```

---

## 1. Working question

Formal question:

```text
Can the observed N=81 six-edge reference core be reproduced by null models
that preserve degree structure or rank/correlation feature structure more strongly
than previous BMC-14/BMC-14d null controls?
```

Subquestions:

```text
Does preserving the N=81 degree sequence reproduce the observed core?
Does preserving degree plus coarse weight classes reproduce the observed core?
Does preserving empirical marginal distributions and rank correlations reproduce the observed core?
```

---

## 2. Reference object

The reference object remains the observed BMC-13a top-strength core:

```text
method_id = top_strength_reference
edge_count = 6
edge_count_target = 81
case_id = baseline_all_features
```

Observed reference value:

```text
observed_core_shared_edges = 6 / 6
observed_core_recovery_fraction = 1.000
```

This is a graph-method diagnostic object, not a physical spacetime object.

---

## 3. Current chain before BMC-14e

```text
BMC-12f:
  N=81 threshold/gap robustness within the tested grid.

BMC-13a:
  The N=81 six-edge core is embedded in all tested alternative backbone envelopes.

BMC-14:
  Simple feature-randomized nulls do not fully recover the observed core.

BMC-14d:
  Global covariance, family covariance, and weight-rank edge rewiring do not fully recover the observed core.

BMC-14 series consolidation:
  0 / 1800 tested null replicates fully recovered the observed core.
```

Remaining open controls:

```text
degree-preserving edge rewiring
degree + weight-class preserving edge rewiring
Gaussian copula / rank-preserving covariance null
noise perturbation
```

BMC-14e addresses the first three.

Noise perturbation should remain a later BMC-14f block because it asks a different question:

```text
local numerical stability
```

rather than:

```text
null-structure specificity
```

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

Observed edge inventory:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_edges_inventory.csv
```

Feature columns:

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

Metadata columns:

```text
node_id
node_family
node_label
origin_tag
comment
```

---

# Part A: Degree-preserving graph nulls

## 5. Null A1: degree_preserving_edge_rewire

### Definition

Start from the observed N=81 baseline graph.

Randomly rewire edges while preserving the degree sequence as closely as possible.

A standard double-edge swap can be used:

```text
(a,b), (c,d) -> (a,d), (c,b)
```

subject to:

```text
no self-loops
no duplicate edges
degree sequence preserved
```

After rewiring, assign the observed N=81 edge weights to the rewired edges.

Default weight assignment:

```text
shuffle observed weights randomly across rewired edges
```

### Preserves

```text
node set
edge count = 81
degree sequence
edge weight multiset
```

### Does not preserve

```text
original edge identities
feature-space geometry
local clustering exactly
specific neighbor identities
```

### Interpretation

This tests whether the observed top-strength core can be explained by degree / hub structure plus the observed weight distribution.

If the observed core is recovered often here, the current core may reflect hub-driven topology rather than data-specific relation identity.

---

## 6. Null A2: degree_weightclass_edge_rewire

### Definition

Start from the observed N=81 graph.

Assign each observed edge to coarse weight classes, for example:

```text
high
mid
low
```

or quantile classes:

```text
q1, q2, q3, q4
```

Then perform degree-preserving rewiring while approximately preserving the number of edges per weight class.

Practical implementation option:

```text
degree_preserving_edge_rewire + weight_class_shuffle
```

or:

```text
degree_preserving_edge_rewire + weight_class_label diagnostic
```

if exact enforcement is too complex.

### Preserves

```text
node set
edge count
degree sequence approximately or exactly
edge weight distribution
coarse weight-class structure
```

### Interpretation

This asks:

```text
Can hub structure plus coarse edge-strength organization reproduce the observed core?
```

---

# Part B: Copula / rank-correlation feature nulls

## 7. Null B1: gaussian_copula_feature_null

### Motivation

BMC-14d used Gaussian covariance nulls. These preserve mean/covariance structure but do not preserve empirical marginal distributions or rank structure.

A Gaussian copula null is stronger because it can preserve:

```text
empirical marginal distributions
rank-like correlation structure
```

while removing exact node-feature identity.

### Definition

For the selected feature matrix X:

1. Convert each feature column to empirical ranks.
2. Convert ranks to approximate normal scores:

```text
z = Phi^-1((rank - 0.5) / n)
```

3. Estimate the correlation matrix R in normal-score space.
4. Generate synthetic correlated normal samples:

```text
Z_null ~ N(0, R)
```

5. Convert each generated normal column back through the empirical quantile function of the original feature column.

### Preserves

```text
node count
empirical marginal distributions approximately
rank-correlation structure approximately
feature dependence structure more strongly than Gaussian covariance alone
```

### Does not preserve

```text
exact node-feature identity
exact feature rows
family-specific structure unless implemented family-wise
```

### Interpretation

This tests whether the observed core can be explained by empirical feature marginals plus rank-correlation structure.

---

## 8. Optional Null B2: family_gaussian_copula_feature_null

Perform Gaussian copula generation within each node_family.

### Preserves

```text
family membership
family-specific empirical marginal distributions approximately
family-specific rank-correlation structure where sample size allows
```

### Practical warning

Small family sizes may make rank-correlation estimates unstable.

Fallback options:

```text
global copula within small families
diagonal copula
skip family-copula for underpowered families
```

Recommendation:

```text
Implement global gaussian_copula_feature_null first.
Keep family_gaussian_copula optional / follow-up.
```

---

## 9. Recommended initial BMC-14e scope

Initial implementation should include:

```text
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
gaussian_copula_feature_null
```

Optional if implementation remains manageable:

```text
family_gaussian_copula_feature_null
```

Suggested replicates:

```text
500 per null model
```

If runtime or rewire feasibility becomes a problem:

```text
quick_test_replicates = 50 or 100
full_run_replicates = 500
```

---

## 10. Graph reconstruction for copula feature nulls

For each copula feature-null replicate:

1. Generate synthetic feature table by Gaussian copula.
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

7. Extract alternative method envelopes:

```text
mutual_kNN_k3
maximum_spanning_tree
```

8. Compare against observed core.

---

## 11. Graph reconstruction for degree rewiring nulls

For each degree-rewiring null replicate:

1. Start from observed N=81 graph.
2. Perform degree-preserving double-edge swaps.
3. Assign weights according to configured rule:

```text
shuffle_weights
rank_assign_weights
weightclass_shuffle
```

4. Extract top-strength core:

```text
k = 6
```

5. Extract alternative method envelopes:

```text
mutual_kNN_k3
maximum_spanning_tree
```

6. Compare against observed core.

---

## 12. Rewire diagnostics

Degree-preserving rewiring should report:

```text
attempted_swaps
successful_swaps
failed_swaps
swap_success_fraction
degree_sequence_preserved
edge_count_preserved
duplicate_or_self_loop_rejections
```

If exact degree preservation fails:

```text
generation_status = warning
warning_message = reason
```

For publication-facing interpretation, failed or under-mixed rewires must not be hidden.

---

## 13. Core metrics

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

If both cores have six edges:

```text
observed_core_jaccard = shared_edges / (12 - shared_edges)
```

---

## 14. Envelope metrics

For each null method envelope:

```text
observed_core_containment_in_null =
  |E_obs_core ∩ E_null_method| / |E_obs_core|

null_core_self_containment =
  |E_null_core ∩ E_null_method| / |E_null_core|
```

As before, this distinguishes:

```text
observed core recovery
```

from:

```text
pipeline-generic core-in-envelope behavior
```

---

## 15. Distribution summary

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

This remains an empirical diagnostic, not a formal proof.

---

## 16. Expected outputs

BMC-14e should write:

```text
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_null_replicate_summary.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_null_method_containment_summary.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_null_distribution_summary.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_rewire_diagnostics.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_readout.md
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_metrics.json
```

Optional:

```text
runs/BMC-14e/degree_copula_structured_nulls_open/null_feature_tables/
runs/BMC-14e/degree_copula_structured_nulls_open/null_edge_tables/
```

Raw tables should be optional and controlled by config.

---

## 17. Field list: bmc14e_null_replicate_summary.csv

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model name |
| random_seed | integer | Seed used for replicate |
| null_family | string | degree_structured or copula_feature |
| edge_count_target | integer | Target edge count |
| core_edge_count | integer | Null core size |
| observed_core_shared_edges | integer | Shared edges between observed and null core |
| observed_core_jaccard | float | Jaccard between observed and null core |
| observed_core_recovery_fraction | float | observed_core_shared_edges / observed_core_size |
| null_core_mean_weight | float | Mean null core edge weight |
| null_core_min_weight | float | Minimum null core edge weight |
| null_core_max_weight | float | Maximum null core edge weight |
| generation_status | string | ok or warning |
| warning_message | string | Diagnostic warning if applicable |

---

## 18. Field list: bmc14e_null_method_containment_summary.csv

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Null model name |
| random_seed | integer | Seed used for replicate |
| null_family | string | degree_structured or copula_feature |
| method_id | string | Backbone envelope method |
| method_edge_count | integer | Number of method edges |
| method_node_count | integer | Number of nodes in method |
| method_component_count | integer | Number of connected components |
| method_largest_component_size | integer | Size of largest component |
| observed_core_overlap | integer | Observed core edges present in this null method |
| observed_core_containment_in_null | float | observed_core_overlap / observed_core_size |
| null_core_overlap | integer | Null core edges present in this null method |
| null_core_self_containment | float | null_core_overlap / null_core_size |
| method_mean_weight | float | Mean method edge weight |
| method_min_weight | float | Minimum method edge weight |
| method_max_weight | float | Maximum method edge weight |

---

## 19. Field list: bmc14e_null_distribution_summary.csv

| field | type | description |
|---|---|---|
| null_model_id | string | Null model name |
| null_family | string | degree_structured or copula_feature |
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

## 20. Field list: bmc14e_rewire_diagnostics.csv

| field | type | description |
|---|---|---|
| replicate_id | integer | Null replicate index |
| null_model_id | string | Rewire null model |
| random_seed | integer | Seed used |
| attempted_swaps | integer | Number of attempted double-edge swaps |
| successful_swaps | integer | Number of accepted swaps |
| failed_swaps | integer | Number of rejected swaps |
| swap_success_fraction | float | successful_swaps / attempted_swaps |
| edge_count_preserved | boolean string | Whether edge count was preserved |
| degree_sequence_preserved | boolean string | Whether degree sequence was preserved |
| warning_message | string | Warning if applicable |

---

## 21. Interpretation logic

### Strong support

If BMC-14e nulls still fail to recover the full observed core:

```text
max observed_core_shared_edges < 6
```

then the observed core remains robust against an expanded null set, including degree and rank-correlation controls.

### Degree / hub explanation

If degree-preserving rewiring frequently recovers the observed core:

```text
observed_core_shared_edges approaches 6
```

then the observed core may be explainable by degree/hub topology.

### Rank-correlation explanation

If Gaussian copula feature nulls frequently recover the observed core:

```text
observed_core_shared_edges approaches 6
```

then the observed core may be explainable by feature marginal distributions plus rank-correlation structure.

### Mixed result

If BMC-14e recovers partial but not full core structure, interpret as:

```text
degree or rank-correlation structure contributes to the signal
but does not fully explain the observed core identity.
```

---

## 22. Allowed statements after BMC-14e

Depending on outcome:

### If full recovery remains absent

Allowed:

```text
The observed N=81 six-edge core remains unrecovered under degree-preserving and copula/rank-correlation null controls.
```

```text
This further supports data-specificity of the observed core identity within the tested null families.
```

Avoid:

```text
All null explanations are excluded.
```

### If degree-preserving null partially recovers the core

Allowed:

```text
Degree structure contributes to partial recovery of the observed core, but does not fully reconstruct the six-edge identity.
```

Avoid:

```text
Degree structure is irrelevant.
```

### If copula null partially recovers the core

Allowed:

```text
Rank-correlation structure contributes to partial recovery of the observed core, but does not fully reconstruct the six-edge identity.
```

Avoid:

```text
Feature dependence structure has no role.
```

### If any null fully recovers the core

Allowed:

```text
The observed core can be reproduced under this stronger null, requiring a narrower interpretation of the current core identity.
```

Avoid:

```text
The project failed.
```

---

## 23. Conservative external wording template

> BMC-14e extends the structured-null analysis by testing degree-preserving graph rewiring and Gaussian-copula feature nulls. These controls evaluate whether the observed N=81 six-edge reference core can be explained by hub/degree structure or by rank-correlation feature structure. The result is interpreted as a methodological specificity diagnostic only. Even if the observed core remains unrecovered, this does not establish physical spacetime emergence; it only further constrains graph-method and feature-null explanations.

---

## 24. Relationship to BMC-14f and BMC-15

BMC-14e addresses structural null explanations.

BMC-14f should address local numerical stability:

```text
small feature perturbations
noise tolerance
core survival probability
edge-rank stability
```

BMC-15 should address geometry-proxy diagnostics only after the null stack is sufficiently constrained:

```text
embedding stress
local dimension proxy
triangle inequality defects
geodesic consistency
component growth
```

---

## 25. Recommended next implementation

Suggested files:

```text
docs/BMC14E_DEGREE_COPULA_STRUCTURED_NULLS_SPEC.md
data/bmc14e_degree_copula_structured_nulls_config.yaml
scripts/run_bmc14e_degree_copula_structured_nulls.py
```

Suggested output root:

```text
runs/BMC-14e/degree_copula_structured_nulls_open/
```

Initial config:

```text
replicates = 500

null_models:
  degree_preserving_edge_rewire
  degree_weightclass_edge_rewire
  gaussian_copula_feature_null
```

Optional:

```text
family_gaussian_copula_feature_null
```

---

## 26. Final internal summary

```text
BMC-14d:
Kovarianz-Rezept und Kantengewicht-Trick bauen unseren Keim nicht vollständig nach.

BMC-14e:
Jetzt prüfen wir,
ob Hub-/Gradstruktur oder Rang-Korrelationen
den Keim erklären können.
```

Loriot-compatible version:

```text
Der Klunker liegt nicht zufällig wieder im Topf.
Rezept und Kantensortierung reichen nicht.
Nun prüfen wir,
ob die Topfform oder die Zutaten-Rangordnung den Klunker erzwingt.
```
