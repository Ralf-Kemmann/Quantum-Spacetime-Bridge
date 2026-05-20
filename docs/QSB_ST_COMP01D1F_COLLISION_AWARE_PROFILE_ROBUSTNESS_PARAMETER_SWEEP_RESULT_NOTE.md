# QSB-ST-COMP01-D1f Collision-Aware Profile Robustness Parameter-Sweep Result Note

## 1. Purpose

This document is the result note for the D1f Collision-Aware Profile Robustness Parameter-Sweep run.

It documents an existing synthetic robustness sweep from:

`runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/`

It does not start a new run, does not introduce a new implementation, does not create a new config, and does not change existing files.

This is not a physical validation, not a positive specificity result, not a physical manifold claim, and not physical parameter fitting.

## 2. Current status anchor

Current chain:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented
- COMP01-D1d Manifold Degeneracy Audit implemented and result documented
- COMP01-D1e Collision-Aware Profile Runner implemented and result documented
- COMP01-D1f Collision-Aware Profile Robustness Runner implemented

Current commit anchor:

`cbc9e8f Add QSB-ST COMP01D1f collision-aware profile robustness runner`

## 3. Run inputs and generated outputs

Run directory:

`runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/`

Generated output files:

- `summary.json`
- `readout.md`
- `case_profile_summary.csv`
- `profile_weight_summary.csv`
- `decoy_family_summary.csv`
- `kernel_size_summary.csv`
- `null_family_summary.csv`
- `warning_stability_summary.csv`
- `resolved_config.json`

## 4. Befund

The D1f robustness sweep completed the full planned sweep.

Summary values:

```yaml
case_count: 9450
expected_case_count: 9450
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed_all: true
warning_count_total: 32961
profile_collision_count: 0
residual_collision_count: 0
delta_vector_collision_count: 0
ambiguity_warning_count: 975
control_profile_mimicry_warnings_count: 4901
residual_matched_profile_warnings_count: 851
adversarial_profile_warnings_count: 1694
profile_weight_sensitivity_warnings_count: 2709
penalty_weight_sensitivity_warnings_count: 5859
kernel_size_sensitivity_warnings_count: 2214
null_family_overlap_warnings_count: 4901
decoy_success_warnings_count: 3956
control_overlap_warnings_count: 4901
mean_profile_distance_raw: 0.07423206485073981
mean_profile_distance_collision_penalized: 0.15990931352798848
mean_decoy_success_rate: 0.4186243386243386
mean_control_overlap_rate: 0.5186243386243387
```

Decision counts:

```yaml
decoy_success_warning: 3956
exact_duplicate_sanity_pass: 945
kernel_size_sensitivity_warning: 216
null_family_overlap_warning: 945
penalty_weight_sensitivity_warning: 591
profile_weight_sensitivity_warning: 1675
warning_reduction_stable_candidate: 1122
```

The full sweep completed: 9450 cases.

Exact duplicate sanity passed across the sweep.

`specificity_established` remains false.

Geometric collision counts remained zero for profile, residual, and delta-vector collisions.

However, broad robustness warnings returned strongly.

Control overlap, null-family overlap, decoy success, profile-weight sensitivity, penalty-weight sensitivity, and kernel-size sensitivity warnings are substantial.

## 5. Interpretation

D1f does not confirm robust D1e warning reduction.

Under broader synthetic parameter sweeps, harder decoys, profile/penalty-weight variation, kernel-size scaling, and independent null families, substantial warning counts return while `specificity_established` remains false.

Deutsch:

D1e sah im freundlichen Setup gut aus. D1f zeigt, dass dieses gute Verhalten unter breiterem Stress nicht stabil ist.

The low profile/residual/delta-vector collision counts show that the explicit collision flags did not dominate the failure mode.

The main problem is robustness instability: control overlap, decoy success, null-family overlap, and weight/kernel sensitivity.

## 6. Hypothese

The collision-aware `wave_identity_profile` may still be useful as a diagnostic stress tool, but not yet as a robust identity marker.

A later analysis should decompose which warning families drive instability:

- decoy family effects
- null family effects
- profile-weight sensitivity
- penalty-weight sensitivity
- kernel-size sensitivity
- control overlap rates

The next direction should not be new score escalation. It should be a D1g warning-decomposition and driver-analysis plan.

## 7. Offene Lücke

- no real data
- no physical validation
- no diagnostic specificity is established
- no physical manifold
- no Hilbert-space reconstruction
- no robust identity metric yet
- no stable warning reduction established
- no independent physical null model
- no Lorentzian structure
- no physical time
- no physical wavefunction claim
- no Pauli or spin-statistics claim
- no Bridge validation

## 8. Comparison to D1e

D1e reported:

```yaml
pair_count: 16
control_profile_mimicry_warnings_count: 0
residual_matched_profile_warnings_count: 0
adversarial_profile_warnings_count: 0
residual_collision_count: 2
delta_vector_collision_count: 0
specificity_established: false
```

D1f reported:

```yaml
case_count: 9450
control_profile_mimicry_warnings_count: 4901
residual_matched_profile_warnings_count: 851
adversarial_profile_warnings_count: 1694
null_family_overlap_warnings_count: 4901
decoy_success_warnings_count: 3956
specificity_established: false
```

This comparison indicates that D1e's improved warning behavior was not robust under the broader D1f synthetic stress sweep.

## 9. Warning-return analysis

The D1f warning counts return under broader synthetic stress.

Key warning-return signals:

- `control_profile_mimicry_warnings_count: 4901` indicates broad control overlap risk.
- `null_family_overlap_warnings_count: 4901` indicates that independent null families often enter the near-duplicate / control-overlap region.
- `decoy_success_warnings_count: 3956` indicates substantial decoy vulnerability.
- `penalty_weight_sensitivity_warnings_count: 5859` indicates that penalty-weight choices strongly affect outcomes.
- `profile_weight_sensitivity_warnings_count: 2709` indicates that profile-component weighting matters.
- `kernel_size_sensitivity_warnings_count: 2214` indicates nontrivial synthetic kernel-size dependence.

The main D1f signal is not classical collision failure, but robustness failure under broader synthetic stress.

## 10. Consequence for next design step

The next step should not be claim escalation.

The next step should be a warning-decomposition / driver-analysis plan.

Possible next block:

`QSB-ST-COMP01-D1g`

Possible title:

`Warning Driver Decomposition and Failure-Mode Analysis Plan`

Possible target path:

`docs/QSB_ST_COMP01D1G_WARNING_DRIVER_DECOMPOSITION_FAILURE_MODE_ANALYSIS_PLAN.md`

D1g should plan:

- identify dominant warning-driving decoy families
- identify dominant null-family overlaps
- compare `profile_weight_set` sensitivity
- compare `penalty_weight_set` sensitivity
- inspect kernel-size sensitivity
- inspect which cases remain stable candidates
- separate true improvement from friendly-configuration artifacts

## 11. Machine-readable status

```yaml
block_id: QSB-ST-COMP01D1F
run_id: collision_aware_profile_robustness_sweep_open
commit_anchor: cbc9e8f
case_count: 9450
expected_case_count: 9450
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed_all: true
warning_count_total: 32961
profile_collision_count: 0
residual_collision_count: 0
delta_vector_collision_count: 0
ambiguity_warning_count: 975
control_profile_mimicry_warnings_count: 4901
residual_matched_profile_warnings_count: 851
adversarial_profile_warnings_count: 1694
profile_weight_sensitivity_warnings_count: 2709
penalty_weight_sensitivity_warnings_count: 5859
kernel_size_sensitivity_warnings_count: 2214
null_family_overlap_warnings_count: 4901
decoy_success_warnings_count: 3956
control_overlap_warnings_count: 4901
mean_profile_distance_raw: 0.07423206485073981
mean_profile_distance_collision_penalized: 0.15990931352798848
mean_decoy_success_rate: 0.4186243386243386
mean_control_overlap_rate: 0.5186243386243387
current_status_label: COMP01D1F_collision_aware_profile_robustness_parameter_sweep_result_documented
```

## 12. Claim Boundary

The manifold language denotes a diagnostic coordinate space of synthetic wave-pattern descriptors.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

`psi` is a diagnostic pattern object here, not automatically a physical wavefunction.

`wave_identity_profile` is a diagnostic profile concept, not a proof of physical identity.

Collision-aware profile distance is a methodological diagnostic construct, not a physical distance.

collision penalties are methodological warning terms, not physical forces or interactions.

Parameter sweeps are robustness tests, not physical parameter fitting.

Kernel-size scaling is a methodological robustness test, not a physical system-size claim.

Null families are diagnostic controls, not physical ensembles.

control mimicry warnings are methodological warnings, not failures of physics.

The D1f result does not establish diagnostic specificity.

The D1f result does not prove wave identity.

The D1f result does not confirm robust D1e warning reduction.

“wave-Pauli” is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

type-like similarity is not the same as relational identity.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1f does not attach `D(A,B)`.

COMP01-D1f does not construct `S_rel2`.

COMP01-D1f does not derive a Lorentzian metric.

COMP01-D1f does not validate a physical Bridge.

COMP01-D1f does not establish diagnostic specificity.

This is synthetic diagnostic collision-aware profile robustness result documentation only.

## 13. Current status label

current_status_label: COMP01D1F_collision_aware_profile_robustness_parameter_sweep_result_documented
