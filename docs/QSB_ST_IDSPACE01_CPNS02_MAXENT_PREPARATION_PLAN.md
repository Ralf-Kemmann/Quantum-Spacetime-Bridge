# QSB-ST IDSPACE-01 plus CPNS-02 / MaxEnt Preparation Plan

## 1. Purpose

This document defines a preparation plan for the next route after BRIDGE-NATURE-01B:

```text
IDSPACE-01 plus CPNS-02 / MaxEnt
```

This is a planning note only. It creates no numerics, no runner, no config, no data artifact, no run output, no physical validation, no Bridge confirmation, and no diagnostic specificity claim.

## 2. Starting gate from BRIDGE-NATURE-01B

Primary input:

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

The route begins from a negative/defensive condition: the diagnostic Fingerprint-Raum exists as a synthetic method object, but Identitaets-Raum is not yet defined and degeneracy is not quantified.

## 3. IDSPACE-01: identity-space definition task

IDSPACE-01 should define what counts as an identity object before any later diagnostic route compares or classifies objects.

Minimum task:

- define the candidate identity unit
- define which differences are identity-relevant
- define which differences are representation, gauge-like, label, or coordinate artifacts
- define the map from diagnostic Fingerprint-Raum objects to candidate Identitaets-Raum objects
- define when two fingerprints are treated as same-identity, ambiguous, or different-identity candidates
- define whether the identity decision is deterministic, thresholded, probabilistic, or left undecided

IDSPACE-01 must not assume that geometric readability in Fingerprint-Raum is already identity specificity.

## 4. CPNS-02 / MaxEnt: degeneracy and ambiguity task

CPNS-02 / MaxEnt should quantify or constrain how many candidate identity explanations remain compatible with a diagnostic fingerprint description.

Minimum task:

- define the constraint set used for the MaxEnt or CPNS-style ambiguity analysis
- define the admissible candidate family before seeing the desired outcome
- estimate or bound degeneracy under the selected constraints
- identify cases where many candidate identities share the same or near-same diagnostic fingerprint
- identify cases where MaxEnt constraints are too weak to distinguish alternatives
- report ambiguity as a first-class result, not as a nuisance

This task should treat degeneracy as a possible stop condition for later claims.

## 5. Required definitions

Required definitions before implementation:

- `fingerprint_object`: the diagnostic object being compared
- `identity_object`: the candidate identity-level object, if defined
- `representation_map`: the mapping from identity object to diagnostic representation
- `observation_map`: the mapping from available diagnostic coordinates to reported observables
- `equivalence_relation`: the rule for same-identity, different-identity, and ambiguous cases
- `gauge_like_transform`: transformations expected to preserve identity
- `label_transform`: relabeling or coordinate changes expected to preserve identity
- `identity_relevant_transform`: transformations expected to change identity
- `degeneracy`: number or measure of candidate identity objects compatible with the same constraints
- `ambiguity_class`: set of candidates not separated by the current definitions
- `maxent_constraint_set`: constraints retained for the MaxEnt comparison
- `null_family`: constructed alternatives used to test artifact sensitivity
- `acceptance_boundary`: exact conditions for accepting the preparation block

Each definition should state whether it is synthetic diagnostic, mathematical, operational, or physical. For this route, the default status is synthetic diagnostic unless explicitly justified otherwise.

## 6. Candidate observables

Candidate observables should remain diagnostic and auditable:

- circular phase-like coordinate distance
- non-compact coordinate deltas
- amplitude-type diagnostic differences
- local-form slope/intercept-type differences
- compact-wrap correction flags
- conflict and warning labels
- ambiguity-label preservation
- nearest-neighbor stability in Fingerprint-Raum
- identity-class multiplicity under a proposed equivalence relation
- entropy over compatible candidate identity classes
- degeneracy count or degeneracy bound
- MaxEnt distribution over admissible candidate classes
- constraint-satisfaction residuals
- stability under label transforms
- sensitivity under weight and scale changes

No candidate observable should be described as a physical phase, physical metric, physical identity proof, or Bridge detector.

## 7. Controls and null families

Controls and null families should be selected before any later result interpretation.

Required control families:

- label-permutation controls
- coordinate-relabeling controls
- compact phase-wrap controls
- global-shift or gauge-like phase controls
- matched-marginal random fingerprints
- near-identity synthetic controls
- deliberately ambiguous fingerprints
- strong-conflict synthetic controls
- weight and scale sensitivity controls
- MaxEnt null ensembles with matched constraints
- degeneracy-preserving controls
- representation-changing but identity-preserving controls, if definable
- identity-changing but representation-close controls, if definable

Control outcomes should be allowed to block escalation. If null families produce the same identity-level readout as the proposed structured family, the diagnostic should be marked ambiguous rather than specific.

## 8. Acceptance criteria

Acceptance criteria for this preparation route:

- identity-space terms are defined before use
- Fingerprint-Raum and Identitaets-Raum remain explicitly separated
- equivalence relations are documented
- all gauge-like, label-like, and identity-relevant transforms are declared
- MaxEnt or CPNS constraints are listed before evaluation
- degeneracy is quantified, bounded, or explicitly marked unquantified
- ambiguity classes are reported, not hidden
- null/control families are defined before interpretation
- no WIFM01E default is introduced
- WIFM02 remains closed
- BRIDGE-NATURE-02 remains closed
- no Bridge confirmation is claimed
- no diagnostic specificity claim is made
- no physical validation is claimed

Fail or revise conditions:

- identity space remains undefined
- degeneracy remains unbounded while later interpretation depends on uniqueness
- controls are defined after seeing favorable outcomes
- MaxEnt constraints smuggle in the target identity
- Fingerprint-Raum is treated as Identitaets-Raum by wording rather than definition
- literature analogy is used as evidence
- null families match the structured readout without a boundary note

## 9. Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary

### Befund

BRIDGE-NATURE-01B routes the project to IDSPACE-01 plus CPNS-02 / MaxEnt because:

```text
identity_space_defined=false
degeneracy_quantified=false
```

The current basis is a synthetic diagnostic route with WIFM01-D closed and no default continuation into WIFM01E.

### Interpretation

The next useful work is definitional and ambiguity-focused. It should not add a new positive bridge-facing result. It should define the identity space, expose degeneracy, and test whether ambiguity remains too large for specificity language.

### Hypothese

Working hypothesis, method-level only:

```text
If identity space and degeneracy are made explicit, later diagnostic claims can be bounded more sharply and unsupported specificity claims can be avoided.
```

This does not imply that later specificity will be achieved.

### Offene Lücke

Open gaps:

- `identity_space_defined=false`
- `degeneracy_quantified=false`
- no identity equivalence relation
- no degeneracy table or bound
- no MaxEnt constraint set
- no accepted ambiguity classes
- no diagnostic specificity claim
- no Bridge confirmation

### Claim Boundary

This is preparation only.

Not established:

- Bridge confirmation
- diagnostic specificity
- physical validation
- physical phase
- physical metric
- physical spacetime geometry
- Hilbert-space reconstruction
- proof of wave identity
- WIFM01E default
- WIFM02 opening
- BRIDGE-NATURE-02 opening

Allowed conclusion:

```text
The next route should prepare IDSPACE-01 plus CPNS-02 / MaxEnt definitions and degeneracy controls before any later escalation is considered.
```

## 10. Recommended next implementation block

Recommended next block:

```text
QSB-ST-IDSPACE-01 identity-space definition specification
```

Recommended scope:

- documentation/specification first
- no runner until identity objects, equivalence relations, and controls are written down
- no data or run artifacts until the accepted definitions and null families are fixed
- CPNS-02 / MaxEnt degeneracy work only after IDSPACE-01 states what is being counted or constrained

This recommendation does not open WIFM01E, WIFM02, or BRIDGE-NATURE-02.
