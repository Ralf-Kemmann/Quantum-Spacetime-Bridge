# QSB-ST COMP01-D1l Synthetic Phase Leakage and Tautology Audit — Result Note

## 1. Purpose

This document records the existing QSB-ST-COMP01-D1l Synthetic Phase Leakage and Tautology Audit run.

D1l is a synthetic diagnostic leakage, tautology, construction-dependence, and overclean-behavior audit for the D1k exposed synthetic phase layer. It documents an already completed run; it does not start a new run, change the runner, add a config, modify prior outputs, or create a new identity score.

D1l preserves D1k as technically useful but construction-dependent. It qualifies the D1k result rather than invalidating it.

## 2. Inputs inspected

The result note is based on the committed D1l implementation and existing D1l run outputs:

- `data/qsb_st_comp01d1l_synthetic_phase_leakage_tautology_audit_config.yaml`
- `scripts/run_qsb_st_comp01d1l_synthetic_phase_leakage_tautology_audit.py`
- `docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE_TEMPLATE.md`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/summary.json`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/readout.md`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/leakage_taxonomy_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/construction_variant_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/component_ablation_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/shuffled_input_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/family_blind_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/threshold_weight_sweep_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/proxy_exposed_mismatch_localization.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/resolved_config.json`

Context files inspected for the D1j/D1k lineage:

- `docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_RESULT_NOTE.md`
- `runs/QSB-ST-COMP01D1J/explicit_phase_field_exposure_cyclic_recheck_open/summary.json`
- `docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_RESULT_NOTE.md`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/summary.json`

## 3. Method summary

D1l reads the D1k exposed phase case table, the D1h cyclic proxy baseline, and the D1f case profile table. It joins cases by `case_id` and requires at least 9000 matched cases before interpreting the audit.

The audit compares D1k against controlled variants:

- leakage taxonomy checks
- construction variants
- component ablations
- shuffled-input variants
- family-blind checks
- threshold and weight sweeps
- proxy-vs-exposed mismatch localization

The audit does not rerun D1f and does not modify D1f, D1h, or D1k outputs.

## 4. Befund

D1l completed on the full 9450-case synthetic diagnostic set.

Machine-readable summary:

```yaml
case_count: 9450
specificity_established: false
input_consistency_passed: true
does_not_rerun_d1f: true
does_not_modify_d1f_outputs: true
does_not_modify_d1h_outputs: true
does_not_modify_d1k_outputs: true
does_not_introduce_physical_phase: true
does_not_introduce_physical_manifold: true
does_not_introduce_new_identity_score: true
does_not_implement_mastermind: true
phase_is_physical: false
phase_is_synthetic_diagnostic: true
mastermind_status: parked_not_implemented
```

D1k baseline entering D1l:

```yaml
d1k_false_accept_warning_exposed_count: 0
d1k_stable_candidate_exposed_count: 9450
d1k_remaining_intrusion_warning_count: 0
d1k_proxy_vs_exposed_phase_mismatch_rate: 0.16328042328042328
```

D1l warning results:

```yaml
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
```

Audit-family details:

- Leakage taxonomy: direct-feature leakage, construction-feedback leakage, and overclean-result warnings are active; label, proxy, target-family, and threshold leakage warnings are not active in this implementation.
- Construction variants: 10 variants were checked; 6 retained baseline-like cleanliness and 4 raised construction-dependence warnings.
- Component ablations: 7 variants were checked; 3 survived ablation and 4 raised component-ablation failure warnings.
- Shuffled-input variants: 8 variants were checked; none survived as all-clean, and no shuffled-input failure warning was raised.
- Family-blind variants: 6 variants were checked; all survived family blindness, and no target-family leakage warning was raised.
- Threshold/weight sweep: 25 variants were checked; 13 remained overclean and no threshold-leakage warning was raised.
- Proxy/exposed mismatch localization: 1543 mismatch rows were localized.

## 5. Interpretation

D1l does not invalidate D1k, but it prevents interpreting the D1k all-clean exposed-phase result as standalone cyclic-geometry support. The audit raises direct-feature leakage, construction-feedback, tautology, construction-dependence, component-ablation, and overclean-result warnings, while not detecting label, proxy, target-family, threshold, shuffled-input, or family-blind failures in this implementation.

The D1k layer remains technically useful: it exposes deterministic diagnostic synthetic phase-like fields and provides a strong synthetic separation behavior. D1l qualifies that behavior by showing that the all-clean result depends on construction choices and on components that overlap downstream decision-driving quantities.

The warnings are audit findings, not a global failure of D1k. They mean the D1k exposed phase layer should be treated as a construction-dependent diagnostic classifier layer until stronger hostile controls are passed.

## 6. Hypothese

The D1k exposed synthetic phase layer may still encode useful diagnostic structure, because shuffled-input variants disrupt the all-clean behavior and family-blind checks do not indicate direct use of family identity fields.

At the same time, the direct-feature leakage, component-ablation sensitivity, construction dependence, and overclean baseline suggest that the current phase layer may partly repackage already-decisive diagnostic components.

The next working hypothesis should therefore be: a multi-channel diagnostic identity profile may be more robust than a single exposed phase score.

## 7. Offene Lücke

- no real data
- no validation of a physical model
- no diagnostic specificity
- `specificity_established: false`
- `phase_is_physical: false`
- `phase_is_synthetic_diagnostic: true`
- no physical phase reconstruction
- no physical manifold
- no Lorentzian structure
- no physical time
- no physical wavefunction claim
- no Pauli or spin-statistics claim
- no Bridge confirmation
- no single-score identity result
- no Mastermind / Knuth / manifold role search yet

## 8. Claim Boundary

D1l is synthetic diagnostic work only.

D1l audits leakage, tautology, construction-dependence, and overclean behavior in the D1k exposed synthetic phase layer.

D1l does not rerun D1f.

D1l does not modify D1f, D1h, or D1k outputs.

D1l does not introduce a new identity score.

D1l does not establish diagnostic specificity.

The D1k exposed phase-like fields are diagnostic synthetic fields.

They are not physical phase reconstruction.

`phase_is_physical: false`

`phase_is_synthetic_diagnostic: true`

Cyclic-coordinate language remains a diagnostic coordinate model, not a physical spacetime claim.

Mastermind, Knuth, role-permutation, and manifold search remain parked.

## 9. Consequence for next step

The next step should not be claim escalation and not Mastermind/Knuth/manifold search.

The next block should convert the D1j/D1k/D1l lesson into a compact multi-channel diagnostic profile that tests phase exposure alongside leakage resistance, residual mimicry, duplicate sanity, near-duplicate controls, ablation behavior, shuffled-input sanity, family-blind sanity, threshold-weight robustness, and channel-specific separability.

Recommended next block:

```text
QSB-ST-COMP01-D1m Multi-Channel Synthetic Phase Identity Profile Plan
```

## 10. Files created / checked

This result note creates only this documentation file:

- `docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE.md`

Checked source artifacts include the D1l config, runner, result template, summary, readout, all D1l CSV audit outputs, resolved config, and the D1j/D1k result notes and summaries listed above.
