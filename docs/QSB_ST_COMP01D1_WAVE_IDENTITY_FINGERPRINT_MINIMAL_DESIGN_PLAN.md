# QSB-ST-COMP01-D1 Wave Identity Fingerprint Minimal Design Plan

## 1. Purpose

COMP01-D1 is a minimal design plan for diagnostic wave identity fingerprints without assuming a time anchor.

It does not implement a scanner. It does not validate a model. It does not make a physical claim.

The purpose is to define a small next-step design for distinguishing diagnostic waves or pattern objects before a time / tau / delay structure is meaningful.

## 2. Current status anchor

COMP01-C2 found two interesting candidates:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

COMP01-C3 did not confirm these candidates as stable under the real kernel / node-level `label_shuffle` smoke test.

Required status anchors:

```text
specificity_established = false
stable_candidate_metrics = none
```

The COMP01-D concept block is already documented and committed. This D1 file is only the minimal design plan for a later scanner.

## 3. Motivation after COMP01-D concept

The question shifts.

Not:

```text
When does correlation emerge?
```

But:

```text
How do we distinguish waves or diagnostic patterns before a time / tau / delay structure is meaningfully introduced?
```

The D1 design therefore starts from distinguishability, not from delay.

## 4. Minimal fingerprint families

D1 should only treat three minimal fingerprint families:

- spectral shift / `delta_k`
- phase drift / `phase_gradient_delta`
- local linear fingerprint / slope-intercept

Sidebands, envelope features, cross-channel leakage, complex component deltas, and related families can remain later extensions. They are not D1 required families.

## 5. Spectral shift / delta_k design

Possible later fields:

- `delta_k`
- `relative_k_shift`
- `k_ratio`
- `spectral_identity_distance`

Design intent:

- compare the diagnostic wave-number or spectral-position parameters of two waves,
- detect whether apparently similar waves carry small but stable spectral displacement,
- keep the metric small enough for duplicate and near-duplicate controls.

Boundary:

Spectral shift is used here as a diagnostic structure analogy. It is not cosmological redshift and not a physical redshift claim.

## 6. Phase drift / phase_gradient_delta design

Possible later fields:

- `relative_phase_drift`
- `phase_gradient_delta`
- `phase_curvature_delta`
- `phase_unwrap_warning`

Design intent:

- compare structure-internal phase movement between two diagnostic waves,
- separate constant phase offset from drift, gradient, or curvature behavior,
- preserve explicit warnings when phase unwrap or support choices affect the result.

Boundary:

Phase drift is a structure-internal pattern marker here. It is not physical time delay, not tau, and not proper time.

## 7. Local linear slope-intercept design

Use the real working form:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

Use the local tangent form at `x0 = 0`:

```text
y ≈ B_i k_i x + A_i
```

Interpretation:

- `A_i` as local offset / intercept
- `B_i k_i` as local slope / initial response

Possible later fields:

- `intercept_similarity`
- `slope_similarity`
- `delta_intercept_ij`
- `delta_slope_ij`
- `slope_intercept_balance`
- `local_linear_response_overlap`

Boundary:

This is a local diagnostic tangent form. It is not a global wave model and not a physical wavefunction derivation.

## 8. Same-wave and near-identical-wave controls

D1 must include these controls in any later implementation design:

- same-wave duplicate sanity check
- near-identical-wave decoy control
- `label_shuffle`
- kernel-level `label_shuffle`

The same-wave duplicate sanity check must verify that a fingerprint does not artificially distinguish two inputs that are actually the same diagnostic wave.

The near-identical-wave decoy control must test whether a fingerprint detects a real structural nuance or merely reacts to numerical noise.

## 9. Required null/control families

Minimum required controls:

- exact duplicate
- near duplicate with small `delta_k`
- near duplicate with small phase drift
- amplitude-preserved perturbation
- `label_shuffle`
- true kernel/node-level `label_shuffle`

Optional later extensions:

- phase_randomized control
- spectrum_matched control
- distribution_matched control
- noise perturbation

## 10. Proposed output files for a later implementation

These are proposals only. This plan creates none of them.

- `data/qsb_st_comp01d1_wave_identity_fingerprint_config.yaml`
- `scripts/run_qsb_st_comp01d1_wave_identity_fingerprint_minimal_scanner.py`
- `runs/QSB-ST-COMP01D1/wave_identity_fingerprint_minimal_open/summary.json`
- `runs/QSB-ST-COMP01D1/wave_identity_fingerprint_minimal_open/readout.md`
- `runs/QSB-ST-COMP01D1/wave_identity_fingerprint_minimal_open/fingerprint_pair_summary.csv`
- `runs/QSB-ST-COMP01D1/wave_identity_fingerprint_minimal_open/control_family_summary.csv`

## 11. Continuous field list

| Field name | Field type | Field description |
|---|---|---|
| `pair_id` | string | Stable pair identifier. |
| `reference_id_i` | string | First diagnostic wave / pattern identifier. |
| `reference_id_j` | string | Second diagnostic wave / pattern identifier. |
| `control_family` | string | Control or reference family. |
| `control_seed` | integer/null | Seed used for generated controls, if applicable. |
| `k_i` | float | Diagnostic wave-number estimate for item i. |
| `k_j` | float | Diagnostic wave-number estimate for item j. |
| `delta_k` | float | Absolute diagnostic wave-number difference. |
| `relative_k_shift` | float/null | Normalized diagnostic k difference with zero-division guard. |
| `k_ratio` | float/null | Ratio of diagnostic k values with guard. |
| `phase_i` | float/array | Phase or phase profile for item i. |
| `phase_j` | float/array | Phase or phase profile for item j. |
| `relative_phase_drift` | float | Relative phase drift over diagnostic support. |
| `phase_gradient_delta` | float | Difference of local phase gradients. |
| `phase_curvature_delta` | float | Difference of phase curvature. |
| `phase_unwrap_warning` | string | Explicit warning for unwrap/support ambiguity. |
| `intercept_i` | float | Local intercept A_i. |
| `intercept_j` | float | Local intercept A_j. |
| `delta_intercept_ij` | float | Difference between local intercepts. |
| `intercept_similarity` | float | Transparent normalized intercept similarity. |
| `slope_i` | float | Local slope B_i * k_i. |
| `slope_j` | float | Local slope B_j * k_j. |
| `delta_slope_ij` | float | Difference between local slopes. |
| `slope_similarity` | float | Transparent normalized slope similarity. |
| `slope_intercept_balance` | float | Joint diagnostic balance of slope and intercept differences. |
| `local_linear_response_overlap` | float | Similarity of local slope/intercept response. |
| `spectral_identity_distance` | float | Aggregate spectral distinguishability distance. |
| `aggregate_fingerprint_distance` | float | Combined diagnostic fingerprint distance. |
| `decision_status` | string | Conservative decision label. |
| `interpretation_note` | string | Short note separating result from interpretation. |

## 12. Minimal computation rules

Future computation rules should stay simple and explicit:

- `delta_k = abs(k_i - k_j)`
- `relative_k_shift` is a normalized difference with protection against division by zero
- `slope_i = B_i * k_i` for the real local working form
- `intercept_i = A_i`
- similarity values must use transparent normalization
- all warnings must be explicit fields, not silently ignored

No threshold should be tuned after seeing the result.

## 13. Decision logic

Allowed cautious decision labels:

- `duplicate_sanity_pass`
- `near_duplicate_decoy_detected`
- `structured_reference_exceeds_tested_controls`
- `control_mimicry_warning`
- `inconclusive`
- `failed_sanity_check`

No label may claim that specificity is established or use stronger language than the tested controls support.

## 14. Interpretation rules

Every future D1 result must separate:

- Befund
- Interpretation
- Hypothese
- Offene Lücke

This separation is required because a fingerprint can be numerically useful without being physically interpreted.

## 15. What this block must not do

This block:

- does not attach D(A,B)
- does not construct S_rel2
- does not introduce tau as physical time
- does not derive proper time
- does not derive a Lorentzian metric
- does not validate the physical Bridge
- does not claim physical wavefunctions
- does not establish diagnostic specificity
- does not explain cosmological redshift
- does not create matter particles

## 16. Claim Boundary

psi is a diagnostic pattern object here, not automatically a physical wavefunction.

wave identity fingerprints are diagnostic distinguishability observables, not physical observables by themselves.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

real_imag_proxy is a diagnostic component split, not a physical derivation.

The complex trigonometric notation is a planned formal representation, not yet an implemented physical wavefunction model.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1 does not attach D(A,B).

COMP01-D1 does not construct S_rel2.

COMP01-D1 does not derive a Lorentzian metric.

COMP01-D1 does not validate a physical Bridge.

COMP01-D1 does not establish diagnostic specificity yet.

This is synthetic diagnostic concept/design work only.

## 17. Current status label

```text
current_status_label: COMP01D1_wave_identity_fingerprint_minimal_design_plan_created
```
