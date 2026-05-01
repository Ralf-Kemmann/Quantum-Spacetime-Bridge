# BMS-FU01c — C60 Motif/Topology Extension Initial Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU01c motif/topology extension

---

## 1. Purpose

BMS-FU01c tests whether the C60 signal persists when explicit 6:6 / 5:6 edge-class weight information is removed.

Working question:

```text
Bleibt das Signal, wenn wir die 6:6/5:6-Gewichtsinformation herausnehmen?
```

Scientific formulation:

```text
Does the C60 structure signal persist under topology-only equal-weight and
graph-distance representations, or is it primarily driven by the explicit
6:6 / 5:6 edge-class weight assignment?
```

Internal image:

```text
Erkennt der Runner den Fußball noch,
wenn wir ihm die farbigen Nähte wegnehmen?
```

---

## 2. Run context

Runner:

```text
scripts/run_bms_fu01c_c60_motif_topology_extension.py
```

Config:

```text
data/bms_fu01c_c60_motif_topology_config.yaml
```

Output directory:

```text
runs/BMS-FU01c/c60_motif_topology_extension_open/
```

Run id:

```text
BMS-FU01c_c60_motif_topology_extension_open
```

The run completed cleanly:

```text
warnings: 0
```

---

## 3. Input graph validation

Input graph:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
```

Validation:

```text
input_graph_valid: true
expected_counts_ok: true

node_count: 60
bond_edge_count: 90
face_count: 32

pentagon_count: 12
hexagon_count: 20

degree_counts:
  3: 60

edge_type_counts:
  5_6: 60
  6_6: 30

all_node_degrees_3: true
```

Thus, FU01c was run on the same validated C60 audit object as FU01/FU01b.

---

## 4. Tested representations

FU01c compared three graph representations:

```text
bond_class_weighted
topology_only_equal_weight
graph_distance_similarity_d3
```

Interpretation:

```text
bond_class_weighted:
  FU01/FU01b continuity representation.
  Uses explicit 6:6 / 5:6 weights.

topology_only_equal_weight:
  Removes explicit edge-class weights.
  All C-C bond edges have equal weight.

graph_distance_similarity_d3:
  Builds a relational graph-distance representation using shortest-path
  similarity up to graph distance 3.
```

This is the first FU run where the explicit 6:6 / 5:6 weight distinction is not required for all tested signals.

---

## 5. Core variants and null families

Core variants:

```text
local_6_6_patch_core
distributed_6_6_core
local_5_6_pentagon_boundary_core
distributed_5_6_pentagon_boundary_core
```

Null families:

```text
degree_preserving_rewire
edge_class_shuffle
motif_class_preserving_edge_swap_proxy
core_seeded_decoy
```

Important methodological note:

```text
motif_class_preserving_edge_swap_proxy is a proxy null. It preserves edge-type
rewiring classes, but it is not a true fullerene face-cycle-preserving
randomizer.
```

---

## 6. Row counts

```text
representation_count: 3
core_variant_count: 4
object_count_per_representation: 801

null_family_counts:
  core_seeded_decoy: 200
  degree_preserving_rewire: 200
  edge_class_shuffle: 200
  motif_class_preserving_edge_swap_proxy: 200

row_counts:
  nodes_resolved: 60
  faces: 32
  representations: 3
  core_variants: 4
  reference_core_edges: 48
  edges: 575755
  core_metrics: 101304
  envelope_metrics: 405216
  real_vs_null_summary: 8064
  representation_summary: 12
  core_variant_summary: 48
  null_family_inventory: 800
  warnings: 0
```

---

## 7. Overall summary labels

Across all representations, core variants and null families:

```text
null_reproduces_metric_behavior: 5370
null_reproduces_core_behavior: 1476
real_exceeds_tested_null_family: 853
mixed_family_dependent_result: 285
inconclusive_due_to_scope_or_warnings: 80
```

The run is large and mixed, but the key result is not ambiguous:

```text
Topology-only and graph-distance representations do not collapse.
```

---

## 8. Representation-level result

### 8.1 bond_class_weighted

This is the FU01/FU01b continuity representation.

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 115
  mixed_family_dependent_result: 23
  null_reproduces_core_behavior: 60
  null_reproduces_metric_behavior: 474

edge_class_shuffle:
  real_exceeds_tested_null_family: 49
  mixed_family_dependent_result: 7
  null_reproduces_core_behavior: 117
  null_reproduces_metric_behavior: 499

motif_class_preserving_edge_swap_proxy:
  real_exceeds_tested_null_family: 92
  mixed_family_dependent_result: 15
  null_reproduces_core_behavior: 89
  null_reproduces_metric_behavior: 476

core_seeded_decoy:
  real_exceeds_tested_null_family: 20
  mixed_family_dependent_result: 10
  null_reproduces_core_behavior: 148
  null_reproduces_metric_behavior: 494
```

Interpretation:

```text
The FU01/FU01b weighted signal is reproduced.
Degree-preserving rewires remain strongly separated.
Edge-class shuffle and core-seeded decoy reproduce substantial behavior.
```

---

### 8.2 topology_only_equal_weight

This is the crucial weight-removal test.

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 110
  mixed_family_dependent_result: 38
  null_reproduces_core_behavior: 86
  null_reproduces_metric_behavior: 438

motif_class_preserving_edge_swap_proxy:
  real_exceeds_tested_null_family: 124
  mixed_family_dependent_result: 22
  null_reproduces_core_behavior: 86
  null_reproduces_metric_behavior: 440

edge_class_shuffle:
  real_exceeds_tested_null_family: 9
  mixed_family_dependent_result: 20
  null_reproduces_core_behavior: 168
  null_reproduces_metric_behavior: 475

core_seeded_decoy:
  real_exceeds_tested_null_family: 16
  mixed_family_dependent_result: 17
  null_reproduces_core_behavior: 168
  null_reproduces_metric_behavior: 471
```

Interpretation:

```text
The topology-only equal-weight representation still shows substantial
real-over-null separation against degree-preserving rewires and the
motif-class-preserving edge-swap proxy.
```

Therefore:

```text
The FU01/FU01b signal is not purely driven by explicit 6:6 / 5:6 edge weights.
```

However:

```text
edge_class_shuffle and core_seeded_decoy reproduce much broad core behavior,
and equal-weight constructions are tie-sensitive.
```

Claim boundary:

```text
C60 topology carries detectable structure in this diagnostic beyond degree
regularity, but the result is not yet a global fullerene-symmetry proof.
```

Internal image:

```text
Der Fußball trägt auch ohne farbige Nähte.
Aber die Suchmethoden greifen teilweise an sehr groben Naht-/Core-Haken.
```

---

### 8.3 graph_distance_similarity_d3

Graph-distance representation:

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 135
  mixed_family_dependent_result: 58
  null_reproduces_core_behavior: 110
  null_reproduces_metric_behavior: 349
  inconclusive_due_to_scope_or_warnings: 20

motif_class_preserving_edge_swap_proxy:
  real_exceeds_tested_null_family: 158
  mixed_family_dependent_result: 38
  null_reproduces_core_behavior: 108
  null_reproduces_metric_behavior: 348
  inconclusive_due_to_scope_or_warnings: 20

edge_class_shuffle:
  real_exceeds_tested_null_family: 9
  mixed_family_dependent_result: 20
  null_reproduces_core_behavior: 168
  null_reproduces_metric_behavior: 455
  inconclusive_due_to_scope_or_warnings: 20

core_seeded_decoy:
  real_exceeds_tested_null_family: 16
  mixed_family_dependent_result: 17
  null_reproduces_core_behavior: 168
  null_reproduces_metric_behavior: 451
  inconclusive_due_to_scope_or_warnings: 20
```

Interpretation:

```text
The graph-distance representation is the strongest indication that C60 topology
can be read as relational distance structure.
```

It shows even more real-over-null rows than the bond-class weighted and topology-only variants against topology-perturbing nulls.

Important caveat:

```text
The 80 inconclusive rows occur only in graph_distance_similarity_d3 summaries.
They are scope/metric effects rather than run warnings, because warnings = 0.
They should be inspected before making stronger claims.
```

---

## 9. Strongest topology-only cases

The strongest topology-only real-over-null core cases show large deltas even without 6:6 / 5:6 weight differences.

Representative examples:

```text
topology_only_equal_weight
local_6_6_patch_core
motif_class_preserving_edge_swap_proxy
envelope_core_edge_containment
maximum_spanning_tree abs_weight_mst:
  real = 1.0
  null_mean = 0.003333333333333333
  delta = 0.9966666666666667
  exceedance = 0.0

topology_only_equal_weight
local_6_6_patch_core
degree_preserving_rewire
envelope_core_edge_containment
maximum_spanning_tree abs_weight_mst:
  real = 1.0
  null_mean = 0.01
  delta = 0.99
  exceedance = 0.0

topology_only_equal_weight
distributed_6_6_core
motif_class_preserving_edge_swap_proxy
envelope_core_edge_containment
maximum_spanning_tree abs_weight_mst:
  real = 1.0
  null_mean = 0.011666666666666665
  delta = 0.9883333333333333
  exceedance = 0.0
```

Interpretation:

```text
Even after explicit edge-class weights are removed, the selected C60 core
relations are retained by several real constructions much more strongly than
by topology-perturbed nulls.
```

Caveat:

```text
Equal-weight top-strength, threshold and MST constructions are tie-sensitive.
This means these results should be treated as topology-calibration evidence,
not as final global specificity evidence.
```

---

## 10. Strongest graph-distance cases

Representative graph-distance results:

```text
graph_distance_similarity_d3
local_6_6_patch_core
motif_class_preserving_edge_swap_proxy
envelope_core_edge_containment
maximum_spanning_tree abs_weight_mst:
  real = 1.0
  null_mean = 0.003333333333333333
  delta = 0.9966666666666667
  exceedance = 0.0

graph_distance_similarity_d3
local_6_6_patch_core
degree_preserving_rewire
envelope_core_edge_containment
maximum_spanning_tree abs_weight_mst:
  real = 1.0
  null_mean = 0.01
  delta = 0.99
  exceedance = 0.0

graph_distance_similarity_d3
distributed_6_6_core
motif_class_preserving_edge_swap_proxy
envelope_core_edge_containment
maximum_spanning_tree abs_weight_mst:
  real = 1.0
  null_mean = 0.011666666666666665
  delta = 0.9883333333333333
  exceedance = 0.0
```

Interpretation:

```text
C60 topology is not only visible as direct bond connectivity. It remains
readable in a shortest-path / graph-distance relational representation.
```

This is the most project-relevant part of FU01c, because it is closer to the relational-distance language of the bridge framework.

Internal image:

```text
Nicht nur die direkte Naht zählt.
Auch das Abstandsmuster im Ball trägt.
```

---

## 11. Befund

BMS-FU01c answers the main question in a bounded but positive way.

Befund:

```text
1. The signal does not collapse when explicit 6:6 / 5:6 edge-class weights are
   removed.

2. topology_only_equal_weight still shows substantial real-over-null separation
   against degree-preserving rewires and motif-class-preserving edge-swap
   proxies.

3. graph_distance_similarity_d3 also shows strong real-over-null separation
   against topology-perturbing nulls.

4. edge_class_shuffle and core_seeded_decoy reproduce broad behavior, confirming
   again that broad containment and simple edge-class placement controls are
   insufficient as standalone specificity evidence.

5. The motif_class_preserving_edge_swap_proxy is informative but remains a proxy;
   it does not preserve true C60 face cycles or fullerene validity.
```

Short internal result:

```text
Ohne farbige Nähte sieht der Runner den Fußball immer noch.
Aber wir dürfen noch nicht sagen, dass er die ganze Fußballsymmetrie verstanden hat.
```

---

## 12. Interpretation

Conservative interpretation:

```text
BMS-FU01c supports that the C60 diagnostic signal is not purely edge-class /
weight driven. Topology-only equal-weight and graph-distance representations
retain substantial real-over-null separation against topology-perturbing nulls.
This indicates that C60 connectivity and relational graph-distance structure
carry detectable information in the diagnostic. However, edge-class shuffles,
core-seeded decoys, tie-sensitive constructions and the proxy status of the
motif-preserving null constrain the result to a controlled topology-calibration
claim, not a global fullerene-symmetry recovery claim.
```

Short version:

```text
FU01c supports topology-sensitive C60 structure information beyond explicit
6:6 / 5:6 weights, with strong methodological boundaries.
```

---

## 13. Relation to FU01/FU01b

FU01:

```text
A local 6:6 seam was detected beyond degree-preserving rewires.
```

FU01b:

```text
The result was not limited to that one seam; other local and distributed 6:6 /
5:6 core selections also carried signal.
```

FU01c:

```text
The signal does not collapse after removing explicit 6:6 / 5:6 edge weights.
Topology-only and graph-distance variants remain informative.
```

Upgrade in interpretation:

```text
From edge-class/motif sensitivity:
  C60 seams carry.

To topology-sensitive calibration:
  C60 connectivity and graph-distance structure also carry.
```

Still not allowed:

```text
global fullerene symmetry has been fully recovered.
```

---

## 14. Relation to broader QSB language

FU01c is project-relevant because the graph-distance representation begins to resemble the bridge language more closely:

```text
not just a bond edge,
but a relational distance pattern over the structure.
```

Project-facing cautious statement:

```text
In the controlled C60 calibration object, structure remains detectable not only
through explicit edge-class weights, but also through topology-only and
shortest-path relational representations. This supports the diagnostic as
sensitive to relational connectivity patterns, while leaving physical
interpretation strictly open.
```

Internal image:

```text
Die Bridge riecht nicht nur an der farbigen Naht.
Sie sieht ein Stück vom Beziehungsmuster des Balls.
```

---

## 15. Open gaps

1. Equal-weight top-strength, threshold and MST constructions are tie-sensitive.  
   FU01c results should therefore be interpreted as calibration evidence, not as final specificity proof.

2. The motif_class_preserving_edge_swap_proxy is not a true fullerene-preserving randomizer.  
   It preserves edge-type rewiring class but not planarity, face cycles or fullerene validity.

3. Graph-distance representation produced 80 inconclusive summary rows despite zero warnings.  
   These are likely metric/scope cases and should be inspected before stronger claims.

4. The current graph-distance variant uses max distance 3.  
   A full all-pairs variant or sweep over max distance should be tested.

5. Current readouts still emphasize core containment.  
   More global readouts should be added before claiming cage-level organization.

6. A true face-cycle-preserving or fullerene-family decoy is still missing.

---

## 16. Recommended next block

Recommended next block:

```text
BMS-FU01d — C60 Global Cage Readouts and Fullerene-Preserving Controls
```

Purpose:

```text
Move beyond core containment toward global cage-level organization.
```

Recommended additions:

```text
1. full all-pairs graph-distance representation
2. max_graph_distance sweep: 2, 3, 4, full
3. global cycle readouts:
   - 5-cycle proxy
   - 6-cycle proxy
   - face-boundary retention
4. cage-shell readouts:
   - distance-shell overlap
   - Laplacian-spectrum comparison
   - shortest-path distribution retention
5. stronger nulls:
   - fullerene-like decoy if feasible
   - face-cycle preserving proxy
   - planar/cubic graph controls where available
```

Decision logic:

```text
If topology-only and graph-distance signals persist under stronger global
controls:
  the diagnostic may be sensitive to broader cage organization.

If stronger controls reproduce the signal:
  FU01c should be interpreted as topology/local-motif calibration rather than
  global cage specificity.
```

---

## 17. Claim boundary

Allowed:

```text
BMS-FU01c shows that the C60 signal does not collapse when explicit 6:6 / 5:6
edge weights are removed. Topology-only equal-weight and graph-distance
representations retain real-over-null separation against topology-perturbing
nulls.
```

Allowed, shorter:

```text
BMS-FU01c supports topology-sensitive C60 structure information beyond explicit
edge-class weights, with strong methodological boundaries.
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

## 18. Minimal commit plan

Commit FU01c implementation and result note deliberately:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU01C_C60_MOTIF_TOPOLOGY_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_INITIAL_RESULT_NOTE.md

git add \
  data/bms_fu01c_c60_motif_topology_config.yaml \
  scripts/run_bms_fu01c_c60_motif_topology_extension.py \
  docs/BMS_FU01C_RUNNER_FIELD_LIST.md \
  docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_EXTENSION_SPEC.md \
  docs/BMS_FU01C_C60_MOTIF_TOPOLOGY_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU01c C60 motif topology extension diagnostic"

git push
```

Run outputs should only be committed deliberately after checking file size and repository policy.

---

## 19. Internal summary

```text
FU01:
  Eine Naht war echt.

FU01b:
  Andere Nähte tragen auch.

FU01c:
  Ohne farbige Nähte trägt der Ball immer noch.

Grenze:
  Noch kein globaler Symmetriebeweis.
  Aber: topology-sensitive calibration survives.
```
