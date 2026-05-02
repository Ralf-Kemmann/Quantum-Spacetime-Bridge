# BMS-FU02e1 — Role-Balance Localization Specificity Extension Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02E1_ROLE_BALANCE_LOCALIZATION_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02e1 follows BMS-FU02e.

FU02e showed:

```text
Connectivity is cheap.
Compact connected localization is the signal.
Role balance is the next sharpening.
```

Specifically:

```text
real carrier_face_count = 17
edge_type / degree nulls spread to about 29 faces
component-size H,P null spreads to about 23 faces
hh_anchor_neighborhood_decoy comes closer at about 20 faces
```

But the strongest anchor-neighborhood decoy tends to overproduce:

```text
mixed_seam_boundary_face_count
carrier_pentagon_face_count
```

FU02e1 asks:

```text
Kann eine Attrappe gleichzeitig so kompakt sein
und dieselbe Rollenbalance behalten?
```

Scientific formulation:

```text
Does the real carrier-face localization profile remain distinctive when
compactness and role-balance metrics are evaluated jointly rather than as
single metrics?
```

---

## 2. Core idea

FU02e used single metrics.

FU02e1 builds multi-metric profile distances between the real FU02d1 face
localization and every FU02e null replicate.

Real profile candidate:

```text
carrier_face_count = 17
carrier_pentagon_face_count = 5
mixed_seam_boundary_face_count = 8
largest_mixed_face_component_count = 8
carrier_face_component_count = 1
largest_carrier_face_component_count = 17
```

The key is not only:

```text
small carrier_face_count
```

but:

```text
small carrier_face_count
without overproducing pentagons or mixed seam-boundary faces.
```

Internal image:

```text
FU02e:
  Attrappen malen oft zu groß.

FU02e1:
  Malen sie auch mit der falschen Farbmischung?
```

---

## 3. Input artifacts

Primary FU02e outputs:

```text
runs/BMS-FU02e/carrier_role_null_localization_open/bms_fu02e_null_localization_metrics.csv
runs/BMS-FU02e/carrier_role_null_localization_open/bms_fu02e_real_vs_null_summary.csv
runs/BMS-FU02e/carrier_role_null_localization_open/bms_fu02e_real_face_metrics.json
runs/BMS-FU02e/carrier_role_null_localization_open/bms_fu02e_run_manifest.json
runs/BMS-FU02e/carrier_role_null_localization_open/bms_fu02e_warnings.json
```

Optional context:

```text
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_localization.csv
```

---

## 4. Profile metrics

FU02e1 uses these profile dimensions:

```text
carrier_face_count
carrier_pentagon_face_count
mixed_seam_boundary_face_count
largest_mixed_face_component_count
carrier_face_component_count
largest_carrier_face_component_count
```

Optional secondary dimensions:

```text
hp_boundary_face_count
carrier_adjacent_face_count
hh_face_count
hp_face_count
```

---

## 5. Distance / score definitions

### 5.1 Raw absolute profile distance

```text
D_abs =
  sum_i |x_i - real_i|
```

### 5.2 Null-normalized profile distance

For each metric and null family:

```text
z_i = (x_i - real_i) / std_null_i
```

with guard:

```text
if std_null_i == 0:
  use absolute difference with penalty scale 1
```

Then:

```text
D_z = sqrt(sum_i z_i^2)
```

### 5.3 Role-balance compactness score

A directional score emphasizing deviation from the desired real balance:

```text
role_balance_deviation =
  |carrier_face_count - 17|
+ |carrier_pentagon_face_count - 5|
+ |mixed_seam_boundary_face_count - 8|
+ |largest_mixed_face_component_count - 8|
+ 4 * I(carrier_face_component_count != 1)
```

The multiplier 4 is not physical; it is a transparent diagnostic penalty.

### 5.4 Near-real profile flags

A null replicate is near-real if:

```text
|carrier_face_count - 17| <= 1
|carrier_pentagon_face_count - 5| <= 1
|mixed_seam_boundary_face_count - 8| <= 1
carrier_face_component_count == 1
```

Strict near-real:

```text
carrier_face_count == 17
carrier_pentagon_face_count == 5
mixed_seam_boundary_face_count == 8
carrier_face_component_count == 1
```

---

## 6. Outputs

Output directory:

```text
runs/BMS-FU02e1/role_balance_localization_specificity_open/
```

Expected files:

```text
bms_fu02e1_profile_distance_by_replicate.csv
bms_fu02e1_profile_summary_by_family.csv
bms_fu02e1_near_real_replicates.csv
bms_fu02e1_real_profile.json
bms_fu02e1_run_manifest.json
bms_fu02e1_warnings.json
bms_fu02e1_config_resolved.yaml
```

---

## 7. Interpretation labels

Per null family:

```text
near_real_profiles_common
near_real_profiles_present_but_rare
near_real_profiles_absent
profile_distance_overlaps_real_neighborhood
profile_distance_separates_real_from_null_family
inconclusive_due_to_zero_variance_or_scope
```

Important:

```text
This is still a diagnostic specificity test, not a formal physical probability.
```

---

## 8. Claim boundary

Allowed:

```text
BMS-FU02e1 evaluates whether null replicates reproduce the joint compactness
and role-balance profile of the real FU02d1 carrier-face localization.
```

Allowed after strong result:

```text
Near-real compact role-balance profiles are rare or absent in tested null
families.
```

Not allowed:

```text
A physical p-value has been computed.
The carrier region is a physical spacetime patch.
Global C60 symmetry has been recovered.
```

---

## 9. Bridge relevance

FU02e1 tests whether geometry-readable carrier information is not only compact
but role-balanced.

Bridge-facing cautious statement:

```text
If near-real role-balance localization profiles are rare in role-assignment
nulls, this supports the methodological view that the C60 carrier signal is not
only localized, but organized by a constrained combination of seam, boundary
and face-incidence roles.
```

Internal formulation:

```text
Nicht nur: Der Fleck ist klein.
Sondern: Der kleine Fleck hat die richtige Rollenfarbe.
```

---

## 10. Recommended next after FU02e1

If near-real profiles are rare:

```text
BMS-FU02f — Carrier Role Visualization and Symmetry-Orbit Inspection
```

Purpose:

```text
Export a visual cage map and inspect whether the compact role-balanced
17-face region corresponds to a recognizable patch, belt, cap, or orbit-like
subset.
```

If near-real profiles are common:

```text
BMS-FU02e2 — Stronger Fullerene-Preserving Null Ensemble
```

Purpose:

```text
Separate fixed-graph role-assignment effects from fullerene-family structural
specificity.
```
