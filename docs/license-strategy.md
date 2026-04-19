# Licensing Strategy

## Purpose of this note

This note documents the current licensing strategy for the **Quantum–Spacetime Bridge** repository.

The goal is to provide a professional and reviewer-friendly baseline that is compatible with a public research repository at an intermediate methodological stage.

## Why a license is useful here

A public repository should make the legal reuse status of its contents explicit. This helps readers, reviewers, and later publishers understand what may be reused and under which conditions.

For a journal-facing workflow, an explicit repository license is often preferable to leaving the reuse status undefined.

## Current recommendation

### 1. Repository root license

The repository root file `LICENSE` is set to the **MIT License**.

This is a pragmatic choice for the code side of the repository because it is:

- widely recognized
- short and easy to inspect
- permissive
- compatible with an open scientific workflow
- low-friction for reviewers and users

### 2. Documentation and figure note

The repository contains not only code-like material, but also scientific texts, notes, and figures. For this reason, maintainers may later decide to separate:

- code reuse
- text reuse
- figure reuse

At the current stage, the root `LICENSE` provides a clear baseline for the repository as a public project. If later needed, a more differentiated structure can be introduced, for example:

- `LICENSE` for code
- `LICENSE-docs.md` or `docs/license-notice.md` for text and figures
- explicit reuse notes inside `figures/` for individual image assets

## Why MIT is a reasonable starting point

MIT is a good default when the immediate goal is clarity and openness without legal complexity. It does not force copyleft propagation and is easy for readers, collaborators, and services such as GitHub to recognize.

For a theory-facing repository, this is often a practical first step when the main need is:

- visible openness
- explicit reuse permission
- no ambiguity about repository status

## Important project distinction

A repository license is **not** the same thing as the copyright and publication terms of a journal article.

That distinction matters:

- the repository license governs reuse of repository material
- article publication terms are governed separately by the publisher and publication agreement
- if material is later submitted or republished elsewhere, that specific publication context must still be checked

## Possible later refinement

If the project grows and the distinction between code, documentation, and figures becomes more important, the repository can later be refined into a mixed licensing model.

A common future refinement would be:

- **MIT** for code
- **CC BY 4.0** for documentation and explanatory text
- explicit figure-by-figure notices where needed

This is optional and can be introduced later if the project needs finer-grained control.

## Bottom line

For the current repository stage, the chosen baseline is:

- root repository license: **MIT**
- future option: split code and documentation/figure licensing if needed

This provides a clear and professional starting point without overstating the legal architecture of the project.
