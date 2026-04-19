# H2_DIAGNOSTIC_NOTE — M.3.9x.3g.c
## Diagnostic note on stability logic and relative-advantage logic in the reduced H2 holdout mode

**Date:** 2026-04-04  
**Project block:** M.3.9x.3g.c  
**Status:** Internal methodological diagnostic note  
**Scope:** First H2 holdout based on `M39x3c_ao_model_transfer`

---

## 1. Purpose

This note documents the first diagnostic interpretation of the project-near H2 holdout run carried out with:

- reduced 3-of-4 feature mapping,
- explicit proxy handling for the missing rigidity dimension,
- fixed thresholds inherited from the current hardened protocol.

The goal is not to reclassify the result prematurely, but to identify **which parts of the current logic remain stable under transfer** and which parts become methodologically fragile in the reduced H2 setting.

---

## 2. Observed result

The first H2 holdout run returned:

- `result_label = type_B_exclusion_weak`

This is an important intermediate result:

- the holdout did **not** collapse to `failed`,
- but it also did **not** yet reach `supported`.

The result therefore indicates a **surviving but weakened transfer signal**.

---

## 3. What clearly worked

### 3.1 Control exclusion remained strong
The holdout did **not** fail because controls became Type-B-like.

Observed:
- `control_typeB_like_fraction = 0.0`
- `control_exclusion_ok = true`

Interpretation:
The adversarial control side remained stably negative even in the H2 transfer setting.

### 3.2 Absolute holdout separation remained strong
Observed:
- `original_separation_margin = 0.3562661316335307`
- reference threshold:
  - `reference_original_separation_margin_min = 0.21`

Interpretation:
The holdout signal is not weak in terms of absolute separation.  
The holdout remains clearly separated from controls in the absolute geometric sense.

### 3.3 Assignment remained strong
Observed:
- `original_assignment_score = 1.0`

Interpretation:
The holdout does not look confused or collapsed in assignment space.

---

## 4. Where the holdout remained weak

The weak result is driven by **two specific logic components**:

### 4.1 Stability logic
Observed:
- `original_stability_score = 0.0`
- threshold:
  - `reference_original_stability_score_min = 0.8`

This is the largest single blocking factor.

### 4.2 Relative-advantage logic
Observed:
- `original_vs_control_margin_delta = 0.014468428827182411`
- threshold:
  - `min_original_over_control_margin_delta = 0.086`

Interpretation:
The holdout margin is strong in absolute terms, but the relative advantage over the controls is too small under the present delta rule.

---

## 5. First diagnosis: why the current H2 run became weak

## 5.1 Reduced-mode feature mismatch
The H2 holdout does not use the exact full 4-feature schema of the original protocol.

Current H2 mapping status:
- `distance_to_type_D` → direct
- `spacing_cv` → direct
- `grid_deviation_score` → extracted from payload
- `simple_rigidity_surrogate` → not directly available
- `rigidity_proxy_second_difference_curvature` → exploratory proxy only

This means the H2 run is already operating in a **reduced 3-of-4-plus-proxy regime**.

The current stability logic may still behave as if a full direct-feature Type-B confirmation were being tested.

## 5.2 Possible overbinding of stability to full Type-B detection
The present result suggests that `stability_score` may still be implicitly tied to a **full Type-B-like pattern criterion**, rather than to a more modest **stable holdout separation criterion**.

If true, then the H2 run is penalized for not satisfying the full internal logic under a transfer setup that was already acknowledged as reduced.

## 5.3 Relative delta threshold may not transfer directly
The current relative-advantage threshold (`0.086`) was inherited from the hardened internal protocol.

In the H2 run:
- controls remain negative,
- but they still show high absolute margins in the reduced mapping space.

This means the holdout can remain well separated in absolute terms while still failing the internal relative-delta requirement.

This is not necessarily evidence against the holdout signal itself.  
It may instead indicate that the current relative-advantage rule is too tightly bound to the original internal feature geometry.

---

## 6. What should *not* be done next

This note explicitly recommends **not** reacting by immediately relaxing thresholds ad hoc.

That would be methodologically weak and too close to post hoc adjustment.

In particular, the following should be avoided for now:

- lowering `min_original_over_control_margin_delta` directly because the holdout missed it,
- redefining `supported` after seeing the holdout outcome,
- silently treating the rigidity proxy as equivalent to the real rigidity feature,
- reporting the H2 run as stronger than it currently is.

---

## 7. Recommended diagnostic decomposition

The next task should be a **logic decomposition**, not a cosmetic reinterpretation.

### 7.1 Stability decomposition
Clarify how `original_stability_score` is currently produced.

Questions:
- Is stability currently tied to full Type-B rule satisfaction?
- Is it binary where it should be graded?
- Does reduced-mode proxy usage automatically suppress stability?

### 7.2 Relative-advantage decomposition
Compute additional diagnostic quantities:

- original margin
- control margin mean
- control margin median
- control margin max
- original minus control mean
- original minus control median
- original minus control max
- original rank among controls

This will show whether the weak result is caused by:
- a genuinely poor transfer advantage,
- or a relative-delta rule that is too internal-protocol-specific.

---

## 8. Proposed conceptual split for future H2 handling

The current run suggests that H2 may need its own explicitly documented evaluation layer.

### 8.1 Full internal protocol mode
Used when all four target features are directly present.

### 8.2 Reduced H2 transfer mode
Used when:
- one feature is missing,
- one feature is represented by a proxy,
- or part of the feature space is reconstructed from secondary fields.

In this reduced mode, the protocol should explicitly distinguish between:

- **stable holdout separation**
- and
- **full direct Type-B confirmation**

This distinction is currently not yet formalized enough.

---

## 9. Current defensible interpretation

The most defensible current wording is:

> The first H2 holdout remains above failure and retains strong absolute separation with cleanly negative controls, but it currently reaches only `weak` support because the inherited stability and relative-advantage logic do not yet appear fully adapted to the reduced 3-of-4-plus-proxy transfer setting.

In German project-internal language:

> Der erste H2-Holdout bricht nicht weg, sondern bleibt oberhalb von `failed` und zeigt starke absolute Trennung bei weiter negativer Kontrollseite. Er erreicht derzeit jedoch nur `weak`, weil Stabilitätslogik und Relative-Advantage-Logik offenbar noch nicht sauber auf den reduzierten 3-of-4-plus-Proxy-Transfermodus abgestimmt sind.

---

## 10. Immediate next steps

1. **Diagnose the current stability logic**
   - determine why it collapses to `0.0`

2. **Add relative-advantage diagnostics**
   - compare original vs control mean / median / max margins

3. **Document reduced-mode status explicitly**
   - `reduced_mapping_mode = true`
   - `proxy_rigidity_used = true`

4. **Avoid ad hoc threshold changes**
   - until the logic decomposition is complete

---

## 11. Bottom line

The first H2 holdout is not a failure.

It is a structurally informative weak result:

- transfer signal survives,
- control exclusion survives,
- absolute separation survives,
- but the inherited internal decision logic currently appears too rigid for the reduced H2 transfer regime.

This makes the next task clear:

> **The priority is now to decompose stability logic and relative-advantage logic for reduced-mode H2 evaluation.**
