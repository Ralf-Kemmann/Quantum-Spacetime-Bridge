# QSB-CAUSALITY06B-04 — First Inner-Sphere ET Data and Admissibility Runner Spec

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY06B-04
block_type = first_data_and_runner_block
runner_present = yes
numerical_analysis_present = no
graph_analysis_present = no
physical_causality_claimed = no
```

This block defines the first data-backed runner for the CAUSALITY06B inner-sphere Co(III)/Cr(II) chloride-transfer record model. It tests formal transition admissibility under the declared 06B-03 rule groups and writes machine-readable outputs plus a defensive readout.

## 2. Inputs

Inputs are:

- `data/QSB-CAUSALITY06B-04/inner_sphere_et_state_records.json`
- `data/QSB-CAUSALITY06B-04/transition_candidates.json`
- `data/QSB-CAUSALITY06B-04/field_aliases_de.json`
- `data/QSB-CAUSALITY06B-04/source_inventory.md`
- `data/QSB-CAUSALITY06B-02/candidate_state_record_schema.json`

The state records are curated source-bound candidate-state data derived from the CAUSALITY06B-02 example records and retain the CAUSALITY06B-01 chemical semantics. They are not raw experimental measurement data and are not a directly time-resolved trajectory.

```text
data_status = curated_source_bound_candidate_state_data
raw_experimental_measurement_data = false
directly_time_resolved_trajectory = false
mechanistic_reference_decomposition = true
```

Reference-order metadata, evidence metadata, descriptive labels, source metadata, known mechanism names, and localized aliases are not admissibility inputs.

## 3. Rule Implementation

The runner implements exactly four rule groups:

- R1 Redox Consistency
- R2 Chloride and Bridge Consistency
- R3 Coordination and Association Consistency
- R4 State-Change Coherence

Only fields under `chemical_features` are used by the transition logic. The forward Boolean is computed as:

```text
forward_admissible = redox_consistent and chloride_bridge_consistent and coordination_consistent and state_change_coherent
```

## 4. Reverse-Direction Logic

Each transition candidate is assessed forward and reverse with the same four rule groups. Reverse comparisons requiring external conditions receive controlled, machine-readable `reverse_external_condition_reasons` values derived only from compared `chemical_features`. The result separates:

```text
forward_transition_status
direction_comparison_class
```

The final comparison class is assigned by the exclusive mapping declared in 06B-03. Formal directional asymmetry is not interpreted as physical causality, thermodynamic irreversibility, or kinetic inaccessibility.

## 5. Localized Alias View

`field_aliases_de.json` provides German display aliases for a presentation view. Canonical field names remain language-neutral and are used for schema, runner, JSON, CSV, tests, validation logic, joins, keys, and machine comparison.

```text
localized_aliases_used_as_logic_inputs = false
schema_change_required_for_new_language = false
```

## 6. Outputs

The runner writes exactly eight files under:

```text
runs/QSB-CAUSALITY06B-04/first_inner_sphere_et_admissibility/
```

The files are `resolved_config.json`, `validated_state_records.json`, `transition_results.csv`, `transition_results.json`, `direction_comparison_summary.csv`, `german_alias_view.csv`, `run_summary.json`, and `readout.md`.

## 7. Validation

The runner uses an internal validator covering a declared run-critical subset of CAUSALITY06B-02 constraints. It is not a complete Draft 2020-12 JSON Schema validator.

```text
validation_mode = internal_schema_constraint_subset
internal_validation_passed = true
full_jsonschema_validation_performed = false
full_jsonschema_validation_passed = not_applicable
```

The internal validation scope includes required run fields, state-id coverage, selected controlled vocabularies, selected cross-field constraints, IS01_S2 bridge constraints, IS01_S3 optionality constraints, and IS01_S4 product constraints. It does not cover complete Draft 2020-12 semantics, all nested required constraints, all additional-properties constraints, all conditional schema branches, or complete metadata validation.

The runner processes five transition candidates, checks forward and reverse directions, writes exactly eight outputs, and exits non-zero on validation or output-count failure.

## 8. Limitations

The internal validator covers a declared run-critical subset and is not a complete Draft 2020-12 JSON Schema validator. The records are curated source-bound candidate-state data, not raw measurements. Reverse external-condition reasons are rule-based classifications, not experimental demonstrations. Formal admissibility does not establish thermodynamic favorability. Formal admissibility does not establish kinetic accessibility. Formal directional asymmetry does not establish physical causality. IS01_S3 remains optional. Localized aliases are presentation metadata only. No independent causal reconstruction is performed.
