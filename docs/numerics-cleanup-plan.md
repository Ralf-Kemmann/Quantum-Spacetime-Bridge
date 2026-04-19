# Numerics Cleanup Plan

## Purpose of this document

This document defines the current cleanup and curation plan for the imported numerical subtree:

```text
numerics/debroglie-phase-bridge/
```

The goal is not to hide or silently remove material, but to make the consolidated numerical project tree more readable, maintainable, and reviewable while preserving the project’s transparency standards.

## Current status

The numerical project tree has already been **consolidated** into the main **Quantum–Spacetime Bridge** repository.

This was the correct first step because it removed the need to maintain two operational repositories.

However, the imported tree is still a **grown research work tree**, not yet a fully curated repository section. It contains:

- active code
- historical code
- run outputs
- notes
- backup traces
- scaffolds
- repeated documentation fragments
- deep result trees
- likely accidental or low-value files

This means the present task is now **curation**, not further relocation.

## Cleanup principle

The cleanup must follow a strict project rule:

> no hidden calculations, no hidden files, no hidden code, and no opaque result handling

Therefore the cleanup plan must be:

- explicit
- documented
- reversible where needed
- conservative before deletion
- transparent in intent and execution

## Main cleanup goals

The cleanup work should pursue five goals:

1. make the numerics subtree easier to navigate  
2. distinguish active material from historical or archival material  
3. identify accidental or low-value files  
4. reduce noise without destroying provenance  
5. preserve scientific traceability

## Cleanup categories

The imported tree should be reviewed in the following categories.

### 1. Active core material

This includes files and directories that are likely part of the active numerical and methodological base.

Typical candidates:

- `src/`
- `scripts/`
- `tests/`
- selected `configs/`
- selected `results/`
- selected `typ_b_analysis/src/`
- selected `typ_b_analysis/configs/`
- selected `typ_b_analysis/runs/`
- selected `typ_b_analysis/results/`

These areas should be retained and later documented more precisely.

### 2. Historical but scientifically relevant material

This includes older notes, prior run outputs, and legacy project states that may still matter for provenance, comparison, or reviewer traceability.

Typical candidates:

- `notes/`
- `docs/theory/`
- `docs/reviews/`
- `m33_v0_scaffold/`
- `typ_b_analysis/notes/`
- `typ_b_analysis/notes_archive/`
- older run directories
- historical result snapshots

These areas should usually be **retained first**, but may later be moved into a more clearly labeled archive structure.

### 3. Obvious cleanup candidates

This category includes files that are suspicious, accidental, redundant, or unlikely to be legitimate long-term project assets.

Examples already visible from the imported tree include likely candidates such as:

- `.bak` files
- malformed filenames
- duplicate status files
- accidental scratch files
- structurally unclear leftovers

These files should **not** be deleted silently. They should first be listed, reviewed, and then either:
- removed,
- renamed,
- or moved into an explicit archive/quarantine area.

## First review targets

The first cleanup pass should focus on the following targets.

### A. Suspicious filenames

Examples already identified include names that deserve inspection, such as:

- `typ_b_analysis/configs/run:.yaml`
- `typ_b_analysis/src/from __future__ import annotations.py`

These should be reviewed first because they look like probable accident artifacts rather than intended project files.

### B. Backup files

Examples:
- `*.bak`

These should be inventoried and then either removed or moved into a clearly marked archival area if they still matter.

### C. Duplicate or near-duplicate status material

The tree contains multiple masterchat/status-like files with similar names and overlapping dates. These should be reviewed to determine:

- canonical version
- archive version
- redundant version

### D. Extremely deep result trees

Some result areas are large and structurally dense. These should be checked for:

- current relevance
- reproducibility importance
- whether everything needs to remain in-place
- whether a summarized index would help more than raw accumulation

## Recommended cleanup workflow

The cleanup should follow this sequence:

### Step 1 — inventory
Create a written inventory of:
- suspicious files
- backup files
- duplicate files
- unclear folders
- likely archive candidates

### Step 2 — classify
For each candidate, assign one of the following statuses:

- **active**
- **historical-relevant**
- **archive**
- **unclear-needs-review**
- **remove-after-review**

### Step 3 — document before action
Before moving or deleting anything important, write the action into a short cleanup note or change log.

### Step 4 — archive before delete
Wherever there is doubt, prefer:
- explicit archive location
over
- immediate deletion

### Step 5 — only then reduce
After review and classification, reduce noise in a controlled and documented way.

## Suggested future supporting files

To make this process easier, the following supporting documents would be useful:

- `docs/numerics-inventory.md`
- `docs/numerics-active-areas.md`
- `docs/numerics-archive-policy.md`

These do not all need to be created immediately, but they would support long-term maintainability.

## What should not happen

The following would be poor cleanup practice and should be avoided:

- deleting “ugly” files without inspection
- silently removing historical result trees
- moving active numerics into undocumented side locations
- making the repository cleaner at the price of lower transparency
- mixing archive and active material without labels

## Practical interpretation of the current state

The right reading of the current numerics subtree is:

- it is now **centralized**
- it is **not yet curated**
- it is usable as a working base
- but it still needs a documented hygiene pass

That is acceptable as long as the repository remains honest about it.

## Bottom line

The imported numerical subtree should now undergo a **transparent cleanup and curation phase**, not a hidden reduction phase.

The main rule is:

> first inventory, then classify, then document, then archive or clean up

This preserves credibility, keeps the numerics visible, and turns the current “monster” into a mapped and maintainable project structure rather than an opaque mass of files.
