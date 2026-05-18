# QSB-ST-LIC01 Tau/Epsilon Residual Control Warning Analysis Result Note

**Block:** QSB-ST-LIC01-I / `tau_epsilon_residual_control_warning_analysis`  
**Run:** `tau_epsilon_phase_response_open`  
**Previous status:** `LIC01_residual_control_warning_analysis_planned_not_implemented`  
**Status after run:** `LIC01_residual_control_warning_analysis_documented_specificity_not_established`  
**Date:** 2026-05-19  
**Document type:** Result note / synthetic residual-control warning analysis documentation  
**Claim level:** Synthetic diagnostic analysis only; no physical time, proper time, Lorentz metric, spacetime, physical Bridge, real-data, or experiment claim.

---

## 1. Purpose

This note documents the LIC01-I Residual-Control-Warning-Analysis run for the QSB-ST-LIC01 tau/epsilon diagnostic.

LIC01-H reduced the global phase warning, but the overall specificity status remained open. LIC01-I therefore separates the remaining warning controls after global phase centering:

- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

The purpose is diagnostic separation of warning mechanisms. It does not introduce `D(A,B)`, does not construct `S_rel2`, does not add Lorentz-interval language, and does not assign physical meaning to `tau_rel_candidate` or `tau_rel_centered`.

---

## 2. Repo status anchor

The local status before this documentation step was clean and synchronized:

```text
## main...origin/main
```

The implementation commit anchor was:

```text
c19bd9c Add QSB-ST LIC01 tau epsilon residual control warning analysis
```

Visible recent LIC01 commits included:

```text
c19bd9c Add QSB-ST LIC01 tau epsilon residual control warning analysis
238bccd Add QSB-ST LIC01 tau epsilon residual control warning analysis plan
5e16239 Add QSB-ST LIC01 tau epsilon global phase invariant probe result note
d3c354e Add QSB-ST LIC01 tau epsilon global phase invariant probe
ea2b48d Add QSB-ST LIC01 tau epsilon global phase invariant observable probe plan
b89899c Add QSB-ST LIC01 next-after-observable-audit status note
df95c37 Add QSB-ST LIC01 tau epsilon observable normalization audit result note
08bd180 Add QSB-ST LIC01 tau epsilon observable normalization audit
5bb1a23 Add QSB-ST LIC01 tau epsilon observable normalization audit plan
c9a470c Add QSB-ST LIC01 tau epsilon specificity contrast result note
2ca8e01 Add QSB-ST LIC01 tau epsilon specificity contrast layer
eb55083 Add QSB-ST LIC01 tau epsilon specificity refinement plan
```

This anchors that the LIC01-I implementation was already committed before this result note was drafted.

---

## 3. Files involved

Planning document:

```text
docs/QSB_ST_LIC01_TAU_EPSILON_RESIDUAL_CONTROL_WARNING_ANALYSIS_PLAN.md
```

Runner:

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

Run output directory:

```text
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/
```

Result note created by this documentation step:

```text
docs/QSB_ST_LIC01_TAU_EPSILON_RESIDUAL_CONTROL_WARNING_ANALYSIS_RESULT_NOTE.md
```

No existing project file is changed by this note.

---

## 4. Residual-control implementation

LIC01-I adds a residual-control analysis layer after the global-phase-centered LIC01-H probe.

The analysis uses centered probe fields:

```text
rho_tau_centered
tau_rel_centered
```

It compares the three residual warning controls against:

```text
structured_local_phase_response
```

It also compares the residual controls against each other to inspect whether the warning patterns look shared or distinct.

The existing `tau_rel_candidate` definition is not changed. The `tau_rel_centered` field remains a diagnostic probe value only.

Optional seed and label-stability files were not generated in this run:

```text
residual_control_seed_sensitivity_file: not_generated
residual_control_label_stability_file: not_generated
```

---

## 5. Acceptance summary

The LIC01-I acceptance check reported:

- runner compiles
- runner runs
- existing output regression check passed
- new residual-control CSVs exist and parse
- `summary.json` contains the required residual-control fields
- `readout.md` contains `## Residual Control Warning Analysis Readout`
- claim-risk grep returned no matches for the forbidden claim phrases
- `git diff --check` passed

Preserved core values:

```text
pair_count: 64
sweep_row_count: 576
tau_rel_constructed: true
S_rel2_constructed: false
```

Key LIC01-I summary field:

```text
residual_control_established_specificity: False
```

Status labels:

```text
random_phase: random_phase_exceeds_reference_warning
amplitude_preserved_phase_randomized: amplitude_preserved_phase_randomized_exceeds_reference_warning
label_shuffle: label_shuffle_close_to_reference_warning
```

---

## 6. Residual-control output files

New LIC01-I residual-control outputs:

```text
residual_control_warning_summary.csv
residual_control_pairwise_comparison.csv
residual_control_family_correlation.csv
```

Verified row counts:

```text
residual_control_warning_summary.csv: 3
residual_control_pairwise_comparison.csv: 192
residual_control_family_correlation.csv: 6
```

Optional outputs were not generated:

```text
residual_control_seed_sensitivity_file: not_generated
residual_control_label_stability_file: not_generated
```

The residual-control outputs are additive and do not replace existing minimal, control, specificity, observable-audit, or global-phase probe outputs.

---

## 7. Befund

LIC01-I Residual-Control-Warning-Analysis ist technisch implementiert.

The runner compiles and runs. The existing output regression check passed. The new residual-control outputs were generated:

- `residual_control_warning_summary.csv`
- `residual_control_pairwise_comparison.csv`
- `residual_control_family_correlation.csv`

Verified row counts:

- `residual_control_warning_summary.csv`: 3
- `residual_control_pairwise_comparison.csv`: 192
- `residual_control_family_correlation.csv`: 6

`readout.md` contains:

```text
## Residual Control Warning Analysis Readout
```

The status remains bounded:

```text
residual_control_established_specificity: False
```

Statuslabels:

- `random_phase`: `random_phase_exceeds_reference_warning`
- `amplitude_preserved_phase_randomized`: `amplitude_preserved_phase_randomized_exceeds_reference_warning`
- `label_shuffle`: `label_shuffle_close_to_reference_warning`

---

## 8. Interpretation

The LIC01-I residual-control analysis separates the remaining random_phase, amplitude-preserved phase-randomized, and label-shuffle warnings after global phase centering. It shows that diagnostic specificity remains not established.

The global phase warning was a real subproblem, but reducing it was not the main solution.

Current interpretation by control:

- `random_phase` exceeds the structured reference.
- `amplitude_preserved_phase_randomized` exceeds the structured reference.
- `label_shuffle` remains close to the structured reference.

The tau/epsilon diagnostic remains controllable and auditable, but it is not specific enough for `D(A,B)`, `S_rel2`, Lorentz-interval language, or physical tau interpretation.

---

## 9. Hypothese

The `random_phase` warning may indicate generic `rho_tau` phase sensitivity, seed or sampling dependence, or high-variance response in the small synthetic kernel.

The `amplitude_preserved_phase_randomized` warning may indicate that amplitude/support structure carries the score more strongly than structured phase organization.

The `label_shuffle` warning may indicate small-kernel ambiguity, distributional scoring, or insufficient source-target identity sensitivity.

Together, the residual controls suggest that the current marker has not yet isolated the intended structured locality or relative phase feature.

---

## 10. Offene Lücke

Open gaps after LIC01-I:

- specificity remains not established
- seed sensitivity has not been tested
- label stability has not been tested
- magnitude/phase component separation has not been performed
- larger or less symmetric kernels have not been tested
- no final cause has been isolated
- no `D(A,B)` attachment
- no `S_rel2` construction
- no Lorentz test
- no physical time claim
- no real-data or experiment claim

These gaps block any move toward an interval-like object.

---

## 11. Claim Boundary

`tau_rel_candidate is not physical time.`

`tau_rel_candidate is not proper time.`

`tau_rel_centered is a diagnostic probe value only.`

Residual control warning analysis does not establish diagnostic specificity.

QSB-ST does not derive a Lorentzian metric here.

QSB-ST does not validate spacetime emergence here.

QSB-ST does not validate a physical Bridge here.

`residual_control_established_specificity remains false.`

This is synthetic diagnostic work only. It does not support a physical-time, proper-time, Lorentz, spacetime, physical Bridge, real-data, experiment, or causal-order claim.

---

## 12. Recommended next step

Recommended next block:

```text
QSB-ST-LIC01-J tau/epsilon seed and label stability controls
```

Possible planning file:

```text
docs/QSB_ST_LIC01_TAU_EPSILON_SEED_LABEL_STABILITY_CONTROL_PLAN.md
```

Goal: complete the optional control lines left open by LIC01-I:

- `seed_sensitivity_sweep` for `random_phase`
- multiple label shuffles for `label_shuffle`
- optional magnitude/phase component separation for `amplitude_preserved_phase_randomized`

The next block should not move directly to:

- `D(A,B)`
- `S_rel2`
- Lorentz interval
- physical time
- physical Bridge validation

The next step should test residual stability before any later interval-side construction is considered.

---

## 13. Current status label

```text
LIC01_residual_control_warning_analysis_documented_specificity_not_established
```
