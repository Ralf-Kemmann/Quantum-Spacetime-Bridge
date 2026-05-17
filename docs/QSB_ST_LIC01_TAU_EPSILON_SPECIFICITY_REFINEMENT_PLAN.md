# QSB-ST-LIC01-F Tau/Epsilon Specificity Refinement Plan

**Block:** QSB-ST-LIC01-F / LIC01_tau_epsilon_specificity_refinement  
**Previous status:** `LIC01_tau_epsilon_controls_documented_specificity_open`  
**Target status:** `LIC01_tau_epsilon_specificity_refinement_planned_not_implemented`  
**Date:** 2026-05-18  
**Document type:** Specificity-refinement plan / Spezifitäts-Schärfungsplan  
**Claim level:** Synthetic diagnostic planning only; no physical time, Lorentz metric, spacetime, or validation claim.

---

## 1. Purpose

This document defines the next refinement plan for the QSB-ST-LIC01 tau/epsilon diagnostic after the first control run.

LIC01-E established that the control runner is technically implemented and reproducible. It also produced the first important cautionary finding:

> Several control families remain close to the structured local phase-response reference.

Therefore, LIC01-F does not move toward `S_rel2_candidate`, physical interpretation, or distance attachment yet.

The purpose of LIC01-F is narrower:

> Identify why the current `rho_tau(A,B)` / `tau_rel_candidate(A,B)` diagnostic does not yet show strong specificity against the tested controls, and define the next transparent refinement path.

---

## 2. Starting point

The current LIC01 chain is:

```text
Design → Config → Minimal Runner → Minimal Result Note → Control Plan → Control Runner → Control Result Note
```

Current repo anchors:

```text
docs/QSB_ST_TAU_REL_PHASE_RESPONSE_CONSTRUCTION_DESIGN.md
data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml
docs/QSB_ST_LIC01_TAU_EPSILON_PHASE_RESPONSE_CONFIG_FIELDS.md
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
docs/QSB_ST_LIC01_TAU_EPSILON_MINIMAL_RUN_RESULT_NOTE.md
docs/QSB_ST_LIC01_TAU_EPSILON_CONTROL_EXTENSION_PLAN.md
docs/QSB_ST_LIC01_TAU_EPSILON_CONTROL_RUN_RESULT_NOTE.md
```

Current status:

```text
LIC01_tau_epsilon_controls_documented_specificity_open
```

---

## 3. Current known result

The first control extension successfully produced:

```text
control_pairwise_response.csv
control_summary.csv
```

with expected row counts:

```text
control_pairwise_response.csv: 320 rows
control_summary.csv: 5 rows
```

Control families implemented:

```text
structured_local_phase_response
global_phase_shift
random_phase
amplitude_preserved_phase_randomized
label_shuffle
```

Key warning:

```text
global_phase_shift: close to structured reference
random_phase: close to structured reference
amplitude_preserved_phase_randomized: close to structured reference
label_shuffle: close/ambiguous warning
```

Current bounded interpretation:

```text
control comparison implemented: yes
diagnostic specificity established: no
physical interpretation: no
```

---

## 4. Core LIC01-F question

The central question is:

> Which part of the current construction makes the structured local perturbation insufficiently distinguishable from the controls?

Candidate causes:

```text
response observable too broad
normalization washes out structure
rho_tau score too generic
tau_rel transform compresses differences
synthetic kernel too symmetric/small
control construction too similar to structured reference
global phase not properly gauge-irrelevant in current observable
small-system label shuffle ambiguity
```

LIC01-F should not assume which explanation is correct. It should define tests that can separate these possibilities.

---

## 5. Diagnostic hypotheses

### 5.1 H1 — Observable too broad

The current target observable uses row/column response around the target. This may react to many kinds of phase motion, not specifically to structured local perturbation.

Possible symptom:

```text
global_phase_shift and random_phase remain close to structured reference
```

Possible refinement:

```text
compare local-neighborhood observable vs row/column-global observable
```

Candidate new observable families:

```text
local_edge_response
nearest_neighbor_response
source_target_path_response
off_source_background_response
antisymmetric_phase_response
phase_gradient_response
```

---

### 5.2 H2 — Normalization washes out specificity

Global max-abs normalization or per-family min/max scaling may compress meaningful differences and make controls look closer than they should.

Possible symptom:

```text
tau_rel_candidate ranges 0..1 for every family even when rho_tau differs
```

Possible refinement:

```text
report raw rho_tau contrasts before tau normalization
compare global normalization vs shared structured-reference normalization
avoid per-family normalization for control comparison
```

Candidate contrast fields:

```text
rho_tau_raw
rho_tau_global_norm
rho_tau_reference_norm
tau_rel_candidate_family_norm
tau_rel_candidate_shared_norm
```

---

### 5.3 H3 — rho_tau score too generic

The current `rho_tau` is based on small positive epsilon response divided by epsilon. This may measure generic sensitivity rather than structured phase-response specificity.

Possible symptom:

```text
all perturbation families produce comparable rho_tau distributions
```

Possible refinement:

```text
add contrast statistics that compare full pairwise response patterns
```

Candidate statistics:

```text
structured_control_mean_delta
structured_control_max_delta
structured_control_rank_separation
pairwise_pattern_correlation
source_target_locality_contrast
within_source_target_anisotropy
```

---

### 5.4 H4 — tau_rel transform hides differences

The inverse-response transform and min/max normalization may create a readable candidate field but may also hide family-level differences.

Possible symptom:

```text
rho_tau differs somewhat but tau_rel_candidate becomes similarly distributed
```

Possible refinement:

```text
separate rho_tau analysis from tau_rel_candidate analysis
```

Rule:

```text
Do not use tau_rel_candidate alone for specificity.
Always report raw response and contrast layer.
```

---

### 5.5 H5 — Synthetic kernel too small or too symmetric

An 8-node synthetic kernel may be too small and symmetric to support robust distinction between structured local and shuffled/random controls.

Possible symptom:

```text
label_shuffle ambiguous
global and random controls too close
```

Possible refinement:

```text
run small kernel family sweep
```

Candidate synthetic kernel families:

```text
ring_phase_kernel_n8
ring_phase_kernel_n12
clustered_phase_kernel_n12
asymmetric_two_cluster_kernel_n12
hierarchical_phase_kernel_n16
```

---

### 5.6 H6 — Control construction too close to structured reference

Some controls may still preserve enough source-indexed or kernel-wide phase structure to mimic the structured local response.

Possible symptom:

```text
random_phase and amplitude_preserved_phase_randomized close to structured reference
```

Possible refinement:

```text
strengthen hostile controls and document exact control operators
```

Candidate additions:

```text
phase_destroyed_control
source_target_decoupled_control
epsilon_sign_scrambled_control
target_response_permuted_control
row_column_background_control
```

---

### 5.7 H7 — Global phase should be gauge-like but is not invisible

A global phase shift should often be physically unobservable if only relative phases matter. If the current observable reacts strongly to global phase, the observable may not be gauge-like enough.

Possible symptom:

```text
global_phase_shift close to structured reference
```

Possible refinement:

```text
add global-phase-invariant response observable
```

Candidate observable:

```text
relative_phase_difference_response
phase_gradient_modulo_global_response
gauge_centered_kernel_response
```

---

## 6. Recommended LIC01-F output strategy

LIC01-F should not immediately rewrite the full runner. The next implementation should add a **contrast layer** while preserving existing outputs.

Recommended new outputs:

```text
specificity_contrast_summary.csv
specificity_pairwise_contrast.csv
```

Optional later output:

```text
specificity_kernel_family_summary.csv
```

The first refinement should prioritize comparing structured reference against controls using raw and shared-normalized response metrics.

---

## 7. Proposed new output fields

### 7.1 `specificity_contrast_summary.csv`

Suggested fields:

```text
control_family
reference_family
pair_count
rho_tau_reference_mean
rho_tau_control_mean
rho_tau_mean_delta
rho_tau_mean_ratio
rho_tau_reference_max
rho_tau_control_max
rho_tau_max_delta
rho_tau_max_ratio
pairwise_pattern_correlation
rank_separation_score
specificity_status
warning
```

### 7.2 `specificity_pairwise_contrast.csv`

Suggested fields:

```text
source_id
target_id
control_family
rho_tau_reference
rho_tau_control
rho_tau_delta
rho_tau_ratio
tau_rel_reference
tau_rel_control
tau_rel_delta
pattern_status
```

---

## 8. Continuous field list

### 8.1 `specificity_contrast_summary.csv`

| Field name | Field type | Field description |
|---|---:|---|
| `control_family` | string | Control family compared against the structured reference. |
| `reference_family` | string | Reference family, expected `structured_local_phase_response`. |
| `pair_count` | integer | Number of source-target pairs compared. |
| `rho_tau_reference_mean` | float | Mean raw response score for reference family. |
| `rho_tau_control_mean` | float | Mean raw response score for control family. |
| `rho_tau_mean_delta` | float | Reference mean minus control mean. |
| `rho_tau_mean_ratio` | float | Control mean divided by reference mean. |
| `rho_tau_reference_max` | float | Maximum raw response score for reference family. |
| `rho_tau_control_max` | float | Maximum raw response score for control family. |
| `rho_tau_max_delta` | float | Reference max minus control max. |
| `rho_tau_max_ratio` | float | Control max divided by reference max. |
| `pairwise_pattern_correlation` | float or null | Correlation between reference and control pairwise response patterns. |
| `rank_separation_score` | float or null | Threshold-free separation score between reference and control ranks. |
| `specificity_status` | string | Summary status label for specificity. |
| `warning` | string | Warning or interpretation note. |

### 8.2 `specificity_pairwise_contrast.csv`

| Field name | Field type | Field description |
|---|---:|---|
| `source_id` | string | Source object/node/pair. |
| `target_id` | string | Target object/node/pair. |
| `control_family` | string | Control family compared against reference. |
| `rho_tau_reference` | float | Raw response score for structured reference. |
| `rho_tau_control` | float | Raw response score for control family. |
| `rho_tau_delta` | float | Reference score minus control score. |
| `rho_tau_ratio` | float | Control score divided by reference score. |
| `tau_rel_reference` | float | Tau-rel candidate value for structured reference. |
| `tau_rel_control` | float | Tau-rel candidate value for control family. |
| `tau_rel_delta` | float | Reference tau candidate minus control tau candidate. |
| `pattern_status` | string | Pair-level diagnostic status label. |

---

## 9. Specificity status labels

Suggested labels:

```text
specificity_supported_in_tested_controls
specificity_weak_or_inconclusive
control_close_to_reference_warning
control_exceeds_reference_warning
normalization_sensitivity_warning
small_kernel_ambiguity_warning
```

Label rules should be conservative. Do not mark specificity as supported unless multiple controls show clear separation under raw and shared-normalized measures.

---

## 10. Acceptance criteria for future implementation

A future LIC01-F implementation should pass:

1. Repo status checked before implementation.
2. Only explicitly requested files are modified.
3. Runner still compiles.
4. Runner still produces original minimal outputs.
5. Runner still produces LIC01-E control outputs.
6. New specificity outputs parse with `csv.DictReader`.
7. `specificity_contrast_summary.csv` contains one row per non-reference control.
8. `specificity_pairwise_contrast.csv` contains pairwise comparison rows.
9. Raw `rho_tau` contrasts are reported before any tau normalization.
10. Shared-normalization or raw-comparison warning is documented.
11. Readout contains a `Specificity Readout` section.
12. Summary JSON includes specificity fields.
13. Claim-risk grep returns only boundary/warning contexts.
14. `git diff --check` passes.
15. Acceptance output above 50 lines is redirected to `~/Downloads/Textfiles/`.

Expected row counts if four non-reference controls are compared against structured reference:

```text
specificity_contrast_summary.csv: 4 rows
specificity_pairwise_contrast.csv: 4 controls × 64 pairs = 256 rows
```

---

## 11. Implementation boundaries

LIC01-F implementation should not:

```text
construct S_rel2_candidate
attach D(A,B)
claim physical time
claim proper time
claim Lorentz compatibility
claim spacetime emergence
claim Bridge validation
```

LIC01-F may only refine diagnostic specificity assessment.

---

## 12. Claim Boundary

LIC01-F planning supports only the following statement:

> The first LIC01 control suite produced warning-level results, so the next step is to refine the diagnostic comparison by separating raw response strength, normalization effects, pairwise pattern similarity, and control/reference contrast.

LIC01-F does not establish diagnostic specificity. It plans tests to evaluate it.

---

## 13. Recommended next action

After this plan is committed, prepare a Codex task for the LIC01-F implementation.

Recommended implementation target:

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

Recommended new outputs:

```text
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/specificity_contrast_summary.csv
runs/QSB-ST-LIC01/tau_epsilon_phase_response_open/specificity_pairwise_contrast.csv
```

Recommended status after committing this plan:

```text
LIC01_tau_epsilon_specificity_refinement_planned_not_implemented
```
