# COMPATIBILITY_LAYER_MINIMAL_PILOT_NOTE

## Minimal pilot note for first operational work on the compatibility layer

**Date:** 2026-04-06  
**Status:** internal mechanism pilot note

---

## 1. Purpose
This note defines the smallest useful pilot frame for working on the compatibility layer.

The goal is deliberately narrow.

It is **not**:
- to claim that compatibility has already been found,
- to close the bridge mechanism,
- or to identify a final metric.

It is only:

> **to define a first operational search frame for a pre-stabilization compatibility signal that is not reducible either to generic overlap or to already-achieved stabilization.**

That is the correct scope.

---

## 2. Why this pilot is needed
The current `typ_b_analysis` block already supports several things quite strongly:

- overlap alone is not enough
- `simple_rigidity_surrogate` is likely too late to count as compatibility itself
- `grid_deviation_score` is even later, more plausibly on the form / readability side
- the bridge therefore appears to require an intermediate selection layer

That intermediate layer is what the project currently calls:
- the **compatibility layer**

At present, however, the compatibility layer is:
- conceptually necessary
- but still operationally missing

This makes it the largest open mechanism gap in the current block.

---

## 3. Minimal pilot question
The pilot should answer only this:

> **Can any candidate pre-stabilization signal predict later bridge-supporting behavior better than generic overlap alone, without merely re-labeling later stabilization?**

This is the core question.

If the answer is yes, the project gains its first bridge toward a real compatibility metric family.
If the answer is no, that is also useful: it means the gap is still genuinely open.

---

## 4. What compatibility is currently supposed to mean
The current best internal reading is:

- **overlap** tells us that relational presence or proximity exists
- **compatibility** would tell us whether some of that overlap is jointly supportable as a common intermediate mode
- **stabilization** tells us that such a mode has actually acquired persistence
- **form / readability** tell us that the stabilized mode has become structured and visible enough to interpret

So compatibility is:
- later than overlap
- earlier than stabilization
- and not identical with either

That ordering is central.

---

## 5. The main danger: tautology
The biggest methodological danger is simple and severe:

> **A compatibility proxy is useless if it merely re-describes the later stabilization result.**

Examples of invalid “solutions”:
- a metric that is basically a disguised version of `simple_rigidity_surrogate`
- a proxy that is computed only after the bridge has already stabilized
- a candidate that predicts survival only because it already contains survival information

This would not discover compatibility.
It would only rename the outcome.

So the pilot must explicitly protect against tautology.

---

## 6. Minimal no-go rule
A candidate compatibility signal should be rejected if:

- it is only computable after stabilization has already occurred
- it correlates with later bridge support only because it already encodes stabilization
- it performs no better than generic overlap
- or it collapses into a later form/readability measure

This is the pilot’s most important rejection rule.

---

## 7. Candidate search space
The pilot should not begin with one alleged solution only.
It should begin with a small candidate space.

At present, the following three candidate directions look plausible enough for first-pass testing.

---

## 7.1 Candidate family A — Pre-stabilization local coherence
This family asks whether compatibility may show up as some local relational consistency before full stabilization.

Possible directions:
- local sign consistency
- local phase-sector consistency
- neighborhood coherence
- directional support agreement across nearby overlap structure

Why this family is interesting:
It sits naturally between:
- mere overlap
and
- achieved persistence

Main risk:
These signals may still collapse either into noisy overlap descriptors or into hidden stability readouts.

---

## 7.2 Candidate family B — Removal sensitivity near the bridge-support layer
This family asks whether compatibility may be inferred from sensitivity structure.

Idea:
- take a bridge-supporting configuration
- remove or weaken selected overlap relations
- identify which removals disproportionately damage later bridge-support behavior

Why this family is interesting:
It may reveal which overlap relations were not merely present, but structurally important.

Main risk:
If done too late in the pipeline, this becomes only a disguised stabilization analysis rather than a true pre-stabilization compatibility signal.

So timing matters.

---

## 7.3 Candidate family C — Sector contrast / structured asymmetry
This family asks whether compatibility may show up through structured sector differences.

Possible directions:
- positive / negative sector contrast
- phase or sign asymmetry patterns
- sector-balanced versus sector-conflicted overlap environments

Why this family is interesting:
Earlier project work already suggested that sign structure can matter strongly.

Main risk:
Sector signals are easy to overread and may be highly model-sensitive.
So this family should be treated as exploratory, not privileged.

---

## 8. Minimal pilot success condition
The pilot should count as provisionally successful if a candidate signal satisfies all of the following:

### 8.1 Pre-stabilization computability
It can be computed before later stabilization/readability outcomes are already known.

### 8.2 Non-triviality
It predicts later bridge-support-related behavior better than generic overlap alone.

### 8.3 Non-collapse
It is not merely a re-labeling of `simple_rigidity_surrogate` or later morphology/readability measures.

### 8.4 Interpretive clarity
Its direction makes structural sense:
- higher value meaningfully corresponds to greater supportability
or
- lower value meaningfully corresponds to stronger incompatibility

This would already be a major step.

---

## 9. Minimal pilot non-success condition
The pilot should count as non-successful if all candidate signals fail in one of the following ways:

- they do not outperform generic overlap
- they only correlate after stabilization is already known
- they collapse into later bridge-survival metrics
- they are too noisy or inconsistent to interpret
- they depend mainly on arbitrary thresholding or fragile implementation choices

This would not be a disaster.
It would simply mean:
- compatibility remains open
- and the current conceptual gap is real, not yet solved

That is still valuable knowledge.

---

## 10. Minimal data logic
The pilot should compare at least three layers:

### Layer 1 — Generic overlap baseline
What does simple overlap already tell us?

### Layer 2 — Candidate compatibility signal
What extra predictive structure does the candidate add?

### Layer 3 — Later outcome proxy
What later bridge-support/stabilization behavior is being predicted?

This three-layer comparison is necessary to avoid cheating.

---

## 11. Minimal interpretation discipline
The correct interpretation order should be:

1. Can the candidate be computed early enough?
2. Does it beat overlap-only?
3. Does it remain distinct from later stabilization?
4. Does it generalize at least weakly across the tested cases?

Only after that should one even tentatively call it a compatibility candidate.

Not before.

---

## 12. Recommended first pilot attitude
The right attitude for this pilot is:

- do not search for “the” compatibility metric
- search for whether the compatibility layer can begin to become operationally visible at all

This is a first-visibility pilot, not a closure pilot.

That distinction is important.

---

## 13. Immediate next test path
A reasonable next test path would be:

### Step 1
Choose one narrow case family where bridge-supporting behavior is already visible.

### Step 2
Define:
- one overlap baseline
- one or two candidate compatibility signals

### Step 3
Compare whether the candidate improves prediction of later support/stabilization behavior.

### Step 4
Reject immediately if the candidate is obviously too late or tautological.

This is enough for a first pilot block.

---

## 14. Safe summary sentence
A useful internal summary sentence is:

> The compatibility-layer pilot should not try to solve the missing mechanism in one step. It should only test whether any pre-stabilization signal can begin to predict later bridge-supporting behavior better than generic overlap, without collapsing into already-achieved stabilization.

A shorter version is:

> **Compatibility first becomes interesting where overlap stops being enough but stabilization has not yet begun to speak for itself.**

---

## 15. Bottom line
The compatibility layer is currently the largest open mechanism gap in the `typ_b_analysis` block.

The correct next move is not to overstate it, but to probe it narrowly:

- start with a small candidate space
- protect against tautology
- compare against overlap-only
- and ask whether any pre-stabilization signal gains real predictive value

That is the correct role of a minimal compatibility-layer pilot.
