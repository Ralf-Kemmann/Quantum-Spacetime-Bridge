# QSB-ST-LIC01 Tau/Epsilon Global-Phase-Invariant Probe Result Note

**Block:** QSB-ST-LIC01-H / `tau_epsilon_global_phase_invariant_observable_probe`  
**Run:** `tau_epsilon_phase_response_open`  
**Previous status:** `LIC01_global_phase_invariant_observable_probe_planned_not_implemented`  
**Status after run:** `LIC01_global_phase_invariant_probe_documented_specificity_still_open`  
**Date:** 2026-05-19  
**Document type:** Result note / synthetic global-phase-invariant probe documentation  
**Claim level:** Synthetic diagnostic probe only; no physical time, proper time, Lorentz metric, spacetime, physical Bridge, real-data, or experiment claim.

---

## 1. Purpose

This note documents the LIC01-H Global-Phase-Invariant Observable Probe for the QSB-ST-LIC01 tau/epsilon diagnostic.

The probe was added after LIC01-G reported a global phase warning:

```text
global_phase_audit_status = global_phase_sensitive_warning
```

LIC01-H asks whether transparent global phase centering reduces the `global_phase_shift` warning while preserving the existing audit boundary.

It does not introduce `D(A,B)`, does not construct `S_rel2`, does not add Lorentz-interval language, and does not assign physical meaning to `tau_rel_candidate` or `tau_rel_centered`.

---

## 2. Repo status anchor

The local status before this documentation step was clean and synchronized:

```text
## main...origin/main
```

The implementation commit anchor was:

```text
d3c354e Add QSB-ST LIC01 tau epsilon global phase invariant probe
```

Visible recent LIC01 commits included:

```text
d3c354e Add QSB-ST LIC01 tau epsilon global phase invariant probe
ea2b48d Add QSB-ST LIC01 tau epsilon global phase invariant observable probe plan
b89899c Add QSB-ST LIC01 next-after-observable-audit status note
df95c37 Add QSB-ST LIC01 tau epsilon observable normalization audit result note
08bd180 Add QSB-ST LIC01 tau epsilon observable normalization audit
5bb1a23 Add QSB-ST LIC01 tau epsilon observable normalization audit plan
c9a470c Add QSB-ST LIC01 tau epsilon specificity contrast result note
2ca8e01 Add QSB-ST LIC01 tau epsilon specificity contrast layer
eb55083 Add QSB-ST LIC01 tau epsilon specificity refinement plan
385ca0b Add QSB-ST LIC01 tau epsilon control run result note
c2139a0 Extend QSB-ST LIC01 tau epsilon runner with controls
8759fbf Add QSB-ST LIC01 tau epsilon control extension plan
```

This anchors that the LIC01-H implementation was already committed before this result note was drafted.

---

## 3. Files involved

Planning document:

```text
docs/QSB_ST_LIC01_TAU_EPSILON_GLOBAL_PHASE_INVARIANT_OBSERVABLE_PROBE_PLAN.md
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
docs/QSB_ST_LIC01_TAU_EPSILON_GLOBAL_PHASE_INVARIANT_PROBE_RESULT_NOTE.md
```

No existing project file is changed by this note.

---

## 4. Probe implementation

LIC01-H adds a global-phase-centered probe layer to the existing tau/epsilon runner.

The probe estimates a global phase angle from matrix entries with magnitude above `eta`, centers the baseline and perturbed matrices by removing that estimated global phase, and then applies the existing response logic to the centered objects.

The existing `tau_rel_candidate` definition is not changed. The additional `tau_rel_centered` field is a probe value only and is not a replacement for `tau_rel_candidate`.

The implementation reports before/after response values for each tested family:

- `structured_local_phase_response`
- `global_phase_shift`
- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

---

## 5. Acceptance summary

The LIC01-H acceptance check reported:

- runner compiles
- runner runs
- existing output regression check passed
- new global-phase probe CSVs exist and parse
- `summary.json` contains the required global phase probe fields
- `readout.md` contains `## Global-Phase-Invariant Observable Probe Readout`
- claim-risk grep returned no matches for the forbidden claim phrases
- `git diff --check` passed

Preserved core values:

```text
pair_count: 64
sweep_row_count: 576
tau_rel_constructed: true
S_rel2_constructed: false
```

Key LIC01-H summary fields:

```text
global_phase_warning_reduced: True
global_phase_probe_established_specificity: False
```

Status labels:

```text
structured_local_phase_response: probe_computed
global_phase_shift: global_phase_warning_reduced_probe
random_phase: control_still_exceeds_reference_warning
amplitude_preserved_phase_randomized: control_still_exceeds_reference_warning
label_shuffle: control_still_exceeds_reference_warning
```

---

## 6. Probe output files

New LIC01-H probe outputs:

```text
global_phase_invariant_probe_summary.csv
global_phase_invariant_pairwise_response.csv
global_phase_centering_diagnostics.csv
```

Verified row counts:

```text
global_phase_invariant_probe_summary.csv: 5
global_phase_invariant_pairwise_response.csv: 320
global_phase_centering_diagnostics.csv: 45
```

The output files document the centered probe without changing the existing minimal, control, specificity, or observable-normalization audit outputs.

---

## 7. Befund

LIC01-H Global-Phase-Invariant Observable Probe ist technisch implementiert.

The runner compiles and runs. The existing output regression check passed. The new probe outputs were generated:

- `global_phase_invariant_probe_summary.csv`
- `global_phase_invariant_pairwise_response.csv`
- `global_phase_centering_diagnostics.csv`

Verified row counts:

- `global_phase_invariant_probe_summary.csv`: 5
- `global_phase_invariant_pairwise_response.csv`: 320
- `global_phase_centering_diagnostics.csv`: 45

`readout.md` contains:

```text
## Global-Phase-Invariant Observable Probe Readout
```

The core result remains bounded:

```text
global_phase_warning_reduced: True
global_phase_probe_established_specificity: False
```

---

## 8. Interpretation

The LIC01-H probe reduces the `global_phase_shift` warning under the tested global-phase-centering diagnostic, but it does not establish overall diagnostic specificity because other controls remain warning cases.

This supports the narrow interpretation that part of the previous warning was likely global-phase-driven.

It does not solve the full specificity problem. The following controls remain warning controls:

- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

The tau/epsilon diagnostic remains controllable and auditable, but not specific enough for `D(A,B)`, `S_rel2`, Lorentz-interval language, or physical tau interpretation.

---

## 9. Hypothese

A global-phase-centered or global-phase-invariant observable layer may reduce one part of the nonspecific response.

The remaining warning controls suggest that additional causes are still active:

- generic `rho_tau` sensitivity
- phase-randomized controls may preserve relevant structure
- small-kernel ambiguity
- label-shuffle ambiguity
- controls preserve too much structure
- the observable may still not measure the intended relative or structured phase feature

These hypotheses remain method-level explanations to test, not physical conclusions.

---

## 10. Offene Lücke

Open gaps after LIC01-H:

- specificity remains not established
- global phase was only one part of the warning
- other controls remain strong
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

The global-phase-invariant probe does not establish diagnostic specificity.

QSB-ST does not derive a Lorentzian metric here.

QSB-ST does not validate spacetime emergence here.

QSB-ST does not validate a physical Bridge here.

`global_phase_probe_established_specificity remains false.`

This is synthetic diagnostic work only. It does not support a physical-time, proper-time, Lorentz, spacetime, physical Bridge, real-data, experiment, or causal-order claim.

---

## 12. Recommended next step

Recommended next block:

```text
QSB-ST-LIC01-I tau/epsilon residual control warning analysis
```

Possible planning file:

```text
docs/QSB_ST_LIC01_TAU_EPSILON_RESIDUAL_CONTROL_WARNING_ANALYSIS_PLAN.md
```

Goal: after reducing the global-phase warning, analyze why these controls remain problematic:

- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

The next block should not move directly to:

- `D(A,B)`
- `S_rel2`
- Lorentz interval
- physical time
- physical Bridge claims

The next step should isolate residual warning mechanisms before any later interval-side construction is considered.

---

## 13. Current status label

```text
LIC01_global_phase_invariant_probe_documented_specificity_still_open
```
