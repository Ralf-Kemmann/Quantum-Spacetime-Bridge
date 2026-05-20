# QSB-ST-COMP01-C2 Candidate Metric Inspection and Harder Label-Shuffle Controls Plan

## 1. Purpose

COMP01-C2 is not a new broad scanner. It is a focused follow-up plan for the two COMP01-C candidate metrics:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

The goal is to:

- test the COMP01-C candidate movement more strictly,
- check stability against additional `label_shuffle` variants,
- prepare multiple `label_shuffle` seeds,
- test whether the observed movement is only a seed or ranking artifact,
- set hard limits before any next interpretation step.

The goal is not to:

- model tau,
- attach D(A,B),
- construct S_rel2,
- claim a physical wavefunction,
- implement a complex trigonometric representation,
- claim specificity,
- validate a Bridge.

## 2. Current status anchor

Current status:

```text
COMP01C_identity_sensitive_component_contrast_result_documented_candidates_observed_specificity_not_established
```

Last commit anchor:

```text
78c63b7 Add QSB-ST COMP01C identity sensitive component contrast result note
```

COMP01-C showed:

`identity_sensitive_candidate_metrics`:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

`label_shuffle_mimic_warning_metrics`:

- none / empty list

`inconclusive_metrics`:

- `component_asymmetry_delta`
- `cos_cos_overlap`
- `component_resolved_local_pattern_correlation`

`specificity_established = False`

COMP01-C was a focused minimal block:

- `structured_local_phase_response` vs `label_shuffle`
- 64 pairs
- 6 selected metrics
- 384 pairwise contrast rows
- 6 rank summary rows
- 6 decision rows

Relevant files:

- `docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_PLAN.md`
- `docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md`
- `docs/QSB_ST_PSI_ADDITION_CURVE_ANALYSIS_LOCAL_LINEAR_FORM.md`
- `scripts/run_qsb_st_comp01c_identity_sensitive_component_contrast.py`

Relevant run output:

- `runs/QSB-ST-COMP01C/identity_sensitive_component_contrast_open/`

Deep Research context suggests the following methodological tools:

- Kernel / Gram-matrix comparison,
- rank / top-k comparisons,
- graph / label permutation controls,
- null-model and specificity tests,
- caution with permutation tests because exchangeability is not automatic,
- no direct physical interpretation.

## 3. Motivation after COMP01-C

COMP01-C was positive enough not to stop, but not strong enough for claims.

The result says:

- `label_shuffle` is not trivially a complete mimic,
- two candidates move identity-sensitively,
- seed stability, harder controls, and null models are still missing.

Therefore COMP01-C2 should test whether the two candidates remain robust when `label_shuffle` is tested more systematically and more strictly than in the single focused COMP01-C comparison.

## 4. Candidate metrics carried forward

Primary Candidates:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

Secondary comparison metrics, only as context:

- `component_asymmetry_delta`
- `cos_cos_overlap`
- `component_resolved_local_pattern_correlation`

Not carried forward as primary metrics:

- `component_balance_ratio`
- `cos_sin_cross_overlap`
- `sin_cos_cross_overlap`

Rationale:

- `sin_sin_overlap` and `component_resolved_relative_phase_similarity` were the only `identity_sensitive_candidate_metrics` in COMP01-C.
- The other metrics may appear as control context, but they should not broaden the block.

## 5. What COMP01-C2 should test

COMP01-C2 should prepare tests for these questions:

1. Do the candidates remain stable over multiple `label_shuffle` seeds?
2. Are the rank / top-quartile shifts reproducible?
3. Are the top pairs stable or seed-dependent?
4. Is `sin_sin_overlap` really stronger than `cos_cos_overlap`, or was that a minimal-block artifact?
5. Does `component_resolved_relative_phase_similarity` remain interesting against harder shuffles?
6. Is the movement large enough to carry the metric forward as a candidate?
7. Are there signs of normalization or ranking artifacts?
8. Which harder null family is the next useful test?

## 6. Harder label_shuffle control ideas

### 6.1 multiple_label_shuffle_seeds

Use multiple independent `label_shuffle` realizations.

Goal:

- test whether identity-sensitive candidate movement is seed-stable.

Minimal seed plan:

- 20 seeds for smoke,
- 100 seeds for a more robust local check,
- 500+ seeds later only if needed.

### 6.2 spectrum_or_distribution_matched_label_shuffle

If possible from the available COMP01-B / COMP01-C data, create a `label_shuffle` control that preserves value distribution or a simple spectral statistic while breaking source-target identity.

This plan should not force this control yet if the available input basis is insufficient.

### 6.3 feature_shuffle_control

Later control type:

- shuffle values or channel components within defined constraints instead of only swapping labels.

Goal:

- separate label identity effects from feature or channel structure effects.

### 6.4 phase_randomized_control_reuse

COMP01 / COMP01-B already included `random_phase` and `amplitude_preserved_phase_randomized`.

COMP01-C2 should check whether the candidates should later also be evaluated against these families with rank / top-quartile checks.

The first C2 minimal block remains `label_shuffle`-focused.

### 6.5 matched_rank_null

Rank-based null:

- same value distribution,
- randomized pair identity,
- comparison through `rank_correlation` and `top_quartile_overlap`.

Goal:

- test whether candidates carry only distribution information or pair identity information.

## 7. Candidate metric inspection ideas

### 7.1 pairwise_distribution_inspection

For each Candidate Metric:

- `structured_value` distribution,
- `label_shuffle_value` distribution,
- `delta` distribution,
- `abs_delta` distribution,
- `signed_direction` counts.

### 7.2 rank_shift_inspection

For each Candidate Metric:

- `rank_correlation`,
- `rank_delta` distribution,
- largest rank shifts,
- `top_pair_structured`,
- `top_pair_label_shuffle`.

### 7.3 top_quartile_stability

For each Candidate Metric:

- `top_quartile_overlap`,
- top structured pairs,
- top `label_shuffle` pairs,
- persistent top pairs over seeds.

### 7.4 seed_stability_summary

Across multiple `label_shuffle` seeds:

- `candidate_signal_count`,
- `fraction_candidate_signal`,
- `mean_rank_correlation`,
- `std_rank_correlation`,
- `mean_top_quartile_overlap`,
- `std_top_quartile_overlap`.

### 7.5 metric_pair_comparison

Direct comparisons:

- `sin_sin_overlap` vs `cos_cos_overlap`,
- `component_resolved_relative_phase_similarity` vs `component_resolved_local_pattern_correlation`.

Goal:

- test whether the candidates are really stronger than nearby related metrics.

## 8. Proposed output files

Plan only three main outputs for the first COMP01-C2 minimal block:

- `candidate_metric_inspection_summary.csv`
- `harder_label_shuffle_seed_summary.csv`
- `candidate_metric_decision.csv`

Optional allowed outputs:

- `summary.json`
- `readout.md`
- `config_resolved.json`

No further outputs should be produced in the first COMP01-C2 minimal block.

Expected future row counts:

`candidate_metric_inspection_summary.csv`:

- one row per inspected metric per control mode,
- Primary Candidates plus optional secondary context,
- minimal: 2 metrics x 1 control mode = 2 rows,
- with secondary context: up to 5 rows.

`harder_label_shuffle_seed_summary.csv`:

- one row per metric per seed,
- smoke mode: 2 metrics x 20 seeds = 40 rows.

`candidate_metric_decision.csv`:

- one row per primary metric,
- 2 rows.

## 9. Continuous field list

For `candidate_metric_inspection_summary.csv`:

| Field name | Type | Description |
|---|---:|---|
| `metric_name` | string | Inspected metric name. |
| `control_mode` | string | Control family or null mode being compared. |
| `pair_count` | integer | Number of matched source-target pairs. |
| `mean_structured` | float | Mean structured value for the metric. |
| `mean_control` | float | Mean control value for the metric. |
| `mean_delta` | float | Mean of structured minus control pairwise deltas. |
| `mean_abs_delta` | float | Mean absolute pairwise delta. |
| `median_abs_delta` | float | Median absolute pairwise delta. |
| `max_abs_delta` | float | Maximum absolute pairwise delta. |
| `structured_greater_count` | integer | Count of pairs where structured value is greater than control. |
| `control_greater_count` | integer | Count of pairs where control value is greater than structured. |
| `near_equal_count` | integer | Count of pairs within near-equal tolerance. |
| `rank_correlation` | float/null | Pearson correlation on descending value ranks. |
| `top_quartile_overlap` | float | Shared fraction of top-quartile pairs. |
| `top_pair_structured` | string | Highest-ranked structured pair. |
| `top_pair_control` | string | Highest-ranked control pair. |
| `inspection_status` | string | Per-metric inspection status. |
| `warning` | string | Empty or semicolon-separated warning labels. |

For `harder_label_shuffle_seed_summary.csv`:

| Field name | Type | Description |
|---|---:|---|
| `metric_name` | string | Inspected metric name. |
| `control_mode` | string | Shuffle/null control mode. |
| `shuffle_seed` | integer | Logged deterministic shuffle seed. |
| `pair_count` | integer | Number of matched source-target pairs. |
| `mean_abs_delta` | float | Mean absolute pairwise delta for this seed. |
| `rank_correlation` | float/null | Pearson correlation on descending value ranks for this seed. |
| `top_quartile_overlap` | float | Shared fraction of top-quartile pairs for this seed. |
| `identity_sensitive_signal` | boolean | Whether this seed passes candidate signal logic. |
| `top_pair_structured` | string | Highest-ranked structured pair. |
| `top_pair_control` | string | Highest-ranked control pair. |
| `candidate_signal_status` | string | Seed-level candidate status. |
| `warning` | string | Empty or semicolon-separated warning labels. |

For `candidate_metric_decision.csv`:

| Field name | Type | Description |
|---|---:|---|
| `metric_name` | string | Primary candidate metric name. |
| `candidate_signal_count` | integer | Number of seeds that pass candidate signal logic. |
| `seed_count` | integer | Total number of evaluated seeds. |
| `candidate_signal_fraction` | float | Candidate signal count divided by seed count. |
| `mean_rank_correlation` | float/null | Mean rank correlation across seeds. |
| `std_rank_correlation` | float/null | Standard deviation of rank correlation across seeds. |
| `mean_top_quartile_overlap` | float | Mean top-quartile overlap across seeds. |
| `std_top_quartile_overlap` | float | Standard deviation of top-quartile overlap across seeds. |
| `mean_abs_delta_mean` | float | Mean of seed-level mean absolute deltas. |
| `decision_status` | string | Final candidate decision status. |
| `recommended_followup` | string | Suggested next diagnostic action. |
| `specificity_status` | string | Always `specificity_not_established`. |
| `warning` | string | Empty or semicolon-separated warning labels. |

## 10. Minimal computation rules

Rules for a future implementation:

- do not overwrite existing LIC01 outputs,
- do not overwrite existing COMP01 outputs,
- do not overwrite existing COMP01-B outputs,
- do not overwrite existing COMP01-C outputs,
- use existing COMP01-C outputs as input when possible,
- write only new COMP01-C2 outputs for multi-seed shuffle checks,
- focus first on `sin_sin_overlap` and `component_resolved_relative_phase_similarity`,
- keep `component_split_mode = real_imag_proxy`,
- treat `real_imag_proxy` as a diagnostic proxy,
- `specificity_established remains false`,
- define thresholds before the run,
- do not tune thresholds after seeing the result.

Minimal future smoke:

- seeds = 20,
- selected primary metrics = 2,
- pair_count = 64,
- compare structured values against generated `label_shuffle` variants,
- write outputs to `runs/QSB-ST-COMP01C2/candidate_metric_harder_label_shuffle_open/`.

## 11. Decision logic

A metric remains a candidate only if:

```text
candidate_signal_fraction >= 0.6
AND mean_rank_correlation < 0.5
AND mean_top_quartile_overlap <= 0.5
```

If:

```text
candidate_signal_fraction >= 0.8
AND mean_rank_correlation < 0.3
AND mean_top_quartile_overlap <= 0.35
```

then:

```text
strong_identity_sensitive_candidate_for_followup
```

If:

```text
mean_rank_correlation >= 0.8
AND mean_top_quartile_overlap >= 0.75
```

then:

```text
label_shuffle_mimic_warning
```

Otherwise:

```text
inconclusive_candidate
```

`specificity_status` is always:

```text
specificity_not_established
```

## 12. Interpretation rules

Outcome A:

`sin_sin_overlap` remains a stable candidate across many seeds.

Interpretation:

- sine-like / quadrature proxy may carry identity-sensitive diagnostic structure in this synthetic kernel.
- No physical sine-component claim follows.

Outcome B:

`component_resolved_relative_phase_similarity` remains a stable candidate.

Interpretation:

- relative phase-pattern compatibility may be a strong COMP01 candidate.
- No physical phase proof follows.

Outcome C:

Both candidates collapse across seeds.

Interpretation:

- COMP01-C movement was likely a seed/control artifact.

Outcome D:

A candidate survives naive `label_shuffle` but fails spectrum- or distribution-matched shuffle.

Interpretation:

- the metric may depend on distributional artifacts rather than identity-sensitive structure.

Outcome E:

A candidate survives multiple controls.

Interpretation:

- the candidate deserves a next diagnostic block,
- still no specificity claim follows until broader null-family separation is shown.

## 13. Acceptance criteria for future implementation

Future implementation is accepted only if:

- the new COMP01-C2 script is additive,
- existing LIC01 outputs are not rewritten,
- existing COMP01 outputs are not rewritten,
- existing COMP01-B outputs are not rewritten,
- existing COMP01-C outputs are not rewritten,
- Candidate metrics are exactly documented,
- multi-seed logic is deterministic and seed-logged,
- output row counts match the plan,
- `component_split_mode` is reported,
- `specificity_established` remains false,
- readout contains a candidate stability summary,
- claim-risk grep returns no forbidden claims,
- `git diff --check` passes,
- output over 50 lines goes to `~/Downloads/Textfiles/`,
- no D(A,B), S_rel2, tau model, or interval construction is introduced.

## 14. What this block must not do

COMP01-C2 must not do the following:

- no D(A,B),
- no S_rel2,
- no Lorentz interval,
- no physical time,
- no proper time,
- no physical wavefunction claim,
- no Bridge validation,
- no real-data validation,
- no experimental validation,
- no tau model fitting,
- no large output cascade,
- no retroactive change of COMP01-C result,
- no dropping `label_shuffle` because it is inconvenient,
- no claiming specificity from one seed,
- no claiming physical sine/cosine components from `real_imag_proxy`.

## 15. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- real_imag_proxy is a diagnostic component split, not a physical derivation.
- Component-resolved psi channels are diagnostic decomposition channels, not physical observables by themselves.
- Identity-sensitive contrasts are diagnostic control checks, not physical observables by themselves.
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-C2 does not attach D(A,B).
- COMP01-C2 does not construct S_rel2.
- COMP01-C2 does not derive a Lorentzian metric.
- COMP01-C2 does not validate a physical Bridge.
- COMP01-C2 does not establish diagnostic specificity yet.
- This is synthetic diagnostic planning only.

## 16. Current status label

```text
COMP01C2_candidate_metric_inspection_harder_label_shuffle_controls_planned
```
