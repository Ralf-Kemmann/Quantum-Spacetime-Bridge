# BMS-FU02d — Carrier Role Geometry and Patch Distribution Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02D_CARRIER_ROLE_GEOMETRY_PATCH_DISTRIBUTION_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02d follows BMS-FU02c.

FU02c refined the FU02b result:

```text
FU02b:
  H,H / 6:6 seams dominate the sharp aggregate carrier layer.

FU02c:
  H,H / 6:6 dominates the bond-class-weighted seam layer.
  H,P / 5:6 dominates the topology-only and graph-distance boundary layers.
  Seven H,H edges survive as all-representation consensus carriers.
```

FU02d asks:

```text
Wo sitzen diese Rollen im C60-Käfig?
```

Scientific formulation:

```text
How are H,H consensus seam carriers and H,P topology/distance boundary carriers
arranged on the C60 cage graph: as local patches, adjacent boundary rings,
paths, shells, or distributed cage-level patterns?
```

Internal image:

```text
FU02c:
  Es gibt Naht-Träger und Grenz-Träger.

FU02d:
  Jetzt zeichnen wir die Rollenkarte im Käfig.
```

---

## 2. Working questions

1. Are the seven H,H all-representation consensus carriers local or distributed?
2. Are H,P secondary carriers adjacent to the H,H consensus spine?
3. Do H,P carriers form boundary rings around H,H seam patches?
4. Do top carrier edges concentrate around particular faces?
5. Do top carrier edges form connected components, paths, or local patches?
6. Which nodes act as carrier-role junctions?
7. Is the carrier geometry patch-like, ring-like, path-like, or distributed?

---

## 3. Input artifacts

Primary FU02c outputs:

```text
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_consensus_carriers.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_edge_representation_summary.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_representation_motif_enrichment.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_representation_rank_matrix.csv
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_run_manifest.json
runs/BMS-FU02c/representation_resolved_carrier_delta_open/bms_fu02c_warnings.json
```

C60 audit inputs:

```text
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

Optional comparison inputs:

```text
runs/BMS-FU02b/carrier_sharpness_rank_stability_open/bms_fu02b_edge_sharpness_scores.csv
runs/BMS-FU02/load_bearing_pattern_analysis_open/bms_fu02_edge_load_bearing_scores.csv
```

---

## 4. Carrier groups

FU02d-v0 defines the following role groups from FU02c consensus labels:

```text
HH_CONSENSUS:
  consensus_label == hh_consensus_all_representations

HP_SECONDARY:
  consensus_label == hp_secondary_carrier

REP_SPECIFIC:
  consensus_label == representation_specific_candidate

UNSTABLE:
  consensus_label == decoy_reproduced_or_unstable
```

The main geometry analysis focuses on:

```text
HH_CONSENSUS
HP_SECONDARY
HH_CONSENSUS + HP_SECONDARY
```

---

## 5. Metrics

### 5.1 Edge adjacency

Two edges are edge-adjacent if they share at least one node.

For carrier sets:

```text
component_count
largest_component_edge_count
largest_component_node_count
mean_edge_degree_inside_carrier_subgraph
isolated_edge_count
```

### 5.2 Node role junctions

For each node:

```text
incident_hh_consensus_count
incident_hp_secondary_count
incident_total_carrier_count
carrier_junction_label
```

Node labels:

```text
hh_spine_node
hp_boundary_node
mixed_role_junction
carrier_isolated_endpoint
noncarrier_node
```

### 5.3 Face involvement

For each face:

```text
incident_hh_consensus_edges
incident_hp_secondary_edges
incident_total_carrier_edges
face_carrier_role_label
```

Face labels:

```text
hh_patch_face
hp_boundary_face
mixed_patch_boundary_face
carrier_sparse_face
noncarrier_face
```

### 5.4 Patch boundary relation

Compute adjacency between HH_CONSENSUS and HP_SECONDARY:

```text
hp_edges_adjacent_to_hh_count
hp_edges_adjacent_to_hh_fraction
hh_edges_with_adjacent_hp_count
hh_edges_with_adjacent_hp_fraction
```

This tests whether H,P secondary carriers sit around the H,H consensus spine.

### 5.5 Shell distance from HH consensus

Graph distance from each edge to nearest HH_CONSENSUS edge:

```text
edge_shell_distance_to_hh_consensus
```

Distance is 0 for HH consensus edges, 1 for edges sharing a node with an HH consensus edge, etc.

---

## 6. Expected outputs

Output directory:

```text
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/
```

Expected files:

```text
bms_fu02d_carrier_edge_geometry.csv
bms_fu02d_carrier_node_geometry.csv
bms_fu02d_carrier_face_geometry.csv
bms_fu02d_carrier_component_summary.csv
bms_fu02d_carrier_role_adjacency_summary.csv
bms_fu02d_run_manifest.json
bms_fu02d_warnings.json
bms_fu02d_config_resolved.yaml
```

Optional visualization-ready table:

```text
bms_fu02d_visualization_edges.csv
```

---

## 7. Interpretation patterns

### Pattern A — compact H,H spine with H,P boundary

```text
HH consensus edges form a connected or near-connected patch.
Most H,P secondary edges sit at shell distance 1 from the H,H spine.
```

Interpretation:

```text
The C60 carrier roles form a seam-boundary structure: H,H seam carriers act as
a local spine and H,P carriers act as surrounding boundary/interface edges.
```

### Pattern B — distributed H,H spine

```text
HH consensus edges are distributed across several components.
H,P secondary edges are not concentrated around them.
```

Interpretation:

```text
The carrier roles are distributed cage-level roles rather than one local patch.
```

### Pattern C — H,P dominates independent topology layer

```text
H,P secondary carriers form their own connected patches with weak adjacency to
H,H consensus carriers.
```

Interpretation:

```text
Topology/distance carrier roles may reflect boundary-layer structure distinct
from weighted H,H seam roles.
```

### Pattern D — mostly unstable / fragmented

```text
Carrier sets break into many isolated edges and small components.
```

Interpretation:

```text
FU02d should be read as local candidate mapping rather than stable carrier
geometry.
```

---

## 8. Claim boundary

Allowed:

```text
BMS-FU02d maps the graph-geometric arrangement of FU02c carrier roles on the
validated C60 cage graph.
```

Allowed after positive result:

```text
The carrier roles form a local seam-boundary pattern in which H,P secondary
carriers are adjacent to or surround H,H consensus carriers.
```

Not allowed:

```text
Global C60 symmetry has been fully recovered.
A physical spacetime metric has been recovered.
The carriers are physical spacetime atoms.
C60 proves emergent spacetime.
```

---

## 9. Bridge relevance

FU02d tests whether role-dependent relational information also has spatial /
graph-geometric organization within the controlled C60 calibration object.

Bridge-facing cautious statement:

```text
If carrier roles form structured patches or boundary arrangements, this
supports the methodological view that geometry-readable relational information
is not only role-differentiated, but also organized in graph-geometric carrier
patterns.
```

Internal formulation:

```text
FU02c sagt:
  Es gibt Naht-Träger und Grenz-Träger.

FU02d fragt:
  Bilden sie ein Gewebe?
```

---

## 10. Recommended next after FU02d

If FU02d shows seam-boundary organization:

```text
BMS-FU02e — Carrier Role Null Localization Test
```

Purpose:

```text
Test whether comparable seam-boundary role geometry appears in null graphs, or
whether the real C60 carrier-role arrangement is localization-specific.
```

If FU02d shows fragmentation:

```text
BMS-FU02c2 — Graph-Distance-Shell Reconstruction Extension
```

Purpose:

```text
Add explicit graph_distance_shells reconstruction and rerun representation-
resolved carrier deltas.
```
