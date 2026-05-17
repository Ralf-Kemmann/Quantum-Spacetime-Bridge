# QSB-ST Resonance Matter Signature
## LIC-01 Pre-Spec Ingredients

Guiding principle:

"Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This note defines the minimum conceptual and diagnostic ingredients that must be fixed before a future QSB-ST-LIC-01 Relational Lorentz Interval Candidate Test can be specified. Its positive purpose is to make the next step small, testable, and claim-safe.

This is not the LIC-01 specification itself. It is not a result note and not a proof. It prepares the ground for a future test by separating distance, delay, scale, interval candidate, transformations, controls, and status labels before any implementation or run exists.

LIC-01 should test for invariant-like behavior of a relational interval candidate, not for a derived Lorentz transformation.

LIC-01 soll invariant-ähnliches Verhalten eines relationalen Intervallkandidaten prüfen, nicht eine bereits abgeleitete Lorentz-Transformation behaupten.

## 2. Why a pre-spec ingredients note is needed

LIC-01 should not start by claiming Lorentz transformations. It should ask whether a combined distance-delay diagnostic object behaves more stably than its components under controlled readout/frame-like transformations and null models.

Without this pre-spec step, the project risks mixing together graph distance, phase delay, fitted scale, Lorentz-like wording, and carrier language before the objects are ready. A pre-spec note keeps each ingredient visible and prevents a diagnostic readout from being treated as a spacetime interval.

## 3. Current status before LIC-01

Current status before LIC-01:

- Lorentz status is currently compatible / inspired / open under specified assumptions, not derived.
- The old Lorentz filter is a consistency filter, not a derivation.
- The old `interval_map` files are theta / parameter interval maps, not Lorentz intervals.
- `D(A,B)` remains a reconstructed distance readout unless Geometry Anchor conditions are met.
- `tau_rel` remains a relational-delay candidate, not physical time.
- `c_eff` is not automatically physical `c`.
- `S_rel^2` is a candidate diagnostic interval object, not a spacetime interval.

The current language should remain candidate, diagnostic, readout, under controls, not established, and not Lorentz-derived.

## 4. Ingredient 1: distance source D(A,B)

Possible distance sources:

1. Reconstructed graph/cost distance `D(A,B)`.
2. `d_ij = -l0 log |K_ij|`.
3. `D_rel` or derived readout score.

Recommendation for first LIC-01:

Use one explicitly declared reconstructed `D(A,B)` source from an existing geometry-readable pipeline, but keep it as diagnostic distance unless Geometry Anchor is passed.

Required metadata:

- `distance_source_id`
- construction method
- backbone / threshold / edge-count method
- `l0` handling if `d_ij` is used
- normalization
- Geometry Anchor status
- whether distance is graph/cost/readout-only or externally anchored

Distance language should stay diagnostic unless an external observable, declared scaling law, or Geometry Anchor condition supports stronger language.

## 5. Ingredient 2: relational delay tau_rel(A,B)

Possible `tau_rel(A,B)` sources:

1. Relational Delay readout.
2. phase-gradient-like readout.
3. pattern-shift between correlation states.
4. Hartman / Dwell-inspired phasengeometric delay proxy.

Recommendation for first LIC-01:

Use the least claim-heavy available `tau_rel` source: a predeclared relational-delay or phase-shift diagnostic if available. If no such source is available, LIC-01 should remain a design-only block until `tau_rel` is constructed.

`tau_rel` is not time. It is a delay-like diagnostic readout until operationally anchored.

Required metadata:

- `delay_source_id`
- construction method
- phase dependence
- directionality/asymmetry status
- no-signalling status
- whether delay is symmetric, directed, or unresolved
- normalization

## 6. Ingredient 3: effective scale c_eff

Possible `c_eff` statuses:

- fixed convention
- calibrated scale parameter
- fitted parameter
- sensitivity parameter
- derived candidate

Recommendation for first LIC-01:

`c_eff` should be handled as a declared sensitivity parameter or fixed convention, not as physical `c`.

If fitted, fitted `c_eff` must be reported as a fit and cannot be used as validation.

Required metadata:

- `c_eff_mode`
- `c_eff_value`
- `calibration_source`
- `fitted_or_predeclared`
- `sensitivity_range`
- `interpretation_status`

## 7. Ingredient 4: interval candidate S_rel^2

Candidate form:

```text
S_rel^2(A,B) = c_eff^2 * tau_rel(A,B)^2 - D(A,B)^2
```

`S_rel^2` is a candidate interval readout. It is not a spacetime interval.

Its first purpose is comparative stability: is `S_rel^2` more stable than `D(A,B)` or `tau_rel` alone under transformations and controls?

Sign interpretation must be disabled or kept diagnostic unless a causal/metric structure is explicitly defined. No "timelike/spacelike/lightlike" language should be used in the LIC-01 first pass unless a separate criterion is defined.

## 8. Ingredient 5: admissible readout/frame-like transformations

Admissible transformations are diagnostic transformations, not physical Lorentz transformations.

Candidate readout/frame-like transformations:

- backbone method variation
- threshold / theta variation
- edge-count or density-matched variation
- cost-function variation
- normalization variation
- phase gauge-like shifts that preserve phase differences
- phase-randomized controls
- spectrum-matched phase controls
- amplitude-only / phase-uniform controls
- label/family shuffles
- source/target role swaps where meaningful
- `c_eff` sensitivity variation

These are readout/frame-like transformations only. They do not yet represent inertial observer transformations.

## 9. Ingredient 6: null models and controls

Minimum null models and controls to predeclare:

- random phase
- trivial / uniform phase
- spectrum-matched phase
- amplitude-shuffled / phase-preserved
- amplitude-preserved / phase-randomized
- label/family shuffle
- topology-preserving or degree-preserving graph controls
- covariance-preserving controls where applicable
- `c_eff` random or permuted calibration controls
- theta/readout variation controls
- mimicry controls if a source dataset has known mimic risk

The null set should be chosen before any LIC-01 readout is interpreted. A candidate interval that is reproduced by nulls should receive a warning label, not a stronger claim.

## 10. Ingredient 7: output status labels

Cautious possible labels:

- `LIC01_design_ready`
- `LIC01_distance_ready_delay_missing`
- `LIC01_delay_ready_distance_unanchored`
- `LIC01_interval_candidate_defined`
- `LIC01_invariant_like_supported_under_controls`
- `LIC01_component_dominated`
- `LIC01_null_reproduced_warning`
- `LIC01_pipeline_artifact_warning`
- `LIC01_inconclusive`
- `LIC01_not_ready`

Even the strongest positive label must remain "under controls" and cannot be read as Lorentz derivation.

## 11. What LIC-01 may test

LIC-01 may test:

- whether `S_rel^2` can be computed from predeclared ingredients;
- whether `S_rel^2` is more stable than distance or delay components alone;
- whether stability survives readout/frame-like transformations;
- whether null models reproduce the same stability;
- whether `c_eff` sensitivity destroys or preserves the candidate;
- whether phase/amplitude controls affect the candidate as expected.

This is enough for a first diagnostic test. It is deliberately not enough for a physical Lorentz claim.

## 12. What LIC-01 may not claim

LIC-01 may not claim:

- Lorentz transformations shown;
- Lorentz covariance shown;
- spacetime interval shown;
- physical `c` recovered;
- light cone found;
- causality shown;
- physical metric shown;
- Bridge physically validated.

These statements remain outside LIC-01 unless a separate stronger criterion and result structure are created.

## 13. Minimum readiness checklist

- [ ] distance source selected
- [ ] Geometry Anchor status stated
- [ ] `tau_rel` source selected
- [ ] `tau_rel` directionality/asymmetry status stated
- [ ] `c_eff` handling selected
- [ ] `S_rel^2` formula frozen
- [ ] transformations predeclared
- [ ] null models predeclared
- [ ] output labels predeclared
- [ ] claim boundary frozen
- [ ] PADS-01 dependency stated where phase/amplitude separation is needed

## 14. Compact Claim Boundary

Claim Boundary:

This pre-spec note does not:

- implement LIC-01;
- define final `tau_rel`;
- validate `D(A,B)` as physical distance;
- validate `tau_rel` as physical time;
- validate `c_eff` as physical `c`;
- establish `S_rel^2`;
- derive Lorentz transformations;
- prove Lorentz covariance;
- establish a spacetime interval;
- validate the Bridge physically.

The current status is candidate, diagnostic, readout, under controls, not established, and not Lorentz-derived.

## 15. Recommended next steps

1. Choose the first `D(A,B)` source.
2. Identify or construct the first `tau_rel` source.
3. Decide `c_eff` handling for smoke design.
4. Freeze the first transformation/control set.
5. Draft QSB-ST-LIC-01 Spec.
6. Keep LIC-01 linked to PADS-01 and Geometry Anchor conditions.

For any old-run material later used near LIC-01, keep the practical discipline: Herkunft und Nachvollziehbarkeit klären, alte Runs sauber zuordnen, Fundstellen und Reproduzierbarkeit prüfen, alte Ergebnisdateien nachvollziehbar einordnen, and klären, welche alten Runs reproduzierbar sind.
