# COMPATIBILITY_BASELINE_COMPARISON_NOTE

## Baseline-comparison note for first-pass compatibility candidate testing

**Date:** 2026-04-06  
**Status:** internal comparison note

---

## 1. Purpose
This note defines the baseline-comparison logic for first-pass compatibility candidate testing.

Its purpose is to prevent a common self-deception pattern:

> **a candidate looks interesting only because it was never compared against the right baselines**

The current `typ_b_analysis` block already has:
- a minimal compatibility pilot frame,
- an evaluation note for candidates,
- and a priority list for candidate families.

What is still needed is a strict comparison frame:

> **Against what must a compatibility candidate prove itself before it deserves further attention?**

This note defines that frame.

---

## 2. Why baseline comparison is needed
The compatibility layer is currently the largest open mechanism gap in the block.

That makes it especially vulnerable to weak victories such as:
- “it correlates with something”
- “it looks structured”
- “it behaves better than expected”
- “it matches the story”

None of these is enough.

A candidate is only interesting if it survives the correct comparisons.

So this note exists to enforce that discipline.

---

## 3. Central comparison principle
The baseline rule is:

> **A compatibility candidate is only meaningful if it adds non-trivial pre-stabilization value beyond generic overlap, while remaining clearly distinguishable from later stabilization or readability-side signals.**

This means the candidate must survive pressure from both sides:

- from below: overlap-only baseline
- from above: too-late stabilization/form proxies

That is the core comparison logic.

---

## 4. Mandatory comparison layers
Every candidate should be compared against at least the following layers.

## 4.1 Layer A — Overlap-only baseline
This is the lower baseline.

Question:
- what does generic overlap already explain by itself?

Purpose:
- prevent weak candidates from being celebrated just because overlap was never used as the baseline to beat

Interpretation rule:
If the candidate does not meaningfully outperform overlap-only, it should not be promoted.

---

## 4.2 Layer B — Candidate compatibility signal
This is the signal under test.

Question:
- does the candidate add any real predictive or structural value between overlap and later stabilization?

Purpose:
- assess whether the candidate might occupy the missing mechanism layer rather than merely talking around it

This is the target layer.

---

## 4.3 Layer C — Later stabilization proxy
This is the upper boundary comparison.

Typical examples:
- `simple_rigidity_surrogate`
- later bridge-support survival
- or other clearly downstream persistence-style indicators

Question:
- is the candidate genuinely earlier, or is it just a disguised stabilization proxy?

Purpose:
- prevent tautology and late-stage leakage

Interpretation rule:
If the candidate performs well only because it behaves like later stabilization, it is not solving compatibility.

---

## 4.4 Layer D — Optional trivial control proxy
If possible, include one deliberately weak or generic control candidate.

Examples:
- simple local density without structural distinction
- arbitrary smoothed overlap average
- naive scalar derived from overlap magnitude alone

Question:
- does the proposed candidate beat a trivial “nice-looking” proxy too?

Purpose:
- avoid giving credit to candidates that are merely prettier versions of weak baselines

This layer is optional but strongly recommended.

---

## 5. Required comparison questions
For each compatibility candidate, ask the following in order:

### 5.1 Does it beat overlap-only?
If not, stop.

### 5.2 Is it computable early enough?
If not, stop.

### 5.3 Does it remain distinct from later stabilization?
If not, stop.

### 5.4 Is its direction interpretable?
If not, downgrade heavily.

### 5.5 Does it remain useful against a trivial control proxy?
If not, treat it with caution.

This sequence should be respected.

---

## 6. What “beating overlap” should mean
“Better than overlap” must not remain vague.

At minimum, the candidate should do one of the following:

- improve prediction of later bridge-support behavior
- separate success/failure cases more clearly than overlap-only
- reveal structured distinctions that overlap-only leaves blurred
- remain useful where overlap-only becomes too generic

A tiny correlation bump with no structural meaning is not enough.

---

## 7. What “remaining distinct from stabilization” should mean
A candidate remains distinct from stabilization only if:

- it can be computed earlier
- it does not require later bridge outcome information
- it does not behave like a thin rescaling of `simple_rigidity_surrogate`
- and its usefulness does not vanish once the timing is restricted to pre-stabilization information

If these conditions are not met, the candidate is likely just late-stage leakage.

---

## 8. Suggested comparison outcomes
A candidate comparison should end in one of the following outcomes.

## 8.1 Fails lower baseline
Meaning:
- overlap-only already does as much or more

Safe wording:
> The candidate does not currently add meaningful value beyond generic overlap.

---

## 8.2 Fails upper boundary
Meaning:
- the candidate appears useful only because it has collapsed into later stabilization

Safe wording:
> The candidate is not cleanly separable from later stabilization and should not currently be treated as a compatibility signal.

---

## 8.3 Beats overlap, but remains fragile
Meaning:
- some incremental value exists
- but the gain is weak, threshold-sensitive, or poorly interpretable

Safe wording:
> The candidate shows some incremental value beyond overlap-only, but remains too fragile for strong use.

---

## 8.4 Beats overlap and stays earlier than stabilization
Meaning:
- the candidate adds non-trivial value
- and remains plausibly pre-stabilization

Safe wording:
> The candidate survives the baseline comparison and qualifies as a promising pre-stabilization compatibility signal for further testing.

This is the strongest currently acceptable outcome.

---

## 9. Comparison table template
A simple internal comparison table should ideally include columns like:

| Candidate | Earlier than stabilization? | Beats overlap-only? | Distinct from rigidity-side proxy? | Trivial control beaten? | Interpretation |
|---|---|---|---|---|---|

This table is recommended whenever more than one candidate is being reviewed.

---

## 10. What this note forbids
This comparison note forbids the following moves:

- evaluating a candidate without overlap-only comparison
- declaring a candidate useful because it correlates with later success
- ignoring whether the candidate is actually earlier than stabilization
- comparing only against weak straw-man baselines
- treating visual plausibility as evidence

These are invalid comparison habits.

---

## 11. Recommended immediate workflow
A good first-pass workflow is:

### Step 1
Select one Tier-1 candidate family.

### Step 2
Define the overlap-only baseline explicitly.

### Step 3
Define one later stabilization proxy explicitly.

### Step 4
If possible, define one trivial control proxy.

### Step 5
Ask whether the candidate:
- beats overlap,
- stays earlier than stabilization,
- and resists trivial-proxy dilution.

Only then decide whether the candidate deserves further work.

---

## 12. Short internal steering sentence
A useful internal sentence is:

> **A compatibility candidate must prove itself against overlap from below and against rigidity from above.**

A second good sentence is:

> **If it cannot beat overlap, it is too weak. If it cannot stay earlier than rigidity, it is too late.**

Both should remain active guidance.

---

## 13. Bottom line
The compatibility layer should not be approached with free-floating candidate enthusiasm.

Every candidate must survive a structured baseline comparison:

- overlap-only baseline
- candidate signal
- later stabilization proxy
- optional trivial control proxy

Only candidates that:
- outperform overlap-only,
- remain earlier than stabilization,
- and stay structurally interpretable

deserve promotion into further pilot work.

That is the current baseline-comparison standard.
