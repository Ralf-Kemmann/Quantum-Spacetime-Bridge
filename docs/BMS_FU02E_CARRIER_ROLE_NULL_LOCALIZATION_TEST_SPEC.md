# BMS-FU02e — Carrier Role Null Localization Test Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02E_CARRIER_ROLE_NULL_LOCALIZATION_TEST_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02e follows BMS-FU02d1.

FU02d1 found that the FU02d seam-boundary carrier network maps onto a connected
C60 face region:

```text
carrier faces:
  17 / 32

carrier face types:
  12 hexagons
  5 pentagons

carrier face components:
  1 connected component

H,H mixed-face set:
  8 hexagons

H,P boundary subset:
  5 pentagons
```

FU02e asks:

```text
Ist diese Face-Landschaft spezifisch oder billig nachbaubar?
```

Scientific formulation:

```text
Do null carrier-role assignments reproduce the same connected face-localization
pattern as the real FU02d1 carrier network?
```

Internal image:

```text
FU02d1:
  Das Netz liegt auf einer verbundenen 17-Face-Landschaft.

FU02e:
  Können Attrappen dieselbe Landschaft billig nachbauen?
```

---

## 2. Core questions

1. Do null carrier assignments also form one connected carrier-face component?
2. Do nulls reproduce a carrier-face count near 17 / 32?
3. Do nulls reproduce an 8-hexagon H,H mixed-face component?
4. Do nulls reproduce a 5-pentagon H,P boundary subset?
5. Do nulls reproduce the same number of mixed seam-boundary faces?
6. Is the real carrier-face region unusually compact, connected or role-organized?

---

## 3. Input artifacts

Primary FU02d1 outputs:

```text
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_parser_audit.json
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_localization.csv
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_component_summary.csv
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_run_manifest.json
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_warnings.json
```

Primary FU02d outputs:

```text
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_carrier_edge_geometry.csv
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open/bms_fu02d_carrier_node_geometry.csv
```

C60 audit inputs:

```text
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

---

## 4. Null families

FU02e-v0 uses role-assignment nulls on the fixed validated C60 graph.

### 4.1 edge_type_preserving_role_shuffle

Shuffle H,H consensus labels among all H,H / 6:6 edges and H,P secondary labels
among all H,P / 5:6 edges.

This preserves:

```text
H,H carrier count = 7
H,P carrier count = 23
edge type class
```

It tests whether the observed face localization is stronger than random
same-edge-class role placement.

### 4.2 degree_spread_role_shuffle

Shuffle carrier labels while approximately matching endpoint degree exposure.
For C60 all nodes have degree 3, so this mostly reduces to edge-type-preserving
role shuffle but remains explicit for future graphs.

### 4.3 component_size_preserving_hp_shuffle

Preserve the H,P component size multiset from FU02d:

```text
5, 5, 5, 4, 4
```

and place H,P carrier components on random connected H,P subgraphs, while H,H
carriers are shuffled among H,H edges.

This tests whether the five H,P local components alone explain the face region.

### 4.4 hh_anchor_neighborhood_decoy

Preserve the seven H,H anchor count and choose H,P carriers preferentially near
the shuffled H,H anchors.

This is the strongest decoy family in FU02e-v0 because it allows a null to build
an H,P boundary around H,H anchors.

It tests whether the real region remains distinctive even against a role-aware
anchor-neighborhood decoy.

---

## 5. Real metrics

From FU02d1 real face localization:

```text
carrier_face_count = 17
carrier_face_fraction = 0.53125
carrier_face_component_count = 1
largest_carrier_face_component_count = 17
mixed_seam_boundary_face_count = 8
hp_boundary_face_count = 9
carrier_adjacent_face_count = 11
noncarrier_face_count = 4
carrier_hexagon_face_count = 12
carrier_pentagon_face_count = 5
hh_face_count = 8
hp_face_count = 17
mixed_face_hexagon_count = 8
mixed_face_pentagon_count = 0
```

FU02e should compute these same metrics for null replicates.

---

## 6. Comparison metrics

For each null family:

```text
real_value
null_mean
null_std
null_min
null_max
null_median
empirical_ge_fraction
empirical_le_fraction
rank_position_of_real
```

Important:

```text
Use empirical exceedance fractions, not formal p-values.
```

Interpretation labels:

```text
real_more_compact_than_nulls
real_less_compact_than_nulls
null_reproduces_metric_behavior
mixed_or_metric_dependent
inconclusive_due_to_scope
```

---

## 7. Expected outputs

Output directory:

```text
runs/BMS-FU02e/carrier_role_null_localization_open/
```

Expected files:

```text
bms_fu02e_null_localization_metrics.csv
bms_fu02e_real_vs_null_summary.csv
bms_fu02e_null_family_inventory.csv
bms_fu02e_real_face_metrics.json
bms_fu02e_run_manifest.json
bms_fu02e_warnings.json
bms_fu02e_config_resolved.yaml
```

Optional details:

```text
bms_fu02e_null_carrier_assignments_sample.csv
```

---

## 8. Interpretation boundary

Allowed:

```text
BMS-FU02e tests whether the FU02d1 connected carrier-face region is reproduced
by role-assignment null families on the fixed C60 graph.
```

Allowed after positive result:

```text
The real carrier-face localization is more connected/compact/role-organized
than the tested null families.
```

Allowed after null reproduction:

```text
The tested null family reproduces the carrier-face localization metric, so that
metric is not specific evidence by itself.
```

Not allowed:

```text
A formal physical probability has been computed.
C60 proves emergent spacetime.
The face region is a physical spacetime patch.
Global fullerene symmetry has been recovered.
```

---

## 9. Bridge relevance

FU02e is a specificity test.

FU02d1 showed:

```text
The seam-boundary carrier network lies on one connected 17-face region.
```

FU02e asks whether that is a stable C60-specific localization signal or a cheap
consequence of assigning 7 H,H and 23 H,P carrier roles.

Bridge-facing cautious statement:

```text
If the real carrier-face localization remains distinctive against role-aware
null assignments, it supports the methodological claim that geometry-readable
relational carrier roles can have nontrivial localization structure beyond
edge-class counts alone.
```

Internal formulation:

```text
Nicht jedes Netz mit 7 H-H und 23 H-P darf automatisch dieselbe Landschaft
malen.
```

---

## 10. Recommended next after FU02e

If real localization exceeds nulls:

```text
BMS-FU02f — Carrier Role Visualization and Symmetry-Orbit Inspection
```

Purpose:

```text
Export a visual cage map and inspect whether the carrier-face region corresponds
to a recognizable C60 patch, belt, or orbit-like subset.
```

If nulls reproduce the localization:

```text
BMS-FU02e1 — Stronger Fullerene-Preserving Nulls
```

Purpose:

```text
Develop stricter C60/fullerene-preserving nulls and separate trivial
face-incidence constraints from nontrivial localization.
```
