# RING_DEGENERACY_EVIDENCE_STANDARD_NOTE

## Minimal evidence standard for a project-valid ring degeneracy perturbation result

**Date:** 2026-04-06  
**Status:** internal methods note / evidence threshold definition

---

## 1. Purpose
This note defines the minimum evidence standard required for a ring degeneracy perturbation result to count as a **project-valid result** rather than merely:

- an interesting idea,
- a suggestive numerical tendency,
- or a provenance-uncertain hint.

The immediate reason for this note is that ring-related degeneracy-lifting numbers were circulated without sufficiently clear provenance.  
That episode made one thing explicit:

> **The ring degeneracy line is scientifically interesting, but it must only enter the project result layer if it satisfies a stricter reproducibility and interpretation standard.**

This note therefore answers a practical question:

> **What would have to be true for a ring degeneracy perturbation outcome to be accepted as evidence within the project?**

---

## 2. Why a separate evidence standard is needed
The ring is not just another family.
Within the current project logic, it is a potential **boundary case**.

That makes it methodologically special for two reasons:

### 2.1 The ring can over-influence interpretation
Because the ring can behave differently from cavity/membrane-like families, it is easy to overread it:
- either as a universal counterexample,
- or as a dramatic rescue case for a preferred interpretation.

Both are dangerous.

### 2.2 The ring is attractive but fragile
A degeneracy-lifting result is precisely the kind of thing that can look compelling even when:
- the intervention point is too naive,
- the provenance is unclear,
- the output is too binary,
- or the effect is not robust.

So the ring requires an explicit evidence threshold.

---

## 3. Three status levels
For the project, ring degeneracy outcomes should be classified into three distinct levels.

## 3.1 Level 1 — Hypothesis
A plausible conceptual possibility such as:

- the ring may be a symmetry-protected `delta_p` boundary case
- explicit degeneracy lifting may increase `delta_p2` influence
- under stronger perturbation, dominance may shift

At this level:
- no trusted numbers are required
- no result is claimed
- the idea is only a test direction

---

## 3.2 Level 2 — Preliminary indication
A numerical tendency may be seen in a trial implementation, but one or more of the following are still unresolved:
- provenance
- intervention realism
- reproducibility
- raw metric transparency
- robustness

At this level:
- the trend may be discussed internally
- but not used as accepted project evidence

---

## 3.3 Level 3 — Project-valid result
A ring degeneracy perturbation outcome may count as a project-valid result only if the full evidence standard below is met.

Only this level allows the result to be used as:
- internal evidence
- synthesis material
- or possible later manuscript support

---

## 4. Core evidence conditions
A project-valid result must satisfy all of the following core conditions.

## 4.1 Provenance condition
The result must have clear and complete provenance:
- runner name
- config file
- exact perturbation definition
- intervention point
- input family description
- seed or sweep definition
- output files

No provenance, no evidence.

---

## 4.2 Intervention condition
The perturbation must act at a scientifically meaningful point in the ring model.

That means it must be clear whether the degeneracy lifting affects:
- spectrum
- state structure
- mode mixing
- kernel-relevant object construction
- or only a convenience-level variable

A merely cosmetic intervention does not satisfy the standard.

---

## 4.3 Reproducibility condition
The result must be reproducible in the normal project style:
- executable runner
- config-driven run
- raw output persisted
- summary persisted
- rerunnable by the same pipeline logic

A screenshot, ad hoc printout, or undocumented table is insufficient.

---

## 4.4 Metric transparency condition
The result must not rely only on winner-flags such as:
- `delta_p` dominant
- `delta_p2` dominant

Instead, it must retain raw metric information such as:
- `delta_p_strength`
- `delta_p2_strength`
- dominance margin
- sign sensitivity
- direction blindness or related auxiliary flags
- variance or spread across seeds / sweeps where applicable

This is essential because boundary cases are often informative precisely through near-transitions, not only through final labels.

---

## 4.5 Robustness condition
A claimed tendency must survive at least a minimal robustness check.

This may include one or more of:
- multiple perturbation strengths
- fine sweep around the apparent transition region
- multiple seeds if stochasticity is real
- a second perturbation family
- or a small implementation-variant test

A single isolated flip is not enough.

---

## 4.6 Alternative-explanation condition
The most plausible non-interesting explanation must be named and checked.

Examples:
- metric artifact
- arbitrary threshold effect
- naive energy relabeling without real state deformation
- pipeline-specific asymmetry
- discretization artifact

A result becomes stronger when its nearest trivial explanation has been weakened.

---

## 5. Minimum acceptable output package
To count as a project-valid result, the ring degeneracy test should minimally produce:

- `config_ring_degeneracy_perturbation.yaml`
- executable runner script
- `summary.json`
- raw metrics table (CSV or equivalent)
- short interpretation note / report
- explicit statement of intervention point
- explicit statement of limitations

This is the minimal project package.

---

## 6. What would count as success
A successful project-valid ring degeneracy result would not need to prove a universal law.

It would be sufficient to show something like:

### Safe success form
> Under an explicitly defined and reproducible degeneracy-lifting perturbation, the ring shows a systematic weakening of `delta_p` dominance and a corresponding strengthening of `delta_p2`-related behavior, with the effect remaining visible across a controlled perturbation sweep.

This would already be valuable because it would support the interpretation of the ring as:
- a symmetry-sensitive boundary case
rather than
- a simple universal counterexample

---

## 7. What would count as failure
The following would count as non-supportive or failure outcomes:

### 7.1 No robust tendency
The apparent shift disappears under rerun or fine sweep.

### 7.2 Purely cosmetic dependence
The effect is seen only when perturbing a convenience-level variable, but vanishes when intervening at the proper structural level.

### 7.3 Binary-only illusion
The dominance flip exists only in a brittle winner-flag while raw metric margins remain unstable or inconsistent.

### 7.4 Strong alternative explanation
The effect can be explained more simply by thresholding, implementation asymmetry, or metric artefact.

### 7.5 Ring remains delta_p-dominated under meaningful lifting
This would not invalidate the project.
It would instead strengthen the ring’s status as a genuine resistant boundary case.

---

## 8. Interpretation matrix

| Status | Condition | Safe interpretation |
|---|---|---|
| Hypothesis | Conceptual plausibility only | Useful test idea, not evidence |
| Preliminary indication | Some numerical tendency, but one or more core conditions missing | Internal hint only |
| Project-valid result | Provenance, intervention, reproducibility, metric transparency, robustness, and alternative-check all sufficiently met | Usable internal evidence |

---

## 9. Recommended current stance
The correct current project stance is:

> The ring degeneracy line is scientifically worth pursuing, but no currently circulated provenance-uncertain numbers should be counted as evidence. The ring remains a valuable boundary-case hypothesis until a project-valid perturbation result is obtained under the full evidence standard.

This protects both:
- the scientific opportunity,
- and the methodological integrity of the project.

---

## 10. Operational next step
The next acceptable step is not theoretical debate about the ring, but a clean pilot run designed to satisfy the evidence standard as far as possible.

That means:
- explicit perturbation model
- explicit intervention point
- raw metric output
- controlled sweep
- summary plus interpretation note

Only then can the ring move from:
- attractive hypothesis
to
- accepted project evidence

---

## 11. Bottom line
A ring degeneracy perturbation result should count as project-valid only when it is:
- provenance-clear,
- structurally meaningful,
- reproducible,
- metrically transparent,
- robust,
- and resistant to trivial alternative explanation.

Until then, the ring degeneracy line remains a promising but unconfirmed hypothesis track.

That is the current evidence standard.
