# BMS-FU02g1 — Structure Inventory Builder Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G1_STRUCTURE_INVENTORY_BUILDER_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02g1 follows BMS-FU02g0.

BMS-FU02g0 defined the next methodological theme:

```text
Real-structure memory:
How specifically does a derived relational/carrier structure recover known
real-structure organization?
```

BMS-FU02g1 now builds the first transparent structure inventory for real,
symmetry-bearing geometry controls:

```text
C60 reference
graphene patch
armchair nanotube
zigzag nanotube
```

This is not a chemistry or electronic-structure block.

It is a graph/cell inventory block.

Internal formulation:

```text
Wir bauen die Prüfkörper.
Noch keine Diagnose.
Noch kein Claim.
```

---

## 2. Design principles

1. Use transparent graph/cell structures.
2. Keep chemistry claims out of scope.
3. Mark boundary, closure, periodicity and symmetry labels explicitly.
4. Preserve C60 as the validated reference structure from FU01/FU02.
5. Use generated graphene/nanotube graph controls as geometry-class Prüfkörper.
6. Treat coordinates as layout coordinates only unless a later block imports validated molecular coordinates.
7. Keep all outputs schema-clear and runner-auditable.

---

## 3. Control structures

### 3.1 C60 reference

Input:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

Role:

```text
closed-curved highly symmetric fullerene reference
```

Expected labels:

```text
structure_class = fullerene
geometry_class = closed_curved_cage
closure_class = closed_cage
curvature_class = positive_closed_curvature_proxy
pentagon_present = true
hexagon_present = true
boundary_present = false
inversion_flag = true
rotation_symmetry_label = icosahedral_reference
```

### 3.2 Graphene patch

Generated control:

```text
flat finite hexagonal patch
```

Role:

```text
flat / two-dimensional / open-boundary hexagonal reference
```

Purpose:

```text
Test whether later carrier structures can be explained by local hexagonal
connectivity and boundary effects alone.
```

Important caveat:

```text
A finite patch has boundaries. Boundary fields must be tracked explicitly.
```

### 3.3 Armchair nanotube control

Generated control:

```text
cylindrical hexagonal graph with armchair-style circumferential closure
```

Role:

```text
open-curved or periodically identified cylindrical reference
```

Purpose:

```text
Test curvature/cylindrical identification without closed fullerene cage closure.
```

### 3.4 Zigzag nanotube control

Generated control:

```text
cylindrical hexagonal graph with zigzag-style circumferential closure
```

Role:

```text
open-curved / cylindrical reference with different wrapping class
```

Purpose:

```text
Test whether later carrier organization is sensitive to tube wrapping class.
```

---

## 4. Inventory table

Output:

```text
data/bms_fu02g_structure_inventory.csv
```

Required fields:

```text
structure_id
structure_class
geometry_class
node_count
edge_count
cell_count
boundary_present
boundary_node_count
boundary_edge_count
periodic_dimension_count
closure_class
curvature_class
pentagon_present
hexagon_present
chirality_label
inversion_flag
rotation_symmetry_label
reflection_flag
screw_symmetry_flag
source_type
source_note
layout_coordinate_status
diagnostic_scope_note
```

---

## 5. Graph/cell outputs

For each structure:

```text
data/bms_fu02g_<structure_id>_nodes.csv
data/bms_fu02g_<structure_id>_edges.csv
data/bms_fu02g_<structure_id>_cells.csv
data/bms_fu02g_<structure_id>_manifest.json
```

For C60 reference, FU02g1 creates normalized FU02g copies while preserving source ids.

---

## 6. Schemas

### Node schema

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

### Edge schema

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

### Cell schema

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

## 7. Expected outputs

```text
data/bms_fu02g_structure_inventory.csv

data/bms_fu02g_c60_reference_nodes.csv
data/bms_fu02g_c60_reference_edges.csv
data/bms_fu02g_c60_reference_cells.csv
data/bms_fu02g_c60_reference_manifest.json

data/bms_fu02g_graphene_patch_nodes.csv
data/bms_fu02g_graphene_patch_edges.csv
data/bms_fu02g_graphene_patch_cells.csv
data/bms_fu02g_graphene_patch_manifest.json

data/bms_fu02g_nanotube_armchair_nodes.csv
data/bms_fu02g_nanotube_armchair_edges.csv
data/bms_fu02g_nanotube_armchair_cells.csv
data/bms_fu02g_nanotube_armchair_manifest.json

data/bms_fu02g_nanotube_zigzag_nodes.csv
data/bms_fu02g_nanotube_zigzag_edges.csv
data/bms_fu02g_nanotube_zigzag_cells.csv
data/bms_fu02g_nanotube_zigzag_manifest.json

data/bms_fu02g_structure_inventory_manifest.json
data/bms_fu02g_structure_inventory_warnings.json
data/bms_fu02g_structure_inventory_config_resolved.yaml
```

---

## 8. Validation checks

Each structure manifest reports:

```text
structure_id
node_count
edge_count
cell_count
boundary_node_count
boundary_edge_count
degree_histogram
cell_type_counts
boundary_present
periodic_dimension_count
closure_class
curvature_class
hexagon_present
pentagon_present
validation_status
warnings
```

Minimum validation:

```text
node_count > 0
edge_count > 0
cell_count > 0
all edges reference valid nodes
all cells reference valid nodes
degree histogram computed
```

---

## 9. Interpretation boundary

Allowed:

```text
BMS-FU02g1 builds transparent graph/cell inventory artifacts for real-structure
memory controls.
```

Allowed:

```text
The generated graphene and nanotube controls are graph-geometric Prüfkörper,
not electronic-structure or chemical simulation models.
```

Not allowed:

```text
The generated coordinates are physical molecular coordinates.
The inventory proves carrier specificity.
The inventory proves quantum chemistry, spacetime or physical geometry.
```

---

## 10. Recommended next block

After FU02g1:

```text
BMS-FU02g2 — Carrier Diagnostic Transfer to Geometry-Class Controls
```

Purpose:

```text
Transfer FU02-style carrier/localization diagnostics from C60 to generalized
cell-based graph controls.
```

---

## 11. Internal summary

```text
FU02g1:

  Prüfkörper bauen:
    C60 reference
    graphene patch
    armchair nanotube
    zigzag nanotube

  Noch nicht:
    Carrierdiagnostik
    Symmetriebeweis
    Chemie
    Raumzeit

  Ziel:
    Reale Symmetrie-Geometrien als sauberes Inventar.
```
