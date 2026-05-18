# QSB-ST-LIC01-H Tau/Epsilon Global-Phase-Invariant Observable Probe Plan

**Block:** QSB-ST-LIC01-H / `tau_epsilon_global_phase_invariant_observable_probe`  
**Previous status:** `LIC01_next_after_observable_audit_status_documented`  
**Target status:** `LIC01_global_phase_invariant_observable_probe_planned_not_implemented`  
**Date:** 2026-05-18  
**Document type:** Plan only / no implementation  
**Claim level:** Synthetic diagnostic planning only; no physical time, proper time, Lorentz interval, spacetime, Bridge, real-data, or experiment claim.

---

## 1. Purpose

LIC01-H plans a first global-phase-invariant observable probe for the existing tau/epsilon diagnostic chain.

This is a plan only. It does not implement a runner, does not change data, and does not create new run outputs.

This plan explicitly excludes:

- no `D(A,B)` attachment
- no `S_rel2` construction
- no Lorentz interval
- no physical tau
- no new physical claim

The purpose is to test, in a future implementation, whether the current warning is partly caused by an observable that responds too strongly to global phase motion.

---

## 2. Current status anchor

Current status before LIC01-H:

```text
LIC01_next_after_observable_audit_status_documented
```

Current technical state:

- tau/epsilon Minimalrunner works
- Control extension works
- Specificity-Contrast layer works
- Observable / Normalization Audit works
- specificity remains not established

Current warning fields:

```text
audit_established_specificity = false
global_phase_audit_status = global_phase_sensitive_warning
small_kernel_audit_status = small_kernel_label_shuffle_ambiguous_present
```

The tau/epsilon diagnostic is technically implemented and auditable, but it is not established as specific under the current controls.

---

## 3. Motivation from LIC01-G

LIC01-G reported:

```text
global_phase_audit_status = global_phase_sensitive_warning
```

If a global phase factor produces a strong response, the current observable may be too sensitive to absolute or global phase motion. That would make the response less clearly tied to relative phase or local structured behavior.

The next conservative step is therefore a global-phase-invariant observable probe. The probe should test whether removing or separating global phase components reduces the `global_phase_shift` warning while preserving useful structured local response information.

---

## 4. Core question

Does a global-phase-invariant observable reduce the `global_phase_shift` warning while preserving structured local response information?

This is a diagnostic question only. A favorable result would not establish physical meaning or diagnostic specificity by itself.

---

## 5. Observable problem statement

The current observable may respond to absolute or global phase movement.

A better candidate for this stage should remove global phase components and inspect relative phase or correlation structure instead. The goal is not to tune the result until the structured reference wins. The goal is to determine whether global phase sensitivity is one cause of the current warning.

Any centering or invariant construction must be reported transparently and compared against the original observable.

---

## 6. Candidate global-phase-invariant observables

### 6.1 relative_phase_difference_response

Idea: for complex `K_ij`, avoid using only absolute phase `arg(K_ij)`. Instead, compute relative phase differences, such as local source-centered, target-centered, edge-adjacent, or loop-adjacent differences.

Expected diagnostic value: a uniform global phase component should cancel or be strongly reduced, while relative phase structure can remain visible.

### 6.2 phase_gradient_response

Idea: measure phase changes along source-target-related edges or neighborhoods. A global phase offset should fall out because the observable depends on differences across the local relation graph.

Expected diagnostic value: global phase shifts should be less dominant than local phase gradients if the structured signal is genuinely local.

### 6.3 gauge_centered_kernel_response

Idea: before computing the response, perform a global phase centering step. For example, estimate a dominant or global phase angle and subtract it, or center `K` against a reference phase.

Expected diagnostic value: the centered object can be compared with the original object to determine how much response was carried by global phase motion.

### 6.4 loop_phase_closure_response

Idea: inspect phase sums or products along small cycles. Global phase factors can partially cancel in closure-style quantities, while relative or structured phase information may remain.

Expected diagnostic value: closure-like quantities can separate some relative phase structure from global phase drift, but they require careful small-kernel checks.

---

## 7. Recommended first probe

Recommended first LIC01-H probe:

```text
global_phase_centered_response
```

Planned definition, not implemented here:

- for each perturbed `K`, estimate a global phase angle
- remove that global phase component
- compute the same response logic as before on the centered object
- compare structured reference and `global_phase_shift` control directly
- report before/after values for raw `rho_tau` and normalized `tau_rel_candidate`

The target is not to force the structured reference to win. The target is to test whether the global phase warning is reduced by a transparent centering probe.

Global phase centering must not be used as an arbitrary result-improvement step. It is a diagnostic probe, not a confirmed replacement for the existing observable.

---

## 8. Required outputs for future implementation

Future implementation should add these outputs:

```text
global_phase_invariant_probe_summary.csv
global_phase_invariant_pairwise_response.csv
global_phase_centering_diagnostics.csv
```

Expected future row counts:

- `global_phase_invariant_probe_summary.csv`: one row per tested family, likely 5 rows
- `global_phase_invariant_pairwise_response.csv`: 5 families x 64 pairs = 320 rows
- `global_phase_centering_diagnostics.csv`: at least one row per family, or family x epsilon if sweep-level diagnostics are added

These outputs should be additive. Existing minimal, control, specificity, and observable-audit outputs should remain preserved.

---

## 9. Continuous field list

### 9.1 global_phase_invariant_probe_summary.csv

| field | type | description |
|---|---|---|
| family | string | Control or reference family name. |
| pair_count | integer | Number of source-target pairs included for the family. |
| rho_tau_original_mean | float | Mean raw `rho_tau` before global phase centering. |
| rho_tau_centered_mean | float | Mean raw `rho_tau` after global phase centering. |
| rho_tau_mean_delta | float | `rho_tau_centered_mean - rho_tau_original_mean`. |
| rho_tau_mean_ratio | float | Centered mean divided by original mean with the configured eta convention. |
| global_phase_warning_before | string | Warning status before centering. |
| global_phase_warning_after | string | Warning status after centering. |
| specificity_status_before | string | Specificity status before centering. |
| specificity_status_after | string | Specificity status after centering. |
| probe_status | string | Machine-readable probe outcome status. |
| warning | string | Human-readable caution or warning text. |

### 9.2 global_phase_invariant_pairwise_response.csv

| field | type | description |
|---|---|---|
| family | string | Control or reference family name. |
| source_id | string | Source node identifier. |
| target_id | string | Target node identifier. |
| rho_tau_original | float | Raw `rho_tau` before global phase centering. |
| rho_tau_centered | float | Raw `rho_tau` after global phase centering. |
| rho_tau_delta | float | `rho_tau_centered - rho_tau_original`. |
| tau_rel_original | float | Existing `tau_rel_candidate` before centering. |
| tau_rel_centered | float | Normalized candidate value after centering, if constructed. |
| tau_rel_delta | float | `tau_rel_centered - tau_rel_original`. |
| global_phase_centering_applied | boolean | Whether centering was applied for the row. |
| status | string | Machine-readable row status. |

### 9.3 global_phase_centering_diagnostics.csv

| field | type | description |
|---|---|---|
| family | string | Control or reference family name. |
| epsilon | float | Perturbation value for sweep-level diagnostics. |
| global_phase_angle_estimate | float | Estimated global phase angle removed by centering. |
| phase_centering_norm_delta | float | Norm difference introduced by the centering operation. |
| response_before_centering | float | Response value before centering. |
| response_after_centering | float | Response value after centering. |
| status | string | Machine-readable centering diagnostic status. |

---

## 10. Acceptance criteria for future implementation

Future implementation is accepted only if:

- runner compiles
- existing minimal outputs are preserved
- existing control outputs are preserved
- existing specificity outputs are preserved
- existing observable audit outputs are preserved
- new global-phase-invariant probe outputs parse
- `global_phase_shift` before/after comparison is reported
- `audit_established_specificity` remains false unless strict predefined criteria are met
- `readout.md` contains a Global-Phase-Invariant Observable Probe section
- claim-risk grep returns only boundary contexts
- `git diff --check` passes
- output longer than 50 lines goes to `~/Downloads/Textfiles/`

The future implementation must report row counts and must not hide warnings.

---

## 11. Interpretation rules

Possible outcomes:

A. global phase warning decreases

Interpretation: the previous observable was likely too sensitive to global phase components.

B. global phase warning persists

Interpretation: the issue is not solved by simple global phase centering; controls may mimic deeper response structure or `rho_tau` remains too generic.

C. structured response also collapses

Interpretation: the apparent structured response may have been dominated by global phase motion.

D. controls still exceed reference

Interpretation: specificity remains not established.

In all cases, no physical claim is allowed. The result remains a synthetic diagnostic probe.

---

## 12. Claim Boundary

`tau_rel_candidate is not physical time.`

`tau_rel_candidate is not proper time.`

The global-phase-invariant observable is a diagnostic probe only.

No Lorentzian metric is derived.

No spacetime interval is constructed.

No Bridge validation is claimed.

No real-data or experimental validation is claimed.

Specificity remains not established until shown by predefined controls.

---

## 13. Current status label

```text
LIC01_global_phase_invariant_observable_probe_planned_not_implemented
```
