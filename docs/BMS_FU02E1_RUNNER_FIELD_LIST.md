# BMS-FU02e1 — Runner Field List

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02E1_RUNNER_FIELD_LIST.md`  
Status: Companion field list for BMS-FU02e1 role-balance localization specificity extension

---

## 1. Purpose

BMS-FU02e1 compares the real FU02d1/FU02e carrier-face localization profile against FU02e null replicates using joint compactness and role-balance metrics.

Core question:

```text
Kann eine Attrappe gleichzeitig so kompakt sein
und dieselbe Rollenbalance behalten?
```

---

## 2. Config fields

| field name | type | description |
|---|---:|---|
| `run.run_id` | string | Stable run identifier. |
| `run.output_dir` | string | Output directory. |
| `inputs.fu02e_output_dir` | string | FU02e output directory. |
| `inputs.fu02d1_output_dir` | string | FU02d1 output directory, included for context. |
| `profile.primary_metrics` | list[string] | Primary metrics used for profile distances. |
| `profile.secondary_metrics` | list[string] | Secondary metrics copied into output for context. |
| `near_real_thresholds.carrier_face_count_abs` | integer | Allowed absolute carrier-face-count deviation for near-real profile. |
| `near_real_thresholds.carrier_pentagon_face_count_abs` | integer | Allowed absolute pentagon-face-count deviation for near-real profile. |
| `near_real_thresholds.mixed_seam_boundary_face_count_abs` | integer | Allowed mixed-face-count deviation for near-real profile. |
| `near_real_thresholds.require_carrier_face_component_count` | integer | Required connected component count. |
| `scoring.component_mismatch_penalty` | float | Penalty in role-balance deviation if component count mismatches. |
| `scoring.zero_std_scale` | float | Fallback z-distance scale for zero-variance metrics. |

---

## 3. Profile distance by replicate

Output:

```text
bms_fu02e1_profile_distance_by_replicate.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family id. |
| `replicate_index` | integer | Replicate index from FU02e. |
| `D_abs_primary` | float | Sum of absolute differences across primary metrics. |
| `D_z_primary` | float | Null-family-standardized Euclidean distance across primary metrics. |
| `role_balance_deviation` | float | Directionally transparent compactness/role-balance deviation. |
| `near_real_profile` | integer | 1 if replicate passes near-real thresholds. |
| `strict_near_real_profile` | integer | 1 if replicate exactly matches selected real profile metrics. |
| `<metric>` | float/integer | Null replicate metric value. |
| `<metric>_real` | float/integer | Real metric value. |
| `<metric>_abs_diff` | float | Absolute difference to real for primary metrics. |
| `<metric>_z_diff` | float | Null-family-standardized signed difference for primary metrics. |

Primary metrics:

```text
carrier_face_count
carrier_pentagon_face_count
mixed_seam_boundary_face_count
largest_mixed_face_component_count
carrier_face_component_count
largest_carrier_face_component_count
```

Secondary metrics:

```text
hp_boundary_face_count
carrier_adjacent_face_count
hh_face_count
hp_face_count
```

---

## 4. Profile summary by family

Output:

```text
bms_fu02e1_profile_summary_by_family.csv
```

| field name | type | description |
|---|---:|---|
| `null_family` | string | Null family id. |
| `replicate_count` | integer | Number of null replicates. |
| `near_real_count` | integer | Number of near-real replicates. |
| `near_real_fraction` | float | Fraction of near-real replicates. |
| `strict_near_real_count` | integer | Number of strict near-real replicates. |
| `strict_near_real_fraction` | float | Fraction of strict near-real replicates. |
| `D_abs_min` | float | Minimum absolute profile distance. |
| `D_abs_mean` | float | Mean absolute profile distance. |
| `D_abs_median` | float | Median absolute profile distance. |
| `D_abs_max` | float | Maximum absolute profile distance. |
| `D_z_min` | float | Minimum z-profile distance. |
| `D_z_mean` | float | Mean z-profile distance. |
| `D_z_median` | float | Median z-profile distance. |
| `D_z_max` | float | Maximum z-profile distance. |
| `role_balance_deviation_min` | float | Minimum role-balance deviation. |
| `role_balance_deviation_mean` | float | Mean role-balance deviation. |
| `role_balance_deviation_median` | float | Median role-balance deviation. |
| `role_balance_deviation_max` | float | Maximum role-balance deviation. |
| `interpretation_label` | string | Family-level interpretation label. |
| `<metric>_real` | float/integer | Real primary metric value. |
| `<metric>_null_mean` | float | Null mean for primary metric. |
| `<metric>_null_min` | float | Null minimum for primary metric. |
| `<metric>_null_max` | float | Null maximum for primary metric. |

Interpretation labels:

```text
near_real_profiles_common
near_real_profiles_present_but_rare
near_real_profiles_absent
profile_distance_overlaps_real_neighborhood
```

---

## 5. Near-real replicates

Output:

```text
bms_fu02e1_near_real_replicates.csv
```

Same fields as the replicate distance table, restricted to near-real or strict near-real profiles.

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

## 6. Real profile

Output:

```text
bms_fu02e1_real_profile.json
```

| field name | type | description |
|---|---:|---|
| `primary_metrics` | object | Real values for primary metrics. |
| `secondary_metrics` | object | Real values for secondary metrics. |
| `near_real_thresholds` | object | Near-real thresholds used. |
| `component_mismatch_penalty` | float | Penalty used in deviation score. |
| `interpretation_note` | string | Scope note. |

---

## 7. Interpretation boundary

Allowed:

```text
FU02e1 evaluates joint compactness and role-balance profile specificity.
```

Not allowed:

```text
FU02e1 computes formal physical p-values or proves physical spacetime.
```
