# QSB-ST IDSPACE/CPNS-03 Minimal Schema Acceptance Test Plan

## 1. Purpose

This document defines a minimal schema and acceptance-test plan for a later IDSPACE-01 plus CPNS-02 / MaxEnt implementation.

This is a schema and acceptance-test plan only. It creates no scripts, data, configs, runs, numerical result, Bridge confirmation, diagnostic specificity claim, physical validation, proof of wave identity, or physical spacetime claim.

## 2. Starting point from IDSPACE-01 and CPNS-02

Mandatory primary inputs:

- `docs/QSB_ST_IDSPACE01_IDENTITY_SPACE_DEFINITION_SPEC.md`
- `docs/QSB_ST_CPNS02_MAXENT_DEGENERACY_SPEC.md`
- `docs/QSB_ST_IDSPACE01_CPNS02_MAXENT_PREPARATION_PLAN.md`
- `docs/QSB_ST_BRIDGE_NATURE_01B_RED_TEAM_AND_CODEX_LITERATURE_SYNTHESIS_GATE.md`

Carried-forward gate:

```text
WIFM01-D is closed.
No WIFM01E default.
WIFM02 remains closed.
BRIDGE-NATURE-02 remains closed.
CPNS/MaxEnt degeneracy measurement depends on IDSPACE-01 definitions.
No Bridge confirmation.
No diagnostic specificity claim.
No physical validation.
```

## 3. Scope and non-scope

Scope:

- define minimal schema fields for later implementation
- define acceptance checks for schema completeness
- include illustrative documentation snippets only
- keep ambiguity as a valid decision and result state
- keep CPNS / MaxEnt dependent on IDSPACE-01 definitions
- keep claim-boundary flags explicit

Non-scope:

- no scripts
- no data files
- no configs
- no runs
- no actual JSON or CSV artifacts
- no numerical result
- no WIFM01E default
- no WIFM02 opening
- no BRIDGE-NATURE-02 opening
- no Bridge confirmation
- no diagnostic specificity claim
- no physical validation

## 4. Minimal schema design principle

The schema should be small enough to audit by eye and strict enough to prevent silent claim escalation.

Design rules:

- every record must identify its schema role
- every decision must name the rule or constraint set used
- every ambiguity must be representable without forcing a positive decision
- every CPNS / MaxEnt record must refer back to IDSPACE-01 definitions
- every claim-bearing record must carry explicit false boundary flags
- later implementation may create scripts, data, configs, or runs only after explicit approval

## 5. Minimal identity-space schema

| Field name | Type | Required | Description |
| --- | --- | --- | --- |
| `identity_object_id` | string | yes | Stable candidate identity-object identifier. |
| `identity_layer` | enum | yes | `operational_synthetic_diagnostic` unless a later approved route justifies otherwise. |
| `identity_attributes` | object | yes | Declared attributes used for identity comparison. |
| `identity_relevant_fields` | array | yes | Attributes that may change identity under the equivalence relation. |
| `allowed_transform_classes` | array | yes | Transform classes allowed for this identity object. |
| `equivalence_relation_id` | string | yes | Rule used to compare this object with another identity object. |
| `status` | enum | yes | `draft`, `accepted_for_test`, `invalid_outside_scope`. |
| `source_note` | string | no | Short human-readable note. |

## 6. Minimal fingerprint-object schema

| Field name | Type | Required | Description |
| --- | --- | --- | --- |
| `fingerprint_object_id` | string | yes | Stable diagnostic fingerprint-object identifier. |
| `identity_object_id` | string or null | yes | Linked identity candidate, if assigned. |
| `fingerprint_coordinates` | object | yes | Full diagnostic coordinate record. |
| `phase_like_coordinates` | array | yes | Compact or circular diagnostic coordinates. |
| `noncompact_coordinates` | object | yes | Non-compact diagnostic coordinates. |
| `diagnostic_labels` | array | yes | Warning, conflict, or ambiguity labels. |
| `representation_map_id` | string | yes | Map from identity object to fingerprint object. |
| `observation_map_id` | string | yes | Map from fingerprint object to observable record. |
| `same_looking_not_resolved` | boolean | yes | True when fingerprint similarity is not identity resolution. |
| `status` | enum | yes | `draft`, `accepted_for_test`, `invalid_outside_scope`. |

## 7. Minimal transform-class schema

| Field name | Type | Required | Description |
| --- | --- | --- | --- |
| `transform_class_id` | string | yes | Stable transform-class identifier. |
| `transform_class` | enum | yes | `label_like`, `gauge_like`, `representation_preserving`, `identity_relevant`, or `ambiguity_preserving`. |
| `transform_description` | string | yes | Plain description of the transform. |
| `expected_identity_effect` | enum | yes | `preserve`, `change`, `unresolved`, or `invalid`. |
| `requires_justification` | boolean | yes | True for classes such as gauge-like transforms. |
| `allowed_for_identity_object_ids` | array | no | Identity objects for which the transform is allowed. |
| `status` | enum | yes | `draft`, `accepted_for_test`, `invalid_outside_scope`. |

## 8. Minimal equivalence-decision schema

| Field name | Type | Required | Description |
| --- | --- | --- | --- |
| `decision_id` | string | yes | Stable decision identifier. |
| `identity_object_a_id` | string | yes | First identity-object candidate. |
| `identity_object_b_id` | string | yes | Second identity-object candidate. |
| `fingerprint_object_a_id` | string or null | yes | First fingerprint object, if used. |
| `fingerprint_object_b_id` | string or null | yes | Second fingerprint object, if used. |
| `equivalence_relation_id` | string | yes | Declared equivalence rule. |
| `transform_class_ids` | array | yes | Transform classes considered in the decision. |
| `decision_state` | enum | yes | `same_identity_candidate`, `different_identity_candidate`, `ambiguous_unresolved`, or `invalid_outside_scope`. |
| `ambiguity_class_id` | string or null | yes | Linked ambiguity class if unresolved. |
| `decision_note` | string | no | Short auditable explanation. |

## 9. Minimal CPNS / MaxEnt degeneracy schema

| Field name | Type | Required | Description |
| --- | --- | --- | --- |
| `cpns_record_id` | string | yes | Stable CPNS / MaxEnt record identifier. |
| `constraint_set_id` | string | yes | Declared constraint set. |
| `candidate_family_id` | string | yes | Candidate family being counted or bounded. |
| `null_family_id` | string or null | yes | Null family identifier, if applicable. |
| `alternative_definition_id` | string | yes | IDSPACE-01 definition of what counts as an alternative. |
| `alternative_count` | integer or null | yes | Exact count if available; otherwise null. |
| `degeneracy_lower_bound` | integer or null | yes | Lower bound if available. |
| `degeneracy_upper_bound` | integer or null | yes | Upper bound if available. |
| `degeneracy_status` | enum | yes | `low_degeneracy`, `high_degeneracy`, `unresolved_degeneracy`, or `invalid_degeneracy_measurement`. |
| `maxent_constraint_set_id` | string or null | yes | MaxEnt constraint set, if used. |
| `entropy_value` | number or null | yes | Entropy readout if later computed. |
| `target_smuggling_check` | enum | yes | `pass`, `warning`, `fail`, or `not_applicable`. |

CPNS / MaxEnt degeneracy measurement depends on IDSPACE-01 definitions. High, unresolved, or invalid degeneracy blocks later specificity language.

## 10. Minimal ambiguity-class schema

| Field name | Type | Required | Description |
| --- | --- | --- | --- |
| `ambiguity_class_id` | string | yes | Stable ambiguity-class identifier. |
| `ambiguity_class` | enum | yes | `label_ambiguity`, `gauge_like_ambiguity`, `fingerprint_coordinate_ambiguity`, `identity_relevance_ambiguity`, `constraint_insufficiency_ambiguity`, `candidate_family_ambiguity`, or `outside_scope_ambiguity`. |
| `linked_decision_ids` | array | no | Decisions assigned to this ambiguity class. |
| `linked_cpns_record_ids` | array | no | CPNS records assigned to this ambiguity class. |
| `resolution_status` | enum | yes | `valid_unresolved_result`, `resolved_by_definition`, or `invalid_outside_scope`. |
| `ambiguity_note` | string | no | Short auditable explanation. |

Ambiguity is a valid decision/result state, not an error.

## 11. Claim-boundary flag schema

| Field name | Type | Required | Description |
| --- | --- | --- | --- |
| `claim_boundary_record_id` | string | yes | Stable claim-boundary record identifier. |
| `linked_record_id` | string | yes | Record to which the flags apply. |
| `bridge_confirmation` | boolean | yes | Must be `false`. |
| `diagnostic_specificity_claim` | boolean | yes | Must be `false`. |
| `physical_validation` | boolean | yes | Must be `false`. |
| `wifm01e_opened` | boolean | yes | Must be `false`. |
| `wifm02_opened` | boolean | yes | Must be `false`. |
| `bridge_nature_02_opened` | boolean | yes | Must be `false`. |
| `physical_spacetime_claim` | boolean | yes | Must be `false`. |
| `wave_identity_proof_claim` | boolean | yes | Must be `false`. |

Required explicit flag values:

```text
bridge_confirmation=false
diagnostic_specificity_claim=false
physical_validation=false
wifm01e_opened=false
wifm02_opened=false
bridge_nature_02_opened=false
```

## 12. Required example records

The following snippets are illustrative documentation examples only. They are not actual JSON, CSV, data, configs, runs, or numerical results.

Identity-object example:

```yaml
identity_object_id: ID_EXAMPLE_A
identity_layer: operational_synthetic_diagnostic
identity_attributes:
  family: example_family
identity_relevant_fields:
  - example_identity_attribute
allowed_transform_classes:
  - label_like
  - ambiguity_preserving
equivalence_relation_id: EQ_EXAMPLE_MINIMAL
status: draft
```

Fingerprint-object example:

```yaml
fingerprint_object_id: FP_EXAMPLE_A
identity_object_id: ID_EXAMPLE_A
fingerprint_coordinates:
  example_coordinate: placeholder
phase_like_coordinates: []
noncompact_coordinates: {}
diagnostic_labels:
  - illustrative_only
representation_map_id: RM_EXAMPLE_MINIMAL
observation_map_id: OM_EXAMPLE_MINIMAL
same_looking_not_resolved: true
status: draft
```

Equivalence-decision example:

```yaml
decision_id: DEC_EXAMPLE_AMBIGUOUS
identity_object_a_id: ID_EXAMPLE_A
identity_object_b_id: ID_EXAMPLE_B
fingerprint_object_a_id: FP_EXAMPLE_A
fingerprint_object_b_id: FP_EXAMPLE_B
equivalence_relation_id: EQ_EXAMPLE_MINIMAL
transform_class_ids:
  - representation_preserving
decision_state: ambiguous_unresolved
ambiguity_class_id: AMB_EXAMPLE_COORDINATE
```

CPNS / MaxEnt example:

```yaml
cpns_record_id: CPNS_EXAMPLE_UNRESOLVED
constraint_set_id: CSET_EXAMPLE_MINIMAL
candidate_family_id: CFAM_EXAMPLE
null_family_id: NFAM_EXAMPLE
alternative_definition_id: ALTDEF_IDSPACE01_EXAMPLE
alternative_count: null
degeneracy_lower_bound: null
degeneracy_upper_bound: null
degeneracy_status: unresolved_degeneracy
maxent_constraint_set_id: MAXENT_CSET_EXAMPLE
entropy_value: null
target_smuggling_check: not_applicable
```

Claim-boundary example:

```yaml
claim_boundary_record_id: CLAIM_EXAMPLE_FALSE_FLAGS
linked_record_id: CPNS_EXAMPLE_UNRESOLVED
bridge_confirmation: false
diagnostic_specificity_claim: false
physical_validation: false
wifm01e_opened: false
wifm02_opened: false
bridge_nature_02_opened: false
physical_spacetime_claim: false
wave_identity_proof_claim: false
```

## 13. Acceptance checks

Schema acceptance checks:

- all schema sections contain `Field name | Type | Required | Description`
- IDSPACE-01 records define identity and fingerprint objects before CPNS / MaxEnt records count alternatives
- equivalence decisions allow `ambiguous_unresolved`
- ambiguity classes can be linked to decisions and CPNS records
- claim-boundary flags are present and false
- MaxEnt constraints are declared before interpretation
- MaxEnt constraints do not smuggle in the target identity
- null families are declared before interpretation
- high, unresolved, or invalid degeneracy blocks later specificity language
- no actual data, scripts, configs, or runs are created by this plan

Text acceptance checks for this file:

- run `git diff --check`
- run the requested case-insensitive forbidden-claim grep for this file
- run `git status --short`

## 14. Stop gates

Stop or revise if:

- identity-space fields are missing
- fingerprint-object fields do not preserve the distinction from identity objects
- equivalence decisions force binary output and omit ambiguity
- CPNS / MaxEnt records count alternatives before IDSPACE-01 defines alternatives
- MaxEnt constraints smuggle in target identity
- null families are declared after interpretation
- claim-boundary flags are absent or true
- high, unresolved, or invalid degeneracy is used as support for specificity language
- later implementation is attempted without explicit approval

## 15. Consequence for later implementation

A later implementation may create data, scripts, configs, or run artifacts only after explicit approval.

Before implementation, a later spec should fix:

- accepted schema version
- accepted example-free machine-readable format
- accepted null families
- accepted constraint sets
- accepted stop gates
- accepted claim-boundary checks

The later implementation should test schema acceptance and diagnostic degeneracy only. It should not open WIFM01E, WIFM02, or BRIDGE-NATURE-02.

## 16. Befund

The current route remains:

```text
identity_space_defined=false
degeneracy_quantified=false
```

IDSPACE-01 defines the vocabulary needed before CPNS / MaxEnt can count alternatives. CPNS-02 defines diagnostic degeneracy statuses and requires null families and constraints before interpretation.

This plan adds only a minimal schema and acceptance-test structure for later work.

## 17. Interpretation

The next risk is silent escalation from definitions to apparent result language. Minimal schemas and explicit false claim-boundary flags reduce that risk by making unsupported states visible.

Ambiguity is not a defect in this route. It is a valid decision/result state that may block later specificity language.

## 18. Hypothese

Working hypothesis, method-level only:

```text
If later implementation uses a minimal schema with explicit ambiguity
states and false claim-boundary flags, then IDSPACE/CPNS records can
be audited without turning diagnostic degeneracy into specificity
language.
```

This does not imply that low degeneracy will be found.

## 19. Offene Lücke

Open gaps after this plan:

- no actual schema files
- no JSON or CSV artifacts
- no scripts
- no configs
- no runs
- no accepted machine-readable format
- no populated identity records
- no populated fingerprint records
- no populated CPNS / MaxEnt records
- no degeneracy count or bound
- no entropy readout
- no target-smuggling audit result
- no Bridge confirmation
- no diagnostic specificity claim

## 20. Claim Boundary

This is a schema and acceptance-test plan only.

Not established:

- Bridge confirmation
- diagnostic specificity
- physical validation
- proof of wave identity
- physical spacetime claim
- physical phase reconstruction
- physical metric
- physical degeneracy
- Hilbert-space reconstruction
- WIFM01E default
- WIFM02 opening
- BRIDGE-NATURE-02 opening

Allowed statement:

```text
IDSPACE/CPNS-03 defines a minimal schema and acceptance-test plan
for later approved implementation of diagnostic identity and
degeneracy records.
```
