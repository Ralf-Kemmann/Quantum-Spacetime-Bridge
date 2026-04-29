# BMC-15 Geometry-Proxy Diagnostics Result Note

## Purpose

BMC-15a is the first geometry-proxy diagnostic block after the BMC-14 null-control series.

The BMC-14 series established that the observed N=81 six-edge core identity was not fully recovered under the tested null families:

```text
feature-randomized nulls
covariance-preserving feature nulls
weight-rank edge rewiring
degree-preserving edge rewiring
degree + weightclass edge rewiring
Gaussian copula / rank-correlation feature nulls
```

BMC-15a asks the next question:

```text
Does the robust N=81 core/envelope structure exhibit geometry-like proxy behavior?
```

Important:

```text
BMC-15a is a geometry-proxy diagnostic.
It is not a physical spacetime reconstruction.
```

Internal image:

```text
Der Klunker liegt stabil auf dem Tisch.
Jetzt schauen wir,
ob er Kristallordnung hat
oder nur sehr überzeugend klumpt.
```

---

## 1. Scope

BMC-15a evaluates the observed graph objects only.

It does not yet compare observed geometry-proxy diagnostics against null ensembles.

That later step is reserved for:

```text
BMC-15b geometry-proxy null comparison
```

BMC-15a computes:

```text
graph inventory
triangle inequality defects
low-dimensional embedding stress
geodesic consistency
shell growth from core
local dimension proxy
```

All metrics are interpreted as:

```text
geometry-like proxy diagnostics
```

not as physical geometry.

---

## 2. Graph objects analyzed

BMC-15a analyzed the following observed graph objects:

```text
N81_full_baseline
top_strength_reference_core
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
threshold_path_consensus_envelope
```

These correspond to:

```text
full N=81 relational neighborhood
compact six-edge reference core
global spanning-tree skeleton
local mutual-neighborhood envelope
broader sparse-path consensus envelope
```

---

## 3. Graph inventory

| graph_id | edges | nodes | components | largest_component | mean_weight | mean_proxy_distance |
|---|---:|---:|---:|---:|---:|---:|
| N81_full_baseline | 81 | 22 | 1 | 22 | 0.451 | 0.833 |
| top_strength_reference_core | 6 | 9 | 3 | 3 | 0.669 | 0.403 |
| maximum_spanning_tree_envelope | 21 | 22 | 1 | 22 | 0.589 | 0.550 |
| mutual_kNN_k3_envelope | 23 | 22 | 4 | 10 | 0.611 | 0.498 |
| threshold_path_consensus_envelope | 70 | 22 | 2 | 14 | 0.473 | 0.778 |

### Interpretation

The observed N=81 baseline and maximum-spanning-tree envelope are connected over all 22 nodes.

The top-strength reference core is compact but disconnected:

```text
6 edges
9 nodes
3 components
largest component = 3
```

Therefore, the compact core alone is too small and fragmented for strong standalone geometry-proxy interpretation.

The geometry-proxy interpretation is more meaningful for:

```text
N81_full_baseline
maximum_spanning_tree_envelope
mutual_kNN_k3 largest component
threshold_path_consensus envelope
```

---

## 4. Triangle inequality defects

BMC-15a used the primary distance proxy:

```text
d(i,j) = -log(w(i,j))
```

Triangle inequality defects were tested in:

```text
edge_only mode
shortest_path_completed mode
```

### Result

| graph_id | mode | triangles | violation_fraction | max_violation |
|---|---|---:|---:|---:|
| N81_full_baseline | edge_only | 139 | 0.000 | 0 |
| N81_full_baseline | shortest_path_completed | 1540 | 0.000 | 0 |
| top_strength_reference_core | edge_only | 0 | 0.000 | 0 |
| top_strength_reference_core | shortest_path_completed | 3 | 0.000 | 0 |
| maximum_spanning_tree_envelope | edge_only | 0 | 0.000 | 0 |
| maximum_spanning_tree_envelope | shortest_path_completed | 1540 | 0.000 | 0 |
| mutual_kNN_k3_envelope | edge_only | 5 | 0.000 | 0 |
| mutual_kNN_k3_envelope | shortest_path_completed | 176 | 0.000 | 0 |
| threshold_path_consensus_envelope | edge_only | 117 | 0.000 | 0 |
| threshold_path_consensus_envelope | shortest_path_completed | 420 | 0.000 | 0 |

### Interpretation

No triangle inequality violations were observed under the tested proxy distance convention.

The most informative triangle results are the edge-only tests, because shortest-path-completed distances are expected to be triangle-consistent by construction when positive edge weights are used.

Important edge-only observations:

```text
N81_full_baseline:
  139 tested direct triangles, 0 violations

threshold_path_consensus_envelope:
  117 tested direct triangles, 0 violations

mutual_kNN_k3_envelope:
  5 tested direct triangles, 0 violations
```

### Caution

The shortest-path-completed triangle mode is partly tautological and should not be overinterpreted.

Allowed:

```text
The observed direct triangles show no triangle inequality defects under the tested proxy distance.
```

Avoid:

```text
This proves a physical metric geometry.
```

---

## 5. Embedding stress

Classical MDS-style embedding diagnostics were computed for dimensions:

```text
2D
3D
4D
```

using shortest-path distances on the largest connected component.

### Result

| graph_id | dim | nodes | stress_normalized | negative_to_positive_abs_ratio |
|---|---:|---:|---:|---:|
| N81_full_baseline | 2 | 22 | 0.107 | 0.081 |
| N81_full_baseline | 3 | 22 | 0.063 | 0.081 |
| N81_full_baseline | 4 | 22 | 0.061 | 0.081 |
| top_strength_reference_core | 2 | 3 | 0.000 | 0.000 |
| top_strength_reference_core | 3 | 3 | 0.000 | 0.000 |
| top_strength_reference_core | 4 | 3 | 0.000 | 0.000 |
| maximum_spanning_tree_envelope | 2 | 22 | 0.119 | 0.044 |
| maximum_spanning_tree_envelope | 3 | 22 | 0.066 | 0.044 |
| maximum_spanning_tree_envelope | 4 | 22 | 0.056 | 0.044 |
| mutual_kNN_k3_envelope | 2 | 10 | 0.040 | 0.011 |
| mutual_kNN_k3_envelope | 3 | 10 | 0.014 | 0.011 |
| mutual_kNN_k3_envelope | 4 | 10 | 0.014 | 0.011 |
| threshold_path_consensus_envelope | 2 | 14 | 0.083 | 0.079 |
| threshold_path_consensus_envelope | 3 | 14 | 0.067 | 0.079 |
| threshold_path_consensus_envelope | 4 | 14 | 0.065 | 0.079 |

### Interpretation

The observed N81 baseline and larger backbone envelopes show low to moderately low embedding stress.

Especially in 3D and 4D:

```text
N81_full_baseline:
  stress approx. 0.063 / 0.061

maximum_spanning_tree_envelope:
  stress approx. 0.066 / 0.056

mutual_kNN_k3_envelope:
  stress approx. 0.014 / 0.014

threshold_path_consensus_envelope:
  stress approx. 0.067 / 0.065
```

This supports the cautious statement:

```text
The observed core/envelope structures show low-dimensional embedding compatibility under the tested proxy distances.
```

### Important caution about the compact core

The top-strength reference core has:

```text
largest component size = 3
```

Its zero embedding stress is therefore trivial and should not be used as evidence of meaningful standalone geometry.

Allowed:

```text
The compact core is too small and disconnected for meaningful standalone embedding interpretation.
```

Avoid:

```text
The core embeds perfectly, therefore it is geometric.
```

---

## 6. Local dimension proxy

BMC-15a estimated a hop-shell growth proxy from the core-node set.

### Result

| graph_id | fit_points | effective_dimension_proxy | fit_r2 | label |
|---|---:|---:|---:|---|
| N81_full_baseline | 2 | 0.000 | 0.000 | insufficient_points |
| top_strength_reference_core | 0 | 0.000 | 0.000 | insufficient_points |
| maximum_spanning_tree_envelope | 4 | 0.445 | 0.933 | stable_proxy |
| mutual_kNN_k3_envelope | 5 | 0.245 | 0.983 | stable_proxy |
| threshold_path_consensus_envelope | 3 | 0.301 | 0.944 | stable_proxy |

### Interpretation

The larger envelopes show stable shell-growth fits:

```text
maximum_spanning_tree_envelope:
  d_eff approx. 0.445, R2 approx. 0.933

mutual_kNN_k3_envelope:
  d_eff approx. 0.245, R2 approx. 0.983

threshold_path_consensus_envelope:
  d_eff approx. 0.301, R2 approx. 0.944
```

However, the effective dimension proxy values are small.

Therefore, the interpretation should be:

```text
ordered sparse-scaffold growth
```

not:

```text
physical spatial dimension
```

Allowed:

```text
The larger envelopes show stable but low effective shell-growth proxies, consistent with sparse scaffold-like expansion from the core.
```

Avoid:

```text
The graph has measured physical dimension 0.3.
```

---

## 7. Geodesic consistency

BMC-15a also wrote:

```text
runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_geodesic_consistency_summary.csv
```

The readout table primarily summarized inventory, triangle defects, embedding stress, and local dimension proxies.

Geodesic consistency should be inspected separately before making strong statements about shortest-path versus direct-distance preservation.

Suggested command:

```bash
column -s, -t < runs/BMC-15/geometry_proxy_diagnostics_open/bmc15_geodesic_consistency_summary.csv
```

Until that table is reviewed, geodesic consistency should remain an open sub-diagnostic.

---

## 8. Main BMC-15a finding

BMC-15a provides an observed geometry-proxy baseline.

The observed N81 full baseline and larger backbone envelopes show:

```text
zero direct triangle inequality defects under tested proxy distance
low to moderately low embedding stress
small negative-eigenvalue burden
stable shell-growth proxies for larger envelopes
```

This supports:

```text
geometry-like proxy consistency
```

for the observed core/envelope structure.

It does not support:

```text
physical spacetime emergence
```

or:

```text
continuum geometry reconstruction
```

---

## 9. Strongest current interpretation

The strongest current interpretation is:

> BMC-15a provides an observed geometry-proxy baseline for the robust N=81 core/envelope structure. Under the tested distance convention, the N81 baseline and larger backbone envelopes show no direct triangle-inequality defects, low to moderately low low-dimensional embedding stress, and stable sparse-scaffold shell-growth proxies. The compact six-edge core alone is too small and disconnected for meaningful standalone geometry interpretation. These results motivate further geometry-proxy analysis, especially null comparisons in BMC-15b, but do not establish physical spacetime emergence or continuum geometry.

Short version:

```text
The observed envelopes show geometry-like proxy consistency.
The compact core alone is not enough.
Null comparison remains necessary.
```

Internal version:

```text
Der Klunker ist nicht nur hart.
In den Hüllen sieht man erste Kristallordnung.
Aber es ist noch kein fertiger Kristall
und schon gar keine physikalische Raumzeit.
```

---

## 10. What BMC-15a strengthens

BMC-15a strengthens the project status by adding a new diagnostic layer.

Previous BMC chain:

```text
BMC-12f:
  threshold/gap robustness

BMC-13a:
  core embedded in method-dependent envelopes

BMC-14 series:
  observed core identity robust against tested null families
```

BMC-15a adds:

```text
observed geometry-proxy baseline
```

The current methodological chain becomes:

```text
threshold-stable
method-crossing embedded
null-resistant core identity
geometry-proxy compatible observed envelopes
```

within the tested scope.

---

## 11. What BMC-15a does not prove

BMC-15a does not prove:

```text
physical spacetime emergence
```

It does not prove:

```text
a physical metric
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
physical dimension
```

It does not prove:

```text
that geometry-proxy behavior is non-null
```

because BMC-15a has not yet compared geometry-proxy values against null ensembles.

---

## 12. Allowed statements after BMC-15a

Allowed:

```text
BMC-15a provides an observed geometry-proxy baseline.
```

```text
The N81 baseline and larger envelopes show no direct triangle inequality defects under the tested proxy distance.
```

```text
The observed larger envelopes show low to moderately low embedding stress, especially in 3D/4D.
```

```text
The larger envelopes show stable but low shell-growth dimension proxies, consistent with sparse scaffold-like growth.
```

```text
The compact six-edge core is too small and disconnected for meaningful standalone geometry interpretation.
```

```text
BMC-15b null comparison remains necessary before interpreting these geometry proxies as specific to the observed structure.
```

Avoid:

```text
BMC-15a proves emergent spacetime.
```

```text
The graph has physical dimension 0.3.
```

```text
The core is a physical geometry.
```

```text
Low embedding stress proves physical space.
```

```text
Shortest-path triangle consistency proves metric structure.
```

---

## 13. Conservative external wording

A suitable research-note paragraph:

> BMC-15a establishes an observed geometry-proxy baseline for the robust N=81 core/envelope structure. Using a negative-log weight distance proxy, the N81 baseline and larger backbone envelopes show no direct triangle-inequality defects in the tested edge-only triangles. Low-dimensional embedding stress is low to moderately low, particularly for 3D and 4D embeddings of the N81 baseline and the larger envelopes. Shell-growth proxies from the core are stable for the larger envelopes, but indicate sparse scaffold-like growth rather than a physical spatial dimension. The compact six-edge core alone is too small and disconnected for standalone geometry interpretation. These diagnostics support geometry-like proxy consistency in the observed structures, while leaving null comparison and physical interpretation explicitly open.

---

## 14. Recommended next step

The immediate next step should be:

```text
BMC-15b Geometry-Proxy Null Comparison
```

Purpose:

```text
Test whether the observed geometry-proxy values are distinctive
relative to null-generated graphs from BMC-14 / BMC-14d / BMC-14e.
```

Candidate comparison targets:

```text
embedding stress distributions
triangle defect distributions
shell-growth dimension proxy distributions
geodesic consistency distributions
negative eigenvalue burden distributions
```

Important:

```text
BMC-15b should reuse the same proxy definitions as BMC-15a.
```

---

## 15. File anchors

BMC-15 specification:

```text
docs/BMC15_GEOMETRY_PROXY_DIAGNOSTICS_SPEC.md
```

BMC-15 config:

```text
data/bmc15_geometry_proxy_diagnostics_config.yaml
```

BMC-15 runner:

```text
scripts/run_bmc15_geometry_proxy_diagnostics.py
```

BMC-15 outputs:

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

This result note:

```text
docs/BMC15_GEOMETRY_PROXY_DIAGNOSTICS_RESULT_NOTE.md
```

---

## 16. Consolidated status after BMC-15a

### Befund

The observed N81 baseline and larger backbone envelopes show no direct triangle inequality defects under the tested proxy distance, low to moderately low embedding stress, and stable sparse-scaffold shell-growth proxies. The compact six-edge core is too small and disconnected for standalone geometry interpretation.

### Interpretation

The observed robust core/envelope structure exhibits geometry-like proxy consistency in the tested diagnostics, especially at the envelope level.

### Hypothesis

The robust N=81 core/envelope may support a relational geometry-proxy reading, but this remains a methodological hypothesis pending null comparison.

### Open gap

BMC-15b must test whether these geometry-proxy values are distinctive relative to null-generated structures.
