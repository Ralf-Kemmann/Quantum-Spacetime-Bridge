# QSB-ST COMP01 Wave Identity Fingerprint Parameter Space — Minimal Metric Runner Specification

## 1. Purpose

This is a runner specification for the minimal Wave Identity Fingerprint Metric route.

It creates no runner now, no config now, no data file now, no run output now, and no implementation now. It creates no D1q and does not continue D1-letter expansion.

This specification is diagnostic only. It creates no validation of a physical model and no diagnostic specificity.

## 2. Starting point from minimal metric spec

The minimal metric spec defines the object as a relational wave-pair fingerprint `R_ij`. The metric compares two relational fingerprints, for example `R_ij` and `R_kl`.

The compact coordinate `delta_phase` uses circular distance. Non-compact coordinates use normalized ordinary differences. The metric is diagnostic only.

Der Fingerprint-Raum ist der Messraum; der Identitäts-Raum muss nicht derselbe Raum sein.

Fingerprint-Raum is the measurement/projection space. Identitäts-Raum remains open.

## 3. Future block identity

```yaml
block_id: QSB-ST-COMP01-WIFM01
route_name: Wave Identity Fingerprint Metric
metric_version: wifm01_minimal_circular_phase_metric_v1
run_id: minimal_metric_open
```

WIFM01 starts a new route outside D1m-D1p. It is not D1q and is not a continuation of D1-letter expansion.

## 4. Future files

Future files, not created now:

- `data/qsb_st_comp01_wifm01_minimal_metric_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01_minimal_metric.py`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/`

This task creates none of those files.

## 5. Future config requirements

Future config must be explicit and non-hidden. Required conceptual structure:

```yaml
block_id: QSB-ST-COMP01-WIFM01
route_name: Wave Identity Fingerprint Metric
metric_version: wifm01_minimal_circular_phase_metric_v1
run_id: minimal_metric_open
output_dir: runs/QSB-ST-COMP01-WIFM01/minimal_metric_open
input_mode: inline_synthetic_cases
phase_period: 2π
coordinate_scales:
  delta_k: explicit_toy_scale
  slope_diff: explicit_toy_scale
  intercept_diff: explicit_toy_scale
  amplitude_diff: explicit_toy_scale
weights:
  delta_k: 1.0
  delta_phase: 1.0
  slope_diff: 1.0
  intercept_diff: 1.0
  amplitude_diff: 1.0
toy_cases:
  - same_relational_identity
  - phase_wrap_equivalent
  - same_looking_not_same_delta_k
  - same_looking_not_same_slope_intercept
  - mixed_ambiguity_case
claim_boundary:
  specificity_established: false
  phase_is_physical: false
  phase_is_synthetic_diagnostic: true
  physical_metric_established: false
  physical_compact_dimensions_established: false
  hilbert_space_reconstruction: false
  bridge_confirmation: false
  mastermind_status: parked_not_implemented
  knuth_status: parked_not_implemented
  manifold_status: parked_not_implemented
output_files:
  summary_json: summary.json
  readout_md: readout.md
  fingerprint_input_table_csv: fingerprint_input_table.csv
  pair_metric_comparison_csv: pair_metric_comparison.csv
  case_family_summary_csv: case_family_summary.csv
  metric_component_summary_csv: metric_component_summary.csv
  naive_vs_circular_phase_summary_csv: naive_vs_circular_phase_summary.csv
  resolved_config_json: resolved_config.json
```

All scales and weights must be explicit. The first implementation must not infer hidden scales or auto-tune weights.

## 6. Future input schema

The input table describes relational fingerprint records, not individual waves.

| field name | field type | description | required | interpretation boundary |
| --- | --- | --- | --- | --- |
| `fingerprint_id` | string | Stable identifier for one relational fingerprint row. | yes | Identifier only. |
| `case_family` | string | Toy case family name. | yes | Diagnostic grouping only. |
| `case_role` | string | Role inside the toy comparison, for example left/right/reference. | yes | Not an identity label. |
| `delta_k` | float | Non-compact spectral/wavenumber difference coordinate. | yes | Diagnostic coordinate only. |
| `delta_phase` | float | Compact phase-difference coordinate in radians. | yes | Must be interpreted modulo `2π`. |
| `slope_diff` | float | Non-compact local slope difference coordinate. | yes | Local diagnostic coordinate only. |
| `intercept_diff` | float | Non-compact local intercept difference coordinate. | yes | Local diagnostic coordinate only. |
| `amplitude_diff` | float | Non-compact amplitude difference coordinate. | yes | Diagnostic coordinate only. |
| `expected_relation` | string | Expected diagnostic relation for toy case review. | yes | Test expectation, not physical truth. |
| `notes` | string | Human-readable construction note. | no | Documentation only. |

## 7. Future pair-comparison schema

The runner compares pairs of relational fingerprints.

| field name | field type | description | required | interpretation boundary |
| --- | --- | --- | --- | --- |
| `pair_id` | string | Stable identifier for one comparison pair. | yes | Identifier only. |
| `left_fingerprint_id` | string | Left fingerprint row id. | yes | Link only. |
| `right_fingerprint_id` | string | Right fingerprint row id. | yes | Link only. |
| `case_family` | string | Toy case family for the comparison. | yes | Diagnostic grouping only. |
| `expected_relation` | string | Expected diagnostic behavior for this comparison. | yes | Test expectation only. |
| `naive_phase_delta` | float | Raw absolute phase delta before circular correction. | yes | Baseline diagnostic distance component. |
| `circular_phase_delta` | float | Circular phase delta after modulo handling. | yes | Compact-coordinate diagnostic component. |
| `naive_metric_distance` | float | Weighted metric distance using naive phase delta. | yes | Diagnostic contrast only. |
| `circular_metric_distance` | float | Weighted metric distance using circular phase delta. | yes | Diagnostic contrast only. |
| `distance_delta_naive_minus_circular` | float | Difference between naive and circular distances. | yes | Wrap-sensitivity diagnostic. |
| `diagnostic_decision_label` | string | Diagnostic label from allowed label set. | yes | Not a true/false identity claim. |
| `diagnostic_reason` | string | Short reason for label assignment. | yes | Review aid only. |
| `claim_boundary` | string | Boundary statement for the row. | yes | Prevents claim escalation. |

Allowed diagnostic labels:

- `metric_equivalent_expected`
- `phase_wrap_corrected_by_circular_metric`
- `noncompact_difference_preserved`
- `local_shape_difference_preserved`
- `mixed_ambiguity_preserved`
- `diagnostic_warning_review_needed`

These labels are diagnostic only, not true/false identity claims.

## 8. Metric computation requirements

The future runner must:

- compute naive phase delta as `abs(phi_left - phi_right)`
- compute circular phase delta with `d_phase(phi1, phi2) = min(|Δphi|, 2π - |Δphi|)`
- compute normalized non-compact deltas
- compute naive metric using naive phase delta
- compute circular metric using circular phase delta
- report component contributions
- output all scales and weights
- avoid auto-tuning weights
- avoid inferred physical units

Metric formula:

```text
d² = w_k ΔK² + w_phi ΔPhi² + w_s ΔS² + w_b ΔB² + w_a ΔA²
```

`ΔPhi` is either naive phase delta or circular phase delta depending on the metric variant.

The metric is a diagnostic compatibility metric in Fingerprint-Raum, not spacetime geometry.

## 9. Toy case requirements

| case_family | required fingerprints | required comparison | expected diagnostic behavior |
| --- | --- | --- | --- |
| `same_relational_identity` | at least two equivalent fingerprints | compare equivalent fingerprints | `circular_metric_distance` near 0 and label `metric_equivalent_expected` |
| `phase_wrap_equivalent` | one fingerprint near phase `0`, one near phase `2π` | compare wrap-equivalent fingerprints | `circular_phase_delta < naive_phase_delta` and label `phase_wrap_corrected_by_circular_metric` |
| `same_looking_not_same_delta_k` | similar phase but separated `delta_k` | compare same-looking phase with different non-compact coordinate | non-compact term preserves separation and label `noncompact_difference_preserved` |
| `same_looking_not_same_slope_intercept` | similar phase/k but changed local slope/intercept | compare local-shape shifted fingerprints | local terms preserve separation and label `local_shape_difference_preserved` |
| `mixed_ambiguity_case` | moderate mixed compact/non-compact changes | compare mixed-difference fingerprints | ambiguity is preserved and label `mixed_ambiguity_preserved` or review warning |

The runner must not force mixed cases into clean same/different identity labels.

## 10. Future output artifacts

Future output artifacts, not created now:

- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/readout.md`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/fingerprint_input_table.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/pair_metric_comparison.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/case_family_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/metric_component_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/naive_vs_circular_phase_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01/minimal_metric_open/resolved_config.json`

All outputs are diagnostic artifacts only.

## 11. Summary.json requirements

Future `summary.json` must include:

- `block_id`
- `run_id`
- `metric_version`
- `fingerprint_count`
- `comparison_pair_count`
- `case_family_count`
- `coordinate_names`
- `compact_coordinates`
- `noncompact_coordinates`
- `coordinate_scales`
- `weights`
- `phase_period`
- `phase_wrap_case_count`
- `phase_wrap_corrected_count`
- `noncompact_separation_case_count`
- `noncompact_separation_preserved_count`
- `mixed_ambiguity_case_count`
- `mixed_ambiguity_preserved_count`
- `naive_vs_circular_distance_delta_summary`
- `diagnostic_decision_label_counts`
- `specificity_established: false`
- `phase_is_physical: false`
- `phase_is_synthetic_diagnostic: true`
- `physical_metric_established: false`
- `physical_compact_dimensions_established: false`
- `hilbert_space_reconstruction: false`
- `bridge_confirmation: false`
- `mastermind_status: parked_not_implemented`
- `knuth_status: parked_not_implemented`
- `manifold_status: parked_not_implemented`

## 12. Readout.md requirements

Future readout must use:

```markdown
# QSB-ST COMP01-WIFM01 Minimal Wave Identity Fingerprint Metric — Readout

## 1. Purpose
## 2. Inputs
## 3. Metric definition
## 4. Toy cases
## 5. Naive vs circular phase comparison
## 6. Befund
## 7. Interpretation
## 8. Hypothese
## 9. Offene Lücke
## 10. Claim Boundary
## 11. Files created
```

The readout must state that the runner is diagnostic only, that no physical metric is established, and that Fingerprint-Raum remains a measurement/projection space.

## 13. Acceptance criteria for future implementation

Future implementation must satisfy:

- all future files are created
- all input schema fields are present
- all pair-comparison schema fields are present
- all required toy case families are represented
- `phase_wrap_equivalent` shows `circular_phase_delta < naive_phase_delta`
- `same_relational_identity` has `circular_metric_distance` near 0
- `same_looking_not_same_delta_k` remains separated by non-compact term
- `same_looking_not_same_slope_intercept` remains separated by local terms
- `mixed_ambiguity_case` remains ambiguity/review label
- `specificity_established` remains false
- `phase_is_physical` remains false
- `physical_metric_established` remains false
- `physical_compact_dimensions_established` remains false
- `hilbert_space_reconstruction` remains false
- `bridge_confirmation` remains false
- `git diff --check` passes
- no claim-risk forbidden phrases appear

## 14. Non-goals

- no implementation now
- no physical phase reconstruction
- no physical compact dimensions
- no spacetime metric
- no Lorentzian metric
- no Hilbert-space norm
- no proof of wave identity
- no diagnostic specificity
- no Bridge confirmation
- no D1q

## 15. Befund expected from this specification

This specification defines future runner I/O, toy cases, naive-vs-circular comparison, output schemas, and acceptance checks.

It prepares transparent implementation without hidden assumptions. It does not create a runner and does not produce numerical results.

## 16. Interpretation

This spec makes the next implementation reproducible and guards against confusing phase wrapping with true diagnostic distance.

It prepares diagnostic comparison only. It makes no physical geometry claim, no compact dimension claim, no wave identity proof, no Hilbert reconstruction, and no Bridge confirmation.

## 17. Hypothese

A circular/torus-aware metric implementation may expose whether relational wave-pair fingerprints behave more coherently than under naive Euclidean phase treatment, especially in phase-wrap and same-looking/not-same cases.

This remains a hypothesis only.

## 18. Offene Lücke

- no runner yet
- no config yet
- no data file yet
- no run output yet
- no numerical result yet
- no real data
- no physical model validation
- no diagnostic specificity
- no physical compact dimensions
- no physical phase reconstruction
- no physical wavefunction
- no Hilbert-space reconstruction
- no Lorentzian metric
- no physical spacetime geometry
- no Pauli/spin-statistics claim
- no Bridge confirmation
- identity space remains open
- metric weights remain diagnostic choices
- normalization scales must be made explicit in future config

## 19. Claim Boundary

- runner specification only
- no implementation
- no new scores calculated
- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- no physical compact dimensions
- no string compactification claim
- no Hilbert-space reconstruction
- no conversion of fingerprint metric into spacetime metric
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- physical_metric_established: false
- physical_compact_dimensions_established: false
- hilbert_space_reconstruction: false
- bridge_confirmation: false
- Mastermind, Knuth, manifold, and role-permutation remain parked

## 20. Next-step recommendation

Recommended next step:

`QSB-ST-COMP01-WIFM01 Minimal Metric Config + Runner Implementation`

Purpose:

- create the config
- create the runner
- generate tiny synthetic toy cases
- compute naive and circular metric distances
- write outputs
- make no physical claims

Implementation should use exactly the schemas specified here.

## 21. Files created / checked

Created by this task:

- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_RUNNER_SPEC.md`

Checked seed/spec/gate files:

- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md`
- `docs/QSB_ST_COMP01_D1M_D1P_CONSOLIDATION_AND_NEXT_STEP_GATE_NOTE.md`

Checked earlier COMP01-D wave-identity context files:

- `docs/QSB_ST_COMP01D_WAVE_IDENTITY_FINGERPRINT_OBSERVABLES_CONCEPT.md`
- `docs/QSB_ST_COMP01D1A_WAVE_IDENTITY_RESIDUAL_SCANNER_SPEC.md`
- `docs/QSB_ST_COMP01D1B_WAVE_IDENTITY_RESIDUAL_MINIMAL_SCANNER_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1C_WAVE_IDENTITY_RESIDUAL_CONTROL_STRESS_RESULT_NOTE.md`
