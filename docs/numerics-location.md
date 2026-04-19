# Numerics Location

## Purpose of this document

This document explains where the deeper numerical and analysis-heavy project material is now located inside the **Quantum–Spacetime Bridge** repository.

Its purpose is to make the repository structure transparent for maintainers, reviewers, and users. After the consolidation of the former `debroglie-phase-bridge` working tree into the current repository, it became especially important to document the new location and role of the imported numerical project material.

## Current location of the numerical project tree

The deeper numerical project material is now located under:

```text
numerics/debroglie-phase-bridge/
```

This subtree contains the consolidated contents of the earlier numerical working repository and should now be treated as the main internal location for the legacy and ongoing numerics-heavy project infrastructure that was formerly maintained separately.

## Why this subtree exists

The project had reached a point where two separate repositories would have created unnecessary maintenance overhead and increased the risk of drift between:

- outward-facing project presentation
- internal numerical development
- supporting documentation
- result material
- working notes and structured runs

To avoid maintaining two operationally active repositories, the numerical project tree was consolidated into the current **Quantum–Spacetime Bridge** repository.

This means:

- outward-facing project framing remains at repository root and in `docs/`
- the deeper numerics-heavy project material now lives under `numerics/debroglie-phase-bridge/`
- future work should, in principle, be continued from this consolidated location rather than split across repositories

## What lives in `numerics/debroglie-phase-bridge/`

The imported subtree contains a broad research and implementation structure, including:

- numerical scripts and executable helpers
- source code and package logic
- configurations
- raw/interim/processed data directories
- results and run outputs
- tests
- notes and working material
- theory-facing documentation
- M33/M39x scaffold structures
- `typ_b_analysis` as a large internal analysis branch

In short: this subtree is not just a code folder. It is a substantial research work tree.

## Relationship to the repository root

The repository root and the numerics subtree serve different roles.

### Repository root

The repository root is primarily the **public scientific entrance layer**. It contains:

- `README.md`
- outward-facing `docs/`
- citation and licensing files
- public links
- project-level orientation material

This layer answers:
- what the project is
- what it currently claims
- what it does not claim
- how the repository should be read

### `numerics/debroglie-phase-bridge/`

The numerics subtree is primarily the **deep working and evidence layer**. It contains the code, results, run structures, and accumulated numerical project material behind the outward-facing scientific framing.

This layer answers:
- where the numerical work actually lives
- how the results were generated
- which runs, scripts, notes, and internal structures belong to the deeper project history

## Transparency principle

The project follows a strict transparency rule for calculations, numerical work, and result discussion.

This means that the numerics subtree is not intended as a hidden backend. It is part of the openly documented project structure. Its location is explicitly documented so that:

- calculations remain traceable
- result discussions remain inspectable
- no hidden numerical layer is created behind the outward-facing project texts

This is a deliberate credibility safeguard.

## Why the old separate repository should not remain the active working base

The previous separate numerical repository may still exist temporarily as an archive or fallback reference. However, it should no longer be treated as the primary operational project base unless a specific recovery or comparison reason requires it.

The main reasons are:

- avoid double maintenance
- avoid diverging project states
- avoid uncertainty about which repository is authoritative
- keep outward-facing framing and deep numerics under one documented project roof

## Practical working rule

The practical rule from now on is:

- project presentation, overview, and public scientific framing live at repository root and under `docs/`
- deeper numerical and historical working material lives under `numerics/debroglie-phase-bridge/`
- if structural cleanup is required, it should happen *inside the consolidated repository*, not by returning to dual-repository maintenance

## Limitations of the current state

Although the numerics subtree is now centrally located, it is not yet fully curated.

The current state should therefore be understood as:

- **consolidated**
- but not yet fully **cleaned up**
- not yet fully **re-mapped**
- not yet fully **reduced to active essentials**

This is acceptable as an intermediate repository state, provided it is clearly documented.

## Recommended next step

The next step after documenting the location is to document the cleanup and curation plan for this imported numerical tree.

That follow-up document is:

- `docs/numerics-cleanup-plan.md`

## Bottom line

The deeper numerical project material for **Quantum–Spacetime Bridge** now lives under:

```text
numerics/debroglie-phase-bridge/
```

This subtree is the consolidated internal numerics and evidence layer of the project. It should be treated as the documented working base for the deeper computational and analytical material, while the repository root remains the outward-facing scientific entrance layer.
