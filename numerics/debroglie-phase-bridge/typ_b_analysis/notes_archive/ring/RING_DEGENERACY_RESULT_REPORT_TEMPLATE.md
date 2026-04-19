# RING_DEGENERACY_RESULT_REPORT_TEMPLATE

## Template for reporting a ring degeneracy perturbation pilot result

**Date:** 2026-04-06  
**Status:** internal reporting template

---

## 1. Purpose
This template defines how a ring degeneracy perturbation pilot should be reported once a clean project-compatible run exists.

Its purpose is to prevent three common reporting failures:

- making the result look stronger than it is
- reporting only exciting labels without the raw metric basis
- skipping artifact and limitation discussion

This template should be used after:
- provenance is clear
- the pilot has been run
- and the decision logic category has been assigned

It is not a synthesis document.
It is a disciplined pilot report format.

---

## 2. Report header

### Run identification
- **Run ID:**  
- **Date:**  
- **Author / operator:**  
- **Project block:** `M.3.9x.3 ring degeneracy perturbation`
- **Status:** draft / reviewed / archived

### Input context
- **Family tested:**  
- **Perturbation family:**  
- **Intervention point:**  
- **Strength sweep:**  
- **Seed logic / repeat logic:**  
- **Config file:**  
- **Runner file:**  

---

## 3. Minimal one-paragraph executive summary
Use only one paragraph here.

Template:

> This pilot tested whether an explicitly defined degeneracy-lifting perturbation in the ring produces a systematic shift in raw readout metrics away from pure `delta_p` dominance and toward stronger `delta_p2`-related behavior. The run was performed with clear provenance and persisted outputs. Under the applied perturbation, the observed result is best classified as [Category A / B / C / D / E], meaning [short safe interpretation only].

No ontological escalation here.

---

## 4. Intervention description
Describe the perturbation in plain, explicit terms.

### Required fields
- Mathematical form of perturbation
- Structural level of intervention
- Why this intervention is relevant to degeneracy lifting
- What was intentionally *not* changed

### Example subheading
**Intervention description**

Template:
> The pilot applied [perturbation] at the level of [state structure / spectrum / mode construction / kernel-relevant layer]. The intention was to lift the relevant ring degeneracy without introducing unrelated structural changes. No modification was made to [other layers].

---

## 5. Raw metric summary
This is the core of the report.

### Required primary metrics
For each perturbation strength, report at least:
- `delta_p_strength`
- `delta_p2_strength`
- `dominance_margin`
- `sign_sensitivity_flag`
- `delta_p2_blind_to_direction_flag`

### Preferred table layout
| strength | delta_p_strength | delta_p2_strength | dominance_margin | sign_sensitivity | blind_to_direction |
|---|---:|---:|---:|---:|---:|

Optional:
- additional readout metrics
- spread / variance
- branch fractions

Important:
- raw metrics first
- labels only after the table

---

## 6. Secondary label summary
This section is explicitly secondary.

### Allowed fields
- dominant label per strength
- category fractions if repeated runs were used
- mixed / transition labels if needed

### Preferred wording
> The winner-label summary is reported here only as a compressed secondary view. Interpretation remains anchored in the raw metric trajectories above.

This sentence should stay.

---

## 7. Decision logic assignment
Assign exactly one category from the ring decision note:

- **Category A — No meaningful effect**
- **Category B — Weak drift only**
- **Category C — Partial transition trend**
- **Category D — Robust transition trend**
- **Category E — Inconclusive due to artifact risk**

### Required explanation
State:
- which category was assigned
- why
- and which decision criteria were decisive

### Template
> The pilot is assigned to **Category X** because [brief reason based on raw metric behavior, not only labels].

---

## 8. Three-sentence safe interpretation
This section must be short and disciplined.

### Sentence 1
What happened in the raw metrics?

### Sentence 2
What does that mean for the ring under this perturbation?

### Sentence 3
What does it *not* justify yet?

### Template example
> The raw metrics show a [flat / weak / partial / robust] directional shift away from pure `delta_p` dominance and toward stronger `delta_p2`-related behavior. Under the tested perturbation, this supports reading the ring as a [resistant / transitional / symmetry-sensitive] boundary case. The result does not by itself justify any stronger universal claim beyond the tested intervention regime.

This format is preferred.

---

## 9. Artifact and limitation block
This section is mandatory.

### Required questions
- Could the result be threshold-driven?
- Could the intervention be too cosmetic?
- Is there any sign of implementation asymmetry?
- Is the sweep fine enough?
- Are raw metrics stronger than winner-label effects?
- What remains uncertain?

### Template heading
**Artifact and limitation assessment**

Template:
> The main remaining risks are [x, y, z]. In particular, [most serious limitation] should be considered before the result is used beyond internal pilot interpretation.

This should never be omitted.

---

## 10. Reproducibility checklist
Include a short checklist.

| Item | Status |
|---|---|
| Config persisted | yes / no |
| Runner persisted | yes / no |
| Raw metrics persisted | yes / no |
| Summary persisted | yes / no |
| Intervention point documented | yes / no |
| Decision logic category assigned | yes / no |
| Limitations stated | yes / no |

A result without this checklist is incomplete.

---

## 11. Internal outcome classification
At the end, classify the reporting status:

- **Internal hypothesis only**
- **Preliminary internal indication**
- **Project-valid internal result**
- **Needs rerun before use**

### Template
> Final internal status: **[classification]**

This should be explicit.

---

## 12. What this template forbids
This report template explicitly forbids:

- reporting only labels without raw metrics
- hiding provenance
- skipping the limitation block
- escalating directly from pilot to ontology
- using the ring as rescue rhetoric for wider claims

This is a discipline template, not a persuasion template.

---

## 13. Recommended file bundle
A completed report should ideally live together with:

- `config_ring_degeneracy_minimal_pilot.yaml`
- runner script
- raw metrics CSV
- `summary.json`
- this report file
- optional quick plot

That is the minimal reporting bundle.

---

## 14. Bottom line
A ring degeneracy pilot result should be reported in a way that is:

- provenance-clear
- raw-metric anchored
- decision-logic disciplined
- limitation-explicit
- and resistant to narrative inflation

This template defines that reporting standard.
