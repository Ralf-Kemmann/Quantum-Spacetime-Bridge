# Research Infrastructure and the QSB Hypercube

## Purpose

The QSB data architecture is not an administrative side project. It is a research instrument.

Exploratory computational physics creates more than final plots. It creates source objects, model configurations, numerical states, controls, rejected candidates, validation outcomes, repair requirements, alternative interpretations, and claim decisions. If these are stored only in separate files and scripts, the relations between them are easily lost.

QSB therefore represents the known research space as a metadata-governed, n-dimensional analytical structure.

## From source to claim

The operational chain is:

> raw source → import → normalisation → SI and dimension handling → mapping → validation → canonical object → Data Mart → analytical view → result → interpretation → claim decision

Lineage is preserved across this chain.

## Computational co-presence

The central idea is not that a computer literally “knows” every value at one instant. The useful property is **joint analytical addressability**.

Spectral values, simulation states, source provenance, quality assessments, controls, repair states, and claim boundaries can remain logically available within one governed research space. A new question therefore need not begin by rebuilding a private collection of files and one-off joins.

The computer handles scale, repetition, and combinatorics. The researcher decides which relations are physically meaningful.

## N-dimensional hypercube

A research cell may be addressed through dimensions such as:

- project strand;
- run family and run;
- model configuration;
- graph seed;
- time and spectral coordinate;
- source object and source family;
- mechanism class;
- control class;
- metadata quality;
- unit quality;
- dimensional quality;
- repair requirement and repair state;
- admissibility status;
- claim status;
- publication or review state.

The exact dimensions depend on the Data Mart and the grain of the observation.

## Data Marts and metadata-governed links

Domain-specific Data Marts keep the physical and analytical grains explicit. They may include simulation, spectral, literature, admissibility, control, quality, claim, and publication views.

The metadata layer records:

- object identity;
- source and version;
- field meaning;
- aliases and vocabulary;
- grain;
- allowed joins;
- units and dimensions;
- validation rules;
- quality semantics;
- lineage;
- deprecation and repair states.

Data Marts can be connected through shared or explicitly mapped dimensions. A technically possible join is not automatically a scientifically valid join.

## OLAP analytics

The research space supports familiar multidimensional operations with scientific restrictions:

- **Slice** — fix one dimension or state;
- **Dice** — select a constrained multidimensional subspace;
- **Pivot** — change the analytical orientation;
- **Roll-up** — aggregate along a valid hierarchy;
- **Drill-down** — descend to a finer grain;
- **Drill-through** — return from an aggregate to source rows and lineage;
- **Drill-across** — compare or connect compatible Data Marts;
- **scenario analysis** — test alternative mappings or thresholds without overwriting historical facts;
- **calculated measures** — derive quality, control, repair, or effect measures under explicit contracts.

## Scientific aggregation rules

Commercial cubes often assume that measures can be summed along convenient hierarchies. Research data require stricter rules.

Examples:

- row count and distinct-candidate count are not interchangeable;
- distinct counts are not generally additive;
- effect sizes must not be summed;
- averages require denominators and weighting rules;
- `not_evaluated`, `not_applicable`, `missing`, and a negative result are different states;
- a roll-up must not destroy source lineage;
- claim status is not an ordinary numerical scale;
- a measure valid at one grain may be meaningless at another.

These contracts are part of the scientific model of the cube.

## Spectral data

Spectral data were an early and important use case because a displayed spectrum is only one projection of a larger state:

\[
S = S(\omega, t, \mathrm{seed}, \mathrm{run}, \mathrm{state}, \mathrm{control}, \mathrm{model}, \mathrm{quality}, \ldots)
\]

The hypercube retains the context behind each spectral value instead of reducing the dataset to a final curve.

## Negative and residual research space

The cube includes more than successful results:

- rejected mappings;
- neutral controls;
- null results;
- blocked claims;
- lineage gaps;
- metadata repairs;
- unresolved residuals.

This makes it possible to ask whether an apparently homogeneous rejection cohort contains recurring subgroups that are not explained by the documented technical reason.

## Accessibility and inclusion

The infrastructure externalises part of the memory, orientation, and consistency burden of complex research. It does not lower scientific standards. It makes those standards less dependent on exceptional working memory, uninterrupted concentration, or a large institutional team.

Natural-language AI assistance can provide an interface to this structure, but it does not replace physical judgement or claim responsibility.

## Publication status

The QSB hypercube and metadata system are active project infrastructure. A dedicated methods paper is planned.

A priority claim such as “the first OLAP hypercube in physics” is not made here. Novelty must be assessed through a dedicated literature review. The present defensible claim is narrower:

> QSB investigates formal multidimensional analytics as a provenance-, grain-, quality-, repair-, control-, and claim-aware analysis layer for exploratory computational physics.
