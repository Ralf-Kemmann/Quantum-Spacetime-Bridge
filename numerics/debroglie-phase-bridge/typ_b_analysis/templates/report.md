# M.3.9x.3g.a — Type-B Exclusion Test / Null-Model Control

## 1. Run metadata

- **Block ID:** `M.3.9x.3g.a`
- **Run ID:** `{{ run_id }}`
- **Run status:** `{{ run_status }}`
- **Date:** `{{ run_date }}`
- **Feature space version:** `{{ feature_space_version }}`
- **Decision rule version:** `{{ decision_rule_version }}`
- **Scaling method:** `{{ scaling_method }}`
- **Distance metric:** `{{ distance_metric }}`
- **Resampling scheme:** `{{ resampling_scheme }}`
- **n_resamples:** `{{ n_resamples }}`
- **Random seed:** `{{ random_seed }}`

## 2. Test question

This block tests whether the current diagnostic apparatus produces Type-B-like path structure
also in explicitly non-Type-B control models.

**Core question:**  
> Does the current analysis pipeline reproduce stable Type-B-like path patterns in realistic
non-Type-B controls?

## 3. Working hypotheses

### H1 — Type-B exclusion hypothesis
Type-B-like structure is not generated arbitrarily.  
Explicit non-Type-B controls should **not** reproduce stable FSW/AO-analogous path structure.

### H0 — residual-class hypothesis
Type B is not a coherent class but a residual catch-all space.  
Under the same diagnostic apparatus, suitable control models may reproduce similar Type-B-like patterns.

## 4. Inputs used

### 4.1 Original reference data
- **Original features path:** `{{ original_features_path }}`
- **Input manifest path:** `{{ input_manifest_path }}`
- **Original dataset count:** `{{ original_dataset_count }}`
- **Original row count:** `{{ original_row_count }}`

### 4.2 Original target groups
- **FSW labels:** `{{ original_fsw_labels }}`
- **AO labels:** `{{ original_ao_labels }}`

### 4.3 Enabled control families
{{#control_families}}
- **{{ id }}** — {{ description }}
  - expected_not_type_B: `{{ expected_not_type_B }}`
  - notes: {{ notes }}
{{/control_families}}

## 5. Preprocessing and analysis protocol

### 5.1 Feature space
- Feature columns:
{{#feature_columns}}
  - `{{ . }}`
{{/feature_columns}}

### 5.2 Preprocessing
- Missing value policy: `{{ missing_value_policy }}`
- Scaling reference: `{{ scaling_reference }}`
- Center: `{{ center }}`
- Scale: `{{ scale }}`
- Clip outliers: `{{ clip_outliers }}`

### 5.3 Metrics
Primary metrics:
{{#primary_metrics}}
- `{{ . }}`
{{/primary_metrics}}

Definitions:
- `pooled_intra_distance = mean(intra_FSW, intra_AO)`
- `separation_margin = mean_inter_distance - pooled_intra_distance`
- `separation_ratio = mean_inter_distance / pooled_intra_distance`

### 5.4 Assignment / stability
- Assignment method: `{{ assignment_method }}`
- CV scheme: `{{ cv_scheme }}`
- Resampling: `{{ resampling_scheme }}`

## 6. Quality checks

| Check | Status | Comment |
|---|---:|---|
| Minimum two enabled control families | `{{ qc_min_two_controls }}` | {{ qc_min_two_controls_comment }} |
| Identical preprocessing for original and controls | `{{ qc_identical_preprocessing }}` | {{ qc_identical_preprocessing_comment }} |
| Fixed feature space documented | `{{ qc_feature_space_documented }}` | {{ qc_feature_space_documented_comment }} |
| Resampling enabled | `{{ qc_resampling_enabled }}` | {{ qc_resampling_enabled_comment }} |
| Decision rules documented | `{{ qc_decision_rules_documented }}` | {{ qc_decision_rules_documented_comment }} |

## 7. Original reference metrics

| Metric | Value |
|---|---:|
| mean_intra_distance | {{ original_mean_intra_distance }} |
| mean_inter_distance | {{ original_mean_inter_distance }} |
| pooled_intra_distance | {{ original_pooled_intra_distance }} |
| separation_margin | {{ original_separation_margin }} |
| separation_ratio | {{ original_separation_ratio }} |
| stability_score | {{ original_stability_score }} |
| assignment_score | {{ original_assignment_score }} |

## 8. Control family results

### 8.1 Summary table

| Control family | Enabled | n_instances | n_rows | separation_margin_mean | separation_ratio_mean | stability_score_mean | assignment_score_mean | Type-B-like detected |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
{{#control_results}}
| {{ control_family }} | {{ enabled }} | {{ n_instances }} | {{ n_rows }} | {{ separation_margin_mean }} | {{ separation_ratio_mean }} | {{ stability_score_mean }} | {{ assignment_score_mean }} | {{ type_B_like_pattern_detected }} |
{{/control_results}}

### 8.2 Per-family interpretation

{{#control_results}}
#### {{ control_family }}
- **Interpretation:** {{ interpretation }}
- **mean_intra_distance:** {{ mean_intra_distance }}
- **mean_inter_distance:** {{ mean_inter_distance }}
- **pooled_intra_distance:** {{ pooled_intra_distance }}
- **separation_margin_mean:** {{ separation_margin_mean }}
- **separation_margin_ci:** {{ separation_margin_ci }}
- **separation_ratio_mean:** {{ separation_ratio_mean }}
- **stability_score_mean:** {{ stability_score_mean }}
- **stability_score_ci:** {{ stability_score_ci }}
- **assignment_score_mean:** {{ assignment_score_mean }}
- **Type-B-like pattern detected:** `{{ type_B_like_pattern_detected }}`

Warnings:
{{#warnings}}
- {{ . }}
{{/warnings}}
{{^warnings}}
- none
{{/warnings}}

{{/control_results}}

## 9. Aggregate comparison: originals vs controls

| Aggregate metric | Value |
|---|---:|
| original_separation_margin | {{ aggregate_original_separation_margin }} |
| original_stability_score | {{ aggregate_original_stability_score }} |
| original_assignment_score | {{ aggregate_original_assignment_score }} |
| control_typeB_like_fraction | {{ aggregate_control_typeB_like_fraction }} |
| original_vs_control_margin_delta | {{ aggregate_original_vs_control_margin_delta }} |

## 10. Decision trace

Thresholds used:
- min_stability_score_for_supported: `{{ thr_min_stability_score_for_supported }}`
- min_original_over_control_margin_delta: `{{ thr_min_original_over_control_margin_delta }}`
- max_control_typeB_like_fraction_for_supported: `{{ thr_max_control_typeB_like_fraction_for_supported }}`
- max_control_typeB_like_fraction_for_weak: `{{ thr_max_control_typeB_like_fraction_for_weak }}`

Condition flags:
- supported_conditions_met: `{{ supported_conditions_met }}`
- weak_conditions_met: `{{ weak_conditions_met }}`
- ambiguous_conditions_met: `{{ ambiguous_conditions_met }}`
- failed_conditions_met: `{{ failed_conditions_met }}`

## 11. Result label

**Result label:** `{{ result_label }}`

**Overall interpretation:**  
{{ overall_interpretation }}

## 12. Scientific interpretation

### 12.1 What is supported
{{ supported_points }}

### 12.2 What remains open
{{ open_points }}

### 12.3 What would count as a serious warning signal
{{ warning_signals }}

## 13. Limitations

- Control families used here do not exhaust all possible non-Type-B alternatives.
- Results depend on the current baseline feature space and decision rules.
- This block tests exclusion strength, not shared mechanism or shared trend.

Additional limitations:
{{#limitations}}
- {{ . }}
{{/limitations}}

## 14. Warnings and errors

### Warnings
{{#global_warnings}}
- {{ . }}
{{/global_warnings}}
{{^global_warnings}}
- none
{{/global_warnings}}

### Errors
{{#global_errors}}
- {{ . }}
{{/global_errors}}
{{^global_errors}}
- none
{{/global_errors}}

## 15. Output files

- `summary.json`
- `diagnostics/`
- `resampling/`
- `{{ report_path }}`

## 16. Reproducibility

- **Seed list:** `{{ seed_list }}`
- **Python version:** `{{ python_version }}`
- **NumPy version:** `{{ numpy_version }}`
- **Pandas version:** `{{ pandas_version }}`
- **scikit-learn version:** `{{ sklearn_version }}`

## 17. Final conclusion

> {{ final_conclusion }}