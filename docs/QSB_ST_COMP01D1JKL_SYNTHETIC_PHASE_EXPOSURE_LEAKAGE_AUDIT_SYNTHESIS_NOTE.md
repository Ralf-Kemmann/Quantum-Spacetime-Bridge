# QSB-ST COMP01-D1j/k/l Synthetic Phase Exposure and Leakage Audit — Synthesis Note

## 1. Purpose

This note freezes the current D1j/D1k/D1l interpretation as a compact phase-diagnostic mini-sequence.

It is not a result escalation. It is a defensive synthesis of three synthetic diagnostic blocks:

- D1j asks whether explicit phase-like output fields are visible.
- D1k exposes deterministic synthetic diagnostic phase-like fields.
- D1l audits whether the D1k all-clean result is leakage-prone, tautological, or construction-dependent.

Central question kept visible: same type, not same wave.

## 2. Short lineage

D1j, D1k, and D1l form a local mini-sequence inside COMP01-D1:

```text
D1j: explicit phase source inventory and cyclic recheck preparation
D1k: deterministic synthetic phase-field exposure and exposed-phase recheck
D1l: leakage, tautology, construction-dependence, and overclean audit
```

This sequence is synthetic diagnostic work only. It does not validate a physical model and does not establish diagnostic specificity.

```yaml
specificity_established: false
mastermind_status: parked_not_implemented
```

## 3. D1j contribution

D1j found that explicit emitted phase-like output fields were not present in the inspected D1f/D1h outputs.

Key D1j values:

```yaml
case_count: 9450
specificity_established: false
explicit_phase_source_available: false
detected_phase_columns: []
detected_proxy_phase_columns:
  - cyclic_phase_distance
  - cyclic_phase_source
explicit_phase_recheck_possible: false
deterministic_synthetic_phase_extension_needed: true
phase_source_label: cyclic_phase_proxy_with_generator_phase_text_mentions
phase_exposure_mode: reconstructed_from_existing_synthetic_parameters_candidate
cyclic_geometry_recheck_decision_status: explicit_phase_recheck_not_possible
mastermind_status: parked_not_implemented
```

D1j contribution: it prevented treating the D1h proxy result as deproxied cyclic geometry. It showed that a deterministic synthetic phase-field exposure step was needed before testing beyond the proxy baseline.

## 4. D1k contribution

D1k exposed deterministic synthetic diagnostic phase-like fields and ran an exposed-phase cyclic recheck.

Key D1k values:

```yaml
case_count: 9450
specificity_established: false
phase_source_label: diagnostic_synthetic_phase_extension_v1
phase_exposure_mode: deterministic_synthetic_phase_extension
phase_construction_rule: deterministic_atan2_from_available_diagnostic_components
phase_is_synthetic_diagnostic: true
phase_is_physical: false
phase_field_exposure_supported: true
input_component_missing_warning_count: 0
baseline_cyclic_phase_source: cyclic_phase_proxy
baseline_proxy_false_accept_warning_count: 992
baseline_proxy_exclusion_success_rate: 0.9691899612324015
baseline_proxy_stable_candidate_count: 7907
false_accept_warning_exposed_count: 0
exclusion_success_exposed_rate: 1.0
stable_candidate_exposed_count: 9450
fragile_candidate_exposed_count: 0
stable_candidate_loss_rate_exposed: 0.0
remaining_intrusion_warning_count: 0
proxy_vs_exposed_phase_mismatch_count: 1543
proxy_vs_exposed_phase_mismatch_rate: 0.16328042328042328
mastermind_status: parked_not_implemented
```

D1k contribution: it showed that a deterministic synthetic diagnostic phase exposure layer can be built and that the exposed-phase recheck is extremely clean in this synthetic setup.

That cleanliness was useful but audit-triggering.

## 5. D1l contribution

D1l audited the D1k all-clean exposed phase result for leakage, tautology, construction-dependence, ablation sensitivity, shuffled-input behavior, family-blind behavior, threshold behavior, and proxy/exposed mismatch localization.

Key D1l values:

```yaml
case_count: 9450
specificity_established: false
input_consistency_passed: true
d1k_false_accept_warning_exposed_count: 0
d1k_stable_candidate_exposed_count: 9450
d1k_remaining_intrusion_warning_count: 0
d1k_proxy_vs_exposed_phase_mismatch_rate: 0.16328042328042328
direct_feature_leakage_warning: true
label_leakage_warning: false
proxy_leakage_warning: false
target_family_leakage_warning: false
threshold_leakage_warning: false
construction_feedback_leakage_warning: true
tautology_warning: true
overclean_result_warning: true
construction_dependence_warning: true
component_ablation_failure_warning: true
shuffled_input_failure_warning: false
family_blind_failure_warning: false
leakage_warning_count: 3
tautology_warning_count: 1
construction_warning_count: 2
audit_supported_candidate_count: 27
phase_is_physical: false
phase_is_synthetic_diagnostic: true
mastermind_status: parked_not_implemented
```

D1l contribution: it qualifies D1k without discarding it. The exposed phase remains useful as a diagnostic construction, but its all-clean behavior cannot yet be treated as standalone cyclic-geometry support.

## 6. Cross-block Befund

Across D1j/D1k/D1l:

- D1j found no explicit emitted phase-like columns.
- D1j found proxy phase columns and phase-related source/text mentions.
- D1k exposed deterministic diagnostic synthetic phase-like fields.
- D1k produced an all-clean exposed-phase recheck in 9450 cases.
- D1l found warnings for direct-feature leakage, construction feedback, tautology, overclean behavior, construction dependence, and component-ablation sensitivity.
- D1l did not flag label leakage, proxy leakage, target-family leakage, threshold leakage, shuffled-input failure, or family-blind failure in this implementation.
- `specificity_established: false`
- `phase_is_physical: false`
- `phase_is_synthetic_diagnostic: true`

## 7. Cross-block Interpretation

The D1j/k/l sequence supports a cautious methodological interpretation:

D1j shows that proxy-only cyclic phase is not enough. D1k shows that synthetic diagnostic phase exposure can be technically powerful. D1l shows that the all-clean D1k result remains construction-sensitive and leakage-audit constrained.

Current evidence therefore favors a multi-feature wave identity profile, not a single residual score and not a single phase-exposure score.

The phrase same type, not same wave remains the controlling diagnostic caution. Type-like similarity can remain high even when relational identity has not been shown.

## 8. Working hypothesis after D1j/k/l

Hypothese: a robust diagnostic route should combine several channels rather than elevate one channel.

The current candidate channels are:

- phase exposure
- phase leakage behavior
- residual mimicry
- duplicate sanity
- near-duplicate controls
- component ablation
- shuffled-input sanity
- family-blind sanity
- threshold-weight robustness
- channel-specific separability

If the multi-channel profile remains stable under hostile controls, it may become a better synthetic diagnostic identity-profile candidate than `wave_identity_residual` alone or a single exposed-phase score alone.

## 9. Remaining risks

Offene Lücke:

- no real data
- no validation of a physical model
- no diagnostic specificity
- no physical phase reconstruction
- no physical manifold
- no physical wavefunction claim
- no Lorentzian structure
- no physical time
- no Pauli or spin-statistics claim
- no Bridge confirmation
- direct-feature leakage warning remains active in D1l
- construction-feedback leakage warning remains active in D1l
- tautology warning remains active in D1l
- construction-dependence warning remains active in D1l
- component-ablation failure warning remains active in D1l
- overclean-result warning remains active in D1l

Leakage-aware controls and component-ablation checks are mandatory safeguards for the next step.

## 10. Recommended next block

Recommended next block:

```text
QSB-ST-COMP01-D1m Multi-Channel Synthetic Phase Identity Profile Plan
```

COMP01-D1m should turn the D1j/k/l lessons into a compact multi-channel phase identity profile:

- phase exposure
- phase leakage
- residual mimicry
- duplicate sanity
- near-duplicate controls
- component ablation
- shuffled-input sanity
- family-blind sanity
- threshold-weight robustness
- channel-specific separability

The goal is not to validate a physical model, but to test whether a multi-feature profile is more robust than a single `wave_identity_residual` or single phase-exposure score.

Mastermind, Knuth, manifold role search, and role-permutation diagnostics should remain parked until the multi-channel profile passes these safeguards.

## 11. Claim Boundary

This synthesis is synthetic diagnostic documentation only.

It does not create a runner, config, or run.

It does not modify D1j, D1k, or D1l outputs.

It does not introduce a new identity score.

It does not establish diagnostic specificity.

It does not claim physical phase reconstruction.

It does not claim a physical manifold.

It does not claim physical spacetime geometry.

It does not claim a Hilbert-space reconstruction.

It does not claim a Lorentzian metric.

It does not claim physical time.

It does not claim fermionic Pauli exclusion or quantum spin-statistics.

It does not claim Bridge confirmation.

`specificity_established: false`

`phase_is_physical: false`

`phase_is_synthetic_diagnostic: true`

Mastermind, Knuth, manifold search, and role-permutation remain parked.
