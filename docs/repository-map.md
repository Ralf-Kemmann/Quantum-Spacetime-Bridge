# Repository Map

## Purpose of this document

This document provides a structured overview of the **Quantum–Spacetime Bridge** repository.

Its purpose is to help readers, reviewers, and maintainers understand:

- what kinds of material the repository contains
- where specific project information can be found
- how the current repository structure reflects the scientific workflow of the project
- how to approach the repository without getting lost in detail too early

For an intermediate-stage research project, this kind of overview is especially useful because the repository contains not only outward-facing texts, but also notes, figures, and evolving result material.

## General reading principle

The repository should be read from **orientation** to **methodological framing** to **supporting material**.

A good rule is:

> start with the project logic, then move to the scientific status, then inspect figures, notes, and results in more detail.

This order helps preserve the intended red thread of the project:

> motivation → model → test → finding → boundary → next step

## Top-level repository structure

```text
README.md
CITATION.cff
LICENSE
docs/
figures/
notes/
results/
links/
```

Each part of the repository has a distinct role.

## Top-level files

### `README.md`
Primary entry point into the repository.

This file gives the shortest outward-facing overview of the project. It is intended for first contact and should answer the most immediate questions:

- What is this project about?
- What is its current scientific status?
- What does it claim?
- What does it not claim?
- Where should a new reader go next?

### `CITATION.cff`
Repository citation metadata.

This file provides machine-readable and human-readable citation information for the project repository. It supports repository citation workflows and helps standardize outward-facing bibliographic metadata.

### `LICENSE`
Repository license file.

This file defines the current baseline reuse status of the repository. At the present stage, it serves as a practical public-facing legal clarification.

## Main directories

### `docs/`
Documentation and outward-facing scientific framing.

This directory contains the main project texts that explain the conceptual basis, methodological status, repository logic, and public-facing interpretation of the work.

Typical contents include:

- project overview
- method status
- “what this is / is not” clarification
- repository map
- structured field description files
- licensing notes
- later formal documentation material

This is usually the most important directory after `README.md` for readers who want to understand the project seriously.

### `figures/`
Project figures and visual material.

This directory contains conceptual and methodological images used to support the outward-facing presentation of the project.

Typical contents may include:

- conceptual bridge figures
- gain profile visualizations
- mixed-sensitivity illustrations
- later scientific diagrams
- publication-support graphics

Readers should treat this directory as visually supportive, not as a substitute for the methodological texts.

### `notes/`
Working notes and intermediate scientific material.

This directory contains more local, evolving, or intermediate project notes. These may include interpretive sketches, methodological reminders, working summaries, or text blocks that are not yet part of the main outward-facing structure.

This material can be highly valuable, but it may also be more provisional than the curated files in `docs/`.

### `results/`
Result material and structured outputs.

This directory contains result-facing project material, such as summaries, structured exports, or later numerical output files.

Depending on the project stage, this directory may contain:

- status summaries
- result snapshots
- intermediate structured data
- run outputs
- later numerical artifacts

For a numerics-heavy project, this directory is especially important. It should ideally remain readable, well-grouped, and accompanied by field descriptions where needed.

### `links/`
Central outward-facing link structure.

This directory contains public project links and related navigation material. Its role is to reduce link drift and keep the outward-facing project presence synchronized.

Typical contents may include:

- public publication links
- repository links
- profile or ORCID links
- later DOI or Zenodo links
- formal release references

## Suggested reading path for new visitors

A good reading path for someone new to the repository is:

1. `README.md`
2. `docs/project-overview.md`
3. `docs/method-status.md`
4. `docs/what-this-is-and-is-not.md`
5. `docs/repository-map.md`
6. `links/public-links.md`
7. `figures/`
8. `notes/`
9. `results/`

This path moves from general orientation to claim discipline to supporting material.

## Suggested reading path for reviewers

A reviewer or scientifically critical reader may prefer this order:

1. `README.md`
2. `docs/method-status.md`
3. `docs/what-this-is-and-is-not.md`
4. `docs/project-overview.md`
5. `links/public-links.md`
6. `results/`
7. `notes/`
8. `figures/`

This path foregrounds evidence level, limitations, and interpretive discipline before conceptual expansion.

## Repository philosophy

The repository is intentionally structured to reflect the project’s scientific style.

That means:

- not everything is reduced to polished presentation
- not everything is left in raw notebook form
- the repository tries to preserve both scientific readability and working transparency

The goal is not maximal volume, but navigable structure.

## Maintenance principles

As the repository evolves, the following principles should remain in place:

- outward-facing core logic should stay in `README.md` and `docs/`
- public links should stay centralized in `links/`
- structured files should be accompanied by field-description `.md` files where helpful
- numerical or result-heavy content should remain readable and not become a blind dump
- repository growth should preserve the project red thread rather than fragment it

## Bottom line

The **Quantum–Spacetime Bridge** repository is not just a storage place for files. It is part of the scientific presentation of the project.

Its structure is meant to help readers see:

- what the project is trying to do
- what has already been established
- what remains limited
- where supporting material lives
- how to follow the work without losing the main line
