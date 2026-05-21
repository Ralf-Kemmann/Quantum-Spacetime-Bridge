# QSB-ST COMP01-D1n D1m Output Audit and Runner Refinement — Result Note

## 1. Purpose

This result note documents the first D1n output audit/review runner result.

D1n reads existing D1m outputs and audits warning origin/granularity, channel semantics, dominance semantics, and output-tracking policy. It does not modify D1m, does not rerun D1m, and does not create validation of a physical model or diagnostic specificity.

This is synthetic diagnostic documentation only. It does not start Mastermind, Knuth, manifold search, role-permutation diagnostics, or new physics claims.

## 2. Inputs inspected

D1n plan/config/runner inspected:

- `docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_PLAN.md`
- `data/qsb_st_comp01d1n_d1m_output_audit_and_runner_refinement_config.yaml`
- `scripts/run_qsb_st_comp01d1n_d1m_output_audit_and_runner_refinement.py`

D1m context result/config/runner inspected:

- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RESULT_NOTE.md`
- `data/qsb_st_comp01d1m_multi_channel_synthetic_phase_identity_profile_config.yaml`
- `scripts/run_qsb_st_comp01d1m_multi_channel_synthetic_phase_identity_profile.py`

D1n output artifacts inspected:

- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/summary.json`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/readout.md`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/warning_origin_summary.csv`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/channel_semantics_audit.csv`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/dominance_semantics_audit.csv`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/output_tracking_policy.md`
- `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/resolved_config.json`

All expected D1n output artifacts were present and readable. No D1n rerun was needed.

## 3. Method summary

The D1n runner reads D1m `summary.json`, `readout.md`, `profile_case_summary.csv`, `channel_summary.csv`, `control_family_summary.csv`, and `warning_taxonomy_summary.csv`.

It classifies warning origin and warning granularity, audits channel score/warning semantics, audits `dominant_channel_id` versus `single_channel_dominance_warning`, and writes D1n `summary.json`, `readout.md`, audit CSVs, `output_tracking_policy.md`, and `resolved_config.json`.

Mastermind, Knuth, and manifold status remain `parked_not_implemented`.

## 4. Befund

Confirmed D1n summary values:

```yaml
block_id: QSB-ST-COMP01D1N
d1m_case_count: 9450
d1m_joined_case_count: 9450
d1m_active_warning_count: 11
d1m_warning_qualified_case_count: 9450
d1m_single_channel_dominance_warning: false
broadcast_warning_count: 9
case_level_warning_count: 2
channel_semantics_rows: 10
dominance_audit_rows: 6
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
mastermind_status: parked_not_implemented
knuth_status: parked_not_implemented
manifold_status: parked_not_implemented
output_tracking_recommendation: keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default
```

D1n turned the D1m warning load into a structured audit object. It did not reduce or remove warnings; it classified them.

## 5. Warning-origin result

Confirmed `warning_origin_counts`:

```yaml
claim_boundary_guard: 1
d1m_case_or_family_logic: 2
d1m_input_join: 4
d1m_interpretation_policy: 4
d1m_output_warning: 1
inherited_d1l_global: 6
```

Confirmed `warning_granularity_counts`:

```yaml
case_level: 2
channel_level: 2
claim_boundary: 1
global_broadcast: 9
input_level: 4
```

The inherited D1l global warnings form a major part of the warning taxonomy. D1m case/family logic contributes separate case-level warnings, especially the near-duplicate and residual-mimicry channels. D1m interpretation policy contributes policy-level/global warnings. Input-join warnings exist as taxonomy categories, but D1m had no active input/join problem in the inspected D1m run. The claim-boundary guard is tracked separately.

Confirmed aggregate warning placement:

```yaml
broadcast_warning_count: 9
case_level_warning_count: 2
```

## 6. Channel-semantics result

The inspected `channel_semantics_audit.csv` contains 10 channel audit rows.

Channels marked with `refinement_needed: true`:

- `phase_exposure`: clarify dominant-channel reporting and emit dominance share per row.
- `phase_leakage`: mark as global qualifier when `warning_count` is broadcast to all cases.
- `near_duplicate_control`: separate case-level near-duplicate warning from family-level ambiguity summary.
- `component_ablation`: mark aggregate-broadcast score origin explicitly.
- `family_blind_sanity`: separate family-blind survival flag from warning semantics.
- `threshold_weight_robustness`: expose threshold instability reason and score component count.
- `channel_specific_separability`: clarify that this is a derived summary channel, not independent evidence.

The audit identifies `component_ablation` and `threshold_weight_robustness` as aggregate/broadcast-like channels that need explicit origin marking. It also identifies `phase_leakage` as a global qualifier when its warning count is broadcast to all cases.

## 7. Dominance-semantics result

The inspected `dominance_semantics_audit.csv` contains 6 dominance audit rows.

Confirmed observed dominance count:

```yaml
dominant_channel_id: phase_exposure:9450
```

The audit clarifies that `dominant_channel_id` identifies the largest numeric channel per profile row. It does not by itself imply single-channel failure. `single_channel_dominance_warning` is threshold-based and remains false in D1m.

Recommended future clarifications:

- `dominant_channel_share`
- `single_channel_dominance_threshold`
- `dominance_interpretation_note`
- `dominance_warning_reason`

This distinction is important because all D1m profile rows can report `phase_exposure` as the largest numeric channel while the summary still reports `d1m_single_channel_dominance_warning: false`.

## 8. Output-tracking result

The inspected `output_tracking_policy.md` recommends a conservative repository policy:

- keep config+runner and result notes tracked
- do not force-add full `runs/` outputs by default
- for public review or reproducibility bundles, create a docs-side digest or force-add selected summary/readout outputs with explicit commit message
- do not silently rely on ignored outputs

The D1n run outputs already exist under `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/` and are probably ignored by normal git status because of `runs/` ignore behavior.

## 9. Interpretation

D1n successfully audits D1m output semantics. It clarifies that the high warning load is not a simple failure signal; it is a structured review object.

D1n identifies which warning categories are inherited/global, case/family-derived, interpretation-policy-related, input-level, output-specific, or claim-boundary guards. It also identifies runner/readout refinement targets before any scoring changes.

D1n supports a conservative next refinement step. It does not validate physical phase, physical wavefunction, physical spacetime geometry, or Bridge confirmation. It does not establish diagnostic specificity, and it does not remove D1m warnings.

## 10. Hypothese

D1n supports the working hypothesis that D1m's high warning load can be made methodically useful by separating warning origin, warning granularity, channel semantics, and dominance semantics before changing the profile score.

## 11. Offene Lücke

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
- D1n audits semantics but does not yet refine D1m runner behavior
- D1m warnings remain active
- D1n outputs are in `runs/` and may be ignored by normal git status
- Mastermind / Knuth / manifold search still parked

## 12. Claim Boundary

This is synthetic diagnostic audit output only.

- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- D1n does not modify D1m
- D1n does not rerun D1m
- Mastermind, Knuth, manifold, and role-permutation remain parked

The D1n result note documents output semantics. It is not a physical interpretation step.

## 13. Consequence for next step

Recommended next block:

`QSB-ST-COMP01-D1o D1m Runner Refinement Specification`

Purpose:

- specify concrete D1m runner refinements based on D1n findings
- add `dominant_channel_share` and `single_channel_dominance_threshold` fields
- split global inherited warnings from case-derived warnings
- clarify `phase_leakage` as global qualifier when broadcast
- clarify aggregate-broadcast channel score origins
- add `warning_origin` and `warning_granularity` metadata to D1m outputs
- preserve warning-qualified interpretation
- avoid physical claims

Mastermind, Knuth, and manifold search should remain parked.

## 14. Files created / checked

Created by this task:

- `docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_RESULT_NOTE.md`

Checked by this task:

- D1n plan, config, and runner
- D1m result note, config, and runner
- D1n `summary.json`
- D1n `readout.md`
- D1n `warning_origin_summary.csv`
- D1n `channel_semantics_audit.csv`
- D1n `dominance_semantics_audit.csv`
- D1n `output_tracking_policy.md`
- D1n `resolved_config.json`

The D1n run outputs already exist under `runs/QSB-ST-COMP01D1N/d1m_output_audit_and_runner_refinement_open/`. They are probably ignored by normal git status because of `runs/` ignore behavior.
