# QSB-ST-COMP01-B Real/Imag Proxy Definition Note

## 1. Purpose

This file clarifies the `real_imag_proxy` used in COMP01-B.

It is a methodological safety note before COMP01-C.

It creates no new implementation and no new outputs.

Its purpose is to prevent `real(psi)` and `imag(psi)` from being misunderstood as physically derived cosine/sine components.

## 2. Current status anchor

LIC01 is parked.

COMP01 showed first psi compatibility movement.

COMP01-B showed additional component-resolved movement.

COMP01-C is planned to test `label_shuffle` in an identity-sensitive way.

Before COMP01-C, the component split must be documented cleanly.

Current status:

`COMP01C_identity_sensitive_component_contrast_planned`

Previous relevant status anchors:

- `LIC01_tau_epsilon_decision_status_after_J_documented`
- `COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`
- `COMP01B_component_resolved_compatibility_result_documented_candidates_observed_specificity_not_established`

Relevant recent line:

- COMP01 concept
- COMP01 implementation plan
- COMP01 minimal scanner
- COMP01 result note
- COMP01-B component-resolved plan
- COMP01-B component-resolved scanner
- COMP01-B result note
- COMP01-C identity-sensitive component contrast plan
- psi-addition curve analysis / local linear form

Current methodological finding:

- COMP01-B showed additional candidate movement.
- `component_split_mode = real_imag_proxy`
- Same-channel, component balance, and component asymmetry metrics moved.
- `label_shuffle` remains problematic.
- `specificity_established = False`

## 3. Why this note is needed

Red Teams marked the real/imag proxy as needing clarification.

The real working form is:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

However, COMP01-B used complex fingerprints in the numerical diagnostic path.

From that diagnostic representation, `real(psi_i)` was read as a cosine-like proxy and `imag(psi_i)` was read as a sine-like proxy.

This reading can be diagnostically useful, but it is not automatically physical.

Without a clear definition, COMP01-C could build on misleading component language.

## 4. Starting point: real oscillatory form

The project-internal real working form is:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

Interpretation:

- `A_i`: cosine-like / in-phase coefficient
- `B_i`: sine-like / quadrature coefficient
- `k_i`: wave number / diagnostic structure frequency

Amplitude-phase form:

```text
R_i = sqrt(A_i² + B_i²)
φ_i = atan2(B_i, A_i)
psi_i(x)=R_i cos(k_i x - φ_i)
```

This form is a mathematical diagnostic form, not automatically a physical wavefunction.

## 5. Complex diagnostic representation

Complex representations are useful in oscillation, signal, and phase analysis, for example to carry amplitude and phase together.

A complex diagnostic form can be written schematically as:

```text
z_i = u_i + i v_i
```

where:

- `u_i = real(z_i)`
- `v_i = imag(z_i)`

These can be read as two orthogonal diagnostic channels.

However, this is directly a true in-phase/quadrature decomposition only if the complex representation is constructed and referenced that way.

## 6. Definition of real_imag_proxy

Definition:

```text
component_split_mode = real_imag_proxy
```

means:

- `real(psi_i)` is treated as a cosine-like / in-phase diagnostic proxy.
- `imag(psi_i)` is treated as a sine-like / quadrature diagnostic proxy.
- The two channels are used as diagnostic components.
- They are not automatically identical to the analytic `A_i cos(k_i x)` and `B_i sin(k_i x)` terms of the real working form.

The real_imag_proxy is a diagnostic component split of complex pattern fingerprints. It is not a physical reconstruction of the real oscillatory basis unless separately derived.

## 7. What the proxy can mean

The proxy can be useful for testing:

- whether two orthogonal diagnostic channels react differently,
- whether same-channel compatibility is stronger than cross-channel compatibility,
- whether `component_balance_ratio` carries structure,
- whether `component_asymmetry_delta` differentiates structured behavior from controls,
- whether `label_shuffle` breaks under pairwise/rank checks.

The proxy can serve as a first approximation for:

- in-phase-like channel,
- quadrature-like channel,
- component balance,
- component organization.

## 8. What the proxy must not mean

The proxy does not mean:

- `real(psi_i)` is a proven physical cosine component,
- `imag(psi_i)` is a proven physical sine component,
- `psi_i` is a physical wavefunction,
- component channels are physical observables,
- a high overlap is a quantum measurement probability,
- the real/imag split validates a Bridge,
- the real/imag split establishes specificity.

The proxy is a diagnostic engineering choice, not a physical derivation.

## 9. Relation to local linear form

Reference form:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

The local tangent at `x0 = 0` is:

```text
y ≈ B_i k_i x + A_i
```

From this:

- `A_i` can be read as a local intercept / offset.
- `B_i k_i` can be read as a local slope / initial response.

This is a local tangent approximation.

For COMP01-C, this could later become a separate diagnostic idea:

- `intercept_similarity`
- `slope_similarity`
- `slope_intercept_balance`
- `delta_intercept_ij`
- `delta_slope_ij`
- `local_linear_response_overlap`

This note does not implement any of those ideas.

## 10. Consequences for COMP01-C

For COMP01-C:

- `real_imag_proxy` may continue to be used, but only as a documented diagnostic proxy.
- COMP01-C should not claim to physically test true A/B/cos/sin components.
- Results must report `component_split_mode = real_imag_proxy`.
- `label_shuffle` comparisons remain methodological control checks.
- `pairwise_delta`, `rank_correlation`, and `top_quartile_overlap` test identity sensitivity of the proxy, not physical components.
- If COMP01-C shows positive movement, this implies only diagnostic identity-sensitive candidate movement, not physical wavefunction structure and not Bridge validation.

If possible, COMP01-C should distinguish these levels:

1. `real_imag_proxy` channel behavior
2. local-linear `A/Bk` fingerprint behavior
3. future true A/B/cos/sin representation, if later constructed in a physically or mathematically clean way

## 11. Interpretation rules

Outcome A: `real_imag_proxy` metrics show identity-sensitive rank/top-quartile shifts against `label_shuffle`.

Interpretation: The proxy may be diagnostically useful; no physical component claim follows.

Outcome B: `real_imag_proxy` metrics remain near-equal against `label_shuffle`.

Interpretation: The proxy does not solve the `label_shuffle` problem in the current kernel.

Outcome C: Same-channel metrics separate better than cross-channel metrics.

Interpretation: Same-channel organization could be diagnostically useful; no physical statement follows.

Outcome D: `component_balance` or `component_asymmetry` shows pairwise identity sensitivity.

Interpretation: Component organization could be a candidate; it remains synthetic-diagnostic.

Outcome E: All proxy metrics remain close to `label_shuffle`.

Interpretation: COMP01-B/COMP01-C must be redesigned or moved to larger/harder kernels or nulls.

## 12. Recommended next step

COMP01-C implementation may proceed after this definition, but with clear boundaries:

- use existing COMP01-B outputs,
- compare structured vs `label_shuffle`,
- use selected metrics,
- compute `pairwise_delta`,
- compute `rank_correlation`,
- compute `top_quartile_overlap`,
- document `component_split_mode`,
- make no specificity claim by default.

Optional later addition:

`QSB-ST-COMP01-D local linear response fingerprint plan`

only if COMP01-C shows that identity-sensitive checks are useful.

## 13. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- real_imag_proxy is a diagnostic component split, not a physical derivation.
- Component-resolved psi channels are diagnostic decomposition channels, not physical observables by themselves.
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- The local y=mx+b form is a tangent or secant approximation, not a global replacement for psi(x).
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-B / COMP01-C do not attach D(A,B).
- COMP01-B / COMP01-C do not construct S_rel2.
- COMP01-B / COMP01-C do not derive a Lorentzian metric.
- COMP01-B / COMP01-C do not validate a physical Bridge.
- This is synthetic diagnostic work only.

## 14. Current status label

`COMP01B_real_imag_proxy_definition_documented_before_COMP01C`
