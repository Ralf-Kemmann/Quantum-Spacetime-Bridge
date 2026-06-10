# OUTREACH01A-03 — Minimal Synthetic DTC State-Identity Demonstrator Spec

## 1. Status and Scope

```text
demonstrator_id = OUTREACH01A_DTC_DEMO01
data_status = synthetic_method_demonstrator
models_reported_laser_experiment = no
experimental_data_used = no
physical_prediction_present = no
time_crystal_mechanism_explained = no
contact_message_present = no
contact_sent = no
validation_mode = internal_schema_constraint_subset
internal_validation_passed = true
full_jsonschema_validation_performed = false
full_jsonschema_validation_passed = not_applicable
canonical_field_names_remain_language_neutral = true
canonical_controlled_values_remain_language_neutral = true
localized_field_aliases_used_as_logic_inputs = false
localized_value_aliases_used_as_logic_inputs = false
localized_aliases_used_as_keys = false
localized_aliases_used_in_joins = false
english_presentation_view_required_for_contact_package = true
english_presentation_view_created = false
```

This block defines and validates a minimal synthetic demonstrator for a later, still gated contact package. It is limited to method-level distinctions between state class, dynamic equivalence, temporal phase offset, domain membership, boundary representation, observable signature, and full-state identity.

It is not a model of the reported laser experiment, not an experimental fit, not a prediction, and not an explanation of discrete time-crystal physics.

## 2. Three-Record Demonstrator

The demonstrator contains exactly three records:

```text
DTC_A
DTC_B
BOUNDARY_AB
```

`DTC_A` and `DTC_B` are synthetic state-configuration records. They share one declared dynamic equivalence class and one state class, but they are not the same record. Their temporal phase offset differs by one drive period, and they belong to different domains.

`BOUNDARY_AB` is a separate synthetic boundary record between `DOMAIN_A` and `DOMAIN_B`. It is not assigned to the dynamic equivalence class of `DTC_A` and `DTC_B`.

## 3. Identity and Equivalence Logic

The demonstrator carries these method statements:

```text
DTC_A and DTC_B share one dynamic equivalence class.
DTC_A and DTC_B are not the same record.
DTC_A and DTC_B differ by one drive period in temporal phase offset.
DTC_A and DTC_B belong to different domains.
BOUNDARY_AB is represented as a separate boundary record.
The boundary representation is a modelling choice, not an experimentally validated ontology.
```

Required non-identity boundaries:

```text
observable_similarity_implies_full_state_identity = false
dynamic_equivalence_implies_record_identity = false
phase_shifted_equivalence_implies_same_domain = false
```

Dynamic equivalence is declared for this synthetic method demonstration. It is not experimentally inferred.

## 4. Boundary Representation

The separate `BOUNDARY_AB` record is included to make the contact question concrete: should a long-lived boundary between coexisting equivalent configurations be represented as a label, a separate object, or another dynamical description?

This demonstrator does not force the boundary-object representation as the correct answer.

```text
preferred_boundary_representation_forced = false
```

## 5. Validation

The validator loads:

- `data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_schema.json`
- `data/OUTREACH01A-DTC-DEMO01/dtc_state_identity_records.json`
- `data/OUTREACH01A-DTC-DEMO01/field_aliases_de.json`

The current validator uses an internal validator covering the declared schema-critical and cross-record constraints. A complete Draft 2020-12 JSON Schema validation is not performed in the active environment because the required validator package is unavailable. The validator reports:

```text
validation_mode = internal_schema_constraint_subset
internal_validation_passed = true
full_jsonschema_validation_performed = false
full_jsonschema_validation_passed = not_applicable
validation_passed_scope = internal_schema_constraint_subset
```

It checks record count, exact IDs, required fields, shared equivalence class, distinct record identity, one-period phase shift, domain separation, separate boundary record, and leakage controls.

German field aliases and controlled-value aliases are used only in human-readable outputs. They are not field identity, record identity, validation input, comparison input, join keys, or result logic.

## 6. Contact-Package Role

The role of this demonstrator is:

```text
contact_package_role = small_auditable_question_carrier
```

It can later support a compact table, a small machine-readable excerpt, and three technical questions. It is not a proof, not a theory summary, not a laser model, and not a repository showcase.

## 7. Limitations

- The demonstrator is synthetic and is not a model of the reported laser experiment.
- Dynamic equivalence is declared for method demonstration and is not experimentally inferred.
- The separate boundary record is an open representation option, not a validated ontology.
- No physical prediction, mechanism explanation, validation, or endorsement claim is made.
- Localized aliases are presentation metadata only.
- Localized field and value aliases are presentation metadata only.
- An English presentation view is still required before inclusion in an external contact package.
- No contact message is created or sent.
