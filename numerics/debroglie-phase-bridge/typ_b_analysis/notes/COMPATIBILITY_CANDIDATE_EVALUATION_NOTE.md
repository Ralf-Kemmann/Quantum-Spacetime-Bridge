# COMPATIBILITY_CANDIDATE_EVALUATION_NOTE

## Evaluation note for candidate compatibility signals

**Date:** 2026-04-06  
**Status:** internal evaluation note

---

## 1. Purpose
This note defines how candidate compatibility signals should be evaluated inside the current `typ_b_analysis` block.

Its purpose is to answer one practical question:

> **When a proposed compatibility candidate appears, how do we decide whether it is useless, merely interesting, or genuinely promising?**

This note exists because the compatibility layer is currently:
- conceptually necessary,
- mechanistically central,
- and operationally still open.

That combination makes it especially vulnerable to premature enthusiasm.

So this note is a discipline tool.

---

## 2. Why an evaluation note is needed
The project already has a strong conceptual reason to posit a compatibility layer between:
- generic overlap
and
- later stabilization / form

But as soon as candidate signals are proposed, several dangers appear:

- a candidate may simply restate overlap
- a candidate may secretly encode later stabilization
- a candidate may work only under one threshold choice
- a candidate may look good in one special case but fail elsewhere
- a candidate may sound physically meaningful while being numerically weak

Without an explicit evaluation rule, all of these can be overread.

This note prevents that.

---

## 3. Basic evaluation principle
The evaluation rule is:

> **A compatibility candidate is interesting only if it adds non-trivial pre-stabilization predictive value beyond generic overlap, while remaining distinct from already-achieved stabilization.**

That is the central principle.

Everything in this note is just an unpacking of that sentence.

---

## 4. Minimum acceptance criteria
A candidate should be taken seriously only if it satisfies all of the following minimum criteria.

## 4.1 Pre-stabilization availability
The candidate must be computable before later stabilization/readability outcomes are already known.

If it is only available after stabilization has effectively happened, it is not a compatibility candidate.

---

## 4.2 Beyond-overlap value
The candidate must do more than generic overlap alone.

That means:
- it should improve prediction
or
- reveal a structured distinction
that simple overlap does not already provide

If it does not outperform overlap-only, it has little value.

---

## 4.3 Non-collapse into stabilization
The candidate must not simply be a disguised version of:
- `simple_rigidity_surrogate`
- later bridge survival
- morphology/readability outcomes
- or other downstream success indicators

This is the anti-tautology condition.

---

## 4.4 Directional interpretability
The candidate should have an interpretable direction.

Example:
- higher value plausibly means greater joint supportability
or
- lower value plausibly means stronger incompatibility

If the metric works numerically but has no interpretable directional meaning, it remains weak.

---

## 5. Immediate rejection criteria
A candidate should be rejected immediately if one or more of the following holds.

## 5.1 Post hoc dependence
The candidate can only be computed after the later result is already known.

## 5.2 Overlap redundancy
The candidate behaves essentially like overlap-only with no extra signal.

## 5.3 Stabilization leakage
The candidate owes its success mainly to already encoding later stabilization.

## 5.4 Threshold fragility
The candidate appears useful only under one brittle threshold regime.

## 5.5 Case-specific illusion
The candidate works only in one special case and collapses immediately elsewhere.

These are hard rejection triggers.

---

## 6. Recommended comparison logic
Every candidate should be judged against at least three reference layers.

### Layer A — Overlap baseline
Question:
- what does generic overlap already explain?

### Layer B — Candidate compatibility signal
Question:
- what extra predictive or structural value does the candidate add?

### Layer C — Later outcome proxy
Question:
- what later bridge-support / stabilization behavior is being predicted?

This comparison is necessary to avoid self-deception.

---

## 7. Evaluation dimensions
A candidate should be scored or discussed along the following dimensions.

### 7.1 Timing
How early in the pipeline can it be computed?

### 7.2 Incremental value
How much does it add beyond overlap-only?

### 7.3 Tautology resistance
How clearly does it remain distinct from later stabilization?

### 7.4 Interpretability
Can one explain what the candidate means structurally?

### 7.5 Stability
Does it survive small variations in implementation or threshold choice?

### 7.6 Scope
Does it show at least weak usefulness beyond one isolated case?

These six dimensions are enough for a first-pass evaluation.

---

## 8. Suggested evaluation categories
The following internal categories are recommended.

## 8.1 Rejected candidate
Use when:
- overlap redundancy is strong
- post hoc dependence is obvious
- or tautology risk is unacceptable

Safe wording:
> The candidate is not usable as a compatibility signal under the current evaluation standard.

---

## 8.2 Exploratory-only candidate
Use when:
- the candidate is interesting conceptually
- but too weak, noisy, or case-specific to support interpretation

Safe wording:
> The candidate remains exploratory and does not yet support compatibility-layer interpretation.

---

## 8.3 Weak but non-tautological candidate
Use when:
- the candidate appears distinct from stabilization
- and may add some value
- but the gain beyond overlap is still modest or uncertain

Safe wording:
> The candidate is non-trivial enough to remain under consideration, but currently too weak for strong use.

---

## 8.4 Promising pre-stabilization candidate
Use when:
- the candidate is computable early
- beats overlap-only in a meaningful way
- remains distinct from later stabilization
- and has a plausible interpretation

Safe wording:
> The candidate is a promising pre-stabilization compatibility signal and justifies further testing.

This is the strongest current acceptable category.

---

## 9. What this note forbids
This evaluation note forbids the following moves:

- calling a candidate “compatibility found”
- promoting a candidate because it fits a desired story
- ignoring overlap-only baselines
- ignoring stabilization leakage
- treating a one-case success as closure
- using conceptual beauty as evidence

These are invalid evaluation habits.

---

## 10. Safe interpretation ladder
When writing about a candidate, the following ladder is preferred.

### Level 1
Rejected candidate

### Level 2
Exploratory-only candidate

### Level 3
Weak but non-tautological candidate

### Level 4
Promising pre-stabilization candidate

This ladder is preferable to dramatic phrases such as:
- “mechanism discovered”
- “compatibility isolated”
- “bridge selection solved”

Those are currently too strong.

---

## 11. Minimal evaluation questions
Before accepting any candidate even provisionally, ask:

1. Is it available early enough?
2. Does it beat overlap-only?
3. Is it still distinct from later stabilization?
4. Is the direction interpretable?
5. Does it survive at least a minimal robustness check?

If any of the first three fail, the candidate should not be promoted.

---

## 12. Recommended immediate workflow
The recommended workflow for candidate evaluation is:

### Step 1
Choose a narrow candidate family.

### Step 2
Define the overlap-only baseline.

### Step 3
Define the later bridge-support proxy.

### Step 4
Check whether the candidate adds anything real in between.

### Step 5
Assign one of the internal evaluation categories.

This is the correct first-pass workflow.

---

## 13. Short internal steering sentence
A useful internal sentence is:

> **A compatibility candidate is only interesting if it speaks before stabilization, speaks more clearly than overlap alone, and does not merely repeat what stabilization later says.**

A shorter version is:

> **Earlier than rigidity, richer than overlap, cleaner than tautology.**

Both are good internal steering lines.

---

## 14. Bottom line
The compatibility layer should not be filled by enthusiasm.

Any proposed candidate must be evaluated under a strict rule:

- early enough,
- stronger than overlap-only,
- distinct from later stabilization,
- and structurally interpretable.

Only then may it count as a promising compatibility-layer candidate.

That is the current evaluation standard.
