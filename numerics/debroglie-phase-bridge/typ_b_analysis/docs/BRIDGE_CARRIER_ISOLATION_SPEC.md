# BRIDGE_CARRIER_ISOLATION_SPEC — M.3.9x
## Specification for isolating likely physical bridge carriers from secondary and diagnostic quantities

**Date:** 2026-04-04  
**Project status:** Internal specification note  
**Scope:** First structured isolation plan for likely bridge carriers in the FSW–AO / Type-B transition picture

---

## 1. Purpose

The purpose of this specification is to move the project from a robust but still partly composite transition picture toward a more explicit physical anatomy of the bridge.

The central question is:

> **Which of the currently used quantities are physically primary bridge carriers, which are only supportive, and which are merely diagnostic scaffolding?**

This specification defines:
- the working categories,
- the first candidate list,
- the main test axes,
- the evaluation logic,
- and the first executable reduction block.

---

## 2. Physical motivation

The project has now reached a stage where the main uncertainty is no longer whether a signal exists at all.  
The more important issue is now whether the signal is carried by a small set of physically meaningful variables or by a wider methodological construction that still mixes mechanism and measurement.

This distinction matters because:
- a bridge can only become a physical mechanism if its carrier quantities are isolated,
- robust classification alone is not yet sufficient,
- and reduced H2 transfer already suggests that not all quantities play the same role.

The isolation task is therefore not merely technical feature selection.  
It is a physical discrimination task.

---

## 3. Working categories

For the purpose of this block, quantities are provisionally assigned to one of three categories.

## 3.1 Primary bridge carriers
Variables that appear to carry the actual transitional structure of the bridge.

Expected property:
- removing them should strongly damage or collapse the bridge picture.

## 3.2 Secondary support variables
Variables that may stabilize, sharpen, or extend the bridge picture without carrying its core on their own.

Expected property:
- removing them should weaken the bridge but not destroy it completely.

## 3.3 Diagnostic variables
Variables that mainly evaluate, classify, or summarize the bridge picture rather than physically constituting it.

Expected property:
- removing them should mainly change interpretive reporting, not the underlying bridge structure itself.

---

## 4. Current candidate list

## 4.1 Provisional primary-candidate pool
The following variables are currently treated as the main bridge-carrier candidates:

- `distance_to_type_D`
- `spacing_cv`
- `simple_rigidity_surrogate`
- `grid_deviation_score`

These four currently define the first core isolation block.

## 4.2 Provisional secondary/support pool
The following variables are currently treated as support candidates or candidate proxies:

- `observed_spacing_ratio_mean`
- `distance_to_FSW_intermediate`
- `second_difference_curvature`
- `type_B_model_transfer_value`

These are not part of the first leave-one-out core block, but may become relevant in later support/proxy tests.

## 4.3 Provisional diagnostic pool
The following variables are currently treated as primarily diagnostic or evaluation-layer quantities:

- `type_B_like_pattern_detected`
- `original_stability_score`
- `original_vs_control_margin_delta`
- `assignment_score`
- result labels such as `supported`, `weak`, `failed`
- holdout decision logic
- ranking thresholds and exclusion rules

These should not be confused with physical bridge carriers.

---

## 5. Main test axes

The isolation program will proceed along four main axes.

## 5.1 Axis A — Leave-one-out reduction
Each core candidate is removed individually while all others remain present.

Goal:
- determine whether the candidate is necessary.

Interpretation:
- large degradation suggests primary importance,
- minor degradation suggests secondary importance.

## 5.2 Axis B — Minimal-set identification
Small subsets of candidate variables are tested to determine whether some subset already preserves a recognizable bridge picture.

Goal:
- identify minimal sufficient carrier sets.

Interpretation:
- if a small subset preserves the structure, the bridge may be co-carried by a reduced core.

## 5.3 Axis C — Proxy and replacement tests
Where a candidate is not directly available, a proxy or alternative descriptor is substituted.

Goal:
- determine whether the candidate is physically irreplaceable or only approximately represented by a proxy.

Interpretation:
- if reduced structure survives but full pattern identity is lost, the candidate is likely important and only partially replaceable.

## 5.4 Axis D — Transfer sensitivity
Candidate sets are evaluated not only internally but under H2-style transfer conditions where possible.

Goal:
- distinguish locally useful variables from genuinely transportable bridge carriers.

Interpretation:
- a variable that matters only internally may be less physically central than one that survives transfer.

---

## 6. First executable block: core leave-one-out test

The first concrete block is restricted to the four current core candidates.

### Full core set
- `distance_to_type_D`
- `spacing_cv`
- `simple_rigidity_surrogate`
- `grid_deviation_score`

### Leave-one-out variants
1. full set
2. minus `distance_to_type_D`
3. minus `spacing_cv`
4. minus `simple_rigidity_surrogate`
5. minus `grid_deviation_score`

This first block is intentionally simple and interpretable.

---

## 7. Evaluation logic

Each candidate will be judged according to several dimensions.

### 7.1 Internal structural necessity
Question:
- does removing the variable damage internal separation / transition structure?

### 7.2 H2 relevance
Question:
- does the variable appear necessary for retaining bridge structure under reduced transfer conditions?

### 7.3 Proxy sensitivity
Question:
- can the variable be approximated without severe loss?
- or does proxy substitution preserve only a weakened form?

### 7.4 Role classification
Based on the results, the variable will be tentatively assigned to:
- primary,
- secondary,
- or diagnostic.

---

## 8. Proposed evaluation table

For each tested variable, the following summary table should be filled.

| variable | internal degradation if removed | H2 transfer effect | proxy replaceable | provisional role |
|---|---|---|---|---|
| distance_to_type_D | TBD | TBD | TBD | TBD |
| spacing_cv | TBD | TBD | TBD | TBD |
| simple_rigidity_surrogate | TBD | TBD | TBD | TBD |
| grid_deviation_score | TBD | TBD | TBD | TBD |

Optional later columns:
- effect on corridor geometry
- effect on AO extension visibility
- effect on reduced-H2 stability

---

## 9. Initial working hypotheses

The following hypotheses guide the first block, but must remain testable and revisable.

### H1
`distance_to_type_D` is a primary bridge carrier because it directly encodes position relative to a structural reference type.

### H2
`spacing_cv` is primary or near-primary because it captures regularity versus deviation in the transition corridor.

### H3
`simple_rigidity_surrogate` is likely important and possibly primary, but currently uncertain because proxy usage already exposed its sensitivity under H2 reduced mode.

### H4
`grid_deviation_score` is likely primary or a strong support variable, especially on the AO-side structural extension and jump sectors.

### H5
`type_B_like_pattern_detected` is not a primary carrier but a diagnostic gate variable.

---

## 10. Expected outcomes and interpretations

### Outcome A — strong collapse after removal
Interpretation:
- the removed quantity is likely primary.

### Outcome B — moderate weakening but no collapse
Interpretation:
- the removed quantity is likely secondary or co-supportive.

### Outcome C — little or no change
Interpretation:
- the removed quantity is likely diagnostic or redundant under current conditions.

### Outcome D — reduced mode survives, full pattern fails
Interpretation:
- the removed or proxied quantity is likely physically relevant but not fully replaceable.

---

## 11. Deliverables of this block

This isolation block should produce:

1. a documented leave-one-out result table  
2. a provisional role classification for each core candidate  
3. a short physical interpretation note  
4. a recommendation for the next minimal-set or proxy block

Suggested follow-up files:
- `BRIDGE_CARRIER_ISOLATION_RESULTS.md`
- `bridge_carrier_leave_one_out.csv`
- `BRIDGE_CARRIER_ROLE_ASSIGNMENT_NOTE.md`

---

## 12. Immediate next implementation step

The next implementation step should be a small, transparent execution block that reproduces the current bridge evaluation logic under the five core feature-set variants:

- full set
- minus one variable each

This block should remain as simple as possible and produce:
- one comparison summary per variant,
- directly comparable metrics,
- and a short provisional interpretation.

---

## 13. Bottom line

This specification marks the transition from:
- robust bridge detection

to:
- bridge-carrier isolation.

That is the correct next physical step.

The bridge can only become a credible physical mechanism if the project learns to separate:
- what carries it,
- what stabilizes it,
- and what merely reports on it.
