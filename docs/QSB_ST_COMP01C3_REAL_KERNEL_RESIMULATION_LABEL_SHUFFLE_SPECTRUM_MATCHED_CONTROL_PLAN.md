# QSB-ST-COMP01-C3 Real Kernel Resimulation Label-Shuffle and Spectrum-Matched Control Plan

## 1. Purpose

COMP01-C3 plans the next hard control step after COMP01-C2.

COMP01-C2 showed stable candidates against value-permutation `label_shuffle` controls. COMP01-C3 should test whether this stability also holds against kernel-level controls:

- real kernel resimulation `label_shuffle`
- spectrum-matched `label_shuffle`
- distribution-matched `label_shuffle`

The goal is to plan harder diagnostic controls for the two stable C2 candidate metrics without broadening the metric list and without moving into a new theory layer.

Not goals:

- implement a new theory layer,
- implement the complex trigonometric representation,
- model tau,
- attach D(A,B),
- construct S_rel2,
- validate a Bridge,
- claim specificity.

## 2. Current status anchor

Current status:

```text
COMP01C2_candidate_metric_inspection_result_documented_candidates_stable_specificity_not_established
```

Last commit anchor:

```text
4b1c839 Add QSB-ST COMP01C2 candidate metric inspection result note
```

COMP01-C2 finding:

Stable candidate metrics:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

Decision values for `sin_sin_overlap`:

- `candidate_signal_count = 20`
- `seed_count = 20`
- `candidate_signal_fraction = 1`
- `mean_rank_correlation = 0.00303938356164`
- `mean_top_quartile_overlap = 0.240625`
- `decision_status = strong_identity_sensitive_candidate_for_followup`

Decision values for `component_resolved_relative_phase_similarity`:

- `candidate_signal_count = 20`
- `seed_count = 20`
- `candidate_signal_fraction = 1`
- `mean_rank_correlation = 0.0243435549027`
- `mean_top_quartile_overlap = 0.240625`
- `decision_status = strong_identity_sensitive_candidate_for_followup`

But:

- `specificity_established = False`
- value-permutation controls are not real kernel resimulations
- the 8-node kernel remains small
- `real_imag_proxy` remains a diagnostic proxy

Relevant files:

- `docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_HARDER_LABEL_SHUFFLE_CONTROLS_PLAN.md`
- `docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md`
- `docs/QSB_ST_PSI_ADDITION_CURVE_ANALYSIS_LOCAL_LINEAR_FORM.md`
- `scripts/run_qsb_st_comp01c2_candidate_metric_inspection.py`
- `scripts/run_qsb_st_comp01c_identity_sensitive_component_contrast.py`
- `scripts/run_qsb_st_comp01b_component_resolved_compatibility.py`
- `scripts/run_qsb_st_comp01_correlation_compatibility_scanner.py`

Relevant run outputs:

- `runs/QSB-ST-COMP01C2/candidate_metric_harder_label_shuffle_open/`
- `runs/QSB-ST-COMP01C/identity_sensitive_component_contrast_open/`
- `runs/QSB-ST-COMP01B/component_resolved_compatibility_open/`

## 3. Motivation after COMP01-C2

COMP01-C2 was a smoke test with a stronger pair-identity disturbance, but it was not a real kernel control.

The two candidates are interesting enough for harder tests.

COMP01-C3 should move from:

```text
value-level permutation controls
```

to:

```text
kernel-level resimulation controls
```

This is necessary because value-permutation preserves value distributions and breaks pair identity, but it does not test whether the metrics remain stable when genuinely new control kernels or fingerprints are constructed.

## 4. Candidate metrics carried forward

Primary Candidates:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

Secondary comparison metrics, context only:

- `cos_cos_overlap`
- `component_resolved_local_pattern_correlation`
- `component_asymmetry_delta`

Not primary:

- `component_balance_ratio`
- `cos_sin_cross_overlap`
- `sin_cos_cross_overlap`

Rationale:

- only `sin_sin_overlap` and `component_resolved_relative_phase_similarity` were C2-stable Primary Candidates,
- COMP01-C3 should not become broad,
- Secondary metrics may help detect false positives or behavior of neighboring metrics.

## 5. Why C2 is not enough

COMP01-C2 controls:

- preserve the existing `label_shuffle` value distribution,
- break pair identity by value permutation,
- test seed stability across deterministic shuffles.

But COMP01-C2 cannot show:

- whether a newly generated `label_shuffle` kernel has the same behavior,
- whether spectrum, distribution, or amplitude structure is controlled at the kernel or fingerprint level,
- whether candidates benefit from the existing COMP01-B `label_shuffle` value distribution,
- whether candidates are robust against true kernel-level controls.

Therefore COMP01-C3 must plan real control families at kernel / fingerprint level.

## 6. Real kernel resimulation label_shuffle controls

### 6.1 true_label_shuffle_kernel_resimulation

Idea:

- start from the same synthetic COMP01 / LIC01 basis,
- generate a true label permutation on kernel / node level for each seed,
- recompute fingerprints and COMP01-B / COMP01-C2 relevant metrics,
- do not merely permute existing metric values.

Goal:

- test whether the candidates remain stable under newly simulated `label_shuffle` kernels.

Minimal smoke:

- `seed_count = 20`
- seeds `2000` through `2019`
- `pair_count = 64`
- Primary Candidates only
- Secondary context optional

### 6.2 paired_structured_vs_resimulated_label_shuffle

For each seed:

- the structured reference remains fixed or is reconstructed with the same seed protocol,
- the `label_shuffle` kernel is generated in a seed-dependent way,
- pair identities are matched,
- rank / top-quartile / delta metrics are computed as in COMP01-C2.

The implementation must document whether the structured reference is fixed or seed-resimulated.

Preferred minimal block:

```text
structured reference fixed
```

### 6.3 seed logging

Every seed must document:

- seed,
- permutation mapping checksum,
- control_family,
- control_mode,
- component_split_mode,
- metric list,
- row counts.

## 7. Spectrum-/distribution-matched control ideas

### 7.1 distribution_matched_label_shuffle

Control preserves:

- marginal value distribution of the metric,
- optionally mean / standard deviation / quantiles.

Control breaks:

- pair identity,
- rank identity.

Goal:

- test whether a candidate only reads value distribution.

### 7.2 spectrum_matched_label_shuffle

Control preserves simple spectral statistics of a kernel / similarity object:

- eigenvalue spectrum approximately preserved,
- trace / Frobenius norm preserved,
- optionally sorted eigenvalue profile preserved.

Control breaks:

- source-target pair identity,
- local pair ranking,
- top-pair identities.

Goal:

- test whether a candidate only reads spectral or coarse matrix structure.

### 7.3 degree_or_strength_matched_control

If a graph-like interpretation is available, preserve approximately:

- node strength,
- row sum,
- column sum.

Break:

- pair identity.

Goal:

- test whether a candidate only reads row / column strength.

### 7.4 phase_randomized_resimulation

Later control type:

- randomize phases,
- preserve amplitudes.

Goal:

- test whether the relative phase-pattern candidate is robust or phase-dependent.

This should be recorded as a follow-up control idea, not forced into the C3 minimal block.

## 8. Proposed minimal C3 control families

Minimal COMP01-C3 should stay small.

Plan exactly these three control families:

1. `true_label_shuffle_kernel_resimulation`

Primary smoke control.

2. `distribution_matched_label_shuffle`

Use if it is possible from output matrices without major extra complexity.

3. `spectrum_matched_label_shuffle`

Initially planned as an optional / feasibility-gated control.

A later C3 minimal implementation may start with:

- `true_label_shuffle_kernel_resimulation` only

and keep spectrum/distribution matched controls as plan or feasibility entries if full implementation would become too broad.

## 9. Proposed output files

Plan only three main outputs:

- `real_kernel_label_shuffle_seed_summary.csv`
- `spectrum_distribution_matched_control_summary.csv`
- `candidate_metric_control_decision.csv`

Optional allowed outputs:

- `summary.json`
- `readout.md`
- `config_resolved.json`

No further outputs should be produced in the first COMP01-C3 minimal block.

Expected future row counts:

`real_kernel_label_shuffle_seed_summary.csv`:

- primary metrics x seeds
- 2 metrics x 20 seeds = 40 rows

`spectrum_distribution_matched_control_summary.csv`:

- one row per metric per control family,
- minimal planned: 2 metrics x 2 control families = 4 rows,
- if only feasibility entries are written, status must be `not_run_feasibility_only`.

`candidate_metric_control_decision.csv`:

- one row per primary metric,
- 2 rows.

## 10. Continuous field list

For `real_kernel_label_shuffle_seed_summary.csv`:

| Field name | Type | Description |
|---|---:|---|
| `metric_name` | string | Primary candidate metric name. |
| `control_family` | string | Control family, expected `true_label_shuffle_kernel_resimulation` for the smoke block. |
| `control_mode` | string | Detailed mode for the kernel-level shuffle. |
| `shuffle_seed` | integer | Deterministic seed used for the control. |
| `permutation_checksum` | string | Stable checksum or summary of the permutation mapping. |
| `component_split_mode` | string | Component split mode, expected `real_imag_proxy`. |
| `pair_count` | integer | Number of matched source-target pairs. |
| `mean_structured` | float | Mean structured metric value. |
| `mean_control` | float | Mean control metric value. |
| `mean_abs_delta` | float | Mean absolute structured-control pairwise delta. |
| `rank_correlation` | float/null | Pearson correlation on descending value ranks. |
| `top_quartile_overlap` | float | Shared top-quartile pair fraction. |
| `identity_sensitive_signal` | boolean | Whether the seed passes candidate signal logic. |
| `candidate_signal_status` | string | Seed-level candidate status. |
| `warning` | string | Empty or semicolon-separated warning labels. |

For `spectrum_distribution_matched_control_summary.csv`:

| Field name | Type | Description |
|---|---:|---|
| `metric_name` | string | Primary candidate metric name. |
| `control_family` | string | `distribution_matched_label_shuffle` or `spectrum_matched_label_shuffle`. |
| `control_mode` | string | Detailed matching / feasibility mode. |
| `feasibility_status` | string | Whether the control was feasible in the minimal input basis. |
| `run_status` | string | Run state, including `not_run_feasibility_only` if applicable. |
| `matched_property` | string | Distributional, spectral, or strength property being matched. |
| `mean_abs_delta` | float/null | Mean absolute delta if run. |
| `rank_correlation` | float/null | Rank correlation if run. |
| `top_quartile_overlap` | float/null | Top-quartile overlap if run. |
| `candidate_signal_status` | string | Control-level candidate status. |
| `warning` | string | Empty or semicolon-separated warning labels. |

For `candidate_metric_control_decision.csv`:

| Field name | Type | Description |
|---|---:|---|
| `metric_name` | string | Primary candidate metric name. |
| `tested_control_families` | string | Semicolon-separated tested control families. |
| `stable_control_families` | string | Semicolon-separated controls where candidate remains stable. |
| `failed_control_families` | string | Semicolon-separated controls where candidate fails or mimics. |
| `candidate_signal_fraction_true_label_shuffle` | float | Candidate seed fraction for true label-shuffle kernel resimulation. |
| `mean_rank_correlation_true_label_shuffle` | float/null | Mean rank correlation for true label-shuffle kernel resimulation. |
| `mean_top_quartile_overlap_true_label_shuffle` | float | Mean top-quartile overlap for true label-shuffle kernel resimulation. |
| `spectrum_distribution_status` | string | Feasibility and result summary for distribution/spectrum controls. |
| `decision_status` | string | Final metric decision status. |
| `recommended_followup` | string | Suggested next diagnostic action. |
| `specificity_status` | string | Always `specificity_not_established` in C3 minimal block. |
| `warning` | string | Empty or semicolon-separated warning labels. |

## 11. Minimal computation rules

Rules for future implementation:

- do not overwrite existing LIC01 outputs,
- do not overwrite existing COMP01 outputs,
- do not overwrite existing COMP01-B outputs,
- do not overwrite existing COMP01-C outputs,
- do not overwrite existing COMP01-C2 outputs,
- write new outputs only in `runs/QSB-ST-COMP01C3/real_kernel_resimulation_controls_open/`,
- focus only on the two Primary Candidates,
- keep `component_split_mode = real_imag_proxy` unless C3 is explicitly reformulated in a complex-trigonometric representation,
- treat `real_imag_proxy` as a diagnostic proxy,
- `specificity_established` remains false,
- new kernel-level shuffles must be seed-logged,
- permutation mapping or checksum must be documented,
- define thresholds before the run,
- do not tune thresholds after seeing the result.

Minimal future smoke:

- `seeds = 20`
- `shuffle_seeds = 2000..2019`
- primary metrics = 2
- `pair_count = 64`
- first control mode: `true_label_shuffle_kernel_resimulation`

## 12. Decision logic

For `true_label_shuffle_kernel_resimulation`, a metric remains a Candidate only if:

```text
candidate_signal_fraction >= 0.6
AND mean_rank_correlation < 0.5
AND mean_top_quartile_overlap <= 0.5
```

Strong candidate only if:

```text
candidate_signal_fraction >= 0.8
AND mean_rank_correlation < 0.3
AND mean_top_quartile_overlap <= 0.35
```

Mimic warning if:

```text
mean_rank_correlation >= 0.8
AND mean_top_quartile_overlap >= 0.75
```

Decision status vocabulary:

- `strong_candidate_survives_true_label_shuffle`
- `candidate_survives_true_label_shuffle`
- `candidate_fails_true_label_shuffle`
- `label_shuffle_mimic_warning`
- `inconclusive_control_result`

`specificity_status` is always:

```text
specificity_not_established
```

Only if later blocks separate multiple hard control families may a stronger diagnostic-specificity-candidate status be planned. It must not be claimed in the C3 minimal block.

## 13. Interpretation rules

Outcome A:

Both candidates survive `true_label_shuffle_kernel_resimulation`.

Interpretation:

- C2 stability was not only a value-permutation artifact.
- No specificity claim follows.

Outcome B:

Only `component_resolved_relative_phase_similarity` survives.

Interpretation:

- relative phase-pattern compatibility becomes the primary follow-up candidate.

Outcome C:

Only `sin_sin_overlap` survives.

Interpretation:

- the sine-like proxy remains a candidate, but `real_imag_proxy` must be checked especially critically.

Outcome D:

Both candidates fail against true `label_shuffle` resimulation.

Interpretation:

- C2 movement was likely a value-permutation / ranking artifact.

Outcome E:

Candidates survive true `label_shuffle` but fail spectrum-matched control.

Interpretation:

- a candidate may read coarse spectral or distributional structure rather than identity-sensitive structure.

Outcome F:

Candidates survive multiple control families.

Interpretation:

- further diagnostic follow-up is justified,
- still no physical validation follows.

## 14. Acceptance criteria for future implementation

Future implementation is accepted only if:

- new COMP01-C3 script is additive,
- existing LIC01 outputs are not rewritten,
- existing COMP01 outputs are not rewritten,
- existing COMP01-B outputs are not rewritten,
- existing COMP01-C outputs are not rewritten,
- existing COMP01-C2 outputs are not rewritten,
- candidate metrics are exactly documented,
- kernel-level shuffle logic is deterministic and seed-logged,
- output row counts match the plan,
- `component_split_mode` is reported,
- permutation checksum or mapping summary is reported,
- `specificity_established` remains false,
- readout contains true `label_shuffle` resimulation summary,
- claim-risk grep returns no forbidden claims,
- `git diff --check` passes,
- output over 50 lines goes to `~/Downloads/Textfiles/`,
- no D(A,B), S_rel2, tau model, or interval construction is introduced.

## 15. What this block must not do

COMP01-C3 must not do the following:

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
- no retroactive change of COMP01-C2 result,
- no dropping `label_shuffle` because it is inconvenient,
- no claiming specificity from C3-Minimalblock,
- no claiming physical sine/cosine components from `real_imag_proxy`,
- no claiming complex trigonometric representation has already been implemented.

## 16. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- real_imag_proxy is a diagnostic component split, not a physical derivation.
- Component-resolved psi channels are diagnostic decomposition channels, not physical observables by themselves.
- Identity-sensitive contrasts are diagnostic control checks, not physical observables by themselves.
- Kernel-level label_shuffle controls are diagnostic control families, not physical control families.
- Spectrum-/distribution-matched controls are methodological null controls, not physical validation tests.
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-C3 does not attach D(A,B).
- COMP01-C3 does not construct S_rel2.
- COMP01-C3 does not derive a Lorentzian metric.
- COMP01-C3 does not validate a physical Bridge.
- COMP01-C3 does not establish diagnostic specificity yet.
- This is synthetic diagnostic planning only.

## 17. Current status label

```text
COMP01C3_real_kernel_resimulation_label_shuffle_spectrum_matched_controls_planned
```
