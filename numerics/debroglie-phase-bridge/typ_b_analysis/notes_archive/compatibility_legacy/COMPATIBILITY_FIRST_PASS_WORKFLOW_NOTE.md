# COMPATIBILITY_FIRST_PASS_WORKFLOW_NOTE

## First-pass workflow for initial compatibility candidate testing

**Date:** 2026-04-06  
**Status:** internal workflow note

---

## 1. Purpose
This note converts the current compatibility-layer preparation into a practical first-pass workflow.

The project now already has:
- a minimal compatibility pilot frame,
- a candidate evaluation note,
- a candidate priority list,
- a baseline comparison rule,
- and a first test matrix.

What is still needed is a simple execution order:

> **In what sequence should the first compatibility comparison block actually be carried out, so that the work remains narrow, disciplined, and resistant to inflation?**

This note provides that sequence.

---

## 2. Why a first-pass workflow is needed
Without a workflow, even a good method set can become diffuse.

Typical risks:
- too many candidates tested at once
- baselines added too late
- evaluation criteria applied inconsistently
- weak signals being carried forward because no stopping rule existed

The compatibility layer is too important to be handled loosely.

So this note is meant to turn:
- prepared method logic
into
- a usable first-pass procedure

---

## 3. Core first-pass principle
The first pass should remain extremely narrow.

Its purpose is not:
- to solve compatibility,
- to optimize many signals,
- or to support broad synthesis.

Its purpose is only:

> **to determine whether at least one Tier-1 candidate can survive disciplined comparison against overlap-only and a later stabilization boundary without collapsing into tautology.**

That is the only first-pass aim.

---

## 4. First-pass input selection

## 4.1 Select exactly one Tier-1 local-coherence candidate
Choose one candidate only from:
- local sign consistency
- local phase-sector consistency
- neighborhood support agreement
- or another clearly defined early local-coherence signal

Do not test multiple local-coherence candidates at once in the first pass.

Reason:
- first pass is not for candidate family expansion
- it is for disciplined signal triage

---

## 4.2 Select exactly one Tier-1 removal-sensitivity candidate
Choose one candidate only from:
- local damage-to-support under removal
- pre-collapse sensitivity ranking
- or another clearly defined structural dependency measure

Again:
- choose one only

Reason:
- this gives the first pass one candidate from each Tier-1 family without creating signal sprawl

---

## 4.3 Do not add Tier-2 or Tier-3 candidates yet
Do not include:
- sign/sector contrast as a third branch
- structured asymmetry candidates
- morphology-near candidates
- stability-near candidates

Reason:
- first pass must remain small enough that rejection is easy and clean

---

## 5. Fix the reference frame before comparison

## 5.1 Overlap-only baseline
Fix one explicit overlap-only baseline.

Question:
- what does generic overlap already explain?

This baseline must be written down before candidate evaluation begins.

---

## 5.2 Later stabilization proxy
Fix one explicit later stabilization proxy, such as:
- `simple_rigidity_surrogate`
or another clearly downstream persistence/support indicator

Question:
- does the candidate remain earlier than this, or collapse into it?

This proxy must also be fixed before comparison begins.

---

## 5.3 Optional trivial control proxy
If feasible, define one weak control proxy, such as:
- local smoothed overlap magnitude
- simple local density
- or another deliberately weak generic scalar

This is optional but recommended.

---

## 5.4 Outcome proxy
Fix one narrow later outcome proxy.

It should represent:
- later bridge-support behavior
- or a narrow persistence-related downstream signal

It should not be vague.
It should be explicit.

---

## 6. First-pass comparison order
Each candidate should be processed in the same order.

### Step 1 — Timing check
Can the candidate be computed early enough?
If no:
- reject immediately

### Step 2 — Overlap comparison
Does the candidate add meaningful value beyond overlap-only?
If no:
- reject immediately

### Step 3 — Stabilization boundary check
Does the candidate remain distinct from the later stabilization proxy?
If no:
- reject immediately or downgrade heavily

### Step 4 — Interpretability check
Does the candidate have a plausible structural meaning as supportability rather than noise?
If no:
- keep at most exploratory

### Step 5 — Optional trivial-control check
If a trivial control exists:
- does the candidate beat it clearly enough to justify further attention?

### Step 6 — Assign candidate outcome
Allowed outcomes:
- rejected candidate
- exploratory-only candidate
- weak but non-tautological candidate
- promising pre-stabilization candidate

This order should not be changed.

---

## 7. Candidate processing sequence
The recommended sequence is:

### 7.1 Process Candidate A first
Run the local-coherence candidate through the full comparison chain.

### 7.2 Process Candidate B second
Run the removal-sensitivity candidate through the full comparison chain.

### 7.3 Only compare the two after both have been independently judged
Do not begin by asking:
- which one is better?

First ask:
- does either one survive at all?

That question must come first.

---

## 8. Stopping rules
The first pass should include explicit stopping discipline.

## 8.1 Stop if Candidate A fails immediately on timing or overlap
If the first Tier-1 local-coherence candidate:
- is too late,
- or fails to beat overlap-only,

do not rescue it with narrative reinterpretation.

Mark it as rejected and move on.

---

## 8.2 Stop if Candidate B collapses into stabilization
If the removal-sensitivity candidate:
- works only because it is effectively a late stabilization readout,

do not promote it.

Mark it as rejected or exploratory-only.

---

## 8.3 Stop the first pass after the two Tier-1 candidates
Do not expand the candidate set midstream just because both first candidates fail.

Reason:
- failure is a valid first-pass result
- inflation by adding more candidates mid-pass destroys discipline

If both fail, the correct result may simply be:
- no useful compatibility candidate found in first pass

That is acceptable.

---

## 9. Acceptable first-pass outcomes
The first pass should end in one of only three overall conclusions.

### Outcome A — No useful first-pass candidate
Neither Tier-1 candidate survives the comparison chain.

Interpretation:
- compatibility remains open
- first-pass candidate space did not yet produce a usable signal

---

### Outcome B — Weak but non-tautological candidate found
At least one candidate:
- survives early checks
- beats overlap modestly
- and remains at least somewhat distinct from stabilization

Interpretation:
- keep for second-pass refinement
- but do not overstate

---

### Outcome C — Promising pre-stabilization candidate found
At least one candidate:
- is early enough
- beats overlap clearly enough
- remains distinct from later stabilization
- and has a plausible structural reading

Interpretation:
- candidate deserves focused next-stage testing

These are the only acceptable first-pass global outcomes.

---

## 10. What the first pass must not do
The first pass must not:

- expand into many candidate branches
- rescue rejected candidates with analogy
- use morphology-side signals as compatibility substitutes
- reinterpret late stabilization as early compatibility
- escalate immediately into mechanism closure claims

This must remain a triage pass.

---

## 11. Minimal documentation requirement
Even this first pass should leave behind:

- candidate definitions
- overlap baseline definition
- stabilization proxy definition
- later outcome proxy definition
- candidate outcomes
- one short summary note

The first pass should still be reconstructable later.

---

## 12. Safe internal summary sentence
A useful summary sentence is:

> The first compatibility pass should test one local-coherence candidate and one removal-sensitivity candidate against overlap-only and a later stabilization boundary, and then stop early unless at least one candidate survives the anti-tautology comparison chain.

A shorter version is:

> **Two Tier-1 candidates in, no rescue logic, stop after triage.**

This is the correct spirit of the first pass.

---

## 13. Bottom line
The first pass for compatibility candidate work should be:

- narrow,
- two-candidate only,
- overlap-baselined,
- bounded above by stabilization,
- and strict about stopping.

Its role is not to close the mechanism.
Its role is only to determine whether the compatibility layer begins to become operationally visible at all.

That is the correct first-pass workflow.
