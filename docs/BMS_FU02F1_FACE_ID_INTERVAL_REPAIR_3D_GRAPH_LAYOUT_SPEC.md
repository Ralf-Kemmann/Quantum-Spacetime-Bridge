# BMS-FU02f1 — Face-ID Interval Repair and 3D/Graph Layout Export Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02F1_FACE_ID_INTERVAL_REPAIR_3D_GRAPH_LAYOUT_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02f1 follows BMS-FU02f.

FU02f made the compact role-balanced C60 carrier region inspectable and found:

```text
mixed core:
  8 mixed seam-boundary faces

boundary:
  9 carrier faces at distance 1 from the mixed core

strongest mixed faces:
  H_17, H_18, H_19

boundary dominated by:
  P_07, P_08, P_09, P_10, P_11
```

However, the FU02f face-id interval helper returned empty fields:

```text
carrier_hexagon_intervals =
carrier_pentagon_intervals =
mixed_face_intervals =
```

FU02f1 repairs this interval helper and exports graph-layout-ready and approximate 3D-layout-ready artifacts.

Internal purpose:

```text
Jetzt machen wir die Karte schöner und robuster.
```

---

## 2. Core questions

1. Can face-id intervals be repaired for ids such as `H_17` and `P_09`?
2. Can the carrier region be exported for graph-layout inspection without relying on hidden assumptions?
3. Can approximate layout coordinates be produced for internal visualization?
4. Do the repaired intervals support the same qualitative picture:
   - mixed hexagon core,
   - pentagon-rich one-step boundary,
   - compact core-plus-boundary region?

---

## 3. Inputs

Primary FU02f outputs:

```text
runs/BMS-FU02f/carrier_role_visualization_symmetry_orbit_open/bms_fu02f_visualization_nodes.csv
runs/BMS-FU02f/carrier_role_visualization_symmetry_orbit_open/bms_fu02f_visualization_edges.csv
runs/BMS-FU02f/carrier_role_visualization_symmetry_orbit_open/bms_fu02f_visualization_faces.csv
runs/BMS-FU02f/carrier_role_visualization_symmetry_orbit_open/bms_fu02f_region_manifest.json
runs/BMS-FU02f/carrier_role_visualization_symmetry_orbit_open/bms_fu02f_shape_diagnostic_summary.json
runs/BMS-FU02f/carrier_role_visualization_symmetry_orbit_open/bms_fu02f_run_manifest.json
```

C60 audit inputs:

```text
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

---

## 4. Face-ID interval repair

FU02f1 must robustly parse ids of the form:

```text
H_01
H_17
P_09
P_11
```

and also tolerate:

```text
H1
H-01
hex_01
pentagon_09
```

The repaired output should include:

```text
carrier_hexagon_intervals
carrier_pentagon_intervals
mixed_face_intervals
hp_boundary_face_intervals
carrier_adjacent_face_intervals
noncarrier_face_intervals
```

Expected for the current FU02f result:

```text
carrier_hexagon_intervals:
  H_07;H_09;H_11-H_20 with gaps depending on exact set representation

carrier_pentagon_intervals:
  P_07-P_11

mixed_face_intervals:
  H_09;H_11;H_13;H_16-H_20
```

The interval notation is descriptive and based on generated face ids. It is not a physical coordinate system.

---

## 5. Layout exports

FU02f1 produces three kinds of layout artifacts.

### 5.1 Graph layout export

A deterministic circular / shell layout that places:

```text
mixed faces:
  inner ring

hp boundary faces:
  middle ring

carrier-adjacent faces:
  outer ring

noncarrier faces:
  far/background ring
```

This is explicitly non-physical but useful for inspection.

### 5.2 Approximate node layout export

If true 3D C60 coordinates are not available, FU02f1 may produce an approximate deterministic spherical layout from node index order.

Required caveat:

```text
Approximate coordinates are layout coordinates only and must not be used as
physical molecular geometry.
```

### 5.3 SVG inspection map

FU02f1 writes a repaired inspection SVG with:

```text
mixed hexagon core faces
hp boundary faces
carrier-adjacent faces
noncarrier faces
```

The SVG is not a true 3D molecule rendering.

---

## 6. Expected outputs

Output directory:

```text
runs/BMS-FU02f1/face_id_interval_repair_3d_graph_layout_open/
```

Expected files:

```text
bms_fu02f1_repaired_interval_summary.json
bms_fu02f1_face_layout.csv
bms_fu02f1_node_layout.csv
bms_fu02f1_edge_layout.csv
bms_fu02f1_graph_layout_manifest.json
bms_fu02f1_repaired_region_map.svg
bms_fu02f1_run_manifest.json
bms_fu02f1_warnings.json
bms_fu02f1_config_resolved.yaml
```

---

## 7. Interpretation boundary

Allowed:

```text
FU02f1 repairs face-id interval diagnostics and exports layout-ready carrier
region artifacts.
```

Allowed after successful repair:

```text
The face-id interval diagnostics are now consistent with the carrier-face sets.
```

Not allowed:

```text
The layout coordinates are physical C60 coordinates.
A physical belt is proven.
A full C60 automorphism orbit is recovered.
Spacetime geometry is proven.
```

---

## 8. Bridge relevance

FU02f1 improves transparency and inspection quality. It does not strengthen the physical claim by itself.

Bridge-facing cautious statement:

```text
BMS-FU02f1 improves reproducibility and visual inspectability of the compact
role-balanced C60 carrier region by repairing face-id interval diagnostics and
exporting graph-layout-ready artifacts.
```

Internal formulation:

```text
Die Karte wird sauberer.
Der Claim bleibt derselbe.
```

---

## 9. Recommended next after FU02f1

If layout exports are satisfactory:

```text
BMS-FU02g — Fullerene-Family Structural Null Ensemble
```

Purpose:

```text
Move beyond fixed-C60 role-assignment nulls toward stronger fullerene-like
structural null ensembles.
```

Optional communication block:

```text
BMS-FU02viz — Publication-safe carrier map figure
```

Purpose:

```text
Create a defensively labeled figure for internal notes or later documentation.
```
