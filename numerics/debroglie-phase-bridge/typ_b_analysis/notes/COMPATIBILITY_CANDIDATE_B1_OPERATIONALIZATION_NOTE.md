# COMPATIBILITY_CANDIDATE_B1_OPERATIONALIZATION_NOTE

## Operationalization note for Candidate B1 in the compatibility first pass

**Date:** 2026-04-07  
**Status:** internal operationalization note  
**Candidate ID:** ERF-B-01

---

## 1. Purpose
This note operationalizes the second compatibility candidate:

> **Candidate B1 = early removal fragility**

Its purpose is to move Candidate B from:
- conceptual plausibility
to
- a first-pass operational shell that is concrete enough to be compared against overlap-only, the later-stabilization boundary, and DLBSR-class.

This note does **not** claim that the final implementation is already closed.
It defines a first operational version strong enough for disciplined first-pass use.

This is an operationalization note, not a result note.

---

## 2. Why operationalization is needed
Candidate B has already been defined conceptually as:
- a fragility-side compatibility candidate
- meant to sit after overlap and before stabilization

But the first pass cannot run on conceptual language alone.

It now needs:
- a concrete local removal or weakening unit
- a concrete perturbation rule
- a concrete support-response measure
- a concrete fragility score
- and a timing-safe computation point

This note provides that first-pass operational shell.

---

## 3. Intended role of Candidate B1
Candidate B1 is meant to answer:

> **Does a local bridge-adjacent support relation already behave as disproportionately support-critical under early weakening, in a way that exceeds raw overlap alone but does not yet rely on already-achieved stabilization?**

That means Candidate B1 should remain:

- earlier than rigidity-side persistence
- richer than overlap-only presence
- and narrower than full morphology/readability

This is the operational niche it must preserve.

---

## 4. First-pass operational definition in words
The first-pass operational reading of Candidate B1 should be:

> **Candidate B1 measures how strongly a local bridge-adjacent support neighborhood loses downstream supportability when one focal relation or one very small focal support unit is weakened or removed early enough that later stabilization has not yet taken over the signal.**

A shorter version is:

> **B1 = local support loss under early controlled weakening.**

That is the operational core.

---

## 5. First-pass computation unit
The first-pass computation should begin on a narrow local unit.

### Recommended unit
Use:
- one focal local relation
or
- one minimal local support unit inside a bridge-adjacent neighborhood

The unit should be:
- small enough to stay pre-stabilization relevant
- large enough that its weakening can produce a meaningful support-response readout

So the first-pass unit should be:

> **one focal local bridge-adjacent relation or minimal support unit**

This is the correct computation unit.

---

## 6. Neighborhood definition
The perturbation should be evaluated inside a strictly local context.

### Recommended first-pass neighborhood rule
Use:
- the focal local relation or local support unit
plus
- its immediate bridge-adjacent support neighborhood

The neighborhood should not expand so far that:
- it becomes a full late bridge-form perturbation
- or mixes multiple internal regimes too strongly

### Short rule
> **Immediate local bridge-adjacent neighborhood only.**

This is the preferred first-pass neighborhood definition.

---

## 7. Perturbation rule
The perturbation should be intentionally small and controlled.

### Recommended first-pass perturbation
Apply:
- one local weakening step
or
- one local removal step

to the focal relation or focal support unit.

The perturbation should not be:
- global
- multi-step adaptive
- or late-stage catastrophic

### Short operational rule
> **One local early weakening/removal only.**

This is the preferred perturbation rule.

---

## 8. Support-response measure
The support-response measure should capture how much local supportability is lost when the focal unit is perturbed.

### Recommended first-pass interpretation
The support-response measure should increase when:
- local support structure remains robust despite perturbation

and decrease when:
- local support structure is disproportionately damaged by perturbation

### Acceptable first-pass ingredients
- local downstream support response scalar
- local support-positive vs support-negative status change
- local supportability retention score
- narrow local DLBSR-related response indicator

### Short operational rule
> **Support-response measure = how much local support remains after controlled early perturbation.**

This is the preferred support-response reading.

---

## 9. First-pass fragility score
A good first-pass fragility shell is:

`B1 = Baseline_support_local - Perturbed_support_local`

where:
- `Baseline_support_local` is the local support-response measure before perturbation
- `Perturbed_support_local` is the same measure after the focal weakening/removal

A larger positive value means:
- larger support loss
- hence stronger early fragility

This shell is intentionally minimal and transparent.

---

## 10. Aggregation rule
The aggregation rule should remain simple in the first pass.

### Recommended first-pass aggregation
Use:
- one local Candidate B1 value per focal local perturbation
or
- one narrow mesoscopic summary only if several immediately related local perturbations are grouped deliberately

Do **not** jump immediately to:
- broad global perturbation summaries
- or whole-family fragility maps

### Preferred rule
> **Compute locally first, summarize one mesoscopic step only if needed.**

This keeps Candidate B1 early and interpretable.

---

## 11. Timing-safe computation point
This section is critical for Candidate B1.

Candidate B1 should be computed at a stage where:

- local overlap/support structure is already available
- a focal local support perturbation is meaningful
- later stabilization-side success is not yet used
- and later morphology/readability is not yet being read back into the candidate

### Timing-safe rule
Do **not** compute B1 from:
- already stabilized bridge-success labels
- rigidity-derived persistence outputs
- later readability-side classifications
- or late full-bridge perturbation response

### Short timing rule
> **Compute B1 before later support success is allowed to define the perturbation effect.**

This is mandatory.

---

## 12. Why this is more than overlap-only
Candidate B1 should beat overlap-only because it adds:
- local structural dependence under perturbation
- not just local presence or local strength

The difference is:

- overlap-only says: local relation is present / strong
- B1 says: when this local relation is weakened, support falls disproportionately or it does not

If the operationalization ends up behaving like:
- stronger overlaps always look more important simply because they are larger
- or a disguised local magnitude ranking

then B1 has failed.

That anti-collapse check must remain explicit.

---

## 13. Why this is earlier than stabilization
Candidate B1 must also stay distinct from later-stabilization logic.

The difference is:

- stabilization says: support has already held strongly enough to look persistent
- B1 asks: does local support look unusually dependent on this focal unit before persistence is granted?

If B1 only becomes meaningful when:
- rigidity-side behavior is already effectively visible
- or the perturbation is applied too late in a nearly formed bridge structure

then it has drifted too late.

That anti-leakage check must remain explicit.

---

## 14. First-pass comparison obligations
Under the current compatibility first-pass chain, Candidate B1 must later be checked against:

### Lower floor
- overlap-only baseline

### Upper ceiling
- later-stabilization boundary
- current preferred proxy: `simple_rigidity_surrogate`

### Downstream target
- DLBSR-class

So the first-pass question becomes:

> **Does this operationalized B1 provide more than overlap, stay earlier than rigidity, and still relate meaningfully to DLBSR-class?**

That is the correct future comparison role.

---

## 15. Main operational risks
### Risk 1 — Overlap collapse
High-overlap local units look fragile only because they were larger to begin with.

### Risk 2 — Hidden stabilization leakage
The perturbation is applied too late, when support has already effectively stabilized.

### Risk 3 — Perturbation arbitrariness
The result depends too strongly on one weakening/removal convention.

### Risk 4 — Neighborhood arbitrariness
The response depends too strongly on one neighborhood boundary choice.

### Risk 5 — Interpretability blur
Support loss becomes numerically visible, but it is unclear whether it reflects compatibility-side fragility or merely late dependence.

These risks must be controlled in the first pass.

---

## 16. Recommended first-pass discipline
For the first pass, Candidate B1 should be implemented under the following discipline:

- one focal local bridge-adjacent perturbation unit only
- one immediate local neighborhood only
- one explicit support-response measure
- one explicit fragility score
- one timing-safe pre-stabilization computation point
- no mid-pass reformulation because the result “almost works”

This is mandatory.

---

## 17. Safe summary sentence
A useful internal sentence is:

> Candidate B1 should be operationalized as local support loss under one controlled early weakening/removal inside an immediate bridge-adjacent neighborhood, computed early enough that later stabilization has not yet defined the signal.

A shorter version is:

> **B1 = local fragility before persistence.**

Both are good steering lines.

---

## 18. Bottom line
The first-pass operationalization of Candidate B1 should now be treated as:

- a local bridge-adjacent perturbation score
- built from one baseline support-response and one perturbed support-response
- aggregated minimally
- computed before later stabilization speaks
- and tested against overlap-only, rigidity-side ceiling, and DLBSR-class

That is the current operationalization standard for Compatibility Candidate B1.
