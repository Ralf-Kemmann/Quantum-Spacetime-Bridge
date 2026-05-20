# QSB-ST-COMP01-D Wave Identity Fingerprint Observables Concept

## 1. Purpose

COMP01-D documents a conceptual shift after COMP01-C3.

COMP01-C and COMP01-C2 found interesting candidate movement, but COMP01-C3 did not confirm those candidates as stable in the first kernel-level `label_shuffle` smoke test.

Therefore COMP01-D should not simply search for more delay or tau metrics. Instead, it asks:

```text
How can apparently identical or very similar waves be distinguished when no time anchor exists yet?
```

The point is to move from a delay-first question toward wave identity fingerprints and distinguishability without a time anchor.

Not goals:

- model tau,
- claim delay,
- claim causality,
- attach D(A,B),
- construct S_rel2,
- claim a physical wavefunction,
- validate a Bridge,
- claim specificity.

## 2. Current status anchor

Current status:

```text
COMP01C3_real_kernel_resimulation_label_shuffle_result_documented_candidates_not_confirmed_specificity_not_established
```

Last commit anchor:

```text
f4def2e Add QSB-ST COMP01C3 real kernel resimulation label shuffle result note
```

COMP01-C3 finding:

`stable_candidate_metrics`:

- none / empty list

`failed_or_inconclusive_metrics`:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

`label_shuffle_mimic_warning_metrics`:

- none / empty list

`specificity_established = False`

Core interpretation:

- COMP01-C2 showed stability against value-permutation controls.
- COMP01-C3 did not confirm these candidates in the kernel-level `label_shuffle` smoke test.
- Therefore a new search question is useful.

Relevant files:

- `docs/QSB_ST_COMP01C3_REAL_KERNEL_RESIMULATION_LABEL_SHUFFLE_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01C3_REAL_KERNEL_RESIMULATION_LABEL_SHUFFLE_SPECTRUM_MATCHED_CONTROL_PLAN.md`
- `docs/QSB_ST_COMP01C2_CANDIDATE_METRIC_INSPECTION_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01B_REAL_IMAG_PROXY_DEFINITION_NOTE.md`
- `docs/QSB_ST_PSI_ADDITION_CURVE_ANALYSIS_LOCAL_LINEAR_FORM.md`

## 3. Why the question changes after COMP01-C3

COMP01-C3 brakes the current candidate line.

If candidates that respond to relative phase or sine-like overlap do not remain kernel-level stable, this may mean:

- the current observables were still too coarse,
- they tested compatibility but not unique wave identity,
- they could not reliably distinguish apparently similar waves,
- the search for delay or tau may assume too much structure too early.

The question therefore shifts from:

```text
When does a correlation form?
```

to:

```text
Which structure-internal fingerprints distinguish waves before there is a when?
```

## 4. The wrong question: when?

`When?` may be the wrong question here.

Reason:

- a `when` presupposes a time axis or at least a when-like ordering,
- in the hypothetical target zone there may be no `when`, no `before/after`, no tau, and no delay,
- if no time structure exists yet, delay cannot be primary,
- tau must therefore not be searched as the starting variable.

In a pre-temporal or time-poor diagnostic regime, asking for delay may import a temporal structure that the model has not earned yet.

## 5. The better question: how can apparently similar waves be distinguished?

The better question is:

```text
How do I recognize that two apparently identical waves are not the same wave?
```

If two waves have equal or similar overlap / compatibility values, identity markers are needed:

- small spectral differences,
- relative k-shift,
- modulation nuance,
- phase drift,
- phase curvature,
- envelope differences,
- local slope / intercept fingerprints,
- sideband / secondary-mode structure,
- channel balance,
- cross-channel leakage.

The goal is not to measure time. The goal is to distinguish identity without a time anchor.

## 6. Conceptual shift: from compatibility to distinguishability

COMP01 asked:

```text
Which psi(i)-psi(j) compatibility values distinguish structured correlations from controls?
```

COMP01-D asks:

```text
Which wave identity fingerprints distinguish apparently similar waves from truly identical or merely relabeled waves?
```

Compatibility:

- How well do two patterns fit together?

Distinguishability:

- How do two patterns differ despite high similarity?

Identity fingerprint:

- Which structure-internal features survive controls on labels, pairing, ranking, or kernel-level shuffles?

## 7. Candidate fingerprint families

### 7.1 Spectral shift fingerprints

Examples:

- `delta_k`
- `relative_k_shift`
- `wavelength_ratio`
- `spectral_centroid_shift`

Interpretation:

The analogy to redshift is only an image for diagnostic spectral displacement. It is not a cosmological redshift claim.

### 7.2 Phase drift fingerprints

Examples:

- `relative_phase_drift`
- `phase_gradient_delta`
- `phase_curvature_delta`
- `local_phase_shear`

Interpretation:

Phase drift is not a time delay. It is a structure-internal relative displacement marker.

### 7.3 Modulation fingerprints

Examples:

- `envelope_difference`
- `modulation_depth_delta`
- `amplitude_texture_delta`
- `sideband_structure_delta`

Interpretation:

Two waves can share a base frequency while carrying different modulation signatures.

### 7.4 Local linear fingerprints

Reference form:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

Local tangent:

```text
y ≈ B_i k_i x + A_i
```

Examples:

- `intercept_similarity`
- `slope_similarity`
- `slope_intercept_balance`
- `delta_intercept_ij`
- `delta_slope_ij`
- `local_linear_response_overlap`

Interpretation:

Local fingerprints can help distinguish globally similar waves through local intercept and slope structure.

### 7.5 Complex component fingerprints

Preferred future notation:

```text
psi_i(x)=A_i^C cos(k_i x)+B_i^C sin(k_i x)
```

Examples:

- `complex_cos_coefficient_delta`
- `complex_sin_coefficient_delta`
- `component_phase_delta`
- `component_magnitude_delta`
- `real_imag_channel_balance`
- `cross_channel_leakage`

Important:

`real_imag_proxy` remains a proxy until a true complex trigonometric representation is implemented.

## 8. Preferred formal notation

The preferred future formal notation is not primarily the exponential form. It is the complex trigonometric form analogous to the real working equation:

```text
psi_i(x)=A_i^C cos(k_i x)+B_i^C sin(k_i x)
```

with:

```text
A_i^C = A_i^R + i A_i^I
B_i^C = B_i^R + i B_i^I
```

Reasons:

- the project thread remains visible,
- cos / sin channels remain interpretable,
- A / B components remain connected to prior local-linear work,
- complex phase, interference, and overlap become possible,
- no extra Euler-notation conversion is needed as the primary project notation.

The exponential form may be mentioned as mathematically equivalent background, but it should not be the primary project notation for COMP01-D.

## 9. Candidate observables for future scanner design

Primary candidates for future design:

| Observable | What it compares | Why it may distinguish similar waves | Risk / limitation |
|---|---|---|---|
| `delta_k` | Difference of diagnostic wave numbers. | Small spectral offsets can distinguish otherwise similar waves. | Requires stable k estimation. |
| `relative_k_shift` | Relative wave-number displacement. | Scale-normalized spectral shift may survive amplitude changes. | Can become unstable near small k. |
| `relative_phase_drift` | Change of relative phase across support. | A drift pattern can separate relabeled from genuinely distinct waves. | Must not be read as delay. |
| `phase_gradient_delta` | Difference in local phase gradients. | Gradient structure may identify wave identity without time ordering. | Sensitive to phase unwrap choices. |
| `phase_curvature_delta` | Difference in second-order phase structure. | Curvature may detect subtle nonuniform phase changes. | Noisy on small kernels. |
| `envelope_difference` | Difference in amplitude envelopes. | Similar carrier waves can have different envelope signatures. | May confuse amplitude scaling with identity. |
| `modulation_depth_delta` | Difference in modulation depth. | Distinguishes waves with similar base frequency but different modulation. | Needs a defined envelope model. |
| `sideband_structure_delta` | Difference in secondary spectral components. | Sidebands can encode a modulation fingerprint. | Needs enough resolution for sidebands. |
| `slope_similarity` | Similarity of local tangent slopes. | Local slopes can separate globally similar wave forms. | Local point choice matters. |
| `intercept_similarity` | Similarity of local tangent intercepts. | Local offsets can carry identity information. | Offset can be normalization-dependent. |
| `local_linear_response_overlap` | Joint local slope/intercept response. | Combines local linear identity features. | Still diagnostic, not physical time. |
| `complex_component_phase_delta` | Difference of complex A/B component phases. | Component phase may encode identity beyond magnitude. | Requires true complex trig representation. |
| `complex_component_magnitude_delta` | Difference of complex A/B magnitudes. | Component magnitudes may distinguish channels. | May duplicate amplitude features. |
| `cross_channel_leakage` | Leakage between cos-like and sin-like channels. | Channel mixing can reveal non-identical wave structure. | `real_imag_proxy` version remains provisional. |

## 10. Control requirements

Every future COMP01-D scanner needs hard controls:

- identity-preserving reference,
- `label_shuffle`,
- kernel-level `label_shuffle`,
- phase-randomized control,
- amplitude-preserved phase-randomized control,
- distribution-matched control,
- spectrum-matched control,
- local perturbation / noise control,
- same-wave duplicate sanity check,
- near-identical-wave decoy control.

The same-wave duplicate sanity check is especially important.

If two inputs are truly the same wave, the fingerprint must not artificially distinguish them.

The near-identical-wave decoy control is also important.

If two waves are nearly identical, the fingerprint should show whether it is reading noise or genuine structure-internal nuance.

## 11. Interpretation rules

Outcome A:

Fingerprint distinguishes structured from `label_shuffle`, but not same-wave duplicate.

Interpretation:

- usable identity candidate.

Outcome B:

Fingerprint also distinguishes same-wave duplicate.

Interpretation:

- artifact / too sensitive / not usable.

Outcome C:

Fingerprint does not separate structured from kernel-level `label_shuffle`.

Interpretation:

- not robust enough.

Outcome D:

Fingerprint separates only under phase-randomized control, but not under spectrum-matched control.

Interpretation:

- possibly phase-sensitive, but not structure-identity-sensitive.

Outcome E:

Fingerprint survives multiple controls.

Interpretation:

- diagnostic follow-up is justified, but no physical validation follows.

## 12. Relation to tau

COMP01-D does not treat tau as a primitive quantity.

Tau could re-enter later only as a derived quantity if wave identity fingerprints show stable structure relations.

Tau should not be searched as a clock in this block. If tau re-enters later, it should enter as a derived relational latency from already distinguishable correlation patterns, not as the first diagnostic variable.

Nicht die Uhr suchen, bevor klar ist, welche Welle welche ist.

## 13. What this concept must not claim

This concept must not claim:

- physical time,
- delay evidence,
- tau evidence,
- causality,
- spacetime,
- wavefunction in the physical sense,
- redshift in the cosmological sense,
- Bridge validation,
- specificity.

## 14. Recommended next step

A QSB-ST-COMP01-D implementation plan should not start directly with many metrics.

First recommended next block:

```text
QSB-ST-COMP01-D1 wave identity fingerprint minimal design plan
```

Minimal D1 should select only three families:

1. spectral shift / `delta_k`
2. phase drift / `phase_gradient_delta`
3. local linear fingerprint / slope-intercept

Not yet:

- full complex trigonometric implementation,
- large scanner,
- tau model,
- D(A,B),
- S_rel2.

## 15. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- wave identity fingerprints are diagnostic distinguishability observables, not physical observables by themselves.
- spectral shift is used here as a diagnostic analogy, not as cosmological redshift.
- phase drift is used here as a structure-internal pattern marker, not as physical time delay.
- real_imag_proxy is a diagnostic component split, not a physical derivation.
- The complex trigonometric notation is a planned formal representation, not yet an implemented physical wavefunction model.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-D does not attach D(A,B).
- COMP01-D does not construct S_rel2.
- COMP01-D does not derive a Lorentzian metric.
- COMP01-D does not validate a physical Bridge.
- COMP01-D does not establish diagnostic specificity yet.
- This is synthetic diagnostic concept work only.

## 16. Current status label

```text
COMP01D_wave_identity_fingerprint_observables_concept_documented
```
