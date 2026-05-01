# BMS-FU01b — C60 Core Selection Sensitivity Initial Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU01B_C60_CORE_SELECTION_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU01b C60 core-selection sensitivity diagnostic

---

## 1. Purpose

BMS-FU01b extends BMS-FU01 by testing whether the C60 diagnostic result depends on a single deterministic local 6:6 reference-core patch.

Working question:

```text
Ist FU01 nur eine lokale Nahtstelle,
oder trägt die C60-Struktur auch bei anders gewählten Core-Schnitten?
```

Scientific working question:

```text
Does the BMS-FU01 C60 signal depend on the deterministic local 6:6 reference-core patch,
or does comparable real-over-null separation persist under alternative local and
distributed 6:6 / 5:6 core selections?
```

Internal image:

```text
FU01 hat eine Naht am Fußball gefunden.
FU01b prüft, ob auch andere Nähte tragen.
```

---

## 2. Run context

Runner:

```text
scripts/run_bms_fu01b_c60_core_selection_sensitivity.py
```

Config:

```text
data/bms_fu01b_c60_core_selection_config.yaml
```

Output directory:

```text
runs/BMS-FU01b/c60_core_selection_sensitivity_open/
```

Run id:

```text
BMS-FU01b_c60_core_selection_sensitivity_open
```

The run completed cleanly:

```text
warnings: 0
```

---

## 3. Input validation

Input graph:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
```

Input graph validity:

```text
input_graph_valid: true
expected_counts_ok: true
```

Loaded graph validation:

```text
node_count: 60
edge_count: 90
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

Thus, FU01b was run on the same valid C60 audit object as FU01.

---

## 4. Core variants

FU01b evaluated four reference-core variants:

```text
local_6_6_patch_core
distributed_6_6_core
local_5_6_pentagon_boundary_core
distributed_5_6_pentagon_boundary_core
```

Interpretation of variants:

```text
local_6_6_patch_core:
  FU01-v0 continuity core; local H-H seam.

distributed_6_6_core:
  6:6 H-H edges distributed across the sorted 6:6 edge list.

local_5_6_pentagon_boundary_core:
  local 5:6 pentagon-boundary core.

distributed_5_6_pentagon_boundary_core:
  5:6 pentagon-boundary edges distributed across the sorted 5:6 edge list.
```

---

## 5. Row counts

```text
core_variant_count: 4
reference_core_edge_count_total: 48

null_family_counts:
  core_seeded_decoy:        200
  degree_preserving_rewire: 200
  edge_class_shuffle:       200

object_count: 601

row_counts:
  nodes_resolved:             60
  faces:                      32
  core_variants:               4
  reference_core_edges:       48
  edges:                   54360
  core_metrics:            22952
  envelope_metrics:        57380
  real_vs_null_summary:     1140
  core_variant_summary:       12
  null_family_inventory:     600
  warnings:                    0
```

---

## 6. Overall summary labels

Across all core variants and null families:

```text
null_reproduces_metric_behavior: 640
null_reproduces_core_behavior:   286
real_exceeds_tested_null_family: 176
mixed_family_dependent_result:    38
```

This is a mixed but highly informative calibration result.

It shows:

```text
1. The real graph often exceeds tested nulls in core-relevant cases.
2. Many broad metrics remain reproducible.
3. Core-seeded decoys correctly expose broad containment as cheap.
```

---

## 7. Result by core variant and null family

### 7.1 local_6_6_patch_core

This is the FU01-v0 continuity core.

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 32
  mixed_family_dependent_result: 3
  null_reproduces_core_behavior: 10
  null_reproduces_metric_behavior: 50

edge_class_shuffle:
  real_exceeds_tested_null_family: 16
  mixed_family_dependent_result: 2
  null_reproduces_core_behavior: 22
  null_reproduces_metric_behavior: 55

core_seeded_decoy:
  real_exceeds_tested_null_family: 2
  mixed_family_dependent_result: 2
  null_reproduces_core_behavior: 38
  null_reproduces_metric_behavior: 53
```

Interpretation:

```text
The original FU01 local 6:6 patch result is reproduced.
It remains strongly separated from degree-preserving rewires.
It is partially reproduced by edge-class shuffles and largely reproduced by
core-seeded decoys.
```

---

### 7.2 distributed_6_6_core

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 28
  mixed_family_dependent_result: 7
  null_reproduces_core_behavior: 10
  null_reproduces_metric_behavior: 50

edge_class_shuffle:
  real_exceeds_tested_null_family: 18
  mixed_family_dependent_result: 3
  null_reproduces_core_behavior: 19
  null_reproduces_metric_behavior: 55

core_seeded_decoy:
  real_exceeds_tested_null_family: 0
  mixed_family_dependent_result: 3
  null_reproduces_core_behavior: 36
  null_reproduces_metric_behavior: 56
```

Interpretation:

```text
The distributed 6:6 core behaves similarly to the local 6:6 patch.
This weakens the concern that FU01-v0 was only an artifact of the first sorted
local patch.
```

The 6:6 signal is not purely local. It persists under a distributed 6:6 core selection.

---

### 7.3 local_5_6_pentagon_boundary_core

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 24
  mixed_family_dependent_result: 4
  null_reproduces_core_behavior: 17
  null_reproduces_metric_behavior: 50

edge_class_shuffle:
  real_exceeds_tested_null_family: 7
  mixed_family_dependent_result: 1
  null_reproduces_core_behavior: 31
  null_reproduces_metric_behavior: 56

core_seeded_decoy:
  real_exceeds_tested_null_family: 9
  mixed_family_dependent_result: 2
  null_reproduces_core_behavior: 31
  null_reproduces_metric_behavior: 53
```

Interpretation:

```text
The local 5:6 pentagon-boundary core also exceeds degree-preserving rewires,
but edge-class shuffles reproduce more of its behavior than for the 6:6 cores.
```

This suggests that 5:6 pentagon-boundary information is visible, but more strongly entangled with edge-class count / placement controls.

---

### 7.4 distributed_5_6_pentagon_boundary_core

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 21
  mixed_family_dependent_result: 8
  null_reproduces_core_behavior: 16
  null_reproduces_metric_behavior: 50

edge_class_shuffle:
  real_exceeds_tested_null_family: 9
  mixed_family_dependent_result: 1
  null_reproduces_core_behavior: 29
  null_reproduces_metric_behavior: 56

core_seeded_decoy:
  real_exceeds_tested_null_family: 10
  mixed_family_dependent_result: 2
  null_reproduces_core_behavior: 27
  null_reproduces_metric_behavior: 56
```

Interpretation:

```text
Distributed 5:6 pentagon-boundary structure remains visible against degree
rewires, but it is less selectively separated than the 6:6 cases.
```

---

## 8. Strongest real-over-null cases

The strongest real-over-null core cases are dominated by degree-preserving rewires, with large positive deltas and zero empirical exceedance.

Representative examples:

```text
local_5_6_pentagon_boundary_core
degree_preserving_rewire
envelope_core_edge_containment
graph_distance_shells shell_depth_3:
  real = 1.0
  null_mean = 0.01
  delta = 0.99
  exceedance = 0.0

distributed_6_6_core
degree_preserving_rewire
envelope_core_edge_containment
threshold abs_weight_ge_0.9:
  real = 1.0
  null_mean = 0.013333333333333332
  delta = 0.9866666666666667
  exceedance = 0.0

local_6_6_patch_core
degree_preserving_rewire
envelope_core_edge_containment
mutual_knn k_2:
  real = 1.0
  null_mean = 0.018333333333333333
  delta = 0.9816666666666667
  exceedance = 0.0

distributed_5_6_pentagon_boundary_core
degree_preserving_rewire
envelope_core_edge_containment
mutual_knn k_3:
  real = 1.0
  null_mean = 0.04333333333333333
  delta = 0.9566666666666667
  exceedance = 0.0
```

Main conclusion:

```text
All tested core families show strong degree-rewire resistance in at least some
selective core-edge containment constructions.
```

---

## 9. Befund

BMS-FU01b answers the main question in a useful, bounded way.

Befund:

```text
1. FU01 is not only a single local seam artifact.
   The distributed 6:6 core also shows strong real-over-null separation against
   degree-preserving rewires.

2. Both 6:6 and 5:6 core classes carry detectable C60 structure beyond simple
   degree-3 regularity.

3. The 6:6 cores appear more selectively separated than the 5:6 pentagon-boundary
   cores under edge-class shuffle controls.

4. Core-seeded decoys reproduce much broad core behavior, confirming again that
   broad containment is cheap and not sufficient as standalone specificity
   evidence.

5. The result is therefore not a global fullerene-symmetry proof, but it is a
   stronger calibration than FU01-v0: the signal persists across alternative
   C60 core cuts.
```

Short internal version:

```text
Es war nicht nur die eine Naht.
Andere Nähte tragen auch.
Aber wenn man die Naht künstlich einnäht, finden grobe Sucher sie natürlich.
```

---

## 10. Interpretation

Conservative interpretation:

```text
BMS-FU01b supports that the C60 structure-information diagnostic is not merely
an artifact of the initial deterministic local 6:6 patch core. Comparable
degree-rewire-resistant behavior appears for distributed 6:6 and for 5:6
pentagon-boundary cores. At the same time, edge-class shuffles and core-seeded
decoys reproduce substantial parts of the behavior, so the result should be
interpreted as controlled local/edge-class structural sensitivity, not as a
standalone global fullerene-symmetry diagnostic.
```

Even shorter:

```text
FU01b supports robust C60 edge-class/motif sensitivity beyond degree regularity,
with strong decoy-aware limitations.
```

---

## 11. Relation to FU01

FU01-v0:

```text
Detected a local 6:6 H-H patch beyond degree-preserving rewires.
```

FU01b:

```text
Shows that the result is not restricted to that one local patch.
Distributed 6:6 and 5:6 cores also produce real-over-null separation against
degree-preserving rewires.
```

Thus, FU01b upgrades the FU01 interpretation from:

```text
local 6:6 seam calibration
```

to:

```text
core-selection-sensitive but not single-patch-dependent C60 structure calibration
```

Still not allowed:

```text
global fullerene symmetry has been proven as a recovered physical geometry
```

---

## 12. Relation to BMS-ST01

BMS-ST01 on RING/CAVITY/MEMBRANE showed:

```text
Structure carries something,
but family carries a lot with it.
```

FU01/FU01b now provide a cleaner calibration object:

```text
Known C60 graph
known degree sequence
known edge classes
known face counts
controlled core variants
```

Combined lesson:

```text
The diagnostic is capable of detecting known controlled structure beyond
simple graph regularity. In noisier/proxy datasets, however, family structure
and seeded controls remain major interpretation boundaries.
```

Internal phrasing:

```text
ST01 war Gelände.
FU01/FU01b sind Eichkörper und Nahttest am Modellball.
```

---

## 13. Hypothesis

Working hypothesis:

```text
The current diagnostic is sensitive to C60 edge-class and local motif placement
beyond degree regularity. The signal is not confined to one deterministic local
6:6 patch, but it is also not yet isolated as global cage-symmetry information.
```

More precise hypothesis:

```text
Degree-preserving rewires destroy the C60-specific local edge-class/motif
organization. Edge-class shuffles preserve enough class-level information to
reproduce substantial behavior. Core-seeded decoys show that broad
core-containment readouts are insufficient without decoy-resistant selectivity.
```

---

## 14. Open gaps

1. FU01b still uses two structural edge weights:
   ```text
   6:6 = 1.00
   5:6 = 0.85
   ```
   This is valid for controlled calibration but not a quantum-chemical bond-order model.

2. Threshold and top-strength constructions remain strongly tied to the two-weight setup.

3. A motif-preserving null family is still missing.

4. FU01b tests edge-class and core-selection robustness, but not yet global fullerene cage organization.

5. A topology-only equal-weight variant is needed to separate pure connectivity from edge-weight/class effects.

6. A graph-distance / all-pairs similarity variant could test whether C60 structure appears beyond bonded-edge-only representations.

---

## 15. Recommended next block

Recommended next block:

```text
BMS-FU01c — C60 Motif-Preserving Null and Topology-Only Extension
```

Purpose:

```text
Separate local edge-class/motif sensitivity from global fullerene cage
organization.
```

Recommended additions:

```text
1. motif-preserving null family:
   preserve local pentagon/hexagon face participation while perturbing global
   arrangement.

2. topology-only equal-weight C60 variant:
   all C-C graph edges weight = 1.0.

3. graph-distance all-pairs similarity variant:
   build pairwise similarity from shortest-path distance or Laplacian embedding.

4. face-cycle readouts:
   cycle-5 / cycle-6 retention proxies.

5. compare local vs distributed cores again under topology-only and
   motif-preserving settings.
```

Decision logic:

```text
If motif-preserving nulls reproduce the real graph:
  FU01/FU01b mainly detect local motif/edge-class structure.

If the real graph still exceeds motif-preserving nulls:
  the diagnostic may be sensitive to broader cage organization.

If topology-only equal-weight variants still show separation:
  pure connectivity carries structure without edge-class weights.

If topology-only variants collapse:
  current signal is mainly edge-class/weight driven.
```

---

## 16. Claim boundary

Allowed:

```text
BMS-FU01b shows that the C60 result is not merely an artifact of one deterministic
local 6:6 patch core. Alternative local and distributed 6:6 / 5:6 core selections
also show real-over-null separation against degree-preserving rewires.
```

Allowed, shorter:

```text
BMS-FU01b supports robust C60 edge-class/motif sensitivity beyond degree
regularity, with strong decoy-aware limitations.
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

## 17. Minimal commit plan

Commit FU01b implementation/result note deliberately:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU01B_C60_CORE_SELECTION_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU01B_C60_CORE_SELECTION_INITIAL_RESULT_NOTE.md

git add \
  data/bms_fu01b_c60_core_selection_config.yaml \
  scripts/run_bms_fu01b_c60_core_selection_sensitivity.py \
  docs/BMS_FU01B_RUNNER_FIELD_LIST.md \
  docs/BMS_FU01B_C60_CORE_SELECTION_SENSITIVITY_SPEC.md \
  docs/BMS_FU01B_C60_CORE_SELECTION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU01b C60 core selection sensitivity diagnostic"

git push
```

Run outputs should only be committed deliberately after checking size and repository policy.

---

## 18. Internal summary

```text
FU01:
  Eine echte lokale 6:6-Naht wurde gefunden.

FU01b:
  Es war nicht nur diese eine Naht.
  Andere 6:6- und 5:6-Schnitte tragen ebenfalls gegen Degree-Rewire.

Grenze:
  Edge-class shuffles und Core-Seeding bauen viel nach.
  Also: Strukturkalibrierung ja, globaler Symmetriebeweis nein.
```
