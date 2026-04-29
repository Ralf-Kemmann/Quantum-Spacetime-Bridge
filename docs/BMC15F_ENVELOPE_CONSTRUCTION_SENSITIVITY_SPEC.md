# BMC-15f Envelope-Construction Sensitivity — Specification

## Purpose

BMC-15f tests whether the BMC-15 geometry-proxy behavior is stable under changes in envelope / backbone construction.

BMC-15e adds explicitly geometry-generated control families.

BMC-15f addresses the complementary concern raised by the red-team review:

```text
Could the observed geometry-proxy behavior be partly induced by the envelope construction method itself?
```

This block is a robustness and sensitivity block.

It is not a new physics-claim block.

It does not test causal structure.

It does not establish physical spacetime emergence.

---

## 1. Scientific question

The central question is:

```text
How stable are the geometry-proxy diagnostics when the envelope/backbone extraction method is varied?
```

More concretely:

```text
Do geometry-proxy metrics remain favorable across multiple envelope constructions,
or do they depend strongly on one specific extraction method or parameter choice?
```

This follows directly from the Louis/Grok red-team concern:

```text
Backbone algorithms may share biases.
Sparse envelope methods may produce visually or numerically geometry-like scaffolds.
Therefore envelope morphology must not be overinterpreted without sensitivity checks.
```

---

## 2. Position in the BMC sequence

```text
BMC-14:
  core identity robustness

BMC-15a:
  observed geometry-proxy baseline

BMC-15b:
  null comparison against graph-rewire and feature-structured nulls

BMC-15d:
  red-team integration and claim boundaries

BMC-15e:
  geometry-control nulls / positive geometry anchors

BMC-15f:
  envelope-construction sensitivity
```

BMC-15f should be read as:

```text
Do the BMC-15 geometry-proxy results survive reasonable changes to how the envelope is constructed?
```

---

## 3. Objects under test

BMC-15f focuses on envelope-level graph objects.

Recommended object families:

```text
maximum_spanning_tree_envelope
mutual_kNN_envelope
threshold_path_consensus_envelope
sparse_path_consensus_envelope
```

Optional baseline:

```text
N81_full_baseline
```

Caution:

```text
top_strength_reference_core is too small and fragmented for standalone geometry interpretation.
It may be included only as a reference anchor, not as an envelope sensitivity object.
```

---

## 4. Envelope-construction variants

### 4.1 Mutual kNN sweep

Working family:

```text
mutual_kNN_k_sweep
```

Candidate parameters:

```text
k = 2, 3, 4, 5, 6
```

Question:

```text
Does embedding compatibility persist as the local-neighborhood envelope thickens or thins?
```

---

### 4.2 Directed or reciprocal neighborhood variants

Working families:

```text
directed_kNN_k_sweep
mutual_kNN_k_sweep
reciprocal_kNN_k_sweep
```

Initial recommendation:

```text
Use mutual_kNN first.
Add directed_kNN only as a graph-construction diagnostic, not as causal evidence.
```

Important:

```text
Directed kNN is not causal direction.
It is only an algorithmic neighbor direction unless separately justified.
```

---

### 4.3 Threshold sweep

Working family:

```text
threshold_sweep
```

Candidate parameters:

```text
top_fraction = 0.02, 0.03, 0.05, 0.08, 0.10
```

or:

```text
weight_quantile = 0.90, 0.92, 0.95, 0.97, 0.98
```

Question:

```text
Does geometry-proxy behavior persist across reasonable sparsity thresholds?
```

---

### 4.4 Path-consensus sweep

Working family:

```text
threshold_path_consensus_sweep
```

Candidate parameters:

```text
path_depth = 2, 3, 4
consensus_threshold = 0.25, 0.50, 0.75
```

Question:

```text
Is the consensus envelope stable, or is geometry-proxy behavior driven by a narrow path-consensus choice?
```

---

### 4.5 Spanning-tree variants

Working families:

```text
maximum_spanning_tree
minimum_distance_spanning_tree
maximum_bottleneck_tree
```

Question:

```text
Does a tree-like sparse skeleton consistently show similar geometry-proxy behavior,
or does the result depend on one spanning construction?
```

Caution:

```text
Tree structures are algorithmically constrained and may have special geometry-proxy behavior.
They should be compared as construction variants, not as independent physical structures.
```

---

## 5. Diagnostics

Use the same geometry-proxy diagnostics as BMC-15a/BMC-15b/BMC-15e where possible:

```text
triangle inequality defects
normalized embedding stress
negative eigenvalue burden
geodesic consistency
local dimension proxy
shell-growth proxies
connectedness
component count
edge count
average degree
degree heterogeneity
```

Additional BMC-15f-specific diagnostics:

```text
metric_stability_across_variants
rank_stability_across_variants
edge_jaccard_between_variants
core_containment_in_variant
variant_family_dispersion
```

---

## 6. Stability summaries

For each graph object / envelope family / metric:

```text
median
IQR
min
max
coefficient of variation where appropriate
rank position
directional label counts
```

For each envelope-construction family:

```text
number of variants generated
number of connected variants
metric dispersion
edge overlap with reference envelope
core containment rate
geometry-proxy stability classification
```

---

## 7. Suggested stability labels

Use defensive labels.

```text
stable_across_variants
moderately_stable_across_variants
parameter_sensitive
method_sensitive
unstable_or_fragmented
not_directional
insufficient_connected_variants
```

Interpretation rules:

```text
stable_across_variants:
  metrics remain in a narrow range and connectedness is preserved

moderately_stable_across_variants:
  metrics vary but qualitative interpretation remains similar

parameter_sensitive:
  metrics change substantially within one method family

method_sensitive:
  metrics differ strongly between envelope-construction families

unstable_or_fragmented:
  graph often disconnects or becomes too sparse for reliable diagnostics
```

---

## 8. Primary outputs

Recommended output directory:

```text
runs/BMC-15f/envelope_construction_sensitivity_open/
```

Recommended files:

```text
summary.json
variant_metrics.csv
family_summary.csv
stability_summary.csv
edge_overlap_summary.csv
core_containment_summary.csv
readout.md
```

Optional diagnostic plots later:

```text
plots/embedding_stress_vs_sparsity.png
plots/edge_overlap_heatmap.png
plots/family_metric_dispersion.png
```

Plots must remain diagnostic.

---

## 9. Main comparison logic

For each envelope-construction family:

```text
1. Generate variants from the same observed relational input.
2. Record construction parameters.
3. Compute graph summary metrics.
4. Compute geometry-proxy diagnostics.
5. Compare each variant to the reference BMC-15 envelope.
6. Compare variation within each family.
7. Compare variation across families.
8. Classify stability.
```

---

## 10. Required safeguards

### 10.1 No causal interpretation

If directed kNN is tested, it must be labeled:

```text
algorithmic directed neighbor relation
```

not:

```text
causal direction
```

### 10.2 No physical geometry claim

Geometry-proxy stability means:

```text
stable under graph construction variants
```

not:

```text
physical geometry confirmed
```

### 10.3 No post-hoc overclaiming

BMC-15f is a post-hoc robustness diagnostic unless a future version is preregistered.

Allowed wording:

```text
post-hoc envelope-construction sensitivity diagnostic
```

Blocked wording:

```text
confirmatory proof of geometry
```

---

## 11. Interpretation rules

### If stable across envelope constructions

Allowed:

```text
The geometry-proxy behavior is not confined to a single envelope-construction choice.
```

Not allowed:

```text
The geometry is real.
```

---

### If parameter-sensitive

Allowed:

```text
The geometry-proxy behavior depends on envelope sparsity or construction parameters.
```

Not allowed:

```text
The signal failed completely.
```

---

### If method-sensitive

Allowed:

```text
The geometry-proxy behavior is partly method-dependent and must be interpreted with caution.
```

Not allowed:

```text
The method is invalid.
```

---

### If unstable / fragmented

Allowed:

```text
Some envelope constructions do not yield graph objects suitable for the current geometry-proxy diagnostics.
```

Not allowed:

```text
The relational structure has no geometry-like content.
```

---

## 12. Risk register

| Risk ID | Risk | Severity | Mitigation |
|---|---|---:|---|
| R1 | Treating envelope stability as physical geometry | High | Strict proxy wording |
| R2 | Directed kNN mistaken for causal direction | High | Explicit algorithmic-direction label |
| R3 | Too many parameter variants causing interpretive noise | Medium | Start with MVP parameter grid |
| R4 | Sparse variants disconnect | Medium | Track connectedness and component count |
| R5 | Core containment overinterpreted | Medium | Treat as structural containment only |
| R6 | Method sensitivity treated as failure | Medium | Frame as informative limitation |
| R7 | Visual plots overstating result | High | Diagnostic plots only |
| R8 | Post-hoc robustness treated as confirmatory | Medium/High | Label as post-hoc diagnostic |
| R9 | Shared input feature structure ignored | Medium | Interpret alongside BMC-15b feature-null result |
| R10 | Single reference envelope chosen too strongly | Medium | Compare to multiple references where possible |

---

## 13. Suggested configuration fields

```text
run_id: string
input_relational_matrix: path
input_node_metadata: path
input_reference_edges: path
output_dir: path
random_seed: integer

reference_objects: list[string]

envelope_families:
  - name: string
    enabled: boolean
    parameters: mapping
    weight_source: string
    construction_mode: string

diagnostics:
  graph_summary: boolean
  triangle_defects: boolean
  embedding_stress: boolean
  negative_eigenvalue_burden: boolean
  geodesic_consistency: boolean
  local_dimension_proxy: boolean
  edge_overlap: boolean
  core_containment: boolean

stability:
  reference_family: string
  metric_tolerance: float
  dispersion_thresholds: mapping
  connectedness_required: boolean

labeling:
  tie_tolerance: float
  directional_metrics: mapping
```

---

## 14. Field list

| Field name | Field type | Description |
|---|---|---|
| `run_id` | string | Stable identifier for the BMC-15f run. |
| `input_relational_matrix` | path/string | Input relational matrix or weighted similarity/distance matrix used to construct envelope variants. |
| `input_node_metadata` | path/string | Optional node metadata used for summaries and family-aware readouts. |
| `input_reference_edges` | path/string | Reference edge list(s) from BMC-15 observed graph objects. |
| `output_dir` | path/string | Output directory for BMC-15f artifacts. |
| `random_seed` | integer | Seed for reproducible stochastic variants if any are used. |
| `reference_objects` | list[string] | Reference observed graph objects used for overlap and containment comparisons. |
| `envelope_families` | list[mapping] | Envelope construction families and parameter grids. |
| `envelope_families.name` | string | Family name, e.g. `mutual_kNN_k_sweep`. |
| `envelope_families.enabled` | boolean | Whether this family is active. |
| `envelope_families.parameters` | mapping | Parameter grid for the construction family. |
| `envelope_families.weight_source` | string | Source of edge weights, e.g. `similarity`, `distance_inverse`, `rank_weight`. |
| `envelope_families.construction_mode` | string | Construction logic, e.g. `mutual`, `directed`, `threshold`, `tree`. |
| `diagnostics` | mapping | Boolean switches for graph and geometry-proxy diagnostics. |
| `stability.reference_family` | string | Reference family for stability comparison. |
| `stability.metric_tolerance` | float | Tolerance for metric equality and stability comparisons. |
| `stability.dispersion_thresholds` | mapping | Thresholds used to classify stable/moderate/sensitive behavior. |
| `stability.connectedness_required` | boolean | Whether disconnected variants are excluded from stability labels. |
| `labeling.tie_tolerance` | float | Numerical tolerance for equality/ties. |
| `labeling.directional_metrics` | mapping | Metric-specific direction of more/less geometry-like interpretation. |

---

## 15. MVP design

The first BMC-15f run should remain small.

Recommended MVP:

```text
reference_objects:
  - maximum_spanning_tree_envelope
  - mutual_kNN_k3_envelope
  - threshold_path_consensus_envelope

envelope_families:
  - mutual_kNN_k_sweep:
      k: [2, 3, 4, 5, 6]

  - threshold_sweep:
      top_fraction: [0.02, 0.03, 0.05, 0.08, 0.10]

  - spanning_tree_variants:
      modes:
        - maximum_spanning_tree
        - minimum_distance_spanning_tree
```

Optional second pass:

```text
threshold_path_consensus_sweep:
  path_depth: [2, 3, 4]
  consensus_threshold: [0.25, 0.50, 0.75]
```

---

## 16. Expected readout structure

The readout should include:

```text
1. Run metadata
2. Input files and reference objects
3. Envelope families and parameter grids
4. Variant generation success / failure counts
5. Connectedness and component counts
6. Geometry-proxy metric summaries
7. Stability classifications
8. Edge overlap / containment summaries
9. Conservative interpretation
10. Open limitations
11. Recommended next step
```

---

## 17. Conservative final claim template

If BMC-15f shows stability:

```text
BMC-15f indicates that selected geometry-proxy diagnostics are not confined to a single
envelope-construction choice. Within the tested parameter ranges, the observed envelope-level
behavior remains qualitatively stable. This supports robustness of the geometry-proxy readout
with respect to the tested construction variants, but does not establish physical geometry,
causal structure, Lorentzian signature, or spacetime emergence.
```

If BMC-15f shows sensitivity:

```text
BMC-15f indicates that selected geometry-proxy diagnostics are sensitive to envelope-construction
choices or sparsity parameters. This does not invalidate the observed BMC-15 behavior, but it
requires that envelope-level geometry-proxy interpretations remain method-qualified.
```

---

## 18. Recommended next action

After this specification:

```text
1. Create data/bmc15f_envelope_construction_sensitivity_config.yaml
2. Create scripts/run_bmc15f_envelope_construction_sensitivity.py
3. Run a small MVP
4. Inspect connectedness, edge overlap, and metric stability
5. Only then expand to path-consensus sweeps or diagnostic plots
```

---

## 19. Final internal sentence

```text
BMC-15f fragt nicht:
Ist der Klunker Raumzeit?

BMC-15f fragt:
Baut die Küchenmaschine immer ähnliche Hüllen,
oder bleibt die geometry-proxy Ordnung auch dann stehen,
wenn wir an den Hüllen-Reglern drehen?
```
