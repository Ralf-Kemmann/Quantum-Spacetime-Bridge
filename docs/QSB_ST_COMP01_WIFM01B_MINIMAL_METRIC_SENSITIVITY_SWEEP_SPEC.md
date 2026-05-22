# QSB-ST COMP01-WIFM01B Minimal Metric Sensitivity Sweep — Specification

## 1. Purpose

This document specifies the future WIFM01B sensitivity sweep for the minimal Wave Identity Fingerprint Metric.

This task creates no runner now, no config now, no data file now, no run output now, and no implementation now. It creates no D1q and does not continue D1-letter expansion.

The specification is diagnostic only. It creates no validation of a physical model and no diagnostic specificity.

## 2. Starting point from WIFM01

WIFM01 is the baseline minimal metric toy run:

```yaml
block_id: QSB-ST-COMP01-WIFM01
metric_version: wifm01_minimal_circular_phase_metric_v1
fingerprint_count: 10
comparison_pair_count: 5
case_family_count: 5
phase_wrap_case_count: 1
phase_wrap_corrected_count: 1
noncompact_separation_case_count: 2
noncompact_separation_preserved_count: 2
mixed_ambiguity_case_count: 1
mixed_ambiguity_preserved_count: 1
all_expected_behaviors_met: true
warning_review_count: 0
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
physical_metric_established: false
physical_compact_dimensions_established: false
hilbert_space_reconstruction: false
bridge_confirmation: false
```

WIFM01 used 10 synthetic relational fingerprint rows and 5 comparison pairs. All expected toy behaviors were met. The baseline had `warning_review_count: 0`, one phase-wrap case, two non-compact separation cases, and one mixed ambiguity case. All claim flags remained false.

## 3. Sweep objective

WIFM01B tests whether the WIFM01 diagnostic behavior remains stable under explicit controlled variation of diagnostic weights and toy normalization scales.

The sweep is sensitivity analysis, not parameter optimization. It must not auto-tune values to make results look good, infer physical units, or create physical claims.

Core question:

Does the tiny WIFM01 diagnostic behavior remain stable across reasonable explicit perturbations of weights and scales?

## 4. Sensitivity dimensions

Future WIFM01B varies only:

- diagnostic weights
- explicit toy coordinate scales

Fixed elements:

- `phase_period` remains fixed at `2π`, represented as `6.283185307179586`
- WIFM01 toy fingerprints remain fixed
- WIFM01 toy comparison pairs remain fixed
- only metric weighting/scaling changes

The variant lists are deliberately small and transparent.

## 5. Weight variants

| variant_id | changed weights | purpose | expected stability check |
| --- | --- | --- | --- |
| `baseline_equal_weights` | `delta_k: 1.0`, `delta_phase: 1.0`, `slope_diff: 1.0`, `intercept_diff: 1.0`, `amplitude_diff: 1.0` | baseline reference for WIFM01-like behavior | all WIFM01 expected labels are reproduced |
| `phase_low_weight` | `delta_phase: 0.25`, others `1.0` | reduce phase contribution | `phase_wrap_equivalent` remains circular-corrected |
| `phase_high_weight` | `delta_phase: 4.0`, others `1.0` | increase phase contribution | phase wrap correction remains visible without creating physical phase claims |
| `delta_k_low_weight` | `delta_k: 0.25`, others `1.0` | reduce spectral/wavenumber diagnostic channel | `same_looking_not_same_delta_k` remains reviewed for non-compact separation |
| `delta_k_high_weight` | `delta_k: 4.0`, others `1.0` | increase spectral/wavenumber diagnostic channel | non-compact delta-k separation remains preserved |
| `local_shape_low_weight` | `slope_diff: 0.25`, `intercept_diff: 0.25`, others `1.0` | reduce local-shape channels | `same_looking_not_same_slope_intercept` remains local-shape separated or explicitly reviewed |
| `local_shape_high_weight` | `slope_diff: 4.0`, `intercept_diff: 4.0`, others `1.0` | increase local-shape channels | local-shape separation remains preserved |
| `amplitude_high_weight` | `amplitude_diff: 4.0`, others `1.0` | increase amplitude channel | amplitude weighting does not hide required phase/non-compact checks |
| `balanced_noncompact_high` | `delta_k: 2.0`, `slope_diff: 2.0`, `intercept_diff: 2.0`, `amplitude_diff: 2.0`, `delta_phase: 1.0` | emphasize non-compact channels together | non-compact separation remains preserved while phase-wrap correction remains detectable |
| `compact_dominant` | `delta_phase: 8.0`, all non-compact weights `0.5` | stress compact-coordinate dominance | phase-wrap correction remains circular and non-compact cases are not silently collapsed |

## 6. Scale variants

| variant_id | changed scales | purpose | expected stability check |
| --- | --- | --- | --- |
| `baseline_scales` | all scales `1.0` | baseline reference for explicit toy scales | all WIFM01 expected labels are reproduced |
| `delta_k_tight_scale` | `delta_k: 0.5`, others `1.0` | make delta-k normalized separation larger | delta-k separation remains preserved |
| `delta_k_loose_scale` | `delta_k: 2.0`, others `1.0` | make delta-k normalized separation smaller | delta-k case remains separated or explicitly reviewed |
| `local_shape_tight_scale` | `slope_diff: 0.5`, `intercept_diff: 0.5`, others `1.0` | make local-shape normalized separation larger | local-shape separation remains preserved |
| `local_shape_loose_scale` | `slope_diff: 2.0`, `intercept_diff: 2.0`, others `1.0` | make local-shape normalized separation smaller | local-shape case remains separated or explicitly reviewed |
| `amplitude_tight_scale` | `amplitude_diff: 0.5`, others `1.0` | make amplitude normalized separation larger | amplitude scaling does not override required case-family checks |
| `amplitude_loose_scale` | `amplitude_diff: 2.0`, others `1.0` | make amplitude normalized separation smaller | amplitude scaling does not hide required case-family checks |
| `combined_loose_noncompact_scale` | `delta_k: 2.0`, `slope_diff: 2.0`, `intercept_diff: 2.0`, `amplitude_diff: 2.0`, `delta_phase` unchanged | loosen all non-compact toy scales | non-compact cases remain separated or explicitly reviewed |
| `combined_tight_noncompact_scale` | `delta_k: 0.5`, `slope_diff: 0.5`, `intercept_diff: 0.5`, `amplitude_diff: 0.5`, `delta_phase` unchanged | tighten all non-compact toy scales | non-compact separation remains preserved |

## 7. Sweep mode

The first implementation should use:

```yaml
curated_variants_only: true
```

The first sweep should avoid full Cartesian bloat. Variant count must be reported from config. There must be no hidden inferred variants and no automatic tuning.

The future implementation may define either a Cartesian or curated variant set, but this specification recommends curated mode first. Expected variants are baseline plus the listed weight variants plus the listed scale variants. The exact count should be determined from the future config and reported in `summary.json`.

## 8. Stability criteria

Required stability checks:

- `phase_wrap_equivalent` remains circular-corrected
- `same_relational_identity` remains near zero
- `same_looking_not_same_delta_k` remains non-compact separated
- `same_looking_not_same_slope_intercept` remains local-shape separated
- `mixed_ambiguity_case` remains ambiguity/review-like, not forced into clean same/different
- `warning_review_count` remains zero or is explicitly explained if nonzero
- claim flags remain false

Allowed stability labels:

- `baseline_reference`
- `stable_expected_behavior_preserved`
- `sensitivity_warning_review_needed`
- `expected_ambiguity_shift`
- `diagnostic_failure_review_needed`

## 9. Future files

Future source files, not created now:

- `data/qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep.py`

Future output folder, not created now:

- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/`

## 10. Future config requirements

Conceptual YAML shape:

```yaml
block_id: QSB-ST-COMP01-WIFM01B
run_id: minimal_metric_sensitivity_sweep_open
sweep_version: wifm01b_weight_scale_sensitivity_v1
baseline_source:
  block_id: QSB-ST-COMP01-WIFM01
  config_path: data/qsb_st_comp01_wifm01_minimal_metric_config.yaml
  output_summary: runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/summary.json
curated_variants_only: true
phase_period: 6.283185307179586
weight_variants:
  - variant_id: baseline_equal_weights
    weights:
      delta_k: 1.0
      delta_phase: 1.0
      slope_diff: 1.0
      intercept_diff: 1.0
      amplitude_diff: 1.0
  - variant_id: phase_low_weight
    weights:
      delta_phase: 0.25
      others: 1.0
  - variant_id: phase_high_weight
    weights:
      delta_phase: 4.0
      others: 1.0
  - variant_id: delta_k_low_weight
    weights:
      delta_k: 0.25
      others: 1.0
  - variant_id: delta_k_high_weight
    weights:
      delta_k: 4.0
      others: 1.0
  - variant_id: local_shape_low_weight
    weights:
      slope_diff: 0.25
      intercept_diff: 0.25
      others: 1.0
  - variant_id: local_shape_high_weight
    weights:
      slope_diff: 4.0
      intercept_diff: 4.0
      others: 1.0
  - variant_id: amplitude_high_weight
    weights:
      amplitude_diff: 4.0
      others: 1.0
  - variant_id: balanced_noncompact_high
    weights:
      delta_k: 2.0
      slope_diff: 2.0
      intercept_diff: 2.0
      amplitude_diff: 2.0
      delta_phase: 1.0
  - variant_id: compact_dominant
    weights:
      delta_phase: 8.0
      noncompact: 0.5
scale_variants:
  - variant_id: baseline_scales
    scales:
      all: 1.0
  - variant_id: delta_k_tight_scale
    scales:
      delta_k: 0.5
      others: 1.0
  - variant_id: delta_k_loose_scale
    scales:
      delta_k: 2.0
      others: 1.0
  - variant_id: local_shape_tight_scale
    scales:
      slope_diff: 0.5
      intercept_diff: 0.5
      others: 1.0
  - variant_id: local_shape_loose_scale
    scales:
      slope_diff: 2.0
      intercept_diff: 2.0
      others: 1.0
  - variant_id: amplitude_tight_scale
    scales:
      amplitude_diff: 0.5
      others: 1.0
  - variant_id: amplitude_loose_scale
    scales:
      amplitude_diff: 2.0
      others: 1.0
  - variant_id: combined_loose_noncompact_scale
    scales:
      delta_k: 2.0
      slope_diff: 2.0
      intercept_diff: 2.0
      amplitude_diff: 2.0
      delta_phase: unchanged
  - variant_id: combined_tight_noncompact_scale
    scales:
      delta_k: 0.5
      slope_diff: 0.5
      intercept_diff: 0.5
      amplitude_diff: 0.5
      delta_phase: unchanged
claim_boundary:
  specificity_established: false
  phase_is_physical: false
  phase_is_synthetic_diagnostic: true
  physical_metric_established: false
  physical_compact_dimensions_established: false
  hilbert_space_reconstruction: false
  bridge_confirmation: false
  mastermind_status: parked_not_implemented
  knuth_status: parked_not_implemented
  manifold_status: parked_not_implemented
output_files:
  summary_json: summary.json
  readout_md: readout.md
  sweep_variant_summary_csv: sweep_variant_summary.csv
  pair_metric_sweep_long_csv: pair_metric_sweep_long.csv
  case_family_stability_summary_csv: case_family_stability_summary.csv
  label_stability_summary_csv: label_stability_summary.csv
  phase_wrap_stability_summary_csv: phase_wrap_stability_summary.csv
  noncompact_separation_stability_summary_csv: noncompact_separation_stability_summary.csv
  ambiguity_stability_summary_csv: ambiguity_stability_summary.csv
  resolved_config_json: resolved_config.json
```

All variants must be explicit in config.

## 11. Future output artifacts

Future WIFM01B outputs:

- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/readout.md`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/sweep_variant_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/pair_metric_sweep_long.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/case_family_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/label_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/phase_wrap_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/noncompact_separation_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/ambiguity_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/resolved_config.json`

All outputs are future diagnostic artifacts only.

## 12. Future output schemas

Future `sweep_variant_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `variant_id` | string | Stable variant identifier. |
| `variant_family` | string | Weight, scale, baseline, or curated combined family. |
| `variant_description` | string | Short explicit description of the variant. |
| `weight_delta_k` | float | Diagnostic weight for `delta_k`. |
| `weight_delta_phase` | float | Diagnostic weight for `delta_phase`. |
| `weight_slope_diff` | float | Diagnostic weight for `slope_diff`. |
| `weight_intercept_diff` | float | Diagnostic weight for `intercept_diff`. |
| `weight_amplitude_diff` | float | Diagnostic weight for `amplitude_diff`. |
| `scale_delta_k` | float | Explicit toy normalization scale for `delta_k`. |
| `scale_slope_diff` | float | Explicit toy normalization scale for `slope_diff`. |
| `scale_intercept_diff` | float | Explicit toy normalization scale for `intercept_diff`. |
| `scale_amplitude_diff` | float | Explicit toy normalization scale for `amplitude_diff`. |
| `all_expected_behaviors_met` | boolean | Whether all expected toy behaviors were met for the variant. |
| `warning_review_count` | integer | Count of warning/review labels in the variant. |
| `phase_wrap_corrected_count` | integer | Count of phase-wrap cases corrected by circular handling. |
| `noncompact_separation_preserved_count` | integer | Count of non-compact separation cases preserved. |
| `mixed_ambiguity_preserved_count` | integer | Count of mixed ambiguity cases preserved. |
| `stability_label` | string | One of the allowed stability labels. |
| `claim_boundary` | string | Row-level diagnostic boundary statement. |

Future `pair_metric_sweep_long.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `variant_id` | string | Stable variant identifier. |
| `pair_id` | string | Pair identifier inherited from WIFM01 toy pairs. |
| `case_family` | string | Required toy case family. |
| `expected_relation` | string | Expected diagnostic relation for the toy case. |
| `naive_phase_delta` | float | Raw absolute phase delta before circular correction. |
| `circular_phase_delta` | float | Circular phase delta after modulo handling. |
| `naive_metric_distance` | float | Weighted diagnostic distance using naive phase delta. |
| `circular_metric_distance` | float | Weighted diagnostic distance using circular phase delta. |
| `distance_delta_naive_minus_circular` | float | Difference between naive and circular distances. |
| `diagnostic_decision_label` | string | Diagnostic label assigned under the variant. |
| `baseline_decision_label` | string | Baseline WIFM01 label for the same pair. |
| `label_changed_from_baseline` | boolean | Whether the variant label differs from baseline. |
| `distance_shift_from_baseline` | float | Circular-distance shift relative to baseline. |
| `diagnostic_reason` | string | Short review reason for the assigned label. |
| `claim_boundary` | string | Row-level diagnostic boundary statement. |

Future `case_family_stability_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `case_family` | string | Required toy case family. |
| `variant_count` | integer | Number of variants evaluated for the case family. |
| `stable_variant_count` | integer | Count of variants preserving expected diagnostic behavior. |
| `changed_label_variant_count` | integer | Count of variants with labels changed from baseline. |
| `warning_variant_count` | integer | Count of variants requiring warning/review. |
| `baseline_label` | string | Baseline WIFM01 label for the case family. |
| `observed_labels` | JSON object | Label counts observed across variants. |
| `stability_summary` | string | Short diagnostic stability summary. |
| `claim_boundary` | string | Case-family boundary statement. |

Future `label_stability_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `diagnostic_decision_label` | string | Diagnostic label being summarized. |
| `baseline_count` | integer | Count of the label in the WIFM01 baseline. |
| `min_count_across_variants` | integer | Minimum count observed across variants. |
| `max_count_across_variants` | integer | Maximum count observed across variants. |
| `variant_count_with_label` | integer | Number of variants in which the label appears. |
| `interpretation_boundary` | string | Boundary statement for interpreting label stability. |

Future `phase_wrap_stability_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `metric` | string | Summary metric name. |
| `value` | float or integer | Summary metric value. |
| `interpretation_boundary` | string | Boundary statement for phase-wrap stability. |

Required `phase_wrap_stability_summary.csv` metrics:

- `variant_count`
- `phase_wrap_variant_count`
- `phase_wrap_corrected_variant_count`
- `phase_wrap_correction_failure_count`
- `min_distance_delta_naive_minus_circular`
- `max_distance_delta_naive_minus_circular`
- `mean_distance_delta_naive_minus_circular`

Future `noncompact_separation_stability_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `metric` | string | Summary metric name. |
| `value` | float or integer | Summary metric value. |
| `interpretation_boundary` | string | Boundary statement for non-compact separation stability. |

Required `noncompact_separation_stability_summary.csv` metrics:

- `variant_count`
- `noncompact_separation_case_count_per_variant`
- `noncompact_separation_preserved_min`
- `noncompact_separation_preserved_max`
- `noncompact_separation_failure_variant_count`

Future `ambiguity_stability_summary.csv` field list:

| field name | field type | description |
| --- | --- | --- |
| `metric` | string | Summary metric name. |
| `value` | float or integer | Summary metric value. |
| `interpretation_boundary` | string | Boundary statement for mixed ambiguity stability. |

Required `ambiguity_stability_summary.csv` metrics:

- `variant_count`
- `mixed_ambiguity_case_count_per_variant`
- `mixed_ambiguity_preserved_count_min`
- `mixed_ambiguity_preserved_count_max`
- `ambiguity_warning_variant_count`

## 13. Future summary.json requirements

Future `summary.json` must include:

- `block_id`
- `run_id`
- `sweep_version`
- `baseline_source_block_id`
- `baseline_source_summary`
- `variant_count`
- `weight_variant_count`
- `scale_variant_count`
- `curated_variants_only`
- `case_family_count`
- `comparison_pair_count_per_variant`
- `all_variants_expected_behaviors_met`
- `variant_warning_review_count`
- `variant_failure_review_count`
- `phase_wrap_all_variants_corrected`
- `noncompact_separation_all_variants_preserved`
- `mixed_ambiguity_all_variants_preserved`
- `stability_label_counts`
- `diagnostic_decision_label_count_ranges`
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

All claim-boundary booleans must remain false except `phase_is_synthetic_diagnostic`, which must remain true.

## 14. Future readout.md requirements

Future readout title:

`# QSB-ST COMP01-WIFM01B Minimal Metric Sensitivity Sweep — Readout`

Future readout headings:

- `## 1. Purpose`
- `## 2. Baseline input`
- `## 3. Sweep variants`
- `## 4. Stability checks`
- `## 5. Phase-wrap stability`
- `## 6. Non-compact separation stability`
- `## 7. Mixed ambiguity stability`
- `## 8. Befund`
- `## 9. Interpretation`
- `## 10. Hypothese`
- `## 11. Offene Lücke`
- `## 12. Claim Boundary`
- `## 13. Files created`

The readout must state that WIFM01B is diagnostic sensitivity analysis only.

## 15. Acceptance criteria for future implementation

Future implementation acceptance criteria:

- required source files are created
- required output files are created
- `variant_count > 1`
- baseline variant is included
- all listed variant families are included
- all required case families are present for every variant
- `phase_wrap_all_variants_corrected` is true unless explicitly justified
- `noncompact_separation_all_variants_preserved` is true unless explicitly justified
- `mixed_ambiguity_all_variants_preserved` is true unless explicitly justified
- all claim flags are false except `phase_is_synthetic_diagnostic: true`
- no hidden tuning
- `git diff --check` passes
- no claim-risk forbidden phrases

## 16. Non-goals

- no implementation now
- no parameter optimization
- no physical phase reconstruction
- no physical compact dimensions
- no spacetime metric
- no Lorentzian metric
- no Hilbert-space norm
- no proof of wave identity
- no diagnostic specificity
- no Bridge confirmation
- no D1q

## 17. Befund expected from this specification

This specification defines the WIFM01B sensitivity plan, variant families, stability criteria, future outputs, and future schemas.

It prepares a future implementation without hidden assumptions. It does not calculate new scores and does not create WIFM01B output.

## 18. Interpretation

This spec prepares controlled diagnostic robustness testing. It asks whether WIFM01 behavior is stable under explicit weight/scale perturbations and guards against one-parameter or toy-scale artifact concerns.

It makes no physical robustness claim, no physical metric claim, no compact dimension claim, no identity proof, and no Bridge confirmation.

## 19. Hypothese

If WIFM01 behavior remains stable under curated diagnostic weight and scale perturbations, this would support the methodological usefulness of circular/torus-aware fingerprint metrics in the toy setting.

This remains a hypothesis only.

## 20. Offene Lücke

- no runner yet
- no config yet
- no run output yet
- no sensitivity result yet
- no real data
- no broad control set
- no adversarial case expansion yet
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
- sweep variants are diagnostic choices, not physical parameters

## 21. Claim Boundary

- sensitivity sweep specification only
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

## 22. Next-step recommendation

Recommended next step:

`QSB-ST-COMP01-WIFM01B Minimal Metric Sensitivity Sweep Config + Runner Implementation`

Purpose:

- create explicit sensitivity config
- implement curated variants
- run WIFM01-like toy cases across weight/scale variants
- produce stability summaries
- no physical claims

## 23. Files created / checked

This task creates only:

- `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_SPEC.md`

Checked WIFM01 docs:

- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_RUNNER_SPEC.md`
- `docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md`

Checked WIFM01 config/runner:

- `data/qsb_st_comp01_wifm01_minimal_metric_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01_minimal_metric.py`

Checked WIFM01 outputs:

- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/pair_metric_comparison.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/case_family_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/metric_component_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/naive_vs_circular_phase_summary.csv`
