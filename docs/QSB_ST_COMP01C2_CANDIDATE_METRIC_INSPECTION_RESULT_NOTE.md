# QSB-ST-COMP01-C2 Candidate Metric Inspection Result Note

## 1. Purpose

COMP01-C2 documents the first multi-seed candidate test for the two COMP01-C candidate metrics.

The goal was to:

- test the COMP01-C candidates more strictly,
- use existing COMP01-B outputs,
- use deterministic multi-seed value-permutation `label_shuffle` controls,
- check whether the candidates remain stable over 20 seeds,
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
88709b0 Add QSB-ST COMP01C2 candidate metric inspection scanner
```

The scanner was committed and pushed before this result note.

Repo status after the scanner commit was clean:

```text
## main...origin/main
```

Status before this note:

```text
COMP01C2_candidate_metric_inspection_implemented_and_run_checked
```

Previous relevant status anchors:

- `LIC01_tau_epsilon_decision_status_after_J_documented`
- `COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_component_resolved_compatibility_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_real_imag_proxy_definition_documented_before_COMP01C`
- `COMP01C_identity_sensitive_component_contrast_result_documented_candidates_observed_specificity_not_established`
- `COMP01C2_candidate_metric_inspection_harder_label_shuffle_controls_planned`

## 3. Files involved

Script:

- `scripts/run_qsb_st_comp01c2_candidate_metric_inspection.py`

Input:

- `runs/QSB-ST-COMP01B/component_resolved_compatibility_open/component_compatibility_pairwise.csv`

Output directory:

- `runs/QSB-ST-COMP01C2/candidate_metric_harder_label_shuffle_open/`

Outputs:

- `candidate_metric_inspection_summary.csv`
- `harder_label_shuffle_seed_summary.csv`
- `candidate_metric_decision.csv`
- `summary.json`
- `readout.md`
- `config_resolved.json`

Result note:

- `docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_RESULT_NOTE.md`

Relevant context files:

- `docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_HARDER_LABEL_SHUFFLE_CONTROLS_PLAN.md`
- `docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md`
- `docs/QSB_ST_PSI_ADDITION_CURVE_ANALYSIS_LOCAL_LINEAR_FORM.md`

## 4. COMP01-C2 scanner implementation

COMP01-C2 was implemented as an additive new scanner.

The LIC01, COMP01, COMP01-B, and COMP01-C runners were not changed.

The existing COMP01-B pairwise output was used as input.

Control mode:

```text
multi_seed_label_shuffle_value_permutation
```

Seeds:

```text
1000 through 1019
```

Run constants:

- `seed_count = 20`
- `pair_count = 64`
- `component_split_mode = real_imag_proxy`

`real_imag_proxy` is a diagnostic proxy, not a physical derivation.

Value-permutation `label_shuffle` controls preserve the existing `label_shuffle` value distribution and break pair identity.

This is a synthetic harder-control approximation, not a newly simulated physical control family.

Inspected metrics:

Primary candidate metrics:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

Secondary context metrics:

- `cos_cos_overlap`
- `component_resolved_local_pattern_correlation`
- `component_asymmetry_delta`

Decision rows were produced only for the two Primary Candidates.

Computed quantities:

- `mean_abs_delta`
- `rank_correlation`
- `top_quartile_overlap`
- `identity_sensitive_signal`
- `candidate_signal_fraction`
- `stable_candidate_metrics`
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
?? scripts/run_qsb_st_comp01c2_candidate_metric_inspection.py
```

Commit after acceptance:

```text
88709b0 Add QSB-ST COMP01C2 candidate metric inspection scanner
```

## 6. Output files

Row counts:

- `candidate_metric_inspection_summary.csv`: 5
- `harder_label_shuffle_seed_summary.csv`: 100
- `candidate_metric_decision.csv`: 2

Summary values:

- `block`: `QSB-ST-COMP01C2`
- `status`: `COMP01C2_candidate_metric_inspection_implemented_and_run_checked`
- `comparison_focus`: `structured_local_phase_response_vs_multi_seed_label_shuffle_value_permutation`
- `control_mode`: `multi_seed_label_shuffle_value_permutation`
- `component_split_mode`: `real_imag_proxy`
- `seed_count`: 20
- `shuffle_seeds`: [1000, ..., 1019]
- `pair_count`: 64
- `inspected_metric_count`: 5
- `primary_metric_count`: 2
- `candidate_metric_inspection_summary_row_count`: 5
- `harder_label_shuffle_seed_summary_row_count`: 100
- `candidate_metric_decision_row_count`: 2
- `specificity_established`: False
- `tau_model_constructed`: False
- `D_AB_attached`: False
- `S_rel2_constructed`: False

## 7. Befund

COMP01-C2 is technically implemented and acceptance-checked.

The scanner produced:

- 5 candidate metric inspection summary rows
- 100 harder `label_shuffle` seed summary rows
- 2 candidate metric decision rows

Stable candidate metrics:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

Unstable or inconclusive metrics:

- none / empty list

`label_shuffle` mimic warning metrics:

- none / empty list

Important:

- `specificity_established = False`
- no tau model
- no D(A,B)
- no S_rel2

## 8. Candidate stability

`sin_sin_overlap` remained stable over 20 deterministic value-permutation `label_shuffle` seeds.

This strengthens the COMP01-C finding against a one-seed interpretation. It remains a diagnostic sine-like / quadrature-proxy finding. It is not a physical sine-channel claim.

Observed decision values:

- `candidate_signal_count = 20`
- `seed_count = 20`
- `candidate_signal_fraction = 1`
- `mean_rank_correlation = 0.00303938356164`
- `mean_top_quartile_overlap = 0.240625`
- `decision_status = strong_identity_sensitive_candidate_for_followup`

`component_resolved_relative_phase_similarity` remained stable over 20 deterministic value-permutation `label_shuffle` seeds.

This supports relative phase-pattern compatibility as a COMP01 candidate. It remains diagnostic. It is not a physical phase proof and not a physical time proof.

Observed decision values:

- `candidate_signal_count = 20`
- `seed_count = 20`
- `candidate_signal_fraction = 1`
- `mean_rank_correlation = 0.0243435549027`
- `mean_top_quartile_overlap = 0.240625`
- `decision_status = strong_identity_sensitive_candidate_for_followup`

Secondary context metrics:

- `cos_cos_overlap`
- `component_resolved_local_pattern_correlation`
- `component_asymmetry_delta`

These are context metrics, not primary C2 decision carriers.

`label_shuffle_mimic_warning_metrics` is empty.

This means the two Primary Candidates were not fully devalued as mimic warnings by this harder value-permutation `label_shuffle` control in the smoke test.

However, this control is still not a real newly simulated kernel control.

## 9. Interpretation

COMP01-C2 provides an important methodological intermediate step:

- COMP01-C candidate movement was not only a single `label_shuffle` seed effect,
- both Primary Candidates remain stable across 20 deterministic value-permutation controls,
- this makes the candidates interesting for further harder controls.

But:

- value-permutation `label_shuffle` is only a harder-control approximation,
- it preserves the value distribution and breaks pair identity, but it does not simulate a new kernel,
- `real_imag_proxy` remains a proxy,
- the 8-node kernel remains small,
- `specificity_established` remains false.

Interpretation:

- Positive movement: yes.
- Seed-stable candidate movement: yes.
- Specificity established: no.
- Tau model justified: no.
- D(A,B) / S_rel2 step justified: no.

## 10. Hypothese

Possible synthetic diagnostic hypotheses:

- `sin_sin_overlap` could carry robust identity-sensitive diagnostic information in the current synthetic kernel.
- `component_resolved_relative_phase_similarity` could be a particularly relevant compatibility candidate because relative phase / pattern matching appears seed-stable here compared with context metrics.
- Family Means may have hidden source-target information; rank / top-quartile / value-permutation checks make it more visible.
- `real_imag_proxy` is useful as a diagnostic split, but it must later be checked through the preferred complex trigonometric form and/or a true A/B/cos/sin coefficient representation.
- If both candidates also survive newly simulated `label_shuffle` kernels, spectrum-matched `label_shuffle`, and `feature_shuffle`, a stronger COMP01 follow-up block would be justified.

These hypotheses are synthetic diagnostic hypotheses, not physical claims.

## 11. Offene Lücke

Open gaps:

- no specificity established,
- only 20 seeds in the smoke test,
- value-permutation `label_shuffle` is not a newly simulated kernel control,
- no real kernel resimulation `label_shuffle`,
- no spectrum-matched `label_shuffle`,
- no `feature_shuffle`,
- no covariance- or spectrum-matched MaxEnt null,
- 8-node kernel remains small,
- `real_imag_proxy` remains a proxy,
- no complex trigonometric representation implemented,
- no true A/B/cos/sin reconstruction,
- no local A/Bk fingerprint metric implemented,
- no scaling to N=16 / N=32,
- no robustness over 100 / 500 true shuffle seeds,
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
- Multi-seed value-permutation label_shuffle controls are diagnostic harder-control approximations, not physical control families.
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-C2 does not attach D(A,B).
- COMP01-C2 does not construct S_rel2.
- COMP01-C2 does not derive a Lorentzian metric.
- COMP01-C2 does not validate a physical Bridge.
- COMP01-C2 does not establish diagnostic specificity yet.
- This is synthetic diagnostic work only.

## 13. Recommended next step

Recommended next step:

```text
QSB-ST-COMP01-C3 real kernel resimulation label_shuffle and spectrum-matched control plan
```

Alternative later path:

```text
QSB-ST-COMP01-D complex trigonometric representation and local-linear fingerprint plan
```

Most useful sequence directly after COMP01-C2:

1. Finish this result note.
2. Plan harder true control families:
   - real kernel resimulation `label_shuffle`
   - multiple true `label_shuffle` seeds
   - spectrum- or distribution-matched `label_shuffle`
   - `feature_shuffle`
3. Only after that, move to a new theory-level or implementation-level complex trigonometric step, unless the method section needs that notation first.

Not recommended as the immediate next step:

- tau model
- D(A,B)
- S_rel2
- Lorentz interval
- Bridge validation

## 14. Current status label

```text
COMP01C2_candidate_metric_inspection_result_documented_candidates_stable_specificity_not_established
```
