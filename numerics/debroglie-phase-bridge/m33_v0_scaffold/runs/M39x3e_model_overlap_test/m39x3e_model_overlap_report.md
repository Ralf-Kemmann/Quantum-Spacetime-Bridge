# M39x3e_model_overlap_test

## 1. Zweck
Model-overlap test to determine whether the finite square well (FSW) and anharmonic oscillator (AO) share a common Type-B structure in a joint feature space, or whether they represent distinct pathways through the broader Type-B region.


## 2. Globales Urteil
```json
{
  "run_id": "M39x3e_model_overlap_test",
  "source_run_id": "M39x3d_transition_mapping",
  "n_pair_feature_rows": 60,
  "n_pair_rows": 12,
  "n_group_rows": 3,
  "global_overlap_status": "no_meaningful_model_overlap",
  "transfer_mean_overlap_distance": 0.9056627684703695,
  "prejump_mean_overlap_distance": 1.2885939444463879,
  "jump_mean_overlap_distance": 1.742406439029231,
  "all_pair_sets_have_only_weak_or_worse_overlap": false
}
```

## 3. Gruppenübersicht
| pair_set_id             |   n_pairs |   mean_overlap_distance |   min_overlap_distance |   max_overlap_distance |   strong_overlap_count |   partial_overlap_count |   weak_overlap_count |   no_overlap_count | group_overlap_status                           | group_overlap_note                                     |
|:------------------------|----------:|------------------------:|-----------------------:|-----------------------:|-----------------------:|------------------------:|---------------------:|-------------------:|:-----------------------------------------------|:-------------------------------------------------------|
| FSW_CORE_VS_AO_TRANSFER |         6 |                0.905663 |               0.760254 |                1.12689 |                      0 |                       0 |                    3 |                  3 | no_meaningful_model_overlap                    | No meaningful overlap in the tested pair set.          |
| FSW_CORE_VS_AO_PREJUMP  |         4 |                1.28859  |               1.11556  |                1.46162 |                      0 |                       0 |                    0 |                  4 | no_meaningful_model_overlap                    | No meaningful overlap in the tested pair set.          |
| FSW_CORE_VS_AO_JUMP     |         2 |                1.74241  |               1.71288  |                1.77194 |                      0 |                       0 |                    0 |                  2 | ao_qualitative_extension_beyond_shared_overlap | AO jump core extends beyond the shared FSW/AO overlap. |

## 4. Paarübersicht
| pair_set_id             | fsw_regime_id   | ao_regime_id   | dominant_marker_fsw   | dominant_marker_ao   | dominant_marker_match_flag   | irregularity_level_fsw   | irregularity_level_ao   | irregularity_level_match_flag   |   mean_normalized_difference |   weighted_overlap_distance_score | overlap_status        | overlap_note                                       |
|:------------------------|:----------------|:---------------|:----------------------|:---------------------|:-----------------------------|:-------------------------|:------------------------|:--------------------------------|-----------------------------:|----------------------------------:|:----------------------|:---------------------------------------------------|
| FSW_CORE_VS_AO_TRANSFER | FSW_D05         | AO_A04         | delta_p               | delta_p              | True                         | low_to_moderate          | low                     | False                           |                     0.21439  |                          1.10823  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_TRANSFER | FSW_D05         | AO_A05         | delta_p               | delta_p              | True                         | low_to_moderate          | low                     | False                           |                     0.147984 |                          0.784693 | weak_overlap          | Weak overlap only.                                 |
| FSW_CORE_VS_AO_TRANSFER | FSW_D05         | AO_A06         | delta_p               | delta_p              | True                         | low_to_moderate          | low                     | False                           |                     0.13728  |                          0.760254 | weak_overlap          | Weak overlap only.                                 |
| FSW_CORE_VS_AO_TRANSFER | FSW_D06         | AO_A04         | delta_p               | delta_p              | True                         | low_to_moderate          | low                     | False                           |                     0.220069 |                          1.12689  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_TRANSFER | FSW_D06         | AO_A05         | delta_p               | delta_p              | True                         | low_to_moderate          | low                     | False                           |                     0.149626 |                          0.778498 | weak_overlap          | Weak overlap only.                                 |
| FSW_CORE_VS_AO_TRANSFER | FSW_D06         | AO_A06         | delta_p               | delta_p              | True                         | low_to_moderate          | low                     | False                           |                     0.163194 |                          0.875418 | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_PREJUMP  | FSW_D05         | AO_A07         | delta_p               | delta_p              | True                         | low_to_moderate          | low_to_moderate         | True                            |                     0.216958 |                          1.11556  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_PREJUMP  | FSW_D05         | AO_A08         | delta_p               | delta_p              | True                         | low_to_moderate          | low_to_moderate         | True                            |                     0.261705 |                          1.38371  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_PREJUMP  | FSW_D06         | AO_A07         | delta_p               | delta_p              | True                         | low_to_moderate          | low_to_moderate         | True                            |                     0.235423 |                          1.19348  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_PREJUMP  | FSW_D06         | AO_A08         | delta_p               | delta_p              | True                         | low_to_moderate          | low_to_moderate         | True                            |                     0.28017  |                          1.46162  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_JUMP     | FSW_D05         | AO_A09         | delta_p               | delta_p              | True                         | low_to_moderate          | low_to_moderate         | True                            |                     0.320115 |                          1.71288  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
| FSW_CORE_VS_AO_JUMP     | FSW_D06         | AO_A09         | delta_p               | delta_p              | True                         | low_to_moderate          | low_to_moderate         | True                            |                     0.333865 |                          1.77194  | no_meaningful_overlap | No meaningful overlap in the shared feature space. |
