# RING_DEGENERACY_PRE_RUN_CHECKLIST

## Pre-run checklist for a clean ring degeneracy perturbation pilot

**Date:** 2026-04-06  
**Status:** internal pre-run checklist

---

## 1. Purpose
This checklist is to be completed **before** a ring degeneracy perturbation pilot is started.

Its purpose is simple:

> **Do not start a ring pilot unless the run is already methodically clean enough that its outcome can later be interpreted without repair-work, memory reconstruction, or narrative rescue.**

The ring is a boundary case.
Boundary cases are especially vulnerable to:
- premature interpretation,
- naive interventions,
- vague pilot goals,
- missing raw metrics,
- and poor run hygiene.

This checklist prevents those failures at the start rather than after the fact.

---

## 2. How to use this checklist
The checklist should be completed before execution.

Each item should be marked as:
- **yes**
- **no**
- **partial**
- or **not applicable**

If there are multiple critical “no” answers, the run should not start yet.

This checklist is the pre-run counterpart to the post-run review checklist.

---

## 3. Section A — Goal clarity

### A1. Minimal question fixed
- Is the run trying to answer one narrow question only?
- Is that question stated in one sentence?
- Is the goal clearly a pilot trend test rather than a full theory claim?

### A2. Scope discipline
- Is the run limited to one ring family?
- Is it limited to one perturbation family?
- Is the sweep limited enough to remain interpretable?

### A3. No hidden escalation
- Is it explicitly clear that this run is not meant to prove a universal claim?
- Is it clear that even a positive outcome would remain intervention-specific?

If not, the run goal is too vague or too ambitious.

---

## 4. Section B — Family and intervention clarity

### B1. Ring family fixed
- Is the ring family explicitly named?
- Is the family generation method documented?
- Is it clear which structural properties of the ring are relevant here?

### B2. Perturbation mathematically defined
- Is the perturbation formula written down?
- Is the strength parameter clearly defined?
- Is the sweep over strengths explicitly listed?

### B3. Intervention point fixed
- Is it clear where the perturbation enters the model?
- Does the intervention plausibly act on a meaningful structural level?
- Is it documented what is intentionally *not* perturbed?

### B4. Cosmetic-risk awareness
- Has the risk of a purely cosmetic intervention been considered?
- Is the most likely intervention weakness already named?

If the intervention point is unclear, the run should not start.

---

## 5. Section C — Metric clarity

### C1. Primary metrics fixed in advance
- Are `delta_p_strength` and `delta_p2_strength` explicitly included?
- Is `dominance_margin` included?
- Are `sign_sensitivity_flag` and `delta_p2_blind_to_direction_flag` included?

### C2. Secondary labels demoted
- Is it explicitly stated that winner-labels are secondary?
- Is it clear that raw metric trajectories outrank label outcomes?

### C3. Trend-reading logic known
- Is it already clear what kind of movement would count as a directional shift?
- Is it clear what would count as mere noise or threshold flicker?

If these are not fixed before the run, later interpretation becomes too vulnerable.

---

## 6. Section D — Sweep and repeat logic

### D1. Strength sweep defined
- Is the perturbation-strength sweep written down?
- Is the sweep fine enough to detect gradual change?
- Is it small enough to remain interpretable?

### D2. Repeat logic defined
- Are seeds or repeated runs actually needed?
- If stochasticity is present, is the repeat logic fixed?
- If no repetition is used, is that limitation already acknowledged?

### D3. Fine-sweep trigger awareness
- If the pilot shows a suspicious transition region, is it already understood that this would justify a later fine sweep rather than immediate overinterpretation?

---

## 7. Section E — Run hygiene

### E1. Run ID assigned
- Is there a clear run ID?
- Does the run ID encode stage and version properly?

### E2. Folder created
- Has the run folder been created before execution?
- Does it follow the ring degeneracy run-folder convention?

### E3. Required files prepared
- Is the config file ready?
- Is the runner file ready?
- Is the output target path defined?

### E4. First-entry report location prepared
- Is it already clear where `report.md` will live?
- Is the intended run bundle structure in place?

If no folder or run ID exists, the run is not ready.

---

## 8. Section F — Decision logic discipline

### F1. Decision categories known in advance
- Are categories A / B / C / D / E already known?
- Is it clear that only one category should be assigned later?

### F2. No-go signatures known
- Are the main no-go signatures already known?
  - winner-flip without raw support
  - one-point flip only
  - contradictory metrics
  - threshold artifact
  - cosmetic intervention

### F3. Strongest trivial alternative named
- Is the most plausible trivial explanation already named before the run?

This matters because otherwise the run may later be interpreted too generously.

---

## 9. Section G — Output bundle readiness

### G1. Required bundle understood
- Is it clear that the run must produce:
  - config
  - runner
  - raw metrics
  - summary
  - report

### G2. Output paths defined
- Are output locations already set in the config or run plan?
- Is there no ambiguity about where files will be written?

### G3. Raw metrics persistence guaranteed
- Is it guaranteed that raw metric outputs will be written, not only final labels?

If not, the run should not start.

---

## 10. Section H — Pre-commitment to interpretation restraint

### H1. Safe interpretation stance accepted
- Is it accepted in advance that even an exciting trend may still remain only preliminary?

### H2. No rescue rhetoric
- Is it accepted in advance that the ring may remain a resistant boundary case?
- Is it accepted that a non-supportive result is still scientifically valuable?

### H3. No ontological escalation from pilot
- Is it accepted that no ring pilot result should directly trigger wider ontological claims?

This section is important because interpretation discipline begins before execution.

---

## 11. Section I — Abort / downgrade conditions known in advance

### I1. Abort condition
- Is it clear under what condition the run should be stopped as technically unfit?

### I2. Draft-only condition
- Is it clear when a finished run should remain only `draft`?

### I3. Rerun-needed condition
- Is it clear when a completed run should be downgraded to “needs rerun before use”?

If this is not known before execution, the run is too exposed to post hoc optimism.

---

## 12. Minimal pre-run decision
At the end of the checklist, assign one of the following:

- **ready to run**
- **ready with limitations**
- **not ready — revise before execution**

### Template
> Pre-run decision: **[ready to run / ready with limitations / not ready]** because [short reason].

This final sentence is mandatory.

---

## 13. What this checklist forbids
This checklist forbids the following pre-run mistakes:

- launching a run with no clear minimal question
- using an unclear or cosmetic intervention point
- treating winner-labels as primary
- starting without raw metrics defined
- starting without run folder / config discipline
- promising too much from a pilot
- entering the run without naming the strongest trivial alternative explanation

These are all invalid starts.

---

## 14. Bottom line
A ring degeneracy pilot should start only when:

- the goal is narrow,
- the perturbation is explicit,
- the intervention point is meaningful,
- the primary metrics are fixed,
- the run bundle structure is prepared,
- the decision logic is already known,
- and interpretation restraint is accepted in advance.

That is the correct pre-run discipline for the ring degeneracy line.
