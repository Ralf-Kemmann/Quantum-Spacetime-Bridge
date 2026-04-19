# COMPATIBILITY_FIRST_TEST_MATRIX_NOTE

## First test matrix for initial compatibility candidate comparison

**Date:** 2026-04-06  
**Status:** internal first-comparison design note

---

## 1. Purpose
This note defines the first concrete test matrix for compatibility-layer candidate work.

The goal is not to solve the compatibility layer in one step.
The goal is much narrower:

> **to define the smallest meaningful first comparison block in which a small set of candidate compatibility signals is tested against explicit baselines and a later bridge-support outcome proxy.**

This note is the bridge between:
- candidate theory
and
- actual first-pass comparative testing

It is still a design note, not yet a run note.

---

## 2. Why a first test matrix is needed
The `typ_b_analysis` block now already has:

- a minimal compatibility pilot frame
- candidate evaluation logic
- a candidate priority list
- a baseline-comparison rule

What is still missing is the first concrete comparison block:
- which candidate families go in,
- which baselines they face,
- what later outcome they are tested against,
- and how the block should end.

Without this matrix, the work remains prepared but not yet test-shaped.

---

## 3. Scope of the first matrix
The first matrix must remain intentionally small.

It should not try to:
- screen many candidate families at once
- cover every bridge family
- or produce a final mechanism verdict

Its purpose is only:
- to determine whether at least one or two Tier-1 candidates survive a disciplined first comparison

This is a first-pass triage matrix.

---

## 4. Core matrix question
The matrix should answer only this:

> **Can any Tier-1 candidate signal add meaningful pre-stabilization value beyond overlap-only, while remaining distinguishable from later stabilization?**

That is the sole core question.

---

## 5. Candidate selection for the first matrix
The first matrix should stay narrow and include only two candidate families.

## 5.1 Candidate A — One pre-stabilization local coherence candidate
Choose one signal from the local-coherence family, for example:
- local sign consistency
- local phase-sector consistency
- local neighborhood agreement
- another clearly defined coherence candidate

Why include it:
- this is the strongest current Tier-1 candidate family
- it most naturally sits between overlap and stabilization

Constraint:
- the signal must be computable early enough
- and must not obviously encode later persistence

---

## 5.2 Candidate B — One removal-sensitivity candidate
Choose one signal from the removal-sensitivity family, for example:
- local damage-to-support under edge removal
- pre-collapse sensitivity ranking
- another clearly defined structural dependency measure

Why include it:
- this family fits the project’s existing leave-one-out logic well
- and may reveal which relations matter more than simple presence

Constraint:
- the removal logic must not be inserted so late that it becomes only a disguised stabilization analysis

---

## 5.3 What should not be included yet
Do **not** include in the first matrix:
- sign/sector contrast family as a third branch
- structured asymmetry family
- morphology-near candidates
- stability-near candidates

Reason:
- first matrix must remain focused
- two Tier-1 candidates are enough for first-pass triage

---

## 6. Baseline structure
Each candidate in the first matrix must be compared against the same baseline frame.

## 6.1 Lower baseline — Overlap-only
Question:
- what does generic overlap already explain by itself?

Function:
- prevent weak candidates from looking strong simply because overlap was never used as the real baseline

This baseline is mandatory.

---

## 6.2 Upper boundary — Later stabilization proxy
Question:
- is the candidate truly earlier than stabilization, or merely a disguised late-stage signal?

Typical proxy:
- `simple_rigidity_surrogate`
or another clearly downstream support/persistence indicator

This comparison is mandatory.

---

## 6.3 Optional control — Trivial proxy
If practical, include one weak control candidate, such as:
- smoothed overlap magnitude
- simple local density measure
- or another deliberately generic proxy

Function:
- check whether the candidate really beats a trivial “nice-looking” measure

This is optional but desirable.

---

## 7. Outcome proxy for the first matrix
The candidates must not be tested against vague “interestingness”.
They need one explicit later outcome proxy.

### Recommended first outcome proxy
Use one narrow later bridge-support or persistence-related proxy such as:
- later bridge-support success
- later support-survival class
- later stabilization-side indicator
- or another clearly downstream but well-defined outcome

The key point is:
- the outcome proxy must be late enough to count as downstream
- but narrow enough to remain interpretable

This proxy must be explicitly declared before comparison.

---

## 8. Comparison questions inside the matrix
For each candidate, the matrix should ask:

### 8.1 Early enough?
Can the candidate be computed before later stabilization is already known?

### 8.2 Better than overlap-only?
Does the candidate add any meaningful value over generic overlap?

### 8.3 Distinct from rigidity-side signal?
Does the candidate remain clearly distinguishable from later stabilization?

### 8.4 Structurally interpretable?
Does the candidate make sense as supportability rather than mere noise?

### 8.5 Worth carrying forward?
Should the candidate be rejected, kept exploratory, or promoted for further work?

These are the matrix decision questions.

---

## 9. Matrix decision outcomes
Each candidate should end in exactly one of the following categories:

### 9.1 Rejected candidate
- does not beat overlap
- or collapses into stabilization
- or is too noisy to interpret

### 9.2 Exploratory-only candidate
- interesting,
- but still too weak or fragile for promotion

### 9.3 Weak but non-tautological candidate
- early enough,
- distinct enough,
- and somewhat better than overlap,
- but still not strong

### 9.4 Promising pre-stabilization candidate
- early enough
- clearly stronger than overlap-only
- distinct from stabilization-side proxy
- and interpretable enough to justify further testing

These are the only allowed matrix outcomes.

---

## 10. Minimal matrix structure
A simple first matrix could be written in the following form:

| Candidate | Earlier than stabilization? | Beats overlap-only? | Distinct from rigidity-side proxy? | Trivial control beaten? | Interpretation |
|---|---|---|---|---|---|

The matrix does not need to be numerically elaborate at the start.
But the logic must be explicit.

---

## 11. Recommended first-pass workflow
The first matrix should be executed conceptually in this order:

### Step 1
Choose one local-coherence candidate.

### Step 2
Choose one removal-sensitivity candidate.

### Step 3
Define overlap-only baseline.

### Step 4
Define one later stabilization proxy.

### Step 5
Optionally define one trivial control proxy.

### Step 6
Compare each candidate against the same reference frame.

### Step 7
Assign candidate outcomes.

This is the intended first-pass workflow.

---

## 12. What the first matrix is not allowed to claim
The first matrix is not allowed to claim:

- compatibility solved
- compatibility isolated
- bridge mechanism closed
- promising candidate = accepted mechanism

The matrix can only say:
- rejected
- exploratory
- weak but non-tautological
- or promising pre-stabilization candidate

Nothing stronger.

---

## 13. Safe summary sentence
A useful internal summary sentence is:

> The first compatibility test matrix should not try to prove the missing mechanism. It should only determine whether one local-coherence candidate and one removal-sensitivity candidate can survive comparison against overlap-only and a later stabilization proxy without collapsing into tautology.

A shorter version is:

> **Two Tier-1 candidates, one overlap baseline, one rigidity boundary, one narrow downstream outcome.**

This is the correct spirit of the first matrix.

---

## 14. Bottom line
The first compatibility test matrix should remain deliberately small.

It should include:
- one local-coherence candidate
- one removal-sensitivity candidate
- overlap-only baseline
- one later stabilization proxy
- optional trivial control proxy
- one narrow later outcome proxy

Its purpose is only to determine whether the compatibility layer can begin to become operationally visible at all.

That is the correct role of the first matrix.
