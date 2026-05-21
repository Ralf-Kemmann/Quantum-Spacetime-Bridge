# QSB-ST COMP01 Wave Identity Fingerprint Parameter Space — Minimal Metric Specification

## 1. Purpose

This is a minimal metric specification for the new Wave Identity Fingerprint Parameter Space route.

It creates no runner, no config, no data file, no run output, and no implementation. It creates no D1q and does not continue D1-letter expansion.

This document specifies a diagnostic metric only. It creates no validation of a physical model and no diagnostic specificity.

## 2. Starting point from seed note

The D1m-D1p gate closed the previous technical hygiene chain. No further D1-letter extension unless externally required.

The seed note separated the diagnostic measurement space from the still-open identity carrier space:

Der Fingerprint-Raum ist der Messraum; der Identitäts-Raum muss nicht derselbe Raum sein.

The Fingerprint-Raum is the measurement/projection space. The Identitäts-Raum remains open. The new route prefers relational wave-pair fingerprints `R_ij` as points in fingerprint space.

## 3. Object of the metric

The metric compares two relational wave-pair fingerprints, for example `R_ij` and `R_kl`.

Working object:

```text
R_ij = (delta_k_ij, delta_phase_ij mod 2π, slope_diff_ij, intercept_diff_ij, amplitude_diff_ij, ...)
```

This is a diagnostic object, not a physical state vector. The metric is defined only in Fingerprint-Raum.

## 4. Coordinate classes

| coordinate | type | compact? | example domain | interpretation boundary |
| --- | --- | --- | --- | --- |
| `delta_k_ij` | spectral/wavenumber difference | no | `R` or controlled interval | diagnostic only |
| `delta_phase_ij` | relative phase difference | yes | `S¹` | periodic diagnostic coordinate |
| `slope_diff_ij` | local response difference | no | `R` | tangent/local diagnostic only |
| `intercept_diff_ij` | local offset difference | no | `R` | local diagnostic only |
| `amplitude_diff_ij` | amplitude difference | no | `R` or controlled interval | diagnostic only |
| `overlap_residual_ij` | optional future compatibility residual | no or bounded interval | `[0,1]` or `R` | future optional, not first metric unless defined |

The coordinate list is deliberately small. It follows earlier COMP01-D fingerprint and residual notes that treated spectral shifts, phase structure, local slope/intercept features, and overlap-like values as diagnostic observables.

## 5. Compact-coordinate handling

Phase-like variables must be handled modulo `2π`.

Naive linear distance fails near the wrap boundary. Values near `0` and values near `2π` can be close as phase coordinates even if their raw numeric difference is large.

Circular distance:

```text
d_phase(phi1, phi2) = min(|Δphi|, 2π - |Δphi|)
```

Here `Δphi` should be reduced to `[0, 2π)` or handled equivalently modulo `2π`.

Equivalent embedding option:

```text
phi -> (cos phi, sin phi)
```

For multiple compact coordinates, the compact part becomes `T^m`, and the mixed diagnostic topology can be written as `R^n × T^m`. This is diagnostic topology, not a physical compact dimension claim.

## 6. Non-compact-coordinate handling

Non-compact coordinates use ordinary differences after normalization.

`k`, slope, intercept, and amplitude are not assumed periodic. Scale choice matters: without normalization, one coordinate may dominate merely by units.

The initial route should use explicit toy scales rather than inferred physical scales. This keeps assumptions visible and prevents hidden data-driven tuning.

## 7. Minimal diagnostic metric

Minimal diagnostic metric for comparing `R_ij` and `R_kl`:

```text
d²(R_ij, R_kl) =
  w_k   * ΔK²
+ w_phi * d_phase(delta_phase_ij, delta_phase_kl)²
+ w_s   * ΔS²
+ w_b   * ΔB²
+ w_a   * ΔA²
```

where:

```text
ΔK = normalized(delta_k_ij - delta_k_kl)
ΔS = normalized(slope_diff_ij - slope_diff_kl)
ΔB = normalized(intercept_diff_ij - intercept_diff_kl)
ΔA = normalized(amplitude_diff_ij - amplitude_diff_kl)
```

Then `d = sqrt(d²)` may be used as diagnostic fingerprint distance.

All weights are diagnostic weights, not physical constants. The metric is not spacetime geometry, not Hilbert-space geometry, and not a physical manifold metric.

## 8. Normalization and weights

Recommended first specification:

- use explicit toy scales in a later YAML/config, not hidden inference
- use default equal weights only as a baseline
- allow an optional sensitivity sweep later
- report all normalization scales in output
- do not tune weights automatically to make results look good

Possible future config fields, conceptually only:

```yaml
coordinate_scales:
  delta_k: explicit_toy_scale
  slope_diff: explicit_toy_scale
  intercept_diff: explicit_toy_scale
  amplitude_diff: explicit_toy_scale
weights:
  delta_k: 1.0
  delta_phase: 1.0
  slope_diff: 1.0
  intercept_diff: 1.0
  amplitude_diff: 1.0
```

These fields are not created in this task.

## 9. Minimal synthetic test cases

| case_id | purpose | construction idea | expected diagnostic behavior | claim boundary |
| --- | --- | --- | --- | --- |
| `same_relational_identity` | sanity check for equivalent fingerprints | two fingerprints identical or equivalent under phase wrap | metric distance near 0 | diagnostic sanity only |
| `phase_wrap_equivalent` | test compact-coordinate handling | `delta_phase` values near `0` and near `2π` | naive Euclidean phase distance looks large; circular metric should be small | phase wrap behavior only |
| `same_looking_not_same_delta_k` | test non-compact separation | similar phase but different `delta_k` | circular metric should not collapse them to same identity | diagnostic contrast only |
| `same_looking_not_same_slope_intercept` | test local shape separation | similar phase/k but different local slope/intercept fingerprint | metric should separate through non-compact terms | local diagnostic contrast only |
| `mixed_ambiguity_case` | test non-overconfident behavior | moderate differences across compact and non-compact channels | should remain diagnostic/ambiguous, not forced into clean same/different label | ambiguity is allowed |

## 10. Expected diagnostic behavior

The circular/torus-aware metric should treat phase wrap equivalence as near, not far.

Non-compact differences should still separate fingerprints that only look same in phase. The metric should expose ambiguous mixed cases rather than force overconfident labels.

A baseline comparison should include naive Euclidean phase treatment. The expected output is diagnostic contrast, not validation of a physical model.

## 11. Non-goals

- no physical phase reconstruction
- no physical compact dimensions
- no spacetime metric
- no Lorentzian metric
- no Hilbert-space norm
- no proof of wave identity
- no diagnostic specificity
- no Bridge confirmation
- no D1q
- no implementation now

## 12. Befund expected from this specification

This specification is expected to define the object `R_ij`, compact/non-compact coordinate handling, a minimal diagnostic metric, normalization and weights policy, and minimal synthetic cases.

It prepares a later implementation without hidden assumptions. It does not produce numerical results.

## 13. Interpretation

This spec prepares a test of whether circular/torus-aware metrics raise the diagnostic treatment quality of periodic fingerprint coordinates.

It clarifies why naive Euclidean fingerprints may fail near phase wrap boundaries and remains inside diagnostic fingerprint space.

It does not say the metric is physical geometry, does not say compact dimensions were found, does not say wave identity is relational as a settled result, does not claim Hilbert-space reconstruction, and does not claim Bridge confirmation.

## 14. Hypothese

A mixed compact/non-compact relational fingerprint metric may distinguish wave-identity residuals more naturally than a naive flat Euclidean metric, especially near phase wrap boundaries and same-looking/not-same cases.

This remains a hypothesis only.

## 15. Offene Lücke

- no implementation
- no runner
- no numerical results yet
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
- metric weights remain diagnostic choices
- normalization scales remain to be specified before implementation

## 16. Claim Boundary

- metric specification only
- no new scores calculated
- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- no physical compact dimensions
- no string compactification claim
- no Hilbert-space reconstruction
- no conversion of fingerprint metric into spacetime metric
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- Mastermind, Knuth, manifold, and role-permutation remain parked

## 17. Next-step recommendation

Recommended next step:

`QSB-ST COMP01 Wave Identity Fingerprint Parameter Space — Minimal Metric Runner Specification`

Purpose:

- specify input toy cases
- specify output schemas
- specify naive-vs-circular metric comparison
- specify acceptance checks
- keep physical claims out of scope

Implementation should come only after runner specification.

## 18. Files created / checked

Created by this task:

- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md`

Checked seed/gate/context files:

- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`
- `docs/QSB_ST_COMP01_D1M_D1P_CONSOLIDATION_AND_NEXT_STEP_GATE_NOTE.md`
- `docs/QSB_ST_COMP01D1P_D1O_REFINED_OUTPUT_AUDIT_REGRESSION_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1O_D1M_REFINED_MULTI_CHANNEL_PROFILE_RESULT_NOTE.md`

Checked earlier COMP01-D wave-identity context files:

- `docs/QSB_ST_COMP01D_WAVE_IDENTITY_FINGERPRINT_OBSERVABLES_CONCEPT.md`
- `docs/QSB_ST_COMP01D1A_WAVE_IDENTITY_RESIDUAL_SCANNER_SPEC.md`
- `docs/QSB_ST_COMP01D1B_WAVE_IDENTITY_RESIDUAL_MINIMAL_SCANNER_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1C_WAVE_IDENTITY_RESIDUAL_CONTROL_STRESS_RESULT_NOTE.md`
