# QSB-ST-COMP01-C3 Real Kernel Resimulation Label-Shuffle Result Note

## 1. Purpose

COMP01-C3 documents the first real kernel / node-level `label_shuffle` smoke test for the two COMP01-C2-stable candidate metrics.

The goal was to:

- test the C2-stable candidates more strictly,
- test real kernel / node-level label permutation controls,
- avoid only permuting existing `label_shuffle` values,
- check whether C2 stability also holds under a kernel-level control,
- document distribution-/spectrum-matched controls as feasibility `not_run`,
- avoid creating a new broad metric list,
- avoid simulating new physics,
- avoid claiming specificity.

The goal was not to:

- model tau,
- attach D(A,B),
- construct S_rel2,
- claim a physical wavefunction,
- create a physical control family,
- validate a Bridge,
- claim specificity.

## 2. Repo status anchor

Startstatus was clean.

Implementation commit anchor:

```text
a4cb1a6 Add QSB-ST COMP01C3 real kernel resimulation label shuffle scanner
```

The scanner was committed and pushed before this result note.

Repo status after the scanner commit was clean:

```text
## main...origin/main
```

Status before this note:

```text
COMP01C3_real_kernel_resimulation_label_shuffle_implemented_and_run_checked
```

Previous relevant status anchors:

- `LIC01_tau_epsilon_decision_status_after_J_documented`
- `COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_component_resolved_compatibility_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_real_imag_proxy_definition_documented_before_COMP01C`
- `COMP01C_identity_sensitive_component_contrast_result_documented_candidates_observed_specificity_not_established`
- `COMP01C2_candidate_metric_inspection_result_documented_candidates_stable_specificity_not_established`
- `COMP01C3_real_kernel_resimulation_label_shuffle_spectrum_matched_controls_planned`

## 3. Files involved

Script:

- `scripts/run_qsb_st_comp01c3_real_kernel_resimulation_label_shuffle.py`

Output directory:

- `runs/QSB-ST-COMP01C3/real_kernel_resimulation_controls_open/`

Outputs:

- `real_kernel_label_shuffle_seed_summary.csv`
- `control_family_feasibility_summary.csv`
- `candidate_metric_control_decision.csv`
- `summary.json`
- `readout.md`
- `config_resolved.json`

Result note:

- `docs/QSB_ST_COMP01C3_REAL_KERNEL_RESIMULATION_LABEL_SHUFFLE_RESULT_NOTE.md`

Relevant context files:

- `docs/QSB_ST_COMP01C3_REAL_KERNEL_RESIMULATION_LABEL_SHUFFLE_SPECTRUM_MATCHED_CONTROL_PLAN.md`
- `docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md`
- `docs/QSB_ST_PSI_ADDITION_CURVE_ANALYSIS_LOCAL_LINEAR_FORM.md`

## 4. COMP01-C3 scanner implementation

COMP01-C3 was implemented as an additive new scanner.

The LIC01, COMP01, COMP01-B, COMP01-C, and COMP01-C2 runners were not changed.

Control family:

```text
true_label_shuffle_kernel_resimulation
```

Control mode:

```text
kernel_node_label_permutation_fixed_structured_reference
```

Seeds:

```text
2000 through 2019
```

Run constants:

- `seed_count = 20`
- `pair_count = 64`
- `component_split_mode = real_imag_proxy`

`real_imag_proxy` is a diagnostic proxy, not a physical derivation.

Kernel-level `label_shuffle` controls are diagnostic control families, not physical control families.

`distribution_matched_label_shuffle` and `spectrum_matched_label_shuffle` were documented as `planned_not_run` / `not_run_feasibility_only`.

Primary candidate metrics:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

Computed quantities:

- `mean_abs_delta`
- `rank_correlation`
- `top_quartile_overlap`
- `identity_sensitive_signal`
- `candidate_signal_fraction`
- `stable_candidate_metrics`
- `failed_or_inconclusive_metrics`
- `label_shuffle_mimic_warning_metrics`

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
?? scripts/run_qsb_st_comp01c3_real_kernel_resimulation_label_shuffle.py
```

Commit after acceptance:

```text
a4cb1a6 Add QSB-ST COMP01C3 real kernel resimulation label shuffle scanner
```

## 6. Output files

Row counts:

- `real_kernel_label_shuffle_seed_summary.csv`: 40
- `control_family_feasibility_summary.csv`: 3
- `candidate_metric_control_decision.csv`: 2

Summary values:

- `block`: `QSB-ST-COMP01C3`
- `status`: `COMP01C3_real_kernel_resimulation_label_shuffle_implemented_and_run_checked`
- `comparison_focus`: `structured_local_phase_response_vs_true_label_shuffle_kernel_resimulation`
- `control_family`: `true_label_shuffle_kernel_resimulation`
- `control_mode`: `kernel_node_label_permutation_fixed_structured_reference`
- `component_split_mode`: `real_imag_proxy`
- `seed_count`: 20
- `shuffle_seeds`: [2000, ..., 2019]
- `pair_count`: 64
- `primary_metric_count`: 2
- `real_kernel_label_shuffle_seed_summary_row_count`: 40
- `control_family_feasibility_summary_row_count`: 3
- `candidate_metric_control_decision_row_count`: 2
- `specificity_established`: False
- `tau_model_constructed`: False
- `D_AB_attached`: False
- `S_rel2_constructed`: False

## 7. Befund

COMP01-C3 is technically implemented and acceptance-checked.

The scanner produced:

- 40 real-kernel `label_shuffle` seed summary rows
- 3 control family feasibility rows
- 2 candidate metric control decision rows

C3 finding:

`stable_candidate_metrics`:

- none / empty list

`failed_or_inconclusive_metrics`:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

`label_shuffle_mimic_warning_metrics`:

- none / empty list

Important:

- `specificity_established = False`
- no tau model
- no D(A,B)
- no S_rel2

## 8. Candidate confirmation status

`sin_sin_overlap` was stable in COMP01-C2 over 20 value-permutation `label_shuffle` controls.

It was not confirmed as a stable candidate in COMP01-C3 under `true_label_shuffle_kernel_resimulation`.

Status:

```text
failed_or_inconclusive under first kernel-level label_shuffle smoke test
```

Observed C3 decision values:

- `candidate_signal_count_true_label_shuffle = 12`
- `seed_count_true_label_shuffle = 20`
- `candidate_signal_fraction_true_label_shuffle = 0.6`
- `mean_rank_correlation_true_label_shuffle = 0.344295815404`
- `mean_top_quartile_overlap_true_label_shuffle = 0.5625`
- `decision_status = inconclusive_control_result`

This does not erase the C2 finding, but it prevents promotion. It is not a physical sine-channel claim.

`component_resolved_relative_phase_similarity` was stable in COMP01-C2 over 20 value-permutation `label_shuffle` controls.

It was not confirmed as a stable candidate in COMP01-C3 under `true_label_shuffle_kernel_resimulation`.

Status:

```text
failed_or_inconclusive under first kernel-level label_shuffle smoke test
```

Observed C3 decision values:

- `candidate_signal_count_true_label_shuffle = 12`
- `seed_count_true_label_shuffle = 20`
- `candidate_signal_fraction_true_label_shuffle = 0.6`
- `mean_rank_correlation_true_label_shuffle = 0.331325743665`
- `mean_top_quartile_overlap_true_label_shuffle = 0.5625`
- `decision_status = inconclusive_control_result`

Relative phase-pattern compatibility remains conceptually interesting, but it is not confirmed in C3. It is not a physical phase proof and not a physical time proof.

`label_shuffle_mimic_warning_metrics` is empty.

This means:

- the candidates were not classified as clear mimic warnings,
- they were also not confirmed as stable candidates,
- C3 is therefore a clarifying brake result, not a positive confirmation result.

## 9. Interpretation

COMP01-C3 provides an important methodological brake result.

COMP01-C2 showed:

- both candidates stable against deterministic value-permutation `label_shuffle` controls.

COMP01-C3 shows:

- both candidates do not survive the first real kernel-level `label_shuffle` smoke test as stable candidates.

Interpretation:

- C2 stability was not robust enough to promote the candidates,
- candidate movement may have been partly value-permutation / ranking / control-design dependent,
- COMP01-C3 prevents overclaiming,
- COMP01 remains a search path, but the current C2 candidate line must be downgraded or controlled again.

Positive movement in C2: yes.

Kernel-level confirmation in C3: no.

Specificity established: no.

Tau model justified: no.

D(A,B) / S_rel2 step justified: no.

## 10. Hypothese

Possible synthetic diagnostic hypotheses:

- the C2 candidates were sensitive to pair identity under value-permutation controls, but not robust under kernel-level label permutation,
- `sin_sin_overlap` and `component_resolved_relative_phase_similarity` may read differences visible in the existing COMP01-B `label_shuffle` value field, but those differences do not remain stable in a newly generated control kernel,
- `real_imag_proxy` may still be useful as a diagnostic split, but the current candidates must not be treated as reliable specificity markers,
- the next useful check is either the detailed analysis of why C3 did not confirm the C2 candidates or a methodological redesign toward complex trigonometric representation / true A/B/cos/sin coefficients,
- a negative C3 result is scientifically useful because it prevents premature promotion.

These hypotheses are synthetic diagnostic hypotheses, not physical claims.

## 11. Offene Lücke

Open gaps:

- no specificity established,
- C3 minimal block tested only `true_label_shuffle_kernel_resimulation`,
- `distribution_matched_label_shuffle` was documented only as `planned_not_run`,
- `spectrum_matched_label_shuffle` was documented only as `planned_not_run`,
- the exact cause of the C2 / C3 break is not yet analyzed,
- it is unclear whether the kernel-level permutation is too strict, too trivially isomorphic, or methodologically differently oriented,
- the 8-node kernel remains small,
- `real_imag_proxy` remains a proxy,
- no complex trigonometric representation implemented,
- no true A/B/cos/sin reconstruction,
- no local A/Bk fingerprint metric implemented,
- no scaling to N=16 / N=32,
- no real spectrum- or distribution-matched nulls,
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
- This is synthetic diagnostic work only.

## 13. Recommended next step

Recommended next step:

```text
QSB-ST-COMP01-C3A failure-mode analysis of C2/C3 divergence
```

Alternative later path:

```text
QSB-ST-COMP01-D complex trigonometric representation and local-linear fingerprint plan
```

Most useful sequence directly after COMP01-C3:

1. Finish this result note.
2. Run C3A Failure-Mode Analysis:
   - Why were C2 candidates value-permutation-stable but not C3-kernel-level stable?
   - Is the kernel-level permutation correctly defined?
   - Is it too strict, too isomorphic, or differently oriented?
   - Which rank / top-pair structures broke?
3. Then decide whether to:
   - redesign the candidate line,
   - plan a true complex-trig / A-B / cos-sin representation,
   - test larger kernels or other null families.

Not recommended as the immediate next step:

- tau model
- D(A,B)
- S_rel2
- Lorentz interval
- Bridge validation

## 14. Current status label

```text
COMP01C3_real_kernel_resimulation_label_shuffle_result_documented_candidates_not_confirmed_specificity_not_established
```
