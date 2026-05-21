# QSB-ST COMP01-D1m Multi-Channel Synthetic Phase Identity Profile — Result Note

## 1. Purpose

This result note documents the first D1m runner output for the multi-channel synthetic phase identity profile.

D1m operationalizes the multi-channel synthetic phase identity profile planned in the D1m plan and specified in the D1m runner specification. It reads existing D1j/D1k/D1l/D1h/D1f artifacts, joins available case-level rows by `case_id`, assembles ten diagnostic channels, and reports warning-qualified profile rows.

This documentation does not create validation of a physical model and does not establish diagnostic specificity. The D1m runner output is synthetic diagnostic documentation only. It does not introduce physical phase, physical wavefunction, physical spacetime geometry, Mastermind, Knuth, manifold search, role-permutation diagnostics, or new physics claims.

## 2. Inputs inspected

Plan/spec/config/runner inspected:

- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_PLAN.md`
- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RUNNER_SPEC.md`
- `data/qsb_st_comp01d1m_multi_channel_synthetic_phase_identity_profile_config.yaml`
- `scripts/run_qsb_st_comp01d1m_multi_channel_synthetic_phase_identity_profile.py`

D1j/k/l context documents inspected:

- `docs/QSB_ST_COMP01D1L_SYNTHETIC_PHASE_LEAKAGE_TAUTOLOGY_AUDIT_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1JKL_SYNTHETIC_PHASE_EXPOSURE_LEAKAGE_AUDIT_SYNTHESIS_NOTE.md`
- `docs/QSB_ST_COMP01D1J_EXPLICIT_PHASE_FIELD_EXPOSURE_CYCLIC_GEOMETRY_RECHECK_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1K_DETERMINISTIC_SYNTHETIC_PHASE_FIELD_EXPOSURE_EXTENSION_RESULT_NOTE.md`

D1m output artifacts inspected:

- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/summary.json`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/readout.md`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/profile_case_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/channel_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/control_family_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/warning_taxonomy_summary.csv`
- `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/resolved_config.json`

All expected D1m output artifacts were present and readable. No D1m runner rerun was needed.

## 3. Method summary

The D1m runner reads the configured D1j, D1k, D1l, D1h, and D1f artifacts through the D1m YAML config. It joins case-level tables by `case_id` and does not guess joins by row order.

The runner assembles ten diagnostic channels:

- phase exposure
- phase leakage
- residual mimicry
- duplicate sanity
- near-duplicate control
- component ablation
- shuffled-input sanity
- family-blind sanity
- threshold-weight robustness
- channel-specific separability

The runner writes `profile_case_summary.csv`, `channel_summary.csv`, `control_family_summary.csv`, `warning_taxonomy_summary.csv`, `summary.json`, `readout.md`, and `resolved_config.json`.

Mastermind, Knuth, and manifold search remain parked as `parked_not_implemented`.

## 4. Befund

The run joined all 9450 cases without join/input warnings, but all 9450 cases are warning-qualified as `diagnostic_profile_candidate_with_warnings`.

Machine-readable D1m summary values:

```yaml
case_count: 9450
joined_case_count: 9450
input_join_warning: false
missing_required_input_warning: false
missing_optional_input_warning: false
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
profile_channel_count: 10
active_warning_count: 11
single_channel_dominance_warning: false
profile_decision_label_counts:
  diagnostic_profile_candidate_with_warnings: 9450
mastermind_status: parked_not_implemented
knuth_status: parked_not_implemented
manifold_status: parked_not_implemented
runner_scope: synthetic diagnostic multi-channel profile skeleton
```

This is a successful operational result for the runner scaffold, but it is not a clean confirmation result. The central result quality is warning-qualified by design.

## 5. Channel-level result

The inspected `channel_summary.csv` reports:

```yaml
phase_exposure:
  mean_score: 1
  warning_count: 0
phase_leakage:
  mean_score: null
  warning_count: 9450
residual_mimicry:
  mean_score: 0.925767935149
  warning_count: 0
near_duplicate_control:
  mean_score: null
  warning_count: 8505
component_ablation:
  mean_score: 0.428571428571
  warning_count: 0
family_blind_sanity:
  mean_score: null
  warning_count: 9450
threshold_weight_robustness:
  mean_score: 0.52
  warning_count: 0
channel_specific_separability:
  mean_score: 0.71858484093
  warning_count: 0
```

The `profile_case_summary.csv` contains 9450 rows. In those rows, `dominant_channel_id` is `phase_exposure` for all inspected cases by aggregate count.

This does not automatically imply `single_channel_dominance_warning: true`. In the D1m runner, `dominant_channel_id` identifies the largest contributing numeric channel, while `single_channel_dominance_warning` is raised only when the dominance share crosses the warning threshold. Therefore `phase_exposure` can be the dominant channel while the aggregate `single_channel_dominance_warning` remains false, because several positive channels contribute to the guarded profile.

## 6. Warning-level result

The inspected `warning_taxonomy_summary.csv` reports `active_warning_count: 11`.

Active warnings:

- `overclean_result_warning`
- `direct_feature_leakage_warning`
- `construction_feedback_leakage_warning`
- `tautology_warning`
- `construction_dependence_warning`
- `component_ablation_failure_warning`
- `family_blind_interpretation_warning`
- `near_duplicate_intrusion_warning`
- `residual_mimicry_warning`
- `threshold_weight_instability_warning`
- `profile_aggregate_untrusted_warning`

The warning taxonomy is the main result-quality qualifier. Warnings are not hidden; they are carried into the machine-readable outputs and the readout.

## 7. Interpretation

D1m operationalizes the multi-channel profile successfully. The case join is complete, the runner produces all planned output artifacts, and the output is structured enough for the next audit/refinement step.

The result is warning-qualified, not a clean confirmation. This is scientifically useful because it prevents overclaiming: every case receives a diagnostic profile label, but every case also remains marked as `diagnostic_profile_candidate_with_warnings`.

D1m provides a usable diagnostic scaffold for refinement. It does not validate physical phase, physical wavefunction, physical spacetime geometry, or Bridge confirmation. It does not establish diagnostic specificity, and it should not be read as standalone cyclic-geometry evidence.

## 8. Hypothese

A multi-channel synthetic diagnostic profile may be a better working scaffold than a single phase-exposure score or single residual score, but D1m shows that this scaffold must remain warning-aware and control-sensitive.

The current profile preserves the D1j/k/l lesson: same-type but not-same wave cases should not be reduced to a single unguarded score.

## 9. Offene Lücke

- no real data
- no validation of a physical model
- no diagnostic specificity
- no physical phase reconstruction
- no physical wavefunction
- no physical spacetime geometry
- no physical time
- no Lorentzian metric
- no Hilbert-space reconstruction
- no Pauli/spin-statistics claim
- no Bridge confirmation
- active warnings remain
- outputs are currently in `runs/` and may be ignored by normal git status
- Mastermind / Knuth / manifold search still parked

## 10. Claim Boundary

This is synthetic diagnostic runner output only.

- no physical phase
- no physical manifold
- no physical model validation claim
- no diagnostic specificity
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- Mastermind, Knuth, manifold, and role-permutation remain parked

The D1m profile is a warning-qualified diagnostic scaffold. It is not a physical identity result, not a physical phase result, and not a Bridge confirmation.

## 11. Consequence for next step

Recommended next block:

`QSB-ST-COMP01-D1n D1m Output Audit and Runner Refinement Plan`

Purpose:

- audit whether the high warning load is driven mostly by inherited D1l warnings, near-duplicate logic, family-blind interpretation, threshold instability, or scoring design
- clarify the `dominant_channel_id` versus `single_channel_dominance_warning` distinction
- decide whether run outputs should be tracked with `git add -f` or left reproducible from config plus runner
- refine channel summary semantics if needed
- avoid physical claims

Mastermind, Knuth, and manifold search should remain parked until the D1m output semantics and warning load have been audited.

## 12. Files created / checked

Created by this task:

- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RESULT_NOTE.md`

Checked by this task:

- D1m plan, runner specification, config, and runner
- D1j/k/l context result and synthesis documents
- D1m `summary.json`
- D1m `readout.md`
- D1m `profile_case_summary.csv`
- D1m `channel_summary.csv`
- D1m `control_family_summary.csv`
- D1m `warning_taxonomy_summary.csv`
- D1m `resolved_config.json`

The D1m run outputs already exist under `runs/QSB-ST-COMP01D1M/multi_channel_synthetic_phase_identity_profile_open/`. They are probably ignored by normal git status because of `runs/` ignore behavior.
