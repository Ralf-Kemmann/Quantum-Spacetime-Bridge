# RING_DEGENERACY_OUTPUT_BUNDLE_SPEC

## Output bundle specification for a project-compatible ring degeneracy pilot

**Date:** 2026-04-06  
**Status:** internal reproducibility / archive specification

---

## 1. Purpose
This note defines the minimal output bundle required for a ring degeneracy perturbation pilot to be:

- reproducible,
- reviewable,
- archivable,
- and later usable for synthesis.

The goal is not just to run a test.
The goal is to leave behind a run artifact that can still be understood later without relying on memory, chat context, or oral explanation.

This note therefore answers:

> **What files must exist after a clean ring degeneracy pilot, and what must each file contain?**

---

## 2. Why a bundle specification is needed
The project has already identified several risks in the ring line:

- provenance uncertainty
- overinterpretation of isolated numbers
- unclear intervention point
- binary labels without raw metric context

A proper output bundle protects against exactly these risks.

Without a bundle specification, even a good pilot can later become unusable because:
- the config is missing
- the runner is unclear
- the raw metrics are gone
- the interpretation is detached from the data
- or the decision logic cannot be reconstructed

So the bundle itself is part of the evidence standard.

---

## 3. Minimal required files
A project-compatible ring degeneracy pilot should minimally produce the following files.

### 3.1 Config file
**Filename (preferred):**
`config_ring_degeneracy_minimal_pilot.yaml`

**Purpose:**
Defines the run conditions.

**Minimum content:**
- run ID
- family tested
- perturbation family
- intervention point
- perturbation strengths
- seed logic or repeat logic
- metric settings
- output paths

This file is mandatory.

---

### 3.2 Runner script
**Filename (preferred):**
`ring_degeneracy_minimal_pilot.py`

**Purpose:**
Documents the executable logic of the run.

**Minimum content:**
- input loading
- perturbation application
- metric computation
- output writing
- summary generation

This file must match the config and actual run behavior.

---

### 3.3 Raw metrics table
**Filename (preferred):**
`raw_metrics.csv`

**Purpose:**
Stores the primary evidential layer.

**Minimum content per row:**
- perturbation strength
- repeat / seed identifier (if applicable)
- `delta_p_strength`
- `delta_p2_strength`
- `dominance_margin`
- `sign_sensitivity_flag`
- `delta_p2_blind_to_direction_flag`

Optional:
- branch fractions
- auxiliary readout metrics
- implementation notes

This file is mandatory.

---

### 3.4 Summary file
**Filename (preferred):**
`summary.json`

**Purpose:**
Provides compact machine-readable run interpretation.

**Minimum content:**
- run ID
- config reference
- family
- perturbation family
- number of sweep points
- whether stochastic repeats were used
- aggregated metric trends
- assigned decision category
- final internal status
- known limitations

This file is mandatory.

---

### 3.5 Short result report
**Filename (preferred):**
`report.md`

**Purpose:**
Provides human-readable interpretation in the project style.

**Minimum content:**
- intervention summary
- raw trend summary
- decision category
- safe interpretation
- artifact and limitation block
- final internal classification

This file is mandatory.

---

## 4. Strongly recommended optional files

### 4.1 Quick plot
**Filename (preferred):**
`quickplot_metrics.png`

**Purpose:**
Fast visual inspection of metric trajectories.

**Suggested contents:**
- `delta_p_strength` vs perturbation strength
- `delta_p2_strength` vs perturbation strength
- margin trend if possible

Optional, but strongly recommended.

---

### 4.2 Decision trace
**Filename (preferred):**
`decision_trace.json`

**Purpose:**
Makes explicit how the assigned category was reached.

**Suggested contents:**
- category candidates considered
- triggered conditions
- failed conditions
- artifact warnings
- final justification

Optional, but highly useful for review.

---

### 4.3 Execution log
**Filename (preferred):**
`run.log`

**Purpose:**
Records execution messages, warnings, and run-time notes.

Optional, but useful for debugging and provenance.

---

## 5. Recommended folder structure
A clean ring degeneracy run should ideally live in a dedicated run folder.

### Preferred structure
`runs/<run_id>/`
containing for example:

- `config_ring_degeneracy_minimal_pilot.yaml`
- `ring_degeneracy_minimal_pilot.py`
- `raw_metrics.csv`
- `summary.json`
- `report.md`
- `quickplot_metrics.png` (optional)
- `decision_trace.json` (optional)
- `run.log` (optional)

This is the preferred archive unit.

---

## 6. Minimum content rules by file

### 6.1 Config must answer
- what was tested?
- how was it perturbed?
- where was it perturbed?
- under which sweep / repeat conditions?

### 6.2 Raw metrics must answer
- what happened numerically?
- at which perturbation strength?
- with which spread if repeated?

### 6.3 Summary must answer
- what is the compressed result?
- which category was assigned?
- what limitations remain?

### 6.4 Report must answer
- what should a human conclude safely?
- what should a human explicitly not conclude?

This division should be respected.

---

## 7. File naming discipline
The ring pilot should avoid vague file names such as:
- `test.csv`
- `results_final.json`
- `new_run.py`

Preferred naming should always indicate:
- family / purpose
- pilot scope
- and run role

Example:
- `config_ring_degeneracy_minimal_pilot.yaml`
- `ring_degeneracy_minimal_pilot.py`
- `raw_metrics.csv`
- `summary.json`
- `report.md`

Clear naming is part of provenance.

---

## 8. What must be present before synthesis
Before any synthesis note uses a ring degeneracy result, the following must already exist in the run bundle:

- config
- runner
- raw metrics
- summary
- report

If one of these is missing, the result should not be promoted into:
- synthesis notes
- review briefs
- or manuscript-facing interpretation

This is non-negotiable.

---

## 9. What the bundle must make impossible
A proper bundle should make it impossible to later ask:

- Where did this number come from?
- Which perturbation was this?
- Was this a real run or an illustrative table?
- Were these raw metrics or just winner-labels?
- Why was this category assigned?

If the bundle cannot answer these questions, it is incomplete.

---

## 10. Minimal archive checklist

| Item | Required? | Purpose |
|---|---|---|
| Config YAML | yes | run definition |
| Runner script | yes | executable provenance |
| Raw metrics CSV | yes | evidential core |
| Summary JSON | yes | compressed machine-readable result |
| Report MD | yes | human-readable interpretation |
| Quick plot | optional | rapid visual inspection |
| Decision trace | optional | explicit category path |
| Run log | optional | debugging and provenance support |

This checklist should be attached mentally to every run.

---

## 11. Bottom line
A ring degeneracy pilot is not project-compatible unless it leaves behind a complete bundle.

At minimum, that bundle consists of:
- config,
- runner,
- raw metrics,
- summary,
- and report.

Everything else is secondary.

This output bundle specification is therefore part of the ring evidence standard, not just a convenience rule.
