# QSB-ST-COMP01-D1d Wave Identity Manifold and Degeneracy Audit Plan

## 1. Purpose

COMP01-D1d is a planning block only.

D1d plans a later audit of the diagnostic wave-identity feature space before introducing further stronger identity metrics. It does not create a scanner, does not create a config, does not create runs, and does not create results.

Goal:

Check whether the synthetic wave-identity feature space has enough non-collapsed dimensions to support meaningful distinguishability tests.

The purpose is to audit the coordinate space itself: if the feature space is too symmetric, too low-dimensional, or too collision-prone, then adding another single residual would likely repeat the D1c control-mimicry problem.

## 2. Current status anchor

Current chain:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Runner implemented and result documented

Current commit anchor:

`8810d63 Add QSB-ST COMP01D1c wave identity residual stress result note`

D1c result values:

```yaml
pair_count: 16
weight_set_count: 7
row_count: 112
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed_all_weight_sets: true
control_mimicry_warnings_count: 68
residual_matched_warnings_count: 7
weight_sensitivity_warnings_count: 8
```

## 3. Motivation from D1c and external review

D1c showed that `wave_identity_residual` is computable and sanity-stable, but vulnerable to control mimicry and residual-matched / adversarial decoys.

Deep Research and external review suggest that single fingerprints are often collision-prone and spoofable. Robust identity work usually requires multi-feature profiles, invariance / ambiguity checks, and control-resistance tests.

A Claude-style review also raised a prior concern:

In a small synthetic kernel, the feature space may be too low-dimensional, symmetric, normalized, or degenerate to support robust distinguishability.

Before adding more identity metrics, D1d audits whether the feature space has enough non-collapsed structure to support meaningful wave-identity diagnostics.

## 4. Central question

Core question:

```text
Woran merke ich, dass ich die gleiche, aber nicht dieselbe Welle habe?
```

D1d-specific reformulation:

Is the diagnostic wave-identity feature space rich enough to distinguish type-like similarity from relational identity, or do collapsed directions and profile collisions make apparent identities easy to fake?

## 5. Diagnostic manifold language

The term manifold / Manigfaltigkeit is used here only as diagnostic feature-space language.

Preferred terms:

- diagnostic feature manifold
- wave identity feature space
- profile geometry
- diagnostic coordinate space

Boundaries:

- This is not a physical spacetime manifold.
- This is not a Hilbert-space reconstruction.
- This is not a Lorentzian geometry.
- This is not a physical phase space.

D1d uses manifold language to ask whether the synthetic descriptors form a sufficiently rich diagnostic coordinate space, not to assert physical geometry.

## 6. Proposed wave identity coordinates

Planned later wave-level / node-level coordinates:

- `wave_id`
- `k`
- `A`
- `B`
- `R = sqrt(A^2 + B^2)`
- `phi = atan2(B, A)`
- `slope = B * k`
- `intercept = A`
- `amplitude_balance = A - B`
- `normalized_amplitude_balance`
- optional `local_response_norm`

The real working form remains:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

The local tangent at `x0 = 0` remains:

```text
intercept_i = A_i
slope_i = B_i * k_i
```

A complex trigonometric extension may remain a later route. It is not a D1d requirement.

## 7. Cyclic, stratified, and collapsed directions

Planned coordinate cautions:

- `phi` is cyclic and should be handled with wrapped / angular differences, not naive subtraction.
- `k` may behave as a stratified or discretized coordinate in synthetic kernels.
- `A` / `B` / `R`-like directions may partially collapse under normalization.
- `slope = B * k` couples two coordinates and may not be independent.
- Some directions may be near-constant in small kernels.
- Feature manifold geometry may not be flat Euclidean without checks.

Planned later fields:

- `phi_wrapped`
- `wrapped_delta_phi_abs`
- `cos_delta_phi`
- `sin_delta_phi`
- `coordinate_std`
- `unique_value_count`
- `near_constant_flag`
- `normalization_collapse_warning`
- `coordinate_dependency_warning`

## 8. Degeneracy and collision audit

Planned checks:

- different wave IDs with near-identical profile vectors
- same or similar `wave_identity_residual` but different `delta_vector`
- same spectral component but different phase / local profile
- same local profile but different spectral / phase profile
- different control families occupying similar profile regions
- `residual_matched_decoy` collisions
- `adversarial_near_duplicate` collisions

Required audit terms:

- `profile_collision`
- `residual_collision`
- `delta_vector_collision`
- `ambiguity_warning`
- `collision_cluster_id`

D1d treats collisions as methodological warnings. Collision-prone coordinates should not be promoted into stronger identity claims.

## 9. Kernel-size and richness concern

Small synthetic kernels may be too low-dimensional to support robust identity diagnostics.

D1d should include a future recommendation to compare feature-space richness under larger synthetic kernels, for example:

- 8-node variants
- 16-node variants
- 32-node variants

This is only planned here. No larger-kernel implementation is introduced in D1d.

The point is to test whether profile collisions and collapsed coordinates are artifacts of a very small synthetic kernel or persistent properties of the current descriptor family.

## 10. Planned audit observables

Wave-level observables:

- `k`
- `A`
- `B`
- `R`
- `phi`
- `slope`
- `intercept`
- `normalized_amplitude_balance`
- `coordinate_std`
- `unique_value_count`
- `near_constant_flag`

Pair-level delta vector:

- `delta_k`
- `delta_R`
- `wrapped_delta_phi_abs`
- `cos_delta_phi`
- `sin_delta_phi`
- `delta_A`
- `delta_B`
- `delta_slope`
- `delta_intercept`
- `delta_balance`
- `delta_vector_norm`
- `profile_distance`

Degeneracy observables:

- `profile_collision_count`
- `residual_collision_count`
- `delta_vector_collision_count`
- `collision_cluster_id`
- `ambiguity_warning_count`
- `manifold_richness_score`
- `collapsed_coordinate_count`

Control observables:

- `label_shuffle_profile_overlap`
- `kernel_shuffle_profile_overlap`
- `control_profile_mimicry_warning`
- `residual_matched_profile_warning`
- `adversarial_profile_warning`

## 11. Planned output files for later implementation

Planned future repo files:

- `data/qsb_st_comp01d1d_wave_identity_manifold_degeneracy_audit_config.yaml`
- `scripts/run_qsb_st_comp01d1d_wave_identity_manifold_degeneracy_audit.py`
- `docs/QSB_ST_COMP01D1D_WAVE_IDENTITY_MANIFOLD_DEGENERACY_AUDIT_RESULT_NOTE_TEMPLATE.md`

Planned future run outputs:

- `runs/QSB-ST-COMP01D1D/wave_identity_manifold_degeneracy_audit_open/summary.json`
- `runs/QSB-ST-COMP01D1D/wave_identity_manifold_degeneracy_audit_open/readout.md`
- `runs/QSB-ST-COMP01D1D/wave_identity_manifold_degeneracy_audit_open/wave_coordinate_summary.csv`
- `runs/QSB-ST-COMP01D1D/wave_identity_manifold_degeneracy_audit_open/pair_delta_vector_summary.csv`
- `runs/QSB-ST-COMP01D1D/wave_identity_manifold_degeneracy_audit_open/collision_summary.csv`
- `runs/QSB-ST-COMP01D1D/wave_identity_manifold_degeneracy_audit_open/control_profile_overlap_summary.csv`
- `runs/QSB-ST-COMP01D1D/wave_identity_manifold_degeneracy_audit_open/resolved_config.json`

This D1d plan creates none of those files.

## 12. Continuous field list

| field name | field type | field description |
| --- | --- | --- |
| `wave_id` | string | Synthetic wave / diagnostic pattern identifier. |
| `k` | number | Wave-number-like diagnostic coordinate. |
| `A` | number | Cosine-channel coefficient in the real diagnostic form. |
| `B` | number | Sine-channel coefficient in the real diagnostic form. |
| `R` | number | Magnitude-like coordinate, `sqrt(A^2 + B^2)`. |
| `phi` | number | Angular coordinate, `atan2(B, A)`. |
| `phi_wrapped` | number | Wrapped angular coordinate in a documented interval. |
| `slope` | number | Local slope proxy, `B * k`. |
| `intercept` | number | Local intercept proxy, `A`. |
| `amplitude_balance` | number | Difference `A - B`. |
| `normalized_amplitude_balance` | number | Normalized balance with denominator protection. |
| `coordinate_name` | string | Name of the audited coordinate. |
| `coordinate_std` | number | Standard deviation of a coordinate across waves. |
| `unique_value_count` | integer | Count of distinct or tolerance-distinct coordinate values. |
| `near_constant_flag` | boolean | Whether a coordinate is near-constant under configured tolerance. |
| `normalization_collapse_warning` | boolean | Whether normalization collapses a coordinate direction. |
| `coordinate_dependency_warning` | boolean | Whether a coordinate is strongly dependent on another coordinate. |
| `pair_id` | string | Pair identifier. |
| `wave_id_i` | string | First wave identifier. |
| `wave_id_j` | string | Second wave identifier. |
| `control_family` | string | Family or control label. |
| `delta_k` | number | Absolute k difference. |
| `delta_R` | number | Absolute R difference. |
| `wrapped_delta_phi_abs` | number | Absolute wrapped angular difference. |
| `cos_delta_phi` | number | Cosine of angular difference. |
| `sin_delta_phi` | number | Sine of angular difference. |
| `delta_A` | number | Absolute A difference. |
| `delta_B` | number | Absolute B difference. |
| `delta_slope` | number | Absolute slope difference. |
| `delta_intercept` | number | Absolute intercept difference. |
| `delta_balance` | number | Absolute amplitude-balance difference. |
| `delta_vector_norm` | number | Norm of the pair-level diagnostic delta vector. |
| `profile_distance` | number | Distance between profile vectors under documented normalization. |
| `wave_identity_residual` | number | Existing diagnostic residual carried as context. |
| `profile_collision` | boolean | Whether two profiles collide under configured tolerance. |
| `residual_collision` | boolean | Whether residual values collide despite different profiles. |
| `delta_vector_collision` | boolean | Whether delta vectors collide under configured tolerance. |
| `collision_cluster_id` | string/null | Identifier for a detected collision cluster. |
| `ambiguity_warning` | boolean | Whether the profile / residual relation is ambiguous. |
| `profile_collision_count` | integer | Number of profile collisions. |
| `residual_collision_count` | integer | Number of residual collisions. |
| `delta_vector_collision_count` | integer | Number of delta-vector collisions. |
| `collapsed_coordinate_count` | integer | Number of near-constant or collapsed coordinates. |
| `manifold_richness_score` | number | Diagnostic richness score, not a physical quantity. |
| `label_shuffle_profile_overlap` | number | Profile overlap for label-shuffle controls. |
| `kernel_shuffle_profile_overlap` | number | Profile overlap for kernel-shuffle controls. |
| `control_profile_mimicry_warning` | boolean | Whether controls occupy similar profile regions. |
| `residual_matched_profile_warning` | boolean | Whether residual-matched decoys collide in profile space. |
| `adversarial_profile_warning` | boolean | Whether adversarial near-duplicates create profile ambiguity. |
| `decision_status` | string | Conservative audit decision label. |
| `warning_flags` | string/list | Explicit warning fields, never hidden. |
| `interpretation_note` | string | Short diagnostic interpretation note. |

## 13. Acceptance criteria for later implementation

Future implementation is accepted only if:

- YAML config parses.
- runner runs without external real data.
- all planned outputs exist.
- CSVs parse with `csv.DictReader`.
- `wave_coordinate_summary.csv` includes all synthetic wave IDs.
- `pair_delta_vector_summary.csv` includes all pair / control families.
- `collision_summary.csv` reports profile / residual / delta-vector collisions.
- `exact_duplicate` remains identified as a sanity case.
- `phi` differences use wrapped / angular handling.
- near-constant or collapsed coordinates are explicitly flagged.
- `specificity_established` remains false.
- no decision label claims proof.
- readout separates Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary.
- claim-risk grep is clean or contains only negated / Claim Boundary mentions.
- `git diff --check` passes.

## 14. Interpretation rules

Befund:

Which coordinates really vary? Which coordinates collapse? Which profile collisions occur?

Interpretation:

Is the diagnostic feature space rich enough to support later identity-profile tests?

Hypothese:

If enough non-collapsed dimensions exist, a `wave_identity_profile` may be more meaningful than a single residual.

Offene Lücke:

No physical validation, no real data, no specificity, no Lorentzian structure, no physical time, no Pauli claim.

## 15. Decision logic

Planned conservative decision labels:

- `manifold_audit_pass_minimal`
- `manifold_richness_warning`
- `coordinate_collapse_warning`
- `profile_collision_warning`
- `residual_collision_warning`
- `delta_vector_collision_warning`
- `control_profile_mimicry_warning`
- `inconclusive`
- `failed_sanity_check`

No label may claim proof, proven status, validated status, or physical identity.

## 16. What this plan must not do

- does not implement the audit runner
- does not create config files
- does not create run outputs
- does not interpret D1c as specificity
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

## 17. Claim Boundary

- The manifold language denotes a diagnostic coordinate space of synthetic wave-pattern descriptors.
- It is not a physical spacetime manifold.
- It is not a Hilbert-space reconstruction.
- It is not a Lorentzian geometry.
- It is not a physical phase space.
- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- wave_identity_residual is a diagnostic distinguishability construct, not a physical observable by itself.
- wave_identity_profile is a planned diagnostic profile concept, not a proof of physical identity.
- control mimicry warnings are methodological warnings, not failures of physics.
- wave-Pauli is a heuristic internal analogy only.
- It does not claim fermionic Pauli exclusion.
- It does not invoke quantum spin-statistics.
- It does not assert a physical exclusion principle.
- type-like similarity is not the same as relational identity.
- spectral shift is used here as a diagnostic analogy, not as cosmological redshift.
- phase drift is used here as a structure-internal pattern marker, not as physical time delay.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-D1d does not attach D(A,B).
- COMP01-D1d does not construct S_rel2.
- COMP01-D1d does not derive a Lorentzian metric.
- COMP01-D1d does not validate a physical Bridge.
- COMP01-D1d does not establish diagnostic specificity.
- This is synthetic diagnostic manifold/feature-space audit planning only.

## 18. Current status label

current_status_label: COMP01D1D_wave_identity_manifold_degeneracy_audit_plan_created
