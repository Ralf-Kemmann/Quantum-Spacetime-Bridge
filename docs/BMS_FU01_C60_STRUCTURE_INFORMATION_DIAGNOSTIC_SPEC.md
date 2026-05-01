# BMS-FU01 — C60 Structure Information Diagnostic Specification

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU01_C60_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md`  
Status: Specification only; no numerical run completed yet

---

## 1. Purpose

BMS-FU01 introduces C60 / fullerene-like structure as a controlled symmetry and structure-information diagnostic.

The goal is not to use C60 as a chemical claim about emergent spacetime. The goal is methodological:

```text
Can the current structure-information diagnostic distinguish
simple local graph regularity, chemically meaningful edge classes,
local ring motifs, and global fullerene-like organization?
```

Internal working image:

```text
ST01 war Gelände.
C60 ist Eichkörper.
```

BMS-ST01 tested structure information using the existing RING / CAVITY / MEMBRANE relational structure graph. That run showed:

```text
Structure carries something.
But family carries a lot with it.
```

BMS-FU01 should now use a deliberately controlled graph object where the expected structure is known in advance.

C60 is suitable because it separates several levels of structure:

```text
1. local regularity:
   every carbon node has degree 3

2. edge-class structure:
   different bond classes, e.g. 5:6 and 6:6 edges

3. local ring motifs:
   pentagons and hexagons

4. global fullerene organization:
   truncated-icosahedral connectivity / cage architecture
```

The diagnostic asks which of these levels the current BMC-15h / ST01-style pipeline can actually see.

---

## 2. Relation to prior blocks

### BMC-15h

BMC-15h showed:

```text
Broad containment is cheap.
Selective local embedding is more informative.
Core-seeded decoys reveal which readouts are easy to fake.
```

### BMS-IS01

BMS-IS01 showed:

```text
same-isotope cross-run stability core
strong edge-containment signal
cheap node containment
```

### BMS-IS01b

BMS-IS01b showed:

```text
once same-isotope cross-run links are removed,
family-balanced isotope-order cores are often reproduced by nulls.
```

### BMS-ST01

BMS-ST01 showed:

```text
interpretable within-family spectral/mode neighborhoods
real graph often exceeds degree-/weight-preserving rewires
feature-structured and seeded controls reproduce substantial behavior
```

### BMS-FU01

BMS-FU01 now introduces a controlled structural calibration object.

It asks:

```text
Does the diagnostic recover known graph-structural organization when the
target object is not a noisy external feature table but a deliberately
structured fullerene graph?
```

---

## 3. Working question

Main question:

```text
Can a BMC-15h/ST01-style structure-information diagnostic distinguish
C60-specific local motif and edge-class organization from simple degree-3
regularity?
```

Sub-questions:

```text
1. Does the real C60 graph exceed degree-preserving rewires?

2. Does the real graph exceed edge-class shuffles that preserve the number
   of 5:6 and 6:6 edges but destroy their placement?

3. Does the real graph exceed motif-preserving partial controls?

4. Is the signal mostly local ring-motif structure, or does it also require
   global fullerene-like organization?

5. Which readouts are informative:
   edge containment,
   node containment,
   edge-class purity,
   ring-motif consistency,
   graph-distance shell preservation,
   or local embedding robustness?
```

---

## 4. Recommended block label

```text
BMS-FU01
```

Meaning:

```text
BMS = Bridge-readable Matter / Structure
FU  = Fullerene
01  = first controlled fullerene structure-information diagnostic
```

Recommended output directory:

```text
runs/BMS-FU01/c60_structure_information_open/
```

Recommended repo files:

```text
docs/BMS_FU01_C60_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md
docs/BMS_FU01_RUNNER_FIELD_LIST.md
docs/BMS_FU01_C60_STRUCTURE_INFORMATION_RESULT_NOTE.md

data/bms_fu01_c60_structure_config.yaml
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv

scripts/build_bms_fu01_c60_graph.py
scripts/run_bms_fu01_c60_structure_information.py
```

---

## 5. C60 graph object

Recommended canonical representation:

```text
nodes:
  60 carbon nodes

edges:
  90 graph edges / C-C bonds

faces:
  12 pentagons
  20 hexagons
```

C60 can be represented as a truncated-icosahedral graph.

For BMS-FU01, the graph should be treated as a topological / structural reference graph, not as a quantum-chemical calculation.

Required node fields:

| field name | type | description |
|---|---:|---|
| `node_id` | string | Stable carbon-node id, e.g. `c60_001`. |
| `element_symbol` | string | Usually `C`. |
| `degree` | integer | Graph degree; expected 3 for all C60 nodes. |
| `pentagon_membership_count` | integer | Number of pentagonal faces containing the node. |
| `hexagon_membership_count` | integer | Number of hexagonal faces containing the node. |
| `local_face_signature` | string | Compact local motif signature, e.g. `P1_H2`. |
| `orbit_label` | string | Optional symmetry orbit label if available. |
| `notes` | string | Provenance and construction notes. |

Required edge fields:

| field name | type | description |
|---|---:|---|
| `source` | string | Source node id. |
| `target` | string | Target node id. |
| `edge_type` | string | Edge class, e.g. `5_6` or `6_6`. |
| `source_degree` | integer | Source degree. |
| `target_degree` | integer | Target degree. |
| `shared_face_count` | integer | Number of faces containing this edge. |
| `shared_face_types` | string | Face types adjacent to the edge, e.g. `P,H` or `H,H`. |
| `weight` | float | Structural similarity / bond weight used by diagnostic. |
| `distance` | float | Derived or assigned distance proxy. |
| `comment` | string | Methodological note. |

Required face fields:

| field name | type | description |
|---|---:|---|
| `face_id` | string | Stable face id. |
| `face_type` | string | `pentagon` or `hexagon`. |
| `node_ids` | string | Semicolon-separated ordered or unordered node ids. |
| `edge_ids` | string | Semicolon-separated edge ids if available. |
| `notes` | string | Construction note. |

---

## 6. Edge weights

BMS-FU01 should start with deliberately simple structural weights.

Recommended first-pass weight assignment:

```text
6:6 edge weight > 5:6 edge weight
```

Example:

```yaml
edge_weights:
  edge_type_6_6: 1.00
  edge_type_5_6: 0.85
```

Rationale:

```text
The first diagnostic should test whether edge-class placement and ring motif
structure are retained under null controls. It should not depend on an
unvalidated quantum-chemical bond-length or bond-order model.
```

Optional later variants:

```text
equal_weight_topology_only:
  all C-C graph edges weight = 1.0

bond_class_weighted:
  6:6 and 5:6 classes assigned distinct weights

distance_shell_weighted:
  graph-distance similarity between all node pairs, not only bonded edges

spectral_embedding_weighted:
  edge/node similarities derived from graph Laplacian eigenstructure
```

Recommended FU01-v0:

```text
bond_class_weighted C60 graph only
```

---

## 7. Reference-core definitions

BMS-FU01 should not use a single reference-core rule only. C60 is useful precisely because several structural cores can be tested.

### Core A — edge-class core

```yaml
reference_core:
  mode: "top_edge_class_core"
  edge_type_priority: ["6_6", "5_6"]
  edge_count: 12
```

Purpose:

```text
Tests whether high-priority edge-class placement is retained.
```

### Core B — pentagon-neighborhood core

```yaml
reference_core:
  mode: "pentagon_neighborhood_core"
  face_count: 3
  include_boundary_edges: true
```

Purpose:

```text
Tests local ring-motif retention.
```

### Core C — graph-distance shell core

```yaml
reference_core:
  mode: "distance_shell_core"
  anchor_nodes: ["auto_high_symmetry"]
  shell_depth: 2
```

Purpose:

```text
Tests local embedding around selected anchor nodes.
```

Recommended FU01-v0:

```text
Core A: edge-class core
Core B: pentagon-neighborhood core
```

If implementation time is limited, start with Core A only.

---

## 8. Null families

BMS-FU01 should use null families that target different structure levels.

### 8.1 Degree-preserving rewire

```text
Preserve node degree sequence.
Destroy ring motifs and fullerene organization.
```

Purpose:

```text
Tests whether the diagnostic sees more than degree-3 regularity.
```

Expected result if diagnostic is useful:

```text
Real C60 should exceed degree-preserving rewires for motif-sensitive readouts.
```

### 8.2 Edge-class shuffle

```text
Preserve the number of 5:6 and 6:6 edges.
Shuffle edge-type labels over the same topology.
```

Purpose:

```text
Tests whether edge-class placement matters, not only edge-class count.
```

### 8.3 Face-motif preserving partial shuffle

```text
Preserve local pentagon/hexagon membership counts approximately.
Perturb global arrangement.
```

Purpose:

```text
Separates local motif information from global cage organization.
```

### 8.4 Core-seeded decoy

```text
Insert a small high-weight motif/core into a null graph.
```

Purpose:

```text
Tests whether the selected core is cheaply reproducible.
```

### 8.5 Fullerene-like decoy family, optional later

```text
Use other 3-regular planar / fullerene-like graphs if available.
```

Purpose:

```text
Tests specificity against related cage architectures rather than generic
degree-preserving rewires.
```

---

## 9. Construction families

BMS-FU01 should use graph-aware construction families.

Recommended first pass:

```yaml
construction_families:
  top_strength:
    enabled: true
    edge_counts: [12, 20, 30, 45, 60, 90]

  threshold:
    enabled: true
    thresholds: [0.80, 0.85, 0.90, 0.95, 1.00]

  mutual_knn:
    enabled: true
    k_values: [2, 3, 4, 6]

  maximum_spanning_tree:
    enabled: true

  graph_distance_shells:
    enabled: true
    shell_depths: [1, 2, 3]
```

For topology-only variants, threshold may become uninformative if many weights are equal. That should be reported as a warning or interpreted as a known limitation.

---

## 10. Metrics

Use the standard BMC-15h/ST01 metrics:

```text
envelope_core_edge_containment
envelope_core_node_containment
real_minus_null_mean
empirical_exceedance_fraction
interpretation_label
```

Add C60-specific metrics:

```text
edge_type_retention
pentagon_edge_fraction
hexagon_edge_fraction
face_boundary_consistency
degree_sequence_validity
cycle_5_count_proxy
cycle_6_count_proxy
local_face_signature_retention
graph_distance_shell_retention
```

Recommended first implementation metrics:

| field name | type | description |
|---|---:|---|
| `envelope_core_edge_containment` | float | Fraction of reference-core edges recovered. |
| `envelope_core_node_containment` | float | Fraction of reference-core nodes recovered. |
| `edge_type_6_6_fraction` | float | Fraction of selected edges that are 6:6 edges. |
| `edge_type_5_6_fraction` | float | Fraction of selected edges that are 5:6 edges. |
| `within_face_boundary_fraction` | float | Fraction of selected edges that lie on known face boundaries. |
| `degree_sequence_validity` | float | Fraction or boolean indicating whether degree sequence is preserved. |

---

## 11. Expected interpretation patterns

### Pattern A — real exceeds degree-preserving rewires

```text
The diagnostic sees more than degree-3 regularity.
```

Allowed interpretation:

```text
C60-specific motif or edge-placement information survives beyond degree
sequence alone.
```

### Pattern B — real exceeds edge-class shuffle

```text
Edge-class placement matters, not only edge-class count.
```

Allowed interpretation:

```text
The diagnostic is sensitive to the relational placement of 5:6 and 6:6
classes.
```

### Pattern C — motif-preserving null reproduces behavior

```text
The signal is mostly local motif structure.
```

Allowed interpretation:

```text
The readout is local-motif sensitive but not yet a global fullerene-architecture
specificity marker.
```

### Pattern D — motif-preserving null fails

```text
The signal may depend on global fullerene arrangement.
```

Allowed interpretation:

```text
This would support a stronger construction-qualified indication of global
cage organization, subject to more controls.
```

### Pattern E — core-seeded decoy reproduces broad readouts

```text
Broad containment is cheap.
```

Allowed interpretation:

```text
Only selective local readouts should be treated as informative.
```

---

## 12. Claim boundary

Allowed:

```text
BMS-FU01 tests whether the structure-information diagnostic can distinguish
degree regularity, edge-class organization, local ring motifs, and global
fullerene-like connectivity in a controlled C60 graph.
```

Allowed after positive result:

```text
BMS-FU01 supports a construction-qualified indication that the diagnostic is
sensitive to known C60 structural organization beyond simple degree
regularity.
```

Allowed after null reproduction:

```text
BMS-FU01 shows that the tested readout is reproduced by controlled nulls and
should not be interpreted as a standalone structure-specificity marker.
```

Not allowed:

```text
C60 proves emergent spacetime.
The bridge recognizes molecules.
Fullerene symmetry is physically encoded in spacetime by this test.
A physical metric has been recovered.
Quantum chemistry has been reproduced.
```

---

## 13. Minimal implementation plan

### Step 1 — build canonical C60 graph files

Create:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
```

Script:

```text
scripts/build_bms_fu01_c60_graph.py
```

The builder should either:

```text
A. use an explicitly embedded audited C60 adjacency / face list, or
B. construct the truncated-icosahedral graph algorithmically and validate counts.
```

Validation checks:

```text
node_count == 60
edge_count == 90
pentagon_count == 12
hexagon_count == 20
all node degrees == 3
edge_type counts reported
warnings == 0
```

### Step 2 — run structure diagnostic

Create:

```text
data/bms_fu01_c60_structure_config.yaml
scripts/run_bms_fu01_c60_structure_information.py
docs/BMS_FU01_RUNNER_FIELD_LIST.md
```

Output directory:

```text
runs/BMS-FU01/c60_structure_information_open/
```

Expected outputs:

```text
bms_fu01_nodes_resolved.csv
bms_fu01_edges.csv
bms_fu01_faces.csv
bms_fu01_reference_core_edges.csv
bms_fu01_core_metrics.csv
bms_fu01_envelope_metrics.csv
bms_fu01_real_vs_null_summary.csv
bms_fu01_null_family_inventory.csv
bms_fu01_run_manifest.json
bms_fu01_warnings.json
bms_fu01_config_resolved.yaml
```

### Step 3 — result note

Create:

```text
docs/BMS_FU01_C60_STRUCTURE_INFORMATION_RESULT_NOTE.md
```

Use structure:

```text
Befund
Interpretation
Hypothesis
Open gap
Claim boundary
Next diagnostic
```

---

## 14. Recommended immediate next action

Create only the specification first:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU01_C60_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md \
  docs/BMS_FU01_C60_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md

git status --short
```

Then commit:

```bash
git add docs/BMS_FU01_C60_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md

git status --short

git commit -m "Add BMS-FU01 C60 structure diagnostic specification"

git push
```

Do not implement before deciding whether the C60 graph will be embedded as an audited adjacency/face list or generated algorithmically.

---

## 15. Internal summary

```text
BMS-ST01 tested structure in a real/proxy data graph.

BMS-FU01 tests structure in a controlled symmetry object.

If ST01 was terrain, C60 is a calibration crystal.
```
