# BMS-FU02d1 — Face Parser Repair and Face-Level Carrier Localization Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02D1_FACE_PARSER_REPAIR_AND_FACE_LOCALIZATION_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02d1 follows BMS-FU02d.

FU02d produced a strong edge-/node-/component-level result:

```text
H,H consensus edges:
  7 distributed seam anchors

H,P secondary edges:
  23 boundary carriers

H,H + H,P:
  one connected 30-edge / 25-node seam-boundary carrier network
```

However, FU02d-v0 produced an invalid face-level readout:

```text
face_label_counts:
  noncarrier_face = 32
```

This is inconsistent with the 30 carrier edges and indicates a face-parser problem, not a physical result.

FU02d1 repairs the face parser and reruns face-level carrier localization.

Internal purpose:

```text
Jetzt prüfen wir, auf welchen Faces dieses Netz liegt.
```

---

## 2. Core questions

1. Which faces carry H,H consensus edges?
2. Which faces carry H,P secondary edges?
3. Which faces carry both H,H and H,P carrier roles?
4. Are carrier faces hexagons, pentagons, or mixed by involvement?
5. Does the 30-edge / 25-node seam-boundary network correspond to:
   - a local patch,
   - a belt,
   - a ring,
   - several connected face regions,
   - or a distributed cage-level pattern?
6. Are mixed-role junction nodes concentrated around carrier faces?

---

## 3. Input artifacts

Primary FU02d outputs:

```text
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_carrier_edge_geometry.csv
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_carrier_node_geometry.csv
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_run_manifest.json
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_warnings.json
```

Primary FU02c outputs:

```text
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_consensus_carriers.csv
```

C60 audit inputs:

```text
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

---

## 4. Face parser repair

FU02d1 must not assume a single face-column name.

It should inspect and support common column patterns:

```text
face_a, face_b
left_face, right_face
face_1, face_2
faces
incident_faces
face_ids
shared_faces
```

If no direct edge-to-face annotations are usable, FU02d1 should reconstruct edge-to-face incidence from the face table if the face table contains node cycles.

Accepted face-table node patterns:

```text
nodes
node_ids
vertices
vertex_ids
cycle_nodes
boundary_nodes
```

The runner must write a face-parser audit table:

```text
bms_fu02d1_face_parser_audit.json
```

The audit must include:

```text
detected_edge_face_columns
detected_face_node_column
edge_face_mapping_source
mapped_edge_count
unmapped_edge_count
face_count
warnings
```

---

## 5. Face localization metrics

For each face:

```text
face_id
face_type
boundary_edge_count
hh_consensus_edge_count
hp_secondary_edge_count
carrier_edge_count
mixed_role_junction_node_count
carrier_node_count
face_carrier_role_label
```

Face role labels:

```text
hh_seam_face
hp_boundary_face
mixed_seam_boundary_face
carrier_adjacent_face
noncarrier_face
parser_unresolved_face
```

---

## 6. Face adjacency and components

Two faces are adjacent if they share one graph edge.

FU02d1 computes carrier-face components for:

```text
HH_FACE_SET:
  faces with H,H consensus edges

HP_FACE_SET:
  faces with H,P secondary edges

MIXED_FACE_SET:
  faces with both H,H and H,P carrier roles

CARRIER_FACE_SET:
  faces with any H,H or H,P carrier edge
```

Component metrics:

```text
component_count
largest_component_face_count
face_type_counts
carrier_edge_counts
face_ids
```

---

## 7. Face-ring / belt indicators

FU02d1-v0 uses conservative graph indicators, not geometric claims.

Indicators:

```text
carrier_face_count
carrier_face_fraction
carrier_face_component_count
largest_carrier_face_component_count
carrier_face_boundary_edge_count
carrier_face_internal_adjacency_count
```

Interpretation is descriptive only:

```text
localized_patch_candidate
connected_face_region_candidate
distributed_face_region_candidate
face_belt_candidate
fragmented_face_region_candidate
```

FU02d1-v0 should not claim a visual belt unless a later visualization confirms it.

---

## 8. Expected outputs

Output directory:

```text
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/
```

Expected files:

```text
bms_fu02d1_face_parser_audit.json
bms_fu02d1_face_localization.csv
bms_fu02d1_face_component_summary.csv
bms_fu02d1_face_adjacency_edges.csv
bms_fu02d1_carrier_face_summary.csv
bms_fu02d1_visualization_faces.csv
bms_fu02d1_run_manifest.json
bms_fu02d1_warnings.json
bms_fu02d1_config_resolved.yaml
```

---

## 9. Claim boundary

Allowed:

```text
BMS-FU02d1 repairs the face parser and maps the FU02d seam-boundary carrier
network onto C60 face incidence.
```

Allowed after successful parser repair:

```text
The connected edge-level seam-boundary carrier network is localized on a
specific set of C60 faces.
```

Not allowed without further visualization/null tests:

```text
The carrier faces form a physical belt.
Global C60 symmetry has been recovered.
The face pattern is null-specific.
A physical spacetime metric has been recovered.
```

---

## 10. Bridge relevance

FU02d showed that role-differentiated carrier edges form one connected
seam-boundary network.

FU02d1 checks whether this network also has face-level organization.

Bridge-facing cautious statement:

```text
If the seam-boundary carrier network maps to a coherent face region, this
supports the methodological view that geometry-readable relational information
can be organized not only through edges and junctions, but also through
higher-order local incidence structures.
```

Internal formulation:

```text
Kanten sagen: Das Netz hängt zusammen.
Faces sagen: Wo liegt das Netz auf dem Käfig?
```

---

## 11. Recommended next after FU02d1

If face localization succeeds:

```text
BMS-FU02e — Carrier Role Null Localization Test
```

Purpose:

```text
Test whether comparable face-localized seam-boundary networks appear in null
graphs or whether the real C60 carrier-role geometry is localization-specific.
```

If parser remains unresolved:

```text
BMS-FU02d1b — C60 Face Incidence Audit Reconstruction
```

Purpose:

```text
Reconstruct face incidence directly from validated C60 faces and edges and
write a canonical edge-to-face incidence table.
```
