# QSB-ST-LIC01-J Tau/Epsilon Seed and Label Stability Controls Plan

**Block:** QSB-ST-LIC01-J / `tau_epsilon_seed_label_stability_controls`  
**Previous status:** `LIC01_residual_control_warning_analysis_documented_specificity_not_established`  
**Target status:** `LIC01_seed_label_stability_controls_planned_not_implemented`  
**Date:** 2026-05-19  
**Document type:** Plan only / no implementation  
**Claim level:** Synthetic diagnostic planning only; no physical time, proper time, Lorentz interval, spacetime, Bridge, real-data, or experiment claim.

---

## 1. Purpose

LIC01-J plans stability controls for the remaining LIC01 residual warnings after LIC01-I.

This is a plan only. It does not implement a runner, does not change data, and does not create new run outputs.

This plan explicitly excludes:

- no `D(A,B)` attachment
- no `S_rel2` construction
- no Lorentz interval
- no physical tau
- no new physical claim
- no specificity claim

The goal is to test whether the remaining warnings are stable features of the current diagnostic or artifacts of seed choice, label-shuffle choice, small-kernel fragility, or magnitude/support dominance.

---

## 2. Current status anchor

Current status before LIC01-J:

```text
LIC01_residual_control_warning_analysis_documented_specificity_not_established
```

Current technical state:

- tau/epsilon Minimalrunner works
- Control extension works
- Specificity-Contrast layer works
- Observable / Normalization Audit works
- Global-Phase-Invariant Probe works
- Residual-Control-Warning-Analysis works
- `global_phase_warning_reduced = True`
- `residual_control_established_specificity = False`
- specificity remains not established

Residual control labels after LIC01-I:

```text
random_phase: random_phase_exceeds_reference_warning
amplitude_preserved_phase_randomized: amplitude_preserved_phase_randomized_exceeds_reference_warning
label_shuffle: label_shuffle_close_to_reference_warning
```

Open tests after LIC01-I:

- seed sensitivity has not been tested
- label stability has not been tested
- magnitude/phase component separation has not been performed

---

## 3. Motivation after LIC01-I

LIC01-I showed:

```text
residual_control_established_specificity = False
```

The `random_phase` and `amplitude_preserved_phase_randomized` controls exceed the structured reference, while `label_shuffle` remains close to the structured reference.

The remaining warnings must be tested for stability before any step toward `D(A,B)`, `S_rel2`, Lorentz-interval language, or physical tau interpretation.

Seed sensitivity and label stability were explicitly left open. LIC01-J should address those gaps directly and optionally plan a first magnitude/phase component separation check for the amplitude-preserved phase-randomized warning.

---

## 4. Core question

Are the residual warnings stable features of the current diagnostic, or are they driven by seed dependence, label-shuffle instability, small-kernel ambiguity, or magnitude/support dominance?

This is a synthetic diagnostic question only. No physical claim follows from any planned outcome.

---

## 5. Random-phase seed-sensitivity plan

Goal: test whether the `random_phase` warning remains strong across multiple deterministic seeds.

Planned seed set:

```text
0, 1, 2, 3, 4, 5, 7, 11, 13, 17
```

Plan:

- generate `random_phase` control for each seed
- apply the same global phase centering used in LIC01-H
- compute `rho_tau_centered` and `tau_rel_centered`
- compare each seed against `structured_local_phase_response`
- report pattern correlation to the structured reference
- report pattern correlation to seed 0
- report top pair and top-quartile overlap

Interpretive warning labels:

- if `random_phase` is strong only for isolated seeds: `seed_instability_warning`
- if `random_phase` is strong across many seeds: `generic_phase_sensitivity_warning`

This seed sweep must not be interpreted as a physical ensemble.

---

## 6. Label-shuffle stability plan

Goal: test whether the `label_shuffle` warning comes from a single permutation or from systematic label/kernel instability.

Planned shuffle ids:

```text
0, 1, 2, 3, 4, 5, 7, 11, 13, 17
```

Plan:

- generate deterministic label shuffles for each shuffle id
- apply the same global phase centering used in LIC01-H
- compute `rho_tau_centered` and `tau_rel_centered`
- compare each shuffle against `structured_local_phase_response`
- report pattern correlation to the original structure
- report pattern correlation to the structured reference
- report top pair and top-quartile overlap
- inspect whether high-response pairs are identity-specific or distributional

Interpretive warning labels:

- if label-shuffle response varies strongly by permutation: `label_shuffle_instability_warning`
- if label-shuffle response remains near or above reference across permutations: `small_kernel_or_distributional_scoring_warning`

---

## 7. Amplitude/phase component separation plan

Goal: test whether `amplitude_preserved_phase_randomized` remains strong because magnitude/support structure dominates the score.

This may be implemented as part of LIC01-J if it stays small, or split into a later LIC01-K block if it becomes too broad.

Planned component probes:

- magnitude-only response probe
- phase-only or relative-phase response probe
- amplitude-preserved phase-randomized comparison
- support-count / edge-count comparison
- correlation of response with magnitude/support features

Interpretive warning labels:

- if magnitude/support explains most response: `magnitude_support_dominance_warning`
- if phase-only response remains strong but unstable: `phase_response_instability_warning`
- if component split separates controls from reference: `component_split_promising_but_no_physical_claim`

The component split is diagnostic only. It is not a replacement observable unless a later block defines and validates it under predefined controls.

---

## 8. Cross-check strategy

LIC01-J should cross-check the stability results across the three residual warning families.

Required cross-checks:

- compare seed-stable `random_phase` behavior against `amplitude_preserved_phase_randomized`
- compare label-shuffle-stable patterns against structured-reference patterns
- check whether top-pair and top-quartile overlaps are stable or seed/shuffle dependent
- check whether magnitude/support features explain the amplitude-preserved warning
- keep every result at method-level status

The goal is to distinguish:

- seed dependence
- label-shuffle instability
- small-kernel ambiguity
- generic phase sensitivity
- magnitude/support dominance
- residual control mimicry

---

## 9. Required outputs for future implementation

Future implementation should add these outputs:

```text
seed_sensitivity_summary.csv
seed_sensitivity_pairwise.csv
label_stability_summary.csv
label_stability_pairwise.csv
amplitude_phase_component_summary.csv
stability_decision_summary.csv
```

Expected future row counts:

- `seed_sensitivity_summary.csv`: 10 rows for 10 seeds
- `seed_sensitivity_pairwise.csv`: 10 seeds x 64 pairs = 640 rows
- `label_stability_summary.csv`: 10 rows for 10 shuffles
- `label_stability_pairwise.csv`: 10 shuffles x 64 pairs = 640 rows
- `amplitude_phase_component_summary.csv`: small fixed table, expected at least 3 rows:
  - `magnitude_only`
  - `phase_or_relative_phase_only`
  - `amplitude_preserved_phase_randomized`
- `stability_decision_summary.csv`: 3 rows:
  - `random_phase`
  - `label_shuffle`
  - `amplitude_preserved_phase_randomized`

All generated outputs must be parseable CSV files.

---

## 10. Continuous field list

### 10.1 seed_sensitivity_summary.csv

| field | type | description |
|---|---|---|
| control_family | string | Control family name, expected `random_phase`. |
| seed | integer | Deterministic seed used for the control generation. |
| pair_count | integer | Number of source-target pairs. |
| rho_tau_centered_mean | float | Mean centered `rho_tau` for this seed. |
| rho_tau_centered_max | float | Maximum centered `rho_tau` for this seed. |
| tau_rel_centered_mean | float | Mean centered diagnostic candidate for this seed. |
| structured_reference_mean | float | Mean centered structured-reference `rho_tau`. |
| mean_ratio_to_reference | float | Seed mean divided by structured-reference mean with eta convention. |
| max_ratio_to_reference | float | Seed max divided by structured-reference max with eta convention. |
| pattern_correlation_to_reference | float or blank | Pairwise pattern correlation to structured reference. |
| pattern_correlation_to_seed0 | float or blank | Pairwise pattern correlation to seed 0. |
| top_pair | string | `source_id->target_id` pair with highest centered `rho_tau`. |
| top_quartile_overlap_to_reference | float | Top-quartile overlap with structured reference. |
| seed_sensitivity_status | string | Machine-readable seed-sensitivity status. |
| warning | string | Human-readable warning text. |

### 10.2 seed_sensitivity_pairwise.csv

| field | type | description |
|---|---|---|
| control_family | string | Control family name, expected `random_phase`. |
| seed | integer | Deterministic seed used for the control generation. |
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

### 10.3 label_stability_summary.csv

| field | type | description |
|---|---|---|
| control_family | string | Control family name, expected `label_shuffle`. |
| shuffle_id | integer | Deterministic shuffle identifier. |
| pair_count | integer | Number of source-target pairs. |
| rho_tau_centered_mean | float | Mean centered `rho_tau` for this shuffle. |
| rho_tau_centered_max | float | Maximum centered `rho_tau` for this shuffle. |
| tau_rel_centered_mean | float | Mean centered diagnostic candidate for this shuffle. |
| structured_reference_mean | float | Mean centered structured-reference `rho_tau`. |
| mean_ratio_to_reference | float | Shuffle mean divided by structured-reference mean with eta convention. |
| max_ratio_to_reference | float | Shuffle max divided by structured-reference max with eta convention. |
| pattern_correlation_to_original | float or blank | Pairwise pattern correlation to the unshuffled original. |
| pattern_correlation_to_reference | float or blank | Pairwise pattern correlation to structured reference. |
| top_pair | string | `source_id->target_id` pair with highest centered `rho_tau`. |
| top_quartile_overlap_to_reference | float | Top-quartile overlap with structured reference. |
| label_stability_status | string | Machine-readable label-stability status. |
| warning | string | Human-readable warning text. |

### 10.4 label_stability_pairwise.csv

| field | type | description |
|---|---|---|
| control_family | string | Control family name, expected `label_shuffle`. |
| shuffle_id | integer | Deterministic shuffle identifier. |
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

### 10.5 amplitude_phase_component_summary.csv

| field | type | description |
|---|---|---|
| component_probe | string | Component probe name, such as `magnitude_only`, `phase_or_relative_phase_only`, or `amplitude_preserved_phase_randomized`. |
| pair_count | integer | Number of source-target pairs. |
| rho_tau_mean | float | Mean response score for the component probe. |
| rho_tau_max | float | Maximum response score for the component probe. |
| tau_rel_mean | float | Mean normalized diagnostic candidate for the component probe. |
| ratio_to_structured_reference | float | Component mean divided by structured-reference mean with eta convention. |
| correlation_to_structured_reference | float or blank | Pairwise pattern correlation to structured reference. |
| component_status | string | Machine-readable component result status. |
| warning | string | Human-readable component warning. |

### 10.6 stability_decision_summary.csv

| field | type | description |
|---|---|---|
| control_family | string | Residual control family name. |
| tested_dimension | string | Tested stability dimension, such as seed, label, or component. |
| main_result | string | Concise machine-readable main result. |
| stability_status | string | Stability status after the check. |
| recommended_next_probe | string | Suggested follow-up probe if the warning remains. |
| specificity_status | string | Specificity status, expected to remain conservative unless predefined criteria pass. |
| warning | string | Human-readable warning text. |

---

## 11. Acceptance criteria for future implementation

Future implementation is accepted only if:

- runner compiles
- existing minimal outputs are preserved
- existing control outputs are preserved
- existing specificity outputs are preserved
- existing observable audit outputs are preserved
- existing global-phase probe outputs are preserved
- existing residual-control outputs are preserved
- new seed/label stability outputs parse
- `seed_sensitivity_summary.csv` contains 10 rows
- `seed_sensitivity_pairwise.csv` contains 640 rows
- `label_stability_summary.csv` contains 10 rows
- `label_stability_pairwise.csv` contains 640 rows
- `stability_decision_summary.csv` contains 3 rows
- result explicitly keeps specificity false unless predefined criteria are met
- `readout.md` contains a Seed and Label Stability Controls section
- claim-risk grep returns only boundary contexts
- `git diff --check` passes
- output longer than 50 lines goes to `~/Downloads/Textfiles/`

The future implementation must report all row counts and must not hide seed- or label-instability warnings.

---

## 12. Interpretation rules

Outcome A: `random_phase` exceeds reference across most seeds.

Interpretation: generic phase sensitivity or control mimicry remains likely.

Outcome B: `random_phase` exceeds reference only for few seeds.

Interpretation: seed/sampling instability; `random_phase` warning needs seed-dependent treatment.

Outcome C: `label_shuffle` remains close or exceeds across most shuffles.

Interpretation: small-kernel or distributional scoring ambiguity remains likely.

Outcome D: `label_shuffle` varies strongly across shuffles.

Interpretation: label-stability problem; current 8-node kernel may be too fragile.

Outcome E: amplitude/support component explains `amplitude_preserved_phase_randomized`.

Interpretation: score may be magnitude/support-dominated rather than structured-phase dominated.

Outcome F: all controls separate clearly after stability checks.

Interpretation: specificity may become supported only if strict predefined criteria are met, but no physical claim follows automatically.

In all cases, no physical claim is allowed.

---

## 13. Claim Boundary

`tau_rel_candidate is not physical time.`

`tau_rel_candidate is not proper time.`

`tau_rel_centered is a diagnostic probe value only.`

Seed and label stability controls are synthetic diagnostic work only.

No Lorentzian metric is derived.

No spacetime interval is constructed.

No D(A,B) is attached.

No S_rel2 is constructed.

No Bridge validation is claimed.

No real-data or experimental validation is claimed.

Specificity remains not established until shown by predefined controls.

---

## 14. Current status label

```text
LIC01_seed_label_stability_controls_planned_not_implemented
```
