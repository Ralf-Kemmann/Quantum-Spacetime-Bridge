# QSB-ST COMP01-D1p D1o Refined Output Audit and Regression Check — Result Note

## 1. Purpose

This result note documents the D1p regression/audit check for D1o refined outputs against the original D1m outputs.

D1p audits whether D1o extends metadata and schema without changing core D1m row counts, case IDs, decision labels, or warning counts. It is a synthetic diagnostic audit document only.

D1p does not rerun D1m or D1o, does not modify D1m or D1o outputs, and does not create validation of a physical model or diagnostic specificity.

## 2. Inputs inspected

D1m/D1n/D1o context documents inspected:

- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1O_D1M_RUNNER_REFINEMENT_SPECIFICATION.md`
- `docs/QSB_ST_COMP01D1O_D1M_REFINED_MULTI_CHANNEL_PROFILE_RESULT_NOTE.md`

D1p implementation files inspected:

- `data/qsb_st_comp01d1p_d1o_refined_output_audit_regression_config.yaml`
- `scripts/run_qsb_st_comp01d1p_d1o_refined_output_audit_regression.py`

D1p output artifacts inspected:

- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/summary.json`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/readout.md`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/d1m_d1o_regression_summary.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/schema_extension_summary.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/decision_label_regression.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/warning_count_regression.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/dominance_share_distribution.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/output_tracking_recommendation.md`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/resolved_config.json`

## 3. Method summary

D1p reads the original D1m summary, profile, channel, and warning outputs, then reads the refined D1o summary, profile, channel, warning, dominance, and comparison outputs.

The audit compares row counts, case IDs, decision-label counts, and warning counts. It also checks D1o schema extensions, computes dominance-share distribution values, and writes D1p summary, readout, regression, schema, decision, warning, dominance, output-tracking, and resolved-config outputs.

The runner keeps Mastermind, Knuth, and manifold search parked as `parked_not_implemented`.

## 4. Befund

Confirmed D1p summary values:

```yaml
block_id: QSB-ST-COMP01D1P
audit_version: d1p_d1o_regression_check_v1
d1m_case_count: 9450
d1o_case_count: 9450
d1m_profile_row_count: 9450
d1o_profile_row_count: 9450
case_id_set_equal: true
profile_decision_label_counts_equal: true
active_warning_count_equal: true
d1o_schema_extended: true
d1o_required_metadata_present: true
regression_passed: true
regression_failure_count: 0
regression_warning_count: 0
rows_crossing_dominance_threshold: 0
dominant_channel_distribution:
  phase_exposure: 9450
dominance_share_min: 0.271317829457
dominance_share_max: 0.313455755499
dominance_share_mean: 0.27844693767536605
dominance_share_median: 0.27750981784100004
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
mastermind_status: parked_not_implemented
knuth_status: parked_not_implemented
manifold_status: parked_not_implemented
output_tracking_recommendation: keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default
```

D1p confirms that D1o extended metadata/schema while preserving D1m row count, case IDs, decision labels, and active warning count.

## 5. Regression result

`d1m_d1o_regression_summary.csv` has 15 rows. `regression_passed` is true and `regression_failure_count` is 0.

The following regression checks passed:

- `case_count_equal`
- `joined_case_count_equal`
- `profile_row_count_equal`
- `case_id_set_equal`
- `profile_decision_label_counts_equal`
- `active_warning_count_equal`

The core flags were preserved:

- `specificity_established` remains false
- `phase_is_physical` remains false
- `phase_is_synthetic_diagnostic` remains true

The D1m-output-not-modified assertion is operational and path-based: the D1p runner reads D1m outputs and writes only to the D1p output path. This is not a forensic filesystem guarantee.

## 6. Schema-extension result

`schema_extension_summary.csv` has 3 rows. `profile_case_summary.csv` is extended from 22 to 37 fields, with 15 profile fields added. The required profile, channel, and warning metadata are present, and the D1o schema extension check passed.

Added profile fields include:

- `dominant_channel_share`
- `single_channel_dominance_threshold`
- `dominance_warning_reason`
- `warning_origin_count_global`
- `warning_origin_count_case`
- `warning_origin_count_policy`
- `warning_origin_count_input`
- `warning_origin_count_claim_boundary`
- `profile_score_component_count`
- `aggregate_broadcast_component_count`
- `case_level_component_count`
- `profile_warning_origin_summary`
- `profile_warning_granularity_summary`
- `dominance_interpretation_note`
- `runner_refinement_version`

This schema extension is metadata-only and does not alter D1m result semantics.

## 7. Decision-label and warning-count result

`decision_label_regression.csv` has 1 row. `diagnostic_profile_candidate_with_warnings` remains 9450 in D1m and 9450 in D1o, with delta 0 and `passed: true`.

`warning_count_regression.csv` has 8 rows. active_warning_count remains 11 in D1m and 11 in D1o. D1o adds explicit warning metadata, while the warning-qualified output remains warning-qualified.

D1o did not turn warning-qualified rows into clean candidates.

## 8. Dominance-share distribution result

`dominance_share_distribution.csv` has 12 rows.

Confirmed dominance distribution values:

```yaml
row_count: 9450
nonblank_dominant_channel_share_count: 9450
rows_crossing_threshold: 0
threshold: 0.8
rows_with_dominant_channel_phase_exposure: 9450
dominant_channel_distribution:
  phase_exposure: 9450
dominance_share_min: 0.271317829457
dominance_share_max: 0.313455755499
dominance_share_mean: 0.27844693767536605
dominance_share_median: 0.27750981784100004
```

The dominance distribution is descriptive diagnostic metadata only. The D1p check confirms the D1o clarification: `phase_exposure` can remain the dominant channel in every row while no row crosses the single-channel dominance threshold.

## 9. Output-tracking result

The output-tracking recommendation remains:

`keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default`

D1p run outputs are in `runs/` and are probably ignored by normal git status because of repository ignore behavior.

Recommended repository behavior:

- track config, runner, plan/spec/result notes
- do not force-add full `runs/` outputs by default
- use a docs-side digest or selected forced summary/readout outputs only with explicit justification
- avoid relying silently on ignored `runs/` outputs

## 10. Interpretation

D1p confirms D1o is a metadata/schema refinement layer. It confirms that D1o did not change D1m row count, case IDs, decision labels, or active warning count.

D1p confirms that the D1o schema extensions are present and that no row crosses the single-channel dominance threshold in the refined D1o output.

This makes the D1m-D1o chain more audit-ready. It is not physical evidence, not a physical phase result, and not diagnostic specificity.

## 11. Hypothese

D1p supports the working hypothesis that the D1o metadata layer can make the D1m warning-qualified output more auditable while preserving original decisions and warning load.

## 12. Offene Lücke

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
- D1p is a regression/audit check, not a new diagnostic concept
- D1m warnings remain active
- D1p outputs are in `runs/` and may be ignored by normal git status
- Mastermind / Knuth / manifold search still parked

## 13. Claim Boundary

- synthetic diagnostic regression/audit output only
- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- no new score claim
- no conversion of warning-qualified rows into clean candidates
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- D1p does not modify original D1m outputs
- D1p does not modify D1o outputs
- D1p does not rerun D1m or D1o
- Mastermind, Knuth, manifold, and role-permutation remain parked

## 14. Consequence for next step

D1p should close the D1m-D1p technical hygiene chain. No D1q extension is recommended by default.

Recommended next block:

`QSB-ST-COMP01 D1m-D1p Consolidation and Next-Step Gate Note`

Purpose:

- summarize D1m through D1p in one compact gate note
- state what the line achieved
- state what it did not achieve
- freeze the no-further-D1-letter-extension rule unless externally required
- prepare transition to a new route, for example wave-identity fingerprint / next-route seed
- preserve defensive claim boundaries
- avoid further formalism creep

No further D1-letter extension unless externally required.

## 15. Files created / checked

Created by this documentation task:

- `docs/QSB_ST_COMP01D1P_D1O_REFINED_OUTPUT_AUDIT_REGRESSION_RESULT_NOTE.md`

Checked context and implementation files:

- `docs/QSB_ST_COMP01D1M_MULTI_CHANNEL_SYNTHETIC_PHASE_IDENTITY_PROFILE_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1N_D1M_OUTPUT_AUDIT_AND_RUNNER_REFINEMENT_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01D1O_D1M_RUNNER_REFINEMENT_SPECIFICATION.md`
- `docs/QSB_ST_COMP01D1O_D1M_REFINED_MULTI_CHANNEL_PROFILE_RESULT_NOTE.md`
- `data/qsb_st_comp01d1p_d1o_refined_output_audit_regression_config.yaml`
- `scripts/run_qsb_st_comp01d1p_d1o_refined_output_audit_regression.py`

Checked D1p run outputs:

- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/summary.json`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/readout.md`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/d1m_d1o_regression_summary.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/schema_extension_summary.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/decision_label_regression.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/warning_count_regression.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/dominance_share_distribution.csv`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/output_tracking_recommendation.md`
- `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/resolved_config.json`

D1p run outputs already exist under `runs/QSB-ST-COMP01D1P/d1o_refined_output_audit_regression_open/` and are probably ignored by normal git status because of `runs/` ignore behavior.
