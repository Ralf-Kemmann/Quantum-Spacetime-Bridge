# BMS-FU02f — Carrier Role Visualization and Symmetry-Orbit Inspection Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02F_CARRIER_ROLE_VISUALIZATION_SYMMETRY_ORBIT_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02f follows BMS-FU02e1.

FU02e1 established a fixed-C60 role-assignment null result:

```text
near_real_profile_count = 0 / 2000
strict_near_real_profile_count = 0 / 2000
```

Interpretation:

```text
No tested null assignment simultaneously matched the real compact carrier-face
count, pentagon involvement, mixed seam-boundary face count and connectedness
constraints.
```

FU02f now turns the compact role-balanced carrier region into visualization-
ready artifacts and performs a cautious symmetry/orbit inspection.

Internal purpose:

```text
Jetzt gucken wir uns den Klunker an.
```

Scientific formulation:

```text
Export a visual C60 carrier-role map and inspect whether the compact
role-balanced 17-face region has patch-, cap-, belt-, or orbit-like structure
under conservative graph diagnostics.
```

---

## 2. Core questions

1. Which nodes, edges and faces belong to the compact carrier region?
2. Which edges are H,H consensus seam anchors and which are H,P boundary carriers?
3. Which faces are mixed seam-boundary faces, H/P boundary faces, adjacent faces or noncarrier faces?
4. Does the 17-face carrier region look like:
   - a local patch,
   - a cap,
   - a belt,
   - a distributed arc,
   - or an orbit-like subset?
5. Are the carrier faces concentrated in one indexed face band?
6. Are the strongest mixed faces H_17/H_18/H_19 central within the carrier region?
7. What can be said without a full automorphism-group/symmetry proof?

---

## 3. Input artifacts

Primary FU02d1 outputs:

```text
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_localization.csv
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_component_summary.csv
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_visualization_faces.csv
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_run_manifest.json
```

Primary FU02d outputs:

```text
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_visualization_edges.csv
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_carrier_node_geometry.csv
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_carrier_edge_geometry.csv
```

C60 audit inputs:

```text
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

Optional FU02e1 context:

```text
runs/BMS-FU02e1/role_balance_localization_specificity_open/bms_fu02e1_run_manifest.json
```

---

## 4. Visualization exports

FU02f should produce lightweight CSV/JSON artifacts suitable for plotting in
Python, Gephi, Cytoscape or later custom diagrams.

### 4.1 Node visualization table

Fields:

```text
node_id
degree
node_role_label
incident_hh_consensus_count
incident_hp_secondary_count
incident_total_carrier_count
carrier_region_member
visual_size
visual_layer
```

### 4.2 Edge visualization table

Fields:

```text
edge_key
source
target
edge_type
shared_face_types
carrier_role
is_hh_consensus
is_hp_secondary
is_role_carrier
shell_distance_to_hh_consensus
visual_weight
visual_layer
```

### 4.3 Face visualization table

Fields:

```text
face_id
face_type
face_carrier_role_label
carrier_edge_count
hh_consensus_edge_count
hp_secondary_edge_count
mixed_role_junction_node_count
carrier_region_member
visual_weight
visual_layer
```

### 4.4 Region manifest

JSON summary:

```text
carrier_face_ids
mixed_face_ids
hp_boundary_face_ids
carrier_adjacent_face_ids
noncarrier_face_ids
carrier_node_ids
carrier_edge_ids
hh_consensus_edges
hp_secondary_edges
```

---

## 5. Symmetry/orbit inspection diagnostics

FU02f-v0 uses conservative graph diagnostics, not a full automorphism-group proof.

### 5.1 Face id run diagnostics

Because the generated C60 face ids are deterministic, not physical coordinates,
face-id runs are only a weak inspection cue.

Compute:

```text
carrier_hexagon_ids
carrier_pentagon_ids
min/max id index
contiguous id intervals
gap counts
```

### 5.2 Carrier region boundary diagnostics

Use face adjacency:

```text
carrier_face_count
carrier_face_internal_adjacency_count
carrier_face_boundary_adjacency_count
carrier_face_external_neighbor_count
```

### 5.3 Central mixed-face diagnostics

For carrier faces, compute distance to the mixed-seam-boundary set:

```text
face_distance_to_mixed_core
```

Then summarize:

```text
max_distance_to_mixed_core
mean_distance_to_mixed_core
mixed_core_face_count
```

### 5.4 Region-shape descriptive labels

Allowed descriptive labels:

```text
connected_face_region_candidate
compact_patch_candidate
cap_like_candidate
belt_like_candidate
arc_or_strip_candidate
distributed_region_candidate
insufficient_for_shape_label
```

Important:

```text
These are descriptive graph-inspection labels, not physical symmetry claims.
```

---

## 6. Optional simple SVG

FU02f-v0 may generate a very simple non-geometric SVG/HTML adjacency map if
matplotlib/networkx are unavailable. This visualization is for internal
inspection only.

Required caveat:

```text
The visualization is graph-layout dependent and not a true 3D C60 geometry.
```

---

## 7. Expected outputs

Output directory:

```text
runs/BMS-FU02f/carrier_role_visualization_symmetry_orbit_open/
```

Expected files:

```text
bms_fu02f_visualization_nodes.csv
bms_fu02f_visualization_edges.csv
bms_fu02f_visualization_faces.csv
bms_fu02f_region_manifest.json
bms_fu02f_symmetry_orbit_inspection.csv
bms_fu02f_shape_diagnostic_summary.json
bms_fu02f_simple_region_map.svg
bms_fu02f_run_manifest.json
bms_fu02f_warnings.json
bms_fu02f_config_resolved.yaml
```

---

## 8. Interpretation boundary

Allowed:

```text
BMS-FU02f exports visualization-ready C60 carrier-role maps and performs a
conservative graph-level shape/orbit inspection.
```

Allowed if diagnostics support it:

```text
The carrier region is a connected compact face-region candidate with a mixed
hexagon core and pentagon boundary involvement.
```

Not allowed:

```text
Full C60 automorphism orbit recovered.
Physical belt proven.
Physical spacetime patch proven.
Global fullerene symmetry proven.
```

---

## 9. Bridge relevance

FU02f does not add physical proof. It improves interpretability.

Bridge-facing cautious statement:

```text
BMS-FU02f makes the compact role-balanced carrier region inspectable as a
graph-geometric object. This supports transparent interpretation of how
role-differentiated relational carrier information is organized on the
controlled C60 calibration graph.
```

Internal formulation:

```text
Nach Nulltest und Rollenbalance:
Jetzt bekommt der Klunker eine Karte.
```

---

## 10. Recommended next after FU02f

If FU02f shows a coherent compact patch/cap/belt candidate:

```text
BMS-FU02g — Fullerene-Family Structural Null Ensemble
```

Purpose:

```text
Test whether comparable compact role-balanced regions appear in other
fullerene-like or fullerene-preserving structural ensembles.
```

If visualization is ambiguous:

```text
BMS-FU02f1 — 3D Coordinate Visualization Export
```

Purpose:

```text
Generate or import approximate C60 3D coordinates and map carrier roles onto a
3D cage visualization.
```
