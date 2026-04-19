# H2_STABILITY_TRACE_NOTE — M.3.9x.3g.c
## Trace note on the stability collapse in the reduced H2 holdout mode

**Date:** 2026-04-04  
**Project block:** M.3.9x.3g.c  
**Status:** Internal methodological trace note  
**Scope:** First H2 holdout based on `M39x3c_ao_model_transfer`

---

## 1. Purpose

This note isolates the currently most critical technical question in the first H2 holdout run:

> Why does the H2 holdout produce `original_stability_score = 0.0` although absolute separation and assignment remain strong?

The purpose is not to redefine the result, but to document the stability-collapse problem explicitly and prepare a targeted trace analysis of the inherited scoring logic.

---

## 2. Immediate empirical observation

In the first H2 holdout run, the following values were observed:

- `result_label = type_B_exclusion_weak`
- `original_separation_margin = 0.3562661316335307`
- `original_assignment_score = 1.0`
- `original_stability_score = 0.0`

This combination is highly informative:

- the holdout is **not** weak in absolute separation,
- the holdout is **not** weak in assignment,
- but the stability score collapses completely.

This indicates that the weak result is not driven by general collapse of the holdout signal, but by a specific part of the inherited stability logic.

---

## 3. Reduced-mode context

The same H2 run explicitly shows:

- `reduced_mapping_mode = true`
- `proxy_rigidity_used = true`
- `direct_feature_count = 3`
- `proxy_feature_count = 1`

The only missing direct feature before proxy fill was:

- `simple_rigidity_surrogate`

This means the H2 holdout was **not evaluated under the full direct 4-feature protocol**, but under a reduced 3-of-4-plus-proxy regime.

This is methodologically important because the inherited stability logic may still behave as if a full direct Type-B feature space were available.

---

## 4. Core diagnostic question

The central question is now:

> Does the current `stability_score` measure stable holdout separation, or does it implicitly require full internal Type-B pattern confirmation?

If the latter is true, then the reduced H2 mode is structurally disadvantaged from the start.

---

## 5. Current working hypotheses

## 5.1 Hypothesis A — stability is effectively tied to `type_B_like_pattern_detected`
The most likely first hypothesis is that `stability_score` depends directly or indirectly on whether a full Type-B-like pattern is detected under the inherited rule block.

If that pattern detector assumes:
- all direct features present,
- no proxy substitution,
- no reduced mapping mode,

then reduced H2 runs may systematically fall to zero stability even when separation remains strong.

## 5.2 Hypothesis B — stability is binary where it should be graded
Another possibility is that the current stability logic behaves as a near-binary pass/fail quantity rather than a graded stability measure.

In that case, the reduced H2 run may miss one internal criterion and therefore collapse entirely to zero, even if most evidence remains positive.

## 5.3 Hypothesis C — proxy usage silently suppresses stability
A third possibility is that the use of a proxy feature (`rigidity_proxy_second_difference_curvature`) does not itself break the pipeline, but still prevents a positive stability classification because the proxy is treated as formally non-equivalent to the original feature.

This would be consistent with:
- strong separation,
- strong assignment,
- but zero stability.

## 5.4 Hypothesis D — resampling logic is incompatible with very small holdout structure
The H2 holdout currently contains:
- `dataset_count = 3`
- `group_labels = ["AO"]`

It is possible that the inherited resampling-based stability definition expects a richer internal group structure and collapses under a very small or one-sided holdout reference.

---

## 6. What is already known

The current diagnostics already make a few things clear:

### 6.1 Stability collapse is not caused by weak separation
The margin is clearly above threshold.

### 6.2 Stability collapse is not caused by weak assignment
Assignment is perfect (`1.0`).

### 6.3 Stability collapse is therefore a logic-level effect
This means the relevant issue is almost certainly:
- rule composition,
- binary gating,
- proxy incompatibility,
- or resampling structure.

---

## 7. What must now be traced explicitly

The next technical task is to trace the exact path by which `stability_score` is produced.

The trace should answer:

1. Which function computes `stability_score`?
2. Which intermediate conditions feed into it?
3. Is `type_B_like_pattern_detected` a direct gate?
4. Is the score continuous or binary?
5. Which exact condition forces the value to `0.0` in the current H2 run?
6. Does reduced-mode proxy usage enter the logic explicitly or implicitly?

---

## 8. Recommended trace output to add

For the next patch, the following trace variables should be recorded if possible:

- `stability_input_type_B_like_pattern_detected`
- `stability_input_assignment_score`
- `stability_input_separation_margin`
- `stability_input_ci_low`
- `stability_input_feature_rule_pass_count`
- `stability_input_proxy_rigidity_used`
- `stability_input_reduced_mapping_mode`
- `stability_zeroing_condition`
- `stability_raw_value_before_gating`
- `stability_final_value`

This would transform the current black-box zero into a transparent decision path.

---

## 9. Interpretation discipline

This note recommends **not** concluding yet that the H2 holdout is intrinsically unstable.

At present, the better reading is:

> The current stability metric is not yet interpretable in the reduced H2 mode because the logic that produces the zero value has not yet been decomposed.

This distinction matters:
- “H2 is unstable” would be too strong.
- “The current inherited stability logic collapses in H2 reduced mode” is the more defensible statement.

---

## 10. Current defensible wording

### Internal concise wording
> The first H2 holdout does not show a general collapse of signal quality. Instead, stability collapses specifically to zero under the inherited full-protocol logic, despite strong absolute separation and perfect assignment. The next task is therefore an explicit trace of the stability computation.

### Internal expanded wording
> The weak H2 result is currently driven primarily by a complete stability collapse (`0.0`) rather than by a loss of separation or assignment. Because the same run was executed in reduced 3-of-4-plus-proxy mode, the most likely explanation is that the inherited stability logic is still too tightly bound to the full internal Type-B confirmation structure. This must now be traced explicitly before any further interpretive or threshold-level changes are considered.

---

## 11. Bottom line

The first H2 holdout has isolated a very specific bottleneck:

> **The main unresolved problem is not whether a transfer signal exists, but why the inherited stability logic collapses to zero in the reduced H2 mode.**

This makes the next methodological step clear:

- trace the stability computation,
- identify the zeroing condition,
- only then decide whether a reduced-mode stability definition is needed.
