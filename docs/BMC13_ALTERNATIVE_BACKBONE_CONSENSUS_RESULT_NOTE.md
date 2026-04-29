# BMC-13 Alternative Backbone / Consensus-Backbone Result Note

## Purpose

BMC-13 addresses the strongest remaining methodological objection after BMC-12f:

```text
The current backbone variants may not be independent methods.
```

BMC-12f showed that the BMC09d reference anchor at:

```text
N = 81
```

is stable across the tested decision-threshold and dominance-gap grid.

However, the previous backbone variants were all members of the same top-strength family:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

These are different cuts through the same edge-weight ordering.

BMC-13 therefore asks:

```text
Does the N=81 sparse/local backbone anchor remain visible under conceptually different backbone extraction rules?
```

Internal image:

```text
Bleibt der Kristallisationskeim sichtbar,
wenn wir die Beleuchtung wechseln?
```

---

## 1. Input

BMC-13 uses the existing BMC-12e edge inventory:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_edges_inventory.csv
```

Initial focus:

```text
edge_count_target = 81
case_id = baseline_all_features
```

This is the strongest reference point after BMC-12f.

---

## 2. Tested backbone methods

BMC-13 compares four backbone views.

### 2.1 top_strength_reference

This is the compact reference core, comparable to the earlier top-strength family.

Default:

```text
k_reference_edges = 6
```

### 2.2 mutual_kNN_k3

A local-neighborhood method.

An edge is retained only if both endpoints include each other among their top local neighbors.

Interpretation:

```text
local reciprocal neighborhood support
```

### 2.3 maximum_spanning_tree

A global load-bearing skeleton.

It keeps a maximum-weight spanning tree over the available N=81 edge set.

Interpretation:

```text
minimal connected high-weight scaffold
```

### 2.4 threshold_path_consensus_min3

A sparsity-path persistence method.

It uses baseline edge sets across:

```text
N = 70, 75, 81
```

and keeps edges present across all selected sparse-path levels.

Interpretation:

```text
edges that persist along the sparse path toward the N=81 reference graph
```

---

## 3. Initial BMC-13 output

BMC-13 produced:

| method_id | edges | nodes | components | largest_component | jaccard_ref | jaccard_consensus | label |
|---|---:|---:|---:|---:|---:|---:|---|
| maximum_spanning_tree | 21 | 22 | 1 | 22 | 0.286 | 0.282 | low_overlap |
| mutual_kNN_k3 | 23 | 22 | 4 | 10 | 0.261 | 0.329 | moderate_overlap |
| threshold_path_consensus_min3 | 70 | 22 | 2 | 14 | 0.086 | 1.000 | high_overlap |
| top_strength_reference | 6 | 9 | 3 | 3 | 1.000 | 0.086 | reference |

The pairwise overlap summary showed:

| method_a | method_b | shared_edges | jaccard |
|---|---|---:|---:|
| maximum_spanning_tree | mutual_kNN_k3 | 18 | 0.692 |
| maximum_spanning_tree | threshold_path_consensus_min3 | 20 | 0.282 |
| maximum_spanning_tree | top_strength_reference | 6 | 0.286 |
| mutual_kNN_k3 | threshold_path_consensus_min3 | 23 | 0.329 |
| mutual_kNN_k3 | top_strength_reference | 6 | 0.261 |
| threshold_path_consensus_min3 | top_strength_reference | 6 | 0.086 |

---

## 4. Why BMC-13a was needed

The initial BMC-13 summary relied heavily on Jaccard overlap.

Jaccard is useful, but it can be misleading when comparing a small reference core with much larger alternative methods.

In this case:

```text
top_strength_reference:        6 edges
maximum_spanning_tree:        21 edges
mutual_kNN_k3:                23 edges
threshold_path_consensus:     70 edges
```

If all 6 reference edges are contained in a larger method, the Jaccard score can still be low because the union is much larger.

Therefore BMC-13a added containment metrics.

---

## 5. BMC-13a containment metrics

BMC-13a added:

```text
reference_edge_count
reference_containment
method_containment
consensus_edge_count
consensus_containment
method_vs_consensus_containment
containment_label
```

Definitions:

```text
reference_containment = overlap_with_reference_edges / reference_edge_count
method_containment    = overlap_with_reference_edges / method_edge_count
```

Interpretation:

```text
reference_containment = 1.000
```

means the entire reference core is contained in the method.

```text
method_containment < 1.000
```

means the method contains additional envelope structure beyond the reference core.

---

## 6. BMC-13a refined result

BMC-13a produced:

| method_id | edges | overlap_ref | reference_containment | method_containment | jaccard_ref | containment_label |
|---|---:|---:|---:|---:|---:|---|
| maximum_spanning_tree | 21 | 6 | 1.000 | 0.286 | 0.286 | reference_core_fully_contained |
| mutual_kNN_k3 | 23 | 6 | 1.000 | 0.261 | 0.261 | reference_core_fully_contained |
| threshold_path_consensus_min3 | 70 | 6 | 1.000 | 0.086 | 0.086 | reference_core_fully_contained |
| top_strength_reference | 6 | 6 | 1.000 | 1.000 | 1.000 | reference_core_equivalent |

---

## 7. Main finding

The six-edge top-strength reference core is fully contained in every tested alternative backbone construction:

```text
maximum_spanning_tree:        6/6 reference edges contained
mutual_kNN_k3:                6/6 reference edges contained
threshold_path_consensus:     6/6 reference edges contained
top_strength_reference:       6/6 reference edges contained
```

### Interpretation

The N=81 reference core is not absent under alternative backbone methods.

Instead:

```text
The compact top-strength core is embedded inside larger method-specific backbone envelopes.
```

This changes the interpretation from:

```text
low overlap with alternative methods
```

to:

```text
full reference-core containment with method-dependent envelope size
```

---

## 8. Core-vs-envelope interpretation

BMC-13/13a supports a core-vs-envelope view.

### Core

The core is the compact six-edge top-strength reference structure:

```text
top_strength_reference
```

It is small:

```text
6 edges
9 nodes
3 components
```

but fully contained in all tested alternative methods.

### Envelope

The envelope is the broader structure recovered by alternative methods:

```text
maximum_spanning_tree
mutual_kNN_k3
threshold_path_consensus_min3
```

These methods recover larger structures:

```text
21 edges
23 edges
70 edges
```

The envelope size and connectivity depend on the method.

### Updated image

Internal picture:

```text
Der harte Keim ist überall drin.
Aber je nach Beleuchtung sieht man unterschiedlich viel Hülle drumherum.
```

Technical wording:

```text
The N=81 top-strength reference core persists as an embedded core across all tested alternative backbone constructions, while the broader backbone envelope remains method-dependent.
```

---

## 9. What BMC-13 strengthens

BMC-13/13a weakens the objection:

```text
The N=81 anchor is only an artifact of the top-strength family.
```

It does not remove the objection completely, but it narrows it.

The result shows:

```text
The exact compact core comes from top-strength selection,
but its edges are not exclusive to that method.
```

They also appear inside:

```text
global spanning-tree support
local reciprocal-neighborhood support
sparsity-path consensus support
```

This is a meaningful methodological strengthening.

---

## 10. What BMC-13 does not prove

BMC-13 does not prove:

```text
a method-independent full backbone
```

because the broader envelopes differ by method.

BMC-13 does not prove:

```text
physical spacetime emergence
```

because it remains a graph-method diagnostic.

BMC-13 does not prove:

```text
a unique geometric structure
```

because no metric, dimension, causal order, continuum limit, or physical observables are established.

BMC-13 does not prove:

```text
feature-role hierarchy
```

because feature ablation remains graph-size and threshold sensitive from BMC-12e/f.

---

## 11. Allowed statements after BMC-13/13a

Allowed:

```text
The six-edge N=81 top-strength reference core is fully contained in all tested alternative backbone constructions.
```

```text
The broader backbone envelope remains method-dependent.
```

```text
BMC-13/13a supports a core-vs-envelope interpretation of the N=81 anchor.
```

```text
The result weakens, but does not eliminate, the concern that the anchor is tied to top-strength extraction.
```

```text
The N=81 anchor appears as a compact core embedded within larger alternative backbone envelopes.
```

Avoid:

```text
BMC-13 proves method-independent backbone robustness.
```

```text
All methods recover the same backbone.
```

```text
The N=81 anchor is no longer method-dependent at all.
```

```text
BMC-13 establishes physical locality or geometry.
```

---

## 12. Conservative external wording

A suitable research-note paragraph:

> BMC-13 evaluates whether the N=81 reference anchor is specific to the top-strength backbone family. Alternative backbone constructions based on reciprocal local neighborhoods, maximum spanning support, and sparse-path consensus recover substantially larger envelopes than the compact six-edge top-strength reference. A Jaccard-only comparison therefore underestimates the result because of strong size asymmetry. After adding containment metrics in BMC-13a, the full six-edge reference core is found to be contained in every tested alternative backbone construction. This supports a core-vs-envelope interpretation: the compact N=81 top-strength core persists across the tested alternative methods, while the broader backbone envelope remains method-dependent. No claim of physical geometry reconstruction is made.

---

## 13. Internal summary

```text
BMC-12f:
N=81 hält bei Threshold-Wacklern.

BMC-13:
Wir wechseln die Backbone-Beleuchtung.

BMC-13a:
Jaccard allein war zu streng.

Ergebnis:
Der harte 6-Kanten-Keim ist überall drin.
Die Hülle drumherum hängt von der Methode ab.
```

Loriot-compatible version:

```text
Der Klunker ist nicht immer gleich groß,
aber der innere Kristallisationskeim glitzert bei jeder Beleuchtung an derselben Stelle.
```

---

## 14. Next methodological step

The next major open methodological risk is no longer only:

```text
top-strength family dependence
```

but rather:

```text
core persistence vs envelope dependence under controls
```

Possible next blocks:

### BMC-13b

Expand alternative backbone methods and parameter ranges:

```text
mutual_kNN k = 2,3,4
top_strength k = 4,6,8
MST plus high-weight augmentation
consensus with minimum presence 2/3 versus 3/3
```

### BMC-14

Null-model or randomized control:

```text
Does a comparable six-edge reference core containment occur under randomized or permuted feature controls?
```

### Recommended next priority

BMC-14 is likely the stronger next control, because BMC-13/13a already shows that the core is embedded across methods. The next skeptical question becomes:

```text
Would a similar core containment appear in null or randomized relational structures?
```

---

## 15. File anchors

BMC-13 specification:

```text
docs/BMC13_ALTERNATIVE_BACKBONE_CONSENSUS_SPEC.md
```

BMC-13 runner:

```text
scripts/run_bmc13_alternative_backbone_consensus.py
```

BMC-13 config:

```text
data/bmc13_alternative_backbone_consensus_config.yaml
```

BMC-13 outputs:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13_backbone_edges.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13_method_summary.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13_pairwise_overlap_summary.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13_readout.md
runs/BMC-13/alternative_backbone_consensus_open/bmc13_metrics.json
```

BMC-13a specification:

```text
docs/BMC13A_CONTAINMENT_METRICS_REFINEMENT_SPEC.md
```

BMC-13a refiner:

```text
scripts/refine_bmc13_containment_metrics.py
```

BMC-13a outputs:

```text
runs/BMC-13/alternative_backbone_consensus_open/bmc13a_method_summary_with_containment.csv
runs/BMC-13/alternative_backbone_consensus_open/bmc13a_containment_readout.md
runs/BMC-13/alternative_backbone_consensus_open/bmc13a_metrics.json
```

---

## 16. Consolidated status after BMC-13/13a

### Befund

The six-edge N=81 top-strength reference core is fully contained in all tested alternative backbone constructions.

### Interpretation

The N=81 reference anchor is best described as a compact core embedded within larger method-dependent backbone envelopes.

### Hypothesis

The N=81 core may represent a persistent relational locality-backbone candidate, while the broader envelope depends on the extraction method.

### Open gap

A null-model or randomized-control test is needed to evaluate whether comparable core containment can arise in non-specific or randomized relational structures.
