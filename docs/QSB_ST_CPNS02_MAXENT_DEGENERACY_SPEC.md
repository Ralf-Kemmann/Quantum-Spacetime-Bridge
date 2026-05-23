# QSB-ST CPNS-02 / MaxEnt Degeneracy Specification

## 1. Purpose

This document specifies CPNS-02 / MaxEnt as a degeneracy and ambiguity task following IDSPACE-01.

It is a degeneracy specification only. It creates no scripts, data, configs, runs, numerical result, physical validation, Bridge confirmation, diagnostic specificity claim, proof of wave identity, or physical spacetime claim.

## 2. Starting point from IDSPACE-01

Mandatory primary inputs:

- `docs/QSB_ST_IDSPACE01_IDENTITY_SPACE_DEFINITION_SPEC.md`
- `docs/QSB_ST_IDSPACE01_CPNS02_MAXENT_PREPARATION_PLAN.md`
- `docs/QSB_ST_BRIDGE_NATURE_01B_RED_TEAM_AND_CODEX_LITERATURE_SYNTHESIS_GATE.md`

Starting boundary carried forward:

```text
WIFM01-D is closed.
No WIFM01E default.
WIFM02 remains closed.
BRIDGE-NATURE-02 remains closed.
identity_space_defined=false until IDSPACE-01 is implemented and accepted.
degeneracy_quantified=false until CPNS-02 / MaxEnt is implemented and accepted.
No Bridge confirmation.
No diagnostic specificity claim.
```

CPNS-02 depends on IDSPACE-01 definitions. It may count, bound, or fail to bound alternatives only after IDSPACE-01 fixes what counts as an identity object, fingerprint object, alternative, transform class, and ambiguity class.

## 3. Scope and non-scope

Scope:

- define Constraint-Preserving Null Space for the diagnostic identity route
- define the MaxEnt role
- define diagnostic degeneracy targets
- define constraint classes and null families
- define degeneracy and entropy readouts
- define ambiguity classes
- define stop and escalation gates
- define a minimal schema for later implementation

Non-scope:

- no WIFM01E default
- no WIFM02 opening
- no BRIDGE-NATURE-02 opening
- no physical degeneracy claim
- no physical validation
- no physical spacetime claim
- no proof of wave identity
- no Bridge confirmation
- no diagnostic specificity claim

## 4. CPNS definition: Constraint-Preserving Null Space

Constraint-Preserving Null Space means the set of candidate alternatives that preserve a declared constraint set while varying features not fixed by that set.

Operational definition:

```text
CPNS(constraint_set, candidate_family) :=
  all admissible candidate alternatives that satisfy the fixed constraints
  under the IDSPACE-01 definitions.
```

The CPNS is diagnostic, not physical. It measures how many synthetic or operational alternatives remain compatible with the chosen diagnostic constraints.

If many alternatives remain in the CPNS, the diagnostic route may be non-specific even if the observed fingerprint is structured.

## 5. MaxEnt role

MaxEnt provides a least-committal distribution over admissible alternatives under declared constraints.

Allowed role:

- expose how much ambiguity remains when only the stated constraints are used
- produce entropy readouts over candidate alternatives or ambiguity classes
- test whether constraints are too weak, too strong, or target-smuggling
- provide a baseline distribution for comparison with structured diagnostic outcomes

Disallowed role:

- MaxEnt must not smuggle in the target identity
- MaxEnt must not encode the desired bridge conclusion
- MaxEnt must not turn an analogy or prior preference into evidence
- MaxEnt must not be used to erase high degeneracy by post hoc constraint selection

## 6. Degeneracy target

The degeneracy target is the number, bound, or uncertainty status of candidate identity alternatives compatible with the same declared constraints and observations.

Diagnostic degeneracy:

```text
degeneracy_diagnostic := count, bound, or measure of candidate alternatives
compatible with the IDSPACE-01 diagnostic definitions.
```

Physical degeneracy:

```text
degeneracy_physical := physical-state degeneracy in a validated physical model.
```

This specification addresses diagnostic degeneracy only. It does not establish physical degeneracy.

Degeneracy can block later specificity language. If the same fingerprint evidence admits many identity alternatives, later notes must report that ambiguity instead of claiming diagnostic specificity.

## 7. Constraint classes

Each constraint class must be declared before interpretation.

### Label constraints

Label constraints preserve or control names, indices, ordering, or symbolic labels.

Use:

- test whether apparent separation depends on label choices
- define label-permutation nulls
- prevent label artifacts from being treated as identity evidence

### Gauge-like constraints

Gauge-like constraints preserve declared gauge-like or representation-convention features from IDSPACE-01.

Use:

- separate convention changes from identity-relevant changes
- test whether gauge-like transforms leave decision states unchanged
- flag any case where gauge-like status is not justified

### Fingerprint-coordinate constraints

Fingerprint-coordinate constraints preserve selected diagnostic coordinates or coordinate summaries.

Use:

- preserve circular phase-like coordinate summaries
- preserve non-compact coordinate marginals or distances
- preserve local-form or amplitude-type diagnostic summaries
- create matched-coordinate nulls

### Identity-relevant constraints

Identity-relevant constraints preserve features IDSPACE-01 declares identity-defining.

Use:

- test whether the declared identity criteria are strong enough
- distinguish identity-preserving from identity-changing alternatives
- avoid counting alternatives that IDSPACE-01 says are outside the identity class

### Ambiguity-preserving constraints

Ambiguity-preserving constraints preserve unresolved cases as unresolved.

Use:

- measure how large unresolved ambiguity classes are
- prevent forced classification when observables are insufficient
- treat ambiguity as a measurable result, not an error

## 8. Candidate null families

Null families must be declared before interpretation.

Candidate null families:

- label-permutation nulls
- coordinate-relabeling nulls
- gauge-like transform nulls
- matched-fingerprint-coordinate nulls
- matched-marginal random fingerprint nulls
- near-identity diagnostic nulls
- identity-changing but fingerprint-close nulls
- identity-preserving but representation-changing nulls
- ambiguity-preserving nulls
- MaxEnt constraint-matched null ensembles
- degeneracy-preserving nulls
- constraint-dropout nulls that remove one constraint class at a time

If a null family matches the structured readout, the result is a boundary finding. It must not be converted into a specificity claim.

## 9. Degeneracy measures

Required diagnostic degeneracy statuses:

- `low_degeneracy`: a small, declared number or tight bound of alternatives remains under the fixed definitions
- `high_degeneracy`: many alternatives remain, or the bound is too loose to support specificity language
- `unresolved_degeneracy`: the count or bound cannot be established with the current definitions or candidate family
- `invalid_degeneracy_measurement`: the measurement violates IDSPACE-01 definitions, uses post hoc constraints, or counts ill-defined alternatives

Candidate measures:

- exact alternative count
- upper and lower bound on alternatives
- ambiguity-class count
- compatible-family count
- null-family match rate
- near-tie count under diagnostic distance
- degeneracy ratio versus candidate-family size
- sensitivity of degeneracy under constraint removal
- stability of degeneracy under label-like and gauge-like transforms

High degeneracy, unresolved degeneracy, or invalid degeneracy measurement can block later diagnostic specificity language.

## 10. Entropy / MaxEnt readouts

Candidate entropy and MaxEnt readouts:

- entropy over compatible candidate alternatives
- entropy over ambiguity classes
- maximum-entropy distribution under declared constraints
- effective number of alternatives
- probability mass concentration on top candidate classes
- entropy change after adding each constraint class
- KL-style comparison between structured and null-family distributions, if later justified
- constraint-satisfaction residuals
- MaxEnt failure status when constraints are inconsistent or target-smuggling

Readouts are diagnostic only. A low entropy readout is not by itself proof of identity. A high entropy readout is a valid ambiguity result.

## 11. Ambiguity classes

Ambiguity classes group candidates that the current definitions and observables cannot separate.

Required classes:

- `label_ambiguity`: unresolved because label-like transforms or label dependence are not separated
- `gauge_like_ambiguity`: unresolved because gauge-like convention changes are not separated
- `fingerprint_coordinate_ambiguity`: unresolved because observed coordinates are same-looking or too close
- `identity_relevance_ambiguity`: unresolved because identity-relevant criteria are incomplete or conflicting
- `constraint_insufficiency_ambiguity`: unresolved because the MaxEnt or CPNS constraints are too weak
- `candidate_family_ambiguity`: unresolved because the candidate family is incomplete or poorly bounded
- `outside_scope_ambiguity`: unresolved because the comparison exceeds this specification

Ambiguity is a measurable result state and may be the correct outcome.

## 12. Stop / escalation gates

Stop or revise gates:

- IDSPACE-01 definitions are missing or unstable
- alternatives are not defined before counting
- null families are introduced after seeing favorable outcomes
- MaxEnt constraints encode the target identity
- high degeneracy remains where specificity language would be required
- unresolved degeneracy remains where later claims depend on uniqueness
- degeneracy measurement is invalid under IDSPACE-01
- ambiguity classes are hidden or collapsed into positive decisions

Escalation gate, still method-level only:

- IDSPACE-01 definitions are fixed
- null families are declared before interpretation
- degeneracy is low or tightly bounded under declared constraints
- high and unresolved degeneracy cases are explicitly reported
- MaxEnt constraints are auditable and do not smuggle the target identity
- claim boundaries remain intact

Escalation does not open WIFM01E, WIFM02, or BRIDGE-NATURE-02 by default.

## 13. Required minimal schema for later implementation

Compact field list for later implementation:

| Field name | Type | Description |
| --- | --- | --- |
| `cpns_record_id` | string | Unique CPNS record identifier. |
| `identity_object_id` | string or null | IDSPACE-01 candidate identity object identifier. |
| `fingerprint_object_id` | string | IDSPACE-01 candidate fingerprint object identifier. |
| `constraint_set_id` | string | Declared constraint set used for this record. |
| `constraint_classes` | array | Constraint classes applied to the candidate family. |
| `candidate_family_id` | string | Admissible candidate or null family identifier. |
| `null_family_id` | string or null | Null family identifier, if this is a null comparison. |
| `alternative_definition_id` | string | IDSPACE-01 definition of what counts as an alternative. |
| `alternative_count` | integer or null | Exact number of compatible alternatives, if available. |
| `degeneracy_lower_bound` | integer or null | Lower bound on compatible alternatives. |
| `degeneracy_upper_bound` | integer or null | Upper bound on compatible alternatives. |
| `degeneracy_status` | enum | One of low_degeneracy, high_degeneracy, unresolved_degeneracy, invalid_degeneracy_measurement. |
| `ambiguity_class_ids` | array | Ambiguity classes attached to the record. |
| `maxent_distribution_id` | string or null | Identifier for the MaxEnt distribution, if defined. |
| `entropy_value` | number or null | Entropy readout over alternatives or classes. |
| `effective_alternative_count` | number or null | Entropy-derived effective number of alternatives. |
| `constraint_residuals` | object or null | Constraint-satisfaction residuals or inconsistency flags. |
| `target_smuggling_check` | enum | pass, warning, fail, or not_applicable. |
| `stop_escalation_gate` | enum | stop, revise, method_level_escalation_candidate, or invalid. |
| `diagnostic_vs_physical_flag` | enum | diagnostic_only or invalid_physical_claim. |
| `claim_boundary_flags` | object | Bridge, specificity, physical validation, and route-opening flags. |
| `notes` | string | Short auditable note without overclaim language. |

## 14. Acceptance criteria

CPNS-02 / MaxEnt is accepted only if:

- it depends on fixed IDSPACE-01 definitions
- alternatives are defined before counting or bounding
- constraint classes are declared before interpretation
- null families are declared before interpretation
- MaxEnt does not smuggle in the target identity
- degeneracy status is reported as low, high, unresolved, or invalid
- ambiguity is treated as a measurable result
- diagnostic degeneracy is separated from physical degeneracy
- high or unresolved degeneracy can block specificity language
- no Bridge confirmation is claimed
- no diagnostic specificity claim is made
- no physical validation is claimed
- no WIFM01E default is introduced
- WIFM02 remains closed
- BRIDGE-NATURE-02 remains closed

## 15. Befund

The current route begins from:

```text
identity_space_defined=false
degeneracy_quantified=false
```

IDSPACE-01 specifies the operational identity vocabulary required before counting alternatives. CPNS-02 / MaxEnt specifies how to count, bound, or mark unresolved the diagnostic alternatives that remain under fixed constraints.

## 16. Interpretation

Degeneracy is not a cleanup detail. It is a central boundary on later interpretation. If many alternatives satisfy the same constraints, the diagnostic route remains ambiguous even when the observed fingerprint is structured.

MaxEnt is useful only as a conservative ambiguity probe. It should show what follows from declared constraints, not supply hidden identity information.

## 17. Hypothese

Working hypothesis, method-level only:

```text
If CPNS-02 / MaxEnt counts or bounds alternatives under fixed
IDSPACE-01 definitions, then later notes can state whether the
diagnostic route is low-degeneracy, high-degeneracy, unresolved,
or invalid for specificity purposes.
```

This hypothesis does not imply that low degeneracy will be found.

## 18. Offene Lücke

Open gaps after this specification:

- no implemented CPNS runner
- no populated candidate family
- no declared final constraint set
- no generated null ensemble
- no exact alternative count
- no degeneracy bound
- no entropy readout
- no ambiguity-class table
- no target-smuggling audit result
- no diagnostic specificity claim
- no Bridge confirmation

## 19. Claim Boundary

This is a degeneracy specification only.

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
CPNS-02 / MaxEnt defines how later work should count, bound,
or explicitly fail to bound diagnostic alternatives under
IDSPACE-01 definitions.
```

## 20. Consequence for a later runner/spec block

A later runner/spec block may be considered only after:

- IDSPACE-01 definitions are accepted
- candidate families and null families are declared
- constraint classes are fixed before interpretation
- schema fields are accepted
- stop and escalation gates are accepted

The later block should be documentation/specification first, then implementation only after explicit approval. It should produce diagnostic degeneracy readouts, not Bridge confirmation, diagnostic specificity, physical validation, WIFM01E, WIFM02, or BRIDGE-NATURE-02.
