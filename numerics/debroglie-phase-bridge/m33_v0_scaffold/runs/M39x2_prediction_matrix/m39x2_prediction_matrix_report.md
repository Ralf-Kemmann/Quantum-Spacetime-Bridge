# M39x2_prediction_matrix

## 1. Ziel und Methode
Prediction-matrix run over predefined spectral types and control cases.

## 2. Family-wise Vorhersage-Passung
| family_id                | family_label                            | spectral_type               | model_class                      | status      | enabled   | variant_id        | dominant_marker   | absolute_best_marker   | relative_rank_top3               |   dominance_margin |   bootstrap_win_fraction | prediction_match_status   | prediction_match_note                                      |   prediction_hard_pass_flag |   prediction_soft_pass_flag |   prediction_fail_flag | expected_relative_winner   | expected_allowed_winners                   | expected_delta_p2_role     | expected_irregularity_level   | expected_direction_blindness_relevant   |   observed_spacing_cv |   observed_spacing_ratio_mean |   observed_direction_blindness_flag | extra   |
|:-------------------------|:----------------------------------------|:----------------------------|:---------------------------------|:------------|:----------|:------------------|:------------------|:-----------------------|:---------------------------------|-------------------:|-------------------------:|:--------------------------|:-----------------------------------------------------------|----------------------------:|----------------------------:|-----------------------:|:---------------------------|:-------------------------------------------|:---------------------------|:------------------------------|:----------------------------------------|----------------------:|------------------------------:|------------------------------------:|:--------|
| ER1_RING                 | external_control_ring                   | type_A_ladder               | ring_schrodinger_quadratic       | implemented | True      | RING_SIGNED       | delta_p           | delta_p                | delta_p,abs_delta_p,abs_delta_p2 |         0          |                    0.997 | supported                 | Core prediction matched.                                   |                           1 |                           0 |                      0 | delta_p                    | delta_p                                    | not_necessarily_dominant   | low_to_moderate               | True                                    |              0.333333 |                      0.75     |                                   1 | {}      |
| ER1_RING                 | external_control_ring                   | type_A_ladder               | ring_schrodinger_quadratic       | implemented | True      | RING_ABS          | delta_p           | delta_p                | delta_p,abs_delta_p,delta_p2     |         0          |                    0.789 | partially_supported       | Allowed winner matched, but not all side expectations fit. |                           0 |                           1 |                      0 | delta_p                    | delta_p                                    | not_necessarily_dominant   | low_to_moderate               | True                                    |              1.22474  |                      0        |                                   0 | {}      |
| ER1_RING                 | external_control_ring                   | type_A_ladder               | ring_schrodinger_quadratic       | implemented | True      | RING_DEGEN_SAFE   | delta_p           | delta_p                | delta_p,abs_delta_p,delta_p2     |         0          |                    0.779 | partially_supported       | Allowed winner matched, but not all side expectations fit. |                           0 |                           1 |                      0 | delta_p                    | delta_p                                    | not_necessarily_dominant   | low_to_moderate               | True                                    |              0.333333 |                      0.75     |                                   0 | {}      |
| TB1_QUADRATIC_NONTRIVIAL | type_B_quadratic_nontrivial_placeholder | type_B_quadratic_nontrivial | quadratic_nontrivial_placeholder | placeholder | False     | N/A               | nan               | nan                    |                                  |       nan          |                  nan     | open                      | Placeholder / missing control case.                        |                           0 |                           0 |                      0 | open                       | delta_p,delta_p2                           | open_test_case             | moderate                      | False                                   |            nan        |                    nan        |                                 nan | {}      |
| ER2_CAVITY               | external_main_test_cavity               | type_C_multiindex_structure | cavity_helmholtz_linear_energy   | implemented | True      | CAVITY_STANDARD   | abs_delta_k       | abs_delta_k            | abs_delta_k,abs_delta_k2,delta_k |         0.00130678 |                    0.511 | partially_supported       | Allowed winner matched, but not all side expectations fit. |                           0 |                           1 |                      0 | delta_k2                   | delta_k2,abs_delta_k2,delta_k,abs_delta_k  | structure_support_expected | moderate                      | False                                   |              0.235507 |                      0.792449 |                                   0 | {}      |
| ER3_MEMBRANE             | external_hard_bias_test_membrane        | type_C_multiindex_structure | membrane_helmholtz_bessel        | implemented | True      | MEMBRANE_STANDARD | delta_k           | delta_k                | delta_k,abs_delta_k,delta_k2     |         0          |                    0.942 | partially_supported       | Allowed winner matched, but not all side expectations fit. |                           0 |                           1 |                      0 | delta_k2                   | delta_k2,abs_delta_k2,delta_lambda,delta_k | structure_support_expected | moderate_to_high              | False                                   |              0.513281 |                      0.502753 |                                   0 | {}      |
| TD1_REGULAR_NONRING      | type_D_regular_nonring_placeholder      | type_D_regular_nonring      | regular_nonring_placeholder      | placeholder | False     | N/A               | nan               | nan                    |                                  |       nan          |                  nan     | open                      | Placeholder / missing control case.                        |                           0 |                           0 |                      0 | open                       | delta_p,delta_p2                           | critical_control_case      | low_to_moderate               | False                                   |            nan        |                    nan        |                                 nan | {}      |

## 3. Zusammenfassung nach Spektraltyp
| spectral_type               |   n_families |   n_supported |   n_partially_supported |   n_open |   n_stressed |   n_failed |
|:----------------------------|-------------:|--------------:|------------------------:|---------:|-------------:|-----------:|
| type_A_ladder               |            3 |             1 |                       2 |        0 |            0 |          0 |
| type_B_quadratic_nontrivial |            1 |             0 |                       0 |        1 |            0 |          0 |
| type_C_multiindex_structure |            2 |             0 |                       2 |        0 |            0 |          0 |
| type_D_regular_nonring      |            1 |             0 |                       0 |        1 |            0 |          0 |

## 4. Fehlende Kontrollfälle
| family_id                | family_label                            | spectral_type               | status      | implementation_note                                                                                                              |
|:-------------------------|:----------------------------------------|:----------------------------|:------------|:---------------------------------------------------------------------------------------------------------------------------------|
| TB1_QUADRATIC_NONTRIVIAL | type_B_quadratic_nontrivial_placeholder | type_B_quadratic_nontrivial | placeholder | Must be defined before the prediction matrix can be considered fully hardened.                                                   |
| TD1_REGULAR_NONRING      | type_D_regular_nonring_placeholder      | type_D_regular_nonring      | placeholder | Must be defined to test whether the current ring explanation is genuinely about ladder regularity or still partly ring-specific. |

## 5. Globaler Status
```json
{
  "run_id": "M39x2_prediction_matrix",
  "n_families_total": 5,
  "n_families_implemented": 3,
  "n_prediction_supported": 1,
  "n_prediction_partially_supported": 4,
  "n_prediction_open": 2,
  "n_prediction_stressed": 0,
  "n_prediction_failed": 0,
  "missing_type_B_flag": 1,
  "missing_type_D_flag": 1,
  "ring_prediction_stressed": 0,
  "type_C_prediction_stressed": 0,
  "global_prediction_status": "prediction_matrix_partially_supported"
}
```
