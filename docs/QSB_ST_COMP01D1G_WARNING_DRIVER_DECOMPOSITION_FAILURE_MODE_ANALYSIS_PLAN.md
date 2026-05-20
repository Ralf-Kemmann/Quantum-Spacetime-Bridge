# QSB-ST-COMP01-D1g Warning Driver Decomposition and Failure-Mode Analysis Plan

## 1. Purpose

COMP01-D1g is a planning block only.

D1g plans a Warning Driver Decomposition and Failure-Mode Analysis based on the D1f robustness sweep.

D1g does not create a scanner, does not create a config, does not create runs, and does not create results.

Goal:

Do not build a new score. Instead, decompose which warning families, decoy families, null families, profile weights, penalty settings, and kernel sizes drive the D1f instability.

D1g also plans a transparent decision table method for rule-based classification of typical failure-mode combinations. This is not a black box and not an ML classifier.

## 2. Current status anchor

Current chain:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented
- COMP01-D1d Manifold Degeneracy Audit implemented and result documented
- COMP01-D1e Collision-Aware Profile Runner implemented and result documented
- COMP01-D1f Robustness Sweep Runner implemented and result documented

Current commit anchor:

`022bcad Add QSB-ST COMP01D1f collision-aware profile robustness result note`

D1f result values:

```yaml
case_count: 9450
expected_case_count: 9450
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed_all: true
warning_count_total: 32961
profile_collision_count: 0
residual_collision_count: 0
delta_vector_collision_count: 0
ambiguity_warning_count: 975
control_profile_mimicry_warnings_count: 4901
residual_matched_profile_warnings_count: 851
adversarial_profile_warnings_count: 1694
profile_weight_sensitivity_warnings_count: 2709
penalty_weight_sensitivity_warnings_count: 5859
kernel_size_sensitivity_warnings_count: 2214
null_family_overlap_warnings_count: 4901
decoy_success_warnings_count: 3956
control_overlap_warnings_count: 4901
mean_decoy_success_rate: 0.4186243386243386
mean_control_overlap_rate: 0.5186243386243387
```

## 3. Motivation from D1f

D1f did not confirm robust D1e warning reduction.

D1f showed that warning counts return strongly under broader synthetic stress.

However, D1f also showed that profile/residual/delta-vector collision counts are not the dominant failure mode in the robustness sweep.

Therefore, the main D1f signal is not simple metric collision but warning-driver instability:

- control overlap
- null-family overlap
- decoy success
- profile-weight sensitivity
- penalty-weight sensitivity
- kernel-size sensitivity

D1g should identify which families and settings drive these warnings before any new metric or claim step is considered.

## 4. Central question

Core question:

Welche Decoy-Familien, Nullfamilien, Profilgewichte, Penalty-Gewichte und Kernelgroessen treiben die D1f-Warnungen wirklich?

English formulation:

Which warning drivers explain the return of substantial warning counts in D1f, and which cases remain stable despite broader synthetic stress?

Ralf/Nova working questions:

- Welche Familien dringen in die Akzeptanzregion ein?
- Welche Gewichtungen oeffnen die Tuer?
- Welche Penaltys schliessen nur scheinbar?
- Welche Kernelgroessen verschieben die Akzeptanzregion?
- Welche Decoys klingen wie die Melodie, obwohl sie nicht dazugehoeren?

Orchestra / score image:

The profile components are like instruments. Single instruments may be tuned correctly, but wrong weighting, wrong entry timing, or missing control response can let the wrong players into the melody. D1g plans to decompose these open doors transparently.

## 5. Why D1g must not be another score

The current chain is already clear:

- D1b showed a standalone residual is insufficient.
- D1c showed mimicry risk.
- D1d showed projection/collision issues.
- D1e improved the warning profile in a friendly setup.
- D1f showed that the improvement is not robust under broader stress.

D1g must therefore not introduce a new score.

D1g must perform decomposition:

- by warning type
- by decoy family
- by null family
- by `profile_weight_set`
- by `penalty_weight_set`
- by `kernel_size_label`
- by `parameter_sweep_family`
- by interaction terms
- by decision table rules

## 6. Warning-driver decomposition axes

Planned analysis axes:

A. `warning_type`:

- `control_profile_mimicry_warning`
- `residual_matched_profile_warning`
- `adversarial_profile_warning`
- `profile_weight_sensitivity_warning`
- `penalty_weight_sensitivity_warning`
- `kernel_size_sensitivity_warning`
- `null_family_overlap_warning`
- `decoy_success_warning`
- `control_overlap_warning`
- `ambiguity_warning`

B. `decoy_family`

C. `null_family`

D. `profile_weight_set_id`

E. `penalty_weight_set_id`

F. `kernel_size_label`

G. `parameter_sweep_family`

H. Interaction terms:

- `decoy_family` x `null_family`
- `decoy_family` x `profile_weight_set_id`
- `decoy_family` x `penalty_weight_set_id`
- `null_family` x `profile_weight_set_id`
- `kernel_size_label` x `decoy_family`
- `parameter_sweep_family` x `decoy_family`

I. `decision_table_rule_id`

## 7. Acceptance-region and false-accept analysis

Required diagnostic terms:

- `acceptance_region_geometry`
- `false_accept_region`
- `impostor_distribution_overlap`
- `open_space_risk`
- `representation_instability`
- `threshold_fragility`
- `manifold_intrusion`

D1f's failure mode is better interpreted as false-accept-region / impostor-overlap vulnerability than as direct metric collision.

Planned fields:

- `acceptance_region_overlap_rate`
- `false_accept_region_warning`
- `impostor_overlap_warning`
- `null_intrusion_warning`
- `decoy_intrusion_warning`
- `profile_distance_raw`
- `profile_distance_collision_penalized`
- `profile_separation_margin`

## 8. Decoy-family driver analysis

For each `decoy_family`, later implementation should report:

- `row_count`
- `warning_count_total`
- `warning_rate`
- `decoy_success_warnings_count`
- `decoy_success_rate`
- `control_overlap_warnings_count`
- `control_overlap_rate`
- `null_family_overlap_warnings_count`
- `null_family_overlap_rate`
- `mean_profile_distance_raw`
- `mean_profile_distance_collision_penalized`
- `mean_profile_separation_margin`
- `dominant_warning_type`
- `dominant_warning_rate`
- `failure_mode_label`
- `decision_table_label`

Priority decoy families to inspect:

- `residual_matched_decoy_sweep`
- `adversarial_near_duplicate_sweep`
- `profile_matched_decoy`
- `rank_stability_matched_decoy`
- `collision_penalty_evading_decoy`
- `angular_phase_matched_decoy`
- `local_response_matched_decoy`
- `multi_component_matched_decoy`

## 9. Null-family overlap analysis

For each `null_family`, later implementation should report:

- `row_count`
- `null_family_overlap_warnings_count`
- `null_family_overlap_rate`
- `mean_profile_distance_raw`
- `mean_profile_distance_collision_penalized`
- `control_overlap_rate`
- `decoy_success_rate`
- `dominant_decoy_family_overlap`
- `failure_mode_label`
- `decision_table_label`

Priority null families to inspect:

- `random_parameter_null`
- `distribution_matched_null`
- `spectrum_matched_null`
- `phase_randomized_null`
- `amplitude_preserved_null`
- `label_shuffle_null`
- `profile_shuffle_null`
- `control_family_permutation_null`

## 10. Profile-weight and penalty-weight sensitivity analysis

For `profile_weight_set_id`, later implementation should report:

- `row_count`
- `warning_rate`
- `profile_weight_sensitivity_warnings_count`
- `mean_profile_distance_raw`
- `mean_profile_distance_collision_penalized`
- `decoy_success_rate`
- `control_overlap_rate`
- `sensitivity_rank`
- `open_door_warning`

For `penalty_weight_set_id`, later implementation should report:

- `row_count`
- `warning_rate`
- `penalty_weight_sensitivity_warnings_count`
- `mean_profile_distance_raw`
- `mean_profile_distance_collision_penalized`
- `mean_penalty_gap`
- `decoy_success_rate`
- `control_overlap_rate`
- `sensitivity_rank`
- `cosmetic_lock_warning`

If warning behavior depends strongly on profile or penalty weights, the profile is not yet robust as a marker.

## 11. Kernel-size sensitivity analysis

For each `kernel_size_label`, later implementation should report:

- `row_count`
- `warning_count_total`
- `warning_rate`
- `kernel_size_sensitivity_warnings_count`
- `mean_profile_distance_raw`
- `mean_profile_distance_collision_penalized`
- `decoy_success_rate`
- `control_overlap_rate`
- `stable_candidate_count`
- `fragile_candidate_count`

Kernel-size effects must be interpreted as methodological synthetic sensitivity, not as physical system-size behavior.

## 12. Decision-table method

D1g plans transparent decision tables.

Decision tables are rule-based if-then diagnostics. They classify typical combinations of warning flags, weights, penalties, and families. They are not physical laws and not ML classifiers.

Planned rules:

`DT001_multi_driver_instability`:

IF at least 3 major warning flags are active

THEN `failure_mode_label = multi_driver_instability`

`DT002_false_accept_region_warning`:

IF `control_profile_mimicry_warning` OR `null_family_overlap_warning` OR `decoy_success_warning`

THEN `failure_mode_label = false_accept_region_overlap_driven`

`DT003_impostor_distribution_overlap`:

IF `null_family_overlap_warning` OR `control_profile_mimicry_warning`

THEN `failure_mode_label = impostor_overlap_driven`

`DT004_representation_instability`:

IF `profile_weight_sensitivity_warning` OR `penalty_weight_sensitivity_warning` OR `kernel_size_sensitivity_warning`

THEN `failure_mode_label = representation_instability_driven`

`DT005_coordinate_dominant_open_door`:

IF `profile_weight_set_id == coordinate_dominant`

AND any major overlap / decoy warning is active

THEN `failure_mode_label = coordinate_weight_open_door`

`DT006_collision_penalty_off_open_door`:

IF `penalty_weight_set_id == penalties_off`

AND any major overlap / decoy warning is active

THEN `failure_mode_label = penalty_disabled_open_door`

`DT007_control_response_low_open_door`:

IF `profile_weight_set_id` is one of `coordinate_dominant`, `angular_phase_dominant`, `local_response_dominant`, `collision_penalty_off`

AND a control / null overlap warning is active

THEN `failure_mode_label = control_response_underweighted`

`DT008_cosmetic_penalty_lock`:

IF `profile_distance_collision_penalized > profile_distance_raw`

AND decoy / control / null overlap warning remains active

THEN `failure_mode_label = penalty_cosmetic_not_separating`

`DT009_kernel_shift_warning`:

IF `kernel_size_sensitivity_warning`

THEN `failure_mode_label = kernel_size_driven`

`DT010_stable_under_tested_stress_candidate`:

IF no major warning flags are active

THEN `failure_mode_label = stable_under_tested_stress_candidate`

Ralf/Nova example:

IF `coordinate_profile_weight` is high

AND `angular_phase_weight` is low

AND `collision_penalty_weight` is off

AND `control_response_weight` is low

AND decoy / control / null warning is active

THEN `coordinate_dominant_open_door_warning`

## 13. Stable-candidate and fragile-candidate separation

Planned provisional stable-candidate criteria:

- no `control_profile_mimicry_warning`
- no `null_family_overlap_warning`
- no `decoy_success_warning`
- no `profile_weight_sensitivity_warning`
- no `penalty_weight_sensitivity_warning`
- no `kernel_size_sensitivity_warning`
- no `residual_matched_profile_warning`
- no `adversarial_profile_warning`

Planned fragile-candidate criteria:

- any major warning flag
- strong profile / penalty weight sensitivity
- null-family overlap
- decoy success
- kernel-size sensitivity

Stable candidate does not mean physical identity, diagnostic specificity, or validation.

## 14. Failure-mode taxonomy

Planned defensive failure-mode labels:

- `false_accept_region_overlap_driven`
- `impostor_overlap_driven`
- `decoy_overlap_driven`
- `null_family_overlap_driven`
- `profile_weight_driven`
- `penalty_weight_driven`
- `penalty_cosmetic_not_separating`
- `coordinate_weight_open_door`
- `control_response_underweighted`
- `kernel_size_driven`
- `adversarial_decoy_driven`
- `residual_matched_decoy_driven`
- `multi_driver_instability`
- `representation_instability_driven`
- `stable_under_tested_stress_candidate`
- `inconclusive`

No label may claim proof, proven, validated, physical identity, or positive specificity status.

## 15. Planned output files for later implementation

Planned future repo files, not created by D1g:

- `data/qsb_st_comp01d1g_warning_driver_decomposition_config.yaml`
- `scripts/run_qsb_st_comp01d1g_warning_driver_decomposition.py`
- `docs/QSB_ST_COMP01D1G_WARNING_DRIVER_DECOMPOSITION_FAILURE_MODE_ANALYSIS_RESULT_NOTE_TEMPLATE.md`

Planned future run outputs:

- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/summary.json`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/readout.md`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/warning_type_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/decoy_driver_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/null_family_driver_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/profile_weight_driver_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/penalty_weight_driver_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/kernel_size_driver_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/interaction_driver_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/stable_fragile_case_summary.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/decision_table_rules.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/decision_table_case_classification.csv`
- `runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/resolved_config.json`

## 16. Continuous field list

Planned continuous field list:

| field name | field type | field description |
| --- | --- | --- |
| `run_id` | string | Identifier for the D1g decomposition run. |
| `analysis_id` | string | Deterministic analysis row identifier. |
| `grouping_axis` | string | Grouping axis used for decomposition. |
| `grouping_value` | string | Grouping value for the row. |
| `warning_type` | string | Warning type being counted or analyzed. |
| `row_count` | integer | Number of D1f case rows in the group. |
| `warning_count` | integer | Count for a specific warning type. |
| `warning_rate` | float | Warning count divided by row count. |
| `warning_count_total` | integer | Total warning count for the group. |
| `decoy_family` | string | Decoy family label. |
| `null_family` | string | Null family label. |
| `profile_weight_set_id` | string | Profile-weight set identifier. |
| `penalty_weight_set_id` | string | Penalty-weight set identifier. |
| `kernel_size_label` | string | Kernel-size label. |
| `parameter_sweep_family` | string | Parameter sweep family label. |
| `mean_profile_distance_raw` | float | Mean raw profile distance. |
| `mean_profile_distance_collision_penalized` | float | Mean collision-penalized profile distance. |
| `mean_profile_separation_margin` | float | Mean separation margin against reference region. |
| `penalty_gap` | float | Penalized distance minus raw distance. |
| `control_overlap_warnings_count` | integer | Count of control overlap warnings. |
| `control_overlap_rate` | float | Control overlap rate. |
| `null_family_overlap_warnings_count` | integer | Count of null-family overlap warnings. |
| `null_family_overlap_rate` | float | Null-family overlap rate. |
| `decoy_success_warnings_count` | integer | Count of decoy-success warnings. |
| `decoy_success_rate` | float | Decoy-success rate. |
| `profile_weight_sensitivity_warnings_count` | integer | Count of profile-weight sensitivity warnings. |
| `profile_weight_sensitivity_rate` | float | Profile-weight sensitivity warning rate. |
| `penalty_weight_sensitivity_warnings_count` | integer | Count of penalty-weight sensitivity warnings. |
| `penalty_weight_sensitivity_rate` | float | Penalty-weight sensitivity warning rate. |
| `kernel_size_sensitivity_warnings_count` | integer | Count of kernel-size sensitivity warnings. |
| `kernel_size_sensitivity_rate` | float | Kernel-size sensitivity warning rate. |
| `ambiguity_warning_count` | integer | Count of ambiguity warnings. |
| `ambiguity_warning_rate` | float | Ambiguity warning rate. |
| `acceptance_region_overlap_rate` | float | Overlap rate with the diagnostic acceptance region. |
| `false_accept_region_warning` | boolean | True if false-accept-region risk is flagged. |
| `impostor_overlap_warning` | boolean | True if impostor overlap is flagged. |
| `null_intrusion_warning` | boolean | True if null family intrudes into accepted region. |
| `decoy_intrusion_warning` | boolean | True if decoy intrudes into accepted region. |
| `dominant_warning_type` | string | Most frequent warning type in the group. |
| `dominant_warning_rate` | float | Rate of the dominant warning type. |
| `dominant_decoy_family` | string | Dominant decoy family in a grouped result. |
| `dominant_null_family` | string | Dominant null family in a grouped result. |
| `failure_mode_label` | string | Methodological failure-mode label. |
| `decision_table_rule_id` | string | Decision-table rule identifier. |
| `decision_table_label` | string | Decision-table classification label. |
| `matched_rule_ids` | string | Semicolon-separated matched rule identifiers. |
| `severity` | string | Planned severity label: high, medium, low, or inconclusive. |
| `major_warning_count` | integer | Count of active major warning flags. |
| `stable_candidate_count` | integer | Count of rows without major warning flags. |
| `fragile_candidate_count` | integer | Count of rows with at least one major warning flag. |
| `stable_candidate_rate` | float | Stable candidate count divided by row count. |
| `fragile_candidate_rate` | float | Fragile candidate count divided by row count. |
| `interaction_axis` | string | Interaction axis, such as decoy x null. |
| `interaction_value` | string | Joined value of the interaction tuple. |
| `interaction_warning_rate` | float | Warning rate for the interaction row. |
| `decision_status` | string | Defensive decision status. |
| `warning_flags` | string | Semicolon-separated warning flags. |
| `interpretation_note` | string | Short diagnostic interpretation note. |

## 17. Acceptance criteria for later implementation

Later implementation should check at least:

- YAML config parses.
- Runner reads existing D1f `case_profile_summary.csv`.
- Runner reads existing D1f `summary.json`.
- Runner does not rerun D1f.
- Runner does not introduce a new identity score.
- All planned outputs exist.
- CSVs parse with `csv.DictReader`.
- Warning counts reconcile with D1f `summary.json`.
- Grouping summaries report `warning_count` and `warning_rate`.
- Interaction summaries include at least decoy x null, decoy x profile weight, decoy x penalty weight, and kernel x decoy.
- `decision_table_rules.csv` exists.
- `decision_table_case_classification.csv` exists.
- Decision table contains `coordinate_dominant_open_door_warning`.
- Decision table contains `false_accept_region_warning`.
- Stable / fragile split is reported.
- `specificity_established` remains false.
- No decision label claims proof.
- Readout separates Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary.
- Claim-risk grep is clean or only contains negated / Claim Boundary mentions.
- `git diff --check` passes.

## 18. Interpretation rules

Befund:

Which warning types and grouping axes dominate the D1f warning return?

Interpretation:

Are D1f failures driven mainly by decoys, null families, weight sensitivity, penalty behavior, kernel scaling, acceptance-region overlap, or interactions?

Hypothese:

Could future work reduce instability by redesigning profile component orchestration, penalties, null filters, or decoy-resistance checks?

Offene Luecke:

No physical validation, no real data, no diagnostic specificity, no physical manifold, no Lorentzian structure, no physical time, and no Pauli claim.

## 19. Decision logic

Planned defensive labels:

- `warning_driver_identified`
- `multi_driver_instability_warning`
- `false_accept_region_warning`
- `impostor_overlap_warning`
- `decoy_overlap_driver_warning`
- `null_family_overlap_driver_warning`
- `profile_weight_driver_warning`
- `penalty_weight_driver_warning`
- `cosmetic_penalty_lock_warning`
- `coordinate_dominant_open_door_warning`
- `control_response_low_open_door_warning`
- `kernel_size_driver_warning`
- `stable_under_tested_stress_candidate`
- `fragile_under_tested_stress`
- `inconclusive`
- `failed_input_consistency_check`

No label may claim proof, proven, validated, physical identity, or positive specificity status.

## 20. What this plan must not do

- does not implement the decomposition runner
- does not rerun D1f
- does not create config files
- does not create run outputs
- does not introduce a new identity score
- does not interpret D1f as specificity
- does not claim that a diagnostic manifold is physical spacetime
- does not claim Hilbert-space reconstruction
- does not claim phase-space physics
- does not attach D(A,B)
- does not construct S_rel2
- does not introduce tau as physical time
- does not derive proper time
- does not derive a Lorentzian metric
- does not validate the physical Bridge
- does not claim physical wavefunctions
- does not establish diagnostic specificity
- does not claim fermionic Pauli exclusion
- does not invoke spin-statistics
- does not claim cosmological redshift
- does not create matter particles

## 21. Claim Boundary

D1g is a warning-driver decomposition and failure-mode analysis plan.

It does not introduce a new identity score.

It does not rerun D1f.

Decision tables are transparent methodological classification rules, not physical laws.

The manifold language denotes a diagnostic coordinate space of synthetic wave-pattern descriptors.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

`psi` is a diagnostic pattern object here, not automatically a physical wavefunction.

`wave_identity_profile` is a diagnostic profile concept, not a proof of physical identity.

Failure-mode labels are methodological diagnostic labels, not physical categories.

Parameter sweeps are robustness tests, not physical parameter fitting.

Kernel-size scaling is a methodological robustness test, not a physical system-size claim.

Null families are diagnostic controls, not physical ensembles.

control mimicry warnings are methodological warnings, not failures of physics.

The D1g plan does not establish diagnostic specificity.

The D1g plan does not prove wave identity.

“wave-Pauli” is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

type-like similarity is not the same as relational identity.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1g does not attach D(A,B).

COMP01-D1g does not construct S_rel2.

COMP01-D1g does not derive a Lorentzian metric.

COMP01-D1g does not validate a physical Bridge.

COMP01-D1g does not establish diagnostic specificity.

This is synthetic diagnostic warning-driver decomposition planning only.

## 22. Current status label

current_status_label: COMP01D1G_warning_driver_decomposition_failure_mode_analysis_plan_created
