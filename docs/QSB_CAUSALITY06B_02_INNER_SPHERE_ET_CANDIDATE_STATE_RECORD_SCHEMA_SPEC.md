# QSB-CAUSALITY06B-02 — Inner-Sphere ET Candidate-State Record Schema

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY06B-02
block_type = schema_specification
runner_present = no
numerical_analysis_present = no
graph_analysis_present = no
direction_reconstruction_present = no
physical_causality_claimed = no
```

This block defines a hardened machine-readable candidate-state record structure. It does not run a model, score states, reconstruct direction, compute continuation spaces, or evaluate physical causality.

## 2. Dependency on CAUSALITY06B-01

This schema depends on `docs/QSB_CAUSALITY06B_01_EVIDENCE_GATED_INNER_SPHERE_ET_STATE_SPEC.md` and preserves its evidence, optionality, and leakage boundaries.

## 3. Schema Purpose

The schema documents candidate states for the classical Co(III)/Cr(II) chloride-transfer reference case while separating chemical features, species status, pathway evidence, descriptive metadata, reference-order metadata, source metadata, optional-state controls, and leakage controls.

## 4. Record Identity

Each record contains `record_id`, `case_id`, `state_id`, and `state_representation_status`. Descriptive roles are stored under `descriptive_metadata` rather than as direction features.

## 5. Chemical Feature Fields

Only `chemical_features` may be considered as candidate inputs in a later, separately specified transition-admissibility block. This schema does not define that later rule.

## 6. Species-Status Fields

`species_status` separates documented species identity from path-context resolution. `directly_documented_species` is not equivalent to `directly_resolved_in_reaction_context`.

## 7. Pathway-Evidence Fields

`pathway_evidence` records mechanistic, tracer, product, kinetic, and direct-resolution metadata. It is forbidden as a direction feature.

## 8. Descriptive and Reference-Order Metadata

`descriptive_metadata` contains `state_role`, `plain_language_description`, `documented_reference_position`, and `is_optional_in_minimal_path`. Reference order is stored for audit and example coverage only.

## 9. Source and Provenance Fields

`source_metadata` records source basis, reference IDs, source role, and provenance notes. It does not encode a direction claim.

## 10. Optional-State Handling

`optional_state_controls` records the S3-specific controls: `post_et_bridge_persistence_required = false`, `IS01_S3_required_as_discrete_species = false`, and `IS01_S3_optional_in_minimal_path_representation = true`. Omitting IS01_S3 in the minimal path does not deny chloride-bridge participation.

## 11. Nullability Rules

The schema uses controlled `unknown`, `not_assessed`, and `not_applicable` values where needed. Required objects must be present. `optional_state_controls` is required by schema only when `state_id = IS01_S3`.

## 12. Controlled Vocabularies

Controlled vocabularies are encoded in `candidate_state_record_schema.json` using Draft 2020-12 `enum`, `const`, and typed fields.

## 13. Leakage-Control Rules

Every record contains complete `leakage_controls`. Chemical features are marked as potentially allowed only for a future, separate admissibility specification:

```text
chemical_features_as_future_direction_inputs_potentially_allowed = true
future_use_requires_separate_admissibility_specification = true
```

This does not mean a direction rule already exists.

## 14. Cross-Field Consistency Rules

The schema rejects selected internal contradictions encoded by the declared record model. Machine-enforced rules include bridge consistency, transferred-electron oxidation-state consistency, chloride-on-Cr consistency, candidate-not-isolated consistency, P5 direct-resolution consistency, and hard rules for IS01_S2, IS01_S3, and IS01_S4.

Rules that remain documentary include chemical completeness beyond these declared fields, kinetic interpretation, thermodynamic interpretation, and whether a real mechanism is uniquely represented.

## 15. Example-State Coverage

The example file contains IS01_S0 through IS01_S4. IS01_S3 is included in the full reference path and excluded from the minimal reference path.

## 16. Validation Requirements

Validation performed for this hardening step:

```text
schema_check = passed
valid_example_record_count = 5
validation_error_count = 0
negative_test_count = 5
unexpected_negative_test_passes = 0
missing_field_paths = 0
duplicate_field_paths = 0
```

Negative tests were run inline without writing a durable test file.

## 17. Allowed Uses

Allowed uses are schema validation, field-list auditing, leakage-control auditing, and preparation for a later admissibility specification.

## 18. Forbidden Uses

Forbidden uses include claiming physical causality, using metadata as direction input, claiming IS01_S2 or IS01_S3 was directly isolated, treating the schema as a runner, or treating schema acceptance as mechanistic proof.

## 19. Acceptance Criteria

This block remains accepted only if the four existing files are updated, no new file is created, Draft 2020-12 is retained, all five examples validate, negative contradiction records are rejected, FIELD_LIST.md is complete and six-column, leakage controls are complete and const-protected, and no physical causality claim is introduced.

## 20. Limitations

The schema rejects selected internal contradictions encoded by the declared record model. It does not guarantee chemical truth, reconstruct direction, fit kinetics, evaluate thermodynamics, calculate transition states, or prove any mechanism.

## 21. Next-Step Boundary

The next allowed block remains a separate validation or admissibility-specification step. No runner, graph analysis, scoring, directed transition comparison, continuation-space computation, or result claim is included here.
