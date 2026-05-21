# QSB-ST COMP01 Next-Route Seed: Wave Identity / Identity Fingerprint Parameter Space

## 1. Purpose

This is a seed/concept note for the next route after the D1m-D1p technical hygiene chain.

It creates no runner, no config, no run output, and no implementation. It does not create D1q, does not continue D1-letter expansion, and does not create validation of a physical model or diagnostic specificity.

The note captures a parameter-space question for wave identity fingerprints before any numerical runner is specified.

## 2. Starting point after D1m-D1p gate

D1m-D1p is closed. No further D1-letter extension unless externally required.

D1m-D1p produced an auditable, regression-checked diagnostic metadata workflow. The line made warning origins, warning granularities, dominance semantics, and regression stability more visible.

It did not create physical phase, physical spacetime, or diagnostic specificity. The next route should therefore be opened outside the D1m-D1p hygiene chain.

## 3. Core seed idea

Wave identity may require distinguishing where we measure fingerprints from where identity is structurally carried.

Der Fingerprint-Raum ist der Messraum; der Identitäts-Raum muss nicht derselbe Raum sein.

In this seed, a fingerprint is a diagnostic projection. It may contain measurable coordinates such as phase difference, slope difference, intercept difference, spectral difference, or overlap-like values. The underlying identity carrier remains open.

## 4. Fingerprint-Raum versus Identitäts-Raum

Fingerprint-Raum:

- diagnostic/projection/measurement space
- contains coordinates such as `delta_k`, `delta_phase`, `phase_gradient`, `slope`, `intercept`, and overlap-like values
- may have mixed compact and non-compact directions
- may be `R^n × T^m`-like as a diagnostic topology

Identitäts-Raum:

- underlying structural space of wave identity
- not yet specified
- may be parameter-based, function-based, or relational
- should not be equated with fingerprint space prematurely

The fingerprint space can be cylinder-like or torus-like as a measurement construction without saying that the identity space itself is literally a cylinder or torus.

## 5. Candidate spaces

| Option | Point represents | Strength | Risk | Near-term status |
| --- | --- | --- | --- | --- |
| Parameterraum | one wave represented by parameters such as `k`, amplitude, phase, slope, or intercept | simple and numerically convenient | may be too absolute/object-like | useful but not preferred as ontology |
| Funktionenraum | one wave function `psi` in a function space | mathematically powerful | too heavy for immediate diagnostic route | parked as later formal context |
| Relationalraum | a relation `R_ij` between two waves | fits same-looking wave versus same wave | requires careful metric and controls | strongest near-term candidate |

These options are diagnostic scaffolds, not physical claims.

## 6. Parameterraum option

In the Parameterraum option, a wave is represented by parameters such as `k`, `A`, `B`, or by `k`, amplitude, and phase.

The phase coordinate is compact and naturally modeled as `S¹`. Non-periodic parameters such as `k`, amplitude, slope, intercept, or `delta_k` live on non-compact or interval-like directions.

Minimal local shapes can look like `R² × S¹`, or more generally `R^n × T^m`. When one non-compact and one compact direction are used, the diagnostic projection is cylinder-like: `R × S¹`.

This option is useful for simple numerical work, but it may be too absolute/object-like for the question of relational wave identity.

## 7. Funktionenraum option

In the Funktionenraum option, wave identity is treated through the function itself, for example `psi` in an `L²` / Hilbert-style setting.

In principle, identity distance could be discussed through norms or inner products. This is mathematically powerful, but too heavy for the immediate diagnostic seed.

It raises normalization, boundary condition, basis dependence, equivalence class, global phase, and operator questions. This should remain parked as possible later formal context, not the first implementation route.

This seed does not claim a Hilbert-space reconstruction.

## 8. Relationalraum option

In the Relationalraum option, identity is treated as a relation rather than an isolated object.

A point in fingerprint space may represent the relation `R_ij` of a wave pair instead of one wave:

```text
R_ij = (delta_k_ij, delta_phase_ij mod 2π, slope_diff_ij, intercept_diff_ij, overlap_ij, ...)
```

This fits the project intuition of same-looking wave versus same wave. It also fits the no-time-anchor intuition, because the relation can be structure-internal rather than time-indexed.

For the next route, this is the strongest near-term candidate.

## 9. Cylinder, torus, and compact fingerprint directions

`R × S¹` is a minimal cylinder-like diagnostic projection when exactly one compact periodic fingerprint coordinate is relevant.

If multiple independent periodic coordinates matter, the compact part becomes torus-like:

```text
T^m = S¹ × ... × S¹
```

The general diagnostic topology can be written as:

```text
R^n × T^m
```

Compact directions arise from periodic parameters such as phase or angles. This is a diagnostic parameter-space topology, not a claim about physical compact dimensions and not a string compactification claim.

## 10. Metric question

Topology or coordinate structure is not enough. A diagnostic space still needs a metric or compatibility rule to define closeness.

Periodic coordinates must not be compared with naive linear distance. For phase, use circular distance:

```text
d_phase(phi1, phi2) = min(|Δphi|, 2π - |Δphi|)
```

Another option is the embedding:

```text
phi -> (cos phi, sin phi)
```

A possible diagnostic compatibility metric is a weighted product of non-compact differences and circular distances. This metric belongs to fingerprint space only. It is not spacetime geometry.

## 11. Preferred working decision for the next route

For the next route, use:

- point in fingerprint space = relational wave-pair fingerprint R_ij
- identity space = open
- working hypothesis = wave identity is relational, and fingerprint space is a diagnostic projection of relational identity differences

This keeps the implementation target narrow while leaving the Identitäts-Raum deliberately unresolved.

## 12. Minimal test idea, not yet implementation

A later minimal test could build a tiny synthetic set of wave pairs, compute mixed compact/non-compact fingerprints, and compare naive Euclidean phase treatment against circular/torus-aware metric treatment.

The conceptual test question would be whether circular/torus-aware diagnostic metrics separate same-looking but not same wave pairs from same relational identity cases more cleanly than a naive flat Euclidean parameter vector.

No implementation is created here.

## 13. Befund

D1m-D1p closed the old technical hygiene line.

This note defines a new conceptual route. It distinguishes measurement space from identity space and prioritizes relational fingerprint space over absolute parameter identity for the next minimal route.

The Befund is conceptual only: the next route should start from relational wave-pair fingerprints, not from more D1-letter hygiene blocks.

## 14. Interpretation

The seed clarifies the conceptual target for future tests. It explains why naive Euclidean fingerprint vectors may be insufficient when phase-like coordinates are periodic.

The seed motivates circular/torus-aware diagnostic metrics for fingerprint space.

It does not claim compact physical dimensions, does not claim that wave identity is already relational, does not claim a Hilbert-space reconstruction, does not claim emergent spacetime geometry, and does not claim Bridge confirmation.

## 15. Hypothese

A relational wave-pair fingerprint space with mixed compact and non-compact diagnostic coordinates may distinguish wave identity residuals more naturally than a naive flat Euclidean parameter vector.

This is a hypothesis only.

## 16. Offene Lücke

- no implementation
- no runner
- no numerical test yet
- no real data
- no validation of a physical model
- no diagnostic specificity
- no physical compact dimensions
- no physical phase reconstruction
- no physical wavefunction
- no Hilbert-space reconstruction
- no Lorentzian metric
- no physical spacetime geometry
- no Pauli/spin-statistics claim
- no Bridge confirmation
- identity space remains open
- metric choice remains open
- point definition remains a working decision, not final ontology

## 17. Claim Boundary

- seed/concept note only
- no new scores calculated
- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- no physical compact dimensions
- no string compactification claim
- no Hilbert-space reconstruction
- no conversion of diagnostic fingerprint topology into physical spacetime topology
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- Mastermind, Knuth, manifold, and role-permutation remain parked

## 18. Next-step recommendation

Recommended next step:

`QSB-ST COMP01 Wave Identity Fingerprint Parameter Space — Minimal Metric Specification`

Purpose:

- define candidate fingerprint coordinates
- define compact/non-compact coordinate treatment
- define circular phase distance
- define a weighted diagnostic metric
- define tiny synthetic test cases
- no implementation until this is specified

## 19. Files created / checked

Created by this task:

- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`

Checked D1m-D1p gate and context files:

- `docs/QSB_ST_COMP01_D1M_D1P_CONSOLIDATION_AND_NEXT_STEP_GATE_NOTE.md`
- `docs/QSB_ST_COMP01D1P_D1O_REFINED_OUTPUT_AUDIT_REGRESSION_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1O_D1M_REFINED_MULTI_CHANNEL_PROFILE_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RESULT_NOTE.md`

Checked earlier COMP01-D wave-identity context files:

- `docs/QSB_ST_COMP01D_WAVE_IDENTITY_FINGERPRINT_OBSERVABLES_CONCEPT.md`
- `docs/QSB_ST_COMP01D1A_WAVE_IDENTITY_RESIDUAL_SCANNER_SPEC.md`
- `docs/QSB_ST_COMP01D1B_WAVE_IDENTITY_RESIDUAL_MINIMAL_SCANNER_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1C_WAVE_IDENTITY_RESIDUAL_CONTROL_STRESS_RESULT_NOTE.md`
