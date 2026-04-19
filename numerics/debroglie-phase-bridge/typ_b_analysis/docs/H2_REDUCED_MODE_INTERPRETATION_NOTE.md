# H2_REDUCED_MODE_INTERPRETATION_NOTE — M.3.9x.3g.c
## Interpretation note for the reduced H2 holdout mode

**Date:** 2026-04-04  
**Project block:** M.3.9x.3g.c  
**Status:** Internal methodological interpretation note  
**Scope:** First H2 holdout based on `M39x3c_ao_model_transfer`

---

## 1. Purpose

This note provides an explicit interpretation layer for the first H2 holdout under the currently active **reduced 3-of-4-plus-proxy mapping mode**.

Its purpose is not to redefine the official result label, but to document clearly how the H2 result should be read under two distinct views:

1. the inherited **full-protocol interpretation**, and  
2. the additional **reduced H2 diagnostic interpretation**.

This distinction is necessary because the first H2 holdout does not behave like a failed signal, but it also does not pass the inherited full internal Type-B gate.

---

## 2. Official result under the inherited full protocol

The first H2 holdout returned:

- `result_label = type_B_exclusion_weak`

This official result remains valid under the inherited current decision logic.

In that logic, the H2 run does **not** reach `supported`, because:

- `original_stability_score = 0.0`
- `original_vs_control_margin_delta = 0.014468428827182411`
- required delta threshold:
  - `0.086`

Thus, under the inherited full-protocol reading, the holdout remains:

> **weak, but not failed**

---

## 3. Reduced H2 context

The same run explicitly documents that it was executed under a reduced mapping condition:

- `reduced_mapping_mode = true`
- `proxy_rigidity_used = true`
- `direct_feature_count = 3`
- `proxy_feature_count = 1`

Missing direct feature before proxy fill:
- `simple_rigidity_surrogate`

This means the H2 run was never a full direct 4-feature reproduction of the internal protocol.

It was from the beginning a **project-near transfer test under reduced feature conditions**.

This reduced-mode status must therefore be part of the interpretation.

---

## 4. What remains strong in reduced H2 mode

Despite the official `weak` result, the holdout retains several clearly positive properties.

### 4.1 Absolute separation remains strong
Observed:
- `original_separation_margin = 0.3562661316335307`

Reference threshold:
- `reference_original_separation_margin_min = 0.21`

Interpretation:
The H2 holdout is not weak in absolute geometric separation.

### 4.2 Assignment remains strong
Observed:
- `original_assignment_score = 1.0`

Interpretation:
The holdout remains perfectly separable in assignment space.

### 4.3 CI-based stability components remain positive
The stability trace shows:

- all margin pass flags = `true`
- all assignment pass flags = `true`
- all CI-low pass flags = `true`

Interpretation:
The holdout does not collapse at the level of margin, assignment, or CI support.

---

## 5. The key split between full-protocol and reduced-H2 interpretation

The decisive difference is this:

### 5.1 Full-protocol stability
Observed:
- `original_stability_score = 0.0`

This score remains the active one under the inherited protocol and keeps the result at `weak`.

### 5.2 Reduced-H2 diagnostic stability
Observed:
- `reduced_h2_stability_score = 1.0`

Diagnostic components:
- `component_mean_margin_pass = 1.0`
- `component_mean_assignment_pass = 1.0`
- `component_mean_ci_low_pass = 1.0`

Interpretation:
If stability is read only as stable separation/assignment/CI support, then the holdout appears fully stable.

Thus:

> The weak result is not caused by loss of transfer signal quality in general, but by the inherited full-protocol stability gate.

---

## 6. Localization of the current weakness

The stability trace shows:

- `any_type_B_like_pattern_detected = false`

At the same time, likely zeroing candidates are:

- `reduced_mapping_mode_active`
- `proxy_rigidity_used`
- `single_group_holdout_reference`
- `very_small_holdout_reference`
- `no_type_B_like_pattern_detected_in_resampling_outputs`

This localizes the problem:

> The first H2 holdout does not currently fail at the level of signal separation.  
> It remains weak because the inherited full internal Type-B pattern gate does not fire under reduced H2 conditions.

---

## 7. Defensible interpretation

The current defensible project-internal interpretation is therefore:

### 7.1 Under the inherited full protocol
The H2 holdout remains:
- `type_B_exclusion_weak`

This remains the official result.

### 7.2 Under the reduced H2 diagnostic layer
The same holdout shows:
- strong absolute separation
- perfect assignment
- positive CI-based stability components
- diagnostic reduced-H2 stability = `1.0`

This means:

> The transfer signal survives structurally, even though the inherited full-pattern gate is not met.

---

## 8. What should *not* be claimed

This note does **not** justify the following claims:

- that the H2 holdout is already `supported`,
- that reduced-H2 stability should automatically replace official stability,
- that the proxy rigidity variable is equivalent to the original rigidity feature,
- that the current weak result can simply be reclassified without further methodological work.

That would go too far.

---

## 9. What *can* now be claimed defensibly

The following claims are now methodologically defensible:

1. The first H2 holdout is **not a failure**.
2. The first H2 holdout preserves **strong absolute separation**.
3. The first H2 holdout preserves **strong assignment structure**.
4. The current weakness is localized to the inherited **full-protocol Type-B-pattern gate**.
5. The reduced H2 diagnostic layer shows that the transfer signal remains **structurally stable**, even though the full gate is not met.

---

## 10. Recommended project wording

### English
> The first H2 holdout remains classified as `type_B_exclusion_weak` under the inherited full-protocol logic. However, reduced-mode diagnostics show that absolute separation, assignment, and CI-based stability components remain fully positive. The current weakness is therefore localized to the inherited Type-B-pattern gate rather than to a general collapse of the transfer signal.

### German
> Der erste H2-Holdout bleibt unter der geerbten Vollprotokoll-Logik bei `type_B_exclusion_weak`. Die reduced-mode-Diagnostik zeigt jedoch, dass absolute Separation, Assignment und CI-basierte Stabilitätskomponenten vollständig positiv bleiben. Die aktuelle Schwäche ist damit am geerbten Type-B-Pattern-Gate lokalisiert und nicht an einem allgemeinen Kollaps des Transfersignals.

---

## 11. Bottom line

The first H2 holdout should currently be read in a **two-layer way**:

- **officially:** `weak`
- **diagnostically:** structurally stable reduced-mode transfer signal

This distinction is the correct defensive reading at the current stage.

It preserves both:
- honesty about the official result,
- and clarity that the H2 signal itself did not collapse.

---

## 12. Immediate next implication

The next methodological question is no longer:

> “Did the H2 signal survive at all?”

That question is now largely answered.

The next question is:

> **How should reduced-mode H2 transfer evidence be integrated without confusing it with full direct 4-feature internal confirmation?**
