# QSB-ST-LIC01-I Tau/Epsilon Residual Control Warning Analysis Plan

**Block:** QSB-ST-LIC01-I / `tau_epsilon_residual_control_warning_analysis`  
**Previous status:** `LIC01_global_phase_invariant_probe_documented_specificity_still_open`  
**Target status:** `LIC01_residual_control_warning_analysis_planned_not_implemented`  
**Date:** 2026-05-19  
**Document type:** Plan only / no implementation  
**Claim level:** Synthetic diagnostic planning only; no physical time, proper time, Lorentz interval, spacetime, Bridge, real-data, or experiment claim.

---

## 1. Purpose

LIC01-I plans a residual-control warning analysis after the LIC01-H global-phase-invariant probe.

This is a plan only. It does not implement a runner, does not change data, and does not create new run outputs.

This plan explicitly excludes:

- no `D(A,B)` attachment
- no `S_rel2` construction
- no Lorentz interval
- no physical tau
- no new physical claim
- no specificity claim

The purpose is to separate the remaining warning controls instead of treating them as one undifferentiated warning class.

---

## 2. Current status anchor

Current status before LIC01-I:

```text
LIC01_global_phase_invariant_probe_documented_specificity_still_open
```

Current technical state:

- tau/epsilon Minimalrunner works
- Control extension works
- Specificity-Contrast layer works
- Observable / Normalization Audit works
- Global-Phase-Invariant Probe works
- `global_phase_warning_reduced = True`
- `global_phase_probe_established_specificity = False`
- specificity remains not established

Residual status labels from LIC01-H:

```text
random_phase: control_still_exceeds_reference_warning
amplitude_preserved_phase_randomized: control_still_exceeds_reference_warning
label_shuffle: control_still_exceeds_reference_warning
```

One subproblem was isolated: global phase sensitivity. The remaining problem is that residual controls are still too strong or too close to the structured reference.

---

## 3. Motivation after LIC01-H

LIC01-H reduced the `global_phase_shift` warning:

```text
global_phase_warning_reduced = True
```

But the overall specificity result remained open:

```text
global_phase_probe_established_specificity = False
```

The residual warning controls must now be analyzed separately. The next analysis should not collapse `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle` into a single warning bucket, because they may fail for different reasons.

---

## 4. Core question

After global-phase centering reduces the `global_phase_shift` warning, why do `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle` remain warning controls?

This is a diagnostic-method question only. No physical interpretation follows from any planned outcome.

---

## 5. Residual warning controls

Residual warning controls after LIC01-H:

```text
random_phase
amplitude_preserved_phase_randomized
label_shuffle
```

These controls should each be compared against the structured reference after global phase centering and also against each other.

The analysis should identify whether the residual warnings arise from one shared mechanism or from distinct failure modes.

---

## 6. Random-phase warning analysis

Possible causes for the `random_phase` warning:

- `rho_tau` may measure generic phase sensitivity
- random phase can generate strong response patterns in a small kernel
- the response may depend more on variance, amplitude, or support than on structured locality
- the warning may be seed- or sampling-dependent

Future implementation should inspect:

- pairwise response distribution
- rank overlap with the structured reference
- pattern correlation with the structured reference
- sensitivity to multiple random seeds if seed sweeps are added
- whether high-response pairs are stable or sampling artifacts

---

## 7. Amplitude-preserved phase-randomized warning analysis

Possible causes for the `amplitude_preserved_phase_randomized` warning:

- amplitude structure may carry most of the response signal
- phase organization may not be sufficiently separating
- the current score may respond to magnitude/support more than structured phase
- randomized phase may retain global or marginal structure that the observable still reads as strong

Future implementation should inspect:

- how much centered response remains when amplitudes are preserved
- whether response ranking tracks amplitude/support patterns
- whether phase-randomized response remains correlated with structured response
- whether separating magnitude-derived and phase-derived components reduces the warning

---

## 8. Label-shuffle warning analysis

Possible causes for the `label_shuffle` warning:

- the 8-node synthetic system may be too small
- source-target labels may not be stable enough
- the score may be distributional rather than identity- or structure-sensitive
- label shuffle may preserve too much kernel-level statistic
- small or symmetric systems may make rank tests unstable

Future implementation should inspect:

- rank stability under multiple label shuffles
- pairwise pattern correlation to the original structured response
- whether high-response pairs are identity-specific or distributional
- whether larger or less symmetric kernels reduce the warning

---

## 9. Cross-control comparison strategy

The residual controls should be compared not only to the structured reference but also to each other.

Required comparisons:

- `random_phase` vs `amplitude_preserved_phase_randomized`
- `random_phase` vs `label_shuffle`
- `amplitude_preserved_phase_randomized` vs `label_shuffle`
- each residual control vs structured reference after global phase centering

The goal is to distinguish whether all residual controls show the same problem or whether they represent separate mechanisms.

Recommended readouts:

- centered `rho_tau` mean and max
- centered `tau_rel` mean
- pairwise correlation to structured reference
- pairwise correlation between residual controls
- top-quartile rank overlap
- rank separation score
- residual warning type
- likely failure mode

---

## 10. Required outputs for future implementation

Future implementation should add these outputs:

```text
residual_control_warning_summary.csv
residual_control_pairwise_comparison.csv
residual_control_family_correlation.csv
residual_control_seed_sensitivity.csv
residual_control_label_stability.csv
```

Expected future row counts:

- `residual_control_warning_summary.csv`: 3 rows, one for each residual warning control
- `residual_control_pairwise_comparison.csv`: 3 residual controls x 64 pairs = 192 rows
- `residual_control_family_correlation.csv`: pairwise family comparisons among structured + 3 residual controls; minimum expected 6 rows
- `residual_control_seed_sensitivity.csv`: optional if multiple seeds are implemented later
- `residual_control_label_stability.csv`: optional if multiple label shuffles are implemented later

Optional files should still be parseable if generated.

---

## 11. Continuous field list

### 11.1 residual_control_warning_summary.csv

| field | type | description |
|---|---|---|
| control_family | string | Residual control family name. |
| pair_count | integer | Number of source-target pairs included for the control. |
| rho_tau_centered_mean | float | Mean centered `rho_tau` for the control. |
| rho_tau_centered_max | float | Maximum centered `rho_tau` for the control. |
| tau_rel_centered_mean | float | Mean centered diagnostic candidate for the control. |
| structured_reference_mean | float | Mean centered `rho_tau` for the structured reference. |
| mean_ratio_to_reference | float | Control mean divided by structured-reference mean with eta convention. |
| max_ratio_to_reference | float | Control max divided by structured-reference max with eta convention. |
| pairwise_pattern_correlation_to_reference | float or blank | Correlation of pairwise centered `rho_tau` pattern to structured reference. |
| rank_separation_score | float | Fraction or score measuring how often structured reference ranks above the control. |
| residual_warning_type | string | Machine-readable residual warning class. |
| likely_failure_mode | string | Conservative failure-mode hypothesis for this control. |
| recommended_next_probe | string | Suggested follow-up probe for this residual warning. |
| warning | string | Human-readable caution text. |

### 11.2 residual_control_pairwise_comparison.csv

| field | type | description |
|---|---|---|
| control_family | string | Residual control family name. |
| source_id | string | Source node identifier. |
| target_id | string | Target node identifier. |
| rho_tau_structured | float | Centered structured-reference `rho_tau` for the pair. |
| rho_tau_control | float | Centered control `rho_tau` for the pair. |
| rho_tau_delta | float | `rho_tau_structured - rho_tau_control`. |
| rho_tau_ratio | float | Control `rho_tau` divided by structured `rho_tau` with eta convention. |
| tau_rel_structured | float | Centered structured diagnostic candidate for the pair. |
| tau_rel_control | float | Centered control diagnostic candidate for the pair. |
| tau_rel_delta | float | `tau_rel_structured - tau_rel_control`. |
| pattern_status | string | Whether the pair is reference higher, control higher, or equal. |
| warning | string | Human-readable pairwise warning text if applicable. |

### 11.3 residual_control_family_correlation.csv

| field | type | description |
|---|---|---|
| family_a | string | First family in the comparison. |
| family_b | string | Second family in the comparison. |
| pair_count | integer | Number of pairs used in the correlation. |
| rho_tau_pattern_correlation | float or blank | Correlation between centered `rho_tau` pair patterns. |
| tau_rel_pattern_correlation | float or blank | Correlation between centered `tau_rel` pair patterns. |
| rank_overlap_top_quartile | float | Top-quartile pair-rank overlap between the two families. |
| interpretation_status | string | Machine-readable interpretation of similarity or separation. |
| warning | string | Human-readable warning text. |

### 11.4 residual_control_seed_sensitivity.csv

| field | type | description |
|---|---|---|
| control_family | string | Control family tested under seed variation. |
| seed | integer | Random seed used for this run. |
| rho_tau_mean | float | Mean centered `rho_tau` for the seed. |
| rho_tau_max | float | Maximum centered `rho_tau` for the seed. |
| rank_top_pair | string | `source_id->target_id` pair with highest centered `rho_tau`. |
| pattern_correlation_to_seed0 | float or blank | Pairwise pattern correlation relative to seed 0 baseline. |
| seed_sensitivity_status | string | Machine-readable seed-sensitivity result. |
| warning | string | Human-readable seed-sensitivity warning. |

### 11.5 residual_control_label_stability.csv

| field | type | description |
|---|---|---|
| shuffle_id | string | Label-shuffle identifier. |
| rho_tau_mean | float | Mean centered `rho_tau` for the shuffle. |
| rho_tau_max | float | Maximum centered `rho_tau` for the shuffle. |
| rank_top_pair | string | `source_id->target_id` pair with highest centered `rho_tau`. |
| pattern_correlation_to_original | float or blank | Pairwise pattern correlation to the unshuffled reference. |
| label_stability_status | string | Machine-readable label-stability result. |
| warning | string | Human-readable label-stability warning. |

---

## 12. Acceptance criteria for future implementation

Future implementation is accepted only if:

- runner compiles
- existing minimal outputs are preserved
- existing control outputs are preserved
- existing specificity outputs are preserved
- existing observable audit outputs are preserved
- existing global-phase probe outputs are preserved
- new residual-control outputs parse
- `residual_control_warning_summary.csv` contains exactly 3 rows
- `residual_control_pairwise_comparison.csv` contains 192 rows
- result explicitly keeps specificity false unless predefined criteria are met
- `readout.md` contains a Residual Control Warning Analysis section
- claim-risk grep returns only boundary contexts
- `git diff --check` passes
- output longer than 50 lines goes to `~/Downloads/Textfiles/`

The future implementation must not hide or demote residual warning rows.

---

## 13. Interpretation rules

Outcome A: `random_phase` remains strong, `amplitude_preserved_phase_randomized` remains strong, and `label_shuffle` remains strong.

Interpretation: the current observable or `rho_tau` may still measure generic perturbation or distributional structure.

Outcome B: `random_phase` weakens while `amplitude_preserved_phase_randomized` remains strong.

Interpretation: amplitude/support structure may dominate the response more than phase organization.

Outcome C: `amplitude_preserved_phase_randomized` weakens while `random_phase` remains strong.

Interpretation: the residual issue may come from random high-variance phase response or seed/sampling instability.

Outcome D: `label_shuffle` remains strong while phase controls weaken.

Interpretation: the diagnostic may be distributional or small-kernel ambiguous rather than source-target identity sensitive.

Outcome E: all residual controls separate clearly from the structured reference.

Interpretation: specificity may become supported only if strict predefined criteria are met, but no physical claim follows automatically.

In all cases, no physical claim is allowed.

---

## 14. Claim Boundary

`tau_rel_candidate is not physical time.`

`tau_rel_candidate is not proper time.`

`tau_rel_centered is a diagnostic probe value only.`

Residual control warning analysis is synthetic diagnostic work only.

No Lorentzian metric is derived.

No spacetime interval is constructed.

No D(A,B) is attached.

No S_rel2 is constructed.

No Bridge validation is claimed.

No real-data or experimental validation is claimed.

Specificity remains not established until shown by predefined controls.

---

## 15. Current status label

```text
LIC01_residual_control_warning_analysis_planned_not_implemented
```
