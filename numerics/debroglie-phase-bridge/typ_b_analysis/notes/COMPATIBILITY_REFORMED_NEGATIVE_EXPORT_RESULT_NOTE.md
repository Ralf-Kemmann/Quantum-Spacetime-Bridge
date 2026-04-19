# COMPATIBILITY_REFORMED_NEGATIVE_EXPORT_RESULT_NOTE

## Result note for the reformed compatibility run on the NPZ-derived negative export

**Date:** 2026-04-08  
**Status:** internal result note

---

## 1. Purpose
This note records the result of the reformed compatibility run on the NPZ-derived negative export.

Its purpose is to document what changed after the A1 anti-stabilization rule was updated from a purely absolute ceiling rule to a joint rule using:

- `a1_score`
- and
- `neighbor_count`

This is a result note, not a design note.

---

## 2. Background
The earlier run on the same negative export produced:

- **A1 = collapsed**
- **B1 = materially active**
- **global outcome = Outcome C**
- **lead candidate = B1**

The focal-unit sweep then showed that this was not a single-focal accident.
It was systematic across the whole negative export:

- A1 collapsed for all focal units
- B1 was materially active for all focal units

The A1 ceiling sweep then showed that the collapse was not caused by weak signal or overlap failure, but by one specific rule effect:

- `a1_score = 1.0`
- with the old rule:
  - `late_stage iff a1_score >= ceiling`

This made A1 collapse automatically whenever the ceiling stayed below 1.0.

---

## 3. Reform that was applied
The A1 anti-stabilization rule was then changed from:

> **late_stage iff a1_score >= a1_stabilization_ceiling**

to:

> **late_stage iff (a1_score >= a1_stabilization_ceiling) AND (neighbor_count >= a1_neighbor_min)**

The first tested project value was:

- **`a1_neighbor_min = 3`**

This reform was motivated by the finding that perfect local coherence inside a tiny immediate shell should not automatically be treated as already late-stage.

---

## 4. Reformed run context
The reformed run was executed on the same NPZ-derived negative export with:

- same export
- same mapping
- same focal unit
- same B1 logic
- same overall compatibility frame

The key changed ingredient was only:

- the A1 anti-stabilization rule

So the comparison is clean and interpretable.

---

## 5. Reformed run result
The reformed run summary is:

- **A1 status:** materially active
- **B1 status:** materially active
- **A1 score:** 1.0
- **A1 neighbor count:** 2
- **B1 relative fragility:** 0.179535
- **global outcome:** Outcome C — Promising pre-stabilization candidate found
- **promotion state:** both candidates promoted
- **lead candidate:** A1_and_B1

This is the new result state.

---

## 6. What changed relative to the earlier run
The most important difference is:

### Earlier run
- A1 collapsed
- B1 carried the run alone

### Reformed run
- A1 is restored as materially active
- B1 remains materially active
- both candidates now survive together

A concise reading is:

> **A1 was restored without sacrificing B1.**

That is the core effect of the reform.

---

## 7. Why A1 was restored
A1 was restored because the reformed rule now recognizes that:

- `a1_score = 1.0`
- inside a neighborhood with
- `neighbor_count = 2`

does **not** yet satisfy the late-stage condition when:

- `a1_neighbor_min = 3`

So the reformed rule no longer treats tiny immediate-shell perfection as automatically persistence-like.

That is exactly the intended effect.

---

## 8. Why B1 remained active
The reform did not weaken B1.

B1 still keeps:

- materially active status
- acceptable anti-overlap separation
- acceptable anti-stabilization status

So the reform did not trade one candidate for the other.

Instead, it changed the run from:

- one-candidate Outcome C

to:

- two-candidate Outcome C

This matters.

---

## 9. Methodical interpretation
The correct interpretation of the reformed result is:

> **The earlier B1-only lead was at least partly an artifact of an over-aggressive A1 ceiling rule in tiny local shells.**

The reformed run now supports a more balanced reading:

- A1 is viable in the negative export
- B1 is also viable in the negative export
- both candidates can coexist under the reformed anti-stabilization logic

This is a stronger and more methodically defensible outcome than the earlier one-sided result.

---

## 10. What the reformed result does not yet prove
Even after the reform, this result still does **not** prove:

- that the reformed rule is already globally optimal
- that `a1_neighbor_min = 3` is universally correct
- that A1 and B1 are equally strong in all exports
- or that Outcome C is already project-wide stable

This note only establishes the new state for:

- the NPZ-derived negative export
- under the tested reformed A1 rule

That limitation must remain explicit.

---

## 11. Recommended current wording
A useful current wording is:

> The reformed negative-export run restores A1 without weakening B1: both candidates are now materially active under the updated anti-stabilization logic, and the run remains in Outcome C.

A shorter version is:

> **A1 restored, B1 retained, Outcome C preserved.**

Both are good steering lines.

---

## 12. Immediate next step
The next correct move after this note is:

> **test the same reformed runner on the NPZ-derived abs and positive exports**

That is the cleanest next validation step because it shows whether the reform:

- only repairs the negative export
or
- generalizes across neighboring export variants

---

## 13. Bottom line
The reformed compatibility run on the NPZ-derived negative export now yields:

- **A1 = materially active**
- **B1 = materially active**
- **global outcome = Outcome C**
- **promotion state = both candidates promoted**

The key result is:

> **A1 was restored by the neighbor-count reform, while B1 remained active.**

This is the current reformed result state for the negative export compatibility run.
