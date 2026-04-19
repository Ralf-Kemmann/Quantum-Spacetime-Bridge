# SPLIT-EVAL NOTE — M.3.9x.3g.b  
## First de-circularized threshold evaluation

**Date:** 2026-04-03  
**Project block:** M.3.9x.3g.b  
**Status:** Internal methodological note  
**Purpose:** Document the first de-circularized threshold evaluation introduced after the Red-Team critique of in-sample calibration.

---

## 1. Motivation

After completion of **M.3.9x.3g.a**, the project reached a protocol-internal `type_B_exclusion_supported` status under the hardened exclusion setup:

- hardened Type-B rule block,
- adversarial controls (`K1a`, `K2a`, `K3a`),
- boundary and fine scans for controls,
- separate original-reference logic,
- calibrated decision thresholds,
- `O2` as primary reference and `O3` as supporting variant.

The strongest remaining critique was that threshold calibration and positive evaluation were still too closely tied to the same project-internal data context. In particular, the concern was that the thresholds could be seen as partly optimized around the same data region in which `O2` and `O3` were later declared successful.

This note documents the first explicit attempt to **reduce that circularity**.

---

## 2. Goal of the split-eval run

The split-eval run was designed to answer the following question:

> Does the positive Type-B exclusion result for `O2` and `O3` persist when threshold calibration is no longer derived directly from the same candidate pair that is later evaluated?

This is **not yet a full external holdout design**.  
Instead, it is a **minimal de-circularization step** inside the current project environment.

---

## 3. Core protocol idea

The split-eval logic separates the workflow into two parts:

### 3.1 Calibration side
Threshold calibration is based on:

- **O1** as the calibration-side original pair
- current control-family summaries

### 3.2 Evaluation side
The calibrated thresholds are then applied to:

- **O2** as the primary evaluation pair
- **O3** as replication / supporting evaluation pair

So the structure is:

- **calibration:** O1
- **evaluation:** O2, O3

This reduces the specific critique that `O2` might only pass because the relevant thresholds were effectively tuned on the same local signal structure.

---

## 4. Implemented logic

The split-eval block was implemented in:

`src/m39x3g_a/threshold_split_eval.py`

### 4.1 Pair definitions

- `O1` = `FSW_D05, FSW_D06` vs `AO_A03, AO_A04, AO_A05`
- `O2` = `FSW_D05, FSW_D06` vs `AO_A04, AO_A05, AO_A06`
- `O3` = `FSW_D05, FSW_D06` vs `AO_A04, AO_A05`

### 4.2 Threshold derivation

#### Margin threshold
The split-eval run first evaluates `O1`, then uses its observed margin as calibration anchor.

The resulting used threshold was:

- `calibrated_margin_threshold = 0.17360190252056484`

This equals the observed `O1` margin in the present run because the calibration input on the original side consisted only of `O1`.

#### Relative-advantage threshold
The relative-advantage threshold was derived from `O1` against the current control-family summaries:

- `calibrated_delta_threshold = 0.1528667928718004`

This threshold is stricter than the earlier in-sample working value of `0.086`.

---

## 5. Results of the split-eval run

### 5.1 Output file
The run produced:

`runs/M39x3g_a_typeB_exclusion/m39x3g_a_run_001/threshold_split_eval.json`

### 5.2 Main result labels

- `O2: type_B_exclusion_supported`
- `O3: type_B_exclusion_supported`

### 5.3 Interpretation

The central result is:

> The positive Type-B exclusion result for `O2` and `O3` survives a first O1-based threshold split-evaluation.

This means the `supported` status is no longer tied only to the earlier O2/O3-near calibration context.

---

## 6. What this step does achieve

This split-eval step **does**:

1. reduce the immediate accusation that `O2` only passes because the thresholds were calibrated too close to `O2`,
2. show that `O2` and `O3` remain positive under a stricter and at least partially separated calibration logic,
3. strengthen the project-internal claim that the positive exclusion result is not purely a threshold-tuning artifact.

---

## 7. What this step does *not* yet achieve

This split-eval step does **not** yet count as a full external validation.

Remaining limitations:

### 7.1 No true out-of-sample independence
Calibration and evaluation still happen within the same overall project dataset universe.

### 7.2 O1 is only a minimal calibration source
Using only `O1` as calibration source is a pragmatic first step, but not a fully mature calibration design.

### 7.3 O3 remains close to O2
`O3` still functions more as a near replication / supporting variant than as a strongly independent robustness case.

### 7.4 No holdout or nested-validation structure yet
The split-eval logic is less circular, but not yet equivalent to a real holdout, nested validation, or transfer validation design.

---

## 8. Current methodological status after split-eval

The most defensible current statement is:

> Under the current hardened protocol, the Type-B exclusion result is supported, and this support survives a first de-circularized O1-based split-evaluation. The result is therefore less tightly tied to the original in-sample threshold context than before, but still remains below a fully independent out-of-sample validation standard.

---

## 9. Recommended wording for internal project use

### Internal concise wording
> A first de-circularized threshold evaluation using O1-based calibration preserves the positive exclusion result for O2 and O3. This weakens the strongest immediate in-sample calibration critique, although full out-of-sample independence is still not achieved.

### Internal expanded wording
> The split-eval run provides a first methodological decoupling between threshold calibration and positive reference evaluation. O2 and O3 remain `type_B_exclusion_supported` when assessed under O1-based calibration, indicating that the positive exclusion result is not merely an artifact of direct O2/O3-near threshold tuning. At the same time, the procedure remains project-internal and should not yet be treated as equivalent to a formal holdout validation.

---

## 10. Next recommended hardening steps

1. **Document this split-eval logic explicitly in the workflow history**
2. **Treat O3 conservatively as a supporting / replication variant**
3. **Add a broader calibration design**
   - more than one calibration-side original condition
4. **Introduce holdout-like or nested validation logic**
5. **Preserve the distinction between**
   - protocol-internal support
   - externally robust confirmation

---

## 11. Bottom line

The split-eval block is a real methodological gain.

It does not finish the validation problem, but it changes the status from:

- “positive only under a strongly in-sample-calibrated setup”

to:

- “positive under the current hardened protocol, and still positive after a first explicit attempt to de-circularize threshold calibration.”

That is a meaningful improvement in project defensibility.
