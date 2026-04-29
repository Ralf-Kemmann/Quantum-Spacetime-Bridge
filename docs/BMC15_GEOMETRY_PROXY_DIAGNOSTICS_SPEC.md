# BMC-15 Geometry-Proxy Diagnostics Specification

## Purpose

BMC-15 starts the next diagnostic layer after the BMC-14 null-control series.

The BMC-14 series established the current methodological status:

```text
BMC-12f:
  N=81 is threshold/gap robust within the tested grid.

BMC-13a:
  The six-edge N=81 reference core is embedded in tested alternative backbone envelopes.

BMC-14:
  The observed core is not fully recovered by simple feature-randomized nulls.

BMC-14d:
  The observed core is not fully recovered by covariance-preserving or weight-rank structured nulls.

BMC-14e:
  The observed core is not fully recovered by degree-preserving, degree/weightclass, or Gaussian-copula nulls.
```

The BMC-14 series therefore supports:

```text
The observed N=81 six-edge core identity is robust against the tested null families.
```

However, this does not yet answer whether the robust relational structure has any geometry-like internal organization.

BMC-15 asks the next question:

```text
Does the robust N=81 core/envelope structure exhibit geometry-like proxy behavior?
```

Internal image:

```text
Ist der Klunker nur hart,
oder hat er schon eine innere Kristallordnung?
```

---

## 1. Scope and non-scope

### In scope

BMC-15 tests graph- and distance-based geometry proxies:

```text
triangle inequality defects
embedding stress
local shell growth
shortest-path vs direct-distance consistency
local dimension proxy
core-to-envelope growth behavior
```

### Not in scope

BMC-15 does not establish:

```text
physical spacetime emergence
causal structure
continuum geometry
metric tensor reconstruction
Einstein geometry
quantum gravity
```

BMC-15 is a methodological geometry-proxy diagnostic.

Safe wording:

```text
geometry-like relational consistency
```

Avoid:

```text
physical spacetime proof
```

---

## 2. Working question

Formal question:

```text
Does the robust N=81 relational core and its associated backbone envelopes show
metric-like, embeddable, or dimension-like proxy behavior beyond mere graph stability?
```

Internal question:

```text
Ist der stabile Keim nur ein graphischer Klumpen,
oder zeigt er erste Anzeichen einer geordneten inneren Struktur?
```

---

## 3. Reference objects

BMC-15 should evaluate several related objects.

### 3.1 Observed N=81 graph

Input:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_edges_inventory.csv
```

Filter:

```text
edge_count_target = 81
case_id = baseline_all_features
```

### 3.2 Observed six-edge reference core

Input:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13_backbone_edges.csv
```

Filter:

```text
method_id = top_strength_reference
```

### 3.3 Alternative backbone envelopes

Input:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13_backbone_edges.csv
```

Methods:

```text
top_strength_reference
maximum_spanning_tree
mutual_kNN_k3
threshold_path_consensus_min3
```

### 3.4 Optional null comparison

BMC-15 may optionally compare observed proxy values against existing null outputs from:

```text
BMC-14
BMC-14d
BMC-14e
```

However, BMC-15a should first establish the observed geometry-proxy baseline.

---

## 4. Distance convention

The observed graph uses edge weights:

```text
w(i,j)
```

A distance-like quantity should be derived from weights.

Recommended primary convention:

```text
d(i,j) = -log(w(i,j))
```

Fallback convention:

```text
d(i,j) = 1 / w(i,j) - 1
```

Rationale:

```text
If weights resemble similarity or relational closeness,
then stronger weights should map to shorter distances.
```

Primary BMC-15a should use:

```text
d = -log(w)
```

with safeguards:

```text
w must be positive
clip w to a small epsilon if needed
```

Important:

```text
This is a proxy distance, not a physical distance.
```

---

## 5. Graph objects to analyze

For each selected method graph, BMC-15 should compute proxy diagnostics.

Recommended graph objects:

```text
N81_full_baseline
top_strength_reference_core
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
threshold_path_consensus_envelope
```

### 5.1 N81_full_baseline

All 81 baseline edges.

Purpose:

```text
reference relational neighborhood
```

### 5.2 top_strength_reference_core

Six-edge compact core.

Purpose:

```text
hard reference seed
```

### 5.3 maximum_spanning_tree_envelope

Global connected high-weight skeleton.

Purpose:

```text
minimal connected load-bearing scaffold
```

### 5.4 mutual_kNN_k3_envelope

Local reciprocal-neighborhood envelope.

Purpose:

```text
local mutual support structure
```

### 5.5 threshold_path_consensus_envelope

Sparse-path persistence envelope.

Purpose:

```text
broader sparse-path consensus structure
```

---

# Part A: Triangle inequality defects

## 6. Triangle inequality defect diagnostic

For a set of nodes and distance proxy d(i,j), test triplets:

```text
d(i,j) <= d(i,k) + d(k,j)
```

A violation occurs if:

```text
d(i,j) - d(i,k) - d(k,j) > tolerance
```

Recommended tolerance:

```text
tolerance = 1e-12
```

Metrics:

```text
triangle_count
valid_triangle_count
violation_count
violation_fraction
mean_violation
max_violation
mean_relative_violation
max_relative_violation
```

Interpretation:

```text
low violation_fraction:
  more metric-like

high violation_fraction:
  less metric-like
```

Caution:

```text
Triangle consistency alone does not establish physical geometry.
```

---

## 7. Direct vs graph-completed distance

Many method graphs are sparse. Triangle tests can be performed in two modes.

### 7.1 Edge-only triangle mode

Only triplets with all three pairwise edges present are tested.

Pros:

```text
directly uses observed edges
```

Cons:

```text
few triangles in sparse graphs
```

### 7.2 Shortest-path completed mode

Use graph shortest-path distances to complete missing pairwise distances.

Pros:

```text
tests graph geodesic consistency
```

Cons:

```text
partly tests graph topology, not direct relational distances
```

Recommendation:

```text
BMC-15a should report both modes where possible.
```

---

# Part B: Embedding stress

## 8. Embedding stress diagnostic

Question:

```text
Can the proxy distances be embedded into low-dimensional Euclidean space
with limited distortion?
```

Candidate dimensions:

```text
2D
3D
4D
```

Recommended first implementation:

```text
classical MDS-style embedding from distance matrix
```

or if dependencies are limited:

```text
use eigen-decomposition of double-centered distance matrix
```

Metrics:

```text
embedding_dimension
node_count
stress_raw
stress_normalized
variance_explained_positive_eigenvalues
negative_eigenvalue_fraction
negative_eigenvalue_magnitude
```

Normalized stress:

```text
stress = sqrt(sum((D_ij - Dhat_ij)^2) / sum(D_ij^2))
```

Interpretation:

```text
lower stress:
  more embeddable / geometry-like

higher stress:
  less compatible with low-dimensional Euclidean embedding
```

Caution:

```text
Low-dimensional embeddability is not physical spacetime.
```

---

## 9. Euclidean signature diagnostic

Classical MDS yields eigenvalues.

If many large negative eigenvalues appear, the distance matrix is less Euclidean-like.

Metrics:

```text
positive_eigenvalue_count
negative_eigenvalue_count
negative_eigenvalue_fraction
negative_eigenvalue_sum_abs
positive_eigenvalue_sum
negative_to_positive_abs_ratio
```

Interpretation:

```text
small negative_to_positive_abs_ratio:
  more Euclidean-like

large negative_to_positive_abs_ratio:
  less Euclidean-like or non-Euclidean / noisy proxy structure
```

Caution:

```text
Non-Euclidean behavior is not necessarily bad;
it may indicate graph, hyperbolic, or non-metric relational structure.
```

---

# Part C: Shortest-path vs direct-distance consistency

## 10. Geodesic consistency diagnostic

For pairs with direct edges and available graph paths:

```text
d_direct(i,j)
d_path(i,j) = shortest path distance in graph
```

Compute:

```text
path_direct_ratio = d_path / d_direct
path_minus_direct = d_path - d_direct
```

Because shortest paths can equal direct edge distances if the direct edge is part of the graph, this is most useful when computed on envelopes and compared to the full N81 baseline direct distances.

Recommended comparison:

```text
direct distance from N81_full_baseline
path distance on method envelope
```

Metrics:

```text
pair_count
mean_path_direct_ratio
median_path_direct_ratio
max_path_direct_ratio
mean_path_minus_direct
max_path_minus_direct
unreachable_pair_fraction
```

Interpretation:

```text
low ratios:
  envelope preserves relational closeness well

high ratios or many unreachable pairs:
  envelope loses direct relational consistency
```

---

# Part D: Shell growth from core

## 11. Core-to-envelope shell growth

Use the top-strength reference core as seed.

Seed nodes:

```text
all nodes appearing in top_strength_reference
```

Then analyze expansion into each envelope graph by graph distance in hops:

```text
shell_0 = core nodes
shell_1 = nodes one edge away
shell_2 = nodes two edges away
...
```

Metrics:

```text
graph_id
shell_index
new_nodes
cumulative_nodes
new_edges_crossing_shell
cumulative_edges
component_count_within_shell
largest_component_size_within_shell
```

Interpretation:

```text
smooth shell growth:
  more ordered envelope expansion

fragmented or abrupt growth:
  less ordered / more method-dependent envelope expansion
```

Internal image:

```text
Wächst vom Keim eine geordnete Hülle,
oder springt die Struktur chaotisch?
```

---

# Part E: Local dimension proxy

## 12. Local dimension proxy

Use shell or radius growth.

Possible relation:

```text
N(r) ~ r^d
```

Estimate:

```text
d_eff = slope(log N(r), log r)
```

where:

```text
N(r) = number of nodes within radius r
```

Radius may be:

```text
hop distance
weighted shortest-path distance
```

Recommended BMC-15a implementation:

```text
hop-shell dimension proxy
weighted-shell dimension proxy optional
```

Metrics:

```text
graph_id
center_mode
radius_type
fit_points
effective_dimension_proxy
fit_r2
```

Interpretation:

```text
stable finite slope:
  dimension-like growth proxy

unstable slope:
  no clear dimension-like shell growth
```

Caution:

```text
This is not a measurement of physical dimension.
```

---

## 13. Center choices

Potential centers:

```text
core_node_set
highest_strength_node
all core nodes averaged
```

Recommendation:

```text
BMC-15a should use core_node_set as primary center.
```

Core-node-set distance:

```text
distance from a node to the closest core node
```

---

# Part F: Null comparison policy

## 14. Initial BMC-15a should be observed-only

BMC-15a should first establish observed geometry-proxy summaries.

Reason:

```text
The proxy definitions should be validated before comparing against null distributions.
```

### BMC-15b

A later BMC-15b can run the same geometry-proxy diagnostics on null-generated graphs from:

```text
BMC-14
BMC-14d
BMC-14e
```

or newly generated null ensembles.

Recommended sequence:

```text
BMC-15a observed geometry-proxy baseline
BMC-15b geometry-proxy null comparison
```

---

## 15. Expected output files

BMC-15a should write:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_graph_inventory.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_triangle_defect_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_embedding_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_geodesic_consistency_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_shell_growth_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_local_dimension_proxy_summary.csv
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_readout.md
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_metrics.json
```

Optional figures:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/figures/
```

Suggested figures:

```text
core_vs_envelope_layout_2d.png
embedding_stress_by_graph.png
shell_growth_by_graph.png
```

Figures should be clearly labeled as visualization / proxy diagnostics, not physical geometry.

---

## 16. Field list: bmc15_graph_inventory.csv

| field | type | description |
|---|---|---|
| graph_id | string | Analyzed graph object ID |
| source | string | Input source file |
| method_id | string | Backbone method or graph source |
| edge_count | integer | Number of edges |
| node_count | integer | Number of nodes |
| component_count | integer | Number of connected components |
| largest_component_size | integer | Size of largest component |
| mean_weight | float | Mean edge weight |
| min_weight | float | Minimum edge weight |
| max_weight | float | Maximum edge weight |
| mean_proxy_distance | float | Mean -log(weight) distance |
| min_proxy_distance | float | Minimum proxy distance |
| max_proxy_distance | float | Maximum proxy distance |

---

## 17. Field list: bmc15_triangle_defect_summary.csv

| field | type | description |
|---|---|---|
| graph_id | string | Analyzed graph object ID |
| triangle_mode | string | edge_only or shortest_path_completed |
| node_count | integer | Number of nodes considered |
| triangle_count | integer | Number of tested triangles |
| violation_count | integer | Number of triangle inequality violations |
| violation_fraction | float | violation_count / triangle_count |
| mean_violation | float | Mean positive violation magnitude |
| max_violation | float | Maximum violation magnitude |
| mean_relative_violation | float | Mean relative positive violation |
| max_relative_violation | float | Maximum relative positive violation |

---

## 18. Field list: bmc15_embedding_summary.csv

| field | type | description |
|---|---|---|
| graph_id | string | Analyzed graph object ID |
| distance_mode | string | direct_or_shortest_path |
| embedding_dimension | integer | Embedding dimension |
| node_count | integer | Number of nodes embedded |
| stress_raw | float | Raw embedding stress |
| stress_normalized | float | Normalized embedding stress |
| positive_eigenvalue_count | integer | Count of positive eigenvalues |
| negative_eigenvalue_count | integer | Count of negative eigenvalues |
| negative_eigenvalue_fraction | float | Fraction of negative eigenvalues |
| positive_eigenvalue_sum | float | Sum of positive eigenvalues |
| negative_eigenvalue_abs_sum | float | Sum of absolute negative eigenvalues |
| negative_to_positive_abs_ratio | float | negative_eigenvalue_abs_sum / positive_eigenvalue_sum |

---

## 19. Field list: bmc15_geodesic_consistency_summary.csv

| field | type | description |
|---|---|---|
| graph_id | string | Envelope graph ID |
| direct_reference_graph_id | string | Graph used for direct distances |
| pair_count | integer | Number of comparable node pairs |
| reachable_pair_count | integer | Number of pairs reachable in envelope |
| unreachable_pair_count | integer | Number of pairs not reachable in envelope |
| unreachable_pair_fraction | float | unreachable_pair_count / pair_count |
| mean_path_direct_ratio | float | Mean shortest-path/direct-distance ratio |
| median_path_direct_ratio | float | Median shortest-path/direct-distance ratio |
| max_path_direct_ratio | float | Maximum shortest-path/direct-distance ratio |
| mean_path_minus_direct | float | Mean path minus direct distance |
| max_path_minus_direct | float | Maximum path minus direct distance |

---

## 20. Field list: bmc15_shell_growth_summary.csv

| field | type | description |
|---|---|---|
| graph_id | string | Analyzed graph object ID |
| center_mode | string | core_node_set or other center mode |
| shell_index | integer | Hop shell index |
| new_nodes | integer | Nodes first reached at this shell |
| cumulative_nodes | integer | Nodes reached up to this shell |
| new_edges_crossing_shell | integer | Edges connecting previous shell to new shell |
| cumulative_edges_induced | integer | Edges induced by cumulative node set |
| component_count_induced | integer | Components in induced cumulative subgraph |
| largest_component_size_induced | integer | Largest induced component size |

---

## 21. Field list: bmc15_local_dimension_proxy_summary.csv

| field | type | description |
|---|---|---|
| graph_id | string | Analyzed graph object ID |
| center_mode | string | Center definition |
| radius_type | string | hop or weighted |
| fit_points | integer | Number of shell/radius points used |
| effective_dimension_proxy | float | Slope of log cumulative nodes vs log radius |
| fit_r2 | float | Coefficient of determination |
| interpretation_label | string | stable_proxy, weak_proxy, insufficient_points |

---

## 22. Interpretation logic

### Geometry-like support

BMC-15a may support geometry-like relational consistency if:

```text
triangle violation fractions are low
embedding stress is moderate/low
negative eigenvalue burden is not dominant
shell growth is ordered
local dimension proxy is stable enough to report
geodesic consistency is not severely distorted
```

### Weak geometry-like support

If results are mixed:

```text
some graphs embed well
others fragment
shell growth is method-dependent
triangle defects are moderate
```

then interpretation should emphasize:

```text
partial geometry-like proxy behavior
method-dependent envelope geometry
```

### Negative or non-geometry result

If:

```text
high triangle defects
high embedding stress
large negative eigenvalue burden
fragmented shell growth
unstable dimension proxy
```

then interpretation should be:

```text
The robust core is graph-methodologically stable but does not yet show strong geometry-like proxy consistency.
```

This would not invalidate the previous BMC chain.

It would simply mean:

```text
robust core identity does not automatically imply geometry-like order
```

---

## 23. Allowed statements after BMC-15a

Depending on result:

### If geometry proxies are favorable

Allowed:

```text
The robust N=81 core/envelope structure exhibits geometry-like proxy consistency under the tested diagnostics.
```

```text
This supports further study of geometry reconstruction proxies.
```

Avoid:

```text
The structure is physical spacetime.
```

### If geometry proxies are mixed

Allowed:

```text
The geometry-proxy diagnostics are mixed and method-dependent.
```

```text
The core remains robust, but geometry-like interpretation remains open.
```

### If geometry proxies are weak

Allowed:

```text
The robust core does not yet show strong geometry-like proxy consistency.
```

```text
The result narrows the interpretation to graph-method robustness rather than geometry reconstruction.
```

Avoid:

```text
The project failed.
```

---

## 24. Conservative external wording template

> BMC-15 evaluates whether the robust N=81 core/envelope structure exhibits geometry-like proxy behavior. The diagnostics include triangle-inequality defects, low-dimensional embedding stress, shortest-path versus direct-distance consistency, shell growth from the core, and local dimension proxies. These quantities are interpreted as methodological geometry proxies only. They do not establish physical spacetime emergence or continuum geometry, but they test whether the robust relational structure has internal organization compatible with a geometric reading.

---

## 25. Recommended implementation

Suggested files:

```text
docs/BMC15_GEOMETRY_PROXY_DIAGNOSTICS_SPEC.md
data/bmc15_geometry_proxy_diagnostics_config.yaml
scripts/run_bmc15_geometry_proxy_diagnostics.py
```

Suggested output root:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/
```

Initial config:

```text
graphs:
  N81_full_baseline
  top_strength_reference_core
  maximum_spanning_tree_envelope
  mutual_kNN_k3_envelope
  threshold_path_consensus_envelope

distance:
  proxy = negative_log_weight

diagnostics:
  triangle_defects = true
  embedding_stress = true
  geodesic_consistency = true
  shell_growth = true
  local_dimension_proxy = true
```

---

## 26. Recommended next sequence

```text
BMC-15a:
  observed geometry-proxy baseline

BMC-15b:
  geometry-proxy null comparison

BMC-15c:
  visualization and core-envelope layout figures
```

BMC-15a should not attempt to include null comparisons or publication figures in the first run.

---

## 27. Final internal summary

```text
BMC-14 showed:
Der Klunker ist nicht leicht durch Nullmodelle nachzubauen.

BMC-15 asks:
Hat der Klunker innere Ordnung,
oder ist er nur ein stabiler graphischer Brocken?
```

Loriot-compatible version:

```text
Der Klunker liegt stabil auf dem Tisch.
Jetzt schauen wir,
ob er Kristallordnung hat
oder nur sehr überzeugend klumpt.
```
