# Numerics Active Areas

## Purpose of this document

This document identifies the currently active, semi-active, historical, and non-active areas of the consolidated numerics subtree inside the **Quantum–Spacetime Bridge** repository.

Its purpose is to improve orientation in a numerics-heavy research repository that contains not only code, but also run structures, historical notes, scaffolds, results, archive areas, and legacy working material.

A repository can be structurally clean and still remain hard to navigate. This note addresses that second problem.

## Scope

This document applies to the consolidated numerics subtree:

```text
numerics/debroglie-phase-bridge/
```

It is meant for maintainers, reviewers, and future project use. It does not replace detailed documentation of individual modules, but provides a high-level working map.

## Classification principle

The subtree is classified into four practical categories:

1. **active**  
   currently relevant for ongoing work, interpretation, or reproducibility

2. **semi-active**  
   not the main current focus, but still potentially relevant and not yet safely reducible

3. **historical / provenance-relevant**  
   older or secondary material that should remain available for traceability

4. **non-active managed storage**  
   quarantine or archive areas that are intentionally outside the active working layer

This classification is a working interpretation, not an eternal truth. It may be refined later.

## Active areas

The following areas are currently best treated as active.

### 1. `docs/project/MASTERCHAT_CANONICAL.md`

**Status:** active  
**Role:** single canonical internal masterchat for the numerics subtree

This file is currently the active canonical masterchat. It should be treated as the authoritative internal project guidance document for this numerics branch.

### 2. `src/`

**Status:** active  
**Role:** main source-code area for the imported numerical project tree

This area contains core package and implementation logic and is part of the active reproducibility layer.

### 3. `scripts/`

**Status:** active  
**Role:** executable workflow and runner-side logic

This area contains execution-facing logic, helper scripts, and workflow entry points. Even where overlap with `src/` exists elsewhere in the repository, this area should currently be treated as active.

### 4. `tests/`

**Status:** active  
**Role:** verification and regression-support layer

This area remains part of the active reliability structure and should be preserved as such.

### 5. `results/`

**Status:** active  
**Role:** currently relevant result layer for the imported numerical project tree

This directory contains result material that still belongs to the readable evidence surface of the numerics project.

### 6. `typ_b_analysis/`

**Status:** active  
**Role:** major active internal analysis branch

This is a substantial internal branch with its own source, configs, notes, results, runs, and diagnostics. It should currently be treated as an active analysis area, not as a passive archive.

## Semi-active areas

The following areas appear important but not yet fully classified as core-canonical current work areas.

### 1. `m33_v0_scaffold/`

**Status:** semi-active  
**Role:** structured scaffold area with internal branching

This subtree contains real structure and should not be treated as a simple duplicate. At least parts of it show internal divergence between branches such as `src/` and `scripts/`. It therefore remains relevant, but is not yet fully canonically resolved.

### 2. `configs/`

**Status:** semi-active  
**Role:** configuration base and experiment configuration layer

This area is clearly relevant, but the degree to which all contained configurations remain equally current is not yet fully classified.

### 3. `docs/theory/`, `docs/reviews/`, `docs/project/`

**Status:** semi-active  
**Role:** theory-facing and review-support documentation inside numerics tree

These materials may still be relevant depending on the line of work, but not all of them should automatically be assumed to define the current active working state.

### 4. `notes/`

**Status:** semi-active  
**Role:** local working notes and interpretation layer

This area may contain relevant conceptual and methodological material, but it is not a canonical top-layer guidance area in the same way as the canonical masterchat.

## Historical / provenance-relevant areas

The following areas should currently be treated as historically useful, provenance-relevant, or secondary-interpretation material.

### 1. `notebooks/`

**Status:** historical / provenance-relevant  
**Role:** exploratory or publication-side notebook material

These materials may remain useful for reconstruction or understanding, but they are typically not the most stable active working layer.

### 2. `docs/figures/`

**Status:** historical / provenance-relevant  
**Role:** figure-support or presentation-side material

Potentially useful, but not usually a primary active logic area.

### 3. `archive/`

**Status:** historical / provenance-relevant  
**Role:** already marked legacy or old-export material

This area is already conceptually historical and should remain outside the active working interpretation.

### 4. `data/raw/`, `data/interim/`, `data/processed/`

**Status:** provenance-relevant  
**Role:** data-layer material

These areas are not “active” in the same sense as code or canonical guidance, but they are important for provenance and reproducibility.

### 5. `typ_b_analysis/notes_archive/`

**Status:** historical / provenance-relevant  
**Role:** structured historical note archive within the typ_b branch

This area is important for traceability but should not be confused with the active interpretation layer.

## Non-active managed storage areas

The following areas are intentionally non-active.

### 1. `_quarantine/`

**Status:** non-active managed storage  
**Role:** malformed, misnamed, or unsafe active-tree artifacts removed from active paths

### 2. `_archive_masterchat_noncanonical/`

**Status:** non-active managed storage  
**Role:** masterchat-like files preserved but not treated as active canonical guidance

### 3. `docs/_archive/`

**Status:** non-active managed storage  
**Role:** documentation-side archive for non-canonical drafts

### 4. local `_archive_heavy/` areas

**Status:** non-active managed storage  
**Role:** heavy run artifacts moved out of active run surfaces while retained in place

## Recommended reading path for maintainers

A maintainer or project collaborator should generally orient themselves in this order:

1. `docs/project/MASTERCHAT_CANONICAL.md`
2. `src/`
3. `scripts/`
4. `tests/`
5. `results/`
6. `typ_b_analysis/`
7. `m33_v0_scaffold/`
8. `notes/`
9. provenance and archive areas only as needed

## Recommended reading path for reviewers

A technically curious reviewer interested in the numerics subtree may prefer:

1. canonical masterchat
2. result-facing directories
3. source and script areas
4. tests
5. typ_b analysis branch
6. scaffold areas
7. archive and provenance material only if needed for traceability

## What this classification is trying to prevent

This document is meant to prevent three common repository problems:

1. treating everything as equally active  
2. treating historical material as if it were current guidance  
3. overlooking active subtrees because the repository contains too much legacy mass

The goal is not to reduce the subtree by rhetoric, but to make its working logic visible.

## Limits of the current classification

The current classification is still provisional in some important places.

Most notably:
- the M33 scaffold area is not yet canonically resolved
- not all config branches are yet fully classified
- not all note families are yet separated into active vs. historical subsets

This is acceptable as long as the uncertainty remains explicit.

## Suggested future follow-up

A useful follow-up document would be:

- `docs/numerics-canonical-structure.md`

That later document could refine the current map into a more stable canonical working architecture once the major sub-branches have been more fully classified.

## Field list

1. `scope` — String — numerics subtree to which the classification applies  
2. `classification_category` — String — one of `active`, `semi-active`, `historical / provenance-relevant`, `non-active managed storage`  
3. `area_path` — String — path of the subtree or file being classified  
4. `status` — String — current working status of the area  
5. `role` — String — short explanation of the function of the area  
6. `maintainer_reading_order` — String — suggested sequence for maintainers to approach the subtree  
7. `reviewer_reading_order` — String — suggested sequence for external or technical readers  
8. `classification_limit` — String — explicit limit or unresolved part of the current classification  
9. `follow_up_candidate` — String — possible future refinement document or classification pass

## Bottom line

The numerics subtree is no longer just “the big imported block.” It now has a readable working map.

Some areas are clearly active, some are semi-active and still structurally unresolved, some are historical but important for provenance, and some are intentionally non-active archive or quarantine storage.

This distinction is necessary if the repository is to remain both transparent and navigable.
