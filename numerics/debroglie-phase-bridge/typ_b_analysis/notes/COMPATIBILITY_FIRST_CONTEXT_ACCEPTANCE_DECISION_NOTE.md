# COMPATIBILITY_FIRST_CONTEXT_ACCEPTANCE_DECISION_NOTE

## Acceptance decision logic for the first local context in the compatibility first pass

**Date:** 2026-04-07  
**Status:** internal decision note

---

## 1. Purpose
This note defines the acceptance decision logic for the first local context in the compatibility first pass.

Its purpose is to answer one practical question:

> **When should the first concrete local bridge-adjacent context be accepted as a valid launch context for Candidate A1 and Candidate B1, when should it be treated as borderline, and when should it be rejected?**

This note is needed because the compatibility block now already has:

- a starter-context note
- a first local context instance note
- a local-context record template
- a launch-sequence note
- and an executive run note

What is still needed is the compact decision logic that stands between:
- first context candidate
and
- actual first-pass launch

This is a decision note, not a result note.

---

## 2. Why a context-acceptance logic is needed
Without explicit context-acceptance logic, the first compatibility launch is vulnerable to three familiar problems:

- a too-weak local context gets accepted just because the project is eager to start
- a too-late local context gets accepted even though rigidity or readability already dominate
- a borderline context gets treated as “good enough” without recording why it is borderline

So this note exists to enforce one thing:

> **the first pass should launch only from a context that is clearly admissible under the current local-context standard**

That is its purpose.

---

## 3. Core acceptance principle
The first local context should be accepted only if it is:

- already more than weak background
- narrow enough to be genuinely local
- meaningful for both A1 and B1
- still earlier than clear rigidity-side domination
- still earlier than clear readability-side domination
- and suitable for the full lower/upper/downstream comparison frame

A shorter version is:

> **Accept only if the context is local, structured enough, early enough, and usable for both candidates plus the full frame.**

That is the governing principle.

---

## 4. Inputs to the decision logic
The acceptance decision should use exactly the following local-context readings:

- focal local unit
- immediate neighborhood definition
- A1 suitability reading
- B1 suitability reading
- overlap-only baseline compatibility
- later-stabilization boundary compatibility
- DLBSR-class compatibility
- exclusion check:
  - too weak?
  - too broad?
  - too readability-side late?
  - too stabilization-side late?

No extra rescue factor should be introduced mid-decision.

---

## 5. The three allowed context outcomes
The first local context should receive exactly one of the following outcomes:

### Outcome A — Accepted first-pass local context
Use only when:
- the context is clearly more than background
- the neighborhood is local enough
- A1 is meaningfully computable
- B1 is meaningfully computable
- overlap baseline still makes sense
- rigidity-side ceiling still makes sense
- DLBSR-class still makes sense
- and no strong exclusion condition applies

### Outcome B — Borderline context — refine once
Use when:
- the context is close to admissible
but
- one important feature remains unclear or slightly unstable

Typical examples:
- neighborhood boundary slightly too broad
- A1 suitability plausible but not yet sharp enough
- B1 perturbation context plausible but not yet clean enough
- downstream-frame compatibility not yet clearly readable

This category should remain narrow.

### Outcome C — Rejected context
Use when:
- the context is too weak
- too broad
- too readability-side late
- too stabilization-side late
- or clearly unusable for either A1 or B1

No fourth category should be introduced.

---

## 6. Positive decision rule
Assign:

## Accepted first-pass local context
only if all of the following hold:

1. **More than weak background**
2. **Immediate bridge-adjacent neighborhood is local enough**
3. **A1 suitability = yes**
4. **B1 suitability = yes**
5. **Overlap-only baseline compatibility = yes or clearly usable**
6. **Later-stabilization boundary compatibility = yes or clearly usable**
7. **DLBSR-class compatibility = yes or clearly usable**
8. **No clear exclusion condition applies**

This should be treated as a strict conjunction.

If one of these clearly fails, do not accept the context.

---

## 7. Borderline decision rule
Assign:

## Borderline context — refine once
only when:

- the context is plausibly usable
but
- one important feature is still too unclear for direct launch,
and
- that uncertainty can realistically be resolved by one narrow refinement step

Examples:
- tighten the neighborhood boundary once
- clarify the focal unit once
- sharpen one frame-compatibility reading once

This category must not become:
- “almost accepted, probably fine”

It means:
- not yet accepted.

---

## 8. Negative decision rule
Assign:

## Rejected context
if any of the following clearly holds:

1. **Too weak / too background-like**
2. **Too broad / too mixed**
3. **Too readability-side late**
4. **Too stabilization-side late**
5. **A1 not meaningfully computable**
6. **B1 not meaningfully computable**
7. **comparison frame not jointly usable**

This should be treated strictly.

A context that clearly satisfies one of these rejection conditions should not be upgraded through narrative rescue.

---

## 9. Recommended decision sequence
The local-context decision should be assigned in this order:

### Step 1
Check the rejection conditions first:
- too weak?
- too broad?
- too late?
- unusable for A1 or B1?
- frame not jointly usable?

If yes, assign **Rejected context** unless there is a very clear reason this is genuinely borderline.

### Step 2
If no clear rejection condition applies, check the full positive conjunction:
- more than background?
- local enough?
- A1 usable?
- B1 usable?
- overlap / rigidity / DLBSR all still meaningful?

If yes, assign **Accepted first-pass local context**.

### Step 3
If neither a clean acceptance nor a clean rejection applies, assign **Borderline context — refine once**.

This order reduces premature launch risk.

---

## 10. One-refinement rule
If a context is classified as borderline, only **one** narrow refinement step should be allowed before re-decision.

Acceptable one-step refinements:
- tighten the neighborhood boundary once
- choose a slightly better focal unit once
- sharpen one frame-compatibility interpretation once

Not acceptable:
- repeated adaptive reshaping until the context finally works

A shorter version is:

> **Borderline means refine once, not rescue indefinitely.**

This is mandatory.

---

## 11. What the decision logic must not do
The context-acceptance logic must not:

- accept a weak context just to get the engine moving
- accept a late context because it looks more structured
- blur borderline into accepted
- keep a context undecided without assigning one of the three statuses
- or use broader theory appeal to rescue a bad launch context

These are invalid decision habits.

---

## 12. Safe summary sentence
A useful internal sentence is:

> The first compatibility pass should launch only from a local context that is already more than background, still earlier than obvious late-stage dominance, meaningful for both A1 and B1, and jointly compatible with overlap, rigidity, and DLBSR-class.

A shorter version is:

> **No launch without a local context that is clearly usable, early enough, and jointly frame-compatible.**

Both are good steering lines.

---

## 13. Bottom line
The first compatibility local context should end in exactly one of three statuses:

- **Accepted first-pass local context**
- **Borderline context — refine once**
- **Rejected context**

The positive launch status should be granted only when the context is:

- more than weak background
- local enough
- usable for A1
- usable for B1
- and jointly usable for the full lower/upper/downstream frame

That is the current acceptance-decision standard for the first compatibility local context.
