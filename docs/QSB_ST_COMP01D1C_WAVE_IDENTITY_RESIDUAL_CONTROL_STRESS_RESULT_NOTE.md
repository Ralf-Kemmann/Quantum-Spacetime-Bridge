# QSB-ST-COMP01-D1c Wave Identity Residual Control-Stress Result Note

## 1. Purpose

This file documents the D1c control-stress and weight-sensitivity run for `wave_identity_residual`.

It is documentation of an existing synthetic stress run in:

`runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/`

This note does not introduce a new run, does not change the implementation, and does not provide physical evidence. It is also not a positive specificity result.

## 2. Current status anchor

Current context:

- COMP01-D Concept documented
- COMP01-D1 Minimal Design Plan documented
- COMP01-D1a Scanner Specification documented
- COMP01-D1b Minimal Scanner implemented and result documented
- COMP01-D1c Control-Stress Plan documented
- COMP01-D1c Control-Stress Runner implemented

Current commit anchor:

`495906e Add QSB-ST COMP01D1c wave identity residual control stress runner`

## 3. Run inputs and generated outputs

Run directory:

`runs/QSB-ST-COMP01D1C/wave_identity_residual_control_stress_open/`

Generated output files:

- `summary.json`
- `readout.md`
- `pair_weight_sweep_summary.csv`
- `control_family_summary.csv`
- `weight_set_summary.csv`
- `decision_summary.csv`
- `resolved_config.json`

This result note was prepared from the existing run outputs. No new scanner run was performed for this documentation step.

## 4. Befund

Summary values:

```yaml
pair_count: 16
weight_set_count: 7
row_count: 112
expected_row_count: 112
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed_all_weight_sets: true
min_wave_identity_residual: 0.0
mean_wave_identity_residual: 0.16744211351696078
max_wave_identity_residual: 0.5433983480436639
control_mimicry_warnings_count: 68
residual_matched_warnings_count: 7
weight_sensitivity_warnings_count: 8
```

Decision counts:

```yaml
duplicate_sanity_pass: 7
near_duplicate_decoy_detected: 33
control_mimicry_warning: 55
residual_matched_decoy_warning: 7
adversarial_decoy_warning: 7
weight_sensitive_residual_warning: 1
inconclusive: 2
```

Observed result:

- Exact duplicate sanity passed across all weight sets.
- The full sweep completed: 16 pairs x 7 weight sets = 112 rows.
- Substantial control mimicry warnings were observed.
- `residual_matched_decoy` and `adversarial_near_duplicate` produced explicit warnings.
- `specificity_established` remains false.

## 5. Interpretation

D1c does not support a specificity reading of `wave_identity_residual` as a standalone marker.

D1c identifies substantial control mimicry risk under harder synthetic controls. The residual is technically computable and sanity-stable, but under control stress it is easily imitated or control-sensitive.

Deutsch:

Der Fingerabdruck ist berechenbar, aber faelschbar. Deshalb darf der Residual nicht als einzelner Identitaetsmarker gelesen werden.

The current result is a brake result. It says that absolute residual magnitude alone is not enough.

## 6. Hypothese

`wave_identity_residual` could remain useful as one part of a broader diagnostic control profile.

The important object may not be the absolute residual alone, but the residual behavior under:

- weight sweeps
- residual-matched decoys
- adversarial near duplicates
- harder control families

A later block should therefore inspect residual profile stability and control-profile response, not only residual magnitude.

## 7. Offene Lücke

- no real data
- no physical validation
- no diagnostic specificity established
- no robust null-model separation
- no physical wave identity established
- no Lorentzian structure
- no physical time
- no physical wavefunction claim
- no Pauli or spin-statistics claim
- no Bridge validation

## 8. Control mimicry and residual-matching warning

The 68 `control_mimicry_warning` rows and 7 `residual_matched_decoy_warning` rows are the central result, not a side result.

The control-stress run shows that `wave_identity_residual` can be mimicked by synthetic controls and therefore must not be interpreted as a standalone specificity marker.

`residual_matched_decoy` shows that a control can artificially reach a similar residual range.

`adversarial_near_duplicate` shows that coordinated small changes can make the residual misleadingly small or warning-worthy.

This is not a failure of the run. It is the methodological signal the D1c run was built to expose.

## 9. Weight-sensitivity warning

```yaml
weight_sensitivity_warnings_count: 8
```

Weight changes influence parts of the residual profile. Therefore weights are not merely technical parameters; they are methodological stress axes.

Weight sensitivity is a methodological stress test, not a physical parameter fit.

The result means later work must report weight behavior explicitly instead of hiding it inside one aggregate score.

## 10. Machine-readable status

```yaml
block_id: QSB-ST-COMP01D1C
run_id: wave_identity_residual_control_stress_open
commit_anchor: 495906e
pair_count: 16
weight_set_count: 7
row_count: 112
expected_row_count: 112
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed_all_weight_sets: true
control_mimicry_warnings_count: 68
residual_matched_warnings_count: 7
weight_sensitivity_warnings_count: 8
min_wave_identity_residual: 0.0
mean_wave_identity_residual: 0.16744211351696078
max_wave_identity_residual: 0.5433983480436639
current_status_label: COMP01D1C_wave_identity_residual_control_stress_result_documented
```

## 11. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- wave_identity_residual is a diagnostic distinguishability construct, not a physical observable by itself.
- The D1c result does not support wave_identity_residual as a standalone specificity marker.
- control mimicry warnings are methodological warnings, not failures of physics.
- weight sensitivity is a methodological stress test, not a physical parameter fit.
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
- This is synthetic diagnostic control-stress result documentation only.

## 12. Current status label

current_status_label: COMP01D1C_wave_identity_residual_control_stress_result_documented
