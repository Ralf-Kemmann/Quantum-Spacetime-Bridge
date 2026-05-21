# QSB-ST-COMP01-D1l Synthetic Phase Leakage and Tautology Audit Plan

## 1. Purpose

D1l is a planning-only block for a leakage, tautology, and construction-dependence audit of the D1k exposed synthetic phase-field result.

D1l does not create a scanner, config, run, or result. It plans how to test whether the D1k all-clean result provides additional diagnostic separation information, repackages decision-driving components, or becomes tautological, leakage-prone, or overfit-like through construction.

D1l does not build a new identity score. D1l does not build physical phase. D1l does not establish diagnostic specificity.

The audit focus is the D1k exposed synthetic phase layer:

- whether it carries independent diagnostic structure
- whether it repackages decision-driving components
- whether it reconstructs the downstream decision boundary
- whether it remains robust under ablation, shuffling, family blindness, alternative construction, threshold sweeps, and hostile intrusion controls

## 2. Current status anchor

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented
- COMP01-D1d Manifold Degeneracy Audit implemented and result documented
- COMP01-D1e Collision-Aware Profile Runner implemented and result documented
- COMP01-D1f Robustness Sweep Runner implemented and result documented
- COMP01-D1g Warning Driver Decomposition Runner implemented and result documented
- COMP01-D1h Cyclic-Coordinate Acceptance-Region Runner implemented and result documented
- COMP01-D1i Cyclic-Phase Source Validation and Overstrictness Audit Runner implemented and result documented
- COMP01-D1j Explicit Phase-Field Exposure and Cyclic Geometry Recheck Runner implemented and result documented
- COMP01-D1k Deterministic Synthetic Phase-Field Exposure Extension Runner implemented and result documented

Current commit anchor:

```yaml
commit_anchor: 6746917 Add QSB-ST COMP01D1k deterministic synthetic phase exposure result note
```

D1k reference values:

```yaml
case_count: 9450
specificity_established: false
phase_source_label: diagnostic_synthetic_phase_extension_v1
phase_exposure_mode: deterministic_synthetic_phase_extension
phase_construction_rule: deterministic_atan2_from_available_diagnostic_components
phase_is_synthetic_diagnostic: true
phase_is_physical: false
phase_field_exposure_supported: true
false_accept_warning_exposed_count: 0
exclusion_success_exposed_rate: 1.0
stable_candidate_exposed_count: 9450
fragile_candidate_exposed_count: 0
stable_candidate_loss_rate_exposed: 0.0
remaining_intrusion_warning_count: 0
proxy_vs_exposed_phase_mismatch_rate: 0.16328042328042328
cyclic_geometry_recheck_decision_status: exposed_phase_geometry_reduces_false_accept_candidate
mastermind_status: parked_not_implemented
```

## 3. Motivation from D1k

D1k exposed deterministic diagnostic synthetic phase-like fields and produced an unusually clean cyclic-geometry recheck:

- zero exposed false-accept warnings
- zero exposed remaining intrusion warnings
- zero stable-candidate loss
- all 9450 cases classified stable under the exposed phase layer

This is technically positive but scientifically suspicious.

D1l is not a claim escalation. It is a safety audit for leakage, tautology, construction dependence, and overfit-like behavior in the synthetic exposed phase layer.

## 4. Central question

Does the D1k exposed synthetic phase layer carry independent diagnostic structure, or does it repackage decision-driving variables in a way that makes the cyclic recheck tautologically clean?

Does the all-clean D1k result survive ablation, shuffling, blindness, alternative construction, and hostile control tests?

## 5. Why leakage and tautology audit is required

- D1k constructs phase-like fields from available diagnostic components.
- Those components may already encode classification-relevant information.
- The exposed-phase result is all-clean.
- All-clean results are useful but dangerous.
- A result with 0 false accepts, 0 intrusions, and 9450 stable candidates may reflect strong structure or construction leakage.
- Before Mastermind/Knuth/manifold search, the phase layer must pass leakage and tautology checks.
- Specificity remains false.

The audit is required because a synthetic phase coordinate can be technically useful while still being methodologically circular. The next step must therefore stress the construction instead of escalating the claim.

## 6. Leakage risk taxonomy

- direct_feature_leakage: exposed phase uses variables that directly enter the downstream cyclic acceptance decision.
- label_leakage: exposed phase construction accidentally uses `current_false_accept_warning`, `stable_candidate`, `fragile_candidate`, `decision_status`, decoy family labels, null family labels, or other classification labels.
- proxy_leakage: exposed phase reconstructs or closely tracks `cyclic_phase_proxy` or `cyclic_acceptance_distance`.
- target_family_leakage: exposed phase uses `decoy_family`, `null_family`, `profile_weight_set_id`, or `penalty_weight_set_id` in a way that can encode control identity.
- threshold_leakage: exposed phase is optimized around thresholds used for acceptance.
- construction_feedback_leakage: exposed phase was designed after observing D1h/D1i/D1j failures and may encode compensatory logic.
- overclean_result_warning: the all-clean result itself triggers audit escalation.

Each leakage class should be reported as a machine-readable warning if detected, and each warning should be separated from interpretation.

## 7. Tautology risk taxonomy

- same_variable_reuse_tautology
- acceptance_distance_repackaging
- decision_boundary_reconstruction
- synthetic_phase_as_classifier_proxy
- stable_candidate_circularity
- intrusion_rule_reuse
- component_rank_tautology
- decoy_exclusion_tautology

A tautological exposed phase can look geometrically meaningful while merely repackaging the decision boundary.

The audit must distinguish a coordinate that reveals useful synthetic structure from a coordinate that is effectively another expression of the existing classifier.

## 8. Construction-dependence audit design

Planned construction variants:

- baseline_d1k_construction
- alternate_pair_1_profile_vs_control
- alternate_pair_2_penalty_vs_decoy
- alternate_pair_3_collision_vs_profile
- swapped_phi_i_phi_j_construction
- sign_flipped_component_construction
- normalized_rank_component_construction
- zscore_component_construction
- monotone_transform_component_construction
- noise_jittered_component_construction

For each variant, later implementation should report:

- false_accept_warning_exposed_count
- stable_candidate_exposed_count
- stable_candidate_loss_rate_exposed
- remaining_intrusion_warning_count
- proxy_vs_exposed_phase_mismatch_rate
- decision_status

If only the baseline construction remains all-clean, the result may be construction-dependent. If every construction remains all-clean, the audit should also check whether the downstream test is too permissive or tautological.

## 9. Component ablation audit design

Planned component ablations:

- remove_profile_distance_raw
- remove_control_overlap_rate
- remove_profile_distance_collision_penalized
- remove_decoy_success_rate
- remove_penalty_gap
- remove_each_component_one_at_a_time
- remove_all_direct_acceptance_components
- use_phase_components_not_used_in_acceptance_distance

If the D1k result works only with decision-driving components, the later audit must raise a leakage or tautology warning.

The component_ablation family should preserve the case table and prior outputs unchanged while constructing new audit variants in a separate D1l run output directory.

## 10. Shuffled-input audit design

Planned shuffled-input variants:

- shuffle_phi_i_source_component
- shuffle_phi_j_source_component
- shuffle_A_component_within_family
- shuffle_B_component_within_family
- shuffle_components_across_families
- permute_case_id_alignment
- preserve_marginal_distribution_shuffle
- preserve_family_distribution_shuffle

If the all-clean result remains under shuffling, the phase is likely not informative or the test is too soft. If the all-clean result holds only without shuffling, the result may reflect real synthetic structure or leakage; further blindness tests are then required.

The shuffled variants should preserve enough marginal structure to distinguish arbitrary breakage from true dependence on case-level alignment.

## 11. Decoy-blind and null-family-blind construction audit

Planned blindness variants:

- build exposed phase without `decoy_family`
- build exposed phase without `null_family`
- build exposed phase without `profile_weight_set_id`
- build exposed phase without `penalty_weight_set_id`
- build exposed phase without `kernel_size_label`
- build exposed phase without any control-family identity field

The construction should not use label or family identities. If such fields are required to preserve the D1k effect, the audit must raise `target_family_leakage_warning`.

The family-blind audit should report both decoy-blind and null-family-blind outcomes separately.

## 12. Alternative deterministic phase construction audit

Planned alternative deterministic construction families:

- atan2_component_pair_v1
- atan2_component_pair_v2
- cos_sin_embedding_v1
- rank_angle_embedding_v1
- normalized_polar_angle_v1
- orthogonal_component_basis_v1
- residual_only_phase_v1
- control_blind_phase_v1

A robust phase layer should not be all-clean only for one construction, but it also should not remain magically all-clean for every arbitrary construction. Both extremes are suspicious in different ways.

The alternative constructions should preserve `phase_is_synthetic_diagnostic: true` and `phase_is_physical: false`.

## 13. Threshold and overstrictness re-audit

Planned threshold and weight sweeps:

- cyclic_acceptance_distance_threshold: 0.10, 0.15, 0.20, 0.25, 0.30
- cyclic_phase_weight: 0.25, 0.35, 0.45, 0.55, 0.65
- profile_distance_weight paired compensation
- stable_candidate_loss_warning_rate sweep

If D1k works only in a narrow threshold window, the audit should raise a threshold-dependence warning. If all thresholds remain all-clean, the audit should check for an overclean or overpermissive warning.

The threshold audit should also report whether the exposed layer becomes overstrict when the cyclic phase weight increases.

## 14. Stability and intrusion stress tests

Targeted intrusion and stability families:

- spectrum_matched_null
- adversarial_near_duplicate_sweep
- local_response_dominant
- strong_collision_penalties
- kernel_size_8
- impostor_overlap_warning
- cosmetic_penalty_lock
- phase_randomized_null
- phase_jittered_decoy

D1l should identify which families re-enter the false-accept or intrusion region when leakage and tautology protections are active.

The stress tests should compare each intrusion family against the D1k all-clean baseline and against the D1h proxy baseline.

## 15. Proxy-vs-exposed comparison audit

D1k reported:

```yaml
proxy_vs_exposed_phase_mismatch_rate: 0.16328042328042328
```

Planned mismatch localization:

- case-level mismatch analysis
- mismatch by `decoy_family`
- mismatch by `null_family`
- mismatch by `kernel_size_label`
- mismatch by `profile_weight_set_id`
- mismatch by `penalty_weight_set_id`
- compare mismatch cases against D1h false accepts and D1k all-stable cases

The 1543 mismatch cases are diagnostically interesting and must be localized.

Mismatch analysis should ask whether exposed phase genuinely changes the case geometry or simply suppresses the D1h proxy warning region.

## 16. Decision-table integration

Planned cautious labels:

- leakage_audit_supported_candidate
- direct_feature_leakage_warning
- label_leakage_warning
- proxy_leakage_warning
- target_family_leakage_warning
- threshold_leakage_warning
- construction_feedback_leakage_warning
- tautology_warning
- overclean_result_warning
- construction_dependence_warning
- component_ablation_failure_warning
- shuffled_input_failure_warning
- decoy_blind_supported_candidate
- null_family_blind_supported_candidate
- stable_retention_supported_candidate
- exposed_phase_survives_hostile_controls_candidate
- exposed_phase_fails_hostile_controls_warning
- mastermind_parked_not_implemented
- inconclusive
- failed_input_consistency_check

No decision label may claim proof, proven status, validation, physical identity, or specificity established.

## 17. Mastermind / Knuth / manifold parking note

Ralf/Nova noted a later variable-dimensional manifold / Knuth / Mastermind-style pairwise role-pruning idea:

- n can define the number of available diagnostic dimensions
- k can define local chart/combination size
- impossible or methodologically meaningless combinations can be excluded
- Knuth/Mastermind-style feedback can later search the reduced role-space
- this is not part of D1l
- it should be considered only after the exposed synthetic phase layer passes leakage/tautology/construction-dependence audit

Mastermind, Knuth, and manifold role-permutation diagnostics remain parked.

## 18. Planned implementation design

A later D1l implementation should:

- read `phase_exposed_case_profile_summary.csv` from D1k
- read `cyclic_region_case_summary.csv` from D1h
- construct audit variants without changing prior outputs
- run ablation variants
- run shuffled-input variants
- run family-blind variants
- run alternative deterministic constructions
- run threshold and weight sweeps
- compare all variants to the D1k baseline
- localize proxy-vs-exposed mismatch cases
- summarize leakage and tautology warnings
- keep Mastermind parked
- not modify any closed prior outputs

The implementation should stop with `failed_input_consistency_check` if required case IDs or baseline columns cannot be matched.

## 19. Planned output files for later implementation

Plan only. D1l does not create these files yet:

```text
data/qsb_st_comp01d1l_synthetic_phase_leakage_tautology_audit_config.yaml
scripts/run_qsb_st_comp01d1l_synthetic_phase_leakage_tautology_audit.py
docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE_TEMPLATE.md
```

Planned later run outputs:

```text
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/summary.json
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/readout.md
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/leakage_taxonomy_summary.csv
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/construction_variant_summary.csv
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/component_ablation_summary.csv
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/shuffled_input_summary.csv
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/family_blind_summary.csv
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/threshold_weight_sweep_summary.csv
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/proxy_exposed_mismatch_localization.csv
runs/QSB-ST-COMP01D1L/synthetic_phase_leakage_tautology_audit_open/resolved_config.json
```

## 20. Continuous field list

| field name | field type | field description |
| --- | --- | --- |
| run_id | string | D1l audit run identifier. |
| audit_variant_id | string | Unique identifier for the audit variant. |
| audit_family | string | Audit family such as construction, ablation, shuffled input, family-blind, threshold, or intrusion stress. |
| leakage_risk_type | string | Leakage risk type assigned to the variant or result. |
| tautology_risk_type | string | Tautology risk type assigned to the variant or result. |
| construction_variant_id | string | Phase construction variant identifier. |
| ablated_component | string | Component removed for ablation, if any. |
| shuffled_component | string | Component shuffled or permuted, if any. |
| blind_field_removed | string | Family or label-like field removed for blindness audit. |
| threshold_variant_id | string | Threshold and weight sweep variant identifier. |
| cyclic_acceptance_distance_threshold | float | Cyclic acceptance threshold used for the variant. |
| cyclic_phase_weight | float | Cyclic phase distance weight used for the variant. |
| profile_distance_weight | float | Profile distance weight used for the variant. |
| case_count | integer | Number of cases included in the variant. |
| phase_source_label | string | Source label for the exposed synthetic phase layer. |
| phase_exposure_mode | string | Exposure mode used for the phase layer. |
| phase_construction_rule | string | Deterministic construction rule used for phase-like fields. |
| phase_is_synthetic_diagnostic | boolean | True when phase fields are diagnostic synthetic fields. |
| phase_is_physical | boolean | False for all D1l audit variants. |
| false_accept_warning_exposed_count | integer | Exposed-phase false-accept warning count under the variant. |
| exclusion_success_exposed_rate | float | Exposed-phase exclusion success rate under the variant. |
| stable_candidate_exposed_count | integer | Stable candidate count under the variant. |
| fragile_candidate_exposed_count | integer | Fragile candidate count under the variant. |
| stable_candidate_loss_rate_exposed | float | Current-stable candidate loss rate under the variant. |
| exposed_phase_overstrictness_warning_count | integer | Overstrictness warning count under the variant. |
| remaining_intrusion_warning_count | integer | Remaining intrusion warning count under the variant. |
| spectrum_matched_null_intrusion_count | integer | Spectrum-matched null intrusion count under the variant. |
| adversarial_near_duplicate_intrusion_count | integer | Adversarial near-duplicate intrusion count under the variant. |
| kernel_size_8_artifact_warning_count | integer | Kernel size 8 artifact warning count under the variant. |
| proxy_vs_exposed_phase_mismatch_count | integer | Number of proxy-vs-exposed mismatch cases. |
| proxy_vs_exposed_phase_mismatch_rate | float | Rate of proxy-vs-exposed mismatch cases. |
| survives_ablation | boolean | Whether the effect survives component ablation. |
| survives_shuffle | boolean | Whether the effect survives shuffled-input tests. |
| survives_family_blindness | boolean | Whether the effect survives family-blind construction. |
| leakage_warning | boolean | Whether a leakage warning is raised. |
| tautology_warning | boolean | Whether a tautology warning is raised. |
| construction_dependence_warning | boolean | Whether a construction-dependence warning is raised. |
| overclean_result_warning | boolean | Whether the result remains suspiciously all-clean. |
| decision_status | string | Cautious decision label for the variant. |
| warning_flags | string | Delimited warning flags. |
| interpretation_note | string | Short diagnostic interpretation note. |

## 21. Acceptance criteria for later implementation

A later D1l implementation should verify at least:

- YAML config parses
- runner reads D1k outputs and D1h baseline
- runner does not modify D1f/D1h/D1i/D1j/D1k outputs
- runner does not rerun D1f
- leakage taxonomy is machine-readable
- construction variants run
- component ablations run
- shuffled-input variants run
- family-blind variants run
- threshold/weight sweeps run
- proxy-vs-exposed mismatch cases are localized
- D1k all-clean baseline is explicitly compared to audit variants
- Mastermind status remains `parked_not_implemented`
- `specificity_established` remains false
- no decision label claims proof
- readout separates Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary
- claim-risk grep is clean or only has negated Claim Boundary mentions
- `git diff --check` passes

## 22. Interpretation rules

Befund:
Which leakage, tautology, and construction-dependence warnings appear?

Interpretation:
Does the exposed phase layer retain diagnostic separation when decision-driving components are ablated, shuffled, blinded, or reconstructed differently?

Hypothese:
If the exposed phase survives hostile audits, it may become a stronger synthetic diagnostic coordinate candidate. If not, it should be treated as a useful but construction-dependent diagnostic classifier layer.

Offene Luecke:
No physical validation, no real data, no specificity, no physical phase reconstruction, no physical manifold, no Lorentzian structure, no physical time, no Pauli claim.

## 23. Decision logic

Planned cautious labels:

- leakage_audit_supported_candidate
- direct_feature_leakage_warning
- label_leakage_warning
- proxy_leakage_warning
- target_family_leakage_warning
- threshold_leakage_warning
- construction_feedback_leakage_warning
- tautology_warning
- overclean_result_warning
- construction_dependence_warning
- component_ablation_failure_warning
- shuffled_input_failure_warning
- family_blind_failure_warning
- decoy_blind_supported_candidate
- null_family_blind_supported_candidate
- stable_retention_supported_candidate
- exposed_phase_survives_hostile_controls_candidate
- exposed_phase_fails_hostile_controls_warning
- mastermind_parked_not_implemented
- inconclusive
- failed_input_consistency_check

No label may claim proof, proven status, validation, physical identity, or specificity established.

## 24. What this plan must not do

- does not implement the D1l runner
- does not rerun D1f
- does not modify D1f/D1h/D1i/D1j/D1k outputs
- does not create config files
- does not create run outputs
- does not claim exposed synthetic phase fields are physical phase
- does not claim physical phase reconstruction
- does not introduce a physical manifold
- does not interpret a cylindrical diagnostic coordinate space as physical spacetime
- does not claim Hilbert-space reconstruction
- does not claim phase-space physics
- does not attach D(A,B)
- does not construct S_rel2
- does not introduce tau as physical time
- does not derive proper time
- does not derive a Lorentzian metric
- does not validate the physical Bridge
- does not claim physical wavefunctions
- does not establish diagnostic specificity
- does not claim fermionic Pauli exclusion
- does not invoke spin-statistics
- does not claim cosmological redshift
- does not create matter particles
- does not implement Mastermind / Knuth / role-permutation yet

## 25. Claim Boundary

D1l is a synthetic phase leakage and tautology audit planning document.

D1l plans to audit whether the D1k exposed synthetic phase layer contains leakage, tautology, construction-dependence, or overfit-like behavior.

D1l does not rerun D1f.

D1l does not modify D1f, D1h, D1i, D1j, or D1k outputs.

D1l does not introduce a new identity score.

D1l does not establish diagnostic specificity.

The D1k exposed phase-like fields are diagnostic synthetic fields.

They are not physical phase reconstruction.

phase_is_physical remains false.

Cyclic-coordinate and cylindrical language denotes a diagnostic coordinate model.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

The cylindrical picture is a methodological representation of periodic phase-like structure plus nonperiodic diagnostic coordinates.

psi is a diagnostic pattern object here, not automatically a physical wavefunction.

wave_identity_profile is a diagnostic profile concept, not a proof of physical identity.

false_accept_region is a diagnostic acceptance-region concept, not a physical region.

impostor_distribution_overlap is a diagnostic distribution-overlap concept, not a physical particle population.

Decision tables are transparent methodological classification rules, not physical laws.

The orchestration metaphor is an internal explanatory image, not a physical mechanism claim.

The D1l plan does not prove wave identity.

The D1l plan does not validate physical phase reconstruction.

The all-clean D1k result requires leakage, tautology, and construction-dependence audit.

wave-Pauli is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

type-like similarity is not the same as relational identity.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1l does not attach D(A,B).

COMP01-D1l does not construct S_rel2.

COMP01-D1l does not derive a Lorentzian metric.

COMP01-D1l does not validate a physical Bridge.

COMP01-D1l does not establish diagnostic specificity.

This is synthetic diagnostic phase leakage and tautology audit planning only.

## 26. Current status label

current_status_label: COMP01D1L_synthetic_phase_leakage_tautology_audit_plan_created
