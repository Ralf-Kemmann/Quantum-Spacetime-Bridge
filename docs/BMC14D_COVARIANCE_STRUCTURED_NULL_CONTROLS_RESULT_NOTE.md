# BMC-14d Covariance-Preserving / Structured Null Controls Result Note

## Purpose

BMC-14d addresses the strongest remaining Red-Team objection after BMC-14.

BMC-14 showed that the observed six-edge N=81 reference core was not fully recovered under feature-randomized null models:

```text
featurewise_permutation
rowwise_vector_permutation
family_preserving_row_permutation
```

However, these nulls all belong to the same broad family:

```text
feature reassignment / feature randomization
```

The Red Team therefore asked whether the observed N=81 core could instead be explained by stronger structure-preserving mechanisms:

```text
empirical feature covariance
family-level covariance
generic edge-weight / graph-rank structure
```

BMC-14d tests these stronger alternatives.

Internal image:

```text
Der Klunker liegt nicht zufällig wieder im Topf.
Nun prüfen wir, ob das Rezept selbst ihn automatisch formt.
```

---

## 1. Working question

Formal question:

```text
Can the observed N=81 six-edge reference core be reproduced by null models
that preserve stronger statistical or graph-structural properties?
```

More specifically:

```text
Can feature covariance alone reproduce the observed core?
Can family-level covariance reproduce the observed core?
Can generic edge-weight rank structure reproduce the observed core?
```

---

## 2. Reference object

The reference object remains the observed BMC-13a six-edge top-strength core:

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

Important:

```text
The observed core is a graph-method diagnostic object,
not a physical spacetime object.
```

---

## 3. Null models tested

BMC-14d used 500 replicates per null model.

### 3.1 global_covariance_gaussian

Synthetic feature vectors were generated from a multivariate Gaussian distribution using the empirical global feature mean and covariance matrix.

Preserves approximately:

```text
global feature mean
global feature covariance
node count
feature dimensionality
```

Does not preserve:

```text
exact feature values
exact node-feature assignment
family-specific structure
non-Gaussian marginal structure
```

### 3.2 family_covariance_gaussian

Synthetic feature vectors were generated family by family using family-level mean and covariance estimates, with fallback handling for small families.

Preserves approximately:

```text
node family membership
family-level feature mean
family-level covariance structure
node count per family
```

Does not preserve:

```text
exact node-feature assignment
exact observed feature values
full empirical rank structure
```

### 3.3 weight_rank_edge_rewire

The observed N=81 edge-weight multiset was preserved, but weights were assigned to randomly sampled node pairs.

Preserves:

```text
node set
edge count = 81
edge weight distribution / weight ranks
```

Does not preserve:

```text
original edge identities
feature-space origin
degree structure
local relational geometry
```

---

## 4. Run setup

BMC-14d used:

```text
replicates per null model = 500
edge_count_target = 81
core_edge_count = 6
```

For covariance nulls, the graph was reconstructed using:

```text
standardized features
Euclidean distance
w(i,j) = 1 / (1 + d(i,j))
top N=81 edges
top-strength core of k=6 edges
```

For edge-rewiring nulls, the observed N=81 weight distribution was rewired over random node pairs before extracting the top-strength core.

---

## 5. Main result: observed core recovery

BMC-14d measured how many of the observed six reference-core edges appeared in the null-generated top-strength cores.

| null_model_id | null_family | mean shared edges | median shared edges | q95 shared edges | max shared edges | max recovery fraction |
|---|---|---:|---:|---:|---:|---:|
| global_covariance_gaussian | feature_covariance | 0.174 / 6 | 0 | 1 | 2 | 0.333 |
| family_covariance_gaussian | feature_covariance | 0.528 / 6 | 0 | 2 | 3 | 0.500 |
| weight_rank_edge_rewire | edge_structured | 0.152 / 6 | 0 | 1 | 2 | 0.333 |

### Finding

No BMC-14d null model fully recovered the observed six-edge core.

```text
observed value = 6 / 6

global_covariance_gaussian max = 2 / 6
family_covariance_gaussian max = 3 / 6
weight_rank_edge_rewire max = 2 / 6
```

Across the tested BMC-14d null space:

```text
0 / 1500 null replicates fully recovered the observed six-edge core
```

---

## 6. Empirical p-like diagnostics

For the primary observed-core metrics, BMC-14d produced:

```text
p_like_upper_tail = 0.001996007984031936
```

This equals approximately:

```text
1 / (500 + 1)
```

because no null replicate reached or exceeded the observed value.

Allowed wording:

```text
empirical p-like diagnostic approx. 0.002 with 500 replicates
```

Avoid:

```text
formal p = 0.002 proof
```

BMC-14d remains an empirical structured-null diagnostic.

---

## 7. Interpretation of global covariance null

The global covariance null produced:

```text
mean shared edges = 0.174 / 6
median shared edges = 0 / 6
max shared edges = 2 / 6
```

### Interpretation

The observed six-edge core is not reproduced by a synthetic feature population preserving the global empirical covariance structure.

This weakens the explanation:

```text
The observed core is simply a consequence of the global feature covariance matrix.
```

Allowed:

```text
The global covariance-preserving null did not reproduce the full observed core.
```

Avoid:

```text
Feature covariance has no role.
```

The result only shows that global covariance alone did not reconstruct the full six-edge core under this null implementation.

---

## 8. Interpretation of family covariance null

The family covariance null produced:

```text
mean shared edges = 0.528 / 6
median shared edges = 0 / 6
q95 shared edges = 2 / 6
max shared edges = 3 / 6
```

This is the strongest null response among the BMC-14d models.

### Interpretation

Family-level covariance carries some of the observed signal, but it does not explain the full six-edge core.

The family covariance null can recover partial core structure, but:

```text
it never reaches 6 / 6
```

This continues the BMC-14 pattern:

```text
family structure contributes to the signal
but does not fully reconstruct the observed core identity
```

---

## 9. Interpretation of weight-rank edge rewiring

The weight-rank edge-rewire null produced:

```text
mean shared edges = 0.152 / 6
median shared edges = 0 / 6
max shared edges = 2 / 6
```

### Interpretation

Preserving the N=81 edge-weight distribution and rewiring it over random node pairs did not reproduce the full observed core.

This weakens the explanation:

```text
The observed core is simply due to edge-weight rank structure
or generic weighted-graph effects.
```

Allowed:

```text
Weight-rank edge rewiring did not reproduce the observed core identity.
```

Avoid:

```text
All graph-structure null explanations are excluded.
```

Degree-preserving and more structured graph nulls remain possible future controls.

---

## 10. Envelope containment under BMC-14d nulls

As in BMC-14, BMC-14d also showed high null-core self-containment.

Examples:

```text
global_covariance_gaussian::mutual_kNN_k3:
  null_core_self_containment mean = 0.996

family_covariance_gaussian::mutual_kNN_k3:
  null_core_self_containment mean = 1.000

weight_rank_edge_rewire::mutual_kNN_k3:
  null_core_self_containment mean = 0.997
```

### Interpretation

Core-in-envelope containment remains partly pipeline-generic.

Thus BMC-14d strengthens the observed core identity, not the uniqueness of the containment motif.

Internal formulation:

```text
Die Maschine baut grundsätzlich gern Keime in Hüllen.
Aber sie baut nicht unseren konkreten Keim nach.
```

---

## 11. Updated status after BMC-14d

### Before BMC-14d

BMC-14 supported:

```text
The observed core identity is data-specific within tested feature-randomized nulls.
```

Open Red-Team objection:

```text
Maybe the core is explained by feature covariance or generic edge-weight structure.
```

### After BMC-14d

BMC-14d supports:

```text
The observed core identity is not fully reproduced by:
  global covariance-preserving synthetic features,
  family-level covariance-preserving synthetic features,
  weight-rank edge-rewiring controls.
```

Therefore:

```text
The observed core identity remains robust against the tested stronger null families.
```

Still:

```text
core-in-envelope containment remains partly pipeline-generic
```

---

## 12. Strongest current interpretation

The strongest current interpretation is:

> BMC-14d extends the null-control evidence by showing that the observed N=81 six-edge core is not fully recovered under global covariance-preserving feature nulls, family-level covariance nulls, or weight-rank edge-rewiring controls across 500 replicates per null model. This strengthens the interpretation that the observed core identity is not explained by simple feature randomization, empirical covariance structure alone, or generic edge-weight rank structure within the tested null families. Core-in-envelope containment remains partly pipeline-generic.

Short version:

```text
Weder Schütteln,
noch Kovarianz-Rezept,
noch Kantengewichts-Rangordnung
baut unseren Klunker vollständig nach.

Aber:
Die Pipeline baut grundsätzlich gern Klunker-in-Hüllen.
```

---

## 13. What BMC-14d strengthens

BMC-14d strengthens the robustness chain:

```text
BMC-12f:
  N=81 is threshold/gap robust within the tested grid.

BMC-13a:
  The N=81 core is embedded in all tested alternative backbone envelopes.

BMC-14:
  The observed N=81 core is not recovered by simple feature-randomized nulls.

BMC-14d:
  The observed N=81 core is not recovered by covariance-preserving feature nulls
  or weight-rank edge-rewiring controls.
```

This makes the observed N=81 core the strongest current methodological object in the BMC series.

---

## 14. What BMC-14d does not prove

BMC-14d does not prove:

```text
physical spacetime emergence
```

It does not prove:

```text
a unique physical geometry
```

It does not prove:

```text
causal structure
```

It does not prove:

```text
continuum reconstruction
```

It does not prove:

```text
all possible null models are excluded
```

It does not prove:

```text
core-in-envelope containment is data-specific
```

because null-generated cores still show high self-containment.

---

## 15. Allowed statements after BMC-14d

Allowed:

```text
The observed N=81 six-edge core was not fully recovered in any tested BMC-14d structured null replicate.
```

```text
Global covariance-preserving synthetic features did not reproduce the full observed core.
```

```text
Family-level covariance nulls recovered more of the observed core than the global covariance null, but still reached only 3/6 edges at maximum.
```

```text
Weight-rank edge rewiring did not reproduce the observed core identity.
```

```text
BMC-14d further supports data-specificity of the observed core identity within the tested null families.
```

```text
Core-in-envelope behavior remains partly pipeline-generic.
```

Avoid:

```text
BMC-14d proves the core is physically real.
```

```text
BMC-14d proves spacetime emergence.
```

```text
All covariance explanations are excluded.
```

```text
All graph-structure explanations are excluded.
```

```text
The empirical p-like value is a formal p-value proof.
```

---

## 16. Conservative external wording

A suitable research-note paragraph:

> BMC-14d extends the null-model analysis by testing stronger structure-preserving controls. Across 500 replicates each, neither a global covariance-preserving Gaussian feature null, a family-level covariance-preserving feature null, nor a weight-rank edge-rewiring null fully recovered the observed six-edge N=81 reference core. Maximum recovery was 2/6 edges for the global covariance null, 3/6 for the family covariance null, and 2/6 for the weight-rank edge-rewiring null. This strengthens the interpretation that the observed core identity is not explained by simple feature randomization, empirical covariance structure alone, or generic edge-weight rank structure within the tested null families. At the same time, null-generated cores continue to show high self-containment within their own method envelopes, indicating that core-in-envelope containment remains partly generic to the extraction pipeline.

---

## 17. Internal summary

```text
BMC-14:
Schütteln erzeugt nicht unseren Keim.

BMC-14d:
Kovarianz-Rezept und Kantengewicht-Trick erzeugen ihn auch nicht vollständig.

Aber:
Die Maschine erzeugt grundsätzlich gern Keime in Hüllen.
```

Loriot-compatible version:

```text
Der Klunker liegt nicht zufällig wieder im Topf.
Auch das Rezept und die Kantensortierung bauen ihn nicht vollständig nach.
Aber die Küchenmaschine formt grundsätzlich gern Klümpchen.
```

---

## 18. Remaining open controls

BMC-14d is strong, but several controls remain open.

### 18.1 Degree-preserving edge rewiring

The current edge null preserves weight ranks, but not degree structure.

A later block should test:

```text
degree-preserving edge rewiring
degree + weight class preserving rewiring
```

### 18.2 Gaussian copula / rank covariance null

The current covariance null is Gaussian and covariance-based.

A later block may test:

```text
rank-preserving Gaussian copula
empirical marginal distributions
non-Gaussian covariance-preserving synthetic features
```

### 18.3 Noise perturbation

A separate local stability test should evaluate:

```text
small perturbations around observed feature values
```

This would answer a different question:

```text
Does the observed core survive small measurement/model noise?
```

### 18.4 Geometry-proxy diagnostics

Only after the stronger null stack remains stable should the project proceed to geometry-proxy diagnostics:

```text
embedding stress
local dimension proxy
triangle inequality defects
geodesic consistency
component growth
```

---

## 19. Recommended next step

Two reasonable next steps exist.

### Option A: Red-Team review of BMC-14d

Recommended if the project wants external critique before adding more controls.

Prompt focus:

```text
Does BMC-14d sufficiently address the covariance-structure objection?
Is family covariance max 3/6 still a warning?
Is weight-rank rewiring enough, or is degree-preserving rewiring required next?
```

### Option B: BMC-14e degree-preserving / copula structured nulls

Recommended if continuing directly in the control sequence.

Candidate focus:

```text
degree-preserving edge rewiring
Gaussian copula covariance null
noise perturbation
```

---

## 20. File anchors

BMC-14d specification:

```text
docs/BMC14D_COVARIANCE_STRUCTURED_NULL_CONTROLS_SPEC.md
```

BMC-14d config:

```text
data/bmc14d_covariance_structured_null_controls_config.yaml
```

BMC-14d runner:

```text
scripts/run_bmc14d_covariance_structured_null_controls.py
```

BMC-14d outputs:

```text
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_null_replicate_summary.csv
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_null_method_containment_summary.csv
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_null_distribution_summary.csv
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_readout.md
runs/BMC-14d/covariance_structured_null_controls_open/bmc14d_metrics.json
```

This result note:

```text
docs/BMC14D_COVARIANCE_STRUCTURED_NULL_CONTROLS_RESULT_NOTE.md
```

---

## 21. Consolidated status after BMC-14d

### Befund

The observed six-edge N=81 reference core was not fully recovered in any tested BMC-14d structured null replicate. Maximum recovery was 2/6 under global covariance nulls, 3/6 under family covariance nulls, and 2/6 under weight-rank edge rewiring.

### Interpretation

The observed core identity remains robust against the tested stronger null families. Feature covariance and generic edge-weight rank structure alone do not fully explain the observed core identity within these tests.

### Hypothesis

The N=81 observed core may represent a specific relational structure in the current feature-space pipeline, not reducible to simple feature randomization, global/family covariance alone, or weight-rank edge rewiring.

### Open gap

Degree-preserving edge rewiring, rank/copula covariance nulls, noise perturbations, and eventual geometry-proxy diagnostics remain open.
