# QSB-ST IDSPACE/CPNS-05 Minimal Schema Validation Runner Plan

## 1. Purpose

This document defines a later minimal validation runner for the IDSPACE/CPNS schema scaffold.

This is a runner-plan document only. It creates no implementation, scripts, data, configs, runs, numerical results, Bridge confirmation, diagnostic specificity claim, physical validation, proof of wave identity, or physical spacetime claim.

## 2. Starting point from CPNS04

Mandatory primary inputs:

- `docs/QSB_ST_IDSPACE_CPNS04_MINIMAL_SCHEMA_SCAFFOLD_RESULT_NOTE.md`
- `docs/QSB_ST_IDSPACE_CPNS03_MINIMAL_SCHEMA_ACCEPTANCE_TEST_PLAN.md`
- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json`
- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json`

CPNS04 created a minimal schema scaffold and illustrative synthetic examples only. The CPNS04 result note states that there is no implemented runner, no numerical result, no measured degeneracy count, no measured degeneracy bound, no entropy readout, no Bridge confirmation, no diagnostic specificity claim, and no physical validation.

## 3. Scope and non-scope

Scope:

- plan a later runner that validates schema/example consistency
- define proposed inputs and outputs for that later runner
- define validation checks, boundary-flag checks, decision-state checks, and schema consistency checks
- define failure modes and stop gates
- keep ambiguity as a valid decision/result state

Non-scope:

- no implementation in this document
- no scripts
- no new data beyond this plan
- no configs
- no runs
- no numerical results
- no physical result computation
- no real degeneracy quantification
- no WIFM01E default
- no WIFM02 opening
- no BRIDGE-NATURE-02 opening
- no Bridge confirmation
- no diagnostic specificity claim
- no physical validation

## 4. Proposed later runner name

Proposed later block name:

```text
QSB-ST-IDSPACE-CPNS06 minimal schema validation runner
```

Proposed later script name, if explicitly approved in a future task:

```text
scripts/run_qsb_st_idspace_cpns06_minimal_schema_validation.py
```

CPNS06, if approved later, may implement the validation runner. CPNS05 does not implement it.

## 5. Proposed later inputs

Proposed later runner inputs:

- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json`
- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json`

Optional later documentation references:

- `docs/QSB_ST_IDSPACE_CPNS04_MINIMAL_SCHEMA_SCAFFOLD_RESULT_NOTE.md`
- `docs/QSB_ST_IDSPACE_CPNS03_MINIMAL_SCHEMA_ACCEPTANCE_TEST_PLAN.md`

The runner should load JSON and validate scaffold consistency only. It should not inspect WIFM01E, WIFM02, or BRIDGE-NATURE-02.

## 6. Proposed later outputs

Proposed later outputs, only if CPNS06 is explicitly approved:

- a machine-readable validation summary
- a human-readable validation note
- a list of failed checks, if any
- a list of accepted decision-state examples
- a boundary-flag report

The outputs should report schema/example consistency only. They should not report physical results, real degeneracy measurement, Bridge confirmation, diagnostic specificity, or physical validation.

## 7. Validation checks

The later runner should check:

- both JSON files parse successfully
- the schema top-level object contains `object_groups`
- required object groups are present
- each object group contains a `fields` object
- each field declares `type`, `required`, and `description`
- example records contain an `examples` list
- each example has an `equivalence_decision_record`
- each example has claim-boundary flags
- CPNS / MaxEnt degeneracy fields are placeholders or status fields only
- no example claims physical result computation

The later runner should not compute physical results and should not quantify real degeneracy.

## 8. Boundary-flag checks

The later runner must check that required false flags remain false wherever they appear:

```text
bridge_confirmation=false
diagnostic_specificity_claim=false
physical_validation=false
wifm01e_opened=false
wifm02_opened=false
bridge_nature_02_opened=false
```

Failure modes:

- missing boundary flag
- boundary flag present with non-boolean value
- boundary flag present with value `true`
- boundary flags present in only some examples
- schema declares a required false flag but examples omit it

Any forbidden claim flag should stop the later runner result from being accepted.

## 9. Decision-state checks

The later runner must check that example records include:

- `same_identity_candidate`
- `different_identity_candidate`
- `ambiguous_unresolved`
- `invalid_outside_scope`

The runner must treat `ambiguous_unresolved` as a valid state, not as an error.

Failure modes:

- missing decision state
- unknown decision state
- decision state not listed in the schema
- ambiguous state treated as failure
- invalid outside-scope state treated as a successful identity decision

## 10. Schema consistency checks

The later runner should check schema/example consistency:

- each example field used by the planned checks is declared in the schema
- each required schema field is present in the relevant example record where that record type appears
- simple values match declared type categories where feasible
- enum values in examples appear in the schema allowed values where declared
- example degeneracy statuses match the declared CPNS statuses
- ambiguity classes match declared ambiguity classes where present
- the schema and examples both preserve the claim-boundary flags

Failure modes:

- missing required field
- wrong type
- unknown enum value
- missing flag
- forbidden claim flag
- missing decision state
- schema/example mismatch
- invalid JSON
- example record that implies a numerical result
- CPNS record that appears to measure real degeneracy

## 11. Stop gates

Stop or revise if:

- JSON parsing fails
- required schema object groups are missing
- example decision states are incomplete
- ambiguity is not represented as valid
- boundary flags are missing or not false
- schema and examples disagree about required fields
- MaxEnt or CPNS fields appear to encode a target identity
- degeneracy fields are treated as measured results
- the runner would need WIFM01E, WIFM02, or BRIDGE-NATURE-02
- any output wording would imply Bridge confirmation, diagnostic specificity, physical validation, proof of wave identity, or a physical spacetime claim

## 12. Acceptance criteria

The later CPNS06 runner would be accepted only if:

- it validates schema/example consistency only
- it does not compute physical results
- it does not quantify real degeneracy
- it reports all required false boundary flags as false
- it confirms all four required decision-state examples are present
- it treats ambiguity as a valid result state
- it reports missing fields, wrong types, missing flags, forbidden claim flags, missing decision states, and schema/example mismatch as failures
- it creates no route opening for WIFM01E, WIFM02, or BRIDGE-NATURE-02

## 13. Befund

CPNS04 provides a minimal schema scaffold and illustrative examples. The examples include the four required decision states and false boundary flags. CPNS04 does not provide a validation runner.

The current CPNS05 step defines the plan for validating those artifacts, without implementing the runner.

## 14. Interpretation

The appropriate next technical step is a consistency validator, not a scientific or physical-result runner.

The planned runner should answer only whether the scaffold and examples are internally consistent enough for later review. It should not infer identity resolution, real degeneracy, physical validation, or bridge status.

## 15. Hypothese

Working hypothesis, method-level only:

```text
If a later CPNS06 runner validates schema/example consistency and
false claim-boundary flags, then the scaffold can be audited before
any future implementation attempts diagnostic degeneracy measurement.
```

This does not imply that later diagnostic specificity will be achieved.

## 16. Offene Lücke

Open gaps:

- no validation runner exists
- no validation output exists
- no machine-readable validation summary exists
- no run artifact exists
- no real degeneracy has been quantified
- no entropy readout exists
- no target-smuggling audit has been executed
- no physical validation exists
- no Bridge confirmation exists
- no diagnostic specificity claim exists

## 17. Claim Boundary

This is a runner-plan document only.

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

Required flags remain:

```text
bridge_confirmation=false
diagnostic_specificity_claim=false
physical_validation=false
wifm01e_opened=false
wifm02_opened=false
bridge_nature_02_opened=false
```

## 18. Consequence for next step

CPNS06, if explicitly approved later, may implement the minimal schema validation runner.

That later implementation should validate only schema/example consistency, boundary flags, decision states, and scaffold compatibility. It should not create physical results, real degeneracy measurements, Bridge confirmation, diagnostic specificity, WIFM01E, WIFM02, or BRIDGE-NATURE-02.
