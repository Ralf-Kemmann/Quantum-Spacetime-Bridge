# QSB-ST-COMP01-C Identity-Sensitive Component Contrast Plan

## 1. Purpose

COMP01-C does not plan a new broad scanner. It plans a targeted follow-up for the `label_shuffle` problem.

The goal is to:

- test moving COMP01-B candidates beyond family means,
- inspect source-target identity,
- inspect pairwise rank and top-pair stability,
- inspect local-neighborhood conditioning,
- decide whether `label_shuffle` only looks similar in family means or also imitates pairwise/rank structure.

This block does not aim to:

- model tau,
- interpret physical time,
- attach `D(A,B)`,
- construct `S_rel2`,
- claim a physical wavefunction,
- claim specificity.

## 2. Current status anchor

LIC01 is parked.

COMP01 showed first psi(i)-psi(j) candidate movement.

COMP01-B showed additional movement in component-resolved channels.

Diagnostic specificity is not established.

`label_shuffle` remains the main boss case.

Current status before COMP01-C:

`COMP01B_component_resolved_compatibility_result_documented_candidates_observed_specificity_not_established`

Previous relevant status anchors:

- `LIC01_tau_epsilon_decision_status_after_J_documented`
- `COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_component_resolved_compatibility_inspection_implemented_and_run_checked`

Relevant recent line:

- COMP01 correlation compatibility scanner concept
- COMP01 scanner implementation plan
- COMP01 minimal scanner implementation
- COMP01 scanner result note
- COMP01-B component resolved compatibility inspection plan
- COMP01-B component resolved compatibility scanner
- COMP01-B component resolved compatibility result note

COMP01-B findings:

- `component_split_mode = real_imag_proxy`
- `component_compatibility_pairwise.csv`: 320 rows
- `component_compatibility_family_summary.csv`: 5 rows
- `component_compatibility_control_contrast.csv`: 32 rows
- `specificity_established = False`
- `tau_model_constructed = False`
- `D_AB_attached = False`
- `S_rel2_constructed = False`

Moving candidates:

- `component_asymmetry_delta`
- `component_balance_ratio`
- `component_resolved_local_pattern_correlation`
- `component_resolved_relative_phase_similarity`
- `cos_cos_overlap`
- `sin_sin_overlap`

Problem:

- `label_shuffle` remains problematic for several metrics.
- Cross-channel overlaps are warning-heavy.
- `component_resolved_local_pattern_correlation` remains problematic against `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle`.
- `component_resolved_relative_phase_similarity` remains problematic against `global_phase_shift` and `label_shuffle`.
- `cos_cos_overlap` remains problematic against `global_phase_shift` and `label_shuffle`.
- `sin_sin_overlap` remains problematic against `label_shuffle`.

## 3. Motivation after COMP01-B

COMP01-B showed movement in same-channel metrics:

- `cos_cos_overlap`
- `sin_sin_overlap`

COMP01-B showed movement in component organization metrics:

- `component_balance_ratio`
- `component_asymmetry_delta`

COMP01-B showed movement in component-resolved pattern metrics:

- `component_resolved_relative_phase_similarity`
- `component_resolved_local_pattern_correlation`

But:

- `label_shuffle` remains problematic.
- Family mean alone can lose source-target identity.
- A label shuffle can preserve global distributions even when pair identities are destroyed.
- Therefore COMP01-C should not primarily invent new metrics. It should evaluate the existing candidates in an identity-sensitive way.

## 4. Core question

Can identity-sensitive component contrasts distinguish structured pairs from label-shuffled controls when family means remain near-equal?

Koennen identity-sensitive Komponenten-Kontraste strukturierte Paare von `label_shuffle` Controls unterscheiden, wenn Family Means nahe gleich bleiben?

## 5. Why label_shuffle is the main target

`label_shuffle` is critical because it tests whether the scanner reads source-target structure or only distribution-like patterns.

If `label_shuffle` remains near-equal, this may mean:

- the metric is not identity-sensitive,
- the 8-node kernel is too small or too symmetric,
- family means hide pairwise differences,
- source-target orientation is missing,
- local neighborhood information is missing.

Therefore `label_shuffle` is not a nuisance side effect. It is a central specificity test.

## 6. Candidate metrics to carry forward

No broad list should be added.

Primary candidates:

- `component_asymmetry_delta`
- `component_balance_ratio`
- `cos_cos_overlap`
- `sin_sin_overlap`

Secondary diagnostic candidates:

- `component_resolved_relative_phase_similarity`
- `component_resolved_local_pattern_correlation`

Diagnostic/control metrics only:

- `cos_sin_cross_overlap`
- `sin_cos_cross_overlap`

Rationale:

- Same-channel and component organization metrics showed candidate movement.
- Cross-channel metrics were warning-heavy and should be kept only as diagnostic controls.
- Phase-/pattern-sensitive values remain important, but must be checked identity-sensitively.

## 7. Identity-sensitive contrast ideas

1. `pairwise_delta_against_label_shuffle`

   For each pair `(i,j)`:

   ```text
   structured_metric(i,j) - label_shuffle_metric(i,j)
   ```

   Goal: test whether pairwise differences exist even when family means are near-equal.

2. `rank_stability_against_label_shuffle`

   Compare pair ranks by metric.

   Goal: if family means are equal but top pairs differ, the metric may still be identity-sensitive.

3. `top_quartile_overlap`

   Compare the top 25% pairs between structured and `label_shuffle`.

   Goal: low overlap would indicate identity-sensitive structure change.

4. `source_target_oriented_contrast`

   Inspect the metric separately for source->target and target->source or row/column-oriented fingerprints.

   Goal: test whether `label_shuffle` remains near-equal because orientation is missing.

5. `local_neighborhood_conditioned_contrast`

   Condition pair values on local neighborhood / row-column fingerprint context.

   Goal: test whether local structural contexts break the `label_shuffle` similarity.

6. `signed_or_directional_component_delta`

   For `component_asymmetry_delta` and `component_balance_ratio`, inspect not only magnitude/mean but also sign, direction, rank, and pair identity.

   Goal: test whether means are similar while direction patterns differ.

## 8. Proposed output files

Only three output files are planned:

- `identity_component_pairwise_contrast.csv`
- `identity_component_rank_summary.csv`
- `identity_component_control_decision.csv`

Optional allowed files:

- `summary.json`
- `readout.md`
- `config_resolved.json`

No further outputs should be produced in the first COMP01-C minimal block.

Expected future row counts:

- `identity_component_pairwise_contrast.csv`: `64 pairs x selected metrics`
- If 6 selected metrics: 384 rows
- `identity_component_rank_summary.csv`: one row per selected metric = 6 rows
- `identity_component_control_decision.csv`: one row per selected metric = 6 rows

Selected metrics:

- `component_asymmetry_delta`
- `component_balance_ratio`
- `cos_cos_overlap`
- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`
- `component_resolved_local_pattern_correlation`

Cross-channel metrics remain optional diagnostics and should not be mandatory in first minimal decision rows.

## 9. Continuous field list

Proposed future file: `identity_component_pairwise_contrast.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `metric_name` | string | Selected component metric. |
| `source_id` | string/integer | Source node or pair source identifier. |
| `target_id` | string/integer | Target node or pair target identifier. |
| `structured_value` | float/null | Metric value for `structured_local_phase_response`. |
| `label_shuffle_value` | float/null | Metric value for `label_shuffle`. |
| `delta` | float/null | `structured_value - label_shuffle_value`. |
| `abs_delta` | float/null | Absolute pairwise contrast magnitude. |
| `signed_direction` | string | Direction of the pairwise contrast. |
| `structured_rank` | integer/null | Pair rank within structured rows for this metric. |
| `label_shuffle_rank` | integer/null | Pair rank within label-shuffle rows for this metric. |
| `rank_delta` | integer/null | Difference between structured and label-shuffle ranks. |
| `structured_top_quartile` | boolean | Whether the pair is in the structured top quartile. |
| `label_shuffle_top_quartile` | boolean | Whether the pair is in the label-shuffle top quartile. |
| `pair_identity_status` | string | Pair identity contrast status. |
| `warning` | string | Warning for missing, tied, degenerate, or inconclusive values. |

Proposed future file: `identity_component_rank_summary.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `metric_name` | string | Selected component metric. |
| `pair_count` | integer | Number of source-target pairs compared. |
| `mean_abs_delta` | float/null | Mean absolute pairwise delta. |
| `median_abs_delta` | float/null | Median absolute pairwise delta. |
| `max_abs_delta` | float/null | Maximum absolute pairwise delta. |
| `rank_correlation` | float/null | Rank correlation, documented as Spearman or Pearson on ranks. |
| `top_quartile_overlap` | float/null | Share of common pairs in both top quartiles. |
| `top_pair_structured` | string | Top structured pair identifier. |
| `top_pair_label_shuffle` | string | Top label-shuffle pair identifier. |
| `identity_shift_status` | string | Whether pair identity/rank shift is observed. |
| `warning` | string | Warning for ties, degeneracy, or inconclusive statistics. |

Proposed future file: `identity_component_control_decision.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `metric_name` | string | Selected component metric. |
| `identity_sensitive_signal` | boolean/string | Predefined identity-sensitive signal result. |
| `rank_shift_status` | string | Rank correlation status. |
| `top_quartile_status` | string | Top-quartile overlap status. |
| `pairwise_delta_status` | string | Pairwise delta status. |
| `overall_label_shuffle_status` | string | Overall label-shuffle decision status. |
| `recommended_followup` | string | Focused follow-up recommendation for this metric. |
| `specificity_status` | string | Specificity status; conservative default remains not established. |
| `warning` | string | Warning or interpretation boundary. |

These field lists are planning targets only. They are not generated by this document.

## 10. Minimal computation rules

Future implementation rules:

- Do not overwrite existing LIC01, COMP01, or COMP01-B outputs.
- Use existing COMP01-B outputs as input if cleanly possible.
- Focus first on `structured_local_phase_response` vs `label_shuffle`.
- Compare pairwise `structured_value` and `label_shuffle_value` for selected metrics.
- Compute ranks per metric within structured and `label_shuffle`.
- Define top quartile as the top 25% of 64 pairs = 16 pairs.
- Define `top_quartile_overlap` as the share of common pairs in both top quartiles.
- Compute `rank_correlation`, for example Spearman or Pearson on ranks, and document which one is used.
- If family mean is near-equal but `rank_correlation` is low and `top_quartile_overlap` is low, an identity-sensitive signal may be possible.
- Do not choose thresholds after seeing results to make the result look better.
- Document all thresholds before use.
- `specificity_established` remains false unless very strict predefined criteria are met.
- For this plan, use the conservative rule: no specificity claim.

Proposed decision logic:

`identity_sensitive_signal = true` only if:

- `mean_abs_delta > small_delta_threshold`
- `rank_correlation < 0.5`
- `top_quartile_overlap <= 0.5`

Otherwise:

`identity_sensitive_signal = false` or `inconclusive`

No specificity claim follows from this decision alone.

## 11. Interpretation rules

Outcome A: Family means are near-equal, but `rank_correlation` is low and `top_quartile_overlap` is low.

Interpretation: The metric may carry pair-identity information hidden by family means.

Outcome B: Family means are near-equal, `rank_correlation` is high, and `top_quartile_overlap` is high.

Interpretation: `label_shuffle` truly mimics the structured metric pattern; the metric is not identity-sensitive enough.

Outcome C: `component_asymmetry_delta` shows rank or top-pair shifts.

Interpretation: Component organization may encode pair identity.

Outcome D: `cos_cos_overlap` or `sin_sin_overlap` shows identity-sensitive rank shifts.

Interpretation: Same-channel compatibility may carry source-target information.

Outcome E: All selected metrics show high rank correlation and high top-quartile overlap.

Interpretation: COMP01-B candidates do not solve the `label_shuffle` problem in the current kernel.

Always:

- No physical wavefunction claim.
- No tau claim.
- No `D(A,B)`.
- No `S_rel2`.
- No specificity claim unless strict controls separate.

## 12. Acceptance criteria for future implementation

Future implementation is accepted only if:

- The new COMP01-C script is additive.
- Existing LIC01 outputs are not rewritten.
- Existing COMP01 outputs are not rewritten.
- Existing COMP01-B outputs are not rewritten.
- `identity_component_pairwise_contrast.csv` parses.
- `identity_component_rank_summary.csv` parses.
- `identity_component_control_decision.csv` parses.
- All selected metrics are present.
- Pairwise rows cover all 64 source-target pairs per selected metric.
- Rank and top-quartile fields are present.
- `label_shuffle` is explicitly tested.
- Readout contains an `Identity-Sensitive Component Contrast` section.
- Claim-risk grep returns only boundary contexts.
- `git diff --check` passes.
- Output greater than 50 lines goes to `~/Downloads/Textfiles/`.
- No `D(A,B)`, `S_rel2`, tau model, or interval construction is introduced.

## 13. What this block must not do

- no `D(A,B)`
- no `S_rel2`
- no Lorentz interval
- no physical time
- no proper time
- no physical wavefunction claim
- no Bridge validation
- no real-data validation
- no experimental validation
- no tau model fitting
- no large output cascade
- no retroactive change of COMP01-B result
- no dropping `label_shuffle` because it is inconvenient

## 14. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- Component-resolved psi channels are diagnostic decomposition channels, not physical observables by themselves.
- Identity-sensitive contrasts are diagnostic control checks, not physical observables by themselves.
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-C does not attach D(A,B).
- COMP01-C does not construct S_rel2.
- COMP01-C does not derive a Lorentzian metric.
- COMP01-C does not validate a physical Bridge.
- COMP01-C does not establish diagnostic specificity yet.
- This is synthetic diagnostic planning only.

## 15. Current status label

`COMP01C_identity_sensitive_component_contrast_planned`
