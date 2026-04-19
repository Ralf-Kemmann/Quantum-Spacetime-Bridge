# DLBSR_CLASS_SCORE_MARGIN_DECISION_NOTE

## Decision note for tightening DLBSR as class, score, or margin

**Date:** 2026-04-07  
**Status:** internal proxy-decision note

---

## 1. Purpose
This note fixes the next narrowing step for the first downstream outcome proxy:

> **Should DLBSR be used in the first pass as a class, a score, or a margin?**

The answer matters because the first compatibility pass should stay:
- narrow,
- interpretable,
- and resistant to inflation.

This note therefore does not just list options.
It recommends an order and a first choice.

---

## 2. The three possible forms

### 2.1 DLBSR-class
A discrete local downstream bridge-support response classification.

Typical forms:
- support-positive / support-negative
- support-positive / borderline / support-negative

This is the simplest first-pass form.

---

### 2.2 DLBSR-score
A continuous local downstream bridge-support response scalar.

Typical meaning:
- larger value = stronger later local bridge-support response
- smaller value = weaker later local bridge-support response

This is richer, but also more interpretation-sensitive.

---

### 2.3 DLBSR-margin
A distance-to-threshold measure.

Typical meaning:
- positive margin = above support threshold
- negative margin = below support threshold
- absolute magnitude = distance from decision boundary

This is useful once a threshold is already trusted.

---

## 3. Decision criteria
The first-pass form should be chosen by the following criteria:

1. **interpretability**
2. **stability**
3. **resistance to over-reading**
4. **fit to first-pass narrowness**
5. **compatibility with later refinement**

The first pass should not begin with the most expressive form.
It should begin with the cleanest one.

---

## 4. Evaluation of DLBSR-class

### Strengths
- simplest to interpret
- easiest to compare against Candidate A and Candidate B
- fits a first-pass triage logic well
- reduces the risk that tiny scalar fluctuations are overinterpreted
- easiest to document in a clean result template

### Weaknesses
- compresses information
- may hide useful gradation
- threshold choice matters

### First-pass suitability
**High**

DLBSR-class is currently the best fit for the first pass because it keeps the downstream target narrow and robust.

---

## 5. Evaluation of DLBSR-score

### Strengths
- richer than class form
- can preserve useful variation
- may reveal weak but real directional differences before a hard class split is visible

### Weaknesses
- easier to narratively overread
- more sensitive to scaling choices
- can make weak drifts look more impressive than they are
- requires stronger discipline in interpretation

### First-pass suitability
**Medium**

DLBSR-score is useful, but better treated as a second-wave refinement once the first pass has already shown that something nontrivial may be there.

---

## 6. Evaluation of DLBSR-margin

### Strengths
- directly tied to a decision boundary
- useful once a threshold is trusted
- can show how near/far a case is from crossing into support-positive status

### Weaknesses
- depends heavily on threshold quality
- too brittle if the threshold is not yet stable
- may create false precision in an early exploratory pass

### First-pass suitability
**Low to medium**

DLBSR-margin is probably premature for the first pass unless the threshold basis is already very well defined.

---

## 7. Recommended first-pass decision
### Recommended first-pass form
> **Use DLBSR-class as the primary first-pass downstream outcome proxy.**

This is the current recommendation.

### Why
Because the first compatibility pass should remain:
- simple enough to reject weak candidates cleanly
- narrow enough not to inflate tiny effects
- and structured enough that Candidate A and Candidate B can be judged against one shared downstream target without unnecessary scalar ambiguity

DLBSR-class satisfies these conditions best.

---

## 8. Recommended working form of DLBSR-class
For the very first pass, the cleanest form is likely:

### Binary form
- **DLBSR-positive**
- **DLBSR-negative**

This is the narrowest clean start.

### Optional ternary extension
Only if needed later:
- **DLBSR-positive**
- **DLBSR-borderline**
- **DLBSR-negative**

The ternary version should not be used unless the binary version proves too crude.

So the preferred current order is:

1. binary DLBSR-class
2. ternary DLBSR-class only if justified
3. DLBSR-score later
4. DLBSR-margin later still

---

## 9. Role of score and margin after the first pass
This note does not reject score or margin forever.
It only sequences them.

### After a useful first pass
If one candidate survives the first pass in a meaningful way, then the next natural refinement order would be:

1. keep DLBSR-class as the anchor
2. add DLBSR-score as a finer descriptive layer
3. add DLBSR-margin only if the threshold basis is stable enough

That is the recommended progression.

---

## 10. Safe first-pass wording
A safe current wording is:

> For the first compatibility-candidate pass, DLBSR should be implemented primarily as a narrow local downstream support-response class rather than as a fully continuous score or threshold margin. This keeps the first pass interpretable, anti-inflationary, and aligned with its triage purpose.

A shorter version is:

> **First pass: DLBSR-class first, score later, margin last.**

---

## 11. Bottom line
The first downstream outcome proxy should now be tightened as follows:

- **Primary first-pass form:** `DLBSR-class`
- **Preferred start:** binary class
- **Optional later extension:** ternary class
- **Second-wave refinement:** `DLBSR-score`
- **Later threshold-sensitive refinement:** `DLBSR-margin`

That is the current best narrowing decision for DLBSR.
