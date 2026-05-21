# QSB-ST-COMP01-D1k Deterministic Synthetic Phase-Field Exposure Extension Plan

## 1. Purpose

COMP01-D1k is a planning block only.

D1k plans a deterministic synthetic phase-field exposure extension to make diagnostic synthetic phase-like fields visible.

D1k does not create a scanner, config, run, or result. It does not implement a runner and does not produce new run outputs.

D1k addresses the missing explicit phase source found in D1j. It plans how a transparent synthetic diagnostic extension could expose phase-like fields for later cyclic-geometry rechecking beyond the D1h `cyclic_phase_proxy` baseline.

D1k does not build a new identity score. D1k does not build a physical phase. D1k plans only a transparent synthetic diagnostic extension.

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
- COMP01-D1j Explicit Phase-Field Exposure and Cyclic Geometry Recheck Runner implemented and result documented

Current commit anchor:

- `d9542e7 Add QSB-ST COMP01D1j explicit phase field exposure result note`

D1j anchor values:

```yaml
case_count: 9450
specificity_established: false
explicit_phase_source_available: false
detected_phase_columns: []
detected_proxy_phase_columns:
  - cyclic_phase_distance
  - cyclic_phase_source
explicit_phase_recheck_possible: false
deterministic_synthetic_phase_extension_needed: true
baseline_cyclic_phase_source: cyclic_phase_proxy
baseline_proxy_false_accept_warning_count: 992
baseline_proxy_exclusion_success_rate: 0.9691899612324015
baseline_proxy_stable_candidate_count: 7907
phase_source_label: cyclic_phase_proxy_with_generator_phase_text_mentions
phase_exposure_mode: reconstructed_from_existing_synthetic_parameters_candidate
phase_source_decision_status: explicit_phase_source_missing_warning
cyclic_geometry_recheck_decision_status: explicit_phase_recheck_not_possible
mastermind_status: parked_not_implemented
```

## 3. Motivation from D1j

D1h produced a positive cyclic-coordinate diagnostic result.

D1i showed that this result is proxy-/threshold-/overstrictness-sensitive.

D1j showed that explicit emitted phase-like output fields are missing.

D1j also detected phase-related source/text mentions and proxy phase columns, suggesting that a transparent synthetic phase-field exposure extension is the next methodological step.

D1k is not a claim escalation. It is a source-exposure planning step for diagnostic synthetic phase-like fields.

## 4. Central question

Can a deterministic synthetic phase-field exposure extension make phase-like diagnostic fields visible enough to recheck cyclic-coordinate geometry beyond the D1h proxy baseline?

Can the cyclic geometry lead from D1h be re-evaluated after exposing transparent synthetic phase-like fields instead of relying only on `cyclic_phase_proxy`?

## 5. Why a deterministic synthetic phase-field exposure is needed

- D1j found no explicit phase output columns.
- D1j found proxy phase columns.
- D1j found phase-related source/text mentions.
- D1h currently depends on `cyclic_phase_proxy`.
- D1i showed proxy dependence and overstrictness warnings.
- D1k must therefore plan how phase-like synthetic fields can be exposed transparently.
- The exposed fields must be deterministic, reproducible, documented, and explicitly diagnostic.
- They must not be presented as physical phase reconstruction.

## 6. Source-to-phase exposure strategy

A. Existing emitted columns:

- if `phi_i` / `phi_j` / `delta_phi_wrapped` / `wrapped_delta_phi_abs` / `cos_delta_phi` / `sin_delta_phi` exist, expose/use them.

B. Existing synthetic parameters:

- if source/config contains phase-like parameters or angular phase component text, derive diagnostic synthetic phase fields from existing synthetic parameters.

C. Deterministic synthetic extension:

- if no latent phase parameters can be safely extracted, add a deterministic synthetic phase extension in a later implementation.
- This extension must be clearly labeled:

```yaml
phase_exposure_mode: deterministic_synthetic_phase_extension
phase_source_label: diagnostic_synthetic_phase_extension_v1
```

D. Proxy-only fallback:

- if extension is not allowed, retain:

```yaml
phase_exposure_mode: unavailable_proxy_only
```

## 7. Deterministic phase-field construction options

Option 1: `existing_generator_phase`

- use existing phase-like fields if found.

Option 2: `reconstructed_from_existing_synthetic_parameters`

- derive `phi_i` / `phi_j` from already existing synthetic generator parameters.

Option 3: `diagnostic_synthetic_phase_extension_v1`

- deterministic construction from stable case attributes, clearly marked synthetic.

Option 4: complex-trigonometric diagnostic embedding

- use real diagnostic components to define a phase-like angle:

```text
phi = atan2(B_component, A_component)
```

- only if A/B-like components are available and documented.

Option 5: `unavailable_proxy_only`

- no explicit phase; stop without fake phase.

D1k should prefer existing generator/synthetic parameters over arbitrary hash-like phase.

Hash-like phase should not be used as a physical or preferred phase. If used at all, it should be used only as a negative control or fallback.

## 8. Required exposed phase-like fields

A later implementation should expose at least these fields when construction is possible:

- `phi_i`
- `phi_j`
- `delta_phi_raw`
- `delta_phi_wrapped`
- `wrapped_delta_phi_abs`
- `normalized_angular_distance`
- `cos_phi_i`
- `sin_phi_i`
- `cos_phi_j`
- `sin_phi_j`
- `cos_delta_phi`
- `sin_delta_phi`
- `angular_phase_distance`
- `phase_source_label`
- `phase_exposure_mode`
- `phase_construction_rule`
- `phase_construction_inputs`
- `phase_is_synthetic_diagnostic`
- `phase_is_physical: false`

## 9. Phase-field formulas and wrapping conventions

Planned formula conventions:

```text
delta_phi_raw = phi_i - phi_j

delta_phi_wrapped = atan2(sin(delta_phi_raw), cos(delta_phi_raw))

wrapped_delta_phi_abs = abs(delta_phi_wrapped)

normalized_angular_distance = wrapped_delta_phi_abs / pi

cos_delta_phi = cos(delta_phi_wrapped)

sin_delta_phi = sin(delta_phi_wrapped)

cyclic_distance_cos_sin = sqrt((cos_phi_i - cos_phi_j)^2 + (sin_phi_i - sin_phi_j)^2) / 2
```

All angular quantities should be in radians.

The principal interval should be `(-pi, pi]`.

No physical phase interpretation is allowed.

## 10. Integration with cyclic geometry recheck

A later D1k implementation should support these recheck modes:

A. proxy baseline:

- D1h `cyclic_phase_proxy` baseline

B. exposed phase recheck:

- cyclic distance from exposed phase fields

C. cos/sin embedding recheck:

- use `cos_phi` / `sin_phi` and `cos_delta_phi` / `sin_delta_phi`

D. wrapped scalar recheck:

- use `normalized_angular_distance`

E. proxy-vs-exposed comparison:

- compare case-level and aggregate differences

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

## 11. Comparison against D1h/D1i/D1j baselines

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

D1j exposure audit:

```yaml
explicit_phase_source_available: false
detected_phase_columns: []
detected_proxy_phase_columns: cyclic_phase_distance, cyclic_phase_source
detected_phase_text_mentions: exist
explicit_phase_recheck_possible: false
deterministic_synthetic_phase_extension_needed: true
phase_exposure_mode: reconstructed_from_existing_synthetic_parameters_candidate
```

D1k should compare the later exposed phase recheck against all three baselines.

## 12. Overstrictness and intrusion re-audit after exposure

A later implementation should report:

- `stable_candidate_current_count`
- `stable_candidate_proxy_count`
- `stable_candidate_exposed_phase_count`
- `current_stable_and_exposed_phase_stable`
- `current_stable_but_exposed_phase_fragile`
- `current_fragile_but_exposed_phase_stable`
- `current_fragile_and_exposed_phase_fragile`
- `stable_candidate_loss_rate_exposed_phase`
- `retained_stable_candidate_rate_exposed_phase`
- `exposed_phase_overstrictness_warning`
- `exposed_phase_remaining_intrusion_warning`

Targeted remaining intrusions:

- `spectrum_matched_null`
- `adversarial_near_duplicate_sweep`
- `local_response_dominant`
- `strong_collision_penalties`
- `kernel_size_8`
- `impostor_overlap_warning`

## 13. Decision-table integration

Planned cautious labels:

- `phase_field_exposure_supported_candidate`
- `phase_field_exposure_missing_warning`
- `deterministic_synthetic_phase_extension_supported_candidate`
- `deterministic_synthetic_phase_extension_needed`
- `exposed_phase_geometry_reduces_false_accept_candidate`
- `exposed_phase_geometry_no_improvement_warning`
- `exposed_phase_overstrictness_warning`
- `proxy_vs_exposed_phase_mismatch_warning`
- `exposed_phase_remaining_intrusion_warning`
- `stable_retention_supported_candidate`
- `cos_sin_embedding_supported_candidate`
- `wrapped_scalar_supported_candidate`
- `mastermind_parked_not_implemented`
- `inconclusive`
- `failed_input_consistency_check`

No label may claim proof, physical identity, or established specificity.

## 14. Mastermind / Knuth / role-permutation parking note

Ralf/Nova noted a later variable-dimensional manifold / Knuth / Mastermind-style pairwise role-pruning idea:

- n can define the number of available diagnostic dimensions
- k can define local chart/combination size
- impossible or methodologically meaningless combinations can be excluded
- Knuth/Mastermind-style feedback can later search the reduced role-space
- this is not part of D1k
- it should be considered only after deterministic synthetic phase-field exposure and cyclic geometry recheck

## 15. Planned implementation design

A later implementation should:

- read D1f/D1h/D1j inputs
- inspect existing field availability
- derive or expose phase-like fields according to `phase_exposure_mode`
- if phase fields cannot be exposed transparently, stop with `phase_field_exposure_missing_warning`
- if deterministic synthetic phase extension is used, clearly mark it as synthetic diagnostic
- write a new phase-exposed case table, without modifying old D1f/D1h outputs
- rerun cyclic geometry classification using exposed phase fields
- compare against D1h proxy baseline
- re-audit overstrictness and remaining intrusions
- keep Mastermind parked
- do not modify any closed prior outputs

## 16. Planned output files for later implementation

Planned future files only. This D1k plan does not create them.

Future implementation inputs/templates:

- `data/qsb_st_comp01d1k_deterministic_synthetic_phase_field_exposure_config.yaml`
- `scripts/run_qsb_st_comp01d1k_deterministic_synthetic_phase_field_exposure.py`
- `docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_RESULT_NOTE_TEMPLATE.md`

Future run outputs:

- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/summary.json`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/readout.md`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_construction_audit.csv`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/exposed_phase_cyclic_recheck_summary.csv`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/proxy_vs_exposed_phase_comparison.csv`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/exposed_phase_overstrictness_summary.csv`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/exposed_phase_remaining_intrusion_summary.csv`
- `runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/resolved_config.json`

## 17. Continuous field list

| field name | field type | field description |
| --- | --- | --- |
| `run_id` | string | Planned D1k run identifier. |
| `case_id` | string | Case identifier carried from existing synthetic run outputs. |
| `phase_source_label` | string | Label for the exposed phase-like source. |
| `phase_exposure_mode` | enum | Exposure mode used for the row or run. |
| `phase_construction_rule` | string | Deterministic rule used to expose or construct the phase-like field. |
| `phase_construction_inputs` | list[string] | Input fields used by the construction rule. |
| `phase_is_synthetic_diagnostic` | boolean | Must be true for constructed synthetic phase-like fields. |
| `phase_is_physical` | boolean | Must be false. |
| `phi_i` | float/null | Diagnostic phase-like coordinate for item i. |
| `phi_j` | float/null | Diagnostic phase-like coordinate for item j. |
| `delta_phi_raw` | float/null | Raw phase-like difference before wrapping. |
| `delta_phi_wrapped` | float/null | Wrapped phase-like difference. |
| `wrapped_delta_phi_abs` | float/null | Absolute wrapped phase-like distance. |
| `normalized_angular_distance` | float/null | `wrapped_delta_phi_abs / pi`. |
| `cos_phi_i` | float/null | Cosine embedding of `phi_i`. |
| `sin_phi_i` | float/null | Sine embedding of `phi_i`. |
| `cos_phi_j` | float/null | Cosine embedding of `phi_j`. |
| `sin_phi_j` | float/null | Sine embedding of `phi_j`. |
| `cos_delta_phi` | float/null | Cosine of `delta_phi_wrapped`. |
| `sin_delta_phi` | float/null | Sine of `delta_phi_wrapped`. |
| `cyclic_distance_cos_sin` | float/null | Cos/sin cyclic distance. |
| `angular_phase_distance` | float/null | Diagnostic angular phase-like distance. |
| `baseline_cyclic_phase_proxy_distance` | float/null | D1h proxy cyclic distance. |
| `exposed_phase_cyclic_distance` | float/null | Exposed phase-like cyclic distance. |
| `proxy_vs_exposed_phase_distance_delta` | float/null | Difference between proxy and exposed phase-like distance. |
| `profile_distance_raw` | float/null | Existing D1f/D1h raw profile distance. |
| `control_overlap_rate` | float/null | Existing diagnostic control overlap rate. |
| `decoy_success_rate` | float/null | Existing diagnostic decoy success rate. |
| `cyclic_acceptance_distance_proxy` | float/null | Proxy-based cyclic acceptance distance. |
| `cyclic_acceptance_distance_exposed` | float/null | Exposed phase-based cyclic acceptance distance. |
| `false_accept_warning_proxy` | boolean | Proxy baseline false-accept warning flag. |
| `false_accept_warning_exposed` | boolean | Exposed phase recheck false-accept warning flag. |
| `exclusion_success_proxy` | boolean | Proxy baseline exclusion success flag. |
| `exclusion_success_exposed` | boolean | Exposed phase recheck exclusion success flag. |
| `stable_candidate_proxy` | boolean | Proxy baseline stable-candidate flag. |
| `stable_candidate_exposed` | boolean | Exposed phase stable-candidate flag. |
| `fragile_candidate_proxy` | boolean | Proxy baseline fragile-candidate flag. |
| `fragile_candidate_exposed` | boolean | Exposed phase fragile-candidate flag. |
| `stable_candidate_loss_rate_exposed` | float/null | Stable candidate loss rate under exposed phase recheck. |
| `exposed_phase_overstrictness_warning` | boolean | Whether exposed phase recheck appears overstrict. |
| `spectrum_matched_null_intrusion_warning` | boolean | Spectrum-matched null intrusion warning. |
| `adversarial_near_duplicate_intrusion_warning` | boolean | Adversarial near-duplicate intrusion warning. |
| `local_response_dominant_warning` | boolean | Local-response-dominant warning. |
| `kernel_size_8_artifact_warning` | boolean | Kernel-size-8 artifact warning. |
| `remaining_intrusion_warning` | boolean | General remaining-intrusion warning. |
| `mastermind_status` | string | Must remain `parked_not_implemented` for D1k. |
| `decision_status` | string | Cautious methodological decision label. |
| `warning_flags` | list[string] | Active warning flags. |
| `interpretation_note` | string | Bounded note separating finding, interpretation, hypothesis, open gap, and claim boundary. |

## 18. Acceptance criteria for later implementation

A later implementation should check at least:

- YAML config parses
- runner reads existing D1h/D1j summaries
- runner does not modify D1f/D1g/D1h/D1i/D1j outputs
- runner does not rerun D1f
- `phase_exposure_mode` is explicitly reported
- `phase_source_label` is explicitly reported
- `phase_is_synthetic_diagnostic` is explicitly reported
- `phase_is_physical` is false
- exposed phase fields are written if construction is possible
- if construction is not possible, result says `phase_field_exposure_missing_warning`
- phase formulas and wrapping convention are documented
- `phase_exposed_case_profile_summary.csv` parses
- cyclic geometry recheck with exposed phase fields is reported if possible
- proxy-vs-exposed comparison is reported if possible
- overstrictness and remaining intrusions are reported
- Mastermind status remains `parked_not_implemented`
- `specificity_established` remains false
- no decision label claims proof
- readout separates Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary
- claim-risk grep clean or only negated/Claim Boundary mentions
- `git diff --check` passes

## 19. Interpretation rules

Befund:

Were deterministic synthetic phase-like fields exposed, and can cyclic geometry be rechecked beyond proxy baseline?

Interpretation:

If exposed fields exist, does cyclic geometry remain useful with acceptable stable retention and reduced proxy dependence?

Hypothese:

Transparent diagnostic synthetic phase fields may allow a more meaningful cyclic-coordinate test than `cyclic_phase_proxy` alone.

Offene Lücke:

No physical validation, no real data, no specificity, no physical phase reconstruction, no physical manifold, no Lorentzian structure, no physical time, no Pauli claim.

## 20. Decision logic

Planned cautious labels:

- `phase_field_exposure_supported_candidate`
- `phase_field_exposure_missing_warning`
- `deterministic_synthetic_phase_extension_supported_candidate`
- `deterministic_synthetic_phase_extension_needed`
- `exposed_phase_geometry_reduces_false_accept_candidate`
- `exposed_phase_geometry_no_improvement_warning`
- `exposed_phase_overstrictness_warning`
- `proxy_vs_exposed_phase_mismatch_warning`
- `exposed_phase_remaining_intrusion_warning`
- `stable_retention_supported_candidate`
- `cos_sin_embedding_supported_candidate`
- `wrapped_scalar_supported_candidate`
- `mastermind_parked_not_implemented`
- `inconclusive`
- `failed_input_consistency_check`

No label may claim proof, physical identity, or established specificity.

## 21. What this plan must not do

- does not implement the D1k runner
- does not rerun D1f
- does not modify D1f/D1g/D1h/D1i/D1j outputs
- does not create config files
- does not create run outputs
- does not claim `cyclic_phase_proxy` is physical phase
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

## 22. Claim Boundary

D1k is a deterministic synthetic phase-field exposure extension planning document.

D1k plans to expose diagnostic synthetic phase-like fields for cyclic-geometry rechecking.

D1k does not rerun D1f.

D1k does not modify D1f, D1g, D1h, D1i, or D1j outputs.

D1k does not introduce a new identity score.

D1k does not establish diagnostic specificity.

cyclic_phase_proxy is diagnostic only.

Exposed synthetic phase-like fields, if later constructed, are diagnostic synthetic fields.

They are not physical phase reconstruction.

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

The D1k plan does not prove wave identity.

The D1k plan does not validate physical phase reconstruction.

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

COMP01-D1k does not attach D(A,B).

COMP01-D1k does not construct S_rel2.

COMP01-D1k does not derive a Lorentzian metric.

COMP01-D1k does not validate a physical Bridge.

COMP01-D1k does not establish diagnostic specificity.

This is synthetic diagnostic deterministic phase-field exposure extension planning only.

## 23. Current status label

current_status_label: COMP01D1K_deterministic_synthetic_phase_field_exposure_extension_plan_created
