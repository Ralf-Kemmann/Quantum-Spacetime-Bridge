# COMPATIBILITY_FIRST_PASS_INPUT_SPEC_NOTE

## Input specification for the first compatibility-candidate pass

**Date:** 2026-04-07  
**Status:** internal input-spec note

---

## 1. Purpose
This note defines the minimum input specification for the first compatibility-candidate pass.

Its purpose is to answer one practical question:

> **What inputs must be fixed and available before the first compatibility pass can actually be run in a disciplined way?**

This note is needed because the compatibility block now already has:

- Candidate A1 operationalization
- Candidate B1 operationalization
- overlap-only baseline
- later-stabilization boundary
- DLBSR-class
- comparison frame
- workflow
- and result template

What is still needed is the compact input-side contract.

This is an input-spec note, not a result note.

---

## 2. Why an input specification is needed
Without a minimal input specification, the first pass remains vulnerable to:

- hidden variation in what data are actually being used
- candidate-specific input drift
- baseline definitions that change from run to run
- downstream target ambiguity
- and partial reruns that are not really comparable

So the first pass needs one fixed answer to:

- what must be on the table before comparison begins?

This note provides that answer.

---

## 3. Core principle
The first compatibility pass should begin only when the full input frame is fixed.

That means:

- the candidate definitions are fixed
- the lower floor is fixed
- the upper boundary is fixed
- the downstream target is fixed
- and the local computation context is fixed

A shorter version is:

> **No first pass without fixed candidates, fixed bounds, fixed target, and fixed local context.**

That is the governing principle.

---

## 4. Required input block A — Local relational support context
The first pass must have one fixed local bridge-adjacent relational support context.

This means:

- a defined local or mesoscopic internal region
- a defined focal local relation or local support unit
- a defined immediate neighborhood around that focal unit

This input block is required because both Candidate A1 and Candidate B1 are local first-pass candidates.

### Minimum requirement
The pass must not start without:
- one explicit local computation context

---

## 5. Required input block B — Candidate A1 inputs
For Candidate A1, the first pass must have:

- one defined focal local neighborhood
- one defined agreement term input set
- one defined conflict term input set
- one fixed penalty strength `lambda`
- and one timing-safe pre-stabilization computation point

### Minimum requirement
The pass must not start without:
- a reproducible Candidate A1 computation shell

---

## 6. Required input block C — Candidate B1 inputs
For Candidate B1, the first pass must have:

- one defined focal local perturbation unit
- one defined early weakening/removal rule
- one defined local support-response measure
- one defined local fragility score shell
- and one timing-safe pre-stabilization perturbation point

### Minimum requirement
The pass must not start without:
- a reproducible Candidate B1 perturbation shell

---

## 7. Required input block D — Overlap-only baseline
The first pass must have:

- one explicit overlap-only baseline
- fixed before candidate comparison begins

This baseline must remain:
- simple
- early
- and free of compatibility, stabilization, and readability logic

### Minimum requirement
The pass must not start without:
- one named lower-floor overlap baseline

---

## 8. Required input block E — Later-stabilization boundary
The first pass must have:

- one explicit later-stabilization boundary
- current preferred proxy: `simple_rigidity_surrogate`

This boundary must remain:
- fixed across Candidate A1 and Candidate B1
- and not redefined mid-pass

### Minimum requirement
The pass must not start without:
- one named upper-boundary proxy

---

## 9. Required input block F — Downstream target
The first pass must have:

- one explicit downstream outcome target:
  - **DLBSR-class**
- one explicit support-positive decision rule
- one explicit support-negative default

This target must remain:
- fixed across Candidate A1 and Candidate B1
- and not broadened mid-pass

### Minimum requirement
The pass must not start without:
- one named downstream target and one fixed class rule

---

## 10. Required input block G — Comparison frame
The first pass must have one fixed comparison frame stating:

- Candidate A1
- Candidate B1
- overlap-only baseline
- later-stabilization boundary
- DLBSR-class

This is the minimum structural frame for the pass.

### Minimum requirement
The pass must not start without:
- one fixed comparison frame record

---

## 11. Required input block H — Decision / result containers
The first pass must have:

- one decision logic
- one result template
- one outcome vocabulary

This ensures that the pass ends in:
- rejected / exploratory / weak but non-tautological / promising
for candidates,
and
- one explicit next step

### Minimum requirement
The pass must not start without:
- one fixed output and decision container

---

## 12. Recommended compact input checklist
A useful first-pass checklist is:

- [ ] local bridge-adjacent computation context fixed  
- [ ] Candidate A1 shell fixed  
- [ ] Candidate B1 shell fixed  
- [ ] overlap-only baseline fixed  
- [ ] later-stabilization boundary fixed  
- [ ] DLBSR-class fixed  
- [ ] comparison frame fixed  
- [ ] decision logic fixed  
- [ ] result template fixed  

This is the compact input checklist.

---

## 13. What this spec must not allow
This input specification must not allow:

- candidate-specific hidden input changes
- changing the overlap baseline after seeing candidate behavior
- changing the rigidity boundary after seeing candidate behavior
- redefining DLBSR-class mid-pass
- using different local computation contexts for A1 and B1 without explicit declaration
- starting the pass with only conceptual candidate descriptions

These are invalid first-pass conditions.

---

## 14. Safe summary sentence
A useful internal sentence is:

> The first compatibility pass should begin only when the local context, Candidate A1 shell, Candidate B1 shell, overlap baseline, rigidity-side boundary, DLBSR-class, comparison frame, and result logic are all fixed.

A shorter version is:

> **No pass before candidates, bounds, target, and local context are all fixed.**

Both are good steering lines.

---

## 15. Bottom line
The first compatibility pass now needs the following minimum input specification:

- local bridge-adjacent computation context
- Candidate A1 shell
- Candidate B1 shell
- overlap-only baseline
- later-stabilization boundary
- DLBSR-class
- fixed comparison frame
- fixed decision and result containers

That is the current input-spec standard for the first compatibility pass.
