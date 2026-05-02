# BMS-FU02f1 — Face-ID Interval Repair and 3D/Graph Layout Export Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02F1_FACE_ID_INTERVAL_REPAIR_3D_GRAPH_LAYOUT_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02f1-v0

---

## 1. Purpose

BMS-FU02f1 follows BMS-FU02f.

FU02f made the compact role-balanced carrier region inspectable, but its weak
face-id interval helper returned empty interval fields:

```text
carrier_hexagon_intervals =
carrier_pentagon_intervals =
mixed_face_intervals =
```

FU02f1 repairs this helper and exports layout-ready artifacts.

Internal purpose:

```text
Die Karte wird sauberer.
Der Claim bleibt derselbe.
```

---

## 2. Main result

FU02f1 successfully repairs the face-id interval diagnostics.

Face shells remain consistent with FU02f:

```text
noncarrier_face: 4
carrier_adjacent_face: 11
hp_boundary_face: 9
mixed_seam_boundary_face: 8
```

Counts remain consistent:

```text
faces: 32
nodes: 60
edges: 90
```

Interpretation:

```text
FU02f1 is a successful visualization/diagnostic repair block. It does not
change the FU02f carrier-region claim; it makes the map cleaner and layout-ready.
```

---

## 3. Repaired intervals

Repaired face-id intervals:

```text
carrier_hexagon_intervals =
  H_07;H_09;H_11-H_20

carrier_pentagon_intervals =
  P_07-P_11

mixed_face_intervals =
  H_09;H_11;H_13;H_16-H_20

hp_boundary_face_intervals =
  H_07;H_12;H_14-H_15;P_07-P_11

carrier_adjacent_face_intervals =
  H_04-H_06;H_08;H_10;P_01-P_06

noncarrier_face_intervals =
  H_01-H_03;P_00
```

Interpretation:

```text
The repaired intervals are consistent with the FU02f top-face readout and with
the FU02d1/FU02e/FU02e1 carrier-localization chain.
```

Important caveat:

```text
These intervals are generated face-id diagnostics only. They are not physical
coordinates and should not be interpreted as a molecular geometry axis.
```

Internal wording:

```text
Der kaputte Intervall-Helfer ist geflickt.
Die Face-Landschaft ist jetzt lesbarer.
```

---

## 4. Core and boundary structure

The repaired intervals support the same FU02f picture:

```text
Mixed hexagon core:
  H_09
  H_11
  H_13
  H_16-H_20

Pentagon-rich boundary:
  P_07-P_11

Light hexagon boundary:
  H_07
  H_12
  H_14-H_15
```

Interpretation:

```text
The compact carrier region has an 8-face mixed hexagon core and a one-step
boundary layer involving five pentagons plus four light hexagon boundary faces.
```

Short internal version:

```text
Hexagon-Mixed-Core plus Pentagongrenze.
```

---

## 5. Top layout rows

The role-shell layout places the mixed core on the inner shell.

Mixed core faces:

```text
H_20:
  carrier = 3
  HH = 1
  HP = 2
  dist_core = 0

H_19:
  carrier = 6
  HH = 3
  HP = 3
  dist_core = 0

H_18:
  carrier = 6
  HH = 3
  HP = 3
  dist_core = 0

H_17:
  carrier = 6
  HH = 3
  HP = 3
  dist_core = 0

H_16:
  carrier = 3
  HH = 1
  HP = 2
  dist_core = 0

H_13:
  carrier = 3
  HH = 1
  HP = 2
  dist_core = 0

H_11:
  carrier = 3
  HH = 1
  HP = 2
  dist_core = 0

H_09:
  carrier = 3
  HH = 1
  HP = 2
  dist_core = 0
```

Boundary pentagon faces:

```text
P_11:
  carrier = 5
  HP = 5
  dist_core = 1

P_10:
  carrier = 5
  HP = 5
  dist_core = 1

P_09:
  carrier = 5
  HP = 5
  dist_core = 1

P_08:
  carrier = 4
  HP = 4
  dist_core = 1

P_07:
  carrier = 4
  HP = 4
  dist_core = 1
```

Light hexagon boundary faces:

```text
H_15:
  carrier = 1
  HP = 1
  dist_core = 1

H_14:
  carrier = 1
  HP = 1
  dist_core = 1

H_12:
  carrier = 1
  HP = 1
  dist_core = 1

H_07:
  carrier = 1
  HP = 1
  dist_core = 1
```

Interpretation:

```text
The layout export preserves the FU02f role structure: a mixed hexagon core and
a pentagon-rich boundary layer at distance one.
```

---

## 6. Layout caveat

FU02f1 produces inspection layouts:

```text
role-shell circular face layout
deterministic spherical index node layout
edge layout based on deterministic node coordinates
```

These are not physical C60 coordinates.

Allowed:

```text
layout-ready inspection artifacts
```

Not allowed:

```text
physical 3D C60 geometry
physical belt proof
automorphism orbit proof
```

Recommended wording:

```text
FU02f1 provides layout-ready inspection coordinates, not molecular coordinates.
```

---

## 7. Bridge interpretation

FU02f1 does not strengthen the physical claim by itself. It strengthens
transparency and reproducibility.

Previous chain:

```text
FU02e1:
  Near-real null profiles absent.

FU02f:
  Carrier region appears as mixed hexagon core plus pentagon-rich boundary.

FU02f1:
  Interval diagnostics are repaired and layout exports are now available.
```

Bridge-facing cautious statement:

```text
BMS-FU02f1 repairs the FU02f face-id interval diagnostics and exports
layout-ready artifacts for the compact role-balanced C60 carrier region. The
repaired intervals are consistent with the previously identified mixed hexagon
core and pentagon-rich boundary layer. The block improves inspection quality and
reproducibility without adding a new physical claim.
```

Internal formulation:

```text
Der Klunker war schon da.
Jetzt ist die Karte sauberer.
```

---

## 8. What FU02f1 does NOT prove

FU02f1 does not prove:

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

FU02f1 also does not prove:

```text
true molecular C60 coordinates
automorphism-group orbit structure
fullerene-family specificity
```

because:

```text
the generated layouts are inspection layouts only.
```

---

## 9. Allowed result statement

Allowed:

```text
BMS-FU02f1 repairs the FU02f face-id interval diagnostics and confirms that the
layout-ready carrier region is consistent with the previous compact
core-plus-boundary picture. The repaired intervals identify a mixed hexagon core
at H_09, H_11, H_13 and H_16-H_20, and a pentagon-rich boundary at P_07-P_11
with additional light hexagon boundary faces H_07, H_12 and H_14-H_15.
```

Short allowed version:

```text
FU02f1 fixes the interval helper and makes the compact carrier map layout-ready.
```

Internal:

```text
Der Intervall-Helfer ist repariert.
Der Hexagon-Kern und die Pentagongrenze bleiben stehen.
```

---

## 10. Recommended next block

Recommended next:

```text
BMS-FU02g — Fullerene-Family Structural Null Ensemble
```

Purpose:

```text
Move beyond fixed-C60 role-assignment nulls and test whether comparable compact
role-balanced regions appear in stronger fullerene-like structural null
ensembles.
```

Why now?

```text
The fixed-C60 chain from FU02c through FU02f1 is internally consistent:
  representation roles
  connected edge/node network
  connected face region
  compact null localization
  role-balance specificity
  visualization/layout repair

The next methodological question is structural generality/specificity beyond
fixed-C60 role assignment.
```

Optional later communication block:

```text
BMS-FU02viz — Publication-safe carrier map figure
```

Purpose:

```text
Generate a defensively labeled figure for documentation, clearly marked as a
graph-layout illustration rather than physical molecular geometry.
```

---

## 11. Internal summary

```text
FU02f1:

  Face shells:
    mixed = 8
    hp_boundary = 9
    adjacent = 11
    noncarrier = 4

  Repaired intervals:
    carrier hexagons:
      H_07;H_09;H_11-H_20

    carrier pentagons:
      P_07-P_11

    mixed core:
      H_09;H_11;H_13;H_16-H_20

    hp boundary:
      H_07;H_12;H_14-H_15;P_07-P_11

  Counts:
    faces = 32
    nodes = 60
    edges = 90

Kern:
  Hexagon-Mixed-Core plus Pentagongrenze bleibt stabil.
  Der kaputte Helper ist repariert.
  Die Karte ist layout-fähig.

Grenze:
  Keine physische 3D-Geometrie.
  Kein Symmetriebeweis.
  Kein Raumzeitbeweis.
```

---

## 12. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02F1_FACE_ID_INTERVAL_REPAIR_3D_GRAPH_LAYOUT_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02F1_FACE_ID_INTERVAL_REPAIR_3D_GRAPH_LAYOUT_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02F1_FACE_ID_INTERVAL_REPAIR_3D_GRAPH_LAYOUT_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02f1 layout repair result note"

git push
```
