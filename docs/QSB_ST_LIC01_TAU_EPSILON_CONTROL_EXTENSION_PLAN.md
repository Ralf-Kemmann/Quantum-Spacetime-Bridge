# QSB-ST-LIC01-D Tau/Epsilon Control Extension Plan

**Block:** QSB-ST-LIC01-D / LIC01_tau_epsilon_control_extension  
**Previous status:** `LIC01_tau_epsilon_minimal_run_documented`  
**Target status:** `LIC01_tau_epsilon_controls_planned_not_implemented`  
**Date:** 2026-05-17  
**Document type:** Control-extension plan / Kontrollgerüst  
**Claim level:** Synthetic diagnostic control planning only; no physical time, Lorentz metric, spacetime, or validation claim.

---

## 1. Purpose

This document defines the next control-extension plan for the QSB-ST-LIC01 tau/epsilon phase-response diagnostic.

The previous minimal run showed that a synthetic reference kernel can be perturbed and used to compute:

```text
rho_tau(A,B)
tau_rel_candidate(A,B)
```

However, this only establishes technical executability in a synthetic setting. It does not yet show whether the response pattern is specific, robust, or distinguishable from trivial perturbation artifacts.

The purpose of LIC01-D is therefore:

> Define a transparent first control suite that tests whether `rho_tau` and `tau_rel_candidate` respond to structured local phase/correlation perturbation differently than to trivial, randomized, shuffled, or globally uniform controls.

---

## 2. Starting point

The current implemented runner is:

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

It reads:

```text
data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml
```

and writes:

```text
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/
```

The first minimal run produced:

```text
synthetic_node_count: 8
pair_count: 64
sweep_row_count: 576
tau_rel_constructed: true
S_rel2_constructed: false
```

Observed diagnostic ranges:

```text
rho_tau_min: 0.1397202524940378
rho_tau_max: 1.4117054798807853
rho_tau_mean: 0.5851738231970339

tau_rel_candidate_min: 0.0
tau_rel_candidate_max: 1.0
tau_rel_candidate_mean: 0.29707575588313
```

These values are not yet interpreted as physical structure. They are a baseline for synthetic diagnostic comparison.

---

## 3. Core question for LIC01-D

The core control question is:

> Does the local phase-response construction produce a pairwise response structure that is distinguishable from simple global phase shifts, randomized phase controls, label shuffles, and amplitude/phase decoupling controls?

More concretely:

```text
structured local perturbation
vs.
trivial/global/random/shuffled controls
```

The first LIC01-D step should test whether the pairwise response field is sensitive to the **type** of perturbation, not only to the existence of any numerical change.

---

## 4. Control families

### 4.1 Primary control families for first implementation

The first implementation should include a small but meaningful subset of the planned control families:

```text
structured_local_phase_response
global_phase_shift
random_phase
amplitude_preserved_phase_randomized
label_shuffle
```

These five are sufficient for a first control comparison without overloading the runner.

### 4.2 Secondary control families for later implementation

The following controls are important but can be deferred until after the first control run:

```text
local_gauge_like_phase_shift
spectrum_matched_phase
amplitude_only_phase_uniform
topology_preserving_graph_control
loop_closure_check
component_dominance_check
c_eff_sensitivity_check
```

The reason for deferral is methodological clarity: LIC01-D should first test whether the current response object survives the simplest hostile controls before adding more complex invariance-like checks.

---

## 5. Control definitions

### 5.1 `structured_local_phase_response`

This is the current minimal-run perturbation family.

Working role:

```text
baseline diagnostic condition
```

It applies a local source-centered phase perturbation and measures the target response profile.

Expected behavior:

```text
A structured source-target response pattern may be visible.
```

Allowed interpretation:

```text
Synthetic baseline response field for comparison.
```

Not allowed:

```text
physical delay
causal propagation
spacetime structure
Lorentz behavior
```

---

### 5.2 `global_phase_shift`

Apply the same phase shift globally to the kernel/state representation.

Working role:

```text
trivial global phase control
```

Expected behavior:

A purely global phase should ideally not create the same localized source-target response structure as the structured local perturbation.

Possible acceptance readout:

```text
global_phase_response_lower_than_structured
global_phase_response_equivalent_to_structured
global_phase_response_not_discriminating
```

If the global control looks too similar to the structured local response, the current observable may be overly sensitive to trivial phase conventions.

---

### 5.3 `random_phase`

Apply random phase perturbations under a fixed seed.

Working role:

```text
noise/randomness control
```

Expected behavior:

Random phase should generate either weaker, less structured, or less reproducible pairwise response patterns than the structured local perturbation.

Important reproducibility rule:

```text
random_seed must be fixed and reported.
```

Possible acceptance readout:

```text
structured_exceeds_random_phase
random_phase_mimics_structured
random_phase_inconclusive
```

---

### 5.4 `amplitude_preserved_phase_randomized`

Preserve amplitudes but randomize phase structure.

Working role:

```text
phase-organization specificity control
```

Expected behavior:

If `rho_tau` depends on organized phase/correlation structure, then preserving amplitudes while randomizing phase should alter or weaken the response pattern.

Possible acceptance readout:

```text
phase_organization_sensitive
amplitude_only_sufficient_warning
phase_randomization_inconclusive
```

This control is especially important because it separates amplitude effects from phase-organization effects.

---

### 5.5 `label_shuffle`

Shuffle node labels while preserving the same numeric kernel values.

Working role:

```text
label/identity control
```

Expected behavior:

A label shuffle should preserve global distributions but disrupt source-target identity. If the response summary remains identical under label shuffle, this may indicate that the diagnostic is only distributional. If source-target structure changes while aggregate values remain similar, this may support structural sensitivity.

Possible acceptance readout:

```text
label_sensitive_structure_detected
distribution_only_warning
label_shuffle_inconclusive
```

Important caution:

Label shuffles can be ambiguous in small synthetic systems. They should not be overinterpreted.

---

## 6. Proposed implementation strategy

LIC01-D should modify the runner only after this plan is accepted.

Preferred implementation style:

```text
new config option:
  controls.enabled: true
  controls.implemented_families:
    - structured_local_phase_response
    - global_phase_shift
    - random_phase
    - amplitude_preserved_phase_randomized
    - label_shuffle
```

Runner extension should add:

```text
control_family loop
control-specific perturbation operator
control_summary.csv
control_pairwise_response.csv
summary.json control fields
readout.md control section
```

The original minimal output files should either remain unchanged or receive clearly documented additional columns. Prefer adding new control-specific outputs instead of silently changing the meaning of existing files.

---

## 7. Recommended new outputs

### 7.1 `control_pairwise_response.csv`

Suggested fields:

```text
control_family
source_id
target_id
epsilon_min
epsilon_max
response_slope
response_integral
response_peak_epsilon
rho_tau
tau_rel_candidate
normalization_family
status
```

### 7.2 `control_summary.csv`

Suggested fields:

```text
control_family
pair_count
rho_tau_min
rho_tau_max
rho_tau_mean
rho_tau_std
tau_rel_candidate_min
tau_rel_candidate_max
tau_rel_candidate_mean
structured_reference_mean_ratio
structured_reference_max_ratio
status
warning
```

### 7.3 `summary.json` additions

Suggested fields:

```text
controls_implemented
control_family_count
control_summary_file
control_pairwise_response_file
structured_reference_family
control_status_labels
control_warnings
```

### 7.4 `readout.md` additions

Required section:

```text
## Control Readout
```

with substructure:

```text
### Control families implemented
### Control summary
### Control warnings
### Control interpretation boundary
```

---

## 8. Continuous field list for new outputs

### 8.1 `control_pairwise_response.csv`

| Field name | Field type | Field description |
|---|---:|---|
| `control_family` | string | Control family used for this pairwise response row. |
| `source_id` | string | Source object/node/pair for the perturbation. |
| `target_id` | string | Target object/node/pair whose response is measured. |
| `epsilon_min` | float | Minimum epsilon value used for this control family. |
| `epsilon_max` | float | Maximum epsilon value used for this control family. |
| `response_slope` | float | Finite-difference response slope estimate. |
| `response_integral` | float | Integrated response over epsilon sweep. |
| `response_peak_epsilon` | float | Epsilon value at maximum observed response. |
| `rho_tau` | float | Pairwise response-strength score. |
| `tau_rel_candidate` | float | Normalized monotone diagnostic transform of `rho_tau`. |
| `normalization_family` | string | Normalization rule used. |
| `status` | string | Row-level diagnostic status. |

### 8.2 `control_summary.csv`

| Field name | Field type | Field description |
|---|---:|---|
| `control_family` | string | Name of the control family. |
| `pair_count` | integer | Number of pairwise rows for the control family. |
| `rho_tau_min` | float | Minimum response-strength score for the control family. |
| `rho_tau_max` | float | Maximum response-strength score for the control family. |
| `rho_tau_mean` | float | Mean response-strength score for the control family. |
| `rho_tau_std` | float | Standard deviation of response-strength scores. |
| `tau_rel_candidate_min` | float | Minimum tau-rel candidate value for the control family. |
| `tau_rel_candidate_max` | float | Maximum tau-rel candidate value for the control family. |
| `tau_rel_candidate_mean` | float | Mean tau-rel candidate value for the control family. |
| `structured_reference_mean_ratio` | float or null | Ratio of this control mean to the structured reference mean. |
| `structured_reference_max_ratio` | float or null | Ratio of this control max to the structured reference max. |
| `status` | string | Summary-level status label. |
| `warning` | string | Warning or limitation note for the control family. |

---

## 9. Acceptance checks for LIC01-D implementation

A future implementation should pass:

1. Repo status checked before implementation.
2. Only explicitly requested files are created/modified.
3. Config parses.
4. Runner compiles with `python -m py_compile`.
5. Runner executes with fixed seed.
6. `summary.json` exists and includes control fields.
7. `control_pairwise_response.csv` parses with `csv.DictReader`.
8. `control_summary.csv` parses with `csv.DictReader`.
9. Each implemented control family has nonzero pair count.
10. Expected row count is documented.
11. Readout contains `Control Readout`.
12. Claim-risk grep returns only boundary/warning contexts.
13. `git diff --check` passes.
14. `git status -sb` is shown after checks.

Expected first-control row count if five families are implemented:

```text
5 control families × 64 pairwise rows = 320 control_pairwise_response rows
5 control families = 5 control_summary rows
```

If epsilon-level control sweep output is added later:

```text
5 control families × 64 pairwise rows × 9 epsilon values = 2880 sweep rows
```

For the first LIC01-D implementation, avoid adding this larger sweep file unless needed.

---

## 10. Claim Boundary

LIC01-D control planning does not establish:

```text
physical time
proper time
causal order
Lorentzian metric
spacetime emergence
Bridge validation
real-data validity
experimental validity
```

Allowed statement after successful implementation would be limited to:

> Under the tested synthetic control families, the LIC01 tau/epsilon response diagnostic can be compared against global, random, phase-randomized, and label-shuffled controls.

Stronger statements require additional controls and interpretation review.

---

## 11. Recommended next action

After this plan is committed, the next implementation step should be a controlled runner extension.

Recommended modified file:

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

Recommended additional outputs:

```text
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/control_pairwise_response.csv
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/control_summary.csv
```

Recommended status after committing this plan:

```text
LIC01_tau_epsilon_controls_planned_not_implemented
```
