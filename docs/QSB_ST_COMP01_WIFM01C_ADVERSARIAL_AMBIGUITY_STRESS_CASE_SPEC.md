# QSB-ST COMP01-WIFM01C Adversarial / Ambiguity Stress Case — Specification

## 1. Purpose

This document specifies the future WIFM01C adversarial/ambiguity stress-case extension for the Wave Identity Fingerprint Metric route.

This task creates no runner now, no config now, no data file now, no run output now, and no implementation now. It creates no D1q and does not continue D1-letter expansion.

The specification is diagnostic only. It creates no validation of a physical model and no diagnostic specificity.

## 2. Starting point from WIFM01/WIFM01B

WIFM01 baseline values confirmed from the existing outputs:

- 10 fingerprints
- 5 comparison pairs
- 5 case families
- all expected behaviors met
- `warning_review_count: 0`
- `phase_wrap_case_count: 1`
- `phase_wrap_corrected_count: 1`
- `noncompact_separation_case_count: 2`
- `noncompact_separation_preserved_count: 2`
- `mixed_ambiguity_case_count: 1`
- `mixed_ambiguity_preserved_count: 1`

WIFM01B sensitivity sweep values confirmed from the existing outputs:

- 19 curated variants
- 10 weight variants
- 9 scale variants
- 95 pair comparisons
- `curated_variants_only: true`
- all variants expected behaviors met
- `variant_warning_review_count: 0`
- `variant_failure_review_count: 0`
- `phase_wrap_all_variants_corrected: true`
- `noncompact_separation_all_variants_preserved: true`
- `mixed_ambiguity_all_variants_preserved: true`

Both WIFM01 and WIFM01B kept the claim flags defensive:

```yaml
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
physical_metric_established: false
physical_compact_dimensions_established: false
hilbert_space_reconstruction: false
bridge_confirmation: false
```

## 3. Stress objective

WIFM01C tests whether the WIFM diagnostic metric preserves warnings and ambiguity under adversarial channel conflicts.

The core question is:

Does the WIFM diagnostic metric preserve warnings/ambiguity when compact phase agreement conflicts with non-compact differences, or when several small non-compact differences accumulate?

WIFM01C is not designed merely to stay green. It should be allowed, and in some cases expected, to produce diagnostic warning labels.

## 4. Conceptual warning shift

In WIFM01/WIFM01B, zero warning labels were expected.

In WIFM01C, some warning/adversarial labels may be expected and scientifically useful. A warning can be a correct diagnostic outcome, not necessarily a failure.

Failure occurs when adversarial cases are over-cleaned or mislabeled as simple equivalence. The goal is controlled stress behavior, not universal pass labels.

WIFM01C should distinguish expected adversarial warnings from unexpected calculation failures. The goal is not to maximize `all_expected_behaviors_met`; the goal is to avoid false over-cleaning.

## 5. Required stress case families

| case_family | construction idea | expected label | purpose | claim boundary |
| --- | --- | --- | --- | --- |
| `phase_agrees_delta_k_conflicts` | `delta_phase` nearly equal; `delta_k` strongly different; slope/intercept/amplitude mostly similar | `adversarial_phase_agreement_noncompact_conflict` | test that phase similarity does not erase spectral/wavenumber conflict | diagnostic conflict only |
| `phase_wrap_agrees_shape_conflicts` | `delta_phase` near wrap boundary and circularly close; `delta_k` similar; `slope_diff` and `intercept_diff` strongly different | `adversarial_wrap_with_shape_conflict` | test that successful phase-wrap correction does not hide local-shape conflict | diagnostic conflict only |
| `many_small_differences_accumulate` | no single channel difference is large; multiple channels differ moderately; combined metric distance enters warning/review band | `cumulative_small_difference_warning` | test whether distributed weak differences can become diagnostically relevant | diagnostic accumulation only |
| `amplitude_conflict_phase_agrees` | phase and `delta_k` similar; `amplitude_diff` strongly different; slope/intercept mildly different | `amplitude_shape_conflict_warning` | test that amplitude/local-channel conflict is not ignored | diagnostic channel conflict only |
| `ambiguous_balanced_conflict` | compact coordinate suggests similarity; non-compact coordinates partly conflict but not decisively | `ambiguous_multi_channel_review` | preserve ambiguity instead of forcing same/different classification | diagnostic ambiguity only |
| `overcleaning_probe` | phase wrap is corrected, but at least one non-compact channel strongly conflicts | `overcleaning_risk_detected` or `adversarial_wrap_with_shape_conflict` | detect metric logic that overprivileges compact phase agreement | diagnostic over-cleaning probe only |
| `near_identity_control` | very small differences across all channels | `metric_equivalent_expected` | keep a positive sanity control in the stress set | diagnostic sanity control only |
| `baseline_reference_replay` | include or reference original WIFM01 toy cases as baseline replay | same labels as WIFM01 | ensure new stress logic does not break baseline behavior | diagnostic replay only |

## 6. Diagnostic labels

Existing WIFM labels retained:

- `metric_equivalent_expected`
- `phase_wrap_corrected_by_circular_metric`
- `noncompact_difference_preserved`
- `local_shape_difference_preserved`
- `mixed_ambiguity_preserved`
- `diagnostic_warning_review_needed`

New adversarial/stress labels:

- `adversarial_phase_agreement_noncompact_conflict`
- `adversarial_wrap_with_shape_conflict`
- `cumulative_small_difference_warning`
- `amplitude_shape_conflict_warning`
- `ambiguous_multi_channel_review`
- `overcleaning_risk_detected`

These labels remain diagnostic decision labels only. They are not physical identity truth labels.

## 7. Future files

Future source files, not created now:

- `data/qsb_st_comp01_wifm01c_adversarial_ambiguity_stress_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01c_adversarial_ambiguity_stress.py`

Future output folder, not created now:

- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/`

## 8. Future config requirements

Conceptual YAML structure:

```yaml
block_id: QSB-ST-COMP01-WIFM01C
route_name: Wave Identity Fingerprint Metric
stress_version: wifm01c_adversarial_ambiguity_stress_v1
run_id: adversarial_ambiguity_stress_open
output_dir: runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open
input_mode: inline_adversarial_synthetic_cases
phase_period: 6.283185307179586

baseline_source:
  wifm01_result_note: docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md
  wifm01b_result_note: docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_RESULT_NOTE.md
  wifm01_config: data/qsb_st_comp01_wifm01_minimal_metric_config.yaml
  wifm01b_config: data/qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep_config.yaml

coordinate_scales:
  delta_k: 1.0
  slope_diff: 1.0
  intercept_diff: 1.0
  amplitude_diff: 1.0

weights:
  delta_k: 1.0
  delta_phase: 1.0
  slope_diff: 1.0
  intercept_diff: 1.0
  amplitude_diff: 1.0

stress_thresholds:
  near_zero_distance: 1.0e-9
  strong_channel_conflict_min: 0.5
  moderate_channel_difference_min: 0.1
  cumulative_warning_distance_min: 0.25
  cumulative_warning_distance_max: 1.5
  ambiguity_min_distance: 0.1
  ambiguity_max_distance: 1.5
  overcleaning_conflict_min: 0.5

stress_fingerprints:
  - explicit toy fingerprints for all adversarial families

stress_pairs:
  - one or more comparison pairs for each adversarial family

claim_boundary:
  specificity_established: false
  phase_is_physical: false
  phase_is_synthetic_diagnostic: true
  physical_metric_established: false
  physical_compact_dimensions_established: false
  hilbert_space_reconstruction: false
  bridge_confirmation: false
  no_real_data: true
  no_physical_model_validation: true
  no_physical_phase_reconstruction: true
  no_physical_spacetime_geometry: true
  no_lorentzian_metric: true
  no_pauli_spin_statistics_claim: true
  mastermind_status: parked_not_implemented
  knuth_status: parked_not_implemented
  manifold_status: parked_not_implemented

output_files:
  summary_json: summary.json
  readout_md: readout.md
  stress_fingerprint_input_table_csv: stress_fingerprint_input_table.csv
  stress_pair_metric_comparison_csv: stress_pair_metric_comparison.csv
  case_family_stress_summary_csv: case_family_stress_summary.csv
  label_stress_summary_csv: label_stress_summary.csv
  overcleaning_risk_summary_csv: overcleaning_risk_summary.csv
  adversarial_channel_conflict_summary_csv: adversarial_channel_conflict_summary.csv
  baseline_replay_summary_csv: baseline_replay_summary.csv
  resolved_config_json: resolved_config.json
```

All stress fingerprints, stress pairs, thresholds, scales, and weights must be explicit. The future runner must not infer hidden scales or tune values automatically.

## 9. Future input schemas

Future `stress_fingerprint_input_table.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `fingerprint_id` | string | Stable synthetic fingerprint identifier. |
| `case_family` | string | Required stress case family. |
| `case_role` | string | Role in the comparison pair, for example left/right/control. |
| `delta_k` | float | Non-compact spectral/wavenumber diagnostic coordinate. |
| `delta_phase` | float | Compact phase-like diagnostic coordinate. |
| `slope_diff` | float | Non-compact local-slope diagnostic coordinate. |
| `intercept_diff` | float | Non-compact local-intercept diagnostic coordinate. |
| `amplitude_diff` | float | Non-compact amplitude diagnostic coordinate. |
| `expected_relation` | string | Expected diagnostic decision label for the stress pair. |
| `adversarial_intent` | string | Human-readable intent of the stress construction. |
| `notes` | string | Additional diagnostic notes; no hidden assumptions. |

Future `stress_pair_metric_comparison.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `pair_id` | string | Stable stress pair identifier. |
| `left_fingerprint_id` | string | Left fingerprint identifier. |
| `right_fingerprint_id` | string | Right fingerprint identifier. |
| `case_family` | string | Required stress case family. |
| `expected_relation` | string | Expected diagnostic label for the pair. |
| `naive_phase_delta` | float | Raw absolute phase delta before circular correction. |
| `circular_phase_delta` | float | Circular phase delta after modulo handling. |
| `delta_k_component` | float | Normalized `delta_k` difference. |
| `slope_diff_component` | float | Normalized `slope_diff` difference. |
| `intercept_diff_component` | float | Normalized `intercept_diff` difference. |
| `amplitude_diff_component` | float | Normalized `amplitude_diff` difference. |
| `noncompact_conflict_norm` | float | Combined non-compact conflict norm. |
| `cumulative_difference_norm` | float | Combined compact/non-compact diagnostic norm for stress review. |
| `naive_metric_distance` | float | Weighted diagnostic distance using naive phase delta. |
| `circular_metric_distance` | float | Weighted diagnostic distance using circular phase delta. |
| `distance_delta_naive_minus_circular` | float | Difference between naive and circular distances. |
| `diagnostic_decision_label` | string | Assigned diagnostic label. |
| `expected_adversarial_behavior_met` | boolean | Whether the expected stress behavior occurred. |
| `overcleaning_risk_flag` | boolean | Whether the pair shows a possible over-cleaning risk. |
| `diagnostic_reason` | string | Short reason for the label. |
| `claim_boundary` | string | Row-level diagnostic boundary statement. |

## 10. Future output artifacts

Future WIFM01C outputs:

- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/readout.md`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/stress_fingerprint_input_table.csv`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/stress_pair_metric_comparison.csv`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/case_family_stress_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/label_stress_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/overcleaning_risk_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/adversarial_channel_conflict_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/baseline_replay_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01C/adversarial_ambiguity_stress_open/resolved_config.json`

All outputs are future diagnostic artifacts only.

## 11. Future output schemas

Future `case_family_stress_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `case_family` | string | Stress case family. |
| `pair_count` | integer | Number of stress pairs in the family. |
| `expected_label` | string | Expected diagnostic label for the family. |
| `observed_labels` | JSON object | Counts of observed labels. |
| `expected_adversarial_behavior_met` | boolean | Whether expected stress behavior was met for the family. |
| `overcleaning_risk_count` | integer | Count of pairs with over-cleaning risk. |
| `diagnostic_warning_count` | integer | Count of warning/adversarial review labels. |
| `stress_interpretation` | string | Short diagnostic interpretation of the family. |
| `claim_boundary` | string | Case-family boundary statement. |

Future `label_stress_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `diagnostic_decision_label` | string | Diagnostic label being summarized. |
| `count` | integer | Count of this label across stress pairs. |
| `case_families` | JSON array | Case families where the label appears. |
| `expected_or_unexpected` | string | Whether the label was expected in the stress design. |
| `interpretation_boundary` | string | Boundary statement for interpreting label counts. |

Future `overcleaning_risk_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `metric` | string | Summary metric name. |
| `value` | float or integer | Summary metric value. |
| `interpretation_boundary` | string | Boundary statement for over-cleaning risk review. |

Required `overcleaning_risk_summary.csv` metrics:

- `total_pair_count`
- `overcleaning_probe_pair_count`
- `overcleaning_risk_detected_count`
- `phase_wrap_label_without_conflict_warning_count`
- `expected_overcleaning_warning_count`
- `unexpected_overcleaning_clean_label_count`

Future `adversarial_channel_conflict_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `metric` | string | Summary metric name. |
| `value` | float or integer | Summary metric value. |
| `interpretation_boundary` | string | Boundary statement for adversarial channel-conflict review. |

Required `adversarial_channel_conflict_summary.csv` metrics:

- `adversarial_pair_count`
- `phase_agreement_noncompact_conflict_count`
- `wrap_with_shape_conflict_count`
- `cumulative_small_difference_warning_count`
- `amplitude_shape_conflict_warning_count`
- `ambiguous_multi_channel_review_count`

Future `baseline_replay_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `metric` | string | Summary metric name. |
| `value` | float or integer | Summary metric value. |
| `interpretation_boundary` | string | Boundary statement for baseline replay review. |

Required `baseline_replay_summary.csv` metrics:

- `baseline_replay_pair_count`
- `baseline_replay_expected_behavior_met_count`
- `baseline_replay_warning_count`
- `baseline_replay_failure_count`

## 12. Future summary.json requirements

Future `summary.json` must include:

- `block_id`
- `run_id`
- `stress_version`
- `created_at`
- `stress_fingerprint_count`
- `stress_pair_count`
- `case_family_count`
- `baseline_replay_pair_count`
- `adversarial_pair_count`
- `expected_adversarial_behaviors_met`
- `expected_adversarial_behavior_count`
- `expected_adversarial_behavior_met_count`
- `overcleaning_risk_case_count`
- `overcleaning_risk_detected_count`
- `unexpected_overcleaning_clean_label_count`
- `diagnostic_warning_review_count`
- `diagnostic_failure_review_count`
- `diagnostic_decision_label_counts`
- `case_family_label_map`
- `strong_conflict_case_count`
- `cumulative_warning_case_count`
- `ambiguity_review_case_count`
- `baseline_replay_expected_behavior_met`
- `specificity_established`
- `phase_is_physical`
- `phase_is_synthetic_diagnostic`
- `physical_metric_established`
- `physical_compact_dimensions_established`
- `hilbert_space_reconstruction`
- `bridge_confirmation`
- `mastermind_status`
- `knuth_status`
- `manifold_status`
- `claim_boundary`
- `output_files`

All physical/escalation claim flags must remain false. `phase_is_synthetic_diagnostic` must remain true.

## 13. Future readout.md requirements

Future readout title:

`# QSB-ST COMP01-WIFM01C Adversarial / Ambiguity Stress Cases — Readout`

Future readout headings:

- `## 1. Purpose`
- `## 2. Baseline context`
- `## 3. Stress case families`
- `## 4. Metric and warning logic`
- `## 5. Adversarial conflict results`
- `## 6. Overcleaning risk results`
- `## 7. Baseline replay results`
- `## 8. Befund`
- `## 9. Interpretation`
- `## 10. Hypothese`
- `## 11. Offene Lücke`
- `## 12. Claim Boundary`
- `## 13. Files created`

The readout must state that WIFM01C is diagnostic stress testing only.

## 14. Acceptance criteria for future implementation

Future implementation acceptance criteria:

- required source files are created
- required output files are created
- all required stress case families are represented
- baseline replay is included
- `near_identity_control` remains equivalent
- `phase_agrees_delta_k_conflicts` produces `adversarial_phase_agreement_noncompact_conflict`
- `phase_wrap_agrees_shape_conflicts` produces `adversarial_wrap_with_shape_conflict`
- `many_small_differences_accumulate` produces `cumulative_small_difference_warning`
- `amplitude_conflict_phase_agrees` produces `amplitude_shape_conflict_warning`
- `ambiguous_balanced_conflict` produces `ambiguous_multi_channel_review`
- `overcleaning_probe` detects overcleaning risk or conflict warning
- expected adversarial warnings are not treated as implementation failure
- unexpected clean labels in adversarial cases are counted
- all physical/escalation claim flags are false, with `phase_is_synthetic_diagnostic: true`
- no hidden tuning
- `git diff --check` passes
- no claim-risk forbidden phrases

## 15. Non-goals

- no implementation now
- no physical phase reconstruction
- no physical compact dimensions
- no spacetime metric
- no Lorentzian metric
- no Hilbert-space norm
- no proof of wave identity
- no diagnostic specificity
- no Bridge confirmation
- no D1q

## 16. Befund expected from this specification

This specification defines the WIFM01C adversarial case plan, stress families, warning/overcleaning labels, future outputs, and future schemas.

It prepares a future implementation without hidden assumptions. It does not calculate new scores and does not create WIFM01C output.

## 17. Interpretation

This spec prepares a harder test of the WIFM route. It asks whether compact phase agreement can be prevented from over-cleaning non-compact conflicts and treats warnings as potentially correct diagnostic outcomes.

It makes no physical robustness claim, no physical metric claim, no compact dimension claim, no identity proof, and no Bridge confirmation.

## 18. Hypothese

If WIFM01C correctly preserves adversarial warnings and ambiguity while retaining near-identity sanity behavior, this would support the methodological usefulness of the WIFM diagnostic metric as a stress-testable fingerprint-space tool in the toy setting.

This remains a hypothesis only.

## 19. Offene Lücke

- no runner yet
- no config yet
- no run output yet
- no stress result yet
- no real data
- no broad control set
- no physical model validation
- no diagnostic specificity
- no physical compact dimensions
- no physical phase reconstruction
- no physical wavefunction
- no Hilbert-space reconstruction
- no Lorentzian metric
- no physical spacetime geometry
- no Pauli/spin-statistics claim
- no Bridge confirmation
- identity space remains open
- adversarial labels are diagnostic choices, not physical identity truth labels

## 20. Claim Boundary

- adversarial/ambiguity stress-case specification only
- no implementation
- no new scores calculated
- no physical phase
- no physical metric
- no physical manifold
- no physical compact dimensions
- no string compactification claim
- no physical model validation
- no diagnostic specificity
- no Hilbert-space reconstruction
- no conversion of fingerprint metric into spacetime metric
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- physical_metric_established: false
- physical_compact_dimensions_established: false
- hilbert_space_reconstruction: false
- bridge_confirmation: false
- Mastermind, Knuth, manifold, and role-permutation remain parked

## 21. Next-step recommendation

Recommended next step:

`QSB-ST-COMP01-WIFM01C Adversarial / Ambiguity Stress Case Config + Runner Implementation`

Purpose:

- create explicit adversarial config
- implement stress-case runner
- generate adversarial toy fingerprints
- compute WIFM-style metrics and conflict norms
- produce stress summaries
- distinguish expected warnings from implementation failures
- no physical claims

## 22. Files created / checked

This task creates only:

- `docs/QSB_ST_COMP01_WIFM01C_ADVERSARIAL_AMBIGUITY_STRESS_CASE_SPEC.md`

Checked WIFM01/WIFM01B context/spec/result docs:

- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_RUNNER_SPEC.md`
- `docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_SPEC.md`
- `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_RESULT_NOTE.md`

Checked WIFM01/WIFM01B config/runner files:

- `data/qsb_st_comp01_wifm01_minimal_metric_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01_minimal_metric.py`
- `data/qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep.py`

Checked WIFM01/WIFM01B outputs:

- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/pair_metric_comparison.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/pair_metric_sweep_long.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/case_family_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/label_stability_summary.csv`
