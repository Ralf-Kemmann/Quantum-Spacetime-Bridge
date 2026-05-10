# BMS-FU02g1 — Structure Inventory Builder Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02g1-v0

---

## 1. Purpose

BMS-FU02g1 builds the first graph/cell inventory for the real-structure memory
and symmetry-control program introduced in BMS-FU02g0.

Scope:

```text
Inventory only.
No carrier diagnostic.
No symmetry proof.
No chemistry or electronic-structure claim.
```

Internal purpose:

```text
Wir bauen die Prüfkörper.
Noch keine Diagnose.
Noch kein Claim.
```

---

## 2. Smoke-test result

The runner completed successfully.

Overall warning count:

```text
WARNINGS: 0
```

All four structures passed the runner's minimal validation:

```text
c60_reference:
  validation: valid

graphene_patch:
  validation: valid

nanotube_armchair:
  validation: valid

nanotube_zigzag:
  validation: valid
```

Important:

```text
The validation here is syntactic graph/cell validation only:
  node_count > 0
  edge_count > 0
  cell_count > 0
  edges reference valid nodes
  cells reference valid nodes
```

It is not yet a physical or crystallographic validation of generated nanotube
geometry.

---

## 3. Structure manifests

### 3.1 C60 reference

```text
validation: valid
degree_histogram: {'3': 60}
cell_type_counts: {'hexagon': 20, 'pentagon': 12}
boundary_nodes: 0
boundary_edges: 0
```

Interpretation:

```text
The normalized C60 reference is consistent with the known FU01/FU02 reference:
60 degree-3 nodes, 20 hexagons, 12 pentagons, no boundary.
```

This is the strongest and most reliable inventory object in FU02g1-v0 because
it is normalized from the already validated C60 project artifacts.

Allowed statement:

```text
The C60 reference inventory is valid and preserves the expected closed
fullerene graph/cell structure.
```

---

### 3.2 Graphene patch

```text
validation: valid
degree_histogram: {'2': 20, '3': 38}
cell_type_counts: {'hexagon': 20}
boundary_nodes: 20
boundary_edges: 34
```

Interpretation:

```text
The generated graphene patch is a finite open hexagonal graph/cell control.
It contains only hexagonal cells and explicit boundary nodes/edges.
```

This is methodologically useful as a flat/open boundary control.

Important caveat:

```text
Boundary effects are strong and must be tracked explicitly in later FU02g2
carrier diagnostics.
```

Allowed statement:

```text
The graphene patch provides a valid finite flat/open hexagonal Prüfkörper with
explicit boundary structure.
```

---

### 3.3 Armchair nanotube control

```text
validation: valid
degree_histogram: {'2': 20, '3': 72, '4': 8}
cell_type_counts: {'hexagon': 40}
boundary_nodes: 20
boundary_edges: 48
```

Interpretation:

```text
The armchair nanotube control is syntactically valid, but the degree histogram
contains 8 degree-4 nodes.
```

For an ideal carbon nanotube graph, degree-4 nodes are not expected.

Therefore:

```text
The FU02g1-v0 armchair nanotube should be treated as a provisional cylindrical
graph-control export, not yet as an acceptable ideal nanotube graph.
```

Likely issue:

```text
The simple wrapping/deduplication rule can create over-identifications at the
periodic seam, producing degree-4 nodes.
```

Required follow-up:

```text
Repair nanotube generator before using nanotube outputs in carrier specificity
diagnostics.
```

Allowed statement:

```text
The armchair control was generated and validated syntactically, but its degree
histogram indicates a topology-generation issue that requires repair before
FU02g2.
```

---

### 3.4 Zigzag nanotube control

```text
validation: valid
degree_histogram: {'2': 84, '3': 84}
cell_type_counts: {'hexagon': 42}
boundary_nodes: 84
boundary_edges: 168
```

Interpretation:

```text
The zigzag nanotube control is syntactically valid, but the very large number
of degree-2 nodes and boundary edges indicates that the v0 generated graph is
not a clean ideal cylindrical nanotube control.
```

For an open ideal tube, boundary nodes should mainly appear at tube ends, not
throughout most of the structure.

Likely issue:

```text
The v0 zigzag construction does not share enough cell edges under the current
wrapping/orientation rule, so many cells remain effectively under-connected.
```

Required follow-up:

```text
Repair nanotube generator before using zigzag outputs in carrier specificity
diagnostics.
```

Allowed statement:

```text
The zigzag control was generated and validated syntactically, but its boundary
and degree profile indicate an unsuitable v0 topology for later carrier
diagnostics.
```

---

## 4. Cross-structure inventory status

| structure | status | usable for FU02g2? | note |
|---|---|---:|---|
| `c60_reference` | valid and reliable | yes | validated closed fullerene reference |
| `graphene_patch` | valid finite patch | yes, with boundary caution | flat/open hexagonal control |
| `nanotube_armchair` | syntactically valid but degree-4 issue | not yet | repair generator first |
| `nanotube_zigzag` | syntactically valid but excessive boundary/degree-2 issue | not yet | repair generator first |

---

## 5. Main result

BMS-FU02g1-v0 successfully establishes the structure-inventory workflow and
normalizes the C60 reference plus generated geometry-class controls.

However, the nanotube controls require topology repair before diagnostic use.

Core result:

```text
C60 reference:
  good

Graphene patch:
  good as finite boundary-marked flat control

Nanotube armchair:
  generated but topology issue: degree-4 nodes

Nanotube zigzag:
  generated but topology issue: excessive degree-2 / boundary edges
```

Internal summary:

```text
C60 steht.
Graphen steht.
Nanotube ist noch krumm im falschen Sinne.
```

---

## 6. Claim boundary

Allowed:

```text
FU02g1 establishes a graph/cell inventory workflow and produces a valid C60
reference plus a usable finite graphene-patch control.
```

Allowed:

```text
The nanotube v0 controls expose generator limitations and should be repaired
before carrier diagnostics.
```

Not allowed:

```text
The nanotube v0 controls are validated molecular nanotube graphs.
The inventory proves carrier specificity.
The inventory proves real-structure memory.
The inventory proves physical molecular geometry.
```

---

## 7. Recommended next block

Before FU02g2, add a repair block:

```text
BMS-FU02g1b — Nanotube Topology Repair and Validation
```

Purpose:

```text
Generate clean armchair and zigzag cylindrical hexagonal graph controls with
expected degree profiles and explicit end-boundary structure.
```

Validation goals:

```text
No degree-4 nodes in ideal tube wall.
Interior tube nodes degree 3.
Boundary nodes restricted to open tube ends unless periodic axial closure is
explicitly requested.
Cell sharing consistent with cylindrical hexagonal tiling.
Degree histogram and boundary counts compatible with intended tube topology.
```

After FU02g1b:

```text
BMS-FU02g2 — Carrier Diagnostic Transfer to Geometry-Class Controls
```

should be run only on:

```text
C60 reference
graphene patch
repaired armchair nanotube
repaired zigzag nanotube
```

---

## 8. Optional immediate patch strategy

A robust nanotube builder should not rely on approximate rounded geometric
deduplication alone.

Recommended alternatives:

```text
1. Build nanotubes from explicit honeycomb lattice indices and quotient
   identifications.

2. Use graph-first construction:
   nodes indexed by lattice coordinates modulo circumference,
   edges generated from deterministic neighbor rules.

3. Derive cells from indexed cycles rather than from approximate vertex
   coordinates.

4. Only then assign inspection coordinates on a cylinder.
```

This avoids accidental degree-4 nodes and under-shared zigzag cells.

Internal formulation:

```text
Erst Topologie sauber.
Dann hübsche Koordinaten.
```

---

## 9. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02g1 structure inventory result note"

git push
```

---

## 10. Internal summary

```text
FU02g1-v0:

  C60:
    valid
    degree 3 everywhere
    20 H + 12 P
    no boundary

  Graphene:
    valid finite patch
    20 hexagons
    boundary explicit
    usable with boundary caution

  Armchair nanotube:
    generated
    but 8 degree-4 nodes
    repair needed

  Zigzag nanotube:
    generated
    but too many degree-2 / boundary nodes
    repair needed

Conclusion:
  Inventory workflow works.
  C60 and Graphen are usable.
  Nanotube generator needs FU02g1b repair.
```
