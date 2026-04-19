# COMPATIBILITY_FIRST_PASS_LAUNCH_SEQUENCE_NOTE

## Launch sequence for the first compatibility-candidate pass

**Date:** 2026-04-07  
**Status:** internal launch-sequence note

---

## 1. Purpose
This note defines the concrete launch sequence for the first compatibility-candidate pass.

Its purpose is to answer one practical question:

> **In what exact order should the compatibility first pass now be started, from the first local context record to the first filled result note?**

This is a launch-sequence note, not a result note.

---

## 2. Why a launch sequence is needed
The compatibility block is now very close to actual first-pass use.

It already has:

- Candidate A1 operationalization
- Candidate B1 operationalization
- overlap-only baseline
- later-stabilization boundary
- DLBSR-class
- first-pass decision logic
- result template
- input specification
- starter-context note
- and a local-context record template

What is still needed is one short operational sequence that says:
- do this first
- then this
- then this
- and stop with one explicit recorded result

This note provides that sequence.

---

## 3. Core launch principle
The first compatibility pass should not begin by “running everything.”
It should begin by fixing one local context and then moving through one narrow comparison chain.

A shorter version is:

> **Context first, candidates second, decision third, result fourth.**

That is the launch principle.

---

## 4. Launch sequence

### Step 1 — Fill the first local-context record
Use:
- `COMPATIBILITY_FIRST_PASS_LOCAL_CONTEXT_RECORD_TEMPLATE.md`

Fix:
- focal local unit
- immediate bridge-adjacent neighborhood
- A1 suitability
- B1 suitability
- overlap / rigidity-boundary / DLBSR compatibility

Do not begin candidate comparison before this record exists.

---

### Step 2 — Lock the local context
Once the local-context record is accepted, freeze:
- focal unit
- neighborhood boundary
- local frame

No local drift after this point.

---

### Step 3 — Compute / assess Candidate A1 in the locked context
Use the A1 operationalization note.

Ask:
- is A1 materially active?
- is A1 more than overlap-only?
- is A1 still earlier than stabilization?

Record the judgment immediately.

---

### Step 4 — Compute / assess Candidate B1 in the locked context
Use the B1 operationalization note.

Ask:
- is B1 materially active?
- is B1 more than overlap-only?
- is B1 still earlier than stabilization?

Record the judgment immediately.

---

### Step 5 — Apply DLBSR-class as the downstream target
Use the fixed DLBSR-class decision rule.

Ask:
- is the local downstream target class meaningful here?
- how do A1 and B1 relate to the same downstream local support-response class?

Do not redefine DLBSR mid-pass.

---

### Step 6 — Apply the compatibility decision logic
Use the fixed compatibility first-pass decision logic.

Assign for each candidate:
- rejected candidate
- exploratory-only candidate
- weak but non-tautological candidate
- promising pre-stabilization candidate

Do not invent new candidate categories mid-pass.

---

### Step 7 — Fill the first result record
Use:
- `COMPATIBILITY_FIRST_PASS_RESULT_TEMPLATE.md`

Record:
- Candidate A1 outcome
- Candidate B1 outcome
- global first-pass outcome
- no-rescue block
- promotion decision
- one next step

This is the first actual first-pass output.

---

## 5. Stop conditions
The launch sequence should stop cleanly after the first result note.

That means:
- do not immediately widen the candidate set
- do not immediately switch contexts
- do not immediately rerun with a softened boundary
- and do not re-interpret weak results in the same launch step

The point of the launch sequence is:
- one first disciplined pass
not
- iterative rescue in disguise

---

## 6. Minimal launch bundle
A valid first launch should leave behind:

- one filled local-context record
- one A1 judgment
- one B1 judgment
- one DLBSR-class application
- one filled first-pass result note

This is the minimum launch bundle.

---

## 7. Safe summary sentence
A useful internal sentence is:

> The compatibility first pass should launch by fixing one local bridge-adjacent context, reading A1 and B1 in that locked context, applying DLBSR-class as the downstream target, and ending in one filled result note without rescue logic.

A shorter version is:

> **Lock context, read A1, read B1, apply target, record result, stop.**

Both are good steering lines.

---

## 8. Bottom line
The concrete launch sequence for the first compatibility pass is:

1. fill the first local-context record
2. lock the local context
3. assess Candidate A1
4. assess Candidate B1
5. apply DLBSR-class
6. apply the decision logic
7. fill the first result note

That is the current launch-sequence standard for the first compatibility pass.
