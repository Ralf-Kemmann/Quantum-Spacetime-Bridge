# BMS-FU02g1b — Nanotube Topology Repair and Validation Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G1B_NANOTUBE_TOPOLOGY_REPAIR_VALIDATION_SPEC.md`  
Status: Repair specification and implementation block

---

## 1. Purpose

BMS-FU02g1b repairs the provisional nanotube controls generated in BMS-FU02g1.

BMS-FU02g1 established the structure-inventory workflow, but its generated
nanotube controls showed topology problems:

```text
nanotube_armchair:
  degree_histogram = {'2': 20, '3': 72, '4': 8}
  issue: degree-4 nodes

nanotube_zigzag:
  degree_histogram = {'2': 84, '3': 84}
  issue: excessive degree-2 / boundary profile
```

These v0 nanotube outputs are syntactically valid but not suitable for FU02g2
carrier diagnostics.

BMS-FU02g1b therefore generates repaired nanotube graph/cell controls.

Internal formulation:

```text
Erst Topologie sauber.
Dann hübsche Koordinaten.
```

---

## 2. Scope

This block is still not a chemistry or electronic-structure block.

Allowed:

```text
Generate clean cylindrical hexagonal graph/cell controls.
Validate degree profiles and boundary placement.
Export repaired inventory artifacts.
```

Not allowed:

```text
Claim physical molecular coordinates.
Claim validated real nanotube electronic/chemical structure.
Run carrier diagnostics.
Infer real-structure memory.
```

---

## 3. Design change from FU02g1

FU02g1 generated nanotubes using approximate geometric vertex deduplication
after wrapping.

FU02g1b avoids that as the main topological mechanism.

Instead, FU02g1b uses a graph-first construction:

```text
1. Build a finite honeycomb strip using explicit cells.
2. Identify circumferential boundary node pairs only when their local valence
   permits the identification.
3. Merge seam nodes conservatively.
4. Recompute edges and incident cells.
5. Assign cylindrical inspection coordinates only after topology is fixed.
```

This reduces accidental over-identification and under-sharing.

---

## 4. Repaired structures

### 4.1 Repaired armchair proxy

Structure id:

```text
nanotube_armchair_repaired
```

Role:

```text
open-ended cylindrical hexagonal graph control with armchair-like offset
```

Expected topology:

```text
mostly degree-3 tube wall nodes
degree-2 nodes restricted to open tube ends
no degree-4 nodes
hexagonal cells only
one circumferential periodic dimension
```

### 4.2 Repaired zigzag proxy

Structure id:

```text
nanotube_zigzag_repaired
```

Role:

```text
open-ended cylindrical hexagonal graph control with zigzag-like offset
```

Expected topology:

```text
mostly degree-3 tube wall nodes
degree-2 nodes restricted to open tube ends
no degree-4 nodes
hexagonal cells only
one circumferential periodic dimension
```

---

## 5. Validation goals

A repaired nanotube is acceptable for FU02g2 only if:

```text
degree_4_count == 0
max_degree <= 3
cell_count > 0
edge_count > 0
node_count > 0
all edges reference valid nodes
all cells reference valid nodes
boundary nodes are present but not dominant
boundary edges are present but not dominant
hexagon_present == true
pentagon_present == false
```

Preferred, but not strictly required in v1:

```text
interior_node_count > boundary_node_count
degree_3_count > degree_2_count
```

Important caveat:

```text
These are graph-geometric controls, not crystallographic nanotube imports.
```

---

## 6. Outputs

Output files:

```text
data/bms_fu02g1b_nanotube_topology_repair_inventory.csv

data/bms_fu02g1b_nanotube_armchair_repaired_nodes.csv
data/bms_fu02g1b_nanotube_armchair_repaired_edges.csv
data/bms_fu02g1b_nanotube_armchair_repaired_cells.csv
data/bms_fu02g1b_nanotube_armchair_repaired_manifest.json

data/bms_fu02g1b_nanotube_zigzag_repaired_nodes.csv
data/bms_fu02g1b_nanotube_zigzag_repaired_edges.csv
data/bms_fu02g1b_nanotube_zigzag_repaired_cells.csv
data/bms_fu02g1b_nanotube_zigzag_repaired_manifest.json

data/bms_fu02g1b_nanotube_topology_repair_manifest.json
data/bms_fu02g1b_nanotube_topology_repair_warnings.json
data/bms_fu02g1b_nanotube_topology_repair_config_resolved.yaml
```

---

## 7. Schemas

FU02g1b uses the same node/edge/cell inventory schemas as FU02g1, with repaired
structure ids.

### Node table

```text
structure_id
node_id
source_node_id
degree
boundary_node
periodic_node
layout_x
layout_y
layout_z
node_role_hint
coordinate_status
```

### Edge table

```text
structure_id
edge_id
source
target
source_source_id
target_source_id
edge_class
boundary_edge
periodic_edge
cell_left
cell_right
cell_count
edge_role_hint
```

### Cell table

```text
structure_id
cell_id
source_cell_id
cell_type
node_ids
edge_ids
boundary_cell
periodic_cell
cell_role_hint
layout_x
layout_y
layout_z
coordinate_status
```

---

## 8. Interpretation boundary

Allowed after successful repair:

```text
FU02g1b provides topology-repaired nanotube graph/cell controls suitable for
subsequent FU02g2 carrier-diagnostic transfer.
```

Not allowed:

```text
The repaired nanotubes are validated molecular structures.
The repaired nanotubes prove carrier specificity.
The repaired nanotubes prove real-structure memory.
```

---

## 9. Recommended next block

After FU02g1b passes validation:

```text
BMS-FU02g2 — Carrier Diagnostic Transfer to Geometry-Class Controls
```

Use FU02g2 only with:

```text
c60_reference
graphene_patch
nanotube_armchair_repaired
nanotube_zigzag_repaired
```

---

## 10. Internal summary

```text
FU02g1:
  Inventarworkflow steht.
  C60 steht.
  Graphen steht.
  Nanotube v0 krumm im falschen Sinne.

FU02g1b:
  Nanotube-Topologie reparieren.
  Keine Grad-4-Knoten.
  Rand nur plausibel an den offenen Enden.
  Dann erst FU02g2.
```
