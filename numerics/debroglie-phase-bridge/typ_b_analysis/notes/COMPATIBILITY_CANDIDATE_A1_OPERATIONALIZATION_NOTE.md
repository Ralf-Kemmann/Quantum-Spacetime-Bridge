# COMPATIBILITY_CANDIDATE_A1_OPERATIONALIZATION_NOTE

## Operationalization note for Candidate A1 in the compatibility first pass

**Date:** 2026-04-07  
**Status:** internal operationalization note  
**Candidate ID:** CLC-A-01

---

## 1. Purpose
This note operationalizes the first compatibility candidate:

> **Candidate A1 = local support coherence**

Its purpose is to move Candidate A from:
- conceptual plausibility
to
- a first-pass operational shell that is concrete enough to be compared against overlap-only, the later-stabilization boundary, and DLBSR-class.

This note does **not** claim that the final formula is already closed.
It defines a first operational version strong enough for disciplined first-pass use.

This is an operationalization note, not a result note.

---

## 2. Why operationalization is needed
Candidate A has already been defined conceptually as:
- a coherence-side compatibility candidate
- meant to sit after overlap and before stabilization

But the first pass cannot run on conceptual language alone.

It now needs:
- a concrete neighborhood definition
- a concrete agreement term
- a concrete conflict term
- a concrete aggregation rule
- and a timing-safe computation point

This note provides that first-pass operational shell.

---

## 3. Intended role of Candidate A1
Candidate A1 is meant to answer:

> **Is the local relational environment already mutually supportable in a way that exceeds raw overlap alone, but does not yet rely on already-achieved stabilization?**

That means Candidate A1 should remain:

- earlier than rigidity-side persistence
- richer than overlap-only
- and simpler than full morphology/readability

This is the operational niche it must preserve.

---

## 4. First-pass operational definition in words
The first-pass operational reading of Candidate A1 should be:

> **Candidate A1 measures whether a local bridge-adjacent relation neighborhood is internally coherent enough that its support structure looks more jointly aligned and less internally conflicted than raw overlap alone would suggest.**

A shorter version is:

> **A1 = local support agreement minus local support conflict.**

That is the operational core.

---

## 5. First-pass computation unit
The first-pass computation should not begin globally.
It should begin on a local unit.

### Recommended unit
Use one:
- local relation-centered neighborhood
or
- small bridge-adjacent mesoscopic neighborhood

The neighborhood should be:
- small enough to remain pre-stabilization-relevant
- large enough to carry internal structure

So the first-pass unit should be:

> **a local bridge-adjacent neighborhood around a relation or small relation cluster**

This is the correct computation unit.

---

## 6. Neighborhood definition
For the first pass, the neighborhood should be defined conservatively.

### Recommended first-pass neighborhood rule
Use:
- the focal local relation or focal local support unit
plus
- its immediately adjacent local relations inside the same bridge-adjacent internal region

The neighborhood should not expand so far that:
- it becomes a global bridge-form descriptor
- or mixes multiple regime layers too strongly

### Short rule
> **Immediate local bridge-adjacent neighborhood only.**

This is the preferred first-pass neighborhood definition.

---

## 7. Agreement term
The agreement term should measure whether the local environment already “hangs together.”

### Recommended first-pass interpretation
The agreement term should increase when:
- nearby local support relations point in a mutually consistent direction
- local support intensity is not isolated but shared
- internal local support pattern looks structured rather than scattered

### Acceptable first-pass ingredients
- local sign agreement fraction
- local support alignment score
- neighborhood consistency proportion
- weighted agreement of nearby support relations

### Short operational rule
> **Agreement term = how strongly the local support neighborhood points in one internally consistent support direction.**

This is the preferred agreement reading.

---

## 8. Conflict term
The conflict term should measure how much the local environment resists joint supportability.

### Recommended first-pass interpretation
The conflict term should increase when:
- nearby support relations are internally contradictory
- sign/sector conflict rises
- support coherence is locally fragmented
- neighborhood support is split rather than aligned

### Acceptable first-pass ingredients
- local sign inconsistency fraction
- local fragmentation penalty
- conflict-weighted disagreement score
- incoherence or dispersion penalty

### Short operational rule
> **Conflict term = how strongly the local support neighborhood is internally split, contradictory, or fragmented.**

This is the preferred conflict reading.

---

## 9. First-pass formal shell
A good first-pass formal shell is:

`A1 = Agreement_local - lambda * Conflict_local`

where:
- `Agreement_local` measures internally aligned local support structure
- `Conflict_local` measures internal fragmentation / contradiction
- `lambda` is a fixed penalty strength chosen before comparison begins

This shell is intentionally minimal.

It is good because it makes explicit that:
- coherence must be earned
- conflict must cost something
- and the candidate is not just a dressed-up magnitude score

---

## 10. Aggregation rule
The aggregation rule should remain simple in the first pass.

### Recommended first-pass aggregation
Use:
- one local Candidate A1 value per focal neighborhood
or
- one narrow mesoscopic summary if multiple adjacent local values are grouped

Do **not** jump immediately to:
- broad global aggregation
- or full-family summary values

### Preferred rule
> **Aggregate locally first, summarize only one mesoscopic step if needed.**

This keeps the candidate early and interpretable.

---

## 11. Timing-safe computation point
This is one of the most important sections.

Candidate A1 should be computed at a stage where:

- local overlap structure is already available
- local relational neighborhood can be defined
- later stabilization-side success is not yet used
- later morphology/readability is not yet being read back into the candidate

### Timing-safe rule
Do **not** compute A1 from:
- already stabilized bridge-success labels
- rigidity-derived outcomes
- later readability-side classifications
- or full late graph form

### Short timing rule
> **Compute A1 before later support success is allowed to speak.**

This is mandatory.

---

## 12. Why this is more than overlap-only
Candidate A1 should beat overlap-only because it adds:
- internal local structure
- not just local presence

The difference is:

- overlap-only says: local relation is present / strong
- A1 says: the local support neighborhood is internally coherent or internally split

If the operationalization ends up behaving like:
- local overlap average
- or smoothed local density

then A1 has failed.

That anti-collapse check must remain explicit.

---

## 13. Why this is earlier than stabilization
Candidate A1 must also stay distinct from later-stabilization logic.

The difference is:

- stabilization says: support has already held strongly enough to look persistent
- A1 asks: does the local support environment already look jointly supportable before that persistence is granted?

If A1 only becomes strong when:
- rigidity-side behavior is already effectively visible

then it has drifted too late.

That anti-leakage check must remain explicit.

---

## 14. First-pass comparison obligations
Under the current compatibility first-pass chain, Candidate A1 must later be checked against:

### Lower floor
- overlap-only baseline

### Upper ceiling
- later-stabilization boundary
- current preferred proxy: `simple_rigidity_surrogate`

### Downstream target
- DLBSR-class

So the first-pass question becomes:

> **Does this operationalized A1 provide more than overlap, stay earlier than rigidity, and still relate meaningfully to DLBSR-class?**

That is the correct future comparison role.

---

## 15. Main operational risks
### Risk 1 — Overlap collapse
Agreement term becomes just a dressed-up local magnitude average.

### Risk 2 — Hidden stabilization leakage
Neighborhood definition already encodes later success structure.

### Risk 3 — Neighborhood arbitrariness
The result depends too strongly on one local neighborhood choice.

### Risk 4 — Penalty arbitrariness
`lambda` is chosen too flexibly or post hoc.

### Risk 5 — Interpretability blur
Agreement and conflict become numerically active but structurally vague.

These risks must be controlled in the first pass.

---

## 16. Recommended first-pass discipline
For the first pass, Candidate A1 should be implemented under the following discipline:

- immediate local bridge-adjacent neighborhood only
- one explicit agreement term
- one explicit conflict term
- one fixed penalty strength
- one timing-safe pre-stabilization computation point
- no mid-pass reformulation because the result “almost works”

This is mandatory.

---

## 17. Safe summary sentence
A useful internal sentence is:

> Candidate A1 should be operationalized as local support agreement minus local support conflict inside an immediate bridge-adjacent neighborhood, computed early enough that later stabilization has not yet entered the signal.

A shorter version is:

> **A1 = local coherence before persistence.**

Both are good steering lines.

---

## 18. Bottom line
The first-pass operationalization of Candidate A1 should now be treated as:

- a local bridge-adjacent neighborhood score
- built from one agreement term and one conflict term
- aggregated minimally
- computed before later stabilization speaks
- and tested against overlap-only, rigidity-side ceiling, and DLBSR-class

That is the current operationalization standard for Compatibility Candidate A1.
