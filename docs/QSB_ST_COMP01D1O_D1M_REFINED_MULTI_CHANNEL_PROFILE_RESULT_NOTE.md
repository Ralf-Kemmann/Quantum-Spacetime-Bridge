# QSB-ST COMP01-D1o D1m Refined Multi-Channel Profile — Result Note

## 1. Purpose

This result note documents the D1o refined D1m metadata runner output.

D1o refines output semantics and metadata only. It does not modify original D1m outputs, does not rerun D1m, and does not create validation of a physical model or diagnostic specificity.

This is synthetic diagnostic documentation. It does not start Mastermind, Knuth, manifold search, role-permutation diagnostics, or new physics claims.

## 2. Inputs inspected

D1o specification/config/runner inspected:

- `docs/QSB_ST_COMP01D1O_D1M_RUNNER_REFINEMENT_SPECIFICATION.md`
- `data/qsb_st_comp01d1o_d1m_refined_multi_channel_profile_config.yaml`
- `scripts/run_qsb_st_comp01d1o_d1m_refined_multi_channel_profile.py`

D1m/D1n context documents inspected:

- `docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RESULT_NOTE.md`

D1o output artifacts inspected:

- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/summary.json`
- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/readout.md`
- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/profile_case_summary.csv`
- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/channel_summary.csv`
- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/warning_taxonomy_summary.csv`
- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/dominance_summary.csv`
- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/refinement_comparison_summary.csv`
- `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/resolved_config.json`

All expected D1o output artifacts were present and readable. No D1o rerun was needed.

## 3. Method summary

The D1o runner reads the original D1m outputs and the D1n audit outputs. It appends refined metadata fields to D1m profile, channel, and warning outputs, then writes D1o `summary.json`, `readout.md`, refined profile/channel/warning CSVs, `dominance_summary.csv`, `refinement_comparison_summary.csv`, and `resolved_config.json`.

D1o preserves old D1m outputs and old D1m profile decision labels. Mastermind, Knuth, and manifold status remain `parked_not_implemented`.

## 4. Befund

Confirmed D1o summary values:

```yaml
block_id: QSB-ST-COMP01D1O
runner_refinement_version: d1o_refined_semantics_v1
original_d1m_case_count: 9450
refined_case_count: 9450
original_d1m_joined_case_count: 9450
refined_joined_case_count: 9450
original_d1m_active_warning_count: 11
refined_active_warning_count: 11
original_profile_decision_label_counts:
  diagnostic_profile_candidate_with_warnings: 9450
refined_profile_decision_label_counts:
  diagnostic_profile_candidate_with_warnings: 9450
single_channel_dominance_threshold: 0.8
rows_crossing_dominance_threshold: 0
dominant_channel_distribution:
  phase_exposure: 9450
aggregate_broadcast_channel_count: 2
case_level_channel_count: 2
broadcast_warning_count: 9
case_level_warning_count: 2
family_level_warning_count: 0
channel_level_warning_count: 2
input_level_warning_count: 4
claim_boundary_warning_count: 1
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
mastermind_status: parked_not_implemented
knuth_status: parked_not_implemented
manifold_status: parked_not_implemented
output_tracking_policy: keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default
```

D1o extended D1m output metadata and schema, but did not reduce warning load, did not change case count, and did not convert warning-qualified rows into clean candidates.

## 5. Refined profile-case result

The refined `profile_case_summary.csv` has 9450 rows. Original D1m fields are preserved, and D1o appended dominance, warning-origin, warning-granularity, and component-count metadata.

The `profile_decision_label` remains `diagnostic_profile_candidate_with_warnings`.

First-row example from the refined profile table:

```yaml
profile_decision_label: diagnostic_profile_candidate_with_warnings
dominant_channel_id: phase_exposure
dominant_channel_share: 0.271317829457
single_channel_dominance_threshold: 0.8
dominance_warning_reason: dominant_channel_share_below_threshold
profile_score_component_count: 5
aggregate_broadcast_component_count: 2
case_level_component_count: 3
runner_refinement_version: d1o_refined_semantics_v1
```

The row also contains `profile_warning_origin_summary`, `profile_warning_granularity_summary`, and `dominance_interpretation_note`. The interpretation note states that `dominant_channel_id` is descriptive and `single_channel_dominance_warning` is threshold-based.

This means `dominant_channel_id` can remain `phase_exposure` while `dominance_warning_reason` remains below threshold.

## 6. Warning-origin and granularity result

Confirmed `warning_origin_counts`:

```yaml
claim_boundary_guard: 1
d1m_case_or_family_logic: 2
d1m_input_join: 4
d1m_interpretation_policy: 4
d1m_output_warning: 1
inherited_d1l_global: 6
```

Confirmed `warning_granularity_counts`:

```yaml
case_level: 2
channel_level: 2
claim_boundary: 1
global_broadcast: 9
input_level: 4
```

D1o makes inherited/global warnings visible, separates case-level warnings from global broadcast warnings, and preserves the warning-qualified status rather than hiding warnings.

The refined `warning_taxonomy_summary.csv` has 18 rows and now includes:

- `warning_origin`
- `warning_granularity`
- `inherited_from`
- `broadcast_warning_flag`
- `interpretation_boundary_refined`
- `runner_refinement_version`

The aggregate counts remain:

```yaml
broadcast_warning_count: 9
case_level_warning_count: 2
```

## 7. Dominance result

Confirmed dominance values:

```yaml
dominant_channel_distribution:
  phase_exposure: 9450
rows_crossing_dominance_threshold: 0
single_channel_dominance_threshold: 0.8
```

The `dominance_summary.csv` has 8 rows. Dominance metadata is descriptive diagnostic metadata only.

Interpretation:

- `dominant_channel_id` identifies the largest numeric channel.
- `dominant_channel_share` quantifies its contribution.
- `single_channel_dominance_warning` is threshold-based.
- In D1o, no rows cross the dominance threshold.

This resolves the earlier reviewer-confusion risk: `phase_exposure` can be the dominant channel in 9450 rows without triggering a single-channel dominance warning.

## 8. Channel-semantics result

The refined `channel_summary.csv` has 10 rows and now includes:

- `score_granularity`
- `warning_granularity`
- `broadcast_warning_flag`
- `interpretation_role`
- `refinement_needed`
- `recommended_change`
- `aggregate_broadcast_score_flag`
- `runner_refinement_version`

Confirmed channel counts:

```yaml
aggregate_broadcast_channel_count: 2
case_level_channel_count: 2
```

Confirmed selected channel semantics:

- `phase_exposure`: `case_level`, `signal_channel`
- `component_ablation`: `aggregate_broadcast`, `construction_sensitivity_channel`
- `threshold_weight_robustness`: `aggregate_broadcast`, `robustness_channel`
- `channel_specific_separability`: `derived_summary`, `summary_channel`

D1o marks aggregate-broadcast-like channels explicitly and keeps derived summary channels from being read as independent evidence.

## 9. Comparison to original D1m

The `refinement_comparison_summary.csv` has 9 rows.

Confirmed comparison result:

- `case_count` unchanged
- `profile_decision_label_counts` unchanged
- `active_warning_count` unchanged
- `single_channel_dominance_warning` unchanged
- output schema extended
- `warning_origin` metadata added
- `warning_granularity` metadata added
- `dominance_share` metadata added
- `output_tracking_policy` added

The comparison tracks schema and metadata changes only. It does not claim stronger physical meaning or diagnostic specificity.

## 10. Output-tracking result

The output tracking policy remains:

`keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default`

D1o run outputs are under `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/` and are probably ignored by normal git status because of `runs/` ignore behavior.

Recommended repository behavior:

- track config, runner, plan/spec/result notes
- do not force-add full `runs/` by default
- use docs-side digest or selected forced summary/readout outputs only with explicit justification

## 11. Interpretation

D1o successfully refines D1m output metadata. It makes warning origin/granularity, broadcast status, dominance semantics, and aggregate/case-level channel origins explicit.

D1o raises auditability and reviewer readability while preserving D1m decisions and warning-qualified interpretation. It prepares a cleaner basis for future methodological comparison.

D1o does not validate physical phase, physical wavefunction, physical spacetime geometry, or Bridge confirmation. It does not establish diagnostic specificity, does not remove D1m warnings, and should not be treated as physical evidence.

## 12. Hypothese

D1o supports the working hypothesis that D1m can be made methodically clearer without changing its warning-qualified result, by exposing warning origin, warning granularity, broadcast status, component counts, and dominance semantics directly in the outputs.

## 13. Offene Lücke

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
- D1o refines metadata but does not validate the underlying diagnostic concept
- D1m warnings remain active
- D1o outputs are in `runs/` and may be ignored by normal git status
- Mastermind / Knuth / manifold search still parked

## 14. Claim Boundary

This is synthetic diagnostic metadata refinement only.

- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- no new score claim
- no conversion of warning-qualified rows into clean candidates
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- D1o does not modify original D1m outputs
- D1o does not rerun D1m
- Mastermind, Knuth, manifold, and role-permutation remain parked

The D1o result note documents metadata semantics. It is not a physical interpretation step.

## 15. Consequence for next step

Recommended next block:

`QSB-ST-COMP01-D1p D1o Refined Output Audit and Regression Check`

Purpose:

- verify that D1o preserved original D1m row counts and decision labels
- verify that warning-qualified rows remained warning-qualified
- compare D1m vs D1o output schemas
- check dominance share distributions
- check whether `rows_crossing_dominance_threshold` remains zero across relevant variants
- audit whether warning-origin counts per row are mapped as intended
- decide whether D1o refined outputs should remain untracked or receive a docs-side digest
- avoid physical claims

Mastermind, Knuth, and manifold search should remain parked.

## 16. Files created / checked

Created by this task:

- `docs/QSB_ST_COMP01D1O_D1M_REFINED_MULTI_CHANNEL_PROFILE_RESULT_NOTE.md`

Checked by this task:

- D1o specification, config, and runner
- D1n result note
- D1m result note
- D1o `summary.json`
- D1o `readout.md`
- D1o `profile_case_summary.csv`
- D1o `channel_summary.csv`
- D1o `warning_taxonomy_summary.csv`
- D1o `dominance_summary.csv`
- D1o `refinement_comparison_summary.csv`
- D1o `resolved_config.json`

The D1o run outputs already exist under `runs/QSB-ST-COMP01D1O/d1m_refined_multi_channel_profile_open/`. They are probably ignored by normal git status because of `runs/` ignore behavior.
