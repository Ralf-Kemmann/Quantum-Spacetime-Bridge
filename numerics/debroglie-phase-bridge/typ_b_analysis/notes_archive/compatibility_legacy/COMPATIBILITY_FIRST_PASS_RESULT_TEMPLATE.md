# COMPATIBILITY_FIRST_PASS_RESULT_TEMPLATE

## Template for documenting the result of a first compatibility-candidate pass

**Date:** 2026-04-06  
**Status:** internal result template

---

## 1. Purpose
This template is used to document the outcome of a first-pass compatibility-candidate comparison block.

Its purpose is to prevent three problems:

- forgetting why a candidate was rejected
- informally rescuing weak candidates later
- losing the comparison logic between overlap, compatibility candidate, and later stabilization boundary

This is a result template, not a synthesis note.

It should be used after:
- the first-pass workflow has been completed
- candidate A and candidate B have both been evaluated
- and the pass has reached a stopping point

---

## 2. Test block header

### Block identification
- **Block ID:**  
- **Date:**  
- **Author / operator:**  
- **Status:** draft / reviewed / archived

### First-pass setup
- **Candidate A:**  
- **Candidate B:**  
- **Overlap-only baseline:**  
- **Later stabilization proxy:**  
- **Optional trivial control proxy:**  
- **Later outcome proxy:**  

### Scope reminder
> This first pass is only a triage block. It does not solve compatibility. It only checks whether at least one candidate survives disciplined comparison against overlap-only and a later stabilization boundary.

Keep this sentence.

---

## 3. Candidate A result block

### A1. Candidate description
- Name / short label:
- Candidate family:
- One-sentence structural meaning:
- Earliest computation point:

### A2. Timing check
- Early enough to count as pre-stabilization?  
  - yes / no / partial
- Notes:

### A3. Overlap comparison
- Does candidate A beat overlap-only?  
  - yes / no / partial
- In what sense?  
  - predictive / separating / structural / other
- Notes:

### A4. Stabilization-boundary check
- Does candidate A remain distinct from the later stabilization proxy?  
  - yes / no / partial
- Tautology risk:
  - low / medium / high
- Notes:

### A5. Interpretability check
- Is the candidate direction structurally interpretable?  
  - yes / no / partial
- Notes:

### A6. Optional trivial-control check
- If a trivial control proxy was used, does candidate A beat it?  
  - yes / no / partial / n.a.
- Notes:

### A7. Candidate A outcome category
Assign exactly one:
- rejected candidate
- exploratory-only candidate
- weak but non-tautological candidate
- promising pre-stabilization candidate

### A8. One-paragraph judgment for candidate A
Template:
> Candidate A is classified as **[category]** because it [summary of timing / overlap / stabilization-boundary / interpretability outcome]. The main reason it [is rejected / remains exploratory / survives provisionally / deserves promotion] is [short reason].

---

## 4. Candidate B result block

### B1. Candidate description
- Name / short label:
- Candidate family:
- One-sentence structural meaning:
- Earliest computation point:

### B2. Timing check
- Early enough to count as pre-stabilization?  
  - yes / no / partial
- Notes:

### B3. Overlap comparison
- Does candidate B beat overlap-only?  
  - yes / no / partial
- In what sense?  
  - predictive / separating / structural / other
- Notes:

### B4. Stabilization-boundary check
- Does candidate B remain distinct from the later stabilization proxy?  
  - yes / no / partial
- Tautology risk:
  - low / medium / high
- Notes:

### B5. Interpretability check
- Is the candidate direction structurally interpretable?  
  - yes / no / partial
- Notes:

### B6. Optional trivial-control check
- If a trivial control proxy was used, does candidate B beat it?  
  - yes / no / partial / n.a.
- Notes:

### B7. Candidate B outcome category
Assign exactly one:
- rejected candidate
- exploratory-only candidate
- weak but non-tautological candidate
- promising pre-stabilization candidate

### B8. One-paragraph judgment for candidate B
Template:
> Candidate B is classified as **[category]** because it [summary of timing / overlap / stabilization-boundary / interpretability outcome]. The main reason it [is rejected / remains exploratory / survives provisionally / deserves promotion] is [short reason].

---

## 5. First-pass global outcome
After both candidates have been reviewed, assign exactly one global first-pass outcome.

### Allowed global outcomes
- **Outcome A — No useful first-pass candidate**
- **Outcome B — Weak but non-tautological candidate found**
- **Outcome C — Promising pre-stabilization candidate found**

### Required rule
Do not invent a fourth global category.

### Template
> Global first-pass outcome: **[A / B / C]** because [short reason based on the candidate results].

---

## 6. No-rescue block
This section is mandatory.

Its purpose is to record which candidates are **not** being carried forward and why.

### Template structure
- **Candidate not carried forward:**  
- **Reason:** overlap redundancy / too late / stabilization leakage / weak interpretability / too fragile / other
- **Decision:** rejected / parked / exploratory only

Repeat as needed.

### Required statement
> No candidate rejected in this first pass should be reintroduced later without an explicit new justification.

Keep this sentence.

---

## 7. Promotion decision
State clearly what moves forward after the first pass.

### Allowed promotion outcomes
- no candidate promoted
- one candidate promoted for second-pass refinement
- two candidates promoted for second-pass refinement

### Template
> Promotion decision: **[state the outcome]** because [short reason].

If no candidate is promoted, say so explicitly.

---

## 8. Next-step block
The first pass must end with one concrete next-step statement only.

### Allowed next-step types
- stop for now
- redefine candidate A
- redefine candidate B
- run second-pass refinement on promoted candidate
- strengthen baseline or control structure before any rerun

### Template
> Next step: **[one concrete next step only]**

Do not list many possible next steps.
Force one.

---

## 9. Minimal artifact reminder
This result template should ideally be stored together with:
- candidate definitions
- overlap baseline definition
- stabilization proxy definition
- optional trivial control definition
- any raw comparison outputs used for the judgment

The result note should not float free from the comparison basis.

---

## 10. What this template forbids
This template forbids:

- carrying weak candidates forward without explicit justification
- replacing rejection with vague optimism
- promoting a candidate only because it “fits the story”
- writing a global success narrative when both candidates failed
- blurring the distinction between exploratory-only and promising

This is a discipline template.

---

## 11. Safe summary sentence
A useful one-line summary at the end is:

> The first compatibility pass is complete, and the candidate set has been narrowed without rescue logic.

A second acceptable version is:

> First-pass outcome recorded: candidate triage complete, promotion status explicit.

Either sentence is acceptable.

---

## 12. Bottom line
A first compatibility pass should leave behind a disciplined result record that states:

- what was tested
- how each candidate performed
- what was rejected
- what, if anything, was promoted
- and what the single next step is

This template defines that result format.
