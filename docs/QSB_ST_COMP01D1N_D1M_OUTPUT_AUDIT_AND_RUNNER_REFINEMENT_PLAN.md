# QSB-ST COMP01-D1n D1m Output Audit and Runner Refinement — Plan

## 1. Purpose

D1n is a planning document for auditing D1m output semantics and preparing possible later runner refinement.

This plan does not implement anything. It creates no runner changes now, performs no rerun now, creates no new config now, and creates no new run outputs now.

D1n focuses on the D1m output layer: warning semantics, channel semantics, dominant-channel reporting, output tracking policy, and possible refinement targets. It is synthetic diagnostic planning only, not validation of a physical model.

## 2. Starting point from D1m

The D1m runner exists and is committed. The D1m result note documents the first runner output under:

`runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/`

Confirmed D1m values from the inspected outputs:

```yaml
case_count: 9450
joined_case_count: 9450
input_join_warning: false
missing_required_input_warning: false
missing_optional_input_warning: false
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
profile_channel_count: 10
active_warning_count: 11
single_channel_dominance_warning: false
profile_decision_label_counts:
  diagnostic_profile_candidate_with_warnings: 9450
```

All 9450 cases are warning-qualified. The D1m outputs show a complete join and no input warnings, but interpretation remains warning-bound.

Confirmed channel features:

- `phase_exposure` mean_score: 1
- `residual_mimicry` mean_score: 0.925767935149
- `component_ablation` mean_score: 0.428571428571
- `threshold_weight_robustness` mean_score: 0.52
- `channel_specific_separability` mean_score: 0.71858484093
- `phase_leakage` warning_count: 9450
- `near_duplicate_control` warning_count: 8505
- `family_blind_sanity` warning_count: 9450

Active warning set:

- `overclean_result_warning`
- `direct_feature_leakage_warning`
- `construction_feedback_leakage_warning`
- `tautology_warning`
- `construction_dependence_warning`
- `component_ablation_failure_warning`
- `family_blind_interpretation_warning`
- `near_duplicate_intrusion_warning`
- `residual_mimicry_warning`
- `threshold_weight_instability_warning`
- `profile_aggregate_untrusted_warning`

The `dominant_channel_id` can be `phase_exposure` while `single_channel_dominance_warning: false` remains true at summary level. This distinction is a central D1n audit target.

## 3. Audit questions

D1n should plan answers to these audit questions:

- Which warnings are inherited from D1l and which are produced by D1m scoring/reporting?
- Is warning load mainly global, case-level, family-level, or channel-level?
- Does phase exposure dominate reporting semantics without triggering single-channel dominance?
- Are near-duplicate and residual mimicry warnings too broad or properly scoped?
- Is family-blind survival being treated as warning, neutral information, or success?
- Are threshold-weight warnings interpretable or too coarse?
- Should run outputs be tracked with `git add -f` or remain reproducible from config plus runner?
- Does the runner need clearer summary fields to prevent reviewer confusion?

## 4. Warning-load decomposition plan

A future D1n audit should decompose warning load into these categories:

- inherited D1l global warnings
- D1m join/input warnings
- D1m channel-derived warnings
- D1m family/control warnings
- D1m aggregate/profile warnings

For each category, the future audit should count:

- `active_count`
- `affected_case_count`
- `affected_family_count`
- `channel_scope`
- `inherited_or_new`
- `severity_label`
- `interpretation_boundary`

The point is not to suppress warnings. The point is to identify whether the high D1m warning load reflects inherited leakage cautions, broad case broadcasts, family/control behavior, channel score semantics, or new D1m reporting choices.

## 5. Channel-semantics audit plan

The future audit should inspect all D1m channels:

- `phase_exposure`
- `phase_leakage`
- `residual_mimicry`
- `duplicate_sanity`
- `near_duplicate_control`
- `component_ablation`
- `shuffled_input_sanity`
- `family_blind_sanity`
- `threshold_weight_robustness`
- `channel_specific_separability`

For each channel, D1n should check:

- whether the score is case-level or aggregate broadcast
- whether `warning_count` means cases, aggregate inherited warning, or channel warning
- whether `mean_score` exists or is intentionally blank
- whether the channel should be interpreted as signal, qualifier, or control
- whether `interpretation_boundary` is sufficient

Current examples that need semantic clarification:

- `phase_leakage` has no mean score but has `warning_count: 9450`.
- `family_blind_sanity` has no mean score but has `warning_count: 9450`.
- `near_duplicate_control` has no mean score but has `warning_count: 8505`.
- `component_ablation` and `threshold_weight_robustness` appear as aggregate-derived numeric scores broadcast into the profile.

## 6. Dominant-channel versus single-channel-dominance clarification

D1n should explicitly separate these meanings:

- `dominant_channel_id` reports the largest contributing numeric channel per row.
- `single_channel_dominance_warning` reports whether one channel crosses a warning threshold.
- These are related but not identical.
- `phase_exposure` can be dominant without crossing the single-channel dominance threshold.

Future runner/readout fields may need to be clearer:

- `dominant_channel_id`
- `dominant_channel_share`
- `single_channel_dominance_threshold`
- `single_channel_dominance_warning`
- `dominance_interpretation_note`

This clarification prevents a reviewer from reading "phase exposure is the largest channel" as "the profile failed as a single-channel profile."

## 7. Run-output tracking decision

The D1m run outputs exist under `runs/` and may be ignored by normal git status because of project `runs/` behavior. The current normal `git status --short` does not list the D1m run output files.

Possible policies:

A. Do not track `runs/` outputs; keep them reproducible from config plus runner.

B. Track only `summary.json` and `readout.md` with `git add -f`.

C. Track the full D1m run output set with `git add -f`.

D. Track no outputs but create a docs-side output digest.

Conservative recommendation:

- keep config plus runner committed
- keep result note committed
- leave full `runs/` outputs untracked for now
- if public review needs outputs, create a small docs-side digest or explicitly force-add selected outputs later

This plan does not make the final repository policy decision.

## 8. Proposed refinement targets

Possible future refinements:

- add explicit `dominant_channel_share` to `profile_case_summary.csv`
- add `single_channel_dominance_threshold` to `summary.json`
- split global inherited warnings from case-derived warnings
- separate `family_blind_survival_flag` from family-blind warning semantics
- separate `residual_mimicry_score` availability from `residual_mimicry_warning`
- clarify `phase_leakage` as global qualifier if broadcast to all rows
- add `warning_origin` column to `warning_taxonomy_summary.csv`
- add `warning_granularity` column: global, channel, family, case
- add `output_tracking_policy` to `summary.json` and `readout.md`
- possibly add `profile_score_component_count` per row

These are refinement targets only. No D1m runner change is made by this plan.

## 9. Proposed audit outputs for a future D1n runner or review script

Potential future outputs:

- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/summary.json`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/readout.md`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/warning_origin_summary.csv`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/channel_semantics_audit.csv`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/dominance_semantics_audit.csv`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/output_tracking_policy.md`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/resolved_config.json`

Proposed `warning_origin_summary.csv` field list:

| field name | field type | field description |
| --- | --- | --- |
| `warning_id` | string | Stable warning identifier. |
| `warning_label` | string | Human-readable warning label. |
| `warning_origin` | string | Origin class, such as D1l inherited, D1m channel, D1m family, or D1m aggregate. |
| `warning_granularity` | string | Global, channel, family, or case granularity. |
| `active_count` | integer | Count of active warning records. |
| `affected_case_count` | integer | Number of affected case rows. |
| `affected_family_count` | integer | Number of affected control/family groups. |
| `inherited_from` | string | Prior block source if inherited. |
| `severity_label` | string | Defensive severity class, not a claim label. |
| `interpretation_boundary` | string | Boundary for interpreting this warning. |

Proposed `channel_semantics_audit.csv` field list:

| field name | field type | field description |
| --- | --- | --- |
| `channel_id` | string | Stable channel identifier. |
| `channel_name` | string | Human-readable channel name. |
| `score_granularity` | string | Case-level, aggregate broadcast, or absent. |
| `warning_granularity` | string | Case-level, family-level, channel-level, or global. |
| `mean_score_present` | boolean | Whether `mean_score` is populated. |
| `warning_count_interpretation` | string | Meaning of the channel warning count. |
| `broadcast_warning_flag` | boolean | Whether a global warning is broadcast to rows. |
| `interpretation_role` | string | Signal, qualifier, control, or bookkeeping. |
| `refinement_needed` | boolean | Whether a runner/readout refinement is recommended. |
| `recommended_change` | string | Proposed change. |

Proposed `dominance_semantics_audit.csv` field list:

| field name | field type | field description |
| --- | --- | --- |
| `dominance_field` | string | Dominance-related field name. |
| `current_meaning` | string | Current semantic meaning. |
| `possible_confusion` | string | Likely reviewer confusion point. |
| `recommended_clarification` | string | Suggested text or field clarification. |
| `runner_change_needed` | boolean | Whether a runner schema change is needed. |
| `readout_change_needed` | boolean | Whether readout wording should change. |

## 10. Acceptance criteria for the future audit

A future D1n audit should meet these criteria:

- existing D1m outputs are read, not rerun unless missing
- warning origins are categorized
- global-vs-case warning broadcast is explicit
- dominant-channel and dominance-warning semantics are separated
- output tracking policy is documented
- no physical-model validation claim
- specificity_established remains false
- phase_is_physical remains false
- phase_is_synthetic_diagnostic remains true
- Mastermind/Knuth/manifold remain parked

## 11. Befund expected from this plan

Planning-level only:

- D1n defines how to audit the D1m warning load.
- D1n defines how to clarify output semantics before modifying the runner.
- D1n does not decide physical interpretation.
- D1n does not implement runner changes.

## 12. Interpretation rules

- Warning-qualified output is not failure.
- High warning load is a diagnostic signal about method semantics and control sensitivity.
- Clean joins do not imply clean interpretation.
- Channel dominance reporting does not equal single-channel failure unless threshold is crossed.
- Family-blind survival must be interpreted together with leakage and ablation.
- No D1m/D1n result may be interpreted as physical phase, physical wavefunction, physical spacetime, diagnostic specificity, or Bridge confirmation.

## 13. Hypothese

The high D1m warning load may be decomposable into inherited D1l global warnings plus D1m scoring/reporting semantics.

A dedicated D1n audit may distinguish method-risk warnings from reporting-semantics warnings, enabling a more transparent D1m runner refinement.

## 14. Offene Lücke

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
- D1n is only a plan
- no D1n runner implemented
- no D1n outputs generated
- D1m outputs still warning-qualified
- Mastermind / Knuth / manifold search still parked

## 15. Claim Boundary

This is synthetic diagnostic planning only.

- no runner implemented
- no new scores calculated
- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- Mastermind, Knuth, manifold, and role-permutation remain parked

D1n is a semantics and refinement planning layer. It is not a physical interpretation step.

## 16. Next-step implementation sketch

A future D1n implementation should:

1. read D1m `summary.json`, `readout.md`, `profile_case_summary.csv`, `channel_summary.csv`, `control_family_summary.csv`, and `warning_taxonomy_summary.csv`
2. classify each warning by origin and granularity
3. audit channel summary fields for score/warning semantics
4. audit `dominant_channel_id` and `single_channel_dominance_warning` semantics
5. produce proposed refinement actions
6. document output tracking recommendation
7. write summary/readout/audit CSVs
8. not alter D1m outputs
9. not introduce physical claims
