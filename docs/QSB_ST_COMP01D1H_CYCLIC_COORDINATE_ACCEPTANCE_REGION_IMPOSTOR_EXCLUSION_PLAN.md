# QSB-ST-COMP01-D1h Cyclic-Coordinate Acceptance-Region and Impostor-Exclusion Plan

## 1. Purpose

COMP01-D1h is a planning block only.

D1h plans a test of whether a cyclic-coordinate / cylindrical diagnostic acceptance-region model can reduce the false-accept-region overlap vulnerability identified by D1g.

D1h does not create a scanner, does not create a config, does not create runs, and does not create results.

D1h does not build a new identity score.

D1h plans an alternative diagnostic geometry for the acceptance region.

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

D1g reference values:

```yaml
case_count: 9450
specificity_established: false
does_not_rerun_d1f: true
does_not_introduce_new_identity_score: true
input_consistency_passed: true
stable_candidate_count: 2067
fragile_candidate_count: 7383
top_warning_type: penalty_weight_sensitivity_warning
top_decoy_family: adversarial_near_duplicate_sweep
top_null_family: spectrum_matched_null
top_profile_weight_set: local_response_dominant
top_penalty_weight_set: strong_collision_penalties
top_kernel_size_label: kernel_size_8
dominant_failure_mode_label: false_accept_region_overlap_driven
```

## 3. Motivation from D1g

D1g identified false-accept-region overlap as the dominant failure mode.

D1g indicates that the issue is not direct metric collision alone, but too many adversarial, null, or control cases entering the accepted diagnostic region.

This motivates testing whether the acceptance region itself should be described in a cyclic-coordinate / cylindrical diagnostic geometry.

## 4. Central question

Kann eine zyklisch/zylindrisch gedachte diagnostische Akzeptanzregion false-accept overlap besser reduzieren als die bisherige gemischte Profilraum-Interpretation?

English formulation:

Does treating phase-sensitive wave-identity profiles as a cyclic-coordinate acceptance region reduce false-accept overlap compared with the current mixed linear/profile interpretation?

## 5. Why cyclic-coordinate geometry is worth testing

- Phase-like coordinates are periodic.
- Treating periodic phase as a naive linear coordinate can distort distances near wrap boundaries.
- A cyclic coordinate can be represented by `cos(phi)`, `sin(phi)`, or wrapped angular distance.
- Other coordinates such as `k`, `A`, `B`, `R`, `slope`, `intercept`, local response, and residual features remain nonperiodic or derived.
- The natural diagnostic geometry may therefore be product-like: cyclic phase direction x linear/derived feature axes.
- This is heuristically cylindrical: S¹ × R^n.
- This is a diagnostic coordinate model, not a physical manifold claim.

## 6. Diagnostic cylindrical coordinate-space concept

Planned `cyclic_axis` components:

- `phi_wrapped`
- `wrapped_delta_phi_abs`
- `cos_delta_phi`
- `sin_delta_phi`
- `angular_phase_profile`

Planned `linear_axes` components:

- `k`
- `A`
- `B`
- `R`
- `slope`
- `intercept`
- `local_response_norm`
- `normalized_amplitude_balance`

Planned `derived_axes` components:

- `slope = B*k`
- `R = sqrt(A^2 + B^2)`
- `local_response_norm`
- `residual_weight_profile`
- `rank_stability_profile`

Planned `decision_axes` components:

- warning flags
- decision-table labels
- `false_accept_region` warning
- impostor overlap warning
- stable/fragile classification

D1h must not claim that these axes are complete or physically fundamental.

## 7. Acceptance-region geometry

Planned comparison:

A. `current_profile_region`:

- existing D1f/D1g profile interpretation
- `profile_distance_raw`
- `profile_distance_collision_penalized`
- decision-table labels

B. `cyclic_coordinate_region`:

- angular distance handled separately
- phase wrap respected
- cyclic contribution not double-counted with linear phase proxies
- acceptance region evaluated as combined cyclic + linear + decision-table space

C. `cylindrical_acceptance_region`:

- `cyclic_phase_band`
- `spectral_band`
- `local_response_band`
- `residual_band`
- `control_exclusion_band`
- `decision_table_exclusion_rule`

Acceptance-region geometry is diagnostic and synthetic.

## 8. Impostor-exclusion logic

Planned exclusion checks:

- `spectrum_matched_null_exclusion_check`
- `adversarial_near_duplicate_exclusion_check`
- `local_response_dominant_exclusion_check`
- `strong_collision_penalty_cosmetic_lock_check`
- `kernel_size_8_artifact_check`
- `false_accept_region_overlap_check`
- `impostor_distribution_overlap_check`

D1h must not simply assert hard thresholds. Thresholds must later be transparent config fields.

## 9. Decision-table orchestration

The D1g decision tables should continue to be used, but they should be extended with cyclic-coordinate awareness.

Example rules for later implementation:

```text
IF cyclic angular distance is small
AND linear spectral/local distance is small
AND null/control overlap warning true
THEN cyclic_false_accept_warning

IF angular match is good
AND local_response_dominant
AND adversarial_near_duplicate_sweep
THEN melody_like_impostor_warning

IF phase wraps across boundary
AND linear distance appears large
THEN phase_wrap_distance_warning

IF strong_collision_penalties increase distance
BUT decision_table false_accept warning remains
THEN cosmetic_penalty_lock_warning
```

Decision tables remain transparent methodological classification rules, not physical laws.

## 10. Comparison against current D1g/D1f interpretation

D1f baseline:

```yaml
warning_count_total: 32961
control_profile_mimicry_warnings_count: 4901
null_family_overlap_warnings_count: 4901
decoy_success_warnings_count: 3956
penalty_weight_sensitivity_warnings_count: 5859
kernel_size_sensitivity_warnings_count: 2214
```

D1g decomposition:

```yaml
dominant_failure_mode_label: false_accept_region_overlap_driven
top_decoy_family: adversarial_near_duplicate_sweep
top_null_family: spectrum_matched_null
top_profile_weight_set: local_response_dominant
top_penalty_weight_set: strong_collision_penalties
top_kernel_size_label: kernel_size_8
```

D1h later test should compare whether cyclic-coordinate acceptance logic reduces:

- `false_accept_region` warnings
- impostor overlap warnings
- spectrum-matched null overlap
- adversarial near-duplicate success
- local-response-dominant open-door behavior
- cosmetic penalty lock behavior
- `kernel_size_8` sensitivity

A reduction would be methodological only, not a physical validation.

## 11. Planned implementation design

D1h should later implement an analysis layer that reads existing D1f/D1g outputs and produces an alternative acceptance-region classification.

Important constraints:

- D1h should not rerun D1f.
- D1h should not change D1g outputs.
- D1h should read existing D1f/D1g case classifications.
- D1h should add a cyclic-coordinate acceptance-region analysis layer.

## 12. Planned output files for later implementation

Planned repo files for later implementation only:

- `data/qsb_st_comp01d1h_cyclic_coordinate_acceptance_region_config.yaml`
- `scripts/run_qsb_st_comp01d1h_cyclic_coordinate_acceptance_region.py`
- `docs/QSB_ST_COMP01D1H_CYCLIC_COORDINATE_ACCEPTANCE_REGION_IMPOSTOR_EXCLUSION_RESULT_NOTE_TEMPLATE.md`

Planned later run outputs:

- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/summary.json`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/readout.md`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/cyclic_region_case_summary.csv`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/cyclic_vs_current_region_summary.csv`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/impostor_exclusion_summary.csv`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/decision_table_cyclic_summary.csv`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/kernel_size_cyclic_sensitivity_summary.csv`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/resolved_config.json`

## 13. Continuous field list

| field name | field type | field description |
| --- | --- | --- |
| `run_id` | string | D1h run identifier. |
| `case_id` | string | Case identifier inherited from D1f/D1g case tables. |
| `decoy_family` | string | Decoy family associated with the case. |
| `null_family` | string | Null family associated with the case. |
| `profile_weight_set_id` | string | Profile-weight setting inherited from D1f. |
| `penalty_weight_set_id` | string | Penalty-weight setting inherited from D1f. |
| `kernel_size_label` | string | Synthetic kernel-size label. |
| `current_decision_table_label` | string | D1g decision-table label. |
| `current_failure_mode_label` | string | D1g failure-mode label. |
| `cyclic_phase_distance` | float | Phase-aware cyclic distance. |
| `cyclic_phase_band` | string | Configured cyclic phase band. |
| `cyclic_region_label` | string | Label for the cyclic-coordinate region. |
| `cylindrical_region_label` | string | Label for the combined cyclic + linear diagnostic region. |
| `cyclic_linear_balance` | float | Relative balance between cyclic and linear contributions. |
| `profile_distance_raw` | float | Existing D1f raw profile distance. |
| `profile_distance_collision_penalized` | float | Existing D1f collision-penalized profile distance. |
| `cyclic_acceptance_distance` | float | Planned diagnostic distance under cyclic-region logic. |
| `cyclic_acceptance_region_member` | boolean | Whether the case lies inside the cyclic acceptance region. |
| `current_false_accept_warning` | boolean | Whether the current D1g/D1f logic flags false accept behavior. |
| `cyclic_false_accept_warning` | boolean | Whether cyclic-region logic flags false accept behavior. |
| `impostor_overlap_warning` | boolean | Diagnostic impostor-overlap warning. |
| `spectrum_matched_null_exclusion_warning` | boolean | Spectrum-matched null intrusion/exclusion warning. |
| `adversarial_near_duplicate_exclusion_warning` | boolean | Adversarial near-duplicate intrusion/exclusion warning. |
| `local_response_dominant_exclusion_warning` | boolean | Local-response-dominant open-door warning. |
| `cosmetic_penalty_lock_warning` | boolean | Penalty increased distance but did not remove overlap. |
| `kernel_size_8_artifact_warning` | boolean | Synthetic kernel-size-8 artifact warning. |
| `phase_wrap_distance_warning` | boolean | Warning for wrap-boundary distance distortion. |
| `stable_candidate_current` | boolean | Current D1g stable candidate status. |
| `stable_candidate_cyclic` | boolean | Planned cyclic-region stable candidate status. |
| `fragile_candidate_current` | boolean | Current D1g fragile candidate status. |
| `fragile_candidate_cyclic` | boolean | Planned cyclic-region fragile candidate status. |
| `warning_count_current` | integer | Current warning count. |
| `warning_count_cyclic` | integer | Planned cyclic-region warning count. |
| `warning_delta_current_to_cyclic` | integer | Difference between current and cyclic warning counts. |
| `exclusion_success_flag` | boolean | Whether cyclic logic excludes a targeted impostor class. |
| `exclusion_failure_flag` | boolean | Whether cyclic logic fails to exclude a targeted impostor class. |
| `decision_status` | string | Defensive diagnostic decision label. |
| `warning_flags` | string | Semicolon-delimited warning flags. |
| `interpretation_note` | string | Defensive interpretation note. |

## 14. Acceptance criteria for later implementation

Later implementation should verify at least:

- YAML config parses
- runner reads existing D1f/D1g outputs
- runner does not rerun D1f
- runner does not modify D1g outputs
- all planned outputs exist
- CSVs parse with `csv.DictReader`
- cyclic phase distance is explicitly reported
- phase wrap handling is explicit
- current vs cyclic warning counts are compared
- spectrum-matched null overlap is explicitly tested
- adversarial-near-duplicate success is explicitly tested
- local-response-dominant behavior is explicitly tested
- penalty cosmetic lock behavior is explicitly tested
- `kernel_size_8` sensitivity is explicitly tested
- `specificity_established` remains false
- no decision label claims proof
- readout separates Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary
- claim-risk grep is clean or only negated/Claim Boundary mentions
- `git diff --check` passes

## 15. Interpretation rules

Befund:

Does cyclic-coordinate acceptance-region logic reduce false-accept overlap compared with current D1g labels?

Interpretation:

If warning counts decrease, does this reflect better diagnostic exclusion or merely stricter thresholds?

Hypothese:

Could cyclic-coordinate geometry become a better acceptance-region model for phase-sensitive wave fingerprints?

Offene Luecke:

No physical validation, no real data, no specificity, no physical manifold, no Lorentzian structure, no physical time, no Pauli claim.

## 16. Decision logic

Planned defensive labels:

- `cyclic_region_reduces_false_accept_candidate`
- `cyclic_region_no_improvement_warning`
- `cyclic_region_overstrict_warning`
- `cyclic_false_accept_warning`
- `phase_wrap_distance_warning`
- `spectrum_matched_null_intrusion_warning`
- `adversarial_near_duplicate_intrusion_warning`
- `local_response_open_door_warning`
- `cosmetic_penalty_lock_warning`
- `kernel_size_8_artifact_warning`
- `stable_under_cyclic_region_candidate`
- `fragile_under_cyclic_region`
- `inconclusive`
- `failed_input_consistency_check`

No label may claim proof, proven status, validation, physical identity, or specificity established.

## 17. What this plan must not do

- does not implement the D1h runner
- does not rerun D1f
- does not change D1g outputs
- does not create config files
- does not create run outputs
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

## 18. Claim Boundary

D1h is a cyclic-coordinate acceptance-region and impostor-exclusion planning document.

Cyclic-coordinate and cylindrical language denotes a diagnostic coordinate model.

It is not a physical spacetime manifold.

It is not a Hilbert-space reconstruction.

It is not a Lorentzian geometry.

It is not a physical phase space.

The cylindrical picture is a methodological representation of periodic phase plus nonperiodic diagnostic coordinates.

psi is a diagnostic pattern object here, not automatically a physical wavefunction.

wave_identity_profile is a diagnostic profile concept, not a proof of physical identity.

false_accept_region is a diagnostic acceptance-region concept, not a physical region.

impostor_distribution_overlap is a diagnostic distribution-overlap concept, not a physical particle population.

Decision tables are transparent methodological classification rules, not physical laws.

The orchestration metaphor is an internal explanatory image, not a physical mechanism claim.

The D1h plan does not establish diagnostic specificity.

The D1h plan does not prove wave identity.

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

COMP01-D1h does not attach D(A,B).

COMP01-D1h does not construct S_rel2.

COMP01-D1h does not derive a Lorentzian metric.

COMP01-D1h does not validate a physical Bridge.

COMP01-D1h does not establish diagnostic specificity.

This is synthetic diagnostic cyclic-coordinate acceptance-region planning only.

## 19. Current status label

current_status_label: COMP01D1H_cyclic_coordinate_acceptance_region_impostor_exclusion_plan_created
