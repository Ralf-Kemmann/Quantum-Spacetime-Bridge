# QSB-ST COMP01-D1m Multi-Channel Synthetic Phase Identity Profile — Plan

## 1. Purpose

D1m is a plan for a compact multi-channel synthetic phase identity profile.

It turns the D1j/D1k/D1l lessons into a guarded profile design for asking whether a candidate pair is the same type, not same wave. It does not implement a runner, does not create a config, does not start a run, and does not calculate a new identity score.

This is synthetic diagnostic planning only. It does not validate a physical model, does not introduce physical phase, and does not start Mastermind, Knuth, manifold search, or role-permutation diagnostics.

Core status anchors:

```yaml
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
```

## 2. Starting point from D1j/k/l

D1j found no explicit emitted phase-like output field in the inspected D1f/D1h outputs. Proxy phase columns were detected, but an explicit phase recheck was not possible. D1j therefore showed that deterministic synthetic phase-field exposure was needed before moving beyond a proxy-only cyclic phase baseline.

D1k exposed deterministic synthetic diagnostic phase-like fields and produced an extremely clean synthetic recheck. The D1k run reported `phase_is_synthetic_diagnostic: true`, `phase_is_physical: false`, and `specificity_established: false`. The clean result was technically useful, but it was also audit-triggering.

D1l qualified D1k. It did not invalidate D1k, but it prevented treating the D1k all-clean result as standalone cyclic-geometry support. Active D1l warnings include direct-feature leakage, construction-feedback leakage, tautology, overclean result, construction dependence, and component-ablation sensitivity. D1l did not detect label leakage, proxy leakage, target-family leakage, threshold leakage, shuffled-input failure, or family-blind failure in that implementation.

D1m therefore plans a multi-channel profile rather than a single residual score or a single phase-exposure score.

## 3. Core diagnostic question

Woran merke ich, dass ich die gleiche, aber nicht dieselbe Welle habe?

In D1m this is a synthetic diagnostic identity question. It asks whether a case pair shares enough type-like structure to look similar while still failing relational identity checks.

The internal heuristic is:

```text
same type, not same wave
```

This heuristic is not a Pauli claim, not a spin-statistics claim, not a physical identity claim, and not a physical wavefunction claim.

## 4. Proposed profile channels

D1m should treat identity-like behavior as a guarded multi-channel profile. No single channel should silently dominate the profile.

Profile channels:

- phase exposure channel
  - purpose: report whether the synthetic diagnostic phase exposure layer is available and informative.
  - expected input: D1k exposed phase fields and D1k summary values.
  - expected output field names: `phase_exposure_score`, `phase_is_synthetic_diagnostic`, `phase_is_physical`.
  - warning condition: missing phase exposure, overclean exposure, or exposure dominated by one construction.
  - interpretation boundary: diagnostic synthetic phase only, not physical phase.

- phase leakage channel
  - purpose: carry D1l leakage warnings into the profile.
  - expected input: D1l leakage taxonomy summary and D1l summary.
  - expected output field names: `phase_leakage_flag`, `phase_leakage_warning_count`.
  - warning condition: direct-feature leakage, construction-feedback leakage, proxy leakage, label leakage, family leakage, or overclean warnings.
  - interpretation boundary: leakage flags qualify usefulness; they do not erase the technical D1k exposure result by themselves.

- residual mimicry channel
  - purpose: check whether the pair remains close only because a residual-like channel is mimicked.
  - expected input: D1f/D1h residual or profile-distance fields where present.
  - expected output field names: `residual_mimicry_score`, `residual_mimicry_warning`.
  - warning condition: near-identical residual behavior under decoy or null controls.
  - interpretation boundary: residual closeness is type-like similarity, not relational identity.

- duplicate sanity channel
  - purpose: keep exact duplicate and direct duplicate controls separate from near-duplicate or impostor behavior.
  - expected input: D1f duplicate sanity fields and control-family labels where present.
  - expected output field names: `duplicate_sanity_passed`, `duplicate_control_label`.
  - warning condition: direct duplicates fail sanity checks or non-duplicates look indistinguishable from duplicates.
  - interpretation boundary: duplicate sanity is a control condition, not a physical identity statement.

- near-duplicate control channel
  - purpose: detect intrusion from near-duplicate, adversarial, or mimicry controls.
  - expected input: D1h/D1l decoy family fields and mismatch localization.
  - expected output field names: `near_duplicate_intrusion_flag`, `near_duplicate_control_family`.
  - warning condition: near-duplicates remain stable or enter an acceptance region under the profile.
  - interpretation boundary: near-duplicate intrusion marks diagnostic ambiguity, not physical particle creation.

- component ablation channel
  - purpose: test whether the profile depends too strongly on one construction component.
  - expected input: D1l component ablation summary.
  - expected output field names: `component_ablation_stability_score`, `component_ablation_warning`.
  - warning condition: profile behavior collapses when a decision-driving component is removed.
  - interpretation boundary: ablation sensitivity is a construction-dependence warning, not a physical result.

- shuffled-input sanity channel
  - purpose: test whether channel structure depends on case-level alignment.
  - expected input: D1l shuffled-input summary.
  - expected output field names: `shuffled_input_survival_flag`, `shuffled_input_warning`.
  - warning condition: shuffled inputs keep the profile too clean or mimic the unshuffled result.
  - interpretation boundary: shuffle survival can signal leakage or an overly permissive test.

- family-blind sanity channel
  - purpose: test whether the profile works without direct control-family identity fields.
  - expected input: D1l family-blind summary.
  - expected output field names: `family_blind_survival_flag`, `family_blind_warning`.
  - warning condition: family identity is required for the result or removal changes behavior unexpectedly.
  - interpretation boundary: family-blind survival is useful only when interpreted with leakage and ablation.

- threshold-weight robustness channel
  - purpose: test whether the profile depends on a narrow threshold or weight window.
  - expected input: D1l threshold/weight sweep summary.
  - expected output field names: `threshold_weight_stability_score`, `threshold_weight_warning`.
  - warning condition: only a narrow parameter window works, or all windows are too clean.
  - interpretation boundary: robustness across thresholds is still synthetic diagnostic behavior only.

- channel-specific separability channel
  - purpose: report which channels separate candidate, duplicate, near-duplicate, null, and control families.
  - expected input: per-channel scores and control-family summaries.
  - expected output field names: `channel_specific_separability_score`, `dominant_channel_id`, `single_channel_dominance_warning`.
  - warning condition: one channel explains nearly all separation or one family drives the result.
  - interpretation boundary: separability supports further diagnostic refinement only.

Continuous field list for the future `profile_case_summary.csv`:

| field name | field type | field description |
| --- | --- | --- |
| case_id | string | Stable case identifier joined across D1j/D1k/D1l-derived artifacts when available. |
| family | string | Control or case family label used for grouped reporting. |
| variant_id | string | Profile or control variant identifier. |
| phase_exposure_score | float | Diagnostic score summarizing exposed synthetic phase behavior. |
| phase_leakage_flag | boolean | True when leakage audit warnings affect the case or variant. |
| residual_mimicry_score | float | Diagnostic score for residual-like mimicry risk. |
| duplicate_sanity_passed | boolean | True when direct duplicate sanity behavior is consistent with expectation. |
| near_duplicate_intrusion_flag | boolean | True when near-duplicate or adversarial controls intrude. |
| component_ablation_stability_score | float | Stability score across component ablation variants. |
| shuffled_input_survival_flag | boolean | True when shuffled inputs retain the profile signal suspiciously. |
| family_blind_survival_flag | boolean | True when family-blind variants retain the profile behavior. |
| threshold_weight_stability_score | float | Stability score across threshold and weight sweeps. |
| channel_specific_separability_score | float | Per-case or per-family separability score aggregated across channels. |
| multi_channel_identity_profile_score | float | Guarded aggregate profile score, reported with channel dominance checks. |
| profile_warning_count | integer | Count of active profile warnings. |
| profile_decision_label | string | Cautious machine-readable profile decision label. |
| profile_decision_reason | string | Short reason for the profile decision label. |
| dominant_channel_id | string | Channel that contributes the largest share of profile separation. |
| single_channel_dominance_warning | boolean | True when the profile is dominated by one channel. |
| phase_is_physical | boolean | Always false for this synthetic diagnostic profile. |
| phase_is_synthetic_diagnostic | boolean | Always true when the phase channel is present. |
| specificity_established | boolean | Remains false for the planning block. |

## 5. Required controls and safeguards

D1m must include the following controls and safeguards:

- direct duplicate controls
- near-duplicate controls
- shuffled-input controls
- family-blind controls
- component ablation
- threshold/weight sweep
- leakage taxonomy
- overclean-result warning
- construction-dependence warning
- proxy-vs-exposed mismatch localization
- single-channel dominance warning

D1m should require every profile result to report both an aggregate profile view and channel-specific warning flags.

The single-channel dominance warning is mandatory because a multi-channel plan fails its purpose if one unguarded channel silently decides the outcome.

## 6. Proposed input artifacts

Existing inputs:

- `docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1JKL_SYNTHETIC_PHASE_EXPOSURE_LEAKAGE_AUDIT_SYNTHESIS_NOTE.md`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/summary.json`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/readout.md`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/leakage_taxonomy_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/construction_variant_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/component_ablation_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/shuffled_input_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/family_blind_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/threshold_weight_sweep_summary.csv`
- `runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/proxy_exposed_mismatch_localization.csv`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/cyclic_region_case_summary.csv`
- `runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv`

Proposed future inputs may include D1m-specific config and profile-channel maps, but those files are not created by this plan.

## 7. Proposed output artifacts

Future D1m runner outputs should be written under:

```text
runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/
```

Planned output artifacts:

- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/summary.json`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/readout.md`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/profile_case_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/channel_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/control_family_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/warning_taxonomy_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/resolved_config.json`

This plan creates none of those future output artifacts.

## 8. Acceptance criteria

Future D1m implementation should require:

- file parses as Markdown
- all required sections present
- all proposed output fields listed with type and description
- no physical-model validation claim
- `specificity_established` remains false unless a future hostile-control suite changes the project status under a separately documented standard
- `phase_is_physical` remains false
- `phase_is_synthetic_diagnostic` remains true
- Mastermind/Knuth/manifold remain parked
- D1m should not reduce the whole profile to one unguarded score
- D1m must report whether the profile is dominated by one channel
- readout separates Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary
- profile warning taxonomy is machine-readable
- profile case rows retain case-level traceability

## 9. Befund expected from this plan

D1m is expected to produce a design for testing whether a multi-channel profile is more robust than a single residual or single phase-exposure score.

It should not claim that robustness has already been demonstrated.

Expected planning-level Befund:

- D1m defines a guarded set of profile channels.
- D1m defines controls that must accompany any aggregate profile score.
- D1m defines field names for a future case-level profile table.
- D1m keeps `specificity_established: false`.
- D1m keeps `phase_is_physical: false`.
- D1m keeps `phase_is_synthetic_diagnostic: true`.

## 10. Interpretation rules

- If multiple channels agree and controls fail to mimic, this supports further diagnostic refinement.
- If one channel dominates, mark `single_channel_dominance_warning`.
- If near-duplicates intrude, mark residual mimicry risk.
- If shuffled inputs survive, mark construction or leakage risk.
- If family-blind checks survive, do not automatically treat this as success; interpret it together with leakage and ablation.
- If all results are too clean, trigger `overclean_result_warning`.
- Never interpret the profile as physical phase, physical wavefunction, physical spacetime, or diagnostic specificity.

Interpretation must stay case-level and channel-specific wherever possible.

## 11. Hypothese

A multi-feature synthetic phase identity profile may be more robust than a single `wave_identity_residual` or single exposed-phase score for distinguishing same-type but not-same relational wave cases.

The working expectation is not that one number identifies a wave. The expectation is that the pattern of channel agreement, channel disagreement, and control resistance may be more informative than any single channel alone.

## 12. Offene Lücke

- no real data
- no validation of a physical model
- no diagnostic specificity
- no physical phase reconstruction
- no physical wavefunction
- no physical spacetime geometry
- no physical time
- no Lorentzian metric
- no Hilbert-space reconstruction
- no Pauli/spin-statistics claim
- no Bridge confirmation
- Mastermind / Knuth / manifold search still parked
- no D1m runner yet
- no D1m config yet
- no D1m run output yet

## 13. Claim Boundary

This is synthetic diagnostic planning only.

This plan does not implement a runner.

No new identity score is calculated yet.

No physical phase is introduced.

No physical manifold is introduced.

No physical model validation is claimed.

```yaml
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
```

The profile is a diagnostic representation of synthetic channel behavior, not a physical wavefunction and not physical spacetime geometry.

Mastermind, Knuth, manifold search, and role-permutation diagnostics remain parked.

## 14. Next-step implementation sketch

Future D1m runner should:

1. read D1j/D1k/D1l summaries and available case-level CSVs
2. assemble per-case profile rows
3. compute channel-level summaries
4. compute control-family summaries
5. flag profile warnings
6. report single-channel dominance
7. produce `summary.json`, `readout.md`, `profile_case_summary.csv`, `channel_summary.csv`, `control_family_summary.csv`, `warning_taxonomy_summary.csv`, and `resolved_config.json`

Do not implement the runner now.
