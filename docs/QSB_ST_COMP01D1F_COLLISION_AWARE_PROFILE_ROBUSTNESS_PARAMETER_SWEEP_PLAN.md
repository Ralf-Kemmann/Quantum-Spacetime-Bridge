# QSB-ST-COMP01-D1f Collision-Aware Profile Robustness and Parameter-Sweep Plan

## 1. Purpose

COMP01-D1f is a planning block only.

D1f plans robustness and parameter-sweep tests for the D1e collision-aware `wave_identity_profile`.

D1f does not create a scanner, does not create a config, does not create runs, and does not create results.

Goal:

Test whether the reduced warning situation from D1e remains stable when parameters are spread more broadly, decoys are made harder, profile weights are varied, kernel sizes are compared, and independent null families are introduced.

The D1f step is deliberately a robustness-planning step, not a claim step.

## 2. Current status anchor

Current chain:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented
- COMP01-D1d Manifold Degeneracy Audit implemented and result documented
- COMP01-D1e Collision-Aware Profile Runner implemented and result documented

Current commit anchor:

`b8238c6 Add QSB-ST COMP01D1e collision-aware wave identity profile result note`

D1e result values:

```yaml
pair_count: 16
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed: true
profile_collision_count: 0
residual_collision_count: 2
delta_vector_collision_count: 0
ambiguity_warning_count: 2
control_profile_mimicry_warnings_count: 0
residual_matched_profile_warnings_count: 0
adversarial_profile_warnings_count: 0
collision_penalty_applied_count: 2
mean_profile_distance_raw: 0.10929545901770898
mean_profile_distance_collision_penalized: 0.15304545901770897
```

## 3. Motivation from D1e

D1e reduced observed mimicry/collision warnings in the tested synthetic setup compared with D1c/D1d.

But D1e does not establish diagnostic specificity.

The reduced warning counts may depend on the chosen synthetic families, parameter values, profile weights, penalty weights, and kernel scale.

D1f must test whether D1e still looks good when the test becomes less friendly.

## 4. Central question

Core question:

```text
Bleibt die gute D1e-Warnlage bestehen, wenn wir Parameter breiter streuen, Decoys haerter machen, Profilgewichte variieren und Kernelgroessen vergleichen?
```

English formulation:

Does the collision-aware `wave_identity_profile` remain stable under broader synthetic parameter sweeps, harder decoys, profile-weight variation, kernel-size scaling, and independent null families?

## 5. Why D1e is not yet enough

The D1b / D1c / D1d / D1e chain:

- D1b showed that a standalone residual is computable.
- D1c showed that the standalone residual is vulnerable to mimicry and adversarial controls.
- D1d showed that the feature space is not collapsed, but naive projections collide.
- D1e showed improved warning behavior under collision-aware profile logic.

However, D1e used one limited synthetic configuration.

A single friendly synthetic configuration cannot establish robustness, diagnostic specificity, or physical relevance.

## 6. Robustness axes

D1f plans five robustness axes.

A. Parameter sweeps:

- `k` variation width
- phase drift width
- `A` / `B` amplitude perturbation width
- local slope / intercept perturbation width
- noise amplitude

B. Harder decoys:

- residual-matched decoy family expansion
- adversarial near-duplicate expansion
- profile-matched decoy
- collision-targeting decoy
- control-overlap decoy

C. Profile-component weight sensitivity:

- `coordinate_profile` weight variation
- `angular_phase_profile` weight variation
- `local_response_profile` weight variation
- `residual_weight_profile` weight variation
- `rank_stability_profile` weight variation
- `collision_profile` weight variation
- `control_response_profile` weight variation

D. Kernel-size scaling:

- 8-node baseline
- 16-node synthetic extension
- 32-node synthetic extension

E. Independent null families:

- random parameter null
- spectrum-matched null
- amplitude-matched null
- phase-randomized null
- profile-shuffled null
- family-label shuffled null

## 7. Parameter-sweep plan

D1f plans parameter sweeps only. No sweep is executed in this plan.

Planned ranges:

- `k_shift_range`: small, medium, large
- `phase_drift_range`: small, medium, large
- `amplitude_perturbation_range`: small, medium, large
- `B_slope_perturbation_range`: small, medium, large
- `noise_level`: 0.0, 0.01, 0.02, 0.05
- `seed_count_per_family`: at least 20 for initial smoke, larger later

Each sweep must document deterministic seeds.

All later runs must keep `specificity_established=false` unless an explicit later specificity standard is defined and satisfied.

The purpose of parameter sweeps is to ask whether the D1e warning reduction is stable across a broader synthetic neighborhood, not to fit physical parameters.

## 8. Harder decoy plan

D1f plans additional decoy families:

- `residual_matched_decoy_sweep`: expands residual-matched cases across deterministic seeds and parameter ranges.
- `adversarial_near_duplicate_sweep`: tests coordinated small shifts in spectral, angular, and local-response components.
- `profile_matched_decoy`: imitates multiple profile components at once, not only the residual.
- `rank_stability_matched_decoy`: targets similar residual ranks across profile-weight sets.
- `collision_penalty_evading_decoy`: tests whether a control can imitate the profile without triggering a penalty.
- `angular_phase_matched_decoy`: matches angular phase behavior while differing in other coordinates.
- `local_response_matched_decoy`: matches slope/intercept/local-response behavior while differing in spectral or angular coordinates.
- `multi_component_matched_decoy`: combines residual, rank, local-response, and angular mimicry.

The `profile_matched_decoy` is especially important because a later control should try to imitate several profile components simultaneously.

The `collision_penalty_evading_decoy` is especially important because it checks whether a control can imitate the profile without activating the warning logic.

## 9. Profile-component weight-sensitivity plan

D1f plans explicit profile and penalty weight sets:

- `equal_profile_weights`
- `coordinate_dominant`
- `angular_phase_dominant`
- `local_response_dominant`
- `residual_weight_dominant`
- `rank_stability_dominant`
- `collision_penalty_dominant`
- `control_response_dominant`
- `collision_penalty_off`
- `control_response_off`
- `angular_phase_off`
- `rank_stability_off`

All profile and penalty weights must later be explicit in config and output.

If reduced warnings appear only under one weight set, `profile_weight_sensitivity_warning` must be set.

If penalty-weight choices alone drive the result, `penalty_weight_sensitivity_warning` must be set.

## 10. Kernel-size scaling plan

D1f plans kernel-size scaling only. Nothing is implemented here.

Planned comparison:

- `kernel_size_8`
- `kernel_size_16`
- `kernel_size_32`

Goals:

- Test whether coordinate richness remains stable.
- Test whether collision counts decrease or increase with a larger feature space.
- Test whether D1e warning reductions persist in a larger synthetic kernel.
- Test whether small-system artifacts of the 8-node kernel become visible.

Kernel-size scaling is a methodological robustness test, not a physical system-size claim.

## 11. Independent null-family plan

D1f plans independent null families:

- `random_parameter_null`
- `distribution_matched_null`
- `spectrum_matched_null`
- `phase_randomized_null`
- `amplitude_preserved_null`
- `label_shuffle_null`
- `profile_shuffle_null`
- `control_family_permutation_null`

Each null family must produce its own warning counts, overlap counts, and profile-distance distributions.

Independent null families test whether reduced D1e warnings are robust against controls that were not tuned from the original D1e setup.

## 12. Planned output files for later implementation

Planned future repo files, not created by D1f:

- `data/qsb_st_comp01d1f_collision_aware_profile_robustness_sweep_config.yaml`
- `scripts/run_qsb_st_comp01d1f_collision_aware_profile_robustness_sweep.py`
- `docs/QSB_ST_COMP01D1F_COLLISION_AWARE_PROFILE_ROBUSTNESS_PARAMETER_SWEEP_RESULT_NOTE_TEMPLATE.md`

Planned future run outputs:

- `runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/summary.json`
- `runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/readout.md`
- `runs/QSB-ST-COMP01D1F/case_profile_summary.csv`
- `runs/QSB-ST-COMP01D1F/profile_weight_summary.csv`
- `runs/QSB-ST-COMP01D1F/decoy_family_summary.csv`
- `runs/QSB-ST-COMP01D1F/kernel_size_summary.csv`
- `runs/QSB-ST-COMP01D1F/null_family_summary.csv`
- `runs/QSB-ST-COMP01D1F/warning_stability_summary.csv`
- `runs/QSB-ST-COMP01D1F/resolved_config.json`

If a later implementation uses a run subfolder, all outputs should be placed consistently under:

`runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/`

## 13. Continuous field list

Planned continuous field list:

| field name | field type | field description |
| --- | --- | --- |
| `run_id` | string | Identifier for the robustness sweep run. |
| `case_id` | string | Deterministic case identifier for a generated sweep case. |
| `sweep_seed` | integer | Deterministic seed used for the case. |
| `kernel_size_label` | string | Label such as `kernel_size_8`, `kernel_size_16`, or `kernel_size_32`. |
| `kernel_size` | integer | Synthetic kernel size used for the case. |
| `parameter_sweep_family` | string | Parameter-sweep family label. |
| `decoy_family` | string | Decoy family label. |
| `null_family` | string | Null family label. |
| `profile_weight_set_id` | string | Profile-component weight-set identifier. |
| `penalty_weight_set_id` | string | Penalty-weight-set identifier. |
| `pair_id` | string | Wave-pair identifier. |
| `wave_id_i` | string | First wave identifier. |
| `wave_id_j` | string | Second wave identifier. |
| `control_family` | string | Control or reference family for the pair. |
| `k_shift_level` | string | Discrete level for `k` shift width. |
| `phase_drift_level` | string | Discrete level for phase drift width. |
| `amplitude_perturbation_level` | string | Discrete level for `A` / `B` perturbation width. |
| `slope_perturbation_level` | string | Discrete level for local slope perturbation width. |
| `noise_level` | float | Synthetic noise amplitude. |
| `profile_distance_raw` | float | Raw diagnostic profile distance. |
| `profile_distance_collision_penalized` | float | Profile distance after explicit warning penalties. |
| `total_collision_penalty` | float | Total methodological penalty applied to the case. |
| `profile_collision` | boolean | True if a profile collision is detected. |
| `residual_collision` | boolean | True if residual profile collision is detected. |
| `delta_vector_collision` | boolean | True if delta-vector collision is detected. |
| `ambiguity_warning` | boolean | True if any collision or ambiguity warning is active. |
| `control_profile_mimicry_warning` | boolean | True if a control overlaps the near-duplicate profile region. |
| `residual_matched_profile_warning` | boolean | True if a residual-matched decoy imitates the profile. |
| `adversarial_profile_warning` | boolean | True if adversarial near-duplicate behavior is flagged. |
| `profile_weight_sensitivity_warning` | boolean | True if warning reduction depends on profile weights. |
| `penalty_weight_sensitivity_warning` | boolean | True if warning reduction depends on penalty weights. |
| `kernel_size_sensitivity_warning` | boolean | True if warning behavior changes across kernel sizes. |
| `null_family_overlap_warning` | boolean | True if an independent null overlaps the near-duplicate profile region. |
| `warning_count_total` | integer | Total warning count for the case. |
| `warning_count_reduction_vs_d1c` | integer | Diagnostic warning-count reduction relative to D1c baseline. |
| `warning_count_reduction_vs_d1d` | integer | Diagnostic warning-count reduction relative to D1d baseline. |
| `warning_count_reduction_vs_d1e` | integer | Diagnostic warning-count reduction relative to D1e baseline. |
| `profile_separation_margin` | float | Difference between reference and control profile regions. |
| `control_overlap_rate` | float | Fraction of controls overlapping the near-duplicate profile region. |
| `decoy_success_rate` | float | Fraction of decoys that evade or defeat the profile warning logic. |
| `exact_duplicate_sanity_passed` | boolean | Exact duplicate sanity status. |
| `specificity_established` | boolean | Claim brake; remains false unless later criteria are defined and satisfied. |
| `decision_status` | string | Defensive decision label. |
| `warning_flags` | string | Semicolon-separated warning flags. |
| `interpretation_note` | string | Short diagnostic interpretation note. |

## 14. Acceptance criteria for later implementation

Later implementation should check at least:

- YAML config parses.
- Runner runs without external real data.
- All planned outputs exist.
- CSVs parse with `csv.DictReader`.
- All sweep seeds are recorded.
- All profile and penalty weight sets are explicitly reported.
- Exact duplicate sanity remains true for all sweep families.
- `specificity_established` remains false.
- Warning counts are reported per sweep family, decoy family, weight set, kernel size, and null family.
- Reduced warning counts from D1e are tested for stability.
- No decision label claims proof, proven, validated, physical identity, or positive specificity status.
- Readout separates Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary.
- Claim-risk grep is clean or only contains negated / Claim Boundary mentions.
- `git diff --check` passes.

## 15. Interpretation rules

Befund:

Do warning counts remain low under broader sweeps, harder decoys, weight changes, kernel scaling, and null families?

Interpretation:

Is D1e's improved behavior robust, or was it tuned/friendly?

Hypothese:

Could the collision-aware profile remain useful as a diagnostic search axis?

Offene Lücke:

No physical validation, no real data, no diagnostic specificity, no physical manifold, no Lorentzian structure, no physical time, and no Pauli claim.

## 16. Decision logic

Planned defensive labels:

- `exact_duplicate_sanity_pass`
- `exact_duplicate_sanity_fail`
- `warning_reduction_stable_candidate`
- `warning_reduction_unstable_warning`
- `profile_weight_sensitivity_warning`
- `penalty_weight_sensitivity_warning`
- `kernel_size_sensitivity_warning`
- `null_family_overlap_warning`
- `decoy_success_warning`
- `control_overlap_warning`
- `inconclusive`
- `failed_sanity_check`

No label may claim proof, proven, validated, physical identity, or a positive specificity status.

## 17. What this plan must not do

- does not implement the robustness runner
- does not create config files
- does not create run outputs
- does not interpret D1e as specificity
- does not claim that a diagnostic manifold is physical spacetime
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

The D1f plan does not establish diagnostic specificity.

The D1f plan does not prove wave identity.

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

COMP01-D1f does not attach D(A,B).

COMP01-D1f does not construct S_rel2.

COMP01-D1f does not derive a Lorentzian metric.

COMP01-D1f does not validate a physical Bridge.

COMP01-D1f does not establish diagnostic specificity.

This is synthetic diagnostic collision-aware profile robustness planning only.

## 19. Current status label

current_status_label: COMP01D1F_collision_aware_profile_robustness_parameter_sweep_plan_created
