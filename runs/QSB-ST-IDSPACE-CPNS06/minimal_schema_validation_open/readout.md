# QSB-ST-IDSPACE-CPNS06 Minimal Schema Validation Readout

## Purpose

Validate CPNS04 schema/example consistency only.

## Inputs

- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json`
- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json`

## Checks

- `schema_json_parse`: True
- `examples_json_parse`: True
- `schema_has_object_groups`: True
- `required_object_groups_present`: True
- `object_group_fields_complete`: True
- `boundary_flags_present_and_false`: True
- `examples_list_present`: True
- `each_example_has_equivalence_decision_record`: True
- `required_decision_states_present`: True
- `decision_states_match_schema`: True
- `ambiguity_valid_state`: True
- `invalid_outside_scope_handled_as_non_success`: True
- `no_measured_real_degeneracy`: True

## Result

- passed: True
- decision_states_found: ambiguous_unresolved, different_identity_candidate, invalid_outside_scope, same_identity_candidate
- ambiguity_valid_state: True
- invalid_outside_scope_handled_as_non_success: True
- degeneracy_measurement_status: placeholder_status_only

## Warnings

- `degeneracy_readouts_are_placeholders_only:not_real_degeneracy_measurements`

## Failed Checks

- none

## Claim Boundary

- No Bridge confirmation.
- No diagnostic specificity claim.
- No physical validation.
- No proof of wave identity.
- No physical spacetime claim.
- No WIFM01E default.
- No WIFM02 opening.
- No BRIDGE-NATURE-02 opening.

## Next step

Review this validation result before any later schema or runner extension.
