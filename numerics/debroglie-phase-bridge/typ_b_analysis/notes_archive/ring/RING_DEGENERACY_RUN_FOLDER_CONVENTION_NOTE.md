# RING_DEGENERACY_RUN_FOLDER_CONVENTION_NOTE

## Run-folder convention for a clean ring degeneracy pilot workflow

**Date:** 2026-04-06  
**Status:** internal run hygiene / folder convention note

---

## 1. Purpose
This note defines the preferred run-folder convention for ring degeneracy perturbation pilots.

The aim is practical and strict:

> **A ring pilot should live in a folder structure that makes provenance, interpretation, and later review possible without relying on memory, chat context, or oral reconstruction.**

This note therefore defines:
- how runs should be named,
- where they should live,
- which files belong together,
- how follow-up runs should be separated,
- and how pilot / rerun / fine-sweep stages should be distinguished.

This is a workflow note, not a physics note.

---

## 2. Why a folder convention is needed
The ring line has already shown why run hygiene matters.

Without explicit structure, later problems appear immediately:
- which config belonged to which run?
- which runner produced which summary?
- which output was only exploratory?
- which result was reviewed?
- which run was finally archived as the authoritative version?

For normal families this is already bad.
For a boundary case such as the ring it is worse, because interpretive discipline is especially important there.

So the folder convention is part of the evidence discipline.

---

## 3. Preferred top-level location
All ring degeneracy pilot runs should live under a dedicated project run path such as:

`runs/ring_degeneracy/`

This avoids mixing:
- ring pilot work
with
- unrelated family analyses
or
- older exploratory output

Preferred root:

`runs/ring_degeneracy/<run_id>/`

Each run gets its own folder.

---

## 4. Run ID convention
Run IDs should be:
- explicit
- stage-aware
- version-aware
- and human-readable

### Recommended pattern
`ring_degpert_<stage>_<version>`

Examples:
- `ring_degpert_pilot_v1`
- `ring_degpert_pilot_v2`
- `ring_degpert_rerun_v1`
- `ring_degpert_finesweep_v1`
- `ring_degpert_altpert_v1`

This is preferred over vague names such as:
- `ring_test`
- `run2`
- `new_ring_result`

The run ID should already tell the reader what kind of run it was.

---

## 5. Meaning of the stage labels
The following stage labels are recommended.

### 5.1 `pilot`
First disciplined minimal run.
Goal:
- detect whether a meaningful directional trend exists at all

### 5.2 `rerun`
Used when:
- provenance needs strengthening
- implementation needs correction
- or the same design must be re-executed cleanly

### 5.3 `finesweep`
Used when:
- a coarse trend exists
- and the perturbation region needs higher-resolution inspection

### 5.4 `altpert`
Used when:
- a second perturbation family is tested
- to distinguish perturbation dependence from generality

These labels should not be mixed casually.

---

## 6. Preferred folder content
Each run folder should minimally contain:

- `config_ring_degeneracy_minimal_pilot.yaml`
- `ring_degeneracy_minimal_pilot.py`
- `raw_metrics.csv`
- `summary.json`
- `report.md`

Optional but recommended:
- `quickplot_metrics.png`
- `decision_trace.json`
- `run.log`

This run folder is the atomic review unit.

---

## 7. Preferred internal folder structure
A flat run folder is acceptable.
But a lightly structured layout is even better.

### Recommended structure
`runs/ring_degeneracy/<run_id>/`
with:

- `config/`
  - config YAML

- `src/`
  - runner script used for that run

- `outputs/`
  - `raw_metrics.csv`
  - `summary.json`
  - optional plots

- `notes/`
  - `report.md`
  - optional decision trace

- `run.log` (optional, top level or outputs)

This keeps:
- execution logic,
- outputs,
- and interpretation
cleanly separated.

---

## 8. First-entry file
Every run folder should have a clear first-entry file for a reviewer or later self-review.

### Preferred first-entry file
`notes/report.md`

This file should tell a human:
- what was run,
- why,
- what happened,
- what category was assigned,
- and what the limitations are

If someone opens the run folder cold, `report.md` should be the first useful anchor.

---

## 9. Status discipline inside run folders
A run should not silently drift from exploratory to authoritative.

Each run should therefore have an explicit internal status.

### Allowed status labels
- `draft`
- `reviewed`
- `archived`

### Meaning
**draft**
- exploratory or not yet checked

**reviewed**
- internally checked against decision logic and evidence standard

**archived**
- accepted as stable project run artifact

The status may live:
- inside `summary.json`
- and/or at the top of `report.md`

This is strongly recommended.

---

## 10. How to treat follow-up runs
A follow-up run should never overwrite a previous run folder.

Instead:
- new run → new run ID
- old run remains intact

Examples:
- `ring_degpert_pilot_v1`
- `ring_degpert_pilot_v2`
- `ring_degpert_finesweep_v1`

This preserves provenance and allows comparison.

No destructive overwriting.

---

## 11. How to separate pilot, rerun, and fine sweep
The following distinction should be maintained:

### Pilot
One narrow first test.
Question:
- is there a directional signal at all?

### Rerun
Same conceptual design, cleaner or corrected execution.
Question:
- does the trend survive a clean rerun?

### Fine sweep
Resolution increase after a visible pilot trend.
Question:
- where exactly does the trend strengthen, flatten, or turn?

These are different run purposes and should remain visibly distinct in naming and reporting.

---

## 12. Archive hygiene rules
Before a run is promoted to synthesis use, check:

- does the run folder contain the full required bundle?
- is the status at least `reviewed`?
- is the report present?
- are raw metrics present?
- can the run be understood without chat context?

If not, do not promote it.

This is mandatory.

---

## 13. What this convention forbids
This convention forbids:

- storing raw metrics in one place and interpretation in another without linkage
- ambiguous run names
- overwriting earlier pilot folders
- mixing multiple perturbation families in one unidentified folder
- relying on “latest” or “final_final” naming
- using downloads as quasi-archive

These are all anti-patterns.

---

## 14. Minimal folder example

`runs/ring_degeneracy/ring_degpert_pilot_v1/`

containing:

- `config/config_ring_degeneracy_minimal_pilot.yaml`
- `src/ring_degeneracy_minimal_pilot.py`
- `outputs/raw_metrics.csv`
- `outputs/summary.json`
- `outputs/quickplot_metrics.png` *(optional)*
- `notes/report.md`
- `notes/decision_trace.json` *(optional)*
- `run.log` *(optional)*

This is the preferred reference layout.

---

## 15. Bottom line
A ring degeneracy pilot is only as trustworthy as its run hygiene.

The correct convention is:
- one run, one folder
- explicit run ID
- config + runner + raw outputs + report kept together
- no overwrite
- status visible
- report as first-entry file

That is the clean folder convention for the ring degeneracy line.
