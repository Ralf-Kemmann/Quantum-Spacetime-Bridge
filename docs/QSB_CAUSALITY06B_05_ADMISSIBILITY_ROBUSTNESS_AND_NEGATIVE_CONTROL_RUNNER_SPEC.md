# QSB-CAUSALITY06B-05 — Admissibility Robustness and Negative-Control Runner Spec

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY06B-05
block_type = robustness_negative_control_run
runner_present = yes
physical_causality_claimed = false
```

This block runs constructed robustness and negative-control tests against the declared CAUSALITY06B-04 admissibility implementation. It checks expected positive transitions, constructed inconsistent controls, and the minimal path without a discrete IS01_S3 state.

## 2. Test Cases

The test classes are:

- `positive_reference_case`
- `negative_control_case`
- `minimal_path_case`

Positive reference cases reuse the five CAUSALITY06B-04 transition candidates. The minimal path case checks `IS01_S2 -> IS01_S4` with `minimal_path_without_discrete_S3 = true`.

## 3. Negative Controls

Negative controls are constructed state-pair tests derived from CAUSALITY06B-04 records. They are not additional experimental observations. Chemical mutations are restricted to `chemical_features`, except the dedicated validator-control case for a candidate configuration marked as separately isolated.

## 4. Runner Logic

The runner imports the pure CAUSALITY06B-04 assessment and validation helpers. It applies the internal run-critical subset validator first. If validation fails, the case follows `validation_path`, sets `rule_evaluation_performed = false`, and does not report chemical rule failures. If validation passes, the case follows `rule_evaluation_path`, evaluates the four chemical rule groups, and compares expected versus actual rule failures exactly. Localized aliases are used only for the German output view.

## 5. Outputs

The runner writes exactly eight outputs under:

```text
runs/QSB-CAUSALITY06B-05/admissibility_robustness/
```

The outputs are `resolved_config.json`, `validated_test_cases.json`, `robustness_results.csv`, `robustness_results.json`, `failure_reason_summary.csv`, `german_alias_view.csv`, `run_summary.json`, and `readout.md`.

## 6. Acceptance Criteria

The run is accepted only if all positive reference cases remain admissible, all negative controls are rejected or fail expected internal validation, validator-rejected controls are not treated as chemically rule-evaluated cases, rule-evaluated negative controls exactly match their expected rule failures, the minimal path remains admissible, no unexpected positives or negatives occur, exactly eight outputs are written, aliases are not used as logic inputs, and `physical_causality_claimed = false`.

## 7. Limitations

Validation failures and chemical rule failures are separate evaluation layers. Validator-rejected controls are not treated as chemically rule-evaluated cases. Exact rule-failure matching tests consistency of the declared controls and implementation only. The negative controls are constructed tests, not additional experimental observations. Positive recall and negative-control rejection rate are descriptive run metrics, not population statistics. The records remain curated source-bound candidate-state data. Formal admissibility does not establish thermodynamic favorability, kinetic accessibility, irreversibility, or physical causality. Localized aliases are presentation metadata only.
