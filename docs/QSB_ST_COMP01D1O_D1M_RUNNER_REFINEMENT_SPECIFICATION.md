# QSB-ST COMP01-D1o D1m Runner Refinement — Specification

## 1. Purpose

D1o is a specification for future refinement of the D1m runner based on the D1n audit findings.

This document specifies what a later refinement should change in the D1m output schema and readout semantics. It does not implement a runner now, does not change configs now, does not rerun D1m or D1n now, and creates no new outputs now.

D1o is synthetic diagnostic specification only. It creates no validation of a physical model and no diagnostic specificity.

## 2. Starting point from D1n

D1n audited existing D1m outputs and found that the D1m warning load is structured, not a simple failure signal.

Confirmed D1n/D1m anchor values:

```yaml
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
```

Confirmed D1n warning-origin counts:

```yaml
claim_boundary_guard: 1
d1m_case_or_family_logic: 2
d1m_input_join: 4
d1m_interpretation_policy: 4
d1m_output_warning: 1
inherited_d1l_global: 6
```

Confirmed D1n warning-granularity counts:

```yaml
case_level: 2
channel_level: 2
claim_boundary: 1
global_broadcast: 9
input_level: 4
```

D1n found `dominant_channel_id` observed as `phase_exposure:9450`. It also clarified that `dominant_channel_id` identifies the largest numeric channel per profile row, while `single_channel_dominance_warning` is threshold-based and remains false in D1m.

D1n output tracking recommendation:

`keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default`

The inspected D1m/D1n outputs live under `runs/` and may be ignored by normal git status because of repository ignore behavior.

## 3. Refinement goals

Future D1m runner refinement should:

- make D1m output semantics clearer
- separate warning origins
- separate warning granularities
- separate global inherited warnings from case-derived warnings
- clarify broadcast warnings
- clarify aggregate-broadcast scores
- clarify dominance semantics
- improve reviewer readability
- preserve warning-qualified interpretation
- keep D1m reproducible from config plus runner

The aim is transparent semantics, not nicer-looking results.

## 4. Non-goals

D1o explicitly does not specify:

- physical claims
- physical phase
- physical wavefunction
- physical spacetime geometry
- diagnostic specificity
- Bridge confirmation
- Mastermind/Knuth/manifold
- role-permutation diagnostics
- score tuning for nicer results
- hiding warnings
- conversion of warning-qualified rows into clean candidates

## 5. Required D1m runner schema refinements

Future D1m `profile_case_summary.csv` should add the fields below without breaking existing field names where possible.

| field name | field type | description | source / calculation | interpretation boundary |
| --- | --- | --- | --- | --- |
| `dominant_channel_share` | float | Share contributed by the dominant numeric channel. | Largest numeric channel contribution divided by summed positive numeric channel contributions. | Descriptive diagnostic metadata only. |
| `single_channel_dominance_threshold` | float | Threshold used to raise `single_channel_dominance_warning`. | Config value or runner constant. | Threshold metadata, not physics. |
| `dominance_warning_reason` | string | Explanation for why dominance warning is active or inactive. | Derived from `dominant_channel_share` and threshold comparison. | Prevents reading dominant channel label as failure by itself. |
| `warning_origin_count_global` | integer | Count of active global inherited/broadcast warnings on the row. | Count active warnings with `warning_origin` or `warning_granularity` mapped to global/broadcast. | Qualifies interpretation; not a classifier proof. |
| `warning_origin_count_case` | integer | Count of active case-derived warnings on the row. | Count active warnings with case-level granularity. | Diagnostic caution only. |
| `warning_origin_count_policy` | integer | Count of active interpretation-policy warnings on the row. | Count active warnings with `d1m_interpretation_policy` origin. | Policy qualifier only. |
| `warning_origin_count_input` | integer | Count of active input/join warnings on the row. | Count active input-level warnings. | Input quality metadata only. |
| `warning_origin_count_claim_boundary` | integer | Count of active claim-boundary guard warnings. | Count active claim-boundary warnings. | Claim-boundary guard only. |
| `profile_score_component_count` | integer | Number of numeric components contributing to the profile score. | Count nonblank numeric score channels used in the row. | Helps detect thin scores; not physical support. |
| `aggregate_broadcast_component_count` | integer | Number of aggregate/broadcast components used in the row. | Count components whose source is aggregate broadcast rather than case-level. | Prevents false case-level reading. |
| `case_level_component_count` | integer | Number of case-level components used in the row. | Count components derived from case-level rows. | Diagnostic source metadata. |
| `profile_warning_origin_summary` | string | Compact origin summary for active row warnings. | Stable semicolon-separated origin counts. | Human/machine readability aid only. |
| `profile_warning_granularity_summary` | string | Compact granularity summary for active row warnings. | Stable semicolon-separated granularity counts. | Human/machine readability aid only. |

## 6. Warning-origin and warning-granularity refinements

Future D1m outputs should add `warning_origin` and `warning_granularity` metadata at least to:

- `warning_taxonomy_summary.csv`
- `profile_case_summary.csv` or a companion `profile_warning_summary.csv`
- `readout.md` warning summary
- `summary.json` aggregate counts

Allowed `warning_origin` values:

- `inherited_d1l_global`
- `d1m_case_or_family_logic`
- `d1m_interpretation_policy`
- `d1m_input_join`
- `claim_boundary_guard`
- `d1m_output_warning`

Allowed `warning_granularity` values:

- `global_broadcast`
- `case_level`
- `family_level`
- `channel_level`
- `input_level`
- `claim_boundary`
- `aggregate_policy`

Future D1m `summary.json` should report:

- `warning_origin_counts`
- `warning_granularity_counts`
- `broadcast_warning_count`
- `case_level_warning_count`
- `family_level_warning_count`
- `channel_level_warning_count`
- `input_level_warning_count`
- `claim_boundary_warning_count`

These metadata fields should make global broadcasts visible instead of letting them look like independent case-level findings.

## 7. Dominance-semantics refinements

Future D1m should emit:

- `dominant_channel_id`
- `dominant_channel_share`
- `single_channel_dominance_threshold`
- `single_channel_dominance_warning`
- `dominance_warning_reason`
- `dominance_interpretation_note`

Interpretation:

- `dominant_channel_id` is descriptive.
- `dominant_channel_share` is quantitative.
- `single_channel_dominance_warning` is threshold-based.
- `dominance_warning_reason` explains warning/no-warning.
- `dominance_interpretation_note` prevents reading dominance as physical evidence or failure by itself.

The D1n audit shows why this matters: `dominant_channel_id` was `phase_exposure:9450`, while `d1m_single_channel_dominance_warning: false` remained the summary-level result.

## 8. Channel-semantics refinements

`phase_exposure`:

- clarify dominant-channel reporting
- emit share metadata
- keep synthetic diagnostic boundary

`phase_leakage`:

- mark as global qualifier if `warning_count` is broadcast to all cases
- do not treat as case-level evidence unless case-level leakage exists

`residual_mimicry`:

- expose source columns and threshold/logic
- distinguish score availability from warning activation

`duplicate_sanity`:

- preserve as control channel
- clarify when blank `mean_score` is intentional

`near_duplicate_control`:

- split case-level near-duplicate warnings from family-level ambiguity summary

`component_ablation`:

- mark aggregate-broadcast score origin explicitly
- avoid implying case-specific ablation if not case-level

`shuffled_input_sanity`:

- clarify survival flag semantics and missing-score behavior

`family_blind_sanity`:

- separate family-blind survival from warning semantics
- interpret with leakage and ablation

`threshold_weight_robustness`:

- expose threshold instability reason
- expose score component count

`channel_specific_separability`:

- mark as derived summary channel
- avoid reading as independent evidence

## 9. Summary.json refinements

Future D1m `summary.json` should add at least:

- `warning_origin_counts`
- `warning_granularity_counts`
- `broadcast_warning_count`
- `case_level_warning_count`
- `family_level_warning_count`
- `channel_level_warning_count`
- `input_level_warning_count`
- `claim_boundary_warning_count`
- `single_channel_dominance_threshold`
- `dominant_channel_distribution`
- `dominance_warning_reason_counts`
- `aggregate_broadcast_channel_count`
- `case_level_channel_count`
- `profile_score_component_count_summary`
- `output_tracking_policy`
- `runner_refinement_version`

The summary should continue to preserve:

```yaml
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
```

## 10. Readout.md refinements

Future D1m `readout.md` should explicitly include:

- warning-origin summary
- warning-granularity summary
- dominance-semantics note
- aggregate-broadcast channel note
- output-tracking note
- channel roles:
  - `signal_channel`
  - `qualifier_channel`
  - `ambiguity_channel`
  - `control_channel`
  - `construction_sensitivity_channel`
  - `robustness_channel`
  - `summary_channel`
- clear statement: warning-qualified output is not failure
- clear statement: clean joins do not imply clean interpretation
- clear statement: `dominant_channel_id` does not imply single-channel failure unless threshold warning is active

The readout should keep the Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary separation.

## 11. Output-tracking policy

Preserve the D1n recommendation:

`keep_config_runner_and_result_notes_tracked_leave_full_runs_untracked_by_default`

Options:

A. keep runs untracked and reproducible from config plus runner

B. force-add selected summary/readout outputs for public review

C. create docs-side digest

D. force-add full run outputs only with explicit justification

Recommended default:

- track config, runner, plan/spec/result notes
- do not force-add full `runs/` outputs by default
- use docs-side digest or selected forced summary/readout outputs if needed

## 12. Acceptance criteria for future implementation

Future D1m refinement implementation must:

- preserve all existing required D1m output files
- add new fields without breaking existing field names where possible
- preserve `specificity_established: false`
- preserve `phase_is_physical: false`
- preserve `phase_is_synthetic_diagnostic: true`
- preserve Mastermind/Knuth/manifold parked
- include `warning_origin` and `warning_granularity` metadata
- include dominance share and threshold metadata
- distinguish global broadcast warnings from case-level warnings
- identify aggregate-broadcast channels
- keep all warning-qualified rows warning-qualified unless a separately justified logic change exists
- pass CSV header checks
- pass summary key checks
- pass readout claim-boundary checks
- pass `git diff --check`

## 13. Befund expected from this specification

Planning/spec-level only:

- D1o translates D1n audit findings into concrete D1m runner refinement requirements.
- D1o does not change D1m results.
- D1o does not reduce warning load.
- D1o makes future warning semantics more explicit.

## 14. Interpretation rules

D1o is a specification, not a result.

Warning decomposition raises transparency, not physical support. Additional dominance metadata raises interpretability, not physics. Aggregate-broadcast flags prevent false case-level interpretation.

No D1o content may be interpreted as physical phase, physical wavefunction, physical spacetime, diagnostic specificity, or Bridge confirmation.

## 15. Hypothese

D1o supports the working hypothesis that D1m can become methodically clearer by preserving the warning-qualified result while exposing warning origin, warning granularity, broadcast status, and dominance semantics directly in the future D1m outputs.

## 16. Offene Lücke

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
- D1o is only a specification
- no D1m runner refinement implemented yet
- no D1o outputs generated
- D1m warnings remain active
- Mastermind / Knuth / manifold search still parked

## 17. Claim Boundary

This is synthetic diagnostic specification only.

- no runner implemented
- no new scores calculated
- no physical phase
- no physical manifold
- no physical model validation
- no diagnostic specificity
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- Mastermind, Knuth, manifold, and role-permutation remain parked

## 18. Next-step implementation sketch

Future D1o implementation should:

1. create a D1m refined config or config version
2. create a refined D1m runner variant or explicitly versioned D1m runner
3. preserve old D1m outputs
4. add `warning_origin`/`warning_granularity` metadata
5. add dominance share and threshold metadata
6. add aggregate-broadcast channel metadata
7. write refined D1m summary/readout/CSV outputs under a new run_id
8. compare old D1m output with refined D1m output
9. produce a result note
10. avoid physical claims

Do not implement now.
