# BMC-14 Series Consolidated Robustness Note

## Purpose

This note consolidates the BMC-14 null-control sequence.

It integrates:

```text
BMC-14:
  feature-randomized null controls

BMC-14 Red-Team integration:
  distinction between observed-core identity and generic core-in-envelope behavior

BMC-14d:
  covariance-preserving and structured null controls
```

The aim is to freeze the current methodological status before moving to further controls or geometry-proxy diagnostics.

Internal image:

```text
Der Klunker liegt nicht zufällig wieder im Topf.
Auch das Rezept und die Kantensortierung bauen ihn nicht vollständig nach.
Aber die Küchenmaschine formt grundsätzlich gern Klümpchen in Hüllen.
```

---

## 1. Reference object

The reference object throughout the BMC-14 series is the observed BMC-13a six-edge N=81 top-strength core:

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

This object is a methodological graph-diagnostic object.

It is not a physical spacetime object.

---

## 2. Preceding status before BMC-14

### BMC-12f

BMC-12f showed that the BMC09d N=81 reference anchor is stable across the tested decision-threshold / dominance-gap grid.

Conservative statement:

```text
N=81 is threshold/gap robust within the tested grid.
```

### BMC-13a

BMC-13a showed that the six-edge N=81 top-strength reference core is fully contained in all tested alternative backbone constructions:

```text
maximum_spanning_tree
mutual_kNN_k3
threshold_path_consensus_min3
top_strength_reference
```

Conservative statement:

```text
The compact N=81 reference core is embedded in larger method-dependent backbone envelopes.
```

Limitation already visible:

```text
core-in-envelope containment may be partly pipeline-generic.
```

---

## 3. BMC-14: feature-randomized null controls

BMC-14 tested whether the observed N=81 core reappears under feature-randomized null controls.

Null models:

```text
featurewise_permutation
rowwise_vector_permutation
family_preserving_row_permutation
```

Replicates:

```text
100 per null model
300 total null replicates
```

### Main BMC-14 result

| null_model_id | mean shared edges | median shared edges | max shared edges | max recovery fraction |
|---|---:|---:|---:|---:|
| featurewise_permutation | 0.17 / 6 | 0 | 2 | 0.333 |
| rowwise_vector_permutation | 0.11 / 6 | 0 | 1 | 0.167 |
| family_preserving_row_permutation | 0.75 / 6 | 1 | 3 | 0.500 |

Finding:

```text
0 / 300 tested feature-randomized null replicates fully recovered the observed six-edge core.
```

### Interpretation

The observed core identity is not reproduced by the tested simple feature-randomized nulls.

Family-preserving permutation recovered more of the observed core than the more disruptive nulls, indicating that family structure contributes to the signal.

However:

```text
family structure alone did not recover the full 6/6 observed core.
```

---

## 4. BMC-14 Red-Team integration

The Red-Team review converged on a key distinction.

### Observed-core identity

Question:

```text
Does the exact observed six-edge core reappear under nulls?
```

BMC-14 answer:

```text
No full recovery in tested nulls.
```

### Core-in-envelope motif

Question:

```text
Do null-generated top-strength cores also sit inside larger null method envelopes?
```

BMC-14 answer:

```text
Yes, often.
```

### Consolidated Red-Team interpretation

The observed core identity appears data-specific within the tested feature-randomized null-model family.

The core-in-envelope motif itself is partly pipeline-generic.

Short version:

```text
The specific observed core is not null-typical.
The containment motif is partly pipeline-typical.
```

Internal version:

```text
Die Suppe klumpt immer irgendwie.
Aber sie klumpt nicht zu unserem Keim.
```

---

## 5. Red-Team-identified open gap after BMC-14

The strongest remaining objection after BMC-14 was:

```text
The observed core may be rare under feature-randomized nulls,
but it might still be explained by stronger structure-preserving nulls.
```

Specifically:

```text
empirical feature covariance
family-level covariance
generic edge-weight rank structure
degree / graph topology effects
```

This led to BMC-14d.

---

## 6. BMC-14d: covariance-preserving / structured null controls

BMC-14d tested stronger null families.

Null models:

```text
global_covariance_gaussian
family_covariance_gaussian
weight_rank_edge_rewire
```

Replicates:

```text
500 per null model
1500 total structured null replicates
```

### BMC-14d main result

| null_model_id | null_family | mean shared edges | median shared edges | q95 shared edges | max shared edges | max recovery fraction |
|---|---|---:|---:|---:|---:|---:|
| global_covariance_gaussian | feature_covariance | 0.174 / 6 | 0 | 1 | 2 | 0.333 |
| family_covariance_gaussian | feature_covariance | 0.528 / 6 | 0 | 2 | 3 | 0.500 |
| weight_rank_edge_rewire | edge_structured | 0.152 / 6 | 0 | 1 | 2 | 0.333 |

Finding:

```text
0 / 1500 tested BMC-14d structured null replicates fully recovered the observed six-edge core.
```

---

## 7. Interpretation of BMC-14d nulls

### 7.1 Global covariance null

The global covariance-preserving Gaussian feature null reached:

```text
max shared edges = 2 / 6
```

Interpretation:

```text
The global empirical feature covariance alone did not reproduce the full observed core.
```

Avoid overclaiming:

```text
This does not mean feature covariance has no role.
```

### 7.2 Family covariance null

The family covariance null reached:

```text
max shared edges = 3 / 6
```

Interpretation:

```text
Family-level covariance carries part of the signal,
but does not fully reconstruct the observed six-edge core.
```

This is consistent with the BMC-14 family-preserving permutation result.

### 7.3 Weight-rank edge rewire

The weight-rank edge-rewire null reached:

```text
max shared edges = 2 / 6
```

Interpretation:

```text
Generic edge-weight rank structure did not reproduce the full observed core.
```

Avoid overclaiming:

```text
This does not exclude all graph-structure null explanations.
```

Degree-preserving rewiring remains open.

---

## 8. Consolidated BMC-14-series finding

Across the BMC-14 series:

```text
BMC-14 feature nulls:
  max recovery = 3 / 6

BMC-14d global covariance null:
  max recovery = 2 / 6

BMC-14d family covariance null:
  max recovery = 3 / 6

BMC-14d weight-rank edge rewire:
  max recovery = 2 / 6
```

Combined:

```text
0 / 1800 tested null replicates fully recovered the observed six-edge N=81 core.
```

This includes:

```text
300 simple feature-randomized null replicates
1500 covariance / structured null replicates
```

---

## 9. What is strengthened?

The BMC-14 series strengthens the interpretation that:

```text
the observed six-edge N=81 core identity is not reproduced by the tested null families
```

including:

```text
simple feature randomization
family-preserving feature randomization
global covariance-preserving synthetic features
family-level covariance-preserving synthetic features
weight-rank edge rewiring
```

Therefore, within the tested null space, the observed core identity is the strongest current methodological object in the BMC series.

---

## 10. What remains limited?

### 10.1 Core-in-envelope motif remains pipeline-generic

BMC-14 and BMC-14d repeatedly show high null-core self-containment.

Thus:

```text
core-in-envelope containment is partly generic to the extraction pipeline.
```

The main evidence is not the containment motif itself.

The main evidence is:

```text
the specific observed edge identity
```

### 10.2 Family/block structure contributes signal

Family-preserving and family-covariance nulls recover more of the observed core than more disruptive nulls.

Thus:

```text
family / block structure contributes to the observed signal.
```

But:

```text
family / block structure does not fully explain the observed six-edge core.
```

### 10.3 Not all nulls are excluded

Open null families include:

```text
degree-preserving edge rewiring
degree + weight-class preserving edge rewiring
Gaussian copula / rank-preserving covariance null
noise perturbation around observed features
non-Gaussian synthetic feature nulls
```

### 10.4 No physical claim follows directly

The BMC-14 series does not establish:

```text
physical spacetime emergence
causal structure
continuum geometry
metric reconstruction
local dimension
physical observables
```

It remains:

```text
a methodological graph/null-model robustness diagnostic
```

---

## 11. Strongest current interpretation

The strongest current interpretation is:

> The BMC-14 series supports the data-specificity of the observed N=81 six-edge reference-core identity within the tested null families. Across 1800 tested null replicates, including simple feature randomizations, covariance-preserving feature nulls, family-level covariance nulls, and weight-rank edge rewiring, the observed six-edge core was never fully recovered. The strongest partial recoveries occurred in family-preserving and family-covariance nulls, indicating that family/block structure contributes to the signal but does not fully explain the observed core identity. Core-in-envelope containment remains partly pipeline-generic.

Short version:

```text
The specific core is robust against the tested nulls.
The envelope motif is not unique.
Family/block structure contributes but does not fully explain the core.
```

Internal version:

```text
Der gleiche Klunker liegt nicht zufällig wieder im Topf.
Auch das Rezept und die Kantensortierung bauen ihn nicht vollständig nach.
Aber Familienstruktur färbt den Klunker sichtbar mit.
```

---

## 12. Allowed statements

Allowed:

```text
The observed N=81 six-edge core was not fully recovered in any tested BMC-14-series null replicate.
```

```text
Across 1800 tested null replicates, maximum recovery was 3/6 observed core edges.
```

```text
The observed core identity appears robust against the tested null families.
```

```text
Family-preserving and family-covariance nulls recover more of the observed core than more disruptive nulls, indicating that family/block structure contributes to the signal.
```

```text
Core-in-envelope containment remains partly pipeline-generic.
```

```text
Degree-preserving and copula/rank-preserving nulls remain open.
```

---

## 13. Avoided statements

Avoid:

```text
The core is proven non-random.
```

```text
All null explanations are excluded.
```

```text
The core-in-envelope motif is unique to the observed data.
```

```text
BMC-14 proves physical structure.
```

```text
BMC-14 proves spacetime emergence.
```

```text
The empirical p-like values are formal p-values.
```

```text
Feature covariance has no role.
```

```text
Graph structure has no role.
```

---

## 14. Conservative external wording

A suitable research-note paragraph:

> The BMC-14 series evaluates the observed N=81 six-edge reference core against increasingly structured null controls. Across 1800 tested null replicates, including feature-randomized nulls, family-preserving feature randomization, global covariance-preserving synthetic features, family-level covariance nulls, and weight-rank edge rewiring, the observed six-edge core was never fully recovered. Maximum recovery was 3/6 observed core edges. The stronger partial recovery under family-preserving and family-covariance nulls suggests that family/block structure contributes to the observed signal, but does not fully explain the reference-core identity. At the same time, null-generated cores commonly show high containment inside their own alternative backbone envelopes, indicating that core-in-envelope containment is partly generic to the extraction pipeline. The result supports data-specificity of the observed core identity within the tested null families, without implying physical spacetime emergence or uniqueness of the containment motif.

---

## 15. Updated methodological chain

```text
BMC-12f:
  threshold/gap robustness at N=81

BMC-13a:
  core embedded in alternative backbone envelopes

BMC-14:
  observed core not recovered by simple feature-randomized nulls

BMC-14 Red Team:
  observed-core identity vs generic containment motif separated

BMC-14d:
  observed core not recovered by covariance-preserving or weight-rank nulls
```

This gives the current robust chain:

```text
threshold-stable
method-crossing embedded
feature-null resistant
covariance-null resistant
weight-rank-null resistant
```

within the tested diagnostic scope.

---

## 16. Next recommended controls

### Option A: BMC-14e Degree-Preserving / Copula Structured Nulls

This is the next technical robustness step.

Candidate nulls:

```text
degree-preserving edge rewiring
degree + weight-class preserving edge rewiring
Gaussian copula / rank-preserving covariance null
```

Purpose:

```text
Test degree / hub effects and non-Gaussian rank covariance explanations.
```

### Option B: BMC-14f Noise Perturbation

Purpose:

```text
Test local numerical stability of the observed core under small feature perturbations.
```

### Option C: BMC-15 Geometry-Proxies

Only after stronger nulls:

```text
embedding stress
local dimension proxy
triangle inequality defects
geodesic consistency
component growth
```

---

## 17. Recommended next action

The safest next action is:

```text
Short Red-Team review of BMC-14d / BMC-14-series consolidation
```

Then proceed to:

```text
BMC-14e Degree-Preserving / Copula Structured Nulls
```

Geometry-proxy diagnostics should remain downstream.

---

## 18. File anchors

BMC-14 specification:

```text
docs/BMC14_NULL_MODEL_FEATURE_CONTROL_SPEC.md
```

BMC-14 result note:

```text
docs/BMC14_NULL_MODEL_FEATURE_CONTROL_RESULT_NOTE.md
```

BMC-14 Red-Team integration:

```text
docs/BMC14_RED_TEAM_INTEGRATION_NOTE.md
```

BMC-14d specification:

```text
docs/BMC14D_COVARIANCE_STRUCTURED_NULL_CONTROLS_SPEC.md
```

BMC-14d result note:

```text
docs/BMC14D_COVARIANCE_STRUCTURED_NULL_CONTROLS_RESULT_NOTE.md
```

This consolidated note:

```text
docs/BMC14_SERIES_CONSOLIDATED_ROBUSTNESS_NOTE.md
```

---

## 19. Consolidated status

### Befund

The observed N=81 six-edge core was not fully recovered in any tested BMC-14-series null replicate. Across 1800 total null replicates, maximum recovery was 3/6 observed core edges.

### Interpretation

The observed core identity appears robust against the tested null families. Family/block structure contributes to the signal, while core-in-envelope containment remains partly pipeline-generic.

### Hypothesis

The observed N=81 core may represent a specific relational structure in the current feature-space graph pipeline, not reducible to the tested feature-randomized, covariance-preserving, or weight-rank null mechanisms.

### Open gap

Degree-preserving edge rewiring, copula/rank covariance nulls, noise perturbation, and eventual geometry-proxy diagnostics remain open.
