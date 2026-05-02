# BMS-FU02e1 — Role-Balance Localization Specificity Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02E1_ROLE_BALANCE_LOCALIZATION_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02e1-v0

---

## 1. Purpose

BMS-FU02e1 follows BMS-FU02e.

FU02e showed:

```text
Connectivity is cheap.
Compact connected localization is the signal.
Role balance is the next sharpening.
```

FU02e1 evaluates the joint profile rather than isolated metrics.

Core question:

```text
Kann eine Attrappe gleichzeitig so kompakt sein
und dieselbe Rollenbalance behalten?
```

The tested profile includes:

```text
carrier_face_count
carrier_pentagon_face_count
mixed_seam_boundary_face_count
largest_mixed_face_component_count
carrier_face_component_count
largest_carrier_face_component_count
```

Near-real rule:

```text
|carrier_face_count - real| <= 1
|carrier_pentagon_face_count - real| <= 1
|mixed_seam_boundary_face_count - real| <= 1
carrier_face_component_count == 1
```

Strict near-real rule:

```text
carrier_face_count == real
carrier_pentagon_face_count == real
mixed_seam_boundary_face_count == real
carrier_face_component_count == 1
```

---

## 2. Main result

FU02e1 gives a strong profile-level specificity result for the tested null families.

Across all four null families:

```text
near_real_profile_count = 0 / 2000
strict_near_real_profile_count = 0 / 2000
```

By family:

```text
component_size_preserving_hp_shuffle:
  near_real = 0 / 500
  strict_near_real = 0 / 500

degree_spread_role_shuffle:
  near_real = 0 / 500
  strict_near_real = 0 / 500

edge_type_preserving_role_shuffle:
  near_real = 0 / 500
  strict_near_real = 0 / 500

hh_anchor_neighborhood_decoy:
  near_real = 0 / 500
  strict_near_real = 0 / 500
```

Interpretation:

```text
No tested null replicate simultaneously matched the real compactness and the
selected role-balance constraints.
```

Internal short version:

```text
Die Attrappen können einzelne Tricks.
Aber keine malt denselben kleinen Fleck mit derselben Rollenfarbe.
```

---

## 3. Family-level summaries

### 3.1 component_size_preserving_hp_shuffle

```text
near_real = 0 / 500
strict_near_real = 0 / 500
D_abs min / mean / median / max = 8 / 16.314 / 16 / 25
role_balance_deviation min / mean / median / max = 4 / 9.94 / 10 / 17
label = near_real_profiles_absent
```

Metric profile:

```text
carrier_face_count:
  real = 17
  null_mean = 23.374
  null_min = 20
  null_max = 25

carrier_pentagon_face_count:
  real = 5
  null_mean = 5.0
  null_min = 5
  null_max = 5

mixed_seam_boundary_face_count:
  real = 8
  null_mean = 9.096
  null_min = 4
  null_max = 13

largest_mixed_face_component_count:
  real = 8
  null_mean = 7.246
  null_min = 2
  null_max = 13

carrier_face_component_count:
  real = 1
  null_mean = 1.0

largest_carrier_face_component_count:
  real = 17
  null_mean = 23.374
```

Interpretation:

```text
This null reproduces the pentagon count exactly, but still over-spreads the
carrier-face region. It does not reproduce the joint compact role-balance
profile.
```

Internal:

```text
Diese Attrappe trifft die Pentagone,
aber sie malt den Fleck zu groß.
```

---

### 3.2 degree_spread_role_shuffle

```text
near_real = 0 / 500
strict_near_real = 0 / 500
D_abs min / mean / median / max = 19 / 34.24 / 34 / 43
role_balance_deviation min / mean / median / max = 13 / 22.14 / 22 / 29
label = near_real_profiles_absent
```

Metric profile:

```text
carrier_face_count:
  real = 17
  null_mean = 29.1
  null_min = 23
  null_max = 32

carrier_pentagon_face_count:
  real = 5
  null_mean = 11.068
  null_min = 8
  null_max = 12
```

Interpretation:

```text
Degree-spread role shuffle strongly over-spreads the carrier region and
over-involves pentagons. It does not approach the real compact role-balance
profile.
```

Because C60 is degree-3 regular, this family is expected to behave similarly to
edge-type role shuffle.

---

### 3.3 edge_type_preserving_role_shuffle

```text
near_real = 0 / 500
strict_near_real = 0 / 500
D_abs min / mean / median / max = 19 / 34.044 / 34 / 45
role_balance_deviation min / mean / median / max = 12 / 21.97 / 22 / 30
label = near_real_profiles_absent
```

Metric profile:

```text
carrier_face_count:
  real = 17
  null_mean = 29.074
  null_min = 24
  null_max = 32

carrier_pentagon_face_count:
  real = 5
  null_mean = 11.048
  null_min = 8
  null_max = 12
```

Interpretation:

```text
Simple edge-type preserving role placement does not explain the real profile.
It heavily over-spreads carrier faces and pentagon involvement.
```

Internal:

```text
Wenn man 7 H-H und 23 H-P nur irgendwo passend verteilt,
schmiert es fast über den ganzen Käfig.
```

---

### 3.4 hh_anchor_neighborhood_decoy

```text
near_real = 0 / 500
strict_near_real = 0 / 500
D_abs min / mean / median / max = 4 / 16.902 / 16 / 34
role_balance_deviation min / mean / median / max = 4 / 13.572 / 13 / 26
label = near_real_profiles_absent
```

Metric profile:

```text
carrier_face_count:
  real = 17
  null_mean = 20.408
  null_min = 16
  null_max = 25

carrier_pentagon_face_count:
  real = 5
  null_mean = 9.064
  null_min = 7
  null_max = 11

mixed_seam_boundary_face_count:
  real = 8
  null_mean = 11.252
  null_min = 9
  null_max = 14

largest_mixed_face_component_count:
  real = 8
  null_mean = 10.228
  null_min = 4
  null_max = 14

carrier_face_component_count:
  real = 1
  null_mean = 1.04
  null_min = 1
  null_max = 2

largest_carrier_face_component_count:
  real = 17
  null_mean = 20.194
  null_min = 9
  null_max = 25
```

Interpretation:

```text
The anchor-neighborhood decoy is the closest family in absolute profile distance.
It can approach compactness, but it systematically shifts role balance:
it overproduces pentagon involvement and mixed seam-boundary faces.
```

Important:

```text
This is the most informative null result. It shows that simply placing H,P near
H,H anchors is not sufficient to reproduce the full real profile.
```

Internal:

```text
Der stärkste Decoy kann den Fleck kleiner machen,
aber dann kippt ihm die Rollenfarbe weg.
```

---

## 4. Overall interpretation

FU02e1 strengthens the FU02e result.

FU02e result:

```text
The real network is unusually compact relative to tested nulls.
```

FU02e1 result:

```text
No tested null replicate reproduced the near-real compact role-balance profile.
```

Best project statement:

```text
BMS-FU02e1 supports a construction-qualified role-balance localization
specificity indication. Across 2000 tested null replicates, no null assignment
simultaneously reproduced the real compact carrier-face count, pentagon
involvement, mixed seam-boundary face count and connectedness constraints. The
strongest anchor-neighborhood decoy came closest in compactness but overproduced
mixed faces and pentagon involvement.
```

Short version:

```text
FU02e:
  Attrappen malen meistens zu groß.

FU02e1:
  Und wenn sie kleiner malen,
  stimmt die Rollenfarbe nicht.
```

---

## 5. Bridge interpretation

FU02e1 supports a stronger methodological reading of the C60 calibration result.

Previous chain:

```text
FU02c:
  H,H / 6:6 and H,P / 5:6 separate into seam and boundary carrier roles.

FU02d:
  The roles form one connected edge/node seam-boundary network.

FU02d1:
  The network lies on one connected 17-face C60 region.

FU02e:
  Nulls can reproduce connectedness but usually over-spread across more faces.

FU02e1:
  Nulls do not reproduce the joint compact role-balance profile.
```

Bridge-facing cautious statement:

```text
BMS-FU02e1 evaluates the FU02d1 carrier-face localization as a joint
compactness and role-balance profile. In the tested fixed-graph role-assignment
null families, no replicate matched the near-real profile constraints. This
supports the methodological view that the C60 carrier signal is not only
connected and compact, but also constrained by a specific balance of seam,
boundary and face-incidence roles.
```

Internal formulation:

```text
Nicht nur: Der Fleck ist klein.
Sondern: Der kleine Fleck hat die richtige Rollenfarbe.
```

---

## 6. What FU02e1 does NOT prove

FU02e1 does not prove:

```text
physical spacetime geometry
a physical metric
global C60 symmetry recovery
molecular recognition
quantum chemistry
that carrier edges or faces are physical spacetime atoms
```

FU02e1 also does not yet prove:

```text
true fullerene-family specificity
a physical cage belt
a unique symmetry orbit
```

because:

```text
FU02e1 uses FU02e fixed-graph role-assignment nulls, not a full fullerene-family
structural null ensemble.
```

Important scope phrase:

```text
construction-qualified role-balance localization specificity indication
```

---

## 7. Allowed result statement

Allowed:

```text
BMS-FU02e1 shows that near-real compact role-balance profiles are absent in the
tested FU02e null families. Across 2000 fixed-C60 role-assignment null
replicates, no replicate simultaneously matched the real carrier-face
compactness, pentagon involvement, mixed seam-boundary face count and
connectedness constraints. The strongest anchor-neighborhood decoy approached
compactness more closely than simpler nulls but overproduced mixed faces and
pentagon involvement.
```

Short allowed version:

```text
Near-real role-balance profiles were absent in the tested null families.
```

Internal:

```text
Keine Attrappe trifft den kleinen Fleck mit derselben Farbmischung.
```

Not allowed:

```text
The result proves physical spacetime.
The result proves global C60 symmetry.
The empirical null fractions are formal physical p-values.
The carrier region is impossible under all conceivable nulls.
```

---

## 8. Recommended next block

Recommended next:

```text
BMS-FU02f — Carrier Role Visualization and Symmetry-Orbit Inspection
```

Purpose:

```text
Export a visual C60 cage map and inspect whether the compact role-balanced
17-face region corresponds to a recognizable patch, belt, cap, or orbit-like
subset.
```

Why now?

```text
FU02e1 has established a strong fixed-graph null result for the joint profile.
The next useful step is to inspect the spatial/symmetry character of the
localized region without overclaiming it.
```

Alternative later block:

```text
BMS-FU02g — Fullerene-Family Structural Null Ensemble
```

Purpose:

```text
Test whether comparable compact role-balanced carrier regions appear in other
fullerene-like or fullerene-preserving structural ensembles.
```

Suggested order:

```text
1. FU02f visualization / orbit inspection.
2. FU02g stronger structural null ensemble.
```

---

## 9. Internal summary

```text
FU02e1:

  near_real:
    0 / 2000

  strict_near_real:
    0 / 2000

  component-size H,P null:
    trifft Pentagone,
    aber ist zu groß.

  edge-type / degree nulls:
    viel zu groß,
    zu viele Pentagone.

  anchor-neighborhood decoy:
    kommt am nächsten,
    aber produziert zu viele Mixed-Faces und Pentagone.

Kern:
  Nicht nur klein.
  Klein mit richtiger Rollenfarbe.

Grenze:
  Fixed-C60 role-assignment nulls.
  Noch kein fullerene-family Ensemble.
  Noch keine physikalische Raumzeit.
```

---

## 10. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02E1_ROLE_BALANCE_LOCALIZATION_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02E1_ROLE_BALANCE_LOCALIZATION_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02E1_ROLE_BALANCE_LOCALIZATION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02e1 role-balance localization result note"

git push
```
