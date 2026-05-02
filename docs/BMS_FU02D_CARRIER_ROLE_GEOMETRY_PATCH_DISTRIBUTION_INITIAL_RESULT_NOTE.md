# BMS-FU02d — Carrier Role Geometry and Patch Distribution Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02D_CARRIER_ROLE_GEOMETRY_PATCH_DISTRIBUTION_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02d-v0

---

## 1. Purpose

BMS-FU02d follows BMS-FU02c.

FU02c separated two representation-dependent carrier roles:

```text
H,H / 6:6:
  seam carriers in the bond-class-weighted layer

H,P / 5:6:
  boundary carriers in the topology-only and graph-distance layers
```

FU02d asks:

```text
Wo sitzen diese Rollen im C60-Käfig?
```

Internal shorthand:

```text
FU02c:
  Es gibt Naht-Träger und Grenz-Träger.

FU02d:
  Bilden sie ein Gewebe?
```

---

## 2. Run manifest

Run:

```text
BMS-FU02d_carrier_role_geometry_patch_distribution_open
```

Output directory:

```text
runs/BMS-FU02d/carrier_role_geometry_patch_distribution_open
```

Core manifest values:

```json
{
  "c60_valid": true,
  "hh_consensus_edge_count": 7,
  "hp_secondary_edge_count": 23,
  "role_carrier_edge_count": 30,
  "component_group_row_counts": {
    "HH_CONSENSUS": 7,
    "HH_PLUS_HP": 1,
    "HP_SECONDARY": 5
  },
  "largest_combined_component_edge_count": 30,
  "largest_combined_component_node_count": 25,
  "hp_edges_adjacent_to_hh_count": 19,
  "hp_edges_adjacent_to_hh_fraction": 0.8260869565217391,
  "hh_edges_with_adjacent_hp_count": 7,
  "hh_edges_with_adjacent_hp_fraction": 1.0,
  "hp_shell_distance_to_hh_counts": {
    "1": 19,
    "2": 4
  },
  "node_label_counts": {
    "hp_boundary_node": 11,
    "mixed_role_junction": 14,
    "noncarrier_node": 35
  }
}
```

Warning:

```text
info - FU02c warnings carried forward: 2
```

Interpretation:

```text
This warning is inherited from FU02c and refers to skipped graph_distance_shells
contexts. It is not a FU02d data failure.
```

---

## 3. Main result

FU02d gives a clear seam-boundary geometry result.

The seven H,H consensus edges are isolated if considered alone:

```text
HH_CONSENSUS:
  7 components
  each component has 1 edge and 2 nodes
```

The H,P secondary carrier set has five local components:

```text
HP_SECONDARY:
  5 components
  component edge counts: 5, 5, 5, 4, 4
```

But the combined carrier-role graph is one connected component:

```text
HH_PLUS_HP:
  component_count = 1
  edge_count = 30
  node_count = 25
  H,H edges = 7
  H,P edges = 23
```

Core interpretation:

```text
H,H consensus carriers are not an isolated connected spine by themselves.
They become connected through H,P secondary carriers.
```

Internal image:

```text
H-H sind die starken Nahtpunkte.
H-P ist das Grenzgewebe, das die Nahtpunkte verbindet.
```

Key FU02d refinement:

```text
The carrier geometry is not a single H,H patch. It is a connected seam-boundary
network in which H,P boundary carriers bridge distributed H,H seam carriers.
```

---

## 4. Adjacency result

Adjacency between H,H consensus and H,P secondary carriers is strong.

```text
hp_edges_adjacent_to_hh_count = 19 / 23
hp_edges_adjacent_to_hh_fraction = 0.8260869565217391
```

and:

```text
hh_edges_with_adjacent_hp_count = 7 / 7
hh_edges_with_adjacent_hp_fraction = 1.0
```

Shell distance of H,P secondary edges to nearest H,H consensus edge:

```text
shell distance 1: 19
shell distance 2: 4
```

Interpretation:

```text
All H,H consensus carriers touch the H,P boundary layer. Most H,P secondary
carriers are directly adjacent to an H,H consensus carrier; the remaining four
are only one further edge step away.
```

Better wording:

```text
FU02d supports a connected seam-boundary carrier network, not a purely connected
H,H spine.
```

---

## 5. Component structure

### 5.1 H,H consensus components

Each H,H consensus edge is an isolated one-edge component when H,H is analyzed alone:

```text
c60_039--c60_043
c60_040--c60_057
c60_044--c60_048
c60_045--c60_058
c60_049--c60_054
c60_050--c60_059
c60_055--c60_060
```

Interpretation:

```text
The all-representation H,H carriers are distributed anchors rather than a
single H,H-only patch.
```

### 5.2 H,P secondary components

H,P secondary carriers form five local boundary components:

```text
component 1:
  c60_046--c60_047
  c60_046--c60_048
  c60_047--c60_049
  c60_048--c60_050
  c60_049--c60_050

component 2:
  c60_051--c60_052
  c60_051--c60_053
  c60_052--c60_054
  c60_053--c60_055
  c60_054--c60_055

component 3:
  c60_056--c60_057
  c60_056--c60_060
  c60_057--c60_058
  c60_058--c60_059
  c60_059--c60_060

component 4:
  c60_036--c60_038
  c60_037--c60_039
  c60_038--c60_040
  c60_039--c60_040

component 5:
  c60_041--c60_043
  c60_042--c60_044
  c60_043--c60_045
  c60_044--c60_045
```

Interpretation:

```text
The H,P layer is locally componentized, but its components bridge the H,H
consensus anchors in the combined carrier network.
```

### 5.3 Combined component

The combined H,H + H,P set is one connected component:

```text
edge_count = 30
node_count = 25
H,H = 7
H,P = 23
```

This is the strongest FU02d result.

Internal summary:

```text
Alle Rollenfäden zusammen ergeben ein einziges Gewebe.
```

---

## 6. Node-level role junctions

Node labels:

```text
mixed_role_junction: 14
hp_boundary_node: 11
noncarrier_node: 35
```

There are no pure `hh_spine_node` labels because every H,H consensus edge endpoint is also incident to H,P secondary structure.

Top mixed role junctions all have:

```text
HH = 1
HP = 2
total = 3
```

Examples:

```text
c60_039:
  HH = 1
  HP = 2
  carrier edges =
    c60_037--c60_039
    c60_039--c60_040
    c60_039--c60_043

c60_040:
  HH = 1
  HP = 2
  carrier edges =
    c60_038--c60_040
    c60_039--c60_040
    c60_040--c60_057

c60_054:
  HH = 1
  HP = 2
  carrier edges =
    c60_049--c60_054
    c60_052--c60_054
    c60_054--c60_055

c60_060:
  HH = 1
  HP = 2
  carrier edges =
    c60_055--c60_060
    c60_056--c60_060
    c60_059--c60_060
```

Interpretation:

```text
The carrier network has 14 mixed-role junction nodes. These nodes are not simply
H,H endpoints; they are junctions where one seam carrier and two boundary
carriers meet.
```

Internal image:

```text
Die Last liegt nicht nur auf Kanten.
Sie sitzt an Knotenpunkten, wo Naht und Grenze zusammenlaufen.
```

Bridge-relevant statement:

```text
FU02d suggests that role-differentiated relational information is organized
through mixed carrier junctions, not only through isolated high-scoring edges.
```

---

## 7. Face-level output issue

FU02d-v0 reports:

```text
face_label_counts:
  noncarrier_face = 32
```

and all faces show:

```text
HH = 0
HP = 0
total = 0
```

This is inconsistent with the valid edge-level and component-level carrier geometry.

Interpretation:

```text
The FU02d-v0 face-level table is not reliable.
```

Likely cause:

```text
The runner's face parser did not match the face-annotation field structure in
the C60 edge table, so face involvement was not populated.
```

This does not invalidate the edge-, node-, and component-level results.

However, face-level claims must not be made from FU02d-v0.

Required correction:

```text
FU02d1 should inspect the actual C60 edge-table face columns and repair the
face-involvement parser.
```

Until corrected:

```text
Do not claim face patch localization.
Do not claim face-level carrier absence.
```

Important wording:

```text
FU02d-v0 supports edge-, node-, and component-level seam-boundary carrier
organization. Face-level localization remains unresolved due to a parser issue.
```

---

## 8. Bridge interpretation

FU02d strengthens the role-structure interpretation.

FU02c showed:

```text
H,H / 6:6:
  weighted seam role

H,P / 5:6:
  topology/distance boundary role
```

FU02d now shows:

```text
The two roles are not independent fragments.
Together they form one connected 30-edge / 25-node carrier network.
```

This supports the Bridge-relevant idea:

```text
Geometry-readable relational information can be role-differentiated and
graph-organized at the same time.
```

Cautious bridge-facing statement:

```text
BMS-FU02d maps the FU02c carrier roles on the validated C60 graph and finds a
connected seam-boundary carrier network. The seven H,H all-representation
consensus edges are individually disconnected, but all are adjacent to H,P
secondary carriers, and together with the H,P layer they form a single
30-edge / 25-node connected component. This suggests that the carrier signal is
organized as a seam-boundary graph pattern rather than as isolated edges.
```

Short internal statement:

```text
Die Nahtpunkte sind verteilt.
Das Grenzgewebe verbindet sie.
Zusammen entsteht ein tragendes Netz.
```

---

## 9. What FU02d does NOT prove

FU02d does not prove:

```text
global C60 symmetry recovery
physical spacetime geometry
a physical metric
molecular recognition
quantum chemistry
that carrier edges are physical spacetime atoms
```

FU02d-v0 also does not yet support:

```text
face-level patch claims
face-level absence claims
true fullerene-preserving null localization
global cage-symmetry claims
```

because:

```text
the face-level parser needs correction.
```

---

## 10. Result statement

Allowed:

```text
BMS-FU02d shows that the FU02c carrier roles form a connected seam-boundary
network at the edge/component level. The seven H,H consensus carriers are
separate as H,H-only components, but every one of them is adjacent to H,P
secondary structure. Nineteen of twenty-three H,P secondary carriers are
directly adjacent to H,H consensus carriers, and the full H,H + H,P carrier set
forms a single 30-edge / 25-node connected component.
```

Short version:

```text
FU02d shows that the seven H,H seam anchors are connected by an H,P boundary
network.
```

Not allowed:

```text
FU02d proves a global C60 face patch.
FU02d proves physical spacetime geometry.
FU02d recovers full C60 symmetry.
```

---

## 11. Recommended next block

The immediate next step should be a small repair/hardening block, not a new
large physics jump.

Recommended next:

```text
BMS-FU02d1 — Face Parser Repair and Face-Level Carrier Localization
```

Purpose:

```text
Fix face involvement parsing from the C60 edge table and rerun the FU02d
face-level readout.
```

Questions:

```text
1. Which faces carry H,H consensus edges?
2. Which faces carry H,P secondary edges?
3. Are mixed-role junctions concentrated around specific hexagons/pentagons?
4. Does the connected seam-boundary network correspond to a face patch, ring, or
   belt on the C60 cage?
```

After FU02d1, if face-level localization is repaired:

```text
BMS-FU02e — Carrier Role Null Localization Test
```

Purpose:

```text
Test whether the connected seam-boundary network is also produced by null
graphs or whether it is real-C60 localization-specific.
```

---

## 12. Internal summary

```text
FU02c:
  H-H sind Naht-Träger.
  H-P sind Grenz-Träger.

FU02d:
  H-H allein:
    7 isolierte Nahtanker.

  H-P allein:
    5 lokale Grenzkomponenten.

  H-H + H-P:
    1 zusammenhängendes 30-edge / 25-node Gewebe.

  7/7 H-H-Kanten berühren H-P.
  19/23 H-P-Kanten liegen direkt an H-H.
  14 mixed_role_junction nodes.

Kern:
  Die Nahtpunkte sind verteilt.
  Das Grenzgewebe verbindet sie.

Grenze:
  Face-Level ist in v0 nicht belastbar.
  Erst FU02d1 repariert die Face-Karte.
```

---

## 13. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02D_CARRIER_ROLE_GEOMETRY_PATCH_DISTRIBUTION_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02D_CARRIER_ROLE_GEOMETRY_PATCH_DISTRIBUTION_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02D_CARRIER_ROLE_GEOMETRY_PATCH_DISTRIBUTION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02d carrier role geometry result note"

git push
```
