# QSB-CORRCORE01 Correlation Matrix Core DWH Integration Specification

## Purpose

QSB-CORRCORE01 registers older QSB correlation-core material as structured DWH and metadata-catalog content before later cross-strand synthesis.

The central object is the correlation matrix

```text
K_ij(tau) = <psi_i(tau) | psi_j(tau)>
```

It recurs in older notes on one-dimensional string-mode correlations, effective distance candidates, relational tunneling and operational time-scale projections, diagnostic fingerprint spaces, IDSPACE/CPNS ambiguity safeguards, and emergent-gravitation vocabulary alignment.

This block does not validate physical spacetime emergence, physical causality, emergent time, quantum gravity, Bridge confirmation, laboratory validation, diagnostic specificity, identity resolution, real degeneracy measurement, or universal correctness of the correlation metric. Its task is metadata catch-up.

## Source Set

The required source documents are treated as provenance sources:

- `Emergent_Spacetime_from_Correlated_One_D.pdf`
- `Relational_Correlation_Dynamics_A_Wave_B.pdf`
- `From_Diagnostic_Fingerprints_to_Identity.pdf`
- `Discussion_Paper_Emergent_Gravitation_fr.pdf`

If a source is not present inside the repository, the inventory records that fact and may record a local external path. The runner does not copy source PDFs into the repository.

## Why Kij Is A First-Class DWH Object

`K_ij(tau)` is not just a formula string. It is the join point between several older strands:

- string-mode overlap/correlation objects,
- magnitude and phase derived quantities,
- an effective-distance candidate `d_ij = -ell_0 log(|K_ij|)`,
- formal dynamics through `S[K]`, `V[K]`, and an equation of motion,
- relational tunneling/time-scale projections,
- fingerprint and identity-space method gates.

Making `K_ij` first-class allows later searches to retrieve its symbols, dependent quantities, equations, source roles, unit decisions, and claim boundaries without re-deriving them from narrative text.

## Effective Distance And Geometry Boundary

The older string-mode line defines

```text
d_ij = -ell_0 * log(|K_ij|)
```

This can be registered as an effective-distance construction in the DWH. It must not be promoted to physical metric recovery or physical spacetime validation. The DWH record therefore separates:

- `correlation_matrix_Kij` as inner-product correlation amplitude,
- `correlation_magnitude_abs_Kij` as dimensionless log argument,
- `effective_distance_dij` as a symbolic length-valued candidate when `ell_0` is length-valued,
- claim boundary `correlation_geometry_not_physical_spacetime_validation`.

## Unit And Dimension Discipline

The logarithm requires a dimensionless argument. CORRCORE01 therefore records `|K_ij|` as a dimensionless nonnegative scalar before it can appear in `log(|K_ij|)`.

`ell_0` carries length dimension and remains symbolic unless a numerical convention is supplied. `d_ij` carries length dimension with coherent SI calculation unit metre (`m`).

`tau` remains a model/internal evolution parameter. It is not mapped to seconds in this block.

`S[K]` remains a formal action functional with pending normalization. CORRCORE01 does not invent physical action units. `alpha` and `beta` are marked as constraint-derived and pending normalization unless a source provides sufficient conventions.

Operational dwell-time and Hartman-type projections are recorded as model-time projections when the source data does not provide physical units. No conversion to seconds is made.

## IDSPACE And CPNS Boundary

Fingerprint readability is not identity resolution. Fingerprints may be close, readable, or geometrically structured while identity remains unresolved.

CPNS/MaxEnt is a safeguard for ambiguity and degeneracy. Ambiguity is a protected valid state, represented by `ambiguous_unresolved`, not an implementation failure. CORRCORE01 imports the closed flags:

- no physical validation,
- no Bridge confirmation,
- no diagnostic specificity,
- no physical spacetime result,
- no quantum-gravity evidence,
- no real degeneracy measurement in CPNS06.

## Emergent-Gravitation Context Boundary

The emergent-gravitation discussion source is registered as conceptual comparison, vocabulary alignment, effective-action comparison, and falsifiability-language context. It is not evidence transfer from string theory to QSB.

## Connection To CAUSALITY07

CORRCORE01 connects to CAUSALITY07 only at the metadata and comparison layer. Later causal or directional calibration can be compared to correlation-core time/dependence concepts, but this block does not claim physical causality, global time, or validated dynamics.

## Metadata Server Catch-Up

The two runners create:

- a DWH seed with source, object, equation, quantity, claim-boundary, cross-strand, validation, summary, and readout outputs;
- an updated read-only-safe copy of the existing metadata catalog with CORRCORE01 represented as a first-class mart/work package/source set.

The metadata update inserts German and English aliases as metadata records where useful. It does not modify GUI/browser files.

## Claim Boundary

Valid CORRCORE01 statement:

```text
The older QSB correlation-core line has been registered as structured, traceable, queryable DWH metadata and seed records with explicit equations, quantities, unit/dimension decisions, provenance, and claim boundaries.
```

Invalid escalations:

- physical spacetime emergence has been validated,
- physical causality or emergent time has been established,
- quantum-gravity evidence exists,
- Bridge confirmation follows,
- diagnostic specificity or identity resolution follows,
- real degeneracy has been measured,
- string-theory context transfers evidential support to QSB.
