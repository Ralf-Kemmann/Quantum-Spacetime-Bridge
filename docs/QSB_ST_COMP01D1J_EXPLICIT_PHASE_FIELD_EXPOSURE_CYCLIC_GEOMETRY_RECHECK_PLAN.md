# QSB-ST-COMP01-D1j Explicit Phase-Field Exposure and Cyclic Geometry Recheck Plan

## 1. Purpose

COMP01-D1j is a planning block only.

D1j plans how explicit phase-like fields from the synthetic COMP01-D1f/D1h context can be made visible, or transparently re-emitted, so that the D1h cyclic-coordinate geometry can be rechecked without relying only on `cyclic_phase_proxy`.

D1j does not create a scanner, config, run, or result. It does not implement a runner and does not produce new run outputs.

D1j does not build a new identity score. D1j does not build a physical phase. D1j plans a methodological phase-field-exposure layer for synthetic diagnostics.

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
- COMP01-D1h Cyclic-Coordinate Acceptance-Region Runner implemented and result documented
- COMP01-D1i Cyclic-Phase Source Validation and Overstrictness Audit Runner implemented and result documented

Current commit anchor:

- `ff47b10 Add QSB-ST COMP01D1i cyclic phase source validation result note`

D1i anchor values:

```yaml
case_count: 9450
specificity_established: false
baseline_cyclic_phase_source: cyclic_phase_proxy
explicit_phase_source_available: false
detected_phase_columns: []
phase_source_validation_status: explicit_phase_source_missing
proxy_variant_count: 6
threshold_variant_count: 5
proxy_dependence_warning_count: 6
threshold_sensitivity_warning_count: 12
overstrictness_warning_count: 30
stable_candidate_loss_warning_count: 30
remaining_intrusion_warning_count: 28
mean_stable_candidate_loss_rate: 0.20517658442186745
dominant_proxy_variant_decision_status: cyclic_overstrictness_warning
dominant_threshold_decision_status: cyclic_overstrictness_warning
```

## 3. Motivation from D1i

D1h produced a positive synthetic diagnostic result, but D1i showed that this result cannot yet be treated as robust cyclic-coordinate evidence because no explicit phase source was available.

D1i found:

- `explicit_phase_source_available: false`
- `detected_phase_columns: []`
- `phase_source_validation_status: explicit_phase_source_missing`
- proxy dependence warnings
- threshold sensitivity warnings
- overstrictness warnings
- stable-candidate loss risk

Therefore, D1j must expose or construct transparent explicit phase-like synthetic fields before cyclic geometry can be rechecked.

D1j is not a claim escalation. It is a source-transparency and recheck planning step.

## 4. Central question

Kann die cyclic-coordinate geometry aus D1h bestaetigt oder begrenzt werden, wenn statt `cyclic_phase_proxy` explizite phase-like synthetic fields verwendet werden?

Does the D1h cyclic-coordinate reduction persist when the phase axis is based on explicit synthetic phase-like fields rather than a diagnostic proxy?

## 5. Why explicit phase fields are needed

- D1h used `cyclic_phase_proxy`.
- D1i found no explicit phase columns.
- Proxy variants triggered proxy-dependence warnings.
- Threshold variants triggered threshold/overstrictness warnings.
- A cyclic-coordinate claim requires at least transparent phase-like source fields in the synthetic diagnostic system.
- Explicit phase-like fields would allow direct comparison:
  - proxy vs explicit phase
  - explicit wrapped distance vs proxy wrapped distance
  - cos/sin embedding vs scalar wrapped distance
  - overstrictness under explicit phase

## 6. Source inspection plan

A later implementation should first inspect whether existing D1f/D1h inputs or generator code contain latent phase-like fields. The inspection should be read-only and should not modify D1f, D1g, D1h, or D1i outputs.

Sources to inspect:

- `data/qsb_st_comp01d1f_collision_aware_profile_robustness_sweep_config.yaml`
- `scripts/run_qsb_st_comp01d1f_collision_aware_profile_robustness_sweep.py`
- `runs/QSB-ST-COMP01D1F/collision_aware_profile_robustness_sweep_open/case_profile_summary.csv`
- `runs/QSB-ST-COMP01D1H/cyclic_coordinate_acceptance_region_open/cyclic_region_case_summary.csv`

Field names to search:

- `phi_i`
- `phi_j`
- `phase_i`
- `phase_j`
- `theta_i`
- `theta_j`
- `delta_phi`
- `delta_phi_wrapped`
- `wrapped_delta_phi_abs`
- `cos_delta_phi`
- `sin_delta_phi`
- `angular_phase_profile`
- `phase_source_label`
- `phase_like_source`
- `cyclic_phase_source`

If such fields are missing, D1j must not claim to have reconstructed phase. In that case, the later implementation must report the absence and plan a transparent synthetic phase exposure layer.

## 7. Explicit phase-field exposure plan

A later implementation may expose or add transparent phase-like output fields if source inspection supports that step.

Possible new phase-like output fields:

- `phi_i`
- `phi_j`
- `delta_phi_raw`
- `delta_phi_wrapped`
- `wrapped_delta_phi_abs`
- `cos_phi_i`
- `sin_phi_i`
- `cos_phi_j`
- `sin_phi_j`
- `cos_delta_phi`
- `sin_delta_phi`
- `angular_phase_distance`
- `phase_source_label`
- `phase_exposure_mode`

Possible `phase_exposure_mode` values:

- `existing_generator_phase`
- `reconstructed_from_existing_synthetic_parameters`
- `deterministic_synthetic_phase_extension`
- `unavailable_proxy_only`

If no genuine latent phase is present, a `deterministic_synthetic_phase_extension` may be planned, but it must be clearly marked as a synthetic extension. It must not be described as physical phase or as recovered phase.

## 8. Phase-derived diagnostic fields

A later implementation may derive diagnostic fields from explicit phase-like synthetic fields:

- `angular_distance_wrapped`
- `normalized_angular_distance`
- `cyclic_distance_cos_sin`
- `phase_alignment_score`
- `phase_opposition_score`
- `phase_wrap_boundary_flag`
- `phase_band_label`
- `cyclic_phase_region_label`

Planned formula conventions:

```text
delta_phi_wrapped = atan2(sin(phi_i - phi_j), cos(phi_i - phi_j))
wrapped_delta_phi_abs = abs(delta_phi_wrapped)
normalized_angular_distance = wrapped_delta_phi_abs / pi
cos_delta_phi = cos(delta_phi_wrapped)
sin_delta_phi = sin(delta_phi_wrapped)
```

These fields are diagnostic-methodological fields, not physical fields.

## 9. Cyclic geometry recheck design

A later D1j implementation should recheck cyclic geometry through separate, comparable modes:

A. `baseline_proxy_recheck`

- D1h `cyclic_phase_proxy` baseline

B. `explicit_phase_recheck`

- cyclic distance from explicit phase-like fields

C. `cos_sin_embedding_recheck`

- cyclic phase represented by cos/sin pair

D. `wrapped_scalar_recheck`

- normalized wrapped angular distance

E. `proxy_vs_explicit_comparison`

- compare case-level changes

Required metrics:

- `false_accept_warning_count`
- `exclusion_success_rate`
- `exclusion_failure_rate`
- `stable_candidate_cyclic_count`
- `fragile_candidate_cyclic_count`
- `stable_candidate_loss_rate`
- `overstrictness_warning_count`
- `remaining_intrusion_warning_count`
- `spectrum_matched_null_intrusion_count`
- `adversarial_near_duplicate_intrusion_count`
- `kernel_size_8_artifact_warning_count`

## 10. Comparison against D1h and D1i baselines

D1h baseline:

```yaml
current_false_accept_warning_count: 4901
cyclic_false_accept_warning_count: 992
exclusion_success_rate: 0.9691899612324015
stable_candidate_cyclic_count: 7907
fragile_candidate_cyclic_count: 1543
mean_warning_delta_current_to_cyclic: -2.520846560846561
```

D1i audit:

```yaml
explicit_phase_source_available: false
detected_phase_columns: []
proxy_dependence_warning_count: 6
threshold_sensitivity_warning_count: 12
overstrictness_warning_count: 30
stable_candidate_loss_warning_count: 30
mean_stable_candidate_loss_rate: 0.20517658442186745
```

D1j should compare the explicit-phase recheck against both the D1h proxy baseline and the D1i proxy/threshold/overstrictness audit.

## 11. Overstrictness and stable-retention recheck

A later implementation should report:

- `current_stable_and_explicit_phase_stable`
- `current_stable_but_explicit_phase_fragile`
- `current_fragile_but_explicit_phase_stable`
- `current_fragile_and_explicit_phase_fragile`
- `stable_candidate_loss_rate_explicit`
- `retained_stable_candidate_rate_explicit`
- `explicit_phase_overstrictness_warning`

If explicit phase reduces false accepts but loses too many current stable candidates, D1j must report overstrictness.

## 12. Remaining intrusion recheck

A later implementation should specifically inspect remaining intrusions:

- `spectrum_matched_null`
- `adversarial_near_duplicate_sweep`
- `local_response_dominant`
- `strong_collision_penalties`
- `kernel_size_8`
- `impostor_overlap_warning`

D1j should distinguish:

- geometry-supported reduction
- remaining intrusion
- overstrict exclusion
- explicit phase source unavailable

## 13. Decision-table integration

D1j should not replace the D1g/D1h decision tables. It should preserve them as transparent classification layers and add explicit-phase source and recheck labels where needed.

Possible labels:

- `explicit_phase_source_available_candidate`
- `explicit_phase_source_missing_warning`
- `explicit_phase_geometry_reduces_false_accept_candidate`
- `explicit_phase_geometry_no_improvement_warning`
- `explicit_phase_overstrictness_warning`
- `proxy_vs_explicit_phase_mismatch_warning`
- `cos_sin_embedding_supported_candidate`
- `wrapped_scalar_supported_candidate`
- `remaining_intrusion_under_explicit_phase_warning`
- `stable_retention_supported_candidate`
- `inconclusive`

No label may claim proof, physical identity, or established specificity.

## 14. Mastermind / role-permutation idea parking note

Ralf/Nova noted a later Mastermind-style pairwise role-permutation idea:

- each diagnostic dimension can be treated like a color
- the compared wave can serve as the pairwise reference
- identity-like matching may require correct component values and correct relational roles/positions
- this is not part of D1j
- it should be considered only after explicit phase-source cleanup and cyclic geometry recheck

## 15. Planned implementation design

A later implementation should:

- read D1f generator/config/script
- inspect existing output fields
- detect explicit phase-like columns
- if available, compute explicit-phase cyclic fields
- if unavailable, write `phase_source_status=missing` and optionally plan `deterministic_synthetic_phase_extension`
- rerun cyclic geometry classification layer using explicit phase-like fields if available
- compare against D1h proxy baseline
- compare against D1i proxy/threshold audit
- do not modify D1f/D1g/D1h/D1i outputs
- do not rerun D1f unless a later separately planned generator extension explicitly allows new synthetic outputs
- produce only diagnostic summaries

## 16. Planned output files for later implementation

Planned future files only. This D1j plan does not create them.

Future implementation inputs/templates:

- `data/qsb_st_comp01d1j_explicit_phase_field_exposure_cyclic_recheck_config.yaml`
- `scripts/run_qsb_st_comp01d1j_explicit_phase_field_exposure_cyclic_recheck.py`
- `docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_RESULT_NOTE_TEMPLATE.md`

Future run outputs:

- `runs/QSB-ST-COMP01D1J/explicit_phase_field_exposure_cyclic_recheck_open/summary.json`
- `runs/QSB-ST-COMP01D1J/explicit_phase_field_exposure_cyclic_recheck_open/readout.md`
- `runs/QSB-ST-COMP01D1J/explicit_phase_source_inventory.csv`
- `runs/QSB-ST-COMP01D1J/phase_field_exposure_summary.csv`
- `runs/QSB-ST-COMP01D1J/explicit_phase_cyclic_recheck_summary.csv`
- `runs/QSB-ST-COMP01D1J/proxy_vs_explicit_phase_comparison.csv`
- `runs/QSB-ST-COMP01D1J/explicit_phase_overstrictness_summary.csv`
- `runs/QSB-ST-COMP01D1J/explicit_phase_remaining_intrusion_summary.csv`
- `runs/QSB-ST-COMP01D1J/resolved_config.json`

## 17. Continuous field list

| field name | field type | field description |
| --- | --- | --- |
| `run_id` | string | Planned D1j run identifier. |
| `source_file` | string | Source file inspected or summarized. |
| `source_type` | string | Source category, such as config, script, D1f output, or D1h output. |
| `phase_source_available` | boolean | Whether explicit phase-like fields are available from inspected sources. |
| `detected_phase_columns` | list[string] | Explicit or phase-like columns detected during source inspection. |
| `phase_source_label` | string | Label describing the phase-like source used for the recheck. |
| `phase_exposure_mode` | enum | Exposure mode, such as existing generator phase, reconstructed synthetic parameters, deterministic synthetic extension, or proxy-only unavailable mode. |
| `case_id` | string | Case identifier carried from the existing synthetic run outputs. |
| `phi_i` | float/null | Planned phase-like coordinate for item i, if available. |
| `phi_j` | float/null | Planned phase-like coordinate for item j, if available. |
| `delta_phi_raw` | float/null | Raw phase-like difference before wrapping. |
| `delta_phi_wrapped` | float/null | Wrapped phase-like difference using atan2(sin(delta), cos(delta)). |
| `wrapped_delta_phi_abs` | float/null | Absolute wrapped phase-like distance. |
| `cos_phi_i` | float/null | Cosine embedding of `phi_i`. |
| `sin_phi_i` | float/null | Sine embedding of `phi_i`. |
| `cos_phi_j` | float/null | Cosine embedding of `phi_j`. |
| `sin_phi_j` | float/null | Sine embedding of `phi_j`. |
| `cos_delta_phi` | float/null | Cosine of the wrapped phase-like difference. |
| `sin_delta_phi` | float/null | Sine of the wrapped phase-like difference. |
| `angular_phase_distance` | float/null | Phase-like angular distance used by the diagnostic layer. |
| `normalized_angular_distance` | float/null | `wrapped_delta_phi_abs / pi`. |
| `cyclic_distance_cos_sin` | float/null | Cyclic distance computed from cos/sin embedding. |
| `phase_alignment_score` | float/null | Diagnostic score for phase-like alignment. |
| `phase_opposition_score` | float/null | Diagnostic score for phase-like opposition. |
| `phase_wrap_boundary_flag` | boolean | Whether the case lies near a wrap boundary. |
| `phase_band_label` | string/null | Discrete phase-like band label for analysis. |
| `cyclic_phase_region_label` | string/null | Cyclic-region label assigned by the recheck layer. |
| `baseline_cyclic_phase_proxy_distance` | float/null | D1h proxy-based cyclic distance for comparison. |
| `explicit_phase_cyclic_distance` | float/null | Explicit phase-like cyclic distance for comparison. |
| `proxy_vs_explicit_phase_distance_delta` | float/null | Difference between proxy and explicit phase-like distance. |
| `cyclic_acceptance_distance_proxy` | float/null | Proxy-based cyclic acceptance distance. |
| `cyclic_acceptance_distance_explicit` | float/null | Explicit phase-like cyclic acceptance distance. |
| `false_accept_warning_proxy` | boolean | D1h proxy-based false-accept warning flag. |
| `false_accept_warning_explicit` | boolean | Explicit phase-like false-accept warning flag. |
| `exclusion_success_proxy` | boolean | Proxy-based exclusion success flag. |
| `exclusion_success_explicit` | boolean | Explicit phase-like exclusion success flag. |
| `stable_candidate_proxy` | boolean | Proxy-based stable-candidate flag. |
| `stable_candidate_explicit` | boolean | Explicit phase-like stable-candidate flag. |
| `fragile_candidate_proxy` | boolean | Proxy-based fragile-candidate flag. |
| `fragile_candidate_explicit` | boolean | Explicit phase-like fragile-candidate flag. |
| `stable_candidate_loss_rate_explicit` | float/null | Fraction of current stable candidates lost under explicit phase-like recheck. |
| `explicit_phase_overstrictness_warning` | boolean | Whether explicit phase-like recheck appears overstrict. |
| `spectrum_matched_null_intrusion_warning` | boolean | Warning for spectrum-matched null intrusion under explicit phase-like recheck. |
| `adversarial_near_duplicate_intrusion_warning` | boolean | Warning for adversarial near-duplicate intrusion under explicit phase-like recheck. |
| `kernel_size_8_artifact_warning` | boolean | Warning for kernel-size-8 artifact under explicit phase-like recheck. |
| `remaining_intrusion_warning` | boolean | General remaining-intrusion warning under explicit phase-like recheck. |
| `decision_status` | string | Transparent methodological decision-table label. |
| `warning_flags` | list[string] | Active warning flags for the case or summary row. |
| `interpretation_note` | string | Bounded note separating finding, interpretation, hypothesis, open gap, and claim boundary. |

## 18. Acceptance criteria for later implementation

A later implementation should check at least:

- YAML config parses
- runner reads existing D1h/D1i summaries
- runner inspects D1f/D1h outputs for phase-like columns
- runner reports `detected_phase_columns`
- runner reports `explicit_phase_source_available`
- runner does not modify D1f/D1g/D1h/D1i outputs
- runner does not introduce physical phase
- all planned outputs exist
- CSVs parse with `csv.DictReader`
- explicit phase formulas are documented if phase fields exist
- if no explicit phase exists, result says `explicit_phase_source_missing`
- proxy vs explicit comparison is reported if possible
- overstrictness under explicit phase is reported if possible
- remaining intrusions are reported
- `specificity_established` remains false
- no decision label claims proof
- readout separates Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary
- claim-risk grep clean or only negated/Claim Boundary mentions
- `git diff --check` passes

## 19. Interpretation rules

Befund:

Are explicit phase-like fields available, and can cyclic geometry be rechecked without proxy-only phase?

Interpretation:

If explicit phase fields are available, does the D1h reduction persist with less proxy dependence and acceptable stable retention?

Hypothese:

Explicit phase-like synthetic outputs may make cyclic-coordinate testing more meaningful and reduce proxy-dependence uncertainty.

Offene Luecke:

No physical validation, no real data, no specificity, no physical phase reconstruction, no physical manifold, no Lorentzian structure, no physical time, no Pauli claim.

## 20. Decision logic

Planned cautious labels:

- `explicit_phase_source_available_candidate`
- `explicit_phase_source_missing_warning`
- `explicit_phase_geometry_reduces_false_accept_candidate`
- `explicit_phase_geometry_no_improvement_warning`
- `explicit_phase_overstrictness_warning`
- `proxy_vs_explicit_phase_mismatch_warning`
- `explicit_phase_remaining_intrusion_warning`
- `stable_retention_supported_candidate`
- `cos_sin_embedding_supported_candidate`
- `wrapped_scalar_supported_candidate`
- `deterministic_synthetic_phase_extension_needed`
- `inconclusive`
- `failed_input_consistency_check`

No label may claim proof, physical identity, or established specificity.

## 21. What this plan must not do

- does not implement the D1j runner
- does not rerun D1f
- does not modify D1f/D1g/D1h/D1i outputs
- does not create config files
- does not create run outputs
- does not claim `cyclic_phase_proxy` is physical phase
- does not claim explicit synthetic phase fields are physical phase
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
- does not implement the Mastermind/role-permutation idea yet

## 22. Claim Boundary

D1j is an explicit phase-field exposure and cyclic geometry recheck planning document.

D1j plans to make phase-like synthetic fields visible for diagnostic rechecking.

D1j does not rerun D1f.

D1j does not modify D1f, D1g, D1h, or D1i outputs.

D1j does not introduce a new identity score.

D1j does not establish diagnostic specificity.

cyclic_phase_proxy is diagnostic only.

Explicit synthetic phase-like fields, if later exposed, are diagnostic synthetic fields.

They are not physical phase reconstruction.

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

The D1j plan does not prove wave identity.

The D1j plan does not validate physical phase reconstruction.

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

COMP01-D1j does not attach D(A,B).

COMP01-D1j does not construct S_rel2.

COMP01-D1j does not derive a Lorentzian metric.

COMP01-D1j does not validate a physical Bridge.

COMP01-D1j does not establish diagnostic specificity.

This is synthetic diagnostic explicit phase-field exposure and cyclic geometry recheck planning only.

## 23. Current status label

current_status_label: COMP01D1J_explicit_phase_field_exposure_cyclic_geometry_recheck_plan_created
