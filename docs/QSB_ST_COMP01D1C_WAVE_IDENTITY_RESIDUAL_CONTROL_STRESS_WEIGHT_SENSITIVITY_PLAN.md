# QSB-ST-COMP01-D1c Wave Identity Residual Control-Stress and Weight-Sensitivity Plan

## 1. Purpose

COMP01-D1c is a plan block for later stress tests of the already implemented COMP01-D1b minimal scanner.

D1c does not create a scanner, does not create a config, does not create runs, and does not create result data. It only plans:

- weight sensitivity of `wave_identity_residual`
- harder synthetic controls
- a check of whether `control_mimicry_warning` remains stable, can be reduced, or becomes stronger

The purpose is methodological. D1c is not a validation block and does not make physical claims.

## 2. Current status anchor

Current project chain:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Implementation Plan documented
- COMP01-D1b Minimal Scanner implemented
- COMP01-D1b Result Note documented

Current commit anchor:

`8e2c777 Add QSB-ST COMP01D1b wave identity residual result note`

D1b result values:

```yaml
pair_count: 7
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed: true
min_wave_identity_residual: 0.0
mean_wave_identity_residual: 0.09883413066168968
max_wave_identity_residual: 0.2944441465335814
control_mimicry_warnings_count: 2
```

D1b decision counts:

```yaml
duplicate_sanity_pass: 1
near_duplicate_decoy_detected: 4
control_mimicry_warning: 2
```

## 3. Motivation from D1b result

The D1b minimal runner showed that `wave_identity_residual` is technically computable and that the exact duplicate sanity check passed.

But the two `control_mimicry_warning` cases are the central brake result.

D1c must not treat D1b as a positive specificity result. D1c starts from the control mimicry warnings as the main methodological signal.

The next question is therefore not whether the residual is already useful, but whether the residual remains controlled under explicit weight variation and harder synthetic null/control families.

## 4. Central methodological problem

Central problem:

Is `wave_identity_residual` robust against weight choices and harder controls, or can the residual be easily imitated by synthetic control families?

Deutsch:

Trägt der Residual wirklich eine Wellenidentitätsinformation, oder ist er nur eine hübsche Aggregation aus `delta_k`, phase drift und lokalen slope/intercept-Unterschieden?

This plan treats that as an open diagnostic question.

## 5. Stress-test scope

D1c plans two later stress-test axes:

A. Weight sensitivity:

- same wave-pair families
- multiple explicit weight sets
- compare residual ranks and residual shifts against `equal_weights`

B. Control stress:

- more synthetic controls
- harder control families
- explicit reporting of whether controls imitate, amplify, or weaken the residual pattern

Out of scope:

- no real data
- no physical validation
- no new theoretical claims

## 6. Weight-sensitivity plan

Planned weight sets:

```yaml
equal_weights:
  spectral_component: 0.3333333333
  phase_component: 0.3333333333
  local_component: 0.3333333333

spectral_dominant:
  spectral_component: 0.60
  phase_component: 0.20
  local_component: 0.20

phase_dominant:
  spectral_component: 0.20
  phase_component: 0.60
  local_component: 0.20

local_dominant:
  spectral_component: 0.20
  phase_component: 0.20
  local_component: 0.60

spectral_off:
  spectral_component: 0.00
  phase_component: 0.50
  local_component: 0.50

phase_off:
  spectral_component: 0.50
  phase_component: 0.00
  local_component: 0.50

local_off:
  spectral_component: 0.50
  phase_component: 0.50
  local_component: 0.00
```

Planning rules:

- All weights must later be explicitly documented in config and output.
- No hidden score logic is allowed.
- Every weight set must keep `specificity_established=false` unless a later explicit criterion is defined and met.
- The later runner must report residual shifts versus `equal_weights`.
- The later runner must report whether `control_mimicry_warning` is weight-stable or weight-dependent.

## 7. Control-stress plan

Planned additional control families:

- `stronger_label_shuffle`: applies stronger label disruption than the D1b `label_shuffle` proxy to test whether the residual mainly tracks label mismatch.
- `phase_randomized_control`: randomizes phase-like parameters while keeping other simple parameters constrained.
- `spectrum_matched_control`: preserves spectral or `k`-distribution features while disrupting relational pairing.
- `amplitude_matched_control`: preserves amplitude-like A/B scale while changing pair identity.
- `slope_intercept_matched_control`: preserves local slope/intercept ranges while disrupting relational identity.
- `residual_matched_decoy`: tests whether a control can artificially produce a similar `wave_identity_residual` while not representing the same relational identity.
- `adversarial_near_duplicate`: tests whether coordinated small changes in `k`, phase, `A`, and `B` can make the residual misleadingly small or misleadingly structured.
- `random_parameter_control`: samples broad synthetic parameter combinations to estimate baseline residual behavior.

Special focus:

- `residual_matched_decoy` checks whether a control can be engineered to match the residual magnitude.
- `adversarial_near_duplicate` checks whether small coordinated changes can fool the residual.

## 8. Planned synthetic families

Baseline / sanity:

- `exact_duplicate`
- `simple_near_duplicate`

D1b carry-over:

- `small_delta_k_decoy`
- `small_phase_drift_decoy`
- `amplitude_preserved_perturbation`
- `combined_near_duplicate_decoy`
- `label_shuffle`
- `kernel_node_label_shuffle_proxy`

D1c harder controls:

- `stronger_label_shuffle`
- `phase_randomized_control`
- `spectrum_matched_control`
- `amplitude_matched_control`
- `slope_intercept_matched_control`
- `residual_matched_decoy`
- `adversarial_near_duplicate`
- `random_parameter_control`

## 9. Planned output files for later implementation

Planned future repo files:

- `data/qsb_st_comp01d1c_wave_identity_residual_control_stress_config.yaml`
- `scripts/run_qsb_st_comp01d1c_wave_identity_residual_control_stress.py`
- `docs/QSB_ST_COMP01D1C_WAVE_IDENTITY_RESIDUAL_CONTROL_STRESS_RESULT_NOTE_TEMPLATE.md`

Planned future run outputs:

- `runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/summary.json`
- `runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/readout.md`
- `runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/pair_weight_sweep_summary.csv`
- `runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/control_family_summary.csv`
- `runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/weight_set_summary.csv`
- `runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/decision_summary.csv`
- `runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/resolved_config.json`

This D1c plan creates none of those files.

## 10. Continuous field list

| field name | field type | field description |
| --- | --- | --- |
| `weight_set_id` | string | Identifier for the explicit weight set. |
| `spectral_weight` | number | Weight applied to the spectral component. |
| `phase_weight` | number | Weight applied to the phase component. |
| `local_weight` | number | Weight applied to the local slope/intercept component. |
| `pair_id` | string | Synthetic pair identifier. |
| `wave_id_i` | string | First diagnostic wave/pattern identifier. |
| `wave_id_j` | string | Second diagnostic wave/pattern identifier. |
| `control_family` | string | Synthetic family or control family. |
| `control_seed` | integer/null | Optional deterministic seed for generated controls. |
| `k_i` | number | First wave/pattern k parameter. |
| `k_j` | number | Second wave/pattern k parameter. |
| `delta_k` | number | Absolute k difference. |
| `relative_k_shift` | number | Normalized k difference with denominator protection. |
| `phase_i` | number | First phase-like parameter. |
| `phase_j` | number | Second phase-like parameter. |
| `relative_phase_drift` | number | Wrapped absolute phase drift. |
| `phase_gradient_delta` | number | Synthetic phase-gradient proxy difference. |
| `A_i` | number | First local intercept coefficient in the real diagnostic form. |
| `A_j` | number | Second local intercept coefficient in the real diagnostic form. |
| `B_i` | number | First local sine coefficient in the real diagnostic form. |
| `B_j` | number | Second local sine coefficient in the real diagnostic form. |
| `intercept_i` | number | Local intercept for first pattern. |
| `intercept_j` | number | Local intercept for second pattern. |
| `delta_intercept_ij` | number | Absolute intercept difference. |
| `slope_i` | number | Local slope proxy for first pattern. |
| `slope_j` | number | Local slope proxy for second pattern. |
| `delta_slope_ij` | number | Absolute slope difference. |
| `spectral_component` | number | Normalized spectral residual component. |
| `phase_component` | number | Normalized phase residual component. |
| `local_component` | number | Normalized local residual component. |
| `wave_identity_residual` | number | Transparent weighted diagnostic residual. |
| `residual_rank_within_weight_set` | integer | Rank of residual inside one weight set. |
| `residual_shift_vs_equal_weights` | number | Difference from the equal-weights residual for the same pair/control. |
| `control_reference_ratio` | number/null | Control residual divided by the configured reference residual. |
| `control_mimicry_warning` | boolean | Whether the control imitates or exceeds the configured reference behavior. |
| `residual_matched_warning` | boolean | Whether a decoy matches the target residual too closely. |
| `weight_sensitivity_flag` | string | Flag describing weight-stable or weight-sensitive behavior. |
| `decision_status` | string | Conservative decision label. |
| `warning_flags` | string/list | Explicit warnings, never hidden. |
| `interpretation_note` | string | Short diagnostic interpretation note. |

## 11. Acceptance criteria for later implementation

Future implementation is accepted only if:

- YAML config parses.
- Runner runs without external real data.
- all planned outputs exist.
- CSVs parse with `csv.DictReader`.
- every pair appears under every `weight_set_id`.
- `exact_duplicate` remains near-zero for all weight sets.
- `specificity_established` remains false.
- `control_mimicry_warnings_count` is reported per weight set.
- residual shift versus `equal_weights` is reported.
- no decision label claims proof.
- readout separates Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary.
- claim-risk grep is clean or contains only negated / Claim Boundary mentions.
- `git diff --check` passes.

## 12. Interpretation rules

Befund:

What changes under weight variation and harder controls?

Interpretation:

Do controls imitate, weaken, or amplify the residual pattern?

Hypothese:

Could `wave_identity_residual` remain useful as a diagnostic search axis?

Offene Lücke:

No physical validation, no real data, no specificity, no Lorentzian structure, no physical time, no Pauli claim.

## 13. Decision logic

Planned conservative decision labels:

- `duplicate_sanity_pass`
- `duplicate_sanity_fail`
- `weight_stable_residual_candidate`
- `weight_sensitive_residual_warning`
- `control_mimicry_warning`
- `residual_matched_decoy_warning`
- `adversarial_decoy_warning`
- `inconclusive`
- `failed_sanity_check`

No label may claim proof, proven status, or validation.

## 14. What this plan must not do

- does not implement the stress runner
- does not create config files
- does not create run outputs
- does not interpret D1b as specificity
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

## 15. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- wave_identity_residual is a diagnostic distinguishability construct, not a physical observable by itself.
- weight sensitivity is a methodological stress test, not a physical parameter fit.
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
- COMP01-D1c does not attach D(A,B).
- COMP01-D1c does not construct S_rel2.
- COMP01-D1c does not derive a Lorentzian metric.
- COMP01-D1c does not validate a physical Bridge.
- COMP01-D1c does not establish diagnostic specificity.
- This is synthetic diagnostic control-stress and weight-sensitivity planning only.

## 16. Current status label

current_status_label: COMP01D1C_wave_identity_residual_control_stress_weight_sensitivity_plan_created
