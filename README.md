<p align="center">
  <img src="figures/figure_conceptual_bridge.png" width="560" alt="Conceptual illustration of a coupled matter–geometry research idea">
</p>

<p align="center"><em>Conceptual illustration. It is not a numerical model output and not evidence for a physical spacetime mechanism.</em></p>

# Quantum–Spacetime Bridge (QSB)

**Quantum–Spacetime Bridge** is an independent research programme in exploratory computational physics. It investigates whether carefully defined relational and graph-based models can expose mathematically readable links between matter-wave structure and effective geometric degrees of freedom.

The project is deliberately ambitious in its questions and conservative in its claims. QSB does **not** currently present a validated theory of quantum gravity, physical spacetime emergence, or an experimentally established mechanism. Its purpose is to build models that can be derived, tested, controlled, reproduced, and rejected without losing the path from source data to scientific statement.

> **The repository is both a research archive and an active research instrument.**

## Current publication focus

The present publication track studies a finite, dimensionless graph model with coupled Schrödinger and edge-field dynamics.

Within the implemented model, the work has established:

- a closed analytic edge response with a unique stable model solution;
- cross-seed replication over 32 independent graph realisations;
- a trivial free uniform branch and a non-trivial constrained preparation branch;
- bounded, reversible model dynamics under refined numerical integration;
- small, directionally consistent geometry-to-matter effects relative to frozen-edge controls.

These are **model-internal mathematical and numerical findings**. They do not establish physical gravitation, physical spacetime dynamics, Lorentz covariance, or an experimentally validated de Broglie mechanism.

[Read the current status](docs/public/CURRENT_STATUS.md) ·
[Read the claim boundaries](docs/public/CLAIM_BOUNDARIES.md)

## The research instrument

QSB is not organised as a collection of isolated scripts and result files. Its computational work is supported by a provenance-controlled research data architecture:

- PostgreSQL research data warehouse;
- source, version, lineage, unit, dimension, validation, repair, control, and claim metadata;
- domain-specific Data Marts;
- an n-dimensional research hypercube;
- spectral data and simulation results held in jointly addressable analytical views;
- metadata-governed links across Data Marts;
- Slice, Dice, Pivot, Roll-up, Drill-down, Drill-through, and Drill-across analysis;
- preservation of positive, neutral, rejected, unresolved, and repair-required results.

The cube is not a decorative dashboard. It is a way of representing the known research space so that the computer can keep many values and relationships analytically co-present while the human researcher remains responsible for physical meaning and judgement.

[Research infrastructure and hypercube](docs/public/RESEARCH_INFRASTRUCTURE.md)

## How to enter the repository

A large part of this repository is a scientific audit trail. New readers should not begin by opening arbitrary historical run folders.

| Entry point | Purpose |
|---|---|
| [Current status](docs/public/CURRENT_STATUS.md) | What is active, what is established, and what remains open |
| [Repository guide](docs/public/REPOSITORY_GUIDE.md) | Directory map and recommended reading order |
| [Claim boundaries](docs/public/CLAIM_BOUNDARIES.md) | What the present evidence does and does not support |
| [Research infrastructure](docs/public/RESEARCH_INFRASTRUCTURE.md) | DWH, metadata control, Data Marts, and hypercube |
| [Human–AI method note](docs/public/HUMAN_AI_METHOD_NOTE.md) | Transparent division of responsibility |
| [Publication roadmap](docs/public/PUBLICATION_ROADMAP.md) | GitHub, journal, Academia, ESA OSIP, and methods-paper routes |
| [Deutsche Übersicht](docs/public/PROJECT_OVERVIEW_DE.md) | Kurzer Einstieg auf Deutsch |

## Scientific working rules

The repository keeps a strict distinction between:

1. **finding** — what was measured, derived, or observed;
2. **interpretation** — the bounded reading supported by the finding;
3. **hypothesis** — a possible explanation requiring further tests;
4. **open gap** — what is missing or unresolved;
5. **claim boundary** — what must not be inferred from the present evidence.

Negative and neutral outcomes are retained. A rejected candidate is not deleted merely because it failed. A historical preregistration decision is not rewritten after a later numerical clarification. A model result is not translated into a physical claim without an explicit bridge.

## Repository structure

The main technical areas are:

- `docs/` — specifications, result notes, status documents, and public orientation;
- `data/` — controlled inputs, manifests, tables, and metadata;
- `scripts/` — executable research and validation scripts;
- `runs/` — tracked run-specific audit material where applicable;
- `numerics/` — model-specific numerical work;
- `validation/` and `tests/` — formal checks and test cases;
- `results/` — selected compact public-facing result summaries;
- `figures/` — scientific figures and clearly labelled conceptual illustrations;
- `artifacts/` — packaged research artifacts and hand-off material.

Generated local exports are not part of the normal Git working tree.

## Publication routes

The same scientific core is being prepared for different audiences without changing the evidence:

- **formal physics journal** — compact LaTeX-style technical paper;
- **Academia** — a more readable and visually paced research presentation;
- **ESA Open Space Innovation Platform (OSIP)** — a technically elegant concept and development route;
- **computational-physics / research-data methods paper** — the metadata-governed hypercube as a research instrument.

The public repository is prepared first so that every later publication can point back to a transparent and versioned source.

## Human–AI collaboration

The project uses AI systems for structured assistance in documentation, coding, data handling, consistency checks, and editorial work. Scientific questions, physical interpretation, acceptance of results, claim release, and publication responsibility remain human decisions.

The aim is not to hide the collaboration behind polished prose. The aim is to make the work traceable enough that readers can distinguish human judgement from machine-supported formal processing.

[Human–AI method note](docs/public/HUMAN_AI_METHOD_NOTE.md)

## Citation, identity, and licence

- Author: **Ralf Kemmann**, Independent Researcher
- ORCID: [0009-0008-9932-3745](https://orcid.org/0009-0008-9932-3745)
- Citation metadata: [`CITATION.cff`](CITATION.cff)
- Public links: [`links/public-links.md`](links/public-links.md)
- Repository licence: [MIT](LICENSE)

Formal publication references and DOI records will be added when the corresponding releases exist.
