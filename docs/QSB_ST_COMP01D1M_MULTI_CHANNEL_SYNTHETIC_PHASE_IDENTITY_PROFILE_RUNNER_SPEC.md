# QSB-ST COMP01-D1m Multi-Channel Synthetic Phase Identity Profile — Runner Specification

## 1. Purpose

This document specifies a future QSB-ST-COMP01-D1m runner for a compact multi-channel synthetic phase identity profile.

It does not implement the runner. It does not produce a config file. It does not write run artifacts. It translates the committed D1m plan into a technical runner specification covering input artifacts, required and optional columns, join rules, fallback behavior, channel computation, warning flags, output schemas, and acceptance checks.

The specification remains synthetic diagnostic only.

```yaml
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
```

## 2. Scope and non-goals

Scope:

- define input joins
- define profile channels
- define warning flags
- define output schemas
- define acceptance checks
- define cautious fallback behavior for missing optional inputs
- define machine-readable status and claim-boundary requirements

Non-goals:

- no runner is implemented in this task
- no new config file is produced
- no run artifacts are written
- no physical phase is introduced
- no physical manifold is introduced
- no physical wavefunction is introduced
- no Mastermind / Knuth / manifold search is started
- no role-permutation diagnostics are started
- no claim escalation is allowed

## 3. Source documents and run artifacts inspected

Inspected source documents:

- present: `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_PLAN.md`
- present: `docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE.md`
- present: `docs/QSB_ST_COMP01D1JKL_SYNTHETIC_PHASE_EXPOSURE_LEAKAGE_AUDIT_SYNTHESIS_NOTE.md`
- present: `docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_RESULT_NOTE.md`
- present: `docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_RESULT_NOTE.md`

Inspected summary artifacts:

- present: `runs/QSB-ST-COMP01D1J/explicit_phase_field_exposure_cyclic_recheck_open/summary.json`
- present: `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/summary.json`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/summary.json`

Inspected case-level and audit CSV artifacts:

- present: `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/leakage_taxonomy_summary.csv`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/construction_variant_summary.csv`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/component_ablation_summary.csv`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/shuffled_input_summary.csv`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/family_blind_summary.csv`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/threshold_weight_sweep_summary.csv`
- present: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/proxy_exposed_mismatch_localization.csv`
- present: `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/cyclic_region_case_summary.csv`
- present: `runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv`

Observed source-of-truth anchors:

- D1j: explicit emitted phase-like output fields were absent; proxy phase columns were present; explicit phase recheck was not possible.
- D1k: deterministic synthetic diagnostic phase-like fields were exposed; `phase_is_synthetic_diagnostic: true`; `phase_is_physical: false`; `specificity_established: false`.
- D1l: D1k was qualified by leakage and construction checks; direct-feature leakage, construction-feedback leakage, tautology, overclean result, construction dependence, and component-ablation sensitivity were active warning classes.

## 4. Input artifacts

Required for a full case-level D1m runner:

- D1m plan document: `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_PLAN.md`
- D1k exposed case profile table: `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv`
- D1l summary: `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/summary.json`
- D1l audit CSVs:
  - `leakage_taxonomy_summary.csv`
  - `construction_variant_summary.csv`
  - `component_ablation_summary.csv`
  - `shuffled_input_summary.csv`
  - `family_blind_summary.csv`
  - `threshold_weight_sweep_summary.csv`
  - `proxy_exposed_mismatch_localization.csv`

Optional but useful inputs:

- D1j summary and result note
- D1k summary and result note
- D1h cyclic region case summary
- D1f case profile summary

Fallback behavior:

- If a required case-level artifact is missing, the future runner must set `missing_required_input_warning: true` and produce only an input-incomplete profile if enough aggregate data remains.
- If an optional artifact is missing, the future runner must set `missing_optional_input_warning: true`, keep the related channel unavailable, and not infer missing values from unrelated tables.
- If a CSV is present but lacks a required key column, the future runner must set `input_join_warning: true`.
- If only aggregate summaries are available, the future runner may produce `channel_summary.csv` and `warning_taxonomy_summary.csv` but must not fabricate `profile_case_summary.csv` case rows.

## 5. Join keys and row alignment

Primary join key:

```text
case_id
```

Join rules:

- Join case-level D1k, D1h, D1f, and D1l mismatch-localization rows by `case_id`.
- Do not guess by row order unless a future config explicitly enables a traceable row-order fallback.
- Preserve all source case identifiers in output rows.
- If duplicate `case_id` values appear in a source table, set `input_join_warning: true` and write a duplicate-key count to `summary.json`.
- If `case_id` is missing in a table, set `input_join_warning: true`, continue only for aggregate-level channels when possible, and write a missing-join-key note to `readout.md`.

Family and variant alignment:

- Family identifiers include `family`, `control_family`, `decoy_family`, `null_family`, `kernel_size_label`, `profile_weight_set_id`, and `penalty_weight_set_id`.
- Variant identifiers include `variant_id`, `construction_variant_id`, `ablated_component`, `shuffled_component`, `blind_field_removed`, and `threshold_variant_id`.
- If family or variant identifiers are missing, fill with `unknown` only for reporting.
- Mark `missing_family_or_variant_warning: true` when `unknown` reporting labels are needed.
- Never use `unknown` labels as evidence for a diagnostic claim.

## 6. Required and optional input columns

Expected input-column mapping:

| field name | required/optional | expected type | source artifact | description | fallback if missing |
| --- | --- | --- | --- | --- | --- |
| case_id | required for case-level rows | string | D1k/D1h/D1f case tables, D1l mismatch table | Primary join key. | Mark `input_join_warning`; case-level profile unavailable for that table. |
| family | optional | string | Derived from control family or decoy/null labels | General reporting family. | Fill `unknown` for display and mark `missing_family_or_variant_warning`. |
| variant_id | optional | string | D1l audit variant tables | General variant identifier. | Fill `unknown` for display and mark `missing_family_or_variant_warning`. |
| cyclic_phase_distance | optional | float | D1h cyclic case table | Proxy cyclic phase distance. | Disable proxy-distance subfeatures. |
| cyclic_phase_source | optional | string | D1h cyclic case table or D1j summary | Phase source label, commonly `cyclic_phase_proxy`. | Record missing optional input. |
| phase_source_label | optional | string | D1k exposed case table or D1k summary | Synthetic phase source label. | Use summary-level label if available. |
| phase_exposure_mode | optional | string | D1k exposed case table or D1k summary | Phase exposure mode. | Use summary-level mode if available. |
| phase_is_synthetic_diagnostic | required for phase channel | boolean | D1k exposed case table or D1k summary | Confirms synthetic diagnostic phase status. | Set channel unavailable if absent. |
| phase_is_physical | required for claim boundary | boolean | D1k exposed case table or D1k summary | Must remain false. | Set `phase_physical_claim_warning` if true or ambiguous. |
| false_accept_warning_exposed | optional | boolean | D1k exposed case table | Exposed-phase false-accept flag. | Use aggregate D1k summary only. |
| stable_candidate_exposed | optional | boolean | D1k exposed case table | Exposed-phase stable candidate flag. | Use aggregate D1k summary only. |
| remaining_intrusion_warning | optional | boolean | D1k exposed case table or D1l audit tables | Remaining intrusion flag. | Disable case-level intrusion channel. |
| proxy_vs_exposed_phase_mismatch | optional | boolean | Derived from D1l mismatch table | Case-level proxy/exposed mismatch flag. | Use mismatch table counts only. |
| direct_feature_leakage_warning | optional | boolean | D1l summary or leakage taxonomy | Direct feature leakage warning. | Use false and mark missing optional input only if no D1l leakage data exists. |
| label_leakage_warning | optional | boolean | D1l summary or leakage taxonomy | Label leakage warning. | Use aggregate fallback if present. |
| proxy_leakage_warning | optional | boolean | D1l summary or leakage taxonomy | Proxy leakage warning. | Use aggregate fallback if present. |
| target_family_leakage_warning | optional | boolean | D1l summary or leakage taxonomy | Target-family leakage warning. | Use aggregate fallback if present. |
| threshold_leakage_warning | optional | boolean | D1l summary or threshold sweep | Threshold leakage warning. | Use aggregate fallback if present. |
| construction_feedback_leakage_warning | optional | boolean | D1l summary or leakage taxonomy | Construction-feedback caution. | Use aggregate fallback if present. |
| tautology_warning | optional | boolean | D1l summary | Tautology warning. | Use false only with missing warning flag. |
| overclean_result_warning | optional | boolean | D1l summary or threshold sweep | Overclean result warning. | Use aggregate fallback if present. |
| construction_dependence_warning | optional | boolean | D1l summary or construction variants | Construction dependence warning. | Use construction table fallback if present. |
| component_ablation_failure_warning | optional | boolean | D1l summary or ablation table | Component ablation failure warning. | Use ablation table fallback if present. |
| shuffled_input_failure_warning | optional | boolean | D1l summary or shuffled-input table | Shuffled-input warning. | Use shuffled table fallback if present. |
| family_blind_failure_warning | optional | boolean | D1l summary or family-blind table | Family-blind warning. | Use family-blind table fallback if present. |

If actual repo column names differ in a future implementation, the runner should use an explicit mapping section in config. It must not invent data to satisfy a missing column.

## 7. Channel computation specification

1. phase exposure channel
   - inputs: D1k exposed case table fields including `phase_source_label`, `phase_exposure_mode`, `phase_is_synthetic_diagnostic`, `phase_is_physical`, `exposed_phase_cyclic_distance`, and exposed false-accept/stable flags.
   - output fields: `phase_exposure_score`, `phase_is_synthetic_diagnostic`, `phase_is_physical`.
   - suggested calculation rule: normalize exposed phase availability, stable behavior, and mismatch context into a bounded diagnostic score.
   - warning condition: missing phase fields, `phase_is_physical` not false, overclean result, or construction dependence.
   - interpretation boundary: diagnostic synthetic phase only.

2. phase leakage channel
   - inputs: D1l summary plus `leakage_taxonomy_summary.csv`.
   - output fields: `phase_leakage_flag`, `phase_leakage_warning_count`.
   - suggested calculation rule: count active leakage warnings and carry their labels into case or aggregate rows.
   - warning condition: any active leakage warning, especially direct-feature or construction-feedback warnings.
   - interpretation boundary: leakage warnings qualify the profile; they do not erase technical phase exposure.

3. residual mimicry channel
   - inputs: D1f/D1h profile-distance, residual, duplicate, and mimicry fields where available.
   - output fields: `residual_mimicry_score`, `residual_mimicry_warning`.
   - suggested calculation rule: score low residual/profile distance under non-duplicate controls as mimicry risk.
   - warning condition: near-duplicate or null controls remain close on residual-like channels.
   - interpretation boundary: residual similarity is type-like similarity, not relational identity.

4. duplicate sanity channel
   - inputs: D1f duplicate sanity fields such as `exact_duplicate_sanity_passed`, plus family labels.
   - output fields: `duplicate_sanity_passed`, `duplicate_control_label`.
   - suggested calculation rule: preserve direct duplicate controls as a separate sanity channel.
   - warning condition: direct duplicates fail sanity or non-duplicates look duplicate-like.
   - interpretation boundary: duplicate sanity is a control check only.

5. near-duplicate control channel
   - inputs: D1h/D1f `decoy_family`, D1l mismatch localization, and exposed false-accept/stable flags.
   - output fields: `near_duplicate_intrusion_flag`, `near_duplicate_control_family`.
   - suggested calculation rule: flag simple near-duplicate and adversarial near-duplicate families when stable or intrusive behavior persists.
   - warning condition: near-duplicates intrude into candidate-like profile regions.
   - interpretation boundary: near-duplicate intrusion reports ambiguity.

6. component ablation channel
   - inputs: D1l `component_ablation_summary.csv`.
   - output fields: `component_ablation_stability_score`, `component_ablation_warning`.
   - suggested calculation rule: calculate the fraction of ablation variants that preserve acceptable behavior.
   - warning condition: required behavior collapses under removal of decision-driving components.
   - interpretation boundary: ablation sensitivity indicates construction dependence.

7. shuffled-input sanity channel
   - inputs: D1l `shuffled_input_summary.csv`.
   - output fields: `shuffled_input_survival_flag`, `shuffled_input_warning`.
   - suggested calculation rule: flag when shuffled variants survive too strongly.
   - warning condition: shuffled inputs preserve profile behavior.
   - interpretation boundary: shuffle survival is a leakage or construction-risk signal.

8. family-blind sanity channel
   - inputs: D1l `family_blind_summary.csv`.
   - output fields: `family_blind_survival_flag`, `family_blind_warning`.
   - suggested calculation rule: report whether family-blind variants retain behavior and whether family labels were used.
   - warning condition: family identity is required or removal causes unexplained behavior.
   - interpretation boundary: family-blind survival is interpreted together with leakage and ablation.

9. threshold-weight robustness channel
   - inputs: D1l `threshold_weight_sweep_summary.csv`.
   - output fields: `threshold_weight_stability_score`, `threshold_weight_warning`.
   - suggested calculation rule: summarize stability across threshold and weight variants.
   - warning condition: narrow parameter survival, instability, or too-clean behavior across many variants.
   - interpretation boundary: threshold robustness is still synthetic diagnostic.

10. channel-specific separability channel
    - inputs: all channel scores plus family labels.
    - output fields: `channel_specific_separability_score`, `dominant_channel_id`, `single_channel_dominance_warning`.
    - suggested calculation rule: compare per-channel separability by family and detect dominance share.
    - warning condition: one channel supplies most of the separation.
    - interpretation boundary: separability supports further diagnostic refinement only.

## 8. Warning logic

Mandatory warning flags:

- `input_join_warning`
- `missing_required_input_warning`
- `missing_optional_input_warning`
- `missing_family_or_variant_warning`
- `phase_physical_claim_warning`
- `single_channel_dominance_warning`
- `overclean_result_warning`
- `direct_feature_leakage_warning`
- `construction_feedback_leakage_warning`
- `tautology_warning`
- `construction_dependence_warning`
- `component_ablation_failure_warning`
- `shuffled_input_survival_warning`
- `family_blind_interpretation_warning`
- `near_duplicate_intrusion_warning`
- `residual_mimicry_warning`
- `threshold_weight_instability_warning`
- `profile_aggregate_untrusted_warning`

`profile_warning_count` is the count of active warning flags for a profile row, channel row, or aggregate summary.

Allowed `profile_decision_label` values:

- `diagnostic_profile_candidate`
- `diagnostic_profile_candidate_with_warnings`
- `untrusted_single_channel_profile`
- `input_incomplete_profile_only`
- `not_interpretable`

No label may imply physical identity, physical phase, or specificity.

Decision rules:

- Use `input_incomplete_profile_only` when required case-level input is missing but aggregate reporting is still possible.
- Use `not_interpretable` when joins fail and aggregate fallback is insufficient.
- Use `untrusted_single_channel_profile` when one channel dominates.
- Use `diagnostic_profile_candidate_with_warnings` when useful profile structure exists with active warnings.
- Use `diagnostic_profile_candidate` only when required inputs are complete and warning counts stay within a future documented tolerance.

## 9. Output artifacts and schemas

Future output directory:

```text
runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/
```

Future output artifacts:

- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/summary.json`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/readout.md`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/profile_case_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/channel_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/control_family_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/warning_taxonomy_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/resolved_config.json`

`profile_case_summary.csv` schema:

| field name | field type | description |
| --- | --- | --- |
| case_id | string | Case identifier joined by `case_id`. |
| family | string | Reporting family derived from control, decoy, or null labels. |
| variant_id | string | Profile or audit variant identifier. |
| phase_exposure_score | float | Bounded diagnostic phase exposure channel score. |
| phase_leakage_flag | boolean | True when leakage warnings affect the profile. |
| residual_mimicry_score | float | Residual-like mimicry risk score. |
| duplicate_sanity_passed | boolean | Direct duplicate sanity status. |
| near_duplicate_intrusion_flag | boolean | True when near-duplicate controls intrude. |
| component_ablation_stability_score | float | Stability across component ablation variants. |
| shuffled_input_survival_flag | boolean | True when shuffled inputs preserve the profile suspiciously. |
| family_blind_survival_flag | boolean | True when family-blind variants retain behavior. |
| threshold_weight_stability_score | float | Stability across threshold/weight variants. |
| channel_specific_separability_score | float | Separability score across channel/family views. |
| multi_channel_identity_profile_score | float | Guarded aggregate diagnostic profile score. |
| profile_warning_count | integer | Count of active warning flags. |
| profile_decision_label | string | Cautious profile decision label from the allowed set. |
| profile_decision_reason | string | Short reason for the profile decision label. |
| dominant_channel_id | string | Channel with largest contribution to separability. |
| single_channel_dominance_warning | boolean | True when a single channel dominates. |
| phase_is_physical | boolean | Always false for this synthetic diagnostic runner. |
| phase_is_synthetic_diagnostic | boolean | True when the phase exposure channel is available. |
| specificity_established | boolean | False unless changed by a future separately documented standard. |

`channel_summary.csv` schema:

| field name | field type | description |
| --- | --- | --- |
| channel_id | string | Stable channel identifier. |
| channel_name | string | Human-readable channel name. |
| case_count | integer | Number of cases represented by the channel. |
| available_input_count | integer | Number of available input fields or rows used. |
| missing_input_count | integer | Number of expected inputs missing for the channel. |
| mean_score | float | Mean channel score when numeric scores exist. |
| min_score | float | Minimum channel score when numeric scores exist. |
| max_score | float | Maximum channel score when numeric scores exist. |
| warning_count | integer | Count of active channel warnings. |
| dominance_share | float | Share of aggregate separation attributed to the channel. |
| interpretation_boundary | string | Boundary note for this channel. |

`control_family_summary.csv` schema:

| field name | field type | description |
| --- | --- | --- |
| control_family | string | Control, decoy, null, or reporting family. |
| case_count | integer | Number of cases in the family. |
| intrusion_count | integer | Number of intrusion or ambiguity flags in the family. |
| intrusion_rate | float | `intrusion_count / case_count` when defined. |
| mean_profile_score | float | Mean guarded profile score for the family. |
| warning_count | integer | Count of active warnings in the family. |
| profile_decision_label | string | Dominant or aggregate decision label for the family. |
| interpretation_boundary | string | Boundary note for this family summary. |

`warning_taxonomy_summary.csv` schema:

| field name | field type | description |
| --- | --- | --- |
| warning_id | string | Stable warning identifier. |
| warning_label | string | Human-readable warning label. |
| warning_scope | string | Case, channel, family, or aggregate warning scope. |
| active_count | integer | Number of active warning instances. |
| active_rate | float | `active_count / denominator` when defined. |
| severity_label | string | Cautious severity label such as info, caution, warning, or blocking. |
| interpretation_boundary | string | Boundary note for the warning. |

## 10. Summary.json schema

Future `summary.json` must include at least:

| field name | field type | description |
| --- | --- | --- |
| block_id | string | Expected value: `QSB-ST-COMP01D1M`. |
| created_at | string | ISO-8601 timestamp written by the future runner. |
| input_artifacts | object | Resolved input paths and availability status. |
| case_count | integer | Source case count when available. |
| joined_case_count | integer | Number of case rows successfully joined by `case_id`. |
| missing_required_input_warning | boolean | True when required input is unavailable. |
| missing_optional_input_warning | boolean | True when optional input is unavailable. |
| input_join_warning | boolean | True when joins are incomplete or unsafe. |
| specificity_established | boolean | Must remain false for this synthetic diagnostic profile unless a future standard changes it. |
| phase_is_physical | boolean | Must remain false. |
| phase_is_synthetic_diagnostic | boolean | Must remain true when phase exposure is included. |
| profile_channel_count | integer | Number of channels included. |
| active_warning_count | integer | Total active warning count. |
| single_channel_dominance_warning | boolean | True when one channel dominates. |
| profile_decision_label_counts | object | Counts of allowed `profile_decision_label` values. |
| mastermind_status | string | Expected value: `parked_not_implemented`. |
| knuth_status | string | Expected value: `parked_not_implemented`. |
| manifold_status | string | Expected value: `parked_not_implemented`. |
| runner_scope | string | Synthetic diagnostic multi-channel profile only. |
| claim_boundary | string | Defensive claim-boundary statement. |

## 11. Readout.md requirements

Future `readout.md` must include:

- Purpose
- Inputs
- Join status
- Channel summary
- Warning summary
- Befund
- Interpretation
- Hypothese
- Offene Lücke
- Claim Boundary
- Files created

If terminal review output would exceed about 50 lines, the future runner or review script should redirect long review output to `~/Downloads/Textfiles/` and print only the path plus line count.

The readout must explicitly state:

```yaml
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
```

## 12. Acceptance criteria

Acceptance criteria for a future D1m implementation:

- runner specification exists
- all required sections are present
- output schemas include field name, field type, description
- the runner remains unimplemented in this task
- no config file is produced in this task
- no run artifacts are written in this task
- no physical-model validation claim
- `specificity_established` remains false
- `phase_is_physical` remains false
- `phase_is_synthetic_diagnostic` remains true
- Mastermind/Knuth/manifold remain parked
- allowed `profile_decision_label` values are defensive
- `profile_warning_count` is defined
- `single_channel_dominance_warning` is mandatory
- `git diff --check` passes

## 13. Befund expected from the future runner

Planning-level expectation only:

- future runner should test whether a multi-channel profile is more robust than single-score behavior
- future runner should report warnings, not hide them
- future runner should allow failure and ambiguity as valid outcomes
- future runner should not treat clean results as automatically strong evidence
- future runner should report whether one channel dominates
- future runner should preserve case-level traceability when joins are complete

## 14. Interpretation rules

- If multiple channels agree and controls fail to mimic, say "supports further diagnostic refinement", not proof.
- If one channel dominates, the profile is untrusted or warning-qualified.
- If inputs are incomplete, label as `input_incomplete_profile_only`.
- If near-duplicates intrude, report ambiguity.
- If shuffled inputs survive, report leakage or construction risk.
- If family-blind checks survive, interpret together with leakage and ablation.
- If all results are too clean, trigger `overclean_result_warning`.
- Never interpret the profile as physical phase, physical wavefunction, physical spacetime, diagnostic specificity, or Bridge confirmation.

## 15. Hypothese

A multi-feature synthetic phase identity profile may be more robust than one `wave_identity_residual` or one exposed-phase score for distinguishing same-type but not-same relational wave cases.

This remains a synthetic diagnostic hypothesis. It requires hostile controls, channel-specific reporting, and single-channel dominance checks.

## 16. Offene Lücke

- no real data
- no validation of a physical model
- no diagnostic specificity
- no physical phase reconstruction
- no physical wavefunction
- no physical spacetime geometry
- no physical time
- no Lorentzian metric
- no Hilbert-space reconstruction
- no Pauli/spin-statistics claim
- no Bridge confirmation
- Mastermind / Knuth / manifold search still parked
- the runner is not implemented by this spec
- no output is generated by this spec

## 17. Claim Boundary

This is a synthetic diagnostic specification only.

The runner is not implemented by this document.

No new identity score is calculated.

No physical phase is introduced.

No physical manifold is introduced.

No physical model validation is claimed.

```yaml
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
```

Mastermind, Knuth, manifold, and role-permutation remain parked.

## 18. Implementation sketch

Future D1m runner should:

1. read a config
2. resolve input paths
3. validate required inputs
4. inspect available columns
5. join case-level tables by `case_id`
6. compute channel scores and warning flags
7. compute aggregate profile score only with dominance warnings
8. compute `channel_summary.csv`
9. compute `control_family_summary.csv`
10. compute `warning_taxonomy_summary.csv`
11. write `profile_case_summary.csv`
12. write `summary.json`
13. write `readout.md`
14. write `resolved_config.json`
15. print only a short terminal summary and redirect long review output to `~/Downloads/Textfiles/`

Do not implement this runner now.
