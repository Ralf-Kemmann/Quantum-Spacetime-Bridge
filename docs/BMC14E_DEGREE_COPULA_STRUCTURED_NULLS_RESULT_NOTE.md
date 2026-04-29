# BMC-14e Degree-Preserving / Copula Structured Nulls Result Note

## Purpose

BMC-14e continues the BMC-14 null-control sequence after BMC-14d.

BMC-14d showed that the observed six-edge N=81 reference core was not fully recovered under:

```text
global_covariance_gaussian
family_covariance_gaussian
weight_rank_edge_rewire
```

The remaining methodological objections were:

```text
1. The observed core might be explainable by degree / hub structure.
2. The observed core might be explainable by degree plus coarse edge-strength organization.
3. The observed core might be explainable by rank/correlation feature structure not captured by Gaussian covariance nulls.
```

BMC-14e tests these objections.

Internal image:

```text
Der Klunker liegt nicht zufällig wieder im Topf.
Rezept und Kantensortierung reichen nicht.
Nun prüfen wir, ob die Topfform oder die Zutaten-Rangordnung den Klunker erzwingt.
```

---

## 1. Reference object

The reference object remains the observed BMC-13a six-edge N=81 top-strength core:

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

This is a graph-method diagnostic object.

It is not a physical spacetime object.

---

## 2. BMC-14e null models

BMC-14e used three null controls.

### 2.1 degree_preserving_edge_rewire

This null starts from the observed N=81 graph and rewires edges by degree-preserving double-edge swaps.

Preserves:

```text
node set
edge count
degree sequence
edge weight multiset
```

Tests:

```text
Can degree / hub structure plus observed edge weights reproduce the observed core?
```

### 2.2 degree_weightclass_edge_rewire

This null also preserves degree structure while retaining coarse edge-weight-class organization.

Preserves:

```text
node set
edge count
degree sequence
edge weight distribution
coarse weight-class organization
```

Tests:

```text
Can hub structure plus coarse edge-strength organization reproduce the observed core?
```

### 2.3 gaussian_copula_feature_null

This null generates synthetic features using empirical marginal distributions and rank-like correlation structure via a Gaussian copula.

Preserves approximately:

```text
empirical feature marginals
rank-correlation structure
node count
feature dimensionality
```

Tests:

```text
Can empirical marginals plus rank-correlation structure reproduce the observed core?
```

---

## 3. Run setup

BMC-14e used:

```text
replicates per null model = 500
edge_count_target = 81
core_edge_count = 6
```

Total BMC-14e null replicates:

```text
1500
```

---

## 4. Main result: observed core recovery

BMC-14e measured how many of the observed six reference-core edges appeared in each null-generated top-strength core.

| null_model_id | null_family | mean shared edges | median shared edges | q95 shared edges | max shared edges | max recovery fraction |
|---|---|---:|---:|---:|---:|---:|
| degree_preserving_edge_rewire | degree_structured | 0.162 / 6 | 0 | 1 | 2 | 0.333 |
| degree_weightclass_edge_rewire | degree_structured | 0.144 / 6 | 0 | 1 | 2 | 0.333 |
| gaussian_copula_feature_null | copula_feature | 0.132 / 6 | 0 | 1 | 2 | 0.333 |

### Finding

No BMC-14e null model fully recovered the observed six-edge core.

```text
observed value = 6 / 6

degree_preserving_edge_rewire max = 2 / 6
degree_weightclass_edge_rewire max = 2 / 6
gaussian_copula_feature_null max = 2 / 6
```

Across BMC-14e:

```text
0 / 1500 tested null replicates fully recovered the observed six-edge core
```

---

## 5. Empirical p-like diagnostics

For the primary observed-core metrics, BMC-14e produced:

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

BMC-14e remains an empirical structured-null diagnostic.

---

## 6. Rewire diagnostics

The degree-structured nulls were checked for formal rewire quality.

### degree_preserving_edge_rewire

```text
n = 500
degree_sequence_preserved = 500 / 500
edge_count_preserved = 500 / 500
warnings = 0
swap_success_fraction mean approx. 0.296
swap_success_fraction min approx. 0.280
swap_success_fraction max approx. 0.316
```

### degree_weightclass_edge_rewire

```text
n = 500
degree_sequence_preserved = 500 / 500
edge_count_preserved = 500 / 500
warnings = 0
swap_success_fraction mean approx. 0.295
swap_success_fraction min approx. 0.275
swap_success_fraction max approx. 0.318
```

### Interpretation

The degree-preserving rewiring controls preserved the intended degree sequence and edge count in all tested rewire replicates.

Therefore, the low observed-core recovery under these nulls is not explained by failed rewiring.

---

## 7. Interpretation of degree_preserving_edge_rewire

The degree-preserving null produced:

```text
mean shared edges = 0.162 / 6
median shared edges = 0 / 6
q95 shared edges = 1 / 6
max shared edges = 2 / 6
```

### Interpretation

Degree / hub structure plus the observed edge-weight distribution did not reproduce the full observed six-edge core.

Allowed:

```text
The observed core was not fully recovered under degree-preserving edge rewiring.
```

Avoid:

```text
Degree structure has no role.
```

The result means degree structure alone, as tested here, does not explain the complete core identity.

---

## 8. Interpretation of degree_weightclass_edge_rewire

The degree-plus-weightclass null produced:

```text
mean shared edges = 0.144 / 6
median shared edges = 0 / 6
q95 shared edges = 1 / 6
max shared edges = 2 / 6
```

### Interpretation

Degree structure plus coarse edge-strength organization did not reproduce the observed six-edge core.

Allowed:

```text
The observed core was not fully recovered under degree-plus-weightclass rewiring.
```

Avoid:

```text
Weight organization has no role.
```

The result means this structured graph null does not fully explain the observed core identity.

---

## 9. Interpretation of gaussian_copula_feature_null

The Gaussian copula feature null produced:

```text
mean shared edges = 0.132 / 6
median shared edges = 0 / 6
q95 shared edges = 1 / 6
max shared edges = 2 / 6
```

### Interpretation

Empirical feature marginals plus rank-like correlation structure did not reproduce the full observed core.

This extends BMC-14d:

```text
global covariance null did not recover the core
Gaussian copula / rank-correlation null also did not recover the core
```

Allowed:

```text
The observed core was not fully recovered under the Gaussian copula feature null.
```

Avoid:

```text
Feature rank correlations have no role.
```

The result means rank-correlation structure alone, as tested here, does not explain the complete six-edge core.

---

## 10. Envelope containment under BMC-14e nulls

As in earlier BMC-14 blocks, null-generated cores often show high self-containment inside their own null method envelopes.

Examples:

```text
degree_preserving_edge_rewire::maximum_spanning_tree:
  null_core_self_containment mean = 0.997

degree_weightclass_edge_rewire::mutual_kNN_k3:
  null_core_self_containment mean = 0.996

gaussian_copula_feature_null::mutual_kNN_k3:
  null_core_self_containment mean = 0.997
```

### Interpretation

Core-in-envelope containment remains partly pipeline-generic.

BMC-14e strengthens the observed core identity, not the uniqueness of the containment motif.

Internal formulation:

```text
Die Maschine baut grundsätzlich gern Keime in Hüllen.
Aber sie baut nicht unseren konkreten Keim nach.
```

---

## 11. Updated status after BMC-14e

### Before BMC-14e

BMC-14-series consolidation showed:

```text
0 / 1800 tested null replicates fully recovered the observed core.
```

BMC-14d had already constrained:

```text
simple feature randomization
global covariance
family covariance
weight-rank edge rewiring
```

### After BMC-14e

BMC-14e adds:

```text
degree-preserving edge rewiring
degree + weightclass edge rewiring
Gaussian copula feature null
```

and shows:

```text
0 / 1500 tested BMC-14e null replicates fully recovered the observed core.
```

Combined BMC-14-series status:

```text
0 / 3300 tested null replicates fully recovered the observed six-edge N=81 core.
```

Maximum recovery remains:

```text
3 / 6 observed core edges
```

from earlier family-preserving / family-covariance nulls.

---

## 12. Strongest current interpretation

The strongest current interpretation is:

> BMC-14e further constrains null explanations by showing that the observed N=81 six-edge reference core is not fully recovered under degree-preserving edge rewiring, degree/weight-class rewiring, or Gaussian-copula feature nulls. Together with BMC-14 and BMC-14d, this supports the data-specificity of the observed core identity within the tested null families. Core-in-envelope containment remains partly generic to the extraction pipeline.

Short version:

```text
Degree / hub structure does not fully explain the core.
Degree plus weightclass structure does not fully explain the core.
Rank-correlation feature structure does not fully explain the core.
```

Internal version:

```text
Weder Schütteln,
noch Kovarianz-Rezept,
noch Kantengewicht,
noch Hub-/Gradstruktur,
noch Rang-Korrelation
baut unseren Klunker vollständig nach.
```

---

## 13. What BMC-14e strengthens

BMC-14e strengthens the robustness chain:

```text
BMC-12f:
  N=81 is threshold/gap robust within the tested grid.

BMC-13a:
  The N=81 core is embedded in tested alternative backbone envelopes.

BMC-14:
  The observed core is not recovered by simple feature-randomized nulls.

BMC-14d:
  The observed core is not recovered by covariance-preserving or weight-rank structured nulls.

BMC-14e:
  The observed core is not recovered by degree-preserving or copula/rank-correlation structured nulls.
```

This yields the current diagnostic chain:

```text
threshold-stable
method-crossing embedded
feature-null resistant
covariance-null resistant
weight-rank-null resistant
degree-null resistant
copula/rank-correlation-null resistant
```

within the tested scope.

---

## 14. What BMC-14e does not prove

BMC-14e does not prove:

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

## 15. Allowed statements after BMC-14e

Allowed:

```text
The observed N=81 six-edge core was not fully recovered in any tested BMC-14e null replicate.
```

```text
Degree-preserving edge rewiring preserved degree sequence and edge count in all tested rewire replicates, but did not reconstruct the full observed core.
```

```text
The Gaussian copula feature null did not reproduce the full observed core.
```

```text
BMC-14e further supports data-specificity of the observed core identity within the tested null families.
```

```text
Core-in-envelope behavior remains partly pipeline-generic.
```

Avoid:

```text
BMC-14e proves the core is physically real.
```

```text
BMC-14e proves spacetime emergence.
```

```text
All degree or graph-structure explanations are excluded.
```

```text
All rank-correlation explanations are excluded.
```

```text
The empirical p-like value is a formal p-value proof.
```

---

## 16. Conservative external wording

A suitable research-note paragraph:

> BMC-14e extends the structured-null analysis by testing degree-preserving edge rewiring, degree/weight-class rewiring, and a Gaussian-copula feature null. Across 500 replicates per null model, the observed six-edge N=81 reference core was never fully recovered. Maximum recovery was 2/6 observed core edges for all three BMC-14e null models. The degree-preserving rewires preserved both edge count and degree sequence in all tested replicates, with no warnings. These results further constrain hub/degree, coarse edge-strength, and rank-correlation explanations of the observed core identity within the tested null families. As in previous controls, null-generated cores still showed high containment within their own alternative method envelopes, indicating that the containment motif remains partly generic to the extraction pipeline.

---

## 17. Internal summary

```text
BMC-14d:
Kovarianz-Rezept und Kantengewicht-Trick bauen unseren Keim nicht vollständig nach.

BMC-14e:
Hub-/Gradstruktur und Rang-Korrelation bauen ihn auch nicht vollständig nach.

Aber:
Die Maschine baut grundsätzlich gern Kerne in Hüllen.
```

Loriot-compatible version:

```text
Der Klunker liegt nicht zufällig wieder im Topf.
Rezept, Kantensortierung, Topfform und Zutaten-Rangordnung reichen nicht.
Aber die Küchenmaschine formt grundsätzlich gern Klümpchen.
```

---

## 18. Remaining open controls

BMC-14e is strong, but some controls remain open.

### 18.1 Noise perturbation

A later BMC-14f should test local numerical stability:

```text
small feature perturbations
edge-rank stability
core survival probability
```

This asks:

```text
Does the observed core survive small perturbations around the observed data?
```

### 18.2 Family copula null

A possible future extension:

```text
family_gaussian_copula_feature_null
```

This would test family-specific marginal/rank structures more directly, but may be sample-size limited.

### 18.3 More aggressive graph nulls

Possible future graph nulls:

```text
degree + clustering preserving rewiring
degree + community/block preserving rewiring
strength-preserving weighted nulls
```

### 18.4 Geometry-proxy diagnostics

Only after the null stack is considered sufficiently constrained:

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

### Option A: BMC-14f Noise Perturbation

This tests local stability rather than new null families.

Recommended if continuing the BMC-14 control sequence.

### Option B: BMC-14 Series 2 Consolidated Robustness Note

This updates the previous BMC-14 consolidated note to include BMC-14e.

Recommended before moving to BMC-15.

### Option C: Short Red-Team review of BMC-14d/e

Recommended if the project wants an external check before geometry-proxy diagnostics.

---

## 20. File anchors

BMC-14e specification:

```text
docs/BMC14E_DEGREE_COPULA_STRUCTURED_NULLS_SPEC.md
```

BMC-14e config:

```text
data/bmc14e_degree_copula_structured_nulls_config.yaml
```

BMC-14e runner:

```text
scripts/run_bmc14e_degree_copula_structured_nulls.py
```

BMC-14e outputs:

```text
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_null_replicate_summary.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_null_method_containment_summary.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_null_distribution_summary.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_rewire_diagnostics.csv
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_readout.md
runs/BMC-14e/degree_copula_structured_nulls_open/bmc14e_metrics.json
```

This result note:

```text
docs/BMC14E_DEGREE_COPULA_STRUCTURED_NULLS_RESULT_NOTE.md
```

---

## 21. Consolidated status after BMC-14e

### Befund

The observed six-edge N=81 reference core was not fully recovered in any tested BMC-14e null replicate. Maximum recovery was 2/6 observed core edges across degree-preserving rewiring, degree/weightclass rewiring, and Gaussian copula feature nulls. Degree-structured rewires preserved edge count and degree sequence in all tested replicates.

### Interpretation

Degree/hub structure, degree plus coarse edge-strength organization, and Gaussian-copula rank-correlation feature structure do not fully explain the observed core identity within the tested null families.

### Hypothesis

The N=81 observed core may represent a specific relational structure in the current feature-space graph pipeline, not reducible to the tested feature-randomized, covariance-preserving, edge-rank, degree-structured, or copula/rank-correlation null mechanisms.

### Open gap

Noise perturbation, possible family-copula nulls, more aggressive graph nulls, and eventual geometry-proxy diagnostics remain open.
