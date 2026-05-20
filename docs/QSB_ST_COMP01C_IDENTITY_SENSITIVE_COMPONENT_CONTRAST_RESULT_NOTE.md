# QSB-ST-COMP01-C Identity-Sensitive Component Contrast Result Note

## 1. Purpose

COMP01-C documents the first identity-sensitive component contrast against `label_shuffle`.

The goal was to:

- use existing COMP01-B outputs,
- compare `structured_local_phase_response` against `label_shuffle`,
- evaluate selected metrics pairwise,
- look beyond Family Means,
- check `pairwise_delta`, `rank_correlation`, and `top_quartile_overlap`,
- test whether `label_shuffle` truly mimics the structured pairs pairwise/rank-wise or breaks under identity-sensitive checks.

The goal was not to:

- model tau,
- attach D(A,B),
- construct S_rel2,
- claim a physical wavefunction,
- validate a Bridge,
- claim specificity.

## 2. Repo status anchor

Startstatus was clean.

Implementation commit anchor:

```text
083be93 Add QSB-ST COMP01C identity sensitive component contrast scanner
```

The scanner was committed and pushed before this result note.

Repo status after the scanner commit was clean:

```text
## main...origin/main
```

Status before this note:

```text
COMP01C_identity_sensitive_component_contrast_implemented_and_run_checked
```

Previous relevant status anchors:

- `LIC01_tau_epsilon_decision_status_after_J_documented`
- `COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_component_resolved_compatibility_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_real_imag_proxy_definition_documented_before_COMP01C`
- `COMP01C_identity_sensitive_component_contrast_planned`

## 3. Files involved

Script:

- `scripts/run_qsb_st_comp01c_identity_sensitive_component_contrast.py`

Input:

- `runs/QSB-ST-COMP01B/component_resolved_compatibility_open/component_compatibility_pairwise.csv`

Run output directory:

- `runs/QSB-ST-COMP01C/identity_sensitive_component_contrast_open/`

Outputs:

- `identity_component_pairwise_contrast.csv`
- `identity_component_rank_summary.csv`
- `identity_component_control_decision.csv`
- `summary.json`
- `readout.md`
- `config_resolved.json`

Result note:

- `docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_RESULT_NOTE.md`

Relevant context files:

- `docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_PLAN.md`
- `docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md`
- `docs/QSB_ST_PSI_ADDITION_CURVE_ANALYSIS_LOCAL_LINEAR_FORM.md`

## 4. COMP01-C scanner implementation

COMP01-C was implemented as an additive new scanner.

The LIC01, COMP01, and COMP01-B runners were not changed.

The existing COMP01-B pairwise output was used as input. The scanner focus was only:

```text
structured_local_phase_response vs label_shuffle
```

The component split mode was:

```text
component_split_mode = real_imag_proxy
```

`real_imag_proxy` is documented as a diagnostic proxy, not as a physical derivation.

Selected metrics:

- `component_asymmetry_delta`
- `component_balance_ratio`
- `cos_cos_overlap`
- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`
- `component_resolved_local_pattern_correlation`

Not used as decision metrics:

- `cos_sin_cross_overlap`
- `sin_cos_cross_overlap`

Computed quantities:

- `pairwise_delta`
- `abs_delta`
- `structured_rank`
- `label_shuffle_rank`
- `rank_delta`
- top-quartile membership
- `rank_correlation`
- `top_quartile_overlap`
- `identity_sensitive_signal`

No tau model was constructed.

No D(A,B) was attached.

No S_rel2 was constructed.

## 5. Acceptance summary

Acceptance checks passed:

- `py_compile` OK
- run OK
- summary keys OK
- CSV acceptance OK
- readout checks OK
- claim-risk grep: no matches
- `git diff --check`: OK

Status after acceptance showed only:

```text
?? scripts/run_qsb_st_comp01c_identity_sensitive_component_contrast.py
```

Commit after acceptance:

```text
083be93 Add QSB-ST COMP01C identity sensitive component contrast scanner
```

## 6. Output files

Row counts:

- `identity_component_pairwise_contrast.csv`: 384
- `identity_component_rank_summary.csv`: 6
- `identity_component_control_decision.csv`: 6

Summary values:

- `block`: `QSB-ST-COMP01C`
- `status`: `COMP01C_identity_sensitive_component_contrast_implemented_and_run_checked`
- `comparison_focus`: `structured_local_phase_response_vs_label_shuffle`
- `component_split_mode`: `real_imag_proxy`
- `pair_count`: 64
- `selected_metric_count`: 6
- `pairwise_contrast_row_count`: 384
- `rank_summary_row_count`: 6
- `control_decision_row_count`: 6
- `specificity_established`: False
- `tau_model_constructed`: False
- `D_AB_attached`: False
- `S_rel2_constructed`: False

## 7. Befund

COMP01-C is technically implemented and acceptance-checked.

The scanner produced:

- 384 pairwise contrast rows
- 6 rank summary rows
- 6 control decision rows

The `label_shuffle`-Bossgegner was not reproduced as a complete mimic warning in the focused comparison.

`identity_sensitive_candidate_metrics`:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

`label_shuffle_mimic_warning_metrics`:

- none / empty list

`inconclusive_metrics`:

- `component_asymmetry_delta`
- `cos_cos_overlap`
- `component_resolved_local_pattern_correlation`

Important:

- `specificity_established = False`
- no tau model
- no D(A,B)
- no S_rel2

## 8. Candidate movement

`sin_sin_overlap` shows identity-sensitive candidate movement against `label_shuffle`.

This could indicate that the sine-like / quadrature proxy channel carries more source-target information in this synthetic setup than Family Means made visible. This remains diagnostic and is not a physical sine-channel claim.

`component_resolved_relative_phase_similarity` shows identity-sensitive candidate movement against `label_shuffle`.

This fits the COMP01 idea conceptually, because relative phase / pattern matching may be more source-target-sensitive than pure magnitude/support values. This remains diagnostic and is not a physical phase proof.

`component_asymmetry_delta` is inconclusive.

Although it moved in COMP01-B, it does not clearly solve the `label_shuffle` problem here.

`cos_cos_overlap` is inconclusive.

The same-channel cos-like proxy is not the strongest identity-sensitive candidate in the COMP01-C minimal block.

`component_resolved_local_pattern_correlation` is inconclusive.

Local pattern correlation remains interesting, but it is not clearly `label_shuffle`-separating here.

`component_balance_ratio` did not emerge as a primary candidate in the COMP01-C summary.

It should not be overinterpreted.

## 9. Interpretation

COMP01-C is a focused step beyond COMP01-B because the `label_shuffle` question was no longer evaluated only through Family Means.

The main result is:

- two metrics show identity-sensitive candidate movement,
- `label_shuffle_mimic_warning_metrics` is empty,
- specificity is still not established.

Interpretation:

- the COMP01 / COMP01-B candidates are not completely dead against `label_shuffle`,
- the identity-sensitive evaluation was useful,
- the strongest next inspection targets are `sin_sin_overlap` and `component_resolved_relative_phase_similarity`.

Limits:

- this is only a synthetic minimal block,
- `real_imag_proxy` remains a proxy,
- the 8-node kernel remains small,
- no specificity claim follows.

Positive movement: yes.

Specificity established: no.

Tau model justified: no.

D(A,B) / S_rel2 step justified: no.

## 10. Hypothese

Possible synthetic diagnostic hypotheses:

- the sine-like / quadrature proxy channel could carry more identity-sensitive structure than the cos-like channel in the current synthetic setup,
- relative phase pattern similarity could be a more robust compatibility candidate than pure same-channel overlap metrics,
- Family Means can hide source-target differences; rank and top-quartile checks can make such differences visible,
- `label_shuffle` is not automatically fatal for all COMP01 candidates, but it remains a necessary hard control case,
- `real_imag_proxy` may be useful as a diagnostic split, but it must later be checked against a cleaner complex trigonometric form or a true A/B/cos/sin representation.

These hypotheses are synthetic diagnostic hypotheses, not physical claims.

## 11. Offene Lücke

Open gaps:

- no specificity established,
- only `label_shuffle` was tested in the focused minimal block,
- no spectrum-matched `label_shuffle`,
- no `feature_shuffle`,
- no covariance- or spectrum-matched MaxEnt null,
- 8-node kernel remains small,
- `real_imag_proxy` remains a proxy,
- no true complex trigonometric representation implemented,
- no true A/B/cos/sin reconstruction,
- no local A/Bk fingerprint metric implemented,
- no scaling to N=16 / N=32,
- no robustness check over multiple `label_shuffle` seeds,
- no tau model,
- no D(A,B),
- no S_rel2,
- no physical wavefunction,
- no real-data or experimental claim.

## 12. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- real_imag_proxy is a diagnostic component split, not a physical derivation.
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
- This is synthetic diagnostic work only.

## 13. Recommended next step

Recommended next step:

```text
QSB-ST-COMP01-C2 candidate metric inspection and harder label-shuffle control plan
```

Reasonable sequence:

1. Finish this result note.
2. Inspect candidate metrics:
   - `sin_sin_overlap`
   - `component_resolved_relative_phase_similarity`
3. Add harder controls:
   - multiple `label_shuffle` seeds
   - spectrum-matched `label_shuffle`
   - `feature_shuffle`
4. Only after that, consider a new theory-level or implementation-level step such as:
   - `QSB-ST-COMP01-D complex trigonometric representation and local-linear fingerprint plan`

Not recommended as the immediate next step:

- tau model
- D(A,B)
- S_rel2
- Lorentz interval
- Bridge validation

## 14. Current status label

```text
COMP01C_identity_sensitive_component_contrast_result_documented_candidates_observed_specificity_not_established
```
