# QSB-ST Resonance Matter Signature
## Status and Claim Taxonomy

This document gives QSB-ST a shared claim discipline. Its positive purpose is to let strong ideas be stated clearly while keeping assumptions, definitions, diagnostics, results, limits, and open gaps in their correct categories.

Guiding principle: "Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This is a reviewer-facing and internal status/claim taxonomy for the QSB-ST Resonance Matter Signature project.

It is not a result note and not a theory proof. It defines how project statements must be classified so that axioms, definitions, model assumptions, heuristics, exploratory results, supported findings, boundary findings, candidate carriers, marker layers, and open gaps are not mixed.

## 2. Why a status taxonomy is needed

QSB-ST uses several kinds of statements at once: mathematical definitions, toy-model assumptions, diagnostic readouts, synthetic scaffold results, archival recovered result clusters, architecture interpretations, and open physical questions.

Without explicit status labels, a reader can mistake a useful diagnostic for an observable, a definition for a derivation, or a candidate carrier for an established carrier. This taxonomy is intended to make the project easier to review and harder to overstate.

## 3. Core rule: no silent category shift

No statement may silently move from one status category to another.

For example:

- a definition must not be presented as a derivation;
- a heuristic must not be presented as a result;
- a diagnostic readout must not be presented as a physical observable;
- an exploratory result must not be presented as validation;
- a candidate carrier must not be presented as an established carrier.

If a claim changes category, the document must say what new assumption, derivation, control, result, or external anchor justifies the change.

## 4. Status classes

### 1. AXIOM

A starting principle adopted for the framework.

Example: relational primacy / no a-priori spacetime.

### 2. DEFINITION

A mathematical definition introduced by the project.

Examples: `K_ij = <psi_i | psi_j>`; `d_ij = -l0 log |K_ij|`.

### 3. MODEL ASSUMPTION

A simplifying or structural assumption used in a toy model, scaffold, simulation, or diagnostic.

Examples: continuum-limit assumptions; chosen kernel form; threshold choice; synthetic scaffold assumptions.

### 4. DERIVATION-WITHIN-ASSUMPTIONS

A result that follows only after specified assumptions.

Example: effective wave-equation-like structure after linearization and continuum approximation.

### 5. HEURISTIC

A conceptual or interpretive reading that guides the project but is not proven.

Example: reading `d_ij` as emergent geometric separation.

### 6. DIAGNOSTIC READOUT

A computed marker or diagnostic score.

Examples: D_rel, geometry_readability, core recovery, containment, phase influence.

### 7. EXPLORATORY RESULT

A result from a toy, synthetic, archival, or non-canonical run that suggests a direction but does not validate physics.

Examples: archival Matter Signature runs; VDW B/C; early phase verification.

### 8. SUPPORTED RESULT

A result supported under explicitly stated controls and scope.

Examples: DATA-02D separated 24/32 controls under its synthetic scaffold; N1 negative/abs upper block over positive under tested conditions.

### 9. BOUNDARY FINDING

A negative, degenerate, mimic, or failure result that constrains interpretation.

Examples: DATA-02D/02E failed controls; `within_system_label_shuffle__adamantane`; inconclusive negative-vs-abs separation.

### 10. CANDIDATE CARRIER

A structure proposed as a possible physical/informational carrier but not established.

Examples: phase-coherent off-diagonal relational correlation; ODLRO-like density-matrix structure; RMS.

### 11. MARKER LAYER

A structure that may track or reveal something without being the underlying carrier.

Examples: D_rel, negative/abs marker channels, Carbon diagnostics, VDW score layers unless proven otherwise.

### 12. OPEN QUESTION

A required clarification not yet resolved.

Examples: physical anchor for D(A,B); Lorentz status; `l0` physical interpretation; de-Broglie specificity beyond random/trivial controls.

### 13. NOT ESTABLISHED

A claim explicitly not shown by the project.

Examples: physical spacetime emergence; a derivation of relativity; established RMS carrier; experimental prediction.

### 14. REJECTED / FALSIFIED

A claim or interpretation contradicted by results or excluded by project boundaries.

Examples: interpreting Carbon DATA-02 as molecular bridge validation; claiming negative channel alone is the carrier despite inconclusive negative-vs-abs tests.

## 5. How to classify QSB-ST statements

For every central statement, ask:

- Is this a starting principle, a definition, an assumption, a result, a diagnostic, an interpretation, or an open question?
- What controls, assumptions, and scope make the statement valid?
- Does the statement depend on synthetic scaffold conditions, archival recovery, or current canonical reruns?
- Is the statement about a marker layer, a candidate carrier, or an established physical object?
- What would be required to move the statement to a stronger category?

The answer should be stated in the document rather than implied.

## 6. Current architecture examples

| Statement | Correct status | Why | Claim-safe wording | Forbidden upgrade |
|---|---|---|---|---|
| "No a-priori spacetime" | AXIOM | It is a starting principle adopted by the framework. | "QSB-ST adopts relational primacy as a starting principle." | "Spacetime has been physically replaced." |
| "K_ij = <psi_i \| psi_j>" | DEFINITION | It defines the project's correlation/Gram object. | "K_ij is the project's correlation/Gram object." | "K_ij is directly measured physical structure." |
| "d_ij = -l0 log \|K_ij\|" | DEFINITION / DIAGNOSTIC READOUT | It defines a relational distance-like readout from correlation magnitude. | "d_ij is a candidate relational distance readout." | "d_ij is physical spacetime distance." |
| "d_ij can be read geometrically" | HEURISTIC / GEOMETRY-READABILITY CANDIDATE | It interprets a readout as geometrically readable under conditions. | "geometrically readable candidate distance under tested conditions." | "physical geometry has emerged." |
| "effective wave equation after linearization" | DERIVATION-WITHIN-ASSUMPTIONS | It follows only after toy-model and approximation assumptions. | "effective wave-equation-like structure under specified toy-model assumptions." | "relativity has been derived." |
| "Lorentz structure" | OPEN QUESTION / LORENTZ-COMPATIBLE CANDIDATE unless further proven | Its status must be separated into assumption, definition, derivation-within-assumptions, or interpretation. | "Lorentz-compatible or Lorentz-inspired structure under specified assumptions." | "relativity derived." |
| "de-Broglie vs random/trivial phase separation" | SUPPORTED RESULT under tested controls | The stated controls support phase specificity only within that pipeline. | "phase-specific under random/trivial controls." | "de-Broglie uniquely generates geometry." |
| "Gram/Graph geometry" | DIAGNOSTIC READOUT / GEOMETRY-READABILITY CANDIDATE | Graph and Gram methods can generate readable structure without physical anchoring. | "metric-readable regime candidate." | "emergent physical geometry." |
| "Green/Poisson / Coulomb" | INTERACTION-ANCHOR CANDIDATE | It tests interaction-form readability and benchmark behavior. | "candidate interaction-form anchor." | "gravity or Coulomb law derived." |
| "Hartman / Relational Delay" | TEMPORAL-CAUSAL ANCHOR CANDIDATE | It gives phasengeometric and delay-like checks, not time or causality by itself. | "phasengeometric / relational-delay anchor candidate." | "time or causality derived." |
| "Matter Signature archival cluster" | EXPLORATORY RESULT / ARCHIVAL RECOVERED SURROGATE RESULT CLUSTER | It was recovered from duplicate-quarantine and is not yet a current canonical rerun. | "archival recovered candidate matter-signature axes." | "canonical current validation." |
| "VDW B/C" | EXPLORATORY RESULT / CANDIDATE MATTER-SENSITIVE AXIS | It suggests a VDW-related axis under specific archival/surrogate conditions. | "candidate matter-sensitive VDW axis." | "VDW carrier established." |
| "negative/abs upper block" | SUPPORTED RESULT under tested conditions | The upper block is supported over positive, while internal negative-vs-abs separation remains unresolved. | "shared negative/abs upper block over positive." | "negative channel is the physical carrier." |
| "Carbon DATA-02" | SCANNER CALIBRATION / BOUNDARY FINDING / SUPPORTED RESULT under synthetic controls | It supports scanner discipline and mimicry stress testing within a synthetic/reference scaffold. | "scanner calibration and mimicry discipline." | "molecular bridge validation." |
| "Causality and entropy anchor" | OPEN QUESTION / ANCHOR CANDIDATE | It names future causally or entropically readable criteria, not established causal or thermodynamic structure. | "causally or entropically readable candidate structures." | "correlation creates causality or entropy." |
| "QSB-ST" | CANDIDATE BRIDGE ARCHITECTURE / TRANSLATION-LAYER PROGRAM | It organizes diagnostics and compatibility questions across RT/QM-facing axes. | "diagnostic bridge-architecture program compatible with RT/QM." | "Theory of Everything." |

## 7. Claim-safe language patterns

Useful claim-safe phrases include:

- "candidate"
- "under tested controls"
- "within this synthetic scaffold"
- "archival recovered"
- "surrogate-level"
- "diagnostic readout"
- "metric-readable regime"
- "not yet physically anchored"
- "not established"
- "requires external observable anchoring"

These phrases should be used where the evidence supports structure, readability, or diagnostic value without establishing physical interpretation.

## 8. Common forbidden upgrades

Common category shifts to avoid:

- definition -> derivation
- heuristic -> physical claim
- readout -> observable
- exploratory result -> validation
- support under controls -> universal claim
- mimic warning -> ignored failure
- archival recovered result -> canonical current result
- candidate carrier -> established carrier
- geometry readability -> spacetime emergence
- compatibility goal -> replacement of RT/QM

When a document needs stronger wording, it should first state the added derivation, control, external observable, or reproducibility step that permits the upgrade.

## 9. How this supports the red-team roadmap

This taxonomy is step 1 in the current roadmap:

1. Status-/Claim-Taxonomy
2. Geometry Anchor Conditions
3. RMS Carrier / Stability Criteria
4. Causality & Entropy Anchor Note
5. PADS-01 Spec
6. Matter Signature Canonicalization

It supports the red-team roadmap by making each attack point classifiable. The physical anchor problem becomes an OPEN QUESTION; Gram/Graph geometry remains a DIAGNOSTIC READOUT / GEOMETRY-READABILITY CANDIDATE; archival Matter Signature remains an EXPLORATORY RESULT until canonicalized; and RMS remains a CANDIDATE CARRIER unless carrier criteria and external anchoring are met.

## 10. Recommended use in future documents

Future QSB-ST documents should include either:

- a short Status Note section; or
- status tags for central claims.

This is especially important for theory-facing documents, reviewer-facing documents, and result discussions. Status tags should be used for statements about Lorentz structure, physical geometry, interaction anchors, carrier status, Carbon scaffold interpretation, causality, entropy, and Matter Signature provenance.

## 11. Compact Claim Boundary

This taxonomy does not:

- prove the theory;
- validate spacetime emergence;
- establish RMS;
- define a physical carrier;
- solve Lorentz covariance;
- replace future derivation, validation, external anchoring, or reproducibility work.

It only defines how claims should be labeled and bounded.

## 12. Next steps

Recommended next steps:

1. Add status tags to the main QSB-ST synthesis documents.
2. Create Geometry Anchor Conditions for D(A,B) and related distance readouts.
3. Create RMS Carrier / Stability Criteria separating marker layers from candidate carriers.
4. Connect this taxonomy to the Causality and entropy anchor note.
5. Use the taxonomy when drafting PADS-01 and Matter Signature canonicalization notes.
