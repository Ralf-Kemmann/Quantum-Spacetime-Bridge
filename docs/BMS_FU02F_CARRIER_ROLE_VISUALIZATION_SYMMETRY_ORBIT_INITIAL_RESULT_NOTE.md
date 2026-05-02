# BMS-FU02f — Carrier Role Visualization and Symmetry-Orbit Inspection Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02F_CARRIER_ROLE_VISUALIZATION_SYMMETRY_ORBIT_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02f-v0

---

## 1. Purpose

BMS-FU02f follows BMS-FU02e1.

FU02e1 established:

```text
near_real_profile_count = 0 / 2000
strict_near_real_profile_count = 0 / 2000
```

Meaning:

```text
No tested fixed-C60 role-assignment null reproduced the near-real compact
role-balance profile.
```

FU02f makes the compact role-balanced carrier region inspectable.

Internal purpose:

```text
Jetzt zeichnen wir die Rollenfarbe auf den Käfig.
```

---

## 2. Main visualization readout

Face labels:

```text
noncarrier_face: 4
carrier_adjacent_face: 11
hp_boundary_face: 9
mixed_seam_boundary_face: 8
```

Edge roles:

```text
OTHER: 60
HP_SECONDARY: 23
HH_CONSENSUS: 7
```

Node roles:

```text
noncarrier_node: 35
hp_boundary_node: 11
mixed_role_junction: 14
```

These values are consistent with the previous FU02d/FU02d1/FU02e1 chain.

---

## 3. Carrier region structure

The key face-distance result is:

```text
Carrier faces by distance to mixed core:
  distance 0: 8
  distance 1: 9

max_distance_to_mixed_core = 1
mean_distance_to_mixed_core = 0.5294117647058824
```

Interpretation:

```text
All carrier faces are either part of the mixed seam-boundary core or directly
adjacent to it.
```

This is stronger than merely saying the region is connected.

Allowed wording:

```text
FU02f supports a compact core-plus-boundary carrier-face structure: eight mixed
hexagon faces form the role-mixed core, and nine boundary carrier faces lie at
face-adjacency distance one.
```

Internal short version:

```text
Der Klunker hat einen Kern und eine direkte Randlage.
Nichts vom Carrier-Gebiet liegt weiter als einen Face-Schritt weg.
```

---

## 4. Mixed seam-boundary core

The mixed core consists of:

```text
8 mixed_seam_boundary_face faces
```

The strongest three are:

```text
H_17:
  carrier = 6
  HH = 3
  HP = 3
  mixed_nodes = 6
  dist_core = 0

H_18:
  carrier = 6
  HH = 3
  HP = 3
  mixed_nodes = 6
  dist_core = 0

H_19:
  carrier = 6
  HH = 3
  HP = 3
  mixed_nodes = 6
  dist_core = 0
```

Additional mixed faces:

```text
H_09:
  carrier = 3
  HH = 1
  HP = 2
  mixed_nodes = 2

H_11:
  carrier = 3
  HH = 1
  HP = 2
  mixed_nodes = 2

H_13:
  carrier = 3
  HH = 1
  HP = 2
  mixed_nodes = 2

H_16:
  carrier = 3
  HH = 1
  HP = 2
  mixed_nodes = 2

H_20:
  carrier = 3
  HH = 1
  HP = 2
  mixed_nodes = 2
```

Interpretation:

```text
The mixed core is hexagon-based and contains three high-density mixed faces
H_17/H_18/H_19, each with six carrier edges and six mixed-role junction nodes.
```

Internal image:

```text
H_17, H_18 und H_19 sind die dicken Knotenplatten im Gewebe.
```

---

## 5. Boundary layer

Boundary carrier faces at distance 1 from the mixed core:

```text
P_09:
  HP = 5
  carrier = 5
  mixed_nodes = 3

P_10:
  HP = 5
  carrier = 5
  mixed_nodes = 2

P_11:
  HP = 5
  carrier = 5
  mixed_nodes = 4

P_07:
  HP = 4
  carrier = 4
  mixed_nodes = 2

P_08:
  HP = 4
  carrier = 4
  mixed_nodes = 3

H_07:
  HP = 1
  carrier = 1
  mixed_nodes = 0

H_12:
  HP = 1
  carrier = 1
  mixed_nodes = 0

H_14:
  HP = 1
  carrier = 1
  mixed_nodes = 0

H_15:
  HP = 1
  carrier = 1
  mixed_nodes = 0
```

Interpretation:

```text
The boundary layer is dominated by five pentagon faces P_07/P_08/P_09/P_10/P_11,
with the strongest boundary carrier load on P_09/P_10/P_11.
```

Internal image:

```text
Die H,P-Grenzträger laufen als Pentagongruppe direkt um den Mixed-Hexagon-Kern.
```

---

## 6. Face-adjacency diagnostics

Graph-level adjacency diagnostics:

```text
carrier_face_internal_adjacency_count = 37
carrier_face_boundary_adjacency_count = 23
carrier_face_external_neighbor_count = 11
```

Interpretation:

```text
The carrier region has substantial internal face adjacency and a finite
boundary to surrounding noncarrier/adjacent faces. This supports a compact
connected region reading rather than a scattered carrier-face distribution.
```

Important boundary:

```text
This is a graph-level face-adjacency statement, not a 3D geometric curvature or
physical belt proof.
```

---

## 7. Face-ID interval diagnostic issue

FU02f-v0 returned empty interval diagnostics:

```text
carrier_hexagon_intervals =
carrier_pentagon_intervals =
mixed_face_intervals =
```

This is inconsistent with the correctly reported face lists and top carrier
faces.

Interpretation:

```text
The face-id interval helper is not reliable in FU02f-v0.
```

Likely cause:

```text
The helper that extracts numeric face indices did not parse the H_17 / P_09
style ids correctly.
```

This does not affect:

```text
face labels
carrier counts
edge roles
node roles
face distance to mixed core
internal/boundary adjacency counts
top carrier face readout
```

Therefore:

```text
Do not use the empty interval diagnostics as evidence.
```

Required correction:

```text
FU02f1 should repair the face-id interval helper or move directly to 3D/graph
layout visualization where face ids are not used as geometric evidence.
```

---

## 8. Shape interpretation

FU02f-v0 supports:

```text
compact core-plus-boundary carrier-face region
```

or more cautiously:

```text
connected compact face-region candidate with a mixed hexagon core and pentagon
boundary layer.
```

It does not yet support a hard label such as:

```text
physical belt
global orbit
symmetry orbit
full C60 automorphism structure
```

The best current description is:

```text
The compact 17-face region has an 8-face mixed hexagon core and a one-step
boundary layer dominated by five pentagons.
```

Internal summary:

```text
Der Klunker ist kein loser Staub.
Er ist ein kompakter Kern mit direkter Randlage.
```

---

## 9. Bridge interpretation

FU02f improves interpretability of the already established specificity chain.

Previous chain:

```text
FU02c:
  seam and boundary roles separate by representation.

FU02d:
  seam and boundary roles form one connected edge/node carrier network.

FU02d1:
  the network maps to one connected 17-face region.

FU02e:
  nulls reproduce connectedness but usually over-spread.

FU02e1:
  no tested null reproduces the compact role-balance profile.

FU02f:
  the real region is inspectable as a compact core-plus-boundary face complex.
```

Bridge-facing cautious statement:

```text
BMS-FU02f makes the compact role-balanced C60 carrier region inspectable as a
graph-geometric face complex. The carrier faces split into an 8-face mixed
hexagon core and a 9-face boundary layer at distance one, dominated by five
pentagons. This supports transparent interpretation of the carrier signal as a
localized role-organized graph structure, while remaining below any claim of
physical spacetime geometry or full C60 symmetry recovery.
```

Short internal statement:

```text
Die Rollenfarbe sitzt als kompakter Klunker im Käfig:
Hexagon-Mixed-Core, Pentagongrenze außen herum.
```

---

## 10. What FU02f does NOT prove

FU02f does not prove:

```text
physical spacetime geometry
a physical metric
global C60 symmetry recovery
a physical belt
a symmetry orbit
molecular recognition
quantum chemistry
that carrier edges or faces are physical spacetime atoms
```

FU02f also does not yet prove:

```text
3D geometric shape of the carrier region
automorphism-group orbit structure
fullerene-family specificity
```

because:

```text
FU02f-v0 uses graph-level face adjacency and a non-geometric inspection map.
```

---

## 11. Allowed result statement

Allowed:

```text
BMS-FU02f maps the FU02e1-supported compact role-balanced carrier region into
visualization-ready node, edge and face artifacts. The carrier-face structure
has an 8-face mixed seam-boundary core and a 9-face boundary layer at
face-adjacency distance one. The mixed core is hexagon-based, with H_17, H_18
and H_19 as the highest-load mixed faces, while the boundary layer is dominated
by five pentagon faces. This supports a compact core-plus-boundary graph
interpretation, not a physical belt or full symmetry-orbit claim.
```

Short allowed version:

```text
FU02f shows a compact mixed-hexagon core with a one-step pentagon-rich boundary
layer.
```

Internal:

```text
Der Klunker hat einen Hexagon-Kern und eine Pentagongrenze.
```

---

## 12. Recommended next block

Recommended next:

```text
BMS-FU02f1 — Face-ID Interval Repair and 3D/Graph Layout Export
```

Purpose:

```text
Repair the face-id interval helper and export a graph/3D-layout-ready map for
visual inspection.
```

Minimum repair:

```text
Fix numeric parsing of face ids such as H_17 and P_09.
```

Better extension:

```text
Export layout-ready tables for:
  networkx spring layout
  approximate C60 3D coordinates
  Gephi/Cytoscape import
```

After visualization hardening:

```text
BMS-FU02g — Fullerene-Family Structural Null Ensemble
```

Purpose:

```text
Test whether comparable compact role-balanced regions appear in stronger
fullerene-like structural null ensembles.
```

---

## 13. Internal summary

```text
FU02f:

  Face labels:
    mixed = 8
    hp_boundary = 9
    adjacent = 11
    noncarrier = 4

  Carrier faces:
    distance to mixed core:
      8 at distance 0
      9 at distance 1
      none beyond distance 1

  Strong mixed faces:
    H_17, H_18, H_19
    each: carrier=6, HH=3, HP=3, mixed_nodes=6

  Boundary:
    P_09, P_10, P_11 strongest
    P_07, P_08 also boundary
    H_07/H_12/H_14/H_15 light boundary

  Core:
    mixed hexagon core

  Boundary:
    pentagon-rich one-step layer

  Caveat:
    face-id interval helper blank / not reliable

Kern:
  Hexagon-Mixed-Core plus Pentagongrenze.
  Kein loser Fleck.
  Kein Symmetriebeweis.
```

---

## 14. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02F_CARRIER_ROLE_VISUALIZATION_SYMMETRY_ORBIT_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02F_CARRIER_ROLE_VISUALIZATION_SYMMETRY_ORBIT_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02F_CARRIER_ROLE_VISUALIZATION_SYMMETRY_ORBIT_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02f visualization result note"

git push
```
