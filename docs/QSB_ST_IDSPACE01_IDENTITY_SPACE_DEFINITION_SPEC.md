# QSB-ST IDSPACE-01 Identity Space Definition Specification

## 1. Purpose

This document specifies the IDSPACE-01 identity-space definition task requested after the IDSPACE/CPNS preparation plan.

It is a definition specification only. It creates no scripts, data, configs, runs, numerical result, physical validation, Bridge confirmation, diagnostic specificity claim, or proof of wave identity.

## 2. Starting point from IDSPACE/CPNS preparation

Primary inputs:

- `docs/QSB_ST_IDSPACE01_CPNS02_MAXENT_PREPARATION_PLAN.md`
- `docs/QSB_ST_BRIDGE_NATURE_01B_RED_TEAM_AND_CODEX_LITERATURE_SYNTHESIS_GATE.md`

Starting gate carried forward:

```text
WIFM01-D is closed.
No WIFM01E default.
WIFM02 remains closed.
BRIDGE-NATURE-02 remains closed.
Next preparation route: IDSPACE-01 plus CPNS-02 / MaxEnt.
identity_space_defined=false.
degeneracy_quantified=false.
No Bridge confirmation.
No diagnostic specificity claim.
```

IDSPACE-01 is the first definition step in that route. CPNS-02 / MaxEnt must not count or bound alternatives until IDSPACE-01 has fixed what counts as an alternative.

## 3. Scope and non-scope

Scope:

- define an operational/synthetic diagnostic Identitaets-Raum layer
- define candidate identity and fingerprint objects
- define representation and observation maps
- define equivalence and transform classes
- define identity decision states
- define the minimal schema needed for later implementation
- preserve ambiguity as a valid result state

Non-scope:

- no WIFM01E default
- no WIFM02 opening
- no BRIDGE-NATURE-02 opening
- no physical spacetime claim
- no physical phase reconstruction
- no physical metric
- no Hilbert-space reconstruction
- no Bridge confirmation
- no diagnostic specificity claim
- no proof of wave identity

## 4. Core distinction: Fingerprint-Raum vs Identitaets-Raum

Fingerprint-Raum is the diagnostic space of observed or constructed relational fingerprints. It may contain circular phase-like coordinates, non-compact coordinate differences, local-form diagnostics, amplitudes, warning labels, and ambiguity labels.

Identitaets-Raum is an operational/synthetic diagnostic layer unless explicitly justified otherwise. It is the layer where candidate identity objects are proposed, grouped, separated, or left unresolved.

Fingerprint-Raum is not automatically Identitaets-Raum. Two fingerprints can be close, same-looking, or geometrically readable in Fingerprint-Raum while remaining unresolved in Identitaets-Raum.

Same-looking does not mean identity-resolved. It means only that the chosen fingerprint observables did not separate the candidate objects under the current definitions and controls.

## 5. Candidate identity object

A candidate identity object is a proposed operational object whose identity status can be compared under an explicit equivalence relation.

Minimal definition:

```text
identity_object := synthetic diagnostic candidate with declared attributes,
declared admissible transforms, and declared identity-relevant differences.
```

The candidate identity object is not a physical wavefunction, not a physical particle state, not a spacetime point, and not proof of wave identity.

An identity object may be treated as unresolved when multiple candidate objects remain compatible with the same fingerprint evidence.

## 6. Candidate fingerprint object

A candidate fingerprint object is the diagnostic representation available for comparison.

Minimal definition:

```text
fingerprint_object := structured diagnostic record containing coordinates,
labels, observables, provenance, and claim-boundary flags.
```

The fingerprint object can include compact/circular phase-like coordinates and non-compact diagnostic coordinates, but these remain synthetic diagnostic quantities unless separately justified.

## 7. Representation map

The representation map links candidate identity objects to fingerprint objects.

Required statement:

```text
representation_map: identity_object -> one or more fingerprint_objects
```

The map may be many-to-one. If different identity objects can produce the same or near-same fingerprint object, the output is not identity-specific.

The representation map must declare which differences are expected to be preserved, erased, compressed, or made ambiguous by representation.

## 8. Observation map

The observation map selects reported observables from a fingerprint object.

Required statement:

```text
observation_map: fingerprint_object -> observable_record
```

The observation map must declare:

- which coordinates are observed directly
- which quantities are derived
- which quantities are labels or annotations
- which quantities are compact/circular
- which quantities are non-compact
- which quantities are excluded from identity decisions

Observation cannot create identity specificity by naming. If the observation map drops identity-relevant information, the decision state must allow ambiguity.

## 9. Equivalence relation

The equivalence relation defines when candidate identity objects are treated as same, different, ambiguous, or invalid.

Required structure:

```text
equivalence_relation(identity_a, identity_b, context) -> decision_state
```

The relation must be declared before evaluation and must distinguish:

- invariance under label-like transforms
- invariance under gauge-like transforms
- representation-preserving differences
- identity-relevant differences
- cases where current observables are insufficient

The equivalence relation may be partial. It is acceptable for it to return ambiguous / unresolved.

## 10. Transform classes

Each transform class must be declared before it is used in later implementation.

### Label-like transforms

Label-like transforms rename, permute, or reorder labels without changing the intended identity object.

Expected decision behavior:

```text
same-identity candidate, if all other identity-relevant structure is preserved
```

### Gauge-like transforms

Gauge-like transforms change representation convention while preserving the intended diagnostic identity content.

Expected decision behavior:

```text
same-identity candidate, if the transform is explicitly declared gauge-like
```

Gauge-like status is not automatic. It must be justified within the synthetic diagnostic setup.

### Representation-preserving transforms

Representation-preserving transforms leave the observed fingerprint record unchanged or equivalent under the observation map.

Expected decision behavior:

```text
same-looking in Fingerprint-Raum, but not automatically identity-resolved
```

This class is the main guard against confusing same-looking fingerprints with same identity.

### Identity-relevant transforms

Identity-relevant transforms change attributes that the equivalence relation has declared identity-defining.

Expected decision behavior:

```text
different-identity candidate, unless the evidence is insufficient and must be marked ambiguous
```

### Ambiguity-preserving transforms

Ambiguity-preserving transforms keep the decision unresolved because the current observables cannot distinguish alternatives.

Expected decision behavior:

```text
ambiguous / unresolved
```

Ambiguity is a valid result state, not a failure.

## 11. Identity decision states

Allowed decision states:

- `same_identity_candidate`: current definitions support same identity under declared transforms
- `different_identity_candidate`: current definitions support different identity under declared identity-relevant differences
- `ambiguous_unresolved`: current definitions and observables do not distinguish the candidates
- `invalid_outside_scope`: the object, transform, or comparison is outside this specification

Decision states are diagnostic classifications only. They are not physical truth labels.

## 12. Required minimal schema for later implementation

Compact field list for a later implementation:

| Field name | Type | Description |
| --- | --- | --- |
| `record_id` | string | Unique record identifier. |
| `identity_object_id` | string or null | Candidate identity object identifier, if assigned. |
| `fingerprint_object_id` | string | Candidate fingerprint object identifier. |
| `source_family` | string | Synthetic family, control family, or null family. |
| `fingerprint_coordinates` | object | Full diagnostic coordinate record. |
| `phase_like_coordinates` | array | Compact/circular diagnostic coordinates. |
| `noncompact_coordinates` | object | Non-compact diagnostic coordinates. |
| `diagnostic_labels` | array | Warning, conflict, ambiguity, or provenance labels. |
| `representation_map_id` | string | Identifier for the representation map used. |
| `observation_map_id` | string | Identifier for the observation map used. |
| `equivalence_relation_id` | string | Identifier for the declared equivalence relation. |
| `transform_class` | enum | One of label-like, gauge-like, representation-preserving, identity-relevant, ambiguity-preserving. |
| `comparison_partner_id` | string or null | Other object in a pairwise identity comparison. |
| `decision_state` | enum | One of same_identity_candidate, different_identity_candidate, ambiguous_unresolved, invalid_outside_scope. |
| `ambiguity_class_id` | string or null | Identifier for unresolved candidate class. |
| `candidate_alternative_count` | integer or null | Number of alternatives, if already countable. |
| `degeneracy_bound` | string or null | Bound or status for compatible alternatives. |
| `maxent_constraint_set_id` | string or null | Constraint set for later CPNS-02 / MaxEnt use. |
| `claim_boundary_flags` | object | Flags for bridge_confirmation, diagnostic_specificity, physical_validation, and related boundaries. |
| `notes` | string | Short auditable note without overclaim language. |

No later implementation should infer a candidate alternative count until IDSPACE-01 has fixed what counts as an alternative.

## 13. Acceptance criteria

IDSPACE-01 is accepted only if:

- Fingerprint-Raum and Identitaets-Raum remain explicitly separated
- identity space is defined as operational/synthetic diagnostic unless explicitly justified otherwise
- candidate identity and fingerprint objects are defined
- representation and observation maps are declared
- equivalence relation and transform classes are declared
- identity decision states include ambiguous / unresolved
- same-looking fingerprints are not treated as identity-resolved by default
- minimal schema fields are specified
- CPNS-02 / MaxEnt is blocked from counting alternatives until alternatives are defined
- no WIFM01E default is introduced
- WIFM02 remains closed
- BRIDGE-NATURE-02 remains closed
- no Bridge confirmation is claimed
- no diagnostic specificity claim is made
- no physical validation is claimed

## 14. Befund

BRIDGE-NATURE-01B and the IDSPACE/CPNS preparation plan both identify the same route boundary:

```text
identity_space_defined=false
degeneracy_quantified=false
```

The current task addresses only the first item by specifying what identity-space definition must contain.

## 15. Interpretation

The identity-space problem is a definition problem before it is a numerical problem. Without an explicit Identitaets-Raum, same-looking fingerprints can be mistaken for identity resolution.

This specification therefore treats identity decisions as operational classifications under declared maps, transforms, and equivalence relations.

## 16. Hypothese

Working hypothesis, method-level only:

```text
If IDSPACE-01 fixes identity objects, fingerprint objects, maps,
equivalence relations, and decision states, then CPNS-02 / MaxEnt
can count or bound alternatives without changing the meaning of
"alternative" during evaluation.
```

This hypothesis does not imply diagnostic specificity or Bridge confirmation.

## 17. Offene Lücke

Open gaps after this specification:

- no implemented schema
- no populated identity-object table
- no populated fingerprint-object table
- no tested equivalence relation
- no accepted transform library
- no counted or bounded degeneracy
- no MaxEnt constraint set applied
- no control-family outcome
- no diagnostic specificity claim
- no Bridge confirmation

## 18. Claim Boundary

This is a definition specification only.

Not established:

- Bridge confirmation
- diagnostic specificity
- physical validation
- proof of wave identity
- physical spacetime claim
- physical phase reconstruction
- physical metric
- Hilbert-space reconstruction
- WIFM01E default
- WIFM02 opening
- BRIDGE-NATURE-02 opening

Allowed statement:

```text
IDSPACE-01 defines the operational/synthetic identity-space vocabulary
needed before CPNS-02 / MaxEnt can count or bound alternatives.
```

## 19. Consequence for CPNS-02 / MaxEnt

CPNS-02 / MaxEnt may proceed only after IDSPACE-01 fixes:

- what counts as a candidate identity object
- what counts as a candidate fingerprint object
- what counts as an alternative
- which transforms preserve identity
- which transforms change identity
- when same-looking fingerprints remain unresolved
- which ambiguity classes are valid result states

CPNS-02 / MaxEnt should then count, bound, or explicitly fail to bound alternatives under the fixed definitions. If alternatives remain numerous or poorly bounded, that is a boundary result and must not be rewritten as diagnostic specificity.
