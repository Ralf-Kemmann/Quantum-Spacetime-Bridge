# QSB-ST-COMP01-D1i Cyclic-Phase Source Validation and Overstrictness Audit Plan

## 1. Purpose

COMP01-D1i is a planning block only.

D1i plans a validation of `cyclic_phase_source` and an overstrictness audit for the positive COMP01-D1h synthetic diagnostic result.

D1i does not create a scanner, config, run, or result. It does not implement a runner and does not produce new run outputs.

D1i is intended to check:

- whether `cyclic_phase_proxy` artificially creates the D1h result
- whether the warning reduction is caused by overly strict acceptance
- whether stable candidates are unnecessarily lost
- whether remaining intrusions stay systematic
- whether explicit phase-like synthetic fields are needed

## 2. Current status anchor

Current documented and implemented sequence:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented
- COMP01-D1d Manifold Degeneracy Audit implemented and result documented
- COMP01-D1e Collision-Aware Profile Runner implemented and result documented
- COMP01-D1f Robustness Sweep Runner implemented and result documented
- COMP01-D1g Warning Driver Decomposition Runner implemented and result documented
- COMP01-D1h Cyclic-Coordinate Acceptance-Region Runner implemented

Current git anchor:

- `a01c5b8 Add QSB-ST COMP01D1h cyclic-coordinate acceptance-region result note`

Minimum expected earlier anchor:

- `b73e450 Add QSB-ST COMP01D1h cyclic-coordinate acceptance-region runner`

D1h baseline values used by this plan:

- `case_count: 9450`
- `specificity_established: false`
- `cyclic_phase_source: cyclic_phase_proxy`
- `current_false_accept_warning_count: 4901`
- `cyclic_false_accept_warning_count: 992`
- `exclusion_success_count: 4750`
- `exclusion_failure_count: 151`
- `exclusion_success_rate: 0.9691899612324015`
- `stable_candidate_current_count: 2067`
- `stable_candidate_cyclic_count: 7907`
- `fragile_candidate_current_count: 7383`
- `fragile_candidate_cyclic_count: 1543`
- `mean_warning_count_current: 2.866243386243386`
- `mean_warning_count_cyclic: 0.3453968253968254`
- `mean_warning_delta_current_to_cyclic: -2.520846560846561`

Additional D1h guardrail and diagnostic context:

- `does_not_rerun_d1f: true`
- `does_not_modify_d1g_outputs: true`
- `does_not_introduce_physical_manifold: true`
- `does_not_introduce_new_identity_score: true`
- `input_consistency_passed: true`
- `cyclic_acceptance_region_member_count: 1858`
- `impostor_overlap_warning_count: 1431`
- `spectrum_matched_null_intrusion_count: 141`
- `adversarial_near_duplicate_intrusion_count: 106`
- `local_response_dominant_warning_count: 146`
- `cosmetic_penalty_lock_warning_count: 104`
- `kernel_size_8_artifact_warning_count: 344`
- `exclusion_failure_rate: 0.030810038767598448`
- `mean_cyclic_acceptance_distance: 0.3438512101215752`

## 3. Motivation from D1h

D1h strongly reduced false-accept and fragile-case warnings under a cyclic-coordinate acceptance-region layer.

However, D1h used `cyclic_phase_proxy`.

Therefore, the positive D1h result must be audited before it can be treated as robust evidence for cyclic-coordinate geometry.

D1i must determine whether D1h's improvement is geometry-driven, proxy-driven, threshold-driven, or overstrictness-driven.

The current interpretation remains bounded: D1h provides a positive synthetic diagnostic result while specificity remains false and the cyclic phase source is diagnostic/proxy-based.

## 4. Central question

Ist die D1h-Reduktion der False-Accept-Warnungen ein echter cyclic-coordinate-Geometriegewinn, oder entsteht sie durch Proxy-Konstruktion, Overstrictness oder Schwellenartefakte?

Does the D1h cyclic-coordinate layer reduce false-accept warnings because it captures useful phase-like geometry, or because the proxy and thresholds overfilter the case space?

## 5. Why D1h must be audited before claim escalation

- D1h is positive but proxy-based.
- `cyclic_phase_proxy` is not physical phase.
- `cyclic_phase_proxy` is not transparent phase reconstruction.
- Large warning reduction could indicate useful geometry.
- Large warning reduction could also indicate overstrict filtering.
- `stable_candidate_cyclic_count` increased strongly, but this needs interpretation.
- `exclusion_success_rate` is high, but exclusion failure and overstrictness cases remain.
- No specificity has been established.

## 6. Cyclic-phase source validation

D1i should plan phase-source validation along three axes.

A. Existing proxy source:

- `cyclic_phase_proxy`
- deterministic hash-based or diagnostic proxy construction
- no physical phase claim

B. Possible explicit synthetic phase source:

- if synthetic generator can expose phase-like fields
- `phi`
- `phase_override`
- `wrapped_delta_phi_abs`
- `cos_delta_phi`
- `sin_delta_phi`
- `angular_phase_distance`

C. Cross-source comparison:

- proxy vs explicit phase-like fields
- proxy vs angular component if available
- proxy vs cos/sin embedding
- proxy vs wrapped angular distance

D1i should plan whether a future D1h-like run can be repeated with explicit phase-like synthetic fields instead of proxy-only.

## 7. Proxy-dependence audit

D1i should plan a proxy-dependence audit that reruns the cyclic logic with multiple deterministic proxy variants, without rerunning D1f and without modifying D1g or D1h outputs.

The audit should compare:

- warning reduction stability
- stable/fragile split stability
- `exclusion_success_rate` stability
- `spectrum_matched_null` intrusion stability
- `adversarial_near_duplicate` intrusion stability
- `kernel_size_8` artifact stability

Planned proxy variants:

- `proxy_hash_phase_v1`
- `proxy_distance_modulated_v1`
- `proxy_decoy_family_modulated_v1`
- `proxy_null_family_modulated_v1`
- `proxy_random_seeded_control_v1`
- `explicit_phase_if_available`

If results vary strongly across proxy variants, D1h is not yet robust.

## 8. Overstrictness audit

D1i should plan an overstrictness audit to test whether D1h reduces false accepts by excluding too many cases.

Planned metrics:

- `cyclic_region_overstrict_warning_count`
- `stable_candidate_loss_count`
- `stable_candidate_loss_rate`
- `current_stable_to_cyclic_fragile_count`
- `current_fragile_to_cyclic_stable_count`
- `exclusion_success_count`
- `exclusion_failure_count`
- `exclusion_success_rate`
- `exclusion_failure_rate`
- `retained_stable_candidate_count`
- `retained_stable_candidate_rate`

Overstrictness means the method may reduce warnings by rejecting too broadly rather than by improving diagnostic separation.

## 9. Stable-candidate loss and retention audit

D1i should plan a D1g/D1h comparison of stable and fragile candidate movement.

Fields to compare:

- `stable_candidate_current_count`
- `stable_candidate_cyclic_count`
- `fragile_candidate_current_count`
- `fragile_candidate_cyclic_count`
- `current_stable_and_cyclic_stable`
- `current_stable_but_cyclic_fragile`
- `current_fragile_but_cyclic_stable`
- `current_fragile_and_cyclic_fragile`

`current_stable_but_cyclic_fragile` cases are important overstrictness candidates.

`current_fragile_but_cyclic_stable` cases require inspection because they may be true exclusions or false relaxations.

## 10. Remaining intrusion analysis

D1i should plan analysis of the D1h remaining warning and intrusion groups:

- `spectrum_matched_null_intrusion_count: 141`
- `adversarial_near_duplicate_intrusion_count: 106`
- `local_response_dominant_warning_count: 146`
- `cosmetic_penalty_lock_warning_count: 104`
- `kernel_size_8_artifact_warning_count: 344`
- `exclusion_failure_count: 151`
- `impostor_overlap_warning_count: 1431`

D1i should inspect whether remaining intrusions share common cyclic distance bands, decoy families, null families, kernel sizes, or profile/penalty settings.

## 11. Threshold sensitivity plan

D1i should plan threshold variation around the D1h baseline:

- `cyclic_acceptance_distance_threshold`: lower, baseline, higher
- `cyclic_phase_small`: lower, baseline, higher
- `profile_distance_low`: lower, baseline, higher
- `penalty_gap_positive_threshold`: lower, baseline, higher
- `overstrict_stable_loss_rate_threshold`: lower, baseline, higher

If the positive D1h result only holds for one narrow threshold setting, robustness remains weak.

## 12. Phase-field exposure plan

D1i should plan a later implementation check for whether the D1f/D1h synthetic generator can expose explicit phase-like fields.

Possible fields:

- `phi_i`
- `phi_j`
- `delta_phi_wrapped`
- `wrapped_delta_phi_abs`
- `cos_delta_phi`
- `sin_delta_phi`
- `angular_phase_profile`
- `phase_source_label`

No existing D1f or D1h file should be changed by this plan.

This is only planning for later D1i/D1j-like runs.

## 13. Comparison against D1h baseline

D1i should later compare its audit outputs against the D1h baseline.

D1h baseline:

- `cyclic_phase_source: cyclic_phase_proxy`
- `current_false_accept_warning_count: 4901`
- `cyclic_false_accept_warning_count: 992`
- `exclusion_success_rate: 0.9691899612324015`
- `exclusion_failure_rate: 0.030810038767598448`
- `stable_candidate_cyclic_count: 7907`
- `fragile_candidate_cyclic_count: 1543`
- `mean_warning_delta_current_to_cyclic: -2.520846560846561`

D1i should later check:

- Does the reduction persist under proxy variants?
- Does the reduction persist under threshold variants?
- Does the reduction persist with explicit phase fields?
- How high is overstrictness?
- Which remaining intrusions persist?

## 14. Planned implementation design

Later implementation should:

- read D1h `cyclic_region_case_summary.csv`
- read D1h `summary.json`
- optionally read D1f `case_profile_summary.csv`
- optionally read D1g `decision_table_case_classification.csv`
- do not rerun D1f
- do not modify D1h/D1g outputs
- create audit summaries only
- compare baseline proxy to proxy variants / explicit phase if available
- report overstrictness and remaining intrusion patterns

## 15. Planned output files for later implementation

Planned files for a later implementation only. This D1i plan does not create them:

- `data/qsb_st_comp01d1i_cyclic_phase_source_validation_overstrictness_config.yaml`
- `scripts/run_qsb_st_comp01d1i_cyclic_phase_source_validation_overstrictness_audit.py`
- `docs/QSB_ST_COMP01D1I_CYCLIC_PHASE_SOURCE_VALIDATION_OVERSTRICTNESS_AUDIT_RESULT_NOTE_TEMPLATE.md`

Planned later run outputs only. This D1i plan does not create them:

- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/summary.json`
- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/readout.md`
- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/proxy_variant_summary.csv`
- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/threshold_sensitivity_summary.csv`
- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/stable_retention_summary.csv`
- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/remaining_intrusion_summary.csv`
- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/phase_source_comparison_summary.csv`
- `runs/QSB-ST-COMP01D1I/cyclic_phase_source_validation_overstrictness_audit_open/resolved_config.json`

## 16. Continuous field list

| field name | field type | field description |
| --- | --- | --- |
| `run_id` | string | Identifier for the later audit run. |
| `audit_id` | string | Identifier for the D1i audit block or audit variant. |
| `phase_source_label` | string | Phase-source label used by the audit case or variant. |
| `proxy_variant_id` | string | Proxy variant identifier, such as `proxy_hash_phase_v1`. |
| `threshold_variant_id` | string | Threshold variant identifier, such as lower, baseline, or higher. |
| `case_id` | string | Case identifier inherited from D1h/D1g/D1f inputs. |
| `decoy_family` | string | Decoy family associated with the case. |
| `null_family` | string | Null family associated with the case. |
| `profile_weight_set_id` | string | Profile weight-set identifier used by the source case. |
| `penalty_weight_set_id` | string | Penalty weight-set identifier used by the source case. |
| `kernel_size_label` | string | Kernel-size label for the source or audit classification. |
| `cyclic_phase_distance_baseline` | number | D1h baseline cyclic phase distance. |
| `cyclic_phase_distance_variant` | number | Variant cyclic phase distance under the audited source or threshold. |
| `cyclic_acceptance_distance_baseline` | number | D1h baseline cyclic acceptance distance. |
| `cyclic_acceptance_distance_variant` | number | Variant cyclic acceptance distance. |
| `current_false_accept_warning` | boolean | Current D1g/D1f false-accept warning state. |
| `cyclic_false_accept_warning_baseline` | boolean | D1h baseline cyclic false-accept warning state. |
| `cyclic_false_accept_warning_variant` | boolean | Variant cyclic false-accept warning state. |
| `exclusion_success_baseline` | boolean | D1h baseline exclusion success flag. |
| `exclusion_success_variant` | boolean | Variant exclusion success flag. |
| `exclusion_failure_baseline` | boolean | D1h baseline exclusion failure flag. |
| `exclusion_failure_variant` | boolean | Variant exclusion failure flag. |
| `stable_candidate_current` | boolean | Current D1g/D1f stable-candidate flag. |
| `stable_candidate_cyclic_baseline` | boolean | D1h baseline cyclic stable-candidate flag. |
| `stable_candidate_cyclic_variant` | boolean | Variant cyclic stable-candidate flag. |
| `fragile_candidate_current` | boolean | Current D1g/D1f fragile-candidate flag. |
| `fragile_candidate_cyclic_baseline` | boolean | D1h baseline cyclic fragile-candidate flag. |
| `fragile_candidate_cyclic_variant` | boolean | Variant cyclic fragile-candidate flag. |
| `current_stable_but_cyclic_fragile` | boolean | Flag for stable current cases that become cyclic-fragile. |
| `current_fragile_but_cyclic_stable` | boolean | Flag for fragile current cases that become cyclic-stable. |
| `overstrictness_warning` | boolean | Warning that the variant may reject too broadly. |
| `stable_candidate_loss_count` | integer | Count of current stable candidates lost under cyclic variant logic. |
| `stable_candidate_loss_rate` | number | Rate of current stable candidates lost under cyclic variant logic. |
| `retained_stable_candidate_count` | integer | Count of current stable candidates retained under cyclic variant logic. |
| `retained_stable_candidate_rate` | number | Rate of current stable candidates retained under cyclic variant logic. |
| `spectrum_matched_null_intrusion_warning` | boolean | Warning for spectrum-matched null intrusion. |
| `adversarial_near_duplicate_intrusion_warning` | boolean | Warning for adversarial near-duplicate intrusion. |
| `local_response_dominant_warning` | boolean | Warning for local-response dominance. |
| `cosmetic_penalty_lock_warning` | boolean | Warning for cosmetic penalty lock. |
| `kernel_size_8_artifact_warning` | boolean | Warning for kernel-size-8 artifact behavior. |
| `impostor_overlap_warning` | boolean | Warning for impostor distribution overlap. |
| `warning_count_baseline` | integer | D1h baseline warning count for the case or group. |
| `warning_count_variant` | integer | Variant warning count for the case or group. |
| `warning_delta_baseline_to_variant` | number | Warning-count change from D1h baseline to variant. |
| `proxy_dependence_warning` | boolean | Warning that results vary materially by proxy variant. |
| `threshold_sensitivity_warning` | boolean | Warning that results vary materially by threshold variant. |
| `phase_source_validation_status` | string | Conservative phase-source audit status. |
| `decision_status` | string | Conservative decision label for the case or group. |
| `warning_flags` | string | Delimited or structured warning flag collection. |
| `interpretation_note` | string | Human-readable interpretation note with claim boundary retained. |

## 17. Acceptance criteria for later implementation

A later D1i implementation should check at minimum:

- YAML config parses
- runner reads existing D1h `summary.json`
- runner reads existing D1h `cyclic_region_case_summary.csv`
- runner does not rerun D1f
- runner does not modify D1g/D1h outputs
- all planned outputs exist
- CSVs parse with `csv.DictReader`
- proxy variants are explicitly reported
- threshold variants are explicitly reported
- overstrictness metrics are reported
- stable retention/loss is reported
- remaining intrusion groups are reported
- `specificity_established` remains false
- no decision label claims proof
- readout separates Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary
- claim-risk grep clean or only negated/Claim Boundary mentions
- `git diff --check` passes

## 18. Interpretation rules

Befund:

Do D1h improvements persist under phase-source/proxy variants and threshold perturbations?

Interpretation:

Is the D1h effect likely geometry-driven, proxy-driven, threshold-driven, or overstrictness-driven?

Hypothese:

Could explicit phase-like fields make the cyclic-coordinate model more robust and less proxy-dependent?

Offene Lücke:

No physical validation, no real data, no specificity, no physical phase reconstruction, no physical manifold, no Lorentzian structure, no physical time, no Pauli claim.

## 19. Decision logic

Planned cautious decision labels:

- `cyclic_phase_proxy_validity_supported_candidate`
- `cyclic_phase_proxy_dependence_warning`
- `cyclic_threshold_sensitivity_warning`
- `cyclic_overstrictness_warning`
- `stable_retention_supported_candidate`
- `stable_candidate_loss_warning`
- `remaining_intrusion_warning`
- `explicit_phase_source_needed`
- `explicit_phase_source_available_candidate`
- `cyclic_geometry_effect_supported_candidate`
- `cyclic_geometry_effect_not_supported_warning`
- `inconclusive`
- `failed_input_consistency_check`

No label may claim proof, proven status, validated status, physical identity, or specificity established.

## 20. What this plan must not do

- does not implement the D1i runner
- does not rerun D1f
- does not modify D1g outputs
- does not modify D1h outputs
- does not create config files
- does not create run outputs
- does not claim `cyclic_phase_proxy` is physical phase
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

## 21. Claim Boundary

D1i is a cyclic-phase source validation and overstrictness audit planning document.

D1i audits the positive D1h synthetic diagnostic result.

D1i does not rerun D1f.

D1i does not modify D1g or D1h outputs.

D1i does not introduce a new identity score.

D1i does not establish diagnostic specificity.

cyclic_phase_proxy is diagnostic only.

cyclic_phase_proxy is not a physical phase reconstruction.

Cyclic-coordinate and cylindrical language denotes a diagnostic coordinate model.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

The cylindrical picture is a methodological representation of periodic phase-like structure plus nonperiodic diagnostic coordinates.

`psi` is a diagnostic pattern object here, not automatically a physical wavefunction.

`wave_identity_profile` is a diagnostic profile concept, not a proof of physical identity.

`false_accept_region` is a diagnostic acceptance-region concept, not a physical region.

`impostor_distribution_overlap` is a diagnostic distribution-overlap concept, not a physical particle population.

Decision tables are transparent methodological classification rules, not physical laws.

The orchestration metaphor is an internal explanatory image, not a physical mechanism claim.

The D1i plan does not prove wave identity.

The D1i plan does not validate physical phase reconstruction.

`wave-Pauli` is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

Type-like similarity is not the same as relational identity.

Spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

Phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1i does not attach D(A,B).

COMP01-D1i does not construct S_rel2.

COMP01-D1i does not derive a Lorentzian metric.

COMP01-D1i does not validate a physical Bridge.

COMP01-D1i does not establish diagnostic specificity.

This is synthetic diagnostic cyclic-phase source validation and overstrictness audit planning only.

## 22. Current status label

current_status_label: COMP01D1I_cyclic_phase_source_validation_overstrictness_audit_plan_created
