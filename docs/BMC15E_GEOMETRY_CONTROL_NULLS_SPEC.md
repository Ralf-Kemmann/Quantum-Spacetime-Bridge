# BMC-15e Geometry-Control Nulls — Specification

## Purpose

BMC-15e extends the BMC-15 geometry-proxy series by adding explicitly geometry-generated control graph families.

BMC-15b compared the observed relational graph objects against:

```text
graph-rewire nulls
feature-/family-/correlation-structured nulls
```

The main BMC-15b outcome was:

```text
Observed graph objects are more geometry-proxy compatible than graph-rewire nulls,
but feature-/family-/correlation-structured nulls can often produce similar proxy values.
```

BMC-15e asks a different and more diagnostic question:

```text
Where does the observed geometry-proxy behavior sit relative to explicitly geometry-generated graph controls?
```

This is still a geometry-proxy block.

It is not a causal block.

It is not a Lorentzian block.

It does not test spacetime emergence.

---

## 1. Scientific question

The central question is:

```text
Does the observed relational graph behave more like:
  a) graph-rewire nulls,
  b) feature-structured nulls,
  c) explicitly geometry-generated graph controls,
  d) or a distinct mixed case?
```

The aim is not to prove geometry.

The aim is to add a positive / geometric comparison anchor.

---

## 2. Motivation

BMC-15b created a two-sided interpretation:

```text
Against graph-rewire nulls:
  observed appears nontrivial and more embedding-compatible.

Against feature-structured nulls:
  observed is often null-typical.
```

This leaves a missing reference point:

```text
What do explicitly geometry-generated controls look like under the same diagnostics?
```

BMC-15e fills that gap.

Internal image:

```text
Graph-rewire nulls:
  shaken graph gravel

Feature-structured nulls:
  sorted feature/family clumps

Geometry-control nulls:
  intentionally geometric scaffold controls

Observed:
  the Klunker under test
```

---

## 3. Control families

BMC-15e should start with simple, auditable geometry-generated controls.

### 3.1 Random Geometric Graphs

Working name:

```text
random_geometric_graph
```

Basic idea:

```text
Sample points in Euclidean space.
Connect nodes based on geometric proximity or k-nearest-neighbor rule.
Optionally assign weights from distance-based kernels.
```

Candidate dimensions:

```text
d = 2
d = 3
d = 4
```

Candidate matching constraints:

```text
same number of nodes as observed graph object
approximately same edge count
optionally same average degree
optionally same weight distribution by rank mapping
```

Purpose:

```text
Provides an explicitly Euclidean geometry-generated comparison family.
```

---

### 3.2 Hyperbolic Random Graphs

Working name:

```text
hyperbolic_random_graph
```

Basic idea:

```text
Generate graph structures from latent hyperbolic geometry,
typically producing heterogeneous degree structure and clustered geometry-like organization.
```

Candidate matching constraints:

```text
same number of nodes
approximately same edge count
approximately same degree heterogeneity
optionally same weight-rank remapping
```

Purpose:

```text
Provides a geometry-generated comparison family with hierarchical / tree-like / negatively curved tendencies.
```

Implementation note:

```text
If a full hyperbolic random graph generator is too much for the first pass,
BMC-15e may begin with a simple soft radial-angular toy generator and mark it as toy_hyperbolic_control.
```

---

### 3.3 Soft geometric kernel controls

Working name:

```text
soft_geometric_kernel
```

Basic idea:

```text
Sample points in Euclidean space.
Compute pair distances.
Convert distances to weights using a monotone kernel.
Select edges by top weights or threshold.
```

Example kernels:

```text
exp(-d / scale)
exp(-d^2 / scale^2)
1 / (1 + d)
```

Purpose:

```text
Creates weighted geometry-like controls that are closer in spirit to relational similarity matrices.
```

This may be the most natural first geometry-control family for the current QSB pipeline.

---

## 4. Matching strategy

BMC-15e must avoid unfair comparisons.

Each geometry-control graph should be matched to the observed graph object at least by:

```text
node count
edge count
connectedness status where possible
```

Recommended optional matching:

```text
degree distribution approximate matching
weight-rank remapping
same number of envelope extraction steps
same downstream geometry-proxy diagnostics
```

Minimal first-pass matching:

```text
For each observed graph object:
  N_control = N_observed
  E_control = E_observed
  generate controls until connectedness condition is satisfied
  assign weights by geometry kernel or observed weight-rank remapping
```

Important:

```text
Do not tune controls to beat or match the observed graph.
Match coarse graph size/edge constraints only.
```

---

## 5. Graph objects to compare

BMC-15e should not immediately explode the object set.

Recommended first pass:

```text
N81_full_baseline
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
threshold_path_consensus_envelope
```

Optional later:

```text
top_strength_reference_core
```

Caution:

```text
The compact core alone is small and fragmented.
It should not be overinterpreted as a standalone geometry object.
```

---

## 6. Diagnostics

Use the same geometry-proxy diagnostics as BMC-15a/BMC-15b where possible:

```text
triangle inequality defects
normalized embedding stress
negative eigenvalue burden
geodesic consistency
local dimension proxy
shell-growth proxies
```

Add comparison summaries:

```text
observed_vs_graph_rewire
observed_vs_feature_structured
observed_vs_geometry_controls
geometry_control_family_ranking
```

---

## 7. Primary outputs

Recommended output files:

```text
runs/BMC-15e/geometry_control_nulls_open/summary.json
runs/BMC-15e/geometry_control_nulls_open/geometry_control_metrics.csv
runs/BMC-15e/geometry_control_nulls_open/family_summary.csv
runs/BMC-15e/geometry_control_nulls_open/observed_position_summary.csv
runs/BMC-15e/geometry_control_nulls_open/readout.md
```

Optional later:

```text
runs/BMC-15e/geometry_control_nulls_open/plots/
```

But plotting should remain diagnostic, not rhetorical.

---

## 8. Main comparison logic

For each observed graph object and metric:

```text
1. Load observed metric from BMC-15a/BMC-15b outputs.
2. Generate geometry-control replicates.
3. Compute the same metric on each replicate.
4. Compare observed value to geometry-control distribution.
5. Label the relation defensively.
```

Possible labels:

```text
observed_within_geometry_control_range
observed_more_geometry_like_than_geometry_controls
observed_less_geometry_like_than_geometry_controls
observed_geometry_control_equivalent
observed_outside_geometry_control_range
not_directional
```

Important:

```text
Labels must handle ties correctly.
All-zero ties must be labeled as equivalent.
```

---

## 9. Interpretation rules

### If observed is close to geometry controls

Allowed:

```text
The observed graph object falls within the range of explicitly geometry-generated controls
under the tested proxy diagnostics.
```

Not allowed:

```text
The observed graph is geometric.
The observed graph reconstructs physical space.
```

---

### If observed is between graph-rewire and geometry controls

Allowed:

```text
The observed graph object occupies an intermediate diagnostic regime between graph-rewire nulls
and explicitly geometry-generated controls.
```

Not allowed:

```text
The observed graph is becoming spacetime.
```

---

### If observed is closer to feature-structured nulls than geometry controls

Allowed:

```text
The observed geometry-proxy behavior may be more strongly explained by structured feature/family/correlation content
than by simple geometry-generated control families.
```

Not allowed:

```text
The signal failed.
```

---

### If geometry controls do not match observed

Allowed:

```text
The tested simple geometry-control families do not reproduce the observed geometry-proxy profile.
```

Not allowed:

```text
Geometry is excluded.
```

---

## 10. Risk register

| Risk ID | Risk | Severity | Mitigation |
|---|---|---:|---|
| R1 | Geometry controls treated as proof of physical geometry | High | Explicit proxy wording |
| R2 | Controls over-tuned to observed graph | High | Match only coarse constraints |
| R3 | Hyperbolic controls too complex / opaque | Medium | Start with auditable toy generator if needed |
| R4 | Weight assignment changes interpretation | Medium | Compare unweighted and weight-rank-remapped variants |
| R5 | Small core overinterpreted | Medium | Keep core optional / cautionary |
| R6 | Visuals overstate geometry | High | Diagnostic plots only |
| R7 | Post-hoc test treated as confirmatory | Medium/High | Label as post-hoc diagnostic |
| R8 | Geometry-control failure overread as anti-geometry | Medium | Limit conclusion to tested families |

---

## 11. Suggested configuration fields

The BMC-15e config should include at least:

```text
run_id: string
input_observed_metrics: path
input_observed_graphs: path
output_dir: path
random_seed: integer
n_replicates: integer

graph_objects: list[string]

control_families:
  - name: string
    enabled: boolean
    dimensions: list[int]
    matching: mapping
    weight_mode: string
    generator_params: mapping

diagnostics:
  triangle_defects: boolean
  embedding_stress: boolean
  negative_eigenvalue_burden: boolean
  geodesic_consistency: boolean
  local_dimension_proxy: boolean

labeling:
  tie_tolerance: float
  all_zero_tie_label: string
  directional_metrics: mapping
```

---

## 12. Field list

| Field name | Field type | Description |
|---|---|---|
| `run_id` | string | Stable identifier for the BMC-15e run. |
| `input_observed_metrics` | path/string | Path to observed BMC-15 geometry-proxy metrics. |
| `input_observed_graphs` | path/string | Path to observed graph-object definitions or edge lists. |
| `output_dir` | path/string | Output directory for BMC-15e run artifacts. |
| `random_seed` | integer | Seed for reproducible control generation. |
| `n_replicates` | integer | Number of geometry-control replicates per family/object/dimension. |
| `graph_objects` | list[string] | Observed graph objects to compare against geometry controls. |
| `control_families` | list[mapping] | Geometry-control families to generate. |
| `control_families.name` | string | Control family name, e.g. `random_geometric_graph`. |
| `control_families.enabled` | boolean | Whether this control family is active. |
| `control_families.dimensions` | list[integer] | Latent geometry dimensions to test. |
| `control_families.matching` | mapping | Matching constraints such as node count, edge count, connectedness. |
| `control_families.weight_mode` | string | Weight assignment mode, e.g. `distance_kernel`, `observed_rank_remap`, `unweighted`. |
| `control_families.generator_params` | mapping | Family-specific generator parameters. |
| `diagnostics` | mapping | Boolean switches for diagnostics. |
| `labeling.tie_tolerance` | float | Numerical tolerance for equality/ties. |
| `labeling.all_zero_tie_label` | string | Label used when observed and controls are all zero. |
| `labeling.directional_metrics` | mapping | Metric-specific direction of more/less geometry-like interpretation. |

---

## 13. Minimum viable BMC-15e

The first implementation should stay small.

Recommended MVP:

```text
graph_objects:
  - N81_full_baseline
  - maximum_spanning_tree_envelope
  - mutual_kNN_k3_envelope

control_families:
  - soft_geometric_kernel
  - random_geometric_graph

dimensions:
  - 2
  - 3
  - 4

n_replicates:
  200

matching:
  node_count: exact
  edge_count: exact
  connected: prefer_true

weight_modes:
  - unweighted
  - observed_rank_remap
```

Hyperbolic controls can be added after the MVP if the initial implementation is stable.

---

## 14. Expected readout structure

The readout should include:

```text
1. Run metadata
2. Input files
3. Control families generated
4. Matching success rates
5. Geometry-proxy metric summaries
6. Observed position relative to each control family
7. Conservative interpretation
8. Open limitations
9. Recommended next step
```

---

## 15. Conservative final claim template

If BMC-15e works as intended, the strongest allowed claim should look like this:

```text
BMC-15e adds explicitly geometry-generated control families to the BMC-15 comparison layer.
The observed relational graph objects can therefore be positioned not only against graph-rewire
and feature-structured nulls, but also against simple Euclidean or hyperbolic geometry-control families.
This comparison remains a geometry-proxy diagnostic and does not establish physical geometry,
causal structure, Lorentzian signature, or spacetime emergence.
```

---

## 16. Recommended next action

After this specification:

```text
1. Create data/bmc15e_geometry_control_nulls_config.yaml
2. Create scripts/run_bmc15e_geometry_control_nulls.py
3. Run a small MVP
4. Inspect matching rates and metric distributions
5. Only then expand to hyperbolic controls or visualization
```

---

## 17. Final internal sentence

```text
BMC-15e fragt nicht:
Ist der Klunker Raumzeit?

BMC-15e fragt:
Wo liegt der Klunker im Diagnostikraum,
wenn wir ihn nicht nur gegen Schüttel-Nulls,
sondern auch gegen absichtlich geometrische Kontrollgerüste halten?
```
