# COMPATIBILITY_CANDIDATE_DEFINITION_TEMPLATE

## Template for defining a single compatibility-layer candidate

**Date:** 2026-04-06  
**Status:** internal candidate-definition template

---

## 1. Purpose
This template is used to define one compatibility-layer candidate in a form that is precise enough for first-pass testing.

Its purpose is to prevent a common failure mode:

> **a candidate sounds interesting in discussion, but remains too vague, too late, or too entangled with stabilization to be tested fairly**

This template should be filled out before a candidate is admitted into:
- the first test matrix
- the first-pass workflow
- or any baseline comparison

This is a candidate-definition template, not a result note.

---

## 2. Candidate header

### Basic identification
- **Candidate ID:**  
- **Candidate name:**  
- **Candidate family:**  
  - pre-stabilization local coherence
  - removal sensitivity
  - sign / sector contrast
  - structured asymmetry
  - other

### Status
- **Definition status:** draft / reviewed / ready for first-pass test
- **Author / operator:**  
- **Date:**  

---

## 3. One-sentence candidate meaning
Fill in one sentence only.

### Template
> This candidate is intended to capture [short phrase] as a possible pre-stabilization indicator of joint supportability beyond generic overlap.

This sentence matters because it prevents the candidate from floating conceptually.

---

## 4. Structural role in the mechanism chain
State explicitly where the candidate is supposed to live.

### Required statement
The candidate is intended to sit:
- **after** generic overlap
- **before** later stabilization / persistence
- and **before** later morphology / readability

### Optional clarification
- Why does it belong here?
- What would make it too early?
- What would make it too late?

This section is mandatory.

---

## 5. Earliest computation point
This is one of the most important fields.

### Required questions
- At what stage in the pipeline can this candidate first be computed?
- What information must already be available?
- Does it require any later survival / stabilization knowledge?

### Required statement
> Earliest computation point: [explicit stage]

### Timing judgment
- clearly pre-stabilization
- borderline
- too late unless redefined

If this cannot be answered clearly, the candidate is not ready.

---

## 6. Required inputs
List the minimal inputs needed to compute the candidate.

### Examples
- overlap matrix entries
- local neighborhood structure
- sign / phase information
- edge-removal response
- pre-threshold graph fragment
- other

### Required question
- Are any of these inputs already contaminated by later stabilization information?

This is important for tautology control.

---

## 7. Explicit definition / formula
This section should define the candidate as explicitly as possible.

### Minimum requirement
Provide either:
- a mathematical formula
- or a procedural computation rule

### Template
> Candidate definition: [formula or procedural rule]

### Additional note
If the candidate cannot yet be defined clearly enough to compute reproducibly, it should remain:
- conceptual only
and not enter first-pass testing.

---

## 8. Why this is not just overlap
This section is mandatory.

### Required explanation
State why the candidate is not merely:
- overlap magnitude
- proximity
- or a thin rescaling of a generic overlap descriptor

### Template
> This candidate differs from overlap-only because [short explanation].

If this cannot be answered, the candidate is weak.

---

## 9. Why this is not just stabilization
This section is equally mandatory.

### Required explanation
State why the candidate is not merely:
- `simple_rigidity_surrogate`
- later persistence
- later bridge survival
- or another already-achieved support indicator

### Template
> This candidate differs from later stabilization because [short explanation].

If this cannot be answered, the candidate is in tautology danger.

---

## 10. Expected directional meaning
State how the candidate should be interpreted if it works.

### Required fields
- Higher value means:
- Lower value means:

### Example
- higher = greater joint supportability
- lower = stronger incompatibility or weaker supportability

If no direction can be given, the candidate remains interpretively weak.

---

## 11. Main risk assessment
Each candidate should come with an explicit self-critique.

### Required fields
- **Main tautology risk:**  
- **Main overlap-redundancy risk:**  
- **Main threshold/artifact risk:**  
- **Main interpretability risk:**  

### Template
> The main current risk of this candidate is that it may [short statement].

This section should not be skipped.

---

## 12. Baseline comparison plan
State explicitly what the candidate must be compared against.

### Required fields
- **Overlap-only baseline:**  
- **Later stabilization proxy:**  
- **Optional trivial control proxy:**  

### Required question
- What would count as “beating overlap” for this candidate?
- What would count as “collapsing into stabilization”?

This links the candidate to the baseline-comparison framework.

---

## 13. First-pass outcome proxy
State the later outcome proxy to be used in the first pass.

### Required field
- **First-pass downstream outcome proxy:**  

### Required statement
> This candidate will be judged in the first pass against the downstream outcome proxy [name].

This is necessary for fair comparison.

---

## 14. Initial evaluation expectation
Before testing, assign an expected status only as a weak prior.

### Allowed pre-test expectations
- exploratory only
- plausible Tier-1 candidate
- risky but interesting
- likely too weak / too late

### Purpose
This is not a result.
It just records the prior expectation before comparison.

---

## 15. Readiness decision
At the end, assign exactly one readiness label.

### Allowed labels
- **not ready for testing**
- **ready for exploratory definition refinement**
- **ready for first-pass comparison**

### Template
> Readiness decision: **[label]** because [short reason].

This is mandatory.

---

## 16. What this template forbids
This template forbids:

- entering a candidate into first-pass work without a clear computation point
- entering a candidate with no formula or reproducible rule
- leaving overlap-distinction vague
- leaving stabilization-distinction vague
- using analogy as a substitute for definition
- carrying candidates forward just because they sound mechanistically attractive

This is a discipline template.

---

## 17. Minimal final summary
At the end, include one short summary sentence.

### Template
> Candidate definition complete: [candidate name] is currently treated as [readiness label], with main promise in [short phrase] and main risk in [short phrase].

This is recommended.

---

## 18. Bottom line
A compatibility-layer candidate should not enter first-pass comparison as a loose idea.

It should first be defined clearly enough that one can answer:

- what it is
- when it can be computed
- why it is not just overlap
- why it is not just stabilization
- how its direction should be read
- and what its main failure risk is

This template defines that minimum standard.
