# RING_DEGENERACY_POST_RUN_REVIEW_CHECKLIST

## Post-run review checklist for a ring degeneracy perturbation pilot

**Date:** 2026-04-06  
**Status:** internal review checklist

---

## 1. Purpose
This checklist is to be used **after** a ring degeneracy perturbation pilot has completed.

Its purpose is simple:

> **Do not let a finished run become an accepted result before it has passed an explicit post-run review.**

The ring is a boundary case.
Boundary cases are especially vulnerable to:
- attractive overinterpretation,
- brittle winner-flips,
- hidden provenance gaps,
- and artifact inflation.

This checklist is therefore a mandatory review layer between:
- finished run
and
- accepted internal interpretation

---

## 2. How to use this checklist
The checklist should be completed after:
- outputs are written,
- summary and report exist,
- and before the run is promoted beyond draft status.

Each item should be marked as:
- **yes**
- **no**
- **partial**
- or **not applicable**

A run with multiple critical “no” answers should not be promoted to:
- reviewed
- archived
- synthesis-ready
- or manuscript-facing status

---

## 3. Section A — Provenance and bundle integrity

### A1. Run identification
- Is the run ID explicit and unambiguous?
- Does the run folder correspond to the documented run ID?
- Is the stage label correct (`pilot`, `rerun`, `finesweep`, `altpert`)?

### A2. Required files present
- Is the config file present?
- Is the runner script present?
- Is `raw_metrics.csv` present?
- Is `summary.json` present?
- Is `report.md` present?

### A3. File coherence
- Do config, runner, summary, and report clearly belong to the same run?
- Is there any sign that files were copied from different runs without clear linkage?
- Can the run be understood without relying on chat history?

If not, stop here: the run is not reviewable yet.

---

## 4. Section B — Intervention clarity

### B1. Intervention defined
- Is the perturbation mathematically described in the report?
- Is the intervention point explicitly stated?
- Is it clear what structural level was perturbed?

### B2. Intervention realism
- Does the perturbation plausibly act at a meaningful ring-structure level?
- Is there any risk that the intervention only touched a convenience-level variable?
- Is that risk explicitly mentioned if unresolved?

### B3. Scope discipline
- Was only the intended perturbation family used?
- Was the run kept within its declared pilot scope?
- Was no hidden rescue logic introduced after the fact?

---

## 5. Section C — Raw metric review

### C1. Primary metrics present
- Are `delta_p_strength` and `delta_p2_strength` both present?
- Is `dominance_margin` present?
- Are `sign_sensitivity_flag` and `delta_p2_blind_to_direction_flag` present?

### C2. Raw metrics readable
- Can the raw metric trajectories actually be inspected?
- Are they reported as tables, not only compressed labels?
- Are the outputs sufficient to reconstruct the trend independently?

### C3. Metric quality
- Do the metrics show a coherent story?
- Or are they contradictory / fragmented?
- If contradictory, is that clearly discussed?

If raw metrics are missing or unreadable, the run is not evidence-capable.

---

## 6. Section D — Decision logic compliance

### D1. Category assigned
- Was exactly one decision category assigned?
- Is the category one of A / B / C / D / E from the decision note?

### D2. Category justified
- Is the assigned category justified using raw metrics?
- Or was it justified mainly through winner-label behavior?

### D3. Label discipline
- Were winner-labels treated as secondary rather than primary?
- Is there any sign that a binary label flip dominated the interpretation unfairly?

If the category assignment is label-driven but not raw-metric-driven, downgrade the run.

---

## 7. Section E — Robustness and trend quality

### E1. Directionality
- Is there a visible directional trend?
- Is it monotonic or at least coherently directional?
- Or is it only flickering around thresholds?

### E2. Magnitude
- Is the movement large enough to matter?
- Or is the trend too weak to support the assigned category?

### E3. Sweep quality
- Is the sweep dense enough to support the interpretation?
- Is the apparent transition confined to one isolated point?
- Was a suspicious transition region identified for later fine sweep?

### E4. Repeat logic
- If repeated runs / seeds were used, are spread and consistency visible?
- If no repetition was used, is that limitation clearly stated?

---

## 8. Section F — Artifact review

### F1. Threshold artifact risk
- Could the trend be mainly due to thresholding?
- Was this considered explicitly?

### F2. Cosmetic perturbation risk
- Could the observed effect come from a superficial intervention rather than true degeneracy lifting?

### F3. Implementation asymmetry risk
- Is there any obvious implementation asymmetry that could generate a false trend?

### F4. Binary-only illusion risk
- Could the “result” be mostly a winner-label illusion without strong raw-metric support?

### F5. Alternative explanation named
- Is the most plausible trivial alternative explanation explicitly named in the report?

If artifact risk is serious and not addressed, the run should stay provisional.

---

## 9. Section G — Reporting quality

### G1. Executive summary discipline
- Is the executive summary short, clear, and non-inflated?
- Does it avoid ontological escalation?

### G2. Safe interpretation
- Does the report include a safe three-sentence interpretation?
- Does it clearly state what the run does **not** justify?

### G3. Limitation block
- Is there a dedicated artifact / limitation section?
- Is it specific rather than perfunctory?

### G4. Internal status stated
- Is the final internal status explicitly stated?
- Is the status justified by the actual review outcome?

---

## 10. Section H — Promotion decision
After the checklist is completed, assign one of the following review outcomes.

### H1. Draft only
Use if:
- provenance is incomplete
- key files are missing
- raw metrics are insufficient
- or artifact risk is too high

### H2. Reviewed, but not synthesis-ready
Use if:
- the run is complete and interpretable
- but still too weak, ambiguous, or artifact-sensitive for synthesis

### H3. Reviewed and synthesis-eligible
Use if:
- provenance is clear
- raw metrics are strong
- category logic is sound
- and limitations are explicit but not disqualifying

### H4. Needs rerun before any use
Use if:
- intervention realism is doubtful
- files are incoherent
- or interpretation depends on unresolved critical artifacts

This promotion decision should be explicit.

---

## 11. Minimal final review statement
At the end of the checklist, include one short review statement.

### Template
> Post-run review outcome: **[draft only / reviewed but not synthesis-ready / reviewed and synthesis-eligible / needs rerun before any use]** because [short reason].

This final sentence is mandatory.

---

## 12. What this checklist forbids
This checklist forbids the following post-run behavior:

- promoting a run because the trend looks exciting
- skipping raw metric inspection
- accepting label flips without margin review
- ignoring artifact warnings
- using incomplete bundles as if they were archived evidence
- silently upgrading `draft` to `reviewed`

No exceptions.

---

## 13. Bottom line
A ring degeneracy pilot is not trustworthy just because it finished.

It becomes trustworthy only if:
- the run bundle is complete,
- the intervention is clear,
- the raw metrics are readable,
- the category assignment is justified,
- artifact risks are reviewed,
- and the final promotion status is made explicit.

That is the correct post-run review discipline for the ring degeneracy line.
