# QSB-ST-SHAPIROINFO04 -- Toy Comparator Minimal Runner Spec

## Purpose

SHAPIROINFO04 setzt den SHAPIROINFO03-Plan in einen minimalen lokalen
Toy-Runner um. Der Runner soll nur pruefen, ob die technische
Residual-Entscheidungslogik fuer synthetische A/B-Signalpaare reproduzierbar
formuliert und auditiert werden kann.

Current anchor:

- `7102e13 Add QSB-ST ShapiroInfo toy comparator plan`

Builds on:

- `docs/QSB_ST_INTERFACE03_RT_QM_CAUSALITY_ROSETTA_TRANSLATOR_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO03_TOY_COMPARATOR_PLAN.md`
- `docs/QSB_ST_INTERFACE_SHAPIROINFO_RESULT_READOUT_2026_05_28.md`

## Scope

- minimal synthetic runner only
- no real Shapiro data
- no external downloads
- no empirical claim
- no physical validation
- no modification of standard Shapiro delay
- no Bridge confirmation

## Created Files

- `data/QSB-ST-SHAPIROINFO/toy_comparator_config.yaml`
- `scripts/run_qsb_st_shapiroinfo_toy_comparator.py`
- `docs/QSB_ST_SHAPIROINFO04_TOY_COMPARATOR_MINIMAL_RUNNER_SPEC.md`

## Config Boundary

The config file is a YAML-compatible JSON document. This keeps the file under
the requested `.yaml` path while allowing the runner to parse it with Python
stdlib `json`, without PyYAML and without external downloads.

The config contains only synthetic toy variants:

- `V0_identity_control`
- `V1_known_delay_only`
- `V2_known_delay_plus_noise`
- `V3_known_artifact`
- `V4_hidden_residual_candidate`
- `V5_false_positive_control`

## Minimal Algorithm

For each variant:

```text
A_reference = configured synthetic baseline

B_influenced = A_reference
             + known_delay_component
             + standard_artifact
             + bounded_noise
             + candidate_residual

corrected_B = B_influenced
            - applied_known_delay_component
            - applied_standard_artifact
            - applied_bounded_noise

residual = corrected_B - A_reference
```

The runner computes residuals for:

- `residual_timing_s`
- `residual_phase_rad`
- `residual_frequency_hz`
- `residual_fingerprint_score`

It also computes a `normalized_residual_score` as the maximum absolute
component residual divided by the corresponding uncertainty.

## Decision Rules

- If resolution is weak or comparison stability is not stable:
  `residual_status = inconclusive`.
- If `normalized_residual_score` is within the configured uncertainty limit:
  `residual_status = no_residual`.
- If a standard artifact or control explains the difference:
  `residual_status = artifact_likely`.
- If the residual is beyond uncertainty, reproducible by the toy repeat count,
  and controls do not explain it:
  `residual_status = candidate_residual`.
- Otherwise:
  `residual_status = inconclusive`.

`candidate_residual` is a technical diagnostic state only. It is not physical
validation.

## Run Outputs

The default output directory is:

- `runs/QSB-ST-SHAPIROINFO04/toy_comparator_minimal_open`

The test run writes only:

- `toy_comparator_variant_results.csv`
- `toy_comparator_status_summary.csv`
- `summary.json`
- `resolved_config.json`
- `readout.md`

The runner refuses to overwrite existing output files.

## Connection to INTERFACE03

- c remains vocabulary/interface context only.
- no derivation of c
- no explanation of the numerical value of c
- timing, phase, frequency, and fingerprint coordinates are comparator fields,
  not theory-level substitutes.

## Connection to SHAPIROINFO01

- Standard Shapiro correction remains a known-correction layer.
- Residual language begins only after known corrections and controls.
- The toy runner does not change standard Shapiro physics.

## Connection to SHAPIROINFO02

- The runner output fields are aligned with the minimal signal record language.
- The current file does not create real records.
- The current file does not create empirical data.

## Befund

SHAPIROINFO04 provides a minimal local route from plan text to a deterministic
synthetic comparator run.

## Interpretation

The runner can later be used to check whether status words such as
`no_residual`, `artifact_likely`, `inconclusive`, and `candidate_residual`
remain mechanically separated under toy inputs.

## Hypothese

A small synthetic runner may help keep later ShapiroInfo work auditable before
any real-data question is introduced.

## Offene Luecke

No real data, no empirical test, no physical validation, no specificity, no
claim about a Shapiro modification.

## Claim Boundary

- no derivation of c
- no explanation of the numerical value of c
- no Bridge confirmation
- no spacetime emergence claim
- no replacement of relativity or quantum mechanics
- no Shapiro modification claim
- no evidence claim from toy runner alone

## Acceptance Checks

- Config file exists.
- Runner script exists.
- Spec file exists.
- Test run writes only the named output files under the declared run directory.
- Variant table contains V0 through V5.
- `expected_status_check_passed=true`.
- Risk grep clean.
- Python syntax compile check clean.
- `git diff --check` clean.
- `git status --short` reported.
