# BMC-14 Null-Model / Randomized Feature-Control Result Note

## Purpose

BMC-14 tests whether the BMC-13a core-vs-envelope result is data-specific or could arise generically under feature-randomized null controls.

BMC-13/13a showed:

```text
The compact six-edge N=81 top-strength reference core is fully contained
inside all tested alternative backbone constructions.
```

This supported a core-vs-envelope interpretation:

```text
core persists
envelope is method-dependent
```

BMC-14 asks the next skeptical question:

```text
Would the same observed six-edge core also appear in randomized feature-space controls?
```

Internal image:

```text
Wenn wir die Beziehungssuppe schütteln,
entsteht dann wieder derselbe Keim?
```

---

## 1. Reference object

The observed reference object is the BMC-13a six-edge top-strength reference core:

```text
method_id = top_strength_reference
edge_count = 6
edge_count_target = 81
case_id = baseline_all_features
```

This object is treated as the observed N=81 core.

Important:

```text
The observed core is a graph-method diagnostic object,
not a physical spacetime object.
```

---

## 2. Null models

BMC-14 used three feature-randomized null models.

### 2.1 featurewise_permutation

Each feature column was independently permuted across nodes.

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
specific feature-to-node assignment
```

### 2.2 rowwise_vector_permutation

Entire feature vectors were permuted across node IDs.

Preserves:

```text
within-row feature correlations
joint feature vectors
feature marginal distributions
```

Breaks:

```text
which node carries which complete feature vector
```

### 2.3 family_preserving_row_permutation

Feature vectors were permuted only within node families.

Preserves:

```text
node_family structure
within-family feature-vector pool
within-row feature correlations
```

Breaks:

```text
specific node-to-feature assignment inside each family
```

This is the strictest of the three initial null models, because family structure is preserved.

---

## 3. Run setup

BMC-14 used:

```text
replicates per null model = 100
edge_count_target = 81
core_edge_count = 6
```

The runner reconstructed null relational graphs using the same basic feature-space procedure:

```text
standardized features
Euclidean distance
w(i,j) = 1 / (1 + d(i,j))
top N=81 edges
top-strength core of k=6 edges
```

It also evaluated alternative null backbone envelopes:

```text
top_strength_reference
mutual_kNN_k3
maximum_spanning_tree
```

---

## 4. Main result: observed core recovery

BMC-14 measured how many of the observed six reference-core edges reappeared in null-generated top-strength cores.

| null_model_id | mean shared edges | median shared edges | max shared edges | max recovery fraction |
|---|---:|---:|---:|---:|
| featurewise_permutation | 0.17 / 6 | 0 | 2 | 0.333 |
| rowwise_vector_permutation | 0.11 / 6 | 0 | 1 | 0.167 |
| family_preserving_row_permutation | 0.75 / 6 | 1 | 3 | 0.500 |

### Finding

No tested null replicate fully recovered the observed six-edge core.

```text
observed value = 6 / 6
featurewise null max = 2 / 6
rowwise null max = 1 / 6
family-preserving null max = 3 / 6
```

Across the tested 300 total null replicates:

```text
0 / 300 fully recovered the observed six-edge core
```

### Interpretation

The observed N=81 six-edge core identity is not reproduced by the tested feature-randomized null controls.

This supports data-specificity of the observed core within the tested null-model family.

---

## 5. Family-preserving null result

The family-preserving null model produced higher observed-core recovery than the more disruptive nulls.

```text
family_preserving_row_permutation:
mean shared edges = 0.75 / 6
median shared edges = 1 / 6
max shared edges = 3 / 6
max recovery fraction = 0.500
```

This is expected because family-level structure is preserved.

### Interpretation

Family structure carries part of the relational signal.

However:

```text
even the family-preserving null never recovered 6/6 observed core edges
```

Therefore the observed core is not explained simply by preserving node-family membership alone.

---

## 6. Core-in-envelope behavior under nulls

BMC-14 also tested whether null-generated top-strength cores are contained inside their own null backbone envelopes.

This was measured as:

```text
null_core_self_containment
```

The result was high across most null models and methods.

Examples:

```text
rowwise_vector_permutation::maximum_spanning_tree:
  null_core_self_containment = 1.000

rowwise_vector_permutation::mutual_kNN_k3:
  null_core_self_containment = 1.000

family_preserving_row_permutation::maximum_spanning_tree:
  null_core_self_containment = 1.000

family_preserving_row_permutation::mutual_kNN_k3:
  null_core_self_containment = 1.000
```

The top-strength reference trivially has:

```text
null_core_self_containment = 1.000
```

because the null core is itself defined as the top-strength reference core.

### Interpretation

Core-in-envelope containment is at least partly generic to the extraction pipeline.

That is:

```text
if the pipeline generates a top-strength core,
that core often lies inside larger alternative null envelopes
```

Therefore the existence of a core-in-envelope pattern alone is not sufficient evidence of data-specific structure.

---

## 7. Critical distinction

BMC-14 separates two issues:

### 7.1 Specific core identity

Question:

```text
Does the observed six-edge core itself reappear under nulls?
```

Answer:

```text
No full recovery in any tested null replicate.
```

Interpretation:

```text
observed core identity is data-specific under the tested null controls
```

### 7.2 Generic containment form

Question:

```text
Do null cores also sit inside their own larger method envelopes?
```

Answer:

```text
Yes, often.
```

Interpretation:

```text
core-in-envelope containment is partly pipeline-generic
```

This distinction is the main BMC-14 result.

Internal formulation:

```text
Die Suppe klumpt auch im Nullmodell.
Aber sie klumpt nicht zu unserem Keim.
```

---

## 8. Empirical p-like diagnostics

Many BMC-14 distribution rows show:

```text
p_like_upper_tail = 0.009900990099009901
```

This value equals:

```text
1 / (100 + 1)
```

because no null replicate reached or exceeded the observed reference value.

### Interpretation

This may be described as:

```text
empirical p-like diagnostic ≈ 0.01 with 100 replicates
```

but not as:

```text
formal p = 0.01 proof
```

BMC-14 remains an empirical null-comparison diagnostic, not a full statistical proof.

---

## 9. Updated project status after BMC-14

### Previous status after BMC-13a

```text
The N=81 reference core is fully embedded in all tested alternative backbone envelopes.
The broader envelope remains method-dependent.
```

### BMC-14 refinement

```text
The observed reference-core identity is not fully recovered under tested feature-randomized null controls.
However, core-in-envelope behavior is common for null-generated cores.
```

Therefore:

```text
core identity = data-specific within tested nulls
core-in-envelope form = partly pipeline-generic
```

---

## 10. Strongest current interpretation

The strongest current interpretation is:

> BMC-14 supports the data-specificity of the observed N=81 six-edge reference-core identity under the tested feature-randomized null controls. At the same time, high null-core self-containment shows that core-in-envelope containment is partly generic to the extraction pipeline. The result therefore strengthens the observed core identity while preventing overinterpretation of the containment pattern itself.

Short version:

> The specific observed core is not null-typical; the containment motif is partly pipeline-typical.

Internal version:

```text
Unser Keim taucht beim Schütteln nicht wieder auf.
Aber Schütteln erzeugt generell auch Klümpchen in Hüllen.
```

---

## 11. What BMC-14 strengthens

BMC-14 strengthens the claim that:

```text
the exact observed six-edge N=81 core is not a trivial result of the tested feature randomizations
```

It strengthens the sequence:

```text
BMC-12f:
  N=81 is threshold-robust within the tested grid.

BMC-13a:
  the N=81 core is embedded in all tested alternative backbone envelopes.

BMC-14:
  the exact N=81 core is not fully reproduced under tested feature-randomized nulls.
```

---

## 12. What BMC-14 does not prove

BMC-14 does not prove:

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
that all possible null models are excluded
```

It does not prove:

```text
that core-in-envelope containment itself is data-specific
```

because null-generated cores also show high self-containment.

---

## 13. Allowed statements after BMC-14

Allowed:

```text
The observed N=81 six-edge reference core was not fully recovered in any of the tested feature-randomized null controls.
```

```text
The family-preserving null model recovered more of the observed core than the more disruptive null models, but still reached only 3/6 edges at maximum.
```

```text
BMC-14 supports data-specificity of the observed core identity within the tested null-model family.
```

```text
High null-core self-containment suggests that core-in-envelope behavior is partly generic to the extraction pipeline.
```

```text
The current result strengthens the core identity, not the uniqueness of the containment motif itself.
```

Avoid:

```text
BMC-14 proves the core is physically real.
```

```text
BMC-14 proves spacetime emergence.
```

```text
Null models are fully excluded.
```

```text
Core-in-envelope containment is unique to the observed data.
```

```text
p = 0.01 proves significance.
```

---

## 14. Conservative external wording

A suitable paragraph for a research note:

> BMC-14 evaluates the BMC-13a core-vs-envelope finding against feature-randomized null controls. Across 100 replicates each of feature-wise permutation, row-wise feature-vector permutation, and family-preserving row permutation, the observed six-edge N=81 reference core was never fully recovered. The maximum recovery was 2/6 edges for feature-wise permutation, 1/6 for row-wise permutation, and 3/6 for the family-preserving null. This supports data-specificity of the observed core identity within the tested null-model family. At the same time, null-generated top-strength cores were often fully contained inside their own alternative backbone envelopes, indicating that core-in-envelope containment is partly generic to the extraction pipeline. Thus, BMC-14 strengthens the observed reference-core identity while keeping the broader containment motif methodologically bounded.

---

## 15. Internal summary

```text
BMC-12f:
Der N=81-Keim hält bei Schwellenwacklern.

BMC-13a:
Der N=81-Keim liegt in allen getesteten alternativen Hüllen.

BMC-14:
Wenn wir die Features schütteln, entsteht nicht wieder derselbe Keim.

Aber:
Schütteln erzeugt grundsätzlich auch Kerne in Hüllen.

Also:
Unser Keim ist spezifisch.
Das Keim-in-Hülle-Muster ist teilweise pipeline-typisch.
```

Loriot-compatible version:

```text
Die Suppe klumpt immer irgendwie.
Aber der gleiche Klunker liegt nicht zufällig wieder im Topf.
```

---

## 16. Next possible controls

### BMC-14b: increased replicate count

Increase null replicates:

```text
replicates = 500 or 1000
```

Purpose:

```text
Refine empirical null ranks and tails.
```

### BMC-14c: noise perturbation

Add small perturbations to standardized features.

Purpose:

```text
Test local numerical stability of the observed core.
```

### BMC-15: geometry-proxy diagnostics

If the core remains stable across null and perturbation controls, later tests may ask whether the core/envelope structure has geometry-like properties:

```text
embedding stress
local dimension proxy
geodesic consistency
triangle inequality defects
component growth
```

### BMC-14d: stronger structured null

Possible future null models:

```text
degree/weight preserving edge rewiring
family-block preserving null
covariance-preserving synthetic features
```

---

## 17. Recommended next step

The immediate next step should be:

```text
Red-Team review of BMC-13a/BMC-14
```

Prompt focus:

```text
Does BMC-14 properly distinguish observed-core identity from generic core-in-envelope pipeline behavior?
Is the data-specificity claim defensible with 100 replicates?
What null models remain necessary before any stronger claim?
```

---

## 18. File anchors

BMC-14 specification:

```text
docs/BMC14_NULL_MODEL_FEATURE_CONTROL_SPEC.md
```

BMC-14 config:

```text
data/bmc14_null_model_feature_control_config.yaml
```

BMC-14 runner:

```text
scripts/run_bmc14_null_model_feature_control.py
```

BMC-14 outputs:

```text
runs/BMC-14/null_model_feature_control_open/bmc14_null_replicate_summary.csv
runs/BMC-14/null_model_feature_control_open/bmc14_null_method_containment_summary.csv
runs/BMC-14/null_model_feature_control_open/bmc14_null_distribution_summary.csv
runs/BMC-14/null_model_feature_control_open/bmc14_readout.md
runs/BMC-14/null_model_feature_control_open/bmc14_metrics.json
```

---

## 19. Consolidated status after BMC-14

### Befund

The observed six-edge N=81 reference core was not fully recovered in any tested feature-randomized null replicate. Null-generated cores, however, commonly show high self-containment in their own alternative backbone envelopes.

### Interpretation

The observed core identity appears data-specific within the tested null-model family, while the core-in-envelope containment motif is partly generic to the extraction pipeline.

### Hypothesis

The N=81 observed core may represent a specific relational structure in the current feature-space graph pipeline.

### Open gap

More nulls, more replicates, noise perturbations, and eventually geometry-proxy diagnostics are needed before stronger structural or physics-facing claims are possible.
