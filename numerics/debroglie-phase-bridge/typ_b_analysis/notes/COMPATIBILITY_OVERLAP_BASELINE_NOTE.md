# COMPATIBILITY_OVERLAP_BASELINE_NOTE

## Overlap-only baseline for first-pass compatibility candidate comparison

**Date:** 2026-04-07  
**Status:** internal baseline note

---

## 1. Purpose
This note defines the overlap-only baseline for the first-pass compatibility-candidate comparison block.

Its purpose is to answer one narrow but essential question:

> **What counts, in the current project, as mere overlap before any compatibility-side, stabilization-side, or readability-side enrichment is allowed in?**

This matters because the first compatibility pass is only meaningful if Candidate A and Candidate B are tested against a baseline that is:

- simple enough,
- early enough,
- and weak enough

to count as genuine overlap-only.

This is a baseline note, not a result note.

---

## 2. Why the overlap baseline must be explicit
The compatibility layer currently sits in the gap between:
- generic overlap
and
- later stabilization / form

That means the lower comparison boundary is not optional.
It must be fixed explicitly.

Without this, several bad things can happen:
- the baseline drifts from run to run
- overlap gets smuggled full of hidden structure
- candidates look better than they are because they face a weak or vague comparator
- and “compatibility” starts to mean whatever overlap could already explain

So the overlap baseline is part of the anti-inflation discipline.

---

## 3. Intended role of the overlap-only baseline
The overlap-only baseline is meant to represent:

- relational presence
- descriptive availability
- raw local connectedness or magnitude

and nothing more.

Its role is not to explain:
- why some overlap becomes jointly supportable
- why some relations later stabilize
- why some structures later acquire form
- or why a bridge later becomes readable

It is only the descriptive lower floor.

---

## 4. What the overlap-only baseline is allowed to contain
The baseline may include only early, simple overlap-side information such as:

- direct overlap magnitude
- local overlap strength
- simple local overlap-derived scalar
- local overlap presence / intensity without structural enrichment

This keeps the baseline in the correct place:
- early
- descriptive
- non-selective

---

## 5. What the overlap-only baseline must not contain
The overlap baseline must **not** include any ingredient that already belongs to a later mechanism layer.

### 5.1 No compatibility logic
It must not include:
- local agreement scoring
- internal support consistency
- conflict penalties
- structured supportability terms

These belong to candidate space, not baseline space.

### 5.2 No fragility logic
It must not include:
- removal sensitivity
- perturbation response
- damage ranking
- support-criticality under weakening

These belong to Candidate B-type logic, not baseline logic.

### 5.3 No stabilization logic
It must not include:
- persistence-style success
- bridge survival
- `simple_rigidity_surrogate`
- or any late-stage support indicator

### 5.4 No morphology/readability logic
It must not include:
- `grid_deviation_score`
- later shape/readability terms
- morphology-like structure measures

If any of these enter, the baseline is no longer overlap-only.

---

## 6. Working conceptual definition
The current working conceptual definition should be:

> **Overlap-only baseline = raw relational presence without compatibility-side, stabilization-side, or readability-side structuring.**

A shorter version is:

> **Overlap-only means: something is there, not yet that it fits, holds, or reads as structure.**

That is the intended meaning.

---

## 7. Recommended minimal baseline form
The preferred first-pass overlap baseline should remain deliberately simple.

### Recommended form
Use one scalar derived directly from local overlap magnitude or local overlap presence, without additional structural terms.

Examples of acceptable baseline style:
- raw local overlap magnitude
- local average overlap strength
- simple local overlap intensity

Examples of unacceptable baseline style:
- overlap weighted by agreement
- overlap adjusted by conflict
- overlap filtered by removal response
- overlap enriched by later graph or stability behavior

The baseline should be almost boring.
That is a feature, not a bug.

---

## 8. Why the baseline should be weak
A weak baseline is scientifically useful here.

Why?
Because the first compatibility pass is supposed to test whether Candidate A or B adds anything beyond:
- mere relation
- mere presence
- mere strength

If the baseline is already enriched, then the candidate comparison becomes muddy.

So the overlap baseline should be:
- simple enough to lose
- if a real compatibility-side candidate exists

That is the correct comparison philosophy.

---

## 9. What it means for a candidate to beat the overlap baseline
A candidate beats the overlap baseline only if it does something overlap alone does not already do.

At minimum, that should mean one of the following:

- it predicts later downstream support behavior better than overlap-only
- it separates local supportable vs non-supportable structure more clearly
- it reveals a structured distinction that overlap-only leaves blurred
- it remains informative where overlap-only becomes too generic

A tiny numerical bump with no structural meaning is not enough.

---

## 10. What it means if a candidate does not beat the overlap baseline
If a candidate does not meaningfully outperform overlap-only, the project should read that as:

- no useful compatibility gain yet
- the candidate may still be conceptually interesting
- but it is not operationally worth promotion in the current state

This is important because the overlap baseline exists precisely to prevent premature candidate inflation.

---

## 11. Relationship to Candidate A
Candidate A (local support coherence) must show that it adds something beyond:
- raw local overlap strength

Its intended gain should come from:
- local agreement / supportability structure

not from:
- stronger overlap dressed up with more words

So Candidate A’s first task is to beat this baseline clearly enough.

---

## 12. Relationship to Candidate B
Candidate B (early removal fragility) must show that it adds something beyond:
- simple relation presence

Its intended gain should come from:
- early structural support dependence

not from:
- “strong overlaps hurt more when removed”

So Candidate B must also beat the overlap baseline in a meaningful, non-trivial way.

---

## 13. Main risks of a bad overlap baseline
If the overlap baseline is badly defined, the whole first pass becomes unstable.

### Main risks
- baseline too weak in an artificial way
- baseline too enriched and therefore no longer pure overlap
- baseline drifting across candidate comparisons
- baseline being redefined mid-pass to make a candidate look better

These must all be prevented.

---

## 14. Required first-pass discipline
For the first pass, the overlap-only baseline must be:

- fixed before candidate comparison begins
- kept identical for Candidate A and Candidate B
- described explicitly in the first-pass result record
- and not redefined mid-pass

This is mandatory.

---

## 15. Safe summary sentence
A useful internal sentence is:

> The overlap-only baseline should represent raw relational presence and nothing more; if a candidate cannot beat that lower floor, it has not yet become a useful compatibility signal.

A shorter version is:

> **Overlap says “there”; compatibility must say more than “there.”**

Both are good steering sentences.

---

## 16. Bottom line
The overlap-only baseline is the lower comparison floor for the first compatibility pass.

It should be:
- simple
- early
- weak
- and free of compatibility, stabilization, and readability logic

Candidate A and Candidate B must both beat this floor before they deserve further promotion.

That is the current overlap-baseline standard.
