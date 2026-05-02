# BMS-FU02e — Carrier Role Null Localization Test Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02E_CARRIER_ROLE_NULL_LOCALIZATION_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02e-v0

---

## 1. Purpose

BMS-FU02e follows BMS-FU02d1.

FU02d1 found that the FU02d seam-boundary carrier network maps onto one connected C60 face region:

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

Specifically:

```text
Do role-assignment null families reproduce the same connected and compact
face-localization pattern as the real FU02d1 carrier network?
```

---

## 2. Null families

FU02e-v0 used four role-assignment null families on the fixed validated C60 graph:

```text
edge_type_preserving_role_shuffle
degree_spread_role_shuffle
component_size_preserving_hp_shuffle
hh_anchor_neighborhood_decoy
```

Each family used:

```text
500 replicates
```

Total:

```text
2000 null replicates
```

Interpretation boundary:

```text
Empirical exceedance fractions are diagnostic comparisons, not formal physical
p-values.
```

---

## 3. Main result

FU02e gives a clear but nuanced result.

The real carrier-face region is not special merely because it is connected:

```text
carrier_face_component_count real = 1
null families mostly also produce 1 connected component
```

So:

```text
Connectivity alone is cheap.
```

The distinctive feature is compactness / limited spread:

```text
real carrier_face_count = 17
```

while nulls usually spread carrier roles over substantially more faces:

```text
edge_type_preserving_role_shuffle:
  mean carrier_face_count = 29.074
  min/median/max = 24 / 29 / 32

degree_spread_role_shuffle:
  mean carrier_face_count = 29.1
  min/median/max = 23 / 29 / 32

component_size_preserving_hp_shuffle:
  mean carrier_face_count = 23.374
  min/median/max = 20 / 24 / 25

hh_anchor_neighborhood_decoy:
  mean carrier_face_count = 20.408
  min/median/max = 16 / 20 / 25
```

Core interpretation:

```text
The real carrier network is much more face-compact than most null role
assignments. It occupies fewer faces while remaining connected.
```

Internal short version:

```text
Nulls können Verbundenheit billig nachbauen.
Aber sie malen meistens zu breit über den Käfig.
Das reale Netz bleibt kompakter.
```

---

## 4. Key metric: carrier_face_count

Real:

```text
carrier_face_count = 17
```

Null comparison:

```text
component_size_preserving_hp_shuffle:
  null_mean = 23.374
  null_min / median / max = 20 / 24 / 25
  empirical_ge_fraction = 1.0
  empirical_le_fraction = 0.0
  rank_position_of_real = 501
  label = real_low_relative_to_null

degree_spread_role_shuffle:
  null_mean = 29.1
  null_min / median / max = 23 / 29 / 32
  empirical_ge_fraction = 1.0
  empirical_le_fraction = 0.0
  rank_position_of_real = 501
  label = real_low_relative_to_null

edge_type_preserving_role_shuffle:
  null_mean = 29.074
  null_min / median / max = 24 / 29 / 32
  empirical_ge_fraction = 1.0
  empirical_le_fraction = 0.0
  rank_position_of_real = 501
  label = real_low_relative_to_null

hh_anchor_neighborhood_decoy:
  null_mean = 20.408
  null_min / median / max = 16 / 20 / 25
  empirical_ge_fraction = 0.998
  empirical_le_fraction = 0.046
  rank_position_of_real = 478
  label = real_low_relative_to_null
```

Interpretation:

```text
The real network occupies fewer carrier faces than essentially all nulls in
three families and fewer than most nulls even in the strongest anchor-neighborhood
decoy.
```

Important nuance:

```text
The hh_anchor_neighborhood_decoy can sometimes produce carrier_face_count <= 17,
with min = 16 and empirical_le_fraction = 0.046. Therefore, compactness is
strong but not impossible under the strongest decoy.
```

Allowed statement:

```text
The real 17-face localization is unusually compact relative to the tested nulls.
```

Not allowed:

```text
The real localization is impossible under all nulls.
```

---

## 5. Key metric: connectedness

Real:

```text
carrier_face_component_count = 1
largest_carrier_face_component_count = 17
```

Nulls:

```text
component_size_preserving_hp_shuffle:
  carrier_face_component_count mean = 1.0
  largest component mean = 23.374

degree_spread_role_shuffle:
  carrier_face_component_count mean = 1.0
  largest component mean = 29.1

edge_type_preserving_role_shuffle:
  carrier_face_component_count mean = 1.0
  largest component mean = 29.074

hh_anchor_neighborhood_decoy:
  carrier_face_component_count mean = 1.04
  largest component mean = 20.194
```

Interpretation:

```text
The fact that the real carrier faces form one connected component is not
specific by itself. On C60, these carrier counts tend to produce connected face
regions under the tested nulls.
```

The specific part is:

```text
connected but smaller / more compact
```

Internal wording:

```text
Ein zusammenhängender Fleck ist billig.
Ein kleiner zusammenhängender Fleck ist interessanter.
```

---

## 6. Pentagon involvement

Real:

```text
carrier_pentagon_face_count = 5
```

Null comparison:

```text
component_size_preserving_hp_shuffle:
  null_mean = 5.0
  min/median/max = 5 / 5 / 5
  label = null_reproduces_metric_behavior

degree_spread_role_shuffle:
  null_mean = 11.068
  min/median/max = 8 / 11 / 12
  label = real_low_relative_to_null

edge_type_preserving_role_shuffle:
  null_mean = 11.048
  min/median/max = 8 / 11 / 12
  label = real_low_relative_to_null

hh_anchor_neighborhood_decoy:
  null_mean = 9.064
  min/median/max = 7 / 9 / 11
  label = real_low_relative_to_null
```

Interpretation:

```text
The five-pentagon count is reproduced exactly by the component-size-preserving
H,P null, because that null construction effectively preserves the local H,P
component pattern strongly enough to fix pentagon involvement.
```

However:

```text
simpler edge-type and degree-spread nulls over-spread into many more pentagons.
```

So the five-pentagon result is not a standalone specificity marker, but it is
a useful diagnostic of what the H,P component-size null already encodes.

Allowed statement:

```text
Pentagon count is not independently specific against the component-size-
preserving H,P null, but it is lower than simpler role-shuffle nulls.
```

---

## 7. Mixed seam-boundary faces

Real:

```text
mixed_seam_boundary_face_count = 8
```

Null comparison:

```text
component_size_preserving_hp_shuffle:
  null_mean = 9.096
  min/median/max = 4 / 9 / 13
  label = null_reproduces_metric_behavior

degree_spread_role_shuffle:
  null_mean = 8.738
  min/median/max = 4 / 9 / 13
  label = null_reproduces_metric_behavior

edge_type_preserving_role_shuffle:
  null_mean = 8.638
  min/median/max = 4 / 9 / 13
  label = null_reproduces_metric_behavior

hh_anchor_neighborhood_decoy:
  null_mean = 11.252
  min/median/max = 9 / 11 / 14
  label = real_low_relative_to_null
```

Interpretation:

```text
The real mixed-face count of 8 is broadly reproducible by the simpler nulls and
is lower than the anchor-neighborhood decoy.
```

So:

```text
mixed_seam_boundary_face_count alone is not specific evidence.
```

Interesting nuance:

```text
The strongest decoy overproduces mixed seam-boundary faces because it explicitly
places H,P near H,H anchors.
```

Internal wording:

```text
Wenn die Attrappe bewusst H-P um H-H klebt, macht sie sogar zu viele Mixed-Faces.
```

---

## 8. Null-family level interpretation

### 8.1 edge_type_preserving_role_shuffle

This null preserves:

```text
7 H,H carriers among H,H edges
23 H,P carriers among H,P edges
```

Result:

```text
carrier_face_count:
  real = 17
  null mean = 29.074
  null min = 24

carrier_pentagon_face_count:
  real = 5
  null mean = 11.048
  null min = 8
```

Interpretation:

```text
Simple edge-class-preserving random role placement badly over-spreads carrier
faces. It does not reproduce the compact real localization.
```

### 8.2 degree_spread_role_shuffle

Because C60 is degree-3 regular, this behaves similarly to edge-type preserving shuffle.

Result:

```text
carrier_face_count:
  real = 17
  null mean = 29.1
  null min = 23
```

Interpretation:

```text
Degree spread does not explain the real compact localization in this 3-regular
C60 calibration graph.
```

### 8.3 component_size_preserving_hp_shuffle

This null preserves the H,P component-size multiset:

```text
5, 5, 5, 4, 4
```

Result:

```text
carrier_face_count:
  real = 17
  null mean = 23.374
  null min = 20

carrier_pentagon_face_count:
  real = 5
  null mean = 5.0
```

Interpretation:

```text
Preserving H,P component sizes explains the five-pentagon count but still
over-spreads the carrier face region. It does not reproduce the compact 17-face
localization.
```

### 8.4 hh_anchor_neighborhood_decoy

This is the strongest FU02e-v0 decoy because it preferentially places H,P near shuffled H,H anchors.

Result:

```text
carrier_face_count:
  real = 17
  null mean = 20.408
  null min = 16
  empirical_le_fraction = 0.046

mixed_seam_boundary_face_count:
  real = 8
  null mean = 11.252
  null min = 9

carrier_pentagon_face_count:
  real = 5
  null mean = 9.064
  null min = 7
```

Interpretation:

```text
The anchor-neighborhood decoy comes closest on carrier_face_count and can
occasionally match or beat real compactness. However, it tends to produce too
many mixed faces and too many pentagon carrier faces.
```

This is important:

```text
The strongest decoy partially reproduces compactness, but not the same role-
balance profile.
```

---

## 9. Overall interpretation

FU02e does not support a simplistic claim:

```text
The real face region is unique under all nulls.
```

Instead, it supports a more careful claim:

```text
The real carrier-face region is unusually compact compared with the tested null
families. Connectivity alone is reproduced by nulls and is not specific.
Pentagon count is reproduced by the component-size-preserving H,P null. The
strongest anchor-neighborhood decoy can sometimes approach real compactness but
typically overproduces mixed seam-boundary faces and pentagon involvement.
```

Best project wording:

```text
BMS-FU02e supports a construction-qualified localization specificity indication:
the real C60 carrier-role network occupies a connected but unusually compact
17-face region relative to the tested role-assignment nulls. The specificity is
not in connectedness alone, but in compact connected localization combined with
role-balance constraints.
```

Internal summary:

```text
Verbundenheit ist billig.
Kompaktheit ist der Befund.
Rollenbalance ist die nächste Schärfe.
```

---

## 10. Bridge interpretation

FU02e strengthens the Bridge-relevant role-structure claim, but only in a bounded way.

FU02d1 showed:

```text
the seam-boundary carrier network lies on one connected 17-face region.
```

FU02e shows:

```text
role-assignment nulls usually spread the same number of carrier roles over more
faces.
```

Bridge-facing cautious statement:

```text
BMS-FU02e tests the FU02d1 carrier-face localization against role-assignment
nulls on the fixed C60 graph. The real carrier-role network remains connected
while occupying fewer faces than most tested null assignments. Connectivity
itself is not specific, but compact connected localization is stronger than
expected under simple edge-class and component-size role shuffles. The strongest
anchor-neighborhood decoy partially approaches the real compactness but tends
to overproduce mixed faces and pentagon involvement.
```

Short internal statement:

```text
Die Attrappen können ein Netz malen.
Aber meistens malen sie zu groß.
```

---

## 11. What FU02e does NOT prove

FU02e does not prove:

```text
physical spacetime geometry
a physical metric
global C60 symmetry recovery
molecular recognition
quantum chemistry
that carrier edges or faces are physical spacetime atoms
```

FU02e also does not yet prove:

```text
true fullerene-family specificity
a physical cage belt
a unique symmetry orbit
```

because:

```text
FU02e-v0 uses role-assignment nulls on the fixed C60 graph, not a full
fullerene-preserving graph ensemble.
```

---

## 12. Result statement

Allowed:

```text
BMS-FU02e shows that the FU02d1 carrier-face region is not specific merely
because it is connected: most tested nulls also produce connected carrier-face
regions. However, the real network occupies only 17 faces, while edge-type and
degree-spread role shuffles typically occupy about 29 faces, and the
component-size-preserving H,P shuffle occupies about 23 faces. The strongest
anchor-neighborhood decoy comes closer but still averages about 20 faces and
overproduces mixed faces and pentagon involvement. Thus the supported claim is
construction-qualified compact localization, not uniqueness or global symmetry
recovery.
```

Short version:

```text
FU02e says: connectedness is cheap, compact connected localization is the
signal.
```

Internal version:

```text
Das reale Netz ist nicht besonders, weil es zusammenhängt.
Es ist besonders, weil es zusammenhängt, ohne über den ganzen Ball zu schmieren.
```

---

## 13. Recommended next block

Recommended next:

```text
BMS-FU02e1 — Role-Balance Localization Specificity Extension
```

Purpose:

```text
Compare combined multi-metric profiles rather than single metrics:
  carrier_face_count
  carrier_pentagon_face_count
  mixed_seam_boundary_face_count
  largest_mixed_face_component_count
  role-balance compactness score
```

Reason:

```text
The anchor-neighborhood decoy partially approaches real compactness but with
different role balance. FU02e1 should quantify that profile difference.
```

Candidate composite score:

```text
role_balance_localization_score =
  z_compact_faces
  + z_low_pentagon_spread
  + z_low_mixed_overproduction
  + z_connectedness_constraint
```

Alternative next block:

```text
BMS-FU02f — Carrier Role Visualization and Symmetry-Orbit Inspection
```

Purpose:

```text
Export a visual C60 cage map to inspect whether the compact 17-face region is a
recognizable patch, belt, cap, or orbit-like subset.
```

Suggested order:

```text
1. FU02e1 for quantitative role-balance specificity.
2. FU02f for visualization and symmetry-orbit inspection.
```

---

## 14. Internal summary

```text
FU02d1:
  Das Netz liegt auf 17 verbundenen Faces.

FU02e:
  Nulls bauen Verbundenheit billig nach.
  Aber sie schmieren über mehr Faces.

  edge_type / degree:
    real 17 vs null ~29 Faces

  component-size H,P:
    real 17 vs null ~23 Faces

  anchor-neighborhood decoy:
    real 17 vs null ~20 Faces
    kommt näher,
    aber macht zu viele Mixed-Faces und zu viele Pentagone.

Kern:
  Nicht connectedness.
  Sondern compact connected localization + Rollenbalance.

Grenze:
  Keine globale Symmetrie.
  Keine physikalische Raumzeit.
  Noch keine fullerene-family null ensemble.
```

---

## 15. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02E_CARRIER_ROLE_NULL_LOCALIZATION_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02E_CARRIER_ROLE_NULL_LOCALIZATION_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02E_CARRIER_ROLE_NULL_LOCALIZATION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02e null localization result note"

git push
```
