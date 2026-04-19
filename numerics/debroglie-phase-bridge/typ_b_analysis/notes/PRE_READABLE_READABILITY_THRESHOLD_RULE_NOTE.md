# PRE_READABLE_READABILITY_THRESHOLD_RULE_NOTE

## Threshold rule for the readability-side boundary in the pre-readable first pass

**Date:** 2026-04-07  
**Status:** internal threshold-rule note

---

## 1. Purpose
This note defines the first threshold rule for the readability-side boundary in the pre-readable first pass.

Its purpose is to answer one narrow operational question:

> **When should the readability-side boundary marker count as still weak enough for a case to remain plausibly pre-readable, and when should it count as already crossed?**

This note does not attempt to define a full theory of readability.
It only fixes the first-pass threshold logic.

This is a threshold-rule note, not a result note.

---

## 2. Why this rule is needed
The pre-readable first-pass block already has:

- one organization-side marker:
  - **A1 = structured support coherence**
- one readability-side boundary marker:
  - **`grid_deviation_score`**
- one first comparison rule:
  - pre-readable only if A1 is active while readability remains weak

What was still missing was the explicit threshold rule for the readability side itself.

Without that, the comparison remains incomplete and too vulnerable to narrative drift.

So this rule is mandatory.

---

## 3. Intended role of the threshold rule
The threshold rule is not a broad success metric.
It is a boundary classifier.

Its role is only to decide:

- **readability boundary weak**
or
- **readability boundary crossed**

for the purposes of the first pre-readable pass.

That is its whole role.

---

## 4. Working conceptual distinction
The threshold rule should follow this conceptual distinction:

### Boundary weak
Readable articulation is still not strong enough to count as formed bridge-relevant structure.

### Boundary crossed
Readable articulation has become strong enough that the case should no longer be treated as merely pre-readable.

A shorter version is:

> **Weak = not yet formed enough to read.  
> Crossed = already formed enough to read.**

That is the intended distinction.

---

## 5. Recommended first-pass threshold philosophy
For the first pass, the readability threshold should be:

- **binary**
- **conservative**
- **pre-declared**
- **fixed across cases**
- and **not narratively adjustable**

This is important because the pre-readable block is a first-pass triage block, not a maximally sensitive detector.

So the threshold should not be too permissive.

A case should not count as pre-readable merely because readability is “not maximal.”
It should count as pre-readable only if readability is still clearly below formed-articulation level.

---

## 6. Recommended binary threshold rule
The first-pass readability threshold rule should be:

> **Assign readability boundary = weak only if the chosen readability-side marker (`grid_deviation_score`) remains below a pre-declared readable-articulation threshold strongly enough that the case cannot yet be treated as formed readable bridge structure. Otherwise assign readability boundary = crossed.**

This is the preferred full verbal rule.

A shorter version is:

> **Below threshold = weak.  
> At or above threshold = crossed.**

That is the intended first-pass binary rule.

---

## 7. What “weak” should mean
For the first pass, readability boundary = weak should mean:

- later readable form articulation is still insufficient
- readable structure is still too incomplete, too weak, or too under-formed
- the case still requires inference from deeper structure rather than already presenting itself as formed readable organization

So “weak” should not mean:
- merely moderate
- merely submaximal
- or “not very impressive”

It should mean:
- still below the minimum formed-readability level.

---

## 8. What “crossed” should mean
For the first pass, readability boundary = crossed should mean:

- the readability-side marker is now strong enough to count as formed bridge-relevant articulation
- the case is no longer merely supported by deeper organization but has already become readable as formed structure
- and therefore should no longer receive the positive pre-readable label

So “crossed” is not:
- “perfectly readable in every sense”

It is:
- “already readable enough that pre-readable status is no longer appropriate.”

---

## 9. Why the threshold should be conservative
A conservative threshold is preferable here because false positives are especially costly.

If the threshold is too permissive, then many cases will remain labeled:
- readability weak

even though they are already substantially readable.

That would inflate the pre-readable category and weaken the whole block.

So for the first pass, it is better that:
- some borderline cases are excluded
than that
- too many formed cases are smuggled into the pre-readable bucket.

---

## 10. What the threshold rule must not do
The threshold rule must not become:

### 10.1 A global bridge-quality score
It is not a full summary of how “good” a case is.

### 10.2 A broad ontology classifier
It is not a criterion for appearance, geometry, or large-scale theoretical success.

### 10.3 A post hoc tuning device
It must not be shifted after looking at cases just to rescue a desired interpretation.

### 10.4 A weak narrative judgment
It must not mean:
- “I personally feel this still looks not fully readable”

It has to remain tied to a pre-declared threshold.

These restrictions are essential.

---

## 11. Relationship to A1
The readability threshold rule matters only relative to A1.

The pre-readable logic is not:
- weak readability alone

The real rule is:
- **A1 active**
and
- **readability boundary weak**

So the threshold rule only supplies the readability-side half of the comparison.

By itself, readability weak is not enough for a positive pre-readable assignment.

That must stay explicit.

---

## 12. Recommended first-pass assignment rule
The first-pass comparison should therefore use:

### Plausible pre-readable case
Assign only if:
- **A1 = materially active**
and
- **readability boundary = weak**

### Not pre-readable
Assign if:
- **A1 = weak**
or
- **readability boundary = crossed**

This keeps the block strict.

---

## 13. Main risks of a bad threshold rule
### Risk 1 — Too permissive
Too many cases remain below the readability boundary.

### Risk 2 — Too strict
Almost nothing remains below the boundary, making the pre-readable category practically unusable.

### Risk 3 — Unstable threshold
The threshold is not fixed cleanly enough to be shared across cases.

### Risk 4 — Post hoc adjustment
The threshold gets reinterpreted after seeing whether a case would otherwise qualify.

These risks must be controlled.

---

## 14. Required discipline for the first pass
For the first pre-readable pass, the readability threshold rule must be:

- binary
- conservative
- pre-declared
- fixed across compared cases
- written explicitly into the first-pass record
- and not changed mid-pass

This is mandatory.

---

## 15. Safe summary sentence
A useful internal sentence is:

> The readability boundary should count as weak only when `grid_deviation_score` remains clearly below the minimum formed-articulation threshold; once that threshold is crossed, the case should no longer be labeled pre-readable.

A shorter version is:

> **Pre-readable requires A1 active and readability still below formed-articulation threshold.**

Both are good steering lines.

---

## 16. Bottom line
The first readability threshold rule for the pre-readable block should be:

- **binary**
- **conservative**
- **fixed**
- and based on whether `grid_deviation_score` remains below or crosses the first formed-articulation threshold**

In working first-pass language:

> **Readability boundary = weak only if readable articulation is still below formed level; otherwise the boundary is crossed.**

That is the current first threshold-rule standard for the pre-readable block.
