# QSB-ST-LIC01 Tau/Epsilon Seed and Label Stability Controls Result Note

## 1. Purpose

This note documents the LIC01-J seed and label stability controls for the current synthetic tau/epsilon diagnostic chain.

The note records the technical run result, the generated outputs, the remaining warning state, and the next recommended diagnostic block. It does not introduce a new physical claim, does not attach D(A,B), does not construct S_rel2, and does not interpret tau_rel_candidate or tau_rel_centered as physical tau.

## 2. Repo status anchor

Status before this result note:

`LIC01_seed_label_stability_controls_implemented_and_run_checked`

Current implementation anchor:

`d121bfa Add QSB-ST LIC01 tau epsilon seed label stability controls`

The documented run state is based on the LIC01-J acceptance result in which the runner compiled, executed, preserved previous outputs by regression check, and produced the new seed/label stability outputs.

## 3. Files involved

Implementation file:

- `scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py`

Run output directory:

- `runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/`

New result-note file:

- `docs/QSB_ST_LIC01_TAU_EPSILON_SEED_LABEL_STABILITY_CONTROL_RESULT_NOTE.md`

No implementation, data, or run-output files are changed by this note.

## 4. Seed/label stability implementation

LIC01-J added seed and label stability controls to the existing tau/epsilon runner.

The added controls test whether the residual warnings remain stable under deterministic random-phase seeds and deterministic label-shuffle variations after the global-phase-centered probe path.

The implementation also includes a compact amplitude/phase component summary to record whether the amplitude-preserved phase-randomized control may be carried by magnitude/support structure.

## 5. Acceptance summary

Acceptance summary:

- Runner compiles.
- Runner runs.
- Existing output regression check: OK.
- `readout.md` contains `Seed and Label Stability Controls Readout`.
- `seed_label_stability_established_specificity: False`

Generated row counts:

- `seed_sensitivity_summary.csv`: 10
- `seed_sensitivity_pairwise.csv`: 640
- `label_stability_summary.csv`: 10
- `label_stability_pairwise.csv`: 640
- `amplitude_phase_component_summary.csv`: 3
- `stability_decision_summary.csv`: 3

## 6. Seed/label stability output files

LIC01-J produced these output files:

- `seed_sensitivity_summary.csv`
- `seed_sensitivity_pairwise.csv`
- `label_stability_summary.csv`
- `label_stability_pairwise.csv`
- `amplitude_phase_component_summary.csv`
- `stability_decision_summary.csv`

The seed sweep used 10 deterministic seeds for `random_phase`.

The label-shuffle sweep used 10 deterministic shuffles for `label_shuffle`.

The amplitude/phase component summary contains the compact component probes:

- `magnitude_only`
- `phase_or_relative_phase_only`
- `amplitude_preserved_phase_randomized`

## 7. Befund

LIC01-J Seed-/Label-Stability-Controls are technically implemented.

The runner compiles, the runner runs, and the regression check for existing outputs passed.

The new Seed-/Label-Stability outputs were generated:

- `seed_sensitivity_summary.csv`
- `seed_sensitivity_pairwise.csv`
- `label_stability_summary.csv`
- `label_stability_pairwise.csv`
- `amplitude_phase_component_summary.csv`
- `stability_decision_summary.csv`

Observed row counts:

- `seed_sensitivity_summary.csv`: 10
- `seed_sensitivity_pairwise.csv`: 640
- `label_stability_summary.csv`: 10
- `label_stability_pairwise.csv`: 640
- `amplitude_phase_component_summary.csv`: 3
- `stability_decision_summary.csv`: 3

Status labels:

- `random_phase`: `generic_phase_sensitivity_warning` across all 10 seeds
- `label_shuffle`: `label_shuffle_stably_close_to_reference_warning` across all 10 shuffles
- `amplitude_preserved_phase_randomized`: `magnitude_support_dominance_warning`

`seed_label_stability_established_specificity: False`

## 8. Interpretation

`random_phase` is not only a single seed outlier in the tested seed set.

`label_shuffle` is not only a single permutation effect in the tested shuffle set.

Amplitude/support appears to play a carrying role for the amplitude-preserved control.

The global phase issue was a subproblem, but stable residual warnings remain after global phase centering.

The tau/epsilon diagnostic remains control-comparable, but diagnostic specificity is not established.

There is no transition here to D(A,B), S_rel2, a Lorentz interval, or physical tau.

## 9. Hypothese

The `random_phase` warning may indicate generic `rho_tau` phase sensitivity or a response observable that is still too broad.

The `label_shuffle` warning may indicate small-kernel ambiguity, distributional scoring, or missing source-target identity sensitivity.

The `amplitude_preserved_phase_randomized` warning may indicate that magnitude/support structure carries the score more strongly than structured phase.

The current marker does not yet robustly isolate the intended structured locality or relative phase signal.

## 10. Offene Lücke

Diagnostic specificity remains not established.

The seed sweep was executed, but `random_phase` remains stably problematic.

The label-shuffle sweep was executed, but `label_shuffle` remains stably close to the reference.

Magnitude-/phase-component separation was performed only as a small summary probe; it is not a complete new observable architecture.

Larger or less symmetric kernels have not yet been checked.

No final cause has been isolated.

No D(A,B) is attached.

No S_rel2 is constructed.

No Lorentz test is performed.

No physical time claim is made.

No real-data or experiment claim is made.

## 11. Claim Boundary

tau_rel_candidate is not physical time.

tau_rel_candidate is not proper time.

tau_rel_centered is a diagnostic probe value only.

seed and label stability controls do not establish diagnostic specificity.

QSB-ST does not derive a Lorentzian metric here.

QSB-ST does not validate spacetime emergence here.

QSB-ST does not validate a physical Bridge here.

seed_label_stability_established_specificity remains false.

## 12. Recommended next step

Recommended next block:

`QSB-ST-LIC01-K tau/epsilon magnitude-phase component separation and kernel-size sensitivity plan`

Possible file:

`docs/QSB_ST_LIC01_TAU_EPSILON_MAGNITUDE_PHASE_KERNEL_SENSITIVITY_PLAN.md`

Recommended target:

- test whether magnitude/support dominance carries the amplitude-preserved control
- test whether a phase-only or relative-phase observable separates the residual warnings better
- test whether a larger or less symmetric kernel reduces the `label_shuffle` ambiguity
- test whether `rho_tau` is too generic and needs a structure- or pattern-specific readout

This next step should not move directly to D(A,B), S_rel2, Lorentz-interval language, physical time, or Bridge validation.

## 13. Current status label

`LIC01_seed_label_stability_controls_documented_specificity_not_established`
