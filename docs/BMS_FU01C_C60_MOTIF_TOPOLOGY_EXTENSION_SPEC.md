# BMS-FU01c — C60 Motif-Preserving Null and Topology-Only Extension Specification

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_EXTENSION_SPEC.md`  
Status: Specification only; no numerical run completed yet

---

## 1. Purpose

BMS-FU01c extends FU01/FU01b by separating three possible sources of the C60 structure-information signal:

```text
1. edge-class / weight effect
2. local pentagon/hexagon motif effect
3. pure topology / cage-connectivity effect
```

FU01 showed that a local 6:6 H-H reference core is strongly retained against degree-preserving rewires.

FU01b showed that this was not only one local seam:

```text
alternative local and distributed 6:6 / 5:6 core selections also show
real-over-null separation against degree-preserving rewires.
```

But FU01/FU01b still used a two-weight edge model:

```text
6:6 = 1.00
5:6 = 0.85
```

Therefore, FU01c asks:

```text
Does the C60 signal survive when edge-class weights are removed or when local
motif structure is preserved by the null model?
```

Internal working image:

```text
FU01: eine echte Naht gefunden.
FU01b: andere Nähte tragen auch.
FU01c: jetzt prüfen, ob der ganze Fußball trägt.
```

---

## 2. Relation to previous FU blocks

### FU01

FU01 established:

```text
The validated C60 graph is a useful structure-calibration object.
The local 6:6 patch core strongly exceeds degree-preserving rewires.
Core-seeded decoys reproduce broad containment.
```

### FU01b

FU01b established:

```text
The result is not confined to the first local 6:6 patch.
Distributed 6:6 and 5:6 pentagon-boundary cores also exceed degree-preserving
rewires in selective readouts.
```

### FU01c

FU01c now tests the mechanism of that result:

```text
Is the signal mainly driven by the 6:6 / 5:6 edge weights?
Is it mainly local pentagon/hexagon motif structure?
Or does pure C60 topology carry enough information by itself?
```

---

## 3. Working question

Main question:

```text
Which layer carries the FU01/FU01b C60 signal: edge-class weights, local
pentagon/hexagon motifs, or topology-only cage connectivity?
```

Sub-questions:

```text
1. Does the signal survive in an equal-weight topology-only C60 graph?

2. Does the signal survive when using graph-distance all-pairs similarity rather
   than only bonded C-C edges?

3. Do motif-preserving nulls reproduce the real graph?

4. If motif-preserving nulls reproduce the signal, is FU01/FU01b mainly local
   motif-sensitive rather than global cage-sensitive?

5. If topology-only variants still exceed nulls, does pure connectivity carry
   recoverable C60 structure?
```

---

## 4. Recommended block label

```text
BMS-FU01c
```

Meaning:

```text
BMS = Bridge-readable Matter / Structure
FU  = Fullerene
01c = motif-preserving and topology-only extension
```

Recommended output directory:

```text
runs/BMS-FU01c/c60_motif_topology_extension_open/
```

Recommended repo files:

```text
docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_EXTENSION_SPEC.md
docs/BMS_FU01C_RUNNER_FIELD_LIST.md
docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_RESULT_NOTE.md

data/bms_fu01c_c60_motif_topology_config.yaml
scripts/run_bms_fu01c_c60_motif_topology_extension.py
```

---

## 5. Input artifacts

Use the validated C60 audit object from BMS-FU01:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

The runner must refuse or warn if:

```text
c60_valid != true
warnings != []
node_count != 60
edge_count != 90
face_count != 32
pentagon_count != 12
hexagon_count != 20
edge_type_counts != {5_6: 60, 6_6: 30}
all_node_degrees_3 != true
```

---

## 6. Representation variants

FU01c should run the same core-selection and null logic across multiple graph representations.

### 6.1 Variant A — bond-class weighted graph

This reproduces FU01/FU01b.

```yaml
representation_id: "bond_class_weighted"
edge_mode: "bond_edges_only"
weight_rule:
  6_6: 1.00
  5_6: 0.85
```

Purpose:

```text
Continuity with FU01/FU01b.
```

Interpretation:

```text
If this variant works but equal-weight topology fails, the signal is largely
edge-class / weight driven.
```

### 6.2 Variant B — topology-only equal-weight graph

All C-C graph edges receive the same weight:

```yaml
representation_id: "topology_only_equal_weight"
edge_mode: "bond_edges_only"
weight_rule:
  all_edges: 1.00
```

Purpose:

```text
Remove edge-class weight information and test pure cage connectivity.
```

Interpretation:

```text
If separation survives here, pure topology carries information.
If separation collapses, FU01/FU01b mainly used edge-class weights.
```

Known limitation:

```text
Threshold and top-strength constructions become tie-sensitive under equal
weights. This must be explicitly reported.
```

### 6.3 Variant C — graph-distance all-pairs similarity

Build a complete or sparse all-pairs similarity graph from shortest-path distance in the C60 topology.

Example:

```yaml
representation_id: "graph_distance_similarity"
edge_mode: "all_pairs"
distance_rule: "shortest_path_distance"
weight_rule: "1 / (1 + graph_distance)"
max_graph_distance: null
```

Optional sparse version:

```yaml
max_graph_distance: 3
```

Purpose:

```text
Test whether C60 topology is readable as relational distance structure, not
only as bonded-edge structure.
```

Interpretation:

```text
If all-pairs graph-distance similarity yields robust signal, the diagnostic is
sensitive to cage topology as a relational distance structure.
```

### 6.4 Variant D — face-motif weighted graph

Weights derive from face-motif context, not just 6:6 / 5:6 edge labels.

Example:

```yaml
representation_id: "face_motif_weighted"
edge_mode: "bond_edges_only"
weight_rule:
  H_H: 1.00
  H_P: 0.85
```

This is similar to bond-class weighted for C60 but should be explicitly tagged as motif-derived.

Purpose:

```text
Make the motif interpretation explicit and prepare for motif-preserving nulls.
```

Recommended FU01c-v0 representations:

```text
A bond_class_weighted
B topology_only_equal_weight
C graph_distance_similarity with max_graph_distance = 3
```

---

## 7. Core variants

Reuse FU01b deterministic core variants for comparability:

```text
local_6_6_patch_core
distributed_6_6_core
local_5_6_pentagon_boundary_core
distributed_5_6_pentagon_boundary_core
```

Important:

```text
Core definitions should be selected from the original validated C60 bond-edge
graph, then evaluated within each representation.
```

This avoids changing the meaning of the core when representation changes.

For graph-distance all-pairs representations:

```text
Reference-core edges remain the same physical C60 bond-pairs, but the envelope
can contain additional non-bonded all-pairs edges.
```

---

## 8. Null families

FU01c should include prior nulls plus motif-aware controls.

### 8.1 Degree-preserving rewire

```text
Preserve degree sequence.
Destroy local pentagon/hexagon motifs and global fullerene cage organization.
```

Purpose:

```text
Baseline test: more than degree-3 regularity?
```

### 8.2 Edge-class shuffle

```text
Preserve topology and edge-class counts.
Shuffle 6:6 / 5:6 labels over C60 edges.
```

Purpose:

```text
Test whether edge-class placement matters.
```

Only meaningful for representation variants with edge-class / motif weights.

For topology-only equal-weight:

```text
edge_class_shuffle may become irrelevant and should be reported as inactive or
non-informative.
```

### 8.3 Core-seeded decoy

```text
Preserve topology and edge-type counts.
Force current reference-core edges to carry the preferred target edge type.
```

Purpose:

```text
Audit whether broad core containment is cheap.
```

Must be conditioned on:

```text
representation_id
core_variant_id
```

### 8.4 Motif-preserving edge swap

New FU01c null.

Goal:

```text
Perturb global connectivity while preserving local face/motif constraints as
far as feasible.
```

Practical version:

```text
Preserve degree sequence and preserve each node's local face signature count
as metadata, while swapping edges only among compatible motif classes.
```

Since full planar fullerene-preserving rewiring is nontrivial, FU01c-v0 should call this a proxy:

```text
motif_class_preserving_edge_swap_proxy
```

Possible conservative implementation:

```text
Only swap edges within the same edge_type class:
  6_6 with 6_6
  5_6 with 5_6

Reject swaps that create duplicate edges or self-loops.
Keep degree sequence.
```

This preserves:

```text
degree sequence
global edge-type counts
edge-type class of swapped edges
```

It does not fully preserve:

```text
planarity
face cycles
true fullerene validity
```

Therefore this null should be labeled as a proxy, not as a true fullerene randomizer.

Purpose:

```text
Test whether real C60 organization exceeds edge-class-preserving topology
perturbations.
```

### 8.5 Face-cycle preserving null, future variant

A harder later null:

```text
preserve 12 pentagon and 20 hexagon face cycle constraints
while altering global cage connectivity
```

This may require specialized fullerene graph generation and is not required for FU01c-v0.

---

## 9. Construction families

Use FU01b construction families for continuity, but add representation-aware warnings.

```yaml
construction_families:
  top_strength:
    enabled: true
    edge_counts: [12, 20, 30, 45, 60, 90]

  threshold:
    enabled: true
    thresholds: [0.50, 0.80, 0.85, 0.90, 0.95, 1.00]

  mutual_knn:
    enabled: true
    k_values: [2, 3, 4, 6]

  maximum_spanning_tree:
    enabled: true

  graph_distance_shells:
    enabled: true
    shell_depths: [1, 2, 3]
```

Representation-specific caution:

```text
topology_only_equal_weight:
  top_strength, threshold, and MST may be tie-sensitive.

graph_distance_similarity:
  thresholds and mutual-kNN may become more informative than raw top-strength.
```

---

## 10. Metrics

Keep FU01b metrics:

```text
envelope_core_edge_containment
envelope_core_node_containment
edge_type_6_6_fraction
edge_type_5_6_fraction
connected_component_count
```

Add FU01c representation-aware metrics:

```text
representation_id
edge_mode
weight_rule_id
null_family
core_variant_id
```

Add topology/motif metrics where feasible:

```text
bond_edge_fraction
nonbond_edge_fraction
mean_graph_distance_selected
core_edge_graph_distance_mean
motif_class_retention
edge_type_count_deviation
```

Recommended FU01c-v0 metrics:

| field name | type | description |
|---|---:|---|
| `representation_id` | string | Representation variant. |
| `core_variant_id` | string | Core variant label. |
| `envelope_core_edge_containment` | float | Fraction of reference-core bond edges recovered. |
| `envelope_core_node_containment` | float | Fraction of reference-core nodes recovered. |
| `edge_type_6_6_fraction` | float | Fraction of selected bond edges with 6:6 class. |
| `edge_type_5_6_fraction` | float | Fraction of selected bond edges with 5:6 class. |
| `bond_edge_fraction` | float | Fraction of selected edges that are original C60 bond edges. |
| `nonbond_edge_fraction` | float | Fraction of selected edges that are all-pairs nonbond edges. |
| `mean_graph_distance_selected` | float | Mean C60 shortest-path distance among selected edges. |
| `connected_component_count` | float | Connected components in selected envelope. |

---

## 11. Expected outputs

Recommended output directory:

```text
runs/BMS-FU01c/c60_motif_topology_extension_open/
```

Expected files:

```text
bms_fu01c_nodes_resolved.csv
bms_fu01c_edges.csv
bms_fu01c_faces.csv
bms_fu01c_representations.csv
bms_fu01c_core_variants.csv
bms_fu01c_reference_core_edges.csv
bms_fu01c_core_metrics.csv
bms_fu01c_envelope_metrics.csv
bms_fu01c_real_vs_null_summary.csv
bms_fu01c_representation_summary.csv
bms_fu01c_core_variant_summary.csv
bms_fu01c_null_family_inventory.csv
bms_fu01c_run_manifest.json
bms_fu01c_warnings.json
bms_fu01c_config_resolved.yaml
```

Required summary grouping:

```text
representation_id
core_variant_id
null_family
metric_name
construction_family
construction_variant
```

---

## 12. Interpretation patterns

### Pattern A — bond-class weighted works, topology-only collapses

Allowed interpretation:

```text
The FU01/FU01b signal is mainly edge-class / weight driven.
```

### Pattern B — topology-only survives degree rewires

Allowed interpretation:

```text
Pure C60 cage connectivity carries detectable structure beyond degree sequence.
```

### Pattern C — graph-distance similarity survives strongly

Allowed interpretation:

```text
C60 topology is readable as relational distance structure in this diagnostic.
```

### Pattern D — motif-preserving swap reproduces real behavior

Allowed interpretation:

```text
The current signal is mainly local motif / edge-class organization and not yet
evidence for global cage organization.
```

### Pattern E — real exceeds motif-preserving swap

Allowed interpretation:

```text
The diagnostic may be sensitive to organization beyond local motif class,
potentially including broader cage arrangement. This remains construction-
qualified and requires stronger fullerene-preserving controls.
```

### Pattern F — core-seeded decoy reproduces broad containment

Allowed interpretation:

```text
Broad core containment remains cheap and should not be used as standalone
specificity evidence.
```

---

## 13. Claim boundary

Allowed:

```text
BMS-FU01c tests whether the C60 diagnostic signal is carried by edge-class
weights, local motif structure, topology-only connectivity, or graph-distance
relational structure.
```

Allowed after positive topology-only result:

```text
BMS-FU01c supports that C60 topology alone carries detectable structure in the
diagnostic beyond degree-preserving rewires.
```

Allowed after motif-null reproduction:

```text
BMS-FU01c shows that the observed signal is largely reproducible by
motif-preserving controls and should be interpreted as local motif sensitivity,
not global fullerene-symmetry recovery.
```

Not allowed:

```text
C60 proves emergent spacetime.
The bridge recognizes molecules.
A physical metric has been recovered.
Fullerene symmetry is proven as spacetime structure.
Quantum chemistry has been reproduced.
Global C60 symmetry has been fully recovered.
```

---

## 14. Recommended immediate implementation

Create:

```text
data/bms_fu01c_c60_motif_topology_config.yaml
scripts/run_bms_fu01c_c60_motif_topology_extension.py
docs/BMS_FU01C_RUNNER_FIELD_LIST.md
```

Implementation plan:

```text
1. Load validated C60 graph.
2. Build canonical shortest-path matrix on C60 topology.
3. Build representation variants:
   a. bond_class_weighted
   b. topology_only_equal_weight
   c. graph_distance_similarity
4. Build FU01b core variants from original bond graph.
5. For each representation and core:
   a. compute real metrics
   b. generate nulls
   c. compute null metrics
   d. summarize real-vs-null
6. Write representation-aware outputs.
```

Critical implementation note:

```text
Do not let graph-distance all-pairs representation redefine the reference-core
edges. Reference cores must remain the same audited C60 bond-pair sets.
```

---

## 15. Minimal commit plan

Commit the specification first:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU01C_C60_MOTIF_TOPOLOGY_EXTENSION_SPEC.md \
  docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_EXTENSION_SPEC.md

git add docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_EXTENSION_SPEC.md

git status --short

git commit -m "Add BMS-FU01c C60 motif topology extension specification"

git push
```

Do not implement before FU01b implementation and result note are cleanly committed.

---

## 16. Internal summary

```text
FU01:
  eine echte lokale 6:6-Naht gefunden

FU01b:
  andere 6:6- und 5:6-Schnitte tragen auch

FU01c:
  jetzt zerlegen:
    Gewicht?
    Motiv?
    Topologie?
    ganzer Fußball?
```
