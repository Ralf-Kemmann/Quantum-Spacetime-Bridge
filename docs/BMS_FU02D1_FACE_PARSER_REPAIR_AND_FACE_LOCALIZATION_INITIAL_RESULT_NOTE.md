# BMS-FU02d1 — Face Parser Repair and Face-Level Carrier Localization Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02D1_FACE_PARSER_REPAIR_AND_FACE_LOCALIZATION_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02d1-v0

---

## 1. Purpose

BMS-FU02d1 follows BMS-FU02d.

FU02d found a connected seam-boundary carrier network at edge/node/component level:

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

FU02d1 repairs the face parser and maps the carrier network onto C60 faces.

Internal purpose:

```text
Jetzt prüfen wir, auf welchen Faces dieses Netz liegt.
```

---

## 2. Parser repair result

The face parser repair succeeded.

Parser audit:

```json
{
  "detected_edge_face_columns": [
    "shared_faces"
  ],
  "detected_face_node_column": "",
  "edge_face_mapping_source": "edge_table_list_column",
  "face_count": 32,
  "mapped_edge_count": 90,
  "unmapped_edge_count": 0,
  "warnings": []
}
```

Interpretation:

```text
FU02d1 detected the edge-table field `shared_faces` and used it as a list-like
edge-to-face incidence column. All 90 C60 edges were mapped to faces.
```

This repairs the FU02d-v0 face-level problem.

Allowed statement:

```text
FU02d1 provides a valid face-level carrier localization based on complete
90/90 edge-to-face mapping.
```

---

## 3. Run manifest

Run:

```text
BMS-FU02d1_face_parser_repair_and_face_localization_open
```

Output directory:

```text
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open
```

Core manifest values:

```json
{
  "c60_valid": true,
  "face_parser_source": "edge_table_list_column",
  "detected_edge_face_columns": [
    "shared_faces"
  ],
  "mapped_edge_count": 90,
  "unmapped_edge_count": 0,
  "face_count": 32,
  "carrier_face_count": 17,
  "carrier_face_fraction": 0.53125,
  "carrier_face_component_count": 1,
  "largest_carrier_face_component_count": 17,
  "carrier_face_type_counts": {
    "H": 12,
    "P": 5
  },
  "face_label_counts": {
    "carrier_adjacent_face": 11,
    "hp_boundary_face": 9,
    "mixed_seam_boundary_face": 8,
    "noncarrier_face": 4
  },
  "region_label": "connected_face_region_candidate"
}
```

Warning:

```text
info - FU02d warnings carried forward: 1
```

Interpretation:

```text
The warning is inherited from FU02d and is not a FU02d1 parser failure.
```

---

## 4. Main face-level result

The seam-boundary carrier network is localized on a connected face region:

```text
carrier_face_count = 17 / 32
carrier_face_fraction = 0.53125
carrier_face_component_count = 1
largest_carrier_face_component_count = 17
region_label = connected_face_region_candidate
```

Carrier face types:

```text
12 hexagons
5 pentagons
```

Face role labels:

```text
mixed_seam_boundary_face = 8
hp_boundary_face = 9
carrier_adjacent_face = 11
noncarrier_face = 4
```

Core interpretation:

```text
The 30-edge / 25-node seam-boundary carrier network maps to one connected
17-face region on the C60 cage.
```

Internal image:

```text
Das Netz liegt nicht als lose Fäden irgendwo im Ball.
Es liegt auf einer zusammenhängenden Face-Region.
```

---

## 5. Carrier face components

The carrier face component structure is clean:

```text
CARRIER_FACE_SET:
  component_count = 1
  faces = 17
  hexagons = 12
  pentagons = 5
  carrier_edge_incidence = 60
  mixed_role_junction_incidence = 42
```

The face ids are:

```text
H_07
H_09
H_11
H_12
H_13
H_14
H_15
H_16
H_17
H_18
H_19
H_20
P_07
P_08
P_09
P_10
P_11
```

Interpretation:

```text
The carrier network does not occupy all C60 faces. It occupies a connected
subregion involving 12 of 20 hexagons and 5 of 12 pentagons.
```

Cautious wording:

```text
FU02d1 supports a connected carrier-face region candidate. It does not by
itself prove a physical belt or global fullerene symmetry.
```

---

## 6. Mixed seam-boundary faces

The mixed face set is:

```text
MIXED_FACE_SET:
  component_count = 1
  faces = 8
  hexagons = 8
  pentagons = 0
```

Mixed faces:

```text
H_09
H_11
H_13
H_16
H_17
H_18
H_19
H_20
```

These faces carry both H,H seam anchors and H,P boundary carriers.

Top mixed faces:

```text
H_17:
  HH = 3
  HP = 3
  carrier = 6
  mixed_nodes = 6
  edges =
    c60_039--c60_040
    c60_039--c60_043
    c60_040--c60_057
    c60_043--c60_045
    c60_045--c60_058
    c60_057--c60_058

H_18:
  HH = 3
  HP = 3
  carrier = 6
  mixed_nodes = 6
  edges =
    c60_044--c60_045
    c60_044--c60_048
    c60_045--c60_058
    c60_048--c60_050
    c60_050--c60_059
    c60_058--c60_059

H_19:
  HH = 3
  HP = 3
  carrier = 6
  mixed_nodes = 6
  edges =
    c60_049--c60_050
    c60_049--c60_054
    c60_050--c60_059
    c60_054--c60_055
    c60_055--c60_060
    c60_059--c60_060
```

Interpretation:

```text
H_17, H_18 and H_19 are especially strong mixed seam-boundary faces: each has
three H,H/H,P role-pair structure, six carrier edges and six mixed-role junction
nodes.
```

Internal image:

```text
H_17, H_18 und H_19 sind die dicken Knotenplatten im Gewebe.
```

---

## 7. H,H face localization

HH_FACE_SET:

```text
faces = 8
hexagons = 8
pentagons = 0
```

Face ids:

```text
H_09
H_11
H_13
H_16
H_17
H_18
H_19
H_20
```

Interpretation:

```text
All H,H seam-anchor face involvement lies on hexagons.
```

This is consistent with the C60 construction:

```text
H,H / 6:6 edges are shared between two hexagons, so H,H carrier faces are
hexagonal.
```

The more interesting result is not merely that H,H touches hexagons, but that:

```text
the H,H-involved hexagon faces form one connected mixed-face component.
```

---

## 8. H,P boundary face localization

HP_FACE_SET:

```text
faces = 17
hexagons = 12
pentagons = 5
```

Face ids:

```text
H_07
H_09
H_11
H_12
H_13
H_14
H_15
H_16
H_17
H_18
H_19
H_20
P_07
P_08
P_09
P_10
P_11
```

Top pentagon boundary faces:

```text
P_09:
  HP = 5
  carrier = 5
  mixed_nodes = 3
  edges =
    c60_046--c60_047
    c60_046--c60_048
    c60_047--c60_049
    c60_048--c60_050
    c60_049--c60_050

P_10:
  HP = 5
  carrier = 5
  mixed_nodes = 2
  edges =
    c60_051--c60_052
    c60_051--c60_053
    c60_052--c60_054
    c60_053--c60_055
    c60_054--c60_055

P_11:
  HP = 5
  carrier = 5
  mixed_nodes = 4
  edges =
    c60_056--c60_057
    c60_056--c60_060
    c60_057--c60_058
    c60_058--c60_059
    c60_059--c60_060

P_07:
  HP = 4
  carrier = 4
  mixed_nodes = 2

P_08:
  HP = 4
  carrier = 4
  mixed_nodes = 3
```

Interpretation:

```text
The H,P boundary carrier layer strongly involves a five-pentagon subset,
especially P_09, P_10 and P_11.
```

Internal image:

```text
Die H,P-Grenzträger laufen über eine Pentagongruppe und koppeln dort an die
H,H-Hexagon-Nähte.
```

---

## 9. Connected face-region interpretation

FU02d1 supports the following role geometry:

```text
H,H seam anchors:
  localized on an 8-hexagon mixed face component.

H,P boundary carriers:
  extend this structure to a 17-face connected region containing 12 hexagons
  and 5 pentagons.

Combined carrier faces:
  one connected 17-face region.
```

This is more specific than FU02d:

```text
FU02d:
  one connected 30-edge / 25-node carrier network.

FU02d1:
  that network lies on one connected 17-face region.
```

Internal summary:

```text
Das Gewebe ist nicht nur im Kantengraphen zusammenhängend.
Es liegt auch auf einer zusammenhängenden Face-Landschaft.
```

---

## 10. Bridge interpretation

FU02d1 strengthens the methodological carrier-role result.

FU02c separated roles:

```text
H,H = seam role
H,P = boundary role
```

FU02d showed:

```text
the roles form one connected edge/node carrier network.
```

FU02d1 now shows:

```text
the same carrier network maps to one connected face region.
```

Bridge-facing cautious statement:

```text
BMS-FU02d1 repairs the face-level parser and maps the FU02d seam-boundary
carrier network onto C60 face incidence. The 30-edge / 25-node carrier network
is localized on a single connected 17-face region involving 12 hexagons and
5 pentagons. The H,H seam-anchor faces form an 8-hexagon mixed component, while
the H,P boundary carriers extend the region across a five-pentagon boundary
subset. This supports the methodological view that role-differentiated
relational carrier information can organize across edges, nodes and
higher-order face incidence.
```

Short internal statement:

```text
Die Nahtpunkte liegen auf Hexagonflächen.
Das Grenzgewebe läuft über Pentagone mit.
Zusammen entsteht eine zusammenhängende Face-Landschaft.
```

---

## 11. What FU02d1 does NOT prove

FU02d1 does not prove:

```text
physical spacetime geometry
a physical metric
global C60 symmetry recovery
molecular recognition
quantum chemistry
that carrier edges or faces are physical spacetime atoms
```

FU02d1 also does not prove:

```text
null-specific localization
a physical belt
a unique fullerene symmetry orbit
```

because these require further null-localization and/or visualization checks.

Allowed wording:

```text
connected_face_region_candidate
```

Not yet allowed as hard claim:

```text
physical belt
global cage belt
symmetry orbit
```

---

## 12. Result statement

Allowed:

```text
BMS-FU02d1 repairs the FU02d face parser using the `shared_faces` edge-table
field and maps all 90 C60 edges to faces. The FU02d seam-boundary carrier
network occupies one connected 17-face region containing 12 hexagons and
5 pentagons. H,H seam-anchor involvement is confined to an 8-hexagon mixed
component, while H,P boundary carriers extend the connected carrier-face region
through a five-pentagon subset.
```

Short version:

```text
FU02d1 shows that the seam-boundary carrier network lies on one connected
17-face region of the C60 cage.
```

Internal version:

```text
Das Netz hängt nicht nur als Kantenmuster zusammen.
Es sitzt auf einer zusammenhängenden Landschaft aus 17 Faces.
```

---

## 13. Recommended next block

Recommended next:

```text
BMS-FU02e — Carrier Role Null Localization Test
```

Purpose:

```text
Test whether comparable connected 17-face seam-boundary regions appear in null
graphs, or whether the real C60 carrier-role geometry is localization-specific.
```

Key questions:

```text
1. Do null carrier sets also form one connected face region?
2. Do null carrier sets also occupy ~17 faces?
3. Do nulls reproduce an 8-hexagon H,H mixed component?
4. Do nulls reproduce the five-pentagon H,P boundary subset?
5. Is the real carrier-face region unusually compact, unusually connected, or
   unusually role-organized?
```

Alternative visualization support block:

```text
BMS-FU02viz — C60 Carrier Role Visualization Export
```

Purpose:

```text
Export visualization-ready node/edge/face tables for plotting the carrier
region as a cage map.
```

Suggested order:

```text
1. FU02e for null-localization specificity.
2. Visualization export for communication and inspection.
```

---

## 14. Internal summary

```text
FU02d:
  Das Netz hängt im Kantengraphen zusammen.

FU02d1:
  Der Face-Parser ist repariert:
    shared_faces erkannt
    90/90 edges gemappt
    0 unmapped

  Carrier-Faces:
    17 / 32 faces
    12 Hexagone
    5 Pentagone
    1 connected component

  Mixed seam-boundary faces:
    8 Hexagone

  H,P boundary:
    fünf Pentagone beteiligt,
    besonders P_09, P_10, P_11

Kern:
  Die Nahtpunkte liegen auf Hexagonflächen.
  Das Grenzgewebe läuft über Pentagone mit.
  Zusammen entsteht eine verbundene Face-Landschaft.

Grenze:
  Noch kein Null-Lokalisierungsbeweis.
  Noch keine globale Symmetrie.
  Noch keine physikalische Raumzeit.
```

---

## 15. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02D1_FACE_PARSER_REPAIR_AND_FACE_LOCALIZATION_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02D1_FACE_PARSER_REPAIR_AND_FACE_LOCALIZATION_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02D1_FACE_PARSER_REPAIR_AND_FACE_LOCALIZATION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02d1 face localization result note"

git push
```
