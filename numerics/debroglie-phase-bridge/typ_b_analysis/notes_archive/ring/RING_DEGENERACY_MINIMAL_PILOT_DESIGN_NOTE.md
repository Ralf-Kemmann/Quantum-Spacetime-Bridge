# RING_DEGENERACY_MINIMAL_PILOT_DESIGN_NOTE

## Minimal pilot design for a clean ring degeneracy perturbation test

**Date:** 2026-04-06  
**Status:** internal pilot design note

---

## 1. Purpose
This note defines the smallest clean experimental design that could move the ring degeneracy line from:

- interesting hypothesis
to
- project-compatible pilot evidence

The aim is not to solve the whole ring question at once.

The aim is much narrower:

> **Test whether an explicitly defined degeneracy-lifting perturbation in the ring produces a systematic shift in raw readout metrics from `delta_p` toward `delta_p2` under controlled and reproducible conditions.**

This is the smallest useful question.

---

## 2. Why a minimal pilot is needed
At present, the ring degeneracy line is scientifically interesting but methodologically unresolved.

The project now has:
- a caution note about provenance-uncertain numbers
- an evidence-standard note defining what would count as a valid result

The missing bridge between those two is a **minimal pilot**:
a small test that is:
- disciplined
- reproducible
- interpretable
- and narrow enough not to hide behind complexity

This note defines that pilot.

---

## 3. Minimal pilot objective
The pilot should answer only this:

> **Does controlled degeneracy lifting in the ring create a consistent directional trend in the raw metrics that weakens `delta_p` dominance and strengthens `delta_p2`-related behavior?**

Important:
- this is not yet a proof of universal `delta_p2` relevance
- not yet a full ring theory
- and not yet a final project conclusion

It is only a pilot trend test.

---

## 4. Minimal design principles
The pilot should satisfy the following principles:

### 4.1 Small scope
Use only:
- one ring family
- one explicitly defined perturbation family
- one controlled strength sweep

### 4.2 Raw metrics first
Treat winner-labels only as secondary.
Primary outputs must be raw metric trajectories.

### 4.3 Reproducible structure
The pilot must run in normal project style:
- explicit config
- explicit runner
- persisted outputs
- interpretation note

### 4.4 No hidden rescue logic
The pilot must have an outcome logic defined in advance.
It must be possible for the pilot to:
- support the hypothesis
- weaken it
- or fail to support it

---

## 5. Minimal input structure

### 5.1 Family
Use one well-defined ring family only.

### 5.2 Perturbation family
Use one explicit degeneracy-lifting perturbation only.

This perturbation must be documented by:
- mathematical form
- intervention point
- physical / structural justification

The pilot should not combine multiple perturbation families yet.

### 5.3 Strength sweep
Use a fine but still small sweep, for example:

- 0.00
- 0.02
- 0.05
- 0.10
- 0.15
- 0.20
- 0.25
- 0.30

The exact values may be adjusted, but the sweep should be:
- fine enough to see gradual change
- small enough to remain interpretable

---

## 6. Core outputs
The pilot must record at least the following raw outputs per perturbation strength:

- `delta_p_strength`
- `delta_p2_strength`
- `dominance_margin`
- `sign_sensitivity_flag`
- `delta_p2_blind_to_direction_flag`

Optional but useful:
- branch match fractions
- auxiliary readout scores
- spread / variance across seeds or repeated runs if stochasticity is real

Secondary outputs:
- dominant label (`delta_p`, `delta_p2`, mixed)

The dominant label alone is not sufficient.

---

## 7. Minimal result package
The pilot should minimally produce:

- `config_ring_degeneracy_minimal_pilot.yaml`
- executable runner file
- raw metrics table (CSV)
- `summary.json`
- short interpretation note
- optional quick plot of metric trajectories

This is the minimum acceptable artifact set.

---

## 8. Decision logic defined in advance
The pilot should be judged by a pre-declared interpretation logic.

## 8.1 Supportive trend
The pilot is considered supportive if:
- `delta_p2_strength` increases systematically with perturbation strength
- `delta_p_strength` weakens or loses relative dominance
- `dominance_margin` shifts in a coherent direction
- and the trend is not explained by a single brittle winner-flip only

This would support the reading:
- the ring may be a symmetry-sensitive boundary case
- degeneracy lifting can partially or strongly expose `delta_p2` behavior

---

## 8.2 Non-supportive trend
The pilot is considered non-supportive if:
- raw metrics remain essentially flat
- only noise-like flips occur
- `delta_p2` gains no systematic strength
- or all visible changes are confined to unstable winner-label toggles

This would support the reading:
- the ring remains a resistant `delta_p`-dominated boundary case under this perturbation

---

## 8.3 Ambiguous trend
The pilot is ambiguous if:
- some shift is visible
- but the shift is weak, non-monotonic, or heavily implementation-sensitive
- or raw metric movement does not translate into a stable interpretive trend

This would justify:
- second-wave refinement
- but not a strong result claim

---

## 9. Three acceptable pilot outcomes
The pilot should be allowed to end in three different ways.

### Outcome A — No meaningful shift
Ring remains robustly `delta_p`-dominated.
Interpretation:
- strong resistant boundary case

### Outcome B — Partial transition
`delta_p2` gains ground, but no robust dominance emerges.
Interpretation:
- mixed or symmetry-sensitive transitional boundary case

### Outcome C — Robust transition trend
`delta_p2` gains systematic and reproducible strength under lifting.
Interpretation:
- ring behaves as a symmetry-protected special case rather than a universal counterexample

All three outcomes are scientifically useful.

---

## 10. Failure modes to watch for
The pilot should explicitly check for the following failure modes:

### 10.1 Cosmetic perturbation
The intervention touches only a convenience-level variable without changing the meaningful structural layer.

### 10.2 Binary-only illusion
A winner-flip appears, but raw metric margins do not support a real shift.

### 10.3 Threshold artifact
The observed trend is driven mainly by thresholding choices rather than by the perturbation itself.

### 10.4 Hidden implementation asymmetry
The trend is caused by pipeline asymmetry rather than by real degeneracy lifting.

### 10.5 Over-interpretation
A weak monotonic drift is overstated as a strong physical transition.

These must be considered before any synthesis note is written.

---

## 11. Safe interpretation language
A safe positive formulation would be:

> Under the tested ring degeneracy-lifting perturbation, the raw metric readouts show a systematic directional shift away from pure `delta_p` dominance and toward stronger `delta_p2`-related behavior. This supports treating the ring as a symmetry-sensitive boundary case, while remaining below any claim of universal `delta_p2` recovery.

A safe negative formulation would be:

> Under the tested perturbation, the ring remains predominantly `delta_p`-dominated, with no robust or reproducible shift toward `delta_p2` behavior. This strengthens the reading of the ring as a genuine resistant boundary case for the present interpretation.

---

## 12. Recommended immediate next step
The immediate next step is not a full external report, but a project-compatible pilot implementation with:

- one ring family
- one perturbation family
- one controlled strength sweep
- raw metrics persisted
- and a short interpretation note

Only after that should second-wave refinements be considered.

---

## 13. Bottom line
The minimal clean ring pilot is not meant to settle the ring question in full.
It is meant to answer one narrow but important question:

> **Does explicit degeneracy lifting produce a reproducible raw-metric shift in the ring consistent with weakening pure `delta_p` dominance and strengthening `delta_p2`-related behavior?**

If yes, the ring becomes a more structured symmetry-boundary case.  
If no, the ring becomes a stronger resistant counter-case.  
If mixed, the ring remains an open transitional test family.

That is the correct role of the minimal pilot.
