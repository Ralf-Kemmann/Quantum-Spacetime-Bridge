# EXPORT_CLASS_ROBUSTNESS_MINI_SERIES_V1_RESULT_NOTE

## Result note for the first export-class robustness mini-series

**Date:** 2026-04-08  
**Status:** internal result note

---

## 1. Purpose
This note records the current result state of **Export-class robustness mini-series v1**.

Its purpose is to consolidate the first small robustness program for the current compatibility framework across the NPZ-derived export classes:

- **negative**
- **abs**
- **positive**

This is a result note, not a new methods note.

---

## 2. Starting comparison picture
Before the mini-series, the working comparison picture was:

- **negative:** launchable, strongest case, dual-candidate compatible after the reformed A1 rule
- **abs:** launchable, intermediate case, B1-led in the first direct run
- **positive:** not launchable under the current local-neighbor rule

The mini-series was designed to test whether this picture survives:
- focal variation
- small parameter variation
- explicit positive-boundary confirmation

---

## 3. Block A — focal robustness

### 3.1 Negative export
Under the **reformed** A1 rule, the negative focal sweep produced:

- **A1 materially active:** 4 / 4
- **B1 materially active:** 4 / 4
- **collapsed:** 0 / 4 for both candidates

All four focal units showed the same qualitative result:

- A1 active
- B1 active
- no collapse
- no ambiguity

This means the negative export is **focally stable and dual-candidate compatible** under the reformed rule.

A concise reading is:

> **negative focal robustness = strong and uniform**

---

### 3.2 Abs export
The abs focal sweep produced a mixed but interpretable pattern:

- **A1 materially active:** 2 / 6
- **A1 weak:** 4 / 6
- **A1 collapsed:** 0 / 6

- **B1 materially active:** 2 / 6
- **B1 weak:** 4 / 6
- **B1 collapsed:** 0 / 6

The focal pattern is not random.
Instead it separates into structured local roles:

- some focal units are more coherence-supportive
- some are more fragility-supportive
- some are weak for both candidates

So the abs export is **focally sensitive but still interpretable**.

A concise reading is:

> **abs focal robustness = mixed but structured**

---

### 3.3 Positive export
The positive export was confirmed as:

- **not launchable under the current local-neighbor rule**

Reason:

- only two pair-units are present
- they do not share endpoints
- therefore no immediate local shell exists

So the positive export remains outside the launchable domain of the current compatibility runner.

A concise reading is:

> **positive boundary = no-local-shell confirmed**

---

## 4. Block B — small parameter robustness

### 4.1 Negative export
The negative export was tested across the small parameter grid:

- `a1_stabilization_ceiling = 0.85, 0.95`
- `a1_neighbor_min = 3, 4`
- `b1_conflict_penalty = 1.0, 1.25`

Across **all** tested combinations, the result remained unchanged:

- **A1 active in all focals**
- **B1 active in all focals**
- **Outcome C in all focals**
- **A1_and_B1 promotion in all focals**

So the negative export is not only focally stable, but also **small-parameter stable** within the tested v1 grid.

A concise reading is:

> **negative parameter robustness = very strong**

---

### 4.2 Abs export
The abs export was tested on the same small parameter grid.

The key pattern remained stable:

- **A1 active count stayed at 2**
- **A1 weak count stayed at 4**
- **A1 collapsed count stayed at 0**

So A1 remained a partially active but non-collapsing candidate.

For B1, the relevant variation came from:

- `b1_conflict_penalty`

At:
- `b1_conflict_penalty = 1.0`
  - **B1 active count = 2**
  - **B1 weak count = 4**

At:
- `b1_conflict_penalty = 1.25`
  - **B1 active count = 4**
  - **B1 weak count = 2**

So B1 becomes stronger under slightly higher conflict penalty, but the export does not collapse into noise.
It remains a structured intermediate case.

A concise reading is:

> **abs parameter robustness = structured and interpretable, with meaningful B1 sensitivity**

---

## 5. Consolidated export-class reading

### Negative
- launchable
- focally stable
- parameter stable in v1
- A1 active
- B1 active

**Reading:** strongest current compatibility case

---

### Abs
- launchable
- focally mixed but interpretable
- parameter-sensitive but structured
- A1 partially active
- B1 partially to clearly active depending on conflict penalty

**Reading:** intermediate compatibility case

---

### Positive
- not launchable under the current local-neighbor rule
- no local shell
- boundary result confirmed

**Reading:** non-launchable boundary class under current rule

---

## 6. Main result statement
The main result of mini-series v1 is:

> **The export-class pattern remains visible under small controlled robustness checks.**

More concretely:

- the negative export stays the strongest case
- the abs export remains intermediate rather than collapsing into noise
- the positive export remains outside the current launchable domain

This is the core result.

---

## 7. Most defensible current interpretation
The most defensible current interpretation is:

> **The present compatibility framework carries real structural signal and retains a nontrivial export-class ordering under small robustness tests. The negative class is robustly strongest, the abs class is robustly intermediate though internally mixed, and the positive class remains non-launchable under the current neighborhood rule.**

A shorter version is:

> **negative robust, abs structured intermediate, positive boundary non-launchable**

That is the best current summary sentence.

---

## 8. What mini-series v1 does not yet prove
Even after this result, mini-series v1 still does **not** prove:

- that the current neighborhood rule is final
- that the export conversion is final
- that the observed ordering is universal
- that the A1/B1 candidate logic is already fully stabilized

This is still an early but now substantially better supported operational result.

That limitation should remain explicit.

---

## 9. Why this matters
This matters because the framework is now doing something much stronger than producing one lucky run.

It now shows:

- class-sensitive structure
- focal robustness in the strongest class
- parameter robustness in the strongest class
- structured focal/parameter sensitivity in the intermediate class
- and a clean non-launch boundary in the positive class

That is exactly the kind of behavior that supports continued serious testing rather than dismissal as an arbitrary construction.

---

## 10. Recommended conclusion line
A disciplined conclusion line for the present state is:

> **Export-class robustness mini-series v1 supports the claim that the current compatibility framework already has operational form: the negative class is robustly strongest, the abs class is an interpretable intermediate case, and the positive class remains a non-launchable boundary case under the present rule.**

A shorter steering line is:

> **The theory keeps its export-class form under small v1 robustness tests.**

---

## 11. Immediate next step
The next correct step after this result note is:

> **decide whether to open a separate methodological branch for an alternative positive-export neighborhood rule, while keeping the current v1 result line unchanged**

That is now the clean next decision point.

---

## 12. Bottom line
Mini-series v1 yields a clear current result:

- **negative:** robustly dual-candidate and stable
- **abs:** robustly intermediate and structured
- **positive:** robustly non-launchable under the current rule

So the present compatibility framework now passes a first small but meaningful robustness test.

This is the current result state of export-class robustness mini-series v1.
