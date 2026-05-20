# QSB-ST-COMP01-D1g Warning Driver Decomposition and Failure-Mode Analysis Result Note

## 1. Purpose

This document is the result note for the D1g Warning Driver Decomposition and Failure-Mode Analysis run.

It documents an existing synthetic D1g decomposition run from:

`runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/`

This is not a new run, not a new implementation, not a new identity score, and not a re-run of D1f.

It is not a physical proof, not a positive specificity result, and not a physical manifold claim.

## 2. Current status anchor

Current chain:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented
- COMP01-D1d Manifold Degeneracy Audit implemented and result documented
- COMP01-D1e Collision-Aware Profile Runner implemented and result documented
- COMP01-D1f Robustness Sweep Runner implemented and result documented
- COMP01-D1g Warning Driver Decomposition Runner implemented

Current commit anchor:

`b026376 Add QSB-ST COMP01D1g warning driver decomposition runner`

## 3. Run inputs and generated outputs

Run directory:

`runs/QSB-ST-COMP01D1G/warning_driver_decomposition_open/`

Generated output files:

- `summary.json`
- `readout.md`
- `warning_type_summary.csv`
- `decoy_driver_summary.csv`
- `null_family_driver_summary.csv`
- `profile_weight_driver_summary.csv`
- `penalty_weight_driver_summary.csv`
- `kernel_size_driver_summary.csv`
- `interaction_driver_summary.csv`
- `stable_fragile_case_summary.csv`
- `decision_table_rules.csv`
- `decision_table_case_classification.csv`
- `resolved_config.json`

## 4. Befund

D1g decomposed the existing D1f case table.

D1g did not rerun D1f and did not introduce a new identity score.

Input consistency passed.

Summary values:

```yaml
case_count: 9450
specificity_established: false
does_not_rerun_d1f: true
does_not_introduce_new_identity_score: true
input_consistency_passed: true
stable_candidate_count: 2067
stable_candidate_rate: 0.21873015873015872
fragile_candidate_count: 7383
fragile_candidate_rate: 0.7812698412698412
top_warning_type: penalty_weight_sensitivity_warning
top_warning_count: 5859
top_warning_rate: 0.62
top_decoy_family: adversarial_near_duplicate_sweep
top_decoy_warning_rate: 0.504021164021164
top_null_family: spectrum_matched_null
top_null_overlap_rate: 0.7802840434419381
top_profile_weight_set: local_response_dominant
top_profile_weight_warning_rate: 0.2866666666666667
top_penalty_weight_set: strong_collision_penalties
top_penalty_warning_rate: 0.62
top_kernel_size_label: kernel_size_8
top_kernel_warning_rate: 0.2342857142857143
dominant_failure_mode_label: false_accept_region_overlap_driven
decision_table_rule_count: 10
decision_table_high_severity_count: 5127
decision_table_medium_severity_count: 2256
decision_table_low_severity_count: 2067
```

The dominant failure mode is `false_accept_region_overlap_driven`.

Most cases are fragile under the D1g warning table: 7383 fragile cases versus 2067 stable cases.

`specificity_established` remains false.

## 5. Interpretation

D1g decomposes the D1f warning return without introducing a new identity score.

The dominant D1g failure mode is false-accept-region overlap, not direct metric collision.

Deutsch sinngemaess:

D1g zeigt nicht einfach, dass die Metrik kollidiert, sondern dass falsche Kandidaten, Nullfamilien und Decoys in den akzeptierten Profilbereich eindringen.

The current problem is best interpreted as acceptance-region vulnerability: too many impostor/control/null cases can enter the acceptable profile region under specific decoy, weight, penalty, and kernel-size settings.

D1g does not solve the problem. It identifies likely drivers.

## 6. Hypothese

The next methodological step should focus on closing or reshaping the false-accept region, not on adding another scalar score.

Possible future directions:

- acceptance-region geometry audit
- impostor/null exclusion checks
- profile component orchestration review
- penalty effectiveness analysis
- local-response-dominant failure analysis
- spectrum-matched null intrusion analysis
- adversarial-near-duplicate stress reduction
- kernel-size-8 artifact check

This remains diagnostic and synthetic.

## 7. Offene Lücke

- no real data
- no physical validation
- no diagnostic specificity established
- no physical manifold
- no Hilbert-space reconstruction
- no robust identity metric yet
- no solved false-accept-region problem
- no physical null model
- no Lorentzian structure
- no physical time
- no physical wavefunction claim
- no Pauli or spin-statistics claim
- no Bridge validation

## 8. Warning-driver decomposition

Which families enter the acceptance region?

- `top_decoy_family: adversarial_near_duplicate_sweep`
- `top_null_family: spectrum_matched_null`

Which weightings open the door?

- `top_profile_weight_set: local_response_dominant`
- `top_profile_weight_warning_rate: 0.2866666666666667`

Which penalties close only cosmetically?

- `top_penalty_weight_set: strong_collision_penalties`
- `top_penalty_warning_rate: 0.62`

Interpretation: stronger penalties can shift distances but do not automatically close the false-accept region.

Which kernel sizes shift the acceptance region?

- `top_kernel_size_label: kernel_size_8`
- `top_kernel_warning_rate: 0.2342857142857143`

Interpretation: the small synthetic kernel condition is the most sensitive in this run.

Which decoys sound like the melody although they do not belong?

- `adversarial_near_duplicate_sweep` is the top decoy driver.
- `dominant_failure_mode_label: false_accept_region_overlap_driven`

The profile components behave like an ensemble: individual components may be meaningful, but if local response, penalties, and control response are not orchestrated robustly, impostor cases can still sound acceptable inside the current profile region.

## 9. Decision-table result

D1g used transparent decision table rules, not a blackbox classifier.

Decision table counts:

```yaml
decision_table_rule_count: 10
decision_table_high_severity_count: 5127
decision_table_medium_severity_count: 2256
decision_table_low_severity_count: 2067
```

The decision table shows many high-severity cases, indicating that the failure-mode structure is not rare under the D1f stress set.

Central rule concepts:

- `multi_driver_instability`
- `false_accept_region_warning`
- `impostor_distribution_overlap_warning`
- `representation_instability_warning`
- `coordinate_dominant_open_door_warning`
- `penalty_off_open_door_warning`
- `control_response_low_open_door_warning`
- `cosmetic_penalty_lock_warning`
- `kernel_shift_acceptance_region_warning`
- `stable_under_tested_stress_candidate`

Decision tables are transparent methodological classification rules, not physical laws.

## 10. Acceptance-region interpretation

Required diagnostic terms:

- `false_accept_region`
- `impostor_distribution_overlap`
- `representation_instability`
- `threshold_fragility`
- `open_space_risk`
- `manifold_intrusion`

The D1g result suggests that the relevant diagnostic issue is not direct collision, but too-large or poorly shaped acceptance regions.

False-accept-region overlap means that a decoy/null/control case need not be identical to a target case; it only needs to fall into the accepted diagnostic region.

## 11. Consequence for next design step

The next step should not be claim escalation and not immediate new score escalation.

Possible next block:

`QSB-ST-COMP01-D1h`

Possible title:

`Acceptance-Region Closure and Impostor-Exclusion Plan`

Possible target path:

`docs/QSB_ST_COMP01D1H_ACCEPTANCE_REGION_CLOSURE_IMPOSTOR_EXCLUSION_PLAN.md`

D1h should plan:

- acceptance-region geometry audit
- stable vs fragile region comparison
- exclusion checks for spectrum-matched nulls
- adversarial-near-duplicate exclusion logic
- local-response-dominant weight failure audit
- penalty effectiveness / cosmetic lock test
- `kernel_size_8` artifact check
- no new physical claim

## 12. Machine-readable status

```yaml
block_id: QSB-ST-COMP01D1G
run_id: warning_driver_decomposition_open
commit_anchor: b026376
case_count: 9450
specificity_established: false
does_not_rerun_d1f: true
does_not_introduce_new_identity_score: true
input_consistency_passed: true
stable_candidate_count: 2067
stable_candidate_rate: 0.21873015873015872
fragile_candidate_count: 7383
fragile_candidate_rate: 0.7812698412698412
top_warning_type: penalty_weight_sensitivity_warning
top_warning_count: 5859
top_warning_rate: 0.62
top_decoy_family: adversarial_near_duplicate_sweep
top_decoy_warning_rate: 0.504021164021164
top_null_family: spectrum_matched_null
top_null_overlap_rate: 0.7802840434419381
top_profile_weight_set: local_response_dominant
top_profile_weight_warning_rate: 0.2866666666666667
top_penalty_weight_set: strong_collision_penalties
top_penalty_warning_rate: 0.62
top_kernel_size_label: kernel_size_8
top_kernel_warning_rate: 0.2342857142857143
dominant_failure_mode_label: false_accept_region_overlap_driven
decision_table_rule_count: 10
decision_table_high_severity_count: 5127
decision_table_medium_severity_count: 2256
decision_table_low_severity_count: 2067
current_status_label: COMP01D1G_warning_driver_decomposition_failure_mode_analysis_result_documented
```

## 13. Claim Boundary

D1g is a warning-driver decomposition and failure-mode analysis result note.

D1g did not rerun D1f.

D1g did not introduce a new identity score.

Decision tables are transparent methodological classification rules, not physical laws.

The manifold language denotes a diagnostic coordinate space of synthetic wave-pattern descriptors.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

psi is a diagnostic pattern object here, not automatically a physical wavefunction.

wave_identity_profile is a diagnostic profile concept, not a proof of physical identity.

Failure-mode labels are methodological diagnostic labels, not physical categories.

false_accept_region is a diagnostic acceptance-region concept, not a physical region.

impostor_distribution_overlap is a diagnostic distribution-overlap concept, not a physical particle population.

Parameter sweeps are robustness tests, not physical parameter fitting.

Kernel-size scaling is a methodological robustness test, not a physical system-size claim.

Null families are diagnostic controls, not physical ensembles.

control mimicry warnings are methodological warnings, not failures of physics.

The D1g result does not establish diagnostic specificity.

The D1g result does not prove wave identity.

"wave-Pauli" is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

type-like similarity is not the same as relational identity.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1g does not attach D(A,B).

COMP01-D1g does not construct S_rel2.

COMP01-D1g does not derive a Lorentzian metric.

COMP01-D1g does not validate a physical Bridge.

COMP01-D1g does not establish diagnostic specificity.

This is synthetic diagnostic warning-driver decomposition result documentation only.

## 14. Current status label

current_status_label: COMP01D1G_warning_driver_decomposition_failure_mode_analysis_result_documented
